"""
Add SLA columns to support_tickets table.
Run: python scripts/migrate_sla.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import engine
from sqlalchemy import text

def migrate_sla():
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("PRAGMA table_info(support_tickets)"))
        columns = [row[1] for row in result]
        print(f"Existing columns in support_tickets: {columns}")
        
        # Add SLA columns
        sla_columns = [
            ("sla_response_deadline", "DATETIME"),
            ("sla_resolution_deadline", "DATETIME"),
            ("sla_status", "VARCHAR DEFAULT 'on_track'"),
            ("first_response_time", "DATETIME")
        ]
        
        for col_name, col_type in sla_columns:
            if col_name not in columns:
                conn.execute(text(f"ALTER TABLE support_tickets ADD COLUMN {col_name} {col_type}"))
                print(f"Added column: {col_name}")
            else:
                print(f"Column already exists: {col_name}")
        
        conn.commit()
        print("Migration complete!")

if __name__ == "__main__":
    migrate_sla()