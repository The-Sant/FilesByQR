@echo off
cd /d "%~dp0"

echo ------------------------------
echo 🔄 Cleaning previous builds...
echo ------------------------------

REM Delete previous build folders and spec file
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q dist_installer
del /q FilesByQR.spec

echo ------------------------------
echo 🚧 Building FilesByQR.exe...
echo ------------------------------

pyinstaller --noconsole --onedir --icon=assets\app_icon.ico ^
--add-data "templates;templates" ^
--add-data "static;static" ^
--add-data "assets;assets" ^
main.py -n FilesByQR

echo.
echo ✅ Build complete. Press any key to exit.
pause > nul
