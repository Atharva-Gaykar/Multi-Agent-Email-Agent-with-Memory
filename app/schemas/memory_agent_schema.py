from pydantic import BaseModel, Field
from typing import Optional

class EmailMemory(BaseModel):
    """Memory entry representing a specific email interaction between users.""" 
    
    user_email_id: str = Field(
        ..., # Use ... to indicate it is required
        description="The users email_id"
    )
    
    receiver_email_id: str = Field(
        ..., 
        description="The email address of the person with whom user is communicating."
    )
    
    content: str = Field(
        ..., 
        description="A concise summary of the key information, intent, and decisions found in the emails.The content should be stored using user name"
    )