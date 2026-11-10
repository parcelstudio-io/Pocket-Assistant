# Parts by project, for sorting into bins

Read on **2026-11-03**: Amazon Orders page, signed in, 207 orders back to 2026-08-03, read 06:17 to 06:28 EST; Gmail (DigiKey, Adafruit, UPS and IMR Batteries mails) and the building's package log, read 06:20 to 06:27 EST, and again at 17:15 EST for today's Amazon deliveries; Todoist, label package: 3 completed pick-up tasks (all 2026-11-01), 0 open, read 06:20 EST; re-read 17:15 EST, when the four 11-02 tasks showed completed at 15:00. DigiKey account (Order History, the invoice list and the three order pages), signed in by the builder, read 06:45 to 06:49 EST; Adafruit account (Order History and its three order pages), signed in by the builder, read 06:46 to 06:48 EST. DigiKey marks only its own FedEx shipments delivered and Adafruit only its October 26 order, so the building's front-desk log settles the rest. One section per project, one table each; a part shared by several builds appears under each with "n of m owned" so the bins can be split. Every part is named by what it is, with the exact listing bought linked on the name; order numbers sit in the From column.

Printable page (US Letter, black and grey): [https://claude.ai/artifact/E2PSC4iZ7cr86nwhN6DWsc](https://claude.ai/artifact/E2PSC4iZ7cr86nwhN6DWsc); the file is `reports/parts-by-project.html`, generated with the markdown by `reports/gen/parts_by_project.py`.

## Still missing

- XIAO ESP32-S3 Sense boards: none on hand. Crumb's and the drone's are now expected by 11-11, the pair for the camera Pocket AI and the Sphere by 11-15.
- Crumb's main box (motors, gears, driver, screen, amplifiers) and the hologram's filament pack: due today, 11-03, not delivered at 06:17.
- Desk satellite: nothing left in the mail. The chips (11-04) and wings (11-05) were picked up 11-05 and are in the satellite bin (sorted 11-07); the steel disc came 11-06 and is spare, in the satellite bin for now. The brass coaster that replaced the disc as the base was ordered 11-06 (delivered 11-09 to the mail room) and given to the desk lighthouse on 11-09; the satellite's is in the builder's Amazon cart since 11-09 evening, not ordered. The Eujgoov fallback panels were cancelled.
- Desk lighthouse: everything on Amazon ordered 2026-11-09 04:22 EST in one checkout of five orders ($122.64): the reed switches, acrylic tube, gearmotors and magnets shipped the same day for Wed 11-11, the gel glue comes 11-14, the 5/8 in tube 11-18 to 11-20 (the brass sheet's order: cancelled by the seller, not charged), the LED filaments 11-27; the brass coaster (bought 11-06 as the satellite's) was delivered 11-09 to the mail room; the five Grand Brass lamp parts are ordered by the builder's word with no confirmation mail yet; the bq25185 charger is not ordered (the 11-09 DigiKey order is the rover's). These five Amazon orders were first logged as the rover's. That evening the builder rejected the acrylic tube (to return) and dropped the brass sheet (its order came back cancelled by the seller, not charged): Rev D, open lantern and no house, awaits approval.
- Desk hologram: beam-splitter cube 11-08.
- Pocket AI with camera: both gear motors came early and were at the bench 2026-11-03; no delivery mail, the Orders page had 11-05 to 11-16.
- XS drone (Orders page read 11-09): controller 11-08 to 11-11; LED regulators, the motion-sensor 3-pack and the clear heat tape all arriving 11-09; motors and propellers 11-13 to 11-24; the 10-pack 11-19 to 12-15 is spare; the 0.01 g scale was dropped the same day (the hover test is the thrust gate). Since 11-09 one line is open again: the speaker's amplifier board (PAM8403 5-pack), in the builder's Amazon cart since that evening, not ordered.
- Not bought: Cyber Dawn's acrylic face and PETG; the satellite's three printed parts; the optional external 16340 charger; the hologram's optional card and epoxy; the drone's amplifier board (added 11-09, in the cart).

## What the accounts corrected

- IMR Batteries: the satellite inventory's "ordered 2026-11-03" cells are order 20739060 of 2026-10-16 (7 Nitecore cells and 12 IMREN 18350), delivered 2026-10-21, alongside order 20739061 (6 Nitecore cells) the same day. 13 cells are on hand; no November order exists in the mail.
- Eujgoov 110 × 60 mm panels (114-9697223-4179439): cancelled and not charged, not arriving 11-07.
- Cree LED stars (114-5101833-0385036): four in one order, delivered 2026-11-02, not two plus four.
- DigiKey (account read 06:45): invoice 135297233 shows Delivered on DigiKey's own page and reached the front desk 2026-11-02 18:07; the Pololu invoice 135297191 (USPS 9400150105496136143356) still shows Shipped there but was at the front desk 11-02 12:13 per the building log. The FedEx site itself rejects the number.
- Enclosed speakers: 6 owned, not 8. DigiKey's account holds three orders (09-02: four speakers; 10-01: two speakers with three climate and three proximity sensors; 10-28); the inventory's 09-21 order of five does not exist.
- Adafruit (account read 06:46): order 3771280 shows DELIVERED 2026-10-28; order 3765988 shows only Shipped there but was at the front desk 2026-10-21 (building log); the September order 3737700 (two 500 mAh and two 1200 mAh packs, the USB-C charger, a flux pen) is Pip's.
- XIAO boards: Crumb's (114-5249290-9043412) and the drone's (114-5295722-2709061) are now expected by 11-11; the pair (114-1888127-6908215) by 11-15.
- Three-set brass tube order 114-2647470-9786634: the Orders page said 11-03, but nothing came by the 13:44 desk log; the shipping mail's 11-06 to 11-13 stands.
- Unlogged stock found on the Orders page: six more amplifiers (2026-10-11), a second OLED 5-pack (10-22), a third microphone 5-pack (10-19), two power-path boards (10-11), seven packs of 1.5 mm tube, 18 packs of 1.5 mm rod, two DIYmall 16 MB dev kits (10-01, delivered 10-06), generic clock, accelerometer, encoder and 2.42 inch OLED modules (10-01).

## Crumb, the desk robot (`desk_robot`)

Nothing of Crumb's own has arrived yet. The main box with the motors, gears, driver, screen and amplifiers is due today; the controller lands by 11-11; the motion sensor now comes from a 3-pack ordered 11-07 instead of the 11-19 to 12-15 pack. The two laser rangers and the fuel gauge are shared parts already in the building.

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 1 | [controller with camera and microphone](https://www.amazon.com/dp/B0C69FFVHH) | Amazon 114-5249290-9043412, 2026-10-31 | in transit · arriving 2026-11-08 to 11-11 (Amazon Orders page, read 2026-11-09; was 11-15) | Crumb's own board. The other three boards are the drone's, the camera Pocket AI's and the Sphere's. |
| ☐ | 1 of 3 | [1.54 inch colour display, 3-pack](https://www.amazon.com/dp/B0HGLQZK3P) | Amazon 114-6045175-2593056, 2026-10-31 | on hand · delivered to the front desk 2026-11-03 12:53 (Amazon mails; building log 12:59 to 13:41), Crumb's order in three boxes with the LED filaments riding in the gears' box; sorted at the bench the same afternoon | Two spare screens for other builds. |
| ☐ | 2 | [64-tooth steel spur gears, one per listing](https://www.amazon.com/dp/B0881RWD2L) | Amazon 114-6045175-2593056 | on hand · delivered to the front desk 2026-11-03 12:53 (Amazon mails; building log 12:59 to 13:41), Crumb's order in three boxes with the LED filaments riding in the gears' box; sorted at the bench the same afternoon | The wheels. Caliper the diameter on arrival; the pinions are spare. |
| ☐ | 2 (one pack) | [N20 gear motors, 2-pack](https://www.amazon.com/dp/B0C9QC4SRY) | Amazon 114-6045175-2593056 | on hand · delivered to the front desk 2026-11-03 12:53 (Amazon mails; building log 12:59 to 13:41), Crumb's order in three boxes with the LED filaments riding in the gears' box; sorted at the bench the same afternoon | Both drive motors. |
| ☐ | 1 | [I²C motor driver](https://www.amazon.com/dp/B07YCVHQD5) | Amazon 114-6045175-2593056 | on hand · delivered to the front desk 2026-11-03 12:53 (Amazon mails; building log 12:59 to 13:41), Crumb's order in three boxes with the LED filaments riding in the gears' box; sorted at the bench the same afternoon | Cut its pull-up jumper before it joins the bus. |
| ☐ | 1 of 12 | [I²S amplifier, 3-pack](https://www.amazon.com/dp/B0CDWXZZCH) | Amazon 111-8554202-0502625 (3, 2026-09-02) and 114-5029591-3604223 (6, 2026-10-11); 3 more in 114-6045175-2593056 | on hand · 9 delivered 2026-09-03 and 10-14; 3 more delivered 2026-11-03 with Crumb's box | Take one of the nine on hand. Pip, Cyber Dawn, the Sphere and the camera Pocket AI take one each; 12 in all once today's box lands. |
| ☐ | 1 of 2 | [8×8 laser ranger](https://www.pololu.com/product/3418) | DigiKey marketplace (Pololu), order 102531268, invoice 135297191, USPS | on hand · USPS box at the front desk 2026-11-02 12:13 (building log; DigiKey's page still says Shipped); picked up 2026-11-03 (pick-up task completed 3 p.m.) | The drone takes the other. None spare. |
| ☐ | 1 of 2 | [single-zone laser ranger](https://www.pololu.com/product/3415) | DigiKey marketplace (Pololu), order 102531268 | on hand · USPS box at the front desk 2026-11-02 12:13 (building log; DigiKey's page still says Shipped); picked up 2026-11-03 (pick-up task completed 3 p.m.) | The drone takes the other. None spare. |
| ☐ | 1 of 3 | [motion sensor, 3-pack](https://www.amazon.com/dp/B00LP25V1A) | Amazon 114-1259113-3701002, 2026-11-06 | in transit · arriving 2026-11-09 (Amazon Orders page, read 2026-11-09) | The drone takes one; one spare. Lands weeks before the 10-pack, which is now all spare. |
| ☐ | 1 of 2 | [fuel gauge](https://www.adafruit.com/product/5580) | Adafruit 3771280, 2026-10-26, UPS | on hand · delivered 2026-10-28 (Adafruit's order history and the building log) | Cyber Dawn takes the other. None spare. |
| ☐ | 1 of 6 | [enclosed speaker](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) | DigiKey 101368762, 2026-09-02 (4) and 101971685, 2026-10-01 (2) | on hand · DigiKey's pages say Delivered (FedEx 541958299829 and 545372714918) | Pip, the Sphere and the camera Pocket AI take one each; two spare. Six owned, not eight: no 09-21 order exists. |
| ☐ | 1 of 13 | [16340 cell, protected](https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery) | IMR Batteries 20739060 (7) and 20739061 (6), both 2026-10-16, UPS | on hand · both IMR boxes at the front desk 2026-10-21 (building log) | Five builds take one each; eight spare. |
| ☐ | 1 of 10 | [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) | Amazon 114-1421763-3353854, 2026-10-27 | on hand · delivered 2026-10-30 | Five builds take one each; five spare. |
| ☐ | 1 of 20 | [toggle switch](https://www.amazon.com/dp/B0CZ6XZ2P9) | Amazon 114-1421763-3353854 | on hand · delivered 2026-10-30 | Three builds take one each; 17 spare. |
| ☐ | 1 of 420 | [tactile button](https://www.amazon.com/dp/B0FHW6HMG4) | Amazon 111-8554202-0502625, 2026-09-02 | on hand · delivered 2026-09-04 | Every build takes one or two. |
| ☐ | 2 of 7 | [100 mm QT cables](https://www.adafruit.com/product/4210) | Adafruit 3765988, 2026-10-19, UPS | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | Cyber Dawn takes five, so none are spare: the four extra ordered on Amazon were cancelled. |
| ☐ | 2 + 6 | [10 kΩ resistors ×2; 220 µF, 100 µF, 10 µF, 1 µF and two 100 nF capacitors](https://www.amazon.com/dp/B0F4P352BB) | resistor kit (linked), electrolytic kit 111-6329624-3227449, ceramic kit 111-8554202-0502625, all 2026-09-02 | on hand · delivered 2026-09-02 and 09-04 | Pull the values; the kits stay in bench stock. |
| ☐ | about 4 rods | [1.0 mm brass rod, 5-packs](https://www.amazon.com/dp/B005WPB7YG) | Amazon 111-4723174-9565024 (09-02), 114-8041650-5363423 (10-07), 114-1256902-8439449 (10-10) | on hand · delivered 2026-09-04, 10-12, 10-12 | Shared brass; count the drawer before cutting. |
| ☐ | about 18 mm of 4 mm and 5 mm | [brass tube set, 2 to 7 mm, 200 mm](https://www.amazon.com/dp/B0F2FKLC2N) | Amazon 114-9676073-9134626, 2026-10-26 (3 sets) | on hand · delivered 2026-10-28 | The hubs. More 330 mm sets due 11-06 to 11-13 and 11-13 to 11-19 (shared stock). |
| ☐ | as needed | [26 AWG and 30 AWG silicone wire, Kapton, fish paper, heat-shrink](https://www.amazon.com/dp/B073RDGTPB) | bench stock, 2026-09-02 | on hand | See shared stock. |
| ☐ | 1, optional | [external 16340 charger](https://www.amazon.com/s?k=nitecore+ui1) | nothing bought | not ordered · optional | Shared with the Pocket AIs if it is ever bought. |
| ☐ | bench | [15× magnifying lamp](https://www.amazon.com/dp/B0GK845R6R) | Amazon 114-0252936-2851446, 2026-10-31 | on hand · delivered 2026-11-01, picked up 2026-11-01 | With the safety glasses (next row): Crumb's bench, already collected. |
| ☐ | bench | [safety glasses](https://www.amazon.com/dp/B0017D3UIS) | Amazon 114-8031860-5409814, 2026-10-31 | on hand · delivered 2026-11-01, picked up 2026-11-01 |  |

## XS drone (`xs_drone`)

The drone's electronics are all in the building: the DigiKey switches, lens and beepers came by FedEx and the Pololu rangers by USPS, both at the front desk on 11-02, the same day as the four flashlight emitters. The frame rod came in two boxes on 11-04 and 11-05. Still in the mail: motors, propellers, the regulators and the motion sensor; the controller lands by 11-11. Added 2026-11-09 for the voice build: a speaker from Pip's stock and an amplifier board to buy.

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 1 | [controller with camera and microphone](https://www.amazon.com/dp/B0C69FFVHH) | Amazon 114-5295722-2709061, 2026-10-27 | in transit · arriving 2026-11-08 to 11-11 (Amazon Orders page, read 2026-11-09; was 11-15) | The drone's own board. |
| ☐ | 4 fitted + 4 spare | [615 coreless motors, two 4-packs](https://www.amazon.com/dp/B09J236JJL) | Amazon 114-5815387-7733816, 2026-10-27 | in transit · 2026-11-13 to 11-24 |  |
| ☐ | 16 (four sets) | [31 mm four-blade propellers](https://www.amazon.com/dp/B09L4MXXCW) | Amazon 114-4118122-0736259, 2026-10-27 | in transit · 2026-11-13 to 11-24 |  |
| ☐ | 4 | [250 mAh 1S flight packs](https://www.amazon.com/dp/B0FCMLVCN2) | Amazon 114-5201101-3840264, 2026-10-27 | on hand · delivered 2026-10-30 | One per flight; also the floor pan. |
| ☐ | 2 of 30 pairs | [JST 1.25 mm 2-pin leads](https://www.amazon.com/dp/B0GW5WWZTY) | Amazon 114-3670533-2737853, 2026-10-27 | on hand · delivered 2026-11-01, picked up 2026-11-01 | Battery lead and charger lead. |
| ☐ | 1 of 3 | [motion sensor, 3-pack](https://www.amazon.com/dp/B00LP25V1A) | Amazon 114-1259113-3701002, 2026-11-06 | in transit · arriving 2026-11-09 (Amazon Orders page, read 2026-11-09) | Crumb takes one; one spare. Bought so the IMU step need not wait for the 10-pack (11-19 to 12-15), now all spare. |
| ☐ | about 0.3 m of 12 rolls | [clear heat tape, 10 mm](https://www.amazon.com/dp/B0BD84GGPV) | Amazon 114-0986744-9273034, 2026-11-07 | in transit · arriving 2026-11-09 (Amazon Orders page, read 2026-11-09) | The finish: battery and speaker straps; no card, no skins (builder's rule 11-09). Eleven rolls spare for any project. |
| ☐ | 4 of 100 | [Schottky diodes](https://www.amazon.com/dp/B079KJ46ZS) | Amazon 114-5201101-3840264 | on hand · delivered 2026-10-30 | The satellite takes one. |
| ☐ | 4 + 1 of 10 | [N-channel MOSFETs](https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089) | DigiKey order 102531269, invoice 135297233, FedEx Ground | on hand · DigiKey's order page says Delivered; FedEx box at the front desk 2026-11-02 18:07 (building log); picked up 2026-11-03 (pick-up task completed 3 p.m.) | The same box holds Cyber Dawn's three controller boards. |
| ☐ | 1 of 2 | [8×8 laser ranger](https://www.pololu.com/product/3418) | DigiKey marketplace (Pololu), order 102531268, invoice 135297191, USPS | on hand · USPS box at the front desk 2026-11-02 12:13 (building log; DigiKey's page still says Shipped); picked up 2026-11-03 (pick-up task completed 3 p.m.) | Crumb takes the other. |
| ☐ | 1 of 2 | [single-zone laser ranger](https://www.pololu.com/product/3415) | DigiKey marketplace (Pololu), order 102531268 | on hand · USPS box at the front desk 2026-11-02 12:13 (building log; DigiKey's page still says Shipped); picked up 2026-11-03 (pick-up task completed 3 p.m.) | Crumb takes the other. |
| ☐ | 1 of 2 | [narrow-spot lens](https://www.digikey.com/en/products/result?keywords=1066-1042-ND) | DigiKey order 102531269 | on hand · DigiKey's order page says Delivered; FedEx box at the front desk 2026-11-02 18:07 (building log); picked up 2026-11-03 (pick-up task completed 3 p.m.) | One spare. |
| ☐ | 1 of 10 | [piezo beeper](https://www.digikey.com/en/products/result?keywords=PS1240P02BT) | DigiKey order 102531269 | on hand · DigiKey's order page says Delivered; FedEx box at the front desk 2026-11-02 18:07 (building log); picked up 2026-11-03 (pick-up task completed 3 p.m.) | Nine spare for any project. |
| ☐ | 2 of 10 | [350 mA LED regulators](https://www.amazon.com/dp/B0CST7GZTN) | Amazon 114-4621584-3017007, 2026-10-27 | in transit · arriving 2026-11-09 (Amazon Orders page, read 2026-11-09; was 11-17 to 11-20) |  |
| ☐ | 1 of 4 | [cool-white LED star](https://www.amazon.com/dp/B00LWU5DWM) | Amazon 114-5101833-0385036, 2026-10-27 | on hand · delivered 2026-11-02 (Amazon; USPS at the front desk 12:14); picked up 2026-11-03 (pick-up task completed 3 p.m.) | Three spare. The record said two plus four; the account shows one order of four. |
| ☐ | about 300 mm of 20 rods | [1 mm stainless rod, two 10-packs](https://www.amazon.com/dp/B082ZNWQ5Q) | Amazon 114-7336723-5981056 and 114-1049705-6516238, 2026-10-27 | on hand · delivered 2026-11-04 and 11-05 (two "online seller" boxes at the front desk, building log); picked up 2026-11-05 (pick-up tasks); the builder named them 2026-11-07 | Rails, axles and bars: 277 mm, one rod. 19 spare. |
| ☐ | about 2 of 10 | [1.5 mm stainless coupons, 150 mm](https://www.amazon.com/dp/B082ZNMD46) | Amazon 114-6765566-8037841, 2026-10-27 | on hand · delivered 2026-10-29 | The four motor collars. The hologram takes one coupon, the satellite three. |
| ☐ | 4 × 100 Ω, 6 × 10 kΩ, 1 × 220 µF | [resistor kit and electrolytic kit](https://www.amazon.com/dp/B0F4P352BB) | Amazon 2026-09-02 | on hand |  |
| ☐ | as needed | [26 AWG silicone wire, Kapton, heat-shrink](https://www.amazon.com/dp/B07G2LRX68) | bench stock, 2026-09-02 | on hand |  |
| ☐ | 1 of 6 | [enclosed speaker, Same Sky](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) | DigiKey 2026-09-02 and 10-01 (Pip's stock) | on hand | Added 2026-11-09 for the voice build; one of Pip's two spares. On the pan's tail, grille up. |
| ☐ | 1 of 5 | [PAM8403 class-D amplifier board, 5-pack](https://www.amazon.com/dp/B0DYYX8DF9) | nothing bought; in the builder's Amazon cart since 2026-11-09 about 22:00 EST (B0DYYX8DF9, the version without the volume knob, $5.59, sold by YFUSET, 4 left) | not ordered · in the cart, the checkout is the builder's; added 2026-11-09 for the speaker, the drone's only open line | Under the pan at the nose, hidden as bought. Four spare. |
| ☐ | 1 | [USB-C LiPo charger, for the flight packs](https://www.adafruit.com/product/4410) | Adafruit 2026-09-01 | on hand | Pip's held part, shared. |

## Cyber Dawn, the alarm clock (`cyber_clock_v2`)

Every electronic part is in the building: the two Adafruit boxes reached the front desk on 10-21 and 10-28 and the controller board on 11-02. Still to buy: the acrylic face. To print: the body.

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 1 of 3 | [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) | DigiKey order 102531269, invoice 135297233, FedEx Ground | on hand · DigiKey's order page says Delivered; FedEx box at the front desk 2026-11-02 18:07 (building log); picked up 2026-11-03 (pick-up task completed 3 p.m.) | Two spare. Also on hand: two 16 MB variants from Amazon 114-3292680-1445046, delivered 2026-10-06 (linked in the notes below). |
| ☐ | 1 of 2 | [2.42 inch OLED display kit](https://www.adafruit.com/product/2719) | Adafruit 3765988, 2026-10-19, UPS | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | The hologram takes the other. |
| ☐ | 1 of 2 | [real-time clock](https://www.adafruit.com/product/5188) | Adafruit 3765988 | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | One spare. |
| ☐ | 1 of 10 | [coin cell, 10-pack](https://www.amazon.com/dp/B0D8T4C5PK) | Amazon 114-9008008-9870602, 2026-10-19 | on hand · delivered 2026-10-20 | Plus one Panasonic single from 114-6114435-1326638, likely delivered 2026-10-08. |
| ☐ | 1 of 2 | [rotary encoder with I²C adapter](https://www.adafruit.com/product/6310) | Adafruit 3765988 | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | One spare. |
| ☐ | 1 of a pair | [stereo speaker pair, 4 Ω 3 W](https://www.adafruit.com/product/1669) | Adafruit 3765988 | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | The second driver is the spare. |
| ☐ | 1 of 2 | [16 mm snooze button](https://www.adafruit.com/product/1505) | Adafruit 3765988 | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | One spare. |
| ☐ | 1 of 2 | [proximity and light sensor](https://www.adafruit.com/product/4161) | Adafruit 3765988 | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | Plus three SparkFun spares from DigiKey 2026-10-01 (keep them off the chain). |
| ☐ | 1 of 2 | [accelerometer](https://www.adafruit.com/product/2809) | Adafruit 3765988 | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | Plus a generic 5-pack from Amazon 114-0516847-5209826, delivered 2026-10-22. |
| ☐ | 1 of 5 | [temperature and humidity sensor](https://www.adafruit.com/product/4566) | Adafruit 3765988 (2) and DigiKey 2026-10-01 (3) | on hand · 2026-10-21 and October | The Sphere takes one; three spare. |
| ☐ | 1 of 2 | [QT-to-header cable](https://www.adafruit.com/product/4209) | Adafruit 3765988 | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | One spare. |
| ☐ | 5 of 7 | [100 mm QT cables](https://www.adafruit.com/product/4210) | Adafruit 3765988 | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | Crumb takes two; none spare. |
| ☐ | 1 of 12 | [I²S amplifier](https://www.amazon.com/dp/B0CDWXZZCH) | Amazon 2026-09-02 (3) and 2026-10-11 (6) | on hand · delivered 2026-09-03 and 10-14 | Three more came 2026-11-03 with Crumb's box. |
| ☐ | 1 of 25 | [slide switch](https://www.amazon.com/dp/B09R434VJQ) | Amazon 111-8554202-0502625, 2026-09-02 | on hand · delivered 2026-09-04 | The arm switch. |
| ☐ | 10 kΩ, 4.7 kΩ; 220 µF (in the display kit), 100 nF | [resistor kit and ceramic kit](https://www.amazon.com/dp/B0F4P352BB) | Amazon 2026-09-02 | on hand |  |
| ☐ | 1 of 2 | [charger board with 5 V boost](https://www.adafruit.com/product/6106) | Adafruit 3771280, 2026-10-26, UPS | on hand · delivered 2026-10-28 (Adafruit's order history and the building log) | The satellite takes the other. None spare. Cut the current jumper. |
| ☐ | 1 of 2 | [fuel gauge](https://www.adafruit.com/product/5580) | Adafruit 3771280 | on hand · delivered 2026-10-28 (Adafruit's order history and the building log) | Crumb takes the other. None spare. |
| ☐ | 1 of 13 | [16340 cell, protected](https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery) | IMR Batteries 20739060 and 20739061, 2026-10-16 | on hand · both IMR boxes at the front desk 2026-10-21 (building log) | Eight spare across the family. |
| ☐ | 1 of 10 | [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) | Amazon 114-1421763-3353854, 2026-10-27 | on hand · delivered 2026-10-30 |  |
| ☐ | 1 of 20 pairs | [JST-PH 2.0 mm pigtails](https://www.amazon.com/dp/B0F6T4LKDG) | Amazon 111-8554202-0502625, 2026-09-02 | on hand · delivered 2026-09-04 | The satellite takes one pair. Meter polarity. |
| ☐ | about 300 mm of 3 mm tube | [brass tube set, 2 to 7 mm, 200 mm](https://www.amazon.com/dp/B0F2FKLC2N) | Amazon 114-9676073-9134626, 2026-10-26 (3 sets) | on hand · delivered 2026-10-28 | The two cradles. 330 mm sets: three due 11-06 to 11-13 (114-2647470-9786634; the Orders page said 11-03 but nothing came by the 13:44 desk log), four 11-13 to 11-19 (114-2645785-1488244). |
| ☐ | 1 | [82 × 52 mm smoked acrylic front, 3 mm](https://sendcutsend.com/materials/acrylic/) | nothing bought | not ordered | After the bench fit check. |
| ☐ | 1 spool | [black PETG for the body, lid and rear panel](https://www.printedsolid.com/collections/1-75mm-petg) | nothing bought | not ordered | Print from shelf stock if a spool is there. |

## Pip, the Pocket AI Assistant (`pocket_ai_assistant`)

Pip's USB prototype has run since September, and every part is on hand, most of them in multiples. The final build's battery parts (two power-path boards, the 1200 mAh packs, the USB-C charger) are on hand too. The 14-gauge sterling for the silver rebuild reached the front desk on 11-02. Nothing to buy.

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 1 of 13 | [ESP32-C3 SuperMini controller, 10-pack](https://www.amazon.com/dp/B0F888JQ91) | Amazon 111-8554202-0502625, 2026-09-02; plus a 3-pack, 114-9058559-0123454, 2026-10-17 (linked in shared stock) | on hand · delivered 2026-09-04 and 10-18 | The hologram and the satellite take one each; ten spare. |
| ☐ | 1 of 10 | [0.96 inch OLED display, two 5-packs](https://www.amazon.com/dp/B09T6SJBV5) | Amazon 111-6329624-3227449 (09-02) and 114-8572576-9885850 (10-22) | on hand · delivered 2026-09-02 and 10-26 | The Sphere and the camera Pocket AI take one each; seven spare. The 10-22 pack was not in the inventory. |
| ☐ | 1 of 15 | [I²S microphone, three 5-packs](https://www.amazon.com/dp/B092HWW4RS) | Amazon 111-8554202-0502625 (09-02), 114-3696034-7495405 (10-19), 114-0550068-3533850 (10-23) | on hand · delivered 2026-09-04, 10-20, 10-24 | The hologram takes one; 13 spare. |
| ☐ | 1 of 12 | [I²S amplifier](https://www.amazon.com/dp/B0CDWXZZCH) | Amazon 111-8554202-0502625 (3) and 114-5029591-3604223 (6) | on hand · delivered 2026-09-03 and 10-14 |  |
| ☐ | 1 of 6 | [enclosed speaker](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) | DigiKey 2026-09-02 (4) and 10-01 (2) | on hand · DigiKey's pages say Delivered |  |
| ☐ | 1 of 420 | [tactile button](https://www.amazon.com/dp/B0FHW6HMG4) | Amazon 111-8554202-0502625 | on hand · delivered 2026-09-04 |  |
| ☐ | 4.7 kΩ, 10 kΩ; 220 µF; 100 nF | [resistor kit, electrolytic kit, ceramic kit](https://www.amazon.com/dp/B0F4P352BB) | Amazon 2026-09-02 | on hand |  |
| ☐ | frame | [1.5 mm brass tube, 4-packs](https://www.amazon.com/dp/B005WPAW9M) | Amazon 111-9290282-4717813 (09-02), 114-7954180-3181065 (10-06), 114-6509974-9230602 (10-07), 114-5551673-5391400 (4 packs, 10-19) | on hand · delivered 2026-09-03 to 10-26 | Seven packs, 28 tubes: the inventory logged one. |
| ☐ | harness rods | [1.0 mm brass rod, 5-packs](https://www.amazon.com/dp/B005WPB7YG) | Amazon 2026-09-02, 10-07, 10-10 | on hand · delivered 2026-09-04, 10-12, 10-12 | Shared with Crumb and the Sphere. |
| ☐ | silver rebuild | [nickel silver wire, 14 / 18 / 20 gauge](https://www.amazon.com/dp/B0BSTSMLF7) | Amazon 114-7658724-9947427, 114-7795722-0389854, 114-0400398-7479413, 2026-10-14 | on hand · delivered 2026-10-16 and 10-17 |  |
| ☐ | silver rebuild | [sterling silver wire, 14 gauge](https://www.amazon.com/dp/B00BY9A9HU) | Amazon 114-2217793-3508253, 2026-10-11 | on hand · delivered 2026-11-02 (USPS at the front desk 12:11); picked up 2026-11-03 (pick-up task completed 3 p.m.) | The 18 gauge (next row) came 10-20. |
| ☐ | silver rebuild | [sterling silver wire, 18 gauge](https://www.amazon.com/dp/B00ANA6JFC) | Amazon 114-9804173-2582632, 2026-10-11 | on hand · delivered 2026-10-20 |  |
| ☐ | as needed | [30 AWG silicone wire, two kits](https://www.amazon.com/dp/B073RDGTPB) | Amazon 111-2854120-5242663 and 111-2522128-9220253, 2026-09-02 | on hand · delivered 2026-09-02 and 09-04 | Shared by every build. |
| ☐ | as needed | [26 AWG silicone wire](https://www.amazon.com/dp/B07G2LRX68) | Amazon 111-9290282-4717813 | on hand · delivered 2026-09-03 |  |
| ☐ | as needed | [Kapton tape](https://www.amazon.com/dp/B072Z92QZ2) | Amazon 111-8554202-0502625 | on hand · delivered 2026-09-04 |  |
| ☐ | as needed | [fish paper](https://www.amazon.com/dp/B0GZVDKBBS) | Amazon 111-8554202-0502625 | on hand · delivered 2026-09-04 |  |
| ☐ | as needed | [heat-shrink kit, white](https://www.amazon.com/dp/B08N4W4K9X) | Amazon 111-8554202-0502625 | on hand · delivered 2026-09-03 |  |
| ☐ | 1 of 2 (final build) | [power-path boost board, PowerBoost 1000C copy](https://www.amazon.com/dp/B0G5PXGVG9) | Amazon 114-0663433-1244242, 2026-10-11 | on hand · delivered 2026-10-19 | The inventory dated this 10-14 and logged one; the account shows two. |
| ☐ | 1 of 4 (final build) | [1200 mAh LiPo pack](https://www.adafruit.com/product/258) | Adafruit 2026-09-01 (2) and 3771280 (2) | on hand | The only owned pouch rated for Pip's load. |
| ☐ | 2, held | [500 mAh LiPo pack](https://www.adafruit.com/product/1578) | Adafruit 2026-09-01 | on hand | Held; not released for any build. |
| ☐ | 1 (final build) | [USB-C LiPo charger](https://www.adafruit.com/product/4410) | Adafruit 2026-09-01 | on hand | Also charges the drone's flight packs. |

## Pocket AI Sphere (`pocket_ai_sphere`)

Only the controller is missing: its board is in the pair now expected by 11-15. Everything else comes out of shared stock and is on hand.

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 1 | [controller with camera and microphone](https://www.amazon.com/dp/B0C69FFVHH) | Amazon 114-1888127-6908215, 2026-10-27 (pair; the other is the camera Pocket AI's) | in transit · now expected by 2026-11-15 (was 11-23) |  |
| ☐ | 1 of 10 | [0.96 inch OLED display](https://www.amazon.com/dp/B09T6SJBV5) | Pip's stock, Amazon 2026-09-02 and 10-22 | on hand |  |
| ☐ | 1 of 5 | [temperature and humidity sensor](https://www.adafruit.com/product/4566) | Adafruit 3765988 and DigiKey 2026-10-01 | on hand | Cyber Dawn takes one. |
| ☐ | 1 of 12 | [I²S amplifier](https://www.amazon.com/dp/B0CDWXZZCH) | Pip's stock | on hand |  |
| ☐ | 1 of 6 | [enclosed speaker](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) | DigiKey 2026-09-02 (4) and 10-01 (2) | on hand · DigiKey's pages say Delivered |  |
| ☐ | 1 of 13 | [16340 cell, protected](https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery) | IMR Batteries 20739060 and 20739061, 2026-10-16 | on hand · both IMR boxes at the front desk 2026-10-21 (building log) |  |
| ☐ | 1 of 10 | [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) | Amazon 114-1421763-3353854 | on hand · delivered 2026-10-30 |  |
| ☐ | 1 of 20 | [toggle switch](https://www.amazon.com/dp/B0CZ6XZ2P9) | Amazon 114-1421763-3353854 | on hand · delivered 2026-10-30 |  |
| ☐ | 1 of 420 | [tactile button](https://www.amazon.com/dp/B0FHW6HMG4) | Pip's stock | on hand |  |
| ☐ | 4.7 kΩ; 220 µF; 10 µF + 100 nF | [resistor kit, electrolytic kit, ceramic kit](https://www.amazon.com/dp/B0F4P352BB) | Pip's stock | on hand |  |
| ☐ | 3 rods | [1.5 mm solid brass rod, 5-packs](https://www.amazon.com/dp/B01C6LUO5Q) | Amazon, many packs between 2026-10-10 and 10-28 (shared stock) | on hand | The three rings. About 90 rods are in the drawer. |
| ☐ | 1 rod | [1.0 mm brass rod](https://www.amazon.com/dp/B005WPB7YG) | Pip's stock | on hand | The two posts and the sensor hangers. |
| ☐ | as needed | [26 and 30 AWG wire, Kapton, fish paper, white heat-shrink](https://www.amazon.com/dp/B073RDGTPB) | Pip's stock | on hand |  |
| ☐ | 1, optional | [external 16340 charger](https://www.amazon.com/s?k=nitecore+ui1) | nothing bought | not ordered · optional |  |

## Pocket AI with camera (`pocket_ai_assistant_with_camera`)

Two things are still in the mail: the controller (in the pair now expected by 11-15) and the two gear motors (both at the bench 11-03, early). The driver, holder and switch came on 10-30; the rest is shared stock.

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 1 | [controller with camera and microphone](https://www.amazon.com/dp/B0C69FFVHH) | Amazon 114-1888127-6908215, 2026-10-27 (pair; the other is the Sphere's) | in transit · now expected by 2026-11-15 (was 11-23) |  |
| ☐ | 1 of 5 | [dual H-bridge motor driver, MX1508](https://www.amazon.com/dp/B075S368Y2) | Amazon 114-1421763-3353854, 2026-10-27 | on hand · delivered 2026-10-30 | Four spare. |
| ☐ | 2 (one per order) | [12 mm gear motor, 3 V 16 rpm](https://www.amazon.com/dp/B0BS9K8Q8Z) | Amazon 114-3598847-0810627 and 114-8685392-8347425, 2026-10-27 | on hand · both at the bench 2026-11-03 while sorting, early (no delivery mail; the Orders page had 11-05 to 11-16) | The record was unsure whether two were ordered; the account shows two orders of one. |
| ☐ | 1 of 10 | [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) | Amazon 114-1421763-3353854 | on hand · delivered 2026-10-30 |  |
| ☐ | 1 of 20 | [toggle switch](https://www.amazon.com/dp/B0CZ6XZ2P9) | Amazon 114-1421763-3353854 | on hand · delivered 2026-10-30 |  |
| ☐ | 1 of 13 | [16340 cell, protected](https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery) | IMR Batteries 20739060 and 20739061, 2026-10-16 | on hand · both IMR boxes at the front desk 2026-10-21 (building log) |  |
| ☐ | 1 of 10 | [0.96 inch OLED display](https://www.amazon.com/dp/B09T6SJBV5) | Pip's stock | on hand |  |
| ☐ | 1 of 12 | [I²S amplifier](https://www.amazon.com/dp/B0CDWXZZCH) | Pip's stock | on hand |  |
| ☐ | 1 of 6 | [enclosed speaker](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) | DigiKey 2026-09-02 (4) and 10-01 (2) | on hand · DigiKey's pages say Delivered |  |
| ☐ | 2 of 420 | [tactile buttons](https://www.amazon.com/dp/B0FHW6HMG4) | Pip's stock | on hand | Action button and home stop. |
| ☐ | 4.7 kΩ, 2 × 10 kΩ; 220 µF, 10 µF, 100 nF | [resistor kit, electrolytic kit, ceramic kit](https://www.amazon.com/dp/B0F4P352BB) | Pip's stock | on hand |  |
| ☐ | frame | [1.5 mm brass tube and rod, 1.0 mm rod, nickel silver](https://www.amazon.com/dp/B005WPAW9M) | Pip's stock | on hand | See shared stock. |
| ☐ | hub | [brass tube set, 4 mm tube](https://www.amazon.com/dp/B0F2FKLC2N) | Amazon 114-9676073-9134626 | on hand · delivered 2026-10-28 |  |
| ☐ | as needed | [26 and 30 AWG wire, headers, heat-shrink, Kapton, fish paper](https://www.amazon.com/dp/B073RDGTPB) | Pip's stock | on hand |  |
| ☐ | 1, optional | [external 16340 charger](https://www.amazon.com/s?k=nitecore+ui1) | nothing bought | not ordered · optional |  |

## Desk hologram (`desk_hologram`)

Two parts were bought and both are still in transit: the cube arrives Sunday 11-08, the filament pack is due today. The display, controller, microphone and leg stock are on hand.

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 1 | [beam-splitter cube, 50 mm](https://www.amazon.com/dp/B0B34FV475) | Amazon 114-6341362-5527437, 2026-11-01 | in transit · arriving Sunday 2026-11-08 | Keep it wrapped until the legs are on. |
| ☐ | 1 of 10 | [LED filament, 3 V, 38 mm, 2200 K](https://www.amazon.com/dp/B0FR35BGYL) | Amazon 114-0670386-1613054, 2026-11-01 | on hand · delivered to the front desk 2026-11-03 12:53 (Amazon mails; building log 12:59 to 13:41), Crumb's order in three boxes with the LED filaments riding in the gears' box; sorted at the bench the same afternoon | The satellite takes one from this pack; eight spare. The pack is in the satellite bin (sorted 11-03). |
| ☐ | 1 of 2 | [2.42 inch OLED display kit](https://www.adafruit.com/product/2719) | Adafruit 3765988, 2026-10-19, UPS | on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped) | Cyber Dawn's spare; its 220 µF is used. |
| ☐ | 1 of 13 | [ESP32-C3 SuperMini controller](https://www.amazon.com/dp/B0F888JQ91) | Pip's stock, Amazon 2026-09-02 and 10-17 | on hand |  |
| ☐ | 1 of 15 | [I²S microphone](https://www.amazon.com/dp/B092HWW4RS) | Pip's stock, Amazon 2026-09-02, 10-19, 10-23 | on hand |  |
| ☐ | 1 of 420 | [tactile button](https://www.amazon.com/dp/B0FHW6HMG4) | Pip's stock | on hand | Push to talk. |
| ☐ | 68 Ω; 100 nF | [resistor kit and ceramic kit](https://www.amazon.com/dp/B0F4P352BB) | Pip's stock | on hand | The only resistor in the build. |
| ☐ | about 0.5 m | [30 AWG silicone wire](https://www.amazon.com/dp/B073RDGTPB) | Pip's stock | on hand |  |
| ☐ | as needed | [Kapton, heat-shrink, CA glue, header pins, solder](https://www.amazon.com/dp/B072Z92QZ2) | bench stock | on hand |  |
| ☐ | 1 of 10 | [1.5 mm stainless coupon, 150 mm](https://www.amazon.com/dp/B082ZNMD46) | Amazon 114-6765566-8037841, 2026-10-27 | on hand · delivered 2026-10-29 | The four legs from one coupon. |
| ☐ | 1 | [USB-C wall adapter, 2 A, and a data cable](https://www.amazon.com/s?k=usb-c+wall+adapter+2a) | owned, no listing recorded | on hand | The only power source. |
| ☐ | optional | [black matte card; 5-minute epoxy](https://www.dickblick.com/) | nothing bought | not ordered · optional | Try the cube without the card first. |

## Desk satellite (`desk_satellite`)

All three parcels are in. The LED chips (delivered 11-04) and the wings (11-05, two days early) were picked up 11-05 and went into the satellite bin on 11-07 at the builder's word. The steel disc came 11-06, twelve days early, and is spare: on the bench it read too white, so the base is a brass coaster; the one ordered 11-06 (delivered 11-09 to the mail room) went to the desk lighthouse on 11-09, so the satellite's is to buy again; the disc sits in the satellite bin for now. The Eujgoov fallback panels were cancelled, so no fallback wing exists. The cell is on hand: the "November 3 order" in the inventory is order 20739060 of October 16, delivered October 21.

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 2 of 5 | [mini solar panels, 80 × 45 mm, 5 V, 5-pack](https://www.amazon.com/dp/B0FL26KWWT) | Amazon 111-1980686-5970641, 2026-11-03 | on hand · delivered 2026-11-05, two days early; picked up 2026-11-05 (pick-up task) | The wings; three spare. The pack is in the satellite bin (sorted 11-07). |
| ☐ | 1 of 20 | [pre-wired warm-white LED chips, 0805](https://www.amazon.com/dp/B09QGJ9LY7) | Amazon 111-9152603-4910637, 2026-11-03 | on hand · delivered 2026-11-04; picked up 2026-11-05 (pick-up task) | The beacon; 19 spare, one of them promised to the Mars rover. Judge the colour against a 2700 K bulb. The pack is in the satellite bin (sorted 11-07). |
| ☐ | 0 (was 1) | [stainless disc, 3 inch × 1/8 inch, 304](https://www.amazon.com/dp/B08JD6GY21) | Amazon 111-4967394-9172244, 2026-11-03 | on hand · delivered 2026-11-06, twelve days early (UPS from the maker, building log); picked up 2026-11-06 | Spare since 11-06: on the bench the steel read too white, so the base is the brass coaster below. In the satellite bin for now (sorted 11-07). |
| ☐ | 0 (to buy again) | [brass coaster, 75 × 8 mm, flat top](https://www.amazon.com/dp/B0D9DMK3L7) | Amazon 114-8443990-0476239, 2026-11-06, $12.99 ($14.14 with tax, sold by TOGGOOL) | not ordered · in the builder's Amazon cart since 2026-11-09 about 22:00 EST ($12.99, TOGGOOL, ships from Amazon); the one bought 2026-11-06 was delivered 2026-11-09 (mail room) and is the desk lighthouse's at the builder's word | The base. Hollow under a thin top, so the printed hub is glued on and about 150 g of steel goes into the hollow. |
| ☐ | 0 (was 3) | [mini solar panels, 110 × 60 mm, 6 V, 3-pack](https://www.amazon.com/dp/B08THXDWS1) | Amazon 114-9697223-4179439, 2026-11-03 | cancelled · the Orders page says cancelled, not charged | The inventory logged this as held stock arriving 11-07. It is not coming; there is no fallback wing. |
| ☐ | 1 of 2 | [charger board with 5 V boost](https://www.adafruit.com/product/6106) | Adafruit 3771280, 2026-10-26, UPS | on hand · delivered 2026-10-28 (Adafruit's order history and the building log) | Cyber Dawn takes the other. Cut the current jumper. |
| ☐ | 1 of 13 | [16340 cell, protected](https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery) | IMR Batteries 20739060 (7 cells with 12 IMREN 18350), 2026-10-16, UPS | on hand · both IMR boxes at the front desk 2026-10-21 (building log) | Not a November order: the pasted summary was this one. Eight spare across the family. |
| ☐ | 1 of 10 | [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) | Amazon 114-1421763-3353854, 2026-10-27 | on hand · delivered 2026-10-30 |  |
| ☐ | 1 of 20 pairs | [JST-PH 2.0 mm pigtails](https://www.amazon.com/dp/B0F6T4LKDG) | Amazon 111-8554202-0502625, 2026-09-02 | on hand · delivered 2026-09-04 | Meter the plug before it goes in. |
| ☐ | 1 of 13 | [ESP32-C3 SuperMini controller](https://www.amazon.com/dp/B0F888JQ91) | Pip's stock | on hand | Remove its red power LED. |
| ☐ | 1 of 100 | [Schottky diode](https://www.amazon.com/dp/B079KJ46ZS) | Amazon 114-5201101-3840264, 2026-10-27 | on hand · delivered 2026-10-30 | The drone's stock; the pack is in the drone bin (sorted 11-03). |
| ☐ | 1 of 10 | [LED filament, 3 V, 38 mm, 2200 K](https://www.amazon.com/dp/B0FR35BGYL) | Amazon 114-0670386-1613054, 2026-11-01 (the hologram's pack) | on hand · delivered to the front desk 2026-11-03 12:53 (Amazon mails; building log 12:59 to 13:41), Crumb's order in three boxes with the LED filaments riding in the gears' box; sorted at the bench the same afternoon | The pool under the body; the pack lives in this bin (sorted 11-03). |
| ☐ | 100 Ω; 68 Ω | [resistor kit](https://www.amazon.com/dp/B0F4P352BB) | Pip's stock | on hand | The two resistors in the build. |
| ☐ | 1 of 420 | [tactile button](https://www.amazon.com/dp/B0FHW6HMG4) | Pip's stock | on hand | The mode button in the lid. |
| ☐ | about 0.4 m | [30 AWG silicone wire](https://www.amazon.com/dp/B073RDGTPB) | Pip's stock | on hand |  |
| ☐ | as needed | [Kapton, white heat-shrink, CA glue, solder](https://www.amazon.com/dp/B072Z92QZ2) | bench stock | on hand |  |
| ☐ | 3 of 10 | [1.5 mm stainless coupons, 150 mm](https://www.amazon.com/dp/B082ZNMD46) | Amazon 114-6765566-8037841, 2026-10-27 | on hand · delivered 2026-10-29 | Post and two booms. |
| ☐ | 3 parts | [black PETG: bus box, lid, hub](https://www.printedsolid.com/collections/1-75mm-petg) | nothing bought | not ordered · print from shelf stock | After the bench fit. |
| ☐ | 12, held | [IMREN 18350 cells, 800 mAh](https://imrbatteries.com/search?q=IMREN+18350+800mAh) | IMR Batteries 20739060, 2026-10-16 | on hand · both IMR boxes at the front desk 2026-10-21 (building log) | Held stock, not for this build: unprotected and 18.2 mm thick. |

## Desk lighthouse (`desk_lighthouse`)

Ordered 2026-11-09 at 04:22 EST in one Amazon checkout that split into five orders ($122.64 with tax and delivery), matched to the lines by price and confirmed by the day's two shipping mails; these five orders were first logged as the Mars rover's. The brass coaster bought 2026-11-06 as the satellite's base is this build's since 11-09 and was delivered that day to the mail room. The five Grand Brass lamp parts are ordered by the builder's word, with no confirmation mail yet. The charger is not ordered: the DigiKey order of 11-09 was the rover's. That evening the builder rejected the acrylic tube and dropped the brass sheet (its order came back cancelled by the seller, not charged), so Rev D (awaiting approval) has an open lantern, no house, and its three small brass pieces made from the owned 1 mm rod and tubes. Everything else comes out of owned stock (`desk_lighthouse/docs/INVENTORY.md`).

| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |
| --- | --- | --- | --- | --- | --- |
| ☐ | 0 (to return) | [clear acrylic tube, 25 mm OD × 21 mm ID × 305 mm](https://www.amazon.com/dp/B08ZM5BCQJ) | Amazon 114-1438198-3243448, 2026-11-09, $8.99 | in transit · shipped 2026-11-09 12:13 EST with the reed switches ($20.48), arriving Wed 11-11; rejected by the builder that evening (Rev D has no glass): return it or keep it as stock | Was the lantern glass. Rev D's lantern is open. |
| ☐ | 1 of 2 | [N20 gearmotor, 6 V, 30 rpm, 3 mm D shaft, 2-pack](https://www.amazon.com/dp/B096S475NH) | Amazon 114-1438198-3243448, $15.99 | in transit · shipped 2026-11-09 17:22 EST with the magnets ($38.63), arriving Wed 11-11 (Amazon's mail) | Turns the shutter; the second is the spare. Check: 3 mm D shaft, runs at 3 V. |
| ☐ | 1 of 10 | [LED filament, 26 mm, 3 V, 2700 K, 10-pack](https://www.amazon.com/dp/B0HBX2YW18) | Amazon 114-6111517-7569023, $25.40 + $4.98 delivery | in transit · arriving Fri 11-27, the last box (Amazon's order mail) | The lamp; nine spare. The holed tab is +. |
| ☐ | 1 of 20 | [glass reed switch, 2 × 14 mm, 20-pack](https://www.amazon.com/dp/B0CHF29394) | Amazon 114-1438198-3243448, $9.82 | in transit · shipped 2026-11-09 with the acrylic tube, arriving Wed 11-11 | The index; pick the most sensitive of the twenty. Never bend a lead at the glass. |
| ☐ | 1 of 100 | [neodymium disc magnets, 3 × 1 mm, N52, 100-pack](https://www.amazon.com/dp/B0BQ3LPGZ1) | Amazon 114-1438198-3243448, $19.49 | in transit · shipped 2026-11-09 with the motors, arriving Wed 11-11 | One under the collar; 99 spare for the family. |
| ☐ | 0 (cancelled) | [brass sheet, 0.015 in, 4 × 10 in](https://www.amazon.com/dp/B0006N6WJE) | Amazon 114-5648832-0318640, $5.31 + $9.49 delivery (seller bestbrandsupply) | cancelled · by the seller, not charged (Your Orders, read in the builder's Chrome at their word, 2026-11-09 about 22:00 EST); Rev D has no house and no sheet-cut discs anyway. A copy from Blick that had reappeared in the cart was moved to Saved for later | Was the house and three discs. Rev D makes the shutter's floor, the magnet arm and the deck's bearing from 1 mm rod and tube rings. |
| ☐ | 1 | [brass round tube, 5/8 in × 0.014 in wall × 12 in](https://www.amazon.com/dp/B07DDFNNXY) | Amazon 114-7188491-2312247, $9.89 (seller What America Buys) | in transit · arriving 11-18 to 11-20 (Amazon's order mail) | The shutter, a 30 mm length; the rest is stock. |
| ☐ | 1 tube | [gel super glue, 4 g](https://www.amazon.com/dp/B003Y49R7G) | Amazon 114-1965907-0721062, $3.29 | in transit · arriving Sat 11-14 (Amazon's order mail) | One tube for this build, the hologram and the rover. |
| ☐ | 1 | [turned brass check ring, 1-1/2 in, 1/8 IP slip](https://grandbrass.com/check-rings/turned-brass-checkrings/?_bc_fsnf=1) | Grand Brass CRT1-12X8, ordered by the builder 2026-11-09 (their word) | ordered · no confirmation mail by 2026-11-09 18:00 EST; order number unknown | The gallery deck. Measure its thickness (drawn 3 mm) and rerun build_page.py. |
| ☐ | 1 | [spun brass vase cap, 1-1/2 in](https://grandbrass.com/categories.php?category=655) | Grand Brass VA01-12, the same order | ordered · as above | The roof. Measure its height (drawn 12.5 mm). |
| ☐ | 1 | [brass ball, 5/8 in, 1/8 IP blind tap](https://grandbrass.com/5-8in-diameter-1-8ips-threaded-tapped-blind-brass-ball-polished-nickle-finish/) | Grand Brass BB0-58X18, unfinished, the same order | ordered · as above | The ventilator ball. |
| ☐ | 1 | [hollow brass nipple, 1/2 in × 1/8 IP](https://grandbrass.com/1-2in-x-1-8ips-threaded-brass-hollow-nipple/) | Grand Brass NI0-12X18BR, the same order | ordered · as above | Through the cap; the lamp post solders up its bore. |
| ☐ | 1 | [beaded brass nut, 1/8 IP](https://grandbrass.com/1-8-27ips-unfinished-brass-beaded-nut/) | Grand Brass, the same order | ordered · as above | Clamps the roof's hardware; the lamp's return. |
| ☐ | 1 | [charger board with 5 V boost (bq25185)](https://www.adafruit.com/product/6106) | nothing bought: not in the 2026-11-09 DigiKey order (the rover's); Cyber Dawn's two and Crumb's (DigiKey 102777448, shipped 11-09) are spoken for | not ordered · one line, Adafruit 6106 or DigiKey 1528-6106-ND, $8.95; Amazon has no bq25185 board (searched 2026-11-09 evening) | The cell's charger and the 5 V rail. Cut the current jumper. |
| ☐ | 1 | [brass coaster, 75 × 8 mm, flat top](https://www.amazon.com/dp/B0D9DMK3L7) | Amazon 114-8443990-0476239, 2026-11-06, $12.99 ($14.14 with tax, sold by TOGGOOL); bought as the satellite's base | on hand · delivered 2026-11-09 12:01 EST to the mail room (Amazon's mail), in one package with the drone's heat tape; pick-up pending its task | The base and the electronics box. Measure the hollow; a magnet must not stick to the top. The satellite buys its own again. |
| ☐ | 1 of 13 | [16340 cell, protected](https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery) | IMR Batteries 20739060 / 20739061, 2026-10-16 | on hand · both IMR boxes at the front desk 2026-10-21 (building log) | Stands in the house behind the motor. |
| ☐ | 1 of 10 | [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) | Amazon 114-1421763-3353854, 2026-10-27 | on hand · delivered 2026-10-30 | Cyber Dawn's stock; meter the leads before the cell goes in. |
| ☐ | 1 of 13 | [ESP32-C3 SuperMini controller](https://www.amazon.com/dp/B0F888JQ91) | Pip's stock | on hand | In the coaster's hollow; no Wi-Fi in this build. |
| ☐ | 1 of 5 | [dual H-bridge driver (MX1508)](https://www.amazon.com/dp/B075S368Y2) | Amazon 114-1421763-3353854, 2026-10-27 | on hand · delivered 2026-10-30 | The camera Pocket AI's stock; channel A the motor, channel B the lamp. |
| ☐ | 1 of 100 | [Schottky diode (SS14)](https://www.amazon.com/dp/B079KJ46ZS) | Amazon 114-5201101-3840264, 2026-10-27 | on hand · delivered 2026-10-30 | The drone's pack, in the drone bin. |
| ☐ | 4 of about 90 | [1.5 mm brass rod, 300 mm](https://www.amazon.com/dp/B01C6LUO5Q) | shared stock, eighteen 5-packs | on hand | The four rods of the cage, cut 222 each. |
| ☐ | 147 mm of one 4 mm tube | [brass tube set, 2 to 7 mm, 200 mm](https://www.amazon.com/dp/B0F2FKLC2N) | Amazon 114-9676073-9134626, 2026-10-26 | on hand · delivered 2026-10-28 | The spine. |
| ☐ | 42 mm of one | [1.0 mm brass rod, 300 mm](https://www.amazon.com/dp/B005WPB7YG) | shared stock | on hand | The lamp post. |
| ☐ | 2 + 2; 1 | [47 Ω and 100 kΩ resistors; tactile button](https://www.amazon.com/dp/B0F4P352BB) | Pip's stock | on hand | The lamp's series pair, the cell divider, the one button. |

## Shared stock, split across the bins

Counts come from the Orders page and the mails read today; "spare" is what is left after every build above takes its share. Bins at the bench (2026-11-03): one per project, a shared bin for parts that active projects share, and a backcase bin for spares that belong to no project; the builder says where each pack went, and the rows record it.

| Part | Owned | Where and when | Who takes what | Spare |
| --- | --- | --- | --- | --- |
| ESP32-C3 SuperMini controllers | 13 | Amazon 10-pack 2026-09-02 and 3-pack 2026-10-17, on hand | Pip 1 · hologram 1 · satellite 1 | 10 |
| XIAO ESP32-S3 Sense boards | 4 ordered, 0 on hand | Amazon: Crumb's and the drone's by 11-11, the pair by 11-15 | Crumb 1 · drone 1 · camera Pocket AI 1 · Sphere 1 | 0 |
| Nitecore 16340 cells | 13 | IMR Batteries, two orders of 2026-10-16, at the front desk 10-21 | Crumb 1 · Cyber Dawn 1 · Sphere 1 · camera Pocket AI 1 · satellite 1 | 8 |
| IMREN 18350 cells | 12 | IMR Batteries 20739060, on hand 10-21 | no build | 12 |
| charger boards with 5 V boost | 2 | Adafruit 3771280, on hand 10-28 | Cyber Dawn 1 · satellite 1 | 0 |
| fuel gauges | 2 | Adafruit 3771280, on hand 10-28 | Cyber Dawn 1 · Crumb 1 | 0 |
| 16340 holders with leads | 10 | Amazon 2026-10-27, on hand 10-30 | Crumb · Cyber Dawn · Sphere · camera Pocket AI · satellite | 5 |
| toggle switches | 20 | Amazon 2026-10-27, on hand 10-30 | Crumb · Sphere · camera Pocket AI | 17 |
| dual H-bridge drivers | 5 | Amazon 2026-10-27, on hand 10-30 | camera Pocket AI 1 | 4 |
| 1.5 mm stainless coupons, 150 mm | 10 | Amazon 2026-10-27, on hand 10-29 | drone about 2 · hologram 1 · satellite 3 | about 4 |
| 1 mm stainless rod, 300 mm | 20 | Amazon 2026-10-27, delivered 11-04 and 11-05, picked up 11-05 | drone about 1 | 19 |
| LED filaments, 38 mm 2200 K | 10 | Amazon 114-0670386-1613054, delivered 11-03 12:53 in the box with Crumb's gears; the pack is in the satellite bin (sorted 11-03) | hologram 1 · satellite 1 | 8 |
| pre-wired warm-white LED chips, 0805 | 20 | Amazon 111-9152603-4910637, delivered 11-04, picked up 11-05; the pack is in the satellite bin (sorted 11-07) | satellite 1 · Mars rover 1 | 18 |
| I²S amplifiers | 9 on hand + 3 today | Amazon 2026-09-02 (3), 10-11 (6), 10-31 (3) | Pip · Cyber Dawn · Crumb · Sphere · camera Pocket AI | 7 |
| enclosed speakers | 6 | DigiKey 2026-09-02 (4) and 10-01 (2); the 09-21 order in the inventory does not exist | Pip · Crumb · Sphere · camera Pocket AI · drone 1 (added 11-09) | 1 |
| 0.96 inch OLED displays | 10 | Amazon 2026-09-02 and 10-22 | Pip 1 (soldered) · Sphere 1 · camera Pocket AI 1 | 7 |
| I²S microphones | 15 | Amazon 2026-09-02, 10-19, 10-23 | Pip 1 (soldered) · hologram 1 | 13 |
| temperature and humidity sensors | 5 | Adafruit 3765988 (2), DigiKey 2026-10-01 (3) | Cyber Dawn 1 · Sphere 1 | 3 |
| 100 mm QT cables | 7 | Adafruit 3765988 | Cyber Dawn 5 · Crumb 2 | 0 |
| motion sensors (GY-521) | 13 ordered | Amazon: HiLetgo 3-pack 114-1259113-3701002 arriving 11-09; Ximimark 10-pack 11-19 to 12-15 | drone 1 · Crumb 1, both from the 3-pack | 11 |
| laser rangers, 8×8 and single-zone | 2 + 2 | Pololu via DigiKey, USPS 9400150105496136143356, at the front desk 11-02 | drone 1 + 1 · Crumb 1 + 1 | 0 |
| Schottky diodes | 100 | Amazon 2026-10-27, on hand 10-30; the pack is in the drone bin (sorted 11-03) | drone 4 · satellite 1 | 95 |
| JST-PH 2.0 mm pigtail pairs | 20 | Amazon 2026-09-02 | Cyber Dawn 1 · satellite 1 · in the shared bin (builder, 2026-11-08) | 18 |
| 1.5 mm solid brass rod, 5-packs | 18 packs, about 90 rods | Amazon 2026-10-10 to 10-28 (the 10-28 order alone is 10 packs) | Sphere 3 rods | about 87 |
| 1.5 mm brass tube, 4-packs | 7 packs, 28 tubes | Amazon 2026-09-02, 10-06, 10-07, 10-19 (4) | Pip's frame | most |
| 1.0 mm brass rod, 5-packs | 3 packs, 15 rods | Amazon 2026-09-02, 10-07, 10-10 | Pip · Crumb about 4 · Sphere 1 | about 8 |
| brass tube sets, 2 to 7 mm | 3 × 200 mm on hand; 3 × 330 mm due 11-06 to 11-13; 4 × 330 mm 11-13 to 11-19 | Amazon 2026-10-26 and 10-30 | Cyber Dawn cradles · Crumb hubs · camera Pocket AI hub | plenty |
| resistor, ceramic and electrolytic kits | 1 each | Amazon 2026-09-02 | every build pulls values |  |
| 30 AWG wire kits | 2 | Amazon 2026-09-02 | every build |  |
| 26 AWG wire kit, Kapton, fish paper, heat-shrink, M3 screw kit | 1 each | Amazon 2026-09-02; M3 kit 2026-10-27, picked up 11-01 | every build |  |
| 1200 mAh LiPo packs | 4 Adafruit + 2 EEMB | Adafruit 2026-09-01 and 3771280; Amazon 114-0584890-2786622 | Pip final build 1 | 5 |
| 500 mAh LiPo packs | 2 | Adafruit 2026-09-01 | held | 2 |
| power-path boost boards | 2 | Amazon 2026-10-11, on hand 10-19 | Pip final build 1 | 1 |
| cool-white LED stars | 4 | Amazon 2026-10-27, on hand 11-02 | drone 1 | 3 |
| controller boards, ESP32-S3 dev kits | 3 (8 MB) + 2 (16 MB) | DigiKey, at the front desk 11-02; Amazon 2026-10-01, on hand 10-06 | Cyber Dawn 1 | 4 |
| solar panel, DC jack parts, USB-C extension, 6600 mAh pack | 1 each | Adafruit 3771280, on hand 10-28; all four in the shared box (sorted 11-03) | no build (Cyber Dawn's removed solar) | all |
| rotary encoders: four KY-040 modules and five bare EC11 switches (WayinTop) | 9 | Amazon, order not in the records; in the backcase bin (sorted 11-03) | no build (Cyber Dawn's wheel is the Adafruit I²C encoder) | 9 |

## Delivered on 2026-11-02; picked up 2026-11-03 (all four pick-up tasks completed 3 p.m.)

The routine's list held no task for these four parcels at 06:20 EST; the routine session created one per order at 06:48, due 3 p.m. today. They are at the front desk per the building's log; a pick-up counts as confirmed only when its task is completed, so they sit here and in the tracker's order table, not in its confirmed pick-ups.

| Delivered | Order | Items | Project |
| --- | --- | --- | --- |
| 2026-11-02 | DigiKey order 102531269, invoice 135297233 (FedEx 549379676887) | MOSFETs, lens, piezos; Cyber Dawn's three controller boards | XS drone, Cyber Dawn |
| 2026-11-02 | DigiKey marketplace order 102531268, invoice 135297191 (Pololu, USPS) | two 8×8 and two single-zone laser rangers | XS drone, Crumb |
| 2026-11-02 | Amazon 114-5101833-0385036 | four cool-white LED stars | XS drone |
| 2026-11-02 | Amazon 114-2217793-3508253 | sterling silver wire, 14 gauge | Pip, silver rebuild |

