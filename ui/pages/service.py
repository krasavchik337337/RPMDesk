from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, \
    QLineEdit, QLabel, QMessageBox
from database.service_repository import get_service_history


class ServicePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_history)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.refresh_button)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Дата",
            "Клиент",
            "Автомобиль",
            "Год",
            "Пробег",
            "Стоимость",
            "Примечания"
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addLayout(buttons_layout)
        layout.addWidget(self.table)

        self.load_history()

    def load_history(self):
        try:
            records = get_service_history()

            self.table.setRowCount(len(records))

            for row, record in enumerate(records):
                values = [
                    record["service_date"],
                    (
                        f'{record["first_name"]} '
                        f'{record["last_name"]}'
                    ),
                    f'{record["make"]} {record["model"]}',
                    str(record["year"] or "—"),
                    str(record["mileage"] or "—"),
                    f'{record["total_cost"] / 100:.2f} ₽',
                    record["notes"] or "—"
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
                f"Не удалось загрузить историю обслуживания:\n{error}"
            )
