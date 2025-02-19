
import otp_funcs
from account_mgr import Account

class TestOTPfuncs:
    def test_is_valid_secretkey(self):
        assert otp_funcs.is_valid_secretkey("AZ27")
        assert not otp_funcs.is_valid_secretkey("AZ12") # 1 is invalid

    def test_otpauth_uri_from_account(self):
        account = Account("Woogle","me@woogle.com","gAAAAABngpqkACjKleIWZa3xdgSjtAagXkdaAjRuMCpqHCcXAKbtZ6RpB9mKeHdToEn1TOIkhqmEXSiyfX0MgYekjYbU79k0TA==","2001-01-01 12:01")
        uri = account.get_otp_auth_uri()
        expected = "otpauth://totp/Woogle:me%40woogle.com?secret=ABC234&issuer=Woogle"
        assert uri == expected

