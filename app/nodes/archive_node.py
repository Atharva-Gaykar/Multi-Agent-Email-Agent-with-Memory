from app.state.state import EmailAgentState
from langchain_core.runnables.config import RunnableConfig
from app.database.connection import get_session
from app.database.utils import save_received_email


def archive_node(state: EmailAgentState,config: RunnableConfig) -> dict:

    print(f"[ARCHIVE] {state['triage_label']} — {state['sender_subject']}")

    
    session=get_session()

    user_id=state['user_id']

    thread_id = config.get("configurable", {}).get("thread_id")

    with get_session() as session:
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