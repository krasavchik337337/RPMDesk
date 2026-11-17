import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "rpm_desk.db"


def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    return con
