from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMainWindow

from direkteresultater.server.http_server import InfoHandler
from direkteresultater.server.server_control import ServerControl

class DirekteMainWindow(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

        self.conn_mgr = ctx.conn_mgr

        self.setWindowTitle("Direkteresultater")

        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Stoppet")

        self.server_control = ServerControl(self)
        self.http_start_btn = QPushButton("Start HTTP server")
        self.http_start_btn.setToolTip("Start HTTP server for reultatliste.")
        self.http_start_btn.clicked.connect(self.server_control.toggle_server)

        layout.addWidget(self.status_label)
        layout.addWidget(self.http_start_btn)

        self.setLayout(layout)

        # Gjør connection manager tilgjengelig for HTTP-serveren
        InfoHandler.conn_mgr = self.conn_mgr


    def closeEvent(self, event):
        # Stopp serveren hvis den kjører
        if self.server_control.server_running:
            self.server_control.stop_server()

        event.accept()  # lukk vinduet
