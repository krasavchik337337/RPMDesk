from pathlib import Path
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox, QDateEdit, QPushButton, \
    QFileDialog, QMessageBox, QGroupBox, QFrame, QLineEdit
from database import reports_repository
from services.report_service import generate_report
from services.email_sender import EmailSender
from database.settings_repository import get_all_settings


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.last_report_path = None
        self.init_ui()
        self.load_customers()
        self.load_vehicles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 25)
        main_layout.setSpacing(18)

        description = QLabel(
            "Создать отчеты по услугам и товарным запасам"
        )
        description.setObjectName("search_label")

        main_layout.addWidget(description)

        report_group = QGroupBox("Report")
        report_layout = QVBoxLayout(report_group)

        self.report_combo = QComboBox()

        self.report_combo.addItem(
            "Отчет по истории обслуживания",
            "service_history"
        )

        self.report_combo.addItem(
            "Отчет по статистике услуг",
            "service_statistics"
        )

        self.report_combo.addItem(
            "Отчет по остаткам на складе",
            "inventory_balance"
        )

        self.report_combo.addItem(
            "Отчет по движению товаров",
            "stock_movements"
        )

        self.report_combo.currentIndexChanged.connect(
            self.update_report_options
        )

        report_layout.addWidget(self.report_combo)

        main_layout.addWidget(report_group)

        filters_group = QGroupBox("Filters")
        filters_layout = QGridLayout(filters_group)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        self.date_from.setDate(
            QDate.currentDate().addMonths(-1)
        )

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        self.date_to.setDate(QDate.currentDate())

        self.customer_combo = QComboBox()
        self.customer_combo.currentIndexChanged.connect(
            self.load_vehicles
        )

        self.vehicle_combo = QComboBox()

        filters_layout.addWidget(
            QLabel("Дата с:"), 0, 0
        )
        filters_layout.addWidget(
            self.date_from, 0, 1
        )

        filters_layout.addWidget(
            QLabel("Дата по:"), 0, 2
        )
        filters_layout.addWidget(
            self.date_to, 0, 3
        )

        filters_layout.addWidget(
            QLabel("Клиент:"), 1, 0
        )
        filters_layout.addWidget(
            self.customer_combo, 1, 1
        )

        filters_layout.addWidget(
            QLabel("Автомобиль:"), 1, 2
        )
        filters_layout.addWidget(
            self.vehicle_combo, 1, 3
        )

        main_layout.addWidget(filters_group)

        info_frame = QFrame()
        info_frame.setObjectName("report_info")

        info_layout = QVBoxLayout(info_frame)

        info_title = QLabel("Report information")
        info_title.setObjectName("section_title")

        self.info_label = QLabel(
            "Выберите отчет и настройте фильтры."
        )
        self.info_label.setObjectName("search_label")
        self.info_label.setWordWrap(True)

        info_layout.addWidget(info_title)
        info_layout.addWidget(self.info_label)

        main_layout.addWidget(info_frame)

        email_group = QGroupBox("Send report by email")
        email_layout = QHBoxLayout(email_group)

        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Адрес почты получателя")

        self.send_email_button = QPushButton("Отправить")
        self.send_email_button.setEnabled(False)
        self.send_email_button.clicked.connect(self.send_report_email)

        email_layout.addWidget(self.recipient_input, 1)
        email_layout.addWidget(self.send_email_button)

        main_layout.addWidget(email_group)

        buttons_layout = QHBoxLayout()

        self.generate_button = QPushButton("Export CSV")
        self.generate_button.setObjectName("primary_button")
        self.generate_button.clicked.connect(self.generate_csv)

        self.refresh_button = QPushButton("Сбросить фильтры")

        self.refresh_button.clicked.connect(self.refresh_filters)

        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.generate_button)

        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()

        self.update_report_options()

    def load_customers(self):
        self.customer_combo.blockSignals(True)

        self.customer_combo.clear()
        self.customer_combo.addItem("Все клиенты", None)

        customers = reports_repository.get_report_customers()

        for customer in customers:
            name = (
                f'{customer["last_name"]} '
                f'{customer["first_name"]}'
            )

            self.customer_combo.addItem(
                name,
                customer["id"]
            )

        self.customer_combo.blockSignals(False)

    def load_vehicles(self):
        self.vehicle_combo.clear()
        self.vehicle_combo.addItem("Все автомобили", None)

        customer_id = self.customer_combo.currentData()

        vehicles = reports_repository.get_report_vehicles(
            customer_id
        )

        for vehicle in vehicles:
            name = (
                f'{vehicle["make"]} '
                f'{vehicle["model"]} '
                f'{vehicle["year"] or ""}'
            ).strip()

            self.vehicle_combo.addItem(
                name,
                vehicle["id"]
            )

    def refresh_filters(self):
        self.load_customers()
        self.load_vehicles()

        self.date_to.setDate(QDate.currentDate())
        self.date_from.setDate(QDate.currentDate().addMonths(-1))

    def update_report_options(self):
        report_type = self.report_combo.currentData()

        inventory_report = (
                report_type == "inventory_balance"
        )

        self.date_from.setEnabled(not inventory_report)
        self.date_to.setEnabled(not inventory_report)

        self.customer_combo.setEnabled(not inventory_report)
        self.vehicle_combo.setEnabled(not inventory_report)

        descriptions = {
            "service_history": (
                "Показывает завершенные визиты на обслуживание."
            ),
            "service_statistics": (
                "Показывает статистику визитов."
            ),
            "inventory_balance": (
                "Показывает текущие остатки на складе."
            ),
            "stock_movements": (
                "Показывает складские операции."
            )
        }

        self.info_label.setText(
            descriptions.get(report_type, "")
        )

    def generate_csv(self):
        report_type = self.report_combo.currentData()

        date_from = self.date_from.date().toString(
            "yyyy-MM-dd"
        )

        date_to = self.date_to.date().toString(
            "yyyy-MM-dd"
        )

        customer_id = self.customer_combo.currentData()
        vehicle_id = self.vehicle_combo.currentData()

        if (
                report_type != "inventory_balance"
                and self.date_from.date() > self.date_to.date()
        ):
            QMessageBox.warning(
                self,
                "Invalid period",
                "Дата начала не может быть позже даты окончания."
            )
            return

        default_name = (
            f"{report_type}_"
            f"{QDate.currentDate().toString('yyyy-MM-dd')}.csv"
        )

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export report",
            str(Path.home() / default_name),
            "CSV files (*.csv)"
        )

        if not output_path:
            return

        if not output_path.lower().endswith(".csv"):
            output_path += ".csv"

        self.generate_button.setEnabled(False)

        try:
            generate_report(
                report_type=report_type,
                date_from=date_from,
                date_to=date_to,
                output_path=output_path,
                customer_id=customer_id,
                vehicle_id=vehicle_id
            )

            self.last_report_path = output_path
            self.send_email_button.setEnabled(True)

            QMessageBox.information(
                self,
                "Export completed",
                f"Отчет успешно сохранен:\n{output_path}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Export error",
                str(error)
            )

        finally:
            self.generate_button.setEnabled(True)

    def send_report_email(self):
        recipient = self.recipient_input.text().strip()
        if not recipient:
            QMessageBox.warning(
                self,
                "Missing recipient",
                "Введите адрес получателя."
            )
            return

        if not self.last_report_path:
            QMessageBox.warning(
                self,
                "No report",
                "Сначала сформируйте отчет."
            )
            return

        settings = get_all_settings()

        try:
            sender = EmailSender(
                host=settings.get("smtp_host"),
                port=settings.get("smtp_port"),
                username=settings.get("smtp_username"),
                password=settings.get("smtp_password"),
                security=settings.get("smtp_security")
            )

            sender.send_email(
                recipient=recipient,
                subject="Отчет RPMDesk",
                body="Запрошенный отчет находится во вложении.",
                attachment_path=self.last_report_path
            )

            QMessageBox.information(
                self,
                "Email sent",
                "Отчет успешно отправлен."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Email error",
                f"Не удалось отправить отчёт:\n{error}"
            )
