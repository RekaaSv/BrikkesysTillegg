README_build.txt
================

Bygge og pakke BrikkesysTillegg med PyInstaller
---------------------------------------------

Fjerne forrige bygg:
rm -r build
rm -r dist
rm brikkesystillegg.spec


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


Bygger man i CMD så brukes ^ i stedet for `.


Installasjonen bygger en spec fil i rotkatalogen.
Etter at .spec-filene er generert, kan du bygge med den:

.\.venv\Scripts\pyinstaller.exe brikkesystillegg.spec

eller
.\.venv\Scripts\pyinstaller.exe --clean brikkesystillegg.spec


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
- brikkesystillegg.cfg (kopier 'brikkesystillegg - dist.cfg' fra rotkatalogen. Rename til brikkesystillegg.cfg.
- README.pdf (kopier fra /docs)

Ny release:
===========

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




Sist oppdatert: 05.06.2026