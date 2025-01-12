import cipher_funcs

class TestSecretsManager:

    def test_encrypt(self):
        secret = cipher_funcs.encrypt("hello world")
        assert secret != "hello world"
        assert cipher_funcs.decrypt(secret) == "hello world"

        secret = cipher_funcs.encrypt("ABC234")
        print (secret)
        cipher_funcs.decrypt(secret)

