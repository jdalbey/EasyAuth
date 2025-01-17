import unittest
from unittest.mock import patch, Mock
from PyQt5.QtWidgets import QMessageBox, QApplication
from account_edit_dialog import EditAccountDialog
from account_manager import Account
class TestAccountDeletion(unittest.TestCase):

    @patch('PyQt5.QtWidgets.QMessageBox.question')
    @patch("account_edit_dialog.AccountManager")  
    def test_confirm_delete_account_accepted(self, MockAccountManager, mock_question):
        # Configure the mock to return QMessageBox.Yes
        mock_question.return_value = QMessageBox.StandardButton.Yes
        
        secretkey = "gAAAAABnheVNEijpl8Hj5sJ13kxWYl0sYuGRxnHBmBYD9WtwiHyL_6iJtsk2XY6puLuNCbcGzJv-aOAN4nB53v6wRsgybXZHpQ=="
        account_in = Account("Woogle", "me@woogle.com", secretkey, "2000-01-01 01:01")

        dialog = EditAccountDialog(None, 1, account_in)
        dialog.account_manager = MockAccountManager
        dialog.accept = Mock()  # Mock the accept method of the dialog
        # Call the method that shows the dialog
        result = dialog.confirm_delete_account()
        
        # Verify the dialog was shown with correct parameters
        mock_question.assert_called_once()

        # Verify the result is what we expect when user clicks Yes
        dialog.accept.assert_called_once()

    @patch("account_edit_dialog.AccountManager")
    def test_handle_update_request_success(self, MockAccountManager):
        # account with a valid secret
        account_in = Account("Woogle", "me@woogle.com", "AB34", "2000-01-01 01:01")
        encrypted_secret = 'gAAAAABnhzAo4D3RsKjiMwAOdhM8kDAQ40zUucOhzBK_Hz_1QP0cwgL6aN1U2XgaCqItPx7ACmH6vp7b1h4XkoAYXKdy_KQUFg=='
        account_in.secret = encrypted_secret
        # setup the mocks
        dialog = EditAccountDialog(None, 1, account_in)
        # mock updated fields the user has modified
        dialog.shared_fields.provider_entry.setText("ModifiedWoogle")
        dialog.shared_fields.label_entry.setText("x@w.com")
        dialog.account_manager = MockAccountManager
        dialog.close = Mock()  # Mock the accept method of the dialog
        # Call the method that shows the dialog
        dialog.handle_update_request(1,account_in)
        # verify results
        assert dialog.encrypted_secret.startswith('gAAAA')
        # We expect the account sent to update has the modified fields
        expected_account = Account("ModifiedWoogle","x@w.com","","2000-01-01 01:01")
        expected_account.secret = dialog.encrypted_secret
        MockAccountManager.update_account.assert_called_once_with(1, expected_account)
        dialog.close.assert_called_once()

    #@patch('PyQt5.QtWidgets.QMessageBox.information')  Not sure if this is better
    @patch('account_edit_dialog.QMessageBox.information')
    @patch("account_edit_dialog.AccountManager")
    def test_handle_update_request_failure(self,MockAccountManager,MockMessageBox):
        # account with an invalid secret
        account_in = Account("Woogle", "me@woogle.com", "CD3334", "2000-01-01 01:01")
        encrypted_secret = 'gAAAAABnhy9vzWtawbgygQLGLP_FC1UZ4xQsDzXS2-gH7WkEzC35YxK9qYpkRVnYYi6CXZhvoMaoTmYqMSL07j67iNkSUlJERQ=='
        account_in.secret = encrypted_secret
        dialog = EditAccountDialog(None, 1, account_in)
        dialog.account_manager = MockAccountManager
        dialog.close = Mock()  # Mock the accept method of the dialog
        # Call the method that shows the dialog
        dialog.handle_update_request(1,account_in)
        # Verify results
        assert dialog.encrypted_secret == None
        MockAccountManager.update_account.assert_not_called()
        dialog.close.assert_not_called()
        MockMessageBox.assert_called_once() # Not MockMessageBox.information.assert_called_once()

        #_with(
            #None, 'Error', "The secret key is invalid", unittest.mock.ANY        )




    @patch('PyQt5.QtWidgets.QMessageBox.question')
    @patch("account_edit_dialog.AccountManager")
    def test_confirm_delete_account_rejected(self, MockAccountManager, mock_question):
        # Configure the mock to return QMessageBox.No
        mock_question.return_value = QMessageBox.StandardButton.No
        secretkey = "gAAAAABnheVNEijpl8Hj5sJ13kxWYl0sYuGRxnHBmBYD9WtwiHyL_6iJtsk2XY6puLuNCbcGzJv-aOAN4nB53v6wRsgybXZHpQ=="
        account_in = Account("Woogle", "me@woogle.com", secretkey, "2000-01-01 01:01")

        dialog = EditAccountDialog(None, 1, account_in)
        dialog.account_manager = MockAccountManager
        dialog.accept = Mock()  # Mock the accept method of the dialog

        # Call the method that shows the dialog
        result = dialog.confirm_delete_account()
        
        # Verify the dialog was shown
        mock_question.assert_called_once()
        MockAccountManager.delete_account.assert_not_called()

        # Verify the result is what we expect when user clicks No
        dialog.accept.assert_not_called()

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

if __name__ == '__main__':
    unittest.main()
