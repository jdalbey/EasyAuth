import unittest
from unittest.mock import patch, Mock

import pytest
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtCore import Qt

from appconfig import AppConfig
from export_import_dialog import ExportImportDialog
from account_mgr import AccountManager, Account, OtpRecord
from preferences_dialog import PreferencesDialog
from view import AppView


class Appview:
    pass


class TestPreferencesDialog(unittest.TestCase):

    def test_load_settings(self):
        """ We're just checking a single setting for this smoke test """
        view = AppView(self.app)
        # Create the dialog instance - it loads settings
        dialog = PreferencesDialog(view)
        # Get the state of the checkbox
        dlg_state = dialog.display_favicons.isChecked()
        # Flip the checkbox
        dialog.display_favicons.setChecked(not dlg_state)
        # Load the settings again
        dialog.load_settings()
        # Verify load_settings restored the checkbox state
        assert dlg_state == dialog.display_favicons.isChecked()

    def set_theme(self):
        """ Mock method used for testing apply_settings() """
        pass

    @patch.object(AppConfig,"set_display_favicons")
    def test_apply_settings(self,mockConfig):
        """ We're just checking a single setting for this smoke test """
        view = AppView(self.app)
        # Create the dialog instance - it loads settings
        dialog = PreferencesDialog(view)
        # Apply the settings (set the configuration)
        dialog.apply_settings()
        mockConfig.assert_called_once()




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
        pass


    def tearDown(self):
        # Clean up dialog and other resources
        pass

