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
    """)
