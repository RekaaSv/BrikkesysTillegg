import os
import configparser
import logging

from common.connection import ConnectionManager
import common.sql
from common.error_handling import install_global_exception_hook
from common.logging_setup import setup_logging
from common.paths import resource_path
from common.registry import Registry


class AppContext:
    def __init__(self):
        # Finn configfil
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.abspath(os.path.join(base_dir, "..", "brikkesystillegg.cfg"))

        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        install_global_exception_hook()
        setup_logging()

        # Lagre config-seksjoner
        self.db_config = self.config["mysql"]
        self.log_config = self.config["logging"]

        # Ressurser
        self.icon_path = resource_path("reshot-icon-running-JUSXPBMDTN.ico")
        self.help_trekkeplan_pdf = resource_path("hjelp_trekkeplan.pdf")
        self.help_fakturagrunnlag_pdf = resource_path("hjelp_fakturagrunnlag.pdf")
        self.help_direkteresultater_pdf = resource_path("hjelp_direkteresultater.pdf")

        # Database
        self.conn_mgr = ConnectionManager(self.db_config)
        self.conn_mgr.get_connection()

        # Installer DB-objekter hvis nødvendig
        is_installed = common.sql.is_db_objects_installed(self.conn_mgr)
        logging.info(f"DB objects installed: {is_installed}")

        if not is_installed:
            try:
                common.sql.is_db_at_least_version_8(self.conn_mgr)
                common.sql.install_db_objects(self.conn_mgr)
            except Exception as e:
                logging.error(f"Failed to install DB objects. Error: {e}")
                raise

        self.registry = Registry("Brikkesys", "BrikkesysTillegg")

