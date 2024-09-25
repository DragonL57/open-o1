import json
import re
import sys
from turtle import color
from typing import Generator
from textwrap import dedent
from litellm.types.utils import ModelResponse
from pydantic import ValidationError
from core.llms.base_llm import BaseLLM
from core.prompts import cot
from core.types import ThoughtSteps, ThoughtStepsDisplay
from core.prompts import REVIEW_PROMPT, SYSTEM_PROMPT ,FINAL_ANSWER_PROMPT, HELPFUL_ASSISTANT_PROMPT
import os
import time
from core.utils import parse_with_fallback
from termcolor import colored
from app.app_config import InputConfig
from core.llms.litellm_llm import LLM
from core.llms.utils import user_message_with_images
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile
from core.prompts.decision_prompt import COT_OR_DA_PROMPT, COTorDAPromptOutput, Decision




def cot_or_da_func(problem: str, llm: BaseLLM = None, **kwargs) -> COTorDAPromptOutput:
    
    cot_decision_message = [
        {"role": "system", "content": COT_OR_DA_PROMPT},
        {"role": "user", "content": problem}] 
    
    raw_decision_response = llm.chat(messages=cot_decision_message, **kwargs)
    print(colored(f"Decision Response: {raw_decision_response.choices[0].message.content}", 'blue', 'on_black'))
    decision_response = raw_decision_response.choices[0].message.content 
    
    try:
        decision = json.loads(decision_response)
        cot_or_da = COTorDAPromptOutput(**decision)
    except (json.JSONDecodeError, ValidationError, KeyError):
        print(colored("Error parsing LLM's CoT decision. Defaulting to Chain of thought.", 'red'))
        cot_or_da = COTorDAPromptOutput(problem=problem, decision="Chain-of-Thought", reasoning="Defaulting to Chain-of-Thought") 
    
    return cot_or_da


def get_system_prompt(decision: Decision) -> str:
    if decision == Decision.CHAIN_OF_THOUGHT:
        return cot.SYSTEM_PROMPT
    elif decision == Decision.DIRECT_ANSWER:
        return HELPFUL_ASSISTANT_PROMPT
    else:
        raise ValueError(f"Invalid decision: {decision}")
    
def set_system_message(messages: list[dict], cot_or_da: COTorDAPromptOutput) -> list[dict]:
    system_prompt = get_system_prompt(cot_or_da.decision)
    #check if any system message already exists
    if any(message['role'] == 'system' for message in messages):
        for i, message in enumerate(messages):
            if message['role'] == 'system':
                messages[i]['content'] = system_prompt        
    else:
        # add a dict at the beginning of the list
        messages.insert(0, {"role": "system", "content": system_prompt})
    return messages


def generate_answer(messages: list[dict], max_steps: int = 20, llm: BaseLLM = None, sleeptime: float = 0.0, force_max_steps: bool = False, **kwargs) -> Generator[ThoughtStepsDisplay, None, None]: 

    user_message = messages[-1]['content']
    cot_or_da = cot_or_da_func(user_message, llm=llm, **kwargs)
    print(colored(f"LLM Decision: {cot_or_da.decision} - Justification: {cot_or_da.reasoning}", 'magenta'))

    MESSAGES = set_system_message(messages, cot_or_da)
    

    if cot_or_da.decision == Decision.CHAIN_OF_THOUGHT:
                
        print(colored(f" {MESSAGES}", 'red'))
        for i in range(max_steps):
            print(i)
            raw_response = llm.chat(messages=MESSAGES, **kwargs)
            print(colored(f"{i+1} - {raw_response.choices[0].message.content}", 'blue', 'on_black'))
            response = raw_response.choices[0].message.content
            thought = response_parser(response)
            
            print(colored(f"{i+1} - {response}", 'yellow'))

            MESSAGES.append({"role": "assistant", "content": thought.model_dump_json()})
            
            yield thought.to_thought_steps_display()
                    
            if thought.is_final_answer and not thought.next_step and not force_max_steps:
                break
            
            MESSAGES.append({"role": "user", "content": cot.REVIEW_PROMPT})

            time.sleep(sleeptime)

        # Get the final answer after all thoughts are processed
        MESSAGES += [{"role": "user", "content": cot.FINAL_ANSWER_PROMPT}]
        
        raw_final_answers = llm.chat(messages=MESSAGES, **kwargs)
        final_answer = raw_final_answers.choices[0].message.content

        print(colored(f"final answer - {final_answer}", 'green'))

        final_thought = response_parser(final_answer)
        
        yield final_thought.to_thought_steps_display()
        
    else:

        raw_response = llm.chat(messages=MESSAGES, **kwargs)  #
        response = raw_response.choices[0].message.content
        thought = response_parser(response)

        print(colored(f"Direct Answer - {response}", 'blue'))

        yield thought.to_thought_steps_display()
        

def response_parser(response:str) -> ThoughtSteps:
    if isinstance(response, str):
        
        try:
            thought_kwargs = json.loads(response)
            thought = ThoughtSteps(**thought_kwargs)                    
        except (json.JSONDecodeError, ValidationError):
            thought = parse_with_fallback(response, ThoughtSteps)

            
    elif isinstance(response, dict):
        thought = ThoughtSteps(**response)

    return thought


def dict_to_markdown(d:dict) -> str:
    '''use keys as headers and values as content'''
    md = ""
    for key, value in d.items():
        md += f"### {key}\n"
        md += f"{value}\n"
    return md




def load_llm(config:InputConfig, tools=None) -> BaseLLM:
    return LLM(api_key=config.model_api_key, model=config.model_name, tools=tools)

    
def image_buffer_to_pillow_image(image_buffer:UploadedFile) -> Image.Image:
    return Image.open(image_buffer)


def process_user_input(user_input:str, image:Image.Image=None)->dict:
    if image:
        message = [user_message_with_images(user_msg_str=user_input, images=[image])] 
    else:
        message = [{"role": "user", "content": user_input}]
    return message


