"""Mars rover, step 2: the science and engineering behind the approved sheet (Rev J, approved 2026-11-09).

Writes docs/pages/mars-rover-physics.html, docs/pages/print/mars-rover-physics.pdf (Letter portrait, black,
10 pt, figures at 72 % of the text width) and docs/PHYSICS.md (the same text without the figures).
Numbers come from build_page.py's D (dimensions), HD (the head), E (speed and budget), MASS and the drum it imports
from cad/drum.py, so the pages cannot drift; everything else is derived here and shown with its working. Every
assumption is a named number in the block below. Edit this script, not the outputs. Rev A's version (silicone tracks,
a mast tube, the lamp in the head) is in the repository's history."""
from __future__ import annotations

import math
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_page import APPROVED_H, APPROVED_J, D, DRUM, E, HD, L, MASS, STYLE, WHEEL, esc, hy, hz, rods_of  # noqa: E402

PAGES = HERE.parent
DOCS = PAGES.parent
OUT = PAGES / "mars-rover-physics.html"
PRINT = PAGES / "print"
BUILD_PAGE = "https://claude.ai/artifact/W8JUGpgYCxVsRdn1t4816z"

# ----------------------------------------------------------------------------- constants, each one a stated assumption
G = 9.81
MU = 0.3                # brass planks on a wooden or laminate desk
MU_SIL = 1.0            # a silicone track on the same desk, for comparison (Rev A's)
L_PATCH = D["pitch"]    # mm, each tread's flat contact run: the stretch between the drum centres
R_PITCH = D["drum_r"]   # mm, the tread's pitch line round a drum: the pin tubes' centres
B_GAUGE = 2 * D["teeth_x"]   # mm, tread centre to tread centre
STALL6 = 1.1            # kg·cm, the 150:1 low-power gearmotor at 6 V (Pololu)
FREE6 = 90.0            # rpm at 6 V (Pololu)
NOLOAD_A = 0.04         # A, its no-load current (Pololu, 6 V)
STALL6_A = 0.36         # A, stall current at 6 V (Pololu)
V_CELL = 3.7
DUTY_EX, V_EX = 0.6, 3.9     # an example: 60 % duty from a 3.9 V cell
R_CELL = 0.15           # Ω: the cell, its protection and the holder's springs
LDO_DROP = 0.2          # V: headroom the head's 3.3 V regulator needs at a few hundred mA
C_STORE = 220e-6        # F, beside the boost on the frame
PULSE_S = 50e-6         # s, one lamp on-time at 10 kHz and 50 %
AWG26 = 0.13            # Ω per metre
NECK_WIRE = 0.07        # m, each of BAT+ and GND up the neck's loop to the head
I_HEAD = 0.37 + E["tof8_peak"] / 1000   # A, the head at an image capture (Seeed: 366 mA), the 8x8 ranger at its worst
I_CHG = 0.5             # A
V_USB = 5.0
CC_SHARE = 0.8          # the share of the charge put in at constant current
C_BUS = 100e-12         # F, about 150 mm of bus and three inputs
R_PULL = 1 / (1 / 10e3 + 1 / 4.7e3 + 1 / 10e3)   # Ω: ranger 10 kΩ, display about 4.7 kΩ, motor controller 10 kΩ
TIMEOUT_S = 0.2
E_ST = 193e9            # Pa, 304 stainless
M_HEAD = next(m for n, m, _ in MASS if n.startswith("head")) / 1000   # kg (the sheet's mass table)
W_HEAD = HD["sh_x1"] - HD["sh_x0"]                                  # mm, the head: the camera board and the 8x8 ranger side by side
RG_HEAD = math.sqrt((W_HEAD ** 2 + D["x_d"] ** 2) / 12) / 1000      # m, the head as a block that wide and 15 mm deep, turning about its middle
SERVO_S60 = 0.10        # s per 60° at 4.8 V (FEETECH)
SERVO_STALL = 0.5       # kg·cm at 4.8 V
ETA = 0.85              # the boost's efficiency
C_MM_NS = 299.79        # mm of light per nanosecond
FOV = 27.0              # degrees, the ranger's full field of view
ROI = 15.0              # degrees, a narrowed field for the edge watch
T_SAMPLE = 0.02         # s, one reading every 20 ms
FOV8 = 60.0             # degrees, the 8x8 ranger's square field (ST: 90° on the diagonal)
ZONES8 = 8              # its zones across
RANGE8 = 3500.0         # mm, its longest reach, in the dark (ST)
HZ8 = 15.0              # frames a second at 8 x 8 (ST's figure for its field-of-view test)
SWEEP8 = 120.0          # degrees, the head's turn on the servo datasheet's pulses
SCAN_DPS = 30.0         # degrees a second, a slow scanning turn of the head
V_PIN_MAX = 3.6         # V, the controller's pins' absolute maximum (ESP32-S3: its 3.3 V supply plus 0.3)
REG_MA = 700.0          # mA, the controller's 3.3 V regulator (Seeed)
T_RAMP = 0.1            # s, the motor controller's deceleration to a stop, as configured
VF0, RS_LED = 2.6, 0.43 # V and Ω: the cool-white LED as 2.6 V plus 0.43 Ω (2.75 V at 350 mA, 2.9 at 700)
LM_350 = 139.0          # lm at 350 mA, the bin's minimum
BEAM = 23.0             # degrees, the narrow-spot lens on this LED
LENS_EFF = 0.85
STAR_KW = 60.0          # °C per W, a 14 mm aluminium disc in still air (the drone's figure)
HEAT_FRAC = 0.65        # the share of the LED's power that leaves as heat
AMC_DROP = 0.12         # V, the regulator's dropout at 350 mA
SAG = 1.0               # mm, the tread's sag on its top run once its last loop is closed
M3_ROOT = 2.39          # mm, an M3 screw's minor diameter
BLINK_S, PERIOD_S = 0.1, 2.0
BOOK = 15.0             # mm, a paperback under one tread
# SendCutSend's laser limits for 6061 (thickness, smallest hole, recommended hole), mm, read 2026-11-07
LASER_6061 = [(1.02, 0.356, 0.406), (1.60, 0.356, 0.635), (2.03, 0.457, 0.813), (2.54, 0.584, 1.016), (3.18, 0.813, 1.270),
              (4.75, 1.067, 1.905), (6.35, 1.448, 2.235), (8.00, 1.905, 2.286), (9.53, 2.159, 3.327), (12.70, 3.175, 4.318)]
BRIDGE_12 = 4.826       # mm, its smallest bridge at 1/2 in

# ----------------------------------------------------------------------------- the working
num = {}
num["W"] = D["mass"] / 1000 * G
num["M_turn"] = MU * num["W"] * L_PATCH / 4                     # N·mm
num["M_sil"] = MU_SIL * num["W"] * L_PATCH / 4
num["F_track"] = num["M_turn"] / B_GAUGE                        # N per tread
num["tau_turn"] = num["F_track"] * R_PITCH                      # N·mm = mN·m
num["stall37"] = STALL6 * V_CELL / 6 * 98.1                    # mN·m
num["stall6"] = STALL6 * 98.1
num["margin"] = num["stall37"] / num["tau_turn"]
num["rpm37"] = FREE6 * V_CELL / 6
num["stall_a37"] = STALL6_A * V_CELL / 6
num["a_turn"] = NOLOAD_A + (num["stall_a37"] - NOLOAD_A) * num["tau_turn"] / num["stall37"]
num["rpm_turn"] = num["rpm37"] * (1 - num["tau_turn"] / num["stall37"])
num["r_pivot"] = math.hypot(D["tr_end"], D["pin_x1"])
num["climb"] = math.degrees(math.atan(MU))
num["climb_sil"] = math.degrees(math.atan(MU_SIL))
num["v_avg"] = DUTY_EX * V_EX
num["rise_ns"] = 0.8473 * R_PULL * C_BUS * 1e9
num["timeout_mm"] = TIMEOUT_S * E["speed"]
num["Wh"] = 3.6 * E["cell_mah"] / 1000
num["sag_1A"] = R_CELL * 1.0
num["park_v"] = 3.4
num["rail_at_park"] = num["park_v"] - R_CELL * 0.5 - LDO_DROP
num["dv_cap"] = 0.35 * PULSE_S / C_STORE * 1000                 # mV
num["neck_mv"] = 2 * NECK_WIRE * AWG26 * I_HEAD * 1000
num["cc_h"] = CC_SHARE * E["cell_mah"] / (I_CHG * 1000)
num["chg_heat"] = (V_USB - 3.8) * I_CHG
# the drum
num["seat"] = 2 * DRUM.SEAT_R
num["play"] = DRUM.SEAT_R - DRUM.PIN_D / 2
num["rod_seat"] = 1.0 + 0.25
num["hole_38"] = next(h for t, h, _ in LASER_6061 if abs(t - 9.53) < 0.01)
num["hole_12"] = next(h for t, h, _ in LASER_6061 if abs(t - 12.7) < 0.01)
num["rod_max_t"] = max(t for t, h, _ in LASER_6061 if h <= num["rod_seat"])
num["chordal"] = (1 - math.cos(math.pi / DRUM.Z)) * 100        # %
num["chordal20"] = (1 - math.cos(math.pi / 20)) * 100
num["chordal11"] = (1 - math.cos(math.pi / 11)) * 100
num["patter_hz"] = DRUM.Z * E["rpm"] * E["load"] / 60
num["flank_share"] = math.tan(DRUM.FLANK) * 100
num["low_share"] = (D["drums_g"] + D["tread_g"]) / D["mass"] * 100
# the servo and the head
num["deg_per_us"] = 120 / 1200
num["sweep_s"] = SERVO_S60 * 2
num["J_head"] = M_HEAD * RG_HEAD ** 2
alpha = 4 * math.radians(60) / SERVO_S60 ** 2
num["head_torque_kgcm"] = num["J_head"] * alpha / 0.0981
num["head_share"] = num["head_torque_kgcm"] / SERVO_STALL * 100
num["boost_run"] = E["srv_run"]
num["boost_stall"] = E["srv_stall"]
# the ranger
num["slant"] = D["tof_slant"]
num["ns"] = 2 * D["tof_slant"] / C_MM_NS
num["ps_per_mm"] = 2 / C_MM_NS * 1000
num["near"] = D["tof_y"] / math.tan(math.radians(D["tof_tilt"] + FOV / 2))
num["far"] = D["tof_y"] / math.tan(math.radians(D["tof_tilt"] - FOV / 2))
num["near_slant"] = D["tof_y"] / math.sin(math.radians(D["tof_tilt"] + FOV / 2))
num["near_roi"] = D["tof_y"] / math.tan(math.radians(D["tof_tilt"] + ROI / 2))
num["roi_slant"] = D["tof_y"] / math.sin(math.radians(D["tof_tilt"] + ROI / 2))
num["far_roi"] = D["tof_y"] / math.tan(math.radians(D["tof_tilt"] - ROI / 2))
num["mm_per_sample"] = E["speed"] * T_SAMPLE
num["stop_mm"] = num["mm_per_sample"] + E["speed"] * T_RAMP / 2
num["warn_x"] = D["tof_reach"] / num["stop_mm"]
# the 8x8 ranger in the head
num["zone_deg"] = FOV8 / ZONES8
num["zone_1m"] = 2 * 1000 * math.tan(math.radians(num["zone_deg"] / 2))   # mm, one zone's width at a metre
num["cover"] = SWEEP8 + FOV8
num["ns_far8"] = 2 * RANGE8 / C_MM_NS
num["sweep8_s"] = SWEEP8 / SCAN_DPS
num["frames_sweep"] = HZ8 * num["sweep8_s"]
num["deg_per_frame"] = SCAN_DPS / HZ8
num["rail_share"] = E["rail3v3_peak"] / REG_MA * 100
# the flashlight
r_res = (4.2 - (VF0 + RS_LED * 0.35)) / 0.35
num["r_res"] = r_res


def i_resistor(v):
    return max(0.0, (v - VF0) / (r_res + RS_LED))


num["i37"] = i_resistor(3.7) * 1000
num["i33"] = i_resistor(3.3) * 1000
num["vf350"] = VF0 + RS_LED * 0.35
num["v_drop"] = num["vf350"] + AMC_DROP
num["p_reg42"] = (4.2 - num["vf350"]) * 0.35
num["p_led"] = num["vf350"] * 0.35
num["heat_cap"] = num["p_led"] * HEAT_FRAC * E["lamp_cap"]
num["dT"] = num["heat_cap"] * STAR_KW
sr = 2 * math.pi * (1 - math.cos(math.radians(BEAM / 2)))
num["cd"] = LM_350 * LENS_EFF / sr
num["lux50"] = num["cd"] / 0.25
num["spot50"] = 2 * 50 * math.tan(math.radians(BEAM / 2))
num["beacon_avg"] = E["beacon"] * BLINK_S / PERIOD_S
# tipping and the frame
num["head_share_mass"] = M_HEAD * 1000 / D["mass"] * 100
num["brake_g"] = E["speed"] / 1000 / T_RAMP / G
num["brake_deg"] = math.degrees(math.atan(num["brake_g"]))
num["book_deg"] = math.degrees(math.asin(BOOK / B_GAUGE))
w_tread = D["tread_g"] / 2 / 1000 * G / (D["planks"] * D["plank_p"])          # N per mm of tread
num["tension"] = w_tread * L_PATCH ** 2 / (8 * SAG)
I15 = math.pi * (D["rod"] / 1000) ** 4 / 64
L_RAIL = (D["idler_z"] - D["r2_z"]) / 1000
num["euler"] = math.pi ** 2 * E_ST * I15 / L_RAIL ** 2
num["euler_margin"] = num["euler"] / num["tension"]
num["stiff15"] = (1.5 / 1.0) ** 4
num["front_share"] = (D["cg"][2] - D["drive_z"]) / D["pitch"]
num["idler_N"] = num["W"] * num["front_share"] / 2
num["screw_lever"] = D["drum_x0"] + D["drum_w"] / 2 - D["rail_x"]
num["screw_MPa"] = num["idler_N"] * num["screw_lever"] / (math.pi * M3_ROOT ** 3 / 32)


def f(x, d=0):
    return f"{x:.{d}f}"


# ----------------------------------------------------------------------------- figure helpers (the satellite's)
def T(x, y, s, cls="fn", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


FIG_CSS = ("<style>"
           ".ink{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
           ".thin{fill:none;stroke:var(--ink);stroke-width:1.1;stroke-linecap:round}"
           ".grey{fill:none;stroke:var(--ink-2);stroke-width:1.1;stroke-dasharray:4 3}"
           ".greyl{fill:none;stroke:var(--ink-2);stroke-width:1.1}"
           ".ray{fill:none;stroke:var(--warn);stroke-width:1.6}"
           ".rayhead{fill:var(--warn);stroke:none}"
           ".sig{fill:none;stroke:var(--signal);stroke-width:1.6}"
           ".sighead{fill:var(--signal);stroke:none}"
           ".cone{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1;stroke-dasharray:4 3}"
           ".solid{fill:var(--ink);stroke:none}"
           ".dark{fill:var(--ink);stroke:none}"
           ".paper{fill:var(--paper);stroke:var(--ink);stroke-width:1.2}"
           ".soft{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.2}"
           ".band{fill:var(--brass-soft);stroke:none}"
           ".bar{fill:var(--ink);stroke:none}"
           ".bar2{fill:var(--ink-2);stroke:none}"
           ".bar3{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1}"
           ".bar4{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1}"
           ".bar5{fill:var(--warn-soft);stroke:var(--warn);stroke-width:1}"
           ".h{font:700 13px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".lab{font:700 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".num{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink)}"
           ".onink{font:700 11px 'JetBrains Mono',monospace;fill:var(--paper)}"
           ".pix{fill:var(--paper)}"
           "</style>")


def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{FIG_CSS}{body}</svg>'


def arrow(x0, y0, x1, y1, cls="ray", head="rayhead", size=8):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx_, hy_ = x1 - size * math.cos(ang), y1 - size * math.sin(ang)
    px, py = size / 2 * math.sin(ang), -size / 2 * math.cos(ang)
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="{cls}"/>'
            f'<path d="M{x1:.1f},{y1:.1f} L{hx_+px:.1f},{hy_+py:.1f} L{hx_-px:.1f},{hy_-py:.1f} z" class="{head}"/>')


def axes(ox, oy, w, h):
    return f'<line x1="{ox}" y1="{oy}" x2="{ox+w}" y2="{oy}" class="ink"/><line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-h}" class="ink"/>'


def poly(pts, cls):
    return '<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" class="{cls}"/>'


def rect(x0, y0, x1, y1, cls, rx=0):
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    return f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{xb - xa:.1f}" height="{yb - ya:.1f}" rx="{rx}" class="{cls}"/>'


# ----------------------------------------------------------------------------- the figures
def fig_turn():
    s = 2.0
    cx, cy = 160, 158
    X = lambda x: cx + x * s            # noqa: E731
    Y = lambda z: cy - z * s            # noqa: E731
    o = [T(20, 24, "Turning on the spot, seen from above", "h")]
    for sg in (-1, 1):
        o.append(rect(X(sg * D["tr_x0"]), Y(D["tr_end"]), X(sg * D["tr_x1"]), Y(-D["tr_end"]), "bar2", 6))
        o.append(rect(X(sg * D["tr_x0"]), Y(L_PATCH / 2), X(sg * D["tr_x1"]), Y(-L_PATCH / 2), "dark", 2))
        for z in (-21, -14, -7, 7, 14, 21):
            x_mid = X(sg * D["teeth_x"])
            d_ = 1 if z > 0 else -1
            o.append(arrow(x_mid - d_ * 9, Y(z), x_mid + d_ * 9, Y(z), "sig", "sighead", 6))
    o.append(arrow(X(D["teeth_x"]), Y(-10), X(D["teeth_x"]), Y(32), "ray", "rayhead", 9))
    o.append(arrow(X(-D["teeth_x"]), Y(10), X(-D["teeth_x"]), Y(-32), "ray", "rayhead", 9))
    o.append(f'<circle cx="{cx}" cy="{cy}" r="4" class="solid"/>')
    o.append(f'<path d="M{cx + 26},{cy - 50} A56,56 0 0 0 {cx - 26},{cy - 50}" class="greyl"/>')
    o.append(arrow(cx - 18, cy - 54, cx - 27, cy - 49, "greyl", "rayhead", 7))
    o.append(T(X(D["teeth_x"]), Y(D["tr_end"]) - 8, f"F = {num['F_track']:.2f} N forward", "num", "middle"))
    o.append(T(X(-D["teeth_x"]), Y(-D["tr_end"]) + 18, f"F = {num['F_track']:.2f} N back", "num", "middle"))
    o.append(T(cx, Y(-D["tr_end"]) + 36, f"treads {B_GAUGE:.0f} mm apart, centre to centre", "fn", "middle"))
    rx = 360
    lines = [(f"dark: the flat contact run, {L_PATCH:.0f} mm a tread", "fn"),
             ("blue: the friction on it while it scrubs", "fn"),
             ("sideways, one way ahead of the centre,", "fn"),
             ("the other way behind; the same size", "fn"),
             ("everywhere, its lever growing with distance", "fn"), ("", "fn"),
             (f"resisting moment μWL/4 = {num['M_turn']:.1f} N·mm", "num"),
             (f"F × {B_GAUGE:.0f} mm = the moment: F = {num['F_track']:.2f} N", "num"),
             (f"at the drum: {num['tau_turn']:.1f} mN·m", "num"),
             (f"the motor has {num['stall37']:.0f} at stall: {num['margin']:.0f}×", "lab")]
    for i, (t, c) in enumerate(lines):
        if t:
            o.append(T(rx, 66 + i * 17, t, c))
    return svg(640, 316, "".join(o), "Skid steering")


def fig_motor():
    ox, oy, w, h = 64, 250, 420, 190
    X = lambda t: ox + t / 115 * w      # noqa: E731
    Y = lambda r: oy - r / 100 * h      # noqa: E731
    o = [T(20, 24, "The gearmotor's straight line, at 6 V and at the cell's 3.7 V", "h"), axes(ox, oy, w, h)]
    for t in range(0, 111, 20):
        o.append(f'<line x1="{X(t):.1f}" y1="{oy}" x2="{X(t):.1f}" y2="{oy+5}" class="thin"/>')
        o.append(T(X(t), oy + 18, f"{t}", "num", "middle"))
    o.append(T(ox + w / 2, oy + 36, "torque at the output shaft, mN·m", "fn", "middle"))
    for r in (0, 25, 50, 75, 100):
        o.append(f'<line x1="{ox-5}" y1="{Y(r):.1f}" x2="{ox}" y2="{Y(r):.1f}" class="thin"/>')
        o.append(T(ox - 8, Y(r) + 4, f"{r}", "num", "end"))
    o.append(T(ox - 8, oy - h - 8, "rpm", "fn", "end"))
    o.append(f'<line x1="{X(0)}" y1="{Y(FREE6):.1f}" x2="{X(num["stall6"]):.1f}" y2="{Y(0)}" class="grey"/>')
    o.append(f'<line x1="{X(0)}" y1="{Y(num["rpm37"]):.1f}" x2="{X(num["stall37"]):.1f}" y2="{Y(0)}" class="ink"/>')
    o.append(f'<circle cx="{X(num["tau_turn"]):.1f}" cy="{Y(num["rpm_turn"]):.1f}" r="5" class="solid"/>')
    o.append(f'<line x1="{X(num["tau_turn"]):.1f}" y1="{Y(num["rpm_turn"]) + 5:.1f}" x2="{X(9):.1f}" y2="{Y(17):.1f}" class="greyl"/>')
    o.append(T(X(9), Y(14), f"turning: {num['tau_turn']:.1f} mN·m,", "fn"))
    o.append(T(X(9), Y(14) + 14, f"{num['rpm_turn']:.0f} rpm, about {num['a_turn']*1000:.0f} mA", "fn"))
    lx = 360
    o.append(f'<line x1="{lx}" y1="62" x2="{lx + 26}" y2="62" class="grey"/>'); o.append(T(lx + 34, 66, f"6 V: {FREE6:.0f} rpm free, {num['stall6']:.0f} stall", "fn"))
    o.append(f'<line x1="{lx}" y1="82" x2="{lx + 26}" y2="82" class="ink"/>'); o.append(T(lx + 34, 86, f"3.7 V: {num['rpm37']:.0f} rpm free, {num['stall37']:.0f} stall", "lab"))
    o.append(T(20, 304, f"Current follows torque: {NOLOAD_A*1000:.0f} mA free, {num['stall_a37']*1000:.0f} mA stalled at 3.7 V.", "fn"))
    o.append(T(20, 318, f"Tread speed = rpm × π × {2*R_PITCH:.1f} mm, the pins' line: {E['speed_free']:.0f} mm/s free at 3.7 V.", "fn"))
    return svg(660, 330, "".join(o), "Torque against speed")


def fig_bridge():
    o = [T(20, 24, "One H-bridge, and what the motor sees", "h")]
    x0, y0, w, h = 70, 60, 190, 170
    xl, xr, yt, yb, ym = x0, x0 + w, y0, y0 + h, y0 + h / 2
    o.append(f'<line x1="{xl-20}" y1="{yt}" x2="{xr+20}" y2="{yt}" class="ink"/>')
    o.append(f'<line x1="{xl-20}" y1="{yb}" x2="{xr+20}" y2="{yb}" class="ink"/>')
    o.append(T(xl - 24, yt + 4, "cell", "lab", "end")); o.append(T(xl - 24, yb + 4, "GND", "lab", "end"))
    for (x, ya, yb_, closed, lab) in ((xl, yt, ym - 18, True, "1"), (xr, yt, ym - 18, False, "2"), (xl, ym + 18, yb, False, "3"), (xr, ym + 18, yb, True, "4")):
        o.append(f'<line x1="{x}" y1="{ya}" x2="{x}" y2="{ya + 18}" class="ink"/>')
        o.append(f'<line x1="{x}" y1="{yb_ - 18}" x2="{x}" y2="{yb_}" class="ink"/>')
        if closed:
            o.append(f'<line x1="{x}" y1="{ya + 18}" x2="{x}" y2="{yb_ - 18}" class="ink"/>')
        else:
            o.append(f'<line x1="{x}" y1="{ya + 18}" x2="{x + 14}" y2="{yb_ - 22}" class="ink"/>')
        o.append(f'<circle cx="{x}" cy="{ya + 18}" r="3" class="solid"/><circle cx="{x}" cy="{yb_ - 18}" r="3" class="solid"/>')
        o.append(T(x - 10, (ya + yb_) / 2 + 4, lab, "num", "end"))
    o.append(f'<line x1="{xl}" y1="{ym - 18}" x2="{xl}" y2="{ym + 18}" class="ink"/><line x1="{xr}" y1="{ym - 18}" x2="{xr}" y2="{ym + 18}" class="ink"/>')
    o.append(f'<line x1="{xl}" y1="{ym}" x2="{xl + 65}" y2="{ym}" class="ink"/><line x1="{xr - 65}" y1="{ym}" x2="{xr}" y2="{ym}" class="ink"/>')
    o.append(f'<circle cx="{(xl + xr) / 2}" cy="{ym}" r="30" class="paper"/>')
    o.append(T((xl + xr) / 2, ym + 5, "M", "lab", "middle"))
    o.append(arrow(xl + 7, yt + 30, xl + 7, ym - 4, "ray", "rayhead", 7))
    o.append(arrow(xl + 26, ym - 8, xl + 58, ym - 8, "ray", "rayhead", 7))
    o.append(arrow(xr - 58, ym + 8, xr - 26, ym + 8, "ray", "rayhead", 7))
    o.append(arrow(xr - 7, ym + 4, xr - 7, yb - 30, "ray", "rayhead", 7))
    o.append(T(x0 - 40, yb + 26, "1 and 4 closed: forward. 2 and 3: reverse.", "fn"))
    o.append(T(x0 - 40, yb + 40, "3 and 4 closed: the motor brakes on itself.", "fn"))
    px0, py0, pw, ph = 360, 252, 220, 92
    PX = lambda t: px0 + t / 3.0 * pw        # noqa: E731
    PY = lambda v: py0 - v / V_EX * ph       # noqa: E731
    for i, line in enumerate((f"{DUTY_EX*100:.0f} % duty: the bridge is on for {DUTY_EX*100:.0f} %",
                              "of each 50 µs period. The winding's",
                              "inductance smooths the current, so the",
                              f"motor runs as if fed {num['v_avg']:.1f} V steady.")):
        o.append(T(px0 - 30, 66 + i * 15, line, "fn"))
    o.append(axes(px0, py0, pw, ph + 14))
    pts = [(PX(0), PY(0))]
    for k in range(3):
        pts += [(PX(k), PY(V_EX)), (PX(k + DUTY_EX), PY(V_EX)), (PX(k + DUTY_EX), PY(0)), (PX(k + 1), PY(0))]
    o.append(poly(pts, "ink"))
    o.append(f'<line x1="{px0}" y1="{PY(num["v_avg"]):.1f}" x2="{px0 + pw}" y2="{PY(num["v_avg"]):.1f}" class="grey"/>')
    o.append(T(px0 - 6, PY(V_EX) + 4, f"{V_EX} V", "num", "end"))
    o.append(T(px0 + pw + 4, PY(num["v_avg"]) + 4, f"{num['v_avg']:.1f} V", "num"))
    o.append(T(px0, py0 + 18, "three periods at 20 kHz", "fn"))
    return svg(640, 290, "".join(o), "H-bridge and PWM")


def fig_budget():
    o = [T(20, 24, "Where the cell's current goes, by mode", "h")]
    base_parts = [("ranger", E["tof"], "bar4"), ("display", E["oled"], "bar4"), ("servo at rest + boost", E["srv_idle"] + E["boost_q"], "bar3"), ("motor ctrl, beacon", E["motoron"] + E["beacon"] * E["beacon_duty"], "bar4")]
    mv = 0.4 * (E["srv_run"] - E["srv_idle"])
    modes = [("parked, watching", [("controller", E["xiao_wifi"], "bar")] + base_parts, E["parked_h"]),
             ("exploring", [("controller", E["xiao_cam"], "bar"), ("motors", 2 * E["mot_run"], "bar2")] + base_parts + [("servo moving", mv, "bar3")], E["explore_h"]),
             ("at night", [("controller", E["xiao_cam"], "bar"), ("motors", 2 * E["mot_run"], "bar2")] + base_parts + [("servo moving", mv, "bar3"), ("flashlight", E["lamp"] * E["lamp_cap"], "bar5")], E["night_h"])]
    sx = 0.62
    for i, (name, parts, hours) in enumerate(modes):
        y = 56 + i * 64
        o.append(T(20, y + 16, name, "lab"))
        x = 140
        for lab, ma, cls in parts:
            o.append(rect(x, y, x + ma * sx, y + 24, cls))
            if ma * sx > 40:
                o.append(T(x + 5, y + 16, f"{ma:.0f}", "onink" if cls in ("bar", "bar2") else "num"))
            x += ma * sx
        tot = sum(p[1] for p in parts)
        o.append(T(x + 8, y + 16, f"{tot:.0f} mA, {hours:.1f} h", "num"))
    ly = 268
    for k, (lab, cls) in enumerate((("controller", "bar"), ("motors", "bar2"), ("servo, boost", "bar3"), ("ranger, display", "bar4"), ("flashlight", "bar5"))):
        lx = 20 + k * 128
        o.append(rect(lx, ly - 10, lx + 14, ly + 2, cls)); o.append(T(lx + 20, ly, lab, "fn"))
    o.append(T(20, 294, f"Hours = {E['cell_mah']} mAh × {E['usable']:.0%} usable ÷ the mode's current. The controller is the biggest load in every mode.", "fn"))
    return svg(660, 306, "".join(o), "The budget by mode")


def fig_charge():
    ox, oy, w, h = 64, 236, 430, 176
    tmax = 2.6
    X = lambda t: ox + t / tmax * w           # noqa: E731
    YI = lambda i: oy - i / 520 * h           # noqa: E731
    YV = lambda v: oy - (v - 3.0) / 1.6 * h   # noqa: E731
    o = [T(20, 24, f"A charge at {I_CHG*1000:.0f} mA: constant current, then constant voltage", "h"), axes(ox, oy, w, h)]
    o.append(f'<line x1="{ox + w}" y1="{oy}" x2="{ox + w}" y2="{oy - h}" class="ink"/>')
    for t in (0, 0.5, 1, 1.5, 2, 2.5):
        o.append(f'<line x1="{X(t):.1f}" y1="{oy}" x2="{X(t):.1f}" y2="{oy+5}" class="thin"/>')
        o.append(T(X(t), oy + 18, f"{t:g} h", "num", "middle"))
    for i in (0, 250, 500):
        o.append(T(ox - 8, YI(i) + 4, f"{i}", "num", "end"))
    o.append(T(ox - 8, oy - h - 8, "mA", "fn", "end"))
    for v in (3.0, 3.6, 4.2):
        o.append(T(ox + w + 8, YV(v) + 4, f"{v:.1f} V", "num"))
    tcc, tau = num["cc_h"], 0.25
    ipts, vpts = [], []
    t = 0.0
    while t <= tmax:
        i = I_CHG * 1000 if t < tcc else I_CHG * 1000 * math.exp(-(t - tcc) / tau)
        v = 3.55 + 0.65 * (t / tcc) ** 1.6 if t < tcc else 4.2
        ipts.append((X(t), YI(i))); vpts.append((X(t), YV(v)))
        t += 0.02
    o.append(poly(ipts, "ink")); o.append(poly(vpts, "grey"))
    o.append(f'<line x1="{X(tcc):.1f}" y1="{oy}" x2="{X(tcc):.1f}" y2="{oy - h}" class="greyl"/>')
    o.append(T(X(0.05), YI(500) - 8, "current, held at 500 mA", "lab"))
    o.append(T(X(0.05), YV(3.55) + 18, "the cell's voltage, dashed", "fn"))
    o.append(T(X(tcc) + 8, YV(4.2) + 16, "held at 4.2 V", "fn"))
    o.append(T(X(2.0) + 6, YI(I_CHG * 1000 * math.exp(-(2.0 - tcc) / tau)) - 6, "the current tapers", "fn"))
    o.append(T(20, 278, f"About {num['cc_h']:.1f} h at {I_CHG*1000:.0f} mA to 4.2 V, then the taper; about {E['charge_h']:.1f} h in all. Red light, then green.", "fn"))
    return svg(640, 290, "".join(o), "CC/CV charging")


def fig_drum():
    o = [T(20, 24, "A drum's seats, and the laser's limit that chose its pins", "h")]
    s = 5.6                                                  # px per mm: the drum face on, its planks round the lower half
    cx, cy = 128, 140
    step = 2 * math.pi / DRUM.Z
    th0 = math.pi - step / 2                                 # a seat under each plank drawn below
    c0, s0 = math.cos(th0), math.sin(th0)
    pts = [(cx + (x * c0 - y * s0) * s, cy - (x * s0 + y * c0) * s) for x, y in WHEEL]
    o.append('<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + 'Z" class="paper"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{(DRUM.RF - 0.6) * s:.1f}" class="band"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{2.0 * s:.1f}" class="soft"/><circle cx="{cx}" cy="{cy}" r="{1.5 * s:.1f}" class="paper"/>')
    for j in range(DRUM.Z // 2 + 1):
        th = j * step
        px_, py_ = cx + D["drum_r"] * math.sin(th - math.pi / 2) * s, cy + D["drum_r"] * math.cos(th - math.pi / 2) * s
        for k, (rz, ry) in enumerate(rods_of(0.0, 0.0, th - math.pi / 2)):
            r = DRUM.PIN_D / 2 if k == 0 else 0.5
            o.append(f'<circle cx="{px_ + rz * s:.1f}" cy="{py_ - ry * s:.1f}" r="{r * s:.1f}" class="{"soft" if k == 0 else "bar2"}"/>')
        o.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="{(DRUM.PIN_D / 2 - DRUM.TUBE_WALL) * s:.1f}" class="paper"/>')
    o.append(T(cx, cy - DRUM.R_TIP * s - 10, f"{DRUM.Z} seats, {2 * DRUM.R_TIP:.1f} mm across", "lab", "middle"))
    o.append(T(cx, cy + 34, "ivory face", "fn", "middle"))
    for i, line in enumerate((f"Seat {num['seat']:.2f} mm, tube {DRUM.PIN_D:.2f} mm:", f"{num['play']:.2f} mm all round for ±0.13.",
                              f"Planks {D['plank_p']:.2f} apart; flanks {math.degrees(DRUM.FLANK):.0f}°.")):
        o.append(T(20, 268 + i * 14, line, "fn"))
    # right: SendCutSend's smallest hole against plate thickness, 6061
    ox, oy, w, h = 330, 236, 280, 170
    X = lambda t: ox + t / 13.0 * w           # noqa: E731
    Y = lambda d: oy - d / 5.0 * h            # noqa: E731
    o.append(axes(ox, oy, w, h))
    for t in (0, 3.18, 6.35, 9.53, 12.7):
        o.append(f'<line x1="{X(t):.1f}" y1="{oy}" x2="{X(t):.1f}" y2="{oy + 5}" class="thin"/>')
        o.append(T(X(t), oy + 18, f"{t:g}", "num", "middle"))
    o.append(T(ox + w / 2, oy + 34, "plate thickness, mm (6061 at SendCutSend)", "fn", "middle"))
    for d in (0, 1, 2, 3, 4, 5):
        o.append(f'<line x1="{ox - 5}" y1="{Y(d):.1f}" x2="{ox}" y2="{Y(d):.1f}" class="thin"/>')
        o.append(T(ox - 8, Y(d) + 4, f"{d}", "num", "end"))
    o.append(T(ox, oy - h - 10, "the smallest hole it cuts, mm", "fn"))
    o.append(poly([(X(t), Y(hl)) for t, hl, _ in LASER_6061], "ink"))
    o.append(poly([(X(t), Y(rec)) for t, _, rec in LASER_6061], "grey"))
    for t, hl, _ in LASER_6061:
        o.append(f'<circle cx="{X(t):.1f}" cy="{Y(hl):.1f}" r="2.6" class="solid"/>')
    for d, lab in ((num["rod_seat"], "a 1 mm rod's seat"), (num["seat"], "the tube's seat")):
        o.append(f'<line x1="{ox}" y1="{Y(d):.1f}" x2="{ox + w}" y2="{Y(d):.1f}" class="sig"/>')
        txt = f"{lab}, {d:.2f}"
        o.append(rect(ox + 4, Y(d) - 17, ox + 10 + len(txt) * 6.1, Y(d) - 3, "pix"))
        o.append(T(ox + 7, Y(d) - 6, txt, "fn"))
    o.append(f'<line x1="{X(9.53):.1f}" y1="{oy}" x2="{X(9.53):.1f}" y2="{oy - h}" class="greyl"/>')
    o.append(T(X(9.53) - 4, oy - 8, "3/8 in: each half", "lab", "end"))
    o.append(T(ox + w / 2, oy + 50, "solid: the smallest; dashed: recommended", "fn", "middle"))
    return svg(640, 312, "".join(o), "Drum seats and laser limits")


def fig_servo():
    o = [T(20, 24, "Inside the servo: a motor told where to stop", "h")]
    boxes = [(20, 60, 110, "pulse from D0", "num"), (160, 60, 110, "comparator", "lab"), (300, 60, 90, "motor", "lab"), (420, 60, 90, "gears", "lab"), (540, 60, 90, "the head", "lab")]
    for (x, y, w_, lab, cls) in boxes:
        o.append(rect(x, y, x + w_, y + 40, "paper", 6))
        o.append(T(x + w_ / 2, y + 25, lab, cls, "middle"))
    for (x0, x1) in ((130, 160), (270, 300), (390, 420), (510, 540)):
        o.append(arrow(x0, 80, x1, 80, "ink", "solid", 7))
    o.append(rect(420, 130, 530, 170, "paper", 6)); o.append(T(475, 155, "potentiometer", "lab", "middle"))
    o.append(poly([(585, 100), (585, 150), (530, 150)], "ink"))
    o.append(arrow(420, 150, 222, 150, "ink", "solid", 7))
    o.append(poly([(215, 150), (215, 104)], "ink"))
    o.append(arrow(215, 116, 215, 102, "ink", "solid", 7))
    o.append(T(320, 144, "where the output is", "fn", "middle"))
    ox, oy, w = 60, 236, 520
    X = lambda us: ox + (us - 900) / 1200 * w        # noqa: E731
    o.append(f'<line x1="{ox}" y1="{oy}" x2="{ox + w}" y2="{oy}" class="ink"/>')
    for us, deg in ((900, "−60°"), (1500, "0°"), (2100, "+60°")):
        o.append(f'<line x1="{X(us):.1f}" y1="{oy - 6}" x2="{X(us):.1f}" y2="{oy + 6}" class="ink"/>')
        o.append(T(X(us), oy + 22, f"{us} µs", "num", "middle")); o.append(T(X(us), oy - 12, deg, "lab", "middle"))
    o.append(T(ox + w / 2, oy + 40, f"the pulse width sets the angle: {num['deg_per_us']:.1f}° per µs, a pulse every 20 ms", "fn", "middle"))
    return svg(650, 290, "".join(o), "Servo loop")


def fig_tof():
    o = [T(20, 24, "The ranger's look at the desk, and what it counts", "h")]
    s = 2.6
    ox, oy = 60, 214
    X = lambda z: ox + z * s          # noqa: E731
    Y = lambda y: oy - y * s          # noqa: E731
    hy_ = D["tof_y"]
    edge = 110.0
    o.append(f'<line x1="{X(-12):.1f}" y1="{Y(0):.1f}" x2="{X(edge):.1f}" y2="{Y(0):.1f}" class="ink"/>')
    o.append(f'<line x1="{X(edge):.1f}" y1="{Y(0):.1f}" x2="{X(edge):.1f}" y2="{Y(-8):.1f}" class="ink"/>')
    o.append(T(X(edge) - 4, Y(-6), "edge", "fn", "end"))
    far_z = min(num["far"], edge)
    o.append(f'<path d="M{X(0):.1f},{Y(hy_):.1f} L{X(num["near"]):.1f},{Y(0):.1f} L{X(far_z):.1f},{Y(0):.1f} z" class="cone"/>')
    o.append(f'<line x1="{X(0):.1f}" y1="{Y(hy_):.1f}" x2="{X(D["tof_reach"]):.1f}" y2="{Y(0):.1f}" class="sig"/>')
    o.append(f'<line x1="{X(-8):.1f}" y1="{Y(0):.1f}" x2="{X(-8):.1f}" y2="{Y(hy_ + 10):.1f}" class="ink"/>')
    o.append(rect(X(-6), Y(hy_ + 5), X(1), Y(hy_ - 5), "dark", 2))
    for i, (line, cls) in enumerate(((f"on the left front post, {hy_:.0f} mm up", "fn"), (f"{D['tof_tilt']:.0f}° down; the 27° cone shaded", "fn"),
                                     (f"the ray: {num['slant']:.0f} mm, {num['ns']:.1f} ns there and back", "lab"))):
        o.append(T(20, 56 + i * 15, line, cls))
    o.append(T(X(D["tof_reach"]), Y(0) + 16, f"{D['tof_reach']:.0f}", "num", "middle"))
    o.append(T(X(num["near"]), Y(0) + 16, f"{num['near']:.0f}", "num", "middle"))
    o.append(T(X(far_z) - 4, Y(0) + 30, f"cone to {num['far']:.0f} mm", "fn", "end"))
    hx0, hy0, hw, hh = 380, 214, 230, 120
    o.append(axes(hx0, hy0, hw, hh))
    bins = 30
    for k in range(bins):
        t_ns = k * 0.08
        peak = 100 * math.exp(-((t_ns - num["ns"]) / 0.09) ** 2)
        hgt = (10 + peak) / 115 * hh
        o.append(rect(hx0 + 4 + k * (hw - 8) / bins, hy0 - hgt, hx0 + 4 + (k + 0.8) * (hw - 8) / bins, hy0, "bar2" if peak > 5 else "bar4"))
    o.append(T(hx0, hy0 + 18, "0", "num", "middle"))
    o.append(T(hx0 + 4 + num["ns"] / 0.08 * (hw - 8) / bins, hy0 + 18, f"{num['ns']:.1f} ns", "num", "middle"))
    o.append(T(hx0 + hw, hy0 + 18, "2.4 ns", "num", "end"))
    o.append(T(hx0, 54, "photons counted against arrival time:", "fn"))
    o.append(T(hx0, 68, "ambient light is the flat floor,", "fn"))
    o.append(T(hx0, 82, "the desk is the peak", "fn"))
    o.append(T(20, 258, f"Past the edge the peak moves to the floor or vanishes: the treads stop about {num['stop_mm']:.0f} mm later.", "fn"))
    return svg(640, 270, "".join(o), "Time of flight")


def fig_tof8():
    o = [T(20, 24, "What one sweep of the head sees, from above", "h")]
    cx, cy, R = 320, 252, 168
    half = FOV8 / 2

    def pt(a, r):
        return cx + r * math.sin(math.radians(a)), cy - r * math.cos(math.radians(a))

    def wedge(a0, a1, cls):
        (x0, y0), (x1, y1) = pt(a0, R), pt(a1, R)
        return f'<path d="M{cx},{cy} L{x0:.1f},{y0:.1f} A{R},{R} 0 0 1 {x1:.1f},{y1:.1f} z" class="{cls}"/>'

    for a in (-SWEEP8 / 2, SWEEP8 / 2):
        o.append(wedge(a - half, a + half, "grey"))
    o.append(wedge(-half, half, "cone"))
    for k in range(1, ZONES8):
        x1, y1 = pt(-half + k * num["zone_deg"], R)
        o.append(f'<line x1="{cx}" y1="{cy}" x2="{x1:.1f}" y2="{y1:.1f}" class="thin" stroke-opacity="0.35"/>')
    (xa, ya), (xb, yb) = pt(-num["cover"] / 2, R + 10), pt(num["cover"] / 2, R + 10)
    o.append(f'<path d="M{xa:.1f},{ya:.1f} A{R + 10},{R + 10} 0 0 1 {xb:.1f},{yb:.1f}" class="sig"/>')
    o.append(rect(cx - 34, cy - 4, cx - 22, cy + 44, "soft", 2))
    o.append(rect(cx + 22, cy - 4, cx + 34, cy + 44, "soft", 2))
    o.append(rect(cx - 9, cy - 5, cx + 9, cy + 4, "dark", 2))
    o.append(T(cx, cy - R - 18, f"{num['cover']:.0f}° in one sweep", "lab", "middle"))
    xl, yl = pt(-SWEEP8 / 2, R + 14)
    o.append(T(xl, yl, f"head turned {SWEEP8 / 2:.0f}° left", "fn", "end"))
    xr, yr = pt(SWEEP8 / 2, R + 14)
    o.append(T(xr, yr, f"{SWEEP8 / 2:.0f}° right", "fn"))
    o.append(T(20, 274, f"each window {FOV8:.0f}° square, {ZONES8} × {ZONES8} zones of {num['zone_deg']:.1f}°", "fn"))
    o.append(T(20, 290, f"a zone is {num['zone_1m']:.0f} mm wide at a metre", "fn"))
    o.append(T(20, 306, f"reach {RANGE8 / 1000:.1f} m in the dark", "fn"))
    o.append(T(620, 274, f"a frame every {num['deg_per_frame']:.0f}° at {SCAN_DPS:.0f}° a second", "fn", "end"))
    o.append(T(620, 290, "the rover drawn small;", "fn", "end"))
    o.append(T(620, 306, "distances not to scale", "fn", "end"))
    return svg(640, 316, "".join(o), "The 8x8 ranger's sweep")


def fig_display():
    o = [T(20, 24, "What the face shows while it drives, at four times size", "h")]
    px = 4
    x0, y0 = 60, 44
    o.append(rect(x0 - 10, y0 - 10, x0 + 128 * px + 10, y0 + 64 * px + 10, "dark", 8))
    o.append(T(x0 + 6, y0 + 16, "SOL 7", "onink")); o.append(T(x0 + 128 * px - 6, y0 + 16, "4.02 V 81%", "onink", "end"))
    o.append(T(x0 + 6, y0 + 22 * px, "AHEAD", "onink"))
    bx0, by0, bw, bh = x0 + 6, y0 + 26 * px, 116 * px, 10 * px      # the distance bar: a frame of pixels, filled to the reading
    o.append(rect(bx0, by0, bx0 + bw, by0 + px, "pix")); o.append(rect(bx0, by0 + bh - px, bx0 + bw, by0 + bh, "pix"))
    o.append(rect(bx0, by0, bx0 + px, by0 + bh, "pix")); o.append(rect(bx0 + bw - px, by0, bx0 + bw, by0 + bh, "pix"))
    reading, full = 12.0, 20.0
    o.append(rect(bx0 + 2 * px, by0 + 2 * px, bx0 + 2 * px + (bw - 4 * px) * reading / full, by0 + bh - 2 * px, "pix"))
    for k in range(0, 21, 5):
        tx = bx0 + 2 * px + (bw - 4 * px) * k / full
        o.append(rect(tx - px / 2, by0 + bh + px, tx + px / 2, by0 + bh + 3 * px, "pix"))
        o.append(T(tx, by0 + bh + 7 * px, f"{k}", "onink", "middle"))
    o.append(T(x0 + 128 * px - 6, y0 + 22 * px, "12 cm", "onink", "end"))
    o.append(T(x0 + 6, y0 + 64 * px - 8, "hello from the phone", "onink"))
    rx = x0 + 128 * px + 30
    for i, line in enumerate(("The bar is the ranger's", "distance ahead, redrawn", "every reading. It shrinks", "as the edge comes near;", "at the stop it reads EDGE.", "", "Black pixels cost", "nothing, so this screen", "draws a few mA.")):
        if line:
            o.append(T(rx, 66 + i * 16, line, "fn"))
    return svg(780, 336, "".join(o), "The distance bar on the display")


def fig_tip():
    o = [T(20, 24, "Where the centre of mass sits, and how far it tilts before it tips", "h")]
    s = 1.55
    oy = 236
    # side: front to the right
    cx = 160
    X = lambda v: cx + v * s           # noqa: E731
    Y = lambda v: oy - v * s           # noqa: E731
    o.append(T(40, 50, "from the side, front to the right", "lab"))
    o.append(f'<line x1="{X(-D["tr_end"] - 12):.1f}" y1="{oy}" x2="{X(D["tr_end"] + 12):.1f}" y2="{oy}" class="ink"/>')
    o.append(rect(X(-D["tr_end"]), Y(D["tr_h"]), X(D["tr_end"]), Y(0), "bar2", 8))
    for zc in (D["drive_z"], D["idler_z"]):
        o.append(f'<circle cx="{X(zc):.1f}" cy="{Y(D["axle_y"]):.1f}" r="{D["drum_ra"] * s:.1f}" class="paper"/>')
    o.append(rect(X(D["piv_z"] - D["srv_w"] / 2), Y(D["srv_top"]), X(D["piv_z"] + D["srv_w"] / 2), Y(D["srv_y0"]), "bar4", 1))
    o.append(rect(X(hz(HD["sh_z0"])), Y(hy(HD["sh_y1"])), X(hz(HD["sh_z1"])), Y(hy(HD["sh_y0"])), "dark", 3))
    gx, gy = X(D["cg"][2]), Y(D["cg"][1])
    ex = X(D["drive_z"] - 2)
    o += _cg(gx, gy, ex, oy, D["tip_back"])
    # front: the rover's right on the left
    cx2 = 480
    X2 = lambda v: cx2 - v * s         # noqa: E731
    o.append(T(330, 50, "from the front (the rover's right on the left)", "lab"))
    o.append(f'<line x1="{X2(D["pin_x1"] + 8):.1f}" y1="{oy}" x2="{X2(-D["pin_x1"] - 8):.1f}" y2="{oy}" class="ink"/>')
    for sg in (-1, 1):
        o.append(rect(X2(sg * D["tr_x0"]), Y(D["tr_h"]), X2(sg * D["tr_x1"]), Y(0), "bar2", 3))
    o.append(rect(X2(4.15), Y(D["srv_top"]), X2(-4.15), Y(D["srv_y0"]), "bar4", 1))
    o.append(rect(X2(HD["sh_x0"]), Y(hy(HD["sh_y1"])), X2(HD["sh_x1"]), Y(hy(HD["sh_y0"])), "dark", 3))
    o += _cg(X2(D["cg"][0]), Y(D["cg"][1]), X2(D["tr_x1"]), oy, D["tip_side"])
    o.append(T(20, 278, f"The centre of mass: {D['cg'][1]:.0f} mm up, {abs(D['cg'][2]):.0f} behind the middle, on the centre line. The drums and treads are {num['low_share']:.0f} % of the mass.", "fn"))
    return svg(660, 290, "".join(o), "Tipping")


def _cg(gx, gy, ex, oy, ang):
    return [f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="7" class="paper"/><path d="M{gx-7:.1f},{gy:.1f} A7,7 0 0 1 {gx:.1f},{gy-7:.1f} L{gx:.1f},{gy:.1f} z M{gx+7:.1f},{gy:.1f} A7,7 0 0 1 {gx:.1f},{gy+7:.1f} L{gx:.1f},{gy:.1f} z" class="solid"/>',
            f'<line x1="{gx:.1f}" y1="{gy:.1f}" x2="{ex:.1f}" y2="{oy}" class="ray"/>',
            f'<line x1="{gx:.1f}" y1="{gy:.1f}" x2="{gx:.1f}" y2="{oy}" class="greyl"/>',
            T(ex, oy + 18, f"pivots here: tips at {ang:.0f}°", "num", "middle")]


def fig_frame():
    o = [T(20, 24, "One side of the frame, between the two drums", "h")]
    s = 3.0
    ox, oy = 320, 150
    X = lambda z: ox + z * s                        # noqa: E731
    Y = lambda y: oy - (y - D["axle_y"]) * s        # noqa: E731
    r = D["tr_h"] / 2
    o.append(rect(X(-D["tr_end"]), Y(D["tr_h"]), X(D["tr_end"]), Y(0), "greyl", r * s))
    for zc, lab, sub in ((D["drive_z"], "drive drum", "on the motor"), (D["idler_z"], "idler drum", "on its screw")):
        o.append(f'<circle cx="{X(zc):.1f}" cy="{Y(D["axle_y"]):.1f}" r="{D["drum_ra"] * s:.1f}" class="grey"/>')
        o.append(f'<circle cx="{X(zc):.1f}" cy="{Y(D["axle_y"]):.1f}" r="3" class="solid"/>')
        o.append(T(X(zc), Y(0) + 18, lab, "fn", "middle"))
        o.append(T(X(zc), Y(0) + 32, sub, "fn", "middle"))
    o.append(poly([(X(D["r1_z"] - 1.5), Y(D["rail_y"])), (X(17), Y(D["rail_y"])), (X(D["idler_z"] - 2.4), Y(D["axle_y"] - 1.5))], "ink"))
    o.append(f'<circle cx="{X(D["idler_z"]):.1f}" cy="{Y(D["axle_y"]):.1f}" r="{D["eye_r"] * s:.1f}" class="ink"/>')
    for zr in (D["r1_z"], D["r2_z"]):
        o.append(f'<circle cx="{X(zr):.1f}" cy="{Y(D["rung_y"]):.1f}" r="3.5" class="solid"/>')
    o.append(arrow(X(D["idler_z"]), Y(D["axle_y"]) - 4, X(D["idler_z"]) - 40, Y(D["axle_y"]) - 4, "ray", "rayhead", 9))
    o.append(arrow(X(D["drive_z"]), Y(D["axle_y"]) - 4, X(D["drive_z"]) + 40, Y(D["axle_y"]) - 4, "ray", "rayhead", 9))
    o.append(T(ox, Y(D["tr_h"]) - 12, f"the sagging tread pulls the two axles together, about {num['tension']:.1f} N", "lab", "middle"))
    o.append(T(ox, Y(0) + 56, f"the rail (dark) between the rungs and the idler's eye is a strut: it buckles at {num['euler']:.0f} N, {num['euler_margin']:,.0f} times the pull", "fn", "middle"))
    return svg(640, 280, "".join(o), "The frame in compression")


def fig_lamp():
    ox, oy, w, h = 64, 236, 440, 180
    X = lambda v: ox + (v - 2.8) / 1.5 * w          # noqa: E731
    Y = lambda i: oy - i / 400 * h                  # noqa: E731
    o = [T(20, 24, "Flashlight current as the cell empties: resistor against regulator", "h"), axes(ox, oy, w, h)]
    for v in (3.0, 3.3, 3.6, 3.9, 4.2):
        o.append(f'<line x1="{X(v):.1f}" y1="{oy}" x2="{X(v):.1f}" y2="{oy+5}" class="thin"/>')
        o.append(T(X(v), oy + 18, f"{v:.1f} V", "num", "middle"))
    o.append(T(ox + w / 2, oy + 34, "the cell's voltage (full at 4.2, empty near 3.0)", "fn", "middle"))
    for i in (0, 100, 200, 300, 400):
        o.append(f'<line x1="{ox-5}" y1="{Y(i):.1f}" x2="{ox}" y2="{Y(i):.1f}" class="thin"/>')
        o.append(T(ox - 8, Y(i) + 4, f"{i}", "num", "end"))
    o.append(T(ox - 8, oy - h - 8, "mA", "fn", "end"))
    pts = [(X(v / 100), Y(i_resistor(v / 100) * 1000)) for v in range(280, 431)]
    o.append(poly(pts, "grey"))
    reg = []
    for k in range(280, 431):
        v = k / 100
        i = 350 if v >= num["v_drop"] else max(0, (v - AMC_DROP - VF0) / RS_LED * 1000)
        reg.append((X(v), Y(i)))
    o.append(poly(reg, "ink"))
    o.append(T(X(3.05), Y(350) - 8, f"regulator: 350 mA down to a {num['v_drop']:.2f} V cell", "lab"))
    o.append(T(X(3.32), Y(num["i33"]) + 18, f"resistor ({num['r_res']:.1f} Ω, set for a full cell):", "fn"))
    o.append(T(X(3.32), Y(num["i33"]) + 32, f"{num['i37']:.0f} mA at 3.7 V, {num['i33']:.0f} at 3.3", "fn"))
    o.append(f'<circle cx="{X(3.7):.1f}" cy="{Y(num["i37"]):.1f}" r="4" class="solid"/><circle cx="{X(3.3):.1f}" cy="{Y(num["i33"]):.1f}" r="4" class="solid"/>')
    return svg(640, 282, "".join(o), "Constant-current flashlight")


# ----------------------------------------------------------------------------- the text
def chapters():
    """List of (heading, [paragraphs or ('fig', svg, caption)])."""
    return [
        ("The whole rover in one breath", [
            f"Two brass treads on four aluminium drums skid it around the desk. Two 150:1 gearmotors turn them at {num['rpm37']:.0f} rpm from one {V_CELL} V cell. The head, the camera board with an 8×8 laser ranger beside it, turns on a servo standing in the frame's collar; a laser on the left front post times its own light off the desk; a regulator holds the flashlight on the right post at 350 mA. One {E['cell_mah']} mAh cell runs all of it for about {E['explore_h']:.1f} hours of exploring.",
            "Every choice on the approved sheet follows from a piece of physics. This page takes them in the order the sheet made them: how a tank turns, what the gearbox trades, how the controller drives the treads, one cell and its charge, why the drums are two thick halves, the servo, the laser, the 8×8 eye that the head sweeps, the flashlight, the beacon and the face, why it does not tip, and the frame.",
        ]),
        ("How a tank turns without steering", [
            "A tank has no steering. To turn, one tread runs forward and the other back, and both contact patches scrub sideways across the desk. That scrubbing is the whole cost of a turn.",
            f"Friction resists it. Each tread's {L_PATCH:.0f} mm run carries half the rover's {num['W']:.2f} N; sliding friction is the same everywhere on it, but its lever about the turning centre grows with the distance. Add it up and the resisting moment is μWL/4: {num['M_turn']:.1f} N·mm with brass on wood, μ about {MU}.",
            ("fig", fig_turn(), f"The rover pivoting left: the right tread drives forward, the left back, and the couple between them, {num['F_track']:.2f} N a tread across {B_GAUGE:.0f} mm, beats the friction of the scrubbing runs."),
            f"Each tread pushes {num['F_track']:.2f} N to do it, {num['tau_turn']:.1f} mN·m at its drum. The motor has {num['stall37']:.0f} mN·m at stall: a {num['margin']:.0f}-fold margin. That is why 10-gram motors turn a {D['mass']:.0f} g rover on the spot, and why the heavier wide drums cost nothing here.",
            f"Brass matters both ways. Silicone, μ about {MU_SIL:.0f}, would need {num['M_sil']:.1f} N·mm, more than three times as much, but it grips: it climbs slopes up to {num['climb_sil']:.0f}°. Brass slips on a nudge and climbs nothing steeper than {num['climb']:.0f}°, a desk toy's trade. Pivoting, the treads' outer corners sweep {num['r_pivot']:.0f} mm from the centre: give it a {2 * num['r_pivot'] / 10 + 1:.0f} cm circle of clear desk.",
        ]),
        ("What the gearbox trades", [
            f"A small DC motor spins fast and pushes weakly. Its torque falls in a straight line from stall to nothing at its free speed, and both ends scale with the voltage. At {V_CELL} V this one gives {num['rpm37']:.0f} rpm free and {num['stall37']:.0f} mN·m at stall, 62 % of its 6 V figures.",
            f"The gears multiply torque by 150 and divide speed by 150. The tread moves with its pins, on a {2 * R_PITCH:.1f} mm circle round each drum: {E['speed_free']:.0f} mm/s free and about {E['speed']:.0f} on the desk. Slow enough to drive by camera, quick enough to cross a desk in ten seconds.",
            ("fig", fig_motor(), f"The motor's line at 6 V (dashed) and at the cell's {V_CELL} V. Turning on the spot uses {num['tau_turn']/num['stall37']*100:.0f} % of the stall torque, so the motor barely slows."),
            f"Current is the other half of the choice. Current follows torque, so a stalled motor draws its stall current: {num['stall_a37']*1000:.0f} mA at {V_CELL} V for this low-power winding. Two stalled together draw {2*num['stall_a37']*1000:.0f} mA, far from the cell's 2 A cut-out. The high-power winding of the same size stalls near 1 A at this voltage; two of those plus the camera would trip the cell the first time a tread jammed.",
        ]),
        ("Four switches a tread, told over two wires", [
            "An H-bridge is four switches around the motor. Close one diagonal pair and current flows forward; close the other and it reverses; close both bottom switches and the motor brakes on itself. The motor controller holds one bridge per tread.",
            f"Speed is the share of time the bridge is on. It switches about 20 000 times a second; the winding's inductance smooths the current, so the motor sees the average: {DUTY_EX*100:.0f} % duty from a {V_EX} V cell runs it like {num['v_avg']:.1f} V steady. Twenty kilohertz is above hearing, so the motors do not whine.",
            ("fig", fig_bridge(), "Switches 1 and 4 closed, the current's path in orange. Right: the bridge's output at 60 % duty, and the average the motor responds to."),
            f"Its gate drivers work from 1.8 V, which is why this controller and not its 4.5 V twin: that one would not start on a single cell. It is also a small computer. It ramps the speed, reads the cell's voltage, and stops both bridges if the head goes quiet for {TIMEOUT_S*1000:.0f} ms. At full speed that is {num['timeout_mm']:.0f} mm of travel before a crashed head stops the treads.",
            f"It listens on I²C: two lines that any device can pull low and resistors pull high. The ranger's, the display's and the controller's pull-ups in parallel make about {R_PULL/1000:.1f} kΩ. With roughly {C_BUS*1e12:.0f} pF of wire and pins, a line rises in about {num['rise_ns']:.0f} ns, inside the 300 ns that 400 kHz allows. Two shared wires carry everything on the frame, which is why the neck is seven wires and not twenty.",
        ]),
        ("One cell for everything", [
            f"The cell holds {num['Wh']:.1f} Wh: {E['cell_mah']} mAh at 3.6 V on average, from 4.2 V full to about 3.0 V empty. Everything runs straight from it: the motors through their bridges, the head's 3.3 V regulator, the servo's boost, the flashlight's regulator.",
            f"Exploring, the controller with its camera and Wi-Fi takes {E['xiao_cam']:.0f} mA, about a third; the 8×8 ranger {E['tof8']:.0f}; the two motors {2*E['mot_run']:.0f}; the ranger, the display and the servo the rest. That is {E['explore']:.0f} mA and {E['explore_h']:.1f} hours. The flashlight at its cap adds {E['lamp']*E['lamp_cap']:.0f} mA and brings it to {E['night_h']:.1f}.",
            ("fig", fig_budget(), "The three modes as stacked bars, in milliamps from the cell."),
            f"A cell sags under load. About {R_CELL} Ω sits between its chemistry and the wires: the cell itself, its protection and the holder's springs. A 1 A burst costs {num['sag_1A']:.2f} V. The head's regulator needs about {LDO_DROP} V of headroom, so the firmware parks the rover at {num['park_v']:.1f} V rather than 3.0: there, at the camera's peak, the controller still gets about {num['rail_at_park']:.1f} V; much lower and it would brown out before the cell is empty.",
            f"The 220 µF beside the boost is a local store. The flashlight pulls 350 mA in pulses; over one 50 µs pulse the capacitor gives the charge and droops only {num['dv_cap']:.0f} mV, so the cell's wires carry the average, not the pulses. Up the neck, the 26 AWG pair, 0.13 Ω a metre and about {NECK_WIRE*100:.0f} cm long, loses {num['neck_mv']:.0f} mV at the head's {I_HEAD:.2f} A peak.",
        ]),
        ("Charging: constant current, then constant voltage", [
            f"A lithium cell charges in two steps. First a constant current, here {I_CHG*1000:.0f} mA, a little over half the cell's capacity per hour; the voltage climbs to 4.2 V in about {num['cc_h']:.1f} h. Then the charger holds 4.2 V and the current tapers as the cell fills, and it stops when the current has fallen to a small fraction. About {E['charge_h']:.1f} h in all: red light, then green.",
            ("fig", fig_charge(), "Current (solid) and the cell's voltage (dashed) through a full charge."),
            "Why the switch must be off. This charger has no power path: whatever is connected to the cell is connected to the charger. With the rover on, the controller and the ranger take about 150 mA of the 500, the current never tapers to the stopping point, and the charger holds the cell at 4.2 V for as long as the cable is in. Switch off, and the charger sees the cell alone.",
            f"Why not the controller's own charger: it gives 100 mA, which is ten hours, and only while the rover sleeps. The 500 mA board turns (5 − 3.8) V × {I_CHG} A = {num['chg_heat']:.1f} W into heat in a chip the size of a grain of rice. It throttles itself if it gets hot, and it stands in free air in front of the cell so it rarely does.",
        ]),
        ("Why the drums are two thick halves", [
            f"The reference's drums are machined aluminium, about three-quarters as wide as they are across, with narrow grooves that each hold a rod. Ours come off a laser. A fibre laser cuts by melting a line through the plate and blowing the melt out of the bottom with a jet of gas. In thick plate the slot is deep and narrow: the beam spreads past its focus and the gas loses its push, so a notch much narrower than the plate is thick fills with re-frozen metal instead of opening. Every cutting service sets a smallest hole that grows with thickness; SendCutSend's for 6061 is 0.36 mm in 1.6 mm plate and {num['hole_38']:.2f} mm in 9.53 mm.",
            f"A seat for a 1 mm rod needs {num['rod_seat']:.2f} mm, the rod plus the laser's ±0.13 mm. That cuts in plate up to {num['rod_max_t']:.2f} mm and no thicker. So the pin became a 3/32 in brass tube, {DRUM.PIN_D:.2f} mm, in a {num['seat']:.2f} mm seat: inside the limit for 3/8 in plate. One plate can't go thicker either: at 1/2 in the smallest hole is {num['hole_12']:.2f} mm and the smallest bridge {BRIDGE_12:.2f}, room for only 11 coarse seats. Two 3/8 in halves glued face to face give {D['drum_w']:.0f} mm and keep {DRUM.Z} seats.",
            ("fig", fig_drum(), f"Left: the drum's cutting outline with the planks seated round its lower half. Right: SendCutSend's smallest hole against plate thickness, and the two seats; a seat can be cut where its line sits above the curve."),
            f"A tread round {DRUM.Z} seats is a {DRUM.Z}-sided polygon, not a circle. As each pin rolls over the top of its seat the tread's speed rises and falls by 1 − cos(180°/{DRUM.Z}) = {num['chordal']:.1f} %: the chordal action every chain drive has. On the desk the seats pass at about {num['patter_hz']:.0f} a second, part of the brass's soft patter. Twenty seats would make it {num['chordal20']:.1f} %, eleven {num['chordal11']:.1f} %.",
            f"The seats' {math.degrees(DRUM.FLANK):.0f}° flanks hold the pins in. A tooth pushing a pin also lifts it by tan {math.degrees(DRUM.FLANK):.0f}° = {num['flank_share']:.0f} % of the push; the tread's weight and its neighbours hold it down. In a turn on the spot the push is only {num['F_track']:.2f} N, spread over the pins in their seats: nothing an aluminium tooth notices.",
        ]),
        ("A motor that knows where it is", [
            "A hobby servo is a small DC motor, a gear train, a potentiometer on the output shaft, and a comparator. Every 20 ms it gets a pulse; the width sets the target: 900 µs one end, 2100 the other, 1500 the middle. The comparator drives the motor until the potentiometer agrees.",
            ("fig", fig_servo(), f"The servo's loop, and the pulse widths the firmware sends: {num['deg_per_us']:.1f}° for every microsecond."),
            "The servo stands shaft up in the frame's collar, its body glued in, and the head's brass cradle is glued to its horn. When the servo drives its shaft, the head turns with it, 120° across the front of the rover.",
            f"The head is easy for it. Its {M_HEAD*1000:.1f} g, a {W_HEAD:.0f} × 15 mm block turning about its middle, swings through 60° in the rated {SERVO_S60} s on about {num['head_torque_kgcm']:.4f} kg·cm, {num['head_share']:.1f} % of the servo's stall torque. The whole 120° takes about {num['sweep_s']:.1f} s.",
            f"Why 5 V. The servo is rated 4.8 to 6 V; at 3.7 V its motor is weak and its electronics are out of their range. The boost converter stores energy in a small inductor and releases it at a higher voltage, about {ETA*100:.0f} % efficiently. The servo's 50 mA at 5 V costs about {num['boost_run']:.0f} mA from the cell; its 0.4 A stall about {num['boost_stall']:.0f}, inside the converter's 1.2 A switch.",
        ]),
        ("Timing light off the desk", [
            f"Light covers 30 cm in a nanosecond. The ranger fires invisible 940 nm laser pulses and times the photons that come back: the desk, {num['slant']:.0f} mm away along the ray, returns them in {num['ns']:.1f} ns. A millimetre of distance is {num['ps_per_mm']:.1f} picoseconds.",
            "No ordinary photodiode resolves that. The sensor uses single-photon avalanche diodes: tiny junctions biased past breakdown, where one arriving photon sets off an avalanche that can be timed. Over thousands of pulses it builds a histogram of arrival times, and the peak is the distance. Ambient light lands at random times and makes only a flat floor, which is why the reading holds in a bright room.",
            ("fig", fig_tof(), f"Left: the ray and the 27° cone from the left front post, {D['tof_y']:.0f} mm up and {D['tof_tilt']:.0f}° down, to scale. Right: the histogram the sensor builds; the peak sits at {num['ns']:.1f} ns."),
            f"Over a flat desk the reading sits near {num['slant']:.0f} mm. At an edge it jumps to the floor, a metre down, or to no target at all, and that jump is the stop. At full speed and a reading every {T_SAMPLE*1000:.0f} ms the rover moves {num['mm_per_sample']:.1f} mm between readings and about {num['stop_mm']:.0f} mm before the treads are still. The warning, {D['tof_reach']/10:.1f} cm, is {num['warn_x']:.0f} times the stop.",
            f"The cone's near edge meets the desk {num['near']:.0f} mm out, {num['near_slant']:.0f} mm away along its ray: right at the sensor's 40 mm minimum, so the full cone's nearest returns are its least sure. Narrowing the 16 × 16 receiving array to a smaller region, about {ROI:.0f}°, moves the near edge to {num['near_roi']:.0f} mm out and {num['roi_slant']:.0f} mm away, clear of it, and tightens the watch to {num['near_roi']:.0f} to {num['far_roi']:.0f} mm. The ranger is fixed to the frame and does not turn with the head, so it always watches the way the treads are going.",
        ]),
        ("An eye of 64 rangers that the head sweeps", [
            f"The ranger on the post answers one question: how far is the desk. The 8×8 ranger in the head answers sixty-four at once. It is the same physics, a 940 nm laser timed by single-photon diodes, with a lens in front of the receiving array that maps a {FOV8:.0f}° square of the room onto 8 × 8 zones. Each zone sees a {num['zone_deg']:.1f}° slice, {num['zone_1m']:.0f} mm wide at a metre. Its farthest wall, {RANGE8 / 1000:.1f} m away in the dark, returns light in {num['ns_far8']:.1f} ns. Daylight's infrared shortens that reach: the flat floor of stray photons rises until a faint return no longer stands above it.",
            f"One look covers a {FOV8:.0f}° window. The head turns {SWEEP8:.0f}°, so a sweep from one side to the other covers {num['cover']:.0f}°, everything in front of the rover. Turning at {SCAN_DPS:.0f}° a second, a sweep takes {num['sweep8_s']:.0f} s and {num['frames_sweep']:.0f} frames at {HZ8:.0f} a second, one every {num['deg_per_frame']:.0f}°: finer than a zone, so the frames overlap and nothing between them is missed. Each frame goes to the desktop with the head's angle, which puts its 64 distances in their places on a map of the room.",
            ("fig", fig_tof8(), f"From above: the head's {FOV8:.0f}° window at both ends of its turn and in the middle, the eight zones drawn in the middle one, and the {num['cover']:.0f}° they cover between them."),
            "Why it has its own two wires. Every ST ranger of this kind answers at the same I²C address, 0x29, when it powers up, and the laser ranger on the post is one of them. Two devices at one address on one bus would answer together. The usual cure holds one in reset at boot and gives the other a new address, which costs a wire down the neck; a second bus in the head costs only two of the controller's spare pins, so the neck stays at seven wires.",
            f"Why it takes 3.3 V on its VDD pin. The board's level shifters pull its I²C lines up to whatever feeds VIN. Fed from the cell, they would sit at up to 4.2 V on the controller's pins, whose absolute maximum is {V_PIN_MAX} V. Fed on VDD from the controller's own 3.3 V, the lines sit at 3.3 V and the board's regulator is bypassed. It draws about {E['tof8']:.0f} mA while it ranges, which the head's linear regulator takes straight from the cell; at worst the 3.3 V rail carries {E['rail3v3_peak']:.0f} mA, {num['rail_share']:.0f} % of its {REG_MA:.0f}.",
        ]),
        ("A light that does not fade with the cell", [
            f"An LED's current climbs steeply with its voltage, so a resistor makes the light follow the cell. A resistor sized for 350 mA from a full 4.2 V cell gives {num['i37']:.0f} mA at 3.7 V and {num['i33']:.0f} at 3.3: less than half the light by the end of a run.",
            f"The regulator is a current sink instead. It holds 350 mA through the LED whatever the cell does, as long as the cell stays {AMC_DROP} V above the LED's {num['vf350']:.2f} V. From full to nearly empty, the beam does not change.",
            ("fig", fig_lamp(), f"The same LED from a resistor (dashed) and from the regulator (solid), against the cell's voltage. The regulator only lets go below a {num['v_drop']:.2f} V cell, where the rover has already parked."),
            f"What it costs. At a full cell the regulator burns (4.2 − {num['vf350']:.2f}) V × 0.35 A = {num['p_reg42']:.2f} W; the LED turns about a third of its {num['p_led']:.2f} W into light and the rest into heat. At the 50 % cap the star carries {num['heat_cap']:.2f} W of heat and warms about {num['dT']:.0f} °C. The drone runs the same light flat out in its propellers' wind; on the post it has no wind, so the cap stays.",
            f"The 10 mm lens folds the light into a 23° spot: about {num['cd']:.0f} candela on the axis, {num['lux50']:,.0f} lux on a spot {num['spot50']:.0f} cm across at half a metre, several times a desk lamp. It points straight ahead from the right post; the camera sees by it when the head looks forward. The lamp's PWM runs at a few kilohertz, far faster than the camera exposes each row, so the picture shows no bands.",
        ]),
        ("The beacon and the face", [
            f"The eye adds up light for about a tenth of a second. A flash that long looks as bright as a steady light; a longer one looks no brighter, only longer. So the beacon's {BLINK_S*1000:.0f} ms every {PERIOD_S:.0f} s looks like its full {E['beacon']:.0f} mA and averages {num['beacon_avg']:.1f} mA. The satellite's page has the whole of Bloch's law.",
            "An OLED pixel is a tiny organic LED: it makes its own light, so a black pixel costs nothing. The rover's face is mostly black: a bar for the distance ahead, the cell, a line of text from the phone. The budget's 12 mA is a half-lit screen; this face lights about a tenth of its pixels.",
            ("fig", fig_display(), "The 128 × 64 screen while driving, at four times size: the cell along the top, the ranger's distance ahead as a bar, a message from the phone."),
        ]),
        ("Why it does not tip", [
            f"The head is only {num['head_share_mass']:.0f} % of the mass, high up; the aluminium drums and the brass treads are {num['low_share']:.0f} % of it, at axle height and below. The centre of mass comes out {D['cg'][1]:.0f} mm up, {abs(D['cg'][2]):.0f} mm behind the middle, on the centre line.",
            f"A rover tips when its centre of mass passes over the edge of what it stands on. Sideways that edge is the outside of a tread, {D['tip_side']:.0f}° of tilt away; backwards it is the rear of the contact run, {D['tip_back']:.0f}°. A desk is flat; a {BOOK:.0f} mm paperback under one tread tilts it {num['book_deg']:.0f}°.",
            ("fig", fig_tip(), "The tipping lines from the centre of mass to the edges it would pivot on."),
            f"The wide drums did this: they doubled the rover's weight but put it at the bottom, and the {B_GAUGE:.0f} mm between the treads makes it hard to roll. Braking from full speed in a tenth of a second is {num['brake_g']:.2f} g, the same as tilting {num['brake_deg']:.0f}°: nowhere near.",
        ]),
        ("The frame: rods in compression", [
            f"The brass tread does not stretch. Its last loop closes on the rover with about {SAG:.0f} mm of sag on the top run, and sag is tension: a chain weighing w per millimetre that sags δ over a span L pulls T = wL²/8δ. The tread weighs about {w_tread * 1000 / G:.2f} g a millimetre over the {L_PATCH:.0f} mm span, so it pulls the two axles together with about {num['tension']:.1f} N.",
            ("fig", fig_frame(), "One side piece between the drums: the tread's pull, and the rail that carries it."),
            f"The rail between them is a strut. A 1.5 mm stainless rod {L_RAIL*1000:.0f} mm long buckles at {num['euler']:.0f} N, {num['euler_margin']:,.0f} times the pull. Why 1.5 mm and not the 1 mm rod: stiffness goes with the fourth power of the diameter, so 1.5 mm is {num['stiff15']:.0f} times stiffer, and the idler's eye at the rail's end must not twist or the tread walks off. Why stainless: the family's frame material from the drone on, {E_ST/1e9:.0f} GPa, hard to dent, and it solders with the acid flux on the bare frame before any part goes on.",
            f"What the frame does carry is the rover's weight. The front drums take {num['front_share']*100:.0f} % of it, {num['idler_N']:.1f} N each, on M3 screws standing {num['screw_lever']:.1f} mm out from their eyes. That bends each screw to about {num['screw_MPa']:.0f} MPa, against several hundred that stainless takes.",
        ]),
    ]


NUMBERS = [
    (f"{num['M_turn']:.1f} N·mm", f"the moment that resists a turn on the spot: μWL/4 = {MU} × {num['W']:.2f} N × {L_PATCH:.0f} mm / 4"),
    (f"{num['F_track']:.2f} N", f"each tread's push to turn: the moment over {B_GAUGE:.0f} mm between the treads"),
    (f"{num['margin']:.0f}×", f"the motor's stall torque at 3.7 V ({num['stall37']:.0f} mN·m) over the turn's {num['tau_turn']:.1f} mN·m"),
    (f"{num['rpm37']:.0f} rpm", "the gearmotor's free speed at 3.7 V: 90 rpm × 3.7 / 6"),
    (f"{E['speed']:.0f} mm/s", f"on the desk: {num['rpm37']:.0f} rpm × π × {2 * R_PITCH:.1f} mm, less 15 % for load"),
    (f"{num['stall_a37']*1000:.0f} mA", "one motor stalled at 3.7 V: 0.36 A × 3.7 / 6"),
    (f"{num['rise_ns']:.0f} ns", f"an I²C line's rise: 0.85 × {R_PULL/1000:.1f} kΩ × {C_BUS*1e12:.0f} pF"),
    (f"{num['timeout_mm']:.0f} mm", f"travel before the motor controller's {TIMEOUT_S*1000:.0f} ms timeout stops the treads"),
    (f"{num['Wh']:.1f} Wh", f"the cell: {E['cell_mah']} mAh × 3.6 V"),
    (f"{num['dv_cap']:.0f} mV", "the 220 µF's droop over one 350 mA, 50 µs lamp pulse"),
    (f"{E['charge_h']:.1f} h", f"a full charge: about {num['cc_h']:.1f} h at 500 mA, then the taper"),
    (f"{num['hole_38']:.2f} mm", f"SendCutSend's smallest hole in 3/8 in 6061: why the pins are {DRUM.PIN_D:.2f} mm tubes in {num['seat']:.2f} mm seats"),
    (f"{num['chordal']:.1f} %", f"the tread's speed ripple round {DRUM.Z} seats: 1 − cos(180°/{DRUM.Z})"),
    (f"{num['ns']:.1f} ns", f"the laser's round trip to the desk, {num['slant']:.0f} mm away"),
    (f"{D['tof_reach']:.0f} mm", f"where the ranger's centre ray meets the desk: {D['tof_y']:.0f} / tan {D['tof_tilt']:.0f}°"),
    (f"{num['stop_mm']:.0f} mm", "from the edge seen to the treads still: one reading plus half the ramp"),
    (f"{num['zone_deg']:.1f}°", f"one zone of the 8×8 ranger: {FOV8:.0f}° / {ZONES8}"),
    (f"{num['cover']:.0f}°", f"what one sweep of the head sees: its {SWEEP8:.0f}° turn plus the {FOV8:.0f}° window"),
    (f"{E['rail3v3_peak']:.0f} mA", f"the 3.3 V rail at its worst, the 8×8 ranger included, of the regulator's {REG_MA:.0f}"),
    (f"{num['i33']:.0f} mA", "what a resistor would give the flashlight at a 3.3 V cell, against the regulator's 350"),
    (f"{num['dT']:.0f} °C", f"the star's rise at the 50 % cap: {num['heat_cap']:.2f} W × {STAR_KW:.0f} °C/W"),
    (f"{num['cd']:.0f} cd", f"the beam: {LM_350:.0f} lm × {LENS_EFF} into a 23° cone"),
    (f"{D['tip_side']:.0f}° / {D['tip_back']:.0f}°", f"tipping, sideways / backwards, from a centre of mass {D['cg'][1]:.0f} mm up"),
    (f"{num['tension']:.1f} N", f"the tread's pull with {SAG:.0f} mm of sag over {L_PATCH:.0f} mm: wL²/8δ"),
    (f"{num['euler']:.0f} N", f"the rail's buckling load, {L_RAIL*1000:.0f} mm of 1.5 mm 304, against the tread's {num['tension']:.1f} N"),
    (f"{num['screw_MPa']:.0f} MPa", f"an idler screw's bending stress, {num['idler_N']:.1f} N at {num['screw_lever']:.1f} mm on an M3"),
]

PARTS_IDEAS = [
    ("skid steering, μWL/4, brass's low grip", "1.0 mm brass rod", "rod10"),
    ("the laser's limit, the seat, the chordal ripple", "aluminium drum halves", "drum"),
    ("the pin in its seat", "3/32 in brass tube", "tube332"),
    ("the torque line, 150:1, the stall current", "micro metal gearmotor", "motor"),
    ("the H-bridge, PWM, the 1.8 V gate drivers, the timeout, I²C", "motor controller", "motoron"),
    ("3.4 Wh, the sag, the 3.4 V park", "Nitecore 16340 cell", "cell"),
    ("constant current then voltage, no power path", "USB-C charger", "charger"),
    ("the closed loop, the pulse widths", "sub-micro servo", "servo"),
    ("an inductor's stored energy, 85 %", "5 V boost regulator", "boost"),
    ("time of flight, SPADs, the histogram, the cone", "laser ranger", "ranger"),
    ("64 zones, the sweep, a second bus, VDD not VIN", "8×8 laser ranger", "tof8"),
    ("the current sink, the dropout, the heat", "350 mA LED regulator", "amc"),
    ("candela, lux, the spot", "cool-white LED star", "star"),
    ("Bloch's law", "pre-wired LED chip", "chip"),
    ("self-lit pixels, the distance bar", "0.96 inch display", "oled"),
    ("the camera's rows, the Wi-Fi's share of the budget", "controller with camera", "xiao"),
    ("Euler, the fourth power, sag tension", "1.5 mm stainless rod", "rod15"),
    ("the cantilevered axle", "M3 × 25 screws", "m3x25"),
]

NEXT = ("Check out the carts: the DigiKey cart (pick USPS Ground Advantage), the Amazon page and the nickel-silver wire, the drum halves at SendCutSend. "
        "Then a bench test for each idea on this page before the frame is soldered: a drum on a motor with a strip of twelve planks, "
        "run at 3.7 V with its current read; the ranger held over a desk edge at the post's height and tilt; the 8×8 ranger on the head's second bus, "
        "turned by hand across a room; the servo on its boost turning the head; the flashlight through its regulator from 4.2 down to 3.0 V. "
        "Caliper the drums, the display, the holder and the head's boards, bend the frame on a 1:1 jig, and write the firmware.")


def page_html():
    o = ['<title>Mars Rover Physics</title>',
         '<meta name="claude:viewport-fit-sides" content="cover">',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
         f"<style>{STYLE}</style>",
         '<style>.wrap{max-width:880px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} figure svg{width:100%;height:auto} td,th{min-width:0}</style>',
         '<div class="wrap">',
         '<div class="masthead"><div class="eyebrow">Mars rover &middot; step 2: the science and engineering &middot; Rev J</div>',
         '<h1>Why it turns on the spot, stops at the edge and sees the room</h1>',
         f'<div class="sub">The working behind every number on the sheet approved {APPROVED_J}: how a tank turns on brass, what the gearbox trades, four switches a tread, one cell and its charge, why the drums are two thick halves, a servo that knows where it is, light timed to the picosecond, an eye of 64 rangers that the head sweeps, a light that does not fade, a blink and a face, why it does not tip, and the frame.<br>Read after <a href="{BUILD_PAGE}" target="_blank" rel="noopener">Mars Rover Build</a>. Nothing measured yet: every figure is derived from datasheet and product-page numbers and the sheet\'s dimensions, and each assumption is a named number in the generator.</div></div>']
    for head, items in chapters():
        o.append(f"<h2>{esc(head)}</h2>")
        for it in items:
            if isinstance(it, tuple):
                _, s_, cap = it
                o.append(f"<figure>{s_}<figcaption>{esc(cap)}</figcaption></figure>")
            else:
                o.append(f"<p>{esc(it)}</p>")
    o.append("<h2>The numbers, and where they come from</h2><div class=\"tw\"><table><tr><th>Number</th><th>What it is</th></tr>")
    o += [f'<tr><td class="m">{esc(n)}</td><td>{esc(w)}</td></tr>' for n, w in NUMBERS]
    o.append("</table></div>")
    o.append("<h2>Which part each idea lives in</h2><ul>")
    o += [f'<li><strong>{esc(idea)}:</strong> the <a href="{L[key]}" target="_blank" rel="noopener">{esc(part)}</a></li>' for idea, part, key in PARTS_IDEAS]
    o.append("</ul>")
    o.append(f"<h2>What comes next</h2><p>{esc(NEXT)}</p>")
    o.append(f'<hr><p class="sub">Built by <code>docs/pages/gen/physics_page.py</code> from the dimensions, head, budget and drum in <code>build_page.py</code> (which imports <code>cad/drum.py</code>); it also writes <code>docs/PHYSICS.md</code>. Assumptions, each a number at the top of the script: μ {MU} for brass on wood and {MU_SIL} for silicone, a {L_PATCH:.0f} mm contact run, a {2*R_PITCH:.1f} mm pitch line, {R_CELL} Ω in the cell\'s path, {LDO_DROP} V of regulator headroom, {C_BUS*1e12:.0f} pF on the bus, {M_HEAD*1000:.1f} g of head turning as a {W_HEAD:.0f} × 15 mm block, the LED as {VF0} V plus {RS_LED} Ω, {LENS_EFF:.0%} through the lens, {STAR_KW:.0f} °C/W off the star, {SAG:.0f} mm of tread sag, a {SCAN_DPS:.0f}° a second scanning turn for the 8×8 ranger, 304 at {E_ST/1e9:.0f} GPa, and SendCutSend\'s 6061 laser limits read 2026-11-07. The motor, servo, boost, ranger, charger and regulator figures are their makers\' pages and datasheets. Nothing here has been measured on the rover itself.</p>')
    o.append("</div>")
    return "\n".join(o)


def physics_md():
    o = ["# Why it turns on the spot, stops at the edge and sees the room: the science and engineering behind the sheet", "",
         f"Step 2 of the house rule, rewritten for Rev J after it was approved on {APPROVED_J}. Generated by `pages/gen/physics_page.py`; the page `pages/mars-rover-physics.html` carries the figures. Edit the script, not this file.", ""]
    for head, items in chapters():
        o += [f"## {head}", ""]
        for it in items:
            if isinstance(it, tuple):
                o += [f"*Figure: {it[2]}*", ""]
            else:
                o += [it, ""]
    o += ["## The numbers, and where they come from", "", "| Number | What it is |", "| --- | --- |"]
    o += [f"| {n} | {w} |" for n, w in NUMBERS]
    o += ["", "## Which part each idea lives in", ""]
    o += [f"- {idea}: the [{part}]({L[key]})" for idea, part, key in PARTS_IDEAS]
    o += ["", "## What comes next", "", NEXT, ""]
    return "\n".join(o)


def print_pdf(html):
    PRINT.mkdir(exist_ok=True)
    css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
           ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#ececec;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#e6e6e6}"
           "html,body{background:#fff!important;color:#000!important;font-size:10pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
           "h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} p,ul,ol{max-width:none} table{font-size:9pt} th,td{padding:4pt 6pt}"
           "figure{width:72%;margin:10pt auto;padding:6pt;break-inside:avoid} figure svg{width:100%} figcaption{font-size:8.5pt} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "p.html"
        pdf = pathlib.Path(d) / "p.pdf"
        head, tail = html.rsplit("</style>", 1)
        src.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + css + tail)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "mars-rover-physics.pdf"
        out.write_bytes(pdf.read_bytes())
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [ln for ln in info.splitlines() if ln.startswith("Pages")])


def figures_png(outdir):
    """Each figure alone as a PNG, for checking by eye (not part of the outputs)."""
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    css = ("<style>html,body{margin:0;background:#fff}:root{--bg:#EDEBE7;--paper:#FFFFFF;--ink:#16181C;--ink-2:#5A6068;--line:#CFCBC4;"
           "--brass:#8F6114;--brass-soft:#F2E6D2;--signal:#0E5F7A;--signal-soft:#D9EAF1;--warn:#98351E;--warn-soft:#F7E1D9}svg{width:660px;height:auto;display:block}</style>")
    figs = [fig_turn, fig_motor, fig_bridge, fig_budget, fig_charge, fig_drum, fig_servo, fig_tof, fig_tof8, fig_lamp, fig_display, fig_tip, fig_frame]
    body = "".join(f"<div style='border-bottom:1px solid #999'>{fn()}</div>" for fn in figs)
    src = outdir / "figs.html"
    src.write_text("<!doctype html><meta charset=utf-8>" + css + body)
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--window-size=660,4300",
                    f"--screenshot={outdir / 'figs.png'}", f"file://{src}"], check=True, capture_output=True, timeout=120)


def main():
    html = page_html()
    OUT.write_text(html)
    (DOCS / "PHYSICS.md").write_text(physics_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "PHYSICS.md")
    for k in sorted(num):
        print(f"  {k} = {num[k]:.4g}")
    if "--png" in sys.argv:
        figures_png(sys.argv[sys.argv.index("--png") + 1])
    if "--pdf" in sys.argv:
        print_pdf(html)


if __name__ == "__main__":
    main()
