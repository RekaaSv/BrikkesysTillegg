import logging
import webbrowser

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QDialog, QHBoxLayout, QFrame, \
    QLineEdit, QFormLayout, QApplication, QGroupBox

from common.gui.common_table_item import CommonTableItem
from common.gui.message_bar import MessageBar
from common.gui.utils import populate_table
from common.message_handler import MessageHandler
from common.select_race_dialog import reload_race, SelectRaceDialog
from direkteresultater.server.http_server import InfoHandler
from direkteresultater.server.server_control import ServerControl

class DirekteMainWindow(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

        self.message_bar = MessageBar()
        self.msg = MessageHandler(self.message_bar)

#        self.ctx.set_message_bar(self.message_bar)

        self.resize(850, 400)
        self.setWindowIcon(QIcon(self.ctx.icon_path))

        cfg = self.ctx.config["direkteresultater"]
        self.default_ip = cfg.get("ip", "127.0.0.1")
        self.default_port = cfg.getint("port", 8080)
        self.default_cl_from = cfg.getint("cl_from", 1)
        self.default_cl_to = cfg.getint("cl_to", 999)
        self.default_scroll = cfg.getint("scroll", 3)
        self.default_px = cfg.getint("px", 1)

        reg = self.ctx.registry

        self.ip = reg.get_str("direkte_ip", self.default_ip)
        self.port = reg.get_int("direkte_port", self.default_port)
        self.cl_from = reg.get_int("direkte_cl_from", self.default_cl_from)
        self.cl_to = reg.get_int("direkte_cl_to", self.default_cl_to)
        self.scroll = reg.get_int("direkte_scroll", self.default_scroll)
        self.px = reg.get_int("direkte_px", self.default_px)

        # Gjør connection manager tilgjengelig for HTTP-serveren
        InfoHandler.conn_mgr = self.ctx.conn_mgr

        self.select_race_btn = QPushButton("Velg løp")
        self.reset_btn = QPushButton("Tilbakestill parametere")
        self.reset_btn.setToolTip("Slett lagrede URL-innstillinger og bruk standardverdier fra konfig.")
        self.close_button = QPushButton("Avslutt")

        self.help_button = QPushButton("Hjelp")
        self.help_button.setFixedWidth(150)
        self.help_button.clicked.connect(self.open_help)

        self.url_edit = QLineEdit()
        self.url_edit.setReadOnly(True)
        self.url_edit.setStyleSheet("font-family: Consolas, monospace;")

        self.copy_url_btn = QPushButton("Kopier URL")
        self.open_url_btn = QPushButton("Åpne URL i nettleser")
        self.open_url_btn.setEnabled(False)

        # Redigere parametere.
        self.ip_edit = QLineEdit(self.ip)
        self.port_edit = QLineEdit(str(self.port))
        self.cl_from_edit = QLineEdit(str(self.cl_from))
        self.cl_to_edit = QLineEdit(str(self.cl_to))
        self.scroll_edit = QLineEdit(str(self.scroll))
        self.px_edit = QLineEdit(str(self.px))

        # Server info.
        self.server_status_label = self.form_label("Status: Stoppet")
        self.server_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.server_status_label.setProperty("class", "sectionheader")

        # Feltvalidering info.
        self.validation_label = self.form_label("Status: OK")
        self.validation_label.setStyleSheet("color: green; font-weight: bold;")
        self.validation_label.setProperty("class", "sectionheader")



        # Server tilstand.
        self.local_url_value = QLineEdit()
        self.local_url_value.setReadOnly(True)
        self.network_url_value = (QLineEdit())
        self.network_url_value.setReadOnly(True)
        self.request_count_value = QLineEdit()
        self.request_count_value.setReadOnly(True)
        self.last_req_ip_value = QLineEdit()
        self.last_req_ip_value.setReadOnly(True)
        self.last_req_path_value = QLineEdit()
        self.last_req_path_value.setReadOnly(True)
        self.last_req_time_value = QLineEdit()
        self.last_req_time_value.setReadOnly(True)
        self.last_req_ip_value.setStyleSheet("font-family: Consolas, monospace;")

        #        self.init_ui()
        self.server_control = ServerControl(self)
        self.http_start_btn = QPushButton("")
        self.http_start_btn.setToolTip("Start HTTP server for reultatliste.")

        # Globale variable
        self.race_id = self.ctx.registry.get_int("direkte_race_id")
        if self.race_id:
            self.race = reload_race(ctx.conn_mgr, self.race_id)
            self.update_url()
        else:
            self.race = {
                "id": None,
                "day": "",
                "name": "",
                "first_start": None,
                "drawplan_changed": None,
                "draw_time": None,
                "bundle_id": None,
            }

        if not self.race_id:
            self.setWindowTitle("Direkteresultater")
        else:
            self.setWindowTitle(f"Direkteresultater - {self.race['name']}    {self.race['day']}")

        self.make_connections()

        self.server_control.server_running = False
        self.server_control.update_button()

        self.make_layout()



    def make_connections(self):
        self.http_start_btn.clicked.connect(self.server_control.toggle_server)

        self.select_race_btn.clicked.connect(self.select_race)
        self.reset_btn.clicked.connect(self.reset_settings)
        self.close_button.clicked.connect(self.close)
        self.ip_edit.editingFinished.connect(self.save_settings)
        self.port_edit.editingFinished.connect(self.save_settings)
        self.cl_from_edit.editingFinished.connect(self.save_settings)
        self.cl_to_edit.editingFinished.connect(self.save_settings)
        self.scroll_edit.editingFinished.connect(self.save_settings)
        self.px_edit.editingFinished.connect(self.save_settings)

        for edit in [
            self.ip_edit,
            self.port_edit,
            self.cl_from_edit,
            self.cl_to_edit,
            self.scroll_edit,
            self.px_edit,
        ]:
            edit.textChanged.connect(self.update_validation_status)
            edit.textChanged.connect(self.update_url)

        self.copy_url_btn.clicked.connect(self.copy_url)
        self.open_url_btn.clicked.connect(self.open_url)




    def make_layout(self):
        #
        # Layout
        #
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        center_layout = QHBoxLayout()
        center_left_layout = QVBoxLayout()
        center_right_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()
#        left_group_layout = QVBoxLayout()
#        right_group_layout = QVBoxLayout()

        center_frame = QFrame()
        center_frame.setFrameShape(QFrame.StyledPanel)
        center_frame.setFrameShadow(QFrame.Plain)
        center_frame.setLayout(center_layout)
        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setFrameShadow(QFrame.Plain)
        bottom_frame.setLayout(bottom_layout)

        left_group = QGroupBox("URL Innstillinger")
#        left_group.setFont(QFont("Segoe UI", 14)) # Dummy
        right_group = QGroupBox("Serverstatus")
#        right_group.setFont(QFont("Segoe UI", 14))
        left_group.setLayout(center_left_layout)
        right_group.setLayout(center_right_layout)

        center_layout.addWidget(left_group)
        center_layout.addWidget(right_group)

        center_layout.addLayout(center_left_layout)
        center_layout.addLayout(center_right_layout)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(center_frame)
        main_layout.addWidget(bottom_frame)
        main_layout.addWidget(self.message_bar)

#        left_group_layout.addLayout(form_layout)

        # Plasser komponenter
        top_layout.addWidget(self.select_race_btn)
        top_layout.addWidget(self.reset_btn)
        top_layout.addWidget(self.help_button)
        top_layout.addStretch()
        top_layout.addWidget(self.http_start_btn)

        center_left_layout.addWidget(self.validation_label)
        center_left_layout.addStretch()

        center_right_layout.addWidget(self.server_status_label)
        center_right_layout.addStretch()

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_button)

        form = QFormLayout()
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)
        form.setContentsMargins(0, 0, 0, 0)
        form.addRow(self.form_label("IP:"), self.ip_edit)
        form.addRow(self.form_label("Port:"), self.port_edit)
        form.addRow(self.form_label("Klasse fra:"), self.cl_from_edit)
        form.addRow(self.form_label("Klasse til:"), self.cl_to_edit)
        form.addRow(self.form_label("Scroll:"), self.scroll_edit)
        form.addRow(self.form_label("Pixcels pr scroll:"), self.px_edit)

        center_left_layout.addLayout(form)
        center_left_layout.addWidget(self.url_edit)


        server_form = QFormLayout()
        server_form.addRow(self.form_label("Lokal URL:"), self.local_url_value)
        server_form.addRow(self.form_label("Nettverks‑URL:"), self.network_url_value)
        server_form.addRow(self.form_label("Forespørsler:"), QLineEdit().setReadOnly(True))
        server_form.addRow(self.form_label("   Antall:"), self.request_count_value)
        server_form.addRow(self.form_label("   Siste req.:"), self.last_req_path_value)
        server_form.addRow(self.form_label("   Fra IP:"), self.last_req_ip_value)
        server_form.addRow(self.form_label("   Tidspunkt:"), self.last_req_time_value)

        center_right_layout.addLayout(server_form)

        url_btns = QHBoxLayout()
        url_btns.addWidget(self.copy_url_btn)
        url_btns.addWidget(self.open_url_btn)

        center_left_layout.addLayout(url_btns)

#        center_right_layout.addWidget(self.url_label)
        center_right_layout.addStretch()

        self.setLayout(main_layout)

    def form_label(self, text):
        lbl = QLabel(text)
        lbl.setProperty("class", "formlabel")
        return lbl

    def save_settings(self):
        if self.validate_fields():
            return  # ikke lagre ugyldige verdier

        reg = self.ctx.registry
        reg.set_str("direkte_ip", self.ip_edit.text())
        reg.set_int("direkte_port", int(self.port_edit.text()))
        reg.set_int("direkte_cl_from", int(self.cl_from_edit.text()))
        reg.set_int("direkte_cl_to", int(self.cl_to_edit.text()))
        reg.set_int("direkte_scroll", int(self.scroll_edit.text()))
        reg.set_int("direkte_px", int(self.px_edit.text()))

    def is_valid(self):
        return len(self.validate_fields()) == 0

    def reset_settings(self):
        reg = self.ctx.registry.settings  # QSettings-objektet

        # Finn alle nøkler som starter med direkte_
        keys = reg.allKeys()

        for key in keys:
            if key.startswith("direkte_") and key != "direkte_race_id":
                reg.remove(key)

        # Sett GUI-feltene tilbake til default
        self.ip_edit.setText(self.default_ip)
        self.port_edit.setText(str(self.default_port))
        self.cl_from_edit.setText(str(self.default_cl_from))
        self.cl_to_edit.setText(str(self.default_cl_to))
        self.scroll_edit.setText(str(self.default_scroll))
        self.px_edit.setText(str(self.default_px))

        # Lagre defaultene tilbake i registry
        self.save_settings()

        # Oppdater URL
        self.update_url()

    def build_url(self):
        if not self.race_id:
            return ""

        ip = self.ip_edit.text().strip()
        port = self.port_edit.text().strip()
        cl_from = self.cl_from_edit.text().strip()
        cl_to = self.cl_to_edit.text().strip()
        scroll = self.scroll_edit.text().strip()
        px = self.px_edit.text().strip()

        race_id = self.race["id"]

        return (
            f"http://{ip}:{port}/results?"
            f"race={race_id}&cl_from={cl_from}&cl_to={cl_to}&scroll={scroll}&px={px}"

        )

    def update_url(self):
        if self.validate_fields():
            self.url_edit.setText("")
            return

        self.url_edit.setText(self.build_url())

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
        dialog = SelectRaceDialog(self.ctx, self, [3, 4, 5, 6])
#        dialog.setWindowIcon(QIcon(self.ctx.icon_path))

        if dialog.exec_() == QDialog.Accepted:
            self.race = dialog.race
            self.race_id = dialog.race["id"]
            if not self.race_id:
                self.setWindowTitle("Direktereultater")
            else:
                self.setWindowTitle(f"Direktereultater - {self.race['name']}    {self.race['day']}")
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
        size = self.size()
        logging.info(f"Resultat vinduet avsluttes med størrelse: {size.width()} x {size.height()}")

        # Stopp serveren hvis den kjører
        if self.server_control.server_running:
            self.server_control.stop_server()

        event.accept()  # lukk vinduet

    def validate_fields(self):
        errors = {}

        # IP
        ip = self.ip_edit.text().strip()
        if not ip:
            errors["ip"] = "IP mangler"

        # Port
        try:
            port = int(self.port_edit.text())
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            errors["port"] = "Ugyldig port"

        # cl_from
        try:
            int(self.cl_from_edit.text())
        except ValueError:
            errors["cl_from"] = "Ugyldig 'klasse fra'"

        # cl_to
        try:
            int(self.cl_to_edit.text())
        except ValueError:
            errors["cl_to"] = "Ugyldig 'klasse til'"

        # scroll
        try:
            int(self.scroll_edit.text())
        except ValueError:
            errors["scroll"] = "Ugyldig scroll-verdi"

        # px
        try:
            int(self.px_edit.text())
        except ValueError:
            errors["px"] = "Ugyldig pixsels pr scroll"

        return errors

    def update_validation_status(self):
        errors = self.validate_fields()

        # Statuslabel
        if errors:
            self.validation_label.setText("Status: Ugyldige felter")
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.validation_label.setText("Status: OK")
            self.validation_label.setStyleSheet("color: green; font-weight: bold;")

        # Fargekode feltene
        self.set_error(self.ip_edit, "ip" in errors)
        self.set_error(self.port_edit, "port" in errors)
        self.set_error(self.cl_from_edit, "cl_from" in errors)
        self.set_error(self.cl_to_edit, "cl_to" in errors)
        self.set_error(self.scroll_edit, "scroll" in errors)
        self.set_error(self.px_edit, "px" in errors)


    def set_error(self, widget, has_error):
        widget.setProperty("class", "error" if has_error else "")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def open_help(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.ctx.help_direkteresultater_pdf))
