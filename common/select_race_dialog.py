import logging

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton
)
from PyQt5.QtCore import Qt

from common import sql
from common.gui.utils import set_table_sizes


class SelectRaceDialog(QDialog):
    def __init__(self, ctx, parent=None):
        super().__init__(parent)
        logging.info("commen.SelectRaceDialog")
        self.ctx = ctx
        self.parent = parent
        self.race = None

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
#        parent.table_race.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Knapper
        layout_buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Avbryt")
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
        rows, columns = sql.read_race_list(self.ctx.conn_mgr)
        self.parent.populate_my_table(self.table_race, columns, rows)
#        self.table_race.setColumnHidden(3, True)

        set_table_sizes(self.table_race, self.col_widths_races, 300)

    def ok_clicked(self):
        valgt = self.table_race.currentRow()
        if valgt >= 0:
            # Er dette løpet med i en bunt?
            item_bundle = self.table_race.item(valgt, 4)
            self.race = {
                "id": int(self.table_race.item(valgt, 0).text()),
                "day": self.table_race.item(valgt, 1).text(),
                "name": self.table_race.item(valgt, 2).text(),
                "bundle_id": int(item_bundle.text()) if item_bundle.text() else None,
            }
            self.accept()
"""
            item_bundle = self.table_race.item(valgt, 4)
            self.selected_bundle = int(item_bundle.text()) if item_bundle.text() else None

            # Id til valgt løp.
            item_id = self.table_race.item(valgt, 0)
            self.selected_race_id = int(item_id.text())

            # Dato og navn på valgt løp.
            self.race_day = self.table_race.item(valgt, 1).text()
            self.race_name = self.table_race.item(valgt, 2).text()
            self.selected_race = f"{self.race_day} {self.race_name}"
"""
