from dataclasses import dataclass

@dataclass
class ThoughtSteps:
    step_title:str
    thought:str
    answer:str
    critic:str
        
        
t = ThoughtSteps(step_title="test", thought="thought", answer="answer", critic="critic")
print(t)