# Custom build: the drone without the ESP-FLY kit

Assessed 2026-10-28 against [payload-assessment.md](payload-assessment.md) and the kit pin map in
[wiring.md](wiring.md). Nothing here has been built or weighed. Web version with the drawings:
[XS Drone Custom Build](https://claude.ai/artifact/34eHTqKHJ2gfCkfK2Yb4up), source [pages/custom-build.html](pages/custom-build.html).

The question was whether the kit is needed at all, given that the aim is a sleek, car-like drone that
looks nothing like the kit. Answer: the kit is not needed. Electrically, the custom drone is the
ESP-FLY driver board rebuilt by hand around the same XIAO, so the firmware, the pin map and every
sensor decision in the payload assessment carry over unchanged. What changes is the shape.

**Frame material, settled 2026-11-07.** The builder asked for an all-brass frame wired with copper, then
withdrew it the same hour, before anything was drawn: stainless stands for the drone and for every project
after it (DIY/CLAUDE.md, Design language). The wiring stays silicone wire as drawn below.

**Following mode, 2026-11-09.** Whether the drone can follow a person indoors with local processing, and what
it would look like without the forward ranger (weighed and declined the same day: the ranger stays): [following.md](following.md), web version [XS Drone Following](https://claude.ai/artifact/LYYQRGev8wnFg92FFNJxxc).

## Battery: nothing owned fits, buy the whoop pack

| Owned cell | Mass | Why not |
| --- | ---: | --- |
| Nitecore NL169, 16340, ×6 | 20 g | 2 A protection trips below the 3.5 A hover; 60 % of the aircraft. Decided 2026-10-27. |
| Adafruit #1578 LiPo 500 mAh, ×2 | 10.5 g | 29 × 36 mm flat pack with a protection board whose current limit Adafruit does not publish; half again the mass of the right pack. |
| Adafruit #258 LiPo 1200 mAh, ×2 | about 23 g | heavier than the drone |

The right cell is the Tiny Whoop pack: 1S, 250 to 300 mAh, 30C continuous, JST-PH 2.0 plug, about
7 g, 55 to 60 mm long and 12 mm wide. The length is useful: it becomes the car's floor pan. The owned
daier JST-PH 2.0 cable pairs make the pigtail; check that the housing mates with the pack's plug before
soldering. The owned Adafruit #4410 charger at 100 mA fills a 250 mAh pack in about 2.5 h; the XIAO's
own USB charger is rated 50 mA per Seeed's wiki, which works but takes five hours. LiHV packs (3.8 V
nominal, 4.35 V full) charge safely to 4.2 V on either charger and simply give up a little capacity.

**As bought (checked 2026-11-07).** The four [flight packs](https://www.amazon.com/dp/B0FCMLVCN2) came with
the smaller Micro JST 1.25 plug, not the PH 2.0 this section asks for. That plug family is rated about 1 A per
contact and would carry the 3.7 A hover, so it is the lossiest joint in the power path. Recommended at build
step 1: re-terminate each pack with a PH 2.0 lead from the owned daier pairs (owned · no link recorded),
cutting and joining one wire at a time so the cutters never bridge the pack. The packs then plug straight
into the [USB-C LiPo charger](https://www.adafruit.com/product/4410), and the drone's pigtail is the PH 2.0
lead drawn here. Meter the polarity at every PH 2.0 housing before a pack meets the charger: generic PH leads
are often wired opposite to Adafruit's. Keeping the 1.25 plugs also works, but the charger then needs an
adapter made from one PH 2.0 lead and one of the [1.25 mm leads](https://www.amazon.com/dp/B0GW5WWZTY), and
the first hover must run through the real plug.

## Buy list for the custom build: complete

Everything was ordered by 2026-10-28; the Amazon order log in
[INVENTORY.md](../../pocket_ai_assistant/docs/INVENTORY.md) has the rows (Amazon #23 to #32, the DigiKey
order, and Amazon #34 for the motion-sensor 3-pack). What was bought for the custom build, with its role:

| Part | Role in the drone | Arrives |
| --- | --- | --- |
| 615 coreless motors, 8 (two packs) | lift; four fitted, four spare | Nov 13–24 |
| 31 mm four-blade props, 16 | propellers, four sets | Nov 13–24 |
| Crazepony 1S 250 mAh 30C, Micro JST 1.25, 4 | power and the floor pan | Oct 30, on hand |
| JST 1.25 2-pin leads, 30 pairs | battery lead and charger lead, if the 1.25 plugs stay | Nov 1, picked up (was Nov 3) |
| GY-521 MPU6050, 10 | spares since Nov 7 | Nov 19–Dec 15 |
| GY-521 MPU6050, 3 (HiLetgo) | tilt and yaw sensor, lands first; Crumb takes one | Nov 9 (Orders page 2026-11-09) |
| Clear heat tape, 12 rolls 10 mm (MEBMIK) | the finish: straps, and the card skins | Nov 9 (Orders page 2026-11-09) |
| SS14 Schottky diodes, 100 | flyback diode across each motor | Oct 30, on hand |
| XIAO ESP32-S3 Sense | brain, camera, microphone | Nov 8–11 (Orders page 2026-11-09) |
| AO3400A MOSFETs, 10 (DigiKey) | four motor switches, flashlight fallback | Nov 2, picked up |
| VL53L1X ×2, VL53L7CX ×2 (Pololu via DigiKey) | down and forward rangers, one spare each | Nov 2, picked up |
| Carclo 10412 ×2, PS1240 ×10 (DigiKey) | flashlight lens, beeper | Nov 2, picked up |
| AMC7135, 10 | flashlight regulators | Nov 9 (Orders page 2026-11-09; was Nov 17–20) |
| Cree XP-G2 stars, 4 (one order of four, not six) | flashlight emitter, three spare | Nov 2, picked up |
| uxcell 1 mm × 300 mm rod, 20 | frame rails, axles and bars | Nov 4–5, picked up |

Owned already: 1.5 mm coupons for the collars, resistor kit, 220 µF capacitors, 26 AWG silicone wire,
Kapton, heat-shrink, flux, iron, saw, bench supply, meter, Adafruit charger.

What the kit would have given that this list does not: a factory-made 1 g driver board, props already matched
to motors, and a baseline flight on a frame that is known to work. The last one matters most; see the
build order.

### Double-check, 2026-11-07

Frame stock and every electronic part are ordered; nothing in the airframe is missing. Read against the
inventory, the per-project list, Gmail and the desk log: no drone box has been reported since 11-03 except the
two "online seller" boxes picked up 11-05. They were the two stainless rod orders (shipped 10-28, due 11-05
to 11-16): the builder named the rods that evening, so all 20 are on hand.

To buy: nothing, as of the evening of 2026-11-07. The 0.01 g scale was dropped (the builder is not buying one):
acceptance tests A07 and D02 now use a coin balance and the hover test, see [acceptance-tests.md](acceptance-tests.md).
The finish uses the clear heat tape bought 2026-11-07 over owned white cardstock (see Colour and finish); the tape
is Amazon order 114-0986744-9273034, read off the Orders page 2026-11-09 and logged in the inventory.

Bought 2026-11-07 (builder-reported): a [motion sensor 3-pack](https://www.amazon.com/dp/B00LP25V1A), so the
IMU step need not wait for the 11-19 to 12-15 window of the ten already ordered. The drone and Crumb take one
each and the ten become spares. Order 114-1259113-3701002, $12.84, arriving Nov 9 (Orders page read 2026-11-09).

Fixes found, nothing to buy:

- **Forward ranger on VDD, not VIN.** Pololu gives the [8×8 laser ranger](https://www.pololu.com/product/3418)
  3.3 to 5.5 V on VIN, so the XIAO's 3.3 V would sit on its floor. Pololu's path for a 3.3 V supply is the
  VDD pin (2.5 to 3.6 V) with VIN left open. Corrected in the pin table and under Sensor power below.
- **Battery plug.** See "As bought" under Battery.
- **Collar former.** No 6 mm round bar is on record. Use the owned 6 mm brass tube from the
  [tube set](https://www.amazon.com/dp/B0F2FKLC2N) with the 5 mm tube slid inside so it cannot crush, and
  wrap it in one turn of Kapton for the solder step so the joint cannot grab the brass.
- **LED star pads.** The [LED star](https://www.amazon.com/dp/B00LWU5DWM)'s four solder pads run out toward
  its corners. Mark the 14 mm circle on it before sawing; if the circle cuts through the pads, stop and
  re-plan the lamp first.
- **Lens glue.** Fix the [lens](https://www.digikey.com/en/products/detail/carclo-technical-plastics/10412/2641658)
  by its four legs with the owned low-temperature hot glue, never CA: Carclo warns against solvents and
  vapour, and CA fumes fog the optic. LEDSupply lists it as fitting the 1-Up Indus star bought.

## The hand-built driver circuit, checked

The ESP-FLY driver board is four low-side motor switches, a battery divider, the MPU6050 and two LEDs.
Rebuilt by hand it is this, and it keeps every GPIO the ESP-Drone configuration already expects:

| Net | XIAO pin | GPIO | Part on the other end |
| --- | --- | ---: | --- |
| Motor M4, front left, CW | D0 | 1 | gate of switch 4 |
| Battery sense | D1 | 2 | middle of the 10 kΩ / 10 kΩ divider from VBAT |
| Motor M3, rear left, CCW | D2 | 3 | gate of switch 3 |
| Motor M2, rear right, CW | D3 | 4 | gate of switch 2 |
| I2C SDA | D4 | 5 | GY-521 SDA, VL53L1X SDA, VL53L7CX SDA |
| I2C SCL | D5 | 6 | GY-521 SCL, VL53L1X SCL, VL53L7CX SCL |
| Flashlight enable / PWM | D6 | 43 | VDD of both AMC7135 |
| VL53L7CX LPn | D7 | 44 | LPn pin of the forward sensor |
| Motor M1, front right, CCW | D8 | 7 | gate of switch 1 |
| IMU interrupt | D9 | 8 | GY-521 INT |
| 3V3 | 3V3 | | VIN of the VL53L1X carrier, VDD of the VL53L7CX carrier (its VIN left open), VCC of the GY-521 |
| Battery | BAT+ / BAT− pads on the back | | the PH 2.0 pigtail (packs re-terminated, see Battery); VBAT and GND buses |

**One motor switch, times four.** GPIO → 100 Ω → AO3400A gate. 10 kΩ from gate to ground, so the
motor stays off while the GPIO floats at boot. Drain → motor negative lead. Motor positive lead → VBAT.
Source → ground. SS14 across the motor with its band (cathode) on VBAT and its anode on the drain.
A 220 µF electrolytic from the owned kit across VBAT near the switches catches the PWM current pulses.

- **The MOSFET is enough.** AO3400A: 30 V, 5.7 A, gate threshold at most 1.45 V, about 35 mΩ with the
  XIAO's 3.3 V on the gate. A 615 motor runs at 0.7 to 1 A and stalls at 2.3 to 2.8 A; 1 A through
  35 mΩ is 35 mW, so the SOT-23 never warms. The kit's SI2300 is the same class of part driven the same way.
- **The diode is enough.** The freewheeling current equals the motor current at the instant of switch-off,
  about 1 A peak and much less on average; SS14 is rated 1 A continuous, 30 A surge. Band toward VBAT;
  backwards it is a dead short across the switch the first time the gate goes high, so the first power-up
  is on the current-limited bench supply, one cell at a time, props off.
- **Motor polarity.** Coreless motors spin either way; the CW and CCW labels tell you which lead is
  positive for the intended direction. The whoop convention is red positive on CW motors and black
  positive on CCW motors, but the motor-direction test in [acceptance-tests.md](acceptance-tests.md)
  decides, not the wire colour. Swap the two leads to reverse a motor.
- **The IMU.** GY-521 at 0x68 (its AD0 is pulled low on the board), 3.3 V logic, its own 2.2 kΩ I2C
  pull-ups, INT brought out. ESP-Drone expects the MPU6050 in the ESP-FLY orientation; mount the GY-521
  flat under the floor pan with its X arrow toward the nose and run test C03. If a sign is wrong, rotate the
  board, do not patch the firmware.
- **Sensor power.** The VL53L1X carrier level-shifts SDA and SCL to its VIN (2.8 to 5.5 V), so its VIN
  takes the XIAO's 3V3, not VBAT. The VL53L7CX carrier wants 3.3 to 5.5 V on VIN, which would leave the
  XIAO's 3.3 V on its floor, so it takes 3V3 on its VDD pin instead (2.5 to 3.6 V, VIN left open), the path
  Pololu gives for a 3.3 V supply; its SDA, SCL and LPn then sit at VDD (corrected 2026-11-07). The GY-521
  goes on 3V3 too, so that all three devices share one logic level. The XIAO's 3V3 rail then carries the
  ESP32, the camera, three sensors and the mic: about 500 mA at the camera's peak, inside the 700 mA
  Seeed's wiki allows. The flashlight and the motors run from VBAT and never touch that rail.
- **The divider.** 10 kΩ + 10 kΩ from the resistor kit, GPIO2 reads half the cell voltage: 2.1 V full,
  1.65 V empty. Same values as the kit, so the firmware's battery display needs no change.
- **What is left out.** The kit's green and red LEDs; the flashlight is the status light now.
  The blue LED and buzzer pins are already disabled in the config for the camera.

Mass of the hand-built board: four SOT-23, four SMA diodes, ten resistors, a capacitor, the GY-521 and
the wire, about 2.5 g est. against the kit board's 1 g. The frame absorbs the difference; see the ledger.

## The car-like layout

The kit is a square. A car is longer than it is wide, low, with its lights at the nose. The custom
frame is a ladder: two 1.0 mm stainless rails 14 mm apart running the length of the body, two cross
rods at the "axle" positions that carry the motors outboard, a nose bar for the headlights and a tail
bar. The battery lies between the rails as the floor pan; the XIAO stack sits on it as the cabin.

| Figure | Kit layout | Car layout |
| --- | ---: | ---: |
| Motor spacing, lateral × fore-aft | 36.8 × 36.8 mm | 40 × 60 mm |
| Diagonal wheelbase | 52 mm | 72 mm |
| Footprint, prop tip to prop tip | 67 × 67 mm | 71 × 91 mm |
| Height, ground to top of the camera | 35 mm | 26 mm |
| Prop plane above the rails | 16 mm | 16 mm |
| Frame mass | 4.5 g | 4.4 g est. |

Why 40 × 60 and not smaller: the four prop discs are 31 mm across and must not pass over anything
taller than 16 mm. Spacing the motors 60 mm fore and aft moves the front discs clear of the cabin,
so the XIAO stack can stand 21 mm tall at the centre without the props sweeping over it. Laterally
40 mm leaves 9 mm between adjacent prop tips. At the nose the discs do pass over the headlight bar, so
everything on it stays under 15 mm: the flashlight star stands 14 mm tall from 3 mm below the rails,
the VL53L7CX board 13 mm, and the camera, which is on the Sense board in the cabin and not at the nose,
looks forward over the hood from 21 mm up on the centre line, where no disc reaches.

A three-quarter view of the whole aircraft, projected to scale from these coordinates, is on the
[web page](https://claude.ai/artifact/34eHTqKHJ2gfCkfK2Yb4up) above the plan views.

Layout, top view, nose up, lateral positions from the centre line:

```text
   headlight bar at +33 mm:   flashlight star at −9, lens 7 mm proud  |  VL53L7CX at +9, facing forward
   front axle at +30 mm:      motors at ±20, CW left (M4), CCW right (M1)
   cabin, +10 to −10 mm:      XIAO + Sense on top of the battery, camera on its front face, 10° down
   floor pan, +27 to −27 mm:  the 55 × 12 mm pack between the rails, Kapton-strapped
   rear axle at −30 mm:       motors at ±20, CCW left (M3), CW right (M2)
   tail, −27 to −33 mm:       VL53L1X under the floor pan, looking down; GY-521 under the pan at the centre
   rails at ±7 mm, 66 mm long; 5 mm skids under the axle ends
```

The two headlights are not symmetrical in function, and that is the car reference: a lamp on the
left, a sensor on the right, both forward. If the flashlight must sit on the centre line as first
asked, the VL53L7CX moves to the hood in front of the cabin, under the camera, and the beam and the
depth map still overlap.

Rod: rails 2 × 66 mm, axles 2 × 40 mm, nose bar 31 mm, tail bar 14 mm, four 5 mm skids: 277 mm of
1.0 mm rod, one 300 mm stick, 1.7 g. Four two-turn 1.5 mm collars at the axle ends for the motors, 48 mm of rod
each, 2.7 g (cut 60 mm blanks to wind). Corrected 2026-11-06 while drawing the jig: the nose bar was 36 mm, which
ran into the front collars, and the collars were costed at 40 mm of rod. Bare frame 4.4 g, not 4.1. The 1:1 jig
is [pages/frame-jig.html](pages/frame-jig.html) (print [pages/print/frame-jig.pdf](pages/print/frame-jig.pdf),
generator `pages/gen/frame_jig.py`). Every joint is a
lap or a T on the stainless procedure in the inventory's Amazon #23 row. The battery is a stressed
member once strapped: it stops the ladder racking.

## Colour and finish

Decided 2026-11-07 at the builder's request, under the family colour rule in DIY/CLAUDE.md: white, ivory or
black as much as possible, the frame its own metal, nothing green, blue or red in sight. First drawn that day as
matte black skins, then redone in white the same evening when the builder put white and ivory first. So:
stainless, white and black. The frame is bare brushed stainless; every board and label that would show a colour
goes under a patch of white card held by clear tape; the props and the controller are the black. The headlight
is white light; the controller's gold pads and the camera's amber ribbon are the only warm notes. Colours as
bought were read from the vendors' photos on 2026-11-07.

| Part | As bought | Finish |
| --- | --- | --- |
| Frame, collars, skids | stainless | bare; wash the flux off |
| [Motors](https://www.amazon.com/dp/B09J236JJL) | silver cans; CCW leads black and white, CW leads red and blue | CW leads in the owned white heat-shrink |
| [Props](https://www.amazon.com/dp/B09L4MXXCW) | black | as bought: the black |
| [Controller](https://www.amazon.com/dp/B0C69FFVHH), camera, antenna | black board, silver shield, gold pads | as bought |
| [Flight packs](https://www.amazon.com/dp/B0FCMLVCN2) | silver-white wrap with a big red "250" | a white card patch over the label under two strips of clear tape; the wrap is already white |
| Battery straps | amber Kapton | clear heat tape, 10 mm |
| [8×8 laser ranger](https://www.pololu.com/product/3418), at the nose | green board | white card on both faces, held by clear tape, window cut over the sensor |
| [Down-looking laser ranger](https://www.pololu.com/product/3415) | green board | white card on the faces that show, held by clear tape, window over the sensor |
| [Motion sensor](https://www.amazon.com/dp/B00LP25V1A) | blue board | white card under clear tape, after test C03 |
| Wire | six colours per kit | white for everything, black for ground; bundles in the owned white heat-shrink |
| [Flashlight](https://www.amazon.com/dp/B00LWU5DWM) | aluminium star, clear lens, black regulators and beeper | as bought; white hot glue on the lens legs |
| Plugs | white PH 2.0 housings | as bought |
| Status lights | motion sensor power LED; controller charge and user LEDs | power LED under its card; the charge LED lights only on USB; the user LED stays off in firmware |

Materials: the [clear heat tape](https://www.amazon.com/dp/B0BD84GGPV) bought 2026-11-07 (12 rolls of 10 mm × 33 m, polyester film
with a heat-resistant adhesive), the owned [white cardstock](https://www.amazon.com/dp/B0DSH5V1TT) and the owned white heat-shrink.
Nothing to buy. Tape rather than heat-shrink on the packs, so no heat goes near a cell. If the white 3M film
turns out to be among the day's orders, it replaces the card and saves 0.2 g.

The finish goes on last, over tested joints: a skin hides a board's pin labels, so solder and test first.
It weighs about 0.4 g (card patches 0.2 g, tape 0.2 g), which takes the estimate to 33.7 g and thrust to
weight to 2.02, still over the 2.0 gate. The hover test decides. The web page's drawings are in these colours.

## Mass ledger and flight numbers

| Item | Mass | Basis |
| --- | ---: | --- |
| 4 × 615 motors | 8.0 g | about 2 g each, vendor figures vary 1.8 to 2 |
| 4 × 31 mm props | 1.2 g est. | |
| 1S 250 mAh pack | 6.7 g | ZEVORO listing |
| XIAO ESP32-S3 | 3.5 g est. | |
| Sense expansion with camera | 2.5 g est. | |
| GY-521, header removed | 1.5 g est. | 2.1 g listed with header |
| Switches, diodes, resistors, capacitor | 1.0 g est. | |
| Stainless ladder frame with collars | 4.4 g | 7.93 g/cm³; jig figures, 2026-11-06 |
| Flashlight: 14 mm star, lens, two AMC7135, piezo | 2.0 g est. | payload assessment |
| VL53L1X + VL53L7CX | 1.0 g | Pololu |
| Wiring, Kapton, solder | 1.5 g est. | |
| Finish: white card under clear tape, straps, lead sleeves | 0.4 g est. | colour and finish |
| **Flying mass** | **33.7 g est.** | |

| Figure | Kit-based plan, 32 g | Custom, 33.7 g |
| --- | ---: | ---: |
| Thrust-to-weight on the vendor's 68 gf | 2.1 | 2.02 |
| Hover current, scaled as mass^1.5 from 2.4 A at 25 g | 3.5 A | 3.8 A |
| Flight time at 80 % of 250 mAh, lamp off | 3.2 min | 3.0 min |

Same aircraft, about a gram apart. The custom column carries the jig's 4.4 g frame (2026-11-06) and the
0.4 g finish (2026-11-07), which together take thrust to weight from 2.06 to 2.02, just over the 2.0 gate. The 68 gf is
still the ESP-FLY vendor's claim for these motors on 30 mm props; the E010, which flies the same motors on
these 31 mm props at about 22 g, is the reassurance that the class works, and the hover test (D02) is
still the gate. If it fails, 716 motors on 40 mm props, with the axles lengthened to 50 mm.

## Build order and gates

1. **Power first.** Packs re-terminated to PH 2.0 (see Battery), then the pigtail, divider, 220 µF, XIAO
   on the bench supply at 3.7 V with the current limit at 0.5 A. The app shows the voltage the meter shows.
2. **One switch cell on the bench**, motor without prop, bench supply limited to 1.5 A. PWM sweep from
   the firmware's motor test. The MOSFET stays cold, the motor stops at zero, the diode band points at
   VBAT. Then the other three.
3. **IMU.** GY-521 under the floor pan, test C03: nose down, right side down, clockwise yaw, each with the
   right sign. Rotate the board until they are.
4. **Solder the ladder frame**, mount everything, put on the finish. Motor-direction test with no props, then props
   on. The thrust gate is read in the first hover (step 5, test D02). Under 2.0 means 716 motors before anything else.
5. **First hover** over a bed, no sensors beyond the IMU, lamp off. This is the custom build's
   baseline, the flight the kit would have given for free. Read the thrust gate here: a full-throttle punch
   from a low hover, the accelerometer's z log peak in g is the thrust-to-weight ratio; without the log,
   hovering at 70 % thrust or less passes.
6. Then as the payload assessment says: VL53L1X and height hold, flashlight and beeper, VL53L7CX last.

## Sources

Motors and props: [615 for H36/E010, 4-pack](https://www.amazon.com/dp/B09J236JJL), [Chaoli CL-615 specification](https://www.rotorama.com/motory/chaoli-cl-615),
[31 mm props for 614/615](https://www.amazon.com/dp/B0FKZZ1T5K), [BETAFPV 31 mm props](https://www.amazon.com/dp/B075F8DM26).
Battery: [ZEVORO 250 mAh](https://www.amazon.com/dp/B0FQC9MDT6), [GNB 250 mAh](https://amazon.com/dp/B07GVDXVY5), [Adafruit 500 mAh](https://www.adafruit.com/product/1578).
IMU: [GY-521](https://www.amazon.com/dp/B07MMZ37PT). Diodes: [Chanzon SS14](https://www.amazon.com/dp/B079KJ46ZS), [onsemi SS14 at DigiKey](https://digikey.com/product-detail/en/fairchild-on-semiconductor/SS14/SS14CT-ND/965729).
MOSFET: [AO3400A](https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089). Kit reference: [Co-Create ESP-FLY](https://github.com/Seeed-Projects/Co-Create_ESP-FLY), [wiring.md](wiring.md), [purchasing.md](purchasing.md).
