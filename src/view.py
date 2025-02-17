import json
import os
import sys, logging
from dataclasses import asdict

from PyQt5.QtWidgets import (QMainWindow, QApplication,
                             QSizePolicy, QAction, QToolBar, QScrollArea,
                             QDialog, QLabel, QPushButton, QLineEdit, QVBoxLayout,
                             QHBoxLayout, QWidget, QMessageBox, QFrame, QMenu, QFileDialog)
from PyQt5.QtCore import Qt, QTimer, QUrl, QRect
from PyQt5.QtGui import QFont, QDesktopServices, QPixmap, QKeySequence
import pyotp
import time, datetime
import pyperclip
import qdarktheme

import qr_funcs
from provider_search_dialog import ProviderSearchDialog
from qr_selection_dialog import QRselectionDialog
from utils import assets_dir
from provider_map import Providers
import cipher_funcs
from account_add_dialog import AddAccountDialog
from account_edit_dialog import EditAccountDialog
from quick_start_dialog import QuickStartDialog
from preferences_dialog import PreferencesDialog
from export_import_dialog import ExportImportDialog
from reorder_dialog import ReorderDialog
from appconfig import AppConfig
from account_manager import AccountManager, Account, OtpRecord
from styles import dark_qss, light_qss
from vault_details_dialog import VaultDetailsDialog
from vault_entry_dialog import VaultEntryDialog


class AppView(QMainWindow):
    def __init__(self, q_app):
        super().__init__()
        self.q_app = q_app
        self.logger = logging.getLogger(__name__)
        self.logger.debug("view init startup")
        self.account_manager = AccountManager()
        self.providers = Providers()
        self.vault_empty = False # Don't display timer if vault empty
        self.app_config = AppConfig() # Get the global AppConfig instance
        self.current_dialog = None
        self.quick_start_dialog = None  # Quick start is not showing

        self.setWindowTitle("EasyAuth")
        self.setGeometry(50, 50, 525, 600)

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        # Create GUI components
        self.create_main_panel()
        self.create_menubar()
        self.create_toolbar()

        self.start_timer()
        self.display_accounts()
        self.logger.debug("view init complete")

    def create_menubar(self):
        # Create menubar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        # Create the submenu
        submenu = QMenu('New Vault Entry', self)

        # Create actions for the submenu
        scanQRcode_action = QAction('Scan from QR code', self)
        scanQRcode_action.setShortcut(QKeySequence("Alt+S"))
        scanQRcode_action.triggered.connect(self.scan_QR_code_clickaction)

        openQRimage_action = QAction('Open QR image file', self)
        openQRimage_action.triggered.connect(self.get_qr_from_image)

        add_account_action = QAction('Enter Manually', self)
        add_account_action.setShortcut(QKeySequence("Alt+A"))

        add_account_action.triggered.connect(self.show_add_account_form)

        # Add the actions to the submenu
        submenu.addAction(scanQRcode_action)
        submenu.addAction(openQRimage_action)
        submenu.addAction(add_account_action)

        # Add the submenu to the File menu
        file_menu.addMenu(submenu)

        file_menu.addSeparator()

        export_action = QAction('Export/Import', self)
        export_action.setObjectName("exportAction")
        export_action.triggered.connect(self.show_export_import_dialog)
        file_menu.addAction(export_action)

        preferences_action = QAction('Preferences', self)
        preferences_action.setObjectName('preferencesAction')
        preferences_action.triggered.connect(self.show_preferences_dialog)
        file_menu.addAction(preferences_action)

        exit_action = QAction('Exit', self)
        exit_action.setObjectName(('exitAction'))
        exit_action.triggered.connect(sys.exit)
        exit_action.setShortcut(QKeySequence("Alt+x"))
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        tools_menu.setObjectName('tools_menu')
        reorder_action = QAction('Reorder Accounts', self)
        reorder_action.setObjectName("reorderAction")
        reorder_action.triggered.connect(self.show_reorder_dialog)
        tools_menu.addAction(reorder_action)

        sort_menu = tools_menu.addMenu('Sort Accounts')
        alpha_sort_action = QAction("Alphabetically", self)
        alpha_sort_action.setObjectName("sortAlphaAction")
        recency_action = QAction("Recently Used", self)
        frequency_action = QAction("Usage Count", self)
        alpha_sort_action.triggered.connect(self.do_alpha_sort_action)
        recency_action.triggered.connect(self.do_recency_sort_action)
        frequency_action.triggered.connect(self.do_frequency_sort_action)
        sort_menu.addAction(alpha_sort_action)
        sort_menu.addAction(recency_action)
        sort_menu.addAction(frequency_action)

        provider_search_action = QAction("Provider Search", self)
        provider_search_action.triggered.connect(self.show_provider_search_dialog)
        tools_menu.addAction(provider_search_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')
        quick_start_action = QAction("Quick Start",self)
        quick_start_action.setObjectName("quickstartAction")
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
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add quick access buttons
        self.add_btn = QPushButton('S\u0332'+"can QR code")  #Place underline under S
        self.add_btn.setObjectName("addAccountButton")
        self.add_btn.clicked.connect(self.scan_QR_code_clickaction)
        toolbar.addWidget(self.add_btn)

        # Add spacer to push search to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        # Create search and filter group
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setObjectName("searchBox")
        #enable a clear button within the search box, allowing users to quickly clear the text.
        #self.search_box.setClearButtonEnabled(True)

        # Create an action for the shortcut
        search_shortcut_action = QAction(self)
        search_shortcut_action.setShortcut(QKeySequence("Alt+e"))  #alt+e for 'search'
        search_shortcut_action.triggered.connect(self.search_box.setFocus)
        self.addAction(search_shortcut_action)
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
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setToolTip("Time remaining until current TOTP code expires.")
        self.timer_label.setFont(timer_font)
        self.timer_label.setStyleSheet("background-color:#ebebeb") # initially hidden (for light theme)
        toolbar.addWidget(self.timer_label)

    def create_main_panel(self):
        # Create scrollable area for main content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(self.scroll_area)
        self.set_theme()

    def set_theme(self):
        def adjust_theme_paths():
            """Return the correct path to images, whether in development or PyInstaller mode."""
            global dark_qss, light_qss

            if getattr(sys, 'frozen', False):
                adjusted_path = assets_dir().replace("\\", "/")
                dark_qss = dark_qss.replace("url(\"assets", f"url(\"{adjusted_path}")
                light_qss = light_qss.replace("url(\"assets", f"url(\"{adjusted_path}")

        adjust_theme_paths()
        # Get desired theme from Configuration
        chosen_theme = self.app_config.get_theme_name()
        self.logger.debug(f"Loading theme preference: {chosen_theme}")
        if chosen_theme == "dark":
            qdarktheme.setup_theme(chosen_theme,additional_qss=dark_qss)
        else:
            qdarktheme.setup_theme(chosen_theme,additional_qss=light_qss)

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
            # See if a QR code is visible.  Would be nice on an initally empty vault.
            # if not qr_hunting.process_qr_codes(called_from_Find_btn=False):
                # If not show empty_vault message
                self.vault_empty = True
                # Display a three-line help message
                help_message = [
                    "Your vault is empty.",
                    "The vault stores two-factor authentication keys",
                    "provided by a website or other online service.",
                    "Store your secret key by clicking 'Add Account'",
                    "or"
                ]
                for line in help_message:
                    help_label = QLabel(line)
                    help_label.setAlignment(Qt.AlignCenter)
                    self.scroll_layout.addWidget(help_label)
                view_quick_btn = QPushButton("View Quick Start")
                view_quick_btn.clicked.connect(self.show_quick_start_dialog)
                view_quick_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.scroll_layout.addWidget(view_quick_btn,alignment=Qt.AlignCenter)

        # If account list is not empty show it
        if self.account_manager.accounts:
            self.vault_empty = False
            # Adjust the spacing of the scroll_layout
            self.scroll_layout.setSpacing(1)  # Set vertical spacing between rows
            for index, account in enumerate(self.account_manager.accounts):
                if search_term in account.issuer.lower():
                    secret_key = cipher_funcs.decrypt(account.secret)
                    try:
                        otp = pyotp.TOTP(secret_key).now()
                    except:  # This would only happen from internal error
                        otp = "??????"
                    row_frame = QFrame()
                    row_frame.setFrameShape(QFrame.NoFrame) #QFrame.StyledPanel)
                    # each row can expand horizontally but is fixed vertically, so they don't expand to fill up the scroll frame.
                    row_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    # Set internal padding for the frame
                    row_frame.setContentsMargins(0,0,0,0)

                    rowframe_layout = QHBoxLayout(row_frame)
                    # Show Favicon
                    if self.app_config.is_display_favicons():
                        icon_label = self.providers.get_provider_icon(account.issuer)
                        rowframe_layout.addWidget(icon_label)
                    # Show Provider
                    provider_string = account.issuer
                    provider_label = QPushButton(provider_string)
                    provider_font = QFont("Verdana", 12)
                    provider_font.setUnderline(True)
                    provider_label.setFont(provider_font)
                    provider_label.setObjectName("providerLabel")
                    provider_label.setToolTip("View/edit details")
                    provider_label.clicked.connect(lambda _, account=account, idx=index: self.show_edit_account_form(idx, account=account))
                    provider_label.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to a pointing hand

                    # Show user
                    user_string = account.label
                    # Limit field length
                    label_length =  len(provider_string) + len(user_string)
                    if label_length > 31:
                        adjusted_length = 31 - len(provider_string)
                        user_string = user_string[:adjusted_length] + "..."
                    user_label = QLabel(user_string)
                    user_label.setFont(QFont("Verdana",12))

                    # Show TOTP code
                    otplabel = QPushButton(f"{otp}") # display the 6-digit code in the label
                    otplabel.setObjectName("otpLabel")
                    otplabel.setToolTip("Copy code to clipboard")
                    otplabel.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to a pointing hand
                    otplabel.clicked.connect(lambda _, otplabel=otplabel, idx=index, acc=account: self.copy_to_clipboard(otplabel, idx, acc))

                    rowframe_layout.addWidget(provider_label)
                    rowframe_layout.addWidget(user_label)
                    rowframe_layout.addStretch()
                    rowframe_layout.addWidget(otplabel)

                    self.scroll_layout.addWidget(row_frame)

        self.scroll_layout.addStretch() # this keeps the rows bunched up at the top

    def update_timer(self):
        """ Called every second to update the timer """
        # Ideally the styles would be handled in styles.py but I can't make it work.
        time_remaining = 30 - (int(time.time()) % 30)
        if self.vault_empty:
            display_time = "  "
            # Hide the timer if all accounts get deleted.
            self.timer_label.setStyleSheet("background-color:#ebebeb")
            if self.app_config.get_theme_name() == "dark":
                self.timer_label.setStyleSheet("background-color: #333333")
        else:
            # Display warning color if time running out
            if time_remaining <= 5:
                self.timer_label.setStyleSheet("background-color: #f7f48a ") #yellow")
                if self.app_config.get_theme_name() == "dark":
                    self.timer_label.setStyleSheet("background-color:#f7f48a;color:gray")
            else:
                self.timer_label.setStyleSheet("background-color:lightgray")
                if self.app_config.get_theme_name() == "dark":
                    self.timer_label.setStyleSheet("background-color:gray")

            display_time = str(time_remaining)
            # pad the display time if necessary
            if len(display_time) < 2:
                display_time = ' ' + display_time
        self.timer_label.setText(display_time)

        # refresh the display every 30 seconds
        # NB: assumes timer period is 30 seconds for all accounts
        if time_remaining == 30:
            self.display_accounts()

    def copy_to_clipboard(self, totp_label, idx, account):
        """ @param totp_label is the label of the one-time password """
        pyperclip.copy(totp_label.text())
        self.logger.debug(f"Copied OTP: {totp_label.text()}")
        now = datetime.datetime.now()
        # update last used time
        account.last_used = now.strftime("%Y-%m-%d %H:%M:%S")
        account.used_frequency += 1
        self.account_manager.update_account(idx,account)
        self.logger.debug(f"Updated last_used time for: {idx} {account.issuer} ({account.label})")

        # Show the floating message relative to the given label position
        popup = QLabel("Copied", self)
        popup.setObjectName("copyPopup")
        popup.setAlignment(Qt.AlignCenter)
        popup.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        popup.setStyleSheet("QLabel#copyPopup {background-color: #dff0d8; color: #3c763d; padding: 5px; border: 1px solid #d6e9c6;}")
        popup.resize(90, 40)
        # Calculate position just above the button
        button_geometry = totp_label.parent().mapToGlobal(totp_label.geometry().topLeft())
        button_center_x = button_geometry.x() + totp_label.width() // 2
        popup_x = button_center_x - popup.width() // 2
        popup_y = button_geometry.y() - popup.height() - 5  # 5 pixels gap above the button

        popup.move(popup_x, popup_y)
        popup.show()

        QTimer.singleShot(3000, popup.close)  # Hide after 3 seconds

    def show_add_account_form(self):
        """ User clicked Add Account button """
        self.logger.debug("Starting Show_add_account_form")
        try:
            add_dialog = VaultEntryDialog(self)
            add_dialog.show()
            add_dialog.exec_()
        except Exception as e:
            self.logger.error("AddAccountDialog not constructed.")

        # Refresh the display
        self.display_accounts()

    def show_edit_account_form(self,index,account):
        self.logger.debug (f"entering show_edit_account_form with {index} {account.issuer}")
        try:
            dialog_EditAcct = VaultDetailsDialog(self, index, account)
            dialog_EditAcct.exec_()
        except Exception as e:
            self.logger.error("EditAccountDialog not constructed.")
        self.display_accounts()

    def scan_QR_code_clickaction(self):
        if self.app_config.is_minimize_during_qr_search():
            self.hide()
            time.sleep(0.1)
            otprec = qr_funcs.obtain_qr_codes(self)
            self.show()
        else:
            otprec = qr_funcs.obtain_qr_codes(self)
        if otprec:
            self.show_popup()
            if self.account_manager.save_new_account(otprec):
                self.display_accounts()
            else:
                QMessageBox.information(self, "Warning", f"Account with provider {otprec.issuer} and user {otprec.label} already exists")

    def show_popup(self):
        # Show a floating message relative to the form fields
        popup = QLabel("QR code found!", self)
        popup.setObjectName("qr_code_found")
        popup.setAlignment(Qt.AlignCenter)
        popup.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        popup.setStyleSheet("QLabel#qr_code_found {font-size:16px; background-color: #dff0d8; color: #3c763d; padding: 5px; border: 1px solid #d6e9c6;}")
        popup.resize(150, 50)
        # Calculate position just above the field

        #button_geometry = self.entry_panel.mapToGlobal(self.entry_panel.provider_entry.geometry().topLeft())
        button_geometry = self.scroll_area.parent().mapToGlobal(self.scroll_area.geometry().topLeft())
        button_center_x = button_geometry.x() + self.scroll_area.width() // 2
        popup_x = button_center_x - popup.width() // 2
        popup_y = button_geometry.y() - popup.height() - 5  # 5 pixels gap above the button

        popup.move(popup_x, popup_y)
        popup.show()
        QTimer.singleShot(3000, popup.close)  # Hide after 3 seconds

    def get_qr_from_image(self):
        otprec = qr_funcs.open_qr_image(self)
        if otprec is not None:
            if self.account_manager.save_new_account(otprec):
                self.display_accounts()
            else:
                QMessageBox.information(self, "Warning",
                                        f"Account with provider {otprec.issuer} and user {otprec.label} already exists")

    def show_preferences_dialog(self):
        dialog = PreferencesDialog(parent=self)
        dialog.exec_()
        self.display_accounts()

    def show_export_import_dialog(self):
        dialog = ExportImportDialog(self)
        dialog.exec_()
        # After restore, reload display
        self.display_accounts()

    def show_reorder_dialog(self):
        account_list = self.account_manager.accounts
        dialog = ReorderDialog(account_list, self)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            self.accounts = dialog.get_ordered_accounts()
            # save back to model
            account_dicts = [asdict(account) for account in self.accounts]
            json_str = json.dumps(account_dicts)
            self.account_manager.set_accounts(json_str)
            # Update main window display
            self.display_accounts()

    def do_alpha_sort_action(self):
        self.account_manager.sort_alphabetically()
        self.accounts = self.account_manager.accounts
        self.display_accounts()

    def do_recency_sort_action(self):
        self.account_manager.sort_recency()
        self.accounts = self.account_manager.accounts
        self.display_accounts()

    def do_frequency_sort_action(self):
        self.account_manager.sort_frequency()
        self.accounts = self.account_manager.accounts
        self.display_accounts()

    def show_provider_search_dialog(self):
        dlg = ProviderSearchDialog()
        dlg.load_data()
        dlg.show()
        dlg.exec_()

    def show_quick_start_dialog(self):
        if self.quick_start_dialog is None or not self.quick_start_dialog.isVisible():
            self.quick_start_dialog = QuickStartDialog(self)
            self.quick_start_dialog.show()
        else:  # IF already open
            self.quick_start_dialog.raise_()
            self.quick_start_dialog.activateWindow()

    def open_user_manual(self):
        url = QUrl("https://github.com/jdalbey/EasyAuth/wiki/User-Manual#easyauth-user-manual")
        QDesktopServices.openUrl(url)

    def show_about_dialog(self):
        """ Show About dialog, including version and build date. """
        # Find the build date
        # If production mode, use path to bundled file created during build
        if getattr(sys, 'frozen', False):
            build_date_path = os.path.join(assets_dir(), "build_date.txt")
            version_path = os.path.join(assets_dir(), "version_info.txt")
            build_date = "Unknown"
            version_number = "0.0"
            # Read the build date from assets folder
            if os.path.exists(build_date_path):
                with open(build_date_path, "r") as f:
                    date_string = f.read().strip()
                    # Oddly, Windows date function prepends some junk, so here we skip over it by starting at [4:]
                    build_date = date_string[4:]
            # Read the version info from assets folder
            if os.path.exists(version_path):
                with open(version_path, "r") as f:
                    version_number = f.read().strip()
        else:  # For development version (running unbundled)
            now = datetime.datetime.now()
            build_date =  now.strftime("%Y-%m-%d %H:%M:%S")
            version_number = "0.0"

        msg = QMessageBox(self)
        msg.setText(f'EasyAuth\n\n2FA authenticator.\n\n' +
             f"Version {version_number}  {build_date}\n\n" +
             "http://www.github.com/jdalbey/EasyAuth\n\n" +
             f"Vault directory:\n" + self.app_config.get_os_data_dir())
        msg.setWindowTitle("About")
        pixmap = QPixmap(os.path.join(assets_dir(), "Vault.png"))
        msg.setIconPixmap(pixmap)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = msg.exec()

    def closeEvent(self, event):
        geometry = self.geometry()
        # TODO Save window geometry and position for next startup
        self.logger.debug(f"Current window geometry:  {QRect(geometry)}")
        self.logger.debug(f"Current window position: {self.pos().x()} x {self.pos().y()}")
        # Note that upon startup geometry says 100,100 but pos says 100,68.
        super().closeEvent(event)

"""    def showEvent(self, event):
        super().showEvent(event)
        # Store the initial size when the dialog is first shown
        if self.initial_size is None:
            self.initial_size = self.size()"""

# local main for unit testing
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppView(app)
    window.show()
    sys.exit(app.exec_())
