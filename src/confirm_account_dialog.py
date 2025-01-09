from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from account_entry_fields import AccountEntryFields

class ConfirmAccountDialog(QDialog):
    def __init__(self, controller, parent=None):
        super(ConfirmAccountDialog, self).__init__(parent)
        self.controller = controller
        self.setWindowTitle("Confirm Account")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()

        header_label = QLabel("A QR code was found with these values:")
        self.layout.addWidget(header_label)

        # Add shared fields
        self.shared_fields = AccountEntryFields()
        self.shared_fields.add_to_layout(self.layout)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Accept")
        self.save_button.clicked.connect(self.save_fields)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Decline")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    # Set values into fields (used by auto qr code scanning)
    def set_account(self, account):
        self.shared_fields.set_fields(account)        

    def save_fields(self):
        provider = self.shared_fields.provider_entry.text()
        label = self.shared_fields.label_entry.text()
        secret = self.shared_fields.secret_entry.text()
        self.controller.save_new_account(provider, label, secret)
        self.accept()