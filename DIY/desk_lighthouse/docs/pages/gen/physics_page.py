"""Desk lighthouse, step 2: the science and engineering behind the sheet (Rev C approved 2026-11-09; Rev D, the open lantern with no house, drawn the same evening for approval).

Writes docs/pages/desk-lighthouse-physics.html, docs/pages/print/desk-lighthouse-physics.pdf (Letter portrait, black,
9.5 pt, figures at 70 % of the text width) and docs/PHYSICS.md (the same text without the figures). Numbers come from
build_page.py's D (dimensions), MASS (masses) and E (budget), so the pages cannot drift; everything else is derived here
and shown with its working. Every assumption is a named number at the top. Edit this script, not the outputs.
`--png <dir>` renders each figure to a PNG for checking by eye; `--pdf` writes the PDF."""
from __future__ import annotations

import math
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_page import D, E, L, MASS, PAGE_TONES, REV, STYLE, esc  # noqa: E402

PAGES = HERE.parent
DOCS = PAGES.parent
OUT = PAGES / "desk-lighthouse-physics.html"
PRINT = PAGES / "print"
APPROVED = "2026-11-09"
BUILD_PAGE = "https://claude.ai/artifact/QUBvYwHYuEkKjCDbn54Lo5"

# ----------------------------------------------------------------------------- constants, each one a stated assumption
G = 9.81
GEAR = 1000.0                                   # the 30 rpm N20's gearbox: the usual 1:1000 box behind a 30 000 rpm rotor
R_WIND = E["mot_v"] / (E["mot_stall"] / 1000)   # ohm: the winding, from the stall current at 6 V
L_WIND = 1.0e-3                                 # H, a small brushed motor's winding
V_DEAD = 0.8                                    # V: below this a small brushed motor's brushes and gears do not start
T_RAMP = 0.2                                    # s, the firmware's PWM ramp
T_BRAKE = 0.03                                  # s, a shorted N20 rotor's stopping time
MX_DROP = 0.05                                  # V across the driver's high-side switch at these currents (the sheet's figure)
VF0, I0_FIL = E["fil_vf"], E["fil_rated"] / 1000   # the filament's rating point: 3.0 V at 100 mA
S_FIL = 0.05                                    # V per e-fold of current: a row of dies side by side
RS_FIL = 1.5                                    # ohm of series resistance inside the strip
LM_PER_W = 110.0                                # lumens per electrical watt for a filament LED
HEAT_FRAC = 0.65                                # the share of the lamp's power that leaves as heat
FULL_MOON = 0.25                                # lux
ROOM_LUX = 300.0                                # a lit room in the evening
H_CONV = 10.0                                   # W/m²K, still air plus radiation off a small warm thing
BOOST_START_MA = 200.0                          # the boost's start-up load limit
V_USB = 5.0
ETA_CC = 0.9                                    # a constant-current LED driver's efficiency, for the comparison
LDO_DROP = 0.1                                  # V, the SuperMini's regulator headroom at 20 mA
C3_MIN = 3.0                                    # V, the chip's specified floor
V_PROTECT = 2.8                                 # V, the cell's own cut-off
CC_SHARE = 0.8                                  # the share of a charge put in at constant current
HOURS = 6.0                                     # h, the charger's safety timer
E_BRASS = 100e9                                 # Pa
SY_BRASS = 200e6                                # Pa, a low figure for drawn brass rod
ALPHA_BRASS, ALPHA_ACRYLIC = 19e-6, 70e-6       # per K
BR_N52 = 1.45                                   # T, the magnet's remanence
B_OPERATE = 3.0e-3                              # T along the reed that closes a reed of this sensitivity
PULLUP = 45e3                                   # ohm, the C3's internal pull-up
SOC = {3.0: 0, 3.2: 1, 3.4: 5, 3.6: 15, 3.8: 50, 4.0: 80, 4.2: 100}   # about how much of a Li-ion cell is left at each voltage

num = {}

# ----------------------------------------------------------------------------- the beacon's character
num["omega"] = 360.0 / E["period"]                        # deg/s
num["omega_rad"] = math.radians(num["omega"])
num["dark_s"] = E["period"] - E["pass_s"]
num["edge_speed_2m"] = num["omega_rad"] * 2.0              # m/s, the pool's edge across a wall 2 m away
num["rotor_rpm"] = E["rpm_target"] * GEAR
num["rotor_hz"] = num["rotor_rpm"] / 60

# ----------------------------------------------------------------------------- the motor
num["i_stall_5v"] = E["v_rail"] / R_WIND * 1000
num["d_dead"] = V_DEAD / E["v_rail"]
num["d_real"] = (V_DEAD + E["rpm_target"] * (E["v_rail"] - V_DEAD) / E["rpm_5v"]) / E["v_rail"]   # duty for 8 rpm with the dead band
num["i_start_real"] = E["v_rail"] * num["d_real"] / R_WIND * 1000     # mA, the stalled rotor at that duty, before it spins up
num["step_no_ramp"] = num["i_start_real"] + E["i_lamp_max"]
num["tau_e_us"] = L_WIND / R_WIND * 1e6
num["pwm_period_us"] = 1e6 / 20e3
num["brake_deg"] = num["omega"] * T_BRAKE


def rpm_of(d):
    """Output rpm at duty d on the 5 V rail, with the dead band."""
    return max(0.0, E["rpm_5v"] * (E["v_rail"] * d - V_DEAD) / (E["v_rail"] - V_DEAD))


# ----------------------------------------------------------------------------- the filament as a diode behind a resistor
def v_fil(i):
    """Volts across the filament at i amps: the rating point, a diode slope and a little series resistance."""
    return VF0 + S_FIL * math.log(i / I0_FIL) + RS_FIL * (i - I0_FIL)


def crossing(v_src, r):
    """Where the filament's curve meets the line (v_src − V) / r: returns (V, I in amps)."""
    lo, hi = 1e-4, v_src / r
    for _ in range(80):
        i = (lo + hi) / 2
        if v_fil(i) + i * r < v_src:
            lo = i
        else:
            hi = i
    i = (lo + hi) / 2
    return v_fil(i), i


num["v_rail_eff"] = E["v_rail"] - MX_DROP
num["v_lamp"], _i_full = crossing(num["v_rail_eff"], E["r_lamp"])
num["i_full"] = _i_full * 1000
num["i_day"] = num["i_full"] * E["lamp_duty"]
num["r_raw"] = (E["v_cell"] - MX_DROP - num["v_lamp"]) / _i_full       # the resistor for the same current straight from a 3.7 V cell
num["raw"] = {v: crossing(v - MX_DROP, num["r_raw"])[1] * 1000 for v in (E["v_cell_low"], E["v_cell"], E["v_cell_full"])}
num["rail_pm5"] = [crossing(num["v_rail_eff"] * k, E["r_lamp"])[1] * 1000 for k in (0.95, 1.05)]
num["p_lamp"] = num["v_lamp"] * _i_full                                 # W at full
num["p_res"] = _i_full ** 2 * E["r_lamp"]                               # W in both resistors at full
num["p_from_cell"] = E["v_rail"] * _i_full / E["boost_eff"]            # W the cell pays for the lamp at full
num["lamp_eff"] = num["p_lamp"] / num["p_from_cell"]
num["lm_full"] = num["p_lamp"] * LM_PER_W
num["lm_day"] = num["lm_full"] * E["lamp_duty"]
num["cd_full"] = num["lm_full"] / math.pi ** 2                          # a vertical strip radiates sideways with Φ = π² I
num["cd_day"] = num["lm_day"] / math.pi ** 2
num["lux"] = {d: num["cd_day"] / d ** 2 for d in (0.5, 1.0, 2.0, 3.0)}
num["lux_full"] = {d: num["cd_full"] / d ** 2 for d in (0.5, 1.0, 2.0, 3.0)}
num["moons_2m"] = num["lux"][2.0] / FULL_MOON
num["pulses_per_deg"] = 5000 / num["omega"]

# ----------------------------------------------------------------------------- heat
num["lantern_m2"] = (math.pi * D["drum_od"] * D["drum_h"] + 2 * math.pi * (D["drum_od"] / 2) ** 2) / 1e6     # the brass drum round the lamp, open at both ends, in free air
num["lantern_dT"] = num["p_lamp"] * HEAT_FRAC / (H_CONV * num["lantern_m2"])
num["lantern_dT_day"] = num["lantern_dT"] * E["lamp_duty"]
num["coaster_m2"] = (2 * math.pi * (D["disc_d"] / 2) ** 2 + math.pi * D["disc_d"] * D["disc_t"]) / 1e6
num["chg_heat"] = (V_USB - E["v_cell"]) * E["chg_ma"] / 1000
num["coaster_dT"] = num["chg_heat"] / (H_CONV * num["coaster_m2"])
num["res_dT"] = num["p_res"] / (H_CONV * num["coaster_m2"])


# ----------------------------------------------------------------------------- the budget from the cell, by part
def via_boost(ma):
    """mA from the cell for ma on the 5 V rail."""
    return ma * E["v_rail"] / E["boost_eff"] / E["v_cell"]


num["ma_per_ma"] = via_boost(1.0)
num["cell_parts"] = [("the lamp", via_boost(E["i_lamp"])), ("the motor", via_boost(E["mot_avg"])), ("the driver", via_boost(E["mx_q"])),
                     ("the controller, awake", E["c3_avg"]), ("the boost's keep", E["boost_q"])]
num["lamp_share"] = via_boost(E["i_lamp"]) / E["cell_typ"]
num["c3_share_idle"] = E["c3_avg"] / E["cell_idle"]
num["usb_a_running"] = (E["chg_ma"] + E["rail_typ"] * E["v_rail"] / 0.9 / V_USB) / 1000   # A from the adapter while it charges and runs
_p_day = num["p_lamp"] * E["lamp_duty"]
num["cc_saving_ma"] = via_boost(E["i_lamp"]) - _p_day / (ETA_CC * E["v_cell"]) * 1000       # what a constant-current driver from the cell would save
num["h_beacon_cc"] = E["cell_mah"] * 0.9 / (E["cell_typ"] - num["cc_saving_ma"])

# ----------------------------------------------------------------------------- the cell and the rail
num["cell_rail"] = 3.3 + LDO_DROP + E["diode_v"]
num["rail_at_low"] = E["v_cell_low"] - LDO_DROP - E["diode_v"]
num["cell_floor"] = C3_MIN + LDO_DROP + E["diode_v"]
num["cc_h"] = CC_SHARE * E["cell_mah"] / E["chg_ma"]
num["cv_h"] = E["h_charge"] - num["cc_h"]
num["timer_x"] = HOURS / E["h_charge"]
num["c_rate"] = E["chg_ma"] / E["cell_mah"]
num["div_years"] = E["cell_mah"] / (E["i_div_ua"] / 1000) / 24 / 365

# ----------------------------------------------------------------------------- the cage
I_ROD = math.pi * (D["rod_d"] / 1000) ** 4 / 64        # m⁴
A_ROD = math.pi * (D["rod_d"] / 2000) ** 2             # m²
L_LEG = D["leg_h"] / 1000
THETA = math.atan(D["leg_slope"])
num["k_bend"] = 4 * 12 * E_BRASS * I_ROD / L_LEG ** 3 / 1000                      # N/mm: four vertical rods fixed at both ends
num["k_axial"] = 2 * E_BRASS * A_ROD / L_LEG * math.sin(THETA) ** 2 / 1000        # N/mm: the lean; two rods stretch, two shorten
num["k_cage"] = num["k_bend"] + num["k_axial"]
num["lean_x"] = num["k_cage"] / num["k_bend"]
num["axial_per_n"] = 1 / (2 * math.sin(THETA))                                     # N along each of two rods for 1 N sideways
_rod_g = next(m for n, m, _ in MASS if n.startswith("four rods")) / 4
_m_top = (D["lantern_g"] + 2 * _rod_g) / 1000                                       # kg: the lantern and about two rods' worth of the cage
num["f_vertical"] = math.sqrt(num["k_bend"] * 1000 / _m_top) / (2 * math.pi)
num["f_cage"] = math.sqrt(num["k_cage"] * 1000 / _m_top) / (2 * math.pi)
num["euler"] = D["rod_euler_n"]
num["rod_load"] = D["rod_load_n"]
num["euler_x"] = num["euler"] / num["rod_load"]
num["lantern_n"] = D["lantern_g"] / 1000 * G
num["rod_mohm"] = E["rod_mohm"]
num["rod_mv"] = num["rod_mohm"] * _i_full
_I1 = math.pi * (1.0e-3) ** 4 / 64                                                  # m⁴, a 1 mm rod
num["drum_g"] = next(m for n, m, _ in MASS if n.startswith("shutter"))
num["bar_defl_um"] = (num["drum_g"] / 1000 * G / 2) * ((D["drum_od"] / 2) / 1000) ** 3 / (3 * E_BRASS * _I1) * 1e6   # µm: half the drum on one 1 mm bar as a cantilever to the wall
num["cell_tray_g"] = next(m for n, m, _ in MASS if n.startswith("cell"))

# ----------------------------------------------------------------------------- the fuse
num["W_N"] = D["mass"] / 1000 * G
num["f_tip"] = D["push_n"]
num["f_tip_b"] = D["push_n_b"]
_x_rod = D["leg_r0"] * math.cos(math.radians(45)) / 1000          # m, a rod's lever arm about the tipping axis
_h_push = (D["height"] - D["disc_t"]) / 1000
num["rod_axial_at_tip"] = num["f_tip"] * _h_push / (4 * _x_rod)    # N in a rod when the push at the ball is the tipping push
_M_y = SY_BRASS * I_ROD / (D["rod_d"] / 2000)                      # N·m, the moment that yields a rod
num["f_set_mid"] = 8 * _M_y / L_LEG                                # N sideways at a rod's middle alone, fixed-fixed
num["f_set_tip"] = _M_y / (D["leg_top"] / 1000)                    # N sideways at a glazing bar's free tip
num["delta_tip"] = num["f_tip"] / num["k_cage"]                    # mm the deck moves under the tipping push

# ----------------------------------------------------------------------------- the reed
R_MAG, T_MAG = D["mag_d"] / 2000, D["mag_t"] / 1000


def b_axis(z):
    """T on a disc magnet's axis, z metres from its face."""
    return BR_N52 / 2 * ((z + T_MAG) / math.hypot(R_MAG, z + T_MAG) - z / math.hypot(R_MAG, z))


M_DIP = BR_N52 * math.pi * R_MAG ** 2 * T_MAG / (4e-7 * math.pi)    # A·m²


def b_z(x, z):
    """T, the vertical field a dipole makes x sideways and z below its centre (the dipole picture, good past a magnet's width)."""
    r = math.hypot(x, z)
    return 1e-7 * M_DIP * (3 * z ** 2 / r ** 5 - 1 / r ** 3)


Z_C = (D["reed_gap"] + D["mag_t"] / 2) / 1000                          # the reed's tip to the magnet's centre
num["b_face"] = [b_axis(z / 1000) * 1000 for z in (2, 4, 6, 10)]      # mT at 2, 4, 6 and 10 mm under the face
num["b_tip"] = b_axis(D["reed_gap"] / 1000) * 1000
_lo, _hi = 0.0, 0.02
for _ in range(60):
    _mid = (_lo + _hi) / 2
    if b_z(_mid, Z_C) > B_OPERATE:
        _lo = _mid
    else:
        _hi = _mid
num["x_operate"] = _lo * 1000                                           # mm sideways where the field falls to the operate level
num["x_zero"] = Z_C * math.sqrt(2) * 1000                               # mm, where the dipole's vertical field reverses
num["v_mag"] = num["omega_rad"] * D["mag_r"]                            # mm/s
num["pulse_s"] = 2 * num["x_operate"] / num["v_mag"]
num["pulse_deg"] = num["pulse_s"] * num["omega"]
num["pullup_ua"] = 3.3 / PULLUP * 1e6 * num["pulse_s"] / E["period"]   # µA averaged over a turn

# ----------------------------------------------------------------------------- the spine
num["bearing_clear"] = (D["bush_hole"] - D["tube_od"]) / 2
num["span"] = D["z_deck1"] - D["z_tube0"]                                # mm between the motor's bearing and the deck's
num["wobble"] = num["bearing_clear"] * (1 + D["drum_top"] / num["span"])
num["rod_clear"] = D["ast_r"] - D["rod_d"] / 2 - D["drum_od"] / 2                  # mm from the drum to the nearest rod


def f(x, d=0):
    return f"{x:.{d}f}"


# ----------------------------------------------------------------------------- figure helpers (the satellite's)
def T(x, y, s, cls="fn", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


FIG_CSS = ("<style>"
           ".ink{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
           ".thick{fill:none;stroke:var(--ink);stroke-width:5;stroke-linecap:butt}"
           ".thin{fill:none;stroke:var(--ink);stroke-width:1.1;stroke-linecap:round}"
           ".grey{fill:none;stroke:var(--ink-2);stroke-width:1.1;stroke-dasharray:4 3}"
           ".greys{fill:none;stroke:var(--ink-2);stroke-width:1.1}"
           ".ray{fill:none;stroke:var(--warn);stroke-width:1.6}"
           ".rayhead{fill:var(--warn);stroke:none}"
           ".fan{fill:var(--warn-soft);stroke:var(--warn);stroke-width:1;stroke-dasharray:3 3}"
           ".glass{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.6}"
           ".diag{fill:none;stroke:var(--signal);stroke-width:1.4;stroke-dasharray:6 4}"
           ".solid{fill:var(--ink);stroke:none}"
           ".hollow{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
           ".soft{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.2}"
           ".band{fill:var(--brass-soft);stroke:none}"
           ".bar{fill:var(--ink);stroke:none}"
           ".bar2{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1}"
           ".bar3{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1}"
           ".bar4{fill:var(--paper);stroke:var(--ink);stroke-width:1}"
           ".h{font:700 13px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".lab{font:700 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".num{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink)}"
           "</style>")


def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{FIG_CSS}{body}</svg>'


def arrow(x0, y0, x1, y1, cls="ray", head="rayhead", size=9):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - size * math.cos(ang), y1 - size * math.sin(ang)
    px, py = size / 2 * math.sin(ang), -size / 2 * math.cos(ang)
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="{cls}"/>'
            f'<path d="M{x1:.1f},{y1:.1f} L{hx+px:.1f},{hy+py:.1f} L{hx-px:.1f},{hy-py:.1f} z" class="{head}"/>')


def axes(ox, oy, w, h):
    return f'<line x1="{ox}" y1="{oy}" x2="{ox+w}" y2="{oy}" class="ink"/><line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-h}" class="ink"/>'


def poly(pts, cls, close=False):
    return '<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" class="{cls}"' + (' fill-rule="evenodd"' if close else "") + "/>"


def polygon(pts, cls):
    return '<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" class="{cls}"/>'


def rect(x0, y0, x1, y1, cls, rx=0):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" rx="{rx}" class="{cls}"/>'


def circ(x, y, r, cls):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="{cls}"/>'


def line(x0, y0, x1, y1, cls="thin"):
    return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="{cls}"/>'


def pt(cx, cy, r, a):
    """A point r from (cx, cy) at a degrees, measured anticlockwise from the right as on paper."""
    return cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))


def arc(cx, cy, r, a0, a1, cls):
    """An arc from a0 to a1 degrees, anticlockwise on the page."""
    (x0, y0), (x1, y1) = pt(cx, cy, r, a0), pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f'<path d="M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} 0 {x1:.1f},{y1:.1f}" class="{cls}"/>'


def sector(cx, cy, r, a0, a1, cls):
    (x0, y0), (x1, y1) = pt(cx, cy, r, a0), pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f'<path d="M{cx:.1f},{cy:.1f} L{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} 0 {x1:.1f},{y1:.1f} z" class="{cls}"/>'


# ----------------------------------------------------------------------------- the figures
def fig_character():
    cx, cy = 175, 160
    rg, rd, rf = 78, 50, 110
    half = D["win_deg"] / 2
    o = [T(20, 24, "A fixed lamp inside a turning window", "h"), T(380, 24, "What the room sees: the light's character", "h")]
    o.append(sector(cx, cy, rf, -half, half, "fan"))
    o.append(circ(cx, cy, rg, "thin"))
    o.append(arc(cx, cy, rd, half, 360 - half, "thick"))
    o.append(circ(cx, cy, 5, "solid"))
    o.append(T(cx, cy + 20, "the lamp", "lab", "middle"))
    o.append(T(cx, cy + 33, "stands still", "fn", "middle"))
    o.append(T(cx - 40, cy + rg + 18, f"brass, {360 - D['win_deg']:.0f}° of the drum", "fn", "middle"))
    o.append(T(cx - 30, cy - rg - 8, "the four rods", "fn", "middle"))
    o.append(T(cx + rg + 16, cy - 8, f"the window, {D['win_deg']:.0f}°:", "fn"))
    o.append(T(cx + rg + 16, cy + 6, "light leaves here", "fn"))
    rm = (rg + rd) / 2
    o.append(arc(cx, cy, rm, 200, 245, "ray"))
    xa, ya = pt(cx, cy, rm, 245)
    xb, yb = pt(cx, cy, rm, 241)
    o.append(arrow(xb, yb, xa, ya))
    o.append(T(cx - rg - 8, cy + 22, f"{E['rpm_target']:.0f} rpm", "num", "end"))
    o.append(T(cx - rg - 8, cy + 36, f"{E['period']:.1f} s a turn", "fn", "end"))
    ox, oy, w = 380, 170, 260
    X = lambda t: ox + t / 15.0 * w                                   # noqa: E731
    o.append(line(ox, oy, ox + w, oy, "ink"))
    for t in (0, 5, 10, 15):
        o.append(line(X(t), oy, X(t), oy + 5))
        o.append(T(X(t), oy + 18, f"{t} s", "num", "middle"))
    hi, lo = oy - 56, oy - 10
    trace = [(X(0), hi)]
    for t0 in (0.0, E["period"]):
        trace += [(X(t0), hi), (X(t0 + E["pass_s"]), hi), (X(t0 + E["pass_s"]), lo), (X(t0 + E["period"]), lo), (X(t0 + E["period"]), hi)]
    trace = trace[:-1] + [(X(15), lo)]
    o.append(poly(trace, "ink"))
    o.append(T(X(E["pass_s"] / 2), hi - 8, f"{E['pass_s']:.1f} s light", "lab", "middle"))
    o.append(T(X(E["pass_s"] + num["dark_s"] / 2), lo - 6, f"{num['dark_s']:.0f} s brass", "fn", "middle"))
    o.append(T(ox, 60, f"Fl W {E['period']:.1f}s", "num"))
    o.append(T(ox + 92, 60, "on a chart", "fn"))
    o.append(T(ox, 80, "flash shorter than dark: flashing", "fn"))
    o.append(T(ox, 94, "equal: isophase; longer: occulting", "fn"))
    o.append(T(20, 290, "A lighthouse burns a fixed lamp inside a turning lens; here the lens is a brass drum with a window.", "fn"))
    o.append(T(20, 304, f"{num['omega']:.0f}° a second: on a wall 2 m away the edge of the light walks at {num['edge_speed_2m']:.1f} m/s.", "fn"))
    return svg(660, 316, "".join(o), "The light's character")


def fig_light():
    ox, oy, w, h = 64, 212, 330, 160
    X = lambda d: ox + (d - 0.5) / 3.5 * w                                      # noqa: E731
    Y = lambda lux: oy - (math.log10(max(lux, 0.1)) + 1) / (math.log10(20) + 1) * h   # noqa: E731
    o = [T(20, 24, "Light on a wall against distance, the window facing it", "h"), axes(ox, oy, w, h)]
    for d in (0.5, 1, 2, 3, 4):
        o.append(line(X(d), oy, X(d), oy + 5))
        o.append(T(X(d), oy + 18, f"{d:g} m", "num", "middle"))
    for lux in (0.1, 1, 10):
        o.append(line(ox - 5, Y(lux), ox, Y(lux)))
        o.append(T(ox - 8, Y(lux) + 4, f"{lux:g}", "num", "end"))
    o.append(T(ox - 8, oy - h - 6, "lux", "fn", "end"))
    for cd, cls in ((num["cd_full"], "grey"), (num["cd_day"], "ink")):
        pts = [(X(d / 100), Y(cd / (d / 100) ** 2)) for d in range(50, 401, 5)]
        o.append(poly(pts, cls))
    for d in (1.0, 2.0, 3.0):
        o.append(circ(X(d), Y(num["lux"][d]), 4, "solid"))
        o.append(T(X(d) - 7, Y(num["lux"][d]) + 14, f"{num['lux'][d]:.2g} lux", "lab", "end"))
    o.append(line(ox, Y(FULL_MOON), ox + w, Y(FULL_MOON), "grey"))
    o.append(T(ox + 6, Y(FULL_MOON) - 5, "full moon", "fn"))
    o.append(T(X(2.3), oy - h + 14, f"dashed: the lamp at full, {num['cd_full']:.1f} cd", "fn"))
    o.append(T(X(2.3), oy - h + 28, f"solid: everyday, {num['cd_day']:.1f} cd", "fn"))
    rx = 420
    rows = ((f"{num['p_lamp']*1000:.0f} mW in the filament at full", "lab"), (f"× {LM_PER_W:.0f} lm/W = {num['lm_full']:.0f} lumens;", "fn"),
            (f"{num['lm_day']:.0f} at the everyday {E['lamp_duty']*100:.0f} %. A candle is 13.", "fn"), ("", "fn"),
            ("a vertical strip radiates sideways", "lab"), ("with Φ / π² candela, and candela", "fn"), ("over metres squared is the lux", "fn"), ("on the wall.", "fn"), ("", "fn"),
            (f"at 2 m: {num['moons_2m']:.0f} full moons", "lab"), ("a pool you can watch cross a dark", "fn"), (f"room; a glint in a {ROOM_LUX:.0f} lux lit one.", "fn"), ("", "fn"),
            ("no glass: nothing between the lamp", "lab"), ("and the room. A lighthouse's trick, the", "fn"), ("Fresnel lens that folds the light into", "fn"), ("one beam, is the one part left out.", "fn"))
    for i, (txt, cls) in enumerate(rows):
        if txt:
            o.append(T(rx, 50 + i * 13.5, txt, cls))
    return svg(660, 292, "".join(o), "Light on the wall")


def fig_loadline():
    ox, oy, w, h = 64, 236, 360, 186
    V0, V1, I1 = 2.6, 3.3, 160.0
    X = lambda v: ox + (v - V0) / (V1 - V0) * w                          # noqa: E731
    Y = lambda i: oy - i / I1 * h                                        # noqa: E731
    o = [T(20, 24, "The filament's curve against two kinds of resistor line", "h"), axes(ox, oy, w, h)]
    for v in (2.6, 2.8, 3.0, 3.2):
        o.append(line(X(v), oy, X(v), oy + 5))
        o.append(T(X(v), oy + 18, f"{v:.1f} V", "num", "middle"))
    for i in (40, 80, 120, 160):
        o.append(line(ox - 5, Y(i), ox, Y(i)))
        o.append(T(ox - 8, Y(i) + 4, f"{i}", "num", "end"))
    o.append(T(ox - 8, oy - h - 6, "mA", "fn", "end"))
    o.append(line(ox, Y(E["fil_rated"]), ox + w, Y(E["fil_rated"]), "grey"))
    o.append(T(ox + 4, Y(E["fil_rated"]) - 4, f"{E['fil_rated']:.0f} mA", "fn"))
    pts = []
    i = 0.004
    while i <= I1 / 1000:
        v = v_fil(i)
        if V0 <= v <= V1:
            pts.append((X(v), Y(i * 1000)))
        i += 0.001
    o.append(poly(pts, "ink"))

    def load_line(v_src, r, cls):
        va, ia = V0, (v_src - V0) / r * 1000
        vb, ib = V1, (v_src - V1) / r * 1000
        if ia > I1:
            va, ia = v_src - I1 * r / 1000, I1
        if ib < 0:
            vb, ib = v_src, 0.0
        return line(X(va), Y(ia), X(vb), Y(ib), cls)

    o.append(load_line(num["v_rail_eff"], E["r_lamp"], "thin"))
    v_c, i_c = num["v_lamp"], num["i_full"]
    o.append(circ(X(v_c), Y(i_c), 4.5, "solid"))
    for vc in (E["v_cell_full"], E["v_cell"], E["v_cell_low"]):
        o.append(load_line(vc - MX_DROP, num["r_raw"], "grey"))
        vv, ii = crossing(vc - MX_DROP, num["r_raw"])
        o.append(circ(X(vv), Y(ii * 1000), 4, "hollow"))
    vv, ii = crossing(E["v_cell_full"] - MX_DROP, num["r_raw"])
    o.append(T(X(vv) - 9, Y(ii * 1000) + 4, f"a full cell: {ii * 1000:.0f} mA", "fn", "end"))
    vv, ii = crossing(E["v_cell_low"] - MX_DROP, num["r_raw"])
    o.append(T(X(vv) - 9, Y(ii * 1000) + 16, f"an empty one: {ii * 1000:.0f} mA", "fn", "end"))
    o.append(T(ox, oy + 36, f"solid dot: {i_c:.0f} mA on the 5 V rail. Dashed: the same lamp straight from the cell through {num['r_raw']:.0f} Ω at {E['v_cell_full']:.1f}, {E['v_cell']:.1f} and {E['v_cell_low']:.1f} V", "fn"))
    rx = 448
    rows = (("the curve is the filament:", "lab"), (f"{VF0:.1f} V at {E['fil_rated']:.0f} mA, e-fold every", "fn"), (f"{S_FIL*1000:.0f} mV, {RS_FIL:.1f} Ω inside the strip.", "fn"), ("", "fn"),
            ("the lines are resistors:", "lab"), ("current where they cross.", "fn"), ("", "fn"),
            ("a 2 V drop makes a flat line:", "lab"), (f"{i_c:.0f} mA at the solid dot; a rail 5 % off", "fn"), (f"gives {num['rail_pm5'][0]:.0f} or {num['rail_pm5'][1]:.0f}. The lamp hardly notices.", "fn"), ("", "fn"),
            ("a 0.6 V drop makes a steep one:", "lab"), (f"{num['raw'][E['v_cell_full']]:.0f} mA full, {num['raw'][E['v_cell_low']]:.0f} empty. That is", "fn"), ("why the rail is a regulated 5 V.", "fn"))
    for i_, (txt, cls) in enumerate(rows):
        if txt:
            o.append(T(rx, 50 + i_ * 13.5, txt, cls))
    return svg(660, 290, "".join(o), "Two load lines")


def fig_motor():
    o = [T(20, 24, "Speed against duty on the 5 V rail", "h"), T(350, 24, "The first second on the rail", "h")]
    ox, oy, w, h = 60, 206, 250, 150
    X = lambda d: ox + d * w                                             # noqa: E731
    Y = lambda rpm: oy - rpm / 30.0 * h                                  # noqa: E731
    o.append(axes(ox, oy, w, h))
    for d in (0, 0.25, 0.5, 0.75, 1.0):
        o.append(line(X(d), oy, X(d), oy + 5))
        o.append(T(X(d), oy + 18, f"{d*100:.0f} %", "num", "middle"))
    for rpm in (10, 20, 30):
        o.append(line(ox - 5, Y(rpm), ox, Y(rpm)))
        o.append(T(ox - 8, Y(rpm) + 4, f"{rpm}", "num", "end"))
    o.append(T(ox - 8, oy - h - 6, "rpm", "fn", "end"))
    o.append(line(X(0), Y(0), X(1), Y(E["rpm_5v"]), "grey"))
    o.append(poly([(X(0), Y(0)), (X(num["d_dead"]), Y(0)), (X(1), Y(E["rpm_5v"]))], "ink"))
    o.append(line(X(0), Y(E["rpm_target"]), X(num["d_real"]), Y(E["rpm_target"]), "grey"))
    o.append(circ(X(E["duty_mot"]), Y(E["rpm_target"]), 4, "hollow"))
    o.append(circ(X(num["d_real"]), Y(E["rpm_target"]), 4.5, "solid"))
    o.append(T(X(num["d_real"]) + 8, Y(E["rpm_target"]) + 4, f"{E['rpm_target']:.0f} rpm at {num['d_real']*100:.0f} %", "lab"))
    o.append(T(X(1) + 4, Y(E["rpm_5v"]) + 4, f"{E['rpm_5v']:.0f}", "num"))
    o.append(T(X(num["d_dead"]) + 2, oy - 8, f"dead band {V_DEAD:.1f} V", "fn"))
    o.append(T(ox, oy + 40, f"grey: speed from voltage alone, the sheet's {E['duty_mot']*100:.0f} % (hollow)", "fn"))
    o.append(T(ox, oy + 54, f"black: with the brushes' dead band, {num['d_real']*100:.0f} %", "fn"))
    o.append(T(ox, oy + 68, "the reed loop finds the duty either way", "fn"))
    ox2, oy2, w2, h2 = 390, 206, 240, 150
    X2 = lambda t: ox2 + t / 1.0 * w2                                    # noqa: E731
    Y2 = lambda ma: oy2 - ma / 250.0 * h2                                # noqa: E731
    o.append(axes(ox2, oy2, w2, h2))
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        o.append(line(X2(t), oy2, X2(t), oy2 + 5))
        o.append(T(X2(t), oy2 + 18, f"{t:g} s", "num", "middle"))
    for ma in (50, 100, 150, 200, 250):
        o.append(line(ox2 - 5, Y2(ma), ox2, Y2(ma)))
        o.append(T(ox2 - 8, Y2(ma) + 4, f"{ma}", "num", "end"))
    o.append(T(ox2 - 8, oy2 - h2 - 6, "mA", "fn", "end"))
    o.append(line(ox2, Y2(BOOST_START_MA), ox2 + w2, Y2(BOOST_START_MA), "grey"))
    o.append(T(ox2 + w2 - 4, Y2(BOOST_START_MA) - 5, f"the boost's start-up limit, {BOOST_START_MA:.0f} mA", "fn", "end"))
    q = E["mx_q"]
    t0, t1, t2, t3 = 0.05, 0.05 + T_RAMP, 0.4, 0.7
    hump = 1.5 * E["mot_ma"]
    top = q + E["mot_ma"] + E["i_lamp"]
    ramp = [(X2(0), Y2(q)), (X2(t0), Y2(q)), (X2(t0 + T_RAMP * 0.6), Y2(q + hump)), (X2(t1), Y2(q + E["mot_ma"] * 1.1)), (X2(t1 + 0.1), Y2(q + E["mot_ma"])),
            (X2(t2), Y2(q + E["mot_ma"])), (X2(t3), Y2(top)), (X2(1.0), Y2(top))]
    o.append(poly(ramp, "ink"))
    step = [(X2(0), Y2(q)), (X2(t0), Y2(q)), (X2(t0), Y2(num["step_no_ramp"])), (X2(t0 + 0.05), Y2(num["step_no_ramp"])), (X2(t0 + 0.05), Y2(q + E["mot_ma"] + E["i_lamp_max"])),
            (X2(1.0), Y2(q + E["mot_ma"] + E["i_lamp_max"]))]
    o.append(poly(step, "grey"))
    o.append(T(X2(t0 + 0.06), Y2(num["step_no_ramp"]) - 6, f"both at once, no ramp: {num['step_no_ramp']:.0f} mA", "fn"))
    o.append(T(X2(0.12), Y2(q + hump) - 10, f"motor ramps {T_RAMP:.1f} s", "fn"))
    o.append(T(X2(1.0), Y2(top) + 14, f"{E['rail_typ']:.0f} mA running", "lab", "end"))
    o.append(T(X2(1.0), Y2(top) + 28, "after the lamp fades up", "fn", "end"))
    o.append(T(ox2, oy2 + 40, "a boost starting into a heavy load never", "fn"))
    o.append(T(ox2, oy2 + 54, "reaches 5 V: rail up with nothing on it,", "fn"))
    o.append(T(ox2, oy2 + 68, "then the motor, then the lamp", "fn"))
    return svg(660, 292, "".join(o), "The motor on the rail")


def fig_budget():
    o = [T(20, 24, "What the cell pays, mode by mode, and for how long", "h")]
    ox, w = 150, 330
    X = lambda ma: ox + ma / 150.0 * w                                   # noqa: E731
    modes = [("beacon turning", [("lamp", via_boost(E["i_lamp"]), "bar2"), ("motor", via_boost(E["mot_avg"]), "bar3"), ("", via_boost(E["mx_q"]), "bar4"),
                                 ("chip", E["c3_avg"], "bar"), ("", E["boost_q"], "bar4")], E["cell_typ"], f"{E['h_beacon']:.1f} h"),
             ("lamp alone, parked", [("lamp", via_boost(E["i_lamp"]), "bar2"), ("", via_boost(E["mx_q"]), "bar4"), ("chip", E["c3_avg"], "bar"), ("", E["boost_q"], "bar4")],
              E["cell_lamp"], f"{E['h_lamp']:.1f} h"),
             ("asleep, boost off", [("chip", E["c3_avg"], "bar"), ("", 0.04, "bar4")], E["cell_idle"], f"{E['h_idle']/24:.0f} days")]
    y = 52
    for name, parts, total, hours in modes:
        o.append(T(ox - 10, y + 15, name, "lab", "end"))
        x = ox
        for lab, ma, cls in parts:
            wd = X(ma) - ox
            o.append(rect(x, y, x + wd, y + 22, cls))
            if lab and wd >= 6.5 * len(lab) + 8:
                o.append(T(x + wd / 2, y + 15, lab, "fn", "middle", 'style="fill:var(--paper)"' if cls == "bar" else 'style="fill:var(--ink)"'))
            x += wd
        o.append(T(x + 8, y + 15, f"{total:.0f} mA", "num"))
        o.append(T(x + 70, y + 15, hours, "lab"))
        y += 40
    for ma in (0, 50, 100, 150):
        o.append(line(X(ma), y - 10, X(ma), y - 4))
        o.append(T(X(ma), y + 10, f"{ma}", "num", "middle"))
    o.append(T(X(75), y + 26, "mA from a 3.7 V cell", "fn", "middle"))
    o.append(T(20, y + 54, "Bars, left to right: the lamp (brass), the motor (grey), the driver, the controller (black), the boost's keep.", "fn"))
    o.append(T(20, y + 68, f"Each mA on the 5 V rail costs {num['ma_per_ma']:.2f} from the cell (5 / {E['boost_eff']:.2f} / {E['v_cell']:.1f}); the controller's {E['c3_avg']:.0f} mA skip the boost.", "fn"))
    o.append(T(20, y + 82, f"The lamp is {num['lamp_share']*100:.0f} % of the beacon. Charging: {E['chg_ma']:.0f} mA back for {E['h_charge']:.1f} h; {num['usb_a_running']:.1f} A from the adapter if it runs meanwhile.", "fn"))
    return svg(660, y + 96, "".join(o), "The budget from the cell")


def fig_rail():
    ox, oy, w, h = 70, 206, 420, 164
    X = lambda v: ox + (v - 3.0) / 1.2 * w                               # noqa: E731
    Y = lambda v: oy - (v - 2.5) / 1.8 * h                               # noqa: E731
    o = [T(20, 24, "What the controller's rail does as the cell empties", "h"), axes(ox, oy, w, h)]
    for v, pct in SOC.items():
        o.append(line(X(v), oy, X(v), oy + 5))
        o.append(T(X(v), oy + 18, f"{v:.1f}", "num", "middle"))
        o.append(T(X(v), oy + 34, f"{pct} %", "fn", "middle"))
    o.append(T(ox + w / 2, oy + 52, "cell voltage, and about how much of the cell is left at it", "fn", "middle"))
    for v in (2.5, 3.0, 3.5, 4.0):
        o.append(line(ox - 5, Y(v), ox, Y(v)))
        o.append(T(ox - 8, Y(v) + 4, f"{v:.1f}", "num", "end"))
    o.append(T(ox - 8, oy - h - 6, "V", "fn", "end"))
    o.append(poly([(X(3.0), Y(3.0)), (X(4.2), Y(4.2))], "grey"))
    o.append(poly([(X(3.0), Y(3.0 - E["diode_v"])), (X(4.2), Y(4.2 - E["diode_v"]))], "greys"))
    rail = [(X(v / 100), Y(min(3.3, v / 100 - E["diode_v"] - LDO_DROP))) for v in range(300, 421, 2)]
    o.append(poly(rail, "ink"))
    o.append(line(ox, Y(C3_MIN), ox + w, Y(C3_MIN), "grey"))
    for vc in (E["v_cell_low"], E["v_cell_low"] + 0.2):
        o.append(line(X(vc), oy, X(vc), oy - h, "diag"))
    o.append(T(X(E["v_cell_low"] + 0.2) + 5, oy - h + 14, f"{E['v_cell_low'] + 0.2:.1f} V: lamp low, two blinks", "fn"))
    o.append(T(X(E["v_cell_low"]) - 5, oy - h + 14, f"{E['v_cell_low']:.1f} V: parks,", "fn", "end"))
    o.append(T(X(E["v_cell_low"]) - 5, oy - h + 28, "dark, boost off", "fn", "end"))
    o.append(circ(X(num["cell_floor"]), Y(C3_MIN), 4, "solid"))
    o.append(circ(X(num["cell_rail"]), Y(3.3), 4, "solid"))
    o.append(circ(X(E["v_cell_low"]), Y(num["rail_at_low"]), 4, "hollow"))
    o.append(T(X(4.2) + 6, Y(4.2) + 4, "the cell (dashed)", "fn"))
    o.append(T(X(4.2) + 6, Y(4.2 - E["diode_v"]) + 10, f"5V pin: cell − {E['diode_v']:.2f} V", "fn"))
    o.append(T(X(4.2) - 4, Y(3.3) + 16, f"the 3.3 V rail, true above a {num['cell_rail']:.2f} V cell", "lab", "end"))
    o.append(T(X(4.2) - 4, Y(C3_MIN) + 16, f"the chip's {C3_MIN:.1f} V floor: a {num['cell_floor']:.2f} V cell", "fn", "end"))
    o.append(T(20, oy + 70, f"The regulator needs {LDO_DROP:.1f} V over 3.3: the rail is 3.3 V down to a {num['cell_rail']:.2f} V cell, then follows it {E['diode_v'] + LDO_DROP:.2f} V behind.", "fn"))
    o.append(T(20, oy + 84, f"The firmware stops at {E['v_cell_low']:.1f} V, where the rail is still {num['rail_at_low']:.2f} (hollow dot); the cell's own {V_PROTECT} V cut is never reached.", "fn"))
    return svg(660, 302, "".join(o), "The rail and the cell")


num["stretch_um"] = num["axial_per_n"] * L_LEG / (E_BRASS * A_ROD) * 1e6


def fig_cage():
    s = 1.1
    cx, by = 190, 250
    top = by - D["leg_h"] * s
    o = [T(20, 24, "Why the rods lean: a sideways push becomes a pull along the brass", "h")]
    o.append(rect(cx - D["disc_d"] / 2 * s, by, cx + D["disc_d"] / 2 * s, by + D["disc_t"] * s, "soft"))
    for sgn in (-1, 1):
        o.append(line(cx + sgn * D["ast_r"] * s, by, cx + sgn * D["ast_r"] * s, top, "grey"))
        o.append(line(cx + sgn * D["leg_r0"] * s, by, cx + sgn * D["ast_r"] * s, top, "ink"))
    o.append(rect(cx - D["deck_d"] / 2 * s, top - D["deck_t"] * s, cx + D["deck_d"] / 2 * s, top, "soft"))
    o.append(arrow(cx + 92, top - 2, cx + D["deck_d"] / 2 * s + 3, top - 2))
    o.append(T(cx + 62, top + 16, "1 N sideways", "lab"))
    o.append(T(cx + 62, top + 30, f"moves the deck {1 / num['k_cage']:.2f} mm", "fn"))
    xl = cx - (D["leg_r0"] + D["ast_r"]) / 2 * s
    xr = cx + (D["leg_r0"] + D["ast_r"]) / 2 * s
    yl = (by + top) / 2
    o.append(T(xl - 10, yl, f"pulls {num['axial_per_n']:.0f} N", "lab", "end"))
    o.append(T(xl - 10, yl + 14, f"stretches {num['stretch_um']:.0f} µm", "fn", "end"))
    o.append(T(xr + 10, yl, f"pushes {num['axial_per_n']:.0f} N", "lab"))
    o.append(T(xr + 10, yl + 14, f"shortens {num['stretch_um']:.0f} µm", "fn"))
    o.append(T(cx, by + 26, "dashed: four vertical rods at the deck's radius, for comparison", "fn", "middle"))
    rows = [("four vertical rods", f"{num['k_bend']:.2f} N/mm at the deck: {1 / num['k_bend']:.0f} mm per newton,", f"swaying at about {num['f_vertical']:.0f} Hz"),
            (f"leaning {D['leg_deg']:.1f}°", f"{num['k_cage']:.0f} N/mm: {1 / num['k_cage']:.2f} mm per newton, {num['f_cage']:.0f} Hz;", f"{num['lean_x']:.0f} times as stiff. A tripod's trick"),
            ("each rod as a column", f"carries {num['rod_load']:.2f} N, buckles at {num['euler']:.0f}: {num['euler_x']:.0f} to one;", f"the whole lantern on one rod, {num['euler'] / num['lantern_n']:.0f} to one"),
            ("the live rod as a wire", f"{num['rod_mohm']:.1f} mΩ, {num['rod_mv']:.1f} mV along it at full:", "the lamp does not notice"),
            ("the roof on three rods", f"soldered through its dome {D['leg_top']:.0f} mm up: the cage", "closed at the top as well as at the deck")]
    for i, (a_, b_, c_) in enumerate(rows):
        yy = 56 + i * 46
        o.append(T(392, yy, a_, "lab"))
        o.append(T(392, yy + 14, b_, "fn"))
        o.append(T(392, yy + 28, c_, "fn"))
    return svg(660, 296, "".join(o), "The leaning rods")


def fig_tip():
    s = 0.85
    cx, by = 150, 262
    z = lambda zz: by - zz * s                                            # noqa: E731
    o = [T(20, 24, "The coaster as the fuse", "h")]
    o.append(rect(cx - D["disc_d"] / 2 * s, z(0), cx + D["disc_d"] / 2 * s, z(D["disc_t"]), "soft"))
    o.append(rect(cx - D["hold_w"] / 2 * s, z(D["disc_t"]), cx + D["hold_w"] / 2 * s, z(D["disc_t"] + D["hold_h"]), "hollow"))
    for sgn in (-1, 1):
        o.append(poly([(cx + sgn * D["leg_r0"] * s, z(D["disc_t"])), (cx + sgn * D["ast_r"] * s, z(D["z_deck0"])), (cx + sgn * D["ast_r"] * s, z(D["z_deck1"] + D["leg_top"]))], "thin"))
    o.append(line(cx, z(D["z_tube0"]), cx, z(D["z_deck1"] + D["tube_top"])))
    o.append(rect(cx - D["deck_d"] / 2 * s, z(D["z_deck0"]), cx + D["deck_d"] / 2 * s, z(D["z_deck1"]), "soft"))
    o.append(rect(cx - D["drum_od"] / 2 * s, z(D["z_deck1"] + D["drum_z0"]), cx + D["drum_od"] / 2 * s, z(D["z_deck1"] + D["drum_top"]), "soft"))
    o.append(polygon([(cx - D["cap_d"] / 2 * s, z(D["z_cap_rim"])), (cx + D["cap_d"] / 2 * s, z(D["z_cap_rim"])), (cx + D["cap_hole"] / 2 * s + 3, z(D["z_cap_top"])), (cx - D["cap_hole"] / 2 * s - 3, z(D["z_cap_top"]))], "soft"))
    o.append(rect(cx - D["nip_od"] / 2 * s, z(D["z_cap_top"]), cx + D["nip_od"] / 2 * s, z(D["z_deck1"] + D["ball_bot"]), "soft"))
    yb = z(D["z_deck1"] + D["ball_c"])
    o.append(circ(cx, yb, D["ball_d"] / 2 * s, "soft"))
    for zz, cls, lab in ((D["cg"], "solid", f"centre of mass, {D['cg']:.0f} mm up"), (D["cg_b"], "hollow", f"{D['cg_b']:.0f} mm with {D['ballast_g']:.0f} g of washers")):
        o.append(circ(cx, z(zz), 4.5, cls))
        o.append(line(cx + 6, z(zz), cx + 40, z(zz), "greys"))
        o.append(T(cx + 44, z(zz) + 4, lab, "fn"))
    xe = cx + D["disc_d"] / 2 * s
    o.append(line(cx, z(D["cg"]), xe, z(0), "grey"))
    o.append(circ(xe, z(0), 3.5, "solid"))
    o.append(T(xe + 8, z(0) - 2, f"pivots here at {D['tip_deg']:.0f}°; {D['tip_deg_b']:.0f}° weighted", "fn"))
    o.append(arrow(cx + 72, yb, cx + D["ball_d"] / 2 * s + 3, yb))
    o.append(T(cx + 78, yb - 4, f"{num['f_tip']:.1f} N here tips it", "lab"))
    o.append(T(cx + 78, yb + 10, f"{num['f_tip_b']:.1f} N with the washers", "fn"))
    rows = [("to tip it over", f"{num['f_tip']:.1f} N at the ball, {num['f_tip_b']:.1f} weighted:", f"{num['W_N']:.2f} N × {D['disc_d'] / 2:.1f} mm / {D['height']:.0f} mm"),
            ("each rod, at that push", f"carries {num['rod_axial_at_tip']:.1f} N along it, {num['euler'] / num['rod_axial_at_tip']:.0f} under", f"its {num['euler']:.0f} N; the deck moves {num['delta_tip']:.2f} mm"),
            ("to bend a rod for good", f"about {num['f_set_mid']:.1f} N on its middle, alone:", "nothing on a desk does that"),
            ("a glazing bar's free tip", f"takes a set at {num['f_set_tip']:.1f} N:", "a fingernail hooked under the roof"),
            ("so the coaster is the fuse", "it tips, lands on brass,", "and stands up again")]
    for i, (a_, b_, c_) in enumerate(rows):
        yy = 56 + i * 46
        o.append(T(400, yy, a_, "lab"))
        o.append(T(400, yy + 14, b_, "fn"))
        o.append(T(400, yy + 28, c_, "fn"))
    return svg(660, 296, "".join(o), "Tipping")


def fig_reed():
    o = [T(20, 24, "The magnet over the reed, from above", "h"), T(350, 24, "The field at the reed's tip as the magnet passes", "h")]
    cx, cy, k = 200, 165, 5.6
    rc = (D["tube_od"] / 2 + D["arm_len"]) * k
    o.append(rect(cx - D["mot_w"] / 2 * k, cy - D["mot_t"] / 2 * k, cx + D["mot_w"] / 2 * k, cy + D["mot_t"] / 2 * k, "grey"))
    o.append(T(cx, cy + 4, "the motor", "fn", "middle"))
    o.append(circ(cx, cy, D["mag_r"] * k, "grey"))
    o.append(line(*pt(cx, cy, D["tube_od"] / 2 * k, 125), *pt(cx, cy, rc, 125), "ink"))
    ry = cy - D["reed_y"] * k
    o.append(circ(cx, ry, D["reed_d"] / 2 * k, "hollow"))
    mx, my = pt(cx, cy, D["mag_r"] * k, 125)
    o.append(circ(mx, my, D["mag_d"] / 2 * k, "solid"))
    xa, ya = pt(cx, cy, D["mag_r"] * k, 112)
    xb, yb = pt(cx, cy, D["mag_r"] * k, 100)
    o.append(arrow(xa, ya, xb, yb))
    o.append(T(cx - rc - 8, cy - 40, f"the magnet, {D['mag_d']:.0f} × {D['mag_t']:.0f} N52", "fn", "end"))
    o.append(T(cx - rc - 8, cy - 26, f"under the arm's tip, r {D['mag_r']:.0f}", "fn", "end"))
    o.append(T(cx + 14, ry - 26, "the reed's tip, standing", "lab"))
    o.append(T(cx + 14, ry - 12, f"{D['reed_gap']:.0f} mm under the magnet's path", "fn"))
    o.append(T(cx + rc + 8, cy + 30, "the arm, 1 mm rod,", "fn"))
    o.append(T(cx + rc + 8, cy + 44, "soldered on the spine", "fn"))
    o.append(arrow(cx, cy + D["mot_t"] / 2 * k + 4, cx, cy + rc + 22))
    o.append(T(cx, cy + rc + 38, "front: the window faces here", "fn", "middle"))
    o.append(T(cx, cy + rc + 52, "when the magnet is over the reed", "fn", "middle"))
    ox, oy, w, h = 400, 196, 230, 140
    X = lambda x: ox + (x + 8) / 16 * w                                  # noqa: E731
    Y = lambda mT: oy - min(mT, 40) / 40 * h                             # noqa: E731
    o.append(axes(ox, oy, w, h))
    for x in (-8, -4, 0, 4, 8):
        o.append(line(X(x), oy, X(x), oy + 5))
        o.append(T(X(x), oy + 18, f"{x}", "num", "middle"))
    o.append(T(ox + w / 2, oy + 34, "the magnet's position along its path, mm", "fn", "middle"))
    for mT in (10, 20, 30, 40):
        o.append(line(ox - 5, Y(mT), ox, Y(mT)))
        o.append(T(ox - 8, Y(mT) + 4, f"{mT}", "num", "end"))
    o.append(T(ox - 8, oy - h - 6, "mT", "fn", "end"))
    for sgn in (-1, 1):
        pts = []
        x = 1.5
        while x <= 8.0:
            pts.append((X(sgn * x), Y(abs(b_z(x / 1000, Z_C)) * 1000)))
            x += 0.1
        o.append(poly(pts, "ink"))
    o.append(T(X(0), oy - h - 6, f"{num['b_tip']:.0f} mT directly under", "lab", "middle"))
    o.append(line(ox, Y(B_OPERATE * 1000), ox + w, Y(B_OPERATE * 1000), "grey"))
    o.append(T(X(3.6), Y(B_OPERATE * 1000) - 9, f"closes at ~{B_OPERATE * 1000:.0f} mT", "fn"))
    for sgn in (-1, 1):
        o.append(circ(X(sgn * num["x_operate"]), Y(B_OPERATE * 1000), 4, "solid"))
    yb2 = oy + 46
    o.append(line(X(-num["x_operate"]), yb2, X(num["x_operate"]), yb2, "ink"))
    o.append(line(X(-num["x_operate"]), yb2 - 4, X(-num["x_operate"]), yb2 + 4, "ink"))
    o.append(line(X(num["x_operate"]), yb2 - 4, X(num["x_operate"]), yb2 + 4, "ink"))
    o.append(T(X(0), yb2 + 16, f"{2 * num['x_operate']:.0f} mm: about {num['pulse_s']:.1f} s, {num['pulse_deg']:.0f}° of each turn", "fn", "middle"))
    o.append(T(X(0), yb2 + 30, "the firmware takes one edge of it", "fn", "middle"))
    return svg(660, 300, "".join(o), "The reed")


# ----------------------------------------------------------------------------- the text
def chapters():
    """List of (heading, [paragraphs or ('fig', svg, caption)])."""
    return [
        ("The whole thing in one sentence", [
            f"A {D['fil_l']:.0f} mm LED filament stands still in the open on four brass rods; a brass shutter with a {D['win_deg']:.0f}° window turns round it once every {E['period']:.1f} s from a gearmotor at the foot; a 16340 cell beside the motor feeds a 5 V boost that runs both; and a charger fills the cell through a notch in the coaster.",
            "Everything on the sheet follows from that: why the lamp is fixed and the brass moves, why the rail is 5 V and not the cell, why the motor runs at a third of its voltage, why the rods lean, why a reed and not a sensor, why the coaster is the fuse. This page takes each in the order the sheet made them and shows the working.",
        ]),
        ("A fixed lamp and a turning window: the light's character", [
            "A lighthouse does not spin its lamp. The lamp burns still at the focus and the lens turns round it, so the beam sweeps the horizon and nobody has to feed a moving flame. The sheet does the same with a brass drum: the filament is wired to nothing that moves, and the window carries the light round the room.",
            f"The pattern a light makes is its character, and sailors tell lights apart by it. Here the window is {D['win_deg']:.0f}° of the drum, so the room sees light for {E['pass_s']:.1f} s and brass for {num['dark_s']:.0f} s, every {E['period']:.1f} s. In a chart's notation that is Fl W {E['period']:.1f}s, a flashing light: a flash shorter than the dark between. A 180° window would make it isophase, light and dark equal; wider still, occulting.",
            ("fig", fig_character(), f"Left: the lamp on the axis, the brass drum round it, the window and the fan of light that leaves it. Right: what the room sees, {E['pass_s']:.1f} s of light and {num['dark_s']:.0f} s of brass, twice."),
            f"The speed is {E['rpm_target']:.0f} rpm, {num['omega']:.0f}° a second. On a wall 2 m away the edge of the light crosses at {num['edge_speed_2m']:.1f} m/s, a slow walking pace: slow enough to watch, quick enough that the eye reads a sweep and not a lamp going on and off. Faster looks like a warning light; slower, like a fault.",
        ]),
        ("How much light leaves the window", [
            f"The filament takes {num['p_lamp'] * 1000:.0f} mW at full, and a filament LED gives about {LM_PER_W:.0f} lumens a watt: about {num['lm_full']:.0f} lumens, {num['lm_day']:.0f} at the everyday {E['lamp_duty'] * 100:.0f} %. A candle gives 13. A vertical strip radiates sideways with an intensity of its flux over π², so {num['cd_day']:.1f} candela everyday and {num['cd_full']:.1f} at full.",
            f"Intensity over distance squared is the light on a wall: {num['lux'][1.0]:.1f} lux at 1 m, {num['lux'][2.0]:.2f} at 2, {num['lux'][3.0]:.2f} at 3. A full moon gives {FULL_MOON} lux and a lit room {ROOM_LUX:.0f}. In a lit room the sweep is a glint moving along the wall; with the lights down it is {num['moons_2m']:.0f} moons at 2 m, a pool you can watch cross the room.",
            ("fig", fig_light(), f"Light on a wall the window faces, against distance, on a log scale: the everyday lamp solid, the full lamp dashed, the full moon for comparison. The three dots are the numbers in the text."),
            f"There is no glass. Rev C had an acrylic tube round the lantern and Rev D took it out at the builder's word, and nothing optical went with it: a plain tube is a window, not a lens, since light from the axis meets both its surfaces square on and goes straight through. A lighthouse's trick, the Fresnel lens that folds a lamp's whole output into one beam, is the one part of a lighthouse the sheet leaves out either way. The window lets out a third of the azimuth at a time; the rest hits the brass inside the drum, which reflects about 60 % of warm light, so some of it follows the window out. Heat is not a worry: {num['p_lamp'] * HEAT_FRAC * 1000:.0f} mW of heat from a strip in free air, inside a brass drum of {num['lantern_m2'] * 1e4:.0f} cm² open at both ends, warms the drum at most {num['lantern_dT']:.0f} °C at full, {num['lantern_dT_day']:.0f} everyday; the air through it takes most of that away.",
        ]),
        ("The filament behind a resistor, and why the rail is 5 V", [
            f"An LED filament is a row of blue dies side by side on a ceramic strip under a yellow phosphor, which is why it wants a diode's 3 V and not a bulb's 120. A diode's current climbs steeply with the voltage across it, e-fold every {S_FIL * 1000:.0f} mV or so here, so no supply may be connected to it directly: a resistor in series sets the current, and the current is where the filament's curve meets the resistor's line.",
            f"From the 5 V rail through {E['r_lamp']:.1f} Ω the two cross at {num['v_lamp']:.2f} V and {num['i_full']:.0f} mA, under the strip's {E['fil_rated']:.0f} mA rating (the sheet's {E['i_lamp_max']:.0f} mA takes the voltage as a flat 3.0). The resistor has 2 V across it, and that is the point: a 5 % wobble in the rail moves the current only to {num['rail_pm5'][0]:.0f} or {num['rail_pm5'][1]:.0f} mA.",
            ("fig", fig_loadline(), f"The filament's curve against the resistor lines. Solid: from the 5 V rail through {E['r_lamp']:.1f} Ω, a flat line. Dashed: the resistor that would give the same current straight from a 3.7 V cell, at a full cell, a half-full one and an empty one."),
            f"Run the same lamp straight from the cell and the resistor shrinks to {num['r_raw']:.0f} Ω, because only {E['v_cell'] - MX_DROP - num['v_lamp']:.2f} V is left to drop at 3.7 V. Then a full cell pushes {num['raw'][E['v_cell_full']]:.0f} mA through it, over the rating, and an empty one {num['raw'][E['v_cell_low']]:.0f}: bright for the first hour, dim for the rest. The boost's price is {(1 - E['boost_eff']) * 100:.0f} % and the resistor's 2 V another 40, so the lamp gets {num['lamp_eff'] * 100:.0f} % of what the cell pays.",
            f"A constant-current driver fed from the cell would do better: about {num['cc_saving_ma']:.0f} mA less from the cell with the beacon on, {num['h_beacon_cc']:.1f} hours a charge instead of {E['h_beacon']:.1f}. The sheet spends it for one board fewer and a rail the motor wants anyway; it is the upgrade if the hours ever feel short.",
        ]),
        ("Warm white at 2700 K, and the heat", [
            "Colour temperature is the colour of a glowing body: a candle at 1 850 K, a tungsten bulb at 2 700, halogen at 3 000, the midday sun at 5 500. The lamp in a lighthouse you remember from a photograph is an incandescent bulb behind a lens, 2 700 to 3 000 K; the oil flames before it were a candle's colour; the LED beacons that replaced them are a colder white. The sheet picks the bulb.",
            "The family's spare filaments are 2 200 K, a candle, and they are right for a pool of amber on brass, the hologram's and the satellite's job. A lighthouse's lamp is the light itself, and the house rule says white or warm white. At 2 700 K the filament reads as a lamp and the brass round it reads as brass, not as more amber. The phosphor is yellow when it is off, the one thing about an LED filament that looks wrong in a lantern; the shutter closes over it.",
            f"PWM dims it at 5 kHz, {num['pulses_per_deg']:.0f} pulses for every degree the shutter turns, so neither the eye nor a phone camera sees anything but the sweep. Dimming by duty keeps the colour: a phosphor LED run at lower current drifts a shade bluer, a pulsed one does not. The filament runs at a quarter of the power each filament carries in a 4 W bulb, in air a couple of degrees over the room; the two resistors put {num['p_res'] * 1000:.0f} mW into the coaster's hollow and warm the brass {num['res_dT']:.1f} °C.",
        ]),
        ("A gearmotor at a third of its voltage", [
            f"A brushed DC motor's speed follows its voltage and its torque follows its current. The N20 is a 30 000 rpm motor behind a {GEAR:.0f}:1 gearbox: 30 rpm at 6 V, {E['rpm_5v']:.0f} on the 5 V rail. The sheet wants {E['rpm_target']:.0f}, so the driver chops the rail at 20 kHz and the motor sees the average, {E['duty_mot'] * 100:.0f} % duty on paper.",
            f"On paper, because a small motor does not start until about {V_DEAD:.1f} V has overcome its brushes and its gears; above that the speed climbs straight. With the dead band the {E['rpm_target']:.0f} rpm point sits nearer {num['d_real'] * 100:.0f} % duty. That is why the reed is there: the firmware measures each revolution and trims the duty until the period is {E['period']:.1f} s, whatever this motor's batch and bearings do. The regulated rail serves the same loop: a motor fed from the cell would slow as the cell emptied, and the loop would chase it all day.",
            ("fig", fig_motor(), f"Left: output speed against duty, with and without the brushes' dead band; the sheet's {E['duty_mot'] * 100:.0f} % and the likelier {num['d_real'] * 100:.0f} %. Right: the current on the 5 V rail in the first second, ramped as the firmware does it, and the step both loads would make switched on at once as the boost starts."),
            f"The gearbox turns speed into torque, {GEAR:.0f} times over; the shutter, a {num['drum_g']:.0f} g drum on a spine in a tube-ring hub, needs a thousandth of what the output can give. The danger runs the other way: if the shutter ever jams the loop winds the duty up to 100 %, the stalled motor takes {num['i_stall_5v']:.0f} mA from the rail, and plastic gears do not like a stall. The reed's silence catches it in two periods. 20 kHz is above hearing, and the winding's time constant of {num['tau_e_us']:.0f} µs against a {num['pwm_period_us']:.0f} µs period smooths the chopped rail into a near-steady current; the gearbox still whispers at {num['rotor_hz']:.0f} Hz, and the hot-glue bed takes most of it.",
            f"The ramp is for the boost. While a boost converter starts it can feed only about {BOOST_START_MA:.0f} mA; more at that moment holds the rail down for good. So the rail comes up with both outputs at zero, the motor's duty ramps over {T_RAMP:.1f} s and the lamp fades up after it: nothing ever lands on the rail as a step. Without the ramp a stalled rotor at {num['i_start_real']:.0f} mA and a cold lamp at {E['i_lamp_max']:.0f} would be {num['step_no_ramp']:.0f} mA in one step. The brake is a short: both inputs high, the motor's own back-EMF stops the rotor in about {T_BRAKE * 1000:.0f} ms, {num['brake_deg']:.1f}° of the shutter.",
        ]),
        ("The boost, and the budget from the cell", [
            f"A boost converter stores energy in an inductor a million times a second and lets it out at a higher voltage; this one makes 5 V from the cell's 3.3 to 4.2 at about {E['boost_eff'] * 100:.0f} %. Power in is power out over the efficiency, so every milliamp on the 5 V rail costs {num['ma_per_ma']:.2f} from a 3.7 V cell. The sheet's rail of {E['rail_typ']:.0f} mA is {via_boost(E['rail_typ']):.0f} from the cell; the controller takes its {E['c3_avg']:.0f} straight from the cell through the diode, and the boost keeps about 1 for itself: {E['cell_typ']:.0f} mA with the beacon turning.",
            ("fig", fig_budget(), f"The cell's current in the three modes, split by what spends it, with the hours that follow from 90 % of {E['cell_mah']:.0f} mAh."),
            f"The lamp is {num['lamp_share'] * 100:.0f} % of it. The motor, at a third of its voltage and a third of the time, is almost nothing. The controller awake is the second biggest line, and when the boost is off it is {num['c3_share_idle'] * 100:.0f} % of the {E['cell_idle']:.0f} mA a sleeping lighthouse spends. Light sleep on the controller, the satellite's trick, would take that figure to under 1 mA and the {E['h_idle'] / 24:.0f} days to months; it is firmware, not wiring, and the sheet leaves it for the bench.",
            "GPIO7 is the other half of the budget. The boost's enable pin shuts it down with a true disconnect, so a dark, parked lighthouse has no 5 V rail at all and the driver draws nothing. The pin is pulled up to the cell on the board, so a controller that has crashed would leave the rail on; the firmware drives it low first thing at boot and never leaves it floating.",
        ]),
        ("The cell, one diode, and the rail as the cell empties", [
            f"The cell is the family's Nitecore 16340: {D['cell_d']} × {D['cell_l']} mm, {E['cell_mah']:.0f} mAh, 3.6 V nominal, 4.2 full, with its protection under the wrap and a button top. A lithium cell's voltage falls slowly from 4.2 to about 3.5 over most of its charge, then quickly; the firmware's {E['v_cell_low']:.1f} V cut-off leaves a few per cent in it, which is the 90 % the hours count on. The protection's own cut at {V_PROTECT} V is a last line it never reaches.",
            f"The SuperMini has no battery input. Its 5V pin is the USB socket's VBUS with nothing in between, so a flashing cable would put 5 V on the cell; one Schottky between the charger's BAT pad and the pin, band toward the controller, drops {E['diode_v']:.2f} V and lets nothing back. Behind the pin a small regulator makes 3.3 V and needs about {LDO_DROP:.1f} V of headroom, so the rail is a true 3.3 V down to a {num['cell_rail']:.2f} V cell and follows the cell down below that: {num['rail_at_low']:.2f} V at the cut-off, still over the chip's {C3_MIN:.1f} V floor, which a {num['cell_floor']:.2f} V cell would reach. The cut-off sits where the controller still works properly, not where the cell dies.",
            ("fig", fig_rail(), f"The cell, the 5V pin and the rail against the cell's voltage, with about how much of the cell is left at each. The rail is a true 3.3 V down to {num['cell_rail']:.2f} V, which is most of the cell; the firmware's two lines are at {E['v_cell_low'] + 0.2:.1f} and {E['v_cell_low']:.1f} V."),
            f"Two 100 kΩ halve the cell for GPIO4: {E['v_sense_full']:.2f} V at full, inside the ADC's range at its 11 dB setting, {E['i_div_ua']:.0f} µA for ever, {num['div_years']:.0f} years of the cell. The C3's ADC is noisy and its scale is per chip, so the firmware averages a burst of readings once a minute and the first bench run writes one calibration point into flash; a 100 nF across the lower resistor would quiet it further if the readings jitter. Below {E['v_cell_low'] + 0.2:.1f} V the lamp dims and blinks twice; below {E['v_cell_low']:.1f} the shutter parks, the lamp goes out, the boost goes off and the controller waits for the button or a cable.",
        ]),
        ("Charging through the coaster", [
            f"The charger is a linear chip, a controlled resistor between the cable's 5 V and the cell: {E['chg_ma']:.0f} mA with its jumper cut, {num['c_rate']:.2f} C for this cell, what a 16340 charger feeds it. Constant current puts about {CC_SHARE * 100:.0f} % in over {num['cc_h']:.1f} h; then it holds 4.2 V and the current tapers for {num['cv_h']:.1f} h more, {E['h_charge']:.1f} h in all. Its safety timer stops at {HOURS:.0f} h, {num['timer_x']:.1f} times that, so a healthy charge never meets it.",
            f"The drop across a linear charger is heat: {V_USB - E['v_cell']:.1f} V × {E['chg_ma']:.0f} mA = {num['chg_heat'] * 1000:.0f} mW in a chip glued up to the brass ceiling of the hollow. The coaster is its heatsink, {num['coaster_m2'] * 1e4:.0f} cm² of brass, and it warms about {num['coaster_dT']:.0f} °C while the cell fills: a warm coaster is how you know it is charging, besides the orange LED in the notch. The chip throttles itself at a 125 °C junction and never gets near it.",
            f"Power path means the cable feeds the loads first and the cell gets the rest, so the lighthouse runs while it charges and the cell is never run down by its own lamp with a cable in. Charging and running together ask the adapter for about {num['usb_a_running']:.1f} A; any 1 A phone adapter does. The cell's own cost is calendar life: a 16340 kept at 4.2 V ages faster than one that is cycled, so a lighthouse that lives on its cable should be charged and unplugged rather than left charging; the chip's timer stops it after six hours either way.",
        ]),
        ("Why the rods lean: four wires as a tower", [
            f"Each rod is a 1.5 mm brass column {D['leg_h']:.0f} mm long between the coaster and the deck. Fixed at both ends it buckles at {num['euler']:.0f} N and carries {num['rod_load']:.2f}, a quarter of the lantern's {D['lantern_g']:.0f} g: {num['euler_x']:.0f} to one. The whole lantern on one rod would still leave {num['euler'] / num['lantern_n']:.0f}. Buckling is not the question; sway is.",
            f"Four vertical rods would sway like four springs. A rod's bending stiffness goes as the fourth power of its diameter over the cube of its length, and four of these give {num['k_bend']:.2f} N/mm at the deck: {1 / num['k_bend']:.0f} mm for every newton, swinging at about {num['f_vertical']:.0f} Hz. Lean them {D['leg_deg']:.1f}° and a sideways push has to stretch two rods and shorten two, which brass resists along its length and not across it: {num['k_axial']:.0f} N/mm more, {num['lean_x']:.0f} times as stiff, {1 / num['k_cage']:.2f} mm per newton, {num['f_cage']:.0f} Hz. A camera tripod stands on the same idea. The lean is why the cage looks like a lighthouse, and why it feels like one piece.",
            ("fig", fig_cage(), f"A 1 N push at the deck pulls {num['axial_per_n']:.0f} N along one rod and pushes {num['axial_per_n']:.0f} along the other; brass stretches {num['stretch_um']:.0f} µm for that and the deck moves {1 / num['k_cage']:.2f} mm. Dashed: four vertical rods, {num['lean_x']:.0f} times softer. The rows are the cage's five numbers."),
            f"The deck is what makes it a frame: a solid brass disc threaded on all four rods and glued, so no rod bends alone. Above it the rods carry nothing but their own {D['leg_top']:.0f} mm as glazing bars. Two of them are wires as well, {num['rod_mohm']:.1f} mΩ each, {num['rod_mv']:.1f} mV along the live one at full, which the lamp does not notice. Above the deck three of the rods pass through the roof's dome and are soldered flush from outside, so the cage is closed at the top as well as at the deck and the roof cannot rock; the live rod stops {D['leg_top_live']:.0f} mm up, booted, and never touches it.",
        ]),
        ("The coaster as the fuse", [
            f"{D['mass']:.0f} g stand {D['height']:.0f} mm tall with their centre of mass {D['cg']:.0f} mm up: {D['disc_g']:.0f} g of it in the coaster and {num['cell_tray_g']:.0f} in the cell and its tray low at the foot. The centre of mass over the coaster's {D['disc_d'] / 2:.1f} mm radius gives the tipping angle, {D['tip_deg']:.0f}°, and a push of {num['f_tip']:.1f} N at the ball tips it. {D['ballast_g']:.0f} g of steel washers in the hollow bring the centre down to {D['cg_b']:.0f} mm, {D['tip_deg_b']:.0f}° and {num['f_tip_b']:.1f} N: a brush of a sleeve rocks it, a hand knocks it over.",
            f"Knocking it over is what it does instead of bending. Under the tipping push each rod carries about {num['rod_axial_at_tip']:.1f} N along its length, {num['euler'] / num['rod_axial_at_tip']:.0f} under its buckling load, and the deck moves {num['delta_tip']:.2f} mm. To put a set in a rod you would have to push about {num['f_set_mid']:.1f} N sideways on its middle alone, or {num['f_set_tip']:.1f} N on the free tip of a glazing bar; nothing on a desk does the first, and the second is a fingernail hooked under the roof. The coaster is the fuse: the lighthouse tips, lands on brass, and stands up again.",
            ("fig", fig_tip(), f"The lighthouse to scale with its centre of mass, with and without the washers, the line to the pivot at the coaster's edge, and the push at the ball that tips it. The rows are the fuse's numbers."),
        ]),
        ("A magnet, a reed and one edge a turn", [
            "A reed switch is two ferromagnetic blades sealed in glass with a gap between them. A field along the glass magnetises the blades, their tips attract, and they touch: no supply, no current while open, two wires. A Hall sensor would want 3.3 V, three wires and a few milliamps all day, for a position the firmware needs once a revolution.",
            f"The magnet is a {D['mag_d']:.0f} × {D['mag_t']:.0f} mm N52 disc under the collar, {D['mag_r']:.0f} mm from the axis, and the reed stands on end under its path with {D['reed_gap']:.0f} mm between. Straight under the magnet the field at the reed's tip is {num['b_tip']:.0f} mT, pointing down the glass, the direction a reed likes. A small magnet's field falls as the cube of the distance: {num['b_face'][1]:.0f} mT at 4 mm, {num['b_face'][2]:.0f} at 6, {num['b_face'][3]:.1f} at 10. So as the magnet comes round, the field at the tip rises from nothing to {num['b_tip']:.0f} mT and back inside a few millimetres of travel.",
            ("fig", fig_reed(), f"Left: the collar from above with the magnet coming round to the reed's tip; the window faces front when the magnet is over the reed. Right: the vertical field at the tip against the magnet's position (a dipole, so the middle is off the chart), the level a reed closes at, and the {2 * num['x_operate']:.0f} mm of travel it stays closed for. The field reverses {num['x_zero']:.1f} mm out, which a reed does not mind."),
            f"A reed of this sensitivity closes at a few millitesla along it, {B_OPERATE * 1000:.0f} in this model, which the magnet's field reaches about {num['x_operate']:.1f} mm either side of centre: {2 * num['x_operate']:.0f} mm of travel at {num['v_mag']:.1f} mm/s, a pulse of about {num['pulse_s']:.1f} s, {num['pulse_deg']:.0f}° of each turn. The pulse's length depends on which of the twenty reeds is picked and how it sits, so the firmware never uses it. It uses one edge, the same edge every turn, which lands at the same angle to a degree or two: the time between edges feeds the speed loop, and the park is that edge plus one offset written into flash on the first bench run, when the window is turned to face front by eye. The brake's {num['brake_deg']:.1f}° is the only scatter left.",
            f"The pull-up on GPIO6 draws {num['pullup_ua']:.0f} µA averaged over a turn. The glass is the one fragile part at the foot: the leads bend clear of the seal, and the tube is glued to the coaster on Kapton where the arm can never touch it.",
        ]),
        ("The spine as a shaft, and a wheel for a washer", [
            f"The spine is a 4 mm brass tube over the motor's 3 mm D shaft, held by a drop of gel glue, and it runs {num['span']:.0f} mm from the motor's own bearing to the hub on the deck, a ring of the 5 mm tube from the same telescoping set, whose bore gives it about {num['bearing_clear']:.1f} mm of play all round. The shutter sits just above that bearing, so its top can wander at most {num['wobble']:.2f} mm against {num['rod_clear']:.1f} mm of clearance to the nearest rod. A bowed tube is the one thing that binds: roll it on the desk before cutting and swap a bowed one.",
            f"Rev C cut the shutter's floor, the magnet's collar and the deck's bushing from 0.4 mm sheet; Rev D makes them from 1 mm rod and tube rings because the builder does not fold sheet. The loads are tiny: the shutter is {num['drum_g']:.0f} g on two bars, and a 1 mm brass rod reaching from the spine to the drum's wall sags about {num['bar_defl_um']:.0f} µm under its share, nothing a finger could feel. What matters is squareness, so the wheel is soldered up on the spine itself, hub ring first, spokes against its flanks, rim ring on their ends: the spine is the jig, and the bearing cannot be off centre. 63/37 solder melts at 183 °C, well under anything the brass minds.",
            "Nothing in Rev D is painted or covered. The motor's steel can, the glass reed, the brass arm and the cell's black tray stand on the coaster in the open, each a colour the house rule allows, and there is no closed surface to lift. The lighthouse is brass, warm light and one dark cell.",
        ]),
    ]


NUMBERS = [
    (f"Fl W {E['period']:.1f}s", f"the light's character: {D['win_deg']:.0f}° of 360° × {E['period']:.1f} s = {E['pass_s']:.1f} s of light, {num['dark_s']:.0f} s of brass"),
    (f"{num['omega']:.0f}°/s", f"the shutter's speed: 360° / {E['period']:.1f} s; the pool's edge crosses a wall 2 m away at {num['edge_speed_2m']:.1f} m/s"),
    (f"{num['lm_day']:.0f} lm", f"everyday light: {num['p_lamp'] * 1000:.0f} mW × {LM_PER_W:.0f} lm/W × {E['lamp_duty']:.1f}; {num['cd_day']:.1f} cd sideways (Φ / π²); {num['lux'][2.0]:.2f} lux at 2 m, {num['moons_2m']:.0f} moons"),
    (f"{num['i_full']:.0f} mA", f"the lamp at full: the filament's curve against ({num['v_rail_eff']:.2f} − V) / {E['r_lamp']:.1f} Ω; the sheet's {E['i_lamp_max']:.0f} with a flat 3.0 V"),
    (f"{num['raw'][E['v_cell_full']]:.0f} / {num['raw'][E['v_cell_low']]:.0f} mA", f"the same lamp straight from the cell through {num['r_raw']:.0f} Ω, full and empty: why the rail is regulated"),
    (f"{num['lamp_eff'] * 100:.0f} %", f"what the lamp gets of what the cell pays: {E['boost_eff']:.2f} for the boost × {num['v_lamp']:.1f} V of 5; a constant-current driver would save {num['cc_saving_ma']:.0f} mA"),
    (f"{num['d_real'] * 100:.0f} %", f"the duty for {E['rpm_target']:.0f} rpm with a {V_DEAD:.1f} V dead band (the sheet's {E['duty_mot'] * 100:.0f} % has none); the reed loop finds it"),
    (f"{num['step_no_ramp']:.0f} mA", f"a stalled rotor and a cold lamp in one step: 5 V × {num['d_real']:.2f} / {R_WIND:.0f} Ω + {E['i_lamp_max']:.0f}, over the boost's {BOOST_START_MA:.0f} mA start"),
    (f"{E['cell_typ']:.0f} mA", f"from the cell with the beacon on: {E['rail_typ']:.0f} mA × 5 V / {E['boost_eff']:.2f} / {E['v_cell']:.1f} V + {E['c3_avg']:.0f} + {E['boost_q']:.0f}"),
    (f"{num['cell_rail']:.2f} V", f"the cell above which the controller's rail is a true 3.3 V: 3.3 + {LDO_DROP:.1f} regulator + {E['diode_v']:.2f} diode"),
    (f"{num['chg_heat'] * 1000:.0f} mW", f"heat in the charger: ({V_USB:.0f} − {E['v_cell']:.1f}) V × {E['chg_ma'] / 1000:.1f} A; the coaster warms about {num['coaster_dT']:.0f} °C"),
    (f"{E['h_charge']:.1f} h", f"the charge: {CC_SHARE:.1f} × {E['cell_mah']:.0f} / {E['chg_ma']:.0f} at constant current, then the taper; the {HOURS:.0f} h timer is {num['timer_x']:.1f}×"),
    (f"{num['euler']:.0f} N", f"a rod's buckling load, fixed at both ends: π² E I / (0.5 L)²; it carries {num['rod_load']:.2f}"),
    (f"{num['lean_x']:.0f}×", "the lean's gift to the sway stiffness: (2 E A sin²θ / L) over (48 E I / L³), plus one"),
    (f"{num['f_tip']:.1f} N", f"the push at the ball that tips it: {num['W_N']:.2f} N × {D['disc_d'] / 2:.1f} / {D['height']:.0f} mm; {num['f_tip_b']:.1f} with the washers"),
    (f"{num['b_tip']:.0f} mT", f"the field at the reed's tip under the magnet: a {D['mag_d']:.0f} × {D['mag_t']:.0f} N52 disc at {D['reed_gap']:.0f} mm, on its axis"),
    (f"{num['pulse_s']:.1f} s", f"the reed's pulse in the model: {2 * num['x_operate']:.0f} mm of travel at {num['v_mag']:.1f} mm/s; the firmware uses one edge"),
    (f"{num['wobble']:.2f} mm", f"the shutter's wander: {num['bearing_clear']:.1f} mm of play × (1 + {D['drum_top']:.0f} / {num['span']:.0f}), against {num['rod_clear']:.1f} to the nearest rod"),
]

PARTS_IDEAS = [
    ("a fixed lamp and a turning window, Fl W 7.5s, a third of the azimuth", "5/8 in brass tube, the shutter", "tube58"),
    ("speed from voltage, 1000:1, the dead band, the ramp into the boost", "N20 gearmotor", "motor"),
    ("a diode behind a resistor, the flat load line, 2700 K, 28 lumens", "LED filament", "filament"),
    ("a 5 V rail that does not sag, 88 %, the 200 mA start, power path, 650 mW", "charger board", "charger"),
    ("0.53 C, 90 % to the knee, calendar life at 4.2 V", "Nitecore 16340 cell", "cell"),
    ("the springs are the only resistance in the path", "16340 holder", "holder"),
    ("the VBUS pin, the 3.3 V floor, 20 mA awake, a noisy ADC", "ESP32-C3 SuperMini", "controller"),
    ("two half-bridges, one of them a switch, flyback inside", "MX1508 driver", "hbridge"),
    ("0.15 V between the cell and a flashing cable", "SS14 Schottky", "diode"),
    ("the cube law, a one-second pulse, one edge", "glass reed switch", "reed"),
    ("1.45 T of remanence, 68 mT at 2 mm", "N52 disc magnet", "magnet"),
    ("Euler at 190 to one, the tripod's 48×, 8 mΩ", "1.5 mm brass rod", "rod15"),
    ("a 3 mm D in a 3 mm bore, 0.2 mm in the bearing", "4 mm brass tube, the spine", "brass_tube"),
    ("80 g at the bottom, 25° and 31°, the fuse", "brass coaster", "coaster"),
    (f"two bars, an arm, a wheel: three sheet discs in rod and tube, {num['bar_defl_um']:.0f} µm of sag", "1.0 mm brass rod", "rod10"),
]

NEXT = (f"Rev D, the open lantern with no house and its three small brass pieces made from rod and tube, awaits the builder's approval. Of the eight Amazon lines ordered on 2026-11-09 (five orders, $122.64; two boxes due 11-11, the filaments 11-27) the brass sheet is cancelled and the acrylic tube goes back; the five lamp parts from Grand Brass are ordered by the builder's word; the charger (1528-6106-ND, or Adafruit 6106) is still to buy, since that morning's DigiKey order was the rover's. "
        "When the parts come: measure the check ring's thickness, the vase cap's height and the coaster's hollow and rerun build_page.py; cut the jumper before the cell meets the charger; meter the tray's leads. "
        "The first bench run writes the park offset and the ADC's calibration point into flash. The first-power measurements the record wants replace this page's figures: the current from the cell in each mode, the lamp's current at full, the period from the reed, the charge current with the jumper cut.")

FIGS = {"character": fig_character, "light": fig_light, "loadline": fig_loadline, "motor": fig_motor, "budget": fig_budget,
        "rail": fig_rail, "cage": fig_cage, "tip": fig_tip, "reed": fig_reed}


def page_html():
    o = ['<title>Desk Lighthouse Physics</title>',
         '<meta name="claude:viewport-fit-sides" content="cover">',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
         f"<style>{STYLE}</style>",
         f"<style>{PAGE_TONES}</style>",
         '<style>.wrap{max-width:880px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} figure svg{width:100%;height:auto} td,th{min-width:0}</style>',
         '<div class="wrap">',
         '<div class="masthead"><div class="eyebrow">Desk lighthouse &middot; step 2: the science and engineering</div>',
         '<h1>Why the lamp stands still and the brass turns</h1>',
         f'<div class="sub">The working behind every number on the Rev {REV} sheet (Rev C approved {APPROVED}; Rev D, the open lantern without the house, drawn that evening for approval): a fixed lamp and a turning window, how much light leaves it, a filament behind a resistor and why the rail is 5 V, a gearmotor at a third of its voltage, the boost and the budget from the cell, one diode and the rail as the cell empties, charging through the coaster, why the rods lean, the coaster as the fuse, a magnet and a reed, the spine and its wheel.<br>Read after <a href="{BUILD_PAGE}" target="_blank" rel="noopener">Desk Lighthouse Build</a>. Nothing measured yet; every figure is derived from datasheet and listing numbers and the sheet\'s dimensions.</div></div>']
    for head, items in chapters():
        o.append(f"<h2>{esc(head)}</h2>")
        for it in items:
            if isinstance(it, tuple):
                _, s, cap = it
                o.append(f"<figure>{s}<figcaption>{esc(cap)}</figcaption></figure>")
            else:
                o.append(f"<p>{esc(it)}</p>")
    o.append("<h2>The numbers on the sheet, and where they come from</h2><div class=\"tw\"><table><tr><th>Number</th><th>What it is</th></tr>")
    o += [f'<tr><td class="m">{esc(n)}</td><td>{esc(w)}</td></tr>' for n, w in NUMBERS]
    o.append("</table></div>")
    o.append("<h2>Which part each idea lives in</h2><ul>")
    o += [f'<li><strong>{esc(idea)}:</strong> the <a href="{L[key]}" target="_blank" rel="noopener">{esc(part)}</a></li>' for idea, part, key in PARTS_IDEAS]
    o.append("</ul>")
    o.append(f"<h2>What comes next</h2><p>{esc(NEXT)}</p>")
    o.append(f'<hr><p class="sub">Built by <code>docs/pages/gen/physics_page.py</code> from the dimensions, masses and budget in <code>build_page.py</code>; it also writes <code>docs/PHYSICS.md</code>. Assumptions, each a number at the top of the script: a {GEAR:.0f}:1 gearbox, a {R_WIND:.0f} Ω winding with {L_WIND * 1000:.0f} mH, a {V_DEAD:.1f} V dead band, a {T_BRAKE * 1000:.0f} ms brake; the filament at {VF0:.1f} V and {E["fil_rated"]:.0f} mA with {S_FIL * 1000:.0f} mV per e-fold and {RS_FIL:.1f} Ω inside, {LM_PER_W:.0f} lm/W, {HEAT_FRAC:.2f} of its power as heat; {H_CONV:.0f} W/m²K off the lantern and the coaster; {LDO_DROP:.1f} V of regulator headroom; {CC_SHARE:.1f} of the charge at constant current; brass at {E_BRASS / 1e9:.0f} GPa and {SY_BRASS / 1e6:.0f} MPa; an N52 disc at {BR_N52:.2f} T and a reed that closes at {B_OPERATE * 1000:.0f} mT. The charger\'s and boost\'s figures are TI\'s and Adafruit\'s; the motor\'s and the filament\'s are their listings. Nothing here has been measured on the lighthouse itself.</p>')
    o.append("</div>")
    return "\n".join(o)


def physics_md():
    o = ["# Why the lamp stands still and the brass turns: the science and engineering behind the sheet", "",
         f"Step 2 of the house rule, written {APPROVED} after Rev C was approved and revised the same evening for Rev {REV}, the open lantern without the house, which awaits approval. Generated by `pages/gen/physics_page.py`; the page `pages/desk-lighthouse-physics.html` carries the figures. Edit the script, not this file.", ""]
    for head, items in chapters():
        o += [f"## {head}", ""]
        for it in items:
            if isinstance(it, tuple):
                o += [f"*Figure: {it[2]}*", ""]
            else:
                o += [it, ""]
    o += ["## The numbers on the sheet", "", "| Number | What it is |", "| --- | --- |"]
    o += [f"| {n} | {w} |" for n, w in NUMBERS]
    o += ["", "## Which part each idea lives in", ""]
    o += [f"- {idea}: the [{part}]({L[key]})" for idea, part, key in PARTS_IDEAS]
    o += ["", "## What comes next", "", NEXT, ""]
    return "\n".join(o)


def print_pdf(html):
    PRINT.mkdir(exist_ok=True)
    css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
           ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
           "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
           "h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
           "figure{width:70%;margin:10pt auto;padding:6pt;break-inside:avoid} figure svg{width:100%} figcaption{font-size:8pt} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "p.html"
        pdf = pathlib.Path(d) / "p.pdf"
        head, tail = html.rsplit("</style>", 1)
        src.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + css + tail)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "desk-lighthouse-physics.pdf"
        out.write_bytes(pdf.read_bytes())
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [ln for ln in info.splitlines() if ln.startswith("Pages")])


def figures_png(outdir):
    """Render each figure to a PNG for checking by eye (not part of the outputs)."""
    import re
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGS.items():
        s = fn()
        w, h = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', s).groups())
        src = outdir / f"{name}.html"
        src.write_text('<!doctype html><html data-theme="light"><meta charset=utf-8>' + f"<style>{STYLE}</style><style>{PAGE_TONES}</style>"
                       "<style>html,body{margin:0;background:#fff;padding:10px} svg{width:1300px;height:auto;display:block}</style>" + s + "</html>")
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--window-size=1320,{int(h * 1300 / w) + 24}",
                        f"--screenshot={outdir / (name + '.png')}", f"file://{src}"], check=True, capture_output=True, timeout=120)
    print("png in", outdir)


def main():
    html = page_html()
    OUT.write_text(html)
    (DOCS / "PHYSICS.md").write_text(physics_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "PHYSICS.md")
    for k in sorted(num):
        v = num[k]
        if isinstance(v, dict):
            print(f"  {k} = " + ", ".join(f"{kk:g}: {vv:.3g}" for kk, vv in v.items()))
        elif isinstance(v, list):
            print(f"  {k} = " + ", ".join(f"{x:.3g}" if not isinstance(x, tuple) else f"{x[0]} {x[1]:.3g}" for x in v))
        else:
            print(f"  {k} = {v:.4g}")
    if "--png" in sys.argv:
        figures_png(sys.argv[sys.argv.index("--png") + 1])
    if "--pdf" in sys.argv:
        print_pdf(html)


if __name__ == "__main__":
    main()
