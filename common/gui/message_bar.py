from PyQt5 import QtWidgets, QtCore

MESSAGE_TEXT_COLOR = "#222"      # nøytral tekstfarge

class MessageBar(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.label = QtWidgets.QLabel("")
#        self.label.setStyleSheet("padding: 4px;")
        self.label.setStyleSheet("padding: 2px;")

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.label)
#        layout.setContentsMargins(4, 2, 4, 2)
        layout.setContentsMargins(3, 1, 3, 1)

        self.hide()

    def show_message(self, text, bg_color, timeout=10000):
        self.label.setText(text)
        self.setStyleSheet(f"background-color: {bg_color}; color: {MESSAGE_TEXT_COLOR};")
        self.show()

        if timeout:
            QtCore.QTimer.singleShot(timeout, self.hide)


    def clear(self):
        self.hide()
