# EasyAuth
A 2FA secrets manager and TOTP generator for Linux desktop.
Focus on ease of use for beginners using TOTP authentication. 

## Features
 - Stores your secret keys encrypted in a vault on your local machine (doesn't rely on third-party cloud services).
 - Generates Time-based One-time Passwords from your secret keys.
 - Accounts are displayed in a scrollable list with a search feature.
 - The list can be sorted alphabetically or by most recently used.
 - The list can be manually reordered to achieve a custom ordering. 
 - Automatically finds QR codes displayed on the screen.  No need to scan QR codes with your phone.
 - QR codes can be read from an image file.
 - Export and Import vault to plain-text JSON file.
 - Familiar easy-to-navigate desktop GUI.
 - Automatically finds favicons for many sites that offer TOTP verification.
 - GUI includes light and dark themes.
 - Preferences dialog has some customization settings.
 - Verifying with TOTP in three easy steps: 
   1. Open the application.  
   2. Click the TOTP code for the account you are logging in to. 
   3. Paste into verification form.
 
   No text messages to your phone, no email to check. Quick and hassle-free.


### Status
All features above are implemented.
Developer is "eating his own dog food" by using the program to login to Github to maintain this project repository.
Error handling implemented for core data model classes.
Approximately 2000 lines of code.  67 automated unit tests for are passing.  

### Screenshots
 
<a href="https://ibb.co/M5FwMGb"><img src="https://i.ibb.co/93QKsVJ/Main-Window.png" alt="Main-Window" border="0"></a>

<a href="https://imgbb.com/"><img src="https://i.ibb.co/kM9b2Tb/Edit-Account-Dialog.png" alt="Edit-Account-Dialog" border="0"></a>
### Limitations

Currently targets Linux OS.

Uses only TOTP codes with SHA1, 6-digit, 30-second parameters.

### Warning
As with any form of two-factor authentication, if the second-factor is compromised (e.g., your phone is lost or stolen) 
you may lose access to your online accounts unless you have saved the recover codes you were issued initially. 
This software is issued with no guarantee.  There is a risk of data loss, including loss of your secret keys.

### Dependencies
Python 3.5+

PyQt5  
pyotp  
pyperclip  
pyautogui  
pyzbar  
cryptography  
qrcode  
qdarktheme

## Usage
Practice storing a new secret key using the sample QR code below.
1. Launch the application.
2. Make sure the QR code below is visible on the screen. Click 'Add Account".
3. The "Confirm New Account" dialog appears with the fields filled from the data in the QR code. Click "Accept".
4. Observe the new account in the main window.

<img src="https://i.ibb.co/GPMh7Rq/Sample-QRcode-easyauth-demo.png" alt="Sample QR code">
