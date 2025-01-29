# Custom additions to dark theme
import qdarktheme

dark_qss = """
/*QLabel {
    color: goldenrod;
}*/
QPushButton {
    border-width: 2px;
}
QPushButton#editButton {
    qproperty-icon: url("images/edit_icon_dark.png");
}
QPushButton#copyButton {
    qproperty-icon: url("images/copy_icon_dark.png");
}
QPushButton#otpLabel {
    font-family: "DejaVu Sans Mono";
    font-size: 16px;
}
QListView::item
{
    border : 1px white;
    padding: 5px;
}
QLabel#timerLabel {
    background-color: dimgrey;
    color: white;
    padding: 3px 15px;
    border-radius: 15px;
}
"""
# Custom additions to light theme
light_qss = """
QLabel {
    /*color: green;*/
}
QCheckBox:focus {
    background-color: #d6dfea;
    color: #212f3c; /* near black */
}
QLineEdit {
    background-color: floralwhite;
    color:  #212f3c; /* near black */
}
QPushButton { background-color: #ebecf0 }  
/*toolbar background #ebebeb */
QPushButton#addAccountButton { background-color: #f0f0f0; }
QPushButton#addAccountButton:hover { background-color: #d6dfea; }
QPushButton#addAccountButton:pressed { background-color: #b9cee9; }

QPushButton#editButton {
    qproperty-icon: url("images/edit_icon_light.png");
}
QPushButton#otpLabel {
    font-family: "DejaVu Sans Mono";
    font-size: 16px;
    /*
    background-color: gray;
    border: None;
    background: transparent;
    color: black;
    */
}
QPushButton#otpLabel:hover {
    text-decoration: underline;
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
QLabel#timerLabel {
    background-color: lightgray;
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
