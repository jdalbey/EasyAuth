from PyQt5.QtCore import QTimer
import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
import find_qr_codes

class TestFind_qr_codess:
    image_file = 'test_find_qr_code_image.png'

    def test_scan_screen_for_qrcode(self):

        # First display a QR code to hunt for
        app = QApplication(sys.argv)
        pixmap = QPixmap(self.image_file)
        label = QLabel()
        label.setPixmap(pixmap)
        label.show()

        # Schedule a function to close the window after 1 second
        def close_window():
            # Look for the image
            results = find_qr_codes.scan_screen_for_qr_codes()
            assert len(results) > 0
            label.close()

        # Create a QTimer to close the window after 1 second
        timer = QTimer()
        timer.timeout.connect(close_window)
        timer.start(1000)

        # Execute the application event loop
        app.exec_()