from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

FIRMWARE = Path(__file__).resolve().parents[2] / "firmware"


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, FIRMWARE / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


verify = load_script("verify_source_build")
record = load_script("record_source_build")


class BuildCliTests(unittest.TestCase):
    def test_rejects_conflicting_modes_before_touching_checkout(self) -> None:
        for modes in (("--assistant", "--diagnostics"), ("--diagnostics", "--assistant")):
            with self.subTest(modes=modes):
                result = subprocess.run(
                    ["bash", str(FIRMWARE / "scripts/build.sh"), *modes],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("mutually exclusive", result.stderr)


class PrepareCheckoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.firmware = root / "firmware"
        upstream = root / "upstream"
        upstream.mkdir()
        self.git(upstream, "init", "--quiet")
        original = {}
        for name in ("main/CMakeLists.txt", "main/Kconfig.projbuild", "main/application.cc",
                     "main/main.cc", "main/mcp_server.cc", "dependencies.lock",
                     "partitions/v2/default.csv"):
            path = upstream / name
            path.parent.mkdir(parents=True, exist_ok=True)
            original[name] = f"original {name}\n"
            path.write_text(original[name])
        self.git(upstream, "add", "--all")
        self.git(upstream, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "--quiet", "-m", "test fixture")
        self.git(upstream, "tag", "fixture-v1")
        commit = self.git(upstream, "rev-parse", "HEAD").strip()
        for name in original:
            if name != "dependencies.lock":
                (upstream / name).write_text(original[name] + "patched\n")
        patch = self.git(upstream, "diff", "--no-ext-diff", "--binary")
        patch += ("diff --git a/main/new_helper.cc b/main/new_helper.cc\n"
                  "new file mode 100644\n--- /dev/null\n+++ b/main/new_helper.cc\n"
                  "@@ -0,0 +1 @@\n+// added helper\n")
        for name, content in original.items():
            (upstream / name).write_text(content)
        for name in ("scripts", "patches", "partitions", "src/boards/pocket-wall-e-c3"):
            (self.firmware / name).mkdir(parents=True)
        shutil.copyfile(FIRMWARE / "scripts/prepare.sh", self.firmware / "scripts/prepare.sh")
        (self.firmware / "patches/xiaozhi-v2.4.0-pocket-wall-e-c3.patch").write_text(patch)
        for name in ("config.h", "config.json", "pocket_wall_e_c3.cc"):
            (self.firmware / "src/boards/pocket-wall-e-c3" / name).write_text(f"fixture {name}\n")
        (self.firmware / "partitions/pocket-ai-4m.csv").write_text("fixture partition\n")
        shutil.copyfile(upstream / "dependencies.lock", self.firmware / "dependencies.lock")
        (self.firmware / "versions.env").write_text(
            f"XIAOZHI_REPOSITORY={upstream}\nXIAOZHI_REF=fixture-v1\nXIAOZHI_COMMIT={commit}\n")
        self.checkout = self.firmware / ".work/xiaozhi-esp32"
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def git(self, root: Path, *arguments: str) -> str:
        return subprocess.check_output(["git", "-C", str(root), *arguments],
                                       text=True, stderr=subprocess.STDOUT)

    def prepare(self, *arguments: str):
        return subprocess.run(["bash", str(self.firmware / "scripts/prepare.sh"), *arguments],
                              capture_output=True, text=True, check=False)

    def test_reuses_full_patch_including_additional_tracked_and_new_files(self) -> None:
        result = self.prepare("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("overlay is ready", result.stdout)
        self.assertTrue((self.checkout / "main/new_helper.cc").is_file())
        self.assertEqual(list((self.firmware / ".work").glob("archive.*")), [])

    def test_refresh_preserves_untracked_user_notes_in_archive(self) -> None:
        (self.checkout / "my-lab-notes.txt").write_text("keep this experiment\n")
        result = self.prepare("--refresh")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        archives = list((self.firmware / ".work").glob("archive.*"))
        self.assertEqual(len(archives), 1)
        self.assertEqual((archives[0] / "xiaozhi-esp32/my-lab-notes.txt").read_text(),
                         "keep this experiment\n")
        self.assertTrue((archives[0] / "overlay.sha256").is_file())
        self.assertEqual(self.prepare("--check").returncode, 0)

    def test_modified_tracked_file_is_rejected_and_preserved(self) -> None:
        source = self.checkout / "main/application.cc"
        source.write_text(source.read_text() + "user experiment\n")
        result = self.prepare("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("user experiment", source.read_text())
        result = self.prepare("--refresh")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        archive = next((self.firmware / ".work").glob("archive.*"))
        self.assertIn("user experiment", (archive / "xiaozhi-esp32/main/application.cc").read_text())
        self.assertNotIn("user experiment", source.read_text())


class SourceBuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.firmware = Path(self.temporary.name) / "firmware"
        self.build = self.firmware / ".work" / "xiaozhi-esp32" / "build"
        self.dist = self.firmware / "dist"
        self.build.mkdir(parents=True)
        self.dist.mkdir()
        for name in verify.required_input_names(FIRMWARE):
            destination = self.firmware / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(FIRMWARE / name, destination)
        self.versions = verify.read_versions(self.firmware)
        self.filename = (f"{self.versions['POCKET_AI_BOARD_TYPE']}-{self.versions['XIAOZHI_REF']}"
                         f"-idf-{self.versions['ESP_IDF_REF']}.bin")
        payload = bytearray(b"\xff" * 0x10010)
        payload[0] = 0xE9
        payload[0x8000:0x8002] = b"\xaa\x50"
        payload[0x10000] = 0xE9
        self.image = self.build / "merged-binary.bin"
        self.image.write_bytes(payload)
        (self.dist / self.filename).write_bytes(payload)
        self.sdkconfig = self.build.parent / "sdkconfig"
        self.sdkconfig.write_text(
            'CONFIG_IDF_TARGET="esp32c3"\n'
            'CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y\n'
            'CONFIG_BOARD_TYPE_POCKET_WALL_E_C3=y\n'
            'CONFIG_POCKET_AI_BENCH_DIAGNOSTICS=y\n'
            '# CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER is not set\n'
        )
        self.toolchain = {key: "test-tool-1.0" for key in verify.TOOLCHAIN_KEYS}
        self.manifest_path = self.make_record()
        self.manifest = json.loads(self.manifest_path.read_text())

    def fake_command(self, command: list[str]) -> str:
        if command[3:] == ["rev-parse", "HEAD"]:
            if command[2] == str(self.build.parent):
                return self.versions["XIAOZHI_COMMIT"]
            return self.versions["ESP_IDF_COMMIT"]
        if command[3:] == ["status", "--porcelain=v1", "--untracked-files=no"]:
            return ""
        self.fail(f"unexpected metadata command: {command}")

    def make_record(self, mode: str = "diagnostics", fingerprint: str | None = None) -> Path:
        if fingerprint is None:
            fingerprint = verify.input_fingerprint(verify.input_hashes(self.firmware))
        with (
            mock.patch.object(record, "collect_toolchain", return_value=self.toolchain),
            mock.patch.object(record, "command_output", side_effect=self.fake_command),
            mock.patch.dict(os.environ, {"IDF_PATH": str(self.firmware / "test-sdk"),
                                        "SOURCE_DATE_EPOCH": self.versions["XIAOZHI_SOURCE_DATE_EPOCH"]}),
        ):
            return record.record_source_build(
                self.firmware, self.build, self.dist, mode,
                expected_input_fingerprint=fingerprint,
            )

    def save_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest))

    def verify_record(self):
        return verify.verify_source_build(self.manifest_path, self.build, self.dist,
                                           firmware_dir=self.firmware)

    def test_successful_record_and_verify_without_hardware_claim(self) -> None:
        path, size, digest = self.verify_record()
        self.assertEqual(path, self.dist / self.filename)
        self.assertEqual(size, self.image.stat().st_size)
        self.assertEqual(digest, verify.sha256_file(self.image))
        self.assertEqual(self.manifest["toolchain"], self.toolchain)
        self.assertEqual(self.manifest["validation"], {
            "clean_builds_compared": 0, "outputs_identical": None, "hardware_tested": False})

    def test_assistant_mode_records_only_matching_effective_config(self) -> None:
        text = self.sdkconfig.read_text().replace(
            "CONFIG_POCKET_AI_BENCH_DIAGNOSTICS=y",
            "# CONFIG_POCKET_AI_BENCH_DIAGNOSTICS is not set")
        self.sdkconfig.write_text(text)
        self.make_record("assistant")
        self.assertEqual(verify.load_manifest(self.manifest_path, self.firmware)["build_mode"],
                         "assistant")
        self.verify_record()

    def test_selects_local_manifest_then_reference_when_absent(self) -> None:
        self.assertEqual(verify.select_manifest(self.firmware, self.dist), self.manifest_path)
        self.manifest_path.unlink()
        self.assertEqual(verify.select_manifest(self.firmware, self.dist),
                         self.firmware / "source-build.json")

    def test_rejects_modified_source_input(self) -> None:
        source = self.firmware / "src/boards/pocket-wall-e-c3/config.h"
        source.write_text(source.read_text() + "\n// changed after compilation\n")
        with self.assertRaisesRegex(verify.VerificationError, "local input .*SHA-256 mismatch"):
            self.verify_record()

    def test_rejects_missing_required_source_file(self) -> None:
        (self.firmware / "src/boards/pocket-wall-e-c3/config.h").unlink()
        with self.assertRaisesRegex(verify.VerificationError, "missing local input"):
            self.verify_record()

    def test_rejects_omitted_required_input_hash(self) -> None:
        del self.manifest["local_inputs"]["sdkconfig.defaults"]
        self.save_manifest()
        with self.assertRaisesRegex(verify.VerificationError, "required input set"):
            self.verify_record()

    def test_rejects_added_unrecorded_source_input(self) -> None:
        (self.firmware / "src/boards/pocket-wall-e-c3/new_source.cc").write_text("// new\n")
        with self.assertRaisesRegex(verify.VerificationError, "required input set"):
            self.verify_record()

    def test_rejects_changed_build_binary(self) -> None:
        payload = bytearray(self.image.read_bytes())
        payload[-1] ^= 1
        self.image.write_bytes(payload)
        with self.assertRaisesRegex(verify.VerificationError, "build artifact SHA-256 mismatch"):
            self.verify_record()

    def test_rejects_changed_dist_binary(self) -> None:
        (self.dist / self.filename).write_bytes(b"incorrect artifact")
        with self.assertRaisesRegex(verify.VerificationError, "dist artifact size mismatch"):
            self.verify_record()

    def test_rejects_changed_effective_config(self) -> None:
        self.sdkconfig.write_text(self.sdkconfig.read_text() + "# changed\n")
        with self.assertRaisesRegex(verify.VerificationError, "effective sdkconfig SHA-256 mismatch"):
            self.verify_record()

    def test_rejects_invalid_mode(self) -> None:
        self.manifest["build_mode"] = "production"
        self.save_manifest()
        with self.assertRaisesRegex(verify.VerificationError, "invalid build_mode"):
            self.verify_record()

    def test_rejects_mode_mislabeling(self) -> None:
        self.manifest["build_mode"] = "assistant"
        self.save_manifest()
        with self.assertRaisesRegex(verify.VerificationError, "build_mode does not match"):
            self.verify_record()

    def test_rejects_enabled_amplifier_even_with_matching_config_digest(self) -> None:
        self.sdkconfig.write_text(self.sdkconfig.read_text().replace(
            "# CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER is not set",
            "CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER=y"))
        self.manifest["source"]["effective_sdkconfig_sha256"] = verify.sha256_file(self.sdkconfig)
        self.save_manifest()
        with self.assertRaisesRegex(verify.VerificationError, "enables the unqualified amplifier"):
            self.verify_record()

    def test_rejects_wrong_target_metadata(self) -> None:
        self.manifest["target"]["chip"] = "esp32s3"
        self.save_manifest()
        with self.assertRaisesRegex(verify.VerificationError, "target metadata"):
            self.verify_record()

    def test_rejects_missing_metadata(self) -> None:
        del self.manifest["toolchain"]["esptool"]
        self.save_manifest()
        with self.assertRaises(verify.VerificationError):
            self.verify_record()

    def test_rejects_legacy_record_without_mode_provenance(self) -> None:
        self.manifest["schema_version"] = 1
        self.save_manifest()
        with self.assertRaisesRegex(verify.VerificationError, "rebuild with build.sh"):
            self.verify_record()

    def test_rejects_invalid_marker_even_with_matching_digest(self) -> None:
        payload = bytearray(self.image.read_bytes())
        payload[0x8000] = 0
        self.image.write_bytes(payload)
        (self.dist / self.filename).write_bytes(payload)
        self.manifest["artifact"]["sha256"] = verify.sha256_file(self.image)
        self.save_manifest()
        with self.assertRaisesRegex(verify.VerificationError, "invalid partition table marker"):
            self.verify_record()

    def test_record_rejects_input_changes_during_build_and_preserves_old_record(self) -> None:
        previous = self.manifest_path.read_bytes()
        fingerprint = verify.input_fingerprint(verify.input_hashes(self.firmware))
        source = self.firmware / "sdkconfig.defaults"
        source.write_text(source.read_text() + "# mid-build change\n")
        with self.assertRaisesRegex(verify.VerificationError, "changed during the build"):
            self.make_record(fingerprint=fingerprint)
        self.assertEqual(self.manifest_path.read_bytes(), previous)

    def test_record_refuses_invalid_mode(self) -> None:
        with self.assertRaisesRegex(verify.VerificationError, "invalid build_mode"):
            self.make_record("production")

    def test_rejects_unsupported_repeat_build_claim(self) -> None:
        self.manifest["validation"]["outputs_identical"] = True
        self.save_manifest()
        with self.assertRaisesRegex(verify.VerificationError, "validation evidence"):
            self.verify_record()


if __name__ == "__main__":
    unittest.main()
