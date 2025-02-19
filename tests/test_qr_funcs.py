from unittest.mock import patch, Mock

from PyQt5.QtCore import QTimer
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QDialog
from PyQt5.QtGui import QPixmap
import qr_funcs
import unittest

from account_mgr import OtpRecord


class Test_qr_funcss(unittest.TestCase):
    image_file = 'tests/test_data/img_qr_code_single.png'

    def test_scan_screen_for_qrcode(self):
        # Schedule a function to close the window after 1 second
        def grab_code():
            # Look for the image
            results = qr_funcs.scan_screen_for_qr_codes()
            # close the window with the qr code
            label.close()
            # Verify that we got some results
            assert len(results) > 0
            # Examine each visible QR code
            for result in results:
                if result == 'otpauth://totp/boogum%40badmail.com?secret=bogus&issuer=Bogus':
                    return
            assert False,  "we didn't find the target QR code"


        # Display a QR code from a test file
        pixmap = QPixmap(self.image_file)
        label = QLabel()
        label.setPixmap(pixmap)
        label.show()
        # Create a QTimer to close the window after 1 second
        timer = QTimer()
        timer.timeout.connect(grab_code)
        timer.start(500)

        # Execute the application event loop
        Test_qr_funcss.app.exec_()

    @patch('qr_funcs.QRselectionDialog')
    @patch('qr_funcs.QMessageBox.information')
    @patch("qr_funcs.scan_screen_for_qr_codes")
    def test_obtain_qr_code(self, mock_find, MockMessageBox, mock_SelectionDialog):
        # Case 1: no QR code is visible
        mock_find.return_value = ([])
        result = qr_funcs.obtain_qr_codes(self)
        assert result == None
        # Should show an alert saying no qr code found
        MockMessageBox.assert_called_once()

        # Case 2: image had one QR code
        mock_find.return_value = (['otpauth://totp/boogum%40badmail.com?secret=bogus&issuer=Bogus'])
        # Should process the URL and fill in the field
        result = qr_funcs.obtain_qr_codes(self)
        assert result.issuer == "Bogus"

        #Case 3: image had two QR codes - doesn't work, doesn't mock selection dialog
        mock_find.return_value = (['otpauth://totp/boogum%40badmail.com?secret=bogus&issuer=Bogus',
                                    'otpauth://totp/me@mail.com?secret=bogus&issuer=Someone'])

        mock_dialog = mock_SelectionDialog.return_value
        mock_dialog.exec_.return_value = QDialog.Accepted
        # Simulate passing an account list to the constructor
        account_list = [
            OtpRecord('Someone', 'me@mail.com', 'bogus').toAccount(),
            OtpRecord('Bogus', 'boogum@badmail.com', 'bogus').toAccount()
        ]
        mock_dialog.get_selected_account.return_value = account_list[0]
        # Should process the URL and fill in the field
        result = qr_funcs.obtain_qr_codes(self)
        assert result.issuer == "Someone"

    @patch('qr_funcs.QFileDialog.getOpenFileName')
    def test_open_qr_image(self, mock_openfile):
        """ Test successful image open """
        # Set up the image file to be opened
        mock_openfile.return_value = (self.image_file,'')
        result = qr_funcs.open_qr_image()
        assert result.issuer == "Bogus"

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

