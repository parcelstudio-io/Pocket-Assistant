# Device host tools

The Pocket AI Assistant normally runs without a laptop-side application. The
ESP32-C3 firmware provisions Wi-Fi locally, then obtains its MQTT or WebSocket
session details from a Xiaozhi-compatible OTA/bootstrap service. These tools are
only for retrieving the published image, flashing it safely, and viewing logs.

The published download is a **merged 4 MB ESP32-C3 image**. It must be written at
address `0x0`, not at the application-only address `0x10000`. The manifest pins
the exact byte size and SHA-256 observed on 2026-09-01. If the publisher changes
the file behind the Google Drive link, the tool stops instead of flashing an
unreviewed artifact.

## Set up the host environment

Python 3.10 or newer and a USB **data** cable are required. From the repository
root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --requirement tools/requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. Linux users
may need membership in their distribution's serial-port group (often
`dialout`) and must sign out and back in after changing it.
If `python3 -m venv` reports that `ensurepip` is unavailable, install your
distribution's Python venv package (commonly `python3-venv`) and retry; do not
fall back to installing or running the flashing stack as root.

## Fetch and verify

```bash
python tools/pocket_ai_device.py fetch
python tools/pocket_ai_device.py verify
```

The default image location is the ignored `tools/.cache/pocket-esp-ai.bin`.
Neither the third-party binary nor credentials are committed to the repository.

## Identify and flash the board

Connect the ESP32-C3 directly over USB, close programs using its serial port,
then list ports:

```bash
python tools/pocket_ai_device.py ports
python tools/pocket_ai_device.py info --port /dev/ttyACM0
```

Use the port shown on your system (`/dev/ttyACM0`, `/dev/ttyUSB0`, a macOS
`/dev/cu.*` device, or a Windows `COM` port). The tool never guesses the target
for a write. To preview and then perform the flash:

```bash
python tools/pocket_ai_device.py flash --port /dev/ttyACM0 --dry-run
python tools/pocket_ai_device.py flash --port /dev/ttyACM0
```

Flashing at `0x0` replaces the bootloader, partition table, application, assets,
and NVS, so saved Wi-Fi configuration is cleared. The tool verifies the image
again and requires typing `FLASH` before it starts. Use `--yes` only in a
controlled automated workflow.

If automatic reset cannot enter the ROM bootloader, hold the board's **BOOT**
button, tap **RESET** (or reconnect USB), release **BOOT**, and retry. Do not use
the destructive erase command as a routine prerequisite. It is available for
recovery and has a separate confirmation:

```bash
python tools/pocket_ai_device.py erase --port /dev/ttyACM0
```

## View boot logs and provision Wi-Fi

```bash
python tools/pocket_ai_device.py monitor --port /dev/ttyACM0
```

The console uses 115200 baud; exit it with `Ctrl+]`. On a clean first boot, the
firmware is expected to create a `Xiaozhi-XXXX` Wi-Fi provisioning access point,
where the suffix is device-specific. Confirm the actual name in the boot log,
join it from a phone or computer, and open <http://192.168.4.1> if the captive
portal does not appear. Choose a 2.4 GHz network and enter its credentials in
the device-hosted form.

The stock image uses `https://api.tenclass.net/xiaozhi/ota/` as its bootstrap
service. That third-party service receives device metadata and assistant audio;
review its terms and privacy behavior before using it. No cloud token or API key
belongs in this repository. A different backend requires a compatible OTA
service URL and, preferably, a source build configured for that service.

## Troubleshooting

- `No serial ports found`: try a known data-capable cable and another USB port.
- Permission denied on Linux: fix serial-group or device permissions; do not run
  the whole workflow as root.
- Connection timeout: manually enter download mode with BOOT/RESET and retry at
  a lower baud, for example `--baud 115200`.
- SHA-256 mismatch: do not bypass verification. Check whether the publisher has
  intentionally released a new image, then review and update the manifest.
- Boot loop after a successful write: capture the complete 115200-baud log and
  confirm the board is actually an ESP32-C3 with at least 4 MB of flash.
