
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
        self.filename = filename
        self.accounts = self.load_accounts()

    def load_accounts(self):
        home_dir_str = str(Path.home())
        filepath = Path.home().joinpath(home_dir_str, self.filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = json.load(f)
                return [Account(**acc) for acc in content]
        else:
            print (f"Missing vault file {filepath}")
            raise FileNotFoundError

    def set_accounts(self,account_string):
        """Set accounts from a string - dependency injection for testing
        @param account_string is JSON string of vault data"""
        self.accounts = json.loads(account_string)

    def save_accounts(self):
        with open(self.filename, 'w') as f:
            json.dump([acc.__dict__ for acc in self.accounts], f)

    def add_account(self, account):
        self.accounts.append(account)
        self.save_accounts()

    def update_account(self, index, account):
        self.accounts[index] = account
        self.save_accounts()

    def delete_account(self, index):
        del self.accounts[index]
        self.save_accounts()