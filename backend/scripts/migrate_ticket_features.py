"""
Database migration script for ticket-centric AI features.
Run: python scripts/migrate_ticket_features.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import engine
from sqlalchemy import text

def run_migration():
    """Add new columns for ticket-centric features."""
    
    print("🔧 Running migration for ticket-centric features...")
    
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("PRAGMA table_info(support_tickets)"))
        existing_columns = [row[1] for row in result]
        print(f"📋 Existing columns: {existing_columns}")
        
        # New columns to add
        new_columns = [
            ("customer_id", "VARCHAR"),  # For linking to customer table
            ("order_history", "TEXT"),    # JSON field for order history
            ("agent_notes", "TEXT"),      # Internal notes for agents
            ("ai_draft", "TEXT"),         # Latest AI-generated draft
        ]
        
        added = []
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                conn.execute(text(f"ALTER TABLE support_tickets ADD COLUMN {col_name} {col_type}"))
                added.append(col_name)
                print(f"✅ Added column: {col_name}")
            else:
                print(f"ℹ️ Column already exists: {col_name}")
        
        # Create customer_orders table for order history
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_email VARCHAR NOT NULL,
                product_id INTEGER,
                product_name VARCHAR,
                order_date DATETIME,
                order_status VARCHAR DEFAULT 'completed',
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """))
        print("✅ Created table: customer_orders")
        
        # Create customer_tickets_summary table for faster lookups
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_tickets_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_email VARCHAR NOT NULL UNIQUE,
                total_tickets INTEGER DEFAULT 0,
                resolved_tickets INTEGER DEFAULT 0,
                open_tickets INTEGER DEFAULT 0,
                escalated_tickets INTEGER DEFAULT 0,
                last_ticket_date DATETIME,
                sentiment_score REAL DEFAULT 0
            )
        """))
        print("✅ Created table: customer_tickets_summary")
        
        conn.commit()
        print(f"✅ Migration complete! Added columns: {', '.join(added) if added else 'None'}")
        print(f"   Created tables: customer_orders, customer_tickets_summary")

if __name__ == "__main__":
    run_migration()