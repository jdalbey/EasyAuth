# Custom additions to dark theme
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
    /* color: green; */
}
QLineEdit {
    background-color: floralwhite;
    color:  #212f3c; /* near black */
}
QPushButton#editButton {
    qproperty-icon: url("images/edit_icon_light.png");
}
QPushButton#copyButton {
    qproperty-icon: url("images/copy_icon_light.png");
}
QPushButton#otpLabel {
    font-family: "DejaVu Sans Mono";
    font-size: 16px;
    /*
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
