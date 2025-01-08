import base64
import pyotp
import re


def is_valid_secretkey(secret: str) -> bool:
    """ Validate that the secret key can generate an OTP """
    try:
        totp = pyotp.TOTP(secret)
        otp = totp.now()  # Generate OTP, which validates the key internally
        return True
    except ValueError as e:
        return False

class OTPManager:
    def __init__(self, secrets_manager):
        self.secrets_manager = secrets_manager

    def generate_otp(self, secret):
        decrypted_secret = self.secrets_manager.decrypt(secret)
        totp = pyotp.TOTP(decrypted_secret)
        return totp.now()