## EasyAuth Quick Start Guide

The quide will show how to store shared keys in your EasyAuth vault and use Time-based One-time Passwords (TOTP) to authenticate with a website.
####  Prerequisites

1. You are using a Linux desktop OS.
2. You have a web browser open to the site with which you want to establish two-factor authentication (for example, `paypal.com`).  We will refer to this site as the "provider".
3. You have begun the process of enabling 2-factor authentication and are viewing a QR code that contains a shared secret key. 

### Step 1: Create an account in EasyAuth

1. Open EasyAuth.  The first time it is launched a message indicates that you have an empty vault.  
![Empty vault screenshot](https://i.ibb.co/NdZ7g6Qv/vault-empty.png)
2. Make sure the QR code is visible somewhere on the screen. Click the 'Add Account' button. 
The program will search for a visible QR code and the QR code data will be entered into the form fields.  
![Add Account Form screenshot](https://i.ibb.co/8gCSrhcw/Add-Account-Form.png)
3. You may change the value of the User field to any label that reminds you which online account this entry is associated with (usually username or email address).  
4. Click "Add." The dialog closes and the main window appears with the new account listed at the top.   The Provider and User fields are shown on the left and on the right is the TOTP.  
![Main Window screenshot](https://i.ibb.co/1t35DGdJ/Main-Window.png)



### Step 2: Verifying with the TOTP code.

1. Now that EasyAuth has created an account for the desired website, it  will display a six-digit One-Time Password (TOTP) for the account that  changes every 30 seconds. The seconds timer indicates how much  time remains for the displayed TOTP to be active.  
![TOTP code](https://i.ibb.co/W4gGx8Hf/TOTP-code.png)
2. Click the 6-digit TOTP code to copy it to the clipboard.

3. Complete the setup process on the website by pasting this code into the verify field in your browser. 

4. Next time you attempt to login to your online account you will be prompted to verify your identity. An entry form will be displayed requesting a  one-time code. 

5. In EasyAuth locate the TOTP for the desired account and click on the TOTP code. Return to the website verification form and paste the six-digit code into the verification field.

6. If you are delayed in completing the copy-and-paste operation the 30-second activation period may expire and the website will decline to verify you.  Simply click the next TOTP code that appears in the main window and try again. 


EasyAuth's goal is to achieve two-factor authentication of your online identify in three mouse clicks. 
Leave feedback or contribute to the project on [Github](https://www.github.com/jdalbey/EasyAuth)  



 