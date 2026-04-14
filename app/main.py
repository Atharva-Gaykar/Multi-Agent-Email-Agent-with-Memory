from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from langgraph.types import Command
import uuid
import logging
from app.graph import graph
from app.state.state import EmailAgentState
from app.database.connection import get_session
from app.database.utils import get_or_create_user
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Email Agent API")

# --- Schemas ---

class EmailProcessRequest(BaseModel):
    thread_id: str
    user_email: EmailStr
    sender_email_id: EmailStr
    sender_subject: str
    sender_email_body: str


class ReviewActionRequest(BaseModel):
    thread_id: str
    user_id: str
    status: str  # "approved" or "rejected"
    feedback: Optional[str] = None


# --- Helper Functions ---

def parse_interrupt(final_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse interrupt from graph state."""
    if "__interrupt__" not in final_state:
        return None

    interrupt_state = final_state.get("__interrupt__")
    if not interrupt_state:
        return None

    interrupt = interrupt_state[0]
    value = getattr(interrupt, "value", {}) or {}

    return {
        "action": value.get("action"),
        "data": value.get("data", {})
    }


# --- Endpoints ---

@app.post("/process-email")
def process_email(request: EmailProcessRequest, db: Session = Depends(get_session)) -> Dict[str, Any]:
    """Process email through the graph pipeline."""
    
    try:
        user = get_or_create_user(db, request.user_email)
        
        thread_id = request.thread_id
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": str(user.id)
            }
        }
        
        input_data = {
            "user_email_id": request.user_email,
            "user_id": user.id,
            "user_name": "Atharva",
            "sender_email_id": request.sender_email_id,
            "sender_subject": request.sender_subject,
            "sender_email_body": request.sender_email_body,
        }

        final_state = graph.invoke(input_data, config=config)

        if final_state.get('triage_label') == "FOLLOW_UP_REQUIRED":
            if "__interrupt__" in final_state and not final_state.get("draft_id"):
                parsed_interrupt = parse_interrupt(final_state)
                if parsed_interrupt:
                    data = parsed_interrupt["data"]

                    return {
                        "status": "needs_review",
                        "thread_id": thread_id,
                        "triage_label": final_state.get("triage_label"),
                        "action": parsed_interrupt["action"],
                        "email_draft": {
                            "to": data.get("to"),
                            "subject": data.get("subject"),
                            "body": data.get("body"),
                        }
                    }

        return {
            "thread_id": thread_id,
            "triage_label": final_state.get("triage_label"),
        }

    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review-action")
def review_action(request: ReviewActionRequest) -> Dict[str, Any]:
    """Resume graph execution based on user review."""
    
    try:
        config = {
            "configurable": {
                "thread_id": request.thread_id,
                "user_id": request.user_id
            }
        }

        if request.status == "rejected":
            payload = Command(resume={
                "status": "rejected",
                "feedback": request.feedback
            })
        elif request.status == "approved":
            payload = Command(resume={
                "status": "approved"
            })
        else:
            raise HTTPException(status_code=400, detail="Invalid status")

        final_state = graph.invoke(payload, config=config)
        
        # Still in review phase
        if "__interrupt__" in final_state and not final_state.get("draft_id"):
            parsed_interrupt = parse_interrupt(final_state)
            if parsed_interrupt:
                data = parsed_interrupt["data"]
                return {
                    "status": "needs_review",
                    "thread_id": request.thread_id,
                    "triage_label": final_state.get("triage_label"),
                    "action": parsed_interrupt["action"],
                    "email_draft": {
                        "to": data.get("to"),
                        "subject": data.get("subject"),
                        "body": data.get("body"),
                    }
                }
        
        # Draft created, review complete
        if final_state.get("draft_id"):
            return {
                "thread_id": request.thread_id,
                "draft_id": final_state["draft_id"],
                "reply_subject": final_state.get("reply_subject"),
                "reply_email_body": final_state.get("reply_email_body"),
            }

    except Exception as e:
        logger.error(f"Error in review action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)