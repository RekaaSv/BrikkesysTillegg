import sys
import logging
from pathlib import Path
import shutil
import time

def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def show_finished_dialog():
    print()
    print("Oppdateringen er fullført.")
    print("Lukk dette vinduet og start BrikkesysTillegg på nytt.")
    print("Den gamle versjonen ligger igjen som reserve i filen *.exe.bak.")
    print()
    input("Trykk Enter for å lukke...")

def main():
    extract_dir = Path(sys.argv[1])
    app_dir = Path(sys.argv[2])

    log_path = Path(app_dir) / "updater.log"
    setup_logging(log_file=log_path)

    logging.info("Updater startet")

    if len(sys.argv) != 3:
        logging.info("Bruk: updater.py <extract_dir> <app_dir>")
        sys.exit(1)


    exe_name = "brikkesystillegg.exe"  # navnet på din exe

    new_exe = next(extract_dir.rglob("*.exe"))
    old_exe = app_dir / exe_name

    logging.debug("Looking for EXE: %s", new_exe)
    logging.debug("Exists? %s", new_exe.exists())

    # Vent til hovedprogrammet er lukket
    time.sleep(2)

    # Erstatt EXE
    logging.debug("Erstatter gammel EXE...")
    backup = old_exe.with_suffix(".exe.bak")
    if backup.exists():
        backup.unlink()
    old_exe.rename(backup)

    shutil.copy2(new_exe, old_exe)

    logging.info("Updater ferdig")

    show_finished_dialog()
    sys.exit(0)

"""
    # Start programmet på nytt
    time.sleep(10)

    new_exe = app_dir / "brikkesystillegg.exe"
    DETACHED_PROCESS = 0x00000008
    CREATE_BREAKAWAY_FROM_JOB = 0x01000000
    flags = DETACHED_PROCESS | CREATE_BREAKAWAY_FROM_JOB
    subprocess.Popen(
        [str(new_exe)],
        creationflags=flags,
        close_fds=True
    )

"""

if __name__ == "__main__":
    main()