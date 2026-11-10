"""Desk hologram, step 2: the physics and engineering behind the approved sheet (approved 2026-11-01 evening).

Writes docs/pages/desk-hologram-physics.html, docs/pages/print/desk-hologram-physics.pdf (Letter portrait, black,
9.5 pt, figures at 70 % of the text width) and docs/PHYSICS.md (the same text without the figures).
Numbers come from build_page.py's D (dimensions) so the two pages cannot drift; everything else is derived here
and shown with its working. Edit this script, not the outputs."""
from __future__ import annotations

import math
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if "--stale" not in sys.argv:   # build_page.py went to Rev C on 2026-11-10 (brass base); this script still describes Rev A's physics (stainless legs with bent feet)
    sys.exit("physics_page.py: Rev A's physics (stainless legs with bent feet) is superseded by Rev C (2026-11-10, awaiting approval). Rewrite this script against build_page.py's new numbers after the yes.")
from build_page import D, L, STYLE, esc  # noqa: E402

PAGES = HERE.parent
DOCS = PAGES.parent
OUT = PAGES / "desk-hologram-physics.html"
PRINT = PAGES / "print"

# ----------------------------------------------------------------------------- derived numbers, with their working
N_GLASS = 1.517                      # K9 / N-BK7 at 550 nm
N_ACRYLIC = 1.49
PITCH = 0.43                         # mm per pixel
EYE = 600.0                          # mm, a seated viewer
T_PLATE = 2.0                        # mm, the acrylic sheet that was not chosen
E_STEEL = 193e9                      # Pa, 304 stainless
ROD = 1.5e-3                         # m

num = {}
num["depth_apparent"] = D["cube"] / N_GLASS                                        # 33 mm
num["fresnel"] = ((N_GLASS - 1) / (N_GLASS + 1)) ** 2                              # 0.042 per surface
num["to_viewer"] = (1 - num["fresnel"]) ** 3 * 0.5                                 # display glass → air → cube → diagonal → front face
theta_r = math.asin(math.sin(math.radians(45)) / N_ACRYLIC)
num["ghost_mm"] = 2 * T_PLATE * math.tan(theta_r) * math.cos(math.radians(45))     # 1.5 mm
num["ghost_px"] = num["ghost_mm"] / PITCH
for px in (8, 16):
    mm = px * PITCH
    num[f"h{px}_mm"] = mm
    num[f"h{px}_arcmin"] = math.degrees(2 * math.atan(mm / 2 / EYE)) * 60
num["frame_ms"] = 128 * 64 / 4e6 * 1000                                            # 2.05 ms at 4 MHz
num["sck_hz"] = 16000 * 64                                                         # 1.024 MHz
num["pcm_bytes"] = 16000 * 2 * 0.040                                               # 1280
num["pcm_kBs"] = 16000 * 2 / 1000                                                  # 32 kB/s
I_rod = math.pi * ROD ** 4 / 64
num["euler_N"] = math.pi ** 2 * E_STEEL * I_rod / (2 * D["leg_clear"] / 1000) ** 2  # fixed-free, 296 N
num["leg_load_N"] = (D["cube_mass"] + 35) / 1000 * 9.81 / 4                        # 0.86 N
num["deflect_mm"] = 1.0 * (D["leg_clear"] / 1000) ** 3 / (3 * E_STEEL * I_rod) * 1000  # 1 N sideways at the top
z_cube_c = D["leg_clear"] + D["pcb_t"] + D["stack"] + D["cube"] / 2
num["com_mm"] = (D["cube_mass"] * z_cube_c + 35 * (D["leg_clear"] + 1)) / (D["cube_mass"] + 35)
half_feet = D["pcb_d"] / 2 - D["hole_in"] + D["foot"]
half_bare = D["pcb_d"] / 2 - D["hole_in"]
num["tip_feet"] = math.degrees(math.atan(half_feet / num["com_mm"]))
num["tip_bare"] = math.degrees(math.atan(half_bare / num["com_mm"]))
num["led_mA"] = (3.3 - 2.4) / (68 + 25) * 1000                                     # about 10 mA with the pin's own ~25 Ω
num["led_mW"] = num["led_mA"] * 2.4
num["led_lm"] = num["led_mW"] / 1000 * 110                                         # ~110 lm/W at low current
num["ldo_peak_W"] = (5.0 - 3.3) * 0.39
num["ldo_avg_W"] = (5.0 - 3.3) * 0.11


def f(x, d=0):
    return f"{x:.{d}f}"


# ----------------------------------------------------------------------------- figure helpers
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
           ".img{fill:none;stroke:var(--ink);stroke-width:2.4;stroke-dasharray:4 3}"
           ".bar{fill:var(--ink);stroke:none}"
           ".bar2{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1}"
           ".h{font:700 13px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".lab{font:700 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".num{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink)}"
           ".mirror{font:700 22px 'JetBrains Mono',monospace;fill:var(--ink)}"
           "</style>")


def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{FIG_CSS}{body}</svg>'


def arrow(x0, y0, x1, y1, cls="ray"):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - 9 * math.cos(ang), y1 - 9 * math.sin(ang)
    px, py = 4.5 * math.sin(ang), -4.5 * math.cos(ang)
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="{cls}"/>'
            f'<path d="M{x1:.1f},{y1:.1f} L{hx+px:.1f},{hy+py:.1f} L{hx-px:.1f},{hy-py:.1f} z" class="rayhead"/>')


def fig_position():
    """Side section of the cube: three pixels, three reflections, the virtual image at the back face."""
    s = 4.0
    x0, y0 = 300, 250                      # cube centre, cube base
    X = lambda xm: x0 + xm * s             # noqa: E731
    Y = lambda zm: y0 - zm * s             # noqa: E731
    c = D["cube"]
    o = [f'<rect x="{X(-c/2)}" y="{Y(c)}" width="{c*s}" height="{c*s}" class="glass"/>',
         f'<line x1="{X(-c/2)}" y1="{Y(0)}" x2="{X(c/2)}" y2="{Y(c)}" class="diag"/>',
         f'<rect x="{X(-c/2 - 6)}" y="{Y(0)}" width="{(c + 12)*s}" height="10" class="soft"/>',
         f'<rect x="{X(-D["active_d"]/2)}" y="{Y(0) - 3}" width="{D["active_d"]*s}" height="4" class="solid"/>',
         T(X(c / 2 + 8), Y(0) + 8, "display, face up", "fn"),
         T(X(-c / 2 - 6), Y(0) + 26, "the front face is on the right; you look in from there", "fn"),
         T(X(2), Y(c / 2 - 6), "half-mirror diagonal", "fn", "middle", f'transform="rotate(-45 {X(2)} {Y(c/2 - 6)})"')]
    for xm, name in ((-D["active_d"] / 2, "back pixel"), (0, "middle"), (D["active_d"] / 2, "front pixel")):
        zh = xm + c / 2
        o.append(f'<line x1="{X(xm)}" y1="{Y(0)}" x2="{X(xm)}" y2="{Y(zh)}" class="ray"/>')
        o.append(arrow(X(xm), Y(zh), X(c / 2 + 24), Y(zh)))
        o.append(f'<line x1="{X(xm)}" y1="{Y(zh)}" x2="{X(-c/2)}" y2="{Y(zh)}" class="grey"/>')
        o.append(f'<circle cx="{X(-c/2)}" cy="{Y(zh)}" r="3" class="solid"/>')
    zi0, zi1 = D["img_bottom"], D["img_bottom"] + D["img_h"]
    o.append(f'<line x1="{X(-c/2)}" y1="{Y(zi0)}" x2="{X(-c/2)}" y2="{Y(zi1)}" class="img"/>')
    o.append(T(X(-c / 2) - 8, Y((zi0 + zi1) / 2) + 4, "the picture: upright,", "lab", "end"))
    o.append(T(X(-c / 2) - 8, Y((zi0 + zi1) / 2) + 18, f"{D['img_h']:.1f} mm tall, {D['img_bottom']:.0f} mm up", "fn", "end"))
    o.append(T(X(-c / 2) - 8, Y((zi0 + zi1) / 2) + 32, "front pixel at the top", "fn", "end"))
    # eye
    ex, ey = X(c / 2 + 44), Y(c / 2)
    o.append(f'<path d="M{ex-14},{ey} Q{ex},{ey-11} {ex+14},{ey} Q{ex},{ey+11} {ex-14},{ey} z" class="ink"/><circle cx="{ex}" cy="{ey}" r="4" class="solid"/>')
    o.append(T(ex, ey + 28, "your eye extends", "fn", "middle")); o.append(T(ex, ey + 42, "each ray straight", "fn", "middle")); o.append(T(ex, ey + 56, "back (grey)", "fn", "middle"))
    # the rule
    o.append(T(20, 24, "height of the picture point = distance of its pixel from the back face", "h"))
    o.append(T(20, 42, f"so the {D['active_d']:.1f} mm deep row of pixels becomes a {D['active_d']:.1f} mm tall picture at the back face", "fn"))
    o.append(T(20, 292, f"Seen through {D['cube']:.0f} mm of glass (n = {N_GLASS}) the back face looks only {f(num['depth_apparent'])} mm in:", "fn"))
    o.append(T(20, 306, "that is why the text seems to float inside the block rather than sit on its back.", "fn"))
    return svg(660, 316, "".join(o), "Where the picture stands")


def fig_mirror():
    o = [T(20, 24, "What the display shows, looked at from above", "h"), T(360, 24, "What you see in the front face", "h")]
    # left panel: the display with mirrored, inverted text
    o.append(f'<rect x="20" y="40" width="300" height="150" rx="6" class="soft"/>')
    o.append(f'<rect x="40" y="60" width="260" height="110" class="solid"/>')
    o.append(f'<text x="170" y="128" class="mirror" text-anchor="middle" transform="scale(1,-1) translate(0,-256)" style="fill:var(--paper)">RAIN 4 PM</text>')
    o.append(T(170, 208, "front edge of the desk at the bottom;", "fn", "middle"))
    o.append(T(170, 222, "the text is flipped top to bottom,", "fn", "middle"))
    o.append(T(170, 236, "so it reads wrong from here", "fn", "middle"))
    # right panel: the cube front face with upright text
    o.append(f'<rect x="360" y="40" width="240" height="150" rx="2" class="glass"/>')
    o.append(f'<text x="480" y="124" class="mirror" text-anchor="middle">RAIN 4 PM</text>')
    o.append(T(480, 208, "one reflection flips one axis;", "fn", "middle"))
    o.append(T(480, 222, "the firmware pre-flips it:", "fn", "middle"))
    o.append(T(480, 236, "one byte in the display's setup", "fn", "middle"))
    return svg(620, 250, "".join(o), "Mirror writing")


def fig_ghost():
    o = [T(20, 24, "A 2 mm sheet at 45°: two surfaces, two reflections", "h"), T(340, 24, "The cube: one coated surface, inside the glass", "h")]
    # plate: a tilted rectangle
    cx, cy = 150, 150
    def rot(x, y):
        a = math.radians(-45)
        return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)
    pts = [rot(-70, -8), rot(70, -8), rot(70, 8), rot(-70, 8)]
    o.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '" class="glass"/>')
    # incoming ray from below, reflections off front and back surfaces (schematic)
    o.append(arrow(90, 260, 150 - 5.7, 150 + 5.7 - 0))       # to the front surface
    o.append(arrow(144.3, 155.7, 270, 155.7))                 # first reflection (front surface)
    o.append(f'<line x1="144.3" y1="155.7" x2="156" y2="142" class="ray"/>')  # into the sheet
    o.append(arrow(156, 142, 270, 142))                       # second reflection (back surface), offset
    o.append(f'<line x1="285" y1="135" x2="285" y2="162" class="thin"/>')
    o.append(T(150, 58, f"{f(num['ghost_mm'], 1)} mm apart = {f(num['ghost_px'], 1)} pixels:", "lab", "middle"))
    o.append(T(150, 72, "two copies of every letter, almost equally bright", "fn", "middle"))
    o.append(T(20, 250, f"offset = 2 t tan θr cos 45°,", "fn")); o.append(T(20, 264, f"sin θr = sin 45° / {N_ACRYLIC}; t = {T_PLATE:.0f} mm", "fn")); o.append(T(20, 278, f"gives {f(num['ghost_mm'], 2)} mm", "fn"))
    # cube
    o.append(f'<rect x="400" y="70" width="160" height="160" class="glass"/>')
    o.append(f'<line x1="400" y1="230" x2="560" y2="70" class="diag"/>')
    o.append(arrow(480, 262, 480, 150)); o.append(arrow(480, 150, 600, 150))
    for i, line in enumerate(("the entry and exit faces meet", "the light square-on: their 4 %", "reflections go straight back,", "never beside the picture")):
        o.append(T(400, 250 + i * 14, line, "fn"))
    return svg(620, 300, "".join(o), "Plate versus cube")


def fig_budget():
    o = [T(20, 24, "Of the light one pixel sends up", "h")]
    rows = [("leaves the display's cover glass", 1 - num["fresnel"]), ("enters the cube's bottom face", (1 - num["fresnel"]) ** 2),
            ("reflected by the diagonal toward the front", (1 - num["fresnel"]) ** 2 * 0.5), ("out of the front face, to you", num["to_viewer"])]
    for i, (lab, frac) in enumerate(rows):
        y = 50 + i * 34
        o.append(f'<rect x="20" y="{y}" width="{frac*380:.1f}" height="20" class="bar"/>')
        o.append(T(20 + frac * 380 + 8, y + 15, f"{frac*100:.0f} %", "num"))
        o.append(T(460, y + 15, lab, "fn"))
    for i, line in enumerate((f"The other {(1 - num['fresnel'])**2 * 50:.0f} % of what enters goes on up through the top face:",
                              "stand over the cube and you see the bare, flipped text.",
                              "Through the same diagonal you also see half of whatever is behind",
                              "the cube, so a black card there makes the room disappear.")):
        o.append(T(20, 200 + i * 14, line, "fn"))
    return svg(620, 262, "".join(o), "Light budget")


def fig_size():
    o = [T(20, 24, f"128 × 64 pixels at {PITCH} mm: the cube shows the middle {D['cols']}", "h")]
    s = 2.6
    gx, gy = 20, 40
    o.append(f'<rect x="{gx}" y="{gy}" width="{128*s}" height="{64*s}" class="solid"/>')
    o.append(f'<rect x="{gx + 6*s}" y="{gy}" width="{116*s}" height="{64*s}" class="diag"/>')
    o.append(f'<text x="{gx + 64*s}" y="{gy + 30}" class="mirror" text-anchor="middle" style="fill:var(--paper);font-size:30px">RAIN FROM 4</text>')
    o.append(f'<text x="{gx + 64*s}" y="{gy + 60}" class="mirror" text-anchor="middle" style="fill:var(--paper);font-size:30px">54°F NOW</text>')
    o.append(f'<text x="{gx + 64*s}" y="{gy + 90}" class="mirror" text-anchor="middle" style="fill:var(--paper);font-size:30px">BRING A COAT</text>')
    o.append(f'<text x="{gx + 64*s}" y="{gy + 140}" class="mirror" text-anchor="middle" style="fill:var(--paper);font-size:13px">eight lines of nineteen, small font</text>')
    o.append(T(gx + 128 * s + 14, gy + 14, f"55.0 × 27.5 mm of pixels", "lab"))
    o.append(T(gx + 128 * s + 14, gy + 32, f"dashed: the 50 mm cube's window", "fn"))
    o.append(T(gx + 128 * s + 14, gy + 62, f"16 px line = {f(num['h16_mm'], 1)} mm", "lab"))
    o.append(T(gx + 128 * s + 14, gy + 78, f"at {EYE/10:.0f} cm: {f(num['h16_arcmin'])} arcminutes", "fn"))
    o.append(T(gx + 128 * s + 14, gy + 92, "like 12-point print at 40 cm", "fn"))
    o.append(T(gx + 128 * s + 14, gy + 120, f"8 px line = {f(num['h8_mm'], 1)} mm", "lab"))
    o.append(T(gx + 128 * s + 14, gy + 136, f"{f(num['h8_arcmin'])} arcminutes: 6-point print", "fn"))
    o.append(T(gx + 128 * s + 14, gy + 150, "an eye chart's 20/20 letters are 5", "fn"))
    o.append(T(20, 236, "A 70 mm cube would show the same 55 × 27.5 mm with 10 mm more glass each side:", "fn"))
    o.append(T(20, 250, "the display sets the picture; the cube only has to be big enough to hold it.", "fn"))
    return svg(620, 262, "".join(o), "Text size")


def fig_led():
    o = [T(20, 24, "The filament's current, set by a resistor and a 3.3 V pin", "h")]
    ox, oy, w, h = 60, 230, 360, 180
    o.append(f'<line x1="{ox}" y1="{oy}" x2="{ox+w}" y2="{oy}" class="ink"/><line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-h}" class="ink"/>')
    o.append(T(ox + w / 2, oy + 30, "volts across the filament", "fn", "middle")); o.append(T(ox - 8, oy - h + 4, "mA", "fn", "end"))
    for v in (1, 2, 3):
        x = ox + v / 3.5 * w
        o.append(f'<line x1="{x}" y1="{oy}" x2="{x}" y2="{oy+5}" class="thin"/>'); o.append(T(x, oy + 18, f"{v}", "num", "middle"))
    for i in (10, 20):
        y = oy - i / 25 * h
        o.append(f'<line x1="{ox-5}" y1="{y}" x2="{ox}" y2="{y}" class="thin"/>'); o.append(T(ox - 8, y + 4, f"{i}", "num", "end"))
    # diode curve: I = Is (exp(V/(n Vt)) - 1), tuned so 2.4 V -> 10 mA, steep
    pts = []
    for k in range(0, 101):
        v = 3.4 * k / 100
        i_ma = 10 * math.exp((v - 2.4) / 0.09)
        if i_ma > 25:
            break
        pts.append((ox + v / 3.5 * w, oy - i_ma / 25 * h))
    o.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '" class="ink"/>')
    # load line: I = (3.3 - V)/93 Ω
    x1, y1 = ox + 3.3 / 3.5 * w, oy
    x0, y0 = ox + (3.3 - 0.025 * 93) / 3.5 * w, oy - 25 / 25 * h
    o.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="grey"/>')
    o.append(T(x1 - 4, oy - 8, "3.3 V", "num", "end"))
    o.append(T(x1 - 40, oy - 46, "load line:", "fn", "end")); o.append(T(x1 - 40, oy - 33, "68 Ω plus the", "fn", "end")); o.append(T(x1 - 40, oy - 20, "pin's own 25 Ω", "fn", "end"))
    # operating point
    px_, py_ = ox + 2.4 / 3.5 * w, oy - 10 / 25 * h
    o.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="5" class="solid"/>')
    o.append(T(px_ - 10, py_ - 10, f"about {f(num['led_mA'])} mA at 2.4 V", "lab", "end"))
    o.append(T(px_ - 10, py_ + 6, f"{f(num['led_mW'])} mW, about {f(num['led_lm'])} lumens", "fn", "end"))
    # the 20 mA ceiling
    yc = oy - 20 / 25 * h
    o.append(f'<line x1="{ox}" y1="{yc}" x2="{ox+w}" y2="{yc}" class="grey"/>'); o.append(T(ox + w - 4, yc - 5, "the pin's 20 mA ceiling", "fn", "end"))
    # PWM inset
    ix, iy = 440, 70
    o.append(T(ix, iy - 10, "PWM at 5 kHz", "lab"))
    for row, duty in enumerate((0.05, 0.30)):
        y = iy + row * 44
        path = f"M{ix},{y+24}"
        for p in range(4):
            xs = ix + p * 30
            path += f" L{xs},{y+24} L{xs},{y} L{xs + 30*duty:.1f},{y} L{xs + 30*duty:.1f},{y+24}"
        path += f" L{ix + 120},{y+24}"
        o.append(f'<path d="{path}" class="ink"/>')
        o.append(T(ix + 126, y + 16, f"{duty*100:.0f} % on", "num"))
    o.append(T(ix, iy + 110, "5 % duty looks about a third", "fn")); o.append(T(ix, iy + 124, "as bright, not a twentieth:", "fn")); o.append(T(ix, iy + 138, "the eye judges light on a", "fn")); o.append(T(ix, iy + 152, "compressed scale", "fn"))
    return svg(640, 270, "".join(o), "LED load line")


def fig_power():
    o = [T(20, 24, "What hangs on the SuperMini's 3.3 V regulator", "h")]
    rows = [("ESP32-C3, radio burst (8.5 dBm cap)", 300, 110), ("display, every pixel lit", 75, 10), ("LED filament", 10, 2), ("microphone", 1.4, 1.4)]
    for i, (lab, peak, avg) in enumerate(rows):
        y = 48 + i * 32
        o.append(f'<rect x="200" y="{y}" width="{peak/400*380:.1f}" height="18" class="bar2"/>')
        o.append(f'<rect x="200" y="{y}" width="{avg/400*380:.1f}" height="18" class="bar"/>')
        o.append(T(190, y + 14, lab, "fn", "end"))
        o.append(T(200 + peak / 400 * 380 + 6, y + 14, f"{peak:g} mA peak", "num"))
    for i, line in enumerate(("black = typical while showing a few words; outlined = the worst moment.",
                              f"Worst case about 390 mA: the regulator drops 1.7 V, {f(num['ldo_peak_W'], 2)} W,",
                              f"for milliseconds; typical {f(num['ldo_avg_W'], 2)} W. That is why the radio is capped",
                              "and why nothing else may use the 3V3 pin.")):
        o.append(T(200, 190 + i * 14, line, "fn"))
    return svg(620, 256, "".join(o), "Power budget")


def fig_legs():
    o = [T(20, 24, "One leg", "h"), T(330, 24, "Tipping", "h")]
    # leg with load arrow and Euler note
    o.append(f'<line x1="90" y1="60" x2="90" y2="180" class="ink" style="stroke-width:5"/>')
    o.append(f'<rect x="40" y="52" width="100" height="8" class="soft"/>')
    o.append(arrow(90, 20, 90, 50, "ray")); o.append(T(100, 40, f"{f(num['leg_load_N'], 2)} N on each leg", "lab"))
    o.append(T(100, 100, f"buckles at {f(num['euler_N'])} N", "fn")); o.append(T(100, 114, f"({f(num['euler_N']/num['leg_load_N'])}× margin)", "fn"))
    o.append(T(100, 140, f"1 N sideways at the top", "fn")); o.append(T(100, 154, f"bends it {f(num['deflect_mm'], 2)} mm", "fn"))
    o.append(T(20, 210, "the weak point is the glue in the hole, not the steel:", "fn")); o.append(T(20, 224, "sleeve the rod so it centres, and let the CA cure a day", "fn"))
    # tipping: side silhouette with CoM and the two footprints
    bx, by = 440, 190
    sc = 1.6
    o.append(f'<line x1="{bx-80}" y1="{by}" x2="{bx+80}" y2="{by}" class="ink"/>')
    o.append(f'<rect x="{bx - 25*sc}" y="{by - (D['leg_clear'] + 7 + D['cube'])*sc}" width="{50*sc}" height="{D['cube']*sc}" class="glass"/>')
    o.append(f'<rect x="{bx - 21.5*sc}" y="{by - (D['leg_clear'] + 2)*sc}" width="{43*sc}" height="{3*sc}" class="soft"/>')
    for sgn in (-1, 1):
        xl = bx + sgn * half_bare * sc
        o.append(f'<path d="M{xl + sgn*D['foot']*sc},{by} L{xl},{by} L{xl},{by - D['leg_clear']*sc}" class="ink" style="stroke-width:3"/>')
    cy_ = by - num["com_mm"] * sc
    o.append(f'<circle cx="{bx}" cy="{cy_}" r="5" class="solid"/>'); o.append(T(bx + 10, cy_ + 4, f"centre of mass, {f(num['com_mm'])} mm up", "fn"))
    o.append(f'<line x1="{bx}" y1="{cy_}" x2="{bx + half_feet*sc}" y2="{by}" class="grey"/>')
    o.append(f'<line x1="{bx}" y1="{cy_}" x2="{bx + half_bare*sc}" y2="{by}" class="grey"/>')
    o.append(T(bx + 40, by + 18, f"with feet: tips past {f(num['tip_feet'])}°", "lab"))
    o.append(T(bx + 40, by + 34, f"bare legs: {f(num['tip_bare'])}°", "fn"))
    return svg(620, 250, "".join(o), "Legs")


def fig_voice():
    o = [T(20, 24, "One question, start to glass", "h")]
    # timeline
    tx, ty, scale = 20, 60, 70  # px per second
    segs = [("you hold the button and speak", 0, 3.0, "bar2"), ("Whisper small.en", 3.0, 3.0 + 0.8, "bar"), ("gpt-oss:20b", 3.8, 4.6, "bar"), ("text in the cube", 4.6, 4.7, "bar")]
    for lab, a, b, cls in segs:
        o.append(f'<rect x="{tx + a*scale}" y="{ty}" width="{max((b-a)*scale, 4):.1f}" height="22" class="{cls}"/>')
    o.append(T(tx + 1.5 * scale, ty + 40, "3 s of speech = 75 frames of 40 ms, 96 kB", "fn", "middle"))
    o.append(T(tx + 3.4 * scale, ty - 8, "~0.8 s", "num", "middle")); o.append(T(tx + 4.2 * scale, ty - 8, "~0.8 s", "num", "middle"))
    o.append(T(tx + 4.75 * scale, ty + 16, "glass", "lab"))
    for sec in range(0, 6):
        x = tx + sec * scale
        o.append(f'<line x1="{x}" y1="{ty+24}" x2="{x}" y2="{ty+29}" class="thin"/>'); o.append(T(x, ty + 56, f"{sec} s", "num", "middle"))
    o.append(T(tx, ty + 80, "release to answer: about one and a half seconds, most of it the two models on the desktop's GPU", "fn"))
    # I2S frame
    fy = 170
    o.append(T(20, fy - 10, "The microphone's wire format: I2S, 16 000 frames a second", "h"))
    o.append(T(20, fy + 14, "WS", "num")); o.append(T(20, fy + 44, "SCK", "num")); o.append(T(20, fy + 74, "SD", "num"))
    o.append(f'<path d="M60,{fy+18} L60,{fy+4} L300,{fy+4} L300,{fy+18} L540,{fy+18}" class="ink"/>')
    path = f"M60,{fy+48}"
    for k in range(60):
        xs = 60 + k * 8
        path += f" L{xs},{fy+48} L{xs},{fy+34} L{xs+4},{fy+34} L{xs+4},{fy+48}"
    o.append(f'<path d="{path}" class="thin"/>')
    o.append(f'<rect x="68" y="{fy+64}" width="180" height="14" class="bar2"/><rect x="248" y="{fy+64}" width="52" height="14" class="soft" style="fill:none;stroke-dasharray:3 3"/>')
    o.append(f'<rect x="308" y="{fy+64}" width="232" height="14" class="soft" style="fill:none;stroke-dasharray:3 3"/>')
    o.append(T(158, fy + 94, "24 bits of sample, left slot (L/R low)", "fn", "middle")); o.append(T(274, fy + 94, "8 pad", "fn", "middle")); o.append(T(424, fy + 94, "right slot, empty: 32 more clocks", "fn", "middle"))
    o.append(T(20, fy + 118, f"64 clocks a frame × 16 000 frames = {num['sck_hz']/1e6:.3f} MHz on SCK.", "fn"))
    o.append(T(20, fy + 132, f"The firmware keeps 16 of the 24 bits: 1280 bytes every 40 ms, {num['pcm_kBs']:.0f} kB/s up the Wi-Fi.", "fn"))
    return svg(620, 314, "".join(o), "Voice path")


# ----------------------------------------------------------------------------- the text
def chapters():
    """List of (heading, [paragraphs or ('fig', svg, caption)])."""
    return [
        ("The trick in one sentence", [
            f"Half of the light from every pixel bounces off a mirror hidden inside a block of glass and comes out of the front face, so your eye traces it back to a picture standing upright at the back of the block, {f(num['depth_apparent'])} mm in, where nothing is.",
            "Everything on the approved sheet follows from that one sentence: why an OLED, why a cube and not a sheet, why 50 mm, why the text is written backwards, why the room behind the cube should be dark. This page takes each decision and shows the working, in the order the sheet made them.",
        ]),
        ("Where the picture stands", [
            "A beam-splitter cube is two right-angle prisms glued face to face, with a coating on the glued face that reflects half the light and passes half. Sitting on the display, that coating is a 45° mirror across the cube, from the bottom edge at the back to the top edge at the front.",
            f"A pixel sends its light straight up. At the diagonal half of it turns 90° toward you. Your eye does not know about the turn: it extends the ray straight back, and the extension lands on the back face of the cube, as high above the base as the pixel was in front of the back face. Height equals depth, one for one.",
            f"So the {D['active_d']:.1f} mm deep strip of pixels becomes a {D['active_d']:.1f} mm tall picture, standing on the back face, with the display's front edge at the top and the back edge at the bottom. The picture is the same size as the display, not magnified, and it is a virtual image: no light actually comes from where you see it, which is the whole charm.",
            ("fig", fig_position(), f"The construction. Three pixels, three turns at the diagonal, three grey extensions meeting the back face. The picture occupies {D['img_bottom']:.0f} to {D['img_bottom'] + D['img_h']:.0f} mm above the cube's base because the pixels sit centred under it."),
            f"One more effect makes it look like it floats inside the glass rather than painted on the back. Light leaving glass bends away from the normal, so anything seen through a slab appears closer than it is, by the index of refraction: {D['cube']:.0f} mm of K9 glass (n = {N_GLASS}) looks {f(num['depth_apparent'])} mm deep. The text seems to hang two thirds of the way in, and when you move your head it slides against the back face exactly as a thing at that depth would.",
        ]),
        ("Why the text is written backwards", [
            "A single mirror flips one axis. Look at the construction again: the pixel nearest you ends up at the top of the picture, the farthest at the bottom, while left and right stay where they are. That is a top-to-bottom flip relative to the display, which is the same thing as a left-to-right flip of the letters as you would read them in the cube.",
            "The fix is free. The display's controller has a one-byte command that reverses the order it maps columns to memory (segment remap) and another that reverses the row scan. The firmware sets the right one during setup, draws normally, and the mirror undoes the pre-flip. Which byte it is depends on which way round the module is mounted, so the sheet says: power it, read it through the cube, and swap the other bit if it is upside down instead of mirrored.",
            ("fig", fig_mirror(), "Looked at from above, the bare display reads wrong; looked at through the front face, it reads right. Standing over the cube you see the bare version through the top face, which is the one give-away of the trick."),
        ]),
        ("Why a cube and not a sheet", [
            f"The cheap version of this effect is a sheet of clear acrylic at 45°. It fails on the fine detail. A sheet has two surfaces and both reflect about 4 %: the front one directly, the back one after the light has gone in, crossed the thickness and come out again. The two reflections leave parallel but displaced, by 2 t tan θr cos 45°, where θr is the refracted angle inside the plastic.",
            f"For a 2 mm sheet that is {f(num['ghost_mm'], 1)} mm, and at {PITCH} mm per pixel that is {f(num['ghost_px'], 1)} pixels: every stroke of every letter appears twice, side by side, almost equally bright. Small text turns to fuzz. A coated plate helps, but the uncoated side still adds a faint second copy.",
            "In the cube the reflecting coating is inside the glass, at the glued diagonal, and the faces the light crosses are square to it. Their 4 % reflections go straight back the way they came and never land next to the picture. One coating, one copy. The cube also needs no frame to hold it at 45°, no black box, and at 314 g it does not move: three decisions solved by one part.",
            ("fig", fig_ghost(), f"Left: the sheet's two reflections, {f(num['ghost_mm'], 1)} mm apart. Right: the cube's single internal mirror. The sheet costs $5 and was rejected for this picture, not for its price."),
        ]),
        ("Where the light goes", [
            f"Each air-to-glass surface reflects ((n − 1)/(n + 1))² of the light, {num['fresnel']*100:.1f} % for this glass. A pixel's light crosses the display's own cover glass, an air gap, the cube's bottom face, the 50 % diagonal and the front face: about {num['to_viewer']*100:.0f} % reaches you. The rest mostly carries on up through the top face.",
            "That is bright enough. The display is built to be read in daylight at full power and here it only has to be read in a room, through glass, at arm's length. It also means the picture is only as dark as what is behind it: through the same 50 % diagonal you see half of the room behind the cube. A black card standing behind the back face turns that half into nothing, and the words hang on black.",
            ("fig", fig_budget(), "The budget, surface by surface. Uncoated faces, which is what a $75 cube has; a lab cube with anti-reflection coatings would change these numbers by a few percent and the look not at all."),
        ]),
        ("How big the words are", [
            f"The display has 128 × 64 pixels at {PITCH} mm, {D['active_w']:.0f} × {D['active_d']:.1f} mm. A 50 mm cube covers 50 of the 55 mm, so the firmware uses the middle {D['cols']} columns and the picture inside the glass is {D['img_w']:.0f} × {D['img_h']:.1f} mm.",
            f"A 16-pixel line of text is {f(num['h16_mm'], 1)} mm tall. Seen from {EYE/10:.0f} cm, a seated viewer's distance, that subtends {f(num['h16_arcmin'])} arcminutes, about what 12-point print subtends on a page held at 40 cm. The small 8-pixel font is {f(num['h8_mm'], 1)} mm and {f(num['h8_arcmin'])} arcminutes, like 6-point print: readable, not comfortable. An eye-chart letter you can just read is 5 arcminutes, so both fonts have room to spare.",
            "That is why 50 mm. A 70 mm cube would hold the same 55 × 27.5 mm of pixels with 10 mm of empty glass each side: more object, no more picture, and 861 g. Bigger words need more pixels, which means a bigger display, which is a different build. The builder looked at 70 mm on 2026-11-01 and kept 50.",
            ("fig", fig_size(), "The frame, the cube's window, and the two text sizes with their angular size at 60 cm. Three lines of fourteen in the big font, or eight of nineteen in the small one; longer answers page."),
        ]),
        ("Why an OLED, and what it asks of the 3.3 V rail", [
            "An OLED pixel is a light source. A black pixel is off and sends nothing into the cube, so black on the display is truly empty in the picture. An LCD cannot do that: its backlight shines through black pixels too, and the cube would show a grey rectangle with the words in it. The beam splitter only works with an emissive display, and the monochrome white one is the brightest per watt the builder owns.",
            f"Being a light source, the display's current follows the number of lit pixels. Every pixel on draws 50 to 75 mA; a few words on black, about a tenth of the pixels, draw about 10 mA. The pixels themselves want 12 to 13 V, which the module makes from 3.3 V with an on-board charge pump. That pump takes its current in gulps, which is why the kit ships a 220 µF capacitor and the sheet puts it at the header pins, not 40 mm away at the controller.",
            f"The picture is 1024 bytes, one bit per pixel. At the display's rated 4 MHz on SPI that is {f(num['frame_ms'], 1)} ms per frame; the hologram redraws a dozen times a second at most, so the bus is idle almost always. The module speaks SPI only when two solder jumpers on its back say so (BS1 = 0, BS2 = 0), which is why the sheet asks for a photograph of the back before the header goes on.",
        ]),
        ("The microphone and the sixteen thousand", [
            "The microphone is a MEMS capsule: a silicon diaphragm over a fixed plate forms a capacitor whose value wobbles with air pressure, and a converter on the same chip turns that into a 24-bit number 16 000 times a second. It leaves the capsule already digital, on the three I2S wires, so nothing analogue is wired and nothing picks up the radio's hum.",
            f"Sixteen thousand samples a second captures everything up to 8 kHz, which covers speech: the consonants that tell words apart live between 2 and 6 kHz. Whisper itself resamples everything it hears to 16 kHz, so sending more would be thrown away. On the wire each frame is two 32-bit slots, left and right; with L/R tied to ground the capsule answers in the left one, and the clock runs at {num['sck_hz']/1e6:.3f} MHz.",
            "The capsule hangs under the table top with its port facing the desk. That is fine for sound. A 72 mm board is small next to the wavelengths of speech, 34 cm at 1 kHz, so sound bends round it; only the highest sibilants, above 5 kHz, lose a little. The desk reflects some sound back into the port, which Whisper has heard a million times before.",
            ("fig", fig_voice(), f"Top: one question in time, from the first word to the words in the glass. Bottom: one I2S frame; the firmware keeps the top 16 bits of each 24 and ships {num['pcm_bytes']:.0f} bytes every 40 ms."),
        ]),
        ("From breath to words to glass", [
            f"While the button is down the controller packs 40 ms of samples, {num['pcm_bytes']:.0f} bytes, into one binary WebSocket frame and sends it: {num['pcm_kBs']:.0f} kB a second, a thirtieth of what the Wi-Fi link carries. The server buffers the frames; on release it hands the whole utterance to Whisper, hands the text to the model, and sends the reply back as one JSON message. Nothing is streamed back but text, because this device has no speaker.",
            "The budget from release to glass is about a second and a half. Whisper small.en on the desktop's GPU transcribes a 4 s question in about 1.1 s; gpt-oss:20b at reasoning effort low answers a short question in half a second to a second once warm. The character prompt asks for two sentences because the glass holds about forty words a page.",
            "Push to talk instead of a wake word is a C3 decision. A wake-word model needs a megabyte or more of RAM to run always-on; the C3 has 400 kB and no external memory, and an always-on microphone on the desk is a different kind of object anyway. The button also makes the start and end of the utterance exact, which is the part Whisper is worst at guessing.",
        ]),
        ("One 3.3 V regulator", [
            f"USB brings 5 V to the SuperMini, and a small low-dropout regulator on the board makes the 3.3 V that everything runs on: the C3, the display, the microphone and the filament. The regulator is the busiest part of the build. Its worst moment is a radio burst with every pixel lit: about 390 mA, dropping 1.7 V, {f(num['ldo_peak_W'], 2)} W of heat in a part the size of a grain of rice. It survives because the burst lasts milliseconds; the typical draw with a few words showing is a third of that, {f(num['ldo_avg_W'], 2)} W.",
            "Two sheet rules come from this. The radio is capped at 8.5 dBm, as on the first Pocket AI, which halves its peak current and still reaches a router in the same flat. And nothing else may hang on the 3V3 pin: the display, the capsule and 10 mA of filament are the whole list.",
            ("fig", fig_power(), "Peak and typical current of the four loads. Only the radio's peaks matter; they are why the display runs its words on black and why no battery was considered."),
        ]),
        ("The amber filament", [
            "An LED filament is a row of tiny blue LED chips on a ceramic strip under a phosphor coating; the thicker and more orange the phosphor, the warmer the light. 2200 K is candle-coloured. Rated at 3 V and 2 W it would pour out 200 lumens; this build wants a glow, not a lamp.",
            f"An LED does not take a voltage and decide a current. Its current climbs exponentially with voltage, so 0.1 V too much is a lot of current and a dead filament. A resistor fixes that: the pin gives 3.3 V, the resistor and the pin's own 25 Ω take whatever the filament does not, and the two curves cross at one point, about {f(num['led_mA'])} mA at 2.4 V (the sheet's 12 mA counts the resistor alone). That is {f(num['led_mW'])} mW and roughly {f(num['led_lm'])} lumens, a quarter of a candle, a soft pool under the table top in a dim room and invisible in daylight, which is what was asked for.",
            "The same pin dims it by pulse-width modulation: on for 5 % of each 200 µs at rest, 30 % while listening, breathing while thinking. The eye compresses brightness roughly as a cube root, so 5 % duty looks like a third, not a twentieth; the firmware's levels are set by eye, not by arithmetic. If a real lamp is ever wanted, the owned MOSFET and the 5 V pin give 200 mA in one more part.",
            ("fig", fig_led(), "The filament's current-voltage curve meets the resistor's load line at one point. The 20 mA line is the pin's drive limit; 68 Ω keeps the crossing under it even with a low-voltage filament."),
        ]),
        ("Four legs", [
            f"The structure is four 1.5 mm stainless rods through the display module's own mounting holes. The whole device weighs about {D['cube_mass'] + 35} g, {f(num['leg_load_N'], 2)} N on each leg. A 20 mm length of 1.5 mm rod fixed at the top buckles at about {f(num['euler_N'])} N by Euler's formula, {f(num['euler_N']/num['leg_load_N'])} times more; a 1 N sideways push at the top bends it {f(num['deflect_mm'], 2)} mm. The steel is not the limit. The glue in the hole is, which is why the rod is sleeved to centre it and the CA gets a day to cure.",
            f"Tipping is the real question with 314 g of glass on top. The centre of mass sits {f(num['com_mm'])} mm up. With the legs bent into feet that reach 15 mm out front and back, the device has to lean {f(num['tip_feet'])}° before it goes over; on bare vertical legs only {f(num['tip_bare'])}°. The feet cost no extra rod and no solder: one bend per leg.",
            "Stainless rather than brass because the material rule says so for every build after Cyber Dawn, and because here it costs nothing: no joints are soldered, the rods are glued, and 304's stiffness is 60 % higher than brass's at the same diameter, which is where the 0.06 mm came from.",
            ("fig", fig_legs(), "Left: one leg's load against what would buckle or bend it. Right: the tipping angle with and without the feet; the dashed lines run from the centre of mass to the two footprints."),
        ]),
    ]


NUMBERS = [
    (f"{f(num['depth_apparent'])} mm", "how deep the picture looks through 50 mm of glass (50 / 1.517)"),
    (f"{D['img_h']:.1f} mm", "picture height: the depth of the row of pixels, one for one"),
    (f"{D['img_bottom']:.0f} mm", "picture bottom above the cube's base: (50 − 27.5) / 2"),
    (f"{D['cols']} of 128", "columns inside the cube: 50 / 0.43"),
    (f"{f(num['ghost_mm'], 1)} mm", f"double-image offset a 2 mm acrylic sheet would give: {f(num['ghost_px'], 1)} pixels"),
    (f"{num['to_viewer']*100:.0f} %", "of a pixel's light that reaches you through four uncoated surfaces and the 50 % diagonal"),
    (f"{f(num['h16_arcmin'])} arcmin", "a 16-pixel line of text seen from 60 cm; 20/20 letters are 5"),
    (f"{f(num['frame_ms'], 1)} ms", "one 1024-byte frame at 4 MHz SPI"),
    (f"{num['sck_hz']/1e6:.3f} MHz", "I2S bit clock: 16 000 frames × 64 bits"),
    (f"{num['pcm_bytes']:.0f} B / 40 ms", f"one audio frame up the Wi-Fi, {num['pcm_kBs']:.0f} kB/s"),
    (f"{f(num['ldo_peak_W'], 2)} W", "worst-moment heat in the 3.3 V regulator: 1.7 V × 390 mA"),
    (f"{f(num['led_mA'])} mA", "filament current: (3.3 − 2.4) / (68 + 25)"),
    (f"{f(num['euler_N'])} N", "buckling load of one 20 mm leg, fixed-free, 1.5 mm 304"),
    (f"{f(num['tip_feet'])}°", f"lean before tipping, with feet; {f(num['tip_bare'])}° without"),
]

PARTS_IDEAS = [
    ("the half-mirror diagonal and the virtual image", "beam-splitter cube", "cube"),
    ("emissive pixels, the charge pump, the mirror byte, 4 MHz SPI", "2.42-inch display", "display"),
    ("the 3.3 V regulator, the radio cap, push to talk", "ESP32-C3 SuperMini", "controller"),
    ("MEMS capsule, I2S frames, 16 kHz", "I2S microphone", "mic"),
    ("the diode curve, the resistor, PWM dimming", "LED filament", "lamp"),
    ("Euler buckling, tipping, glue in a hole", "1.5 mm stainless rod", "rod"),
]


def page_html():
    o = ['<title>Desk Hologram Physics</title>',
         '<meta name="claude:viewport-fit-sides" content="cover">',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
         f"<style>{STYLE}</style>",
         '<style>.wrap{max-width:880px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} figure svg{width:100%;height:auto} td,th{min-width:0}</style>',
         '<div class="wrap">',
         '<div class="masthead"><div class="eyebrow">Desk hologram &middot; step 2: the physics and engineering</div>',
         '<h1>Why the words float</h1>',
         '<div class="sub">The working behind every number on the approved sheet of 2026-11-01: the mirror in the glass, the backwards text, cube against sheet, where the light goes, how big the words are, what the display and the radio ask of one small regulator, a resistor for a filament, and four legs under 314 g of glass.<br>Read after <a href="https://claude.ai/artifact/DZtpfR2LGADWw9Hb7AK1RH" target="_blank" rel="noopener">Desk Hologram Build</a>. Nothing measured yet; every figure is derived from datasheet numbers and the sheet\'s dimensions.</div></div>']
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
    o.append("<h2>What comes next</h2><p>The firmware port: the first Pocket AI's character firmware with the amplifier off, the display driver moved to SPI with the mirror byte, the lamp on GPIO0, and text pages for the transcript. Then the cube and the filament arrive, the display's back gets photographed, and the first words go into the glass.</p>")
    o.append('<hr><p class="sub">Built by <code>docs/pages/gen/physics_page.py</code> from the dimensions in <code>build_page.py</code>; it also writes <code>docs/PHYSICS.md</code>. Constants: K9 glass n = 1.517, acrylic n = 1.49, 304 stainless E = 193 GPa, pixel pitch 0.43 mm, viewer at 60 cm. The display\'s current and SPI limit are Adafruit\'s figures; Whisper and Ollama timings are the first Pocket AI\'s measured ones on this desktop. Nothing here has been measured on the hologram itself.</p>')
    o.append("</div>")
    return "\n".join(o)


def physics_md():
    o = ["# Why the words float: the physics and engineering behind the sheet", "",
         "Step 2 of the house rule, written 2026-11-01 after the sheet was approved. Generated by `pages/gen/physics_page.py`; the page `pages/desk-hologram-physics.html` carries the figures. Edit the script, not this file.", ""]
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
    o.append("")
    return "\n".join(o)


def print_pdf(html):
    PRINT.mkdir(exist_ok=True)
    css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
           ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
           "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
           "h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
           "figure{width:70%;margin:10pt auto;padding:6pt;break-inside:avoid} figure svg{width:100%} figcaption{font-size:8pt} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt} tr{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "p.html"; pdf = pathlib.Path(d) / "p.pdf"
        head, tail = html.rsplit("</style>", 1)
        src.write_text("<!doctype html><meta charset=utf-8>" + head + "</style>" + css + tail)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "desk-hologram-physics.pdf"
        out.write_bytes(pdf.read_bytes())
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


def main():
    html = page_html()
    OUT.write_text(html)
    (DOCS / "PHYSICS.md").write_text(physics_md())
    print("wrote", OUT, OUT.stat().st_size, "and", DOCS / "PHYSICS.md")
    for k in sorted(num):
        print(f"  {k} = {num[k]:.4g}")
    if "--pdf" in sys.argv:
        print_pdf(html)


if __name__ == "__main__":
    main()
