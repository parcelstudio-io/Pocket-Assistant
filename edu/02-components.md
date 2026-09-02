# Components — turning candidates into evidence

> **Status: qualification lesson; R1 examples superseded.** This is not a BOM
> or purchasing list. The only current authority is the status-marked Phase 0
> list in [FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md);
> [MATERIALS.md](../docs/MATERIALS.md) is an archived proposal. Every received
> sample must pass its incoming and bring-up gates before it can be considered
> for a future final design.

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
| Microphone | #6049 ICS-43434 Phase 0 primary or held INMP441 alternative using the required left slot and timing | exact received breakout, GPIO4 capture, port location, decoupling, acoustic mounting; carrier pin orders are not interchangeable |
| Amplifier | MAX98357A breakout, legal I2S rate/format, regulated whole-load supply, floating BTL output | exact received schematic/revision, partial-power signal isolation, reset-safe `SD` mode, gain, decoupling, heat, terminal envelope |
| Speaker | compatible impedance and power under named test conditions | exact driver, DC resistance, leads, enclosure, dimensions, measured clarity |
| Power | current candidate: qualified cell/charger/fuse/MOSFET switch feeding #2873; its regulated 5V_SYS feeds the amp and diode-isolated controller path | reviewed schematic, recalculated low-cell demand, TXU0104 one-way signal-isolation experiment, source/GPIO reverse-current, cutoff/restart, thermal, and fit gates in the current decision |
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

Adafruit **#6049 ICS-43434** is the Phase 0 primary; INMP441 is a held
alternative. Connect microphone data (`DOUT`, or alternate `SD`) to GPIO4,
share GPIO1 word select and GPIO2 bit clock, and tie its documented slot select
low for the intended left slot. At 16 kHz and 64 clocks per frame, expect
1.024 MHz BCLK. Confirm exact carrier pin order, supply behavior, bit/slot
alignment, decoupling, and intelligible capture. Keep flux, solvent,
compressed air, glue, paint, and heat away from the acoustic port.

INMP441 references in the video and older lessons are **historical/alternative
context**, not permission to buy or wire an anonymous carrier. IC-level timing
compatibility does not prove a marketplace breakout's identity or assembly.

### Amplifier

The Phase 0 primary is the controlled Adafruit `#3006` MAX98357A breakout.
Its documented 2.7–5.5 V board range covers candidate `5V_SYS` on paper. The
amp sits behind the same #2873 low-voltage cutoff as the controller, while a
four-channel partial-power isolation experiment separates its I2S/`SD` pins
from a USB-powered MCU when the amp rail is absent. Measure the received
board's `SD` voltage/channel mode and gain state, and capture both TX slots at
16 kHz. Source inspection predicts an inactive right slot, so default mono-mix
**must not** be called full amplitude. A published PCB size excludes any
terminal-block, wire, and tool envelope, which must be measured before layout
acceptance.

DFRobot `DFR0954` is a **former primary and current held alternative** because
its published 3.3 V minimum lacks guaranteed overlap with the candidate
regulator's 3.201 V worst-case output. Do not buy both boards or transfer
DFRobot, Adafruit, or no-name resistor assumptions between them. Any promotion
of DFR0954 requires the rail and review gates in the material decision to close.

The MAX98357A does not support a 24 kHz LRCLK; 16 kHz is a voice-band choice,
not identical audio fidelity.

The speaker connects only between the two BTL outputs. Neither output is
ground. Do not attach an earth-referenced scope ground clip to either speaker
terminal.

### Speaker and enclosure

The current primary sample is Same Sky `CMS-20143-158SP`, 8 ohm and 1.5 W
nominal, tested in a repeatable sealed baffle. The factory-enclosed
`CES-20134-088PM`, 8 ohm and 0.8 W nominal, is the comparison and requires a
measured hard power cap before promotion. Nominal impedance is still
frequency-dependent and can differ from DMM resistance.

Connect a speaker only across the `#3006` BTL screw terminal, never to ground
or the frame. The Phase 0 set compares the open CMS-20143-158SP in a controlled
sealed fixture against the enclosed CES-20134-088PM. Use the battery-free A/B
procedure in Lesson 10 at fixed gain, distance, sample, orientation, and supply
voltage. Accept one only after measuring clarity, buzz, relative level,
feedback, current, heat, fit, and repeatability.

## The power system

The current Phase 0 chain is a **candidate**, not released wiring: shared
cell/#4410 node → candidate fuse → #2810 MOSFET switch → #2873 whole-load
5V_SYS → amp plus diode-isolated controller path. The TXU0104 section of a TI
TXU-EVM tests the powered-MCU/unpowered-amp signal boundary: #2873 `PG` gates
its `OE`, while GPIO5 crosses channel 4 to control amplifier shutdown. The
earlier TXB0104 network is rejected for this role. The exact topology and
gates are in [the current decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md). The older
direct-rail calculation remains only as an archived worked example in
[the power-chain lesson](07-the-power-chain.md).

Lessons the withdrawn chains left behind — they generalize to any project:

- An IC's operating voltage is not its cold-start voltage; a module listing's
  claim must be tested against the manufacturer IC limits and the whole chain.
- IC capability never guarantees an anonymous module's inductor, thermal
  layout, passives, settings, or output current.
- Two parallel PPTCs do not exactly double hold/trip current; temperature,
  matching, sharing, and time-to-trip matter.
- A holder listing does not prove cell fit, polarity, contact force, or
  loaded resistance — and a cell page that omits protection thresholds is not
  a protection spec (this is what disqualified the NL169/16340 path).

No lithium cell is needed until the very last gate. Qualify the complete
chain from a current-limited bench supply using Lesson 06; the pack enters
only after the bench, fit, and unpowered gates close, and charges only
attended.

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

A received sample set is accepted for final assembly only once one coherent
configuration has:

- exact identifiers and received-part measurements;
- one reviewed schematic/netlist, including USB and every return path;
- matching firmware pins, protocols, sample rate, and flash requirement;
- battery-free power startup, load-step, isolation, and thermal evidence;
- battery-free speaker/enclosure and RF/frame A/B evidence;
- complete mechanical envelopes and service/assembly paths; and
- no unresolved contradiction between schematic, BOM, course, CAD, and tests.

Purchases follow the R1 cart in
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md) and
[MATERIALS.md](../docs/MATERIALS.md). No named product in this lesson is
independent purchase authority; a released part still fails acceptance if the
received sample fails its gates.
