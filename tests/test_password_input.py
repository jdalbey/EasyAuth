import unittest
from PyQt5.QtWidgets import QApplication
from common_dialog_funcs import PasswordInput
from appconfig import AppConfig

class TestPasswordInput(unittest.TestCase):

    def test_passwordinput_init_false(self):
        appconfig = AppConfig()
        save_theme = appconfig.get_theme_name() # save original setting
        appconfig.set_theme_name("light")
        input = PasswordInput()
        assert not input.toggle_button.isChecked() # not clicked yet
        # Should initialize hidden by default
        assert input.icon_path == "assets/hide_icon_light.png"
        # Set
        input.set_hidden(is_hidden=False)
        assert not input.toggle_button.isChecked()
        assert input.icon_path == "assets/hide_icon_light.png"
        # Toggle
        input.toggle_button.click()
        assert input.toggle_button.isChecked()
        assert input.icon_path == "assets/show_icon_light.png"
        # Restore
        appconfig.set_theme_name(save_theme) # restore setting

    def test_passwordinput_init_true(self):
        appconfig = AppConfig()
        save_theme = appconfig.get_theme_name() # save original setting
        appconfig.set_theme_name("light")
        input = PasswordInput()
        assert not input.toggle_button.isChecked() # not clicked yet
        # Should initialize hidden by default
        assert input.icon_path == "assets/hide_icon_light.png"
        # Set
        input.set_hidden(is_hidden=True)
        assert input.toggle_button.isChecked()
        assert input.icon_path == "assets/show_icon_light.png"
        # Toggle
        input.toggle_button.click()
        assert not input.toggle_button.isChecked()
        assert input.icon_path == "assets/hide_icon_light.png"
        # Restore
        appconfig.set_theme_name(save_theme) # restore setting

    # Using setUpClass and tearDownClass ensures that QApplication is created once for the entire test suite, preventing multiple instances.
    @classmethod
    def setUpClass(cls):
        # QApplication is created once for the entire test suite
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        # Ensure QApplication is properly cleaned up after all tests
        cls.app.quit()

    def setUp(self):
        # No need to create QApplication here; it's already done in setUpClass
        self.appconfig = AppConfig()

    def tearDown(self):
        # Clean up dialog and other resources
        pass


if __name__ == "__main__":
    unittest.main()
