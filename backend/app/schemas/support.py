"""
Pydantic schemas for support ticket operations.
Defines request/response models for the support API.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SupportTicketBase(BaseModel):
    """Base schema for support tickets."""
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_message: str
    product_id: Optional[int] = None


class SupportTicketCreate(SupportTicketBase):
    """Schema for creating a new support ticket."""
    pass


class SupportTicket(SupportTicketBase):
    """Schema for returning support ticket data."""
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

    class Config:
        from_attributes = True


class SupportAnalysisRequest(BaseModel):
    """Request schema for analyzing a customer message."""
    message: str
    product_id: Optional[int] = None


class SupportAnalysisResponse(BaseModel):
    """Response schema for workflow analysis results."""
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