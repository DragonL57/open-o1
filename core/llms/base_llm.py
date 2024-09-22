from abc import ABC, abstractmethod
from email import message
from urllib import response
from litellm.utils import ModelResponse
import json
from function_schema import get_function_schema
from typing import Any, List, Tuple

class BaseLLM(ABC):

    def __init__(self, api_key:str=None, model:str=None, tools:dict=None):
        self.api_key = api_key
        self.model = model
        self.tools = tools
        
    @property    
    def tools_schema(self) -> List[dict] | None:
        if self.tools:
            tool_func = self.tools.values()
            return self.get_tools_schema(tool_func)
        return None
        

    @abstractmethod
    def _chat(self, messages:list[str], **kargs:Any) -> ModelResponse:
        pass
    
    def chat(self, messages:list, **kargs):
        message =  self._chat(messages, **kargs)  
        message, tool_results = self._handle_tool_calls(message, **kargs)
        
        if tool_results:
            print('tool message: ', message)
            messages.append(message.choices[0].message)
            for tool_result in tool_results:
                messages.append(tool_result)
            
            message = self._chat(messages, **kargs)     
           
        return message
    


    def _handle_tool_calls(self, message:ModelResponse,  **kwargs) -> Tuple[ModelResponse, List[dict]]:

        if (self.tools is None) or (message.choices[0].finish_reason != 'tool_calls'):
            return message, None
        
        tool_results = []
        tools_to_call = message.choices[0].message.tool_calls
        for tool in tools_to_call:
            tool_args = json.loads(tool.function.arguments)
            tool_func = self.tools.get(tool.function.name, None)
            if tool_func:
                print("Calling tool: ", tool.function.name)
                tool_result = tool_func(**tool_args)
                print("Result of tool: ", tool_result) 
                
                
                tool_results.append({
                    'role': 'tool',
                    "tool_call_id": tool.id,
                    'name': tool.function.name,
                    'content': str(tool_result),
                })
        return message, tool_results

    def get_tools_schema(self, tools):
        def make_schema(tool):
            return {'type': 'function',
                    'function': get_function_schema(tool)}
            
        return [make_schema(tool) for tool in tools]