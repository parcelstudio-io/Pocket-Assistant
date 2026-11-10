# Desk Robot: design record

**Rev B, 2026-11-07, supersedes this record for the build: `CRUMB_BUILD.md` (generator `pages/gen/crumb_build.py`, page `pages/crumb-build.html`) keeps this cage and these gears and adds Mochi's lidar, charger-boost 5 V rail, lidar switch, pin map and wiring sheet, with ivory brass-sheet skins on every off-palette board and no cardstock; the 8×8 ranger and the button are set aside. What follows is Crumb as drawn on 2026-10-31.**

**Concept, 2026-10-31. Paper only: nothing bought, bent, soldered or flashed.** The drawings are
on the published page (`pages/desk_robot.html`, see `ARTIFACTS.md`). Working name Crumb.
Checked end to end the same evening; the changes that check forced are listed at the bottom,
followed by the two decisions the builder took afterwards (gear wheels, vertical face) and the
correction made when the gear listing's drawing showed the gear is Ø40, not Ø53.

## What it is

A desk-roaming companion the size of a coffee cup: it drives around the desk on two Ø40 mm
steel spur gears, the way Mo-chan does, stops at the edge, looks at things with a camera,
chirps and talks through a small speaker, listens through the microphone on its camera board,
and shows a face on a 1.54" colour IPS screen (240 × 240, about 220 pixels per inch, SPI with
DMA, 30 frames a second for the eyes). The same local server that Pip, the tower and the
Sphere talk to (`pocket_ai_assistant/character/server`) is the brain over Wi-Fi; the robot's own
firmware owns motion, edge safety and the face.

Coordinates: x right, y up from the desk, z forward (toward the face); the face is at z +27 and
the back at z −29. All sizes in mm.

| Element | Size | Where |
| --- | --- | --- |
| Cage, 1.0 mm brass rod | 52 W × 56 D (z −29..+27) × 54 H (y 6..60); vertical face; corner radius 3 | the whole body |
| Wheels | HSP 11184 steel spur gear, 64T, 0.6 module, Ø40, 5 mm bore, 9 over its boss (the listing's drawing; plate thinner, measure) | outboard at x ±(27..36), boss inboard, one shared axle at z −7, axle height 20 |
| Hub | 5 mm and 4 mm brass tube telescoped, 9 long, soldered | fills the gear's 5 mm bore down to the motor's 3 mm D-shaft; flat filed on the shaft, a drop of CA |
| Motors, N20 gear, 24 × 12 × 10 | end to end on one axis: left x −25..−1, right x +1..+25, 2 mm between them; bodies y 15..25, z −13..−1 | low on the side walls at axle height, shafts out through the fender rails |
| Skid | brass dome, Ø5, on a 1.0 mm post from the floor rail | nose, x 0, z +24 |
| 16340 holder, 43 × 18 × 14 | across the body | on the floor just ahead of the motors, x ±21.5, z 0..+18, y 6.5..20.5 |
| MPU6050 (GY-521), 21 × 16 | flat | tail floor, x −23..−7, z −26..−16 |
| 1.54" IPS module, about 33 × 36 | picture 27.7 × 27.7, 240 × 240 | the face, y 7..43, z 25..27; header pins at the bottom, bent back into the empty chin |
| XIAO ESP32-S3 Sense stack, 21 × 18 × 9 | lens at (x −4, y 50), over the screen's top edge | standing behind the face, z +17..+25, y 36..57, shifted 4 left so the brow has room |
| VL53L7CX carrier, 12.7 × 17.8 | on the brow right of the lens, tilted 35° down | x +1..+19, y 46..56, at the face plane |
| VL53L1X carrier, 12.7 × 17.8 | flat under the top rail, sensor at its front end, aimed 15° forward of straight down | x −19..−6, z +12..+30, y 57.5..59 |
| SparkFun Qwiic Motor Driver, 25.4 × 25.4, about 10 thick with its screw terminals | standing, terminals toward the rods | left wall above the motor, x −24..−14, z −28..−3, y 33..58 |
| MAX98357A amp, 19 × 16 | standing | right wall above the motor, x +22..+24, z −26..−7, y 33..49 |
| MAX17048 fuel gauge, 25 × 18 | standing | right wall forward of the motor, x +22..+24, z 0..+18, y 23..48 |
| Speaker, 20 × 13 × 4.9 | firing backward | the tail wall, x ±10, y 40..53 |
| Toggle MTS-102 | lever out the back | tail wall, right of the speaker, x +19, y 44..48 |
| Button | on the top rail | x 0, z −20 |

The chin (y 6..7 under the screen) is empty except the skid post and the screen's bent header.

## Why these numbers

- **52 wide** is two N20 motors end to end on one axle (24 each plus 2 between) and a millimetre
  to each wall. Staggered motors would allow 42, but with Ø40 wheels a 13 mm offset shows from
  the side and one wheel would reach 11 mm past the tail; the builder chose inline.
- **72 over the gears**: 1 mm from the cage to the gear's boss and 9 mm of gear each side. The
  boss goes inboard so the N20's 10 mm shaft reaches 8 mm into the hub.
- **56 deep** is the 25 mm motor driver on the wall behind the motors, the 18 mm cell holder
  across the floor ahead of them, and the screen and XIAO stack ahead of that.
- **60 tall** is 6 of clearance, 1 of chin, the 36 mm screen, and a 17 mm brow that holds the
  camera lens and both rangers. The gears reach 40, two thirds of the way up. The rangers sit on
  the brow because ST's time-of-flight sensors do not range below about 20–40 mm.
- **Axle 20** is the gear's radius; the motors sit low on the walls at that height, so the cell
  cannot lie under them front-to-back and lies across the floor just ahead of them instead.
  Centre of mass is low and about 8 mm ahead of the axle, so the skid stays loaded and the body
  does not tip on a bump.
- **Ø40 wheels at 60–70 rpm** give 13 cm/s unloaded, about 10 under load; the firmware caps
  drive well under that for a desk.

## Parts

| Qty | Part | Where | Status | Why, and what to check |
| --- | --- | --- | --- | --- |
| 1 | Seeed XIAO ESP32-S3 Sense | Amazon [B0C69FFVHH](https://www.amazon.com/dp/B0C69FFVHH), in the cart | **buy** | All three owned boards are allocated (tower, drone, Sphere). Camera, PDM mic, Wi-Fi, charger (SGM40567, 50–100 mA). Cut jumper J3 on the Sense board so GPIO7/8/9 are free of the SD slot. |
| 1 (of 3) | Hosyond 1.54" IPS TFT, 240 × 240, ST7789, 4-wire SPI, 3.3 V, 3-pack | Amazon [B0HGLQZK3P](https://www.amazon.com/dp/B0HGLQZK3P), in the cart | **buy** | The face: colour, 220 ppi, ESP-IDF's built-in `esp_lcd` ST7789 driver. Four pins: SCK, MOSI, DC, backlight PWM. CS tied to GND, RESET to 3V3 through 10 kΩ with 1 µF to GND. Two spares for other builds. |
| 2 | Globact 11184 steel spur gear, 64T, 0.6 module, Ø40, 5 mm bore, 9 mm over its boss (each listing: one gear and four pinions) | Amazon [B0881RWD2L](https://www.amazon.com/dp/B0881RWD2L), 2 in the cart | **buy** | The wheels. Same HSP 11184 part as ShareGoo [B075NYPT43](https://www.amazon.com/dp/B075NYPT43) and Hobbypark [B01CA49O32](https://www.amazon.com/dp/B01CA49O32); Globact chosen for the best rating (4.4 of 267). The pinions are spare. Ø40 and 9 mm come from the listing's drawing: caliper the diameter, the plate thickness, the boss length and the bore (5.0) on arrival. |
| 2 | JUZITAO N20 gear motor, 6 V 100 rpm, 3 mm D-shaft, 2-pack | Amazon [B0C9QC4SRY](https://www.amazon.com/dp/B0C9QC4SRY), in the cart | **buy** | About 60–70 rpm unloaded at the cell's 3.7–4.2 V. Measure stall current on the bench supply before the frame; the gears add about 32 g each of load. |
| 1 | SparkFun Qwiic Motor Driver, I²C, PSoC + DRV8835, 1.2 A per channel | Amazon [B07YCVHQD5](https://www.amazon.com/dp/B07YCVHQD5), in the cart | **buy** | Both motors over I²C at 0x5D: speed and direction by register, no PWM pins. Motors and the cell on its screw terminals; logic from the 3.3 V Qwiic bus. No current limit of its own, so the firmware ramps drive and caps it at the level the stall test sets. Cut its I²C pull-up jumper (see the bus note). The owned MX1508s stay in the drawer. |
| 1 | HiLetgo MAX98357A I²S amplifier, 3-pack | Amazon [B0CDWXZZCH](https://www.amazon.com/dp/B0CDWXZZCH), in the cart | **buy** | Covers this robot and the one-board shortfall across the tower, the Sphere and Cyber Dawn. `SD` stays on the module pull-up: the chip shuts itself down when the I²S clock stops. VIN from the cell, logic 3.3 V tolerant. |
| 1 | Pololu VL53L7CX carrier #3418 | owned ×2, one spare after the drone ([xs_drone](../../xs_drone/docs/custom-build.md)) | owned | 8×8 ranger on the brow, 60° × 60° field. 0x29 default; LPn on GPIO43. Minimum range about 20 mm. |
| 1 | Pololu VL53L1X carrier #3415 | owned ×2, one spare after the drone | owned | Edge ranger under the top rail looking down past the nose: path 59 mm to the desk, inside its 40 mm minimum. Re-addressed to 0x2A at boot while the 7CX is held off the bus. |
| 1 | GY-521 MPU6050 | owned ×10, nine spare | owned | Heading hold, bump detection, and a wheel-drop fallback. 0x68. **Its 2.2 kΩ I²C pull-ups come off** (see the bus note). |
| 1 | Adafruit MAX17048 fuel gauge #5580 | owned ×2, one spare ([cyber_clock_v2](../../cyber_clock_v2/docs/INVENTORY.md)) | owned | Cell state of charge over I²C at 0x36; no GPIO is left for a divider. Its STEMMA QT socket chains to the motor driver's Qwiic socket with an owned 100 mm QT cable. |
| 1 | Same Sky CES-20134-088PM speaker | owned ×6 (DigiKey account read 2026-11-03), two spare after Pip, the Sphere and the camera Pocket AI | owned | The tail wall. Neither lead to ground. |
| 1 | Nitecore NL169 16340 | owned ×6, three spare | owned | The cell. 950 mAh protected, 2 A limit; the XIAO's charger terminates at 4.2 V. |
| 1 | ACEIRMC 16340 holder with leads | owned ×10 | owned | On the floor. Meter red to + before the cell goes in. |
| 1 | Ferwooh MTS-102 toggle | owned ×20 | owned | In the cell's + lead. |
| 1 | QTEATAK tactile button | owned ×420 | owned | Action button on the top rail, GPIO44 to GND. |
| 2 | Adafruit QT cable 100 mm #4210 | owned, two spare ([cyber_clock_v2](../../cyber_clock_v2/docs/INVENTORY.md)) | owned | Fuel gauge to motor driver; one spare. The XIAO end of the bus is 30 AWG to the gauge's header pads. |
| 2 + 5 | 10 kΩ ×2; 220 µF, 100 µF, 10 µF, 100 nF ×2, 1 µF | owned kits | owned | Screen RESET pull-up and backlight gate; 220 µF at the amp VIN; 100 µF + 100 nF on the 3V3 rail at the rangers; 10 µF + 100 nF at the screen's VCC; 1 µF on the RESET line. |
| ≈ 4 rods | K&S #9861 1.0 mm brass rod | owned ×10 minus Pip's and the Sphere's use | owned, count the drawer | Cage edges ≈ 650 mm, rails ≈ 320, skid post. |
| ≈ 18 mm | 5 mm and 4 mm × 0.5 mm wall brass tube | owned (METERXITY set) | owned | Two hubs, 9 mm each of both sizes, telescoped and soldered. |
|  | 26 / 30 AWG silicone wire, Kapton, fish paper, heat-shrink | owned | owned | 26 AWG for BAT+ and GND; 30 AWG for signals; Kapton on every module back facing brass. |
| 1 | External 16340 charger (Nitecore UI1 or XTAR VC2) | optional | optional | Two hours per cell instead of the XIAO's 10–20 h. Shared with the tower and the Sphere if bought. |

Not used: O-rings (the gears run on bare teeth, by the builder's choice; a desk mat gives grip
on glass or laminate), the owned 1.5 mm brass rod (no rims to bend), the owned MX1508.

## Pin map (XIAO ESP32-S3 Sense, J3 cut)

| Pin | GPIO | Net | Notes |
| --- | --- | --- | --- |
| D0 | 1 | screen SCK | 4-wire SPI through the GPIO matrix; 26 MHz is the safe clock there, enough for 28 full frames a second and far more with eye-only updates |
| D1 | 2 | screen MOSI | |
| D2 | 3 | screen DC | strapping pin for JTAG source only when the eFuse is burned; it is not |
| D3 | 4 | screen backlight | LEDC PWM into the module's BLK pin: dim at night, off when parked |
| D4 | 5 | I²C SDA | motor driver 0x5D, MPU6050 0x68, MAX17048 0x36, VL53L1X 0x2A (re-addressed), VL53L7CX 0x29 |
| D5 | 6 | I²C SCL | 400 kHz: the VL53L7CX uploads about 90 KB of firmware at every boot, 2–3 s at 400 kHz, 10 s at 100 kHz |
| D6 | 43 | VL53L7CX LPn | GPIO43 is UART0 TX: the ROM prints boot messages on it before the app runs. LPn only gates the sensor's I²C, so that chatter is harmless; the app then holds it low until the VL53L1X is moved to 0x2A |
| D7 | 44 | action button | GPIO44 is UART0 RX, an input at boot; to GND, internal pull-up |
| D8 | 7 | I²S BCLK | amp. GPIO7/8/9 are the SD slot's SCK/MISO/MOSI on the Sense board; cutting J3 frees them and they are quiet at boot |
| D9 | 8 | I²S LRC | amp |
| D10 | 9 | I²S DIN | amp |
| BAT+ / BAT− pads | — | cell through the toggle | the XIAO's charger fills it over USB-C; the same cell feeds the motor driver's VIN and the amp's VIN |
| internal | 10–18, 38–40, 47–48 | camera | not on the header |
| internal | 41 / 42 | PDM microphone | not on the header; **PDM receive exists only on I²S0** on the ESP32-S3, so the mic takes I²S0 and the amp runs standard mode on I²S1 |
| internal | 21 | user LED (and SD CS, unused with J3 cut) | free for a status blink |

Screen CS is tied to GND (the only SPI device) and RESET to 3V3 through 10 kΩ with 1 µF to GND;
the firmware issues a software reset. Nothing is left over. Amp `SD` stays on its module
pull-up; battery voltage is the fuel gauge's job; the motors have no GPIO at all. The I²S pins
were moved off GPIO43/44 on purpose: the ROM bootloader's serial output on GPIO43 would have
clocked the amp with garbage at every boot.

**I²C bus note.** Five boards, each with its own pull-ups: GY-521 2.2 kΩ, the Qwiic driver
2.2 kΩ, the two Pololu carriers 10 kΩ each, the Adafruit gauge 10 kΩ. In parallel that is about
1 kΩ, 3.3 mA on every low, over the 3 mA the I²C specification allows. Remove the two 2.2 kΩ
sets: the GY-521's are two 0603 resistors beside the pins (unsolder), the Qwiic driver's are a
cuttable jumper on its back. What remains, about 3.3 kΩ, is right for 400 kHz over 150 mm of
wire.

## Power budget

| Load | Rail | Typical | Peak |
| --- | --- | ---: | ---: |
| XIAO with camera streaming over Wi-Fi | 3V3 (its own regulator, 700 mA) | 200 | 300 |
| Screen logic + backlight at half | 3V3 | 40 | 60 |
| VL53L7CX ranging | 3V3 | 60 | 100 |
| VL53L1X ranging | 3V3 | 20 | 20 |
| MPU6050, fuel gauge, driver logic | 3V3 | 15 | 15 |
| **3V3 rail total** | | **335** | **495** |
| Two N20 motors, running / one stalled | cell | 180 | 700 |
| Amp at cap 65 into the 8 Ω speaker | cell | 30 | 300 |
| **Cell total** | | **≈ 550** | **≈ 1.5 A** |

The 3V3 rail stays under the regulator's 700 mA with Wi-Fi bursts included; the 100 µF at the
rangers covers their ranging pulses. The cell's protection trips at 2 A, so the firmware never
lets both motors stall at full drive: it ramps, and it reads the IMU for a bump within one tick.
Run time at 550 mA average is about 1.7 h roaming; parked with the camera and backlight off
(about 60 mA) about 15 h. Charging through the XIAO at 50–100 mA takes 10–20 h and only with
the robot asleep; the optional external charger does it in 2.

## How it navigates a desk

- **Edge, hard stop.** The VL53L1X under the top rail looks down 15° forward of vertical. Its
  centre ray meets the desk 45 mm ahead of the face, 21 mm ahead of the skid; the cone spans
  32 to 61 mm ahead of the face, clear of the chin and the skid. Path length 59 mm, inside the
  sensor's range. A reading over 90 mm, or no target, is a cliff: both motors brake within one
  control tick (20 ms), then the robot backs up 15 mm and turns away. At 10 cm/s it travels
  about 2 mm in a tick; the wheels' contact line is 31 mm behind the skid, so the wheels stop
  about 50 mm from the edge.
- **Edge and obstacles, early warning.** The VL53L7CX on the brow, tilted 35° down, sees the
  desk from about 27 mm ahead of the face outward in its lower rows and looks nearly level in
  its upper rows. Lower rows that jump far beyond the expected desk distance mark the edge
  early; upper rows closer than 80 mm mark an obstacle. The firmware slows at the early warning
  and lets the VL53L1X make the final call.
- **Wheel-drop fallback.** If a wheel leaves the desk the body pitches or rolls by several
  degrees within 50 ms; the MPU6050 sees it and the motors brake, independent of either ranger.
- **Heading.** The MPU6050's yaw rate integrates to hold a straight line and to turn by a set
  angle. With inline wheels a turn in place pivots about the body centre.
- **Reversing is limited to 15 mm** because nothing looks backward; turns are made in place.
- **Camera** frames go to the server over Wi-Fi for anything smarter; the robot never depends on
  them for safety.

## Test every part before any brass

1. **XIAO alone.** Flash the camera web demo; see a frame and hear the mic in the browser.
   Then flash Pip's audio path moved to I²S1 and confirm a tone with the mic still capturing.
2. **I²C chain on a breadboard, pull-ups removed first.** Motor driver, MPU6050, fuel gauge:
   scan shows 0x5D, 0x68, 0x36 at 400 kHz; scope one SCL edge and check the rise time is under
   300 ns.
3. **Rangers.** Add both at 0x29; hold LPn low, move the VL53L1X to 0x2A, release; scan shows
   0x29 and 0x2A. Hold the VL53L1X 59 mm over a table at 15° and watch it read the edge as the
   table ends. Hold the VL53L7CX at 51 mm tilted 35° and read the 8×8 grid over the same edge.
4. **Motors and wheels.** Qwiic driver from the bench supply at 3.7 V, 500 mA limit: both
   directions, drive levels 30 to 127, stall current logged for each motor with a gear fitted,
   and the drive cap chosen so two stalled motors stay under 1.4 A. Spin each gear on its hub
   and check for wobble; a wobbling gear means the hub is not square.
5. **Amp and speaker.** One second of 440 Hz at cap 30 on I²S1; confirm silence with no clock.
6. **Face.** Pip's eyes at 240 × 240 on the 1.54" IPS; measure the frame rate at 26 MHz and the
   backlight current at the dimmest usable level.
7. **Cell.** Everything on the 16340 through the toggle; log current at idle, streaming, driving.
8. **Edge test on the bench, wheels off the desk.** Drive loop running, move a board under the
   rangers and pull it away; both motors stop within a tick on the VL53L1X alone, and the IMU
   fallback fires when the body is tipped 5°.

## Build order

1. Bench tests 1–8 on jumpers. 2. Make the two hubs: 9 mm of 5 mm tube over 9 mm of 4 mm tube,
soldered; press into the gears, true them on a motor shaft. 3. Bend the cage: floor rail
rectangle, two side frames, top rail; solder at the eight corners; add the two fender rails at
axle height with the motor cradles. 4. Mount the motors end to end on the fender rails, shafts
out; fit the gears; the body must sit level with the skid on the desk and both gears touching.
5. Fit the holder across the floor ahead of the motors, the IMU on the tail floor, the wall boards above the motors, the tail
speaker and the toggle beside it. 6. Fit the face: screen with its header bent back into the
chin, XIAO behind it shifted 4 mm left, the VL53L7CX on the brow to the right of the lens, the
VL53L1X flat under the top rail. 7. Wire, Kapton, meter every rod against every net. 8. First
roll on a towel on the floor, not the desk.

## Mass

| Part | g |
| --- | --- |
| XIAO Sense stack | 10 |
| 1.54" IPS screen | 12 |
| Cell + holder | 44 |
| Motors ×2 | 20 |
| Steel gears ×2 with hubs | 65 |
| Driver, amp, gauge, IMU, rangers | 18 |
| Speaker, toggle, button | 6 |
| Brass cage and skid | 28 |
| Wire, Kapton, passives | 6 |
| **Total** | **≈ 209** |

The gears are about a third of the mass, which is why they went low and the cell went to the
floor. An N20 at 1:100 moves this with margin; it is the stall test, not the running load, that
sets the drive cap.

## Risks

- **Five I²C devices and two with the same default address.** The re-addressing dance is proven
  on the drone's plan, not on hardware. Test 3 is first for a reason.
- **The camera's end of the XIAO.** The lens must land at y 50 over the screen; which end of the
  Sense board carries the camera decides whether the USB-C port faces up (good, charge without
  opening the cage) or down. Check on the real board before the brow is bent.
- **Gear on hub on shaft.** Three press fits in series. A gear that wobbles 1 mm at the rim makes
  the robot waddle; true each wheel on the motor before the cage closes.
- **Steel teeth on the desk.** Fine on wood or a mat; they slip on glass and laminate and will
  mark soft finishes. An O-ring tyre over the teeth is the fallback if that matters.
- **Stall current on the cell.** No current limit on the driver; firmware ramp and cap, IMU bump
  stop, and the cell's own 2 A protection as the last resort.
- **Wi-Fi inside a brass cage.** The XIAO's flex antenna goes along the inside of the top rail;
  compare RSSI in the cage against the bare board at the same distance before the cage is closed.
- **IPS backlight at night.** An LCD never goes black; the PWM floor on D3 and a parked
  backlight-off state are what keep it from glowing on the desk at 3 a.m.

## Verification pass, 2026-10-31

Checked: every XIAO pin's boot role, both I²S controllers' modes, the I²C pull-up sum, the
ranging limits of both ToF sensors against their mounting heights, every part's footprint
against its neighbours in all three views, axle height against wheel radius, the 3V3 and cell
budgets, and the cart against the parts table. Changes forced by the check:

| Found | Fixed |
| --- | --- |
| Both rangers in the chin were 4–15 mm from the desk; ST ToF sensors do not range below 20–40 mm | Both moved to the brow: VL53L1X under the top rail looking down 15° forward (path 59 mm), VL53L7CX beside the lens tilted 35° (lower rows from 27 mm ahead) |
| I²S on GPIO43/44: the ROM bootloader's serial output would clock the amp at every boot | I²S moved to GPIO7/8/9; LPn and the button take 43/44 |
| PDM mic and amp cannot share I²S0 on the S3 | Mic on I²S0, amp on I²S1 |
| Five sets of pull-ups summed to about 1 kΩ | GY-521 and Qwiic driver pull-ups removed; 400 kHz |
| Fuel gauge and amp overlapping; toggle through the speaker; lens half behind the screen | Repositioned |
| Parts table said the driver has a current limit | It does not; firmware cap from the stall test |

## Decisions after the check, same evening

1. **Gear wheels instead of spoked brass wheels.** The builder wanted Mo-chan's gear look. Three
   Amazon listings of the HSP 11184 64T steel gear were compared (ShareGoo, Globact, Hobbypark):
   identical gear, then believed to be 0.8 module, Ø52.8, 5 mm bore (see 3); Globact chosen on rating. Bare teeth, no tyres.
   Axle rose from 15.5 to 26.4, the motors went inline on the side walls (cage 42 → 52, 66 over
   the gears), the cell went to the floor, the wall boards moved above the motors, the IMU to
   the nose floor. O-rings left the cart.
2. **Vertical face.** A 20° lean was drawn and withdrawn the same evening; the face is flat and
   vertical, height 60.
3. **Ø40 correction, later the same night.** The Globact listing's own dimension drawing gives the
   64T gear as Ø40, 9 mm over its boss, 5 mm bore: a 0.6 module gear, not 0.8. All three listings
   are the same HSP 11184 part, so the brand does not help. The bore and the hub plan stand.
   Forced by it: axle 26.4 → 20; motors down the walls to y 15..25, where they ran through the
   front-to-back cell holder, so the holder turned across the floor just ahead of the motors
   (z 0..18) and the IMU moved to the tail floor; the 9 mm gear goes boss inboard 1 mm off the
   cage so the 10 mm N20 shaft reaches 8 mm into a 9 mm hub, 72 over the gears instead of 66;
   speed 13 cm/s unloaded, about 10 under load; gears about 32 g each (the pack of one gear and
   four pinions ships at 50 g), total about 210 g. The ranger geometry hangs off the body, not
   the wheels, so the 59 mm edge path and the 21 mm lead over the skid are unchanged. The body
   still rides at 6 mm clearance. Caliper the gear on arrival; the Ø40 is the seller's drawing.
   The hub recipe's drop of CA: no cyanoacrylate is in the inventories, so add a gel CA to the
   order or solder the hub to the shaft flat.
