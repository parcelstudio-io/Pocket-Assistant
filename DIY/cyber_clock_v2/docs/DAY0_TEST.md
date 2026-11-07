# Day 0 — prove the parts before the controller board arrives

**Written 2026-10-28 for the bench on 2026-10-29.** The [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) is in
transit (DigiKey, ordered 2026-10-28). Everything else for Phase 1 is on hand. This
is the shortest test that shows the prototype works before anything is soldered
together with brass or copper. It runs on the free [stand-in controller](https://www.adafruit.com/product/5302), the small
Adafruit board that came with the 2026-10-19 order, because it has a STEMMA QT socket, runs at
3.3 V like every board in the chain, and needs no soldering to use.

When the controller board arrives, the first QT cable moves from the stand-in to the
[QT-to-header cable](https://www.adafruit.com/product/4209) on the controller and the Phase 1 plan in `BUILD_PLAN.md` starts. Nothing
done here has to be undone.

## What to put on the bench

| Item | Qty | Owned as |
| --- | ---: | --- |
| [Stand-in controller](https://www.adafruit.com/product/5302) | 1 | the small Adafruit board that came free with the 2026-10-19 order |
| USB-C data cable (not charge-only) | 1 | owned |
| [QT cable](https://www.adafruit.com/product/4210), 100 mm | 4 | Adafruit, 7 owned |
| [Real-time clock](https://www.adafruit.com/product/5188) | 1 | Adafruit |
| [Coin cell](https://www.amazon.com/dp/B0D8T4C5PK) | 1 | Amazon 10-pack |
| [Rotary encoder](https://www.adafruit.com/product/6310), QT | 1 | Adafruit |
| [Proximity and light sensor](https://www.adafruit.com/product/4161) | 1 | Adafruit (keep the SparkFun ones in the drawer) |
| [Accelerometer](https://www.adafruit.com/product/2809) | 1 | Adafruit |
| [Temperature and humidity sensor](https://www.adafruit.com/product/4566) | 1 | Adafruit |
| Laptop with a serial terminal | 1 | Mu editor, Thonny, or `tio /dev/ttyACM0` on Linux |

Optional for the two extra steps: the [OLED display](https://www.adafruit.com/product/2719) with its header strip,
the Pocket AI's [amplifier](https://www.amazon.com/dp/B0CDWXZZCH), one [speaker](https://www.adafruit.com/product/1669)
of the stereo pair, seven jumper wires.

## Step 1 — two minutes, no computer, no meter

1. Push a coin cell into the real-time clock's holder, **+ side up** (the marked side). No
   need to meter it: a sealed new cell is 3 V.
2. Turn the OLED over and **photograph the BS1/BS2 jumpers**. Do not touch them
   today. The photo is the record of the shipped state (`WIRING_CROSSREF.md`,
   Finding 6); it matters because those two jumpers decide I2C or SPI.
   **Done 2026-11-03** (`photos/oled-back-2026-11-03.jpg`): the board shipped in
   **8080 parallel**, BS1 = 1, BS2 = 1. Both 0 Ω links sit in the upper "(1)" row of
   the R2/R3 and R4/R5 blocks; SPI needs them in the lower "(0)" row, R2 → R3 and
   R4 → R5, as in Adafruit's SPI photo (`photos/oled-jumpers-vs-adafruit-2026-11-03.jpg`).
   The rework is the first step of Optional A. Check the second board the same way.

The multimeter stays in the drawer today. It comes out only where a wrong value
would damage something or cannot be read off a label: cell polarity at a holder's
leads before a cell meets a board, frame-to-net isolation before power, and the
bench supply's set voltage. (Rule from the builder, 2026-10-30.)

## Step 2 — put CircuitPython on the stand-in controller (10 min)

1. Download the stand-in controller's UF2 from
   [circuitpython.org/board/adafruit_kb2040](https://circuitpython.org/board/adafruit_kb2040/).
2. Hold the **BOOT** button, plug in USB-C, release when a drive named **RPI-RP2**
   appears. Drag the UF2 onto it. The drive goes away and **CIRCUITPY** appears.
3. Download the library bundle for the same major version from
   [circuitpython.org/libraries](https://circuitpython.org/libraries) and copy these
   into `CIRCUITPY/lib/`:
   `adafruit_ds3231.mpy`, `adafruit_register/` (folder), `adafruit_seesaw/` (folder),
   `adafruit_vcnl4040.mpy`, `adafruit_lis3dh.mpy`, `adafruit_ahtx0.mpy`.
4. Open the serial console. Press Enter and you should see `>>>`.

**Done 2026-11-03, on the controller board.** The DevKitC-1 N8R8 was plugged in
first, so the stand-in was never used (see the controller section at the end).
Flash erased and CircuitPython 10.3.1 written with esptool over the UART port
(`/dev/ttyUSB0`, no BOOT button needed); on the USB port the board shows as
CIRCUITPY (5.7 MB) and `/dev/ttyACM0`. Bundle 10.x-mpy-20261031: the six libraries
plus `adafruit_displayio_ssd1306.mpy` copied to `lib/`, all nine imports clean,
`>>>` confirmed. Console: `screen /dev/ttyACM0 115200`.

## Step 3 — build the chain one board at a time (15 min)

Plug a QT cable from the stand-in controller's QT socket into the **real-time clock**. In the console:

```python
import board
i2c = board.STEMMA_I2C()
while not i2c.try_lock(): pass
print([hex(a) for a in i2c.scan()]); i2c.unlock()
```

Then add one board at a time with the next cable and run the scan again. The list
should grow in this order:

| Board added | New address | List after the scan |
| --- | --- | --- |
| Real-time clock | 0x68 | `['0x68']` |
| Rotary encoder | 0x49 | `['0x49', '0x68']` |
| Proximity and light sensor | 0x60 | `['0x49', '0x60', '0x68']` |
| Accelerometer | 0x18 | `['0x18', '0x49', '0x60', '0x68']` |
| Temperature and humidity sensor | 0x38 | `['0x18', '0x38', '0x49', '0x60', '0x68']` |

If a board does not appear: reseat both plugs, then swap in another cable. If it
still does not appear, swap in the second board of that type. Adding boards one
at a time is what tells you whether a cable or a board is the problem. Five
boards is the limit of what the stand-in controller's 3.3 V regulator should feed; that is
fine, the gauge is a Phase 4 part.

**Done 2026-11-04, on the controller board.** All five answered in the table's
order: 0x68 at 00:32:58, 0x49 at 00:38:27, 0x60 at 00:41:15, 0x18 at 00:49:31 (the
default address, the one `code.py` uses), 0x38 at about 00:52. Before the header
cable was on, the bus would not start: *No pull up found on SDA or SCL*. The chain
boards carry the pull-ups, so that message means the chain is unplugged or unpowered.

## Step 4 — set the clock, then make every board talk (15 min)

Set the time once, from the console, with today's date and the current time
(year, month, day, hour, minute, second, weekday 0 = Monday, yearday, dst):

```python
import time, board, adafruit_ds3231
rtc = adafruit_ds3231.DS3231(board.STEMMA_I2C())
rtc.datetime = time.struct_time((2026, 10, 29, 10, 30, 0, 3, -1, -1))
```

Save this as `CIRCUITPY/code.py`. It prints one line a second from all five boards.
It looks at the buttons about 30 times a second and keeps any press, so a tap shows.
(The first version looked once a second and missed every press on 2026-11-04.)

```python
import time, board
import adafruit_ds3231, adafruit_vcnl4040, adafruit_lis3dh, adafruit_ahtx0
from adafruit_seesaw import seesaw, rotaryio

i2c = board.STEMMA_I2C()
rtc = adafruit_ds3231.DS3231(i2c)
prox = adafruit_vcnl4040.VCNL4040(i2c)
acc = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18)
aht = adafruit_ahtx0.AHTx0(i2c)

ss = seesaw.Seesaw(i2c, addr=0x49)
assert (ss.get_version() >> 16) & 0xFFFF == 5740, "not an ANO encoder"
names = ["select", "up", "left", "down", "right"]
pins = (1, 2, 3, 4, 5)
mask = sum(1 << p for p in pins)
for pin in pins:
    ss.pin_mode(pin, ss.INPUT_PULLUP)
knob = rotaryio.IncrementalEncoder(ss)
print("buttons at rest:", hex(ss.digital_read_bulk(mask)), "(0x3e = all five released)")

while True:
    # Look at the buttons ~30 times over the second and keep any press, so a tap counts.
    seen, end = set(), time.monotonic() + 1
    while time.monotonic() < end:
        low = ~ss.digital_read_bulk(mask) & mask
        seen.update(n for n, p in zip(names, pins) if low & (1 << p))
        time.sleep(0.03)
    t = rtc.datetime
    x, y, z = acc.acceleration
    pressed = [n for n in names if n in seen]
    print(f"{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}  "
          f"knob={knob.position:4d} {pressed}  "
          f"prox={prox.proximity:4d} lux={prox.lux:5.0f}  "
          f"g=({x:5.1f},{y:5.1f},{z:5.1f})  "
          f"{aht.temperature:4.1f}C {aht.relative_humidity:3.0f}%")
```

Pass when, on the console:

- the time advances by one second per line;
- `knob` changes as you turn the encoder, and each of the five buttons shows its
  name while pressed;
- `prox` jumps from a few counts to hundreds when your hand covers the sensor,
  and `lux` drops;
- one axis of `g` reads about ±9.8 and moves to another axis when you tip the
  board;
- temperature is room-like and humidity rises when you breathe on the sensor.

**Done 2026-11-04, on the controller board** (console log:
`logs/day0-console-2026-11-04.log`). The clock first read 2000-01-01 with its
lost-power flag set, which is what an unset clock reads. It was set from the computer's
NTP time to 00:53:11 and read back within a second. Knob 0 → 71. Proximity 12 → 399
and light 37 → 7 lux under a hand. Gravity moved from the z to the y axis (9.3 m/s²).
Humidity 45 → 53 % from a breath, at 23.6 °C. Buttons: left, up, down and right
seen; **select (the centre button) not yet seen**. Press it once more next session.
An identity check then read each chip's own ID register: clock time advancing and its
thermometer 24.25 °C, encoder firmware 5740, light sensor ID 0x186, accelerometer
WHO_AM_I 0x33 and 9.81 m/s² at rest, humidity sensor calibrated at 23.9 °C, within
0.4 °C of the clock's thermometer: 5 of 5. Re-run it at the REPL with
`import parts_check`; copies of it and `code.py` are in `../bench/circuitpython/`. If the
console says *Running in safe mode … You pressed the BOOT button at start up*, press
RST once without touching BOOT.

## Step 5 — the coin cell keeps the time (5 min)

Unplug USB. Wait one minute. Plug back in and read the console. The time must be
one minute later than when you unplugged, not reset to 2000-01-01. If it reset,
the cell is flat or not seated. This is the only test the alarm clock truly
depends on.

**Passed 2026-11-04.** USB was out for 12 s (01:05:46 to 01:05:58). A header wire
then came loose, so the chain was off the bus until about 01:10:14. The first line
back read 01:10:21 on the clock and 01:10:21 on the computer: no time lost. The board
also restarted three times while the wires were handled (01:02:54, 01:08:08,
01:10:14). Jumper wires on bare header pins are bench-only; the Phase 1 joints are
soldered.

That is the whole prototype test. Put the chain aside connected; it goes onto the
controller board as one piece.

## Optional A — light the OLED (30 min, needs the header soldered)

**First, move the interface links to SPI.** The photo of 2026-11-03 shows the board
shipped in 8080 parallel (BS1 = 1, BS2 = 1). With flux and the iron, lift the 0 Ω
link off the upper "(1)" pads of the R2/R3 block and bridge the lower "(0)" pads
(R3) with solder; same for R4/R5 (link off R4, bridge R5). Upper link off *before*
the lower bridge goes on: both rows fitted shorts VDD to VSS. Finish with the
meter: pin 1 to pin 2 must not beep, and pin 1 must beep to both lower bridges.
The result looks like Adafruit's SPI photo (`photos/oled-jumpers-vs-adafruit-2026-11-03.jpg`).

Solder the included header strip to the OLED, holding it in a breadboard so it
stays square. The header has 20 pins marked by number, not name: glass facing
you, header along the bottom, pin 1 is on the left and pin 20 on the right. Pin 20
is tied to the metal frame, so a continuity beep from an end pin to the frame
finds pin 20; pin 1 is the other end. Solder the kit's 220 µF across pins 1 and 2,
stripe to pin 1. Then seven jumpers from the stand-in controller:

| OLED pin | Function | Stand-in pin |
| --- | --- | --- |
| 1 | GND | G |
| 2 | 3 V power in | 3V (**never** RAW or 5 V; the module is 3.3 V only) |
| 4 | DC | D9 |
| 7 | D0 = SPI clock | CLK |
| 8 | D1 = SPI data | MOSI |
| 15 | CS | D10 |
| 16 | RESET | D8 |

Leave pins 3, 5, 6, 9–14 and 17–20 empty (pin 20, frame ground, may also go to
GND). Pin map from Adafruit's [pinouts page](https://learn.adafruit.com/1-5-and-2-4-monochrome-128x64-oled-display-module/pinouts).

Add `adafruit_displayio_ssd1306.mpy` to `lib/` (this display's controller chip is a
close relative of the one that library was written for, and takes it). On the console:

```python
import board, busio, displayio, adafruit_displayio_ssd1306
try:
    from fourwire import FourWire        # CircuitPython 9 and later
except ImportError:
    from displayio import FourWire       # CircuitPython 8
displayio.release_displays()
spi = busio.SPI(board.CLK, board.MOSI)
bus = FourWire(spi, command=board.D9, chip_select=board.D10, reset=board.D8)
display = adafruit_displayio_ssd1306.SSD1306(bus, width=128, height=64)
```

Pass when the console text appears on the glass. If it stays dark, re-check the
link rework (both bridges in the lower row, no beep between pins 1 and 2) and stop
there; the Phase 1 plan does this properly on the controller board. Do not spend
the evening on it.

## Optional B — a tone through the amp (15 min)

The [amplifier](https://www.amazon.com/dp/B0CDWXZZCH) is the Pocket AI's; it already has pins. Five jumpers plus the
speaker lead:

| Amp pin | Stand-in pin |
| --- | --- |
| VIN | RAW (USB 5 V; the amp takes 2.7–5.5 V) |
| GND | G |
| BCLK | D2 |
| LRC | D3 |
| DIN | D4 |
| OUT+ / OUT− | one [speaker](https://www.adafruit.com/product/1669), either way round; never to ground |

The stand-in controller needs the word-select pin to be the GPIO right after the bit-clock pin,
which D2 and D3 satisfy. On the console:

```python
import board, audiobusio, audiocore, array, math, time
n = 8000 // 440
wave = array.array("h", [int(math.sin(2 * math.pi * i / n) * 6000) for i in range(n)])
out = audiobusio.I2SOut(board.D2, board.D3, board.D4)
out.play(audiocore.RawSample(wave, sample_rate=8000), loop=True)
time.sleep(1); out.stop(); out.deinit()
```

Pass when you hear one second of a 440 Hz tone. It is deliberately quiet
(6000 of 32767); do not raise it on the bare bench.

## What not to do tomorrow

- Do not touch the OLED's BS1/BS2 links except as Optional A says (upper link off, then lower bridge on; never both).
- Do not put a SparkFun [proximity and light sensor](https://www.sparkfun.com/products/15177) on the chain (2.2 kΩ pull-ups; see `INVENTORY.md`).
- Do not solder anything except the OLED header and its capacitor.
- Do not power any QT board from RAW / 5 V.

## If the controller board is already here: run Day 0 on it instead (added 2026-10-30)

The small Adafruit board was only a stand-in. If the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) has arrived, do
Steps 1-5 on it; Step 2 and the line that opens the I²C bus change,
nothing else does.

**Step 2 on the controller board (15 min).** The board has two USB-C ports, labelled
**UART** and **USB**. CircuitPython for it is at
[circuitpython.org/board/espressif_esp32s3_devkitc_1_n8r8](https://circuitpython.org/board/espressif_esp32s3_devkitc_1_n8r8/)
(10.3.1 stable on 2026-10-30). The board has no UF2 bootloader from the factory,
so the drag-and-drop route does not work the first time:

1. In Chrome, press **OPEN INSTALLER** on that page. Plug the **UART** port into
   the laptop, hold **BOOT**, tap **RESET**, release BOOT. Pick the serial port
   when asked and let the installer write TinyUF2 and CircuitPython.
2. Move the cable to the **USB** port and press RESET. **CIRCUITPY** appears.
   From here on it behaves like the stand-in: drag a UF2 onto the BOOT drive to
   update, copy the same six libraries into `CIRCUITPY/lib/`.
3. The serial console is on the **USB** port too.

From a Linux computer the installer is not needed (done this way 2026-11-03): on the
**UART** port, `esptool --chip esp32s3 --port /dev/ttyUSB0 erase-flash`, then
`esptool --chip esp32s3 --port /dev/ttyUSB0 write-flash 0x0` with the `.bin` from
the same page. No buttons: the UART bridge works the boot pins itself. Then move to
the **USB** port and press RST without touching BOOT, because BOOT held at start-up
drops CircuitPython into safe mode.

**Wiring.** The [QT-to-header cable](https://www.adafruit.com/product/4209) instead of the stand-in's socket: red to **3V3**, black to
**GND**, blue (SDA) to **GPIO8**, yellow (SCL) to **GPIO9**. These are the pins the
firmware's `board_pins.h` already assumes. Its QT plug then takes the first QT cable
to the real-time clock and the chain grows exactly as in Step 3.

**Snippets.** The controller board has no `board.STEMMA_I2C()`. Add `busio` to each
snippet's `import` line and open the bus with this wherever a snippet says
`board.STEMMA_I2C()`:

```python
i2c = busio.I2C(board.IO9, board.IO8)   # SCL, SDA
```

(Corrected 2026-11-04: this used to say "replace the first two lines of every
snippet", which drops the Step 4 imports.) The addresses, the rest of the Step 4
`code.py` and the Step 5 coin-cell test are unchanged.
When Day 0 passes this way the hardware side of Day 1 is already done and
`BUILD_PLAN.md` Phase 1 starts at the ESP-IDF toolchain.

## When the controller board arrives after a stand-in Day 0

Unplug the first QT cable from the stand-in controller and plug it into the
[QT-to-header cable](https://www.adafruit.com/product/4209); land that cable on the controller board's 3V3, GND, GPIO8 (SDA) and GPIO9 (SCL). The chain
is already proven and the clock is already set, so Day 1 of `BUILD_PLAN.md`
Phase 1 starts at the toolchain, not at the hardware.

**Optional A done 2026-11-07, on the controller board.** The screen stayed dark through
every test until the BS1/BS2 links were moved (the "102" parts were still on R2 and R4
in the photos; R3 and R5 are now solder bridges). Then the all-pixels-on command lit
the glass and `bench/circuitpython/oled_clock.py` (title + live clock from the
real-time clock) ran, text the right way round. Pins on the controller board: GND, 3V3,
DC GPIO6, clock GPIO12, data GPIO11, CS GPIO10, reset GPIO7. Earlier the same evening
the board overheated with the first (bare twisted-wire) OLED harness: a short, cleared
by rewiring with insulated wire. `adafruit_display_text` added to `lib/`.

**Chain re-checked 2026-11-07 04:00.** After the OLED work only the clock answered;
reseating the QT cable out of the clock brought all five back. `parts_check` PASS on
knob, proximity/light, accelerometer, humidity; clock keeps exact time, its lost-power
flag (set during the short) cleared. 90 s live watch (`live_chain.py`): knob 91 steps,
proximity to 289, light 919 → 3 lux covered, all six tilt directions. `dashboard.py`
(clock, light/prox, tilt, knob + last button on the OLED, 5 min): builder reports the
button names appeared on the glass, including which ones is unconfirmed; the serial
log recorded no press. 220 µF stripe confirmed on pin 1. Board unplugged 04:12.
