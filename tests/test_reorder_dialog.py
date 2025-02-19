import pytest
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt
from reorder_dialog import ReorderDialog
from account_mgr import OtpRecord
@pytest.fixture
def app(qtbot):
    app = QApplication([])
    return app

def test_dialog_noselection_OK(qtbot):
    rec1 = OtpRecord("Woogle","me@woogle.com","secret")
    rec2 = OtpRecord("Boogle","me@boogle.com","secret")
    accounts = [rec1.toAccount(), rec2.toAccount()]
    # Create and show the dialog
    dialog = ReorderDialog(accounts)

    # Wait for the dialog (it won't actually appear on screen because we didn't do show()
    qtbot.waitForWindowShown(dialog)

    # Verify the list was populated
    assert dialog.list_widget.count() == 2

# This attempt to simulate drag and drop doesn't work.
# def test_drag_and_drop_ascending(qtbot):
#     """Simulates drag and drop from row 1 to row 3."""
#     rec1 = OtpRecord("Able","me@woogle.com","secret")
#     rec2 = OtpRecord("Baker","me@boogle.com","secret")
#     rec3 = OtpRecord("Charly","me@boogle.com","secret")
#     rec4 = OtpRecord("Delta","me@boogle.com","secret")
#     accounts = [rec1.toAccount(), rec2.toAccount(), rec3.toAccount(), rec4.toAccount()]
#
#     dialog = ReorderDialog(accounts)
#     qtbot.waitForWindowShown(dialog)
#
#     source_row = 1
#     target_row = 3
#
#     source_item = dialog.list_widget.item(source_row)
#     target_item = dialog.list_widget.item(target_row)
#
#     assert source_item is not None
#     assert target_item is not None
#     item1 = source_item.text()
#     assert item1.find("Baker") > 0
#
#     # Get screen positions of source and target items
#     source_pos = dialog.list_widget.visualItemRect(source_item).center()
#     target_pos = dialog.list_widget.visualItemRect(target_item).center()
#     print (source_pos, target_pos)
#     # Simulate mouse press on source item
#     QTest.mousePress(dialog.list_widget.viewport(), Qt.LeftButton, pos=source_pos)
#
#     # Simulate mouse move to target position with drag action
#     QTest.mouseMove(dialog.list_widget.viewport(), pos=target_pos, delay=100)
#
#     # Simulate mouse release at target position
#     QTest.mouseRelease(dialog.list_widget.viewport(), Qt.LeftButton, pos=target_pos)
#
#     # Verify the item was moved
#     for idx in range(0,4):
#         print (dialog.list_widget.item(idx).text())
#
#     result = dialog.list_widget.item(target_row).text()
#     assert result.find("Baker") > 0
