from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QRadioButton, \
    QButtonGroup, QToolButton, QHBoxLayout, QSizePolicy

from account_entry_dialog import info_btn_style
from account_manager import AccountManager
""" Reference: Gnome-Authenticator backup JSON format
  {
    "secret": "37E4WSILXWLQ87C2QJ4MXABCD2OW7L6H",
    "issuer": "Figma",
    "label": "fig@figma.commy",
    "digits": 6,
    "type": "totp",
    "algorithm": "sha1",
    "thumbnail": null,
    "last_used": 0,
    "used_frequency": 0,
    "counter": 1,
    "tags": [],
    "period": 30
  }
"""

class ExportImportDialog(QDialog):
    def __init__(self, account_manager: AccountManager, parent=None):
        super(ExportImportDialog, self).__init__(parent)
        self.account_manager = account_manager
        self.setWindowTitle("Export/Import")
        self.setGeometry(100, 100, 250, 300)

        layout = QVBoxLayout()

        # Export panel
        export_panel = QHBoxLayout()
        export_label = QLabel("Export")
        export_label.setFont(QFont("Sans-serif",12))
        export_panel.addWidget(export_label)
        export_info_btn = QToolButton()
        export_info_btn.setToolTip("Save the vault to an external file. Secret keys are NOT encrypted!")
        info_icon = QIcon("images/question_mark_icon_16.png")
        export_info_btn.setIcon(info_icon)
        export_info_btn.setIconSize(QSize(16, 16))
        export_info_btn.setStyleSheet(info_btn_style)
        export_panel.addWidget(export_info_btn)
        export_panel.addStretch()
        layout.addLayout(export_panel)

        choose_label = QLabel("Choose export file format:")
        layout.addWidget(choose_label)
        self.button_group = QButtonGroup()
        self.button_able = QRadioButton("EasyAuth (Plain-text JSON format)")
        self.button_charly = QRadioButton("FreeOTP+, others (Plain-text OTPauth URI format)")
        self.button_group.addButton(self.button_able)
        self.button_group.addButton(self.button_charly)
        self.button_able.setCheckable(True)
        self.button_charly.setCheckable(True)

        self.button_able.setChecked(True)  # Set "EasyAuth" as default selected

        layout.addWidget(self.button_able)
        layout.addWidget(self.button_charly)

        layout.addSpacing(10)  # Add vertical space

        file_choose_btn = QPushButton("Choose export file")
        file_choose_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_choose_btn.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(file_choose_btn)
        file_choose_btn.clicked.connect(lambda: self.export())

        self.setLayout(layout)

        layout.addSpacing(10)  # Add vertical space
        # Horizontal separator line
        separator = QLabel()
        separator.setFrameStyle(QLabel.HLine | QLabel.Sunken)
        layout.addWidget(separator)

        # Import panel
        import_label = QLabel("Import")
        import_label.setFont(QFont("Sans-serif",12))
        layout.addWidget(import_label)

        import_easy_auth_btn = QPushButton("Choose import file")
        import_easy_auth_btn.setEnabled(True)
        import_easy_auth_btn.setFocusPolicy(Qt.NoFocus)
        import_easy_auth_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        import_easy_auth_btn.clicked.connect(lambda: self.importer())
        layout.addWidget(import_easy_auth_btn)

        self.setLayout(layout)

    def export(self, ):
        # Find out which radio button is selected
        selected_button = self.button_group.checkedButton()
        export_file_type = selected_button.text()
        filetype_id = self.button_group.checkedId()
        print (f"Export called: {export_file_type} id={filetype_id}")
        options = QFileDialog.Options()
        if filetype_id == -2:
            file_path, _ = QFileDialog.getSaveFileName(self, f"Export to {export_file_type} format", "", "JSON Files (*.json);;All Files (*)", options=options)
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, f"Export to {export_file_type} format", "",
                                                       "TXT Files (*.txt);;All Files (*)", options=options)
        if file_path:
            if filetype_id == -2 and not file_path.endswith(".json"):
                file_path += ".json"
            if filetype_id == -3 and not file_path.endswith(".txt"):
                file_path += ".txt"

            try:
                self.account_manager.export_accounts(file_path,export_file_type)
                QMessageBox.information(self, "Success", f"Accounts successfully exported up to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export accounts: {e}")
        self.close()

    def build_provider_sample(self, account_list):
        """ build a string with names of first few providers to be imported """
        confirm_count = len(account_list)
        sample_msg = ""
        limit = 3
        if confirm_count < limit:
            limit = confirm_count
        for idx in range(limit):
            sample_msg += account_list[idx].issuer + ", "
        return sample_msg, confirm_count - limit

    def importer(self):
        app_name= "EasyAuth"
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, f"Import {app_name} Accounts", "", "JSON Files (*.json);;TXT Files (*.txt);;All Files (*)", options=options)
        if file_path:
            try:
                # Since import is destructive, get confirmation
                account_list = self.account_manager.import_preview(file_path)
                if account_list is None or len(account_list) == 0:
                    QMessageBox.information(self,"Information","The selected import file is empty or invalid, no action taken.")
                    self.close()
                    return
                sample_msg, remainder = self.build_provider_sample(account_list)
                confirm_msg = f"WARNING: Import will overwrite your current vault.\n"
                confirm_msg += "Do you really want to import "
                confirm_msg += sample_msg + f"and {remainder} others?"
                reply = QMessageBox.question(self, "Confirm import to vault", confirm_msg)
                if reply == QMessageBox.Yes:
                    self.account_manager.import_accounts(file_path)
                    QMessageBox.information(self, "Success", f"Accounts successfully imported from  {file_path}")
                    self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import accounts: {e}")
