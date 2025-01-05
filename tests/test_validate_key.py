from dev_archive.otp_mgrV1 import is_valid_secretkey

class TestValidateSecretKey:
    def test_is_valid_secretkey(self):
        # Example usage:
        secret_key = "JBSWY3DPEHPK3PXP"
        assert is_valid_secretkey(secret_key)

    def test_not_valid_secretkey(self):
        secret_key = "AAAAAAAAAAAAAAAA"
        assert not is_valid_secretkey(secret_key)