"""The parts tray: two Letter sheets with a labelled box per component, to lay the real part on
as you find it. Page 1 is to scale (device parts); page 2 is consumables and tools."""
from __future__ import annotations

import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT_HTML = HERE.parent / "parts-tray.html"
OUT_SVG1 = HERE.parent / "parts-tray-1-letter.svg"
OUT_SVG2 = HERE.parent / "parts-tray-2-letter.svg"

PX = 3.7795   # px per mm at 96 dpi
W, H = 216, 279   # Letter in mm
M = 14            # margin

# (label, sub, w, h, kind)  kind: scale (true size + 4 mm) or box (nominal)
PAGE1 = [
    ("The five modules", [
        ("A1 · ESP32-C3 SuperMini", "USB at the front", 22, 18),
        ("Screen · SSD1306 0.96\"", "SDA·SCL·VCC·GND", 27, 27),
        ("Mic · INMP441", "round, hole up", 14, 14),
        ("Amp · MAX98357A", "pins to the channel", 17, 17),
        ("Speaker · CES-20134", "mesh up", 20, 13),
        ("Button", "legs left / right", 8, 8),
    ]),
    ("Small parts", [
        ("R1 · 4.7 kΩ (or 1 kΩ)", "measured: ____", 14, 8),
        ("R3 · 10 kΩ", "measured: ____", 14, 8),
        ("C1 · 220 µF", "stripe = −", 14, 8),
        ("C2 · 100 nF", "", 10, 8),
    ]),
    ("Power", [
        ("PowerBoost 1000C (copy)", "micro-USB · verify pins", 45, 23),
        ("Cell · 1200 mAh #258", "JST lead, protected", 62, 34),
        ("Slide switch", "", 10, 6),
        ("26 AWG red + black", "2 × 80 mm", 30, 8),
        ("30 AWG", "2 × 60 mm", 30, 8),
    ]),
    ("Stock", [
        ("1.0 mm rod · K&S #9861", "or 18 ga nickel silver (1.02)", 60, 6),
        ("1.5 mm tube · K&S #9831", "or 14 ga nickel silver (frame)", 60, 6),
        ("Cardstock", "jig card, shelf, cradle", 30, 20),
    ]),
]
PAGE2 = [
    ("Consumables", [
        "Kapton tape", "Heat-shrink, thinnest", "63/37 solder", "Chip Quik flux pen", "Solder wick", "400 grit", "91 % IPA", "Hot glue sticks",
    ]),
    ("Tools", [
        "Soldering station", "Electronics tip", "Flush cutters", "Chain-nose pliers", "Round-nose pliers", "Calipers", "Multimeter", "Heat gun",
        "Helping hands", "Tweezers", "Silicone mat", "Hot glue gun", "Printed floor template", "White sheet to work over",
    ]),
]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def sheet(title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W*PX:.1f} {H*PX:.1f}">'
            f'<rect width="100%" height="100%" fill="white"/>'
            f'<text x="{M*PX:.1f}" y="{(M+4)*PX:.1f}" font-size="{4.5*PX:.1f}" font-family="sans-serif" font-weight="bold">{esc(title)}</text>'
            f'<text x="{M*PX:.1f}" y="{(M+9)*PX:.1f}" font-size="{2.8*PX:.1f}" font-family="sans-serif">Lay each part on its box as you find it; tick the corner. Print at Actual size, Letter, black.</text>'
            + body + '</svg>')


def box(x, y, w, h, label, sub, scale=True):
    o = [f'<rect x="{x*PX:.1f}" y="{y*PX:.1f}" width="{w*PX:.1f}" height="{h*PX:.1f}" rx="{1.5*PX:.1f}" fill="none" stroke="black" stroke-width="{0.3*PX:.1f}"' + (' stroke-dasharray="3 2"' if not scale else '') + '/>']
    o.append(f'<rect x="{(x+1)*PX:.1f}" y="{(y+1)*PX:.1f}" width="{3.5*PX:.1f}" height="{3.5*PX:.1f}" fill="none" stroke="black" stroke-width="{0.25*PX:.1f}"/>')
    o.append(f'<text x="{(x+w/2)*PX:.1f}" y="{(y+h+3.6)*PX:.1f}" font-size="{2.6*PX:.1f}" font-family="sans-serif" text-anchor="middle">{esc(label)}</text>')
    if sub:
        o.append(f'<text x="{(x+w/2)*PX:.1f}" y="{(y+h+6.6)*PX:.1f}" font-size="{2.2*PX:.1f}" font-family="sans-serif" fill="#555" text-anchor="middle">{esc(sub)}</text>')
    return "".join(o)


def page1():
    o = []
    y = M + 16
    for group, items in PAGE1:
        o.append(f'<text x="{M*PX:.1f}" y="{y*PX:.1f}" font-size="{3.4*PX:.1f}" font-family="sans-serif" font-weight="bold">{esc(group)}</text>')
        y += 4
        x = M
        rowh = 0
        for label, sub, w, h in items:
            bw, bh = w + 4, h + 4
            if x + bw > W - M:
                x = M; y += rowh + 12; rowh = 0
            o.append(box(x, y, bw, bh, label, sub))
            x += bw + 8
            rowh = max(rowh, bh)
        y += rowh + 16
    return sheet("Pip parts tray · 1 of 2 · the parts that go into the device, boxes 4 mm larger than the part", "".join(o))


def page2():
    o = []
    y = M + 16
    for group, items in PAGE2:
        o.append(f'<text x="{M*PX:.1f}" y="{y*PX:.1f}" font-size="{3.4*PX:.1f}" font-family="sans-serif" font-weight="bold">{esc(group)}</text>')
        y += 4
        x = M
        for label in items:
            bw, bh = 42, 26
            if x + bw > W - M:
                x = M; y += bh + 10
            o.append(box(x, y, bw, bh, label, "", scale=False))
            x += bw + 5
        y += bh + 20
    return sheet("Pip parts tray · 2 of 2 · consumables and tools, boxes not to scale", "".join(o))


def main():
    s1, s2 = page1(), page2()
    OUT_SVG1.write_text(s1); OUT_SVG2.write_text(s2)
    html = ('<title>Parts Tray</title><style>body{margin:0;background:#eee;font-family:sans-serif} .sheet{background:#fff;margin:12px auto;width:216mm;box-shadow:0 1px 6px rgba(0,0,0,.2)} svg{display:block;width:100%;height:auto}'
            ' @media print { body{background:#fff} .sheet{margin:0;box-shadow:none;page-break-after:always} @page{size:letter;margin:0} }</style>'
            f'<div class="sheet">{s1}</div><div class="sheet">{s2}</div>')
    OUT_HTML.write_text(html)
    print("wrote", OUT_HTML, OUT_SVG1, OUT_SVG2)


if __name__ == "__main__":
    main()
