import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from database.initialization import initialize_database

if __name__ == "__main__":
    initialize_database()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
