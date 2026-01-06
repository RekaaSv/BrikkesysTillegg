from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel

from trekkeplan.gui.main_window import TrekkeplanMainWindow


class MainWindow(QMainWindow):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

        self.setWindowTitle("BrikkesysTillegg")
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        self.build_ui(layout)

    def build_ui(self, layout):
        layout.setSpacing(20)

        # Rekkefølge etter faktisk bruk
        btn_tp = QPushButton("Trekkeplan")
        btn_tp.clicked.connect(self.open_trekkeplan)
        layout.addWidget(btn_tp)

        btn_dr = QPushButton("Direkteresultater")
#        btn_dr.clicked.connect(start_direkteresultater)

        btn_fg = QPushButton("Fakturagrunnlag")
        btn_fg.clicked.connect(self.open_fakturagrunnlag)

        title = QLabel("Brikkesys tilleggsmoduler")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(btn_tp)
        layout.addWidget(btn_dr)
        layout.addWidget(btn_fg)

        self.setLayout(layout)

    def open_fakturagrunnlag(self):
        from fakturagrunnlag.gui.main_window import FakturaMainWindow
        self.faktura_win = FakturaMainWindow(self.ctx)
        self.faktura_win.show()

    def open_trekkeplan(self):
        from trekkeplan.gui.main_window import TrekkeplanMainWindow
        self.trekkeplan_win = TrekkeplanMainWindow(self.ctx)
        self.trekkeplan_win.show()
