from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from app.agents.memory_manager_agent import memory_manager_agent
from app.prompts.memory_manager_agent_prompt import memory_agent_template
from app.state.state import EmailAgentState
from app.agents.memory_manager_agent import memory_manager_agent 
from app.database.connection import get_session
from app.database.utils import save_sent_email, save_received_email
from langchain_core.messages import AIMessage
from app.utils.token_utils import *

def store_memory_and_data_node(state: EmailAgentState, config: RunnableConfig):
    """
    Synchronous LangGraph node to persist email interaction with robust session handling.
    """
    print("--- Memory Node: Persisting interaction to DB ---")


    body_for_memory_agent=state.get("reply_email_body")
    reply_subject=state.get("reply_subject")
    

    if count_input_tokens(body_for_memory_agent,reply_subject)>100000:
        body_for_memory_agent=summarise_email_body(body_for_memory_agent)

    # 1. Prepare the memory summary
    prompt = memory_agent_template.invoke({
        "user_name": state["user_name"],
        "senders_email_id": state["sender_email_id"],
        "user_email_id": state["user_email_id"],
        "sent_email_body": body_for_memory_agent,
        "incoming_email_body": state["sender_email_body"],
    })

    # 2. Invoke memory agent logic
     

    print("invoking memory manager")

    
    response = memory_manager_agent.invoke(
        {"messages": prompt.to_messages()},
        config=config
    )

    print(response)

    memory_stored_summary = response[0]['value']['content']['summary']

    # 3. Robust Database Operations
    sender_id = state['user_id']
    thread_id = config.get("configurable", {}).get("thread_id")

    # Using 'with' handles opening/closing even if an error occurs
    with get_session() as session:
        try:
            save_sent_email(session, sender_id, thread_id, state)
            save_received_email(session, sender_id, thread_id, state)
            session.commit()
            print("--- Memory Node: DB Save Successful ---")
        except Exception as e:
            session.rollback()
            print(f"--- Memory Node Error: {e} ---")
            raise e

    return {"memory_agent_messages": [AIMessage(content=memory_stored_summary)],"email_sent": True}