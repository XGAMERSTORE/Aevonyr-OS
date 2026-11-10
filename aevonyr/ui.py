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
from .layout import layout_for_width

BG = "#101b1b"  # Midnight library
SIDE = "#0b1415"
PANEL = "#1a2b2b"
PANEL2 = "#294342"
ACCENT = "#e6b86d"  # Warm gilded details
INK = "#f7efdf"  # Paper
MUTED = "#b6c6bc"
PINK = "#c9a1ba"

class AevonyrDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.preferences = load_preferences()
        self.language = self.preferences["language"]
        self.current_page = "home"
        self.current_dir = Path.home()
        self.title("Bookish OS — Desktop Preview")
        self.geometry("1240x780")
        self.minsize(780, 520)
        self.configure(bg=BG)
        self._create_shell()
        self._layout_mode = None
        self.bind("<Configure>", self._on_resize)
        self.show("home")
        self.after(1000, self._tick)

    def t(self, key):
        return tr(key, self.language)

    def _create_shell(self):
        self.sidebar = tk.Frame(self, bg=SIDE, width=225)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="◕  BOOKISH OS", bg=SIDE, fg=INK,
                 font=("DejaVu Serif", 17, "bold"), pady=29).pack(fill="x")
        self.brand = self.sidebar.winfo_children()[0]
        self.nav = tk.Frame(self.sidebar, bg=SIDE)
        self.nav.pack(fill="x", padx=12)
        main = tk.Frame(self, bg=BG)
        main.pack(side="right", fill="both", expand=True)
        self.header = tk.Frame(main, bg=BG, height=80)
        self.header.pack(fill="x", padx=30, pady=(18, 0))
        self.body = tk.Frame(main, bg=BG)
        self.body.pack(fill="both", expand=True, padx=30, pady=(10, 24))

    def _on_resize(self, event):
        if event.widget is not self:
            return
        profile = layout_for_width(event.width)
        if profile["mode"] == self._layout_mode:
            return
        self._layout_mode = profile["mode"]
        self.sidebar.configure(width=profile["sidebar_width"])
        self.brand.configure(text="◕  BOOKISH OS" if profile["label_navigation"] else "◕")
        self.nav.pack_configure(padx=12 if profile["label_navigation"] else 4)
        self.header.pack_configure(padx=profile["content_padding"])
        self.body.pack_configure(padx=profile["content_padding"])
        self._render_nav()

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
        card = tk.Frame(parent, bg=PANEL, highlightbackground="#47615a", highlightthickness=1)
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
            title = f" {icon}   {self.t(page)}" if self._layout_mode != "compact" else icon
            button = self._button(self.nav, title,
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

    def _library_art(self, parent):
        """Draw a decorative bookshelf without network images or external assets."""
        canvas = tk.Canvas(parent, bg=PANEL, height=174, highlightthickness=0)
        canvas.pack(fill="x", padx=24, pady=(0, 16))
        canvas.bind("<Configure>", lambda event: self._draw_books(canvas, event.width))
        return canvas

    @staticmethod
    def _draw_books(canvas, width):
        canvas.delete("all")
        width = max(width, 300)
        canvas.create_rectangle(0, 0, width, 174, fill="#152525", outline="")
        canvas.create_oval(width - 210, -95, width + 80, 195, fill="#253b36", outline="")
        canvas.create_oval(width - 140, -36, width + 10, 114, fill="#d9ad67", outline="")
        canvas.create_oval(width - 129, -25, width - 1, 103, fill="#152525", outline="")
        canvas.create_line(18, 145, width - 20, 145, fill="#d9ad67", width=3)
        colors = ("#9b665c", "#3e7771", "#a78353", "#635d80", "#637f69",
                  "#b08372", "#52768a", "#947c50", "#6d866e", "#805e71")
        x = 25
        for index, color in enumerate(colors):
            height = 68 + (index * 17) % 58
            book_width = 24 + (index % 3) * 4
            if x + book_width > width - 230:
                break
            canvas.create_rectangle(x, 145 - height, x + book_width, 144,
                                    fill=color, outline="#142222", width=2)
            canvas.create_line(x + 6, 151 - height, x + 6, 139,
                               fill="#e5c99a", width=1)
            canvas.create_line(x + 4, 133, x + book_width - 4, 133,
                               fill="#e5c99a", width=1)
            x += book_width + 5
        canvas.create_text(width - 110, 144, text="BOOKISH  /  01",
                           fill="#ead4ac", font=("DejaVu Sans", 10, "bold"))

    def home_page(self):
        hero = tk.Frame(self.body, bg=PANEL, highlightbackground="#47615a",
                        highlightthickness=1)
        hero.pack(fill="x", pady=(0, 18))
        self._label(hero, "✦  THE LIBRARY DESKTOP", 10, ACCENT, True, PANEL).pack(
            anchor="w", padx=24, pady=(20, 8))
        self._label(hero, "Bookish OS", 30, INK, True, PANEL).pack(
            anchor="w", padx=24)
        self._label(hero, self.t("welcome"), 12, MUTED, False, PANEL).pack(
            anchor="w", padx=24, pady=(6, 12))
        self._library_art(hero)
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x")
        self._card(row, "✦  " + self.t("notes"), self.t("notes_desc"),
                   lambda: self.show("notes"), self.t("notes")).pack(
                       side="left", expand=True, fill="both", padx=(0, 8))
        self._card(row, "▣  " + self.t("files"), self.t("tagline"),
                   lambda: self.show("files"), self.t("browse")).pack(
                       side="left", expand=True, fill="both", padx=(8, 0))
        status = backend_status()
        label = "    •    ".join(f"{name}: {self.t('ready') if status[key] else self.t('missing')}"
                                for name, key in (("Wine", "wine"), ("Waydroid", "waydroid")))
        self._label(self.body, label, 10, MUTED).pack(anchor="w", pady=(18, 0))

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
            if not messagebox.askyesno("Bookish OS", f"{prompt}\n\n{path.name}"):
                return
            execute_plan(plan)
            messagebox.showinfo("Bookish OS", self.t("started"))
        except (CompatibilityError, OSError) as exc:
            messagebox.showerror("Bookish OS", str(exc))

    def _open_android(self):
        try:
            open_android()
        except (CompatibilityError, OSError) as exc:
            messagebox.showerror("Bookish OS", str(exc))

    def files_page(self):
        toolbar = tk.Frame(self.body, bg=BG)
        toolbar.pack(fill="x", pady=(0, 14))
        self._button(toolbar, "↑  " + self.t("up"), self._go_up).pack(side="left", padx=(0, 11))
        self._button(toolbar, self.t("browse"), self._browse_dir).pack(side="left")
        self._label(self.body, str(self.current_dir), 10, MUTED).pack(anchor="w", pady=(0, 12))
        frame = tk.Frame(self.body, bg=PANEL, highlightthickness=1, highlightbackground="#47615a")
        frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        self.file_list = tk.Listbox(frame, bg=PANEL, fg=INK, selectbackground="#47615a",
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
                messagebox.showerror("Bookish OS", "xdg-open is not installed.")
                return
            try:
                subprocess.Popen([program, str(target)], start_new_session=True)
            except OSError as exc:
                messagebox.showerror("Bookish OS", str(exc))

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
            messagebox.showinfo("Bookish OS", self.t("saved"))
        except OSError as exc:
            messagebox.showerror("Bookish OS", str(exc))

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
            messagebox.showinfo("Bookish OS", self.t("language_installed"))
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror("Bookish OS", str(exc))

    def _select_language(self, _event):
        for code, name in LANGUAGES.items():
            if name == self.lang_var.get():
                self.language = code
                self.preferences["language"] = code
                try:
                    save_preferences(self.preferences)
                except OSError as exc:
                    messagebox.showerror("Bookish OS", str(exc))
                self.show("settings")
                break

    def about_page(self):
        self._label(self.body, "Bookish OS 0.5-dev", 22, INK, True).pack(anchor="w", pady=(0, 14))
        self._label(self.body, self.t("about_desc"), 12, MUTED).pack(anchor="w", pady=(0, 14))
        self._label(self.body, f"Python {platform.python_version()}  •  {platform.system()}",
                    11, MUTED).pack(anchor="w")
        self._label(self.body, "github.com/XGAMERSTORE/Aevonyr-OS",
                    11, PINK).pack(anchor="w", pady=16)
