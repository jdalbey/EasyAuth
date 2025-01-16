from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox


class QuickStartDialog(QDialog):
    def __init__(self,parent):
        super().__init__(parent)
        self.setWindowTitle("Quick Start Guide")
        self.resize(700,550)
        layout = QVBoxLayout()

        logOutput = QTextEdit(self)
        logOutput.setReadOnly(True)
        logOutput.setLineWrapMode(QTextEdit.WidgetWidth)
        content = self.load_quickstart_text()
        if len(content) > 0:
            logOutput.setHtml(content)
        else:
            logOutput.setHtml("<h2>Quick Start guide</h2> Appearing here soon.")

        # font = logOutput.font()
        # font.setFamily("Courier")
        # font.setPointSize(10)

        layout.addWidget(logOutput)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        layout.addWidget(buttonBox)

        self.setLayout(layout)

        response = self.exec()

    def load_quickstart_text(self):
        try:
            f = open("docs/quick_start_guide.html")
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