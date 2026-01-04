@echo off
REM Build script for creating Windows executable

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Build the application
pyinstaller --name="PasswordVault" ^
    --windowed ^
    --onefile ^
    --add-data "icons;icons" ^
    --add-data "View/*.ui;View" ^
    Main.py

echo Build complete! Executable is in dist\PasswordVault.exe
pause
