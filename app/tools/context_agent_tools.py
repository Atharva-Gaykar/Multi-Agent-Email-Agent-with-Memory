from langmem import create_search_memory_tool
from langchain.tools import tool

search_memory_tool = create_search_memory_tool(
    namespace=(
        "email",
        "{user_id}",
        "collection"
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