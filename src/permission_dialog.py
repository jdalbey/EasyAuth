from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSpacerItem, QSizePolicy)


class PermissionDialog(QDialog):
    """ A confirmation dialog with custom buttons for responding.
    This is used to request permission from the user to scan the screen for a QR code.
    """
    ALWAYS_ALLOW = 1
    JUST_THIS_TIME = 2
    DENY = 0

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Permission request")
        self.setMinimumWidth(350)

        # Create the layout
        layout = QVBoxLayout()

        # Create a horizontal layout for the icon and message
        message_layout = QHBoxLayout()

        # Add the question icon
        icon_label = QLabel()
        icon_label.setPixmap(self.style().standardIcon(self.style().SP_MessageBoxQuestion).pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignTop)
        message_layout.addWidget(icon_label)
        message_layout.addSpacing(15)  # Add spacing between icon and text

        # Add the message
        message = """
This action will search the display screen for a QR code.
Nothing else on the screen will be examined or retained.
If you choose Deny you can still manually enter the secret key
using File > New Vault Entry > Enter Manually."""
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label, 1)  # Give text more stretch factor

        # Add the message layout to the main layout
        layout.addItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(message_layout)
        layout.addItem(QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Push buttons to the right

        # Create the buttons
        deny_button = QPushButton("&Deny")
        just_this_time_button = QPushButton("&Just once")
        always_allow_button = QPushButton("&Always allow")

        # Connect buttons to their respective return values
        deny_button.clicked.connect(lambda: self.done(PermissionDialog.DENY))
        just_this_time_button.clicked.connect(lambda: self.done(PermissionDialog.JUST_THIS_TIME))
        always_allow_button.clicked.connect(lambda: self.done(PermissionDialog.ALWAYS_ALLOW))

        # Add buttons to the button layout
        button_layout.addWidget(always_allow_button)
        button_layout.addWidget(just_this_time_button)
        button_layout.addWidget(deny_button)

        # Add button layout to the main layout
        layout.addLayout(button_layout)

        # Set the layout
        self.setLayout(layout)

        # Set appropriate default focus
        deny_button.setFocus()


def get_permission(parent=None):
    dialog = PermissionDialog(parent)
    result = dialog.exec_()
    return result