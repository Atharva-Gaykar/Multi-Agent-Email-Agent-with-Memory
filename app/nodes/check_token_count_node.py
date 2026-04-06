from app.state.state import EmailAgentState
from langchain_groq import ChatGroq

llm_for_token_count=ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.1,
)

def count_input_tokens(subject:str ,body:str) -> int:
    text=subject+body
    return llm_for_token_count.get_num_tokens(text)

def check_token_count_node(state: EmailAgentState):
    """
    This is a formal Node. It calculates tokens and can 
    update the state if you add a 'token_count' key to your TypedDict.
    """
    subject = state.get('sender_subject', "")
    body = state.get('sender_email_body', "") 
    
    tokens = count_input_tokens(subject, body)
    print(f"--- NODE: Token Count calculated as {tokens} ---")
    
    # We return the count so it's stored in the state for the next router to see
    return {"sender_email_token_count": tokens}


def check_token_limit_router(state: EmailAgentState):
    """
    Acts as a router to decide if we need summarization.
    """
    if state.get("sender_email_token_count", 0) > 100000:

        return "summarize"
    
    return "triage"
