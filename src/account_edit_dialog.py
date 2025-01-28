import logging
import copy
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QMessageBox, QFrame, QSizePolicy, QGridLayout, QPushButton, QWidget, QDialog, \
    QVBoxLayout, QLineEdit, QHBoxLayout, QToolButton, QApplication
from PyQt5.uic import loadUi

import account_manager
import otp_funcs
from styles import info_btn_style
from account_manager import Account, AccountManager
import cipher_funcs
from provider_search_dialog import ProviderSearchDialog


class EditAccountDialog(QDialog):
    """ Dialog to edit/update an existing account. """
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
        self.setMinimumWidth(300)

        loadUi("assets/EditAccountForm.ui", self)  #loads directions_frame

        # Make the Delete button visible on this form
        self.btn_Delete.setVisible(True)
        self.btn_Delete.setEnabled(True)

        # Setup actions to be taken
        self.btn_Lookup.clicked.connect(self.provider_lookup)
        self.btn_Save.clicked.connect(self.save_fields)
        self.btn_Delete.clicked.connect(self.confirm_delete_account)
        self.btn_Cancel.clicked.connect(self.reject)
        self.provider_entry.textChanged.connect(self.validate_form)
        self.label_entry.textChanged.connect(self.validate_form)
        self.secret_entry.textChanged.connect(self.validate_form)
        #self.set_tab_order()

        # Place current account data into fields for updating
        editable_account = copy.deepcopy(account)
        editable_account.secret = cipher_funcs.decrypt(account.secret)
        self.set_fields(editable_account)


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
        user_info_btn.setStyleSheet(info_btn_style)
        #user_info_btn.setPopupMode(QToolButton.InstantPopup)
        last_used_layout.addWidget(user_info_btn, 1, 2, Qt.AlignCenter)
        self.bottom_layout.addWidget(last_used_frame,alignment=Qt.AlignCenter)

        # Add spacer to push buttons toward top
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bottom_layout.addWidget(spacer)
        # Locate the form's layout so we can add the bottom fields
        form_layout = self.findChild(QVBoxLayout, "verticalLayout")
        form_layout.addLayout(self.bottom_layout)


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
        self.btn_Save.setEnabled(all_filled)

    def provider_lookup(self):
        # Create and show the search page
        search_page = ProviderSearchDialog()
        search_page.load_data()
        search_page.lower()
        # Show the dialog and get the result
        if search_page.exec_() == QDialog.Accepted:
            selected = search_page.get_selected_provider()
            self.provider_entry.setText(selected)

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
        # Create the message box to be a question with Yes and No buttons
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Account Delete")
        msg.setTextFormat(Qt.RichText)  # Use rich text for HTML links
        msg.setIcon(QMessageBox.Question)
        msg.setText(f'Are you sure you want to delete this account?<br>{self.account.issuer} ({self.account.label})<br>'+
            f"You will lose access to {self.account.issuer} unless you have saved the restore codes. "+
            '<a href="https://github.com/jdalbey/EasyAuth/blob/master/docs/user_manual.md#Deleting-an-account">(Learn more)</a>')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

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
        if not self.is_qr_visible:
            # Show QR code
            qr_code_image = otp_funcs.generate_qr_image(self.account)
            pixmap = QPixmap()
            pixmap.loadFromData(qr_code_image)
            self.qr_code_label = QLabel()
            self.qr_code_label.setPixmap(pixmap)
            self.bottom_layout.addWidget(self.qr_code_label,alignment=Qt.AlignCenter)
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

    def set_fields(self, otp_record):
        """ Convenience method for children """
        self.provider_entry.setText(otp_record.issuer)
        self.label_entry.setText(otp_record.label)
        self.secret_entry.setText(otp_record.secret)

    def save_fields(self):
        issuer = self.provider_entry.text()
        label = self.label_entry.text()
        secret = self.secret_entry.text()
        otp_record = account_manager.OtpRecord(issuer, label, secret)
        # Validate secret key
        if otp_funcs.is_valid_secretkey(secret):
            if self.account_manager.save_new_account(otp_record):
                self.accept()
            else:
                 QMessageBox.information(self,"Warning","Account with same provider and user already exists")
        else:
            QMessageBox.information(self,"Error",f'The secret key is invalid')

# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    rec = account_manager.OtpRecord("A","B","AB34")
    acct = rec.toAccount()
    dialog = EditAccountDialog(None, 1, acct)
    dialog.exec()