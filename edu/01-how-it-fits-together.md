# How the Pocket Assistant fits together

> **Evidence status:** the corrected firmware configuration has been built
> reproducibly, but its manifest still says `hardware_tested: false`. The
> diagram below is the intended integration contract, not evidence that the
> received modules, power path, wiring, radio, audio, or enclosure have passed
> physical qualification.

For the underlying circuit ideas, begin with the
[EE foundations course](fundamentals/README.md). This note applies those ideas
to the current prototype.

## System boundary

```text
 current-limited bench supply during qualification
              OR future qualified power subsystem
                              │
                intended 3.3 V/GND distribution
                              │
 OLED ◄── I2C GPIO20/21 ──► ESP32-C3 ◄── GPIO10 action button
                              │
          ┌── WS/BCLK GPIO1/2 ┴── WS/BCLK GPIO1/2 ──┐
          ▼                                          ▼
      INMP441 ── SD/GPIO4 ──► ESP32-C3 ── GPIO3/DIN ──► MAX98357A
                                                        │ OUT+ / OUT−
                                                        ▼
                                                 enclosed speaker

 USB-C reaches the ESP32-C3 only under the reviewed service-isolation
 condition; it is not a second source for the external 3.3 V distribution.
```

The frame is intended to be mechanical structure only. It must remain isolated
from raw power, 3.3 V, ground, every signal, and both speaker leads. That is an
acceptance test, not an assumption.

This overview deliberately does not freeze a converter, fuse, switch,
protection, charging, or USB-isolation circuit. Those choices belong in the
authoritative purchasing list, a reviewed power schematic, and recorded
power-chain tests. Until those tests pass, use a current-limited bench supply
and keep the lithium cell out of the assembly.

## Electrical interfaces

| Interface or net | Current project use | What still needs hardware proof |
| --- | --- | --- |
| 3.3 V and GND | Supply/reference for ESP32-C3 and peripherals | startup, peak current, droop, return paths, decoupling, heat, and USB backfeed isolation |
| I2C | ESP32-C3 controller to OLED, SCL GPIO20 and SDA GPIO21 | exact controller, address, pull-ups, idle level, 400 kHz rise time, and display initialization |
| Duplex I2S | Shared WS GPIO1 and BCLK GPIO2; amp data GPIO3; mic data GPIO4 | 16 kHz WS, 1.024 MHz BCLK, slot alignment, noise, and simultaneous TX/RX |
| GPIO input | Normally-open action button from GPIO10 to GND | received switch pinout, defined released state, debounce, and application actions |
| BTL speaker pair | MAX98357A `OUT+` and `OUT−` to the speaker only | isolation from ground/frame, low-volume function, distortion, heat, and enclosure acoustics |
| Native USB | GPIO18 D− and GPIO19 D+ on the ESP32-C3 module | flashing/logging access and a service condition that cannot back-power the external rail |

Supply rails and a speaker pair are electrical nets/interfaces, not data buses.
Every signal current also needs a return path through the insulated ground
network.

## What the corrected source declares

The current board adapter and configuration declare:

- 16 kHz microphone input and 16 kHz speaker output;
- shared I2S clocks on GPIO1/GPIO2, with separate GPIO3/GPIO4 data lines;
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
The corrected source expects microphone data on GPIO4 and 16 kHz audio; the
published binary expects GPIO8 and 24 kHz. Do not mix those wiring contracts.

## Design intent retained from the video

The visual arrangement and hand-built frame can follow the video, but these
electrical requirements take priority:

- use a removable, guarded cell only after the power subsystem passes its
  release gates; never solder to a lithium cell or use the frame as a conductor;
- keep native USB, BOOT, reset, and the service disconnect accessible;
- wire microphone data to GPIO4 for the corrected source build;
- use 16 kHz because MAX98357A does not specify 24 kHz operation;
- keep microphone, antenna, display, and speaker openings unobstructed; and
- qualify the selected enclosed speaker or sealed fallback before permanent
  mounting.

The frame dimensions shown in the video are layout clues, not verified CAD.
Freeze metalwork only after measuring the received parts, insulation, wire
bends, connector access, antenna keepout, and cell-removal path.

## Integration gate

Bring the system up one layer at a time: bare ESP32-C3, OLED, I2S clocks,
microphone, amplifier at low volume, Wi-Fi plus audio, then the qualified power
subsystem. Only after those stages pass should the battery and finished frame
be introduced. Record measurements in
[the acceptance-test worksheet](06_ACCEPTANCE_TESTS.md).
