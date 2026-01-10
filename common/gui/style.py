# -------------------------
# Direkteresultater styles
# -------------------------

GREEN_BTN = """
QPushButton {
    background-color: #5cb85c;
    color: white;
    font-weight: bold;
    border: 1px solid #3e8e41;
    border-radius: 4px;
    padding: 4px 10px;
}
QPushButton:hover {
    background-color: #4cae4c;
}
QPushButton:pressed {
    background-color: #449d44;
}
QToolTip {
    color: black;
    background-color: #ffffe1;
    border: 1px solid #a0a0a0;
}
"""

RED_BTN = """
QPushButton {
    background-color: #d9534f;
    color: white;
    font-weight: bold;
    border: 1px solid #b52b27;
    border-radius: 4px;
    padding: 4px 10px;
}
QPushButton:hover {
    background-color: #c9302c;
}
QPushButton:pressed {
    background-color: #ac2925;
}
QToolTip {
    color: black;
    background-color: #ffffe1;
    border: 1px solid #a0a0a0;
}
"""


def apply_global_style(app):
    app.setStyleSheet("""
        QPushButton {
            background-color: rgb(200, 220, 240);
            border: 1px solid #888;
            padding: 4px 10px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: rgb(170, 200, 230);
        }
        QPushButton:pressed {
            background-color: rgb(150, 180, 220);
        }

        QLineEdit {
            background-color: rgb(255, 250, 205);  /* svak gul */
        }
        QLineEdit[readOnly="true"] {
            background-color: #eee;
            color: #555;
        }
        QLineEdit.error {
            background-color: #fdd;
        }

        QHeaderView::section {
            background-color: #e0e0e0;
            color: #333;
            font-weight: bold;
            padding: 1px;
            border: 1px solid #ccc;
        }

        QTableView {
            background-color: #f0f0f0; /* tomme områder */
            border: none;
        }
        QTableView::viewport {
            background-color: #f0f0f0; /* bak radene */
        }
        /*
        QTableView::item {
            background-color: white;
        }
        */
        QTableView::item:selected {
            background-color: #3399ff;  /* klassisk blå */
            color: white;
        }

        QLabel {
            font-weight: bold;
            font-size: 16px;
            margin: 10px 0;
        }
        QToolTip {
            color: black;
            background-color: #ffffe1;   /* standard lys gul tooltip */
            border: 1px solid #a0a0a0;
        }
        QLabel.formlabel {
            font-size: 11px;
            font-weight: normal;
            margin: 2px 0;
        }
        QLabel.sectionheader {
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 6px;
        }
        
        QFormLayout > QWidget {
            background: transparent;
        }
    """)
