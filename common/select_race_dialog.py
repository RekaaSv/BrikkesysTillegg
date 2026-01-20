import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton
)
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime

import common
from common import sql
from common.gui.common_table_item import CommonTableItem
from common.gui.utils import set_table_sizes, populate_table

class SelectRaceDialog(QDialog):
    def __init__(self, ctx, parent=None, hide_cols = []):
        super().__init__(parent)
        logging.info("commen.SelectRaceDialog")
        self.ctx = ctx
        self.parent = parent
        self.race = {}

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Velg et løp")
        self.resize(300, 300)
        self.setFont(parent.font())  # arver font fra hovedvinduet
        self.col_widths_races = [60, 350, 100, 70, 150, 150, 70]

        self.selected_race_id = None

        # Tabell
        self.table_race = QTableWidget()
        self.table_race.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_race.setSelectionMode(QTableWidget.SingleSelection)
        self.table_race.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_race.verticalHeader().setVisible(False)

        for col_inx in hide_cols:
            self.table_race.setColumnHidden(col_inx, True)
            self.col_widths_races[col_inx] = 0

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
        rows, columns = sql.read_race_list(self.ctx.conn_mgr)

        populate_table(self.table_race, columns, rows, self.map_draw_row)
#        self.parent.populate_my_table(self.table_race, columns, rows)
        set_table_sizes(self.table_race, self.col_widths_races, 300)

    def map_draw_row(self, row_data):
        return [CommonTableItem.from_value(v, time_only=False) for v in row_data]


    def ok_clicked(self):
        valgt = self.table_race.currentRow()
        if valgt >= 0:
            day = datetime.strptime(self.table_race.item(valgt, 2).text() , "%Y-%m-%d").date()
            first_start_str = self.table_race.item(valgt, 3).text()
            if first_start_str != "" and first_start_str != "0:00":
                first_start_time = datetime.strptime(first_start_str, "%H:%M:%S").time()
                first_start = datetime.fromisoformat(f"{day}T{first_start_time}")
            else:
                first_start = None
            bundle_id = self.table_race.item(valgt, 6).text()
            null_dt = QDateTime(QDate(1, 1, 1), QTime(0, 0, 0))
            draw_time = self.table_race.item(valgt, 5).data(Qt.UserRole)
            if draw_time == "":
                draw_time = None
            drawplan_changed = self.table_race.item(valgt, 4).data(Qt.UserRole)
            if drawplan_changed == "":
                drawplan_changed = None


            self.race = {
                "id": int(self.table_race.item(valgt, 0).text()),
                "day": day,
                "name": self.table_race.item(valgt, 1).text(),
                "first_start":  first_start,
                "drawplan_changed": drawplan_changed,
                "draw_time": draw_time,
                "bundle_id": int(bundle_id) if bundle_id else None,
            }
            self.accept()


def reload_race(conn_mgr, raceid):
    logging.debug("refresh_race")
    rows0, columns0 = common.sql.read_race(conn_mgr, raceid)
    if not rows0: return
    race_row = rows0[0]
    return {
        "id": race_row[0],
        "day": race_row[2],
        "name": race_row[1],
        "first_start": race_row[3] if race_row[3] else None,
        "drawplan_changed": race_row[4] if race_row[4] else None,
        "draw_time": race_row[5] if race_row[5] else None,
        "bundle_id": race_row[6] if race_row[6] else None,
    }

