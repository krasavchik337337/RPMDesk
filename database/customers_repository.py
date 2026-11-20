from database.connection import get_connection


def add_customer(first_name, last_name, phone, email, notes):
    con = get_connection()

    try:
        con.execute("""
            INSERT INTO customers (
                first_name,
                last_name,
                phone,
                email,
                notes
            )
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, phone, email, notes))

        con.commit()

    finally:
        con.close()


def get_all_customers():
    con = get_connection()

    try:
        customers = con.execute("""
                SELECT *
                FROM customers
                WHERE is_active = 1
                ORDER BY last_name, first_name
            """).fetchall()

    finally:
        con.close()

    return customers


def get_customer_by_id(customer_id):
    con = get_connection()

    try:
        customer = con.execute("""
            SELECT * FROM customers
            WHERE id = ? AND is_active = 1
        """, (customer_id,)).fetchone()

    finally:
        con.close()

    return customer


def get_customers_by_name(first_name, last_name):
    con = get_connection()

    try:
        customer = con.execute("""
            SELECT * FROM customers
            WHERE LOWER(TRIM(first_name)) = LOWER(TRIM(?))
              AND LOWER(TRIM(last_name)) = LOWER(TRIM(?))
              AND is_active = 1
            ORDER BY id
        """, (first_name, last_name)).fetchall()

    finally:
        con.close()

    return customer


def deactivate_client(customer_id):
    con = get_connection()

    try:
        con.execute("""
            UPDATE customers
            SET is_active = 0
            WHERE id = ?
        """, (customer_id,))

        con.execute("""
            UPDATE vehicles
            SET is_active = 0
            WHERE customer_id = ?
        """, (customer_id,))

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()
