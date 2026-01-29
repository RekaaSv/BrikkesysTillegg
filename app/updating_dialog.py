from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class UpdatingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oppdaterer")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "Oppdateringen pågår...\n"
            "Vennligst vent til den avsluttende bat-filen er ferdig.\n"
            "Da kan du starte BrikkesysTillegg igjen."
        ))
        self.setLayout(layout)