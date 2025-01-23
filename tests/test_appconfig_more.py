import os
import pytest
from appconfig import AppConfig

@pytest.fixture
def config_file(tmp_path):
    return "/tmp/EasyAuth/test_config.ini"

@pytest.fixture
def app_config(config_file):
    return AppConfig(config_file)

def test_single_instance(config_file):
    config1 = AppConfig(config_file)
    config2 = AppConfig(config_file)
    assert config1 is config2

def test_save_config(app_config, config_file):
    app_config.set_theme_name("light")
    app_config.save_config()
    new_config = AppConfig(config_file)
    assert new_config.get_theme_name() == 'light'

def test_set_get_theme(app_config):
    app_config.set_theme_name("light")
    assert app_config.get_theme_name() == 'light'

def test_missing_config_directory(app_config, config_file):
    try:
        os.remove(config_file)
        os.removedirs("/tmp/EasyAuth")
    except FileNotFoundError as e:
        pass

    app_config.read(config_file)
    assert app_config.get_theme_name() == 'light'
