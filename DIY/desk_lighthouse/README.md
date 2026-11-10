# Desk lighthouse

A lighthouse for the desk drawn in wire, 243 mm tall, on a cell, and nothing else. Four 1.5 mm brass rods rise from
the same 75 × 8 mm brass coaster the satellite stands on, Ø54 at their feet and Ø29 where they pass the gallery, then
straight up as the lantern's bars to the roof, which three of them carry. Up the middle the owned 4 mm brass tube, the
spine, turns slowly from an N20 gearmotor standing at the foot. The lantern is open: a brass gallery (a lamp-maker's
1-1/2 in turned check ring) below, a brass roof (a 1-1/2 in spun vase cap) above with a 5/8 in brass ball for the
ventilator, and air between. In it a 26 mm warm-white LED filament stands still on the axis on a 1 mm brass lamp post,
and a brass shutter cut from a 5/8 in tube turns round it on the spine: one revolution in 7.5 s, a 2.5 s sweep of
light across the room, then brass. A reed switch and a magnet on a thin brass arm at the foot tell the firmware where
the window is, so rotation off parks it facing you and lamp off closes it. At the foot the motor stands on the axis,
the family's Nitecore 16340 stands in the owned black tray behind it, and the reed between them, all in the open. The
family's bq25185 charger board, the owned ESP32-C3 SuperMini and the owned MX1508 driver lie in the coaster's hollow,
both USB-C ports in a notch at the back: plug in there to charge (or to flash). The one button hides inside the rim at
the front; press the coaster. About 7 hours of beacon on a charge, 2.3 to fill. The lamp's current goes up one rod and
comes down another. No screen, no glass, no house, no paint. Started 2026-11-07.
**Rev C was approved by the builder on 2026-11-09 as drawn and step 2, the physics page, delivered the same day; the
Amazon order went in that morning (eight lines in five orders, $122.64). That evening the builder rejected the acrylic
glass ("so ugly, never"), cancelled the brass sheet and refused any plastic house ("just use the wire frame as a
lighthouse, nothing else"), so Rev D, the open wire frame with no glass and no house, was drawn the same evening and
awaits approval. The Grand Brass lamp parts are ordered by the builder's word; the charger is still to buy. Nothing cut
or soldered.**

Rev A (2026-11-07) was an ivory 25 mm brass tube on a 38 mm brass cube with a text screen in its front. Rev B
(2026-11-08) made the tower a wire frame, with the screen in a small ivory door, after the builder asked for
"wired frame rather than huge brass tube". Rev C (2026-11-09) dropped the screen at the builder's word (no OLED
comes in ivory or grey) and put the build on a cell with a charger below, the power drawn on both sheets as asked, with
an acrylic lantern glass and a brass-sheet keeper's house. Rev D (2026-11-09 evening) removes the glass and the house
and makes the shutter's floor, the magnet's collar and the deck's bushing from 1 mm rod and tube rings instead of
sheet; the button moves from the house's roof into the coaster's rim. The earlier generators are kept beside the
current one as `build_page_revA.py.bak`, `build_page_revB.py.bak` and `build_page_revC.py.bak`.

The reference is Huy Vector's [Lighthouse Desk Lamp](https://www.huyvector.org/decor-lamps/lighthouse-desk-lamp):
the page is a parts list and no more (0.2 mm brass sheet, 4 mm brass tube, copper wire, a 3 V 30 rpm gear motor, a
39 mm Edison filament, a glass fuse, a Type-C charging module, a battery, a bamboo coaster). Ours keeps the idea, a
small brass lighthouse on a coaster with a motor, a filament and a cell, and is its own build otherwise. Brass at
the builder's word for this build; the family's rule since the drone is stainless.

## Where it stands: Rev D drawn, awaiting approval; parts ordered

The builder's rule for every new project: the final build first, the science after. Step 1 was approved as drawn on
2026-11-09 as Rev C. Step 2, [Desk Lighthouse Physics](https://claude.ai/artifact/Cf7FTWNsZAdGYGXpTCj535), was written
the same day: why the lamp stands still and the brass turns (the light's character, Fl W 7.5s), how much light leaves
the window (19 lumens, two full moons on a wall 2 m away), the filament behind a resistor and why the rail is a
regulated 5 V (84 mA flat against 134 or 46 straight from the cell), a gearmotor at a third of its voltage (the
brushes' dead band, the reed loop, the ramp into the boost), the boost and the budget from the cell (the lamp is 69 %
of it), one diode and the rail as the cell empties, charging through the coaster (650 mW, a coaster 6 °C warmer), why
the rods lean (47 times as stiff as four vertical rods), the coaster as the fuse, a magnet and a reed (68 mT at the
tip, a one-second pulse, one edge), the spine and its bearing. Nine figures drawn to the numbers; every assumption a
named number at the top of its generator.

That evening the builder saw the parts and ruled: no clear acrylic tube, ever; no brass sheet folded round components;
no plastic house. Rev D redraws all three sheets accordingly: the lantern is open and three rods carry the roof,
soldered through its dome; the foot is bare, with the motor, the cell's tray, the reed and a 1 mm magnet arm standing
on the coaster; the shutter's floor is two 1 mm bars, the deck's bearing a wheel of two tube rings and two spokes made
on the spine itself; the button sits inside the rim at the front. The physics page was revised with it. 217 g instead
of 250, the same hours. **Rev D awaits the builder's yes.**

Three sizes are drawn at their usual value and must be measured when the parts come: the check ring's thickness
(3 mm), the vase cap's height (12.5 mm) and the coaster's hollow (about 6.7 mm deep under a 1.3 mm top, read from
its listed 80 g; the coaster arrived 2026-11-09); the rods' tips, the cap's three holes and whether the boards and the
button fit the hollow follow from them, and the script recomputes them.

Ordered 2026-11-09: the eight Amazon lines (one checkout, five orders, $122.64; the motors, magnets, reeds and acrylic
shipped the same day for Wed 11-11, the glue comes 11-14, the sheet and the tube 11-18 to 11-20, the filaments 11-27).
Two of them were dropped that evening: the brass sheet, which the builder cancelled, and the acrylic tube, which had
shipped and goes back when it comes. The five lamp parts from Grand Brass (check ring, vase cap, ball, nipple, nut,
about $7 in all) are ordered at the builder's word, with no confirmation mail yet. Still to buy: one bq25185 charger
board (Adafruit 6106, $8.95, or DigiKey 1528-6106-ND); the DigiKey order of that morning holds the rover's six lines,
not this one. Rev D needs nothing else: the bars, the spokes and the arm come from the owned 1 mm rod, the bearing's
rings from the owned tube set and the 5/8 in tube on order. Then the measurements and a rerun, then the firmware
(ESP-IDF, no Wi-Fi) once the bench has proven the motor, the reed and the lamp.

| File | What it is |
| --- | --- |
| [`docs/FINAL_BUILD.md`](docs/FINAL_BUILD.md) | The record: the reference, seventeen decisions, dimensions and masses, the pin map, every wire and why (the power chain first), the budget from the cell, the parts (what is ordered, what is dropped, what is owned), the firmware outline, the three meter checks, the status. Generated |
| [`docs/pages/desk-lighthouse-build.html`](docs/pages/desk-lighthouse-build.html) | The published build page: the form sheet (front view, the open lantern in section with the lamp on its post and the shutter on its bars, the foot from above, the plan with the roof off, a section through the foot and the coaster, how it behaves, key numbers), the wiring sheet, the templates, with the text of `FINAL_BUILD.md` |
| [`docs/pages/print/desk-lighthouse-build.pdf`](docs/pages/print/desk-lighthouse-build.pdf) | Letter, black only: the three landscape sheets, then the notes in portrait. Print at Actual size; the templates' 50 mm bar must measure 50 mm. The sheets alone: `desk-lighthouse-form-sheet.pdf`, `desk-lighthouse-wiring-sheet.pdf`, `desk-lighthouse-templates.pdf` |
| [`docs/pages/gen/build_page.py`](docs/pages/gen/build_page.py) | The build generator. Dimensions, pins, nets, the budget, parts and decisions live here; it writes the page, the Markdown and the PDFs, asserts the clearances (shutter inside the rods, post in the shutter, three rods through the roof and the live one under it, the arm clear of the tray, the wheel over the deck's hole, boards in the hollow and their ports in the notch, the button in the rim, the boost under its switch-on limit), and refuses to draw a wiring sheet that fails the line-clearance check. Edit the script, not the outputs. `page_style.css` beside it is the house page style |
| [`docs/PHYSICS.md`](docs/PHYSICS.md) | Step 2: the science and engineering behind every number on the sheet, as text. Generated |
| [`docs/pages/desk-lighthouse-physics.html`](docs/pages/desk-lighthouse-physics.html) | The published physics page with nine figures drawn to the numbers; PDF `docs/pages/print/desk-lighthouse-physics.pdf` (Letter, portrait, black, figures at 70 % width) |
| [`docs/pages/gen/physics_page.py`](docs/pages/gen/physics_page.py) | Its generator; takes the dimensions, masses and budget from `build_page.py` so the two pages cannot drift, and keeps every assumption as a named number at its top. `--png <dir>` renders the figures for checking by eye |
| [`docs/INVENTORY.md`](docs/INVENTORY.md) | What is owned, what was ordered on 2026-11-09 (the eight Amazon lines, order by order, two of them since dropped; the Grand Brass parts at the builder's word) and what is still to buy (the charger) |
| [`docs/ARTIFACTS.md`](docs/ARTIFACTS.md) | Links to the two published pages |

Regenerate everything with:

```bash
python3 docs/pages/gen/build_page.py --pdf
```

```bash
python3 docs/pages/gen/physics_page.py --pdf
```

## In one paragraph

Four rods and a spine; no closed surface at all. The rods are owned K&S 1.5 mm brass, cut 223 each, bent to a 6 mm
foot under the coaster's top and nudged 4.3° to vertical just under the deck, which is threaded down them to 168 mm and
glued; three of them pass through the roof's dome at r 14.5 and are soldered flush from outside, and the live one is
trimmed to end under the dome in a white boot. The spine is one 148 mm piece of the owned 4 mm tube, a slip fit over
the motor's D shaft with a drop of gel glue, running up through a wheel on the deck (a 3 mm ring of the 5/8 in tube as
the rim, two 1 mm spokes, a 3 mm ring of the owned 5 mm tube as the hub, soldered up on the spine itself so it centres)
and soldered to the shutter's two 1 mm bars. Power: the Nitecore 16340 in its tray, standing behind the motor in the
open, feeds the bq25185 charger's battery pads; the controller runs from the cell through an SS14 (the satellite's
wiring), the motor and the lamp from the board's 5 V boost, which GPIO7 switches off when nothing moves; two 100 kΩ
bring the cell's voltage to GPIO4; the charger's USB-C in the coaster's notch charges at 500 mA (jumper cut) and its
power path runs the lighthouse from the cable meanwhile. The lamp is a 3 V, 100 mA filament at 2700 K fed from the
5 V rail through two 47 Ω in parallel, 83 mA flat out, dimmed by PWM; the current climbs the back-left rod (white
heat-shrink at the coaster and the deck, a boot at the tip), a wire takes it to the + tab under the roof, and it
returns down the 1 mm lamp post, the nut, a wire and the back-right rod. The owned MX1508 drives both: channel A the
motor, channel B the lamp as a high-side switch. A 6.5 mm arm of 1 mm rod on the spine carries the index magnet over
a reed standing between the motor and the cell; the button hides inside the rim at the front. 129 mA from the cell
with the beacon turning: about 7 h; 112 mA with the lamp alone: 8 h; 20 mA asleep. 217 g before the ballast, centre
of mass 81 mm up, tipping at 25°; with about 80 g of steel washers in the hollow, 60 mm and 32°. The lantern's 67 g
sit on four rods with a buckling margin of about 211 to one, and the cage sways about 0.08 mm at the deck per newton.

## Rules this build follows

- Design first: sleek, few lines (four rods and a spine); no closed surface; wires in the hollow, two of them the rods themselves; black only in the pad, the cell's wrap and its tray, in the open at the foot as the rule allows.
- No clear acrylic and no folded brass sheet, at the builder's word of 2026-11-09 evening; no plastic house.
- Power drawn on both sheets: the cell stands where the form sheet shows it; the wiring sheet reads cell, charger, controller, driver, loads.
- Colour: brass and warm white; the filament's yellow phosphor hidden by the shutter when off; white heat-shrink where a sleeve shows.
- Component names with the link on the word; no product codes in prose.
- Owned parts stay off the shopping list (the cell, the tray, the diode, the resistors, the controller, the driver, the rods, the tubes, the wire).
- Every wire on the sheet is traceable pin to pin; crossings hop; the generator checks clearance.
- Meter only what matters: three checks before power, one of them the live rod against every other piece of brass, one the tray's polarity before the cell meets anything.
- The final build first, the science after: step 2 was written once step 1 was approved, and revised when the sheet changed.
