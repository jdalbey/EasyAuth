import pygetwindow as gw
import pyautogui
from PIL import Image
import pytesseract

# Get open windows
windows = gw.getWindowsWithTitle("Firefox") + gw.getWindowsWithTitle("Chrome")

if windows:
    browser_window = windows[0]
    browser_window.activate()

    # Locate browser address bar
    address_bar_image = pyautogui.locateOnScreen('address_bar.png', region=browser_window.box)

    if address_bar_image:
        address_bar_screenshot = pyautogui.screenshot(region=address_bar_image)
        address_bar_screenshot.save('address_bar_screenshot.png')

        # Use OCR to extract text from the address bar screenshot
        address_bar_text = pytesseract.image_to_string(Image.open('address_bar_screenshot.png'))

        print("Address bar text:", address_bar_text)
    else:
        print("Address bar not found.")
else:
    print("No open browser window found.")