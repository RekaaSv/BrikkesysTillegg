import logging

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton
)
from PyQt5.QtCore import Qt

from common import sql


class SelectRaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.info("commen.SelectRaceDialog")
        self.parent = parent
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Velg et løp")
        self.resize(650, 300)
        self.setFont(parent.font())  # arver font fra hovedvinduet
        self.col_widths_races = [60, 100, 350, 70, 70]

        self.selected_race_id = None

        # Tabell
        self.table_race = QTableWidget()
        self.table_race.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_race.setSelectionMode(QTableWidget.SingleSelection)
        self.table_race.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_race.verticalHeader().setVisible(False)
        self.table_race.horizontalHeader().setStyleSheet(self.parent.table_header_style_sheet)
        self.table_race.setStyleSheet(self.parent.table_style_sheet)
#        parent.table_race.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Knapper
        layout_buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(self.parent.button_style)
        cancel_btn = QPushButton("Avbryt")
        cancel_btn.setStyleSheet(self.parent.button_style)
        layout_buttons.addWidget(ok_btn)
        layout_buttons.addWidget(cancel_btn)

        ok_btn.clicked.connect(self.ok_clicked)
        cancel_btn.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.table_race)
        layout.addLayout(layout_buttons)
        self.setLayout(layout)

        self.refresh()

    def refresh(self):
        logging.info("common.SelectRaceDialog.refresh")
        rows, columns = None, None
        rows, columns = sql.read_race_list(self.parent.conn_mgr)
        self.parent.populate_my_table(self.table_race, columns, rows)
#        self.table_race.setColumnHidden(3, True)

        self.parent.set_table_sizes(self.table_race, self.col_widths_races, 300)

    def ok_clicked(self):
        valgt = self.table_race.currentRow()
        if valgt >= 0:
            # Er dette løpet med i en bunt?
            item_bundle = self.table_race.item(valgt, 4)
            self.selected_bundle = int(item_bundle.text()) if item_bundle.text() else None

            # Id til valgt løp.
            item_id = self.table_race.item(valgt, 0)
            self.selected_race_id = int(item_id.text())

            # Dato og navn på valgt løp.
            item_day = self.table_race.item(valgt, 1)
            item_race = self.table_race.item(valgt, 2)
            self.selected_race = f"{item_day.text()} {item_race.text()}"

            self.accept()