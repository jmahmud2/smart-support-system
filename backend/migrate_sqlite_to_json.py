# save as migrate_to_neon.py
import os
import json
from sqlalchemy import create_engine, text
from app.database.database import SessionLocal, Base
from app.database.models import (
    Category, Product, SupportTicket, User, 
    CustomerOrder, CustomerTicketsSummary, Agent, KnowledgeBase
)
from datetime import datetime

def import_data():
    # Load exported data
    with open('data_export.json', 'r') as f:
        data = json.load(f)
    
    db = SessionLocal()
    
    try:
        # Clear existing data (optional)
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(text(f'DELETE FROM {table.name}'))
        db.commit()
        print("✅ Cleared existing data")
        
        # Import Categories
        for row in data.get('categories', []):
            cat = Category(**row)
            db.add(cat)
        db.commit()
        print(f"✅ Imported {len(data.get('categories', []))} categories")
        
        # Import Products
        for row in data.get('products', []):
            prod = Product(**row)
            db.add(prod)
        db.commit()
        print(f"✅ Imported {len(data.get('products', []))} products")
        
        # Import Users
        for row in data.get('users', []):
            user = User(**row)
            db.add(user)
        db.commit()
        print(f"✅ Imported {len(data.get('users', []))} users")
        
        # Import Agents
        for row in data.get('agents', []):
            agent = Agent(**row)
            db.add(agent)
        db.commit()
        print(f"✅ Imported {len(data.get('agents', []))} agents")
        
        # Import Support Tickets
        for row in data.get('support_tickets', []):
            # Convert string dates to datetime objects
            for field in ['created_at', 'resolved_at', 'sla_response_deadline', 'sla_resolution_deadline', 'first_response_time']:
                if row.get(field) and isinstance(row[field], str):
                    row[field] = datetime.fromisoformat(row[field].replace('Z', '+00:00'))
            ticket = SupportTicket(**row)
            db.add(ticket)
        db.commit()
        print(f"✅ Imported {len(data.get('support_tickets', []))} tickets")
        
        # Import Customer Orders
        for row in data.get('customer_orders', []):
            if row.get('order_date') and isinstance(row['order_date'], str):
                row['order_date'] = datetime.fromisoformat(row['order_date'].replace('Z', '+00:00'))
            order = CustomerOrder(**row)
            db.add(order)
        db.commit()
        print(f"✅ Imported {len(data.get('customer_orders', []))} orders")
        
        # Import Knowledge Base
        for row in data.get('knowledge_base', []):
            for field in ['created_at', 'updated_at']:
                if row.get(field) and isinstance(row[field], str):
                    row[field] = datetime.fromisoformat(row[field].replace('Z', '+00:00'))
            kb = KnowledgeBase(**row)
            db.add(kb)
        db.commit()
        print(f"✅ Imported {len(data.get('knowledge_base', []))} KB articles")
        
        print("\n✅ Migration complete!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import_data()