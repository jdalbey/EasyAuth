import unittest
from unittest.mock import patch, Mock

import pytest
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtCore import Qt
from export_import_dialog import ExportImportDialog
from account_manager import AccountManager, Account, OtpRecord

class TestExportDialog(unittest.TestCase):

    @patch('export_import_dialog.QMessageBox.information')
    @patch("export_import_dialog.AccountManager")
    @patch.object(QFileDialog, "getSaveFileName")
    def test_export_btn(self, mockFileDialog, mockAccountManager, mock_messagebox):
        # Create the dialog instance
        dialog = ExportImportDialog()
        dialog.accept = Mock()  # Mock the accept method of the dialog
        dialog.account_manager = mockAccountManager
        # Mock QFileDialog.getOpenFileName to return a tuple (file_path, filter)
        mockFileDialog.return_value = ("/tmp/test_export.json", "")
        # Act
        dialog.file_choose_btn.click()
        # Verify calling export_accounts
        dialog.account_manager.export_accounts.assert_called_once()
        # Verify Ack messagebox called
        mock_messagebox.assert_called_once()

    def test_build_provider_preview(self):

        rec1 = OtpRecord("Woogle","me@woogle.com","secret")
        rec2 = OtpRecord("Boogle","me@boogle.com","secret")
        accounts = [rec1.toAccount(), rec2.toAccount()]
        # Construct the dialog
        dialog = ExportImportDialog()
        # Verify that a preview list can be created from a list of accounts
        msg, rem = dialog.build_provider_preview(accounts)
        assert msg == "Woogle, Boogle, "
        assert rem == 0



    # Using setUpClass and tearDownClass ensures that QApplication is created once for the entire test suite, preventing multiple instances.
    @classmethod
    def setUpClass(cls):
        # QApplication is created once for the entire test suite
        cls.app = QApplication([])


    @classmethod
    def tearDownClass(cls):
        # Ensure QApplication is properly cleaned up after all tests
        cls.app.quit()


    def setUp(self):
        # No need to create QApplication here; it's already done in setUpClass
        pass


    def tearDown(self):
        # Clean up dialog and other resources
        pass

