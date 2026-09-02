# 3 — Corrected-source wiring contract

> **Scope:** this is the signal and integration contract for the corrected
> editable firmware. It is not a released power schematic. The build manifest
> records `hardware_tested: false`, so every physical claim below remains a
> qualification requirement until measured on identified received parts.

Read [How the system fits together](01-how-it-fits-together.md) for the block
diagram and the [foundations course](fundamentals/README.md) for the electrical
theory.

## Firmware signal map

| ESP32-C3 connection | Peripheral connection | Contract |
| --- | --- | --- |
| GPIO1 | INMP441 `WS`; MAX98357A `LRC`/`LRCLK` | Shared I2S word select, 16 kHz |
| GPIO2 | INMP441 `SCK`; MAX98357A `BCLK` | Shared I2S bit clock, expected 1.024 MHz; boot strap must remain valid at reset |
| GPIO3 | MAX98357A-module `DIN` | ESP32-C3 audio data output |
| GPIO4 | INMP441 `SD` | Microphone data input for the corrected source |
| GPIO10 | Normally-open action button to GND | Active-low application input; firmware enables an internal pull-up |
| GPIO20 | OLED `SCL` | I2C clock, requested 400 kHz |
| GPIO21 | OLED `SDA` | I2C data |
| GPIO18/GPIO19 | Module USB D−/D+ | Reserved for native USB service in this design |
| 3.3 V | Compatible module supply inputs | Intended regulated distribution, not approved here; verify each received module's input label and range |
| GND | Every logic/power module GND; INMP441 `L/R` for the intended slot | Common insulated reference/return; never the frame |

The signal names on a breakout are connector labels, not a guarantee about its
pin order or fitted circuit. Read each received PCB's silkscreen and exact
documentation before connecting power.

## Firmware identity matters

| Firmware | Microphone data | Audio rate | OLED behavior |
| --- | ---: | ---: | --- |
| Corrected editable source | GPIO4 | 16 kHz input/output | Probe `0x3C`, then `0x3D`; continue headless if initialization fails |
| Creator/vendor binary | GPIO8 | 24 kHz | Recovered contract uses `0x3C` |

This Rev A signal map targets the corrected source. Confirm the actual image
before attaching the harness. The source-build record proves repeatable
compilation on its validation host; it does not prove a flashed board, display,
microphone, amplifier, speaker, radio, or assistant service.

## Power and service boundary

During first bring-up, use a current-limited 3.3 V bench source and no lithium
cell. This note intentionally does not select or approve the converter,
protection, switching, charging, or service-isolation topology.

Native USB can power the ESP32-C3 module. It must not be allowed to back-drive
an unpowered peripheral rail or converter. Before connecting USB to an
assembled unit, open a reviewed service disconnect or otherwise prove by
schematic review and measurement that the external 3.3 V distribution is
isolated. Cell removal alone does not prove that condition.

Every ground connection uses insulated wire. With all power absent, verify that
the metal frame is open/high-resistance to ground, both supply domains, every
signal, and both speaker outputs.

## Module-specific conditions

- **OLED:** `0x3C` and `0x3D` are candidate 7-bit addresses, not identities.
  Inventory fitted pull-ups, verify idle SDA/SCL near 3.3 V, scan, initialize,
  and measure rise time before accepting 400 kHz.
- **Microphone:** set `L/R` for the slot expected by firmware, verify the
  documented SD pull-down, and keep the acoustic port free of flux, solvent,
  glue, paint, hot air, and compressed air.
- **Amplifier:** use the exact purchased MAX98357A module's schematic or
  received-board measurements for `SD`/channel and gain configuration. Do not
  transplant DFRobot, Adafruit, or clone resistor assumptions between boards.
- **Speaker:** connect it only between `OUT+` and `OUT−`. Neither terminal is
  ground. Start at low digital volume and qualify the actual enclosure.
- **Bypassing and returns:** inspect the capacitors already fitted to every
  module. Add required local bypassing close to each load with a short return;
  keep amplifier/speaker current out of the microphone return path.
- **Radio:** keep the antenna end clear of the cell, frame, dense wiring,
  conductive coatings, and guards, then verify RSSI and reconnect behavior in
  the intended geometry.

## Staged integration

1. Flash and identify a bare ESP32-C3 with the external harness disconnected.
2. Qualify the OLED and its I2C electrical behavior.
3. Measure WS and BCLK before adding audio data paths.
4. Add and validate the microphone.
5. Add the amplifier and enclosed speaker at low volume.
6. Exercise Wi-Fi and simultaneous audio from a current-limited source.
7. Qualify the complete power chain and service isolation separately.
8. Dry-fit actual parts and insulation; only then make permanent frame joints.

Use [the acceptance worksheet](06_ACCEPTANCE_TESTS.md) as the record. A boot,
an address ACK, or audible sound is one observation—not final acceptance.
