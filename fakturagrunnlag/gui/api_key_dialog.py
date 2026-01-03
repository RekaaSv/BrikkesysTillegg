from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout

class ApiKeyDialog(QDialog):
    def __init__(self, current_key="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eventor API-key")
        self.api_key_input = QLineEdit(current_key)
        self.api_key_input.setEchoMode(QLineEdit.Password)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout()
        layout.addRow("API-key:", self.api_key_input)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_key(self):
        return self.api_key_input.text()