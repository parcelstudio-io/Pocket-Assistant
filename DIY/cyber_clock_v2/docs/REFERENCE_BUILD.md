# Reference build research

Reviewed on **2026-09-23**.

## Sources reviewed

- Huy Vector, [Smart Cyber Clock V2 project page](https://www.huyvector.org/clocks/smart-cyber-clock-v2)
- Huy Vector, [build video](https://www.youtube.com/watch?v=0l7naYHrVkA)
- The author's [source archive](https://drive.google.com/file/d/13PCg8M7WbFG8tG8a9VvOtz09qilxXAXB/view?usp=sharing), linked from the project page
- Waveshare, [ESP32-C6-LCD-1.3 documentation](https://docs.waveshare.com/ESP32-C6-LCD-1.3)
- A useful secondary overview, [“Flip for Focus: The Cyber Smart Clock V2”](https://www.hackster.io/news/flip-for-focus-the-cyber-smart-clock-v2-60fc83b10443)

The project page, downloadable sketch, and wiring image were treated as the authoritative technical record. This document summarizes behavior and interfaces; it does not copy the author's code.

## What the original clock is

The reference is a sculptural, battery-powered ESP32-C6 desk clock assembled on exposed copper wire and brass tube. A 240×240 color LCD shows time and environmental information. An IMU turns the physical object itself into the mode selector: tipping it starts a focus or break timer, while returning it upright restores the clock dashboard.

Its appeal comes from three ideas worth preserving:

1. The electronics are visually legible instead of hidden in a generic plastic box.
2. Orientation is part of the interaction model.
3. The screen combines time with ambient room information.

## Original material and module list

| Original item | Purpose | Cyber Dawn disposition |
|---|---|---|
| Waveshare ESP32-C6 1.3-inch LCD board | MCU, Wi-Fi/BLE, 240×240 ST7789 display, status LED | Replace with the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) plus a separate [OLED display](https://www.adafruit.com/product/2719) |
| 0.8 mm bare copper wire | Free-wire structure and visual language | Retain as decoration/low-stress structure only; use insulated conductors electrically |
| 2 mm and 3 mm brass tube | Frame and stand | Retain as the stand only: two 3 mm U cradles from the owned [brass tube set](https://www.amazon.com/dp/B0F2FKLC2N) under a printed body (Rev B, 2026-10-31) |
| 14250 cylindrical 3.7 V cell | Portable power; linked listing claims 1200 mAh | Keep the idea: Rev B (2026-10-31) runs on one protected Nitecore 16340 cell in a [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F), with a [fuel gauge](https://www.adafruit.com/product/5580) on its lead |
| USB-C 4.2 V charging module | Battery charging | Replace with the [charger board](https://www.adafruit.com/product/6106): a power-path charger with its own USB-C port and a 5 V boost output, jumper at 500 mA; its solar input is unused since 2026-10-31 |
| ENS160 + AHT2x board | eCO2/TVOC estimate, temperature, humidity | Make optional; temperature/humidity can remain in the base build |
| BMI160 IMU | Tilt/orientation gestures | Replace or retain; configure it at `0x69` to avoid the real-time clock's address |
| Passive buzzer | Timer and air-quality alerts | Upgrade to I2S amp/speaker; optional piezo remains as a fallback |
| Slide switch | Hard power control | Change user-facing switch to alarm arm/disarm; deep sleep replaces hard-off |

## Observed reference behavior

- Connects to hard-coded Wi-Fi credentials at boot.
- Calls network time with a hard-coded UTC offset.
- Displays time, temperature, humidity, eCO2, and TVOC.
- Starts an approximately 30-minute focus timer when tilted one way.
- Starts an approximately 5-minute break timer when tilted the other way.
- Returns to the dashboard when upright.
- Beeps at timer completion and for poor air-quality thresholds.
- Uses the onboard addressable LED for status.

The sketch samples the environmental sensors every five seconds. Its eCO2 status changes below 800, at 800–1199, 1200–1799, and 1800+ ppm-equivalent; the highest band also chirps the buzzer. These values come from the ENS160's gas-derived estimate, not a direct CO2 measurement.

The Arduino sketch uses Arduino_GFX, Adafruit AHTX0/BusIO/Unified Sensor, ScioSense ENS160, DFRobot BMI160, and Adafruit NeoPixel libraries.

There is a mechanical-source conflict worth resolving with a mockup: the web page lists 2 mm and 3 mm brass tube, while the video overlay around 0:38 calls out 1.5 mm brass stock. No dimensioned drawing is supplied, so the redesign uses readily available 3/32- and 1/8-inch US tube for fit trials before committing to final stock.

Useful build-video landmarks are approximately 0:34 for the controller/display, 0:38 for frame stock, 1:12 for the IMU, 2:00 for the air sensor, 2:40 for the cell, 3:16 for the charger, 3:38 for the buzzer, and 3:54 for completed hardware.

The source ZIP contains no explicit software license. Treat it as a behavior reference; do not copy or redistribute it into this repository without permission or a clarified license.

## Reference interfaces and pins

These are useful when reproducing or comparing the original, not the new board's pin assignment.

| Interface | Reference assignment |
|---|---|
| I2C SDA / SCL | ESP32-C6 GPIO 2 / GPIO 1 |
| BMI160 address | `0x69` |
| LCD | ST7789, 240×240 |
| LCD MOSI / SCLK | GPIO 6 / GPIO 7 |
| LCD CS / DC / RESET / backlight | GPIO 14 / 15 / 21 / 22 |
| Passive buzzer | GPIO 12 |
| Onboard NeoPixel | GPIO 8 |

## Gaps to fix in the redesign

| Reference limitation | Cyber Dawn response |
|---|---|
| No actual recurring alarm scheduler | Add a tested alarm engine and a hardware interrupt from the real-time clock |
| Network and fixed-offset time are trusted | Store UTC, use a real timezone/DST policy, and work offline |
| Hard-coded Wi-Fi credentials | BLE/captive-portal provisioning; never commit credentials |
| Buzzer-only sound | Local I2S audio plus procedural fallback tone |
| No independent time backup | [Real-time clock](https://www.adafruit.com/product/5188) with [coin cell](https://www.amazon.com/dp/B0D8T4C5PK) |
| Generic charger and no fuel telemetry | Managed power path, protected pack, [fuel gauge](https://www.adafruit.com/product/5580) |
| Exposed power wiring | Isolated brass frame, insulated conductors, protected battery bay |
| LCD backlight load | OLED with contrast, blanking, and pixel-shift policy |
| Blocking boot/network behavior | Alarm and clock services start before connectivity |

## Design inheritance, not a clone

Cyber Dawn keeps the “electronic artifact” quality and optional tilt-to-focus interaction, while changing the main purpose to dependable bedside alarms. The screen-sized printed body on two brass cradles, the down-firing speaker and the big snooze button on the lid intentionally create a new silhouette rather than a screen-for-screen copy (Rev B, 2026-10-31; the earlier battery pod, snooze rail and solar sail are withdrawn).
