# Radio and frame — applying the RF/EMC lesson

> **Status: lesson only; brass fabrication is held.** The current
> [decision record](../docs/FINAL_MATERIALS_FOR_REVIEW.md) requires measured
> parts, updated CAD, a cardstock fit model, antenna checks, and coating
> coupons before any final brass cut. The exact
> antenna position, brass geometry, and routing on **your** build still earn
> acceptance through this note's battery-free RF tests.

Read [11 — RF, EMC, antennas, and the metal frame](fundamentals/11-rf-emc-antennas-and-metal-frame.md)
and [12 — Soldering, mechanics, insulation, and tolerances](fundamentals/12-soldering-mechanics-insulation-tolerance.md)
before laying out the structure.

## Wavelength gives scale, not forbidden lengths

At `2.45 GHz`, free-space wavelength is approximately:

```text
λ = c/f ≈ 122 mm
λ/4 ≈ 30.6 mm
λ/2 ≈ 61.2 mm
```

Those numbers help explain why a handheld frame can interact strongly with a
2.4 GHz antenna. They do **not** make `28–34 mm` or `58–64 mm` brass runs
automatically resonant or forbidden. Shape, width, bends, joints, dielectric,
end effects, feed/coupling, losses, board ground, wiring, and nearby objects all
change the result.

Replace “break resonant lengths” with a testable hypothesis such as:

> Moving the identified antenna region from 5 mm to 15 mm away from the nearest
> brass member will improve the defined link metrics in the defined setup.

The test may support or reject that hypothesis.

## Identify the exact antenna first

An ESP32-C3 IC datasheet does not describe a SuperMini clone's antenna or
ground layout. Photograph both faces of the received board and identify its
antenna region, feed, ground-plane edge, USB cable route, and any layout
revision. Do not assume the antenna is always the end opposite USB.

Espressif recommends placing an onboard PCB antenna outside the base board
when possible and, for its documented layout context, at least `15 mm`
clearance in all directions inside the housing. It also requires final-product
throughput and range testing. Treat `15 mm` as a starting geometry, not a
guarantee for an unknown clone beside brass.

Primary source: [Espressif ESP32-C3 PCB layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html).

## What nearby metal can do

Metal near the antenna can:

- change antenna impedance and resonance;
- carry induced current even while electrically floating;
- reflect, shadow, or reshape the radiation pattern;
- couple as a parasitic element; and
- change common-mode return paths if bonded.

The effect may improve one direction while worsening another. “Metal always
blocks,” “floating metal is invisible,” and “grounding the frame always helps”
are all unreliable rules.

Candidate placement should leave adjustment space and initially keep the
identified antenna region away from frame members, the cell-sized conductor,
display flex, converter switching region, speaker pair, and dense wire bundles.
Which separation is adequate is a **MEASURED** result.

## RF performance needs repeated measurements

RSSI changes with multipath, channel traffic, access point, orientation,
people, cable position, and receiver estimation. One favorable number is not a
release test.

Record at least:

- median and spread of RSSI;
- packet attempts, loss, or retries;
- transaction latency or throughput;
- disconnect/reconnect count and recovery time; and
- several intended product orientations.

Fix access point, channel, distance, board position, firmware, sample duration,
USB cable, and room activity. Repeat the baseline after each candidate; if the
baseline moved, collect more trials.

## The frame is structure during qualification

Do not use brass as power, ground, signal, or a BTL speaker conductor. With all
sources absent, require high resistance/open circuit between the frame and:

- source positive and return;
- `3V3`, USB power, and circuit ground;
- every signal; and
- both speaker outputs.

Keeping the candidate frame floating avoids deliberately making exposed metal
the current return, but does not make it electromagnetically harmless. A future
ground bond would be a new RF, ESD, and fault architecture requiring a reviewed
schematic, defined connection point, fault analysis, and new testing.

Paint is decoration, not primary insulation. It can thin at edges and scratch
in use. Provide retained insulating barriers, abrasion protection, guarded
contacts, deburred/capped ends, and strain relief. Do not attach a universal
dielectric-strength claim to generic tape; qualify the exact material and
thickness.

## EMC includes the converter and speaker wiring

Wi-Fi connection alone does not prove electromagnetic compatibility. The
buck-boost converter and class-D amplifier intentionally switch fast current.
Reduce coupling before adding suppression parts:

- keep outgoing high-current conductors beside their returns;
- twist the two floating BTL speaker wires together and keep them short;
- place required decoupling at device pins with short return loops;
- keep switching nodes and clock/speaker wiring away from the antenna and mic;
  and
- do not add an unidentified ferrite bead, shield, capacitor, or frame bond
  without a schematic, applicable data, and before/after measurement.

A DMM reads ferrite DC resistance, not its RF impedance.

## Battery-free frame A/B test

Use one identified bare ESP32-C3 board on USB, a nonconductive fixture, fixed
firmware, a fixed access point, and removable brass coupons or the electrically
isolated frame. The bare board avoids the unresolved peripheral backfeed path.
No lithium cell is needed.

1. Mark antenna region, board pose, USB route, access-point location/channel,
   distance, firmware build, and test duration.
2. Run at least five equal baseline captures of RSSI, packet success/loss,
   latency or throughput, and reconnect events.
3. Introduce one brass coupon at a documented distance and orientation without
   touching any powered node. Repeat the same captures.
4. Test several distances and orientations one variable at a time. Use an inert
   metal cylinder—not a cell—if a cell-sized conductor is part of the question.
5. Remove the metal and repeat baseline to reveal environmental drift.
6. Temporarily support the board in the actual electrically isolated frame and
   repeat with the same cable route. Test more than one adjustable board pose.
7. Compare median and range plus packet/reconnect behavior. Decide the pass/fail
   threshold before examining the candidate result.
8. Stop for possible metal-to-pad contact, cable strain, resets, unexpected
   heat, odor, or current behavior.

This ranks candidate geometries in the stated environment. It does not measure
antenna impedance, radiated power, regulatory emissions, immunity, or every
real pocket/room configuration.

## Mechanical and pocket-use gate

Before a frame can be released, the exact received assembly must demonstrate:

- no reachable energized conductor with keys/coins represented by controlled
  probes or fixtures;
- no sharp edge, solder spike, or abrasion path into wiring or a future cell;
- guarded holder contacts and a cell removal path that does not flex boards;
- retained insulation that survives assembly and repeated service;
- speaker opening, rear enclosure, microphone port, button, USB, and antenna
  keepouts that remain functional after tolerance stacking; and
- acceptable RF metrics in the representative held and pocket-adjacent poses.

Do these checks with a bench supply or inert cell dummy. The pack enters only
at the final acceptance gate.

Your particular frame is accepted only when its safety, RF, EMC, acoustics,
tolerance, and service evidence are complete and recorded.
