from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton
)


class NameDialog(QDialog):
    def __init__(self, old_name: str, title="Navn", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        # Input field
        self.edit = QLineEdit(self)
        self.edit.setText(old_name)
        self.edit.selectAll()
        layout.addWidget(self.edit)

        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Avbryt")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Make Enter = OK, Escape = Cancel
        self.edit.returnPressed.connect(self.accept)

    def get_new_name(self) -> str:
        return self.edit.text().strip()