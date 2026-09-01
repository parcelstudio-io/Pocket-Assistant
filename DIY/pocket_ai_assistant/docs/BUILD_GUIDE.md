# Step-by-step build guide — white/silver pager edition

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

## The corrected shopping list

Prices and stock checked 2026-09-01. The fixed shopping rows total roughly
**$130 before tax/shipping**; materials, test equipment, paint, flux,
adhesives, fabrication, and printing can take the real total well above $190.
NYC-specific sources and
the one-week plan live in [NYC_SOURCING.md](NYC_SOURCING.md); the physical
layout source is in [cad/fitcheck.py](../cad/fitcheck.py). Its earlier 93/93
generated result was invalidated by the final holder/capacitor/antenna audit;
read [the CAD status](../cad/README.md) and rerun it with measured parts before
cutting metal.

| # | Part | Source | Price | Color role |
| --- | --- | --- | --- | --- |
| 1 | ESP32-C3 SuperMini, plain (3-pack — you'll qualify two) | [Amazon B0G5XS345R](https://www.amazon.com/dp/B0G5XS345R) | $11.99/3 | black (hidden) |
| 2 | Pololu S8V9F3 3.3 V buck-boost regulator | [Pololu 4964](https://www.pololu.com/product/4964) | $9.95 | hidden |
| 3 | Pololu Mini MOSFET slide switch LV (reverse protection) | [Pololu 2810](https://www.pololu.com/product/2810) | $4.49 | white printed knob cap |
| 4 | **Nitecore NL169** protected 16340, 950 mAh, 2 A continuous, 34.1×16.6 mm | [B&H Photo](https://www.bhphotovideo.com/c/product/1811930-REG/nitecore_nl169_16340_li_ion_rechargeable.html) — listing showed in stock; confirm pickup before travel | $9.95 | untouched (in white cradle) |
| 5 | MPD BH123A CR123A holder (polarity-mark and guard it; do not assume mechanical keying) | [DigiKey](https://www.digikey.com/en/products/detail/mpd-memory-protection-devices/BH123A/2817712) | $1.25 | black, inside white cradle |
| 6 | PTC fuse 1.5 A hold — Littelfuse 1206L150SLYR | [DigiKey](https://www.digikey.com/en/products/detail/littelfuse-inc/1206L150SLYR/2082148) | $2.26 | hidden |
| 7 | Adafruit #326 white 0.96" SSD1306 OLED (STEMMA QT) | [Adafruit 326](https://www.adafruit.com/product/326) | $17.50 | **the face**: white pixels, black bezel |
| 8 | DFRobot DFR0954 MAX98357A amp | [DFRobot](https://www.dfrobot.com/product-2614.html) / [DigiKey](https://www.digikey.com/en/products/detail/dfrobot/DFR0954/18069273) | $4.90/$5.25 checked | black (hidden) |
| 9 | Same Sky CMS-15113-078**L100**-67 speaker (wire leads) | [DigiKey](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMS-15113-078L100-67/9561150) | $3.10 | black behind grille |
| 10 | Same Sky BOX-1511-1CC 1 cc prototyping enclosure plus its specified foam/seal materials *(or a validated white PETG cup)* | [Mouser](https://www.mouser.com/ProductDetail/Same-Sky/BOX-1511-1CC) | $1.99 checked | white if printed |
| 11 | INMP441 microphone (3-pack; pick a black-PCB listing) | [Amazon B0972XP1YS](https://www.amazon.com/AITRIPAITRIP-AITRIP-Omnidirectional-Microphone-Interface/dp/B0972XP1YS) | $9.99/3 | black (hidden) |
| 12 | XTAR ANT MC1 Plus USB-C, exact official variant; confirm automatic 0.5 A selection with the received manual/indicator | [XTAR](https://www.xtar.cc/product/xtar-ant-mc1-plus-charger-7.html) | $9.49 checked | lives off-device |
| 13 | K&S brass tube 1.5 mm OD (4-pack) | [K&S BR225MM-1H](https://ksmetals.com/products/br225mm-1h) | $7.99 | painted satin white |
| 14 | Structural wire 1.0 mm — **Albion Alloys nickel-silver rod NSR10** for silver-with-no-paint (K&S brass rod as fallback) | [Flex-I-File](https://flex-i-file.com/products/nickel-silver-rod) (sold out 2026-09-01; [UK](https://www.scalemodelshop.co.uk/nickel-silver-rod/)/eBay carry it) / [K&S](https://ksmetals.com/products/brrmet-1) | $5.99 | **bare silver** |
| 15 | White tact switch (GPIO10 action button) | [ProtoSupplies](https://protosupplies.com/product/tactile-momentary-pushbutton-white-6mm/) | $0.69/5 | white cap |
| 16 | 30 AWG white PTFE signal wire (silver-plated conductors) | [Remington Industries](https://www.remingtonindustries.com/hook-up-wire/hook-up-wire-30-awg-ptfe-stranded-10-colors-7-sizes-available/) | $18.80 | white |
| 17 | Passives basket: 10 kΩ ×3, 100 kΩ, 100 nF ×4, 10 µF X5R ×3, Panasonic **6SVPC220M** 220 µF/6.3 V polymer, Murata **BLM21PG221SN1D** ferrite bead | DigiKey (same cart as 5–10); buy spares and suitable SMD adapter/protoboard | ~$8–12 | hidden |
| 18 | STEMMA QT JST-SH-to-male-header cable; shorten/terminate at the SuperMini after bench test | [Adafruit 4209](https://www.adafruit.com/product/4209) | $0.95 checked | mostly black/hidden |
| 19 | White polycarbonate sheet 0.5–1 mm (sub-plates, cell cradle), M2.5 white nylon standoffs, white PET braid loom, white 2:1 heat-shrink, Kapton + fish paper, 26–28 AWG power wire | McMaster / Amazon | ~$35–50 | white |

Ordering order and NYC pickup/delivery options for every line (B&H same-day
cells, Micro Center Brooklyn emergency substitutes, Home Depot paint pickup,
Makelab PETG printing in Industry City): see [NYC_SOURCING.md](NYC_SOURCING.md).
Recheck each cart immediately before payment; marketplace sellers, stock, and
delivery dates are not part specifications. The 3-packs bank your qualification
spares automatically.

*Deliberately black (the secondary color):* OLED bezel, both PCBs, speaker,
holder. *Deliberately silver:* nickel-silver rods, holder clip, polymer-cap
cans, silver-plated wire ends. *White:* painted tube frame, PTFE wiring,
loom, standoffs, sub-plates, printed parts, tact cap. Don't chase a
white-PCB SuperMini or mic — none exist; "white SSD1306" listings mean white
*pixels*.

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
   Meter the DFR0954's `SD` pin: ~3.3 V after you fit its jumper (step 5.4).
5. **Acoustic acceptance test:** speaker with and without the 1 cc box at
   0.5 m and 1 m; wake word at 1 m and 2 m. If it fails on the bench, no
   amount of soldering fixes it — this is where you'd change speaker or plan.
6. Run `python3 tools/netcheck.py` — 18 wiring rules must pass before you
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

Solder with the corrected process: active brass flux (Superior No. 90 /
La-Co paste — rosin is marginal on brass; **never** acid flux near
electronics later), 2–3 mm chisel tip at 370–400 °C, joints abraded and
fluxed immediately before heating. **The frame is completed, washed
(hot water + baking-soda rinse + IPA), and painted before any electronic
part exists near it.**

## Phase 3 — complete the cage; do NOT glue the OLED yet *(video 1:30–2:05)*

The video glues the OLED into the front rectangle at 1:30, then solders the
four corner posts around it. **Invert that order**: solder all four corner
posts first, finish *all* hot work, then paint, then mount the display.
Gluing glass-bearing modules into a frame you're still soldering is how
displays die.

Paint now (the one painted assembly): degrease → gray Scotch-Brite scuff →
Rust-Oleum self-etching primer 249322 → 2 thin coats Rust-Oleum satin white
7791830. Handle after ~9 h; it keeps hardening for ~5–7 days. Mask the test
coupon and any tube end that seats into a joint; Rev A has no electrical
frame bond. Skip
chrome-effect paints entirely — they're aluminum flake: patchily conductive,
RF-lossy near the antenna, and not actually insulating.

Nickel-silver structural rods (the silver members) need no paint — they
solder with the same flux and technique as brass, just hold the iron a
moment longer.

## Phase 4 — sub-plates and the power spine *(video has no equivalent)*

The video free-forms everything and uses the frame as the ground bus
(4:20: "I'll connect all the ground connections directly to the brass
frame"). **This build never passes current through the frame.** Instead:

1. Epoxy small white polycarbonate/FR4 sub-plates across frame members
   (masked patches → adhesive meets primer, not paint).
2. Mount on the plates: regulator + a 5 × 8 mm star-point bus (one 3.3 V
   bus, one GND bus — the regulator's four 1.02 mm holes cannot take four
   loads' wires each), the amp, the holder in its white printed cradle, the
   switch board, the PTC.
3. Battery spine, in order: holder + → PTC → Pololu #2810 → regulator VIN.
   Junctions live on a solder tag by the holder, sleeved. Regulator VOUT/GND
   → star buses → four loads. 26–28 AWG for the spine, 30 AWG PTFE for
   signals.
4. Caps: 10–22 µF X5R across the regulator's own VIN/GND pads; 10 µF at the
   ESP32's 3V3 entry; ferrite bead + 10 µF + 220 µF polymer at the amp.

## Phase 5 — wire the modules *(video 2:10–3:35, changed)*

The video piggybacks the amp on the ESP32-C3 with five stiff 1 mm jumpers
and stacks the mic on shared clocks. Keep the *architecture* (shared
BCLK/WS, separate data), change the details:

| Signal | ESP32-C3 | Video | Corrected |
| --- | ---: | --- | --- |
| OLED SDA / SCL | 21 / 20 | same | same — via STEMMA QT cable, no soldering on the display |
| I2S WS (mic + amp) | 1 | same | same — **two separate stubs**, never daisy-chained (a broken WS with BCLK alive = DC into the speaker) |
| I2S BCLK (mic + amp) | 2 | same | same + 10 kΩ pull-up to 3.3 V (strap pin) |
| Amp DIN | 3 | same | same |
| Mic SD | **8** | GPIO8 | **GPIO4** + 100 kΩ pull-down; GPIO8 gets a 10 kΩ pull-up instead |
| Action button | — | absent | GPIO10 → white tact switch → GND, 10 kΩ pull-up + 100 nF |
| Battery sense | — | absent | **Not fitted in Rev A**; current source has no ADC battery monitor |

Amp specifics: jumper `SD` → VCC with insulated wire routed around the board
edge (forces left-channel mode — the board's own default divider can land on
the silent right channel). GAIN stays floating (9 dB). Mic: `L/R` → GND.
Speaker: factory leads to the amp's SPK terminals, twisted pair, **neither
lead ever grounded or touching the frame**; speaker sealed in its 1 cc box
(printed white, or BOX-1511-1CC behind a grille).

Mic handling: port tape stays on until final test; solder only at the header
pads; no flux/IPA/hot-air/compressed air near the port; all heat-shrink work
happens *before* the mic joins the assembly.

## Phase 6 — the switch *(video 4:25–4:35, changed)*

Video: SS12F44 soldered to the frame, switching the raw cell into the `5V`
pin. Corrected: the Pololu #2810 board mounts on a sub-plate and breaks the
**battery positive** line and provides reverse-voltage protection. It is an
operational switch, not a certified emergency/safety cutoff; removing the cell
is the hard disconnect.
Cap its slider with a tiny white printed knob. If you love the original
switch's look, the SS12F44 may instead drive the gate of a DMG2301L P-FET —
but the FET was out of stock at DigiKey on 2026-09-01, and the #2810 does
everything in one part.

## Phase 7 — battery *(video 4:35–5:05 — DO NOT copy this phase)*

The video strips the cell's wrapper and solders its can to the frame. That
sequence is the reason this guide exists. Corrected: the protected 16340
clicks into its polarity-marked guarded holder, cell untouched, wrapper intact, removable by
hand. White comes from the printed PETG cradle *around the holder* — never
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
peripherals. **Do not USB-flash the assembled unit yet:** removing the cell
does not prevent USB 3.3 V from back-powering the peripherals or the unpowered
S8V9F3 output. A reviewed removable-module/service-connector/power-isolation
design must close that gate before assembled flashing. Then use
`./scripts/flash.sh` (or the video's web flasher only for vendor wiring), the
Wi-Fi captive portal, and xiaozhi.me pairing as shown at 5:40–6:35.

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
bare nickel-silver braces, black OLED face with white pixels, white wiring
loom, silver holder clip — intended to run the corrected 16 kHz firmware.
Runtime is an unverified planning estimate (roughly 5–6 hours only if the
assumed average load and usable cell capacity prove true), with half-duplex
conversation (no barge-in on this chip),
speech processed by the configured cloud backend. Not a replica of the
video's raw-brass sculpture — a safer, slightly larger sibling that still
reads unmistakably as the same object.
