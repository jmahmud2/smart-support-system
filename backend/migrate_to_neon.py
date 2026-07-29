import os
import json
from datetime import datetime
from sqlalchemy import text
from app.database.database import SessionLocal
from app.database.models import (
    Category, Product, SupportTicket, User, 
    CustomerOrder, CustomerTicketsSummary, Agent, KnowledgeBase
)

def parse_datetime(value):
    """Convert ISO string to datetime object, handling various formats."""
    if not value or value == 'None':
        return None
    if isinstance(value, datetime):
        return value
    try:
        # Handle format like '2026-07-22 15:32:58.527497'
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            try:
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None

def import_data():
    with open('data_export.json', 'r') as f:
        data = json.load(f)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        for table in reversed(KnowledgeBase.metadata.sorted_tables):
            try:
                db.execute(text(f'DELETE FROM {table.name}'))
            except Exception as e:
                print(f"⚠️ Could not clear {table.name}: {e}")
        db.commit()
        print("✅ Cleared existing data")
        
        # Import Categories
        for row in data.get('categories', []):
            row['created_at'] = parse_datetime(row.get('created_at'))
            cat = Category(**row)
            db.add(cat)
        db.commit()
        print(f"✅ Imported {len(data.get('categories', []))} categories")
        
        # Import Products
        for row in data.get('products', []):
            row['created_at'] = parse_datetime(row.get('created_at'))
            row['updated_at'] = parse_datetime(row.get('updated_at'))
            prod = Product(**row)
            db.add(prod)
        db.commit()
        print(f"✅ Imported {len(data.get('products', []))} products")
        
        # Import Users
        for row in data.get('users', []):
            row['created_at'] = parse_datetime(row.get('created_at'))
            user = User(**row)
            db.add(user)
        db.commit()
        print(f"✅ Imported {len(data.get('users', []))} users")
        
        # Import Agents
        for row in data.get('agents', []):
            row['created_at'] = parse_datetime(row.get('created_at'))
            agent = Agent(**row)
            db.add(agent)
        db.commit()
        print(f"✅ Imported {len(data.get('agents', []))} agents")
        
        # Import Support Tickets
        for row in data.get('support_tickets', []):
            for field in ['created_at', 'resolved_at', 'sla_response_deadline', 
                          'sla_resolution_deadline', 'first_response_time']:
                row[field] = parse_datetime(row.get(field))
            ticket = SupportTicket(**row)
            db.add(ticket)
        db.commit()
        print(f"✅ Imported {len(data.get('support_tickets', []))} tickets")
        
        # Import Customer Orders
        for row in data.get('customer_orders', []):
            row['order_date'] = parse_datetime(row.get('order_date'))
            order = CustomerOrder(**row)
            db.add(order)
        db.commit()
        print(f"✅ Imported {len(data.get('customer_orders', []))} orders")
        
        # Import Customer Tickets Summary
        for row in data.get('customer_tickets_summary', []):
            row['last_ticket_date'] = parse_datetime(row.get('last_ticket_date'))
            summary = CustomerTicketsSummary(**row)
            db.add(summary)
        db.commit()
        print(f"✅ Imported {len(data.get('customer_tickets_summary', []))} summaries")
        
        # Import Knowledge Base
        for row in data.get('knowledge_base', []):
            row['created_at'] = parse_datetime(row.get('created_at'))
            row['updated_at'] = parse_datetime(row.get('updated_at'))
            kb = KnowledgeBase(**row)
            db.add(kb)
        db.commit()
        print(f"✅ Imported {len(data.get('knowledge_base', []))} KB articles")
        
        print("\n✅ Migration complete!")
        print(f"   Categories: {db.query(Category).count()}")
        print(f"   Products: {db.query(Product).count()}")
        print(f"   Tickets: {db.query(SupportTicket).count()}")
        print(f"   Users: {db.query(User).count()}")
        print(f"   KB Articles: {db.query(KnowledgeBase).count()}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import_data()