import json
from typing import Generator
from pydantic import ValidationError
from core.llms.base_llm import BaseLLM
from core.prompts import cot
from core.types import ThoughtSteps, ThoughtStepsDisplay
import time
from core.utils import parse_with_fallback
from termcolor import colored
from app.app_config import InputConfig
from core.llms.litellm_llm import LLM
from core.llms.utils import user_message_with_images
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile
from core.prompts.decision_prompt import PLAN_SYSTEM_PROMPT, COTorDAPromptOutput, Decision
from tenacity import retry, stop_after_attempt, wait_incrementing




@retry(stop=stop_after_attempt(3), wait=wait_incrementing(increment=2))
def cot_or_da_func(problem: str, llm: BaseLLM = None, **kwargs) -> COTorDAPromptOutput:
    
    cot_decision_message = [
        {"role": "system", "content": PLAN_SYSTEM_PROMPT},
        {"role": "user", "content": problem}] 
    
    raw_decision_response = llm.chat(messages=cot_decision_message, **kwargs)
    print(colored(f"Decision Response: {raw_decision_response.choices[0].message.content}", 'blue', 'on_black'))
    decision_response = raw_decision_response.choices[0].message.content 
    
    try:
        decision = json.loads(decision_response)
        cot_or_da = COTorDAPromptOutput(**decision)
    except (json.JSONDecodeError, ValidationError, KeyError) as e:
        raise e
        
    return cot_or_da


    
def set_system_message(messages: list[dict], system_prompt: str) -> list[dict]: 
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

    system_prompt, review_prompt, final_answer_prompt = cot_or_da.prompts.system_prompt, cot_or_da.prompts.review_prompt, cot_or_da.prompts.final_answer_prompt

    system_prompt += f" , {cot.SYSTEM_PROMPT_EXAMPLE_JSON}"
    review_prompt += f" , {cot.REVIEW_PROMPT_EXAMPLE_JSON}"
    final_answer_prompt += f" , {cot.FINAL_ANSWER_EXAMPLE_JSON}"
    
    MESSAGES = set_system_message(messages, system_prompt)
    

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
            
            MESSAGES.append({"role": "user", "content": f"{review_prompt} {thought.critic}"})

            time.sleep(sleeptime)

        # Get the final answer after all thoughts are processed
        MESSAGES += [{"role": "user", "content": f"{final_answer_prompt}"}]
        
        kwargs['max_tokens'] = kwargs.get('max_tokens', 1000) *  3 # giving more tokens to the final answer
        
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


