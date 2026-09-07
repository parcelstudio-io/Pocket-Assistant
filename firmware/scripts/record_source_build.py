#!/usr/bin/env python3
"""Record one successful local build without claiming hardware or repeat-build tests."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verify_source_build import (
    BUILD_MODES, DEFAULT_BUILD_DIR, DEFAULT_DIST_DIR, FIRMWARE_DIR,
    VerificationError, input_fingerprint, input_hashes, read_versions,
    sha256_file, verify_manifest_files,
)


def command_output(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise VerificationError(f"cannot inspect build tool: {' '.join(command)}: {exc}") from exc


def collect_toolchain() -> dict[str, str]:
    try:
        return {
            "riscv32_esp_elf_gcc": command_output(["riscv32-esp-elf-gcc", "--version"]).splitlines()[0],
            "cmake": command_output(["cmake", "--version"]).splitlines()[0],
            "ninja": command_output(["ninja", "--version"]),
            "python": platform.python_version(),
            "idf_component_manager": importlib.metadata.version("idf-component-manager"),
            "esptool": importlib.metadata.version("esptool"),
        }
    except (importlib.metadata.PackageNotFoundError, IndexError) as exc:
        raise VerificationError(f"cannot inspect the activated toolchain: {exc}") from exc


def record_source_build(
    firmware_dir: Path, build_dir: Path, dist_dir: Path, mode: str,
    *, expected_input_fingerprint: str,
) -> Path:
    if mode not in BUILD_MODES:
        raise VerificationError("invalid build_mode; expected diagnostics or assistant")
    hashes = input_hashes(firmware_dir)
    if input_fingerprint(hashes) != expected_input_fingerprint:
        raise VerificationError("local inputs changed during the build; rebuild before recording")
    versions = read_versions(firmware_dir)
    actual_commit = command_output(["git", "-C", str(build_dir.parent), "rev-parse", "HEAD"])
    if actual_commit != versions["XIAOZHI_COMMIT"]:
        raise VerificationError("compiled checkout does not match the pinned Xiaozhi commit")
    idf_path = os.environ.get("IDF_PATH")
    if not idf_path:
        raise VerificationError("IDF_PATH is missing; activate the pinned ESP-IDF environment")
    actual_idf = command_output(["git", "-C", idf_path, "rev-parse", "HEAD"])
    if actual_idf != versions["ESP_IDF_COMMIT"]:
        raise VerificationError("activated SDK does not match the pinned ESP-IDF commit")
    if command_output(["git", "-C", idf_path, "status", "--porcelain=v1", "--untracked-files=no"]):
        raise VerificationError("activated SDK has tracked modifications")
    if os.environ.get("SOURCE_DATE_EPOCH") != versions["XIAOZHI_SOURCE_DATE_EPOCH"]:
        raise VerificationError("SOURCE_DATE_EPOCH does not match the pinned build timestamp")

    image = build_dir / "merged-binary.bin"
    manifest: dict[str, Any] = {
        "schema_version": 2,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "build_mode": mode,
        "amplifier_enabled": False,
        "artifact": {
            "filename": (f"{versions['POCKET_AI_BOARD_TYPE']}-{versions['XIAOZHI_REF']}"
                         f"-idf-{versions['ESP_IDF_REF']}.bin"),
            "build_path": "merged-binary.bin",
            "flash_offset": "0x0",
            "size_bytes": image.stat().st_size,
            "sha256": sha256_file(image),
        },
        "target": {"chip": "esp32c3", "flash_size_bytes": 4194304,
                   "flash_mode": "dio", "flash_frequency_mhz": 80},
        "source": {
            "xiaozhi_ref": versions["XIAOZHI_REF"],
            "xiaozhi_commit": actual_commit,
            "source_date_epoch": int(versions["XIAOZHI_SOURCE_DATE_EPOCH"]),
            "esp_idf_ref": versions["ESP_IDF_REF"],
            "esp_idf_commit": actual_idf,
            "dependencies_lock_sha256": hashes["dependencies.lock"],
            "effective_sdkconfig_sha256": sha256_file(build_dir.parent / "sdkconfig"),
        },
        "local_inputs": hashes,
        "toolchain": collect_toolchain(),
        "validation": {"clean_builds_compared": 0, "outputs_identical": None,
                       "hardware_tested": False},
        "note": ("Local build record. No independent repeat-build comparison or hardware "
                 "test was performed by this workflow. Amplifier remains disabled. "
                 "Checksums detect changed recorded inputs and artifacts; they do not "
                 "establish electrical or end-to-end assistant functionality."),
    }
    verify_manifest_files(manifest, build_dir, dist_dir, firmware_dir=firmware_dir)
    destination = dist_dir / "source-build.json"
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=dist_dir,
                                         prefix=".source-build.", suffix=".json", delete=False) as stream:
            temporary_path = Path(stream.name)
            json.dump(manifest, stream, indent=2)
            stream.write("\n")
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(BUILD_MODES))
    parser.add_argument("--expected-input-fingerprint")
    parser.add_argument("--print-input-fingerprint", action="store_true")
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD_DIR)
    parser.add_argument("--dist-dir", type=Path, default=DEFAULT_DIST_DIR)
    args = parser.parse_args(argv)
    try:
        if args.print_input_fingerprint:
            print(input_fingerprint(input_hashes(FIRMWARE_DIR)))
            return 0
        if args.mode is None or args.expected_input_fingerprint is None:
            parser.error("recording requires --mode and --expected-input-fingerprint")
        path = record_source_build(FIRMWARE_DIR, args.build_dir.resolve(),
                                   args.dist_dir.resolve(), args.mode,
                                   expected_input_fingerprint=args.expected_input_fingerprint)
        print(f"Recorded local {args.mode} build: {path}")
        return 0
    except (VerificationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
