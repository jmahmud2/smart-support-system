"""
Support API routes.
Handles ticket creation, analysis, and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from ..database.database import get_db
from ..database.models import Product, SupportTicket as SupportTicketModel
from ..controllers.support_controller import SupportController
from ..schemas.support import (
    SupportTicketCreate,
    SupportTicket,
    SupportAnalysisRequest,
    SupportAnalysisResponse
)

router = APIRouter()


class ReplyRequest(BaseModel):
    message: str


@router.get("/agent/me")
async def get_current_agent():
    """Get the current agent's information."""
    # In production, this would come from JWT/session
    # For now, we'll return a default agent
    return {
        "name": "Sarah Johnson",
        "role": "agent",
        "email": "sarah.johnson@company.com"
    }


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
            sentiment_explanation=result.get('sentiment_explanation') or "",
            priority=result.get('priority', 'low'),
            priority_reasoning=result.get('priority_reasoning') or "",
            response=result.get('response', ''),
            escalate=result.get('escalate', False),
            escalate_reasoning=result.get('escalate_reasoning') or "",
            reasoning=result.get('reasoning') or "",
            recommended_products=result.get('recommended_products', []),
            assigned_agent=result.get('assigned_agent') or "",
            ticket_summary=result.get('ticket_summary') or "",
            similar_tickets=result.get('similar_tickets', [])
        )

    except Exception as e:
        print(f"❌ Error in analyze: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets", response_model=SupportTicket, status_code=201)
async def create_ticket(
    ticket_data: SupportTicketCreate,
    db: Session = Depends(get_db)
):
    """Create a support ticket and run it through AI analysis."""
    try:
        print(f"🔵 Received ticket creation request")
        print(f"   Name: {ticket_data.customer_name}")
        print(f"   Email: {ticket_data.customer_email}")
        print(f"   Message: {ticket_data.customer_message[:50]}...")
        
        if ticket_data.product_id:
            product = db.query(Product).filter(Product.id == ticket_data.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

        ticket = SupportController.create_ticket(db, ticket_data)
        print(f"✅ Ticket created: #{ticket.id}")
        return ticket

    except Exception as e:
        print(f"❌ Route error: {e}")
        import traceback
        traceback.print_exc()
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


@router.post("/tickets/{ticket_id}/reply")
async def send_reply(
    ticket_id: int,
    reply_data: ReplyRequest,
    db: Session = Depends(get_db)
):
    """Send a reply to a ticket and mark it as resolved."""
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.response = reply_data.message
    ticket.status = "resolved"
    ticket.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "ticket_id": ticket.id,
        "message": "Reply sent successfully"
    }


@router.get("/tickets/customer/{email}")
async def get_customer_history(
    email: str,
    db: Session = Depends(get_db)
):
    """Get all tickets from a specific customer."""
    tickets = db.query(SupportTicketModel).filter(
        SupportTicketModel.customer_email == email
    ).order_by(SupportTicketModel.created_at.desc()).all()
    return tickets


@router.patch("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: int,
    agent_name: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Assign a ticket to an agent."""
    ticket = SupportController.assign_ticket(db, ticket_id, agent_name)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/tickets/assigned/{agent_name}")
async def get_tickets_by_agent(
    agent_name: str,
    status: Optional[str] = Query(None, pattern="^(new|in_progress|resolved|closed)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get tickets assigned to a specific agent."""
    tickets = SupportController.get_tickets_by_agent(db, agent_name, status, limit, offset)
    return tickets


@router.get("/tickets/unassigned")
async def get_unassigned_tickets(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get tickets that haven't been assigned to anyone."""
    tickets = SupportController.get_unassigned_tickets(db, limit, offset)
    return tickets


# ============ TICKET-CENTRIC AI ROUTES ============

@router.get("/tickets/{ticket_id}/context")
async def get_ticket_context(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get customer context for a ticket."""
    context = SupportController.get_ticket_context(db, ticket_id)
    if not context:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return context


@router.get("/tickets/{ticket_id}/customer-orders")
async def get_customer_orders(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get customer order history for a ticket."""
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if not ticket.customer_email:
        return {"orders": []}
    
    orders = SupportController.get_customer_order_history(db, ticket.customer_email)
    return {"orders": orders}


@router.get("/tickets/{ticket_id}/customer-history")
async def get_customer_ticket_history(
    ticket_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get customer ticket history."""
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if not ticket.customer_email:
        return {"tickets": []}
    
    tickets = SupportController.get_customer_ticket_history(db, ticket.customer_email, limit)
    return {"tickets": tickets}


@router.post("/tickets/{ticket_id}/chat")
async def chat_with_ticket(
    ticket_id: int,
    chat_request: dict,
    db: Session = Depends(get_db)
):
    """Chat with AI about a ticket."""
    question = chat_request.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    result = SupportController.chat_with_ticket(db, ticket_id, question)
    return result


@router.post("/tickets/{ticket_id}/generate-draft")
async def generate_ai_draft(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Generate an AI draft reply for a ticket."""
    ticket = SupportController.generate_ai_draft(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"draft": ticket.ai_draft, "ticket_id": ticket.id}


@router.post("/tickets/{ticket_id}/notes")
async def save_agent_notes(
    ticket_id: int,
    notes_data: dict,
    db: Session = Depends(get_db)
):
    """Save internal agent notes on a ticket."""
    notes = notes_data.get("notes", "")
    ticket = SupportController.save_agent_notes(db, ticket_id, notes)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"success": True, "ticket_id": ticket.id, "notes": ticket.agent_notes}


@router.post("/tickets/seed-orders")
async def seed_sample_orders(
    db: Session = Depends(get_db)
):
    """Seed sample order data for customers."""
    from ..services.customer_context import CustomerContextService
    CustomerContextService.seed_sample_orders(db)
    return {"message": "Sample orders seeded successfully"}


@router.get("/tickets/{ticket_id}/draft")
async def get_ai_draft(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get the latest AI draft for a ticket."""
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"draft": ticket.ai_draft, "ticket_id": ticket.id}