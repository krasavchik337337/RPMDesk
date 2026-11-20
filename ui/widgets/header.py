from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel


class Header(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)

        self.title = QLabel("Dashboard")
        self.title.setObjectName("page_title")

        layout.addWidget(self.title)
        layout.addStretch()

    def set_title(self, title):
        self.title.setText(title)
