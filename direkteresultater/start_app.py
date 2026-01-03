import configparser
import logging
import os

from PyQt5.QtWidgets import QMessageBox

from common.error_handling import install_global_exception_hook
from common.logging_setup import setup_logging
from common.connection import ConnectionManager

from direkteresultater.gui.main_window import DirekteresultaterWindow
from direkteresultater.server.http_server import InfoHandler

_window = None

def start_direkteresultater():
    """
    Starter Direkteresultater-modulen.
    Forutsetter at QApplication allerede er startet av overbygningen.
    """

    install_global_exception_hook()
    setup_logging()

    try:
        # Finn configfil
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "..", "brikkesystillegg.cfg")
        config_path = os.path.abspath(config_path)

        config = configparser.ConfigParser()
        config.read(config_path)

        db_config = config["mysql"]
        log_config = config["logging"]


        # Database-tilkobling
        conn_mgr = ConnectionManager(db_config)
        conn_mgr.get_connection()

        # Gjør connection manager tilgjengelig for HTTP-serveren
        InfoHandler.conn_mgr = conn_mgr

        # Start GUI
        global _window
        _window = DirekteresultaterWindow(conn_mgr)
        _window.show()

    except Exception as e:
        logging.error("Feil ved oppstart av Direkteresultater", exc_info=True)
        QMessageBox.critical(None, "Feil", str(e))
        raise