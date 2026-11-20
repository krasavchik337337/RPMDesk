from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtGui import QIcon
from ui.widgets.sidebar import Sidebar
from ui.widgets.header import Header
from config import LOGO_PATH
from ui.pages.customers import CustomersPage
from ui.pages.vehicles import VehiclesPage
from ui.pages.inventory import InventoryPage
from ui.pages.service import ServicePage
from ui.pages.settings import SettingsPage
from ui.pages.reports import ReportsPage
from ui.pages.dashboard import DashboardPage
from ui.themes import get_stylesheet
from database.settings_repository import get_all_settings


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("RPMDesk")
        self.setWindowIcon(QIcon(LOGO_PATH))
        self.setMinimumSize(1100, 800)
        self.resize(1400, 850)
        self.apply_theme()

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
                page.theme_changed.connect(self.apply_theme)
            elif page_name == "Reports":
                page = ReportsPage()
            elif page_name == "Dashboard":
                page = DashboardPage()

            self.pages.addWidget(page)

        content_layout.addWidget(self.header)
        content_layout.addWidget(self.pages)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content)

        self.sidebar.page_changed.connect(self.change_page)

    def change_page(self, index):
        self.pages.setCurrentIndex(index)

        page_name = self.sidebar.pages[index]
        current_page = self.pages.widget(index)
        self.header.set_title(page_name)

        refresh_method = getattr(current_page, "refresh_data", None)

        if callable(refresh_method):
            refresh_method()

    def apply_theme(self):
        theme = get_all_settings().get("theme")
        self.setStyleSheet(get_stylesheet(theme))
