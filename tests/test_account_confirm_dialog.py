import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from account_confirm_dialog import ConfirmAccountDialog
from unittest.mock import Mock
class TestConfirmAccountDialog(unittest.TestCase):
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

    @patch('account_confirm_dialog.QMessageBox.information')
    @patch('account_confirm_dialog.AccountManager')
    def test_Accept_button(self, MockAccountManager, mockmsgbox):
        # Mock the AccountManager
        #mock_account_manager = MockAccountManager.return_value # the mock instance created when AccountManager() is called in ConfirmAccountDialog.
        dialog = ConfirmAccountDialog()

        # Replace account manager in dialog with the mock
        dialog.account_manager = MockAccountManager #mock_account_manager

        # Mock data to populate fields
        mock_account = Mock()
        mock_account.issuer = "Test Provider"
        mock_account.label = "Test Label"
        mock_account.secret = "AB34"

        # Call set_account to populate fields
        dialog.set_account(mock_account)
        dialog.accept = Mock()

        # Simulate pressing the Accept button
        dialog.save_button.click()

        # Verify save_new_account is called once with correct arguments
        MockAccountManager.save_new_account.assert_called_once_with(
            "Test Provider", "Test Label", "AB34"
        )
        mockmsgbox.assert_not_called()
        dialog.accept.assert_called_once()

        # Simulate pressing the Accept button a 2nd time with same data
        MockAccountManager.save_new_account.return_value = False
        dialog.accept = Mock()  # Reset the mock
        dialog.save_button.click()
        mockmsgbox.assert_called_once_with(dialog,"Warning","Account with same provider and user already exists")
        dialog.accept.assert_not_called()

    @patch('account_confirm_dialog.QMessageBox.information')
    @patch('account_confirm_dialog.AccountManager')
    def test_Accept_button_invalid_secret(self, MockAccountManager, mockmsgbox):
        # Mock the AccountManager
        # mock_account_manager = MockAccountManager.return_value # the mock instance created when AccountManager() is called in ConfirmAccountDialog.
        dialog = ConfirmAccountDialog()

        # Replace account manager in dialog with the mock
        dialog.account_manager = MockAccountManager  # mock_account_manager

        # Mock data to populate fields
        mock_account = Mock()
        mock_account.issuer = "Test Provider"
        mock_account.label = "Test Label"
        mock_account.secret = "invalid secret"

        # Call set_account to populate fields
        dialog.set_account(mock_account)
        dialog.accept = Mock()

        # Simulate pressing the Accept button
        dialog.save_button.click()

        # Verify save_new_account not called when key check fails
        MockAccountManager.save_new_account.assert_not_called()
        dialog.accept.assert_not_called()

        # verify the invalid secret key messagebox
        mockmsgbox.assert_called_once_with(dialog, "Error", "The secret key is invalid")


    @patch('account_confirm_dialog.AccountManager')
    def test_Decline_button(self, MockAccountManager):
        # Mock the AccountManager
        mock_account_manager = MockAccountManager.return_value # is the mock instance created when AccountManager() is called in ConfirmAccountDialog.
        dialog = ConfirmAccountDialog()

        # Replace account manager in dialog with the mock
        dialog.account_manager = mock_account_manager

        # Mock data to populate fields
        mock_account = Mock()
        mock_account.issuer = "Test Provider"
        mock_account.label = "Test Label"
        mock_account.secret = "Test Secret"

        # Call set_account to populate fields
        dialog.set_account(mock_account)

        # Simulate pressing the Decline button
        dialog.cancel_button.click()

        # Verify save_new_account is called once with correct arguments
        mock_account_manager.save_new_account.assert_not_called()



if __name__ == "__main__":
    unittest.main()
