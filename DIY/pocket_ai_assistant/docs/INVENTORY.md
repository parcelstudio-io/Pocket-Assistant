# Purchased inventory — what is in hand and what each item is for

> **Factual purchase record, last updated 2026-10-01.** This tracks what was
> *bought*, not what is *approved*. It takes no side in the R1/F0 design fork —
> part-selection authority stays in
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md). Mark items off
> as boxes arrive and incoming inspection passes.

**Status: the recorded orders provide a starting set for the USB prototype.**
Check what has actually arrived before each session. This inventory does not
establish a complete battery-powered design. Start with the
[action-only fast track](../plan/FAST_TRACK.md), using what is already owned;
software setup needs no new purchase, while the first physical boot needs any
proven USB data cable.

## Orders placed

| Order | Date | Contents |
| --- | --- | --- |
| X-Tronic | earlier | Soldering station — $64.80 |
| Adafruit | Sep 1 | Cells, charger, flux pen — $81.29 incl. shipping + tax |
| Amazon #4 | Sep 1 | Bench supply, saw, solder, stripper, brass flux, jumpers, headers |
| Amazon #5 | Sep 1 | Multimeter, calipers, breadboards, safety glasses, pliers |
| Amazon #1 | Sep 2 | Core electronics, passives, insulation, switch, buttons, JST |
| Amazon #2 | Sep 2 | OLED, electrolytic caps |
| Amazon #3 | Sep 2 | K&S 1 mm brass rod |
| DigiKey | Sep 2 | 4 × `CES-20134-088PM` speaker (two lines of two), order 101368762, invoice 132033605, $16.40 + shipping, tariff and tax = $29.67; FedEx 541958299829, delivered (DigiKey account read 2026-11-03) |
| Amazon #6 | Sep 2 | K&S #9831 brass tube, TUOFENG 26 AWG wire |
| Amazon #7 | Sep 2 | CBAZY 30 AWG wire (re-ordered after cancellation) |
| Amazon #8 | Sep 2 | Heat gun $10.33 · hot glue gun $11.92 · diamond needle files |
| Amazon #9 | Sep 21 | Rigol DHO802 oscilloscope, [B0CKX699F5](https://www.amazon.com/dp/B0CKX699F5); price paid not recorded |
| Amazon #10 | Sep 21 | BAISDY 45-piece wet/dry sandpaper, 400–3000 grit ([B07D2YYC11](https://www.amazon.com/dp/B07D2YYC11)) · JoTownCand solder wick 3-pack ([B0DRN688Q5](https://www.amazon.com/dp/B0DRN688Q5)) · Epic Medical Supply 91% isopropyl alcohol, 2 × 16 oz ([B0BSJ93RKB](https://www.amazon.com/dp/B0BSJ93RKB)); prices not recorded |
| ~~DigiKey~~ | ~~Sep 21~~ | ~~5 × Same Sky speaker, $20.50~~ **Correction 2026-11-03: no such order exists in the DigiKey account** (three orders only: 09-02, 10-01, 10-28). The speakers are four from 09-02 and two from 10-01: six owned |
| DigiKey | Oct 1 | 2 × Same Sky `CES-20134-088PM` speaker, 2223-CES-20134-088PM-ND, $4.10 each — $8.20. Same order also carried 3 × Adafruit AHT20 #4566 (1528-4566-ND, $4.50 each) and 3 × SparkFun Qwiic VCNL4040 15177 (1568-15177-ND, $8.50 each), which are Cyber Dawn sensors and are logged in `../../cyber_clock_v2/docs/INVENTORY.md`. Order subtotal $47.20, $61.92 with tariff, shipping and tax; delivered. Logged 2026-10-28 from the DigiKey order history. |
| Amazon #12 | Sep 21 | Rust-Oleum Stops Rust spray paint, 12 oz: `7789830` gloss canvas white ([B000PIG3AS](https://www.amazon.com/dp/B000PIG3AS)) and `7791830` satin white ([B000Z8FGII](https://www.amazon.com/dp/B000Z8FGII)); prices not recorded |
| Amazon #13 | Oct 1 | Amazon Basics cardstock, 65 lb / 176 gsm, 8.5 × 11", 96 bright white, 250 sheets ([B0DSH5V1TT](https://www.amazon.com/dp/B0DSH5V1TT)); for the 1:1 cardboard mock-up templates and box. Price not recorded. |
| Amazon #14 | Oct 1 | DIYSELF craft (Exacto-style) knife, 12 pcs: 1 handle + 11 blades, with case ([B0D4DKYL2C](https://www.amazon.com/dp/B0D4DKYL2C)); for cutting the mock-up card. Price not recorded. |
| Amazon #15 | Oct 1 | Anezus craft knife kit: A4 (12 × 9") self-healing cutting mat, 1 knife, 30 spare #11 blades ([B0BWYJC65J](https://www.amazon.com/dp/B0BWYJC65J)); the mat is the part the DIYSELF knife lacked. Price not recorded. |
| Amazon #16 | Oct 8 | Second pack of K&S #9861 1.0 mm × 300 mm round brass rod, 5 rods ([B005WPB7YG](https://www.amazon.com/dp/B005WPB7YG)); for free-form brass wiring in place of insulated wire. Price not recorded. |
| Amazon #17 | Oct 10 | 900M-T series soldering tip assortment (fits the X-Tronic 3020-XTS; chisel, conical, knife) and a tip tinner (builder-reported; listing and price not recorded). Replaces the tip worn out by the Harris acid flux; keep one chisel for brass and one fine tip for electronics. |
| Amazon #18 | Oct 11 | WireJewelry .925 sterling silver round wire, dead-soft, 5 ft each: 14 gauge / 1.63 mm ([B00BY9A9HU](https://www.amazon.com/dp/B00BY9A9HU)) for a silver frame (two loops + four posts, solid instead of tube), 18 gauge / 1.02 mm ([B00ANA6JFC](https://www.amazon.com/dp/B00ANA6JFC)) for silver harness wiring in place of the K&S rod. For a second, unpainted build; same template and drawings. Dead-soft: stretch-straighten every piece before bending. Prices not recorded. The 14 gauge (order 114-2217793-3508253) was delivered 2026-11-02 and picked up 2026-11-03; the 18 gauge came 2026-10-20. |
| Amazon #19 | Oct 11 | Dahle Vantage 10672 self-healing cutting mat, 18 × 24", black ([B0027ROZ9G](https://www.amazon.com/dp/B0027ROZ9G)); bench surface for cutting the jig card and layout. **PVC: not heat-resistant; never solder on it** — the X-Tronic silicone mat goes on top for soldering. Price not recorded. |
| Amazon #20 | Oct 14 | PowerBoost 1000C-class charger/boost board, sold as "For Powerboost 1000 Charger … 2465 Module" ([B0G5PXGVG9](https://www.amazon.com/dp/B0G5PXGVG9)); a third-party copy of Adafruit #2465, not the Adafruit board. Listing gives no discharge rating and warns the charger chip reaches ~75 °C while charging. Pinout, charge current, load sharing and the EN/LBO pins are to be verified on the bench (the PowerBoost Real Test page) before it goes in the frame. Price not recorded. |
| Amazon #21 | Oct 14 | CRAFT WIRE nickel silver (CDA 752: 65 % Cu, 18 % Ni, 17 % Zn), round, dead soft, 25 ft each, made in USA: **14 gauge / 1.63 mm** ([B0BSTSMLF7](https://www.amazon.com/dp/B0BSTSMLF7)) for the frame (replaces the 1.5 mm brass tube, about twice as stiff, no paint), **18 gauge / 1.02 mm** (the 18-gauge variant of the same listing; child ASIN not recorded) — the exact size of the 1.0 mm brass harness rods, so the harness page applies unchanged — and **20 gauge / 0.81 mm** (20-gauge variant; child ASIN not recorded) as the finer option for the harness rods. Solders like brass with the Harris flux; clear-coat for lasting brightness. Supersedes the sterling (Amazon #18) as the silver-rebuild material; the sterling stays owned. Price not recorded. |
| Amazon #22 | Oct 20 | K&S #9862 round brass rod, **1.5 mm** × 300 mm, 5 rods, solid ([B01C6LUO5Q](https://www.amazon.com/dp/B01C6LUO5Q)); a stiffer solid alternative to the 1.5 mm #9831 tube for frame loops and posts, and the free-wire stock for Cyber Dawn's decorative lines (too thin for that clock's main loops, which want 3 mm rod or 1/8" tube). Price not recorded. |
| Amazon #23 | Oct 27 | uxcell 304 stainless steel solid round rod, **1.5 mm × 150 mm**, 10 pieces ([B082ZNMD46](https://www.amazon.com/dp/B082ZNMD46)); solder-test coupons for the projects after Cyber Dawn (the drone onward), which will be built in stainless. Not for the Pocket AI builds or Cyber Dawn: those stay brass tube and rod. Soft-solders with the owned Harris Stay-Clean flux (labeled for stainless); 150 mm is coupon length only. The 300 mm pack ([B082ZNTD4J](https://www.amazon.com/dp/B082ZNTD4J)) is the frame stock if the test passes. Price not recorded. |
| Amazon #24 | Oct 28 | XLamp Cree XP-G2 Indus Star 1-Up, cool white, **2 pieces, then 4 more on Oct 28 (6 total)** ([B00LWU5DWM](https://www.amazon.com/dp/B00LWU5DWM)); the flashlight emitter for the XS drone (xs_drone/docs/payload-assessment.md): one XP-G2 LED on a 20 mm hexagonal aluminium star, 139 lm minimum at 350 mA, 254 lm at 700 mA, Vf 2.8 to 2.9 V. One is the drone's, sawn to a 14 mm disc; the second is a spare. Not for the Pocket AI builds or Cyber Dawn. Still needed for the flashlight: Carclo 10412 lens and AMC7135 regulators. Price not recorded. Delivered 2026-11-02, picked up 2026-11-03 (order 114-5101833-0385036). |
| Amazon #25 | Oct 28 | 615 coreless brushed motors, 6 × 15 mm, 0.8 mm shaft, 3.7 V, **4 pieces, 2 CW + 2 CCW**, sold as Blade Inductrix / H36 / E010 replacements ([B09J236JJL](https://www.amazon.com/dp/B09J236JJL)), **two packs ordered, 8 motors**; the XS drone's four lift motors plus a spare set (xs_drone/docs/custom-build.md). About 2 g each; stall 2.3 to 2.8 A; run on 31 mm four-blade 0.8 mm-bore props. Not a Pocket AI or Cyber Dawn part. Price not recorded. |
| Amazon #26 | Oct 28 | 31 mm four-blade propellers, 0.8 mm bore, black, **16 pieces** (8 CW + 8 CCW), sold as Blade Inductrix / H36 / E010 614/615 replacements ([B09L4MXXCW](https://www.amazon.com/dp/B09L4MXXCW)); the XS drone's props, four sets. Fit the Amazon #25 motors. Price not recorded. |
| Amazon #27 | Oct 28 | uxcell 304 stainless steel solid round rod, **1 mm × 300 mm**, 10 pieces ([B082ZNWQ5Q](https://www.amazon.com/dp/B082ZNWQ5Q)); the XS drone's frame stock: rails, axles, nose and tail bars of the ladder frame (xs_drone/docs/custom-build.md), about 300 mm used. The 1.5 mm coupons (Amazon #23) make the motor collars. Not for the Pocket AI builds or Cyber Dawn. $16.59 (shipped mail). Delivered with Amazon #32 as two "online seller" boxes at the front desk, 2026-11-04 and 2026-11-05, both picked up 2026-11-05 (orders 114-7336723-5981056 and 114-1049705-6516238; which box held which is not recorded); the builder named the rods 2026-11-07 and confirmed both packs, 20 rods, 2026-11-08. |
| Amazon #28 | Oct 28 | Seeed Studio **XIAO ESP32-S3 Sense**, 1 ([B0C69FFVHH](https://www.amazon.com/dp/B0C69FFVHH)), $23.99: the XS drone's brain, with the OV2640 camera and PDM microphone on the Sense expansion board (xs_drone/docs/custom-build.md). Cut jumper J3 on the expansion board so GPIO7/8/9 are free of the SD slot. Not a Pocket AI or Cyber Dawn part. |
| DigiKey | Oct 28 | XS drone sensors and small parts, submitted 2026-10-28 00:57, two shipments. From DigiKey: 2 × Carclo **10412** 10 mm narrow-spot lens (1066-1042-ND, $2.32), 10 × **AO3400A-EV** SOT-23 N-MOSFET (5272-AO3400A-EVCT-ND, $0.315), 10 × TDK **PS1240P02BT** piezo (445-2525-1-ND, $0.546), and 3 × Espressif **ESP32-S3-DevKitC-1-N8R8** dev boards (1965-ESP32-S3-DEVKITC-1-N8R8-ND, $15.00; one is Cyber Dawn's controller, two are spares; not drone parts); subtotal $58.25. From Pololu via the DigiKey Marketplace: 2 × **VL53L1X** carrier #3415 (2183-3415-ND, $22.95) and 2 × **VL53L7CX** carrier #3418 (2183-3418-ND, $19.95); subtotal $85.80. Roles in xs_drone/docs/custom-build.md and payload-assessment.md: lens and MOSFETs for the flashlight (MOSFETs as fallback switch and as the four motor switches), piezos as the beeper, VL53L1X down-looking and VL53L7CX forward-looking rangers; one of each is a spare. Both shipments delivered 2026-11-02 (FedEx and USPS, front desk) and picked up 2026-11-03. |
| Amazon #29 | Oct 28 | **AMC7135** (L7135) 350 mA constant-current LED driver, SOT-89, 10 pieces ([B0CST7GZTN](https://www.amazon.com/dp/B0CST7GZTN)), $24.58 with delivery; two drive the XS drone's flashlight in parallel at 700 mA, switched by GPIO43. Arriving Nov 17–20. |
| Amazon #30 | Oct 28 | **Crazepony 1S 250 mAh 30C LiPo**, Micro JST 1.25 plug, 4 packs ([B0FCMLVCN2](https://www.amazon.com/dp/B0FCMLVCN2)), 55 × 11 × 5.8 mm each; the XS drone's flight packs and floor pan. Same order: **Chanzon SS14** Schottky diodes 1 A 40 V SMA, 100 pieces ([B079KJ46ZS](https://www.amazon.com/dp/B079KJ46ZS)), the flyback diodes across the four motors; and **Ximimark GY-521 MPU6050** 2-packs × 5 = 10 boards ([B07MMZ37PT](https://www.amazon.com/dp/B07MMZ37PT)), the drone's IMU plus nine spares for other projects. Order total $77.99; batteries and diodes arrive Oct 31, GY-521 Nov 19–Dec 15. |
| Amazon #31 | Oct 28 | **JST 1.25 mm 2-pin micro connectors** with 26 AWG 100 mm leads, male and female, 30 pairs (listing title "30 Pairs JST 1.25mm 2 Pin Micro Male and Female Connector - 1571# 26AWG", ASIN not recorded); the XS drone's battery lead and the charger lead for the Crazepony packs. Delivered Nov 1, two days early, and picked up the same evening (order 114-3670533-2737853). |
| Amazon #32 | Oct 28 | Second order of uxcell **1 mm × 300 mm** 304 stainless rod, 10 pieces ([B082ZNWQ5Q](https://www.amazon.com/dp/B082ZNWQ5Q)), $16.59: a duplicate of Amazon #27, 20 rods in all, far more than the drone's 300 mm. A separate order of 1.5 mm × 100 mm rod was cancelled, not charged. Arrived with Amazon #27 and picked up 2026-11-05 (see there). |
| Amazon #33 | Oct 27 | **M3 screw kit**, 600 pieces, order 114-4394285-9360218, $8.70 (listing not recorded; read from the Orders page 2026-10-31). Shared stock for every build. Delivered Oct 31, picked up Nov 1 (the routine's task called it "Fasteners — Unassigned"). |
| Amazon #34 | Nov 7 | **HiLetgo GY-521 MPU-6050**, 3 boards (listing title "HiLetgo 3pcs GY-521 MPU-6050 MPU6050 3 Axis Accelerometer Gyroscope Module…"; [B00LP25V1A](https://www.amazon.com/dp/B00LP25V1A), the listing linked to the builder that day), order 114-1259113-3701002 (Amazon dates it Nov 6; the mail came 01:18 EST Nov 7), $12.84, arriving Nov 9 (Orders page read 2026-11-09 in the builder's Chrome). Bought so the XS drone's IMU step, and Crumb's, need not wait for the Ximimark 10-pack's 11-19 to 12-15 window (Amazon #30). Same board: MPU6050 at 0x68 with AD0 pulled low, on-board 3.3 V regulator, I²C pull-ups, INT brought out. |
| Amazon #35 | Nov 7 | **BENECREAT 21 gauge silver-plated copper craft wire**, tarnish-resistant (lacquered), 65 ft ([B08MQ9S5B8](https://www.amazon.com/dp/B08MQ9S5B8)); order 114-2994210-6608245, $10.88, arriving Nov 9 (Orders page read 2026-11-09). 0.72 mm. The lacquer resists solder: sand each joint to bare copper and tin it first; pull lengths straight before use; never use for binding joints. Project not named yet; in the backcase bin (builder, 2026-11-10). |
| Amazon #36 | Nov 7 | **Texas Knifemakers Supply 752 nickel silver rod, 1/8 in (3.18 mm) × 12 in**, 2 packs of 5 (10 rods, about 21 g each); order 114-1930656-1985004 together with the 1/16 in rods (Amazon #37), $119.54 for the order, arriving Wed Nov 11 (Orders page read 2026-11-09); two sibling orders of six 1/16 in packs (114-6369839-6983469, 114-4490119-2922600) show as cancelled, not charged. ASIN not recorded. Same alloy as the craft wire (Amazon #21) as bar stock: silver-white, solders like brass at full strength with ordinary flux. Thick: bend in a vise, cut with the jeweler's saw. Shared frame stock; project not named yet. |
| Amazon #37 | Nov 7 | **Texas Knifemakers Supply 752 nickel silver rod, 1/16 in (1.59 mm) × 12 in**, 2 packs of 5 (10 rods, about 5 g each); in order 114-1930656-1985004 with Amazon #36, arriving Wed Nov 11. ASIN not recorded. The nickel-silver match for the 1.5 mm stainless coupons: same look, easy full-strength joints, about 35 % less stiff. Shared frame stock; project not named yet. |
| Amazon #38 | Nov 7 | **MEBMIK clear heat tape**, 12 rolls of 10 mm × 33 m, transparent polyester film with a heat-resistant adhesive, sold for heat presses ([B0BD84GGPV](https://www.amazon.com/dp/B0BD84GGPV)), order 114-0986744-9273034, $14.14, arriving Nov 9 (Orders page read 2026-11-09). The XS drone's finish: battery straps, and the tape over white cardstock (Amazon #13) patches on the sensor boards and the packs' red label (xs_drone/docs/custom-build.md, Colour and finish). About 0.3 m used; eleven rolls spare for any build. |
| Amazon #39 | Nov 8 | **youyeetoo FHL-LD19 lidar kit** (LDROBOT LD19 with pigtail, USB adapter and Dupont leads; [B0B1QCV4XR](https://www.amazon.com/dp/B0B1QCV4XR)) and **Bridgold AO3401 P-channel MOSFETs**, 100, marked A19T ([B09WN8WP8M](https://www.amazon.com/dp/B09WN8WP8M)); order 114-7956116-1377847, $86.43 with tax; shipped the night of 11-08, arriving 11-09. Bought for Crumb Rev B; since Rev C (2026-11-09) neither is Crumb's. Both are in the backcase bin, kept together (the builder's word, 2026-11-10). |
| Amazon #40 | Nov 9 | **Desk lighthouse** (first logged as the Mars rover's Amazon lines; corrected 11-09 evening against the lighthouse cart's prices, which match the five totals to the cent): 8 items in five orders placed together at 04:22 EST, $122.64. 114-1438198-3243448 ($59.11, Wed 11-11; shipped 11-09 in two packages): uxcell clear acrylic tube 25 OD × 21 ID × 305, Augiimor N20 6 V 30 rpm gearmotor 2-pack, JESSINIE 2 × 14 mm reed switches 20-pack, N52 3 × 1 mm magnets 100-pack · 114-1965907-0721062 ($3.58, Sat 11-14): Loctite Ultra Gel Control 4 g, one tube shared with the hologram and the rover · 114-5648832-0318640 ($16.11, Wed 11-18): K&S 252 brass sheet 0.015 in, 4 × 10 in · 114-7188491-2312247 ($10.77, 11-18 to 11-20): K&S 8143 brass tube 5/8 in × 12 in · 114-6111517-7569023 ($33.07, Fri 11-27): UGEFKMQ 26 mm 2700 K 3 V LED filaments 10-pack. None of the rover's Amazon lines was in this checkout (they were only opened in the default browser, which does not fill the cart); they are still to buy. Record: `desk_lighthouse/docs/INVENTORY.md`. |
| Amazon #41 | Nov 9 | **PAM8403 class-D amplifier board, 5-pack**, the version without the volume knob ([B0DYYX8DF9](https://www.amazon.com/dp/B0DYYX8DF9)), order 114-4918612-8872205, $5.59, arriving Thu 11-12 (Orders page, read 2026-11-10 00:50 EST). The XS drone's speaker amplifier: one fitted, four spare. |
| DigiKey | Nov 8 | **Crumb's charger-boost**: Adafruit bq25185 USB-C charger with 5 V boost #6106 (1528-6106-ND, $8.95), sales order 102777448, web ID 379032068, submitted 2026-11-08 15:15 (the receipt pasted in chat); $8.95 + $4.99 USPS Ground Advantage + $1.24 tax = $15.18; shipped 11-09 (invoice 136003544, USPS 9200190106460365547930), due about 11-12 to 11-14. The third 6106 owned: the two of 10-26 are Cyber Dawn's and the desk satellite's. Logged late, on 2026-11-10. |
| DigiKey | Nov 9 | **Mars rover Rev J**, web ID 379047134, submitted 2026-11-09 03:30 (DigiKey's receipt page), two shipments. From Pololu (sales order 102785005, Standard from Las Vegas): 2 × 150:1 LP 6 V micro metal gearmotor (2183-1097-ND, $23.95), Motoron M2T550 (2183-5079-ND, $15.95), VL53L1X carrier (2183-3415-ND, $22.95), U1V11F5 5 V boost (2183-2562-ND, $8.95; its cart reference says "LiDAR boost" but it is the servo's), FEETECH FS0307 sub-micro servo (2183-3420-ND, $10.21). From DigiKey (sales order 102785006, FedEx Ground): Adafruit 4410 USB-C charger (1528-4410-ND, $5.95). $111.91 + $18.44 shipping + $11.57 tax = $141.92. |
| DigiKey | Nov 10 | **3 more Same Sky `CES-20134-088PM` speakers** (2223-CES-20134-088PM-ND, $4.34 each, up from the $4.10 of September), sales order 102810661, web ID 379092784, submitted 2026-11-10 00:14 EST (DigiKey's order mails of 00:14 and 00:15); $13.02 + $4.99 USPS Ground Advantage + $4.53 tariff + $2.00 tax = $24.54; in stock, not shipped yet, expected about 11-13 to 11-16. Spares at the builder's word ("just in case"): shared stock, no project. Nine owned with these; Amazon does not list the part. |
| SendCutSend | Nov 9 | **Mars rover drums**: order SJ983673, 10 × `mars_rover_drum.dxf` (the rover's `cad/mars-rover-drum.dxf`), 35 × 35 mm, 16 seats and the 4.1 mm hub hole, 6061-T6 0.375 in, sheet cutting, no finish; $42.10 + $3.74 tax = $45.84, shipping free, estimated to ship 11-12. Checked 2026-11-09 on SendCutSend's Orders page and in its 2D preview of the part. |

**Status check 2026-11-03, 06:17 to 06:28 EST** (Amazon Orders page back to 2026-08-03, Gmail and the building's package log; the per-project list is `../../PARTS_BY_PROJECT.md`). Delivered 2026-11-02, no pick-up task yet: the four Cree XP-G2 stars (Amazon #24, one order of four, not two then four), the DigiKey box (MOSFETs, lens, piezos, the three DevKitC boards; FedEx, front desk 18:07), the Pololu rangers (USPS, 12:13) and the 14 ga sterling (Amazon #18, USPS, 12:11). The XIAO Sense boards: the drone's is now expected by 11-11, the camera pair by 11-15. Found on the Orders page and not logged above: two more 3-packs of the MAX98357 amplifier (114-5029591-3604223, 2026-10-11, delivered 10-14, nine amplifiers in all), a second Hosyond OLED 5-pack (114-8572576-9885850, 2026-10-22, delivered 10-26), a third INMP441 5-pack (114-3696034-7495405, 2026-10-19, delivered 10-20), two PowerBoost copies not one (Amazon #20 is 114-0663433-1244242 of 2026-10-11, delivered 10-19), seven 4-packs of K&S 1.5 mm tube (2026-09-02, 10-06, 10-07 and four on 10-19), eighteen 5-packs of K&S 1.5 mm rod, two packs of 0.5 mm rod (2026-10-12), and the Oct 1 Cyber Dawn alternates (two DIYmall DevKitC N16R8, a generic DS3231, a 5-pack of LIS3DH, five KY-040 encoders, a generic 2.42" OLED).

Estimated total spend: **≈ $635–660**, plus the DHO802 (Rigol list price $329; the price paid is not recorded here), $20.50 for five more speakers, and the 21 September Amazon consumables (prices not recorded).

---

# 1 · Electronics

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **Meshnology ESP32-C3 SuperMini** dev board | 10 | The brain. A postage-stamp ESP32-C3 board with Wi-Fi, native USB-C, and the GPIO layout the firmware targets. It runs the assistant, talks to the cloud backend, and drives every peripheral. **Gate each board with `esptool flash_id` — reject anything under 4 MB flash**, and reject any "Plus" variant with an RGB LED on GPIO8, which breaks this pin map. ⚠️ **2026-09-21: the received boards carry a ceramic chip antenna and hit the SuperMini's documented Wi-Fi range problem.** The red rectangular block at the end opposite USB is the antenna; there is no U.FL socket and no PCB trace antenna on these. The SuperMini design is widely reported to leave too little clearance around that antenna and to place it too close to other components, so the board interferes with itself — see [Elektor's antenna mod](https://www.elektormagazine.com/articles/boosting-wifi-range-of-the-esp32c3-supermini-antenna-mod). Symptom here: Step 10 provisioning logged `WifiConfigurationAp: Access Point started` and the OLED showed the config screen, but no phone or laptop could see the SSID at any distance — on three separate boards from this pack (A1 in the breadboard, and two spares bare on an open desk), so it is the batch, not one unit or the wiring. Keep the antenna end clear of jumper wires, modules and metal; a 31 mm quarter-wave wire mod recovers 6-10 dB if clearance alone is not enough. **What worked on A1 (2026-09-21, builder-reported, not instrument-verified):** capping Wi-Fi transmit power at 8.5 dBm (`esp_wifi_set_max_tx_power(34)`, quarter-dBm units) made the hotspot visible, A1 was provisioned onto Wi-Fi, and one spoken question returned a remote response (PASS 10C, same day); the source build now applies that cap after every radio start, so try the current assistant build before any wire mod. Ten boards means you can afford to throw out bad clones. **VBUS-01, 2026-09-22 (builder-measured on A1, diode mode):** A1's `5V` pin is wired directly to the USB-C VBUS, with no diode: 0.001 V with red on VBUS and 0.002 V with the probes swapped, beeping both ways. This matches the published SuperMini schematic ([sigmdel.ca](https://sigmdel.ca/michel/ha/esp8266/super_mini_esp32c3_en.html)), which shows VBUS tied straight to the `5V` header pin. Anything connected to `5V` is therefore connected to the computer's USB port. |
| **Hosyond SSD1306 OLED**, 0.96" 128×64 I²C, white | 5 | The screen — the device's only visual output, showing state, the pairing code, and responses. White pixels on black glass are also the intended white/silver accent. Firmware probes both `0x3C` and `0x3D`, so either address works. **Read the silkscreen pin order before wiring**: vendors ship GND-VCC-SCL-SDA *and* VCC-GND-SCL-SDA on identical-looking boards. |
| **AITRIP INMP441** I²S MEMS microphone | 5 | The ears. A digital microphone that outputs I²S directly, so no analog audio wiring is needed. This is the creator's exact part. Tie `L/R` to GND to select the left slot; data goes to GPIO4. **Keep flux, IPA, glue, paint, and compressed air away from the acoustic port** — contaminating it is permanent. |
| **HiLetgo MAX98357** I²S class-D amplifier | 3 | Converts I²S to speaker output. Used in fast-track Step 11, powered only from the controller's `5V` pin; keep it disconnected before Step 11. Its supply range alone does not define a complete power circuit. Later inspect the exact carrier's gain and `SD/MODE` network: shutdown can be intentional, and mono-mix can attenuate left-only source audio. Do not change the mode or power it from a raw cell based on this inventory. |
| **Same Sky CES-20134-088PM** speaker, 8 Ω 0.8 W | 6 (+ 3 ordered 2026-11-10) | The mouth. A factory-enclosed micro-speaker — the sealed rear cavity is what makes it audible at this size, and it removes the hardest acoustic problem in the build. 20 × 13 × 4.87 mm, top-firing, with two mounting flanges and a built-in dust mesh. Ships with 60 mm of 32 AWG lead, longer than the whole device, so **it needs no wire from you**. Cap output at ≤ 2.53 V RMS differential to respect the 0.8 W rating. Four bought 2026-09-02 and two more 2026-10-01, all from DigiKey at $4.10 each (count corrected 2026-11-03 from the DigiKey account; the 09-21 order once logged here does not exist), so no single unit is irreplaceable; three more at $4.34 were ordered 2026-11-10 as spares (DigiKey 102810661, due about 11-13 to 11-16), nine in all once they land. Still never cut the leads of a unit you intend to use. |
| **QTEATAK tactile push buttons** | 420 | The only user control: a momentary button on GPIO10 to ground. Short press toggles chat, long press resets Wi-Fi. Pick a white cap to match the finish. Note the onboard GPIO9 button is ROM BOOT, not this input. |
| **2.54 mm male breakaway header pins** | 22 | Snap-apart pin strips for soldering onto modules so they can plug into a breadboard. Makes the whole Phase 0 bench stack reversible instead of permanent. |

# 2 · Power

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **Adafruit #1578** LiPo 3.7 V **500 mAh**, protected | 2 | Previously purchased compact battery candidate, nominally 29 × 36 × 4.75 mm. Keep disconnected and terminal-protected. The current material review records a 0.5 A maximum continuous-discharge rating and rejects it for the former estimated load; ownership is not permission to use it. Never solder to or alter its factory lead. |
| **Adafruit #258** LiPo 3.7 V **1200 mAh**, protected | 2 | The margin battery option, 34 × 62 × 5 mm. Roughly 1.2 A capable and more than twice the runtime, but 62 mm long — longer than the intended device — so fitting it changes the silhouette. Buying both sizes turns the capacity-vs-size argument into a measurement. |
| **Adafruit #4410** USB-C Micro-Lipo charger | 1 | Purchased LiPo charger, with a default 100 mA setting and no load sharing. Store separately from the USB prototype. A future charging arrangement needs its own wiring procedure; the slide-switch OFF position alone is not evidence of source isolation. Leave the charge-rate jumper unchanged. |
| **Chanzon SPDT mini slide switch** | 25 | Purchased switch samples. Useful for unpowered continuity exercises; not selected to carry the final device's battery current. The beginner prototype turns off by unplugging its USB cable. |
| **daier JST-PH 2.0 mm** 2-pin connector cables | 20 pr | Mating connectors for the battery. Their real value is bench testing: they let the current-limited power supply stand in where the battery goes, so the whole power chain is proven before a cell is ever connected. ⚠️ **Verify polarity with the meter, not wire color** — generic JST-PH leads are frequently wired opposite to Adafruit's convention. |
| **LuminologyPro resistor kit**, 25 values, 1/4 W | 1000 | Pull-up and pull-down resistors. 10 kΩ holds the I²S bit clock line GPIO2 (a boot-strap pin) at a defined level; 100 kΩ pulls down the microphone data line GPIO4. The action button needs no external resistor: it goes from GPIO10 to GND and the firmware enables the chip's internal pull-up (as wired and passed in fast-track Step 6). Without these the board can boot unpredictably. |
| **BOJACK ceramic capacitor kit** | 650 | Local decoupling — small capacitors placed at each module's power pins that supply the instantaneous current spikes digital chips demand, which long wires cannot deliver fast enough. 100 nF and 10 µF are the values used here. |
| **ALLECIN electrolytic capacitor kit**, 24 values | 1 kit | Bulk energy storage. The 220 µF sits at the amplifier's power input as a reservoir for bass notes and Wi-Fi transmit bursts, which would otherwise drag the shared battery rail down and reset the processor. |

Both cell sizes remain stored and terminal-protected. Portable battery power is
out of scope for this prototype by the builder's decision of 2026-09-21. Battery selection is later work and depends on a complete power
design and measured demand.

# 3 · Frame, insulation, and wire

| Item | What it is and why it is here |
| --- | --- |
| **K&S #9831 brass tube**, 1.5 mm OD × 0.225 mm wall × 300 mm, 4 tubes | The frame itself — the exposed brass cage that gives the device its look and holds everything together. The reference build's exact stock. The wall is only 0.225 mm, so it must be cut with the jeweler's saw; flush cutters crush it. ASIN verified to resolve to 9831 and not a wrong-diameter variant. |
| **K&S #9862 1.5 mm round brass rod**, 5 rods, bought 2026-10-20 | Solid 1.5 mm brass: about 30 % stiffer than the 1.5 mm tube at the same diameter, solders with the Harris flux the same way. Frame loops/posts where the tube felt soft, and the free-wire lines of the next project. |
| **K&S 1.0 mm round brass rod**, 10 rods (two packs; second bought 2026-10-08) | Corner posts and cross braces. Solid rod, so it is stiffer than the tube and telescopes inside it (tube ID ≈ 1.05 mm) for clean joints. |
| **615 coreless motors**, 6 × 15 mm, 0.8 mm shaft, 8 pieces (4 CW + 4 CCW, two packs), bought 2026-10-28 | The XS drone's lift motors plus a spare set; coreless motors wear out after a few hours of flight. Not a Pocket AI or Cyber Dawn part. |
| **31 mm four-blade props**, 0.8 mm bore, 16 pieces, bought 2026-10-28 | The XS drone's propellers, four sets; CW on CW motors. |
| **Cree XP-G2 on a 20 mm Indus Star**, cool white, 6 pieces, bought 2026-10-28 | The XS drone's flashlight emitter, one plus a spare; needs the Carclo 10412 lens and AMC7135 regulators still on the drone's buy list. Not a Pocket AI or Cyber Dawn part. |
| **XIAO ESP32-S3 Sense**, 3 (two bought 2026-10-27 for the camera tower, one 2026-10-28 for the drone) | One each: the camera tower, the XS drone, and the Pocket AI Sphere (third board allocated 2026-10-30). The Oct 27 pair is recorded in pocket_ai_assistant_with_camera/docs/COMPONENTS.md. |
| **Crazepony 1S 250 mAh 30C LiPo**, Micro JST 1.25, 4 packs, bought 2026-10-28 | The XS drone's flight packs, one per flight; also the floor pan of the body. Charge on the Adafruit #4410 at 100 mA, about 2.5 h each. |
| **JST 1.25 mm 2-pin connector leads**, 30 pairs, bought 2026-10-28 | Battery and charger leads for the Crazepony packs. Not the same as the PH 2.0 cables. |
| **Chanzon SS14 Schottky diodes**, 100, bought 2026-10-28 | Flyback diodes across the drone's four motors; band toward VBAT. |
| **Ximimark GY-521 MPU6050**, 10 boards, bought 2026-10-28 | Spares since 2026-11-07: the drone and Crumb now take theirs from the HiLetgo 3-pack (next row), which lands weeks earlier. |
| **HiLetgo GY-521 MPU-6050**, 3 boards, bought 2026-11-07 | The drone's tilt and yaw sensor (one) and Crumb's (one); one spare. Leave the header off the drone's. |
| **MEBMIK clear heat tape**, 12 rolls of 10 mm × 33 m, bought 2026-11-07 | The drone's finish: straps, and clear tape over white card patches on its boards and pack labels. Polyester film, heat-resistant adhesive; eleven rolls spare. |
| **AMC7135 350 mA LED drivers**, 10, bought 2026-10-28 | The drone's flashlight regulators (two in parallel). |
| **Pololu VL53L1X carrier #3415**, 2, ordered 2026-10-28 | The XS drone's down-looking laser ranger for altitude hold; one spare. |
| **Pololu VL53L7CX carrier #3418**, 2, ordered 2026-10-28 | The XS drone's forward 8 × 8 laser ranger. Fit last, after height hold flies. The spare is drawn into the Mars rover's head (Rev J, approved 2026-11-09). |
| **Carclo 10412 lens**, 2, ordered 2026-10-28 | The flashlight optic, 23° beam on the XP-G2; one spare. |
| **AO3400A SOT-23 N-MOSFET**, 10, ordered 2026-10-28 | The drone's four motor switches, plus the flashlight fallback switch and spares. |
| **TDK PS1240P02BT piezo**, 10, ordered 2026-10-28 | The drone's beeper, wired across the flashlight LED; the rest are spares for any project. |
| **ESP32-S3-DevKitC-1-N8R8**, 3, ordered 2026-10-28 | Cyber Dawn's controller (one) and two spare ESP32-S3 dev boards; not drone parts. |
| **uxcell 1 mm × 300 mm 304 stainless rod**, 20 pieces in two orders ([B082ZNWQ5Q](https://www.amazon.com/dp/B082ZNWQ5Q)), bought 2026-10-28, on hand since 2026-11-05 | The XS drone's frame rod: rails, axles and bars of the ladder frame, 277 mm (one rod); 19 spare. Solders with the Harris acid flux like the 1.5 mm coupons. Not a Pocket AI or Cyber Dawn part. |
| **uxcell 1.5 mm × 150 mm 304 stainless rod**, 10 pieces ([B082ZNMD46](https://www.amazon.com/dp/B082ZNMD46)), bought 2026-10-27 | Solder-test coupons for the stainless builds that follow Cyber Dawn (drone onward); the Pocket AI frames and Cyber Dawn stay brass. Stainless soft-solders with the Harris acid flux once the oxide is sanded off and the joint is held hot longer than brass needs; the fillet is smaller and the joint about half as strong, so lap joints only. Notches the flush cutters: jeweler's saw only. Rinse the acid flux hard or the joint line rusts. |
| **XFJYMXDM fish paper**, 16.4 ft | Flame-rated electrical insulation board that lines the battery bay. This is the mandatory barrier between the lithium cell and everything else — the one insulation layer that is a safety requirement rather than good practice. |
| **ELEGOO polyimide (Kapton) tape**, 4-pack | High-temperature insulating tape for module backs and anywhere a wire crosses brass. Survives soldering heat without melting, unlike vinyl electrical tape. |
| **Pointool heat-shrink tubing kit**, 14 sizes, **white** | Tubing that shrinks tightly around a solder joint when heated, insulating it and adding a little strain relief. White matches the intended finish. |
| **TUOFENG 26 AWG silicone wire**, 6 colors, 33 ft each | The power wiring — battery bus and any load-carrying run. Thicker than the signal wire for mechanical robustness at the connection you least want to fail. Silicone insulation stays flexible and resists soldering-iron burns. |
| **CBAZY 30 AWG silicone wire**, 6 colors, 32.8 ft each | The signal wiring — I²C to the display, I²S to the microphone and amplifier, and the button. Thin and flexible so 15+ conductors can be routed inside a 45 mm cage without levering on fragile breakout pads. |

### Wire-gauge note — current is not the deciding factor

The "26 AWG for power" rule came from the withdrawn R0 design, which pushed
~1.15 A through a long chain. The current frame is ~45 mm and the chain is
three parts, so on **current** either gauge is comfortable:

| | 30 AWG | 26 AWG |
| --- | ---: | ---: |
| Resistance | ~0.34 Ω/m | ~0.13 Ω/m |
| Loop drop @ 0.8 A peak, 160 mm | 43 mV | 17 mV |
| Loop drop @ 150 mA average | 8 mV | 3 mV |

Both are far inside the ≤300 mV upstream-drop screen. The real trade is
**mechanical**: 26 AWG resists nicking and fatigue on the battery bus, while
30 AWG routes without stressing pads on the signal side. Both are on hand —
use each where it belongs, and strain-relieve every conductor either way.

# 4 · Tools — soldering

| Item | What it is and why it is here |
| --- | --- |
| **JoTownCand solder wick**, 3-pack, 3 widths, bought 2026-09-21 | Braided copper that lifts solder off a joint: the way to clear a bridge or remove header pins. Use the narrowest width on OLED, microphone and amplifier pads, with a touch of flux, and cut off the used end each time. |
| **Epic Medical Supply 91% isopropyl alcohol**, 2 × 16 oz, bought 2026-09-21 | Cleans flux residue off boards and rinses the brass after acid flux. 91% has little enough water to evaporate cleanly; keep it away from the microphone's acoustic port and away from flame or a hot iron. |
| **X-Tronic 3020-XTS station** + 5 tips, solder roll, solder sucker, tweezers, 2 helping hands, silicone mat | Temperature-controlled soldering iron and the bench kit around it. Temperature control matters because a MEMS microphone and an OLED flex tail are heat-sensitive. The helping hands hold parts while both of yours are busy; the silicone mat is the only heat-safe work surface you own. |
| **MAIYUM 63/37 rosin-core solder**, 0.8 mm, 100 g | Electronics solder. The 63/37 tin-lead alloy melts lower and wets faster than lead-free, meaning less time with a hot iron pressed against fragile parts. Wash hands, do not eat at the bench, ventilate. |
| **Chip Quik CQ4LF no-clean flux pen**, 10 ml | Flux chemically strips oxide off metal so solder actually bonds instead of balling up. "No-clean" residue is safe to leave on electronics. ⚠️ Duplicate — one was already owned. |
| **Harris SCLF4 Stay-Clean flux**, 4 oz | A far more aggressive **acid** (zinc-chloride) flux, needed because brass oxidizes too fast for rosin flux to handle. **Empty brass frame only — never near electronics.** It is corrosive and must be washed off and neutralized with baking soda, or it will eat the joints and blister any paint later. |

# 5 · Tools — measurement

| Item | What it is and why it is here |
| --- | --- |
| **KAIWEETS TRMS multimeter**, 6000 counts, + hard case | The most important instrument in the build. Every safety step is a meter step: battery polarity before the first connection, checking the brass frame is isolated from every circuit, continuity, switch voltage drop, charge termination voltage. Nothing electrical gets connected without it. |
| **SKY TOPPOWER DC supply**, 0–30 V / 0–5 A | An adjustable, **current-limited** bench power supply that substitutes for the battery during testing. If something is wired wrong it politely limits current instead of dumping a lithium cell's full energy into the fault. This is what lets the entire power chain be proven before a cell is ever installed. |
| **Rigol DHO802 oscilloscope**, 70 MHz, 2 channels + external trigger, 12-bit, two PVP3150 10X probes, bought 2026-09-21, **not yet received** | Shows voltage against time, which the multimeter cannot: clock edges, rail dips during Wi-Fi bursts, power-up order, and the speaker's differential signal. Two channels with both probe grounds on circuit ground plus its A−B math give the differential-safe speaker measurement the audio gate asks for; **never clip a probe ground to either speaker lead**. Its Single trigger mode catches one-off start-up events. Powered from a USB-C 15 V adapter; before first use, meter whether the BNC shells connect to the adapter's earth and to the rear GND terminal, and record the answer. Warranty three years on the mainframe, not the probes. It does not measure millisecond current peaks or log a charge cycle. |
| **NEIKO digital caliper**, 0–6" | Measures parts to a hundredth of a millimetre. Every module, board, and connector needs its real measured size before the frame geometry can be trusted — listing dimensions are frequently wrong. |
| **REXQualis breadboards**, 4 pcs (830 + 400 point) | Use for resistor labs and the controller's button/OLED/microphone connections. Check split power rails and header joints before use. Amplifier supply and speaker current do not go through breadboard contacts. Loose module headers must be soldered and inspected before jumper testing. |
| **TODOELEC Dupont jumper kit**, 120 wires, 10 cm | Pre-terminated jumper wires for breadboarding. Bench use only — not for final assembly, and never for the speaker output or high-current runs. |

**Instrument decision, 2026-09-21:** the DHO802 is the last instrument purchase. The purchase authority's remaining `ARRANGE` instruments — the fast current meter, the calibrated charge-voltage logger, and the three-channel temperature logger — are to be borrowed or rented if needed. Until access exists, the gates that name them stay closed.

# 6 · Tools — fabrication and safety

| Item | What it is and why it is here |
| --- | --- |
| **SE 3-in-1 jeweler's saw** + 144 blades + V-slot bench pin with clamp | The only correct way to cut 0.225 mm-wall brass tube — a fine-toothed blade removes material without crushing the tube. The bench pin clamps to the table and supports small work while you cut. |
| **WORKPRO jewelry pliers**, 3-pack | Round-nose and chain-nose pliers for bending brass into the frame's rectangles and forming braces. Round jaws make smooth curves without kinking the tube. |
| **BOENFU 6-inch flush cutters** ([B07C5PM8L4](https://www.amazon.com/dp/B07C5PM8L4), listing confirmed by the builder 2026-10-10) | Clip header pins to 2 mm stubs, trim 1 mm brass rod and component leads. Never the 0.225 mm-wall tube: the cutters crush it; the jeweler's saw cuts it. |
| **Hakko CHP CSP-30-1 wire stripper**, 30–20 AWG ([B00FZPHMUG](https://www.amazon.com/dp/B00FZPHMUG)) | Removes insulation without nicking the conductor. Sized correctly for both wire gauges here; a blade or generic stripper nicks fine strands, which then break later inside a sealed frame. |
| **QWORK mini heat gun**, 300 W, with stand | Shrinks the heat-shrink tubing. Directed hot air is controllable in a way a lighter is not — no soot, no scorching adjacent insulation. |
| **SHJADE hot glue gun**, 20 W mini, + 30 sticks, white | Low-temperature adhesive for retaining modules in the frame — the reference build's own method. Low-temp matters near plastic module bodies and the OLED. Keep glue away from the microphone port, the switch mechanism, and connectors. |
| **SE 10-piece diamond needle file set**, 150 grit, 744DF-R | Small shaped files for deburring cut tube ends and fine shaping. ⚠️ **See the note below — diamond is not ideal for brass.** |
| **BAISDY wet/dry sandpaper**, 45 sheets, 400–3000 grit, bought 2026-09-21 | Deburrs every cut brass edge so none can cut a wire or a hand; 400–800 does the deburring, the finer grits polish or key a surface before paint. Sand brass wet or with a mask, well away from the electronics. |
| **3M Solus 1000 safety glasses**, clear | Eye protection for sawing, filing, and clipping wire, all of which throw metal fragments. Wear them; the saw is the sharpest thing on the bench. |
| **KraftSense 20 V brushless cordless drill set** with a 2.0 Ah battery, bought 2026-10-11 (Amazon order history; added to this record 2026-11-09 after the desk lighthouse's parts list assumed no drill was owned) | The bench's drill for brass sheet, discs and coasters. Check its case for metric bits under 3 mm before buying any; the lighthouse wants 1.8, 2.3, 3.5 and 3.6 mm. |

### ⚠️ Note on the diamond file set

Diamond files cut by holding abrasive grit in a metal surface. Soft metals —
brass, copper, aluminium — pack into the gaps between the grit and the file
stops biting. They are excellent on glass, stone, and hardened steel, and they
will do light deburring on brass, but they will load up and dull with repeated
use.

This is not a problem to fix urgently:

- **Clean them** with a stiff brass brush when they load up, and they keep working.
- **Sandpaper does most of this job anyway.** Deburring a thin tube end is
  mostly a few strokes of 400–800 grit wet/dry, now in hand (bought 2026-09-21).
- **If filing gets frustrating**, a steel needle file set in cut 2 is about
  $10 and is the correct tool for brass.

Keep the diamond set — it earns its place on the harder materials.

---

## Still needed

A working data cable was proven at fast-track Step 3, and the 21 September
order covered the wick, sandpaper and alcohol, so nothing below blocks the
build. What remains is small and local.

| Item | Why | Approx. |
| --- | --- | ---: |
| ~~Swabs · baking soda~~ — **bought locally, 2026-10-08** (builder-reported) | For the Harris acid flux: baking soda neutralizes it and the owned 91% IPA rinses it off. Residue left on brass corrodes joints and blisters paint | done |
| Gel cyanoacrylate (super glue) — optional | Spot-bonding where hot glue is too bulky; keep it and its fumes away from the microphone port and the OLED glass | ~$5 |
| USB-A-to-C data cable, spare — optional | One proven cable is enough; a spare helps once one stays plugged into the finished device | ~$10 |

### Optional — white/silver finish

White system. **Bought 2026-09-21:** both topcoats, Rust-Oleum `7789830` gloss
canvas white, a warm off-white, and `7791830` satin white. **Not bought:** the
`7780830` white primer. The Rust-Oleum 249322 dark-green self-etching primer
was ordered and then canceled the same day.

1. Sand the bare brass with the owned 400–600 wet/dry and wipe it with the owned
   91% IPA, so the paint has a clean, keyed surface.
2. Rust-Oleum `7780830` Stops Rust Clean Metal Primer, flat white
   ([B000Z8C3PM](https://www.amazon.com/dp/B000Z8C3PM)).
3. One topcoat, chosen on the test coupons: Rust-Oleum `7791830` satin white
   ([B000Z8FGII](https://www.amazon.com/dp/B000Z8FGII)) or `7789830` gloss
   canvas white ([B000PIG3AS](https://www.amazon.com/dp/B000PIG3AS)). Use one
   sheen on the whole frame.

Without an etching primer, adhesion on smooth non-ferrous brass is the open
question, so the finish stays gated: spray test coupons cut from brass offcuts
first and check that the paint does not lift, and paint the frame only after
the fit and Wi-Fi checks pass. If the coupons peel, an etching primer returns
under the white coats. NYC Admin Code §10-117 keeps spray paint 21+ and locked.
Spray the empty frame outdoors or with strong ventilation, never with
electronics installed, and store cans away from the soldering iron and heat
gun. White styrene sheet for guards (~$10, Blick or Canal Plastics) remains
optional.

---

## What to do first

Follow the [action-only fast track](../plan/FAST_TRACK.md): identify and flash
one bare controller, prepare reliable headers, add the button and OLED, then
observe microphone levels in the offline diagnostic firmware. This uses the
controller's USB supply and needs no cloud account, amplifier, battery, or
enclosure. Save a wiring photograph and the serial output at each step. The
[USB prototype quickstart](PROTOTYPE_QUICKSTART.md) remains the compact
technical reference.

After those local tests pass, the regular source firmware provides the next
software/backend experiment. Speaker output and portable power remain separate
integration tasks; buying the parts did not verify them.
