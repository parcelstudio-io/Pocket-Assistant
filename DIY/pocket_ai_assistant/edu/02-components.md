# Why each component was chosen

Every part below survived a datasheet-level verification pass (and an
adversarial re-check) before making the list. "Rejected" rows explain what the
original video or an earlier recommendation used, and why it did not survive.

## ESP32-C3 SuperMini — the brain

**Chosen because** the reference firmware (Xiaozhi v2.4.0, board
`pocket-wall-e-c3`) targets exactly this board: its GPIO map, its native
USB-C for flashing, its 4 MB flash, and its size (~22.5 × 18 mm) drive the
whole layout. A different C3 board would mean new wiring *and* new frame
dimensions.

**What to watch:** buy the plain black SuperMini, not the "Plus/V2" — the
Plus puts a WS2812 LED on GPIO8 and adds a U.FL socket. Screen the board on
arrival: at least 4 MB flash (`esptool flash_id`), one blue user LED, no U.FL.
Some clones ship a flash-less die; our partition map fills all 4 MB. Buy a
spare — you will qualify two and solder the better one.

## Pololu S8V9F3 — the 3.3 V buck-boost regulator

**Chosen because** a 1S Li-ion cell is 4.2 V full and ~3.0 V empty, while
every chip in this build wants a steady 3.3 V. A *buck-boost* can step down
when the cell is full and step up when it is nearly empty, so the rail never
sags. Verified numbers: 1.29 A available at a 3.0 V input against our 0.78 A
worst-case peak (1.66× margin); soft-start, over-current and over-temperature
protection built in; 10.2 × 16.5 mm.

**Rejected:** running the raw cell into the SuperMini's `5V` pin (the video's
approach). The board's little LDO drops ~0.47 V at the ESP32-C3's 335 mA
Wi-Fi transmit peak; with a 3.4 V cell that lands ~2.93 V — below the chip's
3.0 V minimum. That is a random-reset machine.

**What to watch:** no reverse-polarity protection (handled by the switch
below), and the pin labels are on the *underside* — the square pad is GND.

## Nitecore NL169 protected 16340 (950 mAh) — the battery

**Chosen because** it is a documented, *protected* rechargeable cell with a
published 2 A continuous-discharge rating against the design's estimated
~1 A cell-side peak. Nitecore publishes 950 mAh, 3.6 V and a
16.6 ±0.2 × 34.1 ±0.3 mm envelope. The protection circuit guards against
overcharge, over-discharge and shorts.

**Rejected:**
- The video's cell: a "14250 1200 mAh" whose marking matches *primary*
  (non-rechargeable) lithium chemistry. Charging one is a fire, full stop.
- PKCELL 300 mAh 14250 (real rechargeable): its ~450 mA continuous rating is
  below our peaks.
- USB-port 16340 variants: typically longer and not guaranteed to fit this holder.

**What to watch:** do not promise runtime from the label; use 750 mAh as a
conservative planning derating until the received cell is capacity-tested. The
protected cell measures roughly 17 × 34.4 mm at maximum tolerance — bigger than the video's 14250,
which is one reason the corrected frame grows. It lives in a **polarity-marked
CR123A holder** (MPD BH123A class) behind a guard — never soldered, never
wrapped in vinyl, always removable by hand. Do not assume the holder is
mechanically keyed; the Pololu switch's reverse-voltage protection is still
required and polarity is checked before insertion.

## Pololu #2810 MOSFET slide switch — the power switch

**Chosen because** the switch must carry the estimated ~1 A peak and break the
battery feed with low loss. The #2810 is rated up to 3 A under its stated
conditions, includes reverse-voltage protection, and switches the battery line
itself. Pololu explicitly says it is not intended as an emergency or safety
cutoff; removing the cell is the hard disconnect.

**Rejected:** the tiny SS12F44 in the battery line (0.5 A rating vs ~1 A
load), and the "put the switch on the regulator's EN pin" plan — EN is
*enabled by default*, so a broken switch wire would leave the pager
permanently on, and the cell would stay hard-wired to everything even when
"off." (The SS12F44 is still fine as the *gate* control of a P-FET load
switch if you prefer its look.)

## PTC resettable fuse, 1.5 A hold / 3.9 A trip

**Chosen because** it is the only protection element in the battery path
whose trip threshold we can actually name and cite. The cell's internal
protection is real but its threshold is unpublished and it is slow. A PTC in
the positive lead turns a wiring fault from "tens of watts until something
gives" into a self-resetting inconvenience. Costs about a dollar.

## Adafruit #326 — the white OLED

**Chosen because** it is a *confirmed white* SSD1306 128 × 64 panel from a
vendor that publishes its schematic, ships I2C-ready with two STEMMA QT
connectors (the display can be connected with **zero soldering**), and has
four M2.5 mounting holes — the most fragile module in the build gets a
mechanical mount instead of glue.

**Rejected:** the earlier Amazon listing was the yellow/blue variant.
Generic white 4-pin modules are workable spares, but vendors silently swap
SH1106 controllers (which this firmware cannot drive) and pin order varies.

**What to watch:** Adafruit's 128 × 64 boards answer at I2C address **0x3D**
by default; generic modules use 0x3C. The firmware now probes both, so either
works unmodified. Details in [05-display-and-pins.md](05-display-and-pins.md).

## DFRobot DFR0954 — the MAX98357A amplifier

**Chosen because** the MAX98357A is the amp the firmware expects (plain I2S
in, 3.1 W-class bridge out), and DFRobot publishes the schematic — which
generic no-name boards do not. It runs happily at 3.3 V, has built-in click
suppression, short-circuit and thermal protection, and is ~18 × 18 mm.

**What to watch:** jumper its `SD` pad to VCC to force **left-channel** mode;
the board's default divider can land in "right channel" territory on a 3.3 V
rail, and the right slot in this firmware is silence. One insulated jumper
removes the whole ambiguity ([04-audio.md](04-audio.md)).

## Same Sky CMS-15113-078L100-67 — the speaker

**Chosen because** it is a documented 8 Ω / 0.7 W, 15 × 11 mm micro speaker
whose ratings match the amplifier's ~0.68 W ceiling at 3.3 V almost exactly,
and the **L100** variant brings 100 mm factory wire leads — no soldering on
the speaker itself.

**Rejected:** the video's undocumented phone-replacement speaker (no
impedance, no power rating), 4 Ω parts (double the current for no benefit
here), and the solder-pad "SP" variant of this same speaker (its pads allow
380 °C for 3 seconds — an avoidable risk).

**What to watch:** its own datasheet marks **"Enclosure: Required."** In free
air the front and back waves cancel and it is nearly inaudible at voice
frequencies. It needs a ~1 cc sealed back volume: Same Sky's BOX-1511-1CC, or
a 3D-printed cup.

## INMP441 — the microphone

**Chosen because** the firmware's audio front end is built around this exact
I2S MEMS mic: 3.3 V, digital output, and its L/R pin grounded selects the
left slot the firmware reads. Nothing to calibrate.

**What to watch:** it is the most heat- and contamination-sensitive part in
the build. Keep the port tape on until final test; no flux, IPA, hot air, or
compressed air near the port; solder only at the header pads. Its data pin
now lands on **GPIO4** (not GPIO8 — see
[05-display-and-pins.md](05-display-and-pins.md)).

## External 16340 charger — instead of a built-in charging board

**Chosen because** the v1 frame charges nothing: you pop the cell out of its
holder and charge it in a proper bench charger (XTAR/Nitecore class) with its
own termination, timer, and thermal handling.

**Rejected:** the creator's 1 A USB-C charger module (1 A into a small cell,
no documentation), and building the Adafruit #4410 into the frame — its
charging IC requires >7 MΩ on the battery node for correct battery detection,
which a permanently-attached regulator violates, and it has no safety timer.
A charger inside the sculpture can come back in v2 with a proper power-path
design; it is not worth the risk to get v1 working.

## The frame stock — brass tube + structural wire

1.5 mm OD K&S brass tube (two 300 mm lengths, as the project page says), plus
1 mm structural wire. Brass soft-solders well and takes primer + satin white
enamel beautifully. For the **silver** look without paint, nickel-silver
(German silver) rod solders almost identically and stays silver bare — see
the finish guide in [docs/BUILD_GUIDE.md](../docs/BUILD_GUIDE.md).

## The small stuff that makes it work

| Part | Job |
| --- | --- |
| 10 kΩ × 3 | Pull-ups on GPIO2 and GPIO8 (boot strapping) and GPIO10 (button) |
| 100 kΩ | INMP441 data-line pull-down (fitted at GPIO4) |
| 10 µF × 3, 100 nF × 4 | Local decoupling at regulator input, ESP32 3V3 entry, and amp supply; button filtering |
| 220 µF polymer | Bulk reservoir for amplifier bass transients (polymer, not a vented electrolytic can) |
| Ferrite bead | Keeps regulator switching noise out of the amp |
| Tact switch | The GPIO10 action button — the firmware's only manual input (chat toggle, long-press Wi-Fi reset) |
| FR4/polycarbonate scraps, M2.5 nylon standoffs | Sub-plates: modules mount to plates, plates mount to frame — nothing solders to painted brass |
| Kapton + fish paper | Actual insulation (paint is decoration, not insulation) |

There is deliberately no GPIO0 battery divider in Rev A. The current board
port does not instantiate an ADC battery monitor or report a calibrated
battery level, so the divider would consume parts without implementing a
warning and could create an off-state current path. Add it only with a later,
reviewed firmware and power-path change.
