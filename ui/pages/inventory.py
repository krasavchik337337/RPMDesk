from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, \
    QMessageBox, QHeaderView
from database.inventory_repository import get_inventory_items


class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_inventory)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.refresh_button)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Название",
            "Марка автомобиля",
            "Производитель",
            "Категория",
            "Ед. изм.",
            "Остаток",
            "Цена"
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addLayout(buttons_layout)
        layout.addWidget(self.table)

        self.load_inventory()



    def load_inventory(self):
        try:
            items = get_inventory_items()

            self.table.setRowCount(len(items))

            for row, item in enumerate(items):
                values = [
                    item["name"],
                    item["vehicle_make"] or "—",
                    item["brand"] or "—",
                    item["category"],
                    item["unit"],
                    str(item["stock"]),
                    f'{item["unit_price"] / 100:.2f} ₽'
                ]

                for column, value in enumerate(values):
                    self.table.setItem(
                        row,
                        column,
                        QTableWidgetItem(str(value))
                    )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить склад:\n{error}"
            )

