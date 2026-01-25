@echo off
echo Sletter alle __pycache__-mapper...
rmdir /s /q build
for /d /r %%i in (__pycache__) do @rmdir /s /q "%%i"
echo Ferdig.
pause
