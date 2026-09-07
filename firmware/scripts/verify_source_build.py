#!/usr/bin/env python3
"""Verify the complete reconstructed source-build artifact and its inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

FIRMWARE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = FIRMWARE_DIR / "source-build.json"
DEFAULT_BUILD_DIR = FIRMWARE_DIR / ".work" / "xiaozhi-esp32" / "build"
DEFAULT_DIST_DIR = FIRMWARE_DIR / "dist"
BUILD_MODES = {"diagnostics", "assistant"}
REQUIRED_INPUTS = {
    "dependencies.lock", "versions.env", "sdkconfig.defaults",
    "partitions/pocket-ai-4m.csv",
    "patches/xiaozhi-v2.4.0-pocket-wall-e-c3.patch",
    "src/boards/pocket-wall-e-c3/config.h",
    "src/boards/pocket-wall-e-c3/config.json",
    "src/boards/pocket-wall-e-c3/pocket_wall_e_c3.cc",
    "scripts/prepare.sh", "scripts/build.sh",
    "scripts/record_source_build.py", "scripts/verify_source_build.py",
}
TOOLCHAIN_KEYS = {
    "riscv32_esp_elf_gcc", "cmake", "ninja", "python",
    "idf_component_manager", "esptool",
}


class VerificationError(RuntimeError):
    """A source artifact or input did not match the validated build record."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def checked_relative_path(root: Path, value: str, *, label: str) -> Path:
    if not isinstance(value, str) or not value or value == ".":
        raise VerificationError(f"invalid {label} path in manifest: {value!r}")
    relative = Path(value)
    if (relative.is_absolute() or PureWindowsPath(value).drive
            or ".." in relative.parts
            or not (root / relative).resolve().is_relative_to(root.resolve())):
        raise VerificationError(f"invalid {label} path in manifest: {value}")
    return root / relative


def verify_file(
    path: Path, *, expected_sha256: str, expected_size: int | None, label: str
) -> None:
    if not path.is_file():
        raise VerificationError(f"missing {label}: {path}")
    if expected_size is not None and path.stat().st_size != expected_size:
        raise VerificationError(
            f"{label} size mismatch: expected {expected_size}, "
            f"got {path.stat().st_size}: {path}"
        )
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise VerificationError(
            f"{label} SHA-256 mismatch:\n"
            f"  expected {expected_sha256}\n"
            f"  got      {actual_sha256}\n"
            f"  file     {path}"
        )


def required_input_names(firmware_dir: Path) -> set[str]:
    names = set(REQUIRED_INPUTS)
    for directory in ("src/boards/pocket-wall-e-c3", "patches", "partitions"):
        names.update(path.relative_to(firmware_dir).as_posix()
                     for path in (firmware_dir / directory).rglob("*") if path.is_file())
    return names


def input_hashes(firmware_dir: Path) -> dict[str, str]:
    result = {}
    for name in sorted(required_input_names(firmware_dir)):
        path = checked_relative_path(firmware_dir, name, label="local input")
        if not path.is_file():
            raise VerificationError(f"missing local input {name}: {path}")
        result[name] = sha256_file(path)
    return result


def input_fingerprint(hashes: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()


def read_versions(firmware_dir: Path) -> dict[str, str]:
    values = {}
    for line in (firmware_dir / "versions.env").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=([^\s]+)", line)
        if not match:
            raise VerificationError(f"unsupported versions.env assignment: {line}")
        values[match[1]] = match[2]
    return values


def sdkconfig_values(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text().splitlines():
        if match := re.fullmatch(r"(CONFIG_\w+)=(.*)", line):
            values[match[1]] = match[2]
        elif match := re.fullmatch(r"# (CONFIG_\w+) is not set", line):
            values[match[1]] = "n"
    return values


def validate_manifest(value: dict[str, Any], firmware_dir: Path) -> None:
    try:
        if value["schema_version"] != 2:
            raise VerificationError("unsupported source-build manifest schema; rebuild with build.sh")
        if value["build_mode"] not in BUILD_MODES:
            raise VerificationError("invalid build_mode; expected diagnostics or assistant")
        if value["amplifier_enabled"] is not False:
            raise VerificationError("supported source builds must keep the amplifier disabled")
        artifact = value["artifact"]
        if (type(artifact["size_bytes"]) is not int
                or not 0x10000 < artifact["size_bytes"] <= 0x400000
                or artifact["flash_offset"] != "0x0"
                or artifact["build_path"] != "merged-binary.bin"):
            raise VerificationError("invalid merged artifact size, path, or flash offset")
        target = value["target"]
        if target != {"chip": "esp32c3", "flash_size_bytes": 4194304,
                      "flash_mode": "dio", "flash_frequency_mhz": 80}:
            raise VerificationError("unexpected source-build target metadata")
        versions = read_versions(firmware_dir)
        expected_name = (f"{versions['POCKET_AI_BOARD_TYPE']}-{versions['XIAOZHI_REF']}"
                         f"-idf-{versions['ESP_IDF_REF']}.bin")
        if artifact["filename"] != expected_name:
            raise VerificationError("unexpected dist artifact filename")
        local_inputs = value["local_inputs"]
        if not isinstance(local_inputs, dict):
            raise VerificationError("local_inputs must be an object")
        required = required_input_names(firmware_dir)
        if set(local_inputs) != required:
            raise VerificationError(
                "local_inputs does not match the current required input set: "
                f"missing={sorted(required - set(local_inputs))}, "
                f"unexpected={sorted(set(local_inputs) - required)}")
        source = value["source"]
        expected_source = {
            "xiaozhi_ref": versions["XIAOZHI_REF"],
            "xiaozhi_commit": versions["XIAOZHI_COMMIT"],
            "esp_idf_ref": versions["ESP_IDF_REF"],
            "esp_idf_commit": versions["ESP_IDF_COMMIT"],
            "source_date_epoch": int(versions["XIAOZHI_SOURCE_DATE_EPOCH"]),
            "dependencies_lock_sha256": local_inputs["dependencies.lock"],
        }
        if any(source[key] != expected for key, expected in expected_source.items()):
            raise VerificationError("source metadata does not match pinned inputs")
        for digest in [artifact["sha256"], source["effective_sdkconfig_sha256"],
                       *local_inputs.values()]:
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise VerificationError("invalid SHA-256 metadata")
        for key in TOOLCHAIN_KEYS:
            version = value["toolchain"][key]
            if not isinstance(version, str) or not version.strip():
                raise VerificationError(f"invalid toolchain version: {key}")
        validation = value["validation"]
        count = validation["clean_builds_compared"]
        identical = validation["outputs_identical"]
        if (type(validation["hardware_tested"]) is not bool
                or type(count) is not int or count < 0
                or (identical is not None and type(identical) is not bool)
                or (identical is True and count < 2)):
            raise VerificationError("invalid validation evidence metadata")
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise VerificationError(f"incomplete or invalid source-build manifest: {exc}") from exc


def load_manifest(path: Path, firmware_dir: Path = FIRMWARE_DIR) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read source-build manifest {path}: {exc}") from exc
    validate_manifest(value, firmware_dir)
    return value


def select_manifest(firmware_dir: Path, dist_dir: Path) -> Path:
    local = dist_dir / "source-build.json"
    return local if local.exists() else firmware_dir / "source-build.json"


def verify_source_build(
    manifest_path: Path, build_dir: Path, dist_dir: Path,
    *, firmware_dir: Path = FIRMWARE_DIR,
) -> tuple[Path, int, str]:
    manifest = load_manifest(manifest_path, firmware_dir)
    return verify_manifest_files(manifest, build_dir, dist_dir, firmware_dir=firmware_dir)


def verify_manifest_files(
    manifest: dict[str, Any], build_dir: Path, dist_dir: Path,
    *, firmware_dir: Path = FIRMWARE_DIR,
) -> tuple[Path, int, str]:
    validate_manifest(manifest, firmware_dir)

    try:
        artifact = manifest["artifact"]
        expected_size = int(artifact["size_bytes"])
        expected_sha256 = str(artifact["sha256"])
        build_name = str(artifact["build_path"])
        dist_name = str(artifact["filename"])
        local_inputs = manifest["local_inputs"]
        sdkconfig_sha256 = str(manifest["source"]["effective_sdkconfig_sha256"])
    except (KeyError, TypeError, ValueError) as exc:
        raise VerificationError(f"incomplete source-build manifest: {exc}") from exc

    if not isinstance(local_inputs, dict):
        raise VerificationError("local_inputs must be an object")
    for relative_name, expected_hash in sorted(local_inputs.items()):
        input_path = checked_relative_path(
            firmware_dir, str(relative_name), label="local input"
        )
        verify_file(
            input_path,
            expected_sha256=str(expected_hash),
            expected_size=None,
            label=f"local input {relative_name}",
        )

    sdkconfig_path = build_dir.parent / "sdkconfig"
    verify_file(
        sdkconfig_path,
        expected_sha256=sdkconfig_sha256,
        expected_size=None,
        label="effective sdkconfig",
    )
    config = sdkconfig_values(sdkconfig_path)
    diagnostics = config.get("CONFIG_POCKET_AI_BENCH_DIAGNOSTICS", "n")
    if diagnostics != ("y" if manifest["build_mode"] == "diagnostics" else "n"):
        raise VerificationError("build_mode does not match the effective sdkconfig")
    if config.get("CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER", "n") != "n":
        raise VerificationError("effective sdkconfig enables the unqualified amplifier")
    if (config.get("CONFIG_IDF_TARGET") != '"esp32c3"'
            or config.get("CONFIG_ESPTOOLPY_FLASHSIZE_4MB") != "y"
            or config.get("CONFIG_BOARD_TYPE_POCKET_WALL_E_C3") != "y"):
        raise VerificationError("effective sdkconfig does not select the required board/target/flash")

    build_artifact = checked_relative_path(build_dir, build_name, label="build artifact")
    dist_artifact = checked_relative_path(dist_dir, dist_name, label="dist artifact")
    for label, path in (
        ("build artifact", build_artifact),
        ("dist artifact", dist_artifact),
    ):
        verify_file(
            path,
            expected_sha256=expected_sha256,
            expected_size=expected_size,
            label=label,
        )

    markers = (
        (0x0, b"\xe9", "bootloader"),
        (0x8000, b"\xaa\x50", "partition table"),
        (0x10000, b"\xe9", "application"),
    )
    with dist_artifact.open("rb") as stream:
        for offset, expected, label in markers:
            stream.seek(offset)
            actual = stream.read(len(expected))
            if actual != expected:
                raise VerificationError(
                    f"invalid {label} marker at 0x{offset:x}: "
                    f"expected {expected.hex()}, got {actual.hex() or '<EOF>'}"
                )

    return dist_artifact, expected_size, expected_sha256


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the latest local Pocket AI source build, or the reference if absent."
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD_DIR)
    parser.add_argument("--dist-dir", type=Path, default=DEFAULT_DIST_DIR)
    parser.add_argument("--print-manifest", action="store_true", help="print the selected manifest path only")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest_path = (args.manifest or select_manifest(FIRMWARE_DIR, args.dist_dir)).resolve()
    if args.print_manifest:
        print(manifest_path)
        return 0
    try:
        path, size, digest = verify_source_build(
            manifest_path, args.build_dir.resolve(), args.dist_dir.resolve()
        )
        manifest = load_manifest(manifest_path)
        print(f"Build record: {manifest_path}")
        print(f"Build mode: {manifest['build_mode']}; amplifier: disabled")
        print(f"Verified source artifact: {path}")
        print(f"Size: {size} bytes")
        print(f"SHA-256: {digest}")
        print("This verifies recorded software inputs and bytes, not hardware functionality.")
        return 0
    except (VerificationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
