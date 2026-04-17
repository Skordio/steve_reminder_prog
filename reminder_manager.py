"""
reminder_manager.py — interactive terminal UI for managing reminders.
Run with: python reminder_manager.py
"""

import json
import os
import time
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_FILE = Path(os.environ.get("APPDATA", Path.home())) / "SteveReminderProg" / "reminders.json"

W = 62   # display width


# ── data helpers ──────────────────────────────────────────────────────────────

def load_reminders():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh).get("reminders", [])


def save_reminders(reminders):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump({"reminders": reminders}, fh, indent=2)


# ── terminal helpers ───────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header(subtitle=""):
    print("=" * W)
    print("  REMINDER MANAGER" + (f"  —  {subtitle}" if subtitle else ""))
    print("=" * W)


def pause():
    input("\n  Press Enter to continue...")


def ask(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"  {prompt}{suffix}: ").strip()
    return val or (str(default) if default is not None else "")


def ask_date(prompt, default=None):
    """Ask for a YYYY-MM-DD date, looping until valid."""
    while True:
        val = ask(prompt, default=default)
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except ValueError:
            print("  ✗ Invalid date — use YYYY-MM-DD (e.g. 2026-06-01)")


def ask_int(prompt, default=None, min_val=1):
    """Ask for an integer >= min_val, looping until valid."""
    while True:
        raw = ask(prompt, default=default)
        try:
            n = int(raw)
            if n >= min_val:
                return n
            print(f"  ✗ Must be at least {min_val}.")
        except ValueError:
            print("  ✗ Please enter a whole number.")


def ask_choice(prompt, options):
    """Ask for one of the given single-char options (e.g. ['y','n'])."""
    opts_str = "/".join(options)
    while True:
        val = input(f"  {prompt} ({opts_str}): ").strip().lower()
        if val in options:
            return val
        print(f"  ✗ Please enter one of: {opts_str}")


def pick_index(reminders, action_verb):
    """Ask user to pick a reminder by number. Returns index or None."""
    while True:
        raw = input(f"\n  Enter # to {action_verb} (0 to cancel): ").strip()
        try:
            n = int(raw)
            if n == 0:
                return None
            if 1 <= n <= len(reminders):
                return n - 1
            print(f"  ✗ Enter a number between 1 and {len(reminders)}.")
        except ValueError:
            print("  ✗ Please enter a number.")


# ── screens ───────────────────────────────────────────────────────────────────

def screen_list(reminders):
    clear()
    header("All Reminders")
    if not reminders:
        print("\n  (no reminders yet — use option 2 to add one)\n")
        pause()
        return

    today = date.today()
    print(f"\n  {'#':<4} {'Name':<24} {'Next Date':<13} {'Every':<8} Status")
    print("  " + "─" * (W - 2))

    for i, r in enumerate(reminders, 1):
        rd     = datetime.strptime(r["remind_date"], "%Y-%m-%d").date()
        status = "*** DUE ***" if rd <= today else f"in {(rd - today).days}d"
        idays  = f"{r['interval_days']}d"
        print(f"  {i:<4} {r['name'][:23]:<24} {r['remind_date']:<13} {idays:<8} {status}")

    print()
    pause()


def screen_add(reminders):
    clear()
    header("Add Reminder")
    print()

    name = ""
    while not name:
        name = input("  Name: ").strip()
        if not name:
            print("  ✗ Name cannot be empty.")

    description   = ask("Description (optional)", default="")
    today_str     = date.today().strftime("%Y-%m-%d")
    remind_date   = ask_date("Remind date (YYYY-MM-DD)", default=today_str)
    interval_days = ask_int("Repeat every N days", default=7)

    reminder = {
        "id":           str(uuid.uuid4()),
        "name":         name,
        "description":  description,
        "remind_date":  remind_date,
        "interval_days": interval_days,
    }
    reminders.append(reminder)
    save_reminders(reminders)
    print(f"\n  ✓ Reminder \"{name}\" saved.")
    pause()


def screen_view(reminders):
    if not reminders:
        _no_reminders(); return

    clear()
    header("View Reminder Details")
    _print_name_list(reminders)

    idx = pick_index(reminders, "view")
    if idx is None:
        return

    r = reminders[idx]
    clear()
    header(f"Detail — {r['name']}")
    print(f"\n  Name         {r['name']}")
    print(f"  Description  {r['description'] or '(none)'}")
    print(f"  Next remind  {r['remind_date']}")
    print(f"  Interval     every {r['interval_days']} day(s)")
    print(f"  ID           {r['id']}")
    pause()


def screen_edit(reminders):
    if not reminders:
        _no_reminders(); return

    clear()
    header("Edit Reminder")
    _print_name_list(reminders)

    idx = pick_index(reminders, "edit")
    if idx is None:
        return

    r = reminders[idx]
    print(f"\n  Editing \"{r['name']}\"  (Enter = keep current value)\n")

    new_name = ask("Name", default=r["name"])
    if new_name:
        r["name"] = new_name

    new_desc = ask("Description", default=r["description"] or "")
    r["description"] = new_desc

    r["remind_date"]   = ask_date("Remind date", default=r["remind_date"])
    r["interval_days"] = ask_int("Repeat every N days", default=r["interval_days"])

    save_reminders(reminders)
    print(f"\n  ✓ Reminder updated.")
    pause()


def screen_delete(reminders):
    if not reminders:
        _no_reminders(); return

    clear()
    header("Delete Reminder")
    _print_name_list(reminders)

    idx = pick_index(reminders, "delete")
    if idx is None:
        return

    name = reminders[idx]["name"]
    confirm = ask_choice(f"Delete \"{name}\"? This cannot be undone", ["y", "n"])
    if confirm == "y":
        reminders.pop(idx)
        save_reminders(reminders)
        print(f"\n  ✓ \"{name}\" deleted.")
    else:
        print("  Cancelled.")
    pause()


def screen_startup_help():
    clear()
    header("Windows Startup Setup")
    print("""
  To make reminder_startup.py run every time you log in:

  OPTION A — Batch file in Startup folder (recommended)
  ────────────────────────────────────────────────────
  1. Press  Win + R,  type  shell:startup,  press Enter.
     The Startup folder opens in Explorer.

  2. Create a new file called  run_reminders.bat  there
     with this content (update the path to match yours):

       @echo off
       pythonw "C:\\Users\\YourName\\reminder_startup.py"

     Using  pythonw  (not python) hides the console window.

  OPTION B — Direct shortcut
  ──────────────────────────
  1. Open the Startup folder (same as step 1 above).
  2. Right-click → New → Shortcut.
  3. Target:  pythonw  "C:\\full\\path\\to\\reminder_startup.py"

  DATA FILE LOCATION
  ──────────────────""")
    print(f"  {DATA_FILE}\n")
    pause()


# ── small helpers ──────────────────────────────────────────────────────────────

def _no_reminders():
    print("\n  No reminders found. Add one first (option 2).")
    pause()


def _print_name_list(reminders):
    print()
    for i, r in enumerate(reminders, 1):
        print(f"  {i}.  {r['name']}")


# ── main loop ─────────────────────────────────────────────────────────────────

MENU = [
    ("List all reminders",         screen_list),
    ("Add reminder",               screen_add),
    ("View reminder details",      screen_view),
    ("Edit reminder",              screen_edit),
    ("Delete reminder",            screen_delete),
    ("Startup setup instructions", screen_startup_help),
    ("Exit",                       None),
]


def main():
    while True:
        reminders = load_reminders()
        today     = date.today()
        due       = sum(
            1 for r in reminders
            if datetime.strptime(r["remind_date"], "%Y-%m-%d").date() <= today
        )

        clear()
        header()
        print(f"\n  Reminders: {len(reminders)}", end="")
        if due:
            print(f"   |   {due} DUE TODAY ← ", end="")
        print("\n")

        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {i}.  {label}")

        print()
        choice = input("  Choose: ").strip()

        if not choice.isdigit() or not (1 <= int(choice) <= len(MENU)):
            print("  ✗ Invalid choice.")
            time.sleep(0.6)
            continue

        idx    = int(choice) - 1
        _, fn  = MENU[idx]

        if fn is None:   # Exit
            clear()
            break

        fn(reminders)


if __name__ == "__main__":
    main()
