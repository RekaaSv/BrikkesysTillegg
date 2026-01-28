@echo off
pause
echo Oppdatering av BrikkesysTillegg...

REM Vent litt for å sikre at EXE-en er lukket
timeout /t 2 >nul

pause
REM Sikkerhetskopier gammel versjon
del brikkesystillegg.exe.bak
rename brikkesystillegg.exe brikkesystillegg.exe.bak

REM Bytt inn ny versjon
rename brikkesystillegg.exe.new brikkesystillegg.exe

echo Oppdateringen er fullført.
pause