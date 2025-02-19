import logging
import os

import pyotp
import qdarktheme
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QLabel, QMessageBox, QApplication, QFileDialog, QCompleter
# from account_entry_panel import AccountEntryPanel
from PyQt5.uic import loadUi

import qr_funcs
from account_mgr import AccountManager, OtpRecord
from appconfig import AppConfig
from common_dialog_funcs import set_tab_order, validate_form, provider_lookup, save_fields
from provider_map import Providers
from qr_selection_dialog import QRselectionDialog
from utils import assets_dir

class VaultEntryDialog(QDialog):
    """ Dialog to create a new vault entry """
    def __init__(self, parent ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.account_manager = AccountManager()
        self.appconfig = AppConfig() # Get the global AppConfig instance
        # initialize provider lookup
        self.providers = Providers()
        self.provider_names = self.providers.provider_map.keys()
        self.setWindowFlags(Qt.WindowTitleHint | Qt.Dialog | Qt.WindowCloseButtonHint) # x-platform consistency
        self.setMinimumSize(380, 280)

        try:
            filepath = os.path.join(assets_dir(), "VaultDetails.ui")
            loadUi(filepath, self)
            self.logger.debug("NewVaultEntry.ui loaded.")
        except FileNotFoundError as e:
            self.logger.error("NewVaultEntry.ui not found, can't display dialog.")
            QMessageBox.critical(self, "Error", f"Failed to load UI: {e}")
            raise RuntimeError("Failed to load UI")  # Prevents dialog from appearing

        self.setWindowTitle("Add Vault Entry")
        self.resize(self.width(), self.minimumHeight())

        # Show default globe icon
        self.use_default_icon()

        # Setup auto-complete for provider field
        self.completer = QCompleter(self.provider_names)
        self.completer.setCaseSensitivity(False)  # Makes it case-insensitive
        self.completer.setFilterMode(Qt.MatchContains)  # Allows substring matching
        self.provider_entry.setCompleter(self.completer)
        # Connect activated signal to update icon_name when a match is selected
        # Ensures that when the user picks a provider, the first letter is copied to icon_name.
        # Will call update_icon_name with the string from activated()
        #self.completer.activated[str].connect(self.update_icon_name)
        # Connect text changed signal to monitor matches dynamically
        # If only one match remains, it preemptively updates icon_name without requiring user selection.
        #self.provider_entry.textEdited.connect(self.check_single_match)
        # Connect editingFinished signal
        self.provider_entry.editingFinished.connect(self.on_provider_entry_editting_finished)

        # Set initial buttons state
        self.btn_Edit.hide()
        self.btn_Delete.hide()
        self.btn_Cancel.setEnabled(True)

        # Setup actions to be taken
        self.label_LearnMore.setOpenExternalLinks(True)# Make the link clickable
        self.btn_Save.clicked.connect(lambda: save_fields(self))
        self.btn_Cancel.clicked.connect(self.reject)
        self.provider_entry.textChanged.connect(lambda: validate_form(self))
        self.label_entry.textChanged.connect(lambda: validate_form(self))
        self.secret_entry.textChanged.connect(lambda: validate_form(self))
        # Hide secret according to  preference
        self.secret_entry.set_hidden(self.appconfig.is_secret_key_hidden())

        set_tab_order(self)

    def use_default_icon(self):
        """ Set icon to a default image (used when provider name not found) """
        pixmap = QPixmap(os.path.join(assets_dir(),"globe_icon.png"))
        self.icon_label.setPixmap(pixmap)

    def on_provider_entry_editting_finished(self):
        """ Check if only one match remains and update icon_name. """
        match_list = [name for name in self.provider_names if self.provider_entry.text().lower() in name.lower()]
        if len(match_list) == 1:
            pixmap = self.providers.get_provider_icon_pixmap(match_list[0])
            self.icon_label.setPixmap(pixmap)
            self.provider_entry.setText(match_list[0])
        else:
            # Use default icon if provider name not found
            self.use_default_icon()


# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    from styles import light_qss
    qdarktheme.setup_theme("light", additional_qss=light_qss)
    appconfig = AppConfig()
    dialog = VaultEntryDialog(None)
    dialog.exec()
