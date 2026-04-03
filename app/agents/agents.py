from langchain_groq import ChatGroq
from app.schemas.pydanticschema import ResumeExtract,JobDescriptionExtract,SkillGapAnalysis
from app.core.config import settings
from app.tools.tools import roadmap_planner_agent_tools
from app.prompts.roadmap_planner_agent_prompt import roadmap_planner_agent_prompt
from typing import Any
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
import os

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

