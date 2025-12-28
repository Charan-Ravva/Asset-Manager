from db_conn import get_connection

conn = get_connection()
cur = conn.cursor()

# Check if assets table exists
cur.execute("""
SELECT name FROM sqlite_master
WHERE type='table' AND name='assets';
""")

if not cur.fetchone():
    print("assets table does not exist. Skipping migration.")
else:
    try:
        cur.execute("ALTER TABLE assets ADD COLUMN asset_tag_id TEXT")
        print("asset_tag_id column added")
    except Exception as e:
        print("asset_tag_id:", e)

    try:
        cur.execute("ALTER TABLE assets ADD COLUMN location TEXT")
        print("location column added")
    except Exception as e:
        print("location:", e)

conn.commit()
conn.close()
print("Migration finished.")
