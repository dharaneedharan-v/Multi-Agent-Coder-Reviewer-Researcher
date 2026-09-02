

from datetime import datetime, timezone
from email import message
from pyclbr import Class
from typing import Annotated, Any, Dict, List, Optional, TypedDict
from urllib import response
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

import uuid
from pydantic import BaseModel, Field
#    Response
class APIResponse(BaseModel):
    code:int = Field(..., example=200)
    status:str = Field(..., example="success")
    message:str = Field(..., example="Operation successful")
    data:Optional[Any]  = None
    error:Optional[Dict] = None
    request_id:str  = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:str  = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ChatRequest(BaseModel):
    message : str 
    customer_id : Optional[int] = None

class ChatResponse(BaseModel):
    response : str 

class GraphState(TypedDict):
    messages:Annotated[list, add_messages]
    is_first_turn:bool
    intent: Optional[str]
    research_context:Optional[str]
    review_feedback:Optional[str]
    review_passed:Optional[bool]
    review_issues:Optional[str]
    final_response:Optional[str]
    retry_count:int 