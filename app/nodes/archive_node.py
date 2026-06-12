from app.state.state import EmailAgentState
from langchain_core.runnables.config import RunnableConfig
from app.database.connection import get_session
from app.database.utils import save_received_email
from contextlib import contextmanager


# A Context Manager is your code's automatic cleanup crew. Its only job is to open a resource when you need it, and make sure it gets closed the exact moment you are done
session_context=contextmanager(get_session)

# We are converting your simple get_session function into a fully functioning Python Context Manager.
def archive_node(state: EmailAgentState,config: RunnableConfig) -> dict:

    print(f"[ARCHIVE] {state['triage_label']} — {state['sender_subject']}")

    
    session=get_session()

    user_id=state['user_id']

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




# A Context Manager is a brilliant Python tool that automatically handles the setup and cleanup of a resource for you. It guarantees that no matter what happens inside your code—even if an unexpected error crashes the system—your resources (like database connections or files) are safely closed and cleaned up.
# A context manager is a Python utility used to allocate and release resources precisely when we want them to. By wrapping our database generator with @contextmanager, it allows us to use the standard with statement. This guarantees resource safety, ensuring that our database session is automatically and cleanly closed in the finally block, even if our core logic throws a runtime exception.