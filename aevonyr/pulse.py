"""Aevonyr Pulse: local Linux resource telemetry (read-only).

/proc/stat CPU counters contain cumulative jiffies; utilization needs two
samples. /proc/meminfo MemAvailable, not MemFree, is used for meaningful
RAM utilization. No network, analytics, elevation or personal data collection.
"""
from dataclasses import dataclass
from pathlib import Path
import shutil


@dataclass(frozen=True)
class PulseSample:
    cpu: float | None
    ram: float
    ram_used_gib: float
    ram_total_gib: float
    disk: float
    disk_used_gib: float
    disk_total_gib: float
    uptime_hours: float | None
    cpu_counters: tuple[int, int]


def parse_cpu(text):
    first = text.splitlines()[0].split()
    if first[0] != "cpu" or len(first) < 5:
        raise ValueError("Invalid /proc/stat CPU line")
    fields = [int(n) for n in first[1:9]]
    if len(fields) < 4:
        raise ValueError("Incomplete /proc/stat CPU line")
    total = sum(fields)
    idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
    return total, idle


def calculate_cpu(previous, current):
    if previous is None:
        return None
    total = current[0] - previous[0]
    idle = current[1] - previous[1]
    if total <= 0:
        return None
    return round(max(0.0, min(100.0, (total - idle) * 100.0 / total)), 1)


def parse_memory(text):
    values = {}
    for line in text.splitlines():
        tokens = line.split(":")
        if len(tokens) != 2:
            continue
        key, number = tokens
        try:
            values[key] = int(number.strip().split()[0])
        except (ValueError, IndexError):
            continue
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", values.get("MemFree", 0))
    if total <= 0:
        raise ValueError("Linux RAM metrics are unavailable")
    used = max(0, min(total, total - available))
    percent = round(100.0 * used / total, 1)
    return percent, round(used / 1048576, 2), round(total / 1048576, 2)


def parse_uptime(text):
    try:
        seconds = float(text.split()[0])
    except (IndexError, ValueError):
        return None
    return round(seconds / 3600, 1) if seconds >= 0 else None


def read_pulse(previous=None, reader=None, disk_usage=shutil.disk_usage, disk_path="/"):
    if reader is None:
        reader = lambda name: Path(name).read_text(encoding="utf-8")
    counters = parse_cpu(reader("/proc/stat"))
    ram_pct, ram_used, ram_total = parse_memory(reader("/proc/meminfo"))
    usage = disk_usage(disk_path)
    used = usage.total - usage.free
    disk_pct = round(100 * used / usage.total, 1) if usage.total else 0.0
    try:
        uptime = parse_uptime(reader("/proc/uptime"))
    except OSError:
        uptime = None
    return PulseSample(
        cpu=calculate_cpu(previous, counters),
        ram=ram_pct,
        ram_used_gib=ram_used,
        ram_total_gib=ram_total,
        disk=disk_pct,
        disk_used_gib=round(used / 1073741824, 2),
        disk_total_gib=round(usage.total / 1073741824, 2),
        uptime_hours=uptime,
        cpu_counters=counters,
    )
