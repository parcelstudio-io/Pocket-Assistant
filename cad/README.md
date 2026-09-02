# CAD status and regeneration

> **STALE; NOT FIT OR FABRICATION AUTHORITY — 2026-09-02.** Everything in this
> directory models the withdrawn R0 architecture (16340 cell + BH123A holder +
> older Pololu stack, ~60 × 45 × 33 mm). It also predates the current F0
> candidate, which samples a 34 × 62 × 5 mm #258 pouch, #4410 charger, #2810
> switch, #2873 regulator, fuse, diode, two speaker geometries, and rigid cell
> guard. Use [docs/FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md).
> Do not regenerate from the old constants or cut brass. First measure the
> received Phase 0 parts, then rewrite `fitcheck.py`, regenerate every artifact,
> and verify the result with a 1:1 cardstock model.

`fitcheck.py` is the editable source for the placement study. The existing
`pager_rev_a.FCStd`, `pager_rev_a.step`, and `FITCHECK_REPORT.md` were
generated before the final audit; beyond the architecture change above, they
also used the wrong MPD BH123A dimensions, a discontinued capacitor, and an
incomplete antenna keepout. They are preserved for provenance only.
Regenerate after installing FreeCAD:

```bash
freecadcmd cad/fitcheck.py
```

Accept a new report only when every rule passes with measured part envelopes,
wire-bend room, insulation, fasteners, cell insertion/removal, and actual
connector plugs represented. A 1:1 cardstock/caliper dry fit remains required.
