from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys
from .ui.main_window import MainWindow

class MoneyAnalyzerApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Money Analyzer")
        self.setOrganizationName("Money Analyzer")
        self.setWindowIcon(QIcon('resources/icons/money_analyzer_icon.png'))

        self.main_window = MainWindow()
        self.main_window.show()

def run():
    app = MoneyAnalyzerApp(sys.argv)
    sys.exit(app.exec())