"""Draws the three desk-robot prototypes of 2026-11-07 (round two of the desk robot, after Crumb)
and writes the concept page.

    python3 concepts.py            writes ../desk_robot_concepts.html
    python3 concepts.py --png DIR  also renders every figure to PNG in DIR with headless Chrome (for checking)

Every drawing is derived from the geometry tables below (millimetres: x right, y up from the desk,
z forward toward the face). Front, side and top views share one scale. Nothing here has been built.
"""
from __future__ import annotations
import math, pathlib, subprocess, sys, html

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
OUT = PAGES / "desk_robot_concepts.html"
S = 3.0  # px per mm

# ----------------------------------------------------------------------------- part sizes (mm)
LIDAR_D, LIDAR_H, LIDAR_BASE_H, LIDAR_SCAN = 38.6, 34.8, 22.2, 27.0   # LDROBOT STL-19P/LD19: round body, rotor is the top 12.6 mm, scan plane 27 above the flange's underside
LIDAR_FL_W, LIDAR_FL_D, LIDAR_FL_T = 54.0, 46.3, 1.3                   # the moulded three-lug mounting flange at the base
XIAO_W, XIAO_H, XIAO_T = 18.0, 21.0, 10.0                             # stack standing: width (x), height (y), thickness (z)
CAM = 8.0                                                              # camera module square
IPS_W, IPS_H, IPS_T, IPS_PIC = 33.0, 36.0, 2.5, 27.7                   # 1.54" square colour screen, owned
RND_BOARD, RND_PIC = 38.0, 32.4                                        # 1.28" round colour screen
OLED_B, OLED_GW, OLED_GH = 27.3, 26.7, 19.3                            # 0.96" OLED module, owned
N20_L, N20_W, N20_H, SHAFT = 24.0, 12.0, 10.0, 10.0                    # gear motor: length along the axle, width (z), height (y), shaft length
HOLDER_L, HOLDER_W, HOLDER_H = 43.0, 18.0, 14.0
DRV = 25.4; DRV_T = 10.0                                               # Qwiic motor driver
BOOST_L, BOOST_W, BOOST_T = 36.0, 23.0, 8.0                            # power-path boost board
AMP_L, AMP_W = 19.0, 16.0
GAUGE_L, GAUGE_W = 25.4, 17.8
IMU_L, IMU_W = 21.0, 16.0
SPK_L, SPK_W, SPK_T = 20.0, 13.0, 4.9
RNG_W, RNG_L = 12.7, 17.8                                              # single-point laser ranger carrier
TYRE = 1.6

# ----------------------------------------------------------------------------- drawing helpers
ROD = 'stroke="var(--brass)" stroke-width="2.4" fill="none" stroke-linejoin="round" stroke-linecap="round"'
ROD_THIN = 'stroke="var(--brass)" stroke-width="1.6" fill="none" stroke-linecap="round"'
HID = 'stroke="var(--muted)" stroke-width=".8" stroke-dasharray="2.4 2" fill="none"'
HID_FILL = 'stroke="var(--muted)" stroke-width=".7" stroke-dasharray="2.4 2" fill="var(--hid)"'
SKIN = 'stroke="var(--skin-edge)" stroke-width=".9"'
BEAM = 'stroke="var(--beam)" stroke-width=".9" stroke-dasharray="3 2.2" fill="none"'
SCAN = 'stroke="var(--scan)" stroke-width="1.1" stroke-dasharray="4 2.5" fill="none"'
D2R = math.pi / 180


class View:
    """One orthographic view. (u, v) are the two drawing axes in mm; the frame is in mm too."""

    def __init__(self, w, h, ox, oy, label):
        self.w, self.h, self.ox, self.oy, self.label = w, h, ox, oy, label
        self.parts = []

    def X(self, u): return round((u + self.ox) * S, 2)
    def Y(self, v): return round((self.h - (v + self.oy)) * S, 2)
    def add(self, s): self.parts.append(s)

    def rect(self, u, v, du, dv, fill, extra=""):
        self.add(f'<rect x="{self.X(u)}" y="{self.Y(v + dv)}" width="{du * S:.2f}" height="{dv * S:.2f}" fill="{fill}" {extra}/>')

    def rrect(self, u, v, du, dv, r, fill, extra=""):
        self.add(f'<rect x="{self.X(u)}" y="{self.Y(v + dv)}" width="{du * S:.2f}" height="{dv * S:.2f}" rx="{r * S:.2f}" fill="{fill}" {extra}/>')

    def circ(self, u, v, r, fill, extra=""):
        self.add(f'<circle cx="{self.X(u)}" cy="{self.Y(v)}" r="{r * S:.2f}" fill="{fill}" {extra}/>')

    def line(self, u1, v1, u2, v2, extra):
        self.add(f'<line x1="{self.X(u1)}" y1="{self.Y(v1)}" x2="{self.X(u2)}" y2="{self.Y(v2)}" {extra}/>')

    def poly(self, pts, fill, extra=""):
        p = " ".join(f"{self.X(u)},{self.Y(v)}" for u, v in pts)
        self.add(f'<polygon points="{p}" fill="{fill}" {extra}/>')

    def path(self, d_mm, fill, extra=""):
        """d_mm: list of (cmd, [(u,v),...]) built by the caller in mm; only M/L/A/Z used."""
        out = []
        for cmd, pts in d_mm:
            if cmd == "A":
                (r, (u, v)) = pts
                out.append(f"A{r * S:.2f},{r * S:.2f} 0 0 1 {self.X(u)},{self.Y(v)}")
            elif cmd == "Z":
                out.append("Z")
            else:
                out.append(cmd + " ".join(f"{self.X(u)},{self.Y(v)}" for u, v in pts))
        self.add(f'<path d="{" ".join(out)}" fill="{fill}" {extra}/>')

    def text(self, u, v, s, cls="", anchor="middle", dy=0):
        self.add(f'<text x="{self.X(u)}" y="{self.Y(v) + dy}" class="{cls}" text-anchor="{anchor}">{html.escape(s)}</text>')

    def tag(self, n, u, v, tu, tv):
        """Numbered key marker at (tu, tv) with a leader to (u, v)."""
        self.add(f'<line x1="{self.X(u)}" y1="{self.Y(v)}" x2="{self.X(tu)}" y2="{self.Y(tv)}" stroke="var(--brass-dk)" stroke-width=".7"/>')
        self.add(f'<circle cx="{self.X(u)}" cy="{self.Y(v)}" r="1.6" fill="var(--brass-dk)"/>')
        self.add(f'<circle cx="{self.X(tu)}" cy="{self.Y(tv)}" r="{2.7 * S:.1f}" fill="var(--panel)" stroke="var(--brass-dk)" stroke-width=".9"/>')
        self.add(f'<text x="{self.X(tu)}" y="{self.Y(tv) + 2.9}" class="tag" text-anchor="middle">{n}</text>')

    def dim(self, u1, v1, u2, v2, label, off=0, side="below"):
        """Dimension line between two points, with the label beside it. Horizontal or vertical."""
        if abs(v1 - v2) < 1e-6:  # horizontal
            y = v1 + off
            self.line(u1, y, u2, y, 'stroke="var(--muted)" stroke-width=".7"')
            for u in (u1, u2):
                self.line(u, y - 1.2, u, y + 1.2, 'stroke="var(--muted)" stroke-width=".7"')
                self.line(u, v1, u, y, 'stroke="var(--muted)" stroke-width=".4" stroke-dasharray="1 1"')
            self.text((u1 + u2) / 2, y + (-3.6 if side == "below" else 1.2), label, "dimlab")
        else:  # vertical
            x = u1 + off
            self.line(x, v1, x, v2, 'stroke="var(--muted)" stroke-width=".7"')
            for v in (v1, v2):
                self.line(x - 1.2, v, x + 1.2, v, 'stroke="var(--muted)" stroke-width=".7"')
                self.line(u1, v, x, v, 'stroke="var(--muted)" stroke-width=".4" stroke-dasharray="1 1"')
            self.add(f'<text x="{self.X(x) + (6 if side == "right" else -6)}" y="{self.Y((v1 + v2) / 2) + 2.6}" class="dimlab" text-anchor="{"start" if side == "right" else "end"}">{html.escape(label)}</text>')

    def svg(self):
        W, H = self.w * S, self.h * S
        return (f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{html.escape(self.label)}">'
                + "".join(self.parts) + "</svg>")


def desk(v, u1, u2):
    v.rect(u1, -6, u2 - u1, 6, "var(--desk)")
    v.line(u1, 0, u2, 0, 'stroke="var(--line)" stroke-width="1"')
    v.text(u1 + 7, -4.2, "desk", "dimlab")


def wheel_side(v, zc, yc, r, label_face=True):
    """A wheel face-on: black tyre ring, ivory disc, a brass hub dot."""
    v.circ(zc, yc, r, "var(--tyre)")
    v.circ(zc, yc, r - TYRE, "var(--ivory)", 'stroke="var(--skin-edge)" stroke-width=".7"')
    v.circ(zc, yc, 2.2, "var(--brass)")
    v.circ(zc, yc, 1.0, "var(--ink)")


def wheel_edge(v, u, v0, w, r, yc):
    """A wheel edge-on (front or top view): the tread as a dark slab, w wide, 2r tall/deep, centred at height yc."""
    v.rrect(u, yc - r, w, 2 * r, 1.2, "var(--tyre)")
    v.rect(u + 0.8, yc - r + TYRE, w - 1.6, 2 * r - 2 * TYRE, "var(--tyre-2)")


def lidar_front(v, xc, y0, flange=None):
    """Lidar seen from the side or front: the flange (if asked, hidden or not), the lower housing, the rotor with its window band."""
    r = LIDAR_D / 2
    if flange == "hidden":
        v.rect(xc - LIDAR_FL_W / 2, y0, LIDAR_FL_W, LIDAR_FL_T, "none", HID)
    elif flange == "deep":
        v.rect(xc - LIDAR_FL_D / 2, y0, LIDAR_FL_D, LIDAR_FL_T, "none", HID)
    v.rrect(xc - r, y0 + LIDAR_FL_T, LIDAR_D, LIDAR_BASE_H - LIDAR_FL_T, 1.5, "var(--black)")
    v.rrect(xc - r + 1.6, y0 + LIDAR_BASE_H, LIDAR_D - 3.2, LIDAR_H - LIDAR_BASE_H, 2.5, "var(--black-2)")
    v.rect(xc - r + 1.6, y0 + LIDAR_SCAN - 3.0, LIDAR_D - 3.2, 6, "var(--window)")
    v.rect(xc - r + 1.6, y0 + LIDAR_SCAN - 0.35, LIDAR_D - 3.2, 0.7, "var(--scan)")


def lidar_top(v, xc, zc):
    r = LIDAR_D / 2
    v.circ(xc, zc, r, "var(--black)")
    v.circ(xc, zc, r - 1.2, "var(--black-2)")
    v.circ(xc, zc, 5.5, "var(--window)")
    v.circ(xc, zc, 1.2, "var(--black)")


def eyes_square(v, xc, yc, w=IPS_PIC, h=IPS_PIC):
    """Pip's eyes on a square picture area centred at (xc, yc)."""
    v.rect(xc - w / 2, yc - h / 2, w, h, "var(--glass)")
    for ex in (-7.5, 7.5):
        v.rrect(xc + ex - 4.5, yc - 6, 9, 12, 3.4, "var(--eye)")


def eyes_round(v, xc, yc, d=RND_PIC):
    v.circ(xc, yc, d / 2, "var(--glass)")
    for ex in (-7, 7):
        v.rrect(xc + ex - 4.2, yc - 5.5, 8.4, 11, 3.2, "var(--eye)")


def oled_eye(v, xc, yc):
    v.rect(xc - OLED_GW / 2, yc - OLED_GH / 2, OLED_GW, OLED_GH, "var(--glass)")
    v.rrect(xc - 5, yc - 5.5, 10, 11, 3.5, "var(--eye)")


# ============================================================================= concept A: Mochi
def concept_a():
    """A soft ivory loaf on small wheels wearing the lidar as a hat. Round colour face."""
    WR, AY, AZ = 15.5, 16.0, 0.0            # wheel radius (Pololu 32×7 is Ø31 over the tyre), axle height, axle z
    WX0, WW = 29.0, 7.0                     # wheel inner face x, width
    BX, BZ0, BZ1, BY0, BY1, R = 28.0, -28.0, 28.0, 5.0, 60.0, 6.0   # body skin, side-profile corner radius
    LZ = -3.0                               # lidar centre z
    LY0 = BY1 - LIDAR_FL_T                  # the flange sits just under the top skin; only the round body shows
    FACE_Y = 31.0                           # round screen centre
    TOP = LY0 + LIDAR_H
    key = []
    K = lambda n, t: key.append((n, t))

    # ---------- front (u = x, v = y)
    f = View(100, 122, 50, 17, "Mochi, front view")
    desk(f, -50, 50)
    for sx in (-1, 1):
        u = WX0 if sx > 0 else -(WX0 + WW)
        wheel_edge(f, u, 0, WW, WR, AY)
        f.line(sx * BX, AY, sx * (WX0 + 1), AY, 'stroke="var(--steel)" stroke-width="2.4"')   # shaft stubs
    f.rect(-BX, BY0, 2 * BX, BY1 - BY0, "var(--ivory)", SKIN)                                  # front skin
    f.rect(-25, AY - N20_H / 2, 24, N20_H, "none", HID); f.rect(1, AY - N20_H / 2, 24, N20_H, "none", HID)
    f.rect(-21.5, 22, HOLDER_L, HOLDER_H, "none", HID)
    f.rect(-13, 37, DRV, DRV_T, "none", HID)
    f.rect(-27, 22, BOOST_T, BOOST_L, "none", HID); f.rect(22, 22, 5, GAUGE_L, "none", HID)
    f.rect(-XIAO_W / 2, 28, XIAO_W, XIAO_H, "none", HID)
    f.rect(12, 6, SPK_W, 5, "none", HID); f.rect(-10, 6, IMU_L, 3, "none", HID)
    f.circ(0, FACE_Y, RND_BOARD / 2 - 0.5, "var(--panel)", 'stroke="var(--skin-edge)" stroke-width=".6" stroke-dasharray="1.5 1.5"')
    eyes_round(f, 0, FACE_Y)
    f.circ(-5, 54.5, 2.6, "var(--glass)"); f.circ(-5, 54.5, 1.1, "var(--lens)")                   # camera lens on the brow
    f.rect(4, 52.2, RNG_W, 4.6, "var(--black)"); f.rect(8.6, 53.6, 3.6, 1.9, "var(--window)")      # edge ranger window on the brow
    f.line(-BX, BY0, -BX, BY1, ROD); f.line(BX, BY0, BX, BY1, ROD)                                  # hoops end-on
    f.line(-BX, BY1, BX, BY1, ROD); f.line(-BX, BY0, BX, BY0, ROD)                                  # top and floor rails
    lidar_front(f, 0, LY0, flange="hidden")
    f.line(-BX, BY1, BX, BY1, ROD)                                                                  # the top rail, over the flange
    f.circ(0, 2.6, 2.6, "var(--brass)"); f.line(0, BY0, 0, 2.6, ROD_THIN)                            # nose skid (the tail one is behind it)
    f.dim(-(WX0 + WW), -8.5, WX0 + WW, -8.5, "72 over the wheels", off=0)
    f.dim(BX + 10, 0, BX + 10, TOP, "96", off=0, side="right")
    f.tag(1, 0, FACE_Y + 12, -41, 38); f.tag(2, -5, 54.5, -41, 64); f.tag(3, 10.4, 54.5, 41, 66)
    f.tag(4, 0, LY0 + 20, 41, 90); f.tag(5, -32.5, 22, -42, 10); f.tag(6, 0, 29, 41, 24)

    # ---------- side (u = z forward → right, v = y)
    s = View(116, 122, 46, 17, "Mochi, side view, face to the right")
    desk(s, -46, 70)
    s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "var(--ivory-2)", SKIN)                            # side panel (inside the hoop)
    s.rect(BZ0 + 1, 22, HOLDER_W, HOLDER_H, "none", HID_FILL); s.text(BZ0 + 10, 27.5, "cell", "hid", dy=2)
    s.rect(AZ - N20_W / 2, AY - N20_H / 2, N20_W, N20_H, "none", HID_FILL)
    s.rect(BZ0 + 1, 37, DRV, DRV_T, "none", HID_FILL); s.text(BZ0 + 13.5, 40.5, "driver", "hid", dy=2)
    s.rect(-18, 22, BOOST_W, BOOST_L, "none", HID); s.text(-6.5, 52, "boost", "hid", dy=2)
    s.rect(-23, 22, GAUGE_W, GAUGE_L, "none", HID)
    s.rect(BZ0 + 1, 6, SPK_L, SPK_T, "none", HID); s.text(BZ0 + 10, 12.5, "speaker", "hid", dy=2)
    s.rect(14, 28, XIAO_T, XIAO_H, "none", HID_FILL); s.text(19, 36, "XIAO", "hid", dy=2)
    s.rect(BZ1 - 2.6, FACE_Y - RND_BOARD / 2, IPS_T, RND_BOARD, "var(--black)")                   # round screen edge-on
    wheel_side(s, AZ, AY, WR)
    s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "none", ROD)                                        # the side hoop
    s.circ(0, BY1, 1.0, "var(--brass-dk)"); s.circ(0, BY0, 1.0, "var(--brass-dk)")                  # top and floor rails, end-on
    s.circ(BZ1 - 1.9, 54.8, 1.5, "var(--glass)")                                                   # lens on the brow
    rng = (BZ1 - 2.6, 53.2)
    for a in (28, 40, 52):
        L = rng[1] / math.sin(a * D2R)
        s.line(rng[0], rng[1], rng[0] + L * math.cos(a * D2R), 0, BEAM)
    s.add(f'<text x="{s.X(70)}" y="{s.Y(-4.2)}" class="dimlab" text-anchor="end">edge seen 50–90 mm ahead</text>')
    lidar_front(s, LZ, LY0, flange="deep")
    s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "none", ROD)                                        # hoop again, over the flange line
    sy = LY0 + LIDAR_SCAN
    s.line(-46, sy, LZ - LIDAR_D / 2, sy, SCAN); s.line(LZ + LIDAR_D / 2, sy, 70, sy, SCAN)
    s.add(f'<text x="{s.X(70)}" y="{s.Y(sy + 1.8)}" class="dimlab" text-anchor="end">lidar plane {sy:.0f} mm up</text>')
    s.circ(BZ0 + 3, 2.6, 2.6, "var(--brass)"); s.line(BZ0 + 3, BY0, BZ0 + 3, 2.6, ROD_THIN)        # tail skid
    s.circ(BZ1 - 3, 3.4, 2.4, "var(--brass)"); s.line(BZ1 - 3, BY0, BZ1 - 3, 3.4, ROD_THIN)        # nose skid, 1 mm up
    s.rect(BZ0 - 3, 48, 3, 4, "var(--steel)"); s.line(BZ0 - 3, 50, BZ0 - 9, 52.5, 'stroke="var(--steel)" stroke-width="2"')
    s.dim(BZ0, -8.5, BZ1, -8.5, "56", off=0)
    s.tag(5, AZ, AY, -40, 10); s.tag(7, BZ0 - 6, 51, -40, 66); s.tag(8, BZ0 + 3, 2.6, -40, 24)
    s.tag(9, BZ0 + 10, 29, -40, 42); s.tag(10, rng[0], rng[1], 50, 66); s.tag(4, LZ, LY0 + 20, -32, 92)
    s.tag(13, BZ0 + 10, 8.5, 48, 18)
    s.text(BZ1 + 4, 31, "face", "dimlab", "start")

    # ---------- top (u = x, v = z forward ↑)
    t = View(96, 90, 48, 48, "Mochi, top view, face at the top")
    for sx in (-1, 1):
        u = WX0 if sx > 0 else -(WX0 + WW)
        t.rrect(u, AZ - WR, WW, 2 * WR, 1.2, "var(--tyre)")
        t.line(sx * BX, AZ, sx * (WX0 + 1), AZ, 'stroke="var(--steel)" stroke-width="2.4"')
    t.rrect(-BX, BZ0, 2 * BX, BZ1 - BZ0, 0.5, "var(--ivory)", SKIN)
    t.rect(-25, AZ - N20_W / 2, 24, N20_W, "none", HID); t.rect(1, AZ - N20_W / 2, 24, N20_W, "none", HID)
    t.rect(-21.5, BZ0 + 1, HOLDER_L, HOLDER_W, "none", HID)
    t.rect(-13, BZ0 + 1, DRV, DRV, "none", HID)
    t.rect(-27, -18, BOOST_T, BOOST_W, "none", HID); t.rect(22, -23, 5, GAUGE_W, "none", HID); t.rect(22, -2, 5, AMP_W, "none", HID)
    t.rect(-XIAO_W / 2, 14, XIAO_W, XIAO_T, "none", HID)
    t.rect(-RND_BOARD / 2, BZ1 - 2.6, RND_BOARD, IPS_T, "var(--black)")
    t.rect(12, BZ0 + 1, SPK_W, SPK_L, "none", HID)
    t.rect(-BX, BZ0, 2 * BX, BZ1 - BZ0, "none", ROD)                                               # hoops (sides) and the rails
    t.line(-BX, 0, BX, 0, ROD_THIN)                                                                 # top rail
    t.rrect(-LIDAR_FL_W / 2, LZ - 23, LIDAR_FL_W, LIDAR_FL_D, 6, "none", HID)                       # the flange, under the top skin
    lidar_top(t, 0, LZ)
    t.circ(-5, BZ1 - 1.5, 1.5, "var(--glass)")
    t.rect(-11, BZ0 - 2.6, 3.4, 2.6, "var(--steel)"); t.rect(17, BZ0 - 2.6, 3.4, 2.6, "var(--steel)")   # button, toggle, out the back
    t.text(0, BZ0 - 7.5, "cell and driver lie across the back, under the hat", "hid", dy=2)
    t.dim(-(WX0 + WW), BZ0 - 13, WX0 + WW, BZ0 - 13, "72", off=0)
    t.tag(11, -24, 24, -41, 34); t.tag(7, 18.7, BZ0 - 1.3, 41, -31); t.tag(12, 0, 17, 41, 10)
    t.text(0, BZ1 + 3, "face", "dimlab")

    K(1, "1.28\" round colour screen (240 × 240, SPI; the Waveshare module has a round Ø37.5 board and a backlight pin) behind a Ø33 window: the whole face is one big round eye-pair.")
    K(2, "Camera lens on the brow, on the top-front rounding, looking about 25° up: it sees a face across the desk, not just the desk.")
    K(3, "Single-point laser ranger (owned) beside the lens on the brow, aimed 40° down: the hard edge stop, reading the desk 50–90 mm ahead.")
    K(4, "The lidar, worn as a hat: its three-lug flange (54 × 46 mm) hides under the top skin on two cross rods, so only the round black Ø38.6 body shows, 33 mm of it, 3 mm behind centre. Its plane is 86 mm up and clear all round.")
    K(5, "Two gear motors (owned) end to end on one axle 16 mm up; Ø31 ivory wheels with black silicone tyres, 7 mm wide, outboard of the side panels. 72 wide over them.")
    K(6, "XIAO ESP32-S3 Sense standing behind the screen: camera, microphone, Wi-Fi. Its lens ribbon climbs over the screen’s top to the brow.")
    K(7, "Toggle (cell + lead) and the action button, low on the back panel, lever out the back.")
    K(8, "Brass dome skids at tail and nose: it rests on the tail; the nose dome rides 1 mm up and catches a hard stop.")
    K(9, "16340 cell (owned) in its holder across the back, above the motors’ tails: that puts the weight behind the axle. The driver lies flat on it; the boost stands on the left wall, gauge and amp on the right.")
    K(10, "The ranger’s field: 28° to 52° below level, meeting the desk 50–90 mm ahead of the face.")
    K(11, "Body: an ivory card loaf 56 wide, 56 deep, 55 tall, corners r 6 in profile, on two 1.5 mm brass hoops and two 1.0 mm rails. The brass shows only as the edges.")
    K(12, "Driver, boost, gauge, amp, motion sensor: all inside; nothing coloured shows.")
    K(13, "Speaker (owned) flat on the floor firing down through a slot; the desk is its sounding board. The motion sensor lies beside it.")
    views = [(f.svg(), "Front. A soft ivory loaf with brass edges, one big round face, the hat on top. The wheels are small and tucked under."),
             (s.svg(), "Side, face to the right. The hoop is the outline; the Ø31 wheel is the ivory disc. Dashed: the ranger’s field and the lidar’s plane."),
             (t.svg(), "Top, face at the top. The hat sits 3 mm behind centre so the robot rests on its tail skid.")]
    return dict(name="Mochi", views=views, key=key,
                dims=f"72 W × 56 D × {TOP:.0f} H mm (body 56 × 56 × 55, hat 33 above it) · wheels Ø31 at axle 16 · clearance 5 · about 212 g · lidar plane {LY0 + LIDAR_SCAN:.0f} mm up",
                mass=212, height=TOP, scan=LY0 + LIDAR_SCAN)


# ============================================================================= concept B: Lantern
def concept_b():
    """A puck base and a head, with the lidar's rotor turning in the gap between them."""
    WR, AY, AZ = 20.0, 19.0, -8.0                # Ø40 wheels, axle 19 up, 8 back: the wheel sits flush with the puck's back
    WX0, WW = 29.0, 7.0
    BX, BZ0, BZ1 = 28.0, -28.0, 28.0             # puck
    PY0, PY1 = 5.0, 32.0
    LZ, LY0 = 2.0, 25.0                          # lidar centre z; its base recessed 7 mm into the puck, over the motors
    GAP0, GAP1 = PY1, LY0 + LIDAR_H + 2.2        # open band: 32 .. 62
    HY0, HY1 = GAP1, GAP1 + 44                   # head 62 .. 106
    HX, HZ0, HZ1 = 28.0, -24.0, 24.0             # head 56 wide, 48 deep
    SCR_Y = HY0 + 1.5                            # screen bottom
    posts = [(-25, 18), (25, 18), (0, -26)]
    key = []
    K = lambda n, t: key.append((n, t))

    # ---------- front
    f = View(100, 134, 50, 17, "Lantern, front view")
    desk(f, -50, 50)
    for sx in (-1, 1):
        u = WX0 if sx > 0 else -(WX0 + WW)
        wheel_edge(f, u, 0, WW, WR, AY)
        f.line(sx * BX, AY, sx * (WX0 + 1), AY, 'stroke="var(--steel)" stroke-width="2.4"')
    f.rrect(-BX, PY0, 2 * BX, PY1 - PY0, 0.8, "var(--ivory)", SKIN)
    f.rect(-25, AY - N20_H / 2, 24, N20_H, "none", HID); f.rect(1, AY - N20_H / 2, 24, N20_H, "none", HID)
    f.rect(-21.5, PY0 + 1, HOLDER_L, HOLDER_H, "none", HID)
    f.rect(-18, PY0 + 1, BOOST_L, BOOST_T, "none", HID)
    f.rect(-LIDAR_D / 2, LY0, LIDAR_D, PY1 - LY0, "none", HID)
    for (px, pz) in posts:
        f.line(px, GAP0, px, GAP1, ROD)
    lidar_front(f, 0, LY0, flange="hidden")
    f.rect(-BX, PY1 - 0.5, 2 * BX, 1.0, "var(--ivory)")                                            # puck top skin, over the recess
    f.rrect(-HX, HY0, 2 * HX, HY1 - HY0, 0.8, "var(--ivory)", SKIN)
    f.rect(-XIAO_W / 2, HY0 + 10, XIAO_W, XIAO_H, "none", HID)
    f.rect(-13, HY1 - 12, DRV, DRV_T, "none", HID); f.rect(-27, HY0 + 2, 5, AMP_L, "none", HID)
    f.rect(22, HY0 + 2, 5, GAUGE_L, "none", HID)
    f.rect(-IPS_W / 2, SCR_Y, IPS_W, IPS_H, "var(--panel)", 'stroke="var(--skin-edge)" stroke-width=".6" stroke-dasharray="1.5 1.5"')
    eyes_square(f, 0, SCR_Y + IPS_H / 2 + 0.5)
    f.circ(-4, HY1 - 3.5, 2.6, "var(--glass)"); f.circ(-4, HY1 - 3.5, 1.1, "var(--lens)")
    f.line(-BX, PY1, BX, PY1, ROD); f.line(-BX, PY0, BX, PY0, ROD); f.line(-BX, PY0, -BX, PY1, ROD); f.line(BX, PY0, BX, PY1, ROD)
    f.line(-HX, HY1, HX, HY1, ROD); f.line(-HX, HY0, HX, HY0, ROD); f.line(-HX, HY0, -HX, HY1, ROD); f.line(HX, HY0, HX, HY1, ROD)
    f.circ(0, 2.6, 2.6, "var(--brass)"); f.line(0, PY0, 0, 2.6, ROD_THIN)
    f.dim(-(WX0 + WW), -8.5, WX0 + WW, -8.5, "72 over the wheels", off=0)
    f.dim(HX + 10, 0, HX + 10, HY1, f"{HY1:.0f}", off=0, side="right")
    f.tag(1, 0, SCR_Y + IPS_H - 6, -42, 92); f.tag(2, -4, HY1 - 3.5, -42, 110); f.tag(4, 0, LY0 + LIDAR_SCAN, 42, 54)
    f.tag(5, -32.5, 20, -42, 8); f.tag(3, 25, GAP0 + 12, 42, 38); f.tag(6, 0, HY0 + 24, 42, 76)

    # ---------- side
    s = View(116, 134, 46, 17, "Lantern, side view, face to the right")
    desk(s, -46, 70)
    s.rrect(BZ0, PY0, BZ1 - BZ0, PY1 - PY0, 0.8, "var(--ivory-2)", SKIN)
    s.rect(-1, PY0 + 1, HOLDER_W, HOLDER_H, "none", HID_FILL); s.text(8, 11, "cell", "hid", dy=2)
    s.rect(AZ - N20_W / 2, AY - N20_H / 2, N20_W, N20_H, "none", HID_FILL)
    s.rect(BZ0 + 1, PY0 + 1, BOOST_W, BOOST_T, "none", HID); s.text(BZ0 + 12, 7.5, "boost, flat", "hid", dy=2)
    s.rect(LZ - LIDAR_D / 2, LY0, LIDAR_D, PY1 - LY0, "none", HID)
    wheel_side(s, AZ, AY, WR)
    s.rrect(BZ0, PY0, BZ1 - BZ0, PY1 - PY0, 0.8, "none", ROD)
    for (px, pz) in posts:
        s.line(pz, GAP0, pz, GAP1, ROD if px >= 0 else ROD_THIN)
    lidar_front(s, LZ, LY0, flange="deep")
    s.rect(BZ0, PY1 - 0.5, BZ1 - BZ0, 1.0, "var(--ivory-2)")
    sy = LY0 + LIDAR_SCAN
    s.line(-46, sy, LZ - LIDAR_D / 2, sy, SCAN); s.line(LZ + LIDAR_D / 2, sy, 70, sy, SCAN)
    s.add(f'<text x="{s.X(70)}" y="{s.Y(sy + 1.8)}" class="dimlab" text-anchor="end">lidar plane {sy:.0f} mm up</text>')
    s.rrect(HZ0, HY0, HZ1 - HZ0, HY1 - HY0, 0.8, "var(--ivory-2)", SKIN)
    s.rect(HZ0 + 1, HY1 - 12, DRV, DRV_T, "none", HID_FILL); s.text(HZ0 + 13.5, HY1 - 8.5, "driver", "hid", dy=2)
    s.rect(HZ0 + 1, HY0 + 2, SPK_T, SPK_L, "none", HID); s.text(HZ0 + 9, HY0 + 10, "spk", "hid", dy=2)
    s.rect(HZ0 + 7, HY0 + 2, IMU_W, 3, "none", HID)
    s.rect(HZ1 - IPS_T - 11, HY0 + 10, XIAO_T, XIAO_H, "none", HID_FILL); s.text(HZ1 - 8.5, HY0 + 19, "XIAO", "hid", dy=2)
    s.rect(HZ1 - IPS_T - 0.5, SCR_Y, IPS_T, IPS_H, "var(--black)")
    s.rrect(HZ0, HY0, HZ1 - HZ0, HY1 - HY0, 0.8, "none", ROD)
    s.circ(HZ1 - 1.9, HY1 - 3.5, 1.5, "var(--glass)")
    rng = (HZ1 - 3, HY0 + 3)
    for a in (33, 45, 57):
        L = rng[1] / math.sin(a * D2R)
        s.line(rng[0], rng[1], rng[0] + L * math.cos(a * D2R), 0, BEAM)
    s.add(f'<text x="{s.X(70)}" y="{s.Y(-4.2)}" class="dimlab" text-anchor="end">edge seen 40–65 mm ahead</text>')
    s.circ(BZ1 - 3, 2.6, 2.6, "var(--brass)"); s.line(BZ1 - 3, PY0, BZ1 - 3, 2.6, ROD_THIN)
    s.rect(BZ0 - 3, 26, 3, 4, "var(--steel)"); s.line(BZ0 - 3, 28, BZ0 - 9, 30.5, 'stroke="var(--steel)" stroke-width="2"')
    s.dim(BZ0, -8.5, BZ1, -8.5, "56", off=0)
    s.tag(5, AZ, AY, -40, 8); s.tag(7, BZ0 - 6, 29, -40, 40); s.tag(8, BZ1 - 3, 2.6, 50, 10)
    s.tag(9, 8, 13, 50, 24); s.tag(10, rng[0], rng[1], 50, 76); s.tag(4, LZ, LY0 + 16, -40, 58)
    s.tag(11, HZ0 + 3.5, HY0 + 14, -40, 78); s.tag(12, HZ0 + 13, HY1 - 7, -40, 104)
    s.text(HZ1 + 4, HY0 + 22, "face", "dimlab", "start")

    # ---------- top
    t = View(96, 90, 48, 48, "Lantern, top view, face at the top")
    for sx in (-1, 1):
        u = WX0 if sx > 0 else -(WX0 + WW)
        t.rrect(u, AZ - WR, WW, 2 * WR, 1.2, "var(--tyre)")
        t.line(sx * BX, AZ, sx * (WX0 + 1), AZ, 'stroke="var(--steel)" stroke-width="2.4"')
    t.rrect(-BX, BZ0, 2 * BX, BZ1 - BZ0, 10, "var(--ivory)", 'stroke="var(--skin-edge)" stroke-width=".6" stroke-dasharray="1.5 1.5"')
    t.rect(-25, AZ - N20_W / 2, 24, N20_W, "none", HID); t.rect(1, AZ - N20_W / 2, 24, N20_W, "none", HID)
    t.rrect(-HX, HZ0, 2 * HX, HZ1 - HZ0, 10, "var(--ivory)", SKIN)
    t.rrect(-HX, HZ0, 2 * HX, HZ1 - HZ0, 10, "none", ROD)
    t.circ(0, LZ, LIDAR_D / 2, "none", 'stroke="var(--black)" stroke-width="1.2" stroke-dasharray="3 2"')
    t.rect(-21.5, -1, HOLDER_L, HOLDER_W, "none", HID)
    t.rect(-13, HZ0 + 1, DRV, DRV, "none", HID); t.rect(-18, BZ0 + 1, BOOST_L, BOOST_T, "none", HID)
    t.rect(-10, HZ0 + 1, SPK_L, SPK_T, "none", HID); t.rect(22, HZ0 + 3, 5, GAUGE_W, "none", HID); t.rect(-27, HZ0 + 3, 5, AMP_W, "none", HID)
    t.rect(-XIAO_W / 2, HZ1 - IPS_T - 11, XIAO_W, XIAO_T, "none", HID)
    t.rect(-IPS_W / 2, HZ1 - IPS_T - 0.5, IPS_W, IPS_T, "var(--black)")
    t.circ(-4, HZ1 - 1.5, 1.5, "var(--glass)")
    for (px, pz) in posts:
        t.circ(px, pz, 1.2, "var(--brass-dk)")
    t.rect(17, BZ0 - 2.6, 3.4, 2.6, "var(--steel)")
    t.text(0, BZ0 - 7.5, "dashed circle: the rotor under the head; dots: the three posts", "hid", dy=2)
    t.dim(-(WX0 + WW), BZ0 - 13, WX0 + WW, BZ0 - 13, "72", off=0)
    t.tag(3, 25, 18, 41, 30); t.tag(12, -8, HZ0 + 8, -41, -20); t.tag(7, 18.7, BZ0 - 1.3, 41, -31)
    t.text(0, HZ1 + 3, "face", "dimlab")

    K(1, "1.54\" square colour screen (240 × 240, SPI, owned, one of three) fills the head’s face; Pip’s eyes at 220 ppi.")
    K(2, "Camera lens on the brow above the screen; the XIAO stands behind the screen with its ribbon up.")
    K(3, "Three 1.5 mm brass posts carry the head over the open band: two at the front corners, one at the back. Each hides 2–3° of the scan.")
    K(4, "The lidar’s flange and the first 7 mm of its body are recessed into the puck, over the motors; the rest of the black body and the rotor stand in the open band. Scan plane 52 mm up, all round but the posts.")
    K(5, "Motors (owned) end to end, axle 19 up and 8 back so the Ø40 ivory wheels sit flush with the puck’s back. The robot rests on its nose skid.")
    K(6, "Head 56 × 48 × 44: screen and XIAO at the front, driver under the roof, speaker and motion sensor at the back, amp and gauge on the walls.")
    K(7, "Toggle on the puck’s back wall, lever out; the action button beside it.")
    K(8, "Brass dome skid at the nose, the third contact, carrying about a quarter of the weight.")
    K(9, "16340 cell (owned) across the puck floor, just ahead of the motors, under the lidar’s base: the heaviest part at the lowest point. The charger-boost board lies flat on the floor behind the motors.")
    K(10, "Single-point laser ranger (owned) in the head’s chin, aimed 45° down past the puck’s front: the edge stop, 40–65 mm ahead.")
    K(11, "Speaker (owned) at the head’s back wall firing backward; the motion sensor flat beside it.")
    K(12, "Driver (owned) flat under the head’s roof; its four motor wires and the cell leads run down the back post in a loom.")
    views = [(f.svg(), "Front. Two ivory blocks with brass edges and the black rotor turning between them; wheels at the puck’s back."),
             (s.svg(), "Side, face to the right. The lidar plane runs 50 mm over the desk; the ranger looks down from the chin."),
             (t.svg(), "Top, face at the top. The head hides the puck; the dashed circle is the rotor under it, the dots the three posts.")]
    return dict(name="Lantern", views=views, key=key,
                dims=f"72 W × 56 D × {HY1:.0f} H mm (puck 56 × 56 × 27, band 30, head 56 × 48 × 44) · wheels Ø40 at axle 19 · clearance 5 · about 208 g · lidar plane {LY0 + LIDAR_SCAN:.0f} mm up",
                mass=208, height=HY1, scan=LY0 + LIDAR_SCAN)


# ============================================================================= concept C: Wheelie
def concept_c():
    """Two big ivory wheels, a slim capsule between them, two eyes up top, the lidar low in a front slot."""
    WR, AY, AZ = 30.0, 30.0, -16.0               # Ø60 wheels; the axle sits 16 back so the motors clear the lidar's base
    WX0, WW = 29.0, 8.0
    BX, BZ0, BZ1, BY0, BY1, R = 28.0, -30.0, 30.0, 6.0, 100.0, 10.0
    LZ, LY0 = 10.0, 6.0
    SLOT0, SLOT1 = LY0 + LIDAR_BASE_H - 0.5, 43.0   # the front window band: from the rotor's foot to the upper floor
    EYE_Y = 81.5
    key = []
    K = lambda n, t: key.append((n, t))

    # ---------- front
    f = View(100, 128, 50, 17, "Wheelie, front view")
    desk(f, -50, 50)
    for sx in (-1, 1):
        u = WX0 if sx > 0 else -(WX0 + WW)
        wheel_edge(f, u, 0, WW, WR, AY)
        f.line(sx * BX, AY, sx * (WX0 + 1), AY, 'stroke="var(--steel)" stroke-width="2.4"')
    f.rect(-BX, BY0, 2 * BX, BY1 - BY0, "var(--ivory)", SKIN)
    f.rect(-BX + 0.5, SLOT0, 2 * BX - 1, SLOT1 - SLOT0, "var(--panel)")                           # the open slot
    f.rect(-25, AY - N20_H / 2, 24, N20_H, "none", HID); f.rect(1, AY - N20_H / 2, 24, N20_H, "none", HID)
    lidar_front(f, 0, LY0)
    f.rect(-BX, BY0, 2 * BX, SLOT0 - BY0, "var(--ivory)", SKIN)                                    # lower skin over the lidar base
    f.rect(-LIDAR_FL_W / 2, LY0, LIDAR_FL_W, LIDAR_FL_T, "none", HID)                               # the flange on the floor
    f.rect(-21.5, 44, HOLDER_L, HOLDER_H, "none", HID); f.rect(-13, 44, DRV, DRV_T, "none", HID)
    f.rect(-18, 59, BOOST_L, BOOST_W, "none", HID)
    f.rect(-XIAO_W / 2, 50, XIAO_W, XIAO_H, "none", HID)
    f.rect(21, 60, 5, GAUGE_L, "none", HID)
    for ex in (-1, 1):
        f.rect(ex * 13.6 - OLED_B / 2, EYE_Y - OLED_B / 2, OLED_B, OLED_B, "var(--panel)",
               'stroke="var(--skin-edge)" stroke-width=".6" stroke-dasharray="1.5 1.5"')
        oled_eye(f, ex * 13.6, EYE_Y)
    f.circ(0, 63, 2.6, "var(--glass)"); f.circ(0, 63, 1.1, "var(--lens)")
    f.rect(-20, 45, RNG_W, 4.6, "var(--black)"); f.rect(-15.5, 46.4, 3.6, 1.9, "var(--window)")
    f.line(-BX, BY0, -BX, BY1, ROD); f.line(BX, BY0, BX, BY1, ROD); f.line(-BX, BY1, BX, BY1, ROD); f.line(-BX, BY0, BX, BY0, ROD)
    f.line(-BX, SLOT0, BX, SLOT0, ROD_THIN); f.line(-BX, SLOT1, BX, SLOT1, ROD_THIN)
    f.circ(0, 2.6, 2.6, "var(--brass)"); f.line(0, BY0, 0, 2.6, ROD_THIN)
    f.dim(-(WX0 + WW), -8.5, WX0 + WW, -8.5, "74 over the wheels", off=0)
    f.dim(BX + 12, 0, BX + 12, BY1, f"{BY1:.0f}", off=0, side="right")
    f.tag(1, 13.6, EYE_Y + 6, 42, 98); f.tag(2, 0, 63, -42, 70); f.tag(3, -13.6, 47, -42, 54)
    f.tag(4, 0, LY0 + LIDAR_SCAN, 42, 22); f.tag(5, -31, 50, -42, 36); f.tag(6, 0, 72, 42, 78)

    # ---------- side
    s = View(124, 128, 54, 17, "Wheelie, side view, face to the right")
    desk(s, -54, 70)
    s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "var(--ivory-2)", SKIN)                            # the capsule
    s.rect(BZ0 + 1, 44, HOLDER_W, HOLDER_H, "none", HID_FILL); s.text(BZ0 + 10, 49.5, "cell", "hid", dy=2)
    s.rect(AZ - N20_W / 2, AY - N20_H / 2, N20_W, N20_H, "none", HID_FILL)
    s.rect(-10, 44, DRV, DRV_T, "none", HID_FILL); s.text(2.7, 47.5, "driver", "hid", dy=2)
    s.rect(BZ0 + 1, 59, BOOST_T, BOOST_W, "none", HID); s.text(BZ0 + 5, 70, "boost", "hid", dy=2)
    s.rect(BZ0 + 1, 6, SPK_L, SPK_T, "none", HID); s.text(BZ0 + 10, 12.5, "speaker", "hid", dy=2)
    s.rect(16, 50, XIAO_T, XIAO_H, "none", HID_FILL); s.text(21, 58, "XIAO", "hid", dy=2)
    s.rect(0, SLOT0, BZ1, SLOT1 - SLOT0, "var(--panel)")                                           # the slot opens the front half
    lidar_front(s, LZ, LY0)
    s.rect(0, BY0, BZ1, SLOT0 - BY0, "var(--ivory-2)", SKIN)                                       # lower front skin over the base
    s.rect(LZ - LIDAR_FL_D / 2, LY0, LIDAR_FL_D, LIDAR_FL_T, "none", HID)
    s.rect(BZ1 - 2.5, EYE_Y - OLED_B / 2, 2, OLED_B, "var(--black)")
    wheel_side(s, AZ, AY, WR)
    s.rrect(BZ0, BY0, BZ1 - BZ0, BY1 - BY0, R, "none", ROD)
    s.line(0, SLOT0, BZ1, SLOT0, ROD_THIN); s.line(0, SLOT1, BZ1, SLOT1, ROD_THIN)
    s.line(0, SLOT0, 0, SLOT1, ROD_THIN)                                                           # the post at the slot’s back edge
    sy = LY0 + LIDAR_SCAN
    s.line(LZ + LIDAR_D / 2, sy, 70, sy, SCAN)
    s.add(f'<text x="{s.X(70)}" y="{s.Y(sy + 1.8)}" class="dimlab" text-anchor="end">lidar plane {sy:.0f} mm up</text>')
    s.circ(BZ1 - 1.9, 63, 1.5, "var(--glass)")
    rng = (BZ1 - 2, 47.5)
    for a in (28, 40, 52):
        L = rng[1] / math.sin(a * D2R)
        s.line(rng[0], rng[1], rng[0] + L * math.cos(a * D2R), 0, BEAM)
    s.add(f'<text x="{s.X(70)}" y="{s.Y(-4.2)}" class="dimlab" text-anchor="end">edge seen 50–90 mm ahead</text>')
    s.circ(BZ1 - 3, 2.6, 2.6, "var(--brass)"); s.line(BZ1 - 3, BY0, BZ1 - 3, 2.6, ROD_THIN)
    s.rect(BZ0 - 3, 40, 3, 4, "var(--steel)"); s.line(BZ0 - 3, 42, BZ0 - 9, 44.5, 'stroke="var(--steel)" stroke-width="2"')
    s.dim(AZ - WR, -8.5, BZ1, -8.5, "76 over the wheel", off=0)
    s.tag(5, AZ, AY, -48, 14); s.tag(7, BZ0 - 6, 43, -48, 56); s.tag(8, BZ1 - 3, 2.6, 50, 10)
    s.tag(9, BZ0 + 10, 51, -48, 74); s.tag(10, rng[0], rng[1], 50, 66); s.tag(4, LZ, LY0 + 8, 50, 22)
    s.tag(11, BZ0 + 10, 8.5, -48, 34); s.tag(12, 2.7, 49, -48, 92)
    s.text(BZ1 + 4, 81, "face", "dimlab", "start")

    # ---------- top
    t = View(96, 102, 48, 60, "Wheelie, top view, face at the top")
    for sx in (-1, 1):
        u = WX0 if sx > 0 else -(WX0 + WW)
        t.rrect(u, AZ - WR, WW, 2 * WR, 1.2, "var(--tyre)")
        t.line(sx * BX, AZ, sx * (WX0 + 1), AZ, 'stroke="var(--steel)" stroke-width="2.4"')
    t.rrect(-BX, BZ0, 2 * BX, BZ1 - BZ0, 0.5, "var(--ivory)", SKIN)
    t.rect(-25, AZ - N20_W / 2, 24, N20_W, "none", HID); t.rect(1, AZ - N20_W / 2, 24, N20_W, "none", HID)
    t.circ(0, LZ, LIDAR_D / 2, "none", 'stroke="var(--black)" stroke-width="1.2" stroke-dasharray="3 2"')
    t.rect(-21.5, BZ0 + 1, HOLDER_L, HOLDER_W, "none", HID)
    t.rect(-13, -10, DRV, DRV, "none", HID); t.rect(-18, BZ0 + 1, BOOST_L, BOOST_T, "none", HID)
    t.rect(21, -20, 5, GAUGE_W, "none", HID); t.rect(21, 0, 5, AMP_W, "none", HID)
    t.rect(-XIAO_W / 2, 16, XIAO_W, XIAO_T, "none", HID)
    for ex in (-1, 1):   # the two eye boards, toed in 12°
        t.add(f'<g transform="rotate({ex * 12} {t.X(0)} {t.Y(BZ1 - 1.2)})">')
        t.rect(0 if ex > 0 else -OLED_B, BZ1 - 2.4, OLED_B, 2.0, "var(--black)")
        t.add('</g>')
    t.circ(0, BZ1 - 1.5, 1.5, "var(--glass)")
    t.rect(-BX, BZ0, 2 * BX, BZ1 - BZ0, "none", ROD)
    t.line(-BX, 0, BX, 0, ROD_THIN)
    t.rect(17, BZ0 - 2.6, 3.4, 2.6, "var(--steel)"); t.rect(-11, BZ0 - 2.6, 3.4, 2.6, "var(--steel)")
    t.text(0, AZ - WR - 4, "the wheels reach 16 mm behind the body", "hid", dy=2)
    t.dim(-(WX0 + WW), AZ - WR - 10, WX0 + WW, AZ - WR - 10, "74", off=0)
    t.tag(1, 12, BZ1 - 1, 42, 26); t.tag(7, 18.7, BZ0 - 1.3, 42, -36); t.tag(13, -27, 20, -42, 10)
    t.text(0, BZ1 + 3, "face", "dimlab")

    K(1, "Two 0.96\" white OLEDs (owned) as eyes, toed in 12° so the head reads as round; I²C at 0x3C and 0x3D.")
    K(2, "Camera lens between and below the eyes, a nose; the XIAO stands behind it.")
    K(3, "Single-point laser ranger (owned) under the left eye at the slot’s upper lip, aimed 40° down: the edge stop.")
    K(4, "The lidar stands on the floor ahead of the axle, its flange between the hoops; the rotor looks out of a front slot 21 mm tall. Scan plane 33 mm up, the lowest of the three: it sees books and phones. The wheels hide about ±45° each side.")
    K(5, "Two gear motors (owned) end to end behind the lidar, axle 30 up and 16 back; Ø60 ivory wheels with black silicone tyres. The wheels reach 16 mm behind the body; the robot rests on its nose skid.")
    K(6, "Boost standing at the back wall, driver flat over the lidar, gauge and amp on the right wall.")
    K(7, "Toggle and action button on the back, above the motors.")
    K(8, "Brass dome skid at the nose, carrying about a quarter of the weight.")
    K(9, "16340 cell (owned) across the back, just above the lidar’s top.")
    K(10, "The ranger’s field: desk 50–90 mm ahead of the nose.")
    K(11, "Speaker (owned) flat on the floor behind the lidar, firing down; the motion sensor beside it.")
    K(12, "Driver (owned) flat on the upper floor, over the lidar.")
    K(13, "Body: an ivory card capsule 56 wide, 60 deep, 94 tall, corners r 10 in profile, on two 1.5 mm hoops; the slot’s lips are 1.0 mm rod.")
    views = [(f.svg(), "Front. Two big ivory wheels, a slim ivory capsule between them, two eyes up high and the black rotor low in its slot."),
             (s.svg(), "Side, face to the right. The Ø60 wheel covers the lower body and reaches behind it; the lidar plane runs 31 mm over the desk, out of the front slot."),
             (t.svg(), "Top, face at the top. The eye boards toe in; the lidar’s circle sits ahead of the axle, the cell behind.")]
    return dict(name="Wheelie", views=views, key=key,
                dims=f"74 W × 76 D × {BY1:.0f} H mm (body 56 × 60 × 94; the wheels reach 16 behind it) · wheels Ø60 at axle 30 · clearance 6 · about 218 g · lidar plane {LY0 + LIDAR_SCAN:.0f} mm up",
                mass=218, height=BY1, scan=LY0 + LIDAR_SCAN)


if __name__ == "__main__":
    concepts = [concept_a(), concept_b(), concept_c()]
    if "--png" in sys.argv:
        outdir = pathlib.Path(sys.argv[sys.argv.index("--png") + 1]); outdir.mkdir(parents=True, exist_ok=True)
        css = (HERE / "check_style.css").read_text()
        for c in concepts:
            for i, (svg, cap) in enumerate(c["views"]):
                p = outdir / f'{c["name"].lower()}_{i}.html'
                p.write_text(f"<!doctype html><meta charset=utf-8><style>{css}</style><div style='width:700px'>{svg}</div>")
                subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                                "--window-size=720,900", f"--screenshot={outdir / (p.stem + '.png')}", f"file://{p}"],
                               check=True, capture_output=True, timeout=90)
        print("rendered", outdir)
    else:
        import page
        page.write(concepts)
