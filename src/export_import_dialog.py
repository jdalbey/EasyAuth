import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QRadioButton, \
    QButtonGroup, QToolButton, QHBoxLayout, QSizePolicy
from utils import assets_dir
from styles import info_btn_style
from account_mgr import AccountManager

""" Export and Import features. """
class ExportImportDialog(QDialog):
    def __init__(self, parent=None):
        super(ExportImportDialog, self).__init__(parent)
        self.account_manager = AccountManager()
        self.setWindowTitle("Export/Import")
        self.setMinimumSize(250, 300)
        self.setWindowFlags(Qt.WindowTitleHint | Qt.Dialog | Qt.WindowCloseButtonHint) # x-platform consistency

        layout = QVBoxLayout()

        # Export panel
        export_panel = QHBoxLayout()
        export_label = QLabel("Export")
        export_label.setFont(QFont("Sans-serif",12))
        export_panel.addWidget(export_label)
        export_info_btn = QToolButton()
        export_info_btn.setToolTip("Save the vault to an external file. Secret keys are NOT encrypted!")
        info_icon = QIcon(os.path.join(assets_dir(), "question_mark_icon.svg"))
        export_info_btn.setIcon(info_icon)
        export_info_btn.setIconSize(QSize(16, 16))
        export_info_btn.setStyleSheet(info_btn_style)
        export_panel.addStretch()
        export_panel.addWidget(export_info_btn,alignment=Qt.AlignRight)
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

        self.file_choose_btn = QPushButton("Choose &export file")
        self.file_choose_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.file_choose_btn.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.file_choose_btn)
        self.file_choose_btn.clicked.connect(lambda: self.export())

        self.setLayout(layout)

        layout.addSpacing(10)  # Add vertical space
        # Horizontal separator line
        separator = QLabel()
        separator.setFrameStyle(QLabel.HLine | QLabel.Sunken)
        layout.addWidget(separator)

        # Import panel
        import_panel = QHBoxLayout()
        import_label = QLabel("Import")
        import_label.setFont(QFont("Sans-serif",12))
        import_panel.addWidget(import_label)
        import_info_btn = QToolButton()
        import_info_btn.setToolTip("Merge an external file into the vault.")
        info_icon = QIcon(os.path.join(assets_dir(), "question_mark_icon.svg"))
        import_info_btn.setIcon(info_icon)
        import_info_btn.setIconSize(QSize(16, 16))
        import_info_btn.setStyleSheet(info_btn_style)
        import_panel.addStretch()
        import_panel.addWidget(import_info_btn,alignment=Qt.AlignRight)
        layout.addLayout(import_panel)

        notify_label = QLabel("File format will be auto-detected.")
        notify_label.setFont(QFont("Sans-serif",8))
        layout.addWidget(notify_label)

        self.import_easy_auth_btn = QPushButton("Choose &import file")
        self.import_easy_auth_btn.setEnabled(True)
        self.import_easy_auth_btn.setFocusPolicy(Qt.NoFocus)
        self.import_easy_auth_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.import_easy_auth_btn.clicked.connect(lambda: self.importer())
        layout.addWidget(self.import_easy_auth_btn)

        self.setLayout(layout)

    def is_empty_vault(self):
        """ Check that we have any entries to export. """
        entries = self.account_manager.get_accounts()
        return len(entries) == 0

    def export(self):
        """ Export the vault to an external file. """
        if self.is_empty_vault():
            QMessageBox.information(self, "Alert", f"Vault is empty, nothing to export.")
            self.close()
            return

        # Find out which radio button is selected
        export_file_types = ['json','uri']
        # Oddly radio button checkedId is -2 or -3, so map to 0,1
        file_format = export_file_types[(self.button_group.checkedId() * -1) -2]

        # Present a save file chooser dialog
        options = QFileDialog.Options()
        if file_format == 'json':
            file_path, _ = QFileDialog.getSaveFileName(self, f"Export to {file_format} format", "", "JSON Files (*.json);;All Files (*)", options=options)
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, f"Export to {file_format} format", "",
                                                       "TXT Files (*.txt);;All Files (*)", options=options)
        if file_path:
            if file_format == 'json' and not file_path.endswith(".json"):
                file_path += ".json"
            if file_format == 'uri' and not file_path.endswith(".txt"):
                file_path += ".txt"

            try:
                # Go export the vault to chosen file
                self.account_manager.export_accounts(file_path,file_format)
                QMessageBox.information(self, "Success", f"Vault successfully exported up to {file_path}")
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export vault: {e}")
                self.close()

    def build_provider_preview(self, account_list):
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
        """ Import items from saved file into vault. """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, f"Import vault entries", "", "All Files (*)", options=options)
        if file_path:
            try:
                # Since import is destructive, get confirmation
                account_list = self.account_manager.import_preview(file_path)
                if isinstance(account_list,int) or account_list is None or len(account_list) == 0:
                    QMessageBox.information(self,"Information","The selected import file is empty or invalid, no action taken.")
                    self.close()
                    return
                sample_msg, remainder = self.build_provider_preview(account_list)
                confirm_msg = f"Import will merge these items with your current vault:\n"
                confirm_msg += sample_msg + f"and {remainder} others.  Proceed?"
                reply = QMessageBox.question(self, "Confirm import to vault", confirm_msg)
                if reply == QMessageBox.Yes:
                    # get return value for # of conflicts
                    conflict_count = self.account_manager.import_accounts(file_path)
                    # Report number of conflicts if > 0 and note (marked by !)
                    if conflict_count > 0:
                        QMessageBox.information(self,"Alert", f"Import resulted in {conflict_count} conflicts (flagged with '!').")
                        self.close()
                        return
                    QMessageBox.information(self, "Success", f"Vault successfully imported from  {file_path}")
                    self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import vault: {e}")


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