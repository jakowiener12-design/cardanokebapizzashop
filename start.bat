@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo ===================================================
echo   Cardano Kebapizza - Backend wird gestartet
echo ===================================================
echo.

REM --- Echtes Python suchen (Version muss wirklich antworten) ---
set "PYCMD="
py -3 --version >nul 2>nul && set "PYCMD=py -3"
if not defined PYCMD (
  python --version >nul 2>nul && set "PYCMD=python"
)

if not defined PYCMD (
  echo Python ist noch nicht installiert.
  echo.
  echo SO GEHT ES:
  echo   1^) Seite oeffnen:  https://www.python.org/downloads/
  echo   2^) grossen Button "Download Python" anklicken
  echo   3^) Installer starten und UNTEN das Haekchen
  echo      "Add python.exe to PATH" setzen
  echo   4^) "Install Now" anklicken
  echo   5^) danach diese Datei start.bat erneut doppelklicken
  echo.
  echo Hinweis: Wenn beim Tippen von "python" der Microsoft Store aufgeht,
  echo ist nur ein Windows-Platzhalter aktiv - bitte wie oben echtes Python
  echo installieren.
  echo.
  pause
  exit /b 1
)
echo Python gefunden: %PYCMD%

REM --- Virtuelle Umgebung (einmalig) ---
if not exist "venv\Scripts\python.exe" (
  echo Erstelle virtuelle Umgebung...
  %PYCMD% -m venv venv
)
if not exist "venv\Scripts\python.exe" (
  echo.
  echo FEHLER: Die Umgebung konnte nicht angelegt werden.
  echo Das passiert, wenn nur der Windows-Platzhalter statt echtem Python
  echo installiert ist. Bitte Python von https://www.python.org/downloads/
  echo installieren ^(mit Haekchen "Add python.exe to PATH"^) und start.bat
  echo erneut doppelklicken.
  echo.
  pause
  exit /b 1
)

REM --- Einrichtung + Start ---
call "venv\Scripts\activate.bat"
echo Installiere Pakete... ^(dauert beim ersten Mal etwas^)
python -m pip install -q -r requirements.txt
if errorlevel 1 ( echo FEHLER bei der Installation der Pakete. & pause & exit /b 1 )
python manage.py migrate
python manage.py seed_menu
python manage.py init_admin
python manage.py init_info

echo.
echo ===================================================
echo   Shop:        http://127.0.0.1:8000/
echo   Admin-Panel: http://127.0.0.1:8000/admin/
echo   Login:       admin / CardanoAdmin#2026
echo ===================================================
echo   (Zum Beenden dieses Fenster schliessen)
echo.
python manage.py runserver
echo.
echo Der Server wurde beendet.
pause
