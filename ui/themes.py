Themes = {
    "dark": {
        "window": "#111827",
        "sidebar": "#1F2937",
        "surface": "#1F2937",
        "surface_hover": "#374151",
        "input": "#111827",
        "text": "#FFFFFF",
        "text_secondary": "#D1D5DB",
        "text_muted": "#9CA3AF",
        "placeholder": "#6B7280",
        "border": "#374151",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "accent_pressed": "#1E40AF",
        "disabled": "#374151",
        "disabled_text": "#9CA3AF",
    },
    "light": {
        "window": "#F3F4F6",
        "sidebar": "#FFFFFF",
        "surface": "#FFFFFF",
        "surface_hover": "#E5E7EB",
        "input": "#FFFFFF",
        "text": "#111827",
        "text_secondary": "#374151",
        "text_muted": "#6B7280",
        "placeholder": "#9CA3AF",
        "border": "#D1D5DB",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "accent_pressed": "#1E40AF",
        "disabled": "#E5E7EB",
        "disabled_text": "#9CA3AF",
    }
}


def get_stylesheet(theme_name):
    colors = Themes.get(theme_name)

    return f"""
         QMainWindow {{
            background-color: {colors["window"]};
        }}

        QWidget#sidebar {{
            background-color: {colors["sidebar"]};
        }}

        QLabel#logo {{
            color: {colors["text"]};
            font-size: 24px;
            font-weight: bold;
        }}

        QPushButton#nav_button {{
            background-color: transparent;
            color: {colors["text_muted"]};
            border: none;
            border-radius: 7px;
            padding: 13px;
            text-align: left;
            font-size: 14px;
        }}

        QPushButton#nav_button:hover {{
            background-color: {colors["surface_hover"]};
            color: {colors["text"]};
        }}

        QPushButton#nav_button:checked {{
            background-color: {colors["accent"]};
            color: #FFFFFF;
        }}

        QLabel#page_title {{
            color: {colors["text"]};
            font-size: 22px;
            font-weight: bold;
        }}

        QLabel#placeholder, QLabel#search_label {{
            color: {colors["text_muted"]};
            font-size: 18px;
        }}

        QWidget#settings_page {{
            background-color: {colors["window"]};
        }}

        QLabel#section_title {{
            color: {colors["text"]};
            font-size: 19px;
            font-weight: bold;
            padding-bottom: 10px;
            border: none;
            background: transparent;
        }}

        QListWidget#settings_menu {{
            background-color: {colors["sidebar"]};
            border: none;
            border-radius: 8px;
            padding: 8px;
            outline: none;
            color: {colors["text_muted"]};
            font-size: 14px;
        }}

        QListWidget#settings_menu::item {{
            padding: 12px;
            border-radius: 6px;
            margin: 2px 0;
        }}

        QListWidget#settings_menu::item:hover {{
            background-color: {colors["surface_hover"]};
            color: {colors["text"]};
        }}

        QListWidget#settings_menu::item:selected {{
            background-color: {colors["accent"]};
            color: #FFFFFF;
        }}

        QGroupBox {{
            background-color: transparent;
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 8px;
            margin-top: 18px;
            padding: 20px 12px 12px 12px;
            font-size: 14px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 6px;
            color: {colors["text"]};
        }}

        QLabel {{
            color: {colors["text_secondary"]};
            font-size: 13px;
        }}

        QLineEdit, QSpinBox, QComboBox {{
            background-color: {colors["input"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 6px;
            padding: 9px 10px;
            min-height: 20px;
            selection-background-color: {colors["accent"]};
        }}

        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 1px solid {colors["accent"]};
        }}

        QLineEdit::placeholder {{
            color: {colors["placeholder"]};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 28px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            selection-background-color: {colors["accent"]};
            selection-color: #FFFFFF;
            border: 1px solid {colors["border"]};
            outline: none;
        }}

        QPushButton {{
            background-color: {colors["accent"]};
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 10px 18px;
            font-size: 13px;
            font-weight: bold;
        }}

        QPushButton:hover {{
            background-color: {colors["accent_hover"]};
        }}

        QPushButton:pressed {{
            background-color: {colors["accent_pressed"]};
        }}

        QPushButton:disabled {{
            background-color: {colors["disabled"]};
            color: {colors["disabled_text"]};
        }}

        QLabel#dashboard_detail {{
            color: {colors["text_secondary"]};
            font-size: 13px;
            font-weight: normal;
            padding: 0px;
            border: none;
            background: transparent;
        }}

        QLabel#dashboard_secondary {{
            color: {colors["text_muted"]};
            font-size: 12px;
            font-weight: normal;
            padding: 0px;
            border: none;
            background: transparent;
        }}

        QDialog {{
            background-color: {colors["window"]};
        }}
        """
