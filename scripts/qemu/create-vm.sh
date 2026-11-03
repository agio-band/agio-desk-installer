#!/usr/bin/env bash
# One-time creation of the Windows builder VM.
#
#   bash scripts/qemu/create-vm.sh
#
# What it does:
#   1. checks prerequisites (qemu, kvm, OVMF, swtpm, Windows ISO)
#   2. downloads virtio-win.iso (QEMU device drivers for Windows)
#   3. creates a qcow2 disk and fresh UEFI vars (Secure Boot + TPM 2.0)
#   4. boots the VM with the Windows installer (interactive GUI window)
#
# You then install Windows manually (one time, ~30 min), see README.md.
# The VM stays booted in the foreground; close the window or shut Windows
# down when finished, then run scripts/qemu/guest-setup.ps1 inside the guest.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

echo "=== AGIO Windows builder VM: create ==="
echo "VM dir:     $AGIO_VM_DIR"
echo "Disk:       $AGIO_VM_DISK ($AGIO_VM_DISK_SIZE)"
echo "Windows ISO: $AGIO_WIN_ISO"
echo

# --- prerequisites ---
for bin in "$AGIO_QEMU_BIN" qemu-img swtpm; do
    if ! command -v "$bin" >/dev/null 2>&1; then
        echo "[ERROR] $bin not found. Install: sudo apt install qemu-system-x86 qemu-utils ovmf swtpm swtpm-tools"
        exit 1
    fi
done

if ! ls /dev/kvm >/dev/null 2>&1; then
    echo "[WARN] /dev/kvm not available - the VM will be extremely slow (emulation)."
fi

for f in "$AGIO_OVMF_CODE" "$AGIO_OVMF_VARS_SRC"; do
    if [ ! -f "$f" ]; then
        echo "[ERROR] OVMF firmware not found: $f"
        echo "        Install: sudo apt install ovmf"
        exit 1
    fi
done

if [ ! -f "$AGIO_WIN_ISO" ]; then
    echo "[ERROR] Windows ISO not found: $AGIO_WIN_ISO"
    echo
    echo "Download a Windows 10/11 x64 ISO from Microsoft:"
    echo "  https://www.microsoft.com/software-download/windows11"
    echo "  https://www.microsoft.com/software-download/windows10"
    echo "and save it as:"
    echo "  $AGIO_WIN_ISO"
    echo "or point AGIO_WIN_ISO=/path/to/win.iso to this script."
    exit 1
fi

# --- virtio drivers ---
if [ ! -f "$AGIO_VIRTIO_ISO" ]; then
    echo "--- Downloading virtio-win.iso (QEMU drivers for Windows, ~700 MB) ---"
    mkdir -p "$AGIO_VM_DIR"
    curl -fL --retry 3 -o "$AGIO_VIRTIO.iso.part" "$AGIO_VIRTIO_URL"
    mv "$AGIO_VIRTIO.iso.part" "$AGIO_VIRTIO_ISO"
fi

# --- disk & firmware vars ---
mkdir -p "$AGIO_VM_DIR"

if [ -f "$AGIO_VM_DISK" ]; then
    echo "[WARN] Disk already exists: $AGIO_VM_DISK (skipping creation)"
else
    echo "--- Creating disk ($AGIO_VM_DISK_SIZE, thin provisioned) ---"
    qemu-img create -f qcow2 "$AGIO_VM_DISK" "$AGIO_VM_DISK_SIZE"
fi

if [ ! -f "$AGIO_OVMF_VARS" ]; then
    echo "--- Preparing UEFI vars with Microsoft keys (Secure Boot ready) ---"
    cp "$AGIO_OVMF_VARS_SRC" "$AGIO_OVMF_VARS"
fi

# --- ssh key for later (guest-setup.ps1 installs the pubkey) ---
if [ ! -f "$AGIO_VM_KEY" ]; then
    ssh-keygen -t ed25519 -N "" -C "agio-win-builder" -f "$AGIO_VM_KEY" >/dev/null
    echo "--- Generated SSH key: $AGIO_VM_KEY ---"
fi

# --- display backend ---
DISPLAY_ARGS="-display gtk"
if ! "$AGIO_QEMU_BIN" -display help 2>/dev/null | grep -qE '\bgtk\b'; then
    DISPLAY_ARGS="-vnc 127.0.0.1:1"
    echo "[WARN] GTK display not available; using VNC on 127.0.0.1:5901"
fi

start_swtpm
trap stop_swtpm EXIT

echo
echo "=== Starting Windows installer (interactive) ==="
echo "During setup, when asked for a disk and none is listed:"
echo "  Load driver -> browse virtio-win CD -> viostor\\w11\\amd64 (or w10) -> select"
echo "After install, run virtio-win-guest-tools.exe from the second CD."
echo "Create user:  $AGIO_VM_USER"
echo

# shellcheck disable=SC2086
"$AGIO_QEMU_BIN" $(qemu_base_args) \
    $DISPLAY_ARGS \
    -boot menu=on \
    -drive id=cdwin,if=none,media=cdrom,file="$AGIO_WIN_ISO" \
    -device ide-cd,bus=ide.0,drive=cdwin,bootindex=1 \
    -drive id=cdvirt,if=none,media=cdrom,file="$AGIO_VIRTIO_ISO" \
    -device ide-cd,bus=ide.1,drive=cdvirt,bootindex=2

echo
echo "VM powered off. Next steps (see scripts/qemu/README.md):"
echo "  1. boot the VM:      bash scripts/qemu/build-windows-qemu.sh --boot"
echo "     (it waits for SSH; finish guest setup from README if not done yet)"
echo "  2. or full build:    bash scripts/qemu/build-windows-qemu.sh"
