from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.models import Product as ProductModel
from ..database.models import Category as CategoryModel
from ..database.models import SupportTicket as SupportTicketModel

class StatsController:
    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get aggregate stats"""
        
        # Product stats
        total_products = db.query(func.count(ProductModel.id)).scalar()
        total_revenue = db.query(func.sum(ProductModel.price * ProductModel.stock)).scalar() or 0
        avg_price = db.query(func.avg(ProductModel.price)).scalar() or 0
        
        # Category with most products
        top_category = db.query(
            ProductModel.category_id,
            func.count(ProductModel.id).label('count')
        ).group_by(ProductModel.category_id).order_by(
            func.count(ProductModel.id).desc()
        ).first()
        
        top_category_name = None
        if top_category:
            category = db.query(CategoryModel).filter(
                CategoryModel.id == top_category[0]
            ).first()
            if category:
                top_category_name = category.name
        
        # Ticket stats
        total_tickets = db.query(func.count(SupportTicketModel.id)).scalar()
        open_tickets = db.query(func.count(SupportTicketModel.id)).filter(
            SupportTicketModel.status == "new"
        ).scalar()
        
        # Intent breakdown
        intents = db.query(
            SupportTicketModel.intent,
            func.count(SupportTicketModel.id)
        ).group_by(SupportTicketModel.intent).all()
        intent_breakdown = {intent: count for intent, count in intents if intent}
        
        return {
            "total_products": total_products,
            "total_revenue": round(total_revenue, 2),
            "average_price": round(avg_price, 2),
            "top_category": top_category_name,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "intent_breakdown": intent_breakdown
        }