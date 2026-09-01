#!/usr/bin/env python3
"""Parametric fit check for the Pocket AI Assistant pager (Rev A layout).

Run headless:  freecadcmd cad/fitcheck.py
Outputs (into cad/): pager_rev_a.FCStd, pager_rev_a.step, FITCHECK_REPORT.md

Named parts use manufacturer dimensions where a drawing exists; generic
SuperMini and INMP441 breakout envelopes remain provisional and must be
replaced with measurements from the received parts. The script then enforces
the layout rules that came out of the design review:

  R1  no two components intersect (pairwise common volume == 0)
  R2  every component fits inside the frame envelope, except the ESP32-C3,
      whose provisional 6 mm antenna region MUST clear the frame by >=15 mm
  R3  no other component or frame tube enters the antenna region plus its
      15 mm all-direction keep-out volume
  R4  a USB-C service corridor in front of the SuperMini's connector stays
      empty so the finished pager can be flashed
  R5  minimum air clearances between listed pairs (wire/insulation room)

Coordinates: x = width, y = height, z = depth; the OLED faces z = 0.
Tweak POS/SIZE values and re-run; the report tells you what broke.
"""

import os
import sys

import FreeCAD  # noqa: F401  (provided by freecadcmd)
import Part

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- frame envelope (mm) --------------------------------------------------
FRAME_W, FRAME_H, FRAME_D = 60.0, 45.0, 33.0
TUBE_R = 0.75  # 1.5 mm OD brass tube

# ---- components: name -> (pos xyz, size xyz, cls) -------------------------
# cls is retained for display/grouping; every real component is treated as
# conductive for antenna-clearance purposes.
PARTS = {
    #                      x      y      z       w      h      d
    "oled_326":        ((15.4,  10.0,   0.8), (29.2,  26.7,   6.2), "pcb"),
    # 12.09 mm above the carrier plus a conservative 1.54 mm tab allowance.
    "holder_bh123a":   (( 2.0,   2.0,  15.2), (43.0,  17.78, 13.63), "metal"),
    "speaker_box":     ((30.0,  22.0,   8.5), (21.0,  16.0,   7.8), "pcb"),
    "supermini":       ((59.5,  26.0,  26.0), (22.5,  18.0,   4.0), "pcb"),
    "amp_dfr0954":     (( 3.0,  24.0,  24.0), (18.0,  18.0,   7.1), "pcb"),
    "reg_s8v9f3":      ((26.0,  26.0,  28.0), (10.2,  16.5,   2.6), "pcb"),  # rotated 90deg
    "star_board":      ((38.0,  36.0,  22.0), (12.0,   8.0,   3.0), "pcb"),
    "switch_2810":     ((44.0,  22.0,  18.0), (15.2,  15.2,   2.5), "pcb"),
    "mic_inmp441":     (( 4.0,  30.0,  18.0), (14.0,  11.0,   3.5), "pcb"),
    "cap_220u":        (( 3.0,  17.0,   6.5), ( 6.3,   6.3,   6.0), "pcb"),
    "tact_button":     ((52.0,   4.0,   6.0), ( 6.0,   6.0,   7.3), "pcb"),
}

# The exact generic-board antenna dimensions are not published. Use a
# conservative provisional 6 mm region at the +x end, expanded 15 mm in all
# directions, then replace ANTENNA_LENGTH with the received board measurement.
ANTENNA_LENGTH = 6.0
ANTENNA_CLEARANCE = 15.0
ANT_KEEPOUT = ("ant_keepout", None)  # built from the supermini's placement
USB_CORRIDOR = ("usb_corridor", ((47.5, 27.0, 25.0), (12.0, 16.0, 6.0)))

# R5: required minimum clearances between pairs (mm of air for wire + insulation)
CLEARANCES = [
    ("holder_bh123a", "supermini", 3.0),   # cell away from the radio
    ("holder_bh123a", "oled_326", 1.5),
    ("holder_bh123a", "speaker_box", 2.0),
    ("holder_bh123a", "switch_2810", 2.0),
    ("holder_bh123a", "cap_220u", 2.0),
    ("amp_dfr0954", "reg_s8v9f3", 2.0),    # bead + wiring between them
    ("speaker_box", "mic_inmp441", 3.0),   # acoustic + wiring separation
    ("speaker_box", "oled_326", 1.5),
    ("speaker_box", "switch_2810", 1.5),
]


def box(name, pos, size):
    b = Part.makeBox(size[0], size[1], size[2])
    b.translate(FreeCAD.Vector(*pos))
    return b


def frame_tubes():
    """12 tube edges of the envelope box, as one compound."""
    W, H, D, r = FRAME_W, FRAME_H, FRAME_D, TUBE_R
    cyl = []

    def tube(p0, p1):
        v0, v1 = FreeCAD.Vector(*p0), FreeCAD.Vector(*p1)
        d = v1.sub(v0)
        c = Part.makeCylinder(r, d.Length, v0, d)
        cyl.append(c)

    for z in (0.0, D):
        tube((0, 0, z), (W, 0, z))
        tube((0, H, z), (W, H, z))
        tube((0, 0, z), (0, H, z))
        tube((W, 0, z), (W, H, z))
    for (x, y) in ((0, 0), (W, 0), (0, H), (W, H)):
        tube((x, y, 0), (x, y, D))
    return Part.makeCompound(cyl)


def main():
    doc = FreeCAD.newDocument("pager_rev_a")
    solids, cls = {}, {}
    for name, (pos, size, kind) in PARTS.items():
        solids[name] = box(name, pos, size)
        cls[name] = kind
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = solids[name]

    frame = frame_tubes()
    doc.addObject("Part::Feature", "frame").Shape = frame

    sm_pos, sm_size, _ = PARTS["supermini"]
    ant_end = sm_pos[0] + sm_size[0]
    ant_start = ant_end - ANTENNA_LENGTH
    keepout = box(
        "ant",
        (ant_start - ANTENNA_CLEARANCE,
         sm_pos[1] - ANTENNA_CLEARANCE,
         sm_pos[2] - ANTENNA_CLEARANCE),
        (ANTENNA_LENGTH + 2 * ANTENNA_CLEARANCE,
         sm_size[1] + 2 * ANTENNA_CLEARANCE,
         sm_size[2] + 2 * ANTENNA_CLEARANCE),
    )
    doc.addObject("Part::Feature", "ant_keepout").Shape = keepout
    corridor = box("usb", *USB_CORRIDOR[1])
    doc.addObject("Part::Feature", "usb_corridor").Shape = corridor

    report, failures = [], []

    def check(ok, label):
        report.append(("PASS" if ok else "FAIL") + "  " + label)
        if not ok:
            failures.append(label)

    # R1 pairwise collisions
    names = list(solids)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = solids[a].common(solids[b]).Volume
            check(v < 1e-6, f"R1 no overlap {a} vs {b}" +
                  ("" if v < 1e-6 else f" (common {v:.1f} mm^3)"))

    # R2 envelope containment / mandated antenna protrusion
    env = Part.makeBox(FRAME_W, FRAME_H, FRAME_D)
    for name, s in solids.items():
        inside = s.common(env).Volume
        frac = inside / s.Volume if s.Volume else 0.0
        if name == "supermini":
            nearest_frame_surface = FRAME_W + TUBE_R
            clearance = ant_start - nearest_frame_surface
            check(clearance >= ANTENNA_CLEARANCE,
                  f"R2 provisional antenna region clears frame by "
                  f"{clearance:.1f} mm (>={ANTENNA_CLEARANCE:g})")
        else:
            check(frac > 0.999, f"R2 {name} fully inside envelope "
                  f"({100 * frac:.1f}% in)")

    # R3 keep-out vs every other conductive/component envelope
    for name in [n for n in solids if n != "supermini"]:
        v = solids[name].common(keepout).Volume
        check(v < 1e-6, f"R3 keep-out clear of {name}")
    check(frame.common(keepout).Volume < 1e-6, "R3 keep-out clear of frame tubes")

    # R4 usb corridor free of every other component
    for name, s in solids.items():
        if name == "supermini":
            continue
        v = s.common(corridor).Volume
        check(v < 1e-6, f"R4 USB corridor clear of {name}")

    # R5 clearances
    for a, b, dmin in CLEARANCES:
        d = solids[a].distToShape(solids[b])[0]
        check(d >= dmin, f"R5 {a} <-> {b} clearance {d:.1f} mm (>= {dmin})")

    # frame vs components (tubes sit on the envelope border)
    for name, s in solids.items():
        v = s.common(frame).Volume
        check(v < 1e-6, f"R1 no overlap {name} vs frame tubes")

    doc.recompute()
    doc.saveAs(os.path.join(OUT_DIR, "pager_rev_a.FCStd"))
    Part.export([o for o in doc.Objects], os.path.join(OUT_DIR, "pager_rev_a.step"))

    passed = sum(1 for r in report if r.startswith("PASS"))
    lines = ["# Rev A fit-check report", "",
             f"FreeCAD {'.'.join(FreeCAD.Version()[:3])} · frame envelope "
             f"{FRAME_W:g} x {FRAME_H:g} x {FRAME_D:g} mm · "
             f"{passed}/{len(report)} checks pass", "",
             "> Geometric desk check only. Replace generic-board dimensions "
             "with caliper measurements and rerun before cutting the frame.", ""]
    lines += ["    " + r for r in report]
    with open(os.path.join(OUT_DIR, "FITCHECK_REPORT.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(report))
    print(f"\n{passed}/{len(report)} checks passed")
    if failures:
        sys.exit(1)


main()
