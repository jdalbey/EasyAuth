import base64
import pyotp
import re

def is_valid_secretkey(secret: str) -> bool:
    """
    Validate that the secret key is a valid Base32-encoded string.
    This checks that the string contains only valid Base32 characters
    and the length is a valid multiple of 8 (after considering padding).
    """
    base32_regex = re.compile("^[A-Z2-7=]+$")  # Base32 chars + padding (`=`)

    # Check if the string matches Base32 characters
    if not base32_regex.match(secret):
        return False

    # Check the padding and length, Base32 padding should be 0, 1, or 2 `=`
    if secret.count('=') > 2:
        return False

    # Try decoding and checking if it succeeds
    try:
        decoded = base64.b32decode(secret, casefold=True)
        # Ensure the decoded result is not all zero bytes
        if len(decoded) == 0 or all(byte == 0 for byte in decoded):
            return False
        return True
    except Exception as e:
        return False

class OTPManager:
    def __init__(self, secrets_manager):
        self.secrets_manager = secrets_manager

    def generate_otp(self, secret):
        decrypted_secret = self.secrets_manager.decrypt(secret)
        totp = pyotp.TOTP(decrypted_secret)
        return totp.now()