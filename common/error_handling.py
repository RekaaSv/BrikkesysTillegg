import logging
import traceback
from PyQt5.QtWidgets import QMessageBox


def global_exception_hook(exctype, value, tb):
    """Viser feilmeldinger i GUI og logger dem."""
    logging.error("Uventet feil:", exc_info=(exctype, value, tb))

    msg = f"{exctype.__name__}: {value}"
    QMessageBox.critical(None, "Systemfeil", msg)

    traceback.print_exception(exctype, value, tb)


def install_global_exception_hook():
    """Installerer global exception hook for hele applikasjonen."""
    import sys
    sys.excepthook = global_exception_hook