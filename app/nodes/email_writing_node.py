import json
from langchain_core.runnables import RunnableConfig
from app.state.state import EmailAgentState
from app.agents.email_writing_agent import email_agent
from app.prompts.email_writing_agent_prompt import *
from langchain_core.messages import ToolMessage

def email_writing_agent_node(state: EmailAgentState) -> dict:
    print("--- DEBUG: ENTERING EMAIL_NODE ---")
    messages = state.get("messages", [])

    # 1. Prepare Prompts (Your Style)
    # .to_messages() converts the template into a list: [SystemMessage(...)]
    system_prompt = system_prompt_email_agent_template.invoke({
        "user_name":       state.get("user_name"),
        "draft_context":   state.get("draft_context") or "No relevant past context found.",
        "sender_email_id": state.get("sender_email_id"),
    }).to_messages()

    human_prompt = human_prompt_email_agent_template.invoke({
        "sender_subject":    state.get("sender_subject"),
        "sender_email_body": state.get("sender_email_body"),
        "sender_email_id":   state.get("sender_email_id"),
    }).to_messages()

  
    if len(messages) == 0:
        
        final_prompt = system_prompt + human_prompt
        
    else:
      
        final_prompt = system_prompt + messages

    # 3. Invoke
    response = email_agent.invoke(final_prompt)

    # 4. Return
    return {"messages": [response]}



def route_after_tools(state):

    if state.get("sent_message_id"):
        print("--- ROUTER: Send successful. Moving to Memory. ---")
        return "store_memory_and_data_node"

    return "email_writing_agent"