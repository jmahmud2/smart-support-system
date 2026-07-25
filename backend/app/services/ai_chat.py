"""
AI Chat service for ticket-centric assistant.
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict
import json

from ..workflow.llm import call_llm
from ..database.models import SupportTicket
from .customer_context import CustomerContextService


class AIChatService:
    """AI chat assistant for ticket context."""

    @staticmethod
    def get_ticket_context(db: Session, ticket_id: int) -> dict:
        """Gather all context for a ticket."""
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            return {}

        customer_info = {}
        if ticket.customer_email:
            customer_info = CustomerContextService.get_customer_info(
                db, ticket.customer_email
            )

        return {
            "ticket": {
                "id": ticket.id,
                "message": ticket.customer_message,
                "intent": ticket.intent,
                "sentiment": ticket.sentiment,
                "priority": ticket.priority,
                "status": ticket.status,
                "escalate": ticket.escalate,
                "summary": ticket.ticket_summary,
                "response": ticket.response,
                "assigned_to": ticket.assigned_to
            },
            "customer": {
                "name": ticket.customer_name,
                "email": ticket.customer_email,
                "order_history": customer_info.get("orders", []),
                "ticket_history": customer_info.get("tickets", []),
                "summary": customer_info.get("summary", {})
            }
        }

    @staticmethod
    def chat(db: Session, ticket_id: int, question: str) -> dict:
        """Process a chat question about a ticket."""
        
        context = AIChatService.get_ticket_context(db, ticket_id)
        if not context:
            return {"answer": "Ticket not found.", "context": None}

        # Build prompt with context
        prompt = f"""
        You are an AI assistant helping a customer support agent.
        You have access to the following information about the customer and their ticket.

        TICKET INFORMATION:
        - Ticket ID: {context['ticket']['id']}
        - Customer Message: {context['ticket']['message']}
        - Intent: {context['ticket']['intent']}
        - Sentiment: {context['ticket']['sentiment']}
        - Priority: {context['ticket']['priority']}
        - Status: {context['ticket']['status']}
        - Escalate: {context['ticket']['escalate']}
        - AI Summary: {context['ticket']['summary']}
        - AI Response Draft: {context['ticket']['response']}
        - Assigned Agent: {context['ticket']['assigned_to']}

        CUSTOMER INFORMATION:
        - Name: {context['customer']['name']}
        - Email: {context['customer']['email']}
        - Total Tickets: {context['customer']['summary'].get('total_tickets', 0)}
        - Resolved Tickets: {context['customer']['summary'].get('resolved_tickets', 0)}
        - Open Tickets: {context['customer']['summary'].get('open_tickets', 0)}
        - Escalated Tickets: {context['customer']['summary'].get('escalated_tickets', 0)}
        - Sentiment Score: {context['customer']['summary'].get('sentiment_score', 0)}

        ORDER HISTORY:
        {json.dumps(context['customer']['order_history'], indent=2)}

        TICKET HISTORY:
        {json.dumps(context['customer']['ticket_history'], indent=2)}

        AGENT QUESTION: {question}

        Provide a clear, helpful response to the agent. If asked to draft a reply, write a professional response.
        If asked about order history, list the products they ordered.
        If asked about previous tickets, summarize their history.
        If asked for a summary, provide a concise overview.

        Keep your response professional and actionable.
        """

        try:
            response = call_llm(prompt)
            return {"answer": response, "context": context}
        except Exception as e:
            return {"answer": f"Error processing question: {str(e)}", "context": context}