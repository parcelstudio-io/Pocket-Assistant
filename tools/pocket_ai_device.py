#!/usr/bin/env python3
"""Safe host-side utilities for the Huy Vector Pocket AI Assistant.

The vendor publishes one merged ESP32-C3 image.  This utility downloads and
verifies that exact artifact before allowing it to be written at flash offset
zero.  It deliberately does not accept or persist Wi-Fi or cloud credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path, PureWindowsPath
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

TOOLS_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = TOOLS_DIR / "vendor-firmware.json"
DEFAULT_CACHE_DIR = TOOLS_DIR / ".cache"
DOWNLOAD_CHUNK_BYTES = 1024 * 1024
ESP_IMAGE_MAGIC = b"\xe9"
PARTITION_ENTRY_MAGIC = b"\xaa\x50"


class DeviceToolError(RuntimeError):
    """An expected, user-actionable tool failure."""


def load_artifact(manifest_path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifact = payload["artifact"]
    except FileNotFoundError as exc:
        raise DeviceToolError(f"manifest not found: {manifest_path}") from exc
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise DeviceToolError(
            f"invalid firmware manifest: {manifest_path}: {exc}"
        ) from exc

    if not isinstance(artifact, dict):
        raise DeviceToolError(
            f"invalid firmware manifest: {manifest_path}: artifact must be an object"
        )

    required = {
        "filename",
        "download_url",
        "size_bytes",
        "sha256",
        "chip",
        "flash_offset",
        "partition_table_offset",
        "application_offset",
    }
    missing = sorted(required.difference(artifact))
    if missing:
        raise DeviceToolError(
            f"firmware manifest is missing required fields: {', '.join(missing)}"
        )

    if artifact["chip"] != "esp32c3" or artifact["flash_offset"] != "0x0":
        raise DeviceToolError(
            "refusing unexpected target: this tool only supports the merged "
            "ESP32-C3 image at offset 0x0"
        )
    if urlsplit(str(artifact["download_url"])).scheme != "https":
        raise DeviceToolError("refusing firmware download URL that is not HTTPS")

    filename = artifact["filename"]
    if (
        not isinstance(filename, str)
        or not filename
        or Path(filename).name != filename
        or PureWindowsPath(filename).name != filename
        or filename in {".", ".."}
    ):
        raise DeviceToolError("firmware manifest filename must be a basename")

    try:
        digest = str(artifact["sha256"])
        bytes.fromhex(digest)
        size_bytes = int(str(artifact["size_bytes"]), 10)
        partition_offset = int(str(artifact["partition_table_offset"]), 0)
        application_offset = int(str(artifact["application_offset"]), 0)
    except (TypeError, ValueError) as exc:
        raise DeviceToolError(
            "firmware manifest contains invalid digest, size, or offset metadata"
        ) from exc
    if (
        len(digest) != 64
        or size_bytes <= 0
        or not 0 < partition_offset < application_offset < size_bytes
    ):
        raise DeviceToolError(
            "firmware manifest contains invalid digest, size, or offset metadata"
        )
    return artifact


def default_image_path(artifact: dict[str, Any]) -> Path:
    return DEFAULT_CACHE_DIR / str(artifact["filename"])


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(DOWNLOAD_CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def _read_at(path: Path, offset: int, length: int) -> bytes:
    with path.open("rb") as stream:
        stream.seek(offset)
        return stream.read(length)


def verify_image(path: Path, artifact: dict[str, Any]) -> str:
    """Verify size, digest, and the expected merged-image structural markers."""
    if not path.is_file():
        raise DeviceToolError(f"firmware image not found: {path}")

    expected_size = int(artifact["size_bytes"])
    actual_size = path.stat().st_size
    if actual_size != expected_size:
        raise DeviceToolError(
            f"firmware size mismatch for {path}: expected {expected_size} bytes, "
            f"got {actual_size}"
        )

    expected_digest = str(artifact["sha256"]).lower()
    actual_digest = sha256_file(path)
    if actual_digest != expected_digest:
        raise DeviceToolError(
            f"firmware SHA-256 mismatch for {path}:\n"
            f"  expected {expected_digest}\n"
            f"  got      {actual_digest}\n"
            "Do not flash this file. The vendor artifact may have changed."
        )

    partition_offset = int(str(artifact["partition_table_offset"]), 0)
    application_offset = int(str(artifact["application_offset"]), 0)
    markers = (
        (0, ESP_IMAGE_MAGIC, "bootloader"),
        (partition_offset, PARTITION_ENTRY_MAGIC, "partition table"),
        (application_offset, ESP_IMAGE_MAGIC, "application"),
    )
    for offset, expected, label in markers:
        actual = _read_at(path, offset, len(expected))
        if actual != expected:
            raise DeviceToolError(
                f"verified digest but invalid {label} marker at 0x{offset:x}: "
                f"expected {expected.hex()}, got {actual.hex() or '<EOF>'}"
            )
    return actual_digest


def fetch_image(
    destination: Path, artifact: dict[str, Any], *, force: bool = False
) -> str:
    """Download to a temporary file, verify it, then atomically install it."""
    if destination.exists() and not force:
        digest = verify_image(destination, artifact)
        print(f"Already present and verified: {destination}")
        return digest

    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(
        str(artifact["download_url"]),
        headers={"User-Agent": "pocket-ai-assistant-device-tool/1"},
    )
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{destination.name}.",
            suffix=".part",
            dir=destination.parent,
            delete=False,
        ) as temporary:
            temp_path = Path(temporary.name)
            print(f"Downloading vendor image to {destination} ...")
            downloaded = 0
            maximum = int(artifact["size_bytes"])
            with urlopen(request, timeout=60) as response:
                while chunk := response.read(DOWNLOAD_CHUNK_BYTES):
                    downloaded += len(chunk)
                    if downloaded > maximum:
                        raise DeviceToolError(
                            "firmware download exceeded the size pinned in the manifest"
                        )
                    temporary.write(chunk)

        digest = verify_image(temp_path, artifact)
        os.replace(temp_path, destination)
        temp_path = None
        print(f"Verified SHA-256: {digest}")
        print(f"Saved: {destination}")
        return digest
    except (HTTPError, URLError, TimeoutError) as exc:
        raise DeviceToolError(f"firmware download failed: {exc}") from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _require_module(module: str, install_name: str) -> None:
    if importlib.util.find_spec(module) is None:
        raise DeviceToolError(
            f"missing host dependency '{install_name}'. Install with:\n"
            f"  {sys.executable} -m pip install -r {TOOLS_DIR / 'requirements.txt'}"
        )


def serial_ports() -> list[Any]:
    _require_module("serial", "pyserial")
    from serial.tools import list_ports

    return sorted(list_ports.comports(), key=lambda port: port.device)


def print_ports() -> None:
    ports = serial_ports()
    if not ports:
        print("No serial ports found.")
        print("Connect the ESP32-C3 with a USB data cable, then try again.")
        return

    likely_vendors = {0x303A, 0x10C4, 0x1A86, 0x0403}
    for port in ports:
        likely = " [likely ESP/device port]" if port.vid in likely_vendors else ""
        usb_id = ""
        if port.vid is not None and port.pid is not None:
            usb_id = f" ({port.vid:04x}:{port.pid:04x})"
        print(f"{port.device}: {port.description}{usb_id}{likely}")


def esptool_command(
    artifact: dict[str, Any], port: str, command: Iterable[str], *, baud: int | None
) -> list[str]:
    args = [
        sys.executable,
        "-m",
        "esptool",
        "--chip",
        str(artifact["chip"]),
        "--port",
        port,
    ]
    if baud is not None:
        args.extend(("--baud", str(baud)))
    args.extend(command)
    return args


def _display_command(command: Iterable[str]) -> str:
    """Render a diagnostic command without relying on a platform shell."""
    import shlex

    return shlex.join(str(item) for item in command)


def run_command(command: list[str], *, dry_run: bool = False) -> None:
    print(f"Command: {_display_command(command)}")
    if dry_run:
        print("Dry run only; no device was changed.")
        return
    _require_module("esptool", "esptool")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        raise DeviceToolError(
            f"device command failed with exit code {exc.returncode}"
        ) from exc


def confirm_flash(port: str, *, assume_yes: bool) -> None:
    print(f"Target serial port: {port}")
    print("Flash address: 0x0 (merged 4 MB ESP32-C3 image)")
    print(
        "This replaces the bootloader, partition table, application, assets, and NVS."
    )
    print("Saved Wi-Fi settings on the device will be erased.")
    if assume_yes:
        return
    if not sys.stdin.isatty():
        raise DeviceToolError("confirmation required; rerun interactively or add --yes")
    answer = input("Type FLASH to continue: ").strip()
    if answer != "FLASH":
        raise DeviceToolError("flash cancelled")


def confirm_erase(port: str, *, assume_yes: bool) -> None:
    print(f"Target serial port: {port}")
    print(
        "This erases the entire flash chip, including firmware and saved Wi-Fi settings."
    )
    if assume_yes:
        return
    if not sys.stdin.isatty():
        raise DeviceToolError("confirmation required; rerun interactively or add --yes")
    answer = input(f"Type ERASE {port} to continue: ").strip()
    if answer != f"ERASE {port}":
        raise DeviceToolError("erase cancelled")


def resolve_image(value: str | None, artifact: dict[str, Any]) -> Path:
    return Path(value).expanduser().resolve() if value else default_image_path(artifact)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download, verify, flash, and monitor the Pocket AI Assistant."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="firmware provenance manifest (default: tools/vendor-firmware.json)",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    fetch = subparsers.add_parser(
        "fetch", help="download and verify the pinned vendor image"
    )
    fetch.add_argument("--output", help="destination .bin path (default: tools/.cache)")
    fetch.add_argument(
        "--force",
        action="store_true",
        help="replace an existing file after verification",
    )

    verify = subparsers.add_parser(
        "verify", help="verify a local image without changing hardware"
    )
    verify.add_argument("--image", help="image path (default: tools/.cache)")

    subparsers.add_parser("ports", help="list serial ports without changing hardware")

    info = subparsers.add_parser("info", help="read the connected chip identity")
    info.add_argument(
        "--port",
        required=True,
        help="explicit serial port, such as /dev/ttyACM0 or COM4",
    )

    flash = subparsers.add_parser(
        "flash", help="write the verified merged image at address 0x0"
    )
    flash.add_argument(
        "--port", required=True, help="explicit serial port; never auto-selected"
    )
    flash.add_argument("--image", help="image path (default: tools/.cache)")
    flash.add_argument(
        "--baud", type=int, default=460800, help="flashing baud (default: 460800)"
    )
    flash.add_argument(
        "--yes", action="store_true", help="skip the destructive-action prompt"
    )
    flash.add_argument(
        "--dry-run", action="store_true", help="show the verified command only"
    )

    erase = subparsers.add_parser("erase", help="erase the entire ESP32-C3 flash chip")
    erase.add_argument(
        "--port", required=True, help="explicit serial port; never auto-selected"
    )
    erase.add_argument(
        "--yes", action="store_true", help="skip the destructive-action prompt"
    )
    erase.add_argument("--dry-run", action="store_true", help="show the command only")

    monitor = subparsers.add_parser("monitor", help="open a 115200-baud serial console")
    monitor.add_argument("--port", required=True, help="explicit serial port")
    monitor.add_argument(
        "--baud", type=int, default=115200, help="console baud (default: 115200)"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        artifact = load_artifact(args.manifest.resolve())
        if args.action == "fetch":
            destination = resolve_image(args.output, artifact)
            fetch_image(destination, artifact, force=args.force)
        elif args.action == "verify":
            image = resolve_image(args.image, artifact)
            digest = verify_image(image, artifact)
            print(f"Verified: {image}")
            print(f"Size: {image.stat().st_size} bytes")
            print(f"SHA-256: {digest}")
            print(f"Target: {artifact['chip']} at {artifact['flash_offset']}")
        elif args.action == "ports":
            print_ports()
        elif args.action == "info":
            command = esptool_command(artifact, args.port, ["chip-id"], baud=None)
            run_command(command)
        elif args.action == "flash":
            image = resolve_image(args.image, artifact)
            digest = verify_image(image, artifact)
            print(f"Verified firmware SHA-256: {digest}")
            if not args.dry_run:
                confirm_flash(args.port, assume_yes=args.yes)
            command = esptool_command(
                artifact,
                args.port,
                [
                    "--before",
                    "default-reset",
                    "--after",
                    "hard-reset",
                    "write-flash",
                    str(artifact["flash_offset"]),
                    str(image),
                ],
                baud=args.baud,
            )
            run_command(command, dry_run=args.dry_run)
        elif args.action == "erase":
            if not args.dry_run:
                confirm_erase(args.port, assume_yes=args.yes)
            command = esptool_command(artifact, args.port, ["erase-flash"], baud=None)
            run_command(command, dry_run=args.dry_run)
        elif args.action == "monitor":
            _require_module("serial", "pyserial")
            command = [
                sys.executable,
                "-m",
                "serial.tools.miniterm",
                args.port,
                str(args.baud),
                "--raw",
            ]
            print("Exit the monitor with Ctrl+].")
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as exc:
                raise DeviceToolError(
                    f"serial monitor exited with code {exc.returncode}"
                ) from exc
        return 0
    except DeviceToolError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
