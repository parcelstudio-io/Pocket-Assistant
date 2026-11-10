# Purchased inventory — Desk satellite

Factual purchase record: what was *bought*, not what is approved; part authority stays in
[`FINAL_BUILD.md`](FINAL_BUILD.md). Everything owned from the other builds (the charger board, the
controller, the 16340 holder, the JST-PH pigtails, the Schottky, the filament, the resistors, the button,
wire, tape, heat-shrink, the stainless rod, the adapter) is in `../../pocket_ai_assistant/docs/INVENTORY.md`
and `../../cyber_clock_v2/docs/INVENTORY.md` and is not repeated here.

**Status check 2026-11-03, 06:17 to 06:28 EST** (Amazon Orders page, Gmail and the building's package log; the per-project list is `../../PARTS_BY_PROJECT.md`): the LED chips arrive 11-04, the wings 11-07, the disc 11-18; the Eujgoov order is **cancelled**, so there is no fallback wing; the cells were never a November order (see the corrected IMR row) and are on hand.

**Pick-ups** (completed Todoist tasks): the LED chips and the wings 2026-11-05, the disc 2026-11-06 (UPS from the maker, twelve days early). Every bought part is on hand.

**Bins** (the builder's word at the bench, 2026-11-07): the LED chips, the wings and, for now, the spare steel disc are all in the **satellite bin**.

## Orders placed

| Order | Date | Contents |
| --- | --- | --- |
| IMR Batteries 20739060 (with 20739061 the same night) | 2026-10-16 | 7 × [Nitecore NL169](https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery) 16340 950 mAh protected button top, $69.65 (one for the satellite); 12 × IMREN 18350 800 mAh button top, $48.00 after the per-item deal, **held stock, not for this build** (unprotected, and 18.2 mm thick). **Correction 2026-11-03:** this row first said "ordered 2026-11-03, order number not seen"; the summary pasted into the session was this October order. Both IMR boxes reached the front desk 2026-10-21 (building log and IMR's delivered mails). With order 20739061 (6 × NL169, $59.70) the family owns 13 cells. |
| Amazon 111-9152603-4910637 | 2026-11-03 | 1 × [pre-wired warm-white LED chips](https://www.amazon.com/dp/B09QGJ9LY7), DiCUNO 20-pack, 0805, $7.99; $8.70 with tax, **delivered 2026-11-04, picked up 2026-11-05**. The [Gikfun 56 mm panels](https://www.amazon.com/dp/B0GWQJHSY9) ordered with it ($18.99, $29.38 for the order) were cancelled off it after the wing change: the order page showed the chips alone on 2026-11-03 night. |
| Amazon 111-1980686-5970641 | 2026-11-03 | 1 × [mini solar panels](https://www.amazon.com/dp/B0FL26KWWT), MECCANIXITY 5-pack, 80 × 45 mm poly 5 V 0.45 W 90 mA with 150 mm leads (style "5V 0.45W 90mA"), $12.29; $13.38 with tax, **delivered 2026-11-05 (two days early), picked up 2026-11-05**. The wings. Read from the order page in the app's browser pane 2026-11-03 night, after the builder said it was bought. |
| Amazon 114-9697223-4179439 | 2026-11-03 | 1 × [mini solar panels, 6 V 1 W](https://www.amazon.com/dp/B08THXDWS1), Eujgoov 3-pack, 110 × 60 mm poly with 30 cm leads (sold by Perfurt), $16.48; $17.94 with tax. **Cancelled**: the Orders page read 2026-11-03 06:17 EST says cancelled and not charged (it had shown arriving 11-07 the night before). Nothing arrives; no fallback wing is on hand. |
| Amazon 111-4967394-9172244 | 2026-11-03 | 1 × [stainless disc](https://www.amazon.com/dp/B08JD6GY21), Harness Machine & Fab, 3 in × 1/8 in 304, $9.87; $10.75 with tax, **delivered 2026-11-06 (twelve days early, UPS from the maker), picked up 2026-11-06**. |

## Electronics

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **[Nitecore 16340 cell](https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery)**, NL169, 950 mAh, protected, button top, 7 + 6 bought 2026-10-16, on hand since 2026-10-21 | 1 of 13 | The battery, chosen by the builder on 2026-11-03 over the 500 mAh pouch the sheet was approved with. 16.6 × 34.1 mm, 20 g, 3.42 Wh, 4.20 V termination, 2 A limit. Lies in the owned holder along the front wall of the bus; swaps without a tool. **Incoming check:** 3.6 to 4.1 V on the meter, button top +; nothing else. Never solder to it. |
| **[Mini solar panels](https://www.amazon.com/dp/B0FL26KWWT)**, MECCANIXITY, 80 × 45 mm poly 5 V 0.45 W 90 mA with 150 mm leads, five-pack, ordered 2026-11-03, on hand since 2026-11-05 | 2 of 5 | The wings, one on each boom, the two in series into the charger's VIN pad; three spare. **Incoming check:** each panel open circuit on the meter at the window, about 6 V in sun and 3 to 4 V at a bright window; note which lead the meter calls + and mark it, then the pair in series reads double. Nothing is soldered on a panel: its leads join the box wires in heat-shrink. **In the satellite bin** (sorted 2026-11-07). |
| **[Mini solar panels, 6 V 1 W](https://www.amazon.com/dp/B08THXDWS1)**, Eujgoov, 110 × 60 mm poly with 30 cm leads, three-pack, order cancelled | 0 | **Not coming.** The order was cancelled (Orders page 2026-11-03); none are on hand, so the fallback wing would have to be bought again if the window proves thin (166 mA at full sun, 1.85× the current, 284 mm of span). |
| **[Pre-wired warm-white LED chips](https://www.amazon.com/dp/B09QGJ9LY7)**, DiCUNO, 0805 with 16 cm enamelled leads, twenty-pack, ordered 2026-11-03, on hand since 2026-11-05 | 20 | The beacon, glued flat on the bus's top front corner; nineteen spare. **Incoming check:** light one through its 100 Ω resistor from 3.3 V before gluing and judge the colour against a 2700 K bulb (the listing says only "warm white"); if it looks faint, the kit's 68 Ω. **In the satellite bin** (sorted 2026-11-07); the Mars rover's Rev H borrows one of the spares. |
| **[Stainless disc](https://www.amazon.com/dp/B08JD6GY21)**, Harness Machine & Fab, 3 in × 1/8 in 304, ordered 2026-11-03, on hand since 2026-11-06 | 0 of 1 | **Spare since 2026-11-06.** It was the base (115 g); on the bench the steel read too white, so the builder chose a solid brass coaster instead (Still to order). **In the satellite bin for now** (the builder's word, 2026-11-07). |

## Still to order

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **[Brass coaster](https://www.amazon.com/dp/B0D9DMK3L7)**, 75 × 8 mm, flat top, hollow underneath with a non-slip pad, 80 g (2.82 oz, the listing), one piece; chosen 2026-11-06 and **ordered the same day** (Amazon 114-8443990-0476239, $12.99, $14.14 with tax, sold by TOGGOOL; the Orders page said *arriving today* on 2026-11-09; recorded 2026-11-09 from the order history, which this file had missed). **Given to the desk lighthouse on 2026-11-09 at the builder's word: the satellite buys its own coaster again when it is built.** | 0 (to buy again) | The base, replacing the steel disc: brass matches the family and the amber pool. Too light alone (it would tip at about 25°) and too thin on top to drill, so the printed hub is glued on top and about 150 g of steel is epoxied into the hollow before the pad goes back: about 230 g, tipping at about 39°. **Incoming check:** measure the hollow's inside diameter and depth, which pick the steel (stacked fender washers if round and flat, steel BBs in epoxy if not, bought then); a magnet must not stick to the top. Clear lacquer or wax to keep it bright. |

The box, lid and hub are printed from the shelf's black PETG once the real holder, boards and cell have been set
in the envelope.
