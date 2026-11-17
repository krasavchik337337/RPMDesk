from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, \
    QLineEdit, QLabel
from ui.dialogs.customer_dialog import CustomerDialog
from database.customers_repository import get_all_customers


class CustomersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        top_layout = QHBoxLayout()

        search_label = QLabel("Введите атрибут клиента:")
        search_label.setObjectName("search_label")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск клиента...")
        self.search_input.textChanged.connect(self.search_customers)

        add_button = QPushButton("Добавить клиента")
        add_button.clicked.connect(self.open_add_dialog)

        top_layout.addWidget(search_label)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(add_button)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Имя",
            "Фамилия",
            "Телефон",
            "Email"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        layout.addWidget(self.table)

        self.load_customers()

    def load_customers(self):
        customers = get_all_customers()

        self.table.setRowCount(len(customers))

        for row, customer in enumerate(customers):
            values = [
                customer["id"],
                customer["first_name"],
                customer["last_name"],
                customer["phone"],
                customer["email"] or ""
            ]

            for column, value in enumerate(values):
                self.table.setItem(
                    row, column, QTableWidgetItem(str(value))
                )

    def search_customers(self, text):
        text = text.lower().strip()

        for row in range(self.table.rowCount()):
            match = False

            for column in range(1, self.table.columnCount()):
                item = self.table.item(row, column)

                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def open_add_dialog(self):
        dialog = CustomerDialog(self)

        if dialog.exec():
            self.load_customers()
