# setup_windows_startup.ps1
# Creates a venv, installs dependencies, and adds a .bat launcher to the
# Windows Startup folder so reminder_startup.py runs at every login.
#
# Run from PowerShell:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # (once, if needed)
#   .\setup_windows_startup.ps1

$ErrorActionPreference = "Stop"

$ScriptDir     = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoDir       = Split-Path -Parent $ScriptDir   # repo root (parent of windows/)
$StartupScript = Join-Path $RepoDir "reminder_startup.py"
$VenvDir       = Join-Path $RepoDir ".venv"
$StartupFolder = [System.Environment]::GetFolderPath("Startup")
$BatchFile     = Join-Path $StartupFolder "run_reminders.bat"

# ── sanity check ───────────────────────────────────────────────────────────────

if (-not (Test-Path $StartupScript)) {
    Write-Error "reminder_startup.py not found at: $StartupScript`nMake sure the windows\ folder is inside the repo root."
    exit 1
}

# ── find a system python to bootstrap the venv ────────────────────────────────

$BootstrapPython = $null
foreach ($candidate in @("python", "python3")) {
    $found = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($found) {
        $BootstrapPython = $found.Source
        break
    }
}

if (-not $BootstrapPython) {
    Write-Error "Python not found. Install it from https://www.python.org/downloads/`nMake sure 'Add Python to PATH' is checked during install."
    exit 1
}

Write-Host "Bootstrap Python: $BootstrapPython"

# ── create / refresh venv ─────────────────────────────────────────────────────

if (Test-Path $VenvDir) {
    Write-Host "Existing venv found — recreating..."
    Remove-Item $VenvDir -Recurse -Force
}

Write-Host "Creating venv at $VenvDir ..."
& $BootstrapPython -m venv $VenvDir

$VenvPip     = Join-Path $VenvDir "Scripts\pip.exe"
$VenvPythonw = Join-Path $VenvDir "Scripts\pythonw.exe"
$VenvPython  = Join-Path $VenvDir "Scripts\python.exe"

# ── install dependencies ───────────────────────────────────────────────────────

Write-Host "Installing dependencies..."
& $VenvPip install --quiet --upgrade pip
& $VenvPip install --quiet tkcalendar
Write-Host "Dependencies installed."

# ── pick pythonw vs python (pythonw suppresses the console window) ─────────────

$Launcher = if (Test-Path $VenvPythonw) { $VenvPythonw } else { $VenvPython }
Write-Host "Launcher binary: $Launcher"

# ── write the batch file ───────────────────────────────────────────────────────

$BatchContent = "@echo off`r`n`"$Launcher`" `"$StartupScript`"`r`n"
Set-Content -Path $BatchFile -Value $BatchContent -Encoding ASCII

Write-Host "Launcher written to: $BatchFile"
Write-Host ""
Write-Host "Done. reminder_startup.py will run at every login using the venv at:"
Write-Host "  $VenvDir"
Write-Host ""
Write-Host "To disable:  Delete $BatchFile"
Write-Host "To run now:  & `"$Launcher`" `"$StartupScript`""
