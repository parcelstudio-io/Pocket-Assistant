"""The one-page wiring sheet: A1 in the middle, every GPIO labelled inside the block, one straight lane per
connection, big dots for joints. Standard schematic convention: lines that cross without a dot do not touch.
Writes edu/pages/wiring-sheet.html and prints edu/pages/print/wiring-sheet.pdf (Letter landscape, one page).
Nets and pins are the CLAUDE.md contract and the net list; no physical geometry."""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import tempfile

from harness_page import a, L
from power_page import L as _  # registers the battery links

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "wiring-sheet.html"
PDF = HERE.parent / "print" / "wiring-sheet.pdf"

W, H = 1330, 850


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def dot(x, y, r=6.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="joint"/>'


def ring(x, y):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" class="tap"/>'


class Router:
    """Orthogonal polylines; a segment hops (semicircle) over every earlier segment of a different net it crosses.
    Same-net crossings are joints and get no hop. Draw rails and the busiest lanes first."""
    R = 8

    def __init__(self):
        self.segs = []          # (x0, y0, x1, y1, net)

    def add(self, x0, y0, x1, y1, net):
        self.segs.append((x0, y0, x1, y1, net))

    def wire(self, pts, cls="rod", net=None):
        path = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            horiz, vert = abs(y0 - y1) < 0.01, abs(x0 - x1) < 0.01
            hops = []
            if horiz:
                lo, hi = min(x0, x1), max(x0, x1)
                for (a0, b0, a1, b1, n) in self.segs:
                    if n == net or abs(a0 - a1) > 0.01:
                        continue
                    if lo + self.R < a0 < hi - self.R and min(b0, b1) + 0.5 < y0 < max(b0, b1) - 0.5:
                        hops.append(a0)
                sgn = 1 if x1 > x0 else -1
                for rx in sorted(set(hops), reverse=(sgn < 0)):
                    path += f" L{rx - self.R * sgn:.1f},{y0:.1f} A{self.R},{self.R} 0 0 {1 if sgn > 0 else 0} {rx + self.R * sgn:.1f},{y0:.1f}"
            elif vert:
                lo, hi = min(y0, y1), max(y0, y1)
                for (a0, b0, a1, b1, n) in self.segs:
                    if n == net or abs(b0 - b1) > 0.01:
                        continue
                    if lo + self.R < b0 < hi - self.R and min(a0, a1) + 0.5 < x0 < max(a0, a1) - 0.5:
                        hops.append(b0)
                sgn = 1 if y1 > y0 else -1
                for ry in sorted(set(hops), reverse=(sgn < 0)):
                    path += f" L{x0:.1f},{ry - self.R * sgn:.1f} A{self.R},{self.R} 0 0 {0 if sgn > 0 else 1} {x0:.1f},{ry + self.R * sgn:.1f}"
            path += f" L{x1:.1f},{y1:.1f}"
            self.segs.append((x0, y0, x1, y1, net))
        return f'<path d="{path}" class="{cls}"/>'


RT = Router()


def wire(pts, cls="rod", net=None):
    return RT.wire(pts, cls, net)


def zigzag(x, y0, y1, net=None):
    """Vertical resistor body between (x,y0) and (x,y1): straight, zigzag in the middle, straight."""
    mid = (y0 + y1) / 2
    z = 11
    pts = [(x, y0), (x, mid - 20)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        pts.append((x + dx, mid - 20 + (i + 0.5) * (40 / 6)))
    pts += [(x, mid + 20), (x, y1)]
    return wire(pts, "thin", net)


def capacitor(x, y0, y1, net=None):
    mid = (y0 + y1) / 2
    return "".join([wire([(x, y0), (x, mid - 6)], "thin", net), wire([(x, mid + 6), (x, y1)], "thin", net),
                    f'<line x1="{x-14}" y1="{mid-6}" x2="{x+14}" y2="{mid-6}" class="thin"/>',
                    f'<line x1="{x-14}" y1="{mid+6}" x2="{x+14}" y2="{mid+6}" class="thin"/>',
                    dot(x, y0), dot(x, y1)])


def block(x, y, w, h, title, sub=None):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="part"/>', T(x + w / 2, y + 26, title, "title", "middle")]
    if sub:
        o.append(T(x + w / 2, y + 46, sub, "sub", "middle"))
    return "".join(o)


def pin(x, y, name, side, fn=None, fnx=None):
    """A pin dot on a block edge, its name just inside, and an optional function further in at fnx."""
    o = [f'<circle cx="{x}" cy="{y}" r="5" class="pinend"/>']
    if side == "R":
        o.append(T(x - 12, y + 5, name, "pin", "end"))
        if fn:
            o.append(T(fnx, y + 5, fn, "fn", "end"))
    elif side == "L":
        o.append(T(x + 12, y + 5, name, "pin", "start"))
        if fn:
            o.append(T(fnx, y + 5, fn, "fn", "start"))
    elif side == "B":
        o.append(T(x, y - 10, name, "pin", "start", f'transform="rotate(-90 {x} {y - 10})"'))
    elif side == "T":
        o.append(T(x, y + 10, name, "pin", "end", f'transform="rotate(-90 {x} {y + 10})"'))
    return "".join(o)


def sheet():
    global RT
    RT = Router()
    o = []
    o.append(T(20, 30, "Pip, every connection on one sheet", "h1"))
    o.append(T(20, 46, "A dot is a joint. A line that hops over another does not touch it. Thick = bare rod of the harness. Thin = insulated wire of the battery storey. Dotted = optional. Ring = tap where a rod carries on.", "sub"))

    # ---------------------------------------------------------------- A1, centre
    AX, AY, AW, AH = 400, 120, 300, 380
    o.append(block(AX, AY, AW, AH, "A1 · ESP32-C3 SuperMini", "left row · right row, counted from the USB end"))
    right = [("5V", 190, "power in"), ("GND", 230, ""), ("3V3", 270, "3.3 V out"), ("GPIO4", 310, "mic SD"),
             ("GPIO3", 350, "DIN"), ("GPIO2", 390, "BCLK"), ("GPIO1", 430, "WS"), ("GPIO0", 470, "unused")]
    left = [("GPIO5", 190, "amp SD"), ("GPIO6", 230, "LBO, optional"), ("GPIO7", 270, "unused"), ("GPIO8", 310, "unused"),
            ("GPIO9", 350, "BOOT, never"), ("GPIO10", 390, "button"), ("GPIO20", 430, "screen SCL"), ("GPIO21", 470, "screen SDA")]
    A = {}
    for name, y, fn in right:
        A[name] = (AX + AW, y); o.append(pin(AX + AW, y, name, "R", fn, AX + AW - 90))
    for name, y, fn in left:
        A[name] = (AX, y); o.append(pin(AX, y, name, "L", fn, AX + 90))

    # ---------------------------------------------------------------- rails
    RX3, RXG = 760, 790
    RY0, RY1 = 130, 806
    o.append(f'<line x1="{RX3}" y1="{RY0}" x2="{RX3}" y2="{RY1}" class="rail"/>')
    o.append(f'<line x1="{RXG}" y1="230" x2="{RXG}" y2="{RY1}" class="rail"/>')      # the GND rail hangs from the GND rod: it starts there
    RT.add(RX3, RY0, RX3, RY1, "3V3"); RT.add(RXG, 230, RXG, RY1, "GND")
    o.append(T(RX3 - 12, 690, "3V3 rail", "lab b", "middle", f'transform="rotate(-90 {RX3 - 12} 690)"'))
    o.append(T(RXG + 16, 690, "GND rail", "lab b", "middle", f'transform="rotate(-90 {RXG + 16} 690)"'))

    # ---------------------------------------------------------------- amp and speaker, right top
    MX, MY, MW, MH = 1000, 130, 190, 330
    o.append(block(MX, MY, MW, MH, "Amp · MAX98357A", "GAIN left open = 9 dB"))
    amp = {}
    for name, y in (("VIN", 190), ("GND", 230), ("SD", 270), ("GAIN", 310), ("DIN", 350), ("BCLK", 390), ("LRC", 430)):
        amp[name] = (MX, y); o.append(pin(MX, y, name, "L"))
    for name, y in (("OUT+", 190), ("OUT−", 230)):
        amp[name] = (MX + MW, y); o.append(pin(MX + MW, y, name, "R"))
    SX, SY, SW, SH = 1210, 150, 110, 120
    o.append(block(SX, SY, SW, SH, "Speaker"))
    spk = {"+": (SX, 190), "−": (SX, 230)}
    o.append(pin(SX, 190, "+", "L")); o.append(pin(SX, 230, "−", "L"))
    o.append(wire([amp["OUT+"], spk["+"]], net="OUT+")); o.append(wire([amp["OUT−"], spk["−"]], net="OUT-"))
    o.append(T(SX + SW / 2, 260, "own leads only", "fn", "middle"))

    # ---------------------------------------------------------------- mic, right bottom
    IX, IY, IW, IH = 1000, 490, 190, 230
    o.append(block(IX, IY, IW, IH, "Mic · INMP441", "chip-side down, pins up"))
    mic = {}
    for name, y in (("SCK", 540), ("WS", 580), ("SD", 620)):
        mic[name] = (IX, y); o.append(pin(IX, y, name, "L"))
    for name, x in (("VDD", 1040), ("GND", 1100), ("L/R", 1160)):
        mic[name] = (x, IY + IH); o.append(pin(x, IY + IH, name, "B"))
    o.append(T(IX + 14, 660, "SCK, WS: from the amp's taps", "fn"))

    # ---------------------------------------------------------------- PowerBoost, switch, button, screen, left
    PX, PY, PW, PH = 40, 130, 220, 170
    o.append(block(PX, PY, PW, PH, "PowerBoost 1000C", "charger · load sharing · 5 V boost"))
    pb = {}
    for name, y in (("5V", 190), ("GND", 230), ("LBO", 270)):
        pb[name] = (PX + PW, y); o.append(pin(PX + PW, y, name, "R"))
    for name, x in (("EN", 120), ("GND", 200)):
        pb[name + "b"] = (x, PY + PH); o.append(pin(x, PY + PH, name, "B"))
    # the cell above the PowerBoost, its JST lead as two thin wires into the board's socket
    o.append(block(40, 52, 220, 54, "1200 mAh cell", "pouch, protected, JST-PH lead"))
    for name, x in (("+", 140), ("−", 160)):
        o.append(f'<circle cx="{x}" cy="106" r="5" class="pinend"/>')
    for x in (140, 160):
        o.append(f'<circle cx="{x}" cy="{PY}" r="5" class="pinend"/>')
    o.append(wire([(140, 106), (140, PY)], "thin", net="CELL+")); o.append(wire([(160, 106), (160, PY)], "thin", net="CELL-"))
    o.append(T(133, 122, "+", "lab", "end")); o.append(T(167, 122, "−", "lab"))
    o.append(T(182, 122, "P5 · JST, red +", "lab"))
    o.append(T(40, 122, "JST", "fn"))
    o.append(block(40, 350, 220, 60, "Slide switch"))
    sw = {"a": (120, 350), "b": (200, 350)}
    o.append(pin(120, 350, "a", "T")); o.append(pin(200, 350, "b", "T"))
    o.append(T(150, 398, "closed = EN at GND = off", "fn", "middle"))
    o.append(block(40, 470, 220, 90, "Button"))
    btn = {"a": (260, 510), "b": (40, 540)}
    o.append(pin(260, 510, "left legs", "R")); o.append(pin(40, 540, "right legs", "L"))
    o.append(block(40, 600, 220, 170, "Screen · SSD1306", "read the silkscreen: pin order varies"))
    scr = {}
    for name, y in (("SCL", 650), ("SDA", 680), ("VCC", 710), ("GND", 740)):
        scr[name] = (260, y); o.append(pin(260, y, name, "R"))

    # ---------------------------------------------------------------- the harness lanes (thick)
    LX = 808                                      # lane labels sit just right of the GND rail
    o.append(wire([A["5V"], amp["VIN"]], net="5V")); o.append(T(LX, 182, "5 V rod", "lab"))
    o.append(wire([A["GND"], amp["GND"]], net="GND")); o.append(dot(RXG, 230)); o.append(T(LX, 222, "GND rod", "lab"))
    o.append(T(798, 258, "drop pin: rail hangs here;", "fn")); o.append(T(798, 271, "amp return goes on to A1", "fn"))
    o.append(wire([A["3V3"], (RX3, 270)], net="3V3")); o.append(dot(RX3, 270)); o.append(T(722, 262, "3V3", "lab", "middle"))
    o.append(wire([A["GPIO3"], amp["DIN"]], net="DIN")); o.append(T(LX, 342, "DIN rod", "lab"))
    o.append(wire([A["GPIO2"], amp["BCLK"]], net="BCLK")); o.append(wire([(975, 390), (975, 540), mic["SCK"]], net="BCLK"))
    o.append(ring(975, 390)); o.append(T(LX, 382, "BCLK rod", "lab"))
    o.append(wire([A["GPIO1"], amp["LRC"]], net="WS")); o.append(wire([(990, 430), (990, 580), mic["WS"]], net="WS"))
    o.append(ring(990, 430)); o.append(T(LX, 422, "WS rod", "lab"))
    o.append(wire([A["GPIO4"], (748, 310), (748, 620), mic["SD"]], net="SD")); o.append(T(LX, 612, "mic SD rod", "lab")); o.append(T(740, 470, "mic SD rod", "lab", "middle", 'transform="rotate(-90 740 470)"'))
    o.append(wire([A["GPIO5"], (395, 190), (395, 68), (960, 68), (960, 270), amp["SD"]], net="ASD")); o.append(T(680, 62, "amp SD rod", "lab", "middle"))
    o.append(wire([A["GPIO10"], (365, 390), (365, 510), btn["a"]], net="BTN")); o.append(T(357, 455, "button rod", "lab", "end"))
    o.append(wire([btn["b"], (20, 540), (20, 798), (RXG, 798)], net="GND")); o.append(dot(RXG, 798)); o.append(T(400, 814, "button GND rod → A1 GND stub", "lab", "middle"))
    o.append(wire([A["GPIO20"], (380, 430), (380, 650), scr["SCL"]], net="SCL")); o.append(T(372, 580, "SCL rod", "lab", "end"))
    o.append(wire([A["GPIO21"], (390, 470), (390, 680), scr["SDA"]], net="SDA")); o.append(T(398, 580, "SDA rod", "lab"))
    o.append(wire([scr["VCC"], (405, 710), (405, 752), (RX3, 752)], net="3V3")); o.append(dot(RX3, 752)); o.append(T(590, 745, "screen VCC tap", "lab", "middle"))
    o.append(wire([scr["GND"], (415, 740), (415, 776), (RXG, 776)], net="GND")); o.append(dot(RXG, 776)); o.append(T(590, 770, "screen GND tap", "lab", "middle"))
    o.append(wire([mic["VDD"], (1040, 752), (RX3, 752)], net="3V3")); o.append(T(900, 745, "mic VDD tap", "lab", "middle"))
    o.append(wire([mic["GND"], (1100, 776), (RXG, 776)], net="GND")); o.append(T(940, 770, "mic GND tap", "lab", "middle"))
    o.append(wire([mic["L/R"], (1160, 798), (1100, 798), (1100, 776)], net="GND")); o.append(dot(1100, 776))
    o.append(T(1172, 802, "L/R → GND: left slot", "fn"))

    # ---------------------------------------------------------------- small parts
    o.append(capacitor(880, 190, 230, net="C1")); o.append(T(866, 204, "C1 220 µF", "lab", "end")); o.append(T(866, 246, "stripe to GND", "fn", "end"))
    o.append(capacitor(940, 190, 230, net="C2")); o.append(T(952, 176, "C2 100 nF", "lab", "end"))
    o.append(zigzag(980, 230, 270, net="R1")); o.append(dot(980, 230)); o.append(dot(980, 270))
    o.append(T(950, 250, "R1 4.7 kΩ", "lab", "end")); o.append(T(962, 290, "holds the amp off at boot", "fn", "end"))
    o.append(zigzag(920, 390, 520, net="R3")); o.append(dot(920, 390)); o.append(wire([(920, 520), (RX3, 520)], "thin", net="3V3")); o.append(dot(RX3, 520))
    o.append(T(900, 452, "R3 10 kΩ", "lab", "end")); o.append(T(900, 467, "BCLK → 3V3", "fn", "end")); o.append(T(900, 481, "boot pin reads high", "fn", "end"))

    # ---------------------------------------------------------------- battery storey (thin wires)
    o.append(wire([pb["5V"], (300, 190), (300, 90), (712, 90), (712, 190)], "thin", net="5V")); o.append(dot(712, 190))
    o.append(T(506, 84, "P1 · PowerBoost 5V → A1's 5V stub · 26 AWG red", "lab", "middle"))
    o.append(wire([pb["GND"], (315, 230), (315, 112), (726, 112), (726, 230)], "thin", net="GND")); o.append(dot(726, 230))
    o.append(T(506, 106, "P2 · PowerBoost GND → A1's GND stub · 26 AWG black", "lab", "middle"))
    o.append(wire([pb["ENb"], sw["a"]], "thin", net="EN")); o.append(T(128, 332, "P3", "lab"))
    o.append(wire([pb["GNDb"], sw["b"]], "thin", net="GND")); o.append(T(208, 332, "P4", "lab"))
    o.append(wire([A["GPIO6"], (335, 230), (335, 270), pb["LBO"]], "opt", net="LBO")); o.append(T(268, 290, "P6 · LBO, optional", "lab"))

    # ---------------------------------------------------------------- never
    o.append(T(20, 832, "Never: OUT+ or OUT− to GND, a rail or the frame · anything but A1's 3V3 feeding the screen or the mic", "warn"))
    o.append(T(20, 846, "A1's USB and the PowerBoost output at the same time · the frame touching any conductor · the 500 mAh cell", "warn"))

    css = ("<style>"
           ".part{fill:var(--surface);stroke:var(--ink);stroke-width:1.8}"
           ".title{font:700 20px 'IBM Plex Sans',sans-serif;fill:var(--ink)}"
           ".sub{font:400 13px 'IBM Plex Sans',sans-serif;fill:var(--muted)}"
           ".h1{font:700 26px 'IBM Plex Sans',sans-serif;fill:var(--ink)}"
           ".pin{font:600 16px 'IBM Plex Mono',monospace;fill:var(--ink)}"
           ".fn{font:400 12px 'IBM Plex Sans',sans-serif;fill:var(--muted)}"
           ".lab{font:600 14px 'IBM Plex Sans',sans-serif;fill:var(--ink)}"
           ".lab.b{font-size:16px}"
           ".warn{font:600 13px 'IBM Plex Sans',sans-serif;fill:var(--warn)}"
           ".rod{fill:none;stroke:var(--ink);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}"
           ".thin{fill:none;stroke:var(--ink);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}"
           ".opt{fill:none;stroke:var(--muted);stroke-width:2.2;stroke-dasharray:3 5;stroke-linecap:round}"
           ".rail{stroke:var(--ink);stroke-width:9;stroke-linecap:round}"
           ".joint{fill:var(--ink)}"
           ".tap{fill:var(--surface);stroke:var(--ink);stroke-width:3}"
           ".pinend{fill:var(--surface);stroke:var(--ink);stroke-width:2}"
           "</style>")
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Pip wiring sheet">{css}{"".join(o)}</svg>'


NOTES = [
    ("The harness: bare rods", [
        ("5 V rod · A1 5V → amp VIN", "The only 5 V in the device goes to two pins: A1's own input and the amplifier. The amp wants 5 V because loudness is voltage: it can swing twice what it could at 3.3 V, which is four times the sound. One straight rod across the channel, crossing both rails without touching."),
        ("GND rod · A1 GND → amp GND, with the drop pin", "The amplifier is the one part that pulls current in bursts, so its return runs on its own rod straight to A1's ground stub. A 3 mm pin under that rod drops onto the GND rail and makes the rail ground. The quiet rail hangs off the busy rod instead of carrying its current."),
        ("3V3 tap · A1 3V3 → 3V3 rail", "A1 has a small regulator that turns 5 V into 3.3 V, and its 3V3 pin is that regulator's output. One tap feeds the rail, and after that nobody runs back to A1 for power. The screen and the mic are 3.3 V parts; the mic dies above 3.6 V."),
        ("DIN rod · GPIO3 → amp DIN", "The sound going out, as bits. One sender, one listener, one rod."),
        ("BCLK rod · GPIO2 → amp BCLK, then on to mic SCK", "The bit clock ticks 1,024,000 times a second and is the metronome both the amp and the mic play to, so one rod serves both with a tap at the amp. R3 sits on this line because GPIO2 is a boot-strapping pin the chip reads at power-on and it must be high then."),
        ("WS rod · GPIO1 → amp LRC, then on to mic WS", "The word clock flips 16,000 times a second to say left slot, right slot. Shared with the amp and the mic for the same reason as BCLK: everyone must agree on the beat."),
        ("mic SD rod · GPIO4 → mic SD", "The sound coming in, as bits. The mic drives this line only during its own slot and lets go the rest of the time, so the firmware switches on GPIO4's internal pull-down to keep it quiet in between. That is why there is no resistor on it."),
        ("amp SD rod · GPIO5 → amp SD", "The amplifier's on-off pin, which A1 pulls high only while Pip is speaking. It runs over the top of everything because GPIO5 is on A1's left row and the amp is on the right. R1 holds it low whenever A1 is not driving it."),
        ("button rod · GPIO10 → button, and the button GND rod", "Pressing the button connects GPIO10 to ground; A1 pulls the pin up internally, so it reads high until pressed. The button's other legs go to A1's GND stub by a short rod. Plain high or low, no timing."),
        ("SCL rod and SDA rod · GPIO20, GPIO21 → screen", "I²C: SCL is the clock, SDA the data, and the screen only listens. Both idle at 3.3 V and get pulled low to talk; the pull-up resistors that need are already on the screen module. The two rods also hold the screen up, 17.5 mm above the amp."),
        ("screen VCC tap and screen GND tap", "The screen's power, dropped from its floating position onto the front ends of the two rails. Short taps to the nearest rail, not rods back to A1."),
        ("mic VDD tap, mic GND tap, and the L/R link", "The mic's power from the back ends of the two rails. The L/R pin tied to the mic's own GND selects the left I²S slot, the one the firmware listens to. All three are short because the mic lies right beside the rails."),
        ("speaker · amp OUT+ and OUT− only", "The amp drives the speaker with a bridge: each output is a switched node that sits at 5 V half the time. Neither is ground, and tying one to the rail shorts 5 V straight through a transistor. The speaker gets its own two leads, twisted, and nothing else."),
    ]),
    ("The four small parts", [
        ("R1 · 4.7 kΩ, amp SD → amp GND", "Between power-on and the firmware running, GPIO5 is undefined. This resistor keeps the amp's shutdown pin low through that gap so the speaker cannot pop or sit at full gain on garbage."),
        ("R3 · 10 kΩ, BCLK rod → 3V3 rail", "GPIO2 must read high the instant the chip powers on, and the amp and mic only listen on this line, so nothing else holds it up. Ten kilohms is far too weak to bother the clock afterwards. One meter check retires it: about 10 kΩ between GPIO2 and 3V3 with A1 unpowered means the board has its own."),
        ("C1 · 220 µF, 5 V net → GND, stripe to GND", "A bass note or a Wi-Fi burst asks for a few hundred milliamps for a few milliseconds, and a long thin wire cannot deliver that fast. This capacitor is a local reservoir that answers the slow bursts so the 5 V does not sag and reset A1. The stripe marks the negative lead."),
        ("C2 · 100 nF, at the amp's VIN and GND pins", "The fast part of the same job: it answers the spikes the 220 µF is too slow for. It sits at the pins because a reservoir 50 mm away is a reservoir with a straw."),
    ]),
    ("The battery storey: insulated wires", [
        ("P1 · PowerBoost 5V → A1's 5V stub, 26 AWG red", "That stub is where USB power used to enter, so every rod downstream sees the same 5 V it always did. The 5 V rod carries it on to the amp as before. Nothing in the harness changes."),
        ("P2 · PowerBoost GND → A1's GND stub, 26 AWG black", "One ground meeting point for the supply, A1 and the amp. The rail stays a dead end, so the amp's current has no loop to run through the signal rods."),
        ("P3 and P4 · EN through the slide switch to PowerBoost GND", "EN is a logic input that draws microamps, so a tiny switch controls the whole load without carrying its current or dropping volts where volts are scarce. Closed means EN at ground means output off. The cell stays on the charger even when off, so it charges either way."),
        ("P5 · the cell's JST into the PowerBoost socket", "The plug is the only connection the cell will ever have: factory-terminated, keyed, behind the cell's own protection board. Meter + and − against the board's silkscreen before the first plug-in. No solder, no brass, no iron within 10 cm."),
        ("P6 · PowerBoost LBO → A1 GPIO6, optional", "An open-drain flag that goes low when the cell reaches 3.2 V. A free GPIO reads it so the face can warn before the cell cuts out. Pip runs without it."),
        ("A1's USB-C · nothing, Kapton over it", "On this board the 5V stub is the USB VBUS node with no diode, so a cable there would tie two supplies together. Flashing happens with the PowerBoost switched off."),
    ]),
]


def notes_html():
    o = ['<h2>Each line, in three sentences or fewer</h2>']
    for head, items in NOTES:
        o.append(f'<h3>{esc(head)}</h3><dl class="notes">')
        for term, body in items:
            o.append(f'<dt>{esc(term)}</dt><dd>{esc(body)}</dd>')
        o.append('</dl>')
    return "".join(o)


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def print_pdf():
    """One Letter landscape page, black only."""
    pcss = ("<style>@page{size:letter landscape;margin:7mm} html,body{background:#fff;margin:0}"
            ":root{--bg:#fff;--surface:#fff;--ink:#000;--muted:#333;--warn:#000}"
            "svg{width:262mm;height:auto;display:block;margin:0 auto}</style>")
    html = "<!doctype html><meta charset=utf-8><title>Wiring sheet</title>" + pcss + sheet()
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "ws.html"; pdf = pathlib.Path(d) / "ws.pdf"
        src.write_text(html)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=120)
        shutil.copyfile(pdf, PDF)
    info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
    print("wrote", PDF, [l for l in info.splitlines() if l.startswith(("Pages", "Page size"))])


def print_notes(pt=8.0, cols=2):
    """The notes alone: Letter portrait, two columns, small type, black only; aims for one page."""
    src = (HERE.parent / "wiring-notes.html").read_text()
    pcss = (f"<style>@page{{size:letter;margin:8mm 9mm}} html,body{{background:#fff!important;color:#000!important;font-size:{pt}pt!important;line-height:1.28}}"
            ":root{--bg:#fff;--surface:#fff;--ink:#000;--muted:#222;--line:#999;--accent:#000;--accent-ink:#000;--accent-tint:#f2f2f2;--code-bg:#f0f0f0}"
            ".wrap{max-width:none;padding:0} .eyebrow{font-size:7pt} h1{font-size:14pt;margin:0 0 2pt} .lede{font-size:8pt;margin:0 0 4pt}"
            f"h2{{display:none}} dl.notes{{margin:0}} .cols{{column-count:{cols};column-gap:7mm}} h3{{font-size:9.5pt;margin:6pt 0 2pt;break-after:avoid}}"
            "dl.notes dt{font-weight:600;margin-top:4pt;break-after:avoid} dl.notes dd{margin:1pt 0 0;color:#222} dl.notes div{break-inside:avoid}"
            ".evidence{font-size:7pt;margin:4pt 0 0;padding:0;border:0;background:none;break-inside:avoid} .evidence p{margin:0} p,dd{max-width:none}</style>")
    # group each dt/dd pair so a column break never splits them, and wrap the notes in the column box
    body = src.replace("<dt>", "<div><dt>").replace("</dd>", "</dd></div>")
    i = body.index("<h2>"); j = body.index('<div class="evidence">')
    k = body.index("</div>", j) + len("</div>")
    body = body[:i] + '<div class="cols">' + body[i:k] + "</div>" + body[k:]
    html = "<!doctype html><meta charset=utf-8>" + body.replace("</style>", "</style>" + pcss, 1)
    out = HERE.parent / "print" / "wiring-notes.pdf"
    with tempfile.TemporaryDirectory() as d:
        h = pathlib.Path(d) / "wn.html"; pdf = pathlib.Path(d) / "wn.pdf"
        h.write_text(html)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{h}"], check=True, capture_output=True, timeout=120)
        shutil.copyfile(pdf, out)
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


def main():
    H_ = ['<title>Wiring Sheet</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
          '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">',
          style(),
          '<style>'
          ' .wrap{max-width:none}'
          ' figure.sheet{width:100%;margin:0 0 12px;text-align:center}'
          ' figure.sheet .scroll{overflow:visible}'
          ' figure.sheet svg{width:auto;height:auto;max-width:100%;max-height:calc(100vh - 20px);display:inline-block}'
          ' dl.notes dt{font-weight:600;margin-top:10px} dl.notes dd{margin:2px 0 0 0;color:var(--muted)}'
          ' .tools{display:flex;gap:8px;align-items:center;margin:4px 0 8px} .tools button{font:inherit;padding:6px 12px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink);cursor:pointer}'
          ' body.rot figure.sheet{height:calc(100vw * 1330 / 850);position:relative} body.rot figure.sheet .scroll{position:absolute;left:50%;top:50%;width:calc(100vh - 24px);transform:translate(-50%,-50%) rotate(90deg)} body.rot figure.sheet svg{width:100%;max-height:none}'
          ' @media print{@page{size:letter landscape;margin:7mm} .eyebrow,h1,.lede,.tools,figcaption,p.parts,.evidence{display:none!important} .wrap{padding:0} figure.sheet{margin:0;border:0;padding:0;background:#fff} figure.sheet svg{width:262mm}}'
          '</style>',
          '<script>function rotSheet(){document.body.classList.toggle("rot")}</script>',
          '<div class="wrap">',
          f'<figure class="sheet"><div class="scroll">{sheet()}</div><figcaption><strong>The sheet fits the width of the window; on a phone, rotate it or turn the phone.</strong> Thick lines are the bare rods of the harness, thin lines the insulated wires of the battery storey. A dot is a joint; a ring is a tap where a rod carries on; a crossing without a dot does not touch.</figcaption></figure>',
          '<div class="eyebrow">Pocket AI Assistant · build day · the wiring on one sheet</div>',
          '<h1>Every connection on one sheet</h1>',
          '<p class="lede">A1 in the middle with every GPIO named inside the block; one line per connection to the amp, the mic, the screen, the button and the battery board. No physical layout: any arrangement that keeps these joints is the same device.</p>',
          '<div class="tools"><button type="button" onclick="rotSheet()">Rotate for a phone held upright</button><button type="button" onclick="window.print()">Print, landscape</button></div>',
          f'<p class="parts">Parts: {a("a1", "A1 SuperMini")}, {a("amp")}, {a("mic", "INMP441")}, {a("screen", "SSD1306")}, {a("speaker")}, {a("button", "button")}, {a("powerboost_owned", "PowerBoost 1000C copy")}, {a("cell1200", "1200 mAh cell")}, {a("switch", "slide switch")}; R1 and R3 from the {a("res", "resistor kit")}, C1 from the {a("cap220", "electrolytic kit")}, C2 from the {a("cap100n", "ceramic kit")}.</p>',
          notes_html(),
          '<div class="evidence"><p><strong>Sources.</strong> Pins from the CLAUDE.md hardware contract; nets from the harness net list and the final-build power page; reasons from Why the Wiring; R2 and R4 dropped 2026-10-14. Not built.</p></div>',
          '</div>']
    OUT.write_text("\n".join(H_))
    print("wrote", OUT, OUT.stat().st_size)
    print_pdf()
    # the notes on their own, as a portrait reading page
    N = ['<title>Wiring Notes</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">',
         style(), '<style>dl.notes dt{font-weight:600;margin-top:10px} dl.notes dd{margin:2px 0 0 0;color:var(--muted)}</style>', '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · build day · the wiring sheet, line by line</div>',
         '<h1>Every line on the sheet, explained</h1>',
         '<p class="lede">The companion to the one-page wiring sheet. One entry per line on the drawing, three sentences at most: what it joins and why it is done that way.</p>',
         notes_html(),
         '<div class="evidence"><p><strong>Sources.</strong> The net list, Why the Wiring and the final-build power page. Not built.</p></div>', '</div>']
    NOUT = HERE.parent / "wiring-notes.html"
    NOUT.write_text("\n".join(N)); print("wrote", NOUT, NOUT.stat().st_size)
    print_notes()


if __name__ == "__main__":
    main()
