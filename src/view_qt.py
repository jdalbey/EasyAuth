import logging
import os

from PyQt5.QtWidgets import (QMainWindow, QApplication,
                           QSizePolicy, QMenuBar, QMenu, QAction, QLabel,
                           QLineEdit, QToolBar, QScrollArea, QToolButton,
                             QDialog, QLabel, QPushButton, QGridLayout,
                             QLineEdit, QVBoxLayout, QHBoxLayout, QWidget,
                             QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
import pyotp
import time
import pyperclip

from controllers import AppController


class AppView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.controller.set_view(self)
        
        self.setWindowTitle("Easy Auth")
        self.setGeometry(100, 100, 500, 400)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.create_menubar()
        self.create_toolbar()
        self.create_main_panel()

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
        backup_action.triggered.connect(self.backup_restore)
        file_menu.addAction(backup_action)

        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.settings)
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
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search...")
        search_box.setMaximumWidth(200)
        toolbar.addWidget(search_box)
        
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
            background-color: gray;
            color: yellow;
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
        
        self.refresh_accounts()
        self.start_timer()

    def start_timer(self):
        # Set up the QTimer to call update_timer every second
        self.timer = QTimer(self.central_widget)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 1000 milliseconds = 1 second


    def refresh_accounts(self):
        # for widget in self.scroll_layout.children():
        #     widget.deleteLater()
        accounts = self.controller.get_accounts()
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        # Adjust the spacing of the scroll_layout
        self.scroll_layout.setSpacing(2)  # Set vertical spacing between rows
        for index, account in enumerate(accounts):
            secret_key = self.controller.secrets_manager.decrypt(account.secret)
            otp = pyotp.TOTP(secret_key).now()
            row_frame = QFrame()
            row_frame.setFrameShape(QFrame.StyledPanel)
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
            otplabel.setFont(QFont("Courier", 14, QFont.Bold))
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
            copy_btn.clicked.connect(lambda: self.copy_to_clipboard(otp))
            rowframe_layout.addWidget(copy_btn)

            #rowframe_layout.addStretch()

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
            edit_btn.clicked.connect(lambda index=index, account=account: self.show_edit_account_form(index, account))
            rowframe_layout.addWidget(edit_btn)

            self.scroll_layout.addWidget(row_frame)


    def update_timer(self):
        time_remaining = 30 - (int(time.time()) % 30)
        self.timer_label.setText(f"{time_remaining}")
        if time_remaining == 30:
            self.refresh_accounts()

    def copy_to_clipboard(self, otp):
        pyperclip.copy(otp)
        print(f"Copied OTP: {otp}")
        
    def show_add_account_form(self):
        dialog_AddAcct = AddAccountDialog(self, self.controller)
        dialog_AddAcct.exec_()
        self.refresh_accounts()

    def show_edit_account_form(self,index,account):
        dialog_EditAcct = EditAccountDialog(self, self.controller, index, account)
        dialog_EditAcct.exec_()
        self.refresh_accounts()

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



class AddAccountDialog(QDialog):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("New Account")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Create a New Account from:")
        layout.addWidget(header_label)

        # QR Code section
        qr_screen_label = QLabel("• Fill the form automatically from a QR code on the screen")
        qr_screen_label.setContentsMargins(20, 0, 0, 0)
        layout.addWidget(qr_screen_label)

        find_qr_btn = QPushButton("Find QR code")
        #find_qr_btn.clicked.connect(self.controller.find_qr_code)
        find_qr_btn.clicked.connect(lambda: self.get_qr_code())
        find_qr_btn.setContentsMargins(40, 0, 0, 0)
        layout.addWidget(find_qr_btn)

        qr_file_label = QLabel("• Fill the form automatically from a QR image in a file")
        qr_file_label.setContentsMargins(20, 0, 0, 0)
        layout.addWidget(qr_file_label)

        open_file_btn = QPushButton("Open file")
        open_file_btn.clicked.connect(self.controller.open_qr_image)
        open_file_btn.setContentsMargins(40, 0, 0, 0)
        layout.addWidget(open_file_btn)

        manual_label = QLabel("• Enter the data manually")
        manual_label.setContentsMargins(20, 0, 0, 0)
        layout.addWidget(manual_label)

        # Form section
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
        form_layout = QGridLayout(form_frame)

        # Provider
        form_layout.addWidget(QLabel("Provider:"), 0, 0, Qt.AlignRight)
        self.provider_entry = QLineEdit()
        form_layout.addWidget(self.provider_entry, 0, 1)

        # Label
        form_layout.addWidget(QLabel("Label:"), 1, 0, Qt.AlignRight)
        self.label_entry = QLineEdit()
        form_layout.addWidget(self.label_entry, 1, 1)

        # Secret Key
        form_layout.addWidget(QLabel("Secret Key:"), 2, 0, Qt.AlignRight)
        self.secret_key_entry = QLineEdit()
        form_layout.addWidget(self.secret_key_entry, 2, 1)

        layout.addWidget(form_frame)

        # Button section
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.handle_save_account(
            self.provider_entry.text(),
            self.label_entry.text(),
            self.secret_key_entry.text()
        ))

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addWidget(button_frame)

    def handle_save_account(self, provider, label, secret):
        self.controller.save_account(provider, label, secret)
        self.close()

    def get_qr_code(self):
        provider, label, secret = self.controller.find_qr_code()
        self.provider_entry.setText(provider)
        self.label_entry.setText(label)
        self.secret_key_entry.setText(secret)


class EditAccountDialog(QDialog):
    def __init__(self, parent, controller, index, account):
        super().__init__(parent)
        self.controller = controller
        self.account = account
        self.index = index

        self.setWindowTitle("Edit Account")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)

        # Form section
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
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
        save_btn.clicked.connect(lambda: self.handle_update_request(
            self.index,
            self.provider_entry.text(),
            self.label_entry.text(),
            self.secret_key_entry.text()
        ))

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.confirm_delete_account())

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(cancel_btn)
        layout.addWidget(button_frame)

    def handle_update_request(self,index, provider, label, secret):
        self.controller.update_account(index, provider, label, secret)
        self.close()

    def confirm_delete_account(self):
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f'Are you sure you want to delete this account?\n\n{self.account.provider} - {self.account.label}',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.controller.delete_account(self.account)
            self.accept()


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