import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox, QLineEdit
from PyQt5.QtWidgets import QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon
from utils import assets_dir
import otp_funcs, logging
from account_manager import OtpRecord
from appconfig import AppConfig
from provider_search_dialog import ProviderSearchDialog

""" Utility functions shared by Add and Edit dialogs"""

def set_tab_order(dialog):
    # Set tab order for subclass fields, maintaining parent order
    # First clear any existing tab order by setting all widgets to NoFocus
    for child in dialog.findChildren(QWidget):
        child.setFocusPolicy(Qt.NoFocus)

    # Now explicitly set focus policy for just the widgets we want in our cycle
    dialog.provider_entry.setFocusPolicy(Qt.StrongFocus)
    dialog.label_entry.setFocusPolicy(Qt.StrongFocus)
    dialog.secret_entry.setFocusPolicy(Qt.StrongFocus)
    dialog.btn_Save.setFocusPolicy(Qt.StrongFocus)
    dialog.btn_Cancel.setFocusPolicy(Qt.StrongFocus)
    # Create closed tab cycle among specific widgets
    dialog.setTabOrder(dialog.provider_entry, dialog.label_entry)  # Start with parent class fields
    dialog.setTabOrder(dialog.label_entry, dialog.secret_entry)
    dialog.setTabOrder(dialog.secret_entry, dialog.btn_Save)
    dialog.setTabOrder(dialog.btn_Save, dialog.btn_Cancel)
    dialog.setTabOrder(dialog.btn_Cancel, dialog.provider_entry)  # Complete the cycle


def validate_form(dialog):
    """ Ensure all fields have values before enabling the save button."""
    # Check if all fields are filled
    all_filled = len(dialog.provider_entry.text()) > 0 and len(dialog.label_entry.text()) > 0 and len(dialog.secret_entry.text()) > 0
    dialog.btn_Save.setEnabled(all_filled)
    
def provider_lookup(dialog):
    # Create and show the search page
    search_page = ProviderSearchDialog()
    search_page.load_data()
    search_page.lower()
    # Show the dialog and get the result
    if search_page.exec_() == QDialog.Accepted:
        selected = search_page.get_selected_provider()
        dialog.provider_entry.setText(selected)
          
def save_fields(dialog):
    issuer = dialog.provider_entry.text()
    label = dialog.label_entry.text()
    secret = dialog.secret_entry.text()
    otp_record = OtpRecord(issuer, label, secret)
    # Validate secret key
    if otp_funcs.is_valid_secretkey(secret):
        if dialog.account_manager.save_new_account(otp_record):
            dialog.accept()
        else:
             QMessageBox.information(dialog,"Warning","Account with same provider and user already exists")
    else:
        QMessageBox.information(dialog,"Error",f'The secret key is invalid')

class PasswordInput(QLineEdit):
    """ A LineEdit class that adds password hiding button and behavior """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.appconfig = AppConfig()
        self.logger = logging.getLogger(__name__)

        # Create the visibility toggle button
        self.toggle_button = QPushButton(self)
        self.toggle_button.setObjectName("btn_ShowHide")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(20, 20)
        self.toggle_button.setIconSize(self.toggle_button.size())
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        # Position the button inside the QLineEdit
        self.toggle_button.move(self.width() - self.toggle_button.width() - 2, (self.height() - self.toggle_button.height()) // 2)
        # Set click action to toggle from hidden to shown
        self.toggle_button.clicked.connect(self.toggle_visibility)
        # NB: Toggle button initial state: isChecked = False
        # Set default visibility (client may set after initialization)
        self.set_hidden(is_hidden=False)


    def resizeEvent(self, event):
        """Ensure the toggle button stays positioned inside the QLineEdit when resized."""
        super().resizeEvent(event)
        self.toggle_button.move(self.width() - self.toggle_button.width() - 2, (self.height() - self.toggle_button.height()) // 2)

    def toggle_visibility(self):
        """Toggle between showing and hiding the password."""
        # NB: click() is what actually changes button state
        is_hidden = self.toggle_button.isChecked()  # determine next state
        self.set_hidden(is_hidden)

    def set_hidden(self, is_hidden):
        #If we are called directly we make button state match
        # When called by toggle it has no effect
        self.toggle_button.setChecked(is_hidden)
        """Set password visibility based on the button state."""
        self.setEchoMode(QLineEdit.Password if is_hidden else QLineEdit.Normal)
        """Update the button icon based on the button state."""
        visibility_string = "show" if is_hidden else "hide"
        theme_name = self.appconfig.get_theme_name()
        assets_path = assets_dir().replace("\\",'/') # make proper separator for qstylesheet
        self.icon_path = f"{assets_path}/{visibility_string}_icon_{theme_name}.png"
        self.logger.debug (f"icon_path: {self.icon_path}")
        self.toggle_button.setStyleSheet(f"border: none; background: transparent; qproperty-icon: url({self.icon_path});")