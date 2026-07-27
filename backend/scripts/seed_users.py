"""
Seed users into the database with bcrypt hashed passwords.
Run: python scripts/seed_users.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import User
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def seed_users():
    db = SessionLocal()
    
    try:
        db.query(User).delete()
        db.commit()
        
        users = [
            {
                "email": os.getenv("DEMO_AGENT_EMAIL", "agent@company.com"),
                "password": hash_password(os.getenv("DEMO_AGENT_PASSWORD", "agent123")),
                "name": os.getenv("DEMO_AGENT_NAME", "Sarah Johnson"),
                "role": "agent"
            },
            {
                "email": os.getenv("DEMO_MANAGER_EMAIL", "manager@company.com"),
                "password": hash_password(os.getenv("DEMO_MANAGER_PASSWORD", "manager123")),
                "name": os.getenv("DEMO_MANAGER_NAME", "John Manager"),
                "role": "manager"
            },
            {
                "email": os.getenv("DEMO_ADMIN_EMAIL", "admin@company.com"),
                "password": hash_password(os.getenv("DEMO_ADMIN_PASSWORD", "admin123")),
                "name": os.getenv("DEMO_ADMIN_NAME", "Admin User"),
                "role": "admin"
            }
        ]
        
        for user_data in users:
            user = User(**user_data)
            db.add(user)
            print(f"Added user: {user_data['email']} ({user_data['role']})")
        
        db.commit()
        print("Users seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()