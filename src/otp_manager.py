
import pyotp

class OTPManager:
    def __init__(self, secrets_manager):
        self.secrets_manager = secrets_manager

    def generate_otp(self, secret):
        decrypted_secret = self.secrets_manager.decrypt(secret)
        totp = pyotp.TOTP(decrypted_secret)
        return totp.now()