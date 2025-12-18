import sqlite3

DB_NAME = "sac.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# migrate_assets_table.py
from db_conn import get_connection

conn = get_connection()
cur = conn.cursor()

# Add new columns if they don't exist yet
try:
    cur.execute("ALTER TABLE assets ADD COLUMN asset_tag_id TEXT")
except Exception as e:
    print("asset_tag_id:", e)

try:
    cur.execute("ALTER TABLE assets ADD COLUMN location TEXT")
except Exception as e:
    print("location:", e)

conn.commit()
conn.close()
print("Migration finished.")
