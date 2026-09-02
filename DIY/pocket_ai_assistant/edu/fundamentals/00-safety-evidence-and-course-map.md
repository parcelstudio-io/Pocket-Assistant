# 00 — Safety, evidence, and the course map

## Learning objectives

After this lesson, you should be able to:

- distinguish voltage, current, power, and energy as different quantities;
- choose the safe first instrument for an unknown circuit state;
- distinguish a datasheet limit from a typical value or estimate;
- explain why simulation and static checks do not certify hardware;
- state the conditions that keep the early labs low risk.

## The safe order of evidence

Engineers reduce uncertainty in layers:

```text
read specifications
        ↓
draw and review a schematic
        ↓
calculate limits and margins
        ↓
simulate or run static checks
        ↓
inspect the unpowered assembly
        ↓
power it from a current-limited supply
        ↓
measure function, faults, heat, and timing
        ↓
only then introduce the battery and enclosure
```

Each layer catches a different class of mistake. A simulator cannot discover
that a marketplace module arrived with reversed power pins. A continuity test
cannot prove that an I2C edge rises fast enough. A successful boot cannot prove
safe thermal behavior after an hour.

## The five evidence labels

Suppose a regulator page says “1.5 A typical,” a design spreadsheet assumes
85% efficiency, and a meter later reads 3.28 V at 800 mA:

| Statement | Correct label |
| --- | --- |
| Manufacturer guarantees a 3.0 V minimum rail | **DATASHEET-MIN** |
| Curve shows about 90% at one test point | **TYPICAL** |
| We use 85% before hardware arrives | **ASSUMED** |
| Input current is 1.04 A from the assumed efficiency | **CALCULATED** |
| This serial-numbered board produced 3.28 V at 800 mA | **MEASURED** |

A calculation is only as reliable as its inputs. Write the labels beside the
numbers in your notebook.

## Non-negotiable lab rules

1. Keep lithium cells out of lessons 01–05 and all first-power attempts.
2. De-energize a circuit before continuity or resistance measurement.
3. A voltmeter goes **across** two points. An ammeter goes **in series** with a
   branch. Never place a current-mode meter directly across a source.
4. Start new circuits on a bench supply with a deliberate current limit.
5. Confirm instrument ground references before attaching a scope or logic
   analyzer. A grounded scope clip can create a short.
6. Never connect either BTL speaker output to ground.
7. Wear eye protection for cutting, soldering, and powered fault finding.
8. Stop immediately for unexpected heat, smell, smoke, swelling, noise, or a
   current limit that activates unexpectedly.

## What software can and cannot prove

| Tool | Useful evidence | Important blind spot |
| --- | --- | --- |
| Firmware compiler/tests | Source consistency and host-tool behavior | The actual board, wiring, RF, audio, and power path |
| Wokwi | Digital GPIO/I2C behavior for modeled parts | Analog power, exact clone boards, acoustics, batteries, mechanics |
| KiCad ERC | Schematic pin-type and connection errors | Incorrect symbols, wrong assumptions, physical construction |
| KiCad DRC | PCB connectivity, width, clearance, and layout rules | Enclosure access, cable flex, unmodeled parts, real manufacturing variation |
| FreeCAD | Geometry that was actually modeled | Anything omitted or represented by an estimated envelope |
| DMM | A particular electrical observation | Fast transients outside the meter bandwidth |

## Course exit gate

Before powering the pager from a cell, you should be able to:

- draw every supply and return-current path;
- configure a current-limited supply and use a DMM safely;
- explain pull-ups, open-drain signaling, and boot straps;
- scan an I2C bus and interpret an absent ACK;
- calculate the project's I2S bit clock;
- distinguish startup voltage from operating voltage;
- explain why the speaker is floating between two amplifier outputs; and
- diagnose several injected faults using a repeatable sequence.

## Check yourself

1. A vendor graph shows 1.2 A at 25 °C on one sample. Is 1.2 A a guaranteed
   design limit?
2. A CAD check passes, but the connector and cable are absent from the model.
   Has connector access been verified?
3. What is the first power source for a newly wired circuit?

<details>
<summary>Answers</summary>

1. No. Treat it as **TYPICAL** unless the electrical-characteristics table
   gives an applicable minimum or maximum.
2. No. The result covers only modeled geometry.
3. A correctly configured current-limited bench supply, after unpowered
   inspection and continuity checks—not the lithium cell.

</details>
