from configparser import ConfigParser
import os

class AppConfig:
    """Application configuration settings (Preferences)"""
    _instance = None
    kDefaultPath = ".config/EasyAuth/config.ini"
    def __new__(cls, filepath=None):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, filepath=None):
        if self._initialized:
            return
        # This code executes just once for first/only instance
        self.config = ConfigParser()
        self.filepath = filepath
        # If a filepath was provided load settings from there
        if filepath:
            self.read(filepath)
        # otherwise fallback settings will be used by restore_defaults
        else:
            self.filepath = self.kDefaultPath
            self.restore_defaults()
        self._initialized = True

    def read(self, config_file):
        """ Read config file or create it with defaults """
        # does the file exist
        if not os.path.exists(config_file):
            print (f"The configuration file '{config_file}' does not exist, creating it.")
            # is the directory missing?
            if not os.path.exists(os.path.dirname(config_file)):
                os.makedirs(os.path.dirname(config_file),True)
            # write defaults to the file
            self.restore_defaults()
            print("restored defaults and saved to config file")
        else:
            self.config.read(config_file)

    def saveconfig(self):
        if self.filepath:
            with open(self.filepath, 'w') as configfile:
                self.config.write(configfile)

    def reload(self, config_file):
        """
        Reload the configuration from a file.  Used for testing.
        """
        self.read(config_file)

    def set_config(self, config_string):
        """
        Reload the configuration from a string (INI format).
        Dependency injection for testing.
        """
        self.config.read_string(config_string)

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        """ Set an options value and write it """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        self.saveconfig()

    # Add methods to get and set the new settings
    def is_auto_find_qr_enabled(self):
        return self.get('Settings', 'auto_find_qr', fallback='False') == 'True'

    def set_auto_find_qr_enabled(self, value):
        self.set('Settings', 'auto_find_qr', 'True' if value else 'False')

    def get_search_by(self):
        return self.get('Settings', 'search_by', fallback='Provider')

    def set_search_by(self, value):
        self.set('Settings', 'search_by', value)

    def is_minimize_after_copy(self):
        return self.get('Settings', 'minimize_after_copy', fallback='False') == 'True'

    def set_minimize_after_copy(self, value):
        self.set('Settings', 'minimize_after_copy', 'True' if value else 'False')

    def is_minimize_during_qr_search(self):
        return self.get('Settings', 'minimize_during_qr_search', fallback='False') == 'True'

    def set_minimize_during_qr_search(self, value):
        self.set('Settings', 'minimize_during_qr_search', 'True' if value else 'False')

    def is_auto_fetch_favicons(self):
        return self.get('Settings', 'auto_fetch_favicons', fallback='False') == 'True'

    def set_auto_fetch_favicons(self, value):
        self.set('Settings', 'auto_fetch_favicons', 'True' if value else 'False')

    def is_display_favicons(self):
        return self.get('Settings', 'display_favicons', fallback='False') == 'True'

    def set_display_favicons(self, value):
        self.set('Settings', 'display_favicons', 'True' if value else 'False')

    def is_secret_key_hidden(self):
        return self.get('Settings', 'secret_key_hidden', fallback='False') == 'True'

    def set_secret_key_hidden(self, value):
        self.set('Settings', 'secret_key_hidden', 'True' if value else 'False')

    def get_language(self):
        return self.get('Settings', 'language', fallback='English')

    def set_language(self, value):
        self.set('Settings', 'language', value)

    def is_animate_copy(self):
        return self.get('Settings', 'animate_copy', fallback='False') == 'True'

    def set_animate_copy(self, value):
        self.set('Settings', 'animate_copy', 'True' if value else 'False')

    def get_vault_path(self):
        """
        Get the path to the application database.
        """
        return self.config.get('Settings', 'vault_path', fallback='vault.json')

    def set_vault_path(self, path):
        """
        Set the path to the application database.
        """
        self.set('Settings', 'vault_path', path)

    def is_smart_filtering_enabled(self):
        """
        Check if smart filtering is enabled.
        """
        return self.config.getboolean('Settings', 'smart_filtering', fallback=False)

    def set_smart_filtering_enabled(self, enabled):
        """
        Set the smart filtering enabled status.
        """
        self.set('Settings', 'smart_filtering', str(enabled))

    def get_theme_name(self):
        """
        Get the name of the theme.
        """
        return self.config.get('Settings', 'theme_name', fallback='light')

    def set_theme_name(self, theme_name):
        """
        Set the name of the theme.
        """
        self.set('Settings', 'theme_name', theme_name)

    def get_alt_id(self):
        """
        Get the alternate id.
        """
        return self.config.get('Settings', 'alt_id', fallback="")

    def set_alt_id(self, alt_id):
        """
        Set the alternate id.
        """
        self.set('Settings', 'alt_id', alt_id)

    def restore_defaults(self):
        """ restore and write defaults """
        self.set_auto_find_qr_enabled(False)
        self.set_search_by('Provider')
        self.set_minimize_after_copy(False)
        self.set_minimize_during_qr_search(False)
        self.set_auto_fetch_favicons(False)
        self.set_display_favicons(False)
        self.set_secret_key_hidden(False)
        self.set_language('English')
        self.set_animate_copy(False)
        self.set_vault_path("vault.json")
        self.set_smart_filtering_enabled(False)
        self.set_theme_name("light")
        self.set_alt_id("")