"""
reminder_startup.py — place a shortcut to this in the Windows Startup folder.
Run with: pythonw reminder_startup.py  (no console window)
"""

import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
import tkinter as tk

DATA_FILE = Path(os.environ.get("APPDATA", Path.home())) / "SteveReminderProg" / "reminders.json"

BG       = "#1a1a2e"
BG_CARD  = "#16213e"
ACCENT   = "#e94560"
FG       = "#ffffff"
FG_DIM   = "#aaaaaa"


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


# ── reminder popup ─────────────────────────────────────────────────────────────

def show_reminder_window(reminder):
    """Show reminder window. Returns 'snooze' or 'done'."""
    root = tk.Tk()
    root.title("Reminder")
    root.resizable(False, False)
    root.configure(bg=BG)
    root.attributes("-topmost", True)

    W, H = 640, 420
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

    result = {"action": "snooze"}

    def snooze():
        result["action"] = "snooze"
        root.destroy()

    def done():
        result["action"] = "done"
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", snooze)

    # ── layout ────────────────────────────────────────────────────────────────

    # top banner
    banner = tk.Frame(root, bg=ACCENT, height=6)
    banner.pack(fill="x")

    # "REMINDER" label
    tk.Label(root, text="REMINDER", font=("Segoe UI", 13, "bold"),
             fg=ACCENT, bg=BG, pady=18).pack()

    # name
    tk.Label(root, text=reminder["name"],
             font=("Segoe UI", 26, "bold"),
             fg=FG, bg=BG, wraplength=580, justify="center").pack(padx=30)

    # divider
    tk.Frame(root, bg=ACCENT, height=2).pack(fill="x", padx=40, pady=12)

    # description
    desc = reminder.get("description", "").strip() or "(no description)"
    tk.Label(root, text=desc,
             font=("Segoe UI", 14),
             fg=FG_DIM, bg=BG, wraplength=560, justify="center").pack(padx=30)

    # interval note
    interval = reminder.get("interval_days", 0)
    tk.Label(root, text=f"Repeats every {interval} day(s)",
             font=("Segoe UI", 10),
             fg="#555577", bg=BG).pack(pady=(8, 0))

    # spacer
    tk.Frame(root, bg=BG).pack(expand=True, fill="both")

    # buttons
    btn_row = tk.Frame(root, bg=BG, pady=24)
    btn_row.pack(fill="x")

    _btn(btn_row, "Snooze  (remind next startup)", snooze,
         bg=BG_CARD, fg=FG_DIM, side="left")
    _btn(btn_row, "  Done  ✓  ", done,
         bg=ACCENT, fg=FG, side="right")

    root.mainloop()
    return result["action"]


def _btn(parent, text, cmd, bg, fg, side):
    tk.Button(parent, text=text, command=cmd,
              font=("Segoe UI", 12, "bold"),
              bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
              relief="flat", padx=26, pady=12, cursor="hand2",
              bd=0, highlightthickness=0).pack(side=side, padx=36)


# ── date-picker popup ──────────────────────────────────────────────────────────

def show_date_picker(reminder):
    """
    Ask user for the next remind date.
    Returns a 'YYYY-MM-DD' string (never None — falls back to default).
    """
    interval    = reminder.get("interval_days", 7)
    default_dt  = date.today() + timedelta(days=interval)
    default_str = default_dt.strftime("%Y-%m-%d")

    root = tk.Tk()
    root.title("Next Reminder Date")
    root.resizable(False, False)
    root.configure(bg=BG)
    root.attributes("-topmost", True)

    W, H = 420, 320
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

    result = {"date": default_str}

    tk.Label(root, text="Set Next Reminder Date",
             font=("Segoe UI", 16, "bold"),
             fg=FG, bg=BG, pady=20).pack()

    tk.Label(root, text=f"Default: {default_str}  (today + {interval} days)",
             font=("Segoe UI", 10), fg=FG_DIM, bg=BG).pack()

    # ── try tkcalendar; fall back to plain entry ───────────────────────────────
    try:
        from tkcalendar import DateEntry  # pip install tkcalendar

        frame = tk.Frame(root, bg=BG, pady=22)
        frame.pack()
        cal = DateEntry(frame, width=14, background=ACCENT, foreground=FG,
                        normalbackground=BG_CARD, normalforeground=FG,
                        selectbackground=ACCENT, selectforeground=FG,
                        headersbackground=BG_CARD, headersforeground=FG_DIM,
                        borderwidth=0, font=("Segoe UI", 13),
                        date_pattern="yyyy-mm-dd",
                        year=default_dt.year, month=default_dt.month, day=default_dt.day)
        cal.pack()

        def confirm():
            result["date"] = cal.get_date().strftime("%Y-%m-%d")
            root.destroy()

    except ImportError:
        tk.Label(root, text="Enter date (YYYY-MM-DD):",
                 font=("Segoe UI", 12), fg=FG, bg=BG, pady=16).pack()

        entry_var = tk.StringVar(value=default_str)
        entry = tk.Entry(root, textvariable=entry_var,
                         font=("Segoe UI", 15), width=14,
                         bg=BG_CARD, fg=FG, insertbackground=FG,
                         justify="center", relief="flat", bd=0)
        entry.pack(ipady=8)

        err = tk.Label(root, text="", font=("Segoe UI", 10), fg=ACCENT, bg=BG)
        err.pack()

        def confirm():
            val = entry_var.get().strip()
            try:
                datetime.strptime(val, "%Y-%m-%d")
                result["date"] = val
                root.destroy()
            except ValueError:
                err.config(text="Invalid format — use YYYY-MM-DD")

    def on_close():
        root.destroy()   # result already holds default_str

    root.protocol("WM_DELETE_WINDOW", on_close)

    tk.Button(root, text="Confirm", command=confirm,
              font=("Segoe UI", 13, "bold"),
              bg=ACCENT, fg=FG, activebackground=ACCENT, activeforeground=FG,
              relief="flat", padx=30, pady=10, cursor="hand2",
              bd=0, highlightthickness=0).pack(pady=18)

    root.mainloop()
    return result["date"]


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    reminders = load_reminders()
    today     = date.today()

    due = [
        r for r in reminders
        if datetime.strptime(r["remind_date"], "%Y-%m-%d").date() <= today
    ]

    if not due:
        sys.exit(0)

    for reminder in due:
        action = show_reminder_window(reminder)

        if action == "done":
            new_date = show_date_picker(reminder)
            for r in reminders:
                if r["id"] == reminder["id"]:
                    r["remind_date"] = new_date
                    break
            save_reminders(reminders)
        # snooze → do nothing, will re-appear next startup


if __name__ == "__main__":
    main()
