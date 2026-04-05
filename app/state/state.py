from typing import Any, Dict, List, Optional, Tuple,TypedDict,Literal
from typing import Annotated, Sequence
from langgraph.graph import StateGraph,END,START
from langgraph.types import interrupt  
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from app.schemas.triage_agent_schema import TriageLabel



class EmailAgentState(TypedDict):


    user_email_id:  str
    user_id:        int 
    
    sender_email_body:      str

    sender_email_id:         str

    sender_subject:        str     
    
    user_name:      str                  

    # Safety node output
    is_safe:        Optional[bool]
    safety_reason:  Optional[str]

    # Triage node output
    triage_label:   Optional[TriageLabel]

    requires_reply: Optional[bool]

    triage_notes:   Optional[str]

    priority_score: Optional[int] 

    draft_id: Optional[str]
    
    sent_message_id: Optional[str]  
    
    draft_context:Optional[str]     

    memory_agent_messages:Annotated[Sequence[BaseMessage],add_messages]   


    reply_subject:  Optional[str] 

    draft_email:    Optional[str]

    draft_reason:   Optional[str]


    context_agent_messages:Annotated[Sequence[BaseMessage],add_messages]

    email_sent: Optional[bool]

   
    human_approved: Optional[bool]
    reply_email_body:Optional[str]  

    messages:Annotated[Sequence[BaseMessage],add_messages]
    
           