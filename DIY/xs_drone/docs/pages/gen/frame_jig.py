"""Builds docs/pages/frame-jig.html and docs/pages/print/frame-jig.pdf: the ladder frame drawn 1:1 on US Letter.

Geometry from docs/custom-build.md (2026-10-28), with two corrections made 2026-11-06 while drawing it:
  - nose bar 31 mm, not 36: at 36 its ends run into the front collars (9.2 mm outside, centred at ±20, +30).
  - collar blanks 60 mm, not 40: two turns at a 7.7 mm mean diameter take 48 mm of rod, plus a grip to wind with.
Every coordinate is in millimetres, one SVG unit to one millimetre. Run: python3 docs/pages/gen/frame_jig.py
"""
import math, pathlib, shutil, subprocess, tempfile, textwrap

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
HTML_OUT = PAGES / "frame-jig.html"
PDF_OUT = PAGES / "print" / "frame-jig.pdf"

W, H = 215.9, 279.0          # Letter width; 0.4 mm short of the height so Chrome never spills a blank page 2
ROD = 1.0                    # frame rod
COLLAR_ROD, FORMER = 1.5, 6.2
COLLAR_OD = FORMER + 2 * COLLAR_ROD
RAIL_X, RAIL_Y = 7, 33       # rails at ±7, ends at ±33  -> 66 mm
AXLE_X, AXLE_Y = 20, 30      # axles ±20 at ±30          -> 40 mm, ends under the motor centres
NOSE_X, TAIL_X = 15.5, 7     # nose bar 31 mm at +33, tail bar 14 mm at -33
PROP_D = 31
LIFT = -12                   # everything below the header moves up together
CX, CY = 66, 110             # plan-view origin on the page; drone y is up (nose), page y is down

CUTS = [  # tag, name, count, length, stock
    ("R", "rails", 2, 66, "1 mm"), ("A", "axles", 2, 40, "1 mm"), ("N", "nose bar", 1, 31, "1 mm"),
    ("T", "tail bar", 1, 14, "1 mm"), ("S", "skids", 4, 5, "1 mm"), ("C", "collar blanks", 4, 60, "1.5 mm"),
]
ONE_MM_TOTAL = sum(n * L for _, _, n, L, s in CUTS if s == "1 mm")
COLLAR_ROD_USED = 2 * math.pi * (FORMER + COLLAR_ROD) / 2 * 2
MASS = 7.93e-3 * (ONE_MM_TOTAL * math.pi * ROD ** 2 / 4 + 4 * COLLAR_ROD_USED * math.pi * COLLAR_ROD ** 2 / 4)

STEPS = [
    "Test first. On two 1.5 mm coupons, wind one collar and solder one lap and one T with the stainless flux. "
    "Bend them hard. A joint that pops off clean means more heat and more flux before the frame.",
    "Cut. Lay each rod on its bar below, mark the end tick, saw 0.5 mm long and sand square to the mark.",
    "Set up. Tape this sheet to the silicone mat (never the cutting mat). Put a Kapton square over each "
    "numbered dot, then hold the rails on their lines with Kapton strips.",
    "Solder 1 to 4: tail bar, then nose bar, both laid across the tops of the rails. Check the rail "
    f"diagonals: {math.hypot(2 * RAIL_X, 2 * RAIL_Y):.1f} mm both ways.",
    "Solder 5 to 8: both axles across the tops of the rails, each end on its motor centre.",
    "Collars. Set one on each axle end, lower turn on the axle, with the 6 mm former left inside so it "
    "stays round. Solder, then pull the former out. A motor should push in by hand.",
    "Flip the frame and solder a 5 mm skid under each axle end, straight down.",
    f"Wash off every trace of flux (warm water, a pinch of baking soda), dry and weigh: about {MASS:.1f} g.",
]


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def P(x, y):  # drone plan coordinates -> page
    return CX + x, CY - y


def line(x1, y1, x2, y2, cls, w=None):
    sw = f' stroke-width="{f(w)}"' if w else ""
    return f'<line class="{cls}" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"{sw}/>'


def text(x, y, s, cls="t", size=2.6, anchor="start", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" font-size="{f(size)}" text-anchor="{anchor}"{extra}>{s}</text>'


def rod(x1, y1, x2, y2):
    a, b = P(x1, y1), P(x2, y2)
    return line(*a, *b, "rod", ROD)


def tag(x, y, s, circled=False):
    px, py = P(x, y)
    out = ""
    if circled:
        out += f'<circle class="paper ink-s" cx="{f(px)}" cy="{f(py)}" r="1.45" stroke-width="0.2"/>'
    return out + text(px, py + 0.75, s, "t b", 2.1, "middle")


def plan():
    s = [text(*P(0, 49), "NOSE", "t b", 2.6, "middle"),
         f'<path class="ink" d="M{f(CX - 1.6)} {f(CY - 49 - 2.6)} L{f(CX)} {f(CY - 49 - 5)} L{f(CX + 1.6)} {f(CY - 49 - 2.6)} Z"/>']
    names = {(-1, 1): "M4 CW", (1, 1): "M1 CCW", (-1, -1): "M3 CCW", (1, -1): "M2 CW"}
    for sx in (-1, 1):
        for sy in (-1, 1):
            mx, my = P(sx * AXLE_X, sy * AXLE_Y)
            s.append(f'<circle class="faint" cx="{f(mx)}" cy="{f(my)}" r="{f(PROP_D / 2)}" stroke-dasharray="1.2 1.2"/>')
            s.append(f'<circle class="grey" cx="{f(mx)}" cy="{f(my)}" r="{f(COLLAR_OD / 2)}"/>')
            s.append(f'<circle class="grey" cx="{f(mx)}" cy="{f(my)}" r="{f(FORMER / 2)}" stroke-dasharray="0.6 0.5"/>')
            s.append(line(mx - 1.2, my, mx + 1.2, my, "ink-s", 0.18) + line(mx, my - 1.2, mx, my + 1.2, "ink-s", 0.18))
            s.append(text(mx, my + (8.2 if sy > 0 else -6.4), names[(sx, sy)], "t g", 2.2, "middle"))
    # rails first (they go down first), then the cross pieces that lie on them
    for sx in (-1, 1):
        s.append(rod(sx * RAIL_X, -RAIL_Y, sx * RAIL_X, RAIL_Y))
    s.append(rod(-NOSE_X, RAIL_Y, NOSE_X, RAIL_Y))
    s.append(rod(-TAIL_X, -RAIL_Y, TAIL_X, -RAIL_Y))
    for sy in (-1, 1):
        s.append(rod(-AXLE_X, sy * AXLE_Y, AXLE_X, sy * AXLE_Y))
    joints = [(-1, -RAIL_Y, -1), (1, -RAIL_Y, -1), (-1, RAIL_Y, 1), (1, RAIL_Y, 1),
              (-1, AXLE_Y, -1), (1, AXLE_Y, -1), (-1, -AXLE_Y, 1), (1, -AXLE_Y, 1)]
    for i, (sx, y, side) in enumerate(joints, 1):
        px, py = P(sx * RAIL_X, y)
        s.append(f'<circle class="ink" cx="{f(px)}" cy="{f(py)}" r="0.85"/>')
        s.append(tag(sx * (RAIL_X - 3.6), y + side * 2.7, str(i), True))
    for sy in (-1, 1):
        for sx in (-1, 1):
            s.append(tag(sx * 11.2, sy * AXLE_Y - 2.3, "A"))
    s += [tag(0, RAIL_Y + 2.6, "N"), tag(0, -RAIL_Y - 2.9, "T"), tag(-RAIL_X - 2.4, 0, "R"), tag(RAIL_X + 2.4, 0, "R")]
    ox, oy = P(0, 0)
    s.append(line(ox - 1.5, oy, ox + 1.5, oy, "ink-s", 0.2) + line(ox, oy - 1.5, ox, oy + 1.5, "ink-s", 0.2))
    s.append(text(ox, oy + 4, "balance", "t g", 2, "middle"))
    s.append(text(CX, CY + 52, "Top view, 1:1. Black is rod, laid where it lies. Dots are joints in solder order.", "t", 2.5, "middle"))
    s.append(text(CX, CY + 55.5, "Grey rings are the collars, dashed circles the 31 mm propellers.", "t", 2.5, "middle"))
    return "".join(s)


def scale_bars():
    s = []
    x0, y0 = 150.9, 20                      # horizontal, top right
    s.append(f'<rect id="bar-h" class="ink" x="{f(x0)}" y="{f(y0)}" width="50" height="0.6"/>')
    for i in range(6):
        s.append(line(x0 + 10 * i, y0 - (1.6 if i in (0, 5) else 0.9), x0 + 10 * i, y0 + 0.6, "ink-s", 0.25))
    s.append(text(x0 + 25, y0 + 3.6, "50 mm", "t b", 2.4, "middle"))
    return "".join(s)


def vbar():
    s = []
    x1, y1 = 18, 62                        # vertical, beside the plan
    s.append(f'<rect id="bar-v" class="ink" x="{f(x1)}" y="{f(y1)}" width="0.6" height="50"/>')
    for i in range(6):
        s.append(line(x1 - (1.6 if i in (0, 5) else 0.9), y1 + 10 * i, x1 + 0.6, y1 + 10 * i, "ink-s", 0.25))
    s.append(text(x1 - 2.2, y1 + 25, "50 mm", "t b", 2.4, "middle", f' transform="rotate(-90 {f(x1 - 2.2)} {f(y1 + 25)})"'))
    return "".join(s)


def detail():
    k, x0, base = 3.0, 122, 88               # 3x side view of the right front axle end, drone x 10 to 25
    X = lambda x: x0 + k * (x - 10)
    Y = lambda z: base - k * z               # z = 0 is the top of the axle
    s = [text(118, 48, "Axle end, side view, 3 × size", "t b", 2.8),
         text(118, 52, "Not for laying rod: the 1:1 view is on the left.", "t g", 2.3)]
    s.append(f'<rect class="ink" x="{f(X(10))}" y="{f(Y(0))}" width="{f(k * 10)}" height="{f(k * ROD)}"/>')
    s.append(f'<rect class="ink" x="{f(X(19))}" y="{f(Y(-ROD))}" width="{f(k * ROD)}" height="{f(k * 5)}"/>')
    m0, m1, top = X(AXLE_X - 3), X(AXLE_X + 3), Y(8)
    s.append(f'<path class="grey" d="M{f(m0)} {f(Y(0))} V{f(top + 1)} L{f(m0 + 4)} {f(top - 1)} L{f(m0 + 9)} {f(top + 1)} '
             f'L{f(m0 + 14)} {f(top - 1)} L{f(m1)} {f(top + 0.5)} V{f(Y(0))} Z"/>')
    r = COLLAR_ROD / 2
    for z in (r, 3 * r):
        for x in (AXLE_X - FORMER / 2 - r, AXLE_X + FORMER / 2 + r):
            s.append(f'<circle class="dark" cx="{f(X(x))}" cy="{f(Y(z))}" r="{f(k * r)}"/>')
    s.append(line(X(AXLE_X), Y(10), X(AXLE_X), Y(-7), "ink-s", 0.15) + text(X(AXLE_X), Y(10.6), "motor centre", "t g", 2.1, "middle"))
    lx = 174
    for z, ax, label, sub in ((5.5, X(AXLE_X + 3), "motor", "stands on the axle end"),
                              (1.5, X(AXLE_X + FORMER / 2 + 2 * r), "collar", "2 turns of 1.5 mm rod"),
                              (-3.5, X(19 + ROD), "skid", "5 mm, straight down")):
        s.append(line(ax + 0.6, Y(z), lx - 1.2, Y(z), "ink-s", 0.18))
        s.append(text(lx, Y(z) - 0.2, label, "t b", 2.5) + text(lx, Y(z) + 2.8, sub, "t g", 2.2))
    s.append(text(X(10), Y(-ROD) + 4.2, "axle, on top of the rail", "t g", 2.2))
    cx, cy = 140, 124                         # 1:1 collar check
    s.append(text(118, 112, "Collar check, 1:1", "t b", 2.8))
    s.append(f'<circle class="grey" cx="{cx}" cy="{cy}" r="{f(COLLAR_OD / 2)}" stroke-width="0.25"/>')
    s.append(f'<circle class="ink-s" cx="{cx}" cy="{cy}" r="{f(FORMER / 2)}" stroke-width="0.25" fill="none"/>')
    s.append(text(cx + 8, cy - 1, f"inside {FORMER} mm, outside {f(COLLAR_OD)} mm", "t", 2.4))
    s.append(text(cx + 8, cy + 2.6, "A wound collar should cover the grey ring.", "t g", 2.3))
    s.append(text(118, 140, "Joints", "t b", 2.8))
    for i, row in enumerate(["Laps: each cross piece lies on top of the rails.",
                             "Collars sit on the axle ends; skids hang under them.",
                             "The battery straps between the rails, nose to tail;",
                             "the frame stays electrically floating."]):
        s.append(text(118, 144.5 + 3.8 * i, row, "t", 2.4))
    return "".join(s)


def cut_list():
    s = [text(16, 172, "Cut list, 1:1. Lay the rod on its bar and mark it at the end tick.", "t b", 2.8)]
    for i, (t, name, n, L, stock) in enumerate(CUTS):
        x, y = (16, 112)[i // 3], 182 + 12 * (i % 3)
        s.append(text(x, y - 2.4, f"<tspan class='b'>{t}</tspan>  {name} · {n} × {L} mm · {stock} rod", "t", 2.5))
        s.append(f'<rect class="bar" x="{x}" y="{f(y)}" width="{L}" height="1"/>')
        for e in (x, x + L):
            s.append(line(e, y - 1.2, e, y + 2.2, "ink-s", 0.25))
    s.append(text(16, 216.5, f"All ten 1 mm pieces come from one 300 mm rod: {ONE_MM_TOTAL} mm plus the saw cuts. "
                  "The collars take two 60 mm blanks from each of two 150 mm coupons.", "t g", 2.4))
    return "".join(s)


def steps():
    s = [text(16, 225, "Build order", "t b", 2.8)]
    cols, y, x, col = [], 230, 16, 0
    for i, st in enumerate(STEPS, 1):
        lines = textwrap.wrap(st, 60)
        if col == 0 and i == 5:
            y, x, col = 230, 112, 1
        for j, ln in enumerate(lines):
            if j == 0:
                s.append(text(x, y, f"{i}", "t b", 2.6))
            s.append(text(x + 4, y, ln, "t", 2.6))
            y += 3.7
        y += 1.4
    return "".join(s)


def footer():
    return (text(16, 274, "XS drone · ladder frame jig · 2026-11-06 · from docs/custom-build.md · nose bar 31 mm to clear the front collars",
                  "t g", 2.2))


def sheet_svg():
    head = (text(16, 19, "XS drone frame jig", "t b", 6.4) +
            text(16, 25, "Print on US Letter at Actual size (100 %), never Fit to page.", "t", 2.8) +
            text(16, 29, "Both bars must read 50 mm on a caliper before you cut or lay anything.", "t", 2.8))
    return (f'<svg class="jig" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="1:1 jig for the XS drone ladder frame">'
            f'<rect class="paper" x="0" y="0" width="{W}" height="{H}"/>'
            + head + scale_bars() + f'<g transform="translate(0 {LIFT})">' + vbar() + plan() + detail()
            + cut_list() + steps() + "</g>" + footer() + "</svg>")


LINKS = {
    "rod": "https://www.amazon.com/dp/B082ZNWQ5Q",
    "coupon": "https://www.amazon.com/dp/B082ZNMD46",
    "motor": "https://www.amazon.com/dp/B09J236JJL",
}

CSS = """
/* One sheet of paper on a bench: the drawing is the page, the words around it are a short brief. */
:root {
  --bg: #eceeed; --paper: #ffffff; --ink: #111413; --grey: #6b716f; --faint: #b7bcba; --line: #d3d7d5;
  --sans: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #121514; --paper: #1b1f1e; --ink: #e9eceb; --grey: #9aa19f; --faint: #4b5250; --line: #2e3432; color-scheme: dark } }
:root[data-theme="dark"] { --bg: #121514; --paper: #1b1f1e; --ink: #e9eceb; --grey: #9aa19f; --faint: #4b5250; --line: #2e3432; color-scheme: dark }
body { background: var(--bg); color: var(--ink); font-family: var(--sans); font-size: 15px; line-height: 1.55; }
.wrap { max-width: 860px; margin: 0 auto; padding-block: 28px 48px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 20px; }
h1 { font-size: 26px; line-height: 1.2; margin: 0; letter-spacing: -0.01em; text-wrap: balance; }
.eyebrow { font-family: var(--mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--grey); margin: 0 0 6px; }
.brief { display: grid; gap: 10px; max-width: 66ch; }
.brief p { margin: 0; }
.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1px; background: var(--line);
  border: 1px solid var(--line); }
.facts div { background: var(--paper); padding: 10px 12px; min-width: 0; }
.facts b { display: block; font-family: var(--mono); font-size: 18px; font-weight: 500; font-variant-numeric: tabular-nums; }
.facts span { font-size: 13px; color: var(--grey); }
a { color: var(--ink); text-underline-offset: 2px; }
a:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
.sheet { overflow-x: auto; box-shadow: 0 1px 2px rgba(0,0,0,.08), 0 8px 28px rgba(0,0,0,.08); }
.jig { display: block; width: 100%; min-width: 560px; height: auto; font-family: var(--sans); }
.jig .paper { fill: var(--paper); }
.jig .t { fill: var(--ink); } .jig .g { fill: var(--grey); } .jig .b { font-weight: 600; }
.jig .rod { stroke: var(--ink); stroke-linecap: butt; }
.jig .ink { fill: var(--ink); } .jig .ink-s { stroke: var(--ink); }
.jig .dark { fill: var(--grey); }
.jig .grey { stroke: var(--grey); stroke-width: 0.3; fill: none; }
.jig .faint { stroke: var(--faint); stroke-width: 0.25; fill: none; }
.jig .bar { fill: var(--faint); }
.jig circle.paper { fill: var(--paper); }
.note { font-size: 13px; color: var(--grey); margin: 0; }
@media print {
  @page { size: letter; margin: 0; }
  :root { --paper: #fff; --ink: #000; --grey: #555; --faint: #aaa; --line: #ccc; --bg: #fff; color-scheme: light; }
  html, body { margin: 0; padding: 0; background: #fff; }
  .wrap { display: block; padding: 0; max-width: none; }
  .screen { display: none; }
  .sheet { box-shadow: none; overflow: visible; }
  .jig { width: 215.9mm; height: 279mm; min-width: 0; }
}
"""


def page():
    return f"""<title>XS Drone Frame Jig</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
<main class="wrap">
  <header class="screen">
    <p class="eyebrow">XS drone · ladder frame</p>
    <h1>Frame jig, 1:1 on US Letter</h1>
  </header>
  <section class="brief screen">
    <p>Print the sheet at <b>Actual size</b> and check both 50 mm bars before cutting. Then lay the
    <a href="{LINKS['rod']}">1 mm stainless rod</a> straight onto the black lines and solder the joints in number order.
    The motor collars are wound from the <a href="{LINKS['coupon']}">1.5 mm stainless coupons</a> to fit the
    <a href="{LINKS['motor']}">6 mm coreless motors</a>.</p>
    <p>Two changes from the build plan: the nose bar is <b>31 mm</b>, not 36, because at 36 its ends hit the front collars.
    The collar blanks are <b>60 mm</b>, not 40, because two turns take 48 mm of rod.</p>
  </section>
  <section class="facts screen" aria-label="Frame figures">
    <div><b>40 × 60</b><span>motor centres, mm</span></div>
    <div><b>{ONE_MM_TOTAL} mm</b><span>of 1 mm rod, one 300 mm stick</span></div>
    <div><b>16</b><span>joints: 8 laps, 4 collars, 4 skids</span></div>
    <div><b>{MASS:.1f} g</b><span>bare frame, before solder</span></div>
  </section>
  <figure class="sheet" style="margin:0">{sheet_svg()}</figure>
  <p class="note screen">The printable PDF is xs_drone/docs/pages/print/frame-jig.pdf in the project folder.</p>
</main>
"""


def print_pdf(html):
    PDF_OUT.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "jig.html"
        src.write_text('<!doctype html><html><head><meta charset="utf-8"></head><body>' + html + "</body></html>")
        tmp = pathlib.Path(d) / "jig.pdf"
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={tmp}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        shutil.copyfile(tmp, PDF_OUT)
    info = subprocess.run(["pdfinfo", str(PDF_OUT)], capture_output=True, text=True).stdout
    print([l for l in info.splitlines() if l.startswith(("Pages", "Page size"))])


if __name__ == "__main__":
    html = page()
    HTML_OUT.write_text(html)
    print(f"wrote {HTML_OUT.relative_to(PAGES.parent.parent)}; 1 mm rod {ONE_MM_TOTAL} mm, frame {MASS:.2f} g, "
          f"collar rod {COLLAR_ROD_USED:.1f} mm each")
    print_pdf(html)
