@echo off
setlocal EnableExtensions
title AURA E-Commerce - Starting
cd /d "%~dp0"

set PYTHONHOME=
set PYTHONPATH=

echo.
echo ==========================================
echo       AURA E-COMMERCE STORE
echo ==========================================
echo.

set "PYEXE="
where py >nul 2>&1
if not errorlevel 1 set "PYEXE=py"
if not defined PYEXE (
    where python >nul 2>&1
    if not errorlevel 1 set "PYEXE=python"
)

if not defined PYEXE (
    echo ERROR: Python was not found.
    echo Install Python 3.10+ and run this file again.
    pause
    exit /b 1
)

%PYEXE% --version
if errorlevel 1 (
    echo ERROR: Your Python installation could not start.
    pause
    exit /b 1
)

if exist "venv\Scripts\python.exe" goto HAVE_VENV

echo.
echo [1/5] Creating Python environment...
%PYEXE% -m venv venv
if errorlevel 1 (
    echo.
    echo ERROR: Could not create the Python environment.
    echo If Windows Python is damaged, repair Python and retry.
    pause
    exit /b 1
)

:HAVE_VENV
echo [2/5] Installing only the packages AURA actually needs (Django + Pillow)...
"venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed.
    pause
    exit /b 1
)

echo [3/5] Preparing database...
"venv\Scripts\python.exe" manage.py migrate
if errorlevel 1 (
    echo.
    echo ERROR: Django migration failed.
    pause
    exit /b 1
)

echo [4/5] Loading the existing AURA catalog...
set "ADMIN_USERNAME=admin"
set "ADMIN_EMAIL=admin@aura.local"
set "ADMIN_PASSWORD=Admin@12345"
"venv\Scripts\python.exe" seed_data.py
if errorlevel 1 (
    echo.
    echo WARNING: Catalog seeding did not complete.
    echo The server will still be started.
)

echo [5/5] Starting AURA...
start "AURA Django Server" /B "venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000

timeout /t 3 /nobreak >nul

where msedge >nul 2>&1
if not errorlevel 1 (
    start "" msedge "http://127.0.0.1:8000/"
) else (
    start "" "http://127.0.0.1:8000/"
)

echo.
echo AURA is running at:
echo http://127.0.0.1:8000/
echo.
echo Keep this window open while using the website.
echo Close it to stop the server.
echo.
pause
