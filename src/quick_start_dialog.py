import os
import sys
import logging

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox

class QuickStartDialog(QDialog):
    def __init__(self,parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle("Quick Start Guide")
        self.resize(700,550)
        layout = QVBoxLayout()

        display_window = QTextEdit(self)
        display_window.setReadOnly(True)
        display_window.setLineWrapMode(QTextEdit.WidgetWidth)
        content = self.load_quickstart_text()
        if len(content) > 0:
            display_window.setHtml(content)
        else:
            display_window.setHtml("""<h4>An internal error was encountered loading the quick start guide. 
                Please report this error to the developers.""")

        layout.addWidget(display_window)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        layout.addWidget(buttonBox)
        self.setLayout(layout)

        # Move the dialog to be offset from the main window so the user can see the 'Add Account' button
        # while viewing the guide.
        y = parent.geometry().y()   # use parent's y position
        self.move(self.pos().x() + 250, y)  # offset from original x position


    def load_quickstart_text(self):
        dir_path = "docs"
        # Are we in production mode?
        if getattr(sys, 'frozen', False):
            # PyInstaller bundled case - prefix the temp directory path
            base_dir = sys._MEIPASS  # type: ignore   #--keep PyCharm happy
            dir_path = os.path.join(base_dir, "assets")
        self.file_path = os.path.join(dir_path, 'quick_start_guide.html')
        self.logger.debug(f"file_path: {self.file_path}")
        try:
            f = open(self.file_path)
            text = f.read()
            f.close()
        except FileNotFoundError as e:
            return ""
        return text

"""from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton
# Example of creating and showing the centered dialog

class YourDialog(QDialog):
    def __init__(self, parent=None):
        super(YourDialog, self).__init__(parent)
        
        layout = QVBoxLayout()
        button = QPushButton("Close")
        layout.addWidget(button)
        self.setLayout(layout)
        
        self.setWindowTitle("Centered Dialog")
        self.setGeometry(0, 0, 400, 300)  # Set the initial dialog size
        
        if parent:
            parent_center = parent.geometry().center()
            self_center = self.frameGeometry().center()
            self.move(parent_center - self_center)

# parent_window = YourParentWindow()
# dialog = YourDialog(parent=parent_window)
# dialog.exec_()"""

# To include images in the guide they must be local: QTextEdit can't get remote URLs.
#display_window.setHtml(f"""
#    <h2>Quick Start Guide</h2>
#    <img src="file:///{image_path}" alt="TOTP code">
#""")
# image_path must be adjusted for pyinstaller

# To adjust the font size:
# font = display_window.font()
# font.setFamily("Courier")
# font.setPointSize(10)
