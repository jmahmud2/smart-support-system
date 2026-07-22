import sys
import os
import csv
from datetime import datetime
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import init_db, SessionLocal
from app.database.models import Category, Product, SupportTicket

def clean_price(price_str):
    """Clean price string to float"""
    try:
        if isinstance(price_str, str):
            # Remove ₹, commas, and convert
            cleaned = price_str.replace('₹', '').replace(',', '').strip()
            return float(cleaned)
        return float(price_str)
    except:
        return 0.0

def map_category(cat_name):
    """Map product category to our category names"""
    cat_name_lower = cat_name.lower() if cat_name else ''
    
    if any(word in cat_name_lower for word in ['electronics', 'mobile', 'phone', 'laptop', 'computer', 'headphone', 'camera', 'tv']):
        return 'Electronics'
    elif any(word in cat_name_lower for word in ['clothing', 'apparel', 'fashion', 'shirt', 'jeans', 'dress', 'shoe', 'wear']):
        return 'Clothing'
    elif any(word in cat_name_lower for word in ['home', 'kitchen', 'furniture', 'cookware', 'bed', 'sofa', 'decor']):
        return 'Home & Kitchen'
    elif any(word in cat_name_lower for word in ['book', 'novel', 'fiction', 'nonfiction', 'literature']):
        return 'Books'
    elif any(word in cat_name_lower for word in ['sports', 'outdoor', 'fitness', 'camping', 'bike', 'gym']):
        return 'Sports & Outdoors'
    elif any(word in cat_name_lower for word in ['beauty', 'skin', 'hair', 'makeup', 'cosmetic', 'personal care']):
        return 'Beauty & Personal Care'
    elif any(word in cat_name_lower for word in ['toy', 'game', 'play', 'kid', 'child', 'board game']):
        return 'Toys & Games'
    elif any(word in cat_name_lower for word in ['automotive', 'car', 'auto', 'vehicle']):
        return 'Automotive'
    elif any(word in cat_name_lower for word in ['garden', 'outdoor', 'patio', 'lawn', 'plant']):
        return 'Garden & Outdoor'
    elif any(word in cat_name_lower for word in ['health', 'wellness', 'vitamin', 'supplement', 'fitness']):
        return 'Health & Wellness'
    else:
        return random.choice(['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Sports & Outdoors'])

def seed_real_data():
    print("🌱 Seeding database with real data...")
    
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(SupportTicket).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.commit()
        
        # Categories
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
        category_map = {}
        for cat_data in categories:
            category = Category(**cat_data)
            db.add(category)
            db.flush()
            category_map[cat_data["name"]] = category.id
        
        # Load Products from amazon.csv
        product_count = 0
        products_file = "scripts/data/amazon.csv"
        
        if os.path.exists(products_file):
            print(f"📦 Loading products from {products_file}...")
            with open(products_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Map columns from Amazon dataset
                    name = row.get('product_name', 'Unknown Product')
                    description = row.get('about_product', '')
                    price_str = row.get('discounted_price') or row.get('actual_price', '0')
                    price = clean_price(price_str)
                    stock = random.randint(1, 100)  # Not in dataset
                    category_name = row.get('category', '')
                    
                    # Map category
                    mapped_category = map_category(category_name)
                    category_id = category_map.get(mapped_category, random.choice(list(category_map.values())))
                    
                    # Image URL
                    image_url = row.get('img_link', '')
                    
                    product = Product(
                        name=name[:200],
                        description=description[:500] if description else None,
                        price=price if price > 0 else random.uniform(10, 500),
                        stock=stock,
                        category_id=category_id,
                        image_url=image_url if image_url else None
                    )
                    db.add(product)
                    product_count += 1
                    
                    if product_count % 100 == 0:
                        db.flush()
                        print(f"   Processed {product_count} products...")
            
            db.flush()
            print(f"   ✅ Loaded {product_count} products")
        else:
            print(f"⚠️ Products file not found: {products_file}")
        
        # Load Support Tickets
        ticket_count = 0
        tickets_file = "scripts/data/customer_support_tickets.csv"
        
        if os.path.exists(tickets_file):
            print(f"🎫 Loading support tickets from {tickets_file}...")
            
            # Get product IDs for linking
            product_ids = [p.id for p in db.query(Product).limit(100).all()]
            
            with open(tickets_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Map columns from support dataset
                    customer_name = row.get('Customer Name', 'Anonymous')
                    customer_email = row.get('Customer Email', '')
                    customer_message = row.get('Ticket Description', 'No description')
                    
                    # Intent from Ticket Type
                    ticket_type = row.get('Ticket Type', 'general')
                    ticket_type_lower = ticket_type.lower()
                    if 'technical' in ticket_type_lower or 'product' in ticket_type_lower:
                        intent = 'product_inquiry'
                    elif 'billing' in ticket_type_lower or 'refund' in ticket_type_lower:
                        intent = 'refund'
                    elif 'shipping' in ticket_type_lower or 'delivery' in ticket_type_lower:
                        intent = 'shipping'
                    elif 'complaint' in ticket_type_lower:
                        intent = 'complaint'
                    else:
                        intent = 'general'
                    
                    # Priority
                    priority_raw = row.get('Ticket Priority', 'medium')
                    if priority_raw.lower() in ['urgent', 'critical', 'high']:
                        priority = 'urgent'
                    elif priority_raw.lower() == 'medium':
                        priority = 'medium'
                    else:
                        priority = 'low'
                    
                    # Sentiment from satisfaction rating
                    rating = row.get('Customer Satisfaction Rating', '3')
                    try:
                        rating_val = float(rating)
                        if rating_val >= 4:
                            sentiment = 'positive'
                        elif rating_val >= 2.5:
                            sentiment = 'neutral'
                        else:
                            sentiment = 'negative'
                    except:
                        sentiment = 'neutral'
                    
                    # Escalate based on priority and sentiment
                    escalate = (priority == 'urgent' or sentiment == 'negative')
                    
                    # Link to product (if we have any)
                    product_id = random.choice(product_ids) if product_ids and random.random() > 0.5 else None
                    
                    # Status
                    status = row.get('Ticket Status', 'new').lower()
                    if status not in ['new', 'in_progress', 'resolved', 'closed']:
                        status = 'new'
                    
                    # Resolution date
                    resolved_at = None
                    if status in ['resolved', 'closed']:
                        resolved_at = datetime.now()
                    
                    ticket = SupportTicket(
                        customer_name=customer_name[:50],
                        customer_email=customer_email[:100] if customer_email else None,
                        customer_message=customer_message[:1000],
                        intent=intent,
                        sentiment=sentiment,
                        priority=priority,
                        response=f"Thank you for your {intent} inquiry. Our support team will review and respond shortly.",
                        escalate=escalate,
                        reasoning=f"Priority: {priority}, Sentiment: {sentiment}",
                        product_id=product_id,
                        status=status,
                        resolved_at=resolved_at
                    )
                    db.add(ticket)
                    ticket_count += 1
                    
                    if ticket_count % 50 == 0:
                        db.flush()
                        print(f"   Processed {ticket_count} tickets...")
            
            db.flush()
            print(f"   ✅ Loaded {ticket_count} tickets")
        else:
            print(f"⚠️ Tickets file not found: {tickets_file}")
        
        db.commit()
        
        final_product_count = db.query(Product).count()
        final_ticket_count = db.query(SupportTicket).count()
        
        print("\n✅ Database seeded successfully!")
        print(f"   - {len(categories)} categories")
        print(f"   - {final_product_count} products")
        print(f"   - {final_ticket_count} support tickets")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_data()