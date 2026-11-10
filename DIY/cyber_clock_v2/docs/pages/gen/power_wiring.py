"""Builds docs/pages/cyber-dawn-power.html, docs/pages/cyber-dawn-power-sheet.html and the two print PDFs
docs/pages/print/cyber-dawn-power-sheet.pdf (one landscape Letter page) and cyber-dawn-power-notes.pdf:
the Rev B power wiring of Cyber Dawn on one sheet, an outline of every connection and why, the meter
checks the meter rule allows, and the parts table with the exact products owned.

Rev B 2026-10-31: solar removed, compact body, 16340 cell. The chain is USB-C into the charger board's
own port through the rear panel cutout; one Nitecore 16340 cell in the owned holder, on an owned JST-PH
pigtail, through the fuel gauge into the charger's BAT port; the charger's 5 V boost out through a JST-PH
disconnect to the controller's 5V pin and the amplifier's VIN. The charger's solar input stays empty.
2026-11-08: the sunrise lamp's + tap at the cell's red-lead splice (WIRING_CROSSREF finding 7, 2026-11-05) drawn and explained.

Sources: docs/COMPACT_DESIGN.md (the Rev B decisions), docs/INVENTORY.md (what is owned, checked 2026-10-31),
docs/REVIEW.md §2.1 (the 6 h timer), §4 (power chain) and §8.2 (amp peaks), firmware/main/include/board_pins.h,
the Adafruit guides for the charger board and the fuel gauge, and Espressif's DevKitC-1 v1.1 user guide
("three mutually exclusive ways to provide power"). Drawing helpers and page style come from
wiring_outline.py so the two sheets match. Does NOT touch ORDER_SHEET.md."""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wiring_outline import PAGES, PRINT, Router, T, block, capacitor, dot, esc, flag, gnd, pin, style  # noqa: E402

OUT = PAGES / "cyber-dawn-power.html"
SHEET_OUT = PAGES / "cyber-dawn-power-sheet.html"
W, H = 1360, 1000

CONTROLLER = "https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894"
CHARGER = "https://www.adafruit.com/product/6106"
GAUGE = "https://www.adafruit.com/product/5580"
HOLDER = "https://www.amazon.com/dp/B0CRGK889F"
PIGTAIL = "https://www.amazon.com/dp/B0F6T4LKDG"
AMP = "https://www.adafruit.com/product/3006"
QT = "https://www.adafruit.com/product/4210"


def a(word, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{word}</a>'


def jst(rt, x0, x1, y, net):
    """A JST-PH plug/socket pair drawn in a lane: the hard disconnect."""
    o = [rt.wire([(x0, y), (x0 + 18, y)], "rod", net), rt.wire([(x1 - 18, y), (x1, y)], "rod", net),
         f'<rect x="{x0+18}" y="{y-9}" width="{(x1-x0-36)/2-3}" height="18" rx="3" class="cable"/>',
         f'<rect x="{(x0+x1)/2+3}" y="{y-9}" width="{(x1-x0-36)/2-3}" height="18" rx="3" class="cable"/>']
    return "".join(o)


def jstv(rt, x, y0, y1, net):
    """The same plug pair, drawn in a vertical lane."""
    mid = (y0 + y1) / 2
    o = [rt.wire([(x, y0), (x, mid - 36)], "rod", net), rt.wire([(x, mid + 36), (x, y1)], "rod", net),
         f'<rect x="{x-9}" y="{mid-36}" width="18" height="33" rx="3" class="cable"/>',
         f'<rect x="{x-9}" y="{mid+3}" width="18" height="33" rx="3" class="cable"/>']
    return "".join(o)


def led(x, y, letter, colour):
    return f'<circle cx="{x}" cy="{y}" r="6" class="pinend"/>' + T(x, y + 4, letter, "pinlab", "middle", 'font-size="9px"') + T(x + 11, y + 4, colour, "fn")


def sheet():
    rt = Router()
    w = rt.wire
    o = [T(20, 30, "Cyber Dawn, Rev B: the power wiring on one sheet", "h1"),
         T(20, 48, "A dot is a joint. A line that hops over another does not touch it. Thick = wire you solder or plug. Brass = JST-PH plugs and the STEMMA QT chain. Every ground symbol is the same ground.", "sub"),
         T(W - 20, 30, "Rev B 2026-10-31: solar removed, one 16340 cell, USB-C through the rear panel · 2026-11-08: the sunrise lamp's tap at the cell", "fn", "end")]

    # ---------------------------------------------------------------- charger, centre
    CX, CY, CW, CH = 600, 100, 260, 380
    o.append(block(CX, CY, CW, CH, "Charger board", "USB-C in · 5 V 1 A out"))
    C = {}
    for name, y, fn in (("VIN", 160, "solar in: empty"), ("G", 190, "its ground: empty"), ("USB-C", 300, "5 V in, the port")):
        C[name] = (CX, y); o.append(pin(CX, y, name, "L", fn, CX + 62))
    for name, y, fn in (("5V +", 160, None), ("−", 190, None), ("EN", 250, None)):
        C[name] = (CX + CW, y); o.append(pin(CX + CW, y, name, "R"))
    o.append(T(CX + CW - 14, 214, "terminal block: 5 V, 1 A", "fn", "end"))
    o.append(T(CX + CW - 62, 254, "leave open = on", "fn", "end"))
    C["BAT"] = (CX + 120, CY + CH); o.append(f'<circle cx="{CX+120}" cy="{CY+CH}" r="4.5" class="pinend"/>')
    o.append(T(CX + 120, CY + CH - 10, "BAT, JST-PH", "pin", "middle"))
    o.append(led(CX + 30, 400, "C", "orange: charging")); o.append(led(CX + 30, 424, "F", "red: fault; red + orange = latched"))
    o.append(led(CX + 30, 448, "5", "green: 5 V out is live"))
    o.append(T(CX + 30, 352, "power path: input feeds the load first, surplus charges", "fn"))
    o.append(T(CX + 30, 372, "charge-rate jumper on the back, cut = 500 mA, see left", "fn"))

    # ---------------------------------------------------------------- power-up order and the flashing rule, top left
    o.append(T(40, 120, "Power-up order, every time", "lab"))
    for i, s in enumerate(("1  Cell in the holder. Meter the holder leads: red reads + against black.",
                           "2  Holder → pigtail → gauge → charger BAT. Green 5 lights, off the cell.",
                           "3  USB-C in. Green LED: 5 V out is live.",
                           "4  Then the JST to the controller. It boots on the boost.")):
        o.append(T(40, 142 + i * 17, s, "fn"))
    o.append(T(40, 222, "To flash firmware: pull the 5 V JST first, then plug the controller's USB.", "lab"))
    o.append(T(40, 238, "Espressif: the USB ports, the 5V pin and the 3V3 pin are three", "fn")); o.append(T(40, 252, "mutually exclusive ways to power the board. Never two at once.", "fn"))

    # ---------------------------------------------------------------- USB-C through the rear panel, left middle
    o.append(block(40, 270, 190, 60, "USB-C wall adapter", "owned · 2 A or more"))
    o.append(w([(230, 300), C["USB-C"]], "rod", "USB"))
    # the rear panel: a dashed wall with a cutout the cable passes through
    o.append('<path d="M330,262 L330,286 M330,314 L330,340" class="later"/>')
    o.append(T(338, 274, "rear panel", "fn")); o.append(T(338, 334, "cutout", "fn"))
    o.append(T(500, 290, "USB-C cable", "fn", "middle"))
    o.append(T(40, 352, "The cable passes through a cutout in the rear panel into the charger's own USB-C port. No extension,", "fn"))
    o.append(T(40, 366, "no second port: the controller's USB sockets stay empty. A laptop port's 0.5 A is not enough.", "fn"))

    # ---------------------------------------------------------------- the charger set for one 16340, bottom left
    o.append(T(40, 420, "The charger, set up for one 16340 cell", "lab"))
    for i, s in enumerate(("Cut the charge-rate jumper on the back: closed as shipped = 1 A, cut = 500 mA, 0.5 C.",
                           "Full from empty in about 2.5 h, so the 6 h safety timer is never reached.",
                           "Protected 16340s terminate at 4.20 V: the charger's Li-ion profile fits unchanged.",
                           "VIN and G, the solar / DC input: nothing wired. The 5 W panel is owned stock, in the drawer.",
                           "EN: leave open, so 5 V is always on.")):
        o.append(T(40, 442 + i * 17, s, "fn"))
    o.append(T(40, 560, "Rev B 2026-10-31 removed from this sheet", "lab"))
    o.append(T(40, 576, "the solar panel, the DC jack adapter, the DC jack to screw terminals, the panel-mount", "fn"))
    o.append(T(40, 590, "USB-C extension and the pouch packs. All owned; none wired.", "fn"))

    # ---------------------------------------------------------------- 5 V out to the controller, right
    DX, DY, DW, DH = 1060, 100, 260, 380
    o.append(block(DX, DY, DW, DH, "Controller board", "pins grouped by job"))
    D = {}
    for name, y, fn in (("5V", 160, "powers the board"), ("GND", 190, None), ("GPIO39", 330, "gauge INT · poll")):
        D[name] = (DX, y); o.append(pin(DX, y, name, "L", fn, DX + 70))
    o.append(T(DX + 20, 250, "GPIO8 / GPIO9: the STEMMA QT chain,", "fn")); o.append(T(DX + 20, 264, "wired on the Phase 1 sheet", "fn"))
    o.append(T(DX + 20, 400, "USB sockets: EMPTY while the 5 V", "lab")); o.append(T(DX + 20, 416, "plug is in. Unplug the JST to flash.", "lab"))
    o.append(T(DX + 20, 440, "GPIO41 charger status: unused. The", "fn")); o.append(T(DX + 20, 454, "charger has no STAT pad; read the gauge.", "fn"))
    o.append(w([C["5V +"], (920, 160)], "rod", "5V")); o.append(jst(rt, 920, 1000, 160, "5V")); o.append(w([(1000, 160), D["5V"]], "rod", "5V"))
    o.append(w([C["−"], (920, 190)], "rod", "GND")); o.append(jst(rt, 920, 1000, 190, "GND")); o.append(w([(1000, 190), D["GND"]], "rod", "GND"))
    o.append(T(960, 140, "JST-PH pair, owned", "fn", "middle")); o.append(T(960, 214, "the hard disconnect", "fn", "middle"))
    # amp tap off the 5 V lane
    o.append(w([(1030, 160), (1030, 680), (1150, 680), (1150, 710)], "rod", "5V")); o.append(dot(1030, 160))
    o.append(T(1036, 640, "5 V", "lab"))

    # ---------------------------------------------------------------- amp, bottom right (already wired on the Phase 1 sheet)
    AX, AY, AW, AH = 1090, 710, 230, 110
    o.append(f'<rect x="{AX}" y="{AY}" width="{AW}" height="{AH}" rx="9" class="later"/>')
    o.append(T(AX + AW / 2, AY + 60, "Amplifier", "title", "middle")); o.append(T(AX + AW / 2, AY + 78, "signals on the Phase 1 sheet", "sub", "middle"))
    for name, x in (("VIN", 1150), ("GND", 1230)):
        o.append(f'<circle cx="{x}" cy="{AY}" r="4.5" class="pinend"/>'); o.append(T(x, AY + 18, name, "pin", "middle"))
    o.append(w([(1230, 710), (1230, 680), (1270, 680)], "rod", "GND")); o.append(dot(1230, 680)); o.append(gnd(1270, 680))
    o.append(f'<line x1="1185" y1="668" x2="1185" y2="692" class="thin"/><line x1="1195" y1="668" x2="1195" y2="692" class="thin"/>')
    o.append(w([(1150, 680), (1185, 680)], "thin", "5V")); o.append(dot(1150, 680)); o.append(w([(1195, 680), (1230, 680)], "thin", "GND"))
    o.append(T(1190, 660, "220 µF + 100 nF, at the pins", "fn", "middle"))
    o.append(T(AX + AW, AY + AH + 20, "In Phase 1 the amp took 5 V from the controller's 5V pin.", "fn", "end")); o.append(T(AX + AW, AY + AH + 34, "Now that pin is fed, so it is the same rail.", "fn", "end"))

    # ---------------------------------------------------------------- fuel gauge and the cell, bottom centre
    GX, GY, GW, GH = 600, 700, 260, 150
    o.append(block(GX, GY, GW, GH, "Fuel gauge", "I²C 0x36 · the cell passes through it"))
    G = {"JST1": (GX + 120, GY), "JST2": (GX, GY + 90), "INT": (GX + GW, GY + 110), "QT": (GX + 200, GY + GH)}
    o.append(f'<circle cx="{GX+120}" cy="{GY}" r="4.5" class="pinend"/>'); o.append(T(GX + 132, GY - 10, "JST-PH", "pin"))
    o.append(pin(GX, GY + 90, "JST-PH", "L")); o.append(pin(GX + GW, GY + 110, "INT", "R"))
    o.append(T(GX + GW - 40, GY + 114, "low = alert", "fn", "end"))
    o.append(f'<circle cx="{GX+200}" cy="{GY+GH}" r="4.5" class="pinend"/>'); o.append(T(GX + 200, GY + GH - 10, "STEMMA QT", "pin", "middle"))
    o.append(T(GX + 16, GY + 60, "the two JST ports are the same net;", "fn")); o.append(T(GX + 16, GY + 74, "cell in one, charger in the other", "fn"))
    # charger BAT -> gauge JST1 (a JST-PH plug pair: the gauge's own cable, or an owned pigtail)
    o.append(jstv(rt, 720, C["BAT"][1], G["JST1"][1], "BAT"))
    o.append(T(736, 594, "JST-PH pair, 2 A rated", "fn"))
    # the cell in its holder -> red and black leads -> solder joints to the pigtail -> JST-PH plug -> gauge JST2
    HX, HY, HW, HH = 190, 750, 250, 80
    o.append(block(HX, HY, HW, HH, "16340 cell in its holder", "3.6 V · 950 mAh · protected · owned"))
    for name, y in (("+", 775), ("−", 805)):
        o.append(f'<circle cx="{HX+HW}" cy="{y}" r="4.5" class="pinend"/>'); o.append(T(HX + HW - 10, y + 5, name, "pin", "end"))
    o.append(w([(HX + HW, 775), (520, 775)], "rod", "BAT+")); o.append(w([(HX + HW, 805), (520, 805)], "rod", "BAT-"))
    o.append(dot(490, 775)); o.append(dot(490, 805))
    o.append(T(465, 765, "red", "fn", "middle")); o.append(T(465, 819, "black", "fn", "middle"))
    o.append(T(440, 846, "solder + heat-shrink", "fn", "middle"))
    # the sunrise lamp, whole circuit (WIRING_CROSSREF finding 7): cell + splice -> 15 ohm -> filament -> MOSFET -> GND, gate from GPIO40
    o.append(T(40, 612, "The sunrise lamp: cell + → 15 Ω → LED filament → MOSFET → ground. GPIO40 switches it.", "lab"))
    o.append(T(40, 628, "Up to 0.1 A on a full cell, 0.06 A at 3.7 V. Firmware reads the cell voltage from the gauge and scales the duty.", "fn"))
    LY = 660
    o.append(w([(490, 775), (490, LY), (452, LY)], "rod", "LAMP"))
    o.append(f'<rect x="412" y="{LY-7}" width="40" height="14" rx="2" class="part"/>'); o.append(T(432, LY - 12, "15 Ω", "fn", "middle"))
    o.append(w([(412, LY), (382, LY)], "rod", "LAMPA"))
    o.append(f'<rect x="282" y="{LY-12}" width="100" height="24" rx="12" class="part"/>'); o.append(T(332, LY + 4, "LED filament", "fn", "middle"))
    o.append(T(332, LY - 17, "2200 K, in the lid", "fn", "middle"))
    o.append(w([(282, LY), (242, LY)], "rod", "LAMPK"))
    o.append(f'<rect x="182" y="{LY-20}" width="60" height="60" rx="6" class="part"/>'); o.append(T(212, LY + 14, "MOSFET", "lab", "middle"))
    o.append(T(248, LY - 6, "D", "pinlab")); o.append(T(172, LY + 36, "G", "pinlab")); o.append(T(220, LY + 52, "S", "pinlab"))
    o.append(w([(212, LY + 40), (212, LY + 52)], "rod", "GND")); o.append(gnd(212, LY + 52))
    o.append(w([(182, LY + 20), (150, LY + 20)], "rod", "GATE")); o.append(dot(158, LY + 20))
    o.append(f'<rect x="110" y="{LY+13}" width="40" height="14" rx="2" class="part"/>'); o.append(T(130, LY + 8, "100 Ω", "fn", "middle"))
    o.append(w([(158, LY + 20), (158, LY + 30)], "thin", "GATE"))
    o.append(f'<rect x="151" y="{LY+30}" width="14" height="28" rx="2" class="part"/>'); o.append(T(146, LY + 48, "10 kΩ", "fn", "end"))
    o.append(gnd(158, LY + 58))
    o.append(w([(110, LY + 20), (70, LY + 20)], "rod", "GPIO40")); o.append(f'<circle cx="70" cy="{LY+20}" r="4.5" class="pinend"/>')
    o.append(T(70, LY + 8, "GPIO40", "pin", "middle")); o.append(T(40, LY + 38, "controller", "fn"))
    o.append(f'<rect x="520" y="764" width="40" height="52" rx="3" class="cable"/>')
    o.append(w([(560, 790), G["JST2"]], "rod", "BAT"))
    o.append(T(540, 838, "JST-PH plug", "fn", "middle")); o.append(T(540, 852, "owned pigtail", "fn", "middle"))
    o.append(T(HX, 876, "Meter the holder leads with a cell in, before they meet the pigtail: red reads + against black.", "fn"))
    o.append(T(HX, 890, "One Nitecore cell: 3.6 V, 950 mAh, 3.4 Wh, 2 A continuous. Holder 43 × 18 × 14 mm, top layer, lid lifts off.", "fn"))
    o.append(T(HX, 904, "The cell reaches the gauge and the lamp's 15 Ω, nothing else: never the controller, never a second charger.", "fn"))
    # gauge QT -> the chain
    o.append(w([G["QT"], (800, 910)], "bus", "I2C")); o.append(T(812, 914, "one QT cable to the chain: 3V3, GND, SDA, SCL. Nothing else to wire.", "fn"))
    # gauge INT -> GPIO39
    o.append(w([G["INT"], (960, 810), (960, 330), D["GPIO39"]], "rod", "GINT"))
    o.append(T(870, 830, "INT → GPIO39", "lab")); o.append(T(870, 844, "pull-up is on the board", "fn"))

    css = ("<style>"
           ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
           ".later{fill:var(--paper);stroke:var(--ink-2);stroke-width:1.4;stroke-dasharray:5 4}"
           ".cable{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.4}"
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
           ".joint{fill:var(--ink)}"
           ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
           "</style>")
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cyber Dawn power wiring sheet, Rev B">{css}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- parts: all owned
PARTS = [
    ("Wired in Rev B, all owned", [
        ("Nitecore 16340 cell, 3.6 V 950 mAh, protected", "", "The battery. One cell in the holder; five spares in the drawer.", "Protected button-top, 2 A continuous, terminates at 4.20 V. Owned ×6 from the Pocket AI; no listing recorded."),
        ("16340 holder with leads", HOLDER, "Holds the cell, top layer, front right. Its red and black leads solder to the pigtail.", "10-pack from the Amazon order of 2026-10-27. Meter the leads with a cell in before they meet anything."),
        ("JST-PH 2.0 mm pigtail pairs, 20", PIGTAIL, "The plug into the gauge, and the hard disconnect in the 5 V lane.", "20-pair male and female cable set, daier set, Amazon order of 2026-09-02; 18 pairs spare after this clock and the satellite."),
        ("Charger board with 5 V boost", CHARGER, "Takes USB-C, charges the cell at 500 mA, makes the 5 V the controller runs on.", "Jumper on the back cut for 500 mA (closed as shipped = 1 A). The solar / DC input stays empty."),
        ("Fuel gauge", GAUGE, "Sits between cell and charger; reports % and volts on I²C 0x36.", "Two JST ports on the same net. One QT cable to the chain."),
        ("USB-C wall adapter, 2 A or more, and a USB-C cable", "", "Into the charger's own port through the rear panel cutout.", "Owned. A laptop port's 0.5 A gives a slow charge and a resetting controller."),
        ("Sunrise lamp: 15 Ω, LED filament, MOSFET on GPIO40", "https://www.amazon.com/dp/B0FR35BGYL", "Its + wire joins the cell's red-lead splice at the holder; the rest of the lamp is on the Phase 1 sheet §6.", "Owned: the filament ten-pack, the DigiKey MOSFETs, the resistor kit. Added 2026-11-05."),
        ("22 AWG or 26 AWG silicone wire", "", "Only the short holder-to-pigtail splice on this sheet; the rest is plugs and the terminal block.", "TUOFENG 26 AWG owned; nothing on this sheet carries more than the boost's 1 A."),
        ("220 µF (ALLECIN kit) and 100 nF (BOJACK kit)", "", "At the amp's VIN and GND, as on the Phase 1 sheet.", "Owned."),
        ("Multimeter", "", "The polarity and isolation checks below, nothing else.", "KAIWEETS TRMS, owned."),
    ]),
]

NOT_USED = [
    ("5 W solar panel", "https://www.adafruit.com/product/5367"), ("DC jack adapter", "https://www.adafruit.com/product/4287"),
    ("DC jack to screw terminals", "https://www.adafruit.com/product/368"), ("panel-mount USB-C extension", "https://www.adafruit.com/product/6069"),
    ("6600 mAh battery", "https://www.adafruit.com/product/353"), ("1200 mAh battery", "https://www.amazon.com/dp/B09G2S88Q3"),
]


def parts_html():
    o = ['<h2 id="parts">The parts on this sheet</h2>',
         '<p>Everything on the Rev B sheet is owned; nothing is bought for it. Links go to the exact product in <code>docs/INVENTORY.md</code>; parts with no link had no listing recorded at purchase.</p>']
    for head, rows in PARTS:
        o.append(f'<h3>{esc(head)}</h3><div class="tw"><table><tr><th>Product</th><th>Where it goes</th><th>Check</th></tr>')
        for part, url, use, check in rows:
            name = f'<a href="{url}" target="_blank" rel="noopener">{esc(part)}</a>' if url else esc(part)
            o.append(f'<tr><td>{name}</td><td>{esc(use)}</td><td>{esc(check)}</td></tr>')
        o.append('</table></div>')
    links = ", ".join(a(esc(n), u) for n, u in NOT_USED)
    o.append(f'<h3>Owned, not used in Rev B</h3><p>The {links}. All six stay in <code>docs/INVENTORY.md</code> as stock for another project. None is wired, and the charger\'s solar input is left empty.</p>')
    return "".join(o)


def outline_html():
    return f"""
<h2>What this wiring is</h2>
<p>Phase 1 ran the clock from the {a("controller", CONTROLLER)}'s USB socket. This sheet replaces that one cable with a power path: one Nitecore 16340 cell in the owned {a("16340 holder", HOLDER)}, a {a("charger board", CHARGER)} fed over USB-C through its own port, a {a("fuel gauge", GAUGE)} the firmware reads, and a 5 V boost that feeds the controller. The signals on the Phase 1 sheet do not change. The only wire that moves is the amp's 5 V, and it moves nowhere: the controller's 5V pin is now fed instead of feeding. One wire from that sheet lands here: the sunrise lamp's + lead, soldered into the cell's red-lead splice at the holder (added 2026-11-05, finding 7).</p>
<p>Rev B 2026-10-31: solar removed, compact body, 16340 cell. The clock is a USB-C appliance; the cell rides through unplugs and keeps the alarm armed. It is not there to run the clock for days.</p>
<p>Five groups, built in the order below. Each one can be checked before the next goes on.</p>

<div class="note warn"><span class="lbl">Three rules the whole sheet obeys</span>
<p><strong>One source into the {a("controller", CONTROLLER)} at a time.</strong> Espressif's user guide lists the USB ports, the 5V pin and the 3V3 pin as three mutually exclusive ways to power the board. With the charger's 5 V plugged into the 5V pin, both USB sockets stay empty. To flash firmware, pull the 5 V JST first, then plug USB. That JST pair is on the sheet for exactly this reason.</p>
<p><strong>The cell has one home.</strong> In the clock it reaches the fuel gauge, the gauge the charger, and the lamp's 15 Ω at the splice. Never the controller, never the Pocket AI's <a href="https://www.adafruit.com/product/4410" target="_blank" rel="noopener">charger board</a>, never a second charger at the same time. A cell may go into an external Nitecore charger, but only after it comes out of the holder. Two chargers on one cell fight, and a cell does not win that fight.</p>
<p><strong>The boost starts light.</strong> The boost converter on the charger board stalls if the load asks for more than about 200 mA the instant it comes up. The controller alone is fine. Firmware keeps the OLED, the radio and the amp off until the rail is up, then turns them on one at a time. This is a firmware requirement, not a caution.</p>
</div>

<h2>1 · Cell, holder, pigtail, gauge, charger</h2>
<p><strong>What.</strong> One Nitecore 16340 cell in the {a("16340 holder", HOLDER)}. The holder's red and black leads solder to the two wires of an owned {a("JST-PH pigtail", PIGTAIL)} (from the daier 20-pair JST-PH 2.0 cable set of the Amazon order of 2026-09-02), heat-shrink over each joint, and the pigtail's plug goes into either JST port on the {a("fuel gauge", GAUGE)}. The gauge's other JST port to the {a("charger board", CHARGER)}'s BAT port, with a JST-PH pair. The two gauge ports are the same net, so the cell's current passes straight through; the gauge only watches the voltage.</p>
<p><strong>Why the gauge sits in the middle.</strong> The fuel gauge estimates state of charge from the cell voltage and its own model, and the firmware reads it over I²C at 0x36 for the battery gauge on the display and the alarm reserve. Its INT pin pulls low when the charge drops below a threshold the firmware sets; it goes to GPIO39, which is polled on wake and is not a wake source. It has a 10 kΩ pull-up on the board, so no resistor.</p>
<p><strong>Why nothing else touches the cell.</strong> The protection circuit in the cell's button top handles over-charge, over-discharge and short circuit. The charger handles the charge profile. Everything else the clock draws comes out of the charger's 5 V terminal block; the lamp is the one exception, by design.</p>
<p><strong>The lamp tap.</strong> The sunrise lamp's + wire is soldered into the same joint as the holder's red lead, before the gauge: from there it runs through 15 Ω to the {a('LED filament', 'https://www.amazon.com/dp/B0FR35BGYL')}, and the filament's other end through the {a('MOSFET', 'https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089')} on GPIO40 to ground, drawn whole on this power sheet (bottom left) and on the Phase 1 sheet §6. The 10 kΩ from gate to ground holds the lamp off while the controller boots. It draws up to 0.1 A on a full cell and about 0.06 A at 3.7 V. That current cannot come from the 5 V boost, which is rated 1 A and already peaks near 0.93 A during an alarm; the cell allows 2 A, so the lamp takes it straight from the cell and the boost budget is unchanged. The gauge watches the cell's voltage, not its current, so it reads the same. Plugged in, the charger holds the cell node up and the lamp runs either way. Firmware reads the cell voltage from the gauge and scales the lamp's duty so a sunrise looks the same on any charge.</p>
<p><strong>What to check.</strong> The holder's leads, with a cell in, before they meet the pigtail: red must read positive against black. That is the one polarity on this sheet that no supplier guarantees. Red on the pigtail then lands on the + pad of the gauge and the charger; if the pigtail's own colours disagree, swap the pins in the housing.</p>

<h2>2 · The charger, set up for one 16340 cell</h2>
<p><strong>What it does.</strong> The {a("charger board", CHARGER)} takes 5 V from USB-C, charges the cell to 4.20 V, and runs the load from the input first so the cell is not cycled while power is present. The boost makes 5 V at up to 1 A from whichever is available, input or cell.</p>
<p><strong>The jumper.</strong> Cut the charge-rate jumper on the back. It ships closed, which puts the board's two current-set resistors in parallel for 1 A; cut, one resistor remains and the charge current is 500 mA (verified 2026-10-31 against the board's schematic). The cell is 950 mAh, so 500 mA is about 0.5 C; 1 A would be about 1 C, and Nitecore publishes no maximum charge current for the cell. 500 mA is the gentle choice and it costs nothing in time that matters.</p>
<p><strong>The 6 h timer.</strong> The charger chip stops charging after six hours without a break and latches a fault: red F and orange C both on, cleared only by unplugging and replugging the input. At 500 mA into 950 mAh the constant-current half takes about 1.5 h and the taper about an hour: full from empty in about 2.5 h, so the timer is never reached. It was a real concern with the 6600 mAh pack of the earlier plan; with one cell it is not.</p>
<p><strong>The profile.</strong> Protected 16340s terminate at 4.20 V, the same ceiling the charger holds for any Li-ion cell, so nothing on the board changes but the jumper. The EN pad disables the boost; leave it open so 5 V is always on.</p>
<p><strong>The solar input.</strong> VIN and G stay empty. The 5 W solar panel is owned stock for another project, and nothing lands on those pads.</p>
<p><strong>The LEDs.</strong> Orange C: charging. Green: 5 V out is live; it lights as soon as a cell is in, because the boost runs from the cell with EN open. Red F alone: a recoverable fault (the chip too hot, a short on the 5 V side); it clears itself. Red F and orange C together: a latched fault (the 6 h timer, battery over-current); unplug and replug USB-C. A low or empty cell is not a fault: below 3.0 V the charger pre-charges it gently. If F keeps lighting, pull the cell and check it in the external Nitecore charger.</p>

<h2>3 · USB-C through the rear panel</h2>
<p><strong>What.</strong> A USB-C cable from an owned 2 A wall adapter, through a cutout in the rear panel, into the charger board's own USB-C port. The charger stands against the rear panel with its port in the cutout, so the port on the outside of the clock is the charger's.</p>
<p><strong>Why not an extension.</strong> The panel-mount USB-C extension of the earlier plan is owned and unused: the compact body puts the charger at the rear panel, so there is nothing to extend.</p>
<p><strong>Why not the controller's socket.</strong> The {a("controller", CONTROLLER)}'s USB would power the controller only, bypassing the charger, and would fight the boost on the 5V pin. The clock has one way in, and the charger decides.</p>
<p><strong>Why 2 A.</strong> The charger chip caps what it takes from USB at 1.1 A, charging and load together, so the adapter never sees more; anything rated 1.5 A or above covers it, and the owned 2 A adapter does. Inside that cap the load comes first: during an alarm, charging pauses and the cell may briefly add current (the chip's supplement mode), which is by design. A laptop port gives 0.5 A and the symptom is a slow charge and a resetting controller, which looks exactly like a wiring fault.</p>

<h2>4 · The 5 V lane, and the disconnect</h2>
<p><strong>What.</strong> The charger's terminal block + and − to a JST-PH pair, then on to the {a("controller", CONTROLLER)}'s 5V and GND pins. The {a("amp", AMP)}'s VIN taps the same lane; its 220 µF and 100 nF stay at its pins.</p>
<p><strong>Why a JST in the middle.</strong> It is the switch. Flashing firmware means the controller's USB goes in, and the user guide says that and the 5V pin are mutually exclusive. Pull the JST, flash, replug. The slide switch you own is rated for logic, not for an amp's 0.9 A peaks, so the plug pair does the job instead.</p>
<p><strong>Why the amp is unchanged.</strong> On the Phase 1 sheet the amp took 5 V from the controller's 5V pin, which was the USB input. Now that pin is fed by the boost, so the amp is on the boost too. The 6 dB gain strap from Phase 1 is what keeps the amp's peaks inside the boost's 1 A; do not remove it.</p>
<p><strong>What the controller sees.</strong> 5 V from the boost into the board's linear regulator, 3.3 V out. Two conversions in series are about 59 percent efficient to the 3.3 V loads, which is why one 3.4 Wh cell is roughly 10 h with the face lit and far longer with it dark. The controller's regulator is an 800 mA low-dropout part (per the board's schematic, not the 1.1 V-dropout part the earlier notes assumed), so the 5 V rail can sag to about 3.7 V before the 3.3 V rail follows; that is the brownout threshold to scope in Phase 4, and it matters only while the clock is unplugged and the boost runs from the cell.</p>

<h2>5 · The gauge on the chain</h2>
<p><strong>What.</strong> One {a("QT cable", QT)} from the {a("fuel gauge", GAUGE)}'s STEMMA QT to any free port in the Phase 1 chain. That brings 3V3, GND, SDA and SCL. The gauge's VIN pin needs nothing: the chain powers it.</p>
<p><strong>Why GPIO41 is empty.</strong> The pin map reserved GPIO41 for the charger's status line, but the {a("charger board", CHARGER)} does not break out STAT1 or STAT2; it only has LEDs. The firmware reads charging versus discharging from the gauge's charge-rate register instead, which gives the same answer and a number with it.</p>

<h2>Before power, with the meter</h2>
<p>Only what the meter rule allows: polarity, isolation, and a pin order nobody published. No metering of supplier specs.</p>
<ul class="check">
<li>Holder leads, cell in, before the pigtail: red positive against black. Reversed, stop and re-seat the cell.</li>
<li>Pigtail plug against the gauge's + and − pads: red on +. If the pigtail's colours disagree with the housing, swap the pins.</li>
<li>{a("Controller", CONTROLLER)} 5V pin to its GND pin, before the JST goes in: no beep.</li>
<li>Both brass cradles to the 5 V lane, to GND and to the cell leads: open.</li>
<li>Both controller USB sockets: empty.</li>
<li>Then, in order: cell in, USB-C in, green LED, JST to the controller, boot.</li>
</ul>
"""


def sheet_page_html():
    return "\n".join([
        '<title>Cyber Dawn Power Sheet</title>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        style(),
        '<style>figure.sheet{padding:0;margin:0} figure.sheet svg{width:100%;height:auto} .wrap{max-width:1400px} @page{size:letter landscape;margin:7mm} @media print{.masthead,figcaption{display:none} .wrap{padding:0}}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Cyber Dawn &middot; Rev B power wiring</div>',
        '<h1>The power sheet</h1>',
        '<div class="sub">The diagram alone, sized for one landscape Letter page. The explanation of each connection is the companion page, <strong>Cyber Dawn Power</strong>. Rev B 2026-10-31: solar removed, compact body, 16340 cell. Updated 2026-11-08: the sunrise lamp tap at the cell.</div></div>',
        f'<figure class="sheet">{sheet()}<figcaption>Print landscape at actual size. Thick lines are wires you solder or plug. Brass boxes are JST-PH plugs; the brass line is the STEMMA QT chain. A dot is a joint; a hop is a crossing that does not touch. The dashed amp is on the Phase 1 sheet; the dashed wall is the rear panel.</figcaption></figure>',
        '</div>'])


def page_html():
    return "\n".join([
        '<title>Cyber Dawn Power</title>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        style(),
        '<style>figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} .wrap{max-width:1100px}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Cyber Dawn &middot; Rev B power wiring</div>',
        '<h1>The power path, and why</h1>',
        '<div class="sub">One 16340 cell, the charger board, the fuel gauge and the USB-C port on one sheet, an outline of each group, and the owned parts it is built from. Rev B 2026-10-31: solar removed, compact body, 16340 cell. Updated 2026-11-08: the sunrise lamp tap at the cell.<br>Signals are unchanged from the <strong>Phase 1 sheet</strong>; pin numbers are <code>firmware/main/include/board_pins.h</code>; the decisions are <code>docs/COMPACT_DESIGN.md</code>; the reasoning is <code>docs/REVIEW.md</code> §2.1, §4 and §8.2.</div></div>',
        '<div class="note"><span class="lbl">The diagram is its own page</span><p>The one-sheet drawing is published separately as <strong>Cyber Dawn Power Sheet</strong> and printed as <code>docs/pages/print/cyber-dawn-power-sheet.pdf</code>, one landscape Letter page. This page is the explanation, printed portrait as <code>cyber-dawn-power-notes.pdf</code>.</p></div>',
        outline_html(),
        parts_html(),
        '<hr><p class="sub">Built by <code>docs/pages/gen/power_wiring.py</code> from the repository documents named above. Nothing on this page has been built; the charger and gauge behaviour is from Adafruit\'s guides and the TI datasheet, not from hardware.</p>',
        '</div>'])


def print_pdf(html):
    PRINT.mkdir(exist_ok=True)
    sheet_css = ("<style>@page{size:letter landscape;margin:6mm} html,body{background:#fff;margin:0}"
                 ":root{--paper:#fff;--ink:#000;--ink-2:#333;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#eee}"
                 "svg{width:264mm;height:auto;display:block;margin:0 auto}</style>")
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
        shutil.copyfile(s_pdf, PRINT / "cyber-dawn-power-sheet.pdf")
        shutil.copyfile(p_pdf, PRINT / "cyber-dawn-power-notes.pdf")
    for name in ("cyber-dawn-power-sheet.pdf", "cyber-dawn-power-notes.pdf"):
        info = subprocess.run(["pdfinfo", str(PRINT / name)], capture_output=True, text=True).stdout
        print("wrote", PRINT / name, [l for l in info.splitlines() if l.startswith("Pages")])


def main():
    html = page_html()
    OUT.write_text(html)
    SHEET_OUT.write_text(sheet_page_html())
    print("wrote", OUT, OUT.stat().st_size, "and", SHEET_OUT)
    print_pdf(html)


if __name__ == "__main__":
    main()
