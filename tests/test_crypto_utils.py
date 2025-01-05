from dev_archive.crypto_utils import encrypt, decrypt


class TestCryptoUtils:

    def test_encrypt(self):
        secret = encrypt("hello world")
        assert secret != "hello world"
        assert decrypt(secret) == "hello world"

