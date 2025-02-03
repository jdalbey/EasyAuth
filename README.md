# EasyAuth
A 2FA secrets manager and TOTP generator for Linux desktop.
Focus on ease of use for beginners using TOTP authentication.  
  
[Download](https://github.com/jdalbey/EasyAuth/releases) ... [Website](https://jdalbey.github.io/EasyAuth/) ... [Quick Start](https://github.com/jdalbey/EasyAuth/blob/master/docs/Quick%20Start%20Guide.md) ... [User Manual](https://github.com/jdalbey/EasyAuth/wiki/User-Manual#easyauth-user-manual)
## Features
 - Stores your secret keys encrypted in a vault on your local machine (doesn't rely on third-party cloud services).
 - Automatically finds QR codes displayed on the screen.  No need to scan QR codes with your phone.
 - QR codes can be read from an image file.
 - Generates Time-based One-time Passwords from your secret keys.
 - Accounts are displayed in a scrollable list with a search feature.
 - The list can be sorted alphabetically, by usage frequency, or by most recently used.
 - The list can be manually reordered to achieve a custom ordering. 
 - Vault entries can be displayed as QR codes for migration to other applications.
 - Export and Import vault to plain-text JSON file or otpauth URI format.
 - Familiar easy-to-navigate desktop GUI.
 - Automatically finds favicons for many sites that offer TOTP verification.
 - GUI includes light and dark themes.
 - Preferences dialog has useful customization settings.
 - Verifying with TOTP in three easy steps: 
   1. Open the application.  
   2. Click the TOTP code for the account you are logging in to. 
   3. Paste into verification form.
 
   No text messages to your phone, no email to check. Quick and hassle-free.


### Status
First production release is available for download (Linux only).  All features above are implemented.

[Website](https://jdalbey.github.io/EasyAuth/) is under construction.

Developer Stats:  
Source lines of code: 2392  
Unit tests lines of code: 1529  
Unit test cases: 83  

### Download

Binary for Linux is available under [Releases](https://github.com/jdalbey/EasyAuth/releases).

### Screenshots
 
![Main Window](https://i.ibb.co/XxhTr1dx/Account-List.png)

![Add Account](https://i.ibb.co/HTP9SGwJ/Add-Account.png)

![Edit Account](https://i.ibb.co/WWf6bcgQ/Edit-Account.png)

### Limitations

Currently targets Linux OS.

Uses only TOTP codes with SHA1, 6-digit, 30-second parameters.

### Warning
As with any form of two-factor authentication, if the second-factor is compromised (e.g., your phone is lost or stolen) 
you may lose access to your online accounts unless you have saved the recover codes you were issued initially. 
This software is issued with no guarantee.  There is a risk of data loss, including loss of your secret keys.

## Usage
Practice storing a new secret key using the sample QR code below.
1. Launch the application.
2. Make sure the QR code below is visible on the screen. Click 'Add Account".
3. The form fields are filled automatically with the data from the QR code. Click "Add".
4. Observe the new account in the main window.

<img src="https://i.ibb.co/GPMh7Rq/Sample-QRcode-easyauth-demo.png" alt="Sample QR code">

A [Quick Start guide](https://github.com/jdalbey/EasyAuth/blob/master/docs/Quick%20Start%20Guide.md) is available,
or view the [complete User Manual](https://github.com/jdalbey/EasyAuth/wiki/User-Manual#easyauth-user-manual).



---
## Installation from Source

#### Dependencies
Python 3.5+

PyQt5  
pyotp  
pyperclip  
pyzbar  
cryptography  
qrcode  
qdarktheme
Markdown

#### Prerequisites

- Currently this program only runs on Linux systems.
- Ensure you have Python 3.5+ installed on your system.



#### 1. Download the Repository

1. Click the "Code" button and select "Download ZIP".
2. Extract the downloaded ZIP file to a directory of your choice.

Alternatively, you can clone the repository using Git:

```bash
git clone https://github.com/jdalbey/EasyAuth.git
cd EasyAuth
```

#### 2: Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  
```

#### 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4: Launch the Application


```bash
python src/main.py
```

#### Additional Information

- **Logging**: The application uses logging to provide debug information. You can configure the logging settings in the `main.py` file.
- **HiDPI Support**: The application uses `qdarktheme` to enable HiDPI support.

## Troubleshooting

If you encounter any issues, please check the following:

- Ensure all dependencies are installed correctly.
- Check the console output for any error messages.
- Turn on debugging output (See User Manual)

For further assistance, you can open an [Issue](https://github.com/jdalbey/EasyAuth/issues).

---



