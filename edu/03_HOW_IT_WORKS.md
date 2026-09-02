# 3 — Corrected-source wiring contract

> **Scope:** this is the signal and integration contract for the corrected
> editable firmware. It is not a released power schematic. The build manifest
> records `hardware_tested: false`, so every physical claim below remains a
> qualification requirement until measured on identified received parts.

The exact Phase 0 candidates and their status live in
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md). The
candidate power topology and its rules are in that record and
[the power-chain worksheet](07-the-power-chain.md); this lesson is the signal
side of the contract.

Read [How the system fits together](01-how-it-fits-together.md) for the block
diagram and the [foundations course](fundamentals/README.md) for the electrical
theory.

## Firmware signal map

| ESP32-C3 connection | Peripheral connection | Contract |
| --- | --- | --- |
| GPIO1 | #6049 ICS-43434 `WS/LRCLK` directly; MAX98357A `LRC` through candidate isolator channel 1 | Shared I2S word select, 16 kHz |
| GPIO2 | #6049 ICS-43434 `BCLK` directly; MAX98357A `BCLK` through candidate isolator channel 2 | Shared I2S bit clock: 64 clocks per frame × 16,000 frames/s = 1.024 MHz; GPIO2 boot-strap behavior must remain valid at reset |
| GPIO3 | Candidate isolator channel 3 → MAX98357A `DIN` | ESP32-C3 audio data output |
| GPIO4 | #6049 ICS-43434 `DOUT` (alternate: INMP441 `SD`) | Microphone data input for the corrected source |
| GPIO5 | Candidate TXU0104 A4, with 4.7 kΩ to GND; B4 drives MAX98357A `SD_MODE` with its own 4.7 kΩ to GND. #2873 open-drain `PG` drives translator `OE`, pulled up through 10 kΩ to 5V_SYS | **Not implemented/frozen:** configure GPIO5 low at earliest init, start continuous I2S clocks with zero data, then raise GPIO5 after the MCU startup/rail delay and valid I2S. `PG` independently vetoes `OE`; the MCU does not sense `PG` in this candidate. Do not use an API that resets/enables a pull-up on this MTDI pad |
| GPIO10 | Normally-open action button to GND | Active-low application input; firmware enables an internal pull-up |
| GPIO20 | OLED `SCL` | I2C clock, requested 400 kHz |
| GPIO21 | OLED `SDA` | I2C data |
| GPIO18/GPIO19 | Module USB D−/D+ | Reserved for native USB service in this design |
| 3.3 V | OLED `VCC`, microphone `VDD`, candidate isolator `VCCA` | From the SuperMini's LDO output |
| 5V_SYS | MAX98357A `VIN`, candidate isolator `VCCB` | From #2873 in the candidate whole-load architecture; not a released wiring schematic |
| GND | Every logic/power module GND; #6049 `SEL` low (INMP441 alternate: `L/R` low) for the left slot | Common insulated reference/return; never the frame |

The signal names on a breakout are connector labels, not a guarantee about its
pin order or fitted circuit. Read each received PCB's silkscreen and exact
documentation before connecting power.

## Firmware identity matters

| Firmware | Microphone data | Audio rate | OLED behavior |
| --- | ---: | ---: | --- |
| Corrected editable source (R1 wiring) | GPIO4 | 16 kHz input/output | Probe `0x3C`, then `0x3D`; continue headless if initialization fails |
| Historical creator/vendor binary and video-era microphone harness | GPIO8 | 24 kHz | Recovered contract uses `0x3C` |

This Rev A signal map targets the corrected source. Confirm the actual image
before attaching the harness. The source-build record proves repeatable
compilation on its validation host; it does not prove a flashed board, display,
microphone, amplifier, speaker, radio, or assistant service.

### Microphone choice

Adafruit **#6049 ICS-43434** (`SEL` → GND) is the Phase 0 primary. INMP441
(`L/R` → GND) is a held alternative. Their I2S signals are analogous, but
their carrier pin orders are not interchangeable. Photograph the exact board,
follow that carrier's documentation, and prove slot/word alignment and
intelligible capture before final soldering.

DFRobot `DFR0954` remains a held amplifier alternative. The Phase 0 primary is
Adafruit `#3006`; repeat supply, gain/mode, noise, current, thermal, and fit
qualification for any substitute.

## Power and service boundary

During first bring-up, use a current-limited bench source at the future cell
input and no lithium cell. Measure voltage at each module pin under load; a
source setting is not proof that a module remains within its published range.
The current candidate topology and gates are in
[the material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md).

Native USB can power a bare ESP32-C3 module. Until the received clone's
VBUS/5V path and proposed supply **and I2S/control** isolation pass every
reset/bootloader/source-state test,
service it only while detached from the cell and external power harness. This
procedural limit is not a substitute for the final electrical design.

Every ground connection uses insulated wire. With all power absent, verify that
the metal frame is open/high-resistance to ground, both supply domains, every
signal, and both speaker outputs.

## Module-specific conditions

- **OLED:** `0x3C` and `0x3D` are candidate 7-bit addresses, not identities.
  Inventory fitted pull-ups, verify idle SDA/SCL near 3.3 V, scan, initialize,
  and measure rise time before accepting 400 kHz.
- **Microphone:** tie the slot select low (INMP441 `L/R`, ICS-43434 `SEL`),
  then prove the exact bit/slot alignment and intelligible capture at 16 kHz
  and 1.024 MHz BCLK. Protect the acoustic port from flux, solvent, glue,
  paint, hot air, compressed air, and a sealing guard.
- **Amplifier:** inspect the received MAX98357A board for `SD`/channel and
  gain configuration. It accepts a documented 2.5–5.5 V supply and supports
  the 16 kHz contract. Source inspection predicts active left and inactive
  right TX slots; hardware capture must confirm that. Do not assume the
  board's default left/right mix gives full amplitude. Qualify its `SD` mode
  and select left explicitly if the capture confirms an inactive right slot.
  Measure the board's real envelope including any screw terminal.
- **Speaker:** the open Same Sky `CMS-20143-158SP` is the Phase 0 primary and
  needs a repeatable sealed rear cavity. The factory-enclosed
  `CES-20134-088PM` is the separately capped comparison. Connect only one at a
  time between the amplifier's BTL outputs; neither terminal is ground. Start
  at low digital volume and qualify differential RMS power, front outlet,
  grille, mounting, feedback, current, and temperature.
- **Bypassing and returns:** inspect the capacitors already fitted to every
  module. Add required local bypassing close to each load with a short return;
  keep amplifier/speaker current out of the microphone return path.
- **Radio:** keep the antenna end clear of the cell, frame, dense wiring,
  conductive coatings, and guards, then verify RSSI and reconnect behavior in
  the intended geometry.

## Staged integration

1. Flash and identify a bare ESP32-C3 with the external harness disconnected.
2. Qualify the OLED and its I2C electrical behavior.
3. With data paths absent, measure 16 kHz WS and 1.024 MHz BCLK (64 clocks per
   frame) and prove normal boot plus ROM-download recovery with both clock
   recipients attached.
4. Add the #6049 ICS-43434 primary microphone on GPIO4 and validate slot/word
   alignment and capture quality.
5. Add the MAX98357A into an 8 Ω dummy load first. Then A/B the open
   `CMS-20143-158SP` primary in its sealed fixture against the separately
   capped enclosed `CES-20134-088PM`, one at a time and at low volume. Keep
   both BTL leads off ground and the frame; record differential RMS voltage,
   amplifier-pin voltage, `SD` mode voltage, gain state, current, and
   temperature.
6. Exercise Wi-Fi and simultaneous audio from a current-limited source.
7. Run [the power-chain bench worksheet](07-the-power-chain.md) — the sweep,
   switch, drop, and thermal rows.
8. Dry-fit actual parts and insulation; only then make permanent frame joints.

Use [the acceptance worksheet](06_ACCEPTANCE_TESTS.md) as the record. A boot,
an address ACK, or audible sound is one observation—not final acceptance.
