import datetime
import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMainWindow, QDialog

import common.sql
from common.gui.common_table_item import CommonTableItem
from common.gui.utils import populate_table
from common.settings import get_direkte_race_id
from direkteresultater.server.http_server import InfoHandler
from direkteresultater.server.server_control import ServerControl

class DirekteMainWindow(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.conn_mgr = ctx.conn_mgr

        self.race_id = get_direkte_race_id()
        self.race_name = None

        self.selected_race = None
        self.refresh_race(self.race_id)
        if not self.race_name: self.setWindowTitle("Brikkesys/SvR Direkteresultater - ")
        else: self.setWindowTitle("Brikkesys/SvR Direkteresultater - " + self.race_name + "   " + self.race_date_db.isoformat() )



        self.status_label = QLabel("Status: Stoppet")

        self.server_control = ServerControl(self)
        self.http_start_btn = QPushButton("Start HTTP server")
        self.http_start_btn.setToolTip("Start HTTP server for reultatliste.")
        self.http_start_btn.clicked.connect(self.server_control.toggle_server)


        # Gjør connection manager tilgjengelig for HTTP-serveren
        InfoHandler.conn_mgr = self.conn_mgr

        self.init_ui()
        self.make_layout()

    def init_ui(self):
        self.select_race_btn = QPushButton("Velg løp")
        self.select_race_btn.clicked.connect(self.select_race)

        self.race_label = QLabel("Valgt løp: (ingen)")

    def make_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.select_race_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.http_start_btn)
        layout.addWidget(self.race_label)

        self.setLayout(layout)

    def select_race(self):
        from common.select_race_dialog import SelectRaceDialog

        dlg = SelectRaceDialog(self.ctx, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            race_id = dlg.race["id"]
            if race_id:
                self.selected_race = race_id
                self.race_label.setText(f"Valgt løp: {dlg.race['name']} (ID: {dlg.race['id']})")

    def refresh_race(self, race_id):
        logging.debug("refresh_race")
        rows0, columns0 = common.sql.read_race(self.ctx.conn_mgr, race_id)
        if not rows0: return
        race = rows0[0]
        self.race_name = race[1]
        self.race_date_db: datetime.date = race[2]


    def populate_my_table(self, table, columns: list[any], rows):
        logging.debug("populate_my_table")
        populate_table(table, columns, rows, self.map_rows, None)

    def map_rows(self, row_data):
        return [CommonTableItem.from_value(v) for v in row_data]


    def closeEvent(self, event):
        # Stopp serveren hvis den kjører
        if self.server_control.server_running:
            self.server_control.stop_server()

        event.accept()  # lukk vinduet
