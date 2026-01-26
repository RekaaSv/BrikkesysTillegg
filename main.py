import sys
from PyQt5.QtWidgets import QApplication

from app.update_checker import check_latest_version
from common.gui.style import apply_global_style
from common.app_context import AppContext
from app.main_window import MainWindow
from app import __version__ as CURRENT_VERSION


def main():
    app = QApplication(sys.argv)
    apply_global_style(app)

    ctx = AppContext()
    win = MainWindow(ctx)
    win.show()

    is_newer, latest, url = check_latest_version(CURRENT_VERSION)
    if is_newer:
        win.show_update_dialog(latest, url)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()