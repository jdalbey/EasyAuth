 # Detects one or more QR codes on the screen.
import pyautogui
from pyzbar.pyzbar import decode
from urllib.parse import urlparse, parse_qs
import time

def scan_screen_for_qr_codes():
    """
    Scans the display screen for QR codes and decodes them.

    Returns:
        list: A list of decoded data from QR codes found on the screen.

    """
    print  ("Taking screen shot")
    #starttime = time.time()
    # Take a screenshot of the current screen
    screenshot = pyautogui.screenshot()

    # Convert screenshot to a format usable by pyzbar
    screenshot = screenshot.convert('RGB')

    # Detect and decode QR codes
    qr_codes = decode(screenshot)

    # Extract data from the detected QR codes
    results = [qr_code.data.decode('utf-8') for qr_code in qr_codes if qr_code.data]
    #print (time.time() - starttime)
    return results

""" Reference: 2FA QR generator: https://stefansundin.github.io/2fa-qr/ """
if __name__ == '__main__':
    url = scan_screen_for_qr_codes()
    print (url)
    #url = 'otpauth://totp/PayPal:steve@dottotech.com?secret=DITATUPFVUIJK7X7&issuer=PayPal'
    #url = 'otpauth://totp/bobjones?secret=DITATUPFVUIJK7X7&issuer=Gargle.com'
