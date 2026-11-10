"""XS drone, lift revision, drawn and approved 2026-11-10: 7 x 20 mm motors on 40 mm props, the ladder in brass, and the three
features together: voice (approved 2026-11-09), a camera that tilts +-30 deg on a 1.5 g linear servo, and rangers all round behind
an I2C multiplexer so no pin is needed.

Writes the three-quarter view and the plan views into docs/pages/custom-build.html, replacing the figure blocks between the
markers <!-- lift-3q --> ... <!-- /lift-3q --> and <!-- lift-plan --> ... <!-- /lift-plan --> (on the first run it replaces the
2026-11-09 figures, found by their aria-labels). Geometry in mm: x right, y forward, z up, z = 0 at the rails. Edit this script,
not the SVG. The projection and the helpers are follow_page.py's."""
from __future__ import annotations

import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
PAGE = PAGES / "custom-build.html"

# ---------------------------------------------------------------- the aircraft, in mm
RAIL_X, RAIL_Y = 7, 33                # two rails at x = +-7, y from -33 to +33 (unchanged)
AXLE_X, AXLE_Y = 25, 30               # axles at y = +-30, now x from -25 to +25: 50 mm, for the 40 mm discs
NOSE_HALF, TAIL_HALF = 15.5, 7        # nose bar 31 mm at y = +33, tail bar 14 mm at y = -33
SKID = 7                              # skids 7 mm down at the axle ends (5 before): the 20 mm cans hang 4 mm under the axle
MOTOR_R, MOTOR_Z0, MOTOR_Z1 = 3.5, -4.0, 16.0   # 7 x 20 mm can, prop plane kept where it was
COLLAR_R, COLLAR_H = 5.0, 3.0         # two turns of 1.5 mm brass rod round a 7 mm can: 10 mm over the outside
PROP_R, PROP_Z = 20.0, 16.8           # 40 mm four-blade props
BAT = (-5.5, 5.5, -27, 27, 0.0, 5.8)             # the 250 mAh pack as the floor pan
CABIN = (-8.75, 8.75, -10.5, 10.5, 5.8, 20.8)     # XIAO + Sense on the pan
CAM = (-4.25, 4.25, 10.5, 15.5, 13.0, 21.5)       # the camera module, 8.5 x 8.5 x 5, hanging on its hinge at the cabin's front
HINGE_Y, HINGE_Z, LEVER_TOP = 13.0, 17.25, 24.0   # pin through the module's middle; a 6.75 mm lever up to the servo's arm
SERVO = (-7.6, 7.6, -10.7, 10.7, 20.8, 26.8)      # AGFRC 1.5 g linear servo lying on the roof, arm forward
SIDE_L = (-11.0, -8.0, -12.5, 12.5, 0.0, 11.0)   # TOF400C VL53L1X, about 25 x 11 x 3, low beside the left rail, looking left: under the discs, 6 mm clear
SIDE_R = (8.0, 11.0, -12.5, 12.5, 0.0, 11.0)
REAR = (-12.5, 12.5, -36.0, -33.0, 0.0, 11.0)   # the same behind the tail bar, looking back, low: nothing in its field
MUX = (-15.3, 15.3, 11.0, 28.6, 5.8, 8.5)         # Adafruit TCA9548A across the hood, chip down
GY = (-8, 8, -10.5, 10.5, -2.0, 0.0)              # motion sensor under the pan, centre
VL1 = (-6.5, 6.5, -30, -12, -2.0, 0.0)            # down-looking ranger under the pan, tail
AMP = (-10.5, 10.5, 11, 29.5, -3.0, 0.0)          # PAM8403 under the hood, components down
SPK = (-8, 8, -30.5, -10.5, 5.8, 10.7)            # Same Sky speaker on the pan's tail, grille up
LAMP_X, RANGER_X = -9.0, 9.0
STAR_R, STAR_Y, STAR_Z = 7.0, 33.0, 7.0
LENS_R, LENS_LEN = 5.0, 7.0

MASS = 53.7            # g est., everything on, brass ladder (the build document's ledger)
THRUST_LO, THRUST_HI = 120.0, 140.0   # gf est. for four 7 x 20 motors on 40 mm props at 3.7 V; the hover test decides
FOOT_W, FOOT_L = 2 * (AXLE_X + PROP_R), 2 * (AXLE_Y + PROP_R)   # 90 x 100
HEIGHT = SERVO[5] + SKID                                           # floor to the servo's top: 33.8

# ---------------------------------------------------------------- projection for the three-quarter view
S = 3.5
AZ, EL = math.radians(34), math.radians(27)
CX, CY = 500, 300


def P(x, y, z):
    xr = x * math.cos(AZ) - y * math.sin(AZ)
    yr = x * math.sin(AZ) + y * math.cos(AZ)
    return CX + S * xr, CY - S * (z * math.cos(EL) - yr * math.sin(EL)), yr


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
        else:
            out.append(P(cx + r * math.cos(a), cy, cz + r * math.sin(a)))
    return out


def cylinder(cx, cy, r, z0, z1, fill, edge):
    _, _, d = P(cx, cy, (z0 + z1) / 2)
    top = circle3d(cx, cy, z1, r, "z")
    uc, vt, _ = P(cx, cy, z1)
    _, vb, _ = P(cx, cy, z0)
    rr = r * S
    body = (f'<path d="M{uc - rr:.1f},{vt:.1f} L{uc - rr:.1f},{vb:.1f} '
            f'A{rr:.1f},{rr * math.sin(EL):.1f} 0 0 0 {uc + rr:.1f},{vb:.1f} L{uc + rr:.1f},{vt:.1f}" '
            f'fill="{fill}" fill-opacity="0.9" stroke="{edge}" stroke-width="1.1"/>')
    topd = f'<polygon points="{pts(top)}" fill="{fill}" stroke="{edge}" stroke-width="1.1" style="filter:brightness(1.06)"/>'
    return d, body + topd


def box(b, fill, edge, depth_bias=0.0):
    x0, x1, y0, y1, z0, z1 = b
    _, _, d = P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    top = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]
    front = [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)]
    right = [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)]
    f = (f'<polygon points="{pts(right)}" fill="{fill}" style="filter:brightness(0.72)" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>'
         f'<polygon points="{pts(front)}" fill="{fill}" style="filter:brightness(0.9)" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>'
         f'<polygon points="{pts(top)}" fill="{fill}" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>')
    return d + depth_bias, f


def prop(cx, cy):
    _, _, d = P(cx, cy, PROP_Z)
    disc = circle3d(cx, cy, PROP_Z, PROP_R, "z")
    out = [f'<polygon points="{pts(disc)}" class="disc"/>']
    for k in range(4):
        a = math.radians(45 + 90 * k)
        tip = (cx + PROP_R * 0.95 * math.cos(a), cy + PROP_R * 0.95 * math.sin(a))
        mid = (cx + PROP_R * 0.5 * math.cos(a), cy + PROP_R * 0.5 * math.sin(a))
        w = 3.8
        n = (-math.sin(a) * w, math.cos(a) * w)
        blade = [P(cx + 1.5 * math.cos(a), cy + 1.5 * math.sin(a), PROP_Z),
                 P(mid[0] + n[0], mid[1] + n[1], PROP_Z), P(*tip, PROP_Z), P(mid[0] - n[0], mid[1] - n[1], PROP_Z)]
        out.append(f'<polygon points="{pts(blade)}" class="blade"/>')
    hub = circle3d(cx, cy, PROP_Z + 0.5, 1.8, "z", 16)
    out.append(f'<polygon points="{pts(hub)}" class="hub"/>')
    return d + 40, "".join(out)


def lamp(lx):
    _, _, d = P(lx, STAR_Y + 3, STAR_Z)
    star = circle3d(lx, STAR_Y, STAR_Z, STAR_R, "y")
    lens_back = circle3d(lx, STAR_Y + 1, STAR_Z, LENS_R, "y")
    lens_front = circle3d(lx, STAR_Y + 1 + LENS_LEN, STAR_Z, LENS_R, "y")
    i_top = max(range(len(lens_back)), key=lambda i: -lens_back[i][1])
    i_bot = min(range(len(lens_back)), key=lambda i: -lens_back[i][1])
    i_r = max(range(len(lens_back)), key=lambda i: lens_back[i][0])
    side = [lens_back[i_top], lens_front[i_top], lens_front[i_r], lens_front[i_bot], lens_back[i_bot], lens_back[i_r]]
    f = (f'<polygon points="{pts(star)}" fill="var(--metal-soft)" stroke="var(--metal)" stroke-width="1.1"/>'
         f'<polygon points="{pts(side)}" fill="var(--lens)" fill-opacity="0.9" stroke="var(--metal)" stroke-width="1"/>'
         f'<polygon points="{pts(lens_front)}" fill="var(--lamp-face)" stroke="var(--metal)" stroke-width="1.1"/>')
    return d + 5, f


def three_quarter():
    items = []
    for x in (-RAIL_X, RAIL_X):
        items.append(rod((x, -RAIL_Y, 0), (x, RAIL_Y, 0)))
    for y in (-AXLE_Y, AXLE_Y):
        items.append(rod((-AXLE_X, y, 0), (AXLE_X, y, 0)))
    items.append(rod((-NOSE_HALF, RAIL_Y, 0), (NOSE_HALF, RAIL_Y, 0)))
    items.append(rod((-TAIL_HALF, -RAIL_Y, 0), (TAIL_HALF, -RAIL_Y, 0)))
    for x in (-AXLE_X, AXLE_X):
        for y in (-AXLE_Y, AXLE_Y):
            items.append(rod((x, y, 0), (x, y, -SKID)))
            items.append(cylinder(x, y, COLLAR_R, -COLLAR_H / 2, COLLAR_H / 2, "var(--brass-soft)", "var(--brass)"))
            items.append(cylinder(x, y, MOTOR_R, MOTOR_Z0, MOTOR_Z1, "var(--metal-soft)", "var(--metal)"))
            items.append(prop(x, y))
    items.append(box(GY, "var(--board)", "var(--board-edge)"))
    items.append(box(VL1, "var(--board)", "var(--board-edge)"))
    items.append(box(AMP, "var(--board)", "var(--board-edge)"))
    items.append(box(BAT, "var(--skin)", "var(--skin-edge)"))
    items.append(box(SPK, "var(--matte)", "var(--matte-edge)"))
    items.append(box(MUX, "var(--matte)", "var(--matte-edge)"))
    items.append(box(REAR, "var(--matte)", "var(--matte-edge)"))
    items.append(box(SIDE_L, "var(--matte)", "var(--matte-edge)"))
    items.append(box(CABIN, "var(--matte)", "var(--matte-edge)"))
    items.append(box(SIDE_R, "var(--matte)", "var(--matte-edge)", 2))
    items.append(box(SERVO, "var(--matte)", "var(--matte-edge)", 2))
    items.append(box(CAM, "var(--matte)", "var(--matte-edge)", 3))
    items.append(rod((0, HINGE_Y, HINGE_Z), (0, HINGE_Y, LEVER_TOP), 1.6, "brass"))        # the lever
    items.append(rod((0, SERVO[3], LEVER_TOP), (0, HINGE_Y, LEVER_TOP), 1.6, "brass"))     # the link from the servo's arm
    items.append(rod((-5.5, HINGE_Y, HINGE_Z), (5.5, HINGE_Y, HINGE_Z), 1.6, "brass"))     # the hinge pin
    items.append(lamp(LAMP_X))
    items.append(box((RANGER_X - 9, RANGER_X + 9, 33, 36, 0.5, 13.5), "var(--board)", "var(--board-edge)"))
    items.sort(key=lambda t: t[0])
    body = "\n".join(f for _, f in items)
    L = []

    def label(p3, tx, ty, text, anchor="start"):
        u, v, _ = P(*p3)
        L.append(f'<line x1="{u:.1f}" y1="{v:.1f}" x2="{tx}" y2="{ty}" class="lead"/><circle cx="{u:.1f}" cy="{v:.1f}" r="2.2" class="dot"/>'
                 f'<text x="{tx + (6 if anchor == "start" else -6)}" y="{ty + 4}" class="t" text-anchor="{anchor}">{text}</text>')

    label((AXLE_X, AXLE_Y, MOTOR_Z1), 770, 110, "7 × 20 mm motor, brass collar, 40 mm prop")
    label((4, 15.5, 17), 770, 160, "camera on a brass hinge, ±30°")
    label((7.6, 0, 26.8), 770, 200, "1.5 g linear servo, 6 mm lever")
    label((11.0, 4, 6), 770, 250, "side ranger, low beside the rail, one each side")
    label((15.3, 20, 8.5), 770, 300, "multiplexer across the hood")
    label((RANGER_X, 36, 7), 770, 350, "forward ranger, right headlight")
    label((LAMP_X, STAR_Y + 8, STAR_Z), 770, 400, "flashlight, left headlight")
    label((AXLE_X, -AXLE_Y, -SKID), 770, 450, "7 mm skids; 1.0 mm brass ladder")
    label((0, -36, 11), 230, 110, "rear ranger behind the tail bar", "end")
    label((-8, -20, 10.7), 230, 180, "speaker on the tail, grille up", "end")
    label((-5.5, 20, 5.8), 230, 250, "250 mAh pack: the floor pan", "end")
    label((-8, 0, -2), 230, 400, "sensor, ranger and amplifier under it", "end")
    label((-AXLE_X, -AXLE_Y, PROP_Z), 230, 470, "90 × 100 mm over the props", "end")
    title = f"Lift revision, approved 2026-11-10: brass ladder, 7 × 20 mm motors, 40 mm props, voice, tilting camera, rangers all round. About {MASS:.0f} g."
    return f'''<svg viewBox="0 0 1000 560" role="img" aria-label="Three-quarter view of the lift revision: brass ladder frame, four 7 by 20 mm motors with 40 mm props, white battery pan, black controller cabin with a hinged camera and a servo on its roof, side and rear ranger boards, a multiplexer board across the hood, two headlights">
<style>
.rod{{stroke:var(--brass);stroke-linecap:round;fill:none}} .brass{{stroke:var(--brass);stroke-linecap:round;fill:none}}
.disc{{fill:var(--metal-soft);fill-opacity:0.12;stroke:var(--ink-2);stroke-width:1;stroke-dasharray:4 4}}
.blade{{fill:var(--metal-soft);fill-opacity:0.9;stroke:var(--metal);stroke-width:0.8}} .hub{{fill:var(--metal);stroke:none}}
.lead{{stroke:var(--ink-2);stroke-width:1}} .dot{{fill:var(--ink-2)}}
.t{{font-size:12px;fill:var(--ink)}} .h{{font-size:13.5px;font-weight:700;fill:var(--ink)}}
</style>
<text x="20" y="26" class="h">{title}</text>
{body}
{"".join(L)}
</svg>'''


# ---------------------------------------------------------------- plan views, 3 px per mm
def plan_views():
    s = 3.0
    ox, oy = 300, 262

    def T(x, y):
        return ox + s * x, oy - s * y

    sx, sz0 = 740, 300

    def Sd(y, z):
        return sx - s * y, sz0 - s * z

    out = ['<svg viewBox="0 0 1040 520" role="img" aria-label="Top view and side view of the lift revision: 50 mm axles, 40 mm prop discs, the multiplexer on the hood, the side and rear rangers on the cabin, the servo on the roof, 7 mm skids">',
           '<style>.rod{fill:none;stroke:var(--brass);stroke-width:2.2;stroke-linecap:round}.rodh{fill:none;stroke:var(--metal);stroke-width:3.4;stroke-linecap:round}'
           '.prop{fill:none;stroke:var(--ink-2);stroke-width:1;stroke-dasharray:4 4}.motor{fill:var(--metal-soft);stroke:var(--metal);stroke-width:1.6}.collar{fill:none;stroke:var(--brass);stroke-width:2.6}'
           '.pan{fill:var(--skin);stroke:var(--skin-edge);stroke-width:1.4}.part{fill:var(--matte);stroke:var(--matte-edge);stroke-width:1.4}.board{fill:var(--board);stroke:var(--board-edge);stroke-width:1.4}'
           '.under{fill:none;stroke:var(--ink);stroke-width:1.2;stroke-dasharray:3 3}.lamp{fill:var(--lamp-face);stroke:var(--metal);stroke-width:1.4}.brass{fill:none;stroke:var(--brass);stroke-width:1.8;stroke-linecap:round}'
           '.t{font-size:12px;fill:var(--ink)}.s{font-size:11px;fill:var(--ink-2)}.on{fill:var(--on-matte)}.h{font-size:14px;font-weight:700;fill:var(--ink)}.dim{fill:none;stroke:var(--ink-2);stroke-width:1}</style>',
           f'<text x="{ox}" y="26" class="h" text-anchor="middle">Top view, nose up</text>', '<g>']
    for x in (-AXLE_X, AXLE_X):
        for y in (-AXLE_Y, AXLE_Y):
            u, v = T(x, y)
            out.append(f'<circle cx="{u}" cy="{v}" r="{PROP_R * s}" class="prop"/>')
    for x in (-RAIL_X, RAIL_X):
        (u1, v1), (u2, v2) = T(x, RAIL_Y), T(x, -RAIL_Y)
        out.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" class="rod"/>')
    for y in (-AXLE_Y, AXLE_Y):
        (u1, v1), (u2, v2) = T(-AXLE_X, y), T(AXLE_X, y)
        out.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" class="rod"/>')
    (u1, v1), (u2, v2) = T(-NOSE_HALF, RAIL_Y), T(NOSE_HALF, RAIL_Y)
    out.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" class="rod"/>')
    (u1, v1), (u2, v2) = T(-TAIL_HALF, -RAIL_Y), T(TAIL_HALF, -RAIL_Y)
    out.append(f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" class="rod"/>')

    def rect_top(b, cls):
        x0, x1, y0, y1 = b[:4]
        u, v = T(x0, y1)
        out.append(f'<rect x="{u:.1f}" y="{v:.1f}" width="{(x1 - x0) * s:.1f}" height="{(y1 - y0) * s:.1f}" class="{cls}"/>')

    for b, cls in ((AMP, "under"), (GY, "under"), (VL1, "under"), (BAT, "pan"), (MUX, "part"), (SPK, "part"), (REAR, "part"),
                   (SIDE_L, "part"), (SIDE_R, "part"), (CABIN, "part"), (SERVO, "part"), (CAM, "part")):
        rect_top(b, cls)
    u, v = T(0, -3)
    out.append(f'<text x="{u}" y="{v}" class="s on" text-anchor="middle">servo on</text><text x="{u}" y="{v + 12}" class="s on" text-anchor="middle">the roof</text>')
    u, v = T(-STAR_R, STAR_Y + 1)
    out.append(f'<rect x="{u + LAMP_X * s:.1f}" y="{v:.1f}" width="{2 * STAR_R * s}" height="{2 * s}" class="lamp"/>')
    u, v = T(-LENS_R, STAR_Y + 1 + LENS_LEN)
    out.append(f'<rect x="{u + LAMP_X * s:.1f}" y="{v:.1f}" width="{2 * LENS_R * s}" height="{LENS_LEN * s}" class="lamp"/>')
    rect_top((RANGER_X - 9, RANGER_X + 9, 33, 36), "board")
    for x in (-AXLE_X, AXLE_X):
        for y in (-AXLE_Y, AXLE_Y):
            u, v = T(x, y)
            out.append(f'<circle cx="{u}" cy="{v}" r="{COLLAR_R * s - 1.3}" class="collar"/><circle cx="{u}" cy="{v}" r="{MOTOR_R * s}" class="motor"/>')

    def lab(x, y, tx, ty, text, anchor="start"):
        u, v = T(x, y)
        out.append(f'<line x1="{u:.1f}" y1="{v:.1f}" x2="{tx}" y2="{ty}" class="dim"/><text x="{tx + (4 if anchor == "start" else -4)}" y="{ty + 4}" class="t" text-anchor="{anchor}">{text}</text>')

    lab(RANGER_X, 35, 456, 60, "forward ranger")
    lab(15.3, 20, 456, 96, "multiplexer on the hood")
    lab(4, 15.5, 456, 132, "camera, hinged, ±30°")
    lab(11.0, 5, 456, 168, "side ranger, both sides")
    lab(0, -36, 456, 262, "rear ranger behind the tail bar")
    lab(8, -20, 456, 316, "speaker on the tail")
    lab(AXLE_X, -AXLE_Y, 456, 350, "7 × 20 mm motor, collar")
    lab(LAMP_X, 40, 150, 70, "flashlight", "end")
    lab(-5.5, 24, 150, 128, "pan: the 250 mAh pack", "end")
    lab(-7.6, 8, 150, 176, "servo on the roof", "end")
    lab(-10.5, 24, 150, 224, "amplifier under the hood", "end")
    lab(-8, 0, 150, 290, "motion sensor", "end")
    lab(-6.5, -22, 150, 340, "down ranger", "end")
    out.append('<text x="146" y="356" class="s" text-anchor="end">both under the pan</text>')
    (ua, va), (ub, vb) = T(-AXLE_X - PROP_R, AXLE_Y + PROP_R), T(-AXLE_X - PROP_R, -AXLE_Y - PROP_R)
    out.append(f'<line x1="158" y1="{va}" x2="158" y2="{vb}" class="dim"/><line x1="153" y1="{va}" x2="163" y2="{va}" class="dim"/><line x1="153" y1="{vb}" x2="163" y2="{vb}" class="dim"/>'
               f'<text x="158" y="{va - 8}" class="t" text-anchor="middle">{FOOT_L:.0f} mm</text>')
    (ua, _), (ub, _) = T(-AXLE_X - PROP_R, 0), T(AXLE_X + PROP_R, 0)
    out.append(f'<line x1="{ua}" y1="438" x2="{ub}" y2="438" class="dim"/><line x1="{ua}" y1="433" x2="{ua}" y2="443" class="dim"/><line x1="{ub}" y1="433" x2="{ub}" y2="443" class="dim"/>'
               f'<text x="{ox}" y="456" class="t" text-anchor="middle">{FOOT_W:.0f} mm tip to tip</text>')
    out.append('</g>')
    # side view
    out.append(f'<text x="{sx}" y="26" class="h" text-anchor="middle">Side view, nose left</text><g>')
    (a, b), (c, d) = Sd(60, -SKID), Sd(-60, -SKID)
    out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="dim"/>')
    for y in (AXLE_Y, -AXLE_Y):
        (a, b), (c, d) = Sd(y, 0), Sd(y, -SKID)
        out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="rod"/>')
    (a, b), (c, d) = Sd(RAIL_Y, 0), Sd(-RAIL_Y, 0)
    out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="rod"/>')
    for y in (AXLE_Y, -AXLE_Y):
        a, b = Sd(y + MOTOR_R, MOTOR_Z1)
        out.append(f'<rect x="{a}" y="{b}" width="{2 * MOTOR_R * s}" height="{(MOTOR_Z1 - MOTOR_Z0) * s}" class="motor"/>')
        a, b = Sd(y + COLLAR_R, COLLAR_H / 2)
        out.append(f'<rect x="{a}" y="{b}" width="{2 * COLLAR_R * s}" height="{COLLAR_H * s}" class="collar" fill="var(--brass-soft)"/>')
        (a, b), (c, d) = Sd(y + PROP_R, PROP_Z), Sd(y - PROP_R, PROP_Z)
        out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="rodh"/>')

    def rect_side(bx, cls):
        _, _, y0, y1, z0, z1 = bx
        a, b = Sd(y1, z1)
        out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{(y1 - y0) * s:.1f}" height="{(z1 - z0) * s:.1f}" class="{cls}"/>')

    for bx, cls in ((AMP, "board"), (VL1, "board"), (GY, "board"), (BAT, "pan"), (MUX, "part"), (SPK, "part"), (REAR, "part"),
                    (SIDE_R, "part"), (CABIN, "part"), (SERVO, "part"), (CAM, "part")):
        rect_side(bx, cls)
    (a, b), (c, d) = Sd(HINGE_Y, HINGE_Z), Sd(HINGE_Y, LEVER_TOP)
    out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="brass"/>')
    (a, b), (c, d) = Sd(SERVO[3], LEVER_TOP), Sd(HINGE_Y, LEVER_TOP)
    out.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="brass"/>')
    a, b = Sd(0, 2.9)
    out.append(f'<text x="{a}" y="{b + 4}" class="s" text-anchor="middle">250 mAh</text>')
    a, b = Sd(0, 12.6)
    out.append(f'<text x="{a}" y="{b + 4}" class="s on" text-anchor="middle">XIAO + Sense</text>')
    a, b = Sd(STAR_Y + 3, STAR_Z + STAR_R)
    out.append(f'<rect x="{a}" y="{b}" width="{3 * s}" height="{2 * STAR_R * s}" class="lamp"/>')
    a, b = Sd(STAR_Y + 3 + LENS_LEN, STAR_Z + LENS_R)
    out.append(f'<rect x="{a}" y="{b}" width="{LENS_LEN * s}" height="{2 * LENS_R * s}" class="lamp"/>')

    def labs(y, z, tx, ty, text, anchor="start"):
        a, b = Sd(y, z)
        out.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{tx}" y2="{ty}" class="dim"/><text x="{tx + (4 if anchor == "start" else -4)}" y="{ty + 4}" class="t" text-anchor="{anchor}">{text}</text>')

    labs(0, 26.8, 905, 150, "servo; 34 mm tall")
    labs(13, 24, 600, 44, "6 mm lever on the hinge pin", "end")
    labs(-36, 11, 905, 230, "rear ranger, low")
    labs(-AXLE_Y, PROP_Z, 905, 270, "prop plane, 16.8 mm up")
    labs(20, 8.5, 640, 420, "multiplexer on the hood")
    labs(STAR_Y + 10, 7, 600, 390, "flashlight", "end")
    labs(-20, 10.7, 905, 380, "speaker, grille up")
    labs(-21, -2, 905, 420, "down ranger")
    labs(0, -2, 760, 470, "motion sensor")
    labs(20, -3, 660, 470, "amplifier", "end")
    labs(-AXLE_Y, MOTOR_Z0, 905, 330, "20 mm can; 7 mm skids")
    out.append('</g></svg>')
    return "\n".join(out)


CAP_3Q = ("Lift revision, drawn and approved 2026-11-10. Brass ladder, 7 × 20 mm motors in 7 mm brass collars on 50 mm axles, 40 mm grey four-blade props, "
          "7 mm skids. The three features together: the speaker and amplifier of the voice revision; the camera on a brass hinge at the cabin's front, "
          "tilted ±30° by a 1.5 g linear servo on the roof through a 6 mm lever; two black TOF400C rangers low beside the rails and one behind the tail bar, all under the prop plane, "
          "all five rangers behind a black multiplexer board across the hood, so no pin is spent. From the front right, props fitted, 3.5 px per mm; "
          "white pan, black cabin, bare brass, silver cans, nothing painted or covered. Generated by pages/gen/lift_views.py.")
CAP_PLAN = (f"Targets, not measurements. Motors at ±{AXLE_X} mm lateral and ±{AXLE_Y} mm fore-aft, {math.hypot(2 * AXLE_X, 2 * AXLE_Y):.0f} mm diagonal; "
            f"rails ±{RAIL_X} mm; {FOOT_W:.0f} × {FOOT_L:.0f} mm over the props; {HEIGHT:.0f} mm from the skids' feet to the servo. The side and rear rangers sit low, "
            "their tops 6 mm under the prop plane, so the discs may pass over them; nothing is in their fields. The multiplexer lies across the hood 8 mm under the prop plane. Dashed outlines are under the pan. Generated by pages/gen/lift_views.py.")


def main():
    html = PAGE.read_text(encoding="utf8")
    fig3 = f"<!-- lift-3q -->\n<figure>\n{three_quarter()}\n<figcaption>{CAP_3Q}</figcaption>\n</figure>\n<!-- /lift-3q -->"
    figp = f"<!-- lift-plan -->\n<figure>\n{plan_views()}\n<figcaption>{CAP_PLAN}</figcaption>\n</figure>\n<!-- /lift-plan -->"
    if "<!-- lift-3q -->" in html:
        html = re.sub(r"<!-- lift-3q -->.*?<!-- /lift-3q -->", lambda m: fig3, html, flags=re.S)
        html = re.sub(r"<!-- lift-plan -->.*?<!-- /lift-plan -->", lambda m: figp, html, flags=re.S)
    else:
        n3 = len(re.findall(r'<figure>\s*<svg viewBox="0 0 900 560" role="img" aria-label="Three-quarter view.*?</figure>', html, flags=re.S))
        n_p = len(re.findall(r'<figure>\s*<svg viewBox="0 0 900 470" role="img" aria-label="Top view and side view.*?</figure>', html, flags=re.S))
        assert n3 == 1 and n_p == 1, (n3, n_p)
        html = re.sub(r'<figure>\s*<svg viewBox="0 0 900 560" role="img" aria-label="Three-quarter view.*?</figure>', lambda m: fig3, html, flags=re.S)
        html = re.sub(r'<figure>\s*<svg viewBox="0 0 900 470" role="img" aria-label="Top view and side view.*?</figure>', lambda m: figp, html, flags=re.S)
    PAGE.write_text(html, encoding="utf8")
    print("wrote the two figures into", PAGE, PAGE.stat().st_size)
    print(f"  footprint {FOOT_W:.0f} x {FOOT_L:.0f} mm, height {HEIGHT:.1f} mm, diagonal {math.hypot(2 * AXLE_X, 2 * AXLE_Y):.1f} mm")
    # clearances the caption claims
    def dist(p, q):
        return math.hypot(p[0] - q[0], p[1] - q[1])
    print(f"  side and rear ranger tops under the prop plane: {PROP_Z - SIDE_R[5]:.1f} mm")
    print(f"  mux under the prop plane: {PROP_Z - MUX[5]:.1f} mm; can bottom over the skid feet: {MOTOR_Z0 + SKID:.1f} mm")


if __name__ == "__main__":
    main()
