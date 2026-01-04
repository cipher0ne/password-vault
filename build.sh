#!/bin/bash
# Build script for creating distributable executables

# Activate virtual environment
source .venv/bin/activate

# Build the application
pyinstaller --name="PasswordVault" \
    --windowed \
    --onefile \
    --add-data "icons:icons" \
    --add-data "View/*.ui:View" \
    --icon="icons/app_icon.png" \
    Main.py

echo "Build complete! Executable is in dist/PasswordVault"
