import pytest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from QRselectionDialog import QRselectionDialog
from account_manager import Account
@pytest.fixture
def app(qtbot):
    app = QApplication([])
    return app

def test_dialog_noselection_OK(qtbot):
    accounts = [Account("Woogle","me@woogle.com","secret","2000-01-01 01:01"),
                Account("Boogle","me@boogle.com","secret","2000-01-01 01:01")]

    # Create and show the dialog
    dialog = QRselectionDialog(accounts)

    # Wait for the dialog (it won't actually appear on screen because we didn't do show()
    qtbot.waitForWindowShown(dialog)

    # Find the "OK" button
    ok_button = dialog.ok_button
    # Simulate clicking the "OK" button (this is the "Accept" action)
    qtbot.mouseClick(ok_button, Qt.LeftButton)

    # Verify the dialog was accepted
    assert dialog.result() == QDialog.Accepted, "Failed: Dialog was not accepted"
    assert dialog.get_selected_account() == None

def test_dialog_selection(qtbot):
    accounts = [Account("Woogle","me@woogle.com","secret","2000-01-01 01:01"),
                Account("Boogle","me@boogle.com","secret","2000-01-01 01:01")]

    # Create and show the dialog
    dialog = QRselectionDialog(accounts)
    # Wait for the dialog (it won't actually appear on screen because we didn't do show()
    qtbot.waitForWindowShown(dialog)

    # Select a radio button
    dialog.button_group.buttons()[0].setChecked(True)

    # Find the "OK" button
    ok_button = dialog.ok_button

    # Simulate clicking the "OK" button (this is the "Accept" action)
    qtbot.mouseClick(ok_button, Qt.LeftButton)

    # Verify the dialog was accepted
    assert dialog.result() == QDialog.Accepted, "Failed: Dialog was not accepted"
    assert dialog.get_selected_account().provider == "Woogle"
