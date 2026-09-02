# Pocket AI Assistant firmware

This directory provides a buildable source overlay for the Pocket AI Assistant's
ESP32-C3 hardware. It pins the public Xiaozhi application, adds the project's
board registration and confirmed pin map, forces the real 4 MB flash layout,
and produces a merged image that can be flashed at address `0x0`.

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
- Two clean builds on the validation host with the pinned inputs produced
  identical merged images. Their reference size/SHA-256, byte-producing local
  input hashes, effective configuration hash, and observed tool versions are
  recorded in `source-build.json` so a local rebuild can be compared.
- The source and configuration can be compiled without the device. Electrical,
  microphone, speaker, button, and end-to-end assistant behavior still require
  a hardware smoke test.

The source build additionally diverges for English users: wake word
`wn9s_hiesp` ("Hi, ESP") and `CONFIG_LANGUAGE_EN_US` replace the vendor
image's Mandarin `wn9s_nihaoxiaozhi` and zh-CN strings (both set in
`sdkconfig.defaults` and the board `config.json`; the explicit
`# CONFIG_SR_WN_WN9S_NIHAOXIAOZHI is not set` line is required because the
WakeNet9s entries are independent bools, not a choice group).

For the exact published image and its pinned checksum, use the
[host flashing and verification tools](../tools/README.md).

## Vendor-image and corrected-source pin maps

| Function | ESP32-C3 GPIO | Peripheral connection |
| --- | ---: | --- |
| I2S word select | 1 | INMP441 WS and MAX98357A LRC |
| I2S bit clock | 2 | INMP441 SCK and MAX98357A BCLK |
| I2S speaker data | 3 | MAX98357A DIN |
| I2S microphone data | 8 in vendor image; **4 in corrected source** | INMP441 SD |
| Optional action/config input | 10 | Active-low push button to GND if fitted |
| OLED SCL | 20 | SSD1306 SCL |
| OLED SDA | 21 | SSD1306 SDA |

The published vendor image uses SSD1306 address `0x3c`, 24 kHz full-duplex
audio, and microphone GPIO8. Those values were recovered from the binary and
are retained only for wiring an exact-video replica.

The editable corrected source build uses legal 16 kHz duplex audio, moves mic
data to GPIO4 so GPIO8 can retain a defined high boot strap, probes SSD1306 at
`0x3c` and `0x3d`, and continues headless when no display answers. GPIO10 is
the active-low action/config input; GPIO9 remains ROM BOOT. The authoritative
Rev A harness in [`edu/03_HOW_IT_WORKS.md`](../edu/03_HOW_IT_WORKS.md) targets
this corrected source build. Do not mix the two wiring contracts.

## Directory layout

```text
firmware/
├── partitions/       reviewed 4 MB partition table
├── patches/          Xiaozhi CMake/Kconfig board registration
├── scripts/          prepare, build, verify, and hardware-flash entry points
├── src/boards/       project-owned board adapter and pin configuration
├── dependencies.lock pinned ESP-IDF component graph and registry hashes
├── source-build.json validated source-build size, digest, and inputs
├── sdkconfig.defaults
└── versions.env      pinned source and SDK versions
```

`scripts/prepare.sh` creates an ignored checkout under `.work/`, verifies the
exact upstream commit, applies the registration patch, and copies the reviewed
board files. It never replaces a mismatched checkout, so local experiments are
not silently deleted. Build products go to the ignored `dist/` directory.

## Build

The helper scripts require Bash (Linux/macOS, or a correctly configured WSL or
Git Bash environment on Windows). Install Git, Python 3, CMake/Ninja
prerequisites, and the official Espressif
ESP-IDF `v6.0.2` Git checkout at commit
`7101770dc6db2667b3c477cc31365dd1acd6db4e`. Follow Espressif's
platform-specific installation instructions, then activate that SDK in the
same Bash shell by sourcing its `export.sh`. The build rejects a different SDK
version/commit or tracked modifications in the SDK checkout.

From the repository root:

```bash
firmware/scripts/prepare.sh
firmware/scripts/build.sh
```

The build script rejects a different SDK version, regenerates `sdkconfig`, adds
the board overrides, compiles the app and default assets, and creates:

```text
firmware/dist/pocket-wall-e-c3-v2.4.0-idf-v6.0.2.bin
```

That file is a complete merged 4 MB-layout image for offset `0x0`. The app
partition begins at `0x10000`; do not write the merged image there.
For the pinned inputs, the expected merged image is 3,541,638 bytes with
SHA-256 `7f1827f21e1cfa71545025d9dc6067bf25c6d65214ace11da870f8b860ce9104`.
The machine-readable record is in `source-build.json`; a different digest is a
reason to inspect the host tool versions and inputs before flashing. The flash
helper refuses it rather than assuming cross-host output identity.

To change a Kconfig option permanently, edit `sdkconfig.defaults` and rerun the
build. Move the existing `.work/xiaozhi-esp32` checkout aside only after changing
the source overlay or patch, because `prepare.sh` deliberately refuses to
replace a nonmatching worktree. Temporary `menuconfig` edits are intentionally
replaced on the next scripted build.

## Flash and monitor source builds

During Phase 0, connect a bare SuperMini with its external 3.3 V/peripheral
harness disconnected. Cell removal alone does not prevent USB from driving the
shared 3.3 V rail and reverse-driving an unpowered regulator. Do not flash a
permanently assembled harness until its reviewed service-isolation scheme is
installed and tested. Then identify the serial port, close other serial
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

On a clean first boot, connect to the expected device-specific `Xiaozhi-XXXX`
Wi-Fi provisioning access point, confirm its actual name in the boot log, and
open <http://192.168.4.1> if the captive portal does not appear. Xiaozhi's
default build uses `https://api.tenclass.net/xiaozhi/ota/` as its third-party
bootstrap service. Review that service's privacy and operational requirements
before sending microphone audio to it.
