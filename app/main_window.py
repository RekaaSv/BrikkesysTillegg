import logging

from PyQt5 import sip
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout

from common.gui.about_dialog import AboutDialog
from fakturagrunnlag.gui.main_window import FakturaMainWindow


class MainWindow(QMainWindow):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

        self.open_modules = []
        self.setWindowTitle("BrikkesysTillegg")
        self.setMinimumSize(300, 150)
        self.setWindowIcon(QIcon(self.ctx.icon_path))

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        self.build_ui(layout)

    def build_ui(self, layout):
        layout.setSpacing(20)

        help_button = QPushButton("Hjelp")
        help_button.clicked.connect(self.open_help)

        about_button = QPushButton("Om BrikkesysTillegg")
        about_button.clicked.connect(self.show_about_dialog)


        # Rekkefølge etter faktisk bruk
        btn_tp = QPushButton("Trekkeplan")
        btn_tp.clicked.connect(self.open_trekkeplan)

        btn_dr = QPushButton("Direkteresultater")
        btn_dr.clicked.connect(self.open_direkteresultater)

        btn_fg = QPushButton("Fakturagrunnlag")
        btn_fg.clicked.connect(self.open_fakturagrunnlag)

        title = QLabel("Brikkesys tilleggsmoduler")
        title.setAlignment(Qt.AlignCenter)

        help_about_layout = QHBoxLayout()

        help_about_layout.addWidget(help_button)
        help_about_layout.addWidget(about_button)
        layout.addLayout(help_about_layout)
        layout.addWidget(title)
        layout.addStretch()

        layout.addWidget(btn_tp)
        layout.addWidget(btn_dr)
        layout.addWidget(btn_fg)

        self.setLayout(layout)

    def open_help(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.ctx.help_pdf))

    def show_about_dialog(self):
        dialog = AboutDialog()
#        dialog.setWindowIcon(QIcon(self.icon_path))
        dialog.exec_()

    def open_fakturagrunnlag(self):
        # Hvis vinduet finnes og ikke er slettet → bruk det
        if getattr(self, "faktura_win", None) is not None:
            if not sip.isdeleted(self.faktura_win):
                self.faktura_win.raise_()
                self.faktura_win.activateWindow()
                return

        # Ellers opprett nytt vindu
        win = FakturaMainWindow(self.ctx)
        win.setAttribute(Qt.WA_DeleteOnClose)

        win.destroyed.connect(lambda: self.on_module_closed(win))

        # Lagre referanse for én-instans-sperre
        self.faktura_win = win

        # Registrer i open_modules
        self.open_modules.append(win)

        win.show()

    def open_trekkeplan(self):
        if getattr(self, "trekkeplan_win", None) is not None:
            if not sip.isdeleted(self.trekkeplan_win):
                self.trekkeplan_win.raise_()
                self.trekkeplan_win.activateWindow()
                return

        from trekkeplan.gui.main_window import TrekkeplanMainWindow
        win = TrekkeplanMainWindow(self.ctx)
        win.setAttribute(Qt.WA_DeleteOnClose)

        win.destroyed.connect(lambda: self.on_module_closed(win))

        # Lagre referanse for én-instans-sperre
        self.trekkeplan_win = win

        # Registrer i open_modules
        self.open_modules.append(win)

        win.show()

    def open_direkteresultater(self):
        if getattr(self, "direkte_win", None) is not None:
            if not sip.isdeleted(self.direkte_win):
                self.direkte_win.raise_()
                self.direkte_win.activateWindow()
                return

        from direkteresultater.gui.main_window import DirekteMainWindow
        win = DirekteMainWindow(self.ctx)
        win.setAttribute(Qt.WA_DeleteOnClose)
        win.destroyed.connect(lambda: self.on_module_closed(win))

        self.direkte_win = win
        self.open_modules.append(win)

        win.show()

    def on_module_closed(self, win):
        # Fjern fra open_modules
        self.open_modules = [m for m in self.open_modules if m is not win]

        # Nullstill instansreferansen hvis det er denne modulen
        if getattr(self, "faktura_win", None) is win:
            self.faktura_win = None
        if getattr(self, "trekkeplan_win", None) is win:
            self.trekkeplan_win = None

        # Hvis ingen moduler er åpne → lukk hovedvinduet
        if not self.open_modules:
            size = self.size()
            logging.info(f"Hovedvinduet avsluttes med størrelse: {size.width()} x {size.height()}")
            self.close()

