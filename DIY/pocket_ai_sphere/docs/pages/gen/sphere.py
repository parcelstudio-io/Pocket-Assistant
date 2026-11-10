#!/usr/bin/env python3
"""Pocket AI Sphere: geometry, parts, pins, nets and tests in one place.

Writes docs/pages/sphere.html (the published page) and docs/DESIGN.md (the record).
Coordinates in mm: x right, y up, z toward the viewer (the face). Origin at the
sphere's centre, with the sphere at rest (pan 0, tilt 0). Run from anywhere:
python3 docs/pages/gen/sphere.py

History. 2026-10-29, Rev A: three great circles, then a 2V geodesic (120 struts) at the builder's
ask for the Las Vegas look, then back to three rings at his word ("only 2 or 3 lines other than the
shape"). 2026-11-10, Rev B: the first wiring sheet, every part in its own colour under the no-paint,
no-cover rule, four mistakes of Rev A fixed; approved as drawn that day. 2026-11-10, Rev C (this
file): the builder asked for a head that looks where the camera looks and moves to follow, with a
bigger screen and the equator ring gone. A gimbal inside does not fit a pocket sphere, so the whole
sphere nods and turns on a brass fork: the tilt servo is set into the vertical ring as its right hinge,
a pan servo stands on a brass coaster, the owned 1.54" colour screen is the face with the camera board
behind it, a top ring replaces the equator, and the family's charger-boost makes the 5 V the servos
need. The motion was shown first (pages/sphere-motion.html) and approved; this is step one for Rev C,
for approval. Rev A and Rev B are kept as sphere_revA.py.bak and sphere_revB.py.bak.
"""
import math, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.dirname(HERE)
DOCS = os.path.dirname(PAGES)

REV = "Rev C"
REV_DATE = "2026-11-10"
APPROVED_B = "2026-11-10"
APPROVED_C = "2026-11-10"      # the builder approved Rev C as drawn, after the motion study
ARTIFACT = "https://claude.ai/artifact/TyrrZEifUATc6Fea6JbwQ2"
MOTION = "https://claude.ai/artifact/HBsnWXT2xc8ydkkag35Lid"

# ------------------------------------------------------------------ the numbers (mm), sphere frame
R = 35.0                                        # sphere radius: 70 mm, a tennis ball is 67
CAP_R = 22.0                                    # the top and base rings: 44 mm
CAP_Y = math.sqrt(R*R - CAP_R*CAP_R)            # 27.2: the top ring at +27.2, the base ring at -27.2
PX = 17.0                                       # the two posts, just outside the screen's edges
PZ = math.sqrt(CAP_R**2 - PX**2)                # 14.0: where both cap rings pass x = +-17; the posts run straight between them
SCREEN = dict(x=16.5, y0=-22.0, y1=14.0, z0=15.0, z1=17.0, glass=20.0, gy0=-14.0, gy1=14.0, gx=14.0)   # 33 x 36 module, 28 x 28 glass, 8 mm tab below
XIAO = dict(x=10.5, y0=6.0, y1=24.0, z0=5.5, z1=14.5, lens_y=19.5)      # 21 x 18 board behind the screen's upper half, lens over its top edge
HINGE = dict(x0=17.7, x1=35.0, y0=-6.5, y1=13.5, z=4.15)               # the tilt servo in the ring at the right pole; horn out to x 38
STUB = 42.0                                                             # the left axle stub reaches x = -42
FORK = dict(x=39.5, bar=-39.0, top=12.0, tube=4.0)                      # 4 mm tube: two tines and a bar; the right tine reaches the horn's outer hole at y 12
PAN = dict(x0=-14.0, x1=6.0, z=4.15, y0=-62.3, y1=-45.0, horn1=-41.0)   # the pan servo standing on the coaster, shaft at x 0
COASTER = dict(r=37.5, y0=-70.3, y1=-62.3)                              # 75 x 8 mm brass coaster; the desk is at y -70.3
DESK_Y = COASTER["y0"]
HOLDER = dict(x=21.5, y0=-27.0, y1=-13.0, z0=-11.5, z1=6.5)
CELL = dict(y=-18.6, z=-2.5, r=8.3, x=17.0)                            # NL169, top at y -10.3
SPK = dict(x0=-12.0, x1=8.0, y0=-10.3, y1=-5.4, z0=-9.0, z1=4.0)       # lying across the cell on the tray walls, firing up
TOG = dict(x0=3.5, x1=13.5, y0=-21.5, y1=-8.5, z0=6.5, z1=14.5, ly=-15.0, lz=10.5, lever=26.0)
AMP = dict(x0=-12.5, x1=3.5, y0=-21.5, y1=-5.5, z0=12.0, z1=15.0)      # against the back of the screen, below the XIAO
CHG = dict(x0=-14.5, x1=14.5, y0=-25.0, y1=-6.0, z0=-17.0, z1=-12.0)   # charger-boost standing behind the tray, USB-C to the right
CAP220 = dict(x=-18.0, y0=-25.0, y1=-14.0, z=-14.5, r=3.2)
AHT = dict(x=12.7, y0=24.0, y1=25.6, z0=-20.0, z1=-2.0, hole_x=10.15)
BTN = dict(z=CAP_R-1.0)
LIM = dict(pan=60, tilt=25); FOV = dict(h=33, v=25); DEAD = 18

# ------------------------------------------------------------------ projection
def norm(v):
    l = math.sqrt(sum(a*a for a in v)); return tuple(a/l for a in v)
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dot3(a, b): return sum(x*y for x, y in zip(a, b))

class View:
    def __init__(self, az, el, S, W, H, ox=None, oy=None):
        az, el = math.radians(az), math.radians(el)
        self.c = (math.sin(az)*math.cos(el), math.sin(el), math.cos(az)*math.cos(el))
        up = (0, 1, 0) if abs(el) < math.radians(80) else (0, 0, -1)
        self.r = norm(cross(up, self.c)); self.u = norm(cross(self.c, self.r))
        self.S, self.W, self.H = S, W, H
        self.ox = W/2 if ox is None else ox; self.oy = H/2 if oy is None else oy
        self.light = norm((-0.35, 0.6, 0.72))
        self.els = []
    def P(self, p): return (self.ox + self.S*dot3(p, self.r), self.oy - self.S*dot3(p, self.u))
    def depth(self, p): return dot3(p, self.c)
    def add(self, d, s): self.els.append((d, s))
    @staticmethod
    def fmt(pts): return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    def seg(self, a, b, w, col, dfade=True, dlift=0.0):
        pa, pb = self.P(a), self.P(b); d = (self.depth(a)+self.depth(b))/2
        k = 1.0
        if dfade:
            k = 0.55 + 0.45*(d + R)/(2*R)
        op = 0.45 + 0.55*k if dfade else 1
        self.add(d+dlift, f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" '
                 f'stroke="{col}" stroke-width="{w*k:.2f}" stroke-opacity="{op:.2f}" stroke-linecap="round"/>')
    def arc3(self, center, radius, e1, e2, w, col, n=72, skip=None, dfade=True):
        pts = []
        for k in range(n):
            t = 2*math.pi*k/n
            pts.append((tuple(center[i] + radius*(math.cos(t)*e1[i] + math.sin(t)*e2[i]) for i in range(3)), math.degrees(t)))
        for k in range(n):
            (a, ta), (b, tb) = pts[k], pts[(k+1) % n]
            if skip and skip(ta): continue
            self.seg(a, b, w, col, dfade=dfade)
    def shade(self, nrm, base):
        k = 0.6 + 0.4*max(0.0, dot3(norm(nrm), self.light))
        return f'fill="{base}" style="filter:brightness({k:.2f})"'
    def box(self, x0, x1, y0, y1, z0, z1, base="var(--paper)", stroke="var(--ink)", w=1.1, dlift=0.0, op=1.0):
        faces = [((0, 0, 1), [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]),
                 ((0, 0, -1), [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]),
                 ((1, 0, 0), [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]),
                 ((-1, 0, 0), [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)]),
                 ((0, 1, 0), [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]),
                 ((0, -1, 0), [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)])]
        cen = ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)
        g = []
        for nrm, pts in faces:
            if dot3(nrm, self.c) > 1e-6:
                g.append(f'<polygon points="{self.fmt([self.P(p) for p in pts])}" {self.shade(nrm, base)} '
                         f'fill-opacity="{op}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/>')
        if not g:
            pts = faces[0][1]
            g.append(f'<polygon points="{self.fmt([self.P(p) for p in pts])}" fill="none" stroke="{stroke}" stroke-width="{w}"/>')
        self.add(self.depth(cen)+dlift, "".join(g))
    def flat(self, pts3, fill, stroke="none", w=0, dlift=0.0, op=1.0):
        cen = tuple(sum(p[i] for p in pts3)/len(pts3) for i in range(3))
        self.add(self.depth(cen)+dlift, f'<polygon points="{self.fmt([self.P(p) for p in pts3])}" fill="{fill}" '
                 f'fill-opacity="{op}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/>')
    @staticmethod
    def hull(pts):
        pts = sorted(set(pts))
        if len(pts) < 3: return pts
        def cr(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
        lo = []
        for p in pts:
            while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
            lo.append(p)
        up = []
        for p in reversed(pts):
            while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
            up.append(p)
        return lo[:-1]+up[:-1]
    def cylinder(self, c0, c1, radius, base, stroke, n=28, dlift=0.0):
        axis = norm(tuple(c1[i]-c0[i] for i in range(3)))
        a = (0, 1, 0) if abs(axis[1]) < 0.9 else (1, 0, 0)
        e1 = norm(cross(axis, a)); e2 = cross(axis, e1)
        def ring(c): return [tuple(c[i] + radius*(math.cos(t)*e1[i] + math.sin(t)*e2[i]) for i in range(3))
                             for t in [2*math.pi*k/n for k in range(n)]]
        b, t = ring(c0), ring(c1)
        pb = [self.P(p) for p in b]; pt = [self.P(p) for p in t]
        h = self.hull([(round(x, 2), round(y, 2)) for x, y in pb+pt])
        cen = tuple((c0[i]+c1[i])/2 for i in range(3))
        cap = pt if dot3(axis, self.c) > 0 else pb
        self.add(self.depth(cen)+dlift, f'<polygon points="{self.fmt(h)}" fill="{base}" stroke="{stroke}" stroke-width="1.1" stroke-linejoin="round"/>'
                 f'<polygon points="{self.fmt(cap)}" fill="{base}" style="filter:brightness(1.08)" stroke="{stroke}" stroke-width="1.1"/>')
    def render(self, caption, labels=(), aria="", margin=250):
        self.els.sort(key=lambda e: e[0])
        out = [f'<svg viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{html.escape(aria or caption)}">']
        out.append(f'<text x="18" y="24" font-size="13.5" font-weight="700" fill="var(--ink)">{html.escape(caption)}</text>')
        for d, s in self.els: out.append(s)
        for side in ("left", "right"):
            items = sorted([(self.P(p3)[1], p3, t) for sd, p3, t in labels
                            if (self.P(p3)[0] < self.ox) == (side == "left")])
            n = len(items)
            if not n: continue
            top, bot = 70, self.H-30
            step = (bot-top)/max(1, n-1)
            for i, (py, p3, t) in enumerate(items):
                x, y = self.P(p3); ys = top + i*step if n > 1 else (top+bot)/2
                xs = margin if side == "left" else self.W-margin
                xe = margin+10 if side == "left" else self.W-margin-10
                out.append(f'<path d="M{x:.1f},{y:.1f} L{xe:.1f},{ys:.1f} L{xs:.1f},{ys:.1f}" fill="none" stroke="var(--ink-2)" stroke-width="0.9"/>'
                           f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.3" fill="var(--ink-2)"/>')
                anchor = "end" if side == "left" else "start"
                tx = xs-5 if side == "left" else xs+5
                out.append(f'<text x="{tx}" y="{ys+4:.1f}" font-size="12" text-anchor="{anchor}" fill="var(--ink)">{html.escape(t)}</text>')
        out.append('</svg>')
        return "\n".join(out)

# ------------------------------------------------------------------ the model
ROD = "var(--brass)"; BRASS_HI = "var(--brass-hi)"; BLK = "var(--blk)"; BLO = "var(--blk-lo)"; BLUE = "var(--blue)"; CHR = "var(--chrome)"
WHITE = "var(--white)"; PXL = "var(--px)"; GLASS = "var(--glass)"

def build(v, stand=True):
    hinge_a0 = math.degrees(math.atan2(HINGE["y0"], math.sqrt(R*R-HINGE["y0"]**2)))   # -10.7
    hinge_a1 = math.degrees(math.atan2(HINGE["y1"], math.sqrt(R*R-HINGE["y1"]**2)))   # 22.7
    if stand:
        sh = [v.P((44*math.cos(t), DESK_Y-0.3, 44*math.sin(t))) for t in [2*math.pi*k/48 for k in range(48)]]
        v.add(-999, f'<polygon points="{v.fmt(sh)}" fill="var(--ink)" fill-opacity="0.08"/>')
        v.cylinder((0, COASTER["y0"], 0), (0, COASTER["y1"], 0), COASTER["r"], BRASS_HI, ROD, dlift=-500)
        v.box(PAN["x0"], PAN["x1"], PAN["y0"], PAN["y1"], -PAN["z"], PAN["z"], base=BLK, stroke=BLO)
        v.cylinder((0, PAN["y1"], 0), (0, PAN["horn1"], 0), 3.5, BLO, BLO)
        v.box(0, 12, PAN["horn1"]-1.5, PAN["horn1"], -2, 2, base=BLO, stroke=BLO, dlift=0.02)        # the horn's arm under the bar
        tw = FORK["tube"]
        v.seg((-FORK["x"], FORK["bar"], 0), (FORK["x"], FORK["bar"], 0), tw, ROD, dfade=False)
        v.seg((-FORK["x"], FORK["bar"], 0), (-FORK["x"], 2.0, 0), tw, ROD, dfade=False)
        v.seg((FORK["x"], FORK["bar"], 0), (FORK["x"], FORK["top"], 0), tw, ROD, dfade=False)
        v.cylinder((-FORK["x"]-2.5, 0, 0), (-FORK["x"]+2.5, 0, 0), 1.6, BRASS_HI, ROD, dlift=0.05)     # the 3 mm bushing across the left tine
        v.seg((FORK["x"], FORK["top"], 0), (36.5, FORK["top"], 0), 1.2, ROD, dfade=False, dlift=0.05)   # the 1.0 mm pin into the horn's outer hole
    else:
        sh = [v.P(p) for p in [(26*math.cos(t), -CAP_Y-0.5, 26*math.sin(t)) for t in [2*math.pi*k/48 for k in range(48)]]]
        v.add(-98, f'<polygon points="{v.fmt(sh)}" fill="var(--ink)" fill-opacity="0.08"/>')
    sil = [v.P(p) for p in [tuple(R*(math.cos(t)*v.r[i] + math.sin(t)*v.u[i]) for i in range(3)) for t in [2*math.pi*k/90 for k in range(90)]]]
    v.add(-99, f'<polygon points="{v.fmt(sil)}" fill="var(--paper)" stroke="var(--line)" stroke-width="1" stroke-dasharray="3 4"/>')
    # the three rings: the vertical ring leaves the right pole to the hinge servo
    v.arc3((0, 0, 0), R, (1, 0, 0), (0, 1, 0), 3.2, ROD, n=96, skip=lambda t: t < hinge_a1 or t > 360 + hinge_a0)
    v.arc3((0, CAP_Y, 0), CAP_R, (1, 0, 0), (0, 0, 1), 3.2, ROD)
    v.arc3((0, -CAP_Y, 0), CAP_R, (1, 0, 0), (0, 0, 1), 3.2, ROD)
    for x in (-PX, PX):
        v.seg((x, -CAP_Y, PZ), (x, CAP_Y, PZ), 2.0, ROD)
    # the hinge: tilt servo in the ring's gap, its horn out to the fork; the left stub
    v.box(HINGE["x0"], HINGE["x1"], HINGE["y0"], HINGE["y1"], -HINGE["z"], HINGE["z"], base=BLK, stroke=BLO)
    for y in (HINGE["y0"]-2.5, HINGE["y1"]+2.5):                                  # the mounting ears the ring ends enter
        v.box(HINGE["x1"]-4, HINGE["x1"]-1, y-1.2, y+1.2, -2.5, 2.5, base=BLK, stroke=BLO, dlift=0.02)
    v.cylinder((HINGE["x1"], 0, 0), (HINGE["x1"]+1.5, 0, 0), 3.0, BLO, BLO, dlift=0.03)
    v.box(HINGE["x1"]+1.5, HINGE["x1"]+3.0, -2, FORK["top"]+1, -2, 2, base=BLO, stroke=BLO, dlift=0.04)   # the horn arm, up to the pin
    v.seg((-R, 0, 0), (-STUB, 0, 0), 1.8, ROD, dfade=False)
    # the screen: black module, glass, eyes, tab with its lead
    s = SCREEN
    v.box(-s["x"], s["x"], s["y0"], s["y1"], s["z0"], s["z1"], base=BLK, stroke=BLO)
    v.box(-s["gx"], s["gx"], s["gy0"], s["gy1"], s["z1"], s["glass"], base=GLASS, stroke=BLO, dlift=0.5)
    for ex in (-6.5, 6.5):
        v.flat([(ex-4.2, -5.2, s["glass"]+0.05), (ex+4.2, -5.2, s["glass"]+0.05), (ex+4.2, 5.2, s["glass"]+0.05), (ex-4.2, 5.2, s["glass"]+0.05)], PXL, dlift=4.0)
    v.box(-5.5, 5.5, s["y0"]+1.5, s["y0"]+4.5, s["z1"], s["z1"]+2.0, base=WHITE, stroke=BLO, dlift=0.6)       # the PH2.0 socket on the tab
    # the XIAO stack behind the screen's upper half: lens and mic over the top edge, USB-C on the left
    xx = XIAO
    v.box(-xx["x"], xx["x"], xx["y0"], xx["y1"], xx["z0"], xx["z1"], base=BLK, stroke=BLO)
    v.box(-4, 4, xx["lens_y"]-4, xx["lens_y"]+4, xx["z1"], xx["z1"]+1.8, base=BLO, stroke=BLO, dlift=0.03)
    v.cylinder((0, xx["lens_y"], xx["z1"]+1.8), (0, xx["lens_y"], xx["z1"]+2.8), 2.2, GLASS, BLO, dlift=0.05)
    v.cylinder((7.5, xx["lens_y"]-1.5, xx["z1"]), (7.5, xx["lens_y"]-1.5, xx["z1"]+0.3), 0.6, GLASS, BLO, dlift=0.04)
    v.box(-xx["x"]-2, -xx["x"], 10, 14, xx["z0"]+0.5, xx["z0"]+3.5, base=CHR, stroke=BLO, dlift=0.03)
    # the tray on the base ring, the cell, the speaker on it
    h = HOLDER
    v.box(-h["x"], h["x"], h["y0"], h["y0"]+1.5, h["z0"], h["z1"], base=BLK, stroke=BLO)
    for x in (-h["x"], h["x"]-2):
        v.box(x, x+2, h["y0"], h["y1"], h["z0"], h["z1"], base=BLK, stroke=BLO)
    for z in (h["z0"], h["z1"]-1.2):
        v.box(-h["x"], h["x"], h["y0"], h["y1"]-4, z, z+1.2, base=BLK, stroke=BLO)
    c = CELL
    v.cylinder((-c["x"], c["y"], c["z"]), (c["x"], c["y"], c["z"]), c["r"], "var(--wrap)", BLO)
    v.cylinder((c["x"]-3.5, c["y"], c["z"]), (c["x"]-0.5, c["y"], c["z"]), c["r"]+0.1, "var(--yellow)", BLO, dlift=0.05)
    sp = SPK
    v.box(sp["x0"], sp["x1"], sp["y0"], sp["y1"], sp["z0"], sp["z1"], base=BLK, stroke=BLO, dlift=0.06)
    for x in (-8, -4, 0, 4):
        v.seg((x, sp["y1"]+0.1, sp["z0"]+2), (x, sp["y1"]+0.1, sp["z1"]-2), 0.8, "var(--ink-2)", dfade=False, dlift=0.08)
    # out of sight: the blue amplifier against the screen's back, the blue toggle body against the tray; the chrome lever out
    a = AMP; v.box(a["x0"], a["x1"], a["y0"], a["y1"], a["z0"], a["z1"], base=BLUE, stroke=BLO)
    t = TOG; v.box(t["x0"], t["x1"], t["y0"], t["y1"], t["z0"], t["z1"], base=BLUE, stroke=BLO)
    v.cylinder((t["x1"], t["ly"], t["lz"]), (t["x1"]+3, t["ly"], t["lz"]), 3.0, CHR, BLO, dlift=0.04)
    v.cylinder((t["x1"]+3, t["ly"], t["lz"]), (t["lever"], t["ly"]+1.5, t["lz"]), 1.2, CHR, BLO, dlift=0.05)
    # the charger-boost behind the tray, USB-C to the right; the 220 uF beside it
    g = CHG
    v.box(g["x0"], g["x1"], g["y0"], g["y1"], g["z0"], g["z1"], base=BLK, stroke=BLO)
    v.box(g["x1"], g["x1"]+1.5, g["y0"]+7, g["y0"]+10, g["z0"]+1, g["z0"]+4, base=CHR, stroke=BLO, dlift=0.03)
    cp = CAP220; v.cylinder((cp["x"], cp["y0"], cp["z"]), (cp["x"], cp["y1"], cp["z"]), cp["r"], BLK, BLO)
    # the sensor under the top ring at the back, on two hooks; the button cap on the ring's front
    q = AHT
    v.box(-q["x"], q["x"], q["y0"], q["y1"], q["z0"], q["z1"], base=BLK, stroke=BLO)
    v.box(-1.6, 1.6, q["y1"], q["y1"]+1.0, (q["z0"]+q["z1"])/2-1.6, (q["z0"]+q["z1"])/2+1.6, base=CHR, stroke=BLO, dlift=0.02)
    for x in (-q["hole_x"], q["hole_x"]):
        zr = -math.sqrt(CAP_R**2 - x*x)
        v.seg((x, CAP_Y, zr), (x, q["y1"]+0.3, zr), 1.6, ROD)
        v.seg((x, q["y1"]+0.3, zr), (x, q["y1"]+0.3, q["z0"]+2.5), 1.6, ROD)
        v.seg((x, q["y1"]+0.3, q["z0"]+2.5), (x, q["y0"]-1.5, q["z0"]+2.5), 1.6, ROD)
    v.box(-3, 3, CAP_Y-4.5, CAP_Y-0.5, BTN["z"]-3, BTN["z"]+3, base=BLK, stroke=BLO)
    v.cylinder((0, CAP_Y-0.5, BTN["z"]), (0, CAP_Y+3.0, BTN["z"]), 2.5, WHITE, "var(--ink-2)", dlift=0.05)
    # one white wire bundle down behind the boards
    v.seg((-7, XIAO["y0"], XIAO["z0"]-0.3), (-7, AMP["y1"]+0.5, XIAO["z0"]-0.3), 1.8, WHITE, dfade=False, dlift=0.01)

def make_views():
    out = {}
    v = View(24, 12, 3.4, 960, 760, oy=330)
    build(v)
    out["hero"] = v.render(f"The sphere on its fork, at rest. 3.4 px per mm. {REV}, {REV_DATE}.",
        labels=[("", (-9, 0, SCREEN["glass"]), "1.54\" colour screen, Crumb's spare"),
                ("", (0, XIAO["lens_y"], XIAO["z1"]+2.8), "camera and mic over the screen's top"),
                ("", (-12, 12, XIAO["z0"]+2), "USB-C on the left: flash"),
                ("", (HINGE["x1"]-2, 4, HINGE["z"]), "tilt servo: the right hinge"),
                ("", (-STUB+1, 0, 0), "left pole: brass stub in a bushing"),
                ("", (-FORK["x"], -20, 0), "4 mm brass tube fork; wires inside"),
                ("", (PAN["x0"]+2, -52, PAN["z"]), "pan servo on the coaster"),
                ("", (COASTER["r"]*0.7, COASTER["y1"], COASTER["r"]*0.7), "brass coaster, 75 mm"),
                ("", (0, CAP_Y+3, BTN["z"]), "button cap on the top ring"),
                ("", (-q_x(), AHT["y1"], -10), "AHT20 on hooks under the top ring"),
                ("", (CELL["x"]-2, CELL["y"], CELL["z"]+8), "16340 cell in its tray: the ballast"),
                ("", (SPK["x1"]-3, SPK["y1"], SPK["z1"]-3), "speaker on the cell, firing up"),
                ("", (CHG["x1"], CHG["y1"]-3, CHG["z0"]+2), "charger-boost behind the tray"),
                ("", (TOG["lever"], TOG["ly"]+1.5, TOG["lz"]), "power lever: body behind the screen"),
                ("", (-PX, -5, PZ), "posts outside the screen's edges"),
                ("", (0, -CAP_Y, CAP_R), "base ring; top ring mirrors it")],
        aria="Three-quarter view of the 70 mm brass sphere on a brass fork over a coaster: the colour screen in the open front, the camera board above it, the tilt servo as the right hinge, the pan servo on the coaster")
    v = View(0, 0, 3.0, 440, 520, oy=230); build(v)
    out["front"] = v.render("From the front: the face in the open window.")
    v = View(90, 0, 3.0, 440, 520, oy=230); build(v)
    out["side"] = v.render("From the right: the hinge, the lever, the stack front to back.")
    v = View(180, 0, 3.0, 440, 520, oy=230); build(v)
    out["back"] = v.render("From behind: cell, charger, sensor; nothing blue.")
    return out

def q_x(): return AHT["x"]

# ------------------------------------------------------------------ the data
L = {
    "xiao": "https://www.amazon.com/dp/B0C69FFVHH",
    "xiao_wiki": "https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/",
    "screen": "https://www.amazon.com/dp/B0HGLQZK3P",
    "aht20": "https://www.adafruit.com/product/4566",
    "amp": "https://www.amazon.com/dp/B0CDWXZZCH",
    "spk": "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309",
    "cell": "https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery",
    "holder": "https://www.amazon.com/dp/B0CRGK889F",
    "toggle": "https://www.amazon.com/dp/B0CZ6XZ2P9",
    "button": "https://www.amazon.com/dp/B0FHW6HMG4",
    "kits": "https://www.amazon.com/dp/B0F4P352BB",
    "rod15": "https://www.amazon.com/dp/B005WPAW9M",
    "rod10": "https://www.amazon.com/dp/B005WPB7YG",
    "tubes": "https://www.amazon.com/dp/B0F2FKLC2N",
    "wire": "https://www.amazon.com/dp/B073RDGTPB",
    "glue": "https://www.amazon.com/s?k=b-7000+glue",
    "servo": "https://www.pololu.com/product/3420",
    "chg": "https://www.digikey.com/en/products/detail/adafruit-industries-llc/6106/25805552",
    "coaster": "https://www.amazon.com/dp/B0D9DMK3L7",
    "jst": "https://www.amazon.com/dp/B0F6T4LKDG",
    "charger": "https://www.amazon.com/s?k=nitecore+ui1",
}
PARTS = [  # (qty, part, link text, url, status, colour as sold, why)
    ("2", "FEETECH FS0307 sub-micro servo", "DigiKey 2183-3420-ND, shipped by Pololu, $10.21 each; not on Amazon", L["servo"], "TO BUY", "black",
     "Pan and tilt. 20 x 8.3 x 17.3 mm, 4.4 g, 0.5 kg-cm at 4.8 V, 0.1 s per 60°, 120° on 900-2100 µs pulses, 3.3 V signal, horns and screws in the bag. Rated 4.8-6 V, so both run on the charger-boost's 5 V. One is set into the vertical ring as the sphere's right hinge; the other stands on the coaster and turns the fork."),
    ("1", "Adafruit bq25185 charger-boost", "DigiKey 1528-6106-ND, $8.95; Amazon has none", L["chg"], "TO BUY", "black",
     "The family's power board, as on Crumb and the rover: charges the cell at 500 mA from its USB-C (cut the current jumper) and makes 5 V at up to 1 A for the two servos and the amp. 29 x 19 x 5 mm plus a 6 mm JST. Standing behind the tray, USB-C out to the right. The satellite's owned one could be reassigned instead."),
    ("1", "Brass coaster, 75 x 8 mm", "Amazon, TOGGOOL 3 inch, $12.99; in the cart 2026-11-10", L["coaster"], "TO BUY", "brass",
     "The base, the family's: a thin brass top over a hollow, 80 g. The pan servo stands glued on its top. Light alone (it would tip at 28°), so about 150 g of steel washers go into the hollow as the satellite does; measure the hollow on arrival. The satellite's own was in the 11-10 checkout."),
    ("1", "Seeed XIAO ESP32-S3 Sense", "the pair ordered 2026-10-27, expected by 11-15", L["xiao"], "in the mail", "black boards, silver shield",
     "The brain, the camera and the microphone, behind the screen's upper half with the lens 5.5 mm over its top edge. Cut jumper J3 on the Sense board first: it frees D8-D10 from the SD slot for the screen's clock and data and the tilt servo. BAT pads from the toggle, as on the camera tower."),
    ("1", "Hosyond 1.54\" IPS, ST7789, 240 x 240", "owned, two spare in Crumb's box", L["screen"], "owned", "black glass; board colour to check",
     "The face, 28 x 28 mm of picture on a 33 x 36 mm module with an 8-pin PH2.0 lead (GND VCC SCL SDA RES DC CS BLK). 4-wire SPI as on Crumb: CS to GND, RST pulled up, backlight tied on. Open Crumb's box and look at the board: if it is not black, its 8 mm tab shows under the glass, and a black-board 1.54\" is a Rev D question. Glued by its side edges to the two posts."),
    ("1", "Adafruit AHT20 temperature + humidity", "owned x5, three spare", L["aht20"], "owned", "black",
     "The weather sensor, flat under the top ring at the back on two 1.0 mm hooks through its mounting holes (20.3 x 12.7 mm pattern). I2C 0x38, the only thing on the bus now. Header VIN, GND, SCL, SDA; the QT sockets stay empty."),
    ("1", "HiLetgo MAX98357A amplifier", "owned x12", L["amp"], "owned", "blue, so out of sight",
     "Runs on the 5 V rail now. SD left open (the breakout's own pull-up turns it on, (L+R)/2 mix), as the rover does: the sphere has no pin to spare for it; GAIN open (9 dB); volume cap 65. Blue, so it stands against the back of the screen below the camera board, where the screen hides it from the front and the tray, the cell, the speaker and the charger hide it from behind."),
    ("1", "Same Sky CES-20134-088PM speaker", "owned x6", L["spk"], "owned", "black",
     "Sealed 20 x 13 x 4.9 mm, 8 ohm, 0.8 W. Lies across the cell on the tray's walls, taped, firing up through the open top. Neither lead to ground."),
    ("1", "Nitecore NL169 16340, protected", "owned x13", L["cell"], "owned", "black and yellow wrap",
     "950 mAh, 2 A protection, button top, 20 g on the floor of the sphere: the ballast that keeps the centre of mass 7 mm under the tilt axis, so the sphere levels itself with the power off. Its yellow lettering shows from the sides: the one off-palette thing in view."),
    ("1", "ACEIRMC 16340 / CR123A holder with leads", "owned x10", L["holder"], "owned", "black",
     "43 x 18 x 14 mm tray across the base ring, tied down with two white wire ties. The cell stands 2.6 mm proud of its walls. Meter that red is +."),
    ("1", "Ferwooh MTS-102 toggle switch", "owned x20", L["toggle"], "owned", "blue body, chrome lever",
     "Power switch in the cell's + lead, middle lug and one outer lug. Body against the tray's front wall behind the screen's right half; only the chrome lever shows, out to the right of the screen's lower edge. Lever forward is on. Off is off: nothing but the cell's own protection stays on."),
    ("1", "QTEATAK tactile button, white cap", "owned x420", L["button"], "owned", "black body, white cap",
     "The action button, glued under the top ring at the front with its white cap up: press the top of the sphere."),
    ("1 + 1 + 2", "R1 10 kΩ; C1 1 µF; 220 µF", "LuminologyPro, BOJACK, ALLECIN kits", L["kits"], "owned", "tan, black",
     "R1 pulls the screen's RST to 3V3 with C1 to GND: a power-on reset, then software resets, as on Crumb. 220 µF across the 5 V rail at the amp."),
    ("1", "JST-PH 2.0 mm pigtail", "owned, daier 20-pair set", L["jst"], "owned", "white",
     "From the toggle into the charger-boost's BAT socket. Polarity by meter, not by wire colour."),
    ("2 rods", "K&S 1.5 mm brass rod, 300 mm", "owned (K&S #9862 5-packs)", L["rod15"], "owned", "brass",
     "One rod: the vertical ring, 200 mm (220 less the hinge's gap). One rod: the top and base rings, 138 mm each, 276 of 300. Plus the 7 mm left stub from the offcut."),
    ("1 rod", "K&S 1.0 mm brass rod, 300 mm", "owned (K&S #9861 5-packs)", L["rod10"], "owned", "brass",
     "Two posts (54 mm each, base ring to top ring), two 8 mm hooks for the sensor, the 5 mm pin into the tilt horn, a keeper round the bar: 135 mm."),
    ("1 + 1", "Brass tube, 4 mm and 3 mm, from the 2-7 mm set", "owned (three sets, 200 mm each)", L["tubes"], "owned", "brass",
     "The fork: two 4 mm tines (41 and 51 mm) and a 79 mm bar, lapped and soldered, no bends; the three pan-servo wires run inside the left tine. 8 mm of 3 mm tube across the left tine's top is the bushing the stub turns in."),
    ("", "26 AWG and 30 AWG silicone wire, white; Kapton; 2.54 mm header pins", "owned (TUOFENG, CBAZY kits)", L["wire"], "owned", "white",
     "Every wire white: 26 AWG for the cell, BAT+ and the 5 V rail, 30 AWG for the rest. The servos keep their own leads and plug onto 3-pin headers. Kapton between the camera board and the screen's back."),
    ("", "B-7000 glue", "owned", L["glue"], "owned", "clear",
     "The screen's edges to the posts, the camera board to the screen's back, the ring's ends into the hinge servo's ears, the pan servo to the coaster, the bar to the pan horn. Hot glue lets go of cold brass; B-7000 does not."),
    ("1", "External 16340 charger (Nitecore UI1 or XTAR VC2)", "optional, about $10-15", L["charger"], "optional", "",
     "Not needed now: the charger-boost does 2.2 h through its own USB-C."),
]

PINS = [  # header, gpio, net, job
    ("D0", "1", "BCLK", "amp BCLK"), ("D1", "2", "LRC", "amp LRC"), ("D2", "3", "DIN", "amp DIN"),
    ("D3", "4", "PAN", "pan servo signal, 50 Hz, 900-2100 µs, three wires down the left tine"),
    ("D4", "5", "SDA", "AHT20 SDA"), ("D5", "6", "SCL", "AHT20 SCL"),
    ("D6", "43", "DC", "screen data/command. UART0 TX: the ROM prints here at boot, harmless on a screen not yet initialised (Crumb's choice)"),
    ("D7", "44", "BTN", "action button to GND, internal pull-up. UART0 RX, an input at boot"),
    ("D8", "7", "SCK", "screen clock (J3 cut: the SD slot's pin, freed)"), ("D9", "8", "MOSI", "screen data (J3 cut)"),
    ("D10", "9", "TILT", "tilt servo signal, the hinge (J3 cut)"),
    ("3V3", "", "3V3", "screen VCC and BLK, AHT20 VIN, R1: about 45 mA of the regulator's 700"),
    ("GND pin", "", "GND", "screen GND and CS, AHT20 GND, button, C1 (signal grounds)"),
    ("BAT+ pad (back)", "", "BAT+", "from the toggle, with the charger-boost's BAT"),
    ("BAT− pad (back)", "", "GND", "the holder's − lead, the star"),
    ("5V pin", "", "", "USB VBUS only: nothing, ever"),
    ("camera, mic", "10-18, 38-40, 47, 48; 41, 42", "", "inside the Sense board; not on the sheet"),
]

NETS = [  # (net, from, to, wire, why)
    ("BAT+", "holder + lead (red)", "toggle middle lug; toggle outer lug → XIAO BAT+ pad and the charger-boost BAT (+) through a JST pigtail", "26 AWG white", "3.0-4.2 V from the cell when the toggle is on. The XIAO runs on it as on the camera tower; the charger-boost takes it in and gives 5 V out. Off is off: only the cell's own protection board stays live."),
    ("5V", "charger-boost 5V pad (EN tied to BAT+, so the boost runs whenever the toggle is on)", "amp VIN, 220 µF +, pan servo + (down the left tine), tilt servo +", "26 AWG white; the servos' own leads", "The one rail the cell cannot be: the servos are rated 4.8-6 V. 1 A available; the two servos stall at 0.4 A each, so the firmware never slews both from a stop at once, and waits for boot before the first move (the boost will not start under more than 200 mA)."),
    ("GND", "holder − lead (black), the star", "XIAO BAT− pad, charger-boost BAT (−) and G, amp GND, 220 µF −, both servos −; the XIAO's GND header pin feeds the screen GND and CS, AHT20 GND, the button, C1", "26 AWG white for the power returns, 30 AWG for the signal grounds", "One ground, one star at the holder. The frame is no conductor: nothing is soldered to brass, and the servo wires inside the tine are insulated silicone."),
    ("3V3", "XIAO 3V3 pin", "screen VCC and BLK, AHT20 VIN, R1 top", "30 AWG white", "The screen's backlight is tied on (no pin to spare for dimming); its logic and the sensor are the only loads on the XIAO's regulator besides itself and the camera."),
    ("SCK / MOSI / DC", "D8 (GPIO7) / D9 (GPIO8) / D6 (GPIO43)", "screen SCL / SDA / DC", "30 AWG white, 60 mm, on the head", "4-wire SPI at 26 MHz through the S3's pin matrix, Crumb's driver. CS to GND (the only SPI device); RST through R1 10 kΩ to 3V3 with C1 1 µF to GND."),
    ("SDA / SCL", "D4 (GPIO5) / D5 (GPIO6)", "AHT20 SDA / SCL", "30 AWG white", "The XIAO's hardware I2C pins; one device, 0x38, with its own pull-ups."),
    ("BCLK / LRC / DIN", "D0 / D1 / D2 (GPIO1 / 2 / 3)", "amp BCLK / LRC / DIN", "30 AWG white", "I2S out only; the microphone is the PDM mic on the Sense board (GPIO41/42). The amp's SD stays open, on, as the rover's: with eleven pins for thirteen jobs the shutdown line and backlight dimming were the two let go."),
    ("PAN / TILT", "D3 (GPIO4) / D10 (GPIO9)", "pan servo signal / tilt servo signal", "30 AWG white; the servos' own leads on 3-pin headers", "50 Hz pulses, 900 to 2100 µs for 120°; the firmware uses ±60° of pan and ±25° of tilt, eased, never a step."),
    ("BTN", "D7 (GPIO44)", "button → GND", "30 AWG white", "Short press talks, long press resets Wi-Fi."),
    ("SPK", "amp OUT+ / OUT−", "speaker", "its own 60 mm leads", "Neither lead is ground. Never clip a scope ground to either."),
    ("across the hinge", "nothing", "", "", "The tilt servo is inside the sphere; its horn is what the fork holds. No wire crosses the tilt axis."),
    ("down the left tine", "5V, GND, PAN", "the pan servo's lead at the foot", "three 30 AWG white, inside the 4 mm tube", "They leave the sphere beside the left bushing in a loose loop that bends ±25° with the tilt, run inside the tine, and twist ±60° at the foot with the pan."),
]

CUTS = [
    ("Vertical ring", "1.5 mm rod", "200 mm", "A 70 mm circle less the hinge's gap: bend around a 66 mm can, and cut the ends so they enter the tilt servo's two mounting ears at the right pole (y −9 and +16). Glue them in; the servo is now part of the ring."),
    ("Top ring and base ring", "1.5 mm rod", "138 mm each", "22 mm radius, around a 42 mm jar, lap-join 8 mm. Each crosses the vertical ring at the front and the back: two solder joints per ring. The base ring carries the tray, the top ring the button and the sensor."),
    ("Posts x2", "1.0 mm rod", "54 mm each", "Straight between the two cap rings at x = ±17, 14 mm forward of the centre: just outside the screen's edges. The screen's side edges glue to them."),
    ("Left stub", "1.5 mm rod", "7 mm", "Soldered along the ring's outside at the left pole, pointing out: the axle the left tine's bushing turns on."),
    ("Sensor hooks x2", "1.0 mm rod", "8 mm each", "Down from the top ring at x = ±10.15, forward 2.5 mm, down through the sensor's back holes, bent under."),
    ("Fork tines x2", "4 mm tube", "41 mm left, 51 mm right", "Vertical at x = ±39.5. The left ends at y 2 with the 3 mm bushing soldered across its top at y 0; the right rises to y 12 and carries the 1.0 mm pin that enters the tilt horn's outer hole."),
    ("Fork bar", "4 mm tube", "79 mm", "Across the tines' bottoms at y −39, lapped and soldered to each, 2 mm clear of the sphere's bottom. It sits on the pan horn's arm, glued, with a turn of 1.0 mm rod through the horn's hole as a keeper."),
    ("Bushing", "3 mm tube", "8 mm", "Across the left tine's top, soldered: the stub turns in its 2 mm bore."),
]

TESTS = [
    ("1 · XIAO alone", "Cut J3 on the Sense board. USB-C to the laptop; flash Seeed's CameraWebServer example (PSRAM on); join its Wi-Fi page.", "Live video in the browser. Camera, Wi-Fi, PSRAM and the USB port proven."),
    ("2 · Microphone", "Flash Seeed's PDM record example; speak at the board.", "A waveform that follows your voice in the serial plotter."),
    ("3 · Screen", "Breadboard: VCC and BLK to 3V3, GND and CS to GND, SCL-D8, SDA-D9, DC-D6, RES through 10 k to 3V3 with 1 µF to GND. Crumb's esp_lcd ST7789 test pattern.", "A full-screen pattern at 26 MHz; two white eyes on black."),
    ("4 · AHT20", "VIN-3V3, GND, SDA-D4, SCL-D5. I2C scan, then read.", "Scan shows 0x38; room temperature; humidity jumps when you breathe on it."),
    ("5 · Amp + speaker", "Amp VIN from the bench supply at 5 V, GND, BCLK-D0, LRC-D1, DIN-D2, SD open; speaker on OUT±. A 440 Hz tone at volume 65.", "A clean tone. Nothing else wired to the speaker."),
    ("6 · Charger-boost", "Cell holder through the toggle into BAT; EN to BAT+; nothing on 5 V yet. Toggle on.", "5.0 V on the 5V pad. USB-C in: about 500 mA into the cell (meter in series), the LED on, the board cooler than 45 °C by touch."),
    ("7 · Servos on the 5 V rail", "Both servos' + and − on the charger-boost's 5 V and G, signals from D3 and D10. Sweep each 900 to 2100 µs slowly, then both.", "120° each, no jitter at rest; the 5 V rail stays above 4.8 V while one moves (scope or meter on min hold)."),
    ("8 · Button", "D7 to GND through the button; internal pull-up.", "A press prints once after a 30 ms debounce."),
    ("9 · All together on the breadboard", "Everything from 1-8 at once for an hour, camera streaming, a servo sweeping every ten seconds.", "No brownout, no reboot, XIAO warm not hot. Only now bend brass."),
]

BUILD = [
    "Bench-test every part first (the nine steps). Nothing goes near brass untested.",
    "Look at the screen's board in Crumb's box and note its colour; measure the servo's shaft offset and the horn's holes with the calipers.",
    "Bend the vertical ring and the two cap rings; lap-join the cap rings. Check them on 70 mm and 44 mm circles drawn with a compass.",
    "Glue the vertical ring's two ends into the tilt servo's ears, shaft pointing out: the hinge. Solder the top and base rings to the vertical ring at front and back, then the two posts between them at x = ±17. Harris flux, baking soda, IPA, as on the first frame. Solder the left stub at the left pole. Meter: one piece of metal, nothing else on it.",
    "Wire the head on the bench, in white: the screen's eight, the camera board's BAT pair, the button's two, the amp's five, the sensor's four, the two servo leads to 3-pin headers, the charger's JST and 5 V pair.",
    "Glue the camera board to the back of the screen with Kapton between, lens 5.5 mm over the top edge; glue the screen's side edges to the posts, 22 mm below the centre. Lay the wire bundle down behind the boards.",
    "Tape the toggle to the tray's front wall, lever out to the right, and the amp to the back of the screen below the camera board. Tray onto the base ring with two white ties; speaker across the tray's walls over the cell, grille up; the charger standing behind the tray, USB-C to the right, with the 220 µF; the sensor onto its hooks; the button under the top ring at the front, cap up.",
    "The fork: cut the two tines and the bar from the 4 mm tube, solder the bushing across the left tine's top, lap and solder the bar to both tines. Thread the three pan wires down inside the left tine first.",
    "Hang the sphere: the stub into the bushing, the pin through the right tine's top into the tilt horn's outer hole. Press the horn onto the servo with the sphere level and the servo at its middle pulse, then its screw.",
    "The stand: glue the pan servo standing on the coaster's centre, horn arm forward; glue the bar onto the arm with the keeper. Steel washers into the coaster's hollow, pad back on. Plug the three wires onto the pan servo's lead.",
    "Meter frame-to-every-net before the cell goes in, then after every solder session. First power-up on the charger's USB-C with the toggle ON and the servos unplugged, then the servos, then the cell alone. Run the test-9 sketch again on the fork, with the motion study's dead band and limits.",
]

MASS = [("Cell + tray", 23), ("1.54\" screen", 12), ("XIAO ESP32-S3 Sense", 8), ("Tilt servo", 4.4), ("Charger-boost", 4), ("Speaker", 3.5), ("Amp + 220 µF", 3),
        ("Toggle + button", 4), ("AHT20", 1.5), ("1.5 mm rod, 483 mm", 7.2), ("1.0 mm rod, 135 mm", 0.9),
        ("Fork: 4 mm tube, 171 mm, and the bushing", 8.0), ("Pan servo", 4.4), ("Brass coaster", 80), ("Steel in the coaster (optional)", 150)]
SPHERE_MASS = sum(m for p, m in MASS if p not in ("Fork: 4 mm tube, 171 mm, and the bushing", "Pan servo", "Brass coaster", "Steel in the coaster (optional)"))

POWER = [  # mode, mA from the cell, short, long
    ("camera streaming, talking, head following", 320, "about 2.7 h", "about 2.7 h on 90 % of 950 mAh: 250 mA for the XIAO, screen and amp, plus the two servos through the boost, idle most of the time and moving a few hundred milliseconds at a go"),
    ("idle on Wi-Fi, screen on, servos holding", 140, "about 6 h", "about 6 h"),
    ("deep sleep, toggle on", 8, "about 4 days", "about 4 days: the boost's own quiescent current is most of it; the toggle off is months"),
    ("charging: USB-C into the charger-boost, toggle ON", 500, "about 2.2 h from empty", "about 2.2 h from empty at 500 mA (the current jumper cut), the cell watched the first time; the XIAO's own 100 mA charger on its USB-C still works as a fallback, with the other port empty"),
    ("peak: both servos stalled", 1000, "never asked for", "0.8 A at 5 V from the boost's 1 A: the firmware never starts both from rest at once"),
]

COLOURS = [
    ("Brass rings, posts, stub, fork, coaster", "brass", "the whole outline and the stand", "brass, its own colour"),
    ("1.54\" screen", "black glass; board colour to check in Crumb's box", "the face, on the posts", "the glass and the white eyes; the 8 mm tab under the glass shows whatever colour the board is"),
    ("XIAO ESP32-S3 Sense", "black boards, silver shield", "behind the screen, lens over its top", "black"),
    ("Tilt servo", "black", "set into the ring at the right pole", "black: the hinge knuckle"),
    ("Pan servo", "black", "standing on the coaster", "black: the neck"),
    ("Charger-boost", "black", "behind the tray, USB-C to the right", "black"),
    ("AHT20", "black", "under the top ring at the back", "black, edge-on from the front"),
    ("Amplifier (HiLetgo)", "blue; Adafruit's is blue too", "against the screen's back, below the camera board", "nothing from the front or the back; a 3 mm edge from the sides"),
    ("Toggle (MTS-102)", "blue body, chrome lever", "against the tray wall behind the screen", "the chrome lever; its end face from the right, behind the hinge"),
    ("Speaker", "black", "lying across the cell", "black"),
    ("Cell (NL169)", "black and yellow wrap", "in the tray on the floor", "yellow lettering from the sides; the one off-palette thing in view"),
    ("Button", "black body, white cap", "under the top ring, front", "the white cap"),
    ("Wires", "white", "one bundle behind the boards; three inside the left tine", "a white line"),
]

CHANGES = [
    "**The whole sphere is the head.** The builder asked for eyes that face where the camera faces and move to follow (2026-11-10). A pan-tilt gimbal inside does not fit: the screen with the camera board is 33 x 48 mm, a pan servo stands 21 mm under it and the tray takes 14, more than an 80 mm sphere, and the swept head needs clear space around it. So the sphere itself nods and turns, the screen and the camera rigid to each other, and nothing swings inside. Shown first on the motion page and approved.",
    "**The tilt servo is the right hinge.** The vertical ring's two ends enter the servo's mounting ears at the right pole, its shaft points out along the sphere's axis, and the fork holds its horn still: the servo turns itself and the sphere around it. The left pole is a brass stub in a 3 mm bushing. No wire crosses the hinge.",
    "**A fork and a coaster.** Two 4 mm brass tube tines and a bar, lapped and soldered, rise from a pan servo standing on the family's brass coaster. The three wires to that servo run inside the left tine. 105 mm tall on the desk.",
    "**The equator is gone; a top ring mirrors the base ring**, as asked. The front is one open window from the base ring to the top ring.",
    "**The owned 1.54\" colour screen is the face**, the builder's pick: 28 mm of glass against the 0.96\" OLED's 22 x 11, and the OLED's board was blue. The camera board sits behind its upper half with the lens over the top edge, so the eyes and the camera look the same way by construction; the pupils are drawn where the camera sees you.",
    "**A charger-boost comes in.** The servos are rated 4.8-6 V and will not run on the cell, so the family's bq25185 board makes 5 V for them and the amp, and charges the cell at 500 mA, five times faster than the XIAO.",
    "**Two pins were let go.** Eleven pins carry thirteen jobs, so the amp's shutdown line is left open (on, as the rover's) and the screen's backlight is tied on, undimmed. A Rev D could return either with an I2C expander.",
    "**The posts moved out to x = ±17**, just outside the new screen's edges, running straight between the two cap rings, so no tie to any equator is needed and the screen glues to them by its edges.",
    "**Three lines to buy:** two servos, the charger-boost and a coaster, about $60 landed. Rev B had none.",
]

# ------------------------------------------------------------------ the wiring sheet
SW, SH = 1360, 1040

def esc(t): return str(t).replace("&", "&amp;").replace("<", "&lt;")
def T(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'
def dot(x, y, r=6): return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="joint"/>'

class Router:
    """Orthogonal polylines; a segment hops (semicircle) over every earlier segment of a different net it crosses.
    Same-net crossings are joints and get no hop. Draw rails and the busiest lanes first. Copied from the camera
    Pocket AI's wiring_board.py so this project stands on its own."""
    R = 8
    def __init__(self):
        self.segs = []; self.pins = []
    def pin(self, x, y, net): self.pins.append((x, y, net))
    def wire(self, pts, cls="rod", net=None):
        path = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            horiz, vert = abs(y0 - y1) < 0.01, abs(x0 - x1) < 0.01
            hops = []
            if horiz:
                lo, hi = min(x0, x1), max(x0, x1)
                for (a0, b0, a1, b1, n) in self.segs:
                    if n == net or abs(a0 - a1) > 0.01: continue
                    if lo + self.R < a0 < hi - self.R and min(b0, b1) + 0.5 < y0 < max(b0, b1) - 0.5: hops.append(a0)
                sgn = 1 if x1 > x0 else -1
                for rx in sorted(set(hops), reverse=(sgn < 0)):
                    path += f" L{rx - self.R * sgn:.1f},{y0:.1f} A{self.R},{self.R} 0 0 {1 if sgn > 0 else 0} {rx + self.R * sgn:.1f},{y0:.1f}"
            elif vert:
                lo, hi = min(y0, y1), max(y0, y1)
                for (a0, b0, a1, b1, n) in self.segs:
                    if n == net or abs(b0 - b1) > 0.01: continue
                    if lo + self.R < b0 < hi - self.R and min(a0, a1) + 0.5 < x0 < max(a0, a1) - 0.5: hops.append(b0)
                sgn = 1 if y1 > y0 else -1
                for ry in sorted(set(hops), reverse=(sgn < 0)):
                    path += f" L{x0:.1f},{ry - self.R * sgn:.1f} A{self.R},{self.R} 0 0 {0 if sgn > 0 else 1} {x0:.1f},{ry + self.R * sgn:.1f}"
            path += f" L{x1:.1f},{y1:.1f}"
            self.segs.append((x0, y0, x1, y1, net))
        return f'<path d="{path}" class="{cls}"/>'
    def check(self, min_pin=14, min_lane=14):
        bad = []
        for (x0, y0, x1, y1, n) in self.segs:
            for (px, py, pn) in self.pins:
                if pn == n: continue
                if abs(x0 - x1) < 0.01 and min(y0, y1) - 2 <= py <= max(y0, y1) + 2 and abs(px - x0) < min_pin:
                    bad.append(f"vertical {n} at x={x0} passes {abs(px-x0):.0f}px from pin ({px},{py}) of {pn}")
                if abs(y0 - y1) < 0.01 and min(x0, x1) - 2 <= px <= max(x0, x1) + 2 and abs(py - y0) < min_pin:
                    bad.append(f"horizontal {n} at y={y0} passes {abs(py-y0):.0f}px from pin ({px},{py}) of {pn}")
        crossings = 0
        for i, (x0, y0, x1, y1, n) in enumerate(self.segs):
            for (a0, b0, a1, b1, m) in self.segs[:i]:
                if m == n: continue
                v1, v2 = abs(x0 - x1) < 0.01, abs(a0 - a1) < 0.01
                if v1 and v2 and abs(x0 - a0) < min_lane and min(y0, y1) < max(b0, b1) and max(y0, y1) > min(b0, b1):
                    bad.append(f"verticals {n} x={x0} and {m} x={a0} run {abs(x0-a0):.0f}px apart")
                if (not v1) and (not v2) and abs(y0 - b0) < min_lane and min(x0, x1) < max(a0, a1) and max(x0, x1) > min(a0, a1):
                    bad.append(f"horizontals {n} y={y0} and {m} y={b0} run {abs(y0-b0):.0f}px apart")
                if v1 != v2:
                    vx, vy0, vy1, hx0, hx1, hy = (x0, y0, y1, a0, a1, b0) if v1 else (a0, b0, b1, x0, x1, y0)
                    if min(hx0, hx1) + 0.5 < vx < max(hx0, hx1) - 0.5 and min(vy0, vy1) + 0.5 < hy < max(vy0, vy1) - 0.5:
                        crossings += 1
        return bad, crossings

def block(x, y, w, h, title, sub=None, cls="part", sub2=None, ty=24):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>', T(x + w / 2, y + ty, title, "title", "middle")]
    if sub: o.append(T(x + w / 2, y + ty + 18, sub, "sub", "middle"))
    if sub2: o.append(T(x + w / 2, y + ty + 34, sub2, "sub", "middle"))
    return "".join(o)

def pin(rt, x, y, name, side, net, fn=None, fnx=None):
    rt.pin(x, y, net)
    o = [f'<circle cx="{x}" cy="{y}" r="4.5" class="pinend"/>']
    if side == "R":
        o.append(T(x - 10, y + 5, name, "pin", "end"))
        if fn: o.append(T(fnx, y + 5, fn, "fn", "end"))
    elif side == "L":
        o.append(T(x + 10, y + 5, name, "pin", "start"))
        if fn: o.append(T(fnx, y + 5, fn, "fn", "start"))
    elif side == "B":
        o.append(T(x, y - 8, name, "pin", "start", f'transform="rotate(-90 {x} {y - 8})"'))
    elif side == "T":
        o.append(T(x, y + 8, name, "pin", "end", f'transform="rotate(-90 {x} {y + 8})"'))
    return "".join(o)

def gnd(x, y):
    return f'<path d="M{x},{y} L{x},{y+12} M{x-11},{y+12} L{x+11},{y+12} M{x-7},{y+17} L{x+7},{y+17} M{x-3},{y+22} L{x+3},{y+22}" class="thin"/>'

def zigzag(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2; z = 9
    pts = [(x, y0), (x, mid - 16)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        pts.append((x + dx, mid - 16 + (i + 0.5) * (32 / 6)))
    pts += [(x, mid + 16), (x, y1)]
    return rt.wire(pts, "thin", net)

def zigzag_h(rt, x0, x1, y, net):
    mid = (x0 + x1) / 2; z = 9
    pts = [(x0, y), (mid - 16, y)]
    for i, dy in enumerate((z, -z, z, -z, z, -z)):
        pts.append((mid - 16 + (i + 0.5) * (32 / 6), y + dy))
    pts += [(mid + 16, y), (x1, y)]
    return rt.wire(pts, "thin", net)

def capacitor(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2
    return "".join([rt.wire([(x, y0), (x, mid - 5)], "thin", net), rt.wire([(x, mid + 5), (x, y1)], "thin", "GND"),
                    f'<line x1="{x-12}" y1="{mid-5}" x2="{x+12}" y2="{mid-5}" class="thin"/>',
                    f'<line x1="{x-12}" y1="{mid+5}" x2="{x+12}" y2="{mid+5}" class="thin"/>'])

SHEET_CSS = ("<style>"
             ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
             ".usb{fill:var(--line);stroke:var(--ink-2);stroke-width:1.2}"
             ".title{font:700 17px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".sub{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".h1{font:900 24px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".h2{font:700 15px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
             ".pin{font:700 13px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
             ".lab{font:700 12.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
             ".mono{font:400 11.5px 'JetBrains Mono',monospace;fill:var(--ink)}"
             ".brass{font:700 12px 'JetBrains Mono',monospace;fill:var(--brass);letter-spacing:.08em}"
             ".blue{font:700 12px 'JetBrains Mono',monospace;fill:var(--signal);letter-spacing:.08em}"
             ".rod{fill:none;stroke:var(--ink);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
             ".bus{fill:none;stroke:var(--brass);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}"
             ".bus5{fill:none;stroke:var(--signal);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}"
             ".thin{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
             ".joint{fill:var(--ink)}"
             ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
             "</style>")

def wiring_sheet():
    rt = Router(); w = rt.wire
    o = [T(20, 30, "Pocket AI Sphere: every connection on one sheet", "h1"),
         T(600, 56, "A dot is a joint. A line that hops over another does not touch it. Thick = wire you solder (26 AWG for power, 30 AWG for signals, all white).", "sub"),
         T(600, 72, "Thin = a resistor or capacitor leg, or a lead that comes with the part. Ground symbols are one net: the holder's − lead is the star.", "sub"),
         T(600, 88, "Nothing is soldered to brass. Two rails: BAT+ from the cell (brass) and 5 V from the charger-boost (blue).", "sub")]
    LN = {"3V3": 190, "GND": 220, "SDA": 250, "SCL": 280}
    Y5 = 800; YBAT = 760

    # ---------------------------------------------------------------- XIAO, centre
    XX, XY, XW, XH = 560, 140, 300, 540
    o.append(block(XX, XY, XW, XH, "XIAO ESP32-S3 Sense", "black · camera GPIO10-18, 38-40, 47, 48 · PDM mic GPIO41/42", sub2="all inside the Sense board · SD slot empty, J3 cut", ty=380))
    Lp = {}
    for name, y, fn, net in (("3V3", 190, "3.3 V out, 700 mA", "3V3"), ("GND", 220, "signal ground", "GND"), ("D4", 250, "GPIO5 · SDA", "SDA"), ("D5", 280, "GPIO6 · SCL", "SCL"),
                             ("D8", 340, "GPIO7 · screen SCK", "SCK"), ("D9", 370, "GPIO8 · screen MOSI", "MOSI"), ("D6", 400, "GPIO43 · screen DC", "DC"),
                             ("D0", 580, "GPIO1 · BCLK", "BCLK"), ("D1", 610, "GPIO2 · LRC", "LRC"), ("D2", 640, "GPIO3 · DIN", "DIN")):
        Lp[name] = (XX, y); o.append(pin(rt, XX, y, name, "L", net, fn, XX + 50))
    Rp = {}
    for name, y, fn, net in (("D7", 190, "GPIO44 · button", "BTN"), ("GND", 220, "button return", "GND"), ("D3", 320, "GPIO4 · pan servo", "PAN"), ("D10", 350, "GPIO9 · tilt servo", "TILT")):
        Rp[name] = (XX + XW, y); o.append(pin(rt, XX + XW, y, name, "R", net, fn, XX + XW - 50))
    for i, line in enumerate(("5V pin: USB only · nothing connects here", "BAT pads: on the back, at the USB end", "its own 100 mA charger stays a fallback", "eleven pins, thirteen jobs: amp SD open,", "backlight tied on (Rev D: an I2C expander)")):
        o.append(T(XX + XW - 12, 430 + i * 17, line, "fn", "end"))
    Bp = {}
    for name, x, net in (("BAT+", 760, "BAT+"), ("BAT−", 830, "GND")):
        Bp[name] = (x, XY + XH); o.append(pin(rt, x, XY + XH, name, "B", net))
    o.append(f'<rect x="{XX+XW-52}" y="{XY+8}" width="38" height="15" rx="3" class="usb"/>'); o.append(T(XX + XW - 33, XY + 19, "USB-C", "fn", "middle"))
    o.append(T(XX + XW - 58, XY + 19, "flash · console", "fn", "end"))

    # ---------------------------------------------------------------- button, top right
    o.append(block(1000, 160, 170, 80, "Action button", "white cap · to GND", ty=32))
    o.append(pin(rt, 1000, 190, "", "L", "BTN")); o.append(pin(rt, 1000, 220, "", "L", "GND"))
    o.append(w([Rp["D7"], (1000, 190)], "rod", "BTN")); o.append(w([Rp["GND"], (1000, 220)], "rod", "GND"))
    o.append(T(930, 182, "BTN", "lab", "middle")); o.append(T(930, 212, "GND", "lab", "middle"))

    # ---------------------------------------------------------------- the two servos, right, on the 5 V rail
    SVX, SVW = 1000, 170
    o.append(block(SVX, 270, SVW, 110, "Tilt servo", "right hinge · black · FS0307", ty=22))
    o.append(pin(rt, SVX, 350, "sig", "L", "TILT")); o.append(pin(rt, SVX + SVW, 340, "+", "R", "5V")); o.append(pin(rt, SVX + SVW, 365, "−", "R", "GND"))
    o.append(w([Rp["D10"], (SVX, 350)], "rod", "TILT")); o.append(T(930, 342, "TILT", "lab", "middle"))
    o.append(block(SVX, 420, SVW, 110, "Pan servo", "on the coaster · black", sub2="wires down the left tine", ty=22))
    o.append(pin(rt, SVX, 500, "sig", "L", "PAN")); o.append(pin(rt, SVX + SVW, 490, "+", "R", "5V")); o.append(pin(rt, SVX + SVW, 515, "−", "R", "GND"))
    o.append(w([Rp["D3"], (980, 320), (980, 500), (SVX, 500)], "rod", "PAN")); o.append(T(930, 312, "PAN", "lab", "middle"))
    o.append(w([(SVX + SVW, 340), (1330, 340), (1330, Y5)], "rod", "5V")); o.append(dot(1330, Y5))
    o.append(w([(SVX + SVW, 365), (1215, 365)], "rod", "GND")); o.append(gnd(1215, 365))
    o.append(w([(SVX + SVW, 490), (1300, 490), (1300, Y5)], "rod", "5V")); o.append(dot(1300, Y5))
    o.append(w([(SVX + SVW, 515), (1215, 515)], "rod", "GND")); o.append(gnd(1215, 515))
    for i, line in enumerate(("the left tine carries", "5V, GND and PAN to", "the pan servo's lead")):
        o.append(T(1182, 556 + i * 14, line, "fn"))

    # ---------------------------------------------------------------- lanes to the left: 3V3, GND, SDA, SCL; the AHT20 above them, the screen below
    o.append(w([Lp["3V3"], (90, LN["3V3"])], "rod", "3V3"))
    o.append(w([Lp["GND"], (170, LN["GND"])], "rod", "GND"))
    o.append(w([Lp["D4"], (430, LN["SDA"])], "rod", "SDA"))
    o.append(w([Lp["D5"], (480, LN["SCL"])], "rod", "SCL"))
    for yy, lab in ((190, "3V3"), (220, "GND"), (250, "SDA"), (280, "SCL")):
        o.append(T(520, yy - 7, lab, "lab", "middle"))
    AX, AY, AW, AH = 300, 60, 240, 100
    o.append(block(AX, AY, AW, AH, "AHT20", "black · I2C 0x38 · on hooks at the top", ty=40))
    for x, name, net in ((340, "VIN", "3V3"), (380, "GND", "GND"), (430, "SDA", "SDA"), (480, "SCL", "SCL")):
        o.append(pin(rt, x, AY + AH, name, "B", net)); o.append(w([(x, AY + AH), (x, LN[net])], "rod", net))
        if net in ("3V3", "GND"): o.append(dot(x, LN[net]))
    SX, SY, SWd, SHt = 60, 330, 280, 160
    o.append(block(SX, SY, SWd, SHt, "1.54\" screen", "ST7789 · 240 × 240 · 4-wire SPI · 3.3 V", sub2="black glass · board colour to check", ty=64))
    for x, name, net in ((90, "BLK", "3V3"), (130, "VCC", "3V3"), (170, "GND", "GND")):
        o.append(pin(rt, x, SY, name, "T", net)); o.append(w([(x, SY), (x, LN[net])], "rod", net))
        if x not in (90, 170): o.append(dot(x, LN[net]))
    for y, name, net in ((340, "SCL", "SCK"), (370, "SDA", "MOSI"), (400, "DC", "DC"), (440, "RES", "RST")):
        o.append(pin(rt, SX + SWd, y, name, "R", net))
    for a, b, net in (("D8", 340, "SCK"), ("D9", 370, "MOSI"), ("D6", 400, "DC")):
        o.append(w([Lp[a], (SX + SWd, b)], "rod", net)); o.append(T(450, b - 7, net, "lab", "middle"))
    o.append(pin(rt, 230, SY + SHt, "CS", "B", "GND")); o.append(w([(230, SY + SHt), (230, 504)], "rod", "GND")); o.append(gnd(230, 504))
    o.append(w([(SX + SWd, 440), (370, 440)], "rod", "RST"))
    o.append(zigzag_h(rt, 370, 410, 440, "RST")); o.append(T(390, 426, "R1 10 kΩ", "fn", "middle"))
    o.append(w([(410, 440), (410, LN["3V3"])], "thin", "RST")); o.append(dot(410, LN["3V3"]))
    o.append(capacitor(rt, 370, 440, 500, "RST")); o.append(dot(370, 440)); o.append(gnd(370, 500)); o.append(T(386, 474, "C1 1 µF", "fn"))
    o.append(T(SX + 14, SY + SHt - 14, "PH2.0 lead, 8 wires", "fn"))

    # ---------------------------------------------------------------- amp and speaker, bottom left
    MX, MY, MW, MH = 100, 530, 240, 190
    o.append(block(MX, MY, MW, MH, "MAX98357A amp", "blue · hidden behind the screen", ty=20))
    o.append(T(MX + 12, MY + MH - 48, "SD open: on · GAIN open: 9 dB", "fn")); o.append(T(MX + 12, MY + MH - 62, "VIN 2.5-5.5 V: on the 5 V rail", "fn"))
    Ap = {}
    for name, y, net in (("BCLK", 580, "BCLK"), ("LRC", 610, "LRC"), ("DIN", 640, "DIN")):
        Ap[name] = (MX + MW, y); o.append(pin(rt, MX + MW, y, name, "R", net))
    for name, y, net in (("OUT+", 580, "SPK+"), ("OUT−", 620, "SPK-")):
        Ap[name] = (MX, y); o.append(pin(rt, MX, y, name, "L", net))
    for name, x, net in (("GND", 230, "GND"), ("VIN", 300, "5V")):
        Ap[name] = (x, MY + MH); o.append(pin(rt, x, MY + MH, name, "B", net))
    for a, b, net in (("D0", "BCLK", "BCLK"), ("D1", "LRC", "LRC"), ("D2", "DIN", "DIN")):
        o.append(w([Lp[a], Ap[b]], "rod", net)); o.append(T(450, Lp[a][1] - 7, b, "lab", "middle"))
    o.append(block(8, 540, 72, 100, "Speaker", "8 Ω · black", ty=36))
    rt.pin(80, 580, "SPK+"); rt.pin(80, 620, "SPK-")
    o += [f'<circle cx="80" cy="580" r="4.5" class="pinend"/>', f'<circle cx="80" cy="620" r="4.5" class="pinend"/>']
    o.append(w([(80, 580), Ap["OUT+"]], "thin", "SPK+")); o.append(w([(80, 620), Ap["OUT−"]], "thin", "SPK-"))
    o.append(T(44, 656, "own leads", "fn", "middle"))

    # ---------------------------------------------------------------- the power chain along the bottom: cell → toggle → BAT+ rail; charger-boost → 5 V rail
    o.append(w([(380, YBAT), (900, YBAT)], "bus", "BAT+"))
    o.append(T(400, YBAT - 10, "BAT+ rail · the cell through the toggle · 26 AWG", "brass"))
    o.append(w([(300, Y5), (1330, Y5)], "bus5", "5V"))
    o.append(T(660, Y5 + 22, "5 V rail · from the charger-boost · the servos and the amp", "blue"))
    o.append(w([Ap["VIN"], (300, Y5)], "rod", "5V"))
    o.append(w([Ap["GND"], (230, 740)], "rod", "GND")); o.append(gnd(230, 740))
    o.append(capacitor(rt, 360, Y5, 860, "5V")); o.append(dot(360, Y5)); o.append(gnd(360, 860)); o.append(T(376, 836, "220 µF", "fn"))
    o.append(w([Bp["BAT+"], (760, YBAT)], "rod", "BAT+")); o.append(dot(760, YBAT))
    o.append(w([Bp["BAT−"], (830, 720)], "rod", "GND")); o.append(gnd(830, 720))
    o.append(block(40, 850, 170, 90, "16340 cell", "NL169 · 950 mAh · in the tray", ty=26))
    rt.pin(80, 850, "CELL+"); rt.pin(210, 920, "GND")
    o += [f'<circle cx="80" cy="850" r="4.5" class="pinend"/>', T(92, 842, "+ red", "pin", "start"),
          f'<circle cx="210" cy="920" r="4.5" class="pinend"/>', T(198, 925, "− black", "pin", "end")]
    o.append(w([(210, 920), (250, 920)], "rod", "GND")); o.append(gnd(250, 920)); o.append(T(250, 958, "the star", "fn", "middle"))
    o.append(block(240, 850, 170, 90, "Toggle", "MTS-102 · middle lug in, outer out", sub2="lever forward = on · charge with it ON", ty=26))
    rt.pin(270, 850, "CELL+"); rt.pin(380, 850, "BAT+")
    o += [f'<circle cx="270" cy="850" r="4.5" class="pinend"/>', T(282, 842, "in", "pin", "start"),
          f'<circle cx="380" cy="850" r="4.5" class="pinend"/>', T(392, 842, "out", "pin", "start")]
    o.append(w([(80, 850), (80, 830), (270, 830), (270, 850)], "rod", "CELL+"))
    o.append(w([(380, 850), (380, YBAT)], "rod", "BAT+"))
    QX, QY, QW, QH = 470, 850, 230, 110
    o.append(block(QX, QY, QW, QH, "Charger-boost", "bq25185 · black · jumper cut: 500 mA", sub2="BAT by JST · EN to BAT+ · USB-C right", ty=48))
    o.append(pin(rt, 500, QY, "BAT+", "T", "BAT+")); o.append(pin(rt, 560, QY, "EN", "T", "BAT+")); o.append(pin(rt, 630, QY, "5V", "T", "5V"))
    o.append(pin(rt, QX + QW, 905, "BAT−", "R", "GND")); o.append(pin(rt, QX + QW, 935, "G", "R", "GND"))
    o.append(w([(500, QY), (500, YBAT)], "rod", "BAT+")); o.append(dot(500, YBAT))
    o.append(w([(560, QY), (560, YBAT)], "rod", "BAT+")); o.append(dot(560, YBAT))
    o.append(w([(630, QY), (630, Y5)], "rod", "5V")); o.append(dot(630, Y5))
    o.append(w([(QX + QW, 905), (760, 905), (760, 935), (QX + QW, 935)], "rod", "GND")); o.append(gnd(760, 935))
    o.append(T(QX + 14, QY + QH - 12, "USB-C: charge here, toggle ON", "fn"))

    # ---------------------------------------------------------------- the numbers, right
    NX, NY = 940, 616
    o.append(T(NX, NY, "From the 950 mAh cell", "h2"))
    for i, (mode, ma, note, _l) in enumerate(POWER):
        yy = NY + 22 + i * 30
        o.append(T(NX, yy, mode, "lab")); o.append(T(NX, yy + 14, f"{ma} mA · {note}", "fn"))
    o.append(T(NX, 858, "Meter before the cell goes in", "h2"))
    for i, line in enumerate(("every ring, post and tine against BAT+, 5V, GND, 3V3: open", "holder red lead to the button top: 3.6-4.2 V", "BAT+ to GND open · 5V to GND open · servo + to − open")):
        o.append(T(NX, 880 + i * 16, line, "fn"))
    o.append(T(NX, 944, "Never", "h2"))
    for i, line in enumerate(("the 5V pin · a wire to brass · a scope ground on the speaker", "both USB-C ports at once · the cell soldered or charged below 0 °C", "both servos started from rest at the same instant")):
        o.append(T(NX, 966 + i * 16, line, "fn"))

    bad, crossings = rt.check()
    for b in bad: print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    o.append(T(20, SH - 24, f"{REV}, {REV_DATE}, approved as drawn {APPROVED_C}. {len(rt.segs)} segments, {crossings} crossings, each drawn as a hop; the clearance check passes.", "sub"))
    o.append(T(20, SH - 8, "Pins and powers from the Seeed XIAO ESP32S3 wiki, Crumb's screen wiring, the Pololu FS0307 page, the Adafruit bq25185 and AHT20 pages, the Same Sky and Nitecore sheets. Not built.", "sub"))
    return f'<svg viewBox="0 0 {SW} {SH}" role="img" aria-label="Pocket AI Sphere wiring sheet">{SHEET_CSS}{"".join(o)}</svg>', crossings

# ------------------------------------------------------------------ writers
def tbl(headers, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in headers)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><tr>{h}</tr>{b}</table></div>'

def md_inline(t):
    import re
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return t

def write_html(views, sheet, crossings):
    link = lambda text, url: f'<a href="{html.escape(url)}">{html.escape(text)}</a>'
    parts_rows = []
    for qty, part, where, url, status, colour, why in PARTS:
        badge = {"TO BUY": '<span class="badge buy">to buy</span>', "owned": '<span class="badge own">owned</span>',
                 "optional": '<span class="badge opt">optional</span>', "in the mail": '<span class="badge opt">in the mail</span>'}[status]
        parts_rows.append((qty, f"{html.escape(part)}<br>{badge}", link(where, url), html.escape(colour), html.escape(why)))
    total = sum(m for _, m in MASS)
    css = open(os.path.join(HERE, "style.css")).read()
    page = f'''<title>Pocket AI Sphere</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">
<style>{css}</style>
<div class="wrap">
<div class="masthead">
  <div class="eyebrow">Pocket AI &middot; third build &middot; {REV}, approved as drawn {APPROVED_C}</div>
  <h1>A Pocket AI in a brass sphere that looks at you</h1>
  <div class="sub">The same assistant as the first Pocket AI, plus a camera, a weather sensor and a head that follows you: the whole sphere nods and turns on a brass fork. Rev B was approved {APPROVED_B}; the same day the builder asked for the moving head, the <a href="{MOTION}">motion</a> was shown and approved, and Rev C, step one of the build rule, was approved as drawn on {APPROVED_C}. Nothing bent, soldered or flashed; one board in the mail; three lines to buy, listed in <code>docs/ORDER.md</code>. Source: <code>pocket_ai_sphere/docs/DESIGN.md</code>, drawn by <code>docs/pages/gen/sphere.py</code>.</div>
</div>

<p>Three rings, two posts, a fork. A vertical ring of 1.5&nbsp;mm brass rod, a top ring and a base ring; two thin posts between the cap rings carry the screen. The vertical ring's right pole is a servo: its body is set into the ring, its shaft points out along the sphere's axis, and the fork holds its horn still, so the servo tilts the sphere around itself. The left pole is a brass stub in a bushing. The fork is three pieces of 4&nbsp;mm brass tube on a second servo standing on a brass coaster, and that one turns the whole thing. Inside, the owned 1.54&nbsp;inch colour screen fills the open front with the camera board behind it, lens over the top edge; the cell lies on the floor as ballast with the speaker on it; the charger-boost stands behind the tray; the sensor hangs under the top ring. The two blue parts stand behind the screen where nothing sees them; the chrome lever, the white button cap and white wire are the only things that are not brass or black.</p>

<figure>{views["hero"]}
<figcaption>At rest: pan 0, tilt 0. Every part in the colour it is sold in. The servos are the two black blocks: one is the right hinge, one is the neck. Rods at the back are drawn paler.</figcaption></figure>

<div class="grid3">
<figure>{views["front"]}</figure>
<figure>{views["side"]}</figure>
<figure>{views["back"]}</figure>
</div>

<div class="kpis">
<div><b>70 mm</b><span>sphere; 105 mm tall on its coaster</span></div>
<div><b>{SPHERE_MASS:.0f} g</b><span>the sphere, cell in; {total-150:.0f} g on the desk before any steel</span></div>
<div><b>±60° · ±25°</b><span>pan and tilt; 2.7 h following, 6 h idle</span></div>
<div><b>2.2 h</b><span>to charge through the charger-boost's USB-C</span></div>
</div>

<h2>What changed from Rev B</h2>
<ul class="changes">{"".join(f"<li>{md_inline(s)}</li>" for s in CHANGES)}</ul>

<h2>How it moves</h2>
<p>Shown and approved on the <a href="{MOTION}">motion page</a> before this drawing. The camera sees about {2*FOV["h"]}° across and {2*FOV["v"]}° up and down. While you are inside that cone only the pupils move: the firmware draws them where it sees your face. Past about {DEAD}° off the sphere's axis the eyes are near the edge of the glass, and after a short pause the sphere turns to put you back in the middle while the eyes slide home. Pan stops at ±{LIM["pan"]}° (the wires in the left tine twist no further), tilt at ±{LIM["tilt"]}°. The servos are rated 0.1 s per 60°; the firmware eases every move and never slews both from rest at once. With the power off the sphere hangs level on its own: its centre of mass sits 7 mm under the tilt axis.</p>

<h2>Colour, part by part</h2>
<p>The rule of 2026-11-09: no paint and no covers; parts in brass, ivory, white or black, and anything sold only in another colour placed out of sight.</p>
{tbl(["Part", "Colour as sold", "Where it sits", "What shows"], COLOURS)}

<h2>Why these numbers</h2>
<ul>
<li><strong>70 mm still.</strong> Nothing swings inside now, so the sphere did not have to grow: the 33 x 36 mm screen sits 15 mm forward of the centre with its lower corners 1 mm inside the surface, and the camera board's top at y = 24 is 5 mm inside.</li>
<li><strong>The hinge is the servo.</strong> Any horizontal axis through the centre passes through the vertical ring at the poles, so a servo inside could not reach a horn outside: its shaft would hit the ring. Setting the servo into the ring, with the ring's ends in its ears, puts the shaft on the axis with nothing in the way, and the ring's two ends hold it as well as a bracket would.</li>
<li><strong>0.022 kg-cm to tilt.</strong> {SPHERE_MASS:.0f} g with its centre of mass 7 mm under the axis: at 25° that is 0.022 kg-cm against the servo's 0.5. The pan servo turns about 80 g on its own bearing with no moment to hold; its plastic bushing takes the fork's weight, which is the one thing to watch.</li>
<li><strong>105 mm tall.</strong> Coaster 8, servo 17.3, horn 4, bar 4, 2 mm of clearance, then the 70 mm sphere: the sphere's centre is 70 mm above the desk, which puts the lens 90 mm up, about the height of a face across a desk when it tilts up.</li>
<li><strong>The fork's tines at ±39.5 mm</strong> clear the sphere by 4.5 mm; the left one is a 4 mm tube because three wires run inside it. Tube in three pieces, lapped and soldered, because a 4 mm tube does not bend to a 10 mm radius without a mandrel.</li>
<li><strong>A coaster that tips at 28°</strong> with 80 g under 90 g on a 70 mm lever; the satellite's answer, 150 g of steel in the hollow, makes it 45°. The washers are optional on day one.</li>
<li><strong>5 V from a boost, not from USB.</strong> The XIAO's 5V pin is dead on battery, and the servos want 4.8 V or more. The charger-boost already belongs to the family, costs $7 and charges five times faster into the bargain.</li>
<li><strong>Eleven pins for thirteen jobs.</strong> Three for I2S, two for I2C, three for the screen, two servos, the button: eleven. The amp's shutdown line and backlight dimming went, as on the rover.</li>
</ul>

<h2>Parts</h2>
<p>Three lines to buy, about $60 landed: the coaster on Amazon (in the cart), the two servos and the charger-boost from DigiKey, which Amazon does not sell. Everything else is in the drawers or in the mail. The order sheet is <code>docs/ORDER.md</code>.</p>
{tbl(["Qty", "Part", "Where", "Colour", "Why, and what to check"], parts_rows, "parts")}

<h2>The wiring sheet</h2>
<figure class="sheet">{sheet}
<figcaption>Two rails: the cell's BAT+ through the toggle for the XIAO and the charger, and the charger's 5 V for the servos and the amp. Nothing crosses the hinge; three wires go down the left tine to the pan servo. {crossings} crossings, each a hop.</figcaption></figure>

<h2>Pin map</h2>
{tbl(["Header", "GPIO", "Net", "Job"], [(h, g, f"<code>{n}</code>" if n else "", j) for h, g, n, j in PINS])}

<h2>Every wire, and why</h2>
{tbl(["Net", "From", "To", "Wire", "Why"], [(f"<code>{n}</code>", a, b, wv, y) for n, a, b, wv, y in NETS])}

<h2>Power, run time, charge time</h2>
{tbl(["Mode", "mA from the cell", "Time"], [(m, str(ma), t) for m, ma, _s, t in POWER])}
<div class="note warn"><span class="lbl">Carried over, and new</span>
<ul>
<li>The cell is the only source. Nothing into the XIAO's <code>5V</code> pin; only the holder on the BAT pads, through the toggle.</li>
<li>Volume cap 65; GAIN open. The amp's SD is open now: a soft click at power-up is possible; a Rev D expander gets it back if it matters.</li>
<li>Neither speaker lead is ground. No GND wire, no scope ground.</li>
<li>The brass is not a conductor: meter every ring, post and tine against every net before the cell goes in, and after every solder session.</li>
<li>Never solder to the cell; never charge it below 0 °C; one USB-C port at a time; the first charge watched.</li>
<li>The servos move only after boot, eased, one at a time from rest.</li>
</ul></div>

<h2>Frame cut list</h2>
{tbl(["Piece", "Stock", "Length", "How"], CUTS)}

<h2>Test every part before any brass</h2>
<p>Nine breadboard steps, each with a pass line. They use Seeed's examples and Crumb's screen test; the servos sweep from a sketch. Do them in order.</p>
{tbl(["Step", "Do", "Pass when"], TESTS, "tests")}

<h2>Build order</h2>
<ol>{"".join(f"<li>{html.escape(s)}</li>" for s in BUILD)}</ol>

<h2>Mass</h2>
{tbl(["Part", "g"], [(p, f"{m:g}") for p, m in MASS] + [("<strong>Total on the desk, steel in</strong>", f"<strong>{total:.0f}</strong>")])}

<h2>What could go wrong</h2>
<ul>
<li><strong>The screen's board colour.</strong> Not recorded. If it is not black, its 8 mm tab shows under the glass. Look in Crumb's box before anything else; a black-board 1.54" is the Rev D answer.</li>
<li><strong>The pan servo's bushing.</strong> A sub-micro servo's output shaft turns in plastic; 80 g on a 70 mm lever may wobble. If it does, a 9 g FS90 in the same place, or a 3 mm tube bearing round the horn.</li>
<li><strong>The ring's ends in the servo's ears.</strong> Glue, not solder, holds the hinge to the frame. Rough the rod, fill the ear's hole, let it cure a day; if it ever creeps, a turn of 0.5 mm wire through the ear.</li>
<li><strong>The camera flex and the microphone.</strong> The lens is 5.5 mm over the screen's edge, the mic port 3.5. If the mic port lands behind the screen on the real board, raise the camera board 2 mm.</li>
<li><strong>The boost under both servos.</strong> 0.8 A if both stall; the firmware starts them apart and the 220 µF rides the steps.</li>
<li><strong>Wi-Fi.</strong> The antenna lies flat on the XIAO's back under Kapton, behind the screen's board: test the range in step 9 before brass.</li>
<li><strong>It is top-heavy on an 80 g coaster</strong> until the washers go in.</li>
</ul>
<hr>
</div>
'''
    open(os.path.join(PAGES, "sphere.html"), "w").write(page)

def write_md(crossings):
    def md_tbl(headers, rows):
        out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
        for r in rows: out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
        return "\n".join(out)
    total = sum(m for _, m in MASS)
    parts_rows = [(q, p, f"[{w}]({u})", s, c, why) for q, p, w, u, s, c, why in PARTS]
    md = f'''# Pocket AI Sphere: design record

**{REV}, {REV_DATE}, approved as drawn by the builder on {APPROVED_C}. Nothing bent, soldered or flashed; the XIAO is in the mail; three lines to buy (`ORDER.md`).**
Generated by `pages/gen/sphere.py`; edit the script, not this file. The drawings and the wiring
sheet are on the published page (`pages/sphere.html`, [artifact]({ARTIFACT}), see `ARTIFACTS.md`);
the motion was shown and approved first on the [motion page]({MOTION}) (`pages/sphere-motion.html`).
Rev B (approved as drawn {APPROVED_B}) is kept as `pages/gen/sphere_revB.py.bak` and
`pages/sphere_revB.html.bak`; Rev A as the `_revA` pair.

## What it is

The third Pocket AI: the same assistant as the first build (screen, microphone, amplifier and
speaker, one button, Wi-Fi to the local server), plus the camera of the second build, a weather
sensor, and a head that follows you: the whole 70 mm sphere nods and turns on a brass fork.

The sphere: a vertical ring of 1.5 mm K&S rod (x-y plane), a top ring and a base ring of 22 mm
radius at y = ±27.2, two 1.0 mm posts between the cap rings at x = ±17, z = 14. The vertical
ring's right pole is the tilt servo: its body set into the ring (x 17.7..35, y −6.5..13.5), the
ring's ends glued into its ears, its shaft on the x axis pointing out, its horn held by the fork.
The left pole is a 1.5 mm stub turning in a 3 mm bushing on the left tine. The fork: two 4 mm tube
tines at x = ±39.5 and a bar at y = −39, lapped and soldered; the bar on the horn of the pan servo
standing on a 75 mm brass coaster; the desk 70.3 mm below the sphere's centre.

Inside: the 1.54" screen (33 x 36, glass 28 x 28) at y −22..14, board z 15..17, glass to 20, glued
by its edges to the posts; the XIAO ESP32-S3 Sense behind its upper half (x ±10.5, y 6..24,
z 5.5..14.5, USB-C left, lens at y 19.5); the cell tray on the base ring (y −27..−13, z −11.5..6.5),
the speaker lying across the cell (y −10.3..−5.4) firing up; the toggle's body against the tray's
front wall behind the screen (x 3.5..13.5), chrome lever out right at y −15; the amplifier against
the back of the screen below the camera board (x −12.5..3.5, y −22..−6, z 12..15); the charger-boost
standing behind the tray (x ±14.5, y −25..−6, z −17..−12), USB-C to the right; the 220 µF beside
it; the AHT20 flat under the top ring at the back on two hooks; the button under the top ring at
the front, white cap up.

Coordinates: origin at the sphere's centre, at rest; x right, y up, z toward the face. Radius 35.

## What changed from Rev B

{chr(10).join(f"- {s}" for s in CHANGES)}

## How it moves

The camera sees about {2*FOV["h"]}° x {2*FOV["v"]}°. Inside that cone only the pupils move; past
about {DEAD}° off axis the sphere turns, after a short pause, to re-centre you, pan ±{LIM["pan"]}°,
tilt ±{LIM["tilt"]}°, eased, never both servos from rest at once. Centre of mass 7 mm under the
tilt axis: it hangs level with the power off. Shown and approved on the motion page.

## Colour, part by part

{md_tbl(["Part", "Colour as sold", "Where it sits", "What shows"], COLOURS)}

## Why these numbers

- 70 mm still: nothing swings inside; the screen's lower corners are 1 mm inside the surface.
- The hinge is the servo: any axis through the centre meets the vertical ring at the poles, so the
  servo sits in the ring with the ring's ends in its ears and its shaft on the axis.
- 0.022 kg-cm to tilt ({SPHERE_MASS:.0f} g, centre of mass 7 mm low, 25°) against 0.5 available.
- 105 mm tall: coaster 8 + servo 17.3 + horn 4 + bar 4 + 2 mm clearance + the sphere.
- Tines at ±39.5 clear the sphere by 4.5 mm; three pieces of tube, no bends.
- The coaster tips at 28° bare, 45° with the satellite's 150 g of steel in its hollow.
- 5 V from the charger-boost: the servos are 4.8-6 V and the XIAO's 5V pin is dead on battery.
- Eleven pins, thirteen jobs: amp SD open and backlight tied on, as the rover does.

## Parts

{md_tbl(["Qty", "Part", "Where", "Status", "Colour", "Why, and what to check"], parts_rows)}

## Pin map

{md_tbl(["Header", "GPIO", "Net", "Job"], [(h, g, f"`{n}`" if n else "", j) for h, g, n, j in PINS])}

## Every wire, and why

{md_tbl(["Net", "From", "To", "Wire", "Why"], [(f"`{n}`", a, b, wv, y) for n, a, b, wv, y in NETS])}

The sheet on the page: {crossings} crossings, each drawn as a hop; the clearance check passes.

## Power, run time, charge time

{md_tbl(["Mode", "mA from the cell", "Time"], [(m, str(ma), t) for m, ma, _s, t in POWER])}

Carried over: the cell is the only source and nothing feeds the `5V` pin; cap 65, GAIN open;
neither speaker lead is ground; the brass is not a conductor; never solder to or cold-charge the
cell; one USB-C at a time. New: the amp's SD is open; the servos move only after boot, eased, one
at a time from rest.

## Frame cut list

{md_tbl(["Piece", "Stock", "Length", "How"], CUTS)}

## Test every part before any brass

{md_tbl(["Step", "Do", "Pass when"], TESTS)}

## Build order

{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(BUILD))}

## Mass

{md_tbl(["Part", "g"], [(p, f"{m:g}") for p, m in MASS] + [("**Total on the desk, steel in**", f"**{total:.0f}**")])}

The sphere alone is about {SPHERE_MASS:.0f} g.

## Risks

- The screen's board colour is not recorded; if not black, its tab shows under the glass. Look
  in Crumb's box first; a black-board 1.54" is the Rev D answer.
- The pan servo's plastic bushing carries 80 g on a 70 mm lever; a 9 g FS90 or a tube bearing if
  it wobbles.
- The hinge is glued (ring ends in the servo's ears): rough, fill, cure a day; a wire turn if it creeps.
- If the mic port lands behind the screen on the real board, raise the camera board 2 mm.
- 0.8 A if both servos stall: start them apart; the 220 µF rides the steps.
- Wi-Fi with the antenna behind the screen's board: test the range in step 9.
- Top-heavy on an 80 g coaster until the washers go in.
'''
    open(os.path.join(DOCS, "DESIGN.md"), "w").write(md)

if __name__ == "__main__":
    views = make_views()
    sheet, crossings = wiring_sheet()
    write_html(views, sheet, crossings)
    write_md(crossings)
    print("wrote", os.path.join(PAGES, "sphere.html"), "and", os.path.join(DOCS, "DESIGN.md"), f"({crossings} crossings)")
