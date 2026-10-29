@echo off
cd /d "%~dp0"
rem Prefer the project's isolated environment when one has been created.
set "GAME_PYTHON=python"
if exist "%~dp0.venv\Scripts\python.exe" set "GAME_PYTHON=%~dp0.venv\Scripts\python.exe"
"%GAME_PYTHON%" -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo Python 3 and Pygame are required.
    echo Install Python, then run: python -m pip install -r requirements.txt
    pause
    exit /b 1
)
"%GAME_PYTHON%" main.py
if errorlevel 1 pause
