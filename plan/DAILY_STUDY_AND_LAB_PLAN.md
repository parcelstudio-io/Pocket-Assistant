# 15-session Pocket AI study and lab plan

This plan turns the electronics course into fifteen practical sessions of
about 2–3 hours each. It is written for a software engineer who learns best by
building a small piece, observing it, and then studying the theory that explains
the result.

The objective is not to read all of `edu/` before touching hardware. The
objective is to create one new piece of trustworthy evidence each session.
Do not read this entire plan in one sitting: read the ground rules once, then
open only the section for the day you are working on.

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
project authority is
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md); the old
step-by-step build and wiring guides are archived references, not current
assembly instructions.

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

## Non-negotiable boundaries for all 15 sessions

- Keep every lithium cell terminal-protected, electrically disconnected, and
  outside the active work area. Do not probe, connect, charge, discharge,
  solder, heat, bend, clamp, puncture, or unwrap it.
- Use USB only on a bare controller with external power, 3.3 V, and amplifier
  harnesses detached. Never connect both device USB-C ports.
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

Use the full
[lab record template](../edu/fundamentals/reference/lab-record-template.md) for
each powered experiment. At minimum, record the test-article ID, one question,
prediction, diagram, current limit, stop conditions, acceptance rule, results,
and next action.

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

Choose and record one firmware contract before connecting a peripheral. A
temporary bare-board vendor-image smoke test is fine, but its wiring map must
not be carried into the corrected-source build by memory.

| Property | Pinned vendor image | Corrected source build |
| --- | --- | --- |
| Microphone data | GPIO8 | GPIO4 |
| Audio sample rate | 24 kHz | 16 kHz |
| Expected I2S bit clock | Contract-specific; verify | 1.024 MHz |
| OLED address | `0x3C` | `0x3C` or `0x3D` |
| Editable | No | Yes |

Both use GPIO1 for I2S word select, GPIO2 for I2S bit clock, GPIO3 for speaker
data, GPIO20 for OLED SCL, GPIO21 for OLED SDA, and GPIO10 for the optional
active-low action button. Verify the current firmware files rather than relying
only on this summary.

The default Xiaozhi/Tenclass service receives device metadata and microphone
audio. Do not provision Wi-Fi or perform a voice test until you have made and
recorded a privacy/backend decision.

---

## Week 1 — Build the electrical foundation

### Day 1 — System map, safety, and a green software baseline

**Status:** `NOT STARTED`

**Question:** What is the system made of, and what work is currently allowed?

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
   python3 tools/pocket_ai_device.py verify
   ```

**Evidence to save**

- the system diagram;
- a photograph of the labeled, unpowered parts;
- the three command outputs; and
- five sentences distinguishing `DATASHEET`, `TYPICAL`, `ASSUMED`,
  `CALCULATED`, and `MEASURED` evidence.

**Exit gate:** You can explain the complete signal path, name the current source
of assembly authority, and state why software checks do not prove physical
power or audio behavior.

### Day 2 — Voltage, current, resistance, power, and units

**Status:** `NOT STARTED`

**Question:** Can measured voltage and resistance predict current and resistor
power?

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

**Study**

- Read the identity, pinout, datasheet, and connector sections of
  [Lesson 04](../edu/fundamentals/04-boards-schematics-datasheets-and-connectors.md).
- Read the [host-tools guide](../tools/README.md).
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
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --requirement tools/requirements.txt

python tools/pocket_ai_device.py verify
python tools/pocket_ai_device.py ports
python -m esptool --chip esp32c3 --port <PORT> flash-id
python tools/pocket_ai_device.py info --port <PORT>
python tools/pocket_ai_device.py flash --port <PORT> --dry-run
```

Replace `<PORT>` with the explicitly observed USB serial port. Require an
ESP32-C3 and at least 4 MB of flash. If that gate passes, flash and monitor:

```bash
python tools/pocket_ai_device.py flash --port <PORT>
python tools/pocket_ai_device.py monitor --port <PORT>
```

Flashing at `0x0` replaces the complete image and clears stored Wi-Fi data.
The board must remain bare: no display, microphone, amplifier, external power,
or battery harness.

If choosing the corrected-source image instead, run its verifier first:

```bash
python3 firmware/scripts/verify_source_build.py
```

Do not bypass any manifest, input-hash, size, or digest failure. At the time
this plan was written, the local corrected-source verification reports an
input-hash mismatch, so that path must be reconciled or rebuilt before use.
The pinned vendor image is the simpler bare-board smoke-test path.

**Evidence to save**

- board evidence sheet and photographs;
- flash ID, image digest, explicit port, flash transcript, and complete boot
  log; and
- a label on the board record: `VENDOR / MIC GPIO8` or
  `CORRECTED SOURCE / MIC GPIO4`.

**Exit gate:** The exact board has at least 4 MB flash, the selected artifact
passes its verifier, and the controller produces a stable, understood boot log.

### Day 7 — Digital logic and the action button

**Status:** `NOT STARTED`

**Question:** Can one input have a defined released state and a repeatable
active-low pressed state?

**Study**

- Read [Lesson 07](../edu/fundamentals/07-digital-logic-gpio-pullups-boot-straps.md),
  focusing on GPIO modes, floating inputs, pull resistors, and boot straps.

**Lab**

1. With USB disconnected, identify the exact button terminals using
   continuity mode.
2. Draw the intended active-low circuit before wiring it.
3. Use GPIO10 for the project action button. Keep GPIO9 available exclusively
   for ROM BOOT/recovery.
4. Use the selected firmware's documented pull configuration or an explicitly
   reviewed external pull-up; do not assume both simultaneously.
5. Connect USB and observe/log released and pressed states. Test multiple
   presses without changing wiring.
6. Disconnect USB before altering or removing the circuit.

If the selected firmware does not expose a useful button log, complete the
unpowered switch test and write the smallest appropriate GPIO test program as
a software exercise. Do not move to an undocumented pin for convenience.

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

**Study**

- Read [Lesson 08](../edu/fundamentals/08-i2c-and-the-oled.md).

**Lab**

1. Create an evidence sheet for `OLED-A1`. Record both-side photographs,
   markings, physical pin order, dimensions, and the evidence for its supply
   voltage. Similar-looking OLED carriers can swap VCC and GND positions.
2. Keep the battery, converter, microphone, amplifier, and speaker absent.
3. With USB disconnected, connect only documented ground, supply, GPIO20/SCL,
   and GPIO21/SDA using short jumpers.
4. Inspect for reversed power and shorts before connecting USB.
5. Measure the OLED rail, scan or observe the address, and run the available
   initialization/all-pixel test.
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

**Study**

- Read [Lesson 09](../edu/fundamentals/09-i2s-sampling-and-digital-audio.md)
  through Stage 2 of its safe staged lab.

**Lab**

1. Create an evidence sheet for `MIC-A1`. Verify the carrier's physical pin
   order and voltage; the IC family name does not prove the breakout layout.
2. Calculate the expected clock from sample rate, slots, and bits per slot.
   For corrected source, show `16,000 x 2 x 32 = 1.024 MHz`.
3. Confirm the selected contract again: vendor microphone data is GPIO8;
   corrected-source microphone data is GPIO4. Never connect both.
4. With USB disconnected, attach only the reviewed low-current microphone
   fixture, including its documented left-slot selection.
5. Reconnect USB and record samples or firmware diagnostics during silence,
   normal speech, and a gentle tone.
6. If a suitable logic analyzer is already available, measure WS and BCLK.
   Otherwise mark waveform/rate confirmation `INCONCLUSIVE`; do not purchase an
   instrument merely to complete the day.

Do not energize a generic carrier whose pin order or permitted use remains
unresolved. An unpowered evidence sheet plus source-level signal trace is a
valid `HOLD` outcome.

**Evidence to save**

- microphone pin map and firmware-contract label;
- expected clock calculation;
- sample/log observations; and
- measured clock values or an explicit instrument limitation.

**Exit gate:** Silence and speech produce distinguishable, non-stuck data, or
the powered test is correctly held with the missing evidence named.

### Day 10 — Class-D, BTL, speaker limits, and the audio gate

**Status:** `NOT STARTED`

**Question:** What must be true before it is safe and meaningful to power the
amplifier and speaker?

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

**Study**

- Read [Lesson 13](../edu/fundamentals/13-debugging-integration-and-capstone.md).

**Lab**

1. Draw the complete battery-free test article, including every source,
   return, rail, connector pin, I2C signal, I2S signal, boot/recovery control,
   and explicitly absent or held subsystem.
2. Start from the bare controller and reproduce its flash/boot result.
3. Add only peripherals that individually passed earlier sessions, one layer
   at a time. A sensible ceiling is controller, action button, OLED, and an
   approved low-current microphone on the documented USB-only fixture.
4. Leave the amplifier absent unless Day 10's complete powered fixture passed.
5. Run a regression after each addition and save the serial output.
6. If the backend privacy decision is accepted, provision only a 2.4 GHz
   network and record one non-sensitive service interaction. Otherwise keep
   network/voice behavior `HOLD`; local hardware evidence remains valuable.
7. With power removed before every change, diagnose up to three safe planted
   faults such as swapped OLED SDA/SCL, a removed common ground, or an
   intentionally wrong decoder/address setting. Restore the last known-good
   state after each fault.
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
