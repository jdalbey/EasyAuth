from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QFrame, QSizePolicy, QGridLayout, QToolButton, QPushButton, \
    QDialog


class AccountEntryForm(QFrame):
    def __init__(self, save_button):
        super().__init__()
        self.save_button = save_button
        self.setFrameStyle(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout = QGridLayout(self)

        help_style = """
            QToolButton {
                border: none;       /* Remove border */
                background: none;   /* Remove background */
                padding: 0px;       /* Remove padding */
            }
            """

        # Provider
        form_layout.addWidget(QLabel("Provider:"), 0, 0, Qt.AlignRight)
        self.provider_entry = QLineEdit()
        self.provider_entry.textChanged.connect(self.validate_form)
        form_layout.addWidget(self.provider_entry, 0, 1)

        provider_lookup_btn = QPushButton("Lookup")
        provider_lookup_btn.clicked.connect(self.provider_lookup)
        form_layout.addWidget(provider_lookup_btn, 0,2)
        provider_info_btn = QToolButton()
        provider_info_btn.setToolTip("Name identifying the website or online service\nthis account authenticates with.")
        info_icon = QIcon("images/question_mark_icon_16.png")
        provider_info_btn.setIcon(info_icon)
        provider_info_btn.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        provider_info_btn.setStyleSheet(help_style)
        #provider_info_btn.setPopupMode(QToolButton.InstantPopup)
        form_layout.addWidget(provider_info_btn, 0, 3)

        # Label
        form_layout.addWidget(QLabel("User:"), 1, 0, Qt.AlignRight)
        self.label_entry = QLineEdit()
        self.label_entry.textChanged.connect(self.validate_form)
        form_layout.addWidget(self.label_entry, 1, 1)
        user_info_btn = QToolButton()
        user_info_btn.setToolTip("A label to identify this account\nsuch as your username or email address for the service.")
        user_info_btn.setIcon(info_icon)
        user_info_btn.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        user_info_btn.setStyleSheet(help_style)
        #user_info_btn.setPopupMode(QToolButton.InstantPopup)
        form_layout.addWidget(user_info_btn, 1, 2)

        # Secret Key
        form_layout.addWidget(QLabel("Secret Key:"), 2, 0, Qt.AlignRight)
        self.secret_entry = QLineEdit()
        self.secret_entry.textChanged.connect(self.validate_form)
        form_layout.addWidget(self.secret_entry, 2, 1)

        secret_info_btn = QToolButton()
        secret_info_btn.setToolTip("The alphanumeric code shared with you by the provider.")
        secret_info_btn.setIcon(info_icon)
        secret_info_btn.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        secret_info_btn.setStyleSheet(help_style)
        #secret_info_btn.setPopupMode(QToolButton.InstantPopup)
        form_layout.addWidget(secret_info_btn, 2, 2)

         # Fix tabbing order to skip the info buttons and just go to entry fields
        self.setTabOrder(self.provider_entry, self.label_entry)
        self.setTabOrder(self.label_entry, self.secret_entry)

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

    def provider_lookup(self):
        from provider_search_dialog import ProviderSearchDialog
        # Create and show the search page
        search_page = ProviderSearchDialog()
        # Show the dialog and get the result
        if search_page.exec_() == QDialog.Accepted:
            selected = search_page.get_selected_provider()
            self.provider_entry.setText(selected)
        else:
            print("No selection made")


