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

    def __init__(self, parent=None, ):
        super(PreferencesDialog, self).__init__(parent)
        self.app_config = AppConfig()
        self.setWindowFlags(Qt.WindowTitleHint | Qt.Dialog | Qt.WindowCloseButtonHint) # x-platform consistency
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Display website favicons
        self.display_favicons = QCheckBox("Display provider favicons")
        self.display_favicons.setEnabled(True)
        layout.addWidget(self.display_favicons)

        # Secret key initially hidden when dialog opens
        self.secret_key_hidden = QCheckBox("Secret key initially hidden when dialog opens")
        self.secret_key_hidden.setEnabled(True)
        layout.addWidget(self.secret_key_hidden)

        # Permission to scan screen for QR code
        self.scan_permission = QCheckBox("Allowed to scan screen for QR code")
        self.scan_permission.setEnabled(True)
        layout.addWidget(self.scan_permission)

        # Minimize during QR code search
        self.minimize_during_qr_search = QCheckBox("Hide window during QR code scan")
        self.minimize_during_qr_search.setEnabled(True)
        layout.addWidget(self.minimize_during_qr_search)

        # Minimize application after TOTP copy to clipboard
        self.minimize_after_copy = QCheckBox("Minimize application after TOTP copy to clipboard")
        self.minimize_after_copy.setEnabled(False)
        layout.addWidget(self.minimize_after_copy)

        # Font button
        # self.font_button = QPushButton("Font")
        # self.font_button.setEnabled(False)
        # self.font_button.clicked.connect(self.select_font)
        # layout.addWidget(self.font_button)

        # Theme label and drop down box
        theme_label = QLabel("Theme:")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light","dark"])
        #self.theme_combo.currentTextChanged.connect(self.set_theme)
        self.theme_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.theme_combo.setFixedSize(100,self.theme_combo.size().height())

        form_layout = QFormLayout()
        form_layout.addRow(theme_label, self.theme_combo)

        # Add the theme form layout to the window
        layout.addLayout(form_layout)

        # Button row
        button_row = QHBoxLayout()

        # Restore Defaults button
        self.restore_defaults_button = QPushButton("Restore Defaults")
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        self.restore_defaults_button.setContentsMargins(40, 0, 0, 0)
        self.restore_defaults_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.restore_defaults_button.setFocusPolicy(Qt.NoFocus)
        button_row.addWidget(self.restore_defaults_button, alignment=Qt.AlignLeft)
        button_row.addStretch()

        # OK button
        btn_OK = QPushButton("&OK")
        btn_OK.clicked.connect(self.save_settings)
        btn_OK.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_row.addWidget(btn_OK, alignment=Qt.AlignRight)

        # Apply button
        btn_Apply = QPushButton("&Apply")
        btn_Apply.clicked.connect(self.apply_settings)
        btn_Apply.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_row.addWidget(btn_Apply, alignment=Qt.AlignRight)

        # Cancel button
        btn_Cancel = QPushButton("&Cancel")
        btn_Cancel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_Cancel.clicked.connect(self.reject)
        button_row.addWidget(btn_Cancel, alignment=Qt.AlignRight)
        layout.addLayout(button_row)

        self.setLayout(layout)

        # Load settings
        self.load_settings()

    def load_settings(self):
        self.display_favicons.setChecked(self.app_config.is_display_favicons())
        self.secret_key_hidden.setChecked(self.app_config.is_secret_key_hidden())
        self.scan_permission.setChecked(self.app_config.is_scan_permission())
        self.minimize_after_copy.setChecked(self.app_config.is_minimize_after_copy())
        self.minimize_during_qr_search.setChecked(self.app_config.is_minimize_during_qr_search())
        self.theme_combo.setCurrentText(self.app_config.get_theme_name())

    def apply_settings(self):
        self.app_config.set_display_favicons(self.display_favicons.isChecked())
        self.app_config.set_secret_key_hidden(self.secret_key_hidden.isChecked())
        self.app_config.set_scan_permission(self.scan_permission.isChecked())
        self.app_config.set_minimize_after_copy(self.minimize_after_copy.isChecked())
        self.app_config.set_minimize_during_qr_search(self.minimize_during_qr_search.isChecked())
        self.app_config.set_theme_name(self.theme_combo.currentText())
        self.parent().set_theme()  # set theme in application
        self.parent().display_accounts() # redisplay accounts

    def save_settings(self):
        self.apply_settings()
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

# Local main for unit testing
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    from styles import light_qss
    qdarktheme.setup_theme("light", additional_qss=light_qss)
    dialog = PreferencesDialog(None)
    dialog.exec()