from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox

import otp_funcs
from account_manager import OtpRecord
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
