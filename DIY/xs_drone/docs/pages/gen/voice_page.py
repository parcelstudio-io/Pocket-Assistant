"""XS drone, step 2 for the voice revision (approved late on 2026-11-09): the science and engineering behind the
microphone and the speaker.

Writes docs/pages/voice-physics.html, docs/voice-physics.md (the same text without the figures) and, with --pdf,
docs/pages/print/voice-physics.pdf (Letter, portrait, black). Every number is derived here from the constants at the
top, each a datasheet figure or a named assumption, and the two waveform figures are simulated, not sketched. The page
style is copied from custom-build.html so the drone's pages match. Edit this script, not the outputs."""
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
HTML_OUT = PAGES / "voice-physics.html"
MD_OUT = DOCS / "voice-physics.md"
PRINT = PAGES / "print"
BUILD_PAGE = "https://claude.ai/artifact/34eHTqKHJ2gfCkfK2Yb4up"
FOLLOW_PAGE = "https://claude.ai/artifact/LYYQRGev8wnFg92FFNJxxc"
APPROVED = "2026-11-09"
WRITTEN = "2026-11-10"

# ----------------------------------------------------------------------------- the sheet's values and the datasheets'
VIO = 3.3                      # V, the XIAO's I/O rail: the height of every pulse
R1, R2, C1 = 10e3, 1.5e3, 22e-9  # the divider and its capacitor, as drawn
F_SDM = 1.0e6                  # Hz, the modulator's pulse rate
F_S = 16e3                     # Hz, the timer that writes a new density
BITS = 8                       # the density register
D_FULL, D_CLEAN, D_DEFAULT = 127, 90, 64   # full scale; Espressif's "better randomness" limit; the firmware's default
GAIN_DB = 24.0                 # PAM8403, fixed
R_IN = 18e3                    # Ω, the PAM8403's input resistor at 24 dB (RF 142 kΩ over RI 18 kΩ, its datasheet)
R_ON = 0.18 + 0.14             # Ω, one PMOS and one NMOS in the bridge path (180 and 140 mΩ at 500 mA)
F_SW = 260e3                   # Hz, the amplifier's switching frequency
I_Q = 10e-3                    # A, quiescent at 3.6 V, no load
V_UVLO = 2.0                   # V, the amplifier's under-voltage cut-out
EFF_AMP = 0.85                 # between the datasheet's 83 % (4 Ω, 10 % THD) and its "up to 90 %"
P_AMP_1PC = 0.72               # W into 8 Ω at 3.6 V and 1 % THD+N, the datasheet's figure
R_SPK = 8.0                    # Ω
P_SPK_RATED, P_SPK_MAX = 0.8, 1.0
SPL_REF, P_REF, D_REF = 91.0, 0.8, 0.10     # dB at 0.8 W and 10 cm, the speaker's datasheet (88 to 94)
F_O, F_SPK_LO, F_SPK_HI = 1300.0, 500.0, 20000.0
SPK_R = 0.0065                 # m, about the radius of the moving part inside a 20 × 13 mm box
V_PACK, V_PACK_FULL, V_PACK_SAG = 3.7, 4.2, 3.3   # nominal; full; sagging under a hover near the end
MIC_SENS, MIC_SNR, MIC_AOP = -26.0, 64.0, 120.0   # dBFS at 94 dB SPL; dB(A); dB SPL, the MSM261D3526H1CPM datasheet
MIC_CLK_SLEEP, MIC_CLK_LP, MIC_CLK_STD = 50e3, (150e3, 900e3), (1.1e6, 4.0e6)
I_MIC = 670e-6                 # A at a 2.4 MHz clock
PDM_RATIOS = (64, 128)         # the ESP32-S3's PDM clock over its PCM rate: I2S_PDM_DSR_8S and I2S_PDM_DSR_16S
SPEECH_1M = 60.0               # dB SPL, ordinary speech at 1 m
PROP_1M = (65.0, 70.0)         # dB(A) at 1 m, an estimate: an 80 g Tello measures 46 dB(A) at 13 m, about 68 at 1 m
D_MIC_PROP = 0.03              # m, the microphone to the nearest propeller
C_SOUND = 343.0                # m/s
# flight, from the build document's ledger
THRUST = 68.0                  # gf, the vendor's figure for four motors on 30 mm props
M_BEFORE, M_VOICE = 33.5, 37.5
M_SPK, M_AMP, M_SMALL = 2.0, 1.5, 0.5
I_REF, M_REF = 2.4, 25.0       # A at 25 g: the hover current scales as mass to the 1.5
PACK_MAH, USABLE, ELEC = 250.0, 0.8, 0.95   # 80 % of the pack; 5 % for the controller and the camera
PACK_C = 30.0
GATE, FLOOR = 2.0, 1.5
Y_SPK, Y_AMP, Y_MOTOR = (-30.5, -10.5), (11.0, 29.5), 30.0   # mm along the aircraft; the motors at ±30
Z_SPK_TOP, Z_PROP = 10.9, 16.0 # mm above the pan's floor
SPK_TO_MIC = 0.024             # m, the speaker's centre to the microphone on the cabin
BITS_PCM = 16
CAM_MBPS = (1.2, 1.8)          # the camera stream, following page

num: dict = {}


def dB(x):
    return 20 * math.log10(x)


def derive():
    n = num
    n["gain"] = 10 ** (GAIN_DB / 20)
    n["k"] = R2 / (R1 + R2)
    r2p = 1 / (1 / R2 + 1 / R_IN)
    n["k_loaded"] = r2p / (R1 + r2p)
    n["div_db"] = -dB(1 / n["k_loaded"])
    n["r_th"] = 1 / (1 / R1 + 1 / R2)
    n["r_th_loaded"] = 1 / (1 / R1 + 1 / R2 + 1 / R_IN)
    n["fc"] = 1 / (2 * math.pi * n["r_th"] * C1)
    n["fc_loaded"] = 1 / (2 * math.pi * n["r_th_loaded"] * C1)
    n["tau_loaded"] = n["r_th_loaded"] * C1
    swing = VIO * (2 * D_FULL) / 256
    n["node_full_open"] = VIO * n["k"] * (2 * D_FULL) / 256
    n["node_full"] = swing * n["k_loaded"]
    n["node_default"] = VIO * n["k_loaded"] * (2 * D_DEFAULT) / 256
    n["node_clean"] = VIO * n["k_loaded"] * (2 * D_CLEAN) / 256
    n["node_dc"] = VIO * n["k_loaded"] / 2
    n["out_full"] = n["node_full"] * n["gain"]
    n["out_default"] = n["node_default"] * n["gain"]
    n["out_clean"] = n["node_clean"] * n["gain"]

    def h(f):
        return 1 / math.sqrt(1 + (f / n["fc_loaded"]) ** 2)

    n["h"] = {f: dB(h(f)) for f in (300.0, 3400.0, n["fc_loaded"], 8000.0, 16000.0, F_SW, F_SDM)}
    n["carrier_node_mv"] = VIO * n["k_loaded"] * h(F_SDM) * 1000
    n["sinc_15k"] = dB(abs(math.sin(math.pi * 15000 / F_S) / (math.pi * 15000 / F_S)))
    n["image_db"] = n["h"][16000.0] + n["sinc_15k"]
    n["snr_bits"] = 6.02 * BITS + 1.76
    osr = F_SDM / (2 * (F_S / 2))
    n["osr"] = osr
    n["snr_mod2"] = 6.02 + 1.76 - 10 * math.log10(math.pi ** 4 / 5) + 50 * math.log10(osr)
    n["isr_share"] = F_S * 1e-6 / 1.0 * 100          # one microsecond per interrupt, one core
    n["swing_cap"] = {v: 2 * v * R_SPK / (R_SPK + R_ON) for v in (V_PACK_SAG, V_PACK, V_PACK_FULL)}
    n["v_need_full"] = n["out_full"] / 2 * (R_SPK + R_ON) / R_SPK
    n["v_need_default"] = n["out_default"] / 2 * (R_SPK + R_ON) / R_SPK
    n["p_full"] = (n["out_full"] / (2 * math.sqrt(2))) ** 2 / R_SPK
    n["p_default"] = (n["out_default"] / (2 * math.sqrt(2))) ** 2 / R_SPK
    n["p_clean"] = (n["out_clean"] / (2 * math.sqrt(2))) ** 2 / R_SPK
    n["vpp_rated"] = 2 * math.sqrt(2) * math.sqrt(P_SPK_RATED * R_SPK)
    n["i_amp_full"] = n["p_full"] / EFF_AMP / V_PACK
    n["i_peak_full"] = n["out_full"] / 2 / R_SPK
    n["heat_full"] = n["p_full"] * (1 / EFF_AMP - 1)
    n["spl10_full"] = SPL_REF + 10 * math.log10(n["p_full"] / P_REF)
    n["spl10_default"] = SPL_REF + 10 * math.log10(n["p_default"] / P_REF)
    n["spl1_full"] = n["spl10_full"] - dB(1.0 / D_REF)
    n["spl1_default"] = n["spl10_default"] - dB(1.0 / D_REF)
    n["spl3_full"] = n["spl1_full"] - dB(3.0)
    n["spl_at_mic"] = n["spl10_full"] + dB(D_REF / SPK_TO_MIC)
    n["ka1"] = C_SOUND / (2 * math.pi * SPK_R)       # Hz at which ka = 1
    n["lambda_1k"] = C_SOUND / 1000 * 1000           # mm
    n["below_fo"] = {F_O / 2: -12.0, F_O / 4: -24.0}
    n["mic_full_spl"] = 94 - MIC_SENS
    n["mic_floor_spl"] = 94 - MIC_SNR
    n["speech_dbfs"] = SPEECH_1M - n["mic_full_spl"]
    n["prop_at_mic"] = tuple(p + dB(1.0 / D_MIC_PROP) for p in PROP_1M)
    n["prop_margin"] = tuple(p - SPEECH_1M for p in n["prop_at_mic"])
    n["pdm_clk"] = {r: F_S * r for r in PDM_RATIOS}
    n["cg"] = (M_SPK * sum(Y_SPK) / 2 + M_AMP * sum(Y_AMP) / 2) / M_VOICE
    n["rear_share"] = 0.5 - n["cg"] / (2 * Y_MOTOR)
    n["prop_gap"] = Z_PROP - Z_SPK_TOP
    n["tw"] = {M_BEFORE: THRUST / M_BEFORE, M_VOICE: THRUST / M_VOICE}
    n["m_gate"], n["m_floor"] = THRUST / GATE, THRUST / FLOOR
    n["hover_cmd"] = {m: math.sqrt(1 / tw) * 100 for m, tw in n["tw"].items()}
    n["i_hover"] = {m: I_REF * (m / M_REF) ** 1.5 for m in (M_BEFORE, M_VOICE)}
    n["t_fly"] = {m: USABLE * PACK_MAH / 1000 / i * 60 * ELEC for m, i in n["i_hover"].items()}
    n["c_rate"] = n["i_hover"][M_VOICE] / (PACK_MAH / 1000)
    n["iq_share"] = I_Q / n["i_hover"][M_VOICE] * 100
    n["iq_hours"] = USABLE * PACK_MAH / 1000 / I_Q
    n["mic_ma"] = I_MIC * 1000
    n["kbps"] = F_S * BITS_PCM / 1000
    n["frame_bytes"] = F_S * BITS_PCM / 8 * 0.020
    n["link_share"] = tuple(n["kbps"] / 1000 / c * 100 for c in CAM_MBPS)
    n["added"] = M_SPK + M_AMP + M_SMALL
    n["t_lost"] = n["t_fly"][M_BEFORE] - n["t_fly"][M_VOICE]


derive()


def hover_current(m):
    return I_REF * (m / M_REF) ** 1.5


def fly_minutes(m):
    return USABLE * PACK_MAH / 1000 / hover_current(m) * 60 * ELEC


# ----------------------------------------------------------------------------- the simulation behind figure 2
def simulate(density, f_tone=1000.0, dur=2e-3):
    """A 1 kHz tone at the given peak density, held at 16 kHz, through a second-order 1-bit modulator at F_SDM, then
    through the divider and the capacitor with the amplifier's input across them. Returns pulses, node volts, the
    held input and the ideal tone, one entry per modulator clock."""
    n = int(round(dur * F_SDM))
    dt = 1 / F_SDM
    k, tau = num["k_loaded"], num["tau_loaded"]
    amp = density / 128
    x1 = x2 = 0.0
    vn = k * VIO / 2
    pulses, node, held, ideal = [], [], [], []
    peak = 0.0
    for i in range(n):
        t = i * dt
        ts = math.floor(t * F_S) / F_S
        u = amp * math.sin(2 * math.pi * f_tone * ts)
        v = 1.0 if x2 >= 0 else -1.0            # the comparator
        x1_new = x1 + u - v                       # first integrator
        x2_new = x2 + x1 - 2 * v                  # second integrator, feedback 2: noise shaped as (1 - z^-1)^2
        x1, x2 = x1_new, x2_new
        peak = max(peak, abs(x2))
        pulses.append(1 if v > 0 else 0)
        vp = VIO if v > 0 else 0.0
        vn += dt / tau * (k * vp - vn)            # the RC, one microsecond at a time
        node.append(vn)
        held.append(u)
        ideal.append(amp * math.sin(2 * math.pi * f_tone * t))
    return pulses, node, held, ideal, peak


# ----------------------------------------------------------------------------- figure helpers
def esc(s):
    return html.escape(str(s), quote=False)


def f(x, d=0):
    return f"{x:.{d}f}"


FIG_CSS = ("<style>"
           ".ax{fill:none;stroke:var(--ink);stroke-width:1.4;stroke-linecap:round}"
           ".grid{fill:none;stroke:var(--line);stroke-width:1}"
           ".s1{fill:none;stroke:var(--c1);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}"
           ".s2{fill:none;stroke:var(--c2);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:7 5}"
           ".ref{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:4 4}"
           ".ideal{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:3 3}"
           ".band{fill:var(--steel-soft);stroke:none}"
           ".noise{fill:var(--ink-2);fill-opacity:.18;stroke:none}"
           ".b1{fill:var(--c1-soft);stroke:var(--c1);stroke-width:1}"
           ".b2{fill:var(--c2-soft);stroke:var(--c2);stroke-width:1}"
           ".b0{fill:var(--line);stroke:none}"
           ".dot{fill:var(--ink);stroke:var(--paper);stroke-width:2}"
           ".dot1{fill:var(--c1);stroke:var(--paper);stroke-width:2}"
           ".dot2{fill:var(--c2);stroke:var(--paper);stroke-width:2}"
           ".hol{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
           ".bit{fill:var(--c1);stroke:none}"
           ".box{fill:var(--paper);stroke:var(--line);stroke-width:1}"
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


def rect(x0, y0, x1, y1, cls, rx=0, extra=""):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="{rx}" class="{cls}" {extra}/>'


def circ(x, y, r, cls):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="{cls}"/>'


def legend(x, y, items):
    """items: (class of the swatch line or 'noise', label)."""
    o = []
    for cls, lab in items:
        if cls == "noise":
            o.append(rect(x, y - 6, x + 26, y + 4, "noise"))
        else:
            o.append(line(x, y - 1, x + 26, y - 1, cls))
        o.append(T(x + 32, y + 3, lab, "t"))
        x += 32 + 7 * len(lab) + 22
    return "".join(o)


# ----------------------------------------------------------------------------- figure 1: the microphone's clock
def fig_clock():
    W, H = 860, 200
    x0, x1 = 60, 820
    lo, hi = 1e4, 1e7

    def X(fr):
        return x0 + (math.log10(fr) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (x1 - x0)

    yb0, yb1 = 66, 106
    o = [T(x0, 24, "The microphone's clock bands, from its datasheet, and the two clocks the ESP32-S3 can give it at 16 kHz", "h")]
    o.append(rect(X(lo), yb0, X(MIC_CLK_SLEEP), yb1, "b0"))
    o.append(T((X(lo) + X(MIC_CLK_SLEEP)) / 2, yb0 - 8, "sleep, under 50 kHz", "fn", "middle"))
    o.append(rect(X(MIC_CLK_LP[0]), yb0, X(MIC_CLK_LP[1]), yb1, "b2"))
    o.append(T((X(MIC_CLK_LP[0]) + X(MIC_CLK_LP[1])) / 2, yb0 - 8, "low-power mode, 150 to 900 kHz", "fn", "middle"))
    o.append(rect(X(MIC_CLK_STD[0]), yb0, X(MIC_CLK_STD[1]), yb1, "b1"))
    o.append(T((X(MIC_CLK_STD[0]) + X(MIC_CLK_STD[1])) / 2, yb0 - 8, "standard mode, 1.1 to 4.0 MHz", "fn", "middle"))
    # axis
    ya = 152
    o.append(line(x0, ya, x1, ya))
    for fr, lab in ((1e4, "10 kHz"), (1e5, "100 kHz"), (1e6, "1 MHz"), (1e7, "10 MHz")):
        o.append(line(X(fr), ya, X(fr), ya + 5))
        o.append(T(X(fr), ya + 18, lab, "fn", "middle"))
    for fr in (2e4, 5e4, 2e5, 5e5, 2e6, 5e6):
        o.append(line(X(fr), ya, X(fr), ya + 3, "grid"))
    # the two clocks
    c64, c128 = num["pdm_clk"][64], num["pdm_clk"][128]
    o.append(line(X(c64), yb0 - 4, X(c64), ya, "ref"))
    o.append(circ(X(c64), yb1 + 12, 5, "hol"))
    o.append(T(X(c64) - 9, yb1 + 32, f"×64: {c64 / 1e6:.2f} MHz, the default, in the gap", "num", "end"))
    o.append(line(X(c128), yb0 - 4, X(c128), ya, "ref"))
    o.append(circ(X(c128), yb1 + 12, 5, "dot1"))
    o.append(T(X(c128) + 9, yb1 + 32, f"×128: {c128 / 1e6:.2f} MHz, in band", "num"))
    o.append(T(X(2.4e6) + 4, yb0 + 26, "2.4 MHz: the datasheet's test clock", "fn"))
    o.append(line(X(2.4e6), yb0, X(2.4e6), yb1, "grid"))
    return svg(W, H, "".join(o), "The microphone's three clock bands on a log scale with the ESP32-S3's 64× and 128× clocks at a 16 kHz sample rate marked")


# ----------------------------------------------------------------------------- figure 2: one bit a million times a second
def fig_pdm():
    pulses, node, held, ideal, peak = simulate(D_DEFAULT)
    num["mod2_peak_default"] = peak
    n = len(pulses)
    W, H = 860, 500
    x0, x1 = 60, 820

    def X(i):
        return x0 + i / n * (x1 - x0)

    o = [T(x0, 22, f"A 1 kHz tone at the everyday level (density ±{D_DEFAULT}): the samples, the pulses, and what the capacitor makes of them", "h")]
    # panel A: the held samples and the ideal tone
    ya, ha = 118, 55
    o.append(T(x0, ya - ha - 14, "the timer's 16 kHz steps (solid) over the tone they stand for (dotted), as a fraction of full scale", "fn"))
    o.append(line(x0, ya, x1, ya, "grid"))
    o.append(poly([(X(i), ya - ideal[i] * ha) for i in range(0, n, 4)], "ideal"))
    o.append(poly([(X(i), ya - held[i] * ha) for i in range(0, n, 2)], "s1"))
    o.append(T(x0 - 6, ya - ha + 4, f"+{D_DEFAULT / 128:.1f}", "num", "end"))
    o.append(T(x0 - 6, ya + ha + 4, f"−{D_DEFAULT / 128:.1f}", "num", "end"))
    # panel B: the pulse strip, 10 pulses a cell
    yb0, yb1 = 212, 252
    o.append(T(x0, yb0 - 10, f"the modulator's output at {F_SDM / 1e6:.0f} MHz: {n} pulses, 10 to a cell; the darker the cell, the more of them are high", "fn"))
    cells = n // 10
    cw = (x1 - x0) / cells
    for c in range(cells):
        k = sum(pulses[c * 10:(c + 1) * 10])
        o.append(f'<rect x="{x0 + c * cw:.2f}" y="{yb0}" width="{cw + 0.3:.2f}" height="{yb1 - yb0}" class="bit" fill-opacity="{0.06 + 0.94 * k / 10:.2f}"/>')
    o.append(rect(x0, yb0, x1, yb1, "grid"))
    # two zooms of 40 raw pulses: at the crest (t = 0.25 ms) and at the crossing (t = 0.5 ms)
    for (start, label, zx) in ((250, "40 pulses at the crest: mostly high", 60), (500, "40 pulses at the crossing: half and half", 460)):
        zy0, zy1 = 286, 314
        bw = 340 / 40
        o.append(line(X(start + 20), yb1, zx + 170, zy0 - 2, "grid"))
        o.append(rect(zx, zy0, zx + 340, zy1, "box"))
        for j in range(40):
            if pulses[start + j]:
                o.append(f'<rect x="{zx + j * bw + 1:.1f}" y="{zy0 + 3}" width="{bw - 2:.1f}" height="{zy1 - zy0 - 6}" class="bit"/>')
        o.append(T(zx, zy1 + 15, label, "fn"))
    # panel C: the node voltage
    yc, hc = 424, 40
    mean = sum(node) / n
    scale = hc / (num["node_default"] / 2)
    o.append(T(x0, yc - hc - 16, f"the node after the 10 kΩ, the 1.5 kΩ and the 22 nF (solid), simulated one microsecond at a time, against the tone scaled to the same {num['node_default'] * 1000:.0f} mV peak to peak (dotted)", "fn"))
    o.append(line(x0, yc, x1, yc, "grid"))
    o.append(poly([(X(i), yc - ideal[i] / (D_DEFAULT / 128) * num["node_default"] / 2 * scale) for i in range(0, n, 4)], "ideal"))
    o.append(poly([(X(i), yc - (node[i] - mean) * scale) for i in range(0, n, 2)], "s1"))
    o.append(T(x0 - 6, yc - hc + 4, f"+{num['node_default'] * 500:.0f} mV", "num", "end"))
    o.append(T(x0 - 6, yc + hc + 4, f"−{num['node_default'] * 500:.0f} mV", "num", "end"))
    # time axis
    yt = 478
    o.append(line(x0, yt, x1, yt))
    for ms in (0, 0.5, 1.0, 1.5, 2.0):
        xx = X(ms * 1e-3 * F_SDM) if ms < 2 else x1
        o.append(line(xx, yt, xx, yt + 5))
        o.append(T(xx, yt + 17, f"{ms:g} ms", "fn", "middle"))
    return svg(W, H, "".join(o), "Three panels: the 16 kHz held samples of a 1 kHz tone, the simulated 1 MHz pulse stream as a density strip with two zooms of 40 raw pulses, and the filtered node voltage against the ideal tone")


# ----------------------------------------------------------------------------- figure 3: the filter
def fig_filter():
    W, H = 860, 360
    x0, x1, y0, y1 = 70, 820, 40, 300
    lo, hi = 100.0, 2e6
    fc = num["fc_loaded"]

    def X(fr):
        return x0 + (math.log10(fr) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (x1 - x0)

    def Y(db):
        return y0 + (-db) / 60 * (y1 - y0)

    o = [T(x0, 22, "What the divider and the 22 nF pass, relative to the voice band: a first-order roll-off from 6 kHz", "h")]
    o.append(rect(X(300), y0, X(3400), y1, "band"))
    o.append(T((X(300) + X(3400)) / 2, y0 + 14, "the voice band, 300 to 3 400 Hz", "fn", "middle"))
    for db in (0, -20, -40, -60):
        o.append(line(x0, Y(db), x1, Y(db), "grid"))
        o.append(T(x0 - 8, Y(db) + 4, f"{db:d} dB" if db else "0 dB", "num", "end"))
    o.append(line(x0, y1, x1, y1))
    o.append(line(x0, y0, x0, y1))
    for fr, lab in ((100, "100 Hz"), (1e3, "1 kHz"), (1e4, "10 kHz"), (1e5, "100 kHz"), (1e6, "1 MHz")):
        o.append(line(X(fr), y1, X(fr), y1 + 5))
        o.append(T(X(fr), y1 + 18, lab, "fn", "middle"))
    pts = []
    for i in range(241):
        fr = lo * (hi / lo) ** (i / 240)
        pts.append((X(fr), Y(dB(1 / math.sqrt(1 + (fr / fc) ** 2)))))
    o.append(poly(pts, "s1"))
    marks = ((3400.0, f"3.4 kHz: {num['h'][3400.0]:.1f} dB, the top of the voice band", -10, 22),
             (fc, f"{fc / 1000:.1f} kHz: the corner, −3 dB", 10, 24),
             (16000.0, f"16 kHz: {num['h'][16000.0]:.0f} dB, where the stair-steps live", -10, 22),
             (F_SW, f"260 kHz: {num['h'][F_SW]:.0f} dB, the amplifier's own switching", -10, -8),
             (F_SDM, f"1 MHz: {num['h'][F_SDM]:.0f} dB, the pulses: {num['carrier_node_mv']:.1f} mV left", -10, -8))
    for fr, lab, dx, dy in marks:
        yy = Y(dB(1 / math.sqrt(1 + (fr / fc) ** 2)))
        o.append(circ(X(fr), yy, 4.5, "dot"))
        o.append(T(X(fr) + dx, yy + dy, lab, "t", "end" if dx < 0 else "start"))
    return svg(W, H, "".join(o), "Bode magnitude plot of the divider and capacitor, log frequency 100 Hz to 2 MHz, with the voice band shaded and five marked frequencies")


# ----------------------------------------------------------------------------- figure 4: the levels
def fig_levels():
    W, H = 860, 400
    xs = (170, 430, 690)
    y0, y1 = 50, 300

    def Y(v):
        return y1 - (math.log10(v) + 1) / 2 * (y1 - y0)       # 0.1 V at the bottom, 10 V at the top

    o = [T(60, 22, "Peak-to-peak volts at the three stations, log scale: the pulses, the node, the speaker", "h")]
    for v, lab in ((0.1, "0.1 V"), (0.3, "0.3"), (1.0, "1 V"), (3.0, "3"), (10.0, "10 V")):
        o.append(line(60, Y(v), 820, Y(v), "grid"))
        o.append(T(52, Y(v) + 4, lab, "num", "end"))
    o.append(line(60, y1, 820, y1))
    full = (VIO, num["node_full"], num["out_full"])
    dflt = (VIO, num["node_default"], num["out_default"])
    o.append(poly(list(zip(xs, [Y(v) for v in dflt])), "s2"))
    o.append(poly(list(zip(xs, [Y(v) for v in full])), "s1"))
    for x, v in zip(xs, full):
        o.append(circ(x, Y(v), 5, "dot1"))
    for x, v in zip(xs[1:], dflt[1:]):
        o.append(circ(x, Y(v), 5, "dot2"))
    o.append(T(xs[0], Y(VIO) - 12, f"{VIO:.1f} V pulses, both levels", "num", "middle"))
    o.append(T(xs[1] + 12, Y(num["node_full"]) - 8, f"{num['node_full']:.2f} V full scale", "num"))
    o.append(T(xs[1] + 12, Y(num["node_default"]) + 16, f"{num['node_default']:.2f} V everyday", "num"))
    o.append(T(xs[2] + 12, Y(num["out_full"]) + 4, f"{num['out_full']:.1f} V, {num['p_full']:.2f} W", "num"))
    o.append(T(xs[2] + 12, Y(num["out_default"]) + 4, f"{num['out_default']:.1f} V, {num['p_default']:.2f} W", "num"))
    # ceilings at the speaker station
    cap37, cap33 = num["swing_cap"][V_PACK], num["swing_cap"][V_PACK_SAG]
    for v in (cap37, cap33):
        o.append(line(xs[2] - 90, Y(v), xs[2] + 8, Y(v), "ref"))
    o.append(T(xs[2] - 96, Y(cap37) - 4, f"{cap37:.1f} V: the bridge's ceiling on a {V_PACK:.1f} V pack, and the speaker's {P_SPK_RATED:.1f} W ({num['vpp_rated']:.1f} V)", "fn", "end"))
    o.append(T(xs[2] - 96, Y(cap33) + 14, f"{cap33:.1f} V: the ceiling at {V_PACK_SAG:.1f} V, a pack sagging under a hover", "fn", "end"))
    # station labels
    for x, l1, l2 in ((xs[0], "the pin", "GPIO9, a 1 MHz pulse train"),
                      (xs[1], "the node", f"÷{1 / num['k_loaded']:.1f} through 10 kΩ and 1.5 kΩ, 22 nF across"),
                      (xs[2], "the speaker", f"×{num['gain']:.1f} (24 dB), two outputs in antiphase")):
        o.append(T(x, y1 + 22, l1, "h", "middle"))
        o.append(T(x, y1 + 38, l2, "fn", "middle"))
    o.append(legend(60, y1 + 74, (("s1", f"full scale, density ±{D_FULL}"), ("s2", f"everyday level, density ±{D_DEFAULT}, 6 dB down"))))
    return svg(W, H, "".join(o), "Voltage level diagram on a log scale from the pin through the filter node to the speaker, for full scale and the everyday level, with the amplifier's swing ceilings marked")


# ----------------------------------------------------------------------------- figure 5: how loud, how far
def fig_spl():
    W, H = 860, 380
    x0, x1, y0, y1 = 70, 820, 40, 300
    lo, hi = 0.05, 4.0

    def X(d):
        return x0 + (math.log10(d) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (x1 - x0)

    def Y(db):
        return y1 - (db - 40) / 60 * (y1 - y0)

    o = [T(x0, 22, "Sound level against distance from the drone: the speaker at its two levels, and the propellers' own noise (estimate)", "h")]
    for db in range(40, 101, 10):
        o.append(line(x0, Y(db), x1, Y(db), "grid"))
        o.append(T(x0 - 8, Y(db) + 4, f"{db} dB", "num", "end"))
    o.append(line(x0, y1, x1, y1))
    for d, lab in ((0.05, "5 cm"), (0.1, "10 cm"), (0.3, "30 cm"), (1.0, "1 m"), (3.0, "3 m")):
        o.append(line(X(d), y1, X(d), y1 + 5))
        o.append(T(X(d), y1 + 18, lab, "fn", "middle"))
    ds = [lo * (hi / lo) ** (i / 60) for i in range(61)]
    band = [(X(d), Y(PROP_1M[1] - dB(d))) for d in ds] + [(X(d), Y(PROP_1M[0] - dB(d))) for d in reversed(ds)]
    o.append(polygon(band, "noise"))
    o.append(poly([(X(d), Y(num["spl1_default"] - dB(d))) for d in ds], "s2"))
    o.append(poly([(X(d), Y(num["spl1_full"] - dB(d))) for d in ds], "s1"))
    o.append(circ(X(1.0), Y(SPEECH_1M), 5.5, "hol"))
    o.append(T(X(1.0) - 11, Y(SPEECH_1M) + 4, f"{SPEECH_1M:.0f} dB: a person talking to you from 1 m", "t", "end"))
    o.append(T(X(hi) - 6, Y(num["spl1_full"] - dB(hi)) - 8, f"full: {num['spl1_full']:.0f} dB at 1 m", "num", "end"))
    o.append(T(X(hi) - 6, Y(num["spl1_default"] - dB(hi)) + 16, f"everyday: {num['spl1_default']:.0f} dB at 1 m", "num", "end"))
    o.append(T(X(0.3), Y(PROP_1M[1] - dB(0.3)) - 8, f"the propellers in flight, {PROP_1M[0]:.0f} to {PROP_1M[1]:.0f} dB(A) at 1 m, est.", "t", "middle"))
    o.append(legend(x0, y1 + 44, (("s1", f"speaker at full scale, {num['p_full']:.2f} W"), ("s2", f"speaker at the everyday level, {num['p_default']:.2f} W"), ("noise", "the aircraft's own noise"))))
    return svg(W, H, "".join(o), "Sound pressure level against distance on a log scale for the speaker at two levels, a shaded band for the propellers' estimated noise and a marker for conversational speech at 1 m")


# ----------------------------------------------------------------------------- figure 6: what the grams cost
def fig_mass():
    W, H = 860, 360
    panels = ((60, 400, "Thrust to weight on the vendor's 68 gf", 1.0, 3.0, lambda m: THRUST / m, "{:.2f}", (("gate 2.0", GATE), ("hover floor 1.5", FLOOR))),
              (480, 820, "Minutes in the air, hover, lamp off", 1.5, 4.5, fly_minutes, "{:.1f} min", ()))
    o = []
    for (x0, x1, title, ylo, yhi, fn, fmt, refs) in panels:
        y0, y1 = 50, 290
        mlo, mhi = 25.0, 50.0

        def X(m, x0=x0, x1=x1):
            return x0 + (m - mlo) / (mhi - mlo) * (x1 - x0)

        def Y(v, ylo=ylo, yhi=yhi):
            return y1 - (v - ylo) / (yhi - ylo) * (y1 - y0)

        o.append(T(x0, 22, title, "h"))
        steps = 4 if yhi - ylo <= 2.5 else 6
        for i in range(steps + 1):
            v = ylo + (yhi - ylo) * i / steps
            o.append(line(x0, Y(v), x1, Y(v), "grid"))
            o.append(T(x0 - 8, Y(v) + 4, f"{v:.1f}", "num", "end"))
        o.append(line(x0, y1, x1, y1))
        for m in (25, 30, 35, 40, 45, 50):
            o.append(line(X(m), y1, X(m), y1 + 5))
            o.append(T(X(m), y1 + 18, f"{m} g", "fn", "middle"))
        for lab, v in refs:
            o.append(line(x0, Y(v), x1, Y(v), "ref"))
            o.append(T(x0 + 6, Y(v) - 5, lab, "fn"))
        o.append(poly([(X(m), Y(fn(m))) for m in [mlo + (mhi - mlo) * i / 100 for i in range(101)]], "s1"))
        for m, lab, dy in ((M_BEFORE, "before the speaker", -12), (M_VOICE, "with voice", -12)):
            o.append(circ(X(m), Y(fn(m)), 5.5, "dot"))
            o.append(T(X(m) + 10, Y(fn(m)) + dy, f"{m:.1f} g: {fmt.format(fn(m))}, {lab}", "t"))
        if refs:
            mf = num["m_floor"]
            o.append(circ(X(mf), Y(FLOOR), 5.5, "hol"))
            o.append(T(X(mf) - 10, Y(FLOOR) + 20, f"{mf:.0f} g: the floor", "t", "end"))
    return svg(W, H, "".join(o), "Two panels against flying mass from 25 to 50 g: thrust to weight with the 2.0 gate and 1.5 floor, and hover minutes, with the 33.5 g and 37.5 g builds marked")


FIGS = {"clock": fig_clock, "pdm": fig_pdm, "filter": fig_filter, "levels": fig_levels, "spl": fig_spl, "mass": fig_mass}


# ----------------------------------------------------------------------------- the text
def chapters():
    n = num
    tw0, tw1 = n["tw"][M_BEFORE], n["tw"][M_VOICE]
    return [
        ("The whole thing in one breath", [
            f"The drone already had a microphone: a grain of a MEMS part on the camera board, wired inside the controller, that sends sound as single bits a couple of million times a second. The speaker is the new part, and it had one pin to work with. So the controller makes sound the same way the microphone hears it, as a stream of single bits a million times a second, a resistor and a capacitor turn the stream back into a voltage, a class-D amplifier the size of a thumbnail multiplies it by {n['gain']:.0f} straight from the flight pack, and a sealed speaker the size of a postage stamp on the tail turns it into about {n['spl1_full']:.0f} dB at a metre.",
            f"The price is {n['added']:.1f} g, which takes thrust to weight from {tw0:.2f} to {tw1:.2f}, under the 2.0 gate the build set itself and inside the 1.5 floor the hover test allows. The limit is the propellers, not the parts: in flight they are louder than anything the drone could say or hear. This page takes each piece in the order the signal does and shows the working behind the numbers on the build page.",
        ]),
        ("Hearing for free: a microphone that speaks in single bits", [
            f"A MEMS microphone is a capacitor whose one plate is a diaphragm about a millimetre across, etched into silicon. Sound moves the plate, the capacitance changes, and an amplifier on the same chip turns that into a voltage. This one, a MEMSensing MSM261D3526H1CPM in a 3.5 × 2.65 × 0.94 mm can with a 0.33 mm hole in its lid, goes one step further: it carries its own sigma-delta modulator and sends out a pulse-density stream, one bit per clock, in which a louder sound is a denser run of ones. Its datasheet gives it {MIC_SENS:.0f} dBFS at 94 dB SPL, so it clips at {n['mic_full_spl']:.0f} dB SPL, the level of a chainsaw at arm's length; a signal-to-noise ratio of {MIC_SNR:.0f} dB(A), so its own hiss sits at the equivalent of {n['mic_floor_spl']:.0f} dB SPL, a quiet library; and it takes {n['mic_ma']:.2f} mA.",
            f"It costs nothing because Seeed put it on the Sense board next to the camera, facing up through the board, and wired its clock and data to GPIO42 and GPIO41 through the board-to-board connector; neither pin reaches a castellation, so the drone's pin budget never saw them. The ESP32-S3's first I2S controller has a hardware filter that takes the one-bit stream in, decimates it to {BITS_PCM}-bit samples and writes them to memory by DMA, so the flight controller never touches a sample until a {F_S / 1000:.0f} kHz buffer is ready.",
            f"One number on that path wants attention. The ESP-IDF driver runs the microphone's clock at {PDM_RATIOS[0]} times the sample rate by default, which at {F_S / 1000:.0f} kHz is {n['pdm_clk'][64] / 1e6:.3f} MHz. The microphone's datasheet lists a low-power mode from {MIC_CLK_LP[0] / 1e3:.0f} to {MIC_CLK_LP[1] / 1e3:.0f} kHz and a standard mode from {MIC_CLK_STD[0] / 1e6:.1f} to {MIC_CLK_STD[1] / 1e6:.1f} MHz, and {n['pdm_clk'][64] / 1e6:.3f} MHz falls in the gap between them. Seeed's own example runs there and calls it stable, and it probably is, but it is off the sheet. Asking the driver for the {PDM_RATIOS[1]}× ratio instead puts the clock at {n['pdm_clk'][128] / 1e6:.3f} MHz, squarely in the standard band, for the same {F_S / 1000:.0f} kHz samples and one line of configuration. The microphone task will.",
            ("fig", "clock", f"The microphone's three clock bands from its datasheet on a log scale, with the two clocks the ESP32-S3 offers at {F_S / 1000:.0f} kHz. The default lands in the gap; the 128× ratio lands in the standard band."),
            f"Speech from a metre away is about {SPEECH_1M:.0f} dB SPL at the microphone, {n['speech_dbfs']:.0f} dB below full scale and {SPEECH_1M - n['mic_floor_spl']:.0f} dB above its floor: a clean recording in a quiet room. The 16-bit samples go up the Wi-Fi link to the desk computer, which does the listening; the drone keeps none of it.",
        ]),
        ("One pin left, so the speaker goes analog", [
            f"The XIAO brings eleven pins to its castellations and the drone uses ten: four motors, the pack divider, two for the I²C bus, the lamp, the forward ranger's enable and the motion sensor's interrupt. D10, GPIO9, is the last one. The owned I²S amplifiers need three pins (clock, word select, data), so they are out; the payload plan said so in October and parked a piezo beeper across the flashlight's LED as the only sound the drone would make. One pin can still make a voice, if it goes analog.",
            f"The ESP32-S3 has no analog output pin, but it has eight sigma-delta modulators that can drive any GPIO, and Espressif documents them as an 8-bit DAC. Each one takes a density, a signed byte from −128 to 127, and produces a pulse train at a clock of your choosing whose fraction of high pulses is (density + 128)/256; the voltage a low-pass filter recovers is VDD/256 × density + VDD/2, so density 0 is a steady 1.65 V and a sine of densities is a sine of volts riding on it. The modulator on this chip is second-order: the error it makes in each pulse is fed back twice over, which pushes the quantisation noise upward in frequency, away from the sound and toward the clock, where a filter can take it off.",
            f"The firmware feeds it from a ring buffer of samples. A hardware timer fires {F_S / 1000:.0f} 000 times a second and its interrupt writes the next sample into the density register: one register write every {1e6 / F_S:.1f} µs, about {n['isr_share']:.1f} % of one core at a microsecond each, and no DMA, because the modulator has no DMA path. Espressif's own example does exactly this with a 10 kHz timer and a sine table. {F_SDM / 1e6:.0f} MHz is the pulse rate the documentation uses in its own example and {n['osr']:.0f} times the {F_S / 2000:.0f} kHz the samples can carry; a second-order modulator at that oversampling keeps its own noise about {n['snr_mod2']:.0f} dB below a full-scale tone, while eight bits of density can do no better than {n['snr_bits']:.0f} dB. The knob, not the modulator, sets the floor, and {n['snr_bits']:.0f} dB is telephone grade, which is what a sealed 20 mm speaker can use. A faster clock would buy nothing audible.",
            ("fig", "pdm", f"A 1 kHz tone at the everyday level, simulated: the timer's {F_S / 1000:.0f} kHz steps over the tone they stand for; the modulator's {int(2e-3 * F_SDM)} pulses over two milliseconds as a density strip with forty raw pulses shown at the crest and at the crossing; and the voltage at the node after the divider and the capacitor, one microsecond at a time, against the tone itself. The node lags by about {math.degrees(math.atan(1000 / n['fc_loaded'])):.0f}°; the fuzz on it is the modulator's shaped noise, tens of kilohertz and up, which neither the speaker nor the ear can follow."),
            f"Espressif adds that densities between −90 and 90 give better randomness, and that is the second-order modulator talking: driven close to full scale it falls into short repeating patterns, idle tones, that a filter cannot remove. The firmware's everyday level is ±{D_DEFAULT}, 6 dB under full scale, inside that range with room to spare; full scale is for a shout. The simulation above runs the same modulator and stays well behaved at ±{D_DEFAULT}. Why sigma-delta and not plain PWM from the LED controller, which could also make eight bits at 300 kHz? Both would work. The modulator is the peripheral Espressif built and documents for this, it shapes its noise upward instead of leaving it at one carrier, and it costs the same one pin.",
        ]),
        ("A divider that is also the filter", [
            f"The pin swings {VIO:.1f} V and the amplifier wants a fraction of a volt, so the first job of the two resistors is to divide. 10 kΩ over 1.5 kΩ is a ratio of {1 / n['k']:.1f}; with the amplifier's own {R_IN / 1000:.0f} kΩ input resistor hanging across the lower leg it is {1 / n['k_loaded']:.1f}, which turns a full-scale sine of densities, {VIO * 254 / 256:.2f} V peak to peak at the pin, into {n['node_full']:.2f} V at the node ({n['node_full_open']:.2f} with nothing connected, the figure on the build page). The everyday level is {n['node_default']:.2f} V. The {n['node_dc'] * 1000:.0f} mV of standing voltage from the density-zero midpoint goes no further than the amplifier's input capacitor.",
            f"The 22 nF across the lower leg is the second job. Seen from the capacitor the three resistors in parallel are {n['r_th_loaded']:.0f} Ω, and {n['r_th_loaded']:.0f} Ω into 22 nF is a corner at {n['fc_loaded'] / 1000:.1f} kHz ({n['fc'] / 1000:.1f} kHz with the amplifier disconnected). Below the corner the node follows the density; above it the response falls 20 dB for every tenfold in frequency. The voice band, 300 to 3 400 Hz, loses at most {-n['h'][3400.0]:.1f} dB at its top. The pulses at {F_SDM / 1e6:.0f} MHz are {-n['h'][F_SDM]:.0f} dB down, {n['carrier_node_mv']:.1f} mV of ripple on a {n['node_full'] * 1000:.0f} mV signal, and the amplifier's switching at {F_SW / 1e3:.0f} kHz would be {-n['h'][F_SW]:.0f} dB down if it ever came back that way. What a first-order filter leaves is the modulator's shaped noise between about 20 and 200 kHz, the fuzz on the simulated trace in the figure above: above the speaker's range and far above hearing.",
            ("fig", "filter", f"The divider and the capacitor's response against frequency, relative to the voice band, from 100 Hz to 2 MHz. The corner at {n['fc_loaded'] / 1000:.1f} kHz, the top of the voice band, the 16 kHz stair-steps, the amplifier's 260 kHz and the 1 MHz pulses are marked."),
            f"A first-order filter is gentle, and the one thing it does not finish is the stair-steps. The timer holds each sample for {1e6 / F_S:.1f} µs, so a 1 kHz tone also carries faint images at 15 and 17 kHz; the hold itself attenuates them by about {-n['sinc_15k']:.0f} dB and the filter by another {-n['h'][16000.0]:.0f}, about {-n['image_db']:.0f} dB in all, a whistle at the edge of adult hearing that most ears will not find. Speech has little above 4 kHz to make images from. Test C11 listens for it anyway.",
            f"Espressif recommends an active filter after the modulator, for isolation and so as not to lose voltage. Here the isolation exists already: the amplifier's {R_IN / 1000:.0f} kΩ input is {R_IN / n['r_th_loaded']:.0f} times the node's {n['r_th_loaded']:.0f} Ω, so it loads the divider by {(1 - n['k_loaded'] / n['k']) * 100:.0f} %, and losing voltage is the point, since {VIO:.1f} V into a 24 dB amplifier would be {VIO * n['gain']:.0f} V of demand on a {V_PACK:.1f} V pack. Three passive parts from the owned kits, half a gram with the reservoir, do the job an op-amp board would do at a gram and a rail.",
        ]),
        ("Twenty-four decibels and a bridge: the class-D amplifier", [
            f"A class-D amplifier does not amplify the waveform; it switches. The PAM8403 compares the input with a triangle wave and drives its output transistors fully on or fully off at {F_SW / 1e3:.0f} kHz, with the on-time proportional to the signal. The speaker's own inductance and the ear do the averaging, the transistors are never half on, and almost no power is lost in them: the datasheet gives up to 90 %, 83 % at a 4 Ω load driven hard. At the full {n['p_full']:.2f} W into this speaker the chip would warm by about {n['heat_full'] * 1000:.0f} mW; a linear amplifier of the old kind would throw away as much as it delivered and want a heatsink, a bigger board and, for this swing, a higher rail.",
            f"Its gain is fixed at 24 dB, {n['gain']:.1f} times, which is why the divider is there. Its two outputs for one channel swing in opposite directions about half the supply, so the speaker between them sees twice the swing of either and four times the power that one output into ground could give: a bridge. On a {V_PACK:.1f} V pack, after the {R_ON * 1000:.0f} mΩ of the two switches in the path, that is {n['swing_cap'][V_PACK]:.1f} V peak to peak at most. Full scale asks for {n['out_full']:.1f} V and needs a pack above {n['v_need_full']:.2f} V; once the pack sags toward {V_PACK_SAG:.1f} V under a hover the ceiling is {n['swing_cap'][V_PACK_SAG]:.1f} V and full scale would clip. The everyday level asks for {n['out_default']:.1f} V and needs {n['v_need_default']:.2f} V, which is less than the chip's own {V_UVLO:.1f} V cut-out, so it never clips on any pack the drone will fly. The datasheet puts {P_AMP_1PC:.2f} W into 8 Ω at 3.6 V and 1 % distortion; full scale here is {n['p_full']:.2f} W, under the speaker's {P_SPK_RATED:.1f} W rating, which at 8 Ω is itself {n['vpp_rated']:.1f} V peak to peak, the same ceiling the pack sets.",
            ("fig", "levels", f"Peak-to-peak volts at the three stations on a log scale, for full scale and the everyday level: the pin's {VIO:.1f} V pulses, the node after the divider, the speaker after the bridge. The two dashed lines are the bridge's ceilings on a {V_PACK:.1f} V and a {V_PACK_SAG:.1f} V pack."),
            f"Neither output is ground. OUT L− is a live amplifier output sitting at half the supply, and tying it to the frame would short one half of the bridge; the chip would detect it and mute, and at best the speaker would get half the voltage and a quarter of the power. The right channel's input and both of its outputs stay open. The board has no shutdown pad, so the amplifier is always on at {I_Q * 1000:.0f} mA, {n['iq_share']:.1f} % of a hover and {n['iq_hours']:.0f} hours of a pack on the ground; and at power-up its bypass capacitor charges through the input stage and the speaker gives a soft pop, which the datasheet says a shutdown pin would have hidden. The drone will click when it wakes.",
            f"It runs from VBAT, the pack itself, because its range is 2.5 to 5.5 V and because the XIAO's 3.3 V regulator already feeds the controller, the camera and three sensors and should not also supply the {n['i_amp_full'] * 1000:.0f} mA average and {n['i_peak_full'] * 1000:.0f} mA crests of a loud sentence. Those crests come in bursts at the audio frequency and at {F_SW / 1e3:.0f} kHz; the pack's leads cannot deliver them instantly, so a 47 to 100 µF capacitor across the amplifier's power pads holds the rail through each burst, beside the 1 µF ceramic the board carries. The datasheet asks for a bulk capacitor of at least 20 µF for this reason. The same reservoir keeps the amplifier's bursts off the divider that the flight controller reads the pack voltage from.",
        ]),
        ("A sealed box five millimetres thick: the speaker", [
            f"A bare speaker element in the open is nearly silent at low frequencies: the back of the cone pushes air out while the front pulls it in, and round the edge the two cancel. A box behind the cone stops that. The Same Sky part is such a box, 20 × 13 mm and 4.9 mm thick in ABS, with a PEEK cone and a neodymium magnet, and its sealed back is why it was chosen over the 0.5 g bare element inside it: on a wire frame with nothing to mount it to, the bare element would have had no baffle and no bass at all.",
            f"The datasheet gives a resonance at {F_O / 1000:.1f} kHz and a response from {F_SPK_LO / 1000:.1f} to {F_SPK_HI / 1000:.0f} kHz. Below resonance a sealed speaker falls 12 dB for every halving of frequency: {F_O / 2:.0f} Hz is {n['below_fo'][F_O / 2]:.0f} dB down, {F_O / 4:.0f} Hz is {n['below_fo'][F_O / 4]:.0f}. The fundamentals of a voice, 100 to 250 Hz, do not come out of it. They do not need to: the ear hears a pitch in the harmonics that remain, which is how a telephone has always worked, and the words live in the band from 300 to 3 400 Hz that the speaker, the filter and the 8-bit converter all pass. The chain is telephone grade from end to end, and not by accident.",
            f"Its {R_SPK:.0f} Ω is the load the amplifier's table is written for, and its {P_SPK_RATED:.1f} W rating ({P_SPK_MAX:.1f} W for a second at a time) is above the {n['p_full']:.2f} W that full scale can ask. It is omnidirectional through the voice band: at 1 kHz the wavelength is {n['lambda_1k']:.0f} mm against a {SPK_R * 2000:.0f} mm cone, and the sound only begins to beam above {n['ka1'] / 1000:.0f} kHz. So grille up on the tail costs no loudness in any direction a listener could be; it keeps the grille out of the straps and away from the pan, which would otherwise make a second box in front of the first.",
            f"The datasheet's {SPL_REF:.0f} dB is at {P_REF:.1f} W and 10 cm. Power counts in tenths: {n['p_full']:.2f} W is {n['spl10_full'] - SPL_REF:.1f} dB down, {n['spl10_default']:.0f} dB at 10 cm for the everyday level. Distance counts in squares: every doubling takes 6 dB, so 1 m is 20 dB under 10 cm. That makes {n['spl1_full']:.0f} dB at a metre at full scale and {n['spl1_default']:.0f} at the everyday level, against about {SPEECH_1M:.0f} dB for a person talking to you from the same distance: a clear voice across a desk, a quiet one across a room, {n['spl3_full']:.0f} dB at 3 m.",
            ("fig", "spl", f"Sound level against distance from the drone, both on log scales: the speaker at full scale and at the everyday level, the propellers' own noise in flight as an estimated band, and a person speaking at 1 m. The speaker's lines and the propellers' band fall together, 6 dB per doubling, so the gap between them does not close with distance."),
        ]),
        ("Where it sits and what it weighs", [
            f"The speaker lies on the tail of the floor pan, {-Y_SPK[1]:.1f} to {-Y_SPK[0]:.1f} mm behind the centre, and the amplifier hangs under the hood at the nose, {Y_AMP[0]:.0f} to {Y_AMP[1]:.1f} mm ahead of it. Two grams at {sum(Y_SPK) / 2:.1f} mm and one and a half at +{sum(Y_AMP) / 2:.1f} mm move the aircraft's centre of gravity {abs(n['cg']):.2f} mm toward the tail, and with the motors {Y_MOTOR:.0f} mm either side of the centre the rear pair carries {n['rear_share'] * 100:.1f} % of the hover instead of 50. The controller trims that without being told. The speaker's top at {Z_SPK_TOP:.1f} mm is {n['prop_gap']:.1f} mm under the propeller plane, and the amplifier's components face the floor with 1.5 mm of air on the skids, 0.5 mm short of the front axle.",
            f"Two straps of the clear tape hold the speaker to the pack, and a loop of 30 AWG through each flange hole ties it to the rails. In a full-throttle punch the speaker weighs about {2 * M_SPK:.0f} gf; the tape alone holds that many times over, and the wire loops are there for the day the adhesive warms in the sun and lets go. Nothing is glued, painted or covered: the housing is black, one of the family's colours, and the amplifier's blue board is out of sight under the hood.",
            f"The grams are the real cost. A hovering rotor's power goes as the thrust to the power 1.5, so the hover current scales the same way with mass: {I_REF:.1f} A at {M_REF:.0f} g becomes {n['i_hover'][M_BEFORE]:.1f} A at {M_BEFORE:.1f} g and {n['i_hover'][M_VOICE]:.1f} A at {M_VOICE:.1f} g, {n['c_rate']:.0f} C from a {PACK_C:.0f} C pack. Thrust to weight on the vendor's {THRUST:.0f} gf falls from {tw0:.2f} to {tw1:.2f}, and since a brushed motor's thrust rises about as the square of its duty, the hover command rises from {n['hover_cmd'][M_BEFORE]:.0f} to {n['hover_cmd'][M_VOICE]:.0f} %. The gate the build set itself is 2.0, which the {M_BEFORE:.1f} g aircraft just clears at {n['m_gate']:.0f} g; the floor the hover test accepts is 1.5, which is {n['m_floor']:.0f} g. Eighty per cent of the pack over {n['i_hover'][M_VOICE]:.1f} A, less 5 % for the controller and the camera, is {n['t_fly'][M_VOICE]:.1f} minutes in the air against {n['t_fly'][M_BEFORE]:.1f} before: the voice costs about {n['t_lost'] * 60:.0f} seconds a flight.",
            ("fig", "mass", f"Thrust to weight and hover minutes against flying mass from 25 to 50 g, with the {M_BEFORE:.1f} g and {M_VOICE:.1f} g builds marked. The dashed lines are the 2.0 gate and the 1.5 floor; the floor is reached at {n['m_floor']:.0f} g."),
            f"If the first hover reads under 1.8, the build document names the way back: the bare 0.5 g element, or the 716 motors already in the plan. The ledger's masses are estimates until the coin balance weighs them.",
        ]),
        ("The honest limit: the propellers drown both ends", [
            f"Nobody has published a sound-level measurement of a whoop this size. The nearest is an 80 g Tello, measured at 46 dB(A) from 13 m, which is about 68 dB(A) at 1 m; a 1 kg Phantom measures 70 to 80 dB(A) at 1.5 m. A {M_VOICE:.0f} g aircraft on four 31 mm propellers at 30 000 rpm is likely in the {PROP_1M[0]:.0f} to {PROP_1M[1]:.0f} dB(A) range at 1 m, and the page treats that as an estimate.",
            f"The microphone sits about {D_MIC_PROP * 100:.0f} cm from the nearest propeller, where that noise is {n['prop_at_mic'][0]:.0f} to {n['prop_at_mic'][1]:.0f} dB: under the microphone's {MIC_AOP:.0f} dB overload point, so it does not clip, but {n['prop_margin'][0]:.0f} to {n['prop_margin'][1]:.0f} dB above a voice speaking from a metre away. No recogniser works 35 dB under the noise, and the noise is tonal and in the voice band: the motors' fundamental is around 500 Hz with harmonics above it, and it also reaches the microphone through the frame, since the brushed motors shake the stainless rails the camera board stands on. In flight the drone cannot hear you. Commands in flight go through the desk computer's own microphone, which hears you fine.",
            f"The speaker's {n['spl1_full']:.0f} dB at 1 m is a few decibels under the propellers' {PROP_1M[0]:.0f} to {PROP_1M[1]:.0f}, and both fall together with distance, so in flight a sentence is audible as a voice under the whine at arm's length and lost beyond it. A tone or a chime cuts through better than words. So the design is for a drone that announces while flying and converses when it has landed, perched on the desk or in a hand: there the propellers are off, the microphone's floor is a library and the speaker is a voice across a desk.",
            f"Talking and listening at once is the other limit. The speaker is {SPK_TO_MIC * 1000:.0f} mm from the microphone and at full scale puts about {n['spl_at_mic']:.0f} dB SPL on it, well under its overload but far louder than a person in the room. The character server already takes turns, listening, then speaking, then listening again, and the firmware keeps the microphone stream muted while the speaker plays. There is no echo canceller on a flight controller, and none is needed if nobody talks over the drone.",
        ]),
        ("Over the air: what a voice costs the link", [
            f"The drone sends and receives plain 16-bit samples at {F_S / 1000:.0f} kHz: {n['kbps']:.0f} kbit/s each way, {n['frame_bytes']:.0f} bytes in each 20 ms frame. The camera stream on the same link is {CAM_MBPS[0]:.1f} to {CAM_MBPS[1]:.1f} Mbit/s, so the voice adds {n['link_share'][1]:.0f} to {n['link_share'][0]:.0f} % to it. Compressing it on the drone would save bandwidth nobody needs and cost the controller work it does need for the attitude loop; the character server already speaks this protocol in PCM, the same one Pip uses, so the drone is a wire and the desk computer does the listening, the thinking and the talking.",
            f"The delay is the Wi-Fi hop, 10 to 30 ms each way, plus the 20 ms frame: well under a tenth of a second before the server starts to think. Speech recognition, the reply and the voice synthesis take a second or two on the desk machine, and that, not the drone, is the pause the builder will hear.",
        ]),
    ]


def numbers():
    n = num
    return [
        (f"{1 / n['k_loaded']:.1f}", f"the divider's ratio with the amplifier's {R_IN / 1000:.0f} kΩ input across the lower leg: 1.5 kΩ ∥ 18 kΩ over 10 kΩ plus that ({1 / n['k']:.1f} with nothing connected)"),
        (f"{n['node_full']:.2f} V p-p", f"at the node at full scale: {VIO:.1f} V × 254/256 ÷ {1 / n['k_loaded']:.1f} ({n['node_full_open']:.2f} V unloaded, the build page's figure); {n['node_default']:.2f} V at the everyday ±{D_DEFAULT}"),
        (f"{n['fc_loaded'] / 1000:.1f} kHz", f"the corner: 1 over 2π × {n['r_th_loaded']:.0f} Ω × 22 nF, the three resistors in parallel as the capacitor sees them ({n['fc'] / 1000:.1f} kHz unloaded)"),
        (f"{-n['h'][F_SDM]:.0f} dB", f"the 1 MHz pulses at the node: a first-order filter {F_SDM / n['fc_loaded']:.0f} times above its corner; {n['carrier_node_mv']:.1f} mV of ripple"),
        (f"{n['snr_bits']:.0f} dB", f"what eight bits of density allow: 6.02 × {BITS} + 1.76; the second-order modulator at {n['osr']:.0f}× oversampling would allow about {n['snr_mod2']:.0f}"),
        (f"{n['gain']:.1f}×", "24 dB: 10 to the power 24/20; the PAM8403's fixed ratio of 142 kΩ to 18 kΩ, doubled by its second stage"),
        (f"{n['out_full']:.1f} V p-p", f"across the speaker at full scale, {n['node_full']:.2f} × {n['gain']:.1f}; {(n['out_full'] / (2 * math.sqrt(2))):.2f} V rms, {n['p_full']:.2f} W into 8 Ω"),
        (f"{n['swing_cap'][V_PACK]:.1f} V p-p", f"the bridge's ceiling on a {V_PACK:.1f} V pack: 2 × {V_PACK:.1f} × 8 / (8 + {R_ON:.2f}); {n['swing_cap'][V_PACK_SAG]:.1f} V at {V_PACK_SAG:.1f} V, {n['swing_cap'][V_PACK_FULL]:.1f} at {V_PACK_FULL:.1f}"),
        (f"{n['vpp_rated']:.1f} V p-p", f"the speaker's {P_SPK_RATED:.1f} W rating as a swing: 2√2 × √(0.8 × 8)"),
        (f"{n['heat_full'] * 1000:.0f} mW", f"the amplifier's heat at full scale: {n['p_full']:.2f} W × (1/{EFF_AMP:.2f} − 1)"),
        (f"{n['spl1_full']:.0f} dB", f"at 1 m at full scale: {SPL_REF:.0f} + 10 log({n['p_full']:.2f}/{P_REF:.1f}) − 20 log(1 m / 10 cm); {n['spl1_default']:.0f} dB at the everyday level"),
        (f"{n['ka1'] / 1000:.0f} kHz", f"where the speaker begins to beam: c over 2π × {SPK_R * 1000:.1f} mm; omnidirectional below"),
        (f"{n['pdm_clk'][64] / 1e6:.3f} MHz", f"the microphone's clock at the driver's default 64× ratio at {F_S / 1000:.0f} kHz, in the gap between its {MIC_CLK_LP[1] / 1e3:.0f} kHz and {MIC_CLK_STD[0] / 1e6:.1f} MHz bands; {n['pdm_clk'][128] / 1e6:.3f} MHz at 128×"),
        (f"{n['mic_full_spl']:.0f} dB SPL", f"the microphone's full scale: 94 dB SPL minus a sensitivity of {MIC_SENS:.0f} dBFS; its floor is 94 − {MIC_SNR:.0f} = {n['mic_floor_spl']:.0f} dB SPL"),
        (f"{n['prop_at_mic'][0]:.0f} to {n['prop_at_mic'][1]:.0f} dB", f"the propellers at the microphone: {PROP_1M[0]:.0f} to {PROP_1M[1]:.0f} dB(A) at 1 m (estimate) plus 20 log(1 m / {D_MIC_PROP * 100:.0f} cm)"),
        (f"{abs(n['cg']):.2f} mm", f"the centre of gravity's shift to the tail: ({M_SPK:.1f} g × {sum(Y_SPK) / 2:.1f} mm + {M_AMP:.1f} g × {sum(Y_AMP) / 2:.2f} mm) / {M_VOICE:.1f} g; the rear motors carry {n['rear_share'] * 100:.1f} %"),
        (f"{tw(M_VOICE):.2f}", f"thrust to weight: {THRUST:.0f} gf / {M_VOICE:.1f} g; {tw(M_BEFORE):.2f} before the speaker; the gate at {n['m_gate']:.0f} g, the floor at {n['m_floor']:.0f} g"),
        (f"{n['hover_cmd'][M_VOICE]:.0f} %", f"the hover command: √(1/{tw(M_VOICE):.2f}), thrust about as duty squared; {n['hover_cmd'][M_BEFORE]:.0f} % before"),
        (f"{n['i_hover'][M_VOICE]:.1f} A", f"the hover current: {I_REF:.1f} A × ({M_VOICE:.1f}/{M_REF:.0f})^1.5; {n['c_rate']:.0f} C of the pack"),
        (f"{n['t_fly'][M_VOICE]:.1f} min", f"in the air: 80 % of {PACK_MAH:.0f} mAh over {n['i_hover'][M_VOICE]:.1f} A, less 5 % for the controller and camera; {n['t_fly'][M_BEFORE]:.1f} min before"),
        (f"{n['kbps']:.0f} kbit/s", f"the voice on the link, each way: {F_S / 1000:.0f} kHz × {BITS_PCM} bits; {n['link_share'][1]:.0f} to {n['link_share'][0]:.0f} % of the camera stream"),
    ]


def tw(m):
    return THRUST / m


PARTS = [
    ("single-bit hearing, 120 dB of overload, a clock that should be 2.05 MHz", "XIAO ESP32-S3 Sense, whose camera board carries the microphone", "https://www.amazon.com/dp/B0C69FFVHH"),
    ("eight bits of density a million times a second, on the one free pin", "the same controller's sigma-delta modulator on GPIO9", "https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdm.html"),
    ("divide by 8.2 and roll off at 6 kHz", "10 kΩ and 1.5 kΩ from the owned resistor kit", "https://www.amazon.com/dp/B0F4P352BB"),
    ("the capacitor that averages the pulses", "22 nF from the owned ceramic kit", "https://www.amazon.com/dp/B07P7HRGT9"),
    ("the reservoir that holds the rail through a loud word", "47 to 100 µF from the owned electrolytic kit", "https://www.amazon.com/dp/B0C1VBXCQM"),
    ("24 dB, a bridge, switching at 260 kHz", "PAM8403 class-D amplifier board, a 5-pack, the version without the knob, the one line to buy", "https://www.amazon.com/dp/B0DYYX8DF9"),
    ("a sealed box, 1.3 kHz resonance, 91 dB at 10 cm", "Same Sky enclosed speaker, one of Pip's two spares", "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309"),
    ("the straps and the ties", "the clear heat tape bought 2026-11-07 and the owned 30 AWG wire", "https://www.amazon.com/dp/B0BD84GGPV"),
]

SOURCES = [
    ("PAM8403 datasheet, Diodes Incorporated, DS36439 Rev. 2-3", "https://www.diodes.com/assets/Datasheets/PAM8403.pdf"),
    ("ESP-IDF, sigma-delta modulation driver for the ESP32-S3", "https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdm.html"),
    ("ESP-IDF example sdm_dac: a sine from a timer-fed modulator", "https://github.com/espressif/esp-idf/tree/master/examples/peripherals/sigma_delta/sdm_dac"),
    ("ESP-IDF, I2S driver for the ESP32-S3: PDM RX, 64× and 128× clocks", "https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/i2s.html"),
    ("MSM261D3526H1CPM datasheet, MEMSensing, DS-042 Ver. 1.2", "https://cdn.shopify.com/s/files/1/0174/1800/files/mic-MSM261D3526H1CPM-ENG.pdf"),
    ("XIAO ESP32S3 Sense expansion board schematic v1.2 (the microphone's part number) and the wiki's microphone page", "https://wiki.seeedstudio.com/xiao_esp32s3_sense_mic/"),
    ("CES-20134-088PM datasheet, Same Sky", "https://sameskydevices.com/product/resource/ces-20134-088pm.pdf"),
    ("Hui et al. 2021, drone noise at distance (the Tello figure)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8430946/"),
    ("Intaratep et al. 2016, Phantom II noise in an anechoic chamber", "https://www.bu.edu/ufmal/files/2016/07/aiaa-2016-2873.pdf"),
    ("Speech at about 60 dB SPL at 1 m (Scollie 2009, after Pearsons et al. 1977)", "https://www.audiologyonline.com/ask-the-experts/stimulus-levels-for-pediatric-rem-180"),
]


def next_text():
    n = num
    return (f"The amplifier 5-pack is in the builder's Amazon cart and not yet ordered; everything else is on hand. At build step 1, with the pack on the bench, test C11: a 1 kHz tone from the modulator should read about {n['node_full_open']:.2f} V peak to peak at the node with the amplifier disconnected and about {n['node_full']:.2f} V with it connected, play clean, and show under 20 mA of quiescent draw (the datasheet's typical is {I_Q * 1000:.0f} mA at 3.6 V). "
            f"At step 6, test C12: props off, a spoken sentence transcribed on the desk server and its reply heard at 1 m, both over the drone's own Wi-Fi with the camera running. "
            f"Firmware: the microphone task asks the I2S driver for the 128× ratio, so the clock is {n['pdm_clk'][128] / 1e6:.2f} MHz; the playback task keeps the everyday level at ±{D_DEFAULT} and mutes the microphone while it plays. If an idle tone is audible at any level, the fix is in software: keep the density within ±{D_CLEAN} and, if that is not enough, raise the pulse rate. "
            f"The first measurements replace this page's estimates: the mass on the coin balance, the hover command, the voltage at the node, the sound at 1 m if a meter is ever to hand.")


# ----------------------------------------------------------------------------- the outputs
PAGE_CSS = (":root{--c1:#2A64B0;--c2:#A3580A;--c1-soft:#DCE6F3;--c2-soft:#F3E6D4}"
            "@media (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){--c1:#4F86C8;--c2:#BF8A2A;--c1-soft:#1D2F45;--c2-soft:#3B2E14}}"
            ":root[data-theme=\"dark\"]{--c1:#4F86C8;--c2:#BF8A2A;--c1-soft:#1D2F45;--c2-soft:#3B2E14}"
            "figure svg{width:100%;height:auto} td,th{min-width:0} .src li{margin:4px 0;font-size:15px}")


def page_html(figs):
    style = re.search(r"<style>.*?</style>", (PAGES / "custom-build.html").read_text(encoding="utf8"), re.S).group(0)
    o = ['<title>XS Drone Voice Physics</title>',
         '<meta name="claude:viewport-fit-sides" content="cover">',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=Source+Code+Pro:wght@400;600&display=swap">',
         style,
         f"<style>{PAGE_CSS}</style>",
         '<div class="wrap">',
         '<div class="masthead"><div class="eyebrow">XS drone &middot; step 2: the science and engineering &middot; voice</div>',
         '<h1>Why it hears for free and talks through one pin</h1>',
         f'<div class="sub">The working behind the microphone and the speaker added to the drone on {APPROVED} and approved that night: a microphone that speaks in single bits, a sigma-delta modulator on the last free pin, a divider that is also the filter, a class-D bridge on the flight pack, a sealed speaker on the tail, what the grams cost, and the limit the propellers set. Read after <a href="{BUILD_PAGE}" target="_blank" rel="noopener">XS Drone Custom Build</a>; the link it talks over is on <a href="{FOLLOW_PAGE}" target="_blank" rel="noopener">XS Drone Following</a>. Written {WRITTEN}. Nothing measured yet: every figure is derived from the datasheets and the build page\'s numbers, and the two waveforms are simulated. Source of truth: <code>xs_drone/docs/voice-physics.md</code>.</div></div>']
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
    o.append(f'<hr><p class="sub">Built by <code>docs/pages/gen/voice_page.py</code>, which also writes <code>docs/voice-physics.md</code>. Assumptions, each a number at the top of the script: an amplifier efficiency of {EFF_AMP * 100:.0f} %; a pack at {V_PACK:.1f} V nominal, {V_PACK_SAG:.1f} V sagging under a hover; the propellers at {PROP_1M[0]:.0f} to {PROP_1M[1]:.0f} dB(A) at 1 m, {D_MIC_PROP * 100:.0f} cm from the microphone; speech at {SPEECH_1M:.0f} dB SPL at 1 m; a {SPK_R * 2000:.0f} mm moving part in the speaker; a microsecond per timer interrupt; {USABLE * 100:.0f} % of the pack and {(1 - ELEC) * 100:.0f} % for the controller and camera, as in the build page\'s ledger. The amplifier\'s, the microphone\'s and the speaker\'s figures are their datasheets\'; the modulator\'s are Espressif\'s. Nothing here has been measured on the drone.</p>')
    o.append("</div>")
    return "\n".join(o)


def page_md():
    o = ["# Why it hears for free and talks through one pin: the science and engineering behind the voice", "",
         f"Step 2 of the house rule for the voice revision of the custom build, written {WRITTEN} after the revision was approved late on {APPROVED}. Generated by `pages/gen/voice_page.py`; the page [`pages/voice-physics.html`](pages/voice-physics.html) carries the figures, two of them simulated. Read after [custom-build.md](custom-build.md) (section Voice) and [following.md](following.md). Nothing measured yet. Edit the script, not this file.", ""]
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
           ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--steel:#000;--steel-soft:#eee;--c1:#000;--c2:#555;--c1-soft:#e4e4e4;--c2-soft:#f1f1f1;--ok:#000;--ok-soft:#f2f2f2;--dev:#000;--dev-soft:#f2f2f2;--no:#000;--no-soft:#f2f2f2}"
           "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
           "h2{font-size:14pt;margin-top:16pt;page-break-after:avoid;border-top-color:#000} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
           "figure{width:78%;margin:10pt auto;padding:6pt;break-inside:avoid} figure svg{width:100%} figcaption{font-size:8pt} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid} .bit{fill:#000}</style>")
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "p.html"
        pdf = pathlib.Path(d) / "p.pdf"
        head, tail = page.rsplit("</style>", 1)
        src.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + css + tail, encoding="utf8")
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "voice-physics.pdf"
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
            print(f"  {k} = " + ", ".join(f"{kk:g}: {vv:.4g}" for kk, vv in v.items()))
        elif isinstance(v, tuple):
            print(f"  {k} = " + ", ".join(f"{x:.4g}" for x in v))
        else:
            print(f"  {k} = {v:.4g}")
    if "--pdf" in sys.argv:
        print_pdf(page)


if __name__ == "__main__":
    main()
