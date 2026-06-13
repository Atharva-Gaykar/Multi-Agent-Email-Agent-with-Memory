from app.state.state import EmailAgentState
from langchain_google_community import GmailToolkit
from app.gmail_auth import gmail_toolkit ,api_resource
def check_previous_email_exist_node(state: EmailAgentState):
    # Search for previous interactions (both sent and received)
    search_tool = [t for t in gmail_toolkit.get_tools() if t.name == "search_gmail"][0]
    
    # Combined query using Gmail's OR syntax
    query = f"from:{state['sender_email_id']} OR to:{state['sender_email_id']}"
    results = search_tool.invoke(query)

    if len(results) == 0:
        return {"draft_context": "No relevant past context found."}

def after_mail_check(state: EmailAgentState):
    # Check the actual state value
    if state.get("draft_context") == "No relevant past context found.":
        return "email_writing_agent"
    return "prepare_context_node"