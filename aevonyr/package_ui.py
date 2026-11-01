"""Graphical package opening from Dolphin; worker reports errors on the UI thread."""
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from .packages import package_command, install_apk, checked
from .compat import CompatibilityError


def open_package(filename):
    root = tk.Tk()
    root.title('Aevonyr · Applications')
    root.geometry('560x330')
    root.configure(bg='#101319')
    path = Path(filename).expanduser().resolve()
    events = queue.Queue()
    label = tk.Label(root, text=path.name, bg='#101319', fg='#edf1ed',
                     font=('DejaVu Sans', 16, 'bold'), wraplength=510)
    label.pack(padx=24, pady=(24, 12))
    status = tk.Label(root, bg='#101319', fg='#a4afa9', wraplength=510, justify='left')
    status.pack(padx=24, fill='x')
    progress = ttk.Progressbar(root, mode='indeterminate')
    actions = tk.Frame(root, bg='#101319')
    actions.pack(side='bottom', pady=20)

    def button(text, command):
        return tk.Button(actions, text=text, command=command, bg='#c4ef9c',
                         fg='#101319', relief='flat', padx=16, pady=10)

    def work():
        try:
            if path.suffix.lower() == '.apk':
                package = install_apk(path, lambda text: events.put(('status', text)))
                events.put(('installed', package))
            else:
                command = package_command(path)
                # Use a temporary log rather than pipe output that can deadlock.
                import tempfile
                with tempfile.TemporaryFile(mode='w+b') as log:
                    process = subprocess.Popen(list(command), stdout=log, stderr=log,
                                               start_new_session=True)
                    try:
                        code = process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        events.put(('opened', None))
                        return
                    if code:
                        log.seek(0, 2)
                        log.seek(max(0, log.tell() - 2500))
                        raise CompatibilityError(log.read().decode('utf-8', errors='replace') or 'The application could not start.')
                    events.put(('opened', None))
        except (CompatibilityError, OSError, subprocess.SubprocessError) as exc:
            events.put(('error', str(exc)))

    def begin():
        for child in actions.winfo_children(): child.destroy()
        status.config(text='Opening…')
        progress.pack(fill='x', padx=24, pady=16)
        progress.start()
        threading.Thread(target=work, daemon=True).start()

    def setup():
        try:
            subprocess.Popen(['konsole', '-e', '/usr/local/bin/aevonyr-android-setup'], start_new_session=True)
        except OSError as exc:
            status.config(text=str(exc))

    def launch_android(package):
        for child in actions.winfo_children(): child.destroy()
        status.config(text='Opening Android application…')
        def launch():
            try:
                checked([shutil.which('waydroid') or 'waydroid', 'app', 'launch', package], 30)
                events.put(('opened', None))
            except (CompatibilityError, OSError, subprocess.SubprocessError) as exc:
                events.put(('error', str(exc)))
        threading.Thread(target=launch, daemon=True).start()

    def poll():
        try:
            kind, value = events.get_nowait()
        except queue.Empty:
            root.after(100, poll)
            return
        if kind == 'status':
            status.config(text=value)
        elif kind == 'opened':
            root.destroy()
            return
        else:
            progress.stop()
            progress.pack_forget()
            if kind == 'installed':
                status.config(text='Installed. You can also find this application in Orbit.')
                button('Open', lambda: launch_android(value)).pack(side='left', padx=6)
            else:
                status.config(text=value)
                if path.suffix.lower() == '.apk':
                    button('Set up Android', setup).pack(side='left', padx=6)
            button('Close', root.destroy).pack(side='left', padx=6)
        root.after(100, poll)

    if path.suffix.lower() == '.apk':
        status.config(text='Install this Android application? Only install packages from sources you trust.')
        button('Install', begin).pack(side='left', padx=6)
        button('Cancel', root.destroy).pack(side='left', padx=6)
    else:
        root.after(0, begin)
    root.after(100, poll)
    root.mainloop()
    return 0
