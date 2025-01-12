from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QCheckBox, QPushButton, QComboBox, \
    QFontDialog, QSizePolicy
from appconfig import AppConfig

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        self.app_config = AppConfig()
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Search by: Provider or User
        search_by_label = QLabel("Search by:")
        layout.addWidget(search_by_label)
        self.search_by_provider = QRadioButton("Provider")
        self.search_by_user = QRadioButton("User")
        layout.addWidget(self.search_by_provider)
        layout.addWidget(self.search_by_user)

        # Minimize application after TOTP copy to clipboard
        self.minimize_after_copy = QCheckBox("Minimize application after TOTP copy to clipboard")
        layout.addWidget(self.minimize_after_copy)

        # Minimize during QR code search
        self.minimize_during_qr_search = QCheckBox("Minimize during QR code search")
        layout.addWidget(self.minimize_during_qr_search)

        # Auto fetch website favicons
        self.auto_fetch_favicons = QCheckBox("Auto fetch website favicons")
        layout.addWidget(self.auto_fetch_favicons)

        # Display website favicons
        self.display_favicons = QCheckBox("Display website favicons")
        layout.addWidget(self.display_favicons)

        # Secret key initially hidden with asterisks in Edit dialog
        self.secret_key_hidden = QCheckBox("Secret key initially hidden with asterisks in Edit dialog")
        layout.addWidget(self.secret_key_hidden)

        # Font button
        self.font_button = QPushButton("Font")
        self.font_button.clicked.connect(self.select_font)
        layout.addWidget(self.font_button)

        # Language drop down box
        language_label = QLabel("Language:")
        layout.addWidget(language_label)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish"])
        layout.addWidget(self.language_combo)

        # Theme drop down box
        theme_label = QLabel("Theme:")
        layout.addWidget(theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        layout.addWidget(self.theme_combo)

        # Animate Copy to clipboard
        self.animate_copy = QCheckBox("Animate Copy to clipboard")
        layout.addWidget(self.animate_copy)

        # Auto Find QR Code
        self.auto_find_qr_checkbox = QCheckBox("Add Account finds QR code automatically:")
        self.auto_find_qr_checkbox.setChecked(self.app_config.is_auto_find_qr_enabled())
        layout.addWidget(self.auto_find_qr_checkbox)

        # Restore Defaults button
        self.restore_defaults_button = QPushButton("Restore Defaults")
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        layout.addWidget(self.restore_defaults_button)
        self.restore_defaults_button.setContentsMargins(40, 0, 0, 0)
        self.restore_defaults_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.restore_defaults_button, alignment=Qt.AlignCenter)

        # Load settings
        self.load_settings()

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def load_settings(self):
        self.search_by_provider.setChecked(self.app_config.get_search_by() == "Provider")
        self.search_by_user.setChecked(self.app_config.get_search_by() == "User")
        self.minimize_after_copy.setChecked(self.app_config.is_minimize_after_copy())
        self.minimize_during_qr_search.setChecked(self.app_config.is_minimize_during_qr_search())
        self.auto_fetch_favicons.setChecked(self.app_config.is_auto_fetch_favicons())
        self.display_favicons.setChecked(self.app_config.is_display_favicons())
        self.secret_key_hidden.setChecked(self.app_config.is_secret_key_hidden())
        self.language_combo.setCurrentText(self.app_config.get_language())
        self.animate_copy.setChecked(self.app_config.is_animate_copy())
        self.auto_find_qr_checkbox.setChecked(self.app_config.is_auto_find_qr_enabled())
        self.theme_combo.setCurrentText(self.app_config.get_theme_name())

    def save_settings(self):
        self.app_config.set_search_by("Provider" if self.search_by_provider.isChecked() else "User")
        self.app_config.set_minimize_after_copy(self.minimize_after_copy.isChecked())
        self.app_config.set_minimize_during_qr_search(self.minimize_during_qr_search.isChecked())
        self.app_config.set_auto_fetch_favicons(self.auto_fetch_favicons.isChecked())
        self.app_config.set_display_favicons(self.display_favicons.isChecked())
        self.app_config.set_secret_key_hidden(self.secret_key_hidden.isChecked())
        self.app_config.set_language(self.language_combo.currentText())
        self.app_config.set_animate_copy(self.animate_copy.isChecked())
        self.app_config.set_auto_find_qr_enabled(self.auto_find_qr_checkbox.isChecked())
        self.app_config.set_theme_name(self.theme_combo.currentText())
        self.accept()

    def select_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            # Save the selected font to the configuration if needed
            pass

    def restore_defaults(self):
        self.app_config.restore_defaults()
        self.load_settings()