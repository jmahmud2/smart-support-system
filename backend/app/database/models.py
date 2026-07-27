from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String, nullable=True)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    category = relationship("Category", back_populates="products")
    support_tickets = relationship("SupportTicket", back_populates="product")
    orders = relationship("CustomerOrder", back_populates="product")


class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_message = Column(Text, nullable=False)
    
    intent = Column(String)
    sentiment = Column(String)
    sentiment_explanation = Column(Text, nullable=True)
    priority = Column(String)
    priority_reasoning = Column(Text, nullable=True)
    response = Column(Text)
    escalate = Column(Boolean, default=False)
    escalate_reasoning = Column(Text, nullable=True)
    reasoning = Column(Text)
    
    customer_id = Column(String, nullable=True)
    order_history = Column(Text, nullable=True)
    agent_notes = Column(Text, nullable=True)
    ai_draft = Column(Text, nullable=True)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    assigned_to = Column(String, nullable=True)
    assigned_agent = Column(String, nullable=True)
    ticket_summary = Column(Text, nullable=True)
    
    status = Column(String, default="new")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
    
    product = relationship("Product", back_populates="support_tickets")


class CustomerOrder(Base):
    __tablename__ = "customer_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String, nullable=True)
    order_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="completed")
    
    product = relationship("Product", back_populates="orders")


class CustomerTicketsSummary(Base):
    __tablename__ = "customer_tickets_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, unique=True, nullable=False)
    total_tickets = Column(Integer, default=0)
    resolved_tickets = Column(Integer, default=0)
    open_tickets = Column(Integer, default=0)
    escalated_tickets = Column(Integer, default=0)
    last_ticket_date = Column(DateTime, nullable=True)
    sentiment_score = Column(Float, default=0)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="agent")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    specialty = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))