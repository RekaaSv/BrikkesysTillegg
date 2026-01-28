import logging
import os
import shutil
import sys
import time
import zipfile
import tempfile
import requests
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import QMessageBox


def download_and_start_update(download_url):
    # Last ned ZIP til temp-mappe
    temp_dir = Path(tempfile.mkdtemp())
    zip_path = temp_dir / "update.zip"

    logging.info("Laster ned oppdatering...")

    response = requests.get(download_url, stream=True)
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logging.info("Lastet ned ZIP.")

    # Pakk ut ZIP
    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir()

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    logging.info("ZIP pakket ut.")

    app_dir = get_app_dir()

    logging.debug("App dir: %s", app_dir)
    logging.debug("extract_dir: %s", extract_dir)
    logging.debug("extract_dir content: %s", list(Path(extract_dir).iterdir()))

    ok = copy_to_app_dir(extract_dir, app_dir)

    if ok:
        run_update_bat(app_dir)
    else:
        QMessageBox.warning(
            None,
            "Feil",
            "Klarte ikke å kopiere ny versjon til programkatalogen."
        )


def run_update_bat(app_dir: Path):
    bat_file = app_dir / "update.bat"

    subprocess.Popen(
        ["cmd.exe", "/c", "start", "", str(bat_file)],
        cwd=str(app_dir)
    )
    time.sleep(0.2)

    sys.exit(0)



def copy_to_app_dir(extract_dir: Path, app_dir: Path) -> bool:
    """
    Kopierer ny versjon fra extract_dir inn i app_dir som .exe.new.
    Returnerer True hvis alt gikk bra, False hvis noe feilet.
    """

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


def get_app_dir():
    return Path(sys.executable).parent




def xreplace_exe_with_backup(old_exe: Path, new_exe: Path):
    backup = old_exe.with_suffix(old_exe.suffix + ".bak")

    try:
        # 1. Kopier gammel .exe til .exe.bak som backup.
        if old_exe.exists():
            logging.info("Lager ny backup: %s → %s", old_exe, backup)
            if backup.exists():
                logging.info("Sletter gammel backup før ny lages: %s", backup)
                backup.unlink()

            old_exe.rename(backup)

        # 2. Kopier inn ny EXE
        logging.info("Kopierer inn ny EXE: %s → %s", new_exe, old_exe)
        shutil.copy2(new_exe, old_exe)

        logging.info("Oppdatering vellykket. Backup beholdes: %s", backup)

    except Exception as e:
        logging.error("Feil under oppdatering: %s", e)

        # 3. Rollback hvis noe feiler
        if backup.exists():
            logging.info("Ruller tilbake: %s → %s", backup, old_exe)
            if old_exe.exists():
                old_exe.unlink()
            backup.rename(old_exe)

        raise
