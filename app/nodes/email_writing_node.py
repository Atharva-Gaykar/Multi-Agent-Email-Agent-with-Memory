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



def route_after_tools(state: EmailAgentState):
    # Iterate backwards to find the latest ToolMessage
    # This handles cases where the LLM might have sent a text follow-up
    last_tool_msg = next((m for m in reversed(state["messages"]) 
                         if isinstance(m, ToolMessage)), None)

    if not last_tool_msg:
        return "email_writing_agent"

    content_upper = last_tool_msg.content.upper()
    
    # logic 1: If we just successfully SENT the email, go to Parser -> Memory
    if last_tool_msg.name == "send_draft_by_id" and "SUCCESS" in content_upper:
        print("--- ROUTER: Send successful. Moving to Parse/Memory. ---")
        return "store_memory_and_data_node"
    
    # logic 2: If we just created a DRAFT (or the send failed)
    # Go back to agent to talk to the user
    print("--- ROUTER: Draft created or Tool failed. Returning to Agent. ---")
    return "email_writing_agent"