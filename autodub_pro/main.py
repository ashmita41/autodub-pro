import sys
from PySide6.QtWidgets import QApplication
from autodub_pro.ui.main_window import MainWindow
from autodub_pro.config import load_config


def main():
    """
    Start the AutoDub Pro application.
    """
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("AutoDub Pro")
    app.setOrganizationName("AutoDub")
    app.setOrganizationDomain("autodub.pro")
    
    # Load configuration
    config = load_config()
    
    # Create and show the main window
    window = MainWindow(config)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 