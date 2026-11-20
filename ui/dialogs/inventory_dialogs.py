from PyQt6.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, \
    QLineEdit, QComboBox, QSpinBox, QDialogButtonBox, QLabel, QAbstractItemView
from database.inventory_repository import get_stock_movements


class AddInventoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Добавить товар")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.category_input = QLineEdit()
        self.unit_combo = QComboBox()
        self.notes_input = QLineEdit()

        self.unit_combo.addItem("Штуки", "piece")
        self.unit_combo.addItem("Миллилитры", "ml")

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 1000000)
        self.quantity_input.setValue(0)

        form.addRow("Название:", self.name_input)
        form.addRow("Производитель:", self.brand_input)
        form.addRow("Категория:", self.category_input)
        form.addRow("Единица измерения:", self.unit_combo)
        form.addRow("Начальное количество:", self.quantity_input)
        form.addRow("Примечание:", self.notes_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Warning",
                "Введите название товара."
            )
            return

        if not self.category_input.text().strip():
            QMessageBox.warning(
                self,
                "Warning",
                "Введите категорию товара."
            )
            return

        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "brand": self.brand_input.text().strip(),
            "category": self.category_input.text().strip(),
            "unit": self.unit_combo.currentData(),
            "initial_quantity": self.quantity_input.value(),
            "notes": self.notes_input.text().strip()
        }


class StockMovementDialog(QDialog):
    def __init__(self, item, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Изменить количество")
        self.resize(400, 250)

        self.item = item

        unit = "шт." if item["unit"] == "piece" else "мл"

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.item_label = QLabel(item["name"])
        self.stock_label = QLabel(f'{item["stock"]} {unit}')

        self.type_combo = QComboBox()
        self.type_combo.addItem("Поступление", "receipt")
        self.type_combo.addItem("Списание", "write_off")
        self.type_combo.addItem("Корректировка (+)", "correction_in")
        self.type_combo.addItem("Корректировка (-)", "correction_out")

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1_000_000)
        self.quantity_input.setValue(1)

        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText(
            "Причина или комментарий"
        )

        form.addRow("Товар:", self.item_label)
        form.addRow("Текущий остаток:", self.stock_label)
        form.addRow("Операция:", self.type_combo)
        form.addRow("Количество:", self.quantity_input)
        form.addRow("Примечание:", self.note_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_data(self):
        return {
            "movement_type": self.type_combo.currentData(),
            "quantity": self.quantity_input.value(),
            "note": self.note_input.text().strip()
        }


class MovementHistoryDialog(QDialog):
    MOVEMENT_NAMES = {
        "receipt": "Поступление",
        "write_off": "Списание",
        "correction_in": "Корректировка (+)",
        "correction_out": "Корректировка (-)"
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("История движений склада")
        self.resize(900, 550)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Дата",
            "Товар",
            "Операция",
            "Количество",
            "Ед. изм.",
            "Примечание"
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table)

        self.load_history()

    def load_history(self):
        movements = get_stock_movements()

        self.table.setRowCount(len(movements))

        for row, movement in enumerate(movements):
            unit = (
                "шт."
                if movement["item_unit"] == "piece"
                else "мл"
            )

            values = [
                movement["created_at"],
                movement["item_name"],
                self.MOVEMENT_NAMES.get(
                    movement["movement_type"],
                    movement["movement_type"]
                ),
                str(movement["quantity"]),
                unit,
                movement["note"] or "—"
            ]

            for column, value in enumerate(values):
                self.table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )
