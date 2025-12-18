from db_conn import get_connection

conn = get_connection()
c = conn.cursor()

alter_commands = [
    "ALTER TABLE checkout ADD COLUMN phone TEXT;",
    "ALTER TABLE checkout ADD COLUMN notes TEXT;",
    "ALTER TABLE checkout ADD COLUMN status TEXT NOT NULL DEFAULT 'Checked Out';",
    "ALTER TABLE assets ADD COLUMN asset_tag_id TEXT;",
    "ALTER TABLE assets ADD COLUMN location TEXT;",
]

for cmd in alter_commands:
    try:
        c.execute(cmd)
        print("OK:", cmd)
    except Exception as e:
        print("SKIPPED:", cmd, "->", e)

conn.commit()
conn.close()
print("Migration done!")
