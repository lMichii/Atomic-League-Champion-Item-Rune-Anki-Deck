@echo off
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  echo Python Launcher "py" nicht gefunden. Bitte Python 3.10+ installieren.
  pause
  exit /b 1
)
echo League of Legends Anki Medien-Fetcher
py media_fetcher.py --champions Ahri,Ezreal,Blitzcrank,Nautilus,Thresh,Locke --patch 16.21.1
if errorlevel 1 (
  echo Ein Problem ist aufgetreten. Lies die Ausgabe oben.
) else (
  echo Ergebnis: output\manifest.csv und output\media\
  echo Du kannst manifest.csv und deine Excel-Datei in ChatGPT hochladen.
)
pause
