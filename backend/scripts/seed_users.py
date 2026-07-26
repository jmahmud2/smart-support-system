"""
Seed users into the database.
Run: python scripts/seed_users.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import User
import hashlib

def hash_password(password: str) -> str:
    """Simple password hashing (in production, use bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_users():
    db = SessionLocal()
    
    try:
        # Clear existing users
        db.query(User).delete()
        db.commit()
        
        users = [
            {
                "email": "agent@company.com",
                "password": hash_password("agent123"),
                "name": "Sarah Johnson",
                "role": "agent"
            },
            {
                "email": "manager@company.com",
                "password": hash_password("manager123"),
                "name": "John Manager",
                "role": "manager"
            },
            {
                "email": "admin@company.com",
                "password": hash_password("admin123"),
                "name": "Admin User",
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