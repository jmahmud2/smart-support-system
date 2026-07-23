from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String, nullable=True)
    
    # Foreign Keys
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    support_tickets = relationship("SupportTicket", back_populates="product")


class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_message = Column(Text, nullable=False)
    
    # AI Analysis Results
    intent = Column(String)
    sentiment = Column(String)
    sentiment_explanation = Column(Text, nullable=True)
    priority = Column(String)
    priority_reasoning = Column(Text, nullable=True)
    response = Column(Text)
    escalate = Column(Boolean, default=False)
    escalate_reasoning = Column(Text, nullable=True)
    reasoning = Column(Text)
    
    # Foreign Keys
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    # Agent Assignment
    assigned_to = Column(String, nullable=True)
    assigned_agent = Column(String, nullable=True)
    
    # Summary
    ticket_summary = Column(Text, nullable=True)
    
    # Metadata
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="support_tickets")