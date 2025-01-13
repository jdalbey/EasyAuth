import unittest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QMessageBox, QDialog
from qr_hunting import confirm_account

# Assume the following imports are defined in your module
# from qr_hunting import confirm_account, is_valid_secretkey, Account

class TestConfirmAccount(unittest.TestCase):
    @patch("qr_hunting.is_valid_secretkey")
    @patch("qr_hunting.QMessageBox")
    @patch("qr_hunting.QDialog")
    def test_confirm_account_invalid_secretkey(self, MockQDialog, MockQMessageBox, mock_is_valid_secretkey):
        # Mock dependencies
        mock_is_valid_secretkey.return_value = False  # Simulate invalid secret key
        mock_message_box = Mock()
        MockQMessageBox.information.return_value = mock_message_box

        # Create mock account and dialog
        mock_account = Mock(provider="TestProvider", label="TestLabel", secret="InvalidSecret")
        mock_confirm_dialog = Mock()

        # Call the function
        result = confirm_account(mock_account, mock_confirm_dialog)
        print (f"Test1 result: {result}")

        # Debugging: Check if QMessageBox.information was called
        print(MockQMessageBox.information.call_args_list)
        # Assertions for the invalid key branch
        mock_is_valid_secretkey.assert_called_once_with("InvalidSecret")
        print ("passed first assert")
        MockQMessageBox.information.assert_called_once_with(
            None, 'Info', "QR code has invalid secret key.", unittest.mock.ANY
        )
        self.assertFalse(result)

    # Don't mock entire QDialog, just the methods we need
    @patch("qr_hunting.is_valid_secretkey")
    def test_valid_secretkey_confirm_account_accepted(self, mock_is_valid_secretkey):
        # Mock dependencies
        from PyQt5.QtWidgets import QDialog

        mock_is_valid_secretkey.return_value = True  # Simulate valid secret key
        # Create a mock dialog and configure exec_() to return QDialog.Accepted
        mock_confirm_dialog = Mock()
        mock_confirm_dialog.exec_.return_value = QDialog.Accepted  # Use the original constant

        # Create mock account and dialog
        mock_account = Mock(provider="TestProvider", label="TestLabel", secret="ValidSecret")


        # Call the function - expect True
        result = confirm_account(mock_account, mock_confirm_dialog)
        print(f"Test2 result: {result},  QDialog.Accepted: {QDialog.Accepted}")
        # Debugging output
        print("exec_() returned:", mock_confirm_dialog.exec_())

        # Assertions for the valid key branch with accepted dialog
        mock_is_valid_secretkey.assert_called_once_with("ValidSecret")
        mock_confirm_dialog.set_account.assert_called_once()
        self.assertTrue(result)

    @patch("qr_hunting.is_valid_secretkey")
    @patch("qr_hunting.QDialog")
    def test_valid_secretkey_confirm_account_rejected(self, MockQDialog, mock_is_valid_secretkey):
        # Mock dependencies
        mock_is_valid_secretkey.return_value = True  # Simulate valid secret key
        mock_dialog_instance = Mock()
        mock_dialog_instance.exec_.return_value = QDialog.Rejected
        MockQDialog.return_value = mock_dialog_instance

        # Create mock account and dialog
        mock_account = Mock(provider="TestProvider", label="TestLabel", secret="ValidSecret")
        mock_confirm_dialog = Mock()

        # Call the function
        result = confirm_account(mock_account, mock_confirm_dialog)

        # Assertions for the valid key branch with rejected dialog
        mock_is_valid_secretkey.assert_called_once_with("ValidSecret")
        mock_confirm_dialog.set_account.assert_called_once()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
