
from database.connection import get_connection


def get_report_customers():
    """Return active customers for report filters."""
    con = get_connection()

    try:
        return con.execute("""
            SELECT id, first_name, last_name
            FROM customers
            WHERE is_active = 1
            ORDER BY last_name, first_name
        """).fetchall()

    finally:
        con.close()


def get_report_vehicles(customer_id=None):
    """Return active vehicles, optionally filtered by customer."""
    con = get_connection()

    try:
        query = """
            SELECT id, customer_id, make, model, year
            FROM vehicles
            WHERE is_active = 1
        """

        params = []

        if customer_id is not None:
            query += " AND customer_id = ?"
            params.append(customer_id)

        query += " ORDER BY make, model, year"

        return con.execute(query, params).fetchall()

    finally:
        con.close()


def get_service_history_report(
        date_from,
        date_to,
        customer_id=None,
        vehicle_id=None
):
    """Return completed service records with works and used parts."""
    query = """
        SELECT
            sr.id,
            sr.service_date,
            c.first_name,
            c.last_name,
            v.make,
            v.model,
            v.year,
            sr.mileage,
            sr.notes,

            (
                SELECT GROUP_CONCAT(
                    sw.name || ' x ' || sw.quantity,
                    '; '
                )
                FROM service_works sw
                WHERE sw.service_record_id = sr.id
            ) AS works,

            (
                SELECT GROUP_CONCAT(
                    i.name || ' x ' || up.quantity,
                    '; '
                )
                FROM used_parts up
                JOIN inventory i
                    ON i.id = up.inventory_id
                WHERE up.service_record_id = sr.id
            ) AS used_parts

        FROM service_records sr

        JOIN customers c
            ON c.id = sr.customer_id

        JOIN vehicles v
            ON v.id = sr.vehicle_id

        WHERE date(sr.service_date) BETWEEN ? AND ?
    """

    params = [date_from, date_to]

    if customer_id is not None:
        query += " AND sr.customer_id = ?"
        params.append(customer_id)

    if vehicle_id is not None:
        query += " AND sr.vehicle_id = ?"
        params.append(vehicle_id)

    query += " ORDER BY sr.service_date DESC"

    con = get_connection()

    try:
        return con.execute(query, params).fetchall()

    finally:
        con.close()


def get_service_statistics_report(
        date_from,
        date_to,
        customer_id=None,
        vehicle_id=None
):
    """Return service statistics, popular works and monthly activity."""
    conditions = [
        "date(sr.service_date) BETWEEN ? AND ?"
    ]

    params = [date_from, date_to]

    if customer_id is not None:
        conditions.append("sr.customer_id = ?")
        params.append(customer_id)

    if vehicle_id is not None:
        conditions.append("sr.vehicle_id = ?")
        params.append(vehicle_id)

    where_clause = " AND ".join(conditions)

    con = get_connection()

    try:
        summary = con.execute(f"""
            SELECT
                COUNT(*) AS visit_count,
                COALESCE(SUM((
                    SELECT SUM(sw.quantity)
                    FROM service_works sw
                    WHERE sw.service_record_id = sr.id
                )), 0) AS work_count
            FROM service_records sr
            WHERE {where_clause}
        """, params).fetchone()

        popular_works = con.execute(f"""
            SELECT
                sw.name,
                SUM(sw.quantity) AS quantity
            FROM service_works sw

            JOIN service_records sr
                ON sr.id = sw.service_record_id

            WHERE {where_clause}

            GROUP BY sw.name
            ORDER BY quantity DESC, sw.name
        """, params).fetchall()

        activity = con.execute(f"""
            SELECT
                strftime('%Y-%m', sr.service_date) AS month,
                COUNT(*) AS visit_count
            FROM service_records sr
            WHERE {where_clause}
            GROUP BY strftime('%Y-%m', sr.service_date)
            ORDER BY month
        """, params).fetchall()

        return {
            "summary": summary,
            "popular_works": popular_works,
            "activity": activity
        }

    finally:
        con.close()


def get_inventory_balance_report():
    """Return inventory items and their calculated stock balances."""
    con = get_connection()

    try:
        return con.execute("""
            SELECT
                i.id,
                i.name,
                i.brand,
                i.category,
                i.unit,
                i.notes,

                COALESCE(
                    SUM(
                        CASE
                            WHEN sm.movement_type
                                IN ('receipt', 'correction_in')
                            THEN sm.quantity
                            ELSE -sm.quantity
                        END
                    ),
                    0
                ) AS stock

            FROM inventory i

            LEFT JOIN stock_movements sm
                ON sm.inventory_id = i.id

            GROUP BY i.id

            ORDER BY i.category, i.name
        """).fetchall()

    finally:
        con.close()


def get_stock_movements_report(
        date_from,
        date_to,
        customer_id=None,
        vehicle_id=None
):
    """Return stock movements with optional service filters."""
    query = """
        SELECT
            sm.id,
            sm.created_at,
            i.name AS item_name,
            i.category,
            i.unit,
            sm.movement_type,
            sm.quantity,
            sm.note,
            sr.id AS service_record_id

        FROM stock_movements sm

        JOIN inventory i
            ON i.id = sm.inventory_id

        LEFT JOIN service_records sr
            ON sr.id = sm.service_record_id

        WHERE date(sm.created_at) BETWEEN ? AND ?
    """

    params = [date_from, date_to]

    if customer_id is not None:
        query += " AND sr.customer_id = ?"
        params.append(customer_id)

    if vehicle_id is not None:
        query += " AND sr.vehicle_id = ?"
        params.append(vehicle_id)

    query += """
        ORDER BY sm.created_at DESC, sm.id DESC
    """

    con = get_connection()

    try:
        return con.execute(query, params).fetchall()

    finally:
        con.close()
