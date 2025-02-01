import os
import sys, logging
from PyQt5.QtWidgets import QApplication
from appconfig import AppConfig
from view import AppView
from pathlib import Path # Python 3.5+
import qdarktheme
def main():
    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()

    app = QApplication(sys.argv)
    # Configure logging
    """When you use basicConfig to specify the format option, it sets the format for the root logger """
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')
    logger = logging.getLogger(__name__)
    logging.getLogger('PIL').setLevel(logging.WARNING) # suppress debug messages from PIL
    logging.getLogger('PyQt5.uic.uiparser').setLevel(logging.WARNING)
    logging.getLogger('PyQt5.uic.properties').setLevel(logging.WARNING)
    logger.debug("Application starting with default config")
    appconfig = AppConfig()

    base_dir = ""
    # Are we in production mode?
    if getattr(sys, 'frozen', False):
        # PyInstaller bundled case - prefix the temp directory path
        base_dir = sys._MEIPASS  # type: ignore   #--keep PyCharm happy

    assets_dir = os.path.join(base_dir, "assets")
    # Add a setting for correct assets directory, dev or production
    appconfig.set("System", "assets_dir", assets_dir)

    # Display the main window
    view = AppView(app)
    view.show()

    # Start the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

"""    def showEvent(self, event):
        super().showEvent(event)
        # Store the initial size when the dialog is first shown
        if self.initial_size is None:
            self.initial_size = self.size()"""