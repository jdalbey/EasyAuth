import json
import sys, logging
from dataclasses import asdict

from PyQt5.QtWidgets import (QMainWindow, QApplication,
    QSizePolicy, QMenuBar, QMenu, QAction, QLabel, QLineEdit, QToolBar, QScrollArea,
    QToolButton, QDialog, QLabel, QPushButton, QGridLayout, QLineEdit, QVBoxLayout,
    QHBoxLayout, QWidget, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl, QRect
from PyQt5.QtGui import QFont, QIcon, QPixmap, QDesktopServices
import pyotp
import time, datetime
import pyperclip
import qdarktheme
from provider_map import Providers
from qr_hunting import fetch_qr_code
import cipher_funcs
from account_add_dialog import AddAccountDialog
from quick_start_dialog import QuickStartDialog
from preferences_dialog import PreferencesDialog
from export_import_dialog import ExportImportDialog
from appconfig import AppConfig
from account_manager import AccountManager
from account_edit_dialog import EditAccountDialog
from reorder_dialog import ReorderDialog
from assets.styles import dark_qss, light_qss
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
        self.logger.debug("view init complete")

    def create_menubar(self):
        # Create menubar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')
        add_account_action = QAction('Add Account', self)
        add_account_action.setShortcut('Ctrl+A')
        add_account_action.triggered.connect(self.show_add_account_form)
        file_menu.addAction(add_account_action)

        file_menu.addSeparator()

        export_action = QAction('Export/Import', self)
        export_action.triggered.connect(self.show_export_import_dialog)
        file_menu.addAction(export_action)

        preferences_action = QAction('Preferences', self)
        preferences_action.setShortcut('Ctrl+P')
        preferences_action.triggered.connect(self.show_preferences_dialog)
        file_menu.addAction(preferences_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        reorder_action = QAction('Reorder Accounts', self)
        reorder_action.triggered.connect(self.show_reorder_dialog)
        tools_menu.addAction(reorder_action)

        sort_menu = tools_menu.addMenu('Sort Accounts')
        alpha_sort_action = QAction("Alphabetically", self)
        recency_action = QAction("Recently Used", self)
        alpha_sort_action.triggered.connect(self.do_alpha_sort_action)
        recency_action.triggered.connect(self.do_recency_sort_action)
        sort_menu.addAction(alpha_sort_action)
        sort_menu.addAction(recency_action)

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
        toolbar.setMovable(False)
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
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setToolTip("Time remaining until current TOTP code expires.")
        self.timer_label.setFont(timer_font)
        toolbar.addWidget(self.timer_label)

    def create_main_panel(self):
        # Create scrollable area for main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)
        self.set_theme()

    def set_theme(self):
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
            self.scroll_layout.setSpacing(2)  # Set vertical spacing between rows
            for index, account in enumerate(self.account_manager.accounts):
                if search_term in account.provider.lower():
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
                    rowframe_layout.setSpacing(5)  # Set horizontal spacing between widgets in the row
                    # Assuming your_frame is inside a parent widget with a layout
                    # Set external padding around the frame by adjusting the layout margins of the parent widget
                    #rowframe_layout.layout().setContentsMargins(10, 10, 10, 10)
                    if self.app_config.is_display_favicons():
                        icon_label = self.providers.get_provider_icon(account.provider)
                        rowframe_layout.addWidget(icon_label)

                    label_string = f"{account.provider} ({account.label})"
                    if len(label_string) > 45:
                        label_string = label_string[:45] + "..."
                    provider_label = QLabel(label_string)
                    provider_label.setFont(QFont("Verdana", 12))
                    # provider_label.setStyleSheet("""
                    #     QLabel {
                    #         border: 1px;
                    #         background: transparent;
                    #         color: black;
                    #         font-size: 16px;
                    #         text-align: left;
                    #     }
                    # """)

                    edit_btn = QPushButton()
                    edit_btn.setObjectName("editButton")

                    edit_btn.setToolTip("Edit account")
                    # pass the current values of index, account to show_edit_account_form
                    edit_btn.clicked.connect(lambda _, account=account, idx=index: self.show_edit_account_form(idx, account=account))
                    rowframe_layout.addWidget(edit_btn)

                    otplabel = QPushButton(f"{otp}") # display the 6-digit code in the label
                    otplabel.setObjectName("otpLabel")
                    otplabel.setToolTip("Copy code to clipboard")
                    otplabel.clicked.connect(lambda _, otplabel=otplabel, idx=index, acc=account: self.copy_to_clipboard(otplabel, idx, acc))

                    rowframe_layout.addWidget(provider_label)
                    rowframe_layout.addWidget(edit_btn)
                    rowframe_layout.addStretch()
                    rowframe_layout.addWidget(otplabel)

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

    def copy_to_clipboard(self, totp_label, idx, account):
        """ @param totp_label is the label of the one-time password """
        pyperclip.copy(totp_label.text())
        self.logger.debug(f"Copied OTP: {totp_label.text()}")
        now = datetime.datetime.now()
        # update last used time
        account.last_used = now.strftime("%Y-%m-%d %H:%M:%S")
        self.account_manager.update_account(idx,account)
        self.logger.debug(f"Updated last_used time for: {idx} {account.provider} ({account.label})")

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
        # Are we in auto_find mode?
        if self.app_config.is_auto_find_qr_enabled():
            result_code = fetch_qr_code()
            # if process returned True we should skip exec_
            #result_code = QDialog.result(self.current_dialog)
            self.logger.debug (f"AddAccountDialog closed with result code: {result_code}")
            if not result_code:
                self.current_dialog = AddAccountDialog()
                self.current_dialog.exec_()
        else:
            self.current_dialog = AddAccountDialog()
            self.current_dialog.exec_()
        # Refresh the display
        self.display_accounts()

    def show_edit_account_form(self,index,account):
        self.logger.debug (f"entering show_edit_account_form with {index} {account.provider}")
        dialog_EditAcct = EditAccountDialog(self, index, account)
        dialog_EditAcct.exec_()
        self.display_accounts()

    def show_preferences_dialog(self):
        dialog = PreferencesDialog(self.q_app, parent=self)
        dialog.exec_()
        self.display_accounts()

    def show_export_import_dialog(self):
        dialog = ExportImportDialog(self.account_manager, self)
        dialog.exec_()
        # After restore, reload display
        self.display_accounts()

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

    def do_alpha_sort_action(self):
        self.account_manager.sort_alphabetically()
        self.accounts = self.account_manager.accounts
        self.display_accounts()

    def do_recency_sort_action(self):
        self.account_manager.sort_recency()
        self.accounts = self.account_manager.accounts
        self.display_accounts()

    # def manage_providers(self):
    #     reply = QMessageBox.information(self, "Info", f'This feature not yet implemented.')

    def show_quick_start_dialog(self):
        dlg = QuickStartDialog(self)

    # TODO: Verify that app can be closed even if browser window remains open

    def open_user_manual(self):
        url = QUrl("https://github.com/jdalbey/EasyAuth/blob/master/docs/user_manual.md")
        QDesktopServices.openUrl(url)

    def show_about_dialog(self):
        reply = QMessageBox.information(
            self,
            'About',
            f'EasyAuth\n\n2FA authenticator\n\n' +
            f"Version 0.0.1\n\n" +
            "http://www.github.com/jdalbey/EasyAuth\n\n" +
            f"Vault directory: " + self.app_config.get_os_data_dir(),
            QMessageBox.Ok
        )

    def closeEvent(self, event):
        geometry = self.geometry()
        print("Current window geometry:", QRect(geometry))
        print("Current window position:", self.pos().x(), " x ", self.pos().y())
        super().closeEvent(event)

# local main for unit testing
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppView()
    window.show()
    sys.exit(app.exec_())
