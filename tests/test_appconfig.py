# main.py
from appconfig import AppConfig
from pathlib import Path

class TestAppConfig:

    def test_appconfig(self):
        # Initialize the singleton instance with a config file
        kConfigPath = ".config/EasyAuth/config.ini"
        home_dir_str = str(Path.home())
        filepath = Path.home().joinpath(home_dir_str, kConfigPath)
        config = AppConfig(filepath)

        vault_path = config.get_vault_path()
        smart_filter = config.is_smart_filtering_enabled()
        theme = config.get_theme_name()
        alt_id = config.get_alt_id()

        assert vault_path == "vault.json"
        assert smart_filter == True
        assert theme == "dark"
        assert alt_id.startswith("10b")

        config_string = """
        [settings]
        database_path = /path/to/database.db
        smart_filtering = true
        theme_name = light
        alt_id = A1B2
        """
        config.set_config(config_string)
        assert config.get_theme_name() == "light"
        assert config.get_alt_id() == "A1B2"