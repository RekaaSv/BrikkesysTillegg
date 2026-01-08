import datetime
import logging
import webbrowser

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMainWindow, QDialog, QHBoxLayout, QFrame, \
    QLineEdit, QFormLayout, QApplication

import common.sql
from common.gui.common_table_item import CommonTableItem
from common.gui.utils import populate_table
from common.select_race_dialog import reload_race, SelectRaceDialog
from direkteresultater.server.http_server import InfoHandler
from direkteresultater.server.server_control import ServerControl

class DirekteMainWindow(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
#        self.conn_mgr = ctx.conn_mgr

        # Globale variable
        self.race_id = self.ctx.registry.get_int("direkte_race_id")
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

        cfg = self.ctx.config["direkteresultater"]
        self.default_ip = cfg.get("ip", "127.0.0.1")
        self.default_port = cfg.getint("port", 8080)
        self.default_cl_from = cfg.getint("cl_from", 1)
        self.default_cl_to = cfg.getint("cl_to", 999)
        self.default_scroll = cfg.getint("scroll", 3)
        self.default_px = cfg.getint("px", 1)

        reg = self.ctx.registry

        self.ip = reg.get("direkte_ip", self.default_ip)
        self.port = reg.get_int("direkte_port", self.default_port)
        self.cl_from = reg.get_int("direkte_cl_from", self.default_cl_from)
        self.cl_to = reg.get_int("direkte_cl_to", self.default_cl_to)
        self.scroll = reg.get_int("direkte_scroll", self.default_scroll)


        # Gjør connection manager tilgjengelig for HTTP-serveren
        InfoHandler.conn_mgr = self.ctx.conn_mgr

        self.init_ui()
        self.make_layout()

    def init_ui(self):
        self.select_race_btn = QPushButton("Velg løp")
        self.select_race_btn.clicked.connect(self.select_race)

        self.close_button = QPushButton("Avslutt")
        self.close_button.clicked.connect(self.close)

        self.ip_edit = QLineEdit(self.ip)
        self.port_edit = QLineEdit(str(self.port))
        self.cl_from_edit = QLineEdit(str(self.cl_from))
        self.cl_to_edit = QLineEdit(str(self.cl_to))
        self.scroll_edit = QLineEdit(str(self.scroll))

        self.ip_edit.editingFinished.connect(self.save_settings)
        self.port_edit.editingFinished.connect(self.save_settings)
        self.cl_from_edit.editingFinished.connect(self.save_settings)
        self.cl_to_edit.editingFinished.connect(self.save_settings)
        self.scroll_edit.editingFinished.connect(self.save_settings)

        self.ip_edit.textChanged.connect(self.update_url)
        self.port_edit.textChanged.connect(self.update_url)
        self.cl_from_edit.textChanged.connect(self.update_url)
        self.cl_to_edit.textChanged.connect(self.update_url)
        self.scroll_edit.textChanged.connect(self.update_url)

        self.url_edit = QLineEdit()
        self.url_edit.setReadOnly(True)
        self.url_edit.setStyleSheet("font-family: Consolas, monospace;")

        self.copy_url_btn = QPushButton("Kopier URL")
        self.copy_url_btn.clicked.connect(self.copy_url)

        self.open_url_btn = QPushButton("Åpne i nettleser")
        self.open_url_btn.clicked.connect(self.open_url)



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

        form = QFormLayout()
        form.addRow("IP-adresse:", self.ip_edit)
        form.addRow("Port:", self.port_edit)
        form.addRow("Klasse fra:", self.cl_from_edit)
        form.addRow("Klasse til:", self.cl_to_edit)
        form.addRow("Scroll (sek):", self.scroll_edit)

        center_layout.addLayout(form)
        center_layout.addWidget(self.url_edit)

        url_btns = QHBoxLayout()
        url_btns.addWidget(self.copy_url_btn)
        url_btns.addWidget(self.open_url_btn)

        center_layout.addLayout(url_btns)

        self.setLayout(main_layout)

    def save_settings(self):
        reg = self.ctx.registry

        reg.set("direkte_ip", self.ip_edit.text())
        reg.set_int("direkte_port", int(self.port_edit.text()))
        reg.set_int("direkte_cl_from", int(self.cl_from_edit.text()))
        reg.set_int("direkte_cl_to", int(self.cl_to_edit.text()))
        reg.set_int("direkte_scroll", int(self.scroll_edit.text()))

    def build_url(self):
        if not self.race_id:
            return ""

        ip = self.ip_edit.text().strip()
        port = self.port_edit.text().strip()
        cl_from = self.cl_from_edit.text().strip()
        cl_to = self.cl_to_edit.text().strip()
        scroll = self.scroll_edit.text().strip()

        race_id = self.race["id"]

        return (
            f"http://{ip}:{port}/infoskjerm?"
            f"race={race_id}&cl_from={cl_from}&cl_to={cl_to}&scroll={scroll}"
        )

    def update_url(self):
        url = self.build_url()
        self.url_edit.setText(url)

    def copy_url(self):
        url = self.url_edit.text()
        if url:
            QApplication.clipboard().setText(url)

    def open_url(self):
        url = self.url_edit.text()
        if url:
            webbrowser.open(url)



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
                self.ctx.registry.set_int("direkte_race_id", self.race_id)
                self.update_url()


        #            self.after_plan_changed()
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
