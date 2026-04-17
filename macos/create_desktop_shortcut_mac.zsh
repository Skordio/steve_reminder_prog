#!/usr/bin/env zsh
# create_desktop_shortcut_mac.zsh
# Creates a "Reminder Manager.app" on the Desktop that launches
# reminder_manager_gui.py with no terminal window.

set -e

SCRIPT_DIR="${0:A:h}"         # absolute path to macos/
REPO_DIR="${SCRIPT_DIR:h}"    # repo root (parent of macos/)
GUI_SCRIPT="$REPO_DIR/reminder_manager_gui.py"
VENV_PYTHON="$REPO_DIR/.venv/bin/python3"
APP_NAME="Reminder Manager"
APP_PATH="$HOME/Desktop/${APP_NAME}.app"

# ── sanity check ───────────────────────────────────────────────────────────────

if [[ ! -f "$GUI_SCRIPT" ]]; then
  echo "Error: reminder_manager_gui.py not found at $GUI_SCRIPT"
  echo "Make sure the macos/ folder is inside the repo root."
  exit 1
fi

# ── pick python — venv first, then system ─────────────────────────────────────

if [[ -x "$VENV_PYTHON" ]]; then
  PYTHON="$VENV_PYTHON"
  echo "Using venv Python: $PYTHON"
else
  for candidate in \
    "$(command -v python3 2>/dev/null)" \
    "/opt/homebrew/bin/python3" \
    "/usr/local/bin/python3" \
    "/usr/bin/python3"
  do
    if [[ -x "$candidate" ]] && "$candidate" -c "import tkinter" &>/dev/null; then
      PYTHON="$candidate"
      break
    fi
  done

  if [[ -z "$PYTHON" ]]; then
    echo "Error: no python3 with tkinter found."
    echo "Run setup_macos_startup.zsh first, or install Python from https://www.python.org/downloads/"
    exit 1
  fi
  echo "No venv found — using system Python: $PYTHON"
fi

# ── remove old app if present ─────────────────────────────────────────────────

if [[ -e "$APP_PATH" ]]; then
  echo "Removing existing app at $APP_PATH ..."
  rm -rf "$APP_PATH"
fi

# ── compile AppleScript → .app ────────────────────────────────────────────────
# The & at the end of the shell script detaches the process so the .app
# exits immediately rather than waiting for the GUI window to close.

osacompile -o "$APP_PATH" - <<APPLESCRIPT
on run
  do shell script "${PYTHON} '${GUI_SCRIPT}' > /dev/null 2>&1 &"
end run
APPLESCRIPT

# ── make the app executable and remove quarantine flag ────────────────────────

chmod +x "$APP_PATH/Contents/MacOS/applet"
xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null || true

echo ""
echo "App created: $APP_PATH"
echo "Double-click it from your Desktop to open the Reminder Manager."
echo ""
echo "Tip: to set a custom icon, get a .icns file then:"
echo "  1. Open it in Preview → Edit → Select All → Copy"
echo "  2. Select the .app in Finder → Cmd+I → click the icon → Cmd+V"
