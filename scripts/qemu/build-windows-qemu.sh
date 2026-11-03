#!/usr/bin/env bash
# Build the Windows installer inside the QEMU Windows VM, from the Linux host.
#
#   bash scripts/qemu/build-windows-qemu.sh [--shutdown] [output-dir]
#   bash scripts/qemu/build-windows-qemu.sh --boot        # boot with GUI window
#   bash scripts/qemu/build-windows-qemu.sh --shutdown    # just shut the VM down
#
# One-time preparation (see README.md): create-vm.sh + Windows install +
# guest-setup.ps1 inside the guest.
#
# Build flow: boot VM headless if needed -> sync sources over SSH ->
# run scripts/build-windows.cmd inside the guest -> fetch the .exe back.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

BOOT_ONLY=0
SHUTDOWN=0
POSITIONAL_SEEN=0
OUTPUT_DIR="$AGIO_ROOT/dist"

for arg in "$@"; do
    case "$arg" in
        --boot)    BOOT_ONLY=1 ;;
        --shutdown) SHUTDOWN=1 ;;
        -*) echo "[ERROR] unknown option: $arg"; exit 1 ;;
        *)  OUTPUT_DIR="$arg"; POSITIONAL_SEEN=1 ;;
    esac
done

if [ ! -f "$AGIO_VM_DISK" ]; then
    echo "[ERROR] VM disk not found: $AGIO_VM_DISK"
    echo "        Create the VM first: bash scripts/qemu/create-vm.sh"
    exit 1
fi
if [ ! -f "$AGIO_OVMF_VARS" ]; then
    echo "[ERROR] UEFI vars not found: $AGIO_OVMF_VARS"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

ensure_vm_running() {
    if vm_ssh_reachable; then
        echo "--- VM already running ---"
        return 0
    fi
    if ! vm_is_running; then
        echo "--- Starting VM (headless) ---"
        start_vm_headless
    fi
    wait_for_ssh || {
        echo "[ERROR] Guest did not answer on SSH within timeout."
        echo "        Boot it with GUI to check: bash $0 --boot"
        echo "        If SSH is not set up yet, run scripts/qemu/guest-setup.ps1 in the guest."
        exit 1
    }
}

# ---------- boot-only mode: GUI window, foreground ----------
if [ "$BOOT_ONLY" -eq 1 ]; then
    start_swtpm
    trap stop_swtpm EXIT
    echo "--- Starting VM with GUI (Ctrl+C or guest shutdown to exit) ---"
    # shellcheck disable=SC2086
    "$AGIO_QEMU_BIN" $(qemu_base_args) -display gtk
    exit 0
fi

# ---------- shutdown-only mode ----------
if [ "$SHUTDOWN" -eq 1 ] && [ "$POSITIONAL_SEEN" -eq 0 ]; then
    shutdown_vm
    exit 0
fi
# (--shutdown together with a build falls through: build first, then stop)

ensure_vm_running

# ---------- sync sources to the guest ----------
# NOTE: keep every remote command BARE. A nested `cmd /d /c "a & b & tar -"`
# silently feeds tar an empty stdin on Windows sshd - hence separate calls.
sync_sources() {
    ssh_vm 'if exist agio-src\agio_desk_installer rmdir /s /q agio-src\agio_desk_installer' || true
    ssh_vm 'if not exist agio-src mkdir agio-src'
    tar -czf - -C "$AGIO_ROOT" \
        --exclude=./.git --exclude=./.venv --exclude=./dist --exclude=./_tmp \
        --exclude=./.vm --exclude=./.idea --exclude=./.ruff_cache \
        --exclude=./agio_desk_installer/assets/uv \
        --exclude=__pycache__ --exclude='*.pyc' \
        . | ssh_vm 'tar -xzf - -C agio-src'
}

sync_ok=false
for attempt in 1 2 3; do
    echo "--- Syncing sources to guest (attempt $attempt) ---"
    sync_sources
    if ssh_vm 'if not exist agio-src\scripts\build-windows.cmd exit 1' >/dev/null 2>&1; then
        sync_ok=true
        break
    fi
    echo "[WARN] sync verification failed - retrying"
    sleep 3
done
if [ "$sync_ok" != true ]; then
    echo "[ERROR] sources did not reach the guest after 3 attempts."
    exit 1
fi

# ---------- run the build inside the guest ----------
GUEST_DIR="$(guest_project_dir)"
GUEST_DIR_POSIX="$(guest_project_dir_posix)"
echo
echo "=== Building inside the Windows VM ($GUEST_DIR) ==="
ssh_vm "$GUEST_DIR\\scripts\\build-windows.cmd"

# ---------- fetch the artifact ----------
echo
echo "--- Fetching artifact ---"
scp_from_vm "$GUEST_DIR_POSIX/dist/agio_desk_installer.exe" "$OUTPUT_DIR/"

echo
echo "=== Windows build OK: $OUTPUT_DIR/agio_desk_installer.exe ==="

if [ "$SHUTDOWN" -eq 1 ]; then
    shutdown_vm
fi
