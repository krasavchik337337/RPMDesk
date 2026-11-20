from pathlib import Path
from database.connection import get_connection

SCHEMA_PATH = Path(__file__).resolve().parent / "scheme.txt"


def initialize_database():
    con = get_connection()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            schema = file.read()

        con.executescript(schema)
        con.commit()

    finally:
        con.close()
