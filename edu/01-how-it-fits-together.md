# Pocket Assistant project overview

For your first working bench setup, follow the
[USB prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md): controller, button,
OLED, then microphone diagnostics. That path uses the parts already owned and
one USB source. The power architecture discussed below is future portable
device work, not a requirement for these first experiments.

> **Scope and evidence:** this is the single applied overview for the course.
> It summarizes the intended system; it is not a released power schematic,
> bill of materials, or test result. The firmware manifest still records
> `hardware_tested: false`.

## Sources of truth

Use the narrowest authority for the question you are answering:

| Question | Authority |
| --- | --- |
| Concepts, safety, measurement, and debugging | [EE foundations course](fundamentals/README.md) |
| First USB prototype and owned-part wiring | [Prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md) |
| Logical pins, buses, rates, and build identity | [`config.h`](../firmware/src/boards/pocket-wall-e-c3/config.h), the [firmware README](../firmware/README.md), and [source-build manifest](../firmware/source-build.json) |
| Current hardware candidates, purchase status, and release gates | [Current material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md) |
| What happened on a physical article | A completed [lab record](fundamentals/reference/lab-record-template.md) |

This page is a navigation aid. If its summary ever differs from an authority
above, follow the authority and correct this page.

## Functional system view

```text
 current-limited bench source
             │
             ▼
 reviewed protection / switching / regulation
             │
           5V_SYS ───────────────► I2S amplifier
             │                           │
             │                     floating BTL + / -
             │                           ▼
             │                        speaker
             ▼
 reviewed controller power interface
             │
            3V3 ────────┬──────────┬───────────┐
                        ▼          ▼           ▼
                    ESP32-C3      OLED      microphone
                        │           ▲           │
                        ├── I2C ────┘           │
                        ├── I2S clocks ─────────┤
                        ├◄─ microphone data ────┘
                        └── speaker data ──► candidate gated boundary ──► amp

 conductive frame = mechanical structure only, isolated from every net
```

Every signal current needs a return path through the insulated ground network.
Neither bridge-amplifier speaker lead is ground. The frame must remain isolated
from raw power, regulated rails, ground, signals, and both speaker leads.

The diagram deliberately leaves protection, conversion, charging, switching,
and USB-isolation details abstract. Those details are not released until the
current material decision and a reviewed schematic say they are.

## Corrected-source logical contract

| Signal | ESP32-C3 pin | Destination or role |
| --- | ---: | --- |
| I2S word select | GPIO1 | microphone; amplifier through the candidate boundary |
| I2S bit clock | GPIO2 | microphone; amplifier through the candidate boundary |
| Speaker data | GPIO3 | amplifier through the candidate boundary |
| Microphone data | GPIO4 | ESP32-C3 input |
| Amplifier enable | GPIO5 | held low in default firmware; future powered hardware remains separate |
| Action button | GPIO10 | normally-open input to ground |
| OLED SCL | GPIO20 | I2C clock |
| OLED SDA | GPIO21 | I2C data |
| Native USB D− / D+ | GPIO18 / GPIO19 | flashing and service |

The source requests 16 kHz audio with 32-bit slots: 64 bit clocks per stereo
frame and an expected 1.024 MHz bit clock. It probes unshifted 7-bit OLED
addresses `0x3C` and `0x3D`.

These are source facts, not proof of a received module's controller, pin order,
pull resistors, flash size, or electrical behavior. In particular, the
corrected source uses microphone data on GPIO4 at 16 kHz; the historical
creator binary and harness used a different pin/rate contract. Do not combine
the two.

## Find the right lesson

| Engineering question | Read |
| --- | --- |
| What can hurt me, and what counts as evidence? | [Lesson 00](fundamentals/00-safety-evidence-and-course-map.md) |
| What do voltage, current, power, and energy mean? | Lessons [01](fundamentals/01-units-charge-voltage-current-power-energy-heat.md), [02](fundamentals/02-dc-circuits-ohm-kirchhoff-series-parallel.md), and [03](fundamentals/03-components-rc-diodes-mosfets-converters.md) |
| How do I read a board, datasheet, footprint, or connector? | [Lesson 04](fundamentals/04-boards-schematics-datasheets-and-connectors.md) |
| How should I measure and debug a rail or signal? | [Lesson 05](fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md) |
| Why can power look correct at idle and fail under load? | [Lesson 06](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md) |
| Which pins are risky at reset? | [Lesson 07](fundamentals/07-digital-logic-gpio-pullups-boot-straps.md) |
| How does the display bus work? | [Lesson 08](fundamentals/08-i2c-and-the-oled.md) |
| How does digital audio timing work? | [Lesson 09](fundamentals/09-i2s-sampling-and-digital-audio.md) |
| Why are both speaker outputs live? | [Lesson 10](fundamentals/10-class-d-btl-speakers-and-acoustics.md) |
| How do frame, antenna, soldering, and fit interact? | Lessons [11](fundamentals/11-rf-emc-antennas-and-metal-frame.md) and [12](fundamentals/12-soldering-mechanics-insulation-tolerance.md) |
| In what order should the system be integrated? | [Lesson 13](fundamentals/13-debugging-integration-and-capstone.md) |

## Release path

1. Confirm the build identity against the manifest.
2. Use the [quickstart](../docs/PROTOTYPE_QUICKSTART.md) for the first USB
   prototype. Consult the [material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md)
   for later amplifier, battery, and portable-power experiments.
3. Bring up one layer at a time, following
   [Lesson 13](fundamentals/13-debugging-integration-and-capstone.md).
4. Record predictions, setup, measurements, and failures in a lab record.
5. Apply the promotion gates in the current material decision before calling
   any hardware path released.

Keep the lithium cell out of early experiments. Use controller USB for the
quickstart or a current-limited supply for its specified bench labs. Never
solder to or deliberately short a cell, keep native USB and
recovery controls accessible, and do not cut the final metal frame until exact
parts and the relevant electrical, RF, acoustic, thermal, and service tests
have passed.
