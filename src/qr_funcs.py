import logging

import otp_funcs
from account_mgr import OtpRecord
import pyotp
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog
from pyzbar.pyzbar import decode
from PIL import ImageGrab

from qr_selection_dialog import QRselectionDialog

""" Utilities for scanning QR codes from the screen. """

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
    """ Obtain the URI data from QR codes found on the screen.
     If no QR codes could be found, displays an alert message.
     If multiple QR codes were found, presents a selection dialog.
     If a single QR code was found, returns an OTP record with the data from the QR code.
     """
    # first go find_qr_codes
    urls = scan_screen_for_qr_codes()
    # Show alert if no QR codes found.
    if len(urls) == 0:
        QMessageBox.information(parent, 'Alert',
"""No QR code found.  Be sure the complete QR code with the secret key is visible on your screen and try again.
(The provider will show a QR code in your web browser during enabling of two-factor authentication.)
""", QMessageBox.Ok)
        return
    logging.debug(f"obtain_qr_codes() found these URIs: {urls}")

    # Examine each url to see if it is an otpauth protocol and reject others
    otpauth_list = [item for item in urls if item.startswith('otpauth://totp')]
    if len(otpauth_list) < len(urls):
        QMessageBox.information(parent, 'Alert',
"""QR code found but not for two-factor authentication.  Be sure the QR code with the secret key is visible on your screen and try again.
(The provider will show a QR code in your web browser during enabling of two-factor authentication.)
""", QMessageBox.Ok)
        return
    # Try to parse each url.  Put the fields into an OtpRecord and append to displaylist.
    display_list = []
    invalid_messages = ""
    for uri in otpauth_list:
        try:
            totp_obj = pyotp.parse_uri(uri)
        except ValueError as e:
            invalid_messages += (str(e) + "\n")
            continue  # skip invalid URI's
        # Validate issuer field
        issuer = totp_obj.issuer
        if issuer == None:
            invalid_messages += "Missing issuer name.\n"
            continue
        label = totp_obj.name
        # Validate secret key
        secret_key = totp_obj.secret
        if not otp_funcs.is_valid_secretkey(secret_key):
            invalid_messages += 'Invalid secret key'
            continue
        # Validate digits field
        digits = totp_obj.digits
        if digits != 6:
            invalid_messages += "EasyAuth is limited to 6-digit TOTP codes.\n"
            continue
        account = OtpRecord(issuer, label, secret_key)

        logging.debug(f"obtain_qr_codes() parsing produced: {issuer} {label} ")
        display_list.append(account)
    # How many valid URI's do we have?
    if len(display_list) == 0:
        QMessageBox.information(parent, 'Alert',
"EasyAuth couldn't process the QR code found.  Reason: \n" +
invalid_messages
, QMessageBox.Ok)
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
    """ Obtain QR code data from an image file. """
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
        totp_obj = pyotp.parse_uri(url)
        print ("TOTP: ",totp_obj.now())
    #url = 'otpauth://totp/PayPal:steve@dottotech.com?secret=DITATUPFVUIJK7X7&issuer=PayPal'
    #url = 'otpauth://totp/bobjones?secret=DITATUPFVUIJK7X7&issuer=Gargle.com'
