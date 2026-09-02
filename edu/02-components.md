# Components — turning candidates into evidence

> **DESIGN-FREEZE STATUS: NO-GO.** This is a qualification note, not a BOM or
> purchasing list. Every exact board, module, speaker, holder, protection part,
> connector, and frame dimension remains **PROVISIONAL** until the interfaces
> agree and exact received samples pass the required tests.

Read the applicable foundations first:

- [04 — Boards, schematics, datasheets, and connectors](fundamentals/04-boards-schematics-datasheets-and-connectors.md)
- [06 — Li-ion power integrity, decoupling, UVLO, and heat](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md)
- [10 — Class-D, BTL speakers, and acoustics](fundamentals/10-class-d-btl-speakers-and-acoustics.md)
- [11 — RF, EMC, antennas, and the metal frame](fundamentals/11-rf-emc-antennas-and-metal-frame.md)

## Start with interfaces, not product names

An IC datasheet describes the IC under its stated conditions. It does not
identify a marketplace module, prove the module schematic, or guarantee its
inductor, passives, thermal layout, connectors, pin order, antenna, or size.
Record those separately.

The Pocket Assistant currently needs these interface contracts:

| Subsystem | Durable requirement | Evidence still needed |
| --- | --- | --- |
| Controller | ESP32-C3 firmware target, correct GPIO contract, adequate flash, legal 3.3 V rail | exact board/revision, flash ID, USB/LDO path, strap loading, antenna, dimensions |
| Display | 128×64 I2C display supported by firmware at a probed address | controller identity, pin order, pull-ups, color, current, mounting envelope |
| Microphone | 3.3 V-compatible I2S source with the required slot and timing | exact breakout, pinout, port location, decoupling, acoustic mounting |
| Amplifier | legal I2S rate/format, 3.3 V operation, floating BTL output | exact module schematic, `SD_MODE`, gain, decoupling, heat, connector |
| Speaker | compatible impedance and power under named test conditions | exact driver, DC resistance, leads, enclosure, dimensions, measured clarity |
| Power | regulated rail over the source/load envelope with safe startup, shutdown, isolation, and faults | exact converter module and complete upstream/downstream schematic |
| Structure | no exposed powered conductor, controlled insulation and strain relief | exact received dimensions, assembly tolerance, RF/acoustic test geometry |

If one candidate changes, revisit firmware, wiring, CAD, service access, power,
audio, and RF. A substitute with the same headline description is not
automatically equivalent.

## Controller candidate

An ESP32-C3 SuperMini-style board is a candidate because the current source
tree and GPIO map target that family. “ESP32-C3” alone is insufficient:
marketplace boards can differ in flash population, USB-C implementation,
regulator, LED/boot-strap loading, antenna, headers, and dimensions.

For each received board:

1. photograph both faces and record markings and seller/lot;
2. measure the full envelope, including connector and installed headers;
3. read flash identity/capacity and confirm it fits the built image;
4. map `USB`, `5V/VBUS`, `3V3`, ground, buttons, LED, and relevant GPIOs;
5. check boot, flashing, and strap behavior on USB while the board is bare; and
6. identify the actual antenna region before any frame layout.

Do not connect the candidate controller to the provisional power chain until
that chain has been qualified independently.

## Display candidate

The firmware direction is a white 128×64 SSD1306-compatible I2C display and
can probe the intended addresses. A listing can still be wrong about the
controller, color, address, or pin order.

Before connection, read the received silkscreen from the actual viewing
direction, trace or meter ground, compare the module schematic if available,
and power it from a current-limited 3.3 V source. Scan I2C before deciding that
a blank screen is defective. Record address, current, dimensions, mounting
holes, display active area, connector access, and visible color.

## Audio candidates

### Microphone

An INMP441-style I2S breakout is a candidate because its interface can match
the firmware. Confirm the exact pin order, supply range, `L/R` selection,
clock requirements, and breakout decoupling. Keep flux, solvent, compressed
air, and heat away from the acoustic port; leave protective port tape in place
until the specified stage.

### Amplifier

A MAX98357A-based board is a candidate, but the Analog Devices IC datasheet
does not prove a no-name module's resistor network. Measure `SD_MODE`, inspect
gain selection, and capture I2S timing on the exact firmware. The IC does not
support a 24 kHz LRCLK; 16 kHz is a voice-band candidate, not identical audio
fidelity.

The speaker connects only between the two BTL outputs. Neither output is
ground. Do not attach an earth-referenced scope ground clip to either speaker
terminal.

### Speaker and enclosure

The current generic pre-boxed and rectangular `8 Ω` speakers are candidates.
Do not transfer the Same Sky speaker's `0.7 W`, `91 dB`, dimensions, or `1 cc`
test enclosure to them. Nominal impedance is frequency-dependent and can differ
from DMM resistance.

Qualify each received speaker as an acoustic assembly: driver, baffle, seal,
rear volume, opening, grille, adhesive, wires, and frame. Use the battery-free
A/B procedure in Lesson 10 at fixed gain, distance, sample, orientation, and
supply voltage. Select only after measuring clarity, buzz, relative level,
current, heat, fit, and repeatability.

## Power candidates

A one-cell source that crosses the 3.3 V rail suggests a true buck-boost
topology. That system requirement does not select a module. There is currently
no approved converter, holder, fuse/PPTC arrangement, reverse-polarity circuit,
switch/disconnect, USB service-power path, or UVLO implementation.

Important candidate distinctions include:

- TPS63070 IC operating voltage is not its cold-start voltage; a module claim
  must be tested against the manufacturer IC limits and the complete chain.
- TPS63802 IC capability does not guarantee an Amazon module's inductor,
  thermal layout, passives, settings, or output current.
- AO3401A and DMG2301L have different guaranteed on-resistance and cannot be
  treated as equal “20–40 mΩ” substitutes.
- Two parallel PPTCs do not exactly double hold/trip current; temperature,
  matching, sharing, and time-to-trip matter.
- A generic CR123A holder listing does not prove protected-16340 fit, polarity,
  contact force, or loaded resistance.

The Nitecore NL169 is a documented cell candidate: Nitecore publishes its
nominal energy/capacity, dimensions, and 2 A continuous-discharge rating. Its
public page does not publish the internal resistance or protection thresholds
and timing previously assumed by this project. Those values remain unknown.

No lithium cell is needed for Phase 0. Qualify the complete candidate chain
from a current-limited bench supply using Lesson 06. A cell may enter the
project only after the schematic, protection, normal low-voltage shutdown,
hard-disconnect/service behavior, charger pairing, heat, and fault gates close.

## Passives and connectors are exact parts too

“10 µF ceramic” is incomplete without dielectric, tolerance, voltage rating,
case, temperature behavior, and effective capacitance under DC bias. A bulk
electrolytic does not replace close ceramic decoupling. A ferrite bead requires
impedance-versus-frequency and DC-bias/current data; its DMM resistance does
not qualify it.

Likewise, “JST,” “USB-C,” and “2-pin plug” do not identify connector systems.
Record family, pitch, positions, mating part, pin-view direction, wire gauge,
ratings, keying, latch, crimp, insertion path, bend radius, and strain relief.
Genuine JST PH is 2.0 mm pitch; a “JST-PH 2.5 mm” listing is internally
inconsistent and requires identification rather than assumption.

## Frame and insulation candidates

Brass tube can be a structural candidate because it is workable and
conductive. Conductivity creates obligations: the frame is not a power or
signal path during qualification, decorative paint is not insulation, and
every board/wire needs retained primary insulation plus abrasion protection.

Exact stock diameter, wall, straightness, soldered geometry, finish, access,
tolerances, antenna clearance, speaker opening, and cell guard remain to be
measured. Do not freeze a frame around estimated module boxes.

## One-page incoming evidence record

For every candidate, record:

```text
role and candidate identifier:
manufacturer/order code, or seller/ASIN/lot if no manufacturer exists:
received markings and photographs:
primary datasheet/module document and revision:
pinout and viewing direction:
measured dimensions and mass:
unpowered continuity/resistance observations:
supply settings and current limit:
functional measurements and firmware revision:
thermal, transient, RF, or acoustic result where applicable:
known unknowns:
predeclared pass/fail rule:
disposition: reject / keep as experiment / qualified for next gate:
```

“Qualified for next gate” is not “approved for final purchase.” It means the
sample may proceed to the next controlled experiment.

## Component-release gate

The component setup remains **NO-GO** until one coherent configuration has:

- exact identifiers and received-part measurements;
- one reviewed schematic/netlist, including USB and every return path;
- matching firmware pins, protocols, sample rate, and flash requirement;
- battery-free power startup, load-step, isolation, and thermal evidence;
- battery-free speaker/enclosure and RF/frame A/B evidence;
- complete mechanical envelopes and service/assembly paths; and
- no unresolved contradiction between schematic, BOM, course, CAD, and tests.

Until then, named products are candidates for experiments, not purchase or
final-design claims.
