# Three-week study plan — 2 hours a day, hands on hardware from day one

> For a software engineer who did this five years ago and wants speed without
> skipping the parts that bite. Fifteen sessions, roughly 50 minutes reading and
> 60 minutes at the bench each, ending with a device that talks.

## Is the existing course good enough?

**The content: yes, genuinely.** The 14 lessons in
[fundamentals/](fundamentals/README.md) are accurate, cite primary sources,
and already include worked examples, battery-free labs, "common mistakes," and
self-checks. That is better than most hobby electronics material, which tends
to be either hand-wavy or a parts list pretending to be a tutorial.

**Three gaps, and this plan fixes all three:**

| Gap | Why it matters for you | Fix |
| --- | --- | --- |
| **No pacing.** 5,200 lines with no reading order or schedule | Reading it front-to-back at 2 h/day is ~2 weeks of pure theory before touching hardware — exactly backwards from how you said you learn | The 15 sessions below, ordered by what unblocks the next hands-on step |
| **No soldering practice curriculum.** Lesson 12 explains the metallurgy of a joint well, but never says "do 30 of these, here is what good looks like, here is when you are ready" | You will solder ~40 joints into a device with no undo. Practicing on the device is how people ruin an OLED | The four practice blocks below, with rep counts and pass criteria |
| **Written in an audit register.** Phrases like "MEASURED process-qualification question," evidence labels, release gates | Correct for a build that could involve a lithium fire, but slow reading when you are relearning | Skim the gating language on first pass; it becomes useful later, when you are actually standing at that gate |

**One thing nobody wrote down: what transfers from software.**

- **Transfers well.** Layered abstractions (I²S is a protocol over a physical
  layer, same mental model as TCP over Ethernet). State machines. Reading
  specs — a datasheet is an API doc with worse search. Debugging by bisection.
- **Does not transfer, and this is where people get hurt.** In software, the
  abstraction holds; in hardware, it leaks constantly — a wire has resistance,
  a capacitor has inductance, a "3.3 V rail" is 3.1 V under load. There is no
  undo, no `git revert` on a lifted pad. And failure is not an exception you
  catch; it is heat, smoke, or a component that works for a week and then
  doesn't. **Measure, don't assume** is the whole discipline.

---

## Practice materials you still need

Everything for the *device* is bought. Practice is what you cannot do yet,
because you have no sacrificial boards to solder to.

**These three are commodity items — any equivalent works.** Unlike the speaker
or the connectors, no specific part number matters here. Search terms and the
specs that actually matter are given with each; treat the links as examples,
not requirements.

| Item | Search / examples | What actually matters | Approx. |
| --- | --- | --- | ---: |
| **Perfboard** | `double sided perfboard 2.54mm` — [20 pcs 4 sizes](https://www.amazon.com/Prototype-Printed-Universal-Perfboard-Soldering/dp/B096YJXX62) · [10 pcs 9×15 cm](https://www.amazon.com/Culnflun-Perfboard-Prototype-Soldering-Practice/dp/B0GXC1TFHD) · [74 pcs with headers](https://www.amazon.com/PCB-Prototype-Electronic-Double-Sided-Compatible/dp/B0G6RVM23J) | **2.54 mm pitch**, **FR4** (not phenolic/paper — it scorches and delaminates), double-sided, tinned holes preferred. Tinned holes wet cleanly, so you learn what a *good* joint feels like instead of fighting bare copper | ~$13 |
| **Magnification** | `headband magnifier LED` — [YOCTOSUN 5-lens](https://www.amazon.com/YOCTOSUN-Rechargeable-Magnifying-Professional-Interchangeable/dp/B07T4KPYN2) · [TMANGO visor](https://www.amazon.com/TMANGO-Magnifier-Headband-Magnifying-Brightness/dp/B07XJMZGHS). Or `USB microscope soldering` — [1000× with stand](https://www.amazon.com/Digital-Microscope-Lights-Multifunction-Studying/dp/B0DFLJ8N1S) | Hands-free, with a light. **3.5× is the lens you will live on**; the rest are filler. The purchase that most accelerates the skill — wetting, cold joints, and hairline bridges are invisible at arm's length | $13–28 |
| **Assorted LEDs** | `5mm diffused LED assortment` — [DSSRQI 100 pcs](https://www.amazon.com/DSSRQI-Diffused-Assortment-Emitting-Lighting/dp/B0DGTR8GP3) · [500 pcs, 5 colors](https://www.amazon.com/Assorted-Arduino-Projects-Indicator-Consumption/dp/B07DQQCXV9) | 5 mm, **diffused** rather than clear so they read from any angle. Skip kits that bundle resistors; you own a thousand | ~$7 |
| Sacrificial brass | **Free** — dedicate 1 of your 4 tubes and 1 of your 5 rods to practice. Never practice structural soldering on the piece you intend to keep | — |

Everything else you own: 1,000 resistors, 650 ceramic caps, electrolytics,
420 buttons, header pins, and 60+ feet of wire in two gauges. That is a
lifetime of practice stock.

---

## Week 1 — Fundamentals, and get a board talking

### Session 1 · Safety, evidence, and units
**Read** [00 — Safety and evidence](fundamentals/00-safety-evidence-and-course-map.md) ·
[01 — Charge, voltage, current, power, energy, heat](fundamentals/01-units-charge-voltage-current-power-energy-heat.md)

**Bench (60 min).** Set up the workspace: silicone mat, good light, ventilation.
Unbox and inventory against [INVENTORY.md](../docs/INVENTORY.md). Then learn
your multimeter properly — this is the tool every safety step depends on:
measure both battery packs' open-circuit voltage, read ten resistors and check
them against the color code, run continuity across a wire and then across air.

**Why first.** Voltage, current, and energy are the vocabulary for everything
else, and a lithium pouch holds real energy — 1200 mAh at 3.7 V is about
16 kJ, roughly a gram of TNT's worth, released slowly if you are lucky.

### Session 2 · DC circuits — the load-bearing session
**Read** [02 — Ohm, Kirchhoff, series and parallel](fundamentals/02-dc-circuits-ohm-kirchhoff-series-parallel.md)
(includes a worked example of your own GPIO10 button)

**Bench.** Build a voltage divider on the breadboard. **Predict every value
before you measure it** — this habit is the entire difference between
understanding a circuit and poking at it. Then an LED with a current-limiting
resistor: calculate the resistor, measure the actual current, explain the gap.

**Why it matters most.** Ohm's law and Kirchhoff's two laws explain roughly
80% of what your device does electrically. If only one session sticks, this one.

### Session 3 · Components
**Read** [03 — Resistors, capacitors, diodes, MOSFETs, converters](fundamentals/03-components-rc-diodes-mosfets-converters.md)

**Bench.** Charge a 220 µF capacitor through a 10 kΩ resistor and time the
curve with your meter. You have just measured an RC time constant — and you now
understand exactly why a bulk capacitor at the amplifier keeps Wi-Fi bursts
from resetting your processor.

### Session 4 · Measurement technique
**Read** [05 — DMM, supply, scope, logic analyzer](fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md)

**Bench.** Measure *current*, which means breaking the circuit and putting the
meter in series through the fused jack — and learn the rule that never moves:
**never put a meter in current mode across a voltage source.** It is a dead
short through a fuse. Then measure voltage drop along a wire under load, and
estimate a battery's internal resistance.

### Session 5 · Digital logic, GPIO, and boot straps — first light
**Read** [07 — Digital logic, GPIO, pull resistors, boot straps](fundamentals/07-digital-logic-gpio-pullups-boot-straps.md)

**Bench.** `esptool flash_id` on all ten SuperMinis — record each one, reject
anything under 4 MB. Flash one, get it booting, watch the serial log. You are
now on familiar ground: it's a computer.

**Connect it back.** You just read why GPIO2 needs a pull-up and why GPIO8 and
GPIO9 are untouchable. Those are not arbitrary rules — a strap pin held wrong
at reset means a board that will not enter download mode, which inside a
soldered brass frame is unrecoverable.

---

## Week 2 — Protocols, sound, and learning to solder

### Session 6 · I²C and the display
**Read** [08 — I²C and the OLED](fundamentals/08-i2c-and-the-oled.md)

**Bench.** Breadboard the OLED. Run an I²C scan, find it at `0x3C` or `0x3D`,
get pixels on screen. Read the silkscreen pin order first — vendors swap
VCC/GND between identical-looking boards.

### Session 7 · I²S and digital audio
**Read** [09 — I²S, sampling, and digital audio](fundamentals/09-i2s-sampling-and-digital-audio.md)

**Bench.** Add the INMP441. Tie `L/R` low, data to GPIO4, verify it captures
intelligible audio.

**The satisfying part.** You will finally see why the whole build is pinned to
16 kHz: the amplifier's datasheet excludes 24 kHz, the microphone needs exactly
64 clocks per frame, and the codec is hard-wired to 16 kHz. Three independent
constraints, one number that satisfies all of them.

### Session 8 · Class-D, bridge outputs, speakers — first sound
**Read** [10 — Class-D, BTL, speakers, acoustics](fundamentals/10-class-d-btl-speakers-and-acoustics.md)

**Bench.** Add the amplifier and speaker. Meter the `SD` pin first (~0.30 V is
correct). Keep the volume low. Then run a full voice round trip — wake word,
question, spoken answer. **This is the milestone: the device works.** Everything
after this is making it small, safe, and permanent.

### Session 9 · Soldering theory + practice block 1
**Read** [12 — Soldering, mechanics, insulation, tolerances](fundamentals/12-soldering-mechanics-insulation-tolerance.md),
sections through "What inspection can and cannot prove"

**Practice block 1 — through-hole, ~30 joints (60 min).**
Resistor leads into perfboard. The motion that matters: tin the tip lightly,
touch the tip to *both* pad and lead, feed solder **into the joint** rather than
onto the tip, count two or three seconds, remove solder then iron, hold still
while it freezes.

- **Good** — smooth concave fillet, shiny, solder visibly pulled *onto* the pad
- **Cold** — dull, lumpy, ball-shaped, sitting *on* the pad rather than wetting it
- **Pass criteria: 10 consecutive good joints.** Count honestly; restart the count on a bad one.

### Session 10 · Practice block 2 — wire work
**Read** the rest of [Lesson 12](fundamentals/12-soldering-mechanics-insulation-tolerance.md):
strain relief and insulation as a system

**Practice block 2 (75 min).** This is what your build actually consists of —
almost every project joint is wire-to-pad, not component-to-board.

- 20 wire-to-pad joints, both gauges. Pre-tin the wire, pre-tin the pad, then join
- 10 wire-to-wire splices, each sleeved in heat-shrink — slide the shrink on *before* you solder, a mistake everyone makes once
- One 6-pin header soldered into perfboard
- **Destructive test:** pull five joints apart and look at the break. Solder pulled off cleanly with no copper showing means it never wetted — that joint was always going to fail, and now you know what that failure looks like *before* it happens inside the frame

**Pass criteria: five wire-to-pad joints that survive a firm tug on the wire.**

---

## Week 3 — Power, rework, and the build

### Session 11 · Lithium, power integrity, and heat
**Read** [06 — Li-ion, power integrity, decoupling, UVLO, thermal](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md)
— the longest lesson, and the one where mistakes are permanent

**Bench.** No cell. Re-read your own [power chain worksheet](07-the-power-chain.md)
and predict, in writing, what the rail will do at 4.2 V and at 3.3 V under load.
You will check those predictions next session.

### Session 12 · The power chain, from the bench supply
*(Needs the supply — arriving ~Sep 21–23. If it slips, swap with Session 13.)*

**Bench (the full 2 hours).** Supply standing in for the battery at the JST
position, current limit set low. Sweep 4.2 V down to 3.3 V under Wi-Fi and loud
audio and watch for a reset. Measure the switch's contact drop. Twenty switch
cycles, twenty clean boots. Record everything in a
[lab record](fundamentals/reference/lab-record-template.md).

**This session decides your battery.** The measured current draw is what picks
the 500 mAh pack or the 1200 mAh one — not the argument in the docs.

### Session 13 · Datasheets + practice block 3 (rework)
**Read** [04 — Boards, schematics, datasheets, connectors](fundamentals/04-boards-schematics-datasheets-and-connectors.md)

**Practice block 3 (60 min).** Desolder twenty of your practice joints with
wick, then re-solder them. Rework is the skill that turns a ruined build into a
delayed one — and you *will* wire something backwards.

**Pass criteria: remove and correctly replace a component without lifting a pad.**

### Session 14 · Radio, the metal frame, and fit
**Read** [11 — RF, EMC, antennas, and the metal frame](fundamentals/11-rf-emc-antennas-and-metal-frame.md)

**Bench.** The 1:1 cardstock dry-fit with real measured parts. Every port,
control, and the pack's removal path reachable. **Nothing gets cut until this
closes.**

### Session 15 · Debugging method + practice block 4 (brass)
**Read** [13 — Systematic debugging and the capstone](fundamentals/13-debugging-integration-and-capstone.md)

**Practice block 4 (75 min) — structural brass, a different discipline.**
Sacrifice one tube and one rod. Acid flux, chisel tip, much higher thermal
mass, and **no electronics anywhere in the room**. Cut with the jeweler's saw,
deburr, bend around a form, flux, join six practice joints, then wash and
neutralize with baking soda.

**Pass criteria: a square, clean-jointed practice rectangle you would be
willing to keep.** Then build the real one.

---

## After the fifteen sessions

Follow [the assembly sequence](04_ASSEMBLY_STEP_BY_STEP.md) and record each
gate. Expect the build itself to take another week of evenings — mounting,
wiring, and the unpowered checks are slow, and rushing them is the one way to
turn a working breadboard into a dead sculpture.

## How to actually keep the 2 hours

- **Read with the hardware in front of you.** Every lesson references parts you
  own; hold the part while you read about it.
- **Predict before measuring, every time.** Write the number down first. Being
  wrong on paper is how the intuition gets built — and it is free.
- **Keep a lab log.** Copy the [template](fundamentals/reference/lab-record-template.md).
  In three weeks you will not remember which of ten SuperMinis had the flash-ID
  problem.
- **Skip the gate language on first read.** The release-gate and evidence-label
  paragraphs are for when you are standing at that gate. They are not what you
  are learning today.
- **When a session's bench work fails, that is the session.** Debugging a real
  failure teaches more than the next lesson would. Slide the schedule.

## The two rules that never bend

1. **Never solder to, puncture, or heat a lithium cell**, and keep both packs
   sealed and terminal-protected until Session 12 says otherwise.
2. **Never put a meter in current mode across a source.** It is a short circuit
   with a fuse in it, and it is the most common way beginners destroy a meter.
