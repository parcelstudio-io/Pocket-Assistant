# Mars rover

A palm-sized tank for the desk and the room, built as an open wire frame. Two brass treads you solder yourself
(a 3/32 in brass tube and two 1 mm rods to a plank, little nickel-silver loops between them) run on four
aluminium drums cut on SendCutSend's laser, 35 mm across, with ivory faces, and carry a stainless frame of five
rods. Every board is soldered onto that frame in the open, like a circuit sculpture: the servo in a rectangular
collar at the front, the 0.96 in screen on the collar's front bar, a laser ranger and the drone's flashlight on the
two front posts, the 16340 cell across the rear deck with the charger, the toggle and the motor controller against
it. The frame doubles as the ground. Every board that shows wears a thin ivory skin of brass sheet; black only in
the screen's glass, the camera's lens and the ranger's slot. The head is the camera board on its side with the
drone's spare 8×8 laser ranger beside it, in one ivory sleeve on a little brass cradle on the servo's horn, with a
blinking warm-white beacon on top. You drive it from a phone over Wi-Fi and watch through its camera; the 8×8
ranger sweeps with the head and measures the room. Working name: Sol (a Martian day).

Started 2026-11-06. **Rev A approved as drawn the same day; step 2 written. Rev H, laser-cut drums and ivory
skins, approved as drawn on 2026-11-08; step 2 rewritten for it the same day. Rev I (bigger drums, a longer body
and a LiDAR) and Rev J (the same drums, no LiDAR, an 8×8 ranger in the head) drawn 2026-11-09; Rev J approved as drawn
the same day, step 2 rewritten for it. Carts filled 2026-11-09, nothing paid; nothing cut or soldered.**

The reference is Huy Vector's [DIY Micro RC Spy Tank](https://www.huyvector.org/robots-kinetic/diy-micro-rc-spy-tank)
([video](https://www.youtube.com/watch?v=PszrmrE7JQU)): a 1 mm copper-wire tank on treads of short rods
soldered side by side and tied with thread round four grooved aluminium drums that PCBWay machined (3:16 to 5:30
of the video), with an RC
receiver board, an analog FPV camera, two LED headlights and three 16340 cells. Ours keeps the open wire
frame, the soldered treads, the camera, the light, the 16340 and USB-C charging, and becomes a wide little
tank with a low turning head, Wi-Fi to a phone, and a laser ranger that keeps it on the desk.

## Where it stands: Rev J, approved

The builder's rule for every new project: the final build first, the science after. Step 1, the form sheet,
the wiring sheet, every part and every pin, was approved as drawn on 2026-11-06. Step 2 followed: thirteen
short chapters and twelve figures on why it is built this way.

On 2026-11-07 the body went through seven more drawings, and the builder kept what worked:

- Kept from **Rev D**: soldered brass treads on brass cage drums, no mast, only brass, grey, black and white.
- Kept from **Rev E**: everything but the camera off the head, on a 63 mm deck with the motors 20 mm apart.
- Kept from **Rev F**: the camera board on its side, so the head is low and wide.
- Set aside: the brass frame (B), bars on the silicone tracks (C), and the white card hull and head shell
  (D to F): "the cardstock is going to be very, very ugly".
- Kept from **Rev G**: no box. The boards ride on the stainless frame in the open, each soldered by its ground to
  the nearest rod. Black parts stay bare; the green and blue boards that show wear the owned white
  heat-shrink (ranger, boost, motor controller), and amber Kapton covers the blue charger, the screen's blue
  margin and the cell's yellow wrap (both replaced in Rev H).
- **Rev H** (approved 2026-11-08): the wheels are four aluminium drums like the reference's, cut on SendCutSend's laser from
  `cad/drum.py` (since 2026-11-08): two 3/8 in 6061 halves glued into each, 19 mm wide, 14 round seats, 30.5 mm
  across. The reference's drums, machined by PCBWay, are about 30 mm across and 22 wide. Stock gears came first
  (the stainless 20- and 23-tooth, then SDP/SI's 27-tooth aluminium, out of stock), then a two-plate stainless
  wheel, now the fallback in `cad/`. The planks sit one to a seat on 3/32 in brass-tube pins, 6.4 mm apart, 28 a
  track. Their faces are sprayed canvas white (ivory), the teeth left bare. And nothing shows black but the
  screen's glass and the lens: the camera board (black; it was never in a box), the servo, the coloured boards,
  the screen's margin and the cell holder each wear a thin ivory skin of K&S brass sheet, lined with Kapton.
  115 × 78 × 56 mm and about 275 g; the rails ride 8.6 mm over the desk and the screen's lower edge 5.2 mm.
- **Rev I** (2026-11-09, set aside the same day), at the builder's word ("we need a bigger wheel"; "stick to the 3.5
  centimeter diameter"; "The body can be longer by a little bit"; "add a lidar somewhere because it will require
  navigating a room"): the drums are 35 mm across with 16 seats, still two 3/8 in halves 19 mm wide; the axles are
  52 mm apart; and Crumb's LiDAR, an LDROBOT LD19, rides on two stainless hoops over the back, its scan plane 67 mm
  up, over the head. It runs on its own 5 V boost, which an owned MOSFET switches off when parked; the neck carries
  nine wires. The charger and switch moved into the gap between the LiDAR and the head; the cell and the motor
  controller sit under the LiDAR. 115 × 96 × 75 mm, about 380 g; 1.3 h exploring with the LiDAR spinning, 5.5 h
  parked. A 40 mm drum and a 25 mm-wide drum were weighed and set aside: heavier, for no room inside.
- **Rev J** (approved as drawn 2026-11-09), at the builder's word ("remove the LiDAR ... it's too big and I want the
  device to look quite cute"; "stick with the previous version"): Rev H with Rev I's 35 mm, 16-seat drums and 52 mm
  axles, and no LiDAR. For the room, the drone's spare 8×8 laser ranger (owned) stands beside the camera in the
  head, on its own I²C bus (D8, D9) fed from the controller's 3.3 V: the head is 36 mm wide and the neck stays at
  seven wires. Swept by the head it sees 180° ahead to 3.5 m; the desktop builds a rough map from it. 115 × 90 ×
  58 mm, about 328 g; 1.9 h exploring, 5.5 h parked. On the way a LiDAR sunk in the body under a brass turret, and a
  Pi Zero 2 W on board, were weighed and dropped with the LiDAR.

No 3D printer is needed: nothing in it is printed. Glue will not do for the planks with what is owned (the
hot-glue gun will not hold brass, and super glue is not in the inventory): solder them with the owned iron,
63/37 and Harris flux. The treads cost about eight hours of handwork. Rev J was approved as drawn on 2026-11-09
and step 2 rewritten for it the same day, with a chapter on the 8×8 ranger. Next: the checkouts, then the bench tests.

The carts are filled and nothing is paid; every line and link is in [`docs/ORDER.md`](docs/ORDER.md). Six
lines wait in the builder's DigiKey cart (web ID 379047134: the gearmotors, the motor controller, the laser ranger,
the servo, its boost and the charger; pick USPS Ground Advantage). The Amazon cart was filled in the builder's Chrome on 2026-11-09 evening and read back line by line at 20:55 EST:
the controller board, one pack of 1 mm brass rod, the brass sheet, two packs of 3/32 in brass tube, the 24-gauge
nickel-silver wire and the M3 × 25 screws, 7 items, $108.31, nothing paid; the gel glue came with the desk
lighthouse's order. One rod pack, not two, and the screws kept, at the builder's word. The LiDAR kit is not in the cart.

| File | What it is |
| --- | --- |
| [`docs/FINAL_BUILD.md`](docs/FINAL_BUILD.md) | The record: the reference, the decisions, dimensions and masses, the pin map, every wire and why, the budget, the parts (fourteen lines to buy, the rest owned), the firmware outline, the three meter checks. Generated |
| [`docs/pages/mars-rover-build.html`](docs/pages/mars-rover-build.html) | The published page: the form sheet (side, front and top views to one scale, the face and a cut through the servo, the frame as rods, key numbers), the tread and drum at actual size, and the wiring sheet, with the text of `FINAL_BUILD.md` |
| [`docs/pages/print/mars-rover-build.pdf`](docs/pages/print/mars-rover-build.pdf) | Letter, black only: the form sheet, the wiring sheet and the tread jig in landscape, then the notes in portrait. Print at Actual size. The sheets alone: `mars-rover-form-sheet.pdf`, `mars-rover-wiring-sheet.pdf`, `mars-rover-tread-jig.pdf` (check its 50 mm bar with a ruler) |
| [`docs/pages/gen/build_page.py`](docs/pages/gen/build_page.py) | The generator. Dimensions, pins, nets, the budget, parts and decisions live here; it writes the page, the Markdown and the PDFs, asserts the tread, drum, servo and frame clearances (the drum's numbers and outline come from `cad/drum.py`), and refuses to draw a wiring sheet that fails the line-clearance check. Edit the script, not the outputs. `page_style.css` beside it is the house page style |
| [`docs/PHYSICS.md`](docs/PHYSICS.md) | Step 2, the record (Rev J, rewritten 2026-11-09): why it is built this way, in fourteen chapters, the numbers with their assumptions, and which part each idea lives in. Generated |
| [`docs/pages/mars-rover-physics.html`](docs/pages/mars-rover-physics.html) | The published physics page, with its thirteen figures. Print: `docs/pages/print/mars-rover-physics.pdf`, 11 Letter pages, black only |
| [`docs/pages/gen/physics_page.py`](docs/pages/gen/physics_page.py) | Its generator. It imports the dimensions, the budget and the drum from `build_page.py`; rewritten for Rev H on 2026-11-08 and for Rev J on 2026-11-09, which added the 8×8 ranger: 64 zones, the 180° sweep, its own bus, VDD not VIN (brass on wood, the drums' laser limits and chordal ripple, the head on its servo, the ranger and lamp on the posts, the tread's sag tension) |
| [`docs/ARTIFACTS.md`](docs/ARTIFACTS.md) | Links to the published pages |
| [`cad/`](cad/README.md) | The wheels to have cut on SendCutSend's laser. Approved 2026-11-08: the drum, like the reference's (which PCBWay machined), widened the same day to two 3/8 in 6061 halves glued 19 mm wide, 14 seats for 3/32 in brass-tube pins, 30.5 mm across; 35 mm with 16 seats since Rev I (2026-11-09), from `cad/drum.py`. Fallback: the two-plate stainless wheel from `cad/gear_plate.py`. `cad/wheels.py` draws both to one scale. The build drawing imports the drum from `cad/drum.py` |

Regenerate the build with:

```bash
python3 docs/pages/gen/build_page.py --pdf
```

## In one paragraph

Two 150:1 micro metal gearmotors sit at the rear axle on the ladder's rungs, 14 mm apart; each drives an
aluminium drum (two 3/8 in halves, 19 mm wide, 16 seats, 35 mm, ivory faces) glued on a 4 mm brass hub crimped
on the motor's flat. The idler drums at the front turn on M3 screws soldered into eyes rolled in the frame. Each
tread is 32 brass planks hinged on nickel-silver loops; each plank's pin tube sits in a seat and the teeth push
it. The frame is five rods of the owned 1.5 mm stainless: two side pieces, two rungs, and a rectangular collar at
the front that holds the servo shaft up, its front bar the brow that carries the screen. It is also the ground:
each board's GND is soldered to the nearest rod. The brain rides in the head because the camera is on it: the XIAO
ESP32-S3 Sense, on its side in an ivory sleeve, with the drone's spare 8×8 ranger beside it on its own I²C bus
(D8, D9) and the beacon on top. Everything on the frame speaks I²C (the display, the laser ranger and a Pololu
motor controller that runs from 1.8 V), so the neck is seven wires in a loop: BAT+, GND, 3.3 V, SDA, SCL, the
servo's signal and the lamp's. The ranger looks 30° down from the left front post: the floor or desk 5.1 cm ahead,
the edge found before the treads reach it. 115 wide, 90 long, 58 mm tall, about 328 g; about 8.3 cm/s, 1.9 h
exploring with the camera streaming and the 8×8 ranger on, 2.2 h to charge.

## Rules this build follows

- Component names with the link on the word; model codes only in the parts table's purchase column.
- Owned parts stay off the shopping list: the cell, holder, pigtail, toggle, display, the drone's LED star,
  lens and regulator, the satellite's beacon chip, the coupons, the 4 mm brass tube, the 1.5 mm brass rod
  (if the drawer still holds five), the white heat-shrink, the M3 washers (and screws, if the kit has 25 mm), the
  hook-up wire and the passives.
- Every wire on the sheet is traceable pin to pin; crossings hop; the generator checks clearance.
- Brass, grey, black and white; no green, blue or red on the rover or its sheets. As little plastic as
  possible: none in the running gear, no box, nothing printed. An open frame of five rods; two lines beyond
  the outline, the front posts. Wires along the rods in black and white, and the neck's loop under the head.
- The cell is the only source; nothing feeds the controller's 5V pin; the cell is never soldered; the frame
  is ground and nothing else touches it bare. Meter only polarity, supply and isolation. Untested until it has run.
