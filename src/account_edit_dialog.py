from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox, QFrame, QSizePolicy, QGridLayout, QPushButton, QWidget, QDialog, \
    QVBoxLayout, QLineEdit, QHBoxLayout

from models import Account
from secrets_manager import SecretsManager


class EditAccountDialog(QDialog):
    def __init__(self, parent, controller, index, account):
        super().__init__(parent)
        self.controller = controller
        self.secrets_manager = SecretsManager()
        self.account = account
        self.index = index

        print (f"EditAccountDialog init got {index} {account.provider}")
        self.setWindowTitle("Edit Account")
        self.setMinimumWidth(475)

        # Main layout
        layout = QVBoxLayout(self)

        # Form section
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
        form_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout = QGridLayout(form_frame)

        # Provider
        form_layout.addWidget(QLabel("Provider:"), 0, 0, Qt.AlignRight)
        self.provider_entry = QLineEdit(account.provider)
        form_layout.addWidget(self.provider_entry, 0, 1)

        # Label
        form_layout.addWidget(QLabel("Label:"), 1, 0, Qt.AlignRight)
        self.label_entry = QLineEdit(account.label)
        form_layout.addWidget(self.label_entry, 1, 1)

        # Secret Key
        form_layout.addWidget(QLabel("Secret Key:"), 2, 0, Qt.AlignRight)
        self.secret_key_entry = QLineEdit(controller.secrets_manager.decrypt(account.secret))
        form_layout.addWidget(self.secret_key_entry, 2, 1)

        layout.addWidget(form_frame)

        # Button section
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(
            lambda _, account=account, idx=index: self.handle_update_request(idx, account=account))

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.confirm_delete_account())

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(cancel_btn)
        layout.addWidget(button_frame)

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

        layout.addWidget(last_used_frame)

        # Add spacer to push buttons toward top
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)



    def handle_update_request(self,index, account):
        print (f"EditAcctDialog is handling update request for: {index} ")
        encrypted_secret = self.secrets_manager.encrypt(self.secret_key_entry.text())
        up_account = Account(self.provider_entry.text(), self.label_entry.text(), encrypted_secret, account.last_used)
        self.controller.update_account(index, up_account)
        self.close()

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
            self.controller.delete_account(self.account)
            self.accept()

    def handle_QR_reveal(self):
        # TODO: more robust flag
        if self.reveal_qr_button.text() == "Reveal QR code":
            # Generate QR code
            qr_code_image = self.controller.generate_qr_code(self.account)
            pixmap = QPixmap()
            pixmap.loadFromData(qr_code_image)
            self.qr_code_label = QLabel()
            self.qr_code_label.setPixmap(pixmap)
            self.layout().addWidget(self.qr_code_label)
            self.reveal_qr_button.setText("Hide QR code")
        else:
            # Hide QR code
            self.qr_code_label.deleteLater()
            self.qr_code_label = QLabel()
            self.reveal_qr_button.setText("Reveal QR code")