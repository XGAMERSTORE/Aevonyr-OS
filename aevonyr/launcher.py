"""Aevonyr Orbit: keyboard-accessible application overview, hosted by KDE."""
from datetime import datetime
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import shutil
import subprocess
from .apphub import installed_apps, launch_command, start, AppHubError

BG = '#101319'
PANEL = '#1b2029'
INK = '#edf1ed'
MUTED = '#a4afa9'
ACCENT = '#c4ef9c'


def matching_apps(apps, query):
    """Every word must match; an exact name and then a prefix rank first."""
    words = query.casefold().split()
    query = query.strip().casefold()
    matches = [app for app in apps if all(
        word in (app.name + ' ' + app.source).casefold() for word in words)]
    return sorted(matches, key=lambda app: (
        app.name.casefold() != query,
        not app.name.casefold().startswith(query), app.name.casefold()))


class AevonyrLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Aevonyr Orbit')
        self.configure(bg=BG)
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda event: self.destroy())
        self.bind('<Return>', self.launch_selected)
        self.bind('<Down>', lambda event: self.move_selection(1))
        self.bind('<Up>', lambda event: self.move_selection(-1))
        self.all_apps = []
        self.visible_apps = []
        self.result_queue = queue.Queue()
        self.query = tk.StringVar()
        self.query.trace_add('write', lambda *_: self.filter_apps())
        self._build()
        threading.Thread(target=self._load, daemon=True).start()
        self.after(120, self._poll)
        self._tick()

    def _button(self, parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command, relief='flat', bd=0,
                         bg=ACCENT if primary else PANEL,
                         fg=BG if primary else INK, activebackground='#d7f8b9',
                         activeforeground=BG, font=('DejaVu Sans', 11),
                         padx=18, pady=12, cursor='hand2',
                         highlightthickness=1, highlightbackground=PANEL,
                         highlightcolor=ACCENT)

    def _build(self):
        # A compact rail and two spacious columns; no Windows-style start menu.
        rail = tk.Frame(self, bg='#151920', width=88)
        rail.pack(side='left', fill='y')
        rail.pack_propagate(False)
        self._button(rail, '◒', lambda: self.query.set(''), True).pack(padx=12, pady=28)
        tk.Label(rail, text='O\nR\nB\nI\nT', bg='#151920', fg=MUTED,
                 font=('DejaVu Sans', 10), pady=20).pack()
        self._button(rail, 'Esc', self.destroy).pack(side='bottom', padx=8, pady=24)
        main = tk.Frame(self, bg=BG)
        main.pack(fill='both', expand=True, padx=32, pady=24)
        top = tk.Frame(main, bg=BG)
        top.pack(fill='x')
        tk.Label(top, text='A E V O N Y R   /   O R B I T', bg=BG, fg=ACCENT,
                 font=('DejaVu Sans', 11, 'bold')).pack(side='left')
        self.clock = tk.Label(top, bg=BG, fg=MUTED, font=('DejaVu Sans', 11))
        self.clock.pack(side='right')
        content = tk.Frame(main, bg=BG)
        content.pack(fill='both', expand=True, pady=(24, 12))
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)
        left = tk.Frame(content, bg=BG)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 24))
        tk.Label(left, text='Your next\npossibility.', bg=BG, fg=INK,
                 font=('DejaVu Sans', 32, 'bold'), justify='left', anchor='w').pack(fill='x')
        tk.Label(left, text='Find an app. Make something yours.', bg=BG,
                 fg=MUTED, font=('DejaVu Sans', 11), anchor='w').pack(fill='x', pady=(10, 20))
        tk.Label(left, text='SEARCH APPLICATIONS', bg=BG, fg=ACCENT,
                 font=('DejaVu Sans', 9, 'bold'), anchor='w').pack(fill='x', pady=(0, 8))
        self.search = tk.Entry(left, textvariable=self.query, font=('DejaVu Sans', 16),
                              bg=PANEL, fg=INK, insertbackground=ACCENT, relief='flat',
                              highlightthickness=1, highlightbackground='#39463b',
                              highlightcolor=ACCENT)
        self.search.pack(fill='x', ipady=12)
        self.search.focus_set()
        holder = tk.Frame(left, bg=BG)
        holder.pack(fill='both', expand=True, pady=(14, 0))
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Orbit.Vertical.TScrollbar', background='#39463b',
                        troughcolor=BG, bordercolor=BG, arrowcolor=MUTED,
                        lightcolor='#39463b', darkcolor='#39463b', width=12)
        scrollbar = ttk.Scrollbar(holder, style='Orbit.Vertical.TScrollbar')
        scrollbar.pack(side='right', fill='y')
        self.listbox = tk.Listbox(holder, bg=BG, fg=INK, selectbackground=PANEL,
                                 selectforeground=ACCENT, bd=0, highlightthickness=0,
                                 font=('DejaVu Sans', 13), activestyle='none',
                                 exportselection=False, height=5,
                                 yscrollcommand=scrollbar.set)
        self.listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<Double-Button-1>', self.launch_selected)
        self.status = tk.Label(left, text='Discovering installed applications…',
                               bg=BG, fg=MUTED, anchor='w', font=('DejaVu Sans', 10))
        self.status.pack(fill='x', pady=(12, 0))
        right = tk.Frame(content, bg=PANEL)
        right.grid(row=0, column=1, sticky='nsew')
        self.art = tk.Canvas(right, bg=PANEL, height=180, highlightthickness=0)
        self.art.pack(fill='both', expand=True)
        self.art.bind('<Configure>', lambda _: self._draw())
        tk.Label(right, text='A space for your ideas.', bg=PANEL, fg=INK,
                 font=('DejaVu Sans', 15, 'bold')).pack(pady=(0, 10))
        actions = tk.Frame(right, bg=PANEL)
        actions.pack(fill='x', padx=18, pady=(0, 18))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        for index, (title, command) in enumerate([
            ('Files ↗', ['dolphin']), ('Web ↗', ['firefox-esr']),
            ('Pulse ↗', ['aevonyr', '--pulse']), ('App Hub ↗', ['aevonyr', '--app-hub'])]):
            self._button(actions, title, lambda c=command: self.open_command(c),
                         index == 0).grid(row=index // 2, column=index % 2,
                                          sticky='ew', padx=3, pady=3)
        footer = tk.Frame(main, bg=BG)
        footer.pack(fill='x')
        tk.Label(footer, text='↑ ↓  Navigate    Enter  Open    Esc  Return',
                 bg=BG, fg=MUTED, font=('DejaVu Sans', 9)).pack(side='left')
        self._button(footer, 'About Aevonyr', self.show_about).pack(side='right')

    def _draw(self):
        c = self.art
        c.delete('all')
        w, h = c.winfo_width(), c.winfo_height()
        x, y, r = w * .5, h * .5, min(w, h) * .34
        for scale, color in [(1.24, '#29342c'), (1.0, '#51694b'), (.76, '#91b977')]:
            c.create_oval(x-r*scale, y-r*scale, x+r*scale, y+r*scale,
                          outline=color, width=1)
        c.create_arc(x-r, y-r, x+r, y+r, start=32, extent=242,
                     style='arc', outline=ACCENT, width=6)
        c.create_oval(x+r*.74-6, y-r*.67-6, x+r*.74+6, y-r*.67+6,
                      fill=INK, outline='')
        c.create_text(x, y, text='a', fill=INK, font=('DejaVu Sans', 58))

    def _tick(self):
        self.clock.config(text=datetime.now().strftime('%a %d %b   /   %H:%M'))
        self.after(1000, self._tick)

    def _load(self):
        try:
            self.result_queue.put((installed_apps(), ''))
        except Exception as exc:
            self.result_queue.put(([], str(exc)))

    def _poll(self):
        try:
            apps, error = self.result_queue.get_nowait()
        except queue.Empty:
            self.after(120, self._poll)
            return
        self.all_apps = apps
        self.filter_apps()
        if error:
            self.status.configure(text='Could not list apps: ' + error)

    def filter_apps(self):
        if not hasattr(self, 'listbox'):
            return
        self.visible_apps = matching_apps(self.all_apps, self.query.get())
        self.listbox.delete(0, tk.END)
        for app in self.visible_apps:
            self.listbox.insert(tk.END, '  ' + app.name)
        if self.visible_apps:
            self.listbox.selection_set(0)
        self.status.configure(text=(f'{len(self.visible_apps)} applications' if self.visible_apps
                                    else 'No matching applications. Try another search.'))

    def move_selection(self, delta):
        if not self.visible_apps:
            return 'break'
        selected = self.listbox.curselection()
        index = max(0, min(len(self.visible_apps)-1, (selected[0] if selected else 0)+delta))
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)
        return 'break'

    def launch_selected(self, _event=None):
        # Enter on an explicitly focused button must activate that button.
        focused = self.focus_get()
        if isinstance(focused, tk.Button):
            focused.invoke()
            return 'break'
        selected = self.listbox.curselection()
        if not selected:
            return
        try:
            start(launch_command(self.visible_apps[selected[0]]))
        except (AppHubError, OSError) as exc:
            messagebox.showerror('Aevonyr Orbit', str(exc))
            return
        self.destroy()

    def open_command(self, command):
        binary = shutil.which(command[0])
        if not binary:
            messagebox.showerror('Aevonyr Orbit', f'{command[0]} is not installed.')
            return
        try:
            subprocess.Popen([binary, *command[1:]], start_new_session=True)
        except OSError as exc:
            messagebox.showerror('Aevonyr Orbit', str(exc))
            return
        self.destroy()

    def open_hub(self):
        self.open_command(['aevonyr', '--app-hub'])

    def show_about(self):
        messagebox.showinfo('About Aevonyr',
            'Aevonyr Orbit — experimental desktop experience\n\n'
            'Aevonyr design and integration on Debian GNU/Linux.\n'
            'KDE Plasma and KWin provide the desktop and window management.\n'
            'Third-party components retain their names and licenses.\n'
            'Package copyright notices: /usr/share/doc/<package>/copyright')
