import logging
import copy
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QMessageBox, QFrame, QSizePolicy, QGridLayout, QPushButton, QWidget, QDialog, \
    QVBoxLayout, QLineEdit, QHBoxLayout, QToolButton, QApplication

import otp_funcs
from account_entry_dialog import AccountEntryDialog, help_style
from account_manager import Account, AccountManager
import cipher_funcs

class EditAccountDialog(AccountEntryDialog):
    def __init__(self, parent, index, account):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.account_manager = AccountManager()
        self.account = account
        self.index = index
        self.qr_code_label = None
        self.is_qr_visible = False
        #self.setFixedSize(self.size())
        # Store initial size - gets set in showEvent()
        self.initial_size = None

        self.setWindowTitle("Edit Account")
        self.setMinimumWidth(475)

        # Frame for the edit dialog features
        dialog_frame = QFrame()
        dialog_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.bottom_layout = QVBoxLayout(dialog_frame)

        # Declare save button here so we can add it to Form
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(
            lambda _, account=account, idx=index: self.handle_update_request(idx, account=account))
        self.save_btn.setEnabled(False)
        self.save_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add shared fields
        #self.shared_fields = AccountEntryDialog(self.save_btn)
        #layout.addWidget(self.shared_fields)

        # Place current account data into fields for updating
        editable_account = copy.deepcopy(account)
        editable_account.secret = cipher_funcs.decrypt(account.secret)
        self.set_fields(editable_account)

        # Button section
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        button_layout.addStretch()
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(lambda: self.confirm_delete_account())
        self.delete_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(cancel_btn)
        self.bottom_layout.addWidget(button_frame)

        # Last Used section
        last_used_frame = QFrame()
        last_used_frame.setFrameStyle(QFrame.StyledPanel)
        last_used_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        last_used_layout = QGridLayout(last_used_frame)

        # Last Used Label
        last_used_layout.addWidget(QLabel("Last Used:"), 0, 0, Qt.AlignRight)
        self.last_used_label = QLabel(account.last_used)
        last_used_layout.addWidget(self.last_used_label, 0, 1)

        # Reveal QR Code Button
        self.reveal_qr_button = QPushButton("Reveal QR code")
        self.reveal_qr_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.reveal_qr_button.clicked.connect(self.handle_QR_reveal)
        last_used_layout.addWidget(self.reveal_qr_button, 1, 0, 1, 2, Qt.AlignCenter)
        user_info_btn = QToolButton()
        user_info_btn.setToolTip("This QR code can be used to import this account in another application.")
        info_icon = QIcon("images/question_mark_icon_16.png")
        user_info_btn.setIcon(info_icon)
        user_info_btn.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        user_info_btn.setStyleSheet(help_style)
        #user_info_btn.setPopupMode(QToolButton.InstantPopup)
        last_used_layout.addWidget(user_info_btn, 1, 1, Qt.AlignCenter)
        self.bottom_layout.addWidget(last_used_frame)

        # Add spacer to push buttons toward top
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bottom_layout.addWidget(spacer)

        self.form_layout.addWidget(dialog_frame,4,1)

        # Set tab order for subclass fields, maintaining parent order
        # First clear any existing tab order by setting all widgets to NoFocus
        for child in self.findChildren(QWidget):
            child.setFocusPolicy(Qt.NoFocus)

        # Now explicitly set focus policy for just the widgets we want in our cycle
        self.provider_entry.setFocusPolicy(Qt.StrongFocus)
        self.label_entry.setFocusPolicy(Qt.StrongFocus)
        self.secret_entry.setFocusPolicy(Qt.StrongFocus)
        self.save_btn.setFocusPolicy(Qt.StrongFocus)
        self.delete_btn.setFocusPolicy(Qt.StrongFocus)
        cancel_btn.setFocusPolicy(Qt.StrongFocus)
        self.reveal_qr_button.setFocusPolicy(Qt.StrongFocus)
        # Create closed tab cycle among specific widgets
        self.setTabOrder(self.provider_entry, self.label_entry)  # Start with parent class fields
        self.setTabOrder(self.label_entry, self.secret_entry)
        self.setTabOrder(self.secret_entry, self.save_btn)
        self.setTabOrder(self.save_btn, self.delete_btn)
        self.setTabOrder(self.delete_btn, cancel_btn)
        self.setTabOrder(cancel_btn, self.reveal_qr_button)
        self.setTabOrder(self.reveal_qr_button, self.provider_entry)  # Complete the cycle

        # Disable tab focus for any other widgets you want to skip
        user_info_btn.setFocusPolicy(Qt.NoFocus)


    def showEvent(self, event):
        super().showEvent(event)
        # Store the initial size when the dialog is first shown
        if self.initial_size is None:
            self.initial_size = self.size()
            self.setFixedWidth(self.size().width())

    def validate_form(self):
        """ Ensure all fields have values before enabling the save button."""
        # Check if all fields are filled
        all_filled = len(self.provider_entry.text()) > 0 and len(self.label_entry.text()) > 0 and len(self.secret_entry.text()) > 0
        self.save_btn.setEnabled(all_filled)

    def update_qr_button_text(self):
        """Update button text based on QR code visibility state"""
        self.reveal_qr_button.setText("Hide QR code" if self.is_qr_visible else "Reveal QR code")

    def handle_update_request(self,index, account):
        """Update the account with the fields in the account dialog
           @param index is position in account list
           @param account is info given to edit dialog when launched"""
        self.logger.debug (f"EditAcctDialog is handling update request for: {index} ")
        self.encrypted_secret = None
        # Validate secret key
        if otp_funcs.is_valid_secretkey(self.secret_entry.text()):
            self.encrypted_secret = cipher_funcs.encrypt(self.secret_entry.text())
            up_account = Account(self.provider_entry.text(), self.label_entry.text(),
                                 self.encrypted_secret, account.last_used)
            self.account_manager.update_account(index, up_account)
            self.close()
        else:
            QMessageBox.information(self,"Error",f'The secret key is invalid')

    def confirm_delete_account(self):
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f'Are you sure you want to delete this account?\n\n{self.account.provider} ({self.account.label})\n\n'+
            f"You will lose access to {self.account.provider} unless you have saved the restore codes. (Learn more)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.account_manager.delete_account(self.account)
            self.accept()

    def handle_QR_reveal(self):
        if not self.is_qr_visible:
            # Show QR code
            qr_code_image = otp_funcs.generate_qr_image(self.account)
            pixmap = QPixmap()
            pixmap.loadFromData(qr_code_image)
            self.qr_code_label = QLabel()
            self.qr_code_label.setPixmap(pixmap)
            self.form_layout.addWidget(self.qr_code_label,5,1)
            self.reveal_qr_button.setText("Hide QR code")
            self.disable_fields()
            self.is_qr_visible = True
        else:
            # Hide QR code
            if self.qr_code_label:
                self.qr_code_label.hide()  # Hide immediately
                self.qr_code_label.deleteLater()
                self.qr_code_label = None
                self.enable_fields()
                self.is_qr_visible = False

                # Use QTimer to resize after the event loop processes the deletion
                QTimer.singleShot(0, lambda: self.resize(self.initial_size))

        self.update_qr_button_text()

# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    acct = Account("A","B","AB34","2000-01-01 00:00:00")
    acct.secret = cipher_funcs.encrypt("AB34")
    dialog = EditAccountDialog(None, 1, acct)
    dialog.exec()