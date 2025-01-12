import json
import logging
import os
from dataclasses import asdict

from PyQt5.QtWidgets import (QMainWindow, QApplication,
    QSizePolicy, QMenuBar, QMenu, QAction, QLabel, QLineEdit, QToolBar, QScrollArea, 
    QToolButton, QDialog, QLabel, QPushButton, QGridLayout, QLineEdit, QVBoxLayout, 
    QHBoxLayout, QWidget, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl
from PyQt5.QtGui import QFont, QIcon, QPixmap, QDesktopServices
import pyotp
import time, datetime
import pyperclip

import cipher_funcs
from account_add_dialog import AddAccountDialog
from account_confirm_dialog import ConfirmAccountDialog
from quick_start_dialog import QuickStartDialog
from preferences_dialog import PreferencesDialog
from backup_dialog import BackupRestoreDialog   
from appconfig import AppConfig
from controllers import AppController
from models_singleton import AccountManager
from account_edit_dialog import EditAccountDialog
from reorder_dialog import ReorderDialog

class AppView(QMainWindow):
    def __init__(self, ):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        #self.controller = controller
        self.account_manager = AccountManager()
        #self.controller.set_view(self)
        self.vault_empty = False # Don't display timer if vault empty
        self.app_config = AppConfig() # Get the global AppConfig instance
        self.current_dialog = None
        self.setWindowTitle("Easy Auth")
        self.setGeometry(100, 100, 650, 400)
        
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

        preferences_action = QAction('Preferences', self)
        preferences_action.triggered.connect(self.show_preferences_dialog)
        file_menu.addAction(preferences_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        reorder_action = QAction('Reorder Accounts', self)
        reorder_action.triggered.connect(self.show_reorder_dialog)
        tools_menu.addAction(reorder_action)
        
        providers_action = QAction('Providers', self)
        providers_action.triggered.connect(self.manage_providers)
        tools_menu.addAction(providers_action)
        

        # Help menu
        help_menu = menubar.addMenu('Help')
        quick_start_action = QAction("Quick Start",self)
        quick_start_action.triggered.connect(self.show_quick_start_dialog)
        help_menu.addAction(quick_start_action)
        userManualAction = QAction("User Manual", self)
        userManualAction.triggered.connect(self.open_user_manual)
        help_menu.addAction(userManualAction)
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

        # Add spacer to push timer to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        # Timer label
        timer_font = QFont("Courier", 24, QFont.Bold)
        self.timer_label = QLabel("  ")
        self.timer_label.setToolTip("Time remaining until current TOTP code expires.")
        self.timer_label.setFont(timer_font)
        self.timer_label.setStyleSheet("""
            QLabel {
                background-color: lightgray;
                color: black;
                padding: 3px 15px;
                border-radius: 15px;
            }
            QToolTip {
                color: black;
                background-color: ivory;
                border: 1px solid black;
            }
        """)
        # Set custom style for the tooltip
        # self.timer_label.setStyleSheet(
        #     "QToolTip { color: black; background-color: lightblue; border: 1px solid black; }")

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
        self.account_manager.load_accounts()

        # Clear the existing widgets in the scroll_layout
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Check if the accounts list is empty
        if not self.account_manager.accounts:
            self.vault_empty = True
            # Display a three-line help message
            help_message = [
                "Your vault is empty.",
                "The vault stores two-factor authentication keys",
                "provided by a website or other online service.",
                "Store your secret key by clicking 'Add Account'"
            ]
            for line in help_message:
                help_label = QLabel(line)
                help_label.setAlignment(Qt.AlignCenter)
                self.scroll_layout.addWidget(help_label)
            view_quick_btn = QPushButton("View Quick Start")
            view_quick_btn.clicked.connect(self.show_quick_start_dialog)
            view_quick_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.scroll_layout.addWidget(view_quick_btn,alignment=Qt.AlignCenter)
        else:
            self.vault_empty = False
            # Adjust the spacing of the scroll_layout
            self.scroll_layout.setSpacing(2)  # Set vertical spacing between rows
            for index, account in enumerate(self.account_manager.accounts):
                if search_term in account.provider.lower():
                    secret_key = cipher_funcs.decrypt(account.secret)
                    # I think the preconditions make catching this exception superfluous.
                    try:
                        otp = pyotp.TOTP(secret_key).now()
                    except:
                        otp = "??????"
                    row_frame = QFrame()
                    row_frame.setFrameShape(QFrame.StyledPanel)
                    # each row can expand horizontally but is fixed vertically, so they don't expand to fill up the scroll frame.
                    row_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    # Set internal padding for the frame
                    row_frame.setContentsMargins(0,0,0,0)

                    rowframe_layout = QHBoxLayout(row_frame)
                    rowframe_layout.setSpacing(5)  # Set horizontal spacing between widgets in the row
                    # Assuming your_frame is inside a parent widget with a layout
                    # Set external padding around the frame by adjusting the layout margins of the parent widget
                    #rowframe_layout.layout().setContentsMargins(10, 10, 10, 10)
                    icon_label = QLabel()
                    provider_icon_img = self.account_manager.get_provider_icon_name(account.provider)
                    if provider_icon_img:
                        provider_icon = QPixmap(provider_icon_img)
                        icon_label.setPixmap(provider_icon)
                    else:
                        provider_initial = account.provider[0]  # get first letter of provider name
                        icon_label.setText('(' + provider_initial + ')')
                    rowframe_layout.addWidget(icon_label)

                    label_string = f"{account.provider} ({account.label})"
                    if len(label_string) > 45:
                        label_string = label_string[:45] + "..."
                    label = QLabel(label_string)
                    label.setFont(QFont("Arial", 12))
                    otplabel = QLabel(f"{otp}")
                    otplabel.setFont(QFont("DejaVu Sans Mono", 14)) #, QFont.Bold))
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
        self.account_manager.update_account(idx,account)
        print(f"Updated account: {idx} {account.provider} ({account.label})")

    def show_add_account_form(self):
        """ User clicked Add Account button """
        print("Starting Show_add_account_form")
        # Are we in auto_find mode?
        if self.app_config.is_auto_find_qr_enabled():
            confirmDialog = ConfirmAccountDialog()
            from qr_hunting import fetch_qr_code
            result_code = fetch_qr_code(confirmDialog)
            # if process returned True we should skip exec_
            #result_code = QDialog.result(self.current_dialog)
            print (f"AddAccountDialog closed with result code: {result_code}")
            if not result_code:
                self.current_dialog = AddAccountDialog()
                self.current_dialog.exec_()
        else:
            self.current_dialog = AddAccountDialog()
            self.current_dialog.exec_()
        # Refresh the display
        self.display_accounts()

    def show_edit_account_form(self,index,account):
        print (f"entering show_edit_account_form with {index} {account.provider}")
        dialog_EditAcct = EditAccountDialog(self, index, account)
        dialog_EditAcct.exec_()
        self.display_accounts()

    def show_preferences_dialog(self):
        dialog = PreferencesDialog(self)
        dialog.exec_()

    def show_backup_restore_dialog(self):
        dialog = BackupRestoreDialog(self.account_manager, self)
        dialog.exec_()

    def import_accounts(self):
        reply = QMessageBox.information(
            self,
            'Information',
            f'Importing accounts not yet implemented',
            QMessageBox.Ok
        )

    def show_reorder_dialog(self):
        account_list = self.account_manager.accounts
        dialog = ReorderDialog(account_list, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.accounts = dialog.get_ordered_accounts()
            # save back to model
            account_dicts = [asdict(account) for account in self.accounts]
            json_str = json.dumps(account_dicts)
            self.account_manager.set_accounts(json_str)
            # Update main window display
            self.display_accounts()

    def manage_providers(self):
        reply = QMessageBox.information(self, "Info", f'This feature not yet implemented.')

    def show_quick_start_dialog(self):
        dlg = QuickStartDialog()

    # TODO: Verify that app can be closed even if browser window remains open
    def open_user_manual(self):
        url = QUrl("https://example.com")
        QDesktopServices.openUrl(url)

    def show_about_dialog(self):
        reply = QMessageBox.information(
            self,
            'About',
            f'EasyAuth\n\n2FA authenticator\n\n' +
            f"Version 0.0.1\n\n" +
            "http://www.github.com/jdalbey/EasyAuth",
            QMessageBox.Ok
        )

# local main for unit testing
if __name__ == '__main__':
    import sys
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    app = QApplication(sys.argv)
    controller = AppController()
    window = AppView()
    window.show()
    sys.exit(app.exec_())
