from database.connection import get_connection


def add_work_type(name, description="", default_price=0):
    if not name.strip():
        raise ValueError("Введите название работы")

    if default_price < 0:
        raise ValueError("Цена не может быть отрицательной")

    con = get_connection()
    con.execute(
        """
        INSERT INTO work_types (
            name,
            description,
            default_price
        )
        VALUES (?, ?, ?)
        """,
        (name.strip(), description, default_price)
    )

def get_work_types():
    con = get_connection()
    return con.execute(
        """
        SELECT * FROM WORK_TYPES
        ORDER BY name
        """).fetchall()

def get_work_type(work_type_id):
    with get_connection() as con:
        return con.execute(
            """
            SELECT * FROM work_types
            WHERE id = ?
            """,
            (work_type_id,)
        ).fetchone()

def update_work_type(work_type_id, name, description, default_price):
    if not name.strip():
        raise ValueError("Введите название работы")

    if default_price < 0:
        raise ValueError("Цена не может быть отрицательной")

    with get_connection() as con:
        con.execute(
            """
            UPDATE work_types
            SET name = ?,
                description = ?,
                default_price = ?
            WHERE id = ?
            """,
            (name.strip(), description, default_price, work_type_id)
        )