import pyotp
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QSizePolicy, \
    QApplication

from QRselectionDialog import QRselectionDialog
from account_confirm_dialog import ConfirmAccountDialog
from account_entry_form import AccountEntryForm
from appconfig import AppConfig
from controllers import AppController
from models import Account
from otp_manager import is_valid_secretkey
from pathlib import Path # Python 3.5+

class AddDialog(QDialog):
    def __init__(self, controller, parent=None):
        super(AddDialog, self).__init__(parent)
        self.controller = controller
        self.app_config = AppConfig() # Get the global AppConfig instance
        self.setWindowTitle("Add Account")
        self.setGeometry(100, 100, 400, 300)
        self.create_form()
        # DEFECT.  IF auto-find is on but no QR code is present the app hangs w/o showing Add Dialog
        if self.app_config.is_auto_find_qr_enabled():
            print ("starting with auto_hint")
            if self.process(False):
                # We haven't opened the dialog yet but got a confirmed code so we can just bail out.
                return
            print ("Didn't get a QR code, showing dialog next.")
        # Either we didn't find any qr codes or auto_find is turned off
        self.exec_()

    def confirm_account(self,account):
        # check selection has valid secret key.
        print(f"Checking validity of code for {account.provider}: {account.secret}")
        if not is_valid_secretkey(account.secret):
            # if not valid secret key show message box then return to blank account_add form.
            reply = QMessageBox.information (None, 'Info', "QR code has invalid secret key.",QMessageBox.Ok)
        else:
            # if valid key place the fields from that account into the Confirm dialog form field.
            fields = Account(account.provider, account.label, account.secret, "")
            self.current_dialog = ConfirmAccountDialog(self.controller)
            self.current_dialog.set_account(fields)
            if self.current_dialog.exec_() == QDialog.Accepted:
                print (f"Confirm dialog was accepted.")
                self.accept() # for case where we were called from Find QR button
                return True
        return False


    def process(self,called_from_Find_btn):
        # Before showing form go find_qr_code
        urls = self.controller.find_qr_codes()
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
            account = Account(issuer,name,secret_key,"")
            # TODO: Extract the time period parameter if it exists
            print(f"In AddDialog: Scanned QR code: {issuer} {name} ")
            display_list.append(account)
        # How many valid URI's do we have?
        if len(display_list) == 0:
            # This should only be shown during a requested find, not an automatic one.
            if called_from_Find_btn:  # we might have got here from Find button even though auto_hunt was on and failed.
                QMessageBox.information(None, 'Info', "No QR code found.  Be sure the QR code is visible on your screen.", QMessageBox.Ok)
                return False # no QR
        if len(display_list) == 1:
            return self.confirm_account(display_list[0])
        # Wow, we got more than one QR code
        if len(display_list) > 1:
            # Ask user to select one account from the list
            dialog = QRselectionDialog(display_list, self)
            # The dialog.exec_() call will block execution until the dialog is closed
            if dialog.exec_() == QDialog.Accepted:
                selected_account = dialog.get_selected_account()
                # If user made a selection,
                if selected_account:
                    print(f"Selected Account: {selected_account.provider} - {selected_account.label}")
                    return self.confirm_account(selected_account)

        return False


    def create_form(self):
        self.layout = QVBoxLayout()
        header_label = QLabel("Choose how to create your new account:")
        self.layout.addWidget(header_label)
        # choices section
        qr_screen_label = QLabel("• Fill the form automatically from a QR code on the screen")
        qr_screen_label.setContentsMargins(20, 0, 0, 0)
        self.layout.addWidget(qr_screen_label)

        find_qr_btn = QPushButton("Find QR code")
        find_qr_btn.clicked.connect(lambda: self.get_qr_code())
        find_qr_btn.setContentsMargins(40, 0, 0, 0)
        find_qr_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(find_qr_btn, alignment=Qt.AlignCenter)

        qr_file_label = QLabel("• Fill the form automatically from a QR image in a file")
        qr_file_label.setContentsMargins(20, 0, 0, 0)
        self.layout.addWidget(qr_file_label)

        open_file_btn = QPushButton("Open file")
        #open_file_btn.clicked.connect(self.controller.open_qr_image)
        open_file_btn.setContentsMargins(40, 0, 0, 0)
        open_file_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(open_file_btn, alignment=Qt.AlignCenter)

        manual_label = QLabel("• Enter the data manually")
        manual_label.setContentsMargins(20, 0, 0, 0)
        self.layout.addWidget(manual_label)

        # Declare the save button here so we can pass it to the Form
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_fields)
        self.save_button.setEnabled(False)

        # Add shared fields
        self.shared_fields = AccountEntryForm(self.save_button)
        self.layout.addWidget(self.shared_fields)

        # Add the save button to the layout here
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)


    def save_fields(self):
        # TODO: Don't allow save until all fields have a value
        provider = self.shared_fields.provider_entry.text()
        label = self.shared_fields.label_entry.text()
        secret = self.shared_fields.secret_entry.text()
        # Validate secret key
        if is_valid_secretkey(secret):
            self.controller.save_new_account(provider, label, secret)
            self.accept()
        else:
            reply = QMessageBox.information(self,"Error",
f'The secret key is invalid')

    # Set values into fields (used by auto qr code scanning)
    def set_account(self, account):
        self.shared_fields.set_fields(account)

    def get_qr_code(self):
        self.process(True)
        print ("Finishing get_qr_code, back to Add Dialog")
        # provider, label, secret = self.controller.find_qr_codes()
        # fields = Account(provider, label, secret, "")
        # self.shared_fields.set_fields(fields)

# local main for unit testing
# if __name__ == '__main__':
#     import sys
#     # Initialize the application settings with a config file
#     kConfigPath = ".config/EasyAuth/config.ini"
#     home_dir_str = str(Path.home())
#     filepath = Path.home().joinpath(home_dir_str, kConfigPath)
#
#     app = QApplication(sys.argv)
#     app_config = AppConfig(filepath)
#     ctrl = AppController()
#     dlg = AddDialog(ctrl,None)
#     sys.exit()

