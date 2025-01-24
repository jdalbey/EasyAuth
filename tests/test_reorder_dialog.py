import pytest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from reorder_dialog import ReorderDialog
from account_manager import Account
@pytest.fixture
def app(qtbot):
    app = QApplication([])
    return app

def test_dialog_noselection_OK(qtbot):
    accounts = [Account("Woogle","me@woogle.com","secret","2000-01-01 01:01"),
                Account("Boogle","me@boogle.com","secret","2000-01-01 01:01")]

    # Create and show the dialog
    dialog = ReorderDialog(accounts)

    # Wait for the dialog (it won't actually appear on screen because we didn't do show()
    qtbot.waitForWindowShown(dialog)

    # Verify the list was populated
    assert dialog.list_widget.count() == 2

