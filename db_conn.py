import sqlite3
import os
import sys
import shutil

APP_NAME = "Asset Manager"

def get_app_data_dir():
    base = os.path.expanduser("~/Library/Application Support")
    app_dir = os.path.join(base, APP_NAME)
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_db_path():
    app_db_path = os.path.join(get_app_data_dir(), "sac.db")

    if os.path.exists(app_db_path):
        print("USING APP DB:", app_db_path)
        return app_db_path

    if getattr(sys, "frozen", False):
        bundled_db = os.path.join(sys._MEIPASS, "sac.db")
    else:
        bundled_db = os.path.join(os.path.dirname(__file__), "sac.db")

    shutil.copyfile(bundled_db, app_db_path)
    print("COPIED DB TO:", app_db_path)
    return app_db_path

def get_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
