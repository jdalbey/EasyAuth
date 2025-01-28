import unittest
from unittest.mock import patch, Mock

from PyQt5.QtWidgets import QApplication, QDialog
from account_add_dialog import AddAccountDialog
from account_manager import AccountManager, OtpRecord

class TestAddAccountDialog(unittest.TestCase):
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

    @patch.object(AddAccountDialog, "obtain_qr_codes")
    def test_qr_code_btn(self, mock_obtain):
        # Create the dialog instance
        dialog = AddAccountDialog()
        dialog.accept = Mock()  # Mock the accept method of the dialog

        # Act
        dialog.btn_scanQR.click()

        # Assert
        mock_obtain.assert_called_once_with(True)

        # TODO: Assert that trying to add a duplicate shows a messagebox

    @patch("account_add_dialog.AccountManager")
    def test_add_account(self, MockAccountManager):
        # Create a mock for the AccountManager
        mock_account_manager = MockAccountManager.return_value

        # Create an instance of AddAccountDialog
        dialog = AddAccountDialog()
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

if __name__ == "__main__":
    unittest.main()
