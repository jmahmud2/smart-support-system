import sys
import os
from datetime import datetime
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import init_db, SessionLocal
from app.database.models import Category, Product, SupportTicket

def seed_database():
    """Seed the database with initial data"""
    print("🌱 Seeding database...")
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(SupportTicket).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.commit()
        
        # Insert categories
        categories = [
            {"name": "Electronics", "description": "Smartphones, laptops, headphones, and smart home devices."},
            {"name": "Clothing", "description": "Premium apparel for men and women. Sustainable fabrics."},
            {"name": "Home & Kitchen", "description": "Home essentials, cookware, and decor items."},
            {"name": "Books", "description": "Fiction, non-fiction, and educational books."},
            {"name": "Sports & Outdoors", "description": "Sports equipment, camping gear, and outdoor accessories."},
            {"name": "Beauty & Personal Care", "description": "Cruelty-free skincare, haircare, and wellness products."},
            {"name": "Toys & Games", "description": "Educational and entertaining toys for children."},
            {"name": "Automotive", "description": "Automotive accessories, tools, and maintenance products."},
            {"name": "Garden & Outdoor", "description": "Garden tools, patio furniture, and outdoor decor."},
            {"name": "Health & Wellness", "description": "Vitamins, supplements, and wellness products."}
        ]
        
        print("📂 Adding categories...")
        category_objects = []
        for cat_data in categories:
            category = Category(**cat_data)
            db.add(category)
            db.flush()
            category_objects.append(category)
        
        # Insert sample products
        print("📦 Adding sample products...")
        products = [
            {"name": "iPhone 15 Pro Max", "description": "6.7-inch display, A17 Pro chip, 48MP camera", "price": 1199.00, "stock": 45, "category_id": category_objects[0].id},
            {"name": "Sony WH-1000XM5 Headphones", "description": "Industry-leading noise cancellation, 30-hour battery", "price": 399.99, "stock": 120, "category_id": category_objects[0].id},
            {"name": "MacBook Pro 16-inch", "description": "M3 Pro chip, Liquid Retina XDR display", "price": 2499.00, "stock": 30, "category_id": category_objects[0].id},
            {"name": "Premium Cashmere Sweater", "description": "100% grade-A cashmere, made in Italy", "price": 225.00, "stock": 65, "category_id": category_objects[1].id},
            {"name": "Levi's 501 Original Jeans", "description": "Classic straight-fit jeans, sustainable cotton", "price": 89.50, "stock": 200, "category_id": category_objects[1].id},
            {"name": "Le Creuset Dutch Oven", "description": "Cast iron with enamel finish, 5.5qt", "price": 399.95, "stock": 35, "category_id": category_objects[2].id},
            {"name": "KitchenAid Stand Mixer", "description": "5-quart bowl, 10-speed control", "price": 449.99, "stock": 55, "category_id": category_objects[2].id},
            {"name": "Atomic Habits by James Clear", "description": "#1 New York Times bestseller on habits", "price": 27.00, "stock": 500, "category_id": category_objects[3].id},
            {"name": "Yeti Tundra 45 Cooler", "description": "Rotomolded construction, keeps ice for days", "price": 250.00, "stock": 45, "category_id": category_objects[4].id},
            {"name": "Drunk Elephant Night Serum", "description": "10% AHAs and BHAs, resurfacing treatment", "price": 90.00, "stock": 80, "category_id": category_objects[5].id},
        ]
        
        for product_data in products:
            product = Product(**product_data)
            db.add(product)
        
        # Insert sample support tickets
        print("🎫 Adding sample support tickets...")
        tickets = [
            {
                "customer_name": "Sarah Johnson",
                "customer_email": "sarah@email.com",
                "customer_message": "I ordered a MacBook Pro and it arrived with a scratched screen. I need a replacement immediately!",
                "intent": "complaint",
                "sentiment": "negative",
                "priority": "urgent",
                "response": "We apologize for the damaged product. We will process a replacement right away.",
                "escalate": True,
                "reasoning": "Damaged product with urgent tone"
            },
            {
                "customer_name": "Michael Chen",
                "customer_email": "michael@email.com",
                "customer_message": "When will my iPhone be delivered? It's been 3 days without shipping updates.",
                "intent": "shipping",
                "sentiment": "neutral",
                "priority": "medium",
                "response": "Your order is being processed. You should receive tracking within 24 hours.",
                "escalate": False,
                "reasoning": "Standard shipping inquiry"
            },
            {
                "customer_name": "Emily Rodriguez",
                "customer_email": "emily@email.com",
                "customer_message": "I love the Le Creuset Dutch oven! It makes the best stews. Do you offer gift wrapping?",
                "intent": "product_inquiry",
                "sentiment": "positive",
                "priority": "low",
                "response": "We do offer gift wrapping! You can select this option at checkout.",
                "escalate": False,
                "reasoning": "Positive product inquiry"
            }
        ]
        
        for ticket_data in tickets:
            ticket = SupportTicket(**ticket_data)
            db.add(ticket)
        
        db.commit()
        print(f"✅ Database seeded successfully!")
        print(f"   - {len(categories)} categories")
        print(f"   - {len(products)} products")
        print(f"   - {len(tickets)} support tickets")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()