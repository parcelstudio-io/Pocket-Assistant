# Step-by-step build guide — R1 release

> **RELEASED PROCEDURE — 2026-09-02 final audit.** This guide implements the
> compact architecture released in
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md): protected
> LiPo pack + in-frame USB-C charger + slide switch, brass frame floating.
> The old converter/PTC/P-FET/16340 phases live only in git history.

This guide follows the sequence of the reference video
([*\[Satisfying\] Building a Tiny Pocket AI Assistant*](https://www.youtube.com/watch?v=25RGnr407PM),
8:19, no narration — instruction is on-screen caption cards) so you can watch
each phase and then do the corrected version of it. Timestamps are ±5 s.
Where this guide differs from the video it says so explicitly and links the
reasoning in [edu/](../edu/README.md).

**Firmware note before anything else:** this guide wires for the repository's
**corrected source build** (microphone data on **GPIO4**, 16 kHz audio,
display probed at 0x3C/0x3D). If you instead flash the creator's published
image the way the video does at 5:20, you must wire the microphone's SD to
**GPIO8** and use a 0x3C display — the vendor image knows nothing about the
corrections. Don't mix the two.

**The five hard rules** (from the
[decision doc](FINAL_MATERIALS_FOR_REVIEW.md#the-five-hard-rules)) apply to
every phase: switch OFF before any USB-C is plugged; device OFF while
charging; first charge attended; never solder to / unwrap / heat a cell;
stop on swelling, heat, or odor.

---

## Materials

Shop from **[MATERIALS.md](MATERIALS.md)** (the R1 order sheet). Read
**[the power-chain lesson](../edu/07-the-power-chain.md)** before any
power work.

---

## Phase 0 — before cutting brass: prove everything on the bench *(not in the video)*

The video starts at the template. Don't. This firmware has **never run on
physical hardware** in this workspace, and the assistant is useless if its
cloud backend isn't acceptable to you.

1. **Build or obtain the firmware.** `cd firmware && ./scripts/prepare.sh &&
   ./scripts/build.sh` (pinned ESP-IDF v6.0.2). The corrected build compiles
   clean and reproducibly (two clean builds, identical images — see
   [source-build.json](../firmware/source-build.json)).
2. **Qualify the boards.** `esptool flash_id` → 4 MB minimum. Plain SuperMini
   only (one blue LED, no U.FL socket — a "Plus" variant with a WS2812 on
   GPIO8 cannot use this pin map).
3. **Flash a bare SuperMini and test the backend.** Provision Wi-Fi, pair at
   xiaozhi.me (video 6:00 shows the flow), confirm one full voice round trip.
   The default backend is `api.tenclass.net` — a third-party service that
   receives your microphone audio. Decide *now* whether that's acceptable;
   self-hosting a Xiaozhi-compatible server and changing `CONFIG_OTA_URL` is
   the alternative.
4. **Breadboard the full stack** — OLED (I2C scan: 0x3C generic / 0x3D
   Adafruit), INMP441 records, MAX98357A plays. Meter the amp's `SD` pin:
   ~0.30 V stock (mix mode — fine); **~0 V means shutdown** — rework.
   Speaker leads only to the amp's terminals — never to a breadboard rail.
5. **Bench power test — the R1 chain from a current-limited supply.** Wire
   supply (+) → slide switch → SuperMini `5V` + amp `VIN` (with the 220 µF
   bulk cap fitted), supply (−) → common GND. Set 4.2 V, 1 A limit:
   - device boots, display up, one voice round trip completes;
   - sweep the supply 4.2 → 3.3 V under Wi-Fi + loud audio: **no reset**
     anywhere in the range (below ~3.4 V the LDO is in dropout — the MCU
     rides the sag; that's the reference topology's behavior);
   - toggle the slide switch 20× — clean boot every time;
   - record idle current (~expect 100–180 mA) and peak behavior. If Wi-Fi
     bursts reset the board near 3.3 V, double the bulk capacitance before
     blaming a module.
6. **Charger check, no cell yet.** Plug the #4410 into USB-C alone: 5V pad
   present, JST polarity verified against the pack's connector **with a
   meter, not by wire color**. First real charge happens in Phase 8.
7. **Acoustic A/B (only if using the phone-speaker fallback):** primary
   CES-20134-088PM vs fallback at 0.5 m and 1 m; wake word ("Hi, ESP") at
   1 m and 2 m. If it fails on the bench, no soldering fixes it.
8. Run `python3 tools/netcheck.py` — the static wiring rules must pass before
   you commit the layout.

## Phase 1 — template *(video 0:50–1:10)*

The video: modules measured with a steel ruler, outline drawn on paper with a
machinist square (his marks: ~40 mm × ~15 mm). **Copy the method; derive your
own numbers from the real parts.** The R1 target envelope is **≈ 45 × 32 ×
20 mm**: OLED face front; pack (29 × 36 × 4.75 mm) flat against the back;
SuperMini + amp + mic in the middle layer; charger board edge-mounted so its
USB-C faces out; switch and button reachable on the top face.

Lay the *actual parts* on cardstock. Draw every wire route. Confirm the
SuperMini's antenna end has clear space (no brass, wiring, or pack directly
over the antenna region — give it the board-edge overhang the reference uses).
Nothing gets cut until the cardstock version closes, and
`cad/fitcheck.py` is regenerated from your measured parts if you want the CAD
check (the committed report models the withdrawn architecture and is stale).

## Phase 2 — bend and solder the frame rectangles *(video 1:10–1:30)*

As the video does: bend 1.5 mm brass tube over the template with round-nose
pliers, two matching rectangles. Cut with a jeweler's saw — never flush
cutters, which crush the 0.225 mm wall. Deburr and dome every cut end
(no sharp edge may ever reach the pack).

Solder the frame with the brass process: Harris SCLF4 zinc-chloride flux
(acid-class — it exists ONLY at this empty-frame stage), 2–3 mm chisel tip at
370–400 °C, joints abraded and fluxed immediately before heating. Corner
posts and braces from the #9861 1.0 mm rod; rectangles from the #9831 tube.
**The frame is completed, washed (hot water + baking-soda rinse + IPA), and
optionally painted before any electronic part exists near it.**

## Phase 3 — complete the cage; do NOT glue the OLED yet *(video 1:30–2:05)*

The video glues the OLED into the front rectangle at 1:30, then solders the
four corner posts around it. **Invert that order**: solder all four corner
posts first, finish *all* hot work, wash, then (optionally) paint, then mount
the display. Gluing glass-bearing modules into a frame you're still soldering
is how displays die.

Finish choice: the reference is raw brass — that's fine, the frame carries no
current in this build. If painting white, follow
[edu/05_COLOR_AND_FINISH.md](../edu/05_COLOR_AND_FINISH.md); either way, paint
is decoration — Kapton/fish paper do the insulating.

## Phase 4 — insulation and the power spine *(video has no equivalent)*

The video free-forms everything and uses the frame as the ground bus (4:20:
"I'll connect all the ground connections directly to the brass frame").
**This build never passes current through the frame.** Instead:

1. **Line the pack bay first**: fish paper under and around where the pack
   sits — the flame-rated layer between the cell and everything else. Kapton
   over any module back or splice that can reach brass.
2. Mount the charger board where its USB-C port exits the frame; hot-glue at
   the corners, port and status LED visible.
3. **Battery spine, in order:**
   `pack JST ↔ charger battery port` (or via the JST pigtail splitter), then
   `charger BAT pad → slide switch → switched-positive bus`, and
   `charger GND pad → common ground bus`. The switched bus feeds the
   SuperMini `5V` pin and the amp `VIN`; the ground bus collects every
   return. 26 AWG for the spine, 30 AWG for signals. Sleeve every junction.
4. **Caps:** 220 µF bulk + 10 µF ceramic at the amp's VIN/GND; 10 µF at the
   SuperMini's `5V` entry; 100 nF at OLED and mic supplies.

The pack itself goes in **last** (Phase 7) — the spine is built and tested
with the JST unplugged.

## Phase 5 — wire the modules *(video 2:10–3:35, changed)*

The video piggybacks the amp on the ESP32-C3 with five stiff 1 mm jumpers and
stacks the mic on shared clocks. Keep the *architecture* (shared BCLK/WS,
separate data), change the details:

| Signal | ESP32-C3 | Video | Corrected |
| --- | ---: | --- | --- |
| OLED SDA / SCL | 21 / 20 | same | same — read the silkscreen pin order first (GND/VCC order varies by vendor) |
| I2S WS (mic + amp) | 1 | same | same — **two separate stubs**, never daisy-chained (a broken WS with BCLK alive = DC into the speaker) |
| I2S BCLK (mic + amp) | 2 | same | same + 10 kΩ pull-up to 3.3 V (strap pin) |
| Amp DIN | 3 | same | same |
| Mic SD | **4** | GPIO8 | moved to **GPIO4** + 100 kΩ pull-down; GPIO8 gets a 10 kΩ pull-up instead |
| Action button | 10 | absent | GPIO10 → tact switch → GND, 10 kΩ pull-up + 100 nF |
| Power | `5V` pin | same | same idea — but from the **protected, switched** bus, never a bare cell |

Amp specifics: stock SD ≈ 0.30 V mix mode plays at **full amplitude** (the
ESP32-C3 duplicates the mono slot — see
[edu/04-audio.md](../edu/04-audio.md)); GAIN stays floating (9 dB). Mic:
`L/R` → GND. Speaker: leads to the amp's output terminals, twisted pair,
**neither lead ever grounded or touching the frame**.

Mic handling: port tape stays on until final test; solder only at the header
pads; no flux/IPA/hot-air near the port; all heat-shrink work happens
*before* the mic joins the assembly.

## Phase 6 — the switch *(video 4:25–4:35, corrected)*

Video: a slide switch soldered to the frame, switching the raw cell into the
`5V` pin. R1 keeps the same part and the same job — but it switches the
**protected** positive lead, its terminals are sleeved, and its body mounts
with glue/epoxy to a frame member without its terminals touching brass. It
fails open = pager off. Unplugging the pack's JST is the hard disconnect.

## Phase 7 — battery *(video 4:35–5:05 — DO NOT copy this phase)*

The video strips the cell's wrapper and solders its can to the frame. That
sequence is the reason this repository exists. Corrected: the protected pack
slides into its fish-paper-lined bay, connects **only by its factory JST
lead**, and is retained by a strap/guard so it cannot chafe or escape —
removable by hand for service. The JST stays unplugged for every soldering,
painting, cleaning, or flashing operation, and while the unfinished device is
transported.

Before the first connection: meter the JST polarity against the charger's
markings, and check pack voltage (3.0–4.2 V; outside that, stop).

## Phase 8 — charging *(video 5:05–5:20, kept — with rules)*

The video wires a Type-C module permanently to the cell; R1 does the same,
with a charger whose current is documented (#4410: 100 mA default). The
rules:

- **Switch OFF while charging** (no load sharing on this class of board).
- **First charge attended**, on a non-flammable surface; pack cool to the
  touch; confirm the DONE LED and 4.20 ± 0.05 V at the pack.
- Only after a clean first cycle may you close the #4410's jumper for 500 mA
  (= 1C for the 500 mAh pack; leave at 100 mA for the 350 mAh alternate).

## Phase 9 — flash and configure *(video 5:20–6:35, same idea)*

The video flashes at web.esphome.io and pairs at xiaozhi.me. Do both during
Phase 0 with the bare SuperMini. For the assembled unit the rule is simple
and physical: **slide switch OFF and pack JST unplugged before the
SuperMini's USB-C is connected.** With the pack out of circuit, USB feeds
only the SuperMini's LDO and the 3.3 V peripherals — all rated for it.

Then `./scripts/flash.sh` (or the video's web flasher only for vendor-image
wiring), the Wi-Fi captive portal, and xiaozhi.me pairing as shown at
5:40–6:35.

**The source build is finalized for English:** wake word **"Hi, ESP"**
(`wn9s_hiesp` — say the letters), en-US display strings, spoken prompts and
activation digits. On first boot the device shows and *reads aloud* a 6-digit
code; enter it at xiaozhi.me and set the agent's language and voice to
English there too. (The vendor image instead answers to Mandarin
"ni hao xiao zhi" and boots in Chinese.)

## Phase 10 — bring-up gates *(not in the video; do them all)*

With a meter (and the bench supply for step 2):

1. Pack unplugged: every frame member ↔ BAT+, GND, 3.3 V, each signal, and
   both speaker leads open/high-resistance. This build has no deliberate
   frame bond.
2. Bench supply at the pack's JST position (4.0 V, 1 A limit) → boot,
   display, mic, amp, one voice round trip in final geometry.
3. Toggle the switch 20× — clean boot every time.
4. Ten minutes of loud audio + Wi-Fi → amp warm is fine; nothing too hot to
   touch; pack bay (still empty) unobstructed.
5. Wi-Fi in final geometry vs the bare board in open air at fixed distance:
   compare RSSI/reconnections; investigate any large degradation (brass near
   the antenna region is the usual suspect).
6. Only now does the pack live in the pager (Phase 7 checks), then Phase 8's
   attended first charge.

Full acceptance list: [edu/06_ACCEPTANCE_TESTS.md](../edu/06_ACCEPTANCE_TESTS.md).

---

## What you'll have

A **≈ 45 × 32 × 20 mm** brass cage pager — video-scale — running the
corrected 16 kHz source firmware: OLED face, wake-word voice chat over
**Wi-Fi only** (a phone hotspot covers the street; cellular is out of scope),
half-duplex conversation (no barge-in on this chip). Estimated ~3 h of
always-on listening from the 500 mAh pack (measure it — acceptance test).
Speech is processed by the configured cloud backend. Not a replica of the
video's raw-cell sculpture — the same object, with a power system you can
hand to someone without a safety briefing. Well — a shorter one.
