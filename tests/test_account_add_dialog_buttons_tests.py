import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from account_add_dialog import AddAccountDialog

class TestAddAccountDialogButtons(unittest.TestCase):
#Using setUpClass and tearDownClass ensures that QApplication is created once for the entire test suite, preventing multiple instances.
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

    @patch("account_add_dialog.process_qr_codes")  # Patch where the function is used
    def test_Find_QRcode_button_success(self, MockProcessQRcodes):
        dialog = AddAccountDialog()

        # Mock the qr_hunting function (because we don't want to actually save the new data)
        MockProcessQRcodes.return_value = True  # is the mock instance created when process_qrcodes is called in AddAccountDialog.
        dialog.accept = MagicMock()  # Mock the accept method of the dialog

        # Simulate pressing the Find QR code button
        dialog.find_qr_btn.click()

        # Process events explicitly to ensure the button click triggers the signal and slot
        #QTest.qWait(100)  # Wait for 100 ms to give time for the signal to be processed
        #self.app.processEvents()  # Ensure all pending events are processed

        # Verify process_qr_codes is called once with correct arguments
        MockProcessQRcodes.assert_called_once()

        dialog.accept.assert_called_once()  # Ensure accept() was not called

    @patch("account_add_dialog.process_qr_codes")  # Patch where the function is used
    def test_Find_QRcode_button_failure(self, MockProcessQRcodes):
        dialog = AddAccountDialog()

        # Mock the qr_hunting function to return False (indicating failure)
        MockProcessQRcodes.return_value = False  # Mocked return value
        dialog.accept = MagicMock()  # Mock the accept method of the dialog

        # Simulate pressing the Find QR code button
        dialog.find_qr_btn.click()

        # Verify that process_qr_codes is called once with correct arguments
        MockProcessQRcodes.assert_called_once()

        # Mock the accept() method to check if the dialog closes
        dialog.accept.assert_not_called()  # Ensure accept() was not called


if __name__ == "__main__":
    unittest.main()
