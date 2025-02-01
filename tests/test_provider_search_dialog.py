import unittest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt

from appconfig import AppConfig
from qr_selection_dialog import QRselectionDialog
from account_manager import Account
import logging
from provider_search_dialog import ProviderSearchDialog
def test_load_data(qtbot):
    logging.getLogger().addHandler(logging.StreamHandler())
    appconfig = AppConfig()

    dlg =  ProviderSearchDialog()
    dlg.load_data()
    assert len(dlg.all_items) > 0

