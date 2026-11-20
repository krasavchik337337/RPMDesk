from database.connection import get_connection
from config import DEFAULT_SETTINGS




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
    settings = DEFAULT_SETTINGS.copy()

    con = get_connection()

    try:
        results = con.execute(
            """
            SELECT key, value
            FROM settings
            """
        ).fetchall()

        for row in results:
            settings[row["key"]] = row["value"]

        return settings
    finally:
        con.close()


def set_setting(key, value):
    con = get_connection()

    try:
        con.execute(
            """
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, str(value)),
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
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(KEY) DO UPDATE SET value = excluded.value
                """,
                (key, str(value))
            )

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()
