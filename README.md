# Reminder App

No third-party dependencies required (tkinter ships with Python on Windows). `tkcalendar` is optional for a nicer date picker.

## Files

| File | Purpose |
|------|---------|
| `reminder_manager.py` | Interactive **terminal** UI — create, edit, delete reminders |
| `reminder_manager_gui.py` | Interactive **GUI** UI — same features in a windowed interface |
| `reminder_startup.py` | Startup script — checks due reminders and shows popup windows |

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

### Windows

1. Right-click your Desktop → **New → Shortcut**
2. For the target, enter (update the path to match your install location):
   ```
   pythonw "C:\full\path\to\reminder_manager_gui.py"
   ```
3. Click **Next**, give it a name (e.g. `Reminder Manager`), click **Finish**

> Using `pythonw` instead of `python` prevents a console window from flashing when you open the shortcut.

**Optional — set a custom icon:**
Right-click the shortcut → **Properties → Change Icon**, then browse to any `.ico` file you like.

---

### macOS

1. Open **Script Editor** (search it in Spotlight)
2. Paste the following, updating the path to match your install location:
   ```applescript
   do shell script "/full/path/to/.venv/bin/python3 /full/path/to/reminder_manager_gui.py &> /dev/null &"
   ```
3. Go to **File → Export**, set **File Format** to **Application**, and save it to your Desktop (e.g. `Reminder Manager.app`)
4. Double-clicking that `.app` file will launch the GUI with no terminal window

> If you haven't run the setup script (and therefore have no `.venv`), replace the python path with the output of `which python3`.

**Optional — set a custom icon:**
Get a `.icns` file, open it in Preview, press **⌘A** then **⌘C**, then select the `.app` in Finder, press **⌘I** to open its info panel, click the icon in the top-left, and press **⌘V**.

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
