import unittest
from collections import namedtuple
from aevonyr.pulse import (
    parse_cpu, calculate_cpu, parse_memory, parse_uptime, read_pulse,
)

DiskUsage = namedtuple("DiskUsage", "total used free")


class PulseTests(unittest.TestCase):
    def test_cpu_counter(self):
        a = parse_cpu("cpu  100 0 50 350 10 0 0 0 0 0\ncpu0 10 0 5 35")
        b = parse_cpu("cpu  140 0 80 390 10 0 0 0 0 0")
        self.assertEqual(a, (510, 360))
        self.assertEqual(b, (620, 400))
        self.assertAlmostEqual(calculate_cpu(a, b), 63.6, places=1)
        self.assertIsNone(calculate_cpu(None, b))
        self.assertIsNone(calculate_cpu(b, b))
        self.assertEqual(calculate_cpu((100, 70), (110, 60)), 100.0)

    def test_invalid_cpu(self):
        with self.assertRaises(ValueError):
            parse_cpu("wrong 1 2 3")
        with self.assertRaises(ValueError):
            parse_cpu("cpu 1")

    def test_memory_uses_available_not_free(self):
        a = "MemTotal: 8388608 kB\nMemFree: 1048576 kB\nMemAvailable: 4194304 kB\n"
        pct, used, total = parse_memory(a)
        self.assertEqual(pct, 50)
        self.assertEqual(used, 4.0)
        self.assertEqual(total, 8.0)
        with self.assertRaises(ValueError):
            parse_memory("MemFree: 100 kB")

    def test_uptime(self):
        self.assertEqual(parse_uptime("7200.18 12000.0"), 2.0)
        self.assertIsNone(parse_uptime("n/a"))
        self.assertIsNone(parse_uptime("-45"))

    def test_collect_read_only(self):
        contents = {
            "/proc/stat":"cpu 300 0 60 600 0 0 0 0\n",
            "/proc/meminfo":"MemTotal: 4194304 kB\nMemAvailable: 2097152 kB\n",
            "/proc/uptime":"3600.3 1234.0\n",
        }
        reader=lambda path: contents[path]
        sample=read_pulse(reader=reader,
                          disk_usage=lambda path: DiskUsage(20*2**30,10*2**30,10*2**30))
        self.assertEqual(sample.ram, 50.0)
        self.assertEqual(sample.disk, 50.0)
        self.assertEqual(sample.ram_total_gib, 4)
        self.assertEqual(sample.cpu_counters, (960,600))
        self.assertEqual(sample.uptime_hours, 1.0)
        self.assertIsNone(sample.cpu)
        sample2=read_pulse(sample.cpu_counters,reader=reader,
                           disk_usage=lambda path: DiskUsage(20*2**30,10*2**30,10*2**30))
        self.assertIsNone(sample2.cpu)

if __name__=="__main__":
    unittest.main()
