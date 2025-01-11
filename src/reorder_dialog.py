import json

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QWidget, QLabel, QApplication)

from controllers import AppController
from models import Account, AccountManager

class ReorderDialog(QDialog):
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        # Create copies of each account
        self.accounts = AccountManager.duplicate_accounts(accounts)
        self.setWindowTitle("Reorder Accounts")
        self.resize(700, 300)
        self.setup_ui()


    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)

        # List widget to show accounts
        self.list_widget = QListWidget()
        self.populate_list()
        layout.addWidget(self.list_widget)
        self.list_widget.setCurrentRow(0)

        # Buttons layout
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def populate_list(self):
        for account in self.accounts:
            # Display provider and label for each account
            display_text = f"{account.provider} - {account.label}"
            item = QListWidgetItem() #display_text)
            widget = self.create_item_widget(account)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def create_item_widget(self, account):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)

        # Account label
        label = QLabel(f"{account.provider} - {account.label}")
        layout.addWidget(label)
        
        # Spacer to push buttons to the right
        layout.addStretch()

        # Up button
        up_button = QPushButton("↑")
        up_button.setFixedSize(30, 25)
        up_button.clicked.connect(lambda: self.move_item_up(account))
        layout.addWidget(up_button)

        # Down button
        down_button = QPushButton("↓")
        down_button.setFixedSize(30, 25)
        down_button.clicked.connect(lambda: self.move_item_down(account))
        layout.addWidget(down_button)

        return widget

    def move_item_up(self, account):
        current_row = self.find_account_row(account)
        if current_row > 0:
            self.swap_items(current_row, current_row - 1)
            self.list_widget.setCurrentRow(current_row - 1)

    def move_item_down(self, account):
        current_row = self.find_account_row(account)
        if current_row < self.list_widget.count() - 1:
            self.swap_items(current_row, current_row + 1)
            self.list_widget.setCurrentRow(current_row + 1)

    def find_account_row(self, account):
        # Compare accounts based on their attributes
        for i in range(self.list_widget.count()):
            curr_account = self.accounts[i]
            if (curr_account.provider == account.provider and 
                curr_account.label == account.label and 
                curr_account.secret == account.secret and 
                curr_account.last_used == account.last_used):
                return i
        return -1

    def swap_items(self, row1, row2):
        # Swap in the internal list
        self.accounts[row1], self.accounts[row2] = self.accounts[row2], self.accounts[row1]
        
        # Clear and repopulate the list widget
        self.list_widget.clear()
        self.populate_list()
        # Highlight the item at the new position (row2)
        self.list_widget.setCurrentRow(row2)
    def get_ordered_accounts(self):
        return self.accounts

# local main for unit testing
if __name__ == '__main__':
    import sys
    from dataclasses import dataclass, asdict

    app = QApplication(sys.argv)
    controller = AppController()

    dialog = ReorderDialog(controller.get_accounts(), None)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        accounts = dialog.get_ordered_accounts()

        account_dicts = [asdict(account) for account in accounts]
        json_str = json.dumps(account_dicts)
        print(json_str)


