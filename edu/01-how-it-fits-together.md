# How the Pocket Assistant fits together

> **Evidence status:** the corrected firmware configuration has been built
> reproducibly, but its manifest still says `hardware_tested: false`. The
> diagram below is the intended integration contract, not evidence that the
> received modules, power path, wiring, radio, audio, or enclosure have passed
> physical qualification.

> **Current identity:** Adafruit `#6049` ICS-43434 on GPIO4 is the Phase 0
> primary microphone; INMP441 is a held alternative. Their I2S signals are
> analogous, but carrier pin order is not interchangeable. The MAX98357A data
> input is on GPIO3. Purchase authority is the status-marked Phase 0 list in
> [FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md).

For the underlying circuit ideas, begin with the
[EE foundations course](fundamentals/README.md). This note applies those ideas
to the current prototype.

## System boundary

```text
 current-limited bench source at future cell input
              OR future qualified cell subsystem
                              │
                     candidate #2873
                              │ 5V_SYS
                  ┌───────────┴──────────────┐
                  ▼                          ▼
            #3006 amplifier      diode → SuperMini 5V → LDO → 3V3
                  ▲                                      │
                  │                    ┌─────────────────┼──────────────┐
        TXU0104 A→B boundary           ▼                 ▼              ▼
      (held; PG-gated `OE`)        ESP32-C3           OLED      #6049 microphone
                  ▲                    │ I2C/I2S/button
                  └── WS/BCLK/DIN ─────┘
                  │ BTL + / −
                  ▼
      CMS-20143-158SP primary / CES-20134-088PM comparison

 USB-C reaches the ESP32-C3 only under the reviewed service-isolation
 condition; it is not a second source for the external 3.3 V distribution.
```

The frame is intended to be mechanical structure only. It must remain isolated
from raw power, 3.3 V, ground, every signal, and both speaker leads. That is an
acceptance test, not an assumption.

This overview deliberately does not freeze a converter, fuse, switch,
protection, charging, or USB-isolation circuit. Those choices belong in the
[current material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md), a reviewed
power schematic, and recorded power-chain tests. Until those tests pass, use a
current-limited bench supply and keep the lithium cell out of the assembly.

## Electrical interfaces

| Interface or net | Current project use | What still needs hardware proof |
| --- | --- | --- |
| 3.3 V and GND | Supply/reference for ESP32-C3, OLED, microphone, and translator VCCA | startup, peak current, droop, return paths, decoupling, heat, and USB backfeed isolation |
| 5V_SYS and GND | Candidate regulated supply for `#3006`, translator VCCB, and the diode-fed controller path | whole-load startup/cutoff, transient regulation, current, heat, and every partial-power state |
| I2C | ESP32-C3 controller to OLED, SCL GPIO20 and SDA GPIO21 | exact controller, address, pull-ups, idle level, 400 kHz rise time, and display initialization |
| Duplex I2S | WS GPIO1, BCLK GPIO2, and amp data GPIO3 cross the candidate TXU0104 boundary to `#3006`; GPIO5 crosses channel 4 for reset-safe `SD_MODE`, while #2873 `PG` gates translator `OE`; `#6049` data returns directly on GPIO4 | 16 kHz WS, 64 clocks/frame and 1.024 MHz BCLK, slot alignment, PG/OE sequencing, translator edge quality, partial-power behavior, and simultaneous TX/RX |
| GPIO input | Normally-open action button from GPIO10 to GND | received switch pinout, defined released state, debounce, and application actions |
| BTL speaker pair | Adafruit `#3006` screw-terminal outputs to the CMS primary or separately capped CES comparison, one at a time | isolation from ground/frame, differential RMS power, low-volume function, distortion, heat, and repeatable enclosure acoustics |
| Native USB | GPIO18 D− and GPIO19 D+ on the ESP32-C3 module | flashing/logging access and a service condition that cannot back-power the external rail |

Supply rails and a speaker pair are electrical nets/interfaces, not data buses.
Every signal current also needs a return path through the insulated ground
network.

## What the corrected source declares

The current board adapter and configuration declare:

- 16 kHz microphone input and 16 kHz speaker output;
- shared I2S clocks on GPIO1/GPIO2 with 64 clocks per frame and an expected
  1.024 MHz BCLK, with separate GPIO3/GPIO4 data lines;
- an action/configuration button on GPIO10;
- a 128×64 OLED bus on GPIO20/GPIO21 at a requested 400 kHz;
- probes of the unshifted 7-bit addresses `0x3C` and `0x3D` followed by a
  headless fallback; and
- native USB Serial/JTAG for service.

Those are source facts. A successful build does not prove that a marketplace
module has the advertised controller, pin order, pull resistors, flash size, or
electrical behavior. Compare the flashed build identity with
[`firmware/source-build.json`](../firmware/source-build.json), then run the
hardware acceptance tests.

The source reconstruction also differs from the creator's published binary.
The corrected source and current `#6049` fixture expect microphone data on
GPIO4 and 16 kHz audio. The historical creator/video INMP441 harness expects
GPIO8 and 24 kHz. Do not mix those wiring contracts. DFRobot `DFR0954` is a
former amplifier primary and held alternative, not the current `#3006` fixture.

## Design intent retained from the video

The visual arrangement and hand-built frame can follow the video, but these
electrical requirements take priority:

- use a removable, guarded cell only after the power subsystem passes its
  release gates; never solder to a lithium cell or use the frame as a conductor;
- keep native USB, BOOT, reset, and the service disconnect accessible;
- wire the `#6049` ICS-43434 `DOUT` to GPIO4 for the corrected source build;
- use `#3006` at 16 kHz because its MAX98357A does not specify 24 kHz
  operation;
- keep microphone, antenna, display, and speaker openings unobstructed; and
- qualify the open CMS primary in a sealed fixture against the capped enclosed
  CES comparison before permanent
  mounting.

The frame dimensions shown in the video are layout clues, not verified CAD.
Freeze metalwork only after measuring the received parts, insulation, wire
bends, connector access, antenna keepout, and cell-removal path.

## Integration gate

Bring the system up one layer at a time: bare ESP32-C3, OLED, I2S clocks,
`#6049` ICS-43434 on GPIO4, `#3006` plus an 8 Ω dummy load, then the CMS primary
and separately capped CES comparison at low volume, Wi-Fi plus audio, and the
qualified power subsystem. Only after those stages pass should the battery and
finished frame be introduced. Record
measurements in
[the acceptance-test worksheet](06_ACCEPTANCE_TESTS.md).
