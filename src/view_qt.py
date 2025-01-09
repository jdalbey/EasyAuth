import logging
import os

from PyQt5.QtWidgets import (QMainWindow, QApplication,
    QSizePolicy, QMenuBar, QMenu, QAction, QLabel, QLineEdit, QToolBar, QScrollArea, 
    QToolButton, QDialog, QLabel, QPushButton, QGridLayout, QLineEdit, QVBoxLayout, 
    QHBoxLayout, QWidget, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
import pyotp
import time, datetime
import pyperclip
from settings_dialog import SettingsDialog  
from backup_dialog import BackupRestoreDialog   
from appconfig import AppConfig
from models import Account
from add_account_dialog import AddAccountDialog
from confirm_account_dialog import ConfirmAccountDialog
from controllers import AppController
from secrets_manager import SecretsManager


class AppView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.controller = controller
        self.controller.set_view(self)
        self.vault_empty = False # Don't display timer if vault empty
        self.app_config = AppConfig() # Get the global AppConfig instance
        self.current_dialog = None
        self.setWindowTitle("Easy Auth")
        self.setGeometry(100, 100, 500, 400)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        # Create GUI components
        self.create_main_panel()
        self.create_menubar()
        self.create_toolbar()

        self.display_accounts()
        self.start_timer()

    def create_menubar(self):
        # Create menubar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        add_account_action = QAction('Add Account', self)
        add_account_action.setShortcut('Ctrl+N')
        add_account_action.triggered.connect(self.show_add_account_form)
        file_menu.addAction(add_account_action)
        
        file_menu.addSeparator()
        
        import_action = QAction('Import', self)
        import_action.triggered.connect(self.import_accounts)
        file_menu.addAction(import_action)
        
        backup_action = QAction('Backup/Restore', self)
        backup_action.triggered.connect(self.show_backup_restore_dialog)
        file_menu.addAction(backup_action)

        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        reorder_action = QAction('Reorder Accounts', self)
        reorder_action.triggered.connect(self.reorder_accounts)
        tools_menu.addAction(reorder_action)
        
        providers_action = QAction('Providers', self)
        providers_action.triggered.connect(self.manage_providers)
        tools_menu.addAction(providers_action)
        

        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add quick access buttons
        add_btn = QPushButton("Add Account")
        add_btn.clicked.connect(self.show_add_account_form)
        toolbar.addWidget(add_btn)
        
        # Add spacer to push search to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        # Create search and filter group
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(lambda: self.display_accounts())  # Dynamic search
        self.search_box.setMaximumWidth(200)
        toolbar.addWidget(self.search_box)
        
        # Add filter button with icon and dropdown menu
        filter_btn = QToolButton()
        filter_icon = QIcon("images/filter_icon.png")
        filter_btn.setIcon(filter_icon)
        filter_btn.setIconSize(QSize(16, 16))  # Adjust size as needed
        filter_btn.setPopupMode(QToolButton.InstantPopup)
        filter_btn.setToolTip("Filter")  # Add tooltip for accessibility
        
        filter_menu = QMenu(filter_btn)
        filter_menu.addAction("Provider A-Z")
        filter_menu.addAction("User A-Z")
        filter_menu.addAction("Last used: ↓")
        filter_menu.addAction("Last used: ↑")
        filter_btn.setMenu(filter_menu)
        toolbar.addWidget(filter_btn)
        
        # Add spacer to push timer to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        # Timer label
        timer_font = QFont("Courier", 24, QFont.Bold)
        self.timer_label = QLabel("  ")
        self.timer_label.setFont(timer_font)
        self.timer_label.setStyleSheet("""
            background-color: lightgray;
            color: black;
            padding: 3px 15px;
            border-radius: 15px;
        """)
        toolbar.addWidget(self.timer_label)

    def create_main_panel(self):
        # Create scrollable area for main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)

    def start_timer(self):
        # Set up the QTimer to call update_timer every second
        self.timer = QTimer(self.central_widget)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 1000 milliseconds = 1 second


    def display_accounts(self):
        search_term = self.search_box.text().lower()
        accounts = self.controller.get_accounts()
        # Clear the existing widgets in the scroll_layout
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Check if the accounts list is empty
        if not accounts:
            self.vault_empty = True
            # Display a three-line help message
            help_message = [
                "Your vault is empty.",
                "The vault stores two-factor authentication keys",
                "provided by a website or other online service.",
                "Store your secret key by clicking 'Add Account'",
                "<Learn more>"
            ]
            for line in help_message:
                help_label = QLabel(line)
                help_label.setAlignment(Qt.AlignCenter)
                self.scroll_layout.addWidget(help_label)
        else:
            self.vault_empty = False
            # Adjust the spacing of the scroll_layout
            self.scroll_layout.setSpacing(2)  # Set vertical spacing between rows
            for index, account in enumerate(accounts):
                if search_term in account.provider.lower():
                    secret_key = self.controller.secrets_manager.decrypt(account.secret)
                    try:
                        otp = pyotp.TOTP(secret_key).now()
                    except:
                        otp = "??????"
                    row_frame = QFrame()
                    row_frame.setFrameShape(QFrame.StyledPanel)
                    # each row can expand horizontally but is fixed vertically, so they don't expand to fill up the scroll frame.
                    row_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    # Set internal padding for the frame
                    #row_frame.setContentsMargins(0,0,0,0)

                    rowframe_layout = QHBoxLayout(row_frame)
                    rowframe_layout.setSpacing(5)  # Set horizontal spacing between widgets in the row
                    # Assuming your_frame is inside a parent widget with a layout
                    # Set external padding around the frame by adjusting the layout margins of the parent widget
                    #rowframe_layout.layout().setContentsMargins(10, 10, 10, 10)
                    provider_icon_name = self.controller.get_provider_icon_name(account.provider)
                    provider_icon = QPixmap(provider_icon_name)
                    icon_label = QLabel()
                    icon_label.setPixmap(provider_icon)
                    rowframe_layout.addWidget(icon_label)
                    label = QLabel(f"{account.provider} ({account.label})")
                    label.setFont(QFont("Arial", 12))
                    otplabel = QLabel(f"{otp}")
                    otplabel.setFont(QFont("DejaVu Sans Mono", 14, QFont.Bold))
                    # Set the size policy for widget1
                    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                    rowframe_layout.addWidget(label)
                    #rowframe_layout.addStretch()
                    rowframe_layout.addWidget(otplabel)

                    copy_btn = QToolButton()
                    if os.path.exists("images/copy_icon.png"):
                        copy_icon = QIcon("images/copy_icon.png")
                        copy_btn.setIcon(copy_icon)
                        copy_btn.setIconSize(QSize(16, 16))
                    else:
                        logging.warning("missing copy icon")
                    #copy_btn.setPopupMode(QToolButton.InstantPopup)
                    copy_btn.setToolTip("Copy code to clipboard")
                    copy_btn.clicked.connect(lambda _, otp=otp, idx=index, acc=account: self.copy_to_clipboard(otp, idx, acc))
                    rowframe_layout.addWidget(copy_btn)

                    edit_btn = QToolButton()
                    if os.path.exists("images/pencil_icon.png"):
                        edit_icon = QIcon("images/pencil_icon.png")
                        edit_btn.setIcon(edit_icon)
                        edit_btn.setIconSize(QSize(16, 16))  # Adjust size as needed
                    else:
                        logging.warning("missing pencil icon")
                    #edit_btn.setPopupMode(QToolButton.InstantPopup)
                    edit_btn.setToolTip("Edit account")  # Add tooltip for accessibility
                    # pass the current values of index, account to show_edit_account_form
                    edit_btn.clicked.connect(lambda _, account=account, idx=index: self.show_edit_account_form(idx, account=account))
                    rowframe_layout.addWidget(edit_btn)

                    self.scroll_layout.addWidget(row_frame)

        self.scroll_layout.addStretch() # this keeps the rows bunched up at the top

    def update_timer(self):
        time_remaining = 30 - (int(time.time()) % 30)
        if self.vault_empty:
            display_time = "  "
        else:
            display_time = str(time_remaining)
            # pad the display time if necessary
            if len(display_time) < 2:
                display_time = ' ' + display_time
        self.timer_label.setText(display_time)
        # refresh the display every 30 seconds
        # NB: assumes timer period is 30 seconds for all accounts    
        if time_remaining == 30:
            self.display_accounts()

    def copy_to_clipboard(self, otp, idx, account):
        pyperclip.copy(otp)
        print(f"Copied OTP: {otp}")
        now = datetime.datetime.now()
        account.last_used = now.strftime("%Y-%m-%d %H:%M")
        self.controller.update_account(idx,account)

    def show_add_account_form(self):
        print("Starting Show_add_account_form")
        if self.app_config.is_auto_find_qr_enabled():
            # go find_qr_code
            qr_data = self.controller.find_qr_code()
            # TODO: Check for multiple QR codes found
            if qr_data:
                fields = Account(qr_data[0],qr_data[1],qr_data[2])
                self.current_dialog = ConfirmAccountDialog(self.controller)
                self.current_dialog.set_account(fields)
                retcode = self.current_dialog.exec_()
                print (f"Confirm dialog closing code:  {retcode}")
                self.display_accounts()
                # if user confirmed the account data, return to main window
                if retcode == 1:
                    return
        
        print ("Show_add_account_form is ready to exec() the dialog")
        self.current_dialog = AddAccountDialog(self.controller)
        self.current_dialog.exec_()
        # Refresh the display
        self.display_accounts()

    def show_edit_account_form(self,index,account):
        print (f"entering show_edit_account_form with {index} {account.provider}")
        dialog_EditAcct = EditAccountDialog(self, self.controller, index, account)
        dialog_EditAcct.exec_()
        self.display_accounts()

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

    def show_backup_restore_dialog(self):
        dialog = BackupRestoreDialog(self.controller.account_manager, self)
        dialog.exec_()

    def import_accounts(self):
        pass

    def backup_restore(self):
        pass

    def reorder_accounts(self):
        pass

    def manage_providers(self):
        pass

    def settings(self):
        pass

    def show_about_dialog(self):
        pass

class EditAccountDialog(QDialog):
    def __init__(self, parent, controller, index, account):
        super().__init__(parent)
        self.controller = controller
        self.secrets_manager = SecretsManager()
        self.account = account
        self.index = index

        print (f"EditAccountDialog init got {index} {account.provider}")
        self.setWindowTitle("Edit Account")
        self.setMinimumWidth(475)

        # Main layout
        layout = QVBoxLayout(self)

        # Form section
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
        form_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout = QGridLayout(form_frame)

        # Provider
        form_layout.addWidget(QLabel("Provider:"), 0, 0, Qt.AlignRight)
        self.provider_entry = QLineEdit(account.provider)
        form_layout.addWidget(self.provider_entry, 0, 1)

        # Label
        form_layout.addWidget(QLabel("Label:"), 1, 0, Qt.AlignRight)
        self.label_entry = QLineEdit(account.label)
        form_layout.addWidget(self.label_entry, 1, 1)

        # Secret Key
        form_layout.addWidget(QLabel("Secret Key:"), 2, 0, Qt.AlignRight)
        self.secret_key_entry = QLineEdit(controller.secrets_manager.decrypt(account.secret))
        form_layout.addWidget(self.secret_key_entry, 2, 1)

        layout.addWidget(form_frame)

        # Button section
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(
            lambda _, account=account, idx=index: self.handle_update_request(idx, account=account))

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.confirm_delete_account())

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(cancel_btn)
        layout.addWidget(button_frame)

        # Last Used section
        last_used_frame = QFrame()
        last_used_frame.setFrameStyle(QFrame.StyledPanel)
        last_used_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        last_used_layout = QGridLayout(last_used_frame)

        # Last Used Label
        last_used_layout.addWidget(QLabel("Last Used:"), 0, 0, Qt.AlignRight)
        self.last_used_label = QLabel(account.last_used)
        last_used_layout.addWidget(self.last_used_label, 0, 1)

        # Reveal QR Code Button
        self.reveal_qr_button = QPushButton("Reveal QR code")
        self.reveal_qr_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.reveal_qr_button.clicked.connect(self.handle_QR_reveal)
        last_used_layout.addWidget(self.reveal_qr_button, 1, 0, 1, 2, Qt.AlignCenter)

        layout.addWidget(last_used_frame)

        # Add spacer to push buttons toward top
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)



    def handle_update_request(self,index, account):
        print (f"EditAcctDialog is handling update request for: {index} ")
        encrypted_secret = self.secrets_manager.encrypt(self.secret_key_entry.text())
        up_account = Account(self.provider_entry.text(), self.label_entry.text(), encrypted_secret, account.last_used)
        self.controller.update_account(index, up_account)
        self.close()

    def confirm_delete_account(self):
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f'Are you sure you want to delete this account?\n\n{self.account.provider} ({self.account.label})\n\n'+
            f"You will lose access to {self.account.provider} unless you have saved the restore codes. (Learn more)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.controller.delete_account(self.account)
            self.accept()

    def handle_QR_reveal(self):
        # TODO: more robust flag
        if self.reveal_qr_button.text() == "Reveal QR code":
            # Generate QR code
            qr_code_image = self.controller.generate_qr_code(self.account)
            pixmap = QPixmap()
            pixmap.loadFromData(qr_code_image)
            self.qr_code_label = QLabel()
            self.qr_code_label.setPixmap(pixmap)
            self.layout().addWidget(self.qr_code_label)
            self.reveal_qr_button.setText("Hide QR code")
        else:
            # Hide QR code
            self.qr_code_label.deleteLater()
            self.qr_code_label = QLabel()
            self.reveal_qr_button.setText("Reveal QR code")
            
if __name__ == '__main__':
    import sys
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    app = QApplication(sys.argv)
    controller = AppController()
    window = AppView(controller)  # Pass your controller here
    window.show()
    sys.exit(app.exec_())
