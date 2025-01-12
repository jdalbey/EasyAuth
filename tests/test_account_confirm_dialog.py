import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from account_confirm_dialog import ConfirmAccountDialog
from unittest.mock import Mock
class TestConfirmAccountDialog(unittest.TestCase):
    def setUp(self):
        # Required for QApplication to initialize PyQt components
        self.app = QApplication([])

    @patch('account_confirm_dialog.AccountManager')
    def test_Accept_button(self, MockAccountManager):
        # Mock the AccountManager
        mock_account_manager = MockAccountManager.return_value # is the mock instance created when AccountManager() is called in ConfirmAccountDialog.
        dialog = ConfirmAccountDialog()

        # Replace account manager in dialog with the mock
        dialog.account_manager = mock_account_manager

        # Mock data to populate fields
        mock_account = Mock()
        mock_account.provider = "Test Provider"
        mock_account.label = "Test Label"
        mock_account.secret = "Test Secret"

        # Call set_account to populate fields
        dialog.set_account(mock_account)

        # Simulate pressing the Accept button
        dialog.save_button.click()

        # Verify save_new_account is called once with correct arguments
        mock_account_manager.save_new_account.assert_called_once_with(
            "Test Provider", "Test Label", "Test Secret"
        )

    @patch('account_confirm_dialog.AccountManager')
    def test_Decline_button(self, MockAccountManager):
        # Mock the AccountManager
        mock_account_manager = MockAccountManager.return_value # is the mock instance created when AccountManager() is called in ConfirmAccountDialog.
        dialog = ConfirmAccountDialog()

        # Replace account manager in dialog with the mock
        dialog.account_manager = mock_account_manager

        # Mock data to populate fields
        mock_account = Mock()
        mock_account.provider = "Test Provider"
        mock_account.label = "Test Label"
        mock_account.secret = "Test Secret"

        # Call set_account to populate fields
        dialog.set_account(mock_account)

        # Simulate pressing the Decline button
        dialog.cancel_button.click()

        # Verify save_new_account is called once with correct arguments
        mock_account_manager.save_new_account.assert_not_called()

    def tearDown(self):
        self.app.quit()


if __name__ == "__main__":
    unittest.main()
