# Buy list

**Ordered 2026-10-31 evening (two Amazon orders, below). The cart review and the Ø40 redraw came first.** All seven
lines are Prime from Amazon, so one order and no shipping charge; nothing needed DigiKey or
another vendor. Every other part is owned (see the parts table in `DESIGN.md`). The 1.3" OLED
first placed in the cart was swapped the same evening for the colour IPS screen, which in turn
needed the I²C motor driver to free four pins. Later the same evening the spoked brass wheels
gave way to Mo-chan-style steel gear wheels: the O-rings left the cart and two gears went in. At the
review before ordering, the gear listing's drawing showed the gear is Ø40 (0.6 module), not the Ø52.8
the design had assumed; the design was redrawn for Ø40 and the cart did not change.

## Ordered, and when it lands

| Order | Placed | Arrives | Items | Total |
| --- | --- | --- | --- | --- |
| 114-6045175-2593056 | 2026-10-31 | **delivered Tue 2026-11-03** 12:53, three boxes at the front desk (Amazon mails; building log); sorted the same afternoon — **delivered and picked up 2026-11-03** | N20 motors 2-pack · MAX98357 3-pack · SparkFun Qwiic motor driver · Globact 64T gear ×2 · Hosyond 1.54" IPS 3-pack | $86.25 |
| 114-5249290-9043412 | 2026-10-31 | **by 2026-11-11** (Orders page 11-03; was 11-15, then 11-08 to 11-11) | Seeed XIAO ESP32-S3 Sense | $26.12 |
| 114-2645785-1488244 (earlier, shared stock) | 2026-10-30 | 2026-11-13 to 11-19 | 4 × METERXITY 330 mm brass tube sets (2–7 mm). The hub tubes; the set bought 2026-10-26 should already be in the drawer, so this order is not on the critical path | $67.67 |

Not ordered: the gel cyanoacrylate (the Loctite in Saved for later); solder the hub to the shaft flat, or add it to a later order.
Bench tools from the same evening, the Uvex safety glasses (114-8031860-5409814, $13.01) and the 15× magnifying lamp (114-0252936-2851446, $69.34): **delivered and picked up Sun 2026-11-01** (Todoist task completed 6:36 p.m.).

Check this table against the Orders page when a box arrives; mark each row delivered with the date. Shared parts read 2026-11-03: the two laser rangers (Pololu, USPS) are at the front desk since 11-02; the fuel gauge, speaker, cell, holder, toggle and QT cables are on hand; the motion sensor pack is 11-19 to 12-15. The sorting list is `../../PARTS_BY_PROJECT.md`.

## What was in the cart

| Qty | Part | Listing | Price | Delivery shown | Why this one |
| ---: | --- | --- | ---: | --- | --- |
| 1 | Seeed XIAO ESP32-S3 Sense | [B0C69FFVHH](https://www.amazon.com/dp/B0C69FFVHH), Seeed official | $23.99 | Nov 10–15 | The brain, camera, mic and charger. The three owned boards are the tower's, the drone's and the Sphere's. The slow line of the order. |
| 1 (3 screens) | Hosyond 1.54" IPS TFT 240 × 240, ST7789, SPI, 3.3 V, 3-pack | [B0HGLQZK3P](https://www.amazon.com/dp/B0HGLQZK3P) | $15.99 | Sun Nov 1 | The face: colour, 220 ppi, fast SPI. Same brand as the owned OLEDs. Two spares for other builds. |
| 1 | SparkFun Qwiic Motor Driver, I²C, 2 × 1.2 A | [B07YCVHQD5](https://www.amazon.com/dp/B07YCVHQD5) | $23.75 | Mon Nov 2 | Drives both N20s over I²C so no GPIO goes to motors; that is what pays for the screen's four pins. Screw terminals, Qwiic socket, 3–11 V in. Only 5 in stock at the time. |
| 1 (2 motors) | JUZITAO N20 gear motor, 6 V 100 rpm, 3 mm D-shaft, 2-pack | [B0C9QC4SRY](https://www.amazon.com/dp/B0C9QC4SRY) | $9.99 | Sun Nov 1 | Both drive motors. 60–70 rpm unloaded at the cell's voltage, about 50 under load: about 10 cm/s on the Ø40 gears. 1:100 gearbox. Only 2 reviews; N20 motors are a commodity and the bench test logs stall current before anything is built. |
| 2 | Globact 11184 steel spur gear, 64T, 0.6 module, Ø40, 5 mm bore, 9 mm over its boss (each with four spare pinions) | [B0881RWD2L](https://www.amazon.com/dp/B0881RWD2L) | $9.98 each | Mon Nov 2 | The wheels. Same HSP 11184 gear as ShareGoo [B075NYPT43](https://www.amazon.com/dp/B075NYPT43) ($8.98, 4.1 of 218, tomorrow) and Hobbypark [B01CA49O32](https://www.amazon.com/dp/B01CA49O32) ($9.97, 4.1 of 533, Monday); Globact has the best rating, 4.4 of 267. Hub from owned 5 mm and 4 mm brass tube. |
| 1 (3 boards) | HiLetgo MAX98357 I²S amplifier, 3-pack | [B0CDWXZZCH](https://www.amazon.com/dp/B0CDWXZZCH) | $9.49 | Sun Nov 1 | Covers this robot and the one-board shortfall across the tower, the Sphere and Cyber Dawn, with one spare. Same board the other builds use. |
|  | **Subtotal** |  | **$103.20** |  | before tax, 7 items |

## Deliberately not added

- **MX1508 driver.** Owned, four spare; not used here because its four PWM inputs cost the pins the screen needs.
- **uxcell O-rings** ([B07W85RFY6](https://www.amazon.com/dp/B07W85RFY6)). Were the tyres for the spoked wheels; removed when the gears replaced them. Put back only if the steel teeth slip on the desk.
- **K&S 1.0 mm and 1.5 mm brass rod** ([B005WPB7YG](https://www.amazon.com/dp/B005WPB7YG),
  [B01C6LUO5Q](https://www.amazon.com/dp/B01C6LUO5Q)). The 1.5 mm listing shows seven purchases, the
  latest 2026-10-28, which the inventories do not record, so the drawer likely holds more than the
  five rods logged. Count before cutting the Sphere's rings and this robot's two rims; add a pack
  only if the count is short.
- **External 16340 charger** (Nitecore UI1 or XTAR VC2, about $10–15). Optional, shared with the
  tower and the Sphere; the XIAO charges the cell over USB-C in about 10 h.
- **Gel cyanoacrylate.** The hub recipe wants a drop on the shaft flat and none is in the inventories
  (the Pip list carries it as "optional, still needed"). The Loctite Ultra Gel in Saved for later covers
  it; or solder the hub to the shaft flat instead.
- **Brass ball for the skid.** A dome soldered onto the end of the owned 4 mm brass tube does the
  job; buy a 5 mm brass ball only if the dome drags.

## When the box arrives

- XIAO Sense: cut jumper J3 on the camera board before anything else.
- Screen: note the 8-pin order on the header (GND, VCC, SCL, SDA, RES, DC, CS, BLK on most of these); it is 3.3 V only.
- Motor driver: default address 0x5D. Cut its I²C pull-up jumper (the bus already has 10 kΩ sets on three boards). Meter VIN polarity on the screw terminal before the cell.
- Motors: measure the shaft (3 mm D), the body length (about 24 mm with the gearbox) and the stall
  current at 3.7 V on the bench supply.
- Gears: caliper the outer diameter (the listing's drawing says 40), the bore (5.0), the plate thickness and the boss length (9 overall); spin each on a 5 mm pin and look for wobble before making the hubs. If the diameter is not 40, the axle height and the motor cradles in `DESIGN.md` move with it.
