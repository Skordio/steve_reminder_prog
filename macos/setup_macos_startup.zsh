#!/usr/bin/env zsh
# setup_macos_startup.zsh
# Creates a venv, installs dependencies, and registers a launchd agent so
# reminder_startup.py runs automatically at every login.

set -e

PLIST_LABEL="com.$(whoami).reminder-startup"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
SCRIPT_DIR="${0:A:h}"         # absolute path to macos/
REPO_DIR="${SCRIPT_DIR:h}"    # repo root (parent of macos/)
STARTUP_SCRIPT="$REPO_DIR/reminder_startup.py"
VENV_DIR="$REPO_DIR/.venv"
LOG_DIR="$HOME/Library/Logs/SteveReminderProg"

# ── sanity check ───────────────────────────────────────────────────────────────

if [[ ! -f "$STARTUP_SCRIPT" ]]; then
  echo "Error: reminder_startup.py not found at $STARTUP_SCRIPT"
  echo "Make sure the macos/ folder is inside the repo root."
  exit 1
fi

# ── find a system python3 with tkinter to bootstrap the venv ──────────────────

BOOTSTRAP_PYTHON=""
for candidate in \
  "$(command -v python3 2>/dev/null)" \
  "/opt/homebrew/bin/python3" \
  "/usr/local/bin/python3" \
  "/usr/bin/python3"
do
  if [[ -x "$candidate" ]] && "$candidate" -c "import tkinter" &>/dev/null; then
    BOOTSTRAP_PYTHON="$candidate"
    break
  fi
done

if [[ -z "$BOOTSTRAP_PYTHON" ]]; then
  echo "Error: no python3 with tkinter found."
  echo "Install Python from https://www.python.org/downloads/ (includes tkinter),"
  echo "or via Homebrew:  brew install python-tk"
  exit 1
fi

echo "Bootstrap Python: $BOOTSTRAP_PYTHON"

# ── create / refresh venv ─────────────────────────────────────────────────────

if [[ -d "$VENV_DIR" ]]; then
  echo "Existing venv found at $VENV_DIR — recreating..."
  rm -rf "$VENV_DIR"
fi

echo "Creating venv at $VENV_DIR ..."
"$BOOTSTRAP_PYTHON" -m venv "$VENV_DIR"

VENV_PYTHON="$VENV_DIR/bin/python3"

# ── install dependencies ───────────────────────────────────────────────────────

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet tkcalendar
echo "Dependencies installed."

# ── create log directory ───────────────────────────────────────────────────────

mkdir -p "$LOG_DIR"

# ── write the plist (points at venv python) ───────────────────────────────────

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_LABEL}</string>

  <key>ProgramArguments</key>
  <array>
    <string>${VENV_PYTHON}</string>
    <string>${STARTUP_SCRIPT}</string>
  </array>

  <!-- Run once each time the user logs in -->
  <key>RunAtLoad</key>
  <true/>

  <!-- Do NOT restart automatically if it exits -->
  <key>KeepAlive</key>
  <false/>

  <key>StandardOutPath</key>
  <string>${LOG_DIR}/stdout.log</string>

  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/stderr.log</string>
</dict>
</plist>
EOF

echo "Plist written to: $PLIST_PATH"

# ── unload any existing version, then load the new one ────────────────────────

if launchctl list "$PLIST_LABEL" &>/dev/null; then
  echo "Unloading existing agent..."
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

launchctl load "$PLIST_PATH"
echo ""
echo "Done. reminder_startup.py will run at every login using the venv at:"
echo "  $VENV_DIR"
echo ""
echo "Useful commands:"
echo "  Run now:    launchctl start $PLIST_LABEL"
echo "  Disable:    launchctl unload \"$PLIST_PATH\""
echo "  Re-enable:  launchctl load  \"$PLIST_PATH\""
echo "  Logs:       tail -f $LOG_DIR/stderr.log"
