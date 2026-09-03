# Pocket Assistant electronics course

This is a beginner-first path into the physics and electrical engineering used
by the pocket assistant. It assumes comfortable arithmetic and simple algebra,
but no electronics background and no calculus.

**If you are starting from scratch, read [the three-week study
plan](STUDY_PLAN.md) first.** It sequences everything below into fifteen
2-hour sessions, pairs each reading block with bench work on parts you own,
and adds the soldering practice curriculum (rep counts, pass criteria, and the
materials needed) that the lessons alone do not provide.

The [foundations course](fundamentals/README.md) teaches the ideas
independently of whichever exact marketplace parts eventually pass
qualification:

1. [Safety, evidence, and the learning path](fundamentals/00-safety-evidence-and-course-map.md)
2. [Charge, voltage, current, resistance, power, energy, and heat](fundamentals/01-units-charge-voltage-current-power-energy-heat.md)
3. [DC circuits: nodes, loops, Ohm's law, and Kirchhoff's laws](fundamentals/02-dc-circuits-ohm-kirchhoff-series-parallel.md)
4. [Components: resistors, capacitors, inductors, diodes, MOSFETs, and converters](fundamentals/03-components-rc-diodes-mosfets-converters.md)
5. [Boards, schematics, datasheets, footprints, and connectors](fundamentals/04-boards-schematics-datasheets-and-connectors.md)
6. [Measurement and debugging tools](fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md)
7. [Li-ion power, voltage sag, decoupling, UVLO, and heat](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md)
8. [Digital logic, GPIO, pull resistors, and boot straps](fundamentals/07-digital-logic-gpio-pullups-boot-straps.md)
9. [I2C and the OLED](fundamentals/08-i2c-and-the-oled.md)
10. [I2S, sampling, and digital audio](fundamentals/09-i2s-sampling-and-digital-audio.md)
11. [Class-D amplifiers, BTL outputs, speakers, and acoustics](fundamentals/10-class-d-btl-speakers-and-acoustics.md)
12. [RF, EMC, antennas, and the metal frame](fundamentals/11-rf-emc-antennas-and-metal-frame.md)
13. [Soldering, mechanics, insulation, and tolerances](fundamentals/12-soldering-mechanics-insulation-tolerance.md)
14. [Systematic debugging and the capstone](fundamentals/13-debugging-integration-and-capstone.md)

Keep the [glossary](fundamentals/reference/glossary.md),
[equation sheet](fundamentals/reference/equations.md), and
[project map](fundamentals/reference/project-map.md) open as references. Copy
the [lab record template](fundamentals/reference/lab-record-template.md) for
each physical experiment.

## Applied project notes

The remaining files in this directory apply those concepts to the current
prototype. They are engineering notes, not a second fundamentals course:

- [System overview](01-how-it-fits-together.md)
- [Software and evidence tools](01_SOFTWARE_AND_VERIFICATION.md)
- [Component rationale](02-components.md)
- [White/silver/black candidate-selection criteria](02_COMPONENTS_WHITE_SILVER_BLACK.md)
- [Power and battery notes](03-power-and-battery.md)
- [Current signal contract](03_HOW_IT_WORKS.md)
- [I2S and audio](04-audio.md)
- [Assembly sequence](04_ASSEMBLY_STEP_BY_STEP.md)
- [I2C display and ESP32-C3 pins](05-display-and-pins.md)
- [Color and finish](05_COLOR_AND_FINISH.md)
- [Radio and frame](06-radio-and-frame.md)
- [Acceptance-test worksheet](06_ACCEPTANCE_TESTS.md)
- [Power-chain worksheet](07-the-power-chain.md)

Shopping tables and assembly release status belong in `docs/`. A marketplace
listing, a passing static script, or a CAD cuboid is not proof that a physical
device is safe or functional. The present design remains a qualification
prototype until the exact hardware passes its recorded release gates.

## Evidence boundary

The source has compiled reproducibly and host-side tests exist, but the build
manifest records `hardware_tested: false`. No statement in this course means
that the complete battery, power, audio, radio, or mechanical assembly has
been physically accepted.

Do not reproduce the video's exposed-cell construction. Keep lithium cells
out of the early labs. Never strip, solder, heat, puncture, or deliberately
short a cell. The metal frame is not a circuit conductor or current return,
but must always be treated as electrically conductive and isolated from every
net. Neither bridge-amplifier speaker lead is ground.
