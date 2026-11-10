# Desk satellite

A small satellite on a post. Two 80 × 45 mm solar panels are its wings, a matte black printed box is
its body, a tiny warm-white LED chip is glued on its top front corner with no legs showing (on, or
one blink every two seconds), and under the body the desk hologram's amber LED filament glows down
the post onto a brass base. Inside the box the owned bq25185 charger board tops up a Nitecore 16340
cell in its holder from the wings, with a USB-C port through the back as the fallback, and an
ESP32-C3 SuperMini sleeps between blinks. One 1.5 mm stainless post carries it over a weighted brass base, 75 × 8 mm.
Started 2026-11-02; revised three times the same morning at the builder's word (the light moved
from a mast to the corner, became a legless chip, and the amber pool was added).
**Approved as drawn 2026-11-03 and step 2 delivered the same day; revised that afternoon at the builder's word for the Nitecore 16340 cell and that evening for 80 × 45 mm rectangular wings, confirmed by the builder that night; all three Amazon lines ordered, and all three picked up by 2026-11-06 (the disc twelve days early). On 2026-11-06 the builder swapped the steel disc (too white) for a brass coaster, 75 × 8 mm; at 80 g it is hollow under a thin top, so the printed hub stays and about 150 g of steel goes into the hollow (about 230 g, tipping at 39°). It is still to buy. Nothing printed, cut or soldered.**

The reference is Huy Vector's [Desk Satellite](https://www.huyvector.org/clocks/desk-satellite):
a copper-wire cube with an ESP32-C3 clock and a 0.96-inch screen inside, two solar wings, a dish, a
charging module plus a separate solar controller, on a brass tube over a bamboo coaster. Ours keeps
only the idea (a body on one post over a round base, two solar wings) and is its own build
otherwise, for the builder's brief of 2026-11-02: mini solar panels, a cell they keep topped up, USB
as the fallback, a small 3000 K light at the tip that is on or blinks, a warm light below.

## Where it stands: approved; step 2 delivered

The builder's rule for every new project: the final build first, the science after. Step 1 (the
form sheet, the wiring sheet, every part and every pin) was approved as drawn on 2026-11-03.
Step 2, the science and engineering page, is published the same day. That afternoon the builder
chose a Nitecore 16340 cell they had bought over the 500 mAh pouch, and both pages, the record and
this file were revised for it (decision 4: the owned holder along the front wall, the bus grown to
48 × 52 × 24 mm, both USB-C ports through the lid). The three Amazon lines were ordered that evening, $40.13 with tax in two orders (panels and chips
arriving 2026-11-04, the disc 2026-11-18), logged in [`docs/INVENTORY.md`](docs/INVENTORY.md) and
`DIY/PACKAGE_TRACKER.md`. Next: the box envelope bench-checked against the real holder, boards and
cell, then printed, then the firmware. Also that evening the panels' light figures were corrected:
the listing's 90 mA is a full-sun number (its 38 000 lux was a halogen lamp), so a bright window about
covers the beacon mode and the glow wants direct sun or the cable; the pages and the record carry the
corrected table. Then the wings changed at the builder's word to a rectangle a little smaller than the
reference's panel: the 80 × 45 mm MECCANIXITY poly panel with 150 mm leads, the same 90 mA, nothing
soldered on the panel, 224 mm wing tip to wing tip. Ordered 2026-11-03, arriving 2026-11-07; the Gikfun squares were cancelled off the chip order, and the
Eujgoov 3-pack ordered the same night was cancelled as well, so no fallback wing is on hand.

| File | What it is |
| --- | --- |
| [`docs/FINAL_BUILD.md`](docs/FINAL_BUILD.md) | The record: the reference, the twelve decisions (including where this build leaves the reference), dimensions, the pin map, every wire and why, the energy budget by mode, parts (three to buy, three to print, the rest owned), the firmware outline, the three meter checks. Generated |
| [`docs/pages/desk-satellite-build.html`](docs/pages/desk-satellite-build.html) | The published page: the form sheet (front view with the amber pool, the beacon at the corner in section, side section through the bus, top view, the back with its lid, the base, key numbers, what the wings deliver) and the wiring sheet (every connection, zero crossings, the budget along the bottom), with the text of `FINAL_BUILD.md` |
| [`docs/pages/print/desk-satellite-build.pdf`](docs/pages/print/desk-satellite-build.pdf) | Letter, black only: the two landscape sheets first, then the notes in portrait. Print at Actual size. The sheets alone: `desk-satellite-form-sheet.pdf`, `desk-satellite-wiring-sheet.pdf` |
| [`docs/pages/gen/build_page.py`](docs/pages/gen/build_page.py) | The generator. Dimensions, pins, nets, the budget, parts and decisions live here; it writes the page, the Markdown and the PDFs, and refuses to draw a wiring sheet that fails the line-clearance check. Edit the script, not the outputs. `page_style.css` beside it is the house page style |
| [`docs/PHYSICS.md`](docs/PHYSICS.md) | Step 2: the science and engineering behind every number on the sheet, as text. Generated |
| [`docs/pages/desk-satellite-physics.html`](docs/pages/desk-satellite-physics.html) | The published physics page with nine figures drawn to the numbers; PDF `docs/pages/print/desk-satellite-physics.pdf` (8 Letter pages, portrait, black) |
| [`docs/pages/gen/physics_page.py`](docs/pages/gen/physics_page.py) | Its generator; takes the dimensions, budget and light levels from `build_page.py` so the two pages cannot drift, and keeps every assumption as a named number at its top. Regenerate with `python3 docs/pages/gen/physics_page.py --pdf` |
| [`docs/INVENTORY.md`](docs/INVENTORY.md) | What was bought for this build: the Nitecore cells and the two Amazon orders of 2026-11-03, with incoming checks |
| [`docs/ARTIFACTS.md`](docs/ARTIFACTS.md) | Links to the published pages |

Regenerate everything with:

```bash
python3 docs/pages/gen/build_page.py --pdf
```

```bash
python3 docs/pages/gen/physics_page.py --pdf
```

## In one paragraph

Two 80 × 45 mm polycrystalline panels, leads fitted, in series read 12 V in sun and 7 to 8 V in a
room, always above the 4.8 V the charger wants, so the charger just pulls the pair down and takes
their full current.
The charger is Cyber Dawn's spare board: USB-C or a 5 to 18 V pad through two Schottkys, a weak
input followed instead of collapsed, a fixed 6 h timer that a night resets. The cell is a Nitecore
16340, 950 mAh and protected, in the owned holder along the front wall of a 48 × 52 × 24 mm printed
box, its leads on a JST-PH pigtail into the charger's socket; the charger and the SuperMini lie side
by side behind it with both USB-C ports through the lid, and the SuperMini runs from the cell through
one diode so its own port can be plugged for flashing. The beacon is a pre-wired 0805 warm-white chip,
2 × 1.25 × 1.1 mm, glued flat on the top front corner with its two hair-thin leads dropped through a
pinhole to a 100 Ω resistor and GPIO0 inside; the pool is the hologram's 38 mm 2200 K filament taped
under the floor, on GPIO1 through 68 Ω, 12 mA flat out and dimmed by PWM. 224 mm wing tip to wing
tip, 154 mm tall, about 214 g with 115 of it in the disc; seven 30 AWG wires, two resistors, one
diode, three rods in three glued sockets and no solder on the frame, the box, the wings or the cell. Three modes
on one button: beacon (0.42 mA, 84 days on the cell in the dark, carried by the wings at a bright window),
glow (beacon plus the pool dimmed, 3.4 mA, 10 days, for evenings and sunny sills), lamp (pool flat
out, 13.4 mA, two and a half days, plug in for it). On a desk under room light the wings store
nothing, because the charger itself eats 0.75 mA of input, and a dull window little more. The chips, the wings and the disc were all ordered 2026-11-03 and picked up 2026-11-05, 11-05 and 11-06.

## Rules this build follows

- Component names with the link on the word; no product codes in prose.
- Owned parts stay off the shopping list (the two inventories were read 2026-11-02: the charger and
  the holder are Cyber Dawn's, the cell is the builder's Nitecore stock, the controller and the pigtail
  are Pocket AI stock, the diode and the rods are drone stock, the filament is the hologram's spare).
- Every wire on the sheet is traceable pin to pin; crossings hop; the generator checks clearance.
- Stainless rod for the frame (brass is the Pocket AIs' and Cyber Dawn's); a printed black body,
  like Cyber Dawn's, because a satellite bus is a box; the brass tone appears only as light.
- Few lines: one post and two booms, nothing standing up from the body. Wires under the wings
  and inside the box; the lights are a chip on the corner and a filament underneath.
- A reference, not a copy: the silhouette is Huy Vector's, everything else is this build's.
- Meter only what matters: three checks before power, nothing else.
