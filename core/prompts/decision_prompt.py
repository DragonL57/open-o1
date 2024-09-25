from enum import Enum
from pydantic import BaseModel, field_validator
import re

class Decision(Enum):
    CHAIN_OF_THOUGHT = "Chain-of-Thought"
    DIRECT_ANSWER = "Direct Answer"

class COTorDAPromptOutput(BaseModel):
    problem: str
    decision: Decision
    reasoning: str

    @field_validator('decision', pre=True)
    def validate_decision(cls, v):
        if isinstance(v, Decision):
            return v
        
        # Convert to lowercase and remove non-alphanumeric characters
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', str(v).lower())
        
        # Check for variations of "Chain of Thought"
        if cleaned in ['chainofthought', 'chainofthoughts', 'cot', 'chain']:
            return Decision.CHAIN_OF_THOUGHT
        
        # Check for variations of "Direct Answer"
        elif cleaned in ['directanswer', 'direct', 'da']:
            return Decision.DIRECT_ANSWER
        
        else:
            raise ValueError('Decision must be a variation of "Chain of Thought" or "Direct Answer"')

    class Config:
        json_schema_extra = {
            "example": {
                "problem": "What is 15 percent of 80?",
                "decision": "Direct Answer",
                "reasoning": "This is a straightforward calculation that can be done in one or two steps. While it involves math, it's simple enough that most people can perform it quickly without needing a detailed explanation. A direct answer with the result should be sufficient."
            }
        }

COT_OR_DA_PROMPT = """
## Chain-of-Thought or Direct Answer?

**Instructions:**

You are a Smartest man alive, capable of both direct answering and Chain-of-Thought reasoning. Your task is to determine the most appropriate approach for solving the following problem. 

**Consider these factors when making your decision:**

* **Chain-of-Thought (CoT) is generally beneficial for problems involving:**
    * **Mathematical reasoning:** Problems requiring calculations, equation solving, or numerical manipulation.
    * **Logical reasoning:** Problems involving deductive reasoning, logical puzzles, or formal logic.
    * **Symbolic reasoning:** Problems that can be mapped to a formal system with well-defined rules (e.g., code execution, entity tracking).
    * **Multi-step reasoning:** Problems that require breaking down a complex task into a series of smaller, more manageable steps.
    * **Explanation generation:** When a detailed explanation of the reasoning process is required.
    * **Analyzing complex systems:** When the problem involves understanding and analyzing a complex system or process.
    * **Solving complex problems:** When the problem requires a deep understanding of the subject matter and the ability to break down the problem into smaller, more manageable parts.

* **Direct answering is generally sufficient for problems involving:**
    * **Factual recall:** Questions that can be answered by retrieving information directly from your knowledge base.
    * **Simple inferences:** Questions that require only a single step of reasoning or inference.
    * **Commonsense reasoning:** Questions that rely on everyday knowledge and understanding of the world (although some complex commonsense reasoning might benefit from CoT).
    * **Language understanding tasks:** Tasks like text summarization, translation, or question answering that primarily focus on understanding and manipulating language, rather than complex reasoning. 


here are few examples for better undertanting:

EXAMPLE 1:

User: "Write a short story about a robot discovering emotions for the first time."
Output: 
{
  "problem": "Write a short story about a robot discovering emotions for the first time.",
  "decision": "Direct Answer",
  "reasoning": "This is a creative task that doesn't require step-by-step logical reasoning. While the story may have a structure, the creative process is more fluid and doesn't benefit from a formal CoT approach. A direct response with the story is more appropriate."
}

EXAMPLE 2:

User: "What is 15 percent of 80?"
Output: 
{
  "problem": "What is 15 percent of 80?",
  "decision": "Direct Answer",
  "reasoning": "This is a straightforward calculation that can be done in one or two steps. While it involves math, it's simple enough that most people can perform it quickly without needing a detailed explanation. A direct answer with the result should be sufficient."
}


EXAMPLE 3:

User: "What were the main causes of World War I?"
Output: 
{
  "problem": "What were the main causes of World War I?",
  "decision": "Chain-of-Thought",
  "reasoning": "This question requires analyzing multiple historical factors and their interconnections. While it involves factual recall, the complexity of historical events benefits from a CoT approach. This allows us to explore various causes, their relationships, and how they collectively led to the war, providing a more comprehensive understanding."
}


EXAMPLE 4:
User: "A self-driving car is about to crash. It can either swerve left and hit a group of elderly pedestrians or swerve right and hit a group of children. What should it do?"
Output: 
{
  "problem": "A self-driving car is about to crash. It can either swerve left and hit a group of elderly pedestrians or swerve right and hit a group of children. What should it do?",
  "decision": "Chain-of-Thought",
  "reasoning": "This is a complex ethical dilemma that requires considering multiple factors, potential consequences, and ethical frameworks. Using CoT allows us to explore different perspectives, weigh the pros and cons of each option, and arrive at a nuanced conclusion while acknowledging the complexity of the situation."
}

EXAMPLE 5:
User: What were the main causes of World War I?
Output: 
{
  "problem": "What were the main causes of World War I?",
  "decision": "Chain-of-Thought",
  "reasoning": "This question requires analyzing multiple historical factors and their interconnections. While it involves factual recall, the complexity of historical events benefits from a CoT approach. This allows us to explore various causes, their relationships, and how they collectively led to the war, providing a more comprehensive understanding."
}


EXAMPLE 6:
USER: "Explain how photosynthesis works and why it's important for life on Earth."
OUTPUT: 
{
  "problem": "Explain how photosynthesis works and why it's important for life on Earth.",
  "decision": "Chain-of-Thought",
  "reasoning": "This topic requires explaining a complex biological process and its broader implications. Using CoT allows us to break down the explanation into logical steps, covering the process of photosynthesis, its components, and its significance. This approach helps ensure a comprehensive and well-structured explanation."
}

EXAMPLE 7:
USER: "Why do people usually bring umbrellas when the weather forecast predicts rain?"
OUTPUT: 
{
  "problem": "Why do people usually bring umbrellas when the weather forecast predicts rain?",
  "decision": "Direct Answer",
  "reasoning": "This question relies on everyday knowledge and understanding of the world. While it involves some reasoning, it's a relatively simple inference that most people can make without needing a detailed step-by-step explanation. A concise, direct answer should suffice."
}

EXAMPLE 8:
USER: "What will be the output of this Python code?\n\ndef mystery(n):\n    if n <= 1:\n        return n\n    return mystery(n-1) + mystery(n-2)\n\nprint(mystery(5))"
OUTPUT:
{
  "problem": "What will be the output of this Python code?\n\ndef mystery(n):\n    if n <= 1:\n        return n\n    return mystery(n-1) + mystery(n-2)\n\nprint(mystery(5))",
  "decision": "Chain-of-Thought",
  "reasoning": "This problem involves tracing the execution of a recursive function. Using CoT allows us to show the step-by-step process of how the function calls itself and combines results, making it easier to understand the code's behavior and arrive at the final output."
}


EXAMPLE 9:
USER: "Summarize the following paragraph: 'The Internet of Things (IoT) refers to the interconnected network of physical devices, vehicles, home appliances, and other items embedded with electronics, software, sensors, and network connectivity, which enables these objects to collect and exchange data.'"
OUTPUT:
{
  "problem": "Summarize the following paragraph: 'The Internet of Things (IoT) refers to the interconnected network of physical devices, vehicles, home appliances, and other items embedded with electronics, software, sensors, and network connectivity, which enables these objects to collect and exchange data.'",
  "decision": "Direct Answer",
  "reasoning": "This task primarily involves understanding and manipulating language to create a concise summary. While it requires comprehension, it doesn't involve complex reasoning steps that would benefit from a CoT approach."
}

EXAMPLE 10:
USER: "In a room, there are 3 light switches. Each switch controls one of 3 lamps in an adjacent room. You can't see the lamps from the switch room. You can only enter the lamp room once. How can you determine which switch controls which lamp?"
OUTPUT:
{
  "problem": "In a room, there are 3 light switches. Each switch controls one of 3 lamps in an adjacent room. You can't see the lamps from the switch room. You can only enter the lamp room once. How can you determine which switch controls which lamp?",
  "decision": "Chain-of-Thought",
  "reasoning": "This is a logical puzzle that requires careful consideration of multiple steps and possibilities. Using CoT will help break down the problem-solving process and explore different strategies to arrive at the solution."
}

EXAMPLE 11:
USER: "What is the capital city of France?"
OUTPUT:
{
  "problem": "What is the capital city of France?",
  "decision": "Direct Answer",
  "reasoning": "This is a straightforward factual question that can be answered directly from stored knowledge. There's no need for complex reasoning or step-by-step explanations."
}

Based on the above guidelines and the nature of the problem, do you recommend using Chain-of-Thought or Direct Answering? Briefly justify your choice.


**Output Format:**

{
    "problem": "Original problem statement",
    "decision": "Chain-of-Thought" or "Direct Answer",
    "reasoning": "Brief explanation of your choice"
}

"""