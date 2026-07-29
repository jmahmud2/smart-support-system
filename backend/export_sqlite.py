import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row

tables = ['categories', 'products', 'support_tickets', 'users', 'customer_orders', 'customer_tickets_summary', 'agents', 'knowledge_base']

data = {}

for table in tables:
    try:
        rows = conn.execute(f'SELECT * FROM {table}').fetchall()
        data[table] = [dict(row) for row in rows]
        print(f"✅ {table}: {len(rows)} rows")
    except Exception as e:
        print(f"⚠️ {table}: {e}")
        data[table] = []

conn.close()

with open('data_export.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)

print(f"\n✅ Exported to data_export.json")