
import json
import os

class Account:
    def __init__(self, provider, label, secret):
        self.provider = provider
        self.label = label
        self.secret = secret

class AccountManager:
    kPathToVault = "src/vault.json"
    def __init__(self, filename=kPathToVault):
        self.filename = filename
        self.accounts = self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                content = json.load(f)
                return [Account(**acc) for acc in content]
        return []

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