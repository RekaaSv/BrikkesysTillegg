import logging
import socket
import threading
import time

from PyQt5.QtWidgets import QMessageBox

from common.gui.style import RED_BTN, GREEN_BTN


class ServerControl:
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.server_running = False
        self.httpd = None
        self.request_count = 0

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

        from direkteresultater.server.http_server import InfoHandler
        self.httpd = HTTPServer(("0.0.0.0", port), InfoHandler)
        self.httpd.server_control = self # for at httpd skal kunne finne server_control.

        self.httpd.timeout = 1
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

        count = 0
        for _ in range(40):
            if self.is_port_open(port):
                self.server_running = True
                break
            time.sleep(0.05)
            count += 1
        logging.info(f"Ventet på server {count*50} ms.")

        if self.server_running:
            bind_ip = self.parent.ip_edit.text().strip()
            port = int(self.parent.port_edit.text())
            self.parent.local_url_value.setText(f"http://{bind_ip}:{port}/")

            lan_ip = socket.gethostbyname(socket.gethostname())
            self.parent.network_url_value.setText(f"http://{lan_ip}:{port}/")

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
            self.parent.server_status_label.setText("Status: Kjører")
            self.parent.server_status_label.setStyleSheet("color: green; font-weight: bold;")
            self.parent.reset_btn.setEnabled(False)
            self.parent.open_url_btn.setEnabled(True)
        else:
            self.parent.port_edit.setReadOnly(False)
            self.parent.port_edit.setProperty("readOnly", False)
            self.parent.port_edit.style().unpolish(self.parent.port_edit)
            self.parent.port_edit.style().polish(self.parent.port_edit)
            self.parent.http_start_btn.setText("Start HTTP server")
            self.parent.http_start_btn.setStyleSheet(GREEN_BTN)
            self.parent.http_start_btn.setToolTip("HTTP server kjører ikke. Trykk for å starte den.")
            self.parent.server_status_label.setText("Status: Stoppet")
            self.parent.server_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.parent.reset_btn.setEnabled(True)
            self.parent.open_url_btn.setEnabled(False)

    def is_port_open(self, port):
        s = socket.socket()
        try:
            s.connect(("127.0.0.1", port))
            s.close()
            return True
        except:
            return False