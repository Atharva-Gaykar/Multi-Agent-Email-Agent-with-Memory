

from langchain_core.prompts import PromptTemplate

summarize_agent_initial_prompt_template = """Write a summary of the following email body. 
Include links (if any) and key info (req for reply) if given and maintain a email  structure showing who sent it:

"{body}"

CONCISE SUMMARY:"""


summarize_agent_refine_template = """
We have an existing summary: {existing_answer}
We have more email content below:
------------
{body}
------------
Given the new context, refine the summary. 
Ensure you keep the repository links and the sender's info.
"""

summarize_agent_initial_prompt = PromptTemplate(template=summarize_agent_initial_prompt_template, input_variables=["body"])

summarize_agent_refine_prompt = PromptTemplate(template=summarize_agent_refine_template, input_variables=["existing_answer", "body"])