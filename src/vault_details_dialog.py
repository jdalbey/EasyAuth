import copy
import logging
import os

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QMessageBox, QFrame, QSizePolicy, QGridLayout, QPushButton, QVBoxLayout, \
    QToolButton, QApplication, QWhatsThis

import cipher_funcs
import otp_funcs
from account_mgr import Account, OtpRecord
from styles import info_btn_style
from utils import assets_dir
from vault_entry_dialog import VaultEntryDialog

class VaultDetailsDialog(VaultEntryDialog):
    """ Dialog to edit/update an existing account.
    Inherits from VaultEntryDialog and adds details fields.
    This dialog is displayed when the user clicks on the provider name in the main window."""
    def __init__(self, parent, index, account):
        """ Initialize the dialog.
        @param parent is the parent window.
        @param index the position in the list of accounts of the item to be updated.
        @param account the current account info.
         """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.account = account
        self.index = index
        self.setMinimumSize(380,360)
        self.resize(self.width(), self.minimumHeight())

        self.setWindowTitle("View Vault Entry")

        # Set initial buttons state
        self.btn_Edit.show()
        self.btn_Delete.show()

        # set Learn more link for this dialog
        self.label_LearnMore.setText('<a href="https://github.com/jdalbey/EasyAuth/wiki/User-Manual#41-editing-an-existing-vault-entry">Learn more</a>')

        # Setup actions to be taken
        self.btn_Edit.clicked.connect(self.start_editting)
        self.btn_Save.clicked.disconnect()
        self.btn_Save.clicked.connect(lambda _, account=account, idx=index: self.handle_update_request(idx, account=account))
        self.btn_Delete.clicked.connect(self.confirm_delete_account)

        # Initially fields are read only
        self.provider_entry.setReadOnly(True)
        self.label_entry.setReadOnly(True)
        self.secret_entry.setReadOnly(True)

        # Place current account data into fields for updating
        self.editable_account = copy.deepcopy(account)
        self.editable_account.secret = cipher_funcs.decrypt(account.secret)
        self.provider_entry.setText(self.editable_account.issuer)
        self.label_entry.setText(self.editable_account.label)
        self.secret_entry.setText(self.editable_account.secret)

        # Set the icon for the current provider
        pixmap = self.providers.get_provider_icon_pixmap(self.editable_account.issuer)
        # If we can't find an icon use the default icon, a globe.
        if pixmap == None:
            pixmap = QPixmap(os.path.join(assets_dir(), "globe_icon.png"))
        self.icon_label.setPixmap(pixmap)

        # because setText causes validation to occur, Save will become enabled.  Thus
        # we need to explicitly disable it here so it's ready for user actions.
        self.btn_Save.setEnabled(False)

        # Frame for the edit dialog features
        dialog_frame = QFrame()
        dialog_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.bottom_layout = QVBoxLayout()

        # Last Used section
        last_used_frame = QFrame()
        last_used_frame.setFrameStyle(QFrame.StyledPanel)
        last_used_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        last_used_layout = QGridLayout(last_used_frame)

        # Last Used Label
        last_used_layout.addWidget(QLabel("Last Used:"), 0, 0, Qt.AlignRight)
        self.last_used_label = QLabel(account.last_used)
        last_used_layout.addWidget(self.last_used_label, 0, 1)
        # Usage Count Label
        last_used_layout.addWidget(QLabel("Usage Count:"), 1, 0, Qt.AlignRight)
        self.usage_count_label = QLabel(str(account.used_frequency))
        last_used_layout.addWidget(self.usage_count_label, 1, 1)

        # Reveal QR Code Button
        self.reveal_qr_button = QPushButton("Show &QR code")
        self.reveal_qr_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.reveal_qr_button.clicked.connect(self.handle_QR_reveal)
        last_used_layout.addWidget(self.reveal_qr_button, 2, 0, 1, 2, Qt.AlignCenter)
        # help button
        user_info_btn = QToolButton()
        user_info_btn.setToolTip("This QR code can be used to import this account in another application.")
        info_icon = QIcon(os.path.join(assets_dir(),"question_mark_icon.svg"))
        user_info_btn.setIcon(info_icon)
        user_info_btn.setIconSize(QSize(16, 16))

        # Make square button invisible so only circular icon shows
        user_info_btn.setStyleSheet(info_btn_style)

        last_used_layout.addWidget(user_info_btn, 2, 2, Qt.AlignCenter)
        self.bottom_layout.addWidget(last_used_frame,alignment=Qt.AlignCenter)

        # Locate the form's layout so we can add the bottom fields
        form_layout = self.findChild(QVBoxLayout, "mainVerticalLayout")
        form_layout.insertLayout(1, self.bottom_layout)

    def start_editting(self):
        """ Enable fields for editing. """
        self.btn_Edit.setEnabled(False)
        self.btn_Save.setEnabled(False)
        self.btn_Cancel.setEnabled(True)
        self.btn_Delete.setEnabled(True)
        self.provider_entry.setReadOnly(False)
        self.label_entry.setReadOnly(False)
        self.setWindowTitle("Edit Vault Entry")

    def update_qr_button_text(self):
        """Update button text based on QR code visibility state"""
        self.reveal_qr_button.setText("Hide QR code" if self.is_qr_visible else "Reveal QR code")

    def handle_update_request(self,index, account):
        """Update the account with the fields in the account dialog.
           @param index is position in account list.
           @param account is info given to edit dialog when launched.
        """
        self.logger.debug (f"EditAcctDialog is handling update request for: {index} ")
        self.encrypted_secret = None
        # Validate secret key
        if otp_funcs.is_valid_secretkey(self.secret_entry.text()):
            self.encrypted_secret = cipher_funcs.encrypt(self.secret_entry.text())
            # create the updated account from the data entry fields and the original details fields
            up_account = Account(self.provider_entry.text(), self.label_entry.text(),
                                 self.encrypted_secret, account.last_used, account.used_frequency, account.favorite)
            # Go update the account, checking for duplicates
            if self.account_manager.update_account(index, up_account):
                self.close()
            else:
                QMessageBox.information(self, "Warning", "Account with same provider and user already exists")
        else:
            QMessageBox.information(self,"Error",f'The secret key is invalid')

    def confirm_delete_account(self):
        """ When user tries to delete an account this confirmation dialog is displayed. """
        # Create the message box to be a question with Yes and No buttons
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Account Delete")
        msg.setTextFormat(Qt.RichText)  # Use rich text for HTML links
        msg.setIcon(QMessageBox.Question)
        msg.setText(f'Are you sure you want to delete this account?<br>{self.account.issuer} ({self.account.label})<br>'+
            f"You will lose access to {self.account.issuer} unless you have saved the recover codes. "+
            '<a href="https://github.com/jdalbey/EasyAuth/wiki/User-Manual#42-deleting-an-entry-from-the-vault">(Learn more)</a>')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        # Display the message box
        reply = msg.exec_()

        # If reply is yes, proceed with deletion
        if reply == QMessageBox.Yes:
            self.account_manager.delete_account(self.account)
            self.accept()

    # disable the secret key so it can't be altered while QR code is revealed.
    def disable_fields(self):
        self.secret_entry.setDisabled(True)

    def enable_fields(self):
        self.secret_entry.setEnabled(True)

    def handle_QR_reveal(self):
        """ Show the QR code for this vault entry. """
        # generate QR code
        qr_code_image = otp_funcs.generate_qr_image(self.account)

        # Create the message box
        msg_box = QMessageBox(self)

        # Load the image
        pixmap = QPixmap()
        pixmap.loadFromData(qr_code_image)

        # Set the image as the icon for the message box
        msg_box.setIconPixmap(pixmap)

        msg_box.setWindowTitle(f"{self.provider_entry.text()} QR Code")
        msg_box.setText("")

        # Show the message box
        msg_box.exec_()

# Local main for unit testing
if __name__ == '__main__':
    import sys
    # Note: make sure light theme is set cause the dark icons won't be visible to your eye.
    app = QApplication(sys.argv)
    rec = OtpRecord("Figma","billy@gmail.com","AB34 CD56 EF77")
    acct = rec.toAccount()

    dialog = VaultDetailsDialog(None, 1, acct)
    dialog.exec()