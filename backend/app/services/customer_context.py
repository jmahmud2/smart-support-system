"""
Customer context service for gathering order history, ticket history, and customer info.
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from ..database.models import SupportTicket, Product, CustomerOrder, CustomerTicketsSummary


class CustomerContextService:
    """Service for gathering customer context for AI assistance."""

    @staticmethod
    def get_customer_info(db: Session, email: str) -> dict:
        """Get customer information from all sources."""
        if not email:
            return {}

        # Get order history
        orders = db.query(CustomerOrder).filter(
            CustomerOrder.customer_email == email
        ).order_by(CustomerOrder.order_date.desc()).all()

        # Get ticket history
        tickets = db.query(SupportTicket).filter(
            SupportTicket.customer_email == email
        ).order_by(SupportTicket.created_at.desc()).all()

        # Get summary
        summary = db.query(CustomerTicketsSummary).filter(
            CustomerTicketsSummary.customer_email == email
        ).first()

        return {
            "email": email,
            "orders": [
                {
                    "product_name": order.product_name,
                    "product_id": order.product_id,
                    "order_date": order.order_date.isoformat() if order.order_date else None,
                    "status": order.status
                }
                for order in orders
            ],
            "tickets": [
                {
                    "id": ticket.id,
                    "message": ticket.customer_message[:100] if ticket.customer_message else "",
                    "intent": ticket.intent,
                    "sentiment": ticket.sentiment,
                    "status": ticket.status,
                    "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                    "summary": ticket.ticket_summary
                }
                for ticket in tickets
            ],
            "summary": {
                "total_tickets": summary.total_tickets if summary else 0,
                "resolved_tickets": summary.resolved_tickets if summary else 0,
                "open_tickets": summary.open_tickets if summary else 0,
                "escalated_tickets": summary.escalated_tickets if summary else 0,
                "sentiment_score": summary.sentiment_score if summary else 0
            } if summary else {}
        }

    @staticmethod
    def get_order_history(db: Session, email: str) -> List[dict]:
        """Get customer order history."""
        orders = db.query(CustomerOrder).filter(
            CustomerOrder.customer_email == email
        ).order_by(CustomerOrder.order_date.desc()).all()

        return [
            {
                "product_name": order.product_name,
                "product_id": order.product_id,
                "order_date": order.order_date.isoformat() if order.order_date else None,
                "status": order.status
            }
            for order in orders
        ]

    @staticmethod
    def get_ticket_history(db: Session, email: str, limit: int = 10) -> List[dict]:
        """Get customer ticket history."""
        tickets = db.query(SupportTicket).filter(
            SupportTicket.customer_email == email
        ).order_by(SupportTicket.created_at.desc()).limit(limit).all()

        return [
            {
                "id": ticket.id,
                "message": ticket.customer_message[:100] if ticket.customer_message else "",
                "intent": ticket.intent,
                "sentiment": ticket.sentiment,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "summary": ticket.ticket_summary,
                "escalate": ticket.escalate
            }
            for ticket in tickets
        ]

    @staticmethod
    def update_customer_summary(db: Session, email: str):
        """Update or create customer ticket summary."""
        if not email:
            return

        tickets = db.query(SupportTicket).filter(
            SupportTicket.customer_email == email
        ).all()

        if not tickets:
            return

        total = len(tickets)
        resolved = sum(1 for t in tickets if t.status in ["resolved", "closed"])
        open_count = sum(1 for t in tickets if t.status == "new")
        escalated = sum(1 for t in tickets if t.escalate)

        # Calculate average sentiment (0 = neutral, 1 = positive, -1 = negative)
        sentiment_map = {"positive": 1, "neutral": 0, "negative": -1}
        sentiment_sum = sum(sentiment_map.get(t.sentiment, 0) for t in tickets if t.sentiment)
        sentiment_avg = sentiment_sum / total if total > 0 else 0

        summary = db.query(CustomerTicketsSummary).filter(
            CustomerTicketsSummary.customer_email == email
        ).first()

        if summary:
            summary.total_tickets = total
            summary.resolved_tickets = resolved
            summary.open_tickets = open_count
            summary.escalated_tickets = escalated
            summary.last_ticket_date = tickets[0].created_at if tickets else None
            summary.sentiment_score = sentiment_avg
        else:
            summary = CustomerTicketsSummary(
                customer_email=email,
                total_tickets=total,
                resolved_tickets=resolved,
                open_tickets=open_count,
                escalated_tickets=escalated,
                last_ticket_date=tickets[0].created_at if tickets else None,
                sentiment_score=sentiment_avg
            )
            db.add(summary)

        db.commit()

    @staticmethod
    def seed_sample_orders(db: Session):
        """Seed sample order data for existing customers."""
        # Get all customers with tickets
        customers = db.query(SupportTicket.customer_email).distinct().all()
        
        products = db.query(Product).all()
        if not products:
            print(" No products found. Please seed products first.")
            return

        import random

        added_count = 0
        for customer in customers:
            email = customer[0]
            if not email:
                continue

            # Check if customer already has orders
            existing = db.query(CustomerOrder).filter(
                CustomerOrder.customer_email == email
            ).first()
            if existing:
                continue

            # Create 1-3 random orders
            num_orders = random.randint(1, 3)
            for _ in range(num_orders):
                product = random.choice(products)
                order = CustomerOrder(
                    customer_email=email,
                    product_id=product.id,
                    product_name=product.name,
                    order_date=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                    status=random.choice(["completed", "shipped", "pending"])
                )
                db.add(order)
                added_count += 1

        db.commit()
        print(f" Seeded {added_count} sample orders for customers")