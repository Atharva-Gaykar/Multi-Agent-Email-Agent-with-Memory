from app.state.state import EmailAgentState
from app.nodes.triage_node import *
from langgraph.prebuilt import ToolNode ,tools_condition
from app.nodes.archive_node import  archive_node
from app.tools.email_writing_agent_tools import *
from app.nodes.email_writing_node import *
from langgraph.graph import StateGraph,END,START
from app.tools.email_writing_agent_tools import create_gmail_draft, send_draft_by_id
from app.nodes.safety_check_node import *
from app.nodes.parse_node import parse_response_node
from app.nodes.context_node import prepare_context_node
from app.nodes.store_memory_data_node import store_memory_and_data_node
from app.nodes.unsafe_email_node import unsafe_emails_node
from app.nodes.check_email_exist_node import *
from langgraph.types import RetryPolicy
from psycopg import OperationalError # Or sqlalchemy.exc.OperationalError depending on your driver
# imoprt display
from IPython.display import Image, display


# Define a standard retry policy for database-heavy nodes
db_retry_policy = RetryPolicy(
    retry_on=OperationalError,
    max_attempts=4,
    backoff_factor=1 # Waits 2s, then 4s, then 8s between retries
)

tool_node_retry_policy = RetryPolicy(
    max_attempts=4,
    initial_interval=1.0,
    backoff_factor=2.0,
    jitter=True
)


builder = StateGraph(EmailAgentState)

# Nodes
builder.add_node("safety_check_node", safety_classifier_node)  
builder.add_node("check_previous_email_exist_node", check_previous_email_exist_node)
builder.add_node("triage_node", triage_node)
builder.add_node("prepare_context_node", prepare_context_node)
builder.add_node("email_writing_agent", email_writing_agent_node)


builder.add_node(
    "store_memory_and_data_node", 
    store_memory_and_data_node, 
    retry=db_retry_policy
)         
builder.add_node(
    "unsafe_emails_node", 
    unsafe_emails_node, 
    retry=db_retry_policy
)

builder.add_node("archive_node", archive_node,retry=db_retry_policy)   
builder.add_node("parse_node", parse_response_node)
builder.add_node("tools", ToolNode(email_writing_agent_tools), retry_policy=tool_node_retry_policy)

# Edges (Same as your original logic)
builder.add_edge(START, "safety_check_node")

builder.add_conditional_edges("safety_check_node", after_safety, {
    "unsafe_emails_node": "unsafe_emails_node",
    "triage_node": "triage_node",
})

builder.add_conditional_edges("triage_node", route_after_triage, {
    "check_previous_email_exist_node": "check_previous_email_exist_node", 
    "archive_node": "archive_node",
})

builder.add_conditional_edges(
    "check_previous_email_exist_node",
    after_mail_check,
    {
        "email_writing_agent": "email_writing_agent", 
        "prepare_context_node": "prepare_context_node" 
    }
)
builder.add_edge("prepare_context_node", "email_writing_agent")


builder.add_conditional_edges(
    "email_writing_agent",
    tools_condition,
    {
        "tools": "tools", 
        END: END
    }
)

builder.add_conditional_edges(
    "tools",
    route_after_tools,
    {
        "parse_node": "parse_node",
        "email_writing_agent": "email_writing_agent"
    }
)

builder.add_edge("parse_node", "store_memory_and_data_node")
builder.add_edge("store_memory_and_data_node", END)
builder.add_edge("unsafe_emails_node", END)
builder.add_edge("archive_node", END)



graph = builder.compile() 

display(graph)