"""Builds edu/pages/whole-build-one-frame.html: harness + PowerBoost + cell + switch in one frame,
drawn storey by storey from the same model, with the complete connection list."""
from __future__ import annotations

import pathlib
import re

import harness_model as M
import harness_draw as D
from harness_page import a, L
from power_page import L as _  # registers the power links

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "whole-build-one-frame.html"
HARNESS = "https://claude.ai/artifact/FAsL4WPArRK6QW7yEg2Nix"

# ---------------------------------------------------------------- the new frame and the lower storeys (mm)
IN_X, IN_Y, IN_Z = 65.0, 39.0, 35.0           # inside; outside 68 × 42 × 38
HARNESS_X0 = 0.0                              # the harness keeps its own coordinates, left-aligned
SHELF = dict(x0=0.5, x1=64.5, y0=0.5, y1=38.5, z0=-0.3, z1=0.0)                 # card shelf the harness stands on
PB = dict(x0=20.0, x1=65.0, y0=8.0, y1=31.0, z0=-10.5, z1=-0.5)                 # PowerBoost 45 × 23 × 10, USB port at the right wall
PB_PINS = (22.0, 19.5)                                                            # its pin header end, left end of the board
CELL = dict(x0=1.5, x1=63.5, y0=2.5, y1=36.5, z0=-16.5, z1=-11.5)                # 1200 mAh, 62 × 34 × 5, in a cradle
SWITCH = dict(x0=5.0, x1=13.5, y0=0.5, y1=4.0, z0=-5.0, z1=-1.0)                 # slide switch at the front edge of the shelf
HOLE_5V = (21.5, 3.0)        # the two wires come up through the shelf here, beside A1's front-right corner
HOLE_GND = (22.6, 7.1)       # beside A1's GND stub


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


S = 10.0
OX, OY = 50.0, 40.0


def tx(x):
    return OX + x * S


def ty(y):
    return OY + (IN_Y - y) * S


def T(x, y, s, cls="s", anchor="start"):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{D.esc(s)}</text>'


def R(b, cls, rx=3):
    return f'<rect x="{tx(b["x0"]):.1f}" y="{ty(b["y1"]):.1f}" width="{(b["x1"]-b["x0"])*S:.1f}" height="{(b["y1"]-b["y0"])*S:.1f}" rx="{rx}" class="{cls}"/>'


def frame():
    return (f'<rect x="{tx(0):.1f}" y="{ty(IN_Y):.1f}" width="{IN_X*S:.1f}" height="{IN_Y*S:.1f}" class="frame"/>'
            + "".join(f'<circle cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="{0.8*S:.1f}" class="post"/>' for x in (0.8, IN_X - 0.8) for y in (0.8, IN_Y - 0.8)))


def wire(pts, color, w=3.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{tx(x):.1f},{ty(y):.1f}" for x, y in pts)
    return f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{d}/>'


def hole(x, y, lab):
    return f'<circle cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="7" class="hole"/>' + T(tx(x) + 10, ty(y) + 4, lab, "s b")


def svg(body, h, label):
    return f'<svg viewBox="0 0 760 {h}" role="img" aria-label="{D.esc(label)}">{body}</svg>'


H_TOP = int(OY + IN_Y * S + 44)


def fig_storey1():
    o = [frame(), R(CELL, "cap", 6)]
    o.append(T(tx(32.5), ty(19.5) + 4, "1200 mAh cell, 62 × 34 × 5, in a cardstock cradle", "s b", "middle"))
    o.append(T(tx(32.5), ty(16.5) + 4, "its JST lead runs up to the PowerBoost's JST socket above", "s muted", "middle"))
    o.append(wire([(60, 36.5), (60, 38), (24, 38), (24, 31)], "var(--w-red)", 3, "6 3"))
    o.append(T(tx(42), ty(34.5), "cell lead (red + black in one JST); dashed = goes up a storey", "s muted", "middle"))
    o.append(T(OX, 22, "Storey 1, the bottom: the cell only", "t b"))
    o.append(T(tx(0), ty(0) + 18, "front of the device at the bottom · inside 65 × 39 · 10 px = 1 mm", "s muted"))
    return svg("".join(o), H_TOP, "Storey 1")


def fig_storey2():
    o = [frame(), R(SHELF, "card", 3)]
    o.append(R(PB, "acc-fill", 5))
    o.append(T(tx(42.5), ty(21) + 4, "PowerBoost 1000C, 45 × 23 × 10, lying flat", "s b", "middle"))
    o.append(T(tx(42.5), ty(18) + 4, "USB port at the right wall opening", "s muted", "middle"))
    # port
    o.append(f'<rect x="{tx(63.5):.1f}" y="{ty(22):.1f}" width="{2.5*S:.1f}" height="{5*S:.1f}" class="box"/>')
    o.append(T(tx(64.7), ty(26.5), "USB", "pin", "middle"))
    # pins at the left end
    for i, (name, net) in enumerate((("5V", "var(--w-red)"), ("GND", "var(--w-black)"), ("EN", "var(--w-purple)"), ("LBO", "var(--w-teal)"), ("BAT", "var(--w-orange)"))):
        y = 28.5 - i * 2.54
        o.append(f'<circle cx="{tx(PB_PINS[0]):.1f}" cy="{ty(y):.1f}" r="3.2" class="stubp"/>')
        o.append(T(tx(PB_PINS[0]) + 7, ty(y) + 3.5, name, "pin"))
    o.append(T(tx(PB_PINS[0]) - 4, ty(31.5), "pins (positions per the silkscreen)", "pin", "start"))
    # JST socket
    o.append(f'<rect x="{tx(20.5):.1f}" y="{ty(12.5):.1f}" width="{4*S:.1f}" height="{3*S:.1f}" class="box"/>')
    o.append(T(tx(22.5), ty(9.5) - 2, "JST ← cell", "pin", "middle"))
    # switch at the front
    o.append(R(SWITCH, "box", 2))
    o.append(T(tx(9.25), ty(5.2) - 2, "slide switch, lever through the front opening", "s b", "middle"))
    # wires
    o.append(wire([(PB_PINS[0], 28.5), (17, 28.5), (17, 6), (HOLE_5V[0], HOLE_5V[1])], "var(--w-red)", 4))
    o.append(wire([(PB_PINS[0], 25.96), (18.5, 25.96), (18.5, 7.1), (HOLE_GND[0], HOLE_GND[1])], "var(--w-black)", 4))
    o.append(wire([(PB_PINS[0], 23.42), (15, 23.42), (15, 10), (9, 10), (9, 4)], "var(--w-purple)", 3))
    o.append(wire([(PB_PINS[0], 25.96), (12, 25.96), (12, 11), (11.5, 11), (11.5, 4)], "var(--w-black)", 2.5, "4 3"))
    o.append(wire([(PB_PINS[0], 20.88), (14, 20.88), (14, 14), (23.5, 14)], "var(--w-teal)", 2.5, "4 3"))
    o.append(hole(HOLE_5V[0], HOLE_5V[1], "hole: 5 V up to A1's 5V stub"))
    o.append(hole(HOLE_GND[0], HOLE_GND[1], "hole: GND up to A1's GND stub"))
    o.append(f'<circle cx="{tx(23.5):.1f}" cy="{ty(14):.1f}" r="7" class="hole"/>' + T(tx(23.5) + 10, ty(14) + 4, "hole: LBO up to A1 GPIO6 (optional)", "s b"))
    o.append(T(tx(0.5), ty(35.5), "26 AWG for 5 V and GND, 30 AWG for EN and LBO; all insulated, so they may touch anything", "s muted"))
    o.append(T(OX, 22, "Storey 2: the card shelf, the PowerBoost, the switch, and the wires that go up", "t b"))
    o.append(T(tx(0), ty(0) + 18, "front of the device at the bottom · the harness stands on this shelf", "s muted"))
    return svg("".join(o), H_TOP, "Storey 2")


def fig_storey3():
    # the harness map in the new frame: reuse the draw module with its own origin, then overlay the two wire ends
    body = D.map_figure(title="Storey 3: the harness, every rod as on the harness page, plus two wire ends")
    body = body.replace(f'<rect x="{D.tx(0):.1f}" y="{D.ty(M.INSIDE_Y):.1f}" width="{M.INSIDE_X*D.S:.1f}" height="{M.INSIDE_Y*D.S:.1f}" class="frame"/>',
                        f'<rect x="{D.tx(0):.1f}" y="{D.ty(M.INSIDE_Y):.1f}" width="{IN_X*D.S:.1f}" height="{IN_Y*D.S:.1f}" class="frame"/>')
    extra = (f'<circle cx="{D.tx(HOLE_5V[0]):.1f}" cy="{D.ty(HOLE_5V[1]):.1f}" r="7" class="hole"/>'
             f'<line x1="{D.tx(HOLE_5V[0]):.1f}" y1="{D.ty(HOLE_5V[1]):.1f}" x2="{D.tx(20.8):.1f}" y2="{D.ty(4.6):.1f}" stroke="var(--w-red)" stroke-width="4" stroke-linecap="round"/>'
             f'<circle cx="{D.tx(HOLE_GND[0]):.1f}" cy="{D.ty(HOLE_GND[1]):.1f}" r="7" class="hole"/>'
             f'<line x1="{D.tx(HOLE_GND[0]):.1f}" y1="{D.ty(HOLE_GND[1]):.1f}" x2="{D.tx(20.8):.1f}" y2="{D.ty(7.1):.1f}" stroke="var(--w-black)" stroke-width="4" stroke-linecap="round"/>'
             + T(D.tx(1.5), D.ty(33.5), "dotted rings at the front = holes in the shelf:", "s b")
             + T(D.tx(1.5), D.ty(32.0), "red wire up to A1's 5V stub (the 5 V rod's joint),", "s b")
             + T(D.tx(1.5), D.ty(30.5), "black wire up to A1's GND stub (the star point)", "s b")
             + T(D.tx(58), D.ty(20), "8 mm spare", "s muted", "middle") + T(D.tx(58), D.ty(18.5), "at the right", "s muted", "middle"))
    body = body.replace("</svg>", extra + "</svg>")
    return body.replace(f'viewBox="0 0 760 {int(D.OY + M.INSIDE_Y * D.S + 40)}"', f'viewBox="0 0 760 {int(D.OY + M.INSIDE_Y * D.S + 40)}"')


def fig_front():
    w, h = 760, 420
    sx = (w - 150) / IN_X; sz = 8.5
    X = lambda x: 40 + x * sx
    Z = lambda z: 330 - (z + 17.5) * sz
    o = [T(30, 24, "Front view: the three storeys and the wires that climb between them", "t b")]
    o.append(f'<rect x="{X(-1.5):.1f}" y="{Z(IN_Z - 17.5):.1f}" width="{(IN_X + 3) * sx:.1f}" height="{IN_Z * sz:.1f}" class="frame" rx="3"/>')
    def st(b, cls, lab):
        return (f'<rect x="{X(b["x0"]):.1f}" y="{Z(b["z1"]):.1f}" width="{(b["x1"] - b["x0"]) * sx:.1f}" height="{(b["z1"] - b["z0"]) * sz:.1f}" class="{cls}" rx="2"/>'
                + T(X((b["x0"] + b["x1"]) / 2) - (0 if "cell" not in lab else 120), Z((b["z0"] + b["z1"]) / 2) + 4, lab, "s b", "middle"))
    o.append(st(CELL, "cap", "cell, 5 mm, in its cradle"))
    o.append(st(PB, "acc-fill", "PowerBoost, 10 mm, on the shelf"))
    o.append(st(SWITCH, "box", "switch"))
    o.append(f'<rect x="{X(SHELF["x0"]):.1f}" y="{Z(0):.1f}" width="{(SHELF["x1"] - SHELF["x0"]) * sx:.1f}" height="{0.3 * sz + 2:.1f}" class="card"/>')
    o.append(T(X(IN_X) + 8, Z(0) + 4, "card shelf", "s muted"))
    for name, b, cls in (("A1", M.A1, "pcb"), ("amp", M.AMP, "pcb"), ("mic", M.MIC, "pcb"), ("speaker", M.SPK, "spk"), ("220 µF", M.CAP220, "cap")):
        o.append(f'<rect x="{X(b["x0"]):.1f}" y="{Z(b["z1"]):.1f}" width="{(b["x1"] - b["x0"]) * sx:.1f}" height="{(b["z1"] - b["z0"]) * sz:.1f}" class="{cls}" rx="1.5"/>')
        o.append(T(X((b["x0"] + b["x1"]) / 2), Z(b["z1"]) - 3, name, "s muted", "middle"))
    b = M.SCREEN
    o.append(f'<rect x="{X(b["x0"]):.1f}" y="{Z(15.5):.1f}" width="{(b["x1"] - b["x0"]) * sx:.1f}" height="{3 * sz:.1f}" class="screen-side" rx="1.5"/>')
    o.append(T(X((b["x0"] + b["x1"]) / 2), Z(15.5) - 3, "screen on its rods", "s muted", "middle"))
    for c in M.rods():
        pts = " ".join(f"{X(p[0]):.1f},{Z(p[2]):.1f}" for p in c.pts)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{D.NET_COLOR.get(c.net, "var(--brass)")}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>')
    # climbing wires
    o.append(f'<polyline points="{X(22):.1f},{Z(-5.5):.1f} {X(21.5):.1f},{Z(-5.5):.1f} {X(21.5):.1f},{Z(3.0):.1f} {X(20.8):.1f},{Z(3.0):.1f}" fill="none" stroke="var(--w-red)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<polyline points="{X(22):.1f},{Z(-6.5):.1f} {X(27):.1f},{Z(-6.5):.1f} {X(27):.1f},{Z(0.5):.1f}" fill="none" stroke="var(--w-black)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<polyline points="{X(60):.1f},{Z(-11.5):.1f} {X(60):.1f},{Z(-10):.1f} {X(24):.1f},{Z(-10):.1f}" fill="none" stroke="var(--w-orange)" stroke-width="3" stroke-dasharray="5 3" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(T(X(IN_X) + 8, Z(-2.5) + 4, "5 V and GND wires", "s b"))
    o.append(T(X(IN_X) + 8, Z(-4.0) + 4, "climb through the shelf", "s b"))
    o.append(T(X(50), Z(-12.6), "cell lead to the JST", "s"))
    o.append(f'<rect x="{X(63.5):.1f}" y="{Z(-3):.1f}" width="{1.5 * sx:.1f}" height="{5 * sz:.1f}" class="box"/>')
    o.append(T(X(IN_X) + 8, Z(-7.5) + 4, "USB charge port", "s muted"))
    for z, lab in ((0, "harness plane, 0"), (-11.0, "shelf under the PowerBoost"), (IN_Z - 17.5, f"top loop, 35 up")):
        o.append(f'<line x1="{X(-1.5)-6:.1f}" y1="{Z(z):.1f}" x2="{X(IN_X)+6:.1f}" y2="{Z(z):.1f}" class="grid dashed"/>')
    o.append(T(X(0), 400, "inside 65 × 39 × 35 · outside 68 × 42 × 38 · Kapton on every tube · the cell touches only its cradle and its own plug", "s warn-ink"))
    return svg("".join(o), h, "Front view of the whole build")


def main():
    rods = {c.name: c for c in M.rods()}
    H = ['<title>Whole Build One Frame</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style(),
         '<style>figure svg .acc-fill { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.4; } figure svg .warn-fill { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1.2; }'
         ' figure svg .hole { fill: var(--surface); stroke: var(--pass); stroke-width: 2.2; stroke-dasharray: 3 2; } figure svg .card { fill: var(--surface); stroke: var(--muted); stroke-width: 1.2; }'
         ' figure svg .cap { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.2; } figure svg .spk { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1.2; }</style>',
         '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · final build · everything in one frame</div>',
         '<h1>The whole build in one frame</h1>',
         f'<p class="lede">Harness, PowerBoost, cell and switch, all inside one 68 × 42 × 38 frame, drawn storey by storey from the same model. Every rod of the harness is here unchanged (its own page has the per-rod drawings and cut lengths); this page adds the five connections that make it a battery device and shows where each thing physically sits.</p>']

    H.append('<h2>The frame and its three storeys</h2>')
    H.append(f'<figure><div class="scroll">{fig_front()}</div><figcaption><strong>From the bottom up:</strong> the cell in a cardstock cradle (6 mm), a card shelf carrying the PowerBoost flat with its USB port at the right opening (11 mm), and the harness standing on that shelf (16 mm), the screen floating on its rods. Two wires climb through holes in the shelf to A1\'s 5V and GND stubs. Total 33 of the 35 mm inside.</figcaption></figure>')

    H.append('<h2>Storey 1: the cell</h2>')
    H.append(f'<figure><div class="scroll">{fig_storey1()}</div><figcaption><strong>Nothing touches the cell but its cradle.</strong> 62 × 34 mm of cardstock box, 1 mm of margin, the pouch flat, its own JST lead led up to the PowerBoost. No solder, no brass, no iron near it; it goes in last and comes out first.</figcaption></figure>')

    H.append('<h2>Storey 2: the shelf, the PowerBoost, the switch</h2>')
    H.append(f'<figure><div class="scroll">{fig_storey2()}</div><figcaption><strong>Five wires leave the PowerBoost.</strong> 5 V (red) and GND (black) climb through two holes in the shelf to the harness; EN (purple) goes to the slide switch, whose other side returns to PowerBoost GND; LBO (teal, optional) climbs to A1\'s GPIO6. The cell\'s JST plugs into the socket at the board\'s left end. Being insulated wire, these may cross and touch anything.</figcaption></figure>')

    H.append('<h2>Storey 3: the harness, with its two new joints</h2>')
    H.append(f'<figure><div class="scroll">{fig_storey3()}</div><figcaption><strong>Every rod exactly as on the harness page</strong>, left-aligned in the wider frame with 8 mm spare on the right. The red wire from below ends on A1\'s 5V stub (the same stub the 5 V rod starts from); the black wire ends on the GND rail\'s front end. A1\'s USB socket gets a square of Kapton: it is no longer a power input.</figcaption></figure>')

    # ------------------------------------------------------------ complete list
    H.append('<h2>Every connection in the device</h2>')
    H.append('<h3>Power and battery (new)</h3>')
    H.append('<div class="scrollx"><table class="t"><tr><th>#</th><th>From</th><th>To</th><th>With</th><th>Note</th></tr>'
             f'<tr><td class="n">P1</td><td>PowerBoost <code>5V</code></td><td>A1 5V stub (through the shelf hole at x = 21.5, y = 3)</td><td>26 AWG red, ≈ 60 mm, {a("wire26", "TUOFENG")}</td><td>joins the 5 V rod\'s joint; the 220 µF stays where it is</td></tr>'
             '<tr><td class="n">P2</td><td>PowerBoost <code>GND</code></td><td>A1\'s GND stub (hole at x = 22.6, y = 7.1)</td><td>26 AWG black, ≈ 55 mm</td><td>the star point; the rail stays a dead end</td></tr>'
             f'<tr><td class="n">P3</td><td>PowerBoost <code>EN</code></td><td>{a("switch", "slide switch")}, one side</td><td>30 AWG, ≈ 40 mm</td><td>the other side of the switch to PowerBoost <code>GND</code> (P4). Closed = EN grounded = off</td></tr>'
             '<tr><td class="n">P4</td><td>switch, other side</td><td>PowerBoost <code>GND</code></td><td>30 AWG, ≈ 40 mm</td><td></td></tr>'
             f'<tr><td class="n">P5</td><td>{a("cell1200", "1200 mAh cell")} JST</td><td>PowerBoost JST socket</td><td>the cell\'s own lead</td><td>check + and − against the board\'s silkscreen before the first plug-in</td></tr>'
             '<tr><td class="n">P6</td><td>PowerBoost <code>LBO</code></td><td>A1 GPIO6</td><td>30 AWG, optional</td><td>low-battery flag for a later firmware face</td></tr>'
             '<tr><td class="n">—</td><td>A1 USB-C</td><td>nothing</td><td>Kapton over it</td><td>flashing only, switch off first</td></tr>'
             '</table></div>')
    H.append('<h3>The harness (unchanged)</h3>')
    rows = [
        ("5V", "amp VIN", "5 V rod"), ("GND", "amp GND, and the GND rail", "GND rod + GND drop pin"), ("3V3", "3V3 rail", "3V3 tap"),
        ("GPIO4", "mic SD", "mic SD rod"), ("GPIO3", "amp DIN", "DIN rod"), ("GPIO2", "amp BCLK, then mic SCK", "BCLK rod"),
        ("GPIO1", "amp LRC, then mic WS", "WS rod"), ("GPIO5", "amp SD", "amp SD rod"), ("GPIO10", "button", "button rod"),
        ("GPIO20", "screen SCL", "SCL rod"), ("GPIO21", "screen SDA", "SDA rod"),
    ]
    H.append('<div class="scrollx"><table class="t"><tr><th>A1 pin</th><th>Goes to</th><th>By</th><th>Length</th></tr>')
    for pin, to, by in rows:
        names = [n.strip() for n in by.split("+")]
        Lmm = sum(rods[n].length() for n in names)
        H.append(f'<tr><td class="n">{pin}</td><td>{to}</td><td>{by}</td><td class="n">{Lmm:.0f} mm</td></tr>')
    H.append('</table></div>')
    H.append('<div class="scrollx"><table class="t"><tr><th>Tap or part</th><th>Between</th></tr>'
             '<tr><td>screen GND tap · screen VCC tap</td><td>screen GND → GND rail front · screen VCC → 3V3 rail front</td></tr>'
             '<tr><td>mic GND tap · mic VDD tap · L/R link</td><td>mic GND → GND rail back · mic VDD → 3V3 rail back · mic L/R → mic GND</td></tr>'
             '<tr><td>button GND rod</td><td>button right legs → A1 GND stub</td></tr>'
             '<tr><td>R1 4.7 kΩ</td><td>amp SD → amp GND (GAIN left open, 9 dB)</td></tr>'
             '<tr><td>R3 10 kΩ</td><td>BCLK rod → 3V3 rail, until A1\'s own GPIO2 pull-up is confirmed (mic SD pull-down is in firmware)</td></tr>'
             '<tr><td>C1 220 µF · C2 100 nF</td><td>5 V net → GND rod · amp VIN → amp GND</td></tr>'
             '<tr><td>speaker</td><td>OUT+ / OUT− only, never GND or the frame</td></tr>'
             '</table></div>')

    H.append('<h2>Build order for the one-frame version</h2>')
    H.append('<ol><li>The harness, moves 1–11 of the harness page, on USB, on its jig card. Make it work first.</li>'
             '<li>The frame to the new size: two loops at 65 × 39 inside, four posts of 35. Kapton inside.</li>'
             '<li>The shelf: a 64 × 38 card with the two wire holes and the LBO hole punched where the storey-2 drawing shows; the switch glued at its front edge.</li>'
             '<li>PowerBoost on the shelf, USB port at the right wall; wires P1–P4 (and P6) soldered at the PowerBoost end first, led up through the holes.</li>'
             '<li>Harness off its jig and onto the shelf; P1 to A1\'s 5V stub, P2 to A1\'s GND stub. Kapton over A1\'s USB.</li>'
             '<li>Cradle and cell at the bottom, JST into the PowerBoost. Meter frame to everything: silent.</li>'
             '<li>Switch on: the same tests as move 11. Then charge it once and watch the LEDs.</li></ol>')

    H.append('<div class="evidence"><p><strong>Sources.</strong> The harness from <code>edu/pages/gen/harness_model.py</code>; PowerBoost 1000C dimensions, pins and functions from Adafruit\'s product page; cell size from <code>docs/INVENTORY.md</code>. The lower storeys are a layout proposal measured against those sizes, not a built thing; pin positions on the PowerBoost are drawn as a group and must be read off its silkscreen.</p></div>')
    H.append('</div>')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
