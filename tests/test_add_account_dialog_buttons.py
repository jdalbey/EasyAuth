import unittest
from unittest.mock import patch, Mock

from PyQt5.QtWidgets import QApplication, QDialog
from account_add_dialog import AddAccountDialog

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

    @patch("account_add_dialog.process_qr_codes")  # Correct module path for process
    def test_qr_code_btn_success(self, mock_process):
        # Arrange
        mock_process.return_value = True  # Simulate a successful QR code processing

        # Create the dialog instance
        dialog = AddAccountDialog()
        dialog.accept = Mock()  # Mock the accept method of the dialog

        # Act
        dialog.find_qr_btn.click()

        # Assert
        mock_process.assert_called_once_with(True)
        dialog.accept.assert_called_once()  # Ensure accept() is called when process succeeds

        # TODO: Assert that trying to add a duplicate shows a messagebox

    @patch("account_add_dialog.process_qr_codes")  # Correct module path for processbv
    def test_qr_code_btn_reject(self, mock_process):
        # Arrange
        mock_process.return_value = False  # Simulate a failed QR code processing

        # Create the dialog instance
        dialog = AddAccountDialog()
        dialog.accept = Mock()  # Mock the accept method of the dialog

        # Act
        dialog.find_qr_btn.click()

        # Assert
        mock_process.assert_called_once_with(True)
        dialog.accept.assert_not_called()  # Ensure accept() is NOT called when process fails

if __name__ == "__main__":
    unittest.main()
