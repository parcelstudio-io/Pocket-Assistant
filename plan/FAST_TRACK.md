# Fast track — build the desk prototype in six sessions

This is the short, hands-on version of the education program, written for a
software engineer. Every session builds something you can observe within the
hour, and the theory arrives only when the thing on your bench needs it. Total
time is roughly ten to twelve hours across six sessions, against about
thirty-five for the full [15-session plan](DAILY_STUDY_AND_LAB_PLAN.md), which
stays available as the deep track. This track diverges from it in exactly one
declared place: the deep plan forbids buying parts to stay on schedule, while
this track front-loads the small order below for items `INVENTORY.md` already
lists as still needed. Every safety boundary is unchanged, and the deep plan's
no-buy fallbacks still work if you skip the order.

**What you have at the end:** a USB-powered prototype — controller, button,
OLED, and microphone — that boots reproducibly from a cold start, logs button
presses, toggles the display, and shows microphone levels that track your
voice. That is the fastest version of the pocket assistant that current
project decisions allow anyone to build. The battery, the speaker, and the
brass frame are design-gated, not education-gated: reading faster does not
unlock them, so this track does not pretend to. See
[what stays held](#what-stays-held-and-why) at the end.

**How to read a session:** *Build* is the work, and it links into the
[USB prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md) for exact commands;
wiring is summarized inline for the bench, and the quickstart's tables are
authoritative if the two ever differ. *Core ideas* is the theory that
session actually uses — a few minutes each, with a short illustrated note and
a deep lesson linked if you want more. *Done when* is the exit gate. Skip any
reading you don't need; never skip a gate.

## Before session 1: the short shopping list (one item really matters)

`INVENTORY.md` records a **USB-A-to-C data cable** as still needed, and
nothing past session 1's toolchain build works without one. Order it now (the
recorded pick is a [Rankie 3-pack](https://www.amazon.com/dp/B01JRY0VE4); the
Phase 0 cart separately lists two labelled Adafruit #4473 cables for the later
charger era, and any proven data cable serves this USB-only track) or
prove a cable you already own carries data — it must enumerate a serial
device, not just charge. A charge-only cable makes a working board look dead,
which is the most expensive fake bug in this hobby.

Worth adding to the same order, because session 2 consumes them — none of
these blocks session 1:

| To buy | Why | Link |
| --- | --- | --- |
| USB-A-to-C data cable | Gates everything from the first flash on | [Rankie 3-pack — Amazon B01JRY0VE4](https://www.amazon.com/dp/B01JRY0VE4) (recorded pick) |
| 2.54 mm breakaway header strips, 1×40, a couple | Only 22 pins are in the house; the OLED and microphone alone consume 10, leaving no slack or practice stock | No recorded pick — [Amazon search: 2.54mm male breakaway pin header](https://www.amazon.com/s?k=2.54mm+male+breakaway+pin+header+strips) |
| Solder wick | Clearing bridges on module pads; the owned solder sucker is too coarse for them | [JoTownCand 3-pack — Amazon B0DRN688Q5](https://www.amazon.com/JoTownCand-Premium-Desoldering-Residue-Solder/dp/B0DRN688Q5) (recorded in `INVENTORY.md`) |
| Small perfboard | Session 2 warm-up joints; otherwise you practice on wire offcuts | No recorded pick — [Amazon search: perfboard prototype 2.54mm](https://www.amazon.com/s?k=perfboard+prototype+board+2.54mm) |
| Optional: clip-on fan or fume extractor, and a loupe | Session 2's ventilation gate and joint inspection — an open window plus any fan you own, and a phone camera at max zoom, both pass | No recorded pick; buy only if the free substitutes annoy you |

The two search links are suggestions, not purchase provenance — the recorded
picks above them are the only items `INVENTORY.md` actually names.

## Everything else is already on your bench

Every other item the six sessions name is in the purchase record. Links are
the original recorded orders (an assortment link means the kit, not a new
single-part listing); items marked *not recorded* are owned but the exact
order URL wasn't preserved.

| Already owned | Sessions | Recorded purchase link |
| --- | --- | --- |
| ESP32-C3 SuperMini, 10-pack (use 1, spares stay bagged) | 1–6 | [Amazon B0F888JQ91](https://www.amazon.com/dp/B0F888JQ91) |
| X-Tronic 3020-XTS station: iron, tips, silicone mat, helping hands, tip cleaner, solder sucker, tweezers | 2 | Not recorded (X-Tronic order) |
| MAIYUM 63/37 solder, 0.8 mm | 2 | [Amazon B076QF1Y85](https://www.amazon.com/dp/B076QF1Y85) |
| Chip Quik CQ4LF no-clean flux pen | 2 | Not recorded (Adafruit order) |
| Hakko CSP-30-1 wire stripper | 2 | [Amazon B00FZPHMUG](https://www.amazon.com/dp/B00FZPHMUG) |
| BOENFU flush cutters | 2 | Not recorded |
| CBAZY 30 AWG silicone wire (practice offcuts) | 2 | [Amazon B073RDGTPB](https://www.amazon.com/dp/B073RDGTPB) |
| 2.54 mm breakaway headers, the 22 in-house pins | 2 | Not recorded (Amazon order #4) |
| 3M Solus 1000 safety glasses | 2 | [Amazon B016KZ1ZPM](https://www.amazon.com/dp/B016KZ1ZPM) |
| KAIWEETS TRMS multimeter | 2–6 | [Amazon B08BL288LW](https://www.amazon.com/dp/B08BL288LW) |
| Hosyond SSD1306 OLED, 5-pack (use 1 + 1 swap spare) | 2, 4–6 | [Amazon B09T6SJBV5](https://www.amazon.com/dp/B09T6SJBV5) |
| AITRIP INMP441 microphone, 5-pack (use 1) | 2, 5–6 | [Amazon B092HWW4RS](https://www.amazon.com/dp/B092HWW4RS) |
| QTEATAK tactile buttons with caps (use 1 or 2 of 420) | 3–6 | [Amazon B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4) |
| REXQualis breadboards (use the 830-point one) | 3–6 | Not recorded (Amazon order #5) |
| TODOELEC Dupont jumpers, 120-wire kit | 3–6 | Not recorded (Amazon order #4) |
| Computer, phone camera, notebook | 1–6 | General tools; no project purchase |

The amplifier, speaker, lithium packs, charger, bench supply, and all brass
stock are also owned — and deliberately stay in their bags for this entire
track (see [what stays held](#what-stays-held-and-why)).

## Rules that survive the simplification

The deep plan carries pages of boundaries; for USB-only work they reduce to
seven. These are non-negotiable because they protect the parts, the house, and
the later build:

1. Every lithium cell and the charger stay unmated, terminal-protected, and
   off the bench for all six sessions. Nothing here needs them.
2. USB is the only power source. No *other* source ever connects to the
   3.3 V rail — it feeds the OLED and microphone, and nothing feeds it. The
   amplifier and speaker stay in their bags.
3. Unplug USB before every wiring change and before any continuity or
   resistance measurement. Reconnect only after a visual check.
4. Measure voltage only, with the meter leads in COM and the voltage jack.
   Never connect a current-mode meter across the rail, USB, or any supply,
   and after any deliberate current measurement return the red lead to the
   voltage jack immediately.
5. GPIO9 belongs to ROM boot/recovery. The project button is GPIO10.
6. Soldering needs eye protection and real airflow away from your face, and
   only the electronics flux pen — the Harris acid flux never enters the
   room.
7. Keep flux, solvent, glue, hot air, and compressed air away from the
   microphone's acoustic port; contaminating it is permanent.

If a session produces heat, smell, instability, or a reading you cannot
explain, stop and write down what you saw before changing anything.

---

## Session 1 — Flash it and watch it boot (~2 h, mostly waiting)

The software-engineer on-ramp: no wiring, no soldering, no meter. You turn a
$3 board into a device running code you built, and learn the board's power
anatomy while the toolchain downloads.

**Grab from the bench:** one bare SuperMini (label it `A1`; the other nine
stay bagged), the proven data cable, your computer, notebook.

**Build:** follow the quickstart's
[Boot the controller](../docs/PROTOTYPE_QUICKSTART.md#boot-the-controller)
section end to end: `setup.sh`, source `export.sh`, `build.sh`, the source
verifier, then `flash-id`, a dry-run, and the real flash with monitor. The
first `setup.sh` run downloads the pinned ESP-IDF toolchain and can eat most
of the session — start it first and read this session's concepts while it
runs.

**Core ideas (read while the toolchain downloads):**

- Electricity only does work in loops. The USB cable is not "power in" — it
  is 5 V out *and* the return path back. Every wire you add later either
  starts or completes a loop.
  → [Charge, energy, and circuits](concepts/01-charge-energy-and-circuits.md)
- The board's LDO turns USB's 5 V into the 3.3 V rail everything else will
  drink from. `3V3` and `GND` pins are the rail's public API; the peripherals
  you add in sessions 3–5 are its callers.
- Flashing at offset `0x0` replaces the entire image — bootloader, partition
  table, app — like re-imaging a disk, not deploying an artifact. It also
  wipes stored Wi-Fi settings.
  → [From code to boot](concepts/06-from-code-to-boot.md)
- A passing build and a matching SHA-256 prove *bytes*, not hardware. The
  boot log is your first piece of physical evidence; treat everything before
  it as CI passing on a machine you've never seen.

**Done when:** `flash-id` reports an ESP32-C3 with ≥4 MB flash, and the
monitor shows a stable `BENCH DIAGNOSTICS: offline; Wi-Fi/cloud off;
amplifier GPIO5 LOW` loop with no resets. Save the boot log, label the board
record `SOURCE DIAGNOSTICS / MIC GPIO4 / 16 kHz`.

**If stuck:** no serial port → suspect the cable before the board (that's why
you proved it). Boot loop → hold BOOT (GPIO9), tap RESET, release, re-flash.
A board that fails `flash-id` twice gets rejected — you own ten precisely so
you never debug a bad clone.

---

## Session 2 — Solder the headers (~2 h)

The one manual-skill session. The modules ship with loose header strips, and
pins pushed through unsoldered holes are intermittent-contact generators that
will poison every later debugging session. You practice briefly, then make
the roughly 22 joints the prototype needs — 26 if your ordered strips arrived
and the controller gets full rows.

**Grab from the bench:** X-Tronic station with its silicone mat, tip cleaner,
and helping hands; MAIYUM 63/37 solder; Chip Quik flux pen; flush cutters;
Hakko stripper and offcut 30 AWG wire for practice; the 22 header pins; OLED,
microphone, and controller; KAIWEETS meter; safety glasses.

**Not in hand, decide before you start:** ventilation is a gate — write down
the actual arrangement (open window plus a fan pulling fumes away from your
face is acceptable) before the iron heats. If the before-session-1 order
arrived, warm up on that perfboard and keep the wick beside the iron for
bridges. Building from the recorded inventory alone instead: warm up on
stripped wire offcuts
twisted to header scraps, and a bridged joint gets reflowed or its pin
replaced — the coarse solder sucker is the only removal tool in the house.
No magnifier either way: inspect every joint through your phone camera at
max zoom.

**The header budget, explicitly:** 22 pins must cover the OLED (4) and the
microphone (6), leaving 12 for the controller — enough for the used pins
(3V3, GND, GPIO1, 2, 4, 10, 20, 21) plus corners for mechanical support, and
zero practice stock. If you bought strips per the note above, practice on
those instead and give the controller full rows.

**Build:** set the X-Tronic to about 330–350 °C for the 63/37 solder with the
chisel tip; a good header joint takes two to three seconds, and if it needs
longer the fix is a cleaner or bigger tip, not more heat. Make ~10 warm-up
joints on scrap until three in a row look right, then follow
[Prepare reliable headers](../docs/PROTOTYPE_QUICKSTART.md#prepare-reliable-headers):
one module at a time, inspect both sides, then meter continuity pad-to-pin
and isolation pin-to-neighbor for every used pin. Where that quickstart
section detours you to the deep plan's "Day 11 solder practice", this warm-up
already covers it — continue at "Then solder the required header joints".

**Core ideas:**

- Solder is not glue; it's a metallurgical bond that only forms on metal
  above the melting point. Heat the pad *and* pin, feed solder into the
  joint, not onto the iron. A gray, lumpy joint is a cold joint — a future
  intermittent.
  → [Soldering and heat](concepts/11-soldering-and-heat.md)
- The joint is electrical; strain relief is mechanical. Any tug on a wire
  must land on something other than the joint, or the connection's lifetime
  is measured in flexes.
  → [Joints and strain relief](concepts/12-joints-and-strain-relief.md)
- Continuity mode is your unit test: pad-to-pin must beep, pin-to-neighbor
  must not. Run it on every used pin before power ever arrives.

**Done when:** every used pin on all three modules passes both continuity
checks, and your last three inspected joints are shiny, concave, and fully
wetted. Photograph the worst joint too — honest evidence beats pretty
evidence.

---

## Session 3 — One input: the button (~1.5 h)

First wiring, first live measurements, and the core of digital electronics in
one sitting: how a voltage becomes a bit.

**Grab from the bench:** the flashed `A1`, data cable, one breadboard, a few
jumpers, one QTEATAK button (you own 420 — take two), KAIWEETS meter, safety
glasses.

**Build:** follow the button half of
[Add the button and OLED](../docs/PROTOTYPE_QUICKSTART.md#add-the-button-and-oled).
With USB unplugged, use continuity mode to find which button legs are the
actual switched pair (four-leg switches join legs in pairs — pick wrong and
the input reads pressed forever). Wire GPIO10 to one contact, GND to the
other. Reconnect USB and press: each click logs `BUTTON GPIO10: click N`.
While you're powered and stable, take your first two measurements: 3.3 V rail
with the meter, and the GPIO10 voltage pressed versus released.

**Core ideas:**

- A digital input is a voltage comparator: near 3.3 V reads 1, near 0 V
  reads 0, and a disconnected pin reads *noise*. Floating inputs are
  uninitialized variables — the pull-up resistor is the default value.
  → [GPIO and buttons](concepts/07-gpio-and-buttons.md)
- The firmware enables the internal pull-up, so the resting state is 1 and a
  press shorts to GND: active-low. That's why the log fires on the
  *falling* edge, and why the meter shows ~3.3 V released, ~0 V pressed.
- Ohm's law earns its keep here: the pull-up (tens of kΩ) and your pressed
  button form the whole circuit — `I = V/R` says a press wastes microamps.
  You now understand every resistor this project plans to use: they set
  default states, like the internal pull-up you just measured — that one
  simply lives inside the chip.
  → [Voltage, current, resistance, power](concepts/02-voltage-current-resistance-and-power.md)
- Some GPIOs are read *once at boot* to choose the boot mode — environment
  variables sampled at process start. GPIO9 is one; that's why it's
  reserved.

**Done when:** ten presses log ten clicks, reset still works, and your
notebook has the measured rail and both input voltages.

---

## Session 4 — One bus: the OLED (~1.5 h)

Two wires, a whole bus of addressable devices: I2C is closer to networking
than to wiring, which makes it the most software-engineer-friendly hardware
on the board.

**Grab from the bench:** everything from session 3 still wired, plus one
soldered OLED and four jumpers. Keep the second OLED bagged as the swap unit.

**Build:** the OLED half of
[Add the button and OLED](../docs/PROTOTYPE_QUICKSTART.md#add-the-button-and-oled).
Before wiring, read the silkscreen: identical-looking carriers ship both
`GND-VCC-SCL-SDA` and `VCC-GND-SCL-SDA`, and reversed power kills the module.
USB unplugged → wire GND, VCC (3.3 V), SCL to GPIO20, SDA to GPIO21 → visual
check → USB in. The log reports the detected address (`0x3C` or `0x3D`) and
runs `OLED: ALL ON` / `ALL OFF`; each button press toggles the pixel test.

**Core ideas:**

- I2C is a two-wire bus: SDA is data, SCL is the clock, and every device has
  a 7-bit address. Think of it as a tiny network segment — every chip is a
  host with an address on a shared bus, and the ACK is the SYN-ACK: proof
  somebody is listening at that address, not that the application works.
  → [I2C and the OLED](concepts/08-i2c-and-the-oled.md)
- Nobody ever drives the bus high — devices only pull it low or let go, and
  pull-up resistors restore the idle-high state. That's why an unpowered or
  missing device can't fight the bus, and it's the same
  default-state-by-resistor trick as the button.
- An ACK at `0x3C` proves a chip answered; lit pixels prove the display
  initialized. Two different claims, two different tests — keep them apart
  when debugging.

**Done when:** cold USB start brings up the display, the address appears in
the log, and ten button presses toggle the pixels. Then run the negative
test: power off, pull SDA, power on — watch the diagnostic loop survive
without the display. Reconnect.

---

## Session 5 — One stream: the microphone (~1.5 h)

Sound becomes numbers. The INMP441 is a digital microphone: it samples on the
chip and ships bits over I2S, so there is no analog stage for you to get
wrong — only clocks, slots, and one data pin.

**Grab from the bench:** the running button+OLED stack, one soldered INMP441,
six short jumpers.

**Build:** follow [Add the microphone](../docs/PROTOTYPE_QUICKSTART.md#add-the-microphone).
USB unplugged: VDD→3.3 V, GND→GND, L/R→GND (selects the left slot), SCK→GPIO2,
WS→GPIO1, SD→GPIO4. USB in, then watch the once-per-second `MIC24` stats: ten
seconds of quiet, speak at fixed distance, quiet again, repeated a few times.

**Core ideas:**

- Sampling: 16,000 times per second the chip freezes the sound pressure into
  a signed 24-bit number. WS (word select) is the 16 kHz "whose turn"
  clock, BCLK shifts the bits. The math you can predict and (with an
  analyzer) verify: 16,000 samples × 2 slots × 32 bits = **1.024 MHz** bit
  clock.
  → [Sampling and I2S](concepts/09-sampling-and-i2s.md)
- The stream has two time slots per frame: a two-element interleaved array
  clocked out on one wire, left in index 0, right in index 1. Tying L/R low
  is how this mic claims index 0, and the firmware reads index 0.
- RMS is the useful number in the stats: a power-style average that tracks
  perceived loudness while `min`/`max` catch clipping and stuck bits.
  Ambient noise means silence never reads zero — judge *change*, not
  absolute values, because every measurement sits on a noise floor.
  → [Measurement and uncertainty](concepts/05-measurement-and-uncertainty.md)

**Done when:** silence and speech are clearly distinguishable in RMS across
several trials, with no stuck values or read errors. Without a logic
analyzer the 1.024 MHz clock stays unverified — write `timing: INCONCLUSIVE,
data: plausible` and move on; that's an honest, complete result.

---

## Session 6 — Prove it's a system, not a lucky afternoon (~2 h)

Anyone can get hardware working once. This session is the difference between
"it worked when I stopped touching it" and a prototype you trust: a clean
cold-start rebuild, a regression per layer, and one deliberately planted bug.

**Grab from the bench:** everything from session 5, your saved logs and
photos from sessions 1–5, notebook.

**Build:**

1. Unplug everything from the breadboard. Rebuild from the bare board up —
   flash check, button, OLED, microphone — running the diagnostic loop after
   each layer and saving each log. This is the integration-test suite; the
   earlier sessions were unit tests.
2. Plant one fault (swap SDA/SCL, or disconnect the mic's SD line), predict
   the exact symptom before powering — which log line changes, and to what —
   then verify and restore. Debugging hardware
   is hypothesis testing: the best measurement is the one that splits two
   candidate causes.
   → [Debugging as experiments](concepts/15-debugging-as-experiments.md)
3. Write the closing three-list review from the deep plan, shrunk to one
   page: **proven on this article** (boot, button, OLED, mic data — with
   logs), **inconclusive** (I2S timing, anything you couldn't measure),
   **held by design** (everything below).

**Done when:** the full stack reproduces from a cold start twice, the
planted fault behaved as predicted, and the one-page review exists.

## What stays held, and why

Fast is allowed; unsafe is not. Three things are gated by open engineering
questions, not by unread lessons — the gates live in
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md):

- **Battery.** The packs in the house are not approved for this load, no
  fused/guarded fixture exists, and charging has its own release process.
  The cells stay sealed. When that work happens, it starts from the bench
  supply, never from a pocket.
- **Speaker and amplifier.** The hold is architectural, not probe etiquette:
  the amplifier needs a qualified 5 V rail the USB prototype doesn't have,
  shutdown sequencing proven against its real comparator thresholds, and a
  firmware output cap that doesn't exist yet — and its bridge-tied outputs
  mean neither speaker wire is ground, so a careless probe kills it anyway.
  Powered audio waits for the approved fixture
  (→ [Speakers and amplifiers](concepts/10-speakers-and-amplifiers.md),
  [Power integrity](concepts/13-power-integrity.md)).
- **Brass frame and pocket carry.** The frame stays uncut stock (offcut
  practice coupons excepted) until every promotion gate closes and a written
  final-fabrication release is signed — a measured fit design is only the
  first of those gates. The mock-up work lives in the deep plan's Day 14
  (→ [Fit and radio](concepts/14-fit-and-radio.md)).

Optional next step, decision required first: the assistant firmware
(`build.sh --assistant`) sends microphone audio to a third-party backend once
Wi-Fi is provisioned. Read the
[quickstart's closing section](../docs/PROTOTYPE_QUICKSTART.md#what-this-proves-and-what-comes-next)
and the [firmware guide](../firmware/README.md), and make the privacy call
deliberately, in writing — it is a one-command experiment *after* you choose,
not a default.

## Where the rest of the course went

Nothing was deleted; the fast track just stops making it mandatory. If a
session leaves you wanting the real thing:

| Cut from the fast path | It lives in | Do it when |
| --- | --- | --- |
| Bench-supply labs: Ohm's law, KVL/KCL, RC charging, current limiting | Deep plan Days 2–5 | You want measurement fluency, or before any future power-fixture work |
| Instrument technique beyond the meter basics | Deep plan Day 5, [Lesson 05](../edu/fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md) | Before trusting any measurement that gates a safety decision |
| Audio power, BTL, speaker limits | Deep plan Day 10, [Lesson 10](../edu/fundamentals/10-class-d-btl-speakers-and-acoustics.md) | Before the amplifier is ever powered |
| Wire splices, strain relief, controlled rework | Deep plan Day 12, [Lesson 12](../edu/fundamentals/12-soldering-mechanics-insulation-tolerance.md) | Before building any permanent harness |
| Power integrity, decoupling, UVLO | Deep plan Day 13, [Lesson 06](../edu/fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md) | Before any battery-fixture design work |
| RF, antennas, 1:1 fit mock-up | Deep plan Day 14, [Lesson 11](../edu/fundamentals/11-rf-emc-antennas-and-metal-frame.md) | Before committing to enclosure geometry |
| The full evidence discipline (lab records, status labels, prep tables) | The whole [deep plan](DAILY_STUDY_AND_LAB_PLAN.md) | Whenever a result surprises you — that's the signal you've outgrown the fast track for that topic |

The [illustrated concept notes](concepts/README.md) index all fifteen short
explanations; the six sessions above link the ten that carry the build.
