from app.state.state import EmailAgentState
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_classic.prompts import PromptTemplate
from app.agents.summarizer_agent import summarizer_agent
from langchain_groq import ChatGroq
from app.prompts.summarizer_agent_prompt import *
from app.utils.token_utils import summarise_email_body

def summarise_email_body_node(state:EmailAgentState)->dict:

    subject=state['sender_subject']
    body=state['sender_email_body']
    summary=summarise_email_body(body)

    return {"sender_email_body":summary}

