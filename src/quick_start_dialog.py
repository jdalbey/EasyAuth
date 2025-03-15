import os
import sys
import logging

from appconfig import AppConfig
from utils import assets_dir
import markdown
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, QTextBrowser


class QuickStartDialog(QDialog):
    """ A dialog that displays the Quick Start Guide. """
    def __init__(self,parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setWindowFlags(Qt.WindowTitleHint | Qt.Dialog | Qt.WindowCloseButtonHint) # x-platform consistency

        self.setWindowTitle("Quick Start Guide")
        self.resize(700,550)
        layout = QVBoxLayout()

        display_window = QTextBrowser(self)
        display_window.setOpenExternalLinks(True)  # Enable clickable links
        display_window.setReadOnly(True)
        display_window.setLineWrapMode(QTextEdit.WidgetWidth)
        display_window.setStyleSheet("body {font-size: 30px}")

        # Load the text and set in the window
        content = self.load_quickstart_text()
        if len(content) > 0:
            display_window.setHtml(content)
        else:
            display_window.setHtml("""<h4>An internal error was encountered loading the quick start guide. 
                Please report this error to the developers.""")

        layout.addWidget(display_window)

        buttonBox = QDialogButtonBox()
        ok_btn = buttonBox.addButton(QDialogButtonBox.Ok)
        ok_btn.setText('O\u0332' + 'K')
        ok_btn.setShortcut('Alt+o')

        buttonBox.accepted.connect(self.accept)

        layout.addWidget(buttonBox)
        self.setLayout(layout)

        # Move the dialog to be offset from the main window so the user can see the 'Add Account' button
        # while viewing the guide.
        x = parent.geometry().x() + 250 if parent else 250
        y = parent.geometry().y() if parent else 100  # Fallback y if no parent
        self.move(x, y)

    def load_quickstart_text(self):
        """ Convert the markdown document to html and add style """
        dir_path = "docs"
        # Are we in production mode?
        if getattr(sys, 'frozen', False):
            dir_path = assets_dir()

        self.file_path = os.path.join(dir_path, 'Quick Start Guide.md')
        self.logger.debug(f"Quick Start Guide file_path: {self.file_path}")
        try:
            with open(self.file_path, "r",) as input_file:
                markdown_text = input_file.read()
            text = markdown.markdown(markdown_text)
            style_dark = """
<head>
<style>
body {
    font-family: "Open Sans",sans-serif, Verdana;
    font-size: 16px;
    color: white;
    line-height: 1.2;
}
</style>
</head>
<body>
"""
            # Set the styling based on current theme
            style = style_dark
            if AppConfig().get_theme_name() == 'light':
                # swap light for dark text color
                style = style.replace("color: white;","color: rgb(51, 51, 51);")
            # prepend style to html content
            text = style + text
        except FileNotFoundError as e:
            return ""
        return text


# NOTE: To include images in the guide they must be local: QTextEdit can't get remote URLs.
#display_window.setHtml(f"""
#    <h2>Quick Start Guide</h2>
#    <img src="file:///{image_path}" alt="TOTP code">
#""")
# image_path must be adjusted for pyinstaller

# To adjust the font size:
# font = display_window.font()
# font.setFamily("Courier")
# font.setPointSize(10)
