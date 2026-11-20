import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox, QListWidget, \
    QSpinBox, QComboBox, QStackedWidget, QGroupBox, QFormLayout, QFileDialog
from database.connection import get_connection
from database.settings_repository import get_all_settings, set_settings
from PyQt6.QtCore import pyqtSignal


class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.settings = get_all_settings()
        self.setObjectName("settings_page")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        self.menu = QListWidget()
        self.menu.setObjectName("settings_menu")
        self.menu.setFixedWidth(190)

        self.pages = QStackedWidget()

        self.menu.addItems([
            "General",
            "Appearance",
            "API",
            "Database",
            "Email"
        ])

        for function in [
            self.create_general_page,
            self.create_appearance_page,
            self.create_api_page,
            self.create_database_page,
            self.create_email_page
        ]:
            function()

        content_layout.addWidget(self.menu)
        content_layout.addWidget(self.pages, 1)

        main_layout.addLayout(content_layout)

        bottom_layout = QHBoxLayout()

        bottom_layout.addStretch()

        self.save_button = QPushButton("Сохранить изменения")
        self.save_button.clicked.connect(self.save_settings)

        bottom_layout.addWidget(self.save_button)

        main_layout.addLayout(bottom_layout)

        self.menu.currentRowChanged.connect(
            self.pages.setCurrentIndex
        )

        self.menu.setCurrentRow(0)

        self.load_settings()

        self.theme_combo.currentIndexChanged.connect(
            self.on_theme_changed
        )

    def create_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)

        heading = QLabel(title)
        heading.setObjectName("section_title")

        layout.addWidget(heading)

        self.pages.addWidget(page)

        return page, layout

    def create_general_page(self):
        page, layout = self.create_page("Service information")

        group = QGroupBox("Business details")
        form = QFormLayout(group)

        self.service_name_input = QLineEdit()
        self.organization_input = QLineEdit()
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()

        form.addRow("Название сервиса:", self.service_name_input)
        form.addRow("Организация:", self.organization_input)
        form.addRow("Адрес:", self.address_input)
        form.addRow("Телефон:", self.phone_input)
        form.addRow("Email:", self.email_input)

        layout.addWidget(group)
        layout.addStretch()

    def create_appearance_page(self):
        page, layout = self.create_page("Appearance")

        group = QGroupBox("Application theme")
        form = QFormLayout(group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.addItem("Light", "light")

        form.addRow("Тема:", self.theme_combo)

        layout.addWidget(group)
        layout.addStretch()

    def create_api_page(self):
        page, layout = self.create_page("VIN decoders")

        group = QGroupBox("API credentials")
        form = QFormLayout(group)

        self.plan_parts_token_input = QLineEdit()
        self.plan_parts_token_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        form.addRow(
            "plan.parts token:",
            self.plan_parts_token_input
        )

        layout.addWidget(group)
        layout.addStretch()

    def create_database_page(self):
        page, layout = self.create_page("Database")

        group = QGroupBox("Backup")
        group_layout = QVBoxLayout(group)

        description = QLabel(
            "Создать резервную копию базы данных RPMDesk вручную."
        )
        description.setWordWrap(True)

        self.backup_button = QPushButton("Создать копию")
        self.backup_button.clicked.connect(self.create_backup)

        group_layout.addWidget(description)
        group_layout.addWidget(self.backup_button)

        layout.addWidget(group)
        layout.addStretch()

    def create_email_page(self):
        page, layout = self.create_page("Email")
        group = QGroupBox("SMTP configuration")
        form = QFormLayout(group)

        self.smtp_host_input = QLineEdit()
        self.smtp_port_input = QSpinBox()
        self.smtp_port_input.setRange(1, 65535)
        self.smtp_port_input.setValue(587)

        self.smtp_username_input = QLineEdit()
        self.smtp_password_input = QLineEdit(self.settings.get("smtp_password"))
        self.smtp_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.smtp_security_combo = QComboBox()
        self.smtp_security_combo.addItem("STARTTLS", "starttls")
        self.smtp_security_combo.addItem("SSL/TLS", "ssl")
        self.smtp_security_combo.addItem("Без шифрования", "none")

        form.addRow("SMTP-сервер:", self.smtp_host_input)
        form.addRow("Порт:", self.smtp_port_input)
        form.addRow("Имя пользователя:", self.smtp_username_input)
        form.addRow("Пароль:", self.smtp_password_input)
        form.addRow("Шифрование:", self.smtp_security_combo)

        layout.addWidget(group)

        layout.addStretch()

    def load_settings(self):
        self.service_name_input.setText(
            self.settings.get("service_name")
        )
        self.organization_input.setText(
            self.settings.get("organization")
        )
        self.address_input.setText(
            self.settings.get("address")
        )
        self.phone_input.setText(
            self.settings.get("phone")
        )
        self.email_input.setText(
            self.settings.get("email")
        )

        self.set_combo_value(
            self.theme_combo,
            self.settings.get("theme")
        )

        self.plan_parts_token_input.setText(
            self.settings.get("api_plan_parts_token")
        )

        self.smtp_host_input.setText(
            self.settings.get("smtp_host")
        )
        self.smtp_port_input.setValue(
            int(self.settings.get("smtp_port"))
        )
        self.smtp_username_input.setText(
            self.settings.get("smtp_username")
        )

        self.set_combo_value(
            self.smtp_security_combo,
            self.settings.get("smtp_security")
        )

    @staticmethod
    def set_combo_value(combo, value):
        index = combo.findData(value)

        if index >= 0:
            combo.setCurrentIndex(index)

    def save_settings(self):
        settings = {
            "service_name": self.service_name_input.text().strip(),
            "organization": self.organization_input.text().strip(),
            "address": self.address_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip(),

            "theme": self.theme_combo.currentData(),

            "api_plan_parts_token": (
                self.plan_parts_token_input.text().strip()
            ),

            "smtp_host": self.smtp_host_input.text().strip(),
            "smtp_port": self.smtp_port_input.value(),
            "smtp_username": self.smtp_username_input.text().strip(),
            "smtp_password": self.smtp_password_input.text().strip(),
            "smtp_security": self.smtp_security_combo.currentData()
        }

        try:
            set_settings(settings)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Save error",
                f"Не получилось сохранить настройки:\n{error}"
            )
            return

        self.settings.update(settings)
        self.theme_changed.emit(settings["theme"])

        QMessageBox.information(
            self,
            "Settings",
            "Настройки успешно сохранены."
        )

    def create_backup(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Settings",
            "settings.json",
            "SQLite Database (*.db *.sqlite);;All Files (*)",
        )

        if not file_path:
            return

        source = None
        destination = None

        try:
            source = get_connection()
            destination = sqlite3.connect(file_path)

            source.backup(destination)

            QMessageBox.information(
                self,
                "Backup",
                "Резервная копия базы данных успешна сохранена."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Backup error",
                f"Не удалось сохранить копию базы данных:\n{error}"
            )

        finally:
            if destination is not None:
                destination.close()

            if source is not None:
                source.close()

    def on_theme_changed(self):
        self.theme_changed.emit(self.theme_combo.currentData())
