from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QLineEdit, QCheckBox)
from appconfig import AppConfig  # Import AppConfig

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 200)
        self.app_config = AppConfig() # Get the global AppConfig instance
        layout = QVBoxLayout()

        # Vault Path
        vault_path_label = QLabel("Vault Path:")
        self.vault_path_entry = QLineEdit(self.app_config.get_vault_path())
        layout.addWidget(vault_path_label)
        layout.addWidget(self.vault_path_entry)

        # Smart Filtering
        smart_filtering_label = QLabel("Smart Filtering (True/False):")
        self.smart_filtering_entry = QLineEdit(str(self.app_config.is_smart_filtering_enabled()))
        layout.addWidget(smart_filtering_label)
        layout.addWidget(self.smart_filtering_entry)

        # Theme Name
        theme_name_label = QLabel("Theme Name:")
        self.theme_name_entry = QLineEdit(self.app_config.get_theme_name())
        layout.addWidget(theme_name_label)
        layout.addWidget(self.theme_name_entry)

        # Alternate ID
        alt_id_label = QLabel("Alternate ID:")
        self.alt_id_entry = QLineEdit(self.app_config.get_alt_id() or "")
        layout.addWidget(alt_id_label)
        layout.addWidget(self.alt_id_entry)

        # Auto Find QR Code
        auto_find_qr_label = QLabel("Add Account finds QR code automatically:")
        self.auto_find_qr_checkbox = QCheckBox()
        self.auto_find_qr_checkbox.setChecked(self.app_config.is_auto_find_qr_enabled())
        layout.addWidget(auto_find_qr_label)
        layout.addWidget(self.auto_find_qr_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_settings(self):
        # Save the settings back to AppConfig
        self.app_config.set_vault_path(self.vault_path_entry.text())
        self.app_config.set_smart_filtering_enabled(self.smart_filtering_entry.text().lower() == 'true')
        self.app_config.set_theme_name(self.theme_name_entry.text())
        self.app_config.set_alt_id(self.alt_id_entry.text())
        self.app_config.set_auto_find_qr_enabled(self.auto_find_qr_checkbox.isChecked())
        self.app_config.save_config()
        self.accept()