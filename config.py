import sys
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


BASE_DIR = resource_path(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "content", "RPMDesk_logo3.png")

NHTSA_URL = (
    "https://vpic.nhtsa.dot.gov/api/vehicles/"
    "DecodeVinValuesExtended/{}?format=json"
)
WENMAR_URL = "https://open.wenmarpro.com/v1/vin/{}"

DBVIN_URL = "https://db.vin/api/v1/vin/{}"

DEFAULT_SETTINGS = {
    "service_name": "",
    "organization": "",
    "address": "",
    "phone": "",
    "email": "",
    "theme": "dark",
    "low_stock_threshold": "5",
    "api_plan_parts_token": "1712|q2J7rMwjyEvgZYI48LGtiREaNeADTEicOlJCgjJQ99a0b5af",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": "587",
    "smtp_username": "door.dooro.vich567@gmail.com",
    "smtp_password": "ltid elkz symh mdna",
    "smtp_security": "starttls"
}

REPORT_NAMES = {
    "service_history": "Service History Report",
    "service_statistics": "Service Statistics Report",
    "inventory_balance": "Inventory Balance Report",
    "stock_movements": "Stock Movements Report"
}

MOVEMENT_NAMES = {
    "receipt": "Receipt",
    "write_off": "Write-off",
    "correction_in": "Correction (+)",
    "correction_out": "Correction (-)"
}
