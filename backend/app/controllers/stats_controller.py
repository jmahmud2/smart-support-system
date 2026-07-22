"""
Stats controller for handling business logic related to statistics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.models import Product, Category, SupportTicket


class StatsController:
    """Handles statistics operations."""

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get aggregate stats"""
        
        # Product stats
        total_products = db.query(func.count(Product.id)).scalar()
        total_revenue = db.query(func.sum(Product.price * Product.stock)).scalar() or 0
        avg_price = db.query(func.avg(Product.price)).scalar() or 0

        # Category with most products
        top_category = db.query(
            Product.category_id,
            func.count(Product.id).label('count')
        ).group_by(Product.category_id).order_by(
            func.count(Product.id).desc()
        ).first()

        top_category_name = None
        if top_category:
            category = db.query(Category).filter(Category.id == top_category[0]).first()
            if category:
                top_category_name = category.name

        # Ticket stats
        total_tickets = db.query(func.count(SupportTicket.id)).scalar()
        open_tickets = db.query(func.count(SupportTicket.id)).filter(
            SupportTicket.status == "new"
        ).scalar()

        # Intent breakdown
        intents = db.query(
            SupportTicket.intent,
            func.count(SupportTicket.id)
        ).group_by(SupportTicket.intent).all()
        intent_breakdown = {intent: count for intent, count in intents if intent}

        # Sentiment breakdown
        sentiments = db.query(
            SupportTicket.sentiment,
            func.count(SupportTicket.id)
        ).group_by(SupportTicket.sentiment).all()
        sentiment_breakdown = {sentiment: count for sentiment, count in sentiments if sentiment}

        # Escalation stats
        escalated_count = db.query(func.count(SupportTicket.id)).filter(
            SupportTicket.escalate == True
        ).scalar()

        # Status breakdown
        statuses = db.query(
            SupportTicket.status,
            func.count(SupportTicket.id)
        ).group_by(SupportTicket.status).all()
        status_breakdown = {status: count for status, count in statuses if status}

        return {
            "total_products": total_products,
            "total_revenue": round(total_revenue, 2),
            "average_price": round(avg_price, 2),
            "top_category": top_category_name,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "intent_breakdown": intent_breakdown,
            "sentiment_breakdown": sentiment_breakdown,
            "escalated_count": escalated_count,
            "status_breakdown": status_breakdown,
            "escalation_rate": round((escalated_count / total_tickets * 100) if total_tickets > 0 else 0, 2)
        }