from app.state.state import EmailAgentState
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_classic.prompts import PromptTemplate
from app.agents.summarizer_agent import summarizer_agent
from app.prompts.summarizer_agent_prompt import summarize_agent_initial_prompt_template,summarize_agent_refine_template
def summarise_email_body(body: str):
    # Tip: 100 is very small for an email; 500-1000 is usually better
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = [Document(page_content=t) for t in text_splitter.split_text(body)]

    chain = load_summarize_chain(
        llm=summarizer_agent, 
        chain_type="refine",
        question_prompt=summarize_agent_initial_prompt,
        refine_prompt=summarize_agent_refine_prompt,
        document_variable_name="body"  # <--- ADD THIS LINE
    )
    summary = chain.invoke(docs)
    return summary['output_text']


def summarise_email_body_node(state:EmailAgentState)->dict:


    subject=state['sender_subject']
    body=state['sender_email_body']



    summary=summarise_email_body(body)

    return {"sender_email_body":summary}

