import sqlite3

DB_NAME = "sac.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()

    # ---------- USERS TABLE ----------
    # Admin + staff accounts
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL COLLATE NOCASE UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff'   -- 'admin' or 'staff'
    );
    """)

    # ---------- ASSETS TABLE ----------
    # All equipment in SAC
    c.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_name   TEXT NOT NULL,
        asset_tag_id TEXT,          -- e.g. P1, P2, etc.
        location     TEXT,          -- e.g. Fitness Center
        category     TEXT,          -- e.g. Equipment Checkout
        status       TEXT NOT NULL DEFAULT 'Available'  -- Available / Checked Out / Broken / etc.
    );
    """)

    # ---------- CHECKOUT TABLE ----------
    # Every checkout / check-in event (used by:
    # - Check Out page
    # - Check In page
    # - Student History page)
    c.execute("""
    CREATE TABLE IF NOT EXISTS checkout (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id     INTEGER NOT NULL,
        student_name TEXT   NOT NULL,
        student_id   TEXT   NOT NULL,
        checkout_time TEXT  NOT NULL,
        checkin_time  TEXT,                     -- NULL while still checked out
        status        TEXT  NOT NULL DEFAULT 'Checked Out',
        FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
    );
    """)

    # (Optional) STUDENTS TABLE – not required for history, but safe to keep
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        student_id TEXT NOT NULL UNIQUE,
        phone TEXT,
        email TEXT
    );
    """)

    # ---------- DEFAULT ADMIN USER ----------
    c.execute("""
    INSERT OR IGNORE INTO users (first_name, last_name, email, password, role)
    VALUES ('SAC', 'Admin', 'admin@sac.com', 'admin123', 'admin');
    """)

    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized with tables and default admin ✅")


if __name__ == "__main__":
    init_db()
