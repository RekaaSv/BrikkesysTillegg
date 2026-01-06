import configparser
import logging
import os
import traceback
import pymysql

from PyQt5.QtWidgets import QMessageBox

import common.sql
from common.error_handling import install_global_exception_hook
from common.logging_setup import setup_logging
from common.paths import resource_path
from common.connection import ConnectionManager

from trekkeplan.gui.main_window import TrekkeplanMainWindow
from trekkeplan.db import sql

_window = None

def start_trekkeplan():
    """
    Starter Fakturagrunnlag-modulen.
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

        # Ressurser
        icon_path = resource_path("terning.ico")
        pdf_path = resource_path("hjelp_trekkeplan.pdf")

        # Database-tilkobling
        conn_mgr = ConnectionManager(db_config)
        conn_mgr.get_connection()

        # Sjekk/installér DB-objekter
        is_installed = common.sql.is_db_objects_installed(conn_mgr)
        logging.info(f"DB objects installed: {is_installed}")

        if not is_installed:
            common.sql.is_db_at_least_version_8(conn_mgr)
            common.sql.install_db_objects(conn_mgr)

        # Start GUI
        global _window
        _window = TrekkeplanMainWindow(config, conn_mgr, icon_path, pdf_path)
        _window.show()

    except pymysql.Error as e:
        QMessageBox.critical(None, "Feil ved DB-kobling", f"Kunne ikke koble til databasen:\n{e}")
        traceback.print_exc()
        raise

    except Exception as e:
        logging.error("Systemfeil", exc_info=True)
        QMessageBox.critical(None, "Systemfeil", str(e))
        raise