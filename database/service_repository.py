from database.connection import get_connection


def create_service_record(
        customer_id,
        vehicle_id,
        mileage,
        notes,
        works,
        parts
):
    if not works:
        raise ValueError(
            "Добавьте хотя бы одну выполненную работу"
        )

    con = get_connection()

    try:
        vehicle = con.execute("""
            SELECT id
            FROM vehicles
            WHERE id = ?
              AND customer_id = ?
              AND is_active = 1
        """, (vehicle_id, customer_id)).fetchone()

        if vehicle is None:
            raise ValueError(
                "Автомобиль не найден или не принадлежит этому клиенту"
            )

        customer = con.execute("""
            SELECT id
            FROM customers
            WHERE id = ? AND is_active = 1
        """, (customer_id,)).fetchone()

        if customer is None:
            raise ValueError("Клиент не найден или деактивирован")

        cursor = con.execute("""
            INSERT INTO service_records (
                customer_id,
                vehicle_id,
                mileage,
                notes
            )
            VALUES (?, ?, ?, ?)
        """, (customer_id, vehicle_id, mileage, notes))

        service_record_id = cursor.lastrowid

        for work in works:
            if work["quantity"] <= 0:
                raise ValueError(
                    "Количество работ должно быть больше нуля"
                )

            con.execute("""
                INSERT INTO service_works (
                    service_record_id,
                    work_type_id,
                    name,
                    quantity
                )
                VALUES (?, ?, ?, ?)
            """, (
                service_record_id,
                work.get("work_type_id"),
                work["name"],
                work["quantity"]
            ))

        for part in parts:
            inventory_id = part["inventory_id"]
            quantity = part["quantity"]

            if quantity <= 0:
                raise ValueError(
                    "Количество деталей должно быть больше нуля"
                )

            item = con.execute("""
                SELECT id
                FROM inventory
                WHERE id = ?
            """, (inventory_id,)).fetchone()

            if item is None:
                raise ValueError("Товар не найден")

            movement_cursor = con.execute("""
                INSERT INTO stock_movements (
                    inventory_id,
                    movement_type,
                    quantity,
                    service_record_id,
                    note
                )
                VALUES (
                    ?, 'write_off', ?, ?,
                    'Списание при проведении обслуживания'
                )
            """, (
                inventory_id,
                quantity,
                service_record_id
            ))

            stock_movement_id = movement_cursor.lastrowid

            con.execute("""
                INSERT INTO used_parts (
                    service_record_id,
                    inventory_id,
                    stock_movement_id,
                    quantity
                )
                VALUES (?, ?, ?, ?)
            """, (
                service_record_id,
                inventory_id,
                stock_movement_id,
                quantity
            ))

        con.commit()
        return service_record_id

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def get_service_history(customer_id=None, vehicle_id=None):
    query = """
        SELECT
            service_records.*,
            customers.first_name,
            customers.last_name,
            vehicles.make,
            vehicles.model,
            vehicles.year
        FROM service_records
        JOIN customers ON customers.id = service_records.customer_id
        JOIN vehicles ON vehicles.id = service_records.vehicle_id
    """

    conditions = []
    params = []

    if customer_id is not None:
        conditions.append("service_records.customer_id = ?")
        params.append(customer_id)

    if vehicle_id is not None:
        conditions.append("service_records.vehicle_id = ?")
        params.append(vehicle_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY service_records.service_date DESC"

    con = get_connection()
    return con.execute(query, params).fetchall()


def get_service_details(service_record_id):
    with get_connection() as con:
        record = con.execute(
            """
            SELECT
                service_records.*,
                customers.first_name,
                customers.last_name,
                vehicles.make,
                vehicles.model,
                vehicles.year,
                vehicles.vin
            FROM service_records
            JOIN customers ON customers.id = service_records.customer_id
            JOIN vehicles ON vehicles.id = service_records.vehicle_id
            WHERE service_records.id = ?
            """,
            (service_record_id,)
        ).fetchone()

        if record is None:
            return None

        works = con.execute(
            """
            SELECT *
            FROM service_works
            WHERE service_record_id = ?
            """,
            (service_record_id,)
        ).fetchall()

        parts = con.execute(
            """
            SELECT
                used_parts.*,
                inventory.name,
                inventory.unit,
                inventory.brand
            FROM used_parts
            JOIN inventory
                ON inventory.id = used_parts.inventory_id
            WHERE used_parts.service_record_id = ?
            """,
            (service_record_id,)
        ).fetchall()

        return {
            "record": record,
            "works": works,
            "parts": parts
        }
