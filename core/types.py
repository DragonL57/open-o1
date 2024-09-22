from dataclasses import dataclass
from textwrap import dedent

from pydantic import BaseModel, Field, ValidationError
import json
from textwrap import dedent

class ThoughtSteps(BaseModel):
    step_title: str = Field(..., description="steps to use for the problem/question")
    thought: str = Field(..., description="internal monologue, this contails your questions and its answers")
    next_step: bool =  Field(..., description="Does the problem require more thinking? if yes then set to true, else set to false,")
    answer: str | None = Field(..., description="generate a answer based on inner thoughts")
    critic: str | None = Field(..., description="criticize the answer, try to prove it wrong , have a different perspective, fight it")
    is_final_answer: bool = Field(..., description="this is final answer no next step required,")
    
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
        return dedent(f'''
            {self.step_title}
            ### Thought
            {self.thought}
            ### Answer
            {self.answer}
            ### Critic
            {self.critic}
            ''')



class BigMessage(BaseModel):
    role:str
    content:ThoughtSteps | str
    thoughts:list[ThoughtSteps|None]|None = Field(default_factory=list)
    
    def to_message(self):
        return {
            "role": self.role,
            "content": self.content.model_dump_json() if isinstance(self.content, ThoughtSteps) else self.content,
        }
    
class Message(BaseModel):
    role:str
    content:str
