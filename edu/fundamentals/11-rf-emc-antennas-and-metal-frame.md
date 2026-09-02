# 11 — RF, EMC, antennas, and the metal frame

## Learning objectives

After this lesson, you should be able to:

- relate frequency and wavelength without turning wavelength into a mechanical
  superstition;
- explain why an antenna depends on its board, return path, and surroundings;
- predict several ways nearby metal can change radio behavior;
- distinguish RF communication performance from broader EMC behavior;
- plan a controlled A/B test using RSSI, packet loss, and reconnects; and
- test the frame without a lithium-ion cell.

## Durable theory and provisional geometry

The electromagnetic principles in this lesson are durable. The exact
ESP32-C3 SuperMini clone antenna, frame geometry, board orientation, wiring,
speaker leads, and cell position are **PROVISIONAL project design** until the
received unit and complete geometry are measured.

The old project rule to avoid straight metal runs of `28–34 mm` and
`58–64 mm` near the antenna is not a defensible release rule. Those numbers
resemble free-space quarter- and half-wavelengths, but an irregular floating
brass member does not become a predictable resonator from length alone.

## Frequency, wavelength, and scale

In free space:

```text
wavelength λ = speed of light c / frequency f
```

Near the middle of the `2.4 GHz` Wi-Fi/BLE band, at `2.45 GHz`:

```text
λ ≈ 3.00×10⁸ m/s / 2.45×10⁹ Hz ≈ 0.122 m = 122 mm
quarter wavelength ≈ 30.6 mm
half wavelength ≈ 61.2 mm
```

These values give useful physical scale. They do not define universal
forbidden metal lengths. Effective wavelength and resonance depend on
dielectric materials, conductor width and shape, end effects, bends, nearby
objects, feed position, losses, coupling, and the return-current structure.

## An antenna is part of a current system

An antenna converts guided current and voltage into electromagnetic fields and
back again. It does not work independently of its feed and reference. A PCB or
chip antenna is tuned with some combination of:

- antenna geometry;
- matching components;
- PCB dielectric and copper;
- ground-plane dimensions and current distribution;
- enclosure and nearby materials; and
- cable, battery, hand, and product orientation.

Changing the carrier board or moving metal nearby changes that system. The
result may be reduced efficiency, shifted resonance, a different radiation
pattern, or a changed impedance presented to the radio. “The antenna itself
was not touched” does not mean the RF design stayed the same.

Identify the antenna on the exact received board by inspection and continuity
against an authoritative schematic if one exists. Do not assume it is always
the end opposite USB; marketplace clones can change layout without changing
the listing.

## Near field, far field, and nearby metal

Close to an electrically small antenna, stored electric and magnetic fields
can dominate. An object in this near region can couple strongly even if it
does not sit directly between the antenna and access point.

Metal can affect the radio in several ways:

- induced currents can oppose or redirect the antenna's fields;
- a conductive object can detune the antenna and matching network;
- a sheet or frame member can reflect, shadow, or reshape the pattern;
- a lossy joint or material can dissipate RF energy;
- a floating conductor can act as a coupled parasitic element; and
- a bonded conductor changes the RF return geometry and common-mode currents.

The effect can improve one direction or frequency while worsening another.
That is why “metal always blocks,” “floating metal is invisible,” and “bonding
always helps” are all poor design rules.

## The manufacturer's placement rule is the starting point

Espressif recommends placing a module's onboard PCB antenna outside the base
board when possible. If that cannot be done, its ESP32-C3 hardware guide calls
for at least `15 mm` clearance around the antenna area with no copper, routing,
or components in the specified keepout arrangement.

That is guidance for a known Espressif-style antenna implementation, not proof
that every SuperMini clone is compliant or that `15 mm` from a brass cage is
automatically sufficient. Use it as the initial geometry, then test the exact
board in the exact product orientations.

For the Pocket Assistant:

- place the identified antenna region away from the cell-sized metal object,
  display flex, speaker wiring, converter, and frame members;
- avoid routing class-D speaker current or switching-converter loops through
  the antenna keepout;
- preserve the board's intended ground-plane region rather than cutting or
  extending it casually; and
- leave enough mechanical adjustment to test more than one antenna position
  before soldering the final frame around it.

## RF performance is statistical

RSSI is a received-power estimate, not a complete link-quality score. It
varies with multipath, channel traffic, access-point behavior, orientation,
people moving, firmware timing, and receiver calibration.

In an ideal far field, field amplitude falls approximately with `1/r`, and
received power changes by about `-6 dB` when distance doubles. A room can have
deep constructive and destructive interference over movements smaller than a
wavelength, so one RSSI reading can reverse an apparent result.

A useful product test combines:

- median and spread of RSSI over time;
- packet loss or retransmissions;
- usable throughput or transaction latency;
- association and reconnect success/time; and
- behavior in several intended hand/product orientations.

Set the acceptance rule before seeing the candidate result. A finite room test
is **MEASURED** evidence for that setup, not antenna certification.

## EMC is larger than “does Wi-Fi connect?”

Electromagnetic compatibility includes both:

- **emissions:** unwanted energy the product sends into wires or space; and
- **immunity:** whether external fields, ESD, or conducted disturbances upset
  the product.

The buck-boost converter and class-D amplifier deliberately switch fast
current. The important radiating structures are often loops and common-mode
paths, not only the antenna. Reduce their opportunity to couple:

- place decoupling at device power pins with a short return path;
- keep each high-current outgoing conductor close to its return;
- twist the two BTL speaker wires together and keep them short;
- keep switching nodes physically small and away from antenna/microphone
  wiring;
- do not route current through the structural frame; and
- qualify any bead, shield, capacitor, or frame bond from a schematic and
  measurement rather than adding it decoratively.

A ferrite bead's DMM resistance says almost nothing about its RF impedance.
Impedance versus frequency, DC-current bias, saturation, loss, and placement
must match the problem being solved.

## The conductive frame has two separate design questions

### Electrical safety

The frame is not a circuit conductor in Rev A. With every source disconnected,
it should remain isolated from battery positive, circuit ground, `3V3`, USB,
signals, and both BTL speaker outputs. Paint is decorative, not primary
insulation; edges, scratches, fasteners, and soldered seams expose conductive
metal. Use a mechanically retained, specified insulating barrier and protect
wires from abrasion.

### RF/ESD behavior

Leaving the frame floating avoids deliberately making it battery return, but
does not make it electromagnetically absent. It can acquire induced RF current
or charge. Bonding it to circuit ground would create a different RF, ESD, and
fault architecture; it could help or hurt and must not be improvised at final
assembly. A future bond requires a reviewed schematic, chosen connection point,
fault analysis, ESD strategy, and new RF/EMC testing.

## Layout hypotheses must be testable

Write placement ideas in a form that an A/B test can disprove:

> **HYPOTHESIS:** Moving the identified antenna region from 5 mm to 15 mm away
> from the nearest brass member will improve median RSSI without increasing
> packet loss in the defined test setup.

This is better than “15 mm guarantees good RF.” It names the variable, outcome,
and comparison. Test one variable at a time before trying a complete frame,
cell-shaped conductor, wiring bundle, paint, and hand simultaneously.

Useful controlled variables include distance, orientation, metal area, frame
electrical state, cable route, board position, access-point channel, and
product orientation. Record everything that is held constant.

## Safe lab: metal-proximity A/B without a cell

Use one identified bare ESP32-C3 board on USB, a nonconductive fixture, one
fixed access point, test firmware that logs link metrics, and removable brass
coupons or the unpowered frame. The bare board avoids the unresolved peripheral
backfeed path. Do not attach a lithium-ion cell.

1. Photograph the board and mark the antenna region, USB cable route, test
   orientation, access-point position, distance, channel, and firmware build.
2. Fix the board to cardboard, foam, or another nonconductive jig. Keep the
   operator out of the immediate test volume during each capture.
3. Record at least five equal-duration baseline runs. Log timestamped RSSI,
   packet attempts/successes, latency or throughput, and disconnect/reconnect
   events.
4. Introduce one brass coupon at a documented distance and orientation without
   touching the board. Repeat the same number and duration of runs.
5. Repeat at several controlled distances—for example `5`, `10`, `15`, and
   `30 mm`—and at two orientations. Do not search only until a preferred answer
   appears.
6. Compare median and spread, not one best sample. Note whether packet loss or
   reconnect behavior changes even when RSSI appears similar.
7. Repeat baseline after removing the metal. If the baseline moved, the room or
   network changed and the comparison needs more trials.
8. Place the powered board in the actual but electrically isolated frame using
   temporary nonconductive supports. Repeat with the same USB cable route, then
   try the proposed final board position.
9. Use an inert metal cylinder or coupon only if a cell-shaped conductor is
   part of the experiment. Never use a lithium cell as an RF test weight.
10. Stop if metal can contact a powered pad, the USB cable is strained, the
    board resets unexpectedly, or unexpected heat/odor appears.

This experiment ranks geometries for the stated setup. It does not measure
antenna impedance, radiated power, regulatory emissions, or every real-world
environment.

## Common mistakes

- Treating quarter- and half-wavelength numbers as forbidden frame lengths.
- Assuming a floating frame cannot carry induced current.
- Assuming the antenna is at a particular board end from a product photo.
- Moving the board, access point, cable, operator, and metal at the same time.
- Choosing a geometry from one RSSI number.
- Ignoring packet loss and reconnect behavior when RSSI looks acceptable.
- Routing class-D or converter switching loops beside the antenna.
- Adding an unknown ferrite because its DMM resistance is low.
- Treating paint as insulation or grounding the frame without an ESD/fault
  design.

## Check yourself

1. Why does a `30.6 mm` quarter wavelength not make every 30 mm brass member a
   resonant antenna?
2. How can a floating frame affect RF despite having no DC connection?
3. Why is one RSSI measurement weak evidence?
4. What does Espressif's `15 mm` recommendation establish, and what does it not
   establish?
5. Name two metrics to record in addition to RSSI.

<details>
<summary>Answers</summary>

1. Resonance also depends on shape, width, bends, material, end effects,
   dielectric, feed/coupling, losses, and its electromagnetic environment.
2. Nearby fields induce charge and current; the frame can detune, reflect,
   shadow, dissipate, or re-radiate energy without a DC bond.
3. Multipath, interference, channel traffic, orientation, and receiver
   estimation make it variable; repeated controlled trials are needed.
4. It is the manufacturer's starting layout guidance for its antenna context.
   It does not certify a clone or guarantee performance beside a metal frame.
5. Packet loss/retries, throughput or latency, and disconnect/reconnect success
   or time are suitable examples.

</details>

## Primary sources for the project-specific statements

- [Espressif ESP32-C3 PCB layout design guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html)
- [Espressif ESP32-C3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf)

