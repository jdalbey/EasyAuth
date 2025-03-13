import os
import sys
import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap

from utils import assets_dir

def show(parent):
    """ Show About dialog, including version and build date. """
    # Find the build date
    # If production mode, use path to bundled file created during build
    if getattr(sys, 'frozen', False):
        build_date_path = os.path.join(assets_dir(), "build_date.txt")
        version_path = os.path.join(assets_dir(), "version_info.txt")
        build_date = "Unknown"
        version_number = "0.0"
        # Read the build date from assets folder
        if os.path.exists(build_date_path):
            with open(build_date_path, "r") as f:
                date_string = f.read().strip()
                # Oddly, Windows date function prepends some junk, so here we skip over it by starting at [4:]
                build_date = date_string[4:]
        # Read the version info from assets folder
        if os.path.exists(version_path):
            with open(version_path, "r") as f:
                version_number = f.read().strip()
    else:  # For development version (running unbundled)
        now = datetime.datetime.now()
        build_date = now.strftime("%Y-%m-%d %H:%M:%S")
        version_number = "0.0"

    msg = QMessageBox(parent)
    msg.setTextFormat(Qt.RichText)  # Use rich text for HTML links
    msg.setText(f'EasyAuth<br><br>\n2FA authenticator.<br><br>\n' +
                f"Version {version_number}  {build_date}<br><br>\n" +
                "<a href=\"https://jdalbey.github.io/EasyAuth/\">Website</a><br><br>\n" +
                f"Vault directory:<br>" + parent.app_config.get_os_data_dir())
    msg.setWindowTitle("About")
    # Include our application icon
    pixmap = QPixmap(os.path.join(assets_dir(), "Vault.png"))
    msg.setIconPixmap(pixmap)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()