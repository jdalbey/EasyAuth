import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QRadioButton, QPushButton, \
    QLabel, QSpacerItem, QSizePolicy, QWidget, QButtonGroup
from models import Account

class QRselectionDialog(QDialog):
    def __init__(self, accounts, parent=None ):
        super().__init__(parent)
        self.setWindowTitle("Select a QR code")
        self.selected_account = None

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

        # Add accounts as rows with radio buttons
        for account in accounts:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setAlignment(Qt.AlignLeft)

            # Radio button on the left
            radio_button = QRadioButton()
            self.button_group.addButton(radio_button)  # Add radio button to the button group
            # Label should be adjacent to radio button
            label = QLabel(f"{account.provider} - {account.label}")

            # Add the radio button and label to the row layout
            row_layout.addWidget(radio_button)
            row_layout.addWidget(label,alignment=Qt.AlignLeft)
            self.scroll_layout.addWidget(row_widget)

            # Store a reference to the account in the row widget
            row_widget.account = account

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.scroll_frame)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok)
        button_layout.addWidget(ok_button)
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.accept())
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
                self.selected_account = row_widget.account
                break
        self.accept()  # Close the dialog after selection

    def get_selected_account(self):
        return self.selected_account


# Sample accounts
accounts = [
    Account(provider="Provider1", label="Account1",secret="",last_used=""),
    Account(provider="Provider2", label="Account2",secret="",last_used=""),
    Account(provider="Provider3", label="Account3",secret="",last_used=""),
]

# Test the dialog
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = QRselectionDialog(accounts)

    # The dialog.exec_() call will block execution until the dialog is closed
    if dialog.exec_() == QDialog.Accepted:
        selected_account = dialog.get_selected_account()
        if selected_account:
            print(f"Selected Account: {selected_account.provider} - {selected_account.name}")
        else:
            print("No account selected.")

    sys.exit()  # Ensure that the application quits properly
