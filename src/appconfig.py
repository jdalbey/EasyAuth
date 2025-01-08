import configparser
import os
from PyQt5.QtWidgets import QMessageBox

class AppConfig:
    """Application configuration settings"""
    _instance = None

    def __new__(cls, config_file=None):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._config_file = config_file
            cls._instance._config = configparser.ConfigParser()
            if config_file:
                cls._instance.__read(config_file)
        return cls._instance

    def __read(self, config_file):
        if not os.path.exists(config_file):
            reply = QMessageBox.question(None, "Create Config File",
                                         f"The configuration file '{config_file}' does not exist. Do you want to create it?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                with open(config_file, 'w') as file:
                    self._config['settings'] = {
                        'vault_path': 'default.db',
                        'smart_filtering': 'False',
                        'theme_name': 'default',
                        'alt_id': '',
                        'auto_find_qr': 'False' 
                    }
                    self._config.write(file)
            else:
                raise FileNotFoundError(f"The configuration file '{config_file}' does not exist.")
        self._config.read(config_file)

    def get_vault_path(self):
        """
        Get the path to the application database.
        """
        return self._config.get('settings', 'vault_path', fallback='default.db')

    def set_vault_path(self, path):
        """
        Set the path to the application database.
        """
        self._config.set('settings', 'vault_path', path)

    def is_smart_filtering_enabled(self):
        """
        Check if smart filtering is enabled.
        """
        return self._config.getboolean('settings', 'smart_filtering', fallback=False)

    def set_smart_filtering_enabled(self, enabled):
        """
        Set the smart filtering enabled status.
        """
        self._config.set('settings', 'smart_filtering', str(enabled))

    def get_theme_name(self):
        """
        Get the name of the theme.
        """
        return self._config.get('settings', 'theme_name', fallback='default')

    def set_theme_name(self, theme_name):
        """
        Set the name of the theme.
        """
        self._config.set('settings', 'theme_name', theme_name)

    def get_alt_id(self):
        """
        Get the alternate id.
        """
        return self._config.get('settings', 'alt_id', fallback=None)

    def set_alt_id(self, alt_id):
        """
        Set the alternate id.
        """
        self._config.set('settings', 'alt_id', alt_id)

    def is_auto_find_qr_enabled(self):
        """
        Check if auto find QR code is enabled.
        """
        return self._config.getboolean('settings', 'auto_find_qr', fallback=False)

    def set_auto_find_qr_enabled(self, enabled):
        """
        Set the auto find QR code enabled status.
        """
        self._config.set('settings', 'auto_find_qr', str(enabled))

    def reload(self, config_file):
        """
        Reload the configuration from a file.
        """
        self.__read(config_file)

    def set_config(self, config_string):
        """
        Reload the configuration from a string (INI format).
        Dependency injection for testing.
        """
        self._config.read_string(config_string)

    def save_config(self):
        if self._instance._config_file:
            with open(self._instance._config_file, 'w') as configfile:
                self._config.write(configfile)