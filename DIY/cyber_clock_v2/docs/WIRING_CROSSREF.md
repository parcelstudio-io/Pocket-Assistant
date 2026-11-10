# Wiring cross-reference

Every connection in the Phase 1 bench build, checked against the component's own
published specification. Verified **2026-09-24**. Companion to
[`REVIEW.md`](REVIEW.md); the pin map itself is in
[`firmware/main/include/board_pins.h`](../firmware/main/include/board_pins.h).

**Verdict: the interconnect is electrically sound.** Six findings change what you
solder or what you plug it into; none change the architecture.

**Rev B 2026-10-31: solar removed, compact body, 16340 cell.** Nothing in the Phase 1 wiring below changes.
What changes is the Phase 4 source behind the 5 V rail: one Nitecore 16340 cell (950 mAh, protected, 2 A
discharge limit, 4.20 V termination) in the owned [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F),
through the [fuel gauge](https://www.adafruit.com/product/5580) into the [charger board](https://www.adafruit.com/product/6106)'s BAT port, charger jumper at 500 mA,
the charger board's 5 V boost output into the controller's 5V pin. No solar input, no 6600 mAh pack. Findings 3 and 4
are amended in place below; the body is 82 × 52 × 68 mm, see [`COMPACT_DESIGN.md`](COMPACT_DESIGN.md).

**Verified against datasheets 2026-10-31** (REVIEW.md, "Rev B verification"): Finding 4 and §3 are corrected in place, the
controller board's regulator being an 800 mA low-dropout part rather than the 1.1 V-dropout part assumed in September.

---

## 1. Voltage domains

The ESP32-S3's GPIO is **3.3 V and not 5 V tolerant**, so every logic connection
has to be checked, not assumed.

| Component | Supply | Logic level | Direct to S3? |
| --- | --- | --- | --- |
| [Controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) | 5 V in, an 800 mA low-dropout linear regulator to 3.3 V | 3.3 V | — |
| [OLED display](https://www.adafruit.com/product/2719), 2.42" | **3.3 V only** | **3.3 V only** | **yes** |
| [Real-time clock](https://www.adafruit.com/product/5188) | 3.3 V | 3.3 V, INT open-drain | yes, with pull-up |
| [Amplifier](https://www.adafruit.com/product/3006) | **5 V** (2.7–5.5 V) | thresholds are absolute, not ratiometric | yes |
| [Fuel gauge](https://www.adafruit.com/product/5580), [proximity and light sensor](https://www.adafruit.com/product/4161), [accelerometer](https://www.adafruit.com/product/2809), [temperature and humidity sensor](https://www.adafruit.com/product/4566), [rotary encoder](https://www.adafruit.com/product/6310) | 3.3 V via STEMMA QT | 3.3 V | yes |

### Finding 1 — the level shifter stays in the bag

The OLED kit ships with a level shifter. Adafruit are explicit that the module
"requires a 3.3 V power supply and 3.3 V logic levels," and the shifter exists
only so **5 V** parts like an Arduino Uno can drive it.

The ESP32-S3 is already 3.3 V. **Wire the OLED straight to the S3 and leave the
level shifter unused** — it removes an IC, about twelve solder joints, and a failure
point from the largest soldering job in the project. Keep the included 220 µF
capacitor; Adafruit fit it because the module wants a stiff 3.3 V rail.

### Finding 2 — the amplifier runs from 5 V, and should stay there

The amplifier's control thresholds are quoted as absolute voltages (shutdown
below 0.16 V, left channel above 1.4 V), not as fractions of VIN. A 3.3 V GPIO
therefore reads as a solid logic high even with VIN at 5 V.

Running the amplifier from 3.3 V instead is tempting — it would delete the 5 V
rail from the audio path, and output would fall to 3.2 W × (3.3/5)² ≈ 1.39 W,
close to the 1.6 W the 6 dB strap gives on 5 V anyway. **Do not do it.** That
extra ~364 mA would pass through the controller board's regulator, which is already this build's
thermal bottleneck (§3). Keep the amplifier on 5 V.

---

## 2. The 5 V rail, and the bench supply you need

Current during an alarm, with the 6 dB gain strap fitted:

```text
amplifier, 1.6 W out at ~88% efficiency = 1.82 W / 5 V  = 364 mA average
                                          peak (sine)    = 0.89 A
controller board: its regulator is linear, so 3.3 V load current is
        drawn from 5 V one-for-one                       = 565 mA
                                                  total  ≈ 930 mA average
```

### Finding 3 — a laptop USB port will not do for Days 4 and 5

| Source | Budget | Verdict |
| --- | ---: | --- |
| USB 2.0 port | 500 mA | **insufficient** |
| USB 3.0 port | 900 mA | marginal |
| USB-C wall adapter | 2 A+ | **use this** |

Days 1–3 draw well under 500 mA and any port is fine. **From Day 4, plug the
bench into a wall adapter.** A brownout caused by the host port looks exactly
like a design fault and will cost an evening to chase.

*Rev B, 2026-10-31:* unplugged, the same ~930 mA average and 0.9 A amplifier peaks come from the 16340
cell through the charger board's boost. The cell's protection allows 2 A continuous, so the cell is not the
limit; the boost's 1 A rating is, which is why the 6 dB gain strap stays. Plugged in, the charger board's
own USB-C port takes the 2 A wall adapter and the controller's USB socket stays empty.

### Finding 4 — the regulator's dropout is the brownout mechanism (corrected 2026-10-31)

The [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) regulates with an **800 mA low-dropout linear regulator**
(Espressif's v1.1 schematic names it; the September draft assumed a 1.1 V-dropout part). Its datasheet gives
**0.24 V typical dropout at 500 mA, 0.45 V worst case at 800 mA**. Two consequences worth writing down:

1. **The 5 V rail must stay above about 3.7 V or the 3.3 V rail collapses.** This
   is the precise mechanism behind the Phase 4 brownout risk in `REVIEW.md` §8.2:
   an amplifier transient sags the boost, the sag crosses the dropout threshold,
   and the ESP32-S3 resets mid-alarm. It is not a vague worry — it has a number,
   and the number is kinder than the 4.4 V first written here.
   *Rev B:* the rule applies only while the clock is unplugged and running on the
   16340 cell; plugged in, the charger board's power path feeds the boost from USB.
2. **The boost is still needed**, for the amplifier's 5 V, the board's USB-serial
   bridge, and so the 3.3 V rail holds across the cell's whole 3.0–4.2 V range; a
   cell wired straight to the 5V pin would drop out of regulation near 3.6 V.
3. On USB power the board's 5V pin sits one Schottky drop below VBUS (the v1.1
   schematic puts a diode in each USB port's VBUS line), so in Phase 1 the amplifier
   sees about 4.6 V there, which is fine; and feeding 5 V into the pin in Phase 4
   cannot back-drive the USB sockets. Espressif's one-source rule stands regardless.

---

## 3. The 3.3 V rail

| Load | Current |
| --- | ---: |
| ESP32-S3, Wi-Fi transmitting | ~350–500 mA peak |
| [OLED display](https://www.adafruit.com/product/2719) | 50 mA |
| Six I²C breakouts | ~15 mA |
| Regulator quiescent | ~5 mA |
| **Peak total** | **~570 mA** |

The regulator is rated 800 mA (corrected 2026-10-31: not the 1 A part first assumed), so
570 mA is 71 % of its rating, and **heat is** the nearer limit. At 570 mA it dissipates
(5 − 3.3) × 0.57 ≈ **0.97 W** in a SOT-223 package. That is warm but survivable. At its
full 800 mA it would be 1.36 W, close to thermal shutdown.

**Rule that follows: do not add further 3.3 V loads to the controller board's regulator.**
Anything new gets its own supply, which is also why the amplifier stays on 5 V.

---

## 4. The I²C bus, checked against the specification

Each Adafruit STEMMA QT board carries **two 10 kΩ pull-ups** (one per line). Six
boards on one bus put six in parallel:

```text
R_pullup  = 10 kΩ / 6                     = 1.67 kΩ
I_sink    = 3.3 V / 1.67 kΩ               = 1.98 mA   (I²C limit: 3 mA)
C_bus     ≈ 6 boards x 10 pF + ~750 mm cable at ~50 pF/m  ≈ 100–150 pF
t_rise    = 0.8473 x 1.67 kΩ x 150 pF     = 212 ns
```

| Check | Measured against | Result |
| --- | --- | --- |
| Sink current | 3 mA I²C maximum | **1.98 mA — 66% of budget, passes** |
| Rise time, 400 kHz fast mode | 300 ns maximum | **212 ns — passes, 29% margin** |
| Rise time, 100 kHz standard mode | 1000 ns maximum | passes easily |

**The bus is legal at 400 kHz as designed.** It is the seventh device that would
push sink current past 2.3 mA and start eroding the margin — at that point remove
the pull-up jumper from two or three boards rather than lowering the clock.

---

## 5. Connection-by-connection

| From | To | Validated by |
| --- | --- | --- |
| GPIO8 / GPIO9 | SDA / SCL of the chain, via the [QT-to-header cable](https://www.adafruit.com/product/4209) | §4; red 3V3, black GND, blue SDA, yellow SCL |
| GPIO4 | [Real-time clock](https://www.adafruit.com/product/5188) `INT/SQW` + **10 kΩ to 3V3** | Output is open-drain: it can only pull low. Pull-up is mandatory, not hardening |
| GPIO1 | [Rotary encoder](https://www.adafruit.com/product/6310) `INT` | **See finding 5** |
| GPIO12 / 11 / 10 | OLED SCLK / MOSI / CS | FSPI IO_MUX pins; 3.3 V direct, no shifter |
| GPIO6 / GPIO7 | OLED DC / RESET | 3.3 V direct |
| 3V3 | OLED VCC | Module is 3.3 V only — **never 5 V** |
| GPIO14 / 15 / 16 | Amp BCLK / LRC / DIN | 3.3 V logic into a 5 V-powered part; thresholds absolute |
| GPIO17 | Amp `SD` | Board has 1 MΩ SD→VIN, so the amp powers up **enabled**. Drive LOW before anything else |
| Amp `GAIN` | Amp `VIN` | Selects 6 dB; caps output at ~1.6 W into 4 Ω |
| Amp `OUT+` / `OUT−` | Speaker | Bridge-tied — **neither lead to ground, ever** |
| 5V | Amp `VIN` | 2.7–5.5 V range; 5 V gives the rated output |
| [Charger board](https://www.adafruit.com/product/6106) 5 V out | Controller 5V pin (Phase 4, Rev B) | One source at a time: the controller's USB socket is empty whenever the charger feeds the 5V pin |
| [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) | JST-PH pigtail → [fuel gauge](https://www.adafruit.com/product/5580) → charger `BAT` (Phase 4, Rev B) | Protected cell, 2 A limit, 4.20 V termination; charger jumper at 500 mA. **Meter the holder leads for polarity before the cell goes in** |
| GPIO18 / GPIO21 | Snooze / arm, other leg to GND | Internal pull-ups; active-low. In deep sleep the internal pull-ups hold only while the RTC peripheral domain stays powered (ESP-IDF sleep modes), so the firmware keeps it on, or 10 kΩ go on the board |
| GPIO40 | 100 Ω → MOSFET gate; **10 kΩ gate to GND** (added 2026-11-05) | The sunrise lamp's switch. The [MOSFET](https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089)'s threshold is 1.45 V at most, so 3.3 V turns it fully on; the pull-down holds it off while the controller boots. **See finding 7** |
| Cell + (spliced into the holder's pigtail + lead) | 15 Ω → [LED filament](https://www.amazon.com/dp/B0FR35BGYL) + ; filament − → MOSFET drain; source → GND | Up to about 0.1 A on a full cell, 0.06 A at 3.7 V. **Not on the 5 V boost**: see finding 7. Bench, before the cell: 5V pin through 33 Ω instead |

### Finding 5 — GPIO1 needs a pull-up too

The rotary encoder adapter's `INT` output is described as pulsing low on activity, which is
the signature of an **open-drain** output — the same arrangement as the real-time clock.
Nothing in the pin map or the firmware notes provides a pull-up for it.

Unlike GPIO4, this line does not have to be valid before firmware runs, so the
**ESP32's internal pull-up on GPIO1 is sufficient**. No external resistor. But it
must be enabled explicitly, or the interrupt will never be seen and the encoder
will appear to work only when polled.

### Finding 6 — confirm the OLED's interface mode on arrival

The module selects between 8-bit parallel, 4-wire SPI and I²C using **BS1/BS2
solder jumpers (0 Ω resistors) on the back**. Adafruit say it "may come in SPI
mode," and their own forum has repeated reports that the silkscreen around those
jumpers is ambiguous about which position is which.

**Check the jumpers before wiring anything**, and photograph them first so you can
get back to the shipped state. Confirming this is already Phase 0 work in
`BUILD_PLAN.md`; this is the specific thing to look at.

**Resolved 2026-11-03.** The first board (silkscreen 2420B-12864OLED V3.1) shipped in
**8080 parallel**, BS1 = 1, BS2 = 1: both 0 Ω links in the upper "(1)" row of the R2/R3
and R4/R5 blocks (`photos/oled-back-2026-11-03.jpg`, compared with Adafruit's mode
photos in `photos/oled-jumpers-vs-adafruit-2026-11-03.jpg`). SPI needs R2 → R3 and
R4 → R5, the lower "(0)" row. The rework is in `DAY0_TEST.md` Optional A. Second
board not yet checked.

### Finding 7 — the sunrise lamp runs from the cell, not the 5 V boost (added 2026-11-05)

The builder added the warm [LED filament](https://www.amazon.com/dp/B0FR35BGYL) as a sunrise
lamp on the lid. At the brightness a wake light wants, about 0.1 A, it cannot share the
charger board's 5 V boost: that boost is rated 1 A and an alarm already peaks near 0.93 A
(finding 3). The cell itself allows 2 A continuous, so the lamp takes its current straight
from the cell's + lead, spliced into the holder's pigtail before the fuel gauge, and the boost
budget is unchanged. Plugged in, the charger feeds the cell node, so the lamp is still covered.

The cell's voltage swings from 4.2 V full to about 3.3 V empty, and with a fixed 15 Ω the
filament's current swings with it (about 0.1 A down to 0.04 A). The firmware reads the cell
voltage from the fuel gauge and scales the PWM duty, so a sunrise looks the same on any charge.

GPIO40 drives the gate through 100 Ω with 10 kΩ to ground. **Unconfirmed:** whether GPIO40
carries a weak pull-up between reset and firmware. If it does, the divider puts about 0.6 V on
the gate, under the MOSFET's 0.65 V minimum threshold: at most a faint glimmer for the
fraction of a second before firmware drives it low. If that shows on the bench, use 4.7 kΩ.

The proximity and light sensor sits under the lid a few millimetres from the slot. Firmware
ignores its light reading while the lamp is lit.

---

## 6. Summary of changes

| # | Finding | Action |
| ---: | --- | --- |
| 1 | Level shifter unnecessary at 3.3 V | Leave it unused; ~12 fewer joints |
| 2 | Amplifier belongs on 5 V | No change — record why |
| 3 | ~930 mA during an alarm | Use a 2 A wall adapter from Day 4; in Rev B the 16340 cell's 2 A limit covers it unplugged |
| 4 | Regulator dropout ≈ 0.3 V (corrected from 1.1 V) | 5 V rail must stay above ~3.7 V; this is the brownout threshold to scope in Phase 4, now only while unplugged on the cell |
| 5 | Encoder `INT` is open-drain | Enable the internal pull-up on GPIO1 |
| 6 | OLED mode jumpers ambiguous | Photograph and verify in Phase 0 |
| 7 | Sunrise lamp would overload the 1 A boost | Feed it from the cell + through 15 Ω; MOSFET on GPIO40; firmware scales duty by cell voltage |

## 7. Still to confirm on the hardware

These cannot be settled from documents:

- Measured I²C rise time with all six boards and the real cable lengths fitted.
- The regulator's actual temperature at full Wi-Fi transmit plus OLED.
- ~~Which BS1/BS2 state the OLED actually ships in.~~ Settled 2026-11-03: 8080 parallel (Finding 6).
- The exact addresses of the proximity, accelerometer, temperature/humidity and fuel-gauge breakouts —
  one `i2cdetect` sweep on Day 2 settles all four.
- Rev B: the polarity of the 16340 holder's leads and of the JST-PH pigtail (meter them), and the 5 V rail's
  sag at an alarm peak while running unplugged on the cell.
- The sunrise lamp's current at 4.2 V and 3.7 V (meter in series), and whether it glimmers at boot (finding 7).
