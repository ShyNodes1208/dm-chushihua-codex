@echo off
setlocal
cd /d "%~dp0"
echo Starting DM Query Dashboard desktop mode...
python desktop_app.py
echo.
echo Desktop app stopped. Press any key to close this window.
pause >nul
