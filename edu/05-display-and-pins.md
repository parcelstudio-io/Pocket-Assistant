# The display, I2C, and the ESP32-C3's boot-strapping pins

## I2C in three sentences

I2C is a two-wire party line: one data wire (SDA), one clock wire (SCL), and
any number of devices, each with a 7-bit address. The ESP32-C3 (the bus
master) calls an address; only the matching device answers. Our bus has one
device — the SSD1306 OLED — on SDA=GPIO21, SCL=GPIO20.

## The 0x3C / 0x3D trap

Here is a trap that would have cost a finished, soldered build:

- Generic 4-pin 0.96" SSD1306 modules answer at address **0x3C**.
- Adafruit's 128 × 64 breakouts — including the white #326 this build uses —
  ship answering at **0x3D** (their own example code says so:
  `0x3D for 128x64, 0x3C for 128x32`).
- The original firmware hard-coded 0x3C **and** treated any display-init
  error as fatal. Wrong address → the chip aborts → instant reboot → abort
  again: an endless boot loop with no Wi-Fi, no audio, and no time to even
  read the log. The pager would look completely dead because of a solder
  jumper on the back of the screen.

The corrected firmware (already built) does two things instead:

1. **Probes** 0x3C first, then 0x3D, and uses whichever answers — so either
   display drops in with no configuration.
2. If neither answers, it **logs the failure and boots headless** — a pager
   that still listens and talks is infinitely easier to debug than a boot
   loop.

## Strapping pins — why the microphone moved to GPIO4

When an ESP32-C3 comes out of reset, it reads a few pins *before your
program runs* to decide how to boot. These "strapping pins" are GPIO2, GPIO8,
and GPIO9:

- **GPIO9** — the BOOT button. Held low at reset = "enter the serial
  bootloader so a computer can reflash me."
- **GPIO8** — must read **high** while entering that bootloader.
  (GPIO8 = 0 with GPIO9 = 0 is marked *invalid* in Espressif's table.)
- **GPIO2** — Espressif recommends pulling it high at boot.

The original design wired the microphone's data output to **GPIO8**. The mic
mostly leaves that line floating, but nothing guarantees its level at the
instant of reset — and on the SuperMini, GPIO8 also carries the onboard blue
LED. If the line ever sits low during a BOOT-button reset, the serial
bootloader becomes unreachable. This build has **no over-the-air update
partitions**, so USB download mode is the *only* recovery path. Losing it on
a board soldered inside a finished brass sculpture is permanent.

The fix is one line of firmware and one wire: the microphone's data now
lands on **GPIO4**, an ordinary pin with no boot meaning (its alternate JTAG
role is already covered by the SuperMini's native USB debugging). GPIO8 gets
a 10 kΩ pull-up to 3.3 V so its strap level is defined; GPIO2 — which now
carries only the I2S bit clock into two well-behaved inputs — gets the same,
per Espressif's own schematic checklist.

## The full pin budget

Every usable pin on the SuperMini, and why it is (or is not) free:

| GPIO | Use in this build | Note |
| ---: | --- | --- |
| 0 | Unused in Rev A | ADC-capable, but current firmware has no battery-monitor implementation |
| 1 | I2S WS (shared) | |
| 2 | I2S BCLK (shared) | Strap pin — 10 kΩ pull-up fitted |
| 3 | I2S data → amplifier | |
| 4 | I2S data ← microphone | Moved here from GPIO8 |
| 5–7 | Free | Spares for extensions |
| 8 | *(unused)* + 10 kΩ pull-up | Strap pin + onboard LED |
| 9 | BOOT button (on the module) | Strap pin — leave alone |
| 10 | Action button → GND | The firmware's only user input |
| 11–17 | **Not available** | Internal SPI flash |
| 18, 19 | **Not available** | Native USB D−/D+ |
| 20 | I2C SCL | |
| 21 | I2C SDA | |

Two takeaways for the bench: the action button on GPIO10 is worth fitting
(it is the manual chat toggle *and* the long-press Wi-Fi reset — without it,
a botched Wi-Fi provisioning means reflashing), and pins 5–7 are the
project's entire expansion budget, so spend them deliberately.
