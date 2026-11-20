
from database.connection import get_connection


def add_inventory_item(
        name,
        brand,
        category,
        unit,
        initial_quantity,
        notes=""
):
    con = get_connection()

    try:
        cursor = con.execute("""
            INSERT INTO inventory (
                name,
                brand,
                category,
                unit,
                notes
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            brand,
            category,
            unit,
            notes
        ))

        inventory_id = cursor.lastrowid

        if initial_quantity > 0:
            con.execute("""
                INSERT INTO stock_movements (
                    inventory_id,
                    movement_type,
                    quantity,
                    note
                )
                VALUES (?, 'receipt', ?, 'Начальное количество')
            """, (
                inventory_id,
                initial_quantity
            ))

        con.commit()
        return inventory_id

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def get_inventory_items():
    con = get_connection()

    try:
        items = con.execute("""
            SELECT
                inventory.*,
                COALESCE(
                    SUM(
                        CASE
                            WHEN stock_movements.movement_type
                                IN ('receipt', 'correction_in')
                            THEN stock_movements.quantity
                            ELSE -stock_movements.quantity
                        END
                    ),
                    0
                ) AS stock
            FROM inventory
            LEFT JOIN stock_movements
                ON inventory.id = stock_movements.inventory_id
            GROUP BY inventory.id
            ORDER BY inventory.name
        """).fetchall()

        return items

    finally:
        con.close()


def add_stock_movement(
        inventory_id,
        movement_type,
        quantity,
        note=""
):
    allowed_types = (
        "receipt",
        "write_off",
        "correction_in",
        "correction_out"
    )

    if movement_type not in allowed_types:
        raise ValueError("Недопустимый тип складской операции.")

    if quantity <= 0:
        raise ValueError("Количество должно быть больше нуля.")

    con = get_connection()

    try:
        cursor = con.execute("""
            INSERT INTO stock_movements (
                inventory_id,
                movement_type,
                quantity,
                note
            )
            VALUES (?, ?, ?, ?)
        """, (
            inventory_id,
            movement_type,
            quantity,
            note
        ))

        con.commit()
        return cursor.lastrowid

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def get_stock_movements(inventory_id=None):
    con = get_connection()

    try:
        query = """
            SELECT
                stock_movements.*,
                inventory.name AS item_name,
                inventory.unit AS item_unit
            FROM stock_movements
            JOIN inventory
                ON inventory.id = stock_movements.inventory_id
        """

        params = ()

        if inventory_id is not None:
            query += """
                WHERE stock_movements.inventory_id = ?
            """
            params = (inventory_id,)

        query += """
            ORDER BY stock_movements.created_at DESC,
                     stock_movements.id DESC
        """

        return con.execute(query, params).fetchall()

    finally:
        con.close()
