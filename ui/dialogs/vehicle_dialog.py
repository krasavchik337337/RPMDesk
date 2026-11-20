from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget, QFormLayout, QComboBox, QLineEdit, QTextEdit, QPushButton, \
    QDialogButtonBox, QMessageBox, QLabel, QHBoxLayout
from database.vehicles_repository import add_vehicle
from database.customers_repository import get_customers_by_name, get_customer_by_id
from vin.decoder import decode_vin


class VehicleDialog(QDialog):
    def __init__(self, parent=None, customer_id=None):
        super().__init__(parent)

        self.customer_id = customer_id
        self.api_notes = ""
        self.setWindowTitle("Добавление автомобиля")
        self.setMinimumWidth(500)

        self.initUI()

        if customer_id is not None:
            self.customer_method.setCurrentIndex(0)
            self.customer_id_input.setText(str(customer_id))
            self.find_customer()

    def initUI(self):
        layout = QVBoxLayout(self)
        customer_form = QFormLayout()

        self.customer_method = QComboBox()
        self.customer_method.addItems([
            "По ID",
            "По имени и фамилии"
        ])

        self.customer_method.currentIndexChanged.connect(
            self.update_customer_fields
        )

        self.customer_id_input = QLineEdit()
        self.customer_id_input.setPlaceholderText("ID клиента")

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Имя")

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Фамилия")

        customer_form.addRow(
            "Способ поиска:",
            self.customer_method
        )

        customer_form.addRow(
            "ID:",
            self.customer_id_input
        )

        customer_form.addRow(
            "Имя:",
            self.first_name_input
        )

        customer_form.addRow(
            "Фамилия:",
            self.last_name_input
        )

        layout.addLayout(customer_form)

        self.find_customer_button = QPushButton(
            "Найти клиента"
        )

        self.find_customer_button.clicked.connect(
            self.find_customer
        )

        layout.addWidget(self.find_customer_button)

        self.customer_result = QLabel(
            "Клиент не выбран"
        )

        layout.addWidget(self.customer_result)

        vehicle_form = QFormLayout()

        self.vehicle_method = QComboBox()
        self.vehicle_method.addItems([
            "По VIN",
            "Вручную"
        ])

        self.vehicle_method.currentIndexChanged.connect(
            self.update_vehicle_fields
        )

        self.vin_input = QLineEdit()
        self.vin_input.setPlaceholderText("Введите 17 символов VIN")

        self.decode_button = QPushButton(
            "Расшифровать VIN"
        )

        self.decode_button.clicked.connect(
            self.decode_vehicle
        )

        vin_layout = QHBoxLayout()
        vin_layout.addWidget(self.vin_input)
        vin_layout.addWidget(self.decode_button)

        self.vin_widget = QWidget()
        self.vin_widget.setLayout(vin_layout)

        vehicle_form.addRow(
            "Способ добавления:",
            self.vehicle_method
        )

        vehicle_form.addRow(
            "VIN:",
            self.vin_widget
        )

        self.make_input = QLineEdit()
        self.model_input = QLineEdit()
        self.year_input = QLineEdit()
        self.engine_input = QLineEdit()

        vehicle_form.addRow("Марка:", self.make_input)
        vehicle_form.addRow("Модель:", self.model_input)
        vehicle_form.addRow("Год:", self.year_input)
        vehicle_form.addRow("Двигатель:", self.engine_input)

        layout.addLayout(vehicle_form)

        layout.addWidget(
            QLabel("Дополнительные данные API:")
        )

        self.api_notes_display = QTextEdit()
        self.api_notes_display.setReadOnly(True)
        self.api_notes_display.setMaximumHeight(120)

        layout.addWidget(self.api_notes_display)

        layout.addWidget(QLabel("Примечания:"))

        self.notes_input = QTextEdit()
        layout.addWidget(self.notes_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.save_vehicle)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.update_customer_fields()
        self.update_vehicle_fields()

    def update_customer_fields(self):
        by_id = self.customer_method.currentIndex() == 0

        self.customer_id_input.setVisible(by_id)

        self.first_name_input.setVisible(not by_id)
        self.last_name_input.setVisible(not by_id)

    def update_vehicle_fields(self):
        by_vin = self.vehicle_method.currentIndex() == 0

        self.vin_widget.setVisible(by_vin)

    def find_customer(self):
        self.customer_id = None

        if self.customer_method.currentIndex() == 0:
            customer_id = self.customer_id_input.text().strip()

            if not customer_id.isdigit():
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Введите корректный ID клиента."
                )
                return

            customer = get_customer_by_id(int(customer_id))

            if customer is None:
                QMessageBox.warning(
                    self,
                    "Клиент не найден",
                    "Активный клиент с таким ID не найден."
                )
                return

        else:
            first_name = self.first_name_input.text().strip()
            last_name = self.last_name_input.text().strip()

            if not first_name or not last_name:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Введите имя и фамилию клиента."
                )
                return

            customers = get_customers_by_name(
                first_name,
                last_name
            )

            if len(customers) == 0:
                QMessageBox.warning(
                    self,
                    "Клиент не найден",
                    "Клиентов с такими именем нет."
                )
                return

            if len(customers) > 1:
                ids = ", ".join(
                    str(customer["id"])
                    for customer in customers
                )

                QMessageBox.warning(
                    self,
                    "Несколько совпадений",
                    f"Найдено несколько клиентов.\n"
                    f"Их ID: {ids}\n\n"
                    f"Введите ID нужного клиента."
                )

                self.customer_method.setCurrentIndex(0)
                self.customer_id_input.clear()
                return

            customer = customers[0]

        self.customer_id = customer["id"]

        self.customer_result.setText(
            f'Выбран клиент: '
            f'{customer["first_name"]} '
            f'{customer["last_name"]}, '
            f'ID: {customer["id"]}, '
            f'телефон: {customer["phone"]}'
        )

    def decode_vehicle(self):
        vin = self.vin_input.text()

        if not vin:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите VIN."
            )
            return

        try:
            data = decode_vin(vin)

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Ошибка расшифровки",
                str(error)
            )
            return

        self.vin_input.setText(vin)

        self.make_input.setText(data["make"])
        self.model_input.setText(data["model"])
        self.year_input.setText(str(data["year"]) if data["year"] else "")
        self.engine_input.setText(data["engine"])
        self.api_notes = data["additional_data"]
        self.api_notes_display.setPlainText(self.api_notes)

        QMessageBox.information(
            self,
            "Готово",
            "Данные автомобиля получены. "
            "Проверьте их перед сохранением."
        )

    def save_vehicle(self):
        if self.customer_id is None:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Сначала выберите клиента."
            )
            return

        make = self.make_input.text().strip()
        model = self.model_input.text().strip()
        year_text = self.year_input.text().strip()
        engine = self.engine_input.text().strip()
        vin = self.vin_input.text().strip().upper()
        user_notes = self.notes_input.toPlainText().strip()

        if not make or not model:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Укажите марку и модель автомобиля."
            )
            return

        try:
            year = int(year_text) if year_text else None

        except ValueError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Год должен быть числом."
            )
            return

        if year is not None and not 1886 <= year <= 2100:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Укажите корректный год выпуска."
            )
            return

        if vin:
            if len(vin) != 17 or any(
                    char in vin for char in "IOQ"
            ):
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "VIN должен содержать 17 символов и не содержать I, O или Q."
                )
                return

        if self.vehicle_method.currentIndex() == 0 and not vin:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Укажите VIN."
            )
            return

        notes_parts = []

        if user_notes:
            notes_parts.append(user_notes)

        if self.api_notes:
            notes_parts.append(
                "Дополнительные данные VIN API:\n"
                + self.api_notes
            )

        notes = "\n".join(notes_parts)

        try:
            add_vehicle(
                self.customer_id,
                vin,
                make,
                model,
                year,
                engine,
                notes
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                str(error)
            )
            return

        QMessageBox.information(
            self,
            "Успешно",
            "Автомобиль добавлен."
        )

        self.accept()
