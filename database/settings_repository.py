from database.connection import get_connection


DEFAULT_SETTINGS = {
    "service_name": "",
    "organization": "",
    "address": "",
    "phone": "",
    "email": "",
    "theme": "dark",
    "currency": "RUB",
    "exchange_rate_usd": "0",
    "exchange_rate_eur": "0",
    "low_stock_threshold": "5"
}


def initialize_settings():
    con = get_connection()

    try:
        for key, value in DEFAULT_SETTINGS.items():
            con.execute(
                """
                INSERT OR IGNORE INTO settings (key, value)
                VALUES (?, ?)
                """,
                (key, value)
            )

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def get_setting(key, default=None):
    con = get_connection()

    try:
        result = con.execute(
            """
            SELECT value
            FROM settings
            WHERE key = ?
            """,
            (key,)
        ).fetchone()

        if result is None:
            return default

        return result["value"]

    finally:
        con.close()


def get_all_settings():
    con = get_connection()

    try:
        results = con.execute(
            """
            SELECT key, value
            FROM settings
            """
        ).fetchall()

        return {
            row["key"]: row["value"]
            for row in results
        }

    finally:
        con.close()


def set_setting(key, value):
    con = get_connection()

    try:
        con.execute(
            """
            UPDATE settings 
            SET value = ? 
            HERE key = ?
            """,
            (str(value), key)
        )


        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def set_settings(settings):
    con = get_connection()

    try:
        for key, value in settings.items():
            con.execute(
                """
                UPDATE settings 
                SET value = ? 
                WHERE key = ?
                """,
                (str(value), key)
            )

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()
