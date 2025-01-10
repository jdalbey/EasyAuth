import pyotp
import json
from src.find_qr_codes import scan_screen_for_qr_codes
from dev_archive import crypto_utils
import urllib.parse

import base64
import re


def is_valid_secretkey(secret: str) -> bool:
    """
    Validate that the secret key is a valid Base32-encoded string.
    This checks that the string contains only valid Base32 characters
    and the length is a valid multiple of 8 (after considering padding).
    """
    base32_regex = re.compile("^[A-Z2-7=]+$")  # Base32 chars + padding (`=`)

    # Check if the string matches Base32 characters
    if not base32_regex.match(secret):
        return False

    # Check the padding and length, Base32 padding should be 0, 1, or 2 `=`
    if secret.count('=') > 2:
        return False

    # Try decoding and checking if it succeeds
    try:
        decoded = base64.b32decode(secret, casefold=True)
        # Ensure the decoded result is not all zero bytes
        if len(decoded) == 0 or all(byte == 0 for byte in decoded):
            return False
        return True
    except Exception as e:
        return False



"""Ref: https://2fa.directory/api """
class OTPManager:
    def __init__(self):
        self.accounts_file = '../src/vault.json'

    def load_accounts(self):
        try:
            with open(self.accounts_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_accounts(self, accounts):
        with open(self.accounts_file, 'w') as f:
            json.dump(accounts, f)

    def generate_otp(self,label):
        accounts = self.load_accounts()
        for account in accounts:
            if account['label'] == label:
                secret = crypto_utils.decrypt(account['secret'])
                totp = pyotp.TOTP(secret)

                return totp.now()
        return None
# Remember that the issuer and account name cannot contain a colon (: or %3A)  or a parenthesis
    def add_account(self):
        url = scan_screen_for_qr_codes()
        if len(url) == 1:
            # A valid QR code yields a URI of this form:
            #'otpauth://totp/{Issuer}:{name}?secret={shared key}&issuer={Issuer}'
            totp_obj = pyotp.parse_uri(url[0])
            issuer = totp_obj.issuer
            label = totp_obj.name
            secret_key = totp_obj.secret
            # Extract the time period parameter if it exists
            parsed_uri = urllib.parse.urlparse(url[0])
            query_params = urllib.parse.parse_qs(parsed_uri.query)
            period = query_params.get('period', [None])[0]
            print (f"Scanned QR code: {issuer} {label} ")
            # check for url's not from a valid QR code.
            if not is_valid_secretkey(secret_key):
                print ("Secret key not valid")
                exit()
            encrypted_secret = crypto_utils.encrypt(secret_key)
            accounts = self.load_accounts()
            entry = {'issuer': issuer,'label': label, 'secret': encrypted_secret}
            accounts.append(entry)
            self.save_accounts(accounts)
            return entry
        else:
            print ("Scan fail")
            exit()