import sqlite3
from database.connection import get_connection

def create_service_record(
    customer_id,
    vehicle_id,
    mileage,
    notes,
    works,
    parts
):
    """
    works:
        [
            {
                "work_type_id": 1,
                "name": "Замена масла",
                "quantity": 1,
                "unit_price": 150000
            }
        ]

    parts:
        [
            {
                "inventory_id": 2,
                "quantity": 5000
            }
        ]

    Все цены указаны в копейках.
    Количество деталей — в штуках или миллилитрах.
    """
    if not works:
        raise ValueError("Добавьте хотя бы одну выполненную работу")

    total_cost = 0

    for work in works:
        if work["unit_price"] < 0:
            raise ValueError("Цена работы не может быть отрицательной")\

        total_cost += work["quantity"] * work["unit_price"]

    con = get_connection()
    vehicle = con.execute(
        """
        SELECT id
        FROM vehicles
        WHERE id = ?
          AND customer_id = ?
          AND is_active = 1
        """,
        (vehicle_id, customer_id)
    ).fetchone()

    if vehicle is None:
        raise ValueError("Автомобиль не найден или не принадлежит этому клиенту")

    cur = con.execute(
        """
        INSERT INTO service_records (
            customer_id,
            vehicle_id,
            mileage,
            notes,
            total_cost
        )
        VALUES (?, ?, ?, ?, 0)
        """,
        (customer_id, vehicle_id, mileage, notes)
    )

    service_record_id = cur.lastrowid

    for work in works:
        quantity = work["quantity"]
        unit_price = work["unit_price"]
        work_total = quantity * unit_price

        con.execute(
            """
            INSERT INTO service_works (
                service_record_id,
                work_type_id,
                name,
                quantity,
                unit_price,
                total_price
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                service_record_id,
                work.get("work_type_id"),
                work["name"],
                quantity,
                unit_price,
                work_total
            )
        )

    for part in parts:
        inventory_id = part["inventory_id"]
        quantity = part["quantity"]

        item = con.execute(
            """
            SELECT id, unit_price
            FROM inventory
            WHERE id = ?
            """,
            (inventory_id,)
        ).fetchone()

        if item is None:
            raise ValueError("Товар не найден")

        unit_price = item["unit_price"]
        part_total = quantity * unit_price

        movement_cur = con.execute(
            """
            INSERT INTO stock_movements (
                inventory_id,
                movement_type,
                quantity,
                unit_price,
                service_record_id,
                note
            )
            VALUES (?, 'write_off', ?, ?, ?, ?)
            """,
            (
                inventory_id,
                quantity,
                unit_price,
                service_record_id,
                "Списание при проведении обслуживания"
            )
        )

        stock_movement_id = movement_cur.lastrowid

        con.execute(
            """
            INSERT INTO used_parts (
                service_record_id,
                inventory_id,
                stock_movement_id,
                quantity,
                unit_price,
                total_price
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                service_record_id,
                inventory_id,
                stock_movement_id,
                quantity,
                unit_price,
                part_total
            )
        )

        total_cost += part_total

    con.execute(
        """
        UPDATE service_records
        SET total_cost = ?
        WHERE id = ?
        """,
        (total_cost, service_record_id)
    )

    return service_record_id


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