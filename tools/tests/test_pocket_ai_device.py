from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "pocket_ai_device.py"
SPEC = importlib.util.spec_from_file_location("pocket_ai_device", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
device = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = device
SPEC.loader.exec_module(device)


class DeviceToolTests(unittest.TestCase):
    def test_loads_pinned_esp32c3_artifact(self) -> None:
        artifact = device.load_artifact(device.DEFAULT_MANIFEST)
        self.assertEqual(artifact["chip"], "esp32c3")
        self.assertEqual(artifact["flash_offset"], "0x0")
        self.assertEqual(len(artifact["sha256"]), 64)

    def test_sha256_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.bin"
            path.write_bytes(b"pocket-ai-test")
            self.assertEqual(
                device.sha256_file(path), hashlib.sha256(b"pocket-ai-test").hexdigest()
            )

    def test_verify_rejects_wrong_size_before_digest(self) -> None:
        artifact = device.load_artifact(device.DEFAULT_MANIFEST)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "wrong.bin"
            path.write_bytes(b"\xe9")
            with self.assertRaisesRegex(device.DeviceToolError, "size mismatch"):
                device.verify_image(path, artifact)

    def test_verify_rejects_same_size_bad_digest(self) -> None:
        artifact = {
            "size_bytes": 32,
            "sha256": "0" * 64,
            "partition_table_offset": "0x8",
            "application_offset": "0x10",
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "wrong-digest.bin"
            path.write_bytes(b"\xe9" + b"\xff" * 31)
            with self.assertRaisesRegex(device.DeviceToolError, "SHA-256 mismatch"):
                device.verify_image(path, artifact)

    def test_verify_rejects_bad_structural_marker_after_digest(self) -> None:
        payload = bytearray(b"\xff" * 32)
        payload[0] = 0xE9
        payload[16] = 0xE9
        artifact = {
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "partition_table_offset": "0x8",
            "application_offset": "0x10",
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad-marker.bin"
            path.write_bytes(payload)
            with self.assertRaisesRegex(device.DeviceToolError, "partition table"):
                device.verify_image(path, artifact)

    def test_flash_command_is_explicit_and_uses_offset_zero(self) -> None:
        artifact = device.load_artifact(device.DEFAULT_MANIFEST)
        command = device.esptool_command(
            artifact,
            "/dev/test-port",
            ["write-flash", artifact["flash_offset"], "/tmp/image.bin"],
            baud=460800,
        )
        self.assertIn("esp32c3", command)
        self.assertIn("/dev/test-port", command)
        self.assertEqual(command[-3:], ["write-flash", "0x0", "/tmp/image.bin"])

    def test_noninteractive_confirmations_are_refused(self) -> None:
        with mock.patch.object(sys.stdin, "isatty", return_value=False), redirect_stdout(
            io.StringIO()
        ):
            with self.assertRaisesRegex(device.DeviceToolError, "confirmation required"):
                device.confirm_flash("/dev/test-port", assume_yes=False)
            with self.assertRaisesRegex(device.DeviceToolError, "confirmation required"):
                device.confirm_erase("/dev/test-port", assume_yes=False)

    def test_noninteractive_main_flash_never_runs_subprocess(self) -> None:
        with (
            mock.patch.object(device, "resolve_image", return_value=Path("image.bin")),
            mock.patch.object(device, "verify_image", return_value="ab" * 32),
            mock.patch.object(device, "run_command") as run_command,
            mock.patch.object(sys.stdin, "isatty", return_value=False),
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            result = device.main(
                ["flash", "--port", "/dev/test-port", "--image", "image.bin"]
            )
        self.assertEqual(result, 2)
        run_command.assert_not_called()

    def test_manifest_rejects_path_filename_and_bad_offsets(self) -> None:
        base = {
            "artifact": {
                "filename": "../escape.bin",
                "download_url": "https://example.invalid/image.bin",
                "size_bytes": 100,
                "sha256": "00" * 32,
                "chip": "esp32c3",
                "flash_offset": "0x0",
                "partition_table_offset": "0x8",
                "application_offset": "0x10",
            }
        }
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "manifest.json"
            manifest.write_text(json.dumps(base), encoding="utf-8")
            with self.assertRaisesRegex(device.DeviceToolError, "basename"):
                device.load_artifact(manifest)

            base["artifact"]["filename"] = "safe.bin"
            base["artifact"]["partition_table_offset"] = "not-an-offset"
            manifest.write_text(json.dumps(base), encoding="utf-8")
            with self.assertRaisesRegex(device.DeviceToolError, "offset metadata"):
                device.load_artifact(manifest)


if __name__ == "__main__":
    unittest.main()
