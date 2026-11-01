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


from .orbit_search import matching_apps

class AevonyrLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Aevonyr Orbit')
        self.configure(bg=BG)
        width = min(760, self.winfo_screenwidth() - 48)
        height = min(660, self.winfo_screenheight() - 80)
        self.geometry(f'{width}x{height}+80+48')
        self.minsize(540, 480)
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
        main = tk.Frame(self, bg=BG)
        main.pack(fill='both', expand=True, padx=24, pady=20)
        top = tk.Frame(main, bg=BG)
        top.pack(fill='x', pady=(0, 20))
        tk.Label(top, text='◒  Orbit', bg=BG, fg=INK,
                 font=('DejaVu Sans', 22, 'bold')).pack(side='left')
        self.clock = tk.Label(top, bg=BG, fg=MUTED, font=('DejaVu Sans', 10))
        self.clock.pack(side='right')
        left = main
        tk.Label(main, text='Search your applications', bg=BG, fg=MUTED,
                 anchor='w', font=('DejaVu Sans', 10)).pack(fill='x', pady=(0, 8))
        self.search = tk.Entry(main, textvariable=self.query, font=('DejaVu Sans', 16),
                              bg=PANEL, fg=INK, insertbackground=ACCENT, relief='flat',
                              highlightthickness=1, highlightbackground='#39463b',
                              highlightcolor=ACCENT)
        self.search.pack(fill='x', ipady=10)
        self.search.focus_set()
        tk.Label(main, text='QUICK ACCESS', bg=BG, fg=MUTED,
                 font=('DejaVu Sans', 9), anchor='w').pack(fill='x', pady=(20, 10))
        actions = tk.Frame(main, bg=BG)
        actions.pack(fill='x')
        for index, (title, command) in enumerate([
            ('▣  Files', ['dolphin']), ('◎  Web', ['firefox-esr']),
            ('◴  Pulse', ['aevonyr', '--pulse']), ('⊞  Apps', ['aevonyr', '--app-hub'])]):
            actions.columnconfigure(index, weight=1, uniform='quick')
            self._button(actions, title, lambda c=command: self.open_command(c),
                         index == 0).grid(row=0, column=index, sticky='ew', padx=(0, 6))
        tk.Label(main, text='APPLICATIONS', bg=BG, fg=MUTED,
                 font=('DejaVu Sans', 9), anchor='w').pack(fill='x', pady=(20, 0))
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
        footer = tk.Frame(main, bg=BG)
        footer.pack(fill='x')
        tk.Label(footer, text='↑ ↓  Navigate    Enter  Open    Esc  Return',
                 bg=BG, fg=MUTED, font=('DejaVu Sans', 9)).pack(side='left')
        self._button(footer, 'About Aevonyr', self.show_about).pack(side='right')

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

