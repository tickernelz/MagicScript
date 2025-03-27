@echo off
echo Building MagicScript executable...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
pip install -r requirements.txt

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Build the executable
echo.
echo Building executable with PyInstaller...

REM Check if icon files exist
if not exist icon.ico (
    echo Warning: icon.ico not found. The executable will use a fallback icon.
)
if not exist icon.png (
    echo Warning: icon.png not found. The executable will use a fallback icon.
)

REM Create spec file with more control over the build
echo Creating PyInstaller spec file...
pyinstaller --onefile --windowed --icon=icon.ico --name=MagicScript --add-data "icon.ico;." --add-data "icon.png;." --specpath . magic_script.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo Build successful! Executable is in the dist folder.
    echo.
    echo You can now run MagicScript.exe from the dist folder.
) else (
    echo Build failed. Check the error messages above.
)

pause