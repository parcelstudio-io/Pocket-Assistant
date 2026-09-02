# CAD status and regeneration

> **STALE vs the R1 release — 2026-09-02.** Everything in this directory
> models the **withdrawn** R0 architecture (16340 cell + BH123A holder +
> Pololu regulator/switch stack, ~60 × 45 × 33 mm). The released R1 design is
> the compact protected-LiPo layout (~45 × 32 × 20 mm target) in
> [docs/FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md).
> Before cutting brass, rewrite `fitcheck.py`'s part set for the R1 BOM
> (pack 29 × 36 × 4.75 mm, charger 24 × 19 × 7.2 mm, no holder/regulator)
> using measured envelopes from the received parts — or rely on the required
> 1:1 cardstock dry fit alone.

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
