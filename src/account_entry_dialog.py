from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QFrame, QSizePolicy, QGridLayout, QToolButton, QPushButton, \
    QDialog, QApplication, QMessageBox

import otp_funcs
from provider_search_dialog import ProviderSearchDialog
from account_manager import OtpRecord

# Info button: Make square button invisible so only circular icon shows
info_btn_style = """
    QToolButton {
        border: none;       /* Remove border */
        background: none;   /* Remove background */
        padding: 0px;       /* Remove padding */
    }
    """
class AccountEntryDialog(QDialog):
    """ Form containing three input fields for Provider, User, Secret Key. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.form_layout = QGridLayout(self)
        #self.setFrameStyle(QFrame.StyledPanel)

        # Provider
        self.form_layout.addWidget(QLabel("Provider:"), 1, 0, Qt.AlignRight)
        self.provider_entry = QLineEdit()
        self.provider_entry.textChanged.connect(self.validate_form)
        self.provider_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.form_layout.addWidget(self.provider_entry, 1, 1)
        # Lookup button
        provider_lookup_btn = QPushButton("Lookup")
        provider_lookup_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        provider_lookup_btn.clicked.connect(self.provider_lookup)
        self.form_layout.addWidget(provider_lookup_btn, 1,2)
        provider_info_btn = QToolButton()
        provider_info_btn.setToolTip("Name identifying the website or online service\nthis account authenticates with.")
        info_icon = QIcon("images/question_mark_icon_16.png")
        provider_info_btn.setIcon(info_icon)
        provider_info_btn.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        provider_info_btn.setStyleSheet(info_btn_style)
        #provider_info_btn.setPopupMode(QToolButton.InstantPopup)
        self.form_layout.addWidget(provider_info_btn, 1, 3)

        # Label
        self.form_layout.addWidget(QLabel("User:"), 2, 0, Qt.AlignRight)
        self.label_entry = QLineEdit()
        self.label_entry.textChanged.connect(self.validate_form)
        """
            label: The widget (in this case, a QLabel) to be added to the layout.
            0: The row index where the widget should be placed.
            0: The column index where the widget should be placed.
            1: The number of rows the widget should span.
            2: The number of columns the widget should span.
        """
        self.form_layout.addWidget(self.label_entry, 2, 1, 1, 2)

        user_info_btn = QToolButton()
        user_info_btn.setToolTip("A label to identify this account\nsuch as your username or email address for the service.")
        user_info_btn.setIcon(info_icon)
        user_info_btn.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        user_info_btn.setStyleSheet(info_btn_style)
        #user_info_btn.setPopupMode(QToolButton.InstantPopup)
        self.form_layout.addWidget(user_info_btn, 2, 3)

        # Secret Key
        self.form_layout.addWidget(QLabel("Secret Key:"), 3, 0, Qt.AlignRight)
        self.secret_entry = QLineEdit()
        self.secret_entry.textChanged.connect(self.validate_form)
        self.form_layout.addWidget(self.secret_entry, 3, 1, 1, 2)

        secret_info_btn = QToolButton()
        secret_info_btn.setToolTip("The alphanumeric code shared with you by the provider.")
        secret_info_btn.setIcon(info_icon)
        secret_info_btn.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        secret_info_btn.setStyleSheet(info_btn_style)
        #secret_info_btn.setPopupMode(QToolButton.InstantPopup)
        self.form_layout.addWidget(secret_info_btn, 3, 3)

        # FavIcon
        # form_layout.addWidget(QLabel("Favicon:"), 3,0,Qt.AlignRight)
        # self.favicon = QLabel("")
        # form_layout.addWidget(self.favicon, 3,1)

         # Fix tabbing order to skip the info buttons and just go to entry fields
        # self.setTabOrder(self.provider_entry, self.label_entry)
        # self.setTabOrder(self.label_entry, self.secret_entry)
        provider_lookup_btn.setFocusPolicy(Qt.NoFocus)

    def validate_form(self):
        # Stub implementation is completed by subclasses
        pass

    def set_fields(self, otp_record):
        self.provider_entry.setText(otp_record.issuer)
        self.label_entry.setText(otp_record.label)
        self.secret_entry.setText(otp_record.secret)
        # find icon to show in edit form
        # if len(account.issuer) > 0:
        #     tmplabel = self.providers.get_provider_icon(account.issuer)
        #     self.favicon.setPixmap(tmplabel.pixmap())

    def save_fields(self):
        issuer = self.provider_entry.text()
        label = self.label_entry.text()
        secret = self.secret_entry.text()
        otp_record = OtpRecord(issuer, label, secret)
        # Validate secret key
        if otp_funcs.is_valid_secretkey(secret):
            if self.account_manager.save_new_account(otp_record):
                self.accept()
            else:
                 QMessageBox.information(self,"Warning","Account with same provider and user already exists")
        else:
            QMessageBox.information(self,"Error",f'The secret key is invalid')

    # disable the secret key so it can't be altered while QR code is revealed.
    def disable_fields(self):
        self.secret_entry.setDisabled(True)

    def enable_fields(self):
        self.secret_entry.setEnabled(True)

    def provider_lookup(self):
        # Create and show the search page
        search_page = ProviderSearchDialog()
        search_page.load_data()
        search_page.lower()
        # Show the dialog and get the result
        if search_page.exec_() == QDialog.Accepted:
            selected = search_page.get_selected_provider()
            self.provider_entry.setText(selected)
            # also update the favicon
            #tmplabel = self.providers.get_provider_icon(self.provider_entry.text())
            #self.favicon.setPixmap(tmplabel.pixmap())
        # else No selection made, no action needed

# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = AccountEntryDialog()
    dialog.exec()