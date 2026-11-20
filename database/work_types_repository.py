from database.connection import get_connection


def get_work_types():
    con = get_connection()
    return con.execute(
        """
        SELECT * FROM WORK_TYPES
        ORDER BY name
        """).fetchall()
