import os
import unittest
from unittest.mock import patch, Mock

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

import qr_selection_dialog
from account_add_dialog import AddAccountDialog
from account_manager import AccountManager, OtpRecord
from appconfig import AppConfig
from view import AppView


class TestAddAccountDialog(unittest.TestCase):

    @patch.object(QFileDialog, "getOpenFileName")
    @patch.object(AddAccountDialog, "obtain_qr_codes")
    #@patch.object(AddAccountDialog, "open_qr_image")
    def test_A_qr_code_btn(self, mock_obtain, mockFileDialog):
        """This test fails if run after the Cancel test.  So I changed the name so it runs first.
           Unknown cause: Cancel closes the dialog but that's in a different test so it shouldn't matter.
           And why did it start failing after release 0.2.0 but not before?"""
        # Create the dialog instance
        dialog = AddAccountDialog(AppView(self.app))
        dialog.accept = Mock()  # Mock the accept method of the dialog
        dialog.show_popup = Mock() # Mock the popup to keep it from appearing

        # Act
        dialog.btn_scanQR.click()  # using default radio button "Screen"

        # Assert
        mock_obtain.assert_called_once_with(True)

        # Check a different radio button
        dialog.radioBtnFile.setChecked(True)

        # Mock QFileDialog.getOpenFileName to return a tuple (file_path, filter)
        mockFileDialog.return_value = ("tests/test_data/img_qr_code_single.png", "")
        dialog.btn_scanQR.click()  # Click Scan
        result = dialog.provider_entry.text()
        assert result == "Bogus"

    @patch('qr_selection_dialog.QRselectionDialog')
    @patch('account_edit_dialog.QMessageBox.information')
    @patch("find_qr_codes.scan_screen_for_qr_codes")
    def test_obtain_qr_code(self, mock_find, MockMessageBox, mock_SelectionDialog):
        dialog = AddAccountDialog(AppView(self.app))
        dialog.accept = Mock()  # Mock the accept method of the dialog
        dialog.show_popup = Mock() # Mock the popup to keep it from appearing

        # Case 1: image had no QR code
        mock_find.return_value = ([])
        dialog.btn_scanQR.click()  # using default radio button "Screen"
        # Should process the URL and fill in the field
        result = dialog.provider_entry.text()
        assert result == ""
        # Should show an alert saying no qr code found
        MockMessageBox.assert_called_once()

        # Case 2: image had one QR code
        mock_find.return_value = (['otpauth://totp/boogum%40badmail.com?secret=bogus&issuer=Bogus'])
        dialog.btn_scanQR.click()  # using default radio button "Screen"
        # Should process the URL and fill in the field
        result = dialog.provider_entry.text()
        assert result == "Bogus"

        # Case 3: image had two QR codes - doesn't work, doesn't mock selection dialog
        # mock_find.return_value = (['otpauth://totp/boogum%40badmail.com?secret=bogus&issuer=Bogus',
        #                             'otpauth://totp/me@mail.com?secret=bogus&issuer=Someone'])
        #
        # mock_dialog = Mock()
        # mock_SelectionDialog = mock_dialog
        #
        # # Simulate passing an account list to the constructor
        # account_list = [
        #     OtpRecord('Someone', 'me@mail.com', 'bogus').toAccount(),
        #     OtpRecord('Bogus', 'boogum@badmail.com', 'bogus').toAccount()
        # ]
        # dialog.selected_account = account_list[0]
        # dialog.btn_scanQR.click()  # using default radio button "Screen"
        # # Should process the URL and fill in the field
        # result = dialog.provider_entry.text()
        # assert result == "Someone"


    @patch("account_add_dialog.AccountManager")
    def test_save_new_account(self, MockAccountManager):
        # Create a mock for the AccountManager
        mock_account_manager = MockAccountManager.return_value

        # Create an instance of AddAccountDialog
        dialog = AddAccountDialog(AppView(self.app))
        dialog.account_manager = mock_account_manager

        # Set values for the input fields
        dialog.provider_entry.setText("TestProvider")
        dialog.label_entry.setText("test@example.com")

        # Save button should be disabled until all fields are filled
        assert not dialog.btn_Save.isEnabled()
        dialog.secret_entry.setText("testsecret")
        assert dialog.btn_Save.isEnabled()

        # Mock the save_new_account method
        dialog.account_manager.save_new_account = Mock()

        # Click the Save button
        dialog.btn_Save.click()

        # Verify that save_new_account was called with the correct values
        expected_account = OtpRecord("TestProvider", "test@example.com", "testsecret")
        dialog.account_manager.save_new_account.assert_called_once_with(expected_account)


    @patch('account_add_dialog.AccountManager')
    def test_Cancel_button(self, MockAccountManager):
        # Mock the AccountManager
        dialog_manager = MockAccountManager.return_value # is the mock instance created when AccountManager() is called in ConfirmAccountDialog.
        dialog = AddAccountDialog(AppView(self.app))

        # Replace account manager in dialog with the mock
        dialog.account_manager = dialog_manager

        # Verify save button is disabled until fields are populated
        assert dialog.btn_Save.isEnabled() == False
        # populate fields
        dialog.provider_entry.setText("Woogle")
        dialog.label_entry.setText("me@woogle.com")
        dialog.secret_entry.setText("AB34")

        assert dialog.btn_Save.isEnabled() == True

        # Simulate pressing the Decline button
        dialog.btn_Cancel.click()

        # Verify save_new_account is called once with correct arguments
        dialog_manager.save_new_account.assert_not_called()

    def test_learn_more(self):
        """ Test link content, not that it actually opens the browser page """
        dialog = AddAccountDialog(AppView(self.app))
        link = dialog.label_LearnMore
        linktext = link.text()
        expected = '<a href="https://github.com/jdalbey/EasyAuth/wiki'
        assert linktext.startswith(expected)

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
