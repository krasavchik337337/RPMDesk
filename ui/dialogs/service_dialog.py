from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QComboBox,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialogButtonBox,
    QMessageBox
)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt

from database.connection import get_connection
from database.work_types_repository import get_work_types
from database.inventory_repository import get_inventory_items
from database.service_repository import create_service_record


class ServiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Новое обслуживание")
        self.resize(850, 700)
        if parent is not None:
            self.setStyleSheet(parent.styleSheet())

        self.works = []
        self.parts = []

        self.work_types = []
        self.inventory_items = []

        self.initUI()
        self.load_customers()
        self.load_work_types()
        self.load_inventory()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        customer_group = QGroupBox("Информация об обслуживании")
        customer_layout = QFormLayout(customer_group)

        self.customer_combo = QComboBox()
        self.customer_combo.currentIndexChanged.connect(
            self.load_vehicles
        )

        self.vehicle_combo = QComboBox()

        self.mileage_input = QLineEdit()
        self.mileage_input.setPlaceholderText(
            "Оставьте пустым, если пробег неизвестен"
        )
        self.mileage_input.setValidator(
            QIntValidator(0, 2_000_000, self)
        )

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(
            "Дополнительные примечания"
        )

        customer_layout.addRow("Клиент:", self.customer_combo)
        customer_layout.addRow("Автомобиль:", self.vehicle_combo)
        customer_layout.addRow("Пробег:", self.mileage_input)
        customer_layout.addRow("Примечания:", self.notes_input)

        main_layout.addWidget(customer_group)

        works_group = QGroupBox("Выполненные работы")
        works_layout = QVBoxLayout(works_group)

        works_controls = QHBoxLayout()

        self.work_combo = QComboBox()

        self.work_quantity = QSpinBox()
        self.work_quantity.setRange(1, 10000)
        self.work_quantity.setValue(1)

        self.add_work_button = QPushButton("Добавить работу")
        self.add_work_button.clicked.connect(self.add_work)

        works_controls.addWidget(self.work_combo, 1)
        works_controls.addWidget(self.work_quantity)
        works_controls.addWidget(self.add_work_button)

        self.works_table = QTableWidget()
        self.works_table.setColumnCount(3)
        self.works_table.setHorizontalHeaderLabels([
            "Работа",
            "Количество",
            "ID"
        ])
        self.works_table.setColumnHidden(2, True)
        self.works_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.works_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.remove_work_button = QPushButton("Удалить выбранную работу")
        self.remove_work_button.clicked.connect(
            self.remove_selected_work
        )

        works_layout.addLayout(works_controls)
        works_layout.addWidget(self.works_table)
        works_layout.addWidget(self.remove_work_button)

        main_layout.addWidget(works_group)

        parts_group = QGroupBox("Использованные детали и материалы")
        parts_layout = QVBoxLayout(parts_group)

        parts_controls = QHBoxLayout()

        self.part_combo = QComboBox()

        self.part_quantity = QSpinBox()
        self.part_quantity.setRange(1, 1_000_000)
        self.part_quantity.setValue(1)

        self.add_part_button = QPushButton("Добавить деталь")
        self.add_part_button.clicked.connect(self.add_part)

        parts_controls.addWidget(self.part_combo, 1)
        parts_controls.addWidget(self.part_quantity)
        parts_controls.addWidget(self.add_part_button)

        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(4)
        self.parts_table.setHorizontalHeaderLabels([
            "Деталь",
            "Количество",
            "Ед. изм.",
            "ID"
        ])
        self.parts_table.setColumnHidden(3, True)
        self.parts_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.parts_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.remove_part_button = QPushButton(
            "Удалить выбранную деталь"
        )
        self.remove_part_button.clicked.connect(
            self.remove_selected_part
        )

        parts_layout.addLayout(parts_controls)
        parts_layout.addWidget(self.parts_table)
        parts_layout.addWidget(self.remove_part_button)

        main_layout.addWidget(parts_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.save_service)
        buttons.rejected.connect(self.reject)

        main_layout.addWidget(buttons)

    def load_customers(self):
        con = get_connection()

        try:
            customers = con.execute("""
                SELECT id, first_name, last_name
                FROM customers
                WHERE is_active = 1
                ORDER BY first_name, last_name
            """).fetchall()

        finally:
            con.close()

        self.customer_combo.clear()

        for customer in customers:
            full_name = (
                f'{customer["first_name"]} '
                f'{customer["last_name"]}'
            )

            self.customer_combo.addItem(
                full_name,
                customer["id"]
            )

        self.load_vehicles()

    def load_vehicles(self):
        self.vehicle_combo.clear()

        customer_id = self.customer_combo.currentData()

        if customer_id is None:
            return

        con = get_connection()

        try:
            vehicles = con.execute("""
                SELECT id, make, model, year
                FROM vehicles
                WHERE customer_id = ?
                  AND is_active = 1
                ORDER BY make, model
            """, (customer_id,)).fetchall()

        finally:
            con.close()

        for vehicle in vehicles:
            vehicle_name = (
                f'{vehicle["make"]} {vehicle["model"]}'
            )

            if vehicle["year"]:
                vehicle_name += f' ({vehicle["year"]})'

            self.vehicle_combo.addItem(
                vehicle_name,
                vehicle["id"]
            )

    def load_work_types(self):
        self.work_types = get_work_types()

        self.work_combo.clear()

        for work in self.work_types:
            self.work_combo.addItem(
                work["name"],
                work["id"]
            )

    def load_inventory(self):
        self.inventory_items = get_inventory_items()

        self.part_combo.clear()

        for item in self.inventory_items:
            unit = "шт." if item["unit"] == "piece" else "мл"

            label = (
                f'{item["name"]} '
                f'— остаток: {item["stock"]} {unit}'
            )

            self.part_combo.addItem(
                label,
                item["id"]
            )

    def add_work(self):
        work_type_id = self.work_combo.currentData()

        if work_type_id is None:
            QMessageBox.warning(
                self,
                "Внимание",
                "Сначала добавьте виды работ в справочник."
            )
            return

        work_name = self.work_combo.currentText()
        quantity = self.work_quantity.value()

        row = self.works_table.rowCount()
        self.works_table.insertRow(row)

        self.works_table.setItem(
            row,
            0,
            QTableWidgetItem(work_name)
        )
        self.works_table.setItem(
            row,
            1,
            QTableWidgetItem(str(quantity))
        )

        id_item = QTableWidgetItem()
        id_item.setData(Qt.ItemDataRole.UserRole, work_type_id)

        self.works_table.setItem(row, 2, id_item)

    def remove_selected_work(self):
        row = self.works_table.currentRow()

        if row >= 0:
            self.works_table.removeRow(row)

    def add_part(self):
        inventory_id = self.part_combo.currentData()

        if inventory_id is None:
            QMessageBox.warning(
                self,
                "Внимание",
                "На складе пока нет товаров."
            )
            return

        item = next(
            (
                item for item in self.inventory_items
                if item["id"] == inventory_id
            ),
            None
        )

        if item is None:
            return

        quantity = self.part_quantity.value()

        unit = "шт." if item["unit"] == "piece" else "мл"

        row = self.parts_table.rowCount()
        self.parts_table.insertRow(row)

        self.parts_table.setItem(
            row,
            0,
            QTableWidgetItem(item["name"])
        )
        self.parts_table.setItem(
            row,
            1,
            QTableWidgetItem(str(quantity))
        )
        self.parts_table.setItem(
            row,
            2,
            QTableWidgetItem(unit)
        )

        id_item = QTableWidgetItem()
        id_item.setData(Qt.ItemDataRole.UserRole, inventory_id)

        self.parts_table.setItem(row, 3, id_item)

    def remove_selected_part(self):
        row = self.parts_table.currentRow()

        if row >= 0:
            self.parts_table.removeRow(row)

    def save_service(self):
        customer_id = self.customer_combo.currentData()
        vehicle_id = self.vehicle_combo.currentData()

        if customer_id is None:
            QMessageBox.warning(
                self,
                "Внимание",
                "Выберите клиента."
            )
            return

        if vehicle_id is None:
            QMessageBox.warning(
                self,
                "Внимание",
                "У выбранного клиента нет активного автомобиля."
            )
            return

        if self.works_table.rowCount() == 0:
            QMessageBox.warning(
                self,
                "Внимание",
                "Добавьте хотя бы одну выполненную работу."
            )
            return

        mileage_text = self.mileage_input.text().strip()
        mileage = int(mileage_text) if mileage_text else None

        works = []

        for row in range(self.works_table.rowCount()):
            name = self.works_table.item(row, 0).text()
            quantity = int(self.works_table.item(row, 1).text())
            work_type_id = self.works_table.item(row, 2).data(
                Qt.ItemDataRole.UserRole
            )

            works.append({
                "work_type_id": work_type_id,
                "name": name,
                "quantity": quantity
            })

        parts = []

        for row in range(self.parts_table.rowCount()):
            quantity = int(self.parts_table.item(row, 1).text())
            inventory_id = self.parts_table.item(row, 3).data(
                Qt.ItemDataRole.UserRole
            )

            parts.append({
                "inventory_id": inventory_id,
                "quantity": quantity
            })

        requested = {}

        for part in parts:
            inventory_id = part["inventory_id"]
            requested[inventory_id] = (
                    requested.get(inventory_id, 0)
                    + part["quantity"]
            )

        for inventory_id, quantity in requested.items():
            item = next(
                (
                    item for item in self.inventory_items
                    if item["id"] == inventory_id
                ),
                None
            )

            if item is None or quantity > item["stock"]:
                item_name = (
                    item["name"] if item else "Неизвестный товар"
                )
                available = item["stock"] if item else 0

                QMessageBox.warning(
                    self,
                    "Недостаточно запасов",
                    (
                        f"Недостаточно товара «{item_name}».\n"
                        f"Доступно: {available}.\n"
                        f"Требуется: {quantity}."
                    )
                )
                return

        try:
            create_service_record(
                customer_id=customer_id,
                vehicle_id=vehicle_id,
                mileage=mileage,
                notes=self.notes_input.text().strip(),
                works=works,
                parts=parts
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                (
                    "Не удалось сохранить обслуживание.\n\n"
                    f"{error}"
                )
            )
            return

        QMessageBox.information(
            self,
            "Готово",
            "Обслуживание успешно сохранено."
        )

        self.accept()
