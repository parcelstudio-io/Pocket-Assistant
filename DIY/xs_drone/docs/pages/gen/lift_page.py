"""XS drone, step 2 for the lift revision (approved 2026-11-10): the science and engineering behind the bigger motors, the brass
ladder, the tilting camera, the rangers all round and the pack that has to feed it all.

Writes docs/pages/lift-physics.html, docs/lift-physics.md (the same text without the figures) and, with --pdf,
docs/pages/print/lift-physics.pdf (Letter, portrait, black). Every number is derived here from the constants at the top, each a
datasheet or listing figure or a named assumption; the figures are computed from the same constants. The page style is copied
from custom-build.html. Edit this script, not the outputs."""
from __future__ import annotations

import html
import math
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
DOCS = PAGES.parent
HTML_OUT = PAGES / "lift-physics.html"
MD_OUT = DOCS / "lift-physics.md"
PRINT = PAGES / "print"
BUILD_PAGE = "https://claude.ai/artifact/34eHTqKHJ2gfCkfK2Yb4up"
VOICE_PAGE = "https://claude.ai/artifact/F1GaiD5tUNSf6gDL87SgtG"
JIG_PAGE = "https://claude.ai/artifact/NgbYaHbAoW2Ta996yeXkPF"
APPROVED = "2026-11-10"

# ----------------------------------------------------------------------------- the sheet's values, the listings' and the assumptions
RHO = 1.225                    # kg/m³, air at the desk
G = 9.81
M_VOICE, M_LIFT = 37.5, 53.7   # g, the approved voice build and the lift revision (the build document's ledger)
M_PACK = 6.7                   # g, the 250 mAh pack
D_OLD, D_NEW = 31.0, 40.0      # mm, prop diameters
THRUST_OLD = 68.0              # gf, the vendor's figure for four 615 motors on 31 mm props
I_REF, M_REF = 2.4, 25.0       # A at 25 g on 31 mm props: the ledger's hover model, current as mass^1.5
I_615_FULL, I_720_FULL, I_720_LOW = 1.2, 3.0, 2.2   # A per motor at full throttle, 3.7 V: the 615 from the build document; the 7 × 20 as a range, bench lore
V_PACK, PACK_MAH, C_RATE = 3.7, 250.0, 30.0
USABLE, ELEC = 0.8, 0.95
R_PACK, R_LEADS = 0.040, 0.030  # Ω, a 250 mAh 1S cell's internal resistance and the PH 2.0 pigtail with its plugs: assumptions
V_LDO_IN = 3.55                # V, what the XIAO's 3.3 V regulator needs at its input for a true 3.3 V (0.25 V dropout, est.)
V_BROWN = 2.8                  # V, about where the ESP32-S3's brown-out detector trips at its default setting
CAP = 0.75                     # the firmware's thrust command cap
GATE, FLOOR = 2.0, 1.5
# the ladder
E_BRASS, E_SS = 100e9, 193e9   # Pa
RHO_BRASS, RHO_SS = 8.5, 7.93  # g/cm³
K_BRASS, K_SS = 109.0, 16.0    # W/m·K, thermal conductivity
ROD_D, ROD_LEN = 1.0, 305.0    # mm, the 1 mm rod and the ladder's total length
COLLAR_D, COLLAR_LEN = 1.5, 212.0
RAIL_SPAN = 60.0               # mm, axle to axle
LOAD_ON_RAILS = 15.0           # g, pan plus cabin plus roof: what the rails carry between the axles
# the tilt
LEVER, STROKE_USED, STROKE = 6.0, 6.0, 9.0   # mm
SERVO_SPEED = 0.017            # s per mm at 3.7 V, the listing
SERVO_TORQUE = 80.0            # g·cm, the listing (a pair's rating; taken with salt)
CAM_MASS, CAM_ARM = 0.5, 2.5   # g, mm: the module and its centre of mass ahead of the pin
# the rangers
FOV = 27.0                     # deg, VL53L1X full field
AXLE_X, AXLE_Y, PROP_R, PROP_Z = 25.0, 30.0, 20.0, 16.8
SIDE_X, SIDE_TOP = 11.0, 11.0  # the side boards' outer face and top
REAR_Y, REAR_TOP = -36.0, 11.0
RANGE_HZ, BYTES_PER_READ = 15, 20
IMU_HZ, IMU_BYTES = 500, 14
I2C_KHZ = 400
# masses and stations for the balance, g and mm along the body
STATIONS = [("multiplexer", 1.8, 19.8), ("amplifier", 1.5, 20.25), ("speaker", 2.0, -20.5), ("rear ranger", 1.1, -34.5),
            ("servo and hinge", 2.5, 0.0), ("side rangers", 2.2, 0.0)]

num: dict = {}


def disc_area(d_mm):
    return math.pi * (d_mm / 2000) ** 2


def ideal_hover_power(m_g, d_mm):
    """Momentum theory: four rotors sharing the weight, each P = T^1.5 / sqrt(2 rho A)."""
    t = m_g / 1000 * G / 4
    return 4 * t ** 1.5 / math.sqrt(2 * RHO * disc_area(d_mm))


def hover_current(m_g, d_mm):
    """The ledger's model: 2.4 A at 25 g on 31 mm discs, scaled as mass^1.5 and as the square root of the disc area."""
    return I_REF * (m_g / M_REF) ** 1.5 * math.sqrt(disc_area(D_OLD) / disc_area(d_mm))


def derive():
    n = num
    n["area_ratio"] = disc_area(D_NEW) / disc_area(D_OLD)
    n["p_ideal_voice"] = ideal_hover_power(M_VOICE, D_OLD)
    n["p_ideal_lift"] = ideal_hover_power(M_LIFT, D_NEW)
    n["p_elec_voice"] = hover_current(M_VOICE, D_OLD) * V_PACK
    n["eff_voice"] = n["p_ideal_voice"] / n["p_elec_voice"]
    n["i_hover_lift_model"] = hover_current(M_LIFT, D_NEW)
    n["i_hover_lift_lo"] = 4.5
    n["i_hover_lift"] = (n["i_hover_lift_model"] + n["i_hover_lift_lo"]) / 2
    # thrust from power and disc: T ∝ (P sqrt(2 rho A))^(2/3) at a fixed figure of merit
    p_ratio = I_720_FULL / I_615_FULL
    n["thrust_lift_hi"] = THRUST_OLD * (p_ratio * math.sqrt(n["area_ratio"])) ** (2 / 3)
    n["thrust_lift_lo"] = THRUST_OLD * ((I_720_LOW / I_615_FULL) * math.sqrt(n["area_ratio"])) ** (2 / 3)
    n["tw_lo"] = n["thrust_lift_lo"] / M_LIFT
    n["tw_hi"] = n["thrust_lift_hi"] / M_LIFT
    n["tw_voice"] = THRUST_OLD / M_VOICE
    n["hover_cmd_lo"] = math.sqrt(1 / n["tw_hi"]) * 100
    n["hover_cmd_hi"] = math.sqrt(1 / n["tw_lo"]) * 100
    n["i_full"] = 4 * I_720_FULL
    n["i_cap"] = n["i_full"] * CAP ** 2
    n["i_pack_max"] = PACK_MAH / 1000 * C_RATE
    n["i_hover_duty"] = {c: n["i_full"] * (c / 100) ** 2 for c in (60, 62, 65, 67, 70, 75, 100)}
    r = R_PACK + R_LEADS
    n["v_at"] = {label: V_PACK - i * r for label, i in (("hover", n["i_hover_lift"]), ("cap", n["i_cap"]), ("full", n["i_full"]))}
    n["c_rate_hover"] = n["i_hover_lift"] / (PACK_MAH / 1000)
    n["t_fly"] = USABLE * PACK_MAH / 1000 / n["i_hover_lift"] * 60 * ELEC
    n["t_fly_lo"] = USABLE * PACK_MAH / 1000 / n["i_hover_lift_model"] * 60 * ELEC
    n["t_fly_hi"] = USABLE * PACK_MAH / 1000 / n["i_hover_lift_lo"] * 60 * ELEC
    n["m_gate_lo"], n["m_gate_hi"] = n["thrust_lift_lo"] / GATE, n["thrust_lift_hi"] / GATE
    n["m_floor_lo"] = n["thrust_lift_lo"] / FLOOR
    # the ladder
    area = math.pi * (ROD_D / 2) ** 2
    n["m_rod_brass"] = (ROD_LEN * area + COLLAR_LEN * math.pi * (COLLAR_D / 2) ** 2) * RHO_BRASS / 1000
    n["m_rod_ss"] = (ROD_LEN * area + COLLAR_LEN * math.pi * (COLLAR_D / 2) ** 2) * RHO_SS / 1000
    inertia = math.pi * ROD_D ** 4 / 64                          # mm⁴
    f = LOAD_ON_RAILS / 1000 * G / 2                              # N per rail
    n["defl_brass"] = f * RAIL_SPAN ** 3 / (48 * E_BRASS / 1e6 * inertia)   # mm (E in N/mm²)
    n["defl_ss"] = f * RAIL_SPAN ** 3 / (48 * E_SS / 1e6 * inertia)
    n["defl_brass_punch"] = n["defl_brass"] * 2.5
    n["k_ratio"] = K_BRASS / K_SS
    # the tilt
    n["tilt_deg"] = math.degrees(math.asin(STROKE_USED / 2 / LEVER))
    n["tilt_time"] = STROKE_USED * SERVO_SPEED
    n["cam_torque_gcm"] = CAM_MASS * CAM_ARM / 10
    n["torque_margin"] = SERVO_TORQUE / n["cam_torque_gcm"]
    # the rangers
    half = math.radians(FOV / 2)
    n["side_halfwidth_at_rim"] = (AXLE_X + PROP_R - SIDE_X) * math.tan(half)
    n["disc_inner_y"] = AXLE_Y - PROP_R
    n["side_clear_z"] = PROP_Z - SIDE_TOP
    n["rear_halfwidth_at_disc"] = (abs(REAR_Y) - (AXLE_Y + PROP_R)) * math.tan(half) if abs(REAR_Y) > AXLE_Y + PROP_R else 0.0
    n["rear_halfwidth_at_rim"] = (AXLE_Y + PROP_R - abs(REAR_Y)) * math.tan(half)
    n["bus_rangers_kbps"] = 5 * RANGE_HZ * BYTES_PER_READ * 8 / 1000
    n["bus_imu_kbps"] = IMU_HZ * IMU_BYTES * 8 / 1000
    n["bus_share"] = (n["bus_rangers_kbps"] + n["bus_imu_kbps"]) / (I2C_KHZ * 0.8) * 100
    # balance
    moment = sum(m * y for _, m, y in STATIONS)
    n["cg_shift"] = moment / M_LIFT
    n["rear_share"] = 0.5 - n["cg_shift"] / (2 * AXLE_Y)
    n["added"] = M_LIFT - M_VOICE


derive()


# ----------------------------------------------------------------------------- figure helpers (the voice page's)
def esc(s):
    return html.escape(str(s), quote=False)


FIG_CSS = ("<style>"
           ".ax{fill:none;stroke:var(--ink);stroke-width:1.4;stroke-linecap:round}"
           ".grid{fill:none;stroke:var(--line);stroke-width:1}"
           ".s1{fill:none;stroke:var(--c1);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}"
           ".s2{fill:none;stroke:var(--c2);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:7 5}"
           ".ref{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:4 4}"
           ".band{fill:var(--steel-soft);stroke:none}"
           ".bad{fill:var(--no-soft);stroke:none}"
           ".dot{fill:var(--ink);stroke:var(--paper);stroke-width:2}"
           ".dot1{fill:var(--c1);stroke:var(--paper);stroke-width:2}"
           ".dot2{fill:var(--c2);stroke:var(--paper);stroke-width:2}"
           ".hol{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
           ".rod{fill:none;stroke:var(--brass);stroke-width:2.6;stroke-linecap:round}"
           ".rodt{fill:none;stroke:var(--brass);stroke-width:1.6;stroke-linecap:round}"
           ".disc{fill:var(--metal-soft);fill-opacity:.35;stroke:var(--ink-2);stroke-width:1;stroke-dasharray:4 4}"
           ".cone{fill:var(--c1-soft);fill-opacity:.7;stroke:var(--c1);stroke-width:1}"
           ".board{fill:var(--matte);stroke:var(--matte-edge);stroke-width:1.2}"
           ".pan{fill:var(--skin);stroke:var(--skin-edge);stroke-width:1.2}"
           ".cab{fill:var(--matte);stroke:var(--matte-edge);stroke-width:1.2}"
           ".h{font:700 13px 'Barlow Semi Condensed','Arial Narrow',Arial,sans-serif;fill:var(--ink)}"
           ".t{font:400 12px 'Source Sans 3','Segoe UI',system-ui,sans-serif;fill:var(--ink)}"
           ".fn{font:400 11.5px 'Source Sans 3','Segoe UI',system-ui,sans-serif;fill:var(--ink-2)}"
           ".num{font:600 12px 'Source Code Pro',ui-monospace,monospace;fill:var(--ink)}"
           "</style>")


def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{FIG_CSS}{body}</svg>'


def T(x, y, s, cls="fn", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def line(x0, y0, x1, y1, cls="ax"):
    return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="{cls}"/>'


def poly(pts, cls):
    return '<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" class="{cls}"/>'


def polygon(pts, cls):
    return '<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" class="{cls}"/>'


def rect(x0, y0, x1, y1, cls, rx=0):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="{rx}" class="{cls}"/>'


def circ(x, y, r, cls):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="{cls}"/>'


def legend(x, y, items):
    o = []
    for cls, lab in items:
        if cls in ("band", "bad", "cone", "disc"):
            o.append(rect(x, y - 7, x + 26, y + 3, cls))
        else:
            o.append(line(x, y - 1, x + 26, y - 1, cls))
        o.append(T(x + 32, y + 3, lab, "t"))
        x += 32 + 6.6 * len(lab) + 22
    return "".join(o)


# ----------------------------------------------------------------------------- figure 1: hover current against mass, two disc sizes
def fig_hover():
    W, H = 860, 380
    x0, x1, y0, y1 = 70, 820, 40, 300
    mlo, mhi = 25.0, 60.0

    def X(m):
        return x0 + (m - mlo) / (mhi - mlo) * (x1 - x0)

    def Y(i):
        return y1 - i / 9 * (y1 - y0)

    o = [T(x0, 22, "Hover current against flying mass on 31 mm and on 40 mm discs, from the ledger's model", "h")]
    for i in range(0, 10, 1):
        o.append(line(x0, Y(i), x1, Y(i), "grid"))
        if i % 3 == 0 or i == 7.5:
            o.append(T(x0 - 8, Y(i) + 4, f"{i} A", "num", "end"))
    o.append(line(x0, y1, x1, y1))
    for m in range(25, 61, 5):
        o.append(line(X(m), y1, X(m), y1 + 5))
        o.append(T(X(m), y1 + 18, f"{m} g", "fn", "middle"))
    o.append(line(x0, Y(num["i_pack_max"]), x1, Y(num["i_pack_max"]), "ref"))
    o.append(T(x1 - 4, Y(num["i_pack_max"]) - 6, f"the pack's {C_RATE:.0f} C: {num['i_pack_max']:.1f} A continuous", "fn", "end"))
    ms = [mlo + (mhi - mlo) * k / 100 for k in range(101)]
    o.append(poly([(X(m), Y(hover_current(m, D_OLD))) for m in ms], "s2"))
    o.append(poly([(X(m), Y(hover_current(m, D_NEW))) for m in ms], "s1"))
    o.append(circ(X(M_VOICE), Y(hover_current(M_VOICE, D_OLD)), 5.5, "dot2"))
    o.append(T(X(M_VOICE) + 10, Y(hover_current(M_VOICE, D_OLD)) - 8, f"{M_VOICE} g on 31 mm: {hover_current(M_VOICE, D_OLD):.1f} A, the approved build", "t"))
    o.append(circ(X(M_LIFT), Y(num["i_hover_lift_model"]), 5.5, "dot1"))
    o.append(T(X(M_LIFT) - 10, Y(num["i_hover_lift_model"]) - 10, f"{M_LIFT} g on 40 mm: {num['i_hover_lift_model']:.1f} A by the model", "t", "end"))
    o.append(circ(X(M_LIFT), Y(num["i_hover_lift_lo"]), 5.5, "hol"))
    o.append(T(X(M_LIFT) - 10, Y(num["i_hover_lift_lo"]) + 18, f"{num['i_hover_lift_lo']:.1f} A if the bigger motors are as efficient as whoops suggest", "t", "end"))
    o.append(legend(x0, y1 + 44, (("s2", "31 mm discs, 615 motors"), ("s1", "40 mm discs, 7 × 20 motors"))))
    return svg(W, H, "".join(o), "Hover current against flying mass from 25 to 60 g for 31 mm and 40 mm propeller discs, with the pack's continuous limit and the two builds marked")


# ----------------------------------------------------------------------------- figure 2: what the pack can feed
def fig_pack():
    W, H = 860, 380
    panels = ((60, 410, "Current from the pack against the thrust command", 0.0, 14.0, "A"),
              (490, 820, "Pack voltage at the controller, same command", 2.4, 4.0, "V"))
    o = []
    r = R_PACK + R_LEADS
    for (x0, x1, title, lo, hi, unit) in panels:
        y0, y1 = 50, 290

        def X(c, x0=x0, x1=x1):
            return x0 + c / 100 * (x1 - x0)

        def Y(v, lo=lo, hi=hi):
            return y1 - (v - lo) / (hi - lo) * (y1 - y0)

        o.append(T(x0, 22, title, "h"))
        steps = 7 if unit == "A" else 8
        for k in range(steps + 1):
            v = lo + (hi - lo) * k / steps
            o.append(line(x0, Y(v), x1, Y(v), "grid"))
            o.append(T(x0 - 8, Y(v) + 4, f"{v:.0f}" if unit == "A" else f"{v:.1f}", "num", "end"))
        o.append(line(x0, y1, x1, y1))
        for c in range(0, 101, 25):
            o.append(line(X(c), y1, X(c), y1 + 5))
            o.append(T(X(c), y1 + 18, f"{c} %", "fn", "middle"))
        # the hover band and the cap
        o.append(rect(X(num["hover_cmd_lo"]), y0, X(num["hover_cmd_hi"]), y1, "band"))
        o.append(T((X(num["hover_cmd_lo"]) + X(num["hover_cmd_hi"])) / 2, y0 + 14, "hover", "fn", "middle"))
        o.append(rect(X(CAP * 100), y0, x1, y1, "bad"))
        o.append(line(X(CAP * 100), y0, X(CAP * 100), y1, "ref"))
        o.append(T(X(CAP * 100) + 6, y0 + 14, f"capped at {CAP * 100:.0f} %", "fn"))
        cs = [k for k in range(0, 101)]
        if unit == "A":
            o.append(line(x0, Y(num["i_pack_max"]), x1, Y(num["i_pack_max"]), "ref"))
            o.append(T(x0 + 6, Y(num["i_pack_max"]) - 6, f"{num['i_pack_max']:.1f} A: the pack's {C_RATE:.0f} C", "fn"))
            o.append(poly([(X(c), Y(num["i_full"] * (c / 100) ** 2)) for c in cs], "s1"))
            for c, lab, dy in ((CAP * 100, f"{num['i_cap']:.1f} A at the cap", 20), (100, f"{num['i_full']:.0f} A at full", 16)):
                i = num["i_full"] * (c / 100) ** 2
                o.append(circ(X(c), Y(i), 5, "dot1"))
                o.append(T(X(c) - 10, Y(i) + dy, lab, "t", "end"))
        else:
            o.append(line(x0, Y(V_LDO_IN), x1, Y(V_LDO_IN), "ref"))
            o.append(T(x0 + 6, Y(V_LDO_IN) - 6, f"{V_LDO_IN:.2f} V: a true 3.3 V rail above this", "fn"))
            o.append(line(x0, Y(V_BROWN), x1, Y(V_BROWN), "ref"))
            o.append(T(x0 + 6, Y(V_BROWN) - 6, f"{V_BROWN:.1f} V: the brown-out detector", "fn"))
            o.append(poly([(X(c), Y(V_PACK - num["i_full"] * (c / 100) ** 2 * r)) for c in cs], "s1"))
            for c, lab, dy in ((CAP * 100, f"{num['v_at']['cap']:.2f} V at the cap", -10), (100, f"{num['v_at']['full']:.2f} V at full", 16)):
                v = V_PACK - num["i_full"] * (c / 100) ** 2 * r
                o.append(circ(X(c), Y(v), 5, "dot1"))
                o.append(T(X(c) - 10, Y(v) + dy, lab, "t", "end"))
    return svg(W, H, "".join(o), "Two panels against the thrust command: the current four 7 by 20 motors draw, rising as the square of the command past the pack's limit, and the pack voltage at the controller falling toward the regulator's need and the brown-out line; the hover band and the 75 percent cap are marked")


# ----------------------------------------------------------------------------- figure 3: the rangers' fields and the discs, top view
def fig_fields():
    W, H = 860, 540
    s = 3.2
    ox, oy = 430, 225

    def P(x, y):
        return ox + s * x, oy - s * y

    o = [T(20, 22, "Top view, nose up: the four discs and the three low rangers' 27° fields, which never meet a disc", "h")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = P(sx * AXLE_X, sy * AXLE_Y)
            o.append(circ(cx, cy, PROP_R * s, "disc"))
    half = math.radians(FOV / 2)
    reach = 45.0
    for sx in (-1, 1):
        a = (SIDE_X * sx, 0.0)
        tip = (sx * (SIDE_X + reach), 0.0)
        w = reach * math.tan(half)
        o.append(polygon([P(*a), P(tip[0], tip[1] + w), P(tip[0], tip[1] - w)], "cone"))
    a = (0.0, REAR_Y)
    w = reach * math.tan(half)
    o.append(polygon([P(*a), P(w, REAR_Y - reach), P(-w, REAR_Y - reach)], "cone"))
    # frame and body
    for x in (-7, 7):
        o.append(line(*P(x, 33), *P(x, -33), "rod"))
    for y in (-AXLE_Y, AXLE_Y):
        o.append(line(*P(-AXLE_X, y), *P(AXLE_X, y), "rod"))
    o.append(line(*P(-15.5, 33), *P(15.5, 33), "rod"))
    o.append(line(*P(-7, -33), *P(7, -33), "rod"))
    o.append(rect(*P(-5.5, 27), *P(5.5, -27), "pan"))
    o.append(rect(*P(-8.75, 10.5), *P(8.75, -10.5), "cab"))
    for sx in (-1, 1):
        o.append(rect(*P(sx * 8, 12.5), *P(sx * SIDE_X, -12.5), "board"))
    o.append(rect(*P(-12.5, -33), *P(12.5, REAR_Y), "board"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = P(sx * AXLE_X, sy * AXLE_Y)
            o.append(circ(cx, cy, 3.5 * s, "hol"))
    # dimensions and notes
    x_rim = AXLE_X + PROP_R
    hw = num["side_halfwidth_at_rim"]
    o.append(line(*P(x_rim, hw), *P(x_rim, -hw), "ref"))
    o.append(T(P(x_rim, -hw)[0] - 30, P(x_rim, -hw)[1] + 22, f"±{hw:.1f} mm wide at the discs' outer rim, x = {x_rim:.0f},", "fn", "middle"))
    o.append(T(P(x_rim, -hw)[0] - 30, P(x_rim, -hw)[1] + 36, f"where the only disc is the rim point at y = ±{AXLE_Y:.0f}", "fn", "middle"))
    o.append(line(*P(-AXLE_X, AXLE_Y - PROP_R), 250, P(0, AXLE_Y - PROP_R)[1], "ref"))
    o.append(T(20, P(0, AXLE_Y - PROP_R)[1] - 6, f"the discs begin {num['disc_inner_y']:.0f} mm fore and aft of the centre", "fn"))
    o.append(T(P(0, REAR_Y - reach - 4)[0], P(0, REAR_Y - reach - 4)[1] + 10, f"rear cone: ±{num['rear_halfwidth_at_rim']:.1f} mm wide where the discs end (y = −{AXLE_Y + PROP_R:.0f}); the discs' inner edges are at ±{AXLE_X - PROP_R:.0f}", "fn", "middle"))
    o.append(T(20, 60, f"the ranger boards top out at {SIDE_TOP:.0f} mm, {num['side_clear_z']:.1f} mm under the prop plane:", "fn"))
    o.append(T(20, 74, "the discs may pass over them; the cones stay between the discs", "fn"))
    o.append(legend(20, 522, (("disc", "40 mm prop discs"), ("cone", "ranger fields, 27°, drawn to 45 mm"), ("board", "ranger boards"))))
    return svg(W, H, "".join(o), "Top view of the lift revision with the four 40 mm prop discs, the brass ladder, the two side ranger boards low beside the rails and the rear board behind the tail bar, each with its 27 degree field drawn to 45 mm, none touching a disc")


# ----------------------------------------------------------------------------- figure 4: the tilt mechanism
def fig_tilt():
    W, H = 860, 330
    s = 9.0
    ox, oy = 300, 200          # the hinge pin on the page

    def P(y, z):
        return ox + s * y, oy - s * z

    o = [T(20, 22, "Side view of the cabin's front, 9 px per mm: the servo on the roof, its link, the 6 mm lever and the camera on its pin", "h")]
    # cabin front face and roof
    o.append(rect(*P(-24, 3.6), *P(0, -11.4), "cab"))
    o.append(T(*P(-12, -4), "cabin", "t", "middle"))
    o.append(rect(*P(-21.4, 9.6), *P(0, 3.6), "board"))
    o.append(T(*P(-10.7, 6.2), "servo, 21.4 × 6 mm", "t", "middle"))
    # the pin sits 3 mm ahead of the face; the arm leaves the servo's front at the lever top's height
    PIN_Y = 3.0
    for ang, cls, cam_cls in ((-30, "rodt", "disc"), (30, "rodt", "disc"), (0, "rod", "board")):
        a = math.radians(ang)
        top = (PIN_Y + LEVER * math.sin(a), LEVER * math.cos(a))
        o.append(line(*P(PIN_Y, 0), *P(*top), cls))                       # the lever
        o.append(line(*P(0, LEVER), *P(*top), cls))                        # the servo's arm and link
        pts = []
        for (u, v) in ((-2.5, 4.25), (2.5, 4.25), (2.5, -4.25), (-2.5, -4.25)):
            pts.append(P(PIN_Y + u * math.cos(a) - v * math.sin(a), u * math.sin(a) + v * math.cos(a)))
        o.append(polygon(pts, cam_cls))
    o.append(circ(*P(PIN_Y, 0), 4, "hol"))
    o.append(T(P(PIN_Y + 7, -0.5)[0], P(PIN_Y + 7, -0.5)[1] + 4, "hinge pin, 1 mm brass, in two tabs on the front face", "fn"))
    o.append(T(P(PIN_Y + 7, LEVER + 0.5)[0], P(PIN_Y + 7, LEVER + 0.5)[1], f"the arm moves the lever's top ±{STROKE_USED / 2:.0f} mm: ±{num['tilt_deg']:.0f}°", "fn"))
    o.append(T(P(PIN_Y + 7, -6)[0], P(PIN_Y + 7, -6)[1], "camera module, 8.5 × 5 mm, lens forward:", "fn"))
    o.append(T(P(PIN_Y + 7, -7.8)[0], P(PIN_Y + 7, -7.8)[1], "level (solid), 30° up and 30° down (faint)", "fn"))
    o.append(T(20, 312, f"The arm travels {SERVO_SPEED * 1000:.0f} ms per millimetre, so {STROKE_USED:.0f} mm takes {num['tilt_time'] * 1000:.0f} ms; the module's weight on the pin is {num['cam_torque_gcm']:.2f} g·cm against the servo's {SERVO_TORQUE:.0f}.", "fn"))
    return svg(W, H, "".join(o), "Side view schematic of the camera tilt: the servo lying on the cabin roof, a link to a 6 mm lever on the hinge pin at the cabin's front, and the camera module shown level and at 30 degrees up and down")


FIGS = {"hover": fig_hover, "pack": fig_pack, "fields": fig_fields, "tilt": fig_tilt}


# ----------------------------------------------------------------------------- the text
def chapters():
    n = num
    return [
        ("The whole thing in one breath", [
            f"Three things were asked of the drone at once: a voice, a camera that nods, and eyes all round. Together they weigh {n['added']:.1f} g more than the {M_VOICE} g the approved build lifted at {n['tw_voice']:.2f} to one, and {M_LIFT:.1f} g on 68 gf would hover at 80 % throttle with nothing in reserve. The cheapest lift in the world is the whoop world's own next size: a motor a size larger on a propeller a size larger, nothing else electrical. Four 7 × 20 mm motors on 40 mm discs give, by the physics below, {n['thrust_lift_lo']:.0f} to {n['thrust_lift_hi']:.0f} gf, {n['tw_lo']:.1f} to {n['tw_hi']:.1f} to one, for about 7 g of motor, prop and longer axle.",
            "The rest of this page is why each piece of the revision is shaped the way it is: why the disc matters as much as the motor, what a 250 mAh pack can and cannot feed, why the ladder went to brass and what that costs in stiffness, how a 6 mm lever turns 6 mm of travel into 30° of nod, why the rangers sit low and look sideways between the discs, and why five identical sensors need one small switch and no pins.",
        ]),
        ("Lift is bought with disc, not just with motor", [
            f"A hovering rotor throws air down, and the power it needs to hold a thrust T is T to the power 1.5 over the square root of twice the air density times the disc area. Two things follow. Doubling the mass costs {2 ** 1.5:.1f} times the power, which is why every gram shows in the flight time. And at a fixed weight, a bigger disc lifts it more cheaply: the 40 mm disc has {n['area_ratio']:.2f} times the area of the 31 mm one, so the ideal power falls by the square root of that, {1 / math.sqrt(n['area_ratio']) * 100:.0f} %. Momentum theory gives {n['p_ideal_lift']:.1f} W of ideal power for {M_LIFT:.1f} g on four 40 mm discs; the approved build's {M_VOICE} g on 31 mm discs needs {n['p_ideal_voice']:.1f} W ideal and about {n['p_elec_voice']:.0f} W electrical, so the little brushed motors and their propellers turn about {n['eff_voice'] * 100:.0f} % of the pack's power into lift. That is normal for this size.",
            f"The thrust a motor can make follows from the power it can put in: at a fixed efficiency, thrust goes as the two-thirds power of power times the square root of disc area. A 7 × 20 motor takes about {I_720_FULL:.0f} A at full throttle against the 615's {I_615_FULL:.1f}, which with the bigger disc multiplies the thrust by {(I_720_FULL / I_615_FULL * math.sqrt(n['area_ratio'])) ** (2 / 3):.1f}: {n['thrust_lift_hi']:.0f} gf from the 68. Taking the motor at {I_720_LOW:.1f} A instead gives {n['thrust_lift_lo']:.0f}. No vendor publishes a thrust figure for these motors, so the build document carries 120 to 140 gf as the working range, this page {n['thrust_lift_lo']:.0f} to {n['thrust_lift_hi']:.0f} from the physics, and the first hover reads the truth, as it always did; the gate stays 2.0 and the floor 1.5.",
            ("fig", "hover", f"Hover current against flying mass on the two disc sizes, from the ledger's model: 2.4 A at 25 g on 31 mm discs, scaled as mass to the 1.5 and as the square root of disc area. The dashed line is the pack's {C_RATE:.0f} C. The {M_LIFT:.1f} g lift revision sits at {n['i_hover_lift_model']:.1f} A by the model and nearer {n['i_hover_lift_lo']:.1f} if the bigger motors are as efficient as whoop pilots report; the page uses {n['i_hover_lift']:.0f} A."),
            f"The model is honest about what it knows: it is the ledger's 2.4 A at 25 g carried to the new mass and the new disc. It does not know that a 7 × 20 motor wastes less of its current in brush and winding losses than a 615, which the whoop world's flight times say it does. So the hover current for {M_LIFT:.1f} g is {n['i_hover_lift_lo']:.1f} to {n['i_hover_lift_model']:.1f} A, about {n['i_hover_lift']:.0f}; the build document says the same. At {n['i_hover_lift']:.0f} A the pack is at {n['c_rate_hover']:.0f} C, and 80 % of {PACK_MAH:.0f} mAh less 5 % for the controller and camera is {n['t_fly']:.1f} minutes in the air, {n['t_fly_lo']:.1f} to {n['t_fly_hi']:.1f} across the range.",
        ]),
        ("What a 250 mAh pack can feed, and why the firmware caps the throttle", [
            f"A brushed motor on a propeller draws current about as the square of its throttle command: the speed follows the voltage, the load follows the speed squared. Four 7 × 20 motors at full throttle take about {n['i_full']:.0f} A. The pack is rated {C_RATE:.0f} C, {n['i_pack_max']:.1f} A continuous, and a small cell behind a PH 2.0 pigtail has about {(R_PACK + R_LEADS) * 1000:.0f} mΩ in its way, so {n['i_full']:.0f} A would pull its terminals down to {n['v_at']['full']:.2f} V. The controller's 3.3 V regulator wants about {V_LDO_IN:.2f} V at its input for a true 3.3 V, and the chip's brown-out detector trips near {V_BROWN:.1f} V: a full-throttle punch on this pack would reset the flight controller in the air.",
            f"So the firmware caps the thrust command at {CAP * 100:.0f} %. At the cap the motors draw {n['i_cap']:.1f} A, inside the pack's {n['i_pack_max']:.1f}, and the terminals sit at {n['v_at']['cap']:.2f} V; the hover command for {n['tw_lo']:.1f} to {n['tw_hi']:.1f} to one is {n['hover_cmd_lo']:.0f} to {n['hover_cmd_hi']:.0f} %, well under the cap, with the full margin between still there for a gust. The thrust gate is read by the hover command, not by a punch, which is how D02 was written in the first place.",
            ("fig", "pack", f"Left: current from the pack against the thrust command, rising as the command squared, past the pack's {n['i_pack_max']:.1f} A at about {math.sqrt(n['i_pack_max'] / n['i_full']) * 100:.0f} %; the hover band and the {CAP * 100:.0f} % cap are shaded. Right: the pack voltage the controller sees, falling with that current through {(R_PACK + R_LEADS) * 1000:.0f} mΩ, against the regulator's need and the brown-out line. Resistances are assumptions, named at the top of the script."),
            f"The way to more margin is a bigger pack, not a bigger C rating: a 450 mAh pack has twice the plates, half the resistance and twice the flight time for about 5 g, but it is 17 mm wide and the pan between the rails is 14. That is a later revision, not this one. For now the 220 µF across the switch cells and the 47 to 100 µF at the amplifier hold the rails through each pulse, and the cap keeps the controller awake.",
        ]),
        ("A brass ladder, and what it costs in stiffness", [
            f"The builder asked that the drone match the desk family's brass, and nothing is painted, so the only brass a whoop can wear is its frame. The ladder is {ROD_LEN:.0f} mm of 1.0 mm brass rod and {COLLAR_LEN:.0f} mm of 1.5 mm for the four collars: {n['m_rod_brass']:.1f} g against {n['m_rod_ss']:.1f} in stainless, {RHO_BRASS / RHO_SS * 100 - 100:.0f} % more, because brass is {RHO_BRASS:.1f} g/cm³ to stainless steel's {RHO_SS:.2f}. The rod is already in stock, so the frame costs nothing to buy.",
            f"Brass is about half as stiff: Young's modulus {E_BRASS / 1e9:.0f} GPa against {E_SS / 1e9:.0f}. A rail is a 1 mm beam spanning {RAIL_SPAN:.0f} mm between the axles and carrying half of the {LOAD_ON_RAILS:.0f} g of pan, cabin and roof; with the cubic law of beam bending it sags {n['defl_brass'] * 1000:.0f} µm in brass and {n['defl_ss'] * 1000:.0f} in stainless, and {n['defl_brass_punch'] * 1000:.0f} µm in brass at the 2.5 g of a hard punch. A quarter of a millimetre on a frame that flexes its rubber props more than that is nothing, and in any case the strapped pack turns the two rails into the flanges of a 6 mm-deep beam, many times stiffer than the rods alone. Stiffness was never the reason for stainless; its hardness and its indifference to tarnish were.",
            f"Soldering is where brass wins. Copper alloys carry a thin oxide that rosin flux reduces, so a brass joint wets with ordinary tin and leaves a residue that needs only a wipe of alcohol. Stainless hides under a chromium oxide skin that only an acid flux breaks, and that flux must be washed off or it keeps eating. Brass also conducts heat {n['k_ratio']:.0f} times better than stainless, which means a joint drains the iron faster: a larger tip and a moment longer on the rod, and the collar former left in while the collar is soldered so it does not close. Brass tarnishes toward brown over months, which is in the family's palette and is left alone.",
        ]),
        ("A 6 mm lever: how 6 mm of travel becomes 30° of nod", [
            f"A quadcopter cannot hold a tilted hover, so the camera is hinged and the drone's body stays level. The module hangs on a 1 mm brass pin through two tabs on the cabin's front face, with a {LEVER:.0f} mm lever standing up from the pin. The servo lies on the roof with its arm forward and a 1 mm brass link to the lever's top. A linear servo moves its arm in a straight line, and a lever's top moved sideways by s swings the lever through the angle whose sine is s over the lever's length: {STROKE_USED / 2:.0f} mm on {LEVER:.0f} gives {n['tilt_deg']:.0f}° each way, using {STROKE_USED:.0f} of the arm's {STROKE:.0f} mm.",
            ("fig", "tilt", f"The mechanism from the side at 9 px per mm: the servo on the roof, its link to the {LEVER:.0f} mm lever, and the camera module on its pin shown level and at {n['tilt_deg']:.0f}° up and down."),
            f"The load is almost nothing: the module weighs {CAM_MASS:.1f} g with its centre about {CAM_ARM:.1f} mm ahead of the pin, {n['cam_torque_gcm']:.2f} g·cm, against the servo's rated {SERVO_TORQUE:.0f}; the flex cable's stiffness is the real resistance, and a servo made to move a model aeroplane's elevator in flight does not notice it. The arm moves {SERVO_SPEED * 1000:.0f} ms per millimetre at 3.7 V, so a nod from one stop to the other takes about {n['tilt_time'] * 1000:.0f} ms. The signal is the ordinary 50 Hz pulse of 1 to 2 ms, which the controller makes with its LED timer on the pin the multiplexer freed; the servo's electronics run from the pack and read 3.3 V as high.",
        ]),
        ("Eyes all round, low: why the rangers sit where they do", [
            f"A single-zone ranger sees a cone {FOV:.0f}° wide. Anything inside that cone that is nearer than the wall becomes the reading, and a propeller blade passing through it would be read as a wall 4 cm away. So the side rangers sit low, outside the rails at the cabin's foot, where their boards top out {SIDE_TOP:.0f} mm above the rails, {n['side_clear_z']:.1f} mm under the prop plane: the discs may pass over them. Their cones look straight out to the sides from the middle of the body, and the discs begin {n['disc_inner_y']:.0f} mm fore and aft of that line. At the discs' outer rim, {AXLE_X + PROP_R:.0f} mm out, a cone is only ±{n['side_halfwidth_at_rim']:.1f} mm wide, and the only part of a disc that far out is its rim at y = ±{AXLE_Y:.0f}. The cones and the discs never share a point.",
            ("fig", "fields", "The four discs, the three low ranger boards and their cones drawn to 45 mm, from above. The side cones pass between the front and rear discs; the rear cone leaves from behind the tail bar with nothing ahead of it."),
            f"The rear ranger moved from the cabin's back face to behind the tail bar for the same reason: on the back face its 25 mm board would have reached under the rear discs with its top above the prop plane, and it would have covered the controller's USB port. Behind the tail bar, at {abs(REAR_Y):.0f} mm, it looks back with nothing in its field at all, {n['side_clear_z']:.1f} mm under the discs, and the USB port stays free. The boards hang on two 1 mm brass posts or a brass tab and B-7000, and each board's shutdown pin is tied to its own supply so that none depends on a pull-up that may or may not be fitted.",
        ]),
        ("Five sensors with one address, and one small switch", [
            f"Every VL53 ranger wakes at the same I²C address. The usual way to put several on one bus is to hold all but one in reset at boot and give each a new address in turn, which costs a wire per sensor, and the controller has none left. The multiplexer is the other way: a chip with eight pairs of analog switches, one per channel, that connects exactly one pair to the bus when told to by a single byte written to its own address. Five rangers on five channels never see each other, so all five keep their default address and nothing is re-addressed. The motion sensor stays on the bus itself, at its own address, outside the switch.",
            f"The bus has room. Five rangers read {RANGE_HZ} times a second at about {BYTES_PER_READ} bytes a read are {n['bus_rangers_kbps']:.0f} kbit/s, the motion sensor at {IMU_HZ} Hz another {n['bus_imu_kbps']:.0f}, together about {n['bus_share']:.0f} % of a {I2C_KHZ} kHz bus with its overheads. The switch adds a few nanoseconds and a few picofarads to each channel, and because only one channel is on at a time the bus never carries more than one ranger's capacitance. The board lies across the hood, chip down, 8 mm under the prop plane; it is the one new part that shows, and it is black.",
        ]),
        ("Where the weight went, and the balance", [
            f"The revision adds {n['added']:.1f} g to the voice build: motors {6.0:.1f}, the brass ladder {0.8:.1f} over stainless, props {0.8:.1f} (the grey polycarbonate HQ props weigh 0.5 g each, more than the 1636s first counted), multiplexer {1.8:.1f}, three rangers and their posts {3.3:.1f}, servo and hinge {2.5:.1f}, wiring {1.0:.1f}. The motors and props sit at the four corners and cancel; the multiplexer rides ahead of the centre and the speaker and rear ranger behind it, so the centre of gravity moves {abs(n['cg_shift']):.2f} mm toward the tail and the rear motors carry {n['rear_share'] * 100:.1f} % of the hover instead of 50. The controller trims that without being told.",
            f"At {M_LIFT:.1f} g the margins are these: the 2.0 gate is met up to {n['m_gate_lo']:.0f} to {n['m_gate_hi']:.0f} g depending on where the thrust really lands, and the 1.5 floor up to {n['m_floor_lo']:.0f} g at the low end. If the first hover reads under 2.0, the build document names the lighter paths; if it reads over 2.4, the margin is a 450 mAh pack and twice the time in the air.",
        ]),
    ]


def numbers():
    n = num
    return [
        (f"{n['area_ratio']:.2f}", f"the disc area ratio: (40/31)²; ideal hover power falls by its square root, {1 / math.sqrt(n['area_ratio']) * 100:.0f} %"),
        (f"{n['p_ideal_lift']:.1f} W", f"ideal hover power for {M_LIFT:.1f} g on four 40 mm discs: 4 × T^1.5 / √(2ρA), T = weight/4"),
        (f"{n['eff_voice'] * 100:.0f} %", f"the approved build's ideal power over its electrical power: {n['p_ideal_voice']:.1f} W over {n['p_elec_voice']:.0f}"),
        (f"{n['thrust_lift_lo']:.0f} to {n['thrust_lift_hi']:.0f} gf", f"thrust from power scaling: 68 gf × (I₇₂₀/I₆₁₅ × √area ratio)^(2/3), with the 7 × 20 at {I_720_LOW:.1f} to {I_720_FULL:.0f} A against the 615's 1.2"),
        (f"{n['tw_lo']:.1f} to {n['tw_hi']:.1f}", f"thrust to weight at {M_LIFT:.1f} g; hover command √(1/TW) = {n['hover_cmd_lo']:.0f} to {n['hover_cmd_hi']:.0f} %"),
        (f"{n['i_hover_lift_lo']:.1f} to {n['i_hover_lift_model']:.1f} A", f"hover current: the ledger's model gives {n['i_hover_lift_model']:.1f}, whoop experience nearer {n['i_hover_lift_lo']:.1f}; {n['c_rate_hover']:.0f} C at {n['i_hover_lift']:.0f} A"),
        (f"{n['t_fly']:.1f} min", f"in the air: 80 % of {PACK_MAH:.0f} mAh over {n['i_hover_lift']:.0f} A, less 5 %; {n['t_fly_lo']:.1f} to {n['t_fly_hi']:.1f} across the range"),
        (f"{n['i_full']:.0f} A, {n['i_cap']:.1f} A", f"four motors at full throttle, and at the {CAP * 100:.0f} % cap (current as command squared); the pack gives {n['i_pack_max']:.1f}"),
        (f"{n['v_at']['full']:.2f} V, {n['v_at']['cap']:.2f} V", f"pack terminals at full and at the cap: 3.7 V less the current through {(R_PACK + R_LEADS) * 1000:.0f} mΩ; the regulator wants {V_LDO_IN:.2f}, brown-out near {V_BROWN:.1f}"),
        (f"{n['m_rod_brass']:.1f} g", f"the brass ladder: {ROD_LEN:.0f} mm of 1.0 mm and {COLLAR_LEN:.0f} mm of 1.5 mm rod at {RHO_BRASS:.1f} g/cm³ ({n['m_rod_ss']:.1f} g in stainless)"),
        (f"{n['defl_brass'] * 1000:.0f} µm", f"a rail's sag under half of {LOAD_ON_RAILS:.0f} g over {RAIL_SPAN:.0f} mm: F L³ / 48 E I with E {E_BRASS / 1e9:.0f} GPa ({n['defl_ss'] * 1000:.0f} µm in stainless; {n['defl_brass_punch'] * 1000:.0f} at 2.5 g)"),
        (f"{n['tilt_deg']:.0f}°", f"the camera's swing each way: arcsin({STROKE_USED / 2:.0f} mm / {LEVER:.0f} mm lever)"),
        (f"{n['tilt_time'] * 1000:.0f} ms", f"stop to stop: {STROKE_USED:.0f} mm at {SERVO_SPEED * 1000:.0f} ms/mm"),
        (f"{n['cam_torque_gcm']:.2f} g·cm", f"the module's moment on the pin: {CAM_MASS:.1f} g × {CAM_ARM:.1f} mm; the servo is rated {SERVO_TORQUE:.0f}"),
        (f"±{n['side_halfwidth_at_rim']:.1f} mm", f"a side cone's half-width at the discs' outer rim: ({AXLE_X + PROP_R:.0f} − {SIDE_X:.0f}) mm × tan {FOV / 2:.1f}°; the discs begin {n['disc_inner_y']:.0f} mm fore and aft"),
        (f"{n['side_clear_z']:.1f} mm", f"the ranger boards' tops under the prop plane: {PROP_Z} − {SIDE_TOP:.0f}"),
        (f"{n['bus_share']:.0f} %", f"of the I²C bus: five rangers at {RANGE_HZ} Hz × {BYTES_PER_READ} B plus the motion sensor at {IMU_HZ} Hz × {IMU_BYTES} B, on {I2C_KHZ} kHz at 80 %"),
        (f"{abs(n['cg_shift']):.2f} mm", f"the centre of gravity's shift to the tail from the parts off the centre line; the rear motors carry {n['rear_share'] * 100:.1f} %"),
    ]


PARTS = [
    ("lift from disc as much as motor", "7 × 20 mm coreless motors, 4-pack with JST 1.25 leads, in the cart", "https://www.amazon.com/dp/B0DJ17L348"),
    ("the 40 mm disc, grey polycarbonate", "HQ Prop 40 mm four-blade, 1 mm shaft, two sets in the tinywhoop.com cart", "https://www.tinywhoop.com/products/hq-prop-40mm-4-blade-props-grey-1mm-shaft"),
    ("7.5 A and 70 mΩ: the cap at 75 %", "the 250 mAh 30C flight packs on hand", "https://www.amazon.com/dp/B0FCMLVCN2"),
    ("half the stiffness, rosin flux, brown with time", "K&S 1.0 mm brass rod on hand", "https://www.amazon.com/dp/B005WPB7YG"),
    ("the four collars", "K&S 1.5 mm brass rod on hand", "https://www.amazon.com/dp/B01C6LUO5Q"),
    ("9 mm of stroke, 6 used, 30° each way", "AGFRC 1.5 g linear servo pair, in the cart", "https://www.amazon.com/dp/B07L3N5C4S"),
    ("eight switches, one byte, no pins", "Adafruit TCA9548A multiplexer, in the cart", "https://www.amazon.com/dp/B017C09ETS"),
    ("27° cones that never meet a disc", "TOF400C VL53L1X boards, AITRIP 2-pack ×2, in the cart", "https://www.amazon.com/dp/B09LCHPTNM"),
    ("the cutting sheet for the brass", "the frame jig, regenerated for 50 mm axles and 7 mm collars", JIG_PAGE),
]

SOURCES = [
    ("Momentum theory of a propeller, NASA Glenn", "https://www.grc.nasa.gov/www/k-12/airplane/propth.html"),
    ("TCA9548A datasheet, Texas Instruments", "https://www.ti.com/lit/ds/symlink/tca9548a.pdf"),
    ("VL53L1X datasheet, STMicroelectronics", "https://www.st.com/resource/en/datasheet/vl53l1x.pdf"),
    ("Young's modulus of common metals, Engineering ToolBox", "https://www.engineeringtoolbox.com/young-modulus-d_417.html"),
    ("Thermal conductivity of metals, Engineering ToolBox", "https://www.engineeringtoolbox.com/thermal-conductivity-metals-d_858.html"),
    ("The motor, prop, servo, multiplexer and ranger listings read at the cart on 2026-11-10 (links above)", "https://www.amazon.com/gp/cart/view.html"),
    ("XS Drone Custom Build, the sheet this page explains", BUILD_PAGE),
    ("XS Drone Voice Physics, the previous step-two page", VOICE_PAGE),
]


def next_text():
    n = num
    return (f"When the parts come: weigh the motors, props, multiplexer, boards and servo on the coin balance and correct the ledger; measure one 7 × 20 motor's current at a hover duty and at full on the bench supply (test D01 and the switch cell's diode warmth) and set the cap before the first hover. "
            f"Read the thrust gate from the hover command: under {n['hover_cmd_hi']:.0f} % means at least {n['tw_lo']:.1f} to one. Tests C13 (every ranger answers on its channel and none reads a propeller with the props spinning on the bench) and C14 (±{n['tilt_deg']:.0f}° on a protractor) close this revision. "
            "The following page still draws the 37.5 g build; it gets the new geometry when the brass frame is soldered and weighed.")


# ----------------------------------------------------------------------------- the outputs
PAGE_CSS = (":root{--c1:#2A64B0;--c2:#A3580A;--c1-soft:#DCE6F3;--c2-soft:#F3E6D4}"
            "@media (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){--c1:#4F86C8;--c2:#BF8A2A;--c1-soft:#1D2F45;--c2-soft:#3B2E14}}"
            ":root[data-theme=\"dark\"]{--c1:#4F86C8;--c2:#BF8A2A;--c1-soft:#1D2F45;--c2-soft:#3B2E14}"
            "figure svg{width:100%;height:auto} td,th{min-width:0} .src li{margin:4px 0;font-size:15px}")


def page_html(figs):
    style = re.search(r"<style>.*?</style>", (PAGES / "custom-build.html").read_text(encoding="utf8"), re.S).group(0)
    o = ['<title>XS Drone Lift Physics</title>',
         '<meta name="claude:viewport-fit-sides" content="cover">',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=Source+Code+Pro:wght@400;600&display=swap">',
         style,
         f"<style>{PAGE_CSS}</style>",
         '<div class="wrap">',
         '<div class="masthead"><div class="eyebrow">XS drone &middot; step 2: the science and engineering &middot; the lift revision</div>',
         '<h1>Why bigger motors lift all three, and why the ladder is brass</h1>',
         f'<div class="sub">The working behind the lift revision approved on {APPROVED}: lift bought with disc as much as motor, what a 250 mAh pack can feed and why the throttle is capped, the brass ladder and its stiffness, a 6 mm lever that nods the camera 30°, rangers that sit low and look between the discs, five sensors with one address behind one switch, and where the weight went. Read after <a href="{BUILD_PAGE}" target="_blank" rel="noopener">XS Drone Custom Build</a> and <a href="{VOICE_PAGE}" target="_blank" rel="noopener">XS Drone Voice Physics</a>. Nothing measured yet: every figure is derived from the listings, the datasheets and the build page\'s numbers; the motor thrust is a range from physics, since no vendor sheet could be read. Source of truth: <code>xs_drone/docs/lift-physics.md</code>.</div></div>']
    for head, items in chapters():
        o.append(f"<h2>{esc(head)}</h2>")
        for it in items:
            if isinstance(it, tuple):
                _, key, cap = it
                o.append(f"<figure>{figs[key]}<figcaption>{esc(cap)}</figcaption></figure>")
            else:
                o.append(f"<p>{esc(it)}</p>")
    o.append('<h2>The numbers, and where they come from</h2><div class="tw"><table><tr><th>Number</th><th>What it is</th></tr>')
    o += [f'<tr><td class="m">{esc(a)}</td><td>{esc(b)}</td></tr>' for a, b in numbers()]
    o.append("</table></div>")
    o.append("<h2>Which part each idea lives in</h2><ul>")
    o += [f'<li><strong>{esc(idea)}:</strong> <a href="{url}" target="_blank" rel="noopener">{esc(part)}</a></li>' for idea, part, url in PARTS]
    o.append("</ul>")
    o.append(f"<h2>What comes next</h2><p>{esc(next_text())}</p>")
    o.append('<h2>Sources</h2><ul class="src">')
    o += [f'<li><a href="{url}" target="_blank" rel="noopener">{esc(name)}</a></li>' for name, url in SOURCES]
    o.append("</ul>")
    o.append(f'<hr><p class="sub">Built by <code>docs/pages/gen/lift_page.py</code>, which also writes <code>docs/lift-physics.md</code>. Assumptions, each a number at the top of the script: the 615 at {I_615_FULL:.1f} A and the 7 × 20 at {I_720_LOW:.1f} to {I_720_FULL:.0f} A at full throttle; the ledger\'s hover model of {I_REF:.1f} A at {M_REF:.0f} g; {R_PACK * 1000:.0f} mΩ in the cell and {R_LEADS * 1000:.0f} in the pigtail; a regulator that wants {V_LDO_IN:.2f} V and a brown-out near {V_BROWN:.1f}; {LOAD_ON_RAILS:.0f} g on the rails; a {CAM_MASS:.1f} g module {CAM_ARM:.1f} mm ahead of its pin; {BYTES_PER_READ} bytes a ranger read. Brass and stainless figures are handbook values; the servo\'s are its listing\'s. Nothing here has been measured on the drone.</p>')
    o.append("</div>")
    return "\n".join(o)


def page_md():
    o = ["# Why bigger motors lift all three, and why the ladder is brass: the science and engineering behind the lift revision", "",
         f"Step 2 of the house rule for the lift revision of the custom build, written {APPROVED} after the revision was approved that night. Generated by `pages/gen/lift_page.py`; the page [`pages/lift-physics.html`](pages/lift-physics.html) carries the figures. Read after [custom-build.md](custom-build.md) (section More lift) and [voice-physics.md](voice-physics.md). Nothing measured yet; the motor thrust is a range from physics. Edit the script, not this file.", ""]
    for head, items in chapters():
        o += [f"## {head}", ""]
        for it in items:
            if isinstance(it, tuple):
                o += [f"*Figure: {it[2]}*", ""]
            else:
                o += [it, ""]
    o += ["## The numbers, and where they come from", "", "| Number | What it is |", "| --- | --- |"]
    o += [f"| {a} | {b} |" for a, b in numbers()]
    o += ["", "## Which part each idea lives in", ""]
    o += [f"- {idea}: [{part}]({url})" for idea, part, url in PARTS]
    o += ["", "## What comes next", "", next_text(), "", "## Sources", ""]
    o += [f"- [{name}]({url})" for name, url in SOURCES]
    o.append("")
    return "\n".join(o)


def print_pdf(page):
    PRINT.mkdir(exist_ok=True)
    css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
           ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--steel:#000;--steel-soft:#eee;--c1:#000;--c2:#555;--c1-soft:#e4e4e4;--c2-soft:#f1f1f1;--ok:#000;--ok-soft:#f2f2f2;--dev:#000;--dev-soft:#f2f2f2;--no:#000;--no-soft:#eaeaea;--brass:#000;--brass-soft:#ddd;--metal:#000;--metal-soft:#ddd;--matte:#444;--matte-edge:#000;--skin:#f4f4f4;--skin-edge:#777}"
           "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
           "h2{font-size:14pt;margin-top:16pt;page-break-after:avoid;border-top-color:#000} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
           "figure{width:78%;margin:10pt auto;padding:6pt;break-inside:avoid} figure svg{width:100%} figcaption{font-size:8pt} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "p.html"
        pdf = pathlib.Path(d) / "p.pdf"
        head, tail = page.rsplit("</style>", 1)
        src.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + css + tail, encoding="utf8")
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "lift-physics.pdf"
        out.write_bytes(pdf.read_bytes())
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [ln for ln in info.splitlines() if ln.startswith("Pages")])


def main():
    figs = {k: fn() for k, fn in FIGS.items()}
    page = page_html(figs)
    HTML_OUT.write_text(page, encoding="utf8")
    MD_OUT.write_text(page_md(), encoding="utf8")
    print("wrote", HTML_OUT, HTML_OUT.stat().st_size, "and", MD_OUT)
    for k in sorted(num):
        v = num[k]
        if isinstance(v, dict):
            print(f"  {k} = " + ", ".join(f"{kk}: {vv:.4g}" for kk, vv in v.items()))
        else:
            print(f"  {k} = {v:.4g}")
    if "--pdf" in sys.argv:
        print_pdf(page)


if __name__ == "__main__":
    main()
