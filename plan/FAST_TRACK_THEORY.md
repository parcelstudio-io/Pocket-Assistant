# Fast-track theory companion — why each build step works

[Back to the action-only fast track](FAST_TRACK.md) ·
[Parts outline](FAST_TRACK_PARTS.md) ·
[All illustrated concept notes](concepts/README.md) ·
[Full electronics course](../edu/README.md)

This page is optional while you build. The action guide contains every safety
rule, command, wire, and pass condition you need. Open only the section for the
step you are doing when you want to understand the engineering underneath it.

## Step 0 — why the boundary is so small

A circuit works only when current has a complete path from a source and back.
Using USB as the only source gives the prototype one known supply and one known
return. Adding a charger, battery, regulator, or amplifier would create new
power paths—including paths that can feed an unpowered board backwards—before
the simple digital parts have been tested.

- Short explanation: [charge, energy, and complete circuits](concepts/01-charge-energy-and-circuits.md)
- Short explanation: [voltage, current, resistance, and power](concepts/02-voltage-current-resistance-and-power.md)
- Deeper reference: [safety, evidence, and the course map](../edu/fundamentals/00-safety-evidence-and-course-map.md)

## Steps 1 through 4 — from source code to a running board

The build converts source files into a binary image. Verification checks that
the image matches the recorded inputs; it cannot prove that a physical board
works. `flash-id` is the first hardware observation. Flashing then replaces the
board's stored bootloader, partitions, application, and assets. The serial log
is the first evidence that those bytes actually boot on board `A1`.

- Short explanation: [from code to boot](concepts/06-from-code-to-boot.md)
- Deeper reference: [boards, schematics, datasheets, and connectors](../edu/fundamentals/04-boards-schematics-datasheets-and-connectors.md)
- Exact project workflow: [firmware guide](../firmware/README.md)

## Step 5 — soldering and connections

Solder is not glue. The pad and pin must both become hot enough for molten
solder to wet them. The metal joint carries current; a header and later strain
relief carry mechanical force. Visual inspection can find bridges and damage,
while the unpowered continuity tests separately ask whether the intended path
conducts and neighboring paths remain isolated.

A continuity beeper is a small current source watching for a low resistance.
Every module carries decoupling capacitors across its supply and ground, and an
empty capacitor briefly accepts that current as though it were a short, then
stops as it charges. That is why the action guide treats a **brief chirp**
between a supply and ground as normal and a **persistent tone or near-zero
resistance** as a stop condition: the first is a capacitor filling, the second
is a real fault. This distinction appears in Steps 5C–5E, 6, 7, 8, and 9, so it
is worth reading once.

- Short explanation: [soldering and heat](concepts/11-soldering-and-heat.md)
- Short explanation: [joints and strain relief](concepts/12-joints-and-strain-relief.md)
- Short explanation: [measurement and uncertainty](concepts/05-measurement-and-uncertainty.md)
- Short explanation: [capacitors and time](concepts/04-capacitors-and-time.md) — why a chirp is not a short
- Deeper reference: [soldering, mechanics, insulation, and tolerance](../edu/fundamentals/12-soldering-mechanics-insulation-tolerance.md)

## Step 6 — button and digital input

A solderless breadboard hides spring clips under its holes. On this build, an
ordinary group of five holes is one electrical node, while the center trench
separates the two sides. Side power rails run lengthwise but may be broken at
the midpoint. Printed red and blue stripes are only labels; the continuity
test establishes which holes are really connected. Creating one verified
`3V3` rail and one verified `GND` rail provides clean fan-out for the later
OLED and microphone instead of trying to crowd several leads onto one pin.

A digital input is still a voltage measurement. The firmware's pull-up makes
GPIO10 read high while the external button is open. Pressing the button connects
GPIO10 to ground, so it reads low. GPIO9 is different: the ESP32-C3 samples it
during reset to select boot behavior, which is why it stays reserved for
recovery.

- Short explanation: [series, parallel, and hidden breadboard nodes](concepts/03-series-parallel-and-loading.md)
- Short explanation: [GPIO and buttons](concepts/07-gpio-and-buttons.md)
- Deeper reference: [DC circuits and breadboard topology](../edu/fundamentals/02-dc-circuits-ohm-kirchhoff-series-parallel.md#know-the-solderless-breadboard-before-using-it)
- Deeper reference: [digital logic, GPIO, pulls, and boot straps](../edu/fundamentals/07-digital-logic-gpio-pullups-boot-straps.md)

## Step 7 — I2C and the OLED

I2C lets the controller address a device over two shared signals: `SCL` carries
the clock and `SDA` carries data. An acknowledgement at `0x3C` or `0x3D` proves
that a device at that address answered; the all-on/all-off pixel test
separately proves that the panel initialized and responds. Power polarity is
not part of I2C, which is why the actual `VCC` and `GND` labels must be checked
first.

- Short explanation: [I2C and the OLED](concepts/08-i2c-and-the-oled.md)
- Deeper reference: [I2C and the OLED lesson](../edu/fundamentals/08-i2c-and-the-oled.md)

## Step 8 — I2S microphone and RMS

The microphone samples sound and sends numbers, not an analog audio voltage.
At 16,000 frames per second, `WS` marks each frame, `SCK` shifts each bit, and
`SD` carries the microphone data into GPIO4. Grounding `L/R` chooses the left
slot used by this firmware. RMS summarizes the size of many samples, so a
repeatable quiet-versus-speech difference matters more than one magic number.
The two 32-bit slots in every 16,000 Hz frame require a bit clock of
`16,000 × 2 × 32 = 1.024 MHz`.

The `L/R` mapping rests on two facts that must agree. The mic side is
datasheet-defined: the INMP441 drives the left slot when `L/R` is low. The
controller side — which slot the firmware reads — is configured in upstream
`NoAudioCodecDuplex` (xiaozhi v2.4.0), which is fetched at build time and is
not in this repository. Step 8 is therefore the verification, not a formality:
a slot mismatch produces the specific signature of nonzero `samples` with
`min` and `max` both stuck at zero and `read_errors=0`, and the firmware
itself names "slot" as a suspect in that case.

GPIO2 is also an ESP32-C3 startup strap. The 10 kΩ pull-up gives it a defined
startup level before firmware takes control. The 100 kΩ pull-down prevents the
microphone-data input from floating while it is not actively driven.

- Short explanation: [sampling and I2S](concepts/09-sampling-and-i2s.md)
- Short explanation: [measurement and uncertainty](concepts/05-measurement-and-uncertainty.md)
- Deeper reference: [I2S, sampling, and digital audio](../edu/fundamentals/09-i2s-sampling-and-digital-audio.md)

## Step 9 — integration and repeatability

A device working once can be a lucky contact or an unrecorded setup. Two cold
starts exercise boot order and physical connections again. Adding one layer at
a time localizes a failure: if the button worked before the OLED was added, a
new failure should first be investigated at the OLED layer rather than by
randomly changing firmware.

- Short explanation: [debugging as experiments](concepts/15-debugging-as-experiments.md)
- Deeper reference: [systematic debugging and the capstone](../edu/fundamentals/13-debugging-integration-and-capstone.md)
- Optional record: [lab record template](../edu/fundamentals/reference/lab-record-template.md)

## Step 10 — network and cloud boundary

Assistant mode adds Wi-Fi provisioning and a remote service. That changes both
the failure surface and the privacy boundary: a local microphone problem, a
Wi-Fi problem, account activation, or a remote outage can now look similar.
Returning to offline diagnostics removes the network variables. The default
third-party service receives device metadata and microphone audio, so using it
is a deliberate product/privacy decision rather than an automatic build step.
The pinned provisioning component also uses an open temporary access point and
an unencrypted HTTP form, then stores the selected network credentials in
unencrypted flash settings. A full diagnostic reflash clears those settings;
a reset does not. That is why the action guide calls for a private location and
a unique guest/IoT network.

- Project reference: [assistant-mode firmware notes](../firmware/README.md#flash-and-monitor-source-builds)
- System overview: [how the parts fit together](../edu/01-how-it-fits-together.md)

## Theory for the later projects

Do not turn these readings into permission to connect held hardware. They
explain the questions that later qualification must answer.

| Later project | Short explanation | Deeper reference |
| --- | --- | --- |
| Amplifier and speaker | [Speakers and amplifiers](concepts/10-speakers-and-amplifiers.md) | [Class-D, BTL, speakers, and acoustics](../edu/fundamentals/10-class-d-btl-speakers-and-acoustics.md) |
| Portable power | [Power integrity](concepts/13-power-integrity.md) | [Li-ion, decoupling, UVLO, and thermal behavior](../edu/fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md) |
| Enclosure and radio | [Fit and radio](concepts/14-fit-and-radio.md) | [RF, EMC, antennas, and the metal frame](../edu/fundamentals/11-rf-emc-antennas-and-metal-frame.md) |

The release authority for all three remains the
[current Phase 0 promotion gates](../docs/FINAL_MATERIALS_FOR_REVIEW.md#promotion-gates-before-claude-may-say-final-go).
