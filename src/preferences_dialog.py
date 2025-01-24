from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QCheckBox, QPushButton, QComboBox, \
    QFontDialog, QSizePolicy, QApplication, QFormLayout
from appconfig import AppConfig
import qdarktheme
"""GUI design ideas.
buttons:   OK | CANCEL | APPLY
Category tabs: vertical for many, horizontal for few
   Appearance (theme, font), Keyboard (shortcuts), Behavior, Advanced (e.g. alt machine ID)
Typora has a nice layout and monochrome (?)
Use dimmed text for explanation:
  [ ] Frazzle on exit
      some dim text explanation here
See Oracle Dialog style guide.      
"""
class PreferencesDialog(QDialog):

    def __init__(self, q_app, parent=None, ):
        super(PreferencesDialog, self).__init__(parent)
        self.q_app = q_app
        self.app_config = AppConfig()
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Auto Find QR Code
        self.auto_find_qr_checkbox = QCheckBox("Add Account finds QR code automatically:")
        self.auto_find_qr_checkbox.setChecked(self.app_config.is_auto_find_qr_enabled())
        layout.addWidget(self.auto_find_qr_checkbox)

        # Minimize application after TOTP copy to clipboard
        self.minimize_after_copy = QCheckBox("Minimize application after TOTP copy to clipboard")
        self.minimize_after_copy.setEnabled(False)
        layout.addWidget(self.minimize_after_copy)

        # Minimize during QR code search
        self.minimize_during_qr_search = QCheckBox("Minimize during QR code search")
        self.minimize_during_qr_search.setEnabled(False)
        layout.addWidget(self.minimize_during_qr_search)

        # Display website favicons
        self.display_favicons = QCheckBox("Display provider favicons")
        self.display_favicons.setEnabled(True)
        layout.addWidget(self.display_favicons)

        # Secret key initially hidden with asterisks in Edit dialog
        self.secret_key_hidden = QCheckBox("Secret key initially hidden with asterisks in Edit dialog")
        self.secret_key_hidden.setEnabled(False)
        layout.addWidget(self.secret_key_hidden)

        # Font button
        # self.font_button = QPushButton("Font")
        # self.font_button.setEnabled(False)
        # self.font_button.clicked.connect(self.select_font)
        # layout.addWidget(self.font_button)

        # Theme drop down box
        theme_label = QLabel("Theme:")
        layout.addWidget(theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light","dark"])
        self.theme_combo.currentTextChanged.connect(self.set_theme)
        layout.addWidget(self.theme_combo)

        # Create a QFormLayout to align the label and line edit in a form-like style
        form_layout = QFormLayout()
        form_layout.addRow(theme_label, self.theme_combo)

        # Set the form layout for the window
        layout.addLayout(form_layout)

        # Restore Defaults button
        self.restore_defaults_button = QPushButton("Restore Defaults")
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        self.restore_defaults_button.setContentsMargins(40, 0, 0, 0)
        self.restore_defaults_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.restore_defaults_button.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.restore_defaults_button, alignment=Qt.AlignCenter)

        # Load settings
        self.load_settings()

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        save_button.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def load_settings(self):
        self.minimize_after_copy.setChecked(self.app_config.is_minimize_after_copy())
        self.minimize_during_qr_search.setChecked(self.app_config.is_minimize_during_qr_search())
        self.display_favicons.setChecked(self.app_config.is_display_favicons())
        self.secret_key_hidden.setChecked(self.app_config.is_secret_key_hidden())
        self.auto_find_qr_checkbox.setChecked(self.app_config.is_auto_find_qr_enabled())
        self.theme_combo.setCurrentText(self.app_config.get_theme_name())

    def save_settings(self):
        self.app_config.set_minimize_after_copy(self.minimize_after_copy.isChecked())
        self.app_config.set_minimize_during_qr_search(self.minimize_during_qr_search.isChecked())
        self.app_config.set_display_favicons(self.display_favicons.isChecked())
        self.app_config.set_secret_key_hidden(self.secret_key_hidden.isChecked())
        self.app_config.set_auto_find_qr_enabled(self.auto_find_qr_checkbox.isChecked())
        self.app_config.set_theme_name(self.theme_combo.currentText())
        self.accept()

    def select_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            # Save the selected font to the configuration if needed
            pass

    def set_theme(self):
        # Save chosen theme in Configuration
        self.app_config.set_theme_name(self.theme_combo.currentText())
        self.parent().set_theme()

    def restore_defaults(self):
        self.app_config.restore_defaults()
        self.load_settings()