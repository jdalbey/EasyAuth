
import json
import os
from pathlib import Path # Python 3.5+
from dataclasses import dataclass

@dataclass
class Account:
    provider: str
    label: str
    secret: str

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
            print (f"Missing vault file {self.vault_path}")
            return []
            #raise FileNotFoundError
    def get_provider_icon_name(self, provider):
        # TODO: Look up provider icon
        return "images/favicon_32x32.png"
    
    def set_accounts(self,account_string):
        """Set accounts from a string - dependency injection for testing
        @param account_string is JSON string of vault data"""
        self.accounts = json.loads(account_string)

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

    def add_account(self, account):
        #TODO: Don't allow duplicate accounts (i.e., duplicate secret key)
        #self.accounts.append(account)
        self.accounts.insert(0,account)
        self.save_accounts()

    def update_account(self, index, account):
        self.accounts[index] = account
        self.save_accounts()

    def delete_account(self, account):
        self.accounts.remove(account)
        self.save_accounts()