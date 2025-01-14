import logging
import sys

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
    logging.getLogger('PIL').setLevel(logging.WARNING)

    # Initialize the application settings with a config file
    kConfigPath = ".config/EasyAuth/config.ini"
    home_dir_str = str(Path.home())
    filepath = Path.home().joinpath(home_dir_str, kConfigPath)
    app_config = AppConfig(filepath)
    view = AppView()

    # Start the application
    view.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()

# Development Tasks
# [ ] {NameError}name 'urls' is not defined when debugging a unittest
# [ ] Explore Qt Creator for GUI builder tool for Preferences Dialog.
# [ ] Preferences dialog - changes buttons to OK, Cancel, Apply.
# [ ] Finish removing Controller.
# [ ] Develop GUI unit tests for each dialog
# [ ] Implement drag-n-drop in reorder dialog.
# [ ] Fix defect: Secretkey CD3334 bogus2 passed validation but generated ?????? Why is 'secret' invalid?
# [ ] Prevent file corruption
# [ ] Discover: Can label field in list be a link that opens the edit dialog.
# [ ] Make a Woogle sample 2FA setup web page
# [ ] Add more error handling to Backup and vault read/write
# [ ] Implement Restore
# [ ] Simplify convoluted logic in qr_hunting.
# [ ] In Entry Form fix tab order to skip (?) icons.
# [ ] Animate TOTP code being copied to clipboard https://www.pythonguis.com/tutorials/qpropertyanimation/
# [ ] Put images in resource bundles
# [ ] Where is machine ID on Windows/Mac?
# [ ] Internationalization
# [x]Tooltip for timer styling
# [x] Implement reorder
# [x] Implement Open QR code from file
# [x] Unit test Backup
