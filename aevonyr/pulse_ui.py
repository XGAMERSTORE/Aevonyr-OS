"""Animated Aevonyr Pulse dashboard, embedded in the KDE-hosted app."""
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox
from .pulse import read_pulse

BG = "#100e1c"
PANEL = "#241b37"
INK = "#f8efff"
MUTED = "#bfb1cf"
PURPLE = "#bd88ff"
TEAL = "#70d9d5"
PINK = "#ed91d8"
TRACK = "#49375b"


class PulsePanel(tk.Frame):
    def __init__(self, parent, translate):
        super().__init__(parent, bg=BG)
        self.t = translate
        self.previous_cpu = None
        self.history = []
        self._build()
        self.after(100, self._refresh)

    def _build(self):
        tk.Label(self, text=self.t("pulse_desc"), bg=BG, fg=MUTED,
                 font=("DejaVu Sans", 11), anchor="w").pack(anchor="w", pady=(0, 19))

        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", pady=(0, 16))
        self._values = {}
        self._bars = {}
        for key, color in (("cpu", PURPLE), ("ram", TEAL), ("disk", PINK)):
            cell = tk.Frame(bar, bg=PANEL, highlightbackground="#59416c",
                            highlightthickness=1)
            cell.pack(side="left", expand=True, fill="both", padx=(0, 9))
            tk.Label(cell, text=self.t("pulse_" + key), bg=PANEL, fg=MUTED,
                     font=("DejaVu Sans", 11, "bold")).pack(anchor="w", padx=15, pady=(11, 6))
            value = tk.Label(cell, text="—", bg=PANEL, fg=INK,
                             font=("DejaVu Sans", 25, "bold"))
            value.pack(anchor="w", padx=15, pady=(0, 7))
            self._values[key] = value
            canvas = tk.Canvas(cell, height=8, bg=TRACK, highlightthickness=0, bd=0)
            canvas.pack(fill="x", padx=15, pady=(0, 16))
            canvas.bind("<Configure>", lambda event: self._draw_bars())
            self._bars[key] = (canvas, color)

        self.graph_title = tk.Label(self, text=self.t("pulse_history"), bg=BG,
                                    fg=INK, font=("DejaVu Sans", 14, "bold"))
        self.graph_title.pack(anchor="w", pady=(0, 10))
        self.graph = tk.Canvas(self, bg=PANEL, highlightthickness=1,
                               highlightbackground="#59416c", height=218)
        self.graph.pack(fill="both", expand=True)
        self.graph.bind("<Configure>", lambda _event: self._draw_history())

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", pady=(15, 0))
        self._info = tk.Label(bottom, text=self.t("pulse_loading"), fg=MUTED,
                              bg=BG, font=("DejaVu Sans", 10))
        self._info.pack(side="left")
        tk.Button(bottom, text=self.t("pulse_processes"), command=self.open_monitor,
                  bg="#49345c", fg=INK, relief="flat", bd=0,
                  font=("DejaVu Sans", 10, "bold"), padx=16, pady=11).pack(side="right")

    def _draw_bars(self):
        for key, (canvas, color) in self._bars.items():
            try:
                width = canvas.winfo_width()
                height = canvas.winfo_height()
                percent = getattr(self, "_"+key+"_percent", 0.0)
                canvas.delete("all")
                canvas.create_rectangle(0, 0, max(1, width * percent / 100),
                                        height, fill=color, outline="")
            except tk.TclError:
                return

    def _draw_history(self):
        self.graph.delete("all")
        w, h = self.graph.winfo_width(), self.graph.winfo_height()
        if w < 12 or h < 12:
            return
        for step in (25, 50, 75):
            y = int(h * (1 - step / 100))
            self.graph.create_line(12, y, w - 12, y,
                                   fill="#4c395b", dash=(3, 5))
        samples = self.history
        if not samples:
            return
        for column, key, color in ((0,"cpu",PURPLE),(1,"ram",TEAL)):
            points = []
            for idx, datum in enumerate(samples):
                val = datum[column]
                if val is None:
                    continue
                x = 12 + (w - 24) * (idx / max(1, len(samples)-1))
                y = h - 12 - (h - 24) * (val / 100)
                points.extend((x, y))
            if len(points) >= 4:
                self.graph.create_line(*points, fill=color, width=3, smooth=True)
        self.graph.create_text(16, 15, text="CPU", fill=PURPLE, anchor="w",
                               font=("DejaVu Sans", 10, "bold"))
        self.graph.create_text(76, 15, text="RAM", fill=TEAL, anchor="w",
                               font=("DejaVu Sans", 10, "bold"))

    def _refresh(self):
        if not self.winfo_exists():
            return
        try:
            stats = read_pulse(self.previous_cpu)
        except (OSError, ValueError, IndexError, OverflowError) as exc:
            self._info.configure(text=self.t("pulse_error") + ": " + str(exc)[:90])
        else:
            self.previous_cpu = stats.cpu_counters
            self._cpu_percent = stats.cpu if stats.cpu is not None else 0
            self._ram_percent = stats.ram
            self._disk_percent = stats.disk
            self._values["cpu"].configure(text="—" if stats.cpu is None else f"{stats.cpu:.1f}%")
            self._values["ram"].configure(text=f"{stats.ram:.1f}%")
            self._values["disk"].configure(text=f"{stats.disk:.1f}%")
            self._info.configure(text=(
                f"{self.t('pulse_memory_detail')}: {stats.ram_used_gib:.1f}/{stats.ram_total_gib:.1f} GiB"
                f"   •   {self.t('pulse_disk_detail')}: {stats.disk_used_gib:.1f}/{stats.disk_total_gib:.1f} GiB"
                f"   •   {self.t('pulse_uptime')}: {stats.uptime_hours if stats.uptime_hours is not None else '—'} h"
            ))
            self.history.append((stats.cpu, stats.ram))
            self.history = self.history[-70:]
            self._draw_bars()
            self._draw_history()
        if self.winfo_exists():
            self.after(1500, self._refresh)

    def open_monitor(self):
        executable = shutil.which("plasma-systemmonitor")
        if not executable:
            messagebox.showerror("Aevonyr Pulse", self.t("pulse_monitor_missing"))
            return
        try:
            subprocess.Popen([executable], start_new_session=True)
        except OSError as exc:
            messagebox.showerror("Aevonyr Pulse", str(exc))
