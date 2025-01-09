from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QFrame, QSizePolicy, QGridLayout


class AccountEntryForm(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout = QGridLayout(self)

        # Provider
        form_layout.addWidget(QLabel("Provider:"), 0, 0, Qt.AlignRight)
        self.provider_entry = QLineEdit()
        form_layout.addWidget(self.provider_entry, 0, 1)

        # Label
        form_layout.addWidget(QLabel("Label:"), 1, 0, Qt.AlignRight)
        self.label_entry = QLineEdit()
        form_layout.addWidget(self.label_entry, 1, 1)

        # Secret Key
        form_layout.addWidget(QLabel("Secret Key:"), 2, 0, Qt.AlignRight)
        self.secret_entry = QLineEdit()
        form_layout.addWidget(self.secret_entry, 2, 1)


    def set_fields(self, account):
        self.provider_entry.setText(account.provider)
        self.label_entry.setText(account.label)
        self.secret_entry.setText(account.secret)
        