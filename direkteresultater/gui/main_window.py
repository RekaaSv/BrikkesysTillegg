import datetime
import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMainWindow, QDialog, QHBoxLayout, QFrame

import common.sql
from common.gui.common_table_item import CommonTableItem
from common.gui.utils import populate_table
from common.select_race_dialog import reload_race, SelectRaceDialog
from common.settings import get_direkte_race_id, put_trekkeplan_race_id, put_direkte_race_id
from direkteresultater.server.http_server import InfoHandler
from direkteresultater.server.server_control import ServerControl

class DirekteMainWindow(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.conn_mgr = ctx.conn_mgr

        # Globale variable
        self.race_id = get_direkte_race_id()
        if self.race_id:
            self.race = reload_race(ctx.conn_mgr, self.race_id)
        else:
            self.race = {
                "id": None,
                "day": "",
                "name": "",
                "first_start": None,
                "bundle_id": None,
            }

        if not self.race_id: self.setWindowTitle("Brikkesys/SvR Direkteresultater")
        else: self.setWindowTitle(f"Brikkesys/SvR Direkteresultater - {self.race['name']}    {self.race['day']}")

        self.resize(800, 700)


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

        self.close_button = QPushButton("Avslutt")
        self.close_button.clicked.connect(self.close)

    def make_layout(self):
        #
        # Layout
        #
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        center_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        center_frame = QFrame()
        center_frame.setFrameShape(QFrame.StyledPanel)
        center_frame.setFrameShadow(QFrame.Plain)
        center_frame.setLayout(center_layout)
        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setFrameShadow(QFrame.Plain)
        bottom_frame.setLayout(bottom_layout)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(center_frame)
        #        main_layout.addLayout(center_layout)
        main_layout.addWidget(bottom_frame)

        # Plasser komponenter
        top_layout.addWidget(self.select_race_btn)
        top_layout.addWidget(self.http_start_btn)
        top_layout.addStretch()

        center_layout.addWidget(self.status_label)
        center_layout.addStretch()

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_button)

        self.setLayout(main_layout)



    def xmake_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.select_race_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.http_start_btn)

        self.setLayout(layout)

    def select_race(self: QWidget):
        logging.info("select_race")
        dialog = SelectRaceDialog(self.ctx, self)
#        dialog.setWindowIcon(QIcon(self.ctx.icon_path))

        if dialog.exec_() == QDialog.Accepted:
            self.race = dialog.race
            self.race_id = dialog.race["id"]
            if not self.race_id:
                self.setWindowTitle("Brikkesys/SvR Direktereultater")
            else:
                self.setWindowTitle(f"Brikkesys/SvR Direktereultater - {self.race['name']}    {self.race['day']}")
            put_direkte_race_id(self.race_id)

            self.after_plan_changed()
        else:
            logging.debug("Brukeren avbrøt")

    def after_plan_changed(self):
        logging.info("after_plan_changed")



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
