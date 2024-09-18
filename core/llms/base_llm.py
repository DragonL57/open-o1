from abc import ABC, abstractmethod

class BaseLLM(ABC):

    def __init__(self, api_key, model, tools):
        self.api_key = api_key
        self.model = model
        self.tools = tools
        
    @abstractmethod
    def _chat(self, messages, **kargs):
        pass
    
    def chat(self, messages, **kargs):
        return self._chat(messages, **kargs)    
    
    def get_attr(self,attr:str, kwargs:dict):
        attribute = kwargs.get(attr, None)
        if attribute is None:
            if hasattr(self, attr):
                attribute = getattr(self, attr)
        return attribute