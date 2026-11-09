#!/usr/bin/env python3
"""Fetch the pinned ESP-FLY source, apply the reviewed patch, and build only.

Requires an activated ESP-IDF v5.0.7 environment with ESP32-S3 tools. Never
flashes a device. Firmware output contains the private Wi-Fi password.
"""
import argparse
import os
from pathlib import Path
import re
import secrets
import subprocess

COMMIT = "96de4d78c4d9e561c6a7ade2865a13f16b519ac3"
URL = "https://github.com/Seeed-Projects/Co-Create_ESP-FLY.git"
HERE = Path(__file__).resolve().parent


def run(argv, **kwargs):
    return subprocess.run(argv, check=True, **kwargs)


def output(argv):
    return subprocess.check_output(argv, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=HERE / ".work")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    source = work / "esp-fly"
    if not source.exists():
        run(["git", "clone", "--no-checkout", URL, str(source)])
        run(["git", "-C", str(source), "checkout", "--detach", COMMIT])
    if output(["git", "-C", str(source), "rev-parse", "HEAD"]) != COMMIT:
        raise SystemExit("Work clone is not at the pinned commit; use a new work directory.")
    patch = HERE / "patches/0001-bench-link-hardening.patch"
    check = subprocess.run(["git", "-C", str(source), "apply", "--check", str(patch)], capture_output=True)
    if check.returncode == 0:
        run(["git", "-C", str(source), "apply", str(patch)])
    else:
        already = subprocess.run(["git", "-C", str(source), "apply", "--reverse", "--check", str(patch)], capture_output=True)
        if already.returncode:
            raise SystemExit("Source differs from both pinned and patched versions; use a new work directory.")
    config = work / "sdkconfig-xs"
    password_file = work / "wifi-password.txt"
    if not config.exists():
        password = os.environ.get("XS_DRONE_WIFI_PASSWORD") or secrets.token_urlsafe(18)
        if not re.fullmatch(r"[A-Za-z0-9_-]{12,63}", password):
            raise SystemExit("XS_DRONE_WIFI_PASSWORD must contain 12–63 letters, digits, underscores or hyphens.")
        sdk = output(["git", "-C", str(source), "show", f"{COMMIT}:Firmware/esp-drone/sdkconfig"])
        for key in ("ENABLE_POSITION_HOLD_MODE", "ENABLE_COMMAND_MODE_SET"):
            sdk = re.sub(rf"^CONFIG_{key}=y$", f"# CONFIG_{key} is not set", sdk, flags=re.M)
        sdk = re.sub(r"^CONFIG_ADC1_PIN=10$", "CONFIG_ADC1_PIN=2", sdk, flags=re.M)
        # GPIO43 is the kit's red LED; keep the application console on USB.
        for key in ("ESP_CONSOLE_UART_DEFAULT", "ESP_CONSOLE_SECONDARY_USB_SERIAL_JTAG"):
            sdk = re.sub(rf"^CONFIG_{key}=y$", f"# CONFIG_{key} is not set", sdk, flags=re.M)
        for key in ("ESP_CONSOLE_USB_SERIAL_JTAG", "ESP_CONSOLE_SECONDARY_NONE"):
            sdk = re.sub(rf"^# CONFIG_{key} is not set$", f"CONFIG_{key}=y", sdk, flags=re.M)
        sdk += '\nCONFIG_XS_WIFI_PASSWORD="' + password + '"\n'
        sdk += "CONFIG_XS_LINK_LEVEL_MS=300\nCONFIG_XS_LINK_STOP_MS=500\n# CONFIG_XS_MOTOR_STARTUP_TEST is not set\n"
        config.write_text(sdk)
        config.chmod(0o600)
        password_file.write_text(password + "\n")
        password_file.chmod(0o600)
    print(f"Private Wi-Fi credentials: {password_file} (not printed)")
    print(f"Prepared source: {source}")
    run(["python3", str(HERE.parent / "tests/firmware_audit.py"), "--esp-source", str(source)])
    if args.prepare_only:
        return
    version = output(["idf.py", "--version"])
    if "v5.0.7" not in version:
        raise SystemExit(f"Expected ESP-IDF v5.0.7; found {version}.")
    project = source / "Firmware/esp-drone"
    run(["idf.py", "-B", str(work / "build-local"), "-D", f"SDKCONFIG={config}", "build"], cwd=project)
    print("Build complete. No device has been flashed. Use generated flasher_args.json for exact offsets.")


if __name__ == "__main__":
    main()
