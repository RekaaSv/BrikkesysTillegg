import logging
import shutil
import sys
import time
import zipfile
import tempfile
import requests
import subprocess
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QApplication


class UpdateWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, url, ctx):
        super().__init__()
        self.url = url
        self.ctx = ctx

    def run(self):
        download_and_update(self.url, self.ctx)
        self.finished.emit()

def download_and_update(download_url, ctx):
    logging.warning("Update starter")
    # Last ned ZIP til temp-mappe
    extract_dir = download_and_extract(download_url)

    app_dir = get_app_dir()

    logging.debug("App dir: %s", app_dir)
    logging.debug("extract_dir: %s", extract_dir)
    logging.debug("extract_dir content: %s", list(Path(extract_dir).iterdir()))

    ok = copy_to_app_dir(extract_dir, app_dir)

    if ok:
        run_update_bat(app_dir, ctx)
    else:
        QMessageBox.warning(
            None,
            "Feil",
            "Klarte ikke å kopiere ny versjon til programkatalogen."
        )


def download_and_extract(download_url) -> Path:
    logging.warning(f"Download URL: {download_url}")
    temp_dir = Path(tempfile.mkdtemp())
    zip_path = temp_dir / "update.zip"

    logging.info("Laster ned oppdatering...")

    response = requests.get(download_url, stream=True)
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logging.warning("ZIP-file lastet ned.")

    # Pakk ut ZIP
    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir()

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    logging.warning("ZIP-file pakket ut.")
    return extract_dir


def get_app_dir():
    return Path(sys.executable).parent


def copy_to_app_dir(extract_dir: Path, app_dir: Path) -> bool:
    """
    Kopierer ny versjon fra extract_dir inn i app_dir som .exe.new.
    Returnerer True hvis alt gikk bra, False hvis noe feilet.
    """
    logging.warning("Kopierer ny EXE-fil til programområdet som .exe.new")

    try:
        # Finn EXE i extract_dir
        candidates = list(extract_dir.glob("*.exe"))
        if not candidates:
            logging.error("Fant ingen EXE i extract_dir")
            return False

        new_exe = candidates[0]
        target_new = app_dir / f"{new_exe.stem}.exe.new"

        # Slett gammel .new hvis den finnes
        if target_new.exists():
            target_new.unlink()

        # Kopier ny EXE inn som .exe.new
        shutil.copy2(new_exe, target_new)

        # Rydd opp i extract_dir
        shutil.rmtree(extract_dir, ignore_errors=True)

        return True

    except Exception as e:
        logging.error(f"Feil under kopiering: {e}")
        return False

def run_update_bat(app_dir: Path, ctx):
    logging.warning("Oppretter update.bat i programområdet")

    bat_src = ctx.update_bat
    bat_dst = app_dir / "update.bat"
    shutil.copy2(bat_src, bat_dst)

    logging.debug(f"bat_file: {bat_dst}")
    logging.warning("Starter update.bat som sluttfører oppdateringen.")

    log_file = ctx.log_config.get("file", "BrikkesysTillegg.log")
    logging.debug(f"log_file: {log_file}")

    subprocess.Popen(
      f'start "" "{bat_dst}"',
        cwd=str(app_dir),
        shell=True
    )

    time.sleep(0.2)
