import os
import unittest
from unittest.mock import patch, Mock

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QPushButton, QLabel, QMenuBar, QMenu, QAction

import pyperclip
from account_edit_dialog import EditAccountDialog
from account_manager import AccountManager, OtpRecord, Account
from appconfig import AppConfig
from export_import_dialog import ExportImportDialog
from preferences_dialog import PreferencesDialog
from quick_start_dialog import QuickStartDialog
from reorder_dialog import ReorderDialog
from view import AppView


class TestView(unittest.TestCase):

    @patch('view.AddAccountDialog')
    def test_add_btn_click(self, MockAddAccountDialog):
        # Create a mock for AddAccountDialog
        mock_add_account_dialog = MockAddAccountDialog.return_value
        mock_add_account_dialog.obtain_qr_codes = Mock()

        # Create an instance of AppView
        view = AppView(self.app)
        view.app_config.set_auto_find_qr_enabled(True)

        # Simulate clicking the add_btn
        view.add_btn.click()

        # Verify that obtain_qr_codes was called from AddAccountDialog
        mock_add_account_dialog.obtain_qr_codes.assert_called_once()
        mock_add_account_dialog.exec_.assert_called_once()

    @patch('view.AppView.show_edit_account_form')
    def test_edit_btn_click(self, mock_show_edit_account_form):
        # Create an instance of AppView
        view = AppView(self.app)

        # Mock the accounts list
        #mock_account = OtpRecord("TestProvider", "test@example.com", "AB45").toAccount()
        #view.accounts = [mock_account]
        first_acct = view.account_manager.accounts[0]

        # Find the edit button in the first row
        edit_btns = view.findChildren(QPushButton, "editButton")
        self.assertGreater(len(edit_btns), 0, "No edit buttons found")
        edit_btn = edit_btns[0]

        # Simulate clicking the edit button in the first row
        edit_btn.click()

        # TODO: override comparison in Account to not look at encrypted secret
        # Verify that show_edit_account_form was called with the correct index and account
        mock_show_edit_account_form.assert_called_once() #_with(0, unittest.mock.ANY) #first_acct)

    @patch.object(EditAccountDialog, "exec_")
    def test_show_edit_account_form(self,mockDialog):
        # Create an instance of AppView
        view = AppView(self.app)
        # Find the edit button in the first row
        edit_btns = view.findChildren(QPushButton, "editButton")
        self.assertGreater(len(edit_btns), 0, "No edit buttons found")
        edit_btn = edit_btns[0]
        # Simulate clicking the edit button in the first row
        edit_btn.click()
        # verify the EditAccountDialog.exec_() was called to show the form
        mockDialog.assert_called_once()
        print ("Finished show_edit_account_form")

    @patch('view.AccountManager')
    def test_display_accounts(self, MockAccountManager):
        # Create an instance of AppView
        view = AppView(self.app)

        # Mock the accounts list with two mock accounts
        mock_account1 = OtpRecord("Provider1", "label1", "AB34").toAccount()
        mock_account2 = OtpRecord("Provider2", "label2", "AB34").toAccount()

        view.account_manager.accounts = [mock_account1, mock_account2]

        # Call the display_accounts method
        view.display_accounts()

        # Find the first providerLabel in the layout
        provider_labels = view.findChildren(QLabel, "providerLabel")
        self.assertGreater(len(provider_labels), 0, "No provider labels found")
        first_provider_label = provider_labels[0]

        # Verify that the first providerLabel starts with the string from the first mock account
        self.assertTrue(first_provider_label.text().startswith("Provider1"))

    @patch('view.AccountManager')
    def test_search(self, MockAccountManager):
        # Create an instance of AppView
        view = AppView(self.app)

        # Mock the accounts list with two mock accounts
        mock_account1 = OtpRecord("Able", "label1", "AB34").toAccount()
        mock_account2 = OtpRecord("Baker", "label2", "AB34").toAccount()

        view.account_manager.accounts = [mock_account1, mock_account2]
        view.search_box.setText("k")
        # Call the display_accounts method
        view.display_accounts()

        # Find the first providerLabel in the layout
        provider_labels = view.findChildren(QLabel, "providerLabel")
        self.assertGreater(len(provider_labels), 0, "No provider labels found")
        first_provider_label = provider_labels[0]

        # Verify that the first providerLabel starts with the string from the first mock account
        self.assertTrue(first_provider_label.text().startswith("Baker"))


    @patch('view.AccountManager')
    def test_sort_alpha(self, MockAccountManager):
        # Create an instance of AppView
        view = AppView(self.app)

        # Mock the accounts list with two mock accounts
        mock_account1 = OtpRecord("Rexall", "label1", "AB34").toAccount()
        mock_account2 = OtpRecord("Pennies", "label2", "AB34").toAccount()

        view.account_manager.accounts = [mock_account1, mock_account2]
        view.display_accounts()

        # mock the actual sort call
        view.account_manager.sort_alphabetically = Mock()

        # Find the Tools > Sort > Alphabetically action by object name
        sort_alpha_action = view.findChild(QAction, "sortAlphaAction")
        self.assertIsNotNone(sort_alpha_action, "Sort > Alphabetically action not found")

        # Invoke the Sort > Alphabetically action
        sort_alpha_action.trigger()
        # Assert the sort call was made
        view.account_manager.sort_alphabetically.assert_called_once()

    @patch('view.AccountManager')
    def test_copy_to_clipboard(self, MockAccountManager):
        view = AppView(self.app)
        mock_account1 = OtpRecord("Rexall", "label1", "AB34").toAccount()
        mock_account2 = OtpRecord("Pennies", "label2", "AB34").toAccount()
        view.account_manager.accounts = [mock_account1, mock_account2]
        view.display_accounts()
        # Find the otplabel button in the first row
        otp_btns = view.findChildren(QPushButton, "otpLabel")
        self.assertGreater(len(otp_btns), 0, "No copy buttons found")
        # Simulate clicking the copy button in the first row
        otp_btns[0].click()
        # Get the value from the clipboard
        received = pyperclip.paste()
        # Verify the pasted value matches the button text
        assert otp_btns[0].text() == received
        # Verify the manager updated the account with last_used
        view.account_manager.update_account.assert_called_once()

    @patch.object(ReorderDialog,"exec_")
    @patch('view.AccountManager')
    def test_reorder_form(self, MockAccountManager,mockReorderDialog):
        # Create an instance of AppView
        view = AppView(self.app)
        mockReorderDialog.return_value = 1
        # Mock the accounts list with two mock accounts
        mock_account1 = OtpRecord("Rexall", "label1", "AB34").toAccount()
        mock_account2 = OtpRecord("Pennies", "label2", "AB34").toAccount()
        view.account_manager.accounts = [mock_account1, mock_account2]
        view.display_accounts()

        # Find the Tools > Sort > Alphabetically action by object name
        reorder_action = view.findChild(QAction, "reorderAction")
        self.assertIsNotNone(reorder_action, "Sort > Alphabetically action not found")

        # Invoke the Reorder action
        reorder_action.trigger()
        # Assert the sort call was made
        view.account_manager.set_accounts.assert_called_once()
        mockReorderDialog.assert_called_once()

    @patch.object(ExportImportDialog,"exec_")
    def test_export_action(self, mockDialog):
        view = AppView(self.app)
        # Find the Reorder action by object name
        export_action = view.findChild(QAction, "exportAction")
        self.assertIsNotNone(export_action, "Export action not found")

        # Invoke the  action
        export_action.trigger()
        # Assert the call was made to open the dialog
        mockDialog.assert_called_once()

    @patch.object(PreferencesDialog,"exec_")
    def test_preferences_action(self, mockDialog):
        view = AppView(self.app)
        mockDialog.return_value = 1
        # Find the Reorder action by object name
        preferences_action = view.findChild(QAction, "preferencesAction")
        self.assertIsNotNone(preferences_action, "Export action not found")

        # Invoke the  action
        preferences_action.trigger()
        # Assert the call was made to open the dialog
        mockDialog.assert_called_once()

    @patch.object(QuickStartDialog, "show")
    def test_quickstart_action(self,mockDialog):
        view = AppView(self.app)
        # Find the Reorder action by object name
        quickstart_action = view.findChild(QAction, "quickstartAction")
        self.assertIsNotNone(quickstart_action, "Quickstart action not found")

        # Invoke the  action
        quickstart_action.trigger()
        # Assert the call was made to open the dialog
        mockDialog.assert_called_once()

    # Using setUpClass and tearDownClass ensures that QApplication is created once for the entire test suite, preventing multiple instances.
    @classmethod
    def setUpClass(cls):
        # QApplication is created once for the entire test suite
        cls.app = QApplication([])
        cls.appconfig = AppConfig()

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

if __name__ == "__main__":
    unittest.main()
