from app.agents.triage_agent import triage_agent
from app.prompts.triage_agent_prompt import triage_agent_template
from app.schemas.triage_agent_schema import TriageOutput
from app.state.state import EmailAgentState
def triage_node(state: dict) -> dict:
   
    triage_agent_prompt =triage_agent_template.invoke(
        {
            "sender_subject": state["sender_subject"],
            "sender_body": state["sender_email_body"],
            "user_name": state["user_name"],
        }
    )
    result = triage_agent.invoke(triage_agent_prompt.to_messages())
    parsed: TriageOutput = result["parsed"]
    return {
        "triage_label":   parsed.triage_label,
        "requires_reply": parsed.requires_reply,
        "triage_notes":   parsed.triage_notes,
        "priority_score": parsed.priority_score,
    }


def route_after_triage(state: EmailAgentState):
    # This is a ROUTER, so it returns a STRING name of the next node
    label = state["triage_label"]
     # Go to the node that formats the prompt
    if label == "FOLLOW_UP_REQUIRED":
        return "check_previous_email_exist_node"
    
    return "archive_node"