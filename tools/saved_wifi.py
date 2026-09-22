#!/usr/bin/env python3
"""Show which Wi-Fi network a Pocket AI board has saved, with passwords hidden.

Reads only the NVS settings partition (offset 0x9000, 16 KiB) with esptool,
parses it with ESP-IDF's nvs_tool, prints the ``wifi`` namespace with every
password replaced, and deletes the temporary copy even if a step fails. The
read resets the board once; nothing is written.

Run it inside the activated ESP-IDF environment:

    . firmware/.work/esp-idf/export.sh
    python tools/saved_wifi.py --port /dev/ttyACM1
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[1]
NVS_TOOL = (REPO / "firmware" / ".work" / "esp-idf" / "components" / "nvs_flash"
            / "nvs_partition_tool" / "nvs_tool.py")
NVS_OFFSET = "0x9000"
NVS_SIZE = "0x4000"


def summarize(rows: Iterable[dict[str, Any]]) -> list[str]:
    """Return printable lines for the ``wifi`` namespace, never a password."""
    wifi = [row for row in rows if row.get("namespace") == "wifi"]
    lines = []
    for row in wifi:
        key = str(row.get("key", ""))
        if key.startswith("password"):
            state = "set" if row.get("data") else "empty"
            lines.append(f"{key} = <hidden, {state}>")
        else:
            lines.append(f"{key} = {row.get('data')}")
    if not any(str(row.get("key", "")).startswith("ssid") for row in wifi):
        lines.append("No saved Wi-Fi network")
    return lines


def read_rows(port: str) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="pocket-nvs-") as temporary:
        dump = Path(temporary) / "nvs.bin"
        read = subprocess.run(
            [sys.executable, "-m", "esptool", "--chip", "esp32c3", "--port", port,
             "read-flash", NVS_OFFSET, NVS_SIZE, str(dump)],
            capture_output=True, text=True,
        )
        if read.returncode != 0:
            raise RuntimeError("esptool could not read the board:\n"
                               + (read.stderr or read.stdout).strip())
        parsed = subprocess.run(
            [sys.executable, str(NVS_TOOL), "-d", "minimal", "-f", "json", str(dump)],
            capture_output=True, text=True,
        )
        if parsed.returncode != 0:
            raise RuntimeError("nvs_tool could not parse the dump:\n"
                               + (parsed.stderr or parsed.stdout).strip())
        return json.loads(parsed.stdout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", required=True, help="serial port, e.g. /dev/ttyACM1")
    args = parser.parse_args(argv)
    if importlib.util.find_spec("esptool") is None:
        print("error: esptool is not available; run . firmware/.work/esp-idf/export.sh first",
              file=sys.stderr)
        return 2
    if not NVS_TOOL.is_file():
        print(f"error: nvs_tool not found at {NVS_TOOL}; run firmware/scripts/setup.sh first",
              file=sys.stderr)
        return 2
    try:
        rows = read_rows(args.port)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for line in summarize(rows):
        print(line)
    print("Temporary copy deleted. The board was reset once by the read.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
