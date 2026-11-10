# Desk Robot (working name: Crumb)

A small desk-roaming robot with our own spin on the Mo-chan idea from
[Huy Vector](https://www.huyvector.org/robots-kinetic/diy-cute-desk-robot-mo-chan):
a square 1.0 mm brass-rod case with a flat face, a 1.54" colour IPS screen as the face, a
brow above it with the camera lens and two laser rangers so it never drives off the desk, a
speaker and amplifier, a microphone, a swappable protected 16340 cell, and two Ø40 mm steel
64-tooth spur gears as wheels, the way Mo-chan rides. Concept of 2026-10-31, drawn nine times the same evening; the record of every
turn is at the bottom of `docs/DESIGN.md`. **Paper only: nothing bought,
bent, soldered or flashed.**

## Round two, 2026-11-07: three prototypes, Mochi picked, step one approved, step two written

The builder asked on 2026-11-07 for a brass-and-ivory version with ivory wheels, a camera, a **spinning lidar**, a speaker and a
microphone, cute and compact, with a frame of its own, and three prototype drawings first. The page
[Desk Robot Prototypes](https://claude.ai/artifact/4xh1qfA6EVgNc7ereipQMV) shows **Mochi** (an ivory card loaf on brass hoops wearing the
lidar as a hat, a round colour face, Ø31 ivory wheels, 72 × 56 × 94 mm), **Lantern** (a puck and a head with the lidar's rotor turning in
the open band between them, the owned square screen, Ø40 wheels, 72 × 56 × 106) and **Wheelie** (two Ø60 ivory wheels, a slim capsule,
two OLED eyes, the lidar low in a front slot, 74 × 76 × 100). All three keep Crumb's parts; the steel gears and the 8×8 ranger go back to
the shared bin. New in every one: an LDROBOT STL-19P lidar (Waveshare D500 kit), a pair of Pololu white wheels, an Adafruit bq25185
charger-boost for a 5 V rail, a P-MOSFET for the lidar's power switch. Record: [`docs/CONCEPTS.md`](docs/CONCEPTS.md). **The builder picked Mochi the same day.** Step one for Mochi is drawn and published as
[Mochi Build](https://claude.ai/artifact/SgXkkSjfQp7PcpkcBK1fbz) (record [`docs/MOCHI_BUILD.md`](docs/MOCHI_BUILD.md), generator `docs/pages/gen/mochi_build.py`): final views, the inside packing,
the hoop template and card patterns, the pin-to-pin wiring sheet, budget, parts and checks. 73 × 56 × 93 mm, about 180 g. **Approved as drawn 2026-11-07; nothing
new bought, nothing built.** The same evening the builder asked for a metal gear instead of the white wheels: **Rev B**, Crumb's two 64-tooth steel gears as the wheels on brass-tube hubs with ivory card faces (axle 20.5 up and 1 mm forward, 77 wide, about 239 g, four lines to buy), is drawn on the same page for approval with Rev A beside it; the physics page and the printed templates stay at Rev A until the yes (`--wheel white|gear` switches both generators; `docs/pages/print/mochi-templates-gear.pdf` is Rev B's set). Step two, the science behind it, is [Mochi Physics](https://claude.ai/artifact/2sYByXsGu89mthGFxwCP2q) (record [`docs/PHYSICS.md`](docs/PHYSICS.md));
the order is [`docs/MOCHI_ORDER.md`](docs/MOCHI_ORDER.md) and the 1:1 templates are [`docs/pages/print/mochi-templates.pdf`](docs/pages/print/mochi-templates.pdf). **Late 2026-11-07 the builder set Mochi aside** ("scrap the brass ivory desk robot build"; cardstock is "very ugly") and returned to **Crumb**, whose parts are all in the bin, asking for Crumb to gain Mochi's lidar with nothing in card. Crumb Rev B is drawn, published and **approved as drawn on 2026-11-08** as [Crumb Build](https://claude.ai/artifact/9JgL9nhoR6VCnrrbQXEGiC) (generator `docs/pages/gen/crumb_build.py`, record [`docs/CRUMB_BUILD.md`](docs/CRUMB_BUILD.md), order [`docs/CRUMB_ORDER.md`](docs/CRUMB_ORDER.md): four lines, the LD19 lidar kit, the charger-boost, a P-MOSFET and a brass sheet, the charger-boost ordered from DigiKey on 2026-11-08 (sales order 102777448), the lidar kit and the MOSFET pack ordered the same day (Amazon order 114-7956116-1377847, arriving 11-09); the brass sheet for the skins skipped, so the first build runs with bare boards; nothing left to buy): Crumb's open brass cage, gear wheels and square screen with Mochi's electrical design (lidar on the cage top, charger-boost 5 V rail, lidar switch, pin map), off-palette boards skinned in ivory brass sheet. **Rev C, drawn and approved as drawn 2026-11-09, on the same page:** the builder found the lidar too big and asked for it off both desk robots so they stay small and cute; Rev C drops the lidar, its posts on the top rails, its switch and its serial line (72 × 56 × 60 mm, about 182 g, nothing to buy). The lidar kit and the P-MOSFET pack go to the shared bin, unallocated; the charger-boost stays Crumb's, its 5 V rail now for the XIAO and the amplifier only. The Mochi pages stay as the record of round two. The square-cage design below is Crumb, round one, kept as written.

| File | What it is |
| --- | --- |
| [`docs/CRUMB_BUILD.md`](docs/CRUMB_BUILD.md) | **The build: Crumb Rev C, approved 2026-11-09 (Rev B approved 2026-11-08).** Every part placed, the changes from Crumb, rods, skins, the pin map and nets, the budget, parts owned and to buy, checks, build order, risks; since 2026-11-10 the edge worked through against the wheels, pushing small things and the drive loop's four rules. Written by `docs/pages/gen/crumb_build.py` |
| [`docs/CRUMB_ORDER.md`](docs/CRUMB_ORDER.md) | The four lines to buy for Rev B with the exact listings, what is not bought and why, the caliper checks before and after, and the ownership check of 2026-11-08 (everything else on hand, the XIAO by 11-11); the purchase check of 2026-11-09; since 2026-11-10 one 8×8 ranger to buy just in case, with its links |
| [`docs/COMPUTE.md`](docs/COMPUTE.md) | Where the computing happens (2026-11-09, brought to Rev C the same day): the XIAO ESP32-S3 Sense owns motion, the edge stop and the face; speech and camera frames go over Wi-Fi to the pocket server; data rates; what the server still lacks for Crumb (an image path, a model that can see) |
| [`docs/PHYSICS.md`](docs/PHYSICS.md) | Step two (2026-11-07): the physics and engineering behind every decision on the approved sheet, with the numbers derived from the build generator |
| [`docs/MOCHI_ORDER.md`](docs/MOCHI_ORDER.md) | The lines to buy after the approval (four with Rev B's gears, five with Rev A's wheels), the exact listings, the vendor order, the gear caliper check and the arrival checks |
| [`docs/pages/print/mochi-templates.pdf`](docs/pages/print/mochi-templates.pdf) | The 1:1 paper templates on Letter, black only: the hoop profile and side disc, the card wrap; made by `docs/pages/gen/mochi_templates.py`. `mochi-templates-gear.pdf` beside it is the Rev B set (hub hole and cradle marks moved) |
| [`docs/MOCHI_BUILD.md`](docs/MOCHI_BUILD.md) | Step one for Mochi (2026-11-07; Rev A approved, Rev B with the gear wheels for approval): every part placed, the rods, the card, the pin map, every net, the budget, parts, checks, build order, risks. Written by the generator |
| [`docs/CONCEPTS.md`](docs/CONCEPTS.md) | Round two (2026-11-07): the three prototypes, their layouts, the shared electronics decisions (5 V rail, lidar switch, pins), the research, the open questions |
| [`docs/pages/desk_robot_concepts.html`](docs/pages/desk_robot_concepts.html) | The published prototype page; built by `docs/pages/gen/concepts.py` (drawings) and `page.py` (text). `python3 concepts.py` regenerates it; `--png DIR` renders check images |
| [`docs/DESIGN.md`](docs/DESIGN.md) | The record: what it is, why these sizes, parts (owned vs to buy), pin map, how it navigates a desk, the bench tests before any brass, build order, mass and run time, risks |
| [`docs/BUY_LIST.md`](docs/BUY_LIST.md) | The shopping list with listings, the order it was put into the Amazon cart, and what was deliberately not bought |
| [`docs/pages/desk_robot.html`](docs/pages/desk_robot.html) | The published drawing: front, side and top views to one scale, with the key and the size table. The geometry lives in the script at the bottom of the file; edit it there and republish |
| [`docs/TODO.md`](docs/TODO.md) | The dated to-do list from order to first roll; `docs/crumb_calendar.ics` holds the same dates for a calendar import |
| [`docs/ARTIFACTS.md`](docs/ARTIFACTS.md) | Links to the published pages |

## In one paragraph

Envelope 72 W × 56 D × 60 H mm: a 52 mm wide cage of 1.0 mm brass rod with a vertical face,
two Ø40 steel spur gears outboard on one shared axle at 20 mm, and a brass dome skid at the
nose. The face is a 1.54" 240 × 240 IPS screen on SPI; the XIAO ESP32-S3 Sense stands behind
it with the camera lens on the brow above the screen and the PDM microphone on the same board.
On the brow a VL53L7CX 8×8 ranger tilts 35° down for obstacles and the desk edge ahead; a
VL53L1X flat under the top rail looks down past the nose, 59 mm to the desk, as the hard edge
stop (both need that height: ST's rangers do not work under about 20–40 mm). Two N20 gear
motors sit end to end low on the side walls at axle height on a SparkFun Qwiic I²C motor driver (so no
GPIO goes to motors and the screen gets its four pins); the Nitecore 16340 lies across the floor
in its holder just ahead of the motors; the MPU6050 lies on the tail floor; the driver
stands above the left motor, the MAX98357A amp and the MAX17048 fuel gauge above and ahead of
the right one; the Same Sky 20 × 13 mm speaker is the tail wall. The gauge reads the cell over
I²C, since no GPIO is left for a divider. Checked end to end on 2026-10-31; the gear size corrected the same night from the listing's drawing (Ø40, not Ø53).

## Rules carried over from the other builds

The cell is the only source; the XIAO's own charger fills it over USB-C and nothing feeds its
`5V` pin. Never solder to the cell; it sits in the holder behind the toggle in its + lead.
Neither speaker lead is ground. The brass is not a conductor; every net is insulated wire or
the parts' own pins. Volume cap 65 with `GAIN` open. Say "untested" until it has run.

## What is different from Mo-chan, on purpose

Square case instead of a capsule; a 1.54" colour IPS face instead of a 0.96" OLED; the same 64T steel
gears as wheels, chosen on purpose, on brass-tube hubs; a camera, a microphone, two laser rangers, an IMU and
a speaker where Mo-chan has none; an I²C motor driver instead of a mini L298N; a swappable 16340 instead of
a pouch cell on a TP4056.
