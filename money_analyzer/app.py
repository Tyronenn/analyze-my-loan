from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .theme_manager import ThemeManager

def run():
    app = QApplication([])
    theme_manager = ThemeManager.get_instance()
    theme_manager.apply_theme(app)
    
    main_window = MainWindow()
    main_window.show()
    
    app.exec()

if __name__ == "__main__":
    run()