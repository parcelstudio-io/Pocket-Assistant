# Three-week electronics study plan

For the current day-by-day materials lists and 2–3 hour sessions, use the
[daily study and lab plan](../plan/DAILY_STUDY_AND_LAB_PLAN.md). To start the
hardware immediately, follow the [USB prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md).
The outline below is an optional theory sequence, not a prerequisite list.
If module headers are unsoldered, do the solder practice before any peripheral
wiring, following the quickstart's header preparation step.

Fifteen two-hour sessions combine the
[foundations course](fundamentals/README.md) with battery-free bench work.
The outcome is the knowledge and evidence needed to qualify a prototype—not
permission to build a finished battery-powered device.

A useful rhythm is 45 minutes reading, 60 minutes at the bench, and 15 minutes
for the lab record. Predict before measuring. If a bench result is unexplained,
debug it and move the later sessions instead of advancing.

```text
 Week 1   quantities → circuits → components → measurement → logic
                                                       │
 Week 2   display ← I2C      microphone ← I2S → amplifier → soldering
                                                       │
 Week 3   power theory → bench fixture → rework → RF/fit → integration
```

## Before starting

Use a clear, well-lit, ventilated work area with eye protection and a
current-limited bench supply. Have a fused multimeter, breadboard, insulated
wire, resistors, LEDs, capacitors, and sacrificial perfboard available for the
relevant circuit labs. The quickstart needs only its listed owned parts for
each stage. Follow its USB wiring for the controller and low-current
peripherals; the [current material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md)
concerns the later amplifier and portable-power fixtures.

Keep lithium cells terminal-protected and outside the work area throughout
this plan. Use inert size/weight dummies for fit checks. Structural metalwork
and finish work happen with all electronics and stored-energy devices removed.

Copy the [lab record template](fundamentals/reference/lab-record-template.md)
for every experiment.

## Week 1 — Electrical foundations

### Session 1: safety, evidence, and units

Read [Lesson 00](fundamentals/00-safety-evidence-and-course-map.md) and
[Lesson 01](fundamentals/01-units-charge-voltage-current-power-energy-heat.md).

At the bench, inspect the workspace and meter leads, identify the fused current
jack, measure several de-energized resistors, and verify continuity on a loose
wire and open circuit. Record instrument identity, range, prediction, result,
and uncertainty.

### Session 2: DC circuits

Read [Lesson 02](fundamentals/02-dc-circuits-ohm-kirchhoff-series-parallel.md).

With a current-limited bench source, build a resistor divider and then an LED
with a calculated current-limiting resistor. Predict each node voltage and
current before measuring it; explain the difference between prediction and
result.

### Session 3: components and time constants

Read [Lesson 03](fundamentals/03-components-rc-diodes-mosfets-converters.md).

Identify resistor, capacitor, diode, and transistor markings. Measure an RC
charge curve at several time points and compare it with the calculated time
constant. Discharge the capacitor safely before changing the circuit.

### Session 4: measurement technique

Read [Lesson 05](fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md).

Practice voltage measurement in parallel and current measurement in series on
the low-energy resistor circuit. Move the lead back to the voltage jack as soon
as the current measurement is complete. Measure wire voltage drop under load
and document the setup well enough to reproduce it.

**Never connect a meter in current mode directly across a source.**

### Session 5: digital logic and first boot

Read [Lesson 07](fundamentals/07-digital-logic-gpio-pullups-boot-straps.md).

Using only the reviewed service connection, boot one bare controller, capture
its identity and serial output, and verify that recovery controls remain
accessible. Do not attach project peripherals yet. Record unexpected boot-pin
levels instead of experimenting blindly with strap pins.

## Week 2 — Interfaces, audio, and soldering

### Session 6: I2C and the display

Read [Lesson 08](fundamentals/08-i2c-and-the-oled.md).

Verify the received display's controller and pin order before power is applied.
On the quickstart's USB fixture, record the address log and toggle the OLED
pixel test with GPIO10. Capture waveforms if an instrument is available. Then
test the firmware's headless behavior with the display absent.

### Session 7: I2S and microphone input

Read [Lesson 09](fundamentals/09-i2s-sampling-and-digital-audio.md) and the
[logical contract](01-how-it-fits-together.md#corrected-source-logical-contract).

Use the quickstart's owned INMP441 pin map after checking the received
carrier's labels. Save its offline `MIC24` statistics during quiet and speech,
and record the firmware identity. Word-select/bit-clock timing captures are
an optional extension when an instrument is available.

### Session 8: bridge amplifier and speaker path

Read [Lesson 10](fundamentals/10-class-d-btl-speakers-and-acoustics.md).

Start with the approved amplifier fixture and an 8 Ω dummy load. Confirm
shutdown state, supply current, differential output, and idle heating. A
speaker may be introduced at low volume only after the applicable current
material gates allow it.

**Neither BTL output is ground.** Never connect either speaker lead to circuit
ground, an earth-referenced probe ground, or the metal frame.

### Session 9: through-hole soldering

Read the first half of
[Lesson 12](fundamentals/12-soldering-mechanics-insulation-tolerance.md).

Make about 30 resistor-to-perfboard joints on sacrificial material. Inspect
wetting, fillet shape, solder quantity, bridges, and heat damage under
magnification. Continue until ten consecutive joints meet your written visual
criteria.

### Session 10: wire work and strain relief

Finish [Lesson 12](fundamentals/12-soldering-mechanics-insulation-tolerance.md).

Practice at least 20 wire-to-pad joints and 10 insulated wire splices, including
both intended wire sizes. Add strain relief, inspect under magnification, then
perform a documented pull test on sacrificial samples. Rework any joint whose
failure mode is not understood.

## Week 3 — Power, mechanics, and integration

### Session 11: power integrity and heat

Read [Lesson 06](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md).

From the current material decision, list each allowed experiment's voltage,
current limit, expected load, cutoff behavior, and stop conditions. Calculate
expected loss and temperature-rise questions. No cell is used.

### Session 12: battery-free power fixture

Exercise only the currently approved battery-free fixture with a
current-limited bench supply. Sweep the permitted input range and workload
while recording input/output voltage, current, startup behavior, transients,
and temperature. Stop on instability, unexpected heating, odor, damage, or a
limit violation.

This session produces evidence for the exact tested article; it does not
automatically release a battery subsystem.

### Session 13: datasheets and rework

Read [Lesson 04](fundamentals/04-boards-schematics-datasheets-and-connectors.md).

Choose several sacrificial joints from Sessions 9–10. Record pad and part
orientation, desolder them with appropriate tools, inspect for lifted pads or
heat damage, and restore them. The pass condition is a correct replacement
with intact substrate and continuity—not merely a shiny surface.

### Session 14: RF, enclosure, and dry fit

Read [Lesson 11](fundamentals/11-rf-emc-antennas-and-metal-frame.md).

Make a 1:1 nonconductive mock-up using measurements from the exact received
parts and an inert cell dummy. Check antenna space, acoustic paths, wire bends,
connector and recovery access, insulation, fasteners, and removal sweeps.
Nothing is cut from the final metal stock.

### Session 15: systematic integration

Read [Lesson 13](fundamentals/13-debugging-integration-and-capstone.md).

Write the bring-up order, measurement points, expected observations, and
rollback condition for each layer. Practice structural joining on offcuts with
all electronics absent if that process has its own approved safety setup.
Integrate only the battery-free stages currently permitted by the material
decision.

## After the course

Use the
[promotion gates in the current material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md#promotion-gates-before-claude-may-say-final-go)
and a separate lab record for each exact article. Do not substitute archived
assembly recipes, visual inspection, or a successful software build for those
gates.

The rules that never bend:

1. Never solder to, heat, puncture, strip, crush, or deliberately short a
   lithium cell.
2. Never place a current-mode meter directly across a source.
3. Never treat the conductive frame or either BTL speaker lead as ground.
4. Never advance past an unexplained failure or a written stop condition.
