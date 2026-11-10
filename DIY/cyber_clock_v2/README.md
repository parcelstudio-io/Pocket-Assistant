# Cyber Dawn

Cyber Dawn is an alarm-first reinterpretation of Huy Vector's [Smart Cyber Clock V2](https://www.huyvector.org/clocks/smart-cyber-clock-v2). It keeps a trace of the exposed-brass character (two brass cradles under a compact black body) and turns the idea into an offline-reliable bedside “signal terminal”: a monochrome OLED that fills most of an 82 × 52 mm face, a big snooze button and a knob on the lid, a local speaker, Wi-Fi/BLE setup, and one 16340 cell that rides through unplugs.

**Complete, 2026-11-10.** Closed out at the builder's word: "It was a good project." Assembled 2026-11-09 to Rev B, with the sunrise lamp left out. How to use it: [USER_MANUAL.md](docs/USER_MANUAL.md). The alarm program is `bench/circuitpython/cyberdawn.py`, with its logic in `dawn_core.py`. The spare parts went to the bins on 2026-11-10 ([parts by project](../PARTS_BY_PROJECT.md)).

**Rev B, 2026-10-31: solar removed, compact body, 16340 cell.** The body is in [COMPACT_DESIGN.md](docs/COMPACT_DESIGN.md); the screen decision in [SCREEN_RESEARCH.md](docs/SCREEN_RESEARCH.md).

This directory contains the researched design, a US-sourced bill of materials, power calculations, staged build plan, and an ESP-IDF firmware skeleton. Prices and availability were checked on **2026-09-23** and should be rechecked before ordering.

## Recommendation at a glance

| Decision | Recommendation |
|---|---|
| Controller | [Controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) for the alarm-first prototype; Wi-Fi + BLE, native USB, I2S |
| Display | The owned 2.42-inch 128×64 monochrome [OLED display](https://www.adafruit.com/product/2719) over 4-wire SPI; kept on 2026-10-31 after the [screen research](docs/SCREEN_RESEARCH.md) |
| Timekeeping | [Real-time clock](https://www.adafruit.com/product/5188) with its own [coin cell](https://www.amazon.com/dp/B0D8T4C5PK) and alarm interrupt |
| Audio | I2S [amplifier](https://www.adafruit.com/product/3006) + enclosed 4 Ω / 3 W [speaker](https://www.adafruit.com/product/1669); optional piezo fallback |
| Input | [Rotary encoder](https://www.adafruit.com/product/6310) knob and 16 mm [snooze button](https://www.adafruit.com/product/1505) on the lid, [arm switch](https://www.adafruit.com/product/805) on the left wall |
| Battery | One protected Nitecore 16340 cell (3.6 V, 950 mAh) in a [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F), through the [fuel gauge](https://www.adafruit.com/product/5580) into the [charger board](https://www.adafruit.com/product/6106)'s BAT port; charger jumper 500 mA |
| Power | USB-C into the charger board's own port through the rear panel; the cell is backup, not the main supply. Solar removed 2026-10-31 |
| Body | 82 × 52 × 68 mm printed black PETG on two brass U cradles, full-face smoked acrylic; see [COMPACT_DESIGN.md](docs/COMPACT_DESIGN.md) |
| Networking | BLE for setup/control; Wi-Fi for NTP, local UI, and OTA; alarms never depend on either |

The OLED choice is practical but needs burn-in mitigation: low contrast at night, pixel shifting, sparse layouts, and presence-based blanking. A wider 3.12-inch OLED is visually stronger but raises power and integration work enough that it belongs in a later custom-PCB version; the 2026-10-31 screen research kept the owned module and shrank the body around it instead.

The baseline controller has **BLE, not Bluetooth Classic/A2DP**. Its speaker plays alarms, local chimes, and soundscapes. If phone-to-clock music streaming is a requirement, use the documented “SoundDock” variant on the [Wi-Fi and Bluetooth Feather board](https://www.adafruit.com/product/5400) or a dedicated Bluetooth-audio module; that feature costs power and engineering time.

## Power

The clock is a USB-C appliance. The [charger board](https://www.adafruit.com/product/6106)'s own USB-C port reaches the rear panel through a cutout; its 5 V boost output feeds the controller's 5V pin and the amplifier.

One Nitecore 16340 cell (3.6 V, 950 mAh, protected, about 3.4 Wh) sits in its holder under the lid. Its job is to ride through unplugs and keep the alarm armed: many hours with the face dark and the controller asleep, roughly 10 h with the face lit. The charger jumper is set to 500 mA, about 0.5 C for this cell.

Solar was removed on 2026-10-31 by the builder's decision. Indoor light never paid for the clock ([the solar assessment](docs/SOLAR_FEASIBILITY.md) stays as the record), the screen research showed that any lit face outruns a window panel's daily yield ([SCREEN_RESEARCH.md](docs/SCREEN_RESEARCH.md)), and a plugged-in clock with a cell as backup is simpler. The 5 W [solar panel](https://www.adafruit.com/product/5367), the [DC jack adapter](https://www.adafruit.com/product/4287) and the [DC jack to screw terminals](https://www.adafruit.com/product/368) are owned and stay in [INVENTORY.md](docs/INVENTORY.md) as stock for another project; the charger board's solar input is left empty.

## Project map

- [Original-build research](docs/REFERENCE_BUILD.md)
- [Screen research](docs/SCREEN_RESEARCH.md): which bigger screen fits, 2026-10-31
- [Product and industrial-design brief](docs/PRODUCT_BRIEF.md), drawn to scale in [Cyber Dawn Form](https://claude.ai/artifact/Tepn1aKoRTaFkev9RoNFR7), Rev B (source [docs/pages/cyber-dawn-form.html](docs/pages/cyber-dawn-form.html))
- [Compact design, Rev B](docs/COMPACT_DESIGN.md): the 82 × 52 × 68 mm body and where every part lives, 2026-10-31
- [Hardware architecture and provisional pin plan](docs/ARCHITECTURE.md)
- [US purchase list and alternatives](docs/BOM.md)
- [Machine-readable BOM](bom/bom.csv)
- [Solar and battery feasibility](docs/SOLAR_FEASIBILITY.md), kept as the record behind dropping solar on 2026-10-31
- [Firmware architecture and alarm behavior](docs/SOFTWARE_PLAN.md)
- [Staged build plan and acceptance gates](docs/BUILD_PLAN.md)
- [Day 0: prove the parts on the stand-in controller before the controller board arrives, or on the controller board itself](docs/DAY0_TEST.md)
- [Hardware working notes](hardware/README.md)
- [Enclosure requirements](enclosure/README.md)
- [Firmware scaffold](firmware/README.md)

## Sensible first order

Buy only the USB-powered bench parts first: controller, OLED, real-time clock and coin cell, amp, speaker, controls, and prototype wiring. Prove that alarms survive Wi-Fi loss and resets before wiring the cell and charger board or printing the body. The complete build plan makes each later purchase contingent on a measurable test result.

## Firmware scaffold

The scaffold is intentionally small and uses ESP-IDF so reliability features such as watchdogs, NVS, provisioning, and dual-slot OTA can be added cleanly.

```bash
cd firmware
idf.py set-target esp32s3
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

ESP-IDF is not installed in this workspace, so the scaffold has been structurally checked but not compiled here.

## Safety boundaries

- Use one protected cell (the 16340) on one charger/power path. Never put two cells or two chargers on the same BAT port.
- Keep the cell in its holder under the lid, restrained and serviceable; meter the holder leads for polarity before the cell meets anything.
- The two brass cradles are a stand, not a power bus. Carry power and data on insulated wire; meter cradle-to-net isolation before power.
- Neither of the amplifier's speaker terminals is ground; its output is bridge-tied.
- Treat this as a prototype until brownout, thermal, charging, alarm, RF, and enclosure tests pass.

