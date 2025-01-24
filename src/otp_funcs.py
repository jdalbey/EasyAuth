import logging

import pyotp
import qrcode
from io import BytesIO
import cipher_funcs

def is_valid_secretkey(secret: str) -> bool:
    """ Validate that the secret key can generate an OTP
        I.e., is secret a base32 string """
    try:
        totp = pyotp.TOTP(secret)
        otp = totp.now()  # Generate OTP, which validates the key internally
        return True
    except ValueError as e:
        return False

def generate_otp(secret):
    decrypted_secret = cipher_funcs.decrypt(secret)
    totp = pyotp.TOTP(decrypted_secret)
    result = totp.now()
    return result

def otpauth_uri_from_account(account):
    decrypted_secret = cipher_funcs.decrypt(account.secret)
    totp = pyotp.TOTP(decrypted_secret)
    uri = totp.provisioning_uri(name=account.label, issuer_name=account.issuer)
    logging.debug (f"otp_funcs: created uri from account info: {uri}")
    return uri

def generate_qr_image(account):
    uri = otpauth_uri_from_account(account)
    qr = qrcode.QRCode()
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    # Reduce the size of the image by setting box_size
    img = img.resize((300, 300))  # Set the desired size
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
