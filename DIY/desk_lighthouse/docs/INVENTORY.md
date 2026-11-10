# Purchased inventory — Desk lighthouse

Factual purchase record: what was *bought*, not what is approved; part authority stays in
[`FINAL_BUILD.md`](FINAL_BUILD.md). **Rev C was approved on 2026-11-09 and the Amazon order went in the same
morning: eight lines in five orders, $122.64 with tax and two delivery charges, confirmed by Amazon's order mail of
04:22 EST; two of the five shipped the same day for Wednesday 11-11, the filaments come last on 11-27. The charger is
not ordered: the DigiKey order placed at 03:30 that morning is the Mars rover's six lines, and the bq25185 board from
the shared cart link is not among them. Grand Brass: the builder reports the five lamp parts ordered on 2026-11-09;
no confirmation mail had reached Gmail by 18:00 EST, so the order number and the ship date are not recorded. That evening the builder also rejected the acrylic tube (to return when it comes), and the brass sheet went: its order shows **cancelled by the seller, not charged** (Your Orders, read in the builder's Chrome at their word, 2026-11-09 about 22:00 EST), and the copy that had reappeared in the cart from another seller was moved to Saved for later: Rev D, the open lantern with no house, was drawn the same evening and awaits approval; it needs nothing new to buy.**
Everything owned from the other builds is in `../../pocket_ai_assistant/docs/INVENTORY.md`,
`../../cyber_clock_v2/docs/BOM.md` and `../../PARTS_BY_PROJECT.md` and is not repeated here. Rev B (2026-11-08)
dropped Rev A's 25 mm tube, 0.032 in sheet and square tube; Rev C (2026-11-09) dropped the screen and added the cell,
its tray, the diode, two 100 kΩ (all owned) and one charger board (still to buy).

## Owned, taken from the shared stock once approved

| Item | Qty | Where it is | Why |
| --- | ---: | --- | --- |
| Nitecore NL169 16340 cell, 950 mAh, protected, button top | 1 of 13 | the IMR Batteries boxes of 2026-10-16 | the battery, standing in the house behind the motor |
| 16340 holder with leads, 43 × 18 × 14 (ACEIRMC) | 1 of 10 | Cyber Dawn's stock | the tray the cell drops into; never soldered to the cell |
| ESP32-C3 SuperMini | 1 of 13 (10 spare) | Pocket AI stock | the brain, in the coaster's hollow, fed from the cell through the diode |
| MX1508 dual H-bridge | 1 of 5 (4 spare) | the camera Pocket AI's pack | channel A the shutter's motor, channel B the lamp, on the boost's 5 V |
| SS14 Schottky diode | 1 of 100 | the drone's pack | between the charger's BAT pad and the controller's 5V pin |
| 47 Ω resistors, 1/4 W | 2 | the resistor kit | the lamp's series pair, in the hollow |
| 100 kΩ resistors, 1/4 W | 2 | the resistor kit | the cell-voltage divider into GPIO4 |
| K&S 1.5 mm brass rod, 300 mm | 4 of about 90 | shared stock (eighteen 5-packs) | the four rods of the cage, cut 222 each; two carry the lamp's current |
| brass tube set, 2 to 7 mm × 0.5 mm wall, 200 mm | one 4 mm tube, 147 mm of it | shared stock (3 sets on hand) | the spine, motor to shutter |
| K&S 1.0 mm brass rod, 300 mm | 42 mm of one | shared stock (10 rods) | the lamp post, the filament's return |
| tactile button 6 × 6 mm | 1 | the button kit | the one control, under the house's roof |
| 30 AWG silicone wire | about 1 m | bench stock | the wires between the boards, into the house and under the roof |
| Kapton, white heat-shrink, hot glue, 63/37 solder, flux | | bench stock | the live rod's sleeves and boot, the joints, the motor's bed, the washers, the house's seams |
| Rust-Oleum gloss canvas white 7789830 | | Pip's paint | the ivory house |
| USB-C adapter, 1 A, and a cable | 1 | owned | the charger's cable |
| heavy brass coaster 75 × 8 mm, flat top (B0D9DMK3L7) | 1 | Amazon 114-8443990-0476239, ordered 2026-11-06 ($12.99, $14.14 with tax), **delivered 2026-11-09** 12:01 EST to the mail room (Amazon's mail), in one package with the drone's heat tape; bought as the satellite's base, given to this build 2026-11-09 at the builder's word; the pick-up is recorded when its Todoist task is completed | the base and the electronics box; measure the hollow when it is upstairs and rerun the script; a magnet must not stick to the top |
| KraftSense 20 V brushless cordless drill set | 1 | the bench (bought 2026-10-11; found in the order history 2026-11-09) | every hole in the coaster, the deck, the discs and the house, at its slowest; needs metric bits of 1.8, 2.3, 3.5 and 3.6 mm from its case or a small set |

Cyber Dawn's two bq25185 charger boards are both spoken for (Cyber Dawn's own and the satellite's), and the third in the
house, DigiKey order 102777448 shipped 2026-11-09 by USPS, is Crumb's. This build buys a fourth.

## Ordered on Amazon, 2026-11-09 04:22 EST (one checkout, five orders; Amazon's order mail)

The mail names orders and totals, not items. Each line below is matched to its order by price (New York's 8.875 %
tax on the item and on its delivery charge), and the day's two shipping mails confirm the split: $20.48 shipped at
12:13 EST (reed switches and acrylic tube), $38.63 at 17:22 EST (motors and magnets), both from the four-line order.

| Line | Price | Order | Order total | Delivery |
| --- | ---: | --- | ---: | --- |
| uxcell clear acrylic tube 21 ID × 25 OD × 305 | $8.99 | 114-1438198-3243448 | $59.11, four lines | shipped 2026-11-09 with the reed switches; arriving Wed 11-11. **Rejected by the builder that evening ("so ugly, never"): Rev D has no glass. Return it when it comes, or keep it as stock** |
| Augiimor N20 gearmotor 2-pack, 6 V, 30 rpm | $15.99 | 114-1438198-3243448 | | shipped 2026-11-09 with the magnets; arriving Wed 11-11 |
| UGEFKMQ LED filament 10-pack, 26 mm, 2700 K, 3 V, >100 mA (B0HBX2YW18) | $25.40 + $4.98 delivery | 114-6111517-7569023 | $33.07 | arriving Fri 11-27, the last box; the QIROGKC 26 mm 2700 K pack rated 50 mA (B0FR3BWZTM, $13.16) stays the dimmer alternative if these disappoint |
| JESSINIE reed switches 2 × 14 mm, 20-pack | $9.82 | 114-1438198-3243448 | | shipped 2026-11-09 with the acrylic; Wed 11-11 |
| N52 magnets 3 × 1 mm, 100-pack | $19.49 | 114-1438198-3243448 | | shipped 2026-11-09 with the motors; Wed 11-11 |
| K&S 252 brass sheet 0.015 in, 4 × 10 in | $5.31 + $9.49 delivery | 114-5648832-0318640 | $16.11 | **cancelled: Your Orders (read in the builder's Chrome at their word, 2026-11-09 about 22:00 EST) says "cancelled by the seller, you have not been charged"**; Rev D has no house and no sheet-cut discs anyway. A copy from Blick Art Materials ($16.32 + $11.95 delivery) had reappeared in the cart and was moved to Saved for later the same evening |
| K&S 8143 brass tube 5/8 in × 12 in | $9.89 | 114-7188491-2312247 | $10.77 | arriving 11-18 to 11-20 (seller What America Buys) |
| Loctite Super Glue Ultra Gel Control 4 g (B003Y49R7G) | $3.29 | 114-1965907-0721062 | $3.58 | arriving Sat 11-14; the one tube for this build, the hologram and the rover |
| **Eight lines** | **$98.18 + $14.47 delivery** | five orders | **$122.64** | the last box 11-27; that morning the pin vise ($10.99) came off the cart because a KraftSense 20 V cordless drill is owned, and the coaster ($12.99) because the one ordered 2026-11-06 is this build's |

The same five orders were first logged as the Mars rover's (its Amazon lines had been opened in the default browser,
which does not fill the cart, and the builder told that session the cart was ordered); the rover's record and
`PACKAGE_TRACKER.md` were corrected on 2026-11-09 evening. None of the rover's Amazon lines is in these orders.

## Order-history check, 2026-11-09

Read in the builder's Chrome at their word, against every cart line. Owned already: a **KraftSense 20 V cordless drill** (2026-10-11), the
**METERXITY brass tube sets** 2 to 7 mm (200 mm × 3 and 330 mm × 7, October), K&S 1.5 mm tubes and rods, 1 mm rods, a hot-glue gun, B-7000
glue, QIROGKC **38 mm 2200 K** filaments (2026-11-01, the hologram's amber), two **N20 6 V 100 rpm** gearmotors (2026-10-31) and two **3 V
16 rpm 1218 gearmotors** (2026-10-27, the camera Pocket AI's), one **brass coaster** (2026-11-06, bought as the satellite's; the builder gave it to this build on 11-09). Never bought: any brass
tube over 7 mm (so the 5/8 in tube is new), any acrylic tube, reed switches, small magnets, a 2700 K filament, K&S sheet, Loctite gel, a pin
vise. The owned gearmotors do not fit the sheet (100 rpm is too fast for 8 rpm by PWM; the 3 V 16 rpm pair has a smaller shaft and is the
camera build's); the amber filaments would change the lamp's colour and height.

## The other two orders

| Order | Status, 2026-11-09 evening |
| --- | --- |
| Grand Brass Lamp Parts: 1-1/2 in turned brass check ring, 1/8 IP slip (CRT1-12X8) · 1-1/2 in unfinished spun brass vase cap (VA01-12) · 5/8 in brass ball, 1/8 IP blind tap (BB0-58X18) · 1/2 in × 1/8 IP hollow brass nipple (NI0-12X18BR) · 1/8 IP beaded brass nut, 9/16 in; about $7 | **Ordered by the builder on 2026-11-09, by their word** ("I ordered everything I need for the lighthouse"). No mail from Grand Brass had reached Gmail by 18:00 EST (none ever has, spam excluded), so the order number, the total and the ship date are not recorded here; paste the confirmation when it comes and it goes into this row and the tracker |
| DigiKey: bq25185 USB / DC / solar charger with 5 V boost, 1528-6106-ND, $8.95 (Adafruit 6106 is the same board at the same price) | **Not ordered.** The DigiKey order of 2026-11-09 03:30 (sales orders 102785005 and 102785006, Web ID 379047134, $141.92) holds the Mars rover's six lines and nothing else; the charger in the built-in browser's guest cart (Web ID 379031928, share link [digikey.com/short/p2cn2mp7](https://www.digikey.com/short/p2cn2mp7)) never reached the account's cart, and no Adafruit order exists. One line still to buy, from either shop; Amazon has no bq25185 board (searched 2026-11-09 evening in the builder's Chrome: PowerBoost 1000 clones at $21 to $25 and TP4056 boards only), so it stays DigiKey or Adafruit |

Rev D (2026-11-09 evening) needs nothing new: the shutter's two bars, the magnet arm and the deck's bearing wheel come from the owned 1 mm rod, the owned 2 to 7 mm tube set and the 5/8 in tube already ordered; there is no house and no glass.

Incoming checks, in `FINAL_BUILD.md` beside each part: the motor's shaft is a 3 mm D and it runs at 3 V; the
filament lights on the diode test with the holed tab as +; the reed closes 2 mm from the magnet; the charger's
jumper is cut before the cell meets it; the tray's leads are metered for polarity with the cell in; the check
ring's thickness and the vase cap's height are measured and the script rerun (the cap now also takes three rod holes); the coaster's hollow is measured
(the charger wants 4.8 mm and the controller 5.3; if it is shallower the boards move into a bigger house) and a
magnet does not stick to its top.
