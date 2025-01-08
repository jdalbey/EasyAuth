from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit

class AccountEntryFields:
    def __init__(self):
        self.provider_label = QLabel("Provider:")
        self.provider_entry = QLineEdit()

        self.label_label = QLabel("Label:")
        self.label_entry = QLineEdit()

        self.secret_label = QLabel("Secret Key:")
        self.secret_entry = QLineEdit()

    def add_to_layout(self, layout: QVBoxLayout):
        layout.addWidget(self.provider_label)
        layout.addWidget(self.provider_entry)
        layout.addWidget(self.label_label)
        layout.addWidget(self.label_entry)
        layout.addWidget(self.secret_label)
        layout.addWidget(self.secret_entry)

    def set_fields(self, account):
        self.provider_entry.setText(account.provider)
        self.label_entry.setText(account.label)
        self.secret_entry.setText(account.secret)
        