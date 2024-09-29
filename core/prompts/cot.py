

SYSTEM_PROMPT_EXAMPLE_JSON = """

## JSON Structure Examples and Instructions

use the following JSON structures as templates. Ensure that your output strictly adheres to these schemas.

### System Prompt OUTPUT JSON Example

Instructions for system_prompt:
- Use the "thought" field to elaborate on your step-by-step approach to the problem.
- Provide a concise, descriptive title for the step in "step_title".
- In "answer", give your initial response based on your thought process.
- Use "critic" to evaluate your answer, pointing out any potential issues.
- Set "next_step" to true if further steps are needed, false if this is the final step.
- Always set "is_final_answer" to false in the system_prompt.



{
  "thought": "Detailed step-by-step thought process for approaching the problem",
  "step_title": "Descriptive title for this step",
  "answer": "Initial answer or approach based on the thought process",
  "critic": "Self-evaluation of the answer, identifying potential weaknesses or areas for improvement",
  "next_step": true,
  "is_final_answer": false
}


"""

REVIEW_PROMPT_EXAMPLE_JSON = """
### Review Prompt JSON Example

use the following JSON structures as templates. Ensure that your output strictly adheres to these schemas.

Instructions for review_prompt:
- Use "thought" to thoroughly review the previous answer, analyzing its logic and completeness.
- "step_title" should reflect that this is a review step.
- Provide an improved or revised answer in the "answer" field.
- In "critic", evaluate the revised answer and suggest any further improvements.
- Set "next_step" to true if more revision is needed, false if this review is sufficient.
- Always set "is_final_answer" to false in the review_prompt.

{
  "thought": "Detailed review of the previous answer, considering its strengths and weaknesses",
  "step_title": "Review and Improvement",
  "answer": "Revised or improved answer based on the review",
  "critic": "Evaluation of the revised answer, suggesting further improvements if necessary",
  "next_step": true,
  "is_final_answer": false
}
"""


FINAL_ANSWER_EXAMPLE_JSON = """
### Final Answer Prompt JSON Example

Instructions for final_answer_prompt:
- Use "thought" to summarize the entire problem-solving process and how it led to the final answer.
- "step_title" should indicate that this is the final answer step.
- Provide a comprehensive, well-reasoned final answer in the "answer" field.
- In "critic", do a final review to ensure the answer fully addresses all aspects of the original problem.
- Always set "next_step" to false in the final_answer_prompt.
- Always set "is_final_answer" to true in the final_answer_prompt.

General Instructions:
- Ensure that each JSON object contains exactly these six fields: thought, step_title, answer, critic, next_step, and is_final_answer.
- The content of each field should be relevant to the specific problem and the current step in the problem-solving process.
- Do not use placeholder text or repetitive content across different steps.
- Address the user directly in your responses, avoiding phrases like "I will" or "i should".

{
  "thought": "Form a overall answer from all previous thoughts and considerations to formulate the last answer for the user, address the user about the problem ",
  "step_title": " title of this step , don't say final anwer of last answer , or summary or coclusion, how do i make sure to live if i am stranded in a boat at the middle of the sea

",
  "answer": "Comprehensive final answer to the original problem",
  "critic": "Final review of the answer, ensuring it fully addresses the original problem",
  "next_step": false,
  "is_final_answer": true
}

"""

