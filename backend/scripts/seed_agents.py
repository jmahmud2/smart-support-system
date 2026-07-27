"""
Seed agents into the database.
Run: python scripts/seed_agents.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import Agent

def seed_agents():
    db = SessionLocal()
    
    try:
        # Clear existing agents
        db.query(Agent).delete()
        db.commit()
        
        agents = [
            {"name": "Sarah Johnson", "email": "sarah@company.com", "specialty": "Technical, Product Issues"},
            {"name": "Michael Chen", "email": "michael@company.com", "specialty": "Billing, Refunds, Payments"},
            {"name": "Emily Rodriguez", "email": "emily@company.com", "specialty": "Shipping, Logistics, Returns"},
            {"name": "David Kim", "email": "david@company.com", "specialty": "General Support, Account Issues"},
            {"name": "Jessica Williams", "email": "jessica@company.com", "specialty": "Product Inquiries, Sales"}
        ]
        
        for agent_data in agents:
            agent = Agent(**agent_data)
            db.add(agent)
            print(f"Added agent: {agent_data['name']} ({agent_data['email']})")
        
        db.commit()
        print("Agents seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding agents: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_agents()