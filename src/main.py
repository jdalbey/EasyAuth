import sys, logging
from PyQt5.QtWidgets import QApplication
from appconfig import AppConfig
from pathlib import Path # Python 3.5+

def main():
    app = QApplication(sys.argv)
    # Configure logging
    """When you use basicConfig to specify the format option, it sets the format for the root logger """
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')
    logger = logging.getLogger(__name__)

    logger.debug("Application starting with default config")
    logger.debug("Application starting with default config")
    from view import AppView
    view = AppView(app)

    # Start the application
    view.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()

"""    def showEvent(self, event):
        super().showEvent(event)
        # Store the initial size when the dialog is first shown
        if self.initial_size is None:
            self.initial_size = self.size()"""