from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SupportTicketBase(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_message: str
    product_id: Optional[int] = None

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicket(SupportTicketBase):
    id: int
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    response: Optional[str] = None
    escalate: bool = False
    reasoning: Optional[str] = None
    status: str = "new"
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SupportAnalysisRequest(BaseModel):
    message: str
    product_id: Optional[int] = None

class SupportAnalysisResponse(BaseModel):
    intent: str
    sentiment: str
    priority: str
    response: str
    escalate: bool
    reasoning: str