# Detects one or more QR codes on the screen.
from account_manager import OtpRecord
import pyotp
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pyzbar.pyzbar import decode
from PIL import ImageGrab

def scan_screen_for_qr_codes():
    """
    Scans the display screen for QR codes and decodes them.

    Returns:
        list: A list of decoded data from QR codes found on the screen.

    """
    # Take a screenshot of the current screen
    bbox = None  # take fullscreen
    screenshot = ImageGrab.grab(bbox)

    # Convert screenshot to a format usable by pyzbar
    screenshot = screenshot.convert('RGB')
    #screenshot.save("/tmp/screenshotqrcodes.png")  # diagnostic: save the image to a file

    # Detect and decode QR codes
    qr_codes = decode(screenshot)

    # Extract data from the detected QR codes
    results = [qr_code.data.decode('utf-8') for qr_code in qr_codes if qr_code.data]
    # Return a list, one item for each code.
    return results

def open_qr_image(parent=None):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(parent, f"Open QR image", "",
                                               "PNG Files (*.png);;All Files (*)", options=options)
    if file_path:
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
            # Read image file
            qr_image = Image.open(file_path)
            # decode QR codes
            qr_codes = decode(qr_image)
            # Extract data from the detected QR codes
            results = [qr_code.data.decode('utf-8') for qr_code in qr_codes if qr_code.data]
            if len(results) == 0:
                QMessageBox.critical(parent, "Error", f"QR image not recognized.")
                return
            # results is a list
            if len(results) > 1:
                QMessageBox.critical(parent, "Operation failed", f"The image contained multiple QR codes.\n " +
                                     "The program is currently unable to process more than one QR code per image.")
                return
            # Parse the URI
            try:
                totp_obj = pyotp.parse_uri(results[0])
            except ValueError as e:
                QMessageBox.critical(parent, "Error", f"QR code invalid {e}")
                return
            otprec = OtpRecord(totp_obj.issuer, totp_obj.name, totp_obj.secret)
            return otprec

        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to read QR image: {e}")


""" Reference: 2FA QR generator: https://stefansundin.github.io/2fa-qr/ """
if __name__ == '__main__':
    urls = scan_screen_for_qr_codes()
    for url in urls:
        print(url)
    #url = 'otpauth://totp/PayPal:steve@dottotech.com?secret=DITATUPFVUIJK7X7&issuer=PayPal'
    #url = 'otpauth://totp/bobjones?secret=DITATUPFVUIJK7X7&issuer=Gargle.com'
