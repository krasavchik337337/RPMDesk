from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, \
    QLineEdit, QLabel, QMessageBox
from ui.dialogs.vehicle_dialog import VehicleDialog
from database.vehicles_repository import get_all_vehicles


class VehiclesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        top_layout = QHBoxLayout()

        search_label = QLabel("Введите атрибут автомобиля:")
        search_label.setObjectName("search_label")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск автомобиля...")
        self.search_input.textChanged.connect(self.search_vehicles)

        add_button = QPushButton("Добавить автомобиль")
        add_button.clicked.connect(self.open_add_dialog)

        top_layout.addWidget(search_label)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(add_button)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "ID Владельца",
            "Марка",
            "Модель",
            "Год выпуска",
            "Двигатель",
            "VIN",
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table)

        self.load_vehicles()

    def search_vehicles(self, text):
        text = text.lower().strip()

        for row in range(self.table.rowCount()):
            match = False

            for column in range(1, self.table.columnCount()):
                item = self.table.item(row, column).text()

                if item and text in item.lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def load_vehicles(self):
        try:
            vehicles = get_all_vehicles()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                str(error)
            )
            return

        self.table.setRowCount(len(vehicles))

        for row, vehicle in enumerate(vehicles):
            values = [
                vehicle["id"],
                vehicle["customer_id"],
                vehicle["make"],
                vehicle["model"],
                vehicle["year"],
                vehicle["engine"],
                vehicle["vin"]
            ]

            for column, value in enumerate(values):
                item = "" if value is None else str(value)

                self.table.setItem(
                    row, column, QTableWidgetItem(item)
                )


    def open_add_dialog(self):
        dialog = VehicleDialog(self)

        if dialog.exec():
            self.load_vehicles()
