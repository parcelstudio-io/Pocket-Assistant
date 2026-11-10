"""Mars rover: the drum, as files SendCutSend's laser takes.

The reference's wheels are four solid aluminium drums that PCBWay machined (3:16 to 3:44 in its video): about 30 mm
across and about 22 mm wide (three-quarters of their diameter, read off 3:36 to 3:42), with about 15 square grooves
along the rim and a small hole through the middle. He builds each tread round one of them, the rods laid in its grooves
and tied with thread (4:22). This is the laser's version. The thickest plate that still takes fine seats is 3/8 in
(9.53 mm) 6061 aluminium: SendCutSend's minimum hole there is 2.16 mm, so each plank's pin is a 3/32 in brass tube,
2.38 mm, in a round seat. Two identical halves, glued face to face on the brass hub, make a drum 19.05 mm wide, close to
the reference's. (A single 1/2 in plate would be one piece but only 12.7 mm wide, with 11 coarse seats for 1/8 in
pins.) Rev I (2026-11-09), at the builder's word ("stick to the 3.5 centimeter diameter"; "the body can be longer by a
little bit"): 35 mm over the teeth, sixteen seats 6.5 mm apart, the drums' centres 52 mm apart. Four drums; order ten
halves.

Writes, next to this script (edit the numbers here, not the outputs):
  mars-rover-drum.dxf   the cut, one half: one closed outline and the 4.1 mm hole, in mm (R12 DXF)
  mars-rover-drum.stl   one half, 9.53 mm thick
  mars-rover-drum.svg   the half at 1:1, in mm
  mars-rover-drum.png   a preview: the drum with the planks seated round it, and a wheel cut through its axle

The outline and the writers are gear_plate.py's; only the standard library, and headless Chrome for the preview.
"""
from __future__ import annotations

import math
import pathlib
import subprocess
import tempfile

from gear_plate import clearance, local, outline, path_d, poly_area, write_dxf, write_stl

HERE = pathlib.Path(__file__).resolve().parent
NAME = "mars-rover-drum"

# ----------------------------------------------------------------------------- the drum (mm)
Z = 16                                    # seats: the most a 35 mm drum takes with its teeth over the laser's bridge
R_TIP = 17.5                              # 35 mm over the teeth (Rev I); the reference's are about 30
LIFT = 0.8                                # the tooth tips stand 0.8 mm beyond the pins' line
PIN_D = 2.381                             # the planks' pins: 3/32 in brass tube, 0.014 in wall
SEAT_R = PIN_D / 2 + 0.125                # the laser's +/-0.127 mm never pinches a pin
FLANK = math.radians(15.0)                # steep flanks: at 40° (the plate's) they would eat the teeth
THICK = 9.53                              # 0.375 in 6061-T6 aluminium: one half of the drum in one cut
HALVES = 2                                # glued face to face: 19.05 mm, the reference's drums are about 22
WIDTH = HALVES * THICK
HOLE = 4.1                                # a slip fit on the owned 4 mm brass tube
MIN_HOLE, REC_HOLE, MIN_BRIDGE, HOLE_EDGE = 2.159, 3.327, 3.632, 2.870   # SendCutSend, 0.375 in 6061, read 2026-11-07

# ----------------------------------------------------------------------------- the tread it carries
ROD1 = 1.0                                # the planks' 1 mm face rods
TUBE_WALL = 0.356                         # the pin tube's wall, 0.014 in
GUIDE, PIN_OUT = 0.4, 2.0                 # the loops ride 0.4 mm outside each face; the pins stand 2 mm out for them
LOOP_WIRE = 0.51                          # 24-gauge nickel silver
TUBE4 = (4.0, 3.0)                        # the owned 4 mm brass tube, OD and ID: the drum's hub
CENTRES = 8                               # the drums' centres, in plank pitches: 52 mm, Rev I's longer body

STEP = 2 * math.pi / Z
R_PIN = R_TIP - LIFT                      # 16.7: the pins' line
RF = R_PIN - SEAT_R                       # the bottom of a seat
PITCH = 2 * R_PIN * math.sin(math.pi / Z) # 6.52: the plank pitch
H_FACE = math.sqrt((PIN_D / 2 + ROD1 / 2) ** 2 - (ROD1 / 2) ** 2)   # the face rods' centres, out from the pin's
R_FACE = R_PIN + H_FACE + ROD1 / 2        # 18.81: the tread's face
PLANK_L = WIDTH + 2 * GUIDE               # 19.85: the face rods
PIN_L = PLANK_L + 2 * PIN_OUT             # 23.85: the pin tube, with its ends for the loops
HUB_IN = 1.8                              # the hub reaches 1.8 mm in from the inner face, to the gearmotor's boss (build_page.py)
HUB_L = HUB_IN + WIDTH + 0.5              # 21.4: the brass tube through both halves, 0.5 mm proud of the outer face
PLANKS = Z + 2 * CENTRES                  # 32 a track


def planks_round():
    """The planks seated round the drum: for each seat, the pin tube's centre and the two face rods' (x, y)."""
    out = []
    for j in range(Z):
        phi = (j + 0.5) * STEP
        out.append((local(phi, 0.0, R_PIN), [local(phi, sgn * ROD1 / 2, R_PIN + H_FACE) for sgn in (-1, 1)]))
    return out


def write_svg(pts, path):
    v = math.ceil(R_TIP + 1)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{2 * v}mm" height="{2 * v}mm" viewBox="{-v} {-v} {2 * v} {2 * v}">'
           f'<path d="{path_d(pts, 0, 0, 1)}" fill="none" stroke="#000" stroke-width="0.05"/>'
           f'<circle cx="0" cy="0" r="{HOLE / 2}" fill="none" stroke="#000" stroke-width="0.05"/></svg>')
    path.write_text(svg)


def preview_svg(pts):
    """The drum face on with the planks round it, and one wheel cut through its axle, at up to 13 px per mm."""
    W, H, s = 1200, 700, min(13.0, 200.0 / R_TIP)
    ink, ink2, alu, alu_e, ivory, brass, brass_e, bore, loop = ("#1b1d21", "#5d636c", "#d3d6db", "#7d838c", "#f4efe2",
                                                                "#d9b45a", "#9c7a2a", "#fbfaf7", "#a9adb3")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>',
         f'<text x="30" y="44" font-size="26" font-weight="700" fill="{ink}">The drum: two halves, one wheel</text>',
         f'<text x="30" y="72" font-size="15" fill="{ink2}">{Z} seats, {2 * R_TIP:.1f} mm over the teeth, {WIDTH:.2f} mm wide: two 3/8 in (9.53 mm) halves of 6061 aluminium, '
         f'laser cut and glued face to face.</text>',
         f'<text x="30" y="94" font-size="15" fill="{ink2}">Each plank\'s pin is a 3/32 in brass tube. Four drums; order ten halves.</text>']
    # A: face on, the face sprayed ivory to just under the seats, the teeth bare
    cx, cy = 280, 385
    o.append(f'<text x="40" y="132" font-size="17" font-weight="700" fill="{ink}">Face on, with the planks seated</text>')
    o.append(f'<path d="{path_d(pts, cx, cy, s)}" fill="{alu}" stroke="{alu_e}" stroke-width="1"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{(RF - 0.6) * s:.1f}" fill="{ivory}" stroke="{alu_e}" stroke-width="0.6" stroke-dasharray="3 3"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{TUBE4[0] / 2 * s:.1f}" fill="{brass}" stroke="{brass_e}" stroke-width="1"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{TUBE4[1] / 2 * s:.1f}" fill="{bore}" stroke="{brass_e}" stroke-width="0.6"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R_PIN * s:.1f}" fill="none" stroke="{ink2}" stroke-width="0.6" stroke-dasharray="4 4"/>')
    for pin, faces in planks_round():
        if pin[1] > 0.5:                                    # the lower half only, as a tread wraps a drum
            continue
        tri = " ".join(f"{cx + x * s:.1f},{cy - y * s:.1f}" for x, y in [pin] + faces)
        o.append(f'<polygon points="{tri}" fill="{brass}" stroke="{brass_e}" stroke-width="0.6"/>')
        for x, y in faces:
            o.append(f'<circle cx="{cx + x * s:.1f}" cy="{cy - y * s:.1f}" r="{ROD1 / 2 * s:.1f}" fill="{brass}" stroke="{brass_e}" stroke-width="0.6"/>')
        o.append(f'<circle cx="{cx + pin[0] * s:.1f}" cy="{cy - pin[1] * s:.1f}" r="{PIN_D / 2 * s:.1f}" fill="{brass}" stroke="{brass_e}" stroke-width="0.6"/>')
        o.append(f'<circle cx="{cx + pin[0] * s:.1f}" cy="{cy - pin[1] * s:.1f}" r="{(PIN_D / 2 - TUBE_WALL) * s:.1f}" fill="{bore}" stroke="{brass_e}" stroke-width="0.4"/>')
    y_d = cy - R_TIP * s - 26
    o.append(f'<path d="M{cx - R_TIP * s:.1f},{y_d} L{cx + R_TIP * s:.1f},{y_d} M{cx - R_TIP * s:.1f},{y_d - 6} L{cx - R_TIP * s:.1f},{y_d + 6} M{cx + R_TIP * s:.1f},{y_d - 6} L{cx + R_TIP * s:.1f},{y_d + 6}" stroke="{ink}" stroke-width="1"/>')
    o.append(f'<text x="{cx}" y="{y_d - 8}" font-size="15" text-anchor="middle" fill="{ink}">{2 * R_TIP:.1f} over the teeth</text>')
    for txt, yy in ((f"{Z} seats", cy - 50), ("face sprayed ivory, teeth bare", cy - 30), (f"hole {HOLE:.1f}, the brass tube in it", cy + 46),
                    (f"the pins' line, {2 * R_PIN:.1f}, dashed", cy + 66)):
        o.append(f'<text x="{cx}" y="{yy}" font-size="13" text-anchor="middle" fill="{ink2}">{txt}</text>')
    o.append(f'<text x="40" y="{cy + R_TIP * s + 40:.0f}" font-size="13" fill="{ink2}">Each pin tube sits in a round seat, {SEAT_R - PIN_D / 2:.3f} mm loose;</text>')
    o.append(f'<text x="40" y="{cy + R_TIP * s + 58:.0f}" font-size="13" fill="{ink2}">the planks are {PITCH:.2f} mm apart, the tooth tips {R_FACE - R_TIP:.1f} mm inside the tread\'s face.</text>')
    # B: a wheel cut through its axle (axle horizontal; the drum stands up)
    bx, by, sb = 600, 395, s
    X = lambda x: bx + x * sb          # noqa: E731  x along the axle, from the face rods' inner end
    Y = lambda r: by - r * sb          # noqa: E731
    o.append(f'<text x="560" y="132" font-size="17" font-weight="700" fill="{ink}">A wheel, cut through its axle</text>')
    x0, x1 = GUIDE, GUIDE + WIDTH                           # the drum's faces
    for k in range(HALVES):                                 # each half, cut through a seat: solid to its bottom, the teeth beyond
        xa = x0 + k * THICK
        for sgn in (1, -1):
            o.append(f'<rect x="{X(xa):.1f}" y="{min(Y(sgn * R_TIP), Y(sgn * RF)):.1f}" width="{THICK * sb:.1f}" height="{(R_TIP - RF) * sb:.1f}" fill="#eceef1" stroke="{alu_e}" stroke-width="0.6" stroke-dasharray="3 2"/>')
            o.append(f'<rect x="{X(xa):.1f}" y="{min(Y(sgn * RF), Y(sgn * HOLE / 2)):.1f}" width="{THICK * sb:.1f}" height="{(RF - HOLE / 2) * sb:.1f}" fill="{alu}" stroke="{alu_e}"/>')
    for sgn in (1, -1):
        for xf in (x0, x1):                                 # the sprayed faces
            o.append(f'<rect x="{X(xf) - 2:.1f}" y="{min(Y(sgn * (RF - 0.6)), Y(sgn * HOLE / 2)):.1f}" width="4" height="{(RF - 0.6 - HOLE / 2) * sb:.1f}" fill="{ivory}" stroke="{alu_e}" stroke-width="0.4"/>')
    xh = GUIDE - HUB_IN
    o.append(f'<rect x="{X(xh):.1f}" y="{Y(TUBE4[0] / 2):.1f}" width="{HUB_L * sb:.1f}" height="{TUBE4[0] * sb:.1f}" fill="{brass}" stroke="{brass_e}"/>')
    o.append(f'<rect x="{X(xh):.1f}" y="{Y(TUBE4[1] / 2):.1f}" width="{HUB_L * sb:.1f}" height="{TUBE4[1] * sb:.1f}" fill="{bore}" stroke="{brass_e}" stroke-width="0.6"/>')
    for sgn in (1, -1):                                     # a plank at the top and one at the bottom
        rp, rf = sgn * R_PIN, sgn * (R_PIN + H_FACE)
        o.append(f'<rect x="{X(-PIN_OUT):.1f}" y="{Y(rp + PIN_D / 2):.1f}" width="{PIN_L * sb:.1f}" height="{PIN_D * sb:.1f}" fill="{brass}" stroke="{brass_e}"/>')
        o.append(f'<rect x="{X(0):.1f}" y="{Y(rf + ROD1 / 2):.1f}" width="{PLANK_L * sb:.1f}" height="{ROD1 * sb:.1f}" fill="{brass}" stroke="{brass_e}"/>')
        for xl in (-PIN_OUT / 2, PLANK_L + PIN_OUT / 2):
            o.append(f'<rect x="{X(xl) - LOOP_WIRE * sb / 2:.1f}" y="{Y(rp + PIN_D / 2 + 0.05 + LOOP_WIRE):.1f}" width="{LOOP_WIRE * sb:.1f}" height="{(PIN_D + 0.1 + 2 * LOOP_WIRE) * sb:.1f}" fill="{loop}" stroke="{ink2}" stroke-width="0.5"/>')

    def dim(a, b, yy, txt, up=True):
        o.append(f'<path d="M{X(a):.1f},{yy} L{X(b):.1f},{yy} M{X(a):.1f},{yy - 5} L{X(a):.1f},{yy + 5} M{X(b):.1f},{yy - 5} L{X(b):.1f},{yy + 5}" stroke="{ink}" stroke-width="1"/>')
        o.append(f'<text x="{(X(a) + X(b)) / 2:.1f}" y="{yy - 8 if up else yy + 18}" font-size="13" text-anchor="middle" fill="{ink}">{txt}</text>')
    dim(-PIN_OUT, PLANK_L + PIN_OUT, Y(R_FACE + 0.6) - 14, f"pin tube {PIN_L:.1f}")
    dim(x0, x1, Y(-R_FACE - 0.6) + 16, f"drum {WIDTH:.2f}: two halves of {THICK:.2f}", up=False)
    notes = (("two 3/8 in 6061 halves, glued", 50), ("face to face; dashed, the teeth", 70), ("through both: the 4 mm brass tube,", 98),
             ("3 mm inside, glued in; on the", 118), ("motor's shaft or the idler's M3", 138), ("each plank: a 3/32 in brass tube", 166),
             ("on top, two 1 mm rods below it", 186), (f"the loops ride {GUIDE:.1f} mm outside", 214), ("each face: they keep the tread on", 234))
    for txt, dy in notes:
        o.append(f'<text x="{X(PLANK_L + PIN_OUT) + 24:.1f}" y="{by - 150 + dy}" font-size="13" fill="{ink2}">{txt}</text>')
    o.append(f'<text x="30" y="{H - 18}" font-size="12" fill="{ink2}">Generated by mars_rover/cad/drum.py: the DXF for SendCutSend\'s laser, the STL, the SVG at 1:1.</text>')
    o.append("</svg>")
    return "".join(o)


def main():
    pts, half = outline(z=Z, r_pin=R_PIN, r_tip=R_TIP, seat_r=SEAT_R, flank=FLANK)
    # SendCutSend's limits for 3/8 in 6061, and what the tread relies on
    tip = (STEP - 2 * half) * R_TIP
    assert tip >= MIN_BRIDGE, f"tooth tip {tip:.2f} mm: under the laser's {MIN_BRIDGE} mm bridge at 3/8 in"
    assert 2 * SEAT_R >= MIN_HOLE, f"seat {2 * SEAT_R:.2f} mm: under the laser's {MIN_HOLE} mm hole at 3/8 in"
    assert RF - HOLE / 2 > HOLE_EDGE + 3.0, "the hole leaves a ring of metal under the seats"
    assert 2 * R_TIP >= 25.4, "SendCutSend's smallest 3/8 in part is 0.75 x 1.00 in"
    assert R_FACE - R_TIP > 0.3, "the teeth stay under the tread's face"
    pin_gap = min(clearance(pts, pin, near=6.0) for pin, _ in planks_round()) - PIN_D / 2
    face_gap = min(clearance(pts, f, near=6.0) for _, faces in planks_round() for f in faces) - ROD1 / 2
    assert 0.1 <= pin_gap <= 0.15, f"a pin tube must sit in its seat with the laser's tolerance ({pin_gap:.3f})"
    assert face_gap > 0.15, f"the tooth flanks must clear the face rods ({face_gap:.2f})"
    assert PITCH - PIN_D > 3.0, "the pins need room between them for the loops and to turn round the drum"
    ang = [math.atan2(y, x) for x, y in pts]
    assert all(((ang[(i + 1) % len(ang)] - ang[i] + math.pi) % (2 * math.pi) - math.pi) > 0 for i in range(len(ang))), "the edge must be star-shaped"
    area = poly_area(pts) - math.pi * (HOLE / 2) ** 2
    grams = area * THICK * 2.70e-3
    hub = math.pi / 4 * (TUBE4[0] ** 2 - TUBE4[1] ** 2) * HUB_L * 8.5e-3
    pin_g = math.pi / 4 * (PIN_D ** 2 - (PIN_D - 2 * TUBE_WALL) ** 2) * PIN_L * 8.5e-3
    plank_g = pin_g + 2 * PLANK_L * math.pi / 4 * ROD1 ** 2 * 8.5e-3 + 0.05
    loop_g = math.pi / 4 * LOOP_WIRE ** 2 * (2 * (PITCH - 0.1) + math.pi * (PIN_D + 0.1 + LOOP_WIRE)) * 8.7e-3
    tread = 2 * PLANKS * (plank_g + 2 * loop_g)
    write_dxf(pts, HERE / f"{NAME}.dxf", hole=HOLE)
    n = write_stl(pts, HERE / f"{NAME}.stl", hole=HOLE, thick=THICK, title=f"Mars rover drum half, {Z} seats, {2 * R_TIP:.1f} mm, {THICK:.2f} mm, mm")
    write_svg(pts, HERE / f"{NAME}.svg")
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "p.html"
        src.write_text("<!doctype html><meta charset=utf-8><style>html,body{margin:0}</style>" + preview_svg(pts))
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--window-size=1200,700",
                        f"--screenshot={HERE / (NAME + '.png')}", f"file://{src}"], check=True, capture_output=True, timeout=120)
    print(f"drum: {Z} seats, OD {2 * R_TIP:.1f}, {WIDTH:.2f} wide in {HALVES} halves, seat {2 * SEAT_R:.2f} (laser min {MIN_HOLE}, recommended {REC_HOLE}), "
          f"tooth tip {tip:.2f} (min {MIN_BRIDGE}), area {area:.0f} mm2, {grams:.1f} g a half, {HALVES * grams + hub:.1f} g a drum with its hub; STL {n} facets")
    print(f"tread: pin line r {R_PIN:.2f}, pitch {PITCH:.3f}, face r {R_FACE:.2f}; pin play {pin_gap:.3f}, face-rod clearance {face_gap:.2f}; "
          f"{PLANKS} planks a track, {tread:.1f} g for both, {4 * PLANKS} loops")


if __name__ == "__main__":
    main()
