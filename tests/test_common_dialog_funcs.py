import os
import unittest
from unittest.mock import patch, Mock, MagicMock

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

from account_edit_dialog import EditAccountDialog
from account_manager import AccountManager, OtpRecord, Account
from common_dialog_funcs import save_fields
class TestAddAccountDialog(unittest.TestCase):
    @patch('common_dialog_funcs.QMessageBox.information')
    @patch("account_edit_dialog.AccountManager")
    def test_save_duplicate_account(self,MockAccountManager,MockMessageBox):
        # account with an invalid secret
        encrypted_secret = 'gAAAAABnmqBZJAE6715s4cUAj0T-zcgU2FqYWZBx04JOB-kIaxqCl9rhhBrW8til6eb9PX8Q5r9qlH2XO0rlrlfG5vFXNbq3ww=='
        account_in = Account("Woogle", "me@woogle.com", encrypted_secret, "2000-01-01 01:01")

        dialog = EditAccountDialog(None, 1, account_in)
        dialog.account_manager.save_new_account = MagicMock(return_value=False)
        dialog.close = Mock()

        save_fields(dialog)
        # Verify results
        dialog.account_manager.save_new_account.assert_called_once()
        dialog.close.assert_not_called()
        MockMessageBox.assert_called_once()

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


if __name__ == "__main__":
    unittest.main()
