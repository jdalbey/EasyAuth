import os
import unittest
from unittest.mock import patch, Mock, MagicMock

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

from account_add_dialog import AddAccountDialog
from account_edit_dialog import EditAccountDialog
from account_manager import AccountManager, OtpRecord, Account
import common_dialog_funcs
import provider_search_dialog
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

        common_dialog_funcs.save_fields(dialog)
        # Verify results
        dialog.account_manager.save_new_account.assert_called_once()
        dialog.close.assert_not_called()
        MockMessageBox.assert_called_once()

    @patch('common_dialog_funcs.ProviderSearchDialog') # because that's where it is *used*
    def test_provider_lookup(self, mockDialog):
        """ Open ProviderSearchDialog, check that it returns selected provider
        and places it in provider entry field """

        # Create mock dialog instance
        mock_dialog = mockDialog.return_value

        # Set return value for exec_ to simulate user accepting the dialog
        mock_dialog.exec_.return_value = QDialog.Accepted

        # Set return value for get_selected_provider
        mock_dialog.get_selected_provider.return_value = "Woogle"

        # Create AddAccountDialog instance
        add_dlg = AddAccountDialog()

        # Call function that opens the dialog
        common_dialog_funcs.provider_lookup(add_dlg)

        # Ensure exec_ was called once (dialog was opened)
        mock_dialog.exec_.assert_called_once()

        # Verify that the selected provider was set correctly
        assert add_dlg.provider_entry.text() == "Woogle"

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
