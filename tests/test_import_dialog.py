import pytest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from export_import_dialog import ExportImportDialog
from account_manager import AccountManager, Account
@pytest.fixture
def app(qtbot):
    app = QApplication([])
    return app

def test_dialog_noselection_OK(qtbot):
    accounts = [Account("Woogle","me@woogle.com","secret","2000-01-01 01:01"),
                Account("Boogle","me@boogle.com","secret","2000-01-01 01:01")]
    am = AccountManager()
    # Create and show the dialog
    dialog = ExportImportDialog(am)
    msg, rem = dialog.build_provider_sample(accounts)
    assert msg == "Woogle, Boogle, "
    assert rem == 0


