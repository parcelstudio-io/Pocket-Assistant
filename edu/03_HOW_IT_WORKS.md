# 3 — How the chosen parts work together

Read [How it all fits together](01-how-it-fits-together.md) for the deeper bus/audio explanation. This page is the assembly wiring contract.

## Rev A power tree

```text
removable protected Nitecore NL169 16340
               │
             holder
               │
              PTC
               │
     Pololu #2810 MOSFET switch
               │
       Pololu S8V9F3 regulator
               │ 3.3 V
       ┌───────┼────────┬──────────┐
     ESP32    OLED    INMP441   MAX98357A ── floating 8 Ω speaker

Every GND is insulated wire. The silver/brass frame is connected to nothing.
The cell leaves the device for charging. During Phase 0 the SuperMini is
disconnected from the external rail/peripheral harness before USB is connected.
```

**Unresolved service gate:** cell removal disconnects regulator input but does
not isolate its output from a USB-powered SuperMini 3.3 V pin. The final
carrier must provide a reviewed removable-module/service connector, power mux,
or equivalent isolation so USB cannot back-power the peripherals or S8V9F3.
Do not treat “cell out” alone as permission to attach USB to the full harness.

## Firmware signal contract

| ESP32-C3 | Module pin(s) | Meaning |
| --- | --- | --- |
| GPIO21 | OLED `SDA` | I2C data |
| GPIO20 | OLED `SCL` | I2C clock |
| GPIO1 | INMP441 `WS`; MAX98357A `LRC` | Shared 16 kHz I2S word clock |
| GPIO2 | INMP441 `SCK`; MAX98357A `BCLK` | Shared I2S bit clock; preserve required boot strap state |
| GPIO4 | INMP441 `SD` | Microphone data into corrected source firmware |
| GPIO3 | MAX98357A `DIN` | Audio data out |
| GPIO10 | normally-open action button to GND | Active-low application control |
| 3.3 V | every module supply | Regulated rail from S8V9F3 |
| GND | every module GND; INMP441 `L/R` | Common insulated return and left-slot choice |

The pinned creator/vendor binary still expects microphone data on GPIO8 and OLED `0x3c`. The corrected editable/source-built artifact expects GPIO4 and probes OLED `0x3c` then `0x3d`. Wire to the firmware you will actually flash; this Rev A BOM targets the corrected source build.

## Critical details

- The MAX98357A is bridge-tied. Speaker `+` and `-` go only to the speaker; neither is GND.
- Configure the DFR0954 for the I2S channel used by the firmware, then verify with a tone before installation.
- Keep I2S wires short; twist the speaker pair; place decoupling at the load, not at the far end of the harness.
- Point the ESP32 antenna toward an open nonmetallic edge. Keep cell, frame, wiring bundles, and metallic paint out of its keepout.
- Leave the INMP441 port open and clean. Do not apply flux, IPA, compressed air, glue, or paint to it.
- The selected speaker needs a small enclosure. Validate sound with the intended ~1 cc rear cup before permanent mounting.

## Mechanical stack

```text
front:  white OLED pixels + white bezel
middle: insulated ESP32/mic sub-plate; antenna and mic toward open edges
rear:   removable 16340 holder behind white fish-paper/polycarbonate guard
edge:   black power switch and accessible cell door
lower:  black speaker cloth + ~1 cc cup; amp nearby
```

The video's visible 40 mm and 15 mm marks are layout clues, not a complete dimensioned case. Freeze the frame only after measuring the actual holder, protected cell, plug clearance, speaker cup, insulation, fasteners, and wire bends.
