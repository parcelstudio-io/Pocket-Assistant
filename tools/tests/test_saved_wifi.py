from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "saved_wifi.py"
spec = importlib.util.spec_from_file_location("saved_wifi", TOOL)
assert spec is not None and spec.loader is not None
saved_wifi = importlib.util.module_from_spec(spec)
sys.modules["saved_wifi"] = saved_wifi
spec.loader.exec_module(saved_wifi)


class SummarizeTests(unittest.TestCase):
    def test_hides_every_password_and_keeps_ssid(self) -> None:
        rows = [
            {"namespace": "wifi", "key": "ssid", "data": "GuestNet"},
            {"namespace": "wifi", "key": "password", "data": "not-a-real-password"},
            {"namespace": "wifi", "key": "ssid1", "data": "Second"},
            {"namespace": "wifi", "key": "password1", "data": ""},
            {"namespace": "wifi", "key": "max_tx_power", "data": 34},
            {"namespace": "phy", "key": "cal_data", "data": "ignored"},
        ]
        lines = saved_wifi.summarize(rows)
        self.assertIn("ssid = GuestNet", lines)
        self.assertIn("password = <hidden, set>", lines)
        self.assertIn("password1 = <hidden, empty>", lines)
        self.assertIn("max_tx_power = 34", lines)
        self.assertFalse(any("not-a-real-password" in line for line in lines))
        self.assertFalse(any("cal_data" in line for line in lines))

    def test_reports_no_saved_network(self) -> None:
        self.assertEqual(saved_wifi.summarize([]), ["No saved Wi-Fi network"])
        self.assertEqual(
            saved_wifi.summarize([{"namespace": "wifi", "key": "max_tx_power", "data": 34}]),
            ["max_tx_power = 34", "No saved Wi-Fi network"])


if __name__ == "__main__":
    unittest.main()
