"""
Clean up placeholder text in support tickets.
Replaces {product_purchased} with actual product names
and removes HTML-like tags.
"""

import sys
import os
import re
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import SupportTicket, Product


def clean_ticket_messages():
    """Clean all ticket messages by replacing placeholders with actual data."""
    
    db = SessionLocal()
    
    try:
        print("🔍 Scanning for tickets with placeholders...")
        
        # Get all tickets with {product_purchased} placeholder
        tickets = db.query(SupportTicket).filter(
            SupportTicket.customer_message.contains("{product_purchased}")
        ).all()
        
        print(f"Found {len(tickets)} tickets with placeholders")
        
        if len(tickets) == 0:
            print("✅ No tickets need cleaning!")
            return
        
        # Get all products for random selection
        products = db.query(Product).all()
        product_names = [p.name for p in products if p.name]
        
        if not product_names:
            print("⚠️ No products found in database. Using generic names.")
            product_names = ["Product", "Device", "Item", "Gadget", "Accessory"]
        
        updated_count = 0
        
        for ticket in tickets:
            original_message = ticket.customer_message
            
            # Replace {product_purchased} with a random product name
            if '{product_purchased}' in original_message:
                random_product = random.choice(product_names)
                original_message = original_message.replace(
                    '{product_purchased}', 
                    random_product
                )
            
            # Remove HTML-like tags like </product_purchased> </div> etc.
            original_message = re.sub(r'</?[a-z_]+>', '', original_message)
            
            # Clean up extra spaces
            original_message = re.sub(r'\s+', ' ', original_message).strip()
            
            # Remove multiple newlines
            original_message = re.sub(r'\n{3,}', '\n\n', original_message)
            
            # Update the ticket
            if original_message != ticket.customer_message:
                ticket.customer_message = original_message
                updated_count += 1
                
                # Print progress every 100 tickets
                if updated_count % 100 == 0:
                    print(f"   Processed {updated_count} tickets...")
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Updated {updated_count} tickets successfully!")
        
        # Show a sample of cleaned tickets
        sample_tickets = db.query(SupportTicket).filter(
            SupportTicket.id.in_([t.id for t in tickets[:5]])
        ).all()
        
        print("\n📝 Sample cleaned messages:")
        print("-" * 60)
        for ticket in sample_tickets:
            print(f"Ticket #{ticket.id}:")
            print(f"  {ticket.customer_message[:100]}...")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error cleaning tickets: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def clean_single_ticket(ticket_id):
    """Clean a single ticket by ID (for testing)."""
    
    db = SessionLocal()
    
    try:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            print(f"❌ Ticket #{ticket_id} not found")
            return
        
        original = ticket.customer_message
        print(f"Original: {original}")
        
        # Clean it
        cleaned = original
        cleaned = cleaned.replace('{product_purchased}', 'Product')
        cleaned = re.sub(r'</?[a-z_]+>', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        print(f"Cleaned: {cleaned}")
        
        confirm = input("Apply this change? (y/n): ")
        if confirm.lower() == 'y':
            ticket.customer_message = cleaned
            db.commit()
            print("✅ Updated!")
        else:
            print("❌ Skipped")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode - clean a single ticket
        ticket_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        clean_single_ticket(ticket_id)
    else:
        # Full cleanup
        clean_ticket_messages()