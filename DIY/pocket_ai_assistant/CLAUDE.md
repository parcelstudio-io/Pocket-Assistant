# Pocket AI Assistant — working notes for Claude

A reviewable reconstruction of the Huy Vector Pocket AI Assistant: a pinned
vendor image, host-side flashing tools, a source-buildable ESP32-C3 board port,
an audited bill of materials, and a staged build plan. The hardware is an
ESP32-C3 SuperMini with an SSD1306 OLED and an I2S MEMS microphone, plus, from
fast-track Step 11, a MAX98357A amplifier and speaker on the same USB supply.
By the builder's decision of 2026-09-21 the prototype is a USB-powered home
device; portable battery power is out of scope.

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

- The brass prototype is **USB-powered only** (builder's decision of 2026-09-21).
  On 2026-10-11 the builder decided the **final build will carry a battery**: a
  power-path board (Adafruit PowerBoost 1000C class: load sharing, 5 V boost,
  EN as the switch) feeds the harness's two 5 V entry points, the 1200 mAh cell
  (#258) is the only owned cell rated for the load, and that needs a larger
  frame; A1's own USB port is blocked in that build. Until that page exists,
  nothing battery-related connects to the prototype: battery, charger and
  external regulators stay off it, and the metal case rule below still holds. The amplifier may be connected only as fast-track Step 11 describes:
  `VIN` from the controller's `5V` pin on the same USB supply, `SD` on GPIO5
  with a pull-down, first output into a dummy load. By the builder's decision
  of 2026-09-22 the speaker may instead go on directly at a volume cap of 30 or
  less (Step 11's prototype shortcut). By the builder's decision of 2026-09-30
  that limit is raised to a cap of 45 (datasheet worst case 2.20 V peak at the
  highest gain, against the speaker's 2.53 V); a cap above 45 goes through the
  dummy load and PASS 11B first. By the builder's decision of 2026-10-26 the Pip
  character firmware runs at a cap of 65, justified by the GAIN pin being left open
  (9 dB: full scale 5.43 V peak, cap 65 = 2.29 V peak, 2.06 V measured on speech);
  the firmware refuses anything above 65, and the figure no longer holds if GAIN is
  ever strapped higher.
- Neither speaker output is ground. Never connect `OUT+` or `OUT−` to GND, and
  never clip a scope ground to either.
- OLED and microphone power comes only from the controller's 3.3 V output.
  Never connect an external source to that rail while USB is connected.
- Never connect both USB-C ports at once. SuperMini clones vary in their
  VBUS/`5V` arrangement, so no clone diode may be assumed. On board `A1` the
  builder measured the `5V` pin as USB VBUS directly, with no diode
  (2026-09-22), matching the published SuperMini schematic: never connect
  any other source to `5V` while USB is in.
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
| Amplifier shutdown | MAX98357A `SD`, pull-down to GND | 5 |
| Action button | active-low | 10 |

OLED address `0x3c` or `0x3d` (firmware probes both), 16 kHz duplex audio.
GPIO9 is the ROM BOOT button, not an application input.

Resistors, by the builder's decision of 2026-10-14: the amplifier's `SD`
pull-down (R1, 4.7 kΩ against the breakout's 1 MΩ pull-up) stays; the
10 kΩ `GPIO2`-to-3V3 pull-up (R3) stays until a meter shows the SuperMini
carries its own; the `GAIN` resistor (R2) is dropped, so `GAIN` floats at
9 dB; the external mic-`SD` pull-down (R4) is dropped because the Pip
firmware enables GPIO4's internal pull-down. Do not write instructions that
fit R2 or R4 unless the builder reverses this.

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

`build.sh --assistant` is only for after the offline tests pass.
`build.sh --assistant --amplifier` is for Step 11 only, after PASS 11A. The historical
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
builder's lab record rather than the manifest for that. No battery circuit
exists or is planned for this prototype. Step 11 exists on paper and in the
build scripts but has not run on hardware, so there is still no spoken output;
nothing past Step 10 is established.

A matching checksum or a successful compile still does not prove hardware
operation — do not write that it does, and do not mark a step passed that the
user has not run. When a claim is untested, say so in the text rather than
implying verification.

## The character stack (`character/`, from 2026-10-08)

`character/` is the builder's own firmware and server, replacing the Xiaozhi
image for the finished device: `character/server` (Python, OpenAI or Ollama
behind one WebSocket, `PROTOCOL.md`), `character/firmware` (ESP-IDF 6.0.2,
C, animated eyes on the OLED, push-to-talk), `character/eyes/preview.html`
(the eye model in a browser). It keeps every safety invariant above: amplifier
off unless `CONFIG_POCKET_ENABLE_AMPLIFIER`, volume cap ≤ 45 squared, silent
clocks before SD, the 8.5 dBm transmit cap, the source-build pinout. As of
2026-10-08 it has not run on hardware; `character/README.md` says what is and
is not verified.
