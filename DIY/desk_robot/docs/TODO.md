# Crumb to-do, dated

Written 2026-10-31 after the order. Tick the box and add the date when a line is done. Calendar
file for the same dates: `crumb_calendar.ics` (import into Google Calendar or Apple Calendar).

## Before the box (by Tue Nov 3)

- [ ] Count the drawer: K&S 1.0 mm brass rod (need about 4 rods), METERXITY 5 mm and 4 mm tube (need 18 mm of each), 30 and 26 AWG wire, Kapton.
- [ ] Pull from stock and set aside: VL53L7CX, VL53L1X, GY-521, MAX17048, speaker, 16340 + holder, toggle, button, two QT cables, the passives in `DESIGN.md`.
- [ ] Read `DESIGN.md` tests 1–8 once; set up the bench supply at 3.7 V, 500 mA limit.

## Sun Nov 1: safety glasses and magnifying lamp arrive — picked up 2026-11-01

- [ ] Clamp the lamp on the bench.

## Tue Nov 3: main order arrives (motors, amp, driver, gears, screen) — picked up 2026-11-03

- [ ] Caliper both gears: outer diameter (drawing says 40), bore (5.0), plate thickness, boss length (9 overall). Write the numbers into `DESIGN.md`. If OD ≠ 40, move the axle height.
- [ ] Spin each gear on a 5 mm pin; look for wobble.
- [ ] Measure the N20s: 3 mm D-shaft, body length, shaft length (design assumes 10).
- [ ] Motor driver: confirm address 0x5D, cut the I²C pull-up jumper, meter VIN polarity.
- [ ] Screen: note the 8-pin header order; 3.3 V only.
- [ ] Test 2: I²C chain on a breadboard (driver, MPU6050 with its 2.2 kΩ removed, fuel gauge).
- [ ] Test 3: both rangers, VL53L1X re-addressed to 0x2A. Needs an ESP32 for now: borrow any owned board until the XIAO lands.
- [ ] Test 4: motors on the driver from the bench supply, both directions, stall current with a gear fitted; pick the drive cap.
- [ ] Test 5: amp and speaker, one tone.
- [ ] Make the two hubs (9 mm of 5 mm tube over 9 mm of 4 mm tube, soldered); press into the gears; true on a motor shaft.

## Nov 8–11: XIAO ESP32-S3 Sense arrives (Orders page 11-01; was Nov 10–15)

- [ ] Cut jumper J3 first.
- [ ] Test 1: camera demo, mic, then Pip's audio on I²S1.
- [ ] Test 6: Pip's eyes on the 1.54" IPS at 26 MHz; frame rate and backlight floor.
- [ ] Test 7: everything on the 16340 through the toggle; log idle, streaming, driving current.
- [ ] Test 8: edge test on the bench, wheels off the desk.
- [ ] Check which end of the Sense board carries the camera (USB-C up or down) before bending the brow.

## After test 8: build

- [ ] Bend the cage; solder the eight corners; fender rails at axle height 20 with the motor cradles.
- [ ] Mount motors, gears, holder across the floor, IMU on the tail floor, wall boards, speaker, toggle.
- [ ] Face: screen, XIAO shifted 4 mm left, VL53L7CX on the brow, VL53L1X under the top rail.
- [ ] Wire, Kapton, meter every rod against every net.
- [ ] First roll on a towel on the floor, not the desk.

## Nov 13–19: four more brass tube sets arrive (not on the critical path)

## Rev B, 2026-11-07 (the lidar joins Crumb; see `CRUMB_BUILD.md` and `CRUMB_ORDER.md`)

- [x] 2026-11-08: ordered the charger-boost (DigiKey 102777448, about 11-13 to 11-15) and the LD19 lidar kit with a 100-pack of AO3401A (Amazon order 114-7956116-1377847, arriving 11-09). The brass sheet was skipped; the first build runs without skins.
- [ ] Caliper both gears now (OD, bore, plate, length over the boss; grub screw?) and put the numbers into `pages/gen/crumb_build.py`.
- [x] ~~When the lidar comes: caliper its flange and its three holes; watch a scan through the kit's USB adapter on the PC first.~~ Dropped 2026-11-09: Rev C has no lidar; the kit and the MOSFET pack go to the shared bin unopened.
- [ ] Skins: cut, Kapton-line and spray every piece in the skins table before any fitting. No card anywhere.
- [ ] The bench tests in the Rev B build order, the chain scan first, the current log last; then the cage.
- [x] 2026-11-09: the compute split recorded in `COMPUTE.md` and brought to Rev C the same day (the XIAO does motion, safety and the face; speech and camera frames go to the pocket server). The lidar's serial rate corrected in `pages/gen/mochi_physics.py`: 4,500 points a second, about 17.6 kB, not 4,500 bytes.
- [ ] After the firmware's safety loop and face: give the pocket server an image path (HTTP POST of a JPEG with the device token) and pick a model that can see (a vision-language model through Ollama on the GPU, or the OpenAI path); the local brain is text only. Details in `COMPUTE.md`.

## Rev C, 2026-11-09 (the lidar comes off; see `CRUMB_BUILD.md`)

- [x] 2026-11-09: Rev C approved as drawn on the Crumb Build page (72 × 56 × 60 mm, no lidar, nothing to buy).
- [ ] Step two for Rev C: the physics page (`crumb_physics.py`, forked from `mochi_physics.py`, no lidar) and a 1:1 cage template.
- [ ] When the Amazon box of 11-09 lands: the lidar kit and the AO3401A pack straight to the shared bin.
- [x] 2026-11-09: purchase check against the Amazon, DigiKey and Adafruit order mails: nothing to buy (table in `CRUMB_ORDER.md`).
- [ ] Still in the mail: the XIAO (arriving 11-11, order page read 11-10), the charger-boost (shipped 11-09 by USPS, about 11-12 to 11-14), the motion sensor 3-pack (11-09; the ten-pack is not due until 11-19 to 12-15).

## Edge, pushing and one ranger to buy, 2026-11-10 (see `CRUMB_BUILD.md`, Risks)

- [x] 2026-11-10: the edge worked through against the wheels: the steep ray's foot is 74 mm ahead of the wheels and Crumb stops in 13 mm, so any edge within about 66° of head-on is caught; an edge almost alongside is reached by the outer wheel first (the foot is 34 mm wide, 13 mm right of centre; the wheels 31.5 mm out), and nothing looks back. The drive loop's four rules: step at most 72 mm then sweep ±45°; reverse only the 20 mm back-off after an edge stop; spin in place, never arc, near an edge; a missing or flagged reading is a stop. If a wheel drops, the floor rail catches the desk edge at about 6° of roll and Crumb hangs rather than falls.
- [x] 2026-11-10: pushing assessed: about 0.5 N of traction, so things under about 105 g that slide (heavier if they roll), under about 27 mm tall so they stay under the cone, at half speed. The screen module starts 7 mm up: a bumper rod across the front posts at about 15 mm is a Rev D item.
- [ ] Buy, just in case (decided 2026-11-10): one Pololu VL53L7CX 8×8 ranger carrier, DigiKey Marketplace 2183-3418-ND, $19.95 + post (277 in stock at Pololu on 11-09; not on Amazon). Line and links in `CRUMB_ORDER.md`. The owned spare is the rover's since Rev J. **In the DigiKey cart since 2026-11-10 03:00** (web ID 379101217), a guest cart in the Claude browser pane ($29.90 with Pololu's $9.95 shipping, before tax); checkout the builder's: log in there to merge it into the account, or add the part in your own browser.
- [ ] Rev D, when the first rolls ask for it: the bumper rod, and the 8×8 on the brow beside the lens about 20° down (LPn on D2, the edge ranger to 0x2A at boot, 100 mA on the 3V3 rail). Not drawn.
- [ ] Push test on the towel (in `CRUMB_BUILD.md`, Before power): a 20 g eraser at half speed; the ranger keeps reading the desk beyond it; the board pulled away with the eraser still there stops both motors within the tick.
