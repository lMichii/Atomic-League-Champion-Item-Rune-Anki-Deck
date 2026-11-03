@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 build_deck.py
) else (
  python build_deck.py
)
if errorlevel 1 (
  echo.
  echo Export fehlgeschlagen. Bitte Ausgabe pruefen.
)
pause
