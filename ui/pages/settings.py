import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, \
    QLineEdit, QLabel, QMessageBox, QListWidget, QStackedWidget
from database.connection import get_connection
from database.settings_repository import get_all_settings, set_settings


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = get_all_settings()
        self.init_ui()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        self.menu = QListWidget()
        self.menu.setFixedWidth(190)

        self.pages = QStackedWidget()

        self.menu.addItems([
            "General",
            "Appearance",
            "Currency",
            "API",
            "Database",
            "Email"
        ])

        for function in [self.create_general_page, self.create_appearance_page, self.create_currency_page,
                         self.create_api_page, self.create_database_page, self.create_email_page]:
            function()

        content_layout.addWidget(self.menu)
        content_layout.addWidget(self.pages, 1)

        main_layout.addLayout(content_layout)

        bottom_layout = QHBoxLayout()

        bottom_layout.addStretch()

        self.save_button = QPushButton("Save changes")
        self.save_button.clicked.connect(self.save_settings)

        bottom_layout.addWidget(self.save_button)

        main_layout.addLayout(bottom_layout)

        self.menu.currentRowChanged.connect(
            self.pages.setCurrentIndex
        )

        self.menu.setCurrentRow(0)

        self.load_settings()

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

    def create_appearance_page(self):
        page, layout = self.create_page("Appearance")

    def create_currency_page(self):
        page, layout = self.create_page("Currency")

    def create_api_page(self):
        page, layout = self.create_page("VIN decoders")

    def create_database_page(self):
        page, layout = self.create_page("Database")

    def create_email_page(self):
        page, layout = self.create_page("Email")

    def load_settings(self):
        pass

    def save_settings(self):
        pass

    def create_backup(self):
        pass
