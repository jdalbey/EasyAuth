import hashlib
import base64
from cryptography.fernet import Fernet

# Derive a Fernet Key from the Machine UUID
def derive_key_from_uuid():
    with open("/etc/machine-id", "r") as f:
        uuid = f.read().strip()
    # Hash the UUID to create a 32-byte key
    key = hashlib.sha256(uuid.encode()).digest()
    # Encode the key to Base64 (required by Fernet)
    return base64.urlsafe_b64encode(key)

def encrypt(plain_text):
    # Initialize Fernet with the key
    cipher = Fernet(derive_key_from_uuid())

    # Encrypt data
    encrypted_data = cipher.encrypt(plain_text.encode())
    #print(f"Encrypted Data: {encrypted_data}")
    return encrypted_data.decode()

def decrypt(encrypted_data):
    """@param encrypted_data  encoded form of secret key"""
    # Initialize Fernet with the key
    cipher = Fernet(derive_key_from_uuid())

    # Decrypt data
    decrypted_data = cipher.decrypt(encrypted_data)
    #print(f"Decrypted Data: {decrypted_data.decode()}")
    return decrypted_data.decode()

if __name__ == "__main__":
    secret = encrypt("snoopy")
    print (f"Secret is {secret}")
    print (decrypt(secret))
