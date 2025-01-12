import time

import pyautogui
import pytest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from account_add_dialog import AddAccountDialog
from account_confirm_dialog import ConfirmAccountDialog
from appconfig import AppConfig
from controllers import AppController

from PyQt5.QtTest import QTest

@pytest.fixture
def app(qtbot):
    app = QApplication([])
    return app

@pytest.fixture
def controller():
    mock_controller = MagicMock()
    mock_controller.find_qr_codes.return_value = ["otpauth://totp/Bogus:boogum%40badmail.com?secret=bogus&issuer=Bogus"]
    return mock_controller

@pytest.fixture
def dialog():  # this doesn't work in our case because we would need to use dependency injection to inject
               # this instance of ConfirmAccountDialog into AddAccountDialog
    # Create the dialog instance
    dialog = ConfirmAccountDialog()
    # Mock the exec_() method to return QDialog.Accepted
    dialog.exec_ = MagicMock(return_value=QDialog.Accepted)
    return dialog

@pytest.mark.parametrize("shortcut", [Qt.CTRL + Qt.Key_U])
def test_button_shortcut_activation(qtbot, shortcut,controller):
    app_config = AppConfig(None)
    dialog = AddAccountDialog(controller)
    controller.find_qr_codes.assert_called_once()
    controller.save_new_account.assert_called_once()

    # Simulate pressing the Ctrl+U shortcut to activate the button
    QTest.keyPress(dialog, Qt.Key_U, Qt.ControlModifier)


