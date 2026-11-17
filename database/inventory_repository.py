from database.connection import get_connection


def add_inventory_item(
        name,
        vehicle_make,
        brand,
        category,
        unit,
        unit_price,
        notes=""
):
    con = get_connection()
    con.execute(
        """
        INSERT INTO inventory (
            name,
            vehicle_make,
            brand,
            category,
            unit,
            unit_price,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            vehicle_make,
            brand,
            category,
            unit,
            unit_price,
            notes
        )
    )


def get_inventory_items():
    con = get_connection()
    return con.execute(
        """
        SELECT inventory.*,
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
        """
    ).fetchall()


def get_inventory_item(inventory_id):
    con = get_connection()
    return con.execute(
        """
        SELECT *
        FROM inventory
        WHERE id = ?
        """,
        (inventory_id,)
    ).fetchone()
