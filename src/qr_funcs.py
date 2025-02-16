# Detects one or more QR codes on the screen.
import logging

from account_manager import OtpRecord
import pyotp
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog
from pyzbar.pyzbar import decode
from PIL import ImageGrab

from qr_selection_dialog import QRselectionDialog


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

def obtain_qr_codes(parent):
    # We aren't going to do auto scan in v0.3 so I think this argument is obsolete.
    # first go find_qr_codes
    urls = scan_screen_for_qr_codes()
    logging.debug(f"obtain_qr_codes() found these URIs: {urls}")
    # Examine each url to see if it is an otpauth protocol and reject others
    otpauth_list = [item for item in urls if item.startswith('otpauth://totp')]
    # Try to parse each url.  Put the fields into an OtpRecord and append to displaylist.
    display_list = []
    for uri in otpauth_list:
        try:
            totp_obj = pyotp.parse_uri(uri)
        except ValueError as e:
            continue  # skip invalid URI's
        issuer = totp_obj.issuer
        label = totp_obj.name
        secret_key = totp_obj.secret
        account = OtpRecord(issuer, label, secret_key)
        # TODO: Extract the advanced parameters if they exists
        logging.debug(f"obtain_qr_codes() parsing produced: {issuer} {label} ")
        display_list.append(account)
    # How many valid URI's do we have?
    if len(display_list) == 0:
        QMessageBox.information(parent, 'Alert',
"""No QR code found.  Be sure the QR code is visible on your screen and try again.
(The provider will show a QR code in your web browser during enabling of two-factor authentication.)
""", QMessageBox.Ok)
        return
    if len(display_list) == 1:
        return display_list[0]
    # Wow, we got more than one QR code
    if len(display_list) > 1:
        # Ask user to select one account from the list
        dialog = QRselectionDialog(display_list, parent)
        # The dialog.exec_() call will block execution until the dialog is closed
        if dialog.exec_() == QDialog.Accepted:
            selected_account = dialog.get_selected_account()
            # If user made a selection,
            if selected_account:
                logging.debug(
                    f"QRselectionDialog returned: {selected_account.issuer} - {selected_account.label}")
                return selected_account

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
