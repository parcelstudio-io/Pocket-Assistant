# Pocket AI Assistant

This repository turns the [Huy Vector Pocket AI Assistant](https://www.huyvector.org/robots-kinetic/pocket-ai-assistant) reference build into a reviewable project with a pinned vendor image, safe host-side flashing tools, a source-buildable Xiaozhi board port, an audited bill of materials, and an assembly/test checklist.

## Choose a firmware path

| Path | Use it when | What is reproducible |
| --- | --- | --- |
| Pinned vendor image | You want the creator's published behavior and face assets | The downloaded bytes are checked against a pinned size and SHA-256 before flashing |
| Source build | You want editable firmware, auditable pins, or a different backend | The upstream Xiaozhi release, ESP-IDF SDK, board overlay, partition map, and build steps are pinned |

These paths are deliberately separate. The creator published only a merged binary, not the custom `pocket-wall-e-c3` source or face assets. Inspection identifies it as a private Xiaozhi `2.4.0` build made with `ESP-IDF v5.5.2-dirty`. The editable port in [`firmware/`](firmware/) reconstructs the board against public [Xiaozhi v2.4.0](https://github.com/78/xiaozhi-esp32/releases/tag/v2.4.0) and its supported ESP-IDF v6.0.2 toolchain; it is not claimed to be byte-identical.

## Repository map

```text
.
├── docs/
│   ├── FINAL_MATERIALS_FOR_REVIEW.md  current Phase 0 purchase authority
│   ├── CLAUDE_R1_BUILD_PROPOSAL.md    archived compact-build proposal
│   ├── MATERIALS.md              archived R1 order sheet; do not order from it
│   ├── BUILD_GUIDE.md            video correlation; final assembly is held
│   ├── WIRING_AND_ASSEMBLY.md    archived R1 power wiring; not build authority
│   └── BOM.md                    historical creator-page ↔ R1 reconciliation
├── edu/
│   ├── README.md                 course index and evidence boundary
│   ├── 02_COMPONENTS_*.md        historical component rationale
│   ├── 03_HOW_IT_WORKS.md        corrected source-build wiring contract
│   └── 04–06_*.md                assembly, finish, and acceptance checks
├── firmware/
│   ├── src/                      editable pocket-wall-e-c3 board overlay
│   ├── scripts/                  prepare, build, and source-flash helpers
│   ├── source-build.json         validated source-build digest and inputs
│   └── README.md                 source workflow and known differences
├── simulation/
│   ├── diagram.json              partial ESP32-C3/OLED/button Wokwi fixture
│   └── README.md                 simulation limits and lint command
└── tools/
    ├── netcheck.py               static checker; legacy power model withdrawn
    ├── pocket_ai_device.py       vendor-image fetch/verify/flash/monitor CLI
    ├── vendor-firmware.json      artifact provenance and integrity metadata
    └── tests/                    host-tool unit tests
```

A [partial Wokwi fixture](simulation/README.md) checks the corrected OLED and
GPIO10 button diagram. It intentionally does not model the power or audio
hardware.

**Use [docs/FINAL_MATERIALS_FOR_REVIEW.md](docs/FINAL_MATERIALS_FOR_REVIEW.md)
as the only current purchase decision source.** Its F0 decision is deliberately
narrow: buy one reversible `BUY-P0` qualification batch, but do not connect the
cell, cut brass, assemble a final power chain, or pocket-carry the device until
the listed promotion gates pass. The former complete-cart decision is retained
unchanged in [docs/CLAUDE_R1_BUILD_PROPOSAL.md](docs/CLAUDE_R1_BUILD_PROPOSAL.md)
for review; [docs/MATERIALS.md](docs/MATERIALS.md),
[docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md), and
[docs/WIRING_AND_ASSEMBLY.md](docs/WIRING_AND_ASSEMBLY.md) describe that
superseded R1 candidate and are not purchasing or assembly authority.

Start with the [build course](edu/README.md) and the corrected
[source-build wiring contract](edu/03_HOW_IT_WORKS.md). Regardless of revision,
do **not** strip a lithium cell, solder to its can, use the brass frame as a
conductor, or charge an undocumented cell.

## Flash the exact published image

For Phase 0, flash a bare SuperMini. An assembled service design is not yet
released. Until the proposed supply and I2S/control isolation pass every
source-state test, **unplug the pack and detach the external power and
amplifier-signal harnesses before connecting the SuperMini USB-C**, and never
connect both USB-C ports. Generic SuperMini clones have varying VBUS/`5V`
arrangements, so the final solution cannot rely on an assumed clone diode.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --requirement tools/requirements.txt

python tools/pocket_ai_device.py fetch
python tools/pocket_ai_device.py verify
python tools/pocket_ai_device.py ports
python tools/pocket_ai_device.py info --port /dev/ttyACM0
python tools/pocket_ai_device.py flash --port /dev/ttyACM0 --dry-run
python tools/pocket_ai_device.py flash --port /dev/ttyACM0
python tools/pocket_ai_device.py monitor --port /dev/ttyACM0
```

Replace `/dev/ttyACM0` with the explicit port reported on your machine. The image is a merged ESP32-C3 image and is written at `0x0`; the tool verifies it and asks for confirmation before writing. See [`tools/README.md`](tools/README.md) for Windows/macOS port names, BOOT-mode recovery, Wi-Fi provisioning, and privacy notes.

## Build the editable source port

The source workflow fetches the pinned upstream repository into an ignored working directory, applies the local board files, checks the upstream commit, and builds with ESP-IDF v6.0.2:

```bash
cd firmware
./scripts/prepare.sh
./scripts/build.sh
```

Read [`firmware/README.md`](firmware/README.md) before using the source-flash helper. It records the expected toolchain, generated output, pin assignments, and the differences from the opaque vendor image.

## Hardware contract

| Function | Module signal | ESP32-C3 GPIO |
| --- | --- | ---: |
| OLED I2C | SDA / SCL | 21 / 20 |
| Shared I2S clocks | WS / BCLK | 1 / 2 |
| Microphone input | I2S microphone data (#6049 ICS-43434 Phase 0 primary; INMP441 alternate) | 4 |
| Amplifier output | MAX98357A DIN | 3 |
| Optional external action button | active-low button | 10 |

The corrected source build accepts a 0.96-inch 128×64 SSD1306 I2C module at address `0x3c` or `0x3d`, uses 16 kHz duplex audio, and puts the I2S microphone's data output on GPIO4 with its left-slot select grounded. The Phase 0 primary is the controlled Adafruit #6049 ICS-43434 (`SEL` → GND); INMP441 (`L/R` → GND) remains an alternate after its carrier pinout is checked. The pinned creator binary instead requires microphone data on GPIO8 and OLED address `0x3c`. Both audio modules share `WS` and `BCLK`. GPIO10 is the active-low application input, while the SuperMini's ROM BOOT button remains GPIO9.

## What has and has not been verified

- The published binary's size, digest, merged-image markers, chip target, application metadata, and partition offsets were inspected and pinned.
- The host CLI has unit tests and refuses an unverified image or implicit serial-port target.
- The source overlay compiled successfully twice from clean, pinned inputs on the validation host; both merged images were identical. The size, digest, SDK/source commits, local-input hashes, effective configuration, and observed tool versions are recorded in [`firmware/source-build.json`](firmware/source-build.json).
- No physical ESP32-C3 or assembled battery circuit was connected in this workspace — `hardware_tested` is still `false`. The [staged assembly plan](edu/04_ASSEMBLY_STEP_BY_STEP.md) is retained as a candidate sequence, while the [acceptance worksheet](edu/06_ACCEPTANCE_TESTS.md) and current F0 decision define what must be proved before any cell connection or pocket carry.
