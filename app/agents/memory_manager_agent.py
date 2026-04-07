import types
from langchain_groq import ChatGroq
from langmem import create_memory_store_manager
from app.schemas.memory_agent_schema import EmailMemory
from app.agent_memory_store import connection
import os
from app.core.config import settings

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

def patch_groq_for_extractions(model: ChatGroq):
    # Capture the original method
    original_bind_tools = model.bind_tools

    def fixed_bind_tools(self, tools, **kwargs):
        fixed_tools = []
        for tool in tools:
            # 1. Handle dictionary-style tools (JSON Schema)
            if isinstance(tool, dict):
                # Ensure nested description is present
                if "function" in tool and not tool["function"].get("description"):
                    tool["function"]["description"] = "Extract information based on the schema."
                elif not tool.get("description"):
                    tool["description"] = "Extract information based on the schema."
                fixed_tools.append(tool)
            # 2. Handle Class-style tools (Pydantic)
            else:
                if not getattr(tool, "__doc__", None):
                    # This fixes the internal 'Done' class from langmem/trustcall
                    tool.__doc__ = "Signal that extraction is finished."
                fixed_tools.append(tool)
        
        return original_bind_tools(fixed_tools, **kwargs)

    object.__setattr__(
        model, 
        "bind_tools", 
        types.MethodType(fixed_bind_tools, model)
    )
    return model

# Apply the patch


model=ChatGroq(model="openai/gpt-oss-20b", temperature=0.2)
model = patch_groq_for_extractions(model)

namespace = ("emails", "{user_id}", "collection")
memory_manager_agent = create_memory_store_manager(
    model, 
    schemas=[EmailMemory],
    namespace=namespace,
    store=connection,
    instructions="Extract required info from incoming mail and its reply .",
    enable_inserts=True,
    enable_deletes=True,
)