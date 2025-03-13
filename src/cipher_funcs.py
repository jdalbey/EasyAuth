from cryptography.fernet import Fernet
from appconfig import AppConfig
import hashlib
import base64
import machineid
""" Utility functions for converting the secret key. """

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

def derive_key_from_uuid():
    """ Derive a Fernet Key from the Machine UUID """
    config = AppConfig()
    alt_id = config.get_alt_id()
    if alt_id:
        uuid = alt_id
    else:
        # Use cross-platform machineid module
        uuid = machineid.id()
    # Hash the key
    key = hashlib.sha256(uuid.encode()).digest()
    # Encode the key to Base64 (required by Fernet)
    return base64.urlsafe_b64encode(key)
