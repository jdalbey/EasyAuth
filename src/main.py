import sys, logging
from PyQt5.QtWidgets import QApplication
from appconfig import AppConfig
from handle_args import handle_args
from view import AppView

import qdarktheme
def main():
    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()

    # Declare a PyQt application
    app = QApplication(sys.argv)

    # Configure logging
    """When you use basicConfig to specify the format option, it sets the format for the root logger """
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')
    logger = logging.getLogger(__name__)
    logging.getLogger('PIL').setLevel(logging.WARNING) # suppress debug messages from PIL
    logging.getLogger('PyQt5.uic.uiparser').setLevel(logging.WARNING)
    logging.getLogger('PyQt5.uic.properties').setLevel(logging.WARNING)
    logger.debug("Application starting with default config")
    # Initialize settings
    appconfig = AppConfig()
    # Read the desired logging level from settings
    logging.getLogger().setLevel(int(appconfig.get_log_level()))

    # Display the main window
    view = AppView(app)
    view.show()

    # Start the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    handle_args()
    main()
