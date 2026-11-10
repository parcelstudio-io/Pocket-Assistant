"""Builds docs/pages/following.html and docs/following.md: can the XS drone follow a person indoors,
in real time, with everything processed locally, and what does it look like without the forward ranger?

Geometry from docs/custom-build.md (2026-10-28, jig corrections 2026-11-06); the camera-only nose moves the
flashlight to the centre line and leaves the forward ranger off. Every coordinate is in millimetres, drone
frame: x right, y forward (nose), z up; the rails are z = 0. Run: python3 docs/pages/gen/follow_page.py
"""
import math, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
DOCS = PAGES.parent
HTML_OUT = PAGES / "following.html"
MD_OUT = DOCS / "following.md"
BUILD_PAGE = "https://claude.ai/artifact/34eHTqKHJ2gfCkfK2Yb4up"
FOLLOW_PAGE = "https://claude.ai/artifact/LYYQRGev8wnFg92FFNJxxc"

# ---------------------------------------------------------------- the aircraft, in mm
RAIL_X, RAIL_Y = 7, 33            # two rails at x = ±7, y from -33 to +33
AXLE_X, AXLE_Y = 20, 30           # axles at y = ±30, x from -20 to +20; motors at the ends
NOSE_HALF, TAIL_HALF = 15.5, 7    # nose bar 31 mm at y = +33, tail bar 14 mm at y = -33
SKID = 5                          # skids 5 mm down at the axle ends
MOTOR_R, MOTOR_Z0, MOTOR_Z1 = 3.0, 1.0, 16.0
COLLAR_R, COLLAR_H = 4.5, 3.0     # two-turn 1.5 mm collar around the motor at the axle
PROP_R, PROP_Z = 15.5, 16.8
BAT = (-5.5, 5.5, -27, 27, 0.0, 5.8)          # x0 x1 y0 y1 z0 z1: the floor pan on the rails
CABIN = (-8.75, 8.75, -10.5, 10.5, 5.8, 20.8)  # XIAO + Sense on the pan
CAM = (-2.0, 2.0, 10.5, 13.5, 16.0, 20.0)      # camera on the cabin's front face
GY = (-8, 8, -10.5, 10.5, -2.0, 0.0)           # motion sensor under the pan, centre
VL1 = (-6.5, 6.5, -30, -12, -2.0, 0.0)         # down-looking ranger under the pan, tail
LAMP_X_CAMERA_ONLY, LAMP_X_APPROVED = 0.0, -9.0
RANGER_X = 9.0
STAR_R, STAR_Y, STAR_Z = 7.0, 33.0, 7.0        # 14 mm star disc, vertical, facing forward
LENS_R, LENS_LEN = 5.0, 7.0

MASS_WITH, MASS_WITHOUT = 37.5, 37.0   # with the speaker and amplifier added 2026-11-09 (33.7 / 33.2 before)
TW_WITH, TW_WITHOUT = 68 / MASS_WITH, 68 / MASS_WITHOUT

# ---------------------------------------------------------------- projection for the three-quarter view
S = 3.5                                   # px per mm, as on the build page
AZ, EL = math.radians(34), math.radians(27)
CX, CY = 430, 300


def P(x, y, z):
    """Orthographic view from the front right, above. Returns (u, v, depth); larger depth is nearer."""
    xr = x * math.cos(AZ) - y * math.sin(AZ)
    yr = x * math.sin(AZ) + y * math.cos(AZ)
    u = CX + S * xr
    v = CY - S * (z * math.cos(EL) - yr * math.sin(EL))
    return u, v, yr


def pts(seq):
    return " ".join(f"{u:.1f},{v:.1f}" for u, v, _ in seq)


def rod(a, b, w=2.2, cls="rod"):
    (u1, v1, d1), (u2, v2, d2) = P(*a), P(*b)
    return (d1 + d2) / 2, f'<line x1="{u1:.1f}" y1="{v1:.1f}" x2="{u2:.1f}" y2="{v2:.1f}" class="{cls}" stroke-width="{w}"/>'


def circle3d(cx, cy, cz, r, plane, n=40):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        if plane == "z":
            out.append(P(cx + r * math.cos(a), cy + r * math.sin(a), cz))
        else:  # vertical disc facing +y
            out.append(P(cx + r * math.cos(a), cy, cz + r * math.sin(a)))
    return out


def cylinder(cx, cy, r, z0, z1, fill, edge):
    """A vertical cylinder: side band plus the top disc. Depth from its centre."""
    _, _, d = P(cx, cy, (z0 + z1) / 2)
    top = circle3d(cx, cy, z1, r, "z")
    bot = circle3d(cx, cy, z0, r, "z")
    uc, vt, _ = P(cx, cy, z1)
    _, vb, _ = P(cx, cy, z0)
    rr = r * S
    side = (f'<rect x="{uc - rr:.1f}" y="{vt:.1f}" width="{2 * rr:.1f}" height="{vb - vt:.1f}" '
            f'fill="{fill}" fill-opacity="0.9" stroke="none"/>')
    # the lower half of the bottom ellipse closes the band
    lower = [p for p in bot if p[1] >= vb - 0.01]
    body = (f'<path d="M{uc - rr:.1f},{vt:.1f} L{uc - rr:.1f},{vb:.1f} '
            f'A{rr:.1f},{rr * math.sin(EL):.1f} 0 0 0 {uc + rr:.1f},{vb:.1f} L{uc + rr:.1f},{vt:.1f}" '
            f'fill="{fill}" fill-opacity="0.9" stroke="{edge}" stroke-width="1.1"/>')
    topd = f'<polygon points="{pts(top)}" fill="{fill}" stroke="{edge}" stroke-width="1.1" style="filter:brightness(1.06)"/>'
    return d, body + topd


def box(b, fill, edge):
    """Three visible faces of an axis-aligned box: top, front (+y) and right (+x)."""
    x0, x1, y0, y1, z0, z1 = b
    _, _, d = P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    top = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]
    front = [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)]
    right = [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)]
    f = (f'<polygon points="{pts(right)}" fill="{fill}" style="filter:brightness(0.72)" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>'
         f'<polygon points="{pts(front)}" fill="{fill}" style="filter:brightness(0.9)" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>'
         f'<polygon points="{pts(top)}" fill="{fill}" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>')
    return d, f


def prop(cx, cy):
    """Four narrow blades plus the faint disc, in the plane z = PROP_Z."""
    _, _, d = P(cx, cy, PROP_Z)
    disc = circle3d(cx, cy, PROP_Z, PROP_R, "z")
    out = [f'<polygon points="{pts(disc)}" class="disc"/>']
    for k in range(4):
        a = math.radians(45 + 90 * k)
        tip = (cx + PROP_R * 0.95 * math.cos(a), cy + PROP_R * 0.95 * math.sin(a))
        mid = (cx + PROP_R * 0.5 * math.cos(a), cy + PROP_R * 0.5 * math.sin(a))
        w = 3.2
        n = (-math.sin(a) * w, math.cos(a) * w)
        blade = [P(cx + 1.2 * math.cos(a), cy + 1.2 * math.sin(a), PROP_Z),
                 P(mid[0] + n[0], mid[1] + n[1], PROP_Z), P(*tip, PROP_Z), P(mid[0] - n[0], mid[1] - n[1], PROP_Z)]
        out.append(f'<polygon points="{pts(blade)}" class="blade"/>')
    hub = circle3d(cx, cy, PROP_Z + 0.5, 1.6, "z", 16)
    out.append(f'<polygon points="{pts(hub)}" class="blade"/>')
    return d + 40, "".join(out)  # props sit on top of everything at their motor


def lamp(lx):
    """The 14 mm star, vertical on the nose bar, with the 10 mm lens 7 mm proud."""
    _, _, d = P(lx, STAR_Y + 3, STAR_Z)
    star = circle3d(lx, STAR_Y, STAR_Z, STAR_R, "y")
    lens_back = circle3d(lx, STAR_Y + 1, STAR_Z, LENS_R, "y")
    lens_front = circle3d(lx, STAR_Y + 1 + LENS_LEN, STAR_Z, LENS_R, "y")
    # lens side: hull of the two discs along the extreme points
    i_top = max(range(len(lens_back)), key=lambda i: -lens_back[i][1])
    i_bot = min(range(len(lens_back)), key=lambda i: -lens_back[i][1])
    i_l = min(range(len(lens_back)), key=lambda i: lens_back[i][0])
    i_r = max(range(len(lens_back)), key=lambda i: lens_back[i][0])
    side = [lens_back[i_top], lens_front[i_top], lens_front[i_r], lens_front[i_bot], lens_back[i_bot], lens_back[i_r]]
    f = (f'<polygon points="{pts(star)}" fill="var(--metal-soft)" stroke="var(--metal)" stroke-width="1.1"/>'
         f'<polygon points="{pts(side)}" fill="var(--lens)" fill-opacity="0.9" stroke="var(--metal)" stroke-width="1"/>'
         f'<polygon points="{pts(lens_front)}" fill="var(--lamp-face)" stroke="var(--metal)" stroke-width="1.1"/>')
    return d + 5, f


def three_quarter(camera_only=True):
    items = []
    # frame
    for x in (-RAIL_X, RAIL_X):
        items.append(rod((x, -RAIL_Y, 0), (x, RAIL_Y, 0)))
    for y in (-AXLE_Y, AXLE_Y):
        items.append(rod((-AXLE_X, y, 0), (AXLE_X, y, 0)))
    items.append(rod((-NOSE_HALF, RAIL_Y, 0), (NOSE_HALF, RAIL_Y, 0)))
    items.append(rod((-TAIL_HALF, -RAIL_Y, 0), (TAIL_HALF, -RAIL_Y, 0)))
    for x in (-AXLE_X, AXLE_X):
        for y in (-AXLE_Y, AXLE_Y):
            items.append(rod((x, y, 0), (x, y, -SKID)))
            items.append(cylinder(x, y, COLLAR_R, -COLLAR_H / 2, COLLAR_H / 2, "var(--metal-soft)", "var(--metal)"))
            items.append(cylinder(x, y, MOTOR_R, MOTOR_Z0, MOTOR_Z1, "var(--metal-soft)", "var(--metal)"))
            items.append(prop(x, y))
    items.append(box(GY, "var(--board)", "var(--board-edge)"))
    items.append(box(VL1, "var(--board)", "var(--board-edge)"))
    items.append(box(BAT, "var(--skin)", "var(--skin-edge)"))
    items.append(box(CABIN, "var(--matte)", "var(--matte-edge)"))
    items.append(box(CAM, "var(--matte)", "var(--matte-edge)"))
    items.append(lamp(LAMP_X_CAMERA_ONLY if camera_only else LAMP_X_APPROVED))
    if not camera_only:
        items.append(box((RANGER_X - 9, RANGER_X + 9, 33, 36, 0.5, 13.5), "var(--board)", "var(--board-edge)"))
    items.sort(key=lambda t: t[0])
    body = "\n".join(f for _, f in items)
    # leader labels
    L = []

    def label(p3, tx, ty, text, anchor="start"):
        u, v, _ = P(*p3)
        L.append(f'<line x1="{u:.1f}" y1="{v:.1f}" x2="{tx}" y2="{ty}" class="lead"/><circle cx="{u:.1f}" cy="{v:.1f}" r="2.2" class="dot"/>'
                 f'<text x="{tx + (6 if anchor == "start" else -6)}" y="{ty + 4}" class="t" text-anchor="{anchor}">{text}</text>')

    label((LAMP_X_CAMERA_ONLY if camera_only else LAMP_X_APPROVED, STAR_Y + 8, STAR_Z), 612, 470,
          "flashlight centred: the one headlight" if camera_only else "flashlight, left headlight")
    label((2, 13.5, 18), 612, 150, "camera on the cabin, 10° down")
    label((8.75, 0, 20.8), 612, 95, "XIAO Sense: flight controller, camera, Wi-Fi")
    label((5.5, 20, 5.8), 612, 230, "250 mAh pack: the floor pan")
    label((AXLE_X, AXLE_Y, MOTOR_Z1), 250, 95, "615 motor, 1.5 mm collar, 31 mm prop", "end")
    label((-6.5, -20, -2), 250, 420, "down ranger under the pan: height hold", "end")
    label((-8, 0, -2), 250, 470, "motion sensor under the pan", "end")
    label((-AXLE_X, -AXLE_Y, -SKID), 250, 520, "5 mm skids; 1.0 mm stainless ladder", "end")
    if camera_only:
        label((RANGER_X, 34, 7), 612, 400, "no forward ranger; its hood slot stays free")
    else:
        label((RANGER_X, 36, 7), 612, 400, "forward ranger, right headlight")
    title = ("The camera-only nose: no forward ranger, flashlight centred. From the front right, props fitted, 3.5 px per mm."
             if camera_only else "As approved: flashlight left, forward ranger right.")
    return f'''<svg viewBox="0 0 900 560" role="img" aria-label="Three-quarter view of the drone without the forward ranger: ladder frame, four motors with props, white battery pan, black controller cabin with the camera, one centred headlight">
<style>
.rod{{stroke:var(--metal);stroke-linecap:round;fill:none}}
.disc{{fill:var(--metal-soft);fill-opacity:0.12;stroke:var(--ink-2);stroke-width:1;stroke-dasharray:4 4}}
.blade{{fill:var(--prop);fill-opacity:0.88;stroke:var(--matte-edge);stroke-width:0.8}}
.lead{{stroke:var(--ink-2);stroke-width:1}} .dot{{fill:var(--ink-2)}}
.t{{font-size:12px;fill:var(--ink)}} .h{{font-size:14px;font-weight:700;fill:var(--ink)}}
</style>
<text x="20" y="28" class="h">{title}</text>
{body}
{"".join(L)}
</svg>'''


# ---------------------------------------------------------------- plan views, 3 px per mm
def plan_views():
    s = 3.0
    ox, oy = 230, 240          # top view origin, nose up: drone y up = page y down negative
    def T(x, y):
        return ox + s * x, oy - s * y
    sx, sz0 = 650, 408         # side view: x = drone y (nose left), rails at page y 408
    def Sd(y, z):
        return sx - s * y, sz0 - s * z
    out = ['<svg viewBox="0 0 900 470" role="img" aria-label="Top view and side view of the camera-only drone: flashlight on the centre line, no forward ranger">',
           '<style>.rod{fill:none;stroke:var(--metal);stroke-width:2.2;stroke-linecap:round}.rodh{fill:none;stroke:var(--matte-edge);stroke-width:3.4;stroke-linecap:round}'
           '.prop{fill:none;stroke:var(--ink-2);stroke-width:1;stroke-dasharray:4 4}.motor{fill:var(--metal-soft);stroke:var(--metal);stroke-width:1.6}'
           '.pan{fill:var(--skin);stroke:var(--skin-edge);stroke-width:1.4}.part{fill:var(--matte);stroke:var(--matte-edge);stroke-width:1.4}'
           '.under{fill:none;stroke:var(--ink);stroke-width:1.2;stroke-dasharray:3 3}.lamp{fill:var(--lamp-face);stroke:var(--metal);stroke-width:1.4}'
           '.ghost{fill:none;stroke:var(--ink-2);stroke-width:1;stroke-dasharray:2 3}'
           '.t{font-size:12px;fill:var(--ink)}.s{font-size:11px;fill:var(--ink-2)}.on{fill:var(--on-matte)}.h{font-size:14px;font-weight:700;fill:var(--ink)}.dim{fill:none;stroke:var(--ink-2);stroke-width:1}</style>',
           f'<text x="{ox}" y="26" class="h" text-anchor="middle">Top view, nose up</text>', '<g>']
    for x in (-AXLE_X, AXLE_X):
        for y in (-AXLE_Y, AXLE_Y):
            u, v = T(x, y); out.append(f'<circle cx="{u}" cy="{v}" r="{PROP_R * s}" class="prop"/>')
    for x in (-RAIL_X, RAIL_X):
        (u1, v1), (u2, v2) = T(x, RAIL_Y), T(x, -RAIL_Y); out.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" class="rod"/>')
    for y in (-AXLE_Y, AXLE_Y):
        (u1, v1), (u2, v2) = T(-AXLE_X, y), T(AXLE_X, y); out.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" class="rod"/>')
    (u1, v1), (u2, v2) = T(-NOSE_HALF, RAIL_Y), T(NOSE_HALF, RAIL_Y); out.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" class="rod"/>')
    (u1, v1), (u2, v2) = T(-TAIL_HALF, -RAIL_Y), T(TAIL_HALF, -RAIL_Y); out.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" class="rod"/>')
    for b, cls in ((GY, "under"), (VL1, "under"), (BAT, "pan"), (CABIN, "part"), (CAM, "part")):
        x0, x1, y0, y1 = b[:4]; u, v = T(x0, y1)
        out.append(f'<rect x="{u}" y="{v}" width="{(x1 - x0) * s}" height="{(y1 - y0) * s}" class="{cls}"/>')
    u, v = T(0, 0); out.append(f'<text x="{u}" y="{v - 4}" class="s on" text-anchor="middle">XIAO +</text><text x="{u}" y="{v + 10}" class="s on" text-anchor="middle">Sense</text>')
    # lamp centred on the nose bar: star 14 wide, 2 deep behind the bar; lens 10 wide, 7 proud
    u, v = T(-STAR_R, STAR_Y + 1); out.append(f'<rect x="{u}" y="{v}" width="{2 * STAR_R * s}" height="{2 * s}" class="lamp"/>')
    u, v = T(-LENS_R, STAR_Y + 1 + LENS_LEN); out.append(f'<rect x="{u}" y="{v}" width="{2 * LENS_R * s}" height="{LENS_LEN * s}" class="lamp"/>')
    # ghost of where the forward ranger could go later: on the hood, under the camera
    u, v = T(RANGER_X - 9, 20); out.append(f'<rect x="{u}" y="{v}" width="{18 * s}" height="{3 * s}" class="ghost"/>')
    for x in (-AXLE_X, AXLE_X):
        for y in (-AXLE_Y, AXLE_Y):
            u, v = T(x, y); out.append(f'<circle cx="{u}" cy="{v}" r="{MOTOR_R * s}" class="motor"/>')
    # labels, top
    def lab(x, y, tx, ty, text, anchor="start"):
        u, v = T(x, y); out.append(f'<line x1="{u}" y1="{v}" x2="{tx}" y2="{ty}" class="dim"/><text x="{tx + (4 if anchor == "start" else -4)}" y="{ty + 4}" class="t" text-anchor="{anchor}">{text}</text>')
    lab(0, STAR_Y + 7, 124, 90, "flashlight, centred", "end")
    lab(RANGER_X, 21.5, 350, 96, "forward ranger: optional, later, on the hood")
    lab(5, 10.5, 350, 196, "camera on the cabin, over the hood")
    lab(AXLE_X, -AXLE_Y, 350, 380, "615 motor, axle end")
    lab(6, -20, 350, 330, "down-looking ranger under the pan")
    lab(-5.5, 20, 124, 200, "250 mAh pack, floor pan", "end")
    lab(-8, 0, 124, 260, "motion sensor", "end")
    out.append('<text x="120" y="278" class="t" text-anchor="end">under the pan</text>')
    # dims
    (ua, va), (ub, vb) = T(-AXLE_X - PROP_R, AXLE_Y + PROP_R), T(-AXLE_X - PROP_R, -AXLE_Y - PROP_R)
    out.append(f'<line x1="16" y1="{va}" x2="16" y2="{vb}" class="dim"/><line x1="11" y1="{va}" x2="21" y2="{va}" class="dim"/><line x1="11" y1="{vb}" x2="21" y2="{vb}" class="dim"/><text x="22" y="{(va + vb) / 2}" class="t">91 mm</text>')
    (ua, _), (ub, _) = T(-AXLE_X - PROP_R, 0), T(AXLE_X + PROP_R, 0)
    out.append(f'<line x1="{ua}" y1="420" x2="{ub}" y2="420" class="dim"/><line x1="{ua}" y1="415" x2="{ua}" y2="425" class="dim"/><line x1="{ub}" y1="415" x2="{ub}" y2="425" class="dim"/><text x="{ox}" y="438" class="t" text-anchor="middle">71 mm tip to tip</text>')
    out.append('</g>')
    # side view
    out.append(f'<text x="{sx}" y="26" class="h" text-anchor="middle">Side view, nose left</text><g>')
    (a, b), (c, d) = Sd(60, -SKID), Sd(-60, -SKID); out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="dim"/>')
    for y in (AXLE_Y, -AXLE_Y):
        (a, b), (c, d) = Sd(y, 0), Sd(y, -SKID); out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="rod"/>')
    (a, b), (c, d) = Sd(RAIL_Y, 0), Sd(-RAIL_Y, 0); out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="rod"/>')
    for y in (AXLE_Y, -AXLE_Y):
        a, b = Sd(y + MOTOR_R, MOTOR_Z1); out.append(f'<rect x="{a}" y="{b}" width="{2 * MOTOR_R * s}" height="{(MOTOR_Z1 - MOTOR_Z0) * s}" class="motor"/>')
        (a, b), (c, d) = Sd(y + PROP_R, PROP_Z), Sd(y - PROP_R, PROP_Z); out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="rodh"/>')
    for bx, cls in ((VL1, "pan"), (GY, "pan"), (BAT, "pan"), (CABIN, "part"), (CAM, "part")):
        _, _, y0, y1, z0, z1 = bx; a, b = Sd(y1, z1)
        out.append(f'<rect x="{a}" y="{b}" width="{(y1 - y0) * s}" height="{(z1 - z0) * s}" class="{cls}"/>')
    a, b = Sd(0, 2.9); out.append(f'<text x="{a}" y="{b + 4}" class="s" text-anchor="middle">250 mAh</text>')
    a, b = Sd(0, 13.3); out.append(f'<text x="{a}" y="{b + 4}" class="s on" text-anchor="middle">XIAO + Sense</text>')
    # lamp: star vertical at y 33..35, z 0..14; lens y 35..42, z 2..12
    a, b = Sd(STAR_Y + 3, STAR_Z + STAR_R); out.append(f'<rect x="{a}" y="{b}" width="{3 * s}" height="{2 * STAR_R * s}" class="lamp"/>')
    a, b = Sd(STAR_Y + 3 + LENS_LEN, STAR_Z + LENS_R); out.append(f'<rect x="{a}" y="{b}" width="{LENS_LEN * s}" height="{2 * LENS_R * s}" class="lamp"/>')
    def labs(y, z, tx, ty, text, anchor="start"):
        a, b = Sd(y, z); out.append(f'<line x1="{a}" y1="{b}" x2="{tx}" y2="{ty}" class="dim"/><text x="{tx + (4 if anchor == "start" else -4)}" y="{ty + 4}" class="t" text-anchor="{anchor}">{text}</text>')
    labs(12, 18, 560, 296, "camera, 10° down", "end")
    labs(-AXLE_Y, PROP_Z, 800, 300, "prop plane, 16 mm up")
    labs(STAR_Y + 10, 7, 540, 440, "flashlight, lens 7 mm proud", "end")
    labs(-21, -2, 760, 450, "down-looking ranger")
    labs(0, -2, 640, 450, "motion sensor")
    (a, b), (c, d) = Sd(-45, -SKID), Sd(-45, 20.8)
    out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="dim"/><text x="{a + 6}" y="{(b + d) / 2 + 4}" class="t">26 mm</text>')
    out.append('</g></svg>')
    return "\n".join(out)


# ---------------------------------------------------------------- the two explanatory figures
def system_figure():
    return '''<svg viewBox="0 0 900 400" role="img" aria-label="Where the thinking happens: the drone streams video over Wi-Fi to a local computer, which detects the person and sends velocity commands back; the drone's own controller keeps it level and at height">
<style>.bx{fill:var(--paper);stroke:var(--ink);stroke-width:1.4;rx:5}.bs{fill:var(--steel-soft);stroke:var(--steel);stroke-width:1.4;rx:5}
.t{font-size:12px;fill:var(--ink)}.s{font-size:11px;fill:var(--ink-2)}.h{font-size:14px;font-weight:700;fill:var(--ink)}.m{font-size:11px;fill:var(--steel);font-weight:700}
.ar{fill:none;stroke:var(--steel);stroke-width:2;marker-end:url(#ah)}.ar2{fill:none;stroke:var(--ink);stroke-width:2;marker-end:url(#ah2)}</style>
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--steel)"/></marker>
<marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--ink)"/></marker></defs>
<text x="20" y="26" class="h">Where the thinking happens. The aircraft is the reflexes; the computer on the desk is the brain. Nothing leaves the apartment.</text>
<rect x="30" y="60" width="330" height="300" class="bs"/><text x="195" y="84" class="h" text-anchor="middle">On the drone, 33 g</text>
<rect x="50" y="100" width="290" height="46" class="bx"/><text x="60" y="119" class="t">Camera: 320 &times; 240 JPEG, 10 to 15 frames a second</text><text x="60" y="136" class="s">about 100 to 150 kB/s on the air; stills on request first</text>
<rect x="50" y="158" width="290" height="92" class="bx"/><text x="60" y="177" class="t">ESP-Drone flight controller on the ESP32-S3</text><text x="60" y="194" class="s">500 Hz attitude loop from the motion sensor</text><text x="60" y="210" class="s">height hold from the down-looking ranger</text><text x="60" y="226" class="s">takes velocity setpoints: forward, sideways, yaw rate, height</text><text x="60" y="242" class="s">levels after 300 ms of silence, cuts thrust after 500 ms</text>
<rect x="50" y="262" width="290" height="62" class="bx"/><text x="60" y="281" class="t">Forward 8 &times; 8 ranger</text><text x="60" y="298" class="s">clamps forward speed to zero under 60 cm,</text><text x="60" y="314" class="s">whatever the brain says</text>
<text x="195" y="346" class="s" text-anchor="middle">four motors, 250 mAh pack, about 3 min a pack</text>
<rect x="540" y="60" width="330" height="300" class="bs"/><text x="705" y="84" class="h" text-anchor="middle">On the desk: your PC or a laptop</text>
<rect x="560" y="100" width="290" height="62" class="bx"/><text x="570" y="119" class="t">Person detector + tracker</text><text x="570" y="136" class="s">a small YOLO-class model: a few ms on the RTX 5000 Ada,</text><text x="570" y="152" class="s">30 to 60 ms on a laptop CPU at 320 &times; 240</text>
<rect x="560" y="174" width="290" height="92" class="bx"/><text x="570" y="193" class="t">Follow controller, 15 to 20 times a second</text><text x="570" y="210" class="s">box centre off the frame centre &rarr; yaw rate</text><text x="570" y="226" class="s">box height &rarr; distance &rarr; forward speed, hold 2.5 m</text><text x="570" y="242" class="s">height setpoint 1.2 m; no person for 1 s &rarr; hover; 5 s &rarr; land</text><text x="570" y="258" class="s">limits: 0.8 m/s, 90&deg;/s</text>
<rect x="560" y="278" width="290" height="62" class="bx"/><text x="570" y="297" class="t">Link: the drone's own Wi-Fi network, UDP</text><text x="570" y="314" class="s">the same link the phone app uses today;</text><text x="570" y="330" class="s">a USB Wi-Fi stick if the PC has none</text>
<path d="M360,125 L540,125" class="ar"/><text x="450" y="118" class="m" text-anchor="middle">video up</text>
<path d="M540,215 L360,215" class="ar2"/><text x="450" y="208" class="m" text-anchor="middle">setpoints down</text>
<text x="450" y="262" class="s" text-anchor="middle">loop, camera to motor:</text><text x="450" y="278" class="s" text-anchor="middle">60 to 140 ms with the GPU</text><text x="450" y="294" class="s" text-anchor="middle">100 to 200 ms on a CPU</text>
<text x="450" y="376" class="s" text-anchor="middle">A person walking at 1 m/s moves 15 cm in 150 ms.</text>
<text x="450" y="393" class="s" text-anchor="middle">Only the follow commands cross the air; the aircraft stays level and at height on its own, so a dropped frame costs a little lag, never control.</text>
</svg>'''


def geometry_figure():
    # top view of the room at 1 px = 5 mm; drone at (150, 200) facing right (+x)
    s = 0.14; dx, dy = 120, 270
    fov = math.radians(66 / 2); r = 3500 * s
    fx1, fy1 = dx + r * math.cos(fov), dy - r * math.sin(fov)
    fx2, fy2 = dx + r * math.cos(fov), dy + r * math.sin(fov)
    stop = math.radians(30); rs = 600 * s
    sx1, sy1 = dx + rs * math.cos(stop), dy - rs * math.sin(stop)
    sx2, sy2 = dx + rs * math.cos(stop), dy + rs * math.sin(stop)
    px = dx + 2500 * s
    return f'''<svg viewBox="0 0 900 540" role="img" aria-label="Following geometry from above: the camera's 66 degree field of view, the person held 2.5 m ahead, the yaw and distance corrections, the 60 cm forward stop">
<style>.t{{font-size:12px;fill:var(--ink)}}.s{{font-size:11px;fill:var(--ink-2)}}.h{{font-size:14px;font-weight:700;fill:var(--ink)}}
.fov{{fill:var(--steel-soft);fill-opacity:0.5;stroke:var(--steel);stroke-width:1.2}}.stp{{fill:var(--no-soft);fill-opacity:0.6;stroke:var(--no);stroke-width:1.2;stroke-dasharray:4 3}}
.d{{fill:var(--matte);stroke:var(--matte-edge);stroke-width:1.2}}.p{{fill:var(--skin);stroke:var(--skin-edge);stroke-width:1.4}}.dim{{fill:none;stroke:var(--ink-2);stroke-width:1}}
.ar{{fill:none;stroke:var(--ink);stroke-width:1.6;marker-end:url(#ah3)}}</style>
<defs><marker id="ah3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--ink)"/></marker></defs>
<text x="20" y="26" class="h">Following, seen from above. 1 px = 7 mm. The person is held about 2.5 m ahead, centred in the picture.</text>
<polygon points="{dx},{dy} {fx1:.0f},{fy1:.0f} {fx2:.0f},{fy2:.0f}" class="fov"/>
<polygon points="{dx},{dy} {sx1:.0f},{sy1:.0f} {sx2:.0f},{sy2:.0f}" class="stp"/>
<rect x="{dx - 9}" y="{dy - 7}" width="18" height="14" class="d"/><circle cx="{dx - 7}" cy="{dy - 10}" r="3" class="d"/><circle cx="{dx + 7}" cy="{dy - 10}" r="3" class="d"/><circle cx="{dx - 7}" cy="{dy + 10}" r="3" class="d"/><circle cx="{dx + 7}" cy="{dy + 10}" r="3" class="d"/>
<text x="{dx}" y="{dy + 32}" class="t" text-anchor="middle">drone, 1.2 m up</text>
<circle cx="{px:.0f}" cy="{dy}" r="24" class="p"/><circle cx="{px:.0f}" cy="{dy}" r="8" class="p"/><text x="{px:.0f}" y="{dy + 44}" class="t" text-anchor="middle">person</text>
<line x1="{dx}" y1="{dy + 80}" x2="{px:.0f}" y2="{dy + 80}" class="dim"/><line x1="{dx}" y1="{dy + 75}" x2="{dx}" y2="{dy + 85}" class="dim"/><line x1="{px:.0f}" y1="{dy + 75}" x2="{px:.0f}" y2="{dy + 85}" class="dim"/><text x="{(dx + px) / 2:.0f}" y="{dy + 98}" class="s" text-anchor="middle">2.5 m held, from the person's height in the picture</text>
<text x="{fx1 + 14:.0f}" y="{dy + 4}" class="s">camera, about 66&deg; wide, reads 3.5 m here</text>
<text x="{sx2 + 8:.0f}" y="{sy2 + 14:.0f}" class="s" fill="var(--no)">forward stop: 60&deg;, 60 cm, on the drone</text>
<path d="M{dx + 40},{dy - 60} A60,60 0 0 1 {dx + 64},{dy - 14}" class="ar"/><text x="{dx + 72}" y="{dy - 58}" class="s">yaw toward the person when the box drifts off centre</text>
<path d="M{dx + 20},{dy + 120} L{dx + 120},{dy + 120}" class="ar"/><text x="{dx + 20}" y="{dy + 138}" class="s">forward when the box shrinks, back when it grows</text>
<text x="20" y="528" class="s">Sideways drift is not sensed (no optical-flow sensor fits the XIAO's pins): the loop re-aims and re-ranges, so the drone may slowly orbit the person. Acceptable for a prototype.</text>
</svg>'''


# ---------------------------------------------------------------- text, shared by page and markdown
KPIS = [("0 g", "added to the drone for following"), ("~150 ms", "camera-to-motor loop, est."), ("15 Hz", "follow commands"),
        ("2.6 min", "a pack with the speaker fitted (3 min before it); four packs"), ("kept", "the forward ranger stays, decided 2026-11-09")]

THREE = [
    ("A Raspberry Pi 5 on the drone?", "No. The board alone is 46 g and wants 5 V at up to 5 A, so the aircraft to carry it starts near 300 g with bigger cells and 3-inch props: a different project. Even a Pi Zero 2 W (10 g) drags in a 5 V supply and a camera, about 25 g, and the drone grows into the 716-motor class. None of it is needed: the Wi-Fi link already exists for control, and a video stream rides the same link to the computer on the desk, which has more compute than any flying Pi."),
    ("The LiDAR?", "The drone has no scanning LiDAR and never did: the payload plan rejected the 47 g LD19 that Crumb uses and the 110 g RPLIDAR. What it has are two laser rangers the size of a fingernail, 0.5 g each. The down-looking one gives one distance and is what height hold runs on; it is not optional for indoor flying. The forward one gives an 8 × 8 grid of distances over 60° to 3.5 m: a stop-before-the-wall reflex, not a map. Leaving it off saves 0.5 g and the biggest single firmware item (porting ST's driver, the boot re-addressing dance). It changes nothing in size."),
    ("Smaller drone, local processing?", "The drone stays exactly this size; following adds nothing to it. Every added gram of thinking goes on the desk. Processing is local in the strict sense: the PC joins the drone's own Wi-Fi network, as the phone app does today, and no frame or command touches the internet."),
]

CAPABLE = [
    ("Rotate toward you", "Yes. Yaw in place from the four motors, up to about 90° a second, driven by how far your box sits off the centre of the picture."),
    ("Keep its distance", "Yes. Your height in the picture is the range: at 2.5 m a standing adult fills about two thirds of the frame. The controller holds 2.5 m, moving at up to 0.8 m/s."),
    ("Hold height", "Yes, from the down-looking ranger: 1.2 m, about head height when you are seated. Not sensed by the camera at all."),
    ("Follow around a corner", "Yes. It turns with you, and when it cuts the corner the forward ranger sees the wall the camera is not looking at and clamps forward speed to zero under 60 cm. That reflex runs on the drone, with or without the brain."),
    ("Hold still when it loses you", "Not on its own. With no optical-flow sensor it has no horizontal position hold, so it hovers level but drifts. The rule: no person for 1 s, hover; 5 s, land. The controller's own 500 ms link timeout sits under that."),
    ("Run for how long", "About 2.6 min a pack with the speaker fitted (3 min before it), four packs, so about 10 min of following per charge round. The limit of this class, not of the brain."),
]

LATENCY = [("Capture and JPEG on the drone", "40 to 70 ms"), ("Wi-Fi, drone to PC", "10 to 30 ms"), ("Detector", "5 to 10 ms on the GPU; 30 to 60 ms on a laptop CPU"),
           ("Follow controller", "under 1 ms"), ("Wi-Fi, PC to drone", "5 to 15 ms"), ("Commander to motors", "2 to 10 ms"), ("Whole loop", "60 to 140 ms with the GPU; 100 to 200 ms on a CPU")]

COMPARE = [("Flying mass, est.", f"{MASS_WITH} g", f"{MASS_WITHOUT} g"), ("Thrust to weight on the vendor's 68 gf", f"{TW_WITH:.2f}", f"{TW_WITHOUT:.2f}"),
           ("Footprint, height", "71 × 91 mm, 26 mm", "the same"), ("Nose", "flashlight left, ranger right", "flashlight on the centre line"),
           ("Stops before a wall", "yes, under 60 cm", "no; the brain only sees what the camera sees"),
           ("Firmware to write", "camera task, ST multizone driver, boot re-addressing, lamp; microphone and playback tasks since 2026-11-09", "camera task, lamp; microphone and playback tasks"),
           ("I²C devices", "three, one re-addressed at boot", "two, both at their factory addresses"), ("Pins", "all eleven used; D10 is the speaker's since 2026-11-09", "D7 free"),
           ("Decision 2026-11-09", "kept", "declined")]

WHAT_RUNS = [("Attitude, 500 Hz", "drone", "the motion sensor through ESP-Drone's existing loop"), ("Height hold", "drone", "down-looking ranger into the Kalman estimator, as planned"),
             ("Forward stop", "drone", "the forward 8 \u00d7 8 ranger clamps forward speed under 60 cm"), ("Video", "drone → PC", "QVGA JPEG over UDP, the camera task in the firmware plan"),
             ("See the person", "PC", "a small detector; the RTX 5000 Ada does it in milliseconds"), ("Decide where to go", "PC", "box centre and height into yaw rate, forward speed, height"),
             ("Fly there", "PC → drone", "velocity setpoints over the existing UDP link, 15 to 20 a second")]


def table(rows, head):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table><tr>{th}</tr>{tr}</table></div>'


def md_table(rows, head):
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def build():
    style = re.search(r"<style>.*?</style>", (PAGES / "custom-build.html").read_text(encoding="utf8"), re.S).group(0)
    kpis = "".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{l}</div></div>' for v, l in KPIS)
    three = "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in THREE)
    capable = "".join(f"<li><strong>{q}.</strong> {a}</li>" for q, a in CAPABLE)
    html = f'''<title>XS Drone Following</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=Source+Code+Pro:wght@400;600&display=swap">
{style}
<div class="wrap">
<div class="masthead">
  <div class="eyebrow">XS drone &middot; following mode &middot; where the thinking happens</div>
  <h1>Can it follow you?</h1>
  <div class="sub">Yes, indoors, in real time, with everything processed locally: the aircraft is the reflexes and the computer on your desk is the brain. No Raspberry Pi flies. The drone stays the 33 g car-like ladder of the <a href="{BUILD_PAGE}">build page</a>, forward ranger included: leaving it off was weighed here and declined on 2026-11-09. Drafted 2026-11-09; nothing has flown. Source of truth: <code>xs_drone/docs/following.md</code>.</div>
</div>
<div class="kpis">{kpis}</div>

<h2>Three questions</h2>
{three}

<h2>Where the thinking happens</h2>
<figure>{system_figure()}<figcaption>The split is the Crazyflie's, which ESP-Drone inherits: a fast loop on the aircraft keeps it level and at height; a slow loop on a computer tells it where to go. The video stream and the commands share the one Wi-Fi link, so the first camera flights are stills on request while link loss is measured, exactly as the payload plan says.</figcaption></figure>
{table(WHAT_RUNS, ["Job", "Where", "How"])}
{table(LATENCY, ["Stage", "Time"])}

<h2>What it can do, honestly</h2>
<ul>{capable}</ul>
<figure>{geometry_figure()}<figcaption>The two corrections are yaw (keep you centred) and range (keep your picture-height constant). Height is the down-looking ranger's, not the camera's. The red wedge is the forward ranger's stop, a reflex on the drone itself.</figcaption></figure>

<h2>The forward ranger stays</h2>
<p>Leaving it off was weighed: 0.5 g lighter, a symmetric nose with the flashlight on the centre line, two firmware items instead of four. The builder kept it on 2026-11-09, and following is the reason: the camera looks at the person, not at the wall the drone is about to cut past, and the ranger's stop-before-the-wall reflex covers exactly that blind spot. The nose stays as approved: flashlight left, ranger right.</p>
<figure>{three_quarter(False)}<figcaption>Drawn before the speaker and its amplifier were added later the same evening; those are on the build page. As approved, in the finished colours: bare stainless, the pack's white wrap, the bare boards hidden under it and the forward ranger's green board at the nose (no paint, no skins: rule 2026-11-09), black props and controller, the flashlight left and the forward ranger right under the front prop discs.</figcaption></figure>
{table(COMPARE, ["", "With the forward ranger (the build)", "Camera-only nose (declined 2026-11-09)"])}
<p><strong>What the decision costs.</strong> The two bigger firmware items stay on the list: ST's multizone driver ported to ESP-Drone's I&sup2;C layer, and the boot re-addressing of the down-looking ranger. Both were already in the payload plan; following adds nothing to them.</p>

<h2>What is not promised</h2>
<ul>
<li><strong>Position hold.</strong> No optical-flow sensor fits: the PMW3901 needs four SPI pins and the XIAO has none free with the ranger's LPn line in use. Expect slow drift and a slow orbit around you; the follow loop corrects aim and range, not sideslip.</li>
<li><strong>Frame rate.</strong> 10 to 15 frames a second at 320 &times; 240 is the plan; the payload page's Wi-Fi budget is the open risk and is measured before the rate goes up. Following works at 5 fps, just less smoothly.</li>
<li><strong>Light.</strong> The detector needs a lit room; the flashlight is for seeing, not for the detector.</li>
<li><strong>Mapping.</strong> None. Room maps are Crumb's and the FamilyBot's job, with a real LiDAR on a ground robot that can carry it.</li>
</ul>
</div>
'''
    HTML_OUT.write_text(html, encoding="utf8")

    md = f'''# Following: can the drone follow a person, locally, in real time?

Drafted 2026-11-09 at the builder's question; nothing has flown. Web version with the drawings: [XS Drone Following]({FOLLOW_PAGE}), source [pages/following.html](pages/following.html);
the aircraft is the one on [custom-build.md](custom-build.md) and its [build page]({BUILD_PAGE}).

Short answer: yes, indoors, with the aircraft as the reflexes and the computer on the desk as the brain. No Raspberry Pi
flies. The drone stays the 33 g car-like ladder, forward ranger included: leaving it off was weighed and declined on
2026-11-09.

## Three questions

''' + "\n\n".join(f"**{q}** {a}" for q, a in THREE) + f'''

## Where the thinking happens

The split is the Crazyflie's, which ESP-Drone inherits: a fast loop on the aircraft keeps it level and at height;
a slow loop on a computer tells it where to go. The PC joins the drone's own Wi-Fi network, as the phone app does;
nothing touches the internet.

{md_table(WHAT_RUNS, ["Job", "Where", "How"])}

{md_table(LATENCY, ["Stage", "Time"])}

A person walking at 1 m/s moves 15 cm in 150 ms. Only the follow commands cross the air; a dropped frame costs a
little lag, never control (the commander levels after 300 ms of silence and cuts thrust after 500 ms).

## What it can do

''' + "\n".join(f"- **{q}.** {a}" for q, a in CAPABLE) + f'''

Follow law: box centre off the frame centre → yaw rate (limit 90°/s); box height → range → forward speed (hold 2.5 m,
limit 0.8 m/s); height setpoint 1.2 m on the down-looking ranger; no person for 1 s → hover, 5 s → land. Camera about
66° wide (the stock lens; read the module, OV2640 or OV3660, off the board when it arrives).

## The forward ranger stays

Leaving it off was weighed: 0.5 g lighter, a symmetric nose with the flashlight centred, two firmware items instead of
four. The builder kept it on 2026-11-09, and following is the reason: the camera looks at the person, not at the wall
the drone is about to cut past, and the ranger's stop-before-the-wall reflex covers that blind spot. The nose stays as
approved: flashlight left, ranger right.

{md_table(COMPARE, ["", "With the forward ranger (the build)", "Camera-only nose (declined 2026-11-09)"])}

What the decision costs: ST's multizone driver and the boot re-addressing stay on the firmware list, as the payload
plan already had them.

## Not promised

- **Position hold.** No optical-flow sensor fits (the PMW3901 needs four SPI pins; the XIAO has none free). Expect slow
  drift and a slow orbit; the loop corrects aim and range, not sideslip.
- **Frame rate.** 10 to 15 fps at 320 × 240 is the plan; the Wi-Fi budget is measured before the rate goes up.
- **Light.** The detector needs a lit room.
- **Mapping.** None; that is Crumb's and the FamilyBot's job with a real LiDAR on a ground robot.
'''
    MD_OUT.write_text(md, encoding="utf8")
    print(f"wrote {HTML_OUT.relative_to(DOCS.parent)} and {MD_OUT.relative_to(DOCS.parent)}")


if __name__ == "__main__":
    build()
