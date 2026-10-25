STYLE = '''
QMainWindow, QWidget {
    background: transparent;
    color: #c5ced1;
    font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
}
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background: transparent;
    border: 0;
}
QFrame#card, QFrame#metric {
    background: rgba(8, 13, 16, 0.72);
    border: 1px solid #69777a;
    border-radius: 0;
}
QLabel#brand { color: #93a1a4; font-size: 12px; font-weight: 600; letter-spacing: 1px; }
QLabel#subject { font-size: 19px; font-weight: 700; color: #dbe5e8; }
QLabel#headline { font-size: 19px; font-weight: 700; color: #d9e1e5; }
QLabel#readout { font-size: 17px; font-weight: 700; color: #f0c674; }
QLabel#processName { color: #6ed6c3; font-size: 12px; }
QLabel#processPercent { color: #f0c674; font-size: 12px; font-weight: 700; }
QFrame#processRow {
    background: rgba(10, 16, 19, 0.42);
    border: 0;
    border-bottom: 1px dotted #33484d;
}
QLabel#section { font-size: 12px; font-weight: 700; margin-top: 1px; color: #75d5c3; }
QLabel#timer { font-size: 46px; font-weight: 700; color: #f1f3e9; }
QLabel#muted { color: #8f9da0; font-size: 12px; }
QLabel#status { color: #8ed49a; font-size: 12px; }
QLabel#tip {
    background: rgba(8, 13, 16, 0.72);
    border: 1px solid #69777a;
    border-radius: 0;
    padding: 6px 9px;
    color: #9baab0;
    font-size: 13px;
}
QLabel#metricValue { color: #d6e0e3; font-size: 18px; font-weight: 700; }
QLineEdit {
    background: rgba(5, 10, 12, 0.86);
    border: 1px solid #718083;
    border-radius: 0;
    padding: 6px 8px;
    color: #d6e0e3;
    font-size: 14px;
}
QLineEdit:focus { border: 1px solid #c39a54; }
QSpinBox, QComboBox {
    background: rgba(5, 10, 12, 0.86);
    border: 1px solid #718083;
    border-radius: 0;
    padding: 10px 12px;
    color: #d6e0e3;
}
QCheckBox { color: #aebdc2; spacing: 8px; }
QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #52636b; background: #0d1317; }
QCheckBox::indicator:checked { background: #b89558; border-color: #d0b477; }
QPushButton {
    background: rgba(15, 24, 27, 0.88);
    border: 1px solid #637174;
    border-radius: 0;
    padding: 6px 10px;
    color: #c7d2d6;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover { background: rgba(39, 62, 64, 0.9); border-color: #79cbbd; }
QPushButton:disabled { color: #536169; border-color: #253139; }
QPushButton#primary { background: #b8d8b3; color: #0b1211; border-color: #d0efd0; }
QPushButton#primary:hover { background: #d4efd0; }
QPushButton#chip { padding: 4px 8px; background: rgba(24, 36, 42, 0.82); color: #b9c9ce; }
QPushButton#chip:hover { background: #263a43; }
QProgressBar {
    background: rgba(5, 10, 12, 0.75);
    border: 1px solid #526467;
    border-radius: 0;
    height: 8px;
}
QProgressBar::chunk { background: #64c454; border-radius: 0; }
QTableWidget {
    background: rgba(5, 10, 12, 0.78);
    alternate-background-color: rgba(17, 31, 32, 0.55);
    color: #c5ced1;
    border: 1px solid #69777a;
    gridline-color: transparent;
    selection-background-color: rgba(38, 77, 72, 0.9);
    selection-color: #f0f3e9;
}
QHeaderView::section {
    background: rgba(12, 23, 25, 0.92);
    color: #75d5c3;
    border: 0;
    border-bottom: 1px solid #69777a;
    padding: 4px 6px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#dateCard {
    text-align: left;
    background: rgba(21, 31, 36, 0.88);
    border: 1px solid rgba(83, 106, 112, 0.7);
    color: #d1dcdf;
    padding: 14px 16px;
}
QPushButton#dateCard:hover, QPushButton#dateCard:checked {
    background: #1b2b32;
    border-color: #b89558;
}
QFrame#sessionRow {
    background: rgba(15, 23, 27, 0.82);
    border: 0;
    border-left: 2px solid #3b545b;
    border-radius: 0;
}
QPushButton#sessionRow {
    text-align: left;
    background: rgba(15, 23, 27, 0.82);
    border: 0;
    border-bottom: 1px solid #26343b;
    color: #becbd0;
    padding: 11px 13px;
}
QPushButton#sessionRow:hover, QPushButton#sessionRow:checked {
    background: #1a2a30;
    border-color: #7f9b88;
}
'''
