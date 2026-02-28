@echo off
REM Build script for MP3 Metadata Editor
REM This script creates a standalone .exe file

echo ========================================
echo MP3 Metadata Editor - Build Script
echo ========================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Check if required packages are installed
echo Checking dependencies...
pip install -r requirements.txt

echo.
echo Building executable...
REM Build the executable
echo.
echo Building executable...

REM Use icon only if present to avoid PyInstaller error
if exist app.ico (
    pyinstaller --onefile --windowed --icon=app.ico --name="MP3 Metadata Editor" mp3_metadata_editor.py
) else (
    echo app.ico not found — building without custom icon
    pyinstaller --onefile --windowed --name="MP3 Metadata Editor" mp3_metadata_editor.py
)

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Build successful!
    echo ========================================
    echo.
    echo Executable created at: dist\MP3 Metadata Editor.exe
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    pause
    exit /b 1
)
