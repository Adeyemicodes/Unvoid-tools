@echo off
REM ============================================================================
REM Patient Unvoid Tool - Windows Build Script
REM ============================================================================
REM This script builds a standalone Windows executable (.exe)
REM ============================================================================

echo.
echo ============================================================================
echo Patient Unvoid Tool - Windows Build
echo ============================================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller not found!
    echo.
    echo Installing PyInstaller...
    pip install --user pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        echo Trying with administrator privileges...
        powershell -Command "Start-Process pip -ArgumentList 'install pyinstaller' -Verb RunAs"
        pause
        exit /b 1
    )
)

REM Check if mysql-connector-python is installed
python -c "import mysql.connector" 2>nul
if errorlevel 1 (
    echo [ERROR] mysql-connector-python not found!
    echo.
    echo Installing mysql-connector-python...
    pip install --user mysql-connector-python
    if errorlevel 1 (
        echo [ERROR] Failed to install mysql-connector-python
        pause
        exit /b 1
    )
)

echo.
echo [1/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist patient_unvoid_tool.spec del /q patient_unvoid_tool.spec

echo [2/4] Building executable...
python -m PyInstaller --onefile ^
    --windowed ^
    --name="PatientUnvoidTool" ^
    --icon=NONE ^
    --add-data="unvoid_config.ini;." ^
    patient_unvoid_tool.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo If you see permission errors, try running this script as Administrator:
    echo Right-click build_windows.bat and select "Run as administrator"
    pause
    exit /b 1
)

echo [3/4] Copying config file...
copy unvoid_config.ini dist\unvoid_config.ini

echo [4/4] Creating package folder...
if not exist "PatientUnvoidTool_Windows" mkdir PatientUnvoidTool_Windows
copy dist\PatientUnvoidTool.exe PatientUnvoidTool_Windows\
copy unvoid_config.ini PatientUnvoidTool_Windows\
copy PATIENT_UNVOID_GUIDE.md PatientUnvoidTool_Windows\README.md

echo.
echo ============================================================================
echo BUILD COMPLETE!
echo ============================================================================
echo.
echo Executable location: PatientUnvoidTool_Windows\PatientUnvoidTool.exe
echo Config file:          PatientUnvoidTool_Windows\unvoid_config.ini
echo User guide:           PatientUnvoidTool_Windows\README.md
echo.
echo IMPORTANT: Edit unvoid_config.ini with your database credentials before running!
echo.
echo ============================================================================
pause
