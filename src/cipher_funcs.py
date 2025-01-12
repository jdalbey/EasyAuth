from cryptography.fernet import Fernet
from appconfig import AppConfig
import hashlib
import base64

def encrypt(secret):
    """@param secret is the shared secret key to be encrypted"""
    key = derive_key_from_uuid()
    cipher_suite = Fernet(key)
    encrypted_secret = cipher_suite.encrypt(secret.encode())
    return encrypted_secret.decode()  # Return as string

def decrypt(encrypted_secret):
    """@param encrypted_secret is the encrypted version of the shared secret key (not simply the key itself)"""
    key = derive_key_from_uuid()
    cipher_suite = Fernet(key)
    decrypted_secret = cipher_suite.decrypt(encrypted_secret.encode())
    return decrypted_secret.decode()  # Return as string

# Derive a Fernet Key from the Machine UUID
def derive_key_from_uuid():
    config = AppConfig()
    alt_id = config.get_alt_id()
    if alt_id:
        uuid = alt_id
    else:
        # TODO Make cross-platform
        with open("/etc/machine-id", "r") as f:
            uuid = f.read().strip()
    # Hash the UUID to create a 32-byte key
    key = hashlib.sha256(uuid.encode()).digest()
    # Encode the key to Base64 (required by Fernet)
    return base64.urlsafe_b64encode(key)

    # def load_key(self):
    #     """ load key from a local file """
    #     if os.path.exists(self.key_file):
    #         with open(self.key_file, 'rb') as key_file:
    #             return key_file.read()
    #     else:
    #         key = Fernet.generate_key()
    #         with open(self.key_file, 'wb') as key_file:
    #             key_file.write(key)
    #         return key

