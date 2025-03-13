import pyotp
import qrcode
from io import BytesIO
import cipher_funcs

""" Utility functions for One-time Passcodes """

def is_valid_secretkey(secret: str) -> bool:
    """ Validate that the secret key can generate an OTP
        I.e., is secret a base32 string
        @return true if valid, false if not
    """
    try:
        totp = pyotp.TOTP(secret)
        totp.now()  # Generate OTP, which validates the key internally
        return True
    except ValueError as e:
        return False

def generate_otp(secret):
    """ Generate the OTP from the secret key.
     @param secret the encrypted secret key from the vault.
     @return the current OTP
     """
    decrypted_secret = cipher_funcs.decrypt(secret)
    totp = pyotp.TOTP(decrypted_secret)
    result = totp.now()
    return result

def generate_qr_image(account):
    """ Generate a QR code from the vault entry.
    @pararm account (Account) - the vault entry to be converted to QR code
    @return PNG image
    """
    # Get the URI from the account
    uri = account.get_otp_auth_uri()
    # Use qrcode library to make an image of the QR code.
    qr = qrcode.QRCode()
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    # Reduce the size of the image by setting box_size
    img = img.resize((300, 300))  # Set the desired size
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
