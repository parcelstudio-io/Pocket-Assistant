"""Desk satellite, step 2: the science and engineering behind the approved sheet (approved 2026-11-03).

Writes docs/pages/desk-satellite-physics.html, docs/pages/print/desk-satellite-physics.pdf (Letter portrait, black,
9.5 pt, figures at 70 % of the text width) and docs/PHYSICS.md (the same text without the figures).
Numbers come from build_page.py's D (dimensions), E (budget) and LIGHT (the light levels) so the pages cannot drift;
everything else is derived here and shown with its working. Edit this script, not the outputs."""
from __future__ import annotations

import math
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_page import D, E, L, LIGHT, STYLE, esc, panel_ma  # noqa: E402

PAGES = HERE.parent
DOCS = PAGES.parent
OUT = PAGES / "desk-satellite-physics.html"
PRINT = PAGES / "print"
APPROVED = "2026-11-03"
BUILD_PAGE = "https://claude.ai/artifact/3tn6UYHrUExfsSYK6KPV8T"

# ----------------------------------------------------------------------------- constants, each one a stated assumption
VT = 0.0257            # V, kT/q at 25 °C
N_IDEAL = 1.3          # diode ideality of a small monocrystalline cell
CELLS = 10             # cells in series on one panel
VOC_PANEL = 6.1        # V, one panel open circuit in full sun
ISC = E["isc"]         # mA, one panel (and so the series pair) short circuit in full sun (the listing's figure; see build_page.py)
LUX0 = E["lux_rated"]
RSH_PANEL = 20000.0    # Ω, the shunt leak the model gives one panel: a middling guess for cut cells (5 kΩ collapsed the room-light voltages below what such panels read)
TRACK = 0.33           # V, the charger holds its input this far above the cell (battery tracking)
D_IN = 0.20            # V, the board's input Schottky at tens of milliamps
VBAT = 3.8             # V, a half-full cell
V_OP = VBAT + TRACK + D_IN          # the pad voltage the charger pulls the wings to, half-full cell
V_OP_FULL = 4.2 + TRACK + D_IN      # the same with a full cell
HOURS = 6.0            # h, the charger's fixed safety timer
USB_W_IN = 5.0
I_USB = 0.5            # A, after the jumper is cut
H_CONV = 10.0          # W/m²K, still air plus radiation off a small black box
E_STEEL = 193e9        # Pa, 304 stainless
SY_STEEL = 500e6       # Pa, a low figure for drawn 304 rod
ROD = 1.5e-3           # m
RAIL = 3.3
PIN_R = 25.0           # Ω, the C3's output driver at a few milliamps
D_SS14 = 0.15          # V, the SS14 at one milliamp
LDO_DROP = 0.1         # V, the SuperMini's regulator headroom at these currents
VF_CHIP = 2.75         # V, a warm-white 0805 at a few milliamps
SLOPE_CHIP = 0.085     # V per e-fold of current for a white LED near its working point (about 200 mV per decade)
SLOPE_FIL = 0.09       # the hologram's figure for the filament
VF_FIL = 2.4           # V, the hologram's filament at 10 mA
R_CHIP, R_FIL = 100.0, 68.0
C3_MIN = 3.0           # V, the chip's specified floor
BOOT_MA, BOOT_S, DEEP_MA = 30.0, 0.25, 0.005
BLINK_S, PERIOD_S = 0.1, 2.0
BLOCH_S = 0.1          # s, the eye's summation time in dim light

# ----------------------------------------------------------------------------- the wings as diodes in the light
VT_CELL = N_IDEAL * VT
I0 = ISC / (math.exp(VOC_PANEL / (CELLS * VT_CELL)) - 1)   # mA, one cell's saturation current (a string shares it)


def string_i(v, lux, daylight, n_panels):
    """mA from n_panels in series at v volts: light current, minus the diode, minus the shunt leak."""
    cells, rsh = CELLS * n_panels, RSH_PANEL * n_panels
    return panel_ma(lux, daylight) - I0 * (math.exp(v / (cells * VT_CELL)) - 1) - v / rsh * 1000


def voc(lux, daylight, n_panels):
    lo, hi = 0.0, 16.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if string_i(mid, lux, daylight, n_panels) > 0:
            lo = mid
        else:
            hi = mid
    return lo


def mpp_ma_into_cell(lux, daylight):
    """What a switching charger tracking the pair's maximum-power point would push into the cell, at 90 %."""
    best = 0.0
    v = 0.0
    while v < 16:
        p = v * max(string_i(v, lux, daylight, 2), 0)
        best = max(best, p)
        v += 0.02
    return 0.9 * best / VBAT


num = {}
num["voc_pair_sun"] = voc(LUX0, True, 2)
num["voc_one_sun"] = voc(LUX0, True, 1)
num["voc_pair_room"] = voc(500, False, 2)
num["voc_one_room"] = voc(500, False, 1)
num["voc_pair_window"] = voc(3000, True, 2)
num["voc_one_window"] = voc(3000, True, 1)
num["mv_per_decade"] = N_IDEAL * VT * math.log(10) * 1000
num["leak_ma"] = V_OP / (2 * RSH_PANEL) * 1000
num["series"] = [max(string_i(V_OP, lux, dl, 2), 0) for _, lux, dl, _ in LIGHT]
num["parallel"] = [2 * max(string_i(V_OP, lux, dl, 1), 0) for _, lux, dl, _ in LIGHT]
num["net_series"] = [max(i - E["bq_in"], 0) for i in num["series"]]
num["net_parallel"] = [max(i - E["bq_in"], 0) for i in num["parallel"]]
num["series_full"] = [max(string_i(V_OP_FULL, lux, dl, 2), 0) for _, lux, dl, _ in LIGHT]
num["parallel_full"] = [2 * max(string_i(V_OP_FULL, lux, dl, 1), 0) for _, lux, dl, _ in LIGHT]
num["stored"] = [min(n * HOURS, E["cell_usable"]) for n in num["net_series"]]
num["mppt_window"] = mpp_ma_into_cell(3000, True)
num["mppt_sun"] = mpp_ma_into_cell(LUX0, True)
num["mppt_x"] = num["mppt_window"] / num["series"][2]
num["heat_sun_W"] = (TRACK + D_IN) * ISC / 1000
num["heat_plain_W"] = (num["voc_pair_sun"] - VBAT) * ISC / 1000
num["heat_usb_W"] = (USB_W_IN - VBAT) * I_USB
num["box_cm2"] = 2 * (D["box_w"] * D["box_d"] + D["box_w"] * D["box_h"] + D["box_d"] * D["box_h"]) / 100
num["box_dT"] = num["heat_usb_W"] / (H_CONV * num["box_cm2"] / 1e4)
num["usb_hours"] = E["cell_mah"] / (I_USB * 1000) + 0.3
num["beacon_day"] = E["blink"] * 24
num["glow_day"] = E["glow"] * 24
num["deep_avg"] = DEEP_MA + E["ldo"] + E["en_pullup"] + E["bq_batt"] + BOOT_MA * BOOT_S / PERIOD_S + E["led_on"] * E["blink_duty"]
num["t_cross"] = BOOT_MA * BOOT_S / (E["c3_sleep"] - DEEP_MA)


def crossing(rail, r, vf, i_ref, slope):
    """Where the LED's curve (i_ref mA at vf, e-fold every `slope` volts) meets the resistor's line from `rail`."""
    lo, hi = 0.0, rail
    for _ in range(60):
        v = (lo + hi) / 2
        if i_ref * math.exp((v - vf) / slope) < (rail - v) / (r + PIN_R) * 1000:
            lo = v
        else:
            hi = v
    v = (lo + hi) / 2
    return v, (rail - v) / (r + PIN_R) * 1000


I_CHIP_REF = (RAIL - VF_CHIP) / (R_CHIP + PIN_R) * 1000   # the chip's curve is pinned at 4.4 mA at 2.75 V
I_FIL_REF = (RAIL - VF_FIL) / (R_FIL + PIN_R) * 1000      # the filament's at 9.7 mA at 2.4 V
num["v_chip"], num["i_chip"] = crossing(RAIL, R_CHIP, VF_CHIP, I_CHIP_REF, SLOPE_CHIP)
num["v_fil"], num["i_fil"] = crossing(RAIL, R_FIL, VF_FIL, I_FIL_REF, SLOPE_FIL)
num["vf_chip_20"] = VF_CHIP + SLOPE_CHIP * math.log(20 / I_CHIP_REF)
num["cell_rail"] = RAIL + LDO_DROP + D_SS14           # the cell voltage above which the rail is a true 3.3 V
num["cell_floor"] = C3_MIN + LDO_DROP + D_SS14        # the cell voltage at which the chip reaches its 3.0 V floor
num["rail_low"] = 3.3 - LDO_DROP - D_SS14             # the rail with a 3.3 V cell
num["v_chip_low"], num["i_chip_low"] = crossing(num["rail_low"], R_CHIP, VF_CHIP, I_CHIP_REF, SLOPE_CHIP)
num["v_fil_low"], num["i_fil_low"] = crossing(num["rail_low"], R_FIL, VF_FIL, I_FIL_REF, SLOPE_FIL)
num["chip_mcd"] = 150 * (num["i_chip"] / 20) ** 0.9  # a 150 mcd part at 20 mA, a little better than linear below it
num["chip_lux_3m"] = num["chip_mcd"] / 1000 / 9
num["venus_x"] = num["chip_lux_3m"] / 1.4e-4
I_ROD = math.pi * ROD ** 4 / 64
L_POST = D["post_free"] / 1000
num["euler_N"] = math.pi ** 2 * E_STEEL * I_ROD / (2 * L_POST) ** 2
num["load_N"] = D["top_g"] / 1000 * 9.81
num["margin"] = num["euler_N"] / num["load_N"]
k_post = 3 * E_STEEL * I_ROD / L_POST ** 3
num["defl_mm_per_N"] = 1000 / k_post
num["f_sway"] = math.sqrt(k_post / (D["top_g"] / 1000)) / (2 * math.pi)
num["W_N"] = (D["top_g"] + D["base_g"]) / 1000 * 9.81
num["f_tip"] = num["W_N"] * (D["disc_d"] / 2) / D["height"]
num["f_set"] = SY_STEEL * I_ROD / (ROD / 2 * L_POST)
num["boom_sag"] = (D["panel_g"] / 1000 * 9.81) * (D["panel"] / 2000 + 0.002) ** 3 / (3 * E_STEEL * I_ROD) * 1000
num["disc_pct"] = D["disc_g"] / (D["top_g"] + D["base_g"]) * 100
num["chip_slope_mv"] = SLOPE_CHIP * math.log(10) * 1000

STORED_SHORT = ["desk", "dull window", "bright window", "overcast sill", "sun"]


def f(x, d=0):
    return f"{x:.{d}f}"


# ----------------------------------------------------------------------------- figure helpers (the hologram's)
def T(x, y, s, cls="fn", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


FIG_CSS = ("<style>"
           ".ink{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
           ".thin{fill:none;stroke:var(--ink);stroke-width:1.1;stroke-linecap:round}"
           ".grey{fill:none;stroke:var(--ink-2);stroke-width:1.1;stroke-dasharray:4 3}"
           ".ray{fill:none;stroke:var(--warn);stroke-width:1.6}"
           ".rayhead{fill:var(--warn);stroke:none}"
           ".glass{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.6}"
           ".diag{fill:none;stroke:var(--signal);stroke-width:1.4;stroke-dasharray:6 4}"
           ".solid{fill:var(--ink);stroke:none}"
           ".soft{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.2}"
           ".band{fill:var(--brass-soft);stroke:none}"
           ".bar{fill:var(--ink);stroke:none}"
           ".bar2{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1}"
           ".h{font:700 13px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".lab{font:700 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".num{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink)}"
           "</style>")


def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{FIG_CSS}{body}</svg>'


def arrow(x0, y0, x1, y1, cls="ray"):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - 9 * math.cos(ang), y1 - 9 * math.sin(ang)
    px, py = 4.5 * math.sin(ang), -4.5 * math.cos(ang)
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="{cls}"/>'
            f'<path d="M{x1:.1f},{y1:.1f} L{hx+px:.1f},{hy+py:.1f} L{hx-px:.1f},{hy-py:.1f} z" class="rayhead"/>')


def axes(ox, oy, w, h):
    return f'<line x1="{ox}" y1="{oy}" x2="{ox+w}" y2="{oy}" class="ink"/><line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-h}" class="ink"/>'


def poly(pts, cls):
    return '<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" class="{cls}"/>'


# ----------------------------------------------------------------------------- the figures
def fig_iv():
    ox, oy, w, h = 64, 262, 440, 196
    X = lambda v: ox + v / 13.0 * w                                   # noqa: E731
    Y = lambda i: oy - (math.log10(max(i, 0.1)) + 1) / 3.0 * h        # noqa: E731
    o = [T(20, 24, "The wings' current against their voltage, in three lights", "h"), axes(ox, oy, w, h)]
    for v in range(0, 14, 2):
        o.append(f'<line x1="{X(v):.1f}" y1="{oy}" x2="{X(v):.1f}" y2="{oy+5}" class="thin"/>')
        o.append(T(X(v), oy + 18, f"{v}", "num", "middle"))
    o.append(T(ox + w / 2, oy + 34, "volts at the charger's pad", "fn", "middle"))
    for i in (0.1, 1, 10, 100):
        o.append(f'<line x1="{ox-5}" y1="{Y(i):.1f}" x2="{ox}" y2="{Y(i):.1f}" class="thin"/>')
        o.append(T(ox - 8, Y(i) + 4, f"{i:g}", "num", "end"))
    o.append(T(ox - 8, oy - h - 6, "mA", "fn", "end"))
    o.append(f'<rect x="{X(V_OP):.1f}" y="{oy-h}" width="{X(V_OP_FULL)-X(V_OP):.1f}" height="{h}" class="band"/>')
    o.append(T(20, 44, f"The grey band is where the charger holds the wings, {V_OP:.1f} to {V_OP_FULL:.1f} V; it takes whatever current flows there.", "fn"))
    o.append(f'<line x1="{ox}" y1="{Y(E["bq_in"]):.1f}" x2="{ox+w}" y2="{Y(E["bq_in"]):.1f}" class="grey"/>')
    o.append(T(ox + w - 4, Y(E["bq_in"]) - 5, f"{E['bq_in']:.2f} mA: what the charger eats first", "fn", "end"))

    def curve(lux, dl, n, cls):
        pts, v = [], 0.0
        while v <= 15:
            i = string_i(v, lux, dl, n)
            if i < 0.1:
                break
            pts.append((X(v), Y(i)))
            v += 0.05
        return poly(pts, cls)

    for lux, dl, lab in ((LUX0, True, f"sun, {LUX0:,} lux"), (3000, True, "bright window, 3 000 lux"), (500, False, "desk, 500 lux of LED light")):
        o.append(curve(lux, dl, 2, "ink"))
        isc = panel_ma(lux, dl)
        o.append(T(X(0.3), Y(isc) - 6, f"{lab}: {isc:.2g} mA", "lab"))
        i_op = string_i(V_OP, lux, dl, 2)
        if i_op > 0.1:
            o.append(f'<circle cx="{X(V_OP):.1f}" cy="{Y(i_op):.1f}" r="4" class="solid"/>')
    for lux, dl in ((3000, True), (500, False)):
        o.append(curve(lux, dl, 1, "grey"))
    o.append(T(ox + w - 4, oy - 8, "dashed: one wing alone, in the same two lights", "fn", "end"))
    return svg(660, 306, "".join(o), "The wings' current and voltage")


def fig_heat():
    o = [T(20, 24, "Heat in the charger, three ways", "h")]
    rows = [(f"the wings in sun through the tracking loop: ({TRACK:.2f} + {D_IN:.1f}) V × {ISC:.0f} mA", num["heat_sun_W"]),
            (f"the same wings into a plain linear charger: ({num['voc_pair_sun']:.1f} − {VBAT}) V × {ISC:.0f} mA", num["heat_plain_W"]),
            (f"USB-C at {I_USB*1000:.0f} mA: ({USB_W_IN:.0f} − {VBAT}) V × {I_USB} A", num["heat_usb_W"])]
    for i, (lab, wv) in enumerate(rows):
        y = 44 + i * 52
        o.append(T(20, y + 12, lab, "fn"))
        bw = max(wv / 0.8 * 440, 3)
        o.append(f'<rect x="20" y="{y+18}" width="{bw:.1f}" height="16" class="bar"/>')
        o.append(T(20 + bw + 8, y + 31, f"{wv:.2f} W" if wv >= 0.1 else f"{wv*1000:.0f} mW", "num"))
    lines = (f"{num['heat_usb_W']:.1f} W inside a closed box with {num['box_cm2']:.0f} cm² of skin warms it about {num['box_dT']:.0f} °C above the room;",
             "the chip runs hotter than its board and throttles itself at a 125 °C junction, which it never reaches here.",
             f"On the wings the loop keeps the drop at {TRACK:.2f} V in the chip and {D_IN:.1f} in the board's Schottky: nothing to feel.")
    for i, line in enumerate(lines):
        o.append(T(20, 214 + i * 14, line, "fn"))
    return svg(620, 258, "".join(o), "Heat in the charger")


def fig_day():
    ox, oy, w, h = 60, 236, 400, 176
    Y = lambda m: oy - min(m, 200) / 200 * h                           # noqa: E731
    o = [T(20, 24, "What a day stores at five light levels, against what a day costs", "h"), axes(ox, oy, w, h)]
    for m in (0, 50, 100, 150, 200):
        o.append(f'<line x1="{ox-5}" y1="{Y(m):.1f}" x2="{ox}" y2="{Y(m):.1f}" class="thin"/>')
        o.append(T(ox - 8, Y(m) + 4, f"{m}", "num", "end"))
    o.append(T(ox - 8, oy - h - 8, "mAh", "fn", "end"))
    for k, (where, lux, dl, note) in enumerate(LIGHT):
        x = ox + 22 + k * 82
        s = num["stored"][k]
        if s > 200:
            o.append(f'<rect x="{x}" y="{Y(200)}" width="40" height="{h}" class="bar"/>')
            o.append(f'<line x1="{x-4}" y1="{Y(170)}" x2="{x+44}" y2="{Y(180)}" class="thin" style="stroke:var(--paper);stroke-width:4"/>')
            o.append(T(x + 20, Y(200) - 6, f"{s:.0f}: six hours of sun", "num", "middle"))
        else:
            o.append(f'<rect x="{x}" y="{Y(s):.1f}" width="40" height="{oy - Y(s):.1f}" class="bar"/>')
            if s > 0:
                o.append(T(x + 20, Y(s) - 6, f"{s:.0f}", "num", "middle"))
        o.append(T(x + 20, oy + 16, STORED_SHORT[k], "fn", "middle"))
        o.append(T(x + 20, oy + 30, f"{lux:,} lux", "fn", "middle"))
    for m, lab in ((num["beacon_day"], f"beacon mode: {num['beacon_day']:.0f} mAh a day"), (num["glow_day"], f"glow mode: {num['glow_day']:.0f} mAh a day")):
        o.append(f'<line x1="{ox}" y1="{Y(m):.1f}" x2="{ox+w}" y2="{Y(m):.1f}" class="grey"/>')
        o.append(T(ox + w + 8, Y(m) + 4, lab, "fn"))
    o.append(T(ox + w + 8, Y(num["glow_day"]) + 18, "(the pool dimmed to 3 mA)", "fn"))
    o.append(T(20, 278, f"stored = (the pair's current at {V_OP:.1f} V − {E['bq_in']:.2f} mA) × {HOURS:.0f} h; the model's leak is in, the sheet's table left it out.", "fn"))
    return svg(660, 290, "".join(o), "A day stored against a day spent")


def fig_sleep():
    ox, oy, w, h = 60, 196, 440, 150
    X = lambda t: ox + t / 4.0 * w                                     # noqa: E731
    Y = lambda i: oy - i / 35.0 * h                                    # noqa: E731
    o = [T(20, 24, "Two blinks, two ways of waiting between them", "h"), axes(ox, oy, w, h)]
    for t in range(0, 5):
        o.append(f'<line x1="{X(t)}" y1="{oy}" x2="{X(t)}" y2="{oy+5}" class="thin"/>')
        o.append(T(X(t), oy + 18, f"{t} s", "num", "middle"))
    for i in (0, 10, 20, 30):
        o.append(f'<line x1="{ox-5}" y1="{Y(i):.1f}" x2="{ox}" y2="{Y(i):.1f}" class="thin"/>')
        o.append(T(ox - 8, Y(i) + 4, f"{i}", "num", "end"))
    o.append(T(ox - 8, oy - h - 6, "mA", "fn", "end"))
    base = E["sleep"]
    on = base + E["led_on"]
    light = [(X(0), Y(base))]
    deep = [(X(0), Y(DEEP_MA))]
    for t0 in (0.6, 2.6):
        light += [(X(t0), Y(base)), (X(t0), Y(on)), (X(t0 + BLINK_S), Y(on)), (X(t0 + BLINK_S), Y(base))]
        tb = t0 - BOOT_S
        deep += [(X(tb), Y(DEEP_MA)), (X(tb), Y(BOOT_MA)), (X(t0), Y(BOOT_MA)), (X(t0), Y(on)), (X(t0 + BLINK_S), Y(on)), (X(t0 + BLINK_S), Y(DEEP_MA))]
    light.append((X(4), Y(base)))
    deep.append((X(4), Y(DEEP_MA)))
    o.append(poly(deep, "grey"))
    o.append(poly(light, "ink"))
    o.append(T(X(0.63), Y(BOOT_MA) + 4, f"{BOOT_S*1000:.0f} ms at {BOOT_MA:.0f} mA: a reboot", "fn"))
    o.append(T(X(0.73), Y(on) - 2, f"the blink, {BLINK_S*1000:.0f} ms", "fn"))
    o.append(T(X(1.25), Y(base) - 6, f"{E['c3_sleep']:.2f} mA between", "fn"))
    rx = ox + w + 10
    legend = (("solid: light sleep", "lab"), (f"{E['c3_sleep']:.2f} mA between blinks,", "fn"), (f"{E['blink']:.2f} mA average", "num"), ("", "fn"),
              ("dashed: deep sleep", "lab"), (f"{DEEP_MA*1000:.0f} µA between, but a", "fn"), (f"{BOOT_S*1000:.0f} ms reboot at {BOOT_MA:.0f} mA", "fn"),
              ("for each blink:", "fn"), (f"{num['deep_avg']:.1f} mA average", "num"), ("", "fn"), ("deep sleep wins only", "fn"), (f"past a {num['t_cross']:.0f} s period", "fn"))
    for i, (txt, cls) in enumerate(legend):
        if txt:
            o.append(T(rx, 54 + i * 13, txt, cls))
    return svg(660, 236, "".join(o), "Light sleep against deep sleep")


def fig_led():
    o = [T(20, 24, f"The beacon chip through {R_CHIP:.0f} Ω", "h"), T(340, 24, f"The filament through {R_FIL:.0f} Ω", "h")]

    def panel(x0, vf, slope, i_ref, r):
        ox, oy, w, h = x0 + 30, 226, 240, 170
        X = lambda v: ox + v / 3.6 * w                                 # noqa: E731
        Y = lambda i: oy - i / 20.0 * h                                # noqa: E731
        p = [axes(ox, oy, w, h)]
        for v in (1, 2, 3):
            p.append(f'<line x1="{X(v):.1f}" y1="{oy}" x2="{X(v):.1f}" y2="{oy+5}" class="thin"/>')
            p.append(T(X(v), oy + 18, f"{v} V", "num", "middle"))
        for i in (5, 10, 15, 20):
            p.append(f'<line x1="{ox-5}" y1="{Y(i):.1f}" x2="{ox}" y2="{Y(i):.1f}" class="thin"/>')
            p.append(T(ox - 8, Y(i) + 4, f"{i}", "num", "end"))
        p.append(T(ox - 8, oy - h - 6, "mA", "fn", "end"))
        pts = []
        for k in range(0, 361):
            v = k / 100
            i = i_ref * math.exp((v - vf) / slope)
            if i > 20:
                break
            pts.append((X(v), Y(i)))
        p.append(poly(pts, "ink"))
        ops = []
        for rail, cls in ((RAIL, "thin"), (num["rail_low"], "grey")):
            i_at0 = rail / (r + PIN_R) * 1000
            v_top = rail - 20 * (r + PIN_R) / 1000 if i_at0 > 20 else 0
            i_top = 20 if i_at0 > 20 else i_at0
            p.append(f'<line x1="{X(rail):.1f}" y1="{oy}" x2="{X(v_top):.1f}" y2="{Y(i_top):.1f}" class="{cls}"/>')
            v_op, i_op = crossing(rail, r, vf, i_ref, slope)
            ops.append(i_op)
            p.append(f'<circle cx="{X(v_op):.1f}" cy="{Y(i_op):.1f}" r="4" class="solid"/>')
        p.append(T(X(RAIL) + 2, oy - 6, "3.3 V", "num", "end"))
        p.append(T(X(0.1), Y(20) - 5, "the pin's 20 mA ceiling", "fn"))
        p.append(T(X(0.1), Y(ops[0]) - 4, f"{ops[0]:.1f} mA at a 3.3 V rail", "lab"))
        p.append(T(X(0.1), Y(ops[0]) + 10, f"{ops[1]:.1f} mA at a {num['rail_low']:.2f} V rail", "fn"))
        return "".join(p)

    o.append(panel(20, VF_CHIP, SLOPE_CHIP, I_CHIP_REF, R_CHIP))
    o.append(panel(340, VF_FIL, SLOPE_FIL, I_FIL_REF, R_FIL))
    o.append(T(20, 258, "The curve is the LED, the line is the resistor plus the pin's 25 Ω; they cross at the current.", "fn"))
    o.append(T(20, 272, f"Dashed: the same resistor from a {num['rail_low']:.2f} V rail (cell at 3.3 V). Steeper curve, more spread from chip to chip.", "fn"))
    return svg(640, 284, "".join(o), "Two load lines")


def fig_kelvin():
    x0, w = 50, 560
    X = lambda k: x0 + (k - 1500) / 5500 * w                           # noqa: E731
    y = 150
    o = [T(20, 24, "Where the two lights sit on the glowing-body line", "h")]
    o.append(f'<line x1="{x0}" y1="{y}" x2="{x0+w}" y2="{y}" class="ink"/>')
    for k in range(2000, 7001, 1000):
        o.append(f'<line x1="{X(k):.1f}" y1="{y}" x2="{X(k):.1f}" y2="{y+6}" class="thin"/>')
        o.append(T(X(k), y + 20, f"{k:,} K", "num", "middle"))
    o.append(T(X(1500), y + 36, "redder", "fn", "start"))
    o.append(T(X(7000), y + 36, "bluer", "fn", "end"))
    marks = [(1850, "candle flame", 1, "fn"), (2200, "the pool", 2, "lab"), (2700, "tungsten bulb", 1, "fn"),
             (3000, "the beacon", 2, "lab"), (4000, "the room's LED tubes", 1, "fn"), (5500, "midday sun", 2, "fn"), (6500, "overcast sky", 1, "fn")]
    for k, lab, row, cls in marks:
        top = y - (28 if row == 1 else 64)
        o.append(f'<line x1="{X(k):.1f}" y1="{y}" x2="{X(k):.1f}" y2="{top+6}" class="thin"/>')
        o.append(f'<circle cx="{X(k):.1f}" cy="{y}" r="3.5" class="solid"/>')
        o.append(T(X(k), top, lab, cls, "middle"))
    o.append(f'<path d="M{X(2200):.1f},{y+54} L{X(2200):.1f},{y+60} L{X(3000):.1f},{y+60} L{X(3000):.1f},{y+54}" class="thin"/>')
    o.append(T(50, y + 76, "brass under room light reads between the brackets: polished near 3 000 K, shaded or old near 2 200", "fn"))
    o.append(T(20, y + 100, "Brass reflects the warm end best, so the pool on the base reads a little more golden than the filament's 2 200 K.", "fn"))
    return svg(660, 262, "".join(o), "Colour temperature")


def fig_rail():
    ox, oy, w, h = 70, 206, 420, 164
    X = lambda v: ox + (v - 3.0) / 1.2 * w                             # noqa: E731
    Y = lambda v: oy - (v - 2.5) / 1.8 * h                             # noqa: E731
    o = [T(20, 24, "What the controller's rail does as the cell empties", "h"), axes(ox, oy, w, h)]
    soc = {3.0: 0, 3.2: 1, 3.4: 5, 3.6: 15, 3.8: 50, 4.0: 80, 4.2: 100}
    for v, pct in soc.items():
        o.append(f'<line x1="{X(v):.1f}" y1="{oy}" x2="{X(v):.1f}" y2="{oy+5}" class="thin"/>')
        o.append(T(X(v), oy + 18, f"{v:.1f}", "num", "middle"))
        o.append(T(X(v), oy + 34, f"{pct} %", "fn", "middle"))
    o.append(T(ox + w / 2, oy + 52, "cell voltage, and about how much of the cell is left at it", "fn", "middle"))
    for v in (2.5, 3.0, 3.5, 4.0):
        o.append(f'<line x1="{ox-5}" y1="{Y(v):.1f}" x2="{ox}" y2="{Y(v):.1f}" class="thin"/>')
        o.append(T(ox - 8, Y(v) + 4, f"{v:.1f}", "num", "end"))
    o.append(T(ox - 8, oy - h - 6, "V", "fn", "end"))
    o.append(poly([(X(3.0), Y(3.0)), (X(4.2), Y(4.2))], "grey"))
    rail = [(X(v / 100), Y(min(RAIL, v / 100 - D_SS14 - LDO_DROP))) for v in range(300, 421, 2)]
    o.append(poly(rail, "ink"))
    o.append(f'<line x1="{ox}" y1="{Y(C3_MIN):.1f}" x2="{ox+w}" y2="{Y(C3_MIN):.1f}" class="grey"/>')
    o.append(f'<circle cx="{X(num["cell_floor"]):.1f}" cy="{Y(C3_MIN):.1f}" r="4" class="solid"/>')
    o.append(f'<circle cx="{X(num["cell_rail"]):.1f}" cy="{Y(RAIL):.1f}" r="4" class="solid"/>')
    o.append(T(X(4.2) - 4, Y(4.2) - 8, "the cell itself (grey)", "fn", "end"))
    o.append(T(X(4.2) - 4, Y(RAIL) + 16, f"the 3.3 V rail, true above a {num['cell_rail']:.2f} V cell", "lab", "end"))
    o.append(T(X(4.2) - 4, Y(C3_MIN) + 16, f"the chip's 3.0 V floor: a {num['cell_floor']:.2f} V cell, 1 to 5 % left", "fn", "end"))
    o.append(T(20, oy + 70, f"The 5V pin sits {D_SS14:.2f} V under the cell (not drawn) and the regulator wants {LDO_DROP:.1f} V more,", "fn"))
    o.append(T(20, oy + 84, f"so the rail is the cell less {D_SS14 + LDO_DROP:.2f} V until that reaches 3.3 V, and 3.3 V from there up.", "fn"))
    return svg(640, 302, "".join(o), "The rail and the cell")


def fig_post():
    s = 1.0
    bx, by = 170, 262
    o = [T(20, 24, "The post as a spring, the base as the fuse", "h")]
    o.append(f'<rect x="{bx - D['disc_d']/2*s:.1f}" y="{by - D['disc_t']*s:.1f}" width="{D['disc_d']*s:.1f}" height="{D['disc_t']*s:.1f}" class="soft"/>')
    o.append(f'<rect x="{bx - D['hub_d']/2*s:.1f}" y="{by - D['z_hub']*s:.1f}" width="{D['hub_d']*s:.1f}" height="{D['hub_h']*s:.1f}" class="soft"/>')
    top = by - D["z_box"] * s
    bent = num["defl_mm_per_N"] * s
    o.append(f'<path d="M{bx},{by - D['z_hub']*s:.1f} C{bx},{top + 40:.1f} {bx + bent*0.3:.1f},{top + 20:.1f} {bx + bent:.1f},{top:.1f}" class="ink" style="stroke-width:2.6"/>')
    o.append(f'<line x1="{bx}" y1="{by - D['z_hub']*s:.1f}" x2="{bx}" y2="{top:.1f}" class="grey"/>')
    o.append(f'<rect x="{bx + bent - D['box_w']/2*s:.1f}" y="{top - D['box_h']*s:.1f}" width="{D['box_w']*s:.1f}" height="{D['box_h']*s:.1f}" class="solid"/>')
    for sgn in (-1, 1):
        x1 = bx + bent + sgn * D["box_w"] / 2 * s
        x2 = x1 + sgn * (D["yoke_l"] + D["gap"] + D["panel"]) * s
        o.append(f'<line x1="{x1:.1f}" y1="{top - D['box_h']/2*s:.1f}" x2="{x2:.1f}" y2="{top - D['box_h']/2*s:.1f}" class="ink" style="stroke-width:3"/>')
    ya = top - D["box_h"] * s - 12
    o.append(arrow(bx + bent + 66, ya, bx + bent + 30, ya))
    o.append(T(bx + bent + 72, ya - 4, "1 N sideways at the top", "lab"))
    o.append(T(bx + bent + 72, ya + 10, f"bends it {num['defl_mm_per_N']:.0f} mm, drawn to scale", "fn"))
    cy = by - D["com"] * s
    o.append(f'<circle cx="{bx}" cy="{cy:.1f}" r="4.5" class="solid"/>')
    o.append(T(bx + 12, cy + 4, f"centre of mass {D['com']:.0f} mm up", "fn"))
    o.append(f'<line x1="{bx}" y1="{cy:.1f}" x2="{bx + D['disc_d']/2*s:.1f}" y2="{by:.1f}" class="grey"/>')
    o.append(f'<circle cx="{bx + D['disc_d']/2*s:.1f}" cy="{by:.1f}" r="3.5" class="solid"/>')
    o.append(T(bx + D["disc_d"] / 2 * s + 8, by - 4, f"pivots here at {D['tip_deg']}°", "fn"))
    tx = 420
    rows = [("as a column", f"carries {num['load_N']:.2f} N,", f"buckles at {num['euler_N']:.1f} N: {num['margin']:.0f}× margin"),
            ("as a spring", f"{num['defl_mm_per_N']:.0f} mm per newton at the top;", f"sways at {num['f_sway']:.1f} Hz when nudged"),
            ("to tip it over", f"{num['f_tip']:.2f} N at the top,", "over the edge of the base"),
            ("to bend it for good", f"about {num['f_set']:.1f} N at the top:", "it tips first"),
            ("each boom", f"{D['panel_g']:.0f} g on {D['panel']:.0f} mm,", f"sags {num['boom_sag']:.2f} mm")]
    for i, (a_, b_, c_) in enumerate(rows):
        yy = 60 + i * 46
        o.append(T(tx, yy, a_, "lab"))
        o.append(T(tx, yy + 14, b_, "fn"))
        o.append(T(tx, yy + 28, c_, "fn"))
    return svg(640, 296, "".join(o), "The post")


def fig_blink():
    ox, oy, w, h = 60, 150, 260, 100
    X = lambda ms: ox + (math.log10(ms) - 0) / 3 * w                   # noqa: E731
    o = [T(20, 24, "How bright a flash looks against how long it lasts", "h"), T(360, 24, "The beacon's two seconds", "h"), axes(ox, oy, w, h)]
    for ms, lab in ((1, "1 ms"), (10, "10"), (100, "100"), (1000, "1 s")):
        o.append(f'<line x1="{X(ms):.1f}" y1="{oy}" x2="{X(ms):.1f}" y2="{oy+5}" class="thin"/>')
        o.append(T(X(ms), oy + 18, lab, "num", "middle"))
    pts = []
    for k in range(0, 301):
        ms = 10 ** (k / 100)
        b = min(ms / (BLOCH_S * 1000), 1.0)
        pts.append((X(ms), oy - b * h))
    o.append(poly(pts, "ink"))
    o.append(f'<circle cx="{X(100):.1f}" cy="{oy - h:.1f}" r="4" class="solid"/>')
    o.append(T(X(100) - 8, oy - h - 8, "100 ms: as bright as steady light", "fn", "end"))
    o.append(f'<circle cx="{X(10):.1f}" cy="{oy - 0.1*h:.1f}" r="4" class="solid"/>')
    o.append(T(X(10) + 8, oy - 0.1 * h - 6, "10 ms: a tenth", "fn"))
    o.append(T(ox - 8, oy - h + 4, "full", "fn", "end"))
    o.append(T(ox - 8, oy + 4, "dark", "fn", "end"))
    px, py, pw = 360, 60, 260
    path = f"M{px},{py+40}"
    for k in range(2):
        xs = px + k * pw / 2 + 20
        path += f" L{xs},{py+40} L{xs},{py} L{xs + pw/2*0.05:.1f},{py} L{xs + pw/2*0.05:.1f},{py+40}"
    path += f" L{px+pw},{py+40}"
    o.append(f'<path d="{path}" class="ink"/>')
    o.append(T(px, py + 60, f"{BLINK_S*1000:.0f} ms on, {PERIOD_S - BLINK_S:.1f} s off: 5 % of the time,", "fn"))
    o.append(T(px, py + 74, "all of the brightness, a twentieth of the power.", "fn"))
    o.append(T(px, py + 98, "Steady modes dim by PWM at 5 kHz, far above", "fn"))
    o.append(T(px, py + 112, "the 60 Hz the eye can follow: no flicker.", "fn"))
    return svg(640, 182, "".join(o), "Bloch's law and the blink")


# ----------------------------------------------------------------------------- the text
def chapters():
    """List of (heading, [paragraphs or ('fig', svg, caption)])."""
    k_room, k_dull, k_bright, k_sill, k_sun = range(5)
    return [
        ("The whole thing in one sentence", [
            f"Two wings make a few milliamps in daylight; a charger that follows a weak panel instead of collapsing it feeds a {E['cell_mah']} mAh cell; a controller asleep between blinks spends {E['blink']:.2f} mA on a warm chip at the corner and, when asked, {E['pool_dim']:.0f} more on an amber pool below.",
            "Everything on the approved sheet follows from that: why two wings in series, why this charger and not a cleverer one, why the cell is never rushed, why light sleep and not deep, why a resistor on each light, why one 1.5 mm post can carry it all. This page takes each in the order the sheet made them and shows the working.",
        ]),
        ("What a silicon cell does in room light", [
            f"A solar cell is a diode in the light. Light knocks electrons loose at a rate proportional to the light, so the short-circuit current is linear in lux: the listing's {ISC:.0f} mA in full sun (100 000 lux, the listing's full-sun figure) is {panel_ma(3000):.1f} mA at a bright window (3 000 lux) and {panel_ma(500, False):.2f} mA on a desk under 500 lux of LED light. Silicon counts LED light at only 0.65 of daylight per lux, because an LED spectrum has none of the deep red and infrared that silicon converts best.",
            f"The voltage is the diode's, and it climbs with the logarithm of the light: about {num['mv_per_decade']:.0f} mV per tenfold per cell for cells like these. Ten cells that open at {VOC_PANEL} V in sun open at {num['voc_one_room']:.1f} V on the desk. The leak every small cut cell has (the model gives each panel {RSH_PANEL/1000:.0f} kΩ) pulls the dim-light voltage down further and takes about {num['leak_ma']:.1f} mA off the top at the charger's voltage, whatever the light.",
            ("fig", fig_iv(), f"The series pair in three lights, current on a log scale. The band is where the charger holds the wings; the dots are what it gets there: {num['series'][k_sun]:.0f}, {num['series'][k_bright]:.1f} and {num['series'][k_room]:.1f} mA, the last below the {E['bq_in']:.2f} mA line that the charger spends on itself. Dashed: one wing alone opens at {num['voc_one_room']:.1f} V on the desk and {num['voc_one_window']:.1f} V at the window, under the band or just past it."),
            f"The charger does not care about the voltage above its line. It pulls the wings down to {V_OP:.1f} to {V_OP_FULL:.1f} V (the cell, plus {TRACK:.2f} V of tracking, plus {D_IN:.1f} V in the board's Schottky) and takes the current that flows there. On every curve that point is on the flat top, so the wings behave as a current source and the current is simply the light.",
        ]),
        ("Why two wings in series, and what that costs", [
            f"The one thing the charger needs is {V_OP:.1f} to {V_OP_FULL:.1f} V at its pad, depending on how full the cell is. One wing alone opens at {num['voc_one_room']:.1f} V on the desk and {num['voc_one_window']:.1f} V at a bright window: nothing on the desk, and at the window a cliff a few tenths of a volt past the operating point, where a little shade would push it over. Two in series open at {num['voc_pair_room']:.1f} V in the same room light and {num['voc_pair_window']:.1f} at the window, and the operating point sits on the flat top in any light the satellite will see.",
            f"The cost is current. In series the pair gives one wing's current; in parallel two wings would give two, but only when each can reach the line on its own, and with a full cell the line is at {V_OP_FULL:.1f} V. Keeping a full cell full at a dull window (1 000 lux) the series pair gives {num['series_full'][k_dull]:.1f} mA and a parallel pair nothing at all; at a bright window (3 000 lux) still {num['series_full'][k_bright]:.1f} against {num['parallel_full'][k_bright]:.1f}; only on a sunny sill does parallel pull ahead, {num['parallel_full'][k_sill]:.1f} mA against {num['series_full'][k_sill]:.1f}, and in sun nearly double. The sheet chose the arrangement that never reads zero at a window over the one that gives more on a sill, because keeping a full cell full in dull light is the job, and the bright end has power to spare.",
            f"There is a third way, and it is the upgrade if the window ever feels thin. A switching charger that tracks the pair's maximum-power point trades their spare volts for amps: from the same wings at 3 000 lux it would push about {num['mppt_window']:.0f} mA into the cell instead of {num['series'][k_bright]:.1f}, {num['mppt_x']:.1f} times as much, and {num['mppt_sun']:.0f} mA in sun. The owned board is linear and cannot. It was chosen because it is owned, because it does USB from the same socket, and because the budget closes without the extra.",
        ]),
        ("How the charger follows a weak wing, and why it eats 0.75 mA", [
            f"A linear charger is a controlled resistor between its input and the cell. This one watches its input and, when the source is weak, throttles its own current so the input never falls below the cell plus {TRACK:.2f} V. That is battery tracking, and it is exactly right for a panel: it keeps the wings just above the cell, on the flat top of their curve, where their current is greatest. A charger without it would ask a weak panel for more than it has, the panel's voltage would collapse below the cell, charging would stop, the voltage would recover, and it would chatter.",
            f"The same loop keeps the charger cold on solar. The drop across it is {TRACK:.2f} V and the board's Schottky another {D_IN:.1f}: {num['heat_sun_W']*1000:.0f} mW at the full {ISC:.0f} mA. A plain linear charger holding a 12 V pair at the cell's 3.8 V would burn {num['heat_plain_W']:.2f} W. From USB the drop is 5 V minus the cell at {I_USB*1000:.0f} mA, {num['heat_usb_W']:.1f} W, which inside a closed printed box of {num['box_cm2']:.0f} cm² warms the box about {num['box_dT']:.0f} °C; the chip throttles itself at a 125 °C junction and never gets there.",
            ("fig", fig_heat(), f"The three heats. Only the USB case is felt, and only as a warm box for the hour and a bit a full charge takes."),
            f"Two of the sheet's rules come out of this loop. While tracking, the charger does not terminate: the current is small because the light is weak, not because the cell is full, and the chip cannot tell the two apart, so it holds the cell at 4.2 V as long as there is light. And the charger spends about {E['bq_in']:.2f} mA from its input on its own regulator and references whenever an input is present, so the wings must beat that before anything reaches the cell. On the desk they do not.",
        ]),
        ("Where the six hours come from", [
            f"Every lithium charger has a safety timer: if the cell has not reached full in a set time, something is wrong (a dead cell, a short, a cell that is not there) and it stops. This one fixes it at {HOURS:.0f} h, because from a wall adapter a {I_USB*1000:.0f} mA charge of this cell takes about {num['usb_hours']:.1f} h and six is {HOURS/num['usb_hours']:.1f} times that. The timer was designed for a cable, not a window.",
            f"On the wings it starts when the morning first lifts the input above the cell plus {TRACK:.2f} V and runs out six hours later, whatever the sun is doing; it resets only when the input disappears, which on a window means dusk. So a day on the sill is six hours of harvest, not twelve, and the sheet's table counts six. Cutting the input would restart it, but the board gives the firmware no pin for that without another part, so it is not wired. At a bright window six hours are just enough: 3 000 lux stores {num['stored'][k_bright]:.0f} mAh against the beacon's {num['beacon_day']:.0f} a day.",
        ]),
        ("A day on the sill, in milliamp-hours", [
            f"Add it up at the sheet's five light levels. Stored is the pair's current at {V_OP:.1f} V, less the charger's {E['bq_in']:.2f} mA, times six hours; spent is the mode's current times twenty-four. The beacon costs {num['beacon_day']:.0f} mAh a day, the glow {num['glow_day']:.0f}, the lamp {E['lamp']*24:.0f}.",
            ("fig", fig_day(), f"Stored against spent. Room light and a dull window store next to nothing; a bright window stores {num['stored'][k_bright]:.0f} mAh, about a beacon day; an overcast sill {num['stored'][k_sill]:.0f}, five beacon days or most of a glow day; six hours of direct sun put {num['stored'][k_sun]:.0f} mAh in, more than half the cell."),
            f"The honest reading: on a desk away from the window this is a {E['blink_days']:.0f}-day battery object with a USB top-up; beside a bright window it is a solar one in beacon mode; on a sill it banks beacon days; the glow and the lamp live on direct sun or the cable. All of it is listing figures through a model until the first week on the sill is read off the BAT pad each evening, and the model's leak makes these numbers a shade lower than the sheet's table, which left it out.",
        ]),
        ("The cell: a 16340 that must never be rushed", [
            f"The cell is a Nitecore 16340: a lithium-ion cylinder {D['cell_d']} mm across and {D['cell_l']} long, 3.6 V nominal, 4.2 full, {E['cell_mah']} mAh, with its protection circuit under the wrap and a button top. The builder bought seven on 2026-11-03 and chose it over the 500 mAh pouch the sheet was approved with: nearly double the days in the dark, and a cell that lifts out of its holder when the lid is off. The protection opens the circuit above about 4.25 V, below about 2.8 V and above a couple of amps, and reconnects when the fault clears; in this build the controller's {num['cell_floor']:.2f} V floor comes first, so the cell's own cut-off is a last line it never reaches.",
            f"Lithium cells are charged at a rate of their own capacity. 1 C is {E['cell_mah']} mA for this cell; the board's jumper is cut to {I_USB*1000:.0f} mA, {I_USB*1000/E['cell_mah']:.2f} C, what a 16340 charger feeds it. Faster plates lithium metal onto the graphite instead of slipping it between the layers; so does charging below 0 °C, which a desk does not do, and the board's thermistor pin is fixed so there is no sensor to say otherwise. From the wings the charge is {num['series'][k_sun]:.0f} mA at the very most, a tenth of 1 C.",
            "The holder is a plastic tray with two spring contacts, and the springs are the only resistance in the path: a few tens of milliohms, a few millivolts at the charge current and nothing at all at the beacon's. A cell held at 4.2 V in the light every day ages faster than one that is cycled: the full-charge voltage slowly oxidises the electrolyte at the positive electrode. Expect the capacity to fade over a year or two on a sunny sill, and a $10 cell to swap in; calendar ageing at full charge is the one cost of a charger that never terminates on solar, paid gladly for a cell that is always full when dark comes.",
        ]),
        ("One diode, and the rail as the cell empties", [
            f"The SuperMini has no battery input. Its 5V pin is the USB connector's VBUS pin with nothing in between, so a cable plugged into the controller would put 5 V on anything wired to that pin, here the charger's BAT pad and the cell. One Schottky between the pad and the pin, band toward the controller, lets the cell feed the board and lets nothing feed back; it drops {D_SS14:.2f} V at this milliamp.",
            f"Behind the pin a small regulator makes the 3.3 V rail. It needs about {LDO_DROP:.1f} V of headroom, so the rail holds 3.3 V while the cell is above {num['cell_rail']:.2f} V and follows the cell down, {D_SS14 + LDO_DROP:.2f} V behind, below that. The chip is specified to {C3_MIN:.1f} V, which is a {num['cell_floor']:.2f} V cell, and keeps running out of spec until its own brown-out reset near 2.7 V. Below {num['cell_floor']:.2f} V the cell has a few per cent left, so the floor costs nothing the protection cut was not already taking; the sheet's {E['cell_usable']} of {E['cell_mah']} keeps a margin beyond.",
            ("fig", fig_rail(), f"The cell, the 5V pin and the rail against the cell's voltage, with about how much of the cell is left at each. The rail is a true 3.3 V down to a {num['cell_rail']:.2f} V cell, which is most of the cell."),
            f"The lights feel the sag before the chip does. A resistor from a {num['rail_low']:.2f} V rail gives the chip {num['i_chip_low']:.1f} mA instead of {num['i_chip']:.1f}, a dimmer blink that is itself the low-cell warning; the budget's 4 mA is the full-rail figure, so the days in the dark are, if anything, a little more.",
        ]),
        ("Light sleep against deep sleep for a two-second blink", [
            f"The ESP32-C3 has three sleeps and no coprocessor: unlike the ESP32-S3 it has no ULP to blink a pin while the main chip is off, so the blink is the chip's own job. Modem sleep keeps the CPU running at 20 mA. Deep sleep is {DEEP_MA*1000:.0f} µA with everything off but the clock, and waking is a reboot: about {BOOT_S*1000:.0f} ms through the ROM and the flash at some {BOOT_MA:.0f} mA, which every two seconds averages {BOOT_MA*BOOT_S/PERIOD_S:.2f} mA.",
            f"Light sleep is {E['c3_sleep']:.2f} mA with the clocks gated and the RAM and the pins held, and waking takes under a millisecond. The blink is then four lines: set the pin, sleep {BLINK_S*1000:.0f} ms, clear it, sleep {PERIOD_S - BLINK_S:.1f} s; {E['blink']:.2f} mA all in with the chip's {E['led_on']:.0f} mA. Deep sleep would win only if the period were longer than about {num['t_cross']:.0f} s.",
            ("fig", fig_sleep(), f"Two blinks each way. The solid trace is the sheet's: {E['blink']:.2f} mA. The dashed one reboots for each blink and averages {num['deep_avg']:.1f} mA, ten times more, for a 5 µA floor nobody sees."),
            "The pool is PWM from the LED-control peripheral clocked by the chip's internal RC oscillator, which keeps running in light sleep, so the glow mode is the same sleep with one timer alive. Wi-Fi never starts: its 300 mA peaks would need the boost the sheet turns off, and nothing here has anything to say to a network.",
        ]),
        ("A phosphor chip at 4 mA, a filament at 10", [
            f"An LED is a diode: its current climbs exponentially with the voltage across it, about tenfold for every {num['chip_slope_mv']:.0f} mV, so a pin that set a voltage would set a current it could not control. A resistor in series fixes it. The pin gives 3.3 V, the resistor and the pin's own {PIN_R:.0f} Ω take the difference, and the diode's curve and the resistor's line cross at one point. For the chip, {VF_CHIP} V at a few milliamps and {R_CHIP:.0f} Ω, that is {num['i_chip']:.1f} mA, a fifth of its 20 and about {num['chip_mcd']:.0f} millicandela: at 3 m across a dark room, {num['venus_x']:.0f} times Venus at its brightest. For the filament, the hologram's figure again: {VF_FIL} V, {R_FIL:.0f} Ω, {num['i_fil']:.1f} mA, about 2.5 lumens, a candle's fifth spread over the brass.",
            ("fig", fig_led(), "Both load lines. The dashed lines are the same resistors from the sagged rail of a nearly empty cell; the lights dim before anything else notices."),
            f"The chip is a 0.3 mm blue die on a 2 × 1.25 mm pad under a drop of silicone loaded with yellow and red phosphor, with two 0.1 mm enamelled wires soldered on at the factory; the enamel burns off when the ends are tinned, and the glue that holds it to the box carries no current. The model's chip reads {num['vf_chip_20']:.2f} V at 20 mA; the listing says 2.8 to 3.3, the one number it leaves loose, which is why the sheet asks for the chip to be lit through its resistor on the bench before it is glued: a high-voltage chip would be dim, and the kit's 68 Ω is the fix.",
            "The filament is the same physics on a 38 mm ceramic strip: a row of blue dies under a thick orange phosphor, both leads at one end, a polarity mark. The hologram's physics page has its full curve; here it only matters that 68 Ω holds it under the pin's 20 mA with a low-voltage strip and that it is never connected without the resistor.",
        ]),
        ("Why 3000 K reads warm, and why a 2200 K pool suits brass", [
            "Colour temperature is the colour of a glowing body: a candle flame at 1 850 K, a tungsten bulb at 2 700, a halogen desk lamp at 3 000, the midday sun at 5 500, an overcast sky at 6 500. Lower is redder, because a cooler body radiates less blue. An LED has no temperature. It is a blue die whose light is partly turned yellow and red by phosphor, and the maker mixes the phosphor until the colour lands on the glowing-body line at the kelvin on the box; more red phosphor, lower kelvin, warmer.",
            ("fig", fig_kelvin(), "The glowing-body line with the two lights (the filament at 2 200 K, the chip at about 3 000), the room's light, and where brass reads under it."),
            "3000 K reads warm because it is a halogen lamp's colour, and 2200 K is a candle's, which is why the hologram chose it for the pool on the desk. Brass reflects red and yellow far better than blue, so the pool on the base comes back a shade more golden than the filament itself. Polished brass under room light reads near 3 000 K on the line; shaded or old brass, the kind on the family's earlier builds, nearer 2 200 to 2 500. The pool is that brass at its warm end, in light instead of metal, which is what the builder asked for.",
        ]),
        ("A hundred milliseconds every two seconds", [
            f"The eye adds up light for about a tenth of a second. Within that window a flash twice as long looks twice as bright (Bloch's law); past it, a longer flash looks no brighter, only longer. So {BLINK_S*1000:.0f} ms is the shortest blink that looks as bright as a steady light, and 5 % duty buys the full brightness at a twentieth of the power: the beacon at {E['led_on']*E['blink_duty']:.1f} mA average looks like a {E['led_on']:.0f} mA light that is mostly off.",
            ("fig", fig_blink(), "Left: apparent brightness of a flash against its length, flat past the eye's summation time. Right: the beacon's duty."),
            "Two seconds is the cadence of a thing passing, slow enough to be calm and quick enough that a glance catches one. Aircraft strobes flash for a few tens of milliseconds about once a second, which is why they look sharp but thin; a satellite tumbling across a dark sky flashes every few seconds as a panel catches the sun. The steady modes dim by PWM at 5 kHz, far above the 60 Hz the eye can follow, so dimming shows as brightness and not flicker; and because the eye compresses brightness roughly as a cube root, 30 % duty looks about two thirds as bright, not a third.",
        ]),
        ("The post as a column, the base as the fuse", [
            f"The post is one 1.5 mm 304 rod with {D['post_free']:.0f} mm free between its two sockets, carrying {D['top_g']:.0f} g. As a column fixed at the bottom and free at the top it buckles at {num['euler_N']:.1f} N; it carries {num['load_N']:.2f}, a {num['margin']:.0f}-fold margin. Its softness is sideways. A rod's stiffness goes as the fourth power of its diameter and the cube of its free length, so a 1 N push at the top bends this one {num['defl_mm_per_N']:.0f} mm, and with {D['top_g']:.0f} g on it the satellite sways at about {num['f_sway']:.1f} Hz when nudged, settling in a second or two.",
            f"That is the live feel of a thing on a post, and it is elastic. The steel would take a set only past about {num['f_set']:.1f} N at the top, and long before that, at {num['f_tip']:.2f} N, the whole satellite tips over the edge of its base. The base is the fuse: the post cannot be bent on the desk, only knocked over, and it lands on a wing of epoxy and a box of PETG.",
            ("fig", fig_post(), f"A 1 N push at the top, drawn to scale, and the five numbers of the post. The dashed line from the centre of mass to the base's edge is the {D['tip_deg']}° tipping angle."),
            f"The {D['disc_g']} g base, {D['coaster_g']:.0f} g of brass and {D['ballast_g']:.0f} of steel hidden under it, is {num['disc_pct']:.0f} % of the mass and all of the stability: centre of mass {D['com']:.0f} mm up on a {D['disc_d']/2:.1f} mm radius, so it tips at {D['tip_deg']}°. The booms carry {D['panel_g']:.0f} g each on {D['panel']:.0f} mm and sag {num['boom_sag']:.2f} mm, the panel glued along the rod stiffening both. Nothing is soldered because nothing needs to be: three rods in three glued sockets, a 1.5 mm rod in a 1.6 mm hole, the glue cured a day.",
        ]),
    ]


NUMBERS = [
    (f"{panel_ma(500, False):.2f} mA", f"the pair on a desk at 500 lux of LED light: {ISC:.0f} mA × 500 / 100 000 × 0.65"),
    (f"{num['mv_per_decade']:.0f} mV", "a cell's open-circuit voltage per tenfold of light: 1.3 × 25.7 mV × ln 10"),
    (f"{num['voc_one_room']:.1f} V", f"one wing open on the desk, with the model's {RSH_PANEL/1000:.0f} kΩ leak; {num['voc_pair_room']:.1f} V for the pair"),
    (f"{V_OP:.1f} to {V_OP_FULL:.1f} V", f"where the charger holds the wings: cell + {TRACK:.2f} V tracking + {D_IN:.1f} V Schottky"),
    (f"{num['leak_ma']:.1f} mA", f"the model's leak at that voltage: {V_OP:.1f} V / {2*RSH_PANEL/1000:.0f} kΩ"),
    (f"{num['mppt_x']:.1f}×", "what a maximum-power-point charger would take from the same pair at 3 000 lux"),
    (f"{num['heat_usb_W']:.1f} W", f"heat in the charger from USB: (5 − {VBAT}) V × {I_USB} A; the box rises about {num['box_dT']:.0f} °C"),
    (f"{num['heat_sun_W']*1000:.0f} mW", f"heat in the charger from the wings in sun: {TRACK + D_IN:.2f} V × {ISC:.0f} mA"),
    (f"{num['stored'][2]:.0f} mAh", f"stored at a bright window: ({num['series'][2]:.1f} − {E['bq_in']:.2f}) mA × 6 h, against the beacon's {num['beacon_day']:.0f} a day"),
    (f"{num['cell_rail']:.2f} V", f"the cell above which the rail is a true 3.3 V: 3.3 + {LDO_DROP:.1f} regulator + {D_SS14:.2f} diode"),
    (f"{num['cell_floor']:.2f} V", "the cell at which the chip reaches its 3.0 V floor"),
    (f"{num['t_cross']:.0f} s", f"the period past which deep sleep beats light sleep: {BOOT_MA:.0f} mA × {BOOT_S} s / {E['c3_sleep']:.3g} mA"),
    (f"{num['i_chip']:.1f} mA", f"the beacon's current: the chip's curve ({VF_CHIP} V at a few milliamps) against (3.3 − V) / ({R_CHIP:.0f} + {PIN_R:.0f} Ω)"),
    (f"{num['i_fil']:.1f} mA", f"the filament's: its curve ({VF_FIL} V) against (3.3 − V) / ({R_FIL:.0f} + {PIN_R:.0f} Ω)"),
    (f"{BLOCH_S*1000:.0f} ms", "the eye's summation time: the shortest blink that looks full"),
    (f"{num['euler_N']:.1f} N", f"the post's buckling load, fixed-free, {D['post_free']:.0f} mm of 1.5 mm 304"),
    (f"{num['defl_mm_per_N']:.0f} mm/N", f"the post's give at the top: L³ / 3EI; sways at {num['f_sway']:.1f} Hz under {D['top_g']:.0f} g"),
    (f"{num['f_tip']:.2f} N", f"the push at the top that tips it: {num['W_N']:.2f} N × {D['disc_d']/2:.0f} mm / {D['height']:.0f} mm, before the steel's {num['f_set']:.1f} N"),
]

PARTS_IDEAS = [
    ("a diode in the light, Voc by the logarithm, 0.65 for LED light, the leak", "mini solar panel", "panel"),
    ("battery tracking, the 0.75 mA, the 6 h timer, 48 mW against 0.6 W", "charger board", "charger"),
    ("1 C, protection under the wrap, calendar ageing at 4.2 V", "Nitecore 16340 cell", "cell"),
    ("spring contacts, the pigtail joint 40 mm from the cell", "16340 holder", "holder"),
    ("light sleep against deep sleep, no ULP, the rail and its floor", "ESP32-C3 SuperMini", "controller"),
    ("the VBUS pin, 0.15 V, flashing with the cell in", "SS14 Schottky", "schottky"),
    ("the load line, the loose forward voltage, phosphor, Bloch's law", "pre-wired LED chip", "led"),
    ("2200 K on the glowing-body line, brass in light", "LED filament", "filament"),
    ("Euler, L³ / 3EI, 6.6 Hz, no set on the desk", "1.5 mm stainless rod", "rod15"),
    (f"{num['disc_pct']:.0f} % of the mass, the fuse that tips first", "brass base", "disc"),
]


def page_html():
    o = ['<title>Desk Satellite Physics</title>',
         '<meta name="claude:viewport-fit-sides" content="cover">',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
         f"<style>{STYLE}</style>",
         '<style>.wrap{max-width:880px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} figure svg{width:100%;height:auto} td,th{min-width:0}</style>',
         '<div class="wrap">',
         '<div class="masthead"><div class="eyebrow">Desk satellite &middot; step 2: the science and engineering</div>',
         '<h1>Why a window keeps it blinking</h1>',
         f'<div class="sub">The working behind every number on the sheet of 2026-11-02, approved {APPROVED} and revised the same day for the Nitecore 16340 cell: a silicon cell in room light, two wings in series, a charger that follows a weak panel and what it eats, the six hours, a day in milliamp-hours, a cell never rushed, one diode and the rail, light sleep against deep, two load lines, the glowing-body line, a hundred milliseconds, and one post over a brass base.<br>Read after <a href="{BUILD_PAGE}" target="_blank" rel="noopener">Desk Satellite Build</a>. Nothing measured yet; every figure is derived from datasheet and listing numbers and the sheet\'s dimensions, and the solar curves are a model until the first week on the sill.</div></div>']
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
    o.append("<h2>What comes next</h2><p>The three Amazon lines were ordered on 2026-11-03; the box envelope is checked against the real boards and the cell, then printed with its lid and the hub; the brass base is weighted with steel; the firmware is written (light sleep with a timer, three modes in NVS, PWM for the pool); the wings are soldered and the pair metered in daylight; and the first week on the sill replaces every solar number on this page with a reading off the BAT pad.</p>")
    o.append(f'<hr><p class="sub">Built by <code>docs/pages/gen/physics_page.py</code> from the dimensions, budget and light levels in <code>build_page.py</code>; it also writes <code>docs/PHYSICS.md</code>. Assumptions, each a number at the top of the script: cell ideality {N_IDEAL}, {RSH_PANEL/1000:.0f} kΩ of leak per panel, {TRACK:.2f} V tracking and {D_IN:.1f} V in the board\'s Schottky, a {VBAT} V cell, {LDO_DROP:.1f} V regulator headroom, {D_SS14:.2f} V in the SS14, {VF_CHIP} and {VF_FIL} V forward voltages, a {BOOT_S*1000:.0f} ms reboot at {BOOT_MA:.0f} mA, 304 at {E_STEEL/1e9:.0f} GPa and {SY_STEEL/1e6:.0f} MPa, {H_CONV:.0f} W/m²K off the box. The charger\'s figures are TI\'s datasheet; the chip\'s and the panels\' are their listings. Nothing here has been measured on the satellite itself.</p>')
    o.append("</div>")
    return "\n".join(o)


def physics_md():
    o = ["# Why a window keeps it blinking: the science and engineering behind the sheet", "",
         f"Step 2 of the house rule, written {APPROVED} after the sheet was approved. Generated by `pages/gen/physics_page.py`; the page `pages/desk-satellite-physics.html` carries the figures. Edit the script, not this file.", ""]
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
    o += ["", "## What comes next", "", "The three Amazon lines were ordered on 2026-11-03; the box envelope checked against the real boards and the cell, then printed with its lid and the hub; the brass base weighted with steel; the firmware (light sleep with a timer, three modes in NVS, PWM for the pool); the wings soldered and the pair metered in daylight; the first week on the sill read off the BAT pad each evening.", ""]
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
        out = PRINT / "desk-satellite-physics.pdf"
        out.write_bytes(pdf.read_bytes())
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [ln for ln in info.splitlines() if ln.startswith("Pages")])


def main():
    html = page_html()
    OUT.write_text(html)
    (DOCS / "PHYSICS.md").write_text(physics_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "PHYSICS.md")
    for k in sorted(num):
        v = num[k]
        print(f"  {k} = " + (", ".join(f"{x:.3g}" for x in v) if isinstance(v, list) else f"{v:.4g}"))
    if "--pdf" in sys.argv:
        print_pdf(html)


if __name__ == "__main__":
    main()
