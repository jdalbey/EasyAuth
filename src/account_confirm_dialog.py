from PyQt5.QtCore import Qt

import otp_funcs
from account_manager import AccountManager
from account_entry_dialog import AccountEntryDialog
from appconfig import AppConfig
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QSizePolicy, QFrame, \
    QApplication, QWidget


class ConfirmAccountDialog(AccountEntryDialog):
    """ Dialog to confirm the values obtained from a QR code. """
    def __init__(self, parent=None):
        super(ConfirmAccountDialog, self).__init__(parent)
        self.account_manager = AccountManager()
        self.setWindowTitle("Confirm New Account")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()

        header_label = QLabel("A QR code was found with these values:")
        self.form_layout.addWidget(header_label,0,0,1,3)

        # Declare the button frame
        button_frame = QFrame()
        button_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button_layout = QHBoxLayout(button_frame)

        self.button_layout.addStretch()

        self.save_button = QPushButton("Accept")
        self.save_button.setShortcut('Ctrl+A')
        self.save_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.save_button.clicked.connect(self.save_fields)

        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Decline")
        self.cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cancel_button.clicked.connect(self.reject) # returns False
        self.button_layout.addWidget(self.cancel_button)

        # self.layout.addLayout(self.button_layout)
        # self.setLayout(self.layout)
        self.form_layout.addWidget(button_frame, 4, 1)

        # Set tab order for subclass fields, maintaining parent order
        # First clear any existing tab order by setting all widgets to NoFocus
        for child in self.findChildren(QWidget):
            child.setFocusPolicy(Qt.NoFocus)

        # Now explicitly set focus policy for just the widgets we want in our cycle
        self.provider_entry.setFocusPolicy(Qt.StrongFocus)
        self.label_entry.setFocusPolicy(Qt.StrongFocus)
        self.secret_entry.setFocusPolicy(Qt.StrongFocus)
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.cancel_button.setFocusPolicy(Qt.StrongFocus)
        # Create closed tab cycle among specific widgets
        self.setTabOrder(self.provider_entry, self.label_entry)  # Start with parent class fields
        self.setTabOrder(self.label_entry, self.secret_entry)
        self.setTabOrder(self.secret_entry, self.save_button)
        self.setTabOrder(self.save_button, self.cancel_button)
        self.setTabOrder(self.cancel_button, self.provider_entry)  # Complete the cycle

    # Set values into fields (used by auto qr code scanning)
    def set_account(self, otp_record):
        self.set_fields(otp_record)

# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app_config = AppConfig()
    dialog = ConfirmAccountDialog(None)
    dialog.exec()
