from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
# from trekkeplan.start_app import start_trekkeplan
# from direkteresultater.start_app import start_direkteresultater
from fakturagrunnlag.start_app import start_fakturagrunnlag

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BrikkesysTillegg")

        layout = QVBoxLayout()

        # Rekkefølge etter faktisk bruk
        btn_tp = QPushButton("Trekkeplan")
#        btn_tp.clicked.connect(start_trekkeplan)

        btn_dr = QPushButton("Direkteresultater")
#        btn_dr.clicked.connect(start_direkteresultater)

        btn_fg = QPushButton("Fakturagrunnlag")
        btn_fg.clicked.connect(start_fakturagrunnlag)

        layout.addWidget(btn_tp)
        layout.addWidget(btn_dr)
        layout.addWidget(btn_fg)

        self.setLayout(layout)