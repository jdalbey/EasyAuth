import logging
import json
import os
from pathlib import Path # Python 3.5+
from dataclasses import dataclass
import cipher_funcs
from datetime import datetime

# TODO: Disambiguate - sometimes secret is used as the shared key and sometimes as the encrypted key.
@dataclass
class Account:
    provider: str
    label: str
    secret: str
    last_used: str


class AccountManager:
    # TODO: Make cross-platform
    kPathToVault = ".var/app/org.redpoint.EasyAuth/data/vault.json"  # relative to user.home
    def __init__(self, filename=kPathToVault):
        self.logger = logging.getLogger(__name__)
        home_dir_str = str(Path.home())
        self.vault_path = Path.home().joinpath(home_dir_str, filename)
        self.accounts = self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.vault_path):
            with open(self.vault_path, 'r') as f:
                content = json.load(f)
                return [Account(**acc) for acc in content]
        else:
            print (f"Missing vault file {self.vault_path}")
            return []
            #raise FileNotFoundError

    def get_provider_icon_name(self, provider):
        # TODO: Look up provider icon
        return None   # "images/favicon_32x32.png"

    def set_accounts(self,account_string):
        """Set accounts from a string - dependency injection for testing
        @param account_string is JSON string of vault data"""
        content = json.loads(account_string)
        self.accounts = [Account(**acc) for acc in content]

    # TODO: Need a way to report errors in the model back to the view.
    def save_accounts(self):
        # Handle missing vault (so create it).
        if not os.path.exists(os.path.dirname(self.vault_path)):
            os.makedirs(os.path.dirname(self.vault_path))

        try:
            with open(self.vault_path, 'w') as f:
                json.dump([acc.__dict__ for acc in self.accounts], f)
        except FileNotFoundError:
            print ("Missing Vault, can't save account.")
            exit()

    def save_new_account(self, provider, label, secret):
        """@param secret is plain-text shared secret"""
        encrypted_secret = cipher_funcs.encrypt(secret)
        account = Account(provider, label, encrypted_secret, "")
        now = datetime.now()
        account.last_used = now.strftime("%Y-%m-%d %H:%M")

        self.__add_account(account)
        self.logger.info(f"Saved account: {provider} ({label})")

    def __add_account(self, account):
        """@param account with encrypted secret"""
        #TODO: Don't allow duplicate accounts (i.e., duplicate secret key)
        self.accounts.insert(0,account)  # insert in first spot in list
        self.save_accounts()

    def update_account(self, index, account):
        self.accounts[index] = account
        self.save_accounts()

    def delete_account(self, account):
        self.accounts.remove(account)
        self.save_accounts()

    def backup_accounts(self, file_path):
        """ Store the accounts as json in the given file_path after decrypting the secret keys"""
        decrypted_accounts = []
        for account in self.accounts:
            decrypted_account = account.__dict__.copy()
            decrypted_account['secret'] = cipher_funcs.decrypt(account.secret)
            decrypted_accounts.append(decrypted_account)

        try:
            with open(file_path, 'w') as f:
                json.dump(decrypted_accounts, f)
            print(f"Accounts successfully backed up to {file_path}")
        except Exception as e:
            print(f"Failed to backup accounts: {e}")

    @staticmethod
    def duplicate_accounts(accounts):
        list_copy = []
        for item in accounts:
            newitem = Account(
                provider=item.provider,
                label=item.label,
                secret=item.secret,
                last_used=item.last_used
            )
            list_copy.append(newitem)
        return list_copy
