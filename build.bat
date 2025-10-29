@echo off

set ROOT=%~dp0

set PYTHONPATH=%ROOT%

uv run --active python -m nuitka ^
  --onefile ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --follow-imports ^
  --include-package=agio_desk_installer ^
  --include-qt-plugins=platforms ^
  --include-module=click ^
  --output-dir=. ^
  --remove-output ^
  --output-filename=agio_desk_installer_ui.exe ^
  --windows-icon-from-ico=agio_desk_installer/assets/icons/icon.ico ^
  --include-data-dir=agio_desk_installer/assets=assets agio_desk_installer/main.py

pause
