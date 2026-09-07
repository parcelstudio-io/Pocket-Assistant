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

### Electronics and passive components

| Item referenced by the plan | Purchased item and product link | Used on |
| --- | --- | --- |
| ESP32-C3 controller | Meshnology/plain ESP32-C3 SuperMini 10-pack — [Amazon B0F888JQ91](https://www.amazon.com/dp/B0F888JQ91) | Days 1, 6–10, 14–15 |
| OLED | Hosyond 0.96-inch white SSD1306 I2C 5-pack — [Amazon B09T6SJBV5](https://www.amazon.com/dp/B09T6SJBV5) | Days 1, 6, 8, 14–15 |
| I2S microphone | AITRIP/INMP441 5-pack — [Amazon B092HWW4RS](https://www.amazon.com/dp/B092HWW4RS) | Days 1, 6, 9–10, 14–15 |
| I2S amplifier | HiLetgo MAX98357A 3-pack — [Amazon B0CDWXZZCH](https://www.amazon.com/dp/B0CDWXZZCH) | Days 1, 6, 9–10, 13–14 |
| Speaker | Same Sky CES-20134-088PM, 8 ohm/0.8 W — [DigiKey 2223-CES-20134-088PM-ND](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) | Days 1, 6, 10, 14 |
| Action button | QTEATAK 6x6 mm tactile-switch and cap kit — [Amazon B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4) | Days 1, 6–8, 14–15 |
| Resistors, including 1 kohm, 2.2 kohm, 10 kohm, and 100 kohm | LuminologyPro 1/4 W resistor kit — [Amazon B0F4P352BB](https://www.amazon.com/dp/B0F4P352BB) | Days 2–5, 7, 11, 13 |
| Ceramic capacitors | BOJACK ceramic-capacitor kit — [Amazon B07P7HRGT9](https://www.amazon.com/dp/B07P7HRGT9) | Days 4 and 13 |
| Electrolytic capacitors, including 100 uF and 220 uF | ALLECIN electrolytic-capacitor kit — [Amazon B0C1VBXCQM](https://www.amazon.com/dp/B0C1VBXCQM) | Days 4 and 13 |
| Protected 500 mAh LiPo | Adafruit #1578 — [Adafruit product 1578](https://www.adafruit.com/product/1578) | Storage boundary and Day 14 inert mock-up only |
| Protected 1200 mAh LiPo | Adafruit #258 — [Adafruit product 258](https://www.adafruit.com/product/258) | Storage boundary and Day 14 inert mock-up only |
| USB-C LiPo charger | Adafruit #4410 — [Adafruit product 4410](https://www.adafruit.com/product/4410) | Storage/source-state discussion only |
| Slide switch | Chanzon/SS12D00-class SPDT 25-pack — [Amazon B09R434VJQ](https://www.amazon.com/dp/B09R434VJQ) | Day 13 unpowered or currently permitted testing only |
| LED | Exact purchase URL `not recorded` | Optional Day 7 extension |
| 2.54 mm breakaway headers | Exact purchase URL `not recorded`; recorded in Amazon order #4 | Days 11–12 |
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
| USB-A-to-C data cable | Rankie USB 3.0 3-pack — [Amazon B01JRY0VE4](https://www.amazon.com/Rankie-USB-C-Charging-Transfer-3-Pack/dp/B01JRY0VE4) | Days 6–10 and 14–15 |
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
| Solder wick | JoTownCand 3-pack — [Amazon B0DRN688Q5](https://www.amazon.com/JoTownCand-Premium-Desoldering-Residue-Solder/dp/B0DRN688Q5) | Day 12 |
| Heat gun | QWORK 300 W with stand — [Amazon B09NDCCW29](https://www.amazon.com/QWORK-Shrink-Shrinking-Wrapping-Embossing/dp/B09NDCCW29) | Day 12, with cells absent |
| 30 AWG signal wire | CBAZY silicone-wire kit — [Amazon B073RDGTPB](https://www.amazon.com/dp/B073RDGTPB) | Days 11–12 and mock-up planning |
| 26 AWG power wire | TUOFENG silicone-wire kit — [Amazon B07G2LRX68](https://www.amazon.com/dp/B07G2LRX68) | Days 11–12 and unpowered planning |
| Heat-shrink tubing | Pointool 14-size white kit — [Amazon B08N4W4K9X](https://www.amazon.com/dp/B08N4W4K9X) | Day 12 |
| Sacrificial perfboard | Exact purchase URL `not recorded`; use only if already owned | Days 11–12 |
| Magnification and fume extraction/ventilation | Exact purchase URL `not recorded` | Days 11–12 |

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

**Prepare**

- [ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91),
  [Hosyond OLED](https://www.amazon.com/dp/B09T6SJBV5),
  [INMP441 microphone](https://www.amazon.com/dp/B092HWW4RS),
  [MAX98357A amplifier](https://www.amazon.com/dp/B0CDWXZZCH), and
  [Same Sky speaker](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309), all unpowered;
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW), with its leads
  disconnected while inspecting the jacks;
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM); and
- existing computer, camera/phone, notebook, and drawing paper—no dedicated
  purchase link was recorded for these general tools.

Do not prepare the cells or charger; confirm they remain terminal-protected and
away from the work area.

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

**Prepare**

- [LuminologyPro resistor kit](https://www.amazon.com/dp/B0F4P352BB), including
  one nominal 1 kohm, 1/4 W resistor;
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- [SKY TOPPOWER current-limited supply](https://www.amazon.com/dp/B0BN1F6CGZ);
- REXQualis breadboard and TODOELEC jumpers—the exact purchase URLs were not
  preserved in the repository; and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), notebook, and
  calculator.

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

**Prepare**

- [LuminologyPro resistor kit](https://www.amazon.com/dp/B0F4P352BB): one
  1 kohm, one 2.2 kohm, and three 10 kohm resistors;
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- [SKY TOPPOWER current-limited supply](https://www.amazon.com/dp/B0BN1F6CGZ);
- REXQualis breadboard and TODOELEC jumpers—exact purchase URLs not recorded;
  and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), notebook, and
  calculator.

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

**Prepare**

- [LuminologyPro resistor kit](https://www.amazon.com/dp/B0F4P352BB), including
  one 100 kohm resistor;
- [ALLECIN electrolytic-capacitor kit](https://www.amazon.com/dp/B0C1VBXCQM),
  including one known-polarity 100 uF capacitor rated at least 6.3 V;
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- [SKY TOPPOWER current-limited supply](https://www.amazon.com/dp/B0BN1F6CGZ);
- REXQualis breadboard and TODOELEC jumpers—exact purchase URLs not recorded;
  and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), notebook, and a
  phone/stopwatch.

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

**Prepare**

- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW), its manual, and
  intact leads/fuse;
- [SKY TOPPOWER current-limited supply](https://www.amazon.com/dp/B0BN1F6CGZ)
  and its insulated leads;
- [LuminologyPro resistor kit](https://www.amazon.com/dp/B0F4P352BB), including
  1 kohm and other low-energy test values;
- REXQualis breadboard and TODOELEC jumpers—exact purchase URLs not recorded;
  and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), notebook, and
  calculator.

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

**Prepare**

- one plain [ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91);
- one [Rankie USB-A-to-C data cable](https://www.amazon.com/Rankie-USB-C-Charging-Transfer-3-Pack/dp/B01JRY0VE4);
- [Neiko digital caliper](https://www.amazon.com/dp/B000GSLKIW);
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW), used only for
  the day's planned unpowered checks;
- existing computer with Python, Git, and an available USB-A port; and
- camera/phone, ruler, labels, and notebook—general tools with no recorded
  purchase URLs.

The first flash uses a bare board. If its headers need soldering before Day 7,
prepare the [Day 11 soldering materials](#day-11--soldering-practice-before-project-hardware)
for a separate session with USB unplugged. Do not prepare the amplifier,
external supply, charger, or cells.

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

**Prepare**

- the Day 6-qualified [ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91)
  and [Rankie USB data cable](https://www.amazon.com/Rankie-USB-C-Charging-Transfer-3-Pack/dp/B01JRY0VE4);
- one [QTEATAK tactile button](https://www.amazon.com/dp/B0FHW6HMG4);
- [LuminologyPro resistor kit](https://www.amazon.com/dp/B0F4P352BB), including
  1 kohm and 10 kohm values as required by the chosen test circuit;
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- REXQualis breadboard and TODOELEC jumpers—exact purchase URLs not recorded;
- optional LED—exact purchase URL not recorded; do not buy one for this day;
  and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM) and notebook.

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

**Prepare**

- the qualified [ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91)
  and [Rankie USB data cable](https://www.amazon.com/Rankie-USB-C-Charging-Transfer-3-Pack/dp/B01JRY0VE4);
- one identified [Hosyond SSD1306 OLED](https://www.amazon.com/dp/B09T6SJBV5);
- the Day 7 [QTEATAK button](https://www.amazon.com/dp/B0FHW6HMG4) for toggling
  the diagnostic pixel test;
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- REXQualis breadboard and TODOELEC jumpers—exact purchase URLs not recorded;
- optional logic analyzer—no purchase is recorded; omit rather than buying;
  and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), camera, and
  notebook.

Keep the microphone, amplifier, speaker, external supply, charger, and cells
away from the setup.

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

**Prepare**

- the qualified [ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91)
  and [Rankie USB data cable](https://www.amazon.com/Rankie-USB-C-Charging-Transfer-3-Pack/dp/B01JRY0VE4);
- one identified [AITRIP/INMP441 microphone](https://www.amazon.com/dp/B092HWW4RS);
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- REXQualis breadboard and TODOELEC jumpers—exact purchase URLs not recorded;
- optional logic analyzer—no purchase is recorded; omit rather than buying;
  and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), camera, and
  notebook.

Do not prepare the amplifier, speaker, external supply, charger, or cells.

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

**Prepare**

- one unpowered [HiLetgo MAX98357A amplifier](https://www.amazon.com/dp/B0CDWXZZCH);
- the [Same Sky CES-20134-088PM speaker](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309);
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- notebook, calculator, camera, and drawing paper—general tools with no
  recorded product URLs; and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM).

For the conditional powered extension only, also prepare the
[SKY TOPPOWER current-limited supply](https://www.amazon.com/dp/B0BN1F6CGZ),
an approved 8 ohm dummy load/current-rated leads, and differential-safe
measurement equipment. No exact purchase URLs are recorded for the approved
dummy-load fixture or differential instrument. If either is unavailable, do
only the unpowered lab and mark powered audio `HOLD`.

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

**Prepare**

- X-Tronic 3020-XTS station, holder/helping hands, and silicone mat—exact
  purchase URL not recorded;
- [MAIYUM 63/37 electronics solder](https://www.amazon.com/dp/B076QF1Y85);
- Chip Quik CQ4LF electronics flux—exact purchase URL not recorded;
- sacrificial perfboard—exact purchase URL not recorded; use only if owned;
- [LuminologyPro resistors](https://www.amazon.com/dp/B0F4P352BB) and spare
  2.54 mm headers—the header purchase URL was not recorded;
- [CBAZY 30 AWG wire](https://www.amazon.com/dp/B073RDGTPB) and
  [TUOFENG 26 AWG wire](https://www.amazon.com/dp/B07G2LRX68);
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW) for unpowered
  continuity/isolation checks; and
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), ventilation/fume
  capture, magnification, camera, and notebook. Exact purchase URLs for the
  latter general bench items were not recorded.

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

**Prepare**

- the Day 11 X-Tronic station setup—exact purchase URL not recorded;
- [MAIYUM 63/37 solder](https://www.amazon.com/dp/B076QF1Y85) and Chip Quik
  CQ4LF electronics flux—the flux purchase URL was not recorded;
- [Hakko CSP-30-1 wire stripper](https://www.amazon.com/dp/B00FZPHMUG);
- [CBAZY 30 AWG wire](https://www.amazon.com/dp/B073RDGTPB),
  [TUOFENG 26 AWG wire](https://www.amazon.com/dp/B07G2LRX68), and
  [Pointool heat-shrink](https://www.amazon.com/dp/B08N4W4K9X);
- [JoTownCand solder wick](https://www.amazon.com/JoTownCand-Premium-Desoldering-Residue-Solder/dp/B0DRN688Q5);
- [QWORK heat gun](https://www.amazon.com/QWORK-Shrink-Shrinking-Wrapping-Embossing/dp/B09NDCCW29), used only with every cell outside the work area;
- sacrificial perfboard, spare headers, and practice wire joints—exact
  purchase URLs not recorded; and
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW),
  [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), ventilation,
  magnification, camera, and notebook.

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

**Prepare**

- [SKY TOPPOWER current-limited supply](https://www.amazon.com/dp/B0BN1F6CGZ)
  and insulated leads;
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- [LuminologyPro resistor kit](https://www.amazon.com/dp/B0F4P352BB) for a
  low-energy load;
- [BOJACK ceramic capacitors](https://www.amazon.com/dp/B07P7HRGT9) and
  [ALLECIN electrolytic capacitors](https://www.amazon.com/dp/B0C1VBXCQM) for
  identification/calculation work, not automatic installation;
- one unpowered [Chanzon slide switch](https://www.amazon.com/dp/B09R434VJQ)
  if inspecting the older purchased candidate;
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), notebook,
  calculator, and drawing paper; and
- an exact converter only if it is already owned and currently permitted. No
  confirmed purchase URL for an approved converter is preserved in the
  inventory.

Do not prepare a controller, amplifier, charger, battery harness, or cell for
the powered resistor-load portion.

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

**Prepare**

- [Neiko digital caliper](https://www.amazon.com/dp/B000GSLKIW), ruler,
  notebook, marker, and camera;
- clean reused cardboard/paper and removable tape—no dedicated purchase link
  is required;
- unpowered [ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91),
  [Hosyond OLED](https://www.amazon.com/dp/B09T6SJBV5),
  [INMP441 microphone](https://www.amazon.com/dp/B092HWW4RS),
  [MAX98357A amplifier](https://www.amazon.com/dp/B0CDWXZZCH),
  [Same Sky speaker](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309), and
  [QTEATAK button](https://www.amazon.com/dp/B0FHW6HMG4);
- printed dimensions from the [Adafruit #1578](https://www.adafruit.com/product/1578)
  and [Adafruit #258](https://www.adafruit.com/product/258) pages for making an
  inert cell dummy—do not bring either real cell to the bench;
- [fish paper](https://www.amazon.com/dp/B0GZVDKBBS) and
  [Kapton tape](https://www.amazon.com/dp/B072Z92QZ2) for measuring reserved
  insulation thickness only; and
- optional uncut [K&S #9831 brass tube](https://www.amazon.com/dp/B005WPAW9M)
  plus the qualified bare controller and
  [Rankie USB cable](https://www.amazon.com/Rankie-USB-C-Charging-Transfer-3-Pack/dp/B01JRY0VE4)
  for the controlled RF comparison.

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

**Prepare**

- the qualified [ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91)
  and [Rankie USB data cable](https://www.amazon.com/Rankie-USB-C-Charging-Transfer-3-Pack/dp/B01JRY0VE4);
- only peripherals that passed earlier gates: the
  [QTEATAK action button](https://www.amazon.com/dp/B0FHW6HMG4),
  [Hosyond OLED](https://www.amazon.com/dp/B09T6SJBV5), and conditionally the
  [INMP441 microphone](https://www.amazon.com/dp/B092HWW4RS);
- [KAIWEETS multimeter](https://www.amazon.com/dp/B08BL288LW);
- REXQualis breadboard and TODOELEC jumpers—exact purchase URLs not recorded;
- [3M safety glasses](https://www.amazon.com/dp/B016KZ1ZPM), notebook, camera,
  all earlier lab records, and a printed/handwritten subsystem matrix; and
- access to a 2.4 GHz network only if the backend/privacy decision was
  explicitly accepted.

Keep the amplifier, external supply, charger, battery harness, cells, and brass
frame outside this USB-only capstone. A later audio fixture is a separate setup.

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
