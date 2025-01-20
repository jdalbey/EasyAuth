import sys, logging
from PyQt5.QtWidgets import QApplication
from appconfig import AppConfig
from view import AppView
from pathlib import Path # Python 3.5+

def main():
    app = QApplication(sys.argv)
    # Configure logging
    """When you use basicConfig to specify the format option, it sets the format for the root logger """
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')
    logger = logging.getLogger(__name__)

    logger.debug("Application starting with default config")
    AppConfig()
    view = AppView()

    # Start the application
    view.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()

