# Hardware work area

This directory is reserved for schematics, PCB source, wiring drawings, measurement logs, and exported fabrication files. The architecture is documented in [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md); the order-and-test sequence is in [`docs/BUILD_PLAN.md`](../docs/BUILD_PLAN.md); the body and where every part sits is [`docs/COMPACT_DESIGN.md`](../docs/COMPACT_DESIGN.md).

Rev B 2026-10-31: solar removed, compact body, 16340 cell. The charger board charges from its own USB-C port; its solar input stays empty.

## Planned artifacts

```text
hardware/
  cyber_dawn.kicad_pro       custom carrier, after bench validation
  cyber_dawn.kicad_sch
  cyber_dawn.kicad_pcb
  prototypes/
    bench-wiring.md
    power-wiring.md
  measurements/
    usb-baseline.csv
    battery-runtime.csv
    unplugged-runtime.csv
    rail-scope/
  exports/                   ignored generated Gerber/BOM/PDF output
```

No schematic is fabricated yet because the OLED revision, exact controller-board module, real peak current, RF placement, and power topology still need bench evidence.

## Prototype net checklist

- `+5V_SYS`: the [charger board](https://www.adafruit.com/product/6106)'s boost output to the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894)'s 5 V pin and the amplifier supply
- `+3V3`: controller-board-regulated logic rail for OLED and sensors during prototype
- `I2C_SDA` / `I2C_SCL`: one 3.3 V-pulled bus
- `RTC_INT_N`: open-drain/active-low alarm line from the [real-time clock](https://www.adafruit.com/product/5188) with external pull-up
- `AMP_SD`: defaults low/off through reset
- `I2S_BCLK`, `I2S_WS`, `I2S_DOUT`: digital audio
- `SPK_P` / `SPK_N`: bridge-tied; neither is ground
- `VBUS`: the [charger board](https://www.adafruit.com/product/6106)'s own USB-C port through the rear panel; the board's solar/VIN input is left empty (Rev B, 2026-10-31)
- `VBAT`: one protected Nitecore 16340 cell in the [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F), through the [fuel gauge](https://www.adafruit.com/product/5580) into BAT, charger jumper 500 mA; never routed through the brass cradles

## Bench bring-up order

1. Inspect for shorts with all modules unpowered.
2. Power the ESP32 over current-limited USB without the cell.
3. Add the real-time clock and verify time/alarm interrupt.
4. Add amp with shutdown held off, then speaker and bulk capacitance.
5. Add OLED and controls.
6. Add optional I2C sensors one at a time and test bus recovery.
7. Characterize peak current before connecting the power-path board.
8. Meter the holder leads for polarity, then bring up the 16340 cell on the charger board's BAT port (500 mA jumper) in a fire-conscious workspace.
9. Unplug and replug USB-C while running and while ringing; log the fuel gauge.

## Rules for schematic capture

- No 5 V pull-ups on S3 GPIO.
- Audit pull-ups on every STEMMA QT board and leave an appropriate effective value per I2C segment; do not blindly parallel every onboard pull-up.
- Test points on 5 V, 3.3 V, battery, real-time clock interrupt, amp shutdown, and all buses.
- Explicit source isolation between USB and external 5 V.
- NTC/temperature input and battery connector polarity called out visibly.
- Load switches for OLED, optional air sensor, and amplifier on the custom board.
- Keep antenna keep-out free of copper, battery, speaker, display flex, and brass.
- Place the climate sensor at an enclosure vent, away from MCU/OLED/PMIC heat.

## Safety note

The open-wire visual language is not permission to expose battery conductors. The two brass cradles are the only metal left on the outside and they stay electrically floating: meter cradle-to-net isolation before power. Use insulated wiring, strain relief, a protected cell, and the holder under the lid as its serviceable compartment.
