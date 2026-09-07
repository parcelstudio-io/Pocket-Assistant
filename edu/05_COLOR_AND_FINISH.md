# White, silver, and black finish study

> **Status: provisional visual direction.** This is not a paint recipe,
> purchase list, or release to coat the final frame.

The intended palette is satin white for the dominant silhouette, silver for
small structural accents, and black for the display field, controls, and
acoustic details. Functional requirements take priority over the palette.

Read [Lesson 11](fundamentals/11-rf-emc-antennas-and-metal-frame.md) and
[Lesson 12](fundamentals/12-soldering-mechanics-insulation-tolerance.md) before
developing a finish. Current hardware and release status remain in the
[material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md).

## Functional boundaries

| Area | Requirement |
| --- | --- |
| Conductive frame | Treat as conductive after finishing; isolate it from every net |
| Guards and bezels | Prefer identified nonconductive material; preserve retention and service access |
| Display and controls | Keep active area, labels, controls, indicators, and recovery access clear |
| Microphone and speaker | Do not coat ports, diaphragms, surrounds, or required acoustic volume |
| Antenna region | Keep the tested antenna space and repeat RF comparisons after finishing |
| Connectors and test points | Mask contacts and preserve insertion, probe, and removal paths |
| Cell area | No coating or adhesive on a cell, wrapper, contacts, or inspection/removal path |
| Thermal surfaces | Do not cover a heat path without repeat temperature evidence |

Paint is decoration and surface treatment, not electrical insulation. Design
clearance and solid barriers independently:

```text
 clearance
 coated metal edge █████│<── measured air gap ──>│ live pad

 insulated pass-through
 outside      conductive frame wall       inside
 cable ─────[ qualified bushing ]──────── cable
                  █████████
```

The coating is ignored when making an electrical-safety claim. A bushing,
carrier, guard, spacing feature, or other separately qualified barrier must
provide the protection.

## Development sequence

1. Identify the exact substrate, joining residues, candidate finish, and every
   area that must remain bare. Follow the manufacturers' current technical and
   safety data.
2. Apply the full process to representative offcuts, keeping an untreated
   control. Record preparation, batch, film, environment, and full cure.
3. Test adhesion, scratching, bending near joints, cleaning compatibility, and
   coating thickness. Qualify adhesives separately on the exact surface.
4. Repeat the mechanical dry fit with coating thickness included.
5. Finish only the empty structure, with electronics and stored-energy devices
   outside the work area.
6. After assembly, repeat isolation, RF, thermal, acoustic, mechanical, and
   service-access comparisons against the unfinished baseline.

Stop if the finish cracks, softens, traps residue, changes fit, blocks access,
degrades radio/audio/thermal results, or obscures a required marking. Until
coupon work and all applicable comparisons pass, the palette remains a visual
study only.
