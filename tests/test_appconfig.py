# main.py
from appconfig import AppConfig

class TestAppConfig:

    def test_appconfig(self):
        # Initialize the singleton instance with a config file
        config = AppConfig('../src/appconfig.ini')

        vault_path = config.get_vault_path()
        smart_filter = config.is_smart_filtering_enabled()
        theme = config.get_theme_name()

        assert vault_path == "vault.json"
        assert smart_filter == True
        assert theme == "dark"

        config_string = """
        [settings]
        database_path = /path/to/database.db
        smart_filtering = true
        theme_name = light
        """
        config.set_config(config_string)
        assert config.get_theme_name() == "light"
