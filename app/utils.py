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



def generate_answer(messages: list[dict], max_steps: int = 20, llm: BaseLLM = None, sleeptime: float = 0.0, **kwargs):
    thoughts = []
    
    for i in range(max_steps):
        raw_response = llm.chat(messages, **kwargs)
        response = raw_response.choices[0].message.content
        thought = response_parser(response)
        
        print(colored(f"{i+1} - {response}", 'yellow'))

        if thought:
            thoughts.append(thought)
            messages.append({"role": "assistant", "content": thought.model_dump_json()})
            messages.append({"role": "user", "content": REVIEW_PROMPT})

            yield thought
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

