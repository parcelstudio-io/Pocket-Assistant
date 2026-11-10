# Design review — Cyber Dawn

Independent review of the design set in this directory. Verified **2026-09-23** against
primary sources: vendor product pages, TI's datasheet for the [charger board](https://www.adafruit.com/product/6106)'s
charger chip (SLUSF65B, revised August 2026), and Espressif's v1.1 user guide for the
[controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894).

**Verdict: the design is sound and the reasoning is honest. One hard component
incompatibility and three pin-map defects must be fixed before ordering.** All four are
resolved below with decisions, not options.

**Rev B 2026-10-31: solar removed, compact body, 16340 cell.** The pin map (§3) and the
interconnect findings (§8) stand. The battery is now one Nitecore 16340 cell (950 mAh, protected,
2 A discharge limit, 4.20 V termination) with the charger board's jumper at 500 mA, charged through
the charger board's own USB-C port; no solar input. §2.1, the 6 h charge-timer analysis, the solar
remarks in §4 and §5, the totals in §6 and the 165 × 92 × 72 mm envelope are **superseded** and kept
as the record; the body is 82 × 52 × 68 mm, see [`COMPACT_DESIGN.md`](COMPACT_DESIGN.md).

---

## 1. What was verified, and against what

Everything in this table was checked against a primary source rather than accepted.

| Claim under review | Source | Result |
|---|---|---|
| BOM subtotals $131.48 / $175.38 / $213.88 | recomputed | **Exact**, all three |
| Battery math 24.42 Wh → 16.61 Wh → 72/42/30 h | recomputed | **Exact** |
| Energy model 0.23/0.40/0.55 W → 5.5/9.6/13.2 Wh | recomputed | **Exact** |
| Panel yield table (four rows) | recomputed | **Exact** |
| Partition table fits 8 MB, 64 KB-aligned slots | recomputed | **Byte-perfect** |
| ESP32-S3 strapping pins 0, 3, 45, 46 | Espressif | **Correct** |
| Octal-PSRAM pins unavailable on the 8 MB-PSRAM [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) | Espressif v1.1 guide | **Correct as written: 35, 36, 37** |
| [OLED display](https://www.adafruit.com/product/2719) driver is SSD1305/SSD1309 | Adafruit | **Correct** — SSD1305, SSD1309 since Sept 2023 |
| OLED display draws ~50 mA at 3.3 V | Adafruit | **Correct**, $39.95, in stock |
| 5 W [solar panel](https://www.adafruit.com/product/5367) is 5 W / 6.12 V / 940 mA, 148×223×4 mm | Voltaic | **Correct** — 5 W nominal, 5.75 W peak, Voc 7.13 V, $35.00 (panel owned, not used in Rev B) |
| [Charger board](https://www.adafruit.com/product/6106)'s safety timer is fixed at six hours | TI SLUSF65B §5.5 | **Correct** — t(MAXCHG) = 360 min typ, fixed in silicon (moot with the Rev B cell: ~3 h to terminate at 500 mA) |
| ESP32-S3 has no Classic Bluetooth / A2DP | Espressif | **Correct** |
| BMI160 `0x68` collides with the [real-time clock](https://www.adafruit.com/product/5188) | datasheets | **Correct** — a real flaw in the *reference* build |
| ESP-IDF "not installed, not compiled" | this machine | **True** — `idf.py` absent, `IDF_PATH` unset |

Three claims in an earlier draft of this review were wrong and are corrected here:

- **Octal PSRAM reserves 35–37, not 33–37.** Espressif's v1.1 guide names exactly GPIO35,
  GPIO36, GPIO37. The original text was right; GPIO33 and GPIO34 are free.
- **The controller board's RGB LED revisions were stated backwards.** See §2.2.
- **The solar panel's spec is not internally inconsistent.** 6.12 V × 940 mA = 5.75 W is Voltaic's
  own *peak* figure for a panel they rate 5 W nominal. The original text quoted it correctly.

---

## 2. Defects, with decisions

### 2.1 The charger board cannot charge a 6600 mAh pack — DECIDED: use the 4400 mAh pack — SUPERSEDED 2026-10-31

*Rev B:* the builder bought the 6600 mAh pack anyway on 2026-10-26, then replaced it on 2026-10-31 with one
Nitecore 16340 cell, 950 mAh protected, charger jumper at 500 mA (about 0.5 C). A 950 mAh cell at 500 mA
terminates in roughly 3 h, inside the 6 h timer with margin, so the analysis below no longer bites. The
6600 mAh pack is owned and held for another project. The timer arithmetic is kept as the record.

This is the one hard incompatibility, and it is worse than the docs suggest: they frame it
as a weak-solar risk, but it fails on USB at full current too.

TI SLUSF65B §5.5 gives **t(MAXCHG) = 360 min typical**, with no min/max column — it is fixed
in the die, not a breakout choice. §6.3.7.7: if charging has not terminated when the timer
expires, charging is **disabled** and STAT1/STAT2 latch to a *non-recoverable* fault
(both LOW, §6.3.10). Recovery requires toggling `/CE` or cycling input power.

The [charger board](https://www.adafruit.com/product/6106) defaults to **ICHG = 1 A** (jumper cuts it to 500 mA, which would make this
worse, not better). Charge time to termination, assuming the CC phase delivers ~80% of
capacity and CV taper adds 1.0–1.5 h:

| Pack | CC charge, no system load | CC charge, 250 mA system load | + CV taper | vs 6 h limit |
|---|---:|---:|---:|---|
| 6600 mAh [battery](https://www.adafruit.com/product/353) | 5.28 h | 6.21 h | **6.3 – 7.7 h** | **Fails** |
| 4400 mAh [battery](https://www.adafruit.com/product/354) | 3.52 h | 4.14 h | **4.5 – 5.6 h** | **Fits**, 0.4–1.5 h margin |

**Decision: substitute the 4400 mAh battery for the 6600 mAh one.**

- $19.95 in stock, 69 × 37 × 18 mm, 95 g, 2 × 2200 mAh 18650 in parallel, protected, JST-PH.
- **Max recommended charge current is 1 A** — an exact match for the charger board's default.
- Smaller and 60 g lighter, which helps the 165 × 92 × 72 mm envelope (superseded: the Rev B body is 82 × 52 × 68 mm, [`COMPACT_DESIGN.md`](COMPACT_DESIGN.md)).
- **Saves $4.55.**

Revised reserve: 4400 mAh × 3.7 V = 16.28 Wh nominal; × 0.80 usable × 0.85 conversion =
**11.07 Wh delivered**.

| Mode | Runtime on the 4400 mAh pack |
|---|---:|
| Eco, 5.5 Wh/day | **48 h** |
| Balanced, 9.6 Wh/day | **28 h** |
| Always connected, 13.2 Wh/day | **20 h** |

For a mains-powered bedside clock whose battery is an outage reserve, 48 h of eco runtime is
ample. The 6600 mAh pack bought runtime the charger could never actually replace.

**Keep the [charger board](https://www.adafruit.com/product/6106). Do not switch to the large-pack [solar charger](https://www.adafruit.com/product/4755) + boost.** The charger chip's battery-tracking
VINDPM (§6.3.1, threshold = V_BAT + 330 mV) is real near-MPPT behaviour and is the correct
feature for a weak, high-impedance solar source. With the pack downsized, its only
disqualifying limitation is gone. The large-pack charger path costs $32.45 versus $8.95 and adds a
second board for no remaining benefit.

**Non-obvious consequence worth recording (solar removed in Rev B; kept as the record):** the 6 h timer is *not* a problem for solar even
though solar charging is slow. The panel goes dark each night, V_IN collapses, the device
enters sleep mode (§6.3.4), and sunrise starts a **fresh charge cycle with a fresh timer**.
Solar effectively gets one 6 h window per day, which is already more than the 4 peak-sun-hours
the energy model assumes. The timer only bites on continuous USB power.

### 2.2 GPIO38 collides with the onboard RGB LED — DECIDED: move to GPIO47

Espressif's v1.1 user guide for the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) states plainly: *"Addressable RGB LED, driven by GPIO38,"* and
*"the initial version uses GPIO48, whereas v1.1 uses GPIO38."*

**v1.1 is the current shipping revision**, so `CYBER_PIN_BACKUP_BUZZER 38` drives a line that
already has an addressable-LED data input on it. This is the same defect class that forced the microphone
off GPIO8 in `pocket_ai_assistant`.

**Decision: move the backup buzzer to GPIO47, and treat both GPIO38 and GPIO48 as
board-reserved** so the map is revision-proof.

### 2.3 GPIO1 is assigned twice — DECIDED: separate the maps and guard them

`board_pins.h` defines `CYBER_PIN_ANO_INTERRUPT 1` and `CYBER_PIN_ENCODER_A 1`. The comment
says the budget encoder "replaces" the [rotary encoder](https://www.adafruit.com/product/6310), but nothing enforces it: include both and
whichever driver initialises last silently wins, with no error.

**Decision: give the two input options completely non-overlapping pins and wrap them in a
compile-time guard**, so the conflict is impossible rather than merely discouraged.

### 2.4 Three "wake" pins cannot wake from deep sleep — DECIDED: move the IMU, keep the rest

**ESP32-S3 RTC-capable GPIOs are 0–21 only.** Confirmed against the ESP-IDF sleep-modes
documentation; `esp_sleep_enable_ext1_wakeup()` accepts nothing above GPIO21.

| Pin | Assignment | RTC-capable? | Consequence |
|---|---|---|---|
| 4 | [Real-time clock](https://www.adafruit.com/product/5188) INT/SQW | **Yes** | Alarm wake works — the critical path is fine |
| 18 | Snooze button | **Yes** | Fine |
| 21 | Alarm-arm | **Yes** | Fine |
| 40 | IMU interrupt | **No** | Documented as "motion/tap wake" — **cannot do that** |
| 39 | Fuel-gauge alert | **No** | Acceptable |
| 41 | Charger status | **No** | Acceptable |

**Decision: move the IMU interrupt to GPIO5** (RTC-capable, free once the budget encoder's
push moves). Leave the gauge alert and charger status where they are and poll them on wake —
neither needs to interrupt a sleeping device. Document that tap-to-wake is unavailable if the
budget encoder is fitted instead of the I²C [rotary encoder](https://www.adafruit.com/product/6310).

---

## 3. Decided pin map

Constraints applied: RTC-capable 0–21 · strapping 0, 3, 45, 46 · octal PSRAM 35–37 ·
native USB 19, 20 · UART0 43, 44 · SPI flash 26–32 · RGB LED 38 (v1.1) and 48 (v1.0) ·
FSPI IO_MUX 10–13.

| Function | GPIO | Change | Note |
|---|---:|---|---|
| I2C SDA / SCL | 8 / 9 | — | Shared peripheral bus |
| OLED SCLK / MOSI / CS | 12 / 11 / 10 | — | FSPI IO_MUX pins — fastest path, keep |
| OLED DC / RESET | 6 / 7 | — | |
| I2S BCLK / WS / DOUT | 14 / 15 / 16 | — | |
| Amplifier shutdown | 17 | — | Default low through reset |
| [Real-time clock](https://www.adafruit.com/product/5188) INT/SQW | 4 | — | RTC-capable; external pull-up to 3V3 required |
| [Rotary encoder](https://www.adafruit.com/product/6310) interrupt | 1 | — | Primary option; RTC-capable |
| IMU interrupt | **5** | was 40 | **Now RTC-capable — tap-to-wake works** |
| Snooze button | 18 | — | RTC-capable |
| Alarm-arm switch | 21 | — | RTC-capable |
| Backup buzzer MOSFET | **47** | was 38 | **Clears the RGB LED on v1.1** |
| Fuel-gauge alert | 39 | — | Poll on wake; not a wake source |
| Charger status | 41 | — | Poll on wake; not a wake source |
| Budget encoder A / B / push | **2 / 33 / 13** | was 1 / 2 / 5 | Alternative build only; no overlap with the rotary encoder map |
| Native USB D− / D+ | 19 / 20 | — | Reserved |
| UART0 TX / RX | 43 / 44 | — | Reserved |

GPIO39–42 are the JTAG pins (MTCK/MTDO/MTDI/MTMS). Using 39 and 41 as plain GPIO is safe
here because the ESP32-S3's USB-Serial-JTAG peripheral on GPIO19/20 provides debugging
independently. GPIO33, 34, 42 and 48 remain free.

Drop-in replacement for the conflicting block in `firmware/main/include/board_pins.h`:

```c
/* Input option: define CYBER_USE_ANO_ENCODER (default) or the budget encoder. */
#ifndef CYBER_USE_BUDGET_ENCODER
#define CYBER_USE_ANO_ENCODER 1
#endif

#if defined(CYBER_USE_ANO_ENCODER)
#define CYBER_PIN_ANO_INTERRUPT    1   /* RTC-capable */
#define CYBER_PIN_IMU_INTERRUPT    5   /* RTC-capable: tap/motion wake */
#else
#define CYBER_PIN_ENCODER_A        2
#define CYBER_PIN_ENCODER_B       33
#define CYBER_PIN_ENCODER_PUSH    13   /* RTC-capable */
/* No IMU deep-sleep wake in this build: RTC-capable pins are exhausted. */
#endif

#define CYBER_PIN_SNOOZE          18   /* RTC-capable */
#define CYBER_PIN_ALARM_ARM       21   /* RTC-capable */

#define CYBER_PIN_BACKUP_BUZZER   47   /* NOT 38/48: RGB LED on v1.1/v1.0 */
#define CYBER_PIN_GAUGE_ALERT     39   /* poll on wake; not RTC-capable */
#define CYBER_PIN_CHARGER_STATUS  41   /* poll on wake; not RTC-capable */
```

---

## 4. The power model does not describe the prototype

This is not a defect in the numbers — the arithmetic is exact — but the model and the build
plan measure different machines, and Phase 4's gate will read as a failure because of it.

The model's 0.23 / 0.40 / 0.55 W is a bare-module figure. The prototype chain is:

```text
battery -> charger board SYS (4.5 V) -> boost converter (5 V) -> controller board 5 V pin -> controller board LDO -> 3.3 V
```

Two conversions in series: boost ≈ 90%, then a **linear** 5→3.3 V LDO ≈ 66%. Net to 3.3 V
loads ≈ **59%**. The OLED's 165 mW delivered costs about 280 mW at the battery. Add the
[controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894)'s own overhead — USB-serial bridge, RGB LED, LDO quiescent — and realistic prototype
draw is likely **1.5–2.5× the model**.

Adafruit also warn that the [charger board](https://www.adafruit.com/product/6106)'s boost converter *"will stall over 200 mA"* for loads that draw full
current at startup. The controller board plus OLED plus amplifier inrush exceeds that comfortably.

**Decisions:**

1. **Record two budgets, not one** — a production budget (the existing table) and a prototype
   budget carrying the measured conversion and controller-board overhead. Judge the Phase 4 gate against
   the prototype budget; judge the solar claim against the production one. *Rev B: there is no solar claim
   to judge; the prototype budget sets the 16340 cell's runtime, about 10 h with the face lit, more dark.*
2. **Treat the 200 mA boost-startup limit as a firmware requirement, not a caution.** The
   existing boot order in `ARCHITECTURE.md` already sequences loads correctly — it is now
   load-bearing rather than good practice, and should say so.
3. **Add a $0 test to Phase 1** (below) that settles this before any power hardware is bought.

---

## 5. What is still untested, and how to settle it cheaply

Everything above is verified from specifications and arithmetic. These remain genuinely
unknown and need hardware. The first one is free and gates the expensive decisions.

| Assumption | Test | When | Cost |
|---|---|---|---|
| [Controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) idle draw is near the model | USB power meter on the bench rig, eco/balanced/connected for 1 h each | **Phase 1** | **$0** — already own the rig |
| [Rotary encoder](https://www.adafruit.com/product/6310) adapter default is `0x49` | `i2cdetect` on first power-up | Phase 1 | $0 |
| OLED revision is SSD1309 not SSD1305 | Read the controller ID on receipt | Phase 0 | $0 |
| Received controller board is v1.1 | Inspect silkscreen; confirm the RGB LED pin | Phase 0 | $0 |
| Aggregate I2C pull-ups are sane | Measure bus resistance with all six STEMMA boards fitted | Phase 3 | $0 |
| ~~4400 mAh completes charge inside 6 h~~ superseded: the 16340 cell at 500 mA terminates inside 6 h (expected ~3 h) | Full charge from protection cutoff, watch STAT1/STAT2 | Phase 4 | $0 |
| [Amplifier](https://www.adafruit.com/product/3006) peaks stay inside the 1 A boost (Rev B: the cell's 2 A limit is not the constraint; the boost is) | Scope the 5 V rail at max volume + Wi-Fi TX, unplugged on the cell | Phase 4 | scope |
| ~~5 W panel covers measured load~~ superseded 2026-10-31: solar removed | The existing 7-day campaign | — | — |

**Move the controller board idle measurement to Phase 1.** It costs nothing, needs only parts already in
the bench order, and it determines whether the solar story is viable on this hardware at all
(*Rev B: the solar story is closed; the measurement now sets the 16340 cell's runtime*).
If idle lands above ~0.6 W, the honest response is to move the final build to a bare
ESP32-S3 module on a carrier and keep the controller board purely as a development target —
a decision far cheaper to make before $58.45 of battery and panel is on the desk.

---

## 6. Revised purchase totals (superseded: what was actually bought is in `ORDER_SHEET.md`; Rev B 2026-10-31 buys nothing but the acrylic face)

| Stage | Was | Now | Change |
|---|---:|---:|---|
| Core USB bench order | $131.48 | **$131.48** | unchanged |
| + battery-ready | $175.38 | **$170.83** | 6600 mAh → 4400 mAh pack |
| + solar sail | $213.88 | **$209.33** | −$4.55 |

The staging discipline in `BUILD_PLAN.md` is correct and should be followed as written: the
core order is the only one to place now.

---

## 7. Assessment

**Correctness:** high. Every piece of arithmetic checks out exactly, the partition table is
byte-perfect, the strapping-pin and PSRAM constraints are stated correctly, and the alarm
architecture — UTC in the RTC, hardware alarm interrupt, procedural fallback tone compiled
into flash, connectivity deliberately absent from the alarm state machine — is professionally
correct. It caught a real address conflict in the *reference* design that its own author shipped.

**Honesty:** high, and load-bearing rather than decorative. "These are design estimates, not
measurements", "the pin map is proposed, not verified", and "not claimed as compiled" are all
literally true; the last was confirmed on this machine. The refusal to promise indoor solar
autonomy is correct and unusual.

**Where it is weak:** the specific silicon. Every defect found sits in the layer where you must
check a particular board revision, a particular RTC-GPIO range, or a particular datasheet
timing table. The architecture reasoning is stronger than the component reasoning — which is
exactly why the documents' own repeated instruction to verify against the received hardware
is the right instinct.

**Feasibility:** the engineering is achievable. The 22–36 engineer-day estimate is arithmetically
consistent and plausible for someone fluent in ESP-IDF. But the gates are dominated by *calendar*
time — a 72 h soak, 30 RTC wake events, a week-long OLED static test, 7+ days of solar logging,
a multi-week pilot. Evenings and weekends, this is a **3–6 month project**, mostly waiting.

**Difficulty:** this is a substantial step up from `pocket_ai_assistant`, which ported working
vendor firmware onto a new pin map. This asks for a recurrence engine with correct DST handling,
a real-time-clock driver, an OLED driver, BLE provisioning and dual-slot OTA, written from scratch in C.

Phases 0 and 1 alone — a USB-powered clock that wakes on a hardware RTC interrupt and reliably
makes a sound — are a complete, worthwhile project at $131.48 that teaches most of what matters.
Treat Phases 2–7 as optional continuations rather than a commitment made in advance.

---

## 8. Second pass: interconnect, amplifier headroom, and a BOM gap

Added 2026-09-23 after applying the pin map. `board_pins.h` now carries the §3 map and was
machine-checked: no GPIO is assigned twice in either build variant, and no assignment lands on
a strapping, flash, PSRAM, USB, UART or RGB-LED pin.

### 8.1 BOM gap: nothing bridges the controller board to the I2C chain — DECIDED: add a QT-to-header cable

The bench order lists 4 × [QT cables](https://www.adafruit.com/product/4210), which are JST-SH on **both** ends. The
[controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) has **no STEMMA QT connector** — only 0.1" headers. As ordered, there is no
way to get from GPIO8/GPIO9 to the first sensor.

There are also six I2C devices (real-time clock, fuel gauge, proximity and light sensor,
accelerometer, temperature and humidity sensor, rotary encoder), so a daisy
chain needs five board-to-board cables, not four.

**Decision: add 1 × [QT-to-header cable](https://www.adafruit.com/product/4209) ($0.95) and 1 × QT cable ($0.95).**
Wire colours on the QT-to-header cable are red = 3.3 V, black = GND, blue = SDA, yellow = SCL.

Revised core subtotal: **$133.38**. Battery-ready **$172.73**. With solar **$211.23**.

### 8.2 Amplifier peaks exceed the boost rating — DECIDED: set gain to 6 dB

Adafruit specify the [amplifier](https://www.adafruit.com/product/3006) at **3.2 W into 4 Ω at 10% THD from a 5 V supply**.
Working that back to supply current:

```text
Vrms = sqrt(3.2 W x 4 ohm) = 3.58 V  ->  Vpk = 5.06 V  ->  Ipk = 1.26 A into the speaker
class-D at ~88-90% efficiency  ->  supply peak ~1.3-1.4 A, full-sine average ~0.71 A
```

The boost converter on the [charger board](https://www.adafruit.com/product/6106) is rated **5 V / 1 A**. At full volume the amplifier
alone exceeds it, before the ESP32-S3 and OLED are counted.

**Decision: strap the amplifier gain to 6 dB rather than the 9 dB default.** That drops maximum
output to roughly 1.6 W into 4 Ω — about 0.9 A peak, inside the boost rating with the OLED and
radio still fed. A sealed 4 Ω driver at 1.6 W is loud for a bedside alarm. This puts the ceiling
in **hardware**, where a firmware bug cannot raise it.

Keep the 220-470 µF bulk capacitance at the amplifier regardless; it supplies the transient the
boost cannot.

*Rev B, 2026-10-31:* the source behind the boost is one protected 16340 cell with a 2 A continuous
limit, so the amplifier's ~0.9 A peaks at 6 dB are well inside what the cell will deliver; the boost's
1 A rating remains the ceiling and the 6 dB strap stays.

### 8.3 Remaining verifications

| Item | Source | Result |
|---|---|---|
| [Rotary encoder](https://www.adafruit.com/product/6310) adapter default I2C address | Adafruit learn guide | **0x49 confirmed** (jumpers reach 0x58); no conflict |
| [Amplifier](https://www.adafruit.com/product/3006): 2.7-5.5 V, 3.2 W / 4 Ω, gain 3-15 dB | Adafruit | **Confirmed**, $5.95, in stock |
| 4400 mAh [battery](https://www.adafruit.com/product/354) max charge current | Adafruit | **1 A — exact match for the [charger board](https://www.adafruit.com/product/6106) default** |
| [QT-to-header cable](https://www.adafruit.com/product/4209) exists and bridges header to JST-SH | Adafruit | **Confirmed**, $0.95, in stock |

Not verified from a primary source, and still to confirm on receipt: the DigiKey unit price and
stock for the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) (DigiKey blocks automated fetch; the $15.00 figure is
plausible but unconfirmed), and the individual I2C addresses of the proximity, accelerometer,
temperature/humidity and fuel-gauge breakouts, which an `i2cdetect` sweep settles in one minute on first power-up.

### 8.4 Interconnect summary

Four electrically independent groups. Nothing crosses between them except ground.

| Group | Members | Physical bridge | Soldering |
|---|---|---|---|
| I2C chain | 6 breakouts | [QT-to-header cable](https://www.adafruit.com/product/4209) from the controller board's headers, then [QT cables](https://www.adafruit.com/product/4210) board to board | **None** |
| Two interrupt lines | [Real-time clock](https://www.adafruit.com/product/5188) INT/SQW to GPIO4; [rotary encoder](https://www.adafruit.com/product/6310) INT to GPIO1 | Wire from the breakout's own pad, plus a 10 kΩ pull-up to 3V3 on the clock line | 3 joints |
| OLED, 4-wire SPI | 7 conductors: 3V3, GND, SCLK 12, MOSI 11, CS 10, DC 6, RESET 7 | Header strip to the [solder-in proto board](https://www.adafruit.com/product/1609) | ~20 joints |
| Audio | Amp VIN, GND, BCLK 14, LRC 15, DIN 16, SD 17, gain strap; speaker on OUT+/OUT- | Header strip; speaker leads float | ~12 joints |
| Discrete inputs | Snooze to GPIO18, arm to GPIO21, buzzer MOSFET gate to GPIO47 | Two wires each to GND | ~8 joints |

The real-time clock's alarm interrupt is the one connection people miss: it is **not** carried on the
STEMMA QT connector. It must be wired from the breakout's own INT pad, and it is open-drain, so
without an external pull-up to 3.3 V the alarm wake silently never fires.

---

## Rev B verification, 2026-10-31

Paper review of the Rev B wiring and power design (nothing built) against primary sources: Adafruit's product
pages, learn guides and published board schematics, TI's datasheets for the charger chip (SLUSF65B, August 2026)
and the boost converter, the regulator datasheet named by Espressif's v1.1 controller-board schematic, the
ESP32-S3 datasheet and ESP-IDF sleep documentation, the chip datasheets behind the clock, accelerometer,
proximity and fuel-gauge boards, and Nitecore's page for the cell. Verdicts: **OK** (design matches the source),
**fix applied** (design was wrong; generator or document corrected and regenerated), **open** (cannot be settled
on paper; bench item already recorded or added).

**Three things were wrong and are fixed.** The charger's charge-rate jumper ships **closed** (1 A) and must be
**cut** for 500 mA; the sheets said "set". The controller board's regulator is an **800 mA low-dropout part**
with about 0.3 V of dropout, not the 1.1 V-dropout part the September notes assumed, so the brownout threshold
on the 5 V rail is about **3.7 V, not 4.4 V**. And the charger's LED legend and power-up step 2 described the
chip's status pins wrongly. Everything else, every pin, every address, every open-drain claim and the amplifier's
strap and shutdown network, checks out.

| Item | What the design says | What the source says | Verdict | Source |
|---|---|---|---|---|
| 1a Charger input | Its own USB-C through the rear panel; solar pads empty | USB-C 5 V at up to 1 A (5.1 k CC); DC/solar pads 5–18 V used "instead of USB". The board ORs the two inputs through two Schottky diodes, so an empty VIN pad is isolated | OK | [product page](https://www.adafruit.com/product/6106), [guide](https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board), [schematic](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) |
| 1b Charge-rate jumper | "Set the jumper to 500 mA" | The current-set pin has 600 Ω to ground plus a second 600 Ω through a **closed** solder jumper: 300 Ω = 1 A as shipped (I = 300 AΩ / R). **Cutting** the jumper leaves 600 Ω = 500 mA. Product page: "defaults to 1A, cut the jumper for 500mA" | **fix applied**: power sheet, power notes, parts table, order sheet, COMPACT_DESIGN and ARCHITECTURE now say cut, ships closed at 1 A | [schematic](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB), [charger chip datasheet](https://www.ti.com/lit/ds/symlink/bq25185.pdf) §5.5, §6.3.6 |
| 1c Termination 4.2 V | 4.20 V, Li-ion profile unchanged | The board's 13 kΩ VSET resistor selects 4.2 V regulation and a 1100 mA input limit (Table 6-1); regulation accuracy ±0.5 % | OK | [charger chip datasheet](https://www.ti.com/lit/ds/symlink/bq25185.pdf) Table 6-1 |
| 1d Safety timer | Fixed 6 h; 950 mAh at 500 mA done in ~2.5 h; "latches the red LED" | tMAXCHG 360 min typ, fixed in silicon; precharge timer 25 % of it. Expiry is a **non-recoverable** fault: STAT1 **and** STAT2 both low (red and orange together), cleared only by toggling CE or cycling input power. Termination is disabled while input-limit or DPPM regulation is active, so an alarm playing while charging stretches the cycle | **fix applied**: fault text now says red + orange, unplug and replug | [charger chip datasheet](https://www.ti.com/lit/ds/symlink/bq25185.pdf) §5.5, §6.3.7.7, Table 6-2 |
| 1e LED legend, power-up order | "Red F = a cell outside 3.0–4.2 V"; step 2 "orange C may light" with no USB | Red (STAT1 low) means a fault only; a cell below 3.0 V is pre-charged at 20 % of the set current, not faulted. With no input the chip is in battery-only mode: nothing charges, orange stays off, but the boost's enable has a 100 k pull-up so the **green** LED lights from the cell | **fix applied**: sheet labels, LED paragraph and step 2 corrected | [charger chip datasheet](https://www.ti.com/lit/ds/symlink/bq25185.pdf) §6.1.1.2, Table 6-2; [schematic](https://github.com/adafruit/Adafruit-bq25185-with-5V-Boost-PCB) |
| 1f Boost output vs loads | 1 A rating; amp 364 mA avg / 0.9 A peaks at 6 dB; controller ~350 mA Wi-Fi peaks; OLED 50 mA | Boost chip: 1.5 A at 5 V from a Li-ion cell, 3.7 A valley switch limit, 700 µs soft start; Adafruit rates the board 1 A and warns it stalls above ~200 mA at start-up. Budget: 364 + up to 570 (3.3 V loads pass 1:1 through the linear regulator) ≈ 0.93 A worst-case average, inside 1 A. A bass peak on a Wi-Fi burst is ~1.4 A for milliseconds: inside the chip's switch limit, but about 2.3 A from a cell at 3.3 V | OK, with a firmware rule added to ARCHITECTURE (no radio transmit during alarm playback while unplugged); Phase 4 scope test stands | [boost datasheet](https://www.ti.com/lit/ds/symlink/tps61023.pdf) §7.3.2–7.3.4, §8.2; [guide](https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board) |
| 1g Power path with USB present | Load first, surplus charges | DPPM reduces charge current first; if the load still exceeds the 1.1 A input limit, supplement mode lets the battery add to it; SYS regulated at 4.5 V with input present. The adapter never sees more than 1.1 A | OK; "why 2 A" wording corrected (1.5 A adapter suffices, 2 A owned is fine) | [charger chip datasheet](https://www.ti.com/lit/ds/symlink/bq25185.pdf) §5.4, §6.3.2–6.3.5 |
| 1h 200 mA start-up caveat | Firmware sequences loads | The boost is always enabled and starts unloaded; the JST to the controller is plugged last in the power-up order, so the caveat is met by procedure | OK | [guide](https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board) |
| 1i BAT connector | JST-PH, meter polarity | JST-PH 2-pin labelled BATT; "watch polarity unless an Adafruit battery" | OK (meter rule covers it) | [guide](https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board) |
| 2a Cell ratings | 3.6 V, 950 mAh, 3.4 Wh, protected, 2 A continuous | 3.6 V, 950 mAh, 3.42 Wh, max continuous discharge 2 A, NMC, 34.1 ± 0.3 × 16.6 ± 0.2 mm, 20 g; retailer spec: termination 4.20 ± 0.05 V, do not discharge below 2.5 V, protection circuit fitted | OK | [Nitecore](https://www.nitecore.com/product/nl169), [nkon](https://nkon.nl/en/rechargeable/li-ion/14500-16340/nitecore-16340-nl169-950mah-protected-2a.html) |
| 2b Protection trip currents | Not stated | Not published by Nitecore or any retailer found. The charger chip's own battery over-current trip is 3.13 A | open (no action: the 1f firmware rule keeps millisecond peaks near 2.3 A) | as above |
| 2c Cell current at amp peaks | ~0.75 A at 2 W on 5 V from 3.3 V | 0.93 A average at 5 V from a 3.3 V cell is 0.93 × 5 / (0.92 × 3.3) ≈ 1.5 A, inside 2 A | OK | arithmetic |
| 2d 4.2 V compatibility | Charger profile fits | Cell 4.20 V, charger 4.20 V | OK | 1c, 2a |
| 2e Holder fit | 34.1 × 16.6 button-top in a holder sized 34.5 × 17 | Vendor page blocks fetching. The repository's own record logs listing dims 43.2 × 18.3 × 14.2 mm and a spring contact; holders of this class take 32–34.5 mm cells | open: bench check already on the sheet (spring reaches the button; meter polarity) | ../pocket_ai_assistant/cad/FITCHECK_REPORT.md, ../pocket_ai_assistant_with_camera/docs/COMPONENTS.md |
| 3a Gauge inline on the lead | Between holder pigtail and charger BAT | Two JST ports, "equivalent": one for the battery, the other for the load or charger | OK | [gauge guide](https://learn.adafruit.com/adafruit-max17048-lipoly-liion-fuel-gauge-and-battery-monitor/pinouts) |
| 3b Model for a Li-ion 16340 | Acceptable | Chip is for lithium-ion (Li+) cells, powered from the cell (2.5–4.5 V); guide: 1S 3.7–4.2 V Li-ion or LiPo. A 4.2 V NMC 16340 is in scope; a custom model is optional | OK | [gauge chip datasheet](https://cdn-learn.adafruit.com/assets/assets/000/114/607/original/MAX17048-MAX17049.pdf), [guide overview](https://learn.adafruit.com/adafruit-max17048-lipoly-liion-fuel-gauge-and-battery-monitor/overview) |
| 3c Alert to GPIO39 | Open-drain, pull-up on board, polled on wake | ALRT is open-drain, active-low; the board adds a 10 k pull-up to VIN, and VIN is the QT chain's 3.3 V, so 3.3 V logic reaches GPIO39 (MTCK/GPIO39, not RTC-capable) | OK | [gauge chip datasheet](https://cdn-learn.adafruit.com/assets/assets/000/114/607/original/MAX17048-MAX17049.pdf) pin table; [guide](https://learn.adafruit.com/adafruit-max17048-lipoly-liion-fuel-gauge-and-battery-monitor/pinouts); [user guide v1.1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html) |
| 4a 5V pin as input, USB empty | One source at a time | "Three mutually exclusive ways": USB ports (one or both), 5V + GND, 3V3 + GND. Schematic: a Schottky diode in each USB VBUS line into the 5 V rail, so feeding the 5V pin cannot back-drive a socket, and on USB the 5V pin sits ~0.4 V below VBUS | OK | [user guide v1.1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html), [schematic](https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-DevKitC-1_V1.1_20221130.pdf) |
| 4b Regulator dropout, the 4.4 V rule | 1.1–1.3 V dropout, ~1 A part, rail above 4.4 V | The v1.1 schematic's regulator is an 800 mA low-dropout part: 0.24 V typ at 500 mA, 0.45 V max at 800 mA, current limit 810 mA min, thermal shutdown | **fix applied**: rule is now 3.7 V and the rating 800 mA in WIRING_CROSSREF (§1, Finding 2, §2, Finding 4, §3, §6, §7), ARCHITECTURE, the wiring page §5, the power notes §4, the physics page §5 and §9 | [schematic](https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-DevKitC-1_V1.1_20221130.pdf), [regulator](https://sg-micro.com/product/SGM2212) datasheet §Electrical Characteristics |
| 4c Reserved pins | 35–37 PSRAM; strapping 0, 3, 45, 46; RGB 38 (v1.1) / 48 (v1.0); USB 19/20; UART 43/44 | Guide: GPIO35/36/37 used internally by octal-PSRAM modules; RGB LED GPIO38 on v1.1, GPIO48 on v1.0; USB_D− GPIO19, USB_D+ GPIO20; U0TXD GPIO43, U0RXD GPIO44. Datasheet: strapping pins GPIO0, GPIO3, GPIO45, GPIO46 | OK | [user guide v1.1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html), [ESP32-S3 datasheet](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf) §2.3 |
| 4d Every pin in board_pins.h | 8/9, 12/11/10 + 6 + 7, 14/15/16 + 17, 4, 1, 5, 18, 21, 47, 39, 41 | Header table: 1, 4–12, 14–18, 21 are all RTC_GPIOn; 39 = MTCK, 41 = MTDI (JTAG only if JTAG is routed to pins; default is the USB-Serial-JTAG); 47 = SPICLK_P, unused on this module. IO MUX: GPIO10 FSPICS0, 11 FSPID, 12 FSPICLK, 13 FSPIQ, so CS 10 / MOSI 11 / SCLK 12 are the mux pins as claimed | OK, no pin changes | [user guide v1.1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html) header tables, [ESP32-S3 datasheet](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf) IO MUX table |
| 4e Wake pins 4, 5, 18, 21 (and 1) | RTC-capable 0–21 | ext0/ext1 wake accept GPIO0–21. "Internal pullups and pulldowns don't work when RTC peripherals are shut down": keep the RTC peripheral domain on, or use external resistors | OK for GPIO4 (external 10 k). **Fix applied** for snooze/arm: WIRING_CROSSREF §5 and the wiring page §5 now say keep the domain powered or fit 10 k if deep sleep is used (firmware may stay awake per COMPACT_DESIGN) | [ESP-IDF sleep modes](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/sleep_modes.html) |
| 5a I²C addresses | 0x68, 0x49, 0x60, 0x18, 0x38, 0x36 | Clock 0x68 (fixed); encoder 0x49 default, jumpers to 0x58; proximity "single slave address 0x60"; accelerometer 0x18, 0x19 with the SDO jumper; temperature/humidity 0x38, cannot be changed; gauge 0x36 | OK | [RTClib](https://github.com/adafruit/RTClib/blob/master/src/RTC_DS3231.cpp), [encoder guide](https://learn.adafruit.com/adafruit-ano-rotary-navigation-encoder-to-i2c-stemma-qt-adapter/pinouts), [proximity chip datasheet](https://www.vishay.com/docs/84274/vcnl4040.pdf), [accelerometer guide](https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/pinouts), [temperature/humidity guide](https://learn.adafruit.com/adafruit-aht20/pinouts), [gauge guide](https://learn.adafruit.com/adafruit-max17048-lipoly-liion-fuel-gauge-and-battery-monitor/pinouts) |
| 5b Pull-ups, 3 mA / 400 kHz | Six boards × 10 k = 1.67 kΩ, 1.98 mA, 212 ns | 10 k on both lines confirmed for the clock, encoder, accelerometer, temperature/humidity and gauge boards. The proximity board's guide does not state a value (it has its own regulator; any pull-ups go to its 3.3 V). Worst case is six × 10 k as computed; one fewer only lightens the bus | OK | the five guides above, [proximity guide](https://learn.adafruit.com/adafruit-vcnl4040-proximity-sensor/pinouts) |
| 6a Clock INT/SQW on GPIO4 | Open-drain; external 10 k mandatory | "Open drain, you need to attach a pullup to read this signal"; no pull-up on the board; the alarm pulls it low | OK | [clock guide](https://learn.adafruit.com/adafruit-ds3231-precision-rtc-breakout/pinouts) |
| 6b Encoder INT on GPIO1 | Open-drain, internal pull-up | Guide: "pulses low"; the seesaw firmware builds the line either as emulated open-drain (input when idle, output-low when asserted) or push-pull high/low, by a compile flag. Either way the internal pull-up on GPIO1 is right: needed in one case, harmless in the other | OK | [encoder guide](https://learn.adafruit.com/adafruit-ano-rotary-navigation-encoder-to-i2c-stemma-qt-adapter/pinouts), [seesaw firmware](https://github.com/adafruit/seesaw/blob/master/source/AOInterrupt.cpp) |
| 6c Accelerometer INT on GPIO5 | INT to GPIO5, tap wake | The chip's interrupt pins have no open-drain option (push-pull); polarity is the H_LACTIVE bit in CTRL_REG6, default active-high; guide: 3.3 V logic output | OK; note added to the wiring page §2 (no pull-up; wake on a high level, or flip the bit) | [accelerometer chip datasheet](https://cdn-shop.adafruit.com/datasheets/LIS3DH.pdf) §8.13, [accelerometer guide](https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/pinouts) |
| 7a OLED | 3.3 V only; SPI via BS1/BS2; SCLK 12, MOSI 11, CS 10, DC 6, RESET 7; 50 mA | 3.3 V power and 3 V logic; level shifter only for 5 V hosts; ~50 mA on the product page, 50–75 mA in the guide; SSD1309 since Sept 2023. Pins: 3V power, D0 = SPI clock, D1 = SPI data, DC, CS, RESET. SPI = BS1 0 / BS2 0; newer 2.4" style: solder R5 and R3, leave R4 and R2; "may come in SPI mode" | OK (Phase 0 photo check stands; 75 mA worst case still inside §3's regulator margin) | [product](https://www.adafruit.com/product/2719), [pinouts](https://learn.adafruit.com/1-5-and-2-4-monochrome-128x64-oled-display-module/pinouts), [assembly](https://learn.adafruit.com/1-5-and-2-4-monochrome-128x64-oled-display-module/assembly) |
| 7b Amplifier gain strap | GAIN to VIN = 6 dB | 100 k to GND 15 dB; GND 12 dB; floating 9 dB; **VIN 6 dB**; 100 k to VIN 3 dB | OK | [amplifier guide](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts) |
| 7c Amplifier SD network | 1 M pull-up to VIN; 10 k pull-down holds it off; GPIO17 drives it | Chip has a 100 k internal pull-down; the board adds 1 M to VIN. Below 0.16 V shutdown; 0.16–0.77 V (L+R)/2; 0.77–1.4 V right; above 1.4 V left. As shipped ≈ 0.45 V, so the amp is on (averaged) at power-up; with the design's 10 k to ground ≈ 0.05 V, off through reset; GPIO17 at 3.3 V = left channel | OK; firmware note added to the wiring page §4 (mono stream in the left I²S slot) | [amplifier guide](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts) |
| 7d Amplifier supply and output | 5 V; 3.2 W / 4 Ω; bridge-tied | VIN 2.5–5.5 V; 3 W at 10 % THD into 4 Ω at 5 V (2.5 W at 1 %); bridge-tied, neither output to ground; 4 Ω minimum; "supply rated at least 800 mA (650 mA peak)" | OK; the design's 364 mA / 0.9 A at 6 dB are conservative | [amplifier guide](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts) |
| 7e Speaker | 4 Ω 3 W, 70 × 30 × 17 mm, sealed | 4 Ω, 3 W, 30 × 70 × 17 mm, enclosed, 15" lead per speaker with a JST-PH-like plug | OK | [speaker](https://www.adafruit.com/product/1669) |
| 7f The HiLetgo amplifier actually owned | Same chip and pinout | No vendor data; the 10 k pull-down makes the reset state deterministic whatever the clone's pull-up | open: confirm the GAIN and SD pads exist on the bench | ORDER_SHEET.md |
| 8a Controller lying on the speaker | Foam pad, cone down | No datasheet. The driver is enclosed with its magnet at the centre of its back; a static field does not disturb the controller or the accelerometer. The module's PCB antenna end lies over the enclosure's plastic edge, ~35 mm from the magnet; ARCHITECTURE's RSSI test with the cradles fitted covers it | OK; one line added to COMPACT_DESIGN | [speaker](https://www.adafruit.com/product/1669), ARCHITECTURE.md |
| 8b Brass cradles | Isolated from every net | Nothing on any sheet lands on brass; isolation is metered per the meter rule | OK | power sheet check list |
| 8c OLED ribbon to the controller | Module in the 11 mm head zone | The glass's flex is bonded to the module PCB; the header strip solders to that PCB and wires run to the controller. Solder the header pointing rearward into the main zone; the 220 µF sits at the header | OK | [pinouts](https://learn.adafruit.com/1-5-and-2-4-monochrome-128x64-oled-display-module/pinouts) |
| 8d Temperature sensor near the cell | Rear zone, vents, "away from the cell" | Adafruit gives no placement note. The cell at 0.5 A sheds milliwatts; the **charger chip is linear** and sheds (5 − V_BAT) × 0.5 A ≈ 0.4–1 W while charging, and stood in the same 2 × 2 grid | **fix applied**: COMPACT_DESIGN puts the sensor in the far column by the vents, the gauge and accelerometer next to the charger | [charger chip datasheet](https://www.ti.com/lit/ds/symlink/bq25185.pdf) §5.4 (linear, 1.1 A input), COMPACT_DESIGN.md |

Not reachable on 2026-10-31: the holder's Amazon listing (fetch blocked), the clock chip's datasheet at its publisher
(timed out three times; the address is taken from Adafruit's library source and the open-drain claim from Adafruit's
guide), and Nitecore's protection trip values (not published anywhere found).

Files changed by this verification: `docs/pages/gen/power_wiring.py`, `docs/pages/gen/power_physics.py`,
`docs/pages/gen/wiring_outline.py` (regenerated: `docs/pages/cyber-dawn-wiring.html`, `cyber-dawn-power.html`,
`cyber-dawn-power-sheet.html`, `cyber-dawn-power-physics.html`, `docs/ORDER_SHEET.md` and the five print PDFs),
`docs/WIRING_CROSSREF.md`, `docs/ARCHITECTURE.md` (power paragraph, sequencing bullet; the pin table is unchanged),
`docs/COMPACT_DESIGN.md`, `docs/BOM.md` and `docs/BUILD_PLAN.md` (one sentence each: jumper cut, 3.7 V), and this section. `firmware/main/include/board_pins.h` is unchanged: no pin needed moving.
