import logging
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_file="BrikkesysTillegg.log",
    level="INFO",
    max_bytes=500_000,
    backup_count=5
):
    """Setter opp roterende logging for hele applikasjonen."""
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            file_handler,
            logging.StreamHandler()
        ]
    )

    logging.info("Logging startet")