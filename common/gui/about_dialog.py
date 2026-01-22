from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from app import __version_trekkeplan__, __version_direkteresultater__, __version_fakturagrunnlag__


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setWindowTitle("Om BrikkesysTillegg")

        self.setMinimumWidth(280)

        # Gjelder bare for denne dialogen.
        self.setStyleSheet("""
            QLabel {
                font-weight: normal;
                font-size: 12px;
                margin: 2px 0;
            }
        """)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("BrikkesysTillegg"))
        layout.addWidget(QLabel(f"\tTrekkeplan      \tVersjon: {__version_trekkeplan__}"))
        layout.addWidget(QLabel(f"\tDirekteresultater\tVersjon: {__version_direkteresultater__}"))
        layout.addWidget(QLabel(f"\tFakturagrunnlag \tVersjon: {__version_fakturagrunnlag__}"))
        layout.addWidget(QLabel("Utviklet av Brikkesys/SvR"))
        close_btn = QPushButton("Lukk")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        self.setLayout(layout)
