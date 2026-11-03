@echo off
setlocal

:: Standalone Windows build script.
:: Runs on native Windows (dev machine or VM), from any directory:
::   scripts\build-windows.cmd [output-dir]
::
:: Requires in PATH: uv.exe (winget install astral-sh.uv), git (for agio-core dependency).
:: Nuitka downloads its own C compiler (gcc/winlibs) if MSVC is not installed
:: (--assume-yes-for-downloads).

:: UTF-8 everywhere (source files, console, Nuitka output)
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "NUITKA_COMPILED_FILE_NAME_C_ENCODING=utf-8"

:: project root = parent dir of this script
pushd "%~dp0.."
set "ROOT=%CD%"
popd
cd /d "%ROOT%"

set "PYTHONPATH=%ROOT%"

if "%~1"=="" (
    set "OUTPUT_DIR=%ROOT%\dist"
) else (
    set "OUTPUT_DIR=%~1"
)

:: --- bundle uv.exe into assets (installer ships it to target machines) ---
where uv.exe >nul 2>nul
if errorlevel 1 (
    echo [ERROR] uv.exe not found in PATH. Install: winget install astral-sh.uv
    exit /b 1
)
set "UV_EXE="
for /f "delims=" %%i in ('where uv.exe') do if not defined UV_EXE set "UV_EXE=%%i"
echo uv.exe: "%UV_EXE%"
if not exist "agio_desk_installer\assets" mkdir "agio_desk_installer\assets"
copy /y "%UV_EXE%" "agio_desk_installer\assets\uv.exe" >nul

:: --- venv & dependencies ---
echo === uv venv --clear / uv sync ===
uv venv --clear
if errorlevel 1 exit /b 1
uv sync
if errorlevel 1 exit /b 1
uv pip install pywin32
if errorlevel 1 exit /b 1

set "PY=%ROOT%\.venv\Scripts\python.exe"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo === nuitka ===
"%PY%" -m nuitka ^
  --onefile ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --follow-imports ^
  --assume-yes-for-downloads ^
  --include-package=agio ^
  --include-package=win32com ^
  --include-qt-plugins=platforms ^
  --output-dir="%OUTPUT_DIR%" ^
  --remove-output ^
  --output-filename=agio_desk_installer.exe ^
  --windows-icon-from-ico=agio_desk_installer/assets/icons/icon.ico ^
  --include-data-dir=agio_desk_installer/assets=assets ^
  --include-data-files=agio_desk_installer/assets/uv.exe=assets/ ^
  agio_desk_installer/main.py
if errorlevel 1 (
    echo.
    echo FATAL: Nuitka build failed!
    exit /b 1
)

echo.
echo Nuitka build completed successfully!
echo Output: %OUTPUT_DIR%\agio_desk_installer.exe
endlocal
