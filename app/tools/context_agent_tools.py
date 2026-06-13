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
    store: Annotated[BaseStore, InjectedState("store")] = InjectedState("store") 
) -> str:
    """Accepts a SINGLE string query to search the sender's history. Execute this tool multiple times if you need to search for different facts
    """
    
    active_user = state.get("user_id")
    # Using fallback to match alternative naming conventions in your state
    sender_email = state.get("sender_email_id") or state.get("senders_email") 
    
    if not sender_email:
        return "Error: Cannot isolate history. Active sender_email_id is missing from state context."

    metadata_filter = {
        "content.receiver_email_id": sender_email
    }
    
    results = store.search(
        namespace=("email", active_user, "collection"),
        query=query,
        filter=metadata_filter,
        limit=limit
    )
    
    if not results:
        return f"No prior email context found specifically for sender: {sender_email}."
        
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