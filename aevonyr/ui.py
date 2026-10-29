"""Modern dark desktop-style application for an existing Linux desktop."""
from datetime import datetime
from pathlib import Path
import platform
import queue
import threading
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .compat import CompatibilityError, backend_status, make_plan, execute_plan, open_android
from .config import load_preferences, save_preferences, notes_path
from .i18n import LANGUAGES, tr, install_language_pack
from .network import network_status, open_network_settings
from .diagnostics import diagnose, format_report
from .session import execute_action, SessionError
from .apphub import (
    FEATURED, App, AppHubError, installed_apps, launch_command,
    enable_flathub_command, install_flatpak_command, start,
)
from .restore import RestoreError, is_live_boot, restore_command, backup_command, start_tool
from .onboarding import completed
from .integrations import IntegrationError, available_tools, paired_device_count
from .integrations import start_tool as start_integration

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
        self.title("Aevonyr OS 0.9.0 — Project Eclipse")
        self.geometry("1140x730")
        self.minsize(780, 520)
        self.configure(bg=BG)
        self._create_shell()
        self.show("home")
        self.after(1000, self._tick)
        self.after(750, self._maybe_welcome)

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
                           ("network", "◉"), ("updates", "↻"), ("phone", "▤"), ("system", "◈"), ("restore", "◷"), ("notes", "✎"), ("settings", "⚙"), ("about", "ⓘ")):
            selected = page == self.current_page
            button = self._button(self.nav, f" {icon}   {self.t(page)}",
                                  lambda p=page: self.show(p),
                                  PANEL2 if selected else SIDE)
            button.configure(anchor="w", fg=INK if selected else MUTED, pady=7, font=("DejaVu Sans", 9, "bold"))
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
            "network": self.network_page, "updates": self.updates_page, "phone": self.phone_page, "system": self.system_page, "restore": self.restore_page, "notes": self.notes_page, "settings": self.settings_page,
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
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(16, 0))
        self._button(row, self.t("app_hub"), lambda: self.show("apps")).pack(side="left", padx=(0, 12))
        self._button(row, self.t("restore"), lambda: self.show("restore")).pack(side="left", padx=(0, 9))
        self._button(row, self.t("updates"), lambda: self.show("updates")).pack(side="left")

    def _maybe_welcome(self):
        if not completed():
            self.show_welcome()

    def show_welcome(self):
        if getattr(self, "_wizard", None) is not None:
            try:
                if self._wizard.winfo_exists():
                    self._wizard.lift()
                    self._wizard.focus_force()
                    return
            except tk.TclError:
                pass
        from .welcome import WelcomeWizard
        self._wizard = WelcomeWizard(self)

    def _open_kde_tool(self, key):
        try:
            start_integration(key)
        except (IntegrationError, OSError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

    def updates_page(self):
        self._label(self.body, self.t("updates_desc"), 12, MUTED).pack(anchor="w", pady=(0, 20))
        tools = available_tools()
        self._label(self.body, self.t("updates_manager") + ": " +
                    (self.t("ready") if tools["updates"] else self.t("missing")),
                    13, INK, True).pack(anchor="w", pady=(0, 15))
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x")
        self._card(row, self.t("software_updates"), self.t("software_updates_desc"),
                   lambda: self._open_kde_tool("updates"),
                   self.t("open_updates")).pack(side="left", expand=True, fill="both", padx=(0, 10))
        self._card(row, self.t("firmware_updates"), self.t("firmware_updates_desc"),
                   lambda: self._open_kde_tool("updates"),
                   self.t("open_updates")).pack(side="left", expand=True, fill="both", padx=(10, 0))
        self._label(self.body, self.t("updates_warning"), 10, MUTED).pack(
            anchor="w", pady=(24, 10))
        self._button(self.body, self.t("backup_first"),
                     lambda: self.show("restore")).pack(anchor="w")

    def phone_page(self):
        self._label(self.body, self.t("phone_desc"), 12, MUTED).pack(anchor="w", pady=(0, 22))
        tools = available_tools()
        self._label(self.body, self.t("phone_manager") + ": " +
                    (self.t("ready") if tools["phone"] else self.t("missing")),
                    13, INK, True).pack(anchor="w", pady=(0, 16))
        self._button(self.body, self.t("pair_phone"),
                     lambda: self._open_kde_tool("phone")).pack(anchor="w", pady=(0, 13))
        self.phone_status = self._label(self.body, self.t("checking_devices"), 11, MUTED)
        self.phone_status.pack(anchor="w", pady=(4, 12))
        self._button(self.body, self.t("refresh"), self._scan_devices).pack(anchor="w")
        self._label(self.body, self.t("phone_privacy"), 10, MUTED).pack(anchor="w", pady=(25, 0))
        self._scan_devices()

    def _scan_devices(self):
        if self.current_page != "phone":
            return
        status_queue = queue.Queue(maxsize=1)
        self._phone_queue = status_queue
        self.phone_status.configure(text=self.t("checking_devices"))
        def read_only_probe():
            try:
                status_queue.put(paired_device_count())
            except Exception:
                status_queue.put(None)
        threading.Thread(target=read_only_probe, daemon=True).start()
        self.after(130, lambda: self._poll_devices(status_queue))

    def _poll_devices(self, result_queue):
        if self.current_page != "phone":
            return
        try:
            count = result_queue.get_nowait()
        except queue.Empty:
            self.after(130, lambda: self._poll_devices(result_queue))
            return
        message = self.t("phone_unknown") if count is None else (
            self.t("paired_devices") + ": " + str(count))
        if self.phone_status.winfo_exists():
            self.phone_status.configure(text=message)

    def network_page(self):
        self._label(self.body, self.t("network_desc"), 12, MUTED).pack(anchor="w", pady=(5, 23))
        self._label(self.body, self.t("network_status") + ": " + self.t("network_" + network_status()),
                    16, INK, True).pack(anchor="w", pady=(0, 18))
        self._button(self.body, self.t("network_settings"), self._open_network).pack(anchor="w", pady=(0, 13))
        self._button(self.body, self.t("refresh"), lambda: self.show("network")).pack(anchor="w")

    def _open_network(self):
        try:
            open_network_settings()
        except (RuntimeError, OSError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

    def system_page(self):
        self._label(self.body, self.t("system_desc"), 12, MUTED).pack(anchor="w", pady=(0, 16))
        details = diagnose()
        card = tk.Frame(self.body, bg=PANEL, highlightbackground="#59416c", highlightthickness=1)
        card.pack(fill="both", expand=True, pady=(0, 14))
        self._label(card, format_report(details), 12, INK, False, PANEL).pack(
            anchor="w", padx=20, pady=25)
        self._button(self.body, self.t("copy_diagnostics"),
                     lambda: self._copy_report(format_report(details))).pack(anchor="w")

    def _copy_report(self, report):
        self.clipboard_clear()
        self.clipboard_append(report)
        self.update()
        messagebox.showinfo("Aevonyr OS", self.t("report_copied"))

    def _session_action(self, action):
        if action != "lock" and not messagebox.askyesno(
                "Aevonyr OS", self.t("confirm_action") + " " + self.t("action_" + action) + "?"):
            return
        try:
            execute_action(action)
        except (SessionError, OSError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

    def apps_page(self):
        self._label(self.body, self.t("app_hub_desc"), 10, MUTED).pack(anchor="w", pady=(0, 12))
        actions = tk.Frame(self.body, bg=BG)
        actions.pack(fill="x", pady=(0, 13))
        for text, command in (
            (self.t("choose_exe"), self.pick_windows),
            (self.t("choose_apk"), self.pick_apk),
            (self.t("open_android"), self._open_android),
            (self.t("open_discover"), self._open_discover),
        ):
            self._button(actions, text, command).pack(side="left", padx=(0, 9))

        search_row = tk.Frame(self.body, bg=BG)
        search_row.pack(fill="x")
        self._label(search_row, self.t("search_apps"), 11, INK, True).pack(side="left", padx=(0, 13))
        self.app_search = tk.StringVar()
        tk.Entry(search_row, textvariable=self.app_search, bg=PANEL,
                 fg=INK, insertbackground=INK, relief="flat",
                 font=("DejaVu Sans", 11)).pack(side="left", fill="x", expand=True, ipady=7)
        self.app_search.trace_add("write", lambda *_: self._filter_installed_apps())

        self._label(self.body, self.t("installed_apps"), 12, INK, True).pack(anchor="w", pady=(14, 6))
        listed = tk.Frame(self.body, bg=PANEL)
        listed.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(listed)
        scrollbar.pack(side="right", fill="y")
        self.app_listbox = tk.Listbox(
            listed, bg=PANEL, fg=INK, selectbackground="#7046a2",
            selectforeground=INK, highlightthickness=0, bd=0, height=8,
            activestyle="none", font=("DejaVu Sans", 10),
            yscrollcommand=scrollbar.set,
        )
        self.app_listbox.pack(side="left", fill="both", expand=True, padx=9, pady=8)
        scrollbar.config(command=self.app_listbox.yview)
        self.app_listbox.bind("<Double-Button-1>", lambda _event: self._launch_selected())
        self._all_apps = []
        self._visible_apps = []
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(7, 8))
        self._button(row, self.t("launch_app"), self._launch_selected).pack(side="left", padx=(0, 8))
        self._button(row, self.t("refresh"), lambda: self.show("apps")).pack(side="left")
        self._label(row, self.t("apps_loading"), 9, MUTED).pack(side="right")

        self._label(self.body, self.t("featured_flatpak"), 12, INK, True).pack(anchor="w", pady=(7, 6))
        self.featured_listbox = tk.Listbox(
            self.body, bg=PANEL, fg=INK, selectbackground="#7046a2",
            selectforeground=INK, highlightthickness=0, bd=0,
            font=("DejaVu Sans", 10), height=4, exportselection=False,
        )
        self.featured_listbox.pack(fill="x")
        self._featured = [App("Flatpak", name, identifier) for name, identifier in FEATURED]
        for app in self._featured:
            self.featured_listbox.insert(tk.END, f"  {app.name}  ·  {app.identifier}")
        self.featured_listbox.selection_set(0)
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(9, 2))
        self._button(row, self.t("install_flatpak"), self._install_featured).pack(side="left", padx=(0, 9))
        self._button(row, self.t("enable_flathub"), self._enable_flathub).pack(side="left")

        self._app_result = queue.Queue(maxsize=1)
        load_queue = self._app_result
        def loader():
            try:
                apps = installed_apps()
                load_queue.put((apps, ""))
            except Exception as exc:
                load_queue.put(([], str(exc)))
        threading.Thread(target=loader, daemon=True).start()
        self.after(120, lambda: self._poll_app_result(load_queue))

    def _poll_app_result(self, result_queue):
        if self.current_page != "apps":
            return
        try:
            apps, error = result_queue.get_nowait()
        except queue.Empty:
            self.after(120, lambda: self._poll_app_result(result_queue))
            return
        self._all_apps = apps
        self._filter_installed_apps()
        if error:
            messagebox.showwarning("Aevonyr App Hub", error)

    def _filter_installed_apps(self):
        if not hasattr(self, "app_listbox") or self.current_page != "apps":
            return
        needle = self.app_search.get().casefold().strip()
        self._visible_apps = [app for app in self._all_apps
                              if needle in app.name.casefold() or needle in app.source.casefold()][:350]
        self.app_listbox.delete(0, tk.END)
        for app in self._visible_apps:
            self.app_listbox.insert(tk.END, f"  {app.name}      [{app.source}]")
        if self._visible_apps:
            self.app_listbox.selection_set(0)

    def _launch_selected(self):
        selected = self.app_listbox.curselection()
        if not selected:
            return
        app = self._visible_apps[selected[0]]
        try:
            start(launch_command(app))
        except (AppHubError, OSError) as exc:
            messagebox.showerror("Aevonyr App Hub", str(exc))

    def _install_featured(self):
        selected = self.featured_listbox.curselection()
        if not selected:
            return
        app = self._featured[selected[0]]
        if not messagebox.askyesno("Aevonyr App Hub",
            f"{self.t('install_flatpak')}\n\n{app.name}\n{app.identifier}\n\n"
            + self.t("install_review")):
            return
        try:
            start(install_flatpak_command(app.identifier))
        except (AppHubError, OSError) as exc:
            messagebox.showerror("Aevonyr App Hub", str(exc))

    def _enable_flathub(self):
        if not messagebox.askyesno("Aevonyr App Hub", self.t("flathub_permission")):
            return
        try:
            start(enable_flathub_command())
        except (AppHubError, OSError) as exc:
            messagebox.showerror("Aevonyr App Hub", str(exc))

    def _open_discover(self):
        binary = shutil.which("plasma-discover")
        if not binary:
            messagebox.showerror("Aevonyr App Hub", self.t("discover_missing"))
            return
        try:
            subprocess.Popen([binary], start_new_session=True)
        except OSError as exc:
            messagebox.showerror("Aevonyr App Hub", str(exc))

    def restore_page(self):
        self._label(self.body, self.t("restore_desc"), 12, MUTED).pack(anchor="w", pady=(0, 18))
        live = is_live_boot()
        color = PINK if live else INK
        self._label(self.body,
            self.t("restore_live") if live else self.t("restore_installed"),
            12, color, True).pack(anchor="w", pady=(0, 24))
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x")
        self._card(row, self.t("snapshot_title"), self.t("snapshot_desc"),
            self._open_timeshift, self.t("open_timeshift")).pack(
                side="left", fill="both", expand=True, padx=(0, 8))
        self._card(row, self.t("backup_title"), self.t("backup_desc"),
            self._open_backintime, self.t("open_backintime")).pack(
                side="left", fill="both", expand=True, padx=(8, 0))
        self._label(self.body, self.t("restore_warning"), 11, MUTED).pack(
            anchor="w", pady=(28, 0))

    def _open_timeshift(self):
        if not messagebox.askyesno("Aevonyr OS", self.t("snapshot_warning")):
            return
        try:
            start_tool(restore_command())
        except (RestoreError, OSError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

    def _open_backintime(self):
        if is_live_boot() and not messagebox.askyesno(
                "Aevonyr OS", self.t("live_backup_warning")):
            return
        try:
            start_tool(backup_command())
        except (RestoreError, OSError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc))

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
        self._button(self.body, self.t("open_welcome"), self.show_welcome).pack(
            anchor="w", pady=(15, 0))
        self._button(self.body, self.t("import_language"), self._import_language).pack(anchor="w", pady=(21, 0))
        self._label(self.body, self.t("session_actions"), 17, INK, True).pack(anchor="w", pady=(22, 12))
        actions = tk.Frame(self.body, bg=BG)
        actions.pack(anchor="w")
        for action in ("lock", "logout", "reboot", "poweroff"):
            self._button(actions, self.t("action_" + action),
                         lambda selected=action: self._session_action(selected)).pack(
                side="left", padx=(0, 9))

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
        self._label(self.body, "Aevonyr OS 0.9.0 Linux Live — Project Eclipse", 22, INK, True).pack(anchor="w", pady=(0, 14))
        self._label(self.body, self.t("about_desc"), 12, MUTED).pack(anchor="w", pady=(0, 14))
        self._label(self.body, f"Python {platform.python_version()}  •  {platform.system()}",
                    11, MUTED).pack(anchor="w")
        self._label(self.body, "github.com/XGAMERSTORE/Aevonyr-OS",
                    11, PINK).pack(anchor="w", pady=16)
