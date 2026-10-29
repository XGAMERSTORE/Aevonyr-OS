"""Modern dark desktop-style application for an existing Linux desktop."""
from datetime import datetime
from pathlib import Path
import platform
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .compat import CompatibilityError, backend_status, make_plan, execute_plan, open_android
from .config import load_preferences, save_preferences, notes_path
from .i18n import LANGUAGES, tr, install_language_pack

BG = "#100e1c"
SIDE = "#191528"
PANEL = "#241b37"
PANEL2 = "#39244d"
ACCENT = "#ad7cff"
INK = "#f6f0ff"
MUTED = "#bfb1cf"
PINK = "#ef81d9"

class AevonyrDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.preferences = load_preferences()
        self.language = self.preferences["language"]
        self.current_page = "home"
        self.current_dir = Path.home()
        self.title("Aevonyr OS — Desktop Preview")
        self.geometry("1140x730")
        self.minsize(780, 520)
        self.configure(bg=BG)
        self._create_shell()
        self.show("home")
        self.after(1000, self._tick)

    def t(self, key):
        return tr(key, self.language)

    def _create_shell(self):
        self.sidebar = tk.Frame(self, bg=SIDE, width=205)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="◕  AEVONYR", bg=SIDE, fg=INK,
                 font=("DejaVu Sans", 17, "bold"), pady=29).pack(fill="x")
        self.nav = tk.Frame(self.sidebar, bg=SIDE)
        self.nav.pack(fill="x", padx=12)
        main = tk.Frame(self, bg=BG)
        main.pack(side="right", fill="both", expand=True)
        self.header = tk.Frame(main, bg=BG, height=80)
        self.header.pack(fill="x", padx=30, pady=(18, 0))
        self.body = tk.Frame(main, bg=BG)
        self.body.pack(fill="both", expand=True, padx=30, pady=(10, 24))

    def _button(self, parent, label, callback, bg=PANEL2):
        return tk.Button(parent, text=label, command=callback, bg=bg, fg=INK,
                         activebackground=ACCENT, activeforeground=BG,
                         relief="flat", bd=0, font=("DejaVu Sans", 10, "bold"),
                         cursor="hand2", padx=16, pady=11)

    def _label(self, parent, value, size=11, color=INK, bold=False, bg=BG):
        return tk.Label(parent, text=value,
                        font=("DejaVu Sans", size, "bold" if bold else "normal"),
                        bg=bg, fg=color, anchor="w", justify="left")

    def _card(self, parent, title, description, action, button_text):
        card = tk.Frame(parent, bg=PANEL, highlightbackground="#59416c", highlightthickness=1)
        self._label(card, title, 16, INK, True, PANEL).pack(anchor="w", padx=20, pady=(18, 9))
        tk.Label(card, text=description, bg=PANEL, fg=MUTED, justify="left",
                 wraplength=290, anchor="w", font=("DejaVu Sans", 10)).pack(
                     anchor="w", padx=20, pady=(0, 14))
        self._button(card, button_text, action).pack(anchor="w", padx=20, pady=(0, 20))
        return card

    def _render_nav(self):
        for child in self.nav.winfo_children():
            child.destroy()
        for page, icon in (("home", "⌂"), ("apps", "◇"), ("files", "▣"),
                           ("notes", "✎"), ("settings", "⚙"), ("about", "ⓘ")):
            selected = page == self.current_page
            button = self._button(self.nav, f" {icon}   {self.t(page)}",
                                  lambda p=page: self.show(p),
                                  PANEL2 if selected else SIDE)
            button.configure(anchor="w", fg=INK if selected else MUTED, pady=14)
            button.pack(fill="x", pady=3)

    def _render_header(self):
        for child in self.header.winfo_children():
            child.destroy()
        self._label(self.header, self.t(self.current_page), 25, INK, True).pack(side="left")
        self.clock_label = self._label(self.header, "", 11, MUTED)
        self.clock_label.pack(side="right")
        self._update_clock_text()

    def _update_clock_text(self):
        if hasattr(self, "clock_label") and self.clock_label.winfo_exists():
            self.clock_label.configure(text=datetime.now().strftime("%d %b %Y  •  %H:%M"))

    def _tick(self):
        self._update_clock_text()
        self.after(1000, self._tick)

    def show(self, page):
        self.current_page = page
        self._render_nav()
        self._render_header()
        for child in self.body.winfo_children():
            child.destroy()
        {
            "home": self.home_page, "apps": self.apps_page, "files": self.files_page,
            "notes": self.notes_page, "settings": self.settings_page,
            "about": self.about_page
        }[page]()

    def home_page(self):
        hero = tk.Frame(self.body, bg=PANEL)
        hero.pack(fill="x", pady=(0, 20))
        self._label(hero, self.t("welcome"), 23, INK, True, PANEL).pack(
            anchor="w", padx=24, pady=(23, 8))
        self._label(hero, self.t("tagline"), 12, MUTED, False, PANEL).pack(
            anchor="w", padx=24, pady=(0, 24))
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x")
        self._card(row, self.t("windows"), self.t("windows_desc"),
                   self.pick_windows, self.t("choose_exe")).pack(
                       side="left", expand=True, fill="both", padx=(0, 8))
        self._card(row, self.t("android"), self.t("android_desc"),
                   self.pick_apk, self.t("choose_apk")).pack(
                       side="left", expand=True, fill="both", padx=(8, 0))
        status = backend_status()
        label = "    •    ".join(f"{name}: {self.t('ready') if status[key] else self.t('missing')}"
                                for name, key in (("Wine", "wine"), ("Waydroid", "waydroid")))
        self._label(self.body, label, 11, MUTED).pack(anchor="w", pady=(23, 0))

    def apps_page(self):
        self._label(self.body, self.t("choose_app"), 13, MUTED).pack(anchor="w", pady=(5, 21))
        actions = tk.Frame(self.body, bg=BG)
        actions.pack(fill="x")
        for label, command in ((self.t("choose_exe"), self.pick_windows),
                               (self.t("choose_apk"), self.pick_apk),
                               (self.t("open_android"), self._open_android)):
            self._button(actions, label, command).pack(side="left", padx=(0, 11))
        status = backend_status()
        self._label(self.body, f"Wine: {'available' if status['wine'] else 'not installed'}\n"
                               f"Waydroid: {'available' if status['waydroid'] else 'not installed'}\n"
                               f"Wayland: {'active' if status['wayland'] else 'inactive'}",
                    12, MUTED).pack(anchor="w", pady=26)

    def pick_windows(self):
        name = filedialog.askopenfilename(title=self.t("choose_exe"),
                filetypes=[("Windows EXE / MSI", "*.exe *.msi"), ("All files", "*")])
        if name:
            self._run_path(Path(name))

    def pick_apk(self):
        name = filedialog.askopenfilename(title=self.t("choose_apk"),
                filetypes=[("Android packages", "*.apk"), ("All files", "*")])
        if name:
            self._run_path(Path(name))

    def _run_path(self, path):
        try:
            plan = make_plan(path)
            prompt = self.t("confirm_install") if plan.kind == "apk-install" else self.t("confirm_run")
            if not messagebox.askyesno("Aevonyr OS", f"{prompt}\n\n{path.name}"):
                return
            execute_plan(plan)
            messagebox.showinfo("Aevonyr OS", self.t("started"))
        except (CompatibilityError, OSError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

    def _open_android(self):
        try:
            open_android()
        except (CompatibilityError, OSError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

    def files_page(self):
        toolbar = tk.Frame(self.body, bg=BG)
        toolbar.pack(fill="x", pady=(0, 14))
        self._button(toolbar, "↑  " + self.t("up"), self._go_up).pack(side="left", padx=(0, 11))
        self._button(toolbar, self.t("browse"), self._browse_dir).pack(side="left")
        self._label(self.body, str(self.current_dir), 10, MUTED).pack(anchor="w", pady=(0, 12))
        frame = tk.Frame(self.body, bg=PANEL, highlightthickness=1, highlightbackground="#514164")
        frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        self.file_list = tk.Listbox(frame, bg=PANEL, fg=INK, selectbackground="#694599",
                                    selectforeground=INK, borderwidth=0, highlightthickness=0,
                                    font=("DejaVu Sans Mono", 11), activestyle="none",
                                    yscrollcommand=scrollbar.set)
        self.file_list.pack(side="left", fill="both", expand=True, padx=13, pady=14)
        scrollbar.configure(command=self.file_list.yview)
        self.file_list.bind("<Double-Button-1>", self._open_selection)
        self.file_list.bind("<Return>", self._open_selection)
        self.entries = []
        try:
            self.entries = sorted(self.current_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            for entry in self.entries[:1500]:
                self.file_list.insert("end", ("[DIR] " if entry.is_dir() else "      ") + entry.name)
        except OSError as exc:
            self.file_list.insert("end", str(exc))

    def _go_up(self):
        self.current_dir = self.current_dir.parent
        self.show("files")

    def _browse_dir(self):
        directory = filedialog.askdirectory(initialdir=str(self.current_dir))
        if directory:
            self.current_dir = Path(directory)
            self.show("files")

    def _open_selection(self, _event=None):
        selected = self.file_list.curselection()
        if not selected or selected[0] >= min(len(self.entries), 1500):
            return
        target = self.entries[selected[0]]
        if target.is_dir():
            self.current_dir = target
            self.show("files")
        elif target.suffix.lower() in (".exe", ".msi", ".apk"):
            self._run_path(target)
        else:
            program = shutil.which("xdg-open")
            if not program:
                messagebox.showerror("Aevonyr OS", "xdg-open is not installed.")
                return
            try:
                subprocess.Popen([program, str(target)], start_new_session=True)
            except OSError as exc:
                messagebox.showerror("Aevonyr OS", str(exc))

    def notes_page(self):
        self._label(self.body, self.t("notes_desc"), 11, MUTED).pack(anchor="w", pady=(0, 12))
        self.note_editor = tk.Text(self.body, bg=PANEL, fg=INK, insertbackground=INK,
                                   relief="flat", bd=12, undo=True, wrap="word",
                                   font=("DejaVu Sans", 12))
        self.note_editor.pack(fill="both", expand=True, pady=(0, 14))
        try:
            self.note_editor.insert("1.0", notes_path().read_text(encoding="utf-8"))
        except OSError:
            pass
        self._button(self.body, self.t("save_notes"), self._save_notes).pack(anchor="e")

    def _save_notes(self):
        try:
            destination = notes_path()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(self.note_editor.get("1.0", "end-1c"), encoding="utf-8")
            messagebox.showinfo("Aevonyr OS", self.t("saved"))
        except OSError as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

    def settings_page(self):
        self._label(self.body, self.t("language"), 17, INK, True).pack(anchor="w", pady=(0, 14))
        self.lang_var = tk.StringVar(value=LANGUAGES[self.language])
        chooser = ttk.Combobox(self.body, textvariable=self.lang_var, state="readonly",
                               values=list(LANGUAGES.values()), width=28,
                               font=("DejaVu Sans", 11))
        chooser.pack(anchor="w", pady=(0, 15))
        chooser.bind("<<ComboboxSelected>>", self._select_language)
        self._label(self.body, self.t("language_note"), 10, MUTED).pack(anchor="w")
        self._button(self.body, self.t("import_language"), self._import_language).pack(anchor="w", pady=(21, 0))

    def _import_language(self):
        path = filedialog.askopenfilename(title=self.t("import_language"), filetypes=[("JSON language pack", "*.json")])
        if not path:
            return
        try:
            code = install_language_pack(path)
            self.language = code
            self.preferences["language"] = code
            save_preferences(self.preferences)
            self.show("settings")
            messagebox.showinfo("Aevonyr OS", self.t("language_installed"))
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

    def _select_language(self, _event):
        for code, name in LANGUAGES.items():
            if name == self.lang_var.get():
                self.language = code
                self.preferences["language"] = code
                try:
                    save_preferences(self.preferences)
                except OSError as exc:
                    messagebox.showerror("Aevonyr OS", str(exc))
                self.show("settings")
                break

    def about_page(self):
        self._label(self.body, "Aevonyr OS 0.5-dev", 22, INK, True).pack(anchor="w", pady=(0, 14))
        self._label(self.body, self.t("about_desc"), 12, MUTED).pack(anchor="w", pady=(0, 14))
        self._label(self.body, f"Python {platform.python_version()}  •  {platform.system()}",
                    11, MUTED).pack(anchor="w")
        self._label(self.body, "github.com/XGAMERSTORE/Aevonyr-OS",
                    11, PINK).pack(anchor="w", pady=16)
