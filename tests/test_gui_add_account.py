import unittest
from unittest.mock import patch, Mock
from PyQt5.QtWidgets import QApplication
from account_add_dialog import AddAccountDialog
from account_manager import Account, OtpRecord

class TestAddAccountDialog(unittest.TestCase):

    @patch("account_add_dialog.AccountManager")
    def test_add_account(self, MockAccountManager):
        app = QApplication([])  # Create a QApplication instance

        # Create a mock for the AccountManager
        mock_account_manager = MockAccountManager.return_value

        # Create an instance of AddAccountDialog
        dialog = AddAccountDialog()
        dialog.account_manager = mock_account_manager

        # Set values for the input fields
        dialog.provider_entry.setText("TestProvider")
        dialog.label_entry.setText("test@example.com")

        # Save button should be disabled until all fields are filled
        assert not dialog.save_button.isEnabled()
        dialog.secret_entry.setText("testsecret")
        assert dialog.save_button.isEnabled()

        # Mock the save_new_account method
        dialog.account_manager.save_new_account = Mock()

        # Click the Save button
        dialog.save_button.click()

        # Verify that save_new_account was called with the correct values
        expected_account = OtpRecord("TestProvider", "test@example.com", "testsecret")
        dialog.account_manager.save_new_account.assert_called_once_with(expected_account)

        app.quit()  # Clean up the QApplication instance

if __name__ == '__main__':
    unittest.main()