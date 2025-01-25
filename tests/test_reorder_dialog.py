import pytest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from reorder_dialog import ReorderDialog
from account_manager import OtpRecord
@pytest.fixture
def app(qtbot):
    app = QApplication([])
    return app

def test_dialog_noselection_OK(qtbot):
    rec1 = OtpRecord("Woogle","me@woogle.com","secret")
    rec2 = OtpRecord("Boogle","me@boogle.com","secret")
    accounts = [rec1.toAccount(), rec2.toAccount()]
    # Create and show the dialog
    dialog = ReorderDialog(accounts)

    # Wait for the dialog (it won't actually appear on screen because we didn't do show()
    qtbot.waitForWindowShown(dialog)

    # Verify the list was populated
    assert dialog.list_widget.count() == 2

