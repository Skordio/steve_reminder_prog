# Reminder App

No third-party dependencies required (tkinter ships with Python on Windows). `tkcalendar` is optional for a nicer date picker.

## Files

| File | Purpose |
|------|---------|
| `reminder_manager.py` | Interactive **terminal** UI — create, edit, delete reminders |
| `reminder_manager_gui.py` | Interactive **GUI** UI — same features in a windowed interface |
| `reminder_startup.py` | Startup script — checks due reminders and shows popup windows |
| `create_desktop_shortcut_mac.zsh` | Creates a `Reminder Manager.app` on the macOS Desktop |
| `create_desktop_shortcut_windows.ps1` | Creates a `Reminder Manager` shortcut on the Windows Desktop |

## Quick start

```
# Terminal interface
python reminder_manager.py

# GUI interface
python reminder_manager_gui.py
```

Use the menu to add reminders. Each reminder has:
- **Name** — short title shown in the popup headline
- **Description** — detail text shown in the popup body
- **Remind date** — first date the reminder fires
- **Interval (days)** — how many days ahead to schedule the next reminder after clicking Done

## Startup setup

### macOS — install

```zsh
chmod +x setup_macos_startup.zsh
./setup_macos_startup.zsh
```

Creates and loads a launchd agent (`~/Library/LaunchAgents/`). Logs go to `~/Library/Logs/SteveReminderProg/`.

| Command | Effect |
|---------|--------|
| `launchctl start com.<you>.reminder-startup` | Run now without logging out |
| `launchctl unload ~/Library/LaunchAgents/com.<you>.reminder-startup.plist` | Disable |
| `launchctl load   ~/Library/LaunchAgents/com.<you>.reminder-startup.plist` | Re-enable |

### macOS — uninstall

```zsh
chmod +x uninstall_macos_startup.zsh
./uninstall_macos_startup.zsh
```

Unloads the agent, removes the plist, and optionally deletes logs and reminder data.

---

### Windows — install

Open PowerShell in the project folder and run:

```powershell
# Allow local scripts (only needed once per machine)
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

.\setup_windows_startup.ps1
```

Creates `run_reminders.bat` in your Startup folder (`shell:startup`). Uses `pythonw.exe` to suppress the console window.

### Windows — uninstall

```powershell
.\uninstall_windows_startup.ps1
```

Removes the startup launcher and optionally deletes saved reminder data.

## Desktop shortcut for the GUI manager

### macOS

```zsh
chmod +x create_desktop_shortcut_mac.zsh
./create_desktop_shortcut_mac.zsh
```

Creates `~/Desktop/Reminder Manager.app`. Uses the `.venv` Python if the setup script has been run, otherwise falls back to the system `python3`. Double-click the app to open the GUI with no terminal window.

**Optional — set a custom icon:**
Get a `.icns` file, open it in Preview → **⌘A** → **⌘C**, then select the `.app` in Finder → **⌘I** → click the icon in the top-left → **⌘V**.

---

### Windows

```powershell
.\create_desktop_shortcut_windows.ps1
```

Creates `Reminder Manager.lnk` on the Desktop. Uses the `.venv` `pythonw.exe` if the setup script has been run (no console flash), otherwise falls back to the system Python.

**Optional — set a custom icon:**
Right-click the shortcut → **Properties → Change Icon**, then browse to any `.ico` file you like.

---

## How the popup works

When `reminder_startup.py` runs it checks every reminder whose **remind date ≤ today** and shows a window for each one:

| Button | Effect |
|--------|--------|
| **Done ✓** | Opens a date picker — default is today + interval days. Confirm to save the new remind date. |
| **Snooze** (or close ✗) | Does nothing — the reminder will re-appear next startup. |

## Optional: nicer date picker

Install `tkcalendar` for a calendar widget instead of a plain text box:

```
pip install tkcalendar
```

## Data file

Reminders are stored as JSON at:

```
%APPDATA%\SteveReminderProg\reminders.json
```
