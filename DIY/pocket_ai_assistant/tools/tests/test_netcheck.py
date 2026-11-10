from __future__ import annotations

import copy
import importlib.util
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "netcheck.py"
SPEC = importlib.util.spec_from_file_location("netcheck", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
netcheck = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(netcheck)


class NetcheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.nets = copy.deepcopy(netcheck.NETS)

    def run_check(self) -> tuple[int, str]:
        with (
            mock.patch.object(netcheck, "NETS", self.nets),
            redirect_stdout(io.StringIO()) as stdout,
            redirect_stderr(io.StringIO()),
        ):
            status = netcheck.main()
        return status, stdout.getvalue()

    def assert_bridge_rejected(self) -> None:
        status, output = self.run_check()
        self.assertEqual(status, 1)
        self.assertIn("FAIL  speaker has two distinct floating nets", output)

    def test_current_logical_harness_passes(self) -> None:
        status, output = self.run_check()
        self.assertEqual(status, 0)
        self.assertIn("18/18 static checks passed", output)
        self.assertIn("qualification: NOT CHECKED", output)

    def test_bridge_validation_does_not_depend_on_net_names(self) -> None:
        self.nets["AUDIO_POSITIVE"] = self.nets.pop("SPK_P")
        self.nets["AUDIO_NEGATIVE"] = self.nets.pop("SPK_N")
        self.assertEqual(self.run_check()[0], 0)

    def test_rejects_duplicate_peripheral_endpoint_across_nets(self) -> None:
        self.nets["I2C_SCL"].append(("oled", "SDA"))
        status, output = self.run_check()
        self.assertEqual(status, 1)
        self.assertIn("FAIL  every component/pin endpoint", output)
        self.assertIn("oled.SDA (I2C_SDA, I2C_SCL)", output)

    def test_rejects_duplicate_endpoint_within_one_net(self) -> None:
        self.nets["GND"].append(("amp", "GND"))
        status, output = self.run_check()
        self.assertEqual(status, 1)
        self.assertIn("amp.GND (GND, GND)", output)

    def test_rejects_missing_speaker_net(self) -> None:
        del self.nets["SPK_N"]
        self.assert_bridge_rejected()

    def test_rejects_both_speaker_nets_missing(self) -> None:
        del self.nets["SPK_P"]
        del self.nets["SPK_N"]
        self.assert_bridge_rejected()

    def test_rejects_missing_amplifier_output(self) -> None:
        self.nets["SPK_N"].remove(("amp", "OUT-"))
        self.assert_bridge_rejected()

    def test_rejects_reversed_speaker_polarity(self) -> None:
        self.nets["SPK_P"] = [("amp", "OUT+"), ("speaker", "-")]
        self.nets["SPK_N"] = [("amp", "OUT-"), ("speaker", "+")]
        self.assert_bridge_rejected()

    def test_rejects_both_speaker_leads_on_one_net(self) -> None:
        self.nets["SPK_P"].extend(self.nets.pop("SPK_N"))
        self.assert_bridge_rejected()

    def test_rejects_unexpected_third_speaker_endpoint(self) -> None:
        self.nets["EXTRA_SPEAKER"] = [("speaker", "extra")]
        self.assert_bridge_rejected()

    def test_rejects_direct_speaker_connection_to_frame(self) -> None:
        self.nets["SPK_P"].append(("frame", "brass"))
        self.assert_bridge_rejected()

    def test_rejects_speaker_lead_moved_to_ground(self) -> None:
        self.nets["SPK_N"].remove(("speaker", "-"))
        self.nets["GND"].append(("speaker", "-"))
        self.assert_bridge_rejected()

    def test_rejects_amplifier_output_short_via_duplicate_endpoint(self) -> None:
        self.nets["SPK_P"].append(("amp", "OUT-"))
        self.assert_bridge_rejected()

    def test_rejects_ground_short_via_duplicate_amplifier_endpoint(self) -> None:
        self.nets["GND"].append(("amp", "OUT+"))
        self.assert_bridge_rejected()

    def test_rejects_ground_short_via_duplicate_speaker_endpoint(self) -> None:
        self.nets["GND"].append(("speaker", "-"))
        self.assert_bridge_rejected()


if __name__ == "__main__":
    unittest.main()
