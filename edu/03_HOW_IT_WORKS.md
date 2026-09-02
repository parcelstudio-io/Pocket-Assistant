# 3 — Corrected-source wiring contract

> **Scope:** this is the signal and integration contract for the corrected
> editable firmware. It is not a released power schematic. The build manifest
> records `hardware_tested: false`, so every physical claim below remains a
> qualification requirement until measured on identified received parts.

The exact released parts and their status live in
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md) (R1
build release). The power topology and its rules are in that record and
[the power-chain worksheet](07-the-power-chain.md); this lesson is the signal
side of the contract.

Read [How the system fits together](01-how-it-fits-together.md) for the block
diagram and the [foundations course](fundamentals/README.md) for the electrical
theory.

## Firmware signal map

| ESP32-C3 connection | Peripheral connection | Contract |
| --- | --- | --- |
| GPIO1 | INMP441 `WS` (alternate: ICS-43434 `WS/LRCLK`); MAX98357A `LRC` | Shared I2S word select, 16 kHz |
| GPIO2 | INMP441 `SCK` (alternate: ICS-43434 `BCLK`); MAX98357A `BCLK` | Shared I2S bit clock: 64 clocks per frame × 16,000 frames/s = 1.024 MHz; GPIO2 boot-strap behavior must remain valid at reset |
| GPIO3 | MAX98357A `DIN` | ESP32-C3 audio data output |
| GPIO4 | INMP441 `SD` (alternate: ICS-43434 `DOUT`) | Microphone data input for the corrected source |
| GPIO10 | Normally-open action button to GND | Active-low application input; firmware enables an internal pull-up |
| GPIO20 | OLED `SCL` | I2C clock, requested 400 kHz |
| GPIO21 | OLED `SDA` | I2C data |
| GPIO18/GPIO19 | Module USB D−/D+ | Reserved for native USB service in this design |
| 3.3 V | OLED `VCC`, microphone `VDD` | From the SuperMini's LDO output; the amp's `VIN` instead takes the switched battery rail (see [the power worksheet](07-the-power-chain.md)) |
| GND | Every logic/power module GND; INMP441 `L/R` low (ICS-43434: `SEL` low) for the left slot | Common insulated reference/return; never the frame |

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

The R1 primary is the creator-faithful **INMP441** breakout (`L/R` → GND);
the documented alternate is the Adafruit `#6049` ICS-43434 (`SEL` → GND).
Both are 24-bit, 64-SCK I2S parts that are in-spec at this contract's
1.024 MHz bit clock, and the firmware needs no change between them. Whichever
arrives, photograph the exact breakout, verify its silkscreen pin order, and
prove slot/word alignment and intelligible capture before final soldering —
IC-level claims never transfer blindly to an anonymous carrier.

DFRobot `DFR0954` remains an unqualified amplifier alternative. The MAX98357A
breakouts document a 2.5–5.5 V supply, which the R1 raw-cell rail sits inside;
DFR0954's published 3.3 V minimum does not. Do not substitute it without
revisiting the rail analysis.

## Power and service boundary

During first bring-up, use a current-limited bench source at the pack's JST
position and no lithium cell. Measure voltage at each module pin under load; a
source setting is not proof that a module remains within its published range.
The released power topology and its bench worksheet are in
[the power-chain lesson](07-the-power-chain.md).

Native USB can power the ESP32-C3 module. The R1 service rule is physical:
**slide switch OFF and pack JST unplugged before the SuperMini's USB-C is
connected**, and never both USB-C ports (SuperMini and charger) at once. With
the pack out of circuit, USB feeds only the SuperMini's LDO and the 3.3 V
peripherals — all rated for it.

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
  the 16 kHz contract. The default mode is a left/right average while the
  firmware transmits the left slot — which plays at full amplitude because
  the ESP32-C3 duplicates the mono slot (see
  [the audio lesson](04-audio.md)); meter `SD` (~0.30 V stock; ~0 V =
  shutdown = rework). Measure the board's real envelope including any screw
  terminal.
- **Speaker:** the factory-enclosed Same Sky `CES-20134-088PM` connects only
  between the amplifier's BTL outputs. Neither terminal is ground. Start at
  low digital volume; qualify its front outlet, grille, mounting, feedback,
  current, and temperature. Do not design an added rear cup for this already
  enclosed part.
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
4. Add the microphone (INMP441 primary) on GPIO4 and validate slot/word
   alignment and capture quality.
5. Add the MAX98357A and factory-enclosed Same Sky `CES-20134-088PM` at low
   software volume; keep both BTL leads off ground and the frame. Record the
   amplifier-pin voltage, `SD` mode voltage, gain state, current, and
   temperature.
6. Exercise Wi-Fi and simultaneous audio from a current-limited source.
7. Run [the power-chain bench worksheet](07-the-power-chain.md) — the sweep,
   switch, drop, and thermal rows.
8. Dry-fit actual parts and insulation; only then make permanent frame joints.

Use [the acceptance worksheet](06_ACCEPTANCE_TESTS.md) as the record. A boot,
an address ACK, or audible sound is one observation—not final acceptance.
