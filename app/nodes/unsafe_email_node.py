from app.state.state import EmailAgentState
from langchain_core.runnables.config import RunnableConfig
from app.database.connection import get_session
from app.database.utils import save_received_email
from contextlib import contextmanager

session_context=contextmanager(get_session)

def unsafe_emails_node(state: EmailAgentState, config: RunnableConfig) -> dict:
    """
    Handles emails flagged as unsafe by persisting them to the database 
    and logging the security reason.
    """
    print(f"--- [QUARANTINE SIGNAL] {state['sender_subject']} ---")
    print(f"Reason: {state['safety_reason']}")

    user_id = state['user_id']
    thread_id = config.get("configurable", {}).get("thread_id")

    with session_context() as session:
        try:
            # 2. Persist the received email even if it's unsafe (for records/logging)
            save_received_email(session, user_id, thread_id, state)

            session.commit()
            print("--- [QUARANTINE] Data persisted successfully ---")
            
        except Exception as e:
            # 4. Rollback in case of an OperationalError or SSL timeout
            session.rollback()
            print(f"--- [QUARANTINE ERROR] Failed to persist unsafe email: {e} ---")
         
            raise e

    return {}