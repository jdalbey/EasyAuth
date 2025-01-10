import logging
import copy
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QMessageBox, QFrame, QSizePolicy, QGridLayout, QPushButton, QWidget, QDialog, \
    QVBoxLayout, QLineEdit, QHBoxLayout, QToolButton

from account_entry_form import AccountEntryForm
from models import Account
from secrets_manager import SecretsManager


class EditAccountDialog(QDialog):
    def __init__(self, parent, controller, index, account):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.controller = controller
        self.secrets_manager = SecretsManager()
        self.account = account
        self.index = index
        self.qr_code_label = None
        self.is_qr_visible = False

        # Store initial size
        self.initial_size = None

        self.setWindowTitle("DemoEdit Account")
        self.setMinimumWidth(475)

        # Main layout
        layout = QVBoxLayout(self)

        # Declare save button here so we can add it to Form
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(
            lambda _, account=account, idx=index: self.handle_update_request(idx, account=account))
        self.save_btn.setEnabled(False)

        # Add shared fields
        self.shared_fields = AccountEntryForm(self.save_btn)
        layout.addWidget(self.shared_fields)

        # Place current account data into fields for updating
        editable_account = copy.deepcopy(account)
        editable_account.secret = controller.secrets_manager.decrypt(account.secret)
        self.shared_fields.set_fields(editable_account)

        # Button section
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.confirm_delete_account())

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
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

        help_style = """
            QToolButton {
                border: none;       /* Remove border */
                background: none;   /* Remove background */
                padding: 0px;       /* Remove padding */
            }
            """
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
        layout.addWidget(last_used_frame)

        # Add spacer to push buttons toward top
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

    def showEvent(self, event):
        super().showEvent(event)
        # Store the initial size when the dialog is first shown
        if self.initial_size is None:
            self.initial_size = self.size()

    def update_qr_button_text(self):
        """Update button text based on QR code visibility state"""
        self.reveal_qr_button.setText("Hide QR code" if self.is_qr_visible else "Reveal QR code")

    def handle_QR_reveal(self):
        if not self.is_qr_visible:
            # Show QR code
            qr_code_image = self.controller.generate_qr_code(self.account)
            pixmap = QPixmap()
            pixmap.loadFromData(qr_code_image)
            self.qr_code_label = QLabel()
            self.qr_code_label.setPixmap(pixmap)
            self.layout().addWidget(self.qr_code_label)
            self.reveal_qr_button.setText("Hide QR code")
            self.shared_fields.disable_fields()
            self.is_qr_visible = True
        else:
            # Hide QR code
            if self.qr_code_label:
                self.qr_code_label.hide()  # Hide immediately
                self.qr_code_label.deleteLater()
                self.qr_code_label = None
                self.shared_fields.enable_fields()
                self.is_qr_visible = False

                # Use QTimer to resize after the event loop processes the deletion
                QTimer.singleShot(0, lambda: self.resize(self.initial_size))

        self.update_qr_button_text()

