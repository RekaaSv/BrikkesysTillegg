from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QDateEdit, QComboBox, QPlainTextEdit
)
from PyQt5.QtCore import QDate

class CreateBundleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Opprett ny fakturabunt")

        layout = QFormLayout(self)

        # Fakturadato
        self.order_date_edit = QDateEdit()
        self.order_date_edit.setCalendarPopup(True)
        self.order_date_edit.setDate(QDate.currentDate())
        layout.addRow("Ordredato:", self.order_date_edit)

        # Prefikser og tekst
        self.remark_edit = QPlainTextEdit("Ordre for følgende løp:\n")
        self.remark_edit.setReadOnly(True)
        self.currency_edit = QComboBox()
#        self.currency_edit.addItems(["NOK", "SEK", "EUR", "USD"])
        self.currency_edit.addItems(["NOK"])

        layout.addRow("Fakturaene gjelder:", self.remark_edit)
        layout.addRow("Valuta:", self.currency_edit)

        # OK / Avbryt
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def get_values(self):
        return {
            "order_date": self.order_date_edit.date().toString("yyyy-MM-dd"),
            "remark": self.remark_edit.toPlainText(),
            "currency": self.currency_edit.currentText()
        }