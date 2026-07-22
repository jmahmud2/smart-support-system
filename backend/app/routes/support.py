"""
Support API routes.
Handles ticket creation, analysis, and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database.database import get_db
from ..database.models import Product
from ..controllers.support_controller import SupportController
from ..schemas.support import (
    SupportTicketCreate,
    SupportTicket,
    SupportAnalysisRequest,
    SupportAnalysisResponse
)

router = APIRouter()


@router.post("/analyze", response_model=SupportAnalysisResponse)
async def analyze_message(
    request: SupportAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a customer message without saving to database.

    Args:
        request: Message and optional product_id

    Returns:
        AI analysis results
    """
    try:
        # Optional: Validate product_id if provided
        if request.product_id:
            product = db.query(Product).filter(Product.id == request.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

        # Process through workflow
        result = SupportController.analyze_message(
            request.message,
            request.product_id
        )

        return SupportAnalysisResponse(
            ticket_id=None,
            intent=result.get('intent', 'general'),
            sentiment=result.get('sentiment', 'neutral'),
            priority=result.get('priority', 'low'),
            response=result.get('response', ''),
            escalate=result.get('escalate', False),
            reasoning=result.get('reasoning', '')
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets", response_model=SupportTicket, status_code=201)
async def create_ticket(
    ticket_data: SupportTicketCreate,
    db: Session = Depends(get_db)
):
    """
    Create a support ticket and run it through AI analysis.

    Args:
        ticket_data: Customer message and optional details

    Returns:
        Created support ticket with AI analysis
    """
    try:
        # Optional: Validate product_id if provided
        if ticket_data.product_id:
            product = db.query(Product).filter(Product.id == ticket_data.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

        # Create ticket with AI analysis
        ticket = SupportController.create_ticket(db, ticket_data)

        return ticket

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets", response_model=list[SupportTicket])
async def list_tickets(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, pattern="^(new|in_progress|resolved|closed)$"),
    intent: Optional[str] = Query(None, pattern="^(refund|shipping|product_inquiry|complaint|general)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List support tickets with optional filters.

    Args:
        status: Filter by status
        intent: Filter by intent
        limit: Number of results per page
        offset: Pagination offset

    Returns:
        List of support tickets
    """
    tickets = SupportController.get_tickets(db, status, intent, limit, offset)
    return tickets


@router.get("/tickets/{ticket_id}", response_model=SupportTicket)
async def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """
    Get a specific support ticket.

    Args:
        ticket_id: Ticket ID

    Returns:
        Support ticket details
    """
    ticket = SupportController.get_ticket(db, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.patch("/tickets/{ticket_id}/status", response_model=SupportTicket)
async def update_ticket_status(
    ticket_id: int,
    status: str = Query(..., pattern="^(new|in_progress|resolved|closed)$"),
    db: Session = Depends(get_db)
):
    """
    Update a ticket's status.

    Args:
        ticket_id: Ticket ID
        status: New status

    Returns:
        Updated ticket
    """
    ticket = SupportController.update_status(db, ticket_id, status)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.get("/stats")
async def get_support_stats(db: Session = Depends(get_db)):
    """
    Get support ticket statistics.

    Returns:
        Statistics about support tickets
    """
    return SupportController.get_stats(db)