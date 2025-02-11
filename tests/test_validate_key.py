from otp_funcs import is_valid_secretkey

class TestValidateSecretKey:
    def test_is_valid_secretkey(self):
        # Example usage:
        secret_key = "JBSWY3DPEHPK3PXP"
        assert is_valid_secretkey(secret_key)

    def test_not_valid_secretkey(self):
        secret_key = "1AAAAAAAAAAAAAAA"
        assert not is_valid_secretkey(secret_key)