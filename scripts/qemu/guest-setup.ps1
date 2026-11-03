# One-time provisioning of the Windows builder VM.
# Run INSIDE the Windows guest, in an elevated PowerShell:
#
#   powershell -ExecutionPolicy Bypass -File guest-setup.ps1 -SshPublicKey "<contents of id_ed25519.pub>"
#
# On the host the public key lives at .vm/windows-builder/id_ed25519.pub
# (created by create-vm.sh). Easiest way to transfer it: copy the file to the
# VM via the browser/clipboard, or run this script without the key argument
# and add the key manually as described in README.md.

param(
    [string]$SshPublicKey = "",
    [string]$BuildUser = "Admin"
)

$ErrorActionPreference = "Stop"

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

# --- 1. OpenSSH server: the host wrapper drives the build over SSH ---
Step "Enabling OpenSSH Server"
$cap = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
if ($cap.State -ne 'Installed') {
    Add-WindowsCapability -Online -Name $cap.Name | Out-Null
}
Set-Service sshd -StartupType Automatic
Start-Service sshd
if (-not (Get-NetFirewallRule -Name 'OpenSSH-Server-In' -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In' -DisplayName 'OpenSSH Server (sshd)' `
        -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
}

# --- 2. Build tools: git (agio-core dependency) and uv (python + deps) ---
Step "Installing Git and uv via winget"
winget install --id Git.Git      -e --accept-source-agreements --accept-package-agreements --disable-interactivity
winget install --id astral-sh.uv -e --accept-source-agreements --accept-package-agreements --disable-interactivity

# refresh PATH for this session (winget installs update the registry, not us)
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

foreach ($tool in @("git.exe", "uv.exe")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Warning "$tool still not in PATH - reboot the VM and re-login, it is required for builds."
    }
}

# --- 3. SSH key of the host ---
if ($SshPublicKey -ne "") {
    Step "Installing host SSH key"
    $userDir = "C:\Users\$BuildUser\.ssh"
    New-Item -ItemType Directory -Force "$userDir" | Out-Null
    Add-Content -Encoding ascii "$userDir\authorized_keys" $SshPublicKey

    # for admin accounts sshd reads this file instead
    $adminKeys = "C:\ProgramData\ssh\administrators_authorized_keys"
    Add-Content -Encoding ascii $adminKeys $SshPublicKey
    icacls $adminKeys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F" | Out-Null
} else {
    Write-Warning "No -SshPublicKey given; add .vm/windows-builder/id_ed25519.pub manually (README.md)."
}

# --- 4. Headless-friendly power settings: never sleep while building ---
Step "Disabling sleep/hibernate"
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg -h off

Step "Done. From the Linux host run: bash scripts/qemu/build-windows-qemu.sh"
