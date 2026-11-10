"""Mars rover, step 1 of the builder's rule: the final build first, the science after.

Writes, from the data at the top of this file (edit the script, not the outputs):
  docs/pages/mars-rover-build.html             the page: form sheet, wiring sheet, decisions, pin map, nets, budget, parts
  docs/pages/print/mars-rover-build.pdf         Letter, black only: form sheet (landscape), wiring sheet (landscape), then the notes (portrait)
  docs/pages/print/mars-rover-form-sheet.pdf    the form sheet alone
  docs/pages/print/mars-rover-wiring-sheet.pdf  the wiring sheet alone
  docs/FINAL_BUILD.md                           the same decisions, pin map, nets, budget and parts as Markdown

Reference: Huy Vector, "DIY Micro RC Spy Tank", huyvector.org/robots-kinetic/diy-micro-rc-spy-tank and its video
(youtube.com/watch?v=PszrmrE7JQU), read 2026-11-06: a 1 mm copper-wire frame, two DC gear motors, three 16340 cells and two
USB-C charging modules, a toy RC receiver board, an analog FPV camera, two 3 W LEDs on a 56 ohm resistor, a switch, and
hand-made treads. Its video, re-read 2026-11-07 from 3:30 to 5:30, shows the treads: links of short rods soldered side by
side, tied together with thread round notched drums. Ours keeps the idea (a palm-sized tracked chassis with a camera and a
light on a wire frame, hand-made metal treads, a 16340 and USB-C charging) and is its own build otherwise: a cute little
tank with a head that sits right on its screen and turns, a camera, a laser ranger, a flashlight and a blinking beacon in
the head, and Wi-Fi to a phone instead of an RC radio. Rev D (2026-11-07): brass treads on brass drums, no mast, a white
card hull and head (Revs D to F, set aside); Rev G is an open wire frame with the boards soldered on it; Rev H runs
the treads on wide aluminium drums with ivory faces, cut on SendCutSend's laser like the reference's machined 30 mm drums
(cad/drum.py, whose numbers this script imports), and skins the black boards in ivory. Rev K (2026-11-10) puts it on a frame of six
brass tubes, drops every skin and all paint for parts that come black (the rest hung out of sight), and gives it a voice.

The hop-drawing Router is imported from pocket_ai_assistant/edu/pages/gen/wiring_sheet.py, as the hologram's and the
satellite's generators do; the subclass adds the pin registry and the clearance check. Every electrical and mechanical number
is a datasheet or product-page figure read 2026-11-06 (Pololu product pages, the Motoron user's guide and pinout, the Pololu
track-set, gearmotor and bracket drawings, the FEETECH FS0307 datasheet, the Seeed XIAO ESP32-S3 wiki, the Adafruit product
page, the ADDtek AMC7135 datasheet) or an owned-part record. Nothing here has been built."""
from __future__ import annotations

import math
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
DOCS = PAGES.parent
PROJECT = DOCS.parent
OUT = PAGES / "mars-rover-build.html"
PRINT = PAGES / "print"
STYLE = (HERE / "page_style.css").read_text()

sys.path.insert(0, str(PROJECT.parent / "pocket_ai_assistant" / "edu" / "pages" / "gen"))
from wiring_sheet import Router as _Router  # noqa: E402
sys.path.insert(0, str(PROJECT / "cad"))
import drum as DRUM  # noqa: E402  the wheels: the drum the laser cuts, and its tread
from gear_plate import clearance, outline as wheel_outline, poly_area  # noqa: E402

W, H = 1360, 860
TODAY = "2026-11-06"
APPROVED = "2026-11-06"                                            # the builder approved Rev A as drawn
REV_E = "2026-11-07"                                               # Rev E: Rev D with a small head (camera and beacon only) on a 60 mm hull that holds the rest
REV_F = "2026-11-07"                                               # Rev F: Rev E with the head low and wide (the camera board on its side)
REV_G = "2026-11-07"                                               # Rev G: no card at all: an open wire frame with the boards soldered on it
REV_H = "2026-11-07"                                               # Rev H: metal wheels with ivory faces (laser-cut aluminium drums since v14, 2026-11-08); ivory brass skins instead of black; approved as drawn 2026-11-08
APPROVED_H = "2026-11-08"                                          # the builder approved Rev H (v14) as drawn
REV_I = "2026-11-09"                                               # Rev I: 35 mm drums, the axles 52 mm apart, Crumb's LiDAR on the roof; set aside the same day
REV_J = "2026-11-09"                                               # Rev J: Rev I without the LiDAR ("it's too big ... I want the device to look quite cute"); the drone's spare 8x8 ranger in the head
APPROVED_J = "2026-11-09"                                          # the builder approved Rev J as drawn
REV_K = "2026-11-10"                                               # Rev K, for approval: a brass frame ("brass tubes"), no paint and no skins (builder's rule 2026-11-09), a voice
DRUMS = "2026-11-08"                                               # the builder said yes to the drum, wider like the reference's, cut by SendCutSend
PHYSICS_PAGE = "https://claude.ai/artifact/FofYqDkSvY7paqYTDtg6mZ"  # step 2, written by physics_page.py

# ----------------------------------------------------------------------------- links (component names in prose, links on the word)
A = "https://www.adafruit.com/product/"
AMZ = "https://www.amazon.com/dp/"
PL = "https://www.pololu.com/product/"
L = {
    "xiao": AMZ + "B0C69FFVHH",            # Seeed XIAO ESP32-S3 Sense, the family's listing (four bought, all allocated)
    "xiao_wiki": "https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/",
    "tracks": PL + "3030",                 # Pololu 22T Track Set, black: Rev A's tracks, dropped in Rev D (still a line in the DigiKey cart)
    "motor": PL + "1097",                  # Pololu 150:1 Micro Metal Gearmotor LP 6V
    "motoron": PL + "5079",                # Pololu Motoron M2T550 dual I2C motor controller, headers not soldered
    "motoron_guide": "https://www.pololu.com/docs/0J84",
    "ranger": PL + "3415",                 # Pololu VL53L1X carrier
    "tof8": PL + "3418",                   # Pololu VL53L7CX carrier, 8x8 zones: the drone's spare (owned, DigiKey 2026-10-28)
    "servo": PL + "3420",                  # FEETECH FS0307 sub-micro servo
    "boost": PL + "2562",                  # Pololu 5 V step-up U1V11F5
    "charger": A + "4410",                 # Adafruit Micro-Lipo USB-C (MCP73831); also DigiKey and Micro Center
    "brass_tube": AMZ + "B0F2FKLC2N",     # M METERXITY brass tube set, 2-7 mm OD x 0.5 mm wall (owned): the 4 mm tube is the drums' hubs
    "rod10": AMZ + "B005WPB7YG",           # K&S #9861 1.0 mm x 300 mm round brass rod, 5 rods: the planks' face rods
    "drum": "https://sendcutsend.com/materials/6061-aluminum/",   # SendCutSend laser cutting, 6061-T6 0.375 in: the drum halves, from cad/mars-rover-drum.dxf
    "tube332": AMZ + "B079VL3XD1",   # K&S 8126, 3/32 in x 0.014 in wall x 12 in: the pins
    "m3x25": AMZ + "B07Q6WY2H9",     # M3 x 25 button heads, 50: the idlers' axles
    "sheet": AMZ + "B0006N6WLM",           # K&S 250 brass sheet, 0.005 in x 4 x 10 in, 6-pack: the ivory skins (True Value sells single sheets)
    "paint": AMZ + "B000PIG3AS",           # Rust-Oleum Stops Rust spray, gloss canvas white 7789830 (owned): the ivory
    "ca": AMZ + "B003Y49R7G",   # Loctite Super Glue Ultra Gel Control, 4 g
    "cell":"https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery",
    "holder": AMZ + "B0CRGK889F",
    "pigtail": AMZ + "B0F6T4LKDG",
    "toggle": AMZ + "B0CZ6XZ2P9",
    "oled": AMZ + "B09T6SJBV5",
    "star": AMZ + "B00LWU5DWM",
    "lens": "https://www.digikey.com/en/products/detail/carclo-technical-plastics/10412/2641658",
    "amc": AMZ + "B0CST7GZTN",
    "chip": AMZ + "B09QGJ9LY7",
    "rod15": AMZ + "B082ZNMD46",
    "wire26": AMZ + "B07G2LRX68",
    "wire30": AMZ + "B073RDGTPB",
    "kapton": AMZ + "B072Z92QZ2",
    "nickel": AMZ + "B0BSTSMLF7",             # CRAFT WIRE nickel silver, dead soft; the 20-gauge spool makes the tread's loops
    "resistors": AMZ + "B0F4P352BB",
    "caps": AMZ + "B0C1VBXCQM",
    "crumb_motor": AMZ + "B0C9QC4SRY",     # Crumb's N20 2-pack: the cheaper drive; any 3 mm D-shaft takes the drum's hub
    # Rev K: parts that come black, read off their makers' photos 2026-11-10
    "chg_black": "https://www.digikey.com/en/products/detail/adafruit-industries-llc/6106/25805552",   # Adafruit bq25185 charger with a 5 V boost, black
    "oled_black": A + "326",               # Adafruit 0.96" 128x64 OLED, STEMMA QT, black board (DigiKey 1528-1220-ND)
    "tof_black": AMZ + "B09JLKKW1H",       # AITRIP VL53L1X module with cover, black, 25 x 10.7 x 3.2 mm, 2-pack
    "tof8_black": "https://shop.sb-components.co.uk/products/vl53l5cx-8x8-time-of-flight-tof-array-sensor-breakout",   # Pimoroni VL53L5CX, black; in stock here 2026-11-10
    "tof8_maker": "https://shop.pimoroni.com/products/vl53l5cx-time-of-flight-tof-sensor-breakout",
    "speaker": "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309",   # owned, black
    "amp": AMZ + "B0CDWXZZCH",             # HiLetgo MAX98357A, owned (purple)
    "reference": "https://www.huyvector.org/robots-kinetic/diy-micro-rc-spy-tank",
    "video": "https://www.youtube.com/watch?v=PszrmrE7JQU",
}

# ----------------------------------------------------------------------------- the numbers (mm unless said)
# Coordinates: x to the rover's right, y up from the desk, z forward. Origin on the desk under the body's centre.
D = dict(
    # the treads: each plank a 3/32 in brass tube with two 1 mm brass rods soldered under it, side by side on the tread
    # face; the tube is longer and its ends are the hinge pins, joined by loops of 24-gauge nickel silver.
    # Rev H (since v14): the planks run on four aluminium drums cut on SendCutSend's laser from cad/drum.py, each two 3/8 in
    # halves of 6061 glued face to face: 19 mm wide, 14 round seats, 30.5 mm over the teeth. The reference's drums, machined
    # by PCBWay (3:16 to 3:44 in its video), are about 30 mm across and 22 wide. The laser can't cut a seat for a 1 mm rod in
    # plate this thick, so the pins are tubes; each sits in a seat 0.12 mm loose, and the teeth stay 1.3 mm under the face.
    rod1=1.0, pin_d=DRUM.PIN_D, pin_wall=DRUM.TUBE_WALL, pin_out=DRUM.PIN_OUT, guide=DRUM.GUIDE, loop_wire=DRUM.LOOP_WIRE,
    gear_n=DRUM.Z, drum_w=DRUM.WIDTH, drum_ra=DRUM.R_TIP, drum_rf=DRUM.RF, drum_hole=DRUM.HOLE,
    hub_d=4.0, hub_id=3.0,           # the owned 4 mm brass tube, 3 mm inside: each drum's hub
    screw_l=25.0, screw_head=1.65, washer=0.5,   # the idlers' M3 x 25 button-head screws and their washers
    # Pololu micro metal gearmotor drawing (precious-metal brushes, no encoder, 3 Apr 2024)
    gb_z=12.0, gb_y=10.0, gb_l=9.0, can_l=15.0, ol=25.6, tab=1.5, shaft=10.0, boss=0.7,
    face_x=32.8,                     # each gearbox face, from the centre line: the drum's hub runs from it to the tread
    # frame, Rev K: brass tube, 0.5 mm wall (the owned METERXITY sets), six straight pieces lapped and soldered, no bends.
    # Two 3 mm rails run down the middle as a spine, between the motors' end tabs; two 3 mm rungs under the motors; a 4 mm
    # front axle that the idler drums turn on; a 3 mm back bar behind the servo.
    tube=3.0, tube_id=2.0, axle_d=4.0, collar_d=5.0, collar_l=2.0, rail_x=4.5,
    # body parts
    holder_l=43.0, holder_w=18.0, holder_h=14.0, cell_d=16.6, cell_l=34.1,
    chg_l=29.2, chg_w=19.1, chg_t=7.6,   # Rev K: the black charger with its own 5 V boost (Adafruit), USB-C on a short end; parts side to the holder
    mot_l=20.3, mot_w=15.2,          # Motoron 0.8" x 0.6"
    amp_l=19.0, amp_w=16.0,          # the HiLetgo amplifier, 19 x 16, blue (Crumb's measure)
    under_t=3.0,                     # the boards under the motors, components down, about 3 mm deep
    spk_l=20.0, spk_w=13.0, spk_h=4.87,   # the Same Sky enclosed speaker (datasheet), black, firing from its 20 x 13 face
    oled_w=29.2, oled_h=31.75, oled_gw=26.6, oled_gh=19.3, oled_gt=4.3, oled_t=6.2,   # Rev K: Adafruit's black 0.96" board, its two lower tabs included (fab print)
    tog_l=13.0, tog_w=8.0, tog_h=10.0, tog_bush=6.0, tog_lever=10.0,
    # the parts on the open frame: servo (turning the head from below), boost, ranger, lamp
    srv_l=20.0, srv_w=8.3, srv_h=17.3, srv_shaft=5.0,   # FS0307; the output shaft about 5 mm from one end
    horn=4.5,                                           # the horn 3 mm over the servo and a 1.5 mm brass spacer, so the head clears the taller screen
    tof_w=10.7, tof_h=25.0, tof_t=3.2, tof_tilt=30.0, tof_x=-22.65,  # Rev K: the black ranger (AITRIP listing), on a brass stub on the axle, left of the screen
    lamp_d=14.0, lens_d=10.0, lamp_depth=9.0, lamp_x=22.5,           # on a brass stub on the axle, right of the screen
    # the head: only the controller with its camera, and the beacon
    x_w=17.8, x_h=21.0, x_d=15.0,    # XIAO ESP32-S3 with the Sense board: 21 x 17.8 x 15 (Seeed)
    t8_w=19.0, t8_h=19.0, t8_t=4.6,  # Rev K: Pimoroni's black 8x8 ranger, its parts on the back so the face is flat, beside the camera board
    gap=1.0,
)
D["plank_l"] = D["drum_w"] + 2 * D["guide"]                         # 19.86: the face rods; the loops ride 0.4 mm outside each drum face
D["pin_l"] = D["plank_l"] + 2 * D["pin_out"]                         # 23.86: the pin tube, its ends standing out for the loops
D["drum_r"] = DRUM.R_PIN                                             # 14.45: the pin tubes' line round a drum (the hinge line)
D["plank_p"] = DRUM.PITCH                                            # 6.43: the plank pitch, one seat each
D["face_h"] = DRUM.H_FACE                                            # 1.61: the face rods' centres, out from the tube's
D["face_r"] = DRUM.R_FACE                                            # 16.56: the tread's face round a drum
D["drum_od"] = 2 * D["drum_ra"]                                      # 30.5 over the teeth
D["tri_h"] = D["pin_d"] / 2 + D["face_h"] + D["rod1"] / 2            # 3.3: a plank's thickness, desk to the top of its tube
D["plank_w"] = D["pin_d"]                                            # 2.4: its width along the tread
D["sp_d"] = 2 * D["face_r"]                                          # 33.1
D["tr_h"] = D["sp_d"]
D["pitch"] = DRUM.CENTRES * D["plank_p"]                             # 45.0: drum centres, whole pitches for an even drum
D["planks"] = round(D["gear_n"] + 2 * D["pitch"] / D["plank_p"])     # 28 a track
D["axle_y"] = D["tr_h"] / 2                                          # 16.56
D["drive_z"], D["idler_z"] = -D["pitch"] / 2, D["pitch"] / 2         # -26.1, +26.1
D["r1_z"], D["r2_z"] = D["drive_z"] - 3.5, D["drive_z"] + 3.5       # the two rungs under the motors, both inside the gearboxes' 12 mm
D["tr_end"] = D["pitch"] / 2 + D["tr_h"] / 2                         # 44.9
D["spr_x0"] = D["face_x"] + D["boss"]                                # the gearbox's boss: 33.5
D["drum_x0"] = D["spr_x0"] + 2.0                                     # 35.5: the drum's inner face, 2 mm off the gearbox's boss (the drums are cut)
D["drum_x1"] = D["drum_x0"] + D["drum_w"]                            # 54.6
D["tr_x0"], D["tr_x1"] = D["drum_x0"] - D["guide"], D["drum_x1"] + D["guide"]   # the face rods' ends; the loops just outside steer the tread
D["teeth_x"] = (D["tr_x0"] + D["tr_x1"]) / 2                         # the tread's centre line: 45.0
D["tr_w"] = D["plank_l"]
D["pin_x0"], D["pin_x1"] = D["tr_x0"] - D["pin_out"], D["tr_x1"] + D["pin_out"]           # the pin tubes' ends 33.1 .. 57.0
D["hub_x0"], D["hub_x1"] = D["spr_x0"] + 0.2, D["drum_x1"] + 0.5     # each hub, from the boss to 0.5 mm past the drum
D["hub_l"] = D["hub_x1"] - D["hub_x0"]                               # 21.4
D["shaft_grip"] = D["face_x"] + D["shaft"] - D["hub_x0"]             # 9.1: the hub crimped on the motor's shaft
D["collar_x0"] = D["drum_x0"] - 0.2 - D["collar_l"]                  # Rev K: the idlers turn on the axle between two 5 mm collars
D["axle_x1"] = D["drum_x1"] + 0.2 + D["collar_l"]                    # the axle's ends, flush with the outer collars
D["width"] = 2 * max(D["pin_x1"], D["axle_x1"])                      # 114: the pin tubes' ends
D["mot_y0"], D["mot_y1"] = D["axle_y"] - D["gb_y"] / 2, D["axle_y"] + D["gb_y"] / 2  # 13.8 .. 23.8
D["mot_z0"], D["mot_z1"] = D["drive_z"] - D["gb_z"] / 2, D["drive_z"] + D["gb_z"] / 2   # -32.1 .. -20.1
D["mot_x_in"] = D["face_x"] - D["ol"]                                 # 7.2: each motor's end tabs, a 14 mm gap between them
D["rung_y"] = D["mot_y0"] - D["tube"] / 2                         # 12.3: the rungs carry the motors
D["rail_y"] = D["mot_y0"] + D["tube"] / 2                         # 15.3: the rails lie on the rungs (crossing laps), between the motors
D["axle_y_frame"] = D["rail_y"] + D["tube"] / 2 + D["axle_d"] / 2  # 18.8: the 4 mm axle lies on the rails; the drums' height to the hundredth
D["piv_x"] = 0.0
D["srv_y0"] = D["rail_y"] + D["tube"] / 2                         # 16.8: the servo stands on the rails, shaft up
D["srv_top"] = D["srv_y0"] + D["srv_h"]                           # 34.1
D["head_floor"] = D["srv_top"] + D["horn"]                        # 37.1: the head's cradle sits on the horn
D["piv_z"] = D["idler_z"] - D["axle_d"] / 2 - 0.1 - D["srv_w"] / 2   # 19.8: the servo's front face against the axle
D["bar_z"] = D["piv_z"] - D["srv_w"] / 2 - 0.1 - D["tube"] / 2   # 14.1: the back bar behind the servo, lying on the rails
D["bar_y"] = D["rail_y"] + D["tube"]                              # 18.3
D["bar_x"] = D["rail_x"] + 3.0                                    # it spans the rails and 3 mm past each
D["rail_z0"], D["rail_z1"] = D["r1_z"] - D["tube"] / 2 - 4.0, D["idler_z"] + D["axle_d"] / 2 + 1.0   # the rails' open ends
D["oled_z"] = D["idler_z"] + D["axle_d"] / 2 + 0.3                # 28.4: the display's back, glued to the axle's front
D["oled_top"] = D["head_floor"] - 1.8                             # 36.8: the head turns 1.8 mm over it
D["oled_bot"] = D["oled_top"] - D["oled_h"]                       # 5.1: the lower edge of its two tabs
D["face_z"] = D["oled_z"] + D["oled_t"]                           # 34.6: the display's glass, the face of the rover
D["holder_y0"] = D["mot_y1"]                                      # the holder sits on the motor cans: 23.8
D["holder_z0"], D["holder_z1"] = D["drive_z"] - D["holder_w"] / 2, D["drive_z"] + D["holder_w"] / 2   # -35.1 .. -17.1
D["chg_z1"] = D["holder_z0"] - 0.5                                # Rev K: the black charger stands against the holder's back face, port up
D["chg_z0"] = D["chg_z1"] - D["chg_t"]
D["chg_y0"] = D["holder_y0"] + D["holder_h"] + 0.5 - D["chg_l"]  # its USB-C half a millimetre over the holder's top
D["tog_z0"], D["tog_y0"] = D["holder_z1"], D["rail_y"] + D["tube"] / 2   # Rev K: the switch stands on the rails against the holder's front face, across
D["tog_z1"] = D["tog_z0"] + D["tog_w"]                            # 8 mm deep; the screen hides it from the front, the holder from behind
D["under_y1"] = D["rung_y"] - D["tube"] / 2                       # 10.8: the boards out of sight hang under the rungs, backs up
D["under_y0"] = D["under_y1"] - D["under_t"]
D["spk_y0"] = D["rail_y"] + D["tube"] / 2                         # the speaker lies on the rails behind the head, firing up
D["spk_z0"] = D["tog_z1"] + 0.5                                  # just ahead of the switch
D["spk_z1"] = D["spk_z0"] + D["spk_w"]
D["tof_cy"] = D["head_floor"] - 1.0 - D["tof_h"] / 2 * math.cos(math.radians(D["tof_tilt"]))   # its top edge a millimetre under the head
D["tof_z"] = D["face_z"] - 1.5
D["lamp_z"] = D["face_z"] - 1.6 - D["lamp_depth"] / 2              # the star's back, so the lens comes flush with the screen's glass
D["lamp_cy"] = D["axle_y"] + D["axle_d"] / 2 + 0.4 + D["lamp_d"] / 2   # the star just clears the axle's top
D["tof_y"], D["lamp_y"] = D["tof_cy"], D["lamp_cy"]
D["clear_rails"] = D["rung_y"] - D["tube"] / 2                    # the frame's underside: the rungs
D["clear"] = min(D["clear_rails"], D["oled_bot"], D["under_y0"], D["chg_y0"])   # lowest part over the desk

# the head, in its own frame: origin on the servo shaft at the horn's top; x_h right, y_h up, z_h forward.
# Rev G: the controller stack alone, bare (its boards are black), on its side so its 21 mm length runs across, sitting
# in a cradle of two 1 mm brass rods glued to the horn and soldered to the board's ground pad. The head's outline is the
# stack itself; the lens stands 0.6 mm proud of its face.
_hw = D["x_h"] + 1.0 + D["t8_w"]                                   # Rev J: the camera board and the 8x8 ranger, 1 mm apart, centred on the shaft
HD = dict(x_x0=-_hw / 2, x_x1=-_hw / 2 + D["x_h"], y0=1.5, x_z0=-D["x_d"] / 2, x_z1=D["x_d"] / 2)
HD["t8_x0"], HD["t8_x1"] = HD["x_x1"] + 1.0, _hw / 2              # the 8x8 ranger on the head's right, looking forward
HD["t8_z0"] = HD["x_z1"] - D["t8_t"]                              # its board flush with the camera board's front
HD["y1"] = HD["y0"] + D["x_w"]                                   # 19.3
HD["cam_cx"], HD["cam_cy"] = (HD["x_x0"] + HD["x_x1"]) / 2, HD["y0"] + D["x_w"] / 2
HD["t8_cx"], HD["t8_cy"] = (HD["t8_x0"] + HD["t8_x1"]) / 2, HD["y0"] + D["t8_h"] / 2
HD["sh_x0"], HD["sh_x1"] = HD["x_x0"], HD["t8_x1"]                # Rev K: no sleeve; the head's outline is the bare boards
HD["sh_y0"], HD["sh_y1"] = 0.0, max(HD["y1"], HD["y0"] + D["t8_h"])
HD["sh_z0"] = HD["x_z0"]
HD["sh_z1"] = HD["x_z1"] + 0.6                                   # the lens, 0.6 mm proud of the camera board
HD["z0"], HD["z1"] = HD["sh_z0"], HD["sh_z1"]
HD["w"] = HD["sh_x1"] - HD["sh_x0"]
HD["cx"] = 0.0


def hx(xh):
    return D["piv_x"] + xh


def hy(yh):
    return D["head_floor"] + yh


def hz(zh):
    return D["piv_z"] + zh


D["height"] = hy(HD["sh_y1"]) + 0.5                              # the beacon chip on the head's top edge
D["head_front"] = hz(HD["sh_z1"])
D["length"] = max(D["tr_end"], D["head_front"]) + D["tr_end"]
D["cam_y"] = hy(HD["cam_cy"])
D["tof_reach"] = D["tof_y"] / math.tan(math.radians(D["tof_tilt"]))        # where the ranger's centre ray meets the desk, ahead of the face
D["tof_slant"] = D["tof_y"] / math.sin(math.radians(D["tof_tilt"]))

# Rev K: the frame is six straight brass tubes, lapped and soldered, no bends. Two rails (the spine) lie on two rungs under
# the motors and run forward under the servo; the 4 mm axle lies across their front ends; a short back bar lies across them
# behind the servo. Eight laps: each rail on each rung, the axle on each rail, the back bar on each rail.
TUBE = dict(rail=D["rail_z1"] - D["rail_z0"], rung=2 * (D["face_x"] - 0.5), bar=2 * D["bar_x"], axle=2 * D["axle_x1"])
TUBE["three"] = 2 * TUBE["rail"] + 2 * TUBE["rung"] + TUBE["bar"]   # mm of 3 mm tube
LAPS = 8
g_t3 = math.pi / 4 * (D["tube"] ** 2 - D["tube_id"] ** 2) * 8.5e-3                     # g per mm of 3 mm brass tube
g_t4 = math.pi / 4 * (D["axle_d"] ** 2 - (D["axle_d"] - 1.0) ** 2) * 8.5e-3          # and of 4 mm tube
g_t5 = math.pi / 4 * (D["collar_d"] ** 2 - D["axle_d"] ** 2) * 8.5e-3                # and of 5 mm tube
g_brass1 = math.pi / 4 * D["rod1"] ** 2 * 8.5e-3                 # g per mm of 1 mm brass rod
D["loop_len"] = 2 * (D["plank_p"] - 0.1) + math.pi * (D["pin_d"] + 0.1 + D["loop_wire"])   # one loop of wire, round two pins
D["rod_plank"] = 2 * D["plank_l"]                                                        # 39.7 mm of 1 mm rod in a plank
g_pin = math.pi / 4 * (D["pin_d"] ** 2 - (D["pin_d"] - 2 * D["pin_wall"]) ** 2) * D["pin_l"] * 8.5e-3   # its tube
g_plank = D["rod_plank"] * g_brass1 + g_pin + 0.05               # and its solder
g_loop = math.pi / 4 * D["loop_wire"] ** 2 * D["loop_len"] * 8.7e-3
WHEEL = wheel_outline(z=DRUM.Z, r_pin=DRUM.R_PIN, r_tip=DRUM.R_TIP, seat_r=DRUM.SEAT_R, flank=DRUM.FLANK)[0]   # a drum's edge, its own frame
g_half = (poly_area(WHEEL) - math.pi * (D["drum_hole"] / 2) ** 2) * DRUM.THICK * 2.70e-3       # one 3/8 in half, 6061
g_hub = math.pi / 4 * (D["hub_d"] ** 2 - D["hub_id"] ** 2) * D["hub_l"] * 8.5e-3   # a drive drum's brass hub
g_drum = DRUM.HALVES * g_half + g_hub
D["tread_g"] = 2 * D["planks"] * (g_plank + 2 * g_loop)
D["drums_g"] = 4 * DRUM.HALVES * g_half + 2 * g_hub + 4 * D["collar_l"] * g_t5   # Rev K: the idlers turn on the axle, no hubs
D["frame_g"] = TUBE["three"] * g_t3 + TUBE["axle"] * g_t4
D["rod1_mm"] = 2 * D["planks"] * D["rod_plank"] + 90.0                   # and the cradle, the stubs for the ranger and the lamp
D["tube_mm"] = 2 * D["planks"] * D["pin_l"]                              # 3/32 in tube for the pins
D["loops"] = 4 * D["planks"]
D["wire_m"] = D["loops"] * D["loop_len"] / 1000
D["tread_h"] = (2 * D["planks"] * 1.0 + D["loops"] * 3.25) / 60      # hours of handwork: a minute a plank, three and a quarter a loop

# masses (g) and where they sit (x, y, z): datasheet or listing figures, estimates marked in the notes
_fz = (2 * TUBE["rail"] * g_t3 * (D["rail_z0"] + D["rail_z1"]) / 2 + 2 * TUBE["rung"] * g_t3 * D["drive_z"]
       + TUBE["bar"] * g_t3 * D["bar_z"] + TUBE["axle"] * g_t4 * D["idler_z"]) / D["frame_g"]   # the frame's centre, front to back
MASS = [
    (f"brass treads: {2 * D['planks']} planks and {D['loops']} nickel-silver loops", D["tread_g"], (0, D["axle_y"], 0)),
    ("four aluminium drums of two halves each, the two drive hubs, four collars", D["drums_g"], (0, D["axle_y"], 0)),
    ("two gearmotors", 19.0, (0, D["axle_y"], D["drive_z"])),
    ("cell and holder", 26.0, (0, D["holder_y0"] + 7, D["drive_z"])),
    ("charger with its boost, switch", 5.5, (3, D["chg_y0"] + D["chg_l"] / 2, (D["chg_z0"] + D["chg_z1"]) / 2)),
    ("motor controller and amplifier, under the motors; the 100 and 220 µF", 4.5, (0, D["under_y0"] + 1.5, D["drive_z"])),
    ("speaker, on the spine", 1.6, (0, D["spk_y0"] + D["spk_h"] / 2, (D["spk_z0"] + D["spk_z1"]) / 2)),
    ("servo, on the rails", 4.4, (-5.0, (D["srv_y0"] + D["srv_top"]) / 2, D["piv_z"])),
    ("laser ranger, lamp and its regulator, the 220 µF", 4.0, (0, D["axle_y"] + 9.5, D["face_z"] - 3)),
    ("display", 3.0, (0, (D["oled_top"] + D["oled_bot"]) / 2, D["oled_z"] + 2)),
    ("frame: six brass tubes", D["frame_g"], (0, D["rail_y"] + 0.6, _fz)),
    ("head: controller with camera and microphone, the 8x8 ranger, beacon, cradle", 9.1, (hx(0.0), hy(10.0), hz(0.0))),
    ("wire, Kapton, glue", 4.5, (0, D["axle_y"] + 1.5, 0)),
]
D["mass"] = sum(m for _, m, _ in MASS)
D["cg"] = tuple(sum(m * p[i] for _, m, p in MASS) / D["mass"] for i in range(3))
D["tip_side"] = math.degrees(math.atan2(D["tr_x1"] - abs(D["cg"][0]), D["cg"][1]))
D["tip_back"] = math.degrees(math.atan2(D["cg"][2] - (D["drive_z"] - 2), D["cg"][1]))

# ----------------------------------------------------------------------------- speed and the energy budget (mA from the cell)
E = dict(
    rpm6=90.0, v_cell=3.7, load=0.85, track_pitch_d=2 * D["drum_r"],   # LP 150:1: 90 rpm at 6 V; the tread moves with its pins, 27.6 mm across
    xiao_wifi=110.0, xiao_cam=155.0, xiao_peak=366.0,            # Seeed wiki, at 3.8 V on BAT: Wi-Fi on; camera web stream; image capture peak
    tof=20.0, tof_peak=40.0, oled=12.0, motoron=4.0, boost_q=1.0,
    tof8=95.0, tof8_peak=150.0,                                  # Rev K: Pimoroni's 8x8 ranger on 3.3 V, about 95 mA ranging (ST), 150 at worst; asleep when parked
    mot_run=60.0, mot_stall6=360.0,                              # per motor on a desk (estimate); stall 0.36 A at 6 V (Pololu)
    srv_idle5=5.0, srv_run5=50.0, srv_stall5=400.0, eta=0.85,    # FS0307 at 4.8 V (datasheet), through the boost
    lamp=350.0, lamp_cap=0.5,                                    # one AMC7135; duty capped at 50 %
    beacon=4.0, beacon_duty=0.05,
    amp_q=2.4, talk=120.0, talk_peak=400.0,                      # Rev K: the I²S amplifier, idle (datasheet) and speaking at a room's level into 8 Ω (estimate)
    cell_mah=950, usable=0.9, charge_ma=500,
)
E["rpm"] = E["rpm6"] * E["v_cell"] / 6
E["speed_free"] = E["rpm"] / 60 * math.pi * E["track_pitch_d"]          # mm/s
E["speed"] = E["speed_free"] * E["load"]
E["mot_stall"] = E["mot_stall6"] * E["v_cell"] / 6
E["srv_idle"] = E["srv_idle5"] * 5 / (E["v_cell"] * E["eta"])
E["srv_run"] = E["srv_run5"] * 5 / (E["v_cell"] * E["eta"])
E["srv_stall"] = E["srv_stall5"] * 5 / (E["v_cell"] * E["eta"])
base = E["tof"] + E["oled"] + E["motoron"] + E["boost_q"] + E["srv_idle"] + E["beacon"] * E["beacon_duty"] + E["amp_q"]
E["parked"] = E["xiao_wifi"] + base
E["explore"] = E["xiao_cam"] + base + 2 * E["mot_run"] + 0.4 * (E["srv_run"] - E["srv_idle"]) + E["tof8"]   # Rev J: the 8x8 ranger ranges while it explores
E["night"] = E["explore"] + E["lamp"] * E["lamp_cap"]
E["talking"] = E["xiao_wifi"] + base + E["talk"]                 # Rev K: stopped, listening and speaking; the treads wait while it talks
E["peak_all"] = E["xiao_peak"] + E["tof_peak"] + E["oled"] + E["motoron"] + 2 * E["mot_stall"] + E["srv_stall"] + E["lamp"] + E["tof8_peak"]
E["peak_talk"] = E["xiao_peak"] + E["tof_peak"] + E["oled"] + E["motoron"] + E["srv_stall"] + E["lamp"] + E["tof8_peak"] + E["talk_peak"]   # the treads still
for k in ("parked", "explore", "night", "talking"):
    E[k + "_h"] = E["cell_mah"] * E["usable"] / E[k]
E["charge_h"] = E["cell_mah"] / E["charge_ma"] + 0.3
E["rail3v3_peak"] = E["xiao_peak"] + E["tof_peak"] + E["oled"] + E["motoron"] + E["tof8_peak"]

# ----------------------------------------------------------------------------- the contract: XIAO ESP32-S3 Sense pins (in the head)
PINS = [  # (pin, GPIO, job, goes to)
    ("D0", "1", "servo signal, 50 Hz, 900 to 2100 µs for 120°", "neck wire 6, down to the servo standing on the rails"),
    ("D1", "2", "flashlight: brightness by PWM, capped at 50 %", "neck wire 7, down to the regulator's VDD pin behind the lamp (it draws under 1 mA)"),
    ("D2", "3", "free", "nothing: a strapping pin (JTAG source), left alone"),
    ("D3", "4", "beacon, high = lit", "100 Ω, then the beacon chip's + lead, on the head's roof"),
    ("D4", "5", "I²C SDA, 400 kHz", "neck wire 4, down to the ranger, the display and the motor controller"),
    ("D5", "6", "I²C SCL", "neck wire 5, down to the same three"),
    ("D6", "43", "I²S word clock (LRCLK), 16 kHz", "neck wire 9, down to the amplifier's LRC; the console moves to the USB port, so UART0 is free"),
    ("D7", "44", "I²S bit clock (BCLK), 512 kHz", "neck wire 8, down to the amplifier's BCLK"),
    ("D8", "7", "I²C SDA of a second bus, 1 MHz", "the 8×8 ranger's SDA, in the head"),
    ("D9", "8", "I²C SCL of the second bus", "the 8×8 ranger's SCL, in the head"),
    ("D10", "9", "I²S data out (DIN), 16-bit mono", "neck wire 10, down to the amplifier's DIN; the Sense board's SD slot shares D8 to D10, so the slot stays empty"),
    ("mic (inside)", "42, 41", "the Sense board's digital microphone, PDM clock and data", "nothing to wire: it is on the camera board, its port facing forward"),
    ("3V3", "", "3.3 V out of the board's regulator, 700 mA available", "neck wire 3, down to the ranger VIN, the display VIN and the motor controller VDD; in the head, the 8×8 ranger's supply pin"),
    ("GND", "", "ground", "the beacon and the 8×8 ranger, from the header's GND pin; neck wire 2 at the BAT− pad"),
    ("BAT+ / BAT− pads", "", "the cell, up the neck, after the switch", "two pads on the back of the board; neck wires 1 and 2"),
    ("5V", "", "USB VBUS only: no voltage on battery", "nothing, ever"),
    ("USB-C", "", "flashing, once, on the bench; updates over Wi-Fi after that. It stays open on the head's left end", "a computer; flash with the switch on"),
]

I2C = [("laser ranger", "0x29"), ("display", "0x3D or 0x3C, by the jumper on its back"), ("motor controller", "0x10, plus the general call 0x00"),
       ("8×8 ranger, on its own bus (D8, D9)", "0x29, the laser ranger's address too: hence the second bus")]

NETS = [  # (net, from, to, wire, why)
    ("CELL", "the holder's two leads", "JST-PH pigtail into the charger's socket", "the holder's leads soldered to the owned pigtail, in heat-shrink, behind the charger",
     "The cell never meets an iron: the joint sits 40 mm from it. The button top is +. Meter the plug with the cell in before it goes into the socket."),
    ("VBAT", "charger BAT pad", "switch, the end lug the middle meets with the lever right (meter which)", "26 AWG, 20 mm",
     "The charger's BAT pad is the cell itself. Lever right joins it to the rover; lever left leaves the charger alone with the cell, so it charges cleanly."),
    ("BAT+", "switch, middle lug", "motor controller VIN · the 100 µF · amplifier VIN · its 220 µF · the charger's EN pad · through the left rail: the LED + pad · the 220 µF · neck wire 1", "26 AWG",
     "Everything runs straight off the cell, 3.0 to 4.2 V. The motor controller works from 1.8 V, the amplifier from 2.5 V, the controller board has its own regulator, and the flashlight's regulator is a current sink. The charger's EN pad rides on this rail, so its 5 V boost is on only while the rover is."),
    ("OFF", "switch, the other end lug", "the frame (ground)", "a 5 mm stub of 1 mm brass rod to the rail under it",
     "Lever left ties BAT+ to ground: the capacitors empty, the charger's EN pad goes low and its boost stops, so nothing drains the cell while the rover is off. A toggle breaks before it makes, so the cell never meets ground."),
    ("GND", "charger G pad, on the rear rung", "the frame · motor controller GND (power side) · the 100 µF · amplifier GND · the 220 µFs · servo − · regulator tab · neck wire 2", "the frame, and 26 AWG where a board sits off it",
     "The frame is ground, as in a circuit sculpture: each board's GND is soldered to the nearest tube. The motors' current returns through the rear rung, a few millimetres of brass from the charger's G pad; the head's comes down the neck on its own wire."),
    ("5V", "charger 5V pad", "through the right rail to the servo + lead", "30 AWG, then the servo's own lead",
     "The servo is rated 4.8 to 6 V, so it does not run on the cell. The charger's boost makes 5 V at up to 1 A, more than the servo's 0.4 A stall. It will not start under more than 200 mA, so the firmware waits for boot before it moves the head."),
    ("3V3", "neck wire 3", "display VIN · ranger VIN, and its XSHUT through 10 kΩ · through the left rail: motor controller VDD", "30 AWG",
     "The body's logic runs on the head's 3.3 V regulator. That matters for the motor controller: its 10 kΩ I²C pull-ups go to VDD, and VDD must not be the cell, or the bus would sit at 4.2 V on pins rated 3.6. The ranger module and the display take 3 to 5 V and shift their own levels."),
    ("SDA, SCL", "neck wires 4 and 5", "display · ranger · through the left rail: motor controller", "30 AWG",
     "One I²C bus for the body: the ranger and the display at the front, the motor controller at the back, the long run inside the left rail with BAT+ and 3V3 and away from the sound lines in the right. The boards' pull-ups in parallel come to a few kΩ: fine at 400 kHz. The ranger's GPIO1 stays unconnected."),
    ("GND (logic)", "display GND", "ranger GND · motor controller logic GND", "the frame", "The display's and the ranger's GND pins are soldered to the axle and the brass stub; the motor controller's to the rear rung."),
    ("M1, M2", "motor controller M1A, M1B, M2A, M2B", "left and right gearmotor tabs", "30 AWG, 30 mm, under the motors",
     "Each motor's two tabs. The right motor faces the other way, so the firmware flips its sign. The stall current at 3.7 V is 0.22 A, so 30 AWG is ample. The cans sit on the grounded rungs: meter each can to its tabs, open."),
    ("SERVO", "neck wire 6", "servo signal lead", "30 AWG, then the servo's own lead, cut to 30 mm", "The servo takes a 3.3 V signal (FEETECH, via Pololu). Its three leads stay under the head."),
    ("LAMP", "neck wire 7", "regulator VDD", "30 AWG", "The controller's pin is both the switch and the dimmer: the regulator wakes above 2.7 V on VDD and draws under 1 mA there, the drone's trick."),
    ("LED−", "LED − pad on the star", "regulator OUT", "the LED's own − lead", "The regulator sinks 350 mA from the LED's cathode to ground, whatever the cell's voltage, while the cell stays 0.12 V above the LED's 2.9 V. Its tab is soldered to the axle, its heatsink."),
    ("BAT+ (head)", "neck wire 1", "controller BAT+ pad", "26 AWG in the neck", "Ten silicone wires in a loose loop beside the servo's horn: they twist, not bend, through the head's 120°."),
    ("GND (head)", "neck wire 2", "controller BAT− pad; from its header GND pin, the beacon − and the 8×8 ranger's GND", "26 AWG in the neck, 30 AWG in the head", "One ground in the head, joined at the controller."),
    ("3V3, SDA, SCL (head)", "controller 3V3, D4, D5", "neck wires 3, 4, 5", "30 AWG", "The bus leaves the head on three wires; nothing on it stays up there."),
    ("BEACON", "controller D3", "100 Ω, then the beacon chip's + lead", "the chip's own enamelled leads", "A warm-white 0805 chip drops about 2.9 V: 100 Ω from 3.3 V gives 4 mA, the satellite's figure."),
    ("3V3 (8×8)", "controller 3V3 pin", "8×8 ranger's supply pin", "30 AWG, 15 mm",
     "Pimoroni's board takes 3 to 6 V on one pin and keeps its sensor and its I²C pull-ups at 3.3 V, so the controller's 3.3 V feeds it directly. About 95 mA while it ranges, 150 at worst; the regulator gives 700."),
    ("SDA2, SCL2", "controller D8, D9", "8×8 ranger SDA, SCL", "30 AWG, 15 mm",
     "A second I²C bus, all inside the head: the 8×8 ranger answers at 0x29, the laser ranger's address, so it gets its own two pins instead of an address change. Its INT pin stays unconnected."),
    ("BCLK, LRCLK, DIN", "controller D7, D6, D10", "amplifier BCLK, LRC, DIN", "30 AWG: neck wires 8, 9, 10, then through the right rail",
     "The voice. The controller sends 16-bit mono sound at 16 kHz as I²S: a 512 kHz bit clock, a 16 kHz word clock and the data. The three run down the neck and through the right rail to the amplifier under the motors, away from the I²C pair in the left rail. The firmware moves its console to the USB port, so D6 and D7 (UART0) are free; at reset the ROM still prints on D6 for a moment, and the amplifier stays quiet because it sees no bit clock."),
    ("SPK+, SPK−", "amplifier + and −", "speaker leads", "the speaker's own 32 AWG leads, under it",
     "A bridged output, 8 Ω: neither lead is ground, so neither touches the frame. About 120 mA from the cell while it speaks at a room's level, 0.4 A on a loud syllable, which the 220 µF at the amplifier covers. GAIN stays open (9 dB) and SD on its board's pull-up, so it plays the mono mix."),
]

# ----------------------------------------------------------------------------- parts: owned items stay off the shopping list
PARTS = [
    ("New for Rev K: four lines, each black as sold", [
        ("1", "USB-C charger with a 5 V boost, black", L["chg_black"], "Adafruit bq25185 board; DigiKey 1528-6106-ND", "$8.95",
         f"One black board does two jobs: it charges the cell over USB-C and makes the servo's 5 V. **Cut the jumper on its back for 500 mA**: a full cell in about {E['charge_h']:.1f} h. It stands behind the cell holder, port up, with its parts and its three status lights facing the holder, so only its black back and the USB-C's metal show. If its green terminal block comes soldered, lift it off: the 5 V comes off the pad under it. It replaces Rev J's blue charger and green boost."),
        ("1", "0.96 inch OLED display, white, I²C, on a black board", L["oled_black"], "Adafruit; DigiKey 1528-1220-ND", "$17.50",
         "The face. The five owned screens sit on blue boards; this one is black with gold pads. 29.2 × 26.7 mm, with two tabs below (31.8 in all); the glass is 26.6 × 19.3. It is glued to the axle by its back. Adafruit's current photos show the black board: if a blue one arrives, send it back."),
        ("1 (a 2-pack)", "laser ranger, 4 m, black, with a cover", L["tof_black"], "AITRIP VL53L1X module; Amazon", "$17.99 for two",
         f"The desk-edge eye: 25 × 10.7 × 3.2 mm (listing), 3 to 5 V, its own level shifting. Its GND pin is soldered to a 1 mm brass stub on the axle, left of the screen, tilted {D['tof_tilt']:.0f}° down. **XSHUT goes to its VIN through 10 kΩ**; GPIO1 stays open. Check it answers at 0x29 on the bench. If it has a power light, lift the light off. The second module goes to the shared bin."),
        ("1", "8×8 laser ranger, 4 m, 63°, black", L["tof8_black"], "Pimoroni VL53L5CX breakout; SB Components (UK), in stock 2026-11-10", "$33.00 + shipping",
         "The room eye. It is black, with its parts on the back so the face is flat: 19 × 19 × 4.6 mm, 3 to 6 V, address 0x29, 2 cm to 4 m, about 95 mA while ranging. Pimoroni, DigiKey and The Pi Hut were sold out on 2026-11-10. The drone's green 8×8 stays the drone's spare."),
    ]),
    ("In your Amazon cart from Rev J: four lines to keep, two to delete", [
        ("1", "controller with camera and microphone, ESP32-S3", L["xiao"], "Seeed XIAO ESP32-S3 Sense; in the cart", "$25.99",
         "The head, black: camera, Wi-Fi, a digital microphone and the brain in one 21 × 17.8 × 15 mm stack. It lies on its side on a brass cradle on the servo's horn, camera forward, its USB-C open on the head's left end. Flash it once on the bench; updates come over Wi-Fi. Its stick-on antenna goes flat on the stack's back. Keep its SD slot empty."),
        ("1 pack", "1.0 mm round brass rod, 300 mm, 5 rods", L["rod10"], "K&S; in the cart", "$9.03",
         f"The planks' face rods, the head's cradle and the stubs that hold the ranger and the lamp: {D['rod1_mm'] / 1000:.1f} m, about {math.ceil(D['rod1_mm'] / 280)} rods with the offcuts. Fifteen are owned and about eight spare, so one pack makes enough."),
        ("2 packs of 3", "round brass tube, 3/32 in, 0.014 in wall, 12 in", L["tube332"], "K&S; in the cart", "$8.05 a pack",
         f"The planks' pins: {2 * D['planks']} pieces of {D['pin_l']:.1f} mm, {math.floor(304.8 / (D['pin_l'] + 0.5))} to a tube. Each sits in a drum's seat 0.12 mm loose; the loops wrap its ends."),
        ("1 spool", "24-gauge nickel-silver wire, dead soft, 25 ft", L["nickel"], "CRAFT WIRE; in the cart", "$24.99",
         f"The tread's {D['loops']} loops, {D['wire_m']:.1f} m. The owned 20 gauge would hang below the tread's face and drag; 24 gauge stays a quarter of a millimetre clear."),
        ("delete", "brass sheet, 0.005 in, 6-pack", L["sheet"], "K&S; in the cart", "$24.81",
         "**Delete it before checkout.** It was for Rev J's ivory skins, which the no-paint, no-cover rule took away."),
        ("delete", "M3 × 25 hex-socket screws, 20", L["m3x25"], "uxcell; in the cart", "$7.39",
         "**Delete it before checkout.** The idler drums now turn on the brass axle, so they need no screws."),
    ]),
    ("Ordered for Rev J and still in the build", [
        ("10", f"aluminium drum half, laser cut: {DRUM.Z} seats, {2 * DRUM.R_TIP:.0f} mm, 3/8 in 6061", L["drum"], "SendCutSend order SJ983673, ordered 2026-11-09", "$42.10 for ten",
         f"The four wheels, two halves each, glued face to face: {D['drum_w']:.1f} mm wide, {D['drum_od']:.1f} mm over the teeth, bare aluminium all over now (no paint). The two drive drums are glued on brass hubs on the motors' shafts. The two idlers have no hub: they turn on the 4 mm axle itself, their 4.1 mm holes 0.05 mm loose, between two brass collars. Run a round needle file through each seat and each hole; two halves are spares."),
        ("2", "micro metal gearmotor, 150:1, low power, 6 V", L["motor"], "Pololu; DigiKey order 102785005, shipped 2026-11-09", "$23.95 each",
         f"The drive. About {E['rpm']:.0f} rpm on the cell: {E['speed'] / 10:.1f} cm/s on the desk. Steel cans and gearboxes, their own colour. They sit on the two rungs, the cell holder on top of them."),
        ("1", "motor controller, two channels, I²C", L["motoron"], "Pololu; DigiKey order 102785005", "$15.95",
         "Its board is blue, and no black two-channel controller this small takes I²C. So it hangs under the motors, parts down, glued to the rungs with its GND soldered to one: out of sight. It runs the motors from 1.8 V, stops them if the controller goes quiet, and reads the cell."),
        ("1", "sub-micro servo, 120°", L["servo"], "Pololu; DigiKey order 102785005", "$10.21",
         "Its case is translucent blue, so it stands where nothing sees it: on the two rails, between the axle and the back bar, under the head and behind the screen. Its white horn carries the head. It runs on the charger's 5 V."),
    ]),
    ("Ordered for Rev J, left out of Rev K: to the shared bin", [
        ("1", "USB-C Li-ion charger, 500 mA (blue)", L["charger"], "Adafruit; DigiKey order 102785006", "$5.95", "Replaced by the black charger with its own boost. Unopened, DigiKey may take it back."),
        ("1", "5 V boost regulator (green)", L["boost"], "Pololu; DigiKey order 102785005", "$8.95", "The black charger makes the servo's 5 V now."),
        ("1", "laser ranger, 4 m (green)", L["ranger"], "Pololu; DigiKey order 102785005", "$22.95", "Replaced by the black module. Crumb's edge ranger is the same green board, so it may go there."),
    ]),
    ("Owned: power, switch and sound", [
        ("1 of 13", "16340 cell, 950 mAh, protected, button top", L["cell"], "Nitecore NL169, IMR Batteries 2026-10-16", "owned",
         "16.6 × 34.1 mm, 20 g, 2 A protection. Its wrap is black with yellow bands and print: it lies in the holder with its print face down, like a rover's RTG across the rear deck."),
        ("1 of 10", "16340 holder with leads", L["holder"], "ACEIRMC, Amazon 2026-10-27", "owned", "43 × 18 × 14 mm, black, glued across the two motor cans. Its leads run down its back, behind the charger, to a JST-PH pigtail."),
        ("1 of 20 pairs", "JST-PH 2.0 mm pigtail", L["pigtail"], "daier set, Amazon 2026-09-02", "owned", "Into the charger's socket, between the charger and the holder, out of sight. **Meter its polarity, not its colours.**"),
        ("1 of 20", "toggle switch, on-on", L["toggle"], "Ferwooh MTS-102, Amazon 2026-10-27", "owned",
         "Its body is blue and no black one turned up (the black-looking candidate at DigiKey is red), so it stands on the two rails across the rover, its back to the holder and the speaker in front of it: the screen hides it from the front, the holder from behind, the rear drums from the sides; its chrome top and lever show. Lever to the rover's right is on. Wired so off grounds the rover's supply."),
        ("1 of 6", "enclosed speaker, 8 Ω, 0.8 W", L["speaker"], "Same Sky, DigiKey 2026-09-02", "owned",
         "The voice. Black, 20 × 13 × 4.9 mm, a sealed back, firing from its face. It lies on the two rails behind the head, firing up; its leads run under it to the amplifier."),
        ("1 of 12", "I²S class-D amplifier, 3 W", L["amp"], "HiLetgo MAX98357A, Amazon", "owned",
         "Purple, 19 × 16 mm, so it hangs under the motors beside the motor controller, parts down, out of sight. VIN from the cell after the switch, with a 220 µF beside it; GAIN open (9 dB); SD on its own pull-up, so it plays the mono mix."),
    ]),
    ("Owned: face and head", [
        ("1 of 4", "cool-white LED on a 20 mm star", L["star"], "Cree XP-G2 Indus Star, the drone's pack", "owned", "Sawn to a 14 mm disc as the drone's (solder the leads first). Bare aluminium. 139 lm at 350 mA."),
        ("1 of 2", "10 mm narrow-spot lens", L["lens"], "Carclo, the drone's DigiKey order", "owned", "Clear, glued over the LED; the star is glued to a 1 mm brass bracket on the axle, right of the screen, so the lens comes flush with the glass."),
        ("1 of 10", "350 mA LED regulator", L["amc"], "AMC7135, the drone's pack (arriving 2026-11-17 to 11-20)", "owned", "Black, behind the star: its tab (GND) soldered straight to the axle, which is its heatsink, OUT on the LED's − lead, VDD on the LAMP wire. Read the datasheet's top view before soldering."),
        ("1 of 20", "pre-wired warm-white LED chip, 0805", L["chip"], "DiCUNO 20-pack, the satellite's", "owned", "The beacon, glued flat on the camera board's top edge."),
    ]),
    ("Owned: frame, treads and bench stock", [
        (f"{TUBE['three']:.0f} mm", "brass tube, 3 mm, 0.5 mm wall", L["brass_tube"], "M METERXITY 2 to 7 mm sets (three 200 mm sets on hand, more arriving)", "owned",
         f"The frame: two rails {TUBE['rail']:.0f} mm, two rungs {TUBE['rung']:.0f} mm, the back bar {TUBE['bar']:.0f} mm. Cut with the jeweller's saw, ends filed square. {LAPS} laps, soldered with the Harris flux and rinsed."),
        (f"{TUBE['axle'] + 2 * D['hub_l']:.0f} mm", "brass tube, 4 mm, 0.5 mm wall", L["brass_tube"], "the same sets", "owned",
         f"The front axle, {TUBE['axle']:.1f} mm, and the two drive hubs, {D['hub_l']:.1f} mm each (crimped on the motors' flats over {D['shaft_grip']:.0f} mm of shaft)."),
        (f"{4 * D['collar_l']:.0f} mm", "brass tube, 5 mm, 0.5 mm wall", L["brass_tube"], "the same sets", "owned",
         f"Four collars, {D['collar_l']:.0f} mm each, on the axle either side of each idler drum: the inner ones soldered before the drum goes on, the outer ones glued after."),
        ("1 + 1 + 2 + 1", "100 Ω; 100 µF; 220 µF; 10 kΩ", L["resistors"], "LuminologyPro resistor kit, ALLECIN electrolytic kit", "owned", "100 Ω for the beacon; 100 µF at the motor controller's VIN; 220 µF at the lamp and the servo, and one at the amplifier; 10 kΩ on the ranger's XSHUT."),
        ("about 0.8 m", "26 and 30 AWG silicone wire, black", L["wire30"], "TUOFENG 26 AWG, CBAZY 30 AWG", "owned", "26 AWG for BAT+, 30 AWG for the rest. Black only: most runs go inside the two rails, the rest under parts."),
        ("", "Kapton tape, heat-shrink, solder, Harris flux, baking soda, alcohol", L["kapton"], "bench stock", "owned", "Kapton and heat-shrink as insulation only (joints, and wherever a wire crosses a tube), never as a colour cover. 63/37 and the Harris flux for the treads and the frame, rinsed with baking soda and alcohol before any board goes on."),
    ]),
]

DECISIONS = [
    ("A brass spine, the boards on it",
     f"No box and no paint. Two brass treads carry a frame of six straight brass tubes, lapped and soldered: two 3 mm rails down the middle (the spine), two rungs under the motors, a short back bar, and a 4 mm axle across the front that the idler drums turn on. No bends, {LAPS} laps. "
     f"The servo stands on the rails between the axle and the back bar; the head turns on it; the screen, the laser ranger and the flashlight hang on the axle. {D['width']:.0f} wide, {D['length']:.0f} long, {D['height']:.0f} mm tall, about {D['mass']:.0f} g. You drive it from a phone over Wi-Fi, watch through its camera and talk to it."),
    ("The frame carries the wires and the ground",
     "The rails are tubes with open ends, so the long runs go inside them: BAT+ and the I²C bus in the left rail, the three sound lines and the servo's 5 V in the right. The frame is ground, as in a circuit sculpture: each board's GND is soldered to the nearest tube. Brass takes solder far more easily than Rev J's stainless did."),
    ("Treads you solder, like the reference's",
     f"Huy Vector's treads are links of short rods soldered side by side and tied with thread round grooved drums. Ours: each plank is a 3/32 in [brass tube]({L['tube332']}) with two 1 mm brass rods soldered under it, side by side on the tread face. The tube is {2 * D['pin_out']:.0f} mm longer; its ends are the hinge pins. "
     f"A loop of 24-gauge nickel silver joins each pair of neighbouring pins. {D['planks']} planks a track, {D['plank_p']:.1f} mm apart, {D['loops']} loops in all."),
    ("Laser-cut drums, bare",
     f"Four drums of two 3/8 in 6061 halves each, cut on [SendCutSend's laser]({L['drum']}) and already ordered: {D['drum_w']:.1f} mm wide, {D['gear_n']} round seats, {D['drum_od']:.1f} mm over the teeth. No paint: bare aluminium against the brass. "
     f"The drive drums are glued on {D['hub_l']:.0f} mm brass hubs crimped on the [gearmotors']({L['motor']}) flats. The idlers turn on the brass axle itself between two collars, so the two idler screws are gone."),
    ("No paint, no skins: every part in its own colour",
     "Your rule of 2026-11-09. Every part that shows was read off its maker's photos. Black where black exists: the camera board, the screen's board, both laser rangers, the charger, the cell holder and the speaker; the drone's green 8×8 and Rev J's blue charger, green boost and green ranger give way to black ones. "
     "What only comes in another colour sits where nothing sees it: the blue motor controller and the purple amplifier hang under the motors, the translucent-blue servo stands under the head and behind the screen, and the switch's blue body stands between the holder and the speaker, behind the screen. The cell's yellow print faces down. Lights stay white: the charger's status lights face the holder, and the ranger's power light comes off."),
    ("Brass, aluminium and black",
     "Brass treads and frame; bare aluminium drums; steel motor cans; black head, screen, rangers, charger, holder and speaker. White text on the screen, a white flashlight, one warm beacon. No green, blue, red or purple in sight, no card, no sheet, no paint, nothing printed. Prototype, not product: the head pulls off its horn, the firmware updates over the air."),
    ("A camera, a microphone and an 8×8 ranger in the head",
     f"The [controller board]({L['xiao']}) is the head: one 21 × 17.8 × 15 mm stack with the camera and a digital microphone, its boards black. Pimoroni's black [8×8 laser ranger]({L['tof8_black']}) stands beside it: two eyes on a black face {HD['sh_x1'] - HD['sh_x0']:.0f} mm wide. "
     "Both sit on a cradle of two 1 mm brass rods on the servo's horn, lifted 1.5 mm so the head turns clear of the taller screen. Ten silicone wires join the head to the frame in a loose loop: they twist rather than bend through its 120°."),
    ("A voice: the owned speaker and amplifier",
     f"The microphone is on the camera board already. The voice is a spare [enclosed speaker]({L['speaker']}), black, lying on the spine behind the head and firing up, driven by a spare [I²S amplifier]({L['amp']}) hung under the motors. The controller sends it sound on three pins (D6, D7, D10), down three more neck wires and through the right rail. "
     f"It draws about {E['talk']:.0f} mA while it speaks, so the treads wait while it talks (and while it listens, because their patter fills the microphone). Nothing to buy."),
    ("A motor controller on the same two wires",
     f"The [motor controller]({L['motoron']}) runs motors from 1.8 V, so one cell drives it directly. It takes speed commands over I²C, stops both tracks if the commands stop (a 200 ms timeout), ramps acceleration, and reports the cell's voltage. Its board is blue, so it hangs under the motors."),
    ("The head turns on a servo on the spine",
     f"The [servo]({L['servo']}) stands shaft up on the two rails, glued between the axle in front and the back bar behind. The head's cradle sits on its horn: 120° on the datasheet's pulses, about 180° on wider ones. It is rated 4.8 to 6 V, so it runs on the black charger's 5 V boost, which the switch turns off with everything else."),
    ("The laser ranger is the rover's hazard eye",
     f"The black [ranger]({L['tof_black']}) hangs on a brass stub on the axle, left of the screen, tilted {D['tof_tilt']:.0f}° down. Its centre ray meets the desk {D['tof_reach'] / 10:.1f} cm in front of the rover, {D['tof_slant'] / 10:.1f} cm away: past its 4 cm minimum, about half a second ahead at full speed. When the desk disappears ahead, the tracks stop. "
     "It is the only sensor that sees a drop, so reversing is limited to 2 cm."),
    ("An 8×8 ranger in the head, for the room",
     f"It reads 64 distances at once over a 45° square, 2 cm to 4 m. The head's 120° turn sweeps it, so one sweep sees about 165° ahead: walls, chair legs, the far side of the desk. The frames go to the desktop with the pictures, and the desktop builds a rough map of the room. It draws about {E['tof8']:.0f} mA while it ranges and sleeps when the rover is parked."),
    ("The drone's flashlight, as a headlight",
     f"The same [cool-white LED]({L['star']}) on a star sawn to 14 mm, the same [10 mm lens]({L['lens']}), and one [350 mA regulator]({L['amc']}) whose supply pin is the controller's pin D1: on, off and dimming with no MOSFET. Its tab is soldered to the brass axle, a better heatsink than Rev J's heat-shrink. About 140 lm in a 23° spot, right of the screen, pointing straight ahead; capped at 50 % in firmware."),
    ("A beacon that blinks on the roof",
     f"The satellite's [pre-wired warm-white chip]({L['chip']}), glued flat on the head's roof, 100 ms every 2 s through 100 Ω. It says the rover is on, and it turns with the head."),
    ("One cell, where the RTG goes",
     f"The owned [16340 cell]({L['cell']}) in its black [holder]({L['holder']}) lies across the rear deck on the two motor cans. Behind it stands the [black charger]({L['chg_black']}), port up; in front, the owned [toggle]({L['toggle']}), lever to the right for on. Plug in with the switch off: about {E['charge_h']:.1f} h to full. "
     f"Off grounds the rover's supply, which also turns off the charger's 5 V boost, so nothing drains the cell. About {E['explore_h']:.1f} h exploring with the camera streaming, {E['night_h']:.1f} h with the flashlight on, {E['talking_h']:.1f} h stopped and talking, {E['parked_h']:.1f} h parked and watching."),
    ("A reference, not a copy",
     "Huy Vector's spy tank is a copper-wire box on hand-soldered metal treads, with three cells, a toy RC receiver, an analog FPV camera and two LED headlights on a resistor. This one keeps the idea: a palm-sized tracked chassis on a metal frame, treads of soldered rods, a camera, a light, a 16340 and USB-C charging. "
     "Everything else is its own: a wide little tank on a brass spine with a low turning head that sees, hears and speaks, laser-cut drums of two halves, metal loops instead of thread, Wi-Fi to a phone, a laser ranger that keeps it on the desk, one cell instead of three, brass and black instead of copper."),
]

FIRMWARE = [
    "ESP-IDF 6.0.2 for the esp32s3, the family's toolchain. The `esp32-camera` component streams JPEG to a page served by the controller; the phone's browser shows the picture, a drive pad, a head slider, the lamp, and a Scan button.",
    "I²C at 400 kHz: ST's driver for the ranger (short mode, 50 Hz), the display through `esp_lcd`'s driver for its chip, and the motor controller's protocol from Pololu's user's guide: command timeout 200 ms, a gentle acceleration limit, speeds as signed numbers, the cell's voltage read once a second.",
    "A second I²C bus on D8 and D9 at 1 MHz for the 8×8 ranger: ST's ULD driver loads its firmware at boot, then 8 × 8 zones at 15 Hz while exploring, asleep when parked. Each frame carries the head's angle, so a sweep from −60° to +60° sees about 165° ahead; the frames stream to the desktop with the pictures, and the desktop builds a rough map of the room and sends back where to go.",
    "LEDC: the servo on D0 at 50 Hz (900 to 2100 µs, the head's 120°), down neck wire 6; the lamp on D1, a few kHz, set on the bench so the picture shows no banding, duty capped at 50 %; the beacon on D3, 100 ms every 2 s.",
    "Safety, in this order: the ranger reading the desk ahead every 20 ms while the tracks move forward, stopping and backing 2 cm when the reading jumps past the desk's distance; the 8×8 ranger's middle rows stopping it for anything within 10 cm ahead; reverse limited to 2 cm; the motor controller's own timeout; the cell below 3.4 V parks everything but the beacon.",
    "Sound, Rev K: the Sense board's microphone on I²S0 as PDM (clock GPIO42, data GPIO41), 16 kHz; the amplifier on I²S1, 16 kHz 16-bit mono out on D7 (bit clock), D6 (word clock) and D10 (data). The console moves to the USB Serial/JTAG port so UART0's two pins are free. The treads stop while it listens (their patter fills the microphone) and while it speaks (the current). The desktop that already runs the Pocket AI's server can be its voice: microphone frames up the Wi-Fi, speech back down.",
    "The screen: the distance ahead as a bar, the cell's percentage, the Wi-Fi name and address, and a line of text from the phone.",
    "Over-the-air updates after the first flash on the bench. The servo's 5 V comes on with the switch; the firmware waits half a second after boot before it moves the head, because the charger's boost will not start under a heavy load.",
]

CHECKS = [
    "Polarity, once: the holder's pigtail plug against the charger's socket with the cell in, button top to the pin the board marks +, before the plug goes in.",
    "Supply, once: switch on, the head not yet connected, the cell's voltage between neck wires 1 and 2 at their free ends, and 5.0 V on the charger's 5V pad before the servo's red lead goes on it; switch off, both read 0.",
    "The frame is ground: with the cell out, the frame to GND reads 0 Ω and the frame to BAT+ is open. Nothing but grounds touches a tube bare: BAT+ and every signal stay in silicone, inside the rails and out, and each rail's two open ends are filed smooth before the wires go in.",
    "Isolation, once: each motor's can to each of its two tabs reads open, because the cans sit on the grounded rungs; and each speaker lead to the frame reads open, because the amplifier's outputs are bridged.",
]


# ----------------------------------------------------------------------------- drawing helpers
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def dot(x, y, r=6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="joint"/>'


class Router(_Router):
    """The Pocket AI hop router plus a pin registry and the clearance check."""

    def __init__(self):
        super().__init__()
        self.pins = []

    def pin(self, x, y, net):
        self.pins.append((x, y, net))

    def check(self, min_pin=14, min_lane=14):
        bad = []
        for (x0, y0, x1, y1, n) in self.segs:
            for (px, py, pn) in self.pins:
                if pn == n:
                    continue
                if abs(x0 - x1) < 0.01 and min(y0, y1) - 2 <= py <= max(y0, y1) + 2 and abs(px - x0) < min_pin:
                    bad.append(f"vertical {n} at x={x0} passes {abs(px-x0):.0f}px from pin ({px},{py}) of {pn}")
                if abs(y0 - y1) < 0.01 and min(x0, x1) - 2 <= px <= max(x0, x1) + 2 and abs(py - y0) < min_pin:
                    bad.append(f"horizontal {n} at y={y0} passes {abs(py-y0):.0f}px from pin ({px},{py}) of {pn}")
        crossings = 0
        for i, (x0, y0, x1, y1, n) in enumerate(self.segs):
            for (a0, b0, a1, b1, m) in self.segs[:i]:
                if m == n:
                    continue
                v1, v2 = abs(x0 - x1) < 0.01, abs(a0 - a1) < 0.01
                if v1 and v2 and abs(x0 - a0) < min_lane and min(y0, y1) < max(b0, b1) and max(y0, y1) > min(b0, b1):
                    bad.append(f"verticals {n} x={x0} and {m} x={a0} run {abs(x0-a0):.0f}px apart")
                if (not v1) and (not v2) and abs(y0 - b0) < min_lane and min(x0, x1) < max(a0, a1) and max(x0, x1) > min(a0, a1):
                    bad.append(f"horizontals {n} y={y0} and {m} y={b0} run {abs(y0-b0):.0f}px apart")
                if v1 != v2:
                    vx, vy0, vy1, hx0, hx1, hy_ = (x0, y0, y1, a0, a1, b0) if v1 else (a0, b0, b1, x0, x1, y0)
                    if min(hx0, hx1) + 0.5 < vx < max(hx0, hx1) - 0.5 and min(vy0, vy1) + 0.5 < hy_ < max(vy0, vy1) - 0.5:
                        crossings += 1
        return bad, crossings


def block(x, y, w, h, title, sub=None, cls="part", ty=24):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>', T(x + w / 2, y + ty, title, "title", "middle")]
    if sub:
        o.append(T(x + w / 2, y + ty + 18, sub, "sub", "middle"))
    return "".join(o)


def pin(rt, x, y, name, side, net, fn=None, fnx=None):
    rt.pin(x, y, net)
    o = [f'<circle cx="{x}" cy="{y}" r="4.5" class="pinend"/>']
    if side == "R":
        o.append(T(x - 10, y + 5, name, "pin", "end"))
        if fn:
            o.append(T(fnx, y + 5, fn, "fn", "end"))
    elif side == "L":
        o.append(T(x + 10, y + 5, name, "pin", "start"))
        if fn:
            o.append(T(fnx, y + 5, fn, "fn", "start"))
    elif side == "B":   # pin on a bottom edge: name written upward, just inside the block
        o.append(T(x + 4, y - 10, name, "pin", "start", f'transform="rotate(-90 {x + 4} {y - 10})"'))
    elif side == "T":   # pin on a top edge: name written downward, just inside
        o.append(T(x + 4, y + 10, name, "pin", "end", f'transform="rotate(-90 {x + 4} {y + 10})"'))
    return "".join(o)


def zigzag_h(rt, x0, x1, y, net):
    mid = (x0 + x1) / 2
    z = 7
    pts = [(x0, y), (mid - 14, y)]
    for i, dy in enumerate((z, -z, z, -z, z, -z)):
        pts.append((mid - 14 + (i + 0.5) * (28 / 6), y + dy))
    pts += [(mid + 14, y), (x1, y)]
    return rt.wire(pts, "thin", net)


def zigzag_v(rt, x, y0, y1, net):
    """A resistor standing in a vertical wire, from y0 to y1."""
    mid = (y0 + y1) / 2
    z = 7
    d = -1 if y1 < y0 else 1
    pts = [(x, y0), (x, mid - d * 14)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        pts.append((x + dx, mid - d * 14 + d * (i + 0.5) * (28 / 6)))
    pts += [(x, mid + d * 14), (x, y1)]
    return rt.wire(pts, "thin", net)


def cap_v(x, y0, y1, label, polar=True):
    """Capacitor standing between two horizontal lanes at y0 (top, +) and y1 (bottom): two short plates; not a wire."""
    ym = (y0 + y1) / 2
    o = [f'<path d="M{x},{y0} L{x},{ym - 5} M{x},{ym + 5} L{x},{y1}" class="thin"/>',
         f'<path d="M{x - 11},{ym - 5} L{x + 11},{ym - 5}" class="thin"/>',
         f'<path d="M{x - 11},{ym + 5} Q{x},{ym + 1} {x + 11},{ym + 5}" class="thin"/>' if polar else f'<path d="M{x - 11},{ym + 5} L{x + 11},{ym + 5}" class="thin"/>']
    if polar:
        o.append(T(x + 13, ym - 8, "+", "fn"))
    o.append(T(x + 16, ym + 5, label, "lab"))
    return "".join(o)


def dim_h(x0, x1, y, label, above=True, cls="dim", lcls="dimlab"):
    o = [f'<path d="M{x0},{y-6} L{x0},{y+6} M{x1},{y-6} L{x1},{y+6} M{x0},{y} L{x1},{y}" class="{cls}"/>']
    o.append(T((x0 + x1) / 2, y - 5 if above else y + 15, label, lcls, "middle"))
    return "".join(o)


def dim_v(x, y0, y1, label, right=True, cls="dim"):
    o = [f'<path d="M{x-6},{y0} L{x+6},{y0} M{x-6},{y1} L{x+6},{y1} M{x},{y0} L{x},{y1}" class="{cls}"/>']
    ym = (y0 + y1) / 2
    o.append(T(x + 8 if right else x - 8, ym + 4, label, "dimlab", "start" if right else "end"))
    return "".join(o)


def leader(x0, y0, x1, y1):
    return f'<path d="M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}" class="dim"/>'


def rect(x0, y0, x1, y1, cls, rx=0):
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    return f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{xb - xa:.1f}" height="{yb - ya:.1f}" rx="{rx}" class="{cls}"/>'


def poly(pts, cls):
    return '<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" class="{cls}"/>'


# The rover's own palette: brass, steel and ivory (both themes; greys in print). Brass for the treads
# and cradle; nickel silver for the loops; white heat-shrink and amber Kapton skins; black for the boards, glass and holder;
# amber Kapton over the cell; a warm white for the lights.
RV_LIGHT = ("--rv-ivory:#EFE8D6;--rv-ivory-lo:#8F8672;--rv-steel:#C3C8CD;--rv-steel-lo:#6B7178;"
            "--rv-brass:#C9A24F;--rv-brass-lo:#7A5A22;--rv-ni:#9AA1A8;--rv-card:#FBFAF7;--rv-card-lo:#7E848A;"
            "--rv-black:#1E1F22;--rv-black-lo:#55585E;--rv-kapton:#D9A441;--rv-kapton-lo:#8F6114;--rv-warm:#F4DC9C")
RV_DARK = ("--rv-ivory:#E9E1CD;--rv-ivory-lo:#B9AF97;--rv-steel:#B4BAC0;--rv-steel-lo:#E3E7EB;"
           "--rv-brass:#D2AA58;--rv-brass-lo:#F0D59A;--rv-ni:#B8BEC4;--rv-card:#ECEAE6;--rv-card-lo:#9BA3AC;"
           "--rv-black:#0E0F11;--rv-black-lo:#8D939A;--rv-kapton:#C8902F;--rv-kapton-lo:#F0C77A;--rv-warm:#F4DC9C")
RV_PRINT = ("html:root{--rv-ivory:#fff;--rv-ivory-lo:#000;--rv-steel:#bbb;--rv-steel-lo:#000;--rv-brass:#d9d9d9;--rv-brass-lo:#000;--rv-ni:#555;--rv-card:#fff;--rv-card-lo:#000;"
            "--rv-black:#333;--rv-black-lo:#000;--rv-kapton:#bdbdbd;--rv-kapton-lo:#000;--rv-warm:#eee}")
RV_CSS = (":root{" + RV_LIGHT + "}@media (prefers-color-scheme:dark){:root:not([data-theme=light]){" + RV_DARK + "}}:root[data-theme=dark]{" + RV_DARK + "}"
          ".ivory{fill:var(--rv-ivory);stroke:var(--rv-ivory-lo);stroke-width:.9}"
          ".gearsteel{fill:var(--rv-steel);stroke:var(--rv-steel-lo);stroke-width:.7;stroke-linejoin:round}"
          ".brass{fill:var(--rv-brass);stroke:var(--rv-brass-lo);stroke-width:.6}"
          ".brassfill{fill:var(--rv-brass);stroke:none}"
          ".brassring{fill:none;stroke:var(--rv-brass)}"
          ".brassln{fill:none;stroke:var(--rv-brass-lo);stroke-linecap:round}"
          ".loop{fill:none;stroke:var(--rv-ni);stroke-linecap:round;stroke-linejoin:round}"
          ".card{fill:var(--rv-card);stroke:var(--rv-card-lo);stroke-width:1.2}"
          ".cardln{fill:none;stroke:var(--rv-card-lo);stroke-width:.9;stroke-dasharray:3 2}"
          ".blk{fill:var(--rv-black);stroke:var(--rv-black-lo);stroke-width:.8}"
          ".kapton{fill:var(--rv-kapton);stroke:var(--rv-kapton-lo);stroke-width:.8}"
          ".warm{fill:var(--rv-warm);stroke:var(--rv-brass-lo);stroke-width:.8}"
          ".glowb{fill:none;stroke:var(--rv-brass);stroke-width:1.2;stroke-dasharray:2 3}")

PAGE_TONES = (":root{--signal:#5A6068;--signal-soft:#ECEAE6;--ok:#8F6114;--ok-soft:#F2E6D2;--warn:#8F6114;--warn-soft:#F2E6D2}"
              "@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--signal:#9BA3AC;--signal-soft:#2A2D33;--ok:#D69A4E;--ok-soft:#3A2C18;--warn:#D69A4E;--warn-soft:#3A2C18}}"
              ":root[data-theme=dark]{--signal:#9BA3AC;--signal-soft:#2A2D33;--ok:#D69A4E;--ok-soft:#3A2C18;--warn:#D69A4E;--warn-soft:#3A2C18}")

SHEET_CSS = ("<style>"
             ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
             ".net{fill:var(--bg);stroke:var(--ink-2);stroke-width:1.4}"
             ".usb{fill:var(--line);stroke:var(--ink-2);stroke-width:1.2}"
             ".title{font:700 16px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".sub{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".h1{font:900 24px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".h2{font:700 15px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".zone{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink-2);letter-spacing:.14em}"
             ".pin{font:700 13px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".lab{font:700 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
             ".dimlab{font:700 11.5px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".mono{font:400 11px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".rod{fill:none;stroke:var(--ink);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
             ".thin{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
             ".dim{fill:none;stroke:var(--ink-2);stroke-width:1}"
             ".joint{fill:var(--ink)}"
             ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
             ".solid{fill:var(--ink)}"
             ".board{fill:var(--rv-black);stroke:var(--rv-black-lo);stroke-width:1}"
             ".dark{fill:var(--rv-black);stroke:none}"
             ".cell{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.2}"
             ".steel{fill:none;stroke:var(--ink-2);stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round}"
             ".tube{fill:var(--rv-brass);stroke:var(--rv-brass-lo);stroke-width:1}"
             ".tubeband{fill:var(--bg);stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:6 4}"
             ".ghost{fill:none;stroke:var(--ink-2);stroke-width:1.1;stroke-dasharray:3 3}"
             ".glass{fill:var(--rv-black);stroke:var(--ink-2);stroke-width:1}"
             ".px{fill:var(--paper)}"
             ".lens{fill:var(--paper);stroke:var(--ink);stroke-width:1.4}"
             ".lamp{fill:var(--rv-warm);stroke:var(--ink);stroke-width:1}"
             ".glow{fill:none;stroke:var(--rv-brass);stroke-width:1.2;stroke-dasharray:2 3}"
             ".beam{fill:none;stroke:var(--ink-2);stroke-width:1.4;stroke-dasharray:6 4}"
             ".desk{fill:none;stroke:var(--ink);stroke-width:1.6}"
             ".hatch{fill:none;stroke:var(--ink-2);stroke-width:.8}"
             ".onblack{font:700 10px 'JetBrains Mono',monospace;fill:var(--paper)}"
             ".screen{font:700 7.5px 'JetBrains Mono',monospace;fill:#F4F2EE}"
             ".edge{fill:none;stroke:var(--ink-2);stroke-width:1}"
             ".lever{stroke:var(--ink);stroke-width:2.4;stroke-linecap:round}"
             ".steelc{fill:none;stroke:var(--ink-2);stroke-width:2.6}"
             ".ghostc{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:2 2}"
             ".dimw{fill:none;stroke:var(--paper);stroke-width:1}"
             ".cavity{fill:var(--bg);stroke:var(--ink-2);stroke-width:.8}"
             ".hidden{fill:var(--paper);stroke:var(--ink-2);stroke-width:1;stroke-dasharray:3 2}"
             ".hl{fill:#F4F2EE;opacity:.9}"
             + RV_CSS + "</style>")


# ----------------------------------------------------------------------------- shared drawing pieces
def plank_ring():
    """The planks round one track, side on, as (z, y, a): the pin rod's centre and the plank's angle (0 on the bottom run,
    turning with the tread). Starts under the drive drum and runs forward along the bottom, one plank to a seat.
    Each straight run is k pitches for an even gear, k and a half for an odd one, so the count closes exactly."""
    r, p, n = D["drum_r"], D["plank_p"], D["gear_n"]
    a_, b_ = D["drive_z"], D["idler_z"]
    run, half = D["pitch"] / p, n / 2
    out = []
    for i in range(D["planks"]):
        u = float(i)
        if u < run - 1e-9:                                  # the bottom run, back to front
            out.append((a_ + u * p, D["axle_y"] - r, 0.0))
        elif u < run + half - 1e-9:                         # round the idler, up its front
            th = (u - run) * 2 * math.pi / n
            out.append((b_ + r * math.sin(th), D["axle_y"] - r * math.cos(th), th))
        elif u < 2 * run + half - 1e-9:                     # the top run, front to back
            out.append((b_ - (u - run - half) * p, D["axle_y"] + r, math.pi))
        else:                                               # round the drive gear, down its back
            th = math.pi + (u - 2 * run - half) * 2 * math.pi / n
            out.append((a_ + r * math.sin(th), D["axle_y"] - r * math.cos(th), th))
    return out


def gear_phase(zc):
    """The angle of a seat on the drum at zc, from the planks that sit on it (any one will do)."""
    for z, y, a in plank_ring():
        if abs(math.hypot(z - zc, y - D["axle_y"]) - D["drum_r"]) < 0.05 and (a not in (0.0, math.pi) or abs(z - zc) < 0.05):
            return a
    return 0.0


def rods_of(z, y, a):
    """A plank's three pieces, side on: the pin tube, then the two rods of the tread face, outward of it."""
    ox, oy = math.sin(a), -math.cos(a)
    tx_, ty_ = math.cos(a), math.sin(a)
    h = D["face_h"]
    return [(z, y), (z + ox * h - tx_ * D["rod1"] / 2, y + oy * h - ty_ * D["rod1"] / 2),
            (z + ox * h + tx_ * D["rod1"] / 2, y + oy * h + ty_ * D["rod1"] / 2)]


def rod_r(k):
    """The radius of a plank's piece k: the pin tube first, then the face rods."""
    return D["pin_d"] / 2 if k == 0 else D["rod1"] / 2


def stadium(p0, p1, r, cls, sw):
    """A loop round two points already on the sheet: straight sides, round ends of radius r."""
    (x0, y0), (x1, y1) = p0, p1
    d = math.hypot(x1 - x0, y1 - y0) or 1e-6
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    nx, ny = -uy, ux
    a0, a1 = (x0 + nx * r, y0 + ny * r), (x1 + nx * r, y1 + ny * r)
    b1, b0 = (x1 - nx * r, y1 - ny * r), (x0 - nx * r, y0 - ny * r)
    return (f'<path d="M{a0[0]:.2f},{a0[1]:.2f} L{a1[0]:.2f},{a1[1]:.2f} A{r:.2f},{r:.2f} 0 0 0 {b1[0]:.2f},{b1[1]:.2f} '
            f'L{b0[0]:.2f},{b0[1]:.2f} A{r:.2f},{r:.2f} 0 0 0 {a0[0]:.2f},{a0[1]:.2f}Z" class="{cls}" stroke-width="{sw:.2f}"/>')


def drum_pts(zc):
    """A drum's edge in the side view's millimetres (z, y): the cutting file's outline, turned so its seats sit under the
    planks on it. The outline's first seat is half a seat round from its x axis; a plank at angle a lies at a - 90°."""
    th = gear_phase(zc) - math.pi / 2 - math.pi / D["gear_n"]
    c, s_ = math.cos(th), math.sin(th)
    return [(zc + x * c - y * s_, D["axle_y"] + x * s_ + y * c) for x, y in WHEEL]


def drum_side(X, Y, s, zc):
    """One aluminium drum, side on, bare all over (Rev K: no paint), the brass hub on the motor's shaft or the brass axle
    through the idler. The pin tubes sit in its seats."""
    cx, cy = X(zc), Y(D["axle_y"])
    o = ['<path d="M' + " L".join(f"{X(z):.1f},{Y(y):.1f}" for z, y in drum_pts(zc)) + 'Z" class="gearsteel"/>']
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{(D["drum_rf"] - 0.6) * s:.1f}" class="edge"/>')
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{D["hub_d"] / 2 * s:.1f}" class="brass"/>')
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{D["hub_id"] / 2 * s:.1f}" class="blk"/>')
    return "".join(o)


def plank_side(X, Y, s, z, y, a):
    """One plank end on: the pin tube with two rods under it, the solder between them."""
    rods = rods_of(z, y, a)
    pts = " ".join(f"{X(pz):.2f},{Y(py):.2f}" for pz, py in rods)
    o = [f'<polygon points="{pts}" class="brassfill"/>']
    o += [f'<circle cx="{X(pz):.2f}" cy="{Y(py):.2f}" r="{rod_r(k) * s:.2f}" class="brass"/>' for k, (pz, py) in enumerate(rods)]
    o.append(f'<circle cx="{X(rods[0][0]):.2f}" cy="{Y(rods[0][1]):.2f}" r="{(D["pin_d"] / 2 - D["pin_wall"]) * s:.2f}" class="blk"/>')
    return "".join(o)


def track_side(X, Y, s):
    """One track side on: the two drums, the planks round them, and the near loops of nickel silver on the pin tubes."""
    ring = plank_ring()
    o = [drum_side(X, Y, s, D["drive_z"]), drum_side(X, Y, s, D["idler_z"])]
    o += [plank_side(X, Y, s, z, y, a) for z, y, a in ring]
    rr = (D["pin_d"] / 2 + 0.05 + D["loop_wire"] / 2) * s
    for i in range(len(ring)):
        o.append(stadium((X(ring[i - 1][0]), Y(ring[i - 1][1])), (X(ring[i][0]), Y(ring[i][1])), rr, "loop", D["loop_wire"] * s * 0.6))
    return "".join(o)


def track_front(FX, Y, s, sg):
    """One track from the front: the planks wrapping the idler, nearest last, and the loops up both edges."""
    o = []
    front = [q for q in plank_ring() if q[0] >= D["idler_z"] - 0.01]
    rods = []
    for z, y, a in front:
        for k, (rz, ry) in enumerate(rods_of(z, y, a)):
            rods.append((rz, ry, k))
    for rz, ry, k in sorted(rods):
        x0, x1 = (D["pin_x0"], D["pin_x1"]) if k == 0 else (D["tr_x0"], D["tr_x1"])
        o.append(rect(FX(sg * x0), Y(ry + rod_r(k)), FX(sg * x1), Y(ry - rod_r(k)), "brass", 0.4 * s))
    ys = [y for _, y, _ in front]
    for xe in (D["tr_x0"] - D["pin_out"] / 2, D["tr_x1"] + D["pin_out"] / 2):
        o.append(f'<line x1="{FX(sg * xe):.1f}" y1="{Y(min(ys)):.1f}" x2="{FX(sg * xe):.1f}" y2="{Y(max(ys)):.1f}" class="loop" stroke-width="{D["loop_wire"] * s:.1f}"/>')
    return "".join(o)


def track_top(TX, TY, s, sg):
    """One track from above: the upper half of the loop, tread face up; the pin rods' ends and their loops at both edges."""
    o = []
    top = [q for q in plank_ring() if q[1] >= D["axle_y"] - 0.01]
    for z, y, a in sorted(top, key=lambda q: q[1]):
        for k, (rz, ry) in enumerate(rods_of(z, y, a)):
            x0, x1 = (D["pin_x0"], D["pin_x1"]) if k == 0 else (D["tr_x0"], D["tr_x1"])
            o.append(rect(TX(sg * x0), TY(rz + rod_r(k)), TX(sg * x1), TY(rz - rod_r(k)), "brass", 0.4 * s))
    zs = [z for z, _, _ in top]
    for xe in (D["tr_x0"] - D["pin_out"] / 2, D["tr_x1"] + D["pin_out"] / 2):
        o.append(f'<line x1="{TX(sg * xe):.1f}" y1="{TY(max(zs)):.1f}" x2="{TX(sg * xe):.1f}" y2="{TY(min(zs)):.1f}" class="loop" stroke-width="{D["loop_wire"] * s:.1f}"/>')
    return "".join(o)


# Rev K: what each part that shows is drawn in. No paint and no skins (builder's rule, 2026-11-09): the colour is the part's own,
# read off its maker's photos. The blue and green boards that have no black version hang under the motors, out of sight.
COL = dict(head="board", tof8="board", oled="board", tof="board", servo="hidden", holder="blk", chg="board", spk="blk", tog="usb")


def tube_end(X, Y, s, z, y, d, bore=True):
    """A brass tube seen end on: its wall, and its bore dark."""
    o = [f'<circle cx="{X(z):.1f}" cy="{Y(y):.1f}" r="{d / 2 * s:.1f}" class="brass"/>']
    if bore:
        o.append(f'<circle cx="{X(z):.1f}" cy="{Y(y):.1f}" r="{(d / 2 - 0.5) * s:.1f}" class="dark"/>')
    return "".join(o)


def tube_run(X, Y, s, a0, a1, b, d):
    """A brass tube seen from the side, running from a0 to a1 at height (or depth) b: a band d wide."""
    return rect(X(a0), Y(b + d / 2), X(a1), Y(b - d / 2), "brass", 0.25 * s)


def head_face(X, Y, s):
    """The head from the front at any scale: the bare camera board (black) and its lens, the 8x8 ranger's black board beside
    it with the sensor in its middle, the beacon on top, the ends of the two brass cradle rods under it."""
    o = []
    xa, xb = sorted((X(hx(HD["x_x0"])), X(hx(HD["x_x1"]))))
    o.append(rect(xa, Y(hy(HD["y1"])), xb, Y(hy(HD["y0"])), COL["head"], 0.6 * s))
    ta, tb = sorted((X(hx(HD["t8_x0"])), X(hx(HD["t8_x1"]))))
    o.append(rect(ta, Y(hy(HD["y0"] + D["t8_h"])), tb, Y(hy(HD["y0"])), COL["tof8"], 0.6 * s))
    cx, cy = X(hx(HD["cam_cx"])), Y(hy(HD["cam_cy"]))
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{3.5 * s:.1f}" class="glass"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{2.6 * s:.1f}" class="glass"/>'
             f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{1.4 * s:.1f}" class="dark"/><circle cx="{cx - 0.8 * s:.1f}" cy="{cy - 0.8 * s:.1f}" r="{0.45 * s:.1f}" class="hl"/>')
    for xr in (-6.0, 6.0):
        o.append(f'<circle cx="{X(hx(xr)):.1f}" cy="{Y(hy(0.75)):.1f}" r="{0.5 * s:.1f}" class="brass"/>')
    tx, ty = X(hx(HD["t8_cx"])), Y(hy(HD["t8_cy"]))                  # the 8x8 sensor's package, its two windows catching the light
    o.append(rect(tx - 3.2 * s, ty - 1.6 * s, tx + 3.2 * s, ty + 1.6 * s, "glass", 0.4 * s))
    for dx in (-1.4, 1.4):
        o.append(f'<circle cx="{tx + dx * s:.1f}" cy="{ty:.1f}" r="{0.45 * s:.1f}" class="hl"/>')
    o.append(f'<circle cx="{X(hx(0.0)):.1f}" cy="{Y(hy(HD["sh_y1"]) + 0.5):.1f}" r="{0.9 * s:.1f}" class="lamp"/>')
    return "".join(o)


def front_face(FX, Y, s):
    """The face from the front: the screen on its black board, the black laser ranger tilted on the left (it looks short),
    the flashlight's bare aluminium star and its lens on the right. Returns the drawing and the glass's middle height."""
    o = [rect(FX(D["oled_w"] / 2), Y(D["oled_top"]), FX(-D["oled_w"] / 2), Y(D["oled_bot"]), COL["oled"], 0.8 * s)]
    gy0 = D["oled_top"] - D["oled_gt"]
    gy1 = gy0 - D["oled_gh"]
    o.append(rect(FX(D["oled_gw"] / 2), Y(gy0), FX(-D["oled_gw"] / 2), Y(gy1), "glass", 0.6 * s))
    th = D["tof_h"] * math.cos(math.radians(D["tof_tilt"]))
    tx, ty = FX(D["tof_x"]), Y(D["tof_cy"])
    o.append(rect(tx - D["tof_w"] / 2 * s, ty - th / 2 * s, tx + D["tof_w"] / 2 * s, ty + th / 2 * s, COL["tof"], 0.8 * s))
    o.append(rect(tx - 2.4 * s, ty - 1.25 * s, tx + 2.4 * s, ty + 1.25 * s, "glass", 0.4 * s))
    for dx in (-1.2, 1.2):
        o.append(f'<circle cx="{tx + dx * s:.1f}" cy="{ty:.1f}" r="{0.45 * s:.1f}" class="hl"/>')
    lx, ly = FX(D["lamp_x"]), Y(D["lamp_cy"])
    o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{D["lamp_d"] / 2 * s:.1f}" class="gearsteel"/>')
    o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{D["lens_d"] / 2 * s:.1f}" class="lens"/>')
    o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{1.7 * s:.1f}" class="lamp"/>')
    return "".join(o), (gy0 + gy1) / 2


def label_l(o, px, py, lx, ly, lines):
    """A label to the left of a part: a leader from the part to the end of the text column."""
    o.append(leader(px, py, lx + 4, ly))
    for i, t in enumerate(lines):
        o.append(T(lx, ly + 4 + i * 13, t, "fn", "end"))


def label_r(o, px, py, lx, ly, lines):
    o.append(leader(px, py, lx - 4, ly))
    for i, t in enumerate(lines):
        o.append(T(lx, ly + 4 + i * 13, t, "fn", "start"))


def screen_side(X, Y, s):
    """The screen side on: its black board against the axle's front, the glass in front of it."""
    gy0 = D["oled_top"] - D["oled_gt"]
    zb = D["face_z"] - 1.6                                       # the board's front face; its parts behind it, the glass in front
    return (rect(X(D["oled_z"] + 1.0), Y(gy0 - 1.0), X(zb - 1.6), Y(gy0 - D["oled_gh"] + 1.0), COL["oled"], 0.3 * s)
            + rect(X(zb - 1.6), Y(D["oled_top"]), X(zb), Y(D["oled_bot"]), COL["oled"], 0.3 * s)
            + rect(X(zb), Y(gy0), X(D["face_z"]), Y(gy0 - D["oled_gh"]), "glass", 0.3 * s))


def body_side(X, Y, s):
    """Everything between the treads, seen from the rover's right, farthest first: the left ranger's edge, the spine and its
    laps, the holder, the black charger behind it, the switch, the speaker on the spine, the servo on the rails, the screen
    on the axle, the lamp."""
    o = []
    th = D["tof_h"] / 2
    a = math.radians(D["tof_tilt"])
    cz, cy = D["tof_z"], D["tof_cy"]
    pts = [(cz - th * math.sin(a) - 1.0, cy + th * math.cos(a)), (cz - th * math.sin(a) + 1.0, cy + th * math.cos(a)),
           (cz + th * math.sin(a) + 1.0, cy - th * math.cos(a)), (cz + th * math.sin(a) - 1.0, cy - th * math.cos(a))]
    o.append(poly([(X(z), Y(y)) for z, y in pts] + [(X(pts[0][0]), Y(pts[0][1]))], "edge"))
    o.append(tube_run(X, Y, s, D["rail_z0"], D["rail_z1"], D["rail_y"], D["tube"]))
    for zr in (D["r1_z"], D["r2_z"]):
        o.append(tube_end(X, Y, s, zr, D["rung_y"], D["tube"]))
    o.append(tube_end(X, Y, s, D["bar_z"], D["bar_y"], D["tube"]))
    o.append(tube_end(X, Y, s, D["idler_z"], D["axle_y"], D["axle_d"]))
    o.append(rect(X(D["holder_z0"]), Y(D["holder_y0"] + D["holder_h"]), X(D["holder_z1"]), Y(D["holder_y0"]), COL["holder"], 1.5))
    o.append(rect(X(D["chg_z0"]), Y(D["chg_y0"] + D["chg_l"]), X(D["chg_z1"]), Y(D["chg_y0"]), COL["chg"], 1))
    o.append(rect(X(D["chg_z0"] + 1.0), Y(D["chg_y0"] + D["chg_l"] + 0.6), X(D["chg_z1"] - 1.0), Y(D["chg_y0"] + D["chg_l"]), "usb", 0.5))
    ttop = D["tog_y0"] + D["tog_h"]
    o.append(rect(X(D["tog_z0"]), Y(ttop), X(D["tog_z1"]), Y(D["tog_y0"]), COL["tog"], 1))
    zl = (D["tog_z0"] + D["tog_z1"]) / 2
    o.append(rect(X(zl - 1.5), Y(ttop + D["tog_bush"] / 2), X(zl + 1.5), Y(ttop), "usb", 0.3))
    o.append(f'<line x1="{X(zl):.1f}" y1="{Y(ttop + D["tog_bush"] / 2):.1f}" x2="{X(zl):.1f}" y2="{Y(ttop + D["tog_lever"]):.1f}" class="lever"/>')
    o.append(rect(X(D["spk_z0"]), Y(D["spk_y0"] + D["spk_h"]), X(D["spk_z1"]), Y(D["spk_y0"]), COL["spk"], 0.8))
    o.append(rect(X(D["piv_z"] - D["srv_w"] / 2), Y(D["srv_top"]), X(D["piv_z"] + D["srv_w"] / 2), Y(D["srv_y0"]), COL["servo"], 1))
    o.append(screen_side(X, Y, s))
    o.append(rect(X(D["lamp_z"]), Y(D["lamp_cy"] + D["lamp_d"] / 2), X(D["lamp_z"] + 1.6), Y(D["lamp_cy"] - D["lamp_d"] / 2), "gearsteel", 0.3))
    o.append(rect(X(D["lamp_z"] + 1.6), Y(D["lamp_cy"] + D["lens_d"] / 2), X(D["face_z"]), Y(D["lamp_cy"] - D["lens_d"] / 2), "lens", 1))
    return "".join(o)


def head_side(X, Y, s):
    """The head side on: the horn on the servo's shaft, the two brass cradle rods, the camera stack, the lens, the beacon."""
    o = [rect(X(D["piv_z"] - 4.0), Y(D["head_floor"]), X(D["piv_z"] + 4.0), Y(D["srv_top"]), "dark", 0.5),
         poly([(X(hz(HD["x_z0"]) + 1.0), Y(hy(0.75))), (X(hz(HD["x_z1"]) - 1.0), Y(hy(0.75)))], "brassln").replace('class="brassln"', f'class="brassln" stroke-width="{D["rod1"] * s:.1f}"'),
         rect(X(hz(HD["x_z0"])), Y(hy(HD["sh_y1"])), X(hz(HD["x_z1"])), Y(hy(HD["y0"])), COL["head"], 1),
         rect(X(hz(HD["x_z1"])), Y(hy(HD["cam_cy"] + 3.0)), X(hz(HD["sh_z1"])), Y(hy(HD["cam_cy"] - 3.0)), "glass", 0.5)]
    bz, by_ = hz(-4.0), hy(HD["sh_y1"]) + 0.5
    o.append(f'<circle cx="{X(bz):.1f}" cy="{Y(by_):.1f}" r="{0.9 * s:.1f}" class="lamp"/><circle cx="{X(bz):.1f}" cy="{Y(by_):.1f}" r="{4.5 * s:.1f}" class="glow"/>')
    return "".join(o), (X(bz), Y(by_))


def neck_side(X, Y, s):
    """The neck: ten silicone wires in a loose loop from the head's back down to the rails' front ends."""
    x0, y0 = X(hz(HD["x_z0"]) + 1.5), Y(hy(HD["y0"]))
    x1, y1 = X(D["bar_z"] - 2.0), Y(D["rail_y"] + D["tube"] / 2 + 1.0)
    return f'<path d="M{x0:.1f},{y0:.1f} C{x0 - 14 * s / 2.7:.1f},{y0 + 6:.1f} {x0 - 16 * s / 2.7:.1f},{Y(D["srv_top"] - 6):.1f} {x1:.1f},{y1:.1f}" class="thin"/>'


def under_boards(X, Y, s):
    """The boards that keep their colour out of sight, hung under the rungs, backs up: dashed, because nothing shows."""
    zc = D["drive_z"]
    return (rect(X(zc - D["mot_w"] / 2), Y(D["under_y1"]), X(zc + D["mot_w"] / 2), Y(D["under_y0"]), "ghost", 0.5)
            + rect(X(zc - D["amp_w"] / 2), Y(D["under_y1"] - 0.3), X(zc + D["amp_w"] / 2), Y(D["under_y0"] + 0.3), "ghost", 0.5))


# ----------------------------------------------------------------------------- sheet 1: the form
def form_sheet():
    o = [T(20, 30, "Mars rover: how the finished thing looks", "h1"),
         T(20, 48, f"A wide little tank on a brass spine: brass treads on bare aluminium drums, six brass tubes, every part in its own colour (brass, aluminium, black), the blue and green boards out of sight. {D['width']:.0f} × {D['length']:.0f} × {D['height']:.0f} mm, about {D['mass']:.0f} g; one scale.", "sub")]
    s = 2.7
    DESK = 430

    # ---------------------------------------------------------------- side view, from the rover's right, front to the right
    x0 = 320
    X = lambda z: x0 + z * s           # noqa: E731
    Y = lambda y: DESK - y * s         # noqa: E731
    o.append(T(20, 84, "Side view, from the rover's right", "h2"))
    o.append(f'<line x1="{X(-D["tr_end"] - 7)}" y1="{DESK}" x2="{X(D["tr_end"] + 11)}" y2="{DESK}" class="desk"/>')
    o.append(body_side(X, Y, s))
    o.append(neck_side(X, Y, s))
    hs, (bx, by) = head_side(X, Y, s)
    o.append(hs)
    o.append(track_side(X, Y, s))
    o.append(tube_end(X, Y, s, D["idler_z"], D["axle_y"], D["collar_d"], bore=False))      # the outer collar on the axle's end
    o.append(tube_end(X, Y, s, D["idler_z"], D["axle_y"], D["axle_d"]))
    o.append(under_boards(X, Y, s))
    fz, ty_ = D["tof_z"], D["tof_y"]
    ang = math.radians(D["tof_tilt"])
    zend = D["tr_end"] + 8.0
    o.append(f'<path d="M{X(fz):.1f},{Y(ty_):.1f} L{X(zend):.1f},{Y(ty_ - (zend - fz) * math.tan(ang)):.1f}" class="beam"/>')
    o.append(f'<path d="M{X(D["head_front"] + 0.5):.1f},{Y(D["cam_y"]):.1f} L{X(zend):.1f},{Y(D["cam_y"]):.1f}" class="ghost"/>')
    o.append(T(X(D["head_front"]) + 6, Y(D["cam_y"]) - 6, "camera", "fn"))
    o.append(T(X(fz) + 4, Y(D["tr_h"] + 1.5), f"ranger, {D['tof_tilt']:.0f}°", "fn"))
    LX = 170
    label_l(o, bx - 3, by, LX, 196, ["beacon, blinking on the head"])
    label_l(o, X(hz(HD["sh_z0"])), Y(hy(9.0)), LX, 222, ["the head: camera, microphone", "and the 8×8 ranger, all black"])
    label_l(o, X((D["tog_z0"] + D["tog_z1"]) / 2), Y(D["tog_y0"] + D["tog_h"] + D["tog_lever"] - 2), LX, 258, ["switch, behind the speaker"])
    label_l(o, X((D["chg_z0"] + D["chg_z1"]) / 2), Y(D["chg_y0"] + D["chg_l"] + 0.3), LX, 282, ["charger, black, behind the cell;", "its USB-C on top"])
    label_l(o, X(-5.0), Y(D["spk_y0"] + D["spk_h"] - 1.0), LX, 318, ["speaker on the spine, firing up"])
    label_l(o, X(D["drive_z"] - D["drum_rf"] * 0.6), Y(D["axle_y"] + D["drum_rf"] * 0.6), LX, 342, ["aluminium drum, bare"])
    label_l(o, X(D["drive_z"] - 6.0), Y(D["under_y0"] + 1.0), LX, 366, ["under the motors, out of sight:", "motor controller, amplifier"])
    label_l(o, X(-14.0), Y(1.2), LX, 408, [f"brass treads: {D['planks']} planks a side,", "nickel-silver loops"])
    o.append(dim_h(X(-D["tr_end"]), X(D["tr_end"]), DESK + 22, f"{2 * D['tr_end']:.0f} tread", False))
    o.append(dim_v(X(D["tr_end"]) + 9, Y(0), Y(D["tr_h"]), f"{D['tr_h']:.0f}", True))
    o.append(dim_v(X(D["tr_end"]) + 27, Y(0), Y(D["height"]), f"{D['height']:.0f}", True))

    # ---------------------------------------------------------------- front view: the rover's right on the viewer's left
    fx0 = 727
    FX = lambda x: fx0 - x * s          # noqa: E731
    o.append(T(577, 84, "Front view", "h2"))
    o.append(T(577, 100, "the rover's right is on your left", "fn"))
    o.append(f'<line x1="{FX(60)}" y1="{DESK}" x2="{FX(-60)}" y2="{DESK}" class="desk"/>')
    o.append(rect(FX(D["holder_l"] / 2), Y(D["holder_y0"] + D["holder_h"]), FX(-D["holder_l"] / 2), Y(D["holder_y0"]), COL["holder"], 1.5))
    o.append(rect(FX(D["axle_x1"]), Y(D["axle_y"] + D["axle_d"] / 2), FX(-D["axle_x1"]), Y(D["axle_y"] - D["axle_d"] / 2), "brass", 0.3 * s))
    for sg in (-1, 1):
        o.append(rect(FX(sg * D["collar_x0"]), Y(D["axle_y"] + D["collar_d"] / 2), FX(sg * (D["collar_x0"] + D["collar_l"])), Y(D["axle_y"] - D["collar_d"] / 2), "brass", 0.3 * s))
    face, wy = front_face(FX, Y, s)
    o.append(face)
    o.append(T(FX(0), Y(wy) - 1, "SOL 7  4.0 V", "screen", "middle"))
    o.append(T(FX(0), Y(wy) + 9, "ahead 12 cm", "screen", "middle"))
    for sg in (-1, 1):
        o.append(track_front(FX, Y, s, sg))
    o.append(rect(FX(4.0), Y(D["head_floor"]), FX(-4.0), Y(D["oled_top"]), "dark", 0.5))
    o.append(head_face(FX, Y, s))
    FL, FR = 562, 890
    label_l(o, FX(D["lamp_x"]) + D["lamp_d"] / 2 * s, Y(D["lamp_cy"]), FL, Y(D["lamp_cy"] + 4), ["flashlight"])
    label_l(o, FX(hx(HD["t8_x1"])) + 2, Y(hy(HD["t8_cy"])), FL, Y(hy(HD["t8_cy"]) + 6), ["8×8 ranger"])
    label_l(o, FX(D["teeth_x"]), Y(D["axle_y"] + D["drum_r"] + 1.0), FL, Y(D["axle_y"] + D["drum_r"] + 15), ["tread"])
    label_l(o, FX(30.0), Y(D["axle_y"]), FL, Y(D["axle_y"] - 4), ["brass axle;", "the drums turn on it"])
    label_r(o, FX(hx(HD["x_x0"])) - 2, Y(hy(HD["cam_cy"])), FR, Y(hy(HD["cam_cy"]) + 6), ["camera"])
    label_r(o, FX(D["tof_x"]) + D["tof_w"] / 2 * s, Y(D["tof_cy"]), FR, Y(D["tof_cy"] + 6), ["ranger"])
    label_r(o, FX(-D["oled_w"] / 2), Y(wy), FR, Y(wy) - 4, ["screen, on a", "black board"])
    label_r(o, FX(-D["holder_l"] / 2) + 2, Y(D["holder_y0"] + D["holder_h"] - 1.0), FR, Y(D["holder_y0"] + D["holder_h"] + 9), ["cell holder"])
    o.append(dim_h(FX(D["pin_x1"]), FX(-D["pin_x1"]), DESK + 22, f"{D['width']:.0f}", False))

    # ---------------------------------------------------------------- top view, front up
    tx0, ty0 = 1140, 248
    TX = lambda x: tx0 + x * s          # noqa: E731
    TY = lambda z: ty0 - z * s          # noqa: E731
    o.append(T(975, 84, "Top view, front up", "h2"))
    for sg in (-1, 1):
        o.append(track_top(TX, TY, s, sg))
    for sg in (-1, 1):                                                   # the motors: steel cans, gearboxes at the drums
        o.append(rect(TX(sg * D["mot_x_in"]), TY(D["mot_z1"]), TX(sg * D["face_x"]), TY(D["mot_z0"]), "gearsteel", 1))
    o.append(rect(TX(-D["axle_x1"]), TY(D["idler_z"] + D["axle_d"] / 2), TX(D["axle_x1"]), TY(D["idler_z"] - D["axle_d"] / 2), "brass", 0.3 * s))
    for sg in (-1, 1):
        o.append(rect(TX(sg * D["rail_x"] - D["tube"] / 2), TY(D["rail_z1"]), TX(sg * D["rail_x"] + D["tube"] / 2), TY(D["rail_z0"]), "brass", 0.3 * s))
    o.append(rect(TX(-D["bar_x"]), TY(D["bar_z"] + D["tube"] / 2), TX(D["bar_x"]), TY(D["bar_z"] - D["tube"] / 2), "brass", 0.3 * s))
    o.append(rect(TX(-D["holder_l"] / 2), TY(D["holder_z1"]), TX(D["holder_l"] / 2), TY(D["holder_z0"]), COL["holder"], 1.5))
    o.append(rect(TX(-D["chg_w"] / 2), TY(D["chg_z1"]), TX(D["chg_w"] / 2), TY(D["chg_z0"]), COL["chg"], 1))
    o.append(rect(TX(-4.5), TY(D["chg_z1"] - 1.0), TX(4.5), TY(D["chg_z0"] + 1.0), "usb", 1))
    o.append(rect(TX(-D["spk_l"] / 2), TY(D["spk_z1"]), TX(D["spk_l"] / 2), TY(D["spk_z0"]), COL["spk"], 1))
    o.append(f'<circle cx="{TX(0):.1f}" cy="{TY((D["spk_z0"] + D["spk_z1"]) / 2):.1f}" r="{4.5 * s:.1f}" class="glass"/>')
    o.append(rect(TX(-D["tog_l"] / 2), TY(D["tog_z1"]), TX(D["tog_l"] / 2), TY(D["tog_z0"]), COL["tog"], 1))
    o.append(f'<circle cx="{TX(0):.1f}" cy="{TY((D["tog_z0"] + D["tog_z1"]) / 2):.1f}" r="{1.6 * s:.1f}" class="usb"/>')
    o.append(rect(TX(-15.2), TY(D["piv_z"] + D["srv_w"] / 2), TX(5.2), TY(D["piv_z"] - D["srv_w"] / 2), COL["servo"], 1))
    o.append(rect(TX(-D["oled_w"] / 2), TY(D["face_z"]), TX(D["oled_w"] / 2), TY(D["oled_z"]), COL["oled"], 0.5))
    o.append(rect(TX(D["tof_x"] - D["tof_w"] / 2), TY(D["tof_z"] + 4.5), TX(D["tof_x"] + D["tof_w"] / 2), TY(D["tof_z"] - 4.5), COL["tof"], 0.5))
    o.append(rect(TX(D["lamp_x"] - D["lamp_d"] / 2), TY(D["lamp_z"] + 1.6), TX(D["lamp_x"] + D["lamp_d"] / 2), TY(D["lamp_z"]), "gearsteel", 0.5))
    o.append(rect(TX(D["lamp_x"] - D["lens_d"] / 2), TY(D["face_z"]), TX(D["lamp_x"] + D["lens_d"] / 2), TY(D["lamp_z"] + 1.6), "lens", 1))
    o.append(rect(TX(hx(HD["x_x0"])), TY(hz(HD["x_z1"])), TX(hx(HD["x_x1"])), TY(hz(HD["x_z0"])), COL["head"], 1.5))
    o.append(rect(TX(hx(HD["t8_x0"])), TY(hz(HD["x_z1"])), TX(hx(HD["t8_x1"])), TY(hz(HD["t8_z0"])), COL["tof8"], 0.5))
    o.append(rect(TX(hx(HD["cam_cx"] - 3.0)), TY(hz(HD["sh_z1"])), TX(hx(HD["cam_cx"] + 3.0)), TY(hz(HD["x_z1"])), "glass", 0.5))
    o.append(f'<circle cx="{TX(hx(0.0)):.1f}" cy="{TY(hz(-4.0)):.1f}" r="{1.0 * s:.1f}" class="lamp"/>')
    RXL = 1302
    label_r(o, TX(hx(HD["sh_x1"])) - 4, TY(hz(4.0)), RXL, TY(hz(14.0)) + 4, ["head"])
    label_r(o, TX(D["pin_x1"]) - 2, TY(D["idler_z"] + 8), RXL, TY(D["idler_z"] + 16), ["tread"])
    label_r(o, TX(D["axle_x1"]) - 1, TY(D["idler_z"]), RXL, TY(D["idler_z"] - 1) + 4, ["axle"])
    label_r(o, TX(D["spk_l"] / 2) - 2, TY((D["spk_z0"] + D["spk_z1"]) / 2 + 3), RXL, TY(2.0) + 4, ["speaker"])
    label_r(o, TX(D["tog_l"] / 2), TY((D["tog_z0"] + D["tog_z1"]) / 2), RXL, TY(D["tog_z0"] + 1.0) + 4, ["switch"])
    label_r(o, TX(D["holder_l"] / 2) - 4, TY(D["drive_z"]), RXL, TY(D["drive_z"]) + 4, ["cell"])
    label_r(o, TX(D["chg_w"] / 2) - 2, TY((D["chg_z0"] + D["chg_z1"]) / 2), RXL, TY(D["chg_z0"] + 1.0) + 4, ["charger"])
    o.append(dim_h(TX(-D["pin_x1"]), TX(D["pin_x1"]), TY(-D["tr_end"]) + 22, f"{D['width']:.0f}", False))
    o.append(dim_v(TX(-D["pin_x1"]) - 10, TY(D["tr_end"]), TY(-D["tr_end"]), f"{D['length']:.0f}", False))

    # ---------------------------------------------------------------- row 2, left: the face and a cut, 3.6 px per mm
    s4 = 3.6
    o.append(T(20, 500, "The face and a cut through the servo, at 3.6 px per mm", "h2"))
    hfx, hfb = 140, 792
    FXf = lambda x: hfx - x * s4                         # noqa: E731
    YF = lambda y: hfb - y * s4                          # noqa: E731
    o.append(rect(FXf(34.0), YF(D["axle_y"] + D["axle_d"] / 2), FXf(-34.0), YF(D["axle_y"] - D["axle_d"] / 2), "brass", 0.3 * s4))
    face, wy = front_face(FXf, YF, s4)
    o.append(face)
    o.append(rect(FXf(4.0), YF(D["head_floor"]), FXf(-4.0), YF(D["oled_top"]), "dark", 0.5))
    o.append(head_face(FXf, YF, s4))
    o.append(T(FXf(0), YF(wy) + 4, "screen", "onblack", "middle"))
    o.append(T(FXf(D["lamp_x"]), YF(D["axle_y"] - D["axle_d"] / 2) + 16, "flashlight", "fn", "middle"))
    o.append(T(FXf(D["tof_x"]), YF(D["axle_y"] - D["axle_d"] / 2) + 16, "ranger", "fn", "middle"))
    o.append(T(FXf(0), YF(0) + 14, "all on the brass axle", "fn", "middle"))
    o.append(dim_h(FXf(hx(HD["sh_x1"])), FXf(hx(HD["sh_x0"])), YF(hy(HD["sh_y1"])) - 12, f"{HD['sh_x1'] - HD['sh_x0']:.0f}", True))
    o.append(dim_v(FXf(hx(HD["x_x0"])) + 8, YF(hy(HD["sh_y0"])), YF(hy(HD["sh_y1"])), f"{HD['sh_y1'] - HD['sh_y0']:.0f}", True))
    # the cut, side on, front to the right, through the servo's shaft: the rail beyond it, the axle and the back bar end on
    SZ = lambda z: 344 + (z - D["piv_z"] + 12.0) * s4    # noqa: E731
    o.append(tube_run(SZ, YF, s4, D["piv_z"] - 12.0, D["rail_z1"], D["rail_y"], D["tube"]))
    o.append(tube_end(SZ, YF, s4, D["bar_z"], D["bar_y"], D["tube"]))
    o.append(tube_end(SZ, YF, s4, D["idler_z"], D["axle_y"], D["axle_d"]))
    o.append(rect(SZ(D["piv_z"] - D["srv_w"] / 2), YF(D["srv_top"]), SZ(D["piv_z"] + D["srv_w"] / 2), YF(D["srv_y0"]), COL["servo"], 1))
    o.append(screen_side(SZ, YF, s4))
    o.append(rect(SZ(D["piv_z"] - 0.8), YF(D["head_floor"] - 0.6), SZ(D["piv_z"] + 0.8), YF(D["srv_top"]), "dark", 0))
    o.append(rect(SZ(D["piv_z"] - 5.0), YF(D["head_floor"]), SZ(D["piv_z"] + 5.0), YF(D["head_floor"] - 1.2), "part", 0.5))
    o.append(poly([(SZ(hz(HD["x_z0"]) + 1.0), YF(hy(0.75))), (SZ(hz(HD["x_z1"]) - 1.0), YF(hy(0.75)))], "brassln").replace('class="brassln"', f'class="brassln" stroke-width="{D["rod1"] * s4:.1f}"'))
    o.append(rect(SZ(hz(HD["x_z0"])), YF(hy(HD["sh_y1"])), SZ(hz(HD["x_z1"])), YF(hy(HD["y0"])), COL["head"], 1.5))
    o.append(rect(SZ(hz(HD["x_z1"])), YF(hy(HD["cam_cy"] + 3.0)), SZ(hz(HD["sh_z1"])), YF(hy(HD["cam_cy"] - 3.0)), "glass", 0.5))
    o.append(f'<circle cx="{SZ(hz(-4.0)):.1f}" cy="{YF(hy(HD["sh_y1"]) + 0.5):.1f}" r="3" class="lamp"/>')
    lx0, ly0 = SZ(hz(HD["x_z0"]) + 1.5), YF(hy(HD["y0"]))
    o.append(f'<path d="M{lx0:.1f},{ly0:.1f} C{lx0 - 14:.1f},{ly0 + 6:.1f} {lx0 - 16:.1f},{YF(D["srv_top"] - 3):.1f} {SZ(D["bar_z"] - 3.0):.1f},{YF(D["rail_y"] + D["tube"] / 2 + 1.5):.1f}" class="thin"/>')
    o.append(T(SZ(hz(HD["x_z0"]) + D["x_d"] / 2), YF(hy(9.0)) + 4, "controller", "onblack", "middle"))
    tx_ = SZ(D["face_z"]) + 10
    o.append(T(tx_, YF(hy(HD["cam_cy"])) + 4, "camera board, bare and black", "fn"))
    o.append(T(tx_, YF(D["head_floor"] + 0.6) + 4, "brass cradle on the horn", "fn"))
    o.append(T(tx_, YF(D["srv_top"] - 4.0) + 4, "servo, shaft up, standing", "fn"))
    o.append(T(tx_, YF(D["srv_top"] - 4.0) + 17, "on the rails between the", "fn"))
    o.append(T(tx_, YF(D["srv_top"] - 4.0) + 30, "axle and the back bar", "fn"))
    o.append(T(tx_, YF(D["oled_bot"] + 8.8) + 4, "screen glued to the axle", "fn"))
    o.append(T(tx_, YF(D["oled_bot"] + 8.8) + 17, "rail: the bus inside it", "fn"))
    ny_ = D["head_floor"] + 10.5
    o.append(leader(SZ(hz(HD["x_z0"]) - 2.5), YF(D["srv_top"] + 1.2), SZ(D["piv_z"] - 12.0) - 10, YF(ny_)))
    o.append(T(SZ(D["piv_z"] - 12.0) - 12, YF(ny_) - 2, "neck: ten wires", "fn", "end"))
    o.append(T(SZ(D["piv_z"] - 12.0) - 12, YF(ny_) + 11, "in a loop", "fn", "end"))

    # ---------------------------------------------------------------- row 2, middle: the frame, tubes only
    o.append(T(585, 500, "The frame: six brass tubes, eight laps", "h2"))
    sf = 1.8
    gx, gy = 692, 600
    GX = lambda x: gx + x * sf          # noqa: E731
    GY = lambda z: gy - z * sf          # noqa: E731
    for zr in (D["r1_z"], D["r2_z"]):
        o.append(rect(GX(-TUBE["rung"] / 2), GY(zr + D["tube"] / 2), GX(TUBE["rung"] / 2), GY(zr - D["tube"] / 2), "brass", 0.3 * sf))
    for sg in (-1, 1):
        o.append(rect(GX(sg * D["rail_x"] - D["tube"] / 2), GY(D["rail_z1"]), GX(sg * D["rail_x"] + D["tube"] / 2), GY(D["rail_z0"]), "brass", 0.3 * sf))
    o.append(rect(GX(-D["bar_x"]), GY(D["bar_z"] + D["tube"] / 2), GX(D["bar_x"]), GY(D["bar_z"] - D["tube"] / 2), "brass", 0.3 * sf))
    o.append(rect(GX(-D["axle_x1"]), GY(D["idler_z"] + D["axle_d"] / 2), GX(D["axle_x1"]), GY(D["idler_z"] - D["axle_d"] / 2), "brass", 0.3 * sf))
    for sg in (-1, 1):
        for xa_, xb_ in ((D["collar_x0"], D["collar_x0"] + D["collar_l"]), (D["axle_x1"] - D["collar_l"], D["axle_x1"])):
            o.append(rect(GX(sg * xa_), GY(D["idler_z"] + D["collar_d"] / 2), GX(sg * xb_), GY(D["idler_z"] - D["collar_d"] / 2), "brass", 0.2 * sf))
        o.append(rect(GX(sg * D["drum_x0"]), GY(D["idler_z"] + 4.5), GX(sg * D["drum_x1"]), GY(D["idler_z"] - 4.5), "ghost", 1))
        for zl in (D["r1_z"], D["r2_z"], D["bar_z"], D["idler_z"]):
            o.append(dot(GX(sg * D["rail_x"]), GY(zl), 2.6))
    o.append(T(GX(0), GY(D["idler_z"]) - 9, f"axle, 4 mm, {TUBE['axle']:.0f}", "fn", "middle"))
    o.append(T(GX(D["drum_x0"] + D["drum_w"] / 2), GY(D["idler_z"]) + 20, "idler drum", "fn", "middle"))
    o.append(T(GX(D["bar_x"]) + 6, GY(D["bar_z"]) + 4, "back bar", "fn"))
    o.append(T(GX(D["rail_x"]) + 6, GY((D["bar_z"] + D["r2_z"]) / 2) + 4, "rails: the spine", "fn"))
    o.append(T(GX(TUBE["rung"] / 2) + 6, GY((D["r1_z"] + D["r2_z"]) / 2) + 4, "rungs", "fn"))
    o.append(dim_h(GX(-D["rail_x"]), GX(D["rail_x"]), GY(D["rail_z0"]) + 16, f"{2 * D['rail_x']:.0f}", False))
    # one rail from the side: the rungs under it, the back bar and the axle on it
    ex0, ey0 = 836, 604
    se = 2.4
    EZ = lambda z: ex0 + (z - D["rail_z0"]) * se    # noqa: E731
    EY = lambda y: ey0 - (y - D["rail_y"]) * se     # noqa: E731
    o.append(tube_run(EZ, EY, se, D["rail_z0"], D["rail_z1"], D["rail_y"], D["tube"]))
    for zr in (D["r1_z"], D["r2_z"]):
        o.append(tube_end(EZ, EY, se, zr, D["rung_y"], D["tube"]))
    o.append(tube_end(EZ, EY, se, D["bar_z"], D["bar_y"], D["tube"]))
    o.append(tube_end(EZ, EY, se, D["idler_z"], D["axle_y"], D["axle_d"]))
    o.append(T(ex0, ey0 + 26, "a rail from the side: the rungs", "fn"))
    o.append(T(ex0, ey0 + 39, "under it, the bar and axle on it", "fn"))
    for i, line in enumerate((f"3 mm tube: two rails {TUBE['rail']:.0f}, two rungs {TUBE['rung']:.0f}, the back bar {TUBE['bar']:.0f} mm",
                              f"4 mm tube: the axle, {TUBE['axle']:.0f} mm; 5 mm: four collars, {D['collar_l']:.0f} mm each",
                              f"Six straight tubes, no bends; {LAPS} laps soldered. The frame is the",
                              "ground. The rails' open ends carry the wires inside:",
                              "the bus and BAT+ in the left, the sound in the right.")):
        o.append(T(585, 742 + i * 13.5, line, "fn"))

    # ---------------------------------------------------------------- row 2, right: key numbers and the colours
    kx, ky = 1010, 500
    o.append(T(kx, ky, "Key numbers", "h2"))
    rows = [
        (f"{D['width']:.0f} × {D['length']:.0f} × {D['height']:.0f} mm", "wide, long, tall"),
        (f"{D['mass']:.0f} g", f"centre {D['cg'][1]:.0f} mm up; tips {D['tip_side']:.0f}°, {D['tip_back']:.0f}° back"),
        (f"{E['speed'] / 10:.1f} cm/s", "on the desk; turns on the spot"),
        ("6 tubes", f"the whole frame, {LAPS} laps, and the ground"),
        (f"head {HD['sh_x1'] - HD['sh_x0']:.0f} × {HD['sh_y1'] - HD['sh_y0']:.0f} × {HD['sh_z1'] - HD['sh_z0']:.0f}", "turns 120°; it hears and sees"),
        (f"{2 * D['planks']} planks", f"{D['plank_p']:.1f} mm apart on {D['gear_n']}-seat drums"),
        (f"{E['explore_h']:.1f} h / {E['talking_h']:.1f} h", "exploring / talking, on one 16340"),
        (f"{E['charge_h']:.1f} h", f"to charge, USB-C at {E['charge_ma']} mA"),
        (f"{D['clear']:.1f} mm", "clearance: the screen's edge" if D["clear"] == D["oled_bot"] else "clearance: the boards under the motors"),
    ]
    for i, (num, what) in enumerate(rows):
        o.append(T(kx, ky + 22 + i * 18, num, "dimlab"))
        o.append(T(kx + 122, ky + 22 + i * 18, what, "fn"))
    nx, ny = 1010, 700
    o.append(T(nx, ny, "Brass, aluminium and black", "h2"))
    for i, line in enumerate(("Brass treads and frame, bare aluminium drums;",
                              "black head, screen, ranger, charger, cell holder",
                              "and speaker, as they are sold. No paint, no skins:",
                              "the blue and green boards hang under the motors,",
                              "out of sight. White light, one warm on the head.")):
        o.append(T(nx, ny + 20 + i * 15, line, "fn"))

    o.append(f'<path d="M20,836 L{20 + 20 * s},836 M20,830 L20,842 M{20 + 20 * s},830 L{20 + 20 * s},842" class="thin"/>')
    o.append(T(20, 826, "20 mm in the three views", "fn"))
    o.append(T(W - 20, 848, f"Rev K for approval, {REV_K}: brass frame, no paint, a voice. Rev J approved {APPROVED_J}; Rev H {APPROVED_H}; Rev A {APPROVED}. Nothing cut or soldered yet. Caliper the drums, the boards and the servo first.", "sub", "end"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Mars rover form sheet">{SHEET_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- sheet 3: the tread and a drum at actual size
def jig_sheet():
    """Drawn in millimetres: printed at Actual size on Letter, one unit is one millimetre on the paper."""
    JW, JH = 262, 186
    o = [f'<text x="0" y="7" class="jh1">Tread and drum, actual size</text>',
         f'<text x="0" y="13" class="jsub">Print at Actual size, then check the 50 mm bar with a ruler. Lay rods on the shapes to cut them, and build on the strip.</text>']
    o.append('<path d="M0,20 L50,20 M0,18 L0,22 M50,18 L50,22 M10,19 L10,21 M20,19 L20,21 M30,19 L30,21 M40,19 L40,21" class="jthin"/>')
    o.append('<text x="52" y="21.2" class="jfn">50 mm</text>')
    # A: cutting gauges, one rod of each length to lay a piece against
    o.append('<text x="0" y="31" class="jh2">1. Cut</text>')
    cuts = [(D["plank_l"], D["rod1"], f"{4 * D['planks']} face rods, 1 mm brass, {D['plank_l']:.1f} mm"),
            (D["pin_l"], D["pin_d"], f"{2 * D['planks']} pin tubes, 3/32 in brass tube, {D['pin_l']:.1f} mm"),
            (15.0, D["rod1"], "4 cradle rods for the head (2 used), 1 mm brass, 15.0 mm"),
            (D["hub_l"], D["hub_d"], f"2 hubs for the drive drums, the owned 4 mm brass tube, {D['hub_l']:.1f} mm"),
            (D["loop_len"], D["loop_wire"], f"{D['loops']} loops, 24-gauge nickel silver, {D['loop_len']:.1f} mm each")]
    for i, (ln, dd, lab) in enumerate(cuts):
        y = 37 + i * 7
        o.append(f'<rect x="0" y="{y - dd / 2:.2f}" width="{ln:.2f}" height="{dd:.2f}" class="jbrass"/>')
        o.append(f'<path d="M0,{y - 2:.2f} L0,{y + 2:.2f} M{ln:.2f},{y - 2:.2f} L{ln:.2f},{y + 2:.2f}" class="jthin"/>')
        o.append(f'<text x="{max(ln, 18) + 3:.1f}" y="{y + 1.2:.2f}" class="jfn">{esc(lab)}</text>')
    # B: one plank, end on and from the face, five times size
    o.append('<text x="0" y="81" class="jh2">2. Solder a plank: two rods side by side, the tube on top</text>')
    k5 = 5.0
    px0, py0 = 6, 100
    for (cx, cy, r) in ((0.5, 0.5, D["rod1"] / 2), (1.5, 0.5, D["rod1"] / 2), (1.0, 0.5 + D["face_h"], D["pin_d"] / 2)):
        o.append(f'<circle cx="{px0 + cx * k5:.2f}" cy="{py0 - cy * k5 + 2.5:.2f}" r="{r * k5:.2f}" class="jbrass"/>')
    o.append(f'<circle cx="{px0 + 1.0 * k5:.2f}" cy="{py0 - (0.5 + D["face_h"]) * k5 + 2.5:.2f}" r="{(D["pin_d"] / 2 - D["pin_wall"]) * k5:.2f}" class="jhole"/>')
    o.append(f'<text x="{px0 - 1}" y="{py0 + 9:.1f}" class="jfn">end on, 5 × size: {D["plank_w"]:.1f} wide, {D["tri_h"]:.1f} thick</text>')
    fx0 = 88
    o.append(f'<rect x="{fx0:.2f}" y="{py0 - 4 - D["pin_d"]:.2f}" width="{D["pin_l"] * 2:.2f}" height="{D["pin_d"] * 2:.2f}" class="jpin"/>')
    o.append(f'<rect x="{fx0 + D["pin_out"] * 2:.2f}" y="{py0 - 6:.2f}" width="{D["plank_l"] * 2:.2f}" height="2" class="jbrass"/>')
    o.append(f'<rect x="{fx0 + D["pin_out"] * 2:.2f}" y="{py0 - 4:.2f}" width="{D["plank_l"] * 2:.2f}" height="2" class="jbrass"/>')
    o.append(f'<text x="{fx0}" y="{py0 + 3:.1f}" class="jfn">from the tread face, 2 × size: the tube stands out {D["pin_out"]:.0f} mm each side for its two</text>')
    o.append(f'<text x="{fx0}" y="{py0 + 8:.1f}" class="jfn">loops. Solder the rods to the tube along their length; keep the tube\'s ends bare.</text>')
    # C: the strip, actual size: twelve stations at the pitch, two loops drawn
    o.append(f'<text x="0" y="118" class="jh2">3. Tape planks face down on the stations and close a loop round each pair of tube ends</text>')
    sx0, sy0 = 4, 132
    half = D["pin_l"] / 2
    for i in range(13):
        x = sx0 + i * D["plank_p"]
        o.append(f'<path d="M{x:.2f},{sy0 - half - 0.5:.2f} L{x:.2f},{sy0 + half + 0.5:.2f}" class="jtick"/>')
    rr = D["pin_d"] / 2 + 0.05 + D["loop_wire"] / 2
    for i in range(12):
        x = sx0 + i * D["plank_p"] + D["plank_p"] / 2
        if i < 6:                                           # a plank seen from the back: its two face rods, the tube on top
            o.append(f'<rect x="{x - 1:.2f}" y="{sy0 - D["plank_l"] / 2:.2f}" width="2" height="{D["plank_l"]:.2f}" class="jbrass"/>')
            o.append(f'<rect x="{x - D["pin_d"] / 2:.2f}" y="{sy0 - half:.2f}" width="{D["pin_d"]:.2f}" height="{D["pin_l"]:.2f}" class="jpin"/>')
        else:
            o.append(f'<rect x="{x - D["pin_d"] / 2:.2f}" y="{sy0 - half:.2f}" width="{D["pin_d"]:.2f}" height="{D["pin_l"]:.2f}" class="jghost"/>')
        if i < 5:
            for ye in (sy0 - D["plank_l"] / 2 - D["pin_out"] / 2, sy0 + D["plank_l"] / 2 + D["pin_out"] / 2):
                o.append(stadium((x, ye), (x + D["plank_p"], ye), rr, "jloop", D["loop_wire"]))
    o.append(f'<text x="{sx0 + 12 * D["plank_p"] + 4:.1f}" y="{sy0 - 2:.1f}" class="jfn">{D["plank_p"]:.1f} mm stations: {D["planks"]} planks close each track,</text>')
    o.append(f'<text x="{sx0 + 12 * D["plank_p"] + 4:.1f}" y="{sy0 + 3:.1f}" class="jfn">the last loop closed on the rover. Each loop: {D["loop_len"]:.0f} mm of 24-gauge nickel silver</text>')
    o.append(f'<text x="{sx0 + 12 * D["plank_p"] + 4:.1f}" y="{sy0 + 8:.1f}" class="jfn">wrapped round the two pins, ends twisted, a dot of solder on the twist only.</text>')
    # D: a drum, actual size, with the planks seated round its lower half
    dcx, dcy = 205, 50
    o.append(f'<text x="{dcx - 50}" y="31" class="jh2">4. Check a drum and a strip against this</text>')
    n = D["gear_n"]
    step = 2 * math.pi / n
    th0 = math.pi - step / 2                                 # turn the outline so a seat sits under each plank drawn below
    c0, s0 = math.cos(th0), math.sin(th0)
    pts = [(dcx + x * c0 - y * s0, dcy - (x * s0 + y * c0)) for x, y in WHEEL]
    o.append('<path d="M' + " L".join(f"{x:.3f},{y:.3f}" for x, y in pts) + 'Z" class="jgear"/>')
    o.append(f'<circle cx="{dcx}" cy="{dcy}" r="{D["hub_d"] / 2}" class="jbrass"/><circle cx="{dcx}" cy="{dcy}" r="{D["hub_id"] / 2}" class="jhole"/>')
    for j in range(n // 2 + 1):                                 # planks in the seats round the bottom half
        th = j * step
        cx_, cy_ = dcx + D["drum_r"] * math.sin(th - math.pi / 2), dcy + D["drum_r"] * math.cos(th - math.pi / 2)
        if cy_ < dcy - 0.01:
            continue
        for k, (rz, ry) in enumerate(rods_of(0.0, 0.0, th - math.pi / 2)):
            o.append(f'<circle cx="{cx_ + rz:.3f}" cy="{cy_ - ry:.3f}" r="{rod_r(k):.3f}" class="jbrass"/>')
        o.append(f'<circle cx="{cx_:.3f}" cy="{cy_:.3f}" r="{D["pin_d"] / 2 - D["pin_wall"]:.3f}" class="jhole"/>')
    for i, line in enumerate((f"Aluminium drum, two 3/8 in halves glued: {n} seats, {D['drum_od']:.1f} mm over the teeth.",
                              f"Each plank's pin tube sits in a round seat, {DRUM.SEAT_R - D['pin_d'] / 2:.2f} mm loose; the planks",
                              f"are {D['plank_p']:.2f} mm apart on the runs. Lay the strip round the drum:",
                              "every pin tube should drop into a seat.",
                              "Bare aluminium, no paint: file each seat and the hole.",
                              "Drives on brass hubs; idlers turn on the 4 mm axle.")):
        o.append(f'<text x="{dcx - 50}" y="{dcy + 23 + i * 5:.1f}" class="jfn">{esc(line)}</text>')
    o.append(f'<text x="0" y="{JH - 2}" class="jfn">Rev K for approval, {REV_K}. Frame: 3 mm tube, rails {TUBE['rail']:.0f}, rungs {TUBE['rung']:.0f}, back bar {TUBE['bar']:.0f}; 4 mm axle {TUBE['axle']:.1f}; four 5 mm collars {D['collar_l']:.0f}. Numbers from build_page.py.</text>')
    css = ("<style>.jh1{font:900 6px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".jh2{font:700 3.6px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".jsub,.jfn{font:400 3px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".jthin{fill:none;stroke:var(--ink);stroke-width:.3}"
           ".jtick{fill:none;stroke:var(--ink-2);stroke-width:.2}"
           ".jghost{fill:none;stroke:var(--ink-2);stroke-width:.2;stroke-dasharray:.8 .6}"
           ".jbrass{fill:var(--rv-brass);stroke:var(--rv-brass-lo);stroke-width:.15}"
           ".jpin{fill:var(--rv-brass);stroke:var(--rv-brass-lo);stroke-width:.15;opacity:.85}"
           ".jring{fill:none;stroke:var(--rv-brass)}"
           ".jspoke{fill:none;stroke:var(--rv-brass-lo);stroke-width:1;stroke-linecap:round}"
           ".jhole{fill:var(--paper);stroke:var(--rv-brass-lo);stroke-width:.15}"
           ".jgear{fill:var(--rv-steel);stroke:var(--rv-steel-lo);stroke-width:.15;stroke-linejoin:round}"
           ".jivory{fill:var(--rv-ivory);stroke:var(--rv-ivory-lo);stroke-width:.15}"
           ".jloop{fill:none;stroke:var(--rv-ni);stroke-linecap:round}" + RV_CSS + "</style>")
    return (f'<svg viewBox="0 0 {JW} {JH}" width="{JW}mm" height="{JH}mm" role="img" aria-label="Mars rover tread and drum at actual size">'
            f'{css}{"".join(o)}</svg>')


# ----------------------------------------------------------------------------- sheet 2: the wiring
def gnd_glyph(x, y):
    """The frame as ground: three short bars under a joint."""
    return (f'<path d="M{x - 9},{y} L{x + 9},{y} M{x - 6},{y + 4} L{x + 6},{y + 4} M{x - 3},{y + 8} L{x + 3},{y + 8}" class="thin"/>'
            + T(x + 14, y + 7, "frame", "fn"))


def wiring_sheet():
    rt = Router()
    w = rt.wire
    o = [T(20, 30, "Mars rover: every connection on one sheet", "h1"),
         T(20, 48, "A dot is a joint. A line that hops over another does not touch it. Thick = wire you solder (26 AWG for BAT+, 30 AWG for the rest). Thin = a lead that comes with the part. Pins are grouped by job, not by position on the board.", "sub")]
    MX0, MX1 = 1032, 1100                      # the neck: ten wires in a loop beside the horn
    Y3V3, YSDA, YSCL, YLAMP, YSRV = 150, 190, 230, 262, 290   # logic lanes and the two signals that go down to the frame
    YGND, YBAT, Y5V = 470, 510, 540            # power lanes; the servo's 5 V comes from the charger's boost
    YBCK, YLRC, YDIN = 585, 610, 635           # the sound, down the neck to the amplifier
    o.append(T(30, 82, "BODY: THE FRAME AND THE RUNNING GEAR", "zone")); o.append(T(MX0 + 4, 82, "NECK", "zone")); o.append(T(1128, 82, "HEAD", "zone"))
    o.append(rect(MX0, 92, MX1, 652, "tubeband", 18))
    o.append(T((MX0 + MX1) / 2, 668, "ten wires", "fn", "middle"))
    o.append(T((MX0 + MX1) / 2, 682, "in a loop", "fn", "middle"))

    # ---------------------------------------------------------------- lanes first, so every later crossing hops over them
    o.append(w([(MX0 + 16, Y3V3), (500, Y3V3)], "rod", "3V3"))
    o.append(w([(MX0 + 16, YSDA), (500, YSDA)], "rod", "SDA"))
    o.append(w([(MX0 + 16, YSCL), (500, YSCL)], "rod", "SCL"))
    o.append(w([(MX0 + 16, YLAMP), (878, YLAMP)], "rod", "LAMP"))
    o.append(w([(MX0 + 16, YSRV), (984, YSRV)], "rod", "SERVO"))
    o.append(w([(300, YGND), (1130, YGND)], "rod", "GND"))
    o.append(w([(330, YBAT), (1130, YBAT)], "rod", "BAT+"))
    o.append(w([(340, Y5V), (1004, Y5V)], "rod", "5V"))
    o.append(T(352, Y5V - 6, "5 V from the boost", "fn"))
    for yy, net in ((YBCK, "BCLK"), (YLRC, "LRCLK"), (YDIN, "DIN")):
        o.append(w([(915, yy), (1130, yy)], "rod", net))
    for yy, net in ((Y3V3, "3V3"), (YSDA, "SDA"), (YSCL, "SCL"), (YLAMP, "LAMP"), (YSRV, "SERVO")):
        o.append(w([(MX1 - 16, yy), (1130, yy)], "rod", net))
    for yy, lab in ((Y3V3, "3 · 3V3"), (YSDA, "4 · SDA"), (YSCL, "5 · SCL"), (YLAMP, "7 · LAMP"), (YSRV, "6 · SERVO"), (YGND, "2 · GND"), (YBAT, "1 · BAT+"),
                    (YBCK, "8 · BCLK"), (YLRC, "9 · LRCLK"), (YDIN, "10 · DIN")):
        o.append(T((MX0 + MX1) / 2, yy - 8, lab, "mono", "middle"))

    # ---------------------------------------------------------------- body: motors, motor controller, display, ranger, lamp, servo
    for (yb, name, sub, pa, pb, na, nb) in ((108, "Left gearmotor", "150:1, low power", 150, 178, "M1A", "M1B"),
                                           (218, "Right gearmotor", "faces the other way", 258, 286, "M2A", "M2B")):
        o.append(f'<rect x="30" y="{yb}" width="150" height="86" rx="9" class="part"/>')
        o.append(T(42, yb + 30, name, "title")); o.append(T(42, yb + 50, sub, "sub")); o.append(T(42, yb + 66, "tabs + and −", "sub"))
        o.append(pin(rt, 180, pa, "+", "R", na)); o.append(pin(rt, 180, pb, "−", "R", nb))
    CX, CY, CW, CH = 270, 108, 230, 312
    o.append(block(CX, CY, CW, CH, "Motor controller", "two channels · I²C 0x10", ty=24))
    o.append(pin(rt, CX, 150, "M1A", "L", "M1A")); o.append(pin(rt, CX, 178, "M1B", "L", "M1B"))
    o.append(pin(rt, CX, 258, "M2A", "L", "M2A")); o.append(pin(rt, CX, 286, "M2B", "L", "M2B"))
    for yy, a_, b_ in ((150, "M1A", "M1B"), (258, "M2A", "M2B")):
        o.append(w([(180, yy), (CX, yy)], "rod", a_)); o.append(w([(180, yy + 28), (CX, yy + 28)], "rod", b_))
    o.append(pin(rt, CX + CW, Y3V3, "VDD", "R", "3V3"))
    o.append(pin(rt, CX + CW, YSDA, "SDA", "R", "SDA"))
    o.append(pin(rt, CX + CW, YSCL, "SCL", "R", "SCL"))
    o.append(pin(rt, CX + CW, 270, "GND", "R", "GND"))
    o.append(pin(rt, CX + 60, CY + CH, "VIN", "B", "BAT+")); o.append(pin(rt, CX + 180, CY + CH, "GND", "B", "GND"))
    o.append(T(CX + 16, 316, "VDD is the logic supply: 3.3 V", "fn")); o.append(T(CX + 16, 330, "not wired: VM, ERR, RST, JMP1", "fn"))
    o.append(T(CX + 16, 346, "blue: it hangs under the motors,", "fn"))
    o.append(T(CX + 16, 360, "out of sight; stops both tracks", "fn"))
    o.append(T(CX + 16, 374, "if I²C goes quiet for 200 ms", "fn"))
    o.append(w([(CX + CW, 270), (520, 270), (520, YGND)], "rod", "GND")); o.append(dot(520, YGND))
    o.append(w([(CX + 60, CY + CH), (CX + 60, YBAT)], "rod", "BAT+")); o.append(dot(CX + 60, YBAT))
    o.append(w([(CX + 180, CY + CH), (CX + 180, YGND)], "rod", "GND")); o.append(dot(CX + 180, YGND))
    DX, DY, DW, DH = 525, 320, 120, 130
    o.append(block(DX, DY, DW, DH, "Display", "black board · 0x3D", ty=52))
    o.append(pin(rt, 545, DY, "VIN", "T", "3V3")); o.append(pin(rt, 580, DY, "SDA", "T", "SDA")); o.append(pin(rt, 615, DY, "SCL", "T", "SCL"))
    o.append(pin(rt, 630, DY + DH, "GND", "B", "GND"))
    o.append(w([(615, DY), (615, YSCL)], "rod", "SCL")); o.append(dot(615, YSCL))
    o.append(w([(580, DY), (580, YSDA)], "rod", "SDA")); o.append(dot(580, YSDA))
    o.append(w([(545, DY), (545, Y3V3)], "rod", "3V3")); o.append(dot(545, Y3V3))
    o.append(w([(630, DY + DH), (630, YGND)], "rod", "GND")); o.append(dot(630, YGND))
    RX, RY, RW, RH = 665, 320, 125, 130
    o.append(block(RX, RY, RW, RH, "Laser ranger", "black · 0x29", ty=52))
    o.append(pin(rt, 685, RY, "SCL", "T", "SCL")); o.append(pin(rt, 720, RY, "SDA", "T", "SDA")); o.append(pin(rt, 755, RY, "VIN", "T", "3V3"))
    o.append(pin(rt, 775, RY + RH, "GND", "B", "GND"))
    o.append(pin(rt, RX + RW, 410, "XSHUT", "R", "XSHUT"))
    o.append(w([(685, RY), (685, YSCL)], "rod", "SCL")); o.append(dot(685, YSCL))
    o.append(w([(720, RY), (720, YSDA)], "rod", "SDA")); o.append(dot(720, YSDA))
    o.append(w([(755, RY), (755, Y3V3)], "rod", "3V3")); o.append(dot(755, Y3V3))
    o.append(w([(775, RY + RH), (775, YGND)], "rod", "GND")); o.append(dot(775, YGND))
    o.append(w([(RX + RW, 410), (RX + RW + 16, 410)], "thin", "XSHUT"))
    o.append(zigzag_v(rt, RX + RW + 16, 410, 345, "XSHUT"))
    o.append(T(RX + RW + 25, 382, "10k", "lab"))
    o.append(w([(RX + RW + 16, 345), (RX + RW + 16, 305), (755, 305)], "thin", "3V3")); o.append(dot(755, 305))
    o.append(T(RX + 52, RY + 86, "GPIO1 open", "fn", "middle"))
    LX_, LY_, LW_, LH_ = 842, 320, 72, 130
    o.append(f'<rect x="{LX_}" y="{LY_}" width="{LW_}" height="{LH_}" rx="9" class="part"/>')
    o.append(T(LX_ + LW_ / 2, LY_ + 50, "Lamp", "title", "middle"))
    o.append(T(LX_ + LW_ / 2, LY_ + 68, "regulator", "fn", "middle")); o.append(T(LX_ + LW_ / 2, LY_ + 81, "+ LED", "fn", "middle"))
    o.append(pin(rt, 878, LY_, "VDD", "T", "LAMP"))
    o.append(pin(rt, 858, LY_ + LH_, "GND", "B", "GND")); o.append(pin(rt, 898, LY_ + LH_, "LED+", "B", "BAT+"))
    o.append(w([(878, YLAMP), (878, LY_)], "rod", "LAMP")); o.append(dot(878, YLAMP))
    o.append(w([(858, LY_ + LH_), (858, YGND)], "rod", "GND")); o.append(dot(858, YGND))
    o.append(w([(898, LY_ + LH_), (898, YBAT)], "rod", "BAT+")); o.append(dot(898, YBAT))
    SVX, SVY, SVW, SVH = 946, 320, 74, 130
    o.append(f'<rect x="{SVX}" y="{SVY}" width="{SVW}" height="{SVH}" rx="9" class="part"/>')
    o.append(T(SVX + SVW / 2, SVY + 50, "Servo", "title", "middle"))
    o.append(T(SVX + SVW / 2, SVY + 68, "5 V from", "fn", "middle")); o.append(T(SVX + SVW / 2, SVY + 81, "the charger", "fn", "middle"))
    o.append(pin(rt, 984, SVY, "SIG", "T", "SERVO"))
    o.append(pin(rt, 966, SVY + SVH, "GND", "B", "GND")); o.append(pin(rt, 1004, SVY + SVH, "VIN", "B", "5V"))
    o.append(w([(984, YSRV), (984, SVY)], "rod", "SERVO")); o.append(dot(984, YSRV))
    o.append(w([(966, SVY + SVH), (966, YGND)], "rod", "GND")); o.append(dot(966, YGND))
    o.append(w([(1004, SVY + SVH), (1004, Y5V)], "rod", "5V"))
    o.append(cap_v(926, YGND, YBAT, "")); o.append(dot(926, YGND)); o.append(dot(926, YBAT))
    o.append(T(912, YBAT + 22, "220 µF", "lab", "middle"))

    # ---------------------------------------------------------------- body: the power chain and the voice under the lanes
    o.append(f'<rect x="30" y="570" width="150" height="110" rx="9" class="part"/>')
    o.append(T(42, 600, "16340 cell", "title")); o.append(T(42, 618, "in its black holder", "sub"))
    o.append(pin(rt, 180, 625, "+", "R", "CELL+")); o.append(pin(rt, 180, 650, "−", "R", "CELL-"))
    QX, QY, QW, QH = 228, 556, 170, 144
    o.append(block(QX, QY, QW, QH, "Charger, 5 V boost", "black · jumper cut: 500 mA", ty=44))
    o.append(pin(rt, QX, 625, "+", "L", "CELL+")); o.append(pin(rt, QX, 650, "−", "L", "CELL-"))
    o.append(pin(rt, 300, QY, "G", "T", "GND")); o.append(pin(rt, 340, QY, "5V", "T", "5V")); o.append(pin(rt, 375, QY, "EN", "T", "BAT+"))
    o.append(pin(rt, QX + QW, 625, "BAT", "R", "VBAT"))
    o.append(rect(QX + 14, QY + QH - 28, QX + 54, QY + QH - 12, "usb", 3)); o.append(T(QX + 34, QY + QH - 16, "USB-C", "fn", "middle"))
    o.append(T(QX + 62, QY + QH - 16, "switch off to charge", "fn"))
    o.append(w([(180, 625), (QX, 625)], "thin", "CELL+")); o.append(w([(180, 650), (QX, 650)], "thin", "CELL-"))
    o.append(T(204, 615, "pigtail", "fn", "middle"))
    o.append(w([(300, QY), (300, YGND)], "rod", "GND"))
    o.append(w([(340, QY), (340, Y5V)], "rod", "5V"))
    o.append(w([(375, QY), (375, YBAT)], "rod", "BAT+")); o.append(dot(375, YBAT))
    SX, SY_ = 440, 585
    o.append(block(SX, SY_, 130, 80, "Switch", "right = on", ty=32))
    o.append(pin(rt, SX, 625, "on", "L", "VBAT")); o.append(pin(rt, 555, SY_, "mid", "T", "BAT+")); o.append(pin(rt, 545, SY_ + 80, "off", "B", "GND"))
    o.append(w([(QX + QW, 625), (SX, 625)], "rod", "VBAT"))
    o.append(w([(555, SY_), (555, YBAT)], "rod", "BAT+")); o.append(dot(555, YBAT))
    o.append(w([(545, SY_ + 80), (545, 686)], "rod", "GND")); o.append(gnd_glyph(545, 686))
    o.append(cap_v(612, YGND, YBAT, "100 µF")); o.append(dot(612, YGND)); o.append(dot(612, YBAT))
    PX, PY, PW, PH = 628, 592, 92, 86
    o.append(block(PX, PY, PW, PH, "Speaker", "8 Ω, black", ty=24))
    o.append(pin(rt, PX + PW, 646, "+", "R", "SPK+")); o.append(pin(rt, PX + PW, 662, "−", "R", "SPK-"))
    AX, AY, AW, AH = 760, 570, 155, 125
    o.append(block(AX, AY, AW, AH, "Amplifier", "purple, out of sight", ty=78))
    o.append(pin(rt, 790, AY, "VIN", "T", "BAT+")); o.append(pin(rt, 830, AY, "GND", "T", "GND"))
    o.append(pin(rt, AX, 646, "+", "L", "SPK+")); o.append(pin(rt, AX, 662, "−", "L", "SPK-"))
    o.append(pin(rt, AX + AW, YBCK, "BCLK", "R", "BCLK")); o.append(pin(rt, AX + AW, YLRC, "LRC", "R", "LRCLK")); o.append(pin(rt, AX + AW, YDIN, "DIN", "R", "DIN"))
    o.append(w([(PX + PW, 646), (AX, 646)], "thin", "SPK+")); o.append(w([(PX + PW, 662), (AX, 662)], "thin", "SPK-"))
    o.append(w([(790, AY), (790, YBAT)], "rod", "BAT+")); o.append(dot(790, YBAT))
    o.append(w([(830, AY), (830, YGND)], "rod", "GND")); o.append(dot(830, YGND))
    o.append(cap_v(700, YGND, YBAT, "220 µF")); o.append(dot(700, YGND)); o.append(dot(700, YBAT))
    o.append(T(AX + AW / 2 + 8, AY + 116, "GAIN, SD open", "fn", "middle"))

    # ---------------------------------------------------------------- head: the controller with its camera and microphone, the beacon, the 8x8 ranger
    XX, XY, XW, XH = 1130, 108, 120, 550
    o.append(block(XX, XY, XW, XH, "Controller", "", ty=24))
    o.append(pin(rt, XX, Y3V3, "3V3", "L", "3V3")); o.append(pin(rt, XX, YSDA, "D4", "L", "SDA")); o.append(pin(rt, XX, YSCL, "D5", "L", "SCL"))
    o.append(pin(rt, XX, YLAMP, "D1", "L", "LAMP")); o.append(pin(rt, XX, YSRV, "D0", "L", "SERVO"))
    o.append(pin(rt, XX, YGND, "BAT−", "L", "GND")); o.append(pin(rt, XX, YBAT, "BAT+", "L", "BAT+"))
    o.append(pin(rt, XX, YBCK, "D7", "L", "BCLK")); o.append(pin(rt, XX, YLRC, "D6", "L", "LRCLK")); o.append(pin(rt, XX, YDIN, "D10", "L", "DIN"))
    o.append(pin(rt, XX + XW, 150, "D3", "R", "BEACON"))
    for yy, nm, net in ((256, "GND", "GND"), (278, "3V3", "3V3"), (300, "D8", "SDA2"), (322, "D9", "SCL2")):
        o.append(pin(rt, XX + XW, yy, nm, "R", net))
    o.append(T(XX + 12, 352, "camera, Wi-Fi,", "fn")); o.append(T(XX + 12, 366, "microphone: one", "fn")); o.append(T(XX + 12, 380, "ESP32-S3, black", "fn"))
    o.append(T(XX + 12, 404, "5V pin: never", "fn")); o.append(T(XX + 12, 418, "BAT pads: back", "fn"))
    o.append(T(XX + 12, 442, "console on USB,", "fn")); o.append(T(XX + 12, 456, "so D6, D7 are free", "fn"))
    o.append(rect(XX + 40, XY - 8, XX + 80, XY + 8, "usb", 3)); o.append(T(XX + 60, XY - 14, "USB-C: flash once", "fn", "middle"))
    BX, BY, BW, BH = 1258, 166, 92, 64
    o.append(block(BX, BY, BW, BH, "Beacon", "warm white", ty=34))
    o.append(pin(rt, 1292, BY, "+", "T", "BEACON")); o.append(pin(rt, 1263, BY + BH, "−", "B", "GND"))
    o.append(w([(XX + XW, 150), (1258, 150)], "rod", "BEACON")); o.append(zigzag_h(rt, 1258, 1286, 150, "BEACON"))
    o.append(w([(1286, 150), (1292, 150), (1292, BY)], "thin", "BEACON"))
    o.append(T(1272, 134, "100 Ω", "lab", "middle"))
    o.append(w([(1263, BY + BH), (1263, 256)], "thin", "GND")); o.append(dot(1263, 256))
    TX8, TY8, TW8, TH8 = 1276, 244, 76, 132
    o.append(block(TX8, TY8, TW8, TH8, "8×8 ranger", "black · 3–6 V", ty=106))
    for yy, nm, net in ((256, "GND", "GND"), (278, "VIN", "3V3"), (300, "SDA", "SDA2"), (322, "SCL", "SCL2")):
        o.append(pin(rt, TX8, yy, nm, "L", net))
        o.append(w([(XX + XW, yy), (TX8, yy)], "rod", net))
    for i, line in enumerate(("Only the ten", "neck wires", "cross the turning", "joint: they twist", "through 120°.")):
        o.append(T(1262, 410 + i * 14, line, "fn"))

    # ---------------------------------------------------------------- the budget along the bottom
    NY = 714
    o.append(T(20, NY, "The budget, from the cell (mA)", "h2"))
    cols = [("parked, watching", E["parked"], f"Wi-Fi on, camera idle, display, ranger · {E['parked_h']:.1f} h"),
            ("exploring", E["explore"], f"camera streaming, the 8×8 ranger on, both tracks, the head sweeping · {E['explore_h']:.1f} h"),
            ("at night", E["night"], f"exploring + the flashlight at its 50 % cap · {E['night_h']:.1f} h"),
            ("talking", E["talking"], f"stopped, listening and speaking at a room's level · {E['talking_h']:.1f} h"),
            ("never all at once", E["peak_all"], "every stall and the lamp full; ramps and caps keep peaks near 1 A")]
    for i, (name, ma, note) in enumerate(cols):
        yy = NY + 20 + i * 17
        o.append(T(40, yy, name, "lab")); o.append(T(270, yy, f"{ma:.0f} mA", "mono", "end")); o.append(T(286, yy, note, "fn"))
    o.append(T(820, NY + 20, f"3.3 V rail at its worst: {E['rail3v3_peak']:.0f} mA of the regulator's 700.", "fn"))
    o.append(T(820, NY + 37, f"Charge: USB-C at the charger, port up, switch off, {E['charge_ma']} mA, about {E['charge_h']:.1f} h.", "fn"))
    o.append(T(820, NY + 54, "Never: both USB-C ports at once · the 5V pin · the cell soldered.", "fn"))
    o.append(T(820, NY + 71, "Flash with the switch on, so the board's own charger sees the cell.", "fn"))
    o.append(T(820, NY + 88, "In the rails: BAT+, 3V3, SDA, SCL left; BCLK, LRCLK, DIN, 5V right.", "fn"))

    bad, crossings = rt.check()
    for b in bad:
        print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    o.append(T(20, 848, f"Rev K for approval, {REV_K}: a black charger with its own 5 V boost, the voice on three more neck wires, the switch grounding the supply when off. {crossings} crossings, each a hop. Sources: Pololu, Adafruit, Seeed, Same Sky, ST, Analog Devices.", "sub"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Mars rover wiring sheet">{SHEET_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- page
def md_inline(t):
    t = esc(t).replace("&amp;lt;", "&lt;").replace("&amp;gt;", "&gt;")
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|\.\./[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)


def a(text, key):
    return f'<a href="{L[key]}" target="_blank" rel="noopener">{text}</a>'


def intro_html():
    return f"""
<h2>What it is</h2>
<p>A wide little tank that lives on a desk, built on a brass spine. Two brass treads, soldered from 1 mm {a("brass rod", "rod10")} and 3/32 in {a("brass tube", "tube332")} and joined with {a("nickel-silver", "nickel")} loops, run on four bare {a("aluminium drums", "drum")} like the reference's. Between them, six straight {a("brass tubes", "brass_tube")} make the frame: two rails down the middle, two rungs under the motors, a short back bar, and a 4 mm axle across the front that the idler drums turn on. The {a("servo", "servo")} stands on the rails; the small black {a("screen", "oled_black")}, a black {a("laser ranger", "tof_black")} and a {a("flashlight", "star")} hang on the axle; the {a("cell", "cell")} in its black holder, a black {a("charger", "chg_black")}, the switch and a black {a("speaker", "speaker")} sit on the rear deck. The head is the black {a("camera", "xiao")} board on its side with a black {a("8×8 ranger", "tof8_black")} beside it and a blinking {a("beacon", "chip")} on top.</p>
<p>You drive it from a phone and talk to it. The page shows what the camera sees; the ranger watches the desk ahead and stops the treads before an edge; the 8×8 ranger measures the room as the head turns; the camera board's microphone listens and the speaker answers. It charges over USB-C at the charger behind the cell. No box, no paint, no skins, nothing printed: every part shows its own colour (brass, aluminium, steel, black), and the blue and purple boards that have no black twin hang under the motors, out of sight.</p>
<p>The reference is Huy Vector's <a href="{L['reference']}" target="_blank" rel="noopener">DIY Micro RC Spy Tank</a> (<a href="{L['video']}" target="_blank" rel="noopener">video</a>): a copper-wire tank on treads of short rods soldered side by side, with an FPV camera, two LED headlights and 16340 cells. Ours keeps the metal frame, the soldered treads, the camera, the light and the 16340, and gives it a low turning head that sees, hears and speaks.</p>
<p><strong>Step 1 of the house rule. Rev K, for approval.</strong> Rev J was approved as drawn on {APPROVED_J}, Rev H on {APPROVED_H} and Rev A on {APPROVED}. Rev K keeps Rev J's treads, drums, size and pins, and makes three changes at your word: the frame is brass tube, nothing is painted or skinned, and it has a voice. The <a href="{PHYSICS_PAGE}" target="_blank" rel="noopener">physics page</a> still follows Rev J; it is rewritten after the yes. Nothing cut or soldered yet.</p>
"""


def decisions_html():
    o = ["<h2>The decisions</h2>"]
    for head, text in DECISIONS:
        o.append(f"<h3>{esc(head)}</h3><p>{md_inline(text)}</p>")
    return "".join(o)


def dims_rows():
    return [("width", "overall width, pin end to pin end"), ("length", "overall length"), ("height", "overall height, desk to the beacon on the roof"),
            ("tr_h", "tread height, round a drum"), ("tr_w", "plank length (the tread face)"), ("plank_p", "plank pitch"), ("pitch", "drum centres"),
            ("drum_r", "the tread's hinge line round a drum (radius)"), ("drum_od", "drum, over the teeth"), ("drum_w", "drum, wide (two 3/8 in halves)"),
            ("hub_l", "each drive drum's brass hub"), ("drum_x0", "drum's inner face, from the centre line"), ("axle_x1", "the front axle's ends, from the centre line"),
            ("teeth_x", "tread centre line, from the rover's centre line"), ("face_x", "gearbox face, from the centre line"), ("mot_x_in", "motors' inner ends, from the centre line"),
            ("rail_x", "the two rails (the spine), from the centre line"), ("rail_y", "rails above the desk"), ("rung_y", "rungs above the desk (the motors sit on them)"),
            ("axle_y", "front axle above the desk (the drums' height)"), ("bar_z", "back bar, ahead of the body's centre"), ("bar_y", "back bar above the desk"),
            ("face_z", "the face (screen, ranger, lamp), ahead of the body's centre"),
            ("oled_top", "screen top edge"), ("oled_bot", "screen bottom edge, its tabs"), ("piv_z", "servo shaft, ahead of the body's centre"), ("srv_y0", "servo's foot, on the rails"), ("srv_top", "servo's top face"),
            ("head_floor", "head's floor above the desk"), ("head_front", "camera lens, ahead of the body's centre"), ("cam_y", "camera lens above the desk"),
            ("tof_y", "ranger above the desk"), ("tof_reach", "where the ranger's centre ray meets the desk, ahead of the face"), ("tof_slant", "the ranger's distance to that point"),
            ("holder_y0", "cell holder's floor (on the motor cans)"), ("spk_z0", "speaker's back edge, on the spine"), ("under_y0", "underside of the boards under the motors"),
            ("clear", "ground clearance: the lowest part, the screen's tabs")]


def dims_html():
    o = ['<h2>Dimensions</h2><div class="tw"><table><tr><th>What</th><th>mm</th></tr>']
    o += [f'<tr><td>{esc(lab)}</td><td class="m">{D[k]:.1f}</td></tr>' for k, lab in dims_rows()]
    o.append("</table></div>")
    o.append("<h3>Mass</h3>")
    o.append('<div class="tw"><table><tr><th>Part</th><th>g</th></tr>' + "".join(f'<tr><td>{esc(n)}</td><td class="m">{m:.1f}</td></tr>' for n, m, _ in MASS) + f'<tr><td><strong>Total</strong></td><td class="m"><strong>{D["mass"]:.0f}</strong></td></tr></table></div>')
    o.append(f"<p>Centre of mass {D['cg'][1]:.0f} mm up and {abs(D['cg'][2]):.0f} mm {'behind' if D['cg'][2] < 0 else 'ahead of'} the middle. It tips sideways at {D['tip_side']:.0f}° and backwards at {D['tip_back']:.0f}°. The treads', drums' and head's masses are computed or estimated; weigh them.</p>")
    return "".join(o)


def pins_html():
    o = ['<h2>Pin map, XIAO ESP32-S3 Sense (in the head)</h2>',
         '<p>The I²C pair, the three sound pins and two signals leave the head down the neck; everything else in the body is on I²C.</p>',
         '<div class="tw"><table><tr><th>Pin</th><th>GPIO</th><th>Job</th><th>Goes to</th></tr>']
    for p, g, job, to in PINS:
        o.append(f'<tr><td class="m">{esc(p)}</td><td class="m">{esc(g)}</td><td>{esc(job)}</td><td>{esc(to)}</td></tr>')
    o.append("</table></div>")
    o.append("<h3>The I²C bus</h3><p>" + " · ".join(f"{esc(n)} <code>{esc(a_)}</code>" for n, a_ in I2C) + ". No two share an address, so nothing is re-addressed at boot.</p>")
    o.append('<h3>Motor controller pins</h3><p>Used: <code>VIN</code> and the <code>GND</code> beside it (the cell, after the switch), <code>M1A</code> <code>M1B</code> (left motor), <code>M2A</code> <code>M2B</code> (right motor), <code>VDD</code> (3.3 V from the head), <code>SDA</code>, <code>SCL</code> and one logic <code>GND</code>. Not wired: <code>VM</code>, <code>ERR</code>, <code>RST</code>, <code>JMP1</code>.</p>')
    return "".join(o)


def nets_html():
    o = ['<h2>Every wire, and why</h2>', '<div class="tw"><table><tr><th>Net</th><th>From</th><th>To</th><th>Wire</th><th>Why</th></tr>']
    for net, fr, to, wire, why in NETS:
        o.append(f'<tr><td class="m">{esc(net)}</td><td>{esc(fr)}</td><td>{esc(to)}</td><td>{esc(wire)}</td><td>{md_inline(why)}</td></tr>')
    o.append("</table></div>")
    return "".join(o)


def budget_html():
    rows = [("controller, Wi-Fi on", E["xiao_wifi"], "Seeed wiki, at 3.8 V on BAT, with the Sense board"),
            ("controller, camera streaming", E["xiao_cam"], "the wiki's webcam figure; 366 mA at an image capture"),
            ("laser ranger", E["tof"], "Pololu, typical; 40 mA peaks"),
            ("display", E["oled"], "about half the pixels lit"),
            ("motor controller logic", E["motoron"], "estimate"),
            ("servo at rest, through the charger's boost", E["srv_idle"], "5 mA at 5 V (datasheet); the boost's 1 mA on top"),
            ("8×8 ranger, ranging", E["tof8"], "ST's figure for the sensor; asleep when parked"),
            ("amplifier idle; speaking", E["amp_q"], f"datasheet; about {E['talk']:.0f} mA while it speaks at a room's level, {E['talk_peak']:.0f} on a loud syllable"),
            ("servo moving", E["srv_run"], "50 mA at 5 V"),
            ("two motors on the desk", 2 * E["mot_run"], f"estimate; a stall is {E['mot_stall']:.0f} mA each"),
            ("flashlight at its cap", E["lamp"] * E["lamp_cap"], "350 mA at 50 %")]
    o = ['<h2>The budget</h2>', '<div class="tw"><table><tr><th>Load</th><th class="m">mA</th><th>Source</th></tr>']
    o += [f'<tr><td>{esc(n)}</td><td class="m">{v:.0f}</td><td>{esc(s_)}</td></tr>' for n, v, s_ in rows]
    o.append("</table></div>")
    o.append(f"<p>Parked and watching: {E['parked']:.0f} mA, {E['parked_h']:.1f} h on the 950 mAh cell (90 % usable). Exploring with the camera streaming and the head sweeping: {E['explore']:.0f} mA, {E['explore_h']:.1f} h. With the flashlight on: {E['night']:.0f} mA, {E['night_h']:.1f} h. Stopped and talking: {E['talking']:.0f} mA, {E['talking_h']:.1f} h. Charging: {E['charge_h']:.1f} h at {E['charge_ma']} mA, switch off.</p>")
    o.append(f"<p>Everything at once, every stall and the lamp full, would be {E['peak_all']:.0f} mA, near the cell's 2 A cut-out. It never happens: the motor controller ramps, the firmware caps the drive at 70 % and the lamp at 50 %, the head waits while the tracks start, and the treads wait while it talks. Real peaks sit near 1 A. The head's 3.3 V regulator sees {E['rail3v3_peak']:.0f} mA at worst, of 700.</p>")
    o.append(f"<p>Speed: 90 rpm at 6 V is {E['rpm']:.0f} rpm at 3.7 V; the tread moves with its pins, {E['track_pitch_d']:.0f} mm across a drum, so {E['speed_free']:.0f} mm/s free and about {E['speed']:.0f} on the desk.</p>")
    return "".join(o)


def parts_html():
    o = ['<h2>Parts</h2>', '<p>Rev K adds four black parts: one on Amazon, two from DigiKey in one order, one from SB Components in the UK (no US shop had it). It drops two lines from your Amazon cart, the brass sheet and the M3 screws. The drums and the Pololu parts are ordered. Owned parts are listed so they are not bought twice, and Rev J parts that Rev K leaves out are listed for the shared bin. Each part is named by what it is, with the link on the word to the exact product.</p>']
    for head, rows in PARTS:
        o.append(f"<h3>{esc(head)}</h3>")
        o.append('<div class="tw"><table><tr><th>Qty</th><th>Part</th><th>Where</th><th>Price</th><th>Why, and what to check</th></tr>')
        for qty, part, url, code, where, why in rows:
            name = f'<a href="{url}" target="_blank" rel="noopener">{esc(part)}</a>' if url else esc(part)
            o.append(f'<tr><td class="m">{esc(qty)}</td><td>{name}</td><td>{esc(code)}</td><td class="m">{esc(where)}</td><td>{md_inline(why)}</td></tr>')
        o.append("</table></div>")
    return "".join(o)


def firmware_html():
    o = ['<h2>What the firmware needs</h2>', '<p>Not written yet; listed so the pin map above is known to be enough.</p><ul>']
    o += [f"<li>{md_inline(x)}</li>" for x in FIRMWARE]
    o.append("</ul>")
    return "".join(o)


def checks_html():
    o = ['<h2>Before power, with the meter</h2><ul class="check">']
    o += [f"<li>{md_inline(x)}</li>" for x in CHECKS]
    o.append("</ul>")
    return "".join(o)


def revk_html():
    return (f"<h2>Rev K, for approval</h2><p>What changed from Rev J, and why.</p><ul>"
            f"<li><strong>A brass frame.</strong> You asked for brass tubes. Tube cannot be rolled into Rev J's idler eyes, so the frame is six straight tubes, lapped and soldered: a spine of two rails between the motors, two rungs, a back bar, and a 4 mm axle that the idler drums turn on. The two idler screws and their washers are gone. Brass takes solder easily, and the rails carry the long wires inside.</li>"
            f"<li><strong>No paint, no skins.</strong> Your rule of 2026-11-09. Rev J's ivory skins and painted drum faces are gone; the drums are bare aluminium. Every part that shows is black as sold: the screen's board, both laser rangers and the charger are new black parts. The blue motor controller, the purple amplifier and the translucent-blue servo sit where nothing sees them. Rev J's blue charger, green boost and green ranger go to the shared bin; the drone's green 8×8 stays the drone's.</li>"
            f"<li><strong>A voice.</strong> The camera board's own microphone, a spare speaker and a spare amplifier: three more neck wires, ten in all, and nothing more to buy. The treads wait while it talks.</li>"
            f"<li><strong>The numbers.</strong> {D['width']:.0f} × {D['length']:.0f} × {D['height']:.0f} mm (Rev J 115 × 90 × 58), about {D['mass']:.0f} g (Rev J 328). The new screen is taller, so the head rides 1.5 mm higher; the ground clearance is {D['clear']:.1f} mm, under the screen's two tabs. {E['explore_h']:.1f} h exploring, {E['talking_h']:.1f} h talking, {E['charge_h']:.1f} h to charge.</li>"
            f"<li><strong>The carts.</strong> Delete the brass sheet and the M3 screws from your Amazon cart (five lines left, $76.11) and add the black ranger 2-pack ($17.99). The black charger and screen are one new DigiKey order ($26.45 before shipping). The black 8×8 comes from SB Components in the UK ($33 plus shipping): on 2026-11-10 it was the only shop with stock.</li></ul>"
            f"<h2>Earlier revisions</h2><p>Rev A, approved {APPROVED}: silicone tracks on a stainless ladder. Rev H, approved {APPROVED_H}: soldered brass treads on laser-cut aluminium drums like the reference's, an open stainless frame, ivory skins. Rev J, approved {APPROVED_J}: Rev H on 35 mm drums, with the drone's 8×8 ranger in the head in place of Rev I's LiDAR, which was too big. Revs B to G and I were set aside.</p>")


def page_html(form_svg, wiring_svg, jig_svg):
    return "\n".join([
        '<title>Mars Rover Build</title>',
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        f"<style>{STYLE}</style>",
        f"<style>{PAGE_TONES}</style>",
        '<style>.wrap{max-width:1100px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} '
        'td,th{min-width:0} .tw table{min-width:720px}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Mars rover &middot; step 1: the final build &middot; Rev K, for approval</div>',
        '<h1>A wide little desk tank on a brass spine, with a low head that looks, listens and talks</h1>',
        f'<div class="sub">How it looks, how it is wired, every part and every pin. {D["width"]:.0f} × {D["length"]:.0f} × {D["height"]:.0f} mm, about {D["mass"]:.0f} g. Rev K for approval ({REV_K}): a brass-tube frame, no paint and no skins, a voice. Rev J approved {APPROVED_J}. Nothing built; the drums and the Pololu parts are ordered, the rest waits on your yes.</div></div>',
        intro_html(),
        f'<figure class="sheet">{form_svg}<figcaption><strong>Form sheet. Print landscape on Letter at Actual size; it is page 1 of the PDF.</strong> Side, front and top views to one scale; the face and a cut through the servo at a larger scale; the frame as six tubes; the key numbers.</figcaption></figure>',
        decisions_html(),
        f'<figure class="sheet">{jig_svg}<figcaption><strong>Tread and drum at actual size, page 3 of the PDF.</strong> Printed at Actual size, the 50 mm bar measures 50 mm: lay rods and tubes on the shapes to cut them, solder planks on the stations, check a strip round a drum.</figcaption></figure>',
        f'<figure class="sheet">{wiring_svg}<figcaption><strong>Wiring sheet, page 2 of the PDF.</strong> Everything on the frame on the left, the ten neck wires in the middle, the head on the right, the budget along the bottom. Thick lines are wires you solder, thin ones the leads that come with a part; dots are joints; a hop is a crossing that does not touch.</figcaption></figure>',
        dims_html(),
        pins_html(),
        nets_html(),
        budget_html(),
        parts_html(),
        firmware_html(),
        checks_html(),
        revk_html(),
        f'<hr><p class="sub">Built by <code>docs/pages/gen/build_page.py</code>, which also writes <code>docs/FINAL_BUILD.md</code> and the PDFs; the dimensions, pins, nets, budget and parts live in that script. The wiring sheet\'s clearance check passes, and the drum, plank, frame, servo and head clearances are asserted. Sources: the reference page and its video, Pololu\'s pages and guides, the Seeed XIAO ESP32-S3 wiki, Adafruit\'s pages and guides for the charger with its boost (schematic read {REV_K}) and the screen, the ranger module\'s Amazon listing, Pimoroni\'s 8×8 breakout, Same Sky\'s speaker, the MAX98357A and AMC7135 datasheets, and the family\'s inventories and records. Colours read off each maker\'s photos {REV_K}. Nothing measured.</p>',
        '</div>'])


def final_build_md():
    o = ["# Mars rover: the final build (step 1, Rev K, for approval)", "",
         f"Paper design. Rev K, {REV_K}, for approval: Rev J (approved as drawn {APPROVED_J}) on a frame of six brass tubes, with nothing painted or skinned and a voice. A palm-sized tank, wider than long: brass treads you solder (a 3/32 in brass tube and two 1 mm rods to a plank, nickel-silver loops between them) on four bare aluminium drums cut on SendCutSend's laser, carrying a brass spine: two 3 mm rails between the motors, two rungs under them, a back bar, and a 4 mm axle the idler drums turn on. The servo stands on the rails; the screen, a laser ranger and the drone's flashlight hang on the axle; the cell, a black charger with its own 5 V boost, the switch and a black speaker sit on the rear deck; the blue motor controller and the purple amplifier hang under the motors, out of sight. The head is the black camera board, with its microphone, beside a black 8×8 laser ranger, on a brass cradle on the servo's horn, with a blinking warm-white beacon on top. Every part shows its own colour: brass, aluminium, steel, black. {D['width']:.0f} × {D['length']:.0f} × {D['height']:.0f} mm, about {D['mass']:.0f} g. **Nothing built; the drums and the Pololu parts are ordered, the rest waits on the yes.**",
         "", "Generated by `pages/gen/build_page.py`, which also writes the page `pages/mars-rover-build.html` and the PDFs in `pages/print/`; edit the script, not this file.", "",
         "## The reference", "",
         f"Huy Vector, [DIY Micro RC Spy Tank]({L['reference']}) and its [video]({L['video']}), read {TODAY}, the treads re-read {REV_E} from 3:30 to 5:30: a 1 mm copper-wire frame, two DC gear motors, three 16340 cells and two USB-C charging modules, a toy RC receiver board, an analog FPV camera, two 3 W LEDs on one 56 Ω resistor, a switch, and treads of short rods soldered side by side, tied with thread round four grooved aluminium drums that PCBWay machined (3:16 to 3:44). Ours keeps the open wire frame, the soldered treads, the camera, the light, the 16340 and USB-C charging, and becomes a wide little tank with a low turning head.",
         "", "## The decisions", ""]
    for head, text in DECISIONS:
        o += [f"### {head}", "", text, ""]
    o += ["## Dimensions", "", "| What | mm |", "| --- | ---: |"]
    o += [f"| {lab} | {D[k]:.1f} |" for k, lab in dims_rows()]
    o += ["", "| Part | g |", "| --- | ---: |"] + [f"| {n} | {m:.1f} |" for n, m, _ in MASS] + [f"| **Total** | **{D['mass']:.0f}** |", "",
          f"Centre of mass {D['cg'][1]:.0f} mm up, {abs(D['cg'][2]):.0f} mm {'behind' if D['cg'][2] < 0 else 'ahead of'} the middle; tips sideways at {D['tip_side']:.0f}°, backwards at {D['tip_back']:.0f}°.", "",
          "## The treads at actual size", "", "Page 3 of the PDF: cutting gauges for every rod, a plank end on, a strip of stations at the pitch, and a drum's circle with its pin stations. Print at Actual size and check the 50 mm bar.", "",
          "## Pin map, XIAO ESP32-S3 Sense (in the head)", "", "| Pin | GPIO | Job | Goes to |", "| --- | --- | --- | --- |"]
    o += [f"| {p} | {g} | {job} | {to} |" for p, g, job, to in PINS]
    o += ["", "I²C: " + " · ".join(f"{n} `{a_}`" for n, a_ in I2C) + ".", "",
          "Motor controller pins used: `VIN` and its `GND` (the cell after the switch), `M1A` `M1B` (left motor), `M2A` `M2B` (right motor), `VDD` (3.3 V from the head), `SDA`, `SCL`, one logic `GND`. Not wired: `VM`, `ERR`, `RST`, `JMP1`.", ""]
    o += ["## Every wire, and why", "", "| Net | From | To | Wire | Why |", "| --- | --- | --- | --- | --- |"]
    o += [f"| {n} | {fr} | {to} | {wire} | {why} |" for n, fr, to, wire, why in NETS]
    o += ["", "## The budget", "",
          f"Parked and watching {E['parked']:.0f} mA ({E['parked_h']:.1f} h); exploring with the camera streaming {E['explore']:.0f} mA ({E['explore_h']:.1f} h); with the flashlight at its 50 % cap {E['night']:.0f} mA ({E['night_h']:.1f} h). Everything at once would be {E['peak_all']:.0f} mA, near the cell's 2 A cut-out; ramps and caps keep real peaks near 1 A. 3.3 V rail at worst {E['rail3v3_peak']:.0f} mA of 700. Speed {E['speed_free']:.0f} mm/s free, about {E['speed']:.0f} on the desk. Charge {E['charge_h']:.1f} h at 500 mA.", ""]
    o += ["## Parts", "", "Rev K adds four black parts (one on Amazon, two from DigiKey, one from SB Components in the UK) and drops two lines from the Amazon cart: the brass sheet and the M3 screws. The drums and the Pololu parts are ordered. Owned parts are listed so they are not bought twice.", ""]
    for head, rows in PARTS:
        o += [f"### {head}", "", "| Qty | Part | Where | Price | Why, and what to check |", "| ---: | --- | --- | --- | --- |"]
        for qty, part, url, code, where, why in rows:
            name = f"[{part}]({url})" if url else part
            o.append(f"| {qty} | {name} | {code} | {where} | {why} |")
        o.append("")
    o += ["## What the firmware needs", ""] + [f"- {x}" for x in FIRMWARE] + ["", "## Before power, with the meter", ""] + [f"- {x}" for x in CHECKS]
    o += ["", "## Rev K, for approval", "",
          "- **A brass frame.** You asked for brass tubes. Tube cannot be rolled into Rev J's idler eyes, so the frame is six straight tubes, lapped and soldered: a spine of two rails between the motors, two rungs, a back bar, and a 4 mm axle that the idler drums turn on. The two idler screws and their washers are gone. The rails carry the long wires inside.",
          "- **No paint, no skins.** The rule of 2026-11-09. The skins and the painted drum faces are gone; the drums are bare aluminium. Every part that shows is black as sold: the screen's board, both laser rangers and the charger are new black parts. The blue motor controller, the purple amplifier and the translucent-blue servo sit where nothing sees them. Rev J's blue charger, green boost and green ranger go to the shared bin; the drone's green 8×8 stays the drone's.",
          "- **A voice.** The camera board's own microphone, a spare speaker and a spare amplifier: three more neck wires, ten in all, nothing more to buy. The treads wait while it talks.",
          f"- **The numbers.** {D['width']:.0f} × {D['length']:.0f} × {D['height']:.0f} mm (Rev J 115 × 90 × 58), about {D['mass']:.0f} g (Rev J 328); ground clearance {D['clear']:.1f} mm under the screen's tabs; {E['explore_h']:.1f} h exploring, {E['talking_h']:.1f} h talking, {E['charge_h']:.1f} h to charge.",
          "- **The carts.** Delete the brass sheet and the M3 screws from the Amazon cart (five lines left, $76.11) and add the black ranger 2-pack ($17.99). The black charger and screen are one new DigiKey order ($26.45 before shipping). The black 8×8 comes from SB Components in the UK ($33 plus shipping), the only shop with stock on 2026-11-10.",
          "", "## Earlier revisions", "",
          f"Rev A, approved {APPROVED}: silicone tracks on a stainless ladder. Rev H, approved {APPROVED_H}: soldered brass treads on laser-cut aluminium drums like the reference's, an open stainless frame, ivory skins. Rev J, approved {APPROVED_J}: Rev H on 35 mm drums, with the drone's 8×8 ranger in the head in place of Rev I's LiDAR. Revs B to G and I were set aside. Step 2, the [physics page]({PHYSICS_PAGE}) and [`PHYSICS.md`](PHYSICS.md), follows Rev J until Rev K is approved.", ""]
    return "\n".join(o)


def print_pdf(html, form_svg, wiring_svg, jig_svg):
    PRINT.mkdir(exist_ok=True)
    sheet_css = ("<style>@page{size:letter landscape;margin:7mm} html,body{background:#fff;margin:0}"
                 ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#ccc;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#f1f1f1;--warn:#000;--warn-soft:#eee}"
                 + RV_PRINT + "svg{width:262mm;height:auto;display:block;margin:0 auto}</style>")
    page_css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:10pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
                "figure.sheet{display:none} h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} h3{font-size:9pt;margin-top:10pt} p,ul,ol{max-width:none} table{font-size:9pt} th,td{padding:4pt 6pt}"
                ".tw table{min-width:0} td.m,th.m{white-space:normal} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid} ul.check{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        jobs = []
        for name, svg in (("form", form_svg), ("wiring", wiring_svg), ("jig", jig_svg)):
            src = d / f"{name}.html"; pdf = d / f"{name}.pdf"
            src.write_text(f"<!doctype html><meta charset=utf-8><title>{name}</title>" + sheet_css + svg)
            jobs.append((src, pdf))
        p_html = d / "p.html"; p_pdf = d / "p.pdf"
        head, tail = html.rsplit("</style>", 1)
        p_html.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + page_css + tail)
        jobs.append((p_html, p_pdf))
        for src, pdf in jobs:
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "mars-rover-build.pdf"
        subprocess.run(["pdfunite", str(d / "form.pdf"), str(d / "wiring.pdf"), str(d / "jig.pdf"), str(p_pdf), str(out)], check=True)
        shutil.copyfile(d / "form.pdf", PRINT / "mars-rover-form-sheet.pdf")
        shutil.copyfile(d / "wiring.pdf", PRINT / "mars-rover-wiring-sheet.pdf")
        shutil.copyfile(d / "jig.pdf", PRINT / "mars-rover-tread-jig.pdf")
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


PNG_CSS = ("<style>html,body{margin:0;background:#fff}:root{--bg:#EDEBE7;--paper:#FFFFFF;--ink:#16181C;--ink-2:#5A6068;--line:#CFCBC4;"
           "--brass:#8F6114;--brass-soft:#F2E6D2;--signal:#5A6068;--signal-soft:#ECEAE6;--warn:#8F6114;--warn-soft:#F2E6D2}")


def png(svg, name, outdir, size=(1360, 860)):
    """Render one sheet to a PNG for checking by eye (not part of the outputs)."""
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    src = outdir / f"{name}.html"
    src.write_text("<!doctype html><meta charset=utf-8>" + PNG_CSS + f"svg{{width:{size[0]}px;height:{size[1]}px}}</style>" + svg)
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--window-size={size[0]},{size[1]}",
                    f"--screenshot={outdir / (name + '.png')}", f"file://{src}"], check=True, capture_output=True, timeout=120)


def main():
    # mechanical clearances the drawing relies on
    ring = plank_ring()
    assert len(ring) == D["planks"] and abs(math.dist(ring[-1][:2], ring[0][:2]) - D["plank_p"]) < 0.01, "the tread must close at its pitch"
    edge = drum_pts(D["idler_z"])                           # the cutting file's outline against the planks seated on it
    for z, y, a in ring:
        if math.hypot(z - D["idler_z"], y - D["axle_y"]) > D["drum_r"] + 0.05:
            continue
        for k, piece in enumerate(rods_of(z, y, a)):
            assert clearance(edge, piece, 6.0) > rod_r(k) + 0.1, "every plank on a drum sits in a seat, clear of the teeth"
    assert D["face_r"] - D["drum_ra"] > 0.3, "the teeth must stay under the tread's face"
    hang = D["axle_y"] - D["drum_r"] - (D["pin_d"] / 2 + 0.05 + D["loop_wire"])
    assert hang > 0.1, f"a hanging loop must clear the desk ({hang:.2f})"
    assert abs(D["axle_y_frame"] - D["axle_y"]) < 0.01, "the axle, lying on the rails on the rungs, sits at the drums' height"
    assert D["rail_x"] + D["tube"] / 2 < D["mot_x_in"] - 0.8, "the rails pass between the motors' end tabs"
    assert D["rung_y"] + D["tube"] / 2 <= D["mot_y0"] + 0.01, "the motors sit on the rungs"
    assert D["collar_x0"] > D["rail_x"] + D["tube"] / 2 + 5, "the inner collars sit out by the drums, clear of the spine"
    assert D["drum_x0"] > D["spr_x0"] + 0.5, "the drum stands clear of the gearbox's boss"
    assert D["shaft_grip"] > 8.0, "the hub is crimped on most of the motor's shaft"
    assert abs(D["hub_l"] - DRUM.HUB_L) < 0.05, "cad/drum.py's order sheet and the rover agree on the hub"
    assert max(v for k, v in TUBE.items() if k != "three") < 200, "each tube comes out of one 200 mm length from the sets"
    assert D["mot_x_in"] > 5, "the two motors must leave a gap between their end tabs"
    assert -15.2 < -D["rail_x"] - D["tube"] / 2 and 5.2 > D["rail_x"], "the servo stands on both rails"
    assert D["piv_z"] + D["srv_w"] / 2 < D["idler_z"] - D["axle_d"] / 2 and D["piv_z"] - D["srv_w"] / 2 > D["bar_z"] + D["tube"] / 2, "the servo fits between the axle and the back bar"
    assert D["oled_z"] > D["idler_z"] + D["axle_d"] / 2, "the screen hangs in front of the axle"
    assert D["head_floor"] > D["oled_top"] + 1.5, "the head must turn clear of the screen's top edge"
    sweep = math.hypot(max(-HD["sh_x0"], HD["sh_x1"]), max(-HD["sh_z0"], HD["sh_z1"]))   # the head's corners, turning
    for xc, half, top in ((abs(D["tof_x"]), D["tof_w"] / 2, D["tof_cy"] + D["tof_h"] / 2 * math.cos(math.radians(D["tof_tilt"]))),
                          (abs(D["lamp_x"]), D["lamp_d"] / 2, D["lamp_cy"] + D["lamp_d"] / 2)):
        assert xc - half > D["oled_w"] / 2 + 0.3 and xc + half < D["pin_x0"] - D["guide"] - 0.5, "the ranger and the lamp sit between the screen and the treads"
        assert top < D["head_floor"] - 0.5, "the ranger's and the lamp's tops stay under the turning head"
    assert abs(D["tof_x"]) - D["tof_w"] / 2 > 15.2 + 1.0, "the ranger must clear the servo's body"
    assert D["tof_slant"] > 45, "the ranger must look past its 4 cm minimum"
    assert D["clear"] > 4.0, "ground clearance"
    assert D["holder_l"] / 2 < D["pin_x0"] - 1, "holder must sit between the tracks"
    assert D["holder_y0"] + D["holder_h"] < D["head_floor"] or D["holder_z1"] < D["piv_z"] - sweep - 2, "the cell holder stays clear of the turning head"
    assert D["chg_z0"] > -D["tr_end"] + 1.0 and D["chg_w"] / 2 < D["drum_x0"] - 1, "the charger stands inside the treads' length, between the drive drums"
    assert D["spk_z0"] > D["holder_z1"] and D["spk_z1"] < D["bar_z"] - D["tube"] / 2 and D["spk_z1"] < D["piv_z"] - sweep + 25, "the speaker lies on the spine between the holder and the back bar"
    assert D["tog_z1"] < D["piv_z"] - sweep - 2 or D["tog_y0"] + D["tog_h"] + D["tog_lever"] < D["head_floor"], "the switch's lever stays clear of the turning head"
    assert D["tog_l"] / 2 < D["oled_w"] / 2 - 1 and D["tog_y0"] + D["tog_h"] < D["oled_top"], "the screen hides the switch's body from the front"
    form_svg, wiring_svg, jig_svg = form_sheet(), wiring_sheet(), jig_sheet()
    html = page_html(form_svg, wiring_svg, jig_svg)
    OUT.write_text(html)
    (DOCS / "FINAL_BUILD.md").write_text(final_build_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "FINAL_BUILD.md")
    print(f"numbers: {D['width']:.1f} x {D['length']:.1f} x {D['height']:.1f} mm, {D['mass']:.1f} g, cg {tuple(round(c, 1) for c in D['cg'])}, tip side {D['tip_side']:.0f} back {D['tip_back']:.0f}; "
          f"speed {E['speed']:.0f} mm/s; parked {E['parked']:.0f} explore {E['explore']:.0f} night {E['night']:.0f} talking {E['talking']:.0f} peak {E['peak_all']:.0f} mA; tubes {TUBE}; "
          f"treads {D['tread_g']:.1f} g drums {D['drums_g']:.1f} g, 1 mm rod {D['rod1_mm']:.0f} mm, 3/32 tube {D['tube_mm']:.0f} mm, planks {D['planks']} a track at {D['plank_p']:.3f}, "
          f"loops {D['loops']} = {D['wire_m']:.2f} m, hang {hang:.2f}, hub {D['hub_l']:.1f} grip {D['shaft_grip']:.1f}, clear {D['clear']:.2f}")
    if "--png" in sys.argv:
        outdir = sys.argv[sys.argv.index("--png") + 1]
        png(form_svg, "form", outdir)
        png(wiring_svg, "wiring", outdir)
        png(jig_svg, "jig", outdir, (1310, 930))
        print("png in", outdir)
    if "--pdf" in sys.argv:
        print_pdf(html, form_svg, wiring_svg, jig_svg)


if __name__ == "__main__":
    main()
