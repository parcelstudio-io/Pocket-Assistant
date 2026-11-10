# Pocket AI Sphere

The third Pocket AI: the same assistant as [`pocket_ai_assistant`](../pocket_ai_assistant/)
(screen, microphone, amplifier and speaker, one button, Wi-Fi to the local server), plus the
camera of [`pocket_ai_assistant_with_camera`](../pocket_ai_assistant_with_camera/) and a
weather sensor, inside a 70 mm sphere of three brass rings. Concept of 2026-10-29, simplified the same day from a geodesic to three rings at the builder's request. **Rev B approved as drawn 2026-11-10** (the first wiring sheet, the colour audit, four Rev A mistakes fixed), then superseded the same day: the builder asked for a head that looks where the camera looks and follows you. **Rev C, drawn and approved as drawn 2026-11-10:** the whole sphere nods and turns on a brass fork (the tilt servo set into the vertical ring as the right hinge, a pan servo on a brass coaster), the owned 1.54" colour screen as the face with the camera board behind it, a top ring instead of the equator, the family's charger-boost for the servos' 5 V. The motion was shown and approved first (`docs/pages/sphere-motion.html`). **Nothing bent, soldered or flashed; the XIAO is in the mail (pair expected by 11-15); three lines to buy (two servos, a charger-boost, a coaster, about $60 landed; see `docs/ORDER.md`).**

| File | What it is |
| --- | --- |
| [`docs/DESIGN.md`](docs/DESIGN.md) | The record: geometry, what changed from Rev A, the colour audit, parts (all owned but the XIAO), pin map, every net and why, power and charge, ring cut list, the eight bench tests, build order, mass, risks. Generated |
| [`docs/pages/sphere.html`](docs/pages/sphere.html) | The published page: the sphere on its fork in three-quarter, front, right and back views, and the wiring sheet |
| [`docs/pages/gen/sphere.py`](docs/pages/gen/sphere.py) | The generator. Geometry, parts, pins, nets, the sheet and the tests live here; it writes the page and `DESIGN.md`. Edit the script, not the outputs. Rev A and Rev B are kept beside it as `sphere_revA.py.bak` and `sphere_revB.py.bak` (pages: `../sphere_revA.html.bak`, `../sphere_revB.html.bak`) |
| [`docs/pages/sphere-motion.html`](docs/pages/sphere-motion.html) | The motion study asked for before Rev C (2026-11-10): the sphere on its fork in 3D, eyes first then the sphere, drag or play the demo; `sphere-motion.gif` is the demo as a GIF |
| [`docs/ORDER.md`](docs/ORDER.md) | The order for Rev C: the coaster in the Amazon cart (2026-11-10), the two servos and the charger-boost as DigiKey lines; nothing paid |
| [`docs/ARTIFACTS.md`](docs/ARTIFACTS.md) | Links to the published pages |

Regenerate with `python3 docs/pages/gen/sphere.py`.

## In one paragraph

A 70 mm sphere of three brass rings on a brass fork over a brass coaster, 105 mm tall. The
vertical ring's right pole is a sub-micro servo: the fork holds its horn, so it nods the whole
sphere; a second servo on the coaster turns the fork. The owned 1.54 inch colour screen fills the
open front on two thin posts, the camera board behind it with the lens over the top edge, so the
eyes and the camera look the same way by construction: the pupils follow you across the glass,
and past 18 degrees the sphere turns. The cell lies on the floor as ballast with the speaker on
it; the charger-boost behind the tray makes 5 V for the servos and charges the cell in 2.2 hours;
the sensor hangs under the top ring. The blue amplifier and toggle body stand behind the screen,
out of sight. About 73 g of sphere, 2.7 hours following, three lines to buy.

## Rules carried over

The cell is the only source and nothing feeds the XIAO's `5V` pin; the amp is off until firmware
raises `SD`, volume cap 65, `GAIN` open; neither speaker lead is ground; the brass is not a
conductor; never solder to the cell. Say "untested" until it has run.
