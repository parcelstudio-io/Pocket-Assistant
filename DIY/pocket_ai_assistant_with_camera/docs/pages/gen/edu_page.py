"""Pocket AI with Camera, step two (after the builder approved Rev B on 2026-11-10): the science, engineering and
physics behind why the build and each part were designed the way the wiring sheet shows.

Writes docs/pages/edu-why.html, docs/EDU.md (the same text without the figures) and, with --pdf,
docs/pages/print/edu-why.pdf (Letter, portrait, black only). Every number on the page is derived here from the
constants at the top, each a datasheet figure, a figure from the wiring sheet, or a named assumption. The five
figures are drawn from those numbers, not sketched. The page style is this project's page_style.css so the page
matches the build page. Edit this script, not the outputs."""
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
HTML_OUT = PAGES / "edu-why.html"
MD_OUT = DOCS / "EDU.md"
PRINT = PAGES / "print"
STYLE = (HERE / "page_style.css").read_text()
BUILD_PAGE = "https://claude.ai/artifact/8ZkGQs8B234B2ohePxHEMg"
APPROVED = "2026-11-10"
WRITTEN = "2026-11-10"

# ----------------------------------------------------------------------------- the sheet's values and the datasheets'
# camera and eyes
FOV_H = 65.0            # degrees across, OV2640 with the stock lens on the Sense board (vendor figures 65-68)
SENSOR_W = 3.52         # mm, OV2640 active width: 1600 px × 2.2 µm
FRAME_W = 320           # px, the frame the face finder runs on (QVGA)
FACE_W = 0.16           # m, a face across the ears
DIST = 1.0              # m, the person at the desk
OLED_PX = (128, 64)     # the screen
OLED_MM = (21.7, 10.9)  # mm, its active area
EYE_SHIFT_PX = 20       # px, how far an eye can slide from home before it leaves the glass
EYE_LIMIT_DEG = 20.0    # degrees of gaze that shift stands for: the head takes over past this
FRAME_RATE = 30.0       # frames a second from the camera at QVGA
# motors and the yoke
RPM = 16.0              # gear motor output, rated at 3 V
V_CELL_FULL, V_CELL_NOM, V_CELL_EMPTY = 4.2, 3.6, 3.0
DUTY_CAP = 0.70
STALL_A = 0.36          # A, the 12 mm class; the listing publishes none
TORQUE_KGCM = 0.30      # kg·cm, the low end of what the 12 mm class quotes at this ratio
HEAD_G = 35.0           # g, XIAO + Sense + OLED + amp + speaker + motor + rods
HEAD_H, HEAD_D = 50.0, 42.0   # mm
GAP = 10.0              # mm between the head's rest line and the body
OFF_AXIS_MM = 5.0       # mm, a plausible miss of the centre of mass
L_MOTOR, R_MOTOR = 1.0e-3, 8.0  # H, Ω: a 12 mm brushed motor, typical
F_PWM = 20e3
R_ON_MX = 0.15          # Ω, one MOSFET in the MX1508's bridge path (listing: 1.5 A, "low on-resistance")
V_DROP_L298 = 2.0       # V, the L298N's two Darlington drops at a few hundred mA (its datasheet: 1.8 to 3.2 V)
# the ladder
VIO = 3.3
R_PULL = 10e3
R_BTN, R_PAN, R_TILT = 680.0, 2200.0, 5600.0
C_LADDER = 100e-9
TOL = 0.05              # resistor tolerance
ADC_BITS, ADC_SPAN = 12, 3.1    # 12 dB attenuation reads to about 3.1 V
ADC_ERR = 0.03          # V, offset and noise after a 4-sample average
R_PULLUP_INT = 45e3     # Ω, the S3's internal pull-up, nominal
V_IH_MX = 1.8           # V, the MX1508's input high threshold (listing: 1.8-7 V inputs)
# audio
F_S = 16e3
BITS_PCM = 16
PDM_RATIO = 128
VOL_CAP = 0.65          # the firmware's 65 of 100
R_SPK = 8.0
P_SPK = 0.8             # W, the speaker's rating
EFF_AMP = 0.85
# the cell
CAP_MAH = 950.0
I_TRIP = 2.0            # A, the NL169's protection
I_CHARGE = 0.10         # A, the XIAO's charger (Seeed says 100 mA; the SGM40567 datasheet 50)
I_3V3_PEAK = 390.0      # mA, camera streaming + OLED
I_AMP_PEAK = 250.0
I_AVG_FOLLOW = 270.0    # mA, listening, talking, following
I_AVG_IDLE = 130.0
I_SLEEP = 3.0
EFF_BOOST = 0.88        # what a 5 V boost would have cost
# I2C and UART
BAUD = 115200
F_I2C = 400e3

num = {}


def derive():
    n = num
    # camera geometry
    n["focal_mm"] = (SENSOR_W / 2) / math.tan(math.radians(FOV_H / 2))
    n["deg_per_px"] = FOV_H / FRAME_W
    n["face_deg"] = math.degrees(2 * math.atan(FACE_W / 2 / DIST))
    n["face_px"] = n["face_deg"] / n["deg_per_px"]
    n["half_view_m"] = DIST * math.tan(math.radians(FOV_H / 2))
    n["eye_limit_m"] = DIST * math.tan(math.radians(EYE_LIMIT_DEG))
    n["px_per_deg_eye"] = EYE_SHIFT_PX / EYE_LIMIT_DEG
    n["oled_px_mm"] = OLED_MM[0] / OLED_PX[0]
    # motion
    n["deg_s"] = RPM * 6.0
    n["deg_100ms"] = n["deg_s"] * 0.1
    n["t_eye_limit"] = EYE_LIMIT_DEG / n["deg_s"]
    n["t_90"] = 90.0 / n["deg_s"]
    n["v_avg_full"] = DUTY_CAP * V_CELL_FULL
    n["v_avg_empty"] = DUTY_CAP * V_CELL_EMPTY
    n["duty_for_3v_empty"] = min(1.0, 3.0 / V_CELL_EMPTY)
    n["tau_motor_us"] = L_MOTOR / R_MOTOR * 1e6
    n["pwm_period_us"] = 1e6 / F_PWM
    n["v_drop_mx"] = 2 * R_ON_MX * STALL_A
    n["v_motor_l298"] = V_CELL_NOM - V_DROP_L298
    # balance
    n["torque_mNm"] = TORQUE_KGCM * 9.81 * 10          # kg·cm → mN·m
    n["offaxis_mNm"] = HEAD_G / 1000 * 9.81 * OFF_AXIS_MM / 1000 * 1000
    n["lift_mm"] = n["torque_mNm"] / 1000 / (HEAD_G / 1000 * 9.81) * 1000
    a, b = HEAD_H / 2, HEAD_D / 2
    n["worst_tilt_deg"] = math.degrees(math.atan2(b, a))
    n["half_diag"] = math.hypot(a, b)
    n["dip_mm"] = n["half_diag"] - a
    n["proud_mm"] = a - b
    # ladder
    def v_of(rs):
        g = sum(1 / r for r in rs)
        rp = 1 / g
        return VIO * rp / (rp + R_PULL)
    states = {"none": VIO, "button": v_of([R_BTN]), "pan": v_of([R_PAN]), "tilt": v_of([R_TILT]), "pan+tilt": v_of([R_PAN, R_TILT]),
              "button+pan": v_of([R_BTN, R_PAN]), "button+tilt": v_of([R_BTN, R_TILT]), "all": v_of([R_BTN, R_PAN, R_TILT])}
    n["ladder"] = states
    n["lsb_mV"] = ADC_SPAN / (2 ** ADC_BITS) * 1000
    n["gap_btn_both_mV"] = (states["pan+tilt"] - states["button"]) * 1000
    n["gap_both_pan_mV"] = (states["pan"] - states["pan+tilt"]) * 1000
    n["gap_pan_tilt_mV"] = (states["tilt"] - states["pan"]) * 1000
    n["tol_shift_mV"] = max(abs(v_of([R_PAN * (1 + TOL)]) - states["pan"]), abs(v_of([R_TILT * (1 + TOL)]) - states["tilt"])) * 1000
    n["bands"] = (0.33, 0.52, 0.85, 1.6)
    n["rc_ms"] = R_PULL * C_LADDER * 1e3
    n["pwm_atten"] = 2 * math.pi * F_PWM * R_PULL * C_LADDER
    n["gpio44_v"] = VIO * 10e3 / (10e3 + R_PULLUP_INT)
    n["i_ladder_mA"] = VIO / (R_PULL + R_BTN) * 1000
    # audio
    n["bclk"] = F_S * BITS_PCM * 2
    n["pdm_clk"] = F_S * PDM_RATIO
    n["v_pk"] = VOL_CAP * V_CELL_FULL
    n["p_spk"] = n["v_pk"] ** 2 / 2 / R_SPK
    n["i_amp_avg_mA"] = n["p_spk"] / EFF_AMP / V_CELL_FULL * 1000
    n["i_spk_pk_mA"] = n["v_pk"] / R_SPK * 1000
    n["p_dc_fault"] = n["v_pk"] ** 2 / R_SPK
    n["p_full_vol"] = V_CELL_FULL ** 2 / 2 / R_SPK
    # cell
    n["wh"] = CAP_MAH / 1000 * V_CELL_NOM
    n["h_follow"] = CAP_MAH / I_AVG_FOLLOW
    n["h_idle"] = CAP_MAH / I_AVG_IDLE
    n["d_sleep"] = CAP_MAH / I_SLEEP / 24
    n["h_charge"] = CAP_MAH / (I_CHARGE * 1000)
    n["c_rate"] = I_CHARGE * 1000 / CAP_MAH
    n["worst_A"] = (I_3V3_PEAK + I_AMP_PEAK + STALL_A * 1000) / 1000
    n["both_stall_A"] = n["worst_A"] + STALL_A
    n["boost_loss_min"] = n["h_follow"] * 60 * (1 - EFF_BOOST)
    # I2C vs UART
    n["bit_us"] = 1e6 / BAUD
    n["i2c_bit_us"] = 1e6 / F_I2C
    return n


# ----------------------------------------------------------------------------- drawing
def esc(s):
    return html.escape(str(s), quote=False)


def f(x, d=0):
    return f"{x:.{d}f}"


FIG_CSS = ("<style>"
           ".ax{fill:none;stroke:var(--ink);stroke-width:1.4;stroke-linecap:round}"
           ".thin{fill:none;stroke:var(--ink);stroke-width:1.2;stroke-linecap:round;stroke-linejoin:round}"
           ".ref{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:4 4}"
           ".s1{fill:none;stroke:var(--signal);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}"
           ".s2{fill:none;stroke:var(--brass);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}"
           ".cone{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.2}"
           ".cone2{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.2}"
           ".box{fill:var(--paper);stroke:var(--ink);stroke-width:1.4}"
           ".ghost{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:4 3}"
           ".sw{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
           ".on{fill:var(--signal-soft);stroke:var(--signal);stroke-width:2}"
           ".band{fill:var(--brass-soft);stroke:none}"
           ".band2{fill:var(--signal-soft);stroke:none}"
           ".dot{fill:var(--ink);stroke:var(--paper);stroke-width:2}"
           ".eye{fill:var(--ink)}"
           ".screen{fill:var(--ink);stroke:var(--ink-2);stroke-width:1}"
           ".pupil{fill:var(--paper)}"
           ".h{font:700 13px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".t{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".num{font:600 12px 'JetBrains Mono',ui-monospace,monospace;fill:var(--ink)}"
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


def rect(x0, y0, x1, y1, cls, rx=0, extra=""):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="{rx}" class="{cls}" {extra}/>'


def circ(x, y, r, cls):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="{cls}"/>'


def fig_eyes():
    """Top view: the camera's cone, the eyes' reach inside it, a face at the eye limit; below, the screen at home and at the limit."""
    n = num
    W, H = 820, 400
    o = []
    cx, cy = 60, 124                     # the camera, looking right
    s = 150 / DIST                       # px per metre
    half = math.radians(FOV_H / 2)
    lim = math.radians(EYE_LIMIT_DEG)
    far = DIST * s
    o.append(polygon([(cx, cy), (cx + far, cy - far * math.tan(half)), (cx + far, cy + far * math.tan(half))], "cone"))
    o.append(polygon([(cx, cy), (cx + far, cy - far * math.tan(lim)), (cx + far, cy + far * math.tan(lim))], "cone2"))
    o.append(circ(cx, cy, 6, "dot")); o.append(T(cx, cy + 24, "camera", "t", "middle"))
    o.append(line(cx, cy, cx + far, cy, "ref"))
    fy = cy - n["eye_limit_m"] * s
    fw = FACE_W * s
    o.append(rect(cx + far - 6, fy - fw / 2, cx + far + 6, fy + fw / 2, "box", 4))
    o.append(T(cx + far + 14, fy + 4, f"a face {f(FACE_W*100)} cm wide at {f(DIST)} m: {f(n['face_deg'])}° of view, {f(n['face_px'])} px of {FRAME_W}", "fn"))
    o.append(T(cx + far + 14, cy - far * math.tan(half) + 4, f"±{f(FOV_H/2, 1)}°: the camera's edge, {f(n['half_view_m']*100)} cm each side at {f(DIST)} m", "fn"))
    o.append(T(cx + far + 14, fy - 14, f"±{f(EYE_LIMIT_DEG)}°: the eyes' reach, {f(n['eye_limit_m']*100)} cm each side", "fn"))
    o.append(T(cx, cy + far * math.tan(half) + 20, "inside the brass cone the eyes move; outside it the head moves", "fn"))
    # screens
    sx, sy = 60, 262
    sw, sh = 128 * 1.6, 64 * 1.6
    caps = (("eyes at home:", "the face is centred"), (f"eyes {EYE_SHIFT_PX} px over: the face is {f(EYE_LIMIT_DEG)}° off;", "one more degree and the head turns"))
    for i, (shift, cap) in enumerate(((0, caps[0]), (EYE_SHIFT_PX * 1.6, caps[1]))):
        x = sx + i * 300
        o.append(rect(x, sy, x + sw, sy + sh, "screen", 3))
        for ex in (x + sw * 0.32, x + sw * 0.68):
            o.append(circ(ex + shift, sy + sh / 2, 14, "pupil"))
            o.append(circ(ex + shift + 4, sy + sh / 2, 6, "eye"))
        o.append(T(x, sy + sh + 16, cap[0], "fn")); o.append(T(x, sy + sh + 30, cap[1], "fn"))
    nx = sx + 300 + sw + 16
    o.append(T(nx, sy + 14, f"{OLED_PX[0]} × {OLED_PX[1]} px", "num"))
    o.append(T(nx, sy + 32, f"{f(n['px_per_deg_eye'])} px per degree of gaze", "fn"))
    o.append(T(nx, sy + 48, f"{f(1/FRAME_RATE*1000)} ms per redraw", "fn"))
    return svg(W, H, "".join(o), "What the camera sees, how far the eyes reach, and when the head takes over")


def fig_bridge():
    """The H-bridge with the forward path lit, and the PWM strip with its average."""
    n = num
    W, H = 840, 310
    o = []
    x0, y0 = 50, 40
    bw, bh = 220, 180
    # rails
    o.append(line(x0, y0, x0 + bw, y0)); o.append(T(x0 + bw / 2, y0 - 10, "BAT+ 3.0 to 4.2 V", "t", "middle"))
    o.append(line(x0, y0 + bh, x0 + bw, y0 + bh)); o.append(T(x0 + bw / 2, y0 + bh + 18, "GND", "t", "middle"))
    # four switches: Q1 top-left, Q2 top-right, Q3 bottom-left, Q4 bottom-right; forward = Q1 + Q4
    sw = {"Q1": (x0 + 30, y0 + 20, True), "Q2": (x0 + bw - 30, y0 + 20, False), "Q3": (x0 + 30, y0 + bh - 60, False), "Q4": (x0 + bw - 30, y0 + bh - 60, True)}
    my = y0 + bh / 2
    for x in (x0 + 30, x0 + bw - 30):
        o.append(line(x, y0, x, y0 + 20)); o.append(line(x, y0 + 60, x, y0 + bh - 60)); o.append(line(x, y0 + bh - 20, x, y0 + bh))
    o.append(line(x0 + 30, my, x0 + bw / 2 - 22, my)); o.append(line(x0 + bw / 2 + 22, my, x0 + bw - 30, my))
    o.append(poly([(x0 + 30, y0), (x0 + 30, my), (x0 + bw / 2 - 22, my)], "s1"))
    o.append(poly([(x0 + bw / 2 + 22, my), (x0 + bw - 30, my), (x0 + bw - 30, y0 + bh)], "s1"))
    for name, (x, y, on) in sw.items():
        o.append(rect(x - 14, y, x + 14, y + 40, "on" if on else "sw", 4))
        o.append(T(x, y + 25, name, "num", "middle"))
    o.append(circ(x0 + bw / 2, my, 22, "box")); o.append(T(x0 + bw / 2, my + 4, "M", "h", "middle"))
    o.append(T(x0 + bw + 16, y0 + 30, "Q1 + Q4 on: current left to right, forward", "fn"))
    o.append(T(x0 + bw + 16, y0 + 48, "Q2 + Q3 on: right to left, reverse", "fn"))
    o.append(T(x0 + bw + 16, y0 + 66, "Q3 + Q4 on: the motor shorted, brake", "fn"))
    o.append(T(x0 + bw + 16, y0 + 84, "all off: coast", "fn"))
    o.append(T(x0 + bw + 16, y0 + 112, f"MOSFET switches: {f(R_ON_MX*1000)} mΩ each, {f(n['v_drop_mx']*1000)} mV lost at {f(STALL_A*1000)} mA", "fn"))
    o.append(T(x0 + bw + 16, y0 + 130, f"the L298N's transistors: about {f(V_DROP_L298, 1)} V lost, {f(n['v_motor_l298'], 1)} V left for the motor", "fn"))
    # PWM strip
    px0, py0, pw, ph = x0 + bw + 16, y0 + 150, 380, 60
    o.append(rect(px0, py0, px0 + pw, py0 + ph, "box"))
    per = pw / 4
    pts = [(px0, py0 + ph)]
    for k in range(4):
        a = px0 + k * per
        pts += [(a, py0 + ph), (a, py0), (a + per * DUTY_CAP, py0), (a + per * DUTY_CAP, py0 + ph)]
    pts.append((px0 + pw, py0 + ph))
    o.append(poly(pts, "s1"))
    avg_y = py0 + ph * (1 - DUTY_CAP)
    o.append(line(px0, avg_y, px0 + pw, avg_y, "s2"))
    o.append(T(px0 + pw + 8, py0 + 4, f"{f(V_CELL_FULL,1)} V", "num")); o.append(T(px0 + pw + 8, avg_y + 4, f"{f(n['v_avg_full'],1)} V average", "num"))
    o.append(T(px0, py0 + ph + 16, f"{f(DUTY_CAP*100)} % duty at {f(F_PWM/1000)} kHz: {f(n['pwm_period_us'])} µs a cycle; the winding needs {f(n['tau_motor_us'])} µs", "fn"))
    o.append(T(px0, py0 + ph + 30, "to change its current, so the current barely ripples", "fn"))
    return svg(W, H, "".join(o), "The H-bridge and the PWM that sets the motor's speed")


def fig_ladder():
    """The divider with its three branches, and the voltage scale with the bands."""
    n = num
    W, H = 820, 345
    o = []
    x0, y0 = 70, 40
    o.append(T(x0, y0 - 14, f"3.3 V", "num"))
    o.append(line(x0, y0, x0, y0 + 40))
    o.append(rect(x0 - 10, y0 + 40, x0 + 10, y0 + 80, "box")); o.append(T(x0 + 18, y0 + 64, f"R4 {f(R_PULL/1000)} kΩ", "fn"))
    o.append(line(x0, y0 + 80, x0, y0 + 110)); o.append(circ(x0, y0 + 110, 4, "dot")); o.append(T(x0 + 12, y0 + 106, "D10, the ADC", "t"))
    o.append(line(x0, y0 + 110, x0 + 270, y0 + 110))
    for i, (name, r) in enumerate((("button", R_BTN), ("pan stop", R_PAN), ("tilt stop", R_TILT))):
        x = x0 + 60 + i * 105
        o.append(circ(x, y0 + 110, 4, "dot"))
        o.append(line(x, y0 + 110, x, y0 + 130))
        o.append(line(x - 10, y0 + 130, x + 10, y0 + 150, "thin")); o.append(line(x, y0 + 155, x, y0 + 175))  # the switch
        o.append(rect(x - 10, y0 + 175, x + 10, y0 + 215, "box")); o.append(line(x, y0 + 215, x, y0 + 240))
        o.append(line(x - 12, y0 + 240, x + 12, y0 + 240)); o.append(line(x - 7, y0 + 246, x + 7, y0 + 246, "thin")); o.append(line(x - 3, y0 + 252, x + 3, y0 + 252, "thin"))
        o.append(T(x + 14, y0 + 148, name, "fn")); o.append(T(x + 14, y0 + 199, f"{f(r) if r < 1000 else f(r/1000, 1)} {'Ω' if r < 1000 else 'kΩ'}", "fn"))
    o.append(T(x0, y0 + 285, f"V = 3.3 V × R ÷ (R + {f(R_PULL/1000)} kΩ); two pressed = their parallel value", "fn"))
    # the scale
    sx, sy, sh = 480, 40, 240
    top_v = 1.6
    def yv(v):
        return sy + sh * (1 - min(v, top_v) / top_v)
    bands = [(0, n["bands"][0], "button"), (n["bands"][0], n["bands"][1], "both stops"), (n["bands"][1], n["bands"][2], "pan stop"), (n["bands"][2], n["bands"][3], "tilt stop")]
    for i, (lo, hi, lab) in enumerate(bands):
        o.append(rect(sx, yv(hi), sx + 70, yv(lo), "band" if i % 2 else "band2"))
        o.append(T(sx + 78, (yv(lo) + yv(hi)) / 2 + 4, lab, "t"))
    o.append(line(sx, sy, sx, sy + sh))
    for k, v in (("button", n["ladder"]["button"]), ("pan+tilt", n["ladder"]["pan+tilt"]), ("pan", n["ladder"]["pan"]), ("tilt", n["ladder"]["tilt"])):
        o.append(line(sx - 6, yv(v), sx + 70, yv(v), "s1")); o.append(T(sx - 10, yv(v) + 4, f"{f(v, 2)} V", "num", "end"))
    for v in (n["ladder"]["button+pan"], n["ladder"]["all"]):
        o.append(line(sx - 6, yv(v), sx + 70, yv(v), "ref"))
    o.append(T(sx, sy - 12, f"volts at D10; nothing pressed reads 3.3 V, off this scale", "fn"))
    o.append(T(sx + 160, yv(n["bands"][3]) + 40, f"{f(n['lsb_mV'], 2)} mV a count", "fn")); o.append(T(sx + 160, yv(n["bands"][3]) + 56, f"{f(n['tol_shift_mV'])} mV from 5 % resistors", "fn"))
    o.append(T(sx + 160, yv(n["bands"][3]) + 72, f"{f(n['gap_btn_both_mV'])} mV, the smallest gap", "fn"))
    return svg(W, H, "".join(o), "The ladder: one ADC pin reads three buttons")


def fig_balance():
    """Side view: the head at rest on its axis, and at the worst tilt, with the dip below the rest line and the gap."""
    n = num
    W, H = 870, 335
    o = []
    s = 3.2
    caps = (("at rest: the axis through", "the head's centre of mass"),
            (f"at {f(n['worst_tilt_deg'])}°, the corner's lowest:", f"{f(n['dip_mm'], 1)} mm under the rest line"),
            (f"at 90°: {f(n['proud_mm'])} mm proud of the body's", f"front, {f(n['proud_mm'])} mm above the rest line"))
    for i, (theta, cap) in enumerate(((0.0, caps[0]), (n["worst_tilt_deg"], caps[1]), (90.0, caps[2]))):
        ax, ay = 170 + i * 260, 110
        a, b = HEAD_H / 2 * s, HEAD_D / 2 * s
        th = math.radians(theta)
        pts = []
        for (px, py) in ((-b, -a), (b, -a), (b, a), (-b, a)):
            pts.append((ax + px * math.cos(th) - py * math.sin(th), ay + px * math.sin(th) + py * math.cos(th)))
        o.append(polygon(pts, "box" if i == 0 else "ghost"))
        if i == 0:
            o.append(rect(ax - b - 4, ay + a + GAP * s, ax + b + 4, ay + a + GAP * s + 40, "box"))
            o.append(T(ax, ay + a + GAP * s + 26, "body", "t", "middle"))
            o.append(line(ax - b - 20, ay + a, ax - b - 20, ay + a + GAP * s, "ax")); o.append(T(ax - b - 26, ay + a + GAP * s / 2 + 4, f"{f(GAP)} mm gap", "num", "end"))
        o.append(circ(ax, ay, 4, "dot"))
        o.append(line(ax - b - 20, ay + a, ax + b + 20, ay + a, "ref"))
        low = max(py for _, py in pts)
        if i > 0:
            o.append(line(ax - b - 20, low, ax + b + 20, low, "s2"))
            d = (low - (ay + a)) / s
            o.append(T(ax + b + 24, low + 4, f"{f(abs(d), 1)} mm {'under' if d > 0 else 'above'}", "num"))
        o.append(T(ax, 280, cap[0], "fn", "middle")); o.append(T(ax, 295, cap[1], "fn", "middle"))
    o.append(T(435, 322, f"{f(HEAD_G)} g on the axis holds itself; {f(OFF_AXIS_MM)} mm off it asks {f(n['offaxis_mNm'], 1)} mN·m of the motor's {f(n['torque_mNm'])}", "fn", "middle"))
    return svg(W, H, "".join(o), "Balance on the tilt axis and the corner sweep that sets the gap")


def fig_cell():
    """Current bars against the cell's trip, and hours per charge."""
    n = num
    W, H = 760, 318
    o = []
    x0, y0, bw = 230, 40, 400
    scale = bw / 2.2
    rows = [("worst second, one axis stalled", [("XIAO + camera + screen", I_3V3_PEAK), ("amp", I_AMP_PEAK), ("motor stalled", STALL_A * 1000)]),
            ("both motors stalled (never by design)", [("XIAO + camera + screen", I_3V3_PEAK), ("amp", I_AMP_PEAK), ("motor", STALL_A * 1000), ("motor", STALL_A * 1000)]),
            ("following and talking, average", [("", I_AVG_FOLLOW)]),
            ("Wi-Fi idle, camera off", [("", I_AVG_IDLE)]),
            ("deep sleep", [("", I_SLEEP)])]
    for i, (lab, parts) in enumerate(rows):
        y = y0 + i * 36
        o.append(T(x0 - 10, y + 16, lab, "fn", "end"))
        x = x0
        for j, (p, mA) in enumerate(parts):
            w = mA / 1000 * scale
            o.append(rect(x, y, x + w, y + 24, "band2" if j % 2 == 0 else "band"))
            o.append(rect(x, y, x + w, y + 24, "thin"))
            x += w
        o.append(T(x + 6, y + 16, f"{f(sum(m for _, m in parts))} mA", "num"))
    tx = x0 + I_TRIP * scale
    o.append(line(tx, y0 - 10, tx, y0 + 5 * 36, "s2")); o.append(T(tx, y0 - 16, f"{f(I_TRIP, 1)} A: the cell's protection trips", "num", "middle"))
    o.append(line(x0, y0 + 5 * 36, x0 + bw, y0 + 5 * 36))
    for a in (0, 0.5, 1.0, 1.5, 2.0):
        o.append(line(x0 + a * scale, y0 + 5 * 36, x0 + a * scale, y0 + 5 * 36 + 5)); o.append(T(x0 + a * scale, y0 + 5 * 36 + 18, f"{a:g} A", "fn", "middle"))
    y = y0 + 5 * 36 + 40
    o.append(T(x0 - 10, y + 4, f"{f(CAP_MAH)} mAh, {f(n['wh'], 1)} Wh", "num", "end"))
    o.append(T(x0, y + 4, f"{f(n['h_follow'], 1)} h following and talking · {f(n['h_idle'])} h idle · {f(n['d_sleep'])} days asleep", "fn"))
    o.append(T(x0, y + 20, f"{f(n['h_charge'])} h to charge at {f(I_CHARGE*1000)} mA (C/{f(1/n['c_rate'])}) through the XIAO; 2 h in an external charger", "fn"))
    return svg(W, H, "".join(o), "What the cell is asked for, against what it allows")


FIGS = {"eyes": fig_eyes, "bridge": fig_bridge, "ladder": fig_ladder, "balance": fig_balance, "cell": fig_cell}


# ----------------------------------------------------------------------------- the chapters
def chapters():
    n = num
    L = n["ladder"]
    return [
        ("One cell, and why nothing is boosted", [
            f"{f(n['wh'], 1)} Wh is what the Nitecore cell holds: {f(CAP_MAH)} mAh at {f(V_CELL_NOM, 1)} V nominal. A lithium-ion cell sits at {f(V_CELL_FULL, 1)} V full and is empty at {f(V_CELL_EMPTY, 1)} V, and every part on the sheet works across that whole range: the XIAO regulates it down to 3.3 V itself, the amp runs from 2.5 V up, the driver from 2 V up, the motors are 3 V parts.",
            f"A 5 V boost converter would have cost about {f((1-EFF_BOOST)*100)} % of every watt as heat, plus its idle draw, plus a board and a rail to route. On a {f(n['h_follow'], 1)} hour run that is {f(n['boost_loss_min'])} minutes thrown away for nothing the parts asked for. So the cell is the only rail.",
            f"The cell is a protected one: a small board inside the can opens the circuit above {f(I_TRIP, 1)} A, below {f(2.5, 1)} V and above 4.25 V. That is the last line, not the first: the design's worst second asks {f(n['worst_A'], 2)} A, and even two stalled motors at once would be {f(n['both_stall_A'], 2)} A.",
            ("fig", "cell", f"The bars are the sheet's current budget; the dashed line is the protection's trip. Average running figures give {f(n['h_follow'], 1)} hours of following and talking, {f(n['h_idle'])} idle and {f(n['d_sleep'])} days asleep."),
            f"Charging is slow on purpose. The XIAO's charger pushes {f(I_CHARGE*1000)} mA, which is C/{f(1/n['c_rate'])}: {f(n['h_charge'])} hours from empty, and only when the device sleeps, because awake it draws more than that. A charger follows a constant current until the cell reaches 4.20 V, then holds the voltage while the current tapers; the protected NL169 is built for exactly that profile. Below 0 °C lithium plates onto the anode as metal instead of entering it, which is why the rule says never charge a cold cell.",
        ]),
        ("The camera, the eyes, and why the eyes move first", [
            f"{f(FOV_H)}° is what the camera's lens takes in across the frame. A lens is a pinhole with a focal length: the sensor is {f(SENSOR_W, 2)} mm wide, so the lens sits {f(n['focal_mm'], 2)} mm behind it, and every pixel of a {FRAME_W}-wide frame covers {f(n['deg_per_px'], 2)}°. A face {f(FACE_W*100)} cm across at {f(DIST)} m spans {f(n['face_deg'])}°, about {f(n['face_px'])} pixels: plenty for a face finder, and enough to place its centre to a degree.",
            f"The eyes are drawn on {OLED_PX[0]} × {OLED_PX[1]} pixels of glass {f(OLED_MM[0], 1)} mm wide. An eye can slide {EYE_SHIFT_PX} pixels from home before it runs out of white, and the firmware lets that stand for {f(EYE_LIMIT_DEG)}° of gaze: {f(n['px_per_deg_eye'])} pixel per degree. The screen redraws every {f(1000/FRAME_RATE)} ms, so the eyes follow a face the instant the frame says where it is.",
            f"The head is slower on purpose. At {f(RPM)} rpm it turns {f(n['deg_s'])}° a second, so the {f(EYE_LIMIT_DEG)}° the eyes cover takes it {f(n['t_eye_limit']*1000)} ms and a quarter turn {f(n['t_90'], 1)} s. Fast eyes, slow head is how animals do it too: the eyes jump, then the head catches up and the eyes drift back to centre. The rule in the firmware is one line: while the face is inside ±{f(EYE_LIMIT_DEG)}°, move the eyes; past it, move the head until it is centred.",
            ("fig", "eyes", f"The pale cone is the camera's {f(FOV_H)}°, the brass cone the eyes' ±{f(EYE_LIMIT_DEG)}°. Because the camera sees {f(n['half_view_m']*100)} cm to each side at {f(DIST)} m and the eyes only reach {f(n['eye_limit_m']*100)} cm, the head always moves before the face can leave the frame."),
            "Camera and screen share one head, so where the camera points is where the eyes point, by construction. The difference the builder asked about, the screen looking somewhere the camera is not, is the pixel offset of the eyes, not a second gimbal.",
        ]),
        ("Two gear motors, and what a gearbox buys", [
            f"A brushed DC motor spins at a speed set by its voltage and pushes with a torque set by its current. Bare, a 12 mm motor turns thousands of times a minute with almost no torque. The gearbox trades that speed for force: {f(RPM)} rpm at the output means a few hundred turns of the motor for one of the shaft, and the torque is multiplied by the same ratio, less friction.",
            f"{f(RPM)} rpm is {f(n['deg_s'])}° a second, so a pulse of 100 ms is {f(n['deg_100ms'], 1)}°. That is what makes timed moves repeatable without an encoder. It is also why the same gearbox holds the head where it was left: back-driving a high ratio means pushing the motor through all its stages of friction, which the head's weight cannot do when it sits on its axis.",
            f"The motors are 3 V parts on a cell that reads up to {f(V_CELL_FULL, 1)} V. The driver's PWM fixes that: on for {f(DUTY_CAP*100)} % of each cycle, off for the rest, and the winding's own inductance smooths the pulses into an average of {f(n['v_avg_full'], 1)} V at a full cell. At {f(F_PWM/1000)} kHz a cycle is {f(n['pwm_period_us'])} µs; the winding takes about {f(n['tau_motor_us'])} µs to change its current, so the ripple is small, and 20 kHz is above what an ear picks up.",
            f"Stall is the figure that matters for the wires and the cell: a blocked 12 mm motor draws about {f(STALL_A*1000)} mA. The home stops are what stall it on purpose for an instant at boot, and the firmware moves one axis at a time so the budget only ever carries one.",
        ]),
        ("The H-bridge, and why the MX1508 and not the L298N", [
            "Reversing a motor means reversing which end of it sees the battery. An H-bridge is four switches around the motor; close one upper and the opposite lower and current flows one way, close the other pair and it flows the other. Close both lowers and the motor is shorted across itself, so its own back-EMF brakes it; open all four and it coasts.",
            ("fig", "bridge", f"Forward lit. Below, the PWM: {f(DUTY_CAP*100)} % of {f(V_CELL_FULL, 1)} V averages {f(n['v_avg_full'], 1)} V."),
            f"The MX1508's switches are MOSFETs. On, a MOSFET is a resistor of about {f(R_ON_MX*1000)} mΩ, so two in the path lose {f(n['v_drop_mx']*1000)} mV at {f(STALL_A*1000)} mA. The L298N the listing name borrows from uses bipolar Darlington transistors, which lose a fixed {f(V_DROP_L298, 1)} V or more regardless of current: from a {f(V_CELL_NOM, 1)} V cell the motor would see {f(n['v_motor_l298'], 1)} V. That is the whole reason one works on a cell and the other does not.",
            f"Two pins per motor, four for two: IN1 and IN2 for bridge A, IN3 and IN4 for bridge B, one chip. Each input has a 10 kΩ pull-down because a CMOS input left floating while the processor boots can read as high, and a motor that twitches at power-on is a motor that drifts off its home. GPIO44 wakes with a weak internal pull-up of about {f(R_PULLUP_INT/1000)} kΩ; against the 10 kΩ that is {f(n['gpio44_v'], 1)} V at the driver, under its {f(V_IH_MX, 1)} V threshold.",
        ]),
        ("Balance, the yoke, and the gap", [
            f"The tilt axis runs through the head's centre of mass. A body balanced on its axis asks no torque to hold at any angle, so the tilt motor only ever works against friction and inertia. Miss the centre by {f(OFF_AXIS_MM)} mm and {f(HEAD_G)} g asks {f(n['offaxis_mNm'], 1)} mN·m; the gearbox gives about {f(n['torque_mNm'])} mN·m, enough to lift the whole head {f(n['lift_mm'])} mm off axis. Balance is a courtesy to the battery, not a requirement.",
            ("fig", "balance", f"A {f(HEAD_H)} × {f(HEAD_D)} mm head turning about its centre. The lowest corner is at {f(n['worst_tilt_deg'])}° of tilt, {f(n['dip_mm'], 1)} mm under the rest line, which is why the gap to the body is {f(GAP)} mm."),
            f"The yoke is a U of 1.5 mm brass tube because the head needs two bearings on one line and the pan hub under its middle. One arm carries the motor's D-shaft in a 4 mm tube socket, the other a plain 1.5 mm pin in a 3 mm tube; the motor side locates the head and the pin side only supports it, so nothing is over-constrained and nothing binds. The pan motor turns the yoke, head and all, from the hub below.",
            "Wires that cross a joint are the part that wears. A bare rod bends a few hundred times before it cracks; fine silicone-insulated stranded wire bends hundreds of thousands. Five of them run up one upright as a single line, coiled once round the pan hub so ±150° of turn is spread along the coil, and looped at the tilt pin for the ±90°.",
        ]),
        ("The ladder: three buttons on one pin", [
            f"The XIAO has eleven header pins and the sheet needs twelve signals. The three switches became one by sharing an ADC pin through a resistor ladder. A {f(R_PULL/1000)} kΩ resistor pulls the pin to 3.3 V; each switch, when pressed, pulls it toward ground through its own resistor. The pin voltage is 3.3 V × R ÷ (R + 10 kΩ): {f(L['button'], 2)} V for the button's 680 Ω, {f(L['pan'], 2)} V for the pan stop's 2.2 kΩ, {f(L['tilt'], 2)} V for the tilt stop's 5.6 kΩ.",
            f"Two pressed at once put their resistors in parallel, which is always less than either, so the voltage drops further: {f(L['pan+tilt'], 2)} V for both stops, and anything with the button under {f(L['button'], 2)} V. Every combination lands in its own place, and the firmware reads bands, not values: under {f(n['bands'][0], 2)} V is the button, {f(n['bands'][0], 2)} to {f(n['bands'][1], 2)} both stops, then the pan stop, then the tilt stop up to {f(n['bands'][3], 1)} V, and anything near 3.3 V is nothing.",
            ("fig", "ladder", f"The circuit and its scale. The smallest gap between neighbours is {f(n['gap_btn_both_mV'])} mV; 5 % resistors move a reading by up to {f(n['tol_shift_mV'])} mV and the ADC by about {f(ADC_ERR*1000)} mV. The generator asserts that margin."),
            f"The ADC has {2**ADC_BITS} steps across about {f(ADC_SPAN, 1)} V, {f(n['lsb_mV'], 2)} mV each, so the gaps are hundreds of steps wide. The 100 nF capacitor with the 10 kΩ source makes a {f(n['rc_ms'])} ms filter: the motors' {f(F_PWM/1000)} kHz switching is cut {f(n['pwm_atten'])}-fold before it reaches the pin, and a finger's bounce is averaged away. The ladder never draws more than {f(n['i_ladder_mA'], 1)} mA, and only while something is pressed.",
            "The button is read in the same bands, so it is ignored for the second the head spends homing: a press then would look like a stop closing early. After that the ladder behaves as three separate buttons would.",
        ]),
        ("Why the screen's clock sits on the UART pin", [
            f"GPIO43 is the ESP32-S3's UART0 transmit pin, and the boot ROM prints its log there before any firmware runs: a burst of bits at {BAUD} baud, {f(n['bit_us'], 1)} µs each, for a fraction of a second. Rev A left the pin empty for that reason. Rev B needed it.",
            "I2C has a grammar. A transaction begins only with a start condition: the data line falling while the clock line is high. Clock pulses on their own, with the data line sitting high on its pull-up, are not a start, so the screen's controller ignores them entirely. That makes SCL the one signal that boot chatter cannot disturb, and the S3's GPIO matrix lets I2C live on any pin, so it moved there. The console goes over USB, so the log is not missed.",
            f"The I2C bus itself runs at {f(F_I2C/1000)} kHz, {f(n['i2c_bit_us'], 1)} µs a bit, both lines open-drain with pull-ups, which is why neither line can ever fight the chatter: nothing on I2C drives high.",
        ]),
        ("I2S in, I2S out, and why the amp must be told to sleep", [
            f"The microphone on the Sense board speaks in single bits: a PDM stream at {f(n['pdm_clk']/1e6, 3)} MHz, {PDM_RATIO} pulses for every sample, whose density is the sound pressure. The S3's I2S peripheral filters and decimates that into {BITS_PCM}-bit samples at {f(F_S/1000)} kHz, speech bandwidth, with no analogue stage anywhere.",
            f"Out the other side the samples go to the amp as I2S: a bit clock at {f(n['bclk']/1000)} kHz, a word clock at {f(F_S/1000)} kHz and the data line. The MAX98357A turns each sample into a pulse-width pattern at a few hundred kilohertz and switches the speaker between the rails with it; the speaker's own inductance and mass recover the audio and the switches waste almost nothing, which is why a class-D chip the size of a grain feeds a speaker from a cell.",
            f"The volume cap of 65 is a physics number. At a full cell the output swings {f(n['v_pk'], 2)} V peak, which into {f(R_SPK)} Ω is {f(n['p_spk'], 2)} W, under the speaker's {f(P_SPK, 1)} W. Without the cap it would be {f(n['p_full_vol'], 1)} W, and the cone would not last the afternoon. The amp draws about {f(n['i_amp_avg_mA'])} mA at that level, {f(n['i_spk_pk_mA'])} mA at the peaks.",
            f"The shutdown line stays for a reason the datasheet's maker spells out: the amp must be shut down before its clocks stop. A class-D stage that loses its clock mid-pattern can leave the speaker held at DC, and {f(n['v_pk'], 1)} V of DC across {f(R_SPK)} Ω is {f(n['p_dc_fault'], 2)} W of pure heat in a voice coil rated for {f(P_SPK, 1)} W of music. So SD goes low first, then the clocks, every time, and the pull-down holds it low from the first microsecond of power.",
        ]),
        ("What the Sense board owns, and the pin arithmetic", [
            "The camera talks over a parallel bus: eight data lines, a pixel clock, a frame sync, a line sync, the clock the camera is fed, and two lines of its own I2C-like control bus. Fourteen pins, soldered on the expansion board, not negotiable. The microphone takes two more. The micro-SD slot shares three of the header pins with its SPI, which is why the slot stays empty: those three drive the pan motor and the ladder.",
            "That leaves the eleven header pins: three for I2S out, one for the amp's shutdown, two for I2C, four for the two bridges, one for the ladder. Eleven for eleven. Any future addition goes on the I2C bus, where an address costs no pins.",
        ]),
        ("Brass, bare, and why the frame floats", [
            "Brass solders with the same iron and the same tin as the circuit, so the frame and its sockets are built on the bench with no other tool. It is left bare under the builder's rule: no paint, no skins. Brass does not rust; it darkens to a patina over months, which the family's other builds already wear.",
            "Brass also conducts, and that is the one danger of a metal frame. A single touch between a rod and the frame is harmless; a second touch anywhere else makes a circuit the sheet never drew. So the frame connects to nothing, every rod keeps 2 mm from it, and the meter checks for continuity between the frame and both rails before the cell goes in. A floating frame cannot short, cannot carry motor current and cannot become an antenna for the Wi-Fi.",
            "The parts that come in colours the rule does not allow are placed, not hidden: the red or blue driver board behind the cell holder, the amp under the speaker, the OLED's board behind its own glass. Light from the device is the screen's white pixels and nothing else.",
        ]),
    ]


def numbers():
    n = num
    L = n["ladder"]
    return [
        (f"{f(n['focal_mm'], 2)} mm", f"the lens's focal length: a {f(SENSOR_W, 2)} mm sensor seeing {f(FOV_H)}°"),
        (f"{f(n['deg_per_px'], 2)}° per pixel", f"{f(FOV_H)}° over a {FRAME_W}-pixel frame"),
        (f"{f(n['face_px'])} px", f"a {f(FACE_W*100)} cm face at {f(DIST)} m in that frame"),
        (f"{f(n['px_per_deg_eye'])} px per degree", f"{EYE_SHIFT_PX} px of eye travel standing for {f(EYE_LIMIT_DEG)}° of gaze"),
        (f"{f(n['deg_s'])}° per second", f"{f(RPM)} rpm at the gearbox output"),
        (f"{f(n['deg_100ms'], 1)}°", "one 100 ms pulse of the motor"),
        (f"{f(n['v_avg_full'], 1)} V", f"{f(DUTY_CAP*100)} % duty at a {f(V_CELL_FULL, 1)} V cell"),
        (f"{f(n['v_drop_mx']*1000)} mV", f"lost in the MX1508's two switches at {f(STALL_A*1000)} mA stall"),
        (f"{f(n['v_motor_l298'], 1)} V", f"what an L298N would leave the motor from a {f(V_CELL_NOM, 1)} V cell"),
        (f"{f(n['offaxis_mNm'], 1)} mN·m", f"holding a {f(HEAD_G)} g head {f(OFF_AXIS_MM)} mm off its axis; the motor has about {f(n['torque_mNm'])}"),
        (f"{f(n['dip_mm'], 1)} mm", f"how far the head's corner dips below its rest line, at {f(n['worst_tilt_deg'])}°"),
        (f"{f(L['button'], 2)} / {f(L['pan'], 2)} / {f(L['tilt'], 2)} / {f(L['pan+tilt'], 2)} V", "the ladder: button, pan stop, tilt stop, both stops"),
        (f"{f(n['lsb_mV'], 2)} mV", f"one ADC count: {f(ADC_SPAN, 1)} V over {2**ADC_BITS}"),
        (f"{f(n['rc_ms'])} ms", "the ladder's RC filter: 10 kΩ × 100 nF"),
        (f"{f(n['bclk']/1000)} kHz", f"the I2S bit clock: {f(F_S/1000)} kHz × {BITS_PCM} bits × 2 channels"),
        (f"{f(n['pdm_clk']/1e6, 3)} MHz", f"the microphone's clock: {PDM_RATIO} × {f(F_S/1000)} kHz"),
        (f"{f(n['p_spk'], 2)} W", f"into {f(R_SPK)} Ω at the volume cap of 65 and a full cell; the speaker is rated {f(P_SPK, 1)}"),
        (f"{f(n['p_dc_fault'], 2)} W", "the heat if the amp were ever left at DC: why SD goes low before the clocks"),
        (f"{f(n['wh'], 1)} Wh", f"the cell: {f(CAP_MAH)} mAh × {f(V_CELL_NOM, 1)} V"),
        (f"{f(n['worst_A'], 2)} A", f"the worst second, against a {f(I_TRIP, 1)} A trip"),
        (f"{f(n['h_follow'], 1)} h · {f(n['h_idle'])} h · {f(n['h_charge'])} h", "following and talking · Wi-Fi idle · charging through the XIAO"),
    ]


PARTS = [
    ("the lens, the sensor and the microphone", "Seeed XIAO ESP32-S3 Sense", "https://www.amazon.com/dp/B0C69FFVHH"),
    ("the H-bridges", "MX1508 dual motor driver, Aideepen", "https://www.amazon.com/dp/B075S368Y2"),
    ("the gearboxes", "12 mm gear motor, 3 V 16 rpm, Naroote", "https://www.amazon.com/dp/B0BS9K8Q8Z"),
    ("the cell", "Nitecore NL169 16340, protected", "https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery"),
    ("its holder", "16340 / CR123A holder with leads, ACEIRMC", "https://www.amazon.com/dp/B0CRGK889F"),
    ("the switch in the cell's lead", "MTS-102 toggle, Ferwooh", "https://www.amazon.com/dp/B0CZ6XZ2P9"),
    ("the eyes", "0.96 inch SSD1306 OLED, Hosyond", "https://www.amazon.com/dp/B09T6SJBV5"),
    ("the class-D stage", "MAX98357A I2S amplifier, HiLetgo", "https://www.amazon.com/dp/B0CDWXZZCH"),
    ("the voice coil", "Same Sky CES-20134-088PM enclosed speaker", "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309"),
    ("the ladder's three switches", "tactile buttons, QTEATAK", "https://www.amazon.com/dp/B0FHW6HMG4"),
    ("the ladder's resistors and the pull-downs", "resistor kit, LuminologyPro", "https://www.amazon.com/dp/B0F4P352BB"),
    ("the yoke and the frame", "K&S 1.5 mm brass tube and rod", "https://www.amazon.com/dp/B005WPAW9M"),
    ("the shaft sockets", "METERXITY brass tube set, 2 to 7 mm", "https://www.amazon.com/dp/B0F2FKLC2N"),
]

SOURCES = [
    ("Seeed wiki: Getting started with XIAO ESP32S3 (Sense): pinout, camera and microphone GPIOs, power figures", "https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/"),
    ("Seeed wiki: XIAO ESP32S3 Sense camera usage (OV2640, the expansion board)", "https://wiki.seeedstudio.com/xiao_esp32s3_camera_usage/"),
    ("OV2640 datasheet, OmniVision: 1/4 inch sensor, 2.2 µm pixels", "https://www.uctronics.com/download/cam_module/OV2640DS.pdf"),
    ("ESP32-S3 Technical Reference Manual: ADC (chapter 39), GPIO matrix (chapter 6), I2S (chapter 32)", "https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf"),
    ("ESP-IDF, ADC oneshot driver for the ESP32-S3: attenuation and range", "https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc_oneshot.html"),
    ("MAX98357A/B datasheet, Analog Devices (Maxim): SD_MODE, output power, shutdown", "https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf"),
    ("ADI EngineerZone: shut the MAX98357 down before removing LRCLK", "https://ez.analog.com/audio/w/documents/27472/dc-output-on-speaker-for-max98357"),
    ("L298N datasheet, STMicroelectronics: saturation voltages", "https://www.st.com/resource/en/datasheet/l298.pdf"),
    ("MX1508 listing: 2-10 V, 1.5 A, 1.8-7 V inputs", "https://www.amazon.com/dp/B075S368Y2"),
    ("I2C-bus specification UM10204, NXP: the START condition", "https://www.nxp.com/docs/en/user-guide/UM10204.pdf"),
    ("CES-20134-088PM datasheet, Same Sky: 8 Ω, 0.8 W", "https://sameskydevices.com/product/resource/ces-20134-088pm.pdf"),
    ("Nitecore NL169 at IMR Batteries: 950 mAh, protected, 2 A", "https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery"),
    ("Pocket AI with Camera, Rev B build page: the sheet these numbers come from", BUILD_PAGE),
]


def next_text():
    n = num
    return (f"The controller pair is the only part not yet in the building; Amazon's estimate is this week. Everything on this page becomes a measurement at the bench in the order the sheet's checks give: the ladder's five voltages with a meter before power ({f(n['ladder']['button'], 2)}, {f(n['ladder']['pan'], 2)}, {f(n['ladder']['tilt'], 2)}, {f(n['ladder']['pan+tilt'], 2)} V and 3.3 V), each motor's running and stall current with the head off the shafts (under 0.5 A stalled is the pass), the camera stream's draw (under 400 mA), the first charge watched with a meter in the cell's lead (about {f(I_CHARGE*1000)} mA), and the speaker scoped differentially under 2.7 V peak. "
            f"Firmware is the step after that, and the first of it is the XIAO alone on USB with the screen, exactly as the first Pocket AI began. The first measurements replace this page's estimates: the head's mass and balance, the stall current, the ladder's real voltages, the hours per charge.")


# ----------------------------------------------------------------------------- the outputs
PAGE_CSS = "figure svg{width:100%;height:auto} td,th{min-width:0} .src li{margin:4px 0;font-size:15px} h2{margin-top:34px}"


def page_html(figs):
    o = ['<title>Pocket AI Camera Physics</title>',
         '<meta name="claude:viewport-fit-sides" content="cover">',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
         "<style>" + STYLE + "</style>",
         f"<style>{PAGE_CSS}</style>",
         '<div class="wrap">',
         '<div class="masthead"><div class="eyebrow">Pocket AI Assistant &middot; camera build &middot; step 2: the science and engineering</div>',
         '<h1>Why the head looks before it turns</h1>',
         f'<div class="sub">The working behind Rev B, approved {APPROVED}: one cell and no boost, a lens and a screen that share a head, two gearboxes on one bridge chip, a head balanced on its axis in a brass yoke, three buttons on one ADC pin, a clock line on the pin that chatters at boot, an amplifier that must be told to sleep, and a frame that floats. Read after <a href="{BUILD_PAGE}" target="_blank" rel="noopener">Pocket AI with Camera</a>, the sheet every number here comes from. Written {WRITTEN}. Nothing measured yet. Source of truth: <code>pocket_ai_assistant_with_camera/docs/EDU.md</code>.</div></div>']
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
    o.append(f'<hr><p class="sub">Built by <code>docs/pages/gen/edu_page.py</code>, which also writes <code>docs/EDU.md</code>. Assumptions, each a number at the top of the script: a {f(FOV_H)}° lens; a {f(FACE_W*100)} cm face at {f(DIST)} m; {EYE_SHIFT_PX} px of eye travel for {f(EYE_LIMIT_DEG)}°; a {f(HEAD_G)} g head; {f(STALL_A*1000)} mA stall and {f(TORQUE_KGCM, 1)} kg·cm for the 12 mm motor class; {f(R_ON_MX*1000)} mΩ switches in the MX1508; a {f(R_PULLUP_INT/1000)} kΩ internal pull-up; {f(EFF_AMP*100)} % amplifier efficiency; {f(I_CHARGE*1000)} mA of charge; a boost converter at {f(EFF_BOOST*100)} % had there been one. The rest is datasheet or the sheet. Nothing here has been measured on the build.</p>')
    o.append("</div>")
    return "\n".join(o)


def page_md():
    o = ["# Why the head looks before it turns: the science and engineering behind the camera build", "",
         f"Step two of the house rule, written {WRITTEN} after Rev B was approved on {APPROVED}. Generated by `pages/gen/edu_page.py`; the page [`pages/edu-why.html`](pages/edu-why.html) carries the five figures. Read after [WIRING.md](WIRING.md) and [COMPONENTS.md](COMPONENTS.md). Nothing measured yet. Edit the script, not this file.", ""]
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
           ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#e4e4e4;--signal:#000;--signal-soft:#f1f1f1;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
           "html,body{background:#fff!important;color:#000!important;font-size:10pt!important;line-height:1.4} .wrap{max-width:none;padding:0} body{padding:0}"
           "h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
           "figure{width:84%;margin:10pt auto;padding:6pt;break-inside:avoid} figure svg{width:100%} figcaption{font-size:8pt} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid}"
           ".screen{fill:#000} .pupil{fill:#fff} .eye{fill:#000}</style>")
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "p.html"
        pdf = pathlib.Path(d) / "p.pdf"
        head, tail = page.rsplit("</style>", 1)
        src.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + css + tail, encoding="utf8")
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "edu-why.pdf"
        out.write_bytes(pdf.read_bytes())
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [ln for ln in info.splitlines() if ln.startswith("Pages")])


def preview_png(path):
    """Every figure stacked in one PNG, for checking by eye."""
    body = "".join(f"<div style='width:900px;margin:12px'>{fn()}</div>" for fn in FIGS.values())
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        (d / "f.html").write_text("<!doctype html><meta charset=utf-8><style>:root{--paper:#fff;--ink:#000;--ink-2:#333;--line:#ccc;--brass:#8F6114;--brass-soft:#F2E6D2;--signal:#0E5F7A;--signal-soft:#D9EAF1}body{margin:0;background:#fff}svg{width:900px;height:auto;display:block}</style>" + body)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--window-size=940,1900",
                        f"--screenshot={path}", f"file://{d / 'f.html'}"], check=True, capture_output=True, timeout=180)
    print("preview", path)


def main():
    derive()
    figs = {k: fn() for k, fn in FIGS.items()}
    page = page_html(figs)
    HTML_OUT.write_text(page, encoding="utf8")
    MD_OUT.write_text(page_md(), encoding="utf8")
    print("wrote", HTML_OUT, HTML_OUT.stat().st_size, "and", MD_OUT)
    for k in sorted(num):
        v = num[k]
        if isinstance(v, dict):
            print(f"  {k} = " + ", ".join(f"{kk}: {vv:.4g}" for kk, vv in v.items()))
        elif isinstance(v, tuple):
            print(f"  {k} = " + ", ".join(f"{x:.4g}" for x in v))
        else:
            print(f"  {k} = {v:.4g}")
    if "--pdf" in sys.argv:
        print_pdf(page)
    if "--png" in sys.argv:
        preview_png(sys.argv[sys.argv.index("--png") + 1])


if __name__ == "__main__":
    main()
