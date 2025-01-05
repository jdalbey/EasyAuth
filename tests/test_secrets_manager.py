from secrets_manager import SecretsManager

class TestSecretsManager:

    def test_encrypt(self):
        mgr = SecretsManager()
        secret = mgr.encrypt("hello world")
        assert secret != "hello world"
        assert mgr.decrypt(secret) == "hello world"

