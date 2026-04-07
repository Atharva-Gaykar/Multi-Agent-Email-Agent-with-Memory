from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_groq import ChatGroq
from app.prompts.context_agent_prompt import context_agent_template
from app.tools.context_agent_tools import context_agent_tools
from typing import Any
from app.persistance.memory_store_checkpointer_config import memory_store

context_agent = create_agent(
    model=ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.1,
    ),
    tools=context_agent_tools,
    store=memory_store,  
    middleware=[
        ToolCallLimitMiddleware[Any,None](
           tool_name="search_memory",
           run_limit=5,
         thread_limit=10,
        )
   ] ,
)