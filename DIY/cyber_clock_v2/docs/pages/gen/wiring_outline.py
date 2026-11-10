"""Builds docs/pages/cyber-dawn-wiring.html and docs/pages/print/cyber-dawn-wiring.pdf:
the Phase 1 bench wiring of Cyber Dawn on one landscape sheet (the sunrise lamp added 2026-11-05), a 3-page outline of every
connection and why, and the Rev B parts list (2026-10-31: solar removed, compact body, one 16340 cell; the
order sheet was first verified 2026-10-19 and updated 2026-10-26, 2026-10-28 and 2026-10-31).
Naming rule (2026-10-30): component types, never product codes or chip names, with the link on the
component word; order codes live only in the order sheet's own column.

Sources: docs/ARCHITECTURE.md (buses, boot order), docs/WIRING_CROSSREF.md (findings 1-6, the
connection table), docs/REVIEW.md (decided pin map, 6 dB gain, the QT-to-header cable), docs/COMPACT_DESIGN.md (Rev B),
firmware/main/include/board_pins.h, and the vendor pages fetched on 2026-10-19.
Style is copied from cyber-dawn-bench.html so the pages match."""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
OUT = PAGES / "cyber-dawn-wiring.html"
PRINT = PAGES / "print"
BENCH = PAGES / "cyber-dawn-bench.html"

# the hop-drawing router from the Pocket AI wiring sheet
sys.path.insert(0, str(HERE.parent.parent.parent.parent / "pocket_ai_assistant" / "edu" / "pages" / "gen"))
from wiring_sheet import Router  # noqa: E402

W, H = 1360, 860


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, cls="s", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def dot(x, y, r=6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="joint"/>'


def block(x, y, w, h, title, sub=None, cls="part"):
    tcls = "lab" if cls == "later" else "title"
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>', T(x + w / 2, y + 24, title, tcls, "middle")]
    if sub:
        o.append(T(x + w / 2, y + 42, sub, "sub", "middle"))
    return "".join(o)


def pin(x, y, name, side, fn=None, fnx=None):
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
    """A ground symbol hanging below (x, y)."""
    return (f'<path d="M{x},{y} L{x},{y+12} M{x-11},{y+12} L{x+11},{y+12} M{x-7},{y+17} L{x+7},{y+17} M{x-3},{y+22} L{x+3},{y+22}" class="thin"/>')


def flag(x, y, label):
    """A power flag above (x, y)."""
    return f'<path d="M{x},{y} L{x},{y-12} M{x-9},{y-12} L{x+9},{y-12}" class="thin"/>' + T(x, y - 17, label, "lab", "middle")


def zigzag(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2
    z = 9
    pts = [(x, y0), (x, mid - 16)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        pts.append((x + dx, mid - 16 + (i + 0.5) * (32 / 6)))
    pts += [(x, mid + 16), (x, y1)]
    return rt.wire(pts, "thin", net)


def hzigzag(rt, y, x0, x1, net):
    """A resistor lying along a horizontal wire from x0 to x1."""
    mid = (x0 + x1) / 2
    z = 9
    pts = [(x0, y), (mid - 16, y)]
    for i, dy in enumerate((z, -z, z, -z, z, -z)):
        pts.append((mid - 16 + (i + 0.5) * (32 / 6), y + dy))
    pts += [(mid + 16, y), (x1, y)]
    return rt.wire(pts, "thin", net)


def capacitor(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2
    return "".join([rt.wire([(x, y0), (x, mid - 5)], "thin", net), rt.wire([(x, mid + 5), (x, y1)], "thin", net),
                    f'<line x1="{x-12}" y1="{mid-5}" x2="{x+12}" y2="{mid-5}" class="thin"/>',
                    f'<line x1="{x-12}" y1="{mid+5}" x2="{x+12}" y2="{mid+5}" class="thin"/>', dot(x, y0), dot(x, y1)])


def sheet():
    rt = Router()
    w = rt.wire
    o = [T(20, 30, "Cyber Dawn, Phase 1 bench: every connection on one sheet", "h1"),
         T(20, 48, "A dot is a joint. A line that hops over another does not touch it. Thick = wire you solder or plug. Brass = the STEMMA QT chain. Dotted = later phase. Ground symbols all mean the controller's GND pins.", "sub")]

    # ---------------------------------------------------------------- controller board, centre
    DX, DY, DW, DH = 560, 110, 280, 500
    o.append(block(DX, DY, DW, DH, "Controller board", "pins grouped by job, not by header position"))
    L = {}
    for name, y, fn in (("3V3", 190, "3.3 V out"), ("GND", 220, ""), ("GPIO12", 260, "SCLK"), ("GPIO11", 290, "MOSI"),
                        ("GPIO10", 320, "CS"), ("GPIO6", 350, "DC"), ("GPIO7", 380, "RESET"), ("GPIO40", 508, "lamp")):
        L[name] = (DX, y); o.append(pin(DX, y, name, "L", fn, DX + 80))
    R = {}
    for name, y, fn in (("GPIO4", 170, "clock alarm"), ("GPIO1", 200, "encoder INT"), ("GPIO5", 230, "accel INT, later"),
                        ("3V3", 300, ""), ("GND", 330, ""), ("GPIO8", 360, "SDA"), ("GPIO9", 390, "SCL"), ("5V", 412, "USB 5 V"),
                        ("GPIO14", 440, "BCLK"), ("GPIO15", 470, "LRC"), ("GPIO16", 500, "DIN"), ("GPIO17", 530, "amp SD")):
        R[name] = (DX + DW, y); o.append(pin(DX + DW, y, name, "R", fn, DX + DW - 70))
    B = {}
    for name, x in (("GPIO18", 600), ("GND", 650), ("GPIO21", 730)):
        B[name] = (x, DY + DH); o.append(pin(x, DY + DH, name, "B"))
    o.append(f'<rect x="{DX+8}" y="{DY+DH-22}" width="34" height="14" rx="3" class="usb"/>'); o.append(T(DX + 25, DY + DH - 11, "USB", "fn", "middle"))
    # Phase 4 source, above the controller, dotted
    o.append(block(250, 58, 590, 40, "Phase 4, later: charger board 5 V out, one 16340 cell → 5V pin · USB socket empty", None, "later"))
    o.append(w([(DX + DW / 2, 98), (DX + DW / 2, DY)], "opt", "LATER"))

    # ---------------------------------------------------------------- OLED, left
    OX, OY, OW, OH = 60, 110, 300, 310
    o.append(block(OX, OY, OW, OH, "2.42\" OLED display", "3.3 V only · SPI needs links R2→R3, R4→R5"))
    P = {}
    # header pin numbers (2026-11-04): the module's 20-pin header is marked by number, not by name
    for name, num, y in (("VCC", 2, 190), ("GND", 1, 220), ("SCLK", 7, 260), ("MOSI", 8, 290), ("CS", 15, 320), ("DC", 4, 350), ("RST", 16, 380)):
        P[name] = (OX + OW, y); o.append(pin(OX + OW, y, name, "R", f"pin {num}", OX + OW - 62))
    o.append(T(OX + 16, 398, "empty: 3, 5, 6, 9–14, 17–19 · 20 may float", "fn"))
    o.append(T(OX + 16, 412, "level shifter from the kit: not used", "fn"))
    o.append(w([L["3V3"], P["VCC"]], "rod", "3V3")); o.append(T(500, 182, "3V3", "lab", "middle"))
    o.append(w([L["GND"], P["GND"]], "rod", "GND")); o.append(T(500, 212, "GND", "lab", "middle"))
    for a, b, lab in (("GPIO12", "SCLK", "clock"), ("GPIO11", "MOSI", "data out"), ("GPIO10", "CS", "chip select"), ("GPIO6", "DC", "data / command"), ("GPIO7", "RST", "reset")):
        o.append(w([L[a], P[b]], "rod", a)); o.append(T(500, L[a][1] - 8, lab, "lab", "middle"))
    o.append(capacitor(rt, 400, 190, 220, "C_OLED")); o.append(T(400, 240, "220 µF, from the kit", "fn", "middle"))

    # ---------------------------------------------------------------- sunrise lamp, below the OLED (added 2026-11-05)
    o.append(block(100, 480, 160, 56, "LED filament", "2200 K · in the lid"))
    o.append(pin(100, 508, "+", "L")); o.append(pin(260, 508, "−", "R"))
    o.append(w([(100, 508), (70, 508)], "rod", "LAMPV")); o.append(zigzag(rt, 70, 508, 456, "LAMPV")); o.append(flag(70, 456, "cell +"))
    o.append(T(82, 474, "15 Ω", "lab"))
    o.append(T(100, 556, "cell + is spliced into the holder's lead (Phase 4)", "fn"))
    o.append(T(100, 570, "bench, before the cell: 5V pin through 33 Ω", "fn"))
    o.append(block(310, 478, 120, 60, "MOSFET"))
    o.append(pin(310, 508, "D", "L")); o.append(pin(430, 508, "G", "R")); o.append(f'<circle cx="370" cy="538" r="4.5" class="pinend"/>'); o.append(T(370, 532, "S", "pin", "middle"))
    o.append(w([(260, 508), (310, 508)], "rod", "LAMPK"))
    o.append(w([(370, 538), (370, 552)], "rod", "GND")); o.append(gnd(370, 552))
    o.append(w([(430, 508), (450, 508)], "rod", "GATE")); o.append(hzigzag(rt, 508, 450, 500, "GATE")); o.append(T(475, 490, "100 Ω", "lab", "middle"))
    o.append(w([(500, 508), L["GPIO40"]], "rod", "GATE")); o.append(dot(520, 508))
    o.append(zigzag(rt, 520, 508, 556, "GATE")); o.append(gnd(520, 556)); o.append(T(510, 538, "10 kΩ", "lab", "end"))
    o.append(T(100, 584, "sunrise: PWM on GPIO40 · the 10 kΩ keeps it off at boot", "fn"))

    # ---------------------------------------------------------------- snooze, arm, USB power, bottom
    o.append(block(560, 660, 80, 60, "Snooze", "16 mm push")); o.append(block(690, 660, 80, 60, "Arm", "slide"))
    o.append(w([B["GPIO18"], (600, 660)], "rod", "SNZ")); o.append(w([(630, 660), (630, 640), (650, 640)], "rod", "GND"))
    o.append(w([B["GPIO21"], (730, 660)], "rod", "ARM")); o.append(w([(700, 660), (700, 640), (650, 640)], "rod", "GND"))
    o.append(w([B["GND"], (650, 640)], "rod", "GND")); o.append(dot(650, 640))
    o.append(T(560, 737, "active-low: the controller's internal pull-ups hold them high", "fn"))
    o.append(block(370, 660, 170, 60, "USB-C wall adapter", "2 A, from Day 4"))
    o.append(w([(455, 660), (455, 630), (DX + 25, 630), (DX + 25, DY + DH - 8)], "thin", "USB"))

    # ---------------------------------------------------------------- I2C column, right
    CX, CW, CH = 1010, 170, 48
    chain = [("rotary encoder", "0x49"), ("real-time clock", "0x68"), ("fuel gauge", "0x36, Phase 4"),
             ("proximity + light", "0x60"), ("accelerometer", "0x18/19"), ("temp / humidity", "0x38")]
    ys = [116, 186, 256, 326, 396, 466]
    for (name, addr), y in zip(chain, ys):
        cls = "later" if "Phase 4" in addr else "part"
        o.append(f'<rect x="{CX}" y="{y}" width="{CW}" height="{CH}" rx="7" class="{cls}"/>')
        o.append(T(CX + 10, y + 19, name, "pinlab")); o.append(T(CX + 10, y + 37, "I²C " + addr, "fn"))
    BX = 988
    o.append(w([(BX, ys[0] + CH / 2), (BX, ys[-1] + CH / 2)], "bus", "I2C"))
    for y in ys:
        o.append(w([(BX, y + CH / 2), (CX, y + CH / 2)], "bus", "I2C")); o.append(dot(BX, y + CH / 2, 5))
    # the chain caption in two runs, above and below the stub that joins the cable box to the bus at y=345
    o.append(T(971, 232, "STEMMA QT chain · 4 wires", "fn", "middle", 'transform="rotate(-90 971 232)"'))
    o.append(T(971, 430, "one QT cable per hop", "fn", "middle", 'transform="rotate(-90 971 430)"'))
    # controller to the chain: four wires into the QT-to-header cable
    o.append(f'<rect x="905" y="282" width="56" height="124" rx="6" class="cable"/>')
    o.append(T(933, 320, "QT to", "pinlab", "middle")); o.append(T(933, 336, "header", "fn", "middle")); o.append(T(933, 350, "cable", "fn", "middle"))
    for name, lab in (("3V3", "red"), ("GND", "black"), ("GPIO8", "blue"), ("GPIO9", "yellow")):
        o.append(w([R[name], (905, R[name][1])], "rod", name)); o.append(T(872, R[name][1] - 6, lab, "fn", "middle"))
    o.append(w([(961, 345), (BX, 345)], "bus", "I2C")); o.append(dot(BX, 345))
    # the two interrupt wires, over the top
    o.append(w([R["GPIO4"], (850, 170), (850, 84), (1215, 84), (1215, ys[1] + CH / 2), (CX + CW, ys[1] + CH / 2)], "rod", "RTCINT"))
    o.append(dot(CX + CW, ys[1] + CH / 2)); o.append(T(CX + CW - 8, ys[1] + CH / 2 + 4, "SQW", "pinlab", "end"))
    o.append(T(862, 62, "clock SQW → GPIO4: the alarm wire", "lab")); o.append(T(862, 76, "open-drain, so the 10 kΩ pull-up is mandatory", "fn"))
    o.append(zigzag(rt, 1190, 84, 36, "RTCINT")); o.append(dot(1190, 84)); o.append(flag(1190, 36, "3V3")); o.append(T(1200, 62, "10 kΩ", "lab"))
    o.append(w([R["GPIO1"], (860, 200), (860, 96), (1150, 96), (1150, ys[0])], "rod", "ANOINT")); o.append(dot(1150, ys[0]))
    o.append(T(1156, 108, "INT", "pinlab")); o.append(T(868, 110, "encoder INT → GPIO1 · internal pull-up in firmware", "fn"))
    o.append(T(DX + DW + 8, 246, "wired in Phase 3", "fn"))

    # ---------------------------------------------------------------- amplifier and speaker, bottom right
    AX, AY, AW, AH = 1010, 580, 170, 210
    o.append(f'<rect x="{AX}" y="{AY}" width="{AW}" height="{AH}" rx="9" class="part"/>')
    o.append(T(AX + 62, AY + 52, "Amplifier", "title", "middle")); o.append(T(AX + 62, AY + 70, "owned HiLetgo", "sub", "middle"))
    A = {"VIN": (1060, AY), "GND": (1130, AY)}
    for name, x in (("VIN", 1060), ("GND", 1130)):
        o.append(f'<circle cx="{x}" cy="{AY}" r="4.5" class="pinend"/>'); o.append(T(x, AY + 18, name, "pin", "middle"))
    for name, y, fn in (("BCLK", 670, "bit clock"), ("LRC", 700, "word clock"), ("DIN", 730, "audio in"), ("SD", 760, "shutdown")):
        A[name] = (AX, y); o.append(pin(AX, y, name, "L", fn, AX + 58))
    for name, y in (("OUT+", 620), ("OUT−", 650), ("GAIN", 740)):
        A[name] = (AX + AW, y); o.append(pin(AX + AW, y, name, "R"))
    o.append(block(1230, 590, 110, 100, "Speaker", "4 Ω 3 W, sealed"))
    o.append(w([A["OUT+"], (1230, 620)], "rod", "OUT+")); o.append(w([A["OUT−"], (1230, 650)], "rod", "OUT-"))
    o.append(T(1285, 680, "never to ground", "fn", "middle"))
    o.append(w([A["GAIN"], (1210, 740), (1210, 718)], "thin", "GAINSTRAP")); o.append(flag(1210, 718, "VIN")); o.append(T(1218, 756, "strap = 6 dB", "fn"))
    # 5 V to the amp (the 5V pin sits just above the audio pins, so its rod runs below the cable box), and the capacitors between VIN and GND above the block
    o.append(w([R["5V"], (950, 412), (950, 550), (1060, 550), A["VIN"]], "rod", "5V")); o.append(dot(1060, 550))
    o.append(T(956, 544, "5 V", "lab"))
    o.append(w([A["GND"], (1130, 550), (1160, 550)], "rod", "GND")); o.append(dot(1130, 550)); o.append(gnd(1160, 550))
    o.append(f'<line x1="1090" y1="538" x2="1090" y2="562" class="thin"/><line x1="1100" y1="538" x2="1100" y2="562" class="thin"/>')
    o.append(w([(1060, 550), (1090, 550)], "thin", "5V")); o.append(w([(1100, 550), (1130, 550)], "thin", "GND"))
    o.append(T(1095, 530, "220 µF + 100 nF, at the pins", "fn", "middle"))
    # audio lanes: nested staircase, no crossings
    for name, pinname, x in (("GPIO14", "BCLK", 925), ("GPIO15", "LRC", 910), ("GPIO16", "DIN", 895), ("GPIO17", "SD", 880)):
        o.append(w([R[name], (x, R[name][1]), (x, A[pinname][1]), A[pinname]], "rod", name))
    # the amp SD pull-down
    o.append(zigzag(rt, 866, 760, 796, "SDPD")); o.append(dot(866, 760)); o.append(gnd(866, 796))
    o.append(T(854, 782, "10 kΩ: holds SD low until firmware runs", "fn", "end"))

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
           ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".lab{font:700 12.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".rod{fill:none;stroke:var(--ink);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
           ".bus{fill:none;stroke:var(--brass);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}"
           ".thin{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
           ".opt{fill:none;stroke:var(--ink-2);stroke-width:2;stroke-dasharray:3 5;stroke-linecap:round}"
           ".joint{fill:var(--ink)}"
           ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
           "</style>")
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cyber Dawn Phase 1 wiring sheet">{css}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- Rev B parts list, 2026-10-31
# Naming rule (2026-10-30): the Part cell is the component type, linked to the exact product bought. Order codes
# live only in the "Order code" column so a part can be re-bought. Prose cells may use [text](url) and **bold**;
# md_inline() renders them for the page and the Markdown passes them through unchanged.
# Rev B (2026-10-31): every part is owned. Each Why cell opens with its status: owned / owned, not used in Rev B /
# to buy / to print. The order history lives in NOTES below.
A = "https://www.adafruit.com/product/"
AMZ = "https://www.amazon.com/dp/"
LINK = {
    "controller": "https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894",
    "controller_adafruit": A + "5336",
    "mouser_controller": "https://www.mouser.com/en/ProductDetail/Espressif-Systems/ESP32-S3-DevKitC-1-N8R8?qs=7D1LtPJG0i2PiuUUKucutQ%3D%3D",
    "display": A + "2719", "clock": A + "5188", "coin": AMZ + "B0D8T4C5PK",
    "coin_single": "https://www.batteryjunction.com/products/panasonic-cr1220",
    "encoder": A + "6310", "encoder_plain": A + "377", "speaker": A + "1669", "speaker_mono": A + "3351",
    "snooze": A + "1505", "proximity": A + "4161", "accel": A + "2809", "climate": A + "4566",
    "qt_header": A + "4209", "qt_cable": A + "4210", "proto": A + "571",
    "amp": AMZ + "B0CDWXZZCH", "amp_adafruit": A + "3006", "arm": AMZ + "B09R434VJQ", "arm_adafruit": A + "805",
    "charger": A + "6106", "battery": A + "353", "battery_4400": A + "354", "battery_2500": A + "328",
    "battery_1200": AMZ + "B09G2S88Q3", "gauge": A + "5580", "gauge_amazon": AMZ + "B0BPN4DQM3",
    "charger_clone": AMZ + "B0H2BHTZBM", "usbc": A + "6069", "usbc_amazon": AMZ + "B0CFXTCTK4",
    "panel": A + "5367", "panel_voltaic": "https://voltaicsystems.com/5-watt-panel-etfe/", "jack_adapter": A + "4287",
    "jack_cable": A + "2788", "jack_terminals": A + "368", "voltaic_lead": "https://voltaicsystems.com/W045/",
    "holder": AMZ + "B0CRGK889F", "brass": AMZ + "B0F2FKLC2N",
    "filament": AMZ + "B0FR35BGYL", "mosfet": "https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089",
    "acrylic": "https://sendcutsend.com/materials/acrylic/", "petg": "https://www.printedsolid.com/collections/1-75mm-petg?page=2",
}
L = LINK

SECTIONS = [
    {"kind": "order", "head": "Rev B electronics: every line owned (Adafruit 2026-10-19, DigiKey 2026-10-28, Amazon 2026-10-26, plus the Pocket AI's stock)", "rows": [
        ("1 of 3", "controller board", L["controller"], "DigiKey 1965-ESP32-S3-DEVKITC-1-N8R8-ND", "DigiKey, ordered 2026-10-28", "$15.00",
         "**Owned, 3.** The genuine Espressif board, 8 MB flash + 8 MB octal PSRAM; the pin map assumes exactly this. One is the build's, two are spares. "
         "Check the silkscreen says v1.1. In the compact body its USB ports face the right-wall cutout, so it flashes without opening the box."),
        ("1 of 2", "2.42\" 128×64 OLED display", L["display"], "Adafruit 2719", "Adafruit, 2026-10-19", "$39.95",
         "**Owned, 2.** The face: its 72 × 43 mm module is 73 % of the 82 × 52 mm front. 3.3 V logic, 4-wire SPI. Comes with a level shifter (unused), a 220 µF and a header strip. "
         "Photograph the BS1/BS2 jumpers before touching them."),
        ("1 of 2", "real-time clock, STEMMA QT", L["clock"], "Adafruit 5188", "Adafruit, 2026-10-19", "$13.95",
         "**Owned, 2.** Temperature-compensated clock with the hardware alarm on its SQW pad. Has its own 10 kΩ I²C pull-ups, already counted in the bus budget. Stands in the rear zone, coin cell toward the rear panel."),
        ("1 of 10", "coin cell", L["coin"], "Amazon B0D8T4C5PK (PKCELL 10-pack)", "Amazon, 2026-10-26", "10-pack, price not recorded",
         f"**Owned, 10.** The clock's backup. Any 3 V coin cell of this size works; do not use a rechargeable one here. A [Panasonic single]({L['coin_single']}) is $1.05 at Battery Junction if the pack runs out."),
        ("1 of 2", "rotary encoder with I²C adapter", L["encoder"], "Adafruit 6310", "Adafruit, 2026-10-19", "$13.95",
         "**Owned, 2.** The knob, on the lid rear right with the cap outside. Pre-soldered wheel with five switches; I²C at 0x49, INT pin pulses low. If its board is wider than 25 mm the body grows 2 mm in depth."),
        ("1 of a pair", "stereo speaker pair, 4 Ω 3 W", L["speaker"], "Adafruit 1669", "Adafruit, 2026-10-19", "$7.50",
         f"**Owned, 1 pair.** One sealed 30 × 70 × 17 mm driver lies flat on the floor, cone down over the floor slot; the second is the spare. The [mono speaker]({L['speaker_mono']}) was out of stock on 2026-10-19."),
        ("1 of 2", "16 mm snooze button", L["snooze"], "Adafruit 1505", "Adafruit, 2026-10-19", "$0.95",
         "**Owned, 2.** The big button on the lid, rear row left, hit without looking. Panel-mount momentary; one leg to GPIO18, the other to GND."),
        ("1 of 2", "Adafruit proximity and light sensor", L["proximity"], "Adafruit 4161", "Adafruit, 2026-10-19", "$5.95",
         "**Owned, 2** (plus three SparkFun spares from DigiKey 2026-10-01). Under a 5 mm hole in the lid, facing up: a hand over the clock wakes the face. I²C 0x60."),
        ("1 of 2", "accelerometer", L["accel"], "Adafruit 2809", "Adafruit, 2026-10-19", "$4.95", "**Owned, 2.** Tap wake, Phase 3. I²C 0x18 or 0x19; INT to GPIO5 later. Stands in the rear zone."),
        ("1 of 5", "temperature and humidity sensor", L["climate"], "Adafruit 4566", "Adafruit, 2026-10-19 and DigiKey, 2026-10-01", "$4.50",
         "**Owned, 5.** Room climate. I²C 0x38. Stands in the rear zone behind the vent slots, away from the cell and the controller's regulator."),
        ("1 of 2", "QT-to-header cable", L["qt_header"], "Adafruit 4209", "Adafruit, 2026-10-19", "$0.95",
         "**Owned, 2.** STEMMA QT to male header: the only bridge from the controller's headers to the chain. Red 3V3, black GND, blue SDA, yellow SCL."),
        ("5 of 7", "QT cable, 100 mm", L["qt_cable"], "Adafruit 4210", "Adafruit, 2026-10-19", "$0.95 each", "**Owned, 7.** Six boards need five board-to-board hops; two spare."),
        ("1 of 3", "amplifier", L["amp"], "Amazon B0CDWXZZCH", "HiLetgo, from the Pocket AI build", "",
         f"**Owned, 3.** Same chip and pinout as the [Adafruit amplifier]({L['amp_adafruit']}) (LRC BCLK DIN GAIN SD GND VIN); the 6 dB strap and the SD behaviour are identical. Top layer, rear row centre, short leads to the speaker below."),
        ("1 of 25", "arm switch", L["arm"], "Amazon B09R434VJQ", "Chanzon, from the Pocket AI build", "",
         f"**Owned, 25.** Replaces the [Adafruit slide switch]({L['arm_adafruit']}). On the left wall, high; it carries only a logic input."),
        ("1 of 10", "LED filament, 3 V, 38 mm, 2200 K", L["filament"], "Amazon B0FR35BGYL", "Amazon, 2026-11-01 (the desk hologram's ten-pack, satellite bin)", "$9.99 the pack",
         "**Owned, 8 spare.** The sunrise lamp, added 2026-11-05: one warm line in a 40 × 2 mm slot along the lid's front edge. Fed from the cell + through 15 Ω, about 0.1 A at most. "
         "Both leads leave one end; bend the leads, never the ceramic strip."),
        ("1 of 10", "MOSFET switch, N-channel, SOT-23", L["mosfet"], "DigiKey 5272-AO3400A-EVCT-ND", "DigiKey, 2026-10-28 (the drone order)", "$0.315",
         "**Owned, 5 spare after the drone.** Switches the lamp's − side from GPIO40: threshold 1.45 V at most, so 3.3 V turns it fully on. Tiny; solder thin wires straight to its three legs and heat-shrink it on the lead."),
        ("", "10 kΩ and other resistors, 220 µF and 100 nF capacitors", "", "", "LuminologyPro, ALLECIN and BOJACK kits", "",
         "**Owned.** The clock pull-up, the amp SD pull-down, the two capacitors at the amp, and the lamp's 15 Ω, 100 Ω and 10 kΩ (33 Ω on the bench). If the kits have no 15 Ω, two 33 Ω in parallel make 16.5 Ω."),
        ("", "Header pins, 26 and 30 AWG silicone wire, heat-shrink, Kapton, foam pad", "", "", "from the Pocket AI build", "", "**Owned.** Everything the DigiKey 'passives allowance' in the old BOM was for; the foam pad sits between the speaker and the controller."),
        ("", "Bench supply, multimeter, oscilloscope, iron, tips, flux pen, solder, wick, USB-C wall adapter 2 A", "", "", "owned", "",
         "**Owned.** The 2 A wall adapter powers the bench from Day 4 and, in Phase 4, plugs into the charger board's own USB-C port."),
    ]},
    {"kind": "order", "head": "Rev B power: one 16340 cell, every line owned", "rows": [
        ("1", "charger board with 5 V boost", L["charger"], "Adafruit 6106", "Adafruit, 2026-10-26", "$8.95",
         "**Owned.** Stands in the rear zone with its USB-C port through a cutout in the rear panel: that port is the clock's charging port. The solar/VIN input stays empty. "
         "**Cut the charge-rate jumper on the back** (closed as shipped = 1 A; cut = 500 mA, about 0.5 C on a 950 mAh cell). Its 5 V boost output feeds the controller's 5V pin and the amplifier VIN in Phase 4; the controller's USB socket is then empty. "
         "The fixed 6 h charge timer is no longer a concern: 950 mAh at 500 mA terminates in about 3 h."),
        ("1", "fuel gauge", L["gauge"], "Adafruit 5580", "Adafruit, 2026-10-26", "$5.95",
         "**Owned.** On the battery lead between the holder's pigtail and the charger board's BAT port; state of charge over I²C at 0x36. Stands beside the charger in the rear zone."),
        ("1 of 6", "16340 cell, Nitecore, 3.6 V 950 mAh, protected button-top", "", "Nitecore NL169", "owned from the Pocket AI build; date and price not recorded", "",
         "**Owned, 6.** The battery. Protected, 2 A continuous discharge limit and 4.20 V termination, so the charger board's Li-ion profile fits unchanged and the amplifier's 0.9 A peaks sit inside the cell's limit. "
         "About 3.4 Wh: roughly 10 h with the face lit at the OLED's 50 mA, many hours more with the face dark and the controller asleep. Its job is to ride through unplugs and keep the alarm armed, not to run the clock for days. "
         "Spare cells charge in the external Nitecore charger."),
        ("1 of 10", "16340 holder with leads", L["holder"], "Amazon B0CRGK889F", "Amazon, 10-pack ordered 2026-10-27 (logged in the camera Pocket AI's COMPONENTS.md)", "price not recorded",
         "**Owned, 10.** 43 × 18 × 14 mm, lying along the width in the top layer, front row right, so the lid lifts off and the cell swaps. "
         "On the bench: check the spring reaches the button top, and **meter the leads for polarity before the cell meets anything**: red must land on the + pad."),
        ("1 pair of 20", "JST-PH 2.0 mm pigtail pair", "", "", "Amazon, listing not re-linked (20-pair male and female set, order 2026-09-02, in the Pocket AI's inventory)", "price not recorded",
         "**Owned, 20 pairs.** Joins the holder leads to the fuel gauge's JST-PH plug. Meter polarity, not wire colour: generic leads are often wired opposite to Adafruit's convention."),
    ]},
    {"kind": "order", "head": "Owned, not used in Rev B: held for another project (solar removed 2026-10-31)", "rows": [
        ("1", "5 W solar panel, 6 V ETFE", L["panel"], "Adafruit 5367 (Voltaic P105)", "Adafruit, 2026-10-26", "$34.95",
         "**Owned, not used in Rev B.** Solar was removed from the design on 2026-10-31; nothing is wired to the charger board's solar input. 6.12 V / 940 mA peak, 148 × 223 × 4 mm, 50 cm lead ending in a 3.5 × 1.1 mm barrel. Stock for another project."),
        ("1", "DC jack adapter, 3.5 / 1.1 mm to 5.5 / 2.1 mm", L["jack_adapter"], "Adafruit 4287", "Adafruit, 2026-10-26", "$1.50",
         "**Owned, not used in Rev B.** Was the panel's plug adapter. Stock for another project."),
        ("1", "DC jack to screw terminals, 2.1 mm", L["jack_terminals"], "Adafruit 368", "Adafruit, 2026-10-26", "$2.00",
         "**Owned, not used in Rev B.** Was the two-wire landing for the panel at the charger board's VIN and G pads. Stock for another project."),
        ("1", "panel-mount USB-C extension", L["usbc"], "Adafruit 6069", "Adafruit, 2026-10-26", "$4.50",
         "**Owned, not used in Rev B.** The charger board's own USB-C port reaches the rear panel through a cutout, so no extension is needed. Spare."),
        ("1", "6600 mAh battery, 3.7 V protected", L["battery"], "Adafruit 353", "Adafruit, 2026-10-26", "$24.50",
         "**Owned, not used in Rev B.** Replaced by the 16340 cell: the compact body has no room for a 69 × 54 × 18 mm pack, and the charger board's fixed 6 h timer never suited it on USB (REVIEW.md §2.1). Spare for a larger project."),
        ("1", "1200 mAh battery, 3.7 V protected", L["battery_1200"], "Amazon B09G2S88Q3", "Amazon, 2026-10-26", "price not recorded",
         "**Owned, not used in Rev B.** Was the Phase 4 bench pack. Bench spare; meter its lead's polarity before it ever meets the charger board."),
    ]},
    {"kind": "order", "head": "Compact body: to buy, to print, and the owned brass", "rows": [
        ("1", "3 mm smoked acrylic front, 82 × 52 mm", L["acrylic"], "", "SendCutSend, or a local plastics shop offcut cut by hand", "quote after the bench fit check",
         "**To buy.** The whole face, one piece; the OLED's 60 × 37 mm picture sits 1 mm behind it. Cut only after the real boards have confirmed the zero-margin depths in COMPACT_DESIGN.md."),
        ("1 spool", "black PETG, body, lid and rear panel", L["petg"], "", "owned filament if any, else Printed Solid", "",
         "**To print.** The 82 × 52 × 68 mm shell with 2 mm walls, a lift-off lid, a removable rear panel, a floor slot for the speaker and the four cutouts (lid hole, knob, USB ports, charger port). Print after the fit check."),
        ("2 cradles", "brass tube set, 3 mm tube", L["brass"], "Amazon B0F2FKLC2N", "Amazon, 2026-10-26", "price not recorded",
         "**Owned.** Two bent U cradles under the body, about 150 mm of 3 mm tube each: the stand, the 8° tilt and the 3 mm gap the speaker fires into. Brass stays electrically floating; meter each cradle to every net once fitted."),
    ]},
]

NOTES = [
    ("2026-10-19", "Core order verified against the vendor pages and placed at Adafruit, most lines ×2 for spares, $184.45 before shipping and tax. The mono speaker was out of stock, so the "
     "stereo pair. The solder-in proto board was dropped: the owned solderless breadboards carry Phase 1."),
    ("2026-10-26", "Battery and solar parts bought in one Adafruit order, $82.35 before shipping and tax: the 6600 mAh battery ($24.50, the builder's decision over the review's 4400 mAh pick, "
     "with the 6 h charge-timer limit recorded), the charger board ($8.95), the fuel gauge ($5.95), the panel-mount USB-C extension ($4.50), the 5 W solar panel ($34.95), the DC jack adapter ($1.50) "
     "and the DC jack to screw terminals ($2.00). The same day: the coin cell 10-pack, the 1200 mAh battery and the brass tube set from Amazon. Cheaper sources were checked first "
     "(the charger board at Micro Center Brooklyn, SKU 837740, $8.95 in-store; the fuel gauge at Mouser, 485-5580; generic 6 V panels at $12–18); the builder bought the Adafruit cart anyway. "
     "Next time, check the low-shipping sources first."),
    ("2026-10-28", "Controller board ordered from DigiKey, three pieces, with the drone's sensors. Correction: no controller was ordered on 2026-10-19 as this sheet had said."),
    ("2026-10-30", "Naming rule: component words with the link on the word; order codes only in the Order code column."),
    ("2026-10-31", "**Rev B: solar removed, compact body, 16340 cell.** The battery is one owned 16340 cell in the owned holder on an owned JST-PH pigtail, through the fuel gauge into the charger "
     "board's BAT port; charger jumper to 500 mA; charging through the charger board's own USB-C port. The 5 W solar panel, the DC jack adapter, the DC jack to screw terminals, the panel-mount "
     "USB-C extension, the 6600 mAh battery and the 1200 mAh battery are owned and held for another project. The body is 82 × 52 × 68 mm (COMPACT_DESIGN.md). Nothing to buy but the acrylic face and the PETG print."),
    ("2026-11-05", "**Sunrise lamp added** at the builder's request: an owned LED filament in the lid, fed from the cell + through 15 Ω (not the 1 A boost, which an alarm already nearly fills), "
     "switched by an owned MOSFET on GPIO40, faded up over 30 minutes by the clock's Alarm 2. Nothing to buy."),
]

FOOT = [
    "**Spent so far:** $184.45 at Adafruit on 2026-10-19, $45.00 at DigiKey on 2026-10-28 for the controllers, $82.35 at Adafruit on 2026-10-26 for the battery and solar parts, plus the Amazon lines "
    "with prices not recorded; all before shipping and tax. Of the $82.35, $67.45 is now held stock (panel, adapters, extension, 6600 mAh battery) and $14.90 (charger board, fuel gauge) is in Rev B.",
]

ORDER_COLS = ("Qty", "Part", "Order code", "Where", "Price", "Why")


def md_inline(t):
    """Escape, then render [text](url) and **bold** for the page."""
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)


def order_html():
    o = ['<h2 id="order">Rev B parts list, 2026-10-31</h2>',
         '<p>Every part of Rev B is owned. Each row opens with its status: <strong>owned</strong>, <strong>owned, not used in Rev B</strong> (held for another project), '
         '<strong>to buy</strong> or <strong>to print</strong>. Prices are what was paid or read from the vendor page on the order date. Each part is named by what it is and linked to the '
         'exact product bought; the order-code column is there so a part can be re-bought. The decision notes at the end are the history of this sheet.</p>']
    for sec in SECTIONS:
        o.append(f"<h3>{esc(sec['head'])}</h3>")
        o += [f"<p>{md_inline(p)}</p>" for p in sec.get("intro", [])]
        o.append('<div class="tw"><table><tr>' + "".join(f"<th>{c}</th>" for c in ORDER_COLS) + "</tr>")
        for qty, part, url, code, where, price, why in sec["rows"]:
            name = f'<a href="{url}" target="_blank" rel="noopener">{esc(part)}</a>' if url else esc(part)
            o.append(f'<tr><td class="m">{esc(qty)}</td><td>{name}</td><td class="m">{esc(code)}</td><td>{md_inline(where)}</td><td class="m">{esc(price)}</td><td>{md_inline(why)}</td></tr>')
        o.append("</table></div>")
        o += [f"<p>{md_inline(p)}</p>" for p in sec.get("after", [])]
    o.append("<h3>Decision notes</h3><dl class=\"notes\">")
    o += [f"<dt>{d}</dt><dd>{md_inline(t)}</dd>" for d, t in NOTES]
    o.append("</dl>")
    o += [f"<p>{md_inline(p)}</p>" for p in FOOT]
    return "".join(o)


# ----------------------------------------------------------------------------- the outline
def outline_html():
    def a(word, key):
        return f'<a href="{LINK[key]}" target="_blank" rel="noopener">{word}</a>'
    return f"""
<h2>What this wiring is</h2>
<p>Cyber Dawn's first build is a USB-powered alarm clock on a bench: one {a("controller board", "controller")}, a 2.42-inch {a("OLED display", "display")}, a hardware {a("real-time clock", "clock")}, a small class-D {a("amplifier", "amp")} with a sealed {a("speaker", "speaker")}, a {a("rotary encoder", "encoder")} wheel, a {a("snooze button", "snooze")} and an {a("arm switch", "arm")}, plus three sensors on the same I²C chain. Nothing here is brass yet and nothing has a battery. The wiring exists to prove one thing, that the clock wakes you with no network, before the battery goes in and the body is printed.</p>
<p>The sheet above groups the connections into six independent sets. Only ground is shared between them, and every set can be built and tested on its own day.</p>

<div class="note warn"><span class="lbl">Three rules the whole sheet obeys</span>
<p><strong>Every logic line is 3.3 V.</strong> The controller's pins are not 5 V tolerant. The display, the clock and every sensor run on the controller's 3V3 pin. The amplifier is the only part on 5 V, and it reads 3.3 V logic correctly because its thresholds are absolute voltages, not fractions of its supply. The sunrise lamp runs from the cell, but the controller only ever touches its switch's gate, at 3.3 V.</p>
<p><strong>One power source at a time.</strong> In Phase 1 the controller's USB socket is the source and the 5V pin is an output. In Phase 4 the charger board's 5 V output, with one 16340 cell behind it, feeds the 5V pin and the controller's USB socket must be empty, or two supplies fight on the same copper. Charging then happens at the charger board's own USB-C port, never at the controller's.</p>
<p><strong>The amplifier's outputs are a bridge.</strong> OUT+ and OUT− each swing between 0 and 5 V. Neither is ground, so neither may ever touch the GND rail, a scope clip or a brass part.</p>
</div>

<div class="day" id="tonight">
<div class="dayhead"><span class="daynum">UNTIL THE CONTROLLER BOARD LANDS</span><h2>Tonight: prove every part on the stand-in, 2 to 3 hours</h2><span class="badge">added 2026-10-31 · nothing to undo later</span></div>
<div class="daybody">
<p>The controller board is in transit (DigiKey, ordered 2026-10-28). The free <a href="https://www.adafruit.com/product/5302" target="_blank" rel="noopener">stand-in controller</a> that came with the Adafruit order has a STEMMA QT socket, so the whole I²C chain plugs in with no wiring to any pin. Everything done tonight either stays for the real build (coin cell, OLED header) or is a jumper pulled out in a minute. The aim is only to know that each part is alive before the wiring on this sheet starts. The steps, the code and the expected console lines are on <a href="https://claude.ai/artifact/MzUBsAW1tWAAZRxakyo6yc" target="_blank" rel="noopener">Cyber Dawn Day Zero</a> and in <code>docs/DAY0_TEST.md</code>; this box is the schedule.</p>
<div class="sched">
<div class="t">0:00</div><div><strong>Two minutes, no computer.</strong> Coin cell into the clock, + side up. Photograph the OLED's BS1/BS2 jumpers; touch nothing.</div>
<div class="t">0:10</div><div><strong>CircuitPython onto the stand-in.</strong> Hold BOOT, plug in with a data cable, drag the UF2 onto RPI-RP2, copy the six libraries into <code>CIRCUITPY/lib</code> (Day Zero, Step 2).</div>
<div class="t">0:30</div><div><strong>The chain, one QT cable at a time</strong> from the socket: clock, encoder, proximity and light, accelerometer, temperature and humidity. Scan after each board; the list should read <code>0x68</code>, then add <code>0x49</code>, <code>0x60</code>, <code>0x18</code>, <code>0x38</code>. A board that does not appear: reseat, swap the cable, then swap the board.</div>
<div class="t">0:50</div><div><strong>Set the clock from the console, then run Day Zero's <code>code.py</code>:</strong> one line a second from all five boards. Turn the knob, press its five buttons, cover the sensor, tip the board, breathe on the sensor.</div>
<div class="t">1:20</div><div><strong>Coin-cell test.</strong> Unplug USB for one minute, plug back in: the time is one minute later, not 2000-01-01. This is the one test the alarm clock truly depends on.</div>
<div class="t">1:30</div><div><strong>Snooze button and arm switch,</strong> two jumpers each: one leg to A0 (snooze) or A1 (arm), the other leg to G. In the console a <code>DigitalInOut</code> with <code>Pull.UP</code> reads False while pressed or slid. Five minutes; it proves the two parts and nothing else.</div>
<div class="t">1:40</div><div><strong>Amp and speaker.</strong> The amp already has pins. Five jumpers: VIN to RAW, GND to G, BCLK to D2, LRC to D3, DIN to D4; the speaker on OUT+ and OUT−, never to ground. Day Zero Optional B plays one quiet second of 440 Hz. GAIN and SD stay unwired tonight: the breakout's own pull-up enables it, and the tone is kept quiet in code.</div>
<div class="t">2:00</div><div><strong>Stop here, or, if there is time, the OLED.</strong> Soldering the header strip and the 220 µF is final-build work, so nothing is wasted; the seven jumpers of Day Zero Optional A are the only throwaway. If the glass stays dark, check that the BS1/BS2 photo shows SPI and stop. Do not spend the evening on it.</div>
</div>
<div class="done"><h3>Pass</h3><p>Five addresses on the scan, five live readings on one console line, the time survives a minute unplugged, both switches read, one second of tone. Then every part on this sheet is known good, and the sheet is wired on the controller board the day it lands.</p></div>
<div class="note tip"><span class="lbl">Two things about the stand-in</span>
<p><strong>Nothing transfers, by design.</strong> Nothing from tonight is soldered to it: the chain hangs off its socket, the switches and the amp sit on jumpers. When the controller board arrives, the first QT cable moves to the <a href="https://www.adafruit.com/product/4209" target="_blank" rel="noopener">QT-to-header cable</a> on 3V3, GND, GPIO8 and GPIO9. The chain is already proven and the clock already set, so Day 1 of Phase 1 starts at the toolchain.</p>
<p><strong>Its limits.</strong> A 500 mA fuse on RAW, so bench volume only; 3V feeds the chain and the OLED and nothing more; no Wi-Fi; it cannot run the ESP-IDF firmware in <code>firmware/</code>. If one of the two DIYmall ESP32-S3-DevKitC-1 N16R8 boards from the Amazon order of 2026-10-01 is in the drawer, use it instead of the stand-in: it has the controller board's pin map, so the controller-board variant at the end of Day Zero applies and tonight's wiring is the final wiring.</p>
<p><strong>If you would rather build the whole clock on the stand-in tonight</strong>, alarm wire, amp and switches included, the sheet for that is <a href="https://claude.ai/artifact/SK5hXfRNfcD7ZAkpKVTEFG" target="_blank" rel="noopener">Cyber Dawn Stand-in Wiring</a>: the same drawing style as this page, plus the wiring laid out hole by hole on one of the 830-point breadboards. It is more than the two-hour check above; nothing on it transfers either, except the OLED header and its capacitor.</p>
</div>
</div></div>

<h2>1 · The I²C chain: six boards, four wires</h2>
<p><strong>What.</strong> GPIO8 is SDA and GPIO9 is SCL. A {a("QT-to-header cable", "qt_header")} turns those two pins plus 3V3 and GND into a JST SH plug, and from there the boards daisy-chain with 100 mm {a("QT cables", "qt_cable")}: {a("rotary encoder", "encoder")}, {a("real-time clock", "clock")}, {a("fuel gauge", "gauge")} (Phase 4), {a("proximity and light sensor", "proximity")}, {a("accelerometer", "accel")}, {a("temperature and humidity sensor", "climate")}. No soldering anywhere in this group.</p>
<p><strong>Why one bus.</strong> I²C lets many devices share two wires because each has an address. The six addresses here are all distinct, 0x49, 0x68, 0x36, 0x60, 0x18 and 0x38, so there is nothing to configure. The reference build used a motion sensor whose 0x68 collided with the clock; the accelerometer chosen here avoids that.</p>
<p><strong>Why no extra pull-ups.</strong> Each Adafruit board already carries two 10 kΩ pull-ups. Six in parallel is 1.67 kΩ, which sinks 2 mA against the 3 mA limit and gives a 212 ns rise time against 300 ns at 400 kHz. The bus is legal as shipped. A seventh board would be the point to start removing pull-up jumpers.</p>

<h2>2 · The two interrupt wires: the ones people forget</h2>
<p><strong>The {a("real-time clock", "clock")}'s SQW to GPIO4, with 10 kΩ to 3V3.</strong> This is the alarm. The clock pulls the line low when Alarm 1 matches, and GPIO4 is one of the RTC-capable pins, 0 to 21, that can wake the controller from deep sleep. The wire is not in the STEMMA QT cable; it comes from the breakout's own SQW pad. The output is open-drain, meaning the chip can only pull it down and never up, so without a resistor to 3.3 V the line floats and the alarm silently never fires. That resistor is mandatory, not a precaution.</p>
<p><strong>The {a("rotary encoder", "encoder")}'s INT to GPIO1.</strong> The encoder adapter pulses its INT pin low on any turn or press, also open-drain. This line does not have to be valid before firmware runs, so the controller's internal pull-up is enough, but it must be enabled in code or the wheel will seem to work only when polled.</p>
<p><strong>The {a("accelerometer", "accel")}'s INT to GPIO5</strong> comes in Phase 3 for tap-to-wake. GPIO5 was chosen because it is RTC-capable; the September map had this on GPIO40, which cannot wake anything. Unlike the other two, this output is push-pull and active-high by default (its polarity is a register bit), so it needs no pull-up, and the wake must be set for a high level or the bit flipped to match.</p>

<h2>3 · The display: seven wires, no level shifter</h2>
<p><strong>What.</strong> The {a("OLED display", "display")}'s 20-pin header is marked by number: pin 2 (VCC) to 3V3, pin 1 (GND) to GND, then five signal lines: pin 7 (SCLK) on GPIO12, pin 8 (MOSI) on GPIO11, pin 15 (CS) on GPIO10, pin 4 (DC) on GPIO6, pin 16 (RESET) on GPIO7. Pins 3, 5, 6, 9–14 and 17–19 stay empty, and pin 20, the metal frame, may float. The kit's 220 µF goes across pins 1 and 2 at the module, stripe to pin 1.</p>
<p><strong>Why these pins.</strong> GPIO10 to 13 are the controller's FSPI pins routed through the IO mux, the fastest path for a 128×64 framebuffer refresh. DC and RESET are plain outputs and can be anywhere; 6 and 7 are free and not strapping pins.</p>
<p><strong>Why the shifter stays in the bag.</strong> The level shifter in the box exists for 5 V boards like an Arduino Uno. The controller is already 3.3 V, so wiring it in would add an IC and twelve joints for nothing. The 220 µF stays because the module wants a stiff 3.3 V rail; the controller's regulator is 50 mm away.</p>
<p><strong>Before wiring.</strong> The module picks parallel, SPI or I²C with two 0 Ω links on its back, BS1 and BS2. The first board shipped in 8080 parallel (photo of 2026-11-03), so move R2 to R3 and R4 to R5, which is Adafruit's SPI setting. Take each upper link off before its lower pads are bridged: both fitted short 3.3 V to ground. The steps and meter checks are in Day Zero's Optional A; then solder the header.</p>

<h2>4 · Audio: four signals, 5 V, and a hardware ceiling</h2>
<p><strong>What.</strong> Into the {a("amplifier", "amp")}: BCLK on GPIO14, LRC on GPIO15, DIN on GPIO16, SD on GPIO17. VIN from the controller's 5V pin, GND to GND, 220 µF and 100 nF across them at the amp. GAIN strapped to VIN. The {a("speaker", "speaker")} on OUT+ and OUT−.</p>
<p><strong>Why 5 V and not 3.3.</strong> Not for loudness: with GAIN strapped to VIN, 3.3 V would still give about 1.4 W against 1.6 W on 5 V. The reason is heat. On 3.3 V the amp's current would pass through the controller's linear regulator, which is already the hottest part on the board.</p>
<p><strong>Why GAIN to VIN.</strong> That strap selects 6 dB instead of the default 9 dB and caps the output near 1.6 W into 4 Ω. At 9 dB the amp's 1.3 A peaks exceed the 1 A boost converter that arrives in Phase 4. Putting the ceiling in copper means no firmware bug can raise it.</p>
<p><strong>Why SD has a pull-down.</strong> The breakout has a 1 MΩ pull-up from SD to VIN, so the amp powers up enabled. A 10 kΩ to ground wins against that and holds the amp silent until GPIO17 is driven, so a reset mid-alarm cannot leave the speaker screaming on noise. Driven high by GPIO17, the amp plays the left channel only, so the firmware puts the mono stream in the left I²S slot.</p>
<p><strong>Why the capacitors sit at the pins.</strong> A bass note asks for hundreds of milliamps in a millisecond. The electrolytic answers the slow part, the ceramic the fast part, and every centimetre of wire between them and the amp makes them slower.</p>

<h2>5 · Snooze, arm, and power</h2>
<p><strong>{a("Snooze button", "snooze")} on GPIO18, {a("arm switch", "arm")} on GPIO21,</strong> each switch's other leg to GND. Both pins are RTC-capable so a press can wake the sleeping clock, and the controller's internal pull-ups make them read high until pressed. In deep sleep those internal pull-ups work only while the RTC peripheral domain stays powered, so the firmware keeps it on (or 10 kΩ pull-ups go on the board) if deep sleep is ever used. The arm switch is a logic input only; a clock you can power off is not a reliable alarm.</p>
<p><strong>Power in Phase 1 is the USB socket.</strong> Days 1 to 3 run from any port. From Day 4 the amplifier adds about 360 mA average and 0.9 A peaks to the controller's 565 mA, so use a USB-C wall adapter rated 2 A. A laptop port browns out and the symptom looks exactly like a wiring fault.</p>
<p><strong>Power in Phase 4 is one 16340 cell</strong> (Rev B, 2026-10-31; no solar). The owned {a("16340 holder with leads", "holder")} goes on a JST-PH pigtail through the {a("fuel gauge", "gauge")} into the {a("charger board", "charger")}'s BAT port, jumper cut to 500 mA (it ships closed at 1 A). The charger board's 5 V boost output feeds the 5V pin and the amplifier VIN; the charger's own USB-C port is the charging port; its solar input stays empty. Meter the holder leads for polarity before the cell meets anything.</p>
<p><strong>Why the controller's regulator sets the rules.</strong> It is an 800 mA low-dropout linear regulator (per the controller board's schematic; an earlier note assumed a 1.1 V-dropout part) with about 0.3 V of dropout at this load: the 5 V rail must stay above about 3.7 V or the 3.3 V rail collapses and the controller resets. That is the brownout mechanism Phase 4 will scope while the clock runs unplugged on the cell, and it is why nothing else may be hung on the controller's 3V3 pin beyond the display and the chain.</p>

<h2>6 · The sunrise lamp: one filament, one switch (added 2026-11-05)</h2>
<p><strong>What.</strong> An {a("LED filament", "filament")} lies in a 40 × 2 mm slot along the lid's front edge. Its + lead takes the cell's + through 15 Ω; its − lead goes to the drain of a {a("MOSFET switch", "mosfet")} whose source is on GND. GPIO40 drives the gate through 100 Ω, with 10 kΩ from gate to GND. On the bench, before the cell is in, the + side comes from the 5V pin through 33 Ω.</p>
<p><strong>Why the cell and not the 5 V boost.</strong> The boost is rated 1 A and an alarm already peaks near 0.93 A. The cell allows 2 A, so the lamp's 0.1 A comes from the cell's + lead, spliced into the holder's pigtail, and the boost budget is untouched. Plugged in, the charger feeds that same node.</p>
<p><strong>Why a resistor, and why its current drifts.</strong> An LED's current climbs steeply with voltage, so the resistor sets it: about 0.1 A on a full 4.2 V cell, 0.06 A at 3.7 V. The firmware reads the cell voltage from the {a("fuel gauge", "gauge")} and scales the dimming so the sunrise looks the same on any charge.</p>
<p><strong>Why a MOSFET.</strong> A GPIO pin gives about 20 mA; the lamp wants five times that. The switch's threshold is 1.45 V at most, so 3.3 V turns it fully on, and the 10 kΩ holds it off while the controller boots. GPIO40 is free in both encoder options and needs no wake ability: it is an output.</p>
<p><strong>How the sunrise runs.</strong> The clock's Alarm 2 fires 30 minutes before the alarm, on the same SQW wire, and wakes the controller. The lamp fades up on a perceptual curve, then Alarm 1 rings as before. About 25 lumens at full: a warm glow on the nightstand, not a daylight lamp. A morning's sunrise costs about 2 % of the cell.</p>

<h2>Before power, with the meter</h2>
<ul class="check">
<li>3V3 to GND, 5V to GND, 5V to 3V3: no steady beep. A chirp that stops is a capacitor.</li>
<li>OUT+ and OUT− to GND and to each other: silent, or a few ohms through the speaker only.</li>
<li>Clock SQW to 3V3: about 10 kΩ. If it reads open, the pull-up is missing and the alarm will never fire.</li>
<li>Amp SD to GND: about 10 kΩ. If it reads near 1 MΩ or open, the pull-down is missing.</li>
<li>Lamp switch gate to GND: about 10 kΩ. Filament − to GND: open until GPIO40 drives the gate.</li>
<li>Every display signal pin to its controller pin: beep. Adjacent display pins to each other: silent.</li>
<li>The controller's USB socket empty whenever a bench supply or, later, the charger board feeds the 5V pin.</li>
<li>Phase 4: the 16340 holder's leads, red to the + pad, before the cell goes in. Red on the wrong pad is the one mistake no protection circuit undoes.</li>
</ul>
"""


def style():
    src = BENCH.read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def page_html():
    return "\n".join([
        '<title>Cyber Dawn Wiring</title>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        style(),
        '<style>figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} .wrap{max-width:1100px} dl.notes dt{font-weight:700;margin-top:10px}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Cyber Dawn &middot; Phase 1 wiring</div>',
        '<h1>Every connection, and why</h1>',
        '<div class="sub">The bench alarm clock on one sheet, a short outline of each group of wires, and the Rev B parts list of 2026-10-31 (solar removed, compact body, one 16340 cell).<br>Pin numbers are the decided map in <code>firmware/main/include/board_pins.h</code>; the reasoning is <code>docs/WIRING_CROSSREF.md</code> and <code>docs/REVIEW.md</code>.</div></div>',
        f'<figure class="sheet">{sheet()}<figcaption><strong>Print it landscape on Letter; it is page 1 of the PDF.</strong> Thick lines are wires you solder or plug, the brass line is the STEMMA QT chain, dotted blocks are later phases. A dot is a joint; a hop is a crossing that does not touch.</figcaption></figure>',
        outline_html(),
        order_html(),
        '<hr><p class="sub">Built by <code>docs/pages/gen/wiring_outline.py</code> from the repository documents named above. Nothing on this page has been built; the pin map is verified against Espressif\'s v1.1 user guide and the vendor datasheets, not against hardware. Rev B 2026-10-31: solar removed, compact body, 16340 cell.</p>',
        '</div>'])


def print_pdf(html):
    PRINT.mkdir(exist_ok=True)
    # page 1: the sheet alone, landscape
    sheet_css = ("<style>@page{size:letter landscape;margin:7mm} html,body{background:#fff;margin:0}"
                 ":root{--paper:#fff;--ink:#000;--ink-2:#333;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#eee}"
                 "svg{width:262mm;height:auto;display:block;margin:0 auto}</style>")
    # the rest: portrait, black, 9.5 pt like the Pocket AI reading PDFs
    page_css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:9.5pt!important;line-height:1.4} .wrap{max-width:none;padding:0}"
                "figure.sheet{display:none} h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} h3{font-size:9pt;margin-top:10pt} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
                ".note{margin:10pt 0;padding:8pt 10pt} .note p{margin:3pt 0} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt}"
                "tr{break-inside:avoid} ul.check{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        s_html = pathlib.Path(d) / "s.html"; s_pdf = pathlib.Path(d) / "s.pdf"
        p_html = pathlib.Path(d) / "p.html"; p_pdf = pathlib.Path(d) / "p.pdf"
        s_html.write_text("<!doctype html><meta charset=utf-8><title>sheet</title>" + sheet_css + sheet())
        p_html.write_text("<!doctype html><meta charset=utf-8>" + html.replace("</style>", "</style>" + page_css, 1))
        for src, pdf in ((s_html, s_pdf), (p_html, p_pdf)):
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "cyber-dawn-wiring.pdf"
        subprocess.run(["pdfunite", str(s_pdf), str(p_pdf), str(out)], check=True)
        shutil.copyfile(s_pdf, PRINT / "cyber-dawn-wiring-sheet.pdf")
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


def order_markdown():
    o = ["# Rev B parts list, 2026-10-31 (the order sheet)", "",
         "Every part of Rev B is owned. Each row's Why cell opens with its status: **owned**, **owned, not used in Rev B** (held for",
         "another project), **to buy** or **to print**. Prices are what was paid or read from the vendor page on the order date.",
         "Supersedes the purchase tables in `BOM.md` and `bom/bom.csv`, which keep the September design reasoning. Each part is",
         "named by what it is and linked to the exact product bought; the order-code column is there so a part can be re-bought.",
         "The decision notes at the end are the history of this sheet (first verified 2026-10-19; Rev B 2026-10-31: solar removed,",
         "compact body, 16340 cell). The page `pages/cyber-dawn-wiring.html` is built from the same list by",
         "`pages/gen/wiring_outline.py`; edit the script, not this file.", ""]
    for sec in SECTIONS:
        o += [f"## {sec['head']}", ""]
        for p in sec.get("intro", []):
            o += [p, ""]
        o += ["| " + " | ".join(ORDER_COLS) + " |", "| ---: | --- | --- | --- | --- | --- |"]
        for qty, part, url, code, where, price, why in sec["rows"]:
            name = f"[{part}]({url})" if url else part
            o.append(f"| {qty} | {name} | {code} | {where} | {price} | {why} |")
        o.append("")
        for p in sec.get("after", []):
            o += [p, ""]
    o += ["## Decision notes", ""]
    o += [f"- **{d}:** {t}" for d, t in NOTES]
    o.append("")
    for p in FOOT:
        o += [p, ""]
    (PAGES.parent / "ORDER_SHEET.md").write_text("\n".join(o))
    print("wrote", PAGES.parent / "ORDER_SHEET.md")


def main():
    html = page_html()
    OUT.write_text(html)
    order_markdown()
    print("wrote", OUT, OUT.stat().st_size)
    print_pdf(html)


if __name__ == "__main__":
    main()
