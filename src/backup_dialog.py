from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from models_old import AccountManager

class BackupRestoreDialog(QDialog):
    def __init__(self, account_manager: AccountManager, parent=None):
        super(BackupRestoreDialog, self).__init__(parent)
        self.account_manager = account_manager
        self.setWindowTitle("Backup/Restore")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Backup panel
        backup_label = QLabel("Backup")
        layout.addWidget(backup_label)

        backup_easy_auth_btn = QPushButton("EasyAuth")
        backup_easy_auth_btn.clicked.connect(lambda: self.backup("EasyAuth"))
        layout.addWidget(backup_easy_auth_btn)

        backup_aegis_btn = QPushButton("Aegis")
        backup_aegis_btn.clicked.connect(lambda: self.backup("Aegis"))
        layout.addWidget(backup_aegis_btn)

        backup_freeotp_btn = QPushButton("FreeOTP")
        backup_freeotp_btn.clicked.connect(lambda: self.backup("FreeOTP"))
        layout.addWidget(backup_freeotp_btn)

        # Restore panel
        restore_label = QLabel("Restore")
        layout.addWidget(restore_label)

        restore_easy_auth_btn = QPushButton("EasyAuth")
        restore_easy_auth_btn.clicked.connect(lambda: self.restore("EasyAuth"))
        layout.addWidget(restore_easy_auth_btn)

        restore_aegis_btn = QPushButton("Aegis")
        restore_aegis_btn.clicked.connect(lambda: self.restore("Aegis"))
        layout.addWidget(restore_aegis_btn)

        restore_freeotp_btn = QPushButton("FreeOTP")
        restore_freeotp_btn.clicked.connect(lambda: self.restore("FreeOTP"))
        layout.addWidget(restore_freeotp_btn)

        self.setLayout(layout)

    def backup(self, app_name):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, f"Backup {app_name} Accounts", "", "JSON Files (*.json);;All Files (*)", options=options)
        if not file_path.endswith(".json"):
            file_path += ".json"
        if file_path:
            try:
                self.account_manager.backup_accounts(file_path)
                QMessageBox.information(self, "Success", f"Accounts successfully backed up to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to backup accounts: {e}")

    def restore(self, app_name):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, f"Restore {app_name} Accounts", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            # Implement restore functionality here
            QMessageBox.information(self, "Info", f"Restore functionality for {app_name} is not implemented yet.")