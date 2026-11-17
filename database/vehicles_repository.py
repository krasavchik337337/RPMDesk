from database.connection import get_connection


def add_vehicle(customer_id, vin, make, model, year, engine, notes):
    con = get_connection()

    try:
        con.execute("""
            INSERT INTO vehicles (
                customer_id,
                vin,
                make,
                model,
                year,
                engine,
                notes
            )
            VALUES (?,?,?,?,?,?,?)
        """, (customer_id, vin or None, make, model, year, engine, notes or None))

        con.commit()

    finally:
        con.close()


def get_all_vehicles():
    con = get_connection()
    try:
        vehicles = con.execute("""
            SELECT vehicles.*, customers.first_name, customers.last_name 
            FROM vehicles
            JOIN customers ON customers.id = vehicles.customer_id
            WHERE customers.is_active = 1
            ORDER BY vehicles.id DESC
        """).fetchall()

    finally:
        con.close()

    return vehicles
