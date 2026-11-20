from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, \
    QHeaderView, QSizePolicy
from database import dashboard_repository
from database.settings_repository import get_all_settings


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.load_dashboard()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 25)
        main_layout.setSpacing(18)

        self.organization_card = self.create_card(
            "Organization"
        )

        self.organization_name = QLabel()
        self.organization_name.setObjectName("section_title")
        self.organization_name.setWordWrap(True)

        self.service_name_label = QLabel()
        self.service_name_label.setObjectName("dashboard_secondary")
        self.service_name_label.setWordWrap(True)

        self.organization_address = QLabel()
        self.organization_address.setObjectName("search_label")
        self.organization_address.setWordWrap(True)

        self.organization_card.layout().addWidget(
            self.organization_name
        )
        self.organization_card.layout().addWidget(
            self.service_name_label
        )
        self.organization_card.layout().addWidget(
            self.organization_address
        )

        main_layout.addWidget(self.organization_card)

        statistics_layout = QGridLayout()
        statistics_layout.setSpacing(15)

        self.customers_card, self.customers_value = (
            self.create_stat_card("Active customers")
        )

        self.services_card, self.services_value = (
            self.create_stat_card("Total services")
        )

        statistics_layout.addWidget(
            self.customers_card, 0, 0
        )
        statistics_layout.addWidget(
            self.services_card, 0, 1
        )

        main_layout.addLayout(statistics_layout)

        self.latest_card = self.create_card(
            "Latest service"
        )

        self.latest_service_label = QLabel()
        self.latest_service_label.setWordWrap(True)
        self.latest_service_label.setMinimumWidth(0)
        self.latest_service_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        self.latest_service_label.setObjectName(
            "dashboard_detail"
        )

        self.latest_card.layout().addWidget(
            self.latest_service_label
        )

        main_layout.addWidget(self.latest_card)

        stock_card = self.create_card(
            "Low stock items"
        )

        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(3)
        self.stock_table.setHorizontalHeaderLabels(
            ["Товар", "Количество", "Ед. изм."]
        )

        self.stock_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )

        self.stock_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )

        self.stock_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        self.stock_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.stock_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.setMinimumHeight(180)

        stock_card.layout().addWidget(self.stock_table)

        main_layout.addWidget(stock_card)
        main_layout.addStretch()

    @staticmethod
    def create_card(title):
        card = QFrame()
        card.setObjectName("dashboard_card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(10)

        heading = QLabel(title)
        heading.setObjectName("section_title")

        layout.addWidget(heading)

        return card

    def create_stat_card(self, title):
        card = self.create_card(title)

        value = QLabel("0")
        value.setObjectName("dashboard_value")

        card.layout().addWidget(value)

        return card, value

    def load_dashboard(self):
        self.load_organization()
        self.load_statistics()
        self.load_latest_service()
        self.load_low_stock()

    def load_organization(self):
        settings = get_all_settings()

        service_name = settings.get(
            "service_name", ""
        ).strip()

        organization = settings.get(
            "organization", ""
        ).strip()

        address = settings.get(
            "address", ""
        ).strip()

        self.organization_name.setText(
            organization or "Название организации не указано"
        )
        self.service_name_label.setText(
            service_name or "Название организации не указано"
        )
        self.organization_address.setText(
            address or "Адрес не указан"
        )

    def load_statistics(self):
        statistics = (
            dashboard_repository.get_dashboard_statistics()
        )

        self.customers_value.setText(
            str(statistics["customers_count"])
        )

        self.services_value.setText(
            str(statistics["services_count"])
        )

    def load_latest_service(self):
        service = dashboard_repository.get_latest_service()

        if service is None:
            self.latest_service_label.setText(
                "Записей об обслуживании пока нет."
            )
            return

        customer = (
            f'{service["first_name"]} '
            f'{service["last_name"]}'
        )

        vehicle = (
            f'{service["make"]} {service["model"]}'
        )

        if service["year"]:
            vehicle += f' ({service["year"]})'

        details = [
            f'Дата: {service["service_date"]}',
            f'Клиент: {customer}',
            f'Автомобиль: {vehicle}'
        ]

        if service["mileage"] is not None:
            details.append(
                f'Пробег: {service["mileage"]}'
            )

        self.latest_service_label.setText(
            "\n".join(details)
        )

    def load_low_stock(self):
        settings = get_all_settings()

        threshold = int(
            settings.get("low_stock_threshold", "5")
        )

        items = dashboard_repository.get_low_stock_items(
            threshold
        )

        self.stock_table.setRowCount(len(items))

        for row, item in enumerate(items):
            self.stock_table.setItem(
                row,
                0,
                QTableWidgetItem(item["name"])
            )

            self.stock_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(item["stock_balance"])
                )
            )

            unit = (
                "pcs" if item["unit"] == "piece"
                else "ml"
            )

            self.stock_table.setItem(
                row,
                2,
                QTableWidgetItem(unit)
            )

    def refresh_data(self):
        self.load_dashboard()
