from openai.types.chat.chat_completion_chunk import Choice
from .base_llm import BaseLLM
from litellm import completion
from litellm.utils import ModelResponse
from openai import OpenAI

class LLM(BaseLLM):
    def __init__(self, api_key, model, tools:list=None):
        super().__init__(api_key=api_key, model=model, tools=tools)

    
    def _chat(self, messages, **kwargs):
        return completion(messages=messages, model=self.model, api_key=self.api_key, **kwargs)
    
    def _handle_tool_calls(self, messages:list[ModelResponse], **kwargs):
        
        message = messages[-1]
        
        if self._tools is None:
            return messages
        
        if message.choices[0].finish_reason in ('stop', 'length'):
            return messages
        elif message.choices[0].finish_reason == 'tool_calls':
            tools_to_call = message.choices[0].message.tool_calls
            for tool in tools_to_call:
                print(tool)

            