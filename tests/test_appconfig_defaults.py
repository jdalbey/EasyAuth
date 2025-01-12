# main.py
from appconfig import AppConfig
from pathlib import Path

class TestAppConfig:

    def test_appconfig(self):
        # Initialize the singleton instance with a config file
        config = AppConfig(None)

        vault_path = config.get_vault_path()
        smart_filter = config.is_smart_filtering_enabled()
        theme = config.get_theme_name()
        alt_id = config.get_alt_id()

        assert vault_path == "default.db"
        assert smart_filter == False
        assert theme == "default"
        assert alt_id == ''
        assert config.is_auto_find_qr_enabled() == True
