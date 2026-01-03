import configparser
import logging
import os
import traceback
import pymysql

from PyQt5.QtWidgets import QMessageBox

from common.error_handling import install_global_exception_hook
from common.logging_setup import setup_logging
from common.paths import resource_path
from common.connection import ConnectionManager

from fakturagrunnlag.gui.main_window import MainWindow
from fakturagrunnlag.db import sql
from fakturagrunnlag.html_report.http_server import InfoHandler


def start_fakturagrunnlag():
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
        pdf_path = resource_path("hjelp.pdf")

        # Database-tilkobling
        conn_mgr = ConnectionManager(db_config)
        conn_mgr.get_connection()

        # Gjør connection manager tilgjengelig for HTTP-serveren
        InfoHandler.conn_mgr = conn_mgr

        # Sjekk/installér DB-objekter
        is_installed = sql.is_db_objects_installed(conn_mgr)
        logging.info(f"DB objects installed: {is_installed}")

        if not is_installed:
            sql.is_db_at_least_version_8(conn_mgr)
            sql.install_db_objects(conn_mgr)

        # Start GUI
        window = MainWindow(config, conn_mgr, icon_path, pdf_path)
        window.show()

    except pymysql.Error as e:
        QMessageBox.critical(None, "Feil ved DB-kobling", f"Kunne ikke koble til databasen:\n{e}")
        traceback.print_exc()
        raise

    except Exception as e:
        logging.error("Systemfeil", exc_info=True)
        QMessageBox.critical(None, "Systemfeil", str(e))
        raise