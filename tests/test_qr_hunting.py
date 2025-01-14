import unittest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QMessageBox, QDialog
from qr_hunting import confirm_account, process_qr_codes

# Assume the following imports are defined in your module
# from qr_hunting import confirm_account, is_valid_secretkey, Account

class TestQRHunting(unittest.TestCase):
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
        self.assertTrue(result)

        # Assertions for the valid key branch with accepted dialog
        mock_is_valid_secretkey.assert_called_once_with("ValidSecret")
        mock_confirm_dialog.set_account.assert_called_once()

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


    @patch("find_qr_codes.scan_screen_for_qr_codes")
    def test_process_qr_codes_valid_zero(self, mock_scan_screen_for_qr_codes):
        # Mock dependencies
        mock_scan_screen_for_qr_codes.return_value = []

        # Call the function
        result = process_qr_codes(False, None)

        # Assertions when no urls found
        mock_scan_screen_for_qr_codes.assert_called_once_with()
        # if zero valid urls expect return False
        self.assertFalse(result)

    @patch("find_qr_codes.scan_screen_for_qr_codes")
    @patch("qr_hunting.QMessageBox")
    def test_process_qr_codes_valid_zero_from_find(self, MockQMessageBox, mock_scan_screen_for_qr_codes):
        mock_message_box = Mock()
        MockQMessageBox.information.return_value = mock_message_box

        # Call the function
        result = process_qr_codes(True, None)
        # if zero valid urls expect return False
        self.assertFalse(result)

        # Assertions when no urls found
        mock_scan_screen_for_qr_codes.assert_called_once_with()
        # When True is passed should get an alert
        MockQMessageBox.information.assert_called_once_with(
            None, 'Alert', "No QR code found.  Be sure the QR code is visible on your screen and try again.",
            unittest.mock.ANY
        )

    @patch("find_qr_codes.scan_screen_for_qr_codes")
    @patch("qr_hunting.confirm_account")
    def test_process_qr_codes_valid_one(self, mock_confirm_account, mock_scan_screen_for_qr_codes):
        # Mock dependencies
        mock_scan_screen_for_qr_codes.return_value = ['otpauth://totp/bobjones?secret=DITATUPFVUIJK7X7&issuer=Gargle.com','badurl']
        mock_confirm_account.return_value = True
        # Call the function
        result = process_qr_codes(False, None)
        self.assertTrue(result)
        # Assertions when 1 url found and Accepted
        mock_scan_screen_for_qr_codes.assert_called_once_with()

        mock_confirm_account.return_value = False
        result = process_qr_codes(False, None)
        self.assertFalse(result)



if __name__ == "__main__":
    unittest.main()
