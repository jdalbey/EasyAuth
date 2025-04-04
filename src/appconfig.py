from configparser import ConfigParser
import os, logging
from pathlib import Path
import platform

class AppConfig:
    """Application configuration settings (Preferences)"""
    _instance = None  # Use singleton pattern
    # Path to configuration file
    kDefaultPath = ".config/EasyAuth/config.ini"

    def __new__(cls, filepath=None):
        # Create the single instance of this class
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, filepath=None):
        if self._initialized:
            return
        # This code executes just once for first/only instance
        self.config = ConfigParser()
        self.logwriter = logging.getLogger(__name__)
        # If a filepath was provided load settings from there
        if filepath:
            self.filepath = filepath  #must initialize before read uses it
            self.read(filepath)
        # otherwise fallback settings will be used by restore_defaults
        else:
            home_dir_str = str(Path.home())
            self.filepath = Path.home().joinpath(home_dir_str, AppConfig.kDefaultPath)
            self.logwriter.info (f"using default: {self.filepath}")
            self.read(self.filepath)
        self._initialized = True

    def read(self, config_file):
        """ Read config file or create it with defaults """
        # does the file exist
        if not os.path.exists(config_file):
            self.logwriter.info(f"The configuration file '{config_file}' does not exist, creating it.")
            # is the directory missing?
            if not os.path.exists(os.path.dirname(config_file)):
                os.makedirs(os.path.dirname(config_file),mode=0o777,exist_ok=True)
            # write defaults to the file
            self.restore_defaults()
            self.logwriter.info("restored defaults and saved to config file")
        else:
            self.config.read(config_file)

    def save_config(self):
        if self.filepath:
            with open(self.filepath, 'w') as configfile:
                self.config.write(configfile)

    def get(self, section, option, fallback=None):
        """ Accessor to a specific setting.
        @param section the desired section of the configu file
        @param option the name of the option
        @param fallback the default/fallback value if option isn't in the file. """
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        """ Set an options value and write it """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        self.save_config()

    # Accessor / setters for each option
    def is_display_favicons(self):
        return self.get('Settings', 'display_favicons', fallback='False') == 'True'

    def set_display_favicons(self, value):
        self.set('Settings', 'display_favicons', 'True' if value else 'False')

    def is_secret_key_hidden(self):
        return self.get('Settings', 'secret_key_hidden', fallback='False') == 'True'

    def set_secret_key_hidden(self, value):
        self.set('Settings', 'secret_key_hidden', 'True' if value else 'False')

    def is_scan_permission(self):
        return self.get('Settings', 'scan_permission', fallback='False') == 'True'

    def set_scan_permission(self, value):
        self.set('Settings', 'scan_permission', 'True' if value else 'False')

    def is_minimize_after_copy(self):
        return self.get('Settings', 'minimize_after_copy', fallback='False') == 'True'

    def set_minimize_after_copy(self, value):
        self.set('Settings', 'minimize_after_copy', 'True' if value else 'False')

    def is_minimize_during_qr_search(self):
        return self.get('Settings', 'minimize_during_qr_search', fallback='False') == 'True'

    def set_minimize_during_qr_search(self, value):
        self.set('Settings', 'minimize_during_qr_search', 'True' if value else 'False')

    def get_language(self):
        return self.get('Settings', 'language', fallback='English')

    def set_language(self, value):
        self.set('Settings', 'language', value)

    def get_theme_name(self):
        return self.config.get('Settings', 'theme_name', fallback='light')

    def set_theme_name(self, theme_name):
        self.set('Settings', 'theme_name', theme_name)

    def get_alt_id(self):
        alt_id_string = self.config.get('System', 'alt_id', fallback="")
        if alt_id_string == "":
            return None
        else:
            return alt_id_string

    def get_os_data_dir(self):
        """ Determine the appropriate path to the database based on the OS """
        if platform.system() == "Windows":
            return self.config.get('System','win_data_dir',fallback=str(Path.home() / "Roaming" / "org.redpoint.EasyAuth" / "data"))
        else:  # Default to Linux or Unix-like systems
            return self.config.get('System','linux_data_dir', fallback=str(Path.home() / ".var" / "app" / "org.redpoint.EasyAuth" / "data"))

    def get_log_level(self):
        """ Accessor to desired logging level. """
        return self.config.get('System', 'log_level', fallback='20')

    def restore_defaults(self):
        """ restore and write defaults """
        self.set_display_favicons(True)
        self.set_secret_key_hidden(False)
        self.set_scan_permission(False)
        self.set_minimize_after_copy(False)
        self.set_minimize_during_qr_search(False)
        self.set_language('English')
        self.set_theme_name("light")
        # 'Hidden' settings are not listed in the Preferences dialog and don't have public setter methods
        """ Alternate machine id.  If you want to use a vault created on a different machine you need to
           use the machine id the vault was created on.  """
        self.set('System', 'alt_id', "")
        """ the path to the application data directory (for vault and logs). """
        dirpath = str(Path.home() / "Roaming" / "org.redpoint.EasyAuth" / "data")
        self.set('System', 'win_data_dir', dirpath)
        dirpath = str(Path.home() / ".var" / "app" / "org.redpoint.EasyAuth" / "data")
        self.set('System', 'linux_data_dir', dirpath)
        """ The desired logging level, an integer: 
        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40"""
        self.set('System', 'log_level', '20')

