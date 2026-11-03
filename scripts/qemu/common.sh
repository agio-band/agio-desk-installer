#!/usr/bin/env bash
# Shared configuration for the QEMU Windows builder VM.
# Every value can be overridden via environment variable of the same name.

# Project root (agio-desk-installer), i.e. parent of scripts/qemu
AGIO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# VM files live outside git (added to .gitignore)
AGIO_VM_DIR="${AGIO_VM_DIR:-$AGIO_ROOT/.vm/windows-builder}"
AGIO_VM_DISK="$AGIO_VM_DIR/disk.qcow2"
AGIO_VM_DISK_SIZE="${AGIO_VM_DISK_SIZE:-96G}"

# Windows install ISO - must be provided by the user (see README.md)
AGIO_WIN_ISO="${AGIO_WIN_ISO:-$AGIO_VM_DIR/windows.iso}"
# VirtIO drivers ISO for QEMU devices (auto-downloaded by create-vm.sh)
AGIO_VIRTIO_ISO="${AGIO_VIRTIO_ISO:-$AGIO_VM_DIR/virtio-win.iso}"
AGIO_VIRTIO_URL="https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso"

# QEMU resources
AGIO_VM_CPUS="${AGIO_VM_CPUS:-8}"
AGIO_VM_RAM="${AGIO_VM_RAM:-8G}"

# SSH access: user-mode networking, forwarded to localhost only.
# Default matches the schneegans autounattend (user "Admin"); our fallback
# template flow uses "builder" and overrides this accordingly.
AGIO_VM_SSH_PORT="${AGIO_VM_SSH_PORT:-2222}"
AGIO_VM_USER="${AGIO_VM_USER:-Admin}"
# Project location inside the guest (cmd.exe / posix variants)
AGIO_GUEST_DIR="C:\\Users\\$AGIO_VM_USER\\agio-src"
AGIO_GUEST_DIR_POSIX="C:/Users/$AGIO_VM_USER/agio-src"

# Dedicated SSH key for this VM (generated on first use)
AGIO_VM_KEY="$AGIO_VM_DIR/id_ed25519"
AGIO_VM_PUBKEY="$AGIO_VM_DIR/id_ed25519.pub"

# UEFI firmware (Win11 needs TPM 2.0 + Secure Boot capable UEFI)
AGIO_OVMF_CODE="${AGIO_OVMF_CODE:-/usr/share/OVMF/OVMF_CODE_4M.secboot.fd}"
AGIO_OVMF_VARS_SRC="/usr/share/OVMF/OVMF_VARS_4M.ms.fd"
AGIO_OVMF_VARS="$AGIO_VM_DIR/OVMF_VARS.fd"

# TPM emulator socket/state
AGIO_TPM_DIR="$AGIO_VM_DIR/tpm"
AGIO_TPM_SOCK="$AGIO_TPM_DIR/swtpm.sock"

# how long to wait for the guest to boot and answer SSH, seconds
AGIO_VM_BOOT_TIMEOUT="${AGIO_VM_BOOT_TIMEOUT:-600}"
# password of the local "builder" account inside the guest (VM is reachable
# from localhost only; SSH uses key auth anyway - this is for console login)
AGIO_VM_PASSWORD="${AGIO_VM_PASSWORD:-agio-builder}"

AGIO_QEMU_BIN="${AGIO_QEMU_BIN:-qemu-system-x86_64}"

SSH_OPTS=(
    -i "$AGIO_VM_KEY"
    -o UserKnownHostsFile=/dev/null
    -o StrictHostKeyChecking=no
    -o LogLevel=ERROR
    -o BatchMode=yes
)

ssh_vm() {
    ssh "${SSH_OPTS[@]}" -p "$AGIO_VM_SSH_PORT" \
        "$AGIO_VM_USER@127.0.0.1" "$@"
}

scp_from_vm() {
    # scp_from_vm <guest-path> <local-path>
    scp "${SSH_OPTS[@]}" -P "$AGIO_VM_SSH_PORT" \
        "$AGIO_VM_USER@127.0.0.1:$1" "$2"
}

vm_ssh_reachable() {
    ssh_vm 'echo ok' >/dev/null 2>&1
}

# Project dir inside the guest, based on the SSH user's real profile
# (Windows may create suffixed profiles like C:\Users\admin.BUILDER).
guest_project_dir() {
    ssh_vm 'echo %USERPROFILE%' 2>/dev/null | tr -d '\r' | sed 's|$|\\agio-src|'
}

guest_project_dir_posix() {
    guest_project_dir | tr '\\' '/'
}

start_swtpm() {
    if [ -e "$AGIO_TPM_SOCK" ]; then
        return 0
    fi
    mkdir -p "$AGIO_TPM_DIR"
    swtpm socket --daemon --tpm2 \
        --tpmstate dir="$AGIO_TPM_DIR" \
        --ctrl type=unixio,path="$AGIO_TPM_SOCK" \
        --pid file="$AGIO_TPM_DIR/swtpm.pid" \
        --log file="$AGIO_TPM_DIR/swtpm.log"
}

stop_swtpm() {
    if [ -f "$AGIO_TPM_DIR/swtpm.pid" ]; then
        kill "$(cat "$AGIO_TPM_DIR/swtpm.pid")" 2>/dev/null || true
        rm -f "$AGIO_TPM_DIR/swtpm.pid"
    fi
    rm -f "$AGIO_TPM_SOCK"
}

vm_is_running() {
    [ -f "$AGIO_VM_DIR/qemu.pid" ] && kill -0 "$(cat "$AGIO_VM_DIR/qemu.pid")" 2>/dev/null
}

vm_port_in_use() {
    ss -H -ltn "sport = :$AGIO_VM_SSH_PORT" 2>/dev/null | grep -q .
}

wait_for_ssh() {
    echo "--- Waiting for guest SSH (up to $((AGIO_VM_BOOT_TIMEOUT / 60)) min) ---"
    local deadline=$((SECONDS + AGIO_VM_BOOT_TIMEOUT))
    while [ $SECONDS -lt $deadline ]; do
        if vm_ssh_reachable; then
            echo "--- Guest is up ---"
            return 0
        fi
        sleep 5
    done
    return 1
}

start_vm_headless() {
    start_swtpm
    # shellcheck disable=SC2086
    if ! "$AGIO_QEMU_BIN" $(qemu_base_args) \
        -display none \
        -daemonize \
        -pidfile "$AGIO_VM_DIR/qemu.pid"; then
        rm -f "$AGIO_VM_DIR/qemu.pid"
        stop_swtpm
        return 1
    fi
}

shutdown_vm() {
    echo "--- Shutting down guest ---"
    ssh_vm 'shutdown /s /t 5' >/dev/null 2>&1 || true
    local deadline=$((SECONDS + 120))
    while vm_is_running && [ $SECONDS -lt $deadline ]; do
        sleep 5
    done
    if vm_is_running; then
        echo "[WARN] guest did not stop in time, killing QEMU"
        kill "$(cat "$AGIO_VM_DIR/qemu.pid")" 2>/dev/null || true
    fi
    rm -f "$AGIO_VM_DIR/qemu.pid"
    stop_swtpm
    echo "--- VM stopped ---"
}

qemu_base_args() {
    # Common machine config: UEFI + Secure Boot ready + TPM 2.0 (Win10/Win11)
    echo \
        -name agio-win-builder \
        -machine q35,smm=on -cpu host -enable-kvm \
        -smp "$AGIO_VM_CPUS" -m "$AGIO_VM_RAM" \
        -drive if=pflash,format=raw,readonly=on,file="$AGIO_OVMF_CODE" \
        -drive if=pflash,format=raw,file="$AGIO_OVMF_VARS" \
        -global driver=cfi.pflash01,property=secure,value=on \
        -tpmdev emulator,id=tpm0,chardev=chrtpm \
        -chardev socket,id=chrtpm,path="$AGIO_TPM_SOCK" \
        -device tpm-tis,tpmdev=tpm0 \
        -netdev user,id=net0,hostfwd=tcp:127.0.0.1:"$AGIO_VM_SSH_PORT"-:22 \
        -device virtio-net-pci,netdev=net0 \
        -drive id=hd0,if=none,format=qcow2,file="$AGIO_VM_DISK",cache=writeback \
        -device virtio-blk-pci,drive=hd0,bootindex=0 \
        -monitor unix:"$AGIO_VM_DIR/monitor.sock",server,nowait
}
