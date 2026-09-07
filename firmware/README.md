# Pocket AI Assistant firmware

This directory provides a buildable source overlay for the Pocket AI Assistant's
ESP32-C3 hardware. It pins the public Xiaozhi application, adds the project's
board registration and intended pin map, forces the 4 MB flash layout,
and produces a merged image that can be flashed at address `0x0`.

> **Current-contract boundary:** the corrected source targets an I2S
> microphone on GPIO4 (Phase 0 primary: Adafruit `#6049` ICS-43434 with `SEL`
> low; held alternate: INMP441 with `L/R` low) and a MAX98357A
> amplifier on GPIO3, with shared clocks on GPIO1/GPIO2 at 16 kHz. This README
> is not purchase authority; the release decision is
> [FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md).

## Beginner default: offline USB diagnostics

Start with [the prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md), not the
vendor binary. The default build tests the OLED and prints microphone levels
over USB. It does not start Wi-Fi, provision an account, or send recordings
anywhere. The amplifier is disabled. Begin with a bare controller; add the
OLED and microphone one at a time, powered from its 3.3 V output only.

From the repository root, in Bash:

```bash
firmware/scripts/setup.sh
. firmware/.work/esp-idf/export.sh
firmware/scripts/build.sh
python3 firmware/scripts/verify_source_build.py
```

Setup downloads the pinned SDK and its tools and can take several minutes.
It does not need hardware or administrator privileges. Run setup once and
source `export.sh` again in each new terminal. Use `build.sh --diagnostics`
as an explicit alias for the default, or `build.sh --assistant` later for the
networked application. Both supported modes keep the amplifier disabled.
The last successful build is the one the verifier and flash helper select.

## Source status and limits

The project author publishes a merged binary but not the corresponding board
source. This adapter is therefore a careful source reconstruction, **not** the
author's original code and not a byte-for-byte rebuild of that binary.

- The vendor image identifies itself as Xiaozhi `2.4.0`, board
  `pocket-wall-e-c3`, built by a private `ESP-IDF v5.5.2-dirty` tree.
- This source workflow pins public Xiaozhi tag `v2.4.0` at commit
  `5540258abcbfa62518d09959308200be1c5b1b2b` and the upstream-preferred
  ESP-IDF `v6.0.2`.
- The author's `PocketOledDisplay` behavior is unpublished. The overlay keeps a
  board-specific display extension point but currently uses Xiaozhi's standard
  128x64 OLED interface instead of attempting to imitate the custom face UI.
- The checked-in `dependencies.lock` pins the 60 managed components and their
  registry hashes used by the validated build. The build fails if the component
  manager tries to rewrite that lock.
- `SOURCE_DATE_EPOCH` is fixed to the upstream commit timestamp so generated
  app metadata and compiler date/time strings do not depend on build time.
- A successful build creates ignored `dist/source-build.json`, recording the
  actual image, all local source inputs, effective configuration, build mode,
  and tool versions. Verification checks these again before flashing. The
  checked-in `source-build.json` is a reference for a specific build, not a
  permanent checksum every future source edit must reproduce. Local records
  do not inherit old claims of identical clean builds or hardware tests.
- The source and configuration can be compiled without the device. Electrical,
  microphone, speaker, button, and end-to-end assistant behavior still require
  a hardware smoke test.

Assistant mode additionally diverges for English users: wake word
`wn9s_hiesp` ("Hi, ESP") and `CONFIG_LANGUAGE_EN_US` replace the vendor
image's Mandarin `wn9s_nihaoxiaozhi` and zh-CN strings (both set in
`sdkconfig.defaults` and the board `config.json`; the explicit
`# CONFIG_SR_WN_WN9S_NIHAOXIAOZHI is not set` line is required because the
WakeNet9s entries are independent bools, not a choice group).

For the exact published image and its pinned checksum, use the
[host flashing and verification tools](../tools/README.md).

## Current corrected-source pin map

| Function | ESP32-C3 GPIO | Peripheral connection |
| --- | ---: | --- |
| I2S word select | 1 | #6049 ICS-43434 `WS/LRCLK` (alt: INMP441 `WS`) and MAX98357A `LRC` |
| I2S bit clock | 2 | #6049 ICS-43434 `BCLK` (alt: INMP441 `SCK`) and MAX98357A `BCLK`; expected 1.024 MHz |
| I2S speaker data | 3 | MAX98357A `DIN` |
| I2S microphone data | 4 | #6049 ICS-43434 `DOUT` (alt: INMP441 `SD`) |
| Optional action/config input | 10 | Active-low push button to GND if fitted |
| OLED SCL | 20 | SSD1306 SCL |
| OLED SDA | 21 | SSD1306 SDA |

These are logical endpoints. The F0 hardware experiment interposes a one-way
TXU0104 boundary between GPIO1/GPIO2/GPIO3 and the amplifier. It proposes
GPIO5, with 4.7 kΩ to ground, as channel A4; B4 then releases `SD_MODE` into
left-channel operation. The #2873 open-drain power-good output independently
gates TXU `OE` through a 10 kΩ pull-up to 5V_SYS, so loss of rail-good disables
all amplifier-side outputs. Official chip reset does not itself pull MTDI
(GPIO5) high, but firmware APIs can enable that pull-up: GPIO5 must be driven low
at the earliest board-init point and must not be reset into a pulled-up state.
The candidate has no MCU `PG` sense input: firmware sequencing uses a qualified
startup/rail delay and valid zero-data I2S while `PG` independently vetoes
`OE`. The delay before nonzero samples must cover measured worst-case `PG`
release plus amplifier turn-on, or the final schematic needs a reviewed
level-safe sense path.
The board codec implements the GPIO5 mute/startup/shutdown sequence, but the
physical interface and its timing are **not hardware-qualified**. The supported
prototype builds deliberately keep `CONFIG_POCKET_AI_ENABLE_QUALIFIED_AMPLIFIER`
off. Leave the amplifier disconnected for the USB quickstart; on a separate
unqualified audio fixture, keep `SD_MODE` hard-grounded. Do not bypass that mute
just to hear a sound. Enabling a qualified fixture later requires deliberate
configuration/tooling changes and measured startup, shutdown, and partial-power
checks. A firmware volume limit alone is not a speaker-power qualification.

At 16,000 frames/s and 64 bit clocks per frame, the I2S bit clock is
`16,000 × 64 = 1.024 MHz`. The microphone uses the intended left slot with its
select pin low (#6049 `SEL`; INMP441 `L/R`). The pinned codec selects mono DMA
with `I2S_STD_SLOT_LEFT`; source inspection therefore predicts active left and
inactive right TX slots because ESP-IDF copy-mono is enabled only for a `BOTH`
slot mask. Treat that as unverified until a hardware capture confirms it. Do
not assume the #3006 default mix gives full amplitude; qualify its `SD` mode
and select left explicitly if the capture confirms an inactive right slot.

### Historical vendor/video contract

The published vendor image uses a microphone harness with data on GPIO8,
SSD1306 address `0x3C`, and 24 kHz full-duplex audio. Those recovered values
are historical replication evidence only — never wire the corrected-source
GPIO4 harness for the vendor binary or vice versa. DFRobot `DFR0954` remains
an unqualified amplifier alternative; do not substitute it for a MAX98357A
breakout without revisiting the rail analysis in the materials decision.

The editable corrected source build uses 16 kHz duplex audio, receives mic data
on GPIO4 so GPIO8 can retain a defined high boot strap, probes SSD1306 at
`0x3C` and `0x3D`, and continues headless when no display answers. GPIO10 is
the active-low action/config input; GPIO9 remains ROM BOOT. The
[project overview](../edu/01-how-it-fits-together.md) summarizes this
corrected-source logical contract. This README and the board configuration
remain authoritative for firmware details. Do not mix the two wiring
contracts.

## Directory layout

```text
firmware/
├── partitions/       reviewed 4 MB partition table
├── patches/          Xiaozhi CMake/Kconfig board registration
├── scripts/          setup, prepare, build, record, verify, and flash entry points
├── src/boards/       project-owned board adapter and pin configuration
├── dependencies.lock pinned ESP-IDF component graph and registry hashes
├── source-build.json reference build record (local builds use dist/source-build.json)
├── sdkconfig.defaults
└── versions.env      pinned source and SDK versions
```

`scripts/prepare.sh` creates an ignored checkout under `.work/`, verifies the
exact upstream commit, applies the registration patch, and copies the reviewed
board files. A plain `prepare.sh` preserves and rejects a mismatched checkout.
`prepare.sh --refresh` archives that checkout instead of deleting it, then
prepares the updated overlay. `build.sh` uses this recoverable refresh
automatically, so an intentional source edit does not require manual cache
surgery. Build products go to ignored `dist/`.

## Build

The helper scripts require Bash and Python 3.10 or newer. Linux/macOS users
can use `setup.sh` above; Windows users should use a configured WSL environment
and arrange USB forwarding for the device. Git must already be installed. If
SDK setup reports a missing OS package such as Python venv support, install
that named prerequisite with your OS package manager and rerun setup; do not
run the firmware or flashing workflow as root.

An existing official Espressif ESP-IDF `v6.0.2` checkout at commit
`7101770dc6db2667b3c477cc31365dd1acd6db4e` can also be used: source its
`export.sh` instead. The build rejects a different SDK commit or tracked SDK
modifications. Python tool versions are recorded from the actual environment.

From the repository root:

```bash
firmware/scripts/build.sh
```

The build script rejects a different SDK version, regenerates `sdkconfig`, adds
the board overrides, compiles the app and default assets, and creates:

```text
firmware/dist/pocket-wall-e-c3-v2.4.0-idf-v6.0.2.bin
```

That file is a complete merged 4 MB-layout image for offset `0x0`. The app
partition begins at `0x10000`; do not write the merged image there.
Read the exact size, digest, and selected mode from `dist/source-build.json`
or run the verifier. There is intentionally no second, manually maintained
checksum in this README. A changed source input or modified binary after the
build fails verification; rebuild intentionally instead of bypassing the check.

To change an ordinary Kconfig option permanently, edit `sdkconfig.defaults` and
rerun the build. The CLI selects diagnostics versus assistant mode explicitly
and holds amplifier enable off. Temporary `menuconfig` edits are intentionally
replaced on the next scripted build. Source modifications belong in `src/` or
`patches/`, not the generated `.work/` checkout; refreshed checkouts are archived
so any earlier experiments remain recoverable.

## Flash and monitor source builds

For the USB bench prototype, use only the controller, button, and optional
OLED/microphone powered by the controller's 3.3 V output. Disconnect the
battery, charger, external regulators, amplifier, and all separately powered
wiring. A controller-powered peripheral is not an external supply; an
unpowered regulator connected to the same rail still is a back-power path.
Unplug USB before changing any wiring. Do not flash a permanently assembled
multi-supply harness until its service-isolation scheme is tested.
Then identify the serial port, close other serial
monitors, preview the operation, and run it, for example:

```bash
firmware/scripts/flash.sh /dev/ttyACM0 --dry-run
firmware/scripts/flash.sh /dev/ttyACM0 --monitor
```

Use the actual port on the host (`/dev/cu.*` on macOS; use the serial path exposed
inside WSL/Git Bash on Windows). The script requires typing the exact target
unless `--yes` is deliberately used for automation. It verifies the complete
merged image and byte-producing local inputs, then invokes esptool directly at
offset `0x0`; the flash step cannot trigger a rebuild after verification. Its
blank NVS area clears existing Wi-Fi settings. If automatic reset fails,
hold the module's GPIO9 **BOOT** button, tap RESET or reconnect USB, release
BOOT, and retry.

The default diagnostic image reports its mode over USB and remains offline;
use the quickstart to interpret the OLED and microphone results. No raw
recording is saved. Missing peripherals are reported, not prerequisites for
controller bring-up.

**Assistant mode only:** on a clean first boot, connect to the expected
device-specific `Xiaozhi-XXXX`
Wi-Fi provisioning access point, confirm its actual name in the boot log, and
open <http://192.168.4.1> if the captive portal does not appear. Xiaozhi's
default build uses `https://api.tenclass.net/xiaozhi/ota/` as its third-party
bootstrap service. Review that service's privacy and operational requirements
before sending microphone audio to it.

This 4 MB layout has a factory application and no OTA application slot. The
firmware hides the unsupported manual-update tool and refuses OTA before
changing application state. Update this prototype using the USB flash helper,
not an online firmware-update command.
