from openai.types.chat.chat_completion_chunk import Choice
from .base_llm import BaseLLM
from typing import List, Tuple
from litellm import completion
import json
from litellm import batch_completion
from litellm.utils import ModelResponse
from openai import OpenAI
from litellm.utils import trim_messages
import litellm

litellm.set_verbose=False

class LLM(BaseLLM):
    def __init__(self, api_key:str=None, model:str=None, tools:dict[str, callable]=None):
        super().__init__(api_key=api_key, model=model, tools=tools)


    
    def _chat(self, messages, **kwargs):
        return completion(messages=messages, model=self.model, api_key=self.api_key,tools=self.tools_schema, **kwargs)
    
