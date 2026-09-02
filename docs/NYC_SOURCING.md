# NYC sourcing — where every part actually comes from

> **Cart tables superseded.** Buy only from [MATERIALS.md](MATERIALS.md);
> this file remains useful for the B&H cell trip, Home Depot paint pickup,
> Micro Center substitutes, and the NYC logistics notes.

Checked live on **2026-09-01** (Labor Day is Mon Sep 7 — carrier estimates
this week are padded). "Confirmed" means the listing/spec page was fetched
that day; B&H, Home Depot and Micro Center wall off bots, so call or check
the cart before traveling. Companion to the
[build guide](BUILD_GUIDE.md) — specs are unchanged, only sources move.

## The battery, solved locally

The Illumn/Keeppower pick fails NYC (loose Li-ion ships ground from San
Jose, ~a week). The replacement is *better documented* and has a Manhattan
retailer; online "in stock" does not guarantee same-day store pickup:

| Pick | Cell | Why | Where |
| --- | --- | --- | --- |
| **Primary** | **Nitecore NL169** — protected 16340, 950 mAh, 3.6 V, button top | Nitecore publishes **2 A max continuous** (2× our estimated ~1 A peak); 34.1 × 16.6 mm is compatible on paper with the BH123A envelope, subject to an arrival fit test | [B&H Photo](https://www.bhphotovideo.com/c/product/1811930-REG/nitecore_nl169_16340_li_ion_rechargeable.html), $9.95 — listing showed in stock but no store-display status; place an order/check pickup or call 800-606-6969 before traveling |
| Spare | A second exact NL169 | Same envelope and protection as the qualified cell | Buy only after one received cell passes the holder and load tests, unless return terms are acceptable |
| Do not substitute | NL169R or Fenix ARB-L16-700UP | Their integrated-port/protected envelopes are longer and were not fit-proven in this holder/layout | Useful only after a separate physical fit test, not as Rev A cart substitutions |
| Mail backup | NL169 from [Battery Junction](https://www.batteryjunction.com/products/nitecore-nl169) (Old Saybrook CT) | $6.95, ships ~Sep 4, CT→NYC 1–2 days | confirmed live |

**Charger:** buy the exact [XTAR ANT MC1 Plus USB-C](https://www.xtar.cc/product/xtar-ant-mc1-plus-charger-7.html)
variant from XTAR's official store (listed at $9.49 when checked). It supports
16340 and automatic 0.5/1 A charging; confirm that the received charger selects
0.5 A for this cell before first use. Alternate:
Nitecore UI1 ($11.99 FBA, 1 A max). If you want one in hand on the same B&H
trip, their 16340-capable unit is the Nitecore UMS2 (~$18–20, unverified).
**Do not buy** the Fenix ARE-X1 V2 (its own page: 18650/21700/26650 only, "not
compatible with the ARB-L16 series") or Olight's current 16340s (dual-polarity
magnetic-charging heads, unprotected — wrong for a standard holder).

## Everything else, by cart

| Cart | Items | NYC timing |
| --- | --- | --- |
| **B&H order / possible pickup** | One exact NL169 | confirm in cart or by phone |
| **DigiKey qualification cart** | DFR0954 · CMS-15113-078L100-67 speaker · BH123A holder; hold the PTC/passives until their carrier is designed | Recheck price, stock, and delivery in cart |
| **Mouser** | BOX-1511-1CC prototyping enclosure if using it instead of a later validated printed cup | Recheck stock; DigiKey showed no stock during the final audit |
| **Amazon Prime** | SuperMini 3-pack [B0G5XS345R](https://www.amazon.com/dp/B0G5XS345R) · INMP441 3-pack [B0972XP1YS](https://www.amazon.com/AITRIPAITRIP-AITRIP-Omnidirectional-Microphone-Interface/dp/B0972XP1YS) · tact-switch kit w/ white caps [B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4) · white 2:1 heat-shrink [B08N4W4K9X](https://www.amazon.com/Shrink-Tubing-Sizes-White-Ratio/dp/B08N4W4K9X) · Kapton · white M2.5 standoffs · K&S metric tube/rod only if the exact dimensions match | Recheck price, seller, and delivery in cart |
| **Adafruit** (ships **from Brooklyn**; no walk-in counter) | #326 OLED · #4209 JST-SH-to-male-header cable (the prior #4399 QT-to-QT cable cannot plug directly into a bare SuperMini) | Recheck before ordering |
| **Pololu** (Las Vegas) | S8V9F3 ($9.95, 349 in stock) · #2810 switch ($4.49, 189) — pick 2-Day air | ~Thu with air |
| **K&S direct** (Chicago) | **#9831 metric tube** (1.5 OD × 0.225 wall — ID ≈1.05 mm accepts the 1.0 rod) $7.99 · **#9861 1.0 mm rod** $5.99 | 2–5 days |
| **Home Depot pickup** (23rd St / 59th St / Brooklyn) | Rust-Oleum self-etch primer 249322 $10.48 · Stops Rust Satin White 7791830 $6.98. **NYC Admin Code §10-117: spray paint is 21+, kept locked — bring ID, flag an associate** | same-day (verify store stock in cart) |
| **Blick / Canal Plastics** | Plastruct/Evergreen **white styrene** .020″/.030″ for sub-plates (practical stand-in for white polycarbonate); Canal Plastics Center confirmed open, 345 Canal St, M–F | same-day |
| **Makelab, Industry City Brooklyn** | Potential later source for white PETG parts | **Hold:** this repository does not yet contain accepted printable cup/cradle/guard files |

## Same-day emergency substitutes (Micro Center Brooklyn, 850 3rd Ave)

For breadboarding **tonight** — these are *substitutes*, not the BOM parts:
Adafruit MAX98357A amp $5.95 (3 in stock — same chip as DFR0954; check its
dims before frame work), Adafruit ICS-43434 $4.99 / SPH0645 $6.95 I2S mics
(driver-config tweak vs INMP441), Inland ESP32-WROOM boards $7.99 (wrong
form factor — bench only), 1.3″ 128×64 OLEDs, hookup wire, white heat-shrink.
No ESP32-C3 SuperMini, no INMP441 by name. Tinkersphere (165 Broadway) is
alive with same-day NYC delivery but "last items" stock.

## Losses vs. the ideal list

- **Nickel-silver rod (the silver-no-paint frame option) is unobtainable
  fast**: Flex-I-File still sold out; Amazon only carries ≤0.33 mm; eBay
  ships from the UK in 1–3 weeks. → Rev A uses K&S brass rod + the white
  paint system; order NSR10 from eBay now if you want silver braces for a
  later revision.
- **Blick's in-store K&S rack is imperial**: the 1/16″ tube's ID (~0.88 mm)
  will **not** telescope over the 1.0 mm rod. The build needs the **metric
  #9831** — mail-order only.
- **White 30 AWG PTFE wire has no Prime-fast source**: Remington direct
  (IL, 2–3 days) is the realistic play; Amazon's only white PTFE ships from
  China (Sep 28+). White silicone wire is the same-week compromise.
- **Fish paper is the slowest FBA item** (Sep 9–15); McMaster-Carr (NJ,
  typically next-day) likely beats it — unverified.
- Jan's Hobby Shop (UES) is permanently closed; Shapeways' successor is
  EU-based — Makelab replaced both roles.

## One-week plan

**Stage 1:** order only the Phase 0 parts in
[PURCHASE_READINESS.md](PURCHASE_READINESS.md), retain return options, and run
incoming inspection plus breadboard tests. **Stage 2:** design/review USB
service isolation and the passive carrier. **Stage 3:** update FreeCAD with
the measured parts, add printable guards/door/cup, regenerate the fit report,
and make a 1:1 mockup. Order/cut/paint the final frame only after all three
stages pass.
