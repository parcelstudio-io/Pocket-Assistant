"""Desk lighthouse, step 1 of the builder's rule: the final build first, the science after. Rev C: the wire frame, on a cell.

Writes, from the data at the top of this file (edit the script, not the outputs):
  docs/pages/desk-lighthouse-build.html              the page: form sheet, wiring sheet, templates, decisions, pins, nets, budget, parts
  docs/pages/print/desk-lighthouse-build.pdf          Letter, black only: form sheet, wiring sheet, templates (landscape), then the notes (portrait)
  docs/pages/print/desk-lighthouse-form-sheet.pdf     each sheet alone
  docs/pages/print/desk-lighthouse-wiring-sheet.pdf
  docs/pages/print/desk-lighthouse-templates.pdf      actual size: the coaster's holes, the deck, the shutter, the discs; the house's two U's at half size; a rod
  docs/FINAL_BUILD.md                                 the same decisions, pins, nets, budget and parts as Markdown

Rev A (2026-11-07) was an ivory 25 mm brass tube on a 38 mm brass cube with a text screen in its front. Rev B (2026-11-08) made the
tower a wire frame of four 1.5 mm brass rods round a turning 4 mm spine, with the screen in a small ivory door at the foot. Rev C
(2026-11-09) drops the screen at the builder's word and puts the build on a cell: a Nitecore 16340 stands in the ivory house behind
the motor, the charger board lies in the coaster's hollow with its USB-C at the back, and the power chain is drawn on both sheets.
The lantern (acrylic glass between a turned check ring and a spun vase cap, a fixed warm-white filament on a brass lamp post, a brass
shutter turning round it) is unchanged.

Reference: Huy Vector, "Lighthouse Desk Lamp", huyvector.org/decor-lamps/lighthouse-desk-lamp, read 2026-11-07: a parts list and
nothing else. The hop-drawing Router is imported from pocket_ai_assistant/edu/pages/gen/wiring_sheet.py as the other generators
do; the subclass adds the pin registry and the clearance check. Every number is a listing or datasheet figure or an owned-part
record; the check ring's thickness, the vase cap's height and the coaster's hollow are flagged to be measured. Nothing here has
been built."""
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
OUT = PAGES / "desk-lighthouse-build.html"
PRINT = PAGES / "print"
STYLE = (HERE / "page_style.css").read_text()

sys.path.insert(0, str(PROJECT.parent / "pocket_ai_assistant" / "edu" / "pages" / "gen"))
from wiring_sheet import Router as _Router  # noqa: E402

W, H = 1360, 860
TODAY = "2026-11-09"
REV = "D"
REV_C = "2026-11-09"
REV_A = "2026-11-07"
REV_B = "2026-11-08"
APPROVED = "2026-11-09"          # Rev C, as drawn; Rev D of the same evening awaits the yes
STATUS = f"drawn {TODAY} evening for approval"
PHYSICS_PAGE = "https://claude.ai/artifact/Cf7FTWNsZAdGYGXpTCj535"   # the step-2 artifact, Desk Lighthouse Physics

# ----------------------------------------------------------------------------- links (component names in prose, links on the word)
AMZ = "https://www.amazon.com/dp/"
GB = "https://grandbrass.com/"
L = {
    "reference": "https://www.huyvector.org/decor-lamps/lighthouse-desk-lamp",
    "filament_ref": "https://www.adafruit.com/product/5505",   # Adafruit's 26 mm rigid filament page: a tab at each end, the anode has the hole
    # to buy, Amazon
    "acrylic": AMZ + "B08ZM5BCQJ",         # uxcell clear rigid acrylic tube, 21 mm ID x 25 mm OD x 305 mm: the lantern glass
    "motor": AMZ + "B096S475NH",           # Augiimor 2 x N20 gear motor, 6 V 30 rpm, 3 mm D shaft: turns the shutter
    "filament": AMZ + "B0HBX2YW18",        # UGEFKMQ 10 x rigid ceramic LED filament, 26 mm, 3 V, >100 mA, 2700 K: the 26 mm child of the 38 mm listing below; ordered 2026-11-09
    "filament38": AMZ + "B0HBWV5631",      # UGEFKMQ 10 x 38 mm rigid ceramic LED filament, 3 V, 2700 K: the same listing's 38 mm child, the fallback if 26 mm is out
    "filament50": AMZ + "B0FR3BWZTM",      # QIROGKC 10 x 26 mm 2700 K ceramic filament rated 50 mA, $13.16: the cheaper, dimmer alternative (one 47 ohm instead of two)
    "reed": AMZ + "B0CHF29394",            # JESSINIE 20 x MKA-14103 glass reed switch, 2 x 14 mm, normally open, 7-35 AT
    "magnet": AMZ + "B0BQ3LPGZ1",          # N52 neodymium discs 3 x 1 mm: the index magnet under the collar
    "sheet015": AMZ + "B0006N6WJE",        # K&S 252 brass sheet, 0.015 in x 4 x 10 in: the house, the drum's floor, the collar, the bushing
    "tube58": AMZ + "B07DDFNNXY",          # K&S 8143 round brass tube, 5/8 in OD x 0.014 in wall x 12 in: the drum (the shutter)
    "coaster": AMZ + "B0D9DMK3L7",         # heavy brass coaster, 75 x 8 mm, flat top: bought 2026-11-06 as the satellite's base, this build's since 2026-11-09, delivered that day
    "pinvise": AMZ + "B09WRQPN58",         # pin vise with 0.5 to 3.0 mm twist bits: dropped 2026-11-09, a cordless drill is owned
    "glue": AMZ + "B003Y49R7G",            # Loctite Ultra Gel Control 4 g, the hologram's and the rover's tube; ordered 2026-11-09 (was the Zoro page zoro.com/i/G100464525)
    # to buy, Grand Brass (lamp parts; none of these is on Amazon)
    "checkring": GB + "check-rings/turned-brass-checkrings/?_bc_fsnf=1",   # CRT1-12X8: 1-1/2 in turned brass check ring, 1/8 IP slip (7/16 in hole): the gallery deck
    "vasecap": GB + "categories.php?category=655",                           # VA01-12: 1-1/2 in unfinished brass spun vase cap: the roof
    "ball": GB + "5-8in-diameter-1-8ips-threaded-tapped-blind-brass-ball-polished-nickle-finish/",   # BB0-58X18 (the unfinished brass one, listed beside this nickel page): the ventilator ball
    "nipple": GB + "1-2in-x-1-8ips-threaded-brass-hollow-nipple/",          # NI0-12X18BR: 1/2 in x 1/8 IP hollow brass nipple
    "nut": GB + "1-8-27ips-unfinished-brass-beaded-nut/",                    # 1/8 IP beaded brass nut, 9/16 in x 3/16 in: holds the nipple, carries the lamp post
    # to buy, Adafruit (the family's charger board; Cyber Dawn's two are both spoken for)
    "charger": "https://www.adafruit.com/product/6106",                      # bq25185 USB / DC / solar charger with 5 V boost: the cell's charger and the 5 V rail
    "charger_pins": "https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board/pinouts",
    # owned
    "controller": AMZ + "B0F888JQ91",      # Meshnology ESP32-C3 SuperMini (13 owned, 10 spare)
    "hbridge": AMZ + "B075S368Y2",         # Aideepen MX1508 dual H-bridge, 5-pack (5 owned, 4 spare)
    "cell": "https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery",   # Nitecore NL169 16340, 950 mAh, protected, button top (13 owned)
    "holder": AMZ + "B0CRGK889F",          # ACEIRMC 16340 holder with leads, 43 x 18 x 14 mm (10 owned, Cyber Dawn's stock)
    "diode": AMZ + "B079KJ46ZS",           # Chanzon SS14 Schottky, 100 owned
    "brass_tube": AMZ + "B0F2FKLC2N",      # M METERXITY brass tube set, 2 to 7 mm OD x 0.5 mm wall x 200 mm (3 sets owned): the spine
    "rod15": AMZ + "B01C6LUO5Q",           # K&S 9862 round brass rod, 1.5 mm x 300 mm, 5 a pack (about 90 rods owned): the four legs
    "rod10": AMZ + "B005WPB7YG",           # K&S 9861 round brass rod, 1.0 mm x 300 mm (10 owned): the lamp post
    "wire30": AMZ + "B073RDGTPB",          # CBAZY 30 AWG silicone wire
    "kapton": AMZ + "B072Z92QZ2",          # ELEGOO Kapton
    "resistors": AMZ + "B0F4P352BB",       # the resistor kit (47 ohm, 100 kohm)
    "button": AMZ + "B0FHW6HMG4",          # tactile buttons, 420 owned
    "paint": AMZ + "B000PIG3AS",           # Rust-Oleum Stops Rust gloss canvas white 7789830 (owned): the ivory
    "supermini_notes": "https://sigmdel.ca/michel/ha/esp8266/super_mini_esp32c3_en.html",
}

# ----------------------------------------------------------------------------- the numbers (mm unless said)
D = {
    # the base: the satellite's brass coaster, a thin top over a hollow with a pad. 80 g says the top is about 1.3 thick and the hollow about 6.7 deep: measure
    "disc_d": 75.0, "disc_t": 8.0, "disc_g": 80.0,
    "hollow_d": 71.0, "hollow_h": 6.7, "plate_t": 1.3, "ballast_g": 80.0,
    "notch_w": 40.0, "notch_h": 6.5,                          # the service bay sawn in the rim at the back: the charger's USB-C and the controller's, side by side
    "hole_d": 3.5, "hole_x": 7.0, "hole_y": 7.5,              # two holes in the coaster's top between the motor and the tray: the motor's and the reed's wires right, the cell's leads left
    # no house (Rev D, the builder's word): the motor, the tray, the reed and the magnet arm stand in the open on the coaster's top
    "btn_z": 3.4, "btn_hole": 3.6,                            # the button inside the rim at the front, its plunger through a hole this far up from the bottom edge
    "mot_w": 12.0, "mot_t": 10.0, "mot_l": 24.0, "gear_l": 9.0, "mot_z0": 2.0, "shaft_d": 3.0, "shaft_l": 9.0,
    "arm_len": 6.5, "arm_d": 1.0, "collar_up": 6.5,          # the magnet arm: 1 mm rod soldered to the spine, this far above the gearbox face
    "mag_d": 3.0, "mag_t": 1.0, "mag_r": 7.0,
    "reed_d": 2.0, "reed_l": 14.0, "reed_y": 7.5, "reed_gap": 2.0,   # the reed stands behind the motor; its top this far under the magnet's path
    "cell_d": 16.6, "cell_l": 34.1, "cell_g": 20.0,          # the Nitecore 16340, protected, button top
    "hold_w": 18.0, "hold_d": 17.0, "hold_h": 43.0, "hold_y0": 9.5, "hold_g": 6.0,   # the owned tray standing on end: 18 across, 14 plus the cell's bulge front to back, 43 tall
    # the cage: four 1.5 mm brass rods, coaster to roof
    "rod_d": 1.5, "leg_r0": 27.0, "leg_h": 168.0, "foot": 6.0, "hole_leg": 1.8, "hole_live": 2.3, "sleeve_od": 2.0, "boot": 3.0,
    # the spine: the owned 4 mm brass tube, over the motor's D shaft, up through the deck to the shutter's floor
    "tube_od": 4.0, "tube_id": 3.0, "tube_up": 0.5,
    # the gallery deck: a turned check ring, and the wheel glued on it that is the spine's top bearing: a ring of the 5/8 in tube, two 1 mm spokes, a ring of the owned 5 mm tube as the hub
    "deck_d": 38.1, "deck_t": 3.0, "deck_hole": 11.1, "bush_d": 15.88, "bush_hole": 4.2, "bush_t": 3.0, "hub_od": 5.0, "spoke_d": 1.0,
    # the lantern: open (Rev D), no glass; the rods are its bars and three of them carry the roof
    "ast_r": 14.5,                                           # the rods above the deck, from the axis
    "cap_rim": 34.5,                                         # the cap's rim above the deck: the open lantern's height
    "cap_d": 38.1, "cap_h": 12.5, "cap_t": 0.6, "cap_hole": 10.5,
    "nut_d": 14.3, "nut_h": 4.8, "nip_od": 10.3, "nip_id": 7.2, "nip_l": 12.7, "ball_d": 15.9, "ball_tap": 6.4,
    "fil_l": 26.0, "fil_w": 1.8, "tab": 3.0, "fil_gap": 2.1, # the filament: a tab at each end; its top tab this far under the nut
    "post_d": 1.0, "post_r": 3.1, "post_in": 5.0,            # the lamp post: 1 mm brass rod up inside the nipple's bore, down behind the lamp
    # the shutter: a 5/8 in brass tube on the spine, open 120 degrees
    "drum_od": 15.88, "drum_wall": 0.36, "drum_h": 35.0, "drum_z0": 2.0, "bar_d": 1.0, "floor_z": 0.5,   # two 1 mm bars across the drum's bottom, this far up, are its floor
    "win_deg": 120.0, "dwin_z0": 3.0, "dwin_h": 30.0,
    # the boards, in the coaster's hollow: the charger (terminal block and JST socket removed), the controller, the driver
    "chg_l": 29.2, "chg_w": 19.05, "chg_t": 4.8, "mx_l": 25.0, "mx_w": 20.0, "mx_t": 3.0, "c3_l": 22.5, "c3_w": 18.0, "c3_t": 5.3, "usb_w": 8.9, "usb_h": 3.3,
}

# the vase cap's profile: a cubic from the rim to the flat top (the usual spun shape), r and z' (above the deck top)
CAP_P = ((D["cap_d"] / 2, D["cap_rim"]), (D["cap_d"] / 2, D["cap_rim"] + 7.8), (13.0, D["cap_rim"] + D["cap_h"]), (D["cap_hole"] / 2, D["cap_rim"] + D["cap_h"]))


def cap_pt(t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = CAP_P
    u = 1 - t
    return (u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3,
            u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3)


def cap_inner_pt(t):
    """The inside surface: the outer point moved one sheet thickness along the inward normal."""
    (x, z), (xa, za) = cap_pt(t), cap_pt(min(1.0, t + 1e-3))
    tx, tz = xa - x, za - z
    n = math.hypot(tx, tz) or 1.0
    nx, nz = tz / n, -tx / n          # the outward normal points away from the axis and up
    if nx < 0:
        nx, nz = -nx, -nz
    return (x - nx * D["cap_t"], z - nz * D["cap_t"])


def cap_z_at_r(r, inner=True):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if cap_pt(mid)[0] > r:
            lo = mid
        else:
            hi = mid
    return (cap_inner_pt if inner else cap_pt)((lo + hi) / 2)[1]


# derived heights: z above the desk; z' above the deck's top (the lantern datum)
D["z_deck0"] = D["disc_t"] + D["leg_h"]
D["z_deck1"] = D["z_deck0"] + D["deck_t"]
D["leg_slope"] = (D["leg_r0"] - D["ast_r"]) / D["leg_h"]
D["leg_deg"] = round(math.degrees(math.atan(D["leg_slope"])), 1)
D["leg_top"] = round(cap_z_at_r(D["ast_r"] + D["rod_d"] / 2, inner=False), 1)   # three rods pass through the dome and are soldered flush with its outside
D["leg_top_live"] = round(cap_z_at_r(D["ast_r"] + D["rod_d"] / 2) - 1.0, 1)      # the live rod ends 1 mm short of the dome's inside, booted
D["leg_len"] = round(D["foot"] + D["leg_h"] / math.cos(math.atan(D["leg_slope"])) + D["deck_t"] + D["leg_top"] + 2, 0)   # cut, with 2 to trim
D["deck_mark"] = round(D["foot"] + D["leg_h"] / math.cos(math.atan(D["leg_slope"])), 1)
D["cage_d0"] = 2 * D["leg_r0"]
D["cage_d1"] = 2 * D["ast_r"]
D["z_cap_rim"] = D["z_deck1"] + D["cap_rim"]
D["z_cap_top"] = D["z_cap_rim"] + D["cap_h"]
D["nut_bot"] = D["cap_rim"] + D["cap_h"] - D["cap_t"] - D["nut_h"]    # z'
D["fil_top"] = D["nut_bot"] - D["fil_gap"] - D["tab"]
D["fil_bot"] = D["fil_top"] - D["fil_l"]
D["post_foot"] = D["fil_bot"] - D["tab"]
D["post_top"] = D["nut_bot"] + D["post_in"]
D["post_len"] = round(D["post_top"] - D["post_foot"] + D["post_r"], 0)
D["nip_top"] = D["nut_bot"] + D["nip_l"]
D["ball_bot"] = D["nip_top"] - D["ball_tap"]
D["ball_c"] = D["ball_bot"] + D["ball_d"] / 2
D["height"] = round(D["z_deck1"] + D["ball_bot"] + D["ball_d"], 1)
D["drum_top"] = D["drum_z0"] + D["drum_h"]
D["floor_top"] = D["drum_z0"] + D["floor_z"] + D["bar_d"]                   # the top of the two bars
D["bar_len"] = round(2 * math.sqrt((D["drum_od"] / 2 - D["drum_wall"]) ** 2 - (D["tube_od"] / 2) ** 2), 1)    # a bar tangent to the spine, wall to wall
D["spoke_len"] = round(2 * math.sqrt((D["bush_d"] / 2 - D["drum_wall"]) ** 2 - (D["hub_od"] / 2) ** 2), 1)    # a spoke tangent to the hub, rim to rim
D["tube_top"] = D["floor_top"] + D["tube_up"]                           # z'
D["z_mot_face"] = D["disc_t"] + D["mot_z0"] + D["mot_l"]
D["z_tube0"] = D["z_mot_face"] + 1.0
D["tube_len"] = round(D["z_deck1"] + D["tube_top"] - D["z_tube0"], 1)
D["z_collar"] = D["mot_z0"] + D["mot_l"] + D["collar_up"]              # above the coaster's top
D["reed_top"] = D["z_collar"] - D["mag_t"] - D["reed_gap"]
D["reed_bot"] = D["reed_top"] - D["reed_l"]
D["hold_y1"] = D["hold_y0"] + D["hold_d"]
D["cell_z0"] = (D["hold_h"] - D["cell_l"]) / 2                          # the cell sits between the tray's two springs
D["win_arc"] = round(math.pi * D["drum_od"] * D["win_deg"] / 360, 1)
D["drum_circ"] = round(math.pi * D["drum_od"], 1)
D["hw_rod"] = round(2 * D["bar_len"] + 2 * D["spoke_len"] + D["arm_len"], 0)   # mm of 1 mm rod in the spine's hardware

# masses (g) and where they sit (mm above the desk)
rho_br, rho_ac = 8.5e-3, 1.18e-3
_leg_each = D["leg_len"] * math.pi * (D["rod_d"] / 2) ** 2 * rho_br
MASS = [
    ("brass coaster", D["disc_g"], D["disc_t"] / 2),
    ("cell and holder, standing at the foot", D["cell_g"] + D["hold_g"], D["disc_t"] + D["hold_h"] / 2),
    ("motor, on its bed", 10.0, D["disc_t"] + D["mot_z0"] + D["mot_l"] / 2),
    ("magnet arm, magnet, reed, button, wires at the foot", math.pi * 0.25 * D["arm_len"] * rho_br + 0.1 + 2.0, D["disc_t"] + 20),
    ("charger, controller, driver, diode, resistors, wires in the hollow", 3 + 3 + 3 + 2.5, D["disc_t"] - 3.5),
    ("four rods, 1.5 mm brass", 4 * _leg_each, (D["disc_t"] + D["z_deck1"] + D["leg_top"]) / 2),
    ("spine, 4 mm brass tube", math.pi * (D["tube_od"] - 0.5) * 0.5 * D["tube_len"] * rho_br, (D["z_tube0"] + D["z_deck1"] + D["tube_top"]) / 2),
    ("gallery, turned check ring", math.pi * ((D["deck_d"] / 2) ** 2 - (D["deck_hole"] / 2) ** 2) * D["deck_t"] * rho_br, D["z_deck0"] + D["deck_t"] / 2),
    ("bearing wheel: two tube rings and two 1 mm spokes", (math.pi * (D["bush_d"] - D["drum_wall"]) * D["drum_wall"] + math.pi * (D["hub_od"] - 0.5) * 0.5) * D["bush_t"] * rho_br + 2 * math.pi * 0.25 * D["spoke_len"] * rho_br, D["z_deck1"] + D["bush_t"] / 2),
    ("shutter drum and its two bars", math.pi * (D["drum_od"] - D["drum_wall"]) * D["drum_wall"] * D["drum_h"] * rho_br + 2 * math.pi * 0.25 * D["bar_len"] * rho_br, D["z_deck1"] + D["drum_top"] / 2),
    ("filament, lamp post, two wires", 1.5, D["z_deck1"] + 25),
    ("vase cap", 1600 * D["cap_t"] * rho_br, D["z_cap_rim"] + D["cap_h"] * 0.6),
    ("nut and nipple", 7.0, D["z_deck1"] + D["nut_bot"] + 6),
    ("brass ball", 4 / 3 * math.pi * (D["ball_d"] / 2) ** 3 * rho_br, D["z_deck1"] + D["ball_c"]),
]
D["mass"] = sum(m for _, m, _ in MASS)
D["cg"] = sum(m * z for _, m, z in MASS) / D["mass"]
D["tip_deg"] = math.degrees(math.atan2(D["disc_d"] / 2, D["cg"]))
D["push_n"] = D["mass"] / 1000 * 9.81 * (D["disc_d"] / 2) / D["height"]
mb = D["mass"] + D["ballast_g"]
D["cg_b"] = (D["cg"] * D["mass"] + D["ballast_g"] * D["disc_t"] / 2) / mb
D["tip_deg_b"] = math.degrees(math.atan2(D["disc_d"] / 2, D["cg_b"]))
D["push_n_b"] = mb / 1000 * 9.81 * (D["disc_d"] / 2) / D["height"]
D["lantern_g"] = sum(m for n, m, _ in MASS if n in ("gallery, turned check ring", "bearing wheel: two tube rings and two 1 mm spokes", "shutter drum and its two bars", "filament, lamp post, two wires", "vase cap", "nut and nipple", "brass ball"))
# each rod as a fixed-fixed strut: Euler load and the cage's sway stiffness, for the record
_E, _I, _A = 100e3, math.pi * D["rod_d"] ** 4 / 64, math.pi * (D["rod_d"] / 2) ** 2
D["rod_euler_n"] = round(math.pi ** 2 * _E * _I / (0.5 * D["leg_h"]) ** 2, 1)
D["rod_load_n"] = round(D["lantern_g"] / 1000 * 9.81 / 4, 3)
D["cage_k"] = round(4 * 12 * _E * _I / D["leg_h"] ** 3 + 2 * _E * _A / D["leg_h"] * math.sin(math.atan(D["leg_slope"])) ** 2, 2)   # N/mm at the deck

# ----------------------------------------------------------------------------- the electrical budget
E = {
    "v_rail": 5.0, "fil_vf": 3.0, "fil_rated": 100.0, "r_each": 47.0, "n_par": 2,
    "mot_v": 6.0, "mot_rpm": 30.0, "mot_ma": 35.0, "mot_stall": 400.0,
    "rpm_target": 8.0, "c3_avg": 20.0, "c3_peak": 300.0, "mx_q": 1.0, "lamp_duty": 0.7,
    "v_cell": 3.7, "v_cell_full": 4.2, "v_cell_low": 3.3, "cell_mah": 950.0, "boost_eff": 0.88, "boost_q": 1.0, "chg_ma": 500.0, "diode_v": 0.15,
    "r_div": 100.0,   # kohm, two of them: the cell-voltage divider
}
E["r_lamp"] = E["r_each"] / E["n_par"]
E["i_lamp_max"] = (E["v_rail"] - 0.05 - E["fil_vf"]) / E["r_lamp"] * 1000
E["i_lamp"] = E["i_lamp_max"] * E["lamp_duty"]
E["p_res_each"] = (E["i_lamp_max"] / 1000 / E["n_par"]) ** 2 * E["r_each"]
E["p_short_each"] = (E["v_rail"] / E["r_lamp"] / E["n_par"]) ** 2 * E["r_each"]      # if the live rod ever touched the frame
E["rpm_5v"] = E["mot_rpm"] * E["v_rail"] / E["mot_v"]
E["duty_mot"] = E["rpm_target"] / E["rpm_5v"]
E["period"] = 60 / E["rpm_target"]
E["pass_s"] = E["period"] * D["win_deg"] / 360
E["mot_avg"] = E["mot_ma"] * E["duty_mot"]
E["rail_typ"] = E["mot_avg"] + E["i_lamp"] + E["mx_q"]                    # mA on the 5 V rail, beacon on, lamp at the everyday level
E["rail_lamp"] = E["i_lamp"] + E["mx_q"]                                   # lamp alone, shutter parked
E["rail_peak"] = E["mot_ma"] + E["i_lamp_max"] + E["mx_q"]                 # the most the boost is asked for in normal running
E["rail_jam"] = E["mot_stall"] + E["i_lamp_max"] + E["mx_q"]               # a jammed shutter, until the firmware notices
E["lamp_w"] = E["i_lamp_max"] / 1000 * E["fil_vf"]
E["rod_mohm"] = round(6.4e-8 * (D["leg_len"] / 1000) / (_A * 1e-6) * 1000, 1)   # one rod's resistance in milliohms


def cell_ma(rail_ma, ctrl_ma):
    """Current from the cell: the rail through the boost, plus the controller straight from the cell, plus the boost's own keep."""
    return rail_ma * E["v_rail"] / E["boost_eff"] / E["v_cell"] + ctrl_ma + E["boost_q"]


E["cell_typ"] = cell_ma(E["rail_typ"], E["c3_avg"])
E["cell_lamp"] = cell_ma(E["rail_lamp"], E["c3_avg"])
E["cell_peak"] = cell_ma(E["rail_peak"], E["c3_peak"])
E["cell_idle"] = E["c3_avg"] + 0.04                                        # boost off: the controller and the divider
E["h_beacon"] = E["cell_mah"] * 0.9 / E["cell_typ"]
E["h_lamp"] = E["cell_mah"] * 0.9 / E["cell_lamp"]
E["h_idle"] = E["cell_mah"] * 0.9 / E["cell_idle"]
E["h_charge"] = E["cell_mah"] / E["chg_ma"] * 1.2
E["i_div_ua"] = E["v_cell_full"] / (2 * E["r_div"]) * 1000                 # microamps in the divider
E["v_sense_full"] = E["v_cell_full"] / 2

# ----------------------------------------------------------------------------- the contract: ESP32-C3 SuperMini pins
PINS = [
    ("5V", "power in: the cell through the SS14, 3.5 to 4.0 V, which the board's own regulator turns into 3.3 V", "SS14 cathode; anode to the charger's BAT pad", "V5C"),
    ("GND", "one ground", "charger G · driver GND · reed leg 2 · button leg 2 · the back-right rod's foot (the lamp's return) · the divider's bottom", "GND"),
    ("GPIO4", "the cell's voltage, ADC, through two 100 kΩ (half the cell: 2.1 V at full)", "the divider's middle", "SENSE"),
    ("GPIO7", "the 5 V boost's enable: high to run the motor and the lamp, low to sleep", "charger EN pad", "EN"),
    ("GPIO0", "shutter motor, LEDC PWM at 20 kHz (silent), ramped so the boost never sees a step", "driver IN1", "IN1"),
    ("GPIO1", "shutter direction and brake", "driver IN2", "IN2"),
    ("GPIO3", "lamp, LEDC PWM at 5 kHz", "driver IN3", "IN3"),
    ("GPIO6", "index: the reed switch, internal pull-up, closes once a turn", "reed leg 1; leg 2 to GND", "REED"),
    ("GPIO10", "the button inside the coaster's rim at the front, active low, internal pull-up (the family's pin)", "button leg 1; leg 2 to GND", "BTN"),
    ("GPIO2, 8, 9", "strapping pins: left alone (GPIO8 is the blue LED, held high)", "nothing", ""),
    ("GPIO5, 20, 21", "free", "nothing", ""),
    ("USB-C", "flashing and the console only; the diode keeps its 5 V out of the cell", "a computer's cable, in the notch at the back beside the charger's port", "USB"),
]

# ----------------------------------------------------------------------------- every wire, and why
NETS = [
    ("CELL", "holder's two leads", "the charger's battery pads (where its JST socket was)", "the holder's own leads, 60 mm, down through the left hole",
     f"The cell, a protected Nitecore 16340, button top, never soldered: it drops into the owned holder standing on the coaster behind the motor, and the holder's leads go down through the coaster's top to the charger's battery pads. The JST socket comes off the charger so the board lies flat in the hollow; the holder is empty while the iron is out. Meter the leads for polarity before the cell goes in."),
    ("VBAT", "charger BAT pad", "SS14 anode · the divider's top", "30 AWG, 30 mm",
     f"The cell's own voltage, {E['v_cell_low']:.1f} to {E['v_cell_full']:.1f} V, out of the charger: it feeds the controller through the diode and the divider that measures it. Plugged in, the charger's power path feeds this pad from the cable first and the cell with what is left (the [charger page]({L['charger']}) says so), so the lighthouse runs while it charges."),
    ("V5C", "SS14 cathode (band)", "controller 5V pin", "30 AWG, 30 mm",
     f"The controller's power: the cell less {E['diode_v']:.2f} V, 3.5 to 4.0 V, which its own regulator turns into 3.3 V, exactly as the satellite is wired. The diode is for the controller's own USB-C: on the SuperMini the 5V pin is VBUS with no diode, so without it a flashing cable would push 5 V into a lithium cell. With it, flash whenever you like."),
    ("V5", "charger 5V pad (the boost)", "driver VCC (+) pad", "30 AWG, 40 mm",
     f"The 5 V rail for the motor and the lamp, from the charger's TPS61023 boost: 1 A rated, {E['rail_peak']:.0f} mA asked of it at most in normal running, {E['rail_typ']:.0f} typical. The boost stalls if a load over 200 mA is switched onto it in one step, so the firmware ramps the motor's PWM up over 0.2 s and never starts the motor and the lamp in the same instant. A jammed shutter would ask {E['rail_jam']:.0f} mA; the reed's silence catches it first."),
    ("EN", "GPIO7", "charger EN pad", "30 AWG, 40 mm",
     f"The boost's enable: high while the shutter turns or the lamp is lit, low otherwise, so a sleeping lighthouse costs the cell {E['cell_idle']:.0f} mA instead of {E['cell_lamp']:.0f}. The pad is pulled up to the cell rail on the board (100 kΩ, the satellite's reading); 3.3 V logic drives it either way."),
    ("GND", "controller GND pin", "charger G pad · driver GND pad · reed leg 2 · button leg 2 · the back-right rod's foot · the divider's bottom", "30 AWG",
     "One ground. The charger's G, the driver's GND and the controller's GND pins are tied; the lamp returns by way of the back-right rod, soldered to a ground wire at its foot in the hollow. The back-right rod, the coaster, the deck and the roof may all sit at ground; only the back-left rod is live, and it is sleeved."),
    ("IN4", "driver IN4 pad", "driver GND pad", "30 AWG, 10 mm",
     "Holds channel B's second input low so OUT3 alone does the switching. A floating input on this chip is undefined. OUT4 is left unconnected: the lamp returns through the frame, not through the half-bridge."),
    ("SENSE", "charger BAT pad, through 100 kΩ", "GPIO4; and GPIO4 through 100 kΩ to GND", "two resistors in the hollow, 30 AWG, 30 mm",
     f"The cell's voltage, halved: {E['v_sense_full']:.2f} V at a full cell, inside the C3's ADC range. {E['i_div_ua']:.0f} µA through the pair, nothing against the cell. Below {E['v_cell_low']:.1f} V the firmware dims the lamp, parks the shutter and then shuts the boost off; the cell's own protection is the last word at 2.8 V."),
    ("IN1", "GPIO0", "driver IN1", "30 AWG, 30 mm",
     f"The shutter's speed: PWM at 20 kHz, above hearing. About {E['duty_mot'] * 100:.0f} % duty gives {E['rpm_target']:.0f} rpm from a 30 rpm (6 V) gearmotor on 5 V; the firmware trims the duty from the reed's period so a revolution takes {E['period']:.1f} s whatever the motor's batch. The pin floats for a moment at boot and the spine may twitch once; harmless."),
    ("IN2", "GPIO1", "driver IN2", "30 AWG, 30 mm",
     "Direction and brake. Low while IN1 runs: forward, the way that brings the window round to the front after the index. Both high: the bridge shorts the motor and the shutter stops within a degree or two of where the reed said it was. Reverse is there for the parking move and nothing else."),
    ("IN3", "GPIO3", "driver IN3", "30 AWG, 30 mm",
     f"The lamp's brightness: PWM at 5 kHz into channel B. {E['lamp_duty'] * 100:.0f} % by default, 100 % on a long press, 0 when the shutter closes. The driver's channel B is a plain high-side switch here; it never sees a motor."),
    ("MOT", "driver OUT1, OUT2", "motor terminals", "2 x 30 AWG, 50 mm, up through the right hole",
     f"The gearmotor, about {E['mot_ma']:.0f} mA turning, {E['mot_stall']:.0f} mA if the shutter ever jams; the driver is good for 1.5 A a channel and has its own flyback diodes. The motor's two tabs are bent flat outward before soldering so the can stands on its bed; heat-shrink on both."),
    ("LAMP", "driver OUT3", f"two 47 Ω in parallel ({E['r_lamp']:.1f} Ω), then the back-left rod's foot; at the top a wire from the rod's tip to the filament's + tab", f"30 AWG, 40 mm in the hollow; the rod itself, {D['leg_len']:.0f} mm; 30 AWG, 30 mm under the roof",
     f"A 3 V, 100 mA filament from the 5 V rail: {E['r_lamp']:.1f} Ω drops the other two volts and sets {E['i_lamp_max']:.0f} mA flat out, inside the rating; each resistor dissipates {E['p_res_each'] * 1000:.0f} mW of its 250. PWM takes it to {E['i_lamp']:.0f} mA for everyday. The back-left rod carries it up: {E['rod_mohm']:.1f} mΩ of brass, sleeved in white heat-shrink where it passes the coaster and the deck and booted at its tip, so it touches no other brass. The + tab is the one with the hole in it (the [filament page]({L['filament_ref']})); the diode test lights it faintly. If a sleeve ever failed, 5 V across the resistors would be {E['p_short_each'] * 1000:.0f} mW each: warm, not a fire, and the meter check before power catches it."),
    ("LAMP−", "filament − tab", "the lamp post (1 mm brass rod), the nut, a wire to the back-right rod's tip; the rod; a wire from its foot to controller GND", "the post, 42 mm; 30 AWG, 30 mm under the roof; the rod; 30 AWG, 40 mm in the hollow",
     "The lamp's return. A rigid filament has a tab at each end, so the lower tab is soldered to the foot of a 1 mm brass rod that stands behind the lamp and is soldered up inside the nipple's bore: that rod holds the lamp and carries its current. A wire from the nut goes to the back-right rod's tip under the roof, and the rod takes it down to the hollow. Solder at both ends of every rod, so no joint depends on glue or a thread for contact."),
    ("REED", "GPIO6", "reed leg 1", "30 AWG, 50 mm, up through the right hole",
     f"The index. A 3 × 1 mm magnet under a 1 mm brass arm on the spine passes {D['reed_gap']:.0f} mm over the reed's top end once a revolution and closes it for about {E['period'] * 14 / 360:.2f} s. The firmware times revolutions from it, parks the window on it, and reads a jammed shutter from its silence. The glass is 2 mm thick and 14 long: it stands behind the motor on Kapton, its top {D['reed_top']:.1f} mm above the coaster, in front of the cell."),
    ("REED−", "reed leg 2", "controller GND pin", "30 AWG, 50 mm", "The reed's return. Its top lead is bent down along the glass in heat-shrink; both wires go down beside the motor to the right hole."),
    ("BTN", "GPIO10", "button leg 1", "30 AWG, 40 mm, inside the hollow", "Short press: rotation on or off (off parks the window facing you). Long press: lamp off, low, full; off also closes the shutter. Internal pull-up; no resistor."),
    ("BTN−", "button leg 2", "controller GND pin", "30 AWG, 40 mm", f"The button's return. The 6 mm tactile is glued inside the coaster's rim at the front, its plunger through a {D['btn_hole']:.1f} mm hole {D['btn_z']:.1f} mm up from the bottom edge: press the front of the coaster."),
    ("CHG", "any USB-C adapter or a computer", "charger USB-C, in the notch at the back", "the cable",
     f"Charging: {E['chg_ma']:.0f} mA with the board's jumper cut (its default is 1 A, too much for a 950 mAh cell), about {E['h_charge']:.1f} h from empty, the orange LED while it charges; the chip's own 6 h timer ends it. Plugged in, the power path runs the lighthouse from the cable and fills the cell with the rest. Any phone adapter."),
    ("USB", "a computer", "controller USB-C, in the same notch", "the cable",
     "Flashing and the console only, through the second port in the notch; the diode keeps its 5 V out of the cell. The lighthouse runs on its cell while it is flashed."),
]

# ----------------------------------------------------------------------------- parts: owned items stay off the shopping list
PARTS = [
    ("Ordered on Amazon 2026-11-09: eight lines in five orders, $122.64 with tax and delivery; two of them dropped that evening (the sheet cancelled, the acrylic tube to return)", [
        ("0 (to return)", "clear acrylic tube, 25 mm OD × 21 mm ID × 305 mm", L["acrylic"], "uxcell, Amazon B08ZM5BCQJ", "$8.99; ordered 2026-11-09 (order 114-1438198-3243448) and shipped the same day; rejected that evening: return it when it comes 11-11, or keep it as stock",
         "Rev C's lantern glass, dropped in Rev D at the builder's word (\"so ugly, never\"). The lantern is open: the shutter turns in the air between the rods, and since the glass was a window and not a lens nothing optical is lost."),
        ("1 of 2", "N20 gearmotor, 6 V, 30 rpm, 3 mm D shaft", L["motor"], "Augiimor 2-pack, Amazon B096S475NH", "$15.99 the pair; ordered 2026-11-09 (order 114-1438198-3243448), shipped the same day, arriving Wed 11-11",
         f"Turns the shutter from the foot of the tower. 12 × 10 × 24 mm body plus a 9 mm shaft, 30 to 40 mA. On 5 V it would run {E['rpm_5v']:.0f} rpm; PWM holds it at {E['rpm_target']:.0f}, one revolution in {E['period']:.1f} s. It stands shaft-up on a 2 mm bed of hot glue on the coaster's top, its shaft on the axis; the spine slides over the D shaft with a drop of gel glue. Its two tabs bend flat outward so the can sits level. The second motor is the spare. **Incoming check:** 3 mm D shaft, and it runs at 3 V on the bench supply."),
        ("1 of 10", "LED filament, 26 mm, 3 V 100 mA, warm white 2700 K", L["filament"], "UGEFKMQ 10-pack, Amazon B0HBX2YW18, the 26 mm 2700 K variant of the listing whose 38 mm child is the fallback", "$25.40 plus $4.98 delivery; ordered 2026-11-09 (order 114-6111517-7569023), arriving Fri 11-27, the last box",
         f"The lamp: a strip of LEDs, the kind inside an Edison bulb, with a metal tab at each end; the tab with the hole is + (the [26 mm filament page]({L['filament_ref']}) says so of its own). It stands on the axis, soldered by its lower tab to the lamp post and fed at its upper tab by a wire. 2700 K, not the family's 2200 K spare (amber; a lighthouse lamp is warm white, and the rule is white or warm white light). {E['i_lamp_max']:.0f} mA flat out through {E['r_lamp']:.1f} Ω, {E['lamp_w'] * 1000:.0f} mW, in the open air. If 26 mm is out of stock, the [38 mm 2700 K pack]({L['filament38']}) fits with the shutter cut 12 mm taller and the post 12 longer; nine spare either way. The DLEDMOP listing first named here turned out to be its 18.5 mm item with no size picker, so the cart holds this one; a [26 mm 2700 K pack rated 50 mA]({L['filament50']}) is cheaper and sooner but would want one 47 Ω instead of two and give half the light."),
        ("1 of 20", "glass reed switch, 2 × 14 mm, normally open, 7 to 35 AT", L["reed"], "JESSINIE MKA-14103 20-pack, Amazon B0CHF29394", "$9.82; ordered 2026-11-09 (order 114-1438198-3243448), shipped the same day, arriving Wed 11-11",
         f"The index. Stands behind the motor, in front of the cell, in the open, on Kapton, its top {D['reed_gap']:.0f} mm under the magnet's path. Pick the most sensitive of the twenty on the bench (the one that closes farthest from the magnet). Glass: never bend a lead at the seal."),
        ("1 of 100", "neodymium disc magnets, 3 × 1 mm, N52", L["magnet"], "Amazon B0BQ3LPGZ1 (100 or more a pack)", "$19.49; ordered 2026-11-09 (order 114-1438198-3243448), shipped the same day, arriving Wed 11-11",
         f"The index magnet, glued under the tip of the 1 mm brass arm on the spine, {D['mag_r']:.0f} mm from the axis, opposite the window's middle so the reed fires as the window faces front. One is enough; a second stacked on it doubles the field if the reed is lazy. It shows as a black dot under a thin brass arm."),
        ("0 (cancelled)", "brass sheet, 0.015 in (0.4 mm), 4 × 10 in", L["sheet015"], "K&S 252, Amazon B0006N6WJE", "$5.31 plus $9.49 delivery; ordered 2026-11-09 (order 114-5648832-0318640); cancelled by the builder that evening (confirm with Amazon's cancellation mail)",
         "Rev C's keeper's house and its three sheet-cut discs. Dropped: the builder does not fold brass sheet round components, so Rev D has no house, and the shutter's floor, the magnet's collar and the deck's bushing are made from the 1 mm rod and the tubes already on the bench (below)."),
        ("1", "brass round tube, 5/8 in OD × 0.014 in wall × 12 in", L["tube58"], "K&S 8143, Amazon B07DDFNNXY", "$9.89; ordered 2026-11-09 (order 114-7188491-2312247), arriving 11-18 to 11-20",
         f"The shutter: a {D['drum_h']:.0f} mm length with a {D['win_deg']:.0f}° window sawn out ({D['win_arc']:.1f} mm of the {D['drum_circ']:.1f} mm circumference, {D['dwin_h']:.0f} mm tall); two 1 mm bars across its bottom, {D['floor_z']:.1f} mm up, soldered to the spine's flanks and to the wall, are its floor. A second piece, a {D['bush_t']:.0f} mm ring from the same tube, is the rim of the deck's bearing wheel. 0.36 mm wall: saw gently, file square, polish. The template sheet has the window at actual size."),
        ("0 (dropped)", "pin vise with 0.5 to 3.0 mm twist bits", L["pinvise"], "Amazon B09WRQPN58; dropped from the cart 2026-11-09 at the builder's word", "none",
         f"Dropped: a 20 V cordless drill is owned (bought 2026-10-11, missing from the inventory until 2026-11-09), so the builder took this set out of the cart on 2026-11-09. The holes go to that drill at its slowest, with metric bits from its case or a small bit set if the case has none under 3 mm: the coaster's four rod holes (1.8, one 2.3), two wire holes (3.5) and the button's 3.6 in the rim, the deck's four rod holes, the roof's three 1.8 holes. Centre-punch first; brass grabs a twist bit, so a slow speed and a light hand."),
        ("1 tube", "gel super glue, 4 g", L["glue"], "Loctite Ultra Gel Control, Amazon B003Y49R7G (it was waiting in the builder's Saved for later; the hologram's and the rover's tube)", "$3.29; ordered 2026-11-09 (order 114-1965907-0721062), arriving Sat 11-14",
         "One tube for three builds. Here: the rods' feet under the coaster, the deck to the rods, the wheel's rim to the deck, the magnet under its arm, the reed to the coaster, the spine on the D shaft, the tray to the coaster, the button inside the rim. No epoxy is owned and none is needed."),
    ]),
    ("Grand Brass Lamp Parts: five lines, one order, placed by the builder on 2026-11-09 by their word (no confirmation mail had come by that evening, so no order number here; none of these is on Amazon)", [
        ("1", "turned brass check ring, 1-1/2 in, 1/8 IP slip (7/16 in hole)", L["checkring"], "Grand Brass CRT1-12X8, unfinished", "about $1.60",
         f"The gallery deck: a solid turned brass disc, Ø38.1, about 3 mm thick (measure it; the drawing assumes 3), with an 11 mm hole already in its middle that the spine passes through. Threaded down the four rods to {D['leg_h']:.0f} mm above the coaster and glued to them. Four holes to drill at r {D['ast_r']:.1f}: 1.8 mm for three rods, 2.3 for the sleeved live one. No railing: the slab is the gallery."),
        ("1", "spun brass vase cap, 1-1/2 in, 1/8 IP slip hole", L["vasecap"], "Grand Brass VA01-12, unfinished (the vase-cap listing, 1-1/2 in)", "about $2.50",
         f"The roof. A shallow spun dome Ø38.1, about 12.5 mm tall (measure; drawn 12.5), the same diameter as the deck, so the lantern is an open drum of air between two brass discs. Three Ø1.8 holes drilled in its dome at r {D['ast_r']:.1f}: the three grounded rods pass through and are soldered flush from outside, so the roof is part of the frame; the live rod ends {D['leg_top_live']:.0f} mm above the deck under it, booted. Its centre hole takes the nipple."),
        ("1", "brass ball, 5/8 in, 1/8 IP blind tap", L["ball"], "Grand Brass BB0-58X18, unfinished brass (listed beside the nickel one)", "about $1",
         f"The ventilator ball on the roof, the one silhouette a lighthouse needs after its lantern. Solid, {next(m for n, m, _ in MASS if n == 'brass ball'):.0f} g, screwed onto the nipple until it meets the cap. Unfinished brass, polished by hand."),
        ("1", "hollow brass nipple, 1/2 in long, 1/8 IP", L["nipple"], "Grand Brass NI0-12X18BR", "about $1",
         f"Through the cap's hole: the ball on top, the nut underneath. 12.7 mm long; file it shorter if the ball will not seat. The lamp post is soldered up inside its bore, {D['post_in']:.0f} mm deep."),
        ("1", "beaded brass nut, 1/8 IP, 9/16 in × 3/16 in", L["nut"], "Grand Brass, unfinished", "about $1",
         "Inside the cap on the nipple: it clamps the roof's hardware, and the lamp's return wire is soldered to it. The nut, the nipple and the post are one piece of brass to the meter."),
    ]),
    ("Still to buy: the charger, one line (Adafruit, or DigiKey 1528-6106-ND; the DigiKey order of 2026-11-09 was the rover's and does not hold it)", [
        ("1", "bq25185 USB / DC / solar charger with 5 V boost", L["charger"], "Adafruit 6106 or DigiKey 1528-6106-ND, in stock at both on 2026-11-09", "$8.95; not ordered as of 2026-11-09 evening",
         f"The cell's charger and the 5 V rail in one 29 × 19 mm board, the family's charger (Cyber Dawn's and the satellite's; both of theirs are spoken for, so this is a third). USB-C in; power path, so plugged in the lighthouse runs from the cable and the cell fills with the rest; the charge-rate jumper on the back cut for {E['chg_ma']:.0f} mA (its default is 1 A); a TPS61023 boost, 5 V at 1 A, that the firmware switches off through EN when nothing moves. The screw terminal and the JST socket come off so it lies {D['chg_t']:.1f} mm flat in the hollow with its port in the notch (the [pinouts]({L['charger_pins']}) name every pad). **Incoming check:** cut the jumper before the cell meets it."),
    ]),
    ("Owned: electronics and power", [
        ("1 of 13", "Nitecore 16340 cell, 950 mAh, protected, button top", L["cell"], "Nitecore NL169, IMR Batteries orders of 2026-10-16", "owned",
         f"The battery, the family's cell: 16.6 × 34.1 mm, 20 g, protection under the wrap, 2 A limit, 4.20 V termination. Standing in the holder behind the motor, in the open; it lifts straight out. About {E['h_beacon']:.0f} h of beacon with the lamp at {E['lamp_duty'] * 100:.0f} %, {E['h_lamp']:.0f} h of lamp alone, {E['h_idle'] / 24:.0f} days asleep; {E['h_charge']:.1f} h to charge. **Incoming check:** 3.6 to 4.1 V on the meter, button top +; nothing else. Never solder to it."),
        ("1 of 10", "16340 holder with leads", L["holder"], "ACEIRMC, Amazon B0CRGK889F (Cyber Dawn's stock)", "owned",
         f"A 43 × 18 × 14 mm black plastic tray with two spring contacts and two leads, standing on end on the coaster's top behind the motor on a dot of glue, its leads down through the left hole to the charger's battery pads. The cell drops in from the top. Black is a colour the rule allows in the open. Meter the leads for polarity before the cell goes in."),
        ("1 of 13", "ESP32-C3 SuperMini controller", L["controller"], "Amazon B0F888JQ91 (Pocket AI stock; 10 spare)", "owned",
         f"The brain, in the coaster's hollow, glued up to the ceiling on Kapton with its USB-C in the notch at the back beside the charger's: flashing and the console. It runs from the cell through the diode. No Wi-Fi in this build; the button in the rim is the whole interface. Gate it with `esptool flash_id` as before; nothing is removed from it."),
        ("1 of 5", "MX1508 dual H-bridge driver", L["hbridge"], "Aideepen 5-pack, Amazon B075S368Y2 (the camera Pocket AI's stock; 4 spare)", "owned",
         f"One board for both moving things, on the boost's 5 V: channel A turns the shutter (speed, brake, the parking move), channel B switches the lamp through its resistors. 2 to 10 V in, 1.5 A a channel, inputs that read 3.3 V as high, flyback diodes inside. The screw terminals and the header come off and wires go on the pads, so it lies {D['mx_t']:.0f} mm flat in the hollow at the front."),
        ("1 of 100", "SS14 Schottky diode", L["diode"], "Chanzon, Amazon B079KJ46ZS", "owned",
         f"Between the charger's BAT pad and the controller's 5V pin, band toward the controller: {E['diode_v']:.2f} V lost, and a flashing cable's 5 V can never reach the cell. The satellite's wiring, unchanged."),
        ("2 + 2", "47 Ω and 100 kΩ resistors, 1/4 W", L["resistors"], "the resistor kit", "owned",
         f"Two 47 Ω in parallel, {E['r_lamp']:.1f} Ω, in series with the lamp, in heat-shrink in the hollow ({E['p_res_each'] * 1000:.0f} mW each at full). Two 100 kΩ as the cell-voltage divider into GPIO4. The only resistors in the build."),
        ("1", "tactile button, 6 × 6 mm", L["button"], "the button kit", "owned", f"The one control, glued inside the coaster's rim at the front with its plunger through a {D['btn_hole']:.1f} mm hole {D['btn_z']:.1f} mm up from the bottom edge: press the front of the coaster. Nothing shows but the plunger's tip."),
        ("about 1 m", "30 AWG silicone wire", L["wire30"], "CBAZY kit", "owned",
         "Two to the motor and two to the reed up through the right hole, the holder's own two leads down the left, two to the button inside the rim, eight between the three boards and the diode and the divider, two to the rods' feet, two under the roof. White where a wire could be seen."),
        ("", "Kapton tape, white heat-shrink, hot glue, 63/37 solder and flux", L["kapton"], "bench stock", "owned",
         "Kapton under the boards, the reed and the live rod's foot; white heat-shrink on the live rod where it passes the coaster and the deck, as a boot on its tip, and on every joint near brass; hot glue for the motor's bed, the washers, the button and the boards; solder for the shutter's bars, the magnet arm, the wheel, the lamp post, the rods' tips in the roof and their feet."),
        ("1", "USB-C adapter, 1 A or more, and a cable", None, "owned", "owned", f"Any phone adapter, for the charger's port at the back. The lighthouse takes {E['chg_ma']:.0f} mA to charge and runs from the cable while it does."),
    ]),
    ("Owned: brass", [
        ("1", "brass coaster, 75 × 8 mm, flat top", L["coaster"], "Amazon 114-8443990-0476239, ordered 2026-11-06 ($12.99), delivered 2026-11-09 to the mail room (Amazon's mail), in one package with the drone's heat tape", "owned",
         f"The base and the electronics box in one. Bought on 2026-11-06 as the satellite's base and given to this build on 2026-11-09 at the builder's word (the satellite buys its own again when it is built); the same part under both, so the two desk pieces match. 80 g, which says a top about 1.3 mm thick over a hollow about 6.7 deep: the four rods pass through the top and bend under it; the charger, the controller and the driver glue up to the hollow's ceiling; the two USB-C ports share a {D['notch_w']:.0f} × {D['notch_h']:.1f} notch sawn in the rim at the back; about {D['ballast_g']:.0f} g of steel washers fill the rest. Alone it tips at {D['tip_deg']:.0f}° ({D['push_n']:.1f} N at the ball); weighted, {D['tip_deg_b']:.0f}° ({D['push_n_b']:.1f} N). **Incoming check:** the hollow's depth (the controller wants {D['c3_t']:.1f} mm, the charger {D['chg_t']:.1f}, the button's body 6; if it is shallower the boards do not fit and the base must change); a magnet must not stick to the top."),
        ("4 rods", "brass rod, 1.5 mm × 300 mm", L["rod15"], "K&S 9862, 5 a pack; about 90 rods owned", "owned",
         f"The cage: four rods cut {D['leg_len']:.0f} mm, each from the coaster through the deck to the roof, bent to a 6 mm foot under the coaster's top and nudged {D['leg_deg']:.1f}° to vertical just under the deck; three pass through the roof's dome and are soldered flush, the live one is trimmed to end {D['leg_top_live']:.0f} mm above the deck under it. Two of them carry the lamp's current. Solid rod, not the 1.5 mm tube: about 30 % stiffer, and a conductor you can solder to."),
        ("about 150 mm", "brass tube, 4 mm OD × 0.5 mm wall (from the 2 to 7 mm set, 200 mm)", L["brass_tube"], "M METERXITY set, 3 owned", "owned",
         f"The spine: one piece {D['tube_len']:.0f} mm long, a slip fit over the motor's 3 mm D shaft with a drop of gel glue, up through the hub of the deck's wheel, soldered to the shutter's two bars and ending {D['tube_up']:.0f} mm above them. It turns, so it is the one moving line in the tower. From the same set, a {D['bush_t']:.0f} mm ring of the 5 mm tube is the wheel's hub: the 4 mm spine telescopes into it, which is what the set is made for."),
        (f"about {D['post_len'] + D['hw_rod']:.0f} mm", "brass rod, 1.0 mm × 300 mm", L["rod10"], "K&S 9861, 10 owned", "owned",
         f"The lamp post: {D['post_len']:.0f} mm, soldered {D['post_in']:.0f} mm up inside the nipple's bore, down behind the lamp at r {D['post_r']:.1f}, bent forward at the bottom and soldered to the filament's lower tab; it holds the lamp and is its return. And the spine's hardware, {D['hw_rod']:.0f} mm in all: two bars of {D['bar_len']:.1f} across the shutter's bottom, two spokes of {D['spoke_len']:.1f} in the deck's wheel, one arm of {D['arm_len']:.1f} for the magnet. Nothing in Rev D is painted."),
    ]),
]

# ----------------------------------------------------------------------------- the decisions
DECISIONS = [
    ("A lighthouse drawn in four lines",
     f"Four 1.5 mm brass rods run from the coaster to the roof: Ø{D['cage_d0']:.0f} at the feet, leaning in {D['leg_deg']:.1f}° to Ø{D['cage_d1']:.0f} where they pass the gallery, then straight up as the lantern's bars to the roof, which three of them carry. No rings, no braces, no glass, no house: the coaster holds their feet, the deck holds their waists, the roof their tips, and a 1.5 mm brass rod fixed at both ends carries the lantern's {D['lantern_g']:.0f} g with a buckling margin of about {D['rod_euler_n'] / max(D['rod_load_n'], 1e-6):.0f} to one. Up the middle the 4 mm spine turns. {D['height']:.0f} mm tall, about {D['mass']:.0f} g before the ballast. Rev A's tube and cube, Rev B's screen and Rev C's glass and house are gone; what is left is a wire drawing of a lighthouse with a lamp in it."),
    ("The lamp stands still and the brass turns round it",
     f"A real lighthouse does not spin its lamp; the lens turns round a fixed light. Here the lamp is a {D['fil_l']:.0f} mm LED filament standing on the axis, and a brass drum with a {D['win_deg']:.0f}° window turns round it, one revolution in {E['period']:.1f} s: a {E['pass_s']:.1f} s sweep of light across the room, then brass. No slip rings, no wire ever moves. When rotation is off, the window parks facing you and the lantern is a lamp. When the lamp is off, the shutter closes and shows you brass."),
    ("On a cell: the battery stands at the foot",
     f"The builder asked for a battery and a charger below ({TODAY}). The battery is the family's cell, a Nitecore 16340 of which thirteen are in the drawer, in the owned holder, standing on end on the coaster's top behind the motor, in the open: {D['hold_w']:.0f} × {D['hold_d']:.0f} × {D['hold_h']:.0f} mm of black tray, the one dark block in the build, a colour the rule allows. The cell lifts out of its tray; nothing is soldered to it. {E['cell_typ']:.0f} mA from the cell with the beacon turning and the lamp at {E['lamp_duty'] * 100:.0f} %: about {E['h_beacon']:.0f} hours of lighthouse, {E['h_lamp']:.0f} of lamp alone, {E['h_idle'] / 24:.0f} days asleep with the boost off. The cell's voltage comes to the controller through two 100 kΩ, so it dims, parks and shuts down in order instead of dying mid-turn."),
    ("The charger in the coaster, the ports at the back",
     f"The same charger board as Cyber Dawn and the satellite, a bq25185 with a 5 V boost: USB-C in, {E['chg_ma']:.0f} mA into the cell with its jumper cut ({E['h_charge']:.1f} h from empty), a power path that runs the lighthouse from the cable while it charges, and a 1 A boost that makes the 5 V rail for the motor and the lamp. The controller takes the cell straight through an SS14, the satellite's trick, so the boost can sleep: GPIO7 wakes it only while something moves. Its terminal block and JST socket come off and it lies {D['chg_t']:.1f} mm flat in the coaster's hollow beside the controller, both ports in one {D['notch_w']:.0f} mm notch at the back of the rim: the charging cable and, rarely, the flashing cable. That notch is the build's one compromise."),
    ("The motor on the coaster, the spine up the middle",
     f"A wire frame has nowhere to hide a motor at the top, so the motor stands at the foot on a bed of hot glue, shaft up on the axis, and the owned 4 mm brass tube slides over its D shaft and runs {D['tube_len']:.0f} mm up through the deck's bearing to the shutter. The bearing is a wheel made of what is already here: a {D['bush_t']:.0f} mm ring of the 5/8 in tube glued on the deck over its 11 mm hole, two 1 mm spokes, and a {D['bush_t']:.0f} mm ring of the owned 5 mm tube as the hub, which the 4 mm spine telescopes into with about {(D['bush_hole'] - D['tube_od']) / 2:.1f} mm of play. It is soldered up on the spine itself, so it centres itself, then slid down onto the deck. The spine is the one line beyond the outline, and it is the one that moves: the lighthouse's own lamp post, turning."),
    ("A reed switch so it knows where the window is",
     f"A DC gearmotor has no idea where it stopped. A 1 mm brass rod {D['arm_len']:.1f} mm long is soldered to the spine as an arm, {D['collar_up']:.1f} mm above the gearbox, with a 3 × 1 mm magnet glued under its tip, {D['mag_r']:.0f} mm out, placed opposite the shutter's window; a glass reed switch stands behind the motor, in front of the cell, with its top {D['reed_gap']:.0f} mm under the magnet's path, so it closes once a revolution at the moment the window faces front. From that one pulse the firmware times each revolution and trims the PWM to {E['period']:.1f} s, parks the window on you when you turn rotation off, closes the shutter by running on half a turn when the lamp goes off, and notices a jam. Two short wires; nothing climbs the tower for it."),
    ("Two of the four rods are the lamp's wires",
     f"Nothing may climb a wire frame but the frame, so the lamp's current goes up one rod and comes down another. The back-left rod is live: white heat-shrink where it passes the coaster and the deck, a white boot on its tip, a wire soldered to its foot in the hollow and another from its tip to the filament's + tab under the roof; it is the one rod that stops short of the roof. The back-right rod is the return, soldered to a ground wire at its foot and to the nut's wire at its tip, and through the roof like the two front rods. {E['rod_mohm']:.1f} mΩ each; the brass does not notice {E['i_lamp_max']:.0f} mA. The rover's frame is its ground; this is the same idea with one rod insulated, and the meter checks it before power."),
    ("A lamp post that is also the return",
     f"A rigid LED filament has a metal tab at each end, the + one with a hole in it. So a 1 mm brass rod is soldered {D['post_in']:.0f} mm up inside the nipple's hollow bore, runs down behind the lamp at r {D['post_r']:.1f} inside the shutter, bends forward at the bottom and is soldered to the lower tab: it holds the filament rigid on the axis and carries its return to the nut. The + tab at the top takes one wire. Inside the drum a glowing strip and a thin brass post behind it, the way a lamp sits in a real lantern."),
    ("Warm white, 2700 K, not the family's amber",
     f"The hologram and the satellite use a 2200 K filament as a pool of amber on brass, and eight of them are spare. A lighthouse lamp is not a pool: it is the light itself, and the rule is white or warm white. A 26 mm, 3 V, 100 mA filament at 2700 K is an incandescent lamp's colour; {E['i_lamp_max']:.0f} mA through {E['r_lamp']:.1f} Ω from the 5 V rail, {E['lamp_w'] * 1000:.0f} mW, dimmed to {E['lamp_duty'] * 100:.0f} % by day. Its phosphor is yellow when off, which is why the shutter closes over it."),
    ("No house, no glass, no screen",
     f"The screen went at the builder's word on the morning of {TODAY}; the acrylic lantern glass and the brass-sheet house went that evening (\"so ugly\"; \"just use the wire frame as a lighthouse, nothing else\"). So the lantern is open: the four rods are its bars, the shutter turns in the air, and nothing optical is lost, since the glass was a window and not a lens. At the foot the motor, the reed, the magnet arm and the cell in its tray stand on the brass in the open: steel, glass, brass and black, every one a colour the rule allows. Nothing is folded, nothing is painted, nothing is glued over anything."),
    ("The three small brass pieces are rod and tube, not sheet",
     f"Rev C cut three discs from 0.4 mm sheet: the shutter's floor, the magnet's collar and the deck's bushing. Rev D makes each from the rod and tube already on the bench. Two 1 mm bars {D['bar_len']:.1f} mm long lie across the shutter's bottom, {D['floor_z']:.1f} mm up, soldered to the spine's flanks and the drum's wall: the floor. One 1 mm arm on the spine carries the magnet: the collar. A wheel of two tube rings and two spokes sits on the deck: the bushing. Lighter, nothing to buy, and all of it in the same wire language as the cage."),
    ("Lamp-maker's parts as architecture",
     f"The gallery is a 1-1/2 in turned brass check ring, a solid disc with an 11 mm hole already where the spine goes, threaded down the rods. The roof is a 1-1/2 in spun brass vase cap, held by the rods themselves: three of them pass through its dome at r {D['ast_r']:.1f} and are soldered flush from outside, the one joint that closes the cage at the top. The ventilator ball is a 5/8 in brass ball tapped 1/8 IP, on a 1/2 in nipple with a beaded nut inside the cap that also carries the lamp post. Five parts, about $7, from one lamp-parts house, each already the right shape and the right metal, none of it machined. Nothing is printed."),
    ("Brass lines and white light",
     f"The brief was a brass build with some ivory; the ivory went with the house, and what is left is brass lines and warm white light. The lines are brass: the rods, the spine, the deck, the shutter, the cap, the ball, the coaster. Black only in the pad under the coaster, the cell's wrap and its tray, which stand at the foot in the open as the colour rule allows; the motor is steel, the reed glass; the live rod's sleeves are white heat-shrink. The boards live in the coaster's hollow, so nothing coloured shows. Brass at the builder's word for this build; the family's rule since the drone is stainless."),
    ("One owned driver board does both jobs",
     f"The camera Pocket AI's spare MX1508 dual H-bridge: channel A is the shutter's motor with speed, brake and the parking move; channel B, with one input tied low, is a 1.5 A high-side switch for the lamp through its resistors, the lamp returning through the frame. Both loads get the boost's 5 V, the controller's GPIOs see only logic, and there are no MOSFETs, gate resistors or flyback diodes to wire. Its header and screw terminals come off so it lies {D['mx_t']:.0f} mm flat in the hollow."),
    ("The coaster is the satellite's, and it is the box",
     f"The same 75 × 8 mm brass coaster the satellite stands on, so the two match on the desk; the one bought on 2026-11-06 for the satellite became this build's on 2026-11-09 and arrived that day, and the satellite's comes later. Its listing's 80 g says a top about 1.3 mm thick over a hollow about 6.7 deep: enough for the charger ({D['chg_t']:.1f} mm stripped of its terminal block), the controller ({D['c3_t']:.1f} mm with its port) and the driver glued up to the ceiling, the button glued inside the rim at the front with its plunger through a {D['btn_hole']:.1f} mm hole, the rods' feet bent under the top, and about {D['ballast_g']:.0f} g of steel washers beside them. Alone it tips at {D['tip_deg']:.0f}°, a {D['push_n']:.1f} N push at the ball; weighted, the centre of mass drops to {D['cg_b']:.0f} mm and the tip to {D['tip_deg_b']:.0f}°, {D['push_n_b']:.1f} N; the cell low at the foot helps. Measure the hollow."),
    ("A reference, not a copy",
     "Huy Vector's page is a parts list: 0.2 mm brass sheet, 4 mm brass tube, copper wire, a 3 V 30 rpm gear motor, a 39 mm Edison filament, a glass fuse, a Type-C charging module, a battery, a bamboo coaster. Ours keeps the idea (a small brass lighthouse on a coaster, a gear motor turning something in the lantern, a filament lamp, a cell and a charging port, brass) and does the rest its own way: a wire tower instead of rolled sheet, a fixed lamp and a turning brass shutter, a reed index so it parks, the family's cell and charger, lamp parts for the lantern, no sheet at all. Side by side they share a silhouette, a motor and a battery."),
    ("How it sits with the family",
     f"Brass rods and a few rings are the Pocket AI Sphere's language; an open wire frame that carries current is the rover's; the coaster, the cell, the holder, the charger and the diode are the satellite's, wired the same way. At {D['height']:.0f} mm it is the tall one; the satellite is 159, Cyber Dawn 82, the hologram 72. Few lines: four rods and a spine, and no closed surface at all, the first build in the family with nothing to lift off. Prototype, not product: the cell lifts out of its tray, the firmware reflashes through the notch, and the roof comes off with a hot iron on three joints."),
]

FIRMWARE = [
    "ESP-IDF 6 for the esp32c3, a new small project beside the hologram's. No Wi-Fi: the console on USB Serial/JTAG, the button the whole interface.",
    "GPIO7 high to wake the boost before anything moves, low again when the shutter is parked and the lamp is off; the boost stalls over 200 mA at switch-on, so the motor's PWM ramps from 0 to its duty over 0.2 s and the lamp fades up after it.",
    "LEDC: GPIO0 at 20 kHz for the motor (silent), GPIO3 at 5 kHz for the lamp. GPIO1 low for forward, high with GPIO0 high to brake. All three driven low first thing at boot.",
    f"The reed on GPIO6, interrupt on the falling edge, 5 ms debounce: period of the last revolution; a PI loop trims the motor duty to hold {E['period']:.1f} s; no pulse for twice that with the motor on = jammed, motor off, boost off.",
    "Parking: on rotation off, run until the reed closes, then brake: the window faces front (the magnet sits opposite the window, over the reed behind the motor). On lamp off, run from the index for half a period, then brake: the shutter is closed. On lamp on, open again. A small offset in NVS trims the park angle after the first bench run.",
    "The button on GPIO10: short press rotation on/off; long press (1 s) lamp off, low, full. The lamp blinks once to say so.",
    f"The cell on GPIO4 through the divider, read once a minute: below {E['v_cell_low'] + 0.2:.1f} V the lamp drops to low and blinks twice; below {E['v_cell_low']:.1f} V the shutter parks, the lamp goes out, the boost goes off, and the controller sleeps until the button or a higher reading.",
    f"First-power measurements the record wants: the current from the cell in each mode (expected about {E['cell_typ']:.0f} mA beacon, {E['cell_lamp']:.0f} lamp, {E['cell_idle']:.0f} asleep), the lamp's current at full (about {E['i_lamp_max']:.0f} mA), the revolution period from the reed, and the charge current with the jumper cut (about {E['chg_ma']:.0f} mA).",
]

CHECKS = [
    "Before the cell meets anything: the holder's leads for polarity on the meter with the cell in (3.6 to 4.1 V, button top +); the charger's jumper cut; the filament's polarity with the diode test (it lights faintly; the tab with the hole is +).",
    f"With the boards wired on the bench, the cell in and the lantern not yet up: the cell's voltage on the charger's BAT pad, 3.5 to 4.0 V on the controller's 5V pin (the diode's drop), 5.0 V on the driver's VCC with GPIO7 high and nothing with it low, half the cell's voltage on GPIO4; then the lamp channel at full gives 2.9 to 3.1 V across the filament, about {E['i_lamp_max']:.0f} mA, the motor channel turns the spine, the brake stops it, and the reed closes once a turn. Plug the charger's cable: the orange LED, and the lighthouse still runs.",
    "The live rod alone: back-left rod to the coaster open, to the deck open, to the roof open, before its wires go on. Then back-right rod's foot to the nut: a short, through the solder at both ends. Nothing else bare against brass: the motor's tabs, the reed's leads, the holder's leads and both wires under the roof in heat-shrink. Everything else is a supplier spec and is not metered.",
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
    elif side == "B":
        o.append(T(x + 4, y - 10, name, "pin", "start", f'transform="rotate(-90 {x + 4} {y - 10})"'))
    elif side == "T":
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


def dim_h(x0, x1, y, label, above=True, cls="dim", lcls="dimlab"):
    o = [f'<path d="M{x0:.1f},{y-6} L{x0:.1f},{y+6} M{x1:.1f},{y-6} L{x1:.1f},{y+6} M{x0:.1f},{y} L{x1:.1f},{y}" class="{cls}"/>']
    o.append(T((x0 + x1) / 2, y - 5 if above else y + 15, label, lcls, "middle"))
    return "".join(o)


def dim_v(x, y0, y1, label, right=True, cls="dim"):
    o = [f'<path d="M{x-6},{y0:.1f} L{x+6},{y0:.1f} M{x-6},{y1:.1f} L{x+6},{y1:.1f} M{x},{y0:.1f} L{x},{y1:.1f}" class="{cls}"/>']
    ym = (y0 + y1) / 2
    o.append(T(x + 8 if right else x - 8, ym + 4, label, "dimlab", "start" if right else "end"))
    return "".join(o)


def leader(x0, y0, x1, y1):
    return f'<path d="M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}" class="dim"/>'


def rect(x0, y0, x1, y1, cls, rx=0):
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    return f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{xb - xa:.1f}" height="{yb - ya:.1f}" rx="{rx}" class="{cls}"/>'


def poly(pts, cls, close=False):
    return '<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ('Z' if close else '') + f'" class="{cls}"/>'


def circ(x, y, r, cls):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="{cls}"/>'


def arc_path(cx, cy, r, a0, a1, cls):
    """An arc from angle a0 to a1 (degrees, SVG sense: 0 = +x, 90 = down), the long way when the sweep passes 180."""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f'<path d="M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} 1 {x1:.1f},{y1:.1f}" class="{cls}"/>'


def rod(x0, y0, x1, y1, w, cls="rodfill"):
    """A rod drawn as a filled polygon of width w (px) between two points, so it scales with the view."""
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1.0
    px, py = -dy / n * w / 2, dx / n * w / 2
    return poly([(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)], cls, close=True)


# The lighthouse's own palette: brass, ivory, glass and warm white (both themes; greys in print).
LH_LIGHT = ("--lh-brass:#C9A24F;--lh-brass-lo:#7A5A22;--lh-brass-dk:#A8843A;--lh-rod:#9C7A32;--lh-ivory:#F1EBDD;--lh-ivory-lo:#9A917C;"
            "--lh-glass:#F4F8FA;--lh-glass-lo:#7F8A94;--lh-warm:#F6DE9E;--lh-warm-lo:#B78A2E;--lh-black:#1E1F22;--lh-black-lo:#55585E;"
            "--lh-steel:#C3C8CD;--lh-steel-lo:#6B7178;--lh-board:#2B3340;--lh-mag:#8A8F96;--lh-glue:#E9E4DA")
LH_DARK = ("--lh-brass:#D2AA58;--lh-brass-lo:#F0D59A;--lh-brass-dk:#B08A3E;--lh-rod:#D8B36A;--lh-ivory:#E6DFCC;--lh-ivory-lo:#B9AF97;"
           "--lh-glass:#232A31;--lh-glass-lo:#9BA7B2;--lh-warm:#F6DE9E;--lh-warm-lo:#F0C77A;--lh-black:#0E0F11;--lh-black-lo:#8D939A;"
           "--lh-steel:#B4BAC0;--lh-steel-lo:#E3E7EB;--lh-board:#3A4452;--lh-mag:#A9AEB5;--lh-glue:#3A3F46")
LH_PRINT = ("html:root{--lh-brass:#d9d9d9;--lh-brass-lo:#000;--lh-brass-dk:#bdbdbd;--lh-rod:#555;--lh-ivory:#fff;--lh-ivory-lo:#000;--lh-glass:#fff;--lh-glass-lo:#000;"
            "--lh-warm:#eee;--lh-warm-lo:#000;--lh-black:#333;--lh-black-lo:#000;--lh-steel:#bbb;--lh-steel-lo:#000;--lh-board:#555;--lh-mag:#777;--lh-glue:#f3f3f3}")
LH_CSS = (":root{" + LH_LIGHT + "}@media (prefers-color-scheme:dark){:root:not([data-theme=light]){" + LH_DARK + "}}:root[data-theme=dark]{" + LH_DARK + "}"
          ".brass{fill:var(--lh-brass);stroke:var(--lh-brass-lo);stroke-width:.8}"
          ".brassdk{fill:var(--lh-brass-dk);stroke:var(--lh-brass-lo);stroke-width:.8}"
          ".brassln{fill:none;stroke:var(--lh-brass-lo);stroke-width:1}"
          ".brassring{fill:none;stroke:var(--lh-brass-lo);stroke-width:2.2}"
          ".rodfill{fill:var(--lh-rod);stroke:var(--lh-brass-lo);stroke-width:.5}"
          ".rodln{fill:none;stroke:var(--lh-rod);stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round}"
          ".rodfr{fill:none;stroke:var(--lh-rod);stroke-width:5.5;stroke-linecap:round;stroke-linejoin:round}"
          ".ivory{fill:var(--lh-ivory);stroke:var(--lh-ivory-lo);stroke-width:.9}"
          ".glass{fill:var(--lh-glass);stroke:var(--lh-glass-lo);stroke-width:1}"
          ".glassln{fill:none;stroke:var(--lh-glass-lo);stroke-width:1}"
          ".warm{fill:var(--lh-warm);stroke:var(--lh-warm-lo);stroke-width:.8}"
          ".warmfill{fill:var(--lh-warm);stroke:none;opacity:.55}"
          ".blk{fill:var(--lh-black);stroke:var(--lh-black-lo);stroke-width:.8}"
          ".steel{fill:var(--lh-steel);stroke:var(--lh-steel-lo);stroke-width:.8}"
          ".board{fill:var(--lh-board);stroke:var(--lh-black-lo);stroke-width:.8}"
          ".mag{fill:var(--lh-mag);stroke:var(--lh-steel-lo);stroke-width:.6}"
          ".glue{fill:var(--lh-glue);stroke:var(--lh-ivory-lo);stroke-width:.5}"
          ".glow{fill:none;stroke:var(--lh-warm-lo);stroke-width:1.2;stroke-dasharray:2 3}"
          ".beam{fill:none;stroke:var(--lh-warm-lo);stroke-width:1.3;stroke-dasharray:7 4}"
          ".onblack{font:700 9px 'JetBrains Mono',monospace;fill:#F4F2EE}")

PAGE_TONES = (":root{--signal:#5A6068;--signal-soft:#ECEAE6;--ok:#8F6114;--ok-soft:#F2E6D2;--warn:#8F6114;--warn-soft:#F2E6D2}"
              "@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--signal:#9BA3AC;--signal-soft:#2A2D33;--ok:#D69A4E;--ok-soft:#3A2C18;--warn:#D69A4E;--warn-soft:#3A2C18}}"
              ":root[data-theme=dark]{--signal:#9BA3AC;--signal-soft:#2A2D33;--ok:#D69A4E;--ok-soft:#3A2C18;--warn:#D69A4E;--warn-soft:#3A2C18}")

SHEET_CSS = ("<style>"
             ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
             ".usb{fill:var(--line);stroke:var(--ink-2);stroke-width:1.2}"
             ".title{font:700 16px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".sub{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".h1{font:900 24px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".h2{font:700 15px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".pin{font:700 13px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".lab{font:700 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
             ".dimlab{font:700 11.5px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".mono{font:400 11px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".rod{fill:none;stroke:var(--ink);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
             ".thin{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
             ".hair{fill:none;stroke:var(--ink);stroke-width:1;stroke-linecap:round}"
             ".dim{fill:none;stroke:var(--ink-2);stroke-width:1}"
             ".joint{fill:var(--ink)}"
             ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
             ".ghost{fill:none;stroke:var(--ink-2);stroke-width:1.1;stroke-dasharray:3 3}"
             ".cavity{fill:var(--bg);stroke:var(--ink-2);stroke-width:.7}"
             ".desk{fill:none;stroke:var(--ink);stroke-width:1.6}"
             ".hatch{fill:none;stroke:var(--ink-2);stroke-width:.8}"
             ".cut{fill:none;stroke:var(--ink);stroke-width:1.2}"
             ".tmpl{fill:none;stroke:var(--ink);stroke-width:1.4}"
             ".tmplhole{fill:var(--bg);stroke:var(--ink);stroke-width:1.2}"
             ".fold{fill:none;stroke:var(--ink-2);stroke-width:.9;stroke-dasharray:6 3}"
             ".centre{fill:none;stroke:var(--ink-2);stroke-width:.8;stroke-dasharray:8 3 2 3}"
             + LH_CSS + "</style>")


# ----------------------------------------------------------------------------- shared drawing pieces
def cap_poly(X, Z, inner=False, n=24):
    """The cap's section outline in a view: left profile rim→top, right profile top→rim. X(r) and Z(z') map to the view."""
    f = cap_inner_pt if inner else cap_pt
    left = [f(i / n) for i in range(n + 1)]
    pts = [(X(-r), Z(z)) for r, z in left] + [(X(r), Z(z)) for r, z in reversed(left)]
    return pts


def label_l(o, px, py, lx, ly, lines):
    """A label whose text ends at lx (end-anchored), with a leader from its right end to the part at (px, py)."""
    o.append(leader(px, py, lx + 4, ly - 4))
    for i, s in enumerate(lines):
        o.append(T(lx, ly + i * 14, s, "fn", "end"))


def label_r(o, px, py, lx, ly, lines):
    o.append(leader(px, py, lx - 4, ly - 4))
    for i, s in enumerate(lines):
        o.append(T(lx, ly + i * 14, s, "fn"))


def zigzag_v(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2
    z = 7
    pts = [(x, y0), (x, mid - 14)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        pts.append((x + dx, mid - 14 + (i + 0.5) * (28 / 6)))
    pts += [(x, mid + 14), (x, y1)]
    return rt.wire(pts, "thin", net)


def diode_h(x0, x1, y):
    """A diode symbol on a horizontal wire from x0 to x1, the band at x1 (current flows left to right)."""
    xm = (x0 + x1) / 2
    return (f'<path d="M{xm - 9:.1f},{y - 8} L{xm - 9:.1f},{y + 8} L{xm + 7:.1f},{y} Z" class="joint"/>'
            f'<path d="M{xm + 7:.1f},{y - 8} L{xm + 7:.1f},{y + 8}" class="rod"/>')


# ----------------------------------------------------------------------------- sheet 1: the form
def form_sheet():
    o = [T(20, 30, "Desk lighthouse: how the finished thing looks (Rev D: the open wire frame, on a cell)", "h1"),
         T(20, 48, f"Four brass rods from a brass coaster to a brass roof, a turning spine up the middle, the motor and the cell standing in the open at the foot, an open lantern on top: no glass, no house. {D['height']:.0f} mm tall, Ø{D['disc_d']:.0f} at the base, about {D['mass']:.0f} g before the ballast.", "sub")]
    z1 = D["z_deck1"]
    c45 = math.cos(math.radians(45))
    xl0, xl1 = D["leg_r0"] * c45, D["ast_r"] * c45          # the rods' projected half-widths, at the feet and at the deck

    # ---------------------------------------------------------------- front view, 2.3 px per mm
    s = 2.3
    x0, y0 = 200, 742
    X = lambda xm: x0 + xm * s   # noqa: E731
    Z = lambda zm: y0 - zm * s   # noqa: E731
    o.append(T(40, 90, "Front view", "h2"))
    o.append(f'<line x1="{X(-60)}" y1="{y0}" x2="{X(60)}" y2="{y0}" class="desk"/>')
    o.append(T(X(-60), y0 + 14, "desk", "fn"))
    o.append(rect(X(-D["disc_d"] / 2), Z(0), X(D["disc_d"] / 2), Z(D["disc_t"]), "brass"))
    for sgn in (-1, 1):   # each line is two rods, one in front of the other
        o.append(rod(X(sgn * xl0), Z(D["disc_t"]), X(sgn * xl1), Z(D["z_deck0"]), D["rod_d"] * s))
    # the foot, in the open: the tray behind, the motor on the axis, the spine
    o.append(rect(X(-D["hold_w"] / 2), Z(D["disc_t"]), X(D["hold_w"] / 2), Z(D["disc_t"] + D["hold_h"]), "part"))
    zm0 = D["disc_t"] + D["mot_z0"]
    o.append(rect(X(-D["mot_w"] / 2), Z(D["disc_t"]), X(D["mot_w"] / 2), Z(zm0), "glue"))
    o.append(rect(X(-D["mot_w"] / 2), Z(zm0), X(D["mot_w"] / 2), Z(zm0 + D["mot_l"] - D["gear_l"]), "board"))
    o.append(rect(X(-D["mot_w"] / 2), Z(zm0 + D["mot_l"] - D["gear_l"]), X(D["mot_w"] / 2), Z(zm0 + D["mot_l"]), "steel"))
    o.append(rect(X(-D["tube_od"] / 2), Z(D["z_tube0"]), X(D["tube_od"] / 2), Z(D["z_deck0"]), "brass"))
    o.append(rect(X(-D["deck_d"] / 2), Z(D["z_deck0"]), X(D["deck_d"] / 2), Z(z1), "brass"))
    o.append(rect(X(-D["drum_od"] / 2), Z(z1 + D["drum_z0"]), X(D["drum_od"] / 2), Z(z1 + D["drum_top"]), "brassdk"))
    wx = D["drum_od"] / 2 * math.sin(math.radians(D["win_deg"] / 2))
    zw0, zw1 = z1 + D["drum_z0"] + D["dwin_z0"], z1 + D["drum_z0"] + D["dwin_z0"] + D["dwin_h"]
    o.append(rect(X(-wx), Z(zw0), X(wx), Z(zw1), "warmfill"))
    o.append(rect(X(-D["fil_w"] / 2), Z(z1 + D["fil_bot"]), X(D["fil_w"] / 2), Z(min(zw1, z1 + D["fil_top"])), "warm"))
    o.append(circ(X(0), Z(z1 + 20), 11 * s, "glow"))
    for sgn in (-1, 1):   # the rods continue up as the lantern's bars, through the dome
        o.append(rod(X(sgn * xl1), Z(D["z_deck0"]), X(sgn * xl1), Z(z1 + D["leg_top"]), D["rod_d"] * s))
    o.append(poly(cap_poly(X, lambda z: Z(z1 + z)), "brass", close=True))
    o.append(rect(X(-D["nip_od"] / 2), Z(D["z_cap_top"]), X(D["nip_od"] / 2), Z(z1 + D["ball_bot"]), "brassdk"))
    o.append(circ(X(0), Z(z1 + D["ball_c"]), D["ball_d"] / 2 * s, "brass"))
    cx_, cy_, r_ = X(0), Z(z1 + 17), 19 * s
    a0, a1 = math.radians(-55), math.radians(55)
    o.append(f'<path d="M{cx_ + r_*math.cos(a0):.1f},{cy_ + r_*math.sin(a0):.1f} A{r_:.1f},{r_:.1f} 0 0 1 {cx_ + r_*math.cos(a1):.1f},{cy_ + r_*math.sin(a1):.1f}" class="beam"/>')
    tx, ty = cx_ + r_ * math.cos(a1), cy_ + r_ * math.sin(a1)
    o.append(poly([(tx - 7, ty - 2), (tx + 1, ty - 9), (tx + 3, ty + 1)], "solid", close=True))
    o.append(T(cx_ + r_ + 6, cy_ + 4, f"{E['period']:.1f} s a turn", "fn"))
    o.append(dim_v(X(-D["disc_d"] / 2) - 24, Z(0), Z(D["height"]), f"{D['height']:.0f}", False))
    o.append(dim_v(X(-D["deck_d"] / 2) - 12, Z(z1), Z(D["z_cap_rim"]), f"{D['cap_rim']:.1f}", False))
    o.append(dim_v(X(xl0) + 18, Z(D["disc_t"]), Z(D["z_deck0"]), f"{D['leg_h']:.0f}", True))
    o.append(dim_v(X(-24), Z(D["disc_t"]), Z(D["disc_t"] + D["hold_h"]), f"{D['hold_h']:.0f}", False))
    o.append(dim_h(X(-D["disc_d"] / 2), X(D["disc_d"] / 2), y0 + 34, f"Ø{D['disc_d']:.0f} × {D['disc_t']:.0f} brass coaster, {D['disc_g']:.0f} g", False))
    o.append(dim_h(X(-D["deck_d"] / 2), X(D["deck_d"] / 2), Z(D["height"]) - 30, f"Ø{D['deck_d']:.1f} deck and roof", True))
    lx = 330
    label_r(o, X(D["ball_d"] / 2 * 0.7), Z(z1 + D["ball_c"] - 5), lx, 200, ["ventilator ball: 5/8 in brass,", "on a 1/8 IP nipple"])
    label_r(o, X(15), Z(z1 + D["cap_rim"] + 5), lx, 238, ["roof: 1-1/2 in spun brass vase", "cap; three rods pass through its", "dome and are soldered flush"])
    label_r(o, X(D["drum_od"] / 2), Z(z1 + 22), lx, 290, ["open lantern: no glass; the four", "rods are its bars; inside, a brass", "shutter turns round a fixed 2700 K", "filament on a brass post"])
    label_r(o, X(D["deck_d"] / 2), Z(D["z_deck0"] + 1.5), lx, 356, ["gallery: 1-1/2 in turned brass", "check ring, threaded on the rods"])
    label_r(o, X(D["tube_od"] / 2), Z(118), lx, 430, ["spine: the owned 4 mm brass tube,", "from the motor to the shutter;", f"it turns, {E['period']:.1f} s a revolution"])
    r80 = D["leg_r0"] - (80 - D["disc_t"]) * D["leg_slope"]
    label_r(o, X(r80 * c45), Z(80), lx, 520, ["cage: four 1.5 mm brass rods,", f"Ø{D['cage_d0']:.0f} at the feet, Ø{D['cage_d1']:.0f} at the gallery;", "the two at the back carry the lamp"])
    label_r(o, X(D["hold_w"] / 2), Z(30), lx, 626, ["the foot, in the open: the motor", "on the axis, the cell in its black", "tray behind it, the reed and the", "magnet arm between; no cover"])
    label_r(o, X(D["disc_d"] / 2), Z(D["disc_t"] / 2), lx, 712, ["the satellite's coaster: the boards", "in its hollow, the button inside its", "rim at the front, both USB-Cs in a", "notch at the back"])

    # ---------------------------------------------------------------- section through the lantern, 5 px per mm (front on the left)
    s2 = 5.0
    xs, ys = 600, 445
    X2 = lambda xm: xs + xm * s2      # noqa: E731  front negative (left), back positive
    Z2 = lambda zm: ys - zm * s2      # noqa: E731  z' above the deck's top
    o.append(T(520, 90, "Lantern section, front on the left; the two front rods are cut away", "h2"))
    tr, ti = D["tube_od"] / 2, D["tube_id"] / 2
    dr, dw = D["drum_od"] / 2, D["drum_wall"]
    zb = D["drum_z0"] + D["floor_z"]
    o.append(rect(X2(-(dr - dw)), Z2(zb), X2(dr - dw), Z2(zb + D["bar_d"]), "brassdk"))        # one of the shutter's two bars, behind the plane
    rr = D["bush_d"] / 2 - D["drum_wall"]
    o.append(rect(X2(-rr), Z2(1.0), X2(rr), Z2(1.0 + D["spoke_d"]), "brassdk"))               # one of the wheel's two spokes, behind the plane
    o.append(rect(X2(-tr), Z2(-30), X2(tr), Z2(D["tube_top"]), "brass"))
    o.append(rect(X2(-ti), Z2(-30), X2(ti), Z2(D["tube_top"]), "cavity"))
    hr = D["deck_hole"] / 2
    o.append(rect(X2(-D["deck_d"] / 2), Z2(-D["deck_t"]), X2(-hr), Z2(0), "brass"))
    o.append(rect(X2(hr), Z2(-D["deck_t"]), X2(D["deck_d"] / 2), Z2(0), "brass"))
    for sgn in (-1, 1):   # the rods' holes, off the plane: hidden detail
        o.append(rect(X2(sgn * xl1 - 0.9), Z2(-D["deck_t"]), X2(sgn * xl1 + 0.9), Z2(0), "ghost"))
    br = D["bush_d"] / 2
    for sgn in (-1, 1):   # the wheel: the rim ring and the hub ring, cut
        o.append(rect(X2(sgn * (br - dw)), Z2(0), X2(sgn * br), Z2(D["bush_t"]), "brass"))
        o.append(rect(X2(sgn * (D["hub_od"] / 2 - 0.5)), Z2(0), X2(sgn * D["hub_od"] / 2), Z2(D["bush_t"]), "brass"))
    o.append(poly(cap_poly(X2, Z2), "brass", close=True))
    o.append(poly(cap_poly(X2, Z2, inner=True), "cavity", close=True))
    o.append(rect(X2(-dr + dw), Z2(D["drum_z0"]), X2(dr - dw), Z2(D["drum_top"]), "warmfill"))
    o.append(rect(X2(-dr), Z2(D["drum_z0"]), X2(-dr + dw), Z2(D["drum_z0"] + D["dwin_z0"]), "brassdk"))
    o.append(rect(X2(-dr), Z2(D["drum_z0"] + D["dwin_z0"] + D["dwin_h"]), X2(-dr + dw), Z2(D["drum_top"]), "brassdk"))
    o.append(rect(X2(dr - dw), Z2(D["drum_z0"]), X2(dr), Z2(D["drum_top"]), "brassdk"))
    o.append(rect(X2(-D["fil_w"] / 2), Z2(D["fil_bot"]), X2(D["fil_w"] / 2), Z2(D["fil_top"]), "warm"))
    o.append(rect(X2(-0.25), Z2(D["post_foot"]), X2(0.25), Z2(D["fil_bot"]), "steel"))
    o.append(rect(X2(-0.25), Z2(D["fil_top"]), X2(0.25), Z2(D["fil_top"] + D["tab"]), "steel"))
    pr, pd = D["post_r"], D["post_d"] / 2
    o.append(rect(X2(0), Z2(D["post_foot"] - 0.5), X2(pr + pd), Z2(D["post_foot"] + 0.5), "brassdk"))
    o.append(rect(X2(-D["nut_d"] / 2), Z2(D["nut_bot"]), X2(D["nut_d"] / 2), Z2(D["nut_bot"] + D["nut_h"]), "brassdk"))
    o.append(rect(X2(-D["nip_od"] / 2), Z2(D["nut_bot"]), X2(D["nip_od"] / 2), Z2(D["nip_top"]), "brass"))
    o.append(rect(X2(-D["nip_id"] / 2), Z2(D["nut_bot"]), X2(D["nip_id"] / 2), Z2(D["nip_top"]), "cavity"))
    o.append(rect(X2(pr - pd), Z2(D["post_foot"]), X2(pr + pd), Z2(D["post_top"]), "brassdk"))
    o.append(circ(X2(0), Z2(D["ball_c"]), D["ball_d"] / 2 * s2, "brass"))
    lt, ltl = D["leg_top"], D["leg_top_live"]
    r30 = D["ast_r"] + (30 - D["deck_t"]) * D["leg_slope"]
    o.append(rod(X2(r30 * c45), Z2(-30), X2(xl1), Z2(-D["deck_t"]), D["rod_d"] * s2))
    o.append(rod(X2(xl1), Z2(-D["deck_t"]), X2(xl1), Z2(lt), D["rod_d"] * s2))
    o.append(rect(X2(xl1 - D["sleeve_od"] / 2), Z2(-D["deck_t"] - 2), X2(xl1 + D["sleeve_od"] / 2), Z2(2), "ivory"))
    o.append(rect(X2(xl1 - D["sleeve_od"] / 2), Z2(ltl - D["boot"]), X2(xl1 + D["sleeve_od"] / 2), Z2(ltl + 0.4), "ivory"))
    o.append(f'<path d="M{X2(0.3)},{Z2(D["fil_top"] + D["tab"])} L{X2(7.9)},{Z2(D["nut_bot"] - 0.7)} L{X2(xl1 - 1.4)},{Z2(ltl - 3.6)} L{X2(xl1 - 0.7)},{Z2(ltl - 3.6)}" class="hair"/>')
    o.append(f'<path d="M{X2(D["nut_d"] / 2)},{Z2(D["nut_bot"] + 1)} L{X2(xl1 - 0.7)},{Z2(D["nut_bot"] - 2.2)}" class="hair"/>')
    zw = D["drum_z0"] + D["dwin_z0"] + D["dwin_h"] / 2
    for dz in (-8, 0, 8):
        o.append(f'<line x1="{X2(-dr)}" y1="{Z2(zw)}" x2="{X2(-21)}" y2="{Z2(zw + dz)}" class="beam"/>')
    lxr = 716
    label_r(o, X2(6), Z2(D["ball_c"] + 2), lxr, 166, ["5/8 in brass ball, blind-tapped 1/8 IP"])
    label_r(o, X2(D["nut_d"] / 2), Z2(D["nut_bot"] + 2.4), lxr, 204, ["1/2 in nipple through the cap; the nut", "clamps it; the lamp post is soldered up", "inside the nipple's bore"])
    label_r(o, X2(16.5), Z2(D["cap_rim"] + 4), lxr, 254, ["vase cap Ø38: the roof, on three rods that", "pass through its dome, soldered flush outside"])
    label_r(o, X2(12), Z2(31), lxr, 292, ["open lantern: nothing between the lamp and", "the room; the shutter turns in the air"])
    label_r(o, X2(dr), Z2(24), lxr, 330, [f"shutter: 5/8 in tube, {D['drum_h']:.0f} tall, {D['win_deg']:.0f}° window {D['dwin_h']:.0f}", "tall; two 1 mm bars hold it on the spine"])
    label_r(o, X2(D["fil_w"] / 2), Z2(18), lxr, 368, [f"filament {D['fil_l']:.0f} mm, 3 V, 2700 K, on the axis:", f"{E['i_lamp_max']:.0f} mA flat out, held by its lower tab"])
    label_r(o, X2(pr + pd), Z2(13), lxr, 406, ["lamp post: 1 mm brass rod from the nipple's", "bore down behind the lamp; the return"])
    label_r(o, X2(8.2), Z2(D["nut_bot"] - 1.2), lxr, 444, ["two wires under the roof: + from the live", "rod to the top tab; return, nut to its rod"])
    label_r(o, X2(xl1 + 0.75), Z2(30), lxr, 482, ["the back rods, one behind the other: past", f"the deck at r {D['ast_r']:.1f}; the live one ends {ltl:.0f} up,", "booted; the other through the dome, soldered"])
    label_r(o, X2(br), Z2(D["bush_t"] / 2), lxr, 528, ["bearing: a wheel for a washer: a 3 mm ring", "of the 5/8 in tube glued on the deck, two", "1 mm spokes, a 5 mm tube ring as the hub"])
    label_r(o, X2(D["deck_d"] / 2), Z2(-D["deck_t"] / 2), lxr, 570, [f"gallery: turned check ring Ø{D['deck_d']:.1f} × {D['deck_t']:.0f}; its", "11 mm hole as bought; four rod holes (dashed)"])
    label_r(o, X2(tr), Z2(-14), lxr, 608, [f"spine: the owned 4 mm tube, {D['tube_len']:.0f} long, from", f"the motor's D shaft; below the deck the rods", f"lean {D['leg_deg']:.1f}° out to Ø{D['cage_d0']:.0f} at the coaster"])

    # ---------------------------------------------------------------- the foot, looking down (front at the bottom), 3.6 px per mm
    bi, bj, sb = 972, 125, 3.6
    fw, fy0, fy1 = 14.0, -12.0, 30.0
    BX = lambda xm: bi + (fw + xm) * sb      # noqa: E731
    BY = lambda ym: bj + (fy1 - ym) * sb     # noqa: E731  back (+y) is up
    o.append(T(bi, 110, "The foot, looking down", "h2"))
    o.append(rect(BX(-fw), BY(fy1), BX(fw), BY(fy0), "ghost"))
    o.append(rect(BX(-D["hold_w"] / 2), BY(D["hold_y0"]), BX(D["hold_w"] / 2), BY(D["hold_y1"]), "part"))
    o.append(circ(BX(0), BY(D["hold_y0"] + 0.2 + D["cell_d"] / 2), D["cell_d"] / 2 * sb, "blk"))
    o.append(rect(BX(-D["mot_w"] / 2), BY(-D["mot_t"] / 2), BX(D["mot_w"] / 2), BY(D["mot_t"] / 2), "steel"))
    o.append(circ(BX(0), BY(0), D["mag_r"] * sb, "glow"))
    o.append(circ(BX(0), BY(0), D["tube_od"] / 2 * sb, "brass"))
    o.append(f'<line x1="{BX(0):.1f}" y1="{BY(D["tube_od"] / 2):.1f}" x2="{BX(0):.1f}" y2="{BY(D["tube_od"] / 2 + D["arm_len"]):.1f}" class="rodln"/>')
    o.append(circ(BX(0), BY(D["mag_r"]), D["mag_d"] / 2 * sb, "mag"))
    o.append(circ(BX(0), BY(D["reed_y"]), D["reed_d"] / 2 * sb, "glass"))
    for sgn in (-1, 1):
        o.append(circ(BX(sgn * D["hole_x"]), BY(D["hole_y"]), D["hole_d"] / 2 * sb, "ghost"))
    for i, t in enumerate(["motor on the axis; the arm", "on the spine, its magnet over", "the reed behind the motor;", "the cell in its black tray", "at the back; two wire holes", "dashed; no house: all open"]):
        o.append(T(bi, 282 + i * 13, t, "fn"))

    # ---------------------------------------------------------------- plan, looking down with the roof off, 2.6 px per mm
    cx, cy, sp = 1225, 215, 2.6
    o.append(T(1100, 90, "Plan, roof off", "h2"))
    o.append(circ(cx, cy, D["disc_d"] / 2 * sp, "brass"))
    o.append(rect(cx - D["notch_w"] / 2 * sp, cy - D["disc_d"] / 2 * sp, cx + D["notch_w"] / 2 * sp, cy - (D["disc_d"] / 2 - 2.0) * sp, "cavity"))
    o.append(rect(cx - 3 * sp, cy + (D["disc_d"] / 2 - 2.0) * sp, cx + 3 * sp, cy + D["disc_d"] / 2 * sp, "part"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            o.append(f'<line x1="{cx + sx * xl0 * sp:.1f}" y1="{cy + sy * xl0 * sp:.1f}" x2="{cx + sx * xl1 * sp:.1f}" y2="{cy + sy * xl1 * sp:.1f}" class="ghost"/>')
            o.append(circ(cx + sx * xl0 * sp, cy + sy * xl0 * sp, D["hole_leg"] / 2 * sp + 1, "rodfill"))
    o.append(circ(cx, cy, D["deck_d"] / 2 * sp, "brass"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            if sx < 0 and sy < 0:   # back-left: the live rod in its white sleeve
                o.append(circ(cx + sx * xl1 * sp, cy + sy * xl1 * sp, D["sleeve_od"] / 2 * sp + 1.5, "ivory"))
            o.append(circ(cx + sx * xl1 * sp, cy + sy * xl1 * sp, D["rod_d"] / 2 * sp + 0.6, "rodfill"))
    o.append(circ(cx, cy, D["bush_d"] / 2 * sp, "brass"))
    o.append(arc_path(cx, cy, D["drum_od"] / 2 * sp, 90 + D["win_deg"] / 2, 450 - D["win_deg"] / 2, "brassring"))
    o.append(circ(cx, cy, D["tube_od"] / 2 * sp, "brassdk"))
    o.append(circ(cx, cy, D["fil_w"] / 2 * sp + 1, "warm"))
    o.append(circ(cx, cy - D["post_r"] * sp, D["post_d"] / 2 * sp + 0.6, "brassdk"))
    for a in (90 - D["win_deg"] / 2, 90 + D["win_deg"] / 2):
        o.append(f'<line x1="{cx + 24 * math.cos(math.radians(a)):.1f}" y1="{cy + 24 * math.sin(math.radians(a)):.1f}" x2="{cx + 112 * math.cos(math.radians(a)):.1f}" y2="{cy + 112 * math.sin(math.radians(a)):.1f}" class="beam"/>')
    o.append(arc_path(cx, cy, 108, 90 - D["win_deg"] / 2, 90 + D["win_deg"] / 2, "beam"))
    o.append(T(cx, cy + 128, f"front at the bottom; the {D['win_deg']:.0f}° beam to you", "fn", "middle"))
    col1 = [f"coaster Ø{D['disc_d']:.0f}; the four feet at r {D['leg_r0']:.0f} (Ø{D['cage_d0']:.0f}), leaning in", f"deck Ø{D['deck_d']:.1f}; the rods pass it at r {D['ast_r']:.1f} (Ø{D['cage_d1']:.0f})",
            f"shutter Ø{D['drum_od']:.1f}, open {D['win_deg']:.0f}° to the front, on two bars", f"spine Ø{D['tube_od']:.0f} in the wheel's hub · post at r {D['post_r']:.1f}, behind"]
    col2 = ["no house: motor, tray, reed and arm on the bare brass", "the live rod, back-left, ringed white: its sleeve",
            f"notch {D['notch_w']:.0f} wide in the rim at the back: charge and flash", "the button in the rim at the front: the black mark", f"turns {E['rpm_target']:.0f} rpm: {E['period']:.1f} s a revolution"]
    for i, t in enumerate(col1):
        o.append(T(1062, 358 + i * 14, t, "fn"))
    for i, t in enumerate(col2):
        o.append(T(1062, 418 + i * 14, t, "fn"))

    # ---------------------------------------------------------------- section through the foot and the coaster, front on the left, 3.3 px per mm
    s3 = 3.3
    xc, y3 = 1035, 778
    Y3 = lambda ym: xc + ym * s3   # noqa: E731  front negative
    Z3 = lambda zm: y3 - zm * s3   # noqa: E731  above the coaster's top
    o.append(T(968, 520, "The foot and the coaster, cut", "h2")); o.append(T(968, 536, "front on the left", "h2"))
    o.append(rect(Y3(-D["disc_d"] / 2), Z3(-D["disc_t"]), Y3(D["disc_d"] / 2), Z3(0), "brass"))
    o.append(rect(Y3(-D["hollow_d"] / 2), Z3(-D["disc_t"]), Y3(D["hollow_d"] / 2), Z3(-D["plate_t"]), "cavity"))
    o.append(rect(Y3(D["hollow_d"] / 2), Z3(-D["disc_t"]), Y3(D["disc_d"] / 2), Z3(-D["disc_t"] + D["notch_h"]), "cavity"))
    for yy_ in (-34, -31, 0, 3):
        xx = Y3(yy_)
        o.append(f'<line x1="{xx}" y1="{Z3(-D["disc_t"] + 0.6)}" x2="{xx + 10}" y2="{Z3(-D["plate_t"] - 0.6)}" class="hatch"/>')
    o.append(rect(Y3(-29), Z3(-D["plate_t"]), Y3(-4), Z3(-D["plate_t"] - D["mx_t"]), "board"))
    cy0 = D["disc_d"] / 2 - D["chg_l"]
    o.append(rect(Y3(cy0), Z3(-D["plate_t"]), Y3(D["disc_d"] / 2 - 0.5), Z3(-D["plate_t"] - 1.6), "board"))
    o.append(rect(Y3(cy0 + 2), Z3(-D["plate_t"] - 1.6), Y3(cy0 + 20), Z3(-D["plate_t"] - D["chg_t"]), "board"))
    o.append(rect(Y3(D["disc_d"] / 2 - 9), Z3(-D["plate_t"] - 1.6), Y3(D["disc_d"] / 2), Z3(-D["plate_t"] - 1.6 - D["usb_h"]), "usb"))
    o.append(rect(Y3(-2.5), Z3(-D["plate_t"] - 0.3), Y3(2.5), Z3(-D["plate_t"] - 2.0), "steel"))
    o.append(rect(Y3(D["hole_y"] - D["hole_d"] / 2), Z3(-D["plate_t"]), Y3(D["hole_y"] + D["hole_d"] / 2), Z3(0), "ghost"))
    zb3 = -(D["disc_t"] - D["btn_z"])   # the button's plunger, inside the rim at the front
    o.append(rect(Y3(-D["hollow_d"] / 2), Z3(zb3 - 3.0), Y3(-D["hollow_d"] / 2 + 3.5), Z3(zb3 + 3.0), "part"))
    o.append(rect(Y3(-D["disc_d"] / 2 - 1.0), Z3(zb3 - 1.0), Y3(-D["hollow_d"] / 2), Z3(zb3 + 1.0), "steel"))
    o.append(rect(Y3(D["hold_y0"]), Z3(0), Y3(D["hold_y1"]), Z3(D["hold_h"]), "part"))
    o.append(rect(Y3(D["hold_y0"] + 0.2), Z3(D["cell_z0"]), Y3(D["hold_y0"] + 0.2 + D["cell_d"]), Z3(D["cell_z0"] + D["cell_l"]), "blk"))
    for zz in (D["cell_z0"] - 2.5, D["cell_z0"] + D["cell_l"] + 0.5):
        o.append(f'<path d="M{Y3(D["hold_y0"] + 4)},{Z3(zz)} l4,2 l4,-2 l4,2 l4,-2" class="hair"/>')
    o.append(f'<path d="M{Y3(D["hold_y0"] + 1.2)},{Z3(0.5)} L{Y3(D["hole_y"])},{Z3(0.5)} L{Y3(D["hole_y"])},{Z3(-1.2)}" class="hair"/>')
    mt = D["mot_t"] / 2
    o.append(rect(Y3(-mt), Z3(0), Y3(mt), Z3(D["mot_z0"]), "glue"))
    o.append(rect(Y3(-mt), Z3(D["mot_z0"]), Y3(mt), Z3(D["mot_z0"] + D["mot_l"] - D["gear_l"]), "board"))
    o.append(rect(Y3(-mt), Z3(D["mot_z0"] + D["mot_l"] - D["gear_l"]), Y3(mt), Z3(D["mot_z0"] + D["mot_l"]), "steel"))
    zf = D["mot_z0"] + D["mot_l"]
    o.append(rect(Y3(-D["shaft_d"] / 2), Z3(zf), Y3(D["shaft_d"] / 2), Z3(zf + D["shaft_l"]), "steel"))
    ztop = 62
    for sgn in (-1, 1):
        o.append(rect(Y3(sgn * tr), Z3(zf + 1), Y3(sgn * ti), Z3(ztop), "brass"))
    o.append(rect(Y3(-ti), Z3(zf + D["shaft_l"]), Y3(ti), Z3(ztop), "cavity"))
    o.append(f'<path d="M{Y3(-3.5)},{Z3(ztop) + 4} l3,-7 l3,7 l3,-7 l3,7" class="hair"/>')
    o.append(rect(Y3(tr), Z3(D["z_collar"]), Y3(tr + D["arm_len"]), Z3(D["z_collar"] + D["arm_d"]), "brassdk"))
    o.append(rect(Y3(D["mag_r"] - D["mag_d"] / 2), Z3(D["z_collar"] - D["mag_t"]), Y3(D["mag_r"] + D["mag_d"] / 2), Z3(D["z_collar"]), "mag"))
    ry = D["reed_y"]
    o.append(rect(Y3(ry - 1), Z3(D["reed_bot"]), Y3(ry + 1), Z3(D["reed_top"]), "glass"))
    o.append(f'<path d="M{Y3(ry)},{Z3(D["reed_bot"])} L{Y3(ry)},{Z3(0)} M{Y3(ry)},{Z3(D["reed_top"])} L{Y3(ry - 1.4)},{Z3(D["reed_top"])} L{Y3(ry - 1.4)},{Z3(0)}" class="hair"/>')
    o.append(dim_v(Y3(-D["disc_d"] / 2) - 14, Z3(-D["disc_t"]), Z3(0), f"{D['disc_t']:.0f}", False))
    o.append(dim_v(Y3(D["hold_y1"]) + 14, Z3(0), Z3(D["hold_h"]), f"{D['hold_h']:.0f}", True))
    lxr2 = 1170
    label_r(o, Y3(D["hold_y1"] - 0.5), Z3(D["hold_h"] - 2), lxr2, 556, ["no house: the motor, the tray, the", "reed and the magnet arm stand in", "the open on the coaster's top"])
    label_r(o, Y3(D["hold_y1"] - 0.5), Z3(22), lxr2, 602, ["cell: a 16340 standing in the owned", "black tray behind the motor; its", "leads down the left hole"])
    label_r(o, Y3(mt), Z3(12), lxr2, 648, ["N20 motor on a 2 mm bed, shaft on", "the axis; the spine over its D", "shaft; the magnet on a 1 mm arm", "over the reed behind the motor"])
    label_r(o, Y3(D["disc_d"] / 2), Z3(-D["disc_t"] + 3), lxr2, 702, ["charger in the hollow, glued up to", "the ceiling, USB-C in the notch;", "the controller beside it, cut away;", "driver in front; washers fill the rest"])
    o.append(T(Y3(-D["disc_d"] / 2), Z3(-D["disc_t"]) + 16, f"left: the button inside the rim at the front, its plunger through a Ø{D['btn_hole']:.1f} hole", "fn"))
    o.append(T(Y3(-D["disc_d"] / 2), Z3(-D["disc_t"]) + 29, f"{D['btn_z']:.1f} mm up from the bottom edge; press the front of the coaster", "fn"))

    # ---------------------------------------------------------------- how it behaves, and the key numbers
    bx, by = 522, 628
    o.append(T(bx, by, "How it behaves", "h2"))
    lines = [("off", "lamp dark, shutter closed (brass to you), boost asleep"),
             ("lamp", f"shutter parked open to you, filament {E['lamp_duty'] * 100:.0f} % ({E['i_lamp']:.0f} mA)"),
             ("beacon", f"the shutter turns, {E['period']:.1f} s a revolution: a {E['pass_s']:.1f} s sweep, then brass"),
             ("button", "in the rim at the front. Short press: rotation on/off (off parks the window"),
             ("", "on you); long: lamp off, low, full (off closes the shutter)"),
             ("cell", f"about {E['h_beacon']:.0f} h of beacon, {E['h_lamp']:.0f} of lamp; low: dim, park, sleep"),
             ("charge", f"USB-C at the back, {E['h_charge']:.1f} h; it runs from the cable meanwhile")]
    for i, (k, v) in enumerate(lines):
        yy = by + 18 + i * 14
        o.append(T(bx, yy, k, "lab")); o.append(T(bx + 54, yy, v, "fn"))
    o.append(T(bx, by + 124, "Key numbers", "h2"))
    keys = [f"{D['height']:.0f} tall · Ø{D['disc_d']:.0f} base · cage Ø{D['cage_d0']:.0f} → Ø{D['cage_d1']:.0f} over {D['leg_h']:.0f} · lantern open {D['cap_rim']:.1f}",
            f"{D['mass']:.0f} g, centre of mass {D['cg']:.0f} up, tips at {D['tip_deg']:.0f}° ({D['push_n']:.1f} N at the ball);",
            f"with {D['ballast_g']:.0f} g of steel in the coaster: {D['cg_b']:.0f} up, {D['tip_deg_b']:.0f}° ({D['push_n_b']:.1f} N)",
            f"from the cell: {E['cell_typ']:.0f} mA beacon ({E['h_beacon']:.0f} h), {E['cell_lamp']:.0f} lamp ({E['h_lamp']:.0f} h), {E['cell_idle']:.0f} asleep",
            f"rail {E['rail_typ']:.0f} mA typical, {E['rail_peak']:.0f} peak · lamp {E['i_lamp_max']:.0f} mA ({E['lamp_w'] * 1000:.0f} mW) · charge {E['chg_ma']:.0f} mA",
            f"cuts: rods 4 × {D['leg_len']:.0f} · spine {D['tube_len']:.0f} · shutter {D['drum_h']:.0f} · post {D['post_len']:.0f} · 1 mm rod {D['hw_rod']:.0f} · two {D['bush_t']:.0f} mm rings"]
    for i, k in enumerate(keys):
        o.append(T(bx, by + 142 + i * 13, k, "fn"))
    o.append(T(20, 848, f"Rev {REV}, {STATUS}, not built. The check ring's thickness, the vase cap's height and the coaster's hollow are assumed: measure them and rerun the script. Sources: the listings and the pages named in the record.", "sub"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Desk lighthouse form sheet">{SHEET_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- sheet 2: the wiring
def wiring_sheet():
    rt = Router()
    w = rt.wire
    o = [T(20, 30, "Desk lighthouse: every connection on one sheet, the power chain first", "h1"),
         T(20, 48, "A dot is a joint. A line that hops over another does not touch it. Thick = 30 AWG wire you solder. Thin = a lead or a cable. Brass-filled = a rod of the frame, carrying current. Left to right: cell, charger, controller, driver, loads. Zero crossings.", "sub")]

    # the charger and the cell, left
    CX, CY, CW, CH = 60, 95, 240, 235
    o.append(block(CX, CY, CW, CH, "Charger", "bq25185 + 5 V boost, in the hollow", ty=22))
    o.append(pin(rt, CX + CW, 120, "5V", "R", "V5")); o.append(pin(rt, CX + CW, 150, "BAT", "R", "VBAT"))
    o.append(pin(rt, CX + CW, 270, "G", "R", "GND")); o.append(pin(rt, CX + CW, 300, "EN", "R", "EN"))
    o.append(pin(rt, 120, CY + CH, "B+", "B", "VBAT")); o.append(pin(rt, 180, CY + CH, "B−", "B", "GND"))
    for i, t in enumerate([f"USB-C in, {E['chg_ma']:.0f} mA (jumper cut);", "power path: plugged in, the", "loads run from the cable and", "the rest fills the cell", "", "boost TPS61023: 5 V, 1 A;", "EN low = off", "", "terminal block and JST socket", "off; wires on the pads"]):
        if t:
            o.append(T(CX + 14, 160 + i * 13, t, "fn"))
    o.append(f'<rect x="{CX + 170}" y="{CY + CH - 26}" width="44" height="16" rx="3" class="usb"/>'); o.append(T(CX + 192, CY + CH - 14, "USB-C", "fn", "middle"))
    o.append(block(60, 360, 160, 90, "Cell", "16340, 950 mAh", ty=22))
    o.append(pin(rt, 120, 360, "", "T", "VBAT")); o.append(pin(rt, 180, 360, "", "T", "GND"))
    o.append(T(112, 377, "+", "pin", "end")); o.append(T(188, 377, "−", "pin"))
    o.append(T(74, 414, "Nitecore NL169, protected,", "fn")); o.append(T(74, 428, "button top, in the owned", "fn")); o.append(T(74, 442, "tray; never soldered", "fn"))
    o.append(w([(120, CY + CH), (120, 360)], "rod", "VBAT")); o.append(w([(180, CY + CH), (180, 360)], "rod", "GND"))
    o.append(T(150, 349, "the tray's leads", "fn", "middle"))
    o.append(block(190, 480, 160, 60, "USB-C adapter", "charging: any 1 A adapter"))
    o.append(w([(CX + 192, CY + CH - 8), (CX + 192, 480)], "thin", "CHG"))
    o.append(T(270, 558, f"{E['chg_ma']:.0f} mA; {E['h_charge']:.1f} h from empty", "fn", "middle"))

    # the controller, centre left
    EX, EY, EW, EH = 420, 95, 280, 350
    o.append(block(EX, EY, EW, EH, "ESP32-C3 SuperMini", "in the coaster's hollow; USB-C in the notch", ty=20))
    o.append(pin(rt, EX, 150, "5V", "L", "V5C", "3.5 to 4.0 V, from the cell", EX + 36))
    o.append(pin(rt, EX, 210, "GPIO4", "L", "SENSE", "cell sense (ADC)", EX + 66))
    o.append(pin(rt, EX, 270, "GND", "L", "GND"))
    o.append(pin(rt, EX, 300, "GPIO7", "L", "EN", "boost on/off", EX + 66))
    o.append(pin(rt, EX + EW, 180, "GND", "R", "GND"))
    o.append(pin(rt, EX + EW, 235, "GPIO0", "R", "IN1", "shutter PWM", EX + EW - 66))
    o.append(pin(rt, EX + EW, 265, "GPIO1", "R", "IN2", "direction, brake", EX + EW - 66))
    o.append(pin(rt, EX + EW, 295, "GPIO3", "R", "IN3", "lamp PWM", EX + EW - 66))
    o.append(pin(rt, EX + EW, 350, "GPIO6", "R", "REED", "index, pull-up", EX + EW - 66))
    o.append(pin(rt, 600, EY + EH, "GPIO10", "B", "BTN")); o.append(pin(rt, 680, EY + EH, "GND", "B", "GND"))
    for i, t in enumerate(["no Wi-Fi: the button", "in the rim is the whole", "interface", "GPIO2, 8, 9: straps,", "unwired; 5, 20, 21 free", "LEDC 20 kHz motor, 5 kHz", "lamp; the motor ramps up"]):
        o.append(T(EX + 14, 322 + i * 12.5, t, "fn"))
    o.append(f'<rect x="{EX + 14}" y="{EY + EH - 26}" width="40" height="16" rx="3" class="usb"/>'); o.append(T(EX + 34, EY + EH - 14, "USB-C", "fn", "middle"))
    o.append(T(EX + 62, EY + EH - 14, "flashing; the diode guards the cell", "fn"))
    # the power chain between them
    o.append(w([(CX + CW, 150), (350, 150)], "rod", "VBAT")); o.append(diode_h(350, 380, 150)); o.append(w([(380, 150), (EX, 150)], "rod", "V5C"))
    o.append(T(365, 134, "SS14", "lab", "middle"))
    o.append(dot(330, 150)); o.append(w([(330, 150), (330, 210)], "rod", "DIV1")); o.append(zigzag_h(rt, 330, 400, 210, "DIV1"))
    o.append(dot(400, 210)); o.append(w([(400, 210), (EX, 210)], "rod", "SENSE")); o.append(zigzag_v(rt, 400, 210, 270, "DIV2")); o.append(dot(400, 270))
    o.append(T(365, 198, "100 k", "lab", "middle")); o.append(T(388, 244, "100 k", "lab", "end"))
    o.append(w([(CX + CW, 270), (EX, 270)], "rod", "GND")); o.append(T(348, 284, "ground", "fn", "middle"))
    o.append(w([(CX + CW, 300), (EX, 300)], "rod", "EN")); o.append(T(360, 314, "GPIO7 → EN", "lab", "middle"))
    o.append(w([(CX + CW, 120), (360, 120), (360, 80), (784, 80), (784, 150), (820, 150)], "rod", "V5"))
    o.append(T(572, 72, "the boost's 5 V: the rail for the motor and the lamp, nothing else", "lab", "middle"))

    # the driver, centre right
    DX, DY, DW, DH = 820, 95, 240, 320
    o.append(block(DX, DY, DW, DH, "MX1508 dual H-bridge", "2 to 10 V · 1.5 A a channel · pads", ty=20))
    o.append(pin(rt, DX, 150, "VCC", "L", "V5", "the 5 V rail", DX + 52))
    o.append(pin(rt, DX, 180, "GND", "L", "GND"))
    o.append(pin(rt, DX, 205, "IN4", "L", "GND", "tied low", DX + 46))
    o.append(pin(rt, DX, 235, "IN1", "L", "IN1", "A: speed", DX + 46))
    o.append(pin(rt, DX, 265, "IN2", "L", "IN2", "A: direction", DX + 46))
    o.append(pin(rt, DX, 295, "IN3", "L", "IN3", "B: lamp", DX + 46))
    o.append(pin(rt, DX + DW, 255, "OUT1", "R", "MOT1", "channel A", DX + DW - 56))
    o.append(pin(rt, DX + DW, 285, "OUT2", "R", "MOT2"))
    o.append(pin(rt, DX + DW, 360, "OUT3", "R", "LAMP", "channel B", DX + DW - 56))
    o.append(pin(rt, DX + DW, 390, "OUT4", "R", "NC", "unused", DX + DW - 56))
    o.append(T(DX + 120, 330, "3.3 V inputs · flyback diodes inside", "fn", "middle"))
    o.append(T(DX + 120, 344, "A turns the shutter, B lights the lamp", "fn", "middle"))
    o.append(w([(EX + EW, 180), (DX, 180)], "rod", "GND")); o.append(T(760, 172, "one ground", "fn", "middle"))
    o.append(w([(DX, 205), (800, 205), (800, 180)], "rod", "GND")); o.append(dot(800, 180))
    o.append(w([(EX + EW, 235), (DX, 235)], "rod", "IN1")); o.append(T(760, 227, "GPIO0 → IN1", "lab", "middle"))
    o.append(w([(EX + EW, 265), (DX, 265)], "rod", "IN2")); o.append(T(760, 257, "GPIO1 → IN2", "lab", "middle"))
    o.append(w([(EX + EW, 295), (DX, 295)], "rod", "IN3")); o.append(T(760, 287, "GPIO3 → IN3", "lab", "middle"))

    # the motor and the lamp, right
    MX, MY, MW, MH = 1160, 190, 180, 110
    o.append(block(MX, MY, MW, MH, "Shutter motor", "N20, 6 V 30 rpm, at the foot", ty=22))
    o.append(pin(rt, MX, 255, "M1", "L", "MOT1")); o.append(pin(rt, MX, 285, "M2", "L", "MOT2"))
    o.append(w([(DX + DW, 255), (MX, 255)], "rod", "MOT1")); o.append(w([(DX + DW, 285), (MX, 285)], "rod", "MOT2"))
    o.append(T(1110, 247, f"{E['mot_ma']:.0f} mA", "fn", "middle"))
    o.append(T(MX + 44, 266, "tabs bent flat; two", "fn")); o.append(T(MX + 44, 280, "wires up the right hole", "fn"))
    LX, LY, LW, LH = 1180, 310, 160, 120
    o.append(block(LX, LY, LW, LH, "Lamp", f"{D['fil_l']:.0f} mm filament, 3 V", ty=22))
    o.append(pin(rt, LX, 360, "+ tab", "L", "LAMP"))
    GX = LX + 110
    o.append(pin(rt, GX, LY + LH, "", "B", "GND")); o.append(T(GX - 8, LY + LH - 6, "− tab", "pin", "end"))
    o.append(T(LX + 64, 362, "+ tab: the one", "fn")); o.append(T(LX + 64, 376, "with the hole;", "fn")); o.append(T(LX + 64, 390, "− tab on the post", "fn"))
    o.append(T(LX + 14, 408, f"{E['i_lamp_max']:.0f} mA flat out", "fn"))
    o.append(w([(DX + DW, 360), (1068, 360)], "rod", "LAMP")); o.append(zigzag_h(rt, 1068, 1096, 360, "LAMP"))
    o.append(w([(1096, 360), (1104, 360)], "rod", "LAMP")); o.append(w([(1104, 360), (1170, 360)], "rodfr", "LAMP")); o.append(w([(1170, 360), (LX, 360)], "rod", "LAMP"))
    o.append(T(1082, 381, "2 × 47 Ω", "lab", "middle")); o.append(T(1137, 347, "back-left rod", "lab", "middle"))
    o.append(w([(GX, LY + LH), (GX, 470)], "rod", "GND")); o.append(w([(GX, 470), (GX, 600)], "rodfr", "GND")); o.append(w([(GX, 600), (GX, 620)], "rod", "GND"))
    o.append(T(GX - 10, 458, "post, nut, a wire", "fn", "end"))
    o.append(T(GX - 10, 592, "back-right rod", "lab", "end"))

    # the reed, the button, the computer, and one return lane
    RX, RY, RW, RH = 1100, 470, 160, 90
    o.append(block(RX, RY, RW, RH, "Reed switch", "2 × 14 glass, at the foot", ty=22))
    o.append(pin(rt, RX, 520, "leg 1", "L", "REED")); o.append(pin(rt, RX, 545, "leg 2", "L", "GND"))
    o.append(w([(EX + EW, 350), (740, 350), (740, 520), (RX, 520)], "rod", "REED")); o.append(T(920, 512, "GPIO6 → reed: the index, once a turn", "lab", "middle"))
    o.append(w([(RX, 545), (1070, 545), (1070, 620)], "rod", "GND"))
    BX, BY = 560, 520
    o.append(block(BX, BY, 140, 60, "Button", "6 mm tactile, in the rim", ty=24))
    o.append(pin(rt, 600, BY, "", "T", "BTN")); o.append(pin(rt, 660, BY + 60, "", "B", "GND"))
    o.append(T(590, BY - 6, "leg 1", "fn", "end")); o.append(T(670, BY + 76, "leg 2", "fn"))
    o.append(w([(600, EY + EH), (600, BY)], "rod", "BTN")); o.append(T(612, 486, "GPIO10 → button", "lab"))
    o.append(w([(660, BY + 60), (660, 620)], "rod", "GND"))
    o.append(w([(680, EY + EH), (680, 620)], "rod", "GND"))
    o.append(w([(660, 620), (GX, 620)], "rod", "GND")); o.append(dot(660, 620)); o.append(dot(680, 620)); o.append(dot(1070, 620)); o.append(dot(GX, 620))
    o.append(T(880, 638, "the button's, the reed's and the lamp's returns share one lane into the controller's GND", "fn", "middle"))
    o.append(block(374, 520, 160, 60, "Computer", "flashing only, in the notch"))
    o.append(w([(454, 520), (454, EY + EH - 10)], "thin", "USB"))

    # the budget, along the bottom
    NY = 676
    o.append(T(20, NY - 10, "The budget: from the cell, and on the boost's 5 V rail", "h2"))
    cols = [("cell", f"{E['cell_typ']:.0f} mA with the beacon turning and the lamp at {E['lamp_duty'] * 100:.0f} %: about {E['h_beacon']:.0f} h · {E['cell_lamp']:.0f} mA lamp alone: {E['h_lamp']:.0f} h · {E['cell_idle']:.0f} mA asleep, boost off: {E['h_idle'] / 24:.0f} days"),
            ("rail", f"{E['rail_typ']:.0f} mA typical on the boost's 5 V, {E['rail_peak']:.0f} at most in normal running; the boost stalls if more than 200 mA is switched on in a step, so the motor ramps"),
            ("motor", f"{E['mot_ma']:.0f} turning at {E['duty_mot'] * 100:.0f} % duty ({E['rpm_target']:.0f} rpm); about {E['mot_stall']:.0f} if the shutter jams, which the reed's silence reports"),
            ("lamp", f"{E['i_lamp_max']:.0f} flat out, {E['i_lamp']:.0f} at the {E['lamp_duty'] * 100:.0f} % default; {E['lamp_w'] * 1000:.0f} mW in the lantern, {E['p_res_each'] * 1000:.0f} mW in each resistor; up one rod, down another"),
            ("controller", f"{E['c3_avg']:.0f} from the cell through the diode, no Wi-Fi; the divider {E['i_div_ua']:.0f} µA"),
            ("charge", f"{E['chg_ma']:.0f} mA with the jumper cut, about {E['h_charge']:.1f} h from empty; plugged in, the lighthouse runs from the cable and the cell fills with the rest")]
    for i, (name, note) in enumerate(cols):
        yy = NY + 14 + i * 17
        o.append(T(40, yy, name, "lab")); o.append(T(130, yy, note, "fn"))
    o.append(T(40, NY + 128, "Never: the cell without the diode between it and the controller · the charger's jumper uncut · the lamp without its resistors · the live rod touching any other brass (meter it) · an iron near the cell or the magnet.", "fn"))

    bad, crossings = rt.check()
    for b in bad:
        print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    o.append(T(20, 848, f"Rev {REV}, {STATUS}, not built. {crossings} crossing(s) on this sheet. Sources: the charger's pinouts page, the SuperMini notes (5V = VBUS), the MX1508 datasheet, the satellite's record of the same cell, charger and diode, the listings.", "sub"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Desk lighthouse wiring sheet">{SHEET_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- sheet 3: templates at actual size
def templates_sheet():
    k = W / 262.0        # the PDF prints the sheet 262 mm wide: 5.19 px per mm
    o = [T(20, 30, "Desk lighthouse: templates at actual size", "h1"),
         T(20, 48, "Print landscape on Letter at Actual size: the 50 mm bar measures 50 mm. Prick the hole centres through the paper onto the brass; drill with the cordless drill at its slowest, saw with the jeweler's saw, file to the line.", "sub")]
    c45 = math.cos(math.radians(45))

    # the coaster's top
    cx, cy = 250, 300
    o.append(T(60, 92, "The coaster's top, front at the bottom", "h2"))
    o.append(circ(cx, cy, D["disc_d"] / 2 * k, "tmpl"))
    o.append(circ(cx, cy, D["hollow_d"] / 2 * k, "ghost"))
    o.append(circ(cx, cy, D["leg_r0"] * k, "centre"))
    o.append(f'<line x1="{cx}" y1="{cy - 205}" x2="{cx}" y2="{cy + 205}" class="centre"/><line x1="{cx - 205}" y1="{cy}" x2="{cx + 205}" y2="{cy}" class="centre"/>')
    f0 = D["leg_r0"] * c45 * k
    for sx in (-1, 1):
        for sy in (-1, 1):
            live = sx < 0 and sy < 0
            o.append(circ(cx + sx * f0, cy + sy * f0, (D["hole_live"] if live else D["hole_leg"]) / 2 * k, "tmplhole"))
    o.append(T(cx - f0 + 10, cy - f0 - 8, f"Ø{D['hole_live']:.1f} live, back-left", "dimlab"))
    o.append(T(cx + f0 - 10, cy - f0 + 22, f"Ø{D['hole_leg']:.1f} back-right", "dimlab", "end"))
    o.append(T(cx - f0 + 10, cy + f0 + 18, f"Ø{D['hole_leg']:.1f}", "dimlab")); o.append(T(cx + f0 - 10, cy + f0 + 18, f"Ø{D['hole_leg']:.1f}", "dimlab", "end"))
    for sgn in (-1, 1):
        o.append(circ(cx + sgn * D["hole_x"] * k, cy - D["hole_y"] * k, D["hole_d"] / 2 * k, "tmplhole"))
    o.append(T(cx + D["hole_x"] * k + 14, cy - D["hole_y"] * k + 4, f"two Ø{D['hole_d']:.1f}, the wires", "dimlab"))
    o.append(rect(cx - D["notch_w"] / 2 * k, cy - D["disc_d"] / 2 * k, cx + D["notch_w"] / 2 * k, cy - (D["disc_d"] / 2 - 2.0) * k, "tmplhole"))
    o.append(T(cx, cy - D["disc_d"] / 2 * k + 26, f"notch in the rim: {D['notch_w']:.0f} wide, {D['notch_h']:.1f} up from the bottom edge", "dimlab", "middle"))
    o.append(circ(cx, cy + D["disc_d"] / 2 * k, D["btn_hole"] / 2 * k, "tmplhole"))
    o.append(T(cx + 16, cy + D["disc_d"] / 2 * k + 4, f"Ø{D['btn_hole']:.1f} through the rim at the front, {D['btn_z']:.1f} up from the bottom edge", "dimlab"))
    o.append(T(cx + D["leg_r0"] * k + 4, cy + 44, f"r {D['leg_r0']:.0f}", "dimlab"))
    o.append(T(60, 512, f"The feet sit on the Ø{D['cage_d0']:.0f} circle at 45°; the wire holes sit between the motor and the tray, {D['hole_x']:.0f} either side of", "fn"))
    o.append(T(60, 526, f"the axis and {D['hole_y']:.1f} behind it. Drill the 1.8, 2.3 and 3.5 straight through the 1.3 mm top; the Ø{D['btn_hole']:.1f} for the button goes", "fn"))
    o.append(T(60, 540, f"through the rim at the front. Saw the {D['notch_w']:.0f} mm notch from the rim's bottom edge at the back with two cuts, break it out, file.", "fn"))

    # the spine's hardware: rod and tube rings, actual size
    o.append(T(480, 92, "The spine's hardware: 1 mm rod and tube rings, actual size", "h2"))
    hx, hy = 560, 200
    rr = D["bush_d"] / 2 * k
    o.append(circ(hx, hy, rr, "tmpl")); o.append(circ(hx, hy, (D["bush_d"] / 2 - D["drum_wall"]) * k, "ghost"))
    o.append(circ(hx, hy, D["hub_od"] / 2 * k, "tmpl")); o.append(circ(hx, hy, D["bush_hole"] / 2 * k, "tmplhole"))
    for sgn in (-1, 1):
        xo, half = hx + sgn * D["hub_od"] / 2 * k, D["spoke_len"] / 2 * k
        o.append(f'<line x1="{xo:.1f}" y1="{hy - half:.1f}" x2="{xo:.1f}" y2="{hy + half:.1f}" class="rodln"/>')
    o.append(T(hx, hy + rr + 16, "the bearing wheel, on the deck", "lab", "middle"))
    o.append(T(hx, hy + rr + 30, f"rim: a {D['bush_t']:.0f} mm ring of the 5/8 in tube", "fn", "middle"))
    o.append(T(hx, hy + rr + 43, f"hub: a {D['bush_t']:.0f} mm ring of the 5 mm tube", "fn", "middle"))
    o.append(T(hx, hy + rr + 56, f"two spokes {D['spoke_len']:.1f}, tangent to the hub", "fn", "middle"))
    bx_, by_ = 790, 200
    rd = (D["drum_od"] / 2 - D["drum_wall"]) * k
    o.append(circ(bx_, by_, D["drum_od"] / 2 * k, "ghost")); o.append(circ(bx_, by_, D["tube_od"] / 2 * k, "tmpl"))
    for sgn in (-1, 1):
        xo, half = bx_ + sgn * D["tube_od"] / 2 * k, D["bar_len"] / 2 * k
        o.append(f'<line x1="{xo:.1f}" y1="{by_ - half:.1f}" x2="{xo:.1f}" y2="{by_ + half:.1f}" class="rodln"/>')
    o.append(T(bx_, by_ + rd + 16, "the shutter's floor", "lab", "middle"))
    o.append(T(bx_, by_ + rd + 30, f"two bars {D['bar_len']:.1f}, tangent to the spine,", "fn", "middle"))
    o.append(T(bx_, by_ + rd + 43, f"{D['floor_z']:.1f} mm up inside the drum (dashed)", "fn", "middle"))
    ax_, ay_ = 1000, 200
    o.append(circ(ax_, ay_, D["tube_od"] / 2 * k, "tmpl"))
    o.append(f'<line x1="{ax_ + D["tube_od"] / 2 * k:.1f}" y1="{ay_:.1f}" x2="{ax_ + (D["tube_od"] / 2 + D["arm_len"]) * k:.1f}" y2="{ay_:.1f}" class="rodln"/>')
    o.append(circ(ax_ + D["mag_r"] * k, ay_, D["mag_d"] / 2 * k, "mag"))
    o.append(T(ax_ + 16, ay_ + 40, "the magnet arm", "lab", "middle"))
    o.append(T(ax_ + 16, ay_ + 54, f"{D['arm_len']:.1f} of 1 mm rod on the spine;", "fn", "middle"))
    o.append(T(ax_ + 16, ay_ + 67, f"the magnet under it at r {D['mag_r']:.0f}", "fn", "middle"))
    for i, t in enumerate([f"Five pieces of 1 mm rod ({D['hw_rod']:.0f} mm in all) and two rings; file the ring ends square.",
                           "Make the wheel on the spine itself: the hub ring on the spine, the spokes soldered to its flanks,",
                           "the rim ring to the spoke ends; it centres itself. Slide it down onto the deck and glue the rim.",
                           "The bars go on last, with the drum: solder them to the spine's flanks, then their ends to the wall."]):
        o.append(T(480, 318 + i * 14, t, "fn"))

    # the deck
    dx, dy = 1200, 200
    o.append(T(1060, 92, "Gallery deck (check ring)", "h2"))
    o.append(circ(dx, dy, D["deck_d"] / 2 * k, "tmpl"))
    o.append(circ(dx, dy, D["deck_hole"] / 2 * k, "tmplhole"))
    o.append(circ(dx, dy, D["bush_d"] / 2 * k, "ghost"))
    a0 = D["ast_r"] * c45 * k
    for sx in (-1, 1):
        for sy in (-1, 1):
            live = sx < 0 and sy < 0
            o.append(circ(dx + sx * a0, dy + sy * a0, (D["hole_live"] if live else D["hole_leg"]) / 2 * k, "tmplhole"))
    o.append(f'<line x1="{dx}" y1="{dy - 104}" x2="{dx}" y2="{dy + 104}" class="centre"/><line x1="{dx - 104}" y1="{dy}" x2="{dx + 104}" y2="{dy}" class="centre"/>')
    o.append(T(dx + 32, dy + 4, "Ø11 as bought", "dimlab"))
    o.append(T(dx - a0 - 6, dy - a0 - 8, f"Ø{D['hole_live']:.1f} live", "dimlab", "end")); o.append(T(dx + a0 + 6, dy - a0 - 8, f"Ø{D['hole_leg']:.1f}", "dimlab"))
    o.append(T(1060, 320, f"The four rods pass at r {D['ast_r']:.1f}, at 45° (front at the bottom).", "fn"))
    o.append(T(1060, 334, f"Dashed: the wheel's rim Ø{D['bush_d']:.1f} over the Ø11 hole;", "fn")); o.append(T(1060, 348, "the live rod's hole, back-left, takes its sleeve.", "fn"))

    # the roof: three rod holes in the dome
    rx_, ry_ = 1200, 472
    o.append(T(rx_, 384, "Roof (vase cap), from above", "h2", "middle"))
    o.append(circ(rx_, ry_, D["cap_d"] / 2 * k, "tmpl"))
    o.append(circ(rx_, ry_, D["cap_hole"] / 2 * k, "tmplhole"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            live = sx < 0 and sy < 0
            o.append(circ(rx_ + sx * a0, ry_ + sy * a0, D["hole_leg"] / 2 * k, "ghost" if live else "tmplhole"))
    o.append(f'<line x1="{rx_}" y1="{ry_ - 104}" x2="{rx_}" y2="{ry_ + 104}" class="centre"/><line x1="{rx_ - 104}" y1="{ry_}" x2="{rx_ + 104}" y2="{ry_}" class="centre"/>')
    o.append(T(rx_ - a0 - 6, ry_ - a0 - 8, "none: the live rod", "dimlab", "end")); o.append(T(rx_ + a0 + 6, ry_ - a0 - 8, f"Ø{D['hole_leg']:.1f}", "dimlab"))
    o.append(T(1060, 590, f"Three Ø{D['hole_leg']:.1f} holes at r {D['ast_r']:.1f}, on the dome's slope:", "fn"))
    o.append(T(1060, 603, "centre-punch, drill from outside; the rods pass", "fn"))
    o.append(T(1060, 616, "through and are soldered flush. Measure the cap first.", "fn"))

    # scale bar
    sx, sy = 1080, 652
    o.append(f'<path d="M{sx},{sy - 8} L{sx},{sy + 8} M{sx + 50*k},{sy - 8} L{sx + 50*k},{sy + 8} M{sx},{sy} L{sx + 50*k},{sy}" class="cut"/>')
    o.append(T(sx + 25 * k, sy - 14, "50 mm: check it with a ruler", "dimlab", "middle"))

    # the shutter's flat pattern
    px, py = 60, 575
    pw, ph = D["drum_circ"] * k, D["drum_h"] * k
    o.append(T(px, py - 10, "The shutter, unrolled: 5/8 in brass tube", "h2"))
    o.append(rect(px, py, px + pw, py + ph, "tmpl"))
    wx0 = px + (pw - D["win_arc"] * k) / 2
    o.append(rect(wx0, py + ph - (D["dwin_z0"] + D["dwin_h"]) * k, wx0 + D["win_arc"] * k, py + ph - D["dwin_z0"] * k, "tmplhole"))
    o.append(T(px + pw / 2, py + ph / 2 + 4, f"{D['win_arc']:.1f} × {D['dwin_h']:.0f}", "dimlab", "middle"))
    o.append(dim_h(px, px + pw, py + ph + 14, f"{D['drum_circ']:.1f} round · {D['drum_h']:.0f} tall", False))
    o.append(T(px, py + ph + 44, f"{D['win_deg']:.0f}° window, {D['dwin_z0']:.0f} up from the bottom end. Wrap the", "fn"))
    o.append(T(px, py + ph + 58, "strip round the tube, prick the corners, saw, file.", "fn"))
    o.append(T(px, py + ph + 72, f"A {D['bush_t']:.0f} mm cut of the same tube is the wheel's rim.", "fn"))

    # one rod, not to scale
    rx0, ry0, rs = 355, 800, 1.3
    o.append(T(rx0, 778, "One rod, not to scale", "h2"))
    o.append(f'<path d="M{rx0},{ry0 - 10} L{rx0},{ry0} L{rx0 + (D["leg_len"] - D["foot"]) * rs:.1f},{ry0}" class="rodln"/>')
    xd = rx0 + D["leg_h"] / math.cos(math.atan(D["leg_slope"])) * rs
    o.append(f'<path d="M{xd:.1f},{ry0 - 9} L{xd:.1f},{ry0 + 9}" class="hair"/>')
    for (xa, xb) in ((rx0 - 2, rx0 + 10 * rs), (xd - 5 * rs, xd + 5 * rs)):
        o.append(rect(xa, ry0 - 4.5, xb, ry0 + 4.5, "ivory"))
    o.append(rect(rx0 + (D["leg_len"] - D["foot"] - D["boot"]) * rs, ry0 - 4.5, rx0 + (D["leg_len"] - D["foot"]) * rs, ry0 + 4.5, "ivory"))
    o.append(T(rx0, 818, f"cut {D['leg_len']:.0f} · 6 mm foot · deck mark {D['deck_mark']:.1f} from the bend", "fn"))
    o.append(T(rx0, 832, f"live rod: sleeves at foot and deck, boot at the tip, {D['leg_top'] - D['leg_top_live']:.1f} shorter", "fn"))

    o.append(T(700, 658, "Order of work", "h2"))
    steps = ["1. Coaster: four rod holes, two wire holes, the notch at the back, the button's Ø3.6 in the rim at the front. Roof: three",
             "    Ø1.8 holes in the dome. Shutter: cut 35, saw the window, plus a 3 mm ring from the same tube. Charger: jumper cut.",
             "2. From 1 mm rod: two bars, two spokes, the arm; a 3 mm ring of the 5 mm tube. Make the wheel on the spine as a jig: hub",
             "    ring, spokes on its flanks, rim ring on their ends. Solder the arm to the spine 6.5 above where the gearbox face sits.",
             "3. Bend the motor's tabs, solder its wires, set it on its bed, shaft on the axis. Slide the spine over the D shaft with a",
             "    drop of gel glue; sight it true as the motor turns slowly. Glue the magnet under the arm and the reed behind the motor.",
             "4. Rods: sleeve the live one; thread each through the coaster hole, bend the foot under, glue. Slide the deck down to 168,",
             "    nudge the rods vertical and glue it; slide the wheel down onto the deck, glue its rim over the hole; trim the live rod.",
             "5. Shutter: solder the bars to the spine's flanks 0.5 mm inside the drum's bottom edge, window to the front at the index,",
             "    then the bar ends to the wall from below. Lantern: post into the nipple, filament on the post, nut, then the cap down",
             "    over the three rods' tips, soldered flush outside, the live rod booted beneath; the ball; two wires to the back rods.",
             "6. Boards, diode, divider, the button inside the rim, the washers in the hollow, both ports in the notch. The tray behind",
             "    the motor on a dot of glue, leads down the left hole; the cell in. Flash through the notch; then the meter checks."]
    for i, st in enumerate(steps):
        o.append(T(700, 675 + i * 13.5, st, "fn"))
    o.append(T(20, 848, f"Rev {REV}, {STATUS}. The deck assumes the 1-1/2 in check ring, the roof the 1-1/2 in vase cap, and the coaster's top 1.3 mm from its listed weight. Measure the real parts and rerun the script before cutting.", "sub"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Desk lighthouse templates at actual size">{SHEET_CSS}{"".join(o)}</svg>'


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
<p>A lighthouse for the desk drawn in wire, {D['height']:.0f} mm tall, on a cell, and nothing else. Four {a("1.5 mm brass rods", "rod15")} rise from the same {a("brass coaster", "coaster")} the satellite stands on, Ø{D['cage_d0']:.0f} at their feet and Ø{D['cage_d1']:.0f} where they pass the gallery, then straight up as the lantern's bars to the roof, which three of them carry. Up the middle a {a("4 mm brass tube", "brass_tube")}, the spine, turns slowly from a {a("gearmotor", "motor")} standing at the foot. The lantern is open: a brass gallery (a lamp-maker's {a("check ring", "checkring")}) below, a brass roof (a {a("vase cap", "vasecap")}) above with a {a("brass ball", "ball")} for the ventilator, and air between. In it a warm-white {a("LED filament", "filament")} stands still on the axis, and a brass shutter cut from a {a("5/8 in tube", "tube58")} turns round it on the spine: one revolution in {E['period']:.1f} s, a {E['pass_s']:.1f} s sweep of light across the room, then brass. A {a("reed switch", "reed")} and a {a("magnet", "magnet")} on a thin brass arm at the foot tell the firmware where the window is, so when you turn rotation off it parks facing you, and when the lamp goes off it closes.</p>
<p>At the foot the motor stands on the axis, the family's {a("Nitecore 16340 cell", "cell")} stands in the owned black {a("holder", "holder")} behind it, and the reed stands between them, all in the open. The {a("charger board", "charger")}, the owned {a("ESP32-C3 SuperMini", "controller")} and the owned {a("MX1508 driver", "hbridge")} lie in the coaster's hollow, the charger's USB-C and the controller's side by side in a notch at the back: plug a cable in there to charge, or to flash. The one button hides inside the rim at the front; press the coaster. About {E['h_beacon']:.0f} hours of beacon on a charge, {E['h_charge']:.1f} to fill. The lamp's current goes up one rod and comes down another. No screen, no glass, no house, no paint.</p>
<p>The reference is Huy Vector's <a href="{L['reference']}" target="_blank" rel="noopener">Lighthouse Desk Lamp</a>: a parts list (brass sheet and tube, copper wire, a 3 V 30 rpm gear motor, a 39 mm Edison filament, a glass fuse, a Type-C charging module, a battery, a bamboo coaster) and no more. Ours keeps the idea, a small brass lighthouse on a coaster with a motor, a filament and a cell, and is its own build otherwise.</p>
<p><strong>This page is step 1 of the house rule: the final build first. Rev C was approved by the builder on {APPROVED} as drawn; that evening the builder rejected the acrylic glass, the brass sheet and any plastic house, and this is Rev D, {STATUS}: the same lighthouse with an open lantern, no house, and its three small brass pieces made from rod and tube.</strong> One form sheet, one wiring sheet with the power chain first, one sheet of templates, every part and every pin. Brass at the builder's word for this build. The science and engineering behind it (a fixed lamp and a turning window, a filament behind a resistor and why the rail is 5 V, a gearmotor at a third of its voltage, the budget from the cell, why the rods lean, a magnet and a reed) is step 2, <a href="{PHYSICS_PAGE}" target="_blank" rel="noopener">Desk Lighthouse Physics</a>. The Amazon parts are ordered; nothing is cut or soldered.</p>
"""


def decisions_html():
    o = ["<h2>The decisions</h2>"]
    for head, text in DECISIONS:
        o.append(f"<h3>{esc(head)}</h3><p>{md_inline(text)}</p>")
    return "".join(o)


def dims_rows():
    return [("height", "overall height, desk to the top of the ball"), ("disc_d", "brass coaster, diameter"), ("disc_t", "brass coaster, height"),
            ("plate_t", "coaster's top plate, thickness (from its weight; measure)"), ("hollow_h", "coaster's hollow, depth (measure)"),
            ("notch_w", "notch in the rim at the back, width (both USB-C ports)"), ("notch_h", "notch, height from the bottom edge"),
            ("hole_d", "the two wire holes in the top, between the motor and the tray"), ("hole_x", "wire holes, either side of the axis"), ("hole_y", "wire holes, behind the axis"),
            ("btn_hole", "the button's hole in the rim at the front"), ("btn_z", "button hole, up from the bottom edge"),
            ("cage_d0", "cage at the feet, across"), ("cage_d1", "cage at the gallery, across"), ("leg_r0", "rod holes in the coaster, from the axis"), ("ast_r", "rods at the deck and above, from the axis"),
            ("leg_h", "coaster top to the deck's underside"), ("leg_deg", "rods' lean below the deck, degrees"), ("leg_len", "each rod, cut length"), ("deck_mark", "deck mark from the foot's bend"),
            ("leg_top", "three rods' tips above the deck: flush with the dome's outside"), ("leg_top_live", "the live rod's tip above the deck, under the dome"),
            ("hole_leg", "rod holes, three (coaster, deck and roof)"), ("hole_live", "the live rod's holes, sleeved (coaster and deck)"), ("foot", "each rod's foot under the coaster's top"),
            ("mot_z0", "motor's bed, height"), ("z_collar", "the magnet arm above the coaster"), ("arm_len", "magnet arm, from the spine's side"), ("mag_r", "magnet from the axis"), ("reed_y", "reed behind the axis"), ("reed_top", "reed's top above the coaster"),
            ("hold_y0", "cell tray's front face behind the axis"), ("hold_w", "cell tray, across"), ("hold_d", "cell tray with the cell's bulge, front to back"), ("hold_h", "cell tray, tall"), ("cell_d", "cell, diameter"), ("cell_l", "cell, length"),
            ("chg_l", "charger board, length (port at one end)"), ("chg_w", "charger board, width"), ("chg_t", "charger board, thick, stripped"),
            ("tube_len", "spine, cut length"), ("tube_od", "spine, outside"), ("tube_top", "spine's top above the deck"),
            ("deck_d", "gallery deck, diameter"), ("deck_t", "gallery deck, thickness (measure)"), ("deck_hole", "deck's centre hole (as bought)"),
            ("bush_d", "bearing wheel's rim (a ring of the 5/8 in tube), outside"), ("bush_hole", "bearing hub's bore (a ring of the 5 mm tube), with play"), ("bush_t", "bearing wheel, tall"), ("spoke_len", "each spoke, 1 mm rod"),
            ("cap_rim", "the roof's rim above the deck: the open lantern"), ("cap_d", "roof (vase cap), diameter"), ("cap_h", "roof, height (measure)"),
            ("drum_od", "shutter drum, outside"), ("drum_wall", "shutter drum wall"), ("drum_h", "shutter drum, height"), ("drum_z0", "drum's bottom edge above the deck"), ("floor_z", "the drum's two bars above its bottom edge"), ("bar_len", "each bar, 1 mm rod"),
            ("win_deg", "shutter window, degrees"), ("win_arc", "shutter window, width on the tube"), ("dwin_h", "shutter window, height"),
            ("fil_l", "filament, length"), ("fil_top", "filament top above the deck"), ("fil_bot", "filament bottom above the deck"), ("post_r", "lamp post behind the axis"), ("post_len", "lamp post, cut length"),
            ("nut_bot", "nut's underside above the deck"), ("ball_d", "ventilator ball"), ("nip_l", "nipple, length")]


def dims_html():
    o = ['<h2>Dimensions</h2><div class="tw"><table><tr><th>What</th><th>mm</th></tr>']
    o += [f'<tr><td>{esc(lab)}</td><td class="m">{D[k]:.1f}</td></tr>' for k, lab in dims_rows()]
    o.append("</table></div>")
    o.append("<h3>Mass</h3>")
    o.append('<div class="tw"><table><tr><th>Part</th><th>g</th></tr>' + "".join(f'<tr><td>{esc(n)}</td><td class="m">{m:.1f}</td></tr>' for n, m, _ in MASS) + f'<tr><td><strong>Total, before the ballast</strong></td><td class="m"><strong>{D["mass"]:.0f}</strong></td></tr></table></div>')
    o.append(f"<p>Centre of mass {D['cg']:.0f} mm up: it tips at {D['tip_deg']:.0f}°, a {D['push_n']:.1f} N push at the ball. With about {D['ballast_g']:.0f} g of steel washers hot-glued into the coaster's hollow beside the boards: {D['cg_b']:.0f} mm, {D['tip_deg_b']:.0f}°, {D['push_n_b']:.1f} N. The lantern's {D['lantern_g']:.0f} g ride on four 1.5 mm rods: {D['rod_load_n']:.2f} N each against an Euler load of {D['rod_euler_n']:.0f} N for a rod fixed at both ends, and the cage sways about {1 / D['cage_k']:.2f} mm at the deck for every newton of push. The coaster's mass is the listing's; the rest is computed from the drawings or estimated; weigh them.</p>")
    return "".join(o)


def pins_html():
    o = ['<h2>Pin map, ESP32-C3 SuperMini</h2>',
         '<p>Nine pins of the sixteen. The button keeps the family\'s GPIO10; the cell is read on GPIO4; the boost is switched on GPIO7; no strapping pin is wired. The controller runs from the cell through the diode, as the satellite does.</p>',
         '<div class="tw"><table><tr><th>Pin</th><th>Job</th><th>Goes to</th></tr>']
    for p, job, to, net in PINS:
        o.append(f'<tr><td class="m">{esc(p)}</td><td>{esc(job)}</td><td>{esc(to)}</td></tr>')
    o.append("</table></div>")
    o.append('<h3>Charger board pads</h3><p>Used: the battery pads where the JST socket was (the tray\'s leads), <code>BAT</code> (to the diode and the divider), <code>5V</code> (the boost, to the driver), <code>EN</code> (from GPIO7), <code>G</code> (ground), the USB-C port (charging). Not used: <code>VIN</code>, <code>VU</code>, <code>D+</code>, <code>D−</code>, the terminal block (removed). The charge-rate jumper on the back is cut: 500 mA.</p>')
    o.append('<h3>Driver board pads</h3><p>Used: <code>VCC</code> (+) and <code>GND</code> (the boost\'s 5 V), <code>IN1</code> <code>IN2</code> (channel A, the shutter), <code>IN3</code> (channel B, the lamp), <code>IN4</code> (tied to GND), <code>OUT1</code> <code>OUT2</code> (the motor), <code>OUT3</code> (the lamp through its resistors and up the back-left rod). <code>OUT4</code> is unused: the lamp returns through the back-right rod to ground. The header and the two screw terminals come off; wires go on the pads.</p>')
    return "".join(o)


def nets_html():
    o = ['<h2>Every wire, and why</h2>', '<div class="tw"><table><tr><th>Net</th><th>From</th><th>To</th><th>Wire</th><th>Why</th></tr>']
    for net, fr, to, wire, why in NETS:
        o.append(f'<tr><td class="m">{esc(net)}</td><td>{esc(fr)}</td><td>{esc(to)}</td><td>{esc(wire)}</td><td>{md_inline(why)}</td></tr>')
    o.append("</table></div>")
    return "".join(o)


def budget_html():
    rows = [("beacon: shutter turning, lamp at the everyday level", E["cell_typ"], f"{E['rail_typ']:.0f} mA on the 5 V rail through the boost at {E['boost_eff'] * 100:.0f} %, plus the controller; about {E['h_beacon']:.0f} h on a charge"),
            ("lamp alone, shutter parked", E["cell_lamp"], f"about {E['h_lamp']:.0f} h"),
            ("asleep: boost off, controller waiting for the button", E["cell_idle"], f"about {E['h_idle'] / 24:.0f} days"),
            ("the worst moment", E["cell_peak"], f"{E['rail_peak']:.0f} mA on the rail with the motor and the lamp both full; the cell is good for 2 A"),
            ("charging", E["chg_ma"], f"into the cell, the jumper cut; about {E['h_charge']:.1f} h from empty; the chip's 6 h timer ends it")]
    o = ['<h2>The budget</h2>', '<div class="tw"><table><tr><th>Mode</th><th class="m">mA from the cell</th><th>Note</th></tr>']
    o += [f'<tr><td>{esc(n)}</td><td class="m">{v:.0f}</td><td>{esc(s_)}</td></tr>' for n, v, s_ in rows]
    o.append("</table></div>")
    o.append(f"<p>On the 5 V rail itself: the motor {E['mot_avg']:.0f} mA average ({E['mot_ma']:.0f} at {E['duty_mot'] * 100:.0f} % duty, about {E['mot_stall']:.0f} if the shutter jams), the lamp {E['i_lamp']:.0f} everyday and {E['i_lamp_max']:.0f} full ({E['lamp_w'] * 1000:.0f} mW in the lantern, {E['p_res_each'] * 1000:.0f} mW in each resistor), the driver {E['mx_q']:.0f}. The boost is rated 1 A and stalls only if more than 200 mA is switched onto it in one step, so the firmware ramps. The controller takes its {E['c3_avg']:.0f} mA from the cell through the diode, not from the rail, so the rail can sleep.</p>")
    o.append(f"<p>Speed: a 30 rpm (6 V) gearmotor runs about {E['rpm_5v']:.0f} rpm on 5 V; {E['duty_mot'] * 100:.0f} % duty gives {E['rpm_target']:.0f} rpm, {E['period']:.1f} s a revolution, a {E['pass_s']:.1f} s pass of the {D['win_deg']:.0f}° window. The reed's period closes the loop, so the number holds whatever the motor's batch or the cell's state.</p>")
    return "".join(o)


def parts_html():
    o = ['<h2>Parts</h2>', "<p>Rev C sent fourteen lines to buy in three orders. The eight Amazon lines went in on 2026-11-09 (five orders, $122.64 with tax and delivery; that morning a pin vise came off the cart because a cordless drill is owned, and the coaster because the one bought on 2026-11-06 now belongs to this build), and the five Grand Brass lamp parts by the builder's word (none of them is on Amazon; no confirmation mail had come by that evening). The charger is still to buy: that morning's DigiKey order holds the rover's six lines. That evening Rev D dropped two of the Amazon lines: the brass sheet, which the builder cancelled, and the acrylic tube, which had shipped before it was rejected and goes back. The cell, its tray, the diode, the resistors, the controller, the driver, the rods, the tubes and the wire are in a drawer and listed so they are not bought twice. Each part is named by what it is, with the link on the word to the exact product. Prices are what Amazon charged on 2026-11-09.</p>"]
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


RULES = [
    "Design first: sleek, few lines (four rods and a spine; no rings, no braces, no glass, no house); wires in the hollow, two of them the rods themselves; no closed surface at all.",
    "Colour: brass and warm white; black only in the pad under the coaster, the cell's wrap and its tray, in the open at the foot as the rule allows; the boards in the hollow; the filament's yellow phosphor hidden by the shutter when off; white heat-shrink where a sleeve shows.",
    f"No clear acrylic and no folded brass sheet, at the builder's word of {TODAY} evening: the lantern is open and the three small brass pieces are rod and tube.",
    "Power drawn on both sheets: the cell stands where the form sheet shows it, and the wiring sheet reads cell, charger, controller, driver, loads.",
    "Component names with the link on the word; no product codes in prose.",
    "Owned parts stay off the shopping list: the cell, the tray, the diode, the resistors, the controller and the driver are family stock, the rods and the tubes are shared stock.",
    "Every wire on the sheet is traceable pin to pin; the generator checks clearance and counts crossings (zero).",
    f"Brass at the builder's word for this build ({REV_A}); the family's rule since the drone is stainless.",
    "Meter only what matters: three checks before power, one of them the live rod against every other piece of brass, one the tray's polarity before the cell meets anything.",
]

def rules_html():
    return "<h2>Rules this build follows</h2><ul>" + "".join(f"<li>{esc(r)}</li>" for r in RULES) + "</ul>"


APPROVAL = (f"Rev C was approved by the builder on {APPROVED} as drawn. That evening the builder cancelled the brass sheet (\"very hard to wrap round electric components\"), rejected the acrylic tube (\"so ugly, never\") and any plastic house (\"just use the wire frame as a lighthouse, nothing else\"), so Rev D, drawn the same evening, removes the glass and the house and makes the three small brass pieces from rod and tube; everything else stands. **Rev D awaits the builder's approval.** "
            f"The same three sizes are assumed and must be measured when the parts come: the check ring's thickness (3 mm), the vase cap's height (12.5 mm) and the coaster's hollow (about 6.7 deep under a 1.3 mm top, from its 80 g; the coaster arrived 11-09); the rods' tips and whether the boards fit the hollow follow from them, and the script recomputes them. "
            f"Step 2, the science and engineering behind the sheet, is published as [Desk Lighthouse Physics]({PHYSICS_PAGE}) and written to `docs/PHYSICS.md`, revised for the open lantern. Orders: the eight Amazon lines of 2026-11-09 less the sheet (cancelled) and the acrylic tube (to return) are this build's; the five Grand Brass lamp parts by the builder's word; the charger still to buy. Next: the yes or the changes, the charger, the three measurements, then the firmware.")

def page_html(form_svg, wiring_svg, tmpl_svg):
    return "\n".join([
        '<title>Desk Lighthouse Build</title>',
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        f"<style>{STYLE}</style>",
        f"<style>{PAGE_TONES}</style>",
        '<style>.wrap{max-width:1100px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} '
        'td,th{min-width:0} .tw table{min-width:720px}</style>',
        '<div class="wrap">',
        f'<div class="masthead"><div class="eyebrow">Desk lighthouse &middot; step 1: the final build &middot; Rev {REV}, the open wire frame on a cell, {STATUS}</div>',
        '<h1>A lighthouse drawn in four brass rods, with a lamp that stands still while the brass turns, on a cell, and nothing else</h1>',
        f'<div class="sub">How it looks, how it is wired and powered, every part and every pin. {D["height"]:.0f} mm tall on a Ø{D["disc_d"]:.0f} brass coaster, about {D["mass"]:.0f} g before the ballast, about {E["h_beacon"]:.0f} hours of beacon on a charge. Paper design of {TODAY}, after Rev A of {REV_A}, Rev B of {REV_B} and Rev C of {REV_C} (approved as drawn, then its glass and house rejected the same evening). The science and engineering behind it is <a href="{PHYSICS_PAGE}" target="_blank" rel="noopener">Desk Lighthouse Physics</a>. The Amazon parts are ordered; nothing built.</div></div>',
        intro_html(),
        f'<figure class="sheet">{form_svg}<figcaption><strong>Form sheet. Print landscape on Letter at Actual size; it is page 1 of the PDF.</strong> The front view; a section through the open lantern showing the fixed lamp on its post, the turning shutter on its two bars, the wheel bearing and the back rods; the foot from above; the plan with the roof off; a section through the foot and the coaster with the cell standing behind the motor, the button in the rim and the charger in the hollow; how it behaves; the key numbers.</figcaption></figure>',
        decisions_html(),
        f'<figure class="sheet">{wiring_svg}<figcaption><strong>Wiring sheet, page 2 of the PDF.</strong> The power chain reads left to right: the cell and the charger, the diode and the divider, the controller, the driver on the boost\'s 5 V, then the motor and the lamp on the right with the reed, the button and the cables below and the budget along the bottom. Thick lines are wires you solder, thin ones leads and cables, brass-filled ones the frame\'s rods carrying the lamp\'s current; dots are joints; zero crossings.</figcaption></figure>',
        f'<figure class="sheet">{tmpl_svg}<figcaption><strong>Templates, page 3 of the PDF.</strong> Printed at Actual size, the 50 mm bar measures 50 mm: the coaster\'s holes and notch, the gallery deck\'s holes, the roof\'s three rod holes, the shutter unrolled with its window, the spine\'s hardware and one rod\'s marks; then the order of work.</figcaption></figure>',
        dims_html(),
        pins_html(),
        nets_html(),
        budget_html(),
        parts_html(),
        firmware_html(),
        checks_html(),
        rules_html(),
        f'<h2>Status</h2><p>{md_inline(APPROVAL)}</p>',
        f'<hr><p class="sub">Built by <code>docs/pages/gen/build_page.py</code>, which also writes <code>docs/FINAL_BUILD.md</code> and the PDFs; the dimensions, pins, nets, budget and parts live in that script. The wiring sheet\'s clearance check passes, and the clearances the drawing relies on (shutter inside the rods, post in the shutter, three rods through the roof and the live one under it, the magnet arm clear of the tray, the wheel over the deck\'s hole, the boards in the hollow and their ports in the notch, the button inside the rim, the boost under its switch-on limit) are asserted. Sources read {REV_A} to {TODAY}: the reference page, the Amazon, Grand Brass and Adafruit listings, the charger\'s pinouts page, the filament page, the SuperMini notes, the MX1508 and SSD1306 datasheets, the family\'s inventories and the satellite\'s record. Nothing measured.</p>',
        '</div>'])


def final_build_md():
    o = [f"# Desk lighthouse: the final build (step 1, Rev {REV}, the open wire frame on a cell, {STATUS})", "",
         f"Paper design of {TODAY}, after Rev A of {REV_A} (an ivory 25 mm tube on a 38 mm brass cube with a text screen), Rev B of {REV_B} (the wire frame, the screen in a small door) and Rev C of {REV_C} (no screen, a cell and a charger, a glass lantern and a brass-sheet house; approved as drawn that morning). That evening the builder rejected the glass, the sheet and any plastic house (\"just use the wire frame as a lighthouse, nothing else\"), and Rev D is that: four 1.5 mm brass rods rise from the satellite's 75 × 8 mm brass coaster, Ø{D['cage_d0']:.0f} at the feet and Ø{D['cage_d1']:.0f} at the gallery, and run on up to the roof, which three of them carry; a 4 mm brass spine turns up the middle from an N20 gearmotor standing in the open at the foot, with the family's Nitecore 16340 standing in the owned black tray behind it and the button inside the coaster's rim at the front. The family's bq25185 charger board, the owned ESP32-C3 SuperMini and MX1508 driver lie in the coaster's hollow, both USB-C ports in a notch at the back; the controller runs from the cell through an SS14, the motor and the lamp from the board's 5 V boost. On top an open lantern between a 1-1/2 in turned brass check ring (the gallery) and a 1-1/2 in spun brass vase cap (the roof), with a 5/8 in brass ball. In it a 26 mm warm-white LED filament stands still on the axis on a 1 mm brass lamp post and a brass shutter cut from a 5/8 in tube turns round it on the spine, one revolution in {E['period']:.1f} s; the shutter's floor, the magnet's arm and the deck's bearing are 1 mm rod and tube rings, not sheet. The lamp's current goes up one rod and comes down another. {D['height']:.0f} mm tall, about {D['mass']:.0f} g before {D['ballast_g']:.0f} g of steel goes into the coaster; about {E['h_beacon']:.0f} hours of beacon on a charge. **Rev D awaits the builder's approval; step 2 is `PHYSICS.md`. The Amazon parts are ordered; nothing built.**",
         "", "Generated by `pages/gen/build_page.py`, which also writes the page `pages/desk-lighthouse-build.html` and the PDFs in `pages/print/`; edit the script, not this file. The sheets are the authority for the drawing; this file carries the same decisions, dimensions, pin map, nets, budget and parts as text.", "",
         "## The reference", "",
         f"Huy Vector, [Lighthouse Desk Lamp]({L['reference']}), read {REV_A}. The page is a parts list and nothing else: 0.2 × 100 × 100 mm brass sheet, 4 mm brass tube, 1 mm copper wire, a 3 V 30 rpm DC gear motor, a 39 mm LED Edison filament, a 6 × 30 mm glass fuse, a Type-C 4.2 V charging module, a battery, an 8 cm bamboo coaster; no dimensions, no prose, no video. Ours keeps the idea (a small brass lighthouse on a coaster, a gear motor turning something in the lantern, an LED filament as the lamp, a cell and a charging port) and is its own build otherwise: a wire tower, a fixed lamp and a turning brass shutter, a reed index so it parks, the family's cell and charger, lamp parts for the lantern.",
         "", "## The decisions", ""]
    for head, text in DECISIONS:
        o += [f"### {head}", "", text, ""]
    o += ["## Dimensions", "", "| What | mm |", "| --- | ---: |"]
    o += [f"| {lab} | {D[k]:.1f} |" for k, lab in dims_rows()]
    o += ["", "| Part | g |", "| --- | ---: |"] + [f"| {n} | {m:.1f} |" for n, m, _ in MASS] + [f"| **Total, before the ballast** | **{D['mass']:.0f}** |", "",
          f"Centre of mass {D['cg']:.0f} mm up; tips at {D['tip_deg']:.0f}°, a {D['push_n']:.1f} N push at the ball. With about {D['ballast_g']:.0f} g of steel in the coaster's hollow: {D['cg_b']:.0f} mm, {D['tip_deg_b']:.0f}°, {D['push_n_b']:.1f} N. The lantern's {D['lantern_g']:.0f} g ride on four 1.5 mm rods: {D['rod_load_n']:.2f} N each against an Euler load of {D['rod_euler_n']:.0f} N for a rod fixed at both ends; the cage sways about {1 / D['cage_k']:.2f} mm at the deck for every newton of push.", "",
          "## Pin map, ESP32-C3 SuperMini", "", "| Pin | Job | Goes to |", "| --- | --- | --- |"]
    o += [f"| {p} | {job} | {to} |" for p, job, to, net in PINS]
    o += ["", "Charger board pads used: the battery pads where the JST socket was (the tray's leads), `BAT` (to the diode and the divider), `5V` (the boost, to the driver), `EN` (from GPIO7), `G` (ground), the USB-C port (charging); not used: `VIN`, `VU`, `D+`, `D−`, the terminal block (removed); the charge-rate jumper on the back cut for 500 mA. Driver board pads used: `VCC` (+) and `GND` (the boost's 5 V), `IN1` `IN2` (channel A, the shutter), `IN3` (channel B, the lamp), `IN4` (tied to GND), `OUT1` `OUT2` (the motor), `OUT3` (the lamp through its resistors and up the back-left rod); `OUT4` unused, the lamp returning through the back-right rod to ground. The header and the screw terminals come off; wires go on the pads.", ""]
    o += ["## Every wire, and why", "", "| Net | From | To | Wire | Why |", "| --- | --- | --- | --- | --- |"]
    o += [f"| {n} | {fr} | {to} | {wire} | {why} |" for n, fr, to, wire, why in NETS]
    o += ["", "## The budget", "",
          f"From the cell: {E['cell_typ']:.0f} mA with the beacon turning and the lamp at {E['lamp_duty'] * 100:.0f} % (about {E['h_beacon']:.0f} h on a charge), {E['cell_lamp']:.0f} mA with the lamp alone ({E['h_lamp']:.0f} h), {E['cell_idle']:.0f} mA asleep with the boost off ({E['h_idle'] / 24:.0f} days), {E['cell_peak']:.0f} mA at the worst moment against the cell's 2 A. On the boost's 5 V rail: the motor {E['mot_avg']:.0f} mA average ({E['mot_ma']:.0f} at {E['duty_mot'] * 100:.0f} % duty, about {E['mot_stall']:.0f} if the shutter jams), the lamp {E['i_lamp']:.0f} everyday and {E['i_lamp_max']:.0f} full ({E['lamp_w'] * 1000:.0f} mW in the lantern, {E['p_res_each'] * 1000:.0f} mW in each resistor), the driver {E['mx_q']:.0f}: {E['rail_typ']:.0f} mA typical, {E['rail_peak']:.0f} at most in normal running, under the boost's 200 mA switch-on limit because the motor ramps. Charging: {E['chg_ma']:.0f} mA with the jumper cut, about {E['h_charge']:.1f} h from empty; plugged in, the power path runs the lighthouse from the cable. Speed: {E['rpm_5v']:.0f} rpm free on 5 V, {E['rpm_target']:.0f} rpm at {E['duty_mot'] * 100:.0f} % duty, {E['period']:.1f} s a revolution, a {E['pass_s']:.1f} s pass of the {D['win_deg']:.0f}° window; the reed's period closes the loop.", ""]
    o += ["## Parts", "", "Rev C sent fourteen lines to buy in three orders. The eight Amazon lines went in on 2026-11-09 (five orders, $122.64 with tax and delivery; that morning a pin vise came off the cart because a cordless drill is owned, and the coaster because the one bought on 2026-11-06 now belongs to this build), and the five Grand Brass lamp parts by the builder's word (none of them is on Amazon; no confirmation mail had come by that evening). The charger is still to buy: that morning's DigiKey order holds the rover's six lines. That evening Rev D dropped two of the Amazon lines: the brass sheet, which the builder cancelled, and the acrylic tube, which had shipped before it was rejected and goes back. The cell, its tray, the diode, the resistors, the controller, the driver, the rods, the tubes and the wire are owned and listed so they are not bought twice. Prices are what Amazon charged on 2026-11-09.", ""]
    for head, rows in PARTS:
        o += [f"### {head}", "", "| Qty | Part | Where | Price | Why, and what to check |", "| ---: | --- | --- | --- | --- |"]
        for qty, part, url, code, where, why in rows:
            name = f"[{part}]({url})" if url else part
            o.append(f"| {qty} | {name} | {code} | {where} | {why} |")
        o.append("")
    o += ["## What the firmware needs", ""] + [f"- {x}" for x in FIRMWARE] + ["", "## Before power, with the meter", ""] + [f"- {x}" for x in CHECKS]
    o += ["", "## Rules this build follows", ""] + [f"- {r}" for r in RULES] + ["", "## Status", "", APPROVAL, ""]
    return "\n".join(o)


def print_pdf(html, form_svg, wiring_svg, tmpl_svg):
    PRINT.mkdir(exist_ok=True)
    sheet_css = ("<style>@page{size:letter landscape;margin:7mm} html,body{background:#fff;margin:0}"
                 ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#ccc;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#f1f1f1;--warn:#000;--warn-soft:#eee}"
                 + LH_PRINT + "svg{width:262mm;height:auto;display:block;margin:0 auto}</style>")
    page_css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:10pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
                "figure.sheet{display:none} h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} h3{font-size:9pt;margin-top:10pt} p,ul,ol{max-width:none} table{font-size:9pt} th,td{padding:4pt 6pt}"
                ".tw table{min-width:0} td.m,th.m{white-space:normal} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid} ul.check{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        jobs = []
        for name, svg in (("form", form_svg), ("wiring", wiring_svg), ("templates", tmpl_svg)):
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
        out = PRINT / "desk-lighthouse-build.pdf"
        subprocess.run(["pdfunite", str(d / "form.pdf"), str(d / "wiring.pdf"), str(d / "templates.pdf"), str(p_pdf), str(out)], check=True)
        shutil.copyfile(d / "form.pdf", PRINT / "desk-lighthouse-form-sheet.pdf")
        shutil.copyfile(d / "wiring.pdf", PRINT / "desk-lighthouse-wiring-sheet.pdf")
        shutil.copyfile(d / "templates.pdf", PRINT / "desk-lighthouse-templates.pdf")
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


PNG_CSS = ("<style>html,body{margin:0;background:#fff}:root{--bg:#EDEBE7;--paper:#FFFFFF;--ink:#16181C;--ink-2:#5A6068;--line:#CFCBC4;"
           "--brass:#8F6114;--brass-soft:#F2E6D2;--signal:#5A6068;--signal-soft:#ECEAE6;--warn:#8F6114;--warn-soft:#F2E6D2}")


def png(svg, name, outdir, size=(1360, 860)):
    """Render one sheet to a PNG for checking by eye (not part of the outputs)."""
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    src = outdir / f"{name}.html"
    src.write_text('<!doctype html><html data-theme="light"><meta charset=utf-8>' + PNG_CSS + f"svg{{width:{size[0]}px;height:{size[1]}px}}</style>" + svg + "</html>")
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--window-size={size[0]},{size[1]}",
                    f"--screenshot={outdir / (name + '.png')}", f"file://{src}"], check=True, capture_output=True, timeout=120)


def main():
    # the clearances the drawing relies on
    assert D["post_r"] + D["post_d"] / 2 + 1.5 < D["drum_od"] / 2 - D["drum_wall"], "the lamp post must stand inside the shutter with 1.5 mm to spare"
    assert D["post_r"] - D["post_d"] / 2 > D["fil_w"] / 2 + 1.0, "the lamp post stands clear behind the filament"
    assert D["post_r"] + D["post_d"] / 2 <= D["nip_id"] / 2 + 0.05, "the lamp post fits up inside the nipple's bore against its wall"
    assert D["tube_top"] + 3 < D["post_foot"], "the spine's top stays clear of the lamp post's foot"
    assert D["fil_bot"] > D["floor_top"] + 3, "the filament stands clear of the shutter's bars"
    assert D["fil_top"] + D["tab"] + 1.5 <= D["nut_bot"], "the filament's top tab stays clear of the nut"
    assert D["drum_top"] > D["fil_top"] + 0.4, "the shutter must cover the lamp"
    assert D["drum_top"] + 1 < cap_z_at_r(D["drum_od"] / 2), "the shutter must turn under the roof"
    assert D["nut_bot"] > D["drum_top"] + 2, "the nut sits above the shutter"
    assert D["ast_r"] - D["rod_d"] / 2 - D["drum_od"] / 2 >= 3.0, "the shutter turns inside the rods with 3 mm to spare"
    assert D["ast_r"] + D["hole_live"] / 2 < D["deck_d"] / 2 - 2, "the rod holes leave 2 mm of deck outside them"
    assert D["leg_top_live"] > D["cap_rim"] + 3, "the live rod's tip hides inside the roof"
    assert D["leg_top_live"] < cap_z_at_r(D["ast_r"] + D["rod_d"] / 2), "the live rod ends short of the dome"
    assert D["leg_top"] > D["leg_top_live"], "the three grounded rods reach through the dome"
    assert D["bush_d"] > D["deck_hole"] + 3 and D["bush_hole"] >= D["tube_od"] + 0.1, "the wheel's rim bridges the deck's hole and its hub clears the spine"
    assert D["tube_od"] + 2 < D["deck_hole"], "the spine passes the deck's own hole with room"
    assert D["bar_len"] < D["drum_od"] - 2 * D["drum_wall"] and D["spoke_len"] < D["bush_d"] - 2 * D["drum_wall"], "the bars fit inside the drum and the spokes inside the rim"
    # the foot, in the open
    assert D["hold_y0"] >= D["tube_od"] / 2 + D["arm_len"] + 1.0, "the magnet arm turns clear of the cell's tray"
    assert D["mot_z0"] + D["mot_l"] + 1 < D["z_collar"] and D["z_collar"] + D["arm_d"] < D["mot_z0"] + D["mot_l"] + D["shaft_l"], "the arm sits on the spine over the D shaft"
    assert D["reed_y"] - D["reed_d"] / 2 >= D["mot_t"] / 2 + 0.3 and D["reed_y"] + D["reed_d"] / 2 + 0.5 <= D["hold_y0"], "the reed stands between the motor and the tray"
    assert D["reed_bot"] > D["mot_z0"] and abs(D["mag_r"] - D["reed_y"]) <= D["mag_d"] / 2 + 0.5, "the magnet passes over the reed's end"
    assert D["mag_r"] + D["mag_d"] / 2 <= D["tube_od"] / 2 + D["arm_len"] + 0.1, "the magnet sits under the arm"
    assert D["hole_y"] - D["hole_d"] / 2 >= D["mot_t"] / 2 + 0.5 and D["hole_y"] + D["hole_d"] / 2 <= D["hold_y0"], "the wire holes sit between the motor and the tray"
    assert D["hole_x"] - D["hole_d"] / 2 >= 1.0 + D["reed_d"] / 2, "the wire holes clear the reed"
    for z in (0.0, D["hold_h"]):
        r = (D["leg_r0"] - z * D["leg_slope"]) * math.cos(math.radians(45))
        assert r > D["hold_w"] / 2 + 2.0, "the rods pass clear of the tray"
    assert D["leg_r0"] + 2 < D["disc_d"] / 2 - 2, "the feet sit well inside the coaster's edge"
    assert max(D["c3_t"], D["chg_t"]) + 0.5 <= D["hollow_h"] and D["c3_w"] + D["chg_w"] + 2 <= D["notch_w"] and D["notch_h"] <= D["disc_t"] - D["plate_t"] + 0.1, "the boards fit the hollow and both ports the notch"
    assert D["btn_z"] - 3.0 >= 0.3 and D["btn_z"] + 3.0 <= D["disc_t"] - D["plate_t"] - 0.3, "the button's body fits inside the rim between the pad and the ceiling"
    assert D["tube_len"] + D["bush_t"] <= 200 and D["leg_len"] <= 300 and D["post_len"] + D["hw_rod"] <= 300, "the spine, the rods and the 1 mm rod come out of owned stock"
    assert E["i_lamp_max"] < E["fil_rated"], "the lamp's full current stays under its rating"
    assert E["p_res_each"] < 0.25 * 0.5, "each resistor under half its rating"
    assert E["rail_peak"] < 200, "the boost never sees more than its 200 mA switch-on limit in normal running"
    assert E["cell_peak"] < 2000, "the worst moment stays inside the cell's 2 A"
    form_svg, wiring_svg, tmpl_svg = form_sheet(), wiring_sheet(), templates_sheet()
    html = page_html(form_svg, wiring_svg, tmpl_svg)
    OUT.write_text(html)
    (DOCS / "FINAL_BUILD.md").write_text(final_build_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "FINAL_BUILD.md")
    print(f"numbers: height {D['height']:.1f}, mass {D['mass']:.1f} g, cg {D['cg']:.1f}, tip {D['tip_deg']:.1f} ({D['push_n']:.2f} N); with ballast cg {D['cg_b']:.1f}, tip {D['tip_deg_b']:.1f} ({D['push_n_b']:.2f} N); "
          f"rods {D['leg_len']} ({D['leg_deg']} deg, tips {D['leg_top']} / live {D['leg_top_live']}), spine {D['tube_len']}, post {D['post_len']}, bars {D['bar_len']}, spokes {D['spoke_len']}, arm {D['arm_len']}; "
          f"cell {E['cell_typ']:.0f}/{E['cell_lamp']:.0f}/{E['cell_idle']:.0f} mA -> {E['h_beacon']:.1f}/{E['h_lamp']:.1f} h, {E['h_idle']/24:.0f} d; rail {E['rail_typ']:.0f} typ {E['rail_peak']:.0f} peak; charge {E['h_charge']:.1f} h")
    if "--png" in sys.argv:
        outdir = sys.argv[sys.argv.index("--png") + 1]
        png(form_svg, "form", outdir)
        png(wiring_svg, "wiring", outdir)
        png(tmpl_svg, "templates", outdir)
        print("png in", outdir)
    if "--pdf" in sys.argv:
        print_pdf(html, form_svg, wiring_svg, tmpl_svg)


if __name__ == "__main__":
    main()
