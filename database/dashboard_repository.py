from database.connection import get_connection


def get_dashboard_statistics():
    con = get_connection()

    try:
        customers_count = con.execute(
            """
            SELECT COUNT(*)
            FROM customers
            WHERE is_active = 1
            """
        ).fetchone()[0]

        services_count = con.execute(
            """
            SELECT COUNT(*)
            FROM service_records
            """
        ).fetchone()[0]

        return {
            "customers_count": customers_count,
            "services_count": services_count
        }

    finally:
        con.close()


def get_latest_service():
    con = get_connection()

    try:
        return con.execute(
            """
            SELECT
                sr.id,
                sr.service_date,
                sr.mileage,
                c.first_name,
                c.last_name,
                v.make,
                v.model,
                v.year
            FROM service_records AS sr
            JOIN customers AS c
                ON c.id = sr.customer_id
            JOIN vehicles AS v
                ON v.id = sr.vehicle_id
            ORDER BY sr.service_date DESC, sr.id DESC
            LIMIT 1
            """
        ).fetchone()

    finally:
        con.close()


def get_low_stock_items(threshold):
    con = get_connection()

    try:
        return con.execute(
            """
            SELECT
                i.id,
                i.name,
                i.unit,
                COALESCE(
                    SUM(
                        CASE
                            WHEN sm.movement_type IN (
                                'receipt',
                                'correction_in'
                            )
                            THEN sm.quantity

                            WHEN sm.movement_type IN (
                                'write_off',
                                'correction_out'
                            )
                            THEN -sm.quantity

                            ELSE 0
                        END
                    ),
                    0
                ) AS stock_balance
            FROM inventory AS i
            LEFT JOIN stock_movements AS sm
                ON sm.inventory_id = i.id
            GROUP BY i.id
            HAVING stock_balance < ?
            ORDER BY stock_balance ASC, i.name ASC
            """,
            (threshold,)
        ).fetchall()

    finally:
        con.close()
