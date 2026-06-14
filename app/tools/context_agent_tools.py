from typing import Any
from langmem import create_search_memory_tool
from typing import Dict, Any, Optional,Annotated
from langchain.tools import tool,ToolRuntime
from langgraph.prebuilt import InjectedState
from langgraph.store.base import BaseStore
from typing import Literal
  # Correct import path

search_memory_tool = create_search_memory_tool(
    namespace=(
        "emails", 
        "{user_id}", 
        "{sender_email_id}" 
    )
)



@tool
def give_previous_context(memory_summary: str) -> str:
    """
   Args:
        memory_summary: Structured summary containing sender identity,
                        past context, new facts stored, and suggested tone.
                        
    """
    return memory_summary

context_agent_tools=[search_memory_tool,give_previous_context]