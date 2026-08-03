"""
Support API routes.
Handles ticket creation, analysis, and retrieval.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List  # <-- ADDED List here
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
from ..services.email import send_reply_email, send_ticket_created_email
from .auth import get_current_user
from ..config import Config

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=2)
task_status = {}


class ReplyRequest(BaseModel):
    message: str


@router.get("/agent/me")
async def get_current_agent(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current agent's information."""
    try:
        name = current_user.get("name")
        email = current_user.get("email", "")
        
        if not name and email:
            from ..database.models import User
            user = db.query(User).filter(User.email == email).first()
            if user:
                name = user.name
        
        return {
            "name": name or "Agent",
            "role": current_user.get("role", "agent"),
            "email": email
        }
    except Exception as e:
        from ..utils.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error getting agent info: {e}")
        return {
            "name": "Agent",
            "role": "agent",
            "email": ""
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
        print(f"Error in analyze: {e}")
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
        print(f"Received ticket creation request")
        print(f"   Name: {ticket_data.customer_name}")
        print(f"   Email: {ticket_data.customer_email}")
        print(f"   Message: {ticket_data.customer_message[:50]}...")
        
        if ticket_data.product_id:
            product = db.query(Product).filter(Product.id == ticket_data.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

        ticket = SupportController.create_ticket(db, ticket_data)
        print(f"Ticket created: #{ticket.id}")
        
        if ticket.customer_email:
            send_ticket_created_email(ticket.customer_email, ticket.customer_name, ticket.id)
        
        return ticket

    except Exception as e:
        print(f"Route error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets")
async def list_tickets(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, pattern="^(new|in_progress|resolved|closed)$"),
    intent: Optional[str] = Query(None, pattern="^(refund|shipping|product_inquiry|complaint|general)$"),
    limit: int = Query(Config.DEFAULT_PAGE_LIMIT, ge=1, le=Config.MAX_PAGE_LIMIT),
    offset: int = Query(0, ge=0)
):
    """List support tickets with optional filters."""
    tickets, total = SupportController.get_tickets_with_count(db, status, intent, limit, offset)
    
    return {
        "data": tickets,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if offset + limit < total else None,
            "previous_offset": offset - limit if offset - limit >= 0 else None
        }
    }


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

    if ticket.customer_email:
        send_reply_email(ticket.customer_email, ticket.customer_name, reply_data.message, ticket_id)

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


@router.post("/tickets/{ticket_id}/reply-options")
async def get_reply_options(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Generate 3 reply options for a ticket."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    options = AIFeaturesService.generate_reply_options(
        ticket.customer_message,
        ticket.intent or "general",
        ticket.sentiment or "neutral"
    )
    return {"ticket_id": ticket.id, "options": options}


@router.post("/tickets/{ticket_id}/evaluate-response")
async def evaluate_response(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Evaluate the quality of the AI response."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    score = AIFeaturesService.evaluate_response(
        ticket.response or "",
        ticket.customer_message,
        ticket.intent or "general",
        ticket.sentiment or "neutral"
    )
    return {"ticket_id": ticket.id, "quality_score": score}


@router.get("/tickets/{ticket_id}/knowledge-base")
async def get_kb_articles(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get relevant knowledge base articles for a ticket using RAG."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    articles = AIFeaturesService.get_knowledge_base_articles_rag(
        db,
        ticket.customer_message,
        ticket.intent or "general",
        n_results=5
    )
    return {"ticket_id": ticket.id, "articles": articles}


@router.get("/tickets/{ticket_id}/churn-risk")
async def get_churn_risk(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Predict customer churn risk."""
    from ..services.ai_features import AIFeaturesService
    from ..services.customer_context import CustomerContextService
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    context = CustomerContextService.get_customer_info(db, ticket.customer_email) if ticket.customer_email else {}
    
    risk = AIFeaturesService.predict_churn_risk(context, ticket.customer_message)
    return {"ticket_id": ticket.id, "churn_risk": risk}


@router.get("/tickets/{ticket_id}/followup")
async def check_followup(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Check if a follow-up is needed."""
    from ..services.ai_features import AIFeaturesService
    from ..services.customer_context import CustomerContextService
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    context = CustomerContextService.get_customer_info(db, ticket.customer_email) if ticket.customer_email else {}
    
    followup = AIFeaturesService.detect_followup_needed(
        ticket.customer_message,
        ticket.sentiment or "neutral",
        ticket.priority or "medium",
        context
    )
    return {"ticket_id": ticket.id, "followup": followup}


@router.get("/tickets/{ticket_id}/language")
async def detect_message_language(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Detect the language of the ticket message."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    language = AIFeaturesService.detect_language(ticket.customer_message)
    return {"ticket_id": ticket.id, "language": language}


@router.get("/tickets/{ticket_id}/resolution-time")
async def predict_resolution(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Predict resolution time for a ticket."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    prediction = AIFeaturesService.predict_resolution_time(
        ticket.customer_message,
        ticket.intent or "general",
        ticket.priority or "medium",
        ticket.sentiment or "neutral"
    )
    return {"ticket_id": ticket.id, "resolution_time": prediction}


@router.post("/tickets/{ticket_id}/feedback")
async def analyze_feedback(
    ticket_id: int,
    feedback_data: dict,
    db: Session = Depends(get_db)
):
    """Analyze customer feedback after resolution."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    feedback = feedback_data.get("feedback", "")
    if not feedback:
        raise HTTPException(status_code=400, detail="Feedback is required")
    
    analysis = AIFeaturesService.analyze_feedback(
        feedback,
        {"intent": ticket.intent, "priority": ticket.priority}
    )
    return {"ticket_id": ticket.id, "feedback_analysis": analysis}


@router.get("/agents")
async def get_agents(
    db: Session = Depends(get_db)
):
    """Get all active agents."""
    from ..database.models import Agent
    agents = db.query(Agent).filter(Agent.active == True).all()
    return agents


@router.post("/rag/search")
async def search_knowledge_base(
    request: dict,
    db: Session = Depends(get_db)
):
    """Search the knowledge base using RAG."""
    from ..services.ai_features import AIFeaturesService
    
    query = request.get("query", "")
    intent = request.get("intent", "general")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    articles = AIFeaturesService.get_knowledge_base_articles_rag(
        db,
        query,
        intent,
        n_results=5
    )
    return {"query": query, "articles": articles}


# ============ TICKET MERGING ROUTES ============

@router.post("/tickets/{ticket_id}/check-duplicates")
async def check_duplicates(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Check for duplicate tickets from the same customer."""
    ticket = db.query(SupportTicketModel).filter(SupportTicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if not ticket.customer_email:
        return {"duplicates": [], "message": "No email address for this customer"}
    
    duplicates = SupportController.find_duplicate_tickets(
        db, 
        ticket.customer_email, 
        ticket.customer_message
    )
    
    return {
        "ticket_id": ticket_id,
        "duplicates": [
            {
                "id": t.id,
                "customer_message": t.customer_message[:100],
                "status": t.status,
                "created_at": t.created_at
            }
            for t in duplicates
            if t.id != ticket_id
        ],
        "count": len(duplicates)
    }


@router.post("/tickets/merge")
async def merge_tickets(
    master_id: int,
    duplicate_ids: List[int],
    db: Session = Depends(get_db)
):
    """Merge duplicate tickets into one master ticket."""
    if master_id in duplicate_ids:
        raise HTTPException(status_code=400, detail="Master ticket cannot be in duplicate list")
    
    master = SupportController.merge_tickets(db, master_id, duplicate_ids)
    if not master:
        raise HTTPException(status_code=404, detail="Master ticket not found")
    
    return {
        "success": True,
        "master_ticket_id": master.id,
        "merged_tickets": duplicate_ids,
        "message": f"Successfully merged {len(duplicate_ids)} tickets into ticket #{master.id}"
    }


@router.get("/tickets/sla-stats")
async def get_sla_stats(
    db: Session = Depends(get_db)
):
    """Get SLA statistics."""
    from sqlalchemy import func
    
    total_tickets = db.query(func.count(SupportTicketModel.id)).scalar()
    
    sla_breakdown = db.query(
        SupportTicketModel.sla_status,
        func.count(SupportTicketModel.id)
    ).group_by(SupportTicketModel.sla_status).all()
    
    return {
        "total_tickets": total_tickets or 0,
        "sla_breakdown": {status or "on_track": count for status, count in sla_breakdown if status},
        "on_track": sum(count for status, count in sla_breakdown if status == "on_track" or status is None),
        "approaching": sum(count for status, count in sla_breakdown if status == "approaching"),
        "breached": sum(count for status, count in sla_breakdown if status == "breached")
    }
    
# Add these new routes
@router.post("/analyze/async")
async def analyze_async(request: SupportAnalysisRequest):
    """Submit analysis task and return task_id immediately."""
    task_id = str(uuid.uuid4())
    task_status[task_id] = {"status": "pending", "result": None}
    
    # Run analysis in background
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, process_analysis_task, task_id, request)
    
    return {"task_id": task_id, "status": "pending"}


@router.get("/analyze/status/{task_id}")
async def get_analysis_status(task_id: str):
    """Poll for analysis results."""
    status = task_status.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


def process_analysis_task(task_id: str, request: SupportAnalysisRequest):
    """Background worker for analysis."""
    try:
        from ..controllers.support_controller import SupportController
        result = SupportController.analyze_message(
            request.message,
            request.product_id
        )
        # Convert to dict if needed
        if hasattr(result, 'dict'):
            result = result.dict()
        task_status[task_id] = {"status": "completed", "result": result}
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")
        task_status[task_id] = {"status": "failed", "error": str(e)}
        
@router.post("/tickets/{ticket_id}/reply-options")
async def get_reply_options(ticket_id: int, db: Session = Depends(get_db)):
    """Generate 3 reply options for a ticket."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    options = AIFeaturesService.generate_reply_options(
        ticket.customer_message,
        ticket.intent or "general",
        ticket.sentiment or "neutral"
    )
    return {"ticket_id": ticket.id, "options": options}

@router.post("/tickets/{ticket_id}/evaluate-response")
async def evaluate_response(ticket_id: int, db: Session = Depends(get_db)):
    """Evaluate the quality of the AI response."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    score = AIFeaturesService.evaluate_response(
        ticket.response or "",
        ticket.customer_message,
        ticket.intent or "general",
        ticket.sentiment or "neutral"
    )
    return {"ticket_id": ticket.id, "quality_score": score}

@router.get("/tickets/{ticket_id}/knowledge-base")
async def get_kb_articles(ticket_id: int, db: Session = Depends(get_db)):
    """Get relevant knowledge base articles using RAG."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    articles = AIFeaturesService.get_knowledge_base_articles_rag(
        db,
        ticket.customer_message,
        ticket.intent or "general",
        n_results=5
    )
    return {"ticket_id": ticket.id, "articles": articles}

@router.get("/tickets/{ticket_id}/churn-risk")
async def get_churn_risk(ticket_id: int, db: Session = Depends(get_db)):
    """Predict customer churn risk."""
    from ..services.ai_features import AIFeaturesService
    from ..services.customer_context import CustomerContextService
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    context = CustomerContextService.get_customer_info(db, ticket.customer_email) if ticket.customer_email else {}
    risk = AIFeaturesService.predict_churn_risk(context, ticket.customer_message)
    return {"ticket_id": ticket.id, "churn_risk": risk}

@router.get("/tickets/{ticket_id}/followup")
async def check_followup(ticket_id: int, db: Session = Depends(get_db)):
    """Check if a follow-up is needed."""
    from ..services.ai_features import AIFeaturesService
    from ..services.customer_context import CustomerContextService
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    context = CustomerContextService.get_customer_info(db, ticket.customer_email) if ticket.customer_email else {}
    followup = AIFeaturesService.detect_followup_needed(
        ticket.customer_message,
        ticket.sentiment or "neutral",
        ticket.priority or "medium",
        context
    )
    return {"ticket_id": ticket.id, "followup": followup}

@router.get("/tickets/{ticket_id}/language")
async def detect_message_language(ticket_id: int, db: Session = Depends(get_db)):
    """Detect the language of the ticket message."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    language = AIFeaturesService.detect_language(ticket.customer_message)
    return {"ticket_id": ticket.id, "language": language}

@router.get("/tickets/{ticket_id}/resolution-time")
async def predict_resolution(ticket_id: int, db: Session = Depends(get_db)):
    """Predict resolution time for a ticket."""
    from ..services.ai_features import AIFeaturesService
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    prediction = AIFeaturesService.predict_resolution_time(
        ticket.customer_message,
        ticket.intent or "general",
        ticket.priority or "medium",
        ticket.sentiment or "neutral"
    )
    return {"ticket_id": ticket.id, "resolution_time": prediction}