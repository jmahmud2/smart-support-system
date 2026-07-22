"""
Auto-reply service for sending AI-generated responses to customers.
"""

from sqlalchemy.orm import Session
from ..database.models import SupportTicket
from ..workflow.workflow import process_message


def auto_reply_to_ticket(db: Session, ticket_id: int) -> dict:
    """
    Send an AI-generated auto-reply to a customer.
    In production, this would integrate with an email/SMS service.
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        return {"success": False, "error": "Ticket not found"}
    
    # If ticket already has a response, don't override
    if ticket.response and ticket.response != "Thank you for your inquiry...":
        return {"success": False, "error": "Ticket already has a response"}
    
    # Process the message through AI workflow
    result = process_message(ticket.customer_message)
    
    # Update ticket with AI response
    ticket.response = result.get('response')
    ticket.intent = result.get('intent')
    ticket.sentiment = result.get('sentiment')
    ticket.priority = result.get('priority')
    ticket.escalate = result.get('escalate', False)
    ticket.reasoning = result.get('reasoning')
    
    db.commit()
    db.refresh(ticket)
    
    return {
        "success": True,
        "ticket_id": ticket.id,
        "response": ticket.response,
        "auto_replied": True
    }


def auto_reply_to_all_new_tickets(db: Session) -> dict:
    """Send auto-replies to all 'new' tickets without responses"""
    tickets = db.query(SupportTicket).filter(
        SupportTicket.status == 'new',
        SupportTicket.response.is_(None)
    ).all()
    
    results = []
    for ticket in tickets:
        result = auto_reply_to_ticket(db, ticket.id)
        results.append(result)
    
    return {
        "total_processed": len(results),
        "successful": sum(1 for r in results if r.get('success')),
        "failed": sum(1 for r in results if not r.get('success'))
    }