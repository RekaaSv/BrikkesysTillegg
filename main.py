import sys
from PyQt5.QtWidgets import QApplication
from common.gui.style import apply_global_style
from common.app_context import AppContext
from app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    apply_global_style(app)

    ctx = AppContext()
    win = MainWindow(ctx)
    win.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()