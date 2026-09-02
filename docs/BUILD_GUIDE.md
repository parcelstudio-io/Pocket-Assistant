# Step-by-step build guide — white/silver pager edition

> **REV A LOCKED — 2026-09-02.** Materials and procedure are frozen against
> [MATERIALS.md](MATERIALS.md) (same stamp). Scope: **Wi-Fi + BLE only** — no
> cellular, ever, on this device (a phone hotspot covers on-the-go use;
> standalone LTE is the Mochi Pager's lane). Changes after this stamp require
> re-running `tools/netcheck.py` and `cad/fitcheck.py` and re-stamping both files.

This guide follows the sequence of the reference video
([*\[Satisfying\] Building a Tiny Pocket AI Assistant*](https://www.youtube.com/watch?v=25RGnr407PM),
8:19, no narration — instruction is on-screen caption cards) so you can watch
each phase and then do the corrected version of it. Timestamps are ±5 s
(taken from the video's storyboard frames). Where this guide differs from the
video it says so explicitly and links the reasoning in [edu/](../edu/README.md).

**Firmware note before anything else:** this guide wires for the repository's
**corrected source build** (microphone data on **GPIO4**, 16 kHz audio,
display probed at 0x3C/0x3D). If you instead flash the creator's published
image the way the video does at 5:20, you must wire the microphone's SD to
**GPIO8** and use a 0x3C display — the vendor image knows nothing about the
corrections. Don't mix the two.

---

## Materials

The complete Amazon-first material list — every ASIN, price, spec check and
arrival test — is **[MATERIALS.md](MATERIALS.md)**. Everything electrical is on
Amazon except the cell (Nitecore NL169, B&H Manhattan). Reverse-polarity
protection is IN Rev A: a dedicated always-on P-FET in the battery spine. Read
**[the power-chain lesson](../edu/07-the-power-chain.md)** before ordering the
converter and fuse; those two choices are the ones with a wrong answer that
looks right.

---

## Phase 0 — before ordering brass: prove the electronics (not in the video)

The video starts at the template. Don't. Two facts justify a bench detour:
this firmware has **never run on physical hardware**, and the assistant is
useless if its cloud backend isn't acceptable to you.

1. **Build or obtain the firmware.** `cd firmware && ./scripts/prepare.sh &&
   ./scripts/build.sh` (pinned ESP-IDF v6.0.2). The corrected build in this
   repository compiles clean and reproducibly (two clean builds, identical
   images — see [source-build.json](../firmware/source-build.json)).
2. **Qualify the boards.** `esptool flash_id` → 4 MB minimum. Plain SuperMini
   only (one blue LED, no U.FL socket — the "Plus" has a WS2812 on GPIO8 and
   cannot use this pin map).
3. **Flash a bare SuperMini and test the backend.** Provision Wi-Fi, pair at
   xiaozhi.me (video 6:00 shows this flow), confirm one full voice round
   trip. The default backend is `api.tenclass.net` — a third-party service
   that receives your microphone audio. Decide *now* whether that's
   acceptable; self-hosting a Xiaozhi-compatible server and changing
   `CONFIG_OTA_URL` is the alternative.
4. **Breadboard the full stack** — display (I2C scan: 0x3C generic / 0x3D
   Adafruit — the corrected firmware accepts both), mic records, amp plays.
   Meter the amp clone's `SD` pin: ~0.30 V stock (mix mode — fine) or ~3.3 V with the insurance jumper; **~0 V means shutdown** — rework.
5. **The chain test** — the one measurement the whole power design hangs on.
   Assemble the *real* chain on the bench: current-limited supply standing in
   for the cell → PTC pair → reverse-block P-FET → load-switch P-FET (slide
   switch grounding its gate) → converter → service jumper → a 0.8 A dummy
   load on the 3.3 V rail. Pass marks:
   - converter 3V3 jumper pad verified bridged; Vout = 3.30 ± 0.05 V no-load;
   - external-chain drop (supply terminal → converter VIN) **≤ 250 mV at
     1.0 A** — if higher, the offender is usually the holder's crimped lead;
   - rail holds 3.3 V through a 4.2 → 3.0 V source sweep at 0.8 A;
   - **cold-start 10/10**: power-cycle at a 3.0 V source and the rail must
     come up every time (this settles the module's 2.0-vs-2.8 V startup
     listing conflict — a failure here means swap to the XL63020 backup);
   - slide switch toggled 20× with all caps fitted — clean rail every time;
   - with the cell later in hand: measure its DC internal resistance
     (≤ 0.20 Ω) and repeat the cold-start once from the real cell.
6. **Acoustic acceptance test:** the pre-boxed speaker vs the open fallback
   at 0.5 m and 1 m; wake word ("Hi, ESP") at 1 m and 2 m. If it fails on
   the bench, no amount of soldering fixes it — change speaker or plan here.
7. Run `python3 tools/netcheck.py` — 22 wiring rules must pass before you
   commit the layout.

## Phase 1 — template *(video 0:50–1:10)*

The video: modules measured with a steel ruler, outline drawn on paper with
a machinist square (his marks: ~40 mm × ~15 mm). **Copy the method, not the
numbers.** The corrected build is bigger — protected 16340 + holder, the
regulator, the switch board, and the speaker box need roughly
**60 × 45 × 33 mm** for the cage, plus an approximately 22 mm radio-board
projection (about 83 mm overall before an antenna guard in the current
provisional layout). The
received SuperMini's actual antenna region must have at least 15 mm clearance
from frame, wiring, and components in all directions.

Lay the *actual parts* on cardstock: OLED face front; cell + holder low and
at the antenna-opposite end; regulator + star-point plate central; the
SuperMini USB-C port, BOOT, switch, mic hole, and cell-removal path reachable.
Draw every wire route. The cell leaves the device for charging. Nothing gets
cut until the cardstock version closes.

## Phase 2 — bend and solder the frame rectangles *(video 1:10–1:30)*

As the video does: bend 1.5 mm brass tube over the template with round-nose
pliers, two matching rectangles. Cut with a jeweler's saw or rotary tube
cutter — never flush cutters, which crush the 0.225 mm wall. Deburr and dome
every cut end.

Solder with the corrected process: Harris SCLF4 zinc-chloride brass flux
(the Order Sheet's brass flux — rosin is marginal on brass; this acid-class
flux exists ONLY at this empty-frame stage and is fully washed off before any
electronic part exists), 2–3 mm chisel tip at 370–400 °C, joints abraded and
fluxed immediately before heating. Corner posts and braces are cut from the
#9861 1.0 mm rod; the rectangles from the #9831 tube. **The frame is completed, washed
(hot water + baking-soda rinse + IPA), and painted before any electronic
part exists near it.**

## Phase 3 — complete the cage; do NOT glue the OLED yet *(video 1:30–2:05)*

The video glues the OLED into the front rectangle at 1:30, then solders the
four corner posts around it. **Invert that order**: solder all four corner
posts first, finish *all* hot work, then paint, then mount the display.
Gluing glass-bearing modules into a frame you're still soldering is how
displays die.

Paint now (the one painted assembly): degrease → scuff with 400–600 grit →
Rust-Oleum self-etching primer 249322 → gray sandable primer 2081830 (kills
the green etch coat) → 2 thin coats Rust-Oleum satin white 7791830. Handle after ~9 h; it keeps hardening for ~5–7 days. Mask the test
coupon and any tube end that seats into a joint; Rev A has no electrical
frame bond. Skip
chrome-effect paints entirely — they're aluminum flake: patchily conductive,
RF-lossy near the antenna, and not actually insulating.

## Phase 4 — sub-plates and the power spine *(video has no equivalent)*

The video free-forms everything and uses the frame as the ground bus
(4:20: "I'll connect all the ground connections directly to the brass
frame"). **This build never passes current through the frame.** Instead:

1. Epoxy small white polycarbonate/FR4 sub-plates across frame members
   (masked patches → adhesive meets primer, not paint).
2. Mount on the plates: the converter + a 5 × 8 mm star-point bus (one
   3.3 V bus, one GND bus — the converter's pads cannot take four loads'
   wires each), the amp, the holder in its cradle, the slide switch through
   the top face, the two P-FETs on their SOT-23→DIP adapters, the PTC pair
   on the solder tag by the holder, and the **service jumper** header in the
   converter's VOUT lead where it stays reachable (CAD position verified).
   **Line the cell bay first**: fish paper under and around the holder — it
   is the flame-rated layer between the cell and everything else.
3. Battery spine, in order:
   `holder + → PTC pair (2× RUEF110, resistance-matched) → reverse-block
   P-FET (drain to battery side, source downstream, gate to cell −, always
   on) → load-switch P-FET (source upstream, drain to converter VIN, 100 kΩ
   gate-to-source pull-up = off; slide switch grounds the gate through
   10 kΩ = on)`. The slide switch carries only gate current and fails open =
   pager off. Junctions live on the solder tag, sleeved. Converter VOUT →
   service jumper → 3.3 V star bus → four loads; GND bus collects every
   return. 26–28 AWG for the spine, 30 AWG for signals.
4. Caps: 10–22 µF X5R across the regulator's own VIN/GND pads; 10 µF at the
   ESP32's 3V3 entry; ferrite bead + 10 µF ceramic + 220 µF bulk from the
   ALLECIN kit at the amp (the ceramic handles the class-D edges; the bulk
   can is the bass reservoir). Kapton over the converter's jumper field and
   the cell-facing surfaces; slip the finished harness into the white PET
   loom; any board that gets screws instead of epoxy uses the M2.5 nylon
   standoffs.

## Phase 5 — wire the modules *(video 2:10–3:35, changed)*

The video piggybacks the amp on the ESP32-C3 with five stiff 1 mm jumpers
and stacks the mic on shared clocks. Keep the *architecture* (shared
BCLK/WS, separate data), change the details:

| Signal | ESP32-C3 | Video | Corrected |
| --- | ---: | --- | --- |
| OLED SDA / SCL | 21 / 20 | same | same — via its 4-pin header — read the silkscreen pin order first (GND/VCC order varies by vendor) |
| I2S WS (mic + amp) | 1 | same | same — **two separate stubs**, never daisy-chained (a broken WS with BCLK alive = DC into the speaker) |
| I2S BCLK (mic + amp) | 2 | same | same + 10 kΩ pull-up to 3.3 V (strap pin) |
| Amp DIN | 3 | same | same |
| Mic SD | **4** | GPIO8 | moved to **GPIO4** + 100 kΩ pull-down; GPIO8 gets a 10 kΩ pull-up instead |
| Action button | — | absent | GPIO10 → white tact switch → GND, 10 kΩ pull-up + 100 nF |
| Battery sense | — | absent | **Not fitted in Rev A**; current source has no ADC battery monitor |

Amp specifics: the clone's stock SD ≈ 0.30 V mix mode plays at **full
amplitude** (the ESP32-C3 duplicates the mono slot — see the correction in
[edu/04-audio.md](../edu/04-audio.md)); the optional `SD` → VCC jumper only
insures against a board shipped with no SD resistor (0 V = shutdown = silent).
GAIN stays floating (9 dB). Mic: `L/R` → GND.
Speaker: leads to the amp's SPK terminals, twisted pair, **neither lead
ever grounded or touching the frame**. The primary speaker ships pre-boxed;
if the open fallback won the Phase 0 A/B instead, its trimmed vinyl cap must
be rim-sealed against a small baffle plate before this phase.

Mic handling: port tape stays on until final test; solder only at the header
pads; no flux/IPA/hot-air/compressed air near the port; all heat-shrink work
happens *before* the mic joins the assembly.

## Phase 6 — the switch *(video 4:25–4:35, changed)*

Video: a slide switch soldered to the frame, switching the raw cell into the
`5V` pin. Corrected: the same *style* of slide switch survives, but it never
touches the load current — it grounds the load-switch P-FET's gate (Phase 4
spine). That gives three things the video's wiring lacks: a true break in the
battery-positive line, reverse-battery protection from the second P-FET, and
a switch that **fails open = pager off**. It is an operational switch, not a
certified safety cutoff; removing the cell is the hard disconnect. Cap the
slider with a dab of white epoxy or enamel on the bare actuator (a printed
knob is a nice-to-have, not a dependency); keep paint out of the mechanism.

## Phase 7 — battery *(video 4:35–5:05 — DO NOT copy this phase)*

The video strips the cell's wrapper and solders its can to the frame. That
sequence is the reason this guide exists. Corrected: the protected 16340
clicks into its polarity-marked guarded holder, cell untouched, wrapper intact, removable by
hand. White comes from a cradle folded from the white PC sheet and epoxied
*around the holder* (or an optional print-service PETG cradle) — never
from wrapping the cell. The cell is **out of the holder** for every
soldering, painting, cleaning, or flashing operation, and out when the
unfinished/unguarded pager is transported. Only an accepted, fully guarded
build may operate with the cell installed.

## Phase 8 — charging *(video 5:05–5:20, deleted from the frame)*

The video wires a Type-C module permanently to the cell. Corrected: there is
no charger in the frame. Pop the cell into the externally verified charger,
use its 0.5 A mode, and charge attended on a non-flammable surface. Confirm
the exact charger's manual lists protected 3.6/3.7 V 16340 cells and verify
termination voltage before relying on it; similar XTAR model names have been
used for multiple hardware variants.

## Phase 9 — flash and configure *(video 5:20–6:35, same idea)*

The video flashes at web.esphome.io and pairs at xiaozhi.me. Do both during
Phase 0 with the bare SuperMini disconnected from the external rail and
peripherals. **Assembled-unit flashing rule: cell out of the holder AND the
service jumper pulled** — the jumper is the reviewed power-isolation design:
it opens the converter's output lead, so USB 3.3 V feeds only the SuperMini
and the (3.3 V-tolerant) peripherals, never the converter. Verify once with a
meter: jumper out → converter VOUT to the 3.3 V bus reads open. Then use
`./scripts/flash.sh` (or the video's web flasher only for vendor wiring), the
Wi-Fi captive portal, and xiaozhi.me pairing as shown at 5:40–6:35.

**The source build is finalized for English:** wake word **"Hi, ESP"**
(`wn9s_hiesp` — say the letters), en-US display strings, spoken prompts and
activation digits. On first boot the device shows and *reads aloud* a 6-digit
code in English; enter it at xiaozhi.me and set the agent's language and voice
to English there too. (The vendor image instead answers to Mandarin
"ni hao xiao zhi" and boots in Chinese.)

## Phase 10 — bring-up gates (not in the video; do them all)

With a meter and a current-limited bench supply:

1. Cell out: every frame member ↔ BAT+, GND, 3.3 V, each signal, and both
   speaker leads open/high resistance. Rev A has no deliberate frame bond.
2. Bench supply at holder contacts, 4.2 V, 200 mA limit → regulator output
   3.17–3.43 V, sane idle current. Raise to 1.2 A → boot, display, mic, amp.
3. Toggle the switch 20× — clean rail every time (bulk caps fitted).
4. Rail at the ESP32's pin ≥3.0 V during a Wi-Fi burst; ten minutes of loud
   audio + Wi-Fi → regulator warm is fine, cell surface <40 °C always.
5. Wi-Fi in final geometry, cell installed, **before paint touch-ups**:
   compare RSSI/reconnections against the same board in open air at fixed
   distance/orientation; investigate any material degradation.
6. Only now does the cell live in the pager. First charges attended.

Full Rev A acceptance list: [edu/06_ACCEPTANCE_TESTS.md](../edu/06_ACCEPTANCE_TESTS.md).

---

## What you'll have

A ~60 × 45 × 33 mm white/silver cage pager: white-painted tube frame with
painted brass braces (nickel-silver is unobtainable fast; a Rev B upgrade), black OLED face with white pixels, white wiring
loom, silver holder clip — intended to run the corrected 16 kHz firmware.
Runtime is an unverified planning estimate (roughly 5–6 hours only if the
assumed average load and usable cell capacity prove true), with half-duplex
conversation (no barge-in on this chip),
speech processed by the configured cloud backend over **Wi-Fi only** (a
phone hotspot covers the street; cellular is deliberately out of scope).
Not a replica of the video's raw-brass sculpture — a safer, slightly larger
sibling that still reads unmistakably as the same object.
