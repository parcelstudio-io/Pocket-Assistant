# Pocket AI Assistant — working notes for Claude

A reviewable reconstruction of the Huy Vector Pocket AI Assistant: a pinned
vendor image, host-side flashing tools, a source-buildable ESP32-C3 board port,
an audited bill of materials, and a staged build plan. The hardware is an
ESP32-C3 SuperMini with an SSD1306 OLED and an I2S MEMS microphone.

## Which document is authority

This repository deliberately keeps superseded proposals for review. Citing an
archived document as current guidance is the most damaging mistake here.

| Authoritative | Archived — never cite as current |
| --- | --- |
| `plan/FAST_TRACK.md` — the action guide; order, wiring, pass conditions | `docs/MATERIALS.md` — R1 order sheet, **do not order from it** |
| `plan/FAST_TRACK_PARTS.md` — parts by step, with provenance marks | `docs/WIRING_AND_ASSEMBLY.md` — R1 power wiring, not assembly authority |
| `plan/FAST_TRACK_THEORY.md` — the explanations behind each step | `docs/BUILD_GUIDE.md` — video correlation; final assembly is held |
| `docs/INVENTORY.md` — what was actually purchased | `docs/CLAUDE_R1_BUILD_PROPOSAL.md` — superseded complete-cart decision |
| `docs/FINAL_MATERIALS_FOR_REVIEW.md` — Phase 0 purchase authority, promotion gates | `docs/BOM.md` — historical reconciliation |

`docs/PROTOTYPE_QUICKSTART.md` is the compact technical reference for
troubleshooting; `plan/DAILY_STUDY_AND_LAB_PLAN.md` is the deep 15-session
track. Distinguish a **recorded purchase** from a **candidate link** before
telling the user they own a part — `FAST_TRACK_PARTS.md` marks the difference.

## Safety invariants

These are not style preferences. Do not relax them, and do not write
instructions that violate them.

- The current prototype is **USB-powered only**. Battery, charger, external
  regulators, amplifier, and the metal case stay off it.
- OLED and microphone power comes only from the controller's 3.3 V output.
  Never connect an external source to that rail while USB is connected.
- Never connect both USB-C ports at once. SuperMini clones vary in their
  VBUS/`5V` arrangement, so no clone diode may be assumed.
- Never strip a lithium cell, solder to its can, use the brass frame as a
  conductor, or charge an undocumented cell.
- Read the OLED silkscreen before wiring: vendors ship `GND-VCC-SCL-SDA` and
  `VCC-GND-SCL-SDA` on identical-looking boards.

## Hardware contract (corrected source build)

| Function | Signal | GPIO |
| --- | --- | ---: |
| OLED I2C | SDA / SCL | 21 / 20 |
| Shared I2S clocks | WS / BCLK | 1 / 2 |
| Microphone data | ICS-43434 primary (`SEL`→GND); INMP441 alternate (`L/R`→GND) | 4 |
| Amplifier output | MAX98357A DIN | 3 |
| Action button | active-low | 10 |

OLED address `0x3c` or `0x3d` (firmware probes both), 16 kHz duplex audio.
GPIO9 is the ROM BOOT button, not an application input.

The **pinned vendor image is different**: microphone data on GPIO8, 24 kHz
audio, OLED `0x3c` only. Never mix the two pinouts in one instruction.

## Commands

```bash
# source port (recommended path); setup is needed once
firmware/scripts/setup.sh
. firmware/.work/esp-idf/export.sh   # again in every new shell
firmware/scripts/build.sh            # defaults to offline diagnostics

# host tools and tests
python3 -m unittest discover -s tools/tests -v
python tools/netcheck.py
```

`build.sh --assistant` is only for after the offline tests pass. The historical
vendor-image CLI is `tools/pocket_ai_device.py`; it needs an explicit `--port`.

## Evidence discipline

`firmware/source-build.json` still records `hardware_tested: false`, and it
stays that way: `record_source_build.py` hard-codes it, and the flag means
"this build workflow tested hardware", which it never has. Do not hand-edit it.

The builder separately established `PASS 9` on a physical board on 2026-09-20
— the complete USB prototype, two cold starts — and reported `PASS 10C` on
2026-09-21: board `A1` joined Wi-Fi under the 8.5 dBm transmit-power cap and
one spoken question returned a remote response from the Xiaozhi backend.
Treat Steps 0-10 of `plan/FAST_TRACK.md` as passed on hardware, and cite the
builder's lab record rather than the manifest for that. No assembled battery
circuit has been connected; the amplifier remains disabled, so there is still
no spoken output; nothing past Step 10 is established.

A matching checksum or a successful compile still does not prove hardware
operation — do not write that it does, and do not mark a step passed that the
user has not run. When a claim is untested, say so in the text rather than
implying verification.
