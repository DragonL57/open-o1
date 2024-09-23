import json
import re
from typing import Generator
from textwrap import dedent
from litellm.types.utils import ModelResponse
from pydantic import ValidationError
from core.llms.base_llm import BaseLLM
from core.types import ThoughtSteps
from core.prompts.think_mark_think import REVIEW_PROMPT, SYSTEM_PROMPT ,FINAL_ANSWER_PROMPT
import os
import time
from core.utils import parse_with_fallback
from termcolor import colored
from app.app_config import InputConfig
from core.llms.litellm_llm import LLM
from core.llms.utils import user_message_with_images
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile




def generate_answer(messages: list[dict], max_steps: int = 20, llm: BaseLLM = None, sleeptime: float = 0.0, force_max_steps: bool = False, **kwargs):
    thoughts = []
    
    for i in range(max_steps):
        raw_response = llm.chat(messages, **kwargs)
        response = raw_response.choices[0].message.content
        thought = response_parser(response)
        
        print(colored(f"{i+1} - {response}", 'yellow'))

        thoughts.append(thought)
        messages.append({"role": "assistant", "content": thought.model_dump_json()})
        yield thought
                
        if thought.is_final_answer and not thought.next_step and not force_max_steps:
            break
        
        messages.append({"role": "user", "content": REVIEW_PROMPT})

        time.sleep(sleeptime)

    # Get the final answer after all thoughts are processed
    messages += [{"role": "user", "content": FINAL_ANSWER_PROMPT}]
    raw_final_answers = llm.chat(messages=messages, **kwargs)
    final_answer = raw_final_answers.choices[0].message.content

    print(colored(f"final answer - {final_answer}", 'green'))

    final_thought = response_parser(final_answer)
    yield final_thought

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


