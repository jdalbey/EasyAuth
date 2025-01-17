import sys, logging
from PyQt5.QtWidgets import QApplication
from appconfig import AppConfig
from view import AppView
from pathlib import Path # Python 3.5+

# Global variable to store the application configuration
app_config = None

def main():
    app = QApplication(sys.argv)
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Suppress log messages from the tkinter module
    #logging.getLogger('PIL').setLevel(logging.WARNING)

    # Initialize the application settings with a config file
    kConfigPath = ".config/EasyAuth/config.ini"
    home_dir_str = str(Path.home())
    filepath = Path.home().joinpath(home_dir_str, kConfigPath)
    AppConfig(filepath)
    view = AppView()

    # Start the application
    view.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()

