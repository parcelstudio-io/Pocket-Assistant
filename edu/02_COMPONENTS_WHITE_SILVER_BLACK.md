# 2 — White, silver, and black candidate selection

> **Status: superseded selection study — 2026-09-02.** This lesson records the
> white/silver/black candidate-selection reasoning from the R0 review cycle.
> The R1 build release since restored several creator-faithful primaries
> (INMP441 microphone; generic SSD1306; protected LiPo pack instead of the
> 16340 chain) and made the finish optional (the reference is raw brass). The
> decision record is
> [FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md);
> where this page disagrees with it, the decision record wins.

This note turns the white/silver/black visual direction into selection criteria.
It does not turn a visually suitable part into an electrically or mechanically
accepted part.

## Read the evidence chain first

- [The R1 material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md) names the
  released parts and the rejections that survive from this study's era. It
  supersedes this page's purchase labels.
- [Components — turning candidates into evidence](02-components.md) explains
  why a product-family name or marketplace listing is not an exact part identity.
- [The fundamentals course](fundamentals/README.md), especially
  [boards, schematics, datasheets, and connectors](fundamentals/04-boards-schematics-datasheets-and-connectors.md),
  [power integrity and Li-ion systems](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md),
  [Class-D/BTL audio](fundamentals/10-class-d-btl-speakers-and-acoustics.md),
  [RF and the metal frame](fundamentals/11-rf-emc-antennas-and-metal-frame.md), and
  [mechanics, insulation, and tolerances](fundamentals/12-soldering-mechanics-insulation-tolerance.md)
  defines the durable engineering rules.
- [The project map](fundamentals/reference/project-map.md) identifies which
  files are requirements, firmware contracts, generated studies, or evidence.
- [BUILD_GUIDE.md](../docs/BUILD_GUIDE.md) and
  [ASSEMBLY_EVIDENCE.md](../docs/ASSEMBLY_EVIDENCE.md) are useful only when they
  agree with the released schematic, exact received parts, and current test
  evidence.

## Current Phase 0 digital/audio reference

These are qualification candidates, not a final BOM. The decision record
controls quantities and substitutions.

| Role | Study-era primary (the R1 decision record wins where it differs) | Interface to prove | Visual/fit implication |
| --- | --- | --- | --- |
| Controller | Plain USB-C ESP32-C3 SuperMini-layout board with at least 4 MB flash; exact maker/revision remains uncontrolled | Corrected-source GPIO map, flash identity, native-USB recovery, boot straps, power path, and antenna | Treat the native PCB as black/hidden; qualify multiple same-lot samples before designing its guard |
| Display | Adafruit `#326`, white 0.96-inch 128×64 OLED | GPIO20 `SCL`, GPIO21 `SDA`, 3.3 V-compatible I2C; firmware probes `0x3C` and `0x3D` | White pixels provide the intended accent; use the measured received-board envelope, not stale CAD |
| Microphone | Adafruit `#6049` ICS-43434 breakout | 16 kHz standard I2S; GPIO1 `WS/LRCLK`, GPIO2 `BCLK`, GPIO4 microphone data; 64 bit clocks per frame gives 1.024 MHz; `SEL` low selects the intended left slot | Controlled black bottom-port board; leave its port open and uncoated. The discontinued microphone is a one-off qualification choice, not a production baseline |
| Amplifier | Adafruit `#3006` MAX98357A mono breakout | Shares GPIO1 `LRC` and GPIO2 `BCLK`; GPIO3 drives `DIN`; Adafruit's documented 2.7–5.5 V board input covers the candidate 3.3 V regulator's full tolerance. Prove reset-time loading, channel/mode, gain, and floating BTL output | Blue 19.4 × 17.8 × 3.0 mm PCB plus its pre-soldered terminal-block envelope; conceal it behind a removable ventilated guard and measure the complete received assembly before CAD |
| Speaker | Same Sky `CES-20134-088PM`, factory-enclosed, bare leads, 8 ohm, 0.8 W | Connect only to the Adafruit `#3006` screw-terminal BTL pair; qualify level, current, temperature, grille, feedback, and speech quality | The controlled black enclosure supplies its own rear cavity. Design only the front outlet, mounting, protection, and lead strain relief; do not invent an extra rear cup |
| Action control | Omron `B3F-1000` SPST-NO plus white `B32-1060` cap | GPIO10 to ground, active low; identify the paired switch legs by continuity | The cap is a small white accent, but finger access and the guard opening still require a physical mock-up |

### Historical microphone references

The R1 release restored **INMP441** as the primary microphone (it is the
creator's part and is in-spec at this build's 1.024 MHz bit clock); the
ICS-43434 breakout this page discusses remains the documented alternate.
Either way, raw-IC compatibility claims do not establish a marketplace
module's silicon, pin order, bypassing, or assembly quality — inspect the
received board. The creator binary's separate recovered contract uses
microphone data on GPIO8 at 24 kHz; never combine that binary with the
corrected-source GPIO4/16 kHz harness above.

DFRobot `DFR0954` remains only an alternative amplifier. The MAX98357A
breakouts document a 2.5–5.5 V supply, which the R1 raw-cell rail sits
inside; DFR0954's published 3.3 V minimum does not. Do not substitute it
without revisiting the rail analysis and the decision record.

## Visual direction, not an electrical rule

Use three visual roles:

- **White:** the dominant structural silhouette, removable guards, or bezel.
- **Silver:** restrained braces, fasteners, and small structural accents.
- **Black:** the display field, controls, acoustic opening, and deliberately
  visible electronics.

Prefer a material's native color or a removable nonconductive cover over coating
a functional part. A roughly `45/35/20` white/silver/black split is a useful
mock-up starting point, not a production tolerance. Readability, safe access,
radio performance, heat flow, sound, and electrical isolation take priority.

## Candidate-selection matrix

Every row remains **provisional** until its evidence column is complete.

| Function | Interface that must agree | Color treatment that may be explored | Evidence required before acceptance |
| --- | --- | --- | --- |
| Controller | Exact board revision, flash capacity, legal supply path, USB behavior, boot straps, GPIO map, antenna implementation, and firmware build | Leave the PCB native; use a removable black or white guard outside antenna and service zones | Both-face photographs, chip/board markings, flash report, bare-board boot/flash test, measured pin map and dimensions, USB/power-path investigation, and antenna location on the received unit |
| Display | Exact controller, I2C voltage/address/pin order, current, active area, connector direction, and supported firmware driver | Black display field with a removable white bezel | Primary documentation where available, incoming pin-order check, current-limited I2C test, full-pixel test, caliper envelope, plug and wire-bend volume |
| Microphone | Supply limits, I2S slot/timing, pin order, port location, clock compatibility, and firmware input contract | Native black board behind a non-sealing acoustic opening | Exact breakout inspection, schematic or trace evidence, logic/audio capture, intelligibility test, measured port clearance, contamination-control plan |
| Amplifier | Supported sample rate/format, legal supply, channel/configuration network, shutdown behavior, heat, and floating BTL outputs | A ventilated, removable black guard | Exact module inspection, configuration measurements, low-level audio test, current/temperature record, and proof that neither speaker terminal connects to ground or frame |
| Speaker assembly | Impedance/power compatibility, lead termination, front outlet/grille, mounting, and useful speech response; add a rear-volume design only for an open-driver alternative | Native black/silver driver behind an acoustically transparent black opening | Exact driver and connector identity, DMM sanity check, caliper envelope, controlled grille/mount A/B test, buzz/clarity/current/temperature results, and strain-relief evidence; verify rather than replace a factory enclosure |
| Power and energy storage | Complete source-to-load schematic, operating envelope, startup/shutdown, faults, reverse connection, disconnect/service-power behavior, rail limits, test points, cell/holder/charger compatibility | Hide behind removable nonconductive guards; keep polarity and safety markings visible | Reviewed schematic/netlist, exact component/module revisions, manufacturer limits, current-limited sweep, transient/thermal/fault results, connector/contact measurements, and a separate approved battery-integration plan |
| Controls and service access | Normal state, logic levels, boot-strap interaction, debounce, USB/debug access, and safe service isolation | Black actuator in a white or silver opening | Exact pin/terminal map, firmware behavior, access study with real plugs/fingers/tools, cycle test, and a documented service-power procedure |
| Frame, carriers, guards, and finish | Structural loads, insulation, tolerances, wire paths, component retention, acoustic opening, antenna region, heat, sharp-edge and pocket protection | White main form, silver accents, black functional openings | Exact received-part measurements, 1:1 mock-up, tolerance stack, CAD including plugs/wires/fasteners/removal sweeps, offcut process coupons, isolation test, and assembled RF/audio/thermal evidence |

The current source-build contract is versioned in
[`firmware/src/boards/pocket-wall-e-c3/config.h`](../firmware/src/boards/pocket-wall-e-c3/config.h).
A candidate must match the contract that is actually built and flashed. Do not
mix a vendor binary's wiring with the source-build wiring.

## Color-treatment boundaries

These are release constraints, not styling suggestions:

- Treat every metal frame member as conductive even after painting. Use
  separately specified insulation, spacing, carriers, guards, and strain relief.
  **Paint is never electrical insulation.**
- Do not coat a cell, cell contact, connector contact, PCB, microphone port,
  speaker diaphragm or surround, antenna/keepout, button mechanism, USB opening,
  test point, adjustment/configuration pad, warning, polarity mark, or part label
  needed for inspection.
- A guard must remain removable where diagnosis, cell handling, a service link,
  or a connector requires access. Cosmetic adhesive is not a substitute for a
  designed fastener or retention feature.
- A black mesh or cloth must be acoustically qualified with the exact speaker
  opening. A white or silver radio cover must be RF-qualified in the exact
  finished geometry. Color does not predict either result.
- Do not hide heat-producing parts in tight sleeves. Document airflow, contact
  surfaces, maximum temperature, and the test condition.
- Preserve enough clearance for real connectors, wire bend radii, assembly
  tools, tolerances, guards, and removal paths—not only bare PCB outlines.

## Evidence checklist for each exact candidate

Create one traceable record per received lot or revision:

- [ ] Seller, manufacturer if known, order code, lot/date, and photographs of
      both faces, labels, packaging, connectors, and jumpers are recorded.
- [ ] Manufacturer documentation and the listing are saved separately; claims
      belonging only to the underlying IC are not attributed to the module.
- [ ] Pin order, connector family/pitch, jumper state, polarity, dimensions,
      mass, mounting features, and keepouts are measured on the received sample.
- [ ] The electrical schematic/netlist, firmware contract, and mechanical model
      name the same exact revision and configuration.
- [ ] Bench tests use a current-limited source and written limits; batteries are
      absent unless a later, separately approved battery plan explicitly calls
      for them.
- [ ] Power, digital, audio, USB/service, fault, thermal, RF, and acoustic tests
      are completed where applicable, with raw observations retained.
- [ ] CAD includes plugs, cables, wire bends, fasteners, carriers, insulation,
      coating allowance, guards, antenna region, acoustic volume, and all access
      or removal sweeps.
- [ ] At least one independent reviewer can trace every acceptance claim to a
      primary document, measurement, or repeatable test result.

## Purchase and freeze decision

This study's HOLD/BUY-P0 labels are superseded: the 2026-09-02 final audit
released the complete R1 cart in
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md), and
the finish became optional (the reference build is raw brass; the white
system in [the finish study](05_COLOR_AND_FINISH.md) remains available).

What survives from this study unchanged: the rejections (mystery cells,
frame-as-conductor, paint-as-insulation, grounded BTL leads) and the method —
a received sample still passes incoming inspection and its bench gates before
it is soldered into the frame, and passing a script, compiling firmware, or a
collision-free CAD view never substitutes for that evidence.
