from PyQt5.QtCore import QTimer
import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
import find_qr_codes
import unittest

class TestFind_qr_codes(unittest.TestCase):
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

    image_file = 'tests/test_find_qr_code_image.png'

    def test_scan_screen_for_qrcode(self):
         # Display a QR code from a test file
        pixmap = QPixmap(self.image_file)
        label = QLabel()
        label.setPixmap(pixmap)
        label.show()

        # Schedule a function to close the window after 1 second
        def close_window():
            # Look for the image
            results = find_qr_codes.scan_screen_for_qr_codes()
            # Verify that we got some results
            assert len(results) > 0
            label.close()

        # Create a QTimer to close the window after 1 second
        timer = QTimer()
        timer.timeout.connect(close_window)
        timer.start(500)

        # Execute the application event loop
        TestFind_qr_codes.app.exec_()
