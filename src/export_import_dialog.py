from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QRadioButton, \
    QButtonGroup, QToolButton, QHBoxLayout

from account_entry_dialog import help_style
from account_manager import AccountManager

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
        export_info_btn.setToolTip("Save the vault to an external file.")
        info_icon = QIcon("images/question_mark_icon_16.png")
        export_info_btn.setIcon(info_icon)
        export_info_btn.setIconSize(QSize(16, 16))
        # Make square button invisible so only circular icon shows
        export_info_btn.setStyleSheet(help_style)
        export_panel.addWidget(export_info_btn)
        export_panel.addStretch()
        layout.addLayout(export_panel)

        choose_label = QLabel("Choose export file format:")
        layout.addWidget(choose_label)
        self.button_group = QButtonGroup()
        self.button_able = QRadioButton("EasyAuth")
        self.button_baker = QRadioButton("Aegis")
        self.button_charly = QRadioButton("FreeOTP")
        self.button_group.addButton(self.button_able)
        self.button_group.addButton(self.button_baker)
        self.button_group.addButton(self.button_charly)

        self.button_able.setChecked(True)  # Set "EasyAuth" as default selected

        layout.addWidget(self.button_able)
        layout.addWidget(self.button_baker)
        layout.addWidget(self.button_charly)

        file_choose_btn = QPushButton("Choose export file")
        layout.addWidget(file_choose_btn)
        file_choose_btn.clicked.connect(lambda: self.export())

        self.setLayout(layout)

        # Import panel
        import_label = QLabel("Import")
        import_label.setFont(QFont("Sans-serif",12))
        layout.addWidget(import_label)

        import_easy_auth_btn = QPushButton("Choose import file")
        import_easy_auth_btn.setEnabled(True)
        import_easy_auth_btn.clicked.connect(lambda: self.importer())
        layout.addWidget(import_easy_auth_btn)

        self.setLayout(layout)

    def export(self, ):
        # Find out which radio button is selected
        selected_button = self.button_group.checkedButton()
        export_file_type = selected_button.text()
        # TODO: convert accounts to desired format
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, f"Export to {export_file_type} format", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            if not file_path.endswith(".json"):
                file_path += ".json"
            try:
                self.account_manager.export_accounts(file_path)
                QMessageBox.information(self, "Success", f"Accounts successfully exported up to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export accounts: {e}")
        self.close()

    def importer(self):
        app_name= "EasyAuth"
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, f"Import {app_name} Accounts", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            try:
                # Since import is destructive, get confirmation
                account_list = self.account_manager.import_preview(file_path)
                if account_list is None or len(account_list) == 0:
                    QMessageBox.information(self,"Information","The selected import file is empty, no action taken.")
                    self.close()
                    return
                confirm_count = len(account_list)
                confirm_msg = f"WARNING: Import will overwrite your current vault.\n"
                confirm_msg += "Do you really want to import "
                limit = 3
                if confirm_count < limit:
                    limit = confirm_count
                for idx in range(limit):
                    confirm_msg += account_list[idx].provider + ", "
                confirm_msg += f"and {confirm_count - limit} others?"
                reply = QMessageBox.question(self, "Confirm import to vault", confirm_msg)
                if reply == QMessageBox.Yes:
                    self.account_manager.import_accounts(file_path)
                    QMessageBox.information(self, "Success", f"Accounts successfully imported from  {file_path}")
                    self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import accounts: {e}")
