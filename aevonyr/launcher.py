"""Fullscreen Aevonyr application launcher running inside KDE, not a compositor."""
import queue
import threading
import tkinter as tk
from tkinter import messagebox
from .apphub import installed_apps, launch_command, start, AppHubError

BG="#0b0919"; PANEL="#211630"; INK="#f8efff"; MUTED="#bfa9d3"; ACCENT="#bc86ff"

class AevonyrLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aevonyr Launcher")
        self.configure(bg=BG)
        self.attributes("-fullscreen",True)
        self.bind("<Escape>",lambda event:self.destroy())
        self.bind("<Return>",self.launch_selected)
        self.all_apps=[];self.visible_apps=[]
        self.result_queue=queue.Queue()
        self.query=tk.StringVar()
        self.query.trace_add("write",lambda *_:self.filter_apps())
        self._build()
        threading.Thread(target=self._load,daemon=True).start()
        self.after(120,self._poll)

    def _build(self):
        canvas=tk.Canvas(self,bg=BG,height=240,highlightthickness=0)
        canvas.pack(fill="x")
        canvas.bind("<Configure>",lambda event:self._draw(canvas))
        panel=tk.Frame(self,bg=BG)
        panel.pack(fill="both",expand=True,padx=84,pady=(12,35))
        search=tk.Entry(panel,textvariable=self.query,font=("DejaVu Sans",18),
                        bg=PANEL,fg=INK,insertbackground=ACCENT,relief="flat",
                        highlightthickness=1,highlightbackground="#5e3b88",
                        highlightcolor=ACCENT)
        search.pack(fill="x",ipady=16,pady=(0,17))
        search.focus_set()
        holder=tk.Frame(panel,bg=PANEL)
        holder.pack(fill="both",expand=True)
        bar=tk.Scrollbar(holder);bar.pack(side="right",fill="y")
        self.listbox=tk.Listbox(holder,bg=PANEL,fg=INK,selectbackground="#6d3b9c",
                                selectforeground=INK,bd=0,highlightthickness=0,
                                font=("DejaVu Sans",14),activestyle="none",
                                yscrollcommand=bar.set)
        self.listbox.pack(side="left",fill="both",expand=True,padx=16,pady=12)
        bar.configure(command=self.listbox.yview)
        self.listbox.bind("<Double-Button-1>",self.launch_selected)
        self.status=tk.Label(panel,text="Loading installed Linux, Flatpak and Android apps…",
                             bg=BG,fg=MUTED,font=("DejaVu Sans",11),anchor="w")
        self.status.pack(fill="x",pady=13)
        controls=tk.Frame(panel,bg=BG);controls.pack(fill="x")
        tk.Button(controls,text="Aevonyr App Hub",command=self.open_hub,
                  bg=PANEL,fg=INK,relief="flat",padx=23,pady=11).pack(side="left",padx=(0,12))
        tk.Button(controls,text="Close [Esc]",command=self.destroy,
                  bg=PANEL,fg=INK,relief="flat",padx=23,pady=11).pack(side="left")

    def _draw(self,canvas):
        width=canvas.winfo_width();middle=width//2
        canvas.delete("all")
        canvas.create_oval(middle-145,1,middle+145,291,fill="#30204b",
                           outline="#ba6cfe",width=7)
        canvas.create_oval(middle-123,23,middle+123,269,fill="#110b24",
                           outline="#7742ae",width=3)
        canvas.create_text(middle,95,text="AEVONYR",fill=INK,
                           font=("DejaVu Sans",35,"bold"))
        canvas.create_text(middle,142,text="ONE SYSTEM. TWO WORLDS.",fill="#d6adf6",
                           font=("DejaVu Sans",11,"bold"))
        canvas.create_text(middle,202,text="UNIVERSAL LAUNCHER",fill=MUTED,
                           font=("DejaVu Sans",11))

    def _load(self):
        try:self.result_queue.put((installed_apps(),""))
        except Exception as exc:self.result_queue.put(([],str(exc)))

    def _poll(self):
        try:apps,error=self.result_queue.get_nowait()
        except queue.Empty:
            if self.winfo_exists():self.after(120,self._poll)
            return
        self.all_apps=apps
        self.filter_apps()
        self.status.configure(text=f"{len(apps)} installed apps. Search and press Enter." if not error
                              else f"Could not list apps: {error}")

    def filter_apps(self):
        if not hasattr(self,"listbox"):return
        query=self.query.get().casefold().strip()
        self.visible_apps=[a for a in self.all_apps
                           if query in a.name.casefold() or query in a.source.casefold()][:400]
        self.listbox.delete(0,tk.END)
        for app in self.visible_apps:self.listbox.insert(tk.END,f"  {app.name}     [{app.source}]")
        if self.visible_apps:self.listbox.selection_set(0)

    def launch_selected(self,_event=None):
        selected=self.listbox.curselection()
        if not selected:return
        app=self.visible_apps[selected[0]]
        try:start(launch_command(app))
        except (AppHubError,OSError) as exc:
            messagebox.showerror("Aevonyr Launcher",str(exc));return
        self.destroy()

    def open_hub(self):
        import shutil,subprocess
        command=shutil.which("aevonyr")
        if not command:
            messagebox.showerror("Aevonyr Launcher","Aevonyr OS app not installed.")
            return
        subprocess.Popen([command,"--app-hub"],start_new_session=True)
        self.destroy()
