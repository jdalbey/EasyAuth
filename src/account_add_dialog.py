import logging
import os
import time

import pyotp
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QSizePolicy, \
    QApplication, QFileDialog, QFrame, QWidget, QGridLayout, QLayout

import find_qr_codes
import otp_funcs
from common_dialog_funcs import set_tab_order, validate_form, provider_lookup, save_fields
from qr_selection_dialog import QRselectionDialog
from appconfig import AppConfig
from account_manager import Account, AccountManager, OtpRecord
#from account_entry_panel import AccountEntryPanel
from PyQt5.uic import loadUi

from provider_search_dialog import ProviderSearchDialog


class AddAccountDialog(QDialog):
    """ Dialog to create a new account """
    def __init__(self, parent ):
        #super(AddAccountDialog, self).__init__(parent)
        super().__init__(parent)
        self.account_manager = AccountManager()
        self.app_config = AppConfig() # Get the global AppConfig instance
        self.logger = logging.getLogger(__name__)

        self.setMinimumSize(600, 450)

        try:
            loadUi("assets/AddAccountForm.ui", self)
        except FileNotFoundError as e:
            self.logger.error("AddAccountForm.ui not found, can't display dialog.")
            QMessageBox.critical(self, "Error", f"Failed to load UI: {e}")
            raise RuntimeError("Failed to load UI")  # Prevents dialog from appearing
        self.setWindowTitle("Add Account")

        # Setup actions to be taken
        self.label_LearnMore.setOpenExternalLinks(True)# Make the link clickable
        self.btn_scanQR.clicked.connect(lambda: self.scan_qr_code())
        self.btn_Lookup.clicked.connect(lambda: provider_lookup(self))
        self.btn_Save.clicked.connect(lambda: save_fields(self))
        self.btn_Cancel.clicked.connect(self.reject)
        self.provider_entry.textChanged.connect(lambda: validate_form(self))
        self.label_entry.textChanged.connect(lambda: validate_form(self))
        self.secret_entry.textChanged.connect(lambda: validate_form(self))
        set_tab_order(self)


    def scan_qr_code(self):
        """ User clicked: Scan QR code """
        """ Determine source for scan: screen or file """
        if self.radioBtnScreen.isChecked():
            self.get_qr_code()
        else:
            self.open_qr_image()

    def get_qr_code(self):
        """ Get QR code from screen """
        self.obtain_qr_codes(True)  # True = called from Use QR code
        self.logger.debug(f"Exiting get_qr_code()")

    def open_qr_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, f"Open QR image", "",
                                                   "PNG Files (*.png);;All Files (*)", options=options)
        if file_path:
            try:
                from pyzbar.pyzbar import decode
                from PIL import Image
                # Read image file
                qr_image = Image.open(file_path)
                # decode QR codes
                qr_codes = decode(qr_image)
                # Extract data from the detected QR codes
                results = [qr_code.data.decode('utf-8') for qr_code in qr_codes if qr_code.data]
                if len(results) == 0:
                    QMessageBox.critical(self, "Error", f"QR image not recognized.")
                    return
                # results is a list
                if len(results) > 1:
                    QMessageBox.critical(self, "Operation failed", f"The image contained multiple QR codes.\n " +
                                         "The program is currently unable to process more than one QR code per image.")
                    return
                # Parse the URI
                try:
                    totp_obj = pyotp.parse_uri(results[0])
                except ValueError as e:
                    QMessageBox.critical(self, "Error", f"QR code invalid {e}")
                    return
                # copy the retrieved attributes into the form fields
                otp_record = OtpRecord(totp_obj.issuer, totp_obj.name, totp_obj.secret)
                self.fill_form_fields(otp_record)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read QR image: {e}")

    def _type_field_fill(self, field, value):
        field.setText("")
        for letter in value:
            current = field.text() + letter
            field.setText(current)
            QApplication.processEvents()  # Allow UI to update
            QThread.msleep(30)  # Non-CPU blocking sleep

    def show_popup(self):
        # Show a floating message relative to the form fields
        popup = QLabel("QR code found!", self)
        popup.setObjectName("qr_code_found")
        popup.setAlignment(Qt.AlignCenter)
        popup.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        popup.setStyleSheet("QLabel#qr_code_found {font-size:16px; background-color: #dff0d8; color: #3c763d; padding: 5px; border: 1px solid #d6e9c6;}")
        popup.resize(150, 50)
        # Calculate position just above the field

        #button_geometry = self.entry_panel.mapToGlobal(self.entry_panel.provider_entry.geometry().topLeft())
        button_geometry = self.provider_entry.parent().mapToGlobal(self.provider_entry.geometry().topLeft())
        button_center_x = button_geometry.x() + self.provider_entry.width() // 2
        popup_x = button_center_x - popup.width() // 2
        popup_y = button_geometry.y() - popup.height() - 5  # 5 pixels gap above the button

        popup.move(popup_x, popup_y)
        popup.show()
        QTimer.singleShot(3000, popup.close)  # Hide after 3 seconds

    def fill_form_fields(self, account):
        self.show_popup()
        # Clear the form fields
        self.provider_entry.setText("")
        self.label_entry.setText("")
        self.secret_entry.setText("")
        # copy the retrieved attributes into the form fields (animate if preferences allow)
        if self.app_config.is_animate_form_fill():
            self._type_field_fill(self.provider_entry, account.issuer)
            self._type_field_fill(self.label_entry, account.label)
            self._type_field_fill(self.secret_entry, account.secret)
        else:
            self.provider_entry.setText(account.issuer)
            self.label_entry.setText(account.label)
            self.secret_entry.setText(account.secret)

    def obtain_qr_codes(self, called_from_Find_btn):
        # first go find_qr_codes
        urls = find_qr_codes.scan_screen_for_qr_codes()
        logging.debug (f"obtain_qr_codes() found these URIs: {urls}")
        # Examine each url to see if it is an otpauth protocol and reject others
        otpauth_list = [item for item in urls if item.startswith('otpauth://totp')]
        # Try to parse each url.  Put the fields into an OtpRecord and append to displaylist.
        display_list = []
        for uri in otpauth_list:
            try:
                totp_obj = pyotp.parse_uri(uri)
            except ValueError as e:
                continue  # skip invalid URI's
            issuer = totp_obj.issuer
            label = totp_obj.name
            secret_key = totp_obj.secret
            account = OtpRecord(issuer,label,secret_key)
            # TODO: Extract the advanced parameters if they exists
            logging.debug(f"obtain_qr_codes() parsing produced: {issuer} {label} ")
            display_list.append(account)
        # How many valid URI's do we have?
        if len(display_list) == 0:
            # This should only be shown during a requested find, not an automatic one.
            if called_from_Find_btn:  # we might have got here from Find button even though auto_hunt was on and failed.
                QMessageBox.information(self, 'Alert',
"""No QR code found.  Be sure the QR code is visible on your screen and try again.
(The provider will show a QR code in your web browser during enabling of two-factor authentication.)
""" , QMessageBox.Ok)
                return
        if len(display_list) == 1:
            self.fill_form_fields(display_list[0])
        # Wow, we got more than one QR code
        if len(display_list) > 1:
            # Ask user to select one account from the list
            dialog = QRselectionDialog(display_list, self)
            # The dialog.exec_() call will block execution until the dialog is closed
            if dialog.exec_() == QDialog.Accepted:
                self.selected_account = dialog.get_selected_account()
                # If user made a selection,
                if self.selected_account:
                    logging.debug(f"QRselectionDialog returned: {self.selected_account.issuer} - {self.selected_account.label}")
                    self.fill_form_fields(self.selected_account)




# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app_config = AppConfig()
    dialog = AddAccountDialog(None)
    dialog.exec()
