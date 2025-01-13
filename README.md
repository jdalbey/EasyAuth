# EasyAuth
A 2FA secrets manager and TOTP generator for Linux desktop.
Focus on ease of use for beginners using TOTP authentication. 

## Features
 - Stores your secret keys encrypted in a vault on your local machine (doesn't rely on third-party cloud services)
 - Generates Time-based One-time Passwords from your secret keys
 - Accounts are displayed in a scrollable list with a search feature.
 - The list can be reordered to place your most frequently used accounts at the top.
 - Automatically finds QR codes displayed on the screen.  No need to scan QR codes with your phone.
 - QR codes can be read from an image file
 - Familiar easy-to-navigate desktop GUI
 - Verifying with OTP in three easy steps: 
   1. Open the application  
   2. Click Copy button next to the account you are logging in to. 
   3. Paste into verification form.
 
   No text messages to your phone, no email to check. Quick and hassle-free.


### Status
Early stage development.  Core features and GUI are implemented.  Minimal error handling.  Some unit tests for core modules are passing.

### Screenshot

[![Main Window](https://i.postimg.cc/8zfHwgb5/Screenshot-from-2025-01-08-21-46-10.png)](https://postimg.cc/4YZVNMqk)

### Limitations

Currently targets Linux OS.

Uses only TOTP codes with SHA1, 6-digit, 30-second parameters.

### Warning
As with any form of two-factor authentication, if the second-factor is compromised (e.g., your phone is lost or stolen) 
you may lose access to your online accounts unless you have saved the recover codes you were issued initially. 
This software is issued with no guarantee.  There is a risk of data loss, including loss of your secret keys.