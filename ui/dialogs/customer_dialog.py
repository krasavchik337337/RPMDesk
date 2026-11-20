from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox
from database.customers_repository import add_customer


class CustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Добавление клиента")
        self.setMinimumWidth(400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.notes_input = QTextEdit()

        form.addRow("Имя:", self.first_name_input)
        form.addRow("Фамилия:", self.last_name_input)
        form.addRow("Телефон:", self.phone_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Примечания:", self.notes_input)

        layout.addLayout(form)

        save_button = QPushButton("Добавить клиента", self)
        save_button.clicked.connect(self.save_customer)
        layout.addWidget(save_button)

    def save_customer(self):
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        notes = self.notes_input.toPlainText().strip()

        if not first_name or not last_name or not phone:
            QMessageBox.warning(
                self,
                "Error",
                "Заполни имя, фамилию и телефон."
            )
            return

        try:
            add_customer(
                first_name,
                last_name,
                phone,
                email,
                notes
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Database error",
                str(error)
            )
            return

        QMessageBox.information(
            self,
            "Successful",
            "Клиент добавлен."
        )

        self.accept()
