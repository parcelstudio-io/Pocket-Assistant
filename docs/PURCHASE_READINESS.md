# Purchase-readiness review — archived Claude R1 verdict

> **SUPERSEDED; NOT PURCHASE AUTHORITY.** The independent audit rejected this
> complete-cart verdict. Use
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md): its current
> decision is **GO only for one reversible `BUY-P0` qualification batch and
> NO-GO for a final build, cell connection, brass cutting, or pocket carry**.
> [MATERIALS.md](MATERIALS.md) is the matching archived R1 order sheet.

## Withdrawn R1 verdict (retained for review)

**Original claim — do not act on it:** “Buy the complete R1 cart now.” The part set was described as coherent, every
electrical interface closes on datasheet evidence, the power system uses
documented protected parts, and the procedure is bench-first so every
marketplace unknown is caught before irreversible work. What purchasing does
**not** release: connecting the cell (bench gate first), the first charge
(attended, after the cell gate), and pocket carry (acceptance tests).

Why the earlier NO-GO fell: it was attached to a converter/fuse/16340
architecture that tripled the device volume and demanded a lab-grade
qualification program. The final audit replaced that architecture with the
reference build's own topology on documented protected parts — see the
[current independent-audit summary](FINAL_MATERIALS_FOR_REVIEW.md#independent-audit-summary-claude-must-disposition).

## What the money buys, and in what order

1. **One pass, three carts** (Adafruit / DigiKey / Amazon — see the
   [order sheet](MATERIALS.md#order-sheet)). Adafruit ships from Brooklyn;
   fish paper is the slowest Amazon line, so it goes first.
2. **Bench bring-up** while brass waits: flash, breadboard, backend round
   trip, bench-supply power sweep. Multipacks exist so that qualification
   can measure several samples and keep the best.
3. **Cardstock dry-fit** with real parts → only then cut brass.
4. Optional finish materials (paint) are a separate, later, in-person buy —
   or skip them and keep raw brass like the reference.

## Remaining risks the cart cannot remove

| Risk | Screen |
| --- | --- |
| Clone SuperMini variance (LDO, VBUS path, flash size) | `esptool flash_id` gate; buy the multipack; qualify ≥2 boards; USB rule is procedural (switch off + pack unplugged), so no reliance on a clone's diode |
| LDO-direct rail sags under Wi-Fi + audio near end-of-discharge | Phase 0.5 bench sweep 4.2 → 3.3 V under worst load; fix ladder: bulk capacitance → bigger pack |
| OLED silkscreen pin-order variance | Read before wiring; the 5-pack has spares |
| Speaker loudness through a grille | Bench A/B at 1 m before frame work |
| Backend acceptability (third-party cloud receives mic audio) | Decide at Phase 0.3; self-host alternative documented |
| Fit vs the compact target | Cardstock gate; #4237 350 mAh pack is the short fallback; CAD fitcheck must be regenerated before it counts as evidence |

## What changed hands between reviews

- **Released now:** protected LiPo pack (#1578), USB-C Micro-Lipo charger
  (#4410), slide switch in the protected lead, INMP441 restored as primary
  mic, Same Sky enclosed speaker, full frame/insulation/tool cart.
- **Withdrawn:** Pololu #2873/#2810, PICO fuse, RUEF PPTCs, P-FET pairs,
  NL169/16340 + BH123A holder + external charger, service-jumper hardware,
  scope/current-probe instrumentation gates (now recommended, not blocking).
- **Unchanged rejections:** the video's mystery 14250 and can-soldering,
  frame as a conductor, grounded BTL leads, paint as insulation.
