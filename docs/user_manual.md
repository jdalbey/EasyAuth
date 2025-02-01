## EasyAuth User Manual

### Under construction.  This is a very early draft and no longer accurate.

This is the user manual for the EasyAuth application. 
EasyAuth is a desktop linux application for managing one-time passwords.

The application has a graphical user interface. 
When the application is started a main window appears. 
The title bar shows the name of the application. 
Beneath the title bar is a menu bar. 
The first item on the left of the menu bar is the File menu. 
This menu has several sub menus. 
The first sub menu is "backup/restore", the second is "import". 
The third is "reorder accounts". 
The next is "provider list". 
The next is "settings". 
The next is "about". 
To the right of the file menu is a button with the label "add account". 
To the right of the button is a text field for entering a search term. 
To the right of the text field is a search icon (a magnifying glass). 
To the right of the search icon is the Filter icon. 

The Sort by menu has two options: alphabetically and recently used. 

## Add Account Dialog
In the center of the window is a message that says "no entries found. 
start adding entries by clicking 'Add account'". 
Then there is a hyperlink that says "Learn more". 
Clicking the Add Account button causes a form to appear. 
The title of the form is "new account". 
At the top of the form a message says "Create a New Account from:" and then it lists three options vertically, each with a bullet point. 
The first is a button "Use QR code". 
The second is a button "Open QR image". 
The third is "enter the data manually".

 
The form then shows three fields. 
The first is labeled "provider", the second is labeled "user", and the third is labeled "secret key". 
The provider field is for the name of the service that issued the secret key.  A "Lookup" button will open a dialog 
with a list of providers to choose from.  This reference is a helpful aid to recalling spelling of different websites. 
The user field is for a username, email address, or other identifier to distinguish this account from others with
the same website.
The secret key field is for entering the shared secret key provided by the website.

Clicking the "Use QR code" button the application will search the screen for a visible QR code. 
If it doesn't find one it will present a dialog that says "check that a browser window is open with a QR code visible", and then two buttons that say "try again" or "cancel". 
If the application finds a QR code it will open a confirmation dialog with the three fields on the form prefilled. 
The dialog offers Accept and Decline buttons at the bottom of the form. 
When the user clicks Accept a new account is created and appears at the top of the account list in the main window.
If the provider name exists in the provider list the favicon for the website will be placed next to the account. 


The account list on the main page has a row for each entry. 
Each row contains six fields. 
The second field has two strings, one above the other. 
The first is the provider name. 
The second is the label for this account. 
The third field shows a one time password (six digits). 
The next field shows a Copy icon. 
The next field shows an edit icon, and the last field shows pin icon. 


if a new account form is saved and the value in the provider field does not exist in the provider list, a new provider form will appear. 
The new provider form has a message that says "there is no provider in our list with the name given in the provider Field", and then a prompt to "please add it" the form has a field for provider name, followed by a field for website URL, followed by a field for help URL. 
Beneath that is a spinbox field with a whole number amount that defaults to 30, and the label "time period". 
Beneath that is a spinbox with a whole number amount that defaults to six and the label "digits". 
Beneath that is an image of an icon. 
By default, this image is a single letter, which is the first letter of the provider name. 
To the right of the image are three buttons. 
The first says "find Favicon". 
The second says "Import icon from file", and the third says "reset icon to default". 
The third button is only enabled when the value of the icon being displayed is not the default icon. 
At the bottom of the form are buttons for Save and cancel. 
 When the save button is clicked on the new account form, the value in the secret key field will be checked to make sure it's valid. 
If it's not valid, an error message will be displayed that says, "invalid secret key".


Advanced settings are not displayed on the new account form. 
 (they are taken from provider list and until the form is saved we don't know who the provider is.) 

If the user chooses to create a new account from a QR image by clicking "Open file", a file chooser dialog will appear with a file type for PNG. 
If the user selects a QR image, the QR code in the image will be decoded and the values used to fill in the fields of the new account form in the same manner as if the QR code had been scanned directly. 


If the user chooses to enter the data manually into a new account form, they just complete the three fields required and click Save.

If the user chose to create a new account by QR code and clicks "Find", and there are multiple QR codes found, then a selection dialog will appear that says "multiple QR codes were found, select desired item to be used for the new account", and then it will list all of the QR code information, one for each QR code found. 
The three pieces of information are the provider, the label and the secret key. 
 At the bottom are Select and Cancel buttons. 
Each item listed has a radio button so that only one of the displayed items can be selected. 
The Select button becomes enabled only when a radio button has been clicked. 
When the select button is pressed the values from the selected item are used to complete the fields in the new account form. 


In the account list, there are three buttons. 
The copy button copies the currently displayed one time password onto the clipboard. 
The pin button causes that entry to remain in that current position in the list of accounts. 
The edit button causes an Edit Account form to appear. 


The Edit Account form has fields for provider, label, and secret key. 
The secret key field is displayed as asterisks, and to the right of it is a show button. 
Pressing the show button reveals the secret key. 
 If the secret key is not valid, the asterisks are displayed as question marks in red.
There's an expandable section of the form labeled "advanced settings" and in the advanced settings it displays two read-only fields: provider website URL and provider help URL. 
 Two spinboxes allow for modifying the time period and digits. 
It also displays read-only fields for "last used"  and "usage count". 
The last used field shows the date and time of the last time a one time password was copied for this account, and the usage count is a whole number representing the number of times a one time password was copied for this account. 
Beneath this is a button that labeled "reveal QR code". 
When this button is pressed, a QR code is displayed that has embedded the provider, label, and secret key values in a valid OAuth format. 
When clicked the reveal QR code button text changes to "hide". 
In the same way the show secret key button also changes to hide once it has been clicked. 
The bottom of the form presents save, delete and Cancel buttons. 

## Deleting an account
An account can be deleted from the Edit Account page by using the Delete button. 
This action is not reversible and should be used with caution.  Deleting an account will delete the secret key used to authenticate
with the provider website.  In most cases this means you won't be able to login.  If you haven't saved the recover codes provided
when you setup two-factor authentication you may lose access to the website.

From the File menu, choosing the backup restore option presents a new dialog with two panels, one labeled backup and the other labeled restore. 
Each panel will have a set of radio buttons that indicate the different formats in which data can be backup or restored from. 
At the bottom of each panel is an okay button. 
Once the radio button is selected, the okay button is enabled, and when clicked, will cause the backup or restore in the desired format. 
The three options for backup are 1) EasyAuth format, which is plain-text JSON file, 2) freeOTP, and 3) ageis. 
Restore has the same three options. 
The okay button causes a file chooser dialog to appear in which the user indicates the file that they want to back up to or restore from. 


From the file menu, the import option works in the same manner as restore, with the exception that it merges the values from the import file into the current list of accounts. 


The search text entered into the search field on the menu bar causes a dynamic search to look through the items in the account list. 
First, the search looks for providers that match the query term, and if it doesn't find a match, will look for a label that matches the query term, and if that is not found, a message is displayed that says "no results, no accounts or providers matching the query were found" and the account list is shown as empty. 
As long as the value in the search field matches one or more accounts, the matching account items are displayed in the account list. 




In the main window above the list of accounts, but below the menu bar is a circled whole number that represents the number of seconds remaining in the expiration period for the current one time passwords. 

Choosing reorder accounts from the file menu causes a form to appear that lists all the accounts in a scrollable list. 
Additional buttons on each row allow items to be moved to a new position in the list. 
To the right of each row are up and down buttons which allow moving an entry up or down one slot in the list. 
To the left of the entry is an icon that looks like a hamburger menu which allows an entry to be grabbed and dragged to a new position in the list. 
At the bottom of the form are save and cancel buttons.

When the provider list option is chosen from the file menu a new form appears. 
The form has two panels. 
The left panel is a scrollable list with the names of all the providers. 
The right panel initially says "no provider selected. 
Select a provider or create a new one". 
At the top of the left hand panel is a button labeled "Add" and the search icon. 
Clicking the search icon opens a search text entry field. 
Any text entered in the search text entry field causes the display of any matching items in the provider list. 
The add button opens a new provider form in the right hand panel. 
The new provider form has fields for provider name, website URL, and help URL, and spinboxes for the time period and digits fields. 
The form also provides options for setting a value of the icon. 
Clicking on a name in the provider list in the left panel causes an edit provider form to appear in the right hand panel in which the attributes of a provider can be modified. 
There's also a delete button that would remove the provider from the list. 

