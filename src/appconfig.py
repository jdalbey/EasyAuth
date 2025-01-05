import configparser

class AppConfig:
    """Application configuration settings"""
    _instance = None

    def __new__(cls, config_file=None):
        """@param The config_file is used to specify the location of the configuration file that will be read by the ConfigParser.
The actual file reading happens inside the read method, which is called after the object is created."""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._config = configparser.ConfigParser()
            if config_file:
                cls._instance.__read(config_file)
        return cls._instance

    def __read(self, config_file):
        """
        Load the configuration file.
        """
        self._config.read(config_file)

    def get_vault_path(self):
        """
        Get the path to the application database.
        """
        return self._config.get('settings', 'database_path', fallback='default.db')

    def is_smart_filtering_enabled(self):
        """
        Check if smart filtering is enabled.
        """
        return self._config.getboolean('settings', 'smart_filtering', fallback=False)

    def get_theme_name(self):
        """
        Get the name of the theme.
        """
        return self._config.get('settings', 'theme_name', fallback='default')

    def reload(self, config_file):
        """
        Reload the configuration from a file.
        """
        self.__read(config_file)

    def set_config(self, config_string):
        """
        Reload the configuration from a string (INI format).
        """
        self._config.read_string(config_string)