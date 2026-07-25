"""
Pydantic schemas for support ticket operations.
"""

from pydantic import BaseModel
from typing import Optional, List
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
    sentiment_explanation: Optional[str] = None
    priority: Optional[str] = None
    priority_reasoning: Optional[str] = None
    response: Optional[str] = None
    escalate: bool = False
    escalate_reasoning: Optional[str] = None
    reasoning: Optional[str] = None
    status: str = "new"
    created_at: datetime
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    assigned_agent: Optional[str] = None
    ticket_summary: Optional[str] = None
    customer_id: Optional[str] = None
    order_history: Optional[str] = None
    agent_notes: Optional[str] = None
    ai_draft: Optional[str] = None

    class Config:
        from_attributes = True


class SupportAnalysisRequest(BaseModel):
    message: str
    product_id: Optional[int] = None
    ticket_id: Optional[int] = None  # For context-aware analysis
    question: Optional[str] = None   # For AI chat


class SupportAnalysisResponse(BaseModel):
    ticket_id: Optional[int] = None
    intent: str
    sentiment: str
    sentiment_explanation: Optional[str] = ""
    priority: str
    priority_reasoning: Optional[str] = ""
    response: str
    escalate: bool
    escalate_reasoning: Optional[str] = ""
    reasoning: str = ""
    recommended_products: Optional[List[str]] = []
    assigned_agent: Optional[str] = ""
    ticket_summary: Optional[str] = ""
    similar_tickets: Optional[List[dict]] = []


class AgentChatRequest(BaseModel):
    ticket_id: int
    question: str


class AgentChatResponse(BaseModel):
    answer: str
    context: Optional[dict] = None