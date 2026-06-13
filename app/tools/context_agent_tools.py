from typing import Any
from langmem import create_search_memory_tool
from langchain.tools import tool
from typing import Dict, Any, Optional,Annotated
from langchain.tools import tool
from langgraph.prebuilt import InjectedState
from langgraph.store.base import BaseStore

@tool
def search_sender_memory_tool(
    query: str,
    limit: int = 3,
    # 1. Inject the entire Graph state at runtime
     state: Annotated[Dict[str, Any], InjectedState] = InjectedState,
    
    # 2. Inject the compiled graph storage layer
    store: BaseStore = InjectedState("store") 
) -> str:
    """Search long-term memory for specific historical email contexts.
    This tool automatically scopes the search to the active sender interaction.
    """
    
    # Extract the runtime sender/receiver information directly from your graph state
    # Replace keys with your exact LangGraph state schema keys (e.g., state.get("current_sender"))
    active_user = state.get("user_id")
    sender_email = state.get("sender_email_id") 
    
    # Fail gracefully if mandatory identification is missing in the state
    if not sender_email:
        return "Error: Cannot isolate history. Active sender_email_id is missing from state context."

    # Formulate a strict metadata dictionary check matching your EmailMemory schema.
    # We look for records where the communication partner matches the sender.
    metadata_filter = {
        "receiver_email_id": sender_email
    }
    
    # Query your PostgresStore with explicit structural filters
    results = store.search(
        namespace=("email", active_user, "collection"),
        query=query,
        filter=metadata_filter,
        limit=limit
    )
    
    if not results:
        return f"No prior email context found specifically for sender: {sender_email}."
        
    # Format structural outputs cleanly for your Context Agent
    formatted_memories = []
    for item in results:
        val = item.value
        formatted_memories.append(
            f"--- Past Interaction Summary ---\n"
            f"Sender: {val.get('user_email_id')}\n"
            f"Receiver: {val.get('receiver_email_id')}\n"
            f"Context Summary: {val.get('summary')}\n"
        )
        
    return "\n".join(formatted_memories)


@tool
def give_previous_context(memory_summary: str) -> str:
    """
   Args:
        memory_summary: Structured summary containing sender identity,
                        past context, new facts stored, and suggested tone.
                        
    """
    return memory_summary

context_agent_tools=[search_sender_memory_tool,give_previous_context]