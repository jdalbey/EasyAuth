import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QLabel, QApplication, QSizePolicy)
from account_mgr import AccountManager

""" The reorder dialog lets the user create a custom ordering of items in the vault."""

class CustomListWidget(QListWidget):
    """ A custom list widget that allows drag and drop. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragged_row = None
        self.setWindowFlags(Qt.WindowTitleHint | Qt.Dialog | Qt.WindowCloseButtonHint) # x-platform consistency

    def startDrag(self, supported_actions):
        # Capture the source row
        self.dragged_row = self.currentRow()
        super().startDrag(supported_actions)

    def dropEvent(self, event):
        if event.source() == self:
            # Let the parent class handle visual reordering
            super().dropEvent(event)
            # Target is where the item was dropped
            target_row = self.indexAt(event.pos()).row()
            if target_row == -1:
                target_row = self.count() - 1

            # In the list widget there's a dropindicator that appears BETWEEN rows,
            # so we need to adjust the target_row depending on where the
            # actual drop happened.
            if self.dropIndicatorPosition() == QListWidget.BelowItem:
                target_row += 1

            # If source row < target row then subtract 1 from target row because
            # the source is taken away, moving every one up one spot.
            if self.dragged_row < target_row:
                target_row -= 1

            # Update the underlying model (accounts in ReorderDialog)
            # moving the item from original spot to new spot
            parent = self.parentWidget()
            if isinstance(parent, ReorderDialog):
                account = parent.accounts.pop(self.dragged_row)
                parent.accounts.insert(target_row, account)
        else:
            event.ignore()


class ReorderDialog(QDialog):
    """ Display a list of accounts and allow user to reorder them. """
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        # Create copies of each account
        self.accounts = AccountManager.duplicate_accounts(accounts)
        self.setWindowTitle("Reorder Vault Entries")
        self.resize(500, 300)
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        hint_label = QLabel("Use drag and drop to reorder items.")
        layout.addWidget(hint_label)

        # List widget to show accounts
        self.list_widget = CustomListWidget()
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_widget.setAutoScroll(True)
        layout.addWidget(self.list_widget)
        self.list_widget.setCurrentRow(0)
        self.populate_list()

        # Buttons layout
        button_layout = QHBoxLayout()
        ok_button = QPushButton("&Save")
        cancel_button = QPushButton("&Cancel")
        ok_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def populate_list(self):
        """ Put the items from accounts into the list. """
        for account in self.accounts:
            display_text = f"⇳ {account.issuer} - {account.label}"
            item = QListWidgetItem(display_text)
            self.list_widget.addItem(item)

    def get_ordered_accounts(self):
        """ Accessor to the final list. """
        return self.accounts


# Local main for unit testing
if __name__ == '__main__':
    import sys
    from dataclasses import asdict

    app = QApplication(sys.argv)
    mgr = AccountManager()
    dialog = ReorderDialog(mgr.accounts, None)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        accounts = dialog.get_ordered_accounts()
        print (f"First account: {accounts[0].provider}")
        [print (item.provider) for item in accounts]
        account_dicts = [asdict(account) for account in accounts]
        json_str = json.dumps(account_dicts)
        print(json_str)
        #mgr.set_accounts(json_str)
        #mgr.save_accounts()
