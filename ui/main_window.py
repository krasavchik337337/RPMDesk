from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel
from PyQt6.QtGui import QIcon
from ui.widgets.sidebar import Sidebar
from ui.widgets.header import Header
from config import LOGO_PATH
from ui.pages.customers import CustomersPage
from ui.pages.vehicles import VehiclesPage
from ui.pages.inventory import InventoryPage
from ui.pages.service import ServicePage
from ui.pages.settings import SettingsPage



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("RPMDesk")
        self.setWindowIcon(QIcon(LOGO_PATH))
        self.setMinimumSize(1100, 700)
        self.resize(1400, 850)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #111827;
            }

            QWidget#sidebar {
                background-color: #1F2937;
            }

            QLabel#logo {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
            }

            QPushButton#nav_button {
                background-color: transparent;
                color: #9CA3AF;
                border: none;
                border-radius: 7px;
                padding: 13px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton#nav_button:hover {
                background-color: #374151;
                color: #FFFFFF;
            }

            QPushButton#nav_button:checked {
                background-color: #2563EB;
                color: #FFFFFF;
            }

            QLabel#page_title {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#placeholder, QLabel#search_label {
                color: #9CA3AF;
                font-size: 18px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.header = Header()
        self.pages = QStackedWidget()

        page_names = self.sidebar.pages

        for page_name in page_names:
            if page_name == "Customers":
                page = CustomersPage()
            elif page_name == "Vehicles":
                page = VehiclesPage()
            elif page_name == "Inventory":
                page = InventoryPage()
            elif page_name == "Service":
                page = ServicePage()
            elif page_name == "Settings":
                page = SettingsPage()
            else:
                page = QWidget()
                page_layout = QVBoxLayout(page)

                label = QLabel(f"{page_name} page")
                label.setObjectName("placeholder")

                page_layout.addWidget(label)
                page_layout.addStretch()

            self.pages.addWidget(page)

        content_layout.addWidget(self.header)
        content_layout.addWidget(self.pages)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content)

        self.sidebar.page_changed.connect(self.change_page)

    def change_page(self, index):
        self.pages.setCurrentIndex(index)

        page_name = self.sidebar.pages[index]
        self.header.set_title(page_name)
