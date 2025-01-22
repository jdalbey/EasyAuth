# main.py
import os

from appconfig import AppConfig
from pathlib import Path

class TestAppConfig:

    def test_appconfig(self):
        # reset the singleton
        AppConfig._instance = None
        # A complete config file
        settings_string = """[Settings]\nauto_find_qr = True\nsearch_by = Provider\nminimize_after_copy = False
        minimize_during_qr_search = False\nauto_fetch_favicons = False\ndisplay_favicons = False\nsecret_key_hidden = False
        language = English\nanimate_copy = False"""
        kConfigPath = "/tmp/config_test.ini"
        text_file = open(kConfigPath, "w")
        text_file.write(settings_string)
        text_file.close()
        home_dir_str = str(Path.home())
        filepath = Path.home().joinpath(home_dir_str, kConfigPath)
        config = AppConfig(filepath)

        smart_filter = config.is_smart_filtering_enabled()
        theme = config.get_theme_name()
        alt_id = config.get_alt_id()

        assert config.is_auto_find_qr_enabled()
        assert smart_filter == False
        assert theme == "light"
        #assert alt_id.startswith("10b")
        assert alt_id == None

    def test_partial_config(self):
        # reset the singleton
        AppConfig._instance = None
        # A config file with missing setting for vault_path
        settings_string = """[Settings]\nauto_find_qr = True\nsearch_by = Provider\nminimize_after_copy = False
minimize_during_qr_search = False\nauto_fetch_favicons = False\ndisplay_favicons = False\nsecret_key_hidden = False
language = English\nanimate_copy = False\n"""
        kConfigPath = "/tmp/config_partial_test.ini"
        text_file = open(kConfigPath, "w")
        text_file.write(settings_string)
        text_file.close()
        home_dir_str = str(Path.home())
        filepath = Path.home().joinpath(home_dir_str, kConfigPath)
        config = AppConfig(filepath)

        assert config.is_auto_find_qr_enabled()

    def test_missing_config(self):
        # reset the singleton
        AppConfig._instance = None
        kConfigPath = "/tmp/config_missing.ini"
        try:
            os.remove(kConfigPath)
        except FileNotFoundError as e:
            pass
        home_dir_str = str(Path.home())
        filepath = Path.home().joinpath(home_dir_str, kConfigPath)
        config = AppConfig(filepath)

        assert config.is_auto_find_qr_enabled()

    def test_noarg_missingfile(self):
        # reset the singleton
        AppConfig._instance = None
        # use a temp file for testing
        filepath = "/tmp/default_config.ini"
        try:
            os.remove(filepath)
        except FileNotFoundError as e:
            pass
        AppConfig.kDefaultPath = filepath

        config = AppConfig()  # noarg constructor

        assert config.is_auto_find_qr_enabled()
        # should have been created by restore_defaults()
        assert os.path.exists(filepath)

    def test_noarg_existingfile(self):
        # reset the singleton
        AppConfig._instance = None
        # use a temp file for testing
        filepath = "/tmp/default_config.ini"
        settings_string = "[Settings]\ntheme_name = Cobalt"
        text_file = open(filepath, "w")
        text_file.write(settings_string)
        text_file.close()

        AppConfig.kDefaultPath = filepath

        config = AppConfig()  # noarg constructor

        assert config.get_theme_name() == "Cobalt"
