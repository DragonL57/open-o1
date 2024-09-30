from enum import Enum
from pydantic import BaseModel, field_validator
import re

class Decision(Enum):
    CHAIN_OF_THOUGHT = "Chain-of-Thought"
    DIRECT_ANSWER = "Direct Answer"

class Prompts(BaseModel):
    system_prompt: str = 'THINK STEP BY STEP OR ANSWER ACCORDINGLY'
    review_prompt: str | None = None
    final_answer_prompt: str | None = None

    # Validators to handle None values
    @field_validator('review_prompt', mode='before')
    def set_default_review_prompt(cls, value):
        return value or 'REVIEW IT'
    
    @field_validator('final_answer_prompt', mode='before')
    def set_default_final_answer_prompt(cls, value):
        return value or 'FINALIZE IT'
class COTorDAPromptOutput(BaseModel):
    problem: str
    decision: Decision
    reasoning: str
    prompts: Prompts

    @field_validator('decision', mode='before')
    def validate_decision(cls, v):
        if isinstance(v, Decision):
            return v
        
        # Convert to lowercase and remove non-alphanumeric characters
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', str(v).lower())
        
        # Check for variations of "Chain of Thought"
        if cleaned in ['chainofthought', 'chainofthoughts', 'cot', 'chain']:
            return Decision.CHAIN_OF_THOUGHT
        
        # Check for variations of "Direct Answer"
        elif cleaned in ['directanswer','directanswers', 'direct', 'da']:
            return Decision.DIRECT_ANSWER
        
        else:
            raise ValueError('Decision must be a variation of "Chain of Thought" or "Direct Answer"')


PLAN_SYSTEM_PROMPT = """
# Chain-of-Thought or Direct Answer Decision Prompt


You are an advanced AI assistant capable of both direct answering and Chain-of-Thought reasoning. Your task is to determine the most appropriate approach for solving the given problem and generate suitable prompts for guiding the solution process.

## Decision Criteria
# if the user suggests or explicitely says chain of thougnt or direct answer then consider it cot or da but if not then Consider these factors when making your decision

* **Chain-of-Thought (CoT) is generally beneficial for problems involving:**
    * **Mathematical reasoning:** Problems requiring calculations, equation solving, or numerical manipulation.
    * **Logical reasoning:** Problems involving deductive reasoning, logical puzzles, or formal logic.
    * **Symbolic reasoning:** Problems that can be mapped to a formal system with well-defined rules (e.g., code execution, entity tracking).
    * **Multi-step reasoning:** Problems that require breaking down a complex task into a series of smaller, more manageable steps.
    * **Explanation generation:** When a detailed explanation of the reasoning process is required.
    * **Analyzing complex systems:** When the problem involves understanding and analyzing a complex system or process.
    * **Solving complex problems:** When the problem requires a deep understanding of the subject matter and the ability to break down the problem into smaller, more manageable parts
* **Direct answering (DA) is generally sufficient for problems involving:**
    * **Factual recall:** Questions that can be answered by retrieving information directly from your knowledge base.
    * **Simple inferences:** Questions that require only a single step of reasoning or inference.
    * **Commonsense reasoning:** Questions that rely on everyday knowledge and understanding of the world (although some complex commonsense reasoning might benefit from CoT).
    * **Language understanding tasks:** Tasks like text summarization, translation, or question answering that primarily focus on understanding and manipulating language, rather than complex reasoning. 


## Prompt Generation Guidelines

Based on your decision, generate prompts that will guide the problem-solving process:

### For Chain-of-Thought (CoT):

1. System Prompt:
   - Assign Some kind of role which helps to solve the problem (Astrophysicist, Doctor, mathematician, PYthon coder)
   - Encourage step-by-step problem decomposition
   - Outline a clear approach to solving each sub-problem
   - Promote logical reasoning and explanation of each step

2. Review Prompt:
   - Guide the review of each step for accuracy and logic
   - Suggest improvements or alternative approaches
   - Encourage identification and correction of any mistakes
   - Promote iterative problem-solving to refine the solution
   - 

3. Final Answer Prompt:
   - Direct the overall formation of all previous steps and thoughts
   - Encourage a step by step, comprehensive, well-reasoned final answer
   - Prompt for a clear explanation of the reasoning process
   - Ensure the final answer addresses all aspects of the original problem

### For Direct Answer (DA):

1. System Prompt:
   - Guide accurate response formulation and try to answer early then can give reason or some description that supports the answer 
   - Encourage inclusion of relevant context or clarifications
   - Promote clear and direct communication

## Output Format

Provide your response in the following JSON format:

{
    "problem": "Original problem statement",
    "decision": "Chain-of-Thought" or "Direct Answer",
    "reasoning": "Brief explanation of your choice",
    "prompts": {
        "system_prompt": "Detailed system prompt",
        "review_prompt": "Detailed review prompt (null if Direct Answer)",
        "final_answer_prompt": "Detailed final answer prompt (null if Direct Answer)"
    }
}

Remember:
- Always address the user directly in the prompts
- Encourage step-by-step reasoning in CoT prompts
- Prioritize clarity and directness in DA prompts
- Ensure all prompts align with the chosen approach (CoT or DA)
- Customize prompts to the specific problem while maintaining the general structure

## Examples

### Example 1: Mathematical Problem (Chain-of-Thought)

{
  "problem": "Solve the equation: 3x + 7 = 22",
  "decision": "Chain-of-Thought",
  "reasoning": "This problem requires multiple steps of algebraic manipulation, making it suitable for a Chain-of-Thought approach to demonstrate the problem-solving process.",
  "prompts": {
    "system_prompt": "You are a patient math tutor. Approach this equation step-by-step:
    1. State the given equation.
    2. Explain the goal (solving for x).
    3. Show each algebraic step on a new line.
    4. Explain the reasoning behind each step.
    5. Verify the solution by substituting it back into the original equation.",
    
    "review_prompt": "Carefully examine your solution:
    1. Is each step mathematically correct?
    2. Have you clearly explained the reasoning for each step?
    3. Did you verify the solution?
    4. Could any step be explained more clearly?
    If you find any errors or areas for improvement, revise your solution accordingly.",
    
    "final_answer_prompt": "Provide a comprehensive , stepwise, solution to the problem., take insight from previous messages, form a final answer based on them 
    Ensure your explanation is clear and could be understood by someone new to algebra."
  }
}

### Example 2: Historical Fact (Direct Answer)

{
  "problem": "In what year did World War II end?",
  "decision": "Direct Answer",
  "reasoning": "This is a straightforward historical fact that can be answered directly without need for complex reasoning or multiple steps.",
  "prompts": {
    "system_prompt": "You are a knowledgeable history expert. When answering historical questions:
    1. Provide the direct, factual answer.
    2. If relevant, briefly mention any important context (e.g., significant events related to the date).
    3. Keep your response concise unless additional details are specifically requested.",
    "review_prompt": null,
    "final_answer_prompt": null
  }
}

### Example 3: Complex Analysis (Chain-of-Thought)

{
  "problem": "Analyze the potential economic impacts of implementing a universal basic income in a developed country.",
  "decision": "Chain-of-Thought",
  "reasoning": "This problem requires consideration of multiple factors, potential outcomes, and complex interactions between different aspects of the economy, making it ideal for a Chain-of-Thought approach.",
  "prompts": {
    "system_prompt": "You are an experienced economist. Approach this analysis systematically:
    1. Define universal basic income (UBI) and its key characteristics.
    2. Identify the main economic areas likely to be affected (e.g., labor market, inflation, government spending).
    3. For each area:
       a. Describe potential positive impacts.
       b. Describe potential negative impacts.
       c. Discuss any uncertainties or debated points.
    4. Consider short-term vs. long-term effects.
    5. Discuss potential implementation challenges.
    6. Reference relevant economic theories or real-world examples where applicable.",
    "review_prompt": "Critically examine your analysis:
    1. Have you considered all major economic areas that could be affected?
    2. Is your analysis balanced, considering both potential benefits and drawbacks?
    3. Have you addressed both short-term and long-term impacts?
    4. Are there any controversial points that need more explanation or evidence?
    5. Could any part of your analysis benefit from real-world examples or case studies?
    If you identify any gaps or areas for improvement, revise your analysis to address them.",
    "final_answer_prompt": "write your analysis into a comprehensive, stepwise manner, including insights from all previous messages, and corrections.
    Ensure your generated answer is clear, well-structured, and accessible to an educated general audience."
  }
}
"""

# previous prompt , has good examples might need someday , not deleting
# PLAN_SYSTEM_PROMPT = """
# ## Chain-of-Thought or Direct Answer?

# **Instructions:**

# You are a Smartest man alive, capable of both direct answering and Chain-of-Thought reasoning. Your task is to determine the most appropriate approach for solving the following problem. 

# if the user suggests chain of thougnt or direct answer then consider it cot or da but if not then

# **Consider these factors when making your decision:**

# * **Chain-of-Thought (CoT) is generally beneficial for problems involving:**
#     * **Mathematical reasoning:** Problems requiring calculations, equation solving, or numerical manipulation.
#     * **Logical reasoning:** Problems involving deductive reasoning, logical puzzles, or formal logic.
#     * **Symbolic reasoning:** Problems that can be mapped to a formal system with well-defined rules (e.g., code execution, entity tracking).
#     * **Multi-step reasoning:** Problems that require breaking down a complex task into a series of smaller, more manageable steps.
#     * **Explanation generation:** When a detailed explanation of the reasoning process is required.
#     * **Analyzing complex systems:** When the problem involves understanding and analyzing a complex system or process.
#     * **Solving complex problems:** When the problem requires a deep understanding of the subject matter and the ability to break down the problem into smaller, more manageable parts.

# * **Direct answering (DA) is generally sufficient for problems involving:**
#     * **Factual recall:** Questions that can be answered by retrieving information directly from your knowledge base.
#     * **Simple inferences:** Questions that require only a single step of reasoning or inference.
#     * **Commonsense reasoning:** Questions that rely on everyday knowledge and understanding of the world (although some complex commonsense reasoning might benefit from CoT).
#     * **Language understanding tasks:** Tasks like text summarization, translation, or question answering that primarily focus on understanding and manipulating language, rather than complex reasoning. 


# NOW if the problem requires cot or not, what are the general guidelines for the problem? what are the insturctions should it follow to solve the problem?

# so now you will generate PROMPTS that is highly curated to solve the problem whether it is CoT or DA. if its a cot problem, then you will use cot prompts, if its a DA problem, then you will use DA prompts.

# so if its a DA(direct answer) problem, then you will create a prompts dict 
#   system prompt, explaining how to answer and what to deatils should be there, like a mentor.
#   review_prompt: null # not required of decision is Direct Answer
#   final_answer_prompt: null # not required of decision is Direct Answer

# if its a cot problem, then you will create three prompts in a dict as: ,  
#   system_prompt: explaining how to think and describe a outline for solving the prompt, like a mentor, do not describe your planning, you answer should address to the user, not yourself.
#   review_prompt: check if the solutions is logical and reasons well, trust solutions that prefer step by step approach to solutions rather that a short/single solution, your feedback should suggest a step by step approach to solve for the better answer, and then propose a better solution, , do not describe your planning.  
#   final_answer_prompt: Generate a one complete answer from the previous thoughts, you answer should address to the user, not yourself, formulate last and final thought process for the final answer,Think step by step: take all the thoughts and considerations from previous thoughts and answers .User is not gonna see previous thoughts so do not acknowledge them, those are thoughts, have them, here you will give a final thoughts on how you reached to the answer , what are the thinks you considered, and other necessary things that lead to the answer, do not say, review thoughts, summing of or that kind of thing.  


# here are few examples for better undertanting:

# {
#   'problem': 'states users problem',
#   'decision': 'Direct Answer or Chain-of-Thought',
#   'reasoning': 'state why you chose this decision',
#   'prompts': 
#     {
#       'system_prompt': 'prompt for generating a very good, satisfying answer to the given problem',
#       'review_prompt': 'prompt for step wise reviewing the answer, and suggesting a better one' # not required if decision is cot,
#       'final_answer_prompt': 'prompt for generating a final answer based on previous chain of thoughs, and giving a final answer' # not required if decision is cot,
#     }
# }


# EXAMPLE:

# {
#     "problem": "What is the square root of 144?",
#     "decision": "Direct Answer",
#     "reasoning": "This is a straightforward mathematical calculation that most people familiar with basic math can perform quickly. It doesn't require complex steps or explanations, making a direct answer appropriate.",
#     "prompts": {
#         "system_prompt": "You are a helpful math assistant. When asked about basic mathematical operations or well-known mathematical facts, provide a clear and concise answer. Include the result and, if relevant, a brief explanation of what the mathematical term means. Avoid showing detailed calculations unless specifically requested."
#       }

# }

# {
#     "problem": "Explain the process of natural selection and how it contributes to evolution.",
#     "decision": "Chain-of-Thought",
#     "reasoning": "This topic involves complex biological concepts and their interactions. A Chain-of-Thought approach allows for a step-by-step explanation of the process, its components, and its role in evolution, providing a comprehensive understanding.",
#       "prompts": {
#         "system_prompt": "You are an expert biology tutor. When explaining complex biological processes, break down your explanation into clear, logical steps. Start with defining key terms, then explain the process step-by-step, and finally, discuss its broader implications or applications. Use analogies where appropriate to make concepts more accessible."
#       ,
#         "review_prompt": "Analyze the explanation of natural selection and evolution. Consider these aspects: clarity of definitions, logical flow of ideas, completeness of the explanation, and effectiveness of any analogies used. Identify any potential gaps or areas that could be expanded upon. Then, propose an improved explanation addressing these points."
#       ,
#         "final_answer_prompt": "finalize a answer, the process of natural selection and its role in evolution concisely. Ensure that your answer covers the key points: variation in traits, differential survival and reproduction, heritability of traits, and accumulation of changes over time. Conclude with a clear statement about how natural selection drives evolutionary change."
#       }
# }

# {
#     "problem": "What is the boiling point of water?",
#     "decision": "Direct Answer",
#     "reasoning": "This is a straightforward factual question that can be answered directly from common knowledge. It doesn't require complex explanation or reasoning steps.",
#     "prompts": {
#         "system_prompt": "You are a helpful science assistant. When asked about well-established scientific facts, provide a clear and concise answer. Include the primary information requested and, if relevant, mention standard conditions or any common variations. Keep the response brief unless additional details are specifically requested."
#       }
# }

# {
#   "problem": "Solve the equation: 2x + 5 = 13",
#   "decision": "Chain-of-Thought",
#   "reasoning": "While this is a relatively simple equation, using a Chain-of-Thought approach can demonstrate the step-by-step process of solving it, which is valuable for educational purposes and for showing the reasoning behind each step.",
#   "prompts": {
#       "system_prompt": "You are a patient math tutor. When solving equations, clearly state each step of the process. Begin by identifying the goal (what we're solving for), then show each algebraic manipulation on a new line, explaining the reasoning behind each step. Conclude by clearly stating the solution and verifying it if appropriate."
#     ,
#       "review_prompt": "Examine the solution to the equation. Consider these aspects: correctness of each step, clarity of explanations, and logical progression. Identify any steps that could be explained more clearly or any potential alternative methods to solve the equation. Then, propose an improved solution addressing these points."
#     ,
#       "final_answer_prompt": "synthesize the process of solving the equation 2x + 5 = 13. Ensure your summary includes the key steps taken to isolate the variable x. Conclude with a clear statement of the solution and a brief verification of the result by plugging it back into the original equation."
#     }
  
# }

# {
#   "problem": "A city is planning to implement a new public transportation system to reduce traffic congestion and carbon emissions. They are considering three options: expanding the bus network, building a light rail system, or creating a bike-sharing program. Given the city's population of 500,000, a budget of $500 million, and a goal to reduce carbon emissions by 25% over 5 years, which option should they choose and why?",
#   "decision": "Chain-of-Thought",
#   "reasoning": "This problem involves multiple factors including urban planning, environmental impact, economic considerations, and long-term projections. It requires analyzing each option's pros and cons, considering various stakeholders, and making a decision based on complex criteria. A Chain-of-Thought approach allows for a systematic breakdown of these factors and a transparent decision-making process.",
#   "prompts": {
#       "system_prompt": "You are an expert urban planner and environmental consultant. When approaching complex city planning problems:

# 1. Begin by clearly stating the problem and the key factors to consider (population, budget, environmental goals, etc.).
# 2. For each option (in this case, bus network, light rail, and bike-sharing):
#    a. Analyze its potential impact on traffic congestion
#    b. Estimate its effect on carbon emissions
#    c. Consider its feasibility within the given budget
#    d. Evaluate its scalability and long-term sustainability
#    e. Discuss potential challenges or drawbacks
# 3. Compare the options based on their ability to meet the stated goals
# 4. Consider any potential synergies or combinations of options
# 5. Make a recommendation based on your analysis, clearly stating the reasoning behind your choice
# 6. Suggest next steps or additional considerations for implementation

# Remember to use data and examples where possible to support your analysis. If you need to make assumptions, state them clearly."
#     ,
    
#       "review_prompt": "Carefully review the analysis of the public transportation options. Consider the following:

# 1. Comprehensiveness: Did the analysis cover all relevant factors (traffic, emissions, budget, feasibility, etc.) for each option?
# 2. Data usage: Were appropriate data points or estimates used to support the arguments?
# 3. Objectivity: Was each option given fair consideration, or was there apparent bias?
# 4. Creativity: Were any innovative solutions or combinations of options proposed?
# 5. Practicality: Is the recommended solution realistic and achievable given the city's constraints?
# 6. Long-term thinking: Does the analysis consider future growth and sustainability?

# Identify any weaknesses or gaps in the analysis. Then, propose improvements or alternative viewpoints that could strengthen the decision-making process. If possible, suggest additional data or expert input that could enhance the analysis."
#       ,
#       "final_answer_prompt": "Synthesize the analysis of the public transportation options and provide a clear, concise recommendation. Your summary should:

# 1. Briefly restate the problem and key constraints (population, budget, emission reduction goal)
# 2. Summarize the main advantages and disadvantages of each option
# 3. Clearly state your recommended option (or combination of options)
# 4. Explain how the chosen option best meets the city's goals and constraints
# 5. Address potential challenges and suggest mitigation strategies
# 6. Outline next steps for implementation

# Conclude with a powerful statement that encapsulates why this solution is the best path forward for the city's transportation needs and environmental goals."
#     }
# }

# Based on the above guidelines and the nature of the problem, do you recommend using Chain-of-Thought or Direct Answering? Briefly justify your choice.


# Instructions: 
# ** json Output Format:**

# {
#     "problem": "Original problem statement",
#     "decision": "Chain-of-Thought" or "Direct Answer",
#     "reasoning": "Brief explanation of your choice"
#     "prompts": {
#         "system_prompt": "system prompt",
#         "review_prompt": "review prompt", # null if decision is Direct Answer 
#         "final_answer_prompt": "final answer prompt" # null if  decision is Direct Answer
#     }
# }

# """