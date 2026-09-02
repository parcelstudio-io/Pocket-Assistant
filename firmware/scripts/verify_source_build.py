#!/usr/bin/env python3
"""Verify the complete reconstructed source-build artifact and its inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

FIRMWARE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = FIRMWARE_DIR / "source-build.json"
DEFAULT_BUILD_DIR = FIRMWARE_DIR / ".work" / "xiaozhi-esp32" / "build"
DEFAULT_DIST_DIR = FIRMWARE_DIR / "dist"


class VerificationError(RuntimeError):
    """A source artifact or input did not match the validated build record."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def checked_relative_path(root: Path, value: str, *, label: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
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


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if value["schema_version"] != 1:
            raise VerificationError("unsupported source-build manifest schema")
        return value
    except FileNotFoundError as exc:
        raise VerificationError(f"manifest not found: {path}") from exc
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise VerificationError(f"invalid source-build manifest: {path}: {exc}") from exc


def verify_source_build(
    manifest_path: Path, build_dir: Path, dist_dir: Path
) -> tuple[Path, int, str]:
    manifest = load_manifest(manifest_path)

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
            FIRMWARE_DIR, str(relative_name), label="local input"
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
        description="Verify the pinned Pocket AI source-build artifact and inputs."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD_DIR)
    parser.add_argument("--dist-dir", type=Path, default=DEFAULT_DIST_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path, size, digest = verify_source_build(
            args.manifest.resolve(), args.build_dir.resolve(), args.dist_dir.resolve()
        )
        print(f"Verified source artifact: {path}")
        print(f"Size: {size} bytes")
        print(f"SHA-256: {digest}")
        return 0
    except VerificationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
