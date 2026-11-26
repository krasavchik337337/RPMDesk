from database.connection import get_connection
from config import resource_path

SCHEMA_PATH = resource_path("database/scheme.txt")


def initialize_database():
    con = get_connection()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            schema = file.read()

        con.executescript(schema)
        con.commit()

    finally:
        con.close()
