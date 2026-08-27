README_build.txt
================

Bygge og pakke BrikkesysTillegg med PyInstaller
---------------------------------------------

Hvis det skal bygges fra bunnen av (ikke bruke .spec filen):
Fjerne forrige bygg:
1) Slett build
2) Slett dist/brikkesystillegg.exe
3) Slett brikkesystillegg.spec
4) Slett alle __pycache__ mapper. Gjøres enklest i terminal med denne:
	Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force


Bygg med PyInstaller i terminal.

.\.venv\Scripts\pyinstaller.exe `
  --clean `
  --onefile `
  --noconsole `
  --name brikkesystillegg `
  --icon=brikkesystillegg.ico `
  --add-data "brikkesystillegg.ico;." `
  --add-data "hjelp.pdf;." `
  --add-data "hjelp_trekkeplan.pdf;." `
  --add-data "hjelp_direkteresultater.pdf;." `
  --add-data "hjelp_fakturagrunnlag.pdf;." `
  --add-data "update.bat;." `
  main.py


PS: Bygger man i CMD så brukes ^ i stedet for `.
bruker ikke det!


Installasjonen bygger en spec fil i rotkatalogen.
Etter at .spec-filene er generert, kan du bygge med den:

.\.venv\Scripts\pyinstaller.exe brikkesystillegg.spec

eller
.\.venv\Scripts\pyinstaller.exe --clean brikkesystillegg.spec


Hvis filstrukturen endrer seg, eller nye ressurs-filer, så må *.spec regenereres.
Det gjøres ved å slette *.spec og bygge med den første metoden
(som også lager ny *.spec fil).

Pakke sammen zip-fil for nedlasting fra GitHub
----------------------------------------------
Samle filene som skal zip'es sammen i folderen dist:
- brikkesystillegg.exe (plassert hit under bygging)
- brikkesystillegg.cfg (kopier 'brikkesystillegg - dist.cfg' fra rotkatalogen. Rename til brikkesystillegg.cfg.
- README.pdf (kopier fra /docs)

Ny release:
===========

Oppdater i CHANGELOG.md
Oppdater versjonsnr i app/__init__.py

COMMIT og PUSH.

Bygg ny exe.

I DIST: pakk samme de 3 filene til:
brikkesystillegg.zip

Laste ZIP-fil opp til ny release på GitHub.
-------------------------------------------
0. Logg på til GitHub.com

1. Gå til repoet ditt:
	https://github.com/RekaaSv/BrikkesysTillegg
2. Klikk på Releases (til høyre, under "About").
3. Klikk: Draft a new release.
4. Fyll inn:
  * Tag version: f.eks. v1.4.0
  * Release title: f.eks. BrikkesysTillegg v1.4.0
  * Description: hva som er nytt
5. Dra brikkesys.zip inn i "Attach binaries"‑feltet.
6. Klikk Publish release.


GitHub
======
Ny versjon:
git tag v1.1.3
git push --tags




Biblioteker i bruk
==================
Installeres med: pip install:
requests
pymysql
reportlab
python-docx
openpyxl


Sist oppdatert: 28.08.2026
