from dataclasses import dataclass
from textwrap import dedent

from pydantic import BaseModel, Field, ValidationError
import json
from textwrap import dedent

class ThoughtSteps(BaseModel):
    step_title: str = Field(..., description="steps to use for the problem/question")
    thought: str = Field(..., description="internal monologue, this contails your questions and its answers")
    next_step: bool =  Field(default=True, description="Does the problem require more thinking? if yes then set to true, else set to false,")
    answer: str | None = Field(..., description="generate a answer based on inner thoughts")
    critic: str | None = Field(..., description="criticize the answer, try to prove it wrong , have a different perspective, fight it")
    is_final_answer: bool = Field(default=False, description="this is final answer no next step required,")
    
    def to_thought_steps_display(self):
        return ThoughtStepsDisplay(
            step_title=self.step_title,
            thought=self.thought,
            answer=self.answer,
            critic=self.critic
        )


class ThoughtStepsDisplay(BaseModel):
    step_title:str
    thought:str
    answer:str
    critic:str

    
    def md(self):
        return f'''
            #### {self.step_title}
            
            {self.thought}
            
            {self.answer}
            
            {self.critic}
            '''



class BigMessage(BaseModel):
    role:str
    content:ThoughtStepsDisplay | str
    thoughts:list[ThoughtStepsDisplay|None]|None = Field(default_factory=list)
    
    def to_message(self):
        if isinstance(self.content, ThoughtStepsDisplay):
            content = self.content.model_dump()
            content = ThoughtSteps(**content).model_dump_json()
        
        else:
            content = self.content
        
        return {
            "role": self.role,
            "content": content,
        }
    
class Message(BaseModel):
    role:str
    content:str

class InputConfig(BaseModel):
    prompt: str = Field(..., description="prompt to use")
    model: str = Field(..., description="model to use")
    max_tokens: int = Field(..., description="max tokens to use")
    temperature: float = Field(..., description="temperature to use")
    top_p: float = Field(..., description="top p to use")
    n: int = Field(..., description="number of responses to generate")
    stream: bool = Field(..., description="whether to stream the response")
    stop: list[str] | None = Field(..., description="stop sequences")
    force_max_steps: bool = Field(False, description="force max steps")

    def to_dict(self):
        return self.model_dump()

    def to_json(self):
        return json.dumps(self.to_dict())

