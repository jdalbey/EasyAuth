import pytest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from QRselectionDialog import QRselectionDialog
from account_manager import Account, OtpRecord
@pytest.fixture
def app(qtbot):
    app = QApplication([])
    return app

def test_dialog_noselection_OK(qtbot):
    accounts = [OtpRecord("Woogle","me@woogle.com","secret"),
                OtpRecord("Boogle","me@boogle.com","secret")]

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
    # Nobody was selected
    assert dialog.get_selected_account() == None

def test_dialog_selection(qtbot):
    accounts = [OtpRecord("Woogle","me@woogle.com","secret"),
                OtpRecord("Boogle","me@boogle.com","secret")]

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
    # Woogle was selected
    assert dialog.get_selected_account().issuer == "Woogle"
