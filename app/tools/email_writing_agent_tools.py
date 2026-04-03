from langgraph.types import interrupt
from googleapiclient.errors import HttpError
from app.schemas.email_writing_agent_tools_schema import CreateDraftSchema, SendDraftSchema
from langchain.tools import tool
from langchain_google_community import GmailToolkit


@tool(args_schema=CreateDraftSchema)
def create_gmail_draft(to: str, subject: str, body: str):
    """Creates a new Gmail draft after human approval."""
    
    # 1. Pause and ask for review
    response = interrupt({
        "action": "review_draft",
        "data": {"to": to, "subject": subject, "body": body}
    })

    toolkit = GmailToolkit() 
    draft_tool = [t for t in toolkit.get_tools() if t.name == "create_gmail_draft"][0]

    # 2. Handle the response
    if response.get("status") == "approved":
        reply = draft_tool.invoke({
            "message": body,
            "to": [to],
            "subject": subject
        })

        draft_id=reply.split(":")[1].strip()
        return f"Successfully created draft : <id>{draft_id}</id> <subject>{subject}</subject> <body>{body}</body>"
    
    else:
        # Get the feedback from the user response
        feedback = response.get("feedback", "User rejected without specific notes.")
        
        # We return this to the AGENT so it can read it and rewrite the draft
        return f"DRAFT REJECTED BY USER. Feedback: {feedback}. Please rewrite the draft based on this feedback and try again."
    



@tool(args_schema=SendDraftSchema)
def send_draft_by_id(draft_id: str):
    """Sends a finalized Gmail draft by its ID."""
    try:
        toolkit = GmailToolkit()
        result = toolkit.api_resource.users().drafts().send(
            userId="me", body={"id": draft_id}
        ).execute()
        return f"SUCCESS: Sent! a Gmail with  ID: <id>{result['id']}</id>"
    except HttpError as error:
        if error.resp.status == 404:
            return f"ERROR: Draft ID {draft_id} was not found. Please verify the ID or check if it was already sent."
        return f"ERROR: An unexpected error occurred: {error}"


email_writing_agent_tools = [
    create_gmail_draft,
    send_draft_by_id
]