from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QButtonGroup, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from config import LOGO_PATH


class Sidebar(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.pages = [
            "Dashboard",
            "Customers",
            "Vehicles",
            "Service",
            "Inventory",
            "Reports",
            "Settings"
        ]

        self.initUI()

    def initUI(self):
        self.setFixedWidth(230)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 25, 15, 20)
        layout.setSpacing(8)

        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        logo_layout.setSpacing(10)

        logo = QLabel("RPMDesk")
        logo.setObjectName("logo")

        logo_icon = QLabel()
        logo_icon.setFixedSize(40, 40)
        icon_pixmap = QPixmap(LOGO_PATH)
        logo_icon.setPixmap(
            icon_pixmap.scaled(
                40,
                40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        logo_icon.setObjectName("logo_icon")

        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo)
        logo_layout.addStretch()

        layout.addLayout(logo_layout)

        layout.addSpacing(30)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        for index, page_name in enumerate(self.pages):
            button = QPushButton(page_name)
            button.setCheckable(True)
            button.setObjectName("nav_button")

            self.button_group.addButton(button, index)
            layout.addWidget(button)

        layout.addStretch()

        self.button_group.idClicked.connect(self.page_changed.emit)

        self.button_group.button(0).setChecked(True)
