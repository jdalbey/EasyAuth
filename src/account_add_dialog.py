import logging
import time

import pyotp
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QSizePolicy, \
    QApplication, QFileDialog, QFrame, QWidget, QGridLayout

import find_qr_codes
from QRselectionDialog import QRselectionDialog
from appconfig import AppConfig
from account_manager import Account, AccountManager, OtpRecord
from account_entry_dialog import AccountEntryDialog

class AddAccountDialog(AccountEntryDialog):
    """ Dialog to create a new account """
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

    def get_qr_code(self):
        """ User clicked User QR code """
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
                # self.provider_entry.setText(totp_obj.issuer)
                # self.label_entry.setText(totp_obj.name)
                # self.secret_entry.setText(totp_obj.secret)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read QR image: {e}")

    def _type_field_fill(self, field, value):
        field.setText("")
        for letter in value:
            current = field.text() + letter
            field.setText(current)
            QApplication.processEvents()  # Allow UI to update
            QThread.msleep(30)  # Non-CPU blocking sleep

    def fill_form_fields(self, account):
        # check selection has valid secret key.
        # I think we can omit this ... assuming that QR codes always have valid secret keys.
        # if not is_valid_secretkey(account.secret):
        #     logging.debug ("QR code invalid key")
        #     # if not valid secret key show message box then return to blank account_add form.
        #     reply = QMessageBox.information (None, 'Info', "QR code has invalid secret key.",QMessageBox.Ok)
        # else:
        # Show a floating message relative to the form fields
        popup = QLabel("QR code found!", self)
        popup.setObjectName("qr_code_found")
        popup.setAlignment(Qt.AlignCenter)
        popup.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        popup.setStyleSheet("QLabel#qr_code_found {font-size:16px; background-color: #dff0d8; color: #3c763d; padding: 5px; border: 1px solid #d6e9c6;}")
        popup.resize(150, 50)
        # Calculate position just above the field
        button_geometry = self.provider_entry.parent().mapToGlobal(self.provider_entry.geometry().topLeft())
        button_center_x = button_geometry.x() + self.provider_entry.width() // 2
        popup_x = button_center_x - popup.width() // 2
        popup_y = button_geometry.y() - popup.height() - 5  # 5 pixels gap above the button

        popup.move(popup_x, popup_y)
        popup.show()
        QTimer.singleShot(3000, popup.close)  # Hide after 3 seconds

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
                selected_account = dialog.get_selected_account()
                # If user made a selection,
                if selected_account:
                    logging.debug(f"QRselectionDialog returned: {selected_account.issuer} - {selected_account.label}")
                    self.fill_form_fields(selected_account)





# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app_config = AppConfig()
    dialog = AddAccountDialog(None)
    dialog.exec()
