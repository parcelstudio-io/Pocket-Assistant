"""Builds edu/pages/brass-battery-sleeve.html: the cell's brass sleeve, fish paper inside, drawn step by step.
Also writes brass-sleeve-pattern-letter.svg, the 1:1 cutting pattern for Letter."""
from __future__ import annotations

import pathlib
import re

from harness_page import a, L

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "brass-battery-sleeve.html"
OUT_PATTERN = HERE.parent / "brass-sleeve-pattern-letter.svg"
WHOLE = "https://claude.ai/artifact/H3AXHXGCem2Qfj3RUGbV2u"
POWER = "https://claude.ai/artifact/J9qXnfWho79ZrsDc4a8jy6"

L.update({
    "sheet": ("https://www.amazon.com/dp/B004QB5Y3C", "K&S #251 brass sheet, 0.010 in"),
    "fish": ("https://www.amazon.com/dp/B0GZVDKBBS", "XFJYMXDM fish paper, 0.2 mm"),
    "knife": ("https://www.amazon.com/dp/B0D4DKYL2C", "DIYSELF craft knife"),
    "mat": ("https://www.amazon.com/dp/B0BWYJC65J", "Anezus cutting mat"),
    "harris": ("https://www.amazon.com/dp/B0015DWPV8", "Harris Stay-Clean SCLF4"),
    "cell1200": ("https://www.adafruit.com/product/258", "Adafruit #258, 1200 mAh"),
    "powerboost": ("https://www.adafruit.com/product/2465", "Adafruit PowerBoost 1000C"),
    "powerboost_owned": ("https://www.amazon.com/dp/B0G5PXGVG9", "PowerBoost 1000C copy (Amazon #20)"),
})

# ---------------------------------------------------------------- the numbers (mm)
CELL = (62.0, 34.0, 5.0)          # length, width, thickness of the #258 cell
PAPER = 0.2                       # fish paper
BRASS = 0.25                      # K&S #251
TOP, WALL, LAP = 35.5, 6.5, 8.0   # panel widths; floor = TOP
LEN = 63.0                        # sleeve length
FLAP = (34.5, 6.0)                # end flap on the floor panel: width, height
PAT_W = TOP + WALL + TOP + WALL + LAP   # 92
PAT_H = LEN + FLAP[1]                   # 69
JACKET = (LEN, CELL[1] * 2 + CELL[2] * 2 + 6)   # fish paper band: 63 × 84
BEND = 0.45                       # what one sharp bend eats out of the flat
INSIDE = (TOP - BEND, WALL - BEND)      # ≈ 35.05 × 6.05
OUTSIDE = (INSIDE[0] + 2 * BRASS, INSIDE[1] + 2 * BRASS)
JACKETED = (CELL[1] + 2 * PAPER, CELL[2] + 2 * PAPER)   # 34.4 × 5.4
STOREY = 6.5                      # the cell storey on the whole-build page: z −17.5 … −11


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def R(x, y, w, h, cls, rx=0):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" class="{cls}"/>'


def Ln(x1, y1, x2, y2, cls="edge", w=None, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    sw = f' stroke-width="{w}"' if w else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"{sw}{d}/>'


def P(pts, cls="edge", w=None, close=False, dash=None):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    tag = "polygon" if close else "polyline"
    sw = f' stroke-width="{w}"' if w else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<{tag} points="{d}" class="{cls}"{sw}{da}/>'


def dim(x1, y1, x2, y2, label, off=14, cls="s muted"):
    """A dimension line with end ticks; horizontal if y1 == y2 else vertical."""
    o = []
    if y1 == y2:
        y = y1 + off
        o.append(Ln(x1, y, x2, y, "grid")); o.append(Ln(x1, y - 4, x1, y + 4, "grid")); o.append(Ln(x2, y - 4, x2, y + 4, "grid"))
        o.append(T((x1 + x2) / 2, y + (14 if off > 0 else -6), label, cls, "middle"))
    else:
        x = x1 + off
        o.append(Ln(x, y1, x, y2, "grid")); o.append(Ln(x - 4, y1, x + 4, y1, "grid")); o.append(Ln(x - 4, y2, x + 4, y2, "grid"))
        o.append(T(x + (6 if off > 0 else -6), (y1 + y2) / 2 + 4, label, cls, "start" if off > 0 else "end"))
    return "".join(o)


def svg(body, h, label, w=760):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{body}</svg>'


EXTRA_CSS = ('<style>figure svg .brass { fill: var(--brass-tint); stroke: var(--brass); stroke-width: 1.6; } '
             'figure svg .brassf { fill: var(--brass); stroke: none; } '
             'figure svg .paper { fill: var(--pass-tint); stroke: var(--pass); stroke-width: 1.2; } '
             'figure svg .paperf { fill: var(--pass); fill-opacity: .55; stroke: none; } '
             'figure svg .cellf { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.2; } '
             'figure svg .fold { stroke: var(--brass); stroke-width: 1.4; stroke-dasharray: 6 4; fill: none; } '
             'figure svg .cut { stroke: currentColor; stroke-width: 2; fill: none; } '
             'figure svg .thick { stroke: var(--brass); stroke-width: 5; fill: none; stroke-linecap: round; stroke-linejoin: round; } '
             'figure svg .thickp { stroke: var(--pass); stroke-width: 4; fill: none; stroke-linecap: round; stroke-linejoin: round; } '
             'figure svg .iron { fill: var(--code-bg); stroke: currentColor; stroke-width: 1.2; } '
             'figure svg .solder { fill: var(--muted); } '
             'figure svg .gluel { stroke: var(--pass); stroke-width: 6; stroke-linecap: round; opacity: .8; } '
             'figure svg .lead { stroke: var(--w-red); stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; } '
             'figure svg .arrow { stroke: currentColor; stroke-width: 1.6; fill: none; marker-end: url(#ah); } '
             '.own { color: var(--pass); font-weight: 600; } .buy { color: var(--warn); font-weight: 600; }</style>')
MARKER = '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>'


# ---------------------------------------------------------------- figures
def fig_section():
    """End view: brass outside, fish paper inside, cell in the middle. 1 mm = 13 px."""
    s = 13.0
    ox, oy = 110, 78
    W_o, H_o = OUTSIDE[0] * s, OUTSIDE[1] * s
    o = [MARKER, T(20, 26, "Looking into the open end: three layers, nothing else", "t b")]
    o.append(T(ox, 54, "slack: about 0.6 mm sideways and 0.6 mm up, so the jacketed cell slides without scraping", "s muted"))
    o.append(R(ox, oy, W_o, H_o, "brass", 2))
    o.append(R(ox + BRASS * s, oy + BRASS * s, INSIDE[0] * s, INSIDE[1] * s, "card", 1))
    o.append(R(ox + W_o - BRASS * s - LAP * s, oy + BRASS * s, LAP * s, BRASS * s, "brassf"))
    jw, jh = JACKETED[0] * s, JACKETED[1] * s
    jx, jy = ox + (W_o - jw) / 2, oy + H_o - BRASS * s - jh
    o.append(R(jx, jy, jw, jh, "paper", 1))
    o.append(R(jx + PAPER * s, jy + PAPER * s, CELL[1] * s, CELL[2] * s, "cellf", 1))
    o.append(T(jx + jw / 2, jy + jh / 2 + 5, "cell 34 × 5, jacketed 34.4 × 5.4", "s b", "middle"))
    rx = ox + W_o + 36
    o.append(T(rx, oy + 6, "brass, 0.25 mm", "s b brass-ink")); o.append(T(rx, oy + 22, "the lap sits inside, on top", "s muted"))
    o.append(T(rx, oy + 54, "fish paper, 0.2 mm", "s b pass-ink")); o.append(T(rx, oy + 70, "wrapped on the cell", "s muted"))
    o.append(Ln(rx - 6, oy + 2, ox + W_o + 1, oy + 2, "grid"))
    o.append(Ln(rx - 6, oy + 50, jx + jw + 1, jy + 4, "grid"))
    o.append(dim(ox, oy + H_o, ox + W_o, oy + H_o, f"outside ≈ {OUTSIDE[0]:.1f} mm", 18))
    o.append(dim(ox + BRASS * s, oy + H_o + 26, ox + W_o - BRASS * s, oy + H_o + 26, f"inside ≈ {INSIDE[0]:.0f} mm: the 35.5 panel less one bend each side", 18))
    o.append(dim(ox, oy, ox, oy + H_o, f"≈ {OUTSIDE[1]:.1f} tall", -22))
    return svg("".join(o), 250, "Cross-section of the sleeve")


def fig_pattern(scale=5.6, title=True):
    """The flat pattern: five panels across, the end flap on the floor panel."""
    s = scale
    ox, oy = 70, 70
    o = [MARKER]
    if title:
        o.append(T(20, 26, f"The flat pattern: {PAT_W:.0f} × {PAT_H:.0f} mm from the brass sheet", "t b"))
    xs = [0, TOP, TOP + WALL, TOP + WALL + TOP, TOP + WALL + TOP + WALL, PAT_W]
    names = ["TOP", "WALL", "FLOOR", "WALL", "LAP"]
    # outline: the floor panel carries the flap below it
    fx0, fx1 = xs[2] + (TOP - FLAP[0]) / 2, xs[2] + (TOP + FLAP[0]) / 2
    pts = [(0, 0), (PAT_W, 0), (PAT_W, LEN), (fx1, LEN), (fx1, LEN + FLAP[1]), (fx0, LEN + FLAP[1]), (fx0, LEN), (0, LEN)]
    o.append(P([(ox + x * s, oy + y * s) for x, y in pts], "cut", close=True))
    for i, x in enumerate(xs[1:-1]):
        o.append(Ln(ox + x * s, oy, ox + x * s, oy + LEN * s, "fold"))
    o.append(Ln(ox + fx0 * s, oy + LEN * s, ox + fx1 * s, oy + LEN * s, "fold"))
    widths = [TOP, WALL, TOP, WALL, LAP]
    for i, nm in enumerate(names):
        cx = ox + (xs[i] + xs[i + 1]) / 2 * s
        if widths[i] >= 8:
            o.append(T(cx, oy + LEN * s / 2, nm, "s b brass-ink", "middle"))
            o.append(T(cx, oy + LEN * s / 2 + 16, f"{widths[i]:g}", "s muted", "middle"))
        else:
            o.append(T(cx, oy + LEN * s / 2, nm, "s b brass-ink", "middle", f'transform="rotate(-90 {cx:.1f} {oy + LEN * s / 2:.1f})"'))
            o.append(T(cx, oy + LEN * s / 2 + 40, f"{widths[i]:g}", "s muted", "middle", f'transform="rotate(-90 {cx:.1f} {oy + LEN * s / 2 + 40:.1f})"'))
    o.append(T(ox + (fx0 + fx1) / 2 * s, oy + (LEN + FLAP[1] / 2) * s + 4, f"END FLAP {FLAP[0]:g} × {FLAP[1]:g}", "s b brass-ink", "middle"))
    # dims
    o.append(dim(ox, oy, ox + PAT_W * s, oy, f"{PAT_W:.0f}", -10))
    o.append(dim(ox + PAT_W * s, oy, ox + PAT_W * s, oy + LEN * s, f"{LEN:g}", 14))
    o.append(dim(ox + PAT_W * s, oy + LEN * s, ox + PAT_W * s, oy + PAT_H * s, f"{FLAP[1]:g}", 14))
    for i in range(5):
        o.append(dim(ox + xs[i] * s, oy + LEN * s, ox + xs[i + 1] * s, oy + LEN * s, f"{widths[i]:g}", 12 if i != 2 else 46))
    o.append(T(ox, oy + PAT_H * s + 40, "solid = cut · dashed = fold line, scored lightly on this face · this face becomes the inside", "s muted"))
    o.append(T(ox, oy + PAT_H * s + 56, "the open mouth is the end without the flap; the lead comes out there", "s muted"))
    return svg("".join(o), int(oy + PAT_H * s + 70), "Flat pattern of the sleeve")


def fig_fold():
    """Six end-view panels: the sheet becoming a tube, then the flap. Heights exaggerated."""
    sx, sz = 3.0, 9.0
    o = [MARKER, T(20, 26, "Folding, seen from the end: four folds the same way; TOP stays on the table", "t b")]
    def panel(i, title, segs, dashed=(), notes=()):
        px, py = 30 + (i % 2) * 375, 70 + (i // 2) * 150
        o.append(T(px, py, title, "s b"))
        g = f'<g transform="translate({px + 60},{py + 95})">'
        o.append(g)
        for a_, b_ in segs:
            o.append(Ln(a_[0] * sx, -a_[1] * sz, b_[0] * sx, -b_[1] * sz, "thick"))
        for a_, b_ in dashed:
            o.append(Ln(a_[0] * sx, -a_[1] * sz, b_[0] * sx, -b_[1] * sz, "fold"))
        for (x, z, txt, cls, anc) in notes:
            o.append(T(x * sx, -z * sz, txt, cls, anc))
        o.append('</g>')
    # 0 flat
    panel(0, "0 · flat, scored face up", [((0, 0), (PAT_W, 0))],
          notes=[(17.75, -1.6, "TOP", "s muted", "middle"), (39, -1.6, "WALL", "s muted", "middle"), (56.75, -1.6, "FLOOR", "s muted", "middle"),
                 (81.5, -1.6, "WALL", "s muted", "middle"), (90, -3.4, "LAP", "s muted", "middle")])
    for x in (TOP, TOP + WALL, TOP + WALL + TOP, TOP + WALL + TOP + WALL):
        o.append(Ln(30 + 60 + x * sx, 70 + 95 - 4, 30 + 60 + x * sx, 70 + 95 + 4, "grid"))
    # 1 wall up
    panel(1, "1 · fold at TOP|WALL: the wall stands up", [((0, 0), (TOP, 0)), ((TOP, 0), (TOP, WALL))],
          dashed=[((TOP, WALL), (TOP, WALL + 2.5))], notes=[(TOP + 2, WALL + 2.5, "rest: flat, in the wall's plane", "s muted", "start")])
    # 2 floor across
    panel(2, "2 · fold at WALL|FLOOR: the floor comes back over the top", [((0, 0), (TOP, 0)), ((TOP, 0), (TOP, WALL)), ((TOP, WALL), (0, WALL))],
          dashed=[((0, WALL), (-6, WALL))], notes=[(-7, WALL + 1.5, "wall + lap, still flat", "s muted", "start")])
    # 3 second wall down
    panel(3, "3 · fold at FLOOR|WALL: the second wall comes down", [((0, 0), (TOP, 0)), ((TOP, 0), (TOP, WALL)), ((TOP, WALL), (0, WALL)), ((0, WALL), (0, 0))],
          dashed=[((0, 0), (0, -3))], notes=[(2, -3.2, "lap, not yet folded", "s muted", "start")])
    # 4 lap in, on the TOP panel, inside
    panel(4, "4 · fold at WALL|LAP: the lap lies inside, on TOP", [((0, 0), (TOP, 0)), ((TOP, 0), (TOP, WALL)), ((TOP, WALL), (0, WALL)), ((0, WALL), (0, 0))],
          notes=[(0, -2.0, "lap inside, on TOP · the corner at its left is the seam", "s pass-ink", "start")])
    o.append(Ln(30 + 60 + 0.6 * sx, 70 + 300 + 95 - 0.45 * sz, 30 + 60 + LAP * sx, 70 + 300 + 95 - 0.45 * sz, "thickp"))
    # 5 flap, side view
    panel(5, "5 · the end flap folds down to close the back (side view)", [((0, 0), (LEN * 0.55, 0)), ((0, WALL), (LEN * 0.55, WALL)), ((LEN * 0.55, WALL), (LEN * 0.55, 0.5))],
          notes=[(LEN * 0.55 + 2, 3, "flap", "s muted", "start"), (-2, 3.4, "open mouth", "s muted", "end"), (LEN * 0.2, WALL + 1.5, "FLOOR", "s muted", "start"), (LEN * 0.2, -1.8, "TOP", "s muted", "start")])
    o.append(T(30, 505, "Heights exaggerated ×3. TOP lies on the table while you fold; in the device it is the face glued to the shelf,", "s muted"))
    o.append(T(30, 521, "so the lap and the seam end up on top, hidden.", "s muted"))
    return svg("".join(o), 540, "Folding sequence")


def fig_seam():
    """The soldered corner: lap inside, iron at the outer corner line."""
    o = [MARKER, T(20, 26, "The one solder seam, at the corner on top", "t b")]
    cx, cy = 430, 120
    o.append(Ln(60, cy, cx, cy, "thick"))                       # top panel, outside face up
    o.append(Ln(cx, cy, cx, 262, "thick"))                      # second wall
    o.append(Ln(cx - 3, cy + 8, cx - LAP * 26, cy + 8, "thickp"))   # the lap, inside
    o.append(T(cx - LAP * 26 - 8, cy + 12, "lap, inside", "s pass-ink", "end"))
    o.append(T(240, cy - 12, "top panel: its cut edge ends at the corner →", "s muted", "middle"))
    o.append(f'<path d="M{cx - 16},{cy - 3} Q{cx + 5},{cy - 3} {cx + 5},{cy + 18} L{cx},{cy + 18} L{cx},{cy} Z" class="solder"/>')
    o.append(T(cx + 12, cy + 26, "solder fillet", "s muted"))
    # the iron, coming in from the upper right
    o.append(f'<polygon points="{cx + 34},{cy - 30} {cx + 118},{cy - 114} {cx + 138},{cy - 94} {cx + 54},{cy - 10}" class="iron"/>')
    o.append(Ln(cx + 34, cy - 30, cx + 6, cy - 2, "edge", 3))
    o.append(T(cx + 150, cy - 96, "chisel tip, run along the corner", "s"))
    o.append(T(cx + 40, cy + 60, "Stay-Clean on the corner first,", "s warn-ink"))
    o.append(T(cx + 40, cy + 76, "then 2 s runs of the iron every 10 mm;", "s warn-ink"))
    o.append(T(cx + 40, cy + 92, "the solder wicks into the lap by itself.", "s warn-ink"))
    o.append(T(cx + 40, cy + 118, "Afterwards: baking-soda water, IPA, dry.", "s b"))
    o.append(T(cx + 40, cy + 134, "Empty, cold and washed before any paper", "s b"))
    o.append(T(cx + 40, cy + 150, "or the cell comes near it.", "s b"))
    o.append(T(70, 250, "inside of the sleeve", "s muted"))
    o.append(T(70, 290, "two more dabs tack the end flap's corners to the walls", "s muted"))
    return svg("".join(o), 305, "Soldering the seam")


def fig_jacket():
    """The fish paper jacket: pattern and the wrap."""
    s = 4.0
    ox, oy = 40, 70
    o = [MARKER, T(20, 26, f"The fish paper jacket: {JACKET[0]:g} × {JACKET[1]:g} mm, wrapped on the cell for good", "t b")]
    # pattern
    o.append(R(ox, oy, JACKET[1] * s, JACKET[0] * s, "paper", 2))
    xs = [0, 34, 39, 73, 78, 84]
    for x in xs[1:-1]:
        o.append(Ln(ox + x * s, oy, ox + x * s, oy + JACKET[0] * s, "fold"))
    for i, nm in enumerate(["under", "5", "over", "5", "lap 6"]):
        cx = ox + (xs[i] + xs[i + 1]) / 2 * s
        if xs[i + 1] - xs[i] > 10:
            o.append(T(cx, oy + JACKET[0] * s / 2 + 4, nm, "s b pass-ink", "middle"))
        else:
            o.append(T(cx, oy + JACKET[0] * s / 2 + 4, nm, "s pass-ink", "middle", f'transform="rotate(-90 {cx:.1f} {oy + JACKET[0] * s / 2 + 4:.1f})"'))
    o.append(dim(ox, oy, ox + JACKET[1] * s, oy, f"{JACKET[1]:g}", -10))
    o.append(dim(ox + JACKET[1] * s, oy, ox + JACKET[1] * s, oy + JACKET[0] * s, f"{JACKET[0]:g}", 14))
    o.append(T(ox, oy + JACKET[0] * s + 22, "cut with scissors; fold on the dashed lines, creasing with a fingernail", "s muted"))
    # the wrap, end view, big
    s2 = 9.0
    wx, wy = 470, 110
    cw, ch = CELL[1] * s2 / 2.2, CELL[2] * s2
    o.append(T(wx, oy + 10, "wrap it, end view", "s b"))
    o.append(R(wx, wy, cw, ch, "cellf", 2)); o.append(T(wx + cw / 2, wy + ch / 2 + 5, "cell", "s b", "middle"))
    pad = PAPER * s2 * 4
    o.append(P([(wx - pad, wy - pad), (wx - pad, wy + ch + pad), (wx + cw + pad, wy + ch + pad), (wx + cw + pad, wy - pad), (wx + cw * 0.55, wy - pad)], "thickp"))
    o.append(R(wx + cw * 0.55 - 2, wy - pad - 4, cw * 0.45 + pad + 4, 7, "kap2"))
    o.append(T(wx + cw + pad + 10, wy - pad + 2, "6 mm lap on top,", "s warn-ink")); o.append(T(wx + cw + pad + 10, wy - pad + 18, "one strip of Kapton", "s warn-ink"))
    o.append(T(wx, wy + ch + 40, "It stays on the cell from now on:", "s b")); o.append(T(wx, wy + ch + 56, "the jacket, not the sleeve, is the insulation.", "s b"))
    o.append(T(wx, wy + ch + 78, "Ends flush with the cell; the lead", "s muted")); o.append(T(wx, wy + ch + 94, "comes out of one end as before.", "s muted"))
    return svg("".join(o), int(oy + JACKET[0] * s + 50), "The fish paper jacket")


def fig_place():
    """Front view of the frame: the sleeve under the PowerBoost shelf, storeys from the whole-build page,
    the frame 40 inside because the screen now floats at 17.5 (header strips kept)."""
    IN_X, IN_Z = 65.0, 40.0
    sx, sz = 6.6, 7.0
    X = lambda x: 140 + x * sx
    Z = lambda z: 335 - (z + 17.5) * sz
    o = [MARKER, T(20, 26, "Where it lives: the bottom storey, hung from the PowerBoost's shelf", "t b")]
    o.append(R(X(-1.5), Z(IN_Z - 17.5), (IN_X + 3) * sx, IN_Z * sz, "frame", 3))
    # harness card and a hint of the harness
    o.append(R(X(0.5), Z(0), 64 * sx, 0.3 * sz + 2, "card"))
    o.append(T(X(IN_X) + 10, Z(0) + 4, "harness card", "s muted"))
    o.append(R(X(3.5), Z(4.4), 18 * sx, 1.6 * sz, "pcb", 1)); o.append(T(X(12.5), Z(4.4) - 4, "A1", "s muted", "middle"))
    o.append(R(X(30), Z(4.1), 17 * sx, 1.6 * sz, "pcb", 1)); o.append(T(X(38.5), Z(4.1) - 4, "amp", "s muted", "middle"))
    o.append(R(X(17.5), Z(18.7), 27 * sx, 1.2 * sz, "screen-side", 1)); o.append(R(X(17.5), Z(20.5), 27 * sx, 1.8 * sz, "glass", 1))
    o.append(T(X(45) + 6, Z(19.0) + 4, "screen on its rods, 17.5 up", "s muted"))
    for x in (27.2, 29.7, 32.3, 34.8):
        o.append(Ln(X(x), Z(17.5), X(x), Z(5.0), "edge", 2))
    # PowerBoost storey, the shelf under it
    o.append(R(X(20), Z(-0.5), 45 * sx, 10 * sz, "cap", 2)); o.append(T(X(42.5), Z(-5.5) + 4, "PowerBoost, 10 mm", "s b", "middle"))
    o.append(R(X(0.5), Z(-11) - (0.3 * sz + 2), 64 * sx, 0.3 * sz + 2, "card")); o.append(T(X(IN_X) + 10, Z(-11) + 1, "PowerBoost shelf", "s muted"))
    # the sleeve, hung under the shelf
    o.append(R(X(1.5), Z(-11), LEN * sx, OUTSIDE[1] * sz, "brass", 2))
    o.append(R(X(1.5) + 4, Z(-11) + 4, LEN * sx - 8, OUTSIDE[1] * sz - 8, "paperf"))
    o.append(T(X(33), Z(-14.3) + 4, "brass sleeve, 63 long, 6.5 tall, the jacketed cell inside", "s b", "middle"))
    o.append(Ln(X(3), Z(-11) + 1, X(63), Z(-11) + 1, "gluel"))
    o.append(T(X(IN_X) + 10, Z(-12.5) + 4, "hot glue: two thin lines", "s pass-ink"))
    o.append(T(X(IN_X) + 10, Z(-14.3) + 4, "along the top's long edges", "s pass-ink"))
    o.append(T(X(1.5), Z(-18.6) + 6, "open mouth, left", "s muted"))
    o.append(T(X(64.5), Z(-18.6) + 6, "flap, right", "s muted", "end"))
    # the lead: out of the mouth, up the left wall, through the shelf, into the JST at the board's left end
    o.append(P([(X(1.5), Z(-14.3)), (X(-0.6), Z(-14.3)), (X(-0.6), Z(-10.2)), (X(21), Z(-10.2)), (X(21), Z(-7.5))], "lead"))
    o.append(T(X(2.5), Z(-8.6) + 4, "lead → notch → JST", "s"))
    for z, lab in ((0, "harness plane, 0"), (-11, "shelf, −11"), (-17.5, "bottom loop, −17.5"), (IN_Z - 17.5, "top loop, +22.5")):
        o.append(Ln(X(-1.5) - 6, Z(z), X(IN_X) + 6, Z(z), "grid", dash="4 4"))
        o.append(T(X(-1.5) - 10, Z(z) + 4, lab, "s muted", "end"))
    o.append(T(X(-1.5), 372, "inside 65 × 39 × 40: with the header strips kept, the screen floats at 17.5,", "s warn-ink"))
    o.append(T(X(-1.5), 388, "so the battery frame needs 40 inside (43 outside), not the 35 on the whole-build page.", "s warn-ink"))
    o.append(T(X(-1.5), 406, "The sleeve is 0.3 mm taller than the cradle it replaces; the shelf rides that much higher.", "s muted"))
    return svg("".join(o), 420, "The sleeve in the frame")


def fig_mouth():
    """Side view of the open end: the Kapton tab, the lead's Kapton wrap at the rim."""
    s = 9.0
    ox, oy = 60, 96
    o = [MARKER, T(20, 26, "The open mouth: one tab of Kapton, one wrap on the lead", "t b")]
    L_ = 36 * s
    hh = OUTSIDE[1] * s
    o.append(R(ox + 40, oy, L_, hh, "brass", 2))
    o.append(R(ox + 43, oy + 3, L_ - 3, hh - 6, "paperf"))
    o.append(T(ox + 40 + L_ / 2, oy + hh / 2 + 4, "cell in its jacket", "s b", "middle"))
    # Kapton tab: 5 mm on top, down over the mouth, 5 mm under
    o.append(P([(ox + 40 + 5 * s, oy - 4), (ox + 36, oy - 4), (ox + 36, oy + hh + 4), (ox + 40 + 5 * s, oy + hh + 4)], "tapeline", 7))
    o.append(T(ox + 40 + 5 * s + 10, oy - 12, "Kapton tab, 20 mm: 5 on top, over the mouth, 5 under", "s warn-ink"))
    # the lead, out of the mouth and up; its wrap at the rim
    o.append(P([(ox + 40, oy + hh / 2), (ox + 6, oy + hh / 2), (ox - 30, oy + hh / 2 - 44)], "lead"))
    o.append(R(ox + 12, oy + hh / 2 - 6, 28, 12, "kap2", 3))
    o.append(T(ox - 40, oy - 2, "to the JST ↗", "s"))
    o.append(T(ox + 14, oy + hh + 44, "10 mm of Kapton on the lead where it crosses the brass rim", "s warn-ink"))
    o.append(T(ox + 14, oy + hh + 60, "(the rim is sanded round; this is belt and braces)", "s muted"))
    o.append(T(ox + 14, oy + hh + 92, "To take the cell out: peel the tab, pull the lead gently, the jacketed cell slides out of the mouth.", "s b"))
    return svg("".join(o), 270, "The open mouth")


def fig_meter():
    s = 8.0
    ox, oy = 80, 120
    hh = OUTSIDE[1] * s * 1.6
    o = [MARKER, T(20, 26, "Before the switch goes on: the sleeve must be an island", "t b")]
    o.append(R(ox, oy, 40 * s, hh, "brass", 2))
    o.append(T(ox + 20 * s, oy + hh / 2 + 5, "sleeve, cell inside, plugged in", "s b", "middle"))
    o.append(P([(ox + 40 * s, oy + 30), (ox + 40 * s + 50, oy + 30), (ox + 40 * s + 50, oy - 10), (ox + 40 * s + 110, oy - 10)], "lead"))
    o.append(R(ox + 40 * s + 110, oy - 24, 60, 28, "box", 3)); o.append(T(ox + 40 * s + 140, oy - 6, "JST", "s b", "middle"))
    o.append(Ln(ox + 10 * s, oy - 36, ox + 10 * s, oy + 2, "edge", 3)); o.append(T(ox + 10 * s, oy - 44, "probe 1: on the brass", "s", "middle"))
    o.append(Ln(ox + 40 * s + 170, oy - 54, ox + 40 * s + 170, oy - 24, "edge", 3)); o.append(T(ox + 40 * s + 170, oy - 62, "probe 2: each JST pin in turn", "s", "middle"))
    o.append(T(ox, oy + hh + 30, "Ω range: sleeve to JST +  →  OL · sleeve to JST −  →  OL · sleeve to the GND rail  →  OL", "s b"))
    o.append(T(ox, oy + hh + 50, "Sleeve to frame may read 0: both are metal, both are islands.", "s muted"))
    o.append(T(ox, oy + hh + 66, "Anything but OL on the three above: cell out, find the scrape.", "s muted"))
    return svg("".join(o), int(oy + hh + 84), "Meter check")


def pattern_letter_svg():
    """1:1 pattern on Letter for cutting: mm units, a 50 mm bar to verify the print."""
    px = 3.7795
    W, H = 216, 279
    ox, oy = 30, 40
    xs = [0, TOP, TOP + WALL, TOP + WALL + TOP, TOP + WALL + TOP + WALL, PAT_W]
    fx0, fx1 = xs[2] + (TOP - FLAP[0]) / 2, xs[2] + (TOP + FLAP[0]) / 2
    pts = [(0, 0), (PAT_W, 0), (PAT_W, LEN), (fx1, LEN), (fx1, LEN + FLAP[1]), (fx0, LEN + FLAP[1]), (fx0, LEN), (0, LEN)]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W * px:.2f} {H * px:.2f}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="{ox * px:.1f}" y="{18 * px:.1f}" font-size="{4.5 * px:.1f}" font-family="sans-serif" font-weight="bold">Brass battery sleeve · cutting pattern · 1:1</text>',
         f'<text x="{ox * px:.1f}" y="{25 * px:.1f}" font-size="{2.8 * px:.1f}" font-family="sans-serif">Print at Actual size on Letter. Check the 50 mm bar with the caliper before cutting. Solid = cut. Dashed = fold; score on this face.</text>',
         f'<text x="{ox * px:.1f}" y="{30 * px:.1f}" font-size="{2.8 * px:.1f}" font-family="sans-serif">Stick this sheet to the brass with glue stick or Kapton at the corners, cut through both, then peel.</text>']
    d = " ".join(f"{(ox + x) * px:.2f},{(oy + y) * px:.2f}" for x, y in pts)
    o.append(f'<polygon points="{d}" fill="none" stroke="black" stroke-width="{0.3 * px:.2f}"/>')
    for x in xs[1:-1]:
        o.append(f'<line x1="{(ox + x) * px:.2f}" y1="{oy * px:.2f}" x2="{(ox + x) * px:.2f}" y2="{(oy + LEN) * px:.2f}" stroke="black" stroke-width="{0.25 * px:.2f}" stroke-dasharray="{2 * px:.1f} {1.2 * px:.1f}"/>')
    o.append(f'<line x1="{(ox + fx0) * px:.2f}" y1="{(oy + LEN) * px:.2f}" x2="{(ox + fx1) * px:.2f}" y2="{(oy + LEN) * px:.2f}" stroke="black" stroke-width="{0.25 * px:.2f}" stroke-dasharray="{2 * px:.1f} {1.2 * px:.1f}"/>')
    labels = [("TOP 35.5", (xs[0] + xs[1]) / 2), ("FLOOR 35.5", (xs[2] + xs[3]) / 2), ("LAP 8", (xs[4] + xs[5]) / 2)]
    for lab, cx in labels:
        o.append(f'<text x="{(ox + cx) * px:.1f}" y="{(oy + LEN / 2) * px:.1f}" font-size="{3 * px:.1f}" font-family="sans-serif" text-anchor="middle" fill="#444">{lab}</text>')
    for cx in ((xs[1] + xs[2]) / 2, (xs[3] + xs[4]) / 2):
        o.append(f'<text x="{(ox + cx) * px:.1f}" y="{(oy + LEN / 2) * px:.1f}" font-size="{2.6 * px:.1f}" font-family="sans-serif" text-anchor="middle" fill="#444" transform="rotate(-90 {(ox + cx) * px:.1f} {(oy + LEN / 2) * px:.1f})">WALL 6.5</text>')
    o.append(f'<text x="{(ox + (fx0 + fx1) / 2) * px:.1f}" y="{(oy + LEN + 4) * px:.1f}" font-size="{2.6 * px:.1f}" font-family="sans-serif" text-anchor="middle" fill="#444">END FLAP 34.5 × 6</text>')
    o.append(f'<text x="{(ox + PAT_W / 2) * px:.1f}" y="{(oy - 3) * px:.1f}" font-size="{2.6 * px:.1f}" font-family="sans-serif" text-anchor="middle" fill="#444">← this edge is the open mouth: no flap →</text>')
    # scale bar
    by = oy + PAT_H + 25
    o.append(f'<line x1="{ox * px:.2f}" y1="{by * px:.2f}" x2="{(ox + 50) * px:.2f}" y2="{by * px:.2f}" stroke="black" stroke-width="{0.4 * px:.2f}"/>')
    for i in range(6):
        o.append(f'<line x1="{(ox + i * 10) * px:.2f}" y1="{(by - 2) * px:.2f}" x2="{(ox + i * 10) * px:.2f}" y2="{(by + 2) * px:.2f}" stroke="black" stroke-width="{0.3 * px:.2f}"/>')
    o.append(f'<text x="{(ox + 55) * px:.1f}" y="{(by + 1.2) * px:.1f}" font-size="{3 * px:.1f}" font-family="sans-serif">50 mm: measure this with the caliper; 49–51 is a good print</text>')
    # jacket pattern on the same sheet
    jx, jy = ox, by + 15
    o.append(f'<rect x="{jx * px:.2f}" y="{jy * px:.2f}" width="{JACKET[1] * px:.2f}" height="{JACKET[0] * px:.2f}" fill="none" stroke="black" stroke-width="{0.3 * px:.2f}"/>')
    for x in (34, 39, 73, 78):
        o.append(f'<line x1="{(jx + x) * px:.2f}" y1="{jy * px:.2f}" x2="{(jx + x) * px:.2f}" y2="{(jy + JACKET[0]) * px:.2f}" stroke="black" stroke-width="{0.25 * px:.2f}" stroke-dasharray="{2 * px:.1f} {1.2 * px:.1f}"/>')
    o.append(f'<text x="{(jx + JACKET[1] / 2) * px:.1f}" y="{(jy - 3) * px:.1f}" font-size="{3 * px:.1f}" font-family="sans-serif" text-anchor="middle">fish paper jacket · 84 × 63 · dashed = fold</text>')
    o.append('</svg>')
    return "".join(o)


# ---------------------------------------------------------------- the page
def fig(svg_, caption=""):
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure><div class="scroll">{svg_}</div>{cap}</figure>'


def step(sid, do, check=None):
    chk = f'<span class="chk">{check}</span>' if check else ""
    return f'<div class="step"><input type="checkbox" id="{sid}"><label for="{sid}"><span class="do">{do}</span>{chk}</label></div>'


def main():
    OUT_PATTERN.write_text(pattern_letter_svg())
    H = ['<title>Brass Battery Sleeve</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style(), EXTRA_CSS,
         '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · final build · the cell\'s brass sleeve</div>',
         '<h1>The brass battery sleeve</h1>',
         f'<p class="lede">A flat brass tube, 63 mm long, folded from one piece of 0.25 mm sheet, with the cell inside it in a jacket of fish paper. From outside it is one brass block under the PowerBoost, the same yellow as the rods; the green paper is never seen. One purchase: the sheet. Everything else is on your bench.</p>']
    H.append(f'<p class="stock"><strong>Buy:</strong> {a("sheet")} · <strong>Own:</strong> {a("fish")} · {a("kapton")} · {a("knife")} · {a("mat")} · {a("sand")} · {a("pliers")} · {a("caliper")} · {a("harris")} · {a("solder")} · {a("ipa")} · hot glue gun · {a("cell1200")}</p>')

    H.append('<h2>What it is</h2>')
    H.append(fig(fig_section(), '<strong>Three layers.</strong> Brass is the outside and the structure; fish paper is the insulation and stays wrapped on the cell; the cell floats in the middle with 0.6 mm to spare each way. The brass never touches the cell, the paper never shows.'))
    H.append(fig(fig_place(), f'<strong>It replaces the cardstock cradle</strong> of the <a href="{WHOLE}" target="_blank" rel="noopener">whole-build page</a>, in the same 6.5 mm storey, hung from the underside of the PowerBoost\'s shelf by two lines of hot glue. The open mouth faces left, under the PowerBoost\'s JST socket; the lead comes out of it and climbs through a notch in the shelf. In the silver rebuild the sleeve can be soldered straight onto the bottom loop instead; this version comes off with a fingernail. One consequence of keeping the header strips shows here: the screen now floats 17.5 mm up, so the battery frame needs 40 mm inside (43 outside), 5 more than the whole-build page drew.'))

    H.append('<h2>The pattern</h2>')
    H.append(fig(fig_pattern(), f'<strong>{PAT_W:.0f} × {PAT_H:.0f} mm, five panels and a flap.</strong> TOP and FLOOR are 35.5, the two WALLs 6.5, the LAP 8; one sharp bend eats about 0.45 mm, so the tube comes out ≈ 35 × 6 inside, exactly what a jacketed cell (34.4 × 5.4) needs. The flap on the floor panel folds up to close the back. <a href="brass-sleeve-pattern-letter.svg" target="_blank" rel="noopener">The 1:1 pattern</a> prints on Letter at Actual size with a 50 mm bar to check it.'))
    H.append(fig(fig_fold(), '<strong>Four folds, all the same way.</strong> Keep TOP flat on the table and fold everything else around it: wall up, floor across, wall down, lap in. Because the lap folds inside, the top\'s outer face stays perfectly flat for the glue, and the seam is the corner line on top, hidden under the shelf.'))
    H.append(fig(fig_seam(), '<strong>One seam, soldered from outside.</strong> Brass to brass, so this is a Stay-Clean job like the frame: flux along the corner, a chisel tip run along it, the solder wicks into the lap. Two dabs tack the flap\'s corners. Then neutralise, rinse, dry: nothing comes near the paper or the cell until the sleeve is cold, clean and dry. If you would rather not flux, a strip of Kapton along the inside of the lap holds the tube shut too; it is hidden either way.'))
    H.append(fig(fig_jacket(), '<strong>The jacket, 84 × 63 of fish paper.</strong> Under, up, over, down, 6 mm of lap on top closed with one strip of Kapton. It goes on the cell once and stays: the cell is never handled bare again, and whatever happens to the brass, there is 0.2 mm of flame-rated paper between it and the pouch.'))
    H.append(fig(fig_mouth(), '<strong>Two pieces of Kapton finish it.</strong> A 20 mm tab folded over the open mouth is the seat belt; 10 mm wrapped on the lead where it crosses the brass rim means no edge ever rubs the wire. Peel the tab and the cell slides out, jacket and all.'))

    H.append('<h2>Build it: 14 steps</h2>')
    H.append('<p>Bench rule for this part: the cell stays in its bag until step 11. Brass dust, the knife, the iron and the acid flux are all done by then.</p>')
    H.append(step("s1", f"Print <a href='brass-sleeve-pattern-letter.svg' target='_blank' rel='noopener'>the 1:1 pattern</a> at Actual size and measure its 50 mm bar with the {a('caliper', 'caliper')}.", "49–51 mm. Outside that, print again with scaling off."))
    H.append(step("s2", f"Stick the printed pattern to the {a('sheet', 'brass sheet')} with a glue stick or four corner dabs of {a('kapton', 'Kapton')}, near one corner of the sheet so the rest stays whole.", "The pattern lies flat with no bubbles under the fold lines."))
    H.append(step("s3", "Cut along the solid lines with sturdy household scissors, through paper and brass together; 0.25 mm brass cuts like thick card. Cut the two notches beside the flap last.", "One piece, 92 × 69 with the flap; measure the long edge: 91–93."))
    H.append(step("s4", f"Score the five dashed lines through the paper with the {a('knife', 'craft knife')} against a steel ruler on the {a('mat', 'cutting mat')}: two light passes each, a groove you can feel, never a cut.", "Hold it to the light: a bright line on every fold, no crack."))
    H.append(step("s5", f"Peel the paper off, then take every edge with the {a('sand', '400 grit')}, four strokes each, and wipe the dust away with a tissue. Safety glasses on from here to step 8.", "Run a fingertip along every edge: nothing catches."))
    H.append(step("s6", f"Fold 1: clamp the sheet under the ruler exactly on the first score line (TOP · WALL), with the scored face up, and lift the overhang to 90° with the flat of the {a('pliers', 'pliers')} along its whole length.", "A crisp, straight corner; the caliper reads 35.5 outside on the TOP panel."))
    H.append(step("s7", "Folds 2, 3 and 4 the same way, in order: FLOOR across, second WALL down, LAP in until it lies flat on the inside of TOP; then the end flap up to close the back.", f"Inside width 35 ± 0.3, inside height 6 ± 0.3 at both ends; a 34.5 × 5.5 cardstock stack slides through without scraping."))
    H.append(step("s8", f"Solder the seam: {a('harris', 'Stay-Clean')} along the corner line on top, the chisel tip run along it in 2 s passes, solder fed every 10 mm; two dabs on the flap's corners. Then wash: baking-soda water, rinse with {a('ipa', 'IPA')}, dry an hour.", "The lap does not spring open when you squeeze the walls; no white residue anywhere; dry and cold."))
    H.append(step("s9", "Sand the two mouths round once more, especially the open one, and wipe. The brass is finished.", "No burr at either mouth. If you want it to stay bright, one coat of clear lacquer now, outside only."))
    H.append(step("s10", f"Hot-glue it to the underside of the PowerBoost's shelf: two thin lines along TOP's long edges, press for twenty seconds, open mouth at the shelf's left edge where the notch for the lead is.", "Lift the shelf: the sleeve hangs without a wobble, flush with the shelf's left edge."))
    H.append(step("s11", f"Cut the jacket, 84 × 63, from the {a('fish', 'fish paper')}; wrap the cell under-up-over-down with the lap on top, and close the lap with one strip of {a('kapton', 'Kapton')} the full length.", "Snug, ends flush with the cell, the lead free at one end; it does not slide on the cell."))
    H.append(step("s12", "Slide the jacketed cell into the sleeve lead-end last, until it stops on the flap; the lead hangs out of the open mouth.", "Flush at the mouth, no scrape on the way in; if it drags, the jacket's lap is too thick: re-tape it flatter."))
    H.append(step("s13", "Wrap 10 mm of Kapton on the lead where it crosses the rim, fold the 20 mm tab over the mouth, and feed the lead up through the shelf's notch to the JST (not plugged yet).", "The cell cannot move in any direction by hand."))
    H.append(step("s14", f"Meter, Ω range: sleeve to JST +, sleeve to JST −, sleeve to the GND rail. Then plug in with the switch off.", "OL, OL, OL. Anything else: cell out, find the scrape in the jacket."))
    H.append(fig(fig_meter(), '<strong>The last check.</strong> The sleeve is allowed to touch the frame (both are metal islands) but nothing electrical. Three OL readings and it is a battery device.'))

    H.append('<h2>Materials: do you have it all?</h2>')
    H.append('<p>Everything but the sheet (the PowerBoost arrived on 2026-10-14 as a third-party copy; its pins still need checking on the bench). Two household items are not in the inventory because they are not purchases: sturdy scissors and a steel ruler (the caliper\'s beam works for the short lines).</p>')
    rows = [
        ("Brass sheet 0.010 in × 4 × 10 in", "sheet", "buy", "one sheet makes ten sleeves; 0.25 mm folds by hand and holds a crease"),
        ("Fish paper 0.2 mm", "fish", "own", "the jacket, 84 × 63"),
        ("Kapton tape", "kapton", "own", "jacket lap, mouth tab, lead wrap, holding the pattern"),
        ("Craft knife", "knife", "own", "scoring the fold lines"),
        ("Cutting mat", "mat", "own", "under the scoring"),
        ("400 grit", "sand", "own", "every edge and both mouths"),
        ("Chain-nose pliers", "pliers", "own", "the folds, flat jaw along the line"),
        ("Caliper", "caliper", "own", "the print check and the inside size"),
        ("Harris Stay-Clean flux", "harris", "own", "the one brass seam; baking soda and IPA afterwards"),
        ("63/37 solder", "solder", "own", "the seam"),
        ("91 % IPA", "ipa", "own", "rinse after the acid flux"),
        ("Soldering station, chisel tip", None, "own", "owned · no link recorded"),
        ("Hot glue gun, low-temp, white sticks", None, "own", "owned · no link recorded; two thin lines"),
        ("Cell, 1200 mAh #258", "cell1200", "own", "62 × 34 × 5; the only cell this fits"),
        ("Baking soda · safety glasses", None, "own", "owned, bought locally / Amazon #5"),
        ("Scissors · steel ruler", None, "own", "household; tin snips are not needed for 0.25 mm"),
        ("PowerBoost 1000C (copy, Amazon #20)", "powerboost_owned", "own", f"not part of this piece, but the shelf it hangs from is the PowerBoost\'s: see the <a href=\"{POWER}\" target=\"_blank\" rel=\"noopener\">power page</a>"),
    ]
    H.append('<div class="scrollx"><table class="t"><tr><th>Item</th><th>Status</th><th>The product</th><th>Used for</th></tr>')
    for name, key, st, use in rows:
        link = a(key) if key else "—"
        H.append(f'<tr><td>{name}</td><td class="{st}">{"BUY" if st == "buy" else "own"}</td><td>{link}</td><td>{use}</td></tr>')
    H.append('</table></div>')
    H.append('<p>For the nickel-silver rebuild the same pattern works in nickel-silver sheet (not sourced yet); a brass sleeve under a silver frame is also fine.</p>')

    H.append('<div class="evidence"><p><strong>Sources and limits.</strong> Cell size from <code>docs/INVENTORY.md</code> (Adafruit #258, 62 × 34 × 5); sheet thickness from the K&amp;S listing; storey heights from <code>gen/whole_build_page.py</code>. The bend allowance (0.45 mm per sharp fold in 0.25 mm sheet) is a hand-bending estimate, which is why step 7 measures the inside before anything goes in. Nothing here has been built yet; the numbers are the design.</p></div>')
    H.append('</div>')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size, "and", OUT_PATTERN)


if __name__ == "__main__":
    main()
