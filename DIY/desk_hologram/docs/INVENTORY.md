# Purchased inventory — Desk hologram

Factual purchase record: what was *bought*, not what is approved; part authority stays in
[`FINAL_BUILD.md`](FINAL_BUILD.md). Everything owned from the other builds (the display, the controller,
the microphone, the button, resistors, capacitors, wire, tape, heat-shrink, the stainless rod, the adapter)
is in `../../pocket_ai_assistant/docs/INVENTORY.md` and `../../cyber_clock_v2/docs/INVENTORY.md` and is not
repeated here.

**Status check 2026-11-03, 06:17 EST** (Amazon Orders page; the per-project list is `../../PARTS_BY_PROJECT.md`): the cube is arriving Sunday 11-08; the filament pack was delivered 11-03 at 12:53 in the box with Crumb's gears (Amazon mail; building log). The display kit's Adafruit box (order 3765988) reached the front desk 2026-10-21 per the building log; the controller, microphone and the stainless coupon are on hand.

## Orders placed

| Order | Date | Contents |
| --- | --- | --- |
| Amazon 114-6341362-5527437 | 2026-11-01 | 1 × [beam-splitter cube](https://www.amazon.com/dp/B0B34D4H18), 50 mm, 50:50, K9 glass (NYJLGD; the 50 mm size is child listing B0B34FV475), $74.99, $81.65 with tax, free delivery, **arriving Sun 2026-11-08**; it was one of two in stock. Read from the Amazon Orders page 2026-11-01 evening. |
| Amazon 114-0670386-1613054 | 2026-11-01 | 1 × [LED filament ten-pack](https://www.amazon.com/dp/B0FR35BGYL), 3 V, 38 mm, 2200 K amber (QIROGKC; size 38MM, colour 2200k), $9.99, $10.88 with tax, **delivered and picked up 2026-11-03** (the cart had said Nov 2). Amazon split the one checkout into two orders. |

## Electronics and optics

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **[Beam-splitter cube](https://www.amazon.com/dp/B0B34D4H18)**, 50 mm, 50:50, ordered 2026-11-01 | 1 | The hologram: half the display's light turns 90° at the diagonal inside the glass and the text stands upright at the back face. 314 g. **Incoming check:** no chips on the edges, the diagonal visible as a faint plane; set it on the display, turn it until the text faces you. Keep it in its wrap until the legs are on; glass on glass scratches. |
| **[LED filament](https://www.amazon.com/dp/B0FR35BGYL)**, 3 V, 38 mm, 2200 K, ten-pack, ordered 2026-11-01 | 10 | The dim amber pool under the front edge and the status light, on GPIO0 through 68 Ω. One used, nine spare. **Incoming check:** both leads at one end, the + mark legible; the ceramic strip is brittle, so bend the leads, never the strip. Never connect it without the resistor. |

## Still to order (Rev B, 2026-11-07)

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **[Brass sheet](https://www.amazon.com/dp/B0006N6WLM)**, K&S 250, 0.005 in (0.13 mm), 4 × 10 in, 6-pack, about $3 a sheet; the Mars rover's list carries the same line, so one order serves both | 1 of 6 | The skin: a bare brass frame round the glass on top, an ivory skirt (the owned Rust-Oleum canvas white) down the four edges, Kapton inside. One pattern takes 104 × 75 mm of a sheet, along its length. **Incoming check:** flat, no creases; it cuts with scissors. |
| **[Gel super glue](https://www.zoro.com/loctite-ultra-gel-super-glue-4g-1363589/i/G100464525)**, Loctite Ultra Gel Control, 4 g; the one in the Amazon Saved for later, or Zoro; the rover's list carries the same tube | 1 | The legs in their holes and the button on the module's top. No glue but the hot-glue gun is owned (2026-11-07); the Rev A page's "CA, owned bench stock" was wrong. **Incoming check:** none. |

Everything else for Rev B is owned: the canvas-white spray, the sandpaper, the cardstock for the pattern, Kapton, a white button cap. The display module's 72 × 43 mm outline, hole and glass positions are still the Cyber Dawn record: caliper the spare and put the numbers into `pages/gen/build_page.py` before cutting the legs or the brass (build day, step 0).
