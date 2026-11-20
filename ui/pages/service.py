from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, \
    QMessageBox, QDialog
from database.service_repository import get_service_history
from ui.dialogs.service_dialog import ServiceDialog


class ServicePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Новое обслуживание")
        self.add_button.clicked.connect(self.open_service_dialog)

        buttons_layout.addWidget(self.add_button)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Дата",
            "Клиент",
            "Автомобиль",
            "Год",
            "Пробег",
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

    def open_service_dialog(self):
        dialog = ServiceDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
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

    def refresh_data(self):
        self.load_history()
