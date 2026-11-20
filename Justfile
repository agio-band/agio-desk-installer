
# One-time: install and provision the Windows VM in QEMU
# (requires .vm/windows-builder/windows.iso, see scripts/qemu/README.md)
setup-build:
    @bash scripts/qemu/install-windows.sh


build-windows-install:
    @bash scripts/qemu/install-windows.sh


build-windows:
    -rm ./agio_desk_installer/assets/agio-login*
    cp ../bin/agio-login.exe ./agio_desk_installer/assets/
    @bash scripts/qemu/build-windows-qemu.sh
    @bash scripts/qemu/build-windows-qemu.sh --shutdown


build-windows-gui:
    @bash scripts/qemu/build-windows-qemu.sh --boot
    @bash scripts/qemu/build-windows-qemu.sh --shutdown


build-linux:
    -rm ./agio_desk_installer/assets/agio-login*
    cp ../bin/agio-login ./agio_desk_installer/assets/
    @bash scripts/build-linux.sh


run:
    PYTHONPATH={{invocation_directory_native()}} uv run agio_desk_installer/main.py
