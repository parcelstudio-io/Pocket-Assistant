# 13 — Systematic debugging and the capstone

## Learning objectives

After this lesson, you should be able to:

- bring up a mixed power, digital, audio, and RF system one layer at a time;
- turn a vague symptom into competing, testable hypotheses;
- choose a measurement that separates those hypotheses;
- distinguish diagnosis from qualification and qualification from release;
- write a test plan with conditions, stop rules, and acceptance limits;
- complete a battery-free capstone that exercises the whole course.

## Debugging is information gathering

“The OLED does not work” is a symptom, not a cause. Possible causes include:

- no input power;
- missing or low 3V3 rail;
- reversed connector pins;
- no common return;
- firmware using different GPIOs;
- absent or excessive I2C pull-ups;
- wrong address;
- reset or boot failure;
- a solder open/bridge; or
- a damaged or different module revision.

Changing several things at once may hide the cause. Good debugging finds the
cheapest safe observation that separates hypotheses.

## The bring-up ladder

Do not assemble every subsystem and then apply cell power. Move through layers:

```text
0  documents and exact part identity
          ↓
1  visual and mechanical inspection, power off
          ↓
2  continuity, isolation, and resistance sanity, power off
          ↓
3  input path and rails from a current-limited supply
          ↓
4  controller boot and serial log
          ↓
5  one digital bus and one peripheral at a time
          ↓
6  audio at low level, then controlled load changes
          ↓
7  transient, fault-containment, and thermal tests
          ↓
8  enclosure, acoustic, control-access, and RF A/B tests
          ↓
9  protected cell integration only after an explicit release review
```

At each layer, define what “pass” means before testing. If a lower layer fails,
do not debug a higher one. A protocol trace is meaningless if the target rail
is absent.

## Step 0: freeze the test article, not the design forever

Record enough identity that a result applies to one known article:

- exact seller/manufacturer and order code;
- photographs of both sides and visible chip markings;
- measured dimensions, connector pitch, pin labels, and pin order;
- schematic/BOM revision;
- firmware commit and build command;
- configuration, jumpers, and wiring map; and
- serial number or simple unit label.

“ESP32-C3 SuperMini” or “0.96-inch OLED” describes a family of marketplace
boards, not a controlled electrical part. If a later shipment changes layout,
repeat incoming inspection and affected qualification tests.

## Steps 1–2: unpowered evidence

Inspect under magnification for bridges, whiskers, reversed parts, pin-order
mistakes, exposed conductor near metal, solder balls, cut insulation, and
strained pads.

With power off and capacitors discharged:

1. verify intended grounds are continuous;
2. verify the positive rail is not shorted to ground;
3. verify each signal reaches its intended endpoint and no adjacent pin;
4. verify switches and removable isolation links in every position;
5. verify the frame is isolated from both rails and BTL speaker outputs; and
6. record actual readings, not only a beep.

A low initial resistance that rises can be capacitors charging from the
meter. Compare polarity and repeat; use the schematic rather than declaring a
short from one number.

## Step 3: power as its own subsystem

Disconnect expensive or sensitive loads where possible. Use a current-limited
supply in place of the battery and test the input/protection/converter path.

Measure:

- polarity and rail voltage at no load and controlled loads;
- startup at the lowest intended input, not only operation after startup;
- rail behavior during a load step;
- voltage drop across each important path segment;
- quiescent and operating current; and
- temperature rise after reaching thermal equilibrium.

Do not infer converter capability from its controller IC headline. Module
inductor, layout, thermal path, capacitors, protection devices, and input leads
all matter. Do not call a room-temperature ten-start sample test a universal
guarantee; record the sample, ramp, load, and temperature.

## Step 4: establish a heartbeat

Power only the controller by its documented service method. Confirm:

- enumeration or serial output;
- reset reason;
- expected firmware version;
- no boot loop;
- known idle current; and
- GPIO assignment printed by the build or documented from source.

A repeated reboot is often a power symptom, not “bad code.” Capture the rail
and reset log together before changing firmware.

## Step 5: one bus, one device

For I2C, begin with the controller and one OLED. Run an address scan, then add
the second OLED. Record addresses and pull-up resistance. Capture SDA/SCL if
the scan fails.

For I2S, first confirm clock frequencies without the amplifier or microphone,
then add one endpoint. Verify `BCLK`, `WS`, data direction, slot format, and
word length against source and datasheets. Short digital wires are helpful but
do not make signal integrity automatic.

For any failed peripheral, ask in this order:

```text
correct power and return?
→ correct pin order and voltage level?
→ correct reset/enable/strap state?
→ expected clock/activity?
→ expected address or data format?
→ analog edge/timing margin?
→ exact module fault or incompatibility?
```

## Step 6: add energy-producing loads carefully

An amplifier and speaker can create large, fast current changes. Begin with a
low digital level and a current-limited 3.3 V source. Confirm the speaker is
connected only between the two BTL outputs; neither lead goes to ground.

Observe rail voltage and current while increasing the level in controlled
steps. Stop for clipping, resets, unexpected CC operation, heating, or
mechanical buzzing. Test microphone capture before closing the acoustic path.

## Steps 7–8: qualification is wider than “works once”

Functional bring-up proves an article operated under one condition.
Qualification asks whether it meets stated limits across intended conditions.

| Domain | Example question | Evidence needed |
| --- | --- | --- |
| Power | Does 3V3 stay in bounds during worst credible transient? | scope trace at load, defined input/load/temp |
| Startup | Can it cold-start at minimum intended input? | repeated starts with controlled input ramp and load |
| Thermal | Is every accessible/critical part within its limit? | stabilized temperatures under defined high-average use |
| I2C | Do both exact OLEDs ACK with adequate edge timing? | scan plus captured rise time and logic levels |
| Audio | Is speech intelligible without resets/clipping? | waveform/current plus repeatable acoustic test |
| RF | What does the final frame do relative to the bare baseline? | repeated A/B RSSI/loss/throughput trials |
| Mechanical | Can it be assembled, controlled, and serviced safely? | exact-part fit, plug/cable/tool/removal-path checks |
| Faults | Does a single foreseeable fault become hazardous? | reviewed fault table and safe, bounded tests |

Set quantitative limits from applicable datasheets and project requirements.
Do not invent a limit after seeing the result.

## Hypotheses and discriminating tests

Use a table instead of random rework:

| Symptom | Hypothesis A | Hypothesis B | A useful separating test |
| --- | --- | --- | --- |
| OLED absent | wrong address | no target power | measure target VCC, then scan/capture address |
| resets on tone | rail dip | software crash | scope 3V3 while saving reset reason/log |
| I2C intermittent | weak pull-up | loose connection | measure rise time, then continuity while unpowered |
| quiet/distorted audio | wrong slot/format | bad enclosure/load | inspect I2S frame into a known load before enclosure A/B |
| weak Wi-Fi in frame | metal detuning/coupling | power instability | repeat RF A/B while separately recording rail/reset behavior |
| power path hot | excess current | high path resistance | measure branch current and loaded drop across segments |

The best test often eliminates several causes without changing the device.

## Root cause versus workaround

If touching a wire makes I2C work, the root cause is not “needs a finger.” The
touch may add capacitance, coupling, pressure, or a return path. Measure which
parameter changed.

Similarly:

- reducing speaker level may mask power-path weakness;
- adding arbitrary capacitance may mask layout or pull-up errors;
- retrying startup may hide inadequate startup margin;
- moving a cable may hide a broken conductor;
- resetting after failure may erase the useful log.

A workaround can be valuable, but label it and continue until the causal model
predicts the evidence.

## Fault containment without unsafe fault injection

Begin with analysis and current-limited substitutes. Do not deliberately short,
overcharge, heat, puncture, or reverse a lithium cell. Safe exercises include:

- omit an I2C target or replace the pull-up with a deliberately weak value;
- lower the bench-supply current limit and predict CC behavior;
- insert a known resistor in a simulated source path to study sag;
- disconnect an I2S signal with power off;
- place a nonconductive dummy in the enclosure for fit tests; and
- use metal coupons near a USB-powered radio for RF A/B tests.

High-energy, compliance, abuse, and battery-fault testing require appropriate
facilities and expertise beyond this course.

## Capstone: explain, wire, observe, diagnose

Build a battery-free bench article with:

- a current-limited supply or the controller's documented USB-only setup;
- ESP32-C3 development board;
- one or two qualified 3.3 V-compatible I2C OLED modules;
- optional I2S microphone and amplifier, with speaker initially disconnected;
- DMM and, ideally, a logic analyzer; and
- exact firmware built from the corrected source path.

### Deliverable A — one-page system drawing

Draw:

- every source and return-current path;
- all rail names and nominal voltages;
- each connector pin in physical order;
- I2C SDA/SCL and pull-ups;
- I2S BCLK/WS/data directions;
- enable, reset, and boot-strap pins; and
- frame isolation and the floating speaker connection.

### Deliverable B — calculations

Show with labels and units:

1. current and power for one resistor load;
2. loaded source drop from a known series resistance;
3. approximate I2C pull-up low current and rise time;
4. I2S bit clock from sample rate, slots, and bits per slot;
5. ideal BTL sine power into an 8-ohm nominal load, clearly labeled as an
   idealized calculation; and
6. nominal battery energy from rated voltage and amp-hours, without treating
   it as guaranteed runtime.

### Deliverable C — measurements

Record:

- unpowered rail isolation;
- controller rail and idle current;
- I2C addresses and a decoded transaction;
- I2C rise time or a reason your tool cannot measure it;
- I2S `WS` and `BCLK` frequencies;
- low-level audio test current and rail behavior, if audio is installed; and
- exact test conditions and evidence labels.

### Deliverable D — diagnose three planted faults

With power off between wiring changes, have a partner choose three safe faults:

- swap one OLED's SDA and SCL;
- remove one common ground;
- select the wrong I2C address in firmware;
- make pull-up resistance too weak or too strong within safe current limits;
- disconnect one I2S clock;
- impose a low supply current limit; or
- choose the wrong logic-analyzer decoder setting.

For each, write symptom → hypotheses → discriminating test → evidence → root
cause → verified correction. Do not use the lithium cell.

## Final cell-integration gate

Completing this course is not itself permission to install the cell. The exact
Pocket Assistant must also have:

- one reconciled schematic, BOM, and assembly wiring map;
- qualified exact modules and connector pinouts;
- adequate cold-start and transient margin at intended input conditions;
- normal low-voltage shutdown rather than reliance on protection cutoff;
- reviewed USB/service-power isolation with no backfeed;
- measured thermal and audio behavior;
- exact-part mechanical fit including wires, insulation, controls, and removal;
- RF comparison in the final arrangement; and
- a dated, signed acceptance record with every failure resolved.

Until then, it is a qualification prototype—not a frozen production design.

## Common debugging mistakes

- Replacing parts before recording the failing state.
- Changing wiring, firmware, and power simultaneously.
- Debugging protocol before verifying power, return, and pin order.
- Treating a static tool, simulator, or CAD pass as physical test evidence.
- Confusing peak, average, and RMS conditions.
- Repeating a flaky test until it passes and discarding failures.
- Testing only one marketplace sample or one room temperature.
- Installing in the enclosure before the open-bench reference works.

## Check yourself

1. An OLED scan fails. Name the first three physical checks before editing the
   display library.
2. The device works open-air but resets only at loud volume in the case. What
   two domains should be measured together?
3. Does passing one cold start prove adequate minimum-input startup margin?
4. What is the difference between a diagnosis and an acceptance test?

<details>
<summary>Answers</summary>

1. Correct target supply/ground, physical connector pin order and continuity,
   then SDA/SCL levels/pull-ups. Exact order can vary, but power comes first.
2. Electrical power integrity/current/temperature and the audio/mechanical load
   or enclosure condition. Correlated rail and reset evidence is especially useful.
3. No. Define the input ramp, load, temperature, samples, repetition, and
   datasheet margin; then test the intended range.
4. Diagnosis identifies the cause of a symptom. Acceptance applies a pre-set
   pass/fail rule under defined conditions to decide whether an article meets a
   requirement.

</details>

## Authoritative further reading

- [NASA systems engineering handbook](https://www.nasa.gov/reference/systems-engineering-handbook/)
- [KiCad schematic editor and ERC documentation](https://docs.kicad.org/9.0/en/eeschema/eeschema.html)
- [KiCad PCB editor and DRC documentation](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html)
- [Espressif ESP32-C3 hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/index.html)
