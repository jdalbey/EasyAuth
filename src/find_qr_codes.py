 # Detects one or more QR codes on the screen.
from pyzbar.pyzbar import decode
from PIL import ImageGrab

def scan_screen_for_qr_codes():
    """
    Scans the display screen for QR codes and decodes them.

    Returns:
        list: A list of decoded data from QR codes found on the screen.

    """
    # Take a screenshot of the current screen
    bbox = None  # take fullscreen
    screenshot = ImageGrab.grab(bbox)

    # Convert screenshot to a format usable by pyzbar
    screenshot = screenshot.convert('RGB')
    #screenshot.save("/tmp/screenshotqrcodes.png")

    # Detect and decode QR codes
    qr_codes = decode(screenshot)

    # Extract data from the detected QR codes
    results = [qr_code.data.decode('utf-8') for qr_code in qr_codes if qr_code.data]
    # Return a list, one item for each code.
    return results

""" Reference: 2FA QR generator: https://stefansundin.github.io/2fa-qr/ """
if __name__ == '__main__':
    urls = scan_screen_for_qr_codes()
    for url in urls:
        print(url)
    #url = 'otpauth://totp/PayPal:steve@dottotech.com?secret=DITATUPFVUIJK7X7&issuer=PayPal'
    #url = 'otpauth://totp/bobjones?secret=DITATUPFVUIJK7X7&issuer=Gargle.com'
