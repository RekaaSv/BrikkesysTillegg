import logging
import threading


from fakturagrunnlag.html_report.http_server import InfoHandler


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
        # Start server i egen tråd
        import threading
        from http.server import HTTPServer, SimpleHTTPRequestHandler

        self.httpd = HTTPServer(("0.0.0.0", 8000), InfoHandler)
        self.httpd.timeout = 1  # gjør shutdown rask
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
            self.parent.http_start_btn.setText("Stopp HTTP server")
            self.parent.http_start_btn.setStyleSheet("background-color: #d9534f; color: white;")
        else:
            self.parent.http_start_btn.setText("Start HTTP server")
            self.parent.http_start_btn.setStyleSheet("background-color: #5cb85c; color: white;")
