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

from weasyprint import HTML, CSS
import os

def lag_pdf(html_streng, filnavn, mappe=None):
    # Finn mappe å lagre i
    if mappe is None:
        mappe = os.getcwd()

    sti = os.path.join(mappe, filnavn)

    # Enkel standard-CSS for trygg fontbruk på Windows
    css = CSS(string="""
        @font-face {
            font-family: Arial;
            src: local("Arial");
        }
        body {
            font-family: Arial;
            font-size: 12pt;
        }
    """)

    # Generer PDF
    HTML(string=html_streng).write_pdf(sti, stylesheets=[css])

    return sti