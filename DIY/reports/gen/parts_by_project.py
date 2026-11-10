#!/usr/bin/env python3
"""Parts by project: one data table, two outputs.

Writes DIY/PARTS_BY_PROJECT.md and DIY/reports/parts-by-project.html from the
same rows, so the markdown and the page always agree. Edit the data here, then run:

    python3 reports/gen/parts_by_project.py

Statuses were read from the builder's accounts on 2026-11-03 (times in the READ
constant). Links are the exact listings bought; order numbers sit in the "From"
column, never in prose.
"""
from __future__ import annotations

import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]  # DIY/
MD_OUT = ROOT / "PARTS_BY_PROJECT.md"
HTML_OUT = ROOT / "reports" / "parts-by-project.html"
ARTIFACT_URL = "https://claude.ai/artifact/E2PSC4iZ7cr86nwhN6DWsc"

READ = {
    "date": "2026-11-03",
    "amazon": "Amazon Orders page, signed in, 207 orders back to 2026-08-03, read 06:17 to 06:28 EST",
    "mail": "Gmail (DigiKey, Adafruit, UPS and IMR Batteries mails) and the building's package log, read 06:20 to 06:27 EST, and again at 17:15 EST for today's Amazon deliveries",
    "todoist": "Todoist, label package: 3 completed pick-up tasks (all 2026-11-01), 0 open, read 06:20 EST; re-read 17:15 EST, when the four 11-02 tasks showed completed at 15:00",
    "digikey": "DigiKey account (Order History, the invoice list and the three order pages), signed in by the builder, read 06:45 to 06:49 EST",
    "adafruit": "Adafruit account (Order History and its three order pages), signed in by the builder, read 06:46 to 06:48 EST",
}


def amz(asin: str) -> str:
    return f"https://www.amazon.com/dp/{asin}"


def ada(pid: int) -> str:
    return f"https://www.adafruit.com/product/{pid}"


IMR_NL169 = "https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery"
IMR_IMREN = "https://imrbatteries.com/search?q=IMREN+18350+800mAh"
DK_DEVKIT = "https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894"
DK_AO3400 = "https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089"
DK_SPEAKER = "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309"
DK_CARCLO = "https://www.digikey.com/en/products/result?keywords=1066-1042-ND"
DK_PIEZO = "https://www.digikey.com/en/products/result?keywords=PS1240P02BT"
POLOLU_7CX = "https://www.pololu.com/product/3418"
POLOLU_1X = "https://www.pololu.com/product/3415"
SPARKFUN_VCNL = "https://www.sparkfun.com/products/15177"

# Status vocabulary (the first words decide the styling):
#   on hand ...        delivered, with the date and the evidence
#   in transit ...     with the expected date
#   not ordered ...    nothing bought yet
#   cancelled ...      the order was cancelled
ON_HAND_IMR = "on hand · both IMR boxes at the front desk 2026-10-21 (building log)"
ON_HAND_DK = "on hand · DigiKey's order page says Delivered; FedEx box at the front desk 2026-11-02 18:07 (building log); picked up 2026-11-03 (pick-up task completed 3 p.m.)"
ON_HAND_POLOLU = "on hand · USPS box at the front desk 2026-11-02 12:13 (building log; DigiKey's page still says Shipped); picked up 2026-11-03 (pick-up task completed 3 p.m.)"
ON_HAND_ADA1 = "on hand · UPS box at the front desk 2026-10-21 (building log; Adafruit's page says only Shipped)"
ON_HAND_ADA2 = "on hand · delivered 2026-10-28 (Adafruit's order history and the building log)"
TODAY = "on hand · delivered to the front desk 2026-11-03 12:53 (Amazon mails; building log 12:59 to 13:41), Crumb's order in three boxes with the LED filaments riding in the gears' box; sorted at the bench the same afternoon"
XIAO_11 = "in transit · arriving 2026-11-08 to 11-11 (Amazon Orders page, read 2026-11-09; was 11-15)"
XIAO_15 = "in transit · now expected by 2026-11-15 (was 11-23)"
GY521 = "in transit · 2026-11-19 to 12-15"
GY521_FAST = "on hand · delivered 2026-11-09 to the mail room (Your Orders, read that evening); on the bench in a photo 2026-11-10"

# Each project: (title, folder, intro, rows). Row: (qty, name, url, source, status, note).
PROJECTS = [
    (
        "Crumb, the desk robot",
        "desk_robot",
        "Nothing of Crumb's own has arrived yet. The main box with the motors, gears, driver, "
        "screen and amplifiers is due today; the controller lands by 11-11; the motion sensor now comes "
        "from a 3-pack ordered 11-07 instead of the 11-19 to 12-15 pack. The two laser rangers and the fuel gauge are shared parts "
        "already in the building.",
        [
            ("1", "controller with camera and microphone", amz("B0C69FFVHH"),
             "Amazon 114-5249290-9043412, 2026-10-31", XIAO_11,
             "Crumb's own board. The other three boards are the drone's, the camera Pocket AI's and the Sphere's."),
            ("1 of 3", "1.54 inch colour display, 3-pack", amz("B0HGLQZK3P"),
             "Amazon 114-6045175-2593056, 2026-10-31", TODAY, "Two spare screens for other builds."),
            ("2", "64-tooth steel spur gears, one per listing", amz("B0881RWD2L"),
             "Amazon 114-6045175-2593056", TODAY, "The wheels. Caliper the diameter on arrival; the pinions are spare."),
            ("2 (one pack)", "N20 gear motors, 2-pack", amz("B0C9QC4SRY"),
             "Amazon 114-6045175-2593056", TODAY, "Both drive motors."),
            ("1", "I²C motor driver", amz("B07YCVHQD5"),
             "Amazon 114-6045175-2593056", TODAY, "Cut its pull-up jumper before it joins the bus."),
            ("1 of 12", "I²S amplifier, 3-pack", amz("B0CDWXZZCH"),
             "Amazon 111-8554202-0502625 (3, 2026-09-02) and 114-5029591-3604223 (6, 2026-10-11); 3 more in 114-6045175-2593056",
             "on hand · 9 delivered 2026-09-03 and 10-14; 3 more delivered 2026-11-03 with Crumb's box",
             "Take one of the nine on hand. Pip, Cyber Dawn, the Sphere and the camera Pocket AI take one each; 12 in all once today's box lands."),
            ("1 of 2", "8×8 laser ranger", POLOLU_7CX,
             "DigiKey marketplace (Pololu), order 102531268, invoice 135297191, USPS", ON_HAND_POLOLU,
             "The drone takes the other. None spare."),
            ("1 of 2", "single-zone laser ranger", POLOLU_1X,
             "DigiKey marketplace (Pololu), order 102531268", ON_HAND_POLOLU, "The drone takes the other. None spare."),
            ("1 of 3", "motion sensor, 3-pack", amz("B00LP25V1A"),
             "Amazon 114-1259113-3701002, 2026-11-06", GY521_FAST,
             "The drone takes one; one spare. The pack is in the XS drone bin (builder, 2026-11-10): take Crumb's from there. The 10-pack is all spare."),
            ("1 of 2", "fuel gauge", ada(5580),
             "Adafruit 3771280, 2026-10-26, UPS", ON_HAND_ADA2, "Cyber Dawn takes the other. None spare. In the Crumb bin (builder, 2026-11-10)."),
            ("1 of 6 + 3 ordered", "enclosed speaker", DK_SPEAKER,
             "DigiKey 101368762, 2026-09-02 (4) and 101971685, 2026-10-01 (2); 3 more in 102810661, 2026-11-10", "on hand · DigiKey's pages say Delivered (FedEx 541958299829 and 545372714918); the three of 11-10 not shipped yet, due about 11-13 to 11-16",
             "Pip, the Sphere, the camera Pocket AI, the drone and rover Rev K take one each too: none spare until the three of 11-10 land. Six owned, not eight: no 09-21 order exists."),
            ("1 of 13", "16340 cell, protected", IMR_NL169,
             "IMR Batteries 20739060 (7) and 20739061 (6), both 2026-10-16, UPS", ON_HAND_IMR,
             "Five builds take one each; eight spare."),
            ("1 of 10", "16340 holder with leads", amz("B0CRGK889F"),
             "Amazon 114-1421763-3353854, 2026-10-27", "on hand · delivered 2026-10-30",
             "Seven builds take one each; three spare. The pack is in the shared bin (builder, 2026-11-10)."),
            ("1 of 20", "toggle switch", amz("B0CZ6XZ2P9"),
             "Amazon 114-1421763-3353854", "on hand · delivered 2026-10-30", "Three builds take one each; 17 spare."),
            ("1 of 420", "tactile button", amz("B0FHW6HMG4"),
             "Amazon 111-8554202-0502625, 2026-09-02", "on hand · delivered 2026-09-04", "Every build takes one or two."),
            ("2 of 7", "100 mm QT cables", ada(4210),
             "Adafruit 3765988, 2026-10-19, UPS", ON_HAND_ADA1,
             "Cyber Dawn takes five, so none are spare: the four extra ordered on Amazon were cancelled."),
            ("2 + 6", "10 kΩ resistors ×2; 220 µF, 100 µF, 10 µF, 1 µF and two 100 nF capacitors", amz("B0F4P352BB"),
             "resistor kit (linked), electrolytic kit 111-6329624-3227449, ceramic kit 111-8554202-0502625, all 2026-09-02",
             "on hand · delivered 2026-09-02 and 09-04", "Pull the values; the kits stay in bench stock."),
            ("about 4 rods", "1.0 mm brass rod, 5-packs", amz("B005WPB7YG"),
             "Amazon 111-4723174-9565024 (09-02), 114-8041650-5363423 (10-07), 114-1256902-8439449 (10-10)",
             "on hand · delivered 2026-09-04, 10-12, 10-12", "Shared brass; count the drawer before cutting."),
            ("about 18 mm of 4 mm and 5 mm", "brass tube set, 2 to 7 mm, 200 mm", amz("B0F2FKLC2N"),
             "Amazon 114-9676073-9134626, 2026-10-26 (3 sets)", "on hand · delivered 2026-10-28",
             "The hubs. More 330 mm sets due 11-06 to 11-13 and 11-13 to 11-19 (shared stock)."),
            ("as needed", "26 AWG and 30 AWG silicone wire, Kapton, fish paper, heat-shrink", amz("B073RDGTPB"),
             "bench stock, 2026-09-02", "on hand", "See shared stock."),
            ("1, optional", "external 16340 charger", "https://www.amazon.com/s?k=nitecore+ui1",
             "nothing bought", "not ordered · optional", "Shared with the Pocket AIs if it is ever bought."),
            ("bench", "15× magnifying lamp", amz("B0GK845R6R"),
             "Amazon 114-0252936-2851446, 2026-10-31", "on hand · delivered 2026-11-01, picked up 2026-11-01",
             "With the safety glasses (next row): Crumb's bench, already collected."),
            ("bench", "safety glasses", amz("B0017D3UIS"),
             "Amazon 114-8031860-5409814, 2026-10-31", "on hand · delivered 2026-11-01, picked up 2026-11-01", ""),
        ],
    ),
    (
        "XS drone",
        "xs_drone",
        "The drone's electronics are all in the building: the DigiKey switches, lens and beepers came by "
        "FedEx and the Pololu rangers by USPS, both at the front desk on 11-02, the same day as the four "
        "flashlight emitters. The frame rod came in two boxes on 11-04 and 11-05. Still in the mail: motors, "
        "propellers, the regulators and the motion sensor; the controller lands by 11-11. Added 2026-11-09 for the voice build: "
        "a speaker from Pip's stock and an amplifier board, ordered 11-09 (arriving 11-12). The lift revision was approved 2026-11-10 and its Amazon lines were ordered that night (arriving 11-12): 7 × 20 mm motors, an I2C multiplexer, two 2-packs of black rangers, a tilt servo; the grey 40 mm props wait in the tinywhoop.com cart; the frame goes to owned brass rod.",
        [
            ("1", "controller with camera and microphone", amz("B0C69FFVHH"),
             "Amazon 114-5295722-2709061, 2026-10-27", XIAO_11, "The drone's own board."),
            ("4 fitted + 4 spare", "615 coreless motors, two 4-packs", amz("B09J236JJL"),
             "Amazon 114-5815387-7733816, 2026-10-27", "on hand · on the builder's desk in a Webcam Snap photo 2026-11-10 01:23, early (Amazon said 11-13 to 11-24)", "In the XS drone bin (builder, 2026-11-10). Spares: the lift revision, approved 2026-11-10, flies 7 × 20 mm motors."),
            ("16 (four sets)", "31 mm four-blade propellers", amz("B09L4MXXCW"),
             "Amazon 114-4118122-0736259, 2026-10-27", "on hand · on the builder's desk in a Webcam Snap photo 2026-11-10 01:23, early (Amazon said 11-13 to 11-24)", "In the XS drone bin (builder, 2026-11-10). Spares: the lift revision, approved 2026-11-10, flies 40 mm props."),
            ("4", "250 mAh 1S flight packs", amz("B0FCMLVCN2"),
             "Amazon 114-5201101-3840264, 2026-10-27", "on hand · delivered 2026-10-30", "One per flight; also the floor pan."),
            ("2 of 30 pairs", "JST 1.25 mm 2-pin leads", amz("B0GW5WWZTY"),
             "Amazon 114-3670533-2737853, 2026-10-27", "on hand · delivered 2026-11-01, picked up 2026-11-01",
             "Battery lead and charger lead, only if the packs keep their 1.25 plugs; the build re-terminates them to PH 2.0. In the XS drone bin (builder, 2026-11-10)."),
            ("1 of 3", "motion sensor, 3-pack", amz("B00LP25V1A"),
             "Amazon 114-1259113-3701002, 2026-11-06", GY521_FAST,
             "Crumb takes one; one spare. The pack is in the XS drone bin (builder, 2026-11-10). Bought so the IMU step need not wait for the 10-pack (11-19 to 12-15), now all spare."),
            ("about 0.3 m of 12 rolls", "clear heat tape, 10 mm", amz("B0BD84GGPV"),
             "Amazon 114-0986744-9273034, 2026-11-07",
             "in transit · arriving 2026-11-09 (Amazon Orders page, read 2026-11-09)",
             "The finish: battery and speaker straps; no card, no skins (builder's rule 11-09). Eleven rolls spare for any project."),
            ("4 of 100", "Schottky diodes", amz("B079KJ46ZS"),
             "Amazon 114-5201101-3840264", "on hand · delivered 2026-10-30", "The satellite takes one."),
            ("4 + 1 of 10", "N-channel MOSFETs", DK_AO3400,
             "DigiKey order 102531269, invoice 135297233, FedEx Ground", ON_HAND_DK,
             "The same box holds Cyber Dawn's three controller boards."),
            ("1 of 2", "8×8 laser ranger", POLOLU_7CX,
             "DigiKey marketplace (Pololu), order 102531268, invoice 135297191, USPS", ON_HAND_POLOLU, "Crumb takes the other."),
            ("1 of 2", "single-zone laser ranger", POLOLU_1X,
             "DigiKey marketplace (Pololu), order 102531268", ON_HAND_POLOLU, "Crumb takes the other."),
            ("1 of 2", "narrow-spot lens", DK_CARCLO,
             "DigiKey order 102531269", ON_HAND_DK, "One spare."),
            ("1 of 10", "piezo beeper", DK_PIEZO,
             "DigiKey order 102531269", ON_HAND_DK, "Nine spare for any project."),
            ("2 of 10", "350 mA LED regulators", amz("B0CST7GZTN"),
             "Amazon 114-4621584-3017007, 2026-10-27", "in transit · arriving 2026-11-09 (Amazon Orders page, read 2026-11-09; was 11-17 to 11-20)", ""),
            ("1 of 4", "cool-white LED star", amz("B00LWU5DWM"),
             "Amazon 114-5101833-0385036, 2026-10-27",
             "on hand · delivered 2026-11-02 (Amazon; USPS at the front desk 12:14); picked up 2026-11-03 (pick-up task completed 3 p.m.)",
             "Three spare. The record said two plus four; the account shows one order of four."),
            ("about 300 mm of 20 rods", "1 mm stainless rod, two 10-packs", amz("B082ZNWQ5Q"),
             "Amazon 114-7336723-5981056 and 114-1049705-6516238, 2026-10-27",
             "on hand · delivered 2026-11-04 and 11-05 (two \"online seller\" boxes at the front desk, building log); picked up 2026-11-05 (pick-up tasks); the builder named them 2026-11-07",
             "Rails, axles and bars: 277 mm, one rod. 19 spare."),
            ("about 2 of 10", "1.5 mm stainless coupons, 150 mm", amz("B082ZNMD46"),
             "Amazon 114-6765566-8037841, 2026-10-27", "on hand · delivered 2026-10-29",
             "The four motor collars. The hologram takes one coupon, the satellite three."),
            ("4 × 100 Ω, 6 × 10 kΩ, 1 × 220 µF", "resistor kit and electrolytic kit", amz("B0F4P352BB"),
             "Amazon 2026-09-02", "on hand", ""),
            ("as needed", "26 AWG silicone wire, Kapton, heat-shrink", amz("B07G2LRX68"),
             "bench stock, 2026-09-02", "on hand", ""),
            ("1 of 6", "enclosed speaker, Same Sky", DK_SPEAKER,
             "DigiKey 2026-09-02 and 10-01 (Pip's stock)", "on hand",
             "Added 2026-11-09 for the voice build; one of Pip's two spares. On the pan's tail, grille up."),
            ("1 of 5", "PAM8403 class-D amplifier board, 5-pack", amz("B0DYYX8DF9"),
             "Amazon 114-4918612-8872205, 2026-11-09, $5.59 (B0DYYX8DF9, the version without the volume knob)", "in transit · arriving Thu 2026-11-12 (Orders page, read 2026-11-10)",
             "Under the pan at the nose, hidden as bought. Four spare."),
            ("4", "7 × 20 mm coreless motors, 4-pack with JST 1.25 leads", amz("B0DJ17L348"),
             "Amazon 114-3814610-9158651, 2026-11-10, $15.06 with tax", "in transit · arriving Thu 2026-11-12 (Orders page, read 2026-11-10)",
             "In place of the 615s, which become spares. SpeedyFPV B0CCHXNKDG and BetaFPV's 17500KV are the alternatives."),
            ("4 of 8 (two sets)", "HQ Prop 40 mm four-blade props, grey polycarbonate, 1 mm, set of four", "https://www.tinywhoop.com/products/hq-prop-40mm-4-blade-props-grey-1mm-shaft",
             "in the builder's tinywhoop.com cart 2026-11-10 ($3.49 a set; guest checkout)", "in the cart · lift revision",
             "One set flying, one spare; grey for the palette. White props were sold out everywhere 11-10; the Gemfan clear grey and red pack was dropped from the Amazon cart as ugly against the brass. Black ABS at the same shop is the fallback."),
            ("1", "TCA9548A I2C multiplexer, Adafruit", amz("B017C09ETS"),
             "Amazon 114-0717964-5329021, 2026-11-10, $9.13 (3DMakerWorld)", "in transit · arriving Thu 2026-11-12 (Orders page, read 2026-11-10)",
             "Black, across the hood; the five rangers on one bus, one channel each, no pin."),
            ("3 of 4 (two 2-packs)", "TOF400C VL53L1X ranger boards, AITRIP 2-pack, black", amz("B09LCHPTNM"),
             "Amazon 114-0717964-5329021, 2026-11-10, $14.99 a pack", "in transit · arriving Thu 2026-11-12 (Orders page, read 2026-11-10)",
             "Left and right low beside the rails, back behind the tail bar; one spare. The Pimoroni board drawn first was $43 each on Amazon."),
            ("1 of 2", "AGFRC 1.5 g linear servo, pair", amz("B07L3N5C4S"),
             "Amazon 114-0717964-5329021, 2026-11-10, $17.99", "in transit · arriving Thu 2026-11-12 (Orders page, read 2026-11-10)",
             "The camera's tilt, ±30° on a 6 mm lever; one spare."),
            ("1", "USB-C LiPo charger, for the flight packs", ada(4410),
             "Adafruit 2026-09-01", "on hand", "Pip's held part, shared."),
        ],
    ),
    (
        "Cyber Dawn, the alarm clock",
        "cyber_clock_v2",
        "Complete, 2026-11-10, at the builder's word: assembled 2026-11-09 with the sunrise lamp left out. "
        "The acrylic face and the printed body were never bought. Spares sorted 2026-11-10: the coin cells and "
        "the slide switches to the backcase bin, the cell holders to the shared bin, the JST-PH leads to the XS drone bin.",
        [
            ("1 of 3", "controller board", DK_DEVKIT,
             "DigiKey order 102531269, invoice 135297233, FedEx Ground", ON_HAND_DK,
             "Two spare. Also on hand: two 16 MB variants from Amazon 114-3292680-1445046, delivered 2026-10-06 (linked in the notes below)."),
            ("1 of 2", "2.42 inch OLED display kit", ada(2719),
             "Adafruit 3765988, 2026-10-19, UPS", ON_HAND_ADA1, "The hologram takes the other."),
            ("1 of 2", "real-time clock", ada(5188), "Adafruit 3765988", ON_HAND_ADA1, "One spare."),
            ("1 of 10", "coin cell, 10-pack", amz("B0D8T4C5PK"),
             "Amazon 114-9008008-9870602, 2026-10-19", "on hand · delivered 2026-10-20",
             "Plus one Panasonic single from 114-6114435-1326638, likely delivered 2026-10-08. The pack is in the backcase bin (builder, 2026-11-10)."),
            ("1 of 2", "rotary encoder with I²C adapter", ada(6310), "Adafruit 3765988", ON_HAND_ADA1, "One spare."),
            ("1 of a pair", "stereo speaker pair, 4 Ω 3 W", ada(1669), "Adafruit 3765988", ON_HAND_ADA1, "The second driver is the spare."),
            ("1 of 2", "16 mm snooze button", ada(1505), "Adafruit 3765988", ON_HAND_ADA1, "One spare."),
            ("1 of 2", "proximity and light sensor", ada(4161), "Adafruit 3765988", ON_HAND_ADA1,
             "Plus three SparkFun spares from DigiKey 2026-10-01 (keep them off the chain)."),
            ("1 of 2", "accelerometer", ada(2809), "Adafruit 3765988", ON_HAND_ADA1,
             "Plus a generic 5-pack from Amazon 114-0516847-5209826, delivered 2026-10-22."),
            ("1 of 5", "temperature and humidity sensor", ada(4566),
             "Adafruit 3765988 (2) and DigiKey 2026-10-01 (3)", "on hand · 2026-10-21 and October", "The Sphere takes one; three spare."),
            ("1 of 2", "QT-to-header cable", ada(4209), "Adafruit 3765988", ON_HAND_ADA1, "One spare."),
            ("5 of 7", "100 mm QT cables", ada(4210), "Adafruit 3765988", ON_HAND_ADA1, "Crumb takes two; none spare."),
            ("1 of 12", "I²S amplifier", amz("B0CDWXZZCH"),
             "Amazon 2026-09-02 (3) and 2026-10-11 (6)", "on hand · delivered 2026-09-03 and 10-14", "Three more came 2026-11-03 with Crumb's box."),
            ("1 of 25", "slide switch", amz("B09R434VJQ"),
             "Amazon 111-8554202-0502625, 2026-09-02", "on hand · delivered 2026-09-04", "The arm switch; Pip's power switch is another. The rest of the pack is in the backcase bin (builder, 2026-11-10)."),
            ("10 kΩ, 4.7 kΩ; 220 µF (in the display kit), 100 nF", "resistor kit and ceramic kit", amz("B0F4P352BB"),
             "Amazon 2026-09-02", "on hand", ""),
            ("1 of 2", "charger board with 5 V boost", ada(6106),
             "Adafruit 3771280, 2026-10-26, UPS", ON_HAND_ADA2, "The satellite takes the other. None spare. Cut the current jumper."),
            ("1 of 2", "fuel gauge", ada(5580), "Adafruit 3771280", ON_HAND_ADA2, "Crumb takes the other. None spare."),
            ("1 of 13", "16340 cell, protected", IMR_NL169,
             "IMR Batteries 20739060 and 20739061, 2026-10-16", ON_HAND_IMR, "Eight spare across the family."),
            ("1 of 10", "16340 holder with leads", amz("B0CRGK889F"),
             "Amazon 114-1421763-3353854, 2026-10-27", "on hand · delivered 2026-10-30", ""),
            ("1 of 20 pairs", "JST-PH 2.0 mm pigtails", amz("B0F6T4LKDG"),
             "Amazon 111-8554202-0502625, 2026-09-02", "on hand · delivered 2026-09-04", "The set is in the XS drone bin (builder, 2026-11-10); the drone, Crumb, the satellite and the rover take leads from it. Meter polarity."),
            ("about 300 mm of 3 mm tube", "brass tube set, 2 to 7 mm, 200 mm", amz("B0F2FKLC2N"),
             "Amazon 114-9676073-9134626, 2026-10-26 (3 sets)", "on hand · delivered 2026-10-28",
             "The two cradles. 330 mm sets: three due 11-06 to 11-13 (114-2647470-9786634; the Orders page said 11-03 but nothing came by the 13:44 desk log), four 11-13 to 11-19 (114-2645785-1488244)."),
            ("1", "82 × 52 mm smoked acrylic front, 3 mm", "https://sendcutsend.com/materials/acrylic/",
             "nothing bought", "not ordered · not needed: Cyber Dawn was closed out complete without it (builder, 2026-11-10)", ""),
            ("1 spool", "black PETG for the body, lid and rear panel", "https://www.printedsolid.com/collections/1-75mm-petg",
             "nothing bought", "not ordered · not needed: Cyber Dawn was closed out complete without it (builder, 2026-11-10)", ""),
        ],
    ),
    (
        "Pip, the Pocket AI Assistant",
        "pocket_ai_assistant",
        "First version complete, 2026-11-10, at the builder's word: the first build, battery attached, held its first "
        "spoken conversation on 2026-11-09. Every part is on hand, most of them in multiples. The nickel-silver and "
        "sterling wire wait for the silver rebuild, a second version. Nothing to buy.",
        [
            ("1 of 13", "ESP32-C3 SuperMini controller, 10-pack", amz("B0F888JQ91"),
             "Amazon 111-8554202-0502625, 2026-09-02; plus a 3-pack, 114-9058559-0123454, 2026-10-17 (linked in shared stock)",
             "on hand · delivered 2026-09-04 and 10-18", "The hologram and the satellite take one each; ten spare."),
            ("1 of 10", "0.96 inch OLED display, two 5-packs", amz("B09T6SJBV5"),
             "Amazon 111-6329624-3227449 (09-02) and 114-8572576-9885850 (10-22)", "on hand · delivered 2026-09-02 and 10-26",
             "The Sphere and the camera Pocket AI take one each; seven spare. The 10-22 pack was not in the inventory."),
            ("1 of 15", "I²S microphone, three 5-packs", amz("B092HWW4RS"),
             "Amazon 111-8554202-0502625 (09-02), 114-3696034-7495405 (10-19), 114-0550068-3533850 (10-23)",
             "on hand · delivered 2026-09-04, 10-20, 10-24", "The hologram takes one; 13 spare."),
            ("1 of 12", "I²S amplifier", amz("B0CDWXZZCH"),
             "Amazon 111-8554202-0502625 (3) and 114-5029591-3604223 (6)", "on hand · delivered 2026-09-03 and 10-14", ""),
            ("1 of 6 + 3 ordered", "enclosed speaker", DK_SPEAKER, "DigiKey 2026-09-02 (4) and 10-01 (2); 3 more 2026-11-10 (102810661)", "on hand · DigiKey's pages say Delivered; the three of 11-10 due about 11-13 to 11-16", ""),
            ("1 of 420", "tactile button", amz("B0FHW6HMG4"), "Amazon 111-8554202-0502625", "on hand · delivered 2026-09-04", ""),
            ("4.7 kΩ, 10 kΩ; 220 µF; 100 nF", "resistor kit, electrolytic kit, ceramic kit", amz("B0F4P352BB"),
             "Amazon 2026-09-02", "on hand", ""),
            ("frame", "1.5 mm brass tube, 4-packs", amz("B005WPAW9M"),
             "Amazon 111-9290282-4717813 (09-02), 114-7954180-3181065 (10-06), 114-6509974-9230602 (10-07), 114-5551673-5391400 (4 packs, 10-19)",
             "on hand · delivered 2026-09-03 to 10-26", "Seven packs, 28 tubes: the inventory logged one."),
            ("harness rods", "1.0 mm brass rod, 5-packs", amz("B005WPB7YG"),
             "Amazon 2026-09-02, 10-07, 10-10", "on hand · delivered 2026-09-04, 10-12, 10-12", "Shared with Crumb and the Sphere."),
            ("silver rebuild", "nickel silver wire, 14 / 18 / 20 gauge", amz("B0BSTSMLF7"),
             "Amazon 114-7658724-9947427, 114-7795722-0389854, 114-0400398-7479413, 2026-10-14", "on hand · delivered 2026-10-16 and 10-17", ""),
            ("silver rebuild", "sterling silver wire, 14 gauge", amz("B00BY9A9HU"),
             "Amazon 114-2217793-3508253, 2026-10-11",
             "on hand · delivered 2026-11-02 (USPS at the front desk 12:11); picked up 2026-11-03 (pick-up task completed 3 p.m.)", "The 18 gauge (next row) came 10-20."),
            ("silver rebuild", "sterling silver wire, 18 gauge", amz("B00ANA6JFC"),
             "Amazon 114-9804173-2582632, 2026-10-11", "on hand · delivered 2026-10-20", ""),
            ("as needed", "30 AWG silicone wire, two kits", amz("B073RDGTPB"),
             "Amazon 111-2854120-5242663 and 111-2522128-9220253, 2026-09-02", "on hand · delivered 2026-09-02 and 09-04", "Shared by every build."),
            ("as needed", "26 AWG silicone wire", amz("B07G2LRX68"), "Amazon 111-9290282-4717813", "on hand · delivered 2026-09-03", ""),
            ("as needed", "Kapton tape", amz("B072Z92QZ2"), "Amazon 111-8554202-0502625", "on hand · delivered 2026-09-04", ""),
            ("as needed", "fish paper", amz("B0GZVDKBBS"), "Amazon 111-8554202-0502625", "on hand · delivered 2026-09-04", ""),
            ("as needed", "heat-shrink kit, white", amz("B08N4W4K9X"), "Amazon 111-8554202-0502625", "on hand · delivered 2026-09-03", ""),
            ("1 of 2 (final build)", "power-path boost board, PowerBoost 1000C copy", amz("B0G5PXGVG9"),
             "Amazon 114-0663433-1244242, 2026-10-11", "on hand · delivered 2026-10-19", "The inventory dated this 10-14 and logged one; the account shows two."),
            ("1 of 4 (final build)", "1200 mAh LiPo pack", ada(258),
             "Adafruit 2026-09-01 (2) and 3771280 (2)", "on hand", "The only owned pouch rated for Pip's load."),
            ("2, held", "500 mAh LiPo pack", ada(1578), "Adafruit 2026-09-01", "on hand", "Held; not released for any build."),
            ("1 (final build)", "USB-C LiPo charger", ada(4410), "Adafruit 2026-09-01", "on hand", "Also charges the drone's flight packs."),
        ],
    ),
    (
        "Pocket AI Sphere",
        "pocket_ai_sphere",
        "Only the controller is missing: its board is in the pair now expected by 11-15. Everything else "
        "comes out of shared stock and is on hand.",
        [
            ("1", "controller with camera and microphone", amz("B0C69FFVHH"),
             "Amazon 114-1888127-6908215, 2026-10-27 (pair; the other is the camera Pocket AI's)", XIAO_15, ""),
            ("1 of 10", "0.96 inch OLED display", amz("B09T6SJBV5"), "Pip's stock, Amazon 2026-09-02 and 10-22", "on hand", ""),
            ("1 of 5", "temperature and humidity sensor", ada(4566), "Adafruit 3765988 and DigiKey 2026-10-01", "on hand", "Cyber Dawn takes one."),
            ("1 of 12", "I²S amplifier", amz("B0CDWXZZCH"), "Pip's stock", "on hand", ""),
            ("1 of 6 + 3 ordered", "enclosed speaker", DK_SPEAKER, "DigiKey 2026-09-02 (4) and 10-01 (2); 3 more 2026-11-10 (102810661)", "on hand · DigiKey's pages say Delivered; the three of 11-10 due about 11-13 to 11-16", ""),
            ("1 of 13", "16340 cell, protected", IMR_NL169, "IMR Batteries 20739060 and 20739061, 2026-10-16", ON_HAND_IMR, ""),
            ("1 of 10", "16340 holder with leads", amz("B0CRGK889F"), "Amazon 114-1421763-3353854", "on hand · delivered 2026-10-30", ""),
            ("1 of 20", "toggle switch", amz("B0CZ6XZ2P9"), "Amazon 114-1421763-3353854", "on hand · delivered 2026-10-30", ""),
            ("1 of 420", "tactile button", amz("B0FHW6HMG4"), "Pip's stock", "on hand", ""),
            ("4.7 kΩ; 220 µF; 10 µF + 100 nF", "resistor kit, electrolytic kit, ceramic kit", amz("B0F4P352BB"), "Pip's stock", "on hand", ""),
            ("3 rods", "1.5 mm solid brass rod, 5-packs", amz("B01C6LUO5Q"),
             "Amazon, many packs between 2026-10-10 and 10-28 (shared stock)", "on hand", "The three rings. About 90 rods are in the drawer."),
            ("1 rod", "1.0 mm brass rod", amz("B005WPB7YG"), "Pip's stock", "on hand", "The two posts and the sensor hangers."),
            ("as needed", "26 and 30 AWG wire, Kapton, fish paper, white heat-shrink", amz("B073RDGTPB"), "Pip's stock", "on hand", ""),
            ("1, optional", "external 16340 charger", "https://www.amazon.com/s?k=nitecore+ui1", "nothing bought", "not ordered · optional", ""),
        ],
    ),
    (
        "Pocket AI with camera",
        "pocket_ai_assistant_with_camera",
        "Two things are still in the mail: the controller (in the pair now expected by 11-15) and the two "
        "gear motors (both at the bench 11-03, early). The driver, holder and switch came on 10-30; the rest is shared stock.",
        [
            ("1", "controller with camera and microphone", amz("B0C69FFVHH"),
             "Amazon 114-1888127-6908215, 2026-10-27 (pair; the other is the Sphere's)", XIAO_15, ""),
            ("1 of 5", "dual H-bridge motor driver, MX1508", amz("B075S368Y2"),
             "Amazon 114-1421763-3353854, 2026-10-27", "on hand · delivered 2026-10-30", "Four spare."),
            ("2 (one per order)", "12 mm gear motor, 3 V 16 rpm", amz("B0BS9K8Q8Z"),
             "Amazon 114-3598847-0810627 and 114-8685392-8347425, 2026-10-27", "on hand · both at the bench 2026-11-03 while sorting, early (no delivery mail; the Orders page had 11-05 to 11-16)",
             "The record was unsure whether two were ordered; the account shows two orders of one."),
            ("1 of 10", "16340 holder with leads", amz("B0CRGK889F"), "Amazon 114-1421763-3353854", "on hand · delivered 2026-10-30", ""),
            ("1 of 20", "toggle switch", amz("B0CZ6XZ2P9"), "Amazon 114-1421763-3353854", "on hand · delivered 2026-10-30", ""),
            ("1 of 13", "16340 cell, protected", IMR_NL169, "IMR Batteries 20739060 and 20739061, 2026-10-16", ON_HAND_IMR, ""),
            ("1 of 10", "0.96 inch OLED display", amz("B09T6SJBV5"), "Pip's stock", "on hand", ""),
            ("1 of 12", "I²S amplifier", amz("B0CDWXZZCH"), "Pip's stock", "on hand", ""),
            ("1 of 6 + 3 ordered", "enclosed speaker", DK_SPEAKER, "DigiKey 2026-09-02 (4) and 10-01 (2); 3 more 2026-11-10 (102810661)", "on hand · DigiKey's pages say Delivered; the three of 11-10 due about 11-13 to 11-16", ""),
            ("2 of 420", "tactile buttons", amz("B0FHW6HMG4"), "Pip's stock", "on hand", "Action button and home stop."),
            ("4.7 kΩ, 2 × 10 kΩ; 220 µF, 10 µF, 100 nF", "resistor kit, electrolytic kit, ceramic kit", amz("B0F4P352BB"), "Pip's stock", "on hand", ""),
            ("frame", "1.5 mm brass tube and rod, 1.0 mm rod, nickel silver", amz("B005WPAW9M"), "Pip's stock", "on hand", "See shared stock."),
            ("hub", "brass tube set, 4 mm tube", amz("B0F2FKLC2N"), "Amazon 114-9676073-9134626", "on hand · delivered 2026-10-28", ""),
            ("as needed", "26 and 30 AWG wire, headers, heat-shrink, Kapton, fish paper", amz("B073RDGTPB"), "Pip's stock", "on hand", ""),
            ("1, optional", "external 16340 charger", "https://www.amazon.com/s?k=nitecore+ui1", "nothing bought", "not ordered · optional", ""),
        ],
    ),
    (
        "Desk hologram",
        "desk_hologram",
        "Two parts were bought and both are still in transit: the cube arrives Sunday 11-08, the filament "
        "pack is due today. The display, controller, microphone and leg stock are on hand.",
        [
            ("1", "beam-splitter cube, 50 mm", amz("B0B34FV475"),
             "Amazon 114-6341362-5527437, 2026-11-01", "in transit · arriving Sunday 2026-11-08", "Keep it wrapped until the legs are on."),
            ("1 of 10", "LED filament, 3 V, 38 mm, 2200 K", amz("B0FR35BGYL"),
             "Amazon 114-0670386-1613054, 2026-11-01", TODAY, "The satellite takes one from this pack; eight spare. The pack is in the satellite bin (sorted 11-03)."),
            ("1 of 2", "2.42 inch OLED display kit", ada(2719), "Adafruit 3765988, 2026-10-19, UPS", ON_HAND_ADA1, "Cyber Dawn's spare; its 220 µF is used."),
            ("1 of 13", "ESP32-C3 SuperMini controller", amz("B0F888JQ91"), "Pip's stock, Amazon 2026-09-02 and 10-17", "on hand", ""),
            ("1 of 15", "I²S microphone", amz("B092HWW4RS"), "Pip's stock, Amazon 2026-09-02, 10-19, 10-23", "on hand", ""),
            ("1 of 420", "tactile button", amz("B0FHW6HMG4"), "Pip's stock", "on hand", "Push to talk."),
            ("68 Ω; 100 nF", "resistor kit and ceramic kit", amz("B0F4P352BB"), "Pip's stock", "on hand", "The only resistor in the build."),
            ("about 0.5 m", "30 AWG silicone wire", amz("B073RDGTPB"), "Pip's stock", "on hand", ""),
            ("as needed", "Kapton, heat-shrink, CA glue, header pins, solder", amz("B072Z92QZ2"), "bench stock", "on hand", ""),
            ("1 of 10", "1.5 mm stainless coupon, 150 mm", amz("B082ZNMD46"),
             "Amazon 114-6765566-8037841, 2026-10-27", "on hand · delivered 2026-10-29", "The four legs from one coupon."),
            ("1", "USB-C wall adapter, 2 A, and a data cable", "https://www.amazon.com/s?k=usb-c+wall+adapter+2a", "owned, no listing recorded", "on hand", "The only power source."),
            ("optional", "black matte card; 5-minute epoxy", "https://www.dickblick.com/", "nothing bought", "not ordered · optional", "Try the cube without the card first."),
        ],
    ),
    (
        "Desk satellite",
        "desk_satellite",
        "All three parcels are in. The LED chips (delivered 11-04) and the wings (11-05, two days early) were picked up 11-05 "
        "and went into the satellite bin on 11-07 at the builder's word. The steel disc came 11-06, twelve days early, and is spare: "
        "on the bench it read too white, so the base is a brass coaster; the one ordered 11-06 (delivered 11-09 to the mail room) went to the desk lighthouse on 11-09, so the satellite's is to buy again; the disc sits in the satellite bin for now. "
        "The Eujgoov fallback panels were cancelled, so no fallback wing exists. The cell is on hand: the "
        "\"November 3 order\" in the inventory is order 20739060 of October 16, delivered October 21.",
        [
            ("2 of 5", "mini solar panels, 80 × 45 mm, 5 V, 5-pack", amz("B0FL26KWWT"),
             "Amazon 111-1980686-5970641, 2026-11-03", "on hand · delivered 2026-11-05, two days early; picked up 2026-11-05 (pick-up task)", "The wings; three spare. The pack is in the satellite bin (sorted 11-07)."),
            ("1 of 20", "pre-wired warm-white LED chips, 0805", amz("B09QGJ9LY7"),
             "Amazon 111-9152603-4910637, 2026-11-03", "on hand · delivered 2026-11-04; picked up 2026-11-05 (pick-up task)", "The beacon; 19 spare, one of them promised to the Mars rover. Judge the colour against a 2700 K bulb. The pack is in the satellite bin (sorted 11-07)."),
            ("0 (was 1)", "stainless disc, 3 inch × 1/8 inch, 304", amz("B08JD6GY21"),
             "Amazon 111-4967394-9172244, 2026-11-03", "on hand · delivered 2026-11-06, twelve days early (UPS from the maker, building log); picked up 2026-11-06",
             "Spare since 11-06: on the bench the steel read too white, so the base is the brass coaster below. In the satellite bin for now (sorted 11-07)."),
            ("0 (to buy again)", "brass coaster, 75 × 8 mm, flat top", amz("B0D9DMK3L7"),
             "Amazon 114-8443990-0476239, 2026-11-06, $12.99 ($14.14 with tax, sold by TOGGOOL)", "not ordered · in the builder's Amazon cart since 2026-11-09 about 22:00 EST ($12.99, TOGGOOL, ships from Amazon); the one bought 2026-11-06 was delivered 2026-11-09 (mail room) and is the desk lighthouse's at the builder's word",
             "The base. Hollow under a thin top, so the printed hub is glued on and about 150 g of steel goes into the hollow."),
            ("0 (was 3)", "mini solar panels, 110 × 60 mm, 6 V, 3-pack", amz("B08THXDWS1"),
             "Amazon 114-9697223-4179439, 2026-11-03", "cancelled · the Orders page says cancelled, not charged",
             "The inventory logged this as held stock arriving 11-07. It is not coming; there is no fallback wing."),
            ("1 of 2", "charger board with 5 V boost", ada(6106), "Adafruit 3771280, 2026-10-26, UPS", ON_HAND_ADA2, "Cyber Dawn takes the other. Cut the current jumper. In the satellite bin (builder, 2026-11-10)."),
            ("1 of 13", "16340 cell, protected", IMR_NL169,
             "IMR Batteries 20739060 (7 cells with 12 IMREN 18350), 2026-10-16, UPS", ON_HAND_IMR,
             "Not a November order: the pasted summary was this one. Eight spare across the family."),
            ("1 of 10", "16340 holder with leads", amz("B0CRGK889F"), "Amazon 114-1421763-3353854, 2026-10-27", "on hand · delivered 2026-10-30", ""),
            ("1 of 20 pairs", "JST-PH 2.0 mm pigtails", amz("B0F6T4LKDG"), "Amazon 111-8554202-0502625, 2026-09-02", "on hand · delivered 2026-09-04", "Meter the plug before it goes in."),
            ("1 of 13", "ESP32-C3 SuperMini controller", amz("B0F888JQ91"), "Pip's stock", "on hand", "Remove its red power LED."),
            ("1 of 100", "Schottky diode", amz("B079KJ46ZS"), "Amazon 114-5201101-3840264, 2026-10-27", "on hand · delivered 2026-10-30", "The drone's stock; the pack is in the drone bin (sorted 11-03)."),
            ("1 of 10", "LED filament, 3 V, 38 mm, 2200 K", amz("B0FR35BGYL"), "Amazon 114-0670386-1613054, 2026-11-01 (the hologram's pack)", TODAY, "The pool under the body; the pack lives in this bin (sorted 11-03)."),
            ("100 Ω; 68 Ω", "resistor kit", amz("B0F4P352BB"), "Pip's stock", "on hand", "The two resistors in the build."),
            ("1 of 420", "tactile button", amz("B0FHW6HMG4"), "Pip's stock", "on hand", "The mode button in the lid."),
            ("about 0.4 m", "30 AWG silicone wire", amz("B073RDGTPB"), "Pip's stock", "on hand", ""),
            ("as needed", "Kapton, white heat-shrink, CA glue, solder", amz("B072Z92QZ2"), "bench stock", "on hand", ""),
            ("3 of 10", "1.5 mm stainless coupons, 150 mm", amz("B082ZNMD46"), "Amazon 114-6765566-8037841, 2026-10-27", "on hand · delivered 2026-10-29", "Post and two booms."),
            ("3 parts", "black PETG: bus box, lid, hub", "https://www.printedsolid.com/collections/1-75mm-petg", "nothing bought", "not ordered · print from shelf stock", "After the bench fit."),
            ("12, held", "IMREN 18350 cells, 800 mAh", IMR_IMREN, "IMR Batteries 20739060, 2026-10-16", ON_HAND_IMR, "Held stock, not for this build: unprotected and 18.2 mm thick."),
        ],
    ),
    (
        "Desk lighthouse",
        "desk_lighthouse",
        "Ordered 2026-11-09 at 04:22 EST in one Amazon checkout that split into five orders ($122.64 with tax and delivery), matched to the "
        "lines by price and confirmed by the day's two shipping mails; these five orders were first logged as the Mars rover's. The brass coaster bought "
        "2026-11-06 as the satellite's base is this build's since 11-09 and was delivered that day to the mail room. The five Grand Brass lamp parts "
        "are ordered by the builder's word, with no confirmation mail yet. The charger is not ordered: the DigiKey order of 11-09 was the rover's. "
        "That evening the builder rejected the acrylic tube and dropped the brass sheet (its order came back cancelled by the seller, not charged), so Rev D (awaiting approval) has an open lantern, no house, and its three small brass pieces made from the owned 1 mm rod and tubes. "
        "Everything else comes out of owned stock (`desk_lighthouse/docs/INVENTORY.md`).",
        [
            ("0 (to return)", "clear acrylic tube, 25 mm OD × 21 mm ID × 305 mm", amz("B08ZM5BCQJ"),
             "Amazon 114-1438198-3243448, 2026-11-09, $8.99", "in transit · shipped 2026-11-09 12:13 EST with the reed switches ($20.48), arriving Wed 11-11; rejected by the builder that evening (Rev D has no glass): return it or keep it as stock",
             "Was the lantern glass. Rev D's lantern is open."),
            ("1 of 2", "N20 gearmotor, 6 V, 30 rpm, 3 mm D shaft, 2-pack", amz("B096S475NH"),
             "Amazon 114-1438198-3243448, $15.99", "in transit · shipped 2026-11-09 17:22 EST with the magnets ($38.63), arriving Wed 11-11 (Amazon's mail)",
             "Turns the shutter; the second is the spare. Check: 3 mm D shaft, runs at 3 V."),
            ("1 of 10", "LED filament, 26 mm, 3 V, 2700 K, 10-pack", amz("B0HBX2YW18"),
             "Amazon 114-6111517-7569023, $25.40 + $4.98 delivery", "in transit · arriving Fri 11-27, the last box (Amazon's order mail)",
             "The lamp; nine spare. The holed tab is +."),
            ("1 of 20", "glass reed switch, 2 × 14 mm, 20-pack", amz("B0CHF29394"),
             "Amazon 114-1438198-3243448, $9.82", "in transit · shipped 2026-11-09 with the acrylic tube, arriving Wed 11-11",
             "The index; pick the most sensitive of the twenty. Never bend a lead at the glass."),
            ("1 of 100", "neodymium disc magnets, 3 × 1 mm, N52, 100-pack", amz("B0BQ3LPGZ1"),
             "Amazon 114-1438198-3243448, $19.49", "in transit · shipped 2026-11-09 with the motors, arriving Wed 11-11",
             "One under the collar; 99 spare for the family."),
            ("0 (cancelled)", "brass sheet, 0.015 in, 4 × 10 in", amz("B0006N6WJE"),
             "Amazon 114-5648832-0318640, $5.31 + $9.49 delivery (seller bestbrandsupply)", "cancelled · by the seller, not charged (Your Orders, read in the builder's Chrome at their word, 2026-11-09 about 22:00 EST); Rev D has no house and no sheet-cut discs anyway. A copy from Blick that had reappeared in the cart was moved to Saved for later",
             "Was the house and three discs. Rev D makes the shutter's floor, the magnet arm and the deck's bearing from 1 mm rod and tube rings."),
            ("1", "brass round tube, 5/8 in × 0.014 in wall × 12 in", amz("B07DDFNNXY"),
             "Amazon 114-7188491-2312247, $9.89 (seller What America Buys)", "in transit · arriving 11-18 to 11-20 (Amazon's order mail)",
             "The shutter, a 30 mm length; the rest is stock."),
            ("1 tube", "gel super glue, 4 g", amz("B003Y49R7G"),
             "Amazon 114-1965907-0721062, $3.29", "in transit · arriving Sat 11-14 (Amazon's order mail)",
             "One tube for this build, the hologram and the rover."),
            ("1", "turned brass check ring, 1-1/2 in, 1/8 IP slip", "https://grandbrass.com/check-rings/turned-brass-checkrings/?_bc_fsnf=1",
             "Grand Brass CRT1-12X8, ordered by the builder 2026-11-09 (their word)", "ordered · no confirmation mail by 2026-11-09 18:00 EST; order number unknown",
             "The gallery deck. Measure its thickness (drawn 3 mm) and rerun build_page.py."),
            ("1", "spun brass vase cap, 1-1/2 in", "https://grandbrass.com/categories.php?category=655",
             "Grand Brass VA01-12, the same order", "ordered · as above", "The roof. Measure its height (drawn 12.5 mm)."),
            ("1", "brass ball, 5/8 in, 1/8 IP blind tap", "https://grandbrass.com/5-8in-diameter-1-8ips-threaded-tapped-blind-brass-ball-polished-nickle-finish/",
             "Grand Brass BB0-58X18, unfinished, the same order", "ordered · as above", "The ventilator ball."),
            ("1", "hollow brass nipple, 1/2 in × 1/8 IP", "https://grandbrass.com/1-2in-x-1-8ips-threaded-brass-hollow-nipple/",
             "Grand Brass NI0-12X18BR, the same order", "ordered · as above", "Through the cap; the lamp post solders up its bore."),
            ("1", "beaded brass nut, 1/8 IP", "https://grandbrass.com/1-8-27ips-unfinished-brass-beaded-nut/",
             "Grand Brass, the same order", "ordered · as above", "Clamps the roof's hardware; the lamp's return."),
            ("1", "charger board with 5 V boost (bq25185)", ada(6106),
             "nothing bought: not in the 2026-11-09 DigiKey order (the rover's); Cyber Dawn's two and Crumb's (DigiKey 102777448, shipped 11-09) are spoken for",
             "not ordered · one line, Adafruit 6106 or DigiKey 1528-6106-ND, $8.95; Amazon has no bq25185 board (searched 2026-11-09 evening)", "The cell's charger and the 5 V rail. Cut the current jumper."),
            ("1", "brass coaster, 75 × 8 mm, flat top", amz("B0D9DMK3L7"),
             "Amazon 114-8443990-0476239, 2026-11-06, $12.99 ($14.14 with tax, sold by TOGGOOL); bought as the satellite's base",
             "on hand · delivered 2026-11-09 12:01 EST to the mail room (Amazon's mail), in one package with the drone's heat tape; on the bench in a photo 2026-11-10",
             "The base and the electronics box. Measure the hollow; a magnet must not stick to the top. The satellite buys its own again. In the lighthouse bin (builder, 2026-11-10)."),
            ("1 of 13", "16340 cell, protected", IMR_NL169,
             "IMR Batteries 20739060 / 20739061, 2026-10-16", ON_HAND_IMR, "Stands in the house behind the motor."),
            ("1 of 10", "16340 holder with leads", amz("B0CRGK889F"),
             "Amazon 114-1421763-3353854, 2026-10-27", "on hand · delivered 2026-10-30", "From the shared bin; meter the leads before the cell goes in."),
            ("1 of 13", "ESP32-C3 SuperMini controller", amz("B0F888JQ91"), "Pip's stock", "on hand", "In the coaster's hollow; no Wi-Fi in this build."),
            ("1 of 5", "dual H-bridge driver (MX1508)", amz("B075S368Y2"),
             "Amazon 114-1421763-3353854, 2026-10-27", "on hand · delivered 2026-10-30", "The camera Pocket AI's stock; channel A the motor, channel B the lamp."),
            ("1 of 100", "Schottky diode (SS14)", amz("B079KJ46ZS"),
             "Amazon 114-5201101-3840264, 2026-10-27", "on hand · delivered 2026-10-30", "The drone's pack, in the drone bin."),
            ("4 of about 90", "1.5 mm brass rod, 300 mm", amz("B01C6LUO5Q"), "shared stock, eighteen 5-packs", "on hand", "The four rods of the cage, cut 222 each."),
            ("147 mm of one 4 mm tube", "brass tube set, 2 to 7 mm, 200 mm", amz("B0F2FKLC2N"),
             "Amazon 114-9676073-9134626, 2026-10-26", "on hand · delivered 2026-10-28", "The spine."),
            ("42 mm of one", "1.0 mm brass rod, 300 mm", amz("B005WPB7YG"), "shared stock", "on hand", "The lamp post."),
            ("2 + 2; 1", "47 Ω and 100 kΩ resistors; tactile button", amz("B0F4P352BB"), "Pip's stock", "on hand", "The lamp's series pair, the cell divider, the one button."),
        ],
    ),
]

# Shared stock: (part, owned, where, split, spare)
SHARED = [
    ("ESP32-C3 SuperMini controllers", "13", "Amazon 10-pack 2026-09-02 and 3-pack 2026-10-17, on hand",
     "Pip 1 · hologram 1 · satellite 1", "10"),
    ("XIAO ESP32-S3 Sense boards", "4 ordered, 0 on hand", "Amazon: Crumb's and the drone's by 11-11, the pair by 11-15",
     "Crumb 1 · drone 1 · camera Pocket AI 1 · Sphere 1", "0"),
    ("Nitecore 16340 cells", "13", "IMR Batteries, two orders of 2026-10-16, at the front desk 10-21",
     "Crumb 1 · Cyber Dawn 1 · Sphere 1 · camera Pocket AI 1 · satellite 1", "8"),
    ("IMREN 18350 cells", "12", "IMR Batteries 20739060, on hand 10-21", "no build", "12"),
    ("charger boards with 5 V boost", "2", "Adafruit 3771280, on hand 10-28; the satellite's is in the satellite bin (builder, 2026-11-10)", "Cyber Dawn 1 (in the clock) · satellite 1; the lighthouse and the rover's Rev K need one each, not bought", "0"),
    ("fuel gauges", "2", "Adafruit 3771280, on hand 10-28; Crumb's is in the Crumb bin (builder, 2026-11-10)", "Cyber Dawn 1 (in the clock) · Crumb 1", "0"),
    ("16340 holders with leads", "10", "Amazon 2026-10-27, on hand 10-30; the pack is in the shared bin (builder, 2026-11-10)", "Crumb · Cyber Dawn (in the clock) · Sphere · camera Pocket AI · satellite · lighthouse · Mars rover", "3"),
    ("toggle switches", "20", "Amazon 2026-10-27, on hand 10-30", "Crumb · Sphere · camera Pocket AI", "17"),
    ("dual H-bridge drivers", "5", "Amazon 2026-10-27, on hand 10-30", "camera Pocket AI 1", "4"),
    ("1.5 mm stainless coupons, 150 mm", "10", "Amazon 2026-10-27, on hand 10-29", "drone about 2 · hologram 1 · satellite 3", "about 4"),
    ("1 mm stainless rod, 300 mm", "20", "Amazon 2026-10-27, delivered 11-04 and 11-05, picked up 11-05", "drone about 1", "19"),
    ("LED filaments, 38 mm 2200 K", "10", "Amazon 114-0670386-1613054, delivered 11-03 12:53 in the box with Crumb's gears; the pack is in the satellite bin (sorted 11-03)", "hologram 1 · satellite 1", "8"),
    ("pre-wired warm-white LED chips, 0805", "20", "Amazon 111-9152603-4910637, delivered 11-04, picked up 11-05; the pack is in the satellite bin (sorted 11-07)", "satellite 1 · Mars rover 1", "18"),
    ("I²S amplifiers", "9 on hand + 3 today", "Amazon 2026-09-02 (3), 10-11 (6), 10-31 (3)", "Pip · Cyber Dawn · Crumb · Sphere · camera Pocket AI", "7"),
    ("enclosed speakers", "6 + 3 ordered 11-10", "DigiKey 2026-09-02 (4) and 10-01 (2); 3 more in 102810661, 2026-11-10, $24.54 all in; the 09-21 order in the inventory does not exist", "Pip · Crumb · Sphere · camera Pocket AI · drone (voice) · rover Rev K (voice)", "0 of the six; 3 once the three of 11-10 land"),
    ("0.96 inch OLED displays", "10", "Amazon 2026-09-02 and 10-22", "Pip 1 (soldered) · Sphere 1 · camera Pocket AI 1", "7"),
    ("I²S microphones", "15", "Amazon 2026-09-02, 10-19, 10-23", "Pip 1 (soldered) · hologram 1", "13"),
    ("temperature and humidity sensors", "5", "Adafruit 3765988 (2), DigiKey 2026-10-01 (3)", "Cyber Dawn 1 · Sphere 1", "3"),
    ("100 mm QT cables", "7", "Adafruit 3765988", "Cyber Dawn 5 · Crumb 2", "0"),
    ("motion sensors (GY-521)", "3 on hand + 10 ordered", "Amazon: HiLetgo 3-pack 114-1259113-3701002 delivered 11-09, in the XS drone bin (builder, 2026-11-10); Ximimark 10-pack 11-19 to 12-15", "drone 1 · Crumb 1, both from the 3-pack", "11"),
    ("laser rangers, 8×8 and single-zone", "2 + 2", "Pololu via DigiKey, USPS 9400150105496136143356, at the front desk 11-02", "drone 1 + 1 · Crumb 1 + 1", "0"),
    ("Schottky diodes", "100", "Amazon 2026-10-27, on hand 10-30; the pack is in the drone bin (sorted 11-03)", "drone 4 · satellite 1", "95"),
    ("JST-PH 2.0 mm pigtail pairs", "20", "Amazon 2026-09-02; the set is in the XS drone bin (builder, 2026-11-10; the shared bin from 11-08)", "drone about 5 · Crumb 3 · Cyber Dawn (in the clock) · satellite 1 · Mars rover 1", "about half"),
    ("1.5 mm solid brass rod, 5-packs", "18 packs, about 90 rods", "Amazon 2026-10-10 to 10-28 (the 10-28 order alone is 10 packs)", "Sphere 3 rods", "about 87"),
    ("1.5 mm brass tube, 4-packs", "7 packs, 28 tubes", "Amazon 2026-09-02, 10-06, 10-07, 10-19 (4)", "Pip's frame", "most"),
    ("1.0 mm brass rod, 5-packs", "3 packs, 15 rods", "Amazon 2026-09-02, 10-07, 10-10", "Pip · Crumb about 4 · Sphere 1", "about 8"),
    ("brass tube sets, 2 to 7 mm", "3 × 200 mm on hand; 3 × 330 mm due 11-06 to 11-13; 4 × 330 mm 11-13 to 11-19", "Amazon 2026-10-26 and 10-30", "Cyber Dawn cradles · Crumb hubs · camera Pocket AI hub", "plenty"),
    ("resistor, ceramic and electrolytic kits", "1 each", "Amazon 2026-09-02", "every build pulls values", ""),
    ("30 AWG wire kits", "2", "Amazon 2026-09-02", "every build", ""),
    ("26 AWG wire kit, Kapton, fish paper, heat-shrink, M3 screw kit", "1 each", "Amazon 2026-09-02; M3 kit 2026-10-27, picked up 11-01", "every build", ""),
    ("1200 mAh LiPo packs", "4 Adafruit + 2 EEMB", "Adafruit 2026-09-01 and 3771280; Amazon 114-0584890-2786622", "Pip final build 1", "5"),
    ("500 mAh LiPo packs", "2", "Adafruit 2026-09-01", "held", "2"),
    ("power-path boost boards", "2", "Amazon 2026-10-11, on hand 10-19", "Pip final build 1", "1"),
    ("cool-white LED stars", "4", "Amazon 2026-10-27, on hand 11-02", "drone 1", "3"),
    ("controller boards, ESP32-S3 dev kits", "3 (8 MB) + 2 (16 MB)", "DigiKey, at the front desk 11-02; Amazon 2026-10-01, on hand 10-06", "Cyber Dawn 1", "4"),
    ("solar panel, DC jack parts, USB-C extension, 6600 mAh pack", "1 each", "Adafruit 3771280, on hand 10-28; all four in the shared box (sorted 11-03)", "no build (Cyber Dawn's removed solar)", "all"),
    ("rotary encoders: four KY-040 modules and five bare EC11 switches (WayinTop)", "9", "Amazon, order not in the records; in the backcase bin (sorted 11-03)", "no build (Cyber Dawn's wheel is the Adafruit I²C encoder)", "9"),
    ("coin cells for the clock chip, 10-pack", "10", "Amazon 2026-10-19; the pack is in the backcase bin (builder, 2026-11-10)", "Cyber Dawn 1 (in the clock)", "9"),
    ("mini slide switches, 25-pack", "25", "Amazon 2026-09-02; the pack is in the backcase bin (builder, 2026-11-10)", "Cyber Dawn 1 (in the clock) · Pip 1 (drawn)", "23"),
    ("JST 1.25 mm 2-pin leads", "30 pairs", "Amazon 2026-10-27, picked up 11-01; in the XS drone bin (builder, 2026-11-10)", "drone 2, only if the packs keep their 1.25 plugs", "28 to 30"),
    ("level-shifter chip, from a 2.42 inch OLED kit", "1", "most likely Cyber Dawn's OLED kit, Adafruit 3765988 (no record names it); in the backcase bin (builder, 2026-11-10)", "no build: every controller here runs 3.3 V logic", "1"),
    ("stand-in controller board (KB2040)", "1", "free with Adafruit 3765988, 2026-10-19; in the backcase bin (builder, 2026-11-10)", "no build: never used (Cyber Dawn's Day 0 ran on the real controller)", "1"),
    ("lidar kit, youyeetoo LD19, with its pigtail, USB adapter and leads", "1", "Amazon 114-7956116-1377847, 2026-11-08, delivered 11-09; in the backcase bin, kept with the MOSFETs (builder, 2026-11-10)", "no build: kept for future work since Crumb Rev C and the rover's Rev J dropped it", "1"),
    ("P-channel MOSFETs, 100", "100", "the same order; in the backcase bin with the lidar kit (builder, 2026-11-10)", "no build: bought for Crumb's lidar switch", "100"),
    ("21 gauge silver-plated copper craft wire, 65 ft", "1 spool", "Amazon 114-2994210-6608245, 2026-11-07, delivered 11-09; in the backcase bin (builder, 2026-11-10)", "no build names it", "all"),
]

MISSING = [
    "XIAO ESP32-S3 Sense boards: none on hand. Crumb's and the drone's are now expected by 11-11, the pair for the camera Pocket AI and the Sphere by 11-15.",
    "Crumb's main box (motors, gears, driver, screen, amplifiers) and the hologram's filament pack: due today, 11-03, not delivered at 06:17.",
    "Desk satellite: nothing left in the mail. The chips (11-04) and wings (11-05) were picked up 11-05 and are in the satellite bin (sorted 11-07); the steel disc came 11-06 and is spare, in the satellite bin for now. The brass coaster that replaced the disc as the base was ordered 11-06 (delivered 11-09 to the mail room) and given to the desk lighthouse on 11-09; the satellite's is in the builder's Amazon cart since 11-09 evening, not ordered. The Eujgoov fallback panels were cancelled.",
    "Desk lighthouse: everything on Amazon ordered 2026-11-09 04:22 EST in one checkout of five orders ($122.64): the reed switches, acrylic tube, gearmotors and magnets shipped the same day for Wed 11-11, the gel glue comes 11-14, the 5/8 in tube 11-18 to 11-20 (the brass sheet's order: cancelled by the seller, not charged), the LED filaments 11-27; the brass coaster (bought 11-06 as the satellite's) was delivered 11-09 to the mail room; the five Grand Brass lamp parts are ordered by the builder's word with no confirmation mail yet; the bq25185 charger is not ordered (the 11-09 DigiKey order is the rover's). These five Amazon orders were first logged as the rover's. That evening the builder rejected the acrylic tube (to return) and dropped the brass sheet (its order came back cancelled by the seller, not charged): Rev D, open lantern and no house, awaits approval.",
    "Desk hologram: beam-splitter cube 11-08.",
    "Pocket AI with camera: both gear motors came early and were at the bench 2026-11-03; no delivery mail, the Orders page had 11-05 to 11-16.",
    "XS drone (Orders page read 11-09): controller 11-08 to 11-11; LED regulators, the motion-sensor 3-pack and the clear heat tape all arriving 11-09; motors and propellers came early, on the desk in a 2026-11-10 photo; the 10-pack 11-19 to 12-15 is spare; the 0.01 g scale was dropped the same day (the hover test is the thrust gate). Since 11-09 one line is open again: the speaker's amplifier board (PAM8403 5-pack), in the builder's Amazon cart since that evening, not ordered.",
    "Not bought: the satellite's three printed parts; the optional external 16340 charger; the hologram's optional card and epoxy; the drone's amplifier board (added 11-09, in the cart).",
]

CORRECTIONS = [
    "IMR Batteries: the satellite inventory's \"ordered 2026-11-03\" cells are order 20739060 of 2026-10-16 (7 Nitecore cells and 12 IMREN 18350), delivered 2026-10-21, alongside order 20739061 (6 Nitecore cells) the same day. 13 cells are on hand; no November order exists in the mail.",
    "Eujgoov 110 × 60 mm panels (114-9697223-4179439): cancelled and not charged, not arriving 11-07.",
    "Cree LED stars (114-5101833-0385036): four in one order, delivered 2026-11-02, not two plus four.",
    "DigiKey (account read 06:45): invoice 135297233 shows Delivered on DigiKey's own page and reached the front desk 2026-11-02 18:07; the Pololu invoice 135297191 (USPS 9400150105496136143356) still shows Shipped there but was at the front desk 11-02 12:13 per the building log. The FedEx site itself rejects the number.",
    "Enclosed speakers: 6 owned, not 8. DigiKey's account holds three orders (09-02: four speakers; 10-01: two speakers with three climate and three proximity sensors; 10-28); the inventory's 09-21 order of five does not exist. Three more were ordered 2026-11-10 as spares (sales order 102810661, $4.34 each, $24.54 with post, tariff and tax), nine once they land.",
    "Adafruit (account read 06:46): order 3771280 shows DELIVERED 2026-10-28; order 3765988 shows only Shipped there but was at the front desk 2026-10-21 (building log); the September order 3737700 (two 500 mAh and two 1200 mAh packs, the USB-C charger, a flux pen) is Pip's.",
    "XIAO boards: Crumb's (114-5249290-9043412) and the drone's (114-5295722-2709061) are now expected by 11-11; the pair (114-1888127-6908215) by 11-15.",
    "Three-set brass tube order 114-2647470-9786634: the Orders page said 11-03, but nothing came by the 13:44 desk log; the shipping mail's 11-06 to 11-13 stands.",
    "Unlogged stock found on the Orders page: six more amplifiers (2026-10-11), a second OLED 5-pack (10-22), a third microphone 5-pack (10-19), two power-path boards (10-11), seven packs of 1.5 mm tube, 18 packs of 1.5 mm rod, two DIYmall 16 MB dev kits (10-01, delivered 10-06), generic clock, accelerometer, encoder and 2.42 inch OLED modules (10-01).",
]

PICKUPS_WITHOUT_TASK = [
    ("2026-11-02", "DigiKey order 102531269, invoice 135297233 (FedEx 549379676887)", "MOSFETs, lens, piezos; Cyber Dawn's three controller boards", "XS drone, Cyber Dawn"),
    ("2026-11-02", "DigiKey marketplace order 102531268, invoice 135297191 (Pololu, USPS)", "two 8×8 and two single-zone laser rangers", "XS drone, Crumb"),
    ("2026-11-02", "Amazon 114-5101833-0385036", "four cool-white LED stars", "XS drone"),
    ("2026-11-02", "Amazon 114-2217793-3508253", "sterling silver wire, 14 gauge", "Pip, silver rebuild"),
]


# ---------------------------------------------------------------- markdown

def md_cell(s: str) -> str:
    return s.replace("|", "\\|")


def md_row(row):
    qty, name, url, source, status, note = row
    return f"| ☐ | {md_cell(qty)} | [{md_cell(name)}]({url}) | {md_cell(source)} | {md_cell(status)} | {md_cell(note)} |"


def write_md():
    out = []
    out.append("# Parts by project, for sorting into bins")
    out.append("")
    out.append(f"Read on **{READ['date']}**: {READ['amazon']}; {READ['mail']}; {READ['todoist']}. "
               f"{READ['digikey']}; {READ['adafruit']}. DigiKey marks only its own FedEx shipments delivered and Adafruit only "
               "its October 26 order, so the building's front-desk log settles the rest. One section per project, one table each; a part shared by several builds "
               "appears under each with \"n of m owned\" so the bins can be split. Every part is named by what it is, with the exact "
               "listing bought linked on the name; order numbers sit in the From column.")
    out.append("")
    out.append(f"Printable page (US Letter, black and grey): [{ARTIFACT_URL}]({ARTIFACT_URL}); "
               "the file is `reports/parts-by-project.html`, generated with the markdown by `reports/gen/parts_by_project.py`.")
    out.append("")
    out.append("## Still missing")
    out.append("")
    for m in MISSING:
        out.append(f"- {m}")
    out.append("")
    out.append("## What the accounts corrected")
    out.append("")
    for c in CORRECTIONS:
        out.append(f"- {c}")
    out.append("")
    for title, folder, intro, rows in PROJECTS:
        out.append(f"## {title} (`{folder}`)")
        out.append("")
        out.append(intro)
        out.append("")
        out.append("| ☐ | Qty for this build | Part | From | Status, read 2026-11-03 | Bin note |")
        out.append("| --- | --- | --- | --- | --- | --- |")
        for r in rows:
            out.append(md_row(r))
        out.append("")
    out.append("## Shared stock, split across the bins")
    out.append("")
    out.append("Counts come from the Orders page and the mails read today; \"spare\" is what is left after every build above takes its share. Bins at the bench (2026-11-03): one per project, a shared bin for parts that active projects share, and a backcase bin for spares that belong to no project; the builder says where each pack went, and the rows record it.")
    out.append("")
    out.append("| Part | Owned | Where and when | Who takes what | Spare |")
    out.append("| --- | --- | --- | --- | --- |")
    for part, owned, where, split, spare in SHARED:
        out.append(f"| {md_cell(part)} | {md_cell(owned)} | {md_cell(where)} | {md_cell(split)} | {md_cell(spare)} |")
    out.append("")
    out.append("## Delivered on 2026-11-02; picked up 2026-11-03 (all four pick-up tasks completed 3 p.m.)")
    out.append("")
    out.append("The routine's list held no task for these four parcels at 06:20 EST; the routine session created one per order at 06:48, due 3 p.m. today. "
               "They are at the front desk per the building's log; a pick-up counts as confirmed only when its task is completed, "
               "so they sit here and in the tracker's order table, not in its confirmed pick-ups.")
    out.append("")
    out.append("| Delivered | Order | Items | Project |")
    out.append("| --- | --- | --- | --- |")
    for d, o, items, proj in PICKUPS_WITHOUT_TASK:
        out.append(f"| {d} | {md_cell(o)} | {md_cell(items)} | {proj} |")
    out.append("")
    MD_OUT.write_text("\n".join(out) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- html

def status_class(status: str) -> str:
    s = status.lower()
    if s.startswith("on hand"):
        return "ok"
    if s.startswith("in transit"):
        return "in"
    if s.startswith("cancelled"):
        return "x"
    return "no"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


CSS = """
/* Layout: a sorting sheet. One page per project on Letter; a quiet two-tone sheet on screen. */
:root{
  --bg:#FFFFFF; --fg:#1B1D21; --mute:#5C6168; --line:#C6C9CE; --soft:#F2F3F5; --rule:#1B1D21;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif;
  --body:"Public Sans","Segoe UI",system-ui,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){ --bg:#15171A; --fg:#E8E9EB; --mute:#9CA2AA; --line:#3A3F46; --soft:#1E2126; --rule:#E8E9EB; color-scheme:dark }
}
:root[data-theme="dark"]{ --bg:#15171A; --fg:#E8E9EB; --mute:#9CA2AA; --line:#3A3F46; --soft:#1E2126; --rule:#E8E9EB; color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.5;margin:0;
     padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 72px}
.wrap{max-width:1040px;margin:0 auto}
h1,h2,h3{font-family:var(--display);text-wrap:balance;line-height:1.1;margin:0}
h1{font-size:clamp(28px,5vw,40px);font-weight:900;letter-spacing:-0.015em}
h2{font-size:clamp(19px,3vw,24px);font-weight:700}
h3{font-size:12.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--mute);margin-bottom:6px}
p{margin:8px 0;max-width:78ch}
a{color:var(--fg);text-decoration:underline;text-decoration-color:var(--mute);text-underline-offset:2px}
a:focus-visible{outline:2px solid var(--fg);outline-offset:2px}
.masthead{border-bottom:4px solid var(--rule);padding-bottom:14px;margin-bottom:14px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);font-weight:700}
.sub{font-family:var(--mono);font-size:12.5px;color:var(--mute);margin-top:8px;line-height:1.5;max-width:none}
.folder{font-family:var(--mono);font-size:12.5px;color:var(--mute);font-weight:400;margin-left:10px;white-space:nowrap}
section.project{margin-top:34px}
.intro{max-width:78ch;margin:8px 0 12px}
ul{max-width:78ch;padding-left:20px;margin:6px 0}
li{margin:5px 0}
.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:6px 0 0}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:var(--display);font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);border-bottom:2px solid var(--rule)}
td.box{width:22px;padding-right:0}
td.box span{display:inline-block;width:12px;height:12px;border:1.5px solid var(--fg);border-radius:2px;margin-top:3px}
td.qty{white-space:nowrap;font-variant-numeric:tabular-nums}
td.from{font-family:var(--mono);font-size:11.5px;color:var(--mute)}
td.st{min-width:150px}
.pill{display:inline-block;font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
      padding:1px 7px;border-radius:999px;border:1px solid var(--fg);margin-right:6px;white-space:nowrap}
.pill.ok{background:var(--fg);color:var(--bg)}
.pill.in{background:var(--bg);color:var(--fg)}
.pill.no{background:var(--soft);color:var(--mute);border-color:var(--mute)}
.pill.x{background:var(--soft);color:var(--mute);border-color:var(--mute);text-decoration:line-through}
td.note{color:var(--mute);font-size:12.5px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:0 28px}
@media (max-width:720px){.two{grid-template-columns:1fr}}
.card{border:1px solid var(--line);border-radius:5px;padding:12px 16px;margin-top:16px;background:var(--soft)}
.card ul{max-width:none}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@page{size:Letter;margin:0.5in}
@media print{
  :root{--bg:#FFFFFF;--fg:#000000;--mute:#555555;--line:#999999;--soft:#FFFFFF;--rule:#000000}
  body{font-size:10pt;padding:0;background:#fff;color:#000}
  .wrap{max-width:none}
  a{text-decoration:none;color:#000}
  section.project{break-before:page;margin-top:0}
  .shared{break-before:page}
  tr,li{break-inside:avoid}
  thead{display:table-header-group}
  table{font-size:9pt}
  td.from{font-size:8pt}
  td.note{font-size:8.5pt}
  .pill{font-size:7.5pt;padding:0 5px}
  .card{background:#fff;border-color:#999}
}
"""


def write_html():
    out = []
    out.append("<title>Parts by Project</title>")
    out.append('<meta name="claude:viewport-fit-sides" content="cover">')
    out.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    out.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;900&family=Public+Sans:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap">')
    out.append(f"<style>{CSS}</style>")
    out.append('<div class="wrap">')
    out.append('<header class="masthead">')
    out.append('<div class="eyebrow">DIY · sorting sheet · read 2026-11-03</div>')
    out.append("<h1>Parts by project</h1>")
    out.append(f'<p class="sub">{esc(READ["amazon"])}.<br>{esc(READ["mail"])}.<br>{esc(READ["todoist"])}.<br>'
               f'{esc(READ["digikey"])}; {esc(READ["adafruit"])}. DigiKey marks only its own FedEx shipments delivered and Adafruit only its October 26 order; the building\'s front-desk log settles the rest.</p>')
    out.append('<p class="sub">One page per project. Tick the box as the part goes into the bin. A shared part appears under each build that uses it as "n of m owned". '
               'The name links the exact listing bought; order numbers sit in the From column. The same list is DIY/PARTS_BY_PROJECT.md.</p>')
    out.append("</header>")
    out.append('<div class="two">')
    out.append('<div class="card"><h3>Still missing</h3><ul>')
    for m in MISSING:
        out.append(f"<li>{esc(m)}</li>")
    out.append("</ul></div>")
    out.append('<div class="card"><h3>What the accounts corrected</h3><ul>')
    for c in CORRECTIONS:
        out.append(f"<li>{esc(c)}</li>")
    out.append("</ul></div>")
    out.append("</div>")
    for title, folder, intro, rows in PROJECTS:
        out.append('<section class="project">')
        out.append(f'<h2>{esc(title)}<span class="folder">{esc(folder)}/</span></h2>')
        out.append(f'<p class="intro">{esc(intro)}</p>')
        out.append('<div class="tw"><table>')
        out.append("<thead><tr><th></th><th>Qty for this build</th><th>Part</th><th>From</th><th>Status, read 2026-11-03</th><th>Bin note</th></tr></thead><tbody>")
        for qty, name, url, source, status, note in rows:
            cls = status_class(status)
            label = {"ok": "on hand", "in": "in transit", "no": "not ordered", "x": "cancelled"}[cls]
            rest = status
            for prefix in ("on hand", "in transit", "not ordered", "cancelled"):
                if rest.lower().startswith(prefix):
                    rest = rest[len(prefix):].lstrip(" ·")
                    break
            out.append("<tr>"
                       f'<td class="box"><span aria-hidden="true"></span></td>'
                       f'<td class="qty">{esc(qty)}</td>'
                       f'<td><a href="{esc(url)}" target="_blank" rel="noopener">{esc(name)}</a></td>'
                       f'<td class="from">{esc(source)}</td>'
                       f'<td class="st"><span class="pill {cls}">{label}</span>{esc(rest)}</td>'
                       f'<td class="note">{esc(note)}</td>'
                       "</tr>")
        out.append("</tbody></table></div>")
        out.append("</section>")
    out.append('<section class="project shared">')
    out.append("<h2>Shared stock, split across the bins</h2>")
    out.append('<p class="intro">Counts come from the Orders page and the mails read today; "spare" is what is left after every build takes its share. Bins at the bench (2026-11-03): one per project, a shared bin for parts that active projects share, and a backcase bin for spares that belong to no project; the builder says where each pack went, and the rows record it.</p>')
    out.append('<div class="tw"><table><thead><tr><th>Part</th><th>Owned</th><th>Where and when</th><th>Who takes what</th><th>Spare</th></tr></thead><tbody>')
    for part, owned, where, split, spare in SHARED:
        out.append(f"<tr><td>{esc(part)}</td><td class=\"qty\">{esc(owned)}</td><td class=\"from\">{esc(where)}</td><td>{esc(split)}</td><td class=\"qty\">{esc(spare)}</td></tr>")
    out.append("</tbody></table></div>")
    out.append("<h3 style=\"margin-top:22px\">Delivered on 2026-11-02; picked up 2026-11-03 (all four pick-up tasks completed 3 p.m.)</h3>")
    out.append('<p class="intro">The routine\'s list held no task for these parcels at 06:20 EST; one per order was created at 06:48, due 3 p.m. today. They are at the front desk per the building\'s log; '
               'a pick-up counts as confirmed only when its task is completed, so they sit here and in the tracker\'s order table, not in its confirmed pick-ups.</p>')
    out.append('<div class="tw"><table><thead><tr><th>Delivered</th><th>Order</th><th>Items</th><th>Project</th></tr></thead><tbody>')
    for d, o, items, proj in PICKUPS_WITHOUT_TASK:
        out.append(f"<tr><td class=\"qty\">{esc(d)}</td><td class=\"from\">{esc(o)}</td><td>{esc(items)}</td><td>{esc(proj)}</td></tr>")
    out.append("</tbody></table></div>")
    out.append("</section>")
    out.append("</div>")
    HTML_OUT.write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_md()
    write_html()
    rows = sum(len(p[3]) for p in PROJECTS)
    print(f"wrote {MD_OUT.relative_to(ROOT)} and {HTML_OUT.relative_to(ROOT)}: {len(PROJECTS)} projects, {rows} rows, {len(SHARED)} shared lines")
