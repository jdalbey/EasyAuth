import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
import quick_start_dialog
from appconfig import AppConfig

class TestQuickstart(unittest.TestCase):

    def test_quickstart_load(self):
        dummy_parent = QWidget()
        dlg = quick_start_dialog.QuickStartDialog(dummy_parent)

        save_theme = self.appconfig.get_theme_name() # save original setting
        self.appconfig.set_theme_name("dark")
        text = dlg.load_quickstart_text()
        assert text.find("color: white") > 0

        self.appconfig.set_theme_name("light")
        text = dlg.load_quickstart_text()
        assert text.find("color: rgb") > 0

        # Restore
        self.appconfig.set_theme_name(save_theme) # restore setting

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
