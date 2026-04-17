from langgraph.types import interrupt
from googleapiclient.errors import HttpError
from app.schemas.email_writing_agent_tools_schema import CreateDraftSchema, SendDraftSchema
from langchain.tools import tool
from langchain_google_community import GmailToolkit
from typing import Annotated, Union
from langchain_core.tools import InjectedToolCallId, tool
from langchain.tools import ToolRuntime
from langgraph.types import Command
from langchain_core.messages import SystemMessage, HumanMessage,ToolMessage,AIMessage,BaseMessage
from langgraph.graph import END

@tool(args_schema=CreateDraftSchema)
def create_gmail_draft(
    to: Union[str, list], 
    subject: str, 
    body: str,
    tool_call_id: Annotated[str, InjectedToolCallId] # Injected ID
):
    """Creates a new Gmail draft after human approval."""
    
    if isinstance(to, list):
        to = str(to[0]) if len(to) > 0 else "ERROR"
    
    if to == "ERROR":
        return "ERROR: 'to' parameter is empty."

    # 1. Human-in-the-loop Interrupt
    response = interrupt({
        "action": "review_draft",
        "data": {"to": to, "subject": subject, "body": body}
    })

    toolkit = GmailToolkit() 
    draft_tool = [t for t in toolkit.get_tools() if t.name == "create_gmail_draft"][0]

    # 2. Handle Logic
    if response.get("status") == "approved":
        reply = draft_tool.invoke({"message": body, "to": [to], "subject": subject})
        try:
            draft_id = reply.split(":")[1].strip()

            content = f"Draft created. User You MUST confirm before calling send_draft()."
            
            # UPDATE STATE: Save draft_id directly
            return Command(
                update={
                    "draft_id": draft_id, 
                    "reply_subject": subject,
                    "reply_email_body": body,
                    "messages": [ToolMessage(content, tool_call_id=tool_call_id)]
                },goto=END
            )
        except IndexError:
            return f"Draft created, but response parsing failed: {reply}"
    else:
        feedback = response.get("feedback", "User rejected.")
        return f"DRAFT REJECTED BY USER. Feedback: {feedback}. Please rewrite."
    

#---------------------------------------------------------------------------


def send_draft(
    tool_call_id: Annotated[str, InjectedToolCallId],runtime: ToolRuntime # Injected ID
):
    """Sends a finalized Gmail draft by its ID."""

    try:
        toolkit = GmailToolkit()
        result = toolkit.api_resource.users().drafts().send(
            userId="me", body={"id": runtime.state["draft_id"]}
        ).execute()
        
        sent_id = result['id']
        content = f"SUCCESS: Sent! a Gmail"
        
        # UPDATE STATE: Save sent_message_id directly
        return Command(
            update={
                "sent_message_id": sent_id,
                "messages": [ToolMessage(content, tool_call_id=tool_call_id)]
            }
        )
    except HttpError as error:
        error_msg = f"ERROR: {error}"
        return Command(
            update={"messages": [ToolMessage(error_msg, tool_call_id=tool_call_id)]}
        )



email_writing_agent_tools = [
    create_gmail_draft,
    send_draft
]