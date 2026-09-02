# 12 — Soldering, mechanics, insulation, and tolerances

## Learning objectives

After this lesson, you should be able to:

- explain wetting, flux, heat flow, and why solder is not glue;
- make and inspect a practice electrical joint before touching project parts;
- separate electrical soldering from structural metalwork;
- design strain relief and insulation for a conductive enclosure;
- reason about nominal dimensions, tolerance, clearance, and tolerance stacks;
- identify where sound, radio, buttons, connectors, and the cell need space.

## A joint is a controlled metallurgical interface

Molten solder must **wet** the clean metal surfaces. Wetting means the solder
spreads and bonds at the interface instead of sitting as a ball. Three things
must happen together:

1. the surfaces must be solderable and free of disruptive oxide or dirt;
2. flux must remove or inhibit oxide while the joint is hot; and
3. both workpieces—not merely the solder wire—must reach the needed
   temperature for the needed time.

The iron transfers heat; solder supplies the alloy; flux enables wetting. A
tiny amount of solder on the tip improves thermal contact, but feeding all the
solder onto the tip can leave the workpieces too cold.

During soldering, a thin intermetallic layer forms between solder and the base
metal. Too little heat gives incomplete wetting. Excessive heat or dwell time
can damage pads, insulation, plastic connectors, microphones, and nearby
components. More temperature is not a substitute for the correct tip size,
clean surfaces, flux, and contact area.

## Electrical versus structural soldering

The pocket assistant contains two very different tasks:

- **Electrical joints:** small copper pads, wires, and headers. Use
  electronics-grade flux and solder with controlled heat.
- **Structural metalwork:** a brass or other metal shell/frame with much higher
  thermal mass and possibly a surface finish. It may need different surface
  preparation, flux, alloy, heat source, and ventilation.

Do not let aggressive acid/plumbing flux touch electronics. Residue can be
corrosive or conductive. Do not heat the enclosure with boards, display,
speaker, microphone, wiring, foam, or battery installed. Build and clean the
structure separately; mechanically finish it; then install electronics.

Whether a particular structural joint can be made safely with the purchased
iron is a **MEASURED process-qualification question**, not something CAD can
answer. Practice on offcuts of the exact stock and finish first.

Never solder directly to a lithium-ion cell. Use an intact, protected cell and
a mechanically matching connector/contact system specified for it.

## Tip, temperature, and thermal mass

Heat energy flows from the tip into the work. A very fine tip has little
contact area and stored thermal energy, so it may struggle with a ground plane
or metal frame even when its displayed temperature is high. A broader chisel
tip often heats a pad and lead faster, reducing total dwell time.

Use the lowest process temperature that produces prompt, repeatable wetting
with the actual solder alloy. Follow the solder/flux and component
manufacturers' limits. The station display is tip-heater feedback, not a
measurement of the component body or joint temperature.

For an electrical through-hole joint:

1. clean and mechanically stabilize the work;
2. wet the clean tip with a small amount of solder;
3. touch pad and lead together with the tip;
4. feed solder at the joint, not only onto the tip;
5. remove solder, then the iron;
6. hold still while it solidifies; and
7. clean residue if the flux process requires it.

Always use fume extraction or effective local ventilation and eye protection.
Wash hands after handling solder and do not eat at the bench. “Lead-free” does
not make fumes, flux, heat, or sharp clippings harmless.

## What inspection can and cannot prove

A good small electrical joint normally shows complete wetting of pad and lead,
a smooth continuous fillet, no unintended bridge, and no scorched laminate or
receded insulation. Appearance depends on alloy; lead-free joints need not look
mirror-bright.

Visual inspection finds many defects but not all of them. Follow it with:

- an unpowered continuity/net check;
- a gentle strain inspection of the wire's support, not a pull on the pad;
- current-limited functional testing; and
- voltage-drop measurement for important power paths.

A beeping continuity meter does not prove a high-current joint has low enough
resistance.

## Wires need mechanical support

A solder joint should make an electrical connection, not act as the only cable
anchor. Motion concentrates stress where flexible wire becomes rigid with
solder. Provide strain relief so the load is transferred to the enclosure or a
tie point before it reaches the pad.

Useful methods include a clamped cable jacket, lacing/tie points, adhesive made
for the materials and temperature, a service loop, and heat-shrink over a
spliced wire. Check that strain relief does not block a connector latch,
microphone port, speaker vent, antenna region, or service access.

Avoid wicking solder far up stranded wire; the stiffened section moves the
fatigue point rather than eliminating it.

## Conductive enclosure: insulation is a system

A white/silver metal enclosure is electrically conductive even if it is painted
or powder-coated. Decorative finish is not dependable primary insulation:
edges, screw heads, scratches, soldered seams, and abrasion can expose metal.

For each board and wire, define:

- a primary insulating barrier with a known material and thickness;
- edge and corner clearance;
- mechanical retention that prevents migration;
- protection against cut wire ends and solder spikes;
- inspection access; and
- a plan for heat without squeezing the cell.

The metal frame should not be used as the project's current return unless a
future reviewed schematic deliberately makes it one. A floating frame is not
automatically harmless: capacitive coupling, loose conductors, ESD, or a cut
insulation layer can still create faults.

## Dimensions are distributions, not perfect numbers

A drawing's nominal `20.0 mm` dimension is a target. Real parts vary. A
tolerance such as `20.0 ± 0.2 mm` permits values from `19.8` to `20.2 mm`.
Marketplace modules may also change layout without changing the listing.

For a simple worst-case clearance:

```text
minimum clearance
  = smallest available opening
  - largest possible installed part
```

If a slot is `20.2 ± 0.2 mm` and the received module is
`20.0 ± 0.15 mm`, then:

```text
smallest slot = 20.0 mm
largest module = 20.15 mm
minimum clearance = -0.15 mm
```

**CALCULATED:** the nominal `0.2 mm` gap can become a `0.15 mm` interference.
The design is not released merely because nominal CAD bodies do not collide.

### Tolerance stacks

Several small variations add along an assembly path: enclosure bend, bracket,
adhesive, board edge, connector body, plug, and cable bend radius. In an early
prototype, add the worst cases conservatively and measure exact received
parts. Statistical tolerance analysis becomes appropriate only with a known
manufacturing process and distribution.

## Functional keepouts

A component's rectangular body is not its whole envelope:

| Part | Space that a box model often misses |
| --- | --- |
| Connector | mating plug, latch, finger access, insertion/removal path, cable bend |
| Button/switch | actuator travel, finger/tool access, service clearance |
| Speaker | front opening, rear volume, seal, diaphragm excursion, wires |
| Microphone | acoustic port path, gasket/seal, contamination protection |
| Antenna | RF keepout, nearby metal/plastic, product-use orientation |
| Battery | wrapper protection, contacts, removal path, swelling/fault clearance |
| Board | solder joints, wire loops, programming cable, component height variation |

An enclosure can pass collision checking and still be unassemblable,
unserviceable, acoustically poor, or unsafe.

## Build order for this project

The robust order is:

```text
qualify soldering on scrap
→ measure exact received parts
→ make a paper/cardstock or printed fit mock-up
→ build and clean the empty metal structure
→ deburr and inspect every edge
→ install primary insulation and mechanical mounts
→ install already bench-tested electronics without a cell
→ test access, strain relief, acoustics, heat, and RF
→ introduce the protected cell only after the electrical release gates pass
```

This is deliberately different from soldering a shell around live,
irreplaceable electronics.

## Safe lab: a practice coupon and tolerance stack

### Part A — electrical coupon

Use scrap protoboard, inexpensive wire, and a resistor—not a project module.

1. Make five joints with the intended solder, flux, tip, and ventilation.
2. Photograph both sides and label tip, set temperature, and approximate dwell.
3. Inspect for wetting, bridges, pad damage, and melted insulation.
4. With power off, measure continuity and isolation to adjacent pads.
5. Anchor one wire with strain relief, leave another supported only by its pad,
   and gently move the cable near the anchor. Observe where bending concentrates.
6. Improve the process until five consecutive joints pass the same criteria.

Do structural-metal experiments on a separate offcut with electronics absent.

### Part B — paper tolerance model

Measure one received board in length, width, and maximum height. Add envelopes
for its connector, plug, cable bend, mounting/insulation thickness, and tool or
finger access. Cut both nominal and conservative maximum outlines from card.
Fit the conservative outline through the intended assembly and removal path.
Record what the model still omits.

## Common mistakes

- Treating solder as filler or glue instead of heating both interfaces.
- Raising temperature indefinitely when the real problem is an oxidized or
  undersized tip.
- Using plumbing flux near electronics.
- Assuming “no-clean” always means residue is harmless in every process.
- Using paint or anodizing as the only barrier against a metal enclosure.
- Modeling only component bodies, not plugs, cables, sound paths, and hands.
- Choosing wire length before the assembly and service routes are proven.
- Installing the cell before heating, drilling, deburring, or soldering the frame.

## Check yourself

1. Why can a broader tip expose a component to less total heating than a needle
   tip on a large pad?
2. Is a visually good solder joint sufficient evidence for a power connection?
3. Why is a painted metal frame still treated as conductive?
4. A module and opening both fit at nominal size. What two additional checks
   are required before release?

<details>
<summary>Answers</summary>

1. Better contact and thermal capacity can bring both surfaces to soldering
   temperature quickly, reducing dwell time.
2. No. Add unpowered checks and a loaded voltage-drop/functional test.
3. Finish can be thin, scratched, cut at edges, or penetrated by hardware; it
   is not reliable primary insulation.
4. Analyze worst-case tolerance/clearance and physically test the exact part's
   complete installation, connector, cable, access, and removal envelopes.

</details>

## Authoritative further reading

- [NASA workmanship standard for soldered electrical connections](https://standards.nasa.gov/standard/NASA/NASA-STD-87394)
- [Kester soldering knowledge base](https://www.kester.com/knowledge-base)
- [JST PH connector family drawing (2.0 mm pitch)](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf)
- [Espressif ESP32-C3 PCB and antenna layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html)
