"""
This module contains the main application logic for the Money Analyzer.
It sets up the application, applies the theme, and shows the main window.
"""

from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .theme_manager import ThemeManager

def run():
    """
    Initialize and run the Money Analyzer application.

    This function creates the QApplication, applies the dark theme,
    creates and shows the main window, and starts the event loop.
    """
    app = QApplication([])
    theme_manager = ThemeManager.get_instance()
    theme_manager.apply_theme(app)
    
    main_window = MainWindow()
    main_window.show()
    
    app.exec()

if __name__ == "__main__":
    run()