"""Aevonyr first-run wizard. No telemetry, no network credentials collected.

This is a Tk window shown on first KDE login. It does not change Linux user
passwords, repartition disks, install packages or enable cloud services.
"""
import tkinter as tk
from tkinter import messagebox
from .onboarding import mark_completed
from .integrations import start_tool, IntegrationError
from .network import network_status

BG = "#100c21"
PANEL = "#261b40"
ACCENT = "#b882ff"
WHITE = "#f7f0ff"
MUTED = "#c6b4d8"

STEPS = (
    ("welcome", "Welcome to Aevonyr", "Vítej v Aevonyr",
     "One System. Two Worlds. Choose how you want to start.",
     "Jeden systém. Dva světy. Nastav si prostředí podle sebe."),
    ("network", "Connect to the internet", "Připoj se k internetu",
     "Use the real Linux network manager. No passwords are stored here.",
     "Použij skutečné síťové nastavení Linuxu. Hesla sem neukládáme."),
    ("apps", "Install useful applications", "Nainstaluj si aplikace",
     "Open Discover for KDE, Linux and Flatpak applications.",
     "Otevři Discover pro aplikace KDE, Linuxu a Flatpaku."),
    ("phone", "Connect your phone", "Propoj telefon",
     "Pair locally with KDE Connect to share files and notifications.",
     "Spáruj zařízení přes KDE Connect pro soubory a oznámení."),
    ("backup", "Protect your files", "Chraň své soubory",
     "Use Back In Time for personal documents and photos. Configure an external backup destination.",
     "Zálohuj dokumenty a fotografie pomocí Back In Time. Vyber externí úložiště."),
    ("finish", "Ready for Aevonyr", "Aevonyr je připravený",
     "The wizard can always be opened again from Aevonyr OS.",
     "Průvodce lze kdykoliv znovu otevřít z Aevonyr OS."),
)

ACTIONS = {
    "network": ("updates", None),  # Handled specially with native network editor.
    "apps": ("updates", None),
    "phone": ("phone", None),
    "backup": ("backup", None),
}


class WelcomeWizard(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        self.step = 0
        self.title("Aevonyr OS — Welcome")
        self.configure(bg=BG)
        self.geometry("790x580")
        self.minsize(680, 510)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._render()
        self.lift()

    @property
    def is_czech(self):
        return str(getattr(self.parent_app, "language", "en")).startswith("cs")

    def msg(self, english, czech):
        return czech if self.is_czech else english

    def label(self, parent, text, size=12, color=WHITE, bold=False):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=("DejaVu Sans", size, "bold" if bold else "normal"),
                        justify="center", wraplength=620)

    def button(self, parent, text, command, accent=False):
        return tk.Button(parent, text=text, command=command,
                         bg=ACCENT if accent else PANEL, fg=BG if accent else WHITE,
                         activebackground="#d6aeff", relief="flat", bd=0,
                         padx=22, pady=12, font=("DejaVu Sans", 11, "bold"))

    def _render(self):
        for child in self.winfo_children():
            child.destroy()
        canvas = tk.Canvas(self, height=177, bg=BG, highlightthickness=0)
        canvas.pack(fill="x", pady=(16, 0))
        canvas.bind("<Configure>", lambda event: self._draw_header(canvas))
        self.label(self, self.msg("STEP", "KROK") + f" {self.step+1} / {len(STEPS)}",
                   10, MUTED).pack(pady=(3, 10))
        progress = tk.Frame(self, bg=PANEL, height=7)
        progress.pack(fill="x", padx=75)
        tk.Frame(progress, bg=ACCENT, height=7,
                 width=int(640*(self.step+1)/len(STEPS))).pack(anchor="w")

        key, en_title, cs_title, en_desc, cs_desc = STEPS[self.step]
        self.label(self, self.msg(en_title, cs_title), 23, WHITE, True).pack(pady=(23, 11))
        self.label(self, self.msg(en_desc, cs_desc), 12, MUTED).pack(padx=50, pady=(0, 16))

        if key == "welcome":
            self._language_selector()
        elif key == "network":
            connectivity = network_status()
            self.label(self, self.msg("Network state:", "Stav sítě:") +
                       " " + connectivity, 10, ACCENT).pack(pady=(0, 10))
            self.button(self, self.msg("Open network settings", "Nastavení připojení"),
                        self._open_network, True).pack()
        elif key in ("apps", "phone", "backup"):
            names = {
                "apps": self.msg("Open Software Store", "Otevřít obchod"),
                "phone": self.msg("Open KDE Connect", "Otevřít KDE Connect"),
                "backup": self.msg("Open Back In Time", "Otevřít zálohování"),
            }
            self.button(self, names[key], lambda: self._launch(key), True).pack(pady=(0, 6))
        else:
            self.label(self, self.msg("Your Aevonyr system awaits.",
                                     "Tvůj Aevonyr systém čeká."), 13, ACCENT).pack()

        self.bottom = tk.Frame(self, bg=BG)
        self.bottom.pack(side="bottom", pady=24)
        self.button(self.bottom, self.msg("Not now", "Nyní ne"), self.destroy).pack(side="left", padx=8)
        if self.step:
            self.button(self.bottom, self.msg("Back", "Zpět"),
                        lambda: self._navigate(-1)).pack(side="left", padx=8)
        self.button(self.bottom,
                    self.msg("Finish", "Dokončit") if key == "finish" else self.msg("Next", "Další"),
                    self._next, True).pack(side="left", padx=8)

    def _draw_header(self, canvas):
        w = canvas.winfo_width()
        canvas.delete("all")
        cx = w / 2
        canvas.create_oval(cx-88, 0, cx+88, 176, fill="#3d225d",
                           outline="#9e5bfa", width=8)
        canvas.create_oval(cx-72, 16, cx+72, 160, fill="#18102b",
                           outline="#653b9b", width=2)
        canvas.create_text(cx, 67, text="AEVONYR", fill=WHITE,
                           font=("DejaVu Sans", 21, "bold"))
        canvas.create_text(cx, 100, text="PROJECT ECLIPSE", fill=ACCENT,
                           font=("DejaVu Sans", 9, "bold"))

    def _language_selector(self):
        row = tk.Frame(self, bg=BG)
        row.pack(pady=6)
        self.label(row, self.msg("Interface language", "Jazyk rozhraní"), 11, MUTED).pack(side="left", padx=9)
        self.language_var = tk.StringVar(value="Čeština" if self.is_czech else "English")
        menu = tk.OptionMenu(row, self.language_var, "English", "Čeština",
                             command=lambda _: self._set_language())
        menu.configure(bg=PANEL, fg=WHITE, activebackground=ACCENT, relief="flat",
                       highlightthickness=0)
        menu["menu"].configure(bg=PANEL, fg=WHITE)
        menu.pack(side="left")

    def _set_language(self):
        code = "cs" if self.language_var.get() == "Čeština" else "en"
        self.parent_app.language = code
        self.parent_app.preferences["language"] = code
        from .config import save_preferences
        try:
            save_preferences(self.parent_app.preferences)
        except OSError as exc:
            messagebox.showerror("Aevonyr OS", str(exc), parent=self)
            return
        self.parent_app.show(self.parent_app.current_page)
        self._render()

    def _open_network(self):
        try:
            self.parent_app._open_network()
        except Exception as exc:
            messagebox.showerror("Aevonyr OS", str(exc), parent=self)

    def _launch(self, kind):
        item = "updates" if kind == "apps" else kind
        try:
            start_tool(item)
        except (IntegrationError, OSError) as exc:
            messagebox.showerror("Aevonyr OS", str(exc), parent=self)

    def _navigate(self, delta):
        self.step = max(0, min(len(STEPS)-1, self.step + delta))
        self._render()

    def _next(self):
        if self.step < len(STEPS) - 1:
            self._navigate(1)
            return
        try:
            mark_completed()
        except OSError as exc:
            messagebox.showerror("Aevonyr OS",
                                 self.msg("Could not save completion: ",
                                          "Nelze uložit dokončení: ") + str(exc),
                                 parent=self)
            return
        self.destroy()
