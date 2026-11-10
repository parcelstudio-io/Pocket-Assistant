"""3D model of Pip's brass-rod harness, in millimetres.

Axes: X left→right across the device (0..57 inside the frame), Y front→back
(0 = inner face of the front tube, 39 = back), Z up from the top of the card
that is the floor. Every conductor is a polyline with a radius and a net name.
The checker measures the air gap between every pair of conductors on different
nets, so the drawings and the step text come from numbers, not from a sketch.

Sources: part sizes from the builder's 28 Sept caliper measurements
(cardboard-mockup page); pin pitch 2.54 mm; INMP441 module 12 × 14 mm with two
rows of three 7.62 mm apart (component library data); the pinout from
CLAUDE.md's hardware contract.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# ---------------------------------------------------------------- constants
ROD_R = 0.5          # 1.0 mm K&S #9861 rod
LEAD_R = 0.28        # resistor / capacitor lead
STUB_R = 0.32        # 0.64 mm square header pin
BODY_R = 1.15        # 1/4 W resistor body
PITCH = 2.54
INSIDE_X, INSIDE_Y = 57.0, 39.0
MIN_GAP = 1.0        # air between different nets, else a sleeve is required
GOOD_GAP = 1.5       # comfortable

# ---------------------------------------------------------------- parts
# Header strips stay on (builder's choice, 2026-10-12): A1 and the amp stand 2.5 mm up on their
# strips (the amp shimmed level under its pin-free edge); the mic's strip is on top since it lies
# chip-down; the screen's strip hangs below its PCB. Long pins are clipped flush with the strips.
STRIP = 2.5
A1 = dict(x0=3.5, x1=21.5, y0=2.5, y1=24.5, z0=STRIP + 0.3, z1=STRIP + 1.9)
A1_RIGHT_X = 20.8    # pin centres, 0.7 mm in from the board edge
A1_LEFT_X = 4.2
A1_PIN_Y = [A1["y0"] + 2.1 + i * PITCH for i in range(8)]   # 4.6 … 22.4
A1_RIGHT = ["5V", "GND", "3V3", "GPIO4", "GPIO3", "GPIO2", "GPIO1", "GPIO0"]
A1_LEFT = ["GPIO5", "GPIO6", "GPIO7", "GPIO8", "GPIO9", "GPIO10", "GPIO20", "GPIO21"]
USB = dict(x0=8.3, x1=17.3, y0=0.8, y1=8.4, z0=A1["z1"], z1=A1["z1"] + 3.2)   # socket, shell = GND
A1_CHIP = dict(x0=9.5, x1=15.5, y0=12.0, y1=17.0, z0=A1["z1"], z1=A1["z1"] + 1.0)
A1_ANT = dict(x0=8.0, x1=17.0, y0=20.5, y1=24.5, z0=A1["z1"], z1=A1["z1"] + 1.0)
A1_BTN_L = dict(x0=5.2, x1=7.2, y0=3.0, y1=6.0, z0=A1["z1"], z1=A1["z1"] + 1.5)   # approximate
A1_BTN_R = dict(x0=17.8, x1=19.8, y0=3.0, y1=6.0, z0=A1["z1"], z1=A1["z1"] + 1.5)

AMP = dict(x0=30.0, x1=47.0, y0=3.7, y1=20.7, z0=STRIP, z1=STRIP + 1.6)
AMP_PIN_X = 30.7
AMP_PIN_Y = [AMP["y0"] + 0.9 + i * PITCH for i in range(7)]   # 4.6 … 19.9
AMP_PINS = ["VIN", "GND", "SD", "GAIN", "DIN", "BCLK", "LRC"]
AMP_CHIP = dict(x0=36.0, x1=40.0, y0=10.0, y1=14.0, z0=AMP["z1"], z1=AMP["z1"] + 1.0)
AMP_BLOCK = dict(x0=42.0, x1=50.0, y0=8.2, y1=16.2, z0=AMP["z1"], z1=AMP["z1"] + 7.4)  # terminal block + wire entries

# The AITRIP INMP441 module is a round board, Ø13 by the builder's calipers; this box is its
# bounding square for the clearance check, the drawings use the circle.
MIC_D = 13.0
MIC_C = (30.0, 31.5)
MIC = dict(x0=MIC_C[0] - MIC_D / 2, x1=MIC_C[0] + MIC_D / 2, y0=MIC_C[1] - MIC_D / 2, y1=MIC_C[1] + MIC_D / 2, z0=1.0, z1=2.6)   # flat, port up, on its chip
MIC_COL_X = [26.2, 33.8]                                              # the two rows, 7.62 apart
MIC_PIN_Y = [29.0, 31.54, 34.08]
MIC_PORT = MIC_C
# Drawn case: DIP-style numbering, L/R opposite GND, WS opposite VDD, SCK opposite SD.
MIC_LEFT = ["GND", "VDD", "SD"]       # front → back, the column that faces the channel
MIC_RIGHT = ["L/R", "WS", "SCK"]

SPK = dict(x0=37.0, x1=57.0, y0=24.5, y1=37.5, z0=0.0, z1=4.9)

SCREEN = dict(x0=17.5, x1=44.5, y0=2.5, y1=29.5, z0=17.5, z1=18.7)     # PCB; glass to 20.5; strip hangs 2.5 below
SCREEN_PARTS = dict(x0=19.0, x1=43.0, y0=6.0, y1=28.0, z0=16.3, z1=17.5)   # the header strip at the front is bare
SCREEN_PIN_Y = SCREEN["y0"] + 1.3
SCREEN_PIN_X = [27.2, 29.7, 32.3, 34.8]
SCREEN_PINS = ["SDA", "SCL", "VCC", "GND"]       # a GND-VCC-SCL-SDA module turned header-to-front
SCREEN_STUB = (13.0, 15.0)                         # stubs hang 2 mm below the strip under the PCB

BTN = dict(x0=9.0, x1=15.0, y0=1.0, y1=7.0, z0=USB["z1"], z1=USB["z1"] + 3.5)          # on the USB socket, Kapton under
BTN_PLUNGER_TOP = BTN["z1"] + 1.5
BTN_STUB_Z = BTN["z0"] + 0.5

CAP220 = dict(x0=50.5, x1=56.8, y0=3.0, y1=15.0, z0=0.0, z1=6.3)     # lying on the floor, right strip
CAP100N = dict(x0=32.0, x1=35.2, y0=4.25, y1=7.45, z0=AMP["z1"], z1=AMP["z1"] + 1.6)   # lying on the amp

FRAME_H_MIN = 22.0   # inside height the design needs (screen glass top 20.5 + air)
# A1 and the amp keep their headers (plastic strip underneath, long pins clipped flush); the
# stubs are the pins' short ends on the component side, about 1.4 mm above the board.
TOP_STUB = 1.4


@dataclass
class Cond:
    """A conductor: a polyline of points with one radius and one net."""
    name: str
    net: str
    pts: list
    r: float = ROD_R
    kind: str = "rod"            # rod | stub | lead | body | pin
    sleeve: list = field(default_factory=list)   # [(seg_index, t0, t1)] insulated stretches
    step: str = ""               # which build step adds it
    note: str = ""
    comp: str = ""               # component a lead/body belongs to (pairs inside one part are skipped)

    def segs(self):
        return [(self.pts[i], self.pts[i + 1]) for i in range(len(self.pts) - 1)]

    def length(self):
        return sum(dist(a, b) for a, b in self.segs())


def dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def seg_seg_dist(p1, q1, p2, q2):
    """Minimum distance between segments p1q1 and p2q2 (Ericson, Real-Time Collision Detection)."""
    d1 = [q1[i] - p1[i] for i in range(3)]
    d2 = [q2[i] - p2[i] for i in range(3)]
    r = [p1[i] - p2[i] for i in range(3)]
    a = sum(x * x for x in d1); e = sum(x * x for x in d2); f = sum(d2[i] * r[i] for i in range(3))
    EPS = 1e-9
    if a <= EPS and e <= EPS:
        return dist(p1, p2)
    if a <= EPS:
        s = 0.0; t = min(max(f / e, 0.0), 1.0)
    else:
        c = sum(d1[i] * r[i] for i in range(3))
        if e <= EPS:
            t = 0.0; s = min(max(-c / a, 0.0), 1.0)
        else:
            b = sum(d1[i] * d2[i] for i in range(3))
            denom = a * e - b * b
            s = min(max((b * f - c * e) / denom, 0.0), 1.0) if denom != 0 else 0.0
            t = (b * s + f) / e
            if t < 0:
                t = 0.0; s = min(max(-c / a, 0.0), 1.0)
            elif t > 1:
                t = 1.0; s = min(max((b - c) / a, 0.0), 1.0)
    c1 = [p1[i] + d1[i] * s for i in range(3)]
    c2 = [p2[i] + d2[i] * t for i in range(3)]
    return dist(c1, c2)


# ---------------------------------------------------------------- stubs
def stubs():
    out = []
    for name, y in zip(A1_RIGHT, A1_PIN_Y):
        out.append(Cond(f"A1 {name}", name, [(A1_RIGHT_X, y, A1["z1"]), (A1_RIGHT_X, y, A1["z1"] + TOP_STUB)], STUB_R, "stub"))
    for name, y in zip(A1_LEFT, A1_PIN_Y):
        out.append(Cond(f"A1 {name}", "AMPSD" if name == "GPIO5" else name, [(A1_LEFT_X, y, A1["z1"]), (A1_LEFT_X, y, A1["z1"] + TOP_STUB)], STUB_R, "stub"))
    for name, y in zip(AMP_PINS, AMP_PIN_Y):
        net = {"VIN": "5V", "GND": "GND", "SD": "AMPSD", "GAIN": "GAIN", "DIN": "GPIO3", "BCLK": "GPIO2", "LRC": "GPIO1"}[name]
        out.append(Cond(f"amp {name}", net, [(AMP_PIN_X, y, AMP["z1"]), (AMP_PIN_X, y, AMP["z1"] + TOP_STUB)], STUB_R, "stub"))
    for name, y in zip(MIC_LEFT, MIC_PIN_Y):
        net = {"GND": "GND", "VDD": "3V3", "SD": "GPIO4"}[name]
        out.append(Cond(f"mic {name}", net, [(MIC_COL_X[0], y, MIC["z1"] + STRIP), (MIC_COL_X[0], y, MIC["z1"] + STRIP + 2.0)], STUB_R, "stub"))
    for name, y in zip(MIC_RIGHT, MIC_PIN_Y):
        net = {"L/R": "GND", "WS": "GPIO1", "SCK": "GPIO2"}[name]
        out.append(Cond(f"mic {name}", net, [(MIC_COL_X[1], y, MIC["z1"] + STRIP), (MIC_COL_X[1], y, MIC["z1"] + STRIP + 2.0)], STUB_R, "stub"))
    for name, x in zip(SCREEN_PINS, SCREEN_PIN_X):
        net = {"SDA": "GPIO21", "SCL": "GPIO20", "VCC": "3V3", "GND": "GND"}[name]
        out.append(Cond(f"screen {name}", net, [(x, SCREEN_PIN_Y, SCREEN_STUB[0]), (x, SCREEN_PIN_Y, SCREEN_STUB[1])], STUB_R, "stub"))
    # button legs clipped to 1 mm, pointing sideways at the leg height; left pair = GPIO10, right pair = GND
    for (x, net) in ((BTN["x0"] - 0.5, "GPIO10"), (BTN["x1"] + 0.5, "GND")):
        for y in (BTN["y0"] + 1.25, BTN["y1"] - 1.25):
            sx = x - 1.0 if net == "GPIO10" else x + 1.0
            out.append(Cond(f"button {net} leg", net, [(x, y, BTN_STUB_Z), (sx, y, BTN_STUB_Z)], STUB_R, "stub"))
    return out


def stub_xy(group, name):
    if group == "A1":
        if name in A1_RIGHT:
            return (A1_RIGHT_X, A1_PIN_Y[A1_RIGHT.index(name)])
        return (A1_LEFT_X, A1_PIN_Y[A1_LEFT.index(name)])
    if group == "amp":
        return (AMP_PIN_X, AMP_PIN_Y[AMP_PINS.index(name)])
    if group == "mic":
        if name in MIC_LEFT:
            return (MIC_COL_X[0], MIC_PIN_Y[MIC_LEFT.index(name)])
        return (MIC_COL_X[1], MIC_PIN_Y[MIC_RIGHT.index(name)])
    if group == "screen":
        return (SCREEN_PIN_X[SCREEN_PINS.index(name)], SCREEN_PIN_Y)
    raise KeyError(name)


# ---------------------------------------------------------------- rods
Z_RAIL = 0.5     # rails lie on the card
Z_LOW = 5.0      # rods soldered alongside the 1.4 mm top stubs of A1 and the amp (boards 2.5 up on their strips)
Z_A1 = A1["z1"]  # 1.9
Z_AMP = AMP["z1"]  # 1.6


def rods():
    R = []
    ax, ay = A1_RIGHT_X, dict(zip(A1_RIGHT, A1_PIN_Y))
    lx, ly = A1_LEFT_X, dict(zip(A1_LEFT, A1_PIN_Y))
    px, py = AMP_PIN_X, dict(zip(AMP_PINS, AMP_PIN_Y))
    mL = dict(zip(MIC_LEFT, MIC_PIN_Y)); mR = dict(zip(MIC_RIGHT, MIC_PIN_Y))
    sx = dict(zip(SCREEN_PINS, SCREEN_PIN_X)); sy = SCREEN_PIN_Y
    LANE = 22.0          # the mic SD rod's lane along the channel, just right of A1's stubs

    # the two rails
    R.append(Cond("3V3 rail", "3V3", [(24.0, 2.5, Z_RAIL), (24.0, 23.5, Z_RAIL)], step="rails",
                  note="unpainted rod, or paint sanded off along its whole length"))
    R.append(Cond("GND rail", "GND", [(27.0, 2.0, Z_RAIL), (27.0, 23.5, Z_RAIL)], step="rails",
                  note="unpainted rod, or paint sanded off along its whole length"))
    # the 5 V rod, sleeved where it crosses both rails and passes under the screen taps
    R.append(Cond("5 V rod", "5V", [(ax, ay["5V"], Z_LOW), (px, py["VIN"], Z_LOW)], sleeve=[(0, 0.08, 0.92)], step="5v"))
    # the GND rod and its drop pin to the GND rail
    R.append(Cond("GND rod", "GND", [(ax, ay["GND"], Z_LOW), (px, py["GND"], Z_LOW)], step="gnd"))
    R.append(Cond("GND drop pin", "GND", [(27.0, ay["GND"], Z_LOW), (27.0, ay["GND"], Z_RAIL)], step="gnd",
                  note="a 3 mm piece of rod standing between the GND rod and the GND rail"))
    # A1 3V3 tap: low, then a hook down onto the 3V3 rail
    R.append(Cond("3V3 tap", "3V3", [(ax, ay["3V3"], 4.7), (24.0, ay["3V3"], 4.7), (24.0, ay["3V3"], Z_RAIL)], step="3v3"))
    # DIN
    R.append(Cond("DIN rod", "GPIO3", [(ax, ay["GPIO3"], Z_LOW), (px, py["DIN"], Z_LOW)], step="din"))
    # BCLK: A1 -> amp BCLK (tap in passing) -> up -> along the right of the amp -> mic SCK
    R.append(Cond("BCLK rod", "GPIO2", [
        (ax, ay["GPIO2"], Z_LOW), (px + 0.5, py["BCLK"], Z_LOW), (px + 0.5, py["BCLK"], 8.0),
        (36.0, py["BCLK"], 8.0), (36.0, mR["SCK"], 8.0), (MIC_COL_X[1], mR["SCK"], 8.0), (MIC_COL_X[1], mR["SCK"], 6.7)],
        step="bclk"))
    # WS: A1 -> amp LRC (tap) -> back along the amp's edge -> up -> over the mic's right column -> mic WS
    R.append(Cond("WS rod", "GPIO1", [
        (ax, ay["GPIO1"], Z_LOW), (px + 0.5, py["LRC"], Z_LOW), (px + 0.5, 23.5, Z_LOW), (px + 0.5, 23.5, 10.0),
        (MIC_COL_X[1], 23.5, 10.0), (MIC_COL_X[1], mR["WS"], 10.0), (MIC_COL_X[1], mR["WS"], 6.7)],
        step="ws"))
    # mic SD (GPIO4): out of the stub, up, back along the channel's left lane, in from the left at the SD stub
    R.append(Cond("mic SD rod", "GPIO4", [
        (ax, ay["GPIO4"], Z_LOW), (LANE, ay["GPIO4"], Z_LOW), (LANE, ay["GPIO4"], 8.0),
        (LANE, mL["SD"], 8.0), (MIC_COL_X[0], mL["SD"], 8.0), (MIC_COL_X[0], mL["SD"], 6.7)],
        step="micsd"))
    # amp SD (GPIO5): straight up the stub, back above A1's left stubs, across A1 and the channel high, down, onto the SD stub
    R.append(Cond("amp SD rod", "AMPSD", [
        (lx, ly["GPIO5"], Z_LOW), (lx, ly["GPIO5"], 10.5), (lx, 8.0, 10.5), (26.0, 8.0, 10.5),
        (26.0, py["SD"], 10.5), (26.0, py["SD"], Z_LOW), (px, py["SD"], Z_LOW)],
        step="ampsd"))
    # I2C: out to the left lane, up, forward, across A1 and the channel, forward to the screen stubs
    R.append(Cond("SCL rod", "GPIO20", [
        (lx, ly["GPIO20"], Z_LOW), (2.7, ly["GPIO20"], Z_LOW), (2.7, ly["GPIO20"], 10.5), (2.7, 13.5, 10.5),
        (sx["SCL"], 13.5, 10.5), (sx["SCL"], sy, 10.5), (sx["SCL"], sy, SCREEN_STUB[0] + 0.7)],
        sleeve=[(2, 0.0, 1.0), (3, 0.0, 1.0)], step="scl", note="sleeved along the left lane and across A1, where SDA runs 2 mm above it"))
    R.append(Cond("SDA rod", "GPIO21", [
        (lx, ly["GPIO21"], Z_LOW), (2.7, ly["GPIO21"], Z_LOW), (2.7, ly["GPIO21"], 12.5), (2.7, 13.5, 12.5),
        (sx["SDA"], 13.5, 12.5), (sx["SDA"], sy, 12.5), (sx["SDA"], sy, SCREEN_STUB[0] + 0.7)],
        step="sda"))
    # screen power: the outer stub (GND) low and forward to the GND rail; the inner (VCC) higher to the 3V3 rail
    R.append(Cond("screen GND tap", "GND", [
        (sx["GND"], sy, SCREEN_STUB[0] + 0.7), (sx["GND"], sy, 6.0), (sx["GND"], 2.0, 6.0), (27.0, 2.0, 6.0), (27.0, 2.0, Z_RAIL)],
        step="scrpwr"))
    R.append(Cond("screen VCC tap", "3V3", [
        (sx["VCC"], sy, SCREEN_STUB[0] + 0.7), (sx["VCC"], sy, 8.0), (sx["VCC"], 3.3, 8.0), (24.0, 3.3, 8.0), (24.0, 3.3, Z_RAIL)],
        sleeve=[(2, 0.0, 1.0)], step="scrpwr", note="sleeved along its run: it passes 1.3 mm from the VIN stub and over the GND tap's drop"))
    # button: GPIO10 up, then over A1 well left of the chip, down to the button's back-left leg; the GND leg to A1's GND stub
    R.append(Cond("button rod", "GPIO10", [
        (lx, ly["GPIO10"], Z_LOW), (lx, ly["GPIO10"], BTN_STUB_Z), (6.0, ly["GPIO10"], BTN_STUB_Z), (6.0, BTN["y1"] - 1.25, BTN_STUB_Z), (BTN["x0"] - 0.5, BTN["y1"] - 1.25, BTN_STUB_Z)],
        sleeve=[(3, 0.45, 0.95)], step="button", note="a short sleeve where it passes under the amp SD rod"))
    R.append(Cond("button GND rod", "GND", [
        (BTN["x1"] + 0.5, BTN["y1"] - 1.25, BTN_STUB_Z), (19.3, ay["GND"], BTN_STUB_Z), (19.3, ay["GND"], 5.5), (ax, ay["GND"], 5.5)],
        step="button"))
    # mic taps: the GND stub's rod runs forward low beside the column; VDD rises and runs forward above the column
    R.append(Cond("mic GND tap", "GND", [
        (MIC_COL_X[0] + 0.4, mL["GND"], 6.0), (MIC_COL_X[0] + 0.4, 24.0, 6.0), (27.0, 24.0, 6.0), (27.0, 23.5, 6.0), (27.0, 23.5, Z_RAIL)],
        step="mictaps"))
    R.append(Cond("mic VDD tap", "3V3", [
        (MIC_COL_X[0], mL["VDD"], 6.9), (MIC_COL_X[0], mL["VDD"], 9.0), (MIC_COL_X[0], 24.0, 9.0), (24.6, 24.0, 9.0), (24.6, 23.5, 9.0), (24.6, 23.5, Z_RAIL)],
        step="mictaps"))
    R.append(Cond("L/R link", "GND", [(MIC_COL_X[1], mR["L/R"], 6.9), (MIC_COL_X[0], mL["GND"], 6.9)], step="mictaps",
                  note="L/R and GND face each other on this module, so the link is one straight piece across the board's front edge"))
    return R


def small_parts():
    """Resistors and capacitors: leads (bare) and bodies (insulated, but kept clear mechanically)."""
    P = []
    ax, ay = A1_RIGHT_X, dict(zip(A1_RIGHT, A1_PIN_Y))
    px, py = AMP_PIN_X, dict(zip(AMP_PINS, AMP_PIN_Y))
    mL = dict(zip(MIC_LEFT, MIC_PIN_Y))
    LANE = 22.0
    # R1 amp SD pull-down: a U lying over the amp board, return along the GND stub's line
    P.append(Cond("R1 lead a", "AMPSD", [(px, py["SD"], 5.1), (33.0, py["SD"], 6.3)], LEAD_R, "lead", step="r12", comp="R1"))
    P.append(Cond("R1 body", "R1", [(33.0, py["SD"], 6.5), (39.0, py["SD"], 6.5)], BODY_R, "body", step="r12", comp="R1"))
    P.append(Cond("R1 lead b", "GND", [(39.0, py["SD"], 6.5), (40.0, py["SD"], 6.5), (40.0, py["GND"], 6.1), (px, py["GND"], 5.1)], LEAD_R, "lead", step="r12", comp="R1"))
    # R2 (GAIN to GND, the 15 dB setting) dropped 2026-10-14: GAIN floats at 9 dB.
    P.append(Cond("R2 lead b", "GND", [(39.0, py["GAIN"], 6.7), (40.8, py["GAIN"], 6.7), (40.8, py["GND"], 6.5), (40.0, py["GND"], 6.1)], LEAD_R, "lead", step="r12", comp="R2"))
    # R3 10 k pull-up: from the BCLK rod in the channel, up, body back along the channel at 7.5 mm, down with the mic VDD tap onto the 3V3 rail
    P.append(Cond("R3 lead a", "GPIO2", [(25.5, ay["GPIO2"], 5.0), (25.5, ay["GPIO2"], 11.0), (25.5, 17.8, 11.0)], LEAD_R, "lead", step="r34", comp="R3"))
    P.append(Cond("R3 body", "R3", [(25.5, 17.8, 11.0), (25.5, 22.8, 11.0)], BODY_R, "body", step="r34", comp="R3"))
    P.append(Cond("R3 lead b", "3V3", [(25.5, 22.8, 11.0), (25.5, 23.5, 11.0), (24.6, 23.5, 11.0), (24.6, 23.5, 9.0)], LEAD_R, "lead", step="r34", comp="R3"))
    # R4 (mic SD pull-down) dropped 2026-10-14: the firmware enables GPIO4's internal pull-down.
    P.append(Cond("R4 lead b", "GND", [(29.0, 26.0, 11.0), (29.0, mL["GND"], 6.9)], LEAD_R, "lead", step="r34", comp="R4"))
    # 100 nF: leads on the VIN and GND stubs, body lying flat on the amp board pointing into it
    P.append(Cond("100n lead +", "5V", [(px, py["VIN"], 4.7), (32.0, py["VIN"], 4.9)], LEAD_R, "lead", step="caps", comp="C2"))
    P.append(Cond("100n lead -", "GND", [(px, py["GND"], 4.7), (32.0, py["GND"], 4.9)], LEAD_R, "lead", step="caps", comp="C2"))
    P.append(Cond("100n body", "C2", [(32.0, 5.85, 4.9), (35.2, 5.85, 4.9)], 0.8, "body", step="caps", comp="C2"))
    # 220 uF: lying in the right strip, leads along the floor (sleeved) to the 5 V net and the GND rod
    P.append(Cond("220u lead +", "5V", [(52.4, 3.0, 0.5), (px, 3.0, 0.5), (px, 3.0, 4.7), (px, py["VIN"], 4.7)], LEAD_R, "lead",
                  sleeve=[(0, 0.0, 0.97)], step="caps", comp="C1"))
    P.append(Cond("220u lead -", "GND", [(54.9, 2.0, 0.5), (29.0, 2.0, 0.5), (29.0, py["GND"], 0.5), (29.0, py["GND"], 5.0)], LEAD_R, "lead",
                  sleeve=[(0, 0.0, 1.0), (1, 0.0, 1.0)], step="caps", comp="C1"))
    P.append(Cond("220u body", "C1", [(53.65, 3.0, 3.15), (53.65, 15.0, 3.15)], 3.15, "body", step="caps", comp="C1"))
    return P


# ---------------------------------------------------------------- boxes (mechanical)
BOXES = {
    "A1 board": A1, "USB socket": USB, "A1 chip": A1_CHIP, "A1 antenna": A1_ANT, "A1 button L": A1_BTN_L, "A1 button R": A1_BTN_R,
    "amp board": AMP, "amp chip": AMP_CHIP, "terminal block": AMP_BLOCK,
    "mic board": MIC, "speaker": SPK, "screen PCB": SCREEN, "screen parts": SCREEN_PARTS, "button": BTN,
}
BOX_NET = {"USB socket": "GND"}   # the only conductive box


def seg_box_dist(p, q, b):
    """Distance from segment pq to an axis-aligned box (0 if it enters)."""
    best = 1e9
    n = 24
    for i in range(n + 1):
        t = i / n
        pt = [p[k] + (q[k] - p[k]) * t for k in range(3)]
        dx = max(b["x0"] - pt[0], 0, pt[0] - b["x1"])
        dy = max(b["y0"] - pt[1], 0, pt[1] - b["y1"])
        dz = max(b["z0"] - pt[2], 0, pt[2] - b["z1"])
        best = min(best, math.sqrt(dx * dx + dy * dy + dz * dz))
    return best


def is_sleeved(c, i, t):
    return any(si == i and t0 - 1e-6 <= t <= t1 + 1e-6 for si, t0, t1 in c.sleeve)


def check(conds, boxes=BOXES):
    """Return a list of (gap, a, b, flag) for every pair on different nets closer than GOOD_GAP."""
    out = []
    for i in range(len(conds)):
        for j in range(i + 1, len(conds)):
            a, b = conds[i], conds[j]
            if a.net == b.net or (a.comp and a.comp == b.comp):
                continue
            if a.kind == "body" or b.kind == "body":
                # insulated bodies: only flag actual overlap
                limit = 0.0
            else:
                limit = GOOD_GAP
            best = (1e9, None, None)
            for si, (p1, q1) in enumerate(a.segs()):
                for sj, (p2, q2) in enumerate(b.segs()):
                    d = seg_seg_dist(p1, q1, p2, q2) - a.r - b.r
                    if d < best[0]:
                        best = (d, si, sj)
            gap, si, sj = best
            where = tuple(round((a.pts[si][k] + a.pts[si + 1][k]) / 2, 1) for k in range(3)) if si is not None else None
            if gap < limit - 1e-9 or (limit == 0.0 and gap < -1e-6):
                sleeved = bool(a.sleeve) or bool(b.sleeve)
                flag = "FAIL" if gap < MIN_GAP and not sleeved else ("sleeve" if gap < MIN_GAP else "tight")
                if limit == 0.0:
                    flag = "OVERLAP"
                out.append((round(gap, 2), a.name, b.name, flag, where))
    # conductors vs mechanical boxes
    for c in conds:
        if c.kind in ("stub",):
            continue
        for bname, b in boxes.items():
            bnet = BOX_NET.get(bname)
            # a rod may rest on a board it belongs to; skip rods ending inside the box's footprint top (joints at stubs)
            for p, q in c.segs():
                d = seg_box_dist(p, q, b) - c.r
                if d < 0.9 and not (seg_box_dist(c.pts[0], c.pts[0], b) < 1.5 and dist(p, c.pts[0]) < 1.6) \
                        and not (seg_box_dist(c.pts[-1], c.pts[-1], b) < 1.5 and dist(q, c.pts[-1]) < 1.6):
                    if bname == "USB socket" and c.net == "GND":
                        continue
                    out.append((round(d, 2), c.name, bname, "BOX" if d < 0.25 else "near-box", None))
    out.sort()
    return out


def all_conductors():
    return stubs() + rods() + small_parts()


if __name__ == "__main__":
    conds = all_conductors()
    rep = check(conds)
    seen = set()
    for gap, a, b, flag, where in rep:
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        if flag in ("FAIL", "OVERLAP", "BOX"):
            print(f"{flag:8} {gap:6.2f}  {a}  ×  {b}  near {where}")
    print("---- tight/sleeved (< 1.5 mm) ----")
    for gap, a, b, flag, where in rep:
        if flag in ("tight", "sleeve"):
            print(f"{flag:8} {gap:6.2f}  {a}  ×  {b}  near {where}")
    print("---- rod lengths ----")
    for c in rods():
        print(f"{c.name:18} {c.length():6.1f} mm")
