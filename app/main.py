import os
from app.core.config import settings
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import add_messages
from langgraph.types import Command
import logging
from app.graph import graph
from app.state.state import EmailAgentState
from app.database.connection import get_session
from app.database.utils import get_or_create_user
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from fastapi import Request
from app.database.models import User
from app.utils.email_encode  import encode_email_for_namespace
from app.core.auth import create_access_token,get_current_user
import traceback

# CREATE GMAIL AUTH FILES FROM HF SECRETS



logger = logging.getLogger(__name__)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="AI Email Agent API")

# --- Schemas ---

class EmailProcessRequest(BaseModel):
    thread_id: str
    sender_email_id: EmailStr
    sender_subject: str
    sender_email_body: str


class ReviewActionRequest(BaseModel):
    thread_id: str
    
    status: str  # "approved" or "rejected"
    feedback: Optional[str] = None

class SendEmailRequest(BaseModel):
    thread_id: str
    human_message: str
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


@app.post("/get-user-data")
def get_user_data(user_email: EmailStr, db: Session = Depends(get_session)):
    """Get user data by email."""
    user = get_or_create_user(db, user_email)

    token = create_access_token({
            "id": user.id,
            "email": user_email
        })
    return {"user_id": str(user.id), "email": user.email, "token": token}



@app.post("/process-email")
def process_email(request: EmailProcessRequest, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Process email through the graph pipeline."""
    
    try:
        
        
        thread_id = request.thread_id
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": str(current_user.id),
                "sender_email_id": encode_email_for_namespace(request.sender_email_id ),
            }
        }
        
        input_data = {
            "user_email_id": current_user.email,
            "user_id": current_user.id,
            "user_name": "Atharva",
            "sender_email_id": request.sender_email_id,
            "sender_subject": request.sender_subject,
            "sender_email_body": request.sender_email_body,
        }

        try:

            final_state = graph.invoke(input_data, config=config)
        except Exception as e:
            logger.error(f"Error invoking graph: {str(e)}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Graph invocation error: {str(e)}")

        if final_state.get('triage_label') == "FOLLOW_UP_REQUIRED":
            if "__interrupt__" in final_state and not final_state.get("draft_id"):
                parsed_interrupt = parse_interrupt(final_state)
                if parsed_interrupt:
                    data = parsed_interrupt["data"]

                    return {
                        "status": "needs_review",
                        "thread_id": thread_id,
                        "messages": final_state.get("messages", []),
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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review-action")
def review_action(request: ReviewActionRequest,db: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Resume graph execution based on user review."""
    
    try:
        config = {
            "configurable": {
                "thread_id": request.thread_id,
                "user_id": str(current_user.id),
                
            }
        }

        state=graph.get_state(config)

        sender_email_id=state.values['sender_email_id']

        config["configurable"]["sender_email_id"] = encode_email_for_namespace(sender_email_id)

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

        intermediate_state = graph.invoke(payload, config=config)
        
        # Still in review phase
        if "__interrupt__" in intermediate_state and not intermediate_state.get("draft_id"):
            parsed_interrupt = parse_interrupt(intermediate_state)
            if parsed_interrupt:
                data = parsed_interrupt["data"]
                return {
                    "status": "needs_review",
                    "thread_id": request.thread_id,
                    "triage_label": intermediate_state.get("triage_label"),
                    "action": parsed_interrupt["action"],
                    "email_draft": {
                        "to": data.get("to"),
                        "subject": data.get("subject"),
                        "body": data.get("body"),
                    }
                }
        
        # Draft created, review complete
        if intermediate_state.get("draft_id"):
            return {
                "thread_id": request.thread_id,
                "draft_id": intermediate_state["draft_id"],
                "messages": intermediate_state.get("messages", []),
                "reply_subject": intermediate_state.get("reply_subject"),
                "reply_email_body": intermediate_state.get("reply_email_body"),
            }

    except Exception as e:
        logger.error(f"Error in review action: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/send_email")
def send_email(request: SendEmailRequest,db: Session = Depends(get_session),current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
   
        config = {
            "configurable": {
                "thread_id": request.thread_id,
                "user_id": str(current_user.id),
            }
        }


        state=graph.get_state(config)

        sender_email_id=state.values['sender_email_id']

        config["configurable"]["sender_email_id"] = encode_email_for_namespace(sender_email_id)

        graph.update_state(
          config,
          {"messages": [HumanMessage(content=request.human_message)]},
       as_node="prepare_context_node" 
        )  
        final_state = graph.invoke(None, config=config)

        return {
            "thread_id": request.thread_id,
            "messages": final_state.get("messages", []),
            "sent_message_id": final_state.get("sent_message_id")
        }



# used for local testing

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8080)