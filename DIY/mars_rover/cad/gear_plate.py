"""Mars rover: the gear plate, as files a laser-cutting (or 3D-printing) service takes.

One plate is a 20-tooth sprocket gear, 30.0 mm over the teeth, cut from 1.52 mm (0.060 in) 304 stainless. Between the
teeth are round seats for the tread's 1 mm pin rods, the way the reference's drums are grooved for its rods (its
machined drum has about 15 grooves, counted on a notched disc of its profile at 3:43 in its video). Two plates make a wheel: they sit 8.2 mm
apart on the owned 4 mm brass tube, one at each end of the planks, so each plank's pin rod rests in a seat of both, and
the loops just outside the plates keep the tread on. Eight make the four wheels; order ten.

Writes, next to this script (edit the numbers here, not the outputs):
  mars-rover-gear-plate.dxf   the cut: one closed outline and the 4.1 mm hole, in mm (R12 DXF)
  mars-rover-gear-plate.stl   the same plate, 1.52 mm thick, for a 3D-printing service
  mars-rover-gear-plate.svg   the plate at 1:1, in mm
  mars-rover-gear-plate.png   a preview: the plate with the planks seated round it, and a wheel cut through its axle

Only the standard library; the preview is rendered by headless Chrome, as the build page's PNGs are.
"""
from __future__ import annotations

import math
import pathlib
import struct
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
NAME = "mars-rover-gear-plate"

# ----------------------------------------------------------------------------- the plate (mm)
Z = 20                                    # teeth: the reference has about 15; 20 keeps our 2 mm planks close together
R_TIP = 15.0                              # 30.0 mm over the teeth, the reference's drum size
SEAT_R = 0.625                            # each seat: the 1 mm pin rod with 0.125 mm all round, the laser's +/-0.127
FLANK = math.radians(40.0)                # flanks open 40° from the radial: the pins roll in and out, the face rods clear
THICK = 1.52                              # 0.060 in (16 gauge) 304 stainless
HOLE = 4.1                                # a slip fit on the owned 4 mm brass tube, soldered with the Harris flux

# ----------------------------------------------------------------------------- the tread it carries (from build_page.py)
ROD1 = 1.0                                # the planks' 1 mm brass rods
PLANK_L, PIN_OUT, GUIDE = 12.0, 2.0, 0.4  # plank length, pin ends, the loops' clearance outside each plate
LOOP_WIRE = 0.51                          # 24-gauge nickel silver
TUBE4, TUBE5 = (4.0, 3.0), (5.0, 4.0)     # owned brass tubes, OD and ID

STEP = 2 * math.pi / Z
R_PIN = R_TIP - 0.7                       # 14.3: the pin rods' line, the tooth tips 0.7 mm beyond it
RA = R_TIP
RF = R_PIN - SEAT_R                       # 13.68: the bottom of a seat, the plate's root
PITCH = 2 * R_PIN * math.sin(math.pi / Z) # 4.47: the plank pitch
R_FACE = R_PIN + ROD1 * math.sqrt(3) / 2 + ROD1 / 2   # 15.67: the tread's face
SPACER = PLANK_L - 2 * GUIDE - 2 * THICK  # 8.16 between the plates


def local(phi, a, b):
    """A point a mm along the turning direction and b mm out from the axle, in the frame of the seat at angle phi."""
    return (b * math.cos(phi) - a * math.sin(phi), b * math.sin(phi) + a * math.cos(phi))


def flank_to_tip(t, d, r_tip=R_TIP):
    """How far along direction d from point t the flank reaches the tip circle."""
    td = t[0] * d[0] + t[1] * d[1]
    return -td + math.sqrt(td * td - (t[0] ** 2 + t[1] ** 2) + r_tip ** 2)


def outline(n_seat=14, n_flank=5, n_tip=6, z=Z, r_pin=R_PIN, r_tip=R_TIP, seat_r=SEAT_R, flank=FLANK):
    """The plate's edge, counter-clockwise, seat by seat: down the left flank, round the seat's bottom, up the right
    flank, along the tip to the next seat. Each flank is a straight line tangent to its seat circle. Every point's angle
    grows, so the edge is star-shaped and the STL's fan of triangles stays clean. drum.py draws its drum with it too."""
    step = 2 * math.pi / z
    c, s = math.cos(flank), math.sin(flank)
    t_l, t_r = (-seat_r * c, r_pin - seat_r * s), (seat_r * c, r_pin - seat_r * s)
    d_l, d_r = (-s, c), (s, c)
    u_l, u_r = flank_to_tip(t_l, d_l, r_tip), flank_to_tip(t_r, d_r, r_tip)
    tip_l = (t_l[0] + u_l * d_l[0], t_l[1] + u_l * d_l[1])
    half = math.atan2(-tip_l[0], tip_l[1])                  # half a seat's opening at the tip, in radians
    pts = []
    for j in range(z):
        phi = math.pi / 2 + (j + 0.5) * step - math.pi / 2  # the frame turns with the seat; b points out along phi + 90°
        for k in range(n_flank):                            # left flank, tip to seat
            f = u_l * (1 - k / n_flank)
            pts.append(local(phi, t_l[0] + f * d_l[0], t_l[1] + f * d_l[1]))
        for k in range(n_seat + 1):                         # the seat, through its bottom
            th = math.pi + flank + (math.pi - 2 * flank) * k / n_seat
            pts.append(local(phi, seat_r * math.cos(th), r_pin + seat_r * math.sin(th)))
        for k in range(1, n_flank + 1):                     # right flank, seat to tip
            f = u_r * k / n_flank
            pts.append(local(phi, t_r[0] + f * d_r[0], t_r[1] + f * d_r[1]))
        a0, a1 = half, step - half                          # the tip, to the next seat's left flank
        for k in range(1, n_tip):
            a = a0 + (a1 - a0) * k / n_tip
            pts.append(local(phi, r_tip * math.sin(a), r_tip * math.cos(a)))
    return pts, half


def planks_round():
    """The planks seated round the plate: for each seat, the pin rod and the two face rods (x, y)."""
    out = []
    for j in range(Z):
        phi = (j + 0.5) * STEP
        rf = R_PIN + ROD1 * math.sqrt(3) / 2
        pin = local(phi, 0.0, R_PIN)
        faces = [local(phi, sgn * ROD1 / 2, rf) for sgn in (-1, 1)]
        out.append((pin, faces))
    return out


def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (ax * ax + ay * ay or 1e-12)))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


def clearance(pts, c, near=4.0):
    """Closest approach of the plate's edge to a point c."""
    best = 1e9
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        if math.dist(a, c) > near and math.dist(b, c) > near:
            continue
        best = min(best, seg_dist(c, a, b))
    return best


def poly_area(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2


# ----------------------------------------------------------------------------- writers
def write_dxf(pts, path, hole=HOLE):
    """R12 ASCII DXF, millimetres: one closed polyline (the edge) and one circle (the hole), both on layer CUT."""
    o = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "9", "$INSUNITS", "70", "4", "0", "ENDSEC",
         "0", "SECTION", "2", "ENTITIES",
         "0", "POLYLINE", "8", "CUT", "66", "1", "70", "1", "10", "0.0", "20", "0.0", "30", "0.0"]
    for x, y in pts:
        o += ["0", "VERTEX", "8", "CUT", "10", f"{x:.4f}", "20", f"{y:.4f}", "30", "0.0"]
    o += ["0", "SEQEND", "8", "CUT",
          "0", "CIRCLE", "8", "CUT", "10", "0.0", "20", "0.0", "30", "0.0", "40", f"{hole / 2:.4f}",
          "0", "ENDSEC", "0", "EOF"]
    path.write_text("\n".join(o) + "\n")


def write_stl(pts, path, hole=HOLE, thick=THICK, title=f"Mars rover gear plate, {Z} teeth, 30 mm, mm"):
    """Binary STL of the plate, `thick` mm thick: the faces fan between the edge and the hole at matching angles."""
    tris = []

    def add(a, b, c):
        u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        ln = math.sqrt(sum(x * x for x in n))
        if ln > 1e-10:
            tris.append(((n[0] / ln, n[1] / ln, n[2] / ln), a, b, c))

    rh = hole / 2
    ring = [(rh * math.cos(math.atan2(y, x)), rh * math.sin(math.atan2(y, x))) for x, y in pts]
    z0, z1 = 0.0, thick
    for k in range(len(pts)):
        k1 = (k + 1) % len(pts)
        p0, p1, h0, h1 = pts[k], pts[k1], ring[k], ring[k1]
        add((*h0, z1), (*p0, z1), (*p1, z1)); add((*h0, z1), (*p1, z1), (*h1, z1))       # top
        add((*h0, z0), (*p1, z0), (*p0, z0)); add((*h0, z0), (*h1, z0), (*p1, z0))       # bottom
        add((*p0, z0), (*p1, z0), (*p1, z1)); add((*p0, z0), (*p1, z1), (*p0, z1))       # the edge
        add((*h0, z0), (*h1, z1), (*h1, z0)); add((*h0, z0), (*h0, z1), (*h1, z1))       # the hole
    with open(path, "wb") as f:
        f.write(title.encode().ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for n, a, b, c in tris:
            f.write(struct.pack("<12fH", *n, *a, *b, *c, 0))
    return len(tris)


def path_d(pts, sx, sy, s):
    return "M" + " L".join(f"{sx + x * s:.2f},{sy - y * s:.2f}" for x, y in pts) + "Z"


def write_svg(pts, path):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="32mm" height="32mm" viewBox="-16 -16 32 32">'
           f'<path d="{path_d(pts, 0, 0, 1)}" fill="none" stroke="#000" stroke-width="0.05"/>'
           f'<circle cx="0" cy="0" r="{HOLE / 2}" fill="none" stroke="#000" stroke-width="0.05"/></svg>')
    path.write_text(svg)


def preview_svg(pts):
    """The plate face on with the planks round it, and one wheel cut through its axle, at 13 px per mm."""
    W, H, s = 1200, 700, 13.0
    ink, ink2, steel, steel_e, brass, brass_e, loop = "#1b1d21", "#5d636c", "#d3d6db", "#7d838c", "#d9b45a", "#9c7a2a", "#a9adb3"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>',
         f'<text x="30" y="44" font-size="26" font-weight="700" fill="{ink}">The gear plate, and a wheel of two</text>',
         f'<text x="30" y="72" font-size="15" fill="{ink2}">{Z} teeth, 30.0 mm over the teeth, a round seat for a pin rod between each pair, 1.52 mm 304 stainless, laser cut. Two plates a wheel; order ten.</text>']
    # A: face on
    cx, cy = 280, 385
    o.append(f'<text x="40" y="118" font-size="17" font-weight="700" fill="{ink}">Face on, with the planks seated</text>')
    o.append(f'<path d="{path_d(pts, cx, cy, s)}" fill="{steel}" stroke="{steel_e}" stroke-width="1"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{HOLE / 2 * s:.1f}" fill="#fbfaf7" stroke="{steel_e}" stroke-width="1"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R_PIN * s:.1f}" fill="none" stroke="{ink2}" stroke-width="0.6" stroke-dasharray="4 4"/>')
    for pin, faces in planks_round():
        if pin[1] > 0.5:                                    # the lower half only, as a tread wraps a gear
            continue
        rods = [pin] + faces
        pts_ = " ".join(f"{cx + x * s:.1f},{cy - y * s:.1f}" for x, y in rods)
        o.append(f'<polygon points="{pts_}" fill="{brass}" stroke="{brass_e}" stroke-width="0.6"/>')
        for x, y in rods:
            o.append(f'<circle cx="{cx + x * s:.1f}" cy="{cy - y * s:.1f}" r="{ROD1 / 2 * s:.1f}" fill="{brass}" stroke="{brass_e}" stroke-width="0.6"/>')
    y_d = cy - RA * s - 26
    o.append(f'<path d="M{cx - RA * s:.1f},{y_d} L{cx + RA * s:.1f},{y_d} M{cx - RA * s:.1f},{y_d - 6} L{cx - RA * s:.1f},{y_d + 6} M{cx + RA * s:.1f},{y_d - 6} L{cx + RA * s:.1f},{y_d + 6}" stroke="{ink}" stroke-width="1"/>')
    o.append(f'<text x="{cx}" y="{y_d - 8}" font-size="15" text-anchor="middle" fill="{ink}">30.0 over the teeth</text>')
    for txt, yy in ((f"{Z} teeth", cy - 30), (f"hole {HOLE:.1f}", cy + 46), (f"the pin rods' line, {2 * R_PIN:.1f}, dashed", cy + 66)):
        o.append(f'<text x="{cx}" y="{yy}" font-size="13" text-anchor="middle" fill="{ink2}">{txt}</text>')
    o.append(f'<text x="40" y="{cy + RA * s + 40:.0f}" font-size="13" fill="{ink2}">Each plank\'s pin rod sits in a round seat, {SEAT_R - ROD1 / 2:.3f} mm loose;</text>')
    o.append(f'<text x="40" y="{cy + RA * s + 58:.0f}" font-size="13" fill="{ink2}">the planks are {PITCH:.2f} mm apart, the tooth tips {R_FACE - RA:.1f} mm inside the tread\'s face.</text>')
    # B: a wheel cut through its axle (axle horizontal; the plates stand up)
    bx, by, sb = 700, 395, 13.0
    X = lambda x: bx + x * sb          # noqa: E731  x along the axle, from the planks' inner end
    Y = lambda r: by - r * sb          # noqa: E731
    o.append(f'<text x="640" y="118" font-size="17" font-weight="700" fill="{ink}">A wheel, cut through its axle</text>')
    xa, xb = GUIDE, PLANK_L - GUIDE                         # the plates' outer faces
    plates = ((xa, xa + THICK), (xb - THICK, xb))
    o.append(f'<rect x="{X(xa - 0.4):.1f}" y="{Y(TUBE4[0] / 2):.1f}" width="{(xb - xa + 0.4) * sb:.1f}" height="{TUBE4[0] * sb:.1f}" fill="{brass}" stroke="{brass_e}"/>')
    o.append(f'<rect x="{X(xa - 0.4):.1f}" y="{Y(TUBE4[1] / 2):.1f}" width="{(xb - xa + 0.4) * sb:.1f}" height="{TUBE4[1] * sb:.1f}" fill="#fbfaf7" stroke="{brass_e}" stroke-width="0.6"/>')
    for sgn in (1, -1):
        o.append(f'<rect x="{X(plates[0][1]):.1f}" y="{min(Y(sgn * TUBE5[0] / 2), Y(sgn * TUBE4[0] / 2)):.1f}" width="{SPACER * sb:.1f}" height="{(TUBE5[0] - TUBE4[0]) / 2 * sb:.1f}" fill="{brass}" stroke="{brass_e}"/>')
    for p0, p1 in plates:                                  # cut through a seat: solid to its bottom, the teeth beyond
        for sgn in (1, -1):
            o.append(f'<rect x="{X(p0):.1f}" y="{min(Y(sgn * RA), Y(sgn * RF)):.1f}" width="{THICK * sb:.1f}" height="{(RA - RF) * sb:.1f}" fill="#eceef1" stroke="{steel_e}" stroke-width="0.6" stroke-dasharray="3 2"/>')
            o.append(f'<rect x="{X(p0):.1f}" y="{min(Y(sgn * RF), Y(sgn * HOLE / 2)):.1f}" width="{THICK * sb:.1f}" height="{(RF - HOLE / 2) * sb:.1f}" fill="{steel}" stroke="{steel_e}"/>')
    for sgn in (1, -1):                                    # a plank at the top and one at the bottom
        rp, rf = sgn * R_PIN, sgn * (R_PIN + ROD1 * math.sqrt(3) / 2)
        o.append(f'<rect x="{X(-PIN_OUT):.1f}" y="{Y(rp + ROD1 / 2):.1f}" width="{(PLANK_L + 2 * PIN_OUT) * sb:.1f}" height="{ROD1 * sb:.1f}" fill="{brass}" stroke="{brass_e}"/>')
        o.append(f'<rect x="{X(0):.1f}" y="{Y(rf + ROD1 / 2):.1f}" width="{PLANK_L * sb:.1f}" height="{ROD1 * sb:.1f}" fill="{brass}" stroke="{brass_e}"/>')
        for xl in (-PIN_OUT / 2, PLANK_L + PIN_OUT / 2):
            o.append(f'<rect x="{X(xl) - LOOP_WIRE * sb / 2:.1f}" y="{Y(rp + ROD1 / 2 + 0.05 + LOOP_WIRE):.1f}" width="{LOOP_WIRE * sb:.1f}" height="{(ROD1 + 0.1 + 2 * LOOP_WIRE) * sb:.1f}" fill="{loop}" stroke="{ink2}" stroke-width="0.5"/>')

    def dim(x0, x1, yy, txt, up=True):
        o.append(f'<path d="M{X(x0):.1f},{yy} L{X(x1):.1f},{yy} M{X(x0):.1f},{yy - 5} L{X(x0):.1f},{yy + 5} M{X(x1):.1f},{yy - 5} L{X(x1):.1f},{yy + 5}" stroke="{ink}" stroke-width="1"/>')
        o.append(f'<text x="{(X(x0) + X(x1)) / 2:.1f}" y="{yy - 8 if up else yy + 18}" font-size="13" text-anchor="middle" fill="{ink}">{txt}</text>')
    dim(0, PLANK_L, Y(R_FACE + 0.6) - 14, f"plank {PLANK_L:.0f}")
    bot = Y(-R_PIN - 2.2)
    dim(plates[0][0], plates[0][1], bot + 22, f"{THICK:.2f}", up=False)
    dim(plates[0][1], plates[1][0], bot + 22, f"{SPACER:.1f} apart", up=False)
    notes = (("plates: 1.52 mm stainless; dashed, the teeth", 70), ("between them: the 5 mm brass tube", 92), ("through both: the 4 mm brass tube, 3 mm inside,", 114),
             ("on the motor's shaft or the idler's M3 screw", 134), (f"the loops ride {GUIDE:.1f} mm outside each plate:", 162),
             ("they keep the tread on, both ways", 182), ("solder the stack with the Harris flux", 210))
    for txt, dy in notes:
        o.append(f'<text x="{X(PLANK_L + PIN_OUT) + 24:.1f}" y="{by - 150 + dy}" font-size="13" fill="{ink2}">{txt}</text>')
    o.append(f'<text x="30" y="{H - 18}" font-size="12" fill="{ink2}">Generated by mars_rover/cad/gear_plate.py: the DXF for laser cutting, the STL for 3D printing, the SVG at 1:1.</text>')
    o.append("</svg>")
    return "".join(o)


def main():
    pts, half = outline()
    # checks the plate and the tread rely on
    tip = (STEP - 2 * half) * R_TIP
    assert tip > 1.2, f"tooth tip {tip:.2f} mm: too fine for the laser"
    assert R_FACE - RA > 0.3, "the teeth stay under the tread's face"
    pin_gap = min(clearance(pts, pin) for pin, _ in planks_round()) - ROD1 / 2
    face_gap = min(clearance(pts, f) for _, faces in planks_round() for f in faces) - ROD1 / 2
    assert 0.1 <= pin_gap <= 0.15, f"a pin rod must sit in its seat with the laser's tolerance ({pin_gap:.3f})"
    assert face_gap > 0.15, f"the tooth flanks must clear the face rods ({face_gap:.2f})"
    assert PITCH > 2 * ROD1 + 1.0, "the planks need a gap between them to turn round the gear"
    assert HOLE / 2 < RF - 3.0, "the hole leaves a ring of steel under the seats"
    ang = [math.atan2(y, x) for x, y in pts]
    assert all(((ang[(i + 1) % len(ang)] - ang[i] + math.pi) % (2 * math.pi) - math.pi) > 0 for i in range(len(ang))), "the edge must be star-shaped"
    area = poly_area(pts) - math.pi * (HOLE / 2) ** 2
    grams = area * THICK * 7.93e-3
    write_dxf(pts, HERE / f"{NAME}.dxf")
    n = write_stl(pts, HERE / f"{NAME}.stl")
    write_svg(pts, HERE / f"{NAME}.svg")
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "p.html"
        src.write_text("<!doctype html><meta charset=utf-8><style>html,body{margin:0}</style>" + preview_svg(pts))
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--window-size=1200,700",
                        f"--screenshot={HERE / (NAME + '.png')}", f"file://{src}"], check=True, capture_output=True, timeout=120)
    print(f"plate: {Z} teeth, {len(pts)} edge points, OD {2 * RA:.1f}, seat bottoms {2 * RF:.2f}, tooth tip {tip:.2f}, "
          f"area {area:.0f} mm2, {grams:.2f} g each, {8 * grams:.0f} g for eight; STL {n} facets")
    print(f"tread: pin line r {R_PIN:.2f}, pitch {PITCH:.3f}, face r {R_FACE:.2f}; pin play {pin_gap:.2f}, face-rod clearance {face_gap:.2f}; "
          f"plates {SPACER:.2f} apart")


if __name__ == "__main__":
    main()
