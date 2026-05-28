
from app.state.state import EmailAgentState
from langchain_google_community import GmailToolkit
from app.gmail_auth import gmail_toolkit ,api_resource

def check_previous_email_exist_node(state: EmailAgentState):
    # Search for previous interactions with this sender
    search_tool = [t for t in gmail_toolkit.get_tools() if t.name == "search_gmail"][0]
    results = search_tool.invoke(f"from:{state['sender_email_id']}")

    if len(results) == 0:
        # No history found - flag this for the conditional edge
        return {"draft_context": "No relevant past context found."}

def after_mail_check(state: EmailAgentState):
    # Check the actual state value
    if state.get("draft_context") == "No relevant past context found.":
        return "email_writing_agent"
    return "prepare_context_node"