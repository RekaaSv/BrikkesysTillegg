import logging
import threading

from PyQt5.QtWidgets import QMessageBox

from common.gui.style import RED_BTN, GREEN_BTN
from direkteresultater.server.http_server import InfoHandler


class ServerControl:
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.server_running = False
        self.httpd = None

#        self.button = QPushButton("Start server")
#        self.button.clicked.connect(self.toggle_server)

#        layout = QVBoxLayout()
#        layout.addWidget(self.button)
#        self.setLayout(layout)

    def toggle_server(self):
        logging.info("toggle_server")
        if self.server_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        logging.info("start_server")

        # 1. Sjekk om GUI-feltene er gyldige
        if not self.parent.is_valid():
            QMessageBox.warning(
                self.parent,
                "Feil",
                "Kan ikke starte server: Ugyldige felter."
            )
            return

        # 2. Nå er vi trygge – porten kan parses
        import threading
        from http.server import HTTPServer

        port = int(self.parent.port_edit.text())

        self.httpd = HTTPServer(("0.0.0.0", port), InfoHandler)
        self.httpd.timeout = 1
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

        self.server_running = True
        self.update_button()

    def stop_server(self):
        logging.info("stop_server")

        if not self.server_running:
            return

        self.server_running = False
        self.update_button()

        # shutdown må kjøres i egen tråd
        threading.Thread(target=self.httpd.shutdown, daemon=True).start()

    def update_button(self):
        if self.server_running:
            # port readOnly, og sett stil deretter.
            self.parent.port_edit.setReadOnly(True)
            self.parent.port_edit.setProperty("readOnly", True)
            self.parent.port_edit.style().unpolish(self.parent.port_edit)
            self.parent.port_edit.style().polish(self.parent.port_edit)
            # Endre text og stil på knappen.
            self.parent.http_start_btn.setText("Stopp HTTP server")
            self.parent.http_start_btn.setStyleSheet(RED_BTN)
            self.parent.http_start_btn.setToolTip("HTTP server kjører nå. Trykk for å stoppe den.")
            self.parent.status_label.setText("Status: Kjører")
        else:
            self.parent.port_edit.setReadOnly(False)
            self.parent.port_edit.setProperty("readOnly", False)
            self.parent.port_edit.style().unpolish(self.parent.port_edit)
            self.parent.port_edit.style().polish(self.parent.port_edit)
            self.parent.http_start_btn.setText("Start HTTP server")
            self.parent.http_start_btn.setStyleSheet(GREEN_BTN)
            self.parent.http_start_btn.setToolTip("HTTP server kjører ikke. Trykk for å starte den.")
            self.parent.status_label.setText("Status: Stoppet")
