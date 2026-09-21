# Pocket AI Assistant

This repository turns the [Huy Vector Pocket AI Assistant](https://www.huyvector.org/robots-kinetic/pocket-ai-assistant) reference build into a reviewable project with a pinned vendor image, safe host-side flashing tools, a source-buildable Xiaozhi board port, an audited bill of materials, and an assembly/test checklist.

## Start here: one small step at a time

Follow the [action-only fast track](plan/FAST_TRACK.md). It tells you exactly
what to take out, what to connect, what command to run, and what result counts
as a pass. Do one numbered step at a time; do not unpack the whole project.

The first physical step needs one controller and a proven USB data cable. The
controller order is recorded, but the planned cable purchase is not confirmed;
the guide links the recorded candidate and shows how to test any cable you
already own. It then adds the button, OLED, and microphone one at a time. The
default source build is an **offline bench test**: it reports microphone levels
over USB and tests the OLED without Wi-Fi, a cloud account, an amplifier, or a
battery.

Leave the battery, charger, external regulators, amplifier, and metal case off
this first prototype. OLED/microphone power comes only from the controller's
3.3 V output. Never connect an external power source to that rail while USB is
connected.

The [technical USB quickstart](docs/PROTOTYPE_QUICKSTART.md) remains the compact
reference for experienced builders and troubleshooting. Engineering
explanations moved out of the action guide into the
[fast-track theory companion](plan/FAST_TRACK_THEORY.md). The
[15-session daily plan](plan/DAILY_STUDY_AND_LAB_PLAN.md) is the deep track —
full measurement labs, evidence discipline, and per-day material prep lists —
worth returning to before any future battery, audio-power, or enclosure work.

## Choose a firmware path

| Path | Use it when | What is reproducible |
| --- | --- | --- |
| Corrected source — recommended | Offline prototype tests first; assistant mode later | Pinned upstream/SDK, checked overlay, and a manifest of the actual local build |
| Pinned vendor image — historical | Investigating the creator's published behavior and face assets | Download integrity only; its GPIO8 microphone and 24 kHz audio are not the corrected prototype contract |

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
│   ├── README.md                 course index and source-of-truth map
│   ├── STUDY_PLAN.md             battery-free fifteen-session curriculum
│   ├── 01-how-it-fits-together.md applied system and signal overview
│   ├── 05_COLOR_AND_FINISH.md    provisional finish study
│   └── fundamentals/             durable electronics lessons and references
├── firmware/
│   ├── src/                      editable pocket-wall-e-c3 board overlay
│   ├── scripts/                  prepare, build, and source-flash helpers
│   ├── source-build.json         validated source-build digest and inputs
│   └── README.md                 source workflow and known differences
├── simulation/
│   ├── diagram.json              partial ESP32-C3/OLED/button Wokwi fixture
│   └── README.md                 simulation limits and lint command
├── plan/
│   ├── FAST_TRACK.md             action-only beginner build guide
│   └── FAST_TRACK_THEORY.md      optional theory mapped to each build step
└── tools/
    ├── netcheck.py               static checker; legacy power model withdrawn
    ├── pocket_ai_device.py       vendor-image fetch/verify/flash/monitor CLI
    ├── vendor-firmware.json      artifact provenance and integrity metadata
    └── tests/                    host-tool unit tests
```

A [partial Wokwi fixture](simulation/README.md) checks the corrected OLED and
GPIO10 button diagram. It intentionally does not model the power or audio
hardware.

Software setup can start without a new purchase. The first physical boot needs
a proven data cable, and a fully bare controller/OLED/microphone set needs 26
header pins; check the fast track before ordering or soldering anything. For a
**later battery-powered assembly**,
[docs/FINAL_MATERIALS_FOR_REVIEW.md](docs/FINAL_MATERIALS_FOR_REVIEW.md)
records the proposed F0 hardware and its unresolved tests; it is not a prerequisite
shopping list for the USB prototype. Do not connect the cell, cut brass, assemble
that power chain, or pocket-carry it without completing the relevant tests.
The former complete-cart decision is retained
unchanged in [docs/CLAUDE_R1_BUILD_PROPOSAL.md](docs/CLAUDE_R1_BUILD_PROPOSAL.md)
for review; [docs/MATERIALS.md](docs/MATERIALS.md),
[docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md), and
[docs/WIRING_AND_ASSEMBLY.md](docs/WIRING_AND_ASSEMBLY.md) describe that
superseded R1 candidate and are not purchasing or assembly authority.

Use the [electronics course](edu/README.md) as a reference when a step introduces
a new concept, not an entrance exam. Regardless of revision,
do **not** strip a lithium cell, solder to its can, use the brass frame as a
conductor, or charge an undocumented cell.

## Historical vendor-image workflow

Skip this section for the beginner prototype. Use the corrected source below;
a matching vendor checksum does not establish compatible microphone wiring or
MAX98357A audio timing.

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
firmware/scripts/setup.sh
. firmware/.work/esp-idf/export.sh
firmware/scripts/build.sh
```

Setup is needed once; activate `export.sh` again in each new terminal.
`build.sh` defaults to offline diagnostics. Use `build.sh --assistant` only
after those tests pass and you are ready to configure the third-party service.
Read [`firmware/README.md`](firmware/README.md) before using the source-flash helper.
It records the expected toolchain, generated output, pin assignments, and the
differences from the opaque vendor image.

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
- Each successful source build records its exact inputs, effective configuration,
  mode, and output digest in ignored `firmware/dist/source-build.json`. The
  [checked-in reference record](firmware/source-build.json) describes one specific
  build; neither a checksum nor successful compilation proves hardware operation.
- The USB prototype was built and established `PASS 9` on 2026-09-20: two cold
  starts without a reset loop, every button press logged, the OLED starting and
  toggling, and speech microphone RMS roughly 4x the quiet floor with
  `read_errors=0`. That is a bench result recorded by the builder, not an
  automated one: no assembled battery circuit has been connected, the amplifier
  stays disabled, and `firmware/source-build.json` still records
  `hardware_tested: false` because that flag describes what the build workflow
  verified, which remains nothing physical.
- On 2026-09-21 the builder provisioned board `A1` onto Wi-Fi under the 8.5 dBm
  transmit-power cap and received one remote response from the Xiaozhi backend
  (`PASS 10C`). That is also a builder-reported bench result. The amplifier
  stays disabled, so there is still no spoken output. Follow [Lesson 13's staged integration method](edu/fundamentals/13-debugging-integration-and-capstone.md), keep a separate [lab record](edu/fundamentals/reference/lab-record-template.md) for each article, and use the [current F0 promotion gates](docs/FINAL_MATERIALS_FOR_REVIEW.md#promotion-gates-before-claude-may-say-final-go) before any cell connection or pocket carry.
