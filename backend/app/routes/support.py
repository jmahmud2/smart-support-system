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
    """Analyze a customer message without saving to database."""
    try:
        if request.product_id:
            product = db.query(Product).filter(Product.id == request.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

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
    """Create a support ticket and run it through AI analysis."""
    try:
        if ticket_data.product_id:
            product = db.query(Product).filter(Product.id == ticket_data.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

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
    """List support tickets with optional filters."""
    tickets = SupportController.get_tickets(db, status, intent, limit, offset)
    return tickets


@router.get("/tickets/{ticket_id}", response_model=SupportTicket)
async def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get a specific support ticket."""
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
    """Update a ticket's status."""
    ticket = SupportController.update_status(db, ticket_id, status)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/stats")
async def get_support_stats(db: Session = Depends(get_db)):
    """Get support ticket statistics."""
    return SupportController.get_stats(db)


@router.post("/tickets/{ticket_id}/auto-reply")
async def send_auto_reply(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Send an AI-generated auto-reply to a ticket."""
    result = SupportController.auto_reply_to_ticket(db, ticket_id)
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result


@router.post("/tickets/auto-reply-all")
async def auto_reply_all_new_tickets(
    db: Session = Depends(get_db)
):
    """Send auto-replies to all new tickets."""
    result = SupportController.auto_reply_to_all_new_tickets(db)
    return result


@router.get("/sentiment-trends")
async def get_sentiment_trends(
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=30)
):
    """Get sentiment trends over time."""
    return SupportController.get_sentiment_trends(db, days)


@router.get("/summary")
async def get_ai_summary(
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=30)
):
    """Generate an AI summary of recent tickets."""
    return SupportController.get_ai_summary(db, days)