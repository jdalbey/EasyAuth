import unittest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QMessageBox, QDialog

from account_manager import Account
from qr_hunting import confirm_account, process_qr_codes

class TestQRHunting(unittest.TestCase):

    @patch("qr_hunting.QMessageBox.information")
    @patch("qr_hunting.ConfirmAccountDialog")
    @patch("qr_hunting.is_valid_secretkey")
    def test_confirm_account_ok(self, mock_is_valid_secretkey, mock_ConfirmAccountDialog, mock_information):
        # Mock a valid secret key
        mock_is_valid_secretkey.return_value = True

        # Mock the ConfirmAccountDialog
        mock_dialog_instance = MagicMock()
        mock_dialog_instance.exec_.return_value = QDialog.Accepted
        mock_ConfirmAccountDialog.return_value = mock_dialog_instance

        # Create a sample account
        account = Account(provider="TestProvider", label="TestLabel", secret="ValidSecret", last_used="")

        # Call the function
        result = confirm_account(account)

        # Assert that the dialog was displayed and accepted
        mock_is_valid_secretkey.assert_called_once_with("ValidSecret")
        mock_ConfirmAccountDialog.assert_called_once()  # Confirm dialog was created
        mock_dialog_instance.set_account.assert_called_once()
        mock_dialog_instance.exec_.assert_called_once()  # Dialog exec_ was called
        self.assertTrue(result)

    @patch("qr_hunting.QMessageBox.information")
    @patch("qr_hunting.ConfirmAccountDialog")
    @patch("qr_hunting.is_valid_secretkey")
    def test_confirm_account_cancel(self, mock_is_valid_secretkey, mock_ConfirmAccountDialog, mock_information):
        # Mock a valid secret key
        mock_is_valid_secretkey.return_value = True

        # Mock the ConfirmAccountDialog
        mock_dialog_instance = MagicMock()
        mock_dialog_instance.exec_.return_value = QDialog.Rejected
        mock_ConfirmAccountDialog.return_value = mock_dialog_instance

        # Create a sample account
        account = Account(provider="TestProvider", label="TestLabel", secret="ValidSecret", last_used="")

        # Call the function
        result = confirm_account(account)

        # Assert that the dialog was displayed and canceled
        mock_is_valid_secretkey.assert_called_once_with("ValidSecret")
        mock_dialog_instance.set_account.assert_called_once()
        self.assertFalse(result)

    @patch("qr_hunting.QMessageBox.information")
    @patch("qr_hunting.is_valid_secretkey")
    def test_confirm_account_invalid_secret(self, mock_is_valid_secretkey, mock_information):
        # Mock an invalid secret key
        mock_is_valid_secretkey.return_value = False

        # Create a sample account
        account = Account(provider="TestProvider", label="TestLabel", secret="InvalidSecret", last_used="")

        # Call the function
        result = confirm_account(account)

        mock_is_valid_secretkey.assert_called_once_with('InvalidSecret')

        # Assert that QMessageBox was shown
        mock_information.assert_called_once_with(None, 'Info', "QR code has invalid secret key.", QMessageBox.Ok)
        self.assertFalse(result)

    @patch("find_qr_codes.scan_screen_for_qr_codes")
    def test_process_qr_codes_valid_zero(self, mock_scan_screen_for_qr_codes):
        # Mock dependencies
        mock_scan_screen_for_qr_codes.return_value = []

        # Call the function
        result = process_qr_codes(False)

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
        result = process_qr_codes(True)
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
        result = process_qr_codes(False)
        self.assertTrue(result)
        # Assertions when 1 url found and Accepted
        mock_scan_screen_for_qr_codes.assert_called_once_with()

        mock_confirm_account.return_value = False
        result = process_qr_codes(False)
        self.assertFalse(result)

