#!/usr/bin/env zsh
# uninstall_macos_startup.zsh
# Unloads and removes the launchd agent for reminder_startup.py.

set -e

PLIST_LABEL="com.$(whoami).reminder-startup"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
SCRIPT_DIR="${0:A:h}"
VENV_DIR="$SCRIPT_DIR/.venv"
LOG_DIR="$HOME/Library/Logs/SteveReminderProg"
DATA_DIR="$HOME/SteveReminderProg"

# ── unload agent ───────────────────────────────────────────────────────────────

if launchctl list "$PLIST_LABEL" &>/dev/null; then
  echo "Unloading launchd agent..."
  launchctl unload "$PLIST_PATH"
  echo "Agent unloaded."
else
  echo "Agent is not currently loaded (skipping unload)."
fi

# ── remove plist ───────────────────────────────────────────────────────────────

if [[ -f "$PLIST_PATH" ]]; then
  rm "$PLIST_PATH"
  echo "Removed: $PLIST_PATH"
else
  echo "Plist not found (already removed)."
fi

# ── optionally remove venv ─────────────────────────────────────────────────────

if [[ -d "$VENV_DIR" ]]; then
  echo ""
  read -r "REPLY?Remove venv at $VENV_DIR? [y/N] "
  if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    rm -rf "$VENV_DIR"
    echo "Removed: $VENV_DIR"
  else
    echo "Venv kept at: $VENV_DIR"
  fi
fi

# ── optionally remove logs ─────────────────────────────────────────────────────

if [[ -d "$LOG_DIR" ]]; then
  echo ""
  read -r "REPLY?Remove log files at $LOG_DIR? [y/N] "
  if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    rm -rf "$LOG_DIR"
    echo "Removed: $LOG_DIR"
  fi
fi

# ── optionally remove reminder data ───────────────────────────────────────────

if [[ -d "$DATA_DIR" ]]; then
  echo ""
  read -r "REPLY?Remove reminder data at $DATA_DIR? [y/N] "
  if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    rm -rf "$DATA_DIR"
    echo "Removed: $DATA_DIR"
  else
    echo "Data kept at: $DATA_DIR"
  fi
fi

echo ""
echo "Done. reminder_startup.py will no longer run at login."
