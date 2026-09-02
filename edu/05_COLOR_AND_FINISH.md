# 5 — White, silver, and black finish study

> **STATUS: PROVISIONAL VISUAL DIRECTION.** No exact paint, primer, clear coat,
> adhesive, surface preparation, cure schedule, or finish process is released
> by this note. It is not a purchase list or permission to coat the final frame.

Read [Lesson 11 — RF, EMC, antennas, and the metal frame](fundamentals/11-rf-emc-antennas-and-metal-frame.md)
and [Lesson 12 — soldering, mechanics, insulation, and tolerances](fundamentals/12-soldering-mechanics-insulation-tolerance.md)
before selecting a finish. Those lessons explain why coating cannot replace
isolation and why RF/mechanical behavior must be measured on the exact article.

## Palette and visual hierarchy

The working visual direction is:

- **satin white** for the dominant silhouette and removable protective guards;
- **bare-looking or satin silver** for braces and small hardware accents; and
- **black** for the display field, controls, acoustic opening, and selected
  functional details.

A roughly `45% white / 35% silver / 20% black` mock-up can help judge balance.
It is an artistic starting point, not a controlled finish ratio. White display
pixels can visually connect the black face to the white structure. Preserve
labels, polarity marks, warnings, debug access, and functional contrast even if
that changes the ratio.

## Non-negotiable boundaries

- Fabricate, join, clean, dry-fit, and qualify the **empty structure** before
  coating it. Keep every board, cable, display, microphone, speaker, plastic
  acoustic part, adhesive, and energy-storage device away from structural
  metalwork and finish operations.
- Treat the metal frame as conductive in every clearance and fault analysis,
  even if a coating looks continuous. Use separately specified electrical
  insulation, spacing, carriers, guards, bushings, and strain relief.
  **Paint is decoration and corrosion/surface treatment, not insulation.**
- Coating does not repair a weak joint, remove a burr, provide reliable strain
  relief, or make an adhesive joint structural.
- Never coat a cell or its contacts/wrapper, a connector contact, PCB, antenna
  or antenna keepout, microphone port, speaker diaphragm/surround, display
  glass/flex, switch mechanism, USB/debug opening, test point, configuration
  pad, heat-dissipating surface, or required marking.
- Do not assume that “plastic,” “nonmetallic,” “silver,” or “matte” predicts RF,
  thermal, acoustic, flammability, solvent, or electrical behavior.

## Candidate treatment by visual role

| Surface or feature | Candidate appearance | Qualification needed before use |
| --- | --- | --- |
| Empty main structure | Thin satin-white system | Exact substrate and joining residues identified; maker's technical/safety data applicable; full coating stack tested on offcuts; adhesion, cure, bend/scratch behavior, thickness, and dimensional fit recorded |
| Brace or hardware accent | Native metal appearance or provisional satin-silver system | Corrosion/tarnish plan, galvanic/material compatibility, joint/process compatibility, electrical-conductivity assumption, RF A/B result, and edge safety documented |
| Removable bezel or guard | Native white or black nonconductive material preferred | Material identity, temperature/flammability suitability, retention, fastener/adhesive compatibility, clearance, ventilation, service access, and RF/acoustic impact tested |
| Display and controller area | Black native field with a removable bezel/guard | Active area, connector, controls, indicators needed for diagnosis, antenna region, heat, and service access remain open |
| Microphone and speaker openings | Restrained black opening or qualified acoustic textile | Exact port/diaphragm remains untouched; cloth/mesh plus opening tested for level, clarity, buzz, sealing, contamination, and retention |
| Wires, connectors, and controls | Native black/white accents with durable endpoint labels | Color is not the sole polarity or pin identifier; labels survive handling and access remains possible |
| Cell/holder or other energy-storage area | Hidden behind a removable designed guard | No coating or adhesive touches the cell; contacts, insulation, polarity, inspection, ventilation if required, and tool-free removal remain available under the separately approved battery plan |

## Provisional process-development workflow

This workflow qualifies a future finish; it does not prescribe one:

1. Identify the exact structural alloy, solder/braze/joining process, residues,
   carrier/guard plastics, and all surfaces that must stay bare. Obtain the
   candidate finish and adhesive manufacturers' current technical and safety
   data.
2. Make representative offcuts with the same joints, cleaning, geometry, and
   surface preparation as the proposed frame. Keep an untreated control.
3. Apply the complete candidate primer/color/clear system to coupons only,
   using the manufacturer's ventilation, PPE, temperature, humidity, film,
   recoat, and cure requirements. “Dry to touch” is not full cure.
4. After full cure, record appearance, coating thickness/weight if relevant,
   adhesion, scratching, bending near a representative joint, cleaning-agent
   compatibility, and any cracking, softening, corrosion, residue, or odor.
5. Qualify each proposed adhesive separately on the exact cured finish and on
   the intended masked/bare substrate. A coating may become the weak layer, so
   a good adhesive datasheet alone does not validate the joint.
6. Repeat the full mechanical dry-fit with coating allowance included. Check
   fasteners, connector openings, guards, wire clearances, service tools, and
   all insertion/removal sweeps.
7. Only after coupon review, finish the empty structure while masking functional
   and clearance-critical zones. Retain a labeled witness coupon and product
   batch/cure record with the build evidence.
8. After electronics are installed, repeat isolation, thermal, acoustic,
   handling, and RF A/B tests. A visually successful finish is not accepted if
   any functional result regresses beyond its written limit.

Structural flux selection and residue removal follow the joining-material
manufacturer and [Lesson 12](fundamentals/12-soldering-mechanics-insulation-tolerance.md),
not a generic paint recipe. Adhesive selection likewise depends on exact
materials, loads, temperature, aging, serviceability, and the manufacturer’s
instructions.

## RF, thermal, acoustic, and tolerance cautions

### RF

Nearby coating, metal, pigment, guards, fasteners, wiring, and the user's hand
can change the antenna system. A metallic-looking pigment is not automatically
conductive, and a coating measured nonconductive at DC is not automatically
RF-neutral. Conversely, keeping paint outside a nominal antenna outline does
not guarantee radio performance because the surrounding frame and assembly also
matter.

Use the controlled baseline-versus-finished tests in
[Lesson 11](fundamentals/11-rf-emc-antennas-and-metal-frame.md): same firmware,
access point, channel, locations, orientations, timing, and trial count. Record
RSSI together with loss, reconnects, and functional range. Treat any result as
evidence for that exact geometry only.

### Thermal and acoustic

A guard or coating can block airflow, alter heat spreading, soften at operating
temperature, or conceal discoloration. Measure temperatures during the same
worst-case workload before and after the finished geometry is installed.

Paint, adhesive, cloth, mesh, bezel geometry, and seal condition can change an
acoustic opening or rear volume. Never spray through an acoustic opening. Test
the complete speaker/microphone assembly before and after guards at controlled
distance, orientation, gain, sample, and supply conditions.

### Tolerances and service

Coating adds thickness unevenly at edges, holes, clips, and mating surfaces.
Adhesive adds a bond-line thickness and can creep or shrink. Include both in the
tolerance stack and preserve an adjustment/removal path. Do not sand a finished
assembly near electronics to correct a fit error; return to the empty-structure
or carrier stage.

## Finish release evidence

- [ ] Exact product identities, batches, technical/safety data, substrates, and
      process conditions are recorded.
- [ ] Representative coupons pass the written adhesion, bend/scratch, cure,
      compatibility, and appearance limits.
- [ ] Adhesive joints, if any, have their own load/aging/serviceability evidence.
- [ ] Coating thickness is included in CAD/tolerance and access checks.
- [ ] Frame isolation relies on designed insulation—not coating—and passes an
      unpowered continuity/isolation audit after assembly.
- [ ] Exact finished geometry passes RF, thermal, acoustic, mechanical, and
      service-access comparisons.
- [ ] The finish leaves all warnings, polarity marks, ports, controls,
      connectors, test points, antenna space, and removal paths usable.

Until every applicable item passes, the white/silver/black treatment remains a
rendering and coupon study, not a final process.
