from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QApplication, QLabel, QDialog)
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QIcon
import json
import sys
import provider_map

class SearchBox(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        # Handle special keys
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab, Qt.Key_Down):
            if self.parent and hasattr(self.parent, 'handle_search_special_keys'):
                self.parent.handle_search_special_keys(event.key())
            if event.key() != Qt.Key_Down:  # Allow normal processing for non-Down keys
                event.accept()
                return
        # Allow normal text input
        super().keyPressEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        # Clear table selection when search box gets focus
        if self.parent and hasattr(self.parent, 'clear_table_selection'):
            self.parent.clear_table_selection()

class ProviderSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_provider = None
        self.providers = provider_map.Providers()
        self.all_items = []  # Will store all items for filtering
        self.setup_ui()
        self.load_data()
        self.resize(600, 400)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Search box
        self.search_box = SearchBox(self)
        self.search_box.setPlaceholderText("Search...")
        layout.addWidget(self.search_box)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Icon", "Provider", "Domain"])
        
        # Optimize table appearance
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 40)  # Icon column width
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Selection behavior
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)

        # Connect signals
        self.search_box.textChanged.connect(self.filter_items)
        self.table.itemSelectionChanged.connect(self.handle_selection)

        # Install event filter on table for handling Backtab and Enteer
        self.table.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.table:
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_Backtab:
                    self.search_box.setFocus()
                    self.clear_table_selection()
                    return True
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_Return:
                    selected_row = self.table.currentRow()
                    item = self.table.item(selected_row, 1)
                    self.selected_provider = item.text()
                    self.accept()
        return super().eventFilter(obj, event)


    def select_first_row(self):
        if self.table.rowCount() > 0:
            # Set current cell to first cell of first row
            self.table.setCurrentCell(0, 1)  # Select the provider column
            # Select the entire row
            self.table.selectRow(0)
            self.selected_provider = self.table.item(0, 1).text()

    def handle_search_special_keys(self, key):
        if self.table.rowCount() >= 1:
            if self.table.rowCount() == 1:
                self.select_and_close()
            else:
                self.select_first_row()
                self.table.setFocus()

    def clear_table_selection(self):
        self.table.clearSelection()
        self.selected_provider = None

    def load_data(self):
        try:
            for provider_name, data in self.providers.provider_map.items():
                domain = data['domain']
                raw_image = data['raw_image']
                list_item = {"icon": raw_image, "provider": provider_name, "domain": domain}
                self.all_items.append(list_item)
        except FileNotFoundError:
            # Sample data with new provider names
            self.all_items = [
                {"icon": "icon1.png", "provider": "Figma", "domain": "domain1.com"},
                {"icon": "icon2.png", "provider": "Garden", "domain": "domain2.com"},
                {"icon": "icon3.png", "provider": "Gargle", "domain": "domain3.com"},
                {"icon": "icon4.png", "provider": "Google", "domain": "domain4.com"}
            ]
        self.populate_table(self.all_items)

    def populate_table(self, items):
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            # Icon
            icon_item = QTableWidgetItem()
            icon = QIcon()
            icon.addPixmap(self.providers.get_provider_icon_pixmap(item['provider']))
            icon_item.setIcon(icon)
            self.table.setItem(row, 0, icon_item)
            
            # Provider
            provider_item = QTableWidgetItem(item['provider'])
            self.table.setItem(row, 1, provider_item)
            
            # Domain
            domain_item = QTableWidgetItem(item['domain'])
            self.table.setItem(row, 2, domain_item)

    def filter_items(self):
        search_text = self.search_box.text().lower()
        filtered_items = [
            item for item in self.all_items
            if search_text in item['provider'].lower()
        ]
        self.populate_table(filtered_items)
        
        # If exactly one item remains, select it
        if len(filtered_items) == 1:
            self.select_first_row()
            self.selected_provider = filtered_items[0]['provider']

    def handle_selection(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_provider = self.table.item(row, 1).text()

    def select_and_close(self):
        print(f"Selected: {self.selected_provider}")
        self.accept()

    def get_selected_provider(self):
        return self.selected_provider


def main():
    app = QApplication(sys.argv)
    
    # Set up style for a more modern look
    app.setStyle('Fusion')
    
    dialog = ProviderSearchDialog()

    # Show the dialog and get the result
    if dialog.exec_() == QDialog.Accepted:
        selected = dialog.get_selected_provider()
        print(f"Main Selected provider: {selected}")
    else:
        print("No selection made")

if __name__ == '__main__':
    main()
