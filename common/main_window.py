from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
# from trekkeplan.start_app import start_trekkeplan
from direkteresultater.start_app import start_direkteresultater
from fakturagrunnlag.start_app import start_fakturagrunnlag
from trekkeplan.start_app import start_trekkeplan


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BrikkesysTillegg")

        layout = QVBoxLayout()
        layout.setSpacing(20)
        self.setMinimumWidth(300)

        # Rekkefølge etter faktisk bruk
        btn_tp = QPushButton("Trekkeplan")
        btn_tp.clicked.connect(start_trekkeplan)

        btn_dr = QPushButton("Direkteresultater")
        btn_dr.clicked.connect(start_direkteresultater)

        btn_fg = QPushButton("Fakturagrunnlag")
        btn_fg.clicked.connect(start_fakturagrunnlag)

        title = QLabel("Brikkesys tilleggsmoduler")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(btn_tp)
        layout.addWidget(btn_dr)
        layout.addWidget(btn_fg)

        self.setLayout(layout)