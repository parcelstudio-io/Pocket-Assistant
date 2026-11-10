"""Mochi, the desk robot picked on 2026-11-07: step one, the final build.

    python3 mochi_build.py              writes ../mochi-build.html and ../../MOCHI_BUILD.md
    python3 mochi_build.py --png DIR    also renders every figure to PNG in DIR (headless Chrome) for checking
    python3 mochi_build.py --wheel white|gear   Rev A (Pololu white wheels, approved 2026-11-07) or Rev B (Crumb's steel gears, the default)

Everything on the page derives from the tables below: the geometry (millimetres, x right, y up from the desk, z forward),
PINS, NETS, PARTS, BUDGET and CHECKS. The script refuses to write if the pin audit, the clearance audit of the parts or the
wiring sheet's lane check fails. Nothing has been built."""
from __future__ import annotations
import html, math, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import concepts as C                      # the View class, the part sizes, lidar/wheel/eye helpers
from concepts import View, desk, wheel_side, wheel_edge, lidar_front, lidar_top, eyes_round, ROD, ROD_THIN, HID, HID_FILL, SKIN, BEAM, SCAN, D2R
from page import CSS as PAGE_CSS, L as LINKS, A

OUT_HTML = HERE.parent / "mochi-build.html"
OUT_MD = HERE.parent.parent / "MOCHI_BUILD.md"
esc = html.escape

# ============================================================================= geometry (mm)
BX = 28.0                                   # hoop planes x = ±28 (1.5 mm rod centreline); skin inner faces at ±27.25
BZ0, BZ1, BY0, BY1, R = -28.0, 28.0, 5.0, 60.0, 4.0     # corner r 4: the flat top (z ±24) must take the 46.3 mm flange
# ---- the wheel. Rev A (approved 2026-11-07) rides on Pololu 32×7 white wheels. Rev B, asked the same evening ("a metal gear instead"),
# rides on Crumb's HSP 11184 steel spur gears: 64 teeth, module 0.6, Ø39.6 over the teeth (the seller draws 40), root Ø36.9, 5 mm bore,
# 9 mm over the boss, about 32 g each, on hubs of 5 mm over 4 mm brass tube; each faced with an ivory card disc. configure() sets the rest.
WHEELS = {
    "white": dict(r=15.5, w=7.0, x0=29.5, az=0.0, mass=6,  plate=7.0, boss_w=0.0, boss_d=0.0,  rev="Rev A", pair="Pololu 32×7 white wheels"),
    "gear":  dict(r=20.0, w=9.0, x0=29.5, az=1.0, mass=65, plate=4.0, boss_w=5.0, boss_d=12.0, rev="Rev B", pair="Crumb's 64-tooth steel gears"),
}
GEAR_T, GEAR_MOD = 64, 0.6
GEAR_FACE_R = (GEAR_MOD * GEAR_T - 2.5 * GEAR_MOD) / 2 - 0.25   # the ivory disc stops a quarter millimetre inside the root circle
WHEEL = "gear"
WR, WW, WX0 = 15.5, 7.0, 29.5               # wheel radius, width over the boss, inner face x; set by configure() → OVERALL = 2 (WX0 + WW)
AY, AZ = 16.0, 0.0                          # axle: height WR + 0.5; Rev B puts it 1 mm forward so the heavier wheels leave 2.3 mm of tail
OVERALL, WD, CRADLE_Y = 73.0, 31.0, 10.5
V_FREE = V_LOAD = TIP = ROD10 = 0.0
LZ = 0.5                                    # lidar centre z: the flange (46.3 deep) sits inside the flat top, z −22.65..+23.65
LY_FL = BY1 - C.LIDAR_FL_T - 0.5            # flange underside y 58.2; body from 59.5
LY_BODY = BY1 - 0.5
LID_TOP = LY_BODY + C.LIDAR_H - C.LIDAR_FL_T
SCAN_Y = LY_FL + C.LIDAR_SCAN
FACE_Y = 31.0

# every solid part as an axis-aligned box: name, (x0, x1), (y0, y1), (z0, z1), mass g, note
PARTS_BOX_A = [   # Rev A positions (axle 16, z 0); configure() moves the motors, the driver and the amp with the axle
    ("motor L",      (-26.5, -2.5), (11, 21),     (-6, 6),       10, "N20, shaft out through the left disc"),
    ("motor R",      (2.5, 26.5),   (11, 21),     (-6, 6),       10, "N20, shaft out through the right disc"),
    ("cell holder",  (-21.5, 21.5), (22, 40),     (-27, -13),    28, "on its side, opening to the back hatch; cell inside"),
    ("motion sensor",(-10, 11),     (41, 44),     (-27, -11),    2,  "GY-521 flat on the holder's top face"),
    ("lidar switch", (-8, 2),       (44, 48),     (-26, -16),    1,  "P- and N-MOSFET and three resistors on fish paper, on the motion sensor"),
    ("charger-boost",(-9.55, 9.55), (48.4, 53.5), (-27, 2.2),    5,  "flat, parts up, USB-C at the back end through the skin, glued on the stack below"),
    ("charger-boost tall parts", (-9.55, 9.55), (53.5, 57.8), (-18, 2.2), 0, "terminal block and JST at the front end, under the flange"),
    ("toggle",       (15, 21),      (47, 53),     (-27, -17),    3,  "bushing through the back skin at (18, 50)"),
    ("button",       (-21, -15),    (47, 53),     (-27, -22),    1,  "tactile, through the back skin at (−18, 50)"),
    ("motor driver", (17, 27),      (22, 47.4),   (-12, 13.4),   8,  "standing on the right wall, terminals inward"),
    ("amp",          (-27, -22),    (22, 41),     (-2, 14),      3,  "standing on the left wall"),
    ("fuel gauge",   (-26, -0.6),   (6.1, 10.6),  (-24.3, -6.5), 3,  "flat on the floor, left back, behind the cradle rod"),
    ("speaker",      (4, 24),       (6, 10.9),    (-22, -9),     5,  "flat on the floor across the back right, firing down through a slot"),
    ("XIAO stack",   (-9, 9),       (28, 49),     (12, 22),      10, "standing behind the screen, USB-C up"),
    ("round screen", (-18.75, 18.75), (12.25, 49.75), (24.2, 27.2), 12, "Ø37.5 board against the front skin; its tab and plug below, to y 11"),
    ("screen plug",  (-5, 5),       (11, 14),     (20.2, 24.2),  0,  "PH2.0 plug on the tab's back"),
    ("camera module",(-9, -1),      (50, 57),     (19.5, 25),    1,  "inside the top-front rounding, lens through the arc looking 25° up"),
    ("edge ranger",  (9.4, 27.2),   (46.2, 57.2), (15.3, 24.1),  1,  "tilted 40° down behind the round board's rim, beam out through a slot beside the window"),
    ("lidar flange", (-27, 27),     (58.2, 59.5), (LZ - 23.15, LZ + 23.15), 0, "the three-lug plate under the top skin, on two cross rods"),
    ("lidar body",   (-19.3, 19.3), (59.5, LID_TOP), (LZ - 19.3, LZ + 19.3), 45, "black, Ø38.6, 33.5 tall above the skin"),
]
MASS_OTHER_A = [("wheels, pair", 6), ("brass: two hoops, rails, cradles, shelf, ring, domes", 13), ("card skins, paint, tape", 5), ("wire, capacitors, glue, Kapton", 8)]
PARTS_BOX, MASS_OTHER = PARTS_BOX_A, MASS_OTHER_A
BODY_INNER = ((-27.25, 27.25), (5.75, 59.25), (-27.25, 27.25))


def overlap(a, b):
    (ax, ay, az), (bx, by, bz) = a, b
    return all(min(p[1], q[1]) - max(p[0], q[0]) > 0.05 for p, q in ((ax, bx), (ay, by), (az, bz)))


def audit_geometry():
    """No two solids share space, and everything but the lidar, wheels and skids sits inside the skin."""
    boxes = [(n, (x, y, z)) for n, x, y, z, m, note in PARTS_BOX]
    bad = []
    for i, (n1, b1) in enumerate(boxes):
        for n2, b2 in boxes[i + 1:]:
            if overlap(b1, b2):
                bad.append(f"{n1} overlaps {n2}")
    rin = R - 1.0   # the skin's inner corner radius: rod radius 0.75 and card 0.3 inside the hoop's centreline
    def inside_profile(z, y):
        if not (BODY_INNER[2][0] <= z <= BODY_INNER[2][1] and BODY_INNER[1][0] <= y <= BODY_INNER[1][1]):
            return False
        cz = (BZ1 - R) if z > 0 else (BZ0 + R); cy = (BY1 - R) if y > (BY0 + BY1) / 2 else (BY0 + R)
        if abs(z) > abs(cz) and ((y > cy) if cy > (BY0 + BY1) / 2 else (y < cy)):
            return (z - cz) ** 2 + (y - cy) ** 2 <= rin ** 2 + 1e-6
        return True
    for n, (x, y, z) in boxes:
        if n == "lidar body":
            continue
        if n == "lidar flange":
            if z[0] < -(BZ1 - R) or z[1] > (BZ1 - R):
                bad.append("lidar flange runs into the top roundings")
            continue
        ok = x[0] >= BODY_INNER[0][0] and x[1] <= BODY_INNER[0][1] and all(inside_profile(zz, yy) for zz in z for yy in y)
        if not ok:
            bad.append(f"{n} pokes out of the skin")
    # the front flat zone (y 11..54) must hold the screen board
    scr = next(b for n, b in boxes if n == "round screen")
    if scr[1][0] < BY0 + R or scr[1][1] > BY1 - R:
        bad.append("screen board outside the flat front zone")
    assert not bad, "; ".join(bad)
    m_parts = sum(m for *_, m, note in PARTS_BOX) + sum(m for _, m in MASS_OTHER)
    # centre of mass
    wm = MASS_OTHER[0][1]   # the wheels sit on the axle
    sz = sum(m * (z[0] + z[1]) / 2 for n, x, y, z, m, note in PARTS_BOX) + wm * AZ + 13 * -2 + 5 * 0 + 8 * -5
    sy = sum(m * (y[0] + y[1]) / 2 for n, x, y, z, m, note in PARTS_BOX) + wm * AY + 13 * 30 + 5 * 32 + 8 * 35
    return m_parts, sz / m_parts, sy / m_parts


MASS, ZCOM, YCOM = audit_geometry()   # Rev A at import; configure() at the end of the module recomputes for the chosen wheel

# ============================================================================= the contract: pins and nets
PINS = [  # (header, gpio, net, job)
    ("D0", 1, "CLK", "screen SPI clock, 40 MHz capable; 26 MHz used"),
    ("D1", 2, "DIN", "screen SPI data"),
    ("D2", 3, "LID_EN", "lidar 5 V switch: high = lidar on. Strapping pin only when the JTAG eFuse is burned; it is not. 100 kΩ pull-down keeps the lidar off through boot"),
    ("D3", 4, "LID_TX", "lidar serial in (UART1 RX, 230400 8N1, 3.3 V)"),
    ("D4", 5, "SDA", "I²C data: gauge 0x36, driver 0x5D, ranger 0x29, motion sensor 0x68"),
    ("D5", 6, "SCL", "I²C clock, 400 kHz"),
    ("D6", 43, "DC", "screen data/command. GPIO43 is UART0 TX: the ROM prints here at boot, harmless on a screen that is not initialised yet"),
    ("D7", 44, "BL", "screen backlight PWM. GPIO44 is UART0 RX, pulled up at boot: backlight on during boot, dimmed by the app after"),
    ("D8", 7, "BCLK", "I²S1 bit clock to the amp (SD-slot pin, J3 cut)"),
    ("D9", 8, "LRC", "I²S1 word clock to the amp"),
    ("D10", 9, "I2S_DIN", "I²S1 data to the amp"),
]
RESERVED = {"camera": {10, 11, 12, 13, 14, 15, 16, 17, 18, 38, 39, 40, 47, 48}, "pdm mic": {41, 42}, "sd slot (J3 cut, empty)": {21}}


def audit_pins():
    used = {}
    for hdr, g, net, job in PINS:
        assert g not in used, f"GPIO{g} twice"
        used[g] = hdr
    for owner, gs in RESERVED.items():
        assert not (gs & set(used)), f"clash with the {owner}"
    assert len(used) == 11
    return used


audit_pins()

NETS = [  # (net, from, to, wire, why)
    ("CELL+", "holder + lead (red)", "toggle, middle lug", "the holder's own 26 AWG lead", "Meter red to + before the cell goes in. The toggle breaks the cell's + lead; nothing is live with it off."),
    ("BAT+", "toggle, outer lug", "gauge JST A (+) · driver VIN terminal", "26 AWG; a JST-PH pigtail into the gauge", "The switched cell rail, 3.0–4.2 V. The gauge sits in the cell lead; the motors take the cell straight so stall current never loads the boost."),
    ("BAT+ (through the gauge)", "gauge JST B (+)", "charger-boost JST BAT (+)", "JST-PH pigtail, 26 AWG", "The gauge's two JST ports are a pass-through: cell in one, charger on the other. Polarity by meter, not by wire colour."),
    ("GND", "holder − lead (black), the star", "gauge JST A (−); charger-boost JST BAT (−); driver GND terminal; XIAO GND pin; amp GND; screen GND; lidar GND (pin 3); ranger GND; motion sensor GND; switch board GND", "26 AWG for the power returns, 30 AWG for the signal grounds", "One ground, one star at the holder. The brass is not a conductor: every rod keeps 2 mm from every net, Kapton on every board back that faces brass."),
    ("5V", "charger-boost terminal block +", "Schottky anode (to the XIAO) · P-MOSFET source (to the lidar) · amp VIN · 220 µF +", "26 AWG", "The boosted rail, 5.0–5.2 V, 1 A. Live whenever the toggle is on, with or without USB. Its EN pad stays open: the board's own pull-up keeps the boost on."),
    ("5V_XIAO", "Schottky cathode", "XIAO 5V pin", "26 AWG, the diode heat-shrunk in the lead", "The XIAO's 5V pin is its USB VBUS with no diode on the board. The Schottky lets the rail feed it and stops a PC's USB from feeding the rail, so you flash with the toggle off. About 0.3 V drop; the XIAO's buck is happy from 3.6 V."),
    ("LID_5V", "P-MOSFET drain", "lidar P5V (pin 4) · 100 µF + 100 nF to GND", "26 AWG into the kit's ZH1.5 pigtail", "Switched 5 V for the lidar, on 1 s after boot: the boost chip stalls if 300 mA hangs on it at power-up. The same switch is the lidar's sleep."),
    ("LID_EN", "XIAO D2 (GPIO3)", "1 kΩ → N-MOSFET gate; 100 kΩ gate to GND", "30 AWG", "High turns the N-MOSFET on, which pulls the P-MOSFET's gate to ground against its 10 kΩ pull-up to 5 V: Vgs −5 V, fully on. Low or floating at boot: lidar off."),
    ("LID_TX", "lidar Tx (pin 1)", "XIAO D3 (GPIO4)", "the pigtail's wire, then 30 AWG", "One-way data at 230400 baud, 3.3 V levels, no shifting. The PWM pin (2) stays open and insulated: internal 10 Hz."),
    ("3V3", "XIAO 3V3 pin", "screen VCC (10 µF + 100 nF); ranger VIN; motion sensor VCC; gauge VIN; driver logic through the Qwiic chain", "30 AWG; the QT cables carry it along the chain", "The XIAO's buck gives 600–700 mA; the camera and Wi-Fi take up to 350 of it, the screen 31, the sensors 30, the chain's logic 10."),
    ("SDA / SCL", "XIAO D4 / D5", "gauge SDI / SCL pads → gauge QT → driver Qwiic 1 (100 mm QT cable) → driver Qwiic 2 → QT-to-header cable → ranger SDA/SCL and motion sensor SDA/SCL", "30 AWG to the gauge; QT cables; the header cable's wires", "One chain, four devices. Cut the driver's pull-up jumper; the gauge's and the ranger's 10 kΩ pairs and the motion sensor's 2.2 kΩ pair remain: about 1.6 kΩ, 2 mA per low, fine at 400 kHz."),
    ("CLK / DIN / DC / BL", "XIAO D0 / D1 / D6 / D7", "screen CLK / DIN / DC / BL", "the screen's own 8-wire PH2.0 lead", "Four pins for a 240 × 240 colour face. CS to GND (only SPI device). RST through 10 kΩ to 3V3 with 1 µF to GND: a power-on reset, then software resets."),
    ("BCLK / LRC / I2S_DIN", "XIAO D8 / D9 / D10", "amp BCLK / LRC / DIN", "30 AWG", "I²S1. SD stays on the module's pull-up (the chip sleeps when the clock stops), GAIN open (9 dB). Volume cap 50 on the 5 V rail, where Crumb's 65 was on the cell."),
    ("SPK+ / SPK−", "amp OUT+ / OUT−", "speaker", "the speaker's own leads", "A bridged output: neither lead is ground. Never clip a scope ground to either."),
    ("MA / MB", "driver A1-A2 / B1-B2", "motor L / motor R leads", "the motors' own leads, 60 mm", "Swap a pair if a wheel turns the wrong way. No GPIO goes to the motors."),
    ("motion sensor AD0", "GY-521 AD0", "GND", "a solder blob", "Address 0x68. INT stays open; bumps are read by polling at 100 Hz."),
    ("ranger XSHUT / GPIO1", "open", "", "", "The only ST ranger on the bus keeps its default 0x29; nothing to re-address."),
]

BUDGET = [  # (load, rail, typical mA, peak mA)
    ("XIAO with the camera streaming over Wi-Fi", "5 V, through its own buck", 220, 330),
    ("Lidar spinning", "5 V, switched", 290, 300),
    ("Amp at cap 50 into the 8 Ω speaker", "5 V", 30, 300),
    ("Screen with the backlight at half", "3V3 (counted in the XIAO's draw)", 25, 31),
    ("Ranger, motion sensor, gauge, driver logic", "3V3 (counted in the XIAO's draw)", 40, 60),
    ("5 V rail, all of it", "boost, 1 A", 560, 950),
    ("Two motors, running / one stalled", "cell rail", 150, 700),
]

CHECKS = [
    ("Holder and toggle", "Cell in, nothing else connected: meter DC V across the toggle's outer lug and the holder's − lead, toggle on: +3.6 to +4.2 V. Negative means the leads are swapped; fix it at the holder."),
    ("Gauge pass-through", "Cell through the gauge, toggle on: the same voltage on the second JST, + on the pin that goes to the charger's BAT +. Generic pigtails are often wired opposite to Adafruit's convention: meter, then crimp."),
    ("Charger-boost alone", "Only the cell on BAT. Terminal block: 5.0–5.2 V between + and −. The charge-rate jumper on the back is cut (500 mA). EN left open."),
    ("No shorts, unpowered", "Toggle off, cell out. Ω: 5V rail to GND and BAT+ to GND above 1 kΩ and climbing (the capacitors); 3V3 to GND above 1 kΩ; 5V to BAT+ open."),
    ("Lidar switch", "Toggle on, lidar unplugged: P-MOSFET drain reads 0 V. Short the switch's input to 3V3: drain reads the rail. Release: 0 V again. Then plug the lidar in and repeat; it spins up within a second of the input going high."),
    ("Schottky direction", "Rail on, USB out: XIAO 5V pin reads rail minus 0.3 V. Toggle off, USB in: the XIAO boots and the rail reads 0 V (the diode blocks)."),
    ("Screen and lens", "Before the skin closes: a frame on the screen at 26 MHz, backlight PWM from 5 % to 100 %; the camera demo shows the desk ahead with the lens tilted 25° up; the ranger reads the desk at 50–90 mm ahead from its brow slot."),
    ("Edge test, wheels off the desk", "Drive loop running, a board under the ranger: pull it away and both motors stop within one 20 ms tick; tip the body 5° and the motion sensor stops them too."),
    ("Current, the real numbers", "Everything on the cell: idle with the face on, streaming, driving, lidar on. Log them next to the budget table; the run-time claims stand or fall on them."),
]

def build_order():
    gear = WHEEL == "gear"
    return [
        "Bench tests on jumpers first: the chain scan (0x36, 0x5D, 0x29, 0x68), the screen, the lidar packets on D3, the switch, the amp, the motors from the bench supply at 3.7 V with a 0.5 A limit (stall current sets the drive cap).",
        "Bend the two hoops on the paper template (56 × 55, r 4); solder each closed with a 6 mm lap. Solder the floor rail and the keel between them; the two cradle Us; the shelf; the two flange Us; W1 for the screen.",
        "Cut the card: the wrap 209 × 54.5 with its openings, the two discs with their Ø8 shaft holes" + (", two Ø36 face discs for the gears" if gear else "") + ". Spray canvas white, two coats, dry overnight. Clear tape over the faces fingers touch.",
        ("Hubs: 9 mm of 5 mm tube over 9 mm of 4 mm tube, soldered, one pressed into each gear with the boss inboard; spin each gear on a motor shaft and true it (1 mm of wobble at the rim is a waddle). Motors on the cradles, shafts out through the discs; gears on, the inner tube squeezed into the shaft's flat; ivory faces last. The body must sit level on both domes with both gears touching."
         if gear else
         "Motors on the cradle, shafts out; press the wheels on; the body must sit level on both domes with both tyres touching."),
        "Holder on the shelf, opening back; motion sensor, switch board and charger-boost stacked on it; toggle and button on the back; driver on the right wall; amp on the left; gauge and speaker on the floor.",
        "Face: screen on W1, XIAO behind it, camera module and ranger inside the top-front rounding. Lidar flange on its cross rods through the top skin's hole; brim ring over the join.",
        "Wire to the sheet; Kapton on every board back toward brass; meter every rod against every net; then the checks above in order.",
        "First roll on a towel on the floor, not the desk.",
    ]


def build_risks():
    d = AZ - ZCOM
    rows = [
        ("The 1 A boost against the real draw", "Typical 560 mA, peaks near 950 with the amp loud and the lidar spinning up. If the rail dips, the fix is in firmware first (amp cap, lidar start after Wi-Fi is up); the fallback board is the bq24074 charger with a Pololu U3V16F5 step-up."),
        ("The lidar's flange", "Its 54 × 46 mm plate is read from the LD19 drawing; the STL-19P shares the housing. Caliper it on arrival: the cross rods move with it, and the top skin's hole is cut last."),
        ("A high lidar plane", "86 mm up: it sees mugs, hands, laptop lids and monitor feet, not books or phones. The ranger, the camera and the bump sensor own the low desk."),
        ("Wi-Fi inside card and brass", "Two hoops are not a cage; the antenna flex goes flat on the inside of the top skin at the front. Compare RSSI against the bare board before closing up."),
        ("Weight at the top", f"45 g of lidar at 76 mm puts the centre of mass {YCOM:.0f} mm up and {d:.1f} mm behind the axle: the tail dome carries about {MASS * d / 25:.0f} g and the nose dome, 1 mm up, bounds any pitch. Ramp drive at 0.4 m/s² ({TIP:.1f} lifts the tail); the only hard stop is the edge stop, which pitches it onto the nose dome."
         + (" The gears put 59 g more on the axle, which is why it moved 1 mm forward: left at z 0 the tail would lift at 0.44." if WHEEL == "gear" else "")),
        ("No button", "Eleven pins, eleven jobs. A double tap on the body, read by the motion sensor, is the button; the toggle is the only switch."),
        ("Card as a shell", "Cardstock sprayed on both sides and sealed at the edges stays flat; it will dent if dropped. The brass carries every load; the card carries only itself, the camera module and the ranger."),
    ]
    if WHEEL == "gear":
        rows += [
            ("Gear on hub on shaft", "Three fits in series, and Crumb's recipe wanted a drop of CA, which the bench does not have. The 4 mm tube's bore is the shaft's 3 mm: press it on and squeeze a dimple into the D-flat with pliers so it drives; the 5 mm tube soldered over it fills the gear's bore, and the boss's grub screw, if the gear has one, clamps the stack (else a bead of hot glue on the inboard end). True each wheel on its motor before the hoops close."),
            ("Steel teeth on the desk", "64 tooth tips a turn tick at about 48 a second at speed, faint on wood, sharper on glass, and they can mark a soft finish. Grip is not in question: 0.4 m/s² needs a friction coefficient of 0.04. A desk mat, or a silicone O-ring stretched over the teeth, if the tick matters; the look says bare teeth."),
            ("The seller's Ø40", "The gear is drawn from the listing (Ø40, 9 over the boss, 5 mm bore; 39.6 by its module) and it is on the bench: caliper it before anything is cut. The axle height is its radius plus 0.5; the width is 2 × (29.5 + its length over the boss)."),
        ]
    return rows


def build_parts():
    gear = WHEEL == "gear"
    pololu = ("1 pair", "Pololu wheel 32×7 mm, white", LINKS["w32"], "Pololu only; not on Amazon or DigiKey in white", "$4.45",
              "Ø31 over the black silicone tyre, 7 wide, 3.1 g, press fit on the N20's 3 mm D-shaft; with the motors 5 mm apart the 10 mm shaft ends flush with the hub's outer face. Faces sprayed canvas white, tyre masked.")
    gears = ("2", "HSP 11184 steel spur gears, 64 teeth, module 0.6", LINKS["gears"], "Crumb's box, delivered 11-03; on the bench", "owned",
             "The wheels. Ø40 over the teeth by the seller's drawing (39.6 by the module), root Ø36.9, 5 mm bore, 9 mm over the boss, about 32 g each; the pack's four pinions stay spare. Caliper all four numbers before the frame: the axle height and the width follow them. Boss inboard, an ivory card disc on the outer face.")
    buy = [
        ("1", "LDROBOT STL-19P lidar, as the Waveshare D500 kit (sensor, ZH1.5 pigtail, USB adapter)", LINKS["lidar_amz"], "Amazon (price not read); Waveshare $95.99; Hiwonder $99.99", "about $96",
         "Ø38.6 × 34.8 mm with its flange, 45 g, 5 V 290 mA, 3.3 V serial at 230400, 3 cm to 12 m, ±10 mm to 50 cm. Pins 1 Tx, 2 PWM, 3 GND, 4 P5V. The older D300 (LD19) is the same housing at 180 mA if you find it."),
        ("1", "Adafruit bq25185 USB-C charger with 5 V boost", LINKS["boost_dk"], "DigiKey 1528-6106-ND; Adafruit $8.95; not on Amazon", "$8.95",
         "USB-C in, JST BAT, terminal block + / − at 5 V 1 A, EN pad, a charge-rate jumper on the back: cut it for 500 mA. 29 × 19 mm. Runs the boost from the charger's power path, so the robot keeps running on the lead."),
    ]
    if not gear:
        buy.append(pololu)
    buy += [
        ("1", "Waveshare 1.28\" round LCD, GC9A01, 240 × 240", LINKS["round_amz"], "Amazon (price not read); Waveshare $14.99; PiShop $16.95", "about $15",
         "Round Ø37.5 board (40.4 tall with its tab), Ø32.4 picture, PH2.0 8-pin lead: VCC GND DIN CLK CS DC RST BL. 3.3 V logic, 31 mA. M2 holes. The owned 1.54\" square screen is the fallback on the same front."),
        ("1", "P-channel MOSFET, SOT-23, AO3401A or equal (−30 V, −4 A, Vgs(th) about −1 V)", LINKS["pfet"], "DigiKey, under $1; Amazon sells 20-packs", "under $1",
         "The high side of the lidar switch; soldered dead-bug like the drone's AO3400A. Any P-MOSFET that is fully on at Vgs −4.5 V and carries 0.5 A does."),
    ]
    crumb = [
        ("1", "Seeed XIAO ESP32-S3 Sense", LINKS["xiao"], "Amazon, 2026-10-31; by 11-11", "owned", "Brain, camera, PDM microphone, Wi-Fi. Cut jumper J3 on the Sense board first. BAT pads stay empty; the 5V pin takes the rail through the Schottky."),
        ("2", "N20 gear motor, 6 V 100 rpm, 3 mm D-shaft", LINKS["n20"], "Amazon, delivered 11-03", "owned", f"About 60 rpm at the cell's voltage, 45 under load: {V_LOAD:.0f} cm/s on Ø{WD:.0f}. Measure stall current before the frame."),
    ]
    if gear:
        crumb.append(gears)
    crumb += [
        ("1", "SparkFun Qwiic motor driver", LINKS["drv"], "Amazon, delivered 11-03", "owned", "0x5D, two Qwiic sockets, screw terminals for VIN/GND and the two motors, 3–11 V in. Cut its I²C pull-up jumper. Read the terminal silkscreen before wiring."),
        ("1", "MAX98357A I²S amplifier", LINKS["amp"], "Amazon, nine on hand plus three in Crumb's box", "owned", "VIN from the 5 V rail, 220 µF at its VIN, GAIN open, SD on its pull-up."),
        ("1", "VL53L1X laser ranger carrier", LINKS["rng1"], "Pololu via DigiKey, picked up 11-03", "owned", "VIN 3V3, 0x29, XSHUT and GPIO1 open. On the brow, 40° down, 27° cone, 4 cm minimum, path 70–85 mm."),
        ("1", "GY-521 MPU6050 motion sensor", LINKS["imu"], "Amazon 3-pack ordered 11-07", "owned", "VCC 3V3, AD0 to GND, 0x68. Its 2.2 kΩ pull-ups stay (the driver's go)."),
        ("1", "Adafruit MAX17048 fuel gauge", LINKS["gauge"], "Adafruit 3771280, on hand", "owned", "In the cell lead between the toggle and the charger: JST A from the toggle, JST B to BAT. VIN from the chain's 3V3, 0x36, INT open."),
    ]
    shared = [
        ("1", "Nitecore NL169 16340, 950 mAh, protected", LINKS["cell"], "IMR Batteries, on hand (eight spare)", "owned", "Swaps through the back hatch. 2 A protection; charged at 500 mA, about 2.2 h."),
        ("1", "16340 holder with leads", LINKS["holder"], "Amazon, on hand", "owned", "On its side on the shelf, opening to the back. Meter red to +."),
        ("1", "MTS-102 toggle", LINKS["toggle"], "Amazon, on hand", "owned", "In the cell's + lead, bushing through the back skin."),
        ("1", "tactile button", LINKS["button"], "Amazon, on hand", "owned", "Not wired this round (no pin left); fitted as the reset access for the XIAO if you want one, else left out."),
        ("1", "Same Sky CES-20134-088PM speaker", LINKS["spk"], "DigiKey, on hand", "owned", "20 × 13 × 4.9, 8 Ω 0.8 W, flat on the floor firing down."),
        ("2 + 1", "Schottky diode (1 A) and AO3400A N-MOSFET", LINKS["nfet"], "drone stock, on hand", "owned", "The diode in the XIAO's 5V lead; the N-MOSFET drives the P-MOSFET's gate."),
        ("1 + 1", "100 mm QT cable; QT-to-header cable", LINKS["qt"], "Adafruit, on hand", "owned", "Gauge to driver; driver to the ranger and motion sensor."),
        ("2 × 300 mm", "1.5 mm brass rod (the hoops)", LINKS["rod15"], "K&S, about 87 spare", "owned", "One rod per hoop, 222 mm each."),
        ("3 × 300 mm", "1.0 mm brass rod (rails, keel, cradles, shelf, flange rods, W1, brim ring)", LINKS["rod10"], "K&S, about 8 spare", "owned", f"About {ROD10:.0f} mm in all; the cut list is on the frame drawing."),
        ("20 mm" + (" + 18 + 18 mm" if gear else ""), "4 mm brass tube (the two domes)" + (", 4 and 5 mm tube (the two hubs)" if gear else ""), LINKS["tube"], "METERXITY set, on hand", "owned",
         "A dome soldered on the end of a 4 mm tube stub; the nose one sits 1 mm higher." + (" Each hub: 9 mm of 4 mm tube inside 9 mm of 5 mm tube, soldered; the inner bore is the shaft's 3 mm." if gear else "")),
        ("2 sheets", "65 lb cardstock, canvas-white spray, clear heat tape", LINKS["white"], "Amazon, on hand", "owned", "The wrap (209 × 54.5), the two discs, " + ("a Ø36 face disc on each gear." if gear else "a dot over each shaft end.")),
        ("", "10 kΩ ×1, 1 kΩ ×1, 100 kΩ ×1; 220 µF, 100 µF, 10 µF, 1 µF, 100 nF ×3; 26 and 30 AWG silicone wire; Kapton; heat-shrink; hot glue", LINKS["schottky"], "bench stock", "owned", "Values as drawn on the sheet."),
    ]
    aside = [
        ("1", "VL53L7CX 8×8 ranger", LINKS["rng8"], "Pololu via DigiKey", "spare", "The lidar does its job; the drone has the other."),
        ("2", "1.54\" colour screens", LINKS["ips"], "Crumb's box", "spare", "Three owned; one is the fallback face."),
    ]
    if gear:
        aside.insert(0, ("1 pair", "Pololu wheel 32×7 mm, white", LINKS["w32"], "Pololu", "$4.45", "Rev A's wheel; not bought unless the gears come off (the generator switches back with --wheel white)."))
    else:
        aside.insert(0, ("2", "HSP 11184 64-tooth steel gears", LINKS["gears"], "Crumb's box, delivered 11-03", "spare", "The ivory wheels replace them."))
    return [("To buy", buy), ("Owned: Crumb's bin", crumb), ("Owned: shared stock", shared), ("Set aside" if gear else "Set aside, back to the shared bin", aside)]


BUILD_ORDER, RISKS, PARTS = [], [], []   # filled by configure()

# ============================================================================= drawings: the final views

def gear_outline(zc, yc, teeth=GEAR_T, mod=GEAR_MOD):
    """The gear's silhouette face-on: tooth tips on the outside diameter, roots on the root circle, four points a tooth."""
    ro, rr = mod * (teeth + 2) / 2, (mod * teeth - 2.5 * mod) / 2
    da = 2 * math.pi / teeth
    pts = []
    for i in range(teeth):
        a = i * da
        for frac, r in ((-0.24, rr), (-0.13, ro), (0.13, ro), (0.24, rr)):
            pts.append((zc + r * math.cos(a + frac * da), yc + r * math.sin(a + frac * da)))
    return pts


def gear_side(v, zc, yc):
    """Crumb's 64-tooth gear face-on: steel teeth, an ivory card disc to the root circle, the brass hub tube's end in the middle."""
    pts = " ".join(f"{v.X(z):.1f},{v.Y(y):.1f}" for z, y in gear_outline(zc, yc))
    v.add(f'<polygon points="{pts}" fill="var(--steel)" stroke="var(--fg)" stroke-width=".45" stroke-linejoin="round"/>')
    v.circ(zc, yc, GEAR_FACE_R, "var(--ivory)", 'stroke="var(--skin-edge)" stroke-width=".7"')
    v.circ(zc, yc, 2.5, "var(--brass)"); v.circ(zc, yc, 1.5, "var(--ink)")


def wheel_side_any(v):
    if WHEEL == "white":
        wheel_side(v, AZ, AY, WR)
    else:
        gear_side(v, AZ, AY)


def _gear_edge(v, sx, c, along):
    """The gear edge-on from the side sx, centred on c in the other axis (y in the front view, z in the top view):
    boss inboard (Ø12, 5 long), the plate outboard (4 thick, Ø40), the ivory face on its outer side, the brass hub between disc and boss."""
    w = WHEELS["gear"]
    xi = sx * WX0
    b0, b1 = sorted((xi, xi + sx * w["boss_w"])); p0, p1 = sorted((xi + sx * w["boss_w"], xi + sx * WW)); f0, f1 = sorted((xi + sx * WW, xi + sx * (WW - 0.6)))
    if along == "y":
        v.rect(b0, c - w["boss_d"] / 2, b1 - b0, w["boss_d"], "var(--steel)")
        v.rrect(p0, c - WR, p1 - p0, 2 * WR, 0.8, "var(--steel)", 'stroke="var(--fg)" stroke-width=".4"')
        v.rect(f0, c - GEAR_FACE_R, f1 - f0, 2 * GEAR_FACE_R, "var(--ivory)")
        v.line(sx * BX, c, xi, c, 'stroke="var(--brass)" stroke-width="3.2"')
    else:
        v.rect(b0, c - w["boss_d"] / 2, b1 - b0, w["boss_d"], "var(--steel)")
        v.rrect(p0, c - WR, p1 - p0, 2 * WR, 0.8, "var(--steel)", 'stroke="var(--fg)" stroke-width=".4"')
        v.rect(f0, c - GEAR_FACE_R, f1 - f0, 2 * GEAR_FACE_R, "var(--ivory)")
        v.line(sx * BX, c, xi, c, 'stroke="var(--brass)" stroke-width="3.2"')


def wheel_front_any(v, sx):
    if WHEEL == "white":
        u = WX0 if sx > 0 else -(WX0 + WW)
        wheel_edge(v, u, 0, WW, WR, AY)
        v.line(sx * BX, AY, sx * (WX0 + 0.5), AY, 'stroke="var(--steel)" stroke-width="2.4"')
    else:
        _gear_edge(v, sx, AY, "y")


def wheel_top_any(v, sx):
    if WHEEL == "white":
        u = WX0 if sx > 0 else -(WX0 + WW)
        v.rrect(u, AZ - WR, WW, 2 * WR, 1.2, "var(--tyre)")
        v.line(sx * BX, AZ, sx * (WX0 + 0.5), AZ, 'stroke="var(--steel)" stroke-width="2.4"')
    else:
        _gear_edge(v, sx, AZ, "z")


def configure(kind):
    """Set every number that hangs on the wheel: Rev A ("white") or Rev B ("gear"). Called at the end of the module and by --wheel."""
    global WHEEL, WR, WW, WX0, AY, AZ, OVERALL, WD, CRADLE_Y, V_FREE, V_LOAD, PARTS_BOX, MASS_OTHER, MASS, ZCOM, YCOM, TIP, RODS, ROD10, PARTS, BUILD_ORDER, RISKS
    w = WHEELS[kind]; WHEEL = kind
    WR, WW, WX0, AZ = w["r"], w["w"], w["x0"], w["az"]
    AY = WR + 0.5; WD = 2 * WR; OVERALL = 2 * (WX0 + WW); CRADLE_Y = AY - 5.5
    V_FREE = math.pi * WD * (100 * 3.7 / 6) / 60 / 10; V_LOAD = math.pi * WD * 45 / 60 / 10      # cm/s
    dy, dz = AY - 16.0, AZ
    dw = max(0.0, AY + 5.5 - 22.0)                      # the driver and the amp start half a millimetre above the motors' tops
    PARTS_BOX = []
    for n, x, y, z, m, note in PARTS_BOX_A:
        if n in ("motor L", "motor R"):
            y, z = (y[0] + dy, y[1] + dy), (z[0] + dz, z[1] + dz)
        elif n in ("motor driver", "amp"):
            y = (y[0] + dw, y[1] + dw)
        PARTS_BOX.append((n, x, y, z, m, note))
    MASS_OTHER = [("wheels, pair" if kind == "white" else "gears, pair, with hubs and faces", w["mass"])] + MASS_OTHER_A[1:]
    MASS, ZCOM, YCOM = audit_geometry()
    TIP = 9.81 * (AZ - ZCOM) / YCOM
    RODS = build_rods(); ROD10 = sum(q * l for p, q, r, l, wh in RODS if r == "1.0 mm")
    PARTS = build_parts(); BUILD_ORDER = build_order(); RISKS = build_risks()


def final_views():
    key, views = [], []
    K = lambda n, t: key.append((n, t))
    boxes = {n: (x, y, z) for n, x, y, z, m, note in PARTS_BOX}

    def hid_front(v, name):
        x, y, z = boxes[name]; v.rect(x[0], y[0], x[1] - x[0], y[1] - y[0], "none", HID)

    def hid_side(v, name, fill=False):
        x, y, z = boxes[name]; v.rect(z[0], y[0], z[1] - z[0], y[1] - y[0], "none", HID_FILL if fill else HID)

    def hid_top(v, name):
        x, y, z = boxes[name]; v.rect(x[0], z[0], x[1] - x[0], z[1] - z[0], "none", HID)

    # ---------- front
    g = WHEEL == "gear"
    f = View(112, 124, 56, 17, "Mochi, front view")
    desk(f, -56, 56)
    for sx in (-1, 1):
        wheel_front_any(f, sx)
    f.rect(-BX, BY0, 2 * BX, BY1 - BY0, "var(--ivory)", SKIN)
    for n in ("motor L", "motor R", "cell holder", "motion sensor", "charger-boost", "motor driver", "amp", "fuel gauge", "speaker", "XIAO stack"):
        hid_front(f, n)
    f.circ(0, FACE_Y, C.RND_BOARD / 2, "var(--panel)", 'stroke="var(--skin-edge)" stroke-width=".6" stroke-dasharray="1.5 1.5"')
    eyes_round(f, 0, FACE_Y)
    f.circ(-5, 56.5, 2.6, "var(--glass)"); f.circ(-5, 56.5, 1.1, "var(--lens)")
    f.rect(15.4, 41, 6, 8, "var(--black)"); f.rect(16.6, 43.5, 3.6, 3, "var(--window)")
    f.line(-BX, BY0, -BX, BY1, ROD); f.line(BX, BY0, BX, BY1, ROD); f.line(-BX, BY0, BX, BY0, ROD)
    lidar_front(f, LZ * 0, LY_FL, flange="hidden")
    f.line(-20.25, LY_BODY + 0.5, 20.25, LY_BODY + 0.5, ROD_THIN)                                   # brim ring edge-on
    f.circ(0, 3.5, 2.5, "var(--brass)")                                                               # nose dome
    f.dim(-(WX0 + WW), -8.5, WX0 + WW, -8.5, f"{OVERALL:.0f} over the {'gears' if g else 'wheels'}", off=0)
    f.dim(48, 0, 48, LID_TOP, f"{LID_TOP:.0f}", off=0, side="right")
    f.tag(1, 0, FACE_Y + 12, -42, 40); f.tag(2, -5, 56.5, -42, 66); f.tag(3, 18.4, 45, 42, 52)
    f.tag(4, 0, LY_FL + 20, 42, 90); f.tag(5, -33, 22, -43, 10); f.tag(6, 0, 29, 42, 24)
    views.append((f.svg(), "Front. The two hoops and the floor rail are the brass; the top edge is card with the brim ring round the hat."))

    # ---------- side
    s = View(116, 124, 46, 17, "Mochi, side view, face to the right")
    desk(s, -46, 70)
    s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "var(--ivory-2)", SKIN)
    for n in ("cell holder", "motion sensor", "charger-boost", "fuel gauge", "speaker", "XIAO stack", "motor driver"):
        hid_side(s, n, fill=n in ("cell holder", "charger-boost", "XIAO stack"))
    hid_side(s, "motor L", fill=True)
    # labels that the Ø40 gear would cover move to its edges in Rev B
    s.text(-22.5 if g else -20, 30, "cell", "hid", dy=2); s.text(-12, 53, "charger-boost", "hid", dy=2); s.text(17, 42 if g else 38, "XIAO", "hid", dy=2); s.text(-4 if g else 0, 44 if g else 34, "driver", "hid", dy=2)
    s.text(-22 if g else -17, 8.5, "gauge" if g else "gauge · speaker", "hid", dy=2)
    s.rect(24.5, 12.25, 3, 37.5, "var(--black)")                                                     # screen edge-on
    wheel_side_any(s)
    s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "none", ROD)
    s.circ(0, BY0, 1.0, "var(--brass-dk)")                                                            # floor rail end-on
    s.circ(BZ1 - 1.6, 56.5, 1.5, "var(--glass)")
    s.rect(15.3, 46.2, 8.8, 11, "none", HID); s.text(19.5, 51, "rng", "hid", dy=2)
    rng = (19.4, 52.4)
    for a in (26.5, 40, 53.5):
        Lr = rng[1] / math.sin(a * D2R)
        s.line(rng[0], rng[1], rng[0] + Lr * math.cos(a * D2R), 0, BEAM)
    s.add(f'<text x="{s.X(70)}" y="{s.Y(-4.2)}" class="dimlab" text-anchor="end">edge seen 31–97 mm ahead</text>')
    lidar_front(s, LZ, LY_FL, flange="deep")
    s.line(LZ - 20.25, LY_BODY + 0.5, LZ + 20.25, LY_BODY + 0.5, ROD_THIN)
    s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "none", ROD)
    s.line(-46, SCAN_Y, LZ - 19.3, SCAN_Y, SCAN); s.line(LZ + 19.3, SCAN_Y, 70, SCAN_Y, SCAN)
    s.add(f'<text x="{s.X(70)}" y="{s.Y(SCAN_Y + 1.8)}" class="dimlab" text-anchor="end">lidar plane {SCAN_Y:.0f} mm up</text>')
    s.circ(-25, 2.5, 2.5, "var(--brass)"); s.circ(25, 3.5, 2.5, "var(--brass)")
    s.line(-26, BY0, 26, BY0, 'stroke="var(--brass)" stroke-width="1.6"')                              # the keel
    s.rect(BZ0 - 3, 48, 3, 4, "var(--steel)"); s.line(BZ0 - 3, 50, BZ0 - 9, 52.5, 'stroke="var(--steel)" stroke-width="2"')
    s.rect(BZ0 - 1.2, 51, 1.2, 3.3, "var(--steel)")                                                   # USB-C out the back
    s.rect(BZ0 - 0.4, 21.5, 0.8, 19, "var(--brass-dk)")                                                # the hatch, edge-on
    s.dim(BZ0, -8.5, BZ1, -8.5, "56", off=0)
    s.tag(5, AZ, AY, -40, 10); s.tag(7, BZ0 - 6, 51, -40, 70); s.tag(8, -25, 2.5, -40, 24)
    s.tag(9, -20, 36, -40, 44); s.tag(10, rng[0], rng[1], 50, 66); s.tag(4, LZ, LY_FL + 20, -32, 92)
    s.tag(11, -12, 54, -40, 58); s.tag(12, BZ0 - 0.8, 31, 48, 20); s.tag(13, 8 if g else 0, 48 if g else 38, 48, 44)
    s.text(BZ1 + 4, 31, "face", "dimlab", "start")
    views.append((s.svg(), f"Side, face to the right. The hoop is the outline; {'the Ø40 gear an ivory disc inside a steel toothed rim' if g else 'the Ø31 wheel the ivory disc'}; the hatch, the USB-C and the toggle on the back."))

    # ---------- top
    t = View(100, 92, 50, 48, "Mochi, top view, face at the top")
    for sx in (-1, 1):
        wheel_top_any(t, sx)
    t.rrect(-BX, BZ0, 2 * BX, BZ1 - BZ0, 0.5, "var(--ivory)", SKIN)
    for n in ("motor L", "motor R", "cell holder", "charger-boost", "motor driver", "amp", "fuel gauge", "speaker", "XIAO stack"):
        hid_top(t, n)
    t.rect(-C.RND_BOARD / 2, 24.5, C.RND_BOARD, 3, "var(--black)")
    t.rect(-BX, BZ0, 2 * BX, BZ1 - BZ0, "none", ROD)
    t.rrect(-27, LZ - 24, 54, 46, 6, "none", HID)
    lidar_top(t, 0, LZ)
    t.circ(0, LZ, 20.25, "none", ROD_THIN)
    t.circ(-5, BZ1 - 1.5, 1.5, "var(--glass)")
    t.rect(-19.5, BZ0 - 2.6, 3, 2.6, "var(--steel)"); t.rect(16.5, BZ0 - 2.6, 3, 2.6, "var(--steel)"); t.rect(-4.5, BZ0 - 1.5, 9, 1.5, "var(--steel)")
    t.text(0, BZ0 - 7.5, "back: button · USB-C · toggle, the cell hatch below them", "hid", dy=2)
    t.dim(-(WX0 + WW), BZ0 - 13, WX0 + WW, BZ0 - 13, f"{OVERALL:.0f}", off=0)
    t.tag(14, -24, 24, -43, 34); t.tag(7, 18, BZ0 - 1.3, 43, -31); t.tag(15, 0, 18, 43, 10)
    t.text(0, BZ1 + 3, "face", "dimlab")
    views.append((t.svg(), "Top, face at the top. The dashed plate under the hat is the lidar's flange on its two cross rods."))

    K(1, "Waveshare 1.28\" round screen behind a Ø33 window; its board hangs on rod W1 and the XIAO stands behind it.")
    K(2, "Camera module glued inside the top-front rounding, lens looking 25° up through a Ø3.5 hole in the arc.")
    K(3, "Edge ranger tilted 40° down behind the round board’s rim, its beam out through a 6 × 8 slot beside the window: the hard stop, desk 31–97 mm ahead.")
    K(4, "The lidar: flange under the top skin on two cross rods, body through a Ø40 hole, brim ring of 1.0 mm rod over the join. Plane 86 mm up.")
    K(5, f"Two N20 motors end to end on two cradle Us, axle {AY:g} up and 1 mm forward of centre; Crumb’s Ø40 steel gears on 9 mm brass-tube hubs, each faced with an ivory card disc so only the toothed rim shows steel; {OVERALL:.0f} over them."
         if g else "Two N20 motors end to end on two cradle Us, axle 16 up; Ø31 ivory wheels pressed on the shafts, 73 over them.")
    K(6, "XIAO ESP32-S3 Sense, USB-C up, antenna flex on the inside of the top skin.")
    K(7, "The back: tactile button, the charger-boost's USB-C, the toggle in a row at 50 up; the cell hatch below.")
    K(8, "Tail dome on the keel at z −25; nose dome 1 mm higher at z +25. It rests on the tail.")
    K(9, "16340 holder on its side on the shelf, opening to the hatch; the motion sensor, the lidar switch and the charger-boost stacked on it.")
    K(10, "The ranger's field, 28° to 52° below level.")
    K(11, "Charger-boost flat at the top of the back, parts up, under the flange.")
    K(12, "The hatch: a 44 × 19 opening in the back skin, closed by a card flap under the toggle.")
    K(13, "Motor driver standing on the right wall; the amp stands on the left wall; gauge and speaker lie on the floor.")
    K(14, "Body: card wrap and discs inside two 1.5 mm hoops; floor rail, keel and cradles below; everything sprayed canvas white.")
    K(15, "The flange's two cross rods, shallow Us hanging from the hoops' top segments at z −22 and +12.")
    return views, key


# ============================================================================= drawings: skin off
def inside_views():
    S0 = C.S
    C.S = 4.2   # larger scale for the packing drawings
    try:
        boxes = {n: (x, y, z, note) for n, x, y, z, m, note in PARTS_BOX}
        FILL = {"motor L": "var(--steel)", "motor R": "var(--steel)", "cell holder": "var(--tyre-2)", "lidar body": "var(--black)", "lidar flange": "var(--black-2)",
                "round screen": "var(--glass)", "XIAO stack": "var(--black-2)", "charger-boost": "var(--hid)", "motor driver": "var(--hid)", "amp": "var(--hid)",
                "fuel gauge": "var(--hid)", "motion sensor": "var(--hid)", "speaker": "var(--steel)", "toggle": "var(--steel)", "button": "var(--steel)",
                "lidar switch": "var(--hid)", "camera module": "var(--black)", "edge ranger": "var(--hid)", "screen plug": "var(--steel)"}
        def draw(v, axes, order):
            for n in order:
                x, y, z, note = boxes[n]
                (u0, u1), (w0, w1) = (x if axes[0] == "x" else z), (y if axes[1] == "y" else z)
                v.rect(u0, w0, u1 - u0, w1 - w0, FILL.get(n, "var(--hid)"), 'stroke="var(--ink)" stroke-width=".7"')
        # side section, looking from the right (u = z, v = y): far parts first
        s = View(76, 100, 36, 8, "Mochi inside, side section, face to the right")
        desk(s, -36, 40)
        s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "var(--ivory-2)", SKIN)
        draw(s, "zy", ["amp", "fuel gauge", "speaker", "motor L", "cell holder", "motion sensor", "lidar switch", "charger-boost", "button", "toggle",
                       "motor driver", "XIAO stack", "screen plug", "round screen", "camera module", "edge ranger", "lidar flange"])
        lidar_front(s, LZ, LY_FL)
        s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "none", ROD)
        # the rods, end-on and along z
        for (zz, yy) in ((0, 5), (AZ - 5.5, CRADLE_Y), (AZ + 5.5, CRADLE_Y), (-27, 21.5), (-12, 21.5), (-22, 57.7), (12, 57.7), (25.5, 50)):
            s.circ(zz, yy, 0.8, "var(--brass)")
        s.line(-26, 5, 26, 5, 'stroke="var(--brass)" stroke-width="1.8"')
        s.circ(-25, 2.5, 2.5, "var(--brass)"); s.circ(25, 3.5, 2.5, "var(--brass)")
        for lbl, zz, yy in (("cell", -20, 31), ("driver", 0, 34.5), ("XIAO", 17, 38), ("charger-boost", -12.5, 53.5), ("sensor", -19, 42.5), ("gauge", -17, 8),
                            ("speaker", -17, 12.8), ("amp", 6, 31.5), ("screen", 26, 31), ("lens", 24.5, 57), ("ranger", 24.5, 50.5), ("switch", -21, 46), ("motor", AZ, AY)):
            s.text(zz, yy, lbl, "hid", dy=2)
        s.text(-20, 48.3, "toggle", "hid", dy=2)
        s.add(f'<text x="{s.X(40)}" y="{s.Y(-4.2)}" class="dimlab" text-anchor="end">dots: rods end-on</text>')
        s.text(BZ1 + 3, 31, "face", "dimlab", "start")
        # top, lid off (u = x, v = z): floor first
        t = View(80, 76, 40, 36, "Mochi inside, top view, lid off, face at the top")
        t.rrect(-BX, BZ0, 2 * BX, BZ1 - BZ0, 0.5, "var(--ivory)", SKIN)
        draw(t, "xz", ["fuel gauge", "speaker", "motor L", "motor R", "cell holder", "amp", "motor driver", "motion sensor", "lidar switch", "charger-boost",
                       "toggle", "button", "XIAO stack", "screen plug", "round screen", "camera module", "edge ranger"])
        t.rrect(-27, LZ - 24, 54, 46, 6, "none", 'stroke="var(--black)" stroke-width="1" stroke-dasharray="3 2"')
        t.circ(0, LZ, 19.3, "none", 'stroke="var(--black)" stroke-width="1.2" stroke-dasharray="3 2"')
        t.rect(-BX, BZ0, 2 * BX, BZ1 - BZ0, "none", ROD)
        t.line(-BX, 0, BX, 0, 'stroke="var(--brass)" stroke-width="1.6" stroke-dasharray="2 2"')
        for (xx, zz) in ((-27, -27), (27, -27), (-27, -12), (27, -12)):
            t.circ(xx, zz, 0.9, "var(--brass)")
        for lbl, xx, zz in (("motor L", -14.5, 0), ("motor R", 14.5, 0), ("cell holder", 0, -20), ("gauge", -13, -17), ("speaker", 10.5, -17), ("driver", 22, 0.5),
                            ("amp", -24.5, 6), ("XIAO", 0, 17), ("charger-boost", 0, -8), ("switch", -3, -21), ("toggle", 18, -22), ("button", -18, -24.5)):
            t.text(xx, zz, lbl, "hid", dy=2)
        t.text(0, BZ1 + 3, "face", "dimlab"); t.text(0, BZ0 - 3.5, "back · the dashed circle is the lidar body, the dashed plate its flange", "dimlab")
        return [(s.svg(), "Inside, from the right, skin and wheel removed. Everything to size; the lidar's flange rides on two cross rods under the top skin."),
                (t.svg(), "Inside from above, lid and lidar lifted off. The motors end to end on the axle; the cell across the back; the charger-boost over it with its USB-C through the back skin.")]
    finally:
        C.S = S0


# ============================================================================= drawings: frame and card
def frame_and_card():
    S0 = C.S
    C.S = 3.2
    try:
        # the hoop template, actual profile with dimensions
        h = View(96, 84, 42, 14, "Hoop template, 1.5 mm brass rod")
        h.rrect(BZ0, BY0, 56, 55, R, "none", ROD)
        h.dim(BZ0, BY0 - 4, BZ1, BY0 - 4, "56", off=0)
        h.dim(BZ1 + 5, BY0, BZ1 + 5, BY1, "55", off=0, side="right")
        h.add(f'<path d="M{h.X(24)},{h.Y(60)} A{4*C.S},{4*C.S} 0 0 1 {h.X(28)},{h.Y(56)}" fill="none" stroke="var(--beam)" stroke-width="1.4"/>')
        h.text(-10, 52, "r 4, all four corners", "dimlab")
        h.text(0, 44, "two of these, 222 mm of rod each", "dimlab"); h.text(0, 39, "with a 6 mm soldered lap at the bottom", "dimlab")
        h.text(0, 34, "the wrap runs round inside; the disc fills it", "dimlab")
        # rods between the hoops, seen from the side with their heights
        for (zz, yy, name) in ((0, 5, "floor rail"), (AZ - 5.5, CRADLE_Y, "cradle U"), (AZ + 5.5, CRADLE_Y, "cradle U"), (-27, 21.5, "shelf leg"), (-12, 21.5, "shelf leg"),
                               (-22, 57.7, "flange U"), (12, 57.7, "flange U"), (25.5, 50, "W1")):
            h.circ(zz, yy, 1.0, "var(--brass-dk)")
        h.text(AZ, CRADLE_Y + 3, "cradle Us", "hid", dy=2); h.text(-19.5, 18.5, "shelf legs", "hid", dy=2); h.text(-5, 61.4, "flange Us", "hid", dy=2); h.text(19, 47, "W1", "hid", dy=2); h.text(12, 1.8, "floor rail", "hid", dy=2)
        h.line(-26, 5, 26, 5, 'stroke="var(--brass)" stroke-width="1.6"'); h.text(-10, 8.2, "keel, z −26..+26", "hid", dy=2)
        # the card wrap, unrolled: back (y 11→54 up), top (z −22→+22), front (y 54→11), floor (z +22→−22), with the four arcs between
        w = View(236, 86, 6, 18, "Card wrap, unrolled")
        rin = R - 1.0; arc = 2 * math.pi * rin / 4
        flat_v, flat_h = (BY1 - BY0) - 2 * R, (BZ1 - BZ0) - 2 * R
        segs = [("back", flat_v), ("arc", arc), ("top", flat_h), ("arc", arc), ("front", flat_v), ("arc", arc), ("floor", flat_h), ("arc", arc)]
        u = 0
        w.rect(0, 0, sum(l for _, l in segs), 54.5, "var(--ivory)", SKIN)
        marks = []
        for name, length in segs:
            if name != "arc":
                w.text(u + length / 2, 58, name, "dimlab"); marks.append((name, u))
            else:
                w.rect(u, 0, length, 54.5, "var(--ivory-2)", 'stroke="none"')
            u += length
            w.line(u, 0, u, 54.5, 'stroke="var(--skin-edge)" stroke-width=".5" stroke-dasharray="1.5 1.5"')
        M = dict(marks)
        # openings; along-strip coordinate = M[face] + offset; across-strip = x + 27.25
        X = lambda x: x + 27.25
        # back: hatch, button, usb-c, toggle (strip runs from y 11 at u=0 to y 54)
        y0 = BY0 + R
        w.rect(M["back"] + (21.5 - y0), X(-22), 19, 44, "var(--panel)", 'stroke="var(--brass-dk)" stroke-width=".8"'); w.text(M["back"] + 20, X(0), "hatch 19 × 44", "hid", dy=2)
        w.circ(M["back"] + (50 - y0), X(-18), 2, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"')
        w.rect(M["back"] + (50 - y0), X(-4.5), 3.3, 9, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"')
        w.circ(M["back"] + (50 - y0), X(18), 3, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"')
        w.text(M["back"] + 36, X(-24.5), "button Ø4 · USB-C 9 × 3.3 · toggle Ø6", "hid", dy=2)
        # top: lidar hole Ø40 at z = LZ (strip runs from z −22 at u=0 to +22), cable slot
        w.circ(M["top"] + (LZ + flat_h / 2), X(0), 20, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"'); w.text(M["top"] + flat_h / 2, X(0), "lidar Ø40", "hid", dy=2)
        w.rect(M["top"] + (LZ + flat_h / 2) - 1.5, X(20.5) - 1.5, 3, 6, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"')
        # front: window Ø33 at y 31 (strip runs from y 54 at u=0 down to 11), lens hole and ranger slot are in the arc before it
        w.circ(M["front"] + ((BY1 - R) - FACE_Y), X(0), 16.5, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"'); w.text(M["front"] + 25, X(0), "face Ø33", "hid", dy=2)
        w.circ(M["front"] - arc * 25 / 90, X(-5), 1.75, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"')
        w.rect(M["front"] + ((BY1 - R) - 49), X(15.4), 8, 6, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"')
        w.text(M["front"] + flat_v / 2, -5, "lens Ø3.5 on the arc at x −5 · ranger slot 6 × 8 at y 41–49", "hid", dy=2)
        # floor: speaker slot (strip runs from z +22 at u=0 to −22): slot z −25..−9 → mostly in the arc; draw at z −20..−9
        w.rect(M["floor"] + flat_h / 2 + 10, X(5), 11, 18, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"'); w.text(M["floor"] + 16, X(-8), "speaker slot 11 × 18", "hid", dy=2)
        w.dim(0, -10, u, -10, f"{u:.0f} long", off=0); w.dim(u + 4, 0, u + 4, 54.5, "54.5", off=0, side="right")
        # the disc
        d = View(76, 84, 36, 14, "Side disc, two, mirror images")
        d.rrect(BZ0 + 0.75, BY0 + 0.75, 54.5, 53.5, R - 0.75, "var(--ivory)", SKIN)
        d.circ(AZ, AY, 4, "var(--panel)", 'stroke="var(--ink)" stroke-width=".7"'); d.text(AZ, AY + 7, "Ø8 for the hub", "hid", dy=2)
        d.text(0, 45, "54.5 × 53.5, r 3.25", "dimlab"); d.text(0, 40, "glued to the hoop's inner face", "dimlab")
        out = [(h.svg(), "The hoop, actual profile, and where every rod between the two hoops sits. Rod list below."),
               (w.svg(), "The card wrap unrolled, 209 × 54.5 mm: back, top, front, floor, with a 3 mm arc between each pair. Cut the lidar hole last, to the measured flange."),
               (d.svg(), "The side disc, one each side, with the hub hole on the axle.")]
        frame_and_card.sizes = [(h.w, h.h), (w.w, w.h), (d.w, d.h)]
        return out
    finally:
        C.S = S0


def build_rods():
    legs = CRADLE_Y - BY0
    rods = [  # (piece, qty, rod, length each mm, where)
        ("hoop", 2, "1.5 mm", 222, "the outline, 56 × 55 r 4, lap-soldered at the bottom centre"),
        ("floor rail", 1, "1.0 mm", 56, "hoop to hoop at y 5, z 0, under the floor skin"),
        ("keel", 1, "1.0 mm", 52, "along z at x 0 under the floor, soldered across the floor rail; carries the two domes"),
        ("cradle U", 2, "1.0 mm", round(56 + 2 * legs), f"y {CRADLE_Y:g}, z {AZ - 5.5:g} and {AZ + 5.5:g}, legs {legs:g} down to the hoops' bottoms: the motors sit on them"),
        ("shelf", 1, "1.0 mm", 204, "a 54 × 15 rectangle at y 21.5 (z −27..−12) on four 16.5 legs to the hoops' bottoms: the holder sits on it"),
        ("flange U", 2, "1.0 mm", 61, "y 57.7, z −22 and +12, legs 2.3 up to the hoops' tops: the lidar's flange rests on them"),
        ("W1", 1, "1.0 mm", 61, "y 50, z 25.5, legs 2.5 forward to the hoops' fronts: the screen hangs on it"),
        ("brim ring", 1, "1.0 mm", 127, "Ø40.5 ring on the top skin round the lidar body"),
        ("domes", 2, "4 mm tube", 6, "a stub with a soldered dome, tail on the desk, nose 1 mm up"),
    ]
    if WHEEL == "gear":
        rods.append(("hub", 2, "5 over 4 mm tube", 9, "telescoped and soldered: the 4 mm tube's bore takes the 3 mm D-shaft, the 5 mm tube fills the gear's bore; boss inboard, flush with the gear's outer face"))
    return rods


RODS = []   # filled by configure()

# ============================================================================= the wiring sheet
SHEET_CSS = ("<style>"
             ".part{fill:var(--panel);stroke:var(--fg);stroke-width:1.5}"
             ".title{font:600 16px 'Chakra Petch',system-ui,sans-serif;fill:var(--fg)}"
             ".sub{font:400 11.5px 'IBM Plex Sans',system-ui,sans-serif;fill:var(--muted)}"
             ".h1{font:600 22px 'Chakra Petch',system-ui,sans-serif;fill:var(--fg)}"
             ".pin{font:500 12px 'IBM Plex Mono',monospace;fill:var(--fg)}"
             ".fn{font:400 11px 'IBM Plex Sans',system-ui,sans-serif;fill:var(--muted)}"
             ".lab{font:600 12px 'IBM Plex Sans',system-ui,sans-serif;fill:var(--fg)}"
             ".brass{font:600 11.5px 'IBM Plex Mono',monospace;fill:var(--brass-dk);letter-spacing:.06em}"
             ".rod{fill:none;stroke:var(--fg);stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}"
             ".bus{fill:none;stroke:var(--brass);stroke-width:4.5;stroke-linecap:round;stroke-linejoin:round}"
             ".cell{fill:none;stroke:var(--warn);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
             ".thin{fill:none;stroke:var(--fg);stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}"
             ".joint{fill:var(--fg)}.pinend{fill:var(--panel);stroke:var(--fg);stroke-width:1.6}"
             "</style>")

SHEET_TEXT = dict(  # crumb_build.py overrides these: the electrical design is shared, the body is not
    title="Mochi: every connection on one sheet",
    screen=("1.28\" round screen", "Waveshare GC9A01 · 240 × 240", "PH2.0 8-wire lead · 3.3 V · 31 mA"),
    holder_sub2="through the back hatch",
    usb_note="USB-C out the back skin; charges on",
    foot1="Paper design, 2026-11-07, checked against the Seeed wiki, the Adafruit 6106 and 5580 guides, the Waveshare D500 and 1.28\" pages,",
    foot2="the SparkFun 15451 page and the Pololu carrier page. Not built. The pin audit and the lane check in gen/mochi_build.py pass.",
    aria="Mochi wiring sheet, every connection pin to pin",
    pads="terminal block + / −: the 5 V rail",
    rail="5 V RAIL · from the charger-boost's terminal block + · 26 AWG · 1 A",
)


def T(x, y, s, cls="sub", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def dot(x, y, r=5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="joint"/>'


class Router:
    """Orthogonal polylines; a segment hops over every earlier segment of a different net it crosses (copied from the
    camera Pocket AI's sheet, so the family's drawings share one rule)."""
    R = 7

    def __init__(self):
        self.segs, self.pins = [], []

    def pin(self, x, y, net):
        self.pins.append((x, y, net))

    def wire(self, pts, cls="rod", net=None):
        path = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            horiz, vert = abs(y0 - y1) < 0.01, abs(x0 - x1) < 0.01
            hops = []
            if horiz:
                lo, hi = min(x0, x1), max(x0, x1)
                for (a0, b0, a1, b1, n) in self.segs:
                    if n == net or abs(a0 - a1) > 0.01:
                        continue
                    if lo + self.R < a0 < hi - self.R and min(b0, b1) + 0.5 < y0 < max(b0, b1) - 0.5:
                        hops.append(a0)
                sgn = 1 if x1 > x0 else -1
                for rx in sorted(set(hops), reverse=(sgn < 0)):
                    path += f" L{rx - self.R * sgn:.1f},{y0:.1f} A{self.R},{self.R} 0 0 {1 if sgn > 0 else 0} {rx + self.R * sgn:.1f},{y0:.1f}"
            elif vert:
                lo, hi = min(y0, y1), max(y0, y1)
                for (a0, b0, a1, b1, n) in self.segs:
                    if n == net or abs(b0 - b1) > 0.01:
                        continue
                    if lo + self.R < b0 < hi - self.R and min(a0, a1) + 0.5 < x0 < max(a0, a1) - 0.5:
                        hops.append(b0)
                sgn = 1 if y1 > y0 else -1
                for ry in sorted(set(hops), reverse=(sgn < 0)):
                    path += f" L{x0:.1f},{ry - self.R * sgn:.1f} A{self.R},{self.R} 0 0 {0 if sgn > 0 else 1} {x0:.1f},{ry + self.R * sgn:.1f}"
            path += f" L{x1:.1f},{y1:.1f}"
            self.segs.append((x0, y0, x1, y1, net))
        return f'<path d="{path}" class="{cls}"/>'

    def check(self, min_pin=12, min_lane=12):
        bad = []
        for (x0, y0, x1, y1, n) in self.segs:
            for (px, py, pn) in self.pins:
                if pn == n:
                    continue
                if abs(x0 - x1) < 0.01 and min(y0, y1) - 2 <= py <= max(y0, y1) + 2 and abs(px - x0) < min_pin:
                    bad.append(f"vertical {n} at x={x0} passes {abs(px - x0):.0f}px from pin ({px},{py}) of {pn}")
                if abs(y0 - y1) < 0.01 and min(x0, x1) - 2 <= px <= max(x0, x1) + 2 and abs(py - y0) < min_pin:
                    bad.append(f"horizontal {n} at y={y0} passes {abs(py - y0):.0f}px from pin ({px},{py}) of {pn}")
        crossings = 0
        for i, (x0, y0, x1, y1, n) in enumerate(self.segs):
            for (a0, b0, a1, b1, m) in self.segs[:i]:
                if m == n:
                    continue
                v1, v2 = abs(x0 - x1) < 0.01, abs(a0 - a1) < 0.01
                if v1 and v2 and abs(x0 - a0) < min_lane and min(y0, y1) < max(b0, b1) and max(y0, y1) > min(b0, b1):
                    bad.append(f"verticals {n} x={x0} and {m} x={a0} run {abs(x0 - a0):.0f}px apart")
                if (not v1) and (not v2) and abs(y0 - b0) < min_lane and min(x0, x1) < max(a0, a1) and max(x0, x1) > min(a0, a1):
                    bad.append(f"horizontals {n} y={y0} and {m} y={b0} run {abs(y0 - b0):.0f}px apart")
                if v1 != v2:
                    vx, vy0, vy1, hx0, hx1, hy = (x0, y0, y1, a0, a1, b0) if v1 else (a0, b0, b1, x0, x1, y0)
                    if min(hx0, hx1) + 0.5 < vx < max(hx0, hx1) - 0.5 and min(vy0, vy1) + 0.5 < hy < max(vy0, vy1) - 0.5:
                        crossings += 1
        return bad, crossings


def block(x, y, w, h, title, sub=None, sub2=None, ty=22):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="part"/>', T(x + w / 2, y + ty, title, "title", "middle")]
    if sub:
        o.append(T(x + w / 2, y + ty + 16, sub, "sub", "middle"))
    if sub2:
        o.append(T(x + w / 2, y + ty + 31, sub2, "sub", "middle"))
    return "".join(o)


def pin(rt, x, y, name, side, net, fn=None, fnx=None):
    rt.pin(x, y, net)
    o = [f'<circle cx="{x}" cy="{y}" r="4" class="pinend"/>']
    if side == "R":
        o.append(T(x - 9, y + 4, name, "pin", "end"))
        if fn: o.append(T(fnx, y + 4, fn, "fn", "end"))
    elif side == "L":
        o.append(T(x + 9, y + 4, name, "pin", "start"))
        if fn: o.append(T(fnx, y + 4, fn, "fn", "start"))
    elif side == "B":
        o.append(T(x, y - 7, name, "pin", "start", f'transform="rotate(-90 {x} {y - 7})"'))
    elif side == "T":
        o.append(T(x, y + 7, name, "pin", "end", f'transform="rotate(-90 {x} {y + 7})"'))
    return "".join(o)


def gnd(x, y):
    return f'<path d="M{x},{y} L{x},{y+10} M{x-10},{y+10} L{x+10},{y+10} M{x-6},{y+15} L{x+6},{y+15} M{x-2.5},{y+20} L{x+2.5},{y+20}" class="thin"/>'


def resistor_v(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2; z = 8
    pts = [(x, y0), (x, mid - 14)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        pts.append((x + dx, mid - 14 + (i + 0.5) * (28 / 6)))
    pts += [(x, mid + 14), (x, y1)]
    return rt.wire(pts, "thin", net)


def resistor_h(rt, x0, x1, y, net):
    mid = (x0 + x1) / 2; z = 8
    pts = [(x0, y), (mid - 14, y)]
    for i, dy in enumerate((z, -z, z, -z, z, -z)):
        pts.append((mid - 14 + (i + 0.5) * (28 / 6), y + dy))
    pts += [(mid + 14, y), (x1, y)]
    return rt.wire(pts, "thin", net)


def capacitor(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2
    return "".join([rt.wire([(x, y0), (x, mid - 5)], "thin", net), rt.wire([(x, mid + 5), (x, y1)], "thin", "GND"),
                    f'<line x1="{x-11}" y1="{mid-5}" x2="{x+11}" y2="{mid-5}" class="thin"/>', f'<line x1="{x-11}" y1="{mid+5}" x2="{x+11}" y2="{mid+5}" class="thin"/>'])


def diode_h(x0, x1, y):
    """Schottky, anode at x0, cathode at x1, drawn on an existing wire."""
    m = (x0 + x1) / 2
    return (f'<polygon points="{m-9},{y-8} {m-9},{y+8} {m+7},{y}" fill="var(--panel)" stroke="var(--fg)" stroke-width="1.6"/>'
            f'<path d="M{m+7},{y-8} L{m+7},{y+8} M{m+7},{y-8} L{m+3},{y-11} M{m+7},{y+8} L{m+11},{y+11}" class="thin"/>')


def mosfet(x, y, p=False):
    """A small MOSFET symbol centred at (x, y): gate on the left at (x-16, y), drain top (x, y-18), source bottom (x, y+18)."""
    arrow = f'M{x-2},{y} L{x+6},{y}' if p else f'M{x+6},{y} L{x-2},{y}'
    return (f'<circle cx="{x}" cy="{y}" r="17" fill="var(--panel)" stroke="var(--fg)" stroke-width="1.3"/>'
            f'<path d="M{x-16},{y} L{x-8},{y} M{x-8},{y-11} L{x-8},{y+11} M{x-4},{y-12} L{x-4},{y-5} M{x-4},{y-3} L{x-4},{y+3} M{x-4},{y+5} L{x-4},{y+12} '
            f'M{x-4},{y-9} L{x+6},{y-9} L{x+6},{y-18} M{x-4},{y+9} L{x+6},{y+9} L{x+6},{y+18} M{x-4},{y} L{x+6},{y} L{x+6},{y+9} {arrow}" class="thin"/>')




def sheet():
    W, H = 1540, 1110
    rt = Router(); w = rt.wire
    o = [T(20, 30, SHEET_TEXT["title"], "h1"),
         T(20, 50, "A dot is a joint. A line that hops over another does not touch it. Brass = the 5 V rail. Red = the cell rail after the toggle. "
                   "Thick black = a wire you solder. Thin = a resistor, capacitor or diode leg. Every ground goes to the star at the holder; the brass frame touches no net.", "sub")]
    RAIL_Y, STAR_Y = 80, 760

    # ------------------------------------------------------------ blocks and pins first (so the lane check knows every pin), rails drawn before the lanes
    XX, XY, XW, XH = 600, 150, 300, 420
    o.append(block(XX, XY, XW, XH, "XIAO ESP32-S3 Sense", "camera GPIO 10–18, 38–40, 47, 48 · mic GPIO 41/42", sub2="J3 cut · BAT pads empty · USB-C: flash with the toggle OFF", ty=48))
    Lp = {}
    for name, y, fn, net in (("3V3", 250, "3.3 V out", "3V3"), ("GND", 280, None, "GND"), ("D4", 320, "GPIO5 · SDA", "SDA"), ("D5", 350, "GPIO6 · SCL", "SCL"),
                             ("D0", 400, "GPIO1 · CLK", "CLK"), ("D1", 430, "GPIO2 · DIN", "DIN"), ("D6", 460, "GPIO43 · DC", "DC"), ("D7", 490, "GPIO44 · BL", "BL")):
        Lp[name] = (XX, y); o.append(pin(rt, XX, y, name, "L", net, fn, XX + 44))
    Rp = {}
    for name, y, fn, net in (("D2", 250, "GPIO3 · lidar on", "LID_EN"), ("D3", 330, "GPIO4 · UART1 RX", "LID_TX"),
                             ("D8", 400, "GPIO7 · BCLK", "BCLK"), ("D9", 430, "GPIO8 · LRC", "LRC"), ("D10", 460, "GPIO9 · DIN", "I2S_DIN")):
        Rp[name] = (XX + XW, y); o.append(pin(rt, XX + XW, y, name, "R", net, fn, XX + XW - 44))
    Tp = {"5V": (660, XY)}; o.append(pin(rt, 660, XY, "5V", "T", "5V_XIAO"))
    Bp = {"GND": (700, XY + XH)}; o.append(pin(rt, 700, XY + XH, "GND", "B", "GND"))

    SX, SY, SW, SH = 120, 200, 240, 330
    o.append(block(SX, SY, SW, SH, SHEET_TEXT["screen"][0], SHEET_TEXT["screen"][1], sub2=SHEET_TEXT["screen"][2]))
    Sp = {}
    for name, y, net in (("VCC", 250, "3V3"), ("GND", 280, "GND"), ("CS", 330, "GND"), ("RST", 365, "RST"), ("CLK", 400, "CLK"), ("DIN", 430, "DIN"), ("DC", 460, "DC"), ("BL", 490, "BL")):
        Sp[name] = (SX + SW, y); o.append(pin(rt, SX + SW, y, name, "R", net))

    o.append(f'<rect x="1000" y="95" width="210" height="170" rx="8" class="part"/>'); o.append(T(1010, 117, "Lidar 5 V switch", "title", "start")); o.append(T(1200, 258, "P high side, N driver", "sub", "end"))
    PX, PY = 1130, 160; NX, NY = 1060, 222
    o.append(mosfet(PX, PY, p=True)); o.append(T(PX + 22, PY + 4, "P: AO3401A", "fn"))
    o.append(mosfet(NX, NY)); o.append(T(NX + 24, NY + 4, "N: AO3400A", "fn"))
    rt.pin(PX + 6, PY - 18, "5V"); rt.pin(PX + 6, PY + 18, "LID_5V"); rt.pin(PX - 16, PY, "PG"); rt.pin(NX + 6, NY - 18, "PG"); rt.pin(NX + 6, NY + 18, "GND"); rt.pin(NX - 16, NY, "NG")

    LX, LY, LW, LH = 1270, 150, 220, 200
    o.append(block(LX, LY, LW, LH, "Lidar STL-19P", "ZH1.5 4-pin · 5 V 290 mA", sub2="230400 8N1 · Tx 3.3 V"))
    Dp = {}
    for name, y, net in (("4 P5V", 215, "LID_5V"), ("3 GND", 245, "GND"), ("1 Tx", 305, "LID_TX"), ("2 PWM", 335, "PWM")):
        Dp[name] = (LX, y); o.append(pin(rt, LX, y, name, "L", net))
    o.append(T(LX + 60, 341, "open, insulated: 10 Hz", "fn"))

    AX, AY_, AW, AH = 1000, 380, 240, 210
    o.append(block(AX, AY_, AW, AH, "MAX98357A amp", "GAIN open = 9 dB · SD on its pull-up"))
    Ap = {}
    for name, y, net in (("BCLK", 400, "BCLK"), ("LRC", 430, "LRC"), ("DIN", 460, "I2S_DIN")):
        Ap[name] = (AX, y); o.append(pin(rt, AX, y, name, "L", net))
    for name, y, net in (("OUT+", 420, "SPK+"), ("OUT−", 460, "SPK-")):
        Ap[name] = (AX + AW, y); o.append(pin(rt, AX + AW, y, name, "R", net))
    for name, x, net in (("GND", 1060, "GND"), ("VIN", 1180, "5V")):
        Ap[name] = (x, AY_ + AH); o.append(pin(rt, x, AY_ + AH, name, "B", net))
    o.append(block(1290, 390, 150, 100, "Speaker", "Same Sky 8 Ω 0.8 W", sub2="own leads, 60 mm"))
    rt.pin(1290, 420, "SPK+"); rt.pin(1290, 460, "SPK-"); o += [f'<circle cx="1290" cy="420" r="4" class="pinend"/>', f'<circle cx="1290" cy="460" r="4" class="pinend"/>']

    o.append(block(40, 640, 150, 90, "16340 holder", "Nitecore NL169 950 mAh", sub2=SHEET_TEXT["holder_sub2"], ty=28))
    rt.pin(190, 670, "CELL+"); rt.pin(190, 710, "GND"); o += [f'<circle cx="190" cy="670" r="4" class="pinend"/>', T(178, 674, "+", "pin", "end"), f'<circle cx="190" cy="710" r="4" class="pinend"/>', T(178, 714, "−", "pin", "end")]
    o.append(block(240, 640, 130, 60, "Toggle", "MTS-102, in the + lead", ty=24))
    rt.pin(240, 670, "CELL+"); rt.pin(370, 670, "BAT+"); o += [f'<circle cx="240" cy="670" r="4" class="pinend"/>', f'<circle cx="370" cy="670" r="4" class="pinend"/>']
    GX, GY, GW, GH = 420, 620, 230, 190
    o.append(block(GX, GY, GW, GH, "Fuel gauge", "Adafruit MAX17048 · 0x36"))
    Gp = {}
    for name, y, net in (("JST A +", 670, "BAT+"), ("JST A −", 700, "GND")):
        Gp[name] = (GX, y); o.append(pin(rt, GX, y, name, "L", net))
    for name, y, net in (("JST B +", 670, "BAT+B"), ("JST B −", 700, "GND")):
        Gp[name] = (GX + GW, y); o.append(pin(rt, GX + GW, y, name, "R", net))
    for name, x, net in (("VIN", 470, "3V3"), ("SDI", 530, "SDA"), ("SCL", 580, "SCL")):
        Gp[name] = (x, GY); o.append(pin(rt, x, GY, name, "T", net))
    o.append(T(GX + 12, 782, "two JST ports, a pass-through", "fn")); o.append(T(GX + 12, 798, "INT and QStart open · QT socket below", "fn"))
    rt.pin(535, GY + GH, "QT"); o.append(f'<circle cx="535" cy="{GY + GH}" r="4" class="pinend"/>')
    CX, CY, CW, CH = 720, 620, 260, 230
    o.append(block(CX, CY, CW, CH, "Charger + 5 V boost", "Adafruit bq25185 · USB-C in"))
    Cp = {}
    for name, y, net in (("BAT +", 670, "BAT+B"), ("BAT −", 700, "GND")):
        Cp[name] = (CX, y); o.append(pin(rt, CX, y, name, "L", net))
    for name, x, net in (("+", 800, "5V"), ("−", 860, "GND")):
        Cp[name] = (x, CY); o.append(pin(rt, x, CY, name, "T", net))
    o.append(T(CX + 12, 774, "jumper cut: 500 mA · EN open", "fn")); o.append(T(CX + 12, 790, SHEET_TEXT["pads"], "fn")); o.append(T(CX + 12, 806, SHEET_TEXT["usb_note"], "fn")); o.append(T(CX + 12, 822, "the lead while the robot runs", "fn"))
    o.append(f'<rect x="{CX+CW-56}" y="{CY+CH-28}" width="44" height="16" rx="3" fill="var(--panel)" stroke="var(--brass-dk)" stroke-width="1.2"/>'); o.append(T(CX + CW - 34, CY + CH - 16, "USB-C", "fn", "middle"))
    DX, DY, DW, DH = 1000, 880, 260, 150
    o.append(block(DX, DY, DW, DH, "Qwiic motor driver", "SparkFun · 0x5D · pull-up jumper cut", sub2="VIN 3–11 V from the cell rail"))
    rt.pin(DX, 960, "QT"); o.append(f'<circle cx="{DX}" cy="960" r="4" class="pinend"/>'); o.append(T(DX + 9, 964, "Qwiic 1", "pin"))
    rt.pin(DX + DW, 960, "QT2"); o.append(f'<circle cx="{DX+DW}" cy="960" r="4" class="pinend"/>'); o.append(T(DX + DW - 9, 964, "Qwiic 2", "pin", "end"))
    for name, x, net in (("VIN", 1060, "BAT+"), ("GND", 1120, "GND")):
        o.append(pin(rt, x, DY, name, "T", net))
    for name, x, net in (("A1 A2", 1180, "MA"), ("B1 B2", 1230, "MB")):
        o.append(pin(rt, x, DY + DH, name, "B", net))
    o.append(T(DX + 12, DY + 125, "read the terminal silkscreen", "fn"))
    o.append(block(1300, 1000, 80, 70, "Motor L", "N20", ty=26)); o.append(block(1400, 1000, 80, 70, "Motor R", "N20", ty=26))
    rt.pin(1300, 1035, "MA"); rt.pin(1400, 1035, "MB"); o += [f'<circle cx="1300" cy="1035" r="4" class="pinend"/>', f'<circle cx="1400" cy="1035" r="4" class="pinend"/>']
    o.append(block(1300, 760, 180, 100, "Edge ranger", "Pololu VL53L1X · 0x29", sub2="XSHUT, GPIO1 open"))
    o.append(block(1300, 880, 180, 100, "Motion sensor", "GY-521 MPU6050 · 0x68", sub2="AD0 to GND · INT open"))
    rt.pin(1300, 845, "QT2"); rt.pin(1300, 965, "QT2"); o += [f'<circle cx="1300" cy="845" r="4" class="pinend"/>', f'<circle cx="1300" cy="965" r="4" class="pinend"/>']
    o.append(T(1310, 849, "VIN GND SDA SCL", "pin")); o.append(T(1310, 969, "VCC GND SDA SCL", "pin"))

    # ------------------------------------------------------------ rails: 5 V (brass), the cell rail (red), the ground star line
    o.append(w([Cp["+"], (800, 600), (60, 600), (60, RAIL_Y), (1510, RAIL_Y)], "bus", "5V"))
    o.append(T(880, RAIL_Y - 10, SHEET_TEXT["rail"], "brass", "middle"))
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
    o.append(f'<polygon points="652,100 668,100 660,116" fill="var(--panel)" stroke="var(--fg)" stroke-width="1.6"/><line x1="652" y1="116" x2="668" y2="116" class="thin"/>')
    o.append(w([(660, 116), Tp["5V"]], "thin", "5V_XIAO"))
    o.append(T(672, 112, "Schottky 1 A, owned: rail in, USB never out", "fn"))

    # ------------------------------------------------------------ screen
    o.append(w([Lp["3V3"], Sp["VCC"]], "rod", "3V3")); o.append(T(480, 243, "3V3", "lab", "middle"))
    o.append(w([Lp["GND"], Sp["GND"]], "rod", "GND")); o.append(T(480, 273, "GND", "lab", "middle"))
    for a, b in (("D0", "CLK"), ("D1", "DIN"), ("D6", "DC"), ("D7", "BL")):
        o.append(w([Lp[a], Sp[b]], "rod", {"D0": "CLK", "D1": "DIN", "D6": "DC", "D7": "BL"}[a])); o.append(T(480, Lp[a][1] - 7, b, "lab", "middle"))
    o.append(w([Sp["CS"], (400, 330), (400, 345)], "rod", "GND")); o.append(gnd(400, 345)); o.append(T(412, 340, "CS low: the only SPI device", "fn"))
    o.append(w([Sp["RST"], (440, 365)], "rod", "RST")); o.append(dot(440, 365))
    o.append(resistor_v(rt, 440, 365, 250, "RST")); o.append(dot(440, 250)); o.append(T(452, 300, "10 kΩ", "fn"))
    o.append(w([(440, 365), (470, 365)], "thin", "RST")); o.append(capacitor(rt, 470, 365, 395, "RST")); o.append(dot(470, 365)); o.append(gnd(470, 395)); o.append(T(484, 384, "1 µF: power-on reset", "fn"))
    o.append(capacitor(rt, 510, 250, 280, "3V3")); o.append(dot(510, 250)); o.append(dot(510, 280)); o.append(T(524, 268, "10 µF + 100 nF", "fn"))

    # ------------------------------------------------------------ 3V3 and I²C down to the gauge (three lanes, 14 px apart, clear of the XIAO's pins)
    o.append(w([Lp["3V3"], (552, 250)], "rod", "3V3")); o.append(w([(552, 250), (552, 562), (470, 562), Gp["VIN"]], "rod", "3V3")); o.append(dot(552, 250))
    o.append(w([Lp["D4"], (566, 320)], "rod", "SDA")); o.append(w([(566, 320), (566, 578), (530, 578), Gp["SDI"]], "rod", "SDA")); o.append(dot(566, 320))
    o.append(w([Lp["D5"], (580, 350)], "rod", "SCL")); o.append(w([(580, 350), Gp["SCL"]], "rod", "SCL")); o.append(dot(580, 350))
    o.append(T(462, 556, "3V3", "lab", "end")); o.append(T(522, 572, "SDA", "lab", "end")); o.append(T(590, 600, "SCL", "lab", "start"))

    # ------------------------------------------------------------ lidar switch, lidar
    o.append(w([(PX + 6, RAIL_Y), (PX + 6, PY - 18)], "rod", "5V")); o.append(dot(PX + 6, RAIL_Y)); o.append(T(PX + 14, 136, "source", "fn"))
    o.append(w([(PX - 16, PY), (PX - 40, PY)], "thin", "PG")); o.append(dot(PX - 40, PY))
    o.append(resistor_v(rt, PX - 40, PY, 104, "PG")); o.append(w([(PX - 40, 104), (PX + 6, 104)], "thin", "5V")); o.append(dot(PX + 6, 104)); o.append(T(PX - 48, 136, "10 kΩ", "fn", "end"))
    o.append(w([(PX - 40, PY), (PX - 40, NY - 30), (NX + 6, NY - 30), (NX + 6, NY - 18)], "thin", "PG"))
    o.append(w([(NX + 6, NY + 18), (NX + 6, NY + 34)], "thin", "GND")); o.append(gnd(NX + 6, NY + 34))
    o.append(resistor_h(rt, 940, NX - 16, NY, "NG")); o.append(T(975, NY - 12, "1 kΩ", "fn"))
    o.append(w([Rp["D2"], (925, 250), (925, NY), (940, NY)], "rod", "LID_EN")); o.append(dot(925, 250))
    o.append(resistor_v(rt, 925, 250, 300, "LID_EN")); o.append(gnd(925, 300)); o.append(T(937, 284, "100 kΩ: off through boot", "fn"))
    o.append(w([(PX + 6, PY + 18), (PX + 6, 215), Dp["4 P5V"]], "rod", "LID_5V")); o.append(dot(PX + 6, 215))
    o.append(capacitor(rt, 1230, 215, 245, "LID_5V")); o.append(dot(1230, 215)); o.append(gnd(1230, 245)); o.append(T(1228, 282, "100 µF + 100 nF", "fn", "middle"))
    o.append(w([Dp["3 GND"], (1252, 245), (1252, 365)], "rod", "GND")); o.append(gnd(1252, 365))
    o.append(w([Dp["1 Tx"], (980, 305), (980, 330), Rp["D3"]], "rod", "LID_TX")); o.append(T(1150, 298, "UART1 RX", "lab", "middle"))

    # ------------------------------------------------------------ amp and speaker
    for a, b in (("D8", "BCLK"), ("D9", "LRC"), ("D10", "DIN")):
        o.append(w([Rp[a], Ap[b]], "rod", {"D8": "BCLK", "D9": "LRC", "D10": "I2S_DIN"}[a])); o.append(T(950, Rp[a][1] - 7, b, "lab", "middle"))
    o.append(w([Ap["OUT+"], (1290, 420)], "rod", "SPK+")); o.append(w([Ap["OUT−"], (1290, 460)], "rod", "SPK-"))
    o.append(T(1365, 520, "neither lead is ground", "fn", "middle"))
    o.append(w([Ap["GND"], (1060, 620)], "rod", "GND")); o.append(gnd(1060, 620))
    o.append(w([Ap["VIN"], (1180, 650), (1510, 650), (1510, RAIL_Y)], "rod", "5V")); o.append(dot(1510, RAIL_Y))
    o.append(capacitor(rt, 1300, 650, 690, "5V")); o.append(dot(1300, 650)); o.append(gnd(1300, 690)); o.append(T(1314, 676, "220 µF at the amp's VIN", "fn"))

    # ------------------------------------------------------------ the chain and the motors
    o.append(w([(535, GY + GH), (535, 960), (DX, 960)], "rod", "QT")); o.append(T(545, 940, "gauge QT → 100 mm QT cable → Qwiic 1", "fn"))
    o.append(w([(DX + DW, 960), (1280, 960), (1280, 845), (1300, 845)], "rod", "QT2")); o.append(dot(1280, 960))
    o.append(w([(1280, 960), (1280, 965), (1300, 965)], "rod", "QT2"))
    o.append(T(1278, 806, "QT-to-header cable, owned:", "fn", "end")); o.append(T(1278, 820, "3V3, GND, SDA, SCL to both", "fn", "end"))
    o.append(T(1390, 872, "100 nF at the ranger's VIN", "fn", "middle"))
    o.append(w([(1180, DY + DH), (1180, 1060), (1270, 1060), (1270, 1035), (1300, 1035)], "rod", "MA"))
    o.append(w([(1230, DY + DH), (1230, 1078), (1390, 1078), (1390, 1035), (1400, 1035)], "rod", "MB"))
    o.append(T(1390, 1096, "own leads; swap a pair to fix a direction", "fn", "middle"))

    o.append(T(20, 1082, SHEET_TEXT["foot1"], "sub"))
    o.append(T(20, 1098, SHEET_TEXT["foot2"], "sub"))

    bad, crossings = rt.check()
    for b in bad:
        print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    print(f"sheet: {len(rt.segs)} segments, {crossings} crossings drawn as hops")
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{SHEET_TEXT["aria"]}">{SHEET_CSS}{"".join(o)}</svg>'


# ============================================================================= the page and the record
def tbl(rows, head, cls=None):
    o = ['<div class="tw"><table><tr>' + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr>"]
    for r in rows:
        o.append("<tr>" + "".join(f'<td class="{"m" if (cls and cls[i]) else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>")
    o.append("</table></div>")
    return "".join(o)


def write_all(png_dir=None):
    views, key = final_views()
    inside = inside_views()
    frame = frame_and_card()
    the_sheet = sheet()
    figs = lambda vs: '<div class="views">' + "".join(f"<figure>{svg}<figcaption>{esc(cap)}</figcaption></figure>" for svg, cap in vs) + "</div>"
    keyhtml = '<div class="key">' + "".join(f"<div><b>{n}</b><span>{esc(t)}</span></div>" for n, t in key) + "</div>"
    extra_css = PAGE_CSS + "\n.views.two-up{grid-template-columns:repeat(auto-fit,minmax(360px,1fr))} figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} .rods td:first-child{white-space:nowrap}"

    pins_rows = [(h, str(g), n, esc(j)) for h, g, n, j in PINS]
    nets_rows = [(esc(a), esc(b), esc(c), esc(d), esc(e)) for a, b, c, d, e in NETS]
    budget_rows = [(esc(a), esc(b), f"{c} mA", f"{d}") for a, b, c, d in BUDGET]
    rods_rows = [(esc(p), str(q), r, f"{l}", esc(wh)) for p, q, r, l, wh in RODS]
    parts_html = ""
    for group, rows in PARTS:
        parts_html += f"<h3>{esc(group)}</h3>" + tbl([(esc(q), A(u, esc(p)) if u else esc(p), esc(wh), esc(pr), esc(n)) for q, p, u, wh, pr, n in rows],
                                                     ["Qty", "Part", "Where", "Price", "Why, and what to check"], [1, 0, 0, 1, 0])
    mass_rows = [(esc(n), str(m)) for n, *_, m, note in PARTS_BOX if m] + [(esc(n), str(m)) for n, m in MASS_OTHER] + [("<strong>Total</strong>", f"<strong>≈ {MASS:.0f}</strong>")]

    gear = WHEEL == "gear"
    n_buy = "four" if gear else "five"
    eyebrow = ("set aside late on 2026-11-07: the builder returned to Crumb, which takes Mochi’s electrics (see Crumb Build) · Rev B (gear wheels) had been approved that evening, Rev A earlier that day · nothing bought, nothing built"
               if gear else "2026-11-07 · approved as drawn · nothing bought, nothing built")
    wheel_lede = "turning Crumb’s 64-tooth steel gears, faced in ivory" if gear else "on Ø31 ivory wheels"
    palette = ("Black only in the lidar’s body, the screen’s glass and the lens; steel only as the gears’ toothed rims, 1.35 mm deep. No board shows. Brass only as lines: the two hoops, the floor rail, the brim ring round the hat, and the hub ends in the wheel faces."
               if gear else "Black only in the lidar’s body, the screen’s glass, the lens and the tyres. No board shows. Brass only as lines: the two hoops, the floor rail, the brim ring round the hat.")
    hub_note = ", 18 mm each of 4 and 5 mm tube for the hubs" if gear else ""
    torque_note = (f" The Ø40 gear gives the motor 23 % less push at the rim than Rev A’s Ø31, which the N20 has to spare: {MASS:.0f} g at 0.4 m/s² is about 2 mN·m across both wheels, a hundredth of one N20’s stall."
                   if gear else "")
    parts_intro = ("Four lines to buy, about $121 before shipping: the lidar kit (Amazon listing first; Waveshare or Hiwonder if its price is wrong), the charger-boost (DigiKey, or Adafruit), the P-MOSFET, and the round screen. The wheels are Crumb’s gears on hubs of owned tube; everything else is Crumb’s or shared stock."
                   if gear else "Five lines to buy, about $126 before shipping: the lidar kit (Amazon listing first; Waveshare or Hiwonder if its price is wrong), the charger-boost (DigiKey, or Adafruit), the wheels and the P-MOSFET, and the round screen. Everything else is Crumb’s or shared stock.")
    changes = [
        ("Wheels", "Pololu 32×7 white: Ø31, 3.1 g each, a silicone tyre, pressed on the D-shaft", "HSP 11184 steel spur gear: 64 teeth, module 0.6, Ø40, about 32 g each, bare teeth on the desk, an ivory card disc on the face"),
        ("Axle", "16 up, z 0", f"{AY:g} up, z +{AZ:g}: 1 mm forward"),
        ("Motors and cradle Us", "y 11–21; Us at 10.5, 67 mm each", f"y 15.5–25.5; Us at {CRADLE_Y:g}, {RODS[3][3]} mm each"),
        ("Driver and amp", "standing from y 22", "standing from y 26, half a millimetre above the motors"),
        ("Width over the wheels", "73", f"{OVERALL:.0f}"),
        ("Mass; centre of mass", "180 g; 41 up, 2.2 behind the axle; 16 g on the tail dome", f"{MASS:.0f} g; {YCOM:.0f} up, {AZ - ZCOM:.1f} behind; {MASS * (AZ - ZCOM) / 25:.0f} g on the tail dome"),
        ("The tail lifts at", "0.5 m/s²", f"{TIP:.1f} m/s²; the ramp stays 0.4 (at z 0 it would be 0.44)"),
        ("Speed at 45 rpm", "7 cm/s", f"{V_LOAD:.0f} cm/s, 23 % less push at the rim"),
        ("Hubs", "none: the wheel presses on the shaft", "5 mm over 4 mm brass tube, 9 long, soldered, boss inboard; the 4 mm bore takes the shaft, dimpled onto its flat"),
        ("Steel that shows", "none", "the two toothed rims"),
        ("Sound on the desk", "silent tyres", "a faint tick, 48 a second at speed; a mat or an O-ring over the teeth if it matters"),
        ("To buy", "five lines, about $126", "four lines, about $121: no Pololu order"),
        ("Templates and the physics page", "printed; written", "reprinted and rewritten for Rev B: the disc’s hub hole and the cradle marks moved, every number follows the gears"),
    ]
    if gear:
        cur = WHEEL
        configure("white"); views_a, _ = final_views(); configure(cur)
        compare = ('<div class="views two-up">'
                   f'<figure>{views_a[1][0]}<figcaption>Rev A, approved: the Ø31 white wheel at axle 16.</figcaption></figure>'
                   f'<figure>{views[1][0]}<figcaption>Rev B: Crumb’s Ø40 steel gear at axle {AY:g}, faced in ivory.</figcaption></figure></div>')
        pick = f"""<section class="pick">
  <h2>Rev A approved 2026-11-07 · Rev B, the gears, approved the same evening</h2>
  <p>Rev A, on Ø31 Pololu white wheels, was approved as drawn on 2026-11-07. The builder then asked for a metal gear instead and, shown this page, chose it the same evening. Rev B is the build: the two 64-tooth {A(LINKS['gears'], 'steel spur gears')} bought for Crumb, sitting in his bin, are the wheels, on 9 mm hubs of telescoped {A(LINKS['tube'], 'brass tube')}, each faced with an ivory card disc so the only steel that shows is the toothed rim. The axle rises to the gear’s radius and moves 1 mm forward; the motors, the driver and the amp go up with it. Nothing else moves.</p>
  {compare}
  <h3>What moves</h3>
  {tbl([(esc(a), esc(b), esc(c)) for a, b, c in changes], ["", "Rev A", "Rev B"], [0, 0, 0])}
  <p>Rev B is approved as drawn. Before any brass is cut, caliper the gears, which are on the bench: outer diameter, bore, plate thickness, length over the boss. The drawing takes the seller’s Ø40 and 9 mm; if the caliper disagrees, the axle height and the width move with it. A brass gear would be truer to the hoops (Kyouiku’s S50B60B, 60 teeth, module 0.5, Ø31, 3 mm bore, 2 mm face, would drop straight into Rev A’s geometry), but RS lists it out of stock and Accu’s page would not open; it stays a note. The templates and the physics page are moved to Rev B and the order sheet is four lines; firmware waits for the bench tests, as the house rule says.</p>
</section>"""
    else:
        pick = """<section class="pick">
  <h2>Approved 2026-11-07</h2>
  <p>This was step one for Mochi, approved as drawn: the form, the frame, the card, the wiring sheet, the parts and the checks. Three choices are baked in and easy to flip: the round screen (the owned square one fits the same front), the wheel faces sprayed canvas white (or left white), and the lidar in from the start (the owned 8×8 ranger on the brow is the shorter first version). Say yes, or say what moves, and then: the order, a card mock-up of the loaf and the hat, the bench tests, the frame. Education pages and firmware wait for the yes, as the house rule says.</p>
</section>"""

    page = f"""<title>Mochi Build</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{extra_css}</style>
<main>
<header style="display:grid;gap:10px">
  <span class="eyebrow">Desk robot · Mochi · step 1: the final build · {eyebrow}</span>
  <h1>Mochi: the loaf with a hat, drawn to build</h1>
  <p class="lede">Picked on 2026-11-07 from the three prototypes. An ivory card loaf inside two brass hoops, {OVERALL:.0f} × 56 × {LID_TOP:.0f} mm, about {MASS:.0f} g: a round colour face, a camera on the brow, a laser ranger beside it for the desk edge, the lidar worn as a hat, a speaker in the floor, the microphone on the controller, two gear motors {wheel_lede}, and the cell swapping through a hatch in the back. Every part placed to size, every wire pin to pin, every rod with a length. Crumb’s parts throughout; {n_buy} things to buy.</p>
  <p class="dims">Millimetres · x right, y up from the desk, z forward · front, side (face right) and top (face up) · dashed = hidden inside the skin · blue dashes the lidar plane, orange the ranger’s field</p>
</header>

<section>
  <h2>What it is</h2>
  <p>Two hoops of 1.5 mm {A(LINKS['rod15'], 'brass rod')}, 56 × 55 mm with r 4 corners, stand 56 mm apart; a strip of {A(LINKS['card'], 'cardstock')} sprayed {A(LINKS['white'], 'canvas white')} wraps round inside them and two discs close the sides, so the brass shows only as the body’s edges. Between the hoops, 1.0 mm rods carry everything: a floor rail and a keel with two brass domes under them, two cradles for the {A(LINKS['n20'], 'motors')}, a shelf for the {A(LINKS['holder'], 'cell holder')}, two cross rods for the {A(LINKS['lidar_amz'], 'lidar')}’s flange and one for the {A(LINKS['round_amz'], 'screen')}. The {A(LINKS['xiao'], 'XIAO ESP32-S3 Sense')} stands behind the screen with its lens on the brow; the {A(LINKS['rng1'], 'ranger')} looks down beside it; the {A(LINKS['drv'], 'motor driver')} stands on the right wall, the {A(LINKS['amp'], 'amplifier')} on the left, the {A(LINKS['gauge'], 'fuel gauge')} and the {A(LINKS['spk'], 'speaker')} lie on the floor, and over the cell the {A(LINKS['imu'], 'motion sensor')}, the lidar’s switch and the {A(LINKS['boost'], 'charger-boost')} stack up, its USB-C out the back between the button and the toggle.</p>
  <p>{palette}</p>
</section>

<section>
  <h2>The final views</h2>
  {figs(views)}
  <h3>Key</h3>{keyhtml}
</section>

<section>
  <h2>Inside</h2>
  <p>The packing, to size. Nothing overlaps (the script checks every pair of parts) and nothing but the lidar, the wheels and the domes leaves the skin. The centre of mass lands {AZ - ZCOM:.1f} mm behind the axle and {YCOM:.0f} mm up: the tail dome carries about {MASS * (AZ - ZCOM) / 25:.0f} g, the nose dome rides 1 mm up and bounds any pitch.</p>
  <div class="views two-up">{''.join(f'<figure>{svg}<figcaption>{esc(cap)}</figcaption></figure>' for svg, cap in inside)}</div>
  <h3>Mass</h3>{tbl(mass_rows, ["Part", "g"], [0, 1])}
</section>

<section>
  <h2>The frame and the card</h2>
  <div class="views">{''.join(f'<figure>{svg}<figcaption>{esc(cap)}</figcaption></figure>' for svg, cap in frame)}</div>
  <h3>Rod list</h3>{tbl(rods_rows, ["Piece", "Qty", "Rod", "Length, mm", "Where"], [0, 1, 1, 1, 0])}
  <p class="dims">About {ROD10:.0f} mm of 1.0 mm rod and 444 of 1.5 mm{hub_note}, all owned. Solder with the Harris flux, rinse, neutralise, before any board comes near. The hoops are bent on a paper template printed 1:1 from the hoop drawing.</p>
</section>

<section>
  <h2>Every wire, pin to pin</h2>
  <p>One cell, one toggle, one boost, one brain. The cell rail (red) runs through the fuel gauge into the charger-boost and straight to the motor driver. The 5 V rail (brass) comes off the charger-boost’s terminal block and feeds the XIAO through a Schottky, the amplifier, and the lidar through a switch the firmware closes a second after boot. Everything else is 3.3 V from the XIAO and four buses: SPI to the screen, I²S to the amp, UART from the lidar, and one I²C chain through the gauge, the driver, the ranger and the motion sensor.</p>
  <figure class="sheet">{the_sheet}<figcaption>The wiring sheet. Every connection is traceable pin to pin; crossings hop. The lane check in the generator passes with the pins of different nets at least 12 px apart.</figcaption></figure>
  <h3>Pin map, XIAO ESP32-S3 Sense (J3 cut)</h3>{tbl(pins_rows, ["Pin", "GPIO", "Net", "Job"], [1, 1, 1, 0])}
  <p class="dims">Fixed by the Sense board: camera on GPIO 10–18, 38–40, 47, 48; PDM microphone on 41 and 42; the SD slot’s chip select on 21. The microphone keeps I²S0 (PDM receive exists only there), the amp runs on I²S1. Eleven header pins, eleven jobs; the double tap on the body is the button.</p>
  <h3>Every net, and why</h3>{tbl(nets_rows, ["Net", "From", "To", "Wire", "Why"], [1, 0, 0, 0, 0])}
</section>

<section>
  <h2>The budget</h2>
  {tbl(budget_rows, ["Load", "Rail", "Typical", "Peak, mA"], [0, 0, 1, 1])}
  <p>From the cell: about 1.0 A roaming with the lidar on, so close to an hour; the lidar spinning only while it moves, about 1.5 h; parked with the face on and the lidar and camera off, 0.2 A, four to five hours. A full charge at 500 mA takes about 2.2 h, inside the charger’s six-hour timer, and the robot may keep running on the lead. The cell’s 2 A protection is the last resort: the firmware ramps drive and caps it at the level the stall test sets, so two stalled motors stay under 1.4 A.</p>
  <p>Speed: about 60 rpm at the cell’s voltage, 45 under load, {V_LOAD:.0f} cm/s on Ø{WD:.0f} wheels; the firmware drives slower than that on a desk.{torque_note}</p>
</section>

<section>
  <h2>Parts</h2>
  <p>{parts_intro}</p>
  {parts_html}
</section>

<section>
  <h2>What the firmware needs</h2>
  <ul>
    <li>Boot order: Wi-Fi up, screen on, chain scanned (0x36, 0x5D, 0x29, 0x68), then D2 high for the lidar, then the lidar parser on UART1 at 230400 ({A(LINKS['lds'], 'LDS library')} or the STL-19P packet: 0x54, 12 points, CRC8).</li>
    <li>Safety loop at 50 Hz: ranger over 90 mm or no target → brake, back 15 mm, turn; motion sensor pitch or roll over 5° in 50 ms → brake; lidar closer than 80 mm ahead → slow, turn.</li>
    <li>Drive: ramps of 0.4 m/s² ({TIP:.1f} lifts the tail), the cap from the stall test, turns in place, reversing limited to 15 mm because nothing looks back.</li>
    <li>Face: Pip’s eyes at 240 × 240 on the round screen, backlight PWM with a night floor and a parked-off state. Sound on I²S1, cap 50. Double tap on the body = the button.</li>
    <li>Sleep: lidar switch off, camera off, Wi-Fi on; the gauge’s state of charge on the face.</li>
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

{pick}
</main>"""
    OUT_HTML.write_text(page)
    print("wrote", OUT_HTML, OUT_HTML.stat().st_size, "bytes")

    # ---- the markdown record
    md = [f"# Mochi: step one, the final build (2026-11-07)\n",
          ("**Set aside late on 2026-11-07: the builder returned to Crumb (`CRUMB_BUILD.md`), which carries Mochi's electrics and wiring sheet.** Rev B (the gears as wheels) had been approved that evening, Rev A earlier the same day; nothing was bought or built. Rev A regenerates with `--wheel white`. " if gear else "**Approved as drawn 2026-11-07. Nothing bought, nothing built.** ")
          + f"Picked 2026-11-07 from the three prototypes in `CONCEPTS.md`. Page: `pages/mochi-build.html`, "
          f"generated by `pages/gen/mochi_build.py` (geometry, pins, nets, parts, checks all live there; the pin audit, the part-overlap audit and the "
          f"wiring sheet's lane check must pass for it to write). Published: [Mochi Build](https://claude.ai/artifact/SgXkkSjfQp7PcpkcBK1fbz).\n",
          f"## In numbers\n",
          f"- Envelope {OVERALL:.0f} W × 56 D × {LID_TOP:.0f} H mm; body 56 × 56 × 55 (hoops 56 × 55 r 4 at x ±28); wheels Ø{WD:.0f} × {WW:g} at axle {AY:g}, z {AZ:g}; clearance 5.75 under the floor skin.\n"
          f"- Mass about {MASS:.0f} g; centre of mass {AZ - ZCOM:.1f} mm behind the axle, {YCOM:.0f} mm up; tail dome at z −25 on the desk, nose dome at z +25 1 mm up.\n"
          f"- Lidar centre (0, z {LZ:.0f}); flange under the top skin at y 58.2–59.5 on two cross rods; body y 59.5–{LID_TOP:.0f}; scan plane {SCAN_Y:.0f} mm up.\n"
          f"- Speed about {V_LOAD:.0f} cm/s; run time about 1 h roaming with the lidar on, 1.5 h with it spinning only while moving, 4–5 h parked.\n",
          "## Parts placed (mm, axis-aligned boxes: x, y, z)\n", "| Part | x | y | z | g | Note |", "| --- | --- | --- | --- | ---: | --- |"]
    for n, x, y, z, m, note in PARTS_BOX:
        md.append(f"| {n} | {x[0]:g}..{x[1]:g} | {y[0]:g}..{y[1]:g} | {z[0]:g}..{z[1]:g} | {m} | {note} |")
    md += ["", "## Rods\n", "| Piece | Qty | Rod | mm each | Where |", "| --- | ---: | --- | ---: | --- |"] + [f"| {p} | {q} | {r} | {l} | {wh} |" for p, q, r, l, wh in RODS]
    md += ["", f"Card: the wrap 209 × 54.5 (back, top, front, floor with 3 mm arcs), openings: hatch 44 × 19 at y 21.5–40.5; button Ø4 at (−18, 50); USB-C 9 × 3.3 at (0, 50–53.3); toggle Ø6 at (18, 50); lidar Ø40 at z 0.5 with a 3 × 6 cable slot at x 20.5; face Ø33 at (0, 31); lens Ø3.5 on the top-front arc at x −5, 25° up; ranger slot 6 × 8 at x 15.4–21.4, y 41–49; speaker slot 11 × 18 at x 5–16, z −21–−10. Two discs 54.5 × 53.5 r 3.25 with Ø8 at (z {AZ:g}, y {AY:g}).\n",
           "## Pin map (XIAO ESP32-S3 Sense, J3 cut)\n", "| Pin | GPIO | Net | Job |", "| --- | --- | --- | --- |"] + [f"| {h} | {g} | {n} | {j} |" for h, g, n, j in PINS]
    md += ["", "## Nets\n", "| Net | From | To | Wire | Why |", "| --- | --- | --- | --- | --- |"] + [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in NETS]
    md += ["", "## Budget\n", "| Load | Rail | Typical mA | Peak mA |", "| --- | --- | ---: | ---: |"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in BUDGET]
    md += ["", "## Parts\n"]
    for group, rows in PARTS:
        md += [f"### {group}\n", "| Qty | Part | Where | Price | Note |", "| --- | --- | --- | --- | --- |"] + [f"| {q} | [{p}]({u}) | {wh} | {pr} | {n} |" if u else f"| {q} | {p} | {wh} | {pr} | {n} |" for q, p, u, wh, pr, n in rows] + [""]
    md += ["## Before power\n"] + [f"- **{a}.** {b}" for a, b in CHECKS] + ["", "## Build order\n"] + [f"{i + 1}. {s}" for i, s in enumerate(BUILD_ORDER)] + ["", "## Risks\n"] + [f"- **{a}.** {b}" for a, b in RISKS]
    if gear:
        md += ["", "## Rev B against Rev A\n", "| | Rev A | Rev B |", "| --- | --- | --- |"] + [f"| {a} | {b} | {c} |" for a, b, c in changes]
        md += ["", "Caliper the gears before anything is cut: outer diameter (the seller draws 40; 39.6 by the module), bore (5.0), plate thickness, length over the boss (9). The axle height is the radius plus 0.5 and the width 2 × (29.5 + the length over the boss). A brass gear would be truer to the hoops (Kyouiku S50B60B: 60 T, module 0.5, Ø31, 3 mm bore, 2 mm face; RS out of stock, Accu's page blocked) and would drop into Rev A's geometry unchanged; a note, not a line.\n"]
        md += ["## Choices baked in, easy to flip\n", "1. Round screen (buy) or the owned 1.54\" square on the same front.", "2. Lidar from the start, or the owned 8×8 ranger on the brow for a 35 mm shorter first version.", "", "The wheels are decided: Rev B's steel gears with ivory faces. Rev A's white wheels regenerate with `--wheel white` if they ever come back.", ""]
    else:
        md += ["", "## Choices baked in, easy to flip\n", "1. Round screen (buy) or the owned 1.54\" square on the same front.", "2. Wheel faces sprayed canvas white, or left white.", "3. Lidar from the start, or the owned 8×8 ranger on the brow for a 35 mm shorter first version.", ""]
    OUT_MD.write_text("\n".join(md))
    print("wrote", OUT_MD)

    if png_dir:
        png_dir = pathlib.Path(png_dir); png_dir.mkdir(parents=True, exist_ok=True)
        css = (HERE / "check_style.css").read_text() + " svg.blk text{font-size:12px} .sheet{} " + SHEET_CSS.replace("<style>", "").replace("</style>", "").replace("var(--fg)", "#23211c").replace("var(--muted)", "#6b665a").replace("var(--panel)", "#faf8f2").replace("var(--brass-dk)", "#7d6132").replace("var(--brass)", "#b4904f").replace("var(--warn)", "#98351e")
        items = [(f"final_{i}", svg) for i, (svg, cap) in enumerate(views)] + [(f"inside_{i}", svg) for i, (svg, cap) in enumerate(inside)] + [(f"frame_{i}", svg) for i, (svg, cap) in enumerate(frame)] + [("sheet", the_sheet)]
        for name, svg in items:
            p = png_dir / f"{name}.html"
            wide = 1540 if name == "sheet" else (1100 if name == "frame_1" else 720)
            p.write_text(f"<!doctype html><meta charset=utf-8><style>{css}</style><div style='width:{wide}px'>{svg}</div>")
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--window-size={wide + 20},{1130 if name == 'sheet' else 960}",
                            f"--screenshot={png_dir / (name + '.png')}", f"file://{p}"], check=True, capture_output=True, timeout=90)
        print("rendered", png_dir)


configure(WHEEL)

if __name__ == "__main__":
    if "--wheel" in sys.argv:
        configure(sys.argv[sys.argv.index("--wheel") + 1])
    write_all(sys.argv[sys.argv.index("--png") + 1] if "--png" in sys.argv else None)
