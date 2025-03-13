# Custom additions to dark theme
import qdarktheme

dark_qss = """
QLineEdit:read-only {
                background-color: gray; 
                color: Gainsboro;
                border: 1px solid darkgray;
}
QPushButton {
    border-width: 2px;
}
QPushButton#providerLabel {background: transparent; border:none; color: floralwhite }
QPushButton#providerLabel:hover {color: blue}

QPushButton#otpLabel {
    font-family: "Courier New, monospace";
    font-size: 20px;
    font-weight: bold;
}
QPushButton#otpLabel:hover {
    text-decoration: underline;
    color: blue;
    }
QListView::item
{
    border : 1px white;
    padding: 5px;
}
QLabel#timerLabel {
    background-color: gray;
    color: white;
    padding: 3px 15px;
    border-radius: 15px;
}
"""
# Custom additions to light theme
light_qss = """
QCheckBox:focus {
    background-color: #d6dfea;
    color: #212f3c; /* near black */
}
QLineEdit {
    background-color: floralwhite;
    color:  #212f3c; /* near black */
}
QLineEdit:read-only {
                background-color: #ebebeb;
                color: gray;
                border: 1px solid darkgray;
}
QPushButton { background-color: #ebecf0 }  
/*toolbar background #ebebeb */

QPushButton#providerLabel {
    background: transparent; 
    border:none; color: #212f3c; /* near black */ 
}
QPushButton#providerLabel:hover {color: blue}

QPushButton#addAccountButton { background-color: #f0f0f0; }
QPushButton#addAccountButton:hover { background-color: #d6dfea; }
QPushButton#addAccountButton:pressed { background-color: #b9cee9; }

QPushButton#otpLabel {
    font-family: "Courier New, monospace";
    font-size: 20px;
    font-weight: bold;
}
QPushButton#otpLabel:hover {
    color: blue;
    }

/* For Reorder dialog */
QListWidget {
    border : 2px solid black;
    /* background: #fafbeb; */  
}
QListView::item
{
    /*border : 1px black;*/
    padding: 5px;
}
QListView::item:selected
{
    border : 1px dashed black;
    background : lightblue;
    color: #212f3c; /* near black */
}

/* For Timer */
QLabel#timerLabel {
    background-color:lightgray;
    color: black;
    padding: 3px 15px;
    border-radius: 15px;
}
QToolTip#timerLabel {
    color: black;
    background-color: ivory;
    border: 1px solid black;
}
"""

# Info button: Make square button invisible so only circular icon shows
info_btn_style = """
    QToolButton {
        border: none;       /* Remove border */
        background: none;   /* Remove background */
        padding: 0px;       /* Remove padding */
    }
    """
