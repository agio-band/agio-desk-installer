@echo off

:: encoding
set NUITKA_COMPILED_FILE_NAME_C_ENCODING=utf-8
set PYTHONUTF8=1
set LANG=en_US.UTF-8
set LC_ALL=en_US.UTF-8
:: set cache paths
set TEMP=C:\Temp
set TMP=C:\Temp
set NUITKA_CACHE_DIR=C:\Temp\NuitkaCache
set UV_CACHE_DIR=C:\Temp\UvCache
set UV_PYTHON_INSTALL_DIR=C:\Temp\uv
:: create temp user
set TEMPUSER=C:\Temp\tempuser
set HOME=%TEMPUSER%
set USERPROFILE=%TEMPUSER%
set APPDATA=%TEMPUSER%
set LOCALAPPDATA=%TEMPUSER%
if not exist "%TEMPUSER%" (
    mkdir "%TEMPUSER%"
)

:: check and copy uv.exe
set "TARGET_DIR=%SCRIPT_DIR%agio_desk_installer\assets"
set "TARGET_FILE=%TARGET_DIR%\uv.exe"
for /f "delims=" %%i in ('where uv.exe 2^>nul') do (
    if not defined GLOBAL_UV_PATH set "GLOBAL_UV_PATH=%%i"
)
if defined GLOBAL_UV_PATH (
    echo uv.exe: "%GLOBAL_UV_PATH%"
    if not exist "%TARGET_DIR%" (
        mkdir "%TARGET_DIR%"
    )
    copy "%GLOBAL_UV_PATH%" "%TARGET_FILE%" >nul
    if exist "%TARGET_FILE%" (
        echo "uv copied: %TARGET_FILE%"
        goto :uvok
    ) else (
        exit /b 1
    )
) else (
    echo.
    echo [ERROR] uv.exe not found in PATH.
    exit /b 1
)
:uvok


uv venv --clear
uv sync

call "%~dp0.venv\Scripts\activate.bat"

where python

set ROOT=%~dp0
set PYTHONPATH=%ROOT%

if "%~1"=="" (
    set OUTPUT_DIR=%ROOT%dest
) else (
    set OUTPUT_DIR=%~1
)

if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

uv run --active python -m nuitka ^
  --onefile ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --follow-imports ^
  --assume-yes-for-downloads ^
  --include-package=agio ^
  --include-package=agio.tools ^
  --include-qt-plugins=platforms ^
  --output-dir="%OUTPUT_DIR%" ^
  --remove-output ^
  --output-filename=agio_desk_installer.exe ^
  --windows-icon-from-ico=agio_desk_installer/assets/icons/icon.ico ^
  --include-data-dir=agio_desk_installer/assets=assets agio_desk_installer/main.py

rem --show-scons --verbose ^


if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FATAL: Nuitka build failed!
    pause
) else (
    echo.
    echo Nuitka build completed successfully!
)