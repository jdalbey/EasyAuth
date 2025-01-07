
import json
import os
from pathlib import Path # Python 3.5+
class Account:
    def __init__(self, provider, label, secret):
        self.provider = provider
        self.label = label
        self.secret = secret

class AccountManager:
    kPathToVault = ".var/app/org.redpoint.EasyAuth/data/vault.json"  # relative to user.home
    def __init__(self, filename=kPathToVault):
        home_dir_str = str(Path.home())
        self.vault_path = Path.home().joinpath(home_dir_str, filename)
        self.accounts = self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.vault_path):
            with open(self.vault_path, 'r') as f:
                content = json.load(f)
                return [Account(**acc) for acc in content]
        else:
            #TODO Report no entries in vault
            print (f"Missing vault file {self.vault_path}")
            return []
            #raise FileNotFoundError

    def set_accounts(self,account_string):
        """Set accounts from a string - dependency injection for testing
        @param account_string is JSON string of vault data"""
        self.accounts = json.loads(account_string)

    # TODO: Need a way to report errors in the model back to the view.
    def save_accounts(self):
        # TODO: Handle missing vault (so create it).
        try:
            with open(self.vault_path, 'w') as f:
                json.dump([acc.__dict__ for acc in self.accounts], f)
        except FileNotFoundError:
            print ("Missing Vault, can't save account.")

    def add_account(self, account):
        #TODO: Don't allow duplicate accounts (i.e., duplicate secret key)
        self.accounts.append(account)
        self.save_accounts()

    def update_account(self, index, account):
        self.accounts[index] = account
        self.save_accounts()

    def delete_account(self, account):
        self.accounts.remove(account)
        self.save_accounts()