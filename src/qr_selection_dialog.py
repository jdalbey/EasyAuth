import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QRadioButton, QPushButton, \
    QLabel, QSpacerItem, QSizePolicy, QWidget, QButtonGroup, QShortcut
from account_manager import OtpRecord

class QRselectionDialog(QDialog):
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a QR code")
        self.setWindowFlags(Qt.WindowTitleHint | Qt.Dialog | Qt.WindowCloseButtonHint)  # x-platform consistency
        self.selected_otp_record = None

        # Layout setup
        layout = QVBoxLayout(self)

        # Add the instruction label at the top
        instruction_label = QLabel("We found more than one QR code, please select one.")
        layout.addWidget(instruction_label)

        # Scrollable frame setup
        self.scroll_frame = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_frame)

        # Button group for radio buttons
        self.button_group = QButtonGroup(self)
        self.radio_buttons = []  # Store references to radio buttons for tab ordering

        # Add accounts as rows with radio buttons
        for index, otp_record in enumerate(accounts):
            row_widget = QWidget()
            row_widget.setFocusPolicy(Qt.NoFocus)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setAlignment(Qt.AlignLeft)

            # Create radio button
            radio_button = QRadioButton(f"&{index}: {otp_record.issuer} - {otp_record.label}")
            self.button_group.addButton(radio_button)
            self.radio_buttons.append(radio_button)

            # Add radio button to the layout
            row_layout.addWidget(radio_button)
            row_widget.setLayout(row_layout)
            self.scroll_layout.addWidget(row_widget)

            # Store a reference to the account in the row widget
            row_widget.account = otp_record

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.scroll_frame)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFocusPolicy(Qt.NoFocus)  # Prevent scroll area from interfering with focus
        layout.addWidget(scroll_area)

        # Button layout
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("&OK")
        self.ok_button.clicked.connect(self.on_ok)
        button_layout.addWidget(self.ok_button)

        cancel_button = QPushButton("&Cancel")
        cancel_button.clicked.connect(self.accept)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Add spacer to push the button to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

    def on_ok(self):
        # Check which radio button is selected
        for button in self.button_group.buttons():
            if button.isChecked():
                # Find the corresponding account from the row widget
                row_widget = button.parentWidget()
                self.selected_otp_record = row_widget.account
                break
        self.accept()  # Close the dialog after selection

    def get_selected_account(self):
        return self.selected_otp_record


# Sample accounts
accounts = [
    OtpRecord(issuer="Provider1", label="Account1",secret="x"),
    OtpRecord(issuer="Provider2", label="Account2",secret="x"),
    OtpRecord(issuer="Provider3", label="Account3",secret="x"),
]

# Test the dialog
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = QRselectionDialog(accounts)

    # The dialog.exec_() call will block execution until the dialog is closed
    if dialog.exec_() == QDialog.Accepted:
        selected_account = dialog.get_selected_account()
        if selected_account:
            print(f"Selected Account: {selected_account.issuer} - {selected_account.label}")
        else:
            print("No account selected.")

    sys.exit()  # Ensure that the application quits properly
