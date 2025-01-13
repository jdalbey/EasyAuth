import unittest
from unittest.mock import patch, Mock

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QDialog
from account_add_dialog import AddAccountDialog

class TestAddAccountDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize QApplication only once for all tests
        cls.app = QApplication([])

    @patch("account_add_dialog.process")  # Correct module path for process
    @patch("account_add_dialog.ConfirmAccountDialog")  # Correct module path for ConfirmAccountDialog
    def test_get_qr_code_success(self, MockConfirmAccountDialog, mock_process):
        # Arrange
        mock_process.return_value = True  # Simulate a successful QR code processing
        mock_dialog_instance = Mock(spec=QDialog)
        MockConfirmAccountDialog.return_value = mock_dialog_instance

        # Create the dialog instance
        dialog = AddAccountDialog()
        dialog.accept = Mock()  # Mock the accept method of the dialog

        # Act
        dialog.get_qr_code()

        # Assert
        mock_process.assert_called_once_with(True, mock_dialog_instance)
        dialog.accept.assert_called_once()  # Ensure accept() is called when process succeeds

    @patch("account_add_dialog.process")  # Correct module path for process
    @patch("account_add_dialog.ConfirmAccountDialog")  # Correct module path for ConfirmAccountDialog
    def test_get_qr_code_failure(self, MockConfirmAccountDialog, mock_process):
        # Arrange
        mock_process.return_value = False  # Simulate a failed QR code processing
        mock_dialog_instance = Mock(spec=QDialog)
        MockConfirmAccountDialog.return_value = mock_dialog_instance

        # Create the dialog instance
        dialog = AddAccountDialog()
        dialog.accept = Mock()  # Mock the accept method of the dialog

        # Act
        dialog.get_qr_code()

        # Assert
        mock_process.assert_called_once_with(True, mock_dialog_instance)
        dialog.accept.assert_not_called()  # Ensure accept() is NOT called when process fails

if __name__ == "__main__":
    unittest.main()
