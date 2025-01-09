import logging
import pyotp
from otp_manager import is_valid_secretkey
from models import AccountManager, Account
from secrets_manager import SecretsManager
from otp_manager import OTPManager
from find_qr_codes import scan_screen_for_qr_code

class AppController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.account_manager = AccountManager()
        self.secrets_manager = SecretsManager()
        self.otp_manager = OTPManager(self.secrets_manager)
        self.view = None  # This will be set by the view using our set_view() method

    def set_view(self, view):
        self.view = view
        
    def get_accounts(self):
        return self.account_manager.accounts

    def get_provider_icon_name(self, provider):
        return self.account_manager.get_provider_icon_name(provider)

    def update_account(self, index, account):
        """@pre account.secret is encrypted. """
        print (f"entering controller update account with {index} {account.provider}")
        #encrypted_secret = self.secrets_manager.encrypt(account.secret)
        #account.secret = encrypted_secret
        self.account_manager.update_account(index, account)
        print(f"Updated account: {index} {account.provider} ({account.label})")

    def delete_account(self,account):
        #TODO: Fix issues with confirmation dialog appearin beneath edit window
        self.account_manager.delete_account(account)
    def generate_qr_code(self, account):
        return self.otp_manager.generate_qr_code(account)
    def find_qr_code(self):
        url = scan_screen_for_qr_code()
        if len(url) == 1:
            # A valid QR code yields a URI of this form:
            # 'otpauth://totp/{Issuer}:{name}?secret={shared key}&issuer={Issuer}'
            totp_obj = pyotp.parse_uri(url[0])
            issuer = totp_obj.issuer
            label = totp_obj.name
            secret_key = totp_obj.secret
            # TODO: Extract the time period parameter if it exists
            print(f"Scanned QR code: {issuer} {label} ")
            # check for url's not from a valid QR code.
            if not is_valid_secretkey(secret_key):
                print("Secret key not valid")
                exit()
            #self.view.populate_add_account_form(issuer, label, secret_key)
            return issuer, label, secret_key
        else:
            self.logger.info("No QR code found")
            return None

    def open_qr_image(self):
        # Placeholder for opening a QR image
        pass

    def save_new_account(self, provider, label, secret):
        """@param secret is plain-text shared secret"""
        encrypted_secret = self.secrets_manager.encrypt(secret)
        account = Account(provider, label, encrypted_secret, "")
        self.account_manager.add_account(account)
        self.logger.info(f"Saved account: {provider} ({label})")
