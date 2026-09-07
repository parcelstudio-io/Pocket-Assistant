# Illustrated concepts — the “why” behind each lab

[Back to the daily plan](../DAILY_STUDY_AND_LAB_PLAN.md) · [USB prototype quickstart](../../docs/PROTOTYPE_QUICKSTART.md)

Yes: start with the basic physics of **charge, energy, voltage, and current**,
then learn how complete circuits behave. You do not need to master all of
physics or finish every electronics lesson before booting a bare USB board.
Understand the circuit you are about to change, one small step at a time.

These are optional **5–10 minute illustrated explanations**, not extra lab
requirements. Each connects a physical idea to a calculation and a prototype
decision, then asks you to predict something. Expand the answer after trying.
Use these pages within the daily plan's existing study time, not on top of it.

## A small starting point

Read **01 → 02 → 03** first for the circuit foundation. Add **04 → 05** when
you reach capacitors and measurements. After that, open just the page for
the component you are testing. “I can explain why” is more useful than
memorizing every equation.

| Day | Illustrated explanation | The question it answers |
| ---: | --- | --- |
| 1 | [Charge, energy, and circuits](01-charge-energy-and-circuits.md) | What flows, what transfers energy, and why is a return needed? |
| 2 | [Voltage, current, resistance, power](02-voltage-current-resistance-and-power.md) | What do the units mean, and where does `P = VI` come from? |
| 3 | [Series, parallel, rails, loading](03-series-parallel-and-loading.md) | Why do resistor formulas work, and why does a divider sag? |
| 4 | [Capacitors and time](04-capacitors-and-time.md) | What is stored, and why does voltage change gradually? |
| 5 | [Measurement and uncertainty](05-measurement-and-uncertainty.md) | How does a meter affect the circuit, and what can it miss? |
| 6 | [From code to boot](06-from-code-to-boot.md) | How do files become electrical activity on a board? |
| 7 | [GPIO and buttons](07-gpio-and-buttons.md) | How do voltages become bits, and why do inputs need a defined state? |
| 8 | [I2C and the OLED](08-i2c-and-the-oled.md) | How can devices share a wire without fighting each other? |
| 9 | [Sampling and I2S](09-sampling-and-i2s.md) | How does sound become numbers and timed bits? |
| 10 | [Speakers and amplifiers](10-speakers-and-amplifiers.md) | How does electrical power move a cone, and why is neither output ground? |
| 11 | [Soldering and heat](11-soldering-and-heat.md) | Why must the joint get hot, not just the solder? |
| 12 | [Joints and strain relief](12-joints-and-strain-relief.md) | Where does a tug go, and why do wires break at rigid joints? |
| 13 | [Power integrity](13-power-integrity.md) | Why can a rail dip when current suddenly increases? |
| 14 | [Fit and radio](14-fit-and-radio.md) | Why do clearances, tolerances, and nearby metal matter? |
| 15 | [Debugging as experiments](15-debugging-as-experiments.md) | Which measurement best separates two possible causes? |

## How to read the drawings

A line on a **schematic** represents an electrical connection, not a physical
wire position. A filled dot marks a joined node. A resistor is drawn as a
rectangle; `GND` labels a voltage reference/return, not Earth or the brass frame.
Current arrows use the conventional direction. Block diagrams and mechanical
sketches are labeled and are not wiring layouts.

The SVG figures are original, editable diagrams. Labels and captions carry
the meaning; you do not have to distinguish the colors. Open a figure on its
own to enlarge it. Numeric examples are idealized predictions unless explicitly
identified otherwise, not measured limits of your parts.

These pages introduce **no new purchases or powered experiments**. Keep using
the daily plan's wiring checks, power limits, and stop conditions. Amplifier,
battery, and final enclosure work remain separate from the first USB prototype.
For a longer explanation, follow the existing `edu/` lesson linked at the end
of each page.
