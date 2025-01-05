
from models import AccountManager

class TestAccountsManager:

    def test_set_accounts(self):
        acct_mgr = AccountManager()
        account_json = """[{"provider": "PayPal", "label": "steve@dottotech.com", "secret": "gAAAAABndtcMi6749NCbwinb9vWmFLvO9aVoje1JgxKdAkGO9bINKk4jwhuFUEhx4h3vkuRALL4l_ld8j8mjECJ2fAY5O2Nw0MLGs605saNcnhO1x6JJwl8="}]"""
        acct_mgr.set_accounts(account_json)
        acct_list = acct_mgr.accounts
        the_account = acct_list[0]
        assert the_account['provider'] ==  "PayPal"
        assert the_account['label'].startswith("steve")
        assert the_account['secret'].startswith("gAAAAAB")
