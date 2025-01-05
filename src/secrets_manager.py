from cryptography.fernet import Fernet
import os
import hashlib
import base64

class SecretsManager:
    def __init__(self):
        self.key = self.derive_key_from_uuid()
        self.cipher_suite = Fernet(self.key)

    # def load_key(self):
    #     if os.path.exists(self.key_file):
    #         with open(self.key_file, 'rb') as key_file:
    #             return key_file.read()
    #     else:
    #         key = Fernet.generate_key()
    #         with open(self.key_file, 'wb') as key_file:
    #             key_file.write(key)
    #         return key

    def encrypt(self, secret):
        encrypted_secret = self.cipher_suite.encrypt(secret.encode())
        return encrypted_secret.decode()  # Return as string

    def decrypt(self, encrypted_secret):
        decrypted_secret = self.cipher_suite.decrypt(encrypted_secret.encode())
        return decrypted_secret.decode()  # Return as string
    
    # Derive a Fernet Key from the Machine UUID
    @staticmethod
    def derive_key_from_uuid():
        with open("/etc/machine-id", "r") as f:
            uuid = f.read().strip()
        # Hash the UUID to create a 32-byte key
        key = hashlib.sha256(uuid.encode()).digest()
        # Encode the key to Base64 (required by Fernet)
        return base64.urlsafe_b64encode(key)