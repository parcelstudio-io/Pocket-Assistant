# Pocket Assistant project map

This page connects the durable concepts in the course to the repository's
current prototype. It is a navigation aid, not a released wiring drawing or
purchase approval.

> **Current signal fixture:** Adafruit `#6049` ICS-43434 Phase 0 microphone on
> GPIO4 and a MAX98357A amplifier on GPIO3, with 16 kHz audio and shared
> GPIO1/GPIO2 clocks. INMP441 is a held alternative with analogous signal
> names but a carrier pin order that must be checked independently.
> Purchase authority belongs only to
> [FINAL_MATERIALS_FOR_REVIEW.md](../../../docs/FINAL_MATERIALS_FOR_REVIEW.md);
> this map does not authorize final quantities or assembly.

## Evidence status

As of the repository's current state:

- the corrected firmware source has a defined signal contract and reproducible
  host-side build/test evidence;
- static net checks and CAD checks cover only their encoded assumptions;
- exact marketplace board revisions, module pin order, power behavior, RF,
  audio, mechanics, and the assembled cell path still require physical tests;
- the firmware manifest records `hardware_tested: false`; and
- the component/fabrication design is not frozen merely because files call it
  “Rev A,” “verified,” or “GO.”

Use the five evidence labels from [Lesson 00](../00-safety-evidence-and-course-map.md).

## Functional block view

```text
protected cell or current-limited bench substitute
                     │
                     ▼
       input protection / switching / #2873
                     │ 5V_SYS
          ┌──────────┴──────────────┐
          ▼                         ▼
     I2S amplifier       diode → controller LDO → 3V3
          ▲                               ┌─────┼────────┐
          │                               ▼     ▼        ▼
 PG-gated partial-power translator    ESP32   OLED   I2S mic
          ▲                               │
          └──────── I2S / shutdown ───────┘ Wi-Fi / controls
          │
          ▼
       speaker

conductive frame: mechanically separate, insulated, not a power return
```

Every arrow needs a return-current path even when the drawing omits it for
clarity. The regulated rails, protection strategy, supply and signal isolation,
connectors, and exact module implementations remain design/qualification work.

## Current corrected-source signal contract

The following is a **SOURCE-CODE CONTRACT**, not proof of received-board
compatibility. Its source of truth is
`firmware/src/boards/pocket-wall-e-c3/config.h`.

| Function | ESP32-C3 GPIO | Intended endpoint | Course topic |
| --- | ---: | --- | --- |
| I2S word select | 1 | #6049 ICS-43434 `WS/LRCLK` (alt: INMP441 `WS`), MAX98357A `LRC` | [I2S](../09-i2s-sampling-and-digital-audio.md) |
| I2S bit clock | 2 | #6049 ICS-43434 `BCLK` (alt: INMP441 `SCK`), MAX98357A `BCLK` | [I2S](../09-i2s-sampling-and-digital-audio.md) |
| I2S speaker data | 3 | ESP output → MAX98357A `DIN` | [I2S](../09-i2s-sampling-and-digital-audio.md) |
| I2S microphone data | 4 | #6049 ICS-43434 `DOUT` (alt: INMP441 `SD`) → ESP input | [I2S](../09-i2s-sampling-and-digital-audio.md) |
| Candidate amplifier enable | 5 | TXU0104 A4 → B4 → MAX98357A `SD_MODE`; #2873 `PG` independently gates translator `OE` | [GPIO](../07-digital-logic-gpio-pullups-boot-straps.md) and [audio](../10-class-d-btl-speakers-and-acoustics.md) |
| Action/config input | 10 | external active-low control | [GPIO](../07-digital-logic-gpio-pullups-boot-straps.md) |
| OLED clock | 20 | SSD1306 `SCL` | [I2C](../08-i2c-and-the-oled.md) |
| OLED data | 21 | SSD1306 `SDA` | [I2C](../08-i2c-and-the-oled.md) |

The corrected source uses 16 kHz full-duplex audio, two 32-bit I2S slots, and
probes OLED addresses `0x3C` then `0x3D`. The 64 clocks per frame imply a
1.024 MHz bit clock.

The separately published vendor binary uses a different, **historical**
INMP441-style contract: microphone data on GPIO8, 24 kHz audio, and `0x3C`.
Do not mix vendor-binary wiring with corrected-source wiring. GPIO8 is also
involved in ESP32-C3 boot strapping and may be loaded by an LED on some
SuperMini variants. GPIO9 remains the ROM BOOT strap in the corrected-source
plan. Exact board circuitry must be inspected. DFRobot `DFR0954` is a former
amplifier primary and held alternative, not the active `#3006` endpoint.

## Interfaces at a glance

| Interface | Electrical behavior | What to verify on hardware |
| --- | --- | --- |
| 5V_SYS / 3V3 rails | Candidate #2873 whole-load rail and the controller board's downstream LDO rail | range at load, startup/cutoff, ripple/dips, current, heat, and rail-to-rail backfeed |
| I2C | shared open-drain SDA/SCL with pull-ups | actual pull-ups/levels, addresses, ACK, rise time, pin order |
| I2S | `#6049`/`#3006` point-to-point/shared-clock push-pull stream; amp-side translator `OE` is gated by #2873 `PG` | direction, levels, 16 kHz WS, 1.024 MHz BCLK, slot format, PG/OE/SD sequencing, edge quality |
| Action input | active-low GPIO according to source | external pull/default, reset-time effect, debounce, access |
| USB/service power | depends on exact board implementation | isolation, reverse current/backfeed, regulator path, connector access |
| Speaker output | Adafruit `#3006` bridge-tied screw-terminal pair | neither lead grounded; load, current, heat, acoustic mounting |
| Wi-Fi | onboard 2.4 GHz antenna | exact antenna end, keepout, frame/cell A/B performance |

## Power questions still requiring a reconciled design

Use [Lesson 06](../06-li-ion-power-integrity-decoupling-uvlo-thermal.md) before
approving a power path. At minimum, resolve and verify:

1. Can the exact converter module **cold-start** at the intended minimum input
   with the real load and all path drops?
2. Does it maintain 5V_SYS and the downstream 3V3 rail through credible Wi-Fi/audio transients?
3. What provides a normal low-battery shutdown with hysteresis, rather than
   relying on a cell protection fault cutoff?
4. What does each protection component do across current, time, and temperature?
5. Can service USB create backfeed into the peripheral rail, converter, or cell?
6. What are the measured voltage drops and temperatures of exact samples?

An IC datasheet does not automatically specify an unidentified module built
around that IC. A cell's published capacity and continuous current rating do
not establish internal resistance or protection thresholds the maker did not
publish.

## Exact-module incoming inspection

Before wiring any marketplace board:

- photograph both faces at readable resolution;
- transcribe top markings and seller/order link with purchase date;
- measure length, width, maximum height, hole/connector locations, and weight;
- determine connector family, pitch, orientation, and pin order;
- identify ground and rail continuity while unpowered;
- identify onboard pull-ups, LEDs, regulators, dividers, and configuration
  jumpers from inspection and measurement where possible;
- compare every pin label with a manufacturer or board schematic; and
- assign the unit an identifier used in test records.

For JST terminology, genuine PH is a 2.0 mm-pitch family. A listing that says
“JST-PH 2.5 mm” is internally inconsistent and must not define a purchase.

## Repository navigation by engineering question

| Question | Start here | Then inspect |
| --- | --- | --- |
| What physics quantity am I calculating? | [Lessons 01–03](../README.md) | [equation sheet](equations.md) |
| How do I measure it safely? | [Lesson 05](../05-measurement-dmm-supply-scope-logic-analyzer.md) | project acceptance record |
| How does the cell/converter path behave? | [Lesson 06](../06-li-ion-power-integrity-decoupling-uvlo-thermal.md) | current schematic/BOM and exact datasheets |
| Why does a boot pin matter? | [Lesson 07](../07-digital-logic-gpio-pullups-boot-straps.md) | `config.h`, ESP32-C3 datasheet/guidelines |
| Why does an OLED need pull-ups and an address? | [Lesson 08](../08-i2c-and-the-oled.md) | received OLED schematic and bus capture |
| Why are there four audio signal wires? | [Lesson 09](../09-i2s-sampling-and-digital-audio.md) | source plus mic/amplifier datasheets |
| Why can neither speaker lead be grounded? | [Lesson 10](../10-class-d-btl-speakers-and-acoustics.md) | exact amplifier module schematic |
| What can the metal case do to Wi-Fi? | [Lesson 11](../11-rf-emc-antennas-and-metal-frame.md) | exact-unit RF A/B records |
| Why is collision-free CAD insufficient? | [Lesson 12](../12-soldering-mechanics-insulation-tolerance.md) | exact-part measured fit and assembly trial |
| How do I bring it up without guessing? | [Lesson 13](../13-debugging-integration-and-capstone.md) | dated test plan and evidence files |

## Battery-last release rule

Keep the cell outside the device during soldering, metalwork, debugging, and
initial integration. Use a current-limited bench substitute until the complete
electrical design, normal undervoltage behavior, service-power isolation,
thermal behavior, insulation, strain relief, exact-part fit, and RF/acoustic
arrangement have passed documented review and test.
