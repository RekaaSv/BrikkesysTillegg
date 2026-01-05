from PyQt5.QtWidgets import QApplication
from common.main_window import MainWindow
from common.gui.style import apply_global_style
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)

    apply_global_style(app)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())