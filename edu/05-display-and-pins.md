# Display application and ESP32-C3 pin reservations

> **Evidence status:** the corrected source contains the pin map, two-address
> probe, and headless fallback described here. The selected marketplace display
> and ESP32-C3 boards have not yet passed recorded hardware qualification.

Read [I2C and the OLED](fundamentals/08-i2c-and-the-oled.md) and
[Digital logic, GPIO, pull resistors, and boot straps](fundamentals/07-digital-logic-gpio-pullups-boot-straps.md)
for the protocol and electrical foundations.

## Display contract

| Function | ESP32-C3 pin | Corrected-source setting |
| --- | ---: | --- |
| SCL | GPIO20 | I2C controller clock, requested 400 kHz |
| SDA | GPIO21 | Bidirectional open-drain data |
| Address candidates | — | Unshifted 7-bit `0x3C`, then `0x3D` |
| Geometry | — | 128×64, one bit per pixel |

The firmware probes both candidate addresses. If neither responds, or later
panel initialization fails, it logs the error and continues with a headless
display object. This prevents one display fault from intentionally aborting the
rest of the application.

An ACK means that a target responded at an address. It does not identify the
controller as SSD1306, prove 128×64 geometry, or validate the initialization
sequence. Address depends on the exact controller and board configuration—not
on a universal “generic versus Adafruit” rule. Inspect and scan the received
display.

## Pull-ups and 400 kHz

SDA and SCL need external pull-ups because I2C participants pull LOW and release
HIGH. The source enables the ESP32-C3 internal pull-ups, but Espressif describes
those weak pulls as unsuitable by themselves for a robust high-speed bus.

Before accepting the requested 400 kHz setting:

1. inventory pull-ups and level shifters fitted to every received module;
2. calculate the parallel pull-up resistance rather than adding resistors
   blindly;
3. verify both idle lines sit near 3.3 V;
4. scan at 100 kHz as a diagnostic, then test the project at 400 kHz; and
5. measure rise time with a suitable oscilloscope.

Working at 100 kHz but failing at 400 kHz points toward capacitance, pull-up,
level-shifter, wiring, or edge-timing problems. A logic-analyzer decode proves
transactions were recognized at its threshold; it does not measure analog
rise-time margin.

## Boot straps and native USB

ESP32-C3 samples GPIO2, GPIO8, and GPIO9 at reset, then permits normal GPIO use.
The manufacturer's recommended states are:

| Boot intention | GPIO2 | GPIO8 | GPIO9 |
| --- | --- | --- | --- |
| Normal SPI-flash boot | HIGH recommended | Either | HIGH |
| Joint USB/UART download | HIGH recommended | HIGH | LOW |

GPIO2 does not itself select SPI versus Joint Download Boot, but Espressif
recommends pulling it high because of glitches. GPIO8 is required high when
GPIO9 is low for Joint Download Boot; it is not required high for every normal
boot.

The corrected source moves microphone data from GPIO8 to GPIO4 so an audio
output cannot interfere with GPIO8's strap state. GPIO8 remains unallocated by
the application and may also drive an LED on the selected SuperMini family;
verify that on every received board. GPIO9 remains the BOOT control.

GPIO18/GPIO19 are reserved for native USB D−/D+ in this design. The chip can
repurpose them, but doing so can remove USB flashing, logging, and JTAG.
Recovery may still be possible through Joint Download Boot or UART after a
conflicting external circuit is disconnected; losing accessible USB is a major
serviceability failure, not literally irreversible silicon damage.

GPIO20/GPIO21 have UART0 functions at reset but are routed to I2C by the GPIO
matrix in the application. Verify reset/early-boot behavior with the exact
module and attached OLED.

## Current project reservations

This is a design allocation, not a universal ESP32-C3 capability table:

| GPIO | Current allocation or caution |
| ---: | --- |
| 0 | Unallocated; no implemented battery monitor |
| 1 | Shared I2S WS |
| 2 | Shared I2S BCLK; strap bias required |
| 3 | I2S data to amplifier |
| 4 | I2S data from microphone |
| 5–7 | Unallocated by current firmware; board exposure and startup behavior still require review |
| 8 | Application-unallocated strap; possible on-board LED; preserve download-mode state |
| 9 | Module BOOT strap/control |
| 10 | Active-low action/configuration button; also has a documented startup glitch |
| 11 | Do not allocate until exact die/module flash-supply use is verified |
| 12–17 | Reserved by flash on the intended in-package-flash candidates; confirm the exact received chip |
| 18–19 | Native USB reserved by this design |
| 20 | I2C SCL after reset; UART0 receive function at reset |
| 21 | I2C SDA after reset; UART0 transmit function at reset |

“Unallocated” does not mean electrically safe for an extension. Recheck boot
straps, startup glitches, module circuitry, flash, USB, and firmware before
assigning any spare pin.

## Display and recovery bench gate

1. Flash and identify a bare module with no external harness.
2. With power off, inspect OLED controller claims, pin order, address jumper,
   pull-ups, and supply range; check continuity and shorts.
3. Connect only the OLED, power it from the documented compatible rail, and
   measure that rail plus idle SDA/SCL.
4. Scan and record all ACKs; then run initialization and an all-pixels/orientation
   test.
5. Verify 400 kHz rise time and repeat resets while observing boot logs.
6. Exercise normal reset and GPIO9 BOOT-plus-reset with the intended strap
   resistors and OLED attached.
7. Confirm that USB remains accessible with the cell and external rail isolated
   by the reviewed service procedure.

Do not permanently enclose the module until normal boot, download recovery,
display operation, and headless fallback all pass repeatedly.

## Primary references

- NXP I2C-bus specification UM10204, Rev. 7
  ([NXP-hosted copy](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/other/18306/1/UM10204_I2CSpec.pdf?inline=true))
- Espressif ESP32-C3 I2C guide:
  <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/i2c.html>
- Espressif ESP32-C3 schematic checklist:
  <https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html>
- Espressif USB Serial/JTAG console guide:
  <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/usb-serial-jtag-console.html>
