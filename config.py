import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

BASE_DIR =resource_path(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "content", "RPMDesk_logo3.png")
PLAN_PARTS_TOKEN  = "1712|q2J7rMwjyEvgZYI48LGtiREaNeADTEicOlJCgjJQ99a0b5af"
