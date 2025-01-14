import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from account_add_dialog import AddAccountDialog
from unittest.mock import Mock

from models_singleton import Account


class TestManualAddAccountDialog(unittest.TestCase):
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

    @patch('account_add_dialog.AccountManager')
    def test_Accept_button(self, MockAccountManager):
        dialog = AddAccountDialog()
        # Mock the AccountManager (because we don't want to actually save the new data)
        mock_account_manager = MockAccountManager.return_value # is the mock instance created when AccountManager() is called in ConfirmAccountDialog.

        # Replace account manager in dialog with the mock
        dialog.account_manager = mock_account_manager
        # populate fields
        account = Account("Woogle", "me@woogle.com", "AB34", "2000-01-01 01:01")
        dialog.set_account(account)

        # Simulate pressing the Accept button
        dialog.save_button.click()

        # Verify save_new_account is called once with correct arguments
        mock_account_manager.save_new_account.assert_called_once_with(
            "Woogle", "me@woogle.com", "AB34"
        )


    @patch('account_add_dialog.AccountManager')
    def test_Decline_button(self, MockAccountManager):
        # Mock the AccountManager
        dialog_manager = MockAccountManager.return_value # is the mock instance created when AccountManager() is called in ConfirmAccountDialog.
        dialog = AddAccountDialog()

        # Replace account manager in dialog with the mock
        dialog.account_manager = dialog_manager

        # Verify save button is disabled until fields are populated
        assert dialog.save_button.isEnabled() == False
        # populate fields
        account = Account("Woogle", "me@woogle.com", "AB34", "2000-01-01 01:01")
        dialog.set_account(account)
        assert dialog.save_button.isEnabled() == True

        # Simulate pressing the Decline button
        dialog.cancel_button.click()

        # Verify save_new_account is called once with correct arguments
        dialog_manager.save_new_account.assert_not_called()


if __name__ == "__main__":
    unittest.main()
