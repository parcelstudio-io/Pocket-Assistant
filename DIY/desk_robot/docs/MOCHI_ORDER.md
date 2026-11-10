# Mochi: the order (2026-11-07, after approval; Rev B, the gears, approved the same evening)

**Four lines, about $121 before shipping and tax.** Rev B is the build: Crumb's two steel gears are the wheels, so the Pololu
pair (Rev A's wheels, $4.45) is not bought; its line stays below, struck, in case the gears ever come off. The Globact gear
listing the builder pasted on the evening of 11-07 is this same owned part, two of them in Crumb's bin: nothing to add to any
cart for the wheels. Vendor order per the house rule: Amazon first, then DigiKey, then Adafruit; Pololu only for the white wheels, which nobody else sells in
white. Everything else is owned (`MOCHI_BUILD.md`, Parts). I cannot fill a cart; the links are the exact listings. Mark each line
with the order number and the date when it is placed.

| ☐ | Qty | Part | Buy here | Price | Fallback | Must be genuine? |
| --- | ---: | --- | --- | ---: | --- | --- |
| ☐ | 1 | LDROBOT STL-19P lidar as the **Waveshare D500 kit** (sensor, ZH1.5 pigtail, USB adapter) | [Amazon B0CNCLQ68L](https://www.amazon.com/dp/B0CNCLQ68L) (price not read by me; the page blocks agents) | about $96 | [Waveshare $95.99](https://www.waveshare.com/d500-lidar-kit.htm) · [Hiwonder $99.99](https://www.hiwonder.com/products/stl-19p-d500-lidar) · the older [D300 / LD19](https://www.amazon.com/dp/B0B1QCV4XR) is the same housing at 180 mA | Yes: an LDROBOT unit (STL-19P or LD19). Other "D500" look-alikes have other protocols. |
| ☐ | 1 | Waveshare **1.28" round LCD**, GC9A01, 240 × 240, PH2.0 8-pin lead | [Amazon B08V5538C6](https://www.amazon.com/dp/B08V5538C6) (price not read) | about $15 | [Waveshare $14.99](https://www.waveshare.com/1.28inch-lcd-module.htm) · PiShop $16.95 · the [DIYables one](https://www.amazon.com/dp/B0F9NY6JZ6) ($14.99) has no backlight pin and a square board: second choice | Prefer Waveshare for the round board and the BL pin. |
| ☐ | 1 | Adafruit **bq25185 USB-C charger with 5 V boost** (6106) | [DigiKey 1528-6106-ND](https://www.digikey.com/en/products/detail/adafruit-industries-llc/6106/25805552) | $8.95 | [Adafruit](https://www.adafruit.com/product/6106) $8.95 · Micro Center Brooklyn stocks it (SKU seen for Cyber Dawn) | Yes, the Adafruit board: the jumper, EN pad and power path are what the sheet uses. |
| ☐ | 1 (buy a few) | **P-channel MOSFET, SOT-23**, AO3401A or equal (−30 V, −4 A, on at Vgs −4.5 V) | [DigiKey, search AO3401A](https://www.digikey.com/en/products/result?keywords=AO3401A) | under $1 | any Amazon SOT-23 AO3401 multi-pack | No; any P-MOSFET meeting the line. |
| — | ~~1 pair~~ · Rev A only, not bought | ~~**Pololu wheel 32×7 mm, white** (#1088)~~ | [Pololu](https://www.pololu.com/product/1088) | $4.45 | none in white elsewhere; the black pair is on Amazon if colour stops mattering | Pololu's own. Not bought if Rev B's gears are the wheels. |

Ship together where it saves a box: the 6106 and the MOSFET in one DigiKey order; the lidar and the screen in one Amazon
order; the wheels, if Rev A, from Pololu alone (small, first class).

## The gears are on the bench: caliper them first

Before any brass is cut, caliper the two
[64-tooth steel gears](https://www.amazon.com/dp/B0881RWD2L) from Crumb's box: outer diameter (the seller draws 40; 39.6 by the
0.6 module), bore (5.0), plate thickness, length over the boss (9), and whether the boss carries a grub screw. The build page
draws the seller's numbers; the axle height is the radius plus 0.5 and the width 2 × (29.5 + the length over the boss), so the
numbers go into `pages/gen/mochi_build.py` (`WHEELS["gear"]`) and the page regenerates. The hubs are owned stock: 9 mm of 4 mm
and 9 mm of 5 mm tube per wheel from the [METERXITY set](https://www.amazon.com/dp/B0F2FKLC2N), telescoped and soldered.

A brass gear would match the hoops: Kyouiku's S50B60B+0203 (module 0.5, 60 teeth, Ø31, 3 mm bore, 2 mm face, Ø10 hub, locking
screw not included) would drop into Rev A's geometry unchanged with brass teeth. [RS Components](https://uk.rs-online.com/web/p/spur-gears/5032248)
lists it as currently unavailable and [Accu's US page](https://accu-components.com/us/spur-gears/761155-S50B60B+0203) refused my
fetch, so its price and stock are unread; a pair would likely cost more than the whole Pololu order and ship from the UK. A note,
not a line.

Not bought, on purpose: M2 screws (the flange is hot-glued to its rods), brass sheet, anything printed, a second cell charger (the
6106 charges in 2.2 h on the lead). Super glue: Crumb's hub recipe wanted a drop and the bench has none; the Rev B page dimples the
inner tube onto the shaft's flat instead, and a $4 tube from any store is the fallback if that does not hold.

## When the boxes come

- Lidar: caliper the flange (drawn 54 × 46.3 × 1.3, read from the LD19 drawing) and the body (38.6); write the numbers into
  `MOCHI_BUILD.md`; the two cross rods and the top skin's hole follow them. Plug it into the kit's USB adapter and watch a scan
  on the PC before it goes anywhere near the robot.
- Screen: confirm the 8-wire order on its lead against the sheet (VCC GND DIN CLK CS DC RST BL) and that BL high lights it.
- 6106: cut the charge-rate jumper on the back first, then meter 5.0–5.2 V on the terminal block with only a cell on BAT.
- Gears (no box, they are here): hub soldered and pressed in, spin each gear on a motor shaft; true it until the rim
  wobbles less than half a millimetre before the hoops close.
- MOSFET: read the marking; the AO3401A is marked "A19T".
