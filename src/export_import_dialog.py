from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from account_manager import AccountManager

class ExportImportDialog(QDialog):
    def __init__(self, account_manager: AccountManager, parent=None):
        super(ExportImportDialog, self).__init__(parent)
        self.account_manager = account_manager
        self.setWindowTitle("Export/Import")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Export panel
        export_label = QLabel("Export")
        layout.addWidget(export_label)

        export_easy_auth_btn = QPushButton("EasyAuth")
        export_easy_auth_btn.clicked.connect(lambda: self.export("EasyAuth"))
        layout.addWidget(export_easy_auth_btn)

        export_aegis_btn = QPushButton("Aegis")
        export_aegis_btn.setEnabled(False)
        export_aegis_btn.clicked.connect(lambda: self.export("Aegis"))
        layout.addWidget(export_aegis_btn)

        export_freeotp_btn = QPushButton("FreeOTP")
        export_freeotp_btn.setEnabled(False)
        export_freeotp_btn.clicked.connect(lambda: self.export("FreeOTP"))
        layout.addWidget(export_freeotp_btn)

        # Import panel
        import_label = QLabel("Import")
        import_label.setEnabled(True)
        layout.addWidget(import_label)

        import_easy_auth_btn = QPushButton("EasyAuth")
        import_easy_auth_btn.setEnabled(True)
        import_easy_auth_btn.clicked.connect(lambda: self.importer("EasyAuth"))
        layout.addWidget(import_easy_auth_btn)

        import_aegis_btn = QPushButton("Aegis")
        import_aegis_btn.setEnabled(False)
        import_aegis_btn.clicked.connect(lambda: self.importer("Aegis"))
        layout.addWidget(import_aegis_btn)

        import_freeotp_btn = QPushButton("FreeOTP")
        import_freeotp_btn.setEnabled(False)
        import_freeotp_btn.clicked.connect(lambda: self.importer("FreeOTP"))
        layout.addWidget(import_freeotp_btn)

        self.setLayout(layout)

    def export(self, app_name):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, f"Export {app_name} Accounts", "", "JSON Files (*.json);;All Files (*)", options=options)
        if not file_path.endswith(".json"):
            file_path += ".json"
        if file_path:
            try:
                self.account_manager.export_accounts(file_path)
                QMessageBox.information(self, "Success", f"Accounts successfully exported up to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export accounts: {e}")

    def importer(self, app_name):
        # Since import is destructive, get confirmation
        reply = QMessageBox.question(self,"Confirm Import","Warning: Import will overwrite everything in your vault. Proceed?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if reply == QMessageBox.Yes:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, f"Import {app_name} Accounts", "", "JSON Files (*.json);;All Files (*)", options=options)
            if file_path:
                try:
                    self.account_manager.import_accounts(file_path)
                    QMessageBox.information(self, "Success", f"Accounts successfully imported from  {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to import accounts: {e}")
