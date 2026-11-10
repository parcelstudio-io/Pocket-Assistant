"""Builds docs/pages/cyber-dawn-standin-wiring.html and docs/pages/print/cyber-dawn-standin-wiring.pdf:
the whole Phase 1 bench of Cyber Dawn wired to the stand-in controller (the small Adafruit RP2040 board
that came free with the 2026-10-19 order) instead of the controller board that is still in transit.
Asked for by the builder on 2026-10-31 so the bench can be built now; nothing done here is undone
when the controller board arrives, every wire just moves to the pin in the last column of the table.

Same drawing rules as cyber-dawn-wiring.html (hops at every crossing, no lane near a foreign pin dot;
the check() below refuses to write the page otherwise). Pin facts read 2026-10-31 from the Adafruit
learn guide for the board, its CircuitPython pins.c, and the product page: STEMMA QT on GPIO12/13,
RAW = USB 5 V after a 500 mA fuse, the 3V pin good for 500 mA, CLK and SCK both name GPIO18.
Naming rule (2026-10-30): component types with the link on the word, no product codes in prose."""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
OUT = PAGES / "cyber-dawn-standin-wiring.html"
PRINT = PAGES / "print"
BENCH = PAGES / "cyber-dawn-bench.html"

W, H = 1360, 860

A = "https://www.adafruit.com/product/"
AMZ = "https://www.amazon.com/dp/"
LINK = {
    "standin": A + "5302",
    "controller": "https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894",
    "display": A + "2719", "clock": A + "5188", "coin": AMZ + "B0D8T4C5PK", "encoder": A + "6310",
    "speaker": A + "1669", "snooze": A + "1505", "proximity": A + "4161", "accel": A + "2809", "climate": A + "4566",
    "qt_cable": A + "4210", "qt_header": A + "4209", "amp": AMZ + "B0CDWXZZCH", "arm": AMZ + "B09R434VJQ",
    "cp_board": "https://circuitpython.org/board/adafruit_kb2040/",
    "cp_libs": "https://circuitpython.org/libraries",
}

# ----------------------------------------------------------------------------- the pin map
# (job, stand-in silkscreen, GPIO, CircuitPython name, controller board pin later, note)
PINMAP = [
    ("I²C SDA, the STEMMA QT chain", "QT socket", 12, "board.SDA (board.STEMMA_I2C())", "GPIO8", "No wire: the first QT cable plugs straight into the socket."),
    ("I²C SCL", "QT socket", 13, "board.SCL", "GPIO9", ""),
    ("3.3 V to the display and the chain", "3V", None, "", "3V3", "The socket feeds the chain; one wire feeds the display. 500 mA budget."),
    ("Ground", "G, GND, GND", None, "", "GND", "Three ground pins; any one, all are the same copper."),
    ("Display clock", "CLK", 18, "board.CLK (also board.SCK)", "GPIO12", "The hardware SPI0 clock."),
    ("Display data", "MOSI", 19, "board.MOSI", "GPIO11", ""),
    ("Display chip select", "D10", 10, "board.D10", "GPIO10", ""),
    ("Display data / command", "D9", 9, "board.D9", "GPIO6", ""),
    ("Display reset", "D8", 8, "board.D8", "GPIO7", ""),
    ("Amp bit clock", "D2", 2, "board.D2", "GPIO14", "I²S on this chip is a PIO program: word select must be the GPIO right after bit clock, so D2 and D3."),
    ("Amp word clock", "D3", 3, "board.D3", "GPIO15", ""),
    ("Amp data", "D4", 4, "board.D4", "GPIO16", ""),
    ("Amp shutdown", "D5", 5, "board.D5", "GPIO17", "10 kΩ to ground at the amp, as on the controller board."),
    ("Amp 5 V", "RAW", None, "", "5V", "USB 5 V after the board's 500 mA fuse. Bench volume only; see the limits."),
    ("Clock alarm (SQW)", "D6", 6, "board.D6", "GPIO4", "10 kΩ to 3V: the output is open-drain."),
    ("Encoder INT", "D7", 7, "board.D7", "GPIO1", "Pull.UP in code."),
    ("Snooze button", "A0", 26, "board.A0", "GPIO18", "Other leg to GND; Pull.UP in code."),
    ("Arm switch", "A1", 27, "board.A1", "GPIO21", "Other leg to GND; Pull.UP in code."),
    ("Accelerometer INT, Phase 3", "A2", 28, "board.A2", "GPIO5", "Not wired yet."),
    ("Free", "D0, D1, A3, MISO", None, "", "", "D0/D1 are the UART; leave them for a serial probe."),
]


def audit():
    used = {}
    for job, silk, g, cp, later, note in PINMAP:
        if g is None:
            continue
        assert g not in used, f"GPIO{g} used twice: {used[g]} and {job}"
        used[g] = job
    assert 2 in used and 3 in used, "I2S needs BCLK on D2 and LRC on D3"
    assert 17 not in used and 11 not in used, "GPIO17 is the NeoPixel, GPIO11 the BOOT button"
    return used


# ----------------------------------------------------------------------------- drawing helpers
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def dot(x, y, r=6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="joint"/>'


class Router:
    """Orthogonal polylines; a segment hops (semicircle) over every earlier segment of a different net it crosses.
    Same-net crossings are joints and get no hop. Draw rails and the busiest lanes first."""
    R = 8

    def __init__(self):
        self.segs = []
        self.pins = []

    def pin(self, x, y, net):
        self.pins.append((x, y, net))

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

    def check(self, min_pin=14, min_lane=14):
        bad = []
        for (x0, y0, x1, y1, n) in self.segs:
            for (px, py, pn) in self.pins:
                if pn == n:
                    continue
                if abs(x0 - x1) < 0.01 and min(y0, y1) - 2 <= py <= max(y0, y1) + 2 and abs(px - x0) < min_pin:
                    bad.append(f"vertical {n} at x={x0} passes {abs(px-x0):.0f}px from pin ({px},{py}) of {pn}")
                if abs(y0 - y1) < 0.01 and min(x0, x1) - 2 <= px <= max(x0, x1) + 2 and abs(py - y0) < min_pin:
                    bad.append(f"horizontal {n} at y={y0} passes {abs(py-y0):.0f}px from pin ({px},{py}) of {pn}")
        crossings = 0
        for i, (x0, y0, x1, y1, n) in enumerate(self.segs):
            for (a0, b0, a1, b1, m) in self.segs[:i]:
                if m == n:
                    continue
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


def block(x, y, w, h, title, sub=None, cls="part"):
    tcls = "lab" if cls == "later" else "title"
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>', T(x + w / 2, y + 24, title, tcls, "middle")]
    if sub:
        o.append(T(x + w / 2, y + 42, sub, "sub", "middle"))
    return "".join(o)


def pin(rt, x, y, name, side, net, fn=None, fnx=None):
    rt.pin(x, y, net)
    o = [f'<circle cx="{x}" cy="{y}" r="4.5" class="pinend"/>']
    if side == "R":
        o.append(T(x - 10, y + 5, name, "pin", "end"))
        if fn:
            o.append(T(fnx, y + 5, fn, "fn", "end"))
    elif side == "L":
        o.append(T(x + 10, y + 5, name, "pin", "start"))
        if fn:
            o.append(T(fnx, y + 5, fn, "fn", "start"))
    elif side == "B":
        o.append(T(x, y - 8, name, "pin", "start", f'transform="rotate(-90 {x} {y - 8})"'))
    elif side == "T":
        o.append(T(x, y + 8, name, "pin", "end", f'transform="rotate(-90 {x} {y + 8})"'))
    return "".join(o)


def gnd(x, y):
    return f'<path d="M{x},{y} L{x},{y+12} M{x-11},{y+12} L{x+11},{y+12} M{x-7},{y+17} L{x+7},{y+17} M{x-3},{y+22} L{x+3},{y+22}" class="thin"/>'


def flag(x, y, label):
    return f'<path d="M{x},{y} L{x},{y-12} M{x-9},{y-12} L{x+9},{y-12}" class="thin"/>' + T(x, y - 17, label, "lab", "middle")


def zigzag(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2
    z = 9
    pts = [(x, y0), (x, mid - 16)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        pts.append((x + dx, mid - 16 + (i + 0.5) * (32 / 6)))
    pts += [(x, mid + 16), (x, y1)]
    return rt.wire(pts, "thin", net)


def capacitor(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2
    return "".join([rt.wire([(x, y0), (x, mid - 5)], "thin", net), rt.wire([(x, mid + 5), (x, y1)], "thin", net),
                    f'<line x1="{x-12}" y1="{mid-5}" x2="{x+12}" y2="{mid-5}" class="thin"/>',
                    f'<line x1="{x-12}" y1="{mid+5}" x2="{x+12}" y2="{mid+5}" class="thin"/>', dot(x, y0), dot(x, y1)])


# ----------------------------------------------------------------------------- the physical board inset
TOP_EDGE = ["RAW", "G", "RST", "3V", "A3", "A2", "A1", "A0", "CLK", "MISO", "MOSI", "D10"]
BOTTOM_EDGE = ["D0", "D1", "GND", "GND", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"]
USED = {"RAW", "G", "3V", "A2", "A1", "A0", "CLK", "MOSI", "D10", "GND", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"}


def board_inset(x, y, w=290, h=90):
    """The stand-in seen from the top, USB-C at the left, the QT socket at the right. Used pads filled."""
    o = [T(x, y - 46, "Where the pins are: the stand-in from above, USB-C on the left", "lab")]
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" class="part"/>')
    o.append(f'<rect x="{x-6}" y="{y + h/2 - 11}" width="22" height="22" rx="3" class="usb"/>'); o.append(T(x + 5, y + h / 2 + 4, "USB", "fn", "middle"))
    o.append(f'<rect x="{x + w - 14}" y="{y + h/2 - 13}" width="18" height="26" rx="3" class="cable"/>')
    o.append(T(x + w - 5, y + h / 2 + 3, "QT", "fn", "middle", f'transform="rotate(-90 {x + w - 5} {y + h/2 + 3})"'))
    o.append(T(x + w / 2 - 6, y + h / 2 + 4, "RP2040 · BOOT button · NeoPixel", "fn", "middle"))
    x0, pitch = x + 40, 20
    for i, (top, bot) in enumerate(zip(TOP_EDGE, BOTTOM_EDGE)):
        px = x0 + i * pitch
        for name, py, up in ((top, y, True), (bot, y + h, False)):
            cls = "joint" if name in USED else "pinend"
            o.append(f'<circle cx="{px}" cy="{py}" r="3.5" class="{cls}"/>')
            ty = py - 8 if up else py + 8
            o.append(T(px + 3.5, ty, name, "tiny", "start" if up else "end", f'transform="rotate(-90 {px + 3.5} {ty})"'))
    o.append(T(x, y + h + 56, "filled pad = used here · open pad = free (D0/D1 are the UART, A3 and MISO spare)", "fn"))
    return "".join(o)


# ----------------------------------------------------------------------------- the sheet
def sheet():
    rt = Router()
    w = rt.wire
    o = [T(20, 30, "Cyber Dawn on the stand-in controller: every Phase 1 connection on one sheet", "h1"),
         T(20, 48, "A dot is a joint. A line that hops over another does not touch it. Thick = wire you solder or plug. Brass = the STEMMA QT chain. Dotted = later. Ground symbols all mean the stand-in's G / GND pins. Pins are grouped by job; the inset shows where they sit.", "sub")]

    # ---------------------------------------------------------------- controller block, centre
    DX, DY, DW, DH = 560, 110, 280, 500
    o.append(block(DX, DY, DW, DH, "Stand-in controller", "RP2040 · 3.3 V logic · CircuitPython"))
    o.append(T(DX + DW / 2, DY + 60, "the small Adafruit board from the 2026-10-19 order", "fn", "middle"))
    L = {}
    for name, y, fn, net in (("3V", 190, "3.3 V out, 500 mA", "3V3"), ("GND", 220, "", "GND"), ("CLK", 260, "GPIO18 · clock", "SCLK"), ("MOSI", 290, "GPIO19 · data", "MOSI"),
                             ("D10", 320, "GPIO10 · CS", "CS"), ("D9", 350, "GPIO9 · DC", "DC"), ("D8", 380, "GPIO8 · RESET", "RST")):
        L[name] = (DX, y); o.append(pin(rt, DX, y, name, "L", net, fn, DX + 58))
    R = {}
    for name, y, fn, net in (("D6", 170, "clock alarm", "RTCINT"), ("D7", 200, "encoder INT", "ANOINT"), ("A2", 230, "accel INT, later", "ACCINT"),
                             ("RAW", 412, "USB 5 V, fused 500 mA", "5V"),
                             ("D2", 440, "BCLK", "BCLK"), ("D3", 470, "LRC", "LRC"), ("D4", 500, "DIN", "DIN"), ("D5", 530, "amp SD", "SD")):
        R[name] = (DX + DW, y); o.append(pin(rt, DX + DW, y, name, "R", net, fn, DX + DW - 50))
    # the QT socket on the right edge
    o.append(f'<rect x="{DX + DW - 70}" y="316" width="70" height="60" rx="5" class="cable"/>')
    o.append(T(DX + DW - 35, 336, "QT socket", "pinlab", "middle")); o.append(T(DX + DW - 35, 352, "SDA GPIO12", "fn", "middle")); o.append(T(DX + DW - 35, 366, "SCL GPIO13", "fn", "middle"))
    rt.pin(DX + DW, 345, "I2C")
    B = {}
    for name, x, net in (("A0", 600, "SNZ"), ("GND", 650, "GND"), ("A1", 730, "ARM")):
        B[name] = (x, DY + DH); o.append(pin(rt, x, DY + DH, name, "B", net))
    o.append(f'<rect x="{DX+8}" y="{DY+DH-22}" width="34" height="14" rx="3" class="usb"/>'); o.append(T(DX + 25, DY + DH - 11, "USB", "fn", "middle"))
    o.append(block(250, 58, 590, 40, "When the controller board arrives: every wire moves to the pin in the table below · nothing is undone", None, "later"))
    o.append(w([(DX + DW / 2, 98), (DX + DW / 2, DY)], "opt", "LATER"))

    # ---------------------------------------------------------------- OLED, left
    OX, OY, OW, OH = 60, 110, 300, 310
    o.append(block(OX, OY, OW, OH, "2.42\" OLED display", "3.3 V only · 4-wire SPI · BS1/BS2 jumpers set to SPI"))
    P = {}
    for name, y, net in (("VCC", 190, "3V3"), ("GND", 220, "GND"), ("SCLK", 260, "SCLK"), ("MOSI", 290, "MOSI"), ("CS", 320, "CS"), ("DC", 350, "DC"), ("RST", 380, "RST")):
        P[name] = (OX + OW, y); o.append(pin(rt, OX + OW, y, name, "R", net))
    o.append(T(OX + 16, 404, "level shifter from the kit: not used", "fn"))
    o.append(w([L["3V"], P["VCC"]], "rod", "3V3")); o.append(T(500, 182, "3V", "lab", "middle"))
    o.append(w([L["GND"], P["GND"]], "rod", "GND")); o.append(T(500, 212, "GND", "lab", "middle"))
    for a, b, lab, net in (("CLK", "SCLK", "clock", "SCLK"), ("MOSI", "MOSI", "data out", "MOSI"), ("D10", "CS", "chip select", "CS"), ("D9", "DC", "data / command", "DC"), ("D8", "RST", "reset", "RST")):
        o.append(w([L[a], P[b]], "rod", net)); o.append(T(500, L[a][1] - 8, lab, "lab", "middle"))
    o.append(capacitor(rt, 400, 190, 220, "C_OLED")); o.append(T(400, 240, "220 µF, from the kit", "fn", "middle"))

    # ---------------------------------------------------------------- the board inset, under the OLED
    o.append(board_inset(70, 500))

    # ---------------------------------------------------------------- snooze, arm, USB power, bottom
    o.append(block(560, 660, 80, 60, "Snooze", "16 mm push")); o.append(block(690, 660, 80, 60, "Arm", "slide"))
    rt.pin(600, 660, "SNZ"); rt.pin(730, 660, "ARM"); rt.pin(630, 660, "GND"); rt.pin(700, 660, "GND")
    o.append(w([B["A0"], (600, 660)], "rod", "SNZ")); o.append(w([(630, 660), (630, 640), (650, 640)], "rod", "GND"))
    o.append(w([B["A1"], (730, 660)], "rod", "ARM")); o.append(w([(700, 660), (700, 640), (650, 640)], "rod", "GND"))
    o.append(w([B["GND"], (650, 640)], "rod", "GND")); o.append(dot(650, 640))
    o.append(T(560, 737, "active-low: Pull.UP in code holds them high", "fn"))
    o.append(block(370, 660, 170, 60, "USB-C, data cable", "laptop; 2 A adapter for sound"))
    o.append(w([(455, 660), (455, 630), (DX + 25, 630), (DX + 25, DY + DH - 8)], "thin", "USB"))

    # ---------------------------------------------------------------- I2C column, right
    CX, CW, CH = 1010, 170, 48
    chain = [("rotary encoder", "0x49"), ("real-time clock", "0x68"), ("proximity + light", "0x60"), ("accelerometer", "0x18/19"), ("temp / humidity", "0x38")]
    ys = [116, 186, 256, 326, 396]
    for (name, addr), y in zip(chain, ys):
        o.append(f'<rect x="{CX}" y="{y}" width="{CW}" height="{CH}" rx="7" class="part"/>')
        o.append(T(CX + 10, y + 19, name, "pinlab")); o.append(T(CX + 10, y + 37, "I²C " + addr, "fn"))
    o.append(f'<rect x="{CX}" y="466" width="{CW}" height="{CH}" rx="7" class="later"/>')
    o.append(T(CX + 10, 485, "fuel gauge", "pinlab")); o.append(T(CX + 10, 503, "I²C 0x36 · Phase 4, not here", "fn"))
    BX = 988
    o.append(w([(BX, ys[0] + CH / 2), (BX, ys[-1] + CH / 2)], "bus", "I2C"))
    for y in ys:
        o.append(w([(BX, y + CH / 2), (CX, y + CH / 2)], "bus", "I2C")); o.append(dot(BX, y + CH / 2, 5))
    o.append(T(971, 232, "STEMMA QT chain · 4 wires", "fn", "middle", 'transform="rotate(-90 971 232)"'))
    o.append(T(971, 430, "one QT cable per hop", "fn", "middle", 'transform="rotate(-90 971 430)"'))
    # socket to the chain: one QT cable, no header cable at all
    o.append(w([(DX + DW, 345), (BX, 345)], "bus", "I2C")); o.append(dot(BX, 345))
    o.append(T(914, 336, "first QT cable", "fn", "middle")); o.append(T(914, 362, "straight into the socket", "fn", "middle"))
    # the two interrupt wires, over the top
    o.append(w([R["D6"], (850, 170), (850, 84), (1215, 84), (1215, ys[1] + CH / 2), (CX + CW, ys[1] + CH / 2)], "rod", "RTCINT"))
    o.append(dot(CX + CW, ys[1] + CH / 2)); o.append(T(CX + CW - 8, ys[1] + CH / 2 + 4, "SQW", "pinlab", "end"))
    o.append(T(862, 62, "clock SQW → D6: the alarm wire", "lab")); o.append(T(862, 76, "open-drain, so the 10 kΩ pull-up is mandatory", "fn"))
    o.append(zigzag(rt, 1190, 84, 36, "RTCINT")); o.append(dot(1190, 84)); o.append(flag(1190, 36, "3V")); o.append(T(1200, 62, "10 kΩ", "lab"))
    o.append(w([R["D7"], (866, 200), (866, 100), (1150, 100), (1150, ys[0])], "rod", "ANOINT")); o.append(dot(1150, ys[0]))
    o.append(T(1156, 112, "INT", "pinlab")); o.append(T(874, 116, "encoder INT → D7 · Pull.UP in code", "fn"))
    o.append(T(DX + DW + 8, 246, "wired in Phase 3", "fn"))

    # ---------------------------------------------------------------- amplifier and speaker, bottom right
    AX, AY, AW, AH = 1010, 580, 170, 210
    o.append(f'<rect x="{AX}" y="{AY}" width="{AW}" height="{AH}" rx="9" class="part"/>')
    o.append(T(AX + 62, AY + 52, "Amplifier", "title", "middle")); o.append(T(AX + 62, AY + 70, "owned HiLetgo", "sub", "middle"))
    Am = {"VIN": (1060, AY), "GND": (1130, AY)}
    rt.pin(1060, AY, "5V"); rt.pin(1130, AY, "GND")
    for name, x in (("VIN", 1060), ("GND", 1130)):
        o.append(f'<circle cx="{x}" cy="{AY}" r="4.5" class="pinend"/>'); o.append(T(x, AY + 18, name, "pin", "middle"))
    for name, y, fn, net in (("BCLK", 670, "bit clock", "BCLK"), ("LRC", 700, "word clock", "LRC"), ("DIN", 730, "audio in", "DIN"), ("SD", 760, "shutdown", "SD")):
        Am[name] = (AX, y); o.append(pin(rt, AX, y, name, "L", net, fn, AX + 58))
    for name, y, net in (("OUT+", 620, "OUT+"), ("OUT−", 650, "OUT-"), ("GAIN", 740, "GAINSTRAP")):
        Am[name] = (AX + AW, y); o.append(pin(rt, AX + AW, y, name, "R", net))
    o.append(block(1230, 590, 110, 100, "Speaker", "4 Ω 3 W, sealed"))
    rt.pin(1230, 620, "OUT+"); rt.pin(1230, 650, "OUT-")
    o.append(w([Am["OUT+"], (1230, 620)], "rod", "OUT+")); o.append(w([Am["OUT−"], (1230, 650)], "rod", "OUT-"))
    o.append(T(1285, 680, "never to ground", "fn", "middle"))
    o.append(w([Am["GAIN"], (1210, 740), (1210, 718)], "thin", "GAINSTRAP")); o.append(flag(1210, 718, "VIN")); o.append(T(1218, 756, "strap = 6 dB", "fn"))
    o.append(w([R["RAW"], (950, 412), (950, 550), (1060, 550), Am["VIN"]], "rod", "5V")); o.append(dot(1060, 550))
    o.append(T(956, 544, "RAW 5 V", "lab"))
    o.append(w([Am["GND"], (1130, 550), (1160, 550)], "rod", "GND")); o.append(dot(1130, 550)); o.append(gnd(1160, 550))
    o.append(f'<line x1="1090" y1="538" x2="1090" y2="562" class="thin"/><line x1="1100" y1="538" x2="1100" y2="562" class="thin"/>')
    o.append(w([(1060, 550), (1090, 550)], "thin", "5V")); o.append(w([(1100, 550), (1130, 550)], "thin", "GND"))
    o.append(T(1095, 530, "220 µF + 100 nF, at the pins", "fn", "middle"))
    for name, pinname, x, net in (("D2", "BCLK", 925, "BCLK"), ("D3", "LRC", 910, "LRC"), ("D4", "DIN", 895, "DIN"), ("D5", "SD", 880, "SD")):
        o.append(w([R[name], (x, R[name][1]), (x, Am[pinname][1]), Am[pinname]], "rod", net))
    o.append(zigzag(rt, 866, 760, 796, "SD")); o.append(dot(866, 760)); o.append(gnd(866, 796))
    o.append(T(854, 782, "10 kΩ: holds SD low until code runs", "fn", "end"))

    o.append(T(20, 852, "Pin facts from the board's Adafruit guide and its CircuitPython pins.c, read 2026-10-31. Not built. The pin audit and the line-clearance check in gen/wiring_standin.py pass.", "sub"))

    bad, crossings = rt.check()
    for b in bad:
        print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    print(f"sheet: {len(rt.segs)} segments, {crossings} crossings (all drawn as hops)")

    css = ("<style>"
           ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
           ".later{fill:var(--paper);stroke:var(--ink-2);stroke-width:1.4;stroke-dasharray:5 4}"
           ".cable{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.4}"
           ".usb{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.2}"
           ".title{font:700 17px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".sub{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".h1{font:900 24px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".pin{font:700 13px 'JetBrains Mono',monospace;fill:var(--ink)}"
           ".pinlab{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink)}"
           ".tiny{font:700 9.5px 'JetBrains Mono',monospace;fill:var(--ink)}"
           ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".lab{font:700 12.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".rod{fill:none;stroke:var(--ink);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
           ".bus{fill:none;stroke:var(--brass);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}"
           ".thin{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
           ".opt{fill:none;stroke:var(--ink-2);stroke-width:2;stroke-dasharray:3 5;stroke-linecap:round}"
           ".joint{fill:var(--ink)}"
           ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
           "</style>")
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cyber Dawn Phase 1 wiring on the stand-in controller">{css}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- the breadboard plan (added 2026-10-31 evening)
# An 830-point board (63 columns, rows a-e and f-j, two rail pairs). The stand-in's two pin rows are 0.6" apart, so it
# straddles the trench with its top-edge pins in row c and its bottom-edge pins in row g; holes a-b and h-j stay free.
# The OLED's 20-pin header goes into row j (module standing on its header, off the bottom edge); the amp's 7-pin header
# into row a (standing, off the top edge). Only the hole each wire end lands in is physical; the drawn path is a plan.
BB_P = 13.0
BB_X0 = 70.0
OLED_PINS = {1: "GND", 2: "3V", 3: "nc", 4: "DC", 5: "WR", 6: "RD", 7: "D0", 8: "D1", 9: "D2", 10: "D3", 11: "D4", 12: "D5", 13: "D6", 14: "D7",
             15: "CS", 16: "RST", 17: "nc", 18: "nc", 19: "nc", 20: "FG"}
OLED_USED = {1: "GND", 2: "3 V in", 4: "DC", 7: "D0 = SPI clock", 8: "D1 = SPI data", 15: "CS", 16: "RESET"}
AMP_PINS = ["LRC", "BCLK", "DIN", "GAIN", "SD", "GND", "VIN"]


def breadboard_svg():
    P, X0 = BB_P, BB_X0
    col = lambda c: X0 + (c - 1) * P
    yR1 = 156.0; yR2 = yR1 + P                     # top rails: red (RAW 5 V), blue (GND)
    ya = yR2 + 2 * P; rows_top = {r: ya + i * P for i, r in enumerate("abcde")}
    yf = rows_top["e"] + 3 * P; rows_bot = {r: yf + i * P for i, r in enumerate("fghij")}
    yR3 = rows_bot["j"] + 2 * P; yR4 = yR3 + P      # bottom rails: blue (GND), red (3 V)
    R = {**rows_top, **rows_bot, "R1": yR1, "R2": yR2, "R3": yR3, "R4": yR4}
    o = []
    t = lambda x, y, s, cls="fn", anchor="start", extra="": T(x, y, s, cls, anchor, extra)
    o.append(t(20, 30, "The same wiring on an 830-point breadboard: where every pin and every wire end goes", "h1"))
    o.append(t(20, 48, "Columns are numbered as on the board. The stand-in straddles the trench, columns 1-12: top-edge pins in row c, bottom-edge pins in row g.", "sub"))
    o.append(t(20, 64, "Only the holes a wire ends in are real; the drawn path is a plan. Colour = job. A small square is a header pin (filled = used); a dot is a wire end.", "sub"))
    # board
    bx0, bx1 = col(1) - 30, col(63) + 30
    o.append(f'<rect x="{bx0:.1f}" y="{yR1 - 16:.1f}" width="{bx1 - bx0:.1f}" height="{yR4 + 16 - (yR1 - 16):.1f}" rx="8" class="bb"/>')
    # rails: lines + holes, split in the middle (REXQualis 830 ships split)
    for y, colr in ((yR1, "rail-r"), (yR2, "rail-b"), (yR3, "rail-b"), (yR4, "rail-r")):
        for c0, c1 in ((1, 31), (32, 63)):
            o.append(f'<line x1="{col(c0) - 6:.1f}" y1="{y:.1f}" x2="{col(c1) + 6:.1f}" y2="{y:.1f}" class="{colr}"/>')
        for c in range(1, 64):
            o.append(f'<circle cx="{col(c):.1f}" cy="{y:.1f}" r="2.4" class="hole"/>')
    o.append(t(col(1) - 24, yR1 + 4, "+", "railtxt")); o.append(t(col(1) - 24, yR2 + 4, "−", "railtxt"))
    o.append(t(col(1) - 24, yR3 + 4, "−", "railtxt")); o.append(t(col(1) - 24, yR4 + 4, "+", "railtxt"))
    o.append(t(col(63) + 16, yR1 + 4, "RAW 5 V", "railname")); o.append(t(col(63) + 16, yR2 + 4, "GND", "railname"))
    o.append(t(col(63) + 16, yR3 + 4, "GND", "railname")); o.append(t(col(63) + 16, yR4 + 4, "3 V", "railname"))
    # terminal holes and row letters, column numbers
    for r, y in {**rows_top, **rows_bot}.items():
        o.append(t(col(1) - 14, y + 3.5, r, "rowlet", "middle")); o.append(t(col(63) + 14, y + 3.5, r, "rowlet", "middle"))
        for c in range(1, 64):
            o.append(f'<circle cx="{col(c):.1f}" cy="{y:.1f}" r="2.4" class="hole"/>')
    for c in (1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60):
        o.append(t(col(c), rows_top["a"] - 7, str(c), "colnum", "middle")); o.append(t(col(c), rows_bot["j"] + 12, str(c), "colnum", "middle"))
    o.append(f'<rect x="{col(1) - 8:.1f}" y="{rows_top["e"] + P * 0.9:.1f}" width="{col(63) - col(1) + 16:.1f}" height="{P * 1.2:.1f}" class="trench"/>')
    # ---- the stand-in, columns 1-12, rows c and g
    yc, yg = rows_top["c"], rows_bot["g"]
    kx0, kx1 = col(1) - 9, col(12) + 9
    o.append(f'<rect x="{kx0:.1f}" y="{yc - 8:.1f}" width="{kx1 - kx0:.1f}" height="{yg - yc + 16:.1f}" rx="5" class="kb"/>')
    o.append(f'<rect x="{kx0 - 20:.1f}" y="{(yc + yg) / 2 - 9:.1f}" width="24" height="18" rx="3" class="usb"/>'); o.append(t(kx0 - 8, (yc + yg) / 2 + 3.5, "USB", "tiny", "middle"))
    o.append(f'<rect x="{kx1 - 6:.1f}" y="{(yc + yg) / 2 - 11:.1f}" width="14" height="22" rx="2" class="cable"/>')
    o.append(t(kx1 + 1, (yc + yg) / 2 + 3, "QT", "tiny", "middle", f'transform="rotate(-90 {kx1 + 1:.1f} {(yc + yg) / 2 + 3:.1f})"'))
    o.append(t((kx0 + kx1) / 2, (yc + yg) / 2 + 4, "stand-in controller", "kbname", "middle"))
    for i, (top, bot) in enumerate(zip(TOP_EDGE, BOTTOM_EDGE)):
        x = col(i + 1)
        for name, y, up in ((top, yc, True), (bot, yg, False)):
            o.append(f'<rect x="{x - 3.2:.1f}" y="{y - 3.2:.1f}" width="6.4" height="6.4" class="{"pinused" if name in USED else "pinfree"}"/>')
            ty = y + 13 if up else y - 7
            o.append(t(x + 3, ty, name, "tiny", "start" if up else "end", f'transform="rotate(-90 {x + 3:.1f} {ty:.1f})"'))
    # ---- OLED header, row j, columns 15-34 (pin 1 at column 15)
    OC = lambda pin: col(14 + pin)
    for pin in range(1, 21):
        x = OC(pin); used = pin in OLED_USED
        o.append(f'<rect x="{x - 3.2:.1f}" y="{rows_bot["j"] - 3.2:.1f}" width="6.4" height="6.4" class="{"pinused" if used else "pinfree"}"/>')
        if used or pin in (1, 20):
            o.append(t(x, rows_bot["j"] + 24, str(pin), "tiny", "middle"))
    ox0, ox1 = OC(1) - 10, OC(20) + 10; oy = yR4 + 26
    o.append(f'<rect x="{ox0:.1f}" y="{oy:.1f}" width="{ox1 - ox0:.1f}" height="44" rx="5" class="module"/>')
    o.append(t((ox0 + ox1) / 2, oy + 18, "2.42-inch OLED module, standing on its 20-pin header in row j", "lab", "middle"))
    o.append(t((ox0 + ox1) / 2, oy + 34, "used: 1 GND · 2 3 V · 4 DC · 7 D0 clock · 8 D1 data · 15 CS · 16 RESET · others empty · pin 1 is the module's marked end", "fn", "middle"))
    # ---- amp header, row a, columns 38-44
    AC = {n: col(38 + i) for i, n in enumerate(AMP_PINS)}
    for n, x in AC.items():
        o.append(f'<rect x="{x - 3.2:.1f}" y="{rows_top["a"] - 3.2:.1f}" width="6.4" height="6.4" class="pinused"/>')
        o.append(t(x + 3, rows_top["a"] - 7, n, "tiny", "end", f'transform="rotate(-90 {x + 3:.1f} {rows_top["a"] - 7:.1f})"'))
    ax0, ax1 = AC["LRC"] - 96, AC["VIN"] + 116; ay = yR1 - 86
    o.append(f'<rect x="{ax0:.1f}" y="{ay:.1f}" width="{ax1 - ax0:.1f}" height="46" rx="5" class="module"/>')
    o.append(t((ax0 + ax1) / 2, ay + 18, "amplifier, standing on its 7-pin header in row a", "lab", "middle"))
    o.append(t((ax0 + ax1) / 2, ay + 34, "OUT+ / OUT− on its far edge → the speaker lead", "fn", "middle"))
    # speaker
    sx = ax1 + 22
    o.append(f'<rect x="{sx:.1f}" y="{ay - 2:.1f}" width="150" height="50" rx="5" class="module"/>')
    o.append(t(sx + 75, ay + 18, "speaker", "lab", "middle")); o.append(t(sx + 75, ay + 34, "4 Ω 3 W · never to ground", "fn", "middle"))
    o.append(f'<path d="M{ax1:.1f},{ay + 14:.1f} L{sx:.1f},{ay + 14:.1f} M{ax1:.1f},{ay + 30:.1f} L{sx:.1f},{ay + 30:.1f}" class="spk"/>')

    # ---- wires: each is (class, [(col,row), ...]) ; the path is orthogonal through the given points
    def pt(c, r):
        return (col(c), R[r])
    def wire(cls, pts, via=None):
        """pts are (col,row) hole names; via is an optional list of raw (x,y) bends between the two ends."""
        (c0, r0), (c1, r1) = pts
        x0, y0 = pt(c0, r0); x1, y1 = pt(c1, r1)
        mids = via or []
        d = f"M{x0:.1f},{y0:.1f}" + "".join(f" L{x:.1f},{y:.1f}" for x, y in mids) + f" L{x1:.1f},{y1:.1f}"
        return (f'<path d="{d}" class="wire {cls}"/>'
                f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="3.4" class="wend {cls}"/><circle cx="{x1:.1f}" cy="{y1:.1f}" r="3.4" class="wend {cls}"/>')
    def resistor(cls, a, b, label):
        (xa, ya_), (xb, yb) = pt(*a), pt(*b)
        mx, my = (xa + xb) / 2, (ya_ + yb) / 2
        horiz = abs(ya_ - yb) < 0.1
        w, h = (18, 7) if horiz else (7, 18)
        s = (f'<line x1="{xa:.1f}" y1="{ya_:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" class="lead"/>'
             f'<rect x="{mx - w / 2:.1f}" y="{my - h / 2:.1f}" width="{w}" height="{h}" rx="2" class="res"/>')
        s += t(mx + (12 if horiz else 9), my + (3.5 if horiz else 3.5), label, "tiny", "start")
        return s
    def cap(kind, a, b, label):
        (xa, ya_), (xb, yb) = pt(*a), pt(*b)
        mx, my = (xa + xb) / 2, (ya_ + yb) / 2
        s = f'<line x1="{xa:.1f}" y1="{ya_:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" class="lead"/>'
        if kind == "el":
            s += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="6" class="cel"/><line x1="{mx - 2.5:.1f}" y1="{my - 5:.1f}" x2="{mx - 2.5:.1f}" y2="{my + 5:.1f}" class="stripe"/>'
        else:
            s += f'<rect x="{mx - 4:.1f}" y="{my - 5:.1f}" width="8" height="10" rx="1.5" class="ccer"/>'
        s += t(mx + 9, my + 3.5, label, "tiny", "start")
        return s
    ytr = lambda k: rows_top["e"] + P * (0.9 + 0.45 * k)         # three lanes in the trench, k = 1..3 → inside the trench band
    yab = lambda k: rows_top["a"] - P * (0.55 + 0.35 * k)         # lanes between row a and the blue rail
    ybl = lambda k: rows_bot["j"] + P * (0.5 + 0.35 * k)          # lanes between row j and the bottom blue rail
    W = []
    # power
    W.append(wire("w5v", [(1, "b"), (1, "R1")]))                                     # RAW → top red rail
    W.append(wire("wgnd", [(2, "a"), (2, "R2")]))                                    # G → top blue rail
    W.append(wire("wgnd", [(3, "h"), (3, "R3")]))                                    # GND (bottom edge) → bottom blue rail
    W.append(wire("w3v", [(4, "b"), (4, "R4")], via=[(col(4), yab(1)), (bx0 + 10, yab(1)), (bx0 + 10, yR4)]))   # 3V around the board's end to the bottom red rail
    W.append(wire("w5v", [(31, "R1"), (32, "R1")])); W.append(wire("wgnd", [(31, "R2"), (32, "R2")]))             # rail split bridges, top pair
    # OLED
    W.append(wire("wgnd", [(15, "i"), (15, "R3")])); W.append(wire("w3v", [(16, "i"), (16, "R4")]))
    W.append(cap("el", (15, "h"), (16, "h"), "220 µF"))
    W.append(wire("wspi", [(18, "f"), (12, "h")], via=[(col(18), rows_bot["f"] + 0.5 * P), (col(13) + 4, rows_bot["f"] + 0.5 * P), (col(13) + 4, rows_bot["h"])]))      # DC → D9
    W.append(wire("wspi", [(30, "f"), (11, "i")], via=[(col(30), rows_bot["f"] + 0.3 * P), (col(13) + 8, rows_bot["f"] + 0.3 * P), (col(13) + 8, rows_bot["i"])]))      # RST → D8
    W.append(wire("wspi", [(21, "f"), (9, "a")], via=[(col(21), ytr(1)), (col(13) + 1, ytr(1)), (col(13) + 1, yab(1)), (col(9), yab(1))]))                             # D0 clock → CLK
    W.append(wire("wspi", [(22, "f"), (11, "a")], via=[(col(22), ytr(2)), (col(13) + 5, ytr(2)), (col(13) + 5, yab(2)), (col(11), yab(2))]))                           # D1 data → MOSI
    W.append(wire("wspi", [(29, "f"), (12, "a")], via=[(col(29), ytr(3)), (col(13) + 9, ytr(3)), (col(13) + 9, yab(3)), (col(12), yab(3))]))                           # CS → D10
    # amp
    W.append(wire("w5v", [(44, "c"), (44, "R1")]))                                                   # VIN → top red rail (RAW)
    W.append(wire("wgnd", [(43, "b"), (43, "R2")]))                                                  # GND → top blue rail
    W.append(wire("wi2s", [(41, "b"), (44, "b")]))                                                   # GAIN strap to VIN = 6 dB
    W.append(resistor("wgnd", (42, "c"), (43, "c"), "10 kΩ"))
    W.append(cap("cer", (43, "d"), (44, "d"), "100 nF")); W.append(cap("el", (43, "e"), (44, "e"), "220 µF"))
    for n, c, r, k in (("BCLK", 5, "j", 3), ("LRC", 6, "i", 2), ("DIN", 7, "h", 1), ("SD", 8, "h", 1)):
        yl = ybl(k) if r == "j" else rows_bot[r] + (3 if n == "SD" else -3)
        W.append(wire("wi2s", [(38 + AMP_PINS.index(n), "e"), (c, r)], via=[(AC[n], ytr(k if k < 3 else 3) + (4 if n == "SD" else 0)), (col(13) + 12 + 3 * k, ytr(k if k < 3 else 3) + (4 if n == "SD" else 0)), (col(13) + 12 + 3 * k, yl), (col(c), yl)]))
    # switches: flying leads
    W.append(wire("wsw", [(8, "a"), (8, "R2")], via=[(col(8), yab(2)), (col(8) + 0.4 * P, yab(2)), (col(8) + 0.4 * P, yR2)]))   # snooze: A0 and GND rail
    W.append(wire("wsw", [(7, "a"), (7, "R2")], via=[(col(7), yab(3)), (col(7) - 0.4 * P, yab(3)), (col(7) - 0.4 * P, yR2)]))   # arm: A1 and GND rail
    o += W
    o.append(t(col(8) + 4, yab(3) - 9, "snooze → A0, arm → A1, other leg to the GND rail", "fn"))
    # ---- the QT chain, to the right, and its two wires back to D6 / D7
    CX, CW, CH = 1052, 170, 44
    chain = [("rotary encoder", "I²C 0x49"), ("real-time clock", "I²C 0x68 · SQW pad"), ("proximity + light", "I²C 0x60"), ("accelerometer", "I²C 0x18"), ("temp / humidity", "I²C 0x38")]
    ys = [yR1 - 52 + i * (CH + 14) for i in range(5)]
    BX = CX - 24
    o.append(f'<path d="M{BX},{ys[0] + CH / 2} L{BX},{ys[-1] + CH / 2}" class="bus"/>')
    for (name, sub), y in zip(chain, ys):
        o.append(f'<rect x="{CX}" y="{y}" width="{CW}" height="{CH}" rx="6" class="part"/>')
        o.append(t(CX + 10, y + 18, name, "pinlab")); o.append(t(CX + 10, y + 34, sub, "fn"))
        o.append(f'<path d="M{BX},{y + CH / 2} L{CX},{y + CH / 2}" class="bus"/>'); o.append(dot(BX, y + CH / 2, 4.5))
    # first QT cable: socket → bus
    qy = (yc + yg) / 2
    qx = col(14) + 0.5 * P; qyy = yR1 - 30
    o.append(f'<path d="M{kx1 + 8:.1f},{qy:.1f} L{qx:.1f},{qy:.1f} L{qx:.1f},{qyy:.1f} L{BX},{qyy:.1f}" class="bus"/>')
    o.append(dot(BX, qyy, 4.5))
    o.append(t(qx + 10, qyy - 8, "first QT cable, straight from the socket", "fn"))
    o.append(t(CX, ys[-1] + CH + 20, "STEMMA QT chain beside the breadboard,", "fn")); o.append(t(CX, ys[-1] + CH + 35, "one 100 mm QT cable per hop, no wires", "fn"))
    # SQW → D6 (col 9 h) with 10 kΩ to the bottom red rail (3 V); INT → D7 (col 10 h)
    sqy = ys[1] + CH / 2; inty = ys[0] + CH / 2
    o.append(f'<path d="M{CX + CW},{sqy} L{CX + CW + 20},{sqy} L{CX + CW + 20},{yR4 + 84} L{col(9) + 0.3 * P:.1f},{yR4 + 84} L{col(9) + 0.3 * P:.1f},{rows_bot["j"] + 0.6 * P:.1f} L{col(9):.1f},{rows_bot["j"] + 0.6 * P:.1f} L{col(9):.1f},{rows_bot["h"]:.1f}" class="wire wint"/>')
    o.append(f'<circle cx="{col(9):.1f}" cy="{rows_bot["h"]:.1f}" r="3.4" class="wend wint"/>'); o.append(dot(CX + CW, sqy, 4.5))
    o.append(t(col(13), yR4 + 80, "clock SQW → D6, the alarm wire · 10 kΩ from column 9 j to the 3 V rail", "lab"))
    o.append(resistor("w3v", (9, "j"), (9, "R4"), "10 kΩ"))
    o.append(f'<path d="M{CX + CW},{inty} L{CX + CW + 36},{inty} L{CX + CW + 36},{yR4 + 96} L{col(10) + 0.3 * P:.1f},{yR4 + 96} L{col(10) + 0.3 * P:.1f},{rows_bot["j"] + 0.6 * P:.1f} L{col(10):.1f},{rows_bot["j"] + 0.6 * P:.1f} L{col(10):.1f},{rows_bot["i"]:.1f}" class="wire wint"/>')
    o.append(f'<circle cx="{col(10):.1f}" cy="{rows_bot["i"]:.1f}" r="3.4" class="wend wint"/>'); o.append(dot(CX + CW, inty, 4.5))
    o.append(t(col(13), yR4 + 110, "encoder INT → D7", "lab"))
    # legend
    ly = yR4 + 142
    for i, (cls, name) in enumerate((("w5v", "RAW 5 V (amp only)"), ("w3v", "3 V"), ("wgnd", "GND"), ("wspi", "display SPI"), ("wi2s", "amp I²S + strap"), ("wint", "alarm + encoder INT"), ("wsw", "switch leads"))):
        x = 70 + i * 128
        o.append(f'<line x1="{x}" y1="{ly}" x2="{x + 26}" y2="{ly}" class="wire {cls}"/>'); o.append(t(x + 32, ly + 4, name, "fn"))
    o.append(t(70, ly + 22, "Rails: top pair = RAW 5 V and GND, bottom pair = 3 V and GND. The 3 V rail is fed by the one wire that goes around the USB end of the stand-in.", "fn"))
    o.append(t(70, ly + 38, "The two top rails are bridged across the board's middle split. The OLED's 220 µF sits at its pins 1-2; the amp's 220 µF + 100 nF across GND-VIN.", "fn"))
    css = ("<style>"
           ".bb{fill:var(--paper);stroke:var(--line);stroke-width:1.5}.trench{fill:var(--bg)}"
           ".hole{fill:var(--line)}.rail-r{stroke:#c0392b;stroke-width:1.6;opacity:.75}.rail-b{stroke:#2c5fa8;stroke-width:1.6;opacity:.75}"
           ".railtxt{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink-2)}.railname{font:700 10px 'JetBrains Mono',monospace;fill:var(--ink)}"
           ".rowlet{font:700 9px 'JetBrains Mono',monospace;fill:var(--ink-2)}.colnum{font:400 8.5px 'JetBrains Mono',monospace;fill:var(--ink-2)}"
           ".kb{fill:var(--paper);stroke:var(--ink);stroke-width:1.6;fill-opacity:.96}.kbname{font:700 11px 'Archivo',Arial,sans-serif;fill:var(--ink-2)}"
           ".pinused{fill:var(--ink)}.pinfree{fill:var(--paper);stroke:var(--ink);stroke-width:1.2}"
           ".module{fill:var(--paper);stroke:var(--ink-2);stroke-width:1.3;stroke-dasharray:5 4}"
           ".usb{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.2}.cable{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.4}"
           ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}.bus{fill:none;stroke:var(--brass);stroke-width:4.5;stroke-linecap:round;stroke-linejoin:round}.joint{fill:var(--ink)}"
           ".wire{fill:none;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}.wend{stroke:var(--paper);stroke-width:1.2}"
           ".w5v{stroke:#e67e22}.w3v{stroke:#c0392b}.wgnd{stroke:#3a3f47}.wspi{stroke:#0E5F7A}.wi2s{stroke:#2A6340}.wint{stroke:#7d3c98}.wsw{stroke:#8F6114}"
           ".wend.w5v{fill:#e67e22}.wend.w3v{fill:#c0392b}.wend.wgnd{fill:#3a3f47}.wend.wspi{fill:#0E5F7A}.wend.wi2s{fill:#2A6340}.wend.wint{fill:#7d3c98}.wend.wsw{fill:#8F6114}"
           ".lead{stroke:var(--ink);stroke-width:1.6}.res{fill:#e8dcc4;stroke:var(--ink);stroke-width:1.2}.cel{fill:#2c4a7a;stroke:var(--ink);stroke-width:1}.stripe{stroke:#fff;stroke-width:1.5}.ccer{fill:#d9b36b;stroke:var(--ink);stroke-width:1}"
           ".spk{fill:none;stroke:var(--ink);stroke-width:2.2}"
           ".h1{font:900 22px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}.sub{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".fn{font:400 11px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}.lab{font:700 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".pinlab{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink)}.tiny{font:700 8.5px 'JetBrains Mono',monospace;fill:var(--ink)}"
           "</style>")
    return f'<svg viewBox="0 0 1360 {ly + 52:.0f}" role="img" aria-label="Cyber Dawn stand-in wiring on an 830-point breadboard">{css}{"".join(o)}</svg>'


BREADBOARD_HTML = """
<h2 id="breadboard">The same wiring on a breadboard</h2>
<p><strong>What.</strong> One of the owned 830-point breadboards carries the whole test. The stand-in's two pin rows are 0.6 inch apart, so it straddles the trench: top-edge pins (RAW, G, RST, 3V, A3 to A0, CLK, MISO, MOSI, D10) in row <code>c</code>, bottom-edge pins (D0, D1, GND, GND, D2 to D9) in row <code>g</code>, columns 1 to 12, USB-C hanging off the left end. Holes <code>a</code>-<code>b</code> above it and <code>h</code>-<code>j</code> below it stay free for wires. The OLED module's <strong>20-pin</strong> header goes into row <code>j</code>, columns 15 to 34, the module standing up off the bottom edge; the amp's 7-pin header into row <code>a</code>, columns 38 to 44, standing up off the top edge. The five QT boards never touch the breadboard: the first QT cable leaves the stand-in's socket and the chain lies beside the board.</p>
<p><strong>Rails.</strong> Top pair: RAW 5 V (red, fed from column 1) and GND (blue, from column 2). Bottom pair: GND (blue, from the bottom-edge GND in column 3) and 3 V (red). The 3 V rail is the one awkward wire: 3V is a top-edge pin, so its jumper leaves column 4 and goes around the USB end of the stand-in to the bottom red rail. The owned boards ship with the rails split at the middle; the two top rails are used on both sides of the split, so bridge each with a short jumper at columns 31-32. The bottom rails are only used left of the split.</p>
<p><strong>Order of work</strong>, so the meter checks below stay meaningful: (1) stand-in in, nothing else, power it, see CIRCUITPY; (2) the three rail feeds and the two split bridges, meter 3 V and 5 V against GND; (3) the chain by QT cable, scan; (4) OLED header, its 220 µF, two power wires, five signal wires; (5) amp header, its 10 kΩ, two capacitors, GAIN strap, two power wires, four signal wires; (6) the SQW wire and its 10 kΩ, the INT wire; (7) the two switches on flying leads. Column numbers in the drawing are the ones printed on the board.</p>
<figure class="sheet bbfig">%s<figcaption><strong>Page 2 of the PDF, landscape.</strong> A small square is a header pin (filled = used). A dot is where a wire end goes into a hole; the path between two dots is a plan, not the wire's real shape. Colours are jobs, not wire colours in the kit. Pin numbers under the OLED header are the module's own 1 to 20.</figcaption></figure>
<div class="note tip"><span class="lbl">Two facts that decide this drawing</span>
<p><strong>The OLED header is 20 pins, not 7.</strong> Adafruit's guide for the 1.5"/2.4" 128×64 module family numbers them 1 to 20 from the left: 1 ground, 2 3 V in, 4 DC, 7 Data0 (the SPI clock), 8 Data1 (the SPI data), 15 CS, 16 RESET; 5-6 and 9-14 are the parallel-bus pins, never connected in SPI; 20 is the frame ground. The module may ship in 8-bit mode; the solder-jumper photo decides whether it is already SPI. If it is not, the Day 0 plan says stop, and the display waits for the controller board.</p>
<p><strong>The stand-in's fuse.</strong> RAW is USB 5 V after a 500 mA fuse. The amp alone can pull 0.9 A peaks at 6 dB into 4 Ω, so keep the test tone quiet and expect the fuse, not a wiring fault, if sound cuts out after a loud passage.</p>
</div>
"""


# ----------------------------------------------------------------------------- the notes
def a(word, key):
    return f'<a href="{LINK[key]}" target="_blank" rel="noopener">{word}</a>'


def pinmap_html():
    o = ['<div class="tw"><table><tr><th>Job</th><th>Stand-in pin</th><th>GPIO</th><th>CircuitPython</th><th>Controller board, later</th><th>Note</th></tr>']
    for job, silk, g, cp, later, note in PINMAP:
        o.append(f'<tr><td>{esc(job)}</td><td class="m">{esc(silk)}</td><td class="m">{"" if g is None else g}</td><td class="m">{esc(cp)}</td><td class="m">{esc(later)}</td><td>{esc(note)}</td></tr>')
    o.append("</table></div>")
    return "".join(o)


CODE = '''import board, busio, digitalio
from digitalio import DigitalInOut, Direction, Pull

i2c = board.STEMMA_I2C()                      # the chain, through the socket

spi = busio.SPI(board.CLK, board.MOSI)        # the display, 4-wire SPI
OLED_CS, OLED_DC, OLED_RST = board.D10, board.D9, board.D8

I2S_BCLK, I2S_LRC, I2S_DIN = board.D2, board.D3, board.D4
amp_sd = DigitalInOut(board.D5); amp_sd.direction = Direction.OUTPUT; amp_sd.value = False

def input_pullup(p):
    d = DigitalInOut(p); d.direction = Direction.INPUT; d.pull = Pull.UP; return d
clock_alarm = input_pullup(board.D6)          # low when Alarm 1 fires (the 10 kΩ does the real work)
encoder_int = input_pullup(board.D7)          # low on any turn or press
snooze      = input_pullup(board.A0)          # low while pressed
armed       = input_pullup(board.A1)          # low = armed, if the switch is wired that way round
'''


def notes_html():
    return f"""
<h2>What this sheet is</h2>
<p>The {a("controller board", "controller")} is still in transit, and the {a("stand-in controller", "standin")}, the small Adafruit RP2040 board that came free with the 2026-10-19 order, has every pin the Phase 1 bench needs: a STEMMA QT socket for the chain, a hardware SPI for the {a("OLED display", "display")}, three free GPIOs in a row for the {a("amplifier", "amp")}'s I²S, and spare inputs for the clock alarm, the encoder, the {a("snooze button", "snooze")} and the {a("arm switch", "arm")}. So the whole bench clock can be built and run now, in CircuitPython, and when the controller board lands each wire moves to the pin in the table's last column. Nothing gets desoldered: the OLED header and its capacitor, the two resistors, the switch leads and the speaker lead all stay as they are.</p>
<p>This sheet extends the Day 0 plan: Day 0's chain, OLED and amp steps used exactly these pins, and this page adds the amp shutdown, the clock alarm wire, the encoder interrupt and the two switches so that the alarm itself can be tested.</p>

<div class="note warn"><span class="lbl">Three rules, unchanged</span>
<p><strong>Every logic line is 3.3 V.</strong> The display, the clock and every sensor run from the stand-in's 3V pin or its QT socket. RAW is 5 V and goes to the amplifier VIN and nowhere else.</p>
<p><strong>One power source: the USB-C cable.</strong> There is no battery and no charger board on this sheet. Use a data cable (a charge-only cable gives no CIRCUITPY drive).</p>
<p><strong>The amplifier's outputs are a bridge.</strong> OUT+ and OUT− are never ground, never a scope clip, never brass.</p>
</div>

<h2>The pin map</h2>
{pinmap_html()}
<p>Declared in code, this is the top of <code>code.py</code>:</p>
<pre><code>{esc(CODE)}</code></pre>

<h2>1 · The chain: one cable into the socket</h2>
<p>The {a("QT-to-header cable", "qt_header")} stays in the bag. The first 100 mm {a("QT cable", "qt_cable")} plugs into the stand-in's socket (SDA GPIO12, SCL GPIO13) and the five boards chain from there in any order; the sheet keeps the Day 0 order so the scan list matches: {a("rotary encoder", "encoder")} 0x49, {a("real-time clock", "clock")} 0x68, {a("proximity and light sensor", "proximity")} 0x60, {a("accelerometer", "accel")} 0x18, {a("temperature and humidity sensor", "climate")} 0x38. The fuel gauge is a Phase 4 part and is not on the bench; five boards plus the display is also the comfortable limit of the stand-in's 500 mA regulator.</p>

<h2>2 · The display: the Day 0 wiring, kept</h2>
<p>VCC to 3V, GND to GND, then CLK, MOSI, D10 for chip select, D9 for data/command, D8 for reset. The kit's 220 µF sits across VCC and GND at the module and the level shifter stays in the bag. CLK and MOSI are the hardware SPI0 pins, so <code>busio.SPI(board.CLK, board.MOSI)</code> is the fast path. Photograph the BS1/BS2 jumpers before soldering the header, as the Day 0 plan says.</p>

<h2>3 · Audio: four wires, RAW, and a fuse to respect</h2>
<p>BCLK on D2, LRC on D3, DIN on D4, SD on D5 with 10 kΩ to ground at the amp; GAIN strapped to VIN for the 6 dB ceiling; VIN from RAW; 220 µF and 100 nF across VIN and GND at the amp's pins. The RP2040 makes I²S with a PIO program and CircuitPython's <code>audiobusio.I2SOut</code> requires the word-select pin to be the GPIO right after the bit-clock pin, which is why D2 and D3 are fixed and D4 is the data.</p>
<p><strong>The fuse.</strong> RAW is USB 5 V after the stand-in's 500 mA polyfuse and its protection diode. The amplifier at 6 dB into 4 Ω peaks near 0.9 A, which is why the controller board's design uses a 2 A adapter. On the stand-in keep the volume at bench level (the Day 0 tone at 6000 of 32767 is right) and treat a sudden silence after a loud passage as the fuse resetting, not a fault. There is a jumper on the back of the board that bypasses the fuse for 2 A; leave it alone, the full-volume alarm test belongs on the controller board.</p>

<h2>4 · The alarm wire, the encoder, and the two switches</h2>
<p><strong>Clock SQW to D6 with 10 kΩ to 3V.</strong> The clock pulls the line low when Alarm 1 matches. The output is open-drain, so without the resistor the line floats and the alarm never fires: that resistor is the whole test. On the stand-in any GPIO can wake CircuitPython from light or deep sleep with <code>alarm.pin.PinAlarm(board.D6, value=False)</code>, so the deep-sleep wake test can be run here too.</p>
<p><strong>Encoder INT to D7</strong>, pulled up in code; it pulses low on any turn or press so the loop can skip polling. <strong>Snooze on A0, arm on A1</strong>, each other leg to GND, both pulled up in code. A0 to A3 are the ADC-capable pins, but as plain digital inputs they are no different from the D pins, and using them keeps D0/D1 free for a serial probe.</p>

<h2>What the stand-in cannot do</h2>
<ul class="check">
<li>Run the ESP-IDF firmware in <code>firmware/</code>: it is an ESP32-S3 program. The stand-in runs CircuitPython, so what gets proven here is the hardware and the alarm logic, not the firmware.</li>
<li>Full alarm volume: the 500 mA fuse on RAW, above.</li>
<li>Wi-Fi: no radio. Time is set from the console and kept by the clock's coin cell.</li>
<li>Feed a sixth QT board or anything else from 3V: the regulator is rated 500 mA peak and the display, the chain and the chip already use a share of it.</li>
</ul>

<h2>Before power, with the meter</h2>
<ul class="check">
<li>3V to GND and RAW to GND: no steady beep. A chirp that stops is a capacitor.</li>
<li>OUT+ and OUT− to GND and to each other: silent, or a few ohms through the speaker only.</li>
<li>Clock SQW to 3V: about 10 kΩ. Open means the pull-up is missing and the alarm will never fire.</li>
<li>Amp SD to GND: about 10 kΩ. Near 1 MΩ or open means the pull-down is missing.</li>
<li>Each display signal pin to its stand-in pin: beep. Adjacent display pins to each other: silent.</li>
</ul>
"""


def style():
    src = BENCH.read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def page_html():
    return "\n".join([
        '<title>Cyber Dawn Stand-in Wiring</title>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        style(),
        '<style>figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} .wrap{max-width:1100px} pre{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:10px 14px;overflow-x:auto;font:12.5px/1.5 "JetBrains Mono",monospace}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Cyber Dawn &middot; Phase 1 on the stand-in controller</div>',
        '<h1>The bench clock on the board you already have</h1>',
        '<div class="sub">The whole Phase 1 wiring moved onto the small Adafruit RP2040 board from the 2026-10-19 order, so the alarm clock can be built and run now, before the controller board arrives. One sheet, the pin map with the pin each wire moves to later, the same wiring laid out hole by hole on an 830-point breadboard (added the evening of 2026-10-31), and the few things the stand-in cannot do.<br>Written 2026-10-31. Companion to <code>docs/DAY0_TEST.md</code> and <code>pages/cyber-dawn-wiring.html</code>.</div></div>',
        f'<figure class="sheet">{sheet()}<figcaption><strong>Print it landscape on Letter; it is page 1 of the PDF.</strong> Thick lines are wires you solder or plug, the brass line is the STEMMA QT chain, dotted is later. A dot is a joint; a hop is a crossing that does not touch. The inset at the bottom left shows where each pin sits on the board.</figcaption></figure>',
        notes_html(),
        BREADBOARD_HTML % breadboard_svg(),
        '<hr><p class="sub">Built by <code>docs/pages/gen/wiring_standin.py</code>. Pin facts from the board\'s Adafruit guide and its CircuitPython board definition, read 2026-10-31; not verified against hardware. Nothing on this page has been built.</p>',
        '</div>'])


def print_pdf(html):
    PRINT.mkdir(exist_ok=True)
    sheet_css = ("<style>@page{size:letter landscape;margin:7mm} html,body{background:#fff;margin:0}"
                 ":root{--paper:#fff;--ink:#000;--ink-2:#333;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#eee}"
                 "svg{width:262mm;height:auto;display:block;margin:0 auto}</style>")
    page_css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
                "figure.sheet{display:none} h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
                "pre{font-size:8.5pt;break-inside:avoid} .note{margin:10pt 0;padding:8pt 10pt} .note p{margin:3pt 0} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt}"
                "tr{break-inside:avoid} ul.check{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        s_html = pathlib.Path(d) / "s.html"; s_pdf = pathlib.Path(d) / "s.pdf"
        p_html = pathlib.Path(d) / "p.html"; p_pdf = pathlib.Path(d) / "p.pdf"
        s_html.write_text("<!doctype html><meta charset=utf-8><title>sheet</title>" + sheet_css + sheet() + '<div style="break-before:page"></div>' + breadboard_svg())
        p_html.write_text("<!doctype html><meta charset=utf-8>" + html.replace("</style>", "</style>" + page_css, 1))
        for src, pdf in ((s_html, s_pdf), (p_html, p_pdf)):
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "cyber-dawn-standin-wiring.pdf"
        subprocess.run(["pdfunite", str(s_pdf), str(p_pdf), str(out)], check=True)
        shutil.copyfile(s_pdf, PRINT / "cyber-dawn-standin-wiring-sheet.pdf")
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


def main():
    audit()
    html = page_html()
    OUT.write_text(html)
    print("wrote", OUT, OUT.stat().st_size)
    print_pdf(html)


if __name__ == "__main__":
    main()
