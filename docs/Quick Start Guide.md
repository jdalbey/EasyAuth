## EasyAuth Quick Start Guide

The quide will show how to store shared keys in your EasyAuth vault and use Time-based One-time Passwords (TOTP) to authenticate with a website.

####  Prerequisites

1. You are using a Linux or Windows desktop OS.
2. You have a web browser open to the site with which you want to establish two-factor authentication (for example, `paypal.com`).  We will refer to this site as the "provider".
3. You have begun the process of enabling 2-factor authentication and are viewing a QR code that contains a shared secret key. 

### Step 1: Create a new vault entry

1. Open EasyAuth.  The first time it is launched a message indicates that you have an empty vault.  

2. Make sure the QR code is visible somewhere on the screen. Click the 'Scan QR code' button.  

3. A confirmation dialog explains that EasyAuth will search the display for a QR code. Click "Just once" or "Always allow".  

4. The program will search for a visible QR code and, if found, will create a new vault entry.
The main window appears with the new entry listed at the top.

### Step 2: Verifying with the TOTP code.

1. For each vault entry a six-digit One-Time Password (TOTP) is displayed that changes every 30 seconds. 

2. Click the 6-digit TOTP code to copy it to the clipboard.

3. Complete the setup process on the website by pasting this code into the verify field in your browser. 

4. Next time you attempt to login to your online account you will be prompted to verify your identity. After entering your password a validation form will be displayed requesting a one-time code. 

5. In EasyAuth locate the TOTP for the desired website and click on the TOTP code. Return to the website verification form and paste the six-digit code into the verification field.

6. If you are delayed in completing the copy-and-paste operation the 30-second activation period may expire and the website will decline to verify you.  Simply click the next TOTP code that appears in the main window and try again. 


EasyAuth's goal is to achieve two-factor authentication of your online identify in three mouse clicks. 
Leave feedback or contribute to the project on [Github](https://www.github.com/jdalbey/EasyAuth)  



 
