from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from account_entry_fields import AccountEntryFields
from models import Account

class AddAccountDlg(QDialog):
    def __init__(self, controller, parent=None):
        super(AddAccountDlg, self).__init__(parent)
        self.controller = controller
        self.setWindowTitle("Add Account")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        header_label = QLabel("Choose how to create your new account:")
        self.layout.addWidget(header_label)
        # choices section
        qr_screen_label = QLabel("• Fill the form automatically from a QR code on the screen")
        qr_screen_label.setContentsMargins(20, 0, 0, 0)
        self.layout.addWidget(qr_screen_label)

        find_qr_btn = QPushButton("Find QR code")
        #find_qr_btn.clicked.connect(self.controller.find_qr_code)
        find_qr_btn.clicked.connect(lambda: self.get_qr_code())
        find_qr_btn.setContentsMargins(40, 0, 0, 0)
        self.layout.addWidget(find_qr_btn)

        qr_file_label = QLabel("• Fill the form automatically from a QR image in a file")
        qr_file_label.setContentsMargins(20, 0, 0, 0)
        self.layout.addWidget(qr_file_label)

        open_file_btn = QPushButton("Open file")
        open_file_btn.clicked.connect(self.controller.open_qr_image)
        open_file_btn.setContentsMargins(40, 0, 0, 0)
        self.layout.addWidget(open_file_btn)

        manual_label = QLabel("• Enter the data manually")
        manual_label.setContentsMargins(20, 0, 0, 0)
        self.layout.addWidget(manual_label)

        # Add shared fields
        self.shared_fields = AccountEntryFields()
        self.shared_fields.add_to_layout(self.layout)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_fields)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    # def set_provider(self, provider):
    #     self.provider_entry.setText(provider)

    # def set_label(self, label):
    #     self.label_entry.setText(label)

    # def set_secret(self, secret):
    #     self.secret_entry.setText(secret)

    def save_fields(self):
        provider = self.shared_fields.provider_entry.text()
        label = self.shared_fields.label_entry.text()
        secret = self.shared_fields.secret_entry.text()
        self.controller.save_account(provider, label, secret)
        self.accept()

    # Set values into fields (used by auto qr code scanning)
    def set_account(self, account):
        self.shared_fields.set_fields(account)

    def get_qr_code(self):
        provider, label, secret = self.controller.find_qr_code()
        fields = Account(provider, label, secret)
        self.shared_fields.set_fields(fields)
