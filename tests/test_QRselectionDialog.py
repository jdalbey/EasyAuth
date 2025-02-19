import pytest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from qr_selection_dialog import QRselectionDialog
from account_mgr import Account, OtpRecord
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

    # Find the "Cancel" button
    cancel_button = dialog.cancel_button
    # Simulate clicking Cancel
    qtbot.mouseClick(cancel_button, Qt.LeftButton)

    # Verify the dialog was accepted
    assert dialog.result() == QDialog.Rejected, "Failed: Dialog was not rejected"
    # Nobody was selected
    assert dialog.get_selected_account() == None

def test_dialog_selection(qtbot):
    accounts = [OtpRecord("Woogle","me@woogle.com","secret"),
                OtpRecord("Boogle","me@boogle.com","secret")]

    # Create and show the dialog
    dialog = QRselectionDialog(accounts)
    # Wait for the dialog (it won't actually appear on screen because we didn't do show()
    qtbot.waitForWindowShown(dialog)

    # Find the "OK" button
    ok_button = dialog.ok_button
    assert not ok_button.isEnabled()

    # Select a radio button
    dialog.button_group.buttons()[0].setChecked(True)

    # Selecting a radio button should enable the OK button
    assert ok_button.isEnabled()

    # Simulate clicking the "OK" button (this is the "Accept" action)
    qtbot.mouseClick(ok_button, Qt.LeftButton)

    # Verify the dialog was accepted
    assert dialog.result() == QDialog.Accepted, "Failed: Dialog was not accepted"
    # Woogle was selected
    assert dialog.get_selected_account().issuer == "Woogle"
