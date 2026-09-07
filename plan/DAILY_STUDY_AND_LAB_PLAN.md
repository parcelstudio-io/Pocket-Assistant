# 15-session Pocket AI study and lab plan

This plan turns the electronics course into fifteen practical sessions of
about 2–3 hours each. It is written for a software engineer who learns best by
building a small piece, observing it, and then studying the theory that explains
the result.

The objective is not to read all of `edu/` before touching hardware. The
objective is to create one new piece of trustworthy evidence each session.
Do not read this entire plan in one sitting: read the ground rules once, then
open only the section for the day you are working on.

To get the hardware doing something first, use the
[USB prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md). It uses the owned
controller, button, OLED, and microphone, with one source-firmware pin map and
offline diagnostics. Then work through these sessions around that prototype;
the first five theory labs are useful practice, not prerequisites for bare-board
USB boot. No additional parts are required for that starting point.

For the physics and engineering behind each lab, open the
[illustrated concept notes](concepts/README.md). Each day now has a direct link
to a concise explanation with drawings, a worked example, and a self-check.
Start with concepts 01–03 for charge, voltage, current, and circuit laws; read
the remaining pages as needed. These optional 5–10 minute notes fit inside the
existing study block and add no parts or extra lab requirements.

After Session 15, the intended result is:

- a documented set of basic circuit and measurement labs;
- one identified ESP32-C3 that can be flashed and monitored over USB;
- a battery-free digital prototype built one peripheral at a time, where the
  exact owned parts pass their individual gates;
- soldering and rework practice completed on sacrificial material;
- a 1:1 nonconductive fit mock-up; and
- a written list of what is proven, inconclusive, or still held.

It is **not** a release to connect or charge a lithium cell, assemble the final
power system, cut the final brass stock, or pocket-carry the device. The current
power/enclosure design discussion is
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md). Its future
power-fixture work is separate from the USB prototype. Use the quickstart for
that prototype; the old step-by-step build and wiring guides are archived
references.

## How to use the plan

Treat “Day 1” through “Day 15” as ordered sessions, not calendar deadlines.
Five sessions per week with rest or catch-up days is a good pace. Repeat a
session when a result is unexplained instead of advancing to keep a schedule.

If you already understand a topic, prove it with the exit gate rather than
skipping the lab. If you have already completed a lab and have a reproducible
record, link that evidence and move forward.

Use these status labels:

- `NOT STARTED` — no work yet;
- `IN PROGRESS` — the session has started but its exit gate is open;
- `PASS` — the prediction, result, and acceptance rule agree;
- `REPEAT` — the result is failed or unexplained and needs another session;
- `INCONCLUSIVE` — available instruments cannot answer the question; and
- `HOLD` — current project authority does not permit the experiment.

A failed prediction is useful learning. An unexplained success is not a pass.

## The no-purchase rule

This plan assumes the items recorded in
[INVENTORY.md](../docs/INVENTORY.md) are already available. Do not buy a missing
tool or component merely to stay on schedule.

When something is unavailable:

1. complete the calculation, source inspection, or unpowered portion;
2. record exactly what the available evidence proves;
3. mark the unavailable measurement `INCONCLUSIVE` or the experiment `HOLD`;
4. continue only with later work that does not depend on that result.

Never replace a missing fuse, isolator, dummy load, differential instrument, or
cell fixture with an improvised connection. Generic parts from the older
inventory are useful learning articles, but ownership does not make them
approved final-build parts.

Every session below opens with a **Prepare** block in three parts: what is
already in hand and what this session does with it, what is *not* in hand along
with the substitute or the gate it closes, and what must stay off the bench.
The items that no session can supply are collected in
[the not-in-the-record table](#referenced-by-this-plan-but-not-in-the-purchase-record).

## Product links for items used in this plan

The links below are purchase-provenance links recovered from the project's
archived order sheet and inventory history. They identify what was bought; they
do **not** override the current safety or design status in
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md).

Use this index whenever a daily session names an item. An entry marked
`not recorded` means the repository names the owned item or order batch but
does not preserve its exact product URL. Do not silently replace it with a
similar search result. Add the original order-page URL here if it becomes
available.

When two documents disagree about whether something is in hand,
[INVENTORY.md](../docs/INVENTORY.md) is the purchase record and
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md) is the
design authority. `MATERIALS.md`, `BOM.md`, and `PURCHASE_READINESS.md` are
pre-purchase order sheets: never read their "still to buy" or quantity columns
as the current state of your bench.

### Referenced by this plan but not in the purchase record

These five items were previously listed among the purchased tables below. They
are not in `INVENTORY.md` as bought, so the daily prep lists treat them as
absent and give a fallback for every session that wanted them. Do not buy any
of them to stay on schedule.

| Item | Status | Wanted by | What the plan does instead |
| --- | --- | --- | --- |
| USB-A-to-C data cable (Rankie 3-pack) | `INVENTORY.md` "Still needed" | Days 6–10, 14–15 | Prove any cable you already own carries data before trusting a result; a charge-only cable makes a working board look dead. Otherwise the flash/boot gate is `INCONCLUSIVE`. |
| Solder wick (JoTownCand 3-pack) | `INVENTORY.md` "Still needed" | Day 12 | Use the owned X-Tronic solder sucker on through-hole joints only; mark fine-pad rework `INCONCLUSIVE`. |
| Sacrificial perfboard | No record anywhere | Days 11–12 | Practise on spare header pins, resistor leads, and offcut wire. Never on a project module. |
| Magnification | No record; `BUY-P0` | Days 11–12 | Inspect from phone macro/zoom photographs and record that the method was substituted. |
| Fume extraction | No record; `BUY-P0` | Days 11–12 | A hard gate, not a convenience: write the actual ventilation arrangement into the lab record before the iron is switched on, or do not run the session. |

A discrete LED is also referenced as an optional Day 7 extension and has no
purchase record; that exercise is simply skipped.

### Electronics and passive components

| Item referenced by the plan | Purchased item and product link | Used on |
| --- | --- | --- |
| ESP32-C3 controller | Meshnology/plain ESP32-C3 SuperMini 10-pack — [Amazon B0F888JQ91](https://www.amazon.com/dp/B0F888JQ91) | Days 1, 6–10, 14–15 |
| OLED | Hosyond 0.96-inch white SSD1306 I2C 5-pack — [Amazon B09T6SJBV5](https://www.amazon.com/dp/B09T6SJBV5) | Days 1, 6, 8, 14–15 |
| I2S microphone | AITRIP/INMP441 5-pack — [Amazon B092HWW4RS](https://www.amazon.com/dp/B092HWW4RS) | Days 1, 6, 9–10, 14–15 |
| I2S amplifier | HiLetgo MAX98357A 3-pack — [Amazon B0CDWXZZCH](https://www.amazon.com/dp/B0CDWXZZCH) | Days 1, 6, 9–10, 13–14 |
| Speaker | Same Sky CES-20134-088PM, 8 ohm/0.8 W — [DigiKey 2223-CES-20134-088PM-ND](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309). **One unit only, no spare and no A/B partner**; a damaged factory lead ends speaker work for this plan | Days 1, 6, 10, 14 |
| Action button | QTEATAK 6x6 mm tactile-switch and cap kit — [Amazon B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4) | Days 1, 6–8, 14–15 |
| Resistors, including 1 kohm, 2.2 kohm, 10 kohm, and 100 kohm | LuminologyPro 1/4 W resistor kit — [Amazon B0F4P352BB](https://www.amazon.com/dp/B0F4P352BB) | Days 2–5, 7, 11, 13 |
| Ceramic capacitors | BOJACK ceramic-capacitor kit — [Amazon B07P7HRGT9](https://www.amazon.com/dp/B07P7HRGT9) | Days 4 and 13 |
| Electrolytic capacitors, including 100 uF and 220 uF | ALLECIN electrolytic-capacitor kit — [Amazon B0C1VBXCQM](https://www.amazon.com/dp/B0C1VBXCQM) | Days 4 and 13 |
| Protected 500 mAh LiPo | Adafruit #1578 — [Adafruit product 1578](https://www.adafruit.com/product/1578) | Storage boundary and Day 14 inert mock-up only |
| Protected 1200 mAh LiPo | Adafruit #258 — [Adafruit product 258](https://www.adafruit.com/product/258) | Storage boundary and Day 14 inert mock-up only |
| USB-C LiPo charger | Adafruit #4410 — [Adafruit product 4410](https://www.adafruit.com/product/4410) | Storage/source-state discussion only |
| Slide switch | Chanzon/SS12D00-class SPDT 25-pack — [Amazon B09R434VJQ](https://www.amazon.com/dp/B09R434VJQ) | Day 13 unpowered or currently permitted testing only |
| 2.54 mm breakaway headers | Exact purchase URL `not recorded`; recorded in Amazon order #4. **22 pins exist in total**, and the inventory earmarks them for making the bench stack reversible | Days 11–12 |
| JST-PH pigtails | Exact purchase URL `not recorded`; recorded as daier 2.0 mm cable set | Not used in powered work in this plan |

The resistor and capacitor links point to the purchased assortment, not to
separate listings for each individual value. Confirm markings, measured value,
polarity, voltage rating, and power rating before each lab.

### Bench and measurement equipment

| Item referenced by the plan | Purchased item and product link | Used on |
| --- | --- | --- |
| Digital multimeter | KAIWEETS HT118A/TRMS meter — [Amazon B08BL288LW](https://www.amazon.com/dp/B08BL288LW) | Days 1–5 and 7–13 |
| Current-limited bench supply | SKY TOPPOWER PS305H — [Amazon B0BN1F6CGZ](https://www.amazon.com/dp/B0BN1F6CGZ) | Days 2–5 and 13 |
| Digital caliper | Neiko 01407A — [Amazon B000GSLKIW](https://www.amazon.com/dp/B000GSLKIW) | Days 6 and 14 |
| Safety glasses | 3M Solus 1000 — [Amazon B016KZ1ZPM](https://www.amazon.com/dp/B016KZ1ZPM) | Every physical lab |
| Solderless breadboards | REXQualis 830/400-point set — exact purchase URL `not recorded`; recorded in Amazon order #5 | Days 2–5 and 7–9 |
| Dupont jumpers | TODOELEC 10 cm/120-wire kit — exact purchase URL `not recorded`; recorded in Amazon order #4 | Low-current Days 2–9 only |
| Logic analyzer | No purchase recorded; optional instrument only | Days 8–9 |
| Oscilloscope/differential measurement equipment | No purchase recorded; optional/arranged instrument only | Day 10 |
| Current-rated 8 ohm dummy load and leads | No purchase link recorded for the exact approved fixture | Conditional Day 10 only |
| Camera, scale/ruler, stopwatch, computer, and spreadsheet | General tools; no project purchase URL recorded | Various days |

### Soldering, wire, and rework equipment

| Item referenced by the plan | Purchased item and product link | Used on |
| --- | --- | --- |
| Soldering station, holder, helping hands, and silicone mat | X-Tronic 3020-XTS complete kit — exact purchase URL `not recorded`; recorded as an earlier X-Tronic order | Days 11–12 |
| Electronics solder | MAIYUM 63/37, 0.8 mm — [Amazon B076QF1Y85](https://www.amazon.com/dp/B076QF1Y85) | Days 11–12 |
| Electronics flux | Chip Quik CQ4LF no-clean flux pen — exact purchase URL `not recorded`; recorded in the Adafruit order | Days 11–12 |
| Wire stripper | Hakko CHP CSP-30-1 — [Amazon B00FZPHMUG](https://www.amazon.com/dp/B00FZPHMUG) | Days 11–12 |
| Desoldering pump | Solder sucker included in the X-Tronic 3020-XTS kit; coarse, so through-hole practice joints only | Day 12 |
| Heat gun | QWORK 300 W with stand — [Amazon B09NDCCW29](https://www.amazon.com/QWORK-Shrink-Shrinking-Wrapping-Embossing/dp/B09NDCCW29) | Day 12, with cells absent |
| 30 AWG signal wire | CBAZY silicone-wire kit — [Amazon B073RDGTPB](https://www.amazon.com/dp/B073RDGTPB) | Days 11–12 and mock-up planning |
| 26 AWG power wire | TUOFENG silicone-wire kit — [Amazon B07G2LRX68](https://www.amazon.com/dp/B07G2LRX68) | Days 11–12 and unpowered planning |
| Heat-shrink tubing | Pointool 14-size white kit — [Amazon B08N4W4K9X](https://www.amazon.com/dp/B08N4W4K9X) | Day 12 |
| Flush cutters | BOENFU 6-inch; wire and component leads only, never brass tube | Days 11–12 |

### Mechanical, insulation, and mock-up materials

| Item referenced by the plan | Purchased item and product link | Used on |
| --- | --- | --- |
| Brass tube | K&S #9831, 1.5 mm OD — [Amazon B005WPAW9M](https://www.amazon.com/dp/B005WPAW9M) | Day 14 optional uncut RF comparison only |
| Brass rod | K&S #9861, 1.0 mm — [Amazon B005WPB7YG](https://www.amazon.com/dp/B005WPB7YG) | Fit planning only; do not cut during this plan |
| Fish-paper insulation | XFJYMXDM 0.2 mm fish paper — [Amazon B0GZVDKBBS](https://www.amazon.com/dp/B0GZVDKBBS) | Day 14 clearance planning only |
| Polyimide/Kapton tape | ELEGOO four-pack — [Amazon B072Z92QZ2](https://www.amazon.com/dp/B072Z92QZ2) | Mock-up/insulation planning only |
| Jeweler's saw | SE 3-in-1 saw and blade set — [Amazon B06XPSLS6N](https://www.amazon.com/dp/B06XPSLS6N) | Referenced as a held final-frame tool; no final cutting in this plan |
| Round/chain-nose pliers | WORKPRO three-piece set — [Amazon B0B8QBVXXR](https://www.amazon.com/dp/B0B8QBVXXR) | Held final-frame work only |
| Brass acid flux | Harris SCLF4 — [Amazon B0015DWPV8](https://www.amazon.com/dp/B0015DWPV8) | Storage/safety boundary only; never electronics work |
| Hot-glue gun | SHJADE 20 W mini gun — exact purchase URL `not recorded`; recorded in Amazon order #8 | Held final assembly only |
| Diamond needle files | SE 744DF-R set — exact purchase URL `not recorded`; recorded in Amazon order #8 | Held final-frame work only |
| Cardboard, paper, and tape | Reuse clean packaging/household material; no dedicated purchase link required | Day 14 |

These links are intentionally direct product/order references rather than
search-result links. Amazon inventory and sellers can change behind an ASIN, so
match the received label and physical part rather than treating the web page as
proof of the delivered item.

## Non-negotiable boundaries for all 15 sessions

- Keep every lithium cell terminal-protected, electrically disconnected, and
  outside the active work area. Do not probe, connect, charge, discharge,
  solder, heat, bend, clamp, puncture, or unwrap it.
- Use the controller's USB cable as the only power source for the beginner
  prototype. The button, OLED, and microphone may use its documented GPIO,
  3.3 V output, and GND connections. Disconnect any external 3.3 V/5 V source,
  regulator, charger, battery, and amplifier harness. Flash the controller
  bare initially. Later reflashes may keep the tested USB-powered button,
  OLED, and microphone connected; unplug USB before every wiring change.
- Turn off and disconnect power before changing wiring or using resistance or
  continuity mode.
- Never put a current-mode meter directly across a source. Return its red lead
  to the voltage jack immediately after an optional current measurement.
- Stop for unexpected current limiting, unstable voltage, heat, smell, smoke,
  swelling, arcing, mechanical noise, damaged insulation, or a connection you
  do not understand.
- Neither class-D amplifier speaker output is ground. Never connect either
  output to circuit ground, the brass frame, a logic-analyzer ground, or an
  earth-referenced oscilloscope clip.
- Do not put the amplifier or full-load current through breadboard contacts or
  Dupont jumpers.
- Keep the brass frame electrically floating. Do not cut final stock, glue
  electronics, paint, or perform structural hot work during this plan.
- Keep flux, solvent, glue, paint, hot air, and compressed air away from the
  microphone port.

For each prototype experiment, save the board ID, wiring photograph, firmware
identity, expected result, observed result, and next action. For bench-supply
labs also record voltage and current-limit settings. The full
[lab record template](../edu/fundamentals/reference/lab-record-template.md) is
available when a more detailed measurement needs it.

## Standard 2–3 hour session rhythm

| Time | Activity |
| ---: | --- |
| 10 min | Restore the last known-good setup; confirm cells and charger are absent. |
| 35 min | Read only the assigned lesson sections. Write down unclear terms. |
| 15 min | Write one question, prediction, acceptance rule, and stop conditions. |
| 15 min | Draw the complete source and return path; perform unpowered checks. |
| 60–75 min | Run the lab, changing only one variable at a time. |
| 15 min | Save measurements, photographs, terminal output, and interpretation. |
| 10 min | Disconnect sources, clean the bench, and write the next first action. |
| Optional 20 min | Repeat a run or perform one discriminating debug test. |

Stop at the 3-hour mark. Tired soldering or improvised powered work does not
create useful evidence.

## Firmware contract card

Use the corrected source build throughout this plan and the quickstart. This
provides an editable, consistent pin map and offline diagnostics. Label the
controller `SOURCE / MIC GPIO4 / 16 kHz` before connecting peripherals.

| Property | Corrected source build |
| --- | --- |
| Microphone data | GPIO4 |
| Audio sample rate | 16 kHz |
| Expected I2S bit clock | 1.024 MHz |
| OLED address | `0x3C` or `0x3D` |
| Amplifier | Absent from beginner prototype; GPIO5 enable stays low |

The source uses GPIO1 for I2S word select, GPIO2 for I2S bit clock, GPIO3 for speaker
data, GPIO20 for OLED SCL, GPIO21 for OLED SDA, and GPIO10 for the optional
active-low action button. Verify the current firmware files rather than relying
only on this summary. The historical vendor binary uses microphone GPIO8 and
24 kHz; it is outside this beginner path. Do not flash it onto this harness.

The default Xiaozhi/Tenclass service receives device metadata and microphone
audio. Do not provision Wi-Fi or perform a voice test until you have made and
recorded a privacy/backend decision.

---

## Week 1 — Build the electrical foundation

### Day 1 — System map, safety, and a green software baseline

**Status:** `NOT STARTED`

**Question:** What is the system made of, and what work is currently allowed?

**Optional illustrated explanation:** [Charge, energy, and complete circuits](concepts/01-charge-energy-and-circuits.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| Meshnology ESP32-C3 SuperMini dev board | 1 of the 10 (the other 9 stay bagged and unopened) | Lab step 1: becomes MCU-A1 for the ID label, the block diagram, and the unpowered parts photograph |
| Hosyond SSD1306 OLED, 0.96 in 128x64 I2C, white | 1 of the 5 | Lab step 1: becomes OLED-A1; its silkscreen pin order is read and photographed while nothing is wired |
| AITRIP INMP441 I2S MEMS microphone | 1 of the 5 | Lab step 1: becomes MIC-A1; handled by the board edges only, acoustic port left open, dry, and untaped |
| HiLetgo MAX98357A I2S class-D amplifier | 1 of the 3 | Lab steps 1 and 4: labelled AMP-A1 and drawn into the block diagram only — it is never wired or powered in this plan |
| Same Sky CES-20134-088PM speaker, 8 ohm 0.8 W, factory-enclosed | 1 — the only unit in hand, no spare and no A/B partner | Lab step 1: labelled SPK-A1 and photographed; the 60 mm 32 AWG factory leads are inspected, coiled, and strain-relieved, never cut, tinned, or tugged |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + 1 pair of test leads + hard case + manual | Lab step 3: identify the DC-voltage, resistance, continuity, and fused-current jacks and record lead condition, with the leads out of the jacks during the inspection |
| 3M Solus 1000 safety glasses, clear | 1 | Worn for the whole physical session, per the plan's every-physical-lab rule |
| X-Tronic bundle: tweezers | 1 pair | Position the five modules for the labelled-parts photograph without touching pads or the mic port; also inspected for an ESD marking and the result written down |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll (about 5 flags, ~20 mm each) | Write MCU-A1 / OLED-A1 / MIC-A1 / AMP-A1 / SPK-A1 on tape flags applied to each part's bag or a bare board edge — never across the mic acoustic port, the OLED glass, or the speaker mesh |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | Layout surface for labelling and the parts photograph; there is no hot work today, so the X-Tronic silicone mat stays stored |
| Existing computer with Python 3 and the repository checkout (general tool, not a project purchase) | 1 | Lab step 5: run `python3 -m unittest discover -s tools/tests -v` and `python3 tools/netcheck.py` from the repository root and save both transcripts |
| Camera or phone (general tool, not a project purchase) | 1 | Photograph the labelled unpowered parts, the OLED silkscreen, the board markings, and the meter jacks |
| Notebook, pen, and one sheet of blank drawing paper (general tools, not a project purchase) | 1 set | Lab step 4 one-page block diagram, plus the five sentences distinguishing DATASHEET / TYPICAL / ASSUMED / CALCULATED / MEASURED evidence |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **USB-A-to-C data cable (Rankie 3-pack)** — listed under **Still needed** in
  `INVENTORY.md`.
  Not used by any Day 1 step — nothing is powered today — but Day 1 is the
  session where the bench inventory is reconciled. Days 6-10 and 14-15 cannot
  flash or monitor
  without a data-capable cable. Verify, do not buy. Hunt for any USB-A-to-C
  cable already in the house and prove it carries data (it must enumerate a
  known data device, not just charge); a charge-only cable makes a working
  board look dead. Record the verdict on the Day 1 evidence sheet. No Day 1
  step becomes INCONCLUSIVE. If no data-capable cable is proven, pre-mark the
  Day 6 flash/boot gate INCONCLUSIVE now and plan Day 6 as the unpowered board
  evidence sheet plus the host-tool install only.
- **Grounded ESD mat and wrist strap** — **no purchase record anywhere**.
  Lab step 1 handles a bare ESP32-C3 controller and a MEMS microphone out of
  their bags for labelling and photography. No purchase. Work on the bare bench
  (no carpet, no fleece), touch a large grounded metal object before each
  pickup, hold boards by the edges, and return each module to its antistatic
  bag immediately after its photo. Write 'no ESD control in place; handling
  method substituted' as a limitation line on the Day 1 evidence sheet, and
  record whether the X-Tronic tweezers carry an ESD marking.
- **Magnification (loupe, visor, or bench magnifier)** — **no purchase record
  anywhere**.
  Lab step 3 records DMM lead and jack condition, and the setup checks require
  reading the OLED silkscreen pin order and the controller's fine markings —
  both are visual-criteria judgements. No purchase. Substitute a phone camera
  at macro/zoom: photograph every marking and lead surface and read it enlarged
  on screen. Record in the evidence sheet that the inspection method was
  substituted, because the Day 1 record is what Day 6 and Day 8 will rely on.
- **Li-ion storage / containment case** — **no purchase record anywhere**.
  Lab step 2 requires confirming and recording that all four cells and the
  charger are terminal-protected, disconnected, and away from the bench. No
  purchase. Record the arrangement that actually exists (bagged, connectors
  unmated and taped, stored outside the work area) plus whatever lot/label text
  is legible without handling. Mark the FINAL_MATERIALS containment-case
  requirement UNMET/HOLD in the lab record. Do not move, re-tape, unwrap, or
  electrically inspect a pack to make the record look better — step 2 is
  explicit that the cells are not electrically inspected.

*Keep off the bench today.*

- Adafruit #1578 LiPo 500 mAh x2 and Adafruit #258 LiPo 1200 mAh x2 — all four
  packs stay terminal-protected in storage and are recorded from there, never
  brought to the bench
- Adafruit #4410 USB-C Micro-Lipo charger — off the bench and unpowered; no
  charging is released anywhere in this plan
- daier JST-PH 2.0 mm connector cables — nothing that can mate with a cell
  connector belongs on a Day 1 bench
- Harris SCLF4 Stay-Clean acid flux — stays sealed and out of the room; it is
  brass-only, and the IPA/baking-soda neutraliser it requires is not in hand
- X-Tronic 3020-XTS soldering station, MAIYUM solder, Chip Quik flux pen, QWORK
  heat gun, SHJADE hot glue gun — no hot work of any kind on Day 1
- SKY TOPPOWER DC bench supply — unplugged and unconnected; every part on the
  bench today is unpowered
- Any USB cable plugged into any module — the controller is not powered until
  Day 6

*Check before you start.*

1. Controller variant gate before the board becomes MCU-A1: confirm by eye and
   photograph that it is a plain ESP32-C3 SuperMini, not a 'Plus'/RGB variant
   (RGB LED on GPIO8 breaks this pin map) and not a U.FL variant. Do not judge
   by seller name. Reserve the other nine boards, bagged, as the multipack
   margin.
2. OLED silkscreen order: read and photograph the pin order on OLED-A1 and
   write it on its label. Vendors ship GND-VCC-SCL-SDA and VCC-GND-SCL-SDA on
   identical-looking boards, and this Day 1 record is what Day 8 will wire
   from.
3. DMM incoming inspection with the leads unplugged: check both leads and probe
   tips for cracked insulation or bent tips, identify COM, the V/Ω jack, and
   the fused current jack, and note the meter's input-fuse rating from the
   manual. Finish by seating the red lead in the V/Ω jack so the meter is never
   stored in current mode.
4. Speaker incoming inspection: SPK-A1 is the only speaker in hand. Inspect the
   60 mm 32 AWG factory leads for nicks under camera zoom, coil them against
   the enclosure with a Kapton flag for strain relief, and record that a
   damaged lead ends all speaker work in this plan.
5. Microphone port hygiene: before MIC-A1 comes out of its bag, confirm no
   flux, IPA, glue, paint, aerosol, or adhesive is on or near the bench. Label
   its bag, not the port face; contamination of the acoustic port is permanent.

Day 1 is entirely unpowered and software-only: the two Python commands run on
the host and prove nothing about hardware, which is exactly what the exit gate
asks you to explain. Everything the lab steps touch is already in hand; the
four not-owned items are handling/inspection controls and the cable pre-check,
none of which stop the session. Authority order when documents disagree:
docs/INVENTORY.md is the purchase record, docs/FINAL_MATERIALS_FOR_REVIEW.md is
the design authority, and docs/MATERIALS.md, docs/BOM.md, and
docs/PURCHASE_READINESS.md are pre-purchase order sheets whose 'still to buy'
and quantity columns must never be read as the current in-hand state. Owning a
module is not design approval: the Hosyond OLED, AITRIP mic, and HiLetgo amp
are HOLD-class alternatives to unpurchased preferred parts, and the two cell
types are REJECT/quarantined samples. The 22 loose 2.54 mm header pins are not
consumed today — leave them bagged for the Day 11-12 decision.

**Study**

- Read the [project overview](../edu/01-how-it-fits-together.md).
- Read [Lesson 00](../edu/fundamentals/00-safety-evidence-and-course-map.md).
- Skim the headings in the
  [foundations index](../edu/fundamentals/README.md); do not read every lesson.

**Lab**

1. Assign simple IDs to one controller, OLED, microphone, amplifier, and
   speaker, such as `MCU-A1`, `OLED-A1`, and `MIC-A1`.
2. Confirm every cell and the charger are disconnected and stored away from the
   bench. Record that state; do not electrically inspect the cells.
3. Identify the DMM voltage, resistance, continuity, and fused current jacks.
   Inspect the leads and record their condition.
4. Draw a one-page system block diagram showing controller, display,
   microphone, amplifier, speaker, power, USB, and the floating frame.
5. From the repository root, capture a software-only baseline:

   ```bash
   python3 -m unittest discover -s tools/tests -v
   python3 tools/netcheck.py
   ```

**Evidence to save**

- the system diagram;
- a photograph of the labeled, unpowered parts;
- the two command outputs; and
- five sentences distinguishing `DATASHEET`, `TYPICAL`, `ASSUMED`,
  `CALCULATED`, and `MEASURED` evidence.

**Exit gate:** You can explain the signal path, find the quickstart's USB
prototype instructions, identify the deferred battery/frame work, and state
why software checks do not prove physical power or audio behavior.

### Day 2 — Voltage, current, resistance, power, and units

**Status:** `NOT STARTED`

**Question:** Can measured voltage and resistance predict current and resistor
power?

**Optional illustrated explanation:** [Voltage, current, resistance, and power](concepts/02-voltage-current-resistance-and-power.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| LuminologyPro resistor kit, 25 values, 1/4 W | 3 x nominal 1 kΩ 1/4 W (one under test, two spares in case a lead breaks or a part reads outside its tolerance band) | The entire circuit: measured unpowered, then driven at 3.3 V so current is inferred with I = V/R and power with P = VI |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + 1 pair of test leads + hard case + manual | Lab step 2 unpowered resistance reading, then lab step 5 DC volts across the resistor; red lead stays in the V/Ω jack for the whole session |
| SKY TOPPOWER DC bench supply, 0-30 V / 0-5 A (PS305H) | 1, with its own insulated output leads | Lab step 1: set 3.3 V and a 20 mA current limit with the output OFF, then energize in step 4 and switch off again in step 7 |
| REXQualis solderless breadboards (830 + 400 point) | 1 (the 830-point board; the other three stay boxed) | Holds the single resistor and the two supply landing points; mapped with continuity before anything is energized |
| TODOELEC Dupont jumper kit, 10 cm | 6 wires (2 to bridge the split power rails, 2 as landing wires for the supply's clip leads, 2 spare) | Low-current bench wiring only — 3.3 mA at 3.3 V is far inside their rating |
| BOENFU 6-inch flush cutters | 1 | Trim the 1 kΩ resistor's leads so it seats flat in the breadboard; component leads and wire only, never brass |
| X-Tronic bundle: tweezers | 1 pair | Seat and remove the resistor and jumpers without flexing the breadboard clips or touching a part that has been carrying current |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll (3 flags) | Tape flags marking '+' and '−' on the supply's output leads after polarity is meter-verified, and the MEASURED ohms on the resistor under test |
| 3M Solus 1000 safety glasses, clear | 1 | Worn from the moment leads are trimmed until the supply output is off and the bench is cleared |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | Bench surface under the breadboard; catches trimmed lead offcuts. No hot work today, so the X-Tronic silicone mat stays stored |
| Notebook and pen (general tools, not a project purchase) | 1 set | Circuit diagram, the set/measured/calculated table with units, and the question-prediction-acceptance-rule-stop-conditions block |
| Calculator (general tool, not a project purchase) | 1 | I = V/R, P = VI, and the percentage difference between predicted and inferred current — with the prefix written next to every number |
| Camera or phone (general tool, not a project purchase) | 1 | Wiring photograph before energizing, plus a photo of the supply's set voltage and current limit with the output still off |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **Shrouded banana-to-hook low-current test leads** — **no purchase record
  anywhere**.
  The supply's output has to reach a breadboard rail cleanly for lab step 4; no
  purpose-made low-current banana-to-hook lead set is recorded anywhere. No
  purchase. Use the bench supply's own insulated leads clipped onto the tinned
  end of a Dupont jumper landed in the rail, and keep the whole session at the
  written 3.3 V / 20 mA ceiling so lead current rating is not in question. Do
  not improvise a higher-current connection, and do not raise the limit beyond
  the day's written maximum to make a clip 'work'.
- **Klein MM450 multimeter plus 69032 and 69033 spare input fuses** — **no
  purchase record anywhere**.
  There is exactly one meter and no recorded spare input fuse, so a blown
  current-jack fuse cannot be replaced mid-plan. No purchase, and none needed
  today: the plan explicitly forbids current mode on Day 2 ('Do not use the
  DMM's current mode today; inferred current is sufficient'). Keep the red lead
  in the V/Ω jack all session and mark any directly measured current
  INCONCLUSIVE, deferred to Day 5 step 5 where the manual, fuse, range, and
  jack are checked first. The owned KAIWEETS covers every voltage and
  resistance measurement this day requires.
- **Yageo 1% axial resistors (MFR-25FBF52-1K and family)** — **no purchase
  record anywhere**.
  The exact 1% qualified parts named by the design authority would make the
  prediction-vs-measurement gap attributable to the instrument rather than the
  part. No purchase. The owned LuminologyPro kit is the learning article:
  measure the actual resistor, label it MEASURED, and build the whole
  prediction on that value rather than on '1 kΩ'. In the exit-gate write-up,
  attribute the residual difference explicitly to kit tolerance plus meter
  resolution instead of claiming a 1% part.

*Keep off the bench today.*

- Adafruit #1578 x2 and Adafruit #258 x2 LiPo packs and the Adafruit #4410
  charger — terminal-protected, connectors unmated, outside the work area; this
  is a bench-supply-only lab
- daier JST-PH 2.0 mm cables — the supply's output must never terminate in a
  battery-style connector on a day when the output is switched on
- HiLetgo MAX98357A amplifier and the Same Sky speaker — amplifier and load
  current never pass through breadboard contacts or Dupont jumpers
- ESP32-C3 SuperMini boards, the Hosyond OLED, and the INMP441 microphone — no
  module shares the powered breadboard; controller work starts on Day 6, and
  one wrong jumper at 3.3 V ends a module
- The DMM's fused current jack — the red lead stays in the V/Ω jack all day;
  never bridge a current-mode meter across the supply
- ALLECIN electrolytic and BOJACK ceramic capacitor kits — Day 4's parts; no
  stored-energy component belongs in today's single-resistor circuit
- Harris SCLF4 acid flux, X-Tronic soldering station, QWORK heat gun, SHJADE
  glue gun — nothing hot or corrosive near a powered breadboard

*Check before you start.*

1. Meter first: black lead in COM, red in the V/Ω jack, then touch the probes
   together in continuity mode and write down the lead resistance before
   measuring the 1 kΩ. Unsubtracted lead resistance is the first false source
   of a 'wrong' reading, and a red lead left in the current jack is the classic
   way to short a supply through the meter's fuse.
2. Resistor incoming check: read the colour bands, then measure the part
   UNPOWERED and record the MEASURED ohms and the tolerance band. This is
   uncalibrated bulk kit stock — if a part reads outside its band, set it aside
   and take one of the two spares rather than explaining away the error later.
3. Supply pre-power sequence with the output OFF: set 3.3 V, set the 20 mA
   limit, then verify polarity at the cable end with the DMM (wire colour is
   not proof), connect ground first and positive second, and only then switch
   the output on while watching both the voltage and current displays.
4. Breadboard continuity map before any wiring: with everything disconnected,
   find the hidden break in the 830-point board's power rails with continuity
   mode and jumper across any intended rail break. A split rail is the reason a
   correctly built circuit reads 0 V.
5. Power-margin check before energizing: confirm the part is 1/4 W stock and
   that the calculated dissipation (about 10.9 mW at 3.3 V across 1 kΩ) is
   roughly 23x below its rating. Expected draw is about 3.3 mA against a 20 mA
   limit, so any entry into constant-current mode means a wiring fault — switch
   off and investigate rather than raising the limit.

Every physical item this lab touches is already in hand; nothing about Day 2 is
blocked. No USB cable is needed — no controller is powered today, so the
plan-vs-INVENTORY data-cable conflict has no effect on this session. Keep the
resistor's measured value, the supply's set values, and the meter's mode and
range in the same table so the percentage-difference calculation can be audited
later. De-energize before touching wiring or switching to resistance/continuity
mode, and stop for any unexpected current limiting, heat, or smell. The 22
loose header pins are not consumed here; leave them bagged for the Day 11-12
reservation decision.

**Study**

- Read [Lesson 01](../edu/fundamentals/01-units-charge-voltage-current-power-energy-heat.md),
  focusing on voltage, current, resistance, power, prefixes, and the lab.
- Before touching the supply, read the voltage/resistance sections and safe
  first-power sequence in
  [Lesson 05](../edu/fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md).

**Lab**

Perform Lesson 01's battery-free 1 kΩ resistor lab:

1. With the supply output off, set `3.3 V` and a `20 mA` current limit.
2. Measure the resistor while it is unpowered.
3. Predict current and power using the measured resistance.
4. Wire and inspect the circuit, then energize it.
5. Measure the voltage across the resistor and infer current with `I = V/R`.
6. Calculate `P = VI` and compare prediction with measurement.
7. Turn the output off before touching the wiring.

Do not use the DMM's current mode today; inferred current is sufficient.

**Evidence to save**

- a circuit diagram and wiring photograph;
- a table with set, measured, and calculated values including units; and
- percentage difference between predicted and inferred current.

**Exit gate:** Every value has a unit, the measured result is reasonably
explained by tolerance and instrument limits, and the resistor rating exceeds
the calculated dissipation by a comfortable margin.

### Day 3 — Series, parallel, KVL, KCL, and divider loading

**Status:** `NOT STARTED`

**Question:** Can circuit laws predict node voltages and branch currents before
power is applied?

**Optional illustrated explanation:** [Series, parallel, rails, and divider loading](concepts/03-series-parallel-and-loading.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| LuminologyPro resistor kit, 25 values, 1/4 W | 7 x 1/4 W (1 kΩ x1, 2.2 kΩ x1, 10 kΩ x4 — three for the divider and its load plus one spare) | Lab steps 1-5 use the measured 1 kΩ and 2.2 kΩ in series and then in parallel; step 6 builds the 10 kΩ/10 kΩ divider and adds the third 10 kΩ as a load from Vout to ground |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + 1 pair of test leads + hard case + manual | Unpowered resistance measurement of all five resistors, then DC volts across each element for the KVL, KCL, and divider checks; red lead stays in the V/Ω jack all session |
| SKY TOPPOWER DC bench supply, 0-30 V / 0-5 A (PS305H) | 1, with its own insulated output leads | 3.3 V with a 10 mA limit (lower than Day 2), switched off before every one of the three reconfigurations |
| REXQualis solderless breadboards (830 + 400 point) | 1 (the 830-point board; the other three stay boxed) | Carries three successive networks — series, parallel, and loaded divider — each rebuilt with the output off |
| TODOELEC Dupont jumper kit, 10 cm | 10 wires (2 rail bridges, 2 supply landing wires, 4 node links across the three rebuilds, 2 spare) | Low-current bench wiring only; the largest network here draws about 4.8 mA |
| BOENFU 6-inch flush cutters | 1 | Trim the five resistors' leads to seat flat and stay in the intended five-hole node; component leads and wire only |
| X-Tronic bundle: tweezers | 1 pair | Move resistors between the series, parallel, and divider configurations without bending leads or springing a breadboard clip |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll (7 small flags) | Flag each resistor with its own MEASURED value and an ID (R1, R2, R3...). The three 10 kΩ parts are not identical and the 1.65 V / 1.10 V divider predictions depend on per-part measured values; also flags '+' and '−' on the supply leads after meter verification |
| 3M Solus 1000 safety glasses, clear | 1 | Worn from lead-trimming through the last power-down |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | Bench surface under the breadboard and a tray area for the labelled resistors between the three configurations |
| Notebook and pen (general tools, not a project purchase) | 1 set | Three schematics (series, parallel, loaded divider), the prediction-versus-measurement tables, and the paragraph on why parallel equivalent resistance is below either branch |
| Calculator (general tool, not a project purchase) | 1 | Predictions from measured values: series I and both drops, each parallel branch current and the KCL sum, and the unloaded/loaded divider outputs |
| Camera or phone (general tool, not a project purchase) | 1 | One wiring photograph per configuration, taken before energizing, with the labelled resistor flags legible |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **Klein MM450 multimeter plus 69032 and 69033 spare input fuses** — **no
  purchase record anywhere**.
  Only one meter is in hand, so the two parallel branch voltages must be read
  one after the other rather than simultaneously, and there is no spare input
  fuse if the current jack is ever misused. No purchase. Take the branch
  readings sequentially with the supply setting untouched between them, record
  the reading order and the supply display before and after each, and mark any
  claim that the two branches were sampled at the same instant INCONCLUSIVE.
  Keep the red lead in the V/Ω jack: Lesson 02's lab is explicit that inferring
  branch current from measured voltage and measured resistance is sufficient
  here.
- **Shrouded banana-to-hook low-current test leads** — **no purchase record
  anywhere**.
  The supply must land on the breadboard rails for three separate rebuilds; no
  purpose-made low-current lead set is recorded. No purchase. Clip the supply's
  own insulated leads to the tinned ends of two Dupont jumpers seated in the
  rail, and keep the session at 3.3 V / 10 mA so lead rating is irrelevant.
  Never improvise a heavier connection and never raise the limit above the
  day's written maximum.
- **Yageo 1% axial resistors (MFR-25FBF52-10K, -1K and family)** — **no
  purchase record anywhere**.
  The divider prediction (1.65 V unloaded, about 1.10 V loaded) is cleanest
  with matched 1% parts; the kit's three 10 kΩ resistors will differ from each
  other. No purchase. Measure and label all three 10 kΩ parts individually and
  compute the divider prediction from the measured pair rather than from '10
  kΩ'. If the loaded reading differs from 1.10 V, attribute it to the measured
  ratio and meter loading in the write-up rather than repeating the ideal-value
  prediction; the exit gate asks for the derivation, not a matched-part result.

*Keep off the bench today.*

- Adafruit #1578 x2 and Adafruit #258 x2 LiPo packs and the Adafruit #4410
  charger — terminal-protected, connectors unmated, outside the work area for
  the whole session
- daier JST-PH 2.0 mm cables — no battery-style connector on a bench where an
  output is switched on three times
- HiLetgo MAX98357A amplifier and the Same Sky speaker — no amplifier or load
  current through breadboard contacts or Dupont jumpers
- ESP32-C3 SuperMini boards, Hosyond OLED, and INMP441 microphone — the
  breadboard carries resistors only until Day 6+; a misplaced jumper during a
  reconfiguration is exactly how a module dies
- The DMM's fused current jack — all branch currents today are inferred with I
  = V/R, so the red lead never leaves the V/Ω jack
- ALLECIN electrolytic and BOJACK ceramic capacitor kits — Day 4's parts; a
  stored charge in a network being reconfigured would corrupt both the KVL and
  KCL results
- Harris SCLF4 acid flux, X-Tronic soldering station, QWORK heat gun, SHJADE
  glue gun — no hot or corrosive item near a powered breadboard

*Check before you start.*

1. Measure and label all five resistors unpowered before any wiring, writing
   each MEASURED value and an ID on its own Kapton flag. The three 10 kΩ parts
   look identical and are not; every prediction on this day (KVL residual, KCL
   sum, and both divider voltages) is computed from per-part measured values.
2. Supply pre-power with the output OFF: set 3.3 V, set the 10 mA limit (half
   of Day 2's), verify polarity at the cable end with the DMM, then connect
   ground first and positive second. Pre-compute the expected draws — series
   about 1.03 mA, parallel about 3.3 mA + 1.5 mA = 4.8 mA, loaded divider about
   0.22 mA — so that any entry into constant-current mode is unambiguous
   evidence of a wiring fault, not a normal load.
3. Topology check with continuity, output off, after each of the three
   rebuilds: confirm the series pair really shares one node in the middle and
   that the parallel pair really shares both end nodes. Two legs accidentally
   landing in the same five-hole node is the classic breadboard error that
   makes a 'series' result look like a short.
4. Meter discipline: red lead in the V/Ω jack, probes touched together first to
   note lead resistance, and every resistance or continuity reading taken with
   the supply output off. A 0.2 Ω lead offset is negligible against 1 kΩ but
   not against the millivolt-scale KVL residual you are about to interpret.
5. De-energize before every reconfiguration: confirm the output is off and the
   meter reads toward 0 V across the network before hands go on the board, per
   the plan's standing boundary and Lesson 00 rule 2.

Day 3 needs nothing that is not already in hand; the three not-owned entries
change the write-up, not the ability to run the lab. No USB cable and no
controller are involved, so the plan-vs-INVENTORY data-cable conflict does not
touch this session. Keep the labelled resistors on the mat between
configurations so the same physical part is traceable across all three
schematics — the exit gate is about deriving the equivalent-resistance formulas
and explaining divider loading, which only holds together if each measurement
is tied to a specific measured part. Authority order stands: INVENTORY.md is
the purchase record, FINAL_MATERIALS_FOR_REVIEW.md is the design authority, and
the archived MATERIALS.md / BOM.md / PURCHASE_READINESS.md sheets are
pre-purchase documents whose columns are not the current in-hand state.

**Study**

- Read [Lesson 02](../edu/fundamentals/02-dc-circuits-ohm-kirchhoff-series-parallel.md).
- Work the “Check yourself” questions before viewing their answers.

**Lab**

Use the Lesson 02 battery-free lab with measured 1 kΩ and 2.2 kΩ resistors.
Set the supply to `3.3 V` with a `10 mA` current limit.

1. Build the series network. Predict total current and both voltage drops.
2. Measure the drops and check that KVL closes within expected tolerance.
3. Power off and reconfigure the resistors in parallel.
4. Predict each branch current and their KCL sum.
5. Measure each branch voltage and infer the currents using `I = V/R`.
6. If three 10 kΩ resistors are available, make a 10 kΩ/10 kΩ divider, then
   add the third 10 kΩ as a load from `Vout` to ground. Predict `1.65 V`
   unloaded and approximately `1.10 V` loaded before measuring.

**Evidence to save**

- three schematics: series, parallel, and loaded divider;
- prediction-versus-measurement tables; and
- one paragraph explaining why parallel equivalent resistance is lower than
  either equal branch resistance.

**Exit gate:** You can derive the series and parallel equivalent-resistance
formulas from Ohm's law plus KVL or KCL, and explain divider loading without
memorizing only the formula.

### Day 4 — Components and an observable RC time constant

**Status:** `NOT STARTED`

**Question:** Does a real capacitor charge according to the predicted RC time
constant?

**Optional illustrated explanation:** [Capacitors and time](concepts/04-capacitors-and-time.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| LuminologyPro resistor kit, 25 values, 1/4 W | 2 × 100 kΩ, 1/4 W (one for the RC branch, one spare) | Sets τ = RC with the 100 µF, and is the only permitted discharge path in lab step 5. |
| ALLECIN electrolytic capacitor kit, 24 values | 2 × 100 µF rated ≥ 6.3 V (take the kit's 16 V or 25 V part if it has one); second unit is the spare if the first is reversed | The capacitor under test for lab steps 3–5. |
| BOJACK ceramic capacitor kit | 2 (one 100 nF, one 10 µF) | Unpowered side-by-side comparison for the Lesson 03 decoupling and polarity reading — ceramics are unpolarized, the electrolytic is not; these are not wired into the RC branch. |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 (plus its two test leads; keep the hard case on the bench so the meter is stowed between runs) | Measures the 100 kΩ unpowered, verifies supply-lead polarity at the cable end before connection, then reads capacitor voltage in DC volts every 10 s. |
| SKY TOPPOWER DC bench supply, 0-30 V / 0-5 A (PS305H) | 1, with its own insulated output leads | Supplies the 3.3 V step at a 10 mA current limit; the only energy source on this bench. |
| REXQualis solderless breadboards (830 + 400 point) | 1 (the 400-point board is enough) | Holds the resistor–capacitor node so nothing is hand-held while the output is on. |
| TODOELEC Dupont jumper kit, 10 cm | 4 (2 supply-to-board, 2 rail-to-row links) | Low-current wiring of the RC branch; bench use only. |
| BOENFU 6-inch flush cutters | 1 | Trims and straightens the resistor and capacitor leads so they seat fully in the breadboard; component leads and wire only, never brass. |
| X-Tronic bundle: tweezers | 1 pair | Seats and removes the electrolytic with the output off, keeping fingers off the leads of a capacitor that may still hold charge. |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | Non-conductive layout surface for loose leads and kit strips; it is a layout mat only, never a hot-work surface. |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll, 2 short flags | Flag-labels the exact resistor and capacitor used (for example R4-A and C4-A) so a repeat run measures the same two parts. |
| 3M Solus 1000 safety glasses, clear | 1 | Required for every physical lab; an incorrectly polarized electrolytic can vent. |
| GENERAL TOOL (not an INVENTORY item): notebook and pen | 1 | Prediction table for 1τ/2τ/3τ/5τ, the measured 10-second readings, and the three named sources of difference. |
| GENERAL TOOL (not an INVENTORY item): phone with stopwatch and camera | 1 | Times the 10-second sampling interval through 60 s and photographs the wired, inspected circuit before power-on. |
| GENERAL TOOL (not an INVENTORY item): computer or calculator with a spreadsheet | 1 | Computes τ = RC from the measured resistance and plots voltage versus time. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **Two-channel oscilloscope, ≥50 MHz** — **borrow or arrange access**.
  A scope is the only instrument here that could show the RC curve continuously
  rather than as six sampled points, and the only one that could show the first
  fraction of a second after the step. Do not obtain one for this session. The
  10-second DMM samples of lab step 4 are the evidence; label them MEASURED.
  Any statement about the shape between samples, about the first second, or
  about supply ripple is written into the record as INCONCLUSIVE — instrument
  not available, per the no-purchase rule.
- **Yageo 1% axial resistors (MFR-25FBF52 series) and Panasonic EEU-FC1A221SB
  qualified capacitor samples** — **no purchase record anywhere**.
  Step 1 predicts τ from R and C; the owned LuminologyPro and ALLECIN kit parts
  carry unstated tolerance, so the prediction cannot be quoted to 1%. No
  purchase. Use the resistance you actually measure in the setup checks as the
  R in τ = RC and label it MEASURED. Record the capacitance as nominal/ASSUMED
  unless your meter has a capacitance range. Kit tolerance and electrolytic
  leakage then become two of the three required 'sources of difference from the
  ideal curve' in the Evidence section rather than an unexplained error.
- **Li-ion storage / containment case** — **no purchase record anywhere**.
  Every session requires all four protected packs terminal-protected and
  outside the work area; this is the hardware that requirement assumes. No
  purchase. Keep the 2 × #1578 and 2 × #258 in their original packaging with
  connectors unmated and taped, stored in a different room from the bench, and
  write their location into the lab record during the 10-minute setup block.
  Nothing on Day 4 needs a cell, so no step is blocked.

*Keep off the bench today.*

- All four lithium cells (2 × Adafruit #1578 500 mAh, 2 × Adafruit #258 1200
  mAh) — terminal-protected, connectors unmated, outside the work area; record
  that state before the supply output is switched on
- Adafruit #4410 USB-C Micro-Lipo charger — no charging is released anywhere in
  this plan
- HiLetgo MAX98357A amplifier and the single Same Sky CES-20134-088PM speaker —
  no amplifier power without an approved fixture, and neither is used today
- Meshnology ESP32-C3 SuperMini boards, Hosyond SSD1306 OLED, and AITRIP
  INMP441 microphone — keep every semiconductor module off this bench so a live
  3.3 V supply lead cannot reach one
- daier JST-PH 2.0 mm cables — the plan states they are not used in powered
  work; do not stage them near a bench supply that is standing in for a battery
- Harris SCLF4 acid flux (stays sealed — its IPA/baking-soda neutraliser is not
  in hand) and all hot work: soldering station, heat gun, hot-glue gun
- K&S brass tube and rod, SE jeweler's saw, and diamond needle files — no
  cutting in this plan, and no brass swarf near breadboard contacts

*Check before you start.*

1. Capacitor incoming inspection: read the printed voltage rating on the
   ALLECIN 100 µF and confirm it is ≥ 6.3 V, then find the polarity stripe /
   minus band on the case. Identify negative from the case marking, not from
   lead length — the leads may have been trimmed. Reversing an aluminium
   electrolytic can damage or vent it (Lesson 03, Common mistakes).
2. Resistor identity: measure the '100 kΩ' unpowered with the meter before
   trusting the colour bands — Lesson 03 warns that a 100 kΩ and a 100 Ω look
   alike. Record the reading as MEASURED and use that value, not 100 kΩ
   nominal, in τ = RC.
3. Meter jack discipline: black lead in COM, red lead in the V/Ω jack (never
   the fused current jack — Day 4 uses no current mode), DC volts selected.
   Touch the probes together first and note the lead resistance; inspect both
   leads for cracked insulation.
4. Supply pre-power sequence (Lesson 05): output OFF, set 3.3 V, set the 10 mA
   limit, then verify polarity at the cable end with the DMM, connect ground
   first and positive second, and switch on while watching both the voltage and
   current displays.
5. Discharge plan written before power-on: after the run, the supply goes off
   and its leads come off, and the 100 kΩ stays across the capacitor as the
   only discharge path. Confirm with the meter that the capacitor has fallen
   below about 0.1 V before handling it — never short it with a wire or with
   the probe tips.

Day 4's lab is fully runnable on owned equipment; nothing here is blocked. One
documentation caution: `MATERIALS.md`, `BOM.md`, and `PURCHASE_READINESS.md`
are pre-purchase order sheets; never read their 'still to buy' or quantity
columns as the current in-hand state. `INVENTORY.md` is the purchase record and
docs/FINAL_MATERIALS_FOR_REVIEW.md is the design authority. The ALLECIN and
BOJACK kits are learning articles, not approved final-build parts — ownership
is not design approval.

**Study**

- Read the resistor, capacitor, decoupling, and RC sections of
  [Lesson 03](../edu/fundamentals/03-components-rc-diodes-mosfets-converters.md).
- Skim the diode, MOSFET, and regulator sections; return to them on Day 13.

**Lab**

Perform Lesson 03's battery-free RC lab using a known-polarity 100 µF
capacitor and 100 kΩ resistor:

1. Calculate `tau = RC = 10 s` and the expected capacitor voltage at
   `1tau`, `2tau`, `3tau`, and `5tau`.
2. Set the supply to `3.3 V` and a `10 mA` current limit with output off.
3. Confirm capacitor polarity, wire the circuit, and inspect it.
4. Record capacitor voltage every 10 seconds for 60 seconds.
5. Turn the supply off and discharge the capacitor through the 100 kΩ
   resistor, never through a direct wire short.

**Evidence to save**

- the predicted and measured voltage table;
- a hand-drawn or spreadsheet voltage-versus-time curve; and
- an explanation of at least three sources of difference from the ideal curve.

**Exit gate:** The charge and discharge behavior is reproducible and any
disagreement with the prediction is bounded or marked for repetition.

### Day 5 — Measurement as a controlled experiment

**Status:** `NOT STARTED`

**Question:** Can you choose and connect a measuring instrument without
changing the circuit dangerously?

**Optional illustrated explanation:** [Measurement and uncertainty](concepts/05-measurement-and-uncertainty.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1, with both test leads and the printed manual from the hard case | The instrument under study: continuity baseline in step 1, voltage at three points in step 2, and — only if the manual, fuse, range, and jack are all confirmed — one series current reading in the optional step 5. |
| SKY TOPPOWER DC bench supply, 0-30 V / 0-5 A (PS305H) | 1, with its own insulated output leads | Provides 3.3 V and is deliberately driven into constant-current operation in step 3, then restored to constant voltage in step 4. |
| LuminologyPro resistor kit, 25 values, 1/4 W | 6 (one 1 kΩ load, one spare 1 kΩ, plus four assorted kit values — for example 10 Ω, 2.2 kΩ, 10 kΩ, 100 kΩ — as the resistance sanity set) | The 1 kΩ is the CV/CC load; the assorted values give step 1 several known parts to measure across ranges after the continuity baseline. |
| REXQualis solderless breadboards (830 + 400 point) | 1 (the 400-point board is enough) | Holds the 1 kΩ load so the circuit is not hand-held while the supply is in CC. |
| TODOELEC Dupont jumper kit, 10 cm | 6 (2 supply-to-board, 2 rail-to-row links, 2 spare to reach the separate source / cable-end / load measurement points) | Low-current wiring only; step 2 measures voltage at three points along this run. |
| BOENFU 6-inch flush cutters | 1 | Trims resistor leads so each of the six sanity-set parts seats cleanly; wire and component leads only. |
| X-Tronic bundle: tweezers | 1 pair | Swaps resistors in and out of the breadboard with the output off between runs. |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | Non-conductive layout surface; keeps the six loose resistors separated and identifiable. |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll, 3 short flags | The Evidence section requires instrument IDs — flag the meter (MTR-A1), the supply (PSU-A1), and the 1 kΩ load sample so the record names exact units. |
| 3M Solus 1000 safety glasses, clear | 1 | Required for every physical lab. |
| GENERAL TOOL (not an INVENTORY item): notebook and pen | 1 | Holds the CV-versus-CC table and the personal pre-power checklist of no more than ten items required by the exit gate. |
| GENERAL TOOL (not an INVENTORY item): calculator or spreadsheet | 1 | Computes expected current (about 3.3 mA at 3.3 V into 1 kΩ), the resistor's dissipation, and R = V/I for comparison against the unpowered reading. |
| GENERAL TOOL (not an INVENTORY item): phone camera | 1 | Photographs the meter face during CV and during CC, and the lead-in-jack position before the optional current step. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **Klein MM450 multimeter plus 69032 and 69033 spare input fuses (no spare
  input fuse of any kind is recorded for the owned KAIWEETS either)** — **no
  purchase record anywhere**.
  Lab step 5 inserts the meter in series in the fused current jack. A wrong
  move there opens the meter's input fuse, and the same meter is required on
  Days 7-13. No purchase. Because no replacement fuse is in hand, treat a blown
  fuse as the end of multimeter work for the remaining sessions and take the
  escape the plan already offers at step 5: 'Skip this step if any detail is
  uncertain.' Do the current measurement only if the manual's fuse rating,
  range, and jack are all confirmed in writing first; otherwise omit step 5,
  record the inferred current from I = V/R, and mark the direct current
  measurement INCONCLUSIVE.
- **Shrouded banana-to-hook low-current leads and short ≥5 A banana leads** —
  **no purchase record anywhere**.
  Step 2 measures voltage at the source, the cable end, and the load; hook
  leads make the cable-end contact hands-free and repeatable. No purchase and
  no improvised leads. Use the bench supply's own insulated leads and the DMM's
  standard probes, hold each contact point deliberately, and record in the lab
  record that the cable-end measurement used factory leads and probe-tip
  contact. At about 3.3 mA no heavy lead set is needed, so no step is blocked.
- **Two-channel oscilloscope, ≥50 MHz** — **borrow or arrange access**.
  Lesson 05 is read completely today, and its oscilloscope section is about
  events a DMM's few readings per second cannot see — including how fast the
  supply collapses on the CC transition. No purchase or arrangement for this
  session. The scope section is read-only study. Record the CC transition from
  the supply's own displays and the DMM, and mark any claim about the speed,
  depth, or ringing of that transition INCONCLUSIVE — instrument not available.
- **Logic analyzer** — **no purchase record anywhere**.
  Lesson 05's logic-analyzer section is part of today's complete read, and the
  exit gate asks where each instrument connects. No purchase — the plan records
  it as an optional instrument only. Answer the Lesson 05 'Check yourself'
  question about what must be recorded with an I2C capture on paper, and note
  that the corresponding Day 8-9 measurements will be marked INCONCLUSIVE for
  the same reason.
- **Li-ion storage / containment case** — **no purchase record anywhere**.
  Standing boundary: all four protected packs must be terminal-protected and
  outside the work area for every session. No purchase. Keep the 2 × #1578 and
  2 × #258 in original packaging with connectors unmated and taped, in a
  different room, and record that state during setup. Day 5 uses no cell, so
  nothing is blocked.

*Keep off the bench today.*

- All four lithium cells (2 × Adafruit #1578, 2 × Adafruit #258) —
  terminal-protected, unmated, outside the work area, and their location
  recorded before the supply is switched on. Today's lab deliberately creates a
  current-limit fault condition; no cell is anywhere near it
- Adafruit #4410 USB-C Micro-Lipo charger — no charging is released in this
  plan
- HiLetgo MAX98357A amplifier and the Same Sky CES-20134-088PM speaker — no
  amplifier power without an approved fixture; nothing amplifier-related goes
  through breadboard contacts or Dupont jumpers
- Meshnology ESP32-C3 SuperMini boards, Hosyond OLED, and AITRIP INMP441
  microphone — step 3 intentionally drives the supply into CC and step 5 may
  put a low-resistance meter in the branch; keep every semiconductor module off
  this bench so neither can reach one
- Any LED — none is owned, and Lesson 05 states outright: do not substitute an
  LED without a series resistor. Do not improvise one into the CV/CC
  demonstration
- A second power source of any kind (USB from the computer, a wall adapter, the
  charger) — one source only for the whole session
- Harris SCLF4 acid flux, soldering station, heat gun, hot-glue gun, brass
  stock, saw, and files — Day 5 is a solderless bench-measurement session with
  no hot work and no cutting

*Check before you start.*

1. Meter and fuse gate before anything else: open the hard case, inspect both
   leads end to end for cracked insulation or exposed metal (compare against
   the condition recorded on Day 1), confirm the red lead is in the V/Ω jack,
   and read the manual's fused-current section including the fuse rating and
   the maximum time-limited current. If the fuse rating, range, or jack is
   uncertain in any way, optional step 5 is skipped rather than guessed — there
   is no spare fuse in hand.
2. Continuity baseline (Lesson 05): touch the probe tips together and record
   the lead resistance, then check one deliberately open pair, before trusting
   any low reading. Continuity and resistance modes inject their own stimulus —
   use them only on an unpowered circuit.
3. Load power check before energizing: confirm the 1 kΩ measures near nominal
   unpowered, then compute its dissipation at 3.3 V (about 10.9 mW) and confirm
   it is far below the kit's 1/4 W rating. Do the same for any substitute value
   from the sanity set.
4. Write the day's maximum current limit in the notebook before touching the
   supply knob, and set the output OFF, 3.3 V, and the starting limit before
   connecting anything. Step 3 lowers the limit below the expected 3.3 mA; the
   written maximum exists so the limit is never crept upward during the run to
   make a reading behave.
5. Confirm and record that all four cells and the #4410 charger are out of the
   work area, and that no second power source is connected, before the output
   is switched on.

Everything Day 5's five lab steps require is in hand. The one real decision
point is optional step 5: the owned KAIWEETS is the only multimeter in the
project and no spare input fuse is recorded anywhere, so the honest posture is
to run step 5 only when the manual, fuse, range, and jack have all been
confirmed, and otherwise to skip it and record the inferred current instead.
Note also that a 0-30 V / 0-5 A bench supply is coarse at the very bottom of
its current range: if the PS305H cannot resolve a limit below about 3.3 mA
cleanly, drop the load resistance (a 470 Ω or 330 Ω from the kit raises the
load current to a settable region) rather than raising the voltage, and record
the substitution. FINAL_MATERIALS names a Klein MM450 and a KORAD KA3005P as
its preferred instruments; the owned KAIWEETS and SKY TOPPOWER satisfy the same
capability for every battery-free session in this plan, and neither meter class
could close the 4.23 V charge-endpoint gate anyway — that gate needs an
ARRANGE-class calibrated logger and is not part of this plan.

**Study**

- Read [Lesson 05](../edu/fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md)
  completely.

**Lab**

1. With no powered circuit, sanity-check continuity on an open and a shorted
   pair of leads, then measure several resistors.
2. Repeat Day 2's resistor circuit and measure voltage at the source, cable
   end, and load.
3. With a 1 kΩ load, reduce the current limit below the expected 3.3 mA and
   observe that the supply enters constant-current operation and lowers its
   output voltage. Do not raise the limit beyond the day's written maximum.
4. Restore the safe setting and confirm normal constant-voltage operation.
5. Optional: only after checking the DMM manual, fuse, range, and lead jack,
   insert the meter in series for one low-current reading. Return the lead to
   the voltage jack immediately. Skip this step if any detail is uncertain.

**Evidence to save**

- instrument IDs, modes, ranges, and sanity checks;
- a table showing constant-voltage versus constant-current behavior; and
- a personal pre-power checklist of no more than ten items.

**Exit gate:** You can explain where a voltmeter, ohmmeter, and ammeter connect,
and you consistently de-energize before changing modes or wiring.

---

## Week 2 — Give the controller a heartbeat and senses

### Day 6 — Exact-part evidence and bare-controller boot

**Status:** `NOT STARTED`

**Question:** Is `MCU-A1` the expected board, and can it boot a verified image
with no external hardware attached?

**Optional illustrated explanation:** [From source code to boot](concepts/06-from-code-to-boot.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| Meshnology ESP32-C3 SuperMini dev board | 3 of the 10 (one designated MCU-A1 plus two spares, so a failed flash_id or an RGB/'Plus' variant does not end the session) | The subject of the evidence sheet and the only device powered today; it must stay bare — no display, microphone, amplifier, external power, or battery harness. |
| NEIKO digital caliper, 0-6 in (01407A) | 1 | Lesson 04 step 8: measures the complete envelope, PCB width and thickness at maximum protrusion, mounting holes, header pitch, and the USB-C connector's approach space. |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1, with both leads | Unpowered continuity only, with USB unplugged — for low-risk questions such as whether the labelled GND pins join. No powered probing today. |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll, 3 short flags | Labels the three boards MCU-A1/A2/A3 on their bags or record cards (not across the antenna end), and carries the required firmware-identity label — `CORRECTED SOURCE / MIC GPIO4`, the contract this plan uses throughout — onto the board record. |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | Non-conductive layout and photography surface for a bare board; it is a layout mat only and never a soldering surface. |
| X-Tronic bundle: tweezers | 1 pair | Lifts the board from its bag by the edges without touching the castellated pads. Note `FINAL_MATERIALS_FOR_REVIEW.md` — inspect whether this pair is ESD-marked; if it is not, treat it as a handling aid only and hold the board by its edges. |
| 3M Solus 1000 safety glasses, clear | 1 | Required for every physical lab. |
| GENERAL TOOL (not an INVENTORY item): computer with Python 3.10 or newer, Git, a free USB-A port, and network access | 1 | Creates the.venv, installs tools/requirements.txt, fetches and verifies the pinned image, and runs ports / flash-id / info / flash --dry-run / flash / monitor. On Linux, serial-group membership (often dialout) must already be sorted — do not run the flashing stack as root. |
| GENERAL TOOL (not an INVENTORY item): phone or camera | 1 | Photographs both sides of MCU-A1 next to a scale and captures every readable marking; on Day 6 it also substitutes for the magnifier (see not-owned). |
| GENERAL TOOL (not an INVENTORY item): notebook, board evidence sheet, and pen | 1 | The Lesson 04 three-column claim / evidence-label / test-needed table, the transcribed markings, the block-level schematic, and the closing release sentence. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **USB-A-to-C data cable (Rankie USB 3.0, 3-pack)** — listed under **Still
  needed** in `INVENTORY.md`.
  Every powered step of Day 6 — ports, flash-id, info, flash, and monitor —
  needs a cable with working data lines, and `INVENTORY.md` lists the Rankie
  3-pack under 'Still needed'. Verify before you start rather than assuming you
  have one, and do not buy one to stay on schedule. If any USB-A-to-C cable is
  on your desk, prove it carries data before trusting any result: plug in the
  board and confirm a serial device actually appears (python
  tools/pocket_ai_device.py ports, or the OS device log). A charge-only cable
  makes a working board look dead (`INVENTORY.md`). If no cable proves out,
  apply the no-purchase rule: complete the whole Unpowered evidence section
  (steps 1-3), create the venv, install tools/requirements.txt, and run fetch
  and verify — these are host-side and need no board. Then mark the flash-id ≥4
  MB gate, the flash transcript, and the boot log INCONCLUSIVE —
  instrument/cable not available — and do not advance to Day 7, which depends
  on a Day-6-qualified board.
- **Magnification (loupe, visor, or bench magnifier)** — **no purchase record
  anywhere**.
  Lesson 04's evidence-sheet equipment list names 'magnification and good
  light', and step 3 requires distinguishing a plain SuperMini from an
  RGB/'Plus' or U.FL variant from tiny silkscreen and IC markings. No purchase.
  Photograph every marking at the phone camera's macro/zoom setting under
  strong light and read the markings from the enlarged photo. Record explicitly
  in the evidence sheet that the inspection method was substituted, and mark
  any IC marking you cannot resolve as unknown rather than filling it in from a
  similar board photo (Lesson 04, Common mistakes).
- **Metric rule and engineer's square** — **no purchase record anywhere**.
  Lesson 04 step 1 photographs both sides 'next to a scale'; no rule is
  recorded as purchased anywhere. No purchase. Lock the owned NEIKO caliper at
  a recorded opening (for example exactly 20.00 mm) and place it in the photo
  frame as the scale reference, or measure a known object with the caliper
  first and use that. Record the reference dimension in the photo caption so
  the scale is auditable.
- **Grounded ESD mat and wrist strap** — **no purchase record anywhere**.
  Day 6 is the first session handling a bare controller, and
  `FINAL_MATERIALS_FOR_REVIEW.md` marks ESD control BUY-P0 'especially for the
  MEMS mic and bare controller'. The owned X-Tronic tweezers are not confirmed
  ESD-safe. No purchase. Handle the board by its PCB edges only, keep it on its
  anti-static bag when not in use, touch a large grounded metal object before
  each handling, avoid synthetic clothing and carpet, and write into the
  evidence sheet that ESD control was procedural only. Make no ESD claim in the
  release sentence.
- **Li-ion storage / containment case** — **no purchase record anywhere**.
  Standing boundary: all four protected packs stay terminal-protected and
  outside the work area for every session, and today's session is powered. No
  purchase. Keep the 2 × #1578 and 2 × #258 in original packaging with
  connectors unmated and taped, stored in a different room, and record their
  state before the first USB plug-in. Day 6 uses no cell — USB is the only
  power source.

*Keep off the bench today.*

- Hosyond SSD1306 OLED, AITRIP INMP441 microphone, HiLetgo MAX98357A amplifier,
  Same Sky CES-20134-088PM speaker, and QTEATAK buttons — the first flash
  needs the board bare: no display, microphone, amplifier, external power, or
  battery harness
- REXQualis breadboards, TODOELEC Dupont jumpers, and any partially built
  harness — the board is flashed bare, standing alone on the mat, with nothing
  plugged into its castellations
- SKY TOPPOWER bench supply and every other external 3.3 V or 5 V source — the
  controller's USB cable is the only power source; move the supply's leads
  physically off the bench so they cannot be reached mid-session
- All four lithium cells (2 × Adafruit #1578, 2 × Adafruit #258) and the
  Adafruit #4410 charger — terminal-protected, unmated, out of the room, state
  recorded before the first plug-in
- Soldering station, MAIYUM solder, Chip Quik flux pen, heat gun, and the 22
  owned 2.54 mm header pins — nothing is soldered today, and those 22 pins are
  earmarked for the Phase 0 bench stack, not for Day 6
- Harris SCLF4 acid flux, K&S brass tube and rod, jeweler's saw, and diamond
  files — no cutting, no acid flux near electronics, and no metal swarf near a
  bare board
- Any second serial monitor or program holding the USB serial port open — close
  them before running ports or flash

*Check before you start.*

1. Incoming board gate before anything is plugged in: inspect each of the three
   boards for an RGB LED on GPIO8, a 'Plus' marking, or a U.FL connector, and
   reject any that shows one (`INVENTORY.md`). Write down which of the ten
   boards you took and the ID you assigned it — seller name alone is not
   evidence of the variant.
2. Cable verification before diagnosing anything as broken: if any USB-A-to-C
   cable is on hand, prove it enumerates a serial device before trusting a
   'dead board' result. A charge-only cable makes a working board look dead
   (`INVENTORY.md`). If none proves out, stop at the unpowered evidence sheet
   and record INCONCLUSIVE — do not buy a cable to continue.
3. Meter discipline for the unpowered continuity checks: USB unplugged first,
   black lead in COM and red in the V/Ω jack, probe tips touched together to
   note lead resistance. Use continuity only for low-risk questions such as
   whether labelled GND pins join, and never scrape coatings, bridge pins, or
   touch a MEMS microphone port (Lesson 04).
4. Artifact gate before any write: run the verifier and require an ESP32-C3
   with at least 4 MB of flash from flash-id, plus a passing manifest, size,
   and SHA-256 check. Do not bypass a failure. `verify_source_build.py`
   currently passes and reports the diagnostics build with the amplifier
   disabled, which is the contract this plan uses; re-run it yourself rather
   than trusting this sentence, and remember that flashing at `0x0` clears
   stored Wi-Fi data.
5. Handling and boundary check: work on the non-conductive mat, hold the board
   by its edges, keep the anti-static bag on the bench, and confirm in writing
   that the cells, the charger, the bench supply, and every peripheral module
   are out of the work area before the first USB plug-in.

Day 6 is this plan's single hardest dependency point, because it is the first
session that cannot be completed with what is provably in hand. The data cable
is the whole risk: the unpowered evidence sheet, the host-tool install, and the
image fetch and verify all run without it, and only the flash-id gate, the
flash transcript, and the boot log become `INCONCLUSIVE` if no data-capable
cable proves out. Days 7 onward depend on a Day-6-qualified board, so resolve
the cable before planning past this session — but do not buy one to stay on
schedule.

Ownership of ten SuperMini boards is not design approval:
`FINAL_MATERIALS_FOR_REVIEW.md` rates the generic SuperMini 60% and names a
different part as preferred. Qualify a board with `esptool flash_id`, not with
the product listing.

**Study**

- Read the identity, pinout, datasheet, and connector sections of
  [Lesson 04](../edu/fundamentals/04-boards-schematics-datasheets-and-connectors.md).
- Follow the controller setup in the
  [USB prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md).
- Read the source-status and pin-map sections of the
  [firmware guide](../firmware/README.md).

**Unpowered evidence**

1. Photograph both sides of `MCU-A1` next to a scale.
2. Record every visible marking, physical pin label, dimensions, antenna end,
   buttons, and connector.
3. Confirm it is a plain ESP32-C3 SuperMini rather than an RGB/Plus or U.FL
   variant. Do not infer clone details from the seller name alone.

**Host setup and lab**

```bash
firmware/scripts/setup.sh
. firmware/.work/esp-idf/export.sh
firmware/scripts/build.sh
python3 firmware/scripts/verify_source_build.py
python3 tools/pocket_ai_device.py ports
python3 -m esptool --chip esp32c3 --port <PORT> flash-id
firmware/scripts/flash.sh <PORT> --dry-run
```

Replace `<PORT>` with the explicitly observed USB serial port. Require an
ESP32-C3 and at least 4 MB of flash. If that gate passes, flash and monitor:

```bash
firmware/scripts/flash.sh <PORT> --monitor
```

Flashing at `0x0` replaces the complete image and clears stored Wi-Fi data.
For this initial smoke test, keep the board bare: no display, microphone,
amplifier, external power, or battery harness. Later reflashes may keep the
tested USB-powered button/OLED/microphone connected under the quickstart's
single-source wiring rule.

The default build is the offline diagnostics image. It does not provision
Wi-Fi or send audio to a service. On a bare board, absent OLED and microphone
results are expected; success today is a stable diagnostic log. Do not bypass
manifest or digest failures. The first SDK setup/build needs internet access
and may take a substantial part of this session; count that as useful setup
work and continue the hardware portion next session if necessary.

**Before Day 7:** inspect the controller, OLED, and microphone headers. If they
are loose or absent, complete Day 11's solder practice now, then follow the
[quickstart header step](../docs/PROTOTYPE_QUICKSTART.md#prepare-reliable-headers)
to solder and inspect the required headers with USB disconnected. Count that
as the completed Day 11 session later. Do not wedge loose pins into unsoldered
holes to make an electrical connection.

**Evidence to save**

- board evidence sheet and photographs;
- flash ID, image digest, explicit port, flash transcript, and complete boot
  log; and
- a label on the board record: `SOURCE DIAGNOSTICS / MIC GPIO4 / 16 kHz`.

**Exit gate:** The exact board has at least 4 MB flash, the selected artifact
passes its verifier, and the controller produces a stable, understood boot log.

### Day 7 — Digital logic and the action button

**Status:** `NOT STARTED`

**Question:** Can one input have a defined released state and a repeatable
active-low pressed state?

**Optional illustrated explanation:** [GPIO and buttons](concepts/07-gpio-and-buttons.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| Meshnology ESP32-C3 SuperMini dev board | 2 (MCU-A1 from Day 6, plus 1 unopened spare from the 10-pack) | MCU-A1 carries the GPIO10 input under test; the spare exists only so a board that fails re-qualification with `esptool flash_id` is discarded, not debugged |
| QTEATAK 6x6 mm tactile push buttons with caps | 3 switches + 1 white cap | lab step 1 identifies the true switch terminals by continuity on all three; the best one is wired and the others stay spare (420 in the kit) |
| LuminologyPro resistor kit, 25 values, 1/4 W | 2 (one 10 kΩ, one 1 kΩ) | the 10 kΩ is the external GPIO10 pull-up to 3.3 V for the reviewed active-low circuit; the 1 kΩ stays unfitted because the LED it would feed is not owned |
| BOJACK ceramic capacitor kit | 1 (one 100 nF) | the documented GPIO10 debounce cap (`WIRING_AND_ASSEMBLY.md`) — fit it only if step 2's drawn circuit includes it, and change one variable at a time |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + its 2 test leads + the hard case | unpowered continuity to find the switch pair, then DC volts GPIO10-to-GND released/pressed and the drop across the 10 kΩ for the current check |
| REXQualis solderless breadboards (830 + 400 point) | 1 (the 400-point board is enough) | holds MCU-A1, the pull-up, and the button; low-current logic only |
| TODOELEC Dupont jumper kit, 10 cm | 5 short jumpers (3.3 V to rail, GND to rail, GPIO10 to the pull-up node, and two button legs) | the only wiring on the bench today; bench low-current use only |
| 2.54 mm male breakaway header pins | up to 16 pins (SuperMini pad count) — stage them only to confirm the count, do not solder during this session | MCU-A1 cannot sit in a breadboard without attached pins; stock is 22 pins total, so decide the split before spending any |
| X-Tronic bundle: tweezers | 1 pair | seating the 6x6 tactile switch and short jumpers without bending pins |
| BOENFU 6-inch flush cutters | 1 | trimming the 10 kΩ leads to breadboard length — wire and component leads only |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | non-conductive layout surface for the board, switches, and loose parts (never a soldering surface) |
| 3M Solus 1000 safety glasses, clear | 1 | required for every physical lab, and lead trimming throws clippings |
| Computer with Python venv and a free USB-A port (general tool — no purchase record) | 1 | runs the monitor/log for released and pressed states, or hosts the written GPIO test program if flashing is not possible |
| Camera or phone (general tool — no purchase record) | 1 | the wiring photograph required in Evidence to save |
| Notebook, pen, calculator, and paper labels/masking tape (general tools — no purchase record) | 1 each | the truth table, the 3.3 V / 10 kΩ = 0.33 mA and 1.09 mW calculation, and re-labelling MCU-A1 with its firmware contract |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **USB-A-to-C data cable with working data lines (Rankie 3-pack, or any
  proven-data cable)** — listed under **Still needed** in `INVENTORY.md`.
  lab step 5 connects USB and observes/logs the released and pressed states;
  nothing on this day can be flashed or monitored without it. `INVENTORY.md`
  lists the Rankie 3-pack under 'Still needed', so treat it as not in hand. If
  any
  USB-A-to-C cable is on your own bench, prove it enumerates a serial port
  before trusting a result; a charge-only cable makes a working board look
  dead. With no data cable: complete steps 1-4 and 6 (continuity terminal ID,
  the drawn active-low circuit, the GPIO10/GPIO9 assignment review, the
  single-pull decision), do the Lesson 07 closed-button current and power
  calculation on paper, write the smallest GPIO test program as the software
  exercise the plan already allows without flashing it, and mark lab step 5 and
  the ten-press exit gate INCONCLUSIVE.
- **Discrete LED** — **no purchase record anywhere**.
  The optional Lesson 07 GPIO-output exercise drives an LED through a 1 kΩ
  series resistor, and this plan already forbids buying one for this session. Run the input half only: leave the 1 kΩ
  in the kit, record the push-pull output / open-drain / Hi-Z distinction as a
  written exercise against the Lesson 07 mode table, and mark the LED-output
  extension NOT ATTEMPTED (not failed). Never connect an LED without its series
  resistor if one does turn up.
- **Grounded ESD mat and wrist strap** — **no purchase record anywhere**.
  today is the first session that handles a bare controller out of its bag and
  pushes it into a breadboard No lab step is held for this. Work on the
  WORKLION mat, touch a grounded metal object before picking up MCU-A1, handle
  it by the board edges, and write one line in the lab record stating that Day
  7 ran with no ESD control (`FINAL_MATERIALS_FOR_REVIEW.md`). Do not defer the
  session to acquire one.

*Keep off the bench today.*

- All four lithium cells (2x Adafruit #1578, 2x Adafruit #258) —
  terminal-protected, connectors unmated, outside the work area
- Adafruit #4410 USB-C Micro-Lipo charger
- SKY TOPPOWER PS305H bench supply and every other external 3.3 V or 5 V source
  — USB is the only power source today
- Hosyond SSD1306 OLED and AITRIP INMP441 microphone — the button is the only
  new variable on this board
- HiLetgo MAX98357A amplifier and Same Sky CES-20134-088PM speaker
- daier JST-PH pigtails and Chanzon SPDT slide switch (not used in powered work
  in this plan)
- Any wire, resistor, or cap on GPIO9 — it stays exclusively ROM BOOT/recovery
- X-Tronic soldering station, QWORK heat gun, SHJADE hot glue gun — no hot work
  in a Day 7 session
- Harris SCLF4 acid flux (never near electronics, and it cannot be neutralised:
  IPA/baking soda are not in hand)
- K&S brass tube and rod — keep metal stock off a powered bench

*Check before you start.*

1. Cable check first: no USB-A-to-C data cable is established as in hand. If
   you find one, confirm it enumerates a serial port on the host before you
   trust any pressed/released observation.
2. Meter setup: red lead in the VΩ/continuity jack, NOT the fused current jack;
   short the leads to confirm the continuity beep; leave the fused current jack
   unused all session (never a current-mode meter across a source).
3. Measure the pull-up on the meter's resistance range before wiring it — the
   LuminologyPro kit is a 25-value assortment and the colour band is not the
   evidence; expect ~10 kΩ.
4. Breadboard incoming check with USB disconnected: confirm each power rail is
   continuous end to end and that the two rails are not bridged (`INVENTORY.md`
   — check split power rails before use).
5. Header check: MCU-A1 needs attached pins to sit in a breadboard. Stock is 22
   loose pins against ~16 SuperMini pads, and soldering is not taught until Day
   11 — if the pins are loose, mark the powered step HOLD rather than
   press-fitting a contact.

Day 7 is the first session that puts the qualified controller into a
breadboard, and two prerequisites decide whether it runs at all: a proven-data
USB cable and attached header pins. Both are verify-before-you-start items, not
assumed possessions. Fit either the
firmware's internal pull OR the external 10 kΩ, never both — two enabled pulls
are in parallel (10 kΩ || 45 kΩ ≈ 8.2 kΩ), and the plan requires the choice to
be explicit. Header quantity is a live conflict: `INVENTORY.md` earmarks all 22
pins for making the Phase 0 bench stack reversible, while Days 11-12 treat
header as practice stock — reserve what Days 8-9 need (4 for the OLED, 6 for
the mic) in a labelled bag before spending any. Never read docs/MATERIALS.md,
docs/BOM.md, or docs/PURCHASE_READINESS.md 'still to buy' columns as the
current in-hand state; INVENTORY.md is the purchase record and
FINAL_MATERIALS_FOR_REVIEW.md is the design authority.

**Study**

- Read [Lesson 07](../edu/fundamentals/07-digital-logic-gpio-pullups-boot-straps.md),
  focusing on GPIO modes, floating inputs, pull resistors, and boot straps.

**Lab**

1. With USB disconnected, identify the exact button terminals using
   continuity mode.
2. Draw the intended active-low circuit before wiring it.
3. Use GPIO10 for the project action button. Keep GPIO9 available exclusively
   for ROM BOOT/recovery.
4. Wire the button between GPIO10 and GND using the
   [quickstart map](../docs/PROTOTYPE_QUICKSTART.md#add-the-button-and-oled).
   The diagnostic firmware enables the input's internal pull-up.
5. Connect USB and observe/log released and pressed states. Test multiple
   presses without changing wiring.
6. Disconnect USB before altering or removing the circuit.

Use the source diagnostics image from Day 6. Each press is reported in its
serial output; with the OLED added on Day 8, a press also switches its pixel
test between all-on and all-off.

If a discrete LED is already owned, the Lesson 07 LED-output exercise is an
optional extension using its 1 kΩ series resistor. Do not buy an LED for this
session and do not connect one without a resistor.

**Evidence to save**

- button wiring diagram and photograph;
- released/pressed truth table with measured or logged states; and
- recovery-control notes proving GPIO9 was not repurposed.

**Exit gate:** Ten presses produce the expected state transition, reset still
works, and no boot mode is entered unintentionally.

### Day 8 — I2C and the OLED

**Status:** `NOT STARTED`

**Question:** Does one exact OLED acknowledge at the address and voltage
expected by the selected firmware?

**Optional illustrated explanation:** [I2C and the OLED](concepts/08-i2c-and-the-oled.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| Meshnology ESP32-C3 SuperMini dev board | 1 (MCU-A1, still carrying its Day 6 firmware-contract label) | the I2C controller; GPIO20 = SCL, GPIO21 = SDA |
| Hosyond SSD1306 OLED, 0.96 in 128x64 I2C, white | 2 of the 5-pack (OLED-A1 under test, 1 unopened as the discriminating swap) | OLED-A1 is the target under test; the second board is the one-variable swap if A1 NACKs at both addresses — five in the pack means a bad module is replaced, not debugged forever |
| QTEATAK 6x6 mm tactile push button with cap | 1 (the Day 7-qualified button, or add it with USB disconnected if it is not still wired) | Lab step 5 presses the GPIO10 button to toggle all-pixels-on and all-pixels-off, so the display test has an input to drive it |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + its 2 test leads + the hard case | unpowered short sweep and GPIO20/21 continuity, the module's fitted pull-up resistance, then the OLED rail and idle SDA/SCL levels once USB is connected |
| REXQualis solderless breadboards (830 + 400 point) | 1 (830-point, so MCU-A1 and OLED-A1 sit on one board with short jumpers) | holds both modules on a common ground with the shortest practical bus wiring |
| TODOELEC Dupont jumper kit, 10 cm | 4 of the shortest jumpers (GND, 3.3 V, GPIO20 to SCL, GPIO21 to SDA) | the only four connections permitted today; short wires keep bus capacitance and rise time in range |
| 2.54 mm male breakaway header pins | 4 pins for the OLED's strip, only if it did not arrive factory-soldered | the OLED cannot be breadboarded on loose pins; stage them to confirm the count against the 22-pin total, do not solder in a Day 8 session |
| NEIKO digital caliper, 0-6 in (01407A) | 1 | lab step 1 requires OLED-A1's measured dimensions on its evidence sheet; listed module sizes are frequently wrong |
| X-Tronic bundle: tweezers | 1 pair | handling the glass-fronted OLED carrier and seating jumpers without touching the flex tail |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | non-conductive layout and photography surface for the both-sides evidence photographs |
| 3M Solus 1000 safety glasses, clear | 1 | required for every physical lab |
| Computer with Python venv, esptool, and a free USB-A port (general tool — no purchase record) | 1 | runs the address scan and the initialization/all-pixel test, and captures the serial output |
| Camera or phone (general tool — no purchase record) | 1 | both-side module photographs, the silkscreen close-up, and the lit-display photograph required in Evidence to save |
| Notebook, pen, calculator, and paper labels/masking tape (general tools — no purchase record) | 1 each | the physical-to-logical pin map, the parallel pull-up and t_r ≈ 0.8473 × R × C calculation, and labelling OLED-A1 |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **USB-A-to-C data cable with working data lines (Rankie 3-pack, or any
  proven-data cable)** — listed under **Still needed** in `INVENTORY.md`.
  lab steps 5 and 6 measure the powered OLED rail, scan the address, run the
  all-pixel test, and check headless fallback. `INVENTORY.md` lists the cable
  under 'Still needed', so verify before you start. If
  any USB-A-to-C cable is on your own bench, prove it enumerates a serial port
  first; a charge-only cable makes a working board look dead. With no data
  cable: complete lab step 1 (the OLED-A1 evidence sheet with photographs,
  markings, physical pin order, measured dimensions, and the supply-voltage
  evidence), step 3's wiring built unpowered, step 4's short and reversal
  inspection, plus the pull-up inventory and the rise-time calculation, then
  mark steps 5-6 and the cold-start exit gate INCONCLUSIVE.
- **Logic analyzer** — **no purchase record anywhere**.
  Lesson 08's debug tree step 6 and the plan's optional Day 8 instrument
  capture SDA/SCL to confirm START, the unshifted address decode, the ACK
  clocks, and STOP The plan says omit rather than buy. Substitute the scanner's
  serial output as the evidence that something ACKed, and write explicitly that
  an ACK proves only that a powered target answered at that address — not that
  it is an SSD1306, and not that START/ACK/STOP timing was observed. Mark the
  protocol-decode confirmation INCONCLUSIVE.
- **Two-channel oscilloscope, >=50 MHz** — **borrow or arrange access**.
  Lesson 08 step 7 says an analog rise-time measurement is required before any
  Fast-mode (400 kHz) compliance claim; a decode alone does not measure analog
  margin Do the rise time as a calculation only: inventory the pull-ups
  actually fitted to OLED-A1, compute their parallel value with the ESP32-C3's
  ~45 kΩ internal pull-up, and evaluate t_r ≈ 0.8473 × R × C against the 1000
  ns Standard-mode and 300 ns Fast-mode limits. Label the result CALCULATED,
  run the scan at 100 kHz first, and mark any 400 kHz timing-margin claim
  INCONCLUSIVE.
- **Magnification (loupe, visor, or bench magnifier)** — **no purchase record
  anywhere**.
  lab step 1 turns on reading fine silkscreen — Hosyond ships GND-VCC-SCL-SDA
  and VCC-GND-SCL-SDA on identical-looking boards Photograph the silkscreen
  with a phone camera at macro/zoom and read the enlarged image; record that
  the inspection method was substituted. If the pin order or supply voltage
  still cannot be established from the received board, stop at the unpowered
  evidence sheet and mark the powered test HOLD — do not energise a carrier
  whose pin order is unresolved.

*Keep off the bench today.*

- AITRIP INMP441 microphone — lab step 2 keeps the microphone, amplifier, and
  speaker absent from this setup
- HiLetgo MAX98357A amplifier and Same Sky CES-20134-088PM speaker
- All four lithium cells (2x #1578, 2x #258) and the Adafruit #4410 charger —
  terminal-protected and outside the work area
- SKY TOPPOWER PS305H bench supply and every other external converter or 3.3
  V/5 V source
- daier JST-PH pigtails and Chanzon SPDT slide switch
- Loose resistors on the I2C bus — nothing is fitted to SDA/SCL on Day 8 until
  the pull-up inventory and calculation say so (Lesson 08: do not add resistors
  blindly)
- X-Tronic soldering station, QWORK heat gun, SHJADE hot glue gun — the OLED
  flex tail is heat-sensitive and no hot work belongs in this session
- Harris SCLF4 acid flux and Chip Quik flux pen — no flux near the display
  glass or its tail
- K&S brass tube and rod

*Check before you start.*

1. Read and photograph the received OLED's silkscreen pin order before a single
   wire goes in: vendors ship GND-VCC-SCL-SDA and VCC-GND-SCL-SDA on
   identical-looking boards (`INVENTORY.md`). Write the physical-to-logical map
   on the evidence sheet; if it cannot be established, the day ends at the
   evidence sheet and the powered test is HOLD.
2. Cable check: no USB-A-to-C data cable is established as in hand. If you have
   one, prove it enumerates a serial port before trusting a NACK as a hardware
   result.
3. Unpowered short sweep with the meter before USB: 3.3 V-to-GND, SDA-to-GND,
   and SCL-to-GND on the assembled breadboard, plus continuity from GPIO20 to
   SCL and GPIO21 to SDA. Turn power off before every resistance or continuity
   measurement.
4. Pull-up inventory: with the module off the bus and unpowered, measure
   OLED-A1's fitted SDA and SCL pull-ups and compute the parallel equivalent
   with the ~45 kΩ internal pull-up before choosing bus speed.
5. Header check: the OLED's 4-pin strip must already be attached. Loose pins
   mean HOLD, not a press-fit contact — and reserve those 4 pins out of the
   22-pin total before Day 11-12 practice consumes them.

Address discipline is the trap of the day: pass the unshifted 7-bit 0x3C or
0x3D to the API, never the 0x78/0x7A write bytes a logic-analyzer view shows.
Scan slowly (100 kHz) first — passing slowly and failing at the configured 400
kHz points at rise time and capacitance, not at address selection. The owned
Hosyond module is a learning article: `FINAL_MATERIALS_FOR_REVIEW.md` classes
this exact ASIN as a HOLD alternative at 55% against the unowned preferred
Adafruit #326, so a working scan today promotes nothing to a final part. Keep
the second OLED sealed until A1 has actually failed a defined test, and change
one condition at a time between runs.

**Study**

- Read [Lesson 08](../edu/fundamentals/08-i2c-and-the-oled.md).

**Lab**

1. Create an evidence sheet for `OLED-A1`. Record both-side photographs,
   markings, physical pin order, dimensions, and the evidence for its supply
   voltage. Similar-looking OLED carriers can swap VCC and GND positions.
2. Keep the battery, converter, microphone, amplifier, and speaker absent.
3. With USB disconnected, connect the OLED to controller GND and 3.3 V output,
   GPIO20/SCL, and GPIO21/SDA using the
   [quickstart map](../docs/PROTOTYPE_QUICKSTART.md#add-the-button-and-oled).
   Verify the carrier supports 3.3 V and identify its actual pin order first.
4. Inspect for reversed power and shorts before connecting USB.
5. Measure the OLED rail and read the address in the diagnostic boot log.
   Press the GPIO10 button to switch between all pixels on and all pixels off.
   Add the already-tested button with USB disconnected if it is absent.
6. Power off, remove the display, and confirm the corrected-source firmware's
   headless behavior if that is the selected contract.

If the carrier's voltage or pin order cannot be established, stop at its
unpowered evidence sheet and mark the powered test `HOLD`.

**Evidence to save**

- exact physical-to-logical pin map;
- observed `0x3C` or `0x3D` address and relevant serial output;
- display photograph; and
- failure/headless observation if tested.

**Exit gate:** The display works repeatedly from a cold USB start, or the
failure has been reduced to a specific next discriminating test.

### Day 9 — I2S clocks and microphone input

**Status:** `NOT STARTED`

**Question:** Does the exact microphone produce plausible data using the
selected firmware's clock, data pin, and slot contract?

**Optional illustrated explanation:** [Sampling and I2S](concepts/09-sampling-and-i2s.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| Meshnology ESP32-C3 SuperMini dev board | 1 (MCU-A1, labelled CORRECTED SOURCE / MIC GPIO4 / 16 kHz) | drives WS on GPIO1 and BCLK on GPIO2 and reads mic data on GPIO4 |
| AITRIP INMP441 I2S MEMS microphone | 1 (MIC-A1) — the other four stay sealed in their bag | the carrier under test; do not open a spare unless MIC-A1 is proven dead, because an exposed acoustic port can be contaminated permanently |
| LuminologyPro resistor kit, 25 values, 1/4 W | 2 (one 10 kΩ, one 100 kΩ) | 10 kΩ pull-up to 3.3 V on GPIO2 because the I2S bit clock shares a boot-strap pin, and 100 kΩ pull-down on GPIO4 mic data (`WIRING_AND_ASSEMBLY.md`, `INVENTORY.md`) |
| BOJACK ceramic capacitor kit | 1 (one 100 nF) | the VDD bypass close to the microphone that Lesson 09 cites from the datasheet — fit it only if the received carrier does not already have one; inspect the PCB before adding a duplicate |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + its 2 test leads + the hard case | unpowered pin-order continuity on the carrier, verifying L/R is tied to GND, then the 3.3 V rail measured at the microphone and its MIN/MAX watch as the stand-in for the unavailable scope |
| REXQualis solderless breadboards (830 + 400 point) | 1 (830-point) | holds MCU-A1 and MIC-A1 on a common ground with the shortest clock and data stubs |
| TODOELEC Dupont jumper kit, 10 cm | 6 of the shortest jumpers (3.3 V to VDD, GND to GND, GND to L/R, GPIO1 to WS, GPIO2 to SCK, GPIO4 to SD) | the complete permitted low-current microphone fixture; short stubs because BCLK is a megahertz-class edge |
| 2.54 mm male breakaway header pins | 6 pins for the INMP441 strip, only if it did not arrive factory-soldered | the mic carrier cannot be breadboarded on loose pins; stage them to confirm the count, do not solder in a Day 9 session |
| NEIKO digital caliper, 0-6 in (01407A) | 1 | lab step 1 requires MIC-A1's measured dimensions on its evidence sheet |
| X-Tronic bundle: tweezers | 1 pair | handling MIC-A1 by its board edges and seating jumpers without ever touching or covering the acoustic port |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | clean non-conductive layout and photography surface; keep it free of solder debris and adhesive residue near the mic |
| 3M Solus 1000 safety glasses, clear | 1 | required for every physical lab |
| Computer with Python venv and a free USB-A port (general tool — no purchase record) | 1 | records raw samples or firmware diagnostics during silence, speech, and a gentle tone, and stores the sample logs |
| Camera or phone (general tool — no purchase record) | 1 | both-side carrier photographs, the wiring photograph, and the phone's tone generator for the gentle-tone run in lab step 5 |
| Notebook, pen, calculator, and paper labels/masking tape (general tools — no purchase record) | 1 each | the pin map, the 16,000 x 2 x 32 = 1.024 MHz clock calculation, and the firmware-contract label on MIC-A1 |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **USB-A-to-C data cable with working data lines (Rankie 3-pack, or any
  proven-data cable)** — listed under **Still needed** in `INVENTORY.md`.
  lab step 5 reconnects USB and records samples or firmware diagnostics during
  silence, speech, and a tone. `INVENTORY.md` lists the cable under 'Still
  needed', so verify before you start: if any USB-A-to-C cable is on your own
  bench, prove it enumerates a serial port first. With no
  data cable: complete lab steps 1-4 — the MIC-A1 evidence sheet with verified
  carrier pin order and supply voltage, the expected-clock calculation 16,000 x
  2 x 32 = 1.024 MHz, the written confirmation that data goes to GPIO4 and
  never also GPIO8, and the unpowered fixture built and inspected — then mark
  step 5 and the silence-versus-speech exit gate INCONCLUSIVE. The plan states
  this outcome explicitly: an unpowered evidence sheet plus a source-level
  signal trace is a valid HOLD.
- **Logic analyzer** — **no purchase record anywhere**.
  lab step 6 and Lesson 09 Stage 1 measure WS and BCLK and count the configured
  clocks per WS cycle The plan instructs omitting it rather than buying. Trace
  the clock path in the firmware source instead, keep 1.024 MHz labelled
  CALCULATED and never MEASURED, and mark the waveform and rate confirmation
  INCONCLUSIVE exactly as plan step 6 directs. Do not substitute a DMM
  frequency reading as proof of I2S framing.
- **Two-channel oscilloscope, >=50 MHz** — **borrow or arrange access**.
  Lesson 09 uses a scope to assess rail droop and digital edge quality on the
  clock stubs Lesson 09 names the substitute directly: use the KAIWEETS in
  MIN/MAX to watch the 3.3 V rail at the microphone across silence, speech, and
  tone runs, and skip all waveform claims. Record edge quality as unmeasured.
  No speaker-output waveform work exists on this day anyway — the amplifier is
  absent.
- **Magnification (loupe, visor, or bench magnifier)** — **no purchase record
  anywhere**.
  lab step 1 verifies the carrier's physical pin order from fine silkscreen,
  and the IC family name does not prove the breakout layout Photograph the
  silkscreen at macro/zoom and read the enlarged image, cross-checking every
  pad with unpowered continuity on the meter; record that the inspection method
  was substituted. If the pin order or permitted supply remains unresolved, do
  not energise the carrier — end at the evidence sheet and mark the powered
  test HOLD.
- **Grounded ESD mat and wrist strap** — **no purchase record anywhere**.
  `FINAL_MATERIALS_FOR_REVIEW.md` names the MEMS microphone and the bare
  controller as the specific parts needing ESD control, and today handles both
  No lab step is held for this. Ground yourself on a metal object before
  opening the mic's bag, handle MIC-A1 by its board edges on the mat, leave the
  other four microphones sealed, and record one line stating that Day 9 ran
  with no ESD control. Do not delay the session to acquire one.

*Keep off the bench today.*

- HiLetgo MAX98357A amplifier and Same Sky CES-20134-088PM speaker — explicitly
  excluded ; no amplifier is powered anywhere in this plan without an approved
  fixture
- All four lithium cells (2x #1578, 2x #258) and the Adafruit #4410 charger —
  terminal-protected and outside the work area
- SKY TOPPOWER PS305H bench supply and every other external 3.3 V/5 V source or
  converter — do not invent a 3.3 V injection point (Lesson 09 Stage 2)
- Hosyond SSD1306 OLED — the microphone fixture is the only thing on the bus
  today
- Chip Quik CQ4LF flux pen and Harris SCLF4 acid flux — flux near the acoustic
  port is permanent contamination
- QWORK heat gun, X-Tronic soldering station, and SHJADE hot glue gun — no hot
  air, solder fumes, or adhesive anywhere near the port
- Any solvent, IPA, or can of compressed air
- daier JST-PH pigtails, Chanzon SPDT slide switch, and K&S brass tube and rod
- Any wire on GPIO8 — the vendor contract's mic pin; never wired at the same
  time as GPIO4

*Check before you start.*

1. Verify every INMP441 pad against the received silkscreen and confirm it with
   unpowered continuity before wiring: the IC family name does not prove the
   breakout layout. L/R must be tied LOW to select the left slot the firmware
   expects.
2. Contract check: confirm MCU-A1's label reads CORRECTED SOURCE / MIC GPIO4 /
   16 kHz, and wire SD to GPIO4 only. The historical vendor image uses GPIO8 at
   24 kHz — never combine the two contracts on one harness.
3. Strap check: GPIO2 is both the I2S bit clock and a sampled boot strap.
   Measure the 10 kΩ on the meter's resistance range, fit it as a pull-up to
   3.3 V, and confirm nothing on the mic stub can hold GPIO2 LOW through the 3
   ms strap window after reset.
4. Measure the 100 kΩ GPIO4 pull-down before fitting it, and confirm the
   microphone's VDD lands on the 3.3 V pin and not the 5 V pad — the ESP32-C3
   is a 3.3 V part with no 5 V-tolerant GPIO.
5. Port hygiene before anything is unbagged: no flux pen, acid flux, IPA, glue,
   heat gun, or compressed air on the bench; handle MIC-A1 with tweezers by its
   edges and never set it face-down on the mat (`INVENTORY.md` — contaminating
   the port is permanent).

The single load-bearing calculation is BCLK = 16,000 x 2 x 32 = 1.024 MHz, and
without a logic analyzer it stays CALCULATED — the exit gate is met instead by
distinguishable, non-stuck sample data across silence, speech, and tone. Check
the recorded samples for a stuck value, clipping, wrong byte alignment, and
wrong slot before declaring a pass; an unexplained success is not a pass. The
owned AITRIP INMP441 is a learning article: `FINAL_MATERIALS_FOR_REVIEW.md`
classes the generic INMP441 as HOLD at 50% against the unowned preferred
Adafruit #6049, so plausible data today promotes nothing to a final part.
Reserve the 6 header pins the mic needs out of the 22-pin total before Day
11-12 practice consumes them, and treat docs/MATERIALS.md, docs/BOM.md, and
docs/PURCHASE_READINESS.md as pre-purchase order sheets, never as the current
in-hand state.

**Study**

- Read [Lesson 09](../edu/fundamentals/09-i2s-sampling-and-digital-audio.md)
  through Stage 2 of its safe staged lab.

**Lab**

1. Create an evidence sheet for `MIC-A1`. Verify the carrier's physical pin
   order and voltage; the IC family name does not prove the breakout layout.
2. Calculate the expected clock from sample rate, slots, and bits per slot.
   For corrected source, show `16,000 x 2 x 32 = 1.024 MHz`.
3. Confirm the source contract again: microphone data is GPIO4, at 16 kHz.
4. With USB disconnected, connect the owned INMP441 using the
   [quickstart microphone map](../docs/PROTOTYPE_QUICKSTART.md#add-the-microphone):
   VDD to controller 3.3 V output, GND and L/R to GND, SCK to GPIO2, WS to GPIO1,
   and SD to GPIO4. Check the labels on this exact carrier first.
5. Reconnect USB and capture the diagnostic minimum, maximum, and RMS sample
   values during silence and normal speech. They should change with sound;
   record stuck/clipped/read-failure indications as well. This is an offline
   serial test and requires no speaker or cloud service.
6. If a suitable logic analyzer is already available, measure WS and BCLK.
   Otherwise mark waveform/rate confirmation `INCONCLUSIVE`; do not purchase an
   instrument merely to complete the day.

If the received carrier's pin order or 3.3 V compatibility cannot be identified,
resolve that before connecting it. Use the unpowered/source-trace portion while
that particular question is open.

**Evidence to save**

- microphone pin map and firmware-contract label;
- expected clock calculation;
- sample/log observations; and
- measured clock values or an explicit instrument limitation.

**Exit gate:** Silence and speech produce distinguishable, non-stuck data over
several trials. A missing instrument may leave timing accuracy inconclusive,
but mark microphone functionality unverified if this data test has not passed.

### Day 10 — Class-D, BTL, speaker limits, and the audio gate

**Status:** `NOT STARTED`

**Question:** What must be true before it is safe and meaningful to power the
amplifier and speaker?

**Optional illustrated explanation:** [Speakers and amplifiers](concepts/10-speakers-and-amplifiers.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| HiLetgo MAX98357A I2S class-D amplifier | 1 of the 3 in hand (label it AMP-A1; leave the other 2 bagged and untouched) | Lab steps 1-3: photograph, trace supply/GND/I2S/SD-MODE/OUT+/OUT- from silkscreen, and prove neither output pad is continuous with the board's GND pad. |
| Same Sky CES-20134-088PM speaker, 8 ohm 0.8 W, factory-enclosed | 1 — the only unit in hand, no spare and no A/B partner | Lab steps 1 and 4: identify it and measure voice-coil DC resistance on its 60 mm factory leads (leads are never cut and never soldered to the amplifier today). |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + its 2 test leads, taken out of the hard case and inspected | Continuity mode for step 3 (speaker terminal vs circuit ground) and resistance mode for step 4 (speaker DC resistance); red lead stays in the voltage/ohms jack all session. |
| NEIKO digital caliper, 0-6 in (01407A) | 1 | Lesson 10 safe-lab step 1: record the speaker body's real measured dimensions (nominally 20 x 13 x 4.87 mm) and the amplifier board outline onto the evidence sheets. |
| X-Tronic bundle: helping hands | 1 of the 2 (clips only — the iron stays off the bench today) | Hold the small amplifier board steady so both DMM probes can land on pads without pressing the module against the bench. |
| X-Tronic bundle: tweezers | 1 pair | Position the bare amplifier for photographs by its edges instead of touching its pads. |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll, ~4 short tabs | Tape the speaker's 32 AWG factory leads flat to the bench so probing cannot tug the solder tabs; also carries the handwritten AMP-A1 / SPK-A1 labels. |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | Nonconductive layout and photo surface for the unpowered modules — legitimate today only because no hot work happens on Day 10. |
| 3M Solus 1000 safety glasses, clear | 1 | Required for every physical lab, including handling stiff 32 AWG leads and probe tips. |
| Camera or phone with macro/zoom (general item — not in INVENTORY, no purchase URL recorded) | 1 | Evidence photographs of both modules and, because no magnifier is in hand, the substitute for close visual inspection of the SD/MODE network. |
| Notebook, pen, drawing paper, and a calculator (general items — not in INVENTORY) | 1 set | Step 5 arithmetic (Vrms = sqrt(0.8 x 8) = 2.53 V) and step 6's BTL sketch showing three explicitly forbidden ground connections. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **Current-rated 8 ohm dummy load and current-rated leads** — **no purchase
  record anywhere**.
  The conditional powered extension and Lesson 09 Stage 3 both start by driving
  the amplifier into an 8 ohm dummy load, never straight into the one speaker.
  The conditional powered extension is not run: mark powered audio HOLD in the
  record and complete only the default lab (steps 1-6). This plan forbids both
  improvising a load and approximating one with a breadboard or Dupont wire, so
  no substitute is attempted.
- **Two-channel oscilloscope (>=50 MHz) with a differential-safe speaker
  measurement method** — **borrow or arrange access**.
  Any BTL output waveform check needs a differential probe or two subtracted
  channels; an earth-referenced ground clip on OUT+ or OUT- damages the bridge.
  No output waveform is captured. Record 'BTL waveform confirmation
  INCONCLUSIVE — no differential-safe instrument available' and satisfy the
  exit gate by explanation plus the step 6 drawing instead.
- **Magnification (loupe, visor, or bench magnifier)** — **no purchase record
  anywhere**.
  Step 2 traces the amplifier's supply, ground, I2S, SD/MODE and output
  markings from fine silkscreen and 0402-class parts. Photograph each side at
  phone macro/zoom and read the markings from the enlarged image; write
  'inspection method substituted: phone macro, no magnifier in hand' on the
  amplifier evidence sheet.
- **Grounded ESD mat and wrist strap** — **no purchase record anywhere**.
  Day 10 handles a bare amplifier carrier out of its bag;
  `FINAL_MATERIALS_FOR_REVIEW.md` flags ESD control as needed before Phase 0.
  No ESD control is available: keep the module in its antistatic bag until the
  photo step, touch a large grounded metal object first, hold the board by its
  edges, and record 'handled without ESD control' on the evidence sheet.
- **Same Sky CMS-20143-158SP speaker, 8 ohm 1.5 W (the A/B partner)** — **no
  purchase record anywhere**.
  Lesson 10's safe-lab steps 6-9 compare two speaker assemblies under fixed
  conditions. With exactly one speaker in hand (INVENTORY records qty 1) the
  acoustic A/B is out of scope for this plan; record it as HOLD and do not
  improvise a second driver.
- **Speaker baffle / rear-cavity comparison fixture stock** — **borrow or
  arrange access**.
  Lesson 10 steps 7-8 need two repeatable sealed fixtures to compare baffled
  and leaking conditions. Not built. The enclosure discussion stays a written
  prediction in the notebook; no fixture is glued or taped to the one owned
  factory-enclosed speaker.
- **Adafruit #3006 MAX98357A breakout (the design authority's preferred
  amplifier)** — **no purchase record anywhere**.
  `FINAL_MATERIALS_FOR_REVIEW.md` classes the owned HiLetgo carrier as a HOLD
  alternative at 55%, not the approved part. Run the day on the owned HiLetgo
  board as a learning article (permitted by this plan), and write every finding
  against that exact board — the evidence sheet promotes nothing.
- **USB-A-to-C data cable with proven data lines** — listed under **Still
  needed** in `INVENTORY.md`.
  Only the conditional powered extension would need a controller sourcing I2S;
  `INVENTORY.md` lists the Rankie 3-pack under 'Still needed'. Verify before
  assuming, not after: the
  Day 10 default lab needs no USB link at all, and the powered extension is
  already HOLD for lack of a dummy load, so nothing on Day 10 becomes
  INCONCLUSIVE from the cable's absence. Do not buy one to attempt the
  extension.

*Keep off the bench today.*

- All four lithium cells — 2 x Adafruit #1578 and 2 x Adafruit #258 —
  terminal-protected, connectors unmated, outside the work area.
- Adafruit #4410 USB-C Micro-Lipo charger — no charging or source-state work is
  released.
- SKY TOPPOWER PS305H bench supply and its leads — the powered extension is
  HOLD, so the supply stays off the bench where it cannot be improvised into an
  amplifier test.
- REXQualis breadboards and TODOELEC Dupont jumpers — this plan forbids
  amplifier or full-load current through breadboard contacts or Dupont wire.
- Every ESP32-C3 SuperMini and any USB cable — the default lab is unpowered and
  no I2S source is connected today.
- X-Tronic soldering station, MAIYUM solder, and the SHJADE hot glue gun —
  nothing is soldered or glued to the amplifier or the single speaker on Day
  10.
- Harris SCLF4 acid flux — sealed and out of the electronics workspace (and the
  IPA/baking soda needed to neutralise it are not in hand).
- K&S brass tube and rod — the frame stays floating and nowhere near the
  amplifier output pads.

*Check before you start.*

1. Meter first: inspect both KAIWEETS leads for cracked insulation or bent
   tips, confirm the red lead is in the voltage/ohms jack and NOT the fused
   current jack, then short the probes and confirm the continuity beeper and a
   near-0 ohm reading before trusting step 3 or 4.
2. Read the HiLetgo board's own silkscreen for OUT+, OUT-, GND, VIN, DIN, BCLK,
   LRC and SD/GAIN before probing — the IC family name does not prove this
   carrier's layout, and the ~0.30 V SD/MODE reading noted in INVENTORY is a
   powered measurement that is HOLD today, so record only the resistor network
   you can see.
3. Inspect the speaker's 60 mm 32 AWG factory leads for nicks or near-breaks
   and tape them down before probing: this is the only speaker in hand, and a
   damaged lead ends speaker work for the whole plan.
4. Photograph and record that all four cells and the #4410 charger are stored
   terminal-protected in another location, with no electrical connection and no
   pressure on any pouch, before the first module comes out of its bag.
5. Confirm the bench supply is unplugged and physically off the bench, and
   write the sentence 'powered audio HOLD — no current-rated 8 ohm dummy load
   and no differential-safe instrument in hand' at the top of the lab record
   before starting, so the extension is closed out in advance.

Day 10 is entirely unpowered: the amplifier and speaker sit side by side but
are never connected to each other, to a supply, or to a controller. Treat
docs/MATERIALS.md, docs/BOM.md and docs/PURCHASE_READINESS.md as pre-purchase
order sheets — never read their quantity or 'still to buy' columns as current
state; docs/INVENTORY.md is the purchase record and
docs/FINAL_MATERIALS_FOR_REVIEW.md is the design authority. Exactly one speaker
exists (`INVENTORY.md` qty 1) despite archived sheets specifying x2, so any A/B
described there is out of scope. Owning the HiLetgo amplifier is not design
approval: `FINAL_MATERIALS_FOR_REVIEW.md` keeps it at HOLD.

**Study**

- Finish [Lesson 09](../edu/fundamentals/09-i2s-sampling-and-digital-audio.md).
- Read [Lesson 10](../edu/fundamentals/10-class-d-btl-speakers-and-acoustics.md).

**Default lab: unpowered inspection and calculation**

1. Photograph and identify the exact amplifier and speaker.
2. Trace the amplifier supply, ground, I2S, mode/shutdown, and two speaker
   terminals from markings and available board evidence.
3. With everything unpowered, confirm neither speaker terminal is continuous
   with circuit ground.
4. Measure the speaker's DC resistance and label it resistance, not its
   nominal AC impedance.
5. Calculate idealized RMS voltage and power limits. For an 0.8 W, 8 Ω
   speaker, show `Vrms = sqrt(PR) = sqrt(0.8 x 8) = 2.53 V` differential.
6. Draw the correct floating BTL connection and three explicitly forbidden
   probe/ground connections.

**Conditional powered extension**

Power the amplifier only if the exact current material decision permits the
complete battery-free shutdown/isolation fixture and the necessary
current-rated dummy-load wiring and measurement method are already available.
Follow that fixture's current limits and stop rules. Otherwise mark powered
audio `HOLD`; do not use a breadboard or Dupont approximation.

**Evidence to save**

- amplifier and speaker evidence sheets;
- BTL diagram and calculations; and
- either an approved fixture test record or a precise `HOLD` statement.

**Exit gate:** You can explain why neither speaker lead is ground and why an
audible result alone would not prove safe electrical or thermal operation.

---

## Week 3 — Turn skills into a reproducible prototype

### Day 11 — Soldering practice before project hardware

**Status:** `NOT STARTED`

**Question:** Can you repeatedly make an electrically and mechanically
acceptable joint without risking a project module?

If loose headers were found on Day 6, do this session before Day 7. After the
practice gate passes, prepare the needed module headers using the quickstart.
If already completed then, reuse the record and treat this day as catch-up.

**Optional illustrated explanation:** [Soldering and heat](concepts/11-soldering-and-heat.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| X-Tronic 3020-XTS soldering station (75 W) with iron holder | 1 station + its iron holder | The heat source for all ~30 practice joints, and the stable holder that lab step 2 requires before the iron is switched on. |
| X-Tronic bundle: soldering tips | 1 fitted (the T-2.4D chisel) with the other 4, including the T-K knife, in the tray | Lesson 12: a broader chisel tip heats pad and lead faster and cuts total dwell time; the fitted tip and its set temperature are two of the five settings step 3 records. |
| MAIYUM 63/37 rosin-core solder, 0.8 mm | 1 roll (100 g) — the alloy of record for the session | The known 63/37 alloy for every practice joint; its low melting point is what keeps dwell time short. |
| X-Tronic bundle: solder roll (~50 g), alloy not yet identified | 1 roll — staged only to read its label, then set aside | Incoming check per `FINAL_MATERIALS_FOR_REVIEW.md`: identify the alloy from the label; if it is lead-free or unmarked it is not used today and the MAIYUM roll is the only solder on the bench. |
| Chip Quik CQ4LF no-clean flux pen, 10 ml | 1 pen of the 2 in hand | The only flux permitted on the electronics bench; step 3 records it by name alongside alloy, tip, temperature and dwell. |
| 2.54 mm male breakaway header pins | 22 pins exist in total — split them before you start, e.g. 12 pins for practice and 10 reserved in a labelled bag | The primary practice substrate for step 4 now that no perfboard exists; `INVENTORY.md` earmarks these same pins for making the bench stack reversible, so the split is a decision you record, not an assumption. |
| LuminologyPro resistor kit, 25 values, 1/4 W | about 10 resistors, any value (1 kΩ is convenient) — they are coupons, the value is irrelevant | Through-hole leads to solder to wire and header for step 4, and lead pairs for the adjacent-node isolation check in step 6. |
| CBAZY 30 AWG silicone stranded wire, 6 colours | about 1 m total across 2 colours, cut into ~40 mm pieces | Signal-gauge practice joints — the gauge that will later carry I2C, I2S and the button. |
| TUOFENG 26 AWG silicone stranded wire, 6 colours | about 1 m total across 2 colours, cut into ~40 mm pieces | Power-gauge practice joints, so the recorded settings cover both thermal masses rather than only thin wire. |
| Hakko CHP CSP-30-1 wire stripper, 30-20 AWG | 1 | Strip both 30 AWG and 26 AWG without nicking strands; nicked strands are the defect that breaks later inside a sealed frame. |
| BOENFU 6-inch flush cutters | 1 | Trim resistor leads and wire ends to length; wire and component leads only — never the brass tube. |
| X-Tronic bundle: helping hands | 2 | Lab step 2's 'stable holder' — one holds the coupon, one holds the wire, so neither hand is holding work next to a 300 C tip. |
| X-Tronic bundle: silicone work mat | 1 | The only heat-safe work surface owned (`FINAL_MATERIALS_FOR_REVIEW.md`); all hot work happens on it. |
| X-Tronic bundle: tip cleaner | 1 | Keep the tip wetted and oxide-free — Lesson 12 names an oxidised or undersized tip as the real problem people wrongly answer with more temperature. |
| X-Tronic bundle: tweezers | 1 pair | Hold and reposition header pins and resistor bodies near the hot joint instead of fingers. |
| X-Tronic bundle: solder sucker (desoldering pump) | 1 | Clear a bridge on a through-hole practice joint found during step 5; it is too coarse for fine pads, and no fine-pad work exists on Day 11. |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + 2 leads | Step 6, with power absent: intended continuity through each joint and isolation between adjacent pins. |
| 3M Solus 1000 safety glasses, clear | 1 | Step 2 requirement; flux spatter and flicked clippings are the hazards. |
| Camera or phone with macro/zoom, plus a timer (general items — not in INVENTORY) | 1 | Close photographs of early, middle and final joints, the substitute for the magnifier in step 5, and the approximate dwell-time measurement for step 3. |
| Notebook, pen, and a labelled bag or envelope for the reserved header pins (general items — not in INVENTORY) | 1 set | Record the settings that produced ten consecutive acceptable joints, and physically quarantine the header pins you decided not to spend. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **Sacrificial perfboard / scrap protoboard** — **no purchase record
  anywhere**.
  Lab step 1 and Lesson 12 Part A both open by naming scrap protoboard as the
  practice substrate. No purchase record exists anywhere for perfboard. Use the
  fallback already written: practise on spare header pins, resistor leads and
  offcut wire, and record the limitation in the lab record. Only use perfboard
  if you happen to find scrap on your own bench. Never practise on the OLED,
  microphone, amplifier, speaker, or controller.
- **Source-capture fume extraction / documented local ventilation** — **no
  purchase record anywhere**.
  Lab step 2 makes fume capture a setup item, and Lesson 12 states plainly:
  always use fume extraction or effective local ventilation and eye protection.
  This is a hard gate, not a convenience: Day 11 does not start until you have
  written the actual arrangement into the lab record — for example an open
  window plus a fan drawing fumes away from your face with your head out of the
  plume. Step 2 becomes 'document the ventilation arrangement' rather than 'set
  up the extractor'. If no workable arrangement exists, the session does not
  run.
- **Magnification (loupe, visor, or bench magnifier)** — **no purchase record
  anywhere**.
  Step 5 inspects both sides for wetting, bridges, cold joints and receded
  insulation, and the exit gate is a written visual criterion on ten
  consecutive joints. Inspect and judge from phone macro/zoom photographs of
  every joint, and record explicitly that the inspection method was substituted
  because no magnifier is in hand. The exit gate is still assessable from the
  photographs; do not weaken the criteria to compensate.
- **Sullins PRPC040SAAN-RC 1x40 break-away headers (fresh practice stock)** —
  **no purchase record anywhere**.
  Step 4 asks for about 30 practice joints; only 22 header pins exist in total,
  and `INVENTORY.md` already earmarks them for the reversible bench stack. Do
  not buy strips to reach 30. Spend only the practice share you set aside at
  the start; when it runs out, switch to wire-to-wire and wire-to-resistor-lead
  joints, which need no header at all, and record how many joints were made on
  each substrate. If the reserved count would drop below what your module set
  needs, stop practising on header immediately.
- **Solder wick (JoTownCand 3-pack)** — listed under **Still needed** in
  `INVENTORY.md`.
  Step 5 inspects for bridges and excess solder; wick is the normal way to
  remove them, but `INVENTORY.md` lists the JoTownCand 3-pack under 'Still
  needed'. Treat it as
  absent — clear bridges on through-hole practice joints with the owned solder
  sucker, or cut the coupon off and remake it. Fine-pad cleanup is not
  attempted on Day 11 and no project module is used to practise on.

*Keep off the bench today.*

- All four lithium cells (2 x Adafruit #1578, 2 x Adafruit #258) and the
  Adafruit #4410 charger — terminal-protected and outside the work area; a
  soldering iron is running all session.
- Every project module: all 10 ESP32-C3 SuperMini boards, all 5 Hosyond OLEDs,
  all 5 AITRIP INMP441 microphones, all 3 HiLetgo amplifiers, and the single
  Same Sky speaker — this plan forbids using any of them as a practice article,
  so keep them bagged and off the bench entirely.
- Harris SCLF4 Stay-Clean acid flux — sealed, and in a different room from the
  electronics bench; electronics work uses the Chip Quik no-clean pen only, and
  the IPA, swabs and baking soda needed to neutralise the acid flux are not in
  hand.
- K&S #9831 brass tube, K&S #9861 brass rod, the SE jeweler's saw and the
  diamond needle files — no structural hot work, cutting, or metalwork during
  this plan.
- SHJADE hot glue gun — no adhesive work is released, and hot glue near a
  soldering bench only adds a burn hazard.
- WORKLION self-healing cutting mat — keep it clear of the hot-work area; the
  X-Tronic silicone mat is the only heat-safe surface.
- Food and drink (Lesson 12: do not eat at the bench; wash hands after handling
  solder).

*Check before you start.*

1. Read the label on the X-Tronic bundle's solder roll and identify its alloy.
   If it is lead-free, unmarked, or ambiguous, set it aside for the whole
   session and use the MAIYUM 63/37 only — then write the alloy actually used
   into step 3's settings record.
2. Confirm the flux on the bench is the Chip Quik CQ4LF no-clean pen (cap
   sealed, dispenses cleanly, not dried out) and confirm by sight that the
   Harris SCLF4 acid flux is still sealed and in another room before the iron
   is plugged in.
3. Count the header pins (22 exist per `INVENTORY.md`), split them into a
   'practice' pile and a 'reserved for module headers' labelled bag, and write
   the split into the lab record — practice joints permanently consume this
   stock.
4. Write the ventilation arrangement into the lab record before the iron is
   switched on, and put the safety glasses on at the same moment; no extractor
   is in hand, so the written arrangement is the control.
5. Set up on the X-Tronic silicone mat with the iron holder stable and within
   reach, tin and clean the fitted chisel tip, then short the KAIWEETS probes
   to confirm the continuity beeper works before you rely on it in step 6.

Day 11 exists precisely so that no project module is ever a practice article.
Sacrificial perfboard, magnification, and fume extraction have no purchase
record anywhere, so treat them as absent and use the written fallbacks — the
ventilation one is a gate, not a preference. Header
pins are the session's scarce resource: 22 pins against ~30 requested joints,
with a competing claim on them from `INVENTORY.md`. Decide the split up front
rather than discovering the shortage mid-session. Nothing on this bench is
powered; the DMM is used only with sources absent.

**Study**

- Read the soldering, temperature, inspection, and electrical-versus-structural
  sections of
  [Lesson 12](../edu/fundamentals/12-soldering-mechanics-insulation-tolerance.md).

**Lab**

1. Use sacrificial perfboard, resistors, spare header, and wire already on hand.
   If no scrap board exists, practice on spare header and wire and record the
   limitation; do not use the OLED, microphone, or controller as practice.
2. Set up eye protection, ventilation/fume capture, the silicone hot-work mat,
   and a stable holder.
3. Record solder alloy, flux, tip, temperature, and approximate dwell time.
4. Make approximately 30 practice joints.
5. Inspect both sides for wetting, bridges, excess solder, cold joints, lifted
   pads, and damaged insulation.
6. With power absent, test intended continuity and adjacent-pad isolation.

Electronics work uses electronics flux only. Acid brass flux remains sealed
and outside the electronics workspace.

**Evidence to save**

- close photographs of early, middle, and final joints;
- inspection and continuity results; and
- the settings that produced ten consecutive acceptable joints.

**Exit gate:** Ten consecutive joints meet the same written visual,
continuity, and isolation criteria.

### Day 12 — Wire joints, strain relief, and controlled rework

**Status:** `NOT STARTED`

**Question:** Can a wire connection survive handling without transferring
force to a fragile electrical pad?

**Optional illustrated explanation:** [Joints and strain relief](concepts/12-joints-and-strain-relief.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| X-Tronic 3020-XTS soldering station (75 W) with iron holder | 1 station + iron holder — the same setup left from Day 11 | Steps 1, 2 and 5: wire-to-header joints, splices, and the desolder/restore cycle. |
| X-Tronic bundle: soldering tips | 1 fitted (T-2.4D chisel) | Same tip and temperature carried over from Day 11's qualified settings, so rework results are comparable to the practice record. |
| MAIYUM 63/37 rosin-core solder, 0.8 mm | 1 roll | All 20+ wire joints, 10 splices, and the three restored sacrificial joints. |
| Chip Quik CQ4LF no-clean flux pen, 10 ml | 1 pen | Electronics flux for the joints and, especially, for rewetting old solder during the step 5 restore. |
| Hakko CHP CSP-30-1 wire stripper, 30-20 AWG | 1 | Step 1-2: strip both gauges cleanly; a nicked strand is the exact defect strain relief is supposed to prevent. |
| CBAZY 30 AWG silicone stranded wire, 6 colours | about 2 m across 2 colours — roughly 20 x 40 mm pieces for joints plus 10 x 60 mm pairs for splices | The signal gauge for step 1's wire-to-pad practice and half of step 2's ten splices. |
| TUOFENG 26 AWG silicone stranded wire, 6 colours | about 1.5 m across 2 colours | The power gauge for step 1, and the stiffer conductor that makes the step 3-4 strain-relief comparison visible. |
| 2.54 mm male breakaway header pins | only the practice share you set aside on Day 11, out of the 22 that exist | The wire-to-pad targets for step 1 and the three sacrificial joints desoldered in step 5; the reserved pins stay in their labelled bag. |
| Pointool heat-shrink tubing kit, 14 sizes, white | 10 pieces, sizes chosen after measuring the splice OD (the kit is white only) | Step 2's ten insulated splices, and the heat-shrink form of strain relief in step 3. |
| QWORK mini heat gun, 300 W, with stand | 1 gun + its stand | Shrink the ten splices with controlled hot air — used only with every cell outside the work area, and only over the silicone mat. |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll, ~10 tabs | Step 3's tie point and lacing anchor for the strain-relieved sample, and the marker distinguishing it from the matched unsupported sample; it survives soldering heat where vinyl tape does not. |
| X-Tronic bundle: helping hands | 2 | One holds the anchored sample and one the unsupported sample, so step 4's gentle comparison is repeatable instead of a hand-held tug. |
| X-Tronic bundle: solder sucker (desoldering pump) | 1 | The only desoldering tool in hand for step 5 — usable on through-hole header and wire joints, and explicitly too coarse for small module pads. |
| X-Tronic bundle: silicone work mat | 1 | The heat-safe surface for both the iron and the heat gun; nothing hot touches any other surface. |
| X-Tronic bundle: tip cleaner | 1 | Rework wets old, oxidised solder, so tip condition matters more here than on Day 11. |
| X-Tronic bundle: tweezers | 1 pair | Hold the wire steady during the restore in step 5 and slide heat-shrink into position without fingers in the hot-air stream. |
| BOENFU 6-inch flush cutters | 1 | Cut wire and heat-shrink to length and trim restored joints; wire only, never brass. |
| NEIKO digital caliper, 0-6 in (01407A) | 1 | Measure the finished splice OD before choosing a heat-shrink size — Lesson 12's rule is measure the joint first, then pick the tubing. |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1 meter + 2 leads | Step 6, sources absent: continuity through every reworked joint and isolation between adjacent nodes. |
| 3M Solus 1000 safety glasses, clear | 1 | Worn for the whole session — hot air, flicked clippings, and flux spatter. |
| Camera or phone with macro/zoom (general item — not in INVENTORY) | 1 | Before/after rework photographs, the substrate inspection in step 5, and the substitute for the magnifier that is not in hand. |
| Notebook and pen (general items — not in INVENTORY) | 1 set | The splice/continuity/isolation checklist and the written note on where bending concentrated with and without strain relief. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **Solder wick (JoTownCand 3-pack, 3 widths)** — listed under **Still needed**
  in `INVENTORY.md`.
  Step 5 desolders at least three sacrificial joints, inspects the substrate,
  and restores them; braid is the tool that lifts solder off a joint cleanly.
  `INVENTORY.md` lists the JoTownCand 3-pack under 'Still needed', so treat it
  as absent. Do step
  5 only on through-hole header/wire joints using the owned solder sucker, and
  mark fine-pad rework INCONCLUSIVE. Do not practise desoldering on a project
  module to compensate — `FINAL_MATERIALS_FOR_REVIEW.md` records the sucker as
  too coarse for small module pads, which is exactly why the OLED and
  microphone are off limits.
- **Sacrificial perfboard / scrap protoboard** — **no purchase record
  anywhere**.
  Step 1 says 'wire-to-pad or wire-to-spare-header joints' and step 5 inspects
  the substrate after desoldering — both assume a scrap board. No purchase
  record exists. Step 1 becomes wire-to-header-pin and wire-to-wire joints
  only, and step 5's substrate inspection is limited to the header pin and wire
  insulation. Record the substitution in the lab record; do not use a project
  module as the substrate.
- **Magnification (loupe, visor, or bench magnifier)** — **no purchase record
  anywhere**.
  Step 5's substrate inspection and step 6's adjacent-node check both assume
  close visual examination after heat has been applied twice. Photograph each
  joint at phone macro before desoldering and after restoring, and judge from
  the enlarged images. Record that the inspection method was substituted; do
  not relax the pass criteria.
- **Source-capture fume extraction / documented local ventilation** — **no
  purchase record anywhere**.
  The iron runs all session and the heat gun adds hot air over flux residue and
  shrinking tubing; Lesson 12 makes fume control mandatory. Same hard gate as
  Day 11: the session does not start until the actual ventilation arrangement
  is written into the lab record. If no workable arrangement exists, Day 12
  does not run — there is no calculation substitute for a soldering session.
- **Sullins PRPC040SAAN-RC 1x40 break-away headers (fresh practice stock)** —
  **no purchase record anywhere**.
  Step 1 asks for at least 20 wire-to-pad or wire-to-header joints, and Day 11
  has already spent part of the 22 pins that exist. Do not buy strips to reach
  20. Reuse the same practice pins by reworking them, and make the remainder as
  wire-to-wire joints — this plan already accepts wire joints, and step 2's ten
  insulated splices need no header at all. Record how many joints were made on
  each substrate and never dip into the reserved pin bag.
- **3M FP-301 heat-shrink samples in black, white, and red** — **borrow or
  arrange access**.
  Red tubing is what would permanently identify both ends of CELL_POS on an
  all-black harness; the owned Pointool kit is white only. Nothing on Day 12 is
  blocked, because no cell harness is released in this plan. Use the white
  Pointool tubing for practice splices only, and record that these coupons are
  practice articles, not harness stock — identity marking is a later,
  separately released task.

*Keep off the bench today.*

- All four lithium cells (2 x Adafruit #1578, 2 x Adafruit #258) — outside the
  room or active work area entirely, not merely off the bench: this session
  runs a soldering iron and a 300 W heat gun.
- Adafruit #4410 USB-C Micro-Lipo charger — stored separately; no charging,
  connection, or heat near it.
- Every project module: all 10 ESP32-C3 SuperMini boards, all 5 Hosyond OLEDs,
  all 5 AITRIP INMP441 microphones (flux and hot air permanently ruin the
  acoustic port), all 3 HiLetgo amplifiers, and the single Same Sky speaker —
  rework practice never happens on a project module.
- Harris SCLF4 Stay-Clean acid flux — sealed and in another room; its residue
  is corrosive and conductive, and the IPA, swabs and baking soda needed to
  neutralise it are not in hand.
- K&S brass tube and rod, the SE jeweler's saw, and the diamond needle files —
  no structural hot work or cutting; Lesson 12 keeps structural metalwork on a
  separate offcut with electronics absent.
- SHJADE hot glue gun — no adhesive retention work is released.
- WORKLION self-healing cutting mat and any loose paper, cardboard or packaging
  — out of the heat-gun airflow; all hot work happens over the X-Tronic
  silicone mat only.
- Food and drink at the bench.

*Check before you start.*

1. Confirm, by walking to where they are stored, that all four cells and the
   #4410 charger are in another room and terminal-protected before the heat gun
   is plugged in — hot air plus a cell is the one combination this session most
   needs to be impossible.
2. Measure each finished splice with the NEIKO caliper and select the
   heat-shrink size from that measurement before cutting tubing; the Pointool
   kit is white only, so mark the strain-relieved and unsupported samples with
   Kapton tape and pen, not by tubing colour.
3. Test the Hakko CSP-30-1 on one 30 AWG and one 26 AWG offcut and inspect the
   strands at phone macro: if the notch nicks strands, change notches before
   making 20 joints that all share the same hidden defect.
4. Check the solder sucker's plunger, seal and nozzle, then write 'solder wick
   NOT IN HAND — fine-pad rework INCONCLUSIVE; step 5 limited to through-hole
   header/wire joints with the sucker' into the lab record before starting, so
   the limitation is declared rather than discovered.
5. Re-write the ventilation arrangement into today's lab record, put the safety
   glasses on, confirm the heat-gun stand is stable on the silicone mat with
   nothing flammable downstream, and short the KAIWEETS probes to confirm the
   continuity beeper before relying on it in step 6.

Day 12 depends on three things the purchase record does not support — solder
wick, sacrificial perfboard, and magnification — so confirm what you actually
have before the session rather than mid-step. The real substrate is the header pins left from Day 11's
split plus wire-to-wire splices, and the real desoldering tool is the coarse
solder sucker — which is why the OLED, microphone, amplifier, controller and
speaker stay bagged and out of the room. Cells go further away today than on
any other bench day because both a soldering iron and a heat gun are running.
Archived docs/MATERIALS.md, docs/BOM.md and docs/PURCHASE_READINESS.md are
pre-purchase order sheets; docs/INVENTORY.md is the purchase record and
docs/FINAL_MATERIALS_FOR_REVIEW.md is the design authority.

**Study**

- Finish [Lesson 12](../edu/fundamentals/12-soldering-mechanics-insulation-tolerance.md).
- Revisit Lesson 04's pin/view-direction guidance before any rework.

**Lab**

1. Practice at least 20 wire-to-pad or wire-to-spare-header joints using the
   intended signal and power wire sizes.
2. Make ten insulated practice splices.
3. Add strain relief to one sample and leave a matched sample unsupported.
4. Perform a gentle, documented comparison rather than an uncontrolled
   destructive pull.
5. Choose at least three sacrificial joints, desolder them, inspect the
   substrate, and restore them.
6. Verify continuity and adjacent-node isolation after rework.

Do not use heat-shrink, hot air, or soldering anywhere near a cell. Cells remain
outside the room or active work area.

**Evidence to save**

- before/after rework photographs;
- splice, continuity, and isolation checklist; and
- notes on where bending concentrated with and without strain relief.

**Exit gate:** Reworked samples remain intact and electrically correct, and
you can distinguish soldering quality from mechanical support.

### Day 13 — Power integrity without a battery

**Status:** `NOT STARTED`

**Question:** Why can a circuit that works at idle fail during startup, Wi-Fi,
or audio activity?

**Optional illustrated explanation:** [Power integrity](concepts/13-power-integrity.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| SKY TOPPOWER DC bench supply, 0-30 V / 0-5 A (PS305H) | 1, with both of its insulated leads | The only energy source on the bench today; drives the low-energy resistor load for lab step 3's Day 5 startup and constant-current repeat. |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1, with both test leads and the hard case | Measure each resistor before energising, read output at the supply terminals and again at the load end, and check the slide switch unpowered. |
| LuminologyPro resistor kit, 25 values, 1/4 W | 6 pieces (3 x 1 kΩ, 1 x 2.2 kΩ, 1 x 10 kΩ, 1 x 100 kΩ) | First 1 kΩ is the step-3 load, second 1 kΩ goes in series to simulate source impedance (Lesson 06 step 8), third is the spare for the measured-tolerance check; 2.2 kΩ gives a second load point; 10 kΩ is the paper high-resistance load for the P = Vout²/R rating calculation; 100 kΩ for the pull-network arithmetic in the source-state table. |
| BOJACK ceramic capacitor kit | 4 pieces (2 x 100 nF, 2 x 10 µF) | Identification and calculation only — read the marking code, dielectric class, and voltage rating for Lesson 06's decoupling section; they are not installed in any circuit today. |
| ALLECIN electrolytic capacitor kit, 24 values | 2 pieces (1 x 100 µF, 1 x 220 µF) | Work the ΔV = I × Δt / C example (0.4 A for 100 µs into 100 µF = 0.4 V) and the 220 µF bulk-rail discussion; read the polarity stripe and printed voltage rating on each. |
| Chanzon SPDT mini slide switch | 1 of the 25 | Lab step 4's owned-candidate inspection — unpowered continuity and contact resistance across each throw, nothing else. |
| REXQualis solderless breadboards (830 + 400 point) | 1 (the 830-point board) | Holds the milliamp resistor load only; no amplifier and no full-load current ever passes through breadboard contacts. |
| TODOELEC Dupont jumper kit, 10 cm | 4 wires of the 120 | Supply positive and negative to the breadboard rails plus two meter tap points; low-current bench use only. |
| 3M Solus 1000 safety glasses, clear | 1 | Required for every physical lab in this plan. |
| X-Tronic bundle: tweezers | 1 pair | Place and lift the small ceramic capacitors and trimmed resistor leads without dropping parts across the supply leads. |
| BOENFU 6-inch flush cutters | 1 | Trim resistor leads so they seat fully in the breadboard; component leads and wire only, never the brass stock. |
| X-Tronic bundle: silicone work mat | 1 | Non-conductive, non-slip layout surface so loose component leads cannot bridge the supply leads on the bench top. |
| Notebook, pen, and drawing paper (general item — no project purchase recorded) | 1 notebook + several loose sheets | Step 1's power-block diagram, step 5's source-state table, and the calculation sheet with DATASHEET/ASSUMED/CALCULATED/MEASURED labels. |
| Calculator (general item — no project purchase recorded) | 1 | Step 2's Iin = Pout / (efficiency x Vin) at two input voltages, and the ΔV = I × Δt / C decoupling arithmetic. |
| Camera or phone (general item — no project purchase recorded) | 1 | Photograph the supply front panel showing the set voltage and current limit for every recorded run. |
| Computer (general item — no project purchase recorded) | 1 | Re-read the current power architecture in docs/FINAL_MATERIALS_FOR_REVIEW.md for step 1's drawing. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **Pololu #2873 (S9V11F3S5C3) whole-load 5 V regulator / UVLO module** — **no
  purchase record anywhere**.
  Lab step 4 and Lesson 06's safe lab are built around an exact converter
  sample: photograph the module, check for input/output shorts, power it at 3.8
  V / 100 mA limit, then sweep 4.2 V down to 3.0 V separating cold-start from
  continued operation. No converter is in hand, so lab step 4's converter
  inspection and the whole Lesson 06 sweep are HOLD. Complete step 2's Iin
  calculation at two input voltages with every assumed efficiency and output
  labelled ASSUMED, and write into the step-5 source-state table that converter
  startup versus run thresholds are unmeasured. Do not attach the controller's
  onboard regulator or any other module to make a complete chain.
- **Pololu #2810 Mini MOSFET slide switch (LV)** — **no purchase record
  anywhere**.
  The step-5 source-state table needs a real off-state / isolator row: whether
  the user switch is a control input or a physical battery disconnect, and what
  leaks through body diodes. The isolator rows of the source-state table stay
  HOLD. The owned Chanzon switch is inspected unpowered only and may be
  described as a microamp control input candidate; it is REJECTed for carrying
  battery load and must not be wired as a disconnect (this plan forbids
  improvising a missing isolator).
- **Littelfuse PICO II fuse samples (0251.500MXL 500 mA, 025101.5MAT1L 1.5 A)**
  — **no purchase record anywhere**.
  The exit gate asks you to separate fusing from regulation, UVLO, charge
  control, and cell protection, and Lesson 06 contrasts PPTC behaviour against
  an ideal fuse. Write the fuse/PPTC row of the protection-layer table from
  published curves labelled DATASHEET. No fuse is installed, tested, or
  substituted with a link or a length of wire; mark trip-curve verification
  INCONCLUSIVE.
- **Two-channel oscilloscope, >=50 MHz** — **borrow or arrange access**.
  Lesson 06 step 9 records minimum voltage, overshoot, and settling time at the
  load during power-on and a load step — the direct evidence for the day's
  question about idle-versus-transient failure. Transient droop and overshoot
  are INCONCLUSIVE. Substitute the ΔV = I × Δt / C calculation for the stated
  assumption, label it CALCULATED, and say in the record that no instrument on
  the bench can see a 100 µs event.
- **Fast current-capture instrument (>=100 kHz, Joulescope-class)** — **borrow
  or arrange access**.
  The question 'why does a circuit that works at idle fail during startup,
  Wi-Fi, or audio activity' is a peak-versus-average current question. The
  KAIWEETS gives an average only. Every peak or transient current figure stays
  CALCULATED or INCONCLUSIVE and must not be used to size a cell, fuse, switch,
  converter, or wire in the source-state table.
- **Calibrated Pico USB TC-08 with type-T probes** — **borrow or arrange
  access**.
  Lesson 06's thermal section: case temperature is not junction temperature,
  and touching a board is neither a measurement nor a safe thermometer.
  Temperature-rise claims stay CALCULATED from dissipated power x assumed
  thermal resistance. Do not touch parts to judge heat; mark thermal
  qualification INCONCLUSIVE.
- **Yageo MFR-25FBF52 1% resistors and Panasonic EEU-FC1A221SB 220 µF
  capacitors** — **no purchase record anywhere**.
  These are the exact qualified parts for the pull-down/pull-up and bulk-rail
  roles the day's architecture drawing discusses. Use the owned LuminologyPro
  and ALLECIN parts as teaching articles only. Record their measured values as
  MEASURED-on-this-sample, and mark the exact-part decoupling and pull-network
  design HOLD — a generic assortment is not a traceable power-integrity design
  (Lesson 06).

*Keep off the bench today.*

- All four protected LiPo packs (2 x Adafruit #1578, 2 x Adafruit #258) —
  terminal-protected, connectors unmated, outside the work area; the bench
  supply is the only source today.
- Adafruit #4410 USB-C Micro-Lipo charger — it is a subject of the source-state
  drawing, not a bench part; keep it stored with the cells.
- All 10 Meshnology ESP32-C3 SuperMini boards — this plan explicitly forbids
  preparing a controller for the powered resistor-load portion.
- HiLetgo MAX98357A amplifier and the Same Sky CES-20134-088PM speaker — no
  amplifier is powered without an approved fixture, and none exists.
- daier JST-PH 2.0 mm cables — no battery harness is staged; nothing on this
  bench gets a cell-shaped connector.
- Any USB cable — there is no controller today, so there is nothing to plug in
  and no reason for one to be within reach.
- Harris SCLF4 Stay-Clean acid flux — sealed, stored away from all electronics,
  and it stays sealed until the IPA and baking soda exist.
- X-Tronic soldering station, QWORK heat gun, and SHJADE hot glue gun — no hot
  work is part of Day 13.

*Check before you start.*

1. Meter first: confirm the KAIWEETS leads are uncut and the fused current
   jack's fuse is intact, then leave the red lead in the voltage jack. Never
   put the meter in current mode across the supply, and return the red lead to
   the voltage jack immediately after any optional series reading.
2. Set the supply with its output OFF and the leads open: dial the voltage and
   the current limit before anything is connected, then verify lead polarity at
   the breadboard end with the meter — not by wire colour — before energising.
3. Resistor power gate: measure each resistor's actual resistance, then compute
   P = V²/R for the voltage you intend to apply and confirm it stays under the
   1/4 W rating with at least 2x margin (5 V into 1 kΩ = 25 mW). Do not swap to
   a lower resistance just to force a bigger current.
4. Capacitor incoming inspection: on every ALLECIN electrolytic, read the
   printed voltage rating and find the polarity stripe before it comes anywhere
   near the bench; on the BOJACK ceramics, record the marking code and note
   that effective capacitance falls with DC bias, temperature, and age (Lesson
   06).
5. Confirm and write down that all four cells and the #4410 charger are
   terminal-protected, unmated, and out of the work area before the supply is
   switched on — that recorded state is part of the day's evidence.

Document authority: docs/INVENTORY.md is the purchase record and
docs/FINAL_MATERIALS_FOR_REVIEW.md is the design authority; docs/MATERIALS.md,
docs/BOM.md, and docs/PURCHASE_READINESS.md are stale pre-purchase order sheets
— never read their 'Still to buy' or quantity columns as the current in-hand
state. Practical caveat on step 3: at 3.3 V into 1 kΩ the expected current is
only 3.3 mA, and a 0-5 A supply's current-limit control may not resolve below
that. If you cannot set a limit under the expected current, record the
control's actual resolution and mark the constant-current transition
INCONCLUSIVE rather than substituting a much lower resistance to force the
effect — the resistors on hand are 1/4 W. Nothing on this bench is a qualified
final part: the Chanzon switch is REJECTed for battery load, and the kit
passives are learning articles, so no result from today releases a design
choice.

**Study**

- Read [Lesson 06](../edu/fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md).
- Revisit the converter and efficiency sections of Lesson 03.

**Lab**

1. Draw the current proposed power architecture from the current material
   decision, clearly separating USB, battery-free discharge testing,
   standalone charging, and held future cell use.
2. Calculate an illustrative converter input current using
   `Iin = Pout / (efficiency x Vin)` at two input voltages. Label every assumed
   value; do not claim it is the pager's measured demand.
3. On a low-energy resistor load only, repeat the safe bench-supply startup and
   current-limit observations from Day 5.
4. If an exact converter or switch is currently permitted and already owned,
   inspect its identity and test it alone only within the applicable
   battery-free procedure. Do not attach the controller, amplifier, charger,
   or cell merely to make a complete chain.
5. Write a source-state table covering USB on/off, external rail on/off, and
   possible reverse-current paths. Mark unresolved states `HOLD`.

**Evidence to save**

- power-block diagram and source-state table;
- calculation sheet with evidence labels; and
- resistor-load supply observations or a documented fixture `HOLD`.

**Exit gate:** You can distinguish regulation, UVLO, charge control, cell
protection, fusing, and source isolation, and you can explain why none replaces
the others.

### Day 14 — RF awareness and a 1:1 nonconductive mock-up

**Status:** `NOT STARTED`

**Question:** Can the received parts fit while preserving antenna, connector,
acoustic, insulation, and removal space?

**Optional illustrated explanation:** [Fit and radio](concepts/14-fit-and-radio.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| NEIKO digital caliper, 0-6 in (01407A) | 1 | Lab step 1 — every module, connector, control, and speaker dimension to 0.01 mm, plus the insulation and cardboard thicknesses. |
| Meshnology ESP32-C3 SuperMini dev board | 1 (the Day 6-qualified MCU-A1; the other 9 stay boxed) | Measured, its antenna region marked with a removable keepout, and it is the only board used in the optional step-5 metal-proximity A/B. |
| Hosyond SSD1306 OLED, 0.96 in 128x64 I2C, white | 1 (the identified OLED-A1) | Measure PCB outline, glass position, and the viewing-window offset so the front-panel cutout is placed from a real part, not a listing. |
| AITRIP INMP441 I2S MEMS microphone | 1 | Measure the board outline and the acoustic port position to reserve the port path and contamination keepout. |
| HiLetgo MAX98357A I2S class-D amplifier | 1 | Dimension article only — measure the outline, height, and the two speaker-terminal positions; no supply, no I2S, no speaker leads. |
| Same Sky CES-20134-088PM speaker, 8 ohm 0.8 W, factory-enclosed | 1 — the only unit in the project, no spare | Measure the 20 x 13 x 4.87 mm body, the mounting flanges, and the 60 mm lead exit; set the front opening and rear-cavity keepout. |
| QTEATAK 6x6 mm tactile push buttons with caps | 2 switches + 2 white caps | Measure actuator travel and the cap/finger envelope; a second one lets you compare cap-on and cap-off heights without refitting a cap repeatedly. |
| 2.54 mm male breakaway header pins | 4 pins, returned to the labelled bag afterwards (only 22 exist) | Measure the seated stack height a soldered header adds under each module — measuring consumes none of the reserved stock. |
| XFJYMXDM fish paper (flame-rated insulation board) | 1 roll, calipered at an existing edge — do not cut | Record the real barrier thickness and reserve it in the battery-bay clearance stack; this plan permits measurement only. |
| ELEGOO polyimide (Kapton) tape, 4-pack | 1 roll | Caliper the film-plus-adhesive thickness for the same insulation stack, and hold paper templates without tearing them. |
| TUOFENG 26 AWG silicone stranded wire, 6 colours | 1 offcut, about 150 mm | Measure the real outside diameter and minimum bend radius of a power run so the wire-bend keepout is measured, not guessed. |
| CBAZY 30 AWG silicone stranded wire, 6 colours | 1 offcut, about 150 mm | Same measurement for a signal run (I2C, I2S, button) so both gauges get their own bend allowance. |
| daier JST-PH 2.0 mm 2-pin connector cables | 1 pair, mated dry once then separated | Measure the connector body plus the mated plug envelope and cable bend for the connector keepout; unpowered measurement only, never near a cell. |
| BOENFU 6-inch flush cutters | 1 | Cut the two short wire samples; never the brass tube, whose 0.225 mm wall crushes under flush cutters. |
| WORKLION 12 x 18 inch self-healing cutting mat | 1 | The craft-cutting surface for the cardboard mock-up (this mat is never a soldering surface). |
| OLFA CMP-1 circle cutter | 1 | Cut the speaker grille and the microphone port opening in the cardstock front panel. |
| K&S #9831 brass tube, 1.5 mm OD x 0.225 mm wall x 300 mm | 1 uncut 300 mm tube of the 4 | The metal coupon for the optional step-5 A/B, supported on cardboard or foam so it cannot touch a powered pad; no cutting, bending, or joining. |
| K&S #9861 1.0 mm round brass rod, 300 mm | 1 uncut 300 mm rod of the 5 | Laid alongside the mock-up to represent corner posts and braces at true diameter; do not cut or bend it. |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1, in continuity mode | Prove the brass coupon reads open to the controller GND and the USB shell before and after each RF run — the frame must stay electrically floating. |
| X-Tronic bundle: tweezers | 1 pair | Hold the microphone and OLED by their edges while measuring, keeping fingers off the acoustic port and the glass. |
| 3M Solus 1000 safety glasses, clear | 1 | Required for every physical lab, including blade work on cardboard. |
| Reused clean packaging cardboard (~1 mm), paper, and removable tape (general item — this plan says no dedicated purchase is required) | About 2 letter-size sheets of cardboard, 4 sheets of paper, 1 roll of removable tape | Lab step 2's 1:1 nonconductive mock-up and step 3's inert cell dummy. |
| Camera or phone (general item — no project purchase recorded) | 1 | Six-view mock-up photographs and a photograph of every A/B geometry with the ruler in frame. |
| Notebook, fine marker, and ruler (general item — no project purchase recorded) | 1 each | Dimension and clearance table, the antenna keepout marking, and the interference/removal failure list. |
| Computer and printer (general item — no project purchase recorded) | 1 | Print the Adafruit #1578 (29 x 36 x 4.75 mm) and #258 (34 x 62 x 5 mm) dimension pages so the cell dummy is built from printed figures rather than a real pack. |
| Link-metric test firmware on the computer plus one fixed 2.4 GHz access point (general item — no project purchase recorded) | 1 host + 1 access point | Optional step 5 only, and only if the backend/privacy decision has already been recorded; logs timestamped RSSI, packet attempts/successes, and reconnects. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **USB-A-to-C data cable with working data lines (Rankie USB 3.0 3-pack)** —
  listed under **Still needed** in `INVENTORY.md`.
  Lab step 5's metal-proximity A/B needs the bare qualified controller running
  link-metric firmware from USB power. `INVENTORY.md` lists the 3-pack under
  'Still needed', so verify before you start rather than assuming.
  Treat it as not in hand until a cable you actually possess is proven to carry
  data (`esptool flash_id` returns the chip and flash size on the bare board) —
  a charge-only cable makes a working board look dead. If no data-capable cable
  is proven, step 5 is HOLD and the RF A/B is INCONCLUSIVE; steps 1-4
  (measurement, mock-up, inert cell dummy, antenna keepout) are unaffected and
  still close the day's exit gate.
- **Mock-up stock: ~1 mm cardstock/chipboard, painter's tape, graph paper,
  removable poster putty** — **no purchase record anywhere**.
  Step 2's 1:1 model and the conservative-maximum outlines of Lesson 12 Part B.
  No blocker — the plan is written to run on reused clean packaging. Caliper
  and record the thickness of the cardboard you actually used, so the mock-up's
  own wall thickness is never mistaken for design clearance in the dimension
  table.
- **Metric rule and engineer's square** — **no purchase record anywhere**.
  Squareness and long straight layout when transferring measured dimensions
  onto the mock-up. Use printed graph paper as the straightedge and square
  reference and the caliper's step face for depths. Mark right-angle and
  long-span squareness INCONCLUSIVE in the clearance table rather than
  recording a verified frame layout; no frame layout is released in this plan
  anyway.
- **Same Sky CMS-20143-158SP speaker, 8 ohm 1.5 W** — **no purchase record
  anywhere**.
  The A/B partner for any acoustic-opening or rear-cavity comparison. Exactly
  one speaker exists (INVENTORY qty 1) and there is no spare. Record the single
  measured geometry and the reserved rear volume, and mark speaker A/B
  explicitly out of scope for this plan — the comparison described in the
  archived order sheets assumed two units.
- **Speaker baffle / rear-cavity comparison fixture stock (rigid sheet, gasket,
  clamps)** — **borrow or arrange access**.
  Two repeatable sealed fixtures are required before any acoustic comparison is
  meaningful. Doubly blocked (no second speaker either). The mock-up records
  the front-opening geometry, seal path, and reserved rear volume as geometry
  only; acoustic performance stays HOLD and no sound test is attempted.
- **Grounded ESD mat and wrist strap** — **no purchase record anywhere**.
  Step 1 and step 5 handle a bare controller and a bare MEMS microphone by hand
  for an extended session. No step is removed. Touch a grounded metal object
  before handling, hold boards by their edges with the owned tweezers, and
  write into the lab record that all Day 14 handling was done with no ESD
  control — so a later intermittent failure is not silently blamed on something
  else.
- **FreeCAD-capable host** — **borrow or arrange access**.
  To compare the mock-up against the committed CAD fit artifacts. Do not use
  the committed CAD as evidence: this plan states it is not a substitute for
  measurements of received parts, and the generated fit artifacts are recorded
  as stale. Build the dimension and clearance table from caliper readings only,
  and list the CAD reconciliation as an open item.

*Keep off the bench today.*

- All four protected LiPo packs (2 x Adafruit #1578, 2 x Adafruit #258) — this
  plan says do not bring either real cell to the bench; step 3 permits only a
  paper/cardboard inert dummy built from printed dimensions.
- Adafruit #4410 USB-C Micro-Lipo charger — stays stored with the cells;
  nothing charges on Day 14.
- SKY TOPPOWER bench supply and its leads — the optional RF A/B is USB-only on
  a bare controller, and every external 3.3 V/5 V source must be disconnected.
- Any powered connection to the MAX98357A amplifier or the speaker — both are
  dimension articles today; keep breadboard, jumpers, and any supply away from
  them.
- SE jeweler's saw, blades, and bench pin; SE diamond needle files; WORKPRO
  jewelry pliers — no cutting, filing, or bending of the brass is released, so
  keep them off the bench where the uncut coupon cannot be 'just trimmed'.
- SHJADE hot glue gun, glue sticks, and any adhesive — no gluing is released;
  the mock-up is held together with removable tape only.
- Harris SCLF4 acid flux, the Chip Quik flux pen, IPA, and compressed air —
  none may come near the microphone acoustic port or the mock-up.
- X-Tronic soldering station and QWORK heat gun — no hot work of any kind on
  Day 14.
- Spray primer and paint — none is owned and no painting is released in this
  plan.

*Check before you start.*

1. Zero the NEIKO caliper closed and wipe the jaws before the first reading;
   work in mm to 0.01 and take three readings on every critical dimension,
   because listing dimensions are frequently wrong and a single reading hides
   jaw skew.
2. Speaker incoming inspection: one unit only, no spare. Inspect the 60 mm 32
   AWG leads for nicks, support them so nothing pulls on the solder tabs, and
   do not cut, strip, or re-terminate them — a damaged lead ends speaker work
   for this plan.
3. Before the optional RF A/B, meter continuity from the brass coupon to the
   controller GND and to the USB shell: it must read open. Support the tube on
   cardboard or foam so it cannot touch a powered pad, and re-check the
   isolation after every geometry change (Lesson 11 step 10).
4. Keep tape adhesive, marker ink, solvent, glue, and compressed air away from
   the INMP441 acoustic port while measuring — contamination is permanent;
   handle the module by its edges with the tweezers.
5. Build the cell dummy only from the printed #1578/#258 dimension pages,
   confirm and record that no real cell or charger has entered the room, and
   mark the dummy 'INERT MOCK-UP' in marker so it is never confused with a
   pack.

The single decisive verification for this day is the USB cable: everything
except step 5 runs without it, so start the session with steps 1-4 and treat
the RF A/B as a bonus that only happens if a cable is proven to carry data. If
step 5 does run, follow Lesson 11's discipline — at least five equal-duration
baseline runs, one variable changed at a time, distances at 5/10/15/30 mm and
two orientations, and a repeated baseline after the metal is removed; compare
medians and spread and report packet loss and reconnects, never a single RSSI
number. Step 5 also requires the backend/privacy decision to have been recorded
before any Wi-Fi provisioning. Ownership note: brass tube and rod are already
in hand and must not be re-ordered, but every cutting, bending, joining, and
painting operation remains HOLD pending a separate written final-fabrication
release.

**Study**

- Read [Lesson 11](../edu/fundamentals/11-rf-emc-antennas-and-metal-frame.md).
- Revisit Lesson 12's tolerance-stack and functional-keepout sections.

**Lab**

1. Measure the real controller, OLED, microphone, amplifier, speaker,
   connectors, controls, and wire-bend requirements with the available
   caliper or rule.
2. Create a 1:1 mock-up from packaging cardboard, paper, tape, or other
   nonconductive material already owned.
3. Represent the cell only with an inert paper/cardboard size-and-weight dummy.
4. Mark the controller antenna region and provide a removable keepout around
   it. Check USB plug insertion, button/finger access, wire bends, acoustic
   openings, insulation thickness, and part removal paths.
5. If desired, perform Lesson 11's USB-powered metal-proximity A/B using an
   uncut brass piece supported so it cannot touch a powered pad. Keep the
   controller bare and the cell absent. Record repeated baseline and changed
   conditions rather than one RSSI value.

Do not cut, bend, solder, glue, or paint the final brass stock. The committed
CAD is not a substitute for measurements of the received parts.

**Evidence to save**

- dimension and clearance table;
- six-view mock-up photographs;
- a list of interference/removal failures; and
- optional repeated RF A/B results with exact geometry.

**Exit gate:** Every part has an insertion/removal path, the antenna and ports
remain accessible, and unresolved power/guard geometry is visibly reserved
rather than guessed away.

### Day 15 — Battery-free integration and debugging capstone

**Status:** `NOT STARTED`

**Question:** Can every previously passed subsystem be reproduced from a clean
start and debugged without changing several variables at once?

**Optional illustrated explanation:** [Debugging as experiments](concepts/15-debugging-as-experiments.md)

**Prepare**

Everything in the first table is already in your purchase record. The
quantities are what this session actually consumes, not what the kit contains.

| Already in hand | Qty | What this session does with it |
| --- | --- | --- |
| Meshnology ESP32-C3 SuperMini dev board | 2 (MCU-A1 in use, plus 1 spare already gated with `esptool flash_id` at >= 4 MB) | Step 2's bare-board flash/boot reproduction; the pre-gated spare makes a suspected board fault one documented swap instead of an improvisation mid-capstone. |
| Hosyond SSD1306 OLED, 0.96 in 128x64 I2C, white | 1 (OLED-A1; 4 spares remain in the 5-pack — re-read the silkscreen pin order before substituting one) | Step 3's I2C layer and step 7's swapped SDA/SCL planted fault. |
| AITRIP INMP441 I2S MEMS microphone | 1 — stage it only if Day 9's data test passed | The conditional top layer of the bring-up ladder: L/R tied to GND for the left slot, data to GPIO4 per the firmware contract card. |
| QTEATAK 6x6 mm tactile push buttons with caps | 1 switch + 1 white cap | The first peripheral layer — GPIO10 to GND, active low, with GPIO9 left untouched as ROM BOOT. |
| LuminologyPro resistor kit, 25 values, 1/4 W | 3 pieces (2 x 10 kΩ, 1 x 100 kΩ) | One 10 kΩ as the button pull-up if the firmware's internal pull is not the documented one, one 10 kΩ to hold the GPIO2 I2S bit-clock strap at a defined level through reset, and 100 kΩ as the microphone data-line pull-down (`INVENTORY.md`). |
| REXQualis solderless breadboards (830 + 400 point) | 1 (the 830-point board) | Logic-only bring-up for controller, button, OLED, and microphone; no amplifier and no full-load current ever crosses it. |
| TODOELEC Dupont jumper kit, 10 cm | About 14 of the 120 in use (3V3, GND, GPIO20/SCL, GPIO21/SDA, GPIO10, plus 6 for the microphone), with 4 known-good spares set aside | The wiring for each ladder layer; the four spares let a suspect jumper be swapped as a single changed variable during step 7's fault diagnosis. |
| 2.54 mm male breakaway header pins | 22 pins is the entire stock — a fully socketed controller (16) + OLED (4) + microphone (6) needs 26 | Check the reserved-count record from Days 11-12 before staging and decide which module is socketed and which is jumpered directly, rather than discovering the shortfall mid-capstone. |
| KAIWEETS TRMS multimeter, 6000 counts, with hard case | 1, with both leads and the hard case | Pre-power rail isolation and ground-continuity checks at every layer, the 3V3 rail reading, the OLED carrier's onboard I2C pull-up resistance for the rise-time calculation, and the averaged idle current. |
| X-Tronic bundle: tweezers | 1 pair | Seat and lift resistors and modules without flexing pads or touching the microphone port. |
| BOENFU 6-inch flush cutters | 1 | Trim resistor leads so they seat fully in the breadboard; component leads only. |
| X-Tronic bundle: silicone work mat | 1 | Non-conductive bench surface under the breadboard stack so no stray lead finds the bench top. |
| 3M Solus 1000 safety glasses, clear | 1 | Required for every physical lab, including lead trimming. |
| Computer with Python, git, esptool, and a free USB-A port (general item — no project purchase recorded) | 1 | Step 2's flash/boot reproduction, the serial terminal for the step-5 regression logs, and the final matrix. |
| Camera or phone (general item — no project purchase recorded) | 1 | Photograph the wiring at each ladder layer before power is applied, and photograph each header joint at macro/zoom as the substituted inspection method. |
| Notebook, printed subsystem matrix, and every earlier day's lab record (general item — no project purchase recorded) | 1 notebook + 1 printed matrix + Days 1-14 records | Step 1's one-page system drawing, the symptom-to-root-cause records, and step 8's matrix with identified / wired / observed / documented / safe-to-integrate columns. |
| 2.4 GHz Wi-Fi network access (general item — no project purchase recorded) | 1 network | Step 6 only, and only if the backend/privacy decision has been explicitly recorded; otherwise network and voice behaviour stay HOLD. |

*Not in hand for this session.* Do not buy anything to stay on schedule; each
entry says what to do instead.

- **USB-A-to-C data cable with working data lines (Rankie USB 3.0 3-pack)** —
  listed under **Still needed** in `INVENTORY.md`.
  Steps 2, 3, 5, 6, and 7 all depend on flashing and monitoring the controller
  over USB — this is the single hardest blocker in the whole plan.
  `INVENTORY.md` lists the Rankie 3-pack under 'Still needed', so verify before
  you start. Prove data before trusting any result — `esptool flash_id`
  on the bare board must return the chip and flash size; a charge-only cable
  makes a working board look dead. If no data-capable cable is proven, apply
  the no-purchase rule: complete step 1's system drawing, the unpowered
  continuity and isolation measurements, the measured OLED pull-up value, and
  all of Deliverable B's calculations, then mark steps 2, 3, 5, 6, and 7
  INCONCLUSIVE in the step-8 matrix. Do not swap cables mid-run to see if it
  works.
- **Logic analyzer** — **no purchase record anywhere**.
  Deliverable C asks for I2S WS and BCLK frequencies and a decoded I2C
  transaction. Record the expected bit clock (16 kHz x 2 slots x 32 bits =
  1.024 MHz) as CALCULATED and mark measured I2S timing and the decoded I2C
  transaction INCONCLUSIVE. Drop the 'wrong logic-analyzer decoder setting'
  planted fault from step 7 and use a wrong I2C address in firmware as the
  third fault instead.
- **Two-channel oscilloscope, >=50 MHz** — **borrow or arrange access**.
  Deliverable C's I2C rise-time measurement. Lesson 13 explicitly accepts 'a
  reason your tool cannot measure it'. State the instrument limit, keep the
  pull-up rise-time figure labelled CALCULATED from the measured pull-up
  resistance and estimated bus capacitance, and mark the measured rise time
  INCONCLUSIVE.
- **Current-rated 8 ohm dummy load, current-rated leads, and a
  differential-safe speaker measurement method** — **no purchase record
  anywhere**.
  Day 10's complete powered fixture is the stated precondition for staging the
  amplifier on Day 15. Day 10 cannot have passed without these, so step 4
  stands as written: the amplifier and speaker remain absent from the bench and
  the audio row of the step-8 matrix is HOLD, not INCONCLUSIVE. Never
  earth-reference either BTL speaker lead and never improvise a load.
- **Fast current-capture instrument (>=100 kHz)** — **borrow or arrange
  access**.
  Deliverable C's rail behaviour during Wi-Fi transmit bursts and any
  millisecond-scale current peak. Report only the DMM-averaged idle current
  with its exact test conditions and evidence label. Peak demand stays
  INCONCLUSIVE and must not be used to argue any cell, fuse, switch, or wire
  size in the prioritized blocker list.
- **Magnification (loupe, visor, or bench magnifier)** — **no purchase record
  anywhere**.
  The pre-power visual inspection of soldered module headers before each new
  layer is energised. Photograph each joint with a phone camera at macro/zoom
  and inspect on screen, then record in the lab log that the inspection method
  was substituted — the joint criteria are a visual gate and the substitution
  must be visible in the evidence.
- **Grounded ESD mat and wrist strap** — **no purchase record anywhere**.
  Steps 2 through 7 repeatedly handle a bare controller and a bare MEMS
  microphone across a multi-hour session. No step is removed. Discharge on a
  grounded metal object before each handling, hold boards by their edges, and
  record the ESD-control gap in the final matrix so an intermittent later
  failure is not misdiagnosed as a wiring fault.

*Keep off the bench today.*

- All 3 HiLetgo MAX98357A amplifiers and the Same Sky CES-20134-088PM speaker —
  step 4 keeps them absent unless Day 10's complete powered fixture passed,
  which it cannot have without the dummy load and differential instrument.
- All four protected LiPo packs (2 x Adafruit #1578, 2 x Adafruit #258) and the
  Adafruit #4410 charger — terminal-protected, connectors unmated, out of the
  work area; this plan forbids preparing them.
- SKY TOPPOWER bench supply and its leads — Day 15 is USB-only; this plan
  forbids preparing the external supply.
- daier JST-PH 2.0 mm cables — no battery harness exists in the battery-free
  article, so no cell-shaped connector belongs on the bench.
- Chanzon SPDT slide switch — no isolator is part of this article and it is
  REJECTed for carrying load; leave it in its bag.
- K&S brass tube and rod and any part of the frame — this plan keeps the brass
  off this bench and the frame electrically floating.
- Harris SCLF4 acid flux and the SHJADE hot glue gun — acid flux never comes
  near electronics, and no gluing of electronics is released.
- QWORK heat gun — no hot air near a live bench article.
- Any second controller wired in parallel and any peripheral that has not
  passed its own earlier gate — the ladder adds exactly one layer at a time.

*Check before you start.*

1. Prove the USB cable carries data before anything else: with the bare board
   and nothing else connected, `esptool flash_id` must report the chip and >= 4
   MB flash. If it does not enumerate, stop and mark the flash/boot gate
   INCONCLUSIVE rather than rewiring or swapping peripherals to chase the
   symptom (`INVENTORY.md`).
2. Re-read the silkscreen pin order on the exact OLED unit you are staging —
   vendors ship GND-VCC-SCL-SDA and VCC-GND-SCL-SDA on identical-looking boards
   — and confirm it matches the pin map you drew in step 1 before any 3V3 is
   applied.
3. With USB disconnected, meter the assembled stack: 3V3-to-GND not shorted,
   every module ground common, no bridge between adjacent header pins. While
   you are there, measure the OLED carrier's onboard I2C pull-up resistance so
   Deliverable B's rise-time figure uses a measured value rather than an
   assumed one.
4. Confirm the strap and recovery pins: GPIO9 untouched and available for ROM
   BOOT, button on GPIO10 to GND, GPIO2 held at a defined level through reset,
   microphone L/R tied to GND and its data line pulled down with the 100 kΩ —
   an undefined strap makes a boot failure look like a peripheral fault.
5. Record before the first USB connection that the amplifier, speaker, all four
   cells, the charger, and the bench supply are out of the work area; that
   recorded absence is part of the capstone evidence, not a formality.

Sequence matters more than parts today: prove the cable, then the bare board,
then add one layer, run the regression, and save the serial output before the
next layer goes on — power removed before every wiring change. Header stock is
the quiet constraint: 22 pins total against 26 for a fully socketed
controller-plus-OLED-plus-microphone stack, so settle the
socketed-versus-jumpered split before the session rather than during it. Expect
the honest outcome of this capstone to include several non-passes: I2S timing
and I2C rise time INCONCLUSIVE for want of a logic analyzer and scope, audio
HOLD for want of Day 10's fixture, transient current INCONCLUSIVE for want of a
fast capture instrument, and all cell connection, charging, complete power
integration, final brass work, glue/paint, and pocket carry HOLD by the design
authority. Owning the generic Hosyond/AITRIP/HiLetgo modules makes them
learning articles, not approved final-build parts, so no matrix row may read
'safe to integrate' on ownership alone.

**Study**

- Read [Lesson 13](../edu/fundamentals/13-debugging-integration-and-capstone.md).

**Lab**

1. Draw the complete battery-free test article, including every source,
   return, rail, connector pin, I2C signal, I2S signal, boot/recovery control,
   and explicitly absent or held subsystem.
2. Cold-start the last known-good USB setup and reproduce its diagnostic boot
   log. If reflashing, the tested USB-powered peripherals may stay connected.
3. When rebuilding or adding a peripheral, use only ones that individually
   passed earlier sessions, one layer at a time. A sensible ceiling is
   controller, action button, OLED, and an
   identified INMP441 microphone on the quickstart's USB-only wiring.
4. Keep the amplifier absent and use the offline diagnostics build.
5. Run a regression after each addition and save the serial output.
6. Reproduce the button log, OLED pixel toggle, and silence-versus-speech
   microphone readings together. The optional regular-firmware/backend step in
   the quickstart follows these local checks; it is separate from this offline
   capstone and does not establish speaker output.
7. With USB removed before every change, diagnose up to three reversible
   faults: swapped OLED SDA/SCL, a disconnected OLED signal wire, or an
   intentionally wrong decoder setting. Keep all ground connections intact.
   Missing-ground and missing-I2S-clock exercises are unpowered continuity
   exercises only; restore them before applying power. Restore the last
   known-good state after each fault.
8. Complete a final matrix with one row per subsystem and columns for
   `identified`, `wired`, `observed`, `documented`, and `safe to integrate`.

**Evidence to save**

- one-page system drawing;
- ordered bring-up and regression log;
- symptom → hypotheses → test → observation → root-cause records;
- final subsystem matrix; and
- a prioritized blocker list for any future phase.

**Exit gate:** The battery-free result is reproducible, every omission is
explicit, and no unexplained failure is hidden by the phrase “it works.”

---

## Completion review

At the end of Session 15, sort every claim into three lists:

### Proven on this exact article

Include only measurements and repeatable observations tied to identified
hardware and firmware.

### Inconclusive with available equipment

Examples may include I2S waveform timing, fast transient current, differential
speaker voltage, or thermal qualification. These are not purchase requests;
they are honest limits on the current evidence.

### Held by the current design authority

This should include cell connection and charging, final cell discharge,
complete power integration, unresolved USB backfeed paths, unapproved
amplifier isolation, final brass work, glue/paint, and pocket carry unless a
later reviewed project decision explicitly releases them.

The no-purchase success target is a well-understood battery-free prototype and
nonconductive fit model. Stopping at a written gate is part of engineering, not
an incomplete homework assignment.

## One-page progress tracker

| Day | Topic | Status | Main evidence file or photo | First action next time |
| ---: | --- | --- | --- | --- |
| 1 | Safety, system map, software baseline | `NOT STARTED` |  |  |
| 2 | Units and resistor power | `NOT STARTED` |  |  |
| 3 | Series, parallel, KVL/KCL, loading | `NOT STARTED` |  |  |
| 4 | Components and RC | `NOT STARTED` |  |  |
| 5 | Measurement technique | `NOT STARTED` |  |  |
| 6 | Exact parts and controller boot | `NOT STARTED` |  |  |
| 7 | GPIO and action button | `NOT STARTED` |  |  |
| 8 | I2C and OLED | `NOT STARTED` |  |  |
| 9 | I2S and microphone | `NOT STARTED` |  |  |
| 10 | Class-D, BTL, and audio gate | `NOT STARTED` |  |  |
| 11 | Soldering practice | `NOT STARTED` |  |  |
| 12 | Wire work and rework | `NOT STARTED` |  |  |
| 13 | Power integrity, battery-free | `NOT STARTED` |  |  |
| 14 | RF and nonconductive fit mock-up | `NOT STARTED` |  |  |
| 15 | Integration and debugging capstone | `NOT STARTED` |  |  |
