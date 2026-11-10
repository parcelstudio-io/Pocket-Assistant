"""Builds edu/pages/pip-schematic.html: the whole device as rails and lanes, no physical layout."""
from __future__ import annotations

import pathlib
import re

from harness_page import a, L
from power_page import L as _
L["wire30"] = ("https://www.amazon.com/dp/B073RDGTPB", "CBAZY 30 AWG wire")

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "pip-schematic.html"

C = {"5V": "var(--w-red)", "3V3": "var(--w-orange)", "GND": "var(--w-black)",
     "WS": "var(--w-yellow)", "BCLK": "var(--w-pink)", "DIN": "var(--w-blue)", "micSD": "var(--w-green)",
     "ampSD": "var(--w-olive)", "BTN": "var(--w-purple)", "SCL": "var(--w-teal)", "SDA": "var(--w-navy)", "LBO": "var(--muted)"}


class Router:
    """Draws orthogonal polylines and hops over every earlier segment of a different net it crosses."""
    R = 7

    def __init__(self):
        self.segs = []      # (x0, y0, x1, y1, net)

    def add_straight(self, x0, y0, x1, y1, net):
        self.segs.append((x0, y0, x1, y1, net))

    def wire(self, pts, color, net, w=3, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        path = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            horiz, vert = abs(y0 - y1) < 0.01, abs(x0 - x1) < 0.01
            hops = []
            if horiz:
                lo, hi = min(x0, x1), max(x0, x1)
                for (a0, b0, a1, b1, n) in self.segs:
                    if n == net or abs(a0 - a1) > 0.01:
                        continue              # only vertical segments of other nets
                    if lo + self.R < a0 < hi - self.R and min(b0, b1) + 0.5 < y0 < max(b0, b1) - 0.5:
                        hops.append(a0)
                sgn = 1 if x1 > x0 else -1
                for rx in sorted(set(hops), reverse=(sgn < 0)):
                    path += f" L{rx - self.R * sgn:.1f},{y0:.1f} A{self.R},{self.R} 0 0 {1 if sgn > 0 else 0} {rx + self.R * sgn:.1f},{y0:.1f}"
            elif vert:
                lo, hi = min(y0, y1), max(y0, y1)
                for (a0, b0, a1, b1, n) in self.segs:
                    if n == net or abs(b0 - b1) > 0.01:
                        continue              # only horizontal segments of other nets
                    if lo + self.R < b0 < hi - self.R and min(a0, a1) + 0.5 < x0 < max(a0, a1) - 0.5:
                        hops.append(b0)
                sgn = 1 if y1 > y0 else -1
                for ry in sorted(set(hops), reverse=(sgn < 0)):
                    path += f" L{x0:.1f},{ry - self.R * sgn:.1f} A{self.R},{self.R} 0 0 {0 if sgn > 0 else 1} {x0:.1f},{ry + self.R * sgn:.1f}"
            path += f" L{x1:.1f},{y1:.1f}"
            self.segs.append((x0, y0, x1, y1, net))
        return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{d}/>'



def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def L_(x1, y1, x2, y2, color, w=3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{d}/>'


def dot(x, y):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" class="dot"/>'


def ring(x, y):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="ring"/><circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="var(--figure-bg)"/>'


def schematic():
    W = 1240
    # rails (top) and lanes (bottom)
    RAIL = {"5V": 70, "3V3": 100, "GND": 130}
    LANES = [("WS", "GPIO1 · word select"), ("BCLK", "GPIO2 · bit clock"), ("DIN", "GPIO3 · sound out"), ("micSD", "GPIO4 · sound in"),
             ("ampSD", "GPIO5 · amp on/off"), ("BTN", "GPIO10 · button"), ("SCL", "GPIO20 · screen clock"), ("SDA", "GPIO21 · screen data"), ("LBO", "GPIO6 · low battery (optional)")]
    LY = {k: 470 + i * 30 for i, (k, _) in enumerate(LANES)}
    o = [T(20, 28, "Pip as rails and lanes: three rails on top, one lane per signal below, every part hangs between them. Not a layout.", "t b")]
    o.append(T(20, 46, "A dot is a joint. A ring is a tap where the line carries on. Lines that cross without a dot do not touch. Place the parts wherever you like; keep these connections.", "s muted"))
    X0, X1 = 40, W - 30
    for k, y in RAIL.items():
        o.append(L_(X0, y, X1, y, C[k], 6))
        o.append(T(X1 + 4, y + 4, {"5V": "5 V rail", "3V3": "3V3 rail", "GND": "GND rail"}[k], "s b", "start"))
    for k, lab in LANES:
        y = LY[k]
        o.append(L_(X0, y, X1, y, C[k], 2.5, "6 4" if k == "LBO" else None))
        o.append(T(X1 + 4, y + 4, lab, "s", "start"))

    # ---- parts: boxes with pins; each pin is (name, x) at the box's top edge (to rails) or bottom edge (to lanes)
    def part(x, w, name, sub, top, bottom, h=110, y=250):
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="part"/>', T(x + w / 2, y + 24, name, "t b", "middle")]
        if sub:
            out.append(T(x + w / 2, y + 40, sub, "s muted", "middle"))
        for i, (pin, rail) in enumerate(top):
            px = x + 18 + i * 24
            out.append(L_(px, y, px, RAIL[rail], C[rail], 3))
            out.append(dot(px, RAIL[rail]))
            out.append(T(px, y + 56, pin, "pin", "middle", 'transform="rotate(-90 %.1f %.1f)"' % (px, y + 56)))
        for i, (pin, lane, kind) in enumerate(bottom):
            px = x + 18 + i * 24
            out.append(L_(px, y + h, px, LY[lane], C[lane], 3))
            out.append(ring(px, LY[lane]) if kind == "tap" else dot(px, LY[lane]))
            out.append(T(px, y + h - 10, pin, "pin", "middle", 'transform="rotate(-90 %.1f %.1f)"' % (px, y + h - 10)))
        return "".join(out)

    # PowerBoost + cell + switch + charger
    o.append(part(50, 150, "PowerBoost", "charger + boost", [("5V out", "5V"), ("GND", "GND")], [("LBO", "LBO", "dot")]))
    o.append(f'<rect x="50" y="170" width="68" height="40" rx="6" class="cap"/>' + T(84, 186, "cell", "s b", "middle") + T(84, 200, "1200 mAh", "s muted", "middle"))
    o.append(L_(84, 210, 84, 250, "var(--w-orange)", 3) + T(92, 236, "BAT (JST)", "pin"))
    o.append(f'<rect x="132" y="170" width="68" height="40" rx="6" class="box"/>' + T(166, 186, "USB in", "s b", "middle") + T(166, 200, "charge port", "s muted", "middle"))
    o.append(L_(166, 210, 166, 250, "var(--w-red)", 3))
    o.append(f'<rect x="214" y="250" width="54" height="36" rx="6" class="box"/>' + T(241, 266, "switch", "s b", "middle") + T(241, 280, "EN", "pin", "middle"))
    o.append(L_(200, 290, 214, 290, C["BTN"], 2.5) + L_(268, 268, 290, 268, C["GND"], 2.5) + L_(290, 268, 290, 130, C["GND"], 2.5) + dot(290, 130))
    o.append(T(214, 310, "closed = off", "s muted"))

    # A1
    o.append(part(330, 260, "A1 · ESP32-C3", "its USB port stays unused", [("5V", "5V"), ("3V3", "3V3"), ("GND", "GND")],
                  [("GPIO1", "WS", "dot"), ("GPIO2", "BCLK", "dot"), ("GPIO3", "DIN", "dot"), ("GPIO4", "micSD", "dot"), ("GPIO5", "ampSD", "dot"), ("GPIO10", "BTN", "dot"), ("GPIO20", "SCL", "dot"), ("GPIO21", "SDA", "dot"), ("GPIO6", "LBO", "dot")]))
    o.append(T(460, 382, "3V3 is made by A1's regulator: A1 feeds the 3V3 rail", "s muted", "middle"))

    # amp
    o.append(part(640, 190, "Amp · MAX98357A", "", [("VIN", "5V"), ("GND", "GND")],
                  [("LRC", "WS", "tap"), ("BCLK", "BCLK", "tap"), ("DIN", "DIN", "dot"), ("SD", "ampSD", "dot")]))
    # GAIN, OUT±
    o.append(T(735, 346, "GAIN open (9 dB)", "s", "middle"))
    o.append(f'<rect x="770" y="170" width="70" height="40" rx="6" class="spk"/>' + T(805, 186, "speaker", "s b", "middle") + T(805, 200, "OUT+ / OUT−", "pin", "middle"))
    o.append(L_(790, 210, 790, 250, "var(--warn)", 3) + L_(820, 210, 820, 250, "var(--warn)", 3))
    o.append(T(805, 232, "never to GND or the frame", "s warn-ink", "middle"))

    # mic
    o.append(part(860, 150, "Mic · INMP441", "", [("VDD", "3V3"), ("GND", "GND"), ("L/R", "GND")],
                  [("WS", "WS", "dot"), ("SCK", "BCLK", "dot"), ("SD", "micSD", "dot")]))
    # screen
    o.append(part(1040, 120, "Screen", "", [("VCC", "3V3"), ("GND", "GND")], [("SCL", "SCL", "dot"), ("SDA", "SDA", "dot")]))
    # button
    o.append(f'<rect x="1040" y="170" width="120" height="40" rx="6" class="box"/>' + T(1100, 186, "button", "s b", "middle") + T(1100, 201, "GND · GPIO10", "pin", "middle"))
    o.append(L_(1060, 170, 1060, 130, C["GND"], 3) + dot(1060, 130))
    o.append(L_(1140, 210, 1140, LY["BTN"], C["BTN"], 2.5) + dot(1140, LY["BTN"]))

    # small parts between rails and lanes, drawn as labelled stubs
    def r(x, lane, rail, label):
        y0 = LY[lane]; y1 = RAIL[rail]
        return (L_(x, y0, x, y1, "var(--warn)", 2) + f'<rect x="{x-6}" y="{(y0+y1)/2-14}" width="12" height="28" rx="3" class="r"/>'
                + dot(x, y0) + dot(x, y1) + T(x, (y0 + y1) / 2 + 4, label, "s warn-ink", "middle", 'transform="rotate(-90 %.1f %.1f)"' % (x - 12, (y0 + y1) / 2 + 4)))
    o.append(r(606, "ampSD", "GND", "R1 4.7 kΩ"))
    o.append(r(626, "BCLK", "3V3", "R3 10 kΩ"))
    # capacitors
    o.append(L_(735, 70, 735, 130, "var(--accent)", 2) + f'<rect x="727" y="110" width="16" height="14" rx="2" class="cap"/>' + T(735, 152, "C1 220 µF + C2 100 nF, amp VIN to GND", "s acc-ink", "middle"))
    return f'<svg viewBox="0 0 {W + 170} 760" role="img" aria-label="Pip schematic as rails and lanes">{"".join(o)}</svg>'


def schematic_portrait():
    W, H = 760, 1240
    RX = {"5V": 60, "3V3": 90, "GND": 120}                       # rail columns, left
    LANES = [("WS", "WS · GPIO1"), ("BCLK", "BCLK · GPIO2"), ("DIN", "DIN · GPIO3"), ("micSD", "mic SD · GPIO4"),
             ("ampSD", "amp SD · GPIO5"), ("BTN", "button · GPIO10"), ("SCL", "SCL · GPIO20"), ("SDA", "SDA · GPIO21"), ("LBO", "LBO · GPIO6, optional")]
    LX = {k: 470 + i * 30 for i, (k, _) in enumerate(LANES)}     # lane columns, right
    Y0, Y1 = 150, H - 30
    o = [T(20, 26, "Pip as rails and lanes · rails on the left, one lane per signal on the right, parts stacked between", "t b")]
    o.append(T(20, 44, "A dot is a joint. A ring is a tap where the line carries on. A hop is a line passing over another without touching. Place the parts anywhere; keep the joints.", "s muted"))
    rt = Router()
    for k, x in RX.items():
        rt.add_straight(x, Y0, x, Y1, k)
    for k, _ in LANES:
        rt.add_straight(LX[k], Y0, LX[k], Y1, k)
    for k, x in RX.items():
        o.append(L_(x, Y0, x, Y1, C[k], 6))
        o.append(T(x, Y0 - 8, {"5V": "5 V", "3V3": "3V3", "GND": "GND"}[k], "s b", "middle"))
    for k, lab in LANES:
        x = LX[k]
        o.append(L_(x, Y0, x, Y1, C[k], 2.5, "6 4" if k == "LBO" else None))
        o.append(T(x + 4, Y0 - 10, lab, "s", "start", 'transform="rotate(-55 %.1f %.1f)"' % (x + 4, Y0 - 10)))
    PX0, PW = 165, 280           # part column

    def part(y, h, name, sub, left, right, shape="rect"):
        if shape == "circle":
            # the round mic board: pins in two columns inside the outline, the sound hole in the middle
            cx, cy, r = PX0 + PW / 2, y + h / 2, h / 2
            out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" class="part"/>', f'<circle cx="{cx}" cy="{cy}" r="5" class="hole"/>',
                   T(cx, cy - 40, name, "t b", "middle")]
            if sub:
                out.append(T(cx, cy + r + 16, sub, "s muted", "middle"))
            xl, xr, y0 = cx - 42, cx + 42, cy - 20
        else:
            out = [f'<rect x="{PX0}" y="{y}" width="{PW}" height="{h}" rx="8" class="part"/>', T(PX0 + PW / 2, y + 20, name, "t b", "middle")]
            if sub:
                out.append(T(PX0 + PW / 2, y + 36, sub, "s muted", "middle"))
            xl, xr, y0 = PX0, PX0 + PW, y + 50
        for i, (pin, rail) in enumerate(left):
            py = y0 + i * 20
            out.append(rt.wire([(xl, py), (RX[rail], py)], C[rail], rail, 3)); out.append(dot(RX[rail], py))
            if shape == "circle":
                out.append(dot(xl, py))
            out.append(T(xl + 6, py + 4, pin, "pin", "start"))
        for i, (pin, lane, kind) in enumerate(right):
            py = y0 + i * 20
            out.append(rt.wire([(xr, py), (LX[lane], py)], C[lane], lane, 3))
            out.append(ring(LX[lane], py) if kind == "tap" else dot(LX[lane], py))
            if shape == "circle":
                out.append(dot(xr, py))
            out.append(T(xr - 6, py + 4, pin, "pin", "end"))
        return "".join(out)

    y = 165
    o.append(part(y, 120, "PowerBoost 1000C", "charger + load sharing + 5 V boost", [("5V out", "5V"), ("GND", "GND")], [("LBO", "LBO", "dot")]))
    # cell, USB in, switch beside the PowerBoost inside its box
    o.append(f'<rect x="{PX0+20}" y="{y+78}" width="70" height="30" rx="5" class="cap"/>' + T(PX0 + 55, y + 97, "cell 1200 mAh", "pin", "middle"))
    o.append(f'<rect x="{PX0+105}" y="{y+78}" width="70" height="30" rx="5" class="box"/>' + T(PX0 + 140, y + 97, "USB charge in", "pin", "middle"))
    o.append(f'<rect x="{PX0+190}" y="{y+78}" width="70" height="30" rx="5" class="box"/>' + T(PX0 + 225, y + 97, "switch: EN–GND", "pin", "middle"))
    y += 140
    o.append(part(y, 230, "A1 · ESP32-C3 SuperMini", "its own USB port stays unused", [("5V in", "5V"), ("3V3 out", "3V3"), ("GND", "GND")],
                  [("GPIO1", "WS", "dot"), ("GPIO2", "BCLK", "dot"), ("GPIO3", "DIN", "dot"), ("GPIO4", "micSD", "dot"), ("GPIO5", "ampSD", "dot"), ("GPIO10", "BTN", "dot"), ("GPIO20", "SCL", "dot"), ("GPIO21", "SDA", "dot"), ("GPIO6", "LBO", "dot")]))
    o.append(T(PX0 + PW / 2, y + 222, "A1's regulator makes the 3V3 rail", "s muted", "middle"))
    y += 250
    o.append(part(y, 165, "Amp · MAX98357A", "", [("VIN", "5V"), ("GND", "GND")], [("LRC", "WS", "tap"), ("BCLK", "BCLK", "tap"), ("DIN", "DIN", "dot"), ("SD", "ampSD", "dot")]))
    o.append(T(PX0 + 12, y + 140, "GAIN left open (9 dB) · C1 220 µF + C2 100 nF across VIN/GND", "s", "start"))
    o.append(T(PX0 + 12, y + 155, "OUT+ / OUT− → speaker only, never GND or the frame", "s warn-ink", "start"))
    y += 185
    o.append(part(y, 140, "Mic · INMP441", "round board, hole in the middle", [("VDD", "3V3"), ("GND", "GND"), ("L/R", "GND")], [("WS", "WS", "dot"), ("SCK", "BCLK", "dot"), ("SD", "micSD", "dot")], shape="circle"))
    y += 170
    o.append(part(y, 100, "Screen · SSD1306", "", [("VCC", "3V3"), ("GND", "GND")], [("SCL", "SCL", "dot"), ("SDA", "SDA", "dot")]))
    y += 120
    o.append(part(y, 80, "Button", "", [("leg", "GND")], [("leg", "BTN", "dot")]))
    # resistors between lanes and rails, drawn as short bridges below the button
    yb = y + 80 + 90
    def rb(lane, rail, label, yy):
        x0, x1 = RX[rail], LX[lane]
        return (rt.wire([(x0, yy), (x1, yy)], "var(--warn)", lane + rail, 2) + f'<rect x="{(x0+x1)/2-14}" y="{yy-6}" width="28" height="12" rx="3" class="r"/>' + dot(x0, yy) + dot(x1, yy)
                + T((x0 + x1) / 2, yy - 10, label, "s warn-ink", "middle"))
    o.append(rb("ampSD", "GND", "R1 4.7 kΩ: amp SD lane to GND", yb - 60))
    o.append(rb("BCLK", "3V3", "R3 10 kΩ: BCLK lane to 3V3", yb - 30))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Pip schematic, portrait">{"".join(o)}</svg>'


def schematic_direct():
    """Pin to pin with the two rails drawn as the rods they are: parts placed as in the device."""
    W, H = 820, 900
    o = [T(20, 26, "Pin to pin, with the two rails: parts placed as in the device, every line one piece of rod or wire", "t b")]
    o.append(T(20, 44, "Rails are bare rods between A1 and the amp. A dot is a joint; a hop is a line passing over a rail without touching it.", "s muted"))
    def part(x, y, w, h, title, sub, pins, shape="rect"):
        if shape == "circle":
            # the round mic board, as it looks on the bench: two columns of three pins, the sound hole in the middle
            cx, cy, r = x + w / 2, y + h / 2, min(w, h) / 2
            out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" class="part"/>', f'<circle cx="{cx}" cy="{cy}" r="6" class="hole"/>',
                   T(cx, cy - 58, title, "t b", "middle")]
            if sub:
                out.append(T(cx, cy + r + 16, sub, "s muted", "middle"))
            xl, xr, y0 = cx - 55, cx + 55, cy - 26
        else:
            out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="part"/>', T(x + w / 2, y + 20, title, "t b", "middle")]
            if sub:
                out.append(T(x + w / 2, y + 36, sub, "s muted", "middle"))
            xl, xr, y0 = x, x + w, y + 54
        P = {}
        for name, side, k in pins:
            if side == "L":
                px, py = xl, y0 + k * 26; out.append(T(px + 6, py + 4, name, "pin", "start"))
            elif side == "R":
                px, py = xr, y0 + k * 26; out.append(T(px - 6, py + 4, name, "pin", "end"))
            elif side == "B":
                px, py = x + 24 + k * 26, y + h; out.append(T(px, py - 8, name, "pin", "middle", 'transform="rotate(-90 %.1f %.1f)"' % (px, py - 8)))
            else:
                px, py = x + 24 + k * 26, y; out.append(T(px, py - 10, name, "pin", "middle", 'transform="rotate(-90 %.1f %.1f)"' % (px, py - 10)))
            P[name] = (px, py); out.append(dot(px, py))
        return "".join(out), P
    RX3, RXG = 470, 500                    # the two rails, vertical
    RY0, RY1 = 92, 800
    s_pb, pb = part(20, 140, 150, 150, "PowerBoost", "+ cell, port, switch", [("5V out", "R", 0), ("GND", "R", 1), ("LBO", "R", 2), ("EN", "B", 0)])
    s_sw, sw = part(20, 350, 150, 80, "Switch", "", [("a", "T", 0), ("b", "T", 1)])
    s_a1, a1 = part(230, 120, 190, 330, "A1 · ESP32-C3", "left row · right row", [("GPIO5", "L", 0), ("GPIO10", "L", 1), ("GPIO20", "L", 2), ("GPIO21", "L", 3), ("GPIO6", "L", 4), ("5V", "R", 0), ("GND", "R", 1), ("3V3", "R", 2), ("GPIO4", "R", 3), ("GPIO3", "R", 4), ("GPIO2", "R", 5), ("GPIO1", "R", 6)])
    s_amp, amp = part(560, 120, 180, 260, "Amp", "C1, C2 at its own pins; GAIN open", [("VIN", "L", 0), ("GND", "L", 1), ("SD", "L", 2), ("DIN", "L", 3), ("BCLK", "L", 4), ("LRC", "L", 5), ("OUT+", "R", 0), ("OUT−", "R", 1)])
    s_mic, mic = part(560, 480, 180, 180, "Mic", "left column faces the rails", [("GND", "L", 0), ("VDD", "L", 1), ("SD", "L", 2), ("L/R", "R", 0), ("WS", "R", 1), ("SCK", "R", 2)], shape="circle")
    s_scr, scr = part(230, 560, 190, 130, "Screen", "stubs at its front edge", [("SDA", "T", 0), ("SCL", "T", 1), ("VCC", "T", 2), ("GND", "T", 3)])
    s_btn, btn = part(20, 560, 150, 100, "Button", "", [("leg a", "R", 0), ("leg b", "R", 1)])
    s_spk, spk = part(560, 730, 180, 80, "Speaker", "its own two leads", [("+", "L", 0), ("−", "L", 1)])
    # rails first (under everything)
    o.append(f'<line x1="{RX3}" y1="{RY0}" x2="{RX3}" y2="{RY1}" stroke="{C["3V3"]}" stroke-width="7" stroke-linecap="round"/>')
    o.append(f'<line x1="{RXG}" y1="{RY0}" x2="{RXG}" y2="{RY1}" stroke="{C["GND"]}" stroke-width="7" stroke-linecap="round"/>')
    o.append(T(RX3 - 11, 440, "3V3 rail", "s b", "middle", 'transform="rotate(-90 %.1f %.1f)"' % (RX3 - 11, 440)))
    o.append(T(RXG + 14, 440, "GND rail", "s b", "middle", 'transform="rotate(-90 %.1f %.1f)"' % (RXG + 14, 440)))
    for blk in (s_pb, s_sw, s_a1, s_amp, s_mic, s_scr, s_btn, s_spk):
        o.append(blk)
    rt = Router()
    rt.add_straight(RX3, RY0, RX3, RY1, "3V3"); rt.add_straight(RXG, RY0, RXG, RY1, "GND")
    def wire(pts, color, w=3, dash=None, net=None):
        return rt.wire(pts, color, net or color, w, dash)
    # 5 V: PowerBoost -> A1 5V (wire), A1 5V -> amp VIN (the 5 V rod, crossing both rails)
    o.append(wire([pb["5V out"], (200, pb["5V out"][1]), (200, 72), (432, 72), (432, a1["5V"][1]), a1["5V"]], C["5V"], 4, net="5V"))
    o.append(wire([a1["5V"], amp["VIN"]], C["5V"], 4, net="5V"))
    o.append(T(490, a1["5V"][1] - 9, "5 V rod", "pin", "middle"))
    o.append(T(300, 66, "PowerBoost 5 V wire → A1's 5V stub", "pin", "middle"))
    # GND: PowerBoost -> GND rail (wire); A1 GND -> amp GND (GND rod) with the drop pin at the rail
    o.append(wire([pb["GND"], (210, pb["GND"][1]), (210, 104), (440, 104), (440, a1["GND"][1]), a1["GND"]], C["GND"], 4, net="GND"))
    o.append(T(325, 116, "PowerBoost GND wire → A1's GND stub (the star point)", "pin", "middle"))
    o.append(wire([a1["GND"], amp["GND"]], C["GND"], 4, net="GNDrod"))
    gy = a1["GND"][1]
    o.append(f'<line x1="{RXG + 16}" y1="{gy}" x2="{RXG}" y2="{gy + 22}" stroke="{C["GND"]}" stroke-width="4" stroke-linecap="round"/>')
    o.append(dot(RXG + 16, gy)); o.append(dot(RXG, gy + 22)); rt.add_straight(RXG + 16, gy, RXG, gy + 22, "GND")
    o.append(T(RXG + 6, gy + 40, "drop pin", "pin")); o.append(T(RXG + 6, gy + 52, "to rail", "pin"))
    # 3V3 tap
    o.append(wire([a1["3V3"], (RX3, a1["3V3"][1])], C["3V3"], 4, net="3V3")); o.append(dot(RX3, a1["3V3"][1]))
    # mic taps to the rails' lower part
    o.append(wire([mic["GND"], (RXG, mic["GND"][1])], C["GND"], 3, net="GND")); o.append(dot(RXG, mic["GND"][1]))
    o.append(wire([mic["VDD"], (RX3, mic["VDD"][1])], C["3V3"], 3, net="3V3")); o.append(dot(RX3, mic["VDD"][1]))
    o.append(wire([mic["L/R"], (755, mic["L/R"][1]), (755, 475), (548, 475), (548, mic["GND"][1]), mic["GND"]], C["GND"], 2.5, net="GND"))
    # screen taps to the rails' upper part (front ends)
    o.append(wire([scr["GND"], (scr["GND"][0], 525), (RXG, 525)], C["GND"], 3, net="GND")); o.append(dot(RXG, 525))
    o.append(wire([scr["VCC"], (scr["VCC"][0], 535), (RX3, 535)], C["3V3"], 3, net="3V3")); o.append(dot(RX3, 535))
    # button
    o.append(wire([btn["leg a"], (200, btn["leg a"][1]), (200, a1["GPIO10"][1]), a1["GPIO10"]], C["BTN"], 3, net="BTN"))
    o.append(wire([btn["leg b"], (190, btn["leg b"][1]), (190, 710), (RXG, 710)], C["GND"], 3, net="GND")); o.append(dot(RXG, 710))
    # signals: straight rods across the rails to the amp; clocks continue to the mic
    # DIN: its own jog. BCLK and WS: one vertical each, from the amp's pin down past A1's joint and on to the mic
    o.append(wire([a1["GPIO3"], (530, a1["GPIO3"][1]), (530, amp["DIN"][1]), amp["DIN"]], C["DIN"], 3, net="DIN"))
    o.append(wire([amp["BCLK"], (540, amp["BCLK"][1]), (540, 404), (745, 404), (745, mic["SCK"][1]), mic["SCK"]], C["BCLK"], 3, net="BCLK"))
    o.append(wire([a1["GPIO2"], (540, a1["GPIO2"][1])], C["BCLK"], 3, net="BCLK")); o.append(dot(540, a1["GPIO2"][1]))
    o.append(ring(*amp["BCLK"]))
    o.append(wire([amp["LRC"], (552, amp["LRC"][1]), (552, 410), (750, 410), (750, mic["WS"][1]), mic["WS"]], C["WS"], 3, net="WS"))
    o.append(wire([a1["GPIO1"], (552, a1["GPIO1"][1])], C["WS"], 3, net="WS")); o.append(dot(552, a1["GPIO1"][1]))
    o.append(ring(*amp["LRC"]))
    o.append(wire([a1["GPIO4"], (440, a1["GPIO4"][1]), (440, 470), (540, 470), (540, mic["SD"][1]), mic["SD"]], C["micSD"], 3, net="micSD"))
    o.append(wire([a1["GPIO5"], (215, a1["GPIO5"][1]), (215, 88), (552, 88), (552, amp["SD"][1]), amp["SD"]], C["ampSD"], 3, net="ampSD"))
    o.append(wire([a1["GPIO20"], (205, a1["GPIO20"][1]), (205, 545), (scr["SCL"][0], 545), scr["SCL"]], C["SCL"], 3, net="SCL"))
    o.append(wire([a1["GPIO21"], (195, a1["GPIO21"][1]), (195, 552), (scr["SDA"][0], 552), scr["SDA"]], C["SDA"], 3, net="SDA"))
    o.append(wire([a1["GPIO6"], (220, a1["GPIO6"][1]), (220, 320), (185, 320), (185, pb["LBO"][1]), pb["LBO"]], C["LBO"], 2.5, "6 4", net="LBO"))
    o.append(wire([pb["EN"], (pb["EN"][0], 320), sw["a"]], C["BTN"], 2.5, net="EN"))
    o.append(wire([sw["b"], (sw["b"][0], 315), (180, 315), (180, pb["GND"][1])], C["GND"], 2.5, net="GND")); o.append(dot(180, pb["GND"][1]))
    o.append(wire([amp["OUT+"], (752, amp["OUT+"][1]), (752, 715), (548, 715), (548, spk["+"][1]), spk["+"]], "var(--warn)", 3, net="OUT+"))
    o.append(wire([amp["OUT−"], (748, amp["OUT−"][1]), (748, 722), (544, 722), (544, spk["−"][1]), spk["−"]], "var(--warn)", 3, net="OUT-"))
    o.append(T(20, 850, "R1 4.7 kΩ: amp SD → amp GND · R3 10 kΩ: BCLK rod → 3V3 rail (until A1\'s own pull-up is confirmed) · GAIN open · mic SD pull-down in firmware", "s warn-ink"))
    o.append(T(20, 870, "Dots are joints; rings are taps where a rod carries on; every crossing is drawn as a hop, so no two lines ever meet without a dot.", "s muted"))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Pip pin to pin with rails">{"".join(o)}</svg>'


def main():
    src = (HERE / "harness_page.py").read_text()
    style = re.search(r"<style>.*?</style>", src, re.S).group(0)
    H = ['<title>Pip Schematic</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style,
         '<style>:root { --w-pink: #C2185B; } @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --w-pink: #FF7AB6; } } :root[data-theme="dark"] { --w-pink: #FF7AB6; } figure svg { min-width: 0; } figure svg .part { fill: var(--surface); stroke: currentColor; stroke-width: 1.4; } figure svg .dot { fill: var(--ink); } figure svg .hole { fill: none; stroke: var(--muted); stroke-width: 1.4; } figure svg .ring { fill: none; stroke: var(--ink); stroke-width: 2; }'
         ' figure svg .pin { font-size: 10px; font-family: var(--mono); fill: var(--muted); } figure svg .r { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1.4; } figure svg .cap { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.2; } figure svg .spk { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1.2; }</style>',
         '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · final build · the wiring as a schematic</div>',
         '<h1>Pip as rails and lanes</h1>',
         '<p class="lede">No positions, only connections. Three rails along the top carry power: 5 V from the PowerBoost, 3V3 from A1\'s regulator, GND. Nine lanes along the bottom carry signals, one each. Every part hangs between the rails and the lanes; a pin that touches a rail or a lane is a joint. Place the parts anywhere; keep the joints.</p>',
         f'<figure><div class="scroll">{schematic_direct()}</div><figcaption><strong>Pin to pin, rails included.</strong> The two rails stand between A1 and the amp exactly as in the device. 5 V: PowerBoost to A1\'s 5V stub, then the 5 V rod straight across to VIN. GND: the PowerBoost\'s GND wire lands on A1\'s GND stub, the star point; the GND rod runs straight from there to the amp, pinned to the GND rail where it crosses; the mic, screen and button tap the rail, which is a dead end that carries only their own small currents. 3V3: one tap from A1 onto the 3V3 rail, and the screen and mic tap it. The signal rods cross the rails without touching.</figcaption></figure>'
         '<h2>The same thing with shared rails</h2>',
         f'<figure><div class="scroll">{schematic_portrait()}</div><figcaption><strong>Read it top to bottom.</strong> Power comes down from the rails into each part; signals go down from A1 to the lanes and up into the parts that use them. WS and BCLK each have one joint at A1, a ring at the amp (the line passes and is soldered) and a joint at the mic: one rod, two taps. R1 and R3 bridge a lane to a rail; the two capacitors sit on the amp\'s own pins.</figcaption></figure>']
    H.append('<h2>Which product each block is</h2>')
    H.append('<div class="scrollx"><table class="t"><tr><th>Block</th><th>The product you bought</th><th>What it does here</th></tr>'
             f'<tr><td>PowerBoost</td><td>{a("powerboost_owned")} — a copy of {a("powerboost", "Adafruit #2465")}; verify its pins before trusting the labels</td><td>charges the cell, makes the 5 V rail, switch on its EN pin</td></tr>'
             f'<tr><td>cell</td><td>{a("cell1200")}</td><td>the rechargeable battery, plugs into the PowerBoost by JST</td></tr>'
             f'<tr><td>switch</td><td>{a("switch")}</td><td>EN to GND = off</td></tr>'
             f'<tr><td>A1</td><td>{a("a1")}</td><td>the brain; makes 3V3; every signal lane starts here</td></tr>'
             f'<tr><td>Amp</td><td>{a("amp")}</td><td>turns DIN into speaker power; LRC/BCLK are taps on the WS/BCLK lanes</td></tr>'
             f'<tr><td>speaker</td><td>{a("speaker")}</td><td>OUT+ / OUT− only</td></tr>'
             f'<tr><td>Mic</td><td>{a("mic")}</td><td>sound in on GPIO4; L/R to GND picks the left slot</td></tr>'
             f'<tr><td>Screen</td><td>{a("screen")}</td><td>the eyes, on SCL/SDA</td></tr>'
             f'<tr><td>button</td><td>{a("button")}</td><td>GPIO10 to GND when pressed</td></tr>'
             f'<tr><td>R1 4.7 kΩ · R3 10 kΩ</td><td>{a("res")}</td><td>amp SD pull-down · BCLK pull-up (R3 goes once A1\'s GPIO2-to-3V3 reads ~10 kΩ). R2 (GAIN) and R4 (mic SD) dropped 2026-10-14: GAIN open is 9 dB; the firmware pulls GPIO4 down</td></tr>'
             f'<tr><td>C1 220 µF</td><td>{a("cap220")}</td><td>bulk reservoir on the 5 V rail at the amp, stripe to GND</td></tr>'
             f'<tr><td>C2 100 nF</td><td>{a("cap100n")}</td><td>fast decoupling at the amp\'s pins</td></tr>'
             f'<tr><td>the three rails and the lanes</td><td>{a("rod")} (brass) or the {a("ns18", "18 ga nickel silver")} you bought (1.02 mm, the same size; 20 ga for finer); {a("wire26", "26 AWG")} / {a("wire30", "30 AWG")} for the PowerBoost wires</td><td>rails: bare rod; lanes: rod or wire</td></tr>'
             '</table></div>')
    H.append('<h2>How to use this for a layout you choose yourself</h2>')
    H.append('<ol><li>Make the three rails physical: three bare rods, any length you like, anywhere you like, 3 mm apart from each other and from everything else. Every GND goes to the GND rod, every VDD/VCC to the 3V3 rod, VIN and A1\'s 5V to the 5 V rod.</li>'
             '<li>Then each signal lane is one piece of wire or rod from its A1 pin to the pin that uses it; WS and BCLK pass the amp (soldered) on their way to the mic.</li>'
             '<li>The three rules do not move: OUT+ and OUT− only to the speaker; the frame touches nothing; one power source at a time (the PowerBoost on, A1\'s port unused).</li>'
             f'<li>Everything else about distances and heights on the <a href="https://claude.ai/artifact/FAsL4WPArRK6QW7yEg2Nix" target="_blank" rel="noopener">harness page</a> is one worked answer to this diagram, not the only one.</li></ol>')
    H.append('<div class="legend">' + "".join(f'<div><span class="sw" style="background:{C[k]}"></span>{lab}</div>' for k, lab in
             [("5V", "5 V"), ("3V3", "3V3"), ("GND", "GND"), ("WS", "WS"), ("BCLK", "BCLK"), ("DIN", "DIN"), ("micSD", "mic SD"), ("ampSD", "amp SD"), ("BTN", "button"), ("SCL", "SCL"), ("SDA", "SDA")]) + '</div>')
    H.append('<div class="evidence"><p><strong>Sources.</strong> The net list of fast-track Steps 6–11 and the CLAUDE.md pinout, plus the PowerBoost connections from the final-build page. Same connections as the harness, drawn free of geometry.</p></div>')
    H.append('</div>')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
