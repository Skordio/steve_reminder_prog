# uninstall_windows_startup.ps1
# Removes the startup launcher for reminder_startup.py and optionally
# deletes the venv and saved reminder data.
#
# Run from PowerShell:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # (once, if needed)
#   .\uninstall_windows_startup.ps1

$ErrorActionPreference = "Stop"

$ScriptDir     = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoDir       = Split-Path -Parent $ScriptDir   # repo root (parent of windows/)
$VenvDir       = Join-Path $RepoDir ".venv"
$StartupFolder = [System.Environment]::GetFolderPath("Startup")
$BatchFile     = Join-Path $StartupFolder "run_reminders.bat"
$DataDir       = Join-Path $env:APPDATA "SteveReminderProg"

# ── remove startup launcher ────────────────────────────────────────────────────

if (Test-Path $BatchFile) {
    Remove-Item $BatchFile -Force
    Write-Host "Removed: $BatchFile"
} else {
    Write-Host "Launcher not found (already removed)."
}

# ── optionally remove venv ─────────────────────────────────────────────────────

if (Test-Path $VenvDir) {
    Write-Host ""
    $reply = Read-Host "Remove venv at $VenvDir`? [y/N]"
    if ($reply -match "^[Yy]$") {
        Remove-Item $VenvDir -Recurse -Force
        Write-Host "Removed: $VenvDir"
    } else {
        Write-Host "Venv kept at: $VenvDir"
    }
}

# ── optionally remove reminder data ───────────────────────────────────────────

if (Test-Path $DataDir) {
    Write-Host ""
    $reply = Read-Host "Remove reminder data at $DataDir`? [y/N]"
    if ($reply -match "^[Yy]$") {
        Remove-Item $DataDir -Recurse -Force
        Write-Host "Removed: $DataDir"
    } else {
        Write-Host "Data kept at: $DataDir"
    }
}

Write-Host ""
Write-Host "Done. reminder_startup.py will no longer run at login."
