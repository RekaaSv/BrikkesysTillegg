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

    """)
