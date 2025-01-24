import pyotp
from PyQt5.QtWidgets import QDialog, QMessageBox

import find_qr_codes
from QRselectionDialog import QRselectionDialog
from account_manager import Account
from account_confirm_dialog import ConfirmAccountDialog
from otp_funcs import is_valid_secretkey
import logging

def fetch_qr_code():
    """ Look for a QR code.
    @param automatic True if auto scan for QR code setting is true
    @param confirm_dialog the dialog to be used to ask the user to confirm the QR code that was found"""
    logging.debug ("starting qr hunt")
    if process_qr_codes(False):
        # confirm returned True
        logging.debug("# We haven't opened the dialog yet but got a confirmed code so we can just bail out.")
        return True
    logging.debug ("Didn't get a QR code, showing dialog next.")
    # Either we didn't find any qr codes or auto_find is turned off
    return False

def confirm_account(account): #, confirm_dialog):
    # check selection has valid secret key.
    logging.debug(f"Checking validity of code for {account.issuer}: {account.secret}")
    if not is_valid_secretkey(account.secret):
        logging.debug ("QR code invalid key")
        # if not valid secret key show message box then return to blank account_add form.
        reply = QMessageBox.information (None, 'Info', "QR code has invalid secret key.",QMessageBox.Ok)
    else:
        # if valid key place the fields from that account into the Confirm dialog form field.
        fields = Account(account.issuer, account.label, account.secret, "")
        current_dialog = ConfirmAccountDialog()
        current_dialog.set_account(fields)
        if current_dialog.exec_() == QDialog.Accepted:
            logging.debug (f"Confirm dialog was accepted.")
            #accept() # for case where we were called from Find QR button
            return True
    return False

def process_qr_codes(called_from_Find_btn):
    # first go find_qr_codes
    urls = find_qr_codes.scan_screen_for_qr_codes()
    logging.debug (f"Process got urls: {urls}")
    # Examine each url to see if it is an otpauth protocol and reject others
    otpauth_list = [item for item in urls if item.startswith('otpauth://totp')]
    # Try to parse each url.  Put the fields into an account and append to displaylist.
    display_list = []
    for uri in otpauth_list:
        try:
            totp_obj = pyotp.parse_uri(uri)
        except ValueError as e:
            continue  # skip invalid URI's
        issuer = totp_obj.issuer
        name = totp_obj.name
        secret_key = totp_obj.secret
        account = Account(issuer,name,secret_key,"")
        # TODO: Extract the advanced parameters if they exists
        logging.debug(f"In AddDialog: Scanned QR code: {issuer} {name} ")
        display_list.append(account)
    # How many valid URI's do we have?
    if len(display_list) == 0:
        # This should only be shown during a requested find, not an automatic one.
        if called_from_Find_btn:  # we might have got here from Find button even though auto_hunt was on and failed.
            QMessageBox.information(None, 'Alert',
"""No QR code found.  Be sure the QR code is visible on your screen and try again.
(The provider will show a QR code in your web browser during enabling of two-factor authentication.)
""" , QMessageBox.Ok)
            return False # no QR
    if len(display_list) == 1:
        confirm_code = confirm_account(display_list[0])
        logging.debug (f"Found 1 QR code and confirm dialog returned {confirm_code}")
        return confirm_code # True if accepted, False if declined
    # Wow, we got more than one QR code
    if len(display_list) > 1:
        # Ask user to select one account from the list
        dialog = QRselectionDialog(display_list, None)
        # The dialog.exec_() call will block execution until the dialog is closed
        if dialog.exec_() == QDialog.Accepted:
            selected_account = dialog.get_selected_account()
            # If user made a selection,
            if selected_account:
                logging.debug(f"Selected Account: {selected_account.issuer} - {selected_account.label}")
                return confirm_account(selected_account)

    return False


