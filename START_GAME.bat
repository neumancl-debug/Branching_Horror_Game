@echo off
cd /d "%~dp0"
python hollow_blackthorn.py
if errorlevel 1 (
 echo.
 echo Could not start. Install Pygame with: python -m pip install pygame
 pause
)
