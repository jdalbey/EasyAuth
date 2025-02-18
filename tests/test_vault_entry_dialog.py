import unittest
from unittest.mock import patch, Mock
from PyQt5.QtWidgets import QApplication
from account_manager import AccountManager, OtpRecord
from appconfig import AppConfig
from vault_entry_dialog import VaultEntryDialog
from view import AppView

class TestVaultEntryDialog(unittest.TestCase):

    @patch("vault_entry_dialog.AccountManager")
    def test_save_new_account(self, MockAccountManager):
        # Create a mock for the AccountManager
        mock_account_manager = MockAccountManager.return_value

        # Create an instance of AddAccountDialog
        dialog = VaultEntryDialog(AppView(self.app))
        dialog.account_manager = mock_account_manager

        # Set values for the input fields
        dialog.provider_entry.setText("TestProvider")
        dialog.label_entry.setText("test@example.com")

        # Save button should be disabled until all fields are filled
        assert not dialog.btn_Save.isEnabled()
        dialog.secret_entry.setText("testsecret")
        assert dialog.btn_Save.isEnabled()

        # Mock the save_new_account method
        dialog.account_manager.save_new_account = Mock()

        # Click the Save button
        dialog.btn_Save.click()

        # Verify that save_new_account was called with the correct values
        expected_account = OtpRecord("TestProvider", "test@example.com", "testsecret")
        dialog.account_manager.save_new_account.assert_called_once_with(expected_account)


    @patch('account_add_dialog.AccountManager')
    def test_Cancel_button(self, MockAccountManager):
        # Mock the AccountManager
        dialog_manager = MockAccountManager.return_value # is the mock instance created when AccountManager() is called in ConfirmAccountDialog.
        dialog = VaultEntryDialog(AppView(self.app))

        # Replace account manager in dialog with the mock
        dialog.account_manager = dialog_manager

        # Verify save button is disabled until fields are populated
        assert dialog.btn_Save.isEnabled() == False
        # populate fields
        dialog.provider_entry.setText("Woogle")
        dialog.label_entry.setText("me@woogle.com")
        dialog.secret_entry.setText("AB34")

        assert dialog.btn_Save.isEnabled() == True

        # Simulate pressing the Decline button
        dialog.btn_Cancel.click()

        # Verify save_new_account is called once with correct arguments
        dialog_manager.save_new_account.assert_not_called()

    def test_learn_more(self):
        """ Test link content, not that it actually opens the browser page """
        dialog = VaultEntryDialog(AppView(self.app))
        link = dialog.label_LearnMore
        linktext = link.text()
        expected = '<a href="https://github.com/jdalbey/EasyAuth/wiki'
        assert linktext.startswith(expected)

    # Using setUpClass and tearDownClass ensures that QApplication is created once for the entire test suite, preventing multiple instances.
    @classmethod
    def setUpClass(cls):
        # QApplication is created once for the entire test suite
        cls.app = QApplication([])
        cls.appconfig = AppConfig()

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
