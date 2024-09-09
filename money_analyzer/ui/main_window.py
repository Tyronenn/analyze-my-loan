from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QDockWidget
from PyQt6.QtCore import Qt
from .widgets.loan_widget import LoanWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Money Analyzer")
        self.setGeometry(100, 100, 1200, 800)

        self.setup_menu_bar()
        self.setup_dock_widgets()

    def setup_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)
        file_menu.addAction("Exit", self.close)

        tools_menu = QMenu("Tools", self)
        menu_bar.addMenu(tools_menu)
        tools_menu.addAction("Loan Analyzer", self.show_loan_analyzer)
        # Add more tools here as you implement them

    def setup_dock_widgets(self):
        self.loan_widget = LoanWidget()
        self.loan_dock = QDockWidget("Loan Analyzer", self)
        self.loan_dock.setWidget(self.loan_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.loan_dock)

    def show_loan_analyzer(self):
        self.loan_dock.show()
        self.loan_dock.raise_()