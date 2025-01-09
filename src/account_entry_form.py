from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QFrame, QSizePolicy, QGridLayout, QToolButton


class AccountEntryForm(QFrame):
    def __init__(self, save_button):
        super().__init__()
        self.save_button = save_button
        self.setFrameStyle(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout = QGridLayout(self)

        # Provider
        form_layout.addWidget(QLabel("Provider:"), 0, 0, Qt.AlignRight)
        self.provider_entry = QLineEdit()
        self.provider_entry.textChanged.connect(self.validate_form)
        form_layout.addWidget(self.provider_entry, 0, 1)

        # Label
        form_layout.addWidget(QLabel("User:"), 1, 0, Qt.AlignRight)
        self.label_entry = QLineEdit()
        self.label_entry.textChanged.connect(self.validate_form)
        form_layout.addWidget(self.label_entry, 1, 1)
        help_button = QToolButton()
        #help_button.setText("?")
        help_button.setToolTip("Enter a label to identify this account\nsuch as your username or email address for the service.")
        # Name identifying the website or online service this account authenticates with
        # The alphanumeric code shared with you by the provider.
        #help_button.setStyleSheet("font-weight: bold; color: blue;")  # Style for clarity
        help_icon = QIcon("images/question_mark_icon_16.png")
        help_button.setIcon(help_icon)
        help_button.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        help_button.setStyleSheet(
            """
            QToolButton {
                border: none;       /* Remove border */
                background: none;   /* Remove background */
                padding: 0px;       /* Remove padding */
            }
            """
        )
        help_button.setPopupMode(QToolButton.InstantPopup)
        form_layout.addWidget(help_button, 1, 2)
        # Secret Key
        form_layout.addWidget(QLabel("Secret Key:"), 2, 0, Qt.AlignRight)
        self.secret_entry = QLineEdit()
        self.secret_entry.textChanged.connect(self.validate_form)
        form_layout.addWidget(self.secret_entry, 2, 1)

    def validate_form(self):
        # Check if all fields are filled
        all_filled = len(self.provider_entry.text()) > 0 and len(self.label_entry.text()) > 0 and len(self.secret_entry.text()) > 0
        self.save_button.setEnabled(all_filled)

    def set_fields(self, account):
        self.provider_entry.setText(account.provider)
        self.label_entry.setText(account.label)
        self.secret_entry.setText(account.secret)

    # disable the secret key so it can't be altered while QR code is revealed.
    def disable_fields(self):
        self.secret_entry.setDisabled(True)

    def enable_fields(self):
        self.secret_entry.setEnabled(True)
