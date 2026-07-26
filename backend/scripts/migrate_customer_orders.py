"""
Migrate customer_orders table to add missing columns.
Run: python scripts/migrate_customer_orders.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import engine
from sqlalchemy import text

def migrate_customer_orders():
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("PRAGMA table_info(customer_orders)"))
        columns = [row[1] for row in result]
        print(f"Existing columns in customer_orders: {columns}")
        
        # Add status column if it doesn't exist
        if 'status' not in columns:
            conn.execute(text("ALTER TABLE customer_orders ADD COLUMN status VARCHAR DEFAULT 'completed'"))
            print("✅ Added column: status to customer_orders")
        else:
            print("ℹ️ Column 'status' already exists in customer_orders")
        
        # Check if other columns are missing
        expected_columns = ['id', 'customer_email', 'product_id', 'product_name', 'order_date', 'status']
        for col in expected_columns:
            if col not in columns:
                if col == 'order_date':
                    conn.execute(text("ALTER TABLE customer_orders ADD COLUMN order_date DATETIME"))
                    print(f"✅ Added column: {col}")
                elif col == 'customer_email':
                    conn.execute(text("ALTER TABLE customer_orders ADD COLUMN customer_email VARCHAR"))
                    print(f"✅ Added column: {col}")
                elif col == 'product_id':
                    conn.execute(text("ALTER TABLE customer_orders ADD COLUMN product_id INTEGER"))
                    print(f"✅ Added column: {col}")
                elif col == 'product_name':
                    conn.execute(text("ALTER TABLE customer_orders ADD COLUMN product_name VARCHAR"))
                    print(f"✅ Added column: {col}")
        
        conn.commit()
        print("✅ Migration complete!")

if __name__ == "__main__":
    migrate_customer_orders()