import unittest
from unittest.mock import patch, Mock
from PyQt5.QtWidgets import QMessageBox, QApplication
from account_edit_dialog import EditAccountDialog
from models_singleton import Account
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
        MockAccountManager.delete_account.assert_called_once_with(account_in)

        # Verify the result is what we expect when user clicks Yes
        dialog.accept.assert_called_once()

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
