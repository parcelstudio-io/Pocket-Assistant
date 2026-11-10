# Crumb Rev C: the order (Rev C approved 2026-11-09; Rev B approved and ordered 2026-11-08)

**Nothing to buy for Rev C as drawn; one 8×8 ranger to buy just in case, decided 2026-11-10 (its section below).** Rev B's three lines were ordered on 2026-11-08 and stay ordered; no cart or order is touched. On 2026-11-09 the
builder took the lidar off Crumb (and off the rover): it is too big for a small, cute desk robot. Where each Rev B line goes now:

| Line | Ordered | Rev C, 2026-11-09 |
| --- | --- | --- |
| Adafruit bq25185 charger with 5 V boost (6106) | DigiKey sales order 102777448, $15.18, shipped 11-09 by USPS, about 11-12 to 11-14 | **Stays Crumb's.** Its charger (500 mA, about 2.2 h, toggle on) and its 5 V rail, now for the XIAO (through the Schottky) and the amplifier only: 250 mA typical, 630 peak of its 1 A. The boost is still in use. |
| LDROBOT LD19 lidar, the youyeetoo FHL-LD19 kit | Amazon order 114-7956116-1377847, $86.43 with the MOSFETs, arriving 2026-11-09 | **No longer Crumb's.** To the shared bin in its box, unallocated until the builder names a project. Not the XS drone: 47 g on a 34 g drone with a thrust-to-weight of 2.0 cannot fly. |
| P-channel MOSFET AO3401A, Bridgold 100-pack | the same Amazon order | **No longer Crumb's.** It was the lidar's switch; all 100 spare, to the shared bin. |
| K&S 0.005 in brass sheet, 6-pack | skipped 2026-11-08, in Amazon's Saved for Later | Unchanged: the skins, whenever they are wanted. |

Not needed any more for Crumb: the AO3400A N-MOSFET from the drone's pack (it drove the lidar switch; it stays in the drone bin), the 1 kΩ,
the 100 kΩ, one 10 kΩ, the 100 µF and one 100 nF.

## Just in case, 2026-11-10: one 8×8 ranger

The builder asked whether Crumb can roam the desk without falling off on the single-zone ranger alone, and whether it could push small
things while seeing tens of centimetres ahead. The answers are in `CRUMB_BUILD.md` under Risks: head-on yes, the edge seen 74 mm
before the wheels; edges almost alongside and anything behind are the drive loop's rules; one zone aimed along a desk cannot pick out a
low object 30 cm away. The one part that covers both wheel tracks and looks 30 cm ahead is an 8×8 ranger on the brow, so one goes on the
list just in case. The owned spare is the Mars rover's since Rev J (2026-11-09). Not on Amazon (searched 2026-11-10); the US channel is
DigiKey Marketplace, shipping from Pololu, where the first pair came from.

| ☐ | Qty | Part | Buy here | Price | Fallback | Must be genuine? |
| --- | ---: | --- | --- | ---: | --- | --- |
| ☐ **in the DigiKey cart since 2026-11-10 03:00** (web ID 379101217), a guest cart in the Claude browser pane, not the builder's account (log in there and DigiKey merges it, or add the part in your own browser); $19.95 + $9.95 Pololu marketplace shipping = $29.90 before tax; checkout the builder's | 1 | Pololu **VL53L7CX 8×8 laser ranger carrier** (60° × 60°, 3.5 m, 20 mm minimum, 100 mA typical, 13 × 18 × 3 mm) | [DigiKey Marketplace 2183-3418-ND](https://www.digikey.com/en/products/result?keywords=2183-3418-ND), ships from Pololu by USPS; [Pololu 3418](https://www.pololu.com/product/3418), 277 in stock on 2026-11-09 | $19.95 + post | the black [Pimoroni VL53L5CX](https://shop.sb-components.co.uk/products/vl53l5cx-8x8-time-of-flight-tof-array-sensor-breakout) from the UK, $33 + post, 45° field (it covers the wheel tracks only from 80 mm out) | Pololu's own board: its regulator and logic levels are what the drone's and the rover's sheets assume; a bare module would need its own 3.3 V and 1.8 V |

Where it would go: the brow beside the lens, about 20° down, LPn on the free D2, on the 3V3 rail (100 mA typical, 150 peak), the edge
ranger re-addressed to 0x2A at boot while the 8×8 is held off the bus. Not drawn: a Rev D, if the first rolls say the step-and-look
roaming is too timid or the pushing wants eyes.

## When the boxes come (Rev C)

- Caliper the two gears now (outer diameter, bore, plate thickness, length over the boss; a grub screw in the boss?): the axle
  height and the width follow them. Write the numbers into `pages/gen/crumb_build.py` and regenerate.
- 6106: cut the charge-rate jumper on the back first, then meter 5.0–5.2 V on the 5 V pads with only a cell on BAT. If a terminal
  block comes soldered, unsolder it: the board must stay under 12 mm tall on the tail floor.
- The lidar kit and the MOSFET pack (Amazon, 11-09): log the pick-up as usual, then put both, unopened, in the shared bin. Nothing of
  them goes into Crumb. Whoever takes the lidar next can prove it with a scan on the PC through the kit's USB adapter.
- Brass sheet, if bought: cut the skins to the table in `CRUMB_BUILD.md`; spray before fitting.

## Rev B's order, 2026-11-08 (the record)

**All 3 lines ordered on 2026-11-08, about $102 with post and tax.** The charger-boost from DigiKey (sales order 102777448, $15.18, shipped 11-09 by USPS, about 11-12 to 11-14); the lidar kit and the MOSFET pack from Amazon (Amazon order 114-7956116-1377847, $86.43 with tax, arriving 2026-11-09). The brass sheet was skipped the same day: the first build runs without skins. The builder had asked on the evening of 2026-11-07 whether everything for Crumb was
bought: everything for Crumb as drawn on 10-31 was in the bin or in the mail (the XIAO, by 11-11). No lidar had been bought, for
Crumb or for Mochi, and the lidar brought the charger-boost and its switch with it; the skins bring one sheet of brass. Vendor order
per the house rule: Amazon first, then DigiKey, then Adafruit.

| ☐ | Qty | Part | Buy here | Price | Fallback | Must be genuine? |
| --- | ---: | --- | --- | ---: | --- | --- |
| ☑ **ordered 2026-11-08**, Amazon order 114-7956116-1377847, arriving 11-09; **no longer Crumb's (Rev C)** | 1 | LDROBOT LD19 lidar as the **youyeetoo FHL-LD19 kit** (sensor, pigtail, USB adapter, Dupont leads) | [Amazon B0B1QCV4XR](https://www.amazon.com/dp/B0B1QCV4XR), ships from Amazon, free delivery next day | $71.90 | the STL-19P as the [Waveshare D500 kit on Amazon](https://www.amazon.com/dp/B0CNCLQ68L) was $117.99 with a Nov 23 delivery on 2026-11-08; [Waveshare direct $95.99](https://www.waveshare.com/d500-lidar-kit.htm) · [Hiwonder $99.99](https://www.hiwonder.com/products/stl-19p-d500-lidar) | Yes: an LDROBOT unit (LD19 or STL-19P); the youyeetoo kit is the LD19 with its adapter. Other look-alikes have other protocols. |
| ☑ **ordered 2026-11-08 15:15**, DigiKey sales order 102777448 (web ID 379032068), USPS Ground Advantage, $15.18 | 1 | Adafruit **bq25185 USB-C charger with 5 V boost** (6106) | [DigiKey 1528-6106-ND](https://www.digikey.com/en/products/detail/adafruit-industries-llc/6106/25805552), $8.95 + $4.99 USPS Ground Advantage, about Nov 13 | $15.18 all in | [Adafruit](https://www.adafruit.com/product/6106) $8.95 + post, about $16 · **Amazon's only match** is a no-name 2-pack, [B0H2BHTZBM](https://www.amazon.com/dp/B0H2BHTZBM), $38, free delivery Nov 24, one rating, same layout in the photos (USB-C, JST, terminal block, VIN VU D− D+ G BAT 5V EN pads) · Micro Center Brooklyn stocks the Adafruit board | The genuine board is the one the sheet was checked against; the clone's jumper and EN pad are unverified. |
| ☑ **ordered 2026-11-08**, Amazon order 114-7956116-1377847, arriving 11-09; **no longer Crumb's (Rev C)** | 1 pack of 100 | **P-channel MOSFET AO3401A, SOT-23** (−30 V, −4 A, on at Vgs −4.5 V), marked A19T | [Amazon, Bridgold 100-pack](https://www.amazon.com/dp/B09WN8WP8M), next day | $7.49 | DigiKey 785-1001-1-ND at $0.52 each | No; any P-MOSFET meeting the line. |
| — skipped 2026-11-08 | 1 pack of 6 | ~~**K&S 250 brass sheet**, 0.005 in, 4 × 10 in~~ (the skins; the first build is bare) | [Amazon B0006N6WLM](https://www.amazon.com/dp/B0006N6WLM), SIM Supply, $24.54, moved to Saved for Later | — | other sellers from $23.49; single sheets at True Value; the hologram's build day still carries the line | No. |

Not bought, on purpose: Mochi's round screen and Pololu wheels (Mochi is set aside; the square screen and the gears are owned), a second
cell charger (the 6106 charges in 2.2 h on the lead), M2 screws, super glue (the hubs are dimpled onto the shafts), cardstock (none
anywhere), the return of the owned 8×8 ranger (it is the rover's now; Crumb's own is the just-in-case line above).

## Carts, 2026-11-08

- **DigiKey: ordered.** The builder checked out the cart on 2026-11-08 at 15:15: sales order 102777448, web ID 379032068, 1 ×
  1528-6106-ND, $8.95 + $4.99 USPS Ground Advantage + $1.24 tax = $15.18, Visa, shipping from Thief River Falls; expect it about
  11-12 to 11-14, shipped 11-09 by USPS (the pick-up log records the arrival). The cart page now shows the receipt, which is why the cart looks empty. DigiKey has no free-shipping threshold for US orders (its delivery page, read 2026-11-08, prices every method per
  shipment: USPS Ground Advantage $4.99, FedEx or UPS Ground $8.49, 2nd Day $13.99 and up). The AO3401A line was deleted from it once the Amazon 100-pack went in the Amazon cart.
  The Claude pane's guest cart still shows both lines and can be ignored. DigiKey does not list the Waveshare D500 or any LDROBOT
  lidar (searched 2026-11-08).
- **Amazon: ordered.** The builder checked out at about 15:55 on 2026-11-08: Amazon order 114-7956116-1377847, $86.43 with tax, free delivery 2026-11-09,
  the lidar kit and the MOSFET pack. The lines had been added through the builder's own Chrome earlier that afternoon: the
  [youyeetoo FHL-LD19 kit](https://www.amazon.com/dp/B0B1QCV4XR) at $71.90 (next-day) and the
  [K&S 0.005 in brass sheet 6-pack](https://www.amazon.com/dp/B0006N6WLM) at $24.54 (Nov 12–13); then the [AO3401 100-pack](https://www.amazon.com/dp/B09WN8WP8M) at $7.49 (next day); the brass sheet went in too and came out again when the builder skipped the skins (it sits in Saved for Later); cart subtotal $79.39 for the two items.
  Not added: the [Waveshare D500 kit](https://www.amazon.com/dp/B0CNCLQ68L), $117.99 with a Nov 23 delivery that day.
- **The one line that would not move to Amazon cleanly (asked 2026-11-08):** the charger-boost. Amazon has only the $38 no-name
  2-pack above, arriving Nov 24 (DigiKey about Nov 12 for $22.89 all in; Adafruit about $16). The free PowerBoost 1000C copy in
  the drawer (the camera Pocket AI leaves its one unused) was looked at and set aside: it is 36 × 23 mm, so on Crumb's tail floor
  it can lie only across the body, which points its micro-USB charging port sideways behind a gear; standing it on the tail wall
  points the port up or down through the floor. It also charges at a fixed 1 A and is unverified. **Decided 2026-11-08: the
  charger-boost stays on DigiKey, the genuine board, $15.18 all in by USPS; the Amazon 2-pack is not bought.**
- **Adafruit:** the fallback for the charger-boost if DigiKey's line goes out of stock.

## Purchase check, 2026-11-09 (the Amazon, DigiKey and Adafruit order mails)

The builder asked, before starting Crumb, whether every part has been bought. Yes: nothing is left to buy. Three parts are still in the
mail; everything else was delivered. The motion sensor had been carried as on hand since 11-07 ("ten older ones owned"), but the
ten-pack of 10-27 is not due until 11-19 to 12-15: the 3-pack arriving 11-09 is the one Crumb gets.

| Part | Order | Ordered | Status, from the mails |
| --- | --- | --- | --- |
| XIAO ESP32-S3 Sense | Amazon 114-5249290-9043412 | 2026-10-31 | **in the mail, arriving 11-11**: its Amazon order page, read 2026-11-10 03:30 EST ("Now arriving tomorrow", previously 11-15); no shipping mail, as usual for this seller |
| Adafruit bq25185 charger with 5 V boost (6106) | DigiKey sales order 102777448 | 2026-11-08 | **in the mail, shipped**: shipped 2026-11-09 by USPS Ground Advantage (DigiKey's mail 06:48 EST: invoice 136003544, tracking 9200190106460365547930); about 11-12 to 11-14 |
| GY-521 motion sensor, 3-pack | Amazon 114-1259113-3701002 | 2026-11-06 | **in the mail**: the order mail of 11-07; Amazon's Orders page (read 11-09) says arriving 11-09; no shipping mail yet |
| 1.54" screens ×3, N20 motors ×2, steel gears ×2, Qwiic motor driver, MAX98357A ×3 | Amazon 114-6045175-2593056 | 2026-10-31 | on hand: Amazon's delivery mails of 11-03, picked up 11-03 |
| MAX98357A amplifiers, nine more | Amazon 111-8554202-0502625, 114-5029591-3604223 | 09-02, 10-11 | on hand |
| VL53L1X edge ranger | DigiKey marketplace (Pololu) 102531268 | 2026-10-27 | on hand: shipped 10-28 (invoice 135297191), at the front desk 11-02, picked up 11-03 |
| MAX17048 fuel gauge (two bought) | Adafruit 3771280 | 2026-10-26 | on hand: shipped by UPS 10-27, delivered 10-28 |
| 100 mm QT cables ×7, QT-to-header cables ×2 | Adafruit 3765988 | 2026-10-19 | on hand: shipped by UPS 10-20, at the front desk 10-21 |
| Same Sky speaker | DigiKey 101368762, 101971685 | 09-02, 10-01 | on hand |
| 16340 holder, MTS-102 toggle | Amazon 114-1421763-3353854 | 2026-10-27 | on hand: delivered 10-30 |
| SS14 Schottky diodes ×100 | Amazon 114-5201101-3840264 | 2026-10-27 | on hand: delivered 10-30 (the GY-521 ten-pack in the same order is due 11-19 to 12-15) |
| Nitecore NL169 16340 ×13 | IMR Batteries 20739060, 20739061 | 2026-10-16 | on hand: delivered 10-21 |
| JST-PH pigtails (20 pairs), resistor, ceramic and electrolytic kits | Amazon 111-8554202-0502625, 111-6329624-3227449 | 2026-09-02 | on hand: delivered 09-03 and 09-04 |
| 1.0 mm brass rod | Amazon 111-4723174-9565024, 114-8041650-5363423, 114-1256902-8439449 | 09-02, 10-07, 10-10 | on hand: delivered 09-04 and 10-12; four rods needed, count the drawer |
| 4 and 5 mm brass tube | Amazon 114-9676073-9134626 | 2026-10-26 | on hand: delivered 10-28 |
| Canvas-white spray, Kapton, white heat-shrink, white silicone wire, hot glue | Amazon, Pip's stock | 2026-09-02 | on hand |
| K&S 0.005 in brass sheet (the skins, optional) | not bought | — | skipped 2026-11-08; the first build runs without skins |

Checked from the order mails alone: DigiKey's site and cart were left alone, since the rover session works in the same Chrome's DigiKey cart.
