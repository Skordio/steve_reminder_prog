"""
reminder_manager_gui.py — GUI alternative to reminder_manager.py.
Run with: python reminder_manager_gui.py
"""

import json
import os
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = Path(os.environ.get("APPDATA", Path.home())) / "SteveReminderProg" / "reminders.json"

BG       = "#1a1a2e"
BG_CARD  = "#16213e"
BG_ROW   = "#0f3460"
ACCENT   = "#e94560"
FG       = "#ffffff"
FG_DIM   = "#aaaaaa"
FG_DUE   = "#ff6b6b"


# ── data helpers ───────────────────────────────────────────────────────────────

def load_reminders():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh).get("reminders", [])


def save_reminders(reminders):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump({"reminders": reminders}, fh, indent=2)


# ── date entry widget ──────────────────────────────────────────────────────────

def make_date_entry(parent, default_date):
    """Return (frame, get_date_fn). Uses tkcalendar if available."""
    try:
        from tkcalendar import DateEntry
        frame = tk.Frame(parent, bg=BG_CARD)
        cal = DateEntry(frame, width=14, background=ACCENT, foreground=FG,
                        normalbackground=BG_CARD, normalforeground=FG,
                        selectbackground=ACCENT, selectforeground=FG,
                        headersbackground=BG, headersforeground=FG_DIM,
                        borderwidth=0, font=("Segoe UI", 11),
                        date_pattern="yyyy-mm-dd",
                        year=default_date.year, month=default_date.month,
                        day=default_date.day)
        cal.pack()
        return frame, lambda: cal.get_date().strftime("%Y-%m-%d")
    except ImportError:
        frame = tk.Frame(parent, bg=BG_CARD)
        var = tk.StringVar(value=default_date.strftime("%Y-%m-%d"))
        entry = tk.Entry(frame, textvariable=var, font=("Segoe UI", 11),
                         bg=BG_CARD, fg=FG, insertbackground=FG,
                         relief="flat", bd=0, width=14, justify="center")
        entry.pack(ipady=6)

        def get():
            val = var.get().strip()
            datetime.strptime(val, "%Y-%m-%d")   # raises ValueError if bad
            return val

        return frame, get


# ── shared styled widgets ──────────────────────────────────────────────────────

def styled_button(parent, text, command, primary=False, **kw):
    bg = ACCENT if primary else BG_ROW
    fg = FG if primary else FG_DIM
    return tk.Button(parent, text=text, command=command,
                     font=("Segoe UI", 10, "bold"),
                     bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                     relief="flat", bd=0, highlightthickness=0,
                     padx=16, pady=7, cursor="hand2", **kw)


def field_row(parent, label, row):
    tk.Label(parent, text=label, font=("Segoe UI", 10),
             fg=FG_DIM, bg=BG_CARD, anchor="w").grid(
             row=row, column=0, sticky="w", padx=(16, 8), pady=4)


# ── add / edit dialog ──────────────────────────────────────────────────────────

def open_reminder_dialog(parent, existing=None):
    """
    Modal dialog for adding or editing a reminder.
    Returns the reminder dict on save, or None on cancel.
    """
    is_edit   = existing is not None
    title_txt = "Edit Reminder" if is_edit else "Add Reminder"
    today     = date.today()

    dlg = tk.Toplevel(parent)
    dlg.title(title_txt)
    dlg.resizable(False, False)
    dlg.configure(bg=BG)
    dlg.grab_set()

    W, H = 420, 380
    px = parent.winfo_rootx() + (parent.winfo_width()  - W) // 2
    py = parent.winfo_rooty() + (parent.winfo_height() - H) // 2
    dlg.geometry(f"{W}x{H}+{px}+{py}")

    # title bar
    tk.Frame(dlg, bg=ACCENT, height=4).pack(fill="x")
    tk.Label(dlg, text=title_txt, font=("Segoe UI", 13, "bold"),
             fg=FG, bg=BG, pady=12).pack()

    form = tk.Frame(dlg, bg=BG_CARD, padx=0, pady=12)
    form.pack(fill="both", expand=True, padx=20, pady=(0, 14))
    form.columnconfigure(1, weight=1)

    # ── name ──────────────────────────────────────────────────────────────────
    field_row(form, "Name", 0)
    name_var = tk.StringVar(value=existing["name"] if is_edit else "")
    tk.Entry(form, textvariable=name_var, font=("Segoe UI", 11),
             bg=BG, fg=FG, insertbackground=FG, relief="flat", bd=0
             ).grid(row=0, column=1, sticky="ew", padx=(0, 16), ipady=5)

    # ── description ───────────────────────────────────────────────────────────
    field_row(form, "Description", 1)
    desc_var = tk.StringVar(value=existing.get("description", "") if is_edit else "")
    tk.Entry(form, textvariable=desc_var, font=("Segoe UI", 11),
             bg=BG, fg=FG, insertbackground=FG, relief="flat", bd=0
             ).grid(row=1, column=1, sticky="ew", padx=(0, 16), ipady=5)

    # ── remind date ───────────────────────────────────────────────────────────
    field_row(form, "Remind date", 2)
    default_dt  = (datetime.strptime(existing["remind_date"], "%Y-%m-%d").date()
                   if is_edit else today)
    date_frame, get_date = make_date_entry(form, default_dt)
    date_frame.grid(row=2, column=1, sticky="w", padx=(0, 16), pady=4)

    # ── interval ──────────────────────────────────────────────────────────────
    field_row(form, "Repeat every N days", 3)
    interval_var = tk.StringVar(value=str(existing["interval_days"]) if is_edit else "7")
    tk.Entry(form, textvariable=interval_var, font=("Segoe UI", 11),
             bg=BG, fg=FG, insertbackground=FG, relief="flat", bd=0, width=8
             ).grid(row=3, column=1, sticky="w", padx=(0, 16), ipady=5)

    # ── error label ───────────────────────────────────────────────────────────
    err_var = tk.StringVar()
    tk.Label(dlg, textvariable=err_var, font=("Segoe UI", 9),
             fg=ACCENT, bg=BG).pack()

    result = {"value": None}

    def save():
        name = name_var.get().strip()
        if not name:
            err_var.set("Name cannot be empty.")
            return
        try:
            remind_date = get_date()
        except ValueError:
            err_var.set("Invalid date — use YYYY-MM-DD.")
            return
        try:
            interval = int(interval_var.get().strip())
            if interval < 1:
                raise ValueError
        except ValueError:
            err_var.set("Interval must be a whole number ≥ 1.")
            return

        result["value"] = {
            "id":            existing["id"] if is_edit else str(uuid.uuid4()),
            "name":          name,
            "description":   desc_var.get().strip(),
            "remind_date":   remind_date,
            "interval_days": interval,
        }
        dlg.destroy()

    # ── buttons ───────────────────────────────────────────────────────────────
    btn_row = tk.Frame(dlg, bg=BG)
    btn_row.pack(fill="x", padx=20, pady=(0, 16))
    styled_button(btn_row, "Cancel", dlg.destroy).pack(side="left")
    styled_button(btn_row, "Save", save, primary=True).pack(side="right")

    parent.wait_window(dlg)
    return result["value"]


# ── main window ────────────────────────────────────────────────────────────────

class ReminderManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reminder Manager")
        self.resizable(True, True)
        self.minsize(680, 400)
        self.configure(bg=BG)

        W, H = 780, 500
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

        self._build_ui()
        self.refresh()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        # top accent strip
        tk.Frame(self, bg=ACCENT, height=4).pack(fill="x")

        # header
        hdr = tk.Frame(self, bg=BG, pady=14)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="REMINDER MANAGER", font=("Segoe UI", 16, "bold"),
                 fg=FG, bg=BG).pack(side="left")
        self._status_var = tk.StringVar()
        tk.Label(hdr, textvariable=self._status_var, font=("Segoe UI", 10),
                 fg=FG_DIM, bg=BG).pack(side="right", pady=4)

        # treeview
        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Reminder.Treeview",
                         background=BG_CARD, foreground=FG, fieldbackground=BG_CARD,
                         rowheight=32, font=("Segoe UI", 10), borderwidth=0)
        style.configure("Reminder.Treeview.Heading",
                         background=BG, foreground=FG_DIM,
                         font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Reminder.Treeview",
                  background=[("selected", BG_ROW)],
                  foreground=[("selected", FG)])

        cols = ("name", "description", "remind_date", "interval", "status")
        self._tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                   style="Reminder.Treeview", selectmode="browse")

        self._tree.heading("name",        text="Name")
        self._tree.heading("description", text="Description")
        self._tree.heading("remind_date", text="Next Remind")
        self._tree.heading("interval",    text="Every")
        self._tree.heading("status",      text="Status")

        self._tree.column("name",        width=180, minwidth=120)
        self._tree.column("description", width=220, minwidth=100)
        self._tree.column("remind_date", width=110, minwidth=90,  anchor="center")
        self._tree.column("interval",    width=70,  minwidth=60,  anchor="center")
        self._tree.column("status",      width=100, minwidth=80,  anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._tree.tag_configure("due",    foreground=FG_DUE)
        self._tree.tag_configure("normal", foreground=FG)

        self._tree.bind("<Double-1>", lambda _: self.edit_reminder())
        self._tree.bind("<Delete>",   lambda _: self.delete_reminder())

        # button bar
        btn_bar = tk.Frame(self, bg=BG, pady=12)
        btn_bar.pack(fill="x", padx=20)

        styled_button(btn_bar, "+ Add",    self.add_reminder,    primary=True).pack(side="left", padx=(0, 8))
        styled_button(btn_bar, "✎ Edit",   self.edit_reminder                ).pack(side="left", padx=(0, 8))
        styled_button(btn_bar, "✕ Delete", self.delete_reminder              ).pack(side="left")
        styled_button(btn_bar, "↺ Refresh", self.refresh                     ).pack(side="right")

    # ── data & display ─────────────────────────────────────────────────────────

    def refresh(self):
        self._reminders = load_reminders()
        self._tree.delete(*self._tree.get_children())

        today   = date.today()
        due_cnt = 0

        for r in self._reminders:
            rd     = datetime.strptime(r["remind_date"], "%Y-%m-%d").date()
            is_due = rd <= today
            if is_due:
                due_cnt += 1
                status = "DUE"
            else:
                status = f"in {(rd - today).days}d"

            tag = "due" if is_due else "normal"
            self._tree.insert("", "end", iid=r["id"], tags=(tag,),
                               values=(
                                   r["name"],
                                   r.get("description", "") or "—",
                                   r["remind_date"],
                                   f"{r['interval_days']}d",
                                   status,
                               ))

        total = len(self._reminders)
        if due_cnt:
            self._status_var.set(f"{total} reminder(s)  •  {due_cnt} DUE")
        else:
            self._status_var.set(f"{total} reminder(s)")

    def _selected_reminder(self):
        sel = self._tree.selection()
        if not sel:
            return None
        rid = sel[0]
        return next((r for r in self._reminders if r["id"] == rid), None)

    # ── actions ────────────────────────────────────────────────────────────────

    def add_reminder(self):
        result = open_reminder_dialog(self)
        if result:
            self._reminders.append(result)
            save_reminders(self._reminders)
            self.refresh()
            self._tree.selection_set(result["id"])

    def edit_reminder(self):
        reminder = self._selected_reminder()
        if not reminder:
            messagebox.showinfo("Edit", "Select a reminder first.", parent=self)
            return
        result = open_reminder_dialog(self, existing=reminder)
        if result:
            for i, r in enumerate(self._reminders):
                if r["id"] == result["id"]:
                    self._reminders[i] = result
                    break
            save_reminders(self._reminders)
            self.refresh()
            self._tree.selection_set(result["id"])

    def delete_reminder(self):
        reminder = self._selected_reminder()
        if not reminder:
            messagebox.showinfo("Delete", "Select a reminder first.", parent=self)
            return
        if messagebox.askyesno("Delete",
                                f"Delete \"{reminder['name']}\"?\nThis cannot be undone.",
                                parent=self):
            self._reminders = [r for r in self._reminders if r["id"] != reminder["id"]]
            save_reminders(self._reminders)
            self.refresh()


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ReminderManagerApp()
    app.mainloop()
