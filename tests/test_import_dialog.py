import pytest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from export_import_dialog import ExportImportDialog
from account_manager import AccountManager, Account, OtpRecord
@pytest.fixture
def app(qtbot):
    app = QApplication([])
    return app

def test_dialog_noselection_OK(qtbot):

    rec1 = OtpRecord("Woogle","me@woogle.com","secret")
    rec2 = OtpRecord("Boogle","me@boogle.com","secret")
    accounts = [rec1.toAccount(), rec2.toAccount()]
    am = AccountManager()
    # Create and show the dialog
    dialog = ExportImportDialog(am)
    msg, rem = dialog.build_provider_sample(accounts)
    assert msg == "Woogle, Boogle, "
    assert rem == 0


