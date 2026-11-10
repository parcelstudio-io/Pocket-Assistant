"""Desk satellite, step 1 of the builder's rule: the final build first, the science after.

Writes, from the data at the top of this file (edit the script, not the outputs):
  docs/pages/desk-satellite-build.html             the page: form sheet, wiring sheet, decisions, pin map, nets, budget, parts
  docs/pages/print/desk-satellite-build.pdf         Letter, black only: form sheet (landscape), wiring sheet (landscape), then the notes (portrait)
  docs/pages/print/desk-satellite-form-sheet.pdf    the form sheet alone
  docs/pages/print/desk-satellite-wiring-sheet.pdf  the wiring sheet alone
  docs/FINAL_BUILD.md                               the same decisions, pin map, nets, budget and parts as Markdown

Reference: Huy Vector, "Desk Satellite", huyvector.org/clocks/desk-satellite (read 2026-11-02): a copper-wire cube body with an
ESP32-C3 and a 0.96" TFT clock inside, two solar wings, a Type-C charging module plus a separate solar charge controller
and a LiPo, an SHT31 sensor, a touch switch, on a 3 mm brass tube over a 6 cm bamboo coaster. Ours keeps the form (a body on
one post over a round base, two solar wings) and the builder's brief of 2026-11-02 (mini solar panels, a cell they top up,
USB as the fallback, a small 3000 K LED at the tip that is on or blinks); the clock, display and sensor are dropped.
Revised the same morning at the builder's word ("a small light stuck on the corner, not a tall pin; no legs at all"): the beacon moved
from a 52 mm two-rod mast to a pre-wired 0805 LED chip glued flat on the top front corner of the bus. Then, at the builder's word again
("a little different from the reference; a warm light below, the brass tone"): the hologram's spare 2200 K LED filament under the floor, glowing
down onto the disc, and a decision that lists where this build leaves the reference.

The hop-drawing Router is imported from pocket_ai_assistant/edu/pages/gen/wiring_sheet.py, as the desk hologram's generator
does; the subclass adds the pin registry and the clearance check. Nothing here has been built. Every electrical number is a
datasheet or product-page figure read 2026-11-02 (TI bq25185 datasheet SLUSF65B, the Adafruit product page, Learn guide,
schematic and fab print, the Amazon listings); the printed box is a paper envelope to be checked against the real boards
before it is printed."""
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
OUT = PAGES / "desk-satellite-build.html"
PRINT = PAGES / "print"
STYLE = (HERE / "page_style.css").read_text()

sys.path.insert(0, str(PROJECT.parent / "pocket_ai_assistant" / "edu" / "pages" / "gen"))
from wiring_sheet import Router as _Router  # noqa: E402

W, H = 1360, 860
TODAY = "2026-11-02"
APPROVED = "2026-11-03"

# ----------------------------------------------------------------------------- links (component names in prose, links on the word)
A = "https://www.adafruit.com/product/"
AMZ = "https://www.amazon.com/dp/"
L = {
    "charger": A + "6106",                 # Adafruit bq25185 USB / DC / Solar charger with 5 V boost (Cyber Dawn's spare)
    "charger_guide": "https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board",
    "bq_ds": "https://www.ti.com/lit/ds/symlink/bq25185.pdf",
    "cell": "https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery",   # Nitecore NL169 16340, 950 mAh, protected: 13 owned, two IMR Batteries orders of 2026-10-16 delivered 10-21
    "holder": AMZ + "B0CRGK889F",          # ACEIRMC 16340 holder with leads, 10 owned (Cyber Dawn's stock)
    "controller": AMZ + "B0F888JQ91",      # Meshnology ESP32-C3 SuperMini 10-pack (Pocket AI stock)
    "panel": AMZ + "B0FL26KWWT",           # MECCANIXITY 5 x 80 x 45 mm poly 5 V 0.45 W 90 mA with 150 mm leads: the rectangle chosen 2026-11-03 evening
    "gikfun": AMZ + "B0GWQJHSY9",          # Gikfun 10 x 56 x 56 mm mono 5 V: the squares the sheet was approved with; cancelled off the chip order 2026-11-03
    "led": AMZ + "B09QGJ9LY7",             # DiCUNO 20 x pre-wired 0805 warm white, 2.8-3.3 V, 16 cm enamelled leads
    "filament": AMZ + "B0FR35BGYL",        # QIROGKC 3 V LED filament, 38 mm, 2200 K, 10-pack: the hologram's, nine spare
    "disc": AMZ + "B0D9DMK3L7",            # heavy brass coaster, 75 x 8 mm, flat top: the base from 2026-11-06
    "steel_disc": AMZ + "B08JD6GY21",      # Harness Machine & Fab 3" x 1/8" 304 stainless disc: the first base, spare since 2026-11-06
    "rod15": AMZ + "B082ZNMD46",           # uxcell 304 stainless 1.5 mm x 150 mm, 10 (coupon stock)
    "schottky": AMZ + "B079KJ46ZS",        # Chanzon SS14, 100 (drone stock)
    "wire30": AMZ + "B073RDGTPB",          # CBAZY 30 AWG silicone
    "kapton": AMZ + "B072Z92QZ2",          # ELEGOO Kapton
    "reference": "https://www.huyvector.org/clocks/desk-satellite",
    "cyberdawn_solar": "../../cyber_clock_v2/docs/SOLAR_FEASIBILITY.md",
}

# ----------------------------------------------------------------------------- the numbers (mm unless said)
D = dict(
    disc_d=75.0, disc_t=8.0,                 # the brass coaster, 75 x 8 mm, flat top (listing; builder confirmed the flat top 2026-11-06)
    hub_d=12.0, hub_h=8.0, hub_hole=7.0,     # printed black hub glued to the coaster's flat top; the post's lower socket (the top is too thin to drill)
    coaster_g=80.0, ballast_g=150.0, base_z=3.5,  # coaster 2.82 oz per its listing (hollow under a thin top); steel epoxied into the hollow; their centre of mass, mm up
    post_free=110.0,                         # top of the base to the boss under the bus
    boss_d=6.0, boss_h=8.0,                  # printed boss under the bus: the post's upper socket (the "thruster")
    box_w=48.0, box_d=52.0, box_h=24.0,      # the bus: printed black box, x = width (wings), y = depth, z = height; sized round the cell holder
    wall=2.0, lid=1.5,                       # walls; the back is a press-fit lid
    yoke_l=6.0, yoke_d=6.0, gap=2.0,         # each wing's boom socket is a 6 mm boss on the side wall, then 2 mm of air
    panel=80.0, panel_d=45.0, panel_t=2.5, panel_g=16.0,   # the poly panel: 80 along the boom x 45 deep x about 2.5 mm, 16 g, 150 mm leads fitted
    led_l=2.0, led_w=1.25, led_h=1.1,        # the 0805 LED chip: long axis along the depth, 1.1 mm tall, glued on the top face
    led_off=5.0,                             # chip centre, in from the front face and from the right wall
    lamp_len=38.0, lamp_y=-10.0, lamp_hole=1.5,  # the LED filament under the floor: 38 mm across, 10 mm ahead of the post, its leads up a 1.5 mm hole
    cell_d=16.6, cell_l=34.1, cell_g=20.0,   # Nitecore 16340: 16.6 x 34.1 mm, 20 g, 950 mAh, protected, button top
    holder_l=43.0, holder_w=18.0, holder_h=14.0, holder_g=6.0,   # the owned 16340 tray with leads, along the front wall
    charger_l=29.2, charger_w=19.1, charger_g=4.0,   # fab print: 1.15 x 0.75 in; holes 0.95 x 0.55 in apart
    c3_l=22.5, c3_w=18.0, c3_g=3.0,
    usb_w=9.0, usb_h=3.4,                    # USB-C port opening in the lid
    btn=6.0,
)
D["post_cut"] = D["hub_hole"] + D["post_free"] + D["boss_h"]                      # 125 mm of one 150 mm coupon
D["boom_cut"] = D["wall"] + D["yoke_l"] + D["gap"] + D["panel"]                   # 66 mm each, both from one coupon
D["hole_x"] = D["led_off"] + D["led_w"] / 2 + 1.0                                   # the 1.2 mm pinhole for the leads, 6.6 mm in from the right wall
D["span"] = 2 * D["panel"] + 2 * (D["yoke_l"] + D["gap"]) + D["box_w"]            # 170 mm wing tip to wing tip
D["z_hub"] = D["disc_t"] + D["hub_h"]                                              # 11.2
D["z_box"] = D["z_hub"] + D["post_free"] + D["boss_h"]                             # 129.2: the bus floor
D["z_top"] = D["z_box"] + D["box_h"]                                               # 151.2
D["z_wing"] = D["z_box"] + D["box_h"] / 2                                          # 140.2: the boom axis
D["z_panel"] = D["z_wing"] + 0.75                                                  # the panel rests on the boom
D["height"] = D["z_top"] + D["led_h"]                                              # 152.3 to the top of the chip
D["disc_g"] = round(D["coaster_g"] + D["ballast_g"])                               # the weighted base: 80 g of brass + 150 g of steel
D["box_g"] = 25.0                                                                  # PETG shell + lid + bosses, estimate
rod15 = math.pi * 0.75 ** 2 * 7.9e-3                                               # g per mm of 1.5 mm rod
D["top_g"] = round(2 * D["panel_g"] + D["box_g"] + D["cell_g"] + D["holder_g"] + D["charger_g"] + D["c3_g"]
                   + rod15 * (D["post_cut"] + 2 * D["boom_cut"]) + 3)   # wires, LED, button, diode: 3 g
D["base_g"] = D["disc_g"] + 1                                                      # + the printed hub
D["com"] = (D["top_g"] * (D["z_box"] + D["box_h"] / 2) + D["base_g"] * D["base_z"]) / (D["top_g"] + D["base_g"])
D["tip_deg"] = round(math.degrees(math.atan2(D["disc_d"] / 2, D["com"])))

# ----------------------------------------------------------------------------- the energy budget (mA; mAh/day = mA x 24)
E = dict(
    c3_sleep=0.13,      # ESP32-C3 light sleep, datasheet figure
    ldo=0.05,           # the SuperMini's regulator, idle (unknown part; measure)
    en_pullup=0.037,    # EN tied to G through the board's 100 kΩ pull-up at 3.7 V
    bq_batt=0.004,      # bq25185 battery-only quiescent, datasheet 4 µA
    led_on=4.0,         # the 0805 warm white through 100 Ω from the 3.3 V rail
    blink_duty=0.05,    # 100 ms every 2 s
    steady_duty=0.30,   # PWM-dimmed "on"
    power_led=1.0,      # the SuperMini's red power LED if it is NOT removed (about; measure)
    pool_full=12.0,     # the 3 V filament through 68 Ω from the 3.3 V rail, the hologram's figure
    pool_dim=3.0,       # the pool PWM-dimmed for the glow mode
    bq_in=0.75,         # bq25185 input quiescent while charging, datasheet 0.75 mA typ: the panels must beat this
    cell_mah=950, cell_usable=850,            # Nitecore NL169; usable down to the controller's 3.25 V floor
    isc=90.0, irated=90.0, lux_rated=100000,  # the listing's 90 mA short circuit taken as full sun: its "38 000 lux" was a halogen test lamp, worth nearly three daylight lux each to silicon, and 25 cm² of mono cells cannot give more than about 95 mA in any light (corrected 2026-11-03 evening; it was 38 000)
)
E["sleep"] = E["c3_sleep"] + E["ldo"] + E["en_pullup"] + E["bq_batt"]
E["blink"] = E["sleep"] + E["led_on"] * E["blink_duty"]
E["steady"] = E["sleep"] + E["led_on"] * E["steady_duty"]
E["blink_days"] = E["cell_usable"] / (E["blink"] * 24)
E["steady_days"] = E["cell_usable"] / (E["steady"] * 24)
E["blink_days_pl"] = E["cell_usable"] / ((E["blink"] + E["power_led"]) * 24)
E["glow"] = E["blink"] + E["pool_dim"]                       # beacon blinking, the pool dim and steady
E["lamp"] = E["steady"] + E["pool_full"]                     # beacon steady, the pool flat out
E["glow_days"] = E["cell_usable"] / (E["glow"] * 24)
E["lamp_days"] = E["cell_usable"] / (E["lamp"] * 24)
E["usb_h"] = E["cell_mah"] / 500 + 0.3                        # a 500 mA charge plus the taper


def panel_ma(lux, daylight=True):
    """Short-circuit current of the series pair at a light level: linear in lux from the listing's test point;
    room LED light is worth about 0.65 of daylight per lux on silicon."""
    return E["isc"] * lux / E["lux_rated"] * (1.0 if daylight else 0.65)


def net_ma(lux, daylight=True):
    return max(0.0, panel_ma(lux, daylight) - E["bq_in"])


LIGHT = [  # (where, lux, daylight?, note)
    ("desk, room light only", 500, False, "below what the charger itself eats"),
    ("beside a window, dull day", 1000, True, "barely above the charger's floor"),
    ("beside a window, bright day", 3000, True, "about the beacon's daily need"),
    ("on the sill, overcast sky", 10000, True, "beacon with margin; not the glow"),
    ("an hour of direct sun", 100000, True, "the listing's full-sun figure; nine hours fill the cell"),
]

# ----------------------------------------------------------------------------- the contract: ESP32-C3 SuperMini pins
PINS = [  # (pin, job, goes to, net)
    ("5V", "power in, 3.5 to 4.0 V from the cell through the diode", "SS14 cathode; anode to the charger's BAT pad", "V5"),
    ("GND", "ground", "charger − terminal · the beacon's − lead · the filament's − lead · button", "GND"),
    ("GPIO0", "beacon, high = lit, PWM dims it", "100 Ω, then the beacon chip's + lead, inside the box", "LED"),
    ("GPIO1", "downlight, high = lit, PWM dims it", "68 Ω, then the filament's + lead; − lead to GND", "LAMP"),
    ("GPIO10", "mode button, active low, internal pull-up", "button, other leg to GND", "BTN"),
    ("3V3", "3.3 V out of the board's regulator", "nothing (the LED takes its 3.3 V through GPIO0)", None),
    ("GPIO2", "free: strapping pin, must float or sit high at boot", "nothing", None),
    ("GPIO8", "free: the blue LED (lit when low) and a strapping pin", "nothing; firmware holds it high", None),
    ("GPIO9", "free: the BOOT button", "nothing", None),
    ("GPIO3 to 7, 20, 21", "free", "nothing (GPIO3 or 4 is the ADC pin for a cell-voltage divider, if ever wanted)", None),
    ("USB-C", "flashing and the console only", "a computer, through its own slot in the lid; safe with the cell in because of the diode", None),
]

NETS = [  # (net, from, to, wire, why)
    ("SOL+", "wing A, red lead", "charger VIN pad", "the panel's own 150 mm lead, along the left boom",
     "The top of the series pair. Two 5 V panels in series read 12.2 V open-circuit in sun and still 7 to 8 V in a dim room, so they always sit above the 4.5 to 4.8 V the charger wants at its input (battery + 0.33 V, plus its own Schottky). The board takes 5 to 18 V on this pad."),
    ("SOL mid", "wing A, black lead", "wing B, red lead", "the panels' own leads, joined inside the bus",
     "The series link. Each wing's two leads run under its panel along the boom and through a 2.5 mm hole beside the boom socket; the link is a joint inside the box, nothing else."),
    ("GND", "wing B, black lead", "charger G pad", "the panel's own 150 mm lead, along the right boom",
     "The bottom of the pair. The charger's single G pad takes this wire and the EN wire; every other ground goes to the − screw terminal or the controller's GND pin."),
    ("EN", "charger EN pad", "charger G pad", "30 AWG, 15 mm",
     "Pulls the 5 V boost converter's enable low: the boost and its green LED stay off. The pad has a 100 kΩ pull-up to the cell rail, so this costs 37 µA, against about 1 mA if the boost and its LED ran."),
    ("VBAT", "charger BAT pad", "SS14 anode", "30 AWG",
     "The cell, straight: the BAT pad is the battery terminal. The load on it is 0.2 to 1.5 mA, invisible to the charger's 50 mA termination."),
    ("V5", "SS14 cathode (band)", "controller 5V pin", "30 AWG",
     "The controller's regulator takes 3.5 to 4.0 V here and makes 3.3 V. The diode is there for the controller's own USB-C: on this board the 5V pin is USB VBUS with no diode, so without it a flashing cable would push 5 V straight into the cell. It costs 0.15 V and nothing else."),
    ("GND", "charger − screw terminal", "controller GND pin", "30 AWG",
     "One ground between the two boards, in the screw terminal of the unused 5 V output so no third wire needs the G pad."),
    ("LED", "GPIO0", "100 Ω, then the beacon chip's + lead", "the chip's own enamelled lead, tinned, plus the resistor's leg",
     "A warm-white chip drops 2.8 to 3.0 V at a few milliamps; 100 Ω from a 3.3 V pin sets 4 to 5 mA, a clear point in a room and inside the chip's 20 mA; 68 Ω from the kit gives 7 mA if it looks faint. PWM dims it for the steady mode. GPIO0 floats briefly at boot, so the beacon may flash once; it is a lamp, so that is harmless."),
    ("GND", "the beacon chip's − lead", "controller GND pin", "the chip's own enamelled lead, tinned",
     "The return. The chip is glued flat on the top face at the corner; its two 0.1 mm leads run 1 mm over the surface and down a 1.2 mm pinhole, so nothing stands up but 1.1 mm of chip. The enamel burns off when the lead ends are tinned."),
    ("LAMP", "GPIO1", "68 Ω, then the filament's + lead", "30 AWG, inside the box; the filament's own leads come up through the floor",
     "The amber pool. A 3 V filament on a 3.3 V pin needs the resistor: about 2.5 V across the LEDs, 68 Ω, some 12 mA flat out, the hologram's figure and inside the pin's 20 mA. PWM dims it to about 3 mA for the glow mode. Both leads leave one end of the filament; they come up through a 1.5 mm hole in the floor beside it."),
    ("GND", "the filament's − lead", "controller GND pin", "the filament's own lead, then 30 AWG",
     "The pool's return, into the same lane as the beacon's and the button's. Never connect the filament without the resistor."),
    ("BTN", "GPIO10", "button leg 1", "30 AWG", "The mode button: off, beacon, glow, off; a long press in glow turns the pool up full. Internal pull-up, so no resistor; the family's button pin."),
    ("GND", "button leg 2", "controller GND pin", "30 AWG", "The button's return, into the same GND pin as the beacon's − lead (a 30 AWG and a hair wire fit one pin)."),
    ("CELL", "holder leads", "JST-PH pigtail, then the charger's JST-PH socket", "the holder's two leads soldered to the owned pigtail, in heat-shrink", "The cell never meets an iron: the holder's leads join the pigtail 40 mm away from it. The button top is +; it goes to the pin the board marks +. Meter the plug with the cell in before it goes in."),
    ("USB", "wall adapter", "charger USB-C", "the cable", f"The fallback: 500 mA into the cell, full in about {E['usb_h']:.1f} h, inside the charger's 6 h timer. The board's two Schottkys keep the panels and the cable from fighting."),
]

# ----------------------------------------------------------------------------- parts: owned items stay off the shopping list
PARTS = [
    ("Bought on Amazon 2026-11-03: three lines, $32.83 with tax in three orders", [
        ("2 of 5", "mini solar panel, 80 × 45 mm, polycrystalline, 5 V 90 mA, 150 mm leads", L["panel"], "Amazon B0FL26KWWT (MECCANIXITY 5-pack, style 5V 0.45W 90mA)", "$12.29 ($13.38 with tax); order 111-1980686-5970641 of 2026-11-03, arriving 2026-11-07",
         f"The wings, chosen by the builder on 2026-11-03 evening: a rectangle a little smaller than the reference's 110 × 60 mm panel, and Amazon's one such panel with leads. 10 poly cells under epoxy, 5 V working, about 6.1 V open circuit, {E['isc']:.0f} mA at full sun (the same as the 56 mm squares the sheet was approved with), red and black 150 mm leads welded on, so nothing is soldered on the panel. Two in series, three spare. **Incoming check:** in daylight at a window the pair reads 10 to 12 V open circuit on the meter, red positive, and each panel the same short-circuit current."),
        ("1 of 20", "pre-wired warm-white LED chip, 0805", L["led"], "Amazon B09QGJ9LY7 (DiCUNO 20-pack, warm white)", "$7.99 ($8.70 with tax); order 111-9152603-4910637 of 2026-11-03, arriving 2026-11-04",
         "The beacon: a 2.0 × 1.25 × 1.1 mm chip that comes with two 16 cm enamelled leads already soldered on, glued flat on the top of the bus 5 mm in from the front and the right wall, its leads down a 1.2 mm pinhole beside it. 2.8 to 3.3 V, 20 mA capacity, 120°, 20 to 250 mcd. The listing says warm white and gives no colour temperature, so **check it against a 2700 K bulb before gluing**; nineteen spares to pick from. Runs at 4 to 5 mA here through 100 Ω. Tin the lead ends with a hot iron (the enamel burns off) and **meter the polarity with the diode test, which lights it faintly**, before soldering."),
        ("0 of 1", "stainless disc, 3 in × 1/8 in, 304", L["steel_disc"], "Amazon B08JD6GY21 (Harness Machine & Fab, US made)", "$9.87 ($10.75 with tax); order 111-4967394-9172244 of 2026-11-03, picked up 2026-11-06",
         "**Not used.** The first base, 76 mm and 115 g. On the bench the steel read too white, so on 2026-11-06 the builder chose brass to match the family (next table). Spare."),
    ]),
    ("To buy: one line", [
        ("1", "brass coaster, 75 × 8 mm, flat top, hollow underneath", L["disc"], "Amazon B0D9DMK3L7 (heavy brass coaster, 3 in, one piece)", "price not read (Amazon refuses automated reads)",
         f"The base, chosen by the builder on 2026-11-06: the steel disc looked too white, and brass is the family's metal and the amber light's colour. 75 mm across and 8 mm tall, but only {D['coaster_g']:.0f} g (2.82 oz, the listing): a thin brass top over a hollow, with a non-slip pad. Too light alone (it would tip at about 25°) and too thin to drill, so the printed hub is glued on top and about {D['ballast_g']:.0f} g of steel is epoxied into the hollow, then the pad goes back: {D['disc_g']} g in all, tipping at about {D['tip_deg']}°. **Incoming check:** look underneath and measure the hollow's inside diameter and depth (they pick the steel: stacked fender washers if it is round and flat, steel BBs in epoxy if not); a magnet must not stick to the top. Clear lacquer or wax if it should stay bright."),
    ]),
    ("To print: black PETG, three small parts (no filament to buy if a spool is on the shelf)", [
        ("1", f"bus box, {D['box_w']:.0f} × {D['box_d']:.0f} × {D['box_h']:.0f} mm, 2 mm walls, open at the back", "", "printed", "about 20 g",
         f"The body, sized round the cell holder. A 6 mm boss under the floor takes the post (1.6 mm hole, 8 mm deep); a 6 mm boss on each side wall at mid-height takes a boom (1.6 mm hole, 8 mm deep through boss and wall) with a 2.5 mm wire hole beside it; a 1.2 mm pinhole in the top, {D['hole_x']:.1f} mm in from the right wall and {D['led_off']:.0f} from the front, takes the beacon's leads, and the chip glues flat beside it; a 1.5 mm hole in the floor, {-D['lamp_y']:.0f} mm ahead of the post, takes the filament's leads. "
         "Inside: the holder along the front wall, the charger and the controller side by side behind it, both USB-C ports at the lid. **Check the envelope against the real holder, boards and cell before printing** (Cyber Dawn's rule); the Adafruit board's terminal block is 10 mm tall and faces the holder."),
        ("1", f"back lid, {D['box_w'] - 2*D['wall']:.0f} × {D['box_h'] - 2*D['wall']:.0f} × {D['lid']:.1f} mm, press fit", "", "printed", "about 3 g",
         "The service side: two 9 × 3.4 mm slots, one for the charger's USB-C (the charge) and one for the controller's (flashing), and a 6.5 mm hole for the mode button, which is glued to the lid's inside. Neither cable needs the lid off; pull the lid to swap the cell."),
        ("1", "hub, 12 mm diameter × 8 mm, 1.6 mm hole 7 mm deep", "", "printed", "about 1 g",
         "Glued to the centre of the brass coaster's flat top with CA; the post's lower socket. The coaster's top is too thin to drill."),
    ]),
    ("Owned: electronics", [
        ("1 of 2", "solar charger board with 5 V boost (bq25185)", L["charger"], "Adafruit 6106", "Cyber Dawn's spare, bought 2026-10-26 (cyber_clock_v2/docs/INVENTORY.md)",
         "**Owned.** USB-C or 5 to 18 V on the VIN pad, Schottky-ORed; 4.2 V Li-ion profile; 1 A charge, 500 mA after the jumper on the back is cut (**cut it**: Adafruit asks for 500 mA or less on this cell); holds a weak input at battery + 0.33 V and never terminates while doing so; fixed 6 h timer, reset by dark; 4 µA from the cell when idle. "
         "The 5 V boost is disabled by EN to G and its screw terminal is used only as a ground point. 29.2 × 19.1 mm, 2.5 mm holes 24.1 × 14.0 mm apart. The 50 mA display that sank Cyber Dawn's solar is not here: this load is 0.2 to 1.5 mA."),
        ("1 of 13", "Nitecore 16340 cell, 950 mAh, protected, button top", L["cell"], "Nitecore NL169; 13 owned, two IMR Batteries orders of 2026-10-16 delivered 2026-10-21", "owned",
         f"**Owned.** 16.6 × 34.1 mm, 20 g, 3.42 Wh, protection under the wrap, 4.20 V termination, 2 A limit against a load of 13 mA at most. Charge at 500 mA, 0.53 C, so the jumper is cut. It lies in its holder along the front wall of the bus, button top to the right, and swaps without a tool: pull the lid, lift it out. {E['blink_days']:.0f} days of blinking in the dark, {E['glow_days']:.0f} of glow. The 500 mAh pouch the sheet was approved with goes back to Pocket AI stock."),
        ("1 of 10", "16340 holder with leads", L["holder"], "ACEIRMC, Amazon B0CRGK889F (Cyber Dawn's stock)", "owned",
         "**Owned.** A 43 × 18 × 14 mm plastic tray with two spring contacts and two leads, glued to the bus floor along the front wall. Its leads are soldered to an owned JST-PH pigtail (the 20-pair set in Pocket AI stock) in heat-shrink, 40 mm from the cell, and the plug goes into the charger's socket. **Meter the plug before it goes in: the button-top end is +.**"),
        ("1 of 13", "ESP32-C3 SuperMini controller", L["controller"], "Amazon B0F888JQ91 (Meshnology 10-pack) and a 3-pack", "Pocket AI stock",
         "**Owned.** 22.5 × 18 mm, native USB, the family's board. Powered at its 5V pin from the cell through the diode. **Remove its red power LED** (the 0603 part by the USB connector, or its resistor): it would burn about 1 mA all day, five times the sleeping controller. Wi-Fi stays off. Gate it with `esptool flash_id` as before."),
        ("1 of 100", "Schottky diode SS14", L["schottky"], "Chanzon, Amazon B079KJ46ZS (SMA)", "drone stock, 2026-10-28",
         "**Owned.** Inline between the charger's BAT pad and the controller's 5V pin, band toward the controller, in heat-shrink. 0.15 V at this current. It exists so the controller's USB-C can be plugged with the cell connected."),
        ("1 of 10", "LED filament, 3 V, 38 mm, 2200 K", L["filament"], "Amazon B0FR35BGYL (QIROGKC 10-pack; size 38MM, colour 2200k)", "the desk hologram's pack, ordered 2026-11-01, due 2026-11-03; one used there, nine spare",
         "**Owned.** The amber pool under the body, the warm tone that matches the family's brass: a ceramic strip of LEDs, the kind inside an Edison bulb, both leads at one end, a polarity mark. Kapton-taped flat under the box floor 10 mm ahead of the post, parallel to the wings, glowing down the post onto the brass base. GPIO1 through 68 Ω, about 12 mA flat out, PWM-dimmed. The strip is brittle: bend the leads, never the strip; never connect it without the resistor."),
        ("1 + 1", "100 Ω and 68 Ω resistors, 1/4 W", "", "LuminologyPro kit, owned · no link recorded", "Pocket AI stock",
         "**Owned.** 100 Ω in series with the beacon on GPIO0, 68 Ω with the filament on GPIO1, both inside the box in heat-shrink. 20 mA is a pin's ceiling. The two resistors in the build."),
        ("1", "tactile button, 6 × 6 mm", "", "QTEATAK kit, owned ×420 · no link recorded", "Pocket AI stock",
         "**Owned.** The mode button, glued inside the lid with its cap through the 6.5 mm hole; two 30 AWG leads to GPIO10 and GND."),
        ("about 0.4 m", "30 AWG silicone wire", L["wire30"], "CBAZY kit, Amazon B073RDGTPB", "Pocket AI stock",
         "**Owned.** Seven short wires inside the box; the wings and the beacon bring their own leads. Nothing carries more than 0.5 A for an hour (the USB charge), which 30 AWG does."),
        ("", "Kapton tape, white heat-shrink, CA glue, solder", L["kapton"], "ELEGOO Kapton B072Z92QZ2; the rest no links recorded", "owned bench stock",
         "**Owned.** Kapton under the boards and over the filament under the floor, heat-shrink on the diode, the two resistors and the pigtail joint, CA for the three rod sockets, the hub, the holder and the beacon chip; epoxy for the steel in the base. No flux beyond the solder's own: every joint is copper to copper, none on steel, none within 40 mm of the cell."),
        ("1", "USB-C wall adapter, 2 A, and a cable", "", "owned, no link recorded", "owned",
         "**Owned.** The fallback charger: into the charger board's port through the lid. Unplug when the orange light goes out; the satellite never needs it plugged in."),
    ]),
    ("Owned: frame", [
        ("3 of 10", "1.5 mm stainless rod, 150 mm coupons", L["rod15"], "uxcell 304, Amazon B082ZNMD46", "bought 2026-10-27 as coupon stock for the stainless builds",
         f"**Owned.** One coupon cut to {D['post_cut']:.0f} mm is the post ({D['hub_hole']:.0f} in the hub, {D['post_free']:.0f} free, {D['boss_h']:.0f} in the boss). The second and third give one boom each at {D['boom_cut']:.0f} mm: {D['wall'] + D['yoke_l']:.0f} in the wall and yoke, {D['gap']:.0f} of air, {D['panel']:.0f} glued along the panel's back centreline with CA or epoxy. No solder anywhere in the frame."),
    ]),
]

DECISIONS = [
    ("A satellite at a glance: body, two wings, a light on the corner",
     f"The reference is a copper-wire cube with a clock inside, two solar wings and a dish, on a brass tube over a coaster. Ours keeps that silhouette and nothing it does not need: a matte black bus {D['box_w']:.0f} × {D['box_d']:.0f} × {D['box_h']:.0f} mm, two {D['panel']:.0f} × {D['panel_d']:.0f} mm panels on short booms, "
     f"a tiny warm light glued on its top front corner, an amber pool under the body on a brass base, one stainless post, one brass base. {D['span']:.0f} mm wing tip to wing tip, {D['height']:.0f} mm tall, about {D['top_g'] + D['base_g']:.0f} g. No display, no clock, no sensor: the builder's brief is panels, a cell they keep topped up, USB as the fallback, and a 3000 K beacon at the tip that is on or blinks."),
    ("Two 5 V wings in series, in a rectangle",
     "The charger holds a weak input at the cell's voltage plus 0.33 V and will not charge below that, and the board adds a Schottky, so the wings must deliver 4.3 to 4.7 V in whatever light they get. One 10-cell 5 V panel opens at 6.1 V in sun and about 4 V in a bright room: too low exactly when it matters. "
     f"Two in series open at 12.2 V in sun and 7 to 8 V in a room, always above the line, and the charger pulls the pair down and takes their full current, {E['isc']:.0f} mA in sun; the board is rated to 18 V. The wings changed at the builder's word on the evening of 2026-11-03: the sheet was approved with two 56 mm squares; the builder then wanted a rectangle a little smaller than the reference's 110 × 60 mm panel, and Amazon's one such panel with leads is the [80 × 45 mm 5 V 90 mA poly]({L['panel']}) with 150 mm leads welded on: the same current as the squares, nothing to solder on the panel, {D['span']:.0f} mm wing tip to wing tip."),
    ("Cyber Dawn's spare charger board, straight from the drawer",
     f"Cyber Dawn bought two [bq25185 boards]({L['charger']}) and dropped solar on 2026-10-31 because a 5 W panel could not feed a clock whose display alone drinks 50 mA (its `SOLAR_FEASIBILITY.md` is the record). Here the whole satellite sleeps at 0.2 mA and blinks at 0.4, a hundred times less, so the same board and a pair of 80 × 45 mm panels close the budget at a bright window. "
     "What the board gives, from its schematic and TI's datasheet: USB-C and a 5 to 18 V VIN pad through two Schottkys, so the panels and a cable never fight; charging that follows a weak input instead of collapsing it; no false termination while it does so; a 6 h timer that a night resets; 4 µA from the cell when idle; 500 mA with the jumper cut. Its 5 V boost converter is switched off with one wire (EN to G) and its screw terminal becomes a ground point."),
    ("A 16340 in a holder, never soldered",
     f"The sheet was approved with the owned 500 mAh pouch. The same day the builder chose a [Nitecore 16340 cell]({L['cell']}) instead, thirteen in the drawer from two IMR Batteries orders of 2026-10-16: 950 mAh, protection under the wrap, button top, 20 g. {E['blink_days']:.0f} days of blinking in the dark instead of 45, {E['glow_days']:.0f} of glow instead of 5, and a cell that lifts out of its [holder]({L['holder']}) when the lid is off. "
     f"The holder is Cyber Dawn's 43 × 18 × 14 mm tray; its leads meet an owned JST-PH pigtail 40 mm from the cell, so no iron comes near it, and the plug goes into the charger's socket. The price is the box: the bus grows from 42 × 41 × 22 to {D['box_w']:.0f} × {D['box_d']:.0f} × {D['box_h']:.0f} mm to take the tray along its front wall with the two boards behind it, both ports through the lid, and the satellite gains about 25 g."),
    ("The controller runs from the cell through one diode, and the boost stays off",
     f"The board's BAT pad is the cell. One [SS14]({L['schottky']}) from it to the controller's 5V pin gives the controller 3.5 to 4.0 V, which its own regulator turns into 3.3 V, and costs 0.15 V. The diode is not for the charger: on the SuperMini the 5V pin is USB VBUS with no diode, so without it plugging a flashing cable would push 5 V straight into a lithium cell. With it, flash whenever you like. "
     "The charger's 5 V boost would be the tidy way to power a 5 V board, but it idles at about a milliamp with its green LED, five times the sleeping controller; one wire from EN to G turns it off for 37 µA through its pull-up."),
    ("The ESP32-C3 SuperMini again, with its power LED gone",
     "Thirteen are owned, the toolchain exists, and the firmware is a hundred lines: light sleep with a timer, a pin, a button. The chip sleeps at 0.13 mA in light sleep and wakes in a millisecond, which is what a blink wants; deep sleep would spend more rebooting every two seconds than it saves. The board's red power LED burns about 1 mA all day, five times the rest of the sleeping satellite, so it comes off with tweezers before anything is wired. "
     "An ATtiny would sleep at 1 µA and make a desk under room light nearly self-sustaining, at the price of a new toolchain and programmer; written down here as the upgrade if the window budget ever feels thin."),
    ("The beacon: a chip glued on the corner, no legs, no mast",
     f"The first draft put a 3 mm LED on two bare rods 52 mm above the bus. The builder wanted a small light stuck on the corner, not a tall pin, with no legs at all, so the mast went the same morning and the LED became a [pre-wired 0805 chip]({L['led']}): 2 × 1.25 × 1.1 mm, with two 0.1 mm enamelled leads already soldered on. "
     f"It is glued flat on the top of the bus {D['led_off']:.0f} mm in from the front and the right wall, its leads run 1 mm over the surface and down a 1.2 mm pinhole, and the resistor sits inside above the controller: nothing stands up but {D['led_h']:.1f} mm of chip, and nothing is soldered to the box. "
     "A warm-white chip drops about 2.9 V, so 100 Ω from the 3.3 V pin gives 4 to 5 mA, a clear point of light in a room (the kit's 68 Ω gives 7 mA if it looks faint; the chip takes 20); PWM dims the steady mode to about a quarter. The overall height falls from 209 to 152 mm."),
    ("An amber pool under the body",
     f"The builder asked for a light below the satellite that shines down, in the warm yellow that matches the family's brass. The hologram's [LED filament]({L['filament']}), the 38 mm 2200 K strip with nine spare in its pack, is Kapton-taped under the floor of the bus {-D['lamp_y']:.0f} mm ahead of the post, parallel to the wings, glowing down the post onto the brass base {D['post_free'] + D['boss_h']:.0f} mm below: a pool of amber on brass. "
     f"GPIO1 drives it through 68 Ω, about {E['pool_full']:.0f} mA flat out (the hologram's figure), PWM-dimmed to {E['pool_dim']:.0f} for the glow mode; its two leads come up through a 1.5 mm hole in the floor. It is the one thing on this satellite that is not for the satellite's own sake, and it costs: the glow mode is {E['glow']:.1f} mA, {E['glow_days']:.0f} days on the cell in the dark, so it is the window and evening mode, and the beacon alone is the one that lives on the wings."),
    ("One post on a weighted brass base, a printed hub and box: no solder in the frame",
     f"A [brass coaster]({L['disc']}), {D['disc_d']:.0f} × {D['disc_t']:.0f} mm, is the base. It weighs only {D['coaster_g']:.0f} g, a thin top over a hollow, so about {D['ballast_g']:.0f} g of steel is epoxied into the hollow and the pad goes back over it: {D['disc_g']} g, all of it in the bottom 8 mm, unseen. A 12 mm printed hub glued to its flat top is the post's socket, since the top is too thin to drill. It replaced the 3 in stainless disc on 2026-11-06 at the builder's word: the steel read too white on the bench, and brass is the family's metal and the amber pool's colour. The post is one 1.5 mm coupon, {D['post_free']:.0f} mm free, into a boss under the box. Each boom is a 1.5 mm rod in a 6 mm boss on the box's side wall, glued along the back of its panel. "
     f"Three sockets, three drops of CA, zero frame joints, no solder on steel anywhere. Centre of mass {D['com']:.0f} mm up on a {D['disc_d']:.0f} mm base: it tips at about {D['tip_deg']}°, against 30° on the steel disc and about 25° on the coaster unweighted. The box is the one printed body in the family after Cyber Dawn's, and for the same reason: a satellite bus is a box."),
    ("What the panels really do",
     f"The charger itself takes about {E['bq_in']:.2f} mA from its input while charging, so below about 1 mA of panel current nothing is stored. Room light on a desk (500 lux) gives the pair about {panel_ma(500, False):.1f} mA: nothing. Daylight beside a window (1 000 to 3 000 lux) gives {panel_ma(1000):.1f} to {panel_ma(3000):.1f} mA, so {net_ma(1000):.1f} to {net_ma(3000):.1f} mA net, "
     f"which over the charger's 6 h window is {net_ma(1000) * 6:.0f} to {net_ma(3000) * 6:.0f} mAh a day against the beacon mode's {E['blink'] * 24:.0f}: a bright window carries it, a dull one does not. An overcast sill ({panel_ma(10000):.0f} mA, {net_ma(10000) * 6:.0f} mAh a day) banks five beacon days in one; the glow mode's {E['glow'] * 24:.0f} wants hours of direct sun or the cable. On a desk away from the window it is a {E['blink_days']:.0f}-day battery object that gets a USB top-up; at a bright window it is a solar one. "
     "These are the listing's full-sun figure scaled by lux (its 38 000 lux was a halogen lamp, which silicon counts at nearly three daylight lux each), not measurements; the first week on the sill, with the cell voltage read each evening at the BAT pad, is the real number."),
    ("A reference, not a copy",
     "Huy Vector's satellite is a copper-wire cube with a clock face, a dish, a charging module beside a separate solar controller, on a brass tube over a bamboo coaster. This one keeps only the idea: a body on one post over a round base, two solar wings. "
     "Everything else is its own: a closed matte black bus instead of an open wire cube, no screen and no clock, a stainless post on a weighted brass plinth instead of a brass tube over bamboo, two panels in series into one board that is also the USB charger, a legless chip beacon on the corner where the reference has a dish, and an amber pool under the body that the reference does not have. Side by side they share a silhouette and nothing else."),
    ("How it sits with the family",
     "Black, steel and brass: one 1.5 mm stainless post like the drone's rods, a printed black body like Cyber Dawn's, a brass base like the Pocket AIs' metal, and nothing on it that is decoration. The wings are the two biggest parts and they are the power supply; the lights are a chip on the corner and the hologram's amber filament underneath, glowing on the brass. "
     f"At {D['span']:.0f} mm wide and {D['height']:.0f} tall it stands beside the 82 mm Cyber Dawn and the 72 mm hologram as the wide one. Prototype, not product: the lid pulls off, the cell unplugs, the firmware reflashes."),
]

FIRMWARE = [
    "ESP-IDF 6.0.2 for the esp32c3, a new small project (no Wi-Fi, no server): `esp_pm` light sleep with the RTC timer; GPIO0 as the beacon, GPIO10 as the button with the internal pull-up, GPIO8 driven high so the blue LED stays dark.",
    "Three modes in NVS, cycled by a short press: off; beacon (the chip blinks 100 ms every 2 s: set the pin, sleep 100 ms, clear it, sleep 1.9 s); glow (the beacon blinks and the pool sits at about 3 mA on LEDC PWM, RC_FAST clock so it keeps running in light sleep). A long press in glow turns the pool up full and the beacon steady until the next press.",
    "Nothing else runs. Wi-Fi never starts; the radio's 300 mA peaks have no place in this budget. Console on USB Serial/JTAG when a cable is in.",
    "First-power measurements the record wants: the board's current with the power LED gone, in each mode (expected about 0.2, 0.4, 3.4 and 13 mA), the beacon's current on GPIO0 (3 to 5 mA) and the filament's on GPIO1 (about 12 mA).",
    "If the cell voltage is ever wanted on the beacon (a slow double-blink below 3.4 V): two resistors from BAT to GND into GPIO1, read once an hour. Not drawn; it costs two parts and 4 µA.",
]

CHECKS = [
    "The holder's plug against the charger's socket, before it goes in: the lead from the button-top end on the pin the board marks +, the pigtail joint in heat-shrink; meter the plug with the cell in, 3.6 to 4.1 V, right way round.",
    "The diode's direction, before the controller is powered: band toward the controller's 5V pin; the BAT pad shows the cell's voltage, the 5V pin shows 0.15 V less. Then the panel pair at the VIN and G pads in daylight: positive, 10 to 12 V open circuit, red lead +. Then the beacon's two leads on the diode test: it lights faintly one way; mark that lead +. The filament's + mark goes toward its resistor.",
    "The frame floats: post to G open, each boom to G open (the wing wires run beside the booms, so a nick would show here). Everything else is a supplier spec and is not metered.",
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
                    vx, vy0, vy1, hx0, hx1, hy = (x0, y0, y1, a0, a1, b0) if v1 else (a0, b0, b1, x0, x1, y0)
                    if min(hx0, hx1) + 0.5 < vx < max(hx0, hx1) - 0.5 and min(vy0, vy1) + 0.5 < hy < max(vy0, vy1) - 0.5:
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
    """Horizontal resistor between (x0, y) and (x1, y): straight, zigzag in the middle, straight."""
    mid = (x0 + x1) / 2
    z = 8
    pts = [(x0, y), (mid - 15, y)]
    for i, dy in enumerate((z, -z, z, -z, z, -z)):
        pts.append((mid - 15 + (i + 0.5) * (30 / 6), y + dy))
    pts += [(mid + 15, y), (x1, y)]
    return rt.wire(pts, "thin", net)


def diode_h(x0, x1, y):
    """Diode symbol pointing right between x0 and x1 (anode left, cathode/band right); not a wire."""
    xm = (x0 + x1) / 2
    return (f'<path d="M{x0},{y} L{xm - 8},{y} M{xm + 8},{y} L{x1},{y}" class="thin"/>'
            f'<path d="M{xm - 8},{y - 9} L{xm + 8},{y} L{xm - 8},{y + 9} z" class="solid"/>'
            f'<line x1="{xm + 8}" y1="{y - 9}" x2="{xm + 8}" y2="{y + 9}" class="thin"/>')


def dim_h(x0, x1, y, label, above=True, cls="dim"):
    o = [f'<path d="M{x0},{y-6} L{x0},{y+6} M{x1},{y-6} L{x1},{y+6} M{x0},{y} L{x1},{y}" class="{cls}"/>']
    o.append(T((x0 + x1) / 2, y - 5 if above else y + 15, label, "dimlab", "middle"))
    return "".join(o)


def dim_v(x, y0, y1, label, right=True, cls="dim"):
    o = [f'<path d="M{x-6},{y0} L{x+6},{y0} M{x-6},{y1} L{x+6},{y1} M{x},{y0} L{x},{y1}" class="{cls}"/>']
    ym = (y0 + y1) / 2
    if right:
        o.append(T(x + 8, ym + 4, label, "dimlab", "start"))
    else:
        o.append(T(x - 8, ym + 4, label, "dimlab", "end"))
    return "".join(o)


SHEET_CSS = ("<style>"
             ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
             ".later{fill:var(--paper);stroke:var(--ink-2);stroke-width:1.4;stroke-dasharray:5 4}"
             ".net{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.4}"
             ".usb{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.2}"
             ".title{font:700 17px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".sub{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".h1{font:900 24px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".h2{font:700 15px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".pin{font:700 13px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".lab{font:700 12.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
             ".dimlab{font:700 11.5px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".rod{fill:none;stroke:var(--ink);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
             ".thin{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
             ".opt{fill:none;stroke:var(--ink-2);stroke-width:2;stroke-dasharray:3 5;stroke-linecap:round}"
             ".dim{fill:none;stroke:var(--ink-2);stroke-width:1}"
             ".joint{fill:var(--ink)}"
             ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
             ".solid{fill:var(--ink)}"
             ".board{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.4}"
             ".dark{fill:var(--ink);stroke:none}"
             ".shell{fill:var(--ink);stroke:var(--ink);stroke-width:1}"
             ".cavity{fill:var(--paper);stroke:none}"
             ".cell{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.2}"
             ".panel{fill:var(--ink);stroke:var(--ink);stroke-width:1}"
             ".grid{fill:none;stroke:var(--paper);stroke-width:0.8;opacity:.7}"
             ".steel{fill:none;stroke:var(--ink);stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round}"
             ".steel1{fill:none;stroke:var(--ink);stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}"
             ".plate{fill:var(--line);stroke:var(--ink);stroke-width:1.4}"
             ".ghost{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:3 3}"
             ".hole{fill:var(--paper);stroke:var(--ink);stroke-width:1.2}"
             ".mono{font:400 11px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".onblack{font:700 11.5px 'JetBrains Mono',monospace;fill:var(--paper)}"
             ".lamp{fill:var(--warn);stroke:var(--ink);stroke-width:1}"
             ".glow{fill:none;stroke:var(--warn);stroke-width:1.2;stroke-dasharray:2 3}"
             ".lampbar{fill:none;stroke:var(--warn);stroke-width:4;stroke-linecap:round}"
             ".link{fill:none;stroke:var(--signal);stroke-width:2.2;stroke-dasharray:7 5;stroke-linecap:round}"
             ".rayhead{fill:var(--warn);stroke:none}"
             "</style>")


# ----------------------------------------------------------------------------- sheet 1: the form
def form_sheet():
    o = [T(20, 30, "Desk satellite: how the finished thing looks", "h1"),
         T(20, 48, f"A black bus on one stainless post over a brass base, two solar wings, a tiny warm light on the top front corner, an amber pool below. {D['span']:.0f} wide × {D['panel_d']:.0f} deep × {D['height']:.0f} mm tall, about {D['top_g'] + D['base_g']:.0f} g. Dimensions in mm; each view at its own scale.", "sub")]

    # ---------------------------------------------------------------- front view, 2.4 px per mm
    s = 2.0
    x0, y0 = 290, 568
    X = lambda xm: x0 + xm * s     # noqa: E731  width, right positive
    Z = lambda zm: y0 - zm * s     # noqa: E731  height
    o.append(T(40, 90, "Front view (lid and USB port on the far side)", "h2"))
    o.append(f'<line x1="{X(-100)}" y1="{y0}" x2="{X(100)}" y2="{y0}" class="thin"/>')
    o.append(T(X(100), y0 + 14, "desk", "fn", "end"))
    o.append(f'<rect x="{X(-D["disc_d"]/2)}" y="{Z(D["disc_t"])}" width="{D["disc_d"]*s}" height="{D["disc_t"]*s}" class="plate"/>')
    o.append(f'<rect x="{X(-D["hub_d"]/2)}" y="{Z(D["z_hub"])}" width="{D["hub_d"]*s}" height="{D["hub_h"]*s}" rx="1.5" class="dark"/>')
    o.append(f'<line x1="{X(0)}" y1="{Z(D["z_hub"])}" x2="{X(0)}" y2="{Z(D["z_box"] - D["boss_h"])}" class="steel"/>')
    o.append(f'<rect x="{X(-D["boss_d"]/2)}" y="{Z(D["z_box"])}" width="{D["boss_d"]*s}" height="{D["boss_h"]*s}" class="dark"/>')
    o.append(f'<rect x="{X(-D["box_w"]/2)}" y="{Z(D["z_top"])}" width="{D["box_w"]*s}" height="{D["box_h"]*s}" rx="2" class="shell"/>')
    for sgn in (-1, 1):
        xw = sgn * D["box_w"] / 2
        o.append(f'<rect x="{min(X(xw), X(xw + sgn*D["yoke_l"]))}" y="{Z(D["z_wing"] + D["yoke_d"]/2)}" width="{D["yoke_l"]*s}" height="{D["yoke_d"]*s}" class="dark"/>')
        xa = xw + sgn * D["yoke_l"]
        o.append(f'<line x1="{X(xa)}" y1="{Z(D["z_wing"])}" x2="{X(xa + sgn*D["gap"])}" y2="{Z(D["z_wing"])}" class="steel"/>')
        xp = xa + sgn * D["gap"]
        o.append(f'<rect x="{min(X(xp), X(xp + sgn*D["panel"]))}" y="{Z(D["z_panel"] + D["panel_t"])}" width="{D["panel"]*s}" height="{D["panel_t"]*s}" class="panel"/>')
    o.append(T(X(D["box_w"]/2 + 10), Z(D["z_panel"]) + 16, "wing, edge on, cells up", "fn"))
    # the beacon: a 0805 chip glued flat on the top front-right corner, 1.1 mm proud
    xl_ = D["box_w"]/2 - D["led_off"]
    o.append(f'<rect x="{X(xl_) - D["led_w"]/2*s}" y="{Z(D["z_top"] + D["led_h"])}" width="{D["led_w"]*s}" height="{D["led_h"]*s + 1}" rx="1" class="lamp"/>')
    o.append(f'<circle cx="{X(xl_)}" cy="{Z(D["z_top"] + 0.5)}" r="{7*s}" class="glow"/>')
    o.append(T(X(xl_) + 22, Z(D["z_top"] + 10), "warm-white LED chip, 2 × 1.25 × 1.1 mm, glued flat", "fn"))
    o.append(T(X(xl_) + 22, Z(D["z_top"] + 4.5), "on the top front corner, no legs; leads down a pinhole", "fn"))
    o.append(T(X(xl_) + 22, Z(D["z_top"] - 1), "on, or a 100 ms blink every 2 s", "fn"))
    o.append(T(X(-12), Z(D["z_box"] - D["boss_h"]/2) + 4, "boss: the post's upper socket", "fn", "end"))
    # the amber pool: the filament under the floor, in front of the boss, glowing down onto the disc
    o.append(f'<line x1="{X(-D["lamp_len"]/2)}" y1="{Z(D["z_box"] - 1)}" x2="{X(D["lamp_len"]/2)}" y2="{Z(D["z_box"] - 1)}" class="lampbar"/>')
    for xe in (-30, -14, 14, 30):
        o.append(f'<line x1="{X(xe/2)}" y1="{Z(D["z_box"] - 2.5)}" x2="{X(xe)}" y2="{Z(D["disc_t"] + 0.5)}" class="glow"/>')
    o.append(f'<ellipse cx="{X(0)}" cy="{Z(D["disc_t"]) - 2}" rx="{32*s}" ry="4" class="glow"/>')
    o.append(T(X(22), Z(D["z_box"] - 7), "LED filament under the floor, 2200 K:", "fn"))
    o.append(T(X(22), Z(D["z_box"] - 12.5), "an amber pool on the brass base", "fn"))
    o.append(T(X(6), Z(60) + 4, "1.5 mm stainless post", "fn"))
    o.append(T(X(-D["disc_d"]/2 - 4), Z(D["disc_t"] / 2) + 4, "printed hub, glued on the brass", "fn", "end"))
    # dimensions
    o.append(dim_v(X(-D["span"]/2) - 22, Z(0), Z(D["height"]), f"{D['height']:.0f}", True))
    o.append(dim_v(X(-D["box_w"]/2) - 14, Z(D["z_hub"]), Z(D["z_box"] - D["boss_h"]), f"post {D['post_free']:.0f} free", False))
    o.append(dim_v(X(D["span"]/2) + 22, Z(D["z_box"]), Z(D["z_top"]), f"{D['box_h']:.0f}", True))
    o.append(dim_h(X(-D["span"]/2), X(D["span"]/2), Z(D["height"]) - 40, f"{D['span']:.0f} wing tip to wing tip", True))
    o.append(dim_h(X(-D["box_w"]/2), X(D["box_w"]/2), Z(D["height"]) - 16, f"{D['box_w']:.0f}", True))
    o.append(dim_h(X(-D["disc_d"]/2), X(D["disc_d"]/2), y0 + 34, f"brass {D['disc_d']:.0f} × {D['disc_t']:.0f}, {D['disc_g']} g", False))

    # ---------------------------------------------------------------- the beacon at the corner, 8 px per mm (middle column, top)
    s3 = 8.0
    bx0, bz0 = 900, 204                  # the outer top-right corner of the box in this drawing
    BX = lambda xm: bx0 - xm * s3        # noqa: E731  distance in from the right wall, leftwards
    BZ = lambda zm: bz0 + zm * s3        # noqa: E731  distance down from the top face
    o.append(T(560, 90, "The beacon at the corner, 8 px per mm", "h2"))
    o.append(T(560, 106, "section through the top front-right corner, seen from the front", "fn"))
    o.append(T(560, 130, "0805 chip, 2 × 1.25 × 1.1 mm, glued flat on the top 5 mm in from the front and the right face;", "fn"))
    o.append(T(560, 144, "its own 0.1 mm enamelled leads run 1 mm over the top and down a 1.2 mm pinhole to the resistor", "fn"))
    o.append(T(560, 158, "and GND inside. Nothing stands up but 1.1 mm of chip; nothing is soldered to the box or to steel.", "fn"))
    o.append(f'<rect x="{BX(26)}" y="{BZ(0)}" width="{26*s3}" height="{D["wall"]*s3}" class="shell"/>')          # top wall
    o.append(f'<rect x="{BX(D["wall"])}" y="{BZ(0)}" width="{D["wall"]*s3}" height="{10*s3}" class="shell"/>')    # right wall
    hx = D["hole_x"]
    o.append(f'<rect x="{BX(hx) - 0.6*s3}" y="{BZ(0) - 1}" width="{1.2*s3}" height="{D["wall"]*s3 + 2}" class="cavity"/>')  # the pinhole
    o.append(f'<rect x="{BX(D["led_off"]) - D["led_w"]/2*s3}" y="{BZ(0) - D["led_h"]*s3}" width="{D["led_w"]*s3}" height="{D["led_h"]*s3}" rx="1.5" class="lamp"/>')
    o.append(f'<circle cx="{BX(D["led_off"])}" cy="{BZ(0) - D["led_h"]/2*s3}" r="{5*s3}" class="glow"/>')
    xin = BX(D["led_off"]) + D["led_w"]/2*s3
    o.append(f'<path d="M{xin},{BZ(0) - 4} L{BX(hx) + 2},{BZ(0) - 4} L{BX(hx) + 2},{BZ(5)} L{BX(hx) + 2},{BZ(6)} L{BX(22)},{BZ(6)}" class="thin"/>')
    o.append(f'<path d="M{xin},{BZ(0) - 7} L{BX(hx) - 2},{BZ(0) - 7} L{BX(hx) - 2},{BZ(3)}" class="thin"/>')
    xa_ = BX(hx) - 2
    rz0 = BZ(3)
    pts = [(xa_, rz0), (xa_, rz0 + 4)]
    for i, dx in enumerate((6, -6, 6, -6, 6, -6)):
        pts.append((xa_ + dx, rz0 + 4 + (i + 0.5) * (26 / 6)))
    pts += [(xa_, BZ(7.2)), (xa_, BZ(9)), (BX(22), BZ(9))]
    o.append('<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '" class="thin"/>')
    o.append(T(BX(22) - 6, BZ(6) + 4, "− lead → GND", "lab", "end")); o.append(T(BX(22) - 6, BZ(9) + 4, "+ lead → 100 Ω → GPIO0", "lab", "end"))
    o.append(T(xa_ - 12, BZ(5.2) + 4, "100 Ω", "fn", "end"))
    o.append(T(BX(D["led_off"]), BZ(0) - D["led_h"]*s3 - 8, "chip", "fn", "middle"))
    o.append(T(BX(hx), BZ(D["wall"]) + 14, "pinhole", "fn", "middle"))
    o.append(dim_v(BX(26) - 10, BZ(0) - D["led_h"]*s3, BZ(0), f"{D['led_h']:.1f} proud", False))
    o.append(dim_v(BX(26) - 10, BZ(0), BZ(D["wall"]), f"wall {D['wall']:.0f}", False))

    # ---------------------------------------------------------------- side section through the bus, 6 px per mm (middle column, lower)
    s2 = 6.0
    xs = 745
    Y = lambda ym: xs + ym * s2                        # noqa: E731  depth: front negative (left), back positive (right)
    z0 = D["z_box"] - D["boss_h"] - 3.2                 # the section starts 3.2 mm of post below the boss
    Z2 = lambda zm: 566 - (zm - z0) * s2              # noqa: E731  height, drawn from z0 up
    o.append(T(560, 302, "Side section through the bus, front on the left", "h2"))
    o.append(T(560, 316, "cut through the charger; the back is the service side; the post cut short", "fn"))
    zb, zt = D["z_box"], D["z_top"]
    hd = D["box_d"]
    xl, xr = Y(-hd/2) - 12, Y(hd/2) + 12               # label columns, left (end-anchored) and right
    o.append(f'<rect x="{Y(-D["panel_d"]/2)}" y="{Z2(D["z_panel"] + D["panel_t"])}" width="{D["panel_d"]*s2}" height="{D["panel_t"]*s2}" class="ghost"/>')
    o.append(T(Y(-D["panel_d"]/2) - 6, Z2(D["z_panel"]) + 12, "wing plane", "fn", "end"))
    o.append(f'<rect x="{Y(-hd/2)}" y="{Z2(zt)}" width="{hd*s2}" height="{D["box_h"]*s2}" rx="3" class="shell"/>')
    o.append(f'<rect x="{Y(-hd/2 + D["wall"])}" y="{Z2(zt - D["wall"])}" width="{(hd - 2*D["wall"] - D["lid"])*s2}" height="{(D["box_h"] - 2*D["wall"])*s2}" class="cavity"/>')
    o.append(f'<rect x="{Y(hd/2 - D["wall"] - D["lid"])}" y="{Z2(zt - D["wall"])}" width="{D["lid"]*s2}" height="{(D["box_h"] - 2*D["wall"])*s2}" class="plate"/>')
    zf = zb + D["wall"]
    # the holder tray along the front wall, end on, with the cell in it
    yh0 = -hd/2 + D["wall"]
    o.append(f'<rect x="{Y(yh0)}" y="{Z2(zf + D["holder_h"])}" width="{D["holder_w"]*s2}" height="{D["holder_h"]*s2}" rx="2" class="part"/>')
    o.append(f'<circle cx="{Y(yh0 + D["holder_w"]/2)}" cy="{Z2(zf + 1 + D["cell_d"]/2)}" r="{D["cell_d"]/2*s2}" class="cell"/>')
    o.append(T(Y(yh0 + D["holder_w"]/2), Z2(zf + 1 + D["cell_d"]/2) + 4, "16340", "fn", "middle"))
    zl0 = zf + 0.5
    yb1 = hd/2 - D["wall"] - D["lid"]
    yb0 = yb1 - D["charger_l"]
    o.append(f'<rect x="{Y(yb0)}" y="{Z2(zl0 + 1.6)}" width="{D["charger_l"]*s2}" height="{1.6*s2}" class="board"/>')
    o.append(f'<rect x="{Y(yb0 + 1)}" y="{Z2(zl0 + 1.6 + 10)}" width="{7*s2}" height="{10*s2}" class="part"/>')
    o.append(f'<rect x="{Y(yb1 - 9)}" y="{Z2(zl0 + 1.6 + 3.4)}" width="{(9 + D["lid"])*s2}" height="{3.4*s2}" class="usb"/>')
    zbt = zt - D["wall"] - 5
    o.append(f'<rect x="{Y(yb1 - 3.5)}" y="{Z2(zbt + 3)}" width="{5*s2}" height="{6*s2}" class="part"/>')
    # the beacon chip at the front corner, beyond the cut, flat on the top face
    yl = -hd/2 + D["led_off"]
    o.append(f'<rect x="{Y(yl) - D["led_l"]/2*s2}" y="{Z2(zt + D["led_h"])}" width="{D["led_l"]*s2}" height="{D["led_h"]*s2 + 1}" rx="1.5" class="lamp"/>')
    o.append(f'<circle cx="{Y(yl)}" cy="{Z2(zt + 0.5)}" r="{5*s2}" class="glow"/>')
    # the filament, end on, under the floor ahead of the boss
    o.append(f'<circle cx="{Y(D["lamp_y"])}" cy="{Z2(zb - 1)}" r="{1.2*s2}" class="lamp"/>')
    for ye in (-24, -10, 4):
        o.append(f'<line x1="{Y(D["lamp_y"])}" y1="{Z2(zb - 2.5)}" x2="{Y(ye)}" y2="{Z2(z0)}" class="glow"/>')
    o.append(T(xl, Z2(zb - 1) + 4, "filament, glowing down", "fn", "end"))
    # boss and the post stub
    o.append(f'<rect x="{Y(-D["boss_d"]/2)}" y="{Z2(zb)}" width="{D["boss_d"]*s2}" height="{D["boss_h"]*s2}" class="dark"/>')
    o.append(f'<line x1="{Y(0)}" y1="{Z2(zb - D["boss_h"])}" x2="{Y(0)}" y2="{Z2(z0)}" class="steel"/>')
    # labels, right column, in fixed slots 20 px apart, leaders to what they name
    slots = [(372, "mode button, cap through the lid", (Y(yb1 + 1), Z2(zbt))),
             (392, "charger board, on the floor; controller beside it", (Y(yb0 + D["charger_l"] * 0.55), Z2(zl0 + 1.6))),
             (412, "USB-C: the charge; the controller's port beside it", (Y(yb1 + 1), Z2(zl0 + 3.3))),
             (432, "screw terminal: the one ground joint", (Y(yb0 + 4), Z2(zl0 + 1.6 + 10))),
             (452, "lid, press fit; pull it to swap the cell", (Y(yb1 + D["lid"]/2), Z2(zf + 2)))]
    for yy, txt, (tx2, ty2) in slots:
        o.append(T(xr + 10, yy + 4, txt, "fn"))
        o.append(f'<line x1="{tx2}" y1="{ty2}" x2="{xr + 6}" y2="{yy}" class="dim"/>')
    o.append(T(xl, Z2(zt + 1) + 4, "beacon chip, 1.1 proud", "fn", "end"))
    o.append(T(xl, Z2(zf + 5) + 4, "16340 in its tray", "fn", "end"))
    o.append(T(xl, Z2(zb - D["boss_h"]) + 2, "boss: post socket", "fn", "end"))
    o.append(T(xl, Z2(z0) + 4, "post, cut short", "fn", "end"))
    o.append(dim_h(Y(-hd/2), Y(hd/2), Z2(z0) + 18, f"{hd:.0f}", False))
    o.append(dim_h(Y(-D["panel_d"]/2), Y(D["panel_d"]/2), Z2(z0) + 38, f"wing {D['panel_d']:.0f} deep", False))

    # ---------------------------------------------------------------- top view, 2 px per mm (right column, top)
    st = 1.6
    tx, ty = 1125, 245
    TX = lambda xm: tx + xm * st     # noqa: E731  width
    TY = lambda ym: ty + ym * st     # noqa: E731  depth, front (viewer) at the bottom: back is negative
    o.append(T(940, 90, "Top view", "h2"))
    o.append(T(940, 106, "front of the desk at the bottom; the brass shows around the bus", "fn"))
    o.append(f'<circle cx="{TX(0)}" cy="{TY(0)}" r="{D["disc_d"]/2*st}" class="plate"/>')
    for sgn in (-1, 1):
        xp0 = sgn * (D["box_w"]/2 + D["yoke_l"] + D["gap"])
        o.append(f'<rect x="{min(TX(xp0), TX(xp0 + sgn*D["panel"]))}" y="{TY(-D["panel_d"]/2)}" width="{D["panel"]*st}" height="{D["panel_d"]*st}" rx="1.5" class="panel"/>')
        xa, xb = sorted((TX(xp0), TX(xp0 + sgn*D["panel"])))
        for i in range(1, 5):                     # the ten cells as a 5 x 2 grid
            xx = xa + i * (xb - xa) / 5
            o.append(f'<line x1="{xx:.1f}" y1="{TY(-D["panel_d"]/2) + 3}" x2="{xx:.1f}" y2="{TY(D["panel_d"]/2) - 3}" class="grid"/>')
        o.append(f'<line x1="{xa + 3}" y1="{TY(0)}" x2="{xb - 3}" y2="{TY(0)}" class="grid"/>')
        o.append(f'<rect x="{min(TX(sgn*D["box_w"]/2), TX(sgn*(D["box_w"]/2 + D["yoke_l"])))}" y="{TY(-D["yoke_d"]/2)}" width="{D["yoke_l"]*st}" height="{D["yoke_d"]*st}" class="dark"/>')
    o.append(f'<rect x="{TX(-D["box_w"]/2)}" y="{TY(-D["box_d"]/2)}" width="{D["box_w"]*st}" height="{D["box_d"]*st}" rx="2" class="shell"/>')
    # inside: the holder along the front wall, the two boards side by side behind it with their ports at the lid
    cw = D["box_w"]/2 - D["wall"]; cd_f = D["box_d"]/2 - D["wall"]; cd_b = -(D["box_d"]/2 - D["lid"])
    o.append(f'<rect x="{TX(-cw)}" y="{TY(cd_b)}" width="{2*cw*st}" height="{(cd_f - cd_b)*st}" class="cavity"/>')
    o.append(f'<rect x="{TX(-D["holder_l"]/2)}" y="{TY(cd_f - D["holder_w"])}" width="{D["holder_l"]*st}" height="{D["holder_w"]*st}" rx="2" class="part"/>')
    o.append(f'<rect x="{TX(-D["cell_l"]/2 - 0.5)}" y="{TY(cd_f - D["holder_w"]/2 - D["cell_d"]/2)}" width="{D["cell_l"]*st}" height="{D["cell_d"]*st}" rx="{D["cell_d"]/2*st}" class="cell"/>')
    o.append(f'<rect x="{TX(D["cell_l"]/2 - 0.5)}" y="{TY(cd_f - D["holder_w"]/2 - 2.5)}" width="{1.5*st}" height="{5*st}" class="part"/>')
    o.append(T(TX(-0.5), TY(cd_f - D["holder_w"]/2) + 4, "cell", "fn", "middle"))
    o.append(f'<rect x="{TX(-0.5 - D["charger_w"])}" y="{TY(cd_b)}" width="{D["charger_w"]*st}" height="{D["charger_l"]*st}" class="board"/>')
    o.append(f'<rect x="{TX(0.5)}" y="{TY(cd_b)}" width="{D["c3_w"]*st}" height="{D["c3_l"]*st}" class="board"/>')
    o.append(T(TX(0.5 + D["c3_w"]/2), TY(cd_b + D["c3_l"]/2) + 4, "C3", "fn", "middle"))
    o.append(f'<rect x="{TX(D["box_w"]/2 - D["led_off"]) - D["led_w"]/2*st - 1}" y="{TY(D["box_d"]/2 - D["led_off"]) - D["led_l"]/2*st - 1}" width="{D["led_w"]*st + 2}" height="{D["led_l"]*st + 2}" rx="1" class="lamp"/>')
    o.append(f'<circle cx="{TX(D["box_w"]/2 - D["hole_x"])}" cy="{TY(D["box_d"]/2 - D["led_off"])}" r="1.4" class="hole"/>')
    o.append(f'<circle cx="{TX(D["box_w"]/2 - D["led_off"])}" cy="{TY(D["box_d"]/2 - D["led_off"])}" r="{5*st}" class="glow"/>')
    for xf, lab in ((-10.0, "charge"), (9.5, "flash")):
        o.append(f'<rect x="{TX(xf - D["usb_w"]/2)}" y="{TY(-D["box_d"]/2) - 3}" width="{D["usb_w"]*st}" height="6" class="usb"/>')
        o.append(T(TX(xf) + (-3 if xf < 0 else 3), TY(-D["box_d"]/2) - 10, lab, "fn", "end" if xf < 0 else "start"))
    o.append(f'<circle cx="{TX(16)}" cy="{TY(-D["box_d"]/2) - 1}" r="4" class="part"/>')
    o.append(T(TX(19), TY(-D["box_d"]/2) - 22, "button", "fn", "middle"))
    o.append(T(TX(D["box_w"]/2 - D["led_off"]), TY(D["box_d"]/2) + 12, "beacon", "fn", "middle"))
    o.append(T(TX(-D["span"]/2 + 2), TY(D["panel_d"]/2) + 14, "wing A", "fn")); o.append(T(TX(D["span"]/2 - 2), TY(D["panel_d"]/2) + 14, "wing B", "fn", "end"))
    o.append(dim_h(TX(-D["span"]/2), TX(D["span"]/2), TY(D["disc_d"]/2) + 22, f"{D['span']:.0f}", False))
    o.append(dim_v(TX(D["span"]/2) + 16, TY(-D["panel_d"]/2), TY(D["panel_d"]/2), f"{D['panel_d']:.0f}", True))
    o.append(dim_v(TX(-D["span"]/2) - 16, TY(-D["box_d"]/2), TY(D["box_d"]/2), f"{D['box_d']:.0f}", False))

    # ---------------------------------------------------------------- the back, 3 px per mm (right column, lower)
    s4 = 3.0
    kx0, ky0 = 1000, 556                              # outer bottom-left of the back face in this drawing
    o.append(T(940, 476, "The back, seen from behind, 3 px per mm", "h2"))
    o.append(f'<rect x="{kx0}" y="{ky0 - D["box_h"]*s4}" width="{D["box_w"]*s4}" height="{D["box_h"]*s4}" rx="2" class="shell"/>')
    o.append(f'<rect x="{kx0 + D["wall"]*s4}" y="{ky0 - (D["box_h"] - D["wall"])*s4}" width="{(D["box_w"] - 2*D["wall"])*s4}" height="{(D["box_h"] - 2*D["wall"])*s4}" class="plate"/>')
    zs = D["wall"] + 1.6 + D["usb_h"]/2               # the ports sit on boards that lie on the floor: 5.3 mm up
    for xf, lab in ((-10.0, "charge"), (9.5, "flash")):   # x from the front; seen from behind the sign flips
        ux = kx0 + (D["box_w"]/2 - xf - D["usb_w"]/2) * s4
        o.append(f'<rect x="{ux}" y="{ky0 - (zs + D["usb_h"]/2)*s4}" width="{D["usb_w"]*s4}" height="{D["usb_h"]*s4}" rx="3" class="cavity"/>')
        o.append(T(ux + D["usb_w"]*s4/2, ky0 + 16, lab, "fn", "middle"))
    bxb = kx0 + (D["box_w"]/2 - 16) * s4
    o.append(f'<circle cx="{bxb}" cy="{ky0 - 15*s4}" r="{3.25*s4}" class="cavity"/>')
    o.append(f'<circle cx="{bxb}" cy="{ky0 - 15*s4}" r="{2.6*s4}" class="part"/>')
    o.append(T(bxb, ky0 + 30, "button, 6.5 hole", "fn", "middle"))
    o.append(dim_v(kx0 + D["box_w"]*s4 + 14, ky0 - D["box_h"]*s4, ky0, f"{D['box_h']:.0f}", True))
    for k, line in enumerate((f"lid {D['box_w'] - 2*D['wall']:.0f} × {D['box_h'] - 2*D['wall']:.0f} × {D['lid']:.1f}, a press fit;", f"two 9 × 3.4 slots, {zs:.1f} mm up:",
                              "charge (right) and flash (left);", "button 15 mm up, 8 in from the left;", "pull the lid to swap the cell")):
        o.append(T(1192, ky0 - 64 + k * 14, line, "fn"))

    # ---------------------------------------------------------------- key numbers, bottom left
    kx, ky = 40, 640
    o.append(T(kx, ky, "Key numbers", "h2"))
    rows = [
        (f"{D['span']:.0f} × {D['panel_d']:.0f} × {D['height']:.0f} mm", "overall, wings to the top of the LED"),
        (f"{D['box_w']:.0f} × {D['box_d']:.0f} × {D['box_h']:.0f} mm", "the bus: printed black, 2 mm walls"),
        (f"2 × {D['panel']:.0f} × {D['panel_d']:.0f} wings, 5 V, series", "12.2 V in sun, 7 to 8 V in a room"),
        (f"{D['top_g'] + D['base_g']:.0f} g, {D['disc_g']} in the base", f"centre of mass {D['com']:.0f} mm up; tips at {D['tip_deg']}°"),
        ("3 rods, 3 CA sockets", "post and two booms; no frame joints"),
        ("7 wires, 2 resistors, 1 diode", "30 AWG; wings and beacon have their own leads"),
        (f"{E['sleep']:.2f} / {E['blink']:.2f} / {E['glow']:.1f} mA", "asleep / beacon / glow, from the cell"),
        (f"{E['blink_days']:.0f} / {E['glow_days']:.0f} / {E['lamp_days']:.1f} days", "beacon / glow / lamp, no light at all"),
        (f"USB-C 500 mA, {E['usb_h']:.1f} h", "the fallback charge, through the lid"),
    ]
    for i, (num, what) in enumerate(rows):
        o.append(T(kx, ky + 22 + i * 19, num, "dimlab"))
        o.append(T(kx + 262, ky + 22 + i * 19, what, "fn"))

    # ---------------------------------------------------------------- what the wings do, bottom middle
    ex, ey = 560, 640
    o.append(T(ex, ey, "What the wings deliver (listing figures, scaled by light)", "h2"))
    o.append(T(ex, ey + 20, "where", "lab")); o.append(T(ex + 230, ey + 20, "lux", "lab", "end")); o.append(T(ex + 300, ey + 20, "pair, mA", "lab", "end")); o.append(T(ex + 390, ey + 20, "stored a day", "lab", "end"))
    for i, (where, lux, dl, note) in enumerate(LIGHT):
        yy = ey + 40 + i * 19
        pm, nm = panel_ma(lux, dl), net_ma(lux, dl)
        o.append(T(ex, yy, where, "fn")); o.append(T(ex + 230, yy, f"{lux:,}", "mono", "end")); o.append(T(ex + 300, yy, f"{pm:.1f}", "mono", "end"))
        o.append(T(ex + 390, yy, f"{nm * 6:.0f} mAh" if lux < 100000 else f"{nm:.0f} mAh / h", "mono", "end"))
    o.append(T(ex, ey + 148, f"The charger spends {E['bq_in']:.2f} mA of input on itself and gives 6 h a day:", "fn"))
    o.append(T(ex, ey + 162, "'stored' is six hours of what is left. Room light stores nothing.", "fn"))
    o.append(T(ex, ey + 176, f"Beacon mode needs {E['blink'] * 24:.0f} mAh a day, glow {E['glow'] * 24:.0f}: a bright window carries the beacon,", "fn"))
    o.append(T(ex, ey + 190, "the amber pool lives on direct sun or the cable; a USB top-up now and then.", "fn"))

    # ---------------------------------------------------------------- detail: the base, bottom right
    bx, by = 990, 640
    o.append(T(bx, by, "The base, 3 px per mm", "h2"))
    bcx, bcy = bx + 118, by + 120
    o.append(f'<rect x="{bcx - D["disc_d"]/2*s4}" y="{bcy}" width="{D["disc_d"]*s4}" height="{D["disc_t"]*s4}" class="plate"/>')
    o.append(f'<rect x="{bcx - D["hub_d"]/2*s4}" y="{bcy - D["hub_h"]*s4}" width="{D["hub_d"]*s4}" height="{D["hub_h"]*s4}" rx="2" class="dark"/>')
    o.append(f'<rect x="{bcx - 0.8*s4}" y="{bcy - D["hub_h"]*s4}" width="{1.6*s4}" height="{D["hub_hole"]*s4}" class="cavity"/>')
    o.append(f'<line x1="{bcx}" y1="{bcy - (D["hub_h"] - D["hub_hole"])*s4 - 2}" x2="{bcx}" y2="{bcy - 90}" class="steel"/>')
    o.append(T(bcx + 26, bcy - 64, "brass 75 × 8, hollow; steel epoxied in", "fn"))
    o.append(T(bcx + 26, bcy - 50, "underneath, then the pad. 12 mm hub,", "fn"))
    o.append(T(bcx + 26, bcy - 36, "8 tall, glued on top: the post 7 deep", "fn"))
    o.append(dim_h(bcx - D["disc_d"]/2*s4, bcx + D["disc_d"]/2*s4, bcy + D["disc_t"]*s4 + 20, f"{D['disc_d']:.0f} × {D['disc_t']:.0f}", False))

    # scale bar and footer
    o.append(f'<path d="M40,836 L{40 + 50*s},836 M40,830 L40,842 M{40 + 50*s},830 L{40 + 50*s},842" class="thin"/>')
    o.append(T(40 + 25 * s, 828, "50 mm in the front view", "fn", "middle"))
    o.append(T(W - 20, 848, f"Paper design {TODAY}, revised twice that morning, approved {APPROVED} and revised for the 16340 cell. The box is an envelope round the real holder and boards: bench-check before printing. Nothing built.", "sub", "end"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Desk satellite form sheet">{SHEET_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- sheet 2: the wiring
def wiring_sheet():
    rt = Router()
    w = rt.wire
    o = [T(20, 30, "Desk satellite: every connection on one sheet", "h1"),
         T(20, 48, "A dot is a joint. A line that hops over another does not touch it. Thick = 30 AWG wire you solder. Thin = a lead or cable that comes with the part (the wings' and the beacon's leads are thin lines here). Pins are grouped by job, not by position on the board.", "sub")]

    # wings, left
    PX, PW, PH = 60, 240, 105
    o.append(block(PX, 95, PW, PH, "Solar wing A, left", "80 × 45 poly · 5 V 90 mA · 6.1 V open", ty=22))
    o.append(pin(rt, PX + PW, 150, "+", "R", "SOL+")); o.append(pin(rt, PX + PW, 185, "−", "R", "SOLMID"))
    o.append(block(PX, 235, PW, 105, "Solar wing B, right", "the same panel; the pair in series", ty=22))
    o.append(pin(rt, PX + PW, 290, "+", "R", "SOLMID")); o.append(pin(rt, PX + PW, 325, "−", "R", "GND"))
    o.append(T(PX + 16, 372, "150 mm leads fitted; they run under each", "fn")); o.append(T(PX + 16, 388, "panel along its boom, into the box", "fn"))
    o.append(T(PX + 16, 410, "12.2 V in sun, 7 to 8 V in a room: always", "fn")); o.append(T(PX + 16, 426, "above the 4.8 V the charger needs", "fn"))

    # charger, centre left
    CX, CY, CW, CH = 400, 95, 300, 330
    o.append(block(CX, CY, CW, CH, "Solar charger board", "bq25185 + 5 V boost · jumper cut: 500 mA", ty=20))
    o.append(pin(rt, CX, 150, "VIN", "L", "SOL+", "5 to 18 V in", CX + 56))
    o.append(pin(rt, CX, 325, "G", "L", "GND", "ground pad", CX + 56))
    o.append(pin(rt, CX, 370, "EN", "L", "GND", "boost enable, tied low", CX + 56))
    o.append(pin(rt, CX + CW, 175, "BAT", "R", "VBAT", "the cell", CX + CW - 56))
    o.append(pin(rt, CX + CW, 215, "−", "R", "GND", "screw terminal", CX + CW - 56))
    o.append(pin(rt, 620, CY + CH, "JST +", "B", "CELL+")); o.append(pin(rt, 650, CY + CH, "JST −", "B", "CELL-"))
    o.append(f'<rect x="{CX + 14}" y="{CY + CH - 30}" width="40" height="16" rx="3" class="usb"/>'); o.append(T(CX + 34, CY + CH - 18, "USB-C", "fn", "middle"))
    o.append(T(CX + 150, 255, "not used: VU, D+, D−, 5V, + terminal", "fn", "middle"))
    o.append(T(CX + 150, 271, "the boost stays off; its green LED stays dark", "fn", "middle"))
    o.append(T(CX + 150, 293, "holds a weak input at cell + 0.33 V and keeps", "fn", "middle")); o.append(T(CX + 150, 307, "charging; 6 h timer, reset by a dark night", "fn", "middle"))
    o.append(w([(PX + PW, 150), (CX, 150)], "thin", "SOL+")); o.append(T(350, 142, "A+ → VIN", "lab", "middle"))
    o.append(w([(PX + PW, 185), (330, 185), (330, 290), (PX + PW, 290)], "thin", "SOLMID")); o.append(T(342, 242, "A− → B+", "lab"))
    o.append(w([(PX + PW, 325), (CX, 325)], "thin", "GND")); o.append(T(350, 317, "B− → G", "lab", "middle"))
    o.append(w([(CX, 370), (362, 370), (362, 325)], "rod", "GND")); o.append(dot(362, 325)); o.append(T(372, 352, "EN → G: 37 µA", "fn"))

    # controller, centre right
    EX, EY, EW, EH = 820, 95, 260, 330
    o.append(block(EX, EY, EW, EH, "ESP32-C3 SuperMini", "fed at its 5V pin · red power LED removed", ty=20))
    o.append(pin(rt, EX, 175, "5V", "L", "V5", "3.5 to 4.0 V in", EX + 46))
    o.append(pin(rt, EX, 215, "GND", "L", "GND", "", EX + 46))
    o.append(pin(rt, EX + EW, 175, "GPIO0", "R", "LED", "beacon", EX + EW - 66))
    o.append(pin(rt, EX + EW, 255, "GPIO1", "R", "LAMP", "downlight", EX + EW - 66))
    o.append(pin(rt, EX + EW, 320, "GPIO10", "R", "BTN", "mode button", EX + EW - 74))
    o.append(T(EX + 14, 280, "not wired: 3V3 · GPIO2, 8, 9 (straps)", "fn"))
    o.append(T(EX + 14, 294, "GPIO3 to 7, 20, 21 free · Wi-Fi off", "fn"))
    o.append(T(EX + 14, 308, "light sleep 0.13 mA, wakes in 1 ms", "fn"))
    o.append(f'<rect x="{EX + 14}" y="{EY + EH - 30}" width="40" height="16" rx="3" class="usb"/>'); o.append(T(EX + 34, EY + EH - 18, "USB-C", "fn", "middle"))
    o.append(T(EX + 62, EY + EH - 18, "flashing only, behind the lid; safe with the cell in", "fn"))
    o.append(w([(CX + CW, 175), (738, 175)], "rod", "VBAT")); o.append(diode_h(738, 782, 175)); o.append(w([(782, 175), (EX, 175)], "rod", "V5"))
    rt.add(738, 175, 782, 175, "V5")
    o.append(T(760, 156, "SS14, band toward the controller", "lab", "middle"))
    o.append(w([(CX + CW, 215), (780, 215), (EX, 215)], "rod", "GND")); o.append(T(760, 237, "one ground", "fn", "middle"))

    # the beacon, top right
    MX, MY, MW, MH = 1140, 95, 190, 180
    o.append(block(MX, MY, MW, MH, "Beacon LED", "0805 chip, pre-wired · on the top corner", ty=20))
    o.append(pin(rt, MX, 175, "+ lead", "L", "LED")); o.append(pin(rt, MX + 175, MY + MH, "− lead", "B", "GND"))
    lx0 = MX + 150
    o.append(f'<rect x="{lx0 - 24}" y="{MY + 98}" width="48" height="12" class="shell"/>')          # a piece of the top wall
    o.append(f'<rect x="{lx0 - 14}" y="{MY + 89}" width="12" height="9" rx="2" class="lamp"/>')       # the chip, flat on it
    o.append(f'<circle cx="{lx0 - 8}" cy="{MY + 93}" r="16" class="glow"/>')
    o.append(f'<path d="M{lx0 - 2},{MY + 92} L{lx0 + 8},{MY + 92} L{lx0 + 8},{MY + 150} M{lx0 - 2},{MY + 95} L{lx0 + 12},{MY + 95} L{lx0 + 12},{MY + 140}" class="thin"/>')
    o.append(T(lx0 - 2, MY + 72, "1.1 mm of chip", "fn", "middle"))
    o.append(T(MX + 14, MY + 118, "glued flat on the top", "fn")); o.append(T(MX + 14, MY + 132, "front corner; its own", "fn")); o.append(T(MX + 14, MY + 146, "0.1 mm leads drop", "fn")); o.append(T(MX + 14, MY + 160, "through a pinhole", "fn"))
    o.append(w([(EX + EW, 175), (1092, 175)], "rod", "LED")); o.append(zigzag_h(rt, 1092, 1128, 175, "LED")); o.append(w([(1128, 175), (MX, 175)], "rod", "LED"))
    o.append(T(1110, 156, "100 Ω", "lab", "middle"))
    # the downlight, below the beacon
    DX, DY, DW, DH = 1140, 305, 140, 120
    o.append(block(DX, DY, DW, DH, "Downlight", "38 mm filament, 3 V, 2200 K", ty=20))
    o.append(pin(rt, DX, 360, "+", "L", "LAMP")); o.append(pin(rt, DX, 400, "−", "L", "GND"))
    o.append(T(DX + 30, DY + 72, "taped under the floor,", "fn")); o.append(T(DX + 30, DY + 86, "glowing down the post", "fn")); o.append(T(DX + 30, DY + 100, "onto the brass; 12 mA", "fn")); o.append(T(DX + 30, DY + 114, "full, PWM dims it", "fn"))
    o.append(w([(EX + EW, 255), (1104, 255), (1104, 360)], "rod", "LAMP")); o.append(zigzag_h(rt, 1104, 1136, 360, "LAMP")); o.append(w([(1136, 360), (DX, 360)], "rod", "LAMP"))
    o.append(T(1108, 341, "68 Ω", "lab", "middle"))
    # one return lane for the three grounds on this side, into the controller's GND pin
    o.append(w([(MX + 175, MY + MH), (MX + 175, 580), (780, 580), (780, 215)], "rod", "GND")); o.append(dot(780, 215))
    o.append(w([(DX, 400), (1125, 400), (1125, 580)], "rod", "GND")); o.append(dot(1125, 580))
    o.append(T(1040, 598, "the three returns (beacon, downlight, button) share one lane into the controller's GND pin", "fn", "middle"))

    # mode button, below the controller
    BX, BY = 870, 470
    o.append(block(BX, BY, 130, 60, "Mode button", "6 mm tactile, in the lid", ty=24))
    o.append(pin(rt, 900, BY, "", "T", "BTN")); o.append(pin(rt, 930, BY + 60, "", "B", "GND"))
    o.append(T(890, BY - 6, "leg 1", "fn", "end")); o.append(T(940, BY + 76, "leg 2", "fn"))
    o.append(w([(EX + EW, 320), (1088, 320), (1088, 450), (900, 450), (900, BY)], "rod", "BTN")); o.append(T(1000, 442, "GPIO10 → button", "lab", "middle"))
    o.append(w([(930, BY + 60), (930, 580)], "rod", "GND")); o.append(dot(930, 580))
    o.append(T(1010, 494, "off → beacon → glow → off", "fn")); o.append(T(1010, 510, "long press: pool full · pull-up inside", "fn"))

    # the cell and the wall adapter, below the charger
    o.append(block(590, 470, 170, 70, "16340 cell in its holder", "Nitecore 950 mAh · protected", ty=26))
    o.append(pin(rt, 620, 470, "", "T", "CELL+")); o.append(pin(rt, 650, 470, "", "T", "CELL-"))
    o.append(T(612, 462, "+", "pin", "end")); o.append(T(658, 462, "−", "pin"))
    o.append(w([(620, CY + CH), (620, 470)], "thin", "CELL+")); o.append(w([(650, CY + CH), (650, 470)], "thin", "CELL-"))
    o.append(T(606, 452, "holder leads → pigtail, plugged in", "fn", "end"))
    o.append(block(400, 470, 160, 60, "USB-C wall adapter", "2 A, owned: the fallback"))
    o.append(w([(434, 470), (434, CY + CH - 14)], "thin", "USB"))
    o.append(T(480, 548, f"500 mA into the cell, full in about {E['usb_h']:.1f} h", "fn", "middle"))

    # the budget, along the bottom
    NY = 625
    o.append(T(20, NY - 10, "The budget: from the cell (mA) and from the wings (mA at the charger's input, six hours a day at most)", "h2"))
    cols = [("asleep", E["sleep"], "controller in light sleep, regulator, the EN pull-up, the charger's 4 µA"),
            ("beacon", E["blink"], f"the chip, {E['led_on']:.0f} mA for 100 ms every 2 s · {E['blink_days']:.0f} days on the cell in the dark · the resting mode"),
            ("glow", E["glow"], f"beacon blinking + the pool dimmed to {E['pool_dim']:.0f} mA · {E['glow_days']:.0f} days in the dark · evenings and sunny sills"),
            ("lamp", E["lamp"], f"pool flat out at {E['pool_full']:.0f} mA, beacon steady · {E['lamp_days']:.1f} days · a long press; plug in for it")]
    for i, (name, ma, note) in enumerate(cols):
        yy = NY + 14 + i * 19
        o.append(T(40, yy, name, "lab")); o.append(T(260, yy, f"{ma:.2f} mA", "mono", "end")); o.append(T(350, yy, f"{ma * 24:.0f} mAh/day", "mono", "end")); o.append(T(366, yy, note, "fn"))
    o.append(T(40, NY + 100, f"Wings: {panel_ma(500, False):.1f} mA under room light, nothing stored (the charger eats {E['bq_in']:.2f} mA itself) · {panel_ma(1000):.1f} to {panel_ma(3000):.1f} mA beside a window, {net_ma(1000) * 6:.0f} to {net_ma(3000) * 6:.0f} mAh a day", "fn"))
    o.append(T(40, NY + 116, f"· {panel_ma(10000):.0f} mA on an overcast sill, {net_ma(10000) * 6:.0f} mAh a day · 90 mA in full sun, the listing's figure, scaled by lux; the first week on the sill, with the meter on the BAT pad each evening, is the measurement.", "fn"))
    o.append(T(40, NY + 140, f"Mods, both before wiring: cut the charger's charge-rate jumper (1 A → 500 mA, half the cell's rating an hour); lift the SuperMini's red power LED, or its resistor, with tweezers (about {E['power_led']:.0f} mA all day: beacon mode would last {E['blink_days_pl']:.0f} days, not {E['blink_days']:.0f}).", "fn"))
    o.append(T(40, NY + 156, "Never: the cell on anything but the charger's JST socket · a USB cable in the controller without the diode in place · the wings on the charger's USB side · the filament without its resistor · an iron within 10 cm of the cell.", "fn"))

    bad, crossings = rt.check()
    for b in bad:
        print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    o.append(T(20, 848, f"Paper design {TODAY}, not built. {crossings} crossing(s) on this sheet. Sources: TI bq25185 datasheet SLUSF65B, the Adafruit product page, guide, schematic and fab print, the SuperMini schematic notes, the three listings.", "sub"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Desk satellite wiring sheet">{SHEET_CSS}{"".join(o)}</svg>'


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
<p>A small satellite on a post. Two {a("solar panels", "panel")}, 80 × 45 mm, are its wings, a matte black printed box is its body, and a tiny warm-white {a("LED chip", "led")} is glued on its top front corner, no legs showing: on, or blinking once every two seconds, like a satellite you can see pass over. Under the body the hologram's amber {a("LED filament", "filament")} glows down the post onto a brass base, the family's metal. Inside the box the owned {a("charger board", "charger")} tops up a {a("Nitecore 16340 cell", "cell")} in its {a("holder", "holder")} from the wings, with a USB-C port through the back as the fallback, and an {a("ESP32-C3 SuperMini", "controller")} sleeps between blinks. One 1.5 mm stainless post carries it over a solid {a("brass base", "disc")}, 75 mm across.</p>
<p>The reference is Huy Vector's <a href="{L['reference']}" target="_blank" rel="noopener">Desk Satellite</a>: a copper-wire cube with an ESP32-C3 clock and a 0.96-inch screen inside, two solar wings, a dish, a charging module and a separate solar controller, on a brass tube over a bamboo coaster. Ours keeps the silhouette and the solar wings and drops the clock: the builder's brief is panels, a cell they top up, USB as the fallback, and a small 3000 K light at the tip that is on or blinks.</p>
<p><strong>This page is step 1 of the house rule: the final build first, approved by the builder on 2026-11-03 as drawn, and revised the same day at their word for the Nitecore 16340 cell they had bought, in place of the 500 mAh pouch.</strong> One form sheet, one wiring sheet, every part and every pin. The science behind it (what a solar cell does in room light, how the charger follows a weak wing, the beacon's eye, the post as a column) is step 2, <a href="https://claude.ai/artifact/3pQpnMr1HYgj5bbNUL3nMG" target="_blank" rel="noopener">Desk Satellite Physics</a>. Every part is bought or in a drawer; nothing printed, cut or soldered yet.</p>
"""


def decisions_html():
    o = ["<h2>The decisions</h2>"]
    for head, text in DECISIONS:
        o.append(f"<h3>{esc(head)}</h3><p>{md_inline(text)}</p>")
    return "".join(o)


def dims_rows():
    return [("span", "wing tip to wing tip"), ("panel", "each wing, along the boom"), ("panel_d", "each wing, front to back"), ("panel_t", "wing thickness"), ("box_w", "bus width (along the wings)"), ("box_d", "bus depth"), ("box_h", "bus height"),
            ("wall", "bus wall"), ("lid", "back lid"), ("yoke_l", "boom boss on each side wall"), ("gap", "air between boss and wing"), ("boom_cut", "each boom, cut length"),
            ("post_free", "post, base to boss"), ("post_cut", "post, cut length"), ("boss_h", "post boss under the bus"), ("hub_h", "hub on the base"), ("hub_d", "hub diameter"),
            ("disc_d", "brass base, diameter"), ("disc_t", "brass base, height"), ("cell_l", "cell, length (a 16340)"), ("cell_d", "cell, diameter"), ("holder_l", "holder, along the front wall"), ("holder_w", "holder, front to back"), ("led_off", "beacon chip centre, in from the front and the right wall"), ("hole_x", "pinhole for its leads, in from the right wall"), ("led_h", "beacon chip above the top face"), ("lamp_len", "filament under the floor, across"), ("lamp_y", "filament ahead of the post (negative = toward the front)"),
            ("z_wing", "wing plane above the desk"), ("z_top", "top of the bus above the desk"), ("height", "overall height to the top of the LED")]


def dims_html():
    o = ['<h2>Dimensions</h2><div class="tw"><table><tr><th>What</th><th>mm</th></tr>']
    o += [f'<tr><td>{esc(lab)}</td><td class="m">{D[k]:.1f}</td></tr>' for k, lab in dims_rows()]
    o.append("</table></div>")
    o.append(f"<p>Masses: wings 2 × {D['panel_g']:.0f} g, box and lid about {D['box_g']:.0f}, cell and holder {D['cell_g'] + D['holder_g']:.0f}, boards {D['charger_g'] + D['c3_g']:.0f}, rods {rod15 * (D['post_cut'] + 2 * D['boom_cut']):.1f}: about {D['top_g']} g above the base, {D['disc_g']} g of brass. Centre of mass {D['com']:.0f} mm up, so it tips at about {D['tip_deg']}°.</p>")
    return "".join(o)


def pins_html():
    o = ['<h2>Pin map, ESP32-C3 SuperMini</h2>',
         '<p>Five pins used of sixteen. The button keeps the family\'s GPIO10 and the beacon the hologram\'s GPIO0, the filament takes GPIO1; no strapping pin is wired, so the only resistors are the two lights\'.</p>',
         '<div class="tw"><table><tr><th>Pin</th><th>Job</th><th>Goes to</th></tr>']
    for p, job, to, net in PINS:
        o.append(f'<tr><td class="m">{esc(p)}</td><td>{esc(job)}</td><td>{esc(to)}</td></tr>')
    o.append("</table></div>")
    o.append('<h3>Charger board pads</h3><p>Used: <code>VIN</code> (the wings), <code>G</code> (wing B and EN), <code>BAT</code> (to the diode), <code>EN</code> (to G), the JST-PH socket (the cell\'s pigtail), the USB-C port (the fallback) and the <code>−</code> screw terminal of the unused 5 V output as the controller\'s ground. Not used: <code>VU</code>, <code>D+</code>, <code>D−</code>, <code>5V</code>, the <code>+</code> terminal. The charge-rate jumper on the back is cut.</p>')
    return "".join(o)


def nets_html():
    o = ['<h2>Every wire, and why</h2>', '<div class="tw"><table><tr><th>Net</th><th>From</th><th>To</th><th>Wire</th><th>Why</th></tr>']
    for net, fr, to, wire, why in NETS:
        o.append(f'<tr><td class="m">{esc(net)}</td><td>{esc(fr)}</td><td>{esc(to)}</td><td>{esc(wire)}</td><td>{md_inline(why)}</td></tr>')
    o.append("</table></div>")
    return "".join(o)


def budget_html():
    o = ['<h2>The budget, honestly</h2>',
         f'<p>From the cell: the controller in light sleep ({E["c3_sleep"]:.2f} mA), its regulator (about {E["ldo"]:.2f}), the EN pull-up ({E["en_pullup"]:.3f}) and the charger ({E["bq_batt"]:.3f}) make {E["sleep"]:.2f} mA asleep. The beacon adds {E["led_on"]:.0f} mA for 5 % of the time blinking: {E["blink"]:.2f} mA, {E["blink"] * 24:.0f} mAh a day, {E["blink_days"]:.0f} days on the {E["cell_mah"]} mAh cell ({E["cell_usable"]} usable) with no light at all. '
         f'The glow mode adds the amber pool at {E["pool_dim"]:.0f} mA: {E["glow"]:.1f} mA, {E["glow"] * 24:.0f} mAh a day, {E["glow_days"]:.0f} days in the dark. The lamp mode (pool flat out at {E["pool_full"]:.0f} mA, beacon steady) is {E["lamp"]:.1f} mA and {E["lamp_days"]:.1f} days: an evening setting, not a resting one. The SuperMini\'s red power LED, if left on, costs about {E["power_led"]:.0f} mA and cuts the beacon mode to {E["blink_days_pl"]:.0f} days.</p>',
         f'<p>From the wings: the charger spends {E["bq_in"]:.2f} mA of input on itself while charging and gives six hours a day before its timer stops it until dark, so what the table calls stored is six hours of what the pair delivers beyond that. The figures are the listing\'s {E["isc"]:.0f} mA taken as full sun (1 000 W/m²; 36 cm² of poly cells can give little more), scaled by lux, with room LED light counted at 0.65 of daylight per lux. They are estimates until the first week on the sill is read off the BAT pad each evening.</p>',
         '<div class="tw"><table><tr><th>Where</th><th>lux</th><th>pair, mA</th><th>stored a day</th><th>Which means</th></tr>']
    for where, lux, dl, note in LIGHT:
        pm, nm = panel_ma(lux, dl), net_ma(lux, dl)
        stored = f"{nm * 6:.0f} mAh" if lux < 100000 else f"{nm:.0f} mAh per hour"
        o.append(f'<tr><td>{esc(where)}</td><td class="m">{lux:,}</td><td class="m">{pm:.1f}</td><td class="m">{stored}</td><td>{esc(note)}</td></tr>')
    o.append("</table></div>")
    return "".join(o)


def parts_html():
    o = ['<h2>Parts</h2>', f'<p>Three things bought on Amazon on 2026-11-03, $32.83 with tax in three orders (all three picked up by 2026-11-06; logged in <code>docs/INVENTORY.md</code>), the steel disc now spare; one brass base to buy and weight with steel; three small parts to print; everything else is in a drawer already and is listed only so it is not bought twice. Each part is named by what it is, with the link on the word to the exact product.</p>']
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


def page_html(form_svg, wiring_svg):
    return "\n".join([
        '<title>Desk Satellite Build</title>',
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        f"<style>{STYLE}</style>",
        '<style>.wrap{max-width:1100px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} '
        'td,th{min-width:0} .tw table{min-width:720px}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Desk satellite &middot; step 1: the final build, approved 2026-11-03</div>',
        '<h1>A satellite on a post, blinking warm</h1>',
        f'<div class="sub">How it looks, how it is wired, every part and every pin. {D["span"]:.0f} × {D["panel_d"]:.0f} × {D["height"]:.0f} mm, about {D["top_g"] + D["base_g"]:.0f} g, no solder in the frame or on the wings.<br>Paper design of {TODAY}, revised the same morning at the builder\'s word: the beacon is a tiny LED chip glued on the corner of the bus, no legs, no mast; the hologram\'s amber filament glows down from under the body. Approved 2026-11-03 as drawn, then revised the same day at the builder\'s word for a Nitecore 16340 cell in its holder in place of the pouch (the bus grew round it); the science and engineering behind it is <a href="https://claude.ai/artifact/3pQpnMr1HYgj5bbNUL3nMG" target="_blank" rel="noopener">Desk Satellite Physics</a>. Nothing printed or built.</div></div>',
        intro_html(),
        f'<figure class="sheet">{form_svg}<figcaption><strong>Form sheet. Print landscape on Letter at Actual size; it is page 1 of the PDF.</strong> Front view with the amber pool, the beacon at the corner in section, side section through the bus, top view, the back with its lid, the base, the key numbers and what the wings deliver.</figcaption></figure>',
        decisions_html(),
        f'<figure class="sheet">{wiring_svg}<figcaption><strong>Wiring sheet, page 2 of the PDF.</strong> Wings on the left, charger and controller in the middle, the beacon and the downlight on the right, the cell, the adapter and the button below, the budget along the bottom. Thick lines are the seven 30 AWG wires, thin ones the leads that come with the wings, the cell holder and the beacon; dots are joints; a hop is a crossing that does not touch.</figcaption></figure>',
        dims_html(),
        pins_html(),
        nets_html(),
        budget_html(),
        parts_html(),
        firmware_html(),
        checks_html(),
        '<h2>Approved, then revised for the cell</h2><p>The builder approved the sheet as drawn on 2026-11-03, then chose a Nitecore 16340 cell they had bought over the 500 mAh pouch; the sheet, this record and the physics page were revised for it the same day (decision 4: the holder, the bigger bus, the two ports through the lid). Step 2, the science and engineering behind it, is published as <a href="https://claude.ai/artifact/3pQpnMr1HYgj5bbNUL3nMG" target="_blank" rel="noopener">Desk Satellite Physics</a>: what a silicon cell does at 500 lux and why two wings go in series, how a linear charger follows a weak wing and why it eats 0.75 mA, where the 6 h timer comes from, a day on the sill in milliamp-hours, the cell, one diode and the rail, light sleep against deep sleep, two load lines, why 2200 K looks like brass, a hundred milliseconds every two seconds, and the post as a column. All three Amazon lines were ordered that evening; the wings became 80 × 45 mm rectangles at the builder\'s word (decision 2), confirmed and bought the same night, arriving 2026-11-07. Next: the box is checked against the holder, the boards and the cell and printed, and the firmware is written.</p>',
        f'<hr><p class="sub">Built by <code>docs/pages/gen/build_page.py</code>, which also writes <code>docs/FINAL_BUILD.md</code> and the PDFs; the dimensions, pins, nets, budget and parts live in that script. The drawing-clearance check passes. Sources read {TODAY}: the reference page, the TI bq25185 datasheet (SLUSF65B), the Adafruit product page, Learn guide, schematic and fab print for the charger board, the Adafruit cell page, the SuperMini notes at sigmdel.ca, the Cyber Dawn and Pocket AI inventories and <code>cyber_clock_v2/docs/SOLAR_FEASIBILITY.md</code>, and the three Amazon listings. Nothing measured.</p>',
        '</div>'])


def final_build_md():
    o = ["# Desk satellite: the final build (step 1, approved 2026-11-03)", "",
         f"Paper design of {TODAY}, revised the same morning (the beacon moved from a mast to a chip glued on the corner, at the builder's word). A matte black printed bus on one 1.5 mm stainless post over a weighted brass base, two 80 × 45 mm polycrystalline solar wings in series with their leads fitted, Cyber Dawn's spare bq25185 charger board, a Nitecore 16340 cell in the owned holder, an ESP32-C3 SuperMini asleep between blinks, a pre-wired warm-white LED chip glued flat on the top front corner of the bus (on, or one blink every two seconds), and the hologram\'s spare 2200 K LED filament under the floor glowing down onto the brass. {D['span']:.0f} × {D['panel_d']:.0f} × {D['height']:.0f} mm, about {D['top_g'] + D['base_g']:.0f} g. **Nothing printed or built.**",
         "", "Generated by `pages/gen/build_page.py`, which also writes the page `pages/desk-satellite-build.html` and the PDFs in `pages/print/`; edit the script, not this file. The sheets are the authority for the drawing; this file carries the same decisions, dimensions, pin map, nets, budget and parts as text.", "",
         "## The reference", "",
         f"Huy Vector, [Desk Satellite]({L['reference']}), read {TODAY}. A copper-wire (1 and 0.7 mm) cube body with an ESP32-C3 and a 0.96\" 80 × 160 TFT showing an NTP clock, an SHT31 temperature and humidity sensor, a touch switch, a 4.2 V Type-C charging module plus a separate solar charge controller and a LiPo, mini solar cells or panels as the wings, a battery level indicator, a 3 mm brass tube post and a 6 cm bamboo coaster. Ours keeps the silhouette (a body on one post over a round base, two solar wings) and the builder's brief: mini solar panels, a cell they keep topped up, USB as the fallback, a small 3000 K LED at the tip that is on or blinks. The clock, display and sensor are dropped; the two charging boards become the one owned board that does both jobs.",
         "", "## The decisions", ""]
    for head, text in DECISIONS:
        o += [f"### {head}", "", text.replace("&lt;", "<").replace("&gt;", ">"), ""]
    o += ["## Dimensions", "", "| What | mm |", "| --- | ---: |"]
    o += [f"| {lab} | {D[k]:.1f} |" for k, lab in dims_rows()]
    o += ["", f"Masses: wings 2 × {D['panel_g']:.0f} g, box and lid about {D['box_g']:.0f} g, cell and holder {D['cell_g'] + D['holder_g']:.0f} g, boards {D['charger_g'] + D['c3_g']:.0f} g, rods {rod15 * (D['post_cut'] + 2 * D['boom_cut']):.1f} g: about {D['top_g']} g above the base and {D['disc_g']} g of brass. Centre of mass {D['com']:.0f} mm up; tips at about {D['tip_deg']}°.", "",
          "## Pin map, ESP32-C3 SuperMini", "", "| Pin | Job | Goes to |", "| --- | --- | --- |"]
    o += [f"| {p} | {job} | {to} |" for p, job, to, net in PINS]
    o += ["", "Charger board pads used: `VIN` (the wings), `G` (wing B and EN), `BAT` (to the diode), `EN` (to G), the JST-PH socket (the cell's pigtail), the USB-C port (the fallback), the `−` screw terminal (the controller's ground). Not used: `VU`, `D+`, `D−`, `5V`, the `+` terminal. The charge-rate jumper on the back is cut (500 mA).", ""]
    o += ["## Every wire, and why", "", "| Net | From | To | Wire | Why |", "| --- | --- | --- | --- | --- |"]
    o += [f"| {n} | {fr} | {to} | {wire} | {why} |" for n, fr, to, wire, why in NETS]
    o += ["", "## The budget, honestly", "",
          f"From the cell: {E['sleep']:.2f} mA asleep (controller in light sleep {E['c3_sleep']:.2f}, regulator about {E['ldo']:.2f}, EN pull-up {E['en_pullup']:.3f}, charger {E['bq_batt']:.3f}); beacon mode {E['blink']:.2f} mA ({E['led_on']:.0f} mA for 100 ms every 2 s), {E['blink'] * 24:.0f} mAh a day, {E['blink_days']:.0f} days on the {E['cell_mah']} mAh cell ({E['cell_usable']} usable) in the dark; glow mode (the pool at {E['pool_dim']:.0f} mA) {E['glow']:.1f} mA, {E['glow'] * 24:.0f} mAh a day, {E['glow_days']:.0f} days; lamp mode (pool flat out, beacon steady) {E['lamp']:.1f} mA, {E['lamp_days']:.1f} days. The SuperMini's red power LED, if left on, adds about {E['power_led']:.0f} mA and cuts the beacon mode to {E['blink_days_pl']:.0f} days.", "",
          f"From the wings: the charger spends {E['bq_in']:.2f} mA of input on itself while charging and stops after 6 h until dark; stored means six hours of what the pair gives beyond that. The listing's {E['isc']:.0f} mA taken as a full-sun figure, scaled by lux, room LED light at 0.65 of daylight per lux; estimates until the first week on the sill is read off the BAT pad.", "",
          "| Where | lux | pair, mA | stored a day | Which means |", "| --- | ---: | ---: | ---: | --- |"]
    for where, lux, dl, note in LIGHT:
        pm, nm = panel_ma(lux, dl), net_ma(lux, dl)
        stored = f"{nm * 6:.0f} mAh" if lux < 100000 else f"{nm:.0f} mAh per hour"
        o.append(f"| {where} | {lux:,} | {pm:.1f} | {stored} | {note} |")
    o += ["", "## Parts", "", "Three things bought on Amazon on 2026-11-03 ($32.83 with tax, three orders; all three picked up by 2026-11-06; see `INVENTORY.md`), the steel disc now spare; one brass base to buy and weight with steel; three small parts to print; the rest is owned and listed so it is not bought twice.", ""]
    for head, rows in PARTS:
        o += [f"### {head}", "", "| Qty | Part | Where | Price | Why, and what to check |", "| ---: | --- | --- | --- | --- |"]
        for qty, part, url, code, where, why in rows:
            name = f"[{part}]({url})" if url else part
            o.append(f"| {qty} | {name} | {code} | {where} | {why} |")
        o.append("")
    o += ["## What the firmware needs", ""] + [f"- {x}" for x in FIRMWARE] + ["", "## Before power, with the meter", ""] + [f"- {x}" for x in CHECKS]
    o += ["", "## Approved", "", "Approved by the builder on 2026-11-03 as drawn, then revised the same day at their word for a Nitecore 16340 cell in the owned holder in place of the 500 mAh pouch (decision 4: the bus grew round the holder, both USB-C ports through the lid). Step 2, the science and engineering behind the sheet, is `PHYSICS.md` and the page `pages/desk-satellite-physics.html` (the artifact Desk Satellite Physics). All three Amazon lines were ordered that evening; the wings became 80 × 45 mm rectangles at the builder's word (decision 2), confirmed and bought the same night, arriving 2026-11-07. Next: the box checked against the holder, the boards and the cell and printed, the firmware written.", ""]
    return "\n".join(o)


def print_pdf(html, form_svg, wiring_svg):
    PRINT.mkdir(exist_ok=True)
    sheet_css = ("<style>@page{size:letter landscape;margin:7mm} html,body{background:#fff;margin:0}"
                 ":root{--paper:#fff;--ink:#000;--ink-2:#333;--line:#ddd;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#f1f1f1;--warn:#000;--warn-soft:#eee}"
                 "svg{width:262mm;height:auto;display:block;margin:0 auto}</style>")
    page_css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
                "figure.sheet{display:none} h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} h3{font-size:9pt;margin-top:10pt} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
                ".tw table{min-width:0} td.m,th.m{white-space:normal} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid} ul.check{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        jobs = []
        for name, svg in (("form", form_svg), ("wiring", wiring_svg)):
            src = d / f"{name}.html"; pdf = d / f"{name}.pdf"
            src.write_text(f"<!doctype html><meta charset=utf-8><title>{name}</title>" + sheet_css + svg)
            jobs.append((src, pdf))
        p_html = d / "p.html"; p_pdf = d / "p.pdf"
        head, tail = html.rsplit("</style>", 1)   # after the last style block, so the print rules win
        p_html.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + page_css + tail)
        jobs.append((p_html, p_pdf))
        for src, pdf in jobs:
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "desk-satellite-build.pdf"
        subprocess.run(["pdfunite", str(d / "form.pdf"), str(d / "wiring.pdf"), str(p_pdf), str(out)], check=True)
        shutil.copyfile(d / "form.pdf", PRINT / "desk-satellite-form-sheet.pdf")
        shutil.copyfile(d / "wiring.pdf", PRINT / "desk-satellite-wiring-sheet.pdf")
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


def main():
    form_svg, wiring_svg = form_sheet(), wiring_sheet()
    html = page_html(form_svg, wiring_svg)
    OUT.write_text(html)
    (DOCS / "FINAL_BUILD.md").write_text(final_build_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "FINAL_BUILD.md")
    print(f"numbers: span {D['span']:.0f} height {D['height']:.1f} top {D['top_g']} g base {D['base_g']} g com {D['com']:.0f} tip {D['tip_deg']} deg; "
          f"sleep {E['sleep']:.3f} blink {E['blink']:.3f} steady {E['steady']:.3f} mA; blink {E['blink_days']:.0f} d steady {E['steady_days']:.0f} d")
    if "--pdf" in sys.argv:
        print_pdf(html, form_svg, wiring_svg)


if __name__ == "__main__":
    main()
