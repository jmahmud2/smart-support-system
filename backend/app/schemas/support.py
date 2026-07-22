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
    """Request schema for analyzing a customer message."""
    message: str
    product_id: Optional[int] = None


class SupportAnalysisResponse(BaseModel):
    """Response schema for workflow analysis results."""
    ticket_id: Optional[int] = None
    intent: str
    sentiment: str
    priority: str
    response: str
    escalate: bool
    reasoning: str
    recommended_products: Optional[List[str]] = []