import os
from pathlib import Path
import sys


# Roten til prosjektet (mappen der main.py ligger)
ROOT = Path(__file__).resolve().parent.parent


def resource_path(relative_path: str) -> str:
    """
    Finner riktig bane til ressursen, uansett om programmet kjøres fra .py eller .exe.
    """
    base_path = getattr(sys, '_MEIPASS', ROOT)
    return os.path.join(base_path, relative_path)


def module_path(*parts) -> Path:
    """
    Gir en trygg måte å bygge paths til moduler.
    Eksempel: module_path("fakturagrunnlag", "html_report", "templates")
    """
    return ROOT.joinpath(*parts)