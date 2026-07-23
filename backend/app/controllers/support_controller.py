"""
Support controller for handling business logic related to support tickets.
Coordinates between the database, workflow, and API routes.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta, timezone

from ..database.models import SupportTicket, Product
from ..schemas.support import SupportTicketCreate
from ..workflow.workflow import process_message
from ..workflow.llm import call_llm


class SupportController:
    """Handles support ticket operations including AI analysis."""

    @staticmethod
    def analyze_message(message: str, product_id: Optional[int] = None) -> dict:
        """Process a customer message through the AI workflow."""
        result = process_message(message)
        if product_id:
            result['product_id'] = product_id
        return result

    @staticmethod
    def create_ticket(db: Session, ticket_data: SupportTicketCreate) -> SupportTicket:
        """Create a new support ticket and run it through the AI workflow."""
        workflow_result = process_message(ticket_data.customer_message)

        ticket = SupportTicket(
            customer_name=ticket_data.customer_name,
            customer_email=ticket_data.customer_email,
            customer_message=ticket_data.customer_message,
            product_id=ticket_data.product_id,
            intent=workflow_result.get('intent'),
            sentiment=workflow_result.get('sentiment'),
            priority=workflow_result.get('priority'),
            response=workflow_result.get('response'),
            escalate=workflow_result.get('escalate', False),
            reasoning=workflow_result.get('reasoning'),
            status='new'
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Optional[SupportTicket]:
        """Get a support ticket by ID."""
        return db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    @staticmethod
    def get_tickets(
        db: Session,
        status: Optional[str] = None,
        intent: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SupportTicket]:
        """Get a list of support tickets with optional filters."""
        query = db.query(SupportTicket)

        if status:
            query = query.filter(SupportTicket.status == status)
        if intent:
            query = query.filter(SupportTicket.intent == intent)

        return query.order_by(SupportTicket.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def update_status(db: Session, ticket_id: int, status: str) -> Optional[SupportTicket]:
        """Update a ticket's status."""
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            return None

        ticket.status = status
        if status in ['resolved', 'closed']:
            ticket.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get support ticket statistics."""
        from sqlalchemy import func

        total_tickets = db.query(func.count(SupportTicket.id)).scalar()

        status_breakdown = db.query(
            SupportTicket.status,
            func.count(SupportTicket.id)
        ).group_by(SupportTicket.status).all()

        intent_breakdown = db.query(
            SupportTicket.intent,
            func.count(SupportTicket.id)
        ).group_by(SupportTicket.intent).all()

        escalated_count = db.query(func.count(SupportTicket.id)).filter(
            SupportTicket.escalate == True
        ).scalar()

        return {
            "total_tickets": total_tickets or 0,
            "status_breakdown": {status: count for status, count in status_breakdown if status},
            "intent_breakdown": {intent: count for intent, count in intent_breakdown if intent},
            "escalated_count": escalated_count or 0,
            "escalation_rate": round((escalated_count / total_tickets * 100) if total_tickets > 0 else 0, 2)
        }

    @staticmethod
    def auto_reply_to_ticket(db: Session, ticket_id: int) -> dict:
        """Send an AI-generated auto-reply to a customer."""
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            return {"success": False, "error": "Ticket not found"}

        if ticket.response and "Thank you for your" not in ticket.response[:50]:
            return {"success": False, "error": "Ticket already has a response"}

        result = process_message(ticket.customer_message)

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

    @staticmethod
    def auto_reply_to_all_new_tickets(db: Session) -> dict:
        """Send auto-replies to all 'new' tickets without responses."""
        tickets = db.query(SupportTicket).filter(
            SupportTicket.status == 'new',
            SupportTicket.response.is_(None)
        ).all()

        results = []
        for ticket in tickets:
            result = SupportController.auto_reply_to_ticket(db, ticket.id)
            results.append(result)

        return {
            "total_processed": len(results),
            "successful": sum(1 for r in results if r.get('success')),
            "failed": sum(1 for r in results if not r.get('success'))
        }

    @staticmethod
    def get_sentiment_trends(db: Session, days: int = 7) -> dict:
        """Get sentiment trends over time."""
        from sqlalchemy import func

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        results = db.query(
            func.date(SupportTicket.created_at).label('date'),
            SupportTicket.sentiment,
            func.count(SupportTicket.id).label('count')
        ).filter(
            SupportTicket.created_at >= start_date
        ).group_by(
            func.date(SupportTicket.created_at),
            SupportTicket.sentiment
        ).all()

        dates = {}
        for result in results:
            date_str = str(result.date)
            if date_str not in dates:
                dates[date_str] = {'positive': 0, 'neutral': 0, 'negative': 0}
            sentiment = result.sentiment or 'neutral'
            if sentiment in dates[date_str]:
                dates[date_str][sentiment] = result.count

        total_sentiment = db.query(
            SupportTicket.sentiment,
            func.count(SupportTicket.id).label('count')
        ).group_by(SupportTicket.sentiment).all()

        sentiment_distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        for result in total_sentiment:
            if result.sentiment and result.sentiment in sentiment_distribution:
                sentiment_distribution[result.sentiment] = result.count

        return {
            'trends': dates,
            'distribution': sentiment_distribution,
            'period': f'Last {days} days'
        }

    @staticmethod
    def get_ai_summary(db: Session, days: int = 7) -> dict:
        """Generate an AI summary of recent tickets."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        tickets = db.query(SupportTicket).filter(
            SupportTicket.created_at >= start_date
        ).limit(50).all()

        if not tickets:
            return {"summary": "No recent tickets to summarize."}

        ticket_data = []
        for ticket in tickets:
            ticket_data.append({
                'id': ticket.id,
                'intent': ticket.intent,
                'sentiment': ticket.sentiment,
                'priority': ticket.priority,
                'message': ticket.customer_message[:100] if ticket.customer_message else ''
            })

        prompt = f"""
        Generate a brief executive summary of these customer support tickets from the last {days} days.

        Ticket data:
        {ticket_data}

        Please provide:
        1. Total tickets and key trends
        2. Top issues identified
        3. Recommendations for improvement

        Keep it concise and professional.
        """

        summary = call_llm(prompt)

        return {
            'period': f'Last {days} days',
            'total_tickets': len(tickets),
            'summary': summary
        }

    @staticmethod
    def assign_ticket(db: Session, ticket_id: int, agent_name: str) -> Optional[SupportTicket]:
        """Assign a ticket to an agent."""
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            return None

        ticket.assigned_to = agent_name
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_tickets_by_agent(
        db: Session,
        agent_name: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SupportTicket]:
        """Get tickets assigned to a specific agent."""
        query = db.query(SupportTicket).filter(SupportTicket.assigned_to == agent_name)

        if status:
            query = query.filter(SupportTicket.status == status)

        return query.order_by(SupportTicket.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_unassigned_tickets(
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> List[SupportTicket]:
        """Get tickets that haven't been assigned to anyone."""
        return db.query(SupportTicket).filter(
            SupportTicket.assigned_to.is_(None)
        ).order_by(SupportTicket.created_at.desc()).offset(offset).limit(limit).all()