"""SVG drawing helpers for the harness pages. Everything is drawn from harness_model."""
from __future__ import annotations

import html
import math

import harness_model as M

S = 10.0          # px per mm in the top view
OX, OY = 50.0, 40.0   # origin of the floor rectangle in the top view (front at the bottom)

NET_COLOR = {
    "5V": "var(--w-red)", "GND": "var(--w-black)", "3V3": "var(--w-orange)",
    "GPIO1": "var(--w-yellow)", "GPIO2": "var(--w-white)", "GPIO3": "var(--w-blue)", "GPIO4": "var(--w-green)",
    "AMPSD": "var(--w-olive)", "GPIO10": "var(--w-purple)", "GPIO20": "var(--w-teal)", "GPIO21": "var(--w-navy)",
    "GAIN": "var(--w-olive)",
}
NET_LABEL = {
    "5V": "5 V", "GND": "GND", "3V3": "3V3", "GPIO1": "WS (GPIO1)", "GPIO2": "BCLK (GPIO2)", "GPIO3": "DIN (GPIO3)",
    "GPIO4": "mic SD (GPIO4)", "AMPSD": "amp SD (GPIO5)", "GPIO10": "button (GPIO10)", "GPIO20": "SCL (GPIO20)", "GPIO21": "SDA (GPIO21)",
    "GAIN": "GAIN",
}


def esc(t):
    return html.escape(str(t), quote=True)


def tx(x):
    return OX + x * S


def ty(y):
    return OY + (M.INSIDE_Y - y) * S


def rect(b, cls, rx=2, extra=""):
    return (f'<rect x="{tx(b["x0"]):.1f}" y="{ty(b["y1"]):.1f}" width="{(b["x1"]-b["x0"])*S:.1f}" '
            f'height="{(b["y1"]-b["y0"])*S:.1f}" rx="{rx}" class="{cls}" {extra}/>')


def text(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def label_at(x, y, s, cls="s", anchor="middle", dy=0):
    return text(tx(x), ty(y) + dy, s, cls, anchor)


def poly_top(c: M.Cond, width=3.0, color=None, opacity=1.0, dash=None, cls=""):
    """A conductor's XY projection as a polyline; vertical segments collapse to points."""
    color = color or NET_COLOR.get(c.net, "var(--brass)")
    pts = " ".join(f"{tx(p[0]):.1f},{ty(p[1]):.1f}" for p in c.pts)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{opacity}"{d} class="{cls}"/>')


def sleeves_top(c: M.Cond, width=7.0):
    out = []
    for si, t0, t1 in c.sleeve:
        p, q = c.pts[si], c.pts[si + 1]
        a = [p[k] + (q[k] - p[k]) * t0 for k in range(3)]
        b = [p[k] + (q[k] - p[k]) * t1 for k in range(3)]
        out.append(f'<line x1="{tx(a[0]):.1f}" y1="{ty(a[1]):.1f}" x2="{tx(b[0]):.1f}" y2="{ty(b[1]):.1f}" '
                   f'stroke="var(--figure-bg)" stroke-width="{width}" stroke-linecap="round"/>')
        out.append(f'<line x1="{tx(a[0]):.1f}" y1="{ty(a[1]):.1f}" x2="{tx(b[0]):.1f}" y2="{ty(b[1]):.1f}" '
                   f'stroke="currentColor" stroke-width="{width}" stroke-linecap="round" fill="none" opacity=".9" stroke-dasharray="2 2"/>')
    return "".join(out)


def stub_dot(x, y, r=3.2, cls="stubp"):
    return f'<circle cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="{r}" class="{cls}"/>'


def parts_top(dim=False, labels=True):
    """All the parts in the top view (labels drawn by part_labels, last)."""
    o = []
    cls_board = "pcb" if not dim else "pcb dim"
    o.append(rect(M.A1, cls_board, 3))
    o.append(rect(M.USB, "box", 1))
    o.append(rect(M.A1_ANT, "ant", 1))
    o.append(rect(M.AMP, cls_board, 3))
    o.append(rect(M.AMP_BLOCK, "box", 1))
    o.append(f'<circle cx="{tx(M.MIC_C[0]):.1f}" cy="{ty(M.MIC_C[1]):.1f}" r="{M.MIC_D/2*S:.1f}" class="{cls_board}"/>')
    o.append(f'<circle cx="{tx(M.MIC_PORT[0]):.1f}" cy="{ty(M.MIC_PORT[1]):.1f}" r="{0.6*S:.1f}" class="port"/>')
    o.append(rect(M.SPK, "spk", 3))
    o.append(rect(M.CAP220, "cap", 12))
    o.append(rect(M.BTN, "box", 2))
    o.append(f'<circle cx="{tx((M.BTN["x0"]+M.BTN["x1"])/2):.1f}" cy="{ty((M.BTN["y0"]+M.BTN["y1"])/2):.1f}" r="{1.7*S:.1f}" class="edge"/>')
    # stubs
    for st in M.stubs():
        p = st.pts[0]
        o.append(stub_dot(p[0], p[1]))
    return "".join(o)


def part_labels():
    o = []
    if True:
        o.append(label_at(12.5, 14.5, "A1", "t b"))
        o.append(label_at(12.5, 4.0, "USB", "s muted", dy=4))
        o.append(label_at(12.5, 22.4, "antenna", "s warn-ink", dy=4))
        o.append(label_at(38.5, 18.5, "amp", "t b"))
        o.append(label_at(46.0, 12.2, "block", "s muted", "middle", 4))
        o.append(label_at(30.0, 36.6, "mic, pins up", "s b", "middle", 4))
        o.append(label_at(47.0, 31.0, "speaker, mesh up", "s b", "middle", 4))
        o.append(label_at(53.65, 9.0, "220 µF", "s b", "middle", 4))
        o.append(label_at(12.0, 8.6, "button", "s b", "middle", -3))
        # pin names
        for name, y in zip(M.A1_RIGHT, M.A1_PIN_Y):
            o.append(text(tx(M.A1_RIGHT_X) - 6, ty(y) + 3.5, name.replace("GPIO", ""), "pin", "end"))
        for name, y in zip(M.A1_LEFT, M.A1_PIN_Y):
            o.append(text(tx(M.A1_LEFT_X) + 6, ty(y) + 3.5, name.replace("GPIO", ""), "pin", "start"))
        for name, y in zip(M.AMP_PINS, M.AMP_PIN_Y):
            o.append(text(tx(M.AMP_PIN_X) + 6, ty(y) + 3.5, name, "pin", "start"))
        for name, y in zip(M.MIC_LEFT, M.MIC_PIN_Y):
            o.append(text(tx(M.MIC_COL_X[0]) - 6, ty(y) + 3.5, name, "pin", "end"))
        for name, y in zip(M.MIC_RIGHT, M.MIC_PIN_Y):
            o.append(text(tx(M.MIC_COL_X[1]) + 6, ty(y) + 3.5, name, "pin", "start"))
        for name, x in zip(M.SCREEN_PINS, M.SCREEN_PIN_X):
            o.append(text(tx(x), ty(0.9) + 3, name, "pin", "middle"))
    return "".join(o)


def screen_outline():
    b = M.SCREEN
    return (f'<rect x="{tx(b["x0"]):.1f}" y="{ty(b["y1"]):.1f}" width="{(b["x1"]-b["x0"])*S:.1f}" height="{(b["y1"]-b["y0"])*S:.1f}" '
            f'rx="4" class="screen-out"/>' + text(tx(1.5), ty(31.0), "dashed: the screen, 17.5 mm up,", "s acc-ink") + text(tx(1.5), ty(29.6), "its four stubs at the front", "s acc-ink"))


def frame_top():
    return (f'<rect x="{tx(0):.1f}" y="{ty(M.INSIDE_Y):.1f}" width="{M.INSIDE_X*S:.1f}" height="{M.INSIDE_Y*S:.1f}" class="frame"/>'
            + "".join(f'<circle cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="{0.5*S:.1f}" class="post"/>'
                      for x in (0.5, M.INSIDE_X - 0.5) for y in (0.5, M.INSIDE_Y - 0.5)))


def svg_wrap(body, w=760, h=520, label="", vb=None):
    vb = vb or f"0 0 {w} {h}"
    return f'<svg viewBox="{vb}" role="img" aria-label="{esc(label)}">{body}</svg>'


def map_figure(highlight=None, dim_others=True, title="", show_screen=True, width=3.0, extra="", labels=True):
    """The whole harness in top view. highlight: set of conductor names drawn bold; others dimmed."""
    conds = M.rods() + M.small_parts()
    o = [frame_top(), parts_top(labels=labels)]
    if show_screen:
        o.append(screen_outline())
    hl = set(highlight or [])
    # draw dimmed first, highlighted last
    for c in conds:
        if hl and c.name in hl:
            continue
        if c.kind == "body":
            o.append(poly_top(c, width=c.r * 2 * S * 0.7, color="var(--warn)", opacity=0.18 if hl else 0.45))
        else:
            o.append(poly_top(c, width=width if c.kind == "rod" else 1.8, opacity=0.22 if (hl and dim_others) else 1.0))
            if not hl:
                o.append(sleeves_top(c))
    for c in conds:
        if c.name in hl:
            if c.kind == "body":
                o.append(poly_top(c, width=c.r * 2 * S * 0.7, color="var(--warn)", opacity=0.75))
            else:
                o.append(poly_top(c, width=width + 1.5 if c.kind == "rod" else 2.6))
                o.append(sleeves_top(c))
                # joints: endpoints
                for p in (c.pts[0], c.pts[-1]):
                    o.append(f'<circle cx="{tx(p[0]):.1f}" cy="{ty(p[1]):.1f}" r="5" class="joint"/>')
    if labels:
        o.append(part_labels())
    if title:
        o.append(text(OX, 22, title, "t b"))
    o.append(text(tx(0), ty(0) + 18, "front of the device (USB) · 10 px = 1 mm", "s muted"))
    o.append(extra)
    return svg_wrap("".join(o), 760, int(OY + M.INSIDE_Y * S + 40), title or "Top view of the harness")


# ---------------------------------------------------------------- unrolled side profile
def unrolled(c: M.Cond, w=760, h=230, title=None):
    """Z against distance along the rod's path: every bend as a corner, with the length of each segment."""
    pts = c.pts
    s_acc = [0.0]
    for a, b in c.segs():
        s_acc.append(s_acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = s_acc[-1]
    zmax = max(p[2] for p in pts)
    zmin = min(p[2] for p in pts)
    px0, px1 = 60, w - 70
    py0, py1 = 58, h - 60
    sc = (px1 - px0) / max(total, 8.0)
    zsc = min((py1 - py0) / max(zmax - 0.0, 6.0), sc * 2.2)
    X = lambda s: px0 + s * sc
    Y = lambda z: py1 - z * zsc
    o = []
    # floor line
    o.append(f'<line x1="{px0-20}" y1="{Y(0):.1f}" x2="{px1+10}" y2="{Y(0):.1f}" class="floor"/>')
    o.append(text(px0 - 22, Y(0) + 4, "card", "s muted", "end"))
    for z in (5.0, 8.0, 10.5, 12.5):
        if z <= zmax + 0.5:
            o.append(f'<line x1="{px0-10}" y1="{Y(z):.1f}" x2="{px1+10}" y2="{Y(z):.1f}" class="grid dashed"/>')
            o.append(text(px0 - 14, Y(z) + 4, f"{z:g}", "s muted", "end"))
    path = " ".join(f"{X(s_acc[i]):.1f},{Y(pts[i][2]):.1f}" for i in range(len(pts)))
    o.append(f'<polyline points="{path}" fill="none" stroke="{NET_COLOR.get(c.net, "var(--brass)")}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    # sleeves
    for si, t0, t1 in c.sleeve:
        s0 = s_acc[si] + (s_acc[si + 1] - s_acc[si]) * t0
        s1 = s_acc[si] + (s_acc[si + 1] - s_acc[si]) * t1
        z0 = pts[si][2] + (pts[si + 1][2] - pts[si][2]) * t0
        z1 = pts[si][2] + (pts[si + 1][2] - pts[si][2]) * t1
        o.append(f'<line x1="{X(s0):.1f}" y1="{Y(z0):.1f}" x2="{X(s1):.1f}" y2="{Y(z1):.1f}" stroke="currentColor" stroke-width="10" stroke-dasharray="3 3" opacity=".85" stroke-linecap="round"/>')
    # segment labels
    for i, (a, b) in enumerate(c.segs()):
        L = M.dist(a, b)
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        if abs(dz) > 1e-6 and abs(dx) < 1e-6 and abs(dy) < 1e-6:
            word = "up" if dz > 0 else "down"
        elif abs(dz) < 1e-6:
            if abs(dx) >= abs(dy):
                word = "right →" if dx > 0 else "← left"
            else:
                word = "back ↑" if dy > 0 else "forward ↓"
        else:
            word = "rising" if dz > 0 else "falling"
        mx = (X(s_acc[i]) + X(s_acc[i + 1])) / 2
        my = (Y(a[2]) + Y(b[2])) / 2
        short = L < 4.0
        if abs(dz) > 1e-6 and abs(dx) < 1e-6 and abs(dy) < 1e-6:
            o.append(text(mx + 8, my + 4, f"{L:.0f} {word}", "s b"))
        elif short:
            o.append(text(mx, my + 16 if i % 2 else my - 9, f"{L:.0f} {word}", "s b", "middle"))
        else:
            o.append(text(mx, my - 9, f"{L:.0f} mm {word}", "s b", "middle"))
    # joints
    for p, s in ((pts[0], s_acc[0]), (pts[-1], s_acc[-1])):
        o.append(f'<circle cx="{X(s):.1f}" cy="{Y(p[2]):.1f}" r="6" class="joint"/>')
    o.append(text(px0, 22, title or f"{c.name}: side view unrolled along its path · total {c.length():.0f} mm, cut {c.length()+6:.0f}", "t b"))
    o.append(text(px1, h - 8, "heights in mm above the card · dotted = heat-shrink", "s muted", "end"))
    return svg_wrap("".join(o), w, h, title or c.name)


def bend_table(c: M.Cond):
    rows = []
    for i, (a, b) in enumerate(c.segs()):
        L = M.dist(a, b)
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        parts = []
        if abs(dx) > 1e-6:
            parts.append(f"{'right' if dx > 0 else 'left'} {abs(dx):.1f}")
        if abs(dy) > 1e-6:
            parts.append(f"{'back' if dy > 0 else 'forward'} {abs(dy):.1f}")
        if abs(dz) > 1e-6:
            parts.append(f"{'up' if dz > 0 else 'down'} {abs(dz):.1f}")
        rows.append((i + 1, f"{L:.1f}", ", ".join(parts), f"{b[2]:g}"))
    return rows


# ---------------------------------------------------------------- elevations
def front_elevation(w=760, h=300, title="Front view: every rod projected onto the front, heights to scale"):
    """X–Z projection of boards, rods and the screen."""
    sx = (w - 170) / M.INSIDE_X
    sz = 11.0
    X = lambda x: 45 + x * sx
    Z = lambda z: h - 40 - z * sz
    o = []
    o.append(f'<line x1="{X(0)}" y1="{Z(0):.1f}" x2="{X(M.INSIDE_X)}" y2="{Z(0):.1f}" class="floor"/>')
    for name, b, cls in (("A1", M.A1, "pcb"), ("amp", M.AMP, "pcb"), ("mic", M.MIC, "pcb"), ("speaker", M.SPK, "spk"), ("USB", M.USB, "box"),
                         ("block", M.AMP_BLOCK, "box"), ("button", M.BTN, "box"), ("220 µF", M.CAP220, "cap"), ("screen", M.SCREEN, "screen-side")):
        o.append(f'<rect x="{X(b["x0"]):.1f}" y="{Z(b["z1"]):.1f}" width="{(b["x1"]-b["x0"])*sx:.1f}" height="{(b["z1"]-b["z0"])*sz:.1f}" class="{cls}" rx="1.5"/>')
        if name in ("A1", "amp", "mic", "speaker", "screen", "220 µF", "block"):
            o.append(text(X((b["x0"] + b["x1"]) / 2), Z(b["z1"]) - 4, name, "s muted", "middle"))
    o.append(f'<rect x="{X(M.SCREEN["x0"]):.1f}" y="{Z(20.5):.1f}" width="{(M.SCREEN["x1"]-M.SCREEN["x0"])*sx:.1f}" height="{1.8*sz:.1f}" class="glass" rx="1.5"/>')
    for c in M.rods():
        pts = " ".join(f"{X(p[0]):.1f},{Z(p[2]):.1f}" for p in c.pts)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{NET_COLOR.get(c.net, "var(--brass)")}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>')
    for z, name in ((0.5, "rails on the card"), (5.0, "stub level, 5"), (8.0, "8"), (10.5, "10.5"), (12.5, "12.5"), (17.5, "screen 17.5")):
        o.append(f'<line x1="{X(0)-8}" y1="{Z(z):.1f}" x2="{X(M.INSIDE_X)+8}" y2="{Z(z):.1f}" class="grid dashed"/>')
        o.append(text(X(M.INSIDE_X) + 12, Z(z) + 4, name, "s muted"))
    o.append(f'<line x1="{X(0)-8}" y1="{Z(M.FRAME_H_MIN):.1f}" x2="{X(M.INSIDE_X)+8}" y2="{Z(M.FRAME_H_MIN):.1f}" class="warn-line" stroke-width="1.6"/>')
    o.append(text(X(M.INSIDE_X) + 12, Z(M.FRAME_H_MIN) + 4, f"needs ≥ {M.FRAME_H_MIN:g} inside", "s warn-ink"))
    o.append(text(45, 22, title, "t b"))
    return svg_wrap("".join(o), w, h, title)


def side_elevation(w=760, h=290, title="Right side view: the channel from front (left) to back (right)"):
    """Y–Z projection."""
    sy = (w - 190) / M.INSIDE_Y
    sz = 11.0
    Yp = lambda y: 45 + y * sy
    Z = lambda z: h - 40 - z * sz
    o = []
    o.append(f'<line x1="{Yp(0)}" y1="{Z(0):.1f}" x2="{Yp(M.INSIDE_Y)}" y2="{Z(0):.1f}" class="floor"/>')
    for name, b, cls in (("A1", M.A1, "pcb"), ("amp", M.AMP, "pcb"), ("mic", M.MIC, "pcb"), ("speaker", M.SPK, "spk"), ("USB", M.USB, "box"),
                         ("block", M.AMP_BLOCK, "box"), ("button", M.BTN, "box"), ("220 µF", M.CAP220, "cap"), ("screen", M.SCREEN, "screen-side")):
        o.append(f'<rect x="{Yp(b["y0"]):.1f}" y="{Z(b["z1"]):.1f}" width="{(b["y1"]-b["y0"])*sy:.1f}" height="{(b["z1"]-b["z0"])*sz:.1f}" class="{cls}" rx="1.5"/>')
        if name in ("A1", "amp", "mic", "speaker", "screen"):
            o.append(text(Yp((b["y0"] + b["y1"]) / 2), Z(b["z1"]) - 4, name, "s muted", "middle"))
    o.append(f'<rect x="{Yp(M.SCREEN["y0"]):.1f}" y="{Z(20.5):.1f}" width="{(M.SCREEN["y1"]-M.SCREEN["y0"])*sy:.1f}" height="{1.8*sz:.1f}" class="glass" rx="1.5"/>')
    for c in M.rods():
        pts = " ".join(f"{Yp(p[1]):.1f},{Z(p[2]):.1f}" for p in c.pts)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{NET_COLOR.get(c.net, "var(--brass)")}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>')
    for z, name in ((0.5, "rails"), (5.0, "5"), (8.0, "8"), (10.5, "10.5"), (12.5, "12.5"), (17.5, "screen")):
        o.append(f'<line x1="{Yp(0)-8}" y1="{Z(z):.1f}" x2="{Yp(M.INSIDE_Y)+8}" y2="{Z(z):.1f}" class="grid dashed"/>')
        o.append(text(Yp(M.INSIDE_Y) + 12, Z(z) + 4, name, "s muted"))
    o.append(text(Yp(0), Z(0) + 16, "front", "s muted"))
    o.append(text(Yp(M.INSIDE_Y), Z(0) + 16, "back", "s muted", "end"))
    o.append(text(45, 22, title, "t b"))
    return svg_wrap("".join(o), w, h, title)


# ---------------------------------------------------------------- floor template (1:1)
def floor_template_svg(px_per_mm):
    """The 57 × 39 floor with every part outline, pin dot and rail line, for printing at 1:1."""
    s = px_per_mm
    W = int(110 * s); H = int(68 * s)
    ox, oy = 10 * s, 10 * s
    X = lambda x: ox + x * s
    Y = lambda y: oy + (M.INSIDE_Y - y) * s
    o = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>']
    o.append(f'<rect x="{X(0)}" y="{Y(M.INSIDE_Y)}" width="{M.INSIDE_X*s}" height="{M.INSIDE_Y*s}" fill="none" stroke="black" stroke-width="{0.5*s}"/>')
    def box(b, dash=None, lab=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o.append(f'<rect x="{X(b["x0"])}" y="{Y(b["y1"])}" width="{(b["x1"]-b["x0"])*s}" height="{(b["y1"]-b["y0"])*s}" fill="none" stroke="black" stroke-width="{0.25*s}"{d}/>')
        if lab:
            o.append(f'<text x="{X((b["x0"]+b["x1"])/2)}" y="{Y((b["y0"]+b["y1"])/2)+0.8*s}" font-size="{2.2*s}" font-family="sans-serif" text-anchor="middle">{esc(lab)}</text>')
    box(M.A1, lab="A1"); box(M.USB, "2 2"); box(M.AMP, lab="amp")
    o.append(f'<circle cx="{X(M.MIC_C[0])}" cy="{Y(M.MIC_C[1])}" r="{M.MIC_D/2*s}" fill="none" stroke="black" stroke-width="{0.25*s}"/>')
    o.append(f'<text x="{X(M.MIC_C[0])}" y="{Y(M.MIC_C[1]+4.6)}" font-size="{2.2*s}" font-family="sans-serif" text-anchor="middle">mic</text>')
    box(M.SPK, "3 2", "speaker"); box(M.CAP220, "2 2"); box(M.BTN, "1 1")
    o.append(f'<text x="{X((M.CAP220["x0"]+M.CAP220["x1"])/2)}" y="{Y((M.CAP220["y0"]+M.CAP220["y1"])/2)}" font-size="{2.2*s}" font-family="sans-serif" text-anchor="middle" transform="rotate(-90 {X((M.CAP220["x0"]+M.CAP220["x1"])/2)},{Y((M.CAP220["y0"]+M.CAP220["y1"])/2)})">220 µF</text>')
    box(M.SCREEN, "4 3")
    for st in M.stubs():
        p = st.pts[0]
        o.append(f'<circle cx="{X(p[0])}" cy="{Y(p[1])}" r="{0.45*s}" fill="black"/>')
    for i, c in enumerate(M.rods()[:2]):
        a, b = c.pts[0], c.pts[-1]
        o.append(f'<line x1="{X(a[0])}" y1="{Y(a[1])}" x2="{X(b[0])}" y2="{Y(b[1])}" stroke="black" stroke-width="{1.0*s}" stroke-linecap="round" opacity=".55"/>')
        if i == 0:
            o.append(f'<text x="{X(b[0])-1.5*s}" y="{Y(b[1])-1.0*s}" font-size="{2.0*s}" font-family="sans-serif" text-anchor="end">3V3</text>')
        else:
            o.append(f'<text x="{X(b[0])+1.5*s}" y="{Y(b[1])-1.0*s}" font-size="{2.0*s}" font-family="sans-serif" text-anchor="start">GND</text>')
    # crosshair marks for the two straight-rod rows
    for y in M.A1_PIN_Y[:7]:
        o.append(f'<line x1="{X(M.A1_RIGHT_X)}" y1="{Y(y)}" x2="{X(M.AMP_PIN_X)}" y2="{Y(y)}" stroke="black" stroke-width="{0.15*s}" stroke-dasharray="1 1"/>')
    # scale bar
    o.append(f'<line x1="{X(0)}" y1="{Y(-6)}" x2="{X(50)}" y2="{Y(-6)}" stroke="black" stroke-width="{0.6*s}"/>')
    for i in range(0, 51, 10):
        o.append(f'<line x1="{X(i)}" y1="{Y(-6)-1.5*s}" x2="{X(i)}" y2="{Y(-6)+1.5*s}" stroke="black" stroke-width="{0.3*s}"/>')
    o.append(f'<text x="{X(25)}" y="{Y(-6)+5*s}" font-size="{3*s}" font-family="sans-serif" text-anchor="middle">50 mm check — print at Actual size, Letter, black</text>')
    o.append(f'<text x="{X(0)}" y="{Y(M.INSIDE_Y)-4*s}" font-size="{3.0*s}" font-family="sans-serif">Pip brass harness · floor card 57 × 39 mm · front edge at the bottom</text>')
    o.append(f'<text x="{X(0)}" y="{Y(-15)}" font-size="{2.6*s}" font-family="sans-serif">dots = 2 mm stubs · grey lines = the two rails · dotted = parts that sit higher or carry no stubs</text>')
    o.append(f'<text x="{X(0)}" y="{Y(-19)}" font-size="{2.6*s}" font-family="sans-serif">A1: USB at the bottom edge · amp: pins on its left edge, VIN at the front</text>')
    o.append(f'<text x="{X(0)}" y="{Y(-23)}" font-size="{2.6*s}" font-family="sans-serif">mic: chip side down, hole up, the SD-VDD-GND column on the left</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W/s:.0f}mm" height="{H/s:.0f}mm" viewBox="0 0 {W} {H}">{"".join(o)}</svg>'


# ---------------------------------------------------------------- where the Kapton goes
def kapton_figure():
    """Top view with every piece of Kapton drawn in place and numbered."""
    o = [frame_top(), parts_top(labels=False), screen_outline()]
    o.append("".join(poly_top(c, width=5, opacity=.5) for c in M.rods()[:2]))
    def kap(x0, x1, y0, y1, n, lab, rx=2):
        b = dict(x0=x0, x1=x1, y0=y0, y1=y1)
        return (rect(b, "kap", rx) + f'<circle cx="{tx(x0)+9:.1f}" cy="{ty(y1)+9:.1f}" r="8" class="num"/>'
                + text(tx(x0) + 9, ty(y1) + 12.5, str(n), "s b numt", "middle") + (label_at((x0 + x1) / 2, (y0 + y1) / 2, lab, "s b warn-ink", "middle", 4) if lab else ""))
    # 1 USB socket, two layers
    o.append(kap(M.USB["x0"] - 0.3, M.USB["x1"] + 0.3, M.USB["y0"], M.USB["y1"] + 0.3, 1, "2 layers"))
    # 2 amp strip between the stubs and the chip
    o.append(kap(31.2, 41.5, M.AMP["y0"] + 0.3, 13.3, 2, "strip"))
    # 3 mic pad
    o.append(f'<circle cx="{tx(M.MIC_C[0]):.1f}" cy="{ty(M.MIC_C[1]):.1f}" r="{(M.MIC_D/2+0.8)*S:.1f}" class="kap"/>')
    o.append(f'<circle cx="{tx(M.MIC_C[0]-6.5)+9:.1f}" cy="{ty(M.MIC_C[1]+6.5)+9:.1f}" r="8" class="num"/>' + text(tx(M.MIC_C[0]-6.5)+9, ty(M.MIC_C[1]+6.5)+12.5, "3", "s b numt", "middle"))
    o.append(label_at(M.MIC_C[0], M.MIC_C[1] - 2.2, "pad", "s b warn-ink", "middle", 4))
    # 4 220 uF pad
    o.append(kap(M.CAP220["x0"] - 0.5, M.CAP220["x1"] + 0.2, M.CAP220["y0"] - 0.8, M.CAP220["y1"] + 0.8, 4, "pad"))
    # 5 rail loops, three per rail
    for y in (4.0, 12.5, 21.0):
        for x in (24.0, 27.0):
            o.append(rect(dict(x0=x - 1.2, x1=x + 1.2, y0=y - 1.0, y1=y + 1.0), "kap", 1))
    o.append(f'<circle cx="{tx(25.5):.1f}" cy="{ty(12.5):.1f}" r="8" class="num"/>' + text(tx(25.5), ty(12.5) + 3.5, "5", "s b numt", "middle"))
    # 6 holding loops on the modules: two corners of A1 and the amp
    for (x, y) in ((M.A1["x0"] + 1.5, M.A1["y1"] - 1.5), (M.A1["x1"] - 1.5, M.A1["y0"] + 11), (M.AMP["x1"] - 1.5, M.AMP["y1"] - 1.5), (M.AMP["x0"] + 8, M.AMP["y1"] - 1.0)):
        o.append(rect(dict(x0=x - 1.5, x1=x + 1.5, y0=y - 1.5, y1=y + 1.5), "kap", 1))
    o.append(f'<circle cx="{tx(M.A1["x0"]+1.5)-9:.1f}" cy="{ty(M.A1["y1"]-1.5)-9:.1f}" r="8" class="num"/>' + text(tx(M.A1["x0"]+1.5)-9, ty(M.A1["y1"]-1.5)-5.5, "6", "s b numt", "middle"))
    # 7 the scrap over the mic hole
    o.append(f'<circle cx="{tx(M.MIC_PORT[0]):.1f}" cy="{ty(M.MIC_PORT[1]):.1f}" r="{1.6*S:.1f}" class="kap2"/>')
    o.append(f'<circle cx="{tx(M.MIC_PORT[0])+16:.1f}" cy="{ty(M.MIC_PORT[1])-14:.1f}" r="8" class="num"/>' + text(tx(M.MIC_PORT[0])+16, ty(M.MIC_PORT[1])-10.5, "7", "s b numt", "middle"))
    # A1 shim (cardstock, not Kapton)
    o.append(rect(dict(x0=M.A1["x0"]-0.4, x1=M.A1["x1"]+0.4, y0=M.A1["y0"]-0.4, y1=M.A1["y1"]+0.4), "shim", 3))
    o.append(label_at(12.5, 11.0, "A1 sits on one layer", "s muted", "middle", 4))
    o.append(label_at(12.5, 9.6, "of cardstock, not Kapton", "s muted", "middle", 4))
    o.append(label_at(12.5, 22.4, "antenna: nothing on it", "s warn-ink", "middle", 4))
    o.append(text(OX, 22, "Where the Kapton goes, top view · numbers match the list", "t b"))
    o.append(text(tx(0), ty(0) + 18, "front of the device (USB) · 10 px = 1 mm · amber = Kapton · the frame's inner faces get it too, later", "s muted"))
    return svg_wrap("".join(o), 760, int(OY + M.INSIDE_Y * S + 40), "Where the Kapton goes")


# ---------------------------------------------------------------- what touches the frame
def attachment_figure(w=760, h=345):
    """Left: cross-section from the front. Right: the card in the frame from above. Glue dots marked."""
    o = []
    # ---- left panel: front cross-section
    sx = 5.2; sz = 7.0
    X = lambda x: 30 + x * sx
    Z = lambda z: 300 - z * sz
    o.append(text(30, 24, "Front cross-section: what sits on what", "t b"))
    # bottom loop tube (under the card), top loop tube at 32 mm
    for zc, lab in ((-1.05, "bottom loop"), (32.0 + 0.75, "top loop")):
        o.append(f'<rect x="{X(-1.5):.1f}" y="{Z(zc + 0.75):.1f}" width="{(M.INSIDE_X + 3) * sx:.1f}" height="{1.5 * sz:.1f}" class="tube"/>')
        o.append(text(X(M.INSIDE_X + 2), Z(zc) + (12 if zc < 0 else 4), lab, "s brass-ink"))
    # posts
    for x in (-0.5, M.INSIDE_X + 0.5):
        o.append(f'<rect x="{X(x) - 2.5:.1f}" y="{Z(32):.1f}" width="5" height="{32 * sz:.1f}" class="tube"/>')
    # kapton on the tubes
    o.append(f'<rect x="{X(0):.1f}" y="{Z(0.0) - 2:.1f}" width="{M.INSIDE_X * sx:.1f}" height="2" class="kap2"/>')
    # the card on the bottom tube
    o.append(f'<rect x="{X(0.25):.1f}" y="{Z(0.3):.1f}" width="{(M.INSIDE_X - 0.5) * sx:.1f}" height="{0.3 * sz:.1f}" class="card"/>')
    o.append(text(X(M.INSIDE_X + 2), Z(1.2) + 4, "floor card", "s muted"))
    # parts on the card
    for name, b, cls in (("A1", M.A1, "pcb"), ("amp", M.AMP, "pcb"), ("220 µF", M.CAP220, "cap"), ("block", M.AMP_BLOCK, "box")):
        o.append(f'<rect x="{X(b["x0"]):.1f}" y="{Z(b["z1"]):.1f}" width="{(b["x1"] - b["x0"]) * sx:.1f}" height="{(b["z1"] - b["z0"]) * sz:.1f}" class="{cls}" rx="1.5"/>')
        o.append(text(X((b["x0"] + b["x1"]) / 2), Z(b["z1"]) - 4, name, "s muted", "middle"))
    # screen on rods
    b = M.SCREEN
    o.append(f'<rect x="{X(b["x0"]):.1f}" y="{Z(b["z1"]):.1f}" width="{(b["x1"] - b["x0"]) * sx:.1f}" height="{(b["z1"] - b["z0"]) * sz:.1f}" class="screen-side" rx="1.5"/>')
    o.append(f'<rect x="{X(b["x0"]):.1f}" y="{Z(b["z1"] + 1.8):.1f}" width="{(b["x1"] - b["x0"]) * sx:.1f}" height="{1.8 * sz:.1f}" class="glass" rx="1.5"/>')
    o.append(text(X((b["x0"] + b["x1"]) / 2), Z(b["z1"] + 1.8) - 4, "screen, on its four rods, 17.5 up", "s muted", "middle"))
    for x in M.SCREEN_PIN_X:
        o.append(f'<line x1="{X(x):.1f}" y1="{Z(b["z0"]):.1f}" x2="{X(x):.1f}" y2="{Z(5.0):.1f}" class="rod" stroke-width="2.5"/>')
    # glue dots: card corners to the tube, screen to the block, cap to its pad
    for x in (1.5, M.INSIDE_X - 1.5):
        o.append(f'<circle cx="{X(x):.1f}" cy="{Z(0.0):.1f}" r="5" class="glue"/>')
    o.append(f'<circle cx="{X(46):.1f}" cy="{Z(M.SCREEN["z0"] - 0.3):.1f}" r="5" class="glue"/>')
    o.append(f'<circle cx="{X(53.6):.1f}" cy="{Z(0.2):.1f}" r="5" class="glue"/>')
    o.append(text(X(10), Z(0) + 16, "glue: card to the bottom tube, four corners", "s pass-ink"))
    o.append(text(X(47.5), Z(M.SCREEN["z0"] - 0.3) + 4, "glue: screen to the block", "s pass-ink"))
    o.append(text(X(42), Z(0) + 30, "glue: capacitor to its pad", "s pass-ink"))
    o.append(text(X(-1), Z(20), "air: nothing", "s warn-ink"))
    o.append(text(X(-1), Z(18.5), "touches the posts", "s warn-ink"))
    # ---- right panel: top view of the frame with the card, mini
    ox, oy, k = 540, 60, 3.2
    TX = lambda x: ox + x * k; TY = lambda y: oy + (M.INSIDE_Y - y) * k
    o.append(text(ox, 24, "From above", "t b"))
    o.append(f'<rect x="{TX(0) - 4:.1f}" y="{TY(M.INSIDE_Y) - 4:.1f}" width="{M.INSIDE_X * k + 8:.1f}" height="{M.INSIDE_Y * k + 8:.1f}" class="frame" rx="3"/>')
    o.append(f'<rect x="{TX(0.25):.1f}" y="{TY(M.INSIDE_Y - 0.25):.1f}" width="{(M.INSIDE_X - 0.5) * k:.1f}" height="{(M.INSIDE_Y - 0.5) * k:.1f}" class="card"/>')
    for nm, b in (("A1", M.A1), ("amp", M.AMP), ("spk", M.SPK), ("C1", M.CAP220)):
        o.append(f'<rect x="{TX(b["x0"]):.1f}" y="{TY(b["y1"]):.1f}" width="{(b["x1"] - b["x0"]) * k:.1f}" height="{(b["y1"] - b["y0"]) * k:.1f}" class="pcb" rx="1"/>')
        o.append(text(TX((b["x0"] + b["x1"]) / 2), TY((b["y0"] + b["y1"]) / 2) + 3, nm, "s muted", "middle"))
    o.append(f'<circle cx="{TX(M.MIC_C[0]):.1f}" cy="{TY(M.MIC_C[1]):.1f}" r="{M.MIC_D / 2 * k:.1f}" class="pcb"/>')
    o.append(f'<rect x="{TX(M.SCREEN["x0"]):.1f}" y="{TY(M.SCREEN["y1"]):.1f}" width="{(M.SCREEN["x1"] - M.SCREEN["x0"]) * k:.1f}" height="{(M.SCREEN["y1"] - M.SCREEN["y0"]) * k:.1f}" class="screen-out" rx="2"/>')
    for (x, y) in ((1.5, 1.5), (M.INSIDE_X - 1.5, 1.5), (1.5, M.INSIDE_Y - 1.5), (M.INSIDE_X - 1.5, M.INSIDE_Y - 1.5)):
        o.append(f'<circle cx="{TX(x):.1f}" cy="{TY(y):.1f}" r="4" class="glue"/>')
    o.append(f'<circle cx="{TX(46):.1f}" cy="{TY(12.2):.1f}" r="4" class="glue"/>')
    o.append(f'<circle cx="{TX(53.6):.1f}" cy="{TY(9):.1f}" r="4" class="glue"/>')
    o.append(text(ox, TY(0) + 22, "six dots of glue in all;", "s pass-ink"))
    o.append(text(ox, TY(0) + 36, "none near the mic hole,", "s muted"))
    o.append(text(ox, TY(0) + 50, "the USB port or the button", "s muted"))
    return svg_wrap("".join(o), w, h, "What holds the harness in the frame")


def kapton_min_figure():
    """Top view with only the two pieces of Kapton that matter."""
    o = [frame_top(), parts_top(labels=False), screen_outline()]
    o.append("".join(poly_top(c, width=5, opacity=.5) for c in M.rods()[:2]))
    def kap(x0, x1, y0, y1, n, lab):
        b = dict(x0=x0, x1=x1, y0=y0, y1=y1)
        return (rect(b, "kap", 2) + f'<circle cx="{tx(x0)+9:.1f}" cy="{ty(y1)+9:.1f}" r="8" class="num"/>'
                + text(tx(x0) + 9, ty(y1) + 12.5, str(n), "s b numt", "middle") + label_at((x0 + x1) / 2, (y0 + y1) / 2, lab, "s b warn-ink", "middle", 4))
    o.append(kap(M.USB["x0"] - 0.3, M.USB["x1"] + 0.3, M.USB["y0"], M.USB["y1"] + 0.3, 1, "2 layers"))
    o.append(kap(31.2, 41.5, M.AMP["y0"] + 0.3, 13.3, 2, "1 strip"))
    o.append(text(tx(M.USB["x1"]) + 6, ty(M.USB["y1"]) - 6, "1 · the roof of the USB socket, 9 × 8 mm, two layers", "s b warn-ink"))
    o.append(text(tx(31.2), ty(13.3) - 6, "2 · on the amp between stubs and chip, 10 × 9 mm", "s b warn-ink"))
    o.append(text(OX, 22, "The two pieces of Kapton, to scale", "t b"))
    o.append(text(tx(0), ty(0) + 18, "front of the device (USB) at the bottom · 10 px = 1 mm · amber = tape · nothing on any stub, nothing on the antenna end", "s muted"))
    return svg_wrap("".join(o), 760, int(OY + M.INSIDE_Y * S + 40), "The two pieces of Kapton")


def amp_level_figure(w=760, h=330):
    """Front view of the amp on the card: header strip under the pin edge, a 2.5 mm shim under the far edge, tape over the top."""
    sx = 24.0; sz = 16.0
    X = lambda x: 215 + x * sx     # x in mm from the amp's pin edge
    Z = lambda z: 250 - z * sz
    STRIP = M.STRIP
    o = [text(30, 24, "The amp on the card, seen from the front: the strip on one edge, a shim on the other", "t b")]
    o.append(f'<rect x="{X(-6):.1f}" y="{Z(0):.1f}" width="{26 * sx:.1f}" height="{0.4 * sz:.1f}" class="card"/>')
    o.append(text(X(-6), Z(0) + 20, "floor card", "s muted"))
    # the black header strip under the pin edge, the pin clipped flush with its underside
    o.append(f'<rect x="{X(-0.2):.1f}" y="{Z(STRIP):.1f}" width="{2.54 * sx:.1f}" height="{STRIP * sz:.1f}" class="box"/>')
    o.append(f'<rect x="{X(0.4):.1f}" y="{Z(STRIP):.1f}" width="{0.64 * sx:.1f}" height="{STRIP * sz:.1f}" class="stubp"/>')
    o.append(text(X(1.1), Z(0) + 42, "header strip, 2.5 mm; the pin clipped flush with its underside", "s", "middle"))
    # the shim under the far edge: tube offcut + three layers of cardstock
    o.append(f'<rect x="{X(12.5):.1f}" y="{Z(STRIP):.1f}" width="{4.5 * sx:.1f}" height="{1.5 * sz:.1f}" class="tube"/>')
    o.append(f'<rect x="{X(12.5):.1f}" y="{Z(STRIP - 1.5):.1f}" width="{4.5 * sx:.1f}" height="{1.0 * sz:.1f}" class="card"/>')
    o.append(text(X(14.75), Z(0) + 42, "shim under the far edge, 2.5 mm:", "s", "middle"))
    o.append(text(X(14.75), Z(0) + 56, "a flat K&S tube offcut (1.5) + three layers of cardstock (1.0), taped", "s", "middle"))
    # board
    zb = STRIP
    o.append(f'<rect x="{X(0):.1f}" y="{Z(zb + 1.6):.1f}" width="{17 * sx:.1f}" height="{1.6 * sz:.1f}" class="pcb"/>')
    o.append(text(X(8.5), Z(zb + 0.8) + 4, "amp board, level, 2.5 mm up", "s muted", "middle"))
    # top stub with solder, the rod against it
    o.append(f'<rect x="{X(0.4):.1f}" y="{Z(zb + 1.6 + 1.4):.1f}" width="{0.64 * sx:.1f}" height="{1.4 * sz:.1f}" class="stubp"/>')
    o.append(f'<ellipse cx="{X(0.72):.1f}" cy="{Z(zb + 1.6):.1f}" rx="{1.0 * sx:.1f}" ry="{0.4 * sz:.1f}" class="solder"/>')
    o.append(f'<circle cx="{X(-0.45):.1f}" cy="{Z(zb + 2.5):.1f}" r="{0.5 * sx:.1f}" class="rodx"/>')
    o.append(text(X(-6), Z(zb + 5.2), "a channel rod lies", "s brass-ink"))
    o.append(text(X(-6), Z(zb + 4.4), "against the stub,", "s brass-ink"))
    o.append(text(X(-6), Z(zb + 3.6), "5 mm up", "s brass-ink"))
    o.append(text(X(1.8), Z(zb + 1.6 + 3.6), "the stub: the pin's short end, 1.5 mm, in its solder", "s b"))
    # chip and a short terminal block
    o.append(f'<rect x="{X(6):.1f}" y="{Z(zb + 1.6 + 1.0):.1f}" width="{4 * sx:.1f}" height="{1.0 * sz:.1f}" class="box"/>')
    o.append(text(X(8), Z(zb + 1.6 + 1.0) - 6, "chip", "s muted", "middle"))
    o.append(f'<rect x="{X(12):.1f}" y="{Z(zb + 1.6 + 5.0):.1f}" width="{5 * sx:.1f}" height="{5.0 * sz:.1f}" class="box"/>')
    o.append(text(X(14.5), Z(zb + 1.6 + 2.5) + 4, "terminal", "s muted", "middle"))
    o.append(text(X(14.5), Z(zb + 1.6 + 2.5) + 17, "block", "s muted", "middle"))
    # tape loops over the board edges
    o.append(f'<path d="M{X(-1.2):.1f},{Z(0):.1f} L{X(-1.2):.1f},{Z(zb + 1.9):.1f} L{X(2.5):.1f},{Z(zb + 1.9):.1f}" class="tapeline"/>')
    o.append(f'<path d="M{X(18.2):.1f},{Z(0):.1f} L{X(18.2):.1f},{Z(zb + 1.9):.1f} L{X(11.5):.1f},{Z(zb + 1.9):.1f}" class="tapeline"/>')
    o.append(text(X(4), Z(zb + 1.6 + 5.6), "tape goes over the board and down onto the card on both sides, never under it", "s warn-ink"))
    return svg_wrap("".join(o), w, h, "Levelling the amp")
