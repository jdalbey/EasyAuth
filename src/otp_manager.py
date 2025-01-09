import pyotp
import qrcode
from io import BytesIO

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
    
    def generate_qr_code(self, account):
        decrypted_secret = self.secrets_manager.decrypt(account.secret)
        totp = pyotp.TOTP(decrypted_secret)
        uri = totp.provisioning_uri(name=account.label, issuer_name=account.provider)
        qr = qrcode.QRCode()
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        # Reduce the size of the image by setting box_size
        img = img.resize((300, 300))  # Set the desired size
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    