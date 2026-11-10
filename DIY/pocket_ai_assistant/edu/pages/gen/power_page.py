"""Builds edu/pages/final-build-power.html: the battery version of Pip, wiring and charging."""
from __future__ import annotations

import pathlib
import re

from harness_page import a, L

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "final-build-power.html"
HARNESS = "https://claude.ai/artifact/FAsL4WPArRK6QW7yEg2Nix"
NETLIST = "https://claude.ai/artifact/3vPVU2PCtftqR1CwzJJFiM"

L.update({
    "powerboost": ("https://www.adafruit.com/product/2465", "Adafruit PowerBoost 1000C"),
    "cell1200": ("https://www.adafruit.com/product/258", "Adafruit #258, 1200 mAh"),
    "cell500": ("https://www.adafruit.com/product/1578", "Adafruit #1578, 500 mAh"),
    "charger4410": ("https://www.adafruit.com/product/4410", "Adafruit #4410 Micro-Lipo"),
    "switch": ("https://www.amazon.com/dp/B09R434VJQ", "Chanzon slide switch"),
    "wire26": ("https://www.amazon.com/dp/B07G2LRX68", "TUOFENG 26 AWG wire"),
})


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, cls="s", anchor="start"):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(s)}</text>'


def box(x, y, w, h, cls="box", rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>'


def line(x1, y1, x2, y2, color, w=3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{d}/>'


def dot(x, y, cls="joint"):
    return f'<circle cx="{x}" cy="{y}" r="4.5" class="{cls}"/>'


def fig_power():
    o = [T(20, 24, "Power, final build: one board owns it", "t b")]
    # charge cable
    o.append(box(20, 70, 110, 44, "box"))
    o.append(T(75, 88, "USB charger", "s b", "middle")); o.append(T(75, 104, "any 5 V USB", "s muted", "middle"))
    o.append(line(130, 92, 190, 92, "var(--w-red)", 4)); o.append(T(160, 84, "5 V in", "s", "middle"))
    # powerboost
    o.append(box(190, 40, 250, 180, "acc-fill", 8))
    o.append(T(315, 62, "PowerBoost 1000C", "t b", "middle"))
    o.append(T(315, 78, "charger + load sharing + 5 V boost", "s muted", "middle"))
    o.append(box(205, 95, 100, 40, "box", 4)); o.append(T(255, 113, "charger", "s b", "middle")); o.append(T(255, 127, "1 A to the cell", "s muted", "middle"))
    o.append(box(325, 95, 100, 40, "box", 4)); o.append(T(375, 113, "boost", "s b", "middle")); o.append(T(375, 127, "cell → 5.2 V", "s muted", "middle"))
    o.append(line(305, 115, 325, 115, "var(--w-red)", 3))
    o.append(T(315, 160, "EN", "s m", "middle")); o.append(T(315, 176, "pull to GND = off", "s muted", "middle"))
    o.append(T(230, 160, "BAT", "s m", "middle")); o.append(T(400, 160, "5V · GND", "s m", "middle"))
    o.append(T(230, 200, "LBO", "s m", "middle")); o.append(T(230, 212, "low-battery flag", "s muted", "middle"))
    # cell
    o.append(box(40, 160, 110, 70, "cap", 8))
    o.append(T(95, 185, "1200 mAh cell", "s b", "middle")); o.append(T(95, 201, "3.7 V, protected", "s muted", "middle")); o.append(T(95, 217, "JST-PH plug", "s muted", "middle"))
    o.append(line(150, 190, 230, 190, "var(--w-red)", 3)); o.append(line(150, 198, 230, 198, "var(--w-black)", 3))
    o.append(line(230, 165, 230, 190, "var(--w-red)", 3))
    # switch
    o.append(box(280, 240, 70, 36, "box", 4)); o.append(T(315, 255, "slide", "s b", "middle")); o.append(T(315, 269, "switch", "s b", "middle"))
    o.append(line(315, 182, 315, 240, "var(--w-purple)", 3)); o.append(line(350, 258, 400, 258, "var(--w-black)", 3)); o.append(T(405, 262, "GND", "s m"))
    # 5V out to the harness
    o.append(line(440, 150, 520, 150, "var(--w-red)", 4)); o.append(line(440, 168, 520, 168, "var(--w-black)", 4))
    o.append(T(480, 142, "5 V", "s b", "middle")); o.append(T(480, 184, "GND", "s b", "middle"))
    # harness block
    o.append(box(520, 40, 220, 240, "pcb", 8))
    o.append(T(630, 64, "The harness, unchanged", "t b", "middle"))
    o.append(T(630, 80, "every rod as on the harness page", "s muted", "middle"))
    o.append(box(540, 110, 80, 50, "box", 4)); o.append(T(580, 130, "A1", "s b", "middle")); o.append(T(580, 146, "5V stub", "s m", "middle"))
    o.append(box(650, 110, 80, 50, "box", 4)); o.append(T(690, 130, "amp", "s b", "middle")); o.append(T(690, 146, "VIN stub", "s m", "middle"))
    o.append(line(520, 150, 560, 150, "var(--w-red)", 4)); o.append(dot(560, 150))
    o.append(line(600, 150, 650, 150, "var(--w-red)", 4)); o.append(T(625, 142, "5 V rod", "s", "middle"))
    o.append(line(520, 168, 580, 168, "var(--w-black)", 4)); o.append(dot(580, 160)); o.append(line(580, 168, 580, 210, "var(--w-black)", 3)); o.append(line(560, 210, 720, 210, "var(--w-black)", 5))
    o.append(T(640, 226, "GND rail, fed from A1's GND stub", "s b", "middle"))
    o.append(box(540, 240, 80, 30, "warn-fill", 4)); o.append(T(580, 259, "A1 USB: blocked", "s b warn-ink", "middle"))
    # LBO to GPIO6 optional
    o.append(line(230, 220, 230, 300, "var(--w-teal)", 2, "5 4")); o.append(line(230, 300, 650, 300, "var(--w-teal)", 2, "5 4")); o.append(line(650, 300, 650, 280, "var(--w-teal)", 2, "5 4"))
    o.append(T(440, 294, "LBO → A1 GPIO6 (later: a low-battery face)", "s muted", "middle"))
    return f'<svg viewBox="0 0 760 320" role="img" aria-label="Power architecture of the final build">{"".join(o)}</svg>'


def fig_storeys():
    o = [T(20, 24, "Side view from the front: three storeys in a frame 68 × 42 × 38 outside", "t b")]
    X0, W = 60, 520
    def st(y, h, cls, lab, sub):
        return box(X0, y, W, h, cls, 3) + T(X0 + W / 2, y + h / 2 + 4, lab, "s b", "middle") + T(X0 + W + 14, y + h / 2 + 4, sub, "s muted")
    o.append(f'<rect x="{X0-8}" y="40" width="{W+16}" height="260" class="frame" rx="4"/>')
    o.append(st(52, 120, "pcb", "the harness, 16 mm: A1, amp, mic, screen floating on its rods", "storey 3 · 16 mm"))
    o.append(st(180, 24, "box", "a card shelf with the PowerBoost lying on it, 45 × 23 × 10, USB port to the side", "storey 2 · 11 mm"))
    o.append(st(212, 50, "cap", "the 1200 mAh cell, 62 × 34 × 5, in a cardstock cradle, nothing pressing on it", "storey 1 · 6 mm"))
    o.append(T(X0, 290, "inside 65 × 39 × 35 · Kapton on every tube · the cell never touches brass, solder or the iron", "s warn-ink"))
    return f'<svg viewBox="0 0 760 310" role="img" aria-label="Three storeys">{"".join(o)}</svg>'


def main():
    H = ['<title>Final Build Power</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style(), '<style>figure svg .acc-fill { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.4; } figure svg .warn-fill { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1.2; }</style>', '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · final build · battery, charging, the frame around it</div>',
         '<h1>Pip on a battery: the final wiring</h1>',
         f'<p class="lede">The harness does not change. Battery power is one extra board that owns the 5 V, one cell, one switch and one charge port, feeding the same two points the USB socket fed: A1\'s 5V stub and, through the 5 V rod, the amp\'s VIN. Every other rod is the one on the <a href="{HARNESS}" target="_blank" rel="noopener">harness page</a> and the <a href="{NETLIST}" target="_blank" rel="noopener">net list</a>.</p>']

    H.append('<div class="callout"><span class="label">Four rules that replace "USB only"</span><ul>'
             '<li><strong>One source at a time.</strong> A1\'s own USB port is blocked in this build. To flash, switch the PowerBoost off first, then plug A1 in; unplug before switching back on.</li>'
             '<li><strong>Only the PowerBoost touches the cell.</strong> Never a wire soldered to it, never the brass, never the iron within 10 cm of it. It plugs in by its JST and unplugs the same way.</li>'
             '<li><strong>Only the 1200 mAh cell.</strong> The 500 mAh is rated 0.5 A and this device peaks above that; the PowerBoost also charges at 1 A, which is right for 1200 and too much for 500.</li>'
             '<li><strong>Everything from the harness page still holds:</strong> OUT+/OUT− never to GND or the frame; the frame carries nothing; the amp\'s cap stays at 45.</li></ul></div>')

    H.append('<h2>The wiring</h2>')
    H.append(f'<figure><div class="scroll">{fig_power()}</div><figcaption><strong>Two wires into the harness, two into the switch, one JST to the cell, one cable to charge.</strong> The PowerBoost charges the cell from its USB port and feeds the device at the same time (load sharing); with no cable it boosts the cell to 5.2 V. EN pulled to ground turns the output off: that is the on/off switch.</figcaption></figure>')
    H.append('<div class="scrollx"><table class="t"><tr><th>From</th><th>To</th><th>With</th><th>Note</th></tr>'
             f'<tr><td>PowerBoost <code>5V</code></td><td>A1\'s 5V stub</td><td>26 AWG red, {a("wire26", "TUOFENG")}, 40–60 mm</td><td>the 5 V rod carries it on to amp VIN as before; the 220 µF stays where it is</td></tr>'
             '<tr><td>PowerBoost <code>GND</code></td><td>A1\'s GND stub</td><td>26 AWG black</td><td>the star point: the supply\'s ground meets A1\'s and the amp\'s there, and the rail stays a dead end</td></tr>'
             f'<tr><td>PowerBoost <code>EN</code></td><td>one side of the {a("switch", "slide switch")}</td><td>30 AWG</td><td>other side of the switch to PowerBoost GND. Switch closed = EN at ground = off</td></tr>'
             f'<tr><td>PowerBoost JST</td><td>{a("cell1200", "1200 mAh cell")} JST-PH plug</td><td>the cell\'s own lead</td><td>meter the polarity on the board\'s silkscreen before the first plug-in: red to +, black to −</td></tr>'
             '<tr><td>PowerBoost USB port</td><td>the front or side opening</td><td>—</td><td>this is the only port the finished device shows</td></tr>'
             '<tr><td>PowerBoost <code>LBO</code></td><td>A1 GPIO6 (optional)</td><td>30 AWG</td><td>goes low at 3.2 V; the firmware can show a low-battery face. Not needed to run</td></tr>'
             '<tr><td>A1 USB-C</td><td>nothing</td><td>a square of Kapton over the opening</td><td>flashing only, with the switch off</td></tr>'
             '</table></div>')

    H.append('<h3>Why each pin</h3><ul>'
             '<li><strong>5V to A1\'s 5V stub.</strong> That stub is where USB power used to enter, so every rod downstream sees the same 5 V it always did.</li>'
             '<li><strong>GND to A1\'s GND stub, and nowhere else.</strong> One ground meeting point means no loop for the amp\'s current to run through the signal rods.</li>'
             '<li><strong>EN through the switch to GND.</strong> EN is a logic input that draws microamps, so the small slide switch controls the whole load without carrying its current.</li>'
             '<li><strong>JST, not wires, to the cell.</strong> The cell\'s lead is factory-terminated and keyed; the board\'s charger and protection are the only things that ever touch it.</li>'
             '<li><strong>LBO to GPIO6.</strong> An open-drain flag that goes low at 3.2 V; a free GPIO reads it so the face can warn before the cell cuts out.</li>'
             '<li><strong>A1 USB-C blocked.</strong> On A1 the 5V stub is the USB VBUS node with no diode, so a cable there would fight the PowerBoost\'s output.</li>'
             '</ul>')

    H.append('<h2>How it charges</h2>')
    H.append('<ul>'
             '<li><strong>Plug any USB charger into the PowerBoost\'s port.</strong> Yellow LED: charging. Green: full. About 1½ hours from empty at 1 A.</li>'
             '<li><strong>The device may stay on while charging.</strong> Load sharing runs Pip from the cable and charges the cell with what is left. Switch off and it charges a little faster.</li>'
             '<li><strong>Unplug and it runs on the cell:</strong> about 5 hours of talking, longer idle (A1 with Wi-Fi 100–300 mA at 5 V, the amp at cap 45 another 100 mA in bursts; 1200 mAh through the boost gives roughly 4 Wh usable).</li>'
             '<li><strong>Red LED: low battery.</strong> Charge it; the cell\'s own protection cuts off at 3.0 V before any harm.</li>'
             f'<li><strong>The {a("charger4410", "#4410 charger")} you own is not used</strong> in the device. It stays a bench charger for a cell on its own.</li>'
             '</ul>')

    H.append('<h2>Where it all goes</h2>')
    H.append(f'<figure><div class="scroll">{fig_storeys()}</div><figcaption><strong>The cell is 62 mm long and the current frame is 57 inside, so the battery build gets the new frame</strong>: 68 × 42 × 38 outside, inside 65 × 39 × 35. The cell lies on the bottom in a cardstock cradle; a card shelf above it carries the PowerBoost flat, its USB port at the side opening; the harness sits on top exactly as built. The silver wire you bought is for this frame: two loops of 14 ga at 65 × 39 inside, four posts of 35.</figcaption></figure>')

    H.append('<h2>What to buy</h2>')
    H.append(f'<ul><li>Nothing, since 2026-10-14: the board on the bench is a third-party copy of the {a("powerboost")} sold as <a href="https://www.amazon.com/dp/B0G5PXGVG9" target="_blank" rel="noopener">"For Powerboost 1000 Charger … 2465 Module"</a> (Amazon #20). Same chips and pin names are claimed, not proven: the <a href="https://claude.ai/artifact/6kZ6h285bMka6wo8bbLfyp" target="_blank" rel="noopener">real test</a> is what turns the labels on its silkscreen into facts, and its listing warns the charger chip runs hot (~75 °C) while charging.</li>'
             f'<li>Owned already: the {a("cell1200", "1200 mAh cell")}, the {a("switch", "slide switch")}, {a("wire26", "26 AWG wire")}, Kapton, cardstock, the silver wire for the frame.</li></ul>')

    H.append('<h2>Order of work</h2>')
    H.append('<ol><li>Finish the brass harness on USB and make it work (the harness page). Nothing here starts before that.</li>'
             '<li>Bench-test the PowerBoost alone: cell in, switch, meter 5.2 V on its output, charge it once, watch the LEDs.</li>'
             '<li>Bend and solder the silver frame to the new size.</li>'
             '<li>Cradle, shelf, PowerBoost, two wires up into the harness, switch, Kapton over A1\'s port.</li>'
             '<li>Meter sweep (frame to everything: silent), switch on, the same tests as move 11.</li></ol>')

    H.append('<div class="evidence"><p><strong>Sources.</strong> PowerBoost 1000C functions and pins from Adafruit\'s product page (MCP73871 charger with load sharing, TPS61090 boost, EN, LBO, 1 A charge); cell sizes and ratings from <code>docs/INVENTORY.md</code> and the September materials review (500 mAh rejected for its 0.5 A rating); the harness from the generated model. Runtime is an estimate from typical ESP32-C3 and MAX98357A currents, not a measurement. Nothing on this page has been built.</p></div>')
    H.append('</div>')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
