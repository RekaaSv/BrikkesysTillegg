@echo off
set LOGFILE=%1

echo %date% %time% [UPDATE.BAT] Oppdatering starter >> "%LOGFILE%"
echo %date% %time% Oppdatering starter

REM echo Innhold i %cd%:
REM dir

REM 1: Slett gammel .bak
echo %date% %time% [UPDATE.BAT] Sletter gammel .bak hvis den finnes >> "%LOGFILE%"

:delete_bak
if exist "brikkesystillegg.exe.bak" (
    del /f /q "brikkesystillegg.exe.bak"
    if exist "brikkesystillegg.exe.bak" (
        timeout /t 1 >nul
        goto delete_bak
    )
)

REM 2: Vent til EXE er frigitt
echo %date% %time% [UPDATE.BAT] Gammel exe til exe.bak >> "%LOGFILE%"

:wait_exe
rename "brikkesystillegg.exe" "brikkesystillegg.exe.bak"
if errorlevel 1 (
    timeout /t 1 >nul
    goto wait_exe
)

REM 3: Bytt inn ny EXE
echo %date% %time% [UPDATE.BAT] Bytt inn ny EXE >> "%LOGFILE%"
rename "brikkesystillegg.exe.new" "brikkesystillegg.exe"

echo %date% %time% [UPDATE.BAT] Oppdatering fullført! >> "%LOGFILE%"
exit