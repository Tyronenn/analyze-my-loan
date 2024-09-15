from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class ThemeManager:
    _instance = None

    @staticmethod
    def get_instance():
        if ThemeManager._instance is None:
            ThemeManager()
        return ThemeManager._instance

    def __init__(self):
        if ThemeManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ThemeManager._instance = self
        
        self.dark_palette = self.create_dark_palette()
        self.style_sheet = self.create_style_sheet()

    def create_dark_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        return palette

    def create_style_sheet(self):
        return """
        QToolTip { 
            color: #ffffff; 
            background-color: #2a82da; 
            border: 1px solid white; 
        }

        QWidget {
            background-color: #353535;
            color: #ffffff;
        }

        QPlainTextEdit, QTextEdit {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #5a5a5a;
        }

        QPushButton {
            background-color: #5a5a5a;
            color: #ffffff;
            border: 1px solid #7a7a7a;
            padding: 5px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #7a7a7a;
        }

        QPushButton:pressed {
            background-color: #3a3a3a;
        }

        QLineEdit {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 3px;
            border-radius: 3px;
        }

        QTabWidget::pane {
            border: 1px solid #5a5a5a;
        }

        QTabBar::tab {
            background-color: #2a2a2a;
            color: #ffffff;
            padding: 5px;
            border: 1px solid #5a5a5a;
        }

        QTabBar::tab:selected {
            background-color: #3a3a3a;
        }

        QTableWidget {
            background-color: #1e1e1e;
            color: #ffffff;
            gridline-color: #5a5a5a;
        }

        QHeaderView::section {
            background-color: #2a2a2a;
            color: #ffffff;
            padding: 5px;
            border: 1px solid #5a5a5a;
        }

        QScrollBar:vertical, QScrollBar:horizontal {
            border: 1px solid #5a5a5a;
            background: #1e1e1e;
            width: 15px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #5a5a5a;
            min-height: 20px;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: 1px solid #5a5a5a;
            background: #5a5a5a;
            height: 15px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        """

    def apply_theme(self, app: QApplication):
        app.setPalette(self.dark_palette)
        app.setStyleSheet(self.style_sheet)
