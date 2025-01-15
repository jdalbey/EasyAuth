import datetime
import logging
from account_manager import AccountManager, Account
import otp_funcs
import cipher_funcs
from find_qr_codes import scan_screen_for_qr_codes

class AppController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.account_manager = AccountManager()
        self.view = None  # This will be set by the view using our set_view() method

    def set_view(self, view):
        self.view = view
        
    def get_accounts(self):
        return self.account_manager.accounts

    def set_accounts(self,json_str):
        self.account_manager.set_accounts(json_str)
        self.account_manager.save_accounts()

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
        print(f"Deleted account: {account.provider} ({account.label})")

    # def save_new_account(self, provider, label, secret):
    #     """@param secret is plain-text shared secret"""
    #     encrypted_secret = cipher_funcs.encrypt(secret)
    #     account = Account(provider, label, encrypted_secret, "")
    #     now = datetime.datetime.now()
    #     account.last_used = now.strftime("%Y-%m-%d %H:%M")
    #
    #     self.account_manager.add_account(account)
    #     self.logger.info(f"Saved account: {provider} ({label})")
