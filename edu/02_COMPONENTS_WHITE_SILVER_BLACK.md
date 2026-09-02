# 2 — White, silver, and black candidate selection

> **DESIGN/PURCHASE FREEZE: NO-GO.** This note is not a BOM, shopping list,
> wiring diagram, or permission to fabricate the final frame. It intentionally
> contains no exact purchase identities or quantities. The repository currently
> contains conflicting “locked” and “qualification only” status claims in
> [MATERIALS.md](../docs/MATERIALS.md) and
> [PURCHASE_READINESS.md](../docs/PURCHASE_READINESS.md). That conflict must be
> reconciled in a reviewed release record before a component or frame freeze.

This note turns the white/silver/black visual direction into selection criteria.
It does not turn a visually suitable part into an electrically or mechanically
accepted part.

## Read the evidence chain first

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
| Speaker assembly | Impedance/power compatibility, lead termination, baffle/seal/rear volume, outlet geometry, and useful speech response | Native black/silver driver behind an acoustically transparent black opening | Exact driver and connector identity, DMM sanity check, caliper envelope, controlled enclosure A/B test, buzz/clarity/current/temperature results, and strain-relief evidence |
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

Until the contradictory repository status banners and the missing evidence are
resolved:

- **Qualification samples:** HOLD for an explicit, scoped Phase 0 authorization.
- **Final electronics quantities:** HOLD.
- **Final cell/holder/charger or battery integration:** HOLD.
- **Final frame stock cut to size, carriers, guards, and irreversible finish:**
  HOLD.
- **Legacy named component lists and legacy power chains:** REJECT as design or
  purchase authority.

A final **GO** requires one reconciled BOM/revision, one reviewed full schematic,
one matching firmware contract, exact-sample bench evidence, measured mechanical
evidence, and a signed release record. Passing a script, compiling firmware, or
producing a collision-free nominal CAD view does not satisfy those gates alone.
