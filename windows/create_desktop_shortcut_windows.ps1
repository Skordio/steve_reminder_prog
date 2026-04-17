# create_desktop_shortcut_windows.ps1
# Creates a Desktop shortcut that launches reminder_manager_gui.py.
#
# Run from PowerShell:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # (once, if needed)
#   .\create_desktop_shortcut_windows.ps1

$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoDir     = Split-Path -Parent $ScriptDir   # repo root (parent of windows/)
$GuiScript   = Join-Path $RepoDir "reminder_manager_gui.py"
$VenvPythonw = Join-Path $RepoDir ".venv\Scripts\pythonw.exe"
$VenvPython  = Join-Path $RepoDir ".venv\Scripts\python.exe"
$Desktop     = [System.Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "Reminder Manager.lnk"

# ── sanity check ───────────────────────────────────────────────────────────────

if (-not (Test-Path $GuiScript)) {
    Write-Error "reminder_manager_gui.py not found at: $GuiScript`nMake sure the windows\ folder is inside the repo root."
    exit 1
}

# ── pick pythonw (suppresses console window) or fall back ─────────────────────

if (Test-Path $VenvPythonw) {
    $Launcher = $VenvPythonw
    Write-Host "Using venv pythonw: $Launcher"
} elseif (Test-Path $VenvPython) {
    $Launcher = $VenvPython
    Write-Warning "pythonw.exe not found in venv — using python.exe (a console window may briefly appear)."
} else {
    # No venv — fall back to system pythonw/python
    $found = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($found) {
        $Launcher = $found.Source
    } else {
        $found = Get-Command python -ErrorAction SilentlyContinue
        if (-not $found) {
            Write-Error "Python not found. Run setup_windows_startup.ps1 first, or install Python from https://www.python.org/downloads/"
            exit 1
        }
        $Launcher = $found.Source
        Write-Warning "pythonw.exe not found — using python.exe (a console window may briefly appear)."
    }
    Write-Host "No venv found — using system Python: $Launcher"
}

# ── create the shortcut ────────────────────────────────────────────────────────

$Shell    = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)

$Shortcut.TargetPath       = $Launcher
$Shortcut.Arguments        = "`"$GuiScript`""
$Shortcut.WorkingDirectory = $RepoDir
$Shortcut.Description      = "Open the Reminder Manager"
$Shortcut.WindowStyle      = 1   # normal window

# Use the Python executable's own icon as a fallback.
# If you have a custom .ico, replace this line with:
#   $Shortcut.IconLocation = "C:\path\to\icon.ico,0"
$Shortcut.IconLocation = "$Launcher,0"

$Shortcut.Save()

Write-Host ""
Write-Host "Shortcut created: $ShortcutPath"
Write-Host "Double-click it from your Desktop to open the Reminder Manager."
