README_build.txt
================

Bygge og pakke Trekkeplan GUI med PyInstaller
---------------------------------------------

Start. Søk. Anaconda -> Anaconda prompt.
Bygg med PyInstaller her.

Aktiver miljøet weasy2: conda activate weasy2
Installer PyInstaller:
(weasy2) C:\Users\svein>pip show pyinstaller
(weasy2) C:\Users\svein>pip install pyinstaller

CD til:
(weasy2) C:\Users\svein\OneDrive\Dokumenter\PycharmProjects\BrikkesysTillegg>


pyinstaller ^
  --onefile ^
  --noconsole ^
  --name brikkesystillegg ^
  --icon=reshot-icon-running-JUSXPBMDTN.ico ^
  --add-data "reshot-icon-running-JUSXPBMDTN.ico;." ^
  --add-data "hjelp.pdf;." ^
  --add-data "hjelp_trekkeplan.pdf;." ^
  --add-data "hjelp_direkteresultater.pdf;." ^
  --add-data "hjelp_fakturagrunnlag.pdf;." ^
  main.py


Installasjonen bygger en spec fil i rotkatalogen.
Etter at .spec-filene er generert, kan du bygge med den:

pyinstaller brikkesystillegg.spec

Opprydding etter bygging
-------------------------
Du kan slette midlertidige filer:
- build/
- __pycache__/

Hvis filstrukturen endrer seg, eller nye ressurs-filer, så må *.spec regenereres.
Det gjøres ved å slette *.spec og byge med den første metoden
(som også lager ny *.spec fil).

Pakke sammen zip-fil for nedlasting fra GitHub
----------------------------------------------
Samle filene som skal zip'es sammen i folderen dist:
- brikkesystillegg.exe (plassert hit under bygging)
- brikkesystillegg.cfg (kopier fra rotkatalogen, men endre password til <passord>
- README.pdf (kopier fra /docs)

Pakk samme de 3 filene til:
brikkesystillegg.zip

Laste ZIP-fil opp til ny release på GitHub.
-------------------------------------------


Sist oppdatert: 25.01.2026