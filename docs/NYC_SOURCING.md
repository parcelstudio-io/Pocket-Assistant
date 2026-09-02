# NYC sourcing — where every part actually comes from

> **UPDATED FOR THE R1 RELEASE — 2026-09-02.** Matches the released cart in
> [MATERIALS.md](MATERIALS.md). "Confirmed" means a listing/spec page was
> fetched on the stated date; re-check stock and price in the cart before
> ordering.

## The battery, solved locally

The R1 power pair ships from **Adafruit — which is in Brooklyn** (mail order,
no walk-in counter; typically 1–2 days to NYC):

| Pick | Part | Why | Where |
| --- | --- | --- | --- |
| **Cell** | Adafruit **#1578** — protected 500 mAh LiPo, JST-PH | Documented protection (overcharge, 3.0 V cutout, short), documented ≤500 mA charge | [adafruit.com/product/1578](https://www.adafruit.com/product/1578), $7.95, in stock 2026-09-02. Buy two |
| Smaller alternate | Adafruit **#4237** — protected 350 mAh | 7 mm shorter if the dry-fit is tight | $5.95, same order |
| **Charger** | Adafruit **#4410** — USB-C Micro-Lipo | 100 mA default / 500 mA jumper, 4.2 V termination, JST port | $5.95, same order |
| Do not buy | Nitecore NL169/16340 cells, CR123A holders, XTAR/Nitecore chargers | Withdrawn R0 architecture | — |

## Everything else, by cart

| Cart | Items | NYC timing |
| --- | --- | --- |
| **Adafruit** (Brooklyn) | #1578 ×2 · #4410 · optional #4237 / #6049 mic / #3006 amp | 1–2 days |
| **DigiKey** | CES-20134-088PM speaker ×2 (`2223-CES-20134-088PM-ND`) | 2–3 days |
| **Amazon Prime** | SuperMini pack · SSD1306 ×5 · INMP441 ×5 · MAX98357A ×3 · tact kit · slide switches · JST-PH 2.0 pigtails · passives · fish paper (slowest — order first) · Kapton · heat-shrink · wire · K&S #9831/#9861 (caliper on arrival) | 1–5 days |
| **K&S direct** (Chicago) fallback | #9831 metric tube $7.99 · #9861 rod $5.99 — if the Amazon ASINs resolve to the wrong variant | 2–5 days |
| **Home Depot pickup** (23rd St / 59th St / Brooklyn) — only if painting | 249322 self-etch · 2081830 gray · 7791830 satin white. **NYC Admin Code §10-117: spray paint is 21+, kept locked — bring ID** | same-day |
| **Blick / Canal Plastics** | White styrene .020″/.030″ for guards/baffle templates; Canal Plastics Center, 345 Canal St, M–F | same-day |

## Same-day emergency substitutes (Micro Center Brooklyn, 850 3rd Ave)

For breadboarding **tonight** — substitutes, not the BOM parts: Adafruit
MAX98357A amp $5.95, Adafruit ICS-43434 $4.99 I2S mic (the documented
alternate), 1.3″ OLEDs, hookup wire, heat-shrink. No ESP32-C3 SuperMini and no
INMP441 by name in-store. Tinkersphere (165 Broadway) offers same-day NYC
delivery with "last items" stock.

## Notes that survived the audit

- **Blick's in-store K&S rack is imperial**: the 1/16″ tube's ID (~0.88 mm)
  will **not** telescope over the 1.0 mm rod. The build needs the **metric
  #9831** — mail-order only.
- Fish paper is consistently the slowest Amazon consumable (about a week);
  McMaster-Carr (NJ, typically next-day) likely beats it if you're in a hurry.
- Buying paint in person avoids Amazon's aerosol/hazmat friction entirely —
  and painting is optional in R1 (the reference is raw brass).

## One-week plan

**Day 0:** place all three carts (Adafruit, DigiKey, Amazon) per the
[order sheet](MATERIALS.md#order-sheet). **Days 1–4:** as parts land, run
incoming checks (flash-ID the SuperMinis, caliper the brass and OLED, meter
the switch samples) and the Phase 0 bench bring-up from
[BUILD_GUIDE.md](BUILD_GUIDE.md). **Days 4–6:** cardstock dry-fit with real
parts; regenerate the CAD check if using it. **Day 6+:** cut brass. The cell
connects only after the bench gate passes, per the
[decision doc](FINAL_MATERIALS_FOR_REVIEW.md#release-gates-that-remain).
