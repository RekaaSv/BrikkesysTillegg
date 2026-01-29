import os
import configparser
import logging
import sys

from common.connection import ConnectionManager
import common.sql
from common.error_handling import install_global_exception_hook
from common.logging_setup import setup_logging
from common.paths import resource_path
from common.registry import Registry


class AppContext:
    def __init__(self):
        self.message_bar = None   # settes av hovedvinduet

        # Finn configfil
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        config_path = os.path.join(base_dir, "brikkesystillegg.cfg")

        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        install_global_exception_hook()

        # Lagre config-seksjoner
        self.db_config = self.config["mysql"]
        self.log_config = self.config["logging"]

        setup_logging(
            log_file=self.log_config.get("file", "BrikkesysTillegg.log"),
            level=self.log_config.get("level", "INFO"),
            max_bytes=self.log_config.getint("max_bytes", 500_000),
            backup_count=self.log_config.getint("backup_count", 5)
        )

        # Ressurser
        self.icon_path = resource_path("reshot-icon-running-JUSXPBMDTN.ico")
        self.help_pdf = resource_path("hjelp.pdf")
        self.help_trekkeplan_pdf = resource_path("hjelp_trekkeplan.pdf")
        self.help_fakturagrunnlag_pdf = resource_path("hjelp_fakturagrunnlag.pdf")
        self.help_direkteresultater_pdf = resource_path("hjelp_direkteresultater.pdf")
        self.update_bat = resource_path("update.bat")

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
