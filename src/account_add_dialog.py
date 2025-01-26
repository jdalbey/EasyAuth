import logging

import pyotp
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QSizePolicy, \
    QApplication, QFileDialog, QFrame, QWidget, QGridLayout

import find_qr_codes
from QRselectionDialog import QRselectionDialog
from account_confirm_dialog import ConfirmAccountDialog
from appconfig import AppConfig
from account_manager import Account, AccountManager, OtpRecord
from otp_funcs import is_valid_secretkey
#from qr_hunting import process_qr_codes
from account_entry_dialog import AccountEntryDialog

class AddAccountDialog(AccountEntryDialog):
    def __init__(self, parent=None, ):
        super(AddAccountDialog, self).__init__(parent)
        self.account_manager = AccountManager()
        self.app_config = AppConfig() # Get the global AppConfig instance
        self.setWindowTitle("Add Account")
        self.setGeometry(100, 100, 400, 300)
        self.logger = logging.getLogger(__name__)
        self.create_form()

    def create_form(self):
        # Frame for the dialog features
        directions_frame = QFrame()
        directions_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout = QGridLayout(directions_frame)
        self.layout.setVerticalSpacing(15)

        header_label = QLabel("Choose how to create a new account:")
        self.layout.addWidget(header_label, 0,0,1,2)
        # choices section

        self.find_qr_btn = QPushButton("Use QR code")
        self.find_qr_btn.setShortcut('Ctrl+U')
        self.find_qr_btn.clicked.connect(lambda: self.get_qr_code())
        self.find_qr_btn.setContentsMargins(40, 0, 0, 0)
        self.find_qr_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(self.find_qr_btn, 1,0, alignment=Qt.AlignRight)
        qr_screen_label = QLabel("Automatically obtain the data from a QR code on the screen.")
        qr_screen_label.setContentsMargins(5, 0, 0, 0)
        self.layout.addWidget(qr_screen_label,1,1, alignment=Qt.AlignLeft)

        open_file_btn = QPushButton("Open QR image")
        open_file_btn.clicked.connect(self.open_qr_image)
        open_file_btn.setContentsMargins(40, 0, 0, 0)
        open_file_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(open_file_btn, 2,0)
        qr_file_label = QLabel("Automatically obtain the data from a QR image in a file.")  # •
        qr_file_label.setContentsMargins(5, 0, 0, 0)
        self.layout.addWidget(qr_file_label, 2,1)

        ellipsis_label = QLabel("...")
        ellipsis_label.setFont(QFont('monospaced',16))
        ellipsis_label.setContentsMargins(40, 0, 0, 10)
        self.layout.addWidget(ellipsis_label,3,0, alignment=Qt.AlignRight)

        manual_label = QLabel("Manually enter the data in the following fields.")
        """Enter the data manually"""
        manual_label.setContentsMargins(5, 0, 0, 0)
        self.layout.addWidget(manual_label,3,1)

        self.form_layout.addWidget(directions_frame, 0,0,1,3 )

        # Declare the button frame
        button_frame = QFrame()
        button_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button_layout = QHBoxLayout(button_frame)

        # Declare the save button here so we can pass it to the Form
        self.button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.save_button.clicked.connect(self.save_fields)
        self.save_button.setEnabled(False)

        # Add the save button to the layout here
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        #self.layout.addLayout(self.button_layout)
        self.form_layout.addWidget(button_frame, 4, 1)
        #self.setLayout(self.layout)

        # Set tab order for subclass fields, maintaining parent order
        # First clear any existing tab order by setting all widgets to NoFocus
        for child in self.findChildren(QWidget):
            child.setFocusPolicy(Qt.NoFocus)

        # Now explicitly set focus policy for just the widgets we want in our cycle
        self.provider_entry.setFocusPolicy(Qt.StrongFocus)
        self.label_entry.setFocusPolicy(Qt.StrongFocus)
        self.secret_entry.setFocusPolicy(Qt.StrongFocus)
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.cancel_button.setFocusPolicy(Qt.StrongFocus)
        # Create closed tab cycle among specific widgets
        self.setTabOrder(self.provider_entry, self.label_entry)  # Start with parent class fields
        self.setTabOrder(self.label_entry, self.secret_entry)
        self.setTabOrder(self.secret_entry, self.save_button)
        self.setTabOrder(self.save_button, self.cancel_button)
        self.setTabOrder(self.cancel_button, self.provider_entry)  # Complete the cycle

    def validate_form(self):
        """ Ensure all fields have values before enabling the save button."""
        # Check if all fields are filled
        all_filled = len(self.provider_entry.text()) > 0 and len(self.label_entry.text()) > 0 and len(self.secret_entry.text()) > 0
        self.save_button.setEnabled(all_filled)


    # Set values into fields (used by auto qr code scanning)
    def set_account(self, account):
        self.set_fields(account)

    def get_qr_code(self):
        """ User clicked User QR code """
        result_code = AddAccountDialog.process_qr_codes(True)  # True = called from Use QR code
        self.logger.debug(f"Finishing get_qr_code with result {result_code}")
        if result_code:
            self.accept()

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
                # copy the retrieved attributes into the shared_fields
                self.provider_entry.setText(totp_obj.issuer)
                self.label_entry.setText(totp_obj.name)
                self.secret_entry.setText(totp_obj.secret)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read QR image: {e}")

    @staticmethod
    def confirm_account(account):
        # check selection has valid secret key.
        logging.debug(f"Checking validity of code for {account.issuer}: {account.secret}")
        if not is_valid_secretkey(account.secret):
            logging.debug ("QR code invalid key")
            # if not valid secret key show message box then return to blank account_add form.
            reply = QMessageBox.information (None, 'Info', "QR code has invalid secret key.",QMessageBox.Ok)
        else:
            # if valid key place the fields from that account into the Confirm dialog form field.
            fields = OtpRecord(account.issuer, account.label, account.secret)
            current_dialog = ConfirmAccountDialog()
            current_dialog.set_account(fields)
            if current_dialog.exec_() == QDialog.Accepted:
                logging.debug (f"Confirm dialog was accepted.")
                #accept() # for case where we were called from Find QR button
                return True
        return False

    @staticmethod
    def process_qr_codes(called_from_Find_btn):
        # first go find_qr_codes
        urls = find_qr_codes.scan_screen_for_qr_codes()
        logging.debug (f"Process got urls: {urls}")
        # Examine each url to see if it is an otpauth protocol and reject others
        otpauth_list = [item for item in urls if item.startswith('otpauth://totp')]
        # Try to parse each url.  Put the fields into an account and append to displaylist.
        display_list = []
        for uri in otpauth_list:
            try:
                totp_obj = pyotp.parse_uri(uri)
            except ValueError as e:
                continue  # skip invalid URI's
            issuer = totp_obj.issuer
            name = totp_obj.name
            secret_key = totp_obj.secret
            account = OtpRecord(issuer,name,secret_key)
            # TODO: Extract the advanced parameters if they exists
            logging.debug(f"In AddDialog: Scanned QR code: {issuer} {name} ")
            display_list.append(account)
        # How many valid URI's do we have?
        if len(display_list) == 0:
            # This should only be shown during a requested find, not an automatic one.
            if called_from_Find_btn:  # we might have got here from Find button even though auto_hunt was on and failed.
                QMessageBox.information(None, 'Alert',
    """No QR code found.  Be sure the QR code is visible on your screen and try again.
    (The provider will show a QR code in your web browser during enabling of two-factor authentication.)
    """ , QMessageBox.Ok)
                return False # no QR
        if len(display_list) == 1:
            confirm_code = AddAccountDialog.confirm_account(display_list[0])
            logging.debug (f"Found 1 QR code and confirm dialog returned {confirm_code}")
            return confirm_code # True if accepted, False if declined
        # Wow, we got more than one QR code
        if len(display_list) > 1:
            # Ask user to select one account from the list
            dialog = QRselectionDialog(display_list, None)
            # The dialog.exec_() call will block execution until the dialog is closed
            if dialog.exec_() == QDialog.Accepted:
                selected_account = dialog.get_selected_account()
                # If user made a selection,
                if selected_account:
                    logging.debug(f"Selected Account: {selected_account.issuer} - {selected_account.label}")
                    return AddAccountDialog.confirm_account(selected_account)

        return False



# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app_config = AppConfig()
    dialog = AddAccountDialog(None)
    dialog.exec()
