import json

from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QDrag, QFont
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QWidget, QLabel, QApplication, QSizePolicy)

from account_manager import AccountManager

class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragged_row = None

    def startDrag(self, supported_actions):
        # Capture the source row
        self.dragged_row = self.currentRow()
        super().startDrag(supported_actions)

    def dropEvent(self, event):
        if event.source() == self:
            target_row = self.indexAt(event.pos()).row()
            if target_row == -1:
                target_row = self.count() - 1

            # Update the underlying model
            parent = self.parentWidget()
            if isinstance(parent, ReorderDialog):
                account = parent.accounts.pop(self.dragged_row)
                parent.accounts.insert(target_row, account)

            # Let the parent class handle visual reordering
            super().dropEvent(event)
        else:
            event.ignore()


class ReorderDialog(QDialog):
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        # Create copies of each account
        self.accounts = AccountManager.duplicate_accounts(accounts)
        self.setWindowTitle("Reorder Accounts")
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
        self.populate_list()
        layout.addWidget(self.list_widget)
        self.list_widget.setCurrentRow(0)
        self.list_widget.setStyleSheet("""QListWidget
{
border : 2px solid black;
background: #fafbeb;  
}
QListView::item
{
    padding: 5px;
}
QListView::item:selected
{
border : 1px dashed black;
background : lightblue;
color:blue;
}""")

        # Buttons layout
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def populate_list(self):
        font = QFont("Serif", 12)
        for account in self.accounts:
            display_text = f"⇳ {account.provider} - {account.label}"
            item = QListWidgetItem(display_text)
            item.setFont(font)
            self.list_widget.addItem(item)

    def get_ordered_accounts(self):
        return self.accounts


# Local main for unit testing
if __name__ == '__main__':
    import sys
    from dataclasses import asdict
    from account_manager import AccountManager

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
