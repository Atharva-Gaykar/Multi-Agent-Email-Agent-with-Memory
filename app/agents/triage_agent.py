from langchain_groq import ChatGroq
from app.schemas.triage_agent_schema import TriageOutput
from app.core.config import settings
from app.prompts.triage_agent_prompt import triage_agent_template
from typing import Any
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
import os


if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY


triage_agent=ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.1,
)


triage_agent=triage_agent.with_structured_output(
    TriageOutput,
    method="json_schema",
    include_raw=True,
    strict=True
)


