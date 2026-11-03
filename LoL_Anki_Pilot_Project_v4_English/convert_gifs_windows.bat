@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 prepare_gifs.py
) else (
  python prepare_gifs.py
)
if errorlevel 1 (
 echo GIF-Konvertierung fehlgeschlagen. FFmpeg und Dateipfade pruefen.
)
pause
