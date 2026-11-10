"""Crumb Rev C: the desk robot's open brass cage on its steel gear wheels, without the lidar. Step one, approved as drawn 2026-11-09.

    python3 crumb_build.py              writes ../crumb-build.html, ../../CRUMB_BUILD.md and ../../CRUMB_ORDER.md
    python3 crumb_build.py --png DIR    also renders every figure to PNG in DIR (headless Chrome) for checking

Rev B (asked for on 2026-11-07, approved 2026-11-08) gave Crumb Mochi's lidar and electrics. On 2026-11-09 the builder found the
lidar too big and asked for it off both desk robots so they stay small and cute: "remove the LiDAR for both projects". Rev C is
Rev B without it: the lidar, its posts on the top rails, its P-MOSFET switch and its serial line are gone, and the top comes down
from 95 mm to the cage's own rail at 60. The body is Crumb's (docs/DESIGN.md, 2026-10-31): a 1.0 mm brass-rod cage, 52 × 56 × 54,
on two Ø40 HSP 11184 steel gears, a 1.54" square colour screen as the face. The electrics are Rev B's less the lidar's branch: the
Adafruit bq25185 charger-boost still makes the 5 V rail, now for the XIAO (through a Schottky) and the amplifier only. From Rev C
the wiring sheet is Crumb's own (sheet() below, drawn with mochi_build's router and symbols; Mochi's sheet stays Mochi's record).
Every off-palette board wears a skin of 0.13 mm brass sheet, Kapton-lined, sprayed canvas white; nothing is card. The script refuses
to write if a part overlaps another or leaves the cage, if the pin audit fails, or if the sheet's lane check fails. Nothing has been built."""
from __future__ import annotations
import html, math, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import concepts as C
from concepts import View, desk, lidar_front, eyes_square, ROD, ROD_THIN, HID, BEAM, D2R
import mochi_build as M
from page import CSS as PAGE_CSS, L as LINKS, A

OUT_HTML = HERE.parent / "crumb-build.html"
OUT_MD = HERE.parent.parent / "CRUMB_BUILD.md"
OUT_ORDER = HERE.parent.parent / "CRUMB_ORDER.md"
esc = html.escape
tbl = M.tbl
PASSIVES = "https://www.amazon.com/dp/B0F4P352BB"     # the LuminologyPro resistor kit; the family's link for the bench's resistor and capacitor kits

# ============================================================================= geometry (mm; x right, y up from the desk, z forward)
CX0, CX1 = -26.0, 26.0                 # the cage's posts, rod centrelines; 52 wide
CZ0, CZ1 = -29.0, 27.0                 # back and face planes; 56 deep
CY0, CY1 = 6.0, 60.0                   # floor and top rails; 54 tall, 6 mm clearance
CR = 3.0
TOP = CY1                              # Rev C: the top rail is the top; Rev B's lidar stood to 95
IN = ((-25.5, 25.5), (6.5, 59.5), (-28.5, 27.0))      # the interior every part must keep to (rods are Ø1); the face parts may sit flush with the front plane
WR, WW, WX0 = 20.0, 9.0, 27.0          # gear: radius (the seller's Ø40), length over the boss, inner face 1 mm off the post
AY, AZ = 20.0, -7.0                    # the axle: at the gear's radius, 7 mm behind the cage's mid-depth (Crumb's choice; the cell sits ahead of it)
PLATE, BOSS_W, BOSS_D = 5.0, 4.0, 12.0 # toothed plate outboard, boss inboard: the listing's reading, to be calipered
OVERALL = 2 * (WX0 + WW)               # 72 over the gears
SKID_Z, SKID_R = 24.0, 2.5             # the brass dome at the nose
IPS_W, IPS_H, IPS_PIC = 33.0, 36.0, 27.7
FACE_Y = 7 + IPS_H / 2 + 0.15          # picture centre, y 25.15
LENS = (-4.0, 50.0)                    # the camera on the Sense board, on the brow
RNG_EYE = (13.3, 57.0, 25.0)           # the edge ranger's sensor: x, y, z
RNG_TILT = 40.0                        # its optical axis, degrees below level
RNG_CONE = 27.0
CELL_L, CELL_D, CELL_Z = 34.1, 16.6, 9.5   # the Nitecore NL169 lying along x in its holder
REV_B = dict(top=95, mass=250, ycom=35, roam_ma=1010)  # Rev B as approved on 2026-11-08, for the comparisons

PARTS_BOX = [  # (name, x, y, z, g, note); axis-aligned boxes, audited for overlap and for staying inside the cage
    ("motor L",       (-25, -1),      (15, 25),      (-13, -1),      10, "N20 end to end with its twin on the axle, shaft out through the left post line"),
    ("motor R",       (1, 25),        (15, 25),      (-13, -1),      10, "the other N20"),
    ("cell holder",   (-21.5, 21.5),  (6.5, 20.5),   (0.5, 18.5),    28, "across the floor just ahead of the motors, cell inside; ivory skin over its front and top"),
    ("charger-boost", (-9.5, 9.5),    (6.5, 11.6),   (-28.5, 0.5),   5,  "flat on the floor rails at the tail, USB-C out the back; the terminal block is not fitted, the 5 V pair solders to its pads"),
    ("charger-boost JST", (-9.5, 0),  (11.6, 14.1),  (-28.5, -20),   0,  "the JST BAT socket at the USB end, 6 mm tall"),
    ("motion sensor", (10, 25.5),     (6.5, 9.5),    (-28.5, -8),    2,  "GY-521 flat on the right tail floor, long side along z"),
    ("motor driver",  (-24, -14),     (33, 58),      (-28, -3),      8,  "standing on the left wall above the motor, terminals toward the rods"),
    ("amp",           (21, 24),       (33, 49),      (-26, -7),      3,  "standing on the right wall above the motor"),
    ("fuel gauge",    (21, 24),       (23, 48),      (0, 18),        3,  "standing on the right wall ahead of the motor"),
    ("speaker",       (-10, 10),      (40, 53),      (-28.5, -23.6), 5,  "the tail wall, firing backward between the rods"),
    ("toggle",        (12, 18),       (42, 50),      (-28.5, -19),   3,  "tail wall, right of the speaker, lever out the back"),
    ("1.54\" screen", (-16.5, 16.5),  (7, 43),       (24.5, 27),     12, "the lower face, vertical; header pins bent back into the chin; ivory bezel"),
    ("XIAO stack",    (-14.5, 6.5),   (36, 57),      (16.5, 24.5),   10, "standing behind the face, shifted 4 mm left; lens on the brow; ivory sleeve"),
    ("edge ranger",   (7, 19.7),      (45, 59),      (18, 26.8),     1,  "on the brow right of the lens, tilted 40° down, looking out past the nose"),
]
RODS = [  # (piece, qty, stock, length each mm, where)
    ("post", 4, "1.0 mm rod", 54, "the cage's four corners, y 6..60"),
    ("side rail", 4, "1.0 mm rod", 56, "floor and top, both sides, along z"),
    ("cross rail", 4, "1.0 mm rod", 52, "floor and top, face and tail, along x; r 3 corners bent, not mitred"),
    ("fender rail", 2, "1.0 mm rod", 56, "each side wall at y 14.5: the motors sit on them, the gauge and amp hang from the posts above"),
    ("motor cradle", 2, "1.0 mm rod", 40, "a shallow U from the fender rail round each motor's body, z −13 and −1"),
    ("brow sill", 1, "1.0 mm rod", 52, "across the face at y 45: the screen's top edge and the XIAO's sleeve rest on it"),
    ("skid post", 1, "1.0 mm rod", 6, "from the front floor rail at x 0 down to the dome"),
    ("skid dome", 1, "4 mm tube", 5, "a stub with a soldered dome, the third contact at z +24"),
    ("hub", 2, "5 over 4 mm tube", 9, "telescoped and soldered: the 4 mm bore takes the 3 mm D-shaft, the 5 mm fills the gear's bore; boss inboard"),
]
ROD10 = sum(q * l for p, q, s, l, w in RODS if s == "1.0 mm rod")
ROD10_G = ROD10 * math.pi * 0.5 ** 2 * 8.5e-3        # 1.0 mm brass at 8.5 g/cm³
CAGE_G = round(ROD10_G + 1.5)                          # with the skid dome and the solder; Crumb and Rev B carried 28 g here
MASS_OTHER = [  # (what, g, z, y)
    ("gears, pair, with hubs and ivory faces", 65, AZ, AY),
    ("brass cage, fender rails, cradles, sill, skid", CAGE_G, -1, 33),
    ("skins: brass sheet, Kapton, paint", 5, 0, 30),
    ("wire, capacitors, glue", 5, -5, 25),
]


def audit():
    boxes = [(n, (x, y, z)) for n, x, y, z, m, note in PARTS_BOX]
    bad = []
    for i, (n1, b1) in enumerate(boxes):
        for n2, b2 in boxes[i + 1:]:
            if M.overlap(b1, b2):
                bad.append(f"{n1} overlaps {n2}")
    for n, (x, y, z) in boxes:
        if not (IN[0][0] <= x[0] and x[1] <= IN[0][1] and IN[1][0] <= y[0] and y[1] <= IN[1][1] and IN[2][0] <= z[0] and z[1] <= IN[2][1]):
            bad.append(f"{n} pokes out of the cage")
    assert not bad, "; ".join(bad)
    m = sum(g for *_, g, note in PARTS_BOX) + sum(g for _, g, zz, yy in MASS_OTHER)
    sz = sum(g * (z[0] + z[1]) / 2 for n, x, y, z, g, note in PARTS_BOX) + sum(g * zz for _, g, zz, yy in MASS_OTHER)
    sy = sum(g * (y[0] + y[1]) / 2 for n, x, y, z, g, note in PARTS_BOX) + sum(g * yy for _, g, zz, yy in MASS_OTHER)
    return m, sz / m, sy / m


MASS, ZCOM, YCOM = audit()
D_AX = ZCOM - AZ                                  # the centre of mass sits this far ahead of the axle: on the skid
SKID_ARM = SKID_Z - AZ
SKID_LOAD = MASS * D_AX / SKID_ARM
TIP_FWD = 9.81 * (SKID_Z - ZCOM) / YCOM           # braking that would pitch it over the nose skid
TIP_BACK = 9.81 * D_AX / YCOM                      # forward acceleration that would lift the skid
RAMP = 0.4
V_LOAD, V_FREE = M.V_LOAD, M.V_FREE                # Ø40 at 45 / 62 rpm, cm/s
STOP_MM = (V_LOAD / 100) ** 2 / (2 * RAMP) * 1000 + (V_LOAD / 100) * 0.02 * 1000
# the edge ranger's rays: steep, centre, shallow (degrees below level), where they meet the desk
RAYS = {}
for name, a in (("steep", RNG_TILT + RNG_CONE / 2), ("centre", RNG_TILT), ("shallow", RNG_TILT - RNG_CONE / 2)):
    z_hit = RNG_EYE[2] + RNG_EYE[1] / math.tan(a * D2R)
    RAYS[name] = dict(deg=a, z=z_hit, ahead_face=z_hit - CZ1, ahead_skid=z_hit - SKID_Z, path=RNG_EYE[1] / math.sin(a * D2R))
EDGE_WARN = RAYS["steep"]["ahead_skid"]
# 2026-11-10: the edge against the wheels, and pushing (the builder's questions; the answers are in RISKS)
WHEEL_WARN = EDGE_WARN + (SKID_Z - AZ)                                # the steep ray's foot, ahead of the wheels' contact
FAR_WHEEL = RAYS["shallow"]["ahead_skid"] + (SKID_Z - AZ)             # the shallow ray's foot, ahead of the wheels
FOOT_HALF = RAYS["steep"]["path"] * math.tan(RNG_CONE / 2 * D2R)      # the cone's half-width where it first meets the desk
WHEEL_X = WX0 + WW / 2                                                # each gear's contact, off the midline
ANGLE_L = math.degrees(math.atan((WHEEL_WARN - STOP_MM) / (WHEEL_X + RNG_EYE[0] - FOOT_HALF)))   # approach off head-on still caught, left of the ranger
ANGLE_R = math.degrees(math.atan((WHEEL_WARN - STOP_MM) / max(WHEEL_X - RNG_EYE[0] - FOOT_HALF, 0.5)))   # and on the right, under it
STEP_MM = RAYS["shallow"]["ahead_skid"] - RAYS["steep"]["ahead_skid"]   # one step between looks: the foot's own length
CATCH_DEG = math.degrees(math.atan(CY0 / (CX1 + WHEEL_X)))            # the roll at which the floor rail meets the desk edge, one wheel over
PUSH_N = 0.35 * (MASS - SKID_LOAD) / 1000 * 9.81                      # traction on the wheels, steel teeth on wood
PUSH_G = PUSH_N / (0.5 * 9.81) * 1000                                 # what slides under it at a friction coefficient of 0.5
UNDER_MM = RNG_EYE[1] - (20 + CZ1 - RNG_EYE[2]) * math.tan(RAYS["steep"]["deg"] * D2R)   # the cone's underside 20 mm ahead of the face
assert RAYS["steep"]["path"] > 45, "the ranger's steepest ray must meet the desk beyond its 40 mm floor"

# ============================================================================= the electrics: Rev B's (Mochi's) less the lidar's branch
PINS = [  # (header, gpio, net, job)
    ("D0", 1, "CLK", "screen SPI clock, 40 MHz capable; 26 MHz used"),
    ("D1", 2, "DIN", "screen SPI data"),
    ("D2", 3, "free", "free since Rev C (it was the lidar's switch). A strapping pin only when the JTAG eFuse is burned, which it is not, so it may float through boot; the firmware holds it as an input with its pull-down"),
    ("D3", 4, "free", "free since Rev C (it was the lidar's serial in); the firmware holds it as an input with its pull-down"),
    ("D4", 5, "SDA", "I²C data: gauge 0x36, driver 0x5D, ranger 0x29, motion sensor 0x68"),
    ("D5", 6, "SCL", "I²C clock, 400 kHz"),
    ("D6", 43, "DC", "screen data/command. GPIO43 is UART0 TX: the ROM prints here at boot, harmless on a screen that is not initialised yet"),
    ("D7", 44, "BL", "screen backlight PWM. GPIO44 is UART0 RX, pulled up at boot: backlight on during boot, dimmed by the app after"),
    ("D8", 7, "BCLK", "I²S1 bit clock to the amp (SD-slot pin, J3 cut)"),
    ("D9", 8, "LRC", "I²S1 word clock to the amp"),
    ("D10", 9, "I2S_DIN", "I²S1 data to the amp"),
]


def audit_pins():
    every = [g for h, g, n, j in PINS]
    used = [g for h, g, n, j in PINS if n != "free"]
    assert len(every) == len(set(every)) == 11, "eleven header pins, eleven GPIOs"
    assert len(used) == 9, "nine in use, two free"
    for owner, gs in M.RESERVED.items():
        assert not (gs & set(every)), f"clash with the {owner}"


audit_pins()

NETS = [  # (net, from, to, wire, why)
    ("CELL+", "holder + lead (red)", "toggle, middle lug", "the holder's own 26 AWG lead", "Meter red to + before the cell goes in. The toggle breaks the cell's + lead; with it off and no USB lead in, nothing is live."),
    ("BAT+", "toggle, outer lug", "gauge JST A (+) · driver VIN terminal", "26 AWG; a JST-PH pigtail into the gauge", "The switched cell rail, 3.0–4.2 V. The gauge sits in the cell lead; the motors take the cell straight so stall current never loads the boost."),
    ("BAT+ (through the gauge)", "gauge JST B (+)", "charger-boost JST BAT (+)", "JST-PH pigtail, 26 AWG", "The gauge's two JST ports are a pass-through: cell in one, charger on the other. Polarity by meter, not by wire colour. The charger reaches the cell only through the toggle: charge with it on."),
    ("GND", "holder − lead (black), the star", "gauge JST A (−); charger-boost JST BAT (−) and 5 V − pad; driver GND terminal; XIAO GND pin; amp GND; the 220 µF; screen GND and CS; ranger GND; motion sensor GND", "26 AWG for the power returns, 30 AWG for the signal grounds", "One ground, one star at the holder. The brass is not a conductor: every rod keeps 2 mm from every net, Kapton on every board back that faces brass."),
    ("5V", "charger-boost 5 V + pad (no terminal block)", "Schottky anode (to the XIAO) · amp VIN · 220 µF +", "26 AWG", "The boosted rail, 5.0–5.2 V, 1 A, now for the XIAO and the amp only: 250 mA typical, 630 peak. Live whenever the toggle is on, with or without USB. Its EN pad stays open: the board's own pull-up keeps the boost on."),
    ("5V_XIAO", "Schottky cathode", "XIAO 5V pin", "26 AWG, the diode heat-shrunk in the lead", "The XIAO's 5V pin is its USB VBUS with no diode on the board. The Schottky lets the rail feed it and stops a PC's USB from feeding the rail, so you flash with the toggle off. About 0.3 V drop; the XIAO's buck is happy from 3.6 V."),
    ("3V3", "XIAO 3V3 pin", "screen VCC (10 µF + 100 nF); ranger VIN (100 nF); motion sensor VCC; gauge VIN; driver logic through the Qwiic chain", "30 AWG; the QT cables carry it along the chain", "The XIAO's buck gives 600–700 mA; the camera and Wi-Fi take up to 350 of it, the screen 31, the sensors 30, the chain's logic 10."),
    ("SDA / SCL", "XIAO D4 / D5", "gauge SDI / SCL pads → gauge QT → driver Qwiic 1 (100 mm QT cable) → driver Qwiic 2 → QT-to-header cable → ranger SDA/SCL and motion sensor SDA/SCL", "30 AWG to the gauge; QT cables; the header cable's wires", "One chain, four devices. Cut the driver's pull-up jumper; the gauge's and the ranger's 10 kΩ pairs and the motion sensor's 2.2 kΩ pair remain: about 1.5 kΩ, 2.2 mA per low, fine at 400 kHz."),
    ("CLK / DIN / DC / BL", "XIAO D0 / D1 / D6 / D7", "screen CLK / DIN / DC / BL", "the screen's own 8-wire PH2.0 lead", "Four pins for a 240 × 240 colour face. CS to GND (only SPI device). RST through 10 kΩ to 3V3 with 1 µF to GND: a power-on reset, then software resets."),
    ("BCLK / LRC / I2S_DIN", "XIAO D8 / D9 / D10", "amp BCLK / LRC / DIN", "30 AWG", "I²S1. SD stays on the module's pull-up (the chip sleeps when the clock stops), GAIN open (9 dB). Volume cap 50 on the 5 V rail, where Crumb's 65 was on the cell."),
    ("SPK+ / SPK−", "amp OUT+ / OUT−", "speaker", "the speaker's own leads", "A bridged output: neither lead is ground. Never clip a scope ground to either."),
    ("MA / MB", "driver A1-A2 / B1-B2", "motor L / motor R leads", "the motors' own leads, 60 mm", "Swap a pair if a wheel turns the wrong way. No GPIO goes to the motors."),
    ("motion sensor AD0", "GY-521 AD0", "GND", "a solder blob", "Address 0x68. INT stays open; bumps are read by polling at 100 Hz."),
    ("ranger XSHUT / GPIO1", "open", "", "", "The only ST ranger on the bus keeps its default 0x29; nothing to re-address."),
    ("D2, D3", "XIAO", "nothing", "none", "Free since Rev C: the lidar's switch and its serial line are gone. Inputs with pull-downs in firmware."),
]

XIAO_MA, AMP_MA, SCREEN_MA, SENS_MA, MOTOR_MA = (220, 330), (30, 300), (25, 31), (40, 60), (150, 700)   # (typical, peak) mA
RAIL5 = (XIAO_MA[0] + AMP_MA[0], XIAO_MA[1] + AMP_MA[1])
BUDGET = [  # (load, rail, typical mA, peak mA)
    ("XIAO with the camera streaming over Wi-Fi", "5 V, through the Schottky and its own buck", *XIAO_MA),
    ("Amp at cap 50 into the 8 Ω speaker", "5 V", *AMP_MA),
    ("Screen with the backlight at half", "3V3 (counted in the XIAO's draw)", *SCREEN_MA),
    ("Ranger, motion sensor, gauge, driver logic", "3V3 (counted in the XIAO's draw)", *SENS_MA),
    ("5 V rail, all of it", "boost, 1 A", *RAIL5),
    ("Two motors, running / one stalled", "cell rail", *MOTOR_MA),
]
CELL_MAH, V_CELL, BOOST_EFF, PARK_5V, CHARGE_H = 950, 3.7, 0.88, 135, 2.2   # PARK_5V: Wi-Fi on, camera off, face at half, amp idle
cell_ma = lambda rail5, motors: rail5 * 5.0 / BOOST_EFF / V_CELL + motors
I_ROAM, I_PARK = cell_ma(RAIL5[0], MOTOR_MA[0]), cell_ma(PARK_5V, 0)
RUN_ROAM, RUN_PARK = CELL_MAH / I_ROAM, CELL_MAH / I_PARK
assert abs(cell_ma(560, 150) - REV_B["roam_ma"]) < 5, "Rev B's 1.0 A roaming comes out of the same arithmetic"
POWER_LINES = [
    "one 950 mAh 16340 → toggle → fuel gauge → charger-boost; toggle off and no lead: nothing live",
    f"5 V rail: XIAO {XIAO_MA[0]} + amp {AMP_MA[0]} = {RAIL5[0]} mA typical, {RAIL5[1]} peak, of the boost's 1 A",
    f"cell rail: the motors, {MOTOR_MA[0]} mA running, {MOTOR_MA[1]} with one stalled, never through the boost",
    f"from the cell: {I_ROAM / 1000:.2f} A roaming, camera streaming → about {RUN_ROAM:.1f} h",
    f"{I_PARK / 1000:.2f} A parked, face on, camera off → about {RUN_PARK:.1f} h",
    f"USB-C, toggle on: 500 mA into the cell, full in about {CHARGE_H} h; it runs on the lead meanwhile",
]

CHECKS = [
    ("Holder and toggle", "Cell in, nothing else connected: meter DC V across the toggle's outer lug and the holder's − lead, toggle on: +3.6 to +4.2 V. Negative means the leads are swapped; fix it at the holder."),
    ("Gauge pass-through", "Cell through the gauge, toggle on: the same voltage on the second JST, + on the pin that goes to the charger's BAT +. Generic pigtails are often wired opposite to Adafruit's convention: meter, then crimp."),
    ("Charger-boost alone", "Only the cell on BAT. The 5 V pads: 5.0–5.2 V between + and −. The charge-rate jumper on the back is cut (500 mA). EN left open."),
    ("No shorts, unpowered", "Toggle off, cell out. Ω: 5V rail to GND and BAT+ to GND above 1 kΩ and climbing (the capacitors); 3V3 to GND above 1 kΩ; 5V to BAT+ open."),
    ("Every rod, every skin", "Ω from the cage and from each brass skin to GND, 5V, BAT+ and 3V3: open. The brass carries no net; Kapton lines every skin and every board back that faces a rod."),
    ("Schottky direction", "Rail on, USB out: XIAO 5V pin reads rail minus 0.3 V. Toggle off, USB in: the XIAO boots and the rail reads 0 V (the diode blocks)."),
    ("Gears true", "Each gear on its hub on its motor, spinning on the bench supply: under 0.5 mm of wobble at the rim; the body sits level with both gears and the skid touching."),
    ("Screen, lens, ranger", "On the bench: a frame on the screen at 26 MHz, backlight PWM from 5 % to 100 %; the camera demo shows the desk ahead; the ranger, tilted 40° down from the brow, reads the desk 85–90 mm away and a mug in front of it shorter."),
    ("Edge test, wheels off the desk", "Drive loop running, a board under the ranger: pull it away and both motors stop within one 20 ms tick; tip the body 5° and the motion sensor stops them too."),
    ("Push test, on the towel", "A 20 g eraser against the front rail at half speed: the ranger keeps reading the desk beyond it (a few millimetres shorter at the near foot is the eraser's back; longer is an edge) and the wheels slip before the motors stall. Then the board pulled from under the ranger with the eraser still there: both motors stop within the tick."),
    ("Current, the real numbers", "Everything on the cell: idle with the face on, streaming, driving. Log them next to the budget table; the run-time claims stand or fall on them."),
]

BUILD_ORDER = [
    "Bench tests on jumpers first: the chain scan (0x36, 0x5D, 0x29, 0x68), the screen, the amp, the motors from the bench supply at 3.7 V with a 0.5 A limit (stall current sets the drive cap).",
    "Caliper the two gears (outer diameter, bore, plate, length over the boss); correct the numbers at the top of this generator and regenerate before any brass is cut.",
    "Hubs: 9 mm of 5 mm tube over 9 mm of 4 mm tube, soldered, pressed into each gear with the boss inboard; true each gear on its motor shaft (1 mm of wobble at the rim is a waddle); squeeze the inner tube into the shaft's flat so it drives.",
    "Skins, when the sheet is bought (skipped 2026-11-08): cut each piece from the brass sheet to the table below, line the inside with Kapton, spray the outside canvas white, two coats, dry overnight; the two gear faces the same, with a Ø5 hole for the hub. The first build goes straight to the cage with bare boards.",
    "Bend and solder the cage: four posts, eight rails, r 3 corners; then the two fender rails at y 14.5 with the motor cradles, the brow sill, the skid post with its dome. Nothing goes on the top rails.",
    "Motors on their cradles, shafts out; gears on; the body must sit level on both gears and the skid.",
    "Floor: the holder across the front, the charger-boost at the tail with its USB-C between the back rods, the motion sensor on the right tail floor. Walls: the driver left, the amp and gauge right. Tail: the speaker and the toggle. Face: the screen in its bezel, the XIAO in its sleeve behind it, the ranger on the brow right of the lens.",
    "Kapton on every board back toward brass; wire to the sheet in white; meter every rod and every skin against every net; then the checks above in order.",
    "First roll on a towel on the floor, not the desk.",
]

RISKS = [
    ("The boost's margin", f"{RAIL5[0]} mA typical and {RAIL5[1]} peak of its 1 A, with the amp loud and Wi-Fi sending. Rev B ran 560 and 950 with the lidar; the margin is back. If the rail ever dips, cap the amp first."),
    ("The charger-boost under the motors", "Flat on the tail floor it passes 0.9 mm under the motors only without its screw terminal; the 5 V pair solders to the terminal's pads instead. If the board comes with the block soldered, two pins to unsolder."),
    ("Nothing looks far ahead", f"With the lidar gone the edge ranger is the only range sensor. Its cone sweeps the desk {RAYS['steep']['ahead_face']:.0f}–{RAYS['shallow']['ahead_face']:.0f} mm ahead of the face; anything standing in it, a mug or a book, reads shorter than the desk and stops Crumb as an edge does. A pen lying flat may not; the motion sensor feels the bump. The camera sees further when the server is on. Aimed along a desk, one zone mostly reads the desk at its near foot, so this ranger cannot pick out a low object 30 cm away: the camera and the server can, at a few frames a second, and an 8×8 ranger on the brow could, which is why one is on the list to buy, just in case (2026-11-10)."),
    ("Edges alongside, and behind", f"Head-on, the steep ray meets the desk {EDGE_WARN:.0f} mm before the skid and {WHEEL_WARN:.0f} mm before the wheels, and Crumb stops in {STOP_MM:.0f} mm from {V_LOAD:.0f} cm/s. But the foot is only {2 * FOOT_HALF:.0f} mm wide where it first meets the desk and sits {RNG_EYE[0]:.0f} mm right of the midline, while the wheels run {WHEEL_X:.1f} mm either side: an edge within about {ANGLE_L:.0f}° of head-on is seen before a wheel reaches it (to {ANGLE_R:.0f}° on the right, under the ranger), an edge running almost alongside is reached by the outer wheel first, the left sooner, and nothing looks back. Four rules for the drive loop close that with no new part: step at most {STEP_MM:.0f} mm, then sweep ±45°, whose foot covers both wheel tracks {WHEEL_WARN:.0f}–{FAR_WHEEL:.0f} mm ahead; reverse only the 20 mm back-off after an edge stop, over desk just crossed; spin in place, never arc, near an edge; a missing or flagged reading is a stop (glass desks defeat the beam, so Crumb will refuse to move on one; sun gives false stops, which are safe). The last line is the motion sensor: if a wheel drops, the body rolls until the floor rail meets the desk edge at about {CATCH_DEG:.0f}°, the 5° tilt stop firing first, and the centre of mass stays over the other wheel and the skid, so Crumb hangs with one wheel in the air rather than falling. Worked through 2026-11-10."),
    ("Pushing small things", f"Traction sets the push: about {MASS - SKID_LOAD:.0f} g rides on the wheels, so steel teeth on wood give roughly {PUSH_N:.1f} N and the wheels slip before the motors stall. That moves anything under about {PUSH_G:.0f} g that slides, and heavier things that roll: a pen, an eraser, a bottle cap, a spare cell; not a mug, not a phone. Anything under about {UNDER_MM:.0f} mm tall within 20 mm of the face stays under the cone, so the desk beyond it is still read and the edge stop keeps working; in push mode a slightly shorter reading is the object's back at the near foot, a longer one is still the edge. Things that fill the foot, a book or a long box, blind it: not those. Push at half speed, which cuts the stop to a few millimetres so the object's far side stays on the desk. The screen module starts 7 mm above the desk and the only bumper today is the 6 mm floor rail and the skid, so pushing wants a bumper rod across the front posts at about 15 mm, a few millimetres proud of the face: one more line, for a Rev D, not drawn."),
    ("The nose skid", f"The centre of mass sits {D_AX:.1f} mm ahead of the axle and {YCOM:.0f} mm up, {REV_B['ycom'] - YCOM:.0f} mm lower than Rev B's with the lidar on the roof. It rests on its nose skid with about {SKID_LOAD:.0f} g. Braking cannot tip it over the skid below {TIP_FWD:.1f} m/s²; accelerating forward lifts the skid only above {TIP_BACK:.1f}. The firmware ramps at {RAMP}."),
    ("Gear on hub on shaft", "Three fits in series, and Crumb's recipe wanted a drop of CA, which the bench does not have. The 4 mm tube's bore is the shaft's 3 mm: press it on and squeeze a dimple into the D-flat with pliers so it drives; the 5 mm tube soldered over it fills the gear's bore, and the boss's grub screw, if the gear has one, clamps the stack (else a bead of hot glue on the inboard end). True each wheel on its motor before the cage closes."),
    ("Steel teeth on the desk", f"64 tooth tips a turn tick at about {64 * 45 / 60:.0f} a second at speed, faint on wood, sharper on glass, and they can mark a soft finish. Grip is not in question: 0.4 m/s² needs a friction coefficient of 0.04. A desk mat, or a silicone O-ring stretched over the teeth, if the tick matters; the look says bare teeth."),
    ("The seller's Ø40", "The gear is drawn from the listing (Ø40, 9 over the boss, 5 mm bore; 39.6 by its module) and it is on the bench: caliper it before anything is cut. The axle height is its radius; the width is 2 × (27 + its length over the boss)."),
    ("Skins in an open cage", "A skin is 0.13 mm brass over Kapton: it insulates by the Kapton, not by itself. Every skin is metered against every net before power, and no skin reaches a rod. Spray before fitting; keep the iron off the painted side."),
    ("Wi-Fi inside brass", "An open cage of 1 mm rod is not a shield at 2.4 GHz; the antenna flex lies flat on the inside of the XIAO's sleeve, facing the open top. Compare RSSI against the bare board before the skins go on."),
    ("Two free pins", "Nine pins in use, two free (D2, D3). A double tap on the body, read by the motion sensor, is the button; the toggle is the only switch. The owned button could come back on D3, or the 8×8 ranger to buy on D2 (its LPn); neither is drawn."),
]

CHECKED = [  # (what, how it was re-checked, 2026-11-09)
    ("Pins", "Nine header pins in use on nine different GPIOs (1, 2, 5–9, 43, 44), checked by the script; D2 (GPIO3) and D3 (GPIO4) are free. GPIO3 is a strapping pin only with the JTAG eFuse burned, which it is not, so it may float through boot now that its 100 kΩ is gone; the firmware makes both inputs with pull-downs. GPIO43 prints the ROM's boot log and drives only the screen's DC line; GPIO44 is the ROM's RX, pulled up, and drives only the backlight. I²S sits on GPIO 7, 8, 9, freed by cutting J3; the PDM microphone keeps I²S0, the amp takes I²S1."),
    ("I²C chain", "Unchanged. Four addresses, none shared: ranger 0x29, gauge 0x36, driver 0x5D, motion sensor 0x68. Pull-ups once the driver's jumper is cut: 2.2 kΩ ∥ 10 kΩ ∥ 10 kΩ = 1.5 kΩ, a 2.2 mA sink, under the 3 mA the bus allows at 400 kHz."),
    ("The power chain", f"Cell, toggle, fuel gauge, charger-boost, in that order, as Rev B. The 5 V rail feeds the XIAO through the Schottky and the amp: {RAIL5[0]} mA typical, {RAIL5[1]} peak of the boost's 1 A. Nothing new rides on the boost's start: the XIAO and the amp were on the rail at power-up in Rev B too, and the lidar came on a second later through its switch. Motors on the cell rail only: {MOTOR_MA[0]} mA running, {MOTOR_MA[1]} stalled, 1.4 A for two under the firmware's cap, inside the cell's 2 A protection. The toggle sits between the cell and the charger, so the cell charges with the toggle on."),
    ("Why the 5 V rail stays", "Nothing on Crumb needs 5 V by itself: the XIAO has battery pads and the amp runs from 2.5 V. But on its battery pads the XIAO brings its own 100 mA charger onto the cell beside the charger-boost, makes the cell rail live whenever its USB is in with the toggle off, and sags with every motor stall at a low cell. Through its 5V pin and the Schottky it sits on a steady 4.7 V, the charger-boost is the only charger, and the toggle still kills everything. So the boost stays in use, for the XIAO and the amp."),
    ("The lidar's branch, removed", "Gone: the lidar and its ZH1.5 pigtail, the three posts on the top rails, the P-MOSFET, the N-MOSFET that drove it, the 10 kΩ, 1 kΩ and 100 kΩ, the 100 µF and 100 nF at the lidar, the serial wire to D3 and the switch wire from D2. Nothing else on the sheet changed its connections; the amplifier moved up under the rail where the switch and the lidar were, and the screen's reset network was redrawn so no ground symbol sits on the clock line."),
    ("The diode", "SS14 Schottky in the XIAO's 5V lead, 0.3 V drop at 0.3 A: the rail feeds the pin, a PC's USB never backfeeds the rail. Flash with the toggle off, or over the air."),
    ("Screen", "ST7789 on 4-wire SPI through the GPIO matrix at 26 MHz: CLK GPIO1, DIN GPIO2, DC GPIO43, CS tied to GND as the only SPI device, RST 10 kΩ to 3V3 with 1 µF, BLK on GPIO44 PWM; 3.3 V throughout. The header order (GND VCC SCL SDA RES DC CS BLK on this family) is read off the silkscreen before wiring."),
    ("Amp and speaker", "MAX98357A on 5 V with 220 µF at VIN, GAIN open (9 dB), SD on its own pull-up; BCLK, LRC, DIN on GPIO 7, 8, 9. Bridged output: neither speaker lead is ground."),
    ("Charger-boost", "bq25185: charge-rate jumper cut for 500 mA (0.53 C on the 950 mAh cell), EN open, six-hour timer, power path so the robot runs on the lead; BAT through the gauge's pass-through; the 5 V pair soldered to the pads of the unfitted terminal block. Its boost is in use."),
    ("Geometry", f"The overlap audit passes for every pair of parts and every part stays inside the cage: nothing rises above the top rail at {TOP:.0f} mm. The charger-boost clears the motors by 0.9 mm. The ranger's steepest ray meets the desk {RAYS['steep']['path']:.0f} mm away, past the sensor's 40 mm floor."),
    ("Mass and balance", f"About {MASS:.0f} g: Rev B's 250 less the lidar (45 g), its switch and its wiring (2 g), and the cage weighed from its rod list, {ROD10} mm of 1.0 mm brass at {ROD10_G:.0f} g, about {CAGE_G} g with the skid and the solder, where Crumb and Rev B had carried 28. Centre of mass {D_AX:.1f} mm ahead of the axle and {YCOM:.0f} up; {SKID_LOAD:.0f} g on the skid."),
    ("Parts", "Nothing to buy, checked 2026-11-09 against the Amazon, DigiKey and Adafruit order mails. In the mail: the XIAO (arriving 11-11, its Amazon order page read 2026-11-10), the charger-boost (DigiKey, shipped 11-09 by USPS, about 11-12 to 11-14) and the motion sensor 3-pack (arriving 11-09); everything else delivered. The motion sensor was carried as on hand since 11-07, but the ten-pack is not due until 11-19 to 12-15. The lidar kit and the P-MOSFET pack go to the shared bin, unallocated. 2026-11-10: one 8×8 ranger added to buy, just in case, for the look-ahead and the cover of both wheel tracks; the owned spare went into the Mars rover's head (Rev J, 11-09)."),
    ("Still to measure", "On the bench, before brass: the two gears (outer diameter, bore, plate, length over the boss, grub screw), the Hosyond header order, whether the 6106 arrives with its terminal block soldered, the N20s' stall current (it sets the drive cap), and Wi-Fi RSSI inside the cage with the skins on."),
]

SKINS = [  # (part, as sold, the skin, window)
    ("Motor driver", "red SparkFun board, 25 × 25", "25 × 25 face plate, folded 10 mm over the top edge", "none; the terminals face the rods"),
    ("Amplifier", "blue HiLetgo board, 19 × 16", "19 × 16 face plate", "none"),
    ("Fuel gauge", "black Adafruit board, 25 × 18", "25 × 18 face plate", "none"),
    ("Motion sensor", "blue GY-521, 21 × 16", "21 × 16 top plate", "none"),
    ("Edge ranger", "green Pololu carrier, 13 × 18", "13 × 18 front plate", "4 × 3 for the sensor"),
    ("Charger-boost", "black Adafruit board, 29 × 19", "29 × 19 top plate, cut round the JST", "none; USB-C and LEDs face the back"),
    ("XIAO stack", "black Seeed boards, 21 × 18 × 9", "a sleeve round three sides, 21 tall", "Ø3.5 for the lens; the top open for the antenna flex"),
    ("1.54\" screen", "module board, 33 × 36", "33 × 36 bezel", "28 × 28 to the glass"),
    ("Cell holder", "black plastic, 43 × 18 × 14", "a U over the front and top, 43 wide", "none"),
    ("Gear faces", "steel, Ø40", "two Ø37 discs on the outer faces", "Ø5 for the hub tube"),
    ("Left black", "screen glass, lens, speaker cone", "none", "—"),
]

PARTS = [  # (group, rows: qty, part, url, where, price, note); "where" carries the order and what its mails said when checked, 2026-11-09
    ("Bought, in the mail", [
        ("1", "Seeed XIAO ESP32-S3 Sense", LINKS["xiao"], "Amazon 114-5249290-9043412, ordered 2026-10-31; shipped: its Amazon order page (read 2026-11-10 03:30 EST) says arriving 11-11, previously expected 11-15", "$26.12 with tax",
         "Brain, camera, PDM microphone, Wi-Fi. Cut jumper J3 first. BAT pads stay empty; the 5V pin takes the rail through the Schottky."),
        ("1", "Adafruit bq25185 USB-C charger with 5 V boost", LINKS["boost_dk"], "DigiKey sales order 102777448 (1528-6106-ND), ordered 2026-11-08; shipped 2026-11-09 by USPS Ground Advantage (DigiKey's mail 06:48 EST: invoice 136003544, tracking 9200190106460365547930); about 11-12 to 11-14", "$15.18 all in",
         "Crumb's charger and its 5 V rail: USB-C in, JST BAT, 5 V 1 A out on two pads (its terminal block is left off here), EN pad, a charge-rate jumper on the back: cut it for 500 mA. The boost stays in use for the XIAO and the amp, run from the charger's power path, so the robot keeps running on the lead. The two Adafruit ones of 10-26 are Cyber Dawn's and the satellite's."),
        ("1 of 3", "GY-521 MPU6050 motion sensor, 3-pack", LINKS["imu"], "Amazon 114-1259113-3701002, ordered 2026-11-06; arriving 11-09 by Amazon's Orders page (read 11-09), no shipping mail yet", "$12.84 the pack",
         "VCC 3V3, AD0 to GND, 0x68. Its 2.2 kΩ pull-ups stay (the driver's go). The drone takes one of the three. The ten-pack of 10-27 is not due until 11-19 to 12-15, so this pack is the only motion sensor coming soon."),
    ]),
    ("To buy, just in case (decided 2026-11-10)", [
        ("1", "VL53L7CX 8×8 laser ranger carrier", LINKS["rng8"], "Pololu via DigiKey Marketplace, 2183-3418-ND, ships from Pololu by USPS; 277 in stock at Pololu on 2026-11-09; not sold on Amazon", "$19.95 + post",
         "The look-ahead and the cover for both wheel tracks, if the single-zone ranger proves thin on the desk: on the brow beside the lens, tilted about 20° down, its upper rows 30 cm out, its lower rows on the near desk, its 60° field wider than the track. LPn on the free D2; the edge ranger moves to 0x2A at boot while this one is held off the bus; 100 mA typical, 150 peak, on the 3V3 rail. A Rev D if it goes on; not drawn."),
    ]),
    ("On hand: Crumb's bin", [
        ("1 of 3", "Hosyond 1.54\" IPS, ST7789, 240 × 240", LINKS["ips"], "Amazon 114-6045175-2593056, 2026-10-31; delivered 11-03", "owned", "The face: 220 ppi, 4-wire SPI at 26 MHz, backlight pin on PWM. Header GND VCC SCL SDA RES DC CS BLK, bent back into the chin. CS to GND, RST pulled up."),
        ("2", "N20 gear motor, 6 V 100 rpm, 3 mm D-shaft", LINKS["n20"], "the same order; delivered 11-03", "owned", f"About 60 rpm at the cell's voltage, 45 under load: {V_LOAD:.0f} cm/s on Ø40. Measure stall current before the frame."),
        ("2", "HSP 11184 steel spur gears, 64 teeth, module 0.6", LINKS["gears"], "the same order; delivered 11-03, on the bench", "owned", "The wheels. Ø40 over the teeth by the seller's drawing (39.6 by the module), 5 mm bore, 9 mm over the boss, about 32 g each; the pack's pinions stay spare. Caliper before the frame."),
        ("1", "SparkFun Qwiic motor driver", LINKS["drv"], "the same order; delivered 11-03", "owned", "0x5D, two Qwiic sockets, screw terminals for VIN/GND and the two motors, 3–11 V in. Cut its I²C pull-up jumper. Read the terminal silkscreen before wiring."),
        ("1 of 12", "MAX98357A I²S amplifier", LINKS["amp"], "three in the same order (delivered 11-03), nine from Amazon 111-8554202-0502625 and 114-5029591-3604223 (09-02, 10-11)", "owned", "VIN from the 5 V rail, 220 µF at its VIN, GAIN open, SD on its pull-up."),
    ]),
    ("On hand: shared stock", [
        ("1", "VL53L1X laser ranger carrier", LINKS["rng1"], "DigiKey marketplace (Pololu) 102531268, 2026-10-27; shipped 10-28, picked up 11-03", "owned", f"VIN 3V3, 0x29, XSHUT and GPIO1 open. On the brow, 40° down, 27° cone, 4 cm minimum, path {RAYS['steep']['path']:.0f}–{RAYS['shallow']['path']:.0f} mm. With the lidar gone it is also the forward eye: anything standing in its cone reads short."),
        ("1 of 2", "Adafruit MAX17048 fuel gauge", LINKS["gauge"], "Adafruit 3771280, 2026-10-26 (two bought; Cyber Dawn has the other); delivered 10-28", "owned", "In the cell lead between the toggle and the charger: JST A from the toggle, JST B to BAT. VIN from the chain's 3V3, 0x36, INT open."),
        ("1 of 13", "Nitecore NL169 16340, 950 mAh, protected", LINKS["cell"], "IMR Batteries 20739060 and 20739061, 2026-10-16; delivered 10-21", "owned", "16.6 × 34.1 mm, 20 g, 2 A protection; charged at 500 mA in place, about 2.2 h."),
        ("1 of 10", "16340 holder with leads", LINKS["holder"], "Amazon 114-1421763-3353854, 2026-10-27; delivered 10-30", "owned", "Across the floor, opening up. Meter red to +."),
        ("1 of 20", "MTS-102 toggle", LINKS["toggle"], "the same order; delivered 10-30", "owned", "In the cell's + lead, on the tail wall, lever out the back."),
        ("1 of 6 + 3 ordered", "Same Sky CES-20134-088PM speaker", LINKS["spk"], "DigiKey 101368762 and 101971685 (09-02, 10-01); delivered. Three more ordered 2026-11-10 as spares (sales order 102810661, $24.54 all in), due about 11-13 to 11-16", "owned", "20 × 13 × 4.9, 8 Ω 0.8 W, the tail wall, firing backward."),
        ("1 of 100", "Chanzon SS14 Schottky diode, 1 A 40 V", LINKS["schottky"], "Amazon 114-5201101-3840264 (the drone's pack), 2026-10-27; delivered 10-30", "owned", "In the XIAO's 5V lead, band toward the XIAO, heat-shrunk in the wire."),
        ("1 + 1", "100 mm QT cable; QT-to-header cable", LINKS["qt"], "Adafruit 3765988, 2026-10-19 (seven and two bought); at the front desk 10-21", "owned", "Gauge to driver; driver to the ranger and motion sensor."),
        ("3 plugs", "JST-PH 2.0 mm 2-pin pigtails, daier 20-pair set", "https://www.amazon.com/dp/B0F6T4LKDG", "Amazon 111-8554202-0502625, 2026-09-02; delivered 09-04", "owned", "One plug into the gauge's JST A from the toggle; two plugs back to back from the gauge's JST B to the charger's BAT. Meter the polarity, not the colours."),
        ("4 × 300 mm", "1.0 mm brass rod (the cage, rails, cradles, sill, skid post)", LINKS["rod10"], "Amazon 111-4723174-9565024, 114-8041650-5363423, 114-1256902-8439449 (09-02, 10-07, 10-10); delivered; count the drawer", "owned", f"About {ROD10} mm in all, which needs a fourth rod once the pieces are laid out on 300 mm lengths; the cut list is below."),
        ("5 + 18 + 18 mm", "4 mm brass tube (the skid dome), 4 and 5 mm tube (the two hubs)", LINKS["tube"], "Amazon 114-9676073-9134626 (METERXITY sets), 2026-10-26; delivered 10-28", "owned", "Each hub: 9 mm of 4 mm tube inside 9 mm of 5 mm tube, soldered."),
        ("", "Rust-Oleum canvas-white spray; Kapton tape; white heat-shrink; white 26 and 30 AWG silicone wire", LINKS["white"], "Pip's stock, Amazon 2026-09-02; on hand", "owned", "The skins' outside, their lining, the wire sleeves, the wire."),
        ("", "10 kΩ ×1; 220 µF, 10 µF, 1 µF, 100 nF ×2; hot glue", PASSIVES, "the resistor kit, the ceramic kit (111-8554202-0502625) and the electrolytic kit (111-6329624-3227449), 2026-09-02; on hand", "owned", "Values as drawn on the sheet: the screen's reset pull-up and its 1 µF, the amp's 220 µF, the screen's 10 µF and 100 nF, the ranger's 100 nF."),
    ]),
    ("Later, if the skins are wanted (skipped by the builder 2026-11-08)", [
        ("1 sheet of 6", "K&S 250 brass sheet, 0.005 in (0.13 mm), 4 × 10 in", LINKS["sheet"], "Amazon, 6-pack, $24.54; moved to Saved for Later 2026-11-08", "not bought",
         "The skins: about 85 cm² of one sheet. Cut with scissors, folded over a rule, Kapton inside, canvas white outside. The first build runs with bare boards and bare gear faces; the skins table below is the finish step whenever the sheet is bought."),
    ]),
    ("No longer Crumb's (Rev C, 2026-11-09)", [
        ("1", "LDROBOT LD19 lidar, as the youyeetoo FHL-LD19 kit (sensor, pigtail, USB adapter, Dupont leads)", LINKS["lidar_d300"], "Amazon order 114-7956116-1377847 of 2026-11-08; shipped that night, arriving 11-09", "$71.90",
         "Bought for Rev B, dropped in Rev C: too big for a small, cute desk robot. It goes to the shared bin, unallocated until the builder names a project. Not the XS drone: 47 g on a 34 g drone with a thrust-to-weight of 2.0 cannot fly."),
        ("1 pack of 100", "P-channel MOSFET AO3401A, SOT-23", "https://www.amazon.com/dp/B09WN8WP8M", "the same Amazon order; shipped that night", "$7.49 the pack",
         "Bought for the lidar's switch; all 100 spare now, to the shared bin for the family."),
    ]),
    ("Set aside", [
        ("0", "VL53L7CX 8×8 ranger, the owned spare", LINKS["rng8"], "the drone's spare of 2026-10-28, drawn into the Mars rover's head (Rev J, 2026-11-09)", "the rover's", "Crumb's first brow sensor, set aside in Rev B for the lidar and claimed by the rover the day Rev C was approved. Crumb's own is the just-in-case line above."),
        ("1", "tactile button", LINKS["button"], "Amazon, on hand", "spare", "D3 is free again, so it could come back on the tail wall; not drawn. The double tap is the button."),
        ("2", "1.54\" colour screens", LINKS["ips"], "Crumb's box", "spare", "Three owned; one is the face."),
        ("", "Mochi's round screen and Pololu white wheels", LINKS["round_amz"], "never bought", "—", "Mochi is set aside; nothing of it was ordered."),
    ]),
]


# ============================================================================= drawings
IVORY, IVORY2 = "var(--ivory)", "var(--ivory-2)"
STEEL_DK = "var(--steel-dk)"
STEEL_DK_CSS = (":root{--steel-dk:#6c7178}@media (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){--steel-dk:#7b8189}}"
                ":root[data-theme=\"dark\"]{--steel-dk:#7b8189}")   # the motors' cans, a shade under the gears' steel
SKIN = 'stroke="var(--skin-edge)" stroke-width=".6"'


def skin(v, u, w_, du, dw, op=1.0):
    """A board face wearing its ivory skin."""
    v.rect(u, w_, du, dw, IVORY, SKIN + (f' opacity="{op}"' if op < 1 else ""))


def gear_edge(v, sx, c):
    """A gear edge-on from side sx (±1): boss inboard, plate outboard, the ivory face on its outer side, the brass hub between post and boss. c = the axle's other coordinate."""
    xi = sx * WX0
    b0, b1 = sorted((xi, xi + sx * BOSS_W)); p0, p1 = sorted((xi + sx * BOSS_W, xi + sx * WW)); f0, f1 = sorted((xi + sx * WW, xi + sx * (WW - 0.6)))
    v.rect(b0, c - BOSS_D / 2, b1 - b0, BOSS_D, "var(--steel)")
    v.rrect(p0, c - WR, p1 - p0, 2 * WR, 0.8, "var(--steel)", 'stroke="var(--fg)" stroke-width=".4"')
    v.rect(f0, c - M.GEAR_FACE_R, f1 - f0, 2 * M.GEAR_FACE_R, IVORY)
    v.line(sx * CX1, c, xi, c, 'stroke="var(--brass)" stroke-width="3.2"')


def ranger_side_pts():
    """The ranger board seen from the side: 17.8 long, 2.5 thick, its normal 40° below level, centred behind the brow."""
    n = (math.cos(RNG_TILT * D2R), -math.sin(RNG_TILT * D2R))      # (z, y) the way it looks
    t = (math.sin(RNG_TILT * D2R), math.cos(RNG_TILT * D2R))       # along the board
    cz, cy = RNG_EYE[2] - 1.3 * n[0] - 6.5 * t[0], RNG_EYE[1] - 1.3 * n[1] - 6.5 * t[1]
    return [(cz + a * t[0] + b * n[0], cy + a * t[1] + b * n[1]) for a, b in ((-8.9, -1.25), (8.9, -1.25), (8.9, 1.25), (-8.9, 1.25))]


def front_face(v, xc=0.0):
    """The face seen from the front: the bezel, the picture with Pip's eyes, the lens and the ranger on the brow."""
    skin(v, xc - IPS_W / 2, 7, IPS_W, IPS_H)
    v.rect(xc - IPS_PIC / 2, FACE_Y - IPS_PIC / 2, IPS_PIC, IPS_PIC, "var(--glass)"); eyes_square(v, xc, FACE_Y, IPS_PIC, IPS_PIC)
    v.circ(xc + LENS[0], LENS[1], 2.6, "var(--glass)"); v.circ(xc + LENS[0], LENS[1], 1.1, "var(--lens)")
    skin(v, xc + 7, 45, 12.7, 14); v.rect(xc + 11.5, 54.5, 3.6, 3, "var(--window)")


def final_views():
    key, views = [], []
    K = lambda n, t: key.append((n, t))

    # ---------- front
    f = View(112, 100, 56, 19, "Crumb Rev C, front view")
    desk(f, -56, 56)
    for sx in (-1, 1):
        gear_edge(f, sx, AY)
    f.rect(-25, 15, 24, 10, STEEL_DK); f.rect(1, 15, 24, 10, STEEL_DK)                           # motors, behind the holder and the screen
    skin(f, -21.5, 6.5, 43, 14)                                                                   # holder, skinned
    skin(f, -24, 33, 10, 25)                                                                      # driver edge-on, left wall
    skin(f, 21, 23, 3, 26)                                                                        # gauge and amp edge-on, right wall
    skin(f, -14.5, 36, 21, 21)                                                                    # XIAO sleeve
    front_face(f)
    f.rrect(CX0, CY0, CX1 - CX0, CY1 - CY0, CR, "none", ROD); f.line(CX0, 45, CX1, 45, ROD_THIN)    # the cage, the brow sill
    f.circ(0, SKID_R, SKID_R, "var(--brass)"); f.line(0, CY0, 0, 2 * SKID_R, 'stroke="var(--brass)" stroke-width="1.4"')
    f.dim(-(WX0 + WW), -8.5, WX0 + WW, -8.5, f"{OVERALL:.0f} over the gears", off=0)
    f.dim(48, 0, 48, TOP, f"{TOP:.0f}", off=0, side="right")
    f.tag(1, 0, FACE_Y + 10, -42, 36); f.tag(2, LENS[0], LENS[1], -42, 62); f.tag(3, 13.3, 52, 42, 60); f.tag(4, -31.5, 10, -43, 8)
    f.tag(7, -19, 45, -42, 48); f.tag(8, 22.5, 36, 42, 30); f.tag(10, 0, 2.5, 42, 6); f.tag(12, CX1, 56, 42, 74)
    views.append((f.svg(), f"Front. An open cage of 1.0 mm brass rod, {TOP:.0f} mm to its top rail and nothing above it; the two gears edge-on either side, ivory faces out; the square screen in its ivory bezel; the camera and the edge ranger on the brow."))

    # ---------- side, face to the right (seen from the robot's right)
    s = View(118, 100, 46, 19, "Crumb Rev C, side view, face to the right")
    desk(s, -46, 72)
    skin(s, -28, 33, 25, 25, op=.45)                                                               # the driver on the far wall, behind the amp from here
    skin(s, -28.5, 6.5, 29, 5.1); s.rect(-28.5, 11.6, 8.5, 2.5, "var(--steel)")                    # charger-boost on the floor, its JST
    skin(s, 0.5, 6.5, 18, 14)                                                                      # holder in its skin
    s.rect(AZ - 6, 15, 12, 10, STEEL_DK)                                                           # motor end-on
    skin(s, -28.5, 6.5, 20.5, 3)                                                                   # motion sensor, right tail floor
    skin(s, -26, 33, 19, 16); skin(s, 0, 23, 18, 25)                                               # amp, gauge on the near wall
    s.text(-16.5, 40, "amp", "hid", dy=2); s.text(11, 44, "gauge", "hid", dy=2)
    s.rect(-28.5, 40, 4.9, 13, "var(--black)")                                                     # speaker on the tail wall
    s.rect(CZ0 - 1, 44, 1, 4, "var(--steel)"); s.line(CZ0 - 1, 46, CZ0 - 7, 48, 'stroke="var(--steel)" stroke-width="2"')   # toggle bat
    s.rect(CZ0 - 1.2, 7.3, 1.2, 3.3, "var(--steel)")                                               # USB-C, back
    skin(s, 16.5, 36, 8, 21)                                                                       # XIAO sleeve
    s.rect(24.5, 7, 1.9, IPS_H, "var(--black)"); s.rect(26.4, 7, 0.6, IPS_H, IVORY)                # screen edge-on, bezel
    s.circ(CZ1 - 1.2, LENS[1], 1.5, "var(--glass)")
    s.poly(ranger_side_pts(), IVORY, SKIN)
    for name, w_ in (("steep", 1), ("centre", 2), ("shallow", 1)):
        r = RAYS[name]; s.line(RNG_EYE[2], RNG_EYE[1], r["z"], 0, BEAM if w_ == 1 else 'stroke="var(--beam)" stroke-width="1.4" stroke-dasharray="3 2"')
    s.add(f'<text x="{s.X(72)}" y="{s.Y(-4.2)}" class="dimlab" text-anchor="end">edge seen {RAYS["steep"]["ahead_face"]:.0f}–{RAYS["shallow"]["ahead_face"]:.0f} mm ahead of the face</text>')
    s.rrect(CZ0, CY0, CZ1 - CZ0, CY1 - CY0, CR, "none", ROD)                                      # the cage sits inside the gear: drawn first
    s.line(CZ0, 14.5, CZ1, 14.5, ROD_THIN); s.circ(CZ1, 45, 0.9, "var(--brass-dk)")               # fender rail, brow sill end-on
    M.gear_side(s, AZ, AY)
    s.circ(SKID_Z, SKID_R, SKID_R, "var(--brass)"); s.line(SKID_Z, CY0, SKID_Z, 2 * SKID_R, 'stroke="var(--brass)" stroke-width="1.4"')
    s.dim(CZ0, -8.5, CZ1, -8.5, "56", off=0)
    s.tag(4, AZ, AY, -40, 14); s.tag(5, 16, 12, 48, 12); s.tag(6, CZ0 - 0.6, 9, -40, 4); s.tag(8, -22, 46, -40, 34)
    s.tag(9, CZ0 - 4, 47, -40, 58); s.tag(11, -26, 8, -40, 24); s.tag(3, 22, 52, 50, 64); s.tag(10, SKID_Z, 2.5, 50, 4)
    s.text(CZ1 + 4, 31, "face", "dimlab", "start")
    views.append((s.svg(), "Side, face to the right. The Ø40 gear with its ivory face covers the lower two thirds of the cage; behind it the motor at axle height, the cell across the floor ahead of it, the charger-boost on the tail floor; the driver is on the far wall behind the amp. Orange dashes: the edge ranger's cone."))

    # ---------- top: looking down through the open top, the parts drawn lowest first so the higher ones cover them
    t = View(100, 94, 50, 50, "Crumb Rev C, top view, face at the top")
    for sx in (-1, 1):
        gear_edge(t, sx, AZ)
    skin(t, 10, -28.5, 15.5, 20.5)                                                         # motion sensor, to y 9.5
    skin(t, -9.5, -28.5, 19, 29); t.rect(-9.5, -28.5, 9.5, 8.5, "var(--steel)")            # charger-boost to 11.6, its JST to 14.1
    skin(t, -21.5, 0.5, 43, 18)                                                             # holder to 20.5
    t.rect(-25, AZ - 6, 24, 12, STEEL_DK); t.rect(1, AZ - 6, 24, 12, STEEL_DK)                  # motors to 25
    t.rect(-IPS_W / 2, 24.5, IPS_W, 1.9, "var(--black)"); t.rect(-IPS_W / 2, 26.4, IPS_W, 0.6, IVORY)   # screen to 43, its bezel
    skin(t, 21, 0, 3, 18); skin(t, 21, -26, 3, 19)                                          # gauge to 48, amp to 49
    t.rect(12, -28.5, 6, 9.5, "var(--steel)")                                               # toggle to 50
    t.rect(-10, -28.5, 20, 4.9, "var(--black)")                                             # speaker to 53
    skin(t, -14.5, 16.5, 21, 8); t.circ(LENS[0], 23.5, 1.5, "var(--glass)")                 # XIAO sleeve to 57, the lens at its face
    skin(t, -24, -28, 10, 25)                                                               # driver to 58
    skin(t, 7, 18, 12.7, 8.8)                                                               # edge ranger to 59
    t.rect(-CELL_L / 2, CELL_Z - CELL_D / 2, CELL_L, CELL_D, "none", HID)                   # the cell in its holder, under the skin
    t.circ(0, SKID_Z, SKID_R, "none", HID)                                                  # the skid, under the face
    t.text(0, CELL_Z - 1, "16340 cell", "hid", dy=2); t.text(-19, -15, "drv", "hid", dy=2); t.text(15.5, -16.5, "MPU", "hid", dy=2)
    t.rrect(CX0, CZ0, CX1 - CX0, CZ1 - CZ0, CR, "none", ROD)
    t.text(0, CZ0 - 7.5, "back: USB-C low in the middle · toggle right of the speaker", "hid", dy=2)
    t.dim(-(WX0 + WW), CZ0 - 13, WX0 + WW, CZ0 - 13, f"{OVERALL:.0f}", off=0)
    t.tag(12, CX0, 20, -43, 30); t.tag(5, -19, 3, -43, 12); t.tag(13, -19, -10, -43, -10); t.tag(6, 0, CZ0 - 1, 43, -31); t.tag(11, 15, -14.5, 43, -18)
    t.text(0, CZ1 + 3, "face", "dimlab")
    views.append((t.svg(), "Top, face at the top, looking down through the open top. The cell lies across the floor in its holder (dashed); the charger-boost lies behind the motors with its USB-C at the back; every board drawn in its ivory skin."))

    K(1, "Hosyond 1.54\" square colour screen, the lower face, in an ivory brass bezel with a 28 × 28 window; Pip's eyes at 240 × 240.")
    K(2, "XIAO ESP32-S3 Sense standing behind the face in an ivory sleeve, lens on the brow at (−4, 50) looking straight out; camera, microphone, Wi-Fi.")
    K(3, f"Edge ranger on the brow right of the lens, tilted 40° down: the hard stop, desk {RAYS['steep']['ahead_face']:.0f}–{RAYS['shallow']['ahead_face']:.0f} mm ahead of the face, the edge seen {EDGE_WARN:.0f} mm before the skid reaches it and {WHEEL_WARN:.0f} before the wheels; anything standing in its cone reads short of the desk.")
    K(4, "Two N20 motors end to end on one axle at 20 up, 7 back; Crumb's Ø40 steel gears on 9 mm brass-tube hubs, each with an ivory brass disc on its face and bare teeth round it; 72 over them.")
    K(5, "16340 holder across the floor just ahead of the motors, under an ivory U-skin, the cell inside (dashed in the top view); it charges in place, toggle on, or lifts out through the open top.")
    K(6, "Charger-boost flat on the tail floor, parts up, USB-C low in the middle of the back between the rods: it charges the cell and makes the 5 V rail for the XIAO and the amplifier.")
    K(7, "Motor driver standing on the left wall above the motor, red under an ivory plate.")
    K(8, "Amplifier and fuel gauge standing on the right wall, under ivory plates.")
    K(9, "Speaker as the tail wall, firing backward; the toggle right of it, lever out the back.")
    K(10, f"Brass dome skid at the nose, the third contact; it carries about {SKID_LOAD:.0f} g.")
    K(11, "Motion sensor flat on the right tail floor under an ivory plate: heading hold, bump detection, the double tap.")
    K(12, f"The cage: four posts and eight rails of 1.0 mm brass rod, r 3 corners, {TOP:.0f} mm to the top rail and nothing on it; fender rails, cradles and a brow sill inside. Brass stays brass; no net touches it.")
    K(13, "Every board that is not black wears a 0.13 mm brass skin, Kapton inside, canvas white outside. Black is left only in the screen's glass, the lens and the speaker.")
    return views, key


def size_pair():
    """Rev B and Rev C side by side, front views to one scale: the lidar's 35 mm is the difference."""
    v = View(196, 124, 98, 19, "Crumb Rev B and Rev C, front views to one scale")
    desk(v, -98, 98)
    for xc, rev, top in ((-46, "Rev B, approved 2026-11-08", REV_B["top"]), (46, "Rev C, approved 2026-11-09", TOP)):
        for sx in (-1, 1):
            v.rrect(xc + (WX0 + BOSS_W if sx > 0 else -(WX0 + WW)), AY - WR, WW - BOSS_W, 2 * WR, 0.8, "var(--steel)", 'stroke="var(--fg)" stroke-width=".4"')
            v.line(xc + sx * CX1, AY, xc + sx * (WX0 + BOSS_W), AY, 'stroke="var(--brass)" stroke-width="3.2"')
        front_face(v, xc)
        v.rrect(xc + CX0, CY0, CX1 - CX0, CY1 - CY0, CR, "none", ROD); v.line(xc + CX0, 45, xc + CX1, 45, ROD_THIN)
        v.circ(xc, SKID_R, SKID_R, "var(--brass)")
        if top > TOP:
            v.rect(xc - 27, CY1, 54, C.LIDAR_FL_T, "var(--black-2)"); lidar_front(v, xc, CY1)
        v.dim(xc + 44, 0, xc + 44, top, f"{top:.0f}", off=0, side="right")
        v.text(xc, -14, rev, "dimlab")
    return v.svg()


# ============================================================================= the wiring sheet: Crumb's own since Rev C
T, dot, block, pin, gnd = M.T, M.dot, M.block, M.pin, M.gnd


def no_connect(x, y):
    """A free pin: a cross at its end, nothing wired."""
    return f'<path d="M{x - 5},{y - 5} L{x + 5},{y + 5} M{x - 5},{y + 5} L{x + 5},{y - 5}" class="thin"/>'


def sheet():
    W, H = 1540, 1110
    rt = M.Router(); w = rt.wire
    o = [T(20, 30, "Crumb Rev C: every connection on one sheet", "h1"),
         T(20, 50, "A dot is a joint. A line that hops over another does not touch it. Brass = the 5 V rail. Red = the cell rail after the toggle. "
                   "Thick black = a wire you solder. Thin = a resistor, capacitor or diode leg. Every ground goes to the star at the holder; the brass frame touches no net.", "sub")]
    RAIL_Y, STAR_Y = 80, 760

    # ------------------------------------------------------------ blocks and pins first (so the lane check knows every pin), rails drawn before the lanes
    XX, XY, XW, XH = 600, 150, 300, 420
    o.append(block(XX, XY, XW, XH, "XIAO ESP32-S3 Sense", "camera GPIO 10–18, 38–40, 47, 48 · mic 41, 42", sub2="J3 cut · BAT pads empty · flash with toggle OFF", ty=48))
    Lp = {}
    for name, y, fn, net in (("3V3", 250, "3.3 V out", "3V3"), ("GND", 280, None, "GND"), ("D4", 320, "GPIO5 · SDA", "SDA"), ("D5", 350, "GPIO6 · SCL", "SCL"),
                             ("D0", 400, "GPIO1 · CLK", "CLK"), ("D1", 430, "GPIO2 · DIN", "DIN"), ("D6", 460, "GPIO43 · DC", "DC"), ("D7", 490, "GPIO44 · BL", "BL")):
        Lp[name] = (XX, y); o.append(pin(rt, XX, y, name, "L", net, fn, XX + 44))
    Rp = {}
    for name, y, fn, net in (("D8", 290, "GPIO7 · BCLK", "BCLK"), ("D9", 320, "GPIO8 · LRC", "LRC"), ("D10", 350, "GPIO9 · DIN", "I2S_DIN"),
                             ("D2", 420, "GPIO3 · free", "FREE_D2"), ("D3", 450, "GPIO4 · free", "FREE_D3")):
        Rp[name] = (XX + XW, y); o.append(pin(rt, XX + XW, y, name, "R", net, fn, XX + XW - 44))
    o += [no_connect(XX + XW + 14, Rp["D2"][1]), no_connect(XX + XW + 14, Rp["D3"][1]), T(XX + XW + 28, 439, "free since Rev C", "fn")]
    Tp = {"5V": (660, XY)}; o.append(pin(rt, 660, XY, "5V", "T", "5V_XIAO"))
    Bp = {"GND": (700, XY + XH)}; o.append(pin(rt, 700, XY + XH, "GND", "B", "GND"))

    SX, SY, SW, SH = 120, 200, 240, 330
    o.append(block(SX, SY, SW, SH, "1.54\" square screen", "Hosyond ST7789 · 240 × 240", sub2="8-pin header · 3.3 V · 40 mA"))
    Sp = {}
    for name, y, net in (("VCC", 250, "3V3"), ("GND", 280, "GND"), ("CS", 330, "GND"), ("RST", 365, "RST"), ("CLK", 400, "CLK"), ("DIN", 430, "DIN"), ("DC", 460, "DC"), ("BL", 490, "BL")):
        Sp[name] = (SX + SW, y); o.append(pin(rt, SX + SW, y, name, "R", net))
    o += [T(SX + 12, 334, "tied low: the only SPI device", "fn"), T(SX + 12, 369, "10 kΩ up, 1 µF down: reset", "fn")]

    AX, AY_, AW, AH = 1000, 220, 240, 200
    o.append(block(AX, AY_, AW, AH, "MAX98357A amp", "I²S in · class D · 5 V"))
    Ap = {}
    for name, y, net in (("BCLK", 290, "BCLK"), ("LRC", 320, "LRC"), ("DIN", 350, "I2S_DIN")):
        Ap[name] = (AX, y); o.append(pin(rt, AX, y, name, "L", net))
    for name, y, net in (("OUT+", 300, "SPK+"), ("OUT−", 340, "SPK-")):
        Ap[name] = (AX + AW, y); o.append(pin(rt, AX + AW, y, name, "R", net))
    Ap["VIN"] = (1222, AY_); o.append(pin(rt, 1222, AY_, "VIN", "T", "5V"))
    Ap["GND"] = (1222, AY_ + AH); o.append(pin(rt, 1222, AY_ + AH, "GND", "B", "GND"))
    o += [T(AX + 12, 392, "GAIN open: 9 dB", "fn"), T(AX + 12, 408, "SD on its own pull-up", "fn")]
    o.append(block(1290, 260, 150, 100, "Speaker", "Same Sky 8 Ω 0.8 W", sub2="own leads, 60 mm"))
    rt.pin(1290, 300, "SPK+"); rt.pin(1290, 340, "SPK-"); o += ['<circle cx="1290" cy="300" r="4" class="pinend"/>', '<circle cx="1290" cy="340" r="4" class="pinend"/>']

    o.append(block(40, 640, 150, 90, "16340 holder", "NL169 · 950 mAh", sub2="across the floor", ty=22))
    rt.pin(190, 670, "CELL+"); rt.pin(190, 710, "GND"); o += ['<circle cx="190" cy="670" r="4" class="pinend"/>', T(178, 674, "+", "pin", "end"), '<circle cx="190" cy="710" r="4" class="pinend"/>', T(178, 714, "−", "pin", "end")]
    o.append(block(240, 640, 130, 60, "Toggle", "in the + lead", ty=24))
    rt.pin(240, 670, "CELL+"); rt.pin(370, 670, "BAT+"); o += ['<circle cx="240" cy="670" r="4" class="pinend"/>', '<circle cx="370" cy="670" r="4" class="pinend"/>']
    GX, GY, GW, GH = 420, 620, 230, 190
    o.append(block(GX, GY, GW, GH, "Fuel gauge", "MAX17048 · 0x36", ty=44))
    Gp = {}
    for name, y, net in (("JST A +", 670, "BAT+"), ("JST A −", 700, "GND")):
        Gp[name] = (GX, y); o.append(pin(rt, GX, y, name, "L", net))
    for name, y, net in (("JST B +", 670, "BAT+B"), ("JST B −", 700, "GND")):
        Gp[name] = (GX + GW, y); o.append(pin(rt, GX + GW, y, name, "R", net))
    for name, x, net in (("VIN", 470, "3V3"), ("SDI", 530, "SDA"), ("SCL", 580, "SCL")):
        Gp[name] = (x, GY); o.append(pin(rt, x, GY, name, "T", net))
    o += [T(GX + 12, 782, "two JST ports, a pass-through", "fn"), T(GX + 12, 798, "INT and QStart open · QT socket below", "fn")]
    rt.pin(535, GY + GH, "QT"); o.append(f'<circle cx="535" cy="{GY + GH}" r="4" class="pinend"/>')
    CX, CY, CW, CH = 720, 620, 260, 230
    o.append(block(CX, CY, CW, CH, "Charger-boost", "bq25185 · 5 V 1 A · USB-C in", ty=44))
    Cp = {}
    for name, y, net in (("BAT +", 670, "BAT+B"), ("BAT −", 700, "GND")):
        Cp[name] = (CX, y); o.append(pin(rt, CX, y, name, "L", net))
    for name, x, net in (("+", 800, "5V"), ("−", 860, "GND")):
        Cp[name] = (x, CY); o.append(pin(rt, x, CY, name, "T", net))
    o += [T(CX + 12, 774, "jumper cut: 500 mA · EN open", "fn"), T(CX + 12, 790, "5 V pads +/−, terminal block off", "fn"),
          T(CX + 12, 806, "USB-C out the back, between the rods;", "fn"), T(CX + 12, 822, "charges, toggle on, while it runs", "fn")]
    o.append(f'<rect x="{CX + CW - 56}" y="{CY + CH - 28}" width="44" height="16" rx="3" fill="var(--panel)" stroke="var(--brass-dk)" stroke-width="1.2"/>'); o.append(T(CX + CW - 34, CY + CH - 16, "USB-C", "fn", "middle"))
    DX, DY, DW, DH = 1000, 880, 260, 150
    o.append(block(DX, DY, DW, DH, "Qwiic motor driver", "SparkFun · 0x5D · pull-up jumper cut", ty=44))
    rt.pin(DX, 960, "QT"); o.append(f'<circle cx="{DX}" cy="960" r="4" class="pinend"/>'); o.append(T(DX + 9, 964, "Qwiic 1", "pin"))
    rt.pin(DX + DW, 960, "QT2"); o.append(f'<circle cx="{DX + DW}" cy="960" r="4" class="pinend"/>'); o.append(T(DX + DW - 9, 964, "Qwiic 2", "pin", "end"))
    for name, x, net in (("VIN", 1060, "BAT+"), ("GND", 1120, "GND")):
        o.append(pin(rt, x, DY, name, "T", net))
    for name, x, net in (("A1 A2", 1180, "MA"), ("B1 B2", 1230, "MB")):
        o.append(pin(rt, x, DY + DH, name, "B", net))
    o += [T(DX + 12, 990, "VIN from the cell rail", "fn"), T(DX + 12, 1006, "read the terminal silkscreen", "fn")]
    o.append(block(1300, 1000, 80, 70, "Motor L", "N20", ty=26)); o.append(block(1400, 1000, 80, 70, "Motor R", "N20", ty=26))
    rt.pin(1300, 1035, "MA"); rt.pin(1400, 1035, "MB"); o += ['<circle cx="1300" cy="1035" r="4" class="pinend"/>', '<circle cx="1400" cy="1035" r="4" class="pinend"/>']
    o.append(block(1300, 760, 180, 100, "Edge ranger", "Pololu VL53L1X · 0x29", sub2="XSHUT, GPIO1 open"))
    o.append(block(1300, 880, 180, 100, "Motion sensor", "GY-521 MPU6050 · 0x68", sub2="AD0 to GND · INT open"))
    rt.pin(1300, 845, "QT2"); rt.pin(1300, 965, "QT2"); o += ['<circle cx="1300" cy="845" r="4" class="pinend"/>', '<circle cx="1300" cy="965" r="4" class="pinend"/>']
    o.append(T(1310, 849, "VIN GND SDA SCL", "pin")); o.append(T(1310, 969, "VCC GND SDA SCL", "pin"))

    # ------------------------------------------------------------ rails: 5 V (brass), the cell rail (red), the ground star line
    o.append(w([Cp["+"], (800, 600), (60, 600), (60, RAIL_Y), (1222, RAIL_Y)], "bus", "5V")); o.append(dot(1222, RAIL_Y))
    o.append(T(900, RAIL_Y - 10, "5 V RAIL · from the charger-boost's 5 V pads · 26 AWG · 1 A", "brass", "middle"))
    o.append(T(190, 592, "5 V out, up the left, along the top", "brass", "middle"))
    o.append(w([(210, STAR_Y), (960, STAR_Y)], "rod", "GND")); o.append(dot(210, STAR_Y)); o.append(gnd(210, STAR_Y)); o.append(T(226, STAR_Y + 22, "the star: every ground comes here", "fn"))
    o.append(w([(190, 710), (210, 710), (210, STAR_Y)], "rod", "GND"))
    o.append(w([(190, 670), (240, 670)], "rod", "CELL+"))
    o.append(w([(370, 670), (385, 670), (385, 1050), (985, 1050), (985, 860), (1060, 860), (1060, DY)], "cell", "BAT+")); o.append(dot(385, 670))
    o.append(w([(385, 670), Gp["JST A +"]], "cell", "BAT+")); o.append(T(402, 660, "BAT+", "lab", "middle"))
    o.append(T(690, 1042, "CELL RAIL · 3.0–4.2 V after the toggle · 26 AWG · the motors never load the boost", "brass", "middle"))
    o.append(w([Gp["JST B +"], Cp["BAT +"]], "cell", "BAT+B")); o.append(T(672, 660, "pigtail", "lab", "middle"))
    o.append(w([Gp["JST A −"], (405, 700), (405, STAR_Y)], "rod", "GND")); o.append(dot(405, STAR_Y))
    o.append(w([Gp["JST B −"], Cp["BAT −"]], "rod", "GND")); o.append(dot(700, 700))
    o.append(w([Cp["−"], (860, 580), (960, 580), (960, STAR_Y)], "rod", "GND")); o.append(dot(960, STAR_Y))
    o.append(w([(1120, DY), (1120, 840), (960, 840), (960, STAR_Y)], "rod", "GND"))
    o.append(w([Bp["GND"], (700, STAR_Y)], "rod", "GND")); o.append(dot(700, STAR_Y))

    # ------------------------------------------------------------ XIAO 5V through the Schottky
    o.append(w([(660, RAIL_Y), (660, 100)], "rod", "5V")); o.append(dot(660, RAIL_Y))
    o.append('<polygon points="652,100 668,100 660,116" fill="var(--panel)" stroke="var(--fg)" stroke-width="1.6"/><line x1="652" y1="116" x2="668" y2="116" class="thin"/>')
    o.append(w([(660, 116), Tp["5V"]], "thin", "5V_XIAO"))
    o.append(T(672, 112, "Schottky 1 A, owned: rail in, USB never out", "fn"))

    # ------------------------------------------------------------ screen: the reset network sits between its pins and the lanes, clear of the SPI lines
    o.append(w([Lp["3V3"], Sp["VCC"]], "rod", "3V3")); o.append(T(412, 243, "3V3", "lab", "middle"))
    o.append(w([Lp["GND"], Sp["GND"]], "rod", "GND")); o.append(T(412, 273, "GND", "lab", "middle"))
    for a, b in (("D0", "CLK"), ("D1", "DIN"), ("D6", "DC"), ("D7", "BL")):
        o.append(w([Lp[a], Sp[b]], "rod", {"D0": "CLK", "D1": "DIN", "D6": "DC", "D7": "BL"}[a])); o.append(T(480, Lp[a][1] - 7, b, "lab", "middle"))
    o.append(w([Sp["CS"], (385, 330), (385, 280)], "rod", "GND")); o.append(dot(385, 280))
    o.append(w([Sp["RST"], (470, 365)], "rod", "RST")); o.append(dot(440, 365))
    o.append(M.resistor_v(rt, 440, 365, 250, "RST")); o.append(dot(440, 250)); o.append(T(426, 312, "10 kΩ", "fn", "end"))
    o.append(w([(470, 365), (470, 327)], "thin", "RST")); o.append(w([(470, 317), (470, 280)], "thin", "GND")); o.append(dot(470, 280))
    o += ['<line x1="459" y1="327" x2="481" y2="327" class="thin"/>', '<line x1="459" y1="317" x2="481" y2="317" class="thin"/>', T(487, 326, "1 µF", "fn")]
    o.append(M.capacitor(rt, 510, 250, 280, "3V3")); o.append(dot(510, 250)); o.append(dot(510, 280)); o.append(T(505, 243, "10 µF + 100 nF", "fn", "middle"))

    # ------------------------------------------------------------ 3V3 and I²C down to the gauge (three lanes, 14 px apart, clear of the XIAO's pins)
    o.append(w([Lp["3V3"], (552, 250)], "rod", "3V3")); o.append(w([(552, 250), (552, 562), (470, 562), Gp["VIN"]], "rod", "3V3")); o.append(dot(552, 250))
    o.append(w([Lp["D4"], (566, 320)], "rod", "SDA")); o.append(w([(566, 320), (566, 578), (530, 578), Gp["SDI"]], "rod", "SDA")); o.append(dot(566, 320))
    o.append(w([Lp["D5"], (580, 350)], "rod", "SCL")); o.append(w([(580, 350), Gp["SCL"]], "rod", "SCL")); o.append(dot(580, 350))
    o.append(T(462, 556, "3V3", "lab", "end")); o.append(T(522, 572, "SDA", "lab", "end")); o.append(T(590, 588, "SCL", "lab", "start"))

    # ------------------------------------------------------------ amp and speaker, under the rail
    for a, b in (("D8", "BCLK"), ("D9", "LRC"), ("D10", "DIN")):
        o.append(w([Rp[a], Ap[b]], "rod", {"D8": "BCLK", "D9": "LRC", "D10": "I2S_DIN"}[a])); o.append(T(950, Rp[a][1] - 7, b, "lab", "middle"))
    o.append(w([Ap["OUT+"], (1290, 300)], "rod", "SPK+")); o.append(w([Ap["OUT−"], (1290, 340)], "rod", "SPK-"))
    o.append(T(1365, 380, "neither lead is ground", "fn", "middle"))
    o.append(w([(1222, RAIL_Y), Ap["VIN"]], "rod", "5V"))
    o.append(w([(1222, 140), (1285, 140)], "thin", "5V")); o.append(dot(1222, 140))
    o.append(M.capacitor(rt, 1285, 140, 180, "5V")); o.append(gnd(1285, 180)); o.append(T(1299, 166, "220 µF at the amp's VIN", "fn"))
    o.append(w([Ap["GND"], (1222, 440)], "rod", "GND")); o.append(gnd(1222, 440))

    # ------------------------------------------------------------ the power chain in numbers, where the lidar's branch was
    o.append(T(1000, 492, "THE POWER CHAIN, IN NUMBERS", "brass"))
    for i, line in enumerate(POWER_LINES):
        o.append(T(1000, 516 + 18 * i, line, "sub"))

    # ------------------------------------------------------------ the chain and the motors
    o.append(w([(535, GY + GH), (535, 960), (DX, 960)], "rod", "QT")); o.append(T(545, 940, "gauge QT → 100 mm QT cable → Qwiic 1", "fn"))
    o.append(w([(DX + DW, 960), (1280, 960), (1280, 845), (1300, 845)], "rod", "QT2")); o.append(dot(1280, 960))
    o.append(w([(1280, 960), (1280, 965), (1300, 965)], "rod", "QT2"))
    o.append(T(1278, 806, "QT-to-header cable, owned:", "fn", "end")); o.append(T(1278, 820, "3V3, GND, SDA, SCL to both", "fn", "end"))
    o.append(T(1390, 872, "100 nF at the ranger's VIN", "fn", "middle"))
    o.append(w([(1180, DY + DH), (1180, 1060), (1270, 1060), (1270, 1035), (1300, 1035)], "rod", "MA"))
    o.append(w([(1230, DY + DH), (1230, 1078), (1390, 1078), (1390, 1035), (1400, 1035)], "rod", "MB"))
    o.append(T(1390, 1096, "own leads; swap a pair to fix a direction", "fn", "middle"))

    o.append(T(20, 1082, "Paper design, 2026-11-09: Rev B's sheet (Mochi's electrics of 2026-11-07) less the lidar, its switch and its serial line; checked against the Seeed wiki, the Adafruit 6106 and 5580 guides,", "sub"))
    o.append(T(20, 1098, "the Hosyond 1.54\" header, the SparkFun 15451 page and the Pololu carrier page. Not built. The pin audit and the lane check in gen/crumb_build.py pass.", "sub"))

    bad, crossings = rt.check()
    for b in bad:
        print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    print(f"sheet: {len(rt.segs)} segments, {crossings} crossings drawn as hops")
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Crumb Rev C wiring sheet, every connection pin to pin">{M.SHEET_CSS}{"".join(o)}</svg>'


def write_all(png_dir=None):
    views, key = final_views()
    pair = size_pair()
    the_sheet = sheet()
    figs = lambda vs: '<div class="views">' + "".join(f"<figure>{svg}<figcaption>{esc(cap)}</figcaption></figure>" for svg, cap in vs) + "</div>"
    keyhtml = '<div class="key">' + "".join(f"<div><b>{n}</b><span>{esc(t)}</span></div>" for n, t in key) + "</div>"
    extra_css = PAGE_CSS + "\n" + STEEL_DK_CSS + "\nfigure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} figure.pair{max-width:660px} .rods td:first-child{white-space:nowrap}"
    pins_rows = [(h, str(g), n, esc(j)) for h, g, n, j in PINS]
    nets_rows = [(esc(a), esc(b), esc(c), esc(d), esc(e)) for a, b, c, d, e in NETS]
    budget_rows = [(esc(a), esc(b), f"{c} mA", f"{d}") for a, b, c, d in BUDGET]
    rods_rows = [(esc(p), str(q), s, f"{l}", esc(w)) for p, q, s, l, w in RODS]
    skin_rows = [(esc(a), esc(b), esc(c), esc(d)) for a, b, c, d in SKINS]
    parts_html = ""
    for group, rows in PARTS:
        parts_html += f"<h3>{esc(group)}</h3>" + tbl([(esc(q), A(u, esc(p)) if u else esc(p), esc(wh), esc(pr), esc(n)) for q, p, u, wh, pr, n in rows],
                                                     ["Qty", "Part", "Where", "Price", "Why, and what to check"], [1, 0, 0, 1, 0])
    mass_rows = [(esc(n), str(m)) for n, *_, m, note in PARTS_BOX if m] + [(esc(n), str(m)) for n, m, *_ in MASS_OTHER] + [("<strong>Total</strong>", f"<strong>≈ {MASS:.0f}</strong>")]
    changes = [
        ("Top", "the cage's top rail, 60 mm up", f"the lidar on the top side rails, its body to {REV_B['top']} mm", f"the cage's top rail again, {TOP:.0f} mm: {REV_B['top'] - TOP:.0f} lower than Rev B"),
        ("Sensing", "8×8 ranger on the brow; single-point ranger under the top rail, looking down past the nose", "the lidar on the roof, its plane 87 mm up, 360°; the single-point ranger on the brow, 40° down; the 8×8 set aside", f"no lidar: the single-point ranger on the brow, 40° down, sees the edge {EDGE_WARN:.0f} mm before the skid and anything standing in its cone; the camera; the bump"),
        ("Power", "cell straight to the boards; the XIAO's 100 mA charger", "the charger-boost's 5 V for the XIAO (Schottky), the lidar (switch) and the amp; motors on the cell; USB-C at 500 mA", f"the same charger-boost, its 5 V rail for the XIAO (Schottky) and the amp only: {RAIL5[0]} mA typical of 1 A; the lidar's switch is gone"),
        ("Pins", "D2 DC, D3 backlight, D6 8×8 enable, D7 button", "D2 lidar switch, D3 lidar serial in, D6 DC, D7 backlight; no button", "D6 DC, D7 backlight as Rev B; D2 and D3 free; the double tap is still the button"),
        ("Run time", "about 1.7 h roaming; 10–20 h to charge", "about 1 h roaming with the lidar spinning; 2.2 h to charge", f"about {RUN_ROAM:.1f} h roaming with the camera streaming, {RUN_PARK:.1f} h parked; {CHARGE_H} h to charge"),
        ("Size, mass", "72 × 56 × 60 mm, about 209 g", f"72 × 56 × {REV_B['top']} mm, about {REV_B['mass']} g; centre of mass {REV_B['ycom']} up", f"{OVERALL:.0f} × 56 × {TOP:.0f} mm, about {MASS:.0f} g; centre of mass {YCOM:.0f} up, {D_AX:.1f} ahead of the axle, {SKID_LOAD:.0f} g on the skid (the cage now weighed from its rod list, {CAGE_G} g where both carried 28)"),
        ("Colour", "bare boards: red, blue, green and black in the open cage", "ivory brass-sheet skins on every board (skipped for the first build) and ivory gear faces; black only in the lidar, the glass, the lens and the speaker", "the same skins; black now only in the glass, the lens and the speaker"),
        ("To buy", "everything in the bin but the XIAO", "three lines, all ordered 2026-11-08: the lidar kit, the P-MOSFET pack, the charger-boost", "nothing for Rev C as drawn; since 2026-11-10 one 8×8 ranger, just in case. The charger-boost stays Crumb's; the lidar kit and the P-MOSFET pack go to the shared bin, unallocated"),
    ]
    page = f"""<title>Crumb Build</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{extra_css}</style>
<main>
<header style="display:grid;gap:10px">
  <span class="eyebrow">Desk robot · Crumb · Rev C · step 1: the final build · drawn 2026-11-09, approved the same day · nothing built</span>
  <h1>Crumb Rev C: the brass cage, without the lidar</h1>
  <p class="lede">{OVERALL:.0f} × 56 × {TOP:.0f} mm, about {MASS:.0f} g: Crumb with the lidar off the roof. On 2026-11-09 the builder found the lidar too big and asked for it off both desk robots, so they stay small and cute. The lidar, its posts on the top rails, its 5 V switch and its serial line are gone, and the top comes down {REV_B['top'] - TOP:.0f} mm to the cage’s own rail. Everything else is Rev B’s, and nothing is left to buy.</p>
  <p class="dims">Millimetres · x right, y up from the desk, z forward · front, side (face right) and top (face up) · lighter = on the far wall · dashed = hidden · orange dashes the ranger’s cone</p>
</header>

<section>
  <h2>What it is</h2>
  <p>A cage of 1.0 mm {A(LINKS['rod10'], 'brass rod')}, 52 wide, 56 deep and 54 tall with r 3 corners, open on every face. Two {A(LINKS['n20'], 'N20 motors')} lie end to end on one axle 20 mm up and 7 mm back, and Crumb’s two {A(LINKS['gears'], '64-tooth steel gears')} ride on their shafts outside the posts, each with an ivory brass disc on its face so the steel shows only as a toothed rim. The {A(LINKS['ips'], '1.54" square screen')} fills the lower face in an ivory bezel; the {A(LINKS['xiao'], 'XIAO ESP32-S3 Sense')} stands behind it in an ivory sleeve with its lens on the brow, and the {A(LINKS['rng1'], 'edge ranger')} sits beside the lens looking 40° down at the desk ahead.</p>
  <p>Inside: the {A(LINKS['holder'], 'cell holder')} across the floor with the {A(LINKS['cell'], '16340 cell')} in it, the {A(LINKS['boost'], 'charger-boost')} flat on the tail floor with its USB-C out the back, the {A(LINKS['drv'], 'motor driver')} on the left wall, the {A(LINKS['amp'], 'amplifier')} and {A(LINKS['gauge'], 'fuel gauge')} on the right, the {A(LINKS['imu'], 'motion sensor')} on the tail floor, the {A(LINKS['spk'], 'speaker')} as the tail wall and the {A(LINKS['toggle'], 'toggle')} beside it. Nothing sits on the roof: the top is the cage’s own rail.</p>
  <p>Brass is the cage, the hubs and the skid, its own colour. Ivory is every skin: the {A(LINKS['sheet'], 'brass sheet')} cut to each board, Kapton inside, {A(LINKS['white'], 'canvas white')} outside. Black only in the screen’s glass, the lens and the speaker; steel only as the gears’ teeth; white wire along the rods. <strong>The builder skipped the brass sheet on 2026-11-08:</strong> the first build runs bare, its boards’ red, blue, green and black showing through the cage. The drawings show the finished look.</p>
</section>

<section>
  <h2>The final views</h2>
  {figs(views)}
  <h3>Key</h3>{keyhtml}
</section>

<section>
  <h2>What Rev C changes</h2>
  <figure class="pair">{pair}<figcaption>Rev B and Rev C from the front, to one scale. The lidar stood {REV_B['top'] - TOP:.0f} mm above the cage; without it Crumb is back to the cage’s own height.</figcaption></figure>
  {tbl([(esc(a), esc(b), esc(c), esc(d)) for a, b, c, d in changes], ["", "Crumb, 2026-10-31", "Rev B, approved 2026-11-08", "Rev C, approved 2026-11-09"], [0, 0, 0, 0])}
</section>

<section>
  <h2>Inside, and the stance</h2>
  <p>Every part is an axis-aligned box the script checks against every other and against the cage; nothing overlaps and nothing leaves it, so nothing rises above the top rail at {TOP:.0f} mm. The centre of mass lands {D_AX:.1f} mm ahead of the axle and {YCOM:.0f} mm up, {REV_B['ycom'] - YCOM:.0f} mm lower than Rev B’s, so Crumb rests on its nose skid with about {SKID_LOAD:.0f} g on it. Braking pitches it harder onto the skid and cannot lift the gears below {TIP_FWD:.1f} m/s²; accelerating forward would lift the skid above {TIP_BACK:.1f} m/s². The firmware ramps at {RAMP}.</p>
  <h3>Parts placed</h3>{tbl([(esc(n), f"{x[0]:g}..{x[1]:g}", f"{y[0]:g}..{y[1]:g}", f"{z[0]:g}..{z[1]:g}", str(m), esc(note)) for n, x, y, z, m, note in PARTS_BOX], ["Part", "x", "y", "z", "g", "Where and how"], [0, 1, 1, 1, 1, 0])}
  <h3>Mass</h3>{tbl(mass_rows, ["Part", "g"], [0, 1])}
  <p class="dims">The cage is weighed from its rod list now: {ROD10} mm of 1.0 mm brass is {ROD10_G:.0f} g, about {CAGE_G} g with the skid dome and the solder, where Crumb and Rev B carried 28. The bare first build is about 7 g lighter again: no skins, no ivory gear faces.</p>
</section>

<section>
  <h2>The cage, the rods and the skins</h2>
  <h3>Rod list</h3>{tbl(rods_rows, ["Piece", "Qty", "Stock", "Length, mm", "Where"], [0, 1, 1, 1, 0])}
  <p class="dims">About {ROD10} mm of 1.0 mm rod, 36 mm of hub tube and 5 of 4 mm tube, all owned. Solder with the Harris flux, rinse, neutralise, before any board comes near. The cage is bent as two 52 × 54 rectangles joined by four 56 mm rails; a paper template follows the approval. Nothing goes on the top rails now.</p>
  <h3>Skins</h3>{tbl(skin_rows, ["Part", "As sold", "Skin", "Window"], [0, 0, 0, 0])}
  <p class="dims">One sheet of 0.005 in brass makes them all. Cut with scissors, fold the driver’s return over a steel rule, line the inside with Kapton, spray the outside canvas white, two coats. A skin is held by two dots of hot glue at its corners and never reaches a rod. Deferred 2026-11-08: the first build is bare; fit the skins whenever the sheet comes.</p>
</section>

<section>
  <h2>Every wire, pin to pin</h2>
  <p>Rev B’s sheet less the lidar’s branch. One cell, one toggle, one boost, one brain. The cell rail (red) runs from the toggle through the fuel gauge into the charger-boost, and straight to the motor driver. The 5 V rail (brass) comes off the charger-boost’s pads and feeds the XIAO through a Schottky and the amplifier, nothing else. Everything else is 3.3 V from the XIAO on three buses: SPI to the screen, I²S to the amp, and one I²C chain through the gauge, the driver, the ranger and the motion sensor. D2 and D3, the lidar’s two pins, are free.</p>
  <figure class="sheet">{the_sheet}<figcaption>The wiring sheet. Every connection is traceable pin to pin; crossings hop. The lane check passes with the pins of different nets at least 12 px apart. The power chain in numbers sits where the lidar’s branch was.</figcaption></figure>
  <h3>Pin map, XIAO ESP32-S3 Sense (J3 cut)</h3>{tbl(pins_rows, ["Pin", "GPIO", "Net", "Job"], [1, 1, 1, 0])}
  <p class="dims">Fixed by the Sense board: camera on GPIO 10–18, 38–40, 47, 48; PDM microphone on 41 and 42; the SD slot’s chip select on 21. The microphone keeps I²S0 (PDM receive exists only there), the amp runs on I²S1. Nine header pins in use, two free; the double tap on the body is the button.</p>
  <h3>Every net, and why</h3>{tbl(nets_rows, ["Net", "From", "To", "Wire", "Why"], [1, 0, 0, 0, 0])}
</section>

<section>
  <h2>The budget</h2>
  {tbl(budget_rows, ["Load", "Rail", "Typical", "Peak, mA"], [0, 0, 1, 1])}
  <p>From the cell: about {I_ROAM / 1000:.2f} A roaming with the camera streaming, so about {RUN_ROAM:.1f} h on the full 950 mAh (Rev B, with the lidar spinning: about 1 h). Parked with the face on and the camera off, {I_PARK / 1000:.2f} A, about {RUN_PARK:.1f} h. Take a tenth off both for a real cell. The boost carries {RAIL5[0]} mA typical and {RAIL5[1]} peak of its 1 A, a margin Rev B did not have.</p>
  <p>A full charge at 500 mA takes about {CHARGE_H} h with the toggle on, since the toggle sits in the cell’s lead; Crumb keeps running on the lead. Speed: about 60 rpm at the cell’s voltage, 45 under load, {V_LOAD:.0f} cm/s on Ø40; it stops in about {STOP_MM:.0f} mm from that, against the {EDGE_WARN:.0f} mm the ranger gives it.</p>
</section>

<section>
  <h2>Parts</h2>
  <p>Nothing to buy for Rev C as drawn (one 8×8 ranger to buy just in case since 2026-11-10, in the parts list below): every part was checked on 2026-11-09 against the Amazon, DigiKey and Adafruit order mails. Three are still in the mail: the XIAO (Amazon, not shipped yet, by 11-11), the charger-boost (DigiKey, acknowledged 11-08, about 11-13 to 11-15) and the motion sensor 3-pack (Amazon, arriving 11-09). Everything else has been delivered. The lidar kit and the P-MOSFET pack (Amazon, arriving 11-09) are no longer Crumb’s and go to the shared bin, unallocated; the XS drone cannot carry the lidar. The order sheet is <code>CRUMB_ORDER.md</code>.</p>
  {parts_html}
</section>

<section>
  <h2>What the firmware needs</h2>
  <ul>
    <li>Boot order: Wi-Fi up, screen on, chain scanned (0x36, 0x5D, 0x29, 0x68); D2 and D3 set as inputs with pull-downs.</li>
    <li>Safety loop at 50 Hz: ranger over 110 mm or no target → brake, back 15 mm, turn; ranger under 70 mm (something standing in its cone) → stop, turn; motion sensor pitch or roll over 5° in 50 ms, or a bump → brake.</li>
    <li>Drive: ramps of {RAMP} m/s², the cap from the stall test, turns in place about the axle, reversing limited to 15 mm because nothing looks back.</li>
    <li>Face: Pip’s eyes at 240 × 240 on the square screen (ST7789, 26 MHz), backlight PWM with a night floor and a parked-off state. Sound on I²S1, cap 50. Double tap on the body = the button.</li>
    <li>Sleep: camera off, Wi-Fi on, the face dimmed; the gauge’s state of charge on the face.</li>
  </ul>
</section>

<section>
  <h2>Before power, with the meter</h2>
  {tbl([(esc(a), esc(b)) for a, b in CHECKS], ["Check", "How"], [0, 0])}
</section>

<section>
  <h2>Build order</h2>
  <ol>{''.join(f'<li>{esc(s)}</li>' for s in BUILD_ORDER)}</ol>
</section>

<section>
  <h2>Risks</h2>
  {tbl([(esc(a), esc(b)) for a, b in RISKS], ["Risk", "What is done about it"], [0, 0])}
</section>

<section>
  <h2>Re-checked, 2026-11-09</h2>
  <p>Rev B’s electrics were checked on 2026-11-07 and 2026-11-08 against the Seeed wiki, the Adafruit 6106 and 5580 guides, the SparkFun motor driver page and the Pololu carrier page. Rev C only takes things away, so the re-check is of what the lidar touched: the pins, the power chain, the run time, the mass and the balance.</p>
  {tbl([(esc(a), esc(b)) for a, b in CHECKED], ["What", "How"], [0, 0])}
</section>

<section class="pick">
  <h2>Approved 2026-11-09</h2>
  <p>Rev C, approved as drawn by the builder on 2026-11-09: Rev B as approved on 2026-11-08, without the lidar, its posts, its switch and its serial line. {OVERALL:.0f} × 56 × {TOP:.0f} mm, about {MASS:.0f} g, about {RUN_ROAM:.1f} h roaming on a charge, nothing to buy. Two things stay open and are easy to flip: ivory faces on the gears or bare steel, and the two free pins (the owned button or the 8×8 ranger could come back on them; neither is drawn). Next: step two (the physics page) and a 1:1 cage template, the bench tests in the build order, the cage.</p>
</section>
</main>"""
    OUT_HTML.write_text(page)
    print("wrote", OUT_HTML, OUT_HTML.stat().st_size, "bytes")

    # ---- the markdown record
    md = [f"# Crumb Rev C: step one, the final build (drawn and approved 2026-11-09)\n",
          f"**Approved as drawn 2026-11-09; nothing built.** Rev B (approved 2026-11-08) without the lidar, at the builder's word of 2026-11-09: the lidar is too big, Crumb should look cute (\"remove the LiDAR for both projects\"). "
          f"Gone: the lidar, its three posts on the top rails, its P-MOSFET switch and its serial line; the top comes down from {REV_B['top']} mm to the cage's {TOP:.0f}. "
          f"Kept: Crumb's brass cage and gears, the square screen, and the rest of Rev B's electrics; the charger-boost still makes the 5 V rail, now for the XIAO and the amplifier only. Nothing to buy for Rev C as drawn; one 8×8 ranger to buy just in case (2026-11-10). "
          f"Page `pages/crumb-build.html`, generated by `pages/gen/crumb_build.py` (geometry, electrics, parts, checks and, from Rev C, Crumb's own wiring sheet live there; it borrows the router and symbols from `mochi_build.py`; "
          f"the overlap audit, the pin audit and the sheet's lane check must pass for it to write). Order sheet `CRUMB_ORDER.md`.\n",
          "## In numbers\n",
          f"- Envelope {OVERALL:.0f} W × 56 D × {TOP:.0f} H mm (Rev B {REV_B['top']} H); cage 52 × 56 × 54 (rods at x ±26, z −29..27, y 6..60, r 3); gears Ø40 × 9 at axle 20, z −7; skid at z +24; clearance 6.\n"
          f"- Mass about {MASS:.0f} g; centre of mass {D_AX:.1f} mm ahead of the axle, {YCOM:.0f} mm up; {SKID_LOAD:.0f} g on the skid; the skid lifts above {TIP_BACK:.1f} m/s² forward, the gears above {TIP_FWD:.1f} braking.\n"
          f"- Power: one 950 mAh 16340 → toggle → fuel gauge → charger-boost; 5 V rail {RAIL5[0]} mA typical, {RAIL5[1]} peak of 1 A (the XIAO through the Schottky, the amp); the motors on the cell rail.\n"
          f"- Run time about {RUN_ROAM:.1f} h roaming with the camera streaming ({I_ROAM:.0f} mA from the cell), about {RUN_PARK:.1f} h parked ({I_PARK:.0f} mA); charge about {CHARGE_H} h at 500 mA, toggle on.\n"
          f"- Edge ranger: sensor at ({RNG_EYE[0]}, {RNG_EYE[1]}, {RNG_EYE[2]}), 40° down, 27° cone: desk {RAYS['steep']['ahead_face']:.0f}–{RAYS['shallow']['ahead_face']:.0f} mm ahead of the face, paths {RAYS['steep']['path']:.0f}–{RAYS['shallow']['path']:.0f} mm; the edge seen {EDGE_WARN:.0f} mm before the skid, {WHEEL_WARN:.0f} before the wheels; edges within about {ANGLE_L:.0f}° of head-on caught before a wheel reaches them.\n"
          f"- Speed about {V_LOAD:.0f} cm/s; stops in {STOP_MM:.0f} mm. Pins: nine in use, D2 and D3 free.\n",
          "## Parts placed (mm, axis-aligned boxes: x, y, z)\n", "| Part | x | y | z | g | Note |", "| --- | --- | --- | --- | ---: | --- |"]
    for n, x, y, z, m, note in PARTS_BOX:
        md.append(f"| {n} | {x[0]:g}..{x[1]:g} | {y[0]:g}..{y[1]:g} | {z[0]:g}..{z[1]:g} | {m} | {note} |")
    md += ["", "## Mass\n", "| Part | g |", "| --- | ---: |"] + [f"| {n} | {m} |" for n, *_, m, note in PARTS_BOX if m] + [f"| {n} | {m} |" for n, m, *_ in MASS_OTHER] + [f"| **Total** | **≈ {MASS:.0f}** |"]
    md += ["", f"The cage is weighed from its rod list now: {ROD10} mm of 1.0 mm brass is {ROD10_G:.0f} g, about {CAGE_G} g with the skid dome and the solder, where Crumb and Rev B carried 28. The bare first build is about 7 g lighter again (no skins, no gear faces)."]
    md += ["", "## What Rev C changes\n", "| | Crumb, 2026-10-31 | Rev B, approved 2026-11-08 | Rev C, approved 2026-11-09 |", "| --- | --- | --- | --- |"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in changes]
    md += ["", "## Rods\n", "| Piece | Qty | Stock | mm each | Where |", "| --- | ---: | --- | ---: | --- |"] + [f"| {p} | {q} | {s} | {l} | {w} |" for p, q, s, l, w in RODS]
    md += ["", "## Skins (0.005 in brass, Kapton inside, canvas white outside)\n", "| Part | As sold | Skin | Window |", "| --- | --- | --- | --- |"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in SKINS]
    md += ["", "## Pin map (XIAO ESP32-S3 Sense, J3 cut)\n", "| Pin | GPIO | Net | Job |", "| --- | --- | --- | --- |"] + [f"| {h} | {g} | {n} | {j} |" for h, g, n, j in PINS]
    md += ["", "## Nets\n", "| Net | From | To | Wire | Why |", "| --- | --- | --- | --- | --- |"] + [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in NETS]
    md += ["", "## Budget\n", "| Load | Rail | Typical mA | Peak mA |", "| --- | --- | ---: | ---: |"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in BUDGET]
    md += ["", "The power chain in numbers (also on the sheet):", ""] + [f"- {s}" for s in POWER_LINES]
    md += ["", "## Parts\n"]
    for group, rows in PARTS:
        md += [f"### {group}\n", "| Qty | Part | Where | Price | Note |", "| --- | --- | --- | --- | --- |"] + [f"| {q} | [{p}]({u}) | {wh} | {pr} | {n} |" if u else f"| {q} | {p} | {wh} | {pr} | {n} |" for q, p, u, wh, pr, n in rows] + [""]
    md += ["## Before power\n"] + [f"- **{a}.** {b}" for a, b in CHECKS] + ["", "## Build order\n"] + [f"{i + 1}. {s}" for i, s in enumerate(BUILD_ORDER)] + ["", "## Risks\n"] + [f"- **{a}.** {b}" for a, b in RISKS]
    md += ["", "## Re-checked, 2026-11-09\n"] + [f"- **{a}.** {b}" for a, b in CHECKED]
    md += ["", "## Baked in, easy to flip\n", "1. Ivory faces on the gears, or bare steel.", "2. D2 and D3 left free: the owned button (D3) or the 8×8 ranger to buy (D2, its LPn) could take them.", ""]
    md += ["## History\n", "- 2026-10-31: Crumb drawn (`DESIGN.md`, page Desk Robot Crumb): the cage, the gears, the square screen, the 8×8 ranger, no lidar.",
           "- 2026-11-07: Rev B drawn: Crumb's cage with Mochi's lidar and electrics, no cardstock. Approved as drawn 2026-11-08 and confirmed point by point the same day; the lidar kit, the P-MOSFET pack and the charger-boost ordered 2026-11-08; the brass sheet skipped.",
           "- 2026-11-09: Rev C drawn and approved as drawn the same day (\"Approve Rev C\"): the lidar removed at the builder's word (too big; both desk robots stay small and cute). The lidar kit and the P-MOSFET pack go to the shared bin; the charger-boost stays.", "",
           f"- 2026-11-10: the edge worked through against the wheels (seen {WHEEL_WARN:.0f} mm before them; edges within about {ANGLE_L:.0f}° of head-on caught; alongside and behind are the drive loop's four rules), pushing small things assessed (under about {PUSH_G:.0f} g and {UNDER_MM:.0f} mm tall; a bumper rod for a Rev D), and one 8×8 ranger put on the list to buy just in case, the owned spare being the rover's."]
    OUT_MD.write_text("\n".join(md))
    print("wrote", OUT_MD)

    # ---- the order sheet
    order = f"""# Crumb Rev C: the order (Rev C approved 2026-11-09; Rev B approved and ordered 2026-11-08)

**Nothing to buy for Rev C as drawn; one 8×8 ranger to buy just in case, decided 2026-11-10 (its section below).** Rev B's three lines were ordered on 2026-11-08 and stay ordered; no cart or order is touched. On 2026-11-09 the
builder took the lidar off Crumb (and off the rover): it is too big for a small, cute desk robot. Where each Rev B line goes now:

| Line | Ordered | Rev C, 2026-11-09 |
| --- | --- | --- |
| Adafruit bq25185 charger with 5 V boost (6106) | DigiKey sales order 102777448, $15.18, shipped 11-09 by USPS, about 11-12 to 11-14 | **Stays Crumb's.** Its charger (500 mA, about {CHARGE_H} h, toggle on) and its 5 V rail, now for the XIAO (through the Schottky) and the amplifier only: {RAIL5[0]} mA typical, {RAIL5[1]} peak of its 1 A. The boost is still in use. |
| LDROBOT LD19 lidar, the youyeetoo FHL-LD19 kit | Amazon order 114-7956116-1377847, $86.43 with the MOSFETs, arriving 2026-11-09 | **No longer Crumb's.** To the shared bin in its box, unallocated until the builder names a project. Not the XS drone: 47 g on a 34 g drone with a thrust-to-weight of 2.0 cannot fly. |
| P-channel MOSFET AO3401A, Bridgold 100-pack | the same Amazon order | **No longer Crumb's.** It was the lidar's switch; all 100 spare, to the shared bin. |
| K&S 0.005 in brass sheet, 6-pack | skipped 2026-11-08, in Amazon's Saved for Later | Unchanged: the skins, whenever they are wanted. |

Not needed any more for Crumb: the AO3400A N-MOSFET from the drone's pack (it drove the lidar switch; it stays in the drone bin), the 1 kΩ,
the 100 kΩ, one 10 kΩ, the 100 µF and one 100 nF.

## Just in case, 2026-11-10: one 8×8 ranger

The builder asked whether Crumb can roam the desk without falling off on the single-zone ranger alone, and whether it could push small
things while seeing tens of centimetres ahead. The answers are in `CRUMB_BUILD.md` under Risks: head-on yes, the edge seen {WHEEL_WARN:.0f} mm
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
"""
    OUT_ORDER.write_text(order)
    print("wrote", OUT_ORDER)

    if png_dir:
        png_dir = pathlib.Path(png_dir); png_dir.mkdir(parents=True, exist_ok=True)
        css = (HERE / "check_style.css").read_text() + STEEL_DK_CSS + " svg.blk text{font-size:12px} " + M.SHEET_CSS.replace("<style>", "").replace("</style>", "").replace("var(--fg)", "#23211c").replace("var(--muted)", "#6b665a").replace("var(--panel)", "#faf8f2").replace("var(--brass-dk)", "#7d6132").replace("var(--brass)", "#b4904f").replace("var(--warn)", "#98351e")
        items = [(f"final_{i}", svg) for i, (svg, cap) in enumerate(views)] + [("pair", pair), ("sheet", the_sheet)]
        for name, svg in items:
            p = png_dir / f"{name}.html"
            wide = 1540 if name == "sheet" else 720
            p.write_text(f"<!doctype html><meta charset=utf-8><style>{css}</style><div style='width:{wide}px'>{svg}</div>")
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--window-size={wide + 20},{1130 if name == 'sheet' else 1000}",
                            f"--screenshot={png_dir / (name + '.png')}", f"file://{p}"], check=True, capture_output=True, timeout=90)
        print("rendered", png_dir)


if __name__ == "__main__":
    write_all(sys.argv[sys.argv.index("--png") + 1] if "--png" in sys.argv else None)
