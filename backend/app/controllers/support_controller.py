"""
Support controller for handling business logic related to support tickets.
Coordinates between the database, workflow, and API routes.
"""

from sqlalchemy.orm import Session
from typing import Optional, List

from ..database.models import SupportTicket, Product
from ..schemas.support import SupportTicketCreate
from ..workflow.workflow import process_message


class SupportController:
    """Handles support ticket operations including AI analysis."""

    @staticmethod
    def analyze_message(message: str, product_id: Optional[int] = None) -> dict:
        """
        Process a customer message through the AI workflow.

        Args:
            message: Customer's message
            product_id: Optional product reference

        Returns:
            Dictionary with workflow results
        """
        result = process_message(message)

        # Add product_id if provided
        if product_id:
            result['product_id'] = product_id

        return result

    @staticmethod
    def create_ticket(db: Session, ticket_data: SupportTicketCreate) -> SupportTicket:
        """
        Create a new support ticket and run it through the AI workflow.

        Args:
            db: Database session
            ticket_data: Ticket data including customer message

        Returns:
            Created SupportTicket with AI analysis
        """
        # Run message through workflow
        workflow_result = process_message(ticket_data.customer_message)

        # Create ticket with workflow results
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
        """
        Get a list of support tickets with optional filters.

        Args:
            db: Database session
            status: Filter by ticket status
            intent: Filter by intent
            limit: Number of results per page
            offset: Pagination offset

        Returns:
            List of support tickets
        """
        query = db.query(SupportTicket)

        if status:
            query = query.filter(SupportTicket.status == status)

        if intent:
            query = query.filter(SupportTicket.intent == intent)

        return query.order_by(SupportTicket.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def update_status(db: Session, ticket_id: int, status: str) -> Optional[SupportTicket]:
        """
        Update a ticket's status.

        Args:
            db: Database session
            ticket_id: Ticket ID
            status: New status (new, in_progress, resolved, closed)

        Returns:
            Updated ticket or None if not found
        """
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

        if not ticket:
            return None

        ticket.status = status

        if status in ['resolved', 'closed']:
            from datetime import datetime
            ticket.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(ticket)

        return ticket

    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        Get support ticket statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with ticket statistics
        """
        from sqlalchemy import func

        total_tickets = db.query(func.count(SupportTicket.id)).scalar()

        # Status breakdown
        status_breakdown = db.query(
            SupportTicket.status,
            func.count(SupportTicket.id)
        ).group_by(SupportTicket.status).all()

        # Intent breakdown
        intent_breakdown = db.query(
            SupportTicket.intent,
            func.count(SupportTicket.id)
        ).group_by(SupportTicket.intent).all()

        # Escalation stats
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