import pyotp
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QSizePolicy, \
    QApplication, QFileDialog

from account_confirm_dialog import ConfirmAccountDialog
from account_entry_form import AccountEntryForm
from appconfig import AppConfig
from models_singleton import Account, AccountManager
from otp_funcs import is_valid_secretkey
from qr_hunting import process_qr_codes

class AddAccountDialog(QDialog):
    def __init__(self, parent=None, ):
        super(AddAccountDialog, self).__init__(parent)
        self.account_manager = AccountManager()
        self.app_config = AppConfig() # Get the global AppConfig instance
        self.setWindowTitle("Add Account")
        self.setGeometry(100, 100, 400, 300)
        self.create_form()

    def create_form(self):
        self.layout = QVBoxLayout()
        header_label = QLabel("Choose how to create your new account:")
        self.layout.addWidget(header_label)
        # choices section
        qr_screen_label = QLabel("• Fill the form automatically from a QR code on the screen")
        qr_screen_label.setContentsMargins(20, 0, 0, 0)
        self.layout.addWidget(qr_screen_label)

        self.find_qr_btn = QPushButton("Use QR code")
        self.find_qr_btn.setShortcut('Ctrl+U')
        self.find_qr_btn.clicked.connect(lambda: self.get_qr_code())
        self.find_qr_btn.setContentsMargins(40, 0, 0, 0)
        self.find_qr_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(self.find_qr_btn, alignment=Qt.AlignCenter)

        qr_file_label = QLabel("• Fill the form automatically from a QR image in a file")
        qr_file_label.setContentsMargins(20, 0, 0, 0)
        self.layout.addWidget(qr_file_label)

        open_file_btn = QPushButton("Open file")
        open_file_btn.clicked.connect(self.open_qr_image)
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
        provider = self.shared_fields.provider_entry.text()
        label = self.shared_fields.label_entry.text()
        secret = self.shared_fields.secret_entry.text()
        # Validate secret key
        if is_valid_secretkey(secret):
            self.account_manager.save_new_account(provider, label, secret)
            self.accept()
        else:
            reply = QMessageBox.information(self,"Error",f'The secret key is invalid')

    # Set values into fields (used by auto qr code scanning)
    def set_account(self, account):
        self.shared_fields.set_fields(account)

    def get_qr_code(self):
        """ User clicked User QR code """
        confirmDialog = ConfirmAccountDialog()
        result_code = process_qr_codes(True, confirmDialog)  # True = called from Use QR code
        print (f"Finishing get_qr_code with result {result_code}")
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
                self.shared_fields.provider_entry.setText(totp_obj.issuer)
                self.shared_fields.label_entry.setText(totp_obj.name)
                self.shared_fields.secret_entry.setText(totp_obj.secret)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read QR image: {e}")

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
#     dlg = AddAccountDialog(ctrl,None)
#     sys.exit()

