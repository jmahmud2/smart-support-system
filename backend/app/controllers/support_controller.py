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
from ..utils.logger import get_logger, log_error

logger = get_logger(__name__)


class SupportController:
    """Handles support ticket operations including AI analysis."""

    @staticmethod
    def analyze_message(message: str, product_id: Optional[int] = None) -> dict:
        """Process a customer message through the AI workflow."""
        logger.info(f" Analyzing message: {message[:50]}...")
        result = process_message(message)
        if product_id:
            result['product_id'] = product_id
        logger.info(f" Analysis complete: Intent={result.get('intent')}, Sentiment={result.get('sentiment')}")
        return result

    @staticmethod
    def create_ticket(db: Session, ticket_data: SupportTicketCreate) -> SupportTicket:
        """Create a new support ticket and run it through the AI workflow."""
        try:
            logger.info(f" Creating ticket for: {ticket_data.customer_message[:50]}...")
            
            workflow_result = process_message(ticket_data.customer_message)
            logger.info(f" Workflow result: Intent={workflow_result.get('intent')}, Sentiment={workflow_result.get('sentiment')}")

            ticket = SupportTicket(
                customer_name=ticket_data.customer_name,
                customer_email=ticket_data.customer_email,
                customer_message=ticket_data.customer_message,
                product_id=ticket_data.product_id,
                intent=workflow_result.get('intent') or "general",
                sentiment=workflow_result.get('sentiment') or "neutral",
                sentiment_explanation=workflow_result.get('sentiment_explanation') or "",
                priority=workflow_result.get('priority') or "medium",
                priority_reasoning=workflow_result.get('priority_reasoning') or "",
                response=workflow_result.get('response') or "Thank you for reaching out. Our team will review your inquiry.",
                escalate=workflow_result.get('escalate', False),
                escalate_reasoning=workflow_result.get('escalate_reasoning') or "",
                reasoning=workflow_result.get('reasoning') or "",
                assigned_agent=workflow_result.get('assigned_agent') or "",
                ticket_summary=workflow_result.get('ticket_summary') or "",
                status='new'
            )

            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            logger.info(f" Ticket created successfully: #{ticket.id}")
            return ticket
            
        except Exception as e:
            log_error(logger, e, "Creating ticket")
            db.rollback()
            raise

    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Optional[SupportTicket]:
        """Get a support ticket by ID."""
        logger.info(f"🔍 Fetching ticket #{ticket_id}")
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if ticket:
            logger.info(f" Ticket #{ticket_id} found")
        else:
            logger.warning(f" Ticket #{ticket_id} not found")
        return ticket

    @staticmethod
    def get_tickets(
        db: Session,
        status: Optional[str] = None,
        intent: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SupportTicket]:
        """Get a list of support tickets with optional filters."""
        logger.info(f" Fetching tickets: status={status}, intent={intent}, limit={limit}, offset={offset}")
        query = db.query(SupportTicket)

        if status:
            query = query.filter(SupportTicket.status == status)
        if intent:
            query = query.filter(SupportTicket.intent == intent)

        tickets = query.order_by(SupportTicket.created_at.desc()).offset(offset).limit(limit).all()
        logger.info(f" Found {len(tickets)} tickets")
        return tickets

    @staticmethod
    def update_status(db: Session, ticket_id: int, status: str) -> Optional[SupportTicket]:
        """Update a ticket's status."""
        logger.info(f" Updating ticket #{ticket_id} status to: {status}")
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            logger.warning(f"⚠️ Ticket #{ticket_id} not found")
            return None

        ticket.status = status
        if status in ['resolved', 'closed']:
            ticket.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(ticket)
        logger.info(f" Ticket #{ticket_id} status updated to: {status}")
        return ticket

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get support ticket statistics."""
        from sqlalchemy import func
        logger.info(" Fetching support statistics")

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

        result = {
            "total_tickets": total_tickets or 0,
            "status_breakdown": {status: count for status, count in status_breakdown if status},
            "intent_breakdown": {intent: count for intent, count in intent_breakdown if intent},
            "escalated_count": escalated_count or 0,
            "escalation_rate": round((escalated_count / total_tickets * 100) if total_tickets > 0 else 0, 2)
        }
        logger.info(f" Stats fetched: {result['total_tickets']} total tickets")
        return result

    @staticmethod
    def auto_reply_to_ticket(db: Session, ticket_id: int) -> dict:
        """Send an AI-generated auto-reply to a customer."""
        logger.info(f" Auto-reply to ticket #{ticket_id}")
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            logger.warning(f" Ticket #{ticket_id} not found")
            return {"success": False, "error": "Ticket not found"}

        if ticket.response and "Thank you for your" not in ticket.response[:50]:
            logger.info(f"ℹ Ticket #{ticket_id} already has a response")
            return {"success": False, "error": "Ticket already has a response"}

        result = process_message(ticket.customer_message)

        ticket.response = result.get('response')
        ticket.intent = result.get('intent')
        ticket.sentiment = result.get('sentiment')
        ticket.sentiment_explanation = result.get('sentiment_explanation')
        ticket.priority = result.get('priority')
        ticket.priority_reasoning = result.get('priority_reasoning')
        ticket.escalate = result.get('escalate', False)
        ticket.escalate_reasoning = result.get('escalate_reasoning')
        ticket.reasoning = result.get('reasoning')
        ticket.assigned_agent = result.get('assigned_agent')
        ticket.ticket_summary = result.get('ticket_summary')

        db.commit()
        db.refresh(ticket)

        logger.info(f" Auto-reply sent to ticket #{ticket_id}")
        return {
            "success": True,
            "ticket_id": ticket.id,
            "response": ticket.response,
            "auto_replied": True
        }

    @staticmethod
    def auto_reply_to_all_new_tickets(db: Session) -> dict:
        """Send auto-replies to all 'new' tickets without responses."""
        logger.info(" Auto-replying to all new tickets")
        tickets = db.query(SupportTicket).filter(
            SupportTicket.status == 'new',
            SupportTicket.response.is_(None)
        ).all()

        logger.info(f" Found {len(tickets)} tickets without responses")
        results = []
        for ticket in tickets:
            result = SupportController.auto_reply_to_ticket(db, ticket.id)
            results.append(result)

        success_count = sum(1 for r in results if r.get('success'))
        logger.info(f" Auto-replied to {success_count}/{len(tickets)} tickets")
        return {
            "total_processed": len(results),
            "successful": success_count,
            "failed": len(results) - success_count
        }

    @staticmethod
    def get_sentiment_trends(db: Session, days: int = 7) -> dict:
        """Get sentiment trends over time."""
        from sqlalchemy import func
        logger.info(f" Fetching sentiment trends for last {days} days")

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

        logger.info(f" Sentiment trends fetched: {sentiment_distribution}")
        return {
            'trends': dates,
            'distribution': sentiment_distribution,
            'period': f'Last {days} days'
        }

    @staticmethod
    def get_ai_summary(db: Session, days: int = 7) -> dict:
        """Generate an AI summary of recent tickets."""
        logger.info(f" Generating AI summary for last {days} days")
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        tickets = db.query(SupportTicket).filter(
            SupportTicket.created_at >= start_date
        ).limit(50).all()

        if not tickets:
            logger.info(" No recent tickets found")
            return {"summary": "No recent tickets to summarize."}

        ticket_data = []
        for ticket in tickets:
            ticket_data.append({
                'id': ticket.id,
                'intent': ticket.intent,
                'sentiment': ticket.sentiment,
                'priority': ticket.priority,
                'summary': ticket.ticket_summary or ticket.customer_message[:100] if ticket.customer_message else ''
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

        logger.info(f" AI summary generated ({len(tickets)} tickets)")
        return {
            'period': f'Last {days} days',
            'total_tickets': len(tickets),
            'summary': summary
        }

    @staticmethod
    def assign_ticket(db: Session, ticket_id: int, agent_name: str) -> Optional[SupportTicket]:
        """Assign a ticket to an agent."""
        logger.info(f" Assigning ticket #{ticket_id} to: {agent_name}")
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            logger.warning(f" Ticket #{ticket_id} not found")
            return None

        ticket.assigned_to = agent_name
        db.commit()
        db.refresh(ticket)
        logger.info(f" Ticket #{ticket_id} assigned to: {agent_name}")
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
        logger.info(f" Fetching tickets for agent: {agent_name}")
        query = db.query(SupportTicket).filter(SupportTicket.assigned_to == agent_name)

        if status:
            query = query.filter(SupportTicket.status == status)

        tickets = query.order_by(SupportTicket.created_at.desc()).offset(offset).limit(limit).all()
        logger.info(f" Found {len(tickets)} tickets for {agent_name}")
        return tickets

    @staticmethod
    def get_unassigned_tickets(
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> List[SupportTicket]:
        """Get tickets that haven't been assigned to anyone."""
        logger.info(f" Fetching unassigned tickets")
        tickets = db.query(SupportTicket).filter(
            SupportTicket.assigned_to.is_(None)
        ).order_by(SupportTicket.created_at.desc()).offset(offset).limit(limit).all()
        logger.info(f" Found {len(tickets)} unassigned tickets")
        return tickets