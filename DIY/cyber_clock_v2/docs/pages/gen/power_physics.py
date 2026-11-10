"""Builds docs/pages/cyber-dawn-power-physics.html and docs/pages/print/cyber-dawn-power-physics.pdf:
a light read on the physics and engineering behind Cyber Dawn's power path: energy units, how a
solar cell works (kept as background after solar was removed), Li-ion cells and their limits, CC/CV
charging and the safety timer, the boost and the LDO, capacitors on the rail, why one source at a
time, and what a fuel gauge actually measures. Written for the builder, who asked on 2026-10-26 for
the background to understand why the parts were chosen.

Rev B 2026-10-31: solar removed, compact body, 16340 cell. The numbers now match the Rev B power
sheet: one Nitecore 16340 (3.6 V, 950 mAh, 3.4 Wh, 2 A continuous, protected), 500 mA charge, no panel.
Figures: REVIEW.md, SOLAR_FEASIBILITY.md (superseded, kept as the record), COMPACT_DESIGN.md,
INVENTORY.md, the Adafruit guides for the charger board and the fuel gauge, and Voltaic's page for
the solar panel (background only)."""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wiring_outline import PAGES, PRINT, style  # noqa: E402

OUT = PAGES / "cyber-dawn-power-physics.html"
PDF = PRINT / "cyber-dawn-power-physics.pdf"

SVG_CSS = ("<style>.ax{stroke:var(--ink);stroke-width:1.4;fill:none}.cv{stroke:var(--ink);stroke-width:2.6;fill:none;stroke-linecap:round}"
           ".cv2{stroke:var(--ink-2);stroke-width:2;fill:none;stroke-dasharray:5 4}.g{stroke:var(--line);stroke-width:1;fill:none}"
           ".t{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}.tb{font:700 12.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".m{font:700 12px 'JetBrains Mono',monospace;fill:var(--ink)}.bx{fill:var(--paper);stroke:var(--ink);stroke-width:1.5}"
           ".bxs{fill:var(--brass-soft);stroke:var(--brass);stroke-width:1.4}.w{stroke:var(--ink);stroke-width:2.4;fill:none;stroke-linecap:round;stroke-linejoin:round}"
           ".dot{fill:var(--ink)}.ar{fill:var(--ink)}.sh{fill:var(--signal-soft);stroke:none}</style>")


def fig(svg, cap, w, h):
    return f'<figure><svg viewBox="0 0 {w} {h}" role="img" style="max-width:{int(w*0.72)}px">{SVG_CSS}{svg}</svg><figcaption>{cap}</figcaption></figure>'


def fig_iv():
    # I-V curve of the P105 with the power curve and the MPP, plus the charger's operating window
    o = []
    X0, Y0, XW, YH = 70, 30, 520, 220   # plot box
    o.append(f'<rect x="{X0}" y="{Y0}" width="{XW}" height="{YH}" class="g"/>')
    # x axis volts 0..8, y axis amps 0..1.1
    def px(v): return X0 + v / 8 * XW
    def py(a): return Y0 + YH - a / 1.1 * YH
    for v in range(0, 9):
        o.append(f'<line x1="{px(v)}" y1="{Y0+YH}" x2="{px(v)}" y2="{Y0+YH+5}" class="ax"/><text x="{px(v)}" y="{Y0+YH+19}" class="t" text-anchor="middle">{v}</text>')
    for a in (0.25, 0.5, 0.75, 1.0):
        o.append(f'<line x1="{X0-5}" y1="{py(a)}" x2="{X0}" y2="{py(a)}" class="ax"/><text x="{X0-9}" y="{py(a)+4}" class="t" text-anchor="end">{a}</text>')
    o.append(f'<text x="{X0+XW/2}" y="{Y0+YH+38}" class="tb" text-anchor="middle">panel voltage, V</text>')
    o.append(f'<text x="18" y="{Y0+YH/2}" class="tb" text-anchor="middle" transform="rotate(-90 18 {Y0+YH/2})">panel current, A</text>')
    # charger window 5-7 V shaded
    o.append(f'<rect x="{px(5)}" y="{Y0}" width="{px(7)-px(5)}" height="{YH}" class="sh"/>')
    o.append(f'<text x="{px(6)}" y="{Y0+YH-28}" class="t" text-anchor="middle">charger wants</text><text x="{px(6)}" y="{Y0+YH-13}" class="t" text-anchor="middle">5–7 V</text>')
    # I-V: flat ~1.0 A until knee near 5.5 V, then down to 0 at 7.13 V
    pts = []
    import math
    for i in range(0, 101):
        v = 7.13 * i / 100
        a = 1.0 * (1 - math.exp((v - 7.13) / 0.42)) if v < 7.13 else 0
        pts.append((px(v), py(max(a, 0))))
    o.append('<path d="M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '" class="cv"/>')
    # power curve (scaled: P/6 so 5.75 W -> ~0.96 on the A axis)
    ppts = []
    for i in range(0, 101):
        v = 7.13 * i / 100
        a = 1.0 * (1 - math.exp((v - 7.13) / 0.42))
        ppts.append((px(v), py(max(a, 0) * v / 6.3)))
    o.append('<path d="M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in ppts) + '" class="cv2"/>')
    # MPP marker
    vm, am = 6.12, 0.94
    o.append(f'<circle cx="{px(vm)}" cy="{py(am)}" r="5" class="dot"/>')
    o.append(f'<text x="{px(vm)-12}" y="{py(am)+26}" class="tb" text-anchor="end">max power: 6.1 V × 0.94 A = 5.75 W</text>')
    o.append(f'<text x="{px(0.3)}" y="{py(1.0)+64}" class="t">in full sun the panel is a current source:</text><text x="{px(0.3)}" y="{py(1.0)+79}" class="t">about 1 A whatever the voltage</text>')
    o.append(f'<text x="{px(7.13)+4}" y="{py(0)-6}" class="t">7.1 V open</text>')
    o.append(f'<text x="{px(3.6)}" y="{py(0.42)+2}" class="t">dashed: power = V × I</text>')
    return fig("".join(o), "The 5 W solar panel's current–voltage curve, drawn from Voltaic's numbers. Below the knee the panel gives the same current at any voltage; above it the current collapses. Power peaks at the knee. The charger holds the panel inside the shaded band by refusing to draw more current than the panel can give, which is why no capacitor is needed on the solar input.", 620, 300)


def fig_cells():
    # a panel = cells in series; voltage adds, current doesn't
    o = []
    for i in range(11):
        x = 40 + i * 48
        o.append(f'<rect x="{x}" y="60" width="40" height="40" rx="3" class="bx"/><text x="{x+20}" y="85" class="m" text-anchor="middle">0.6</text>')
        if i < 10:
            o.append(f'<line x1="{x+40}" y1="80" x2="{x+48}" y2="80" class="w"/>')
    o.append('<text x="40" y="44" class="tb">11 silicon cells in series, 0.5–0.65 V each</text>')
    o.append('<line x1="40" y1="118" x2="560" y2="118" class="w"/><polygon points="560,113 572,118 560,123" class="ar"/>')
    o.append('<text x="40" y="140" class="t">voltages add: 11 × 0.65 = 7.1 V open circuit, about 6.1 V under load</text>')
    o.append('<text x="40" y="158" class="t">current does not add: every cell passes the same current, set by light × cell area</text>')
    o.append('<text x="40" y="186" class="tb">one shaded cell</text>')
    o.append('<text x="40" y="204" class="t">chokes the whole string, because the current has to pass through it. A panel wants to be fully lit or fully dark.</text>')
    return fig("".join(o), "Why a \"6 V\" panel is a row of cells. A single silicon cell makes about 0.6 V no matter how big it is; size only sets the current. So a panel's voltage tells you how many cells are in series, and its wattage tells you how much area is behind them.", 620, 220)


def fig_charge():
    # CC/CV charge profile for one 950 mAh 16340 cell at the 500 mA jumper setting, with the 6 h timer far to the right
    o = []
    X0, Y0, XW, YH = 70, 30, 520, 200
    o.append(f'<rect x="{X0}" y="{Y0}" width="{XW}" height="{YH}" class="g"/>')
    def px(h): return X0 + h / 8 * XW
    for h in range(0, 9):
        o.append(f'<line x1="{px(h)}" y1="{Y0+YH}" x2="{px(h)}" y2="{Y0+YH+5}" class="ax"/><text x="{px(h)}" y="{Y0+YH+19}" class="t" text-anchor="middle">{h}</text>')
    o.append(f'<text x="{X0+XW/2}" y="{Y0+YH+38}" class="tb" text-anchor="middle">hours on USB-C, from empty</text>')
    # current: 0.5 A flat to 1.5 h then taper to 0.05 A at 2.5 h
    yI = lambda a: Y0 + YH - a / 0.5 * (YH * 0.8)
    o.append(f'<path d="M{px(0)},{yI(0.5)} L{px(1.5)},{yI(0.5)} C{px(1.9)},{yI(0.38)} {px(2.2)},{yI(0.12)} {px(2.5)},{yI(0.05)}" class="cv"/>')
    o.append(f'<text x="{px(2.8)}" y="{yI(0.5)+42}" class="tb">solid: charge current</text>')
    o.append(f'<text x="{px(2.1)}" y="{yI(0.3)+4}" class="tb">taper</text>')
    # voltage: 3.4 rising to 4.2 at 1.5 h then flat (dashed)
    yV = lambda v: Y0 + YH - (v - 3.0) / 1.4 * (YH * 0.9)
    o.append(f'<path d="M{px(0)},{yV(3.4)} C{px(0.4)},{yV(3.75)} {px(1.0)},{yV(3.9)} {px(1.5)},{yV(4.2)} L{px(8)},{yV(4.2)}" class="cv2"/>')
    o.append(f'<text x="{px(2.8)}" y="{yI(0.5)+60}" class="t">dashed: cell voltage, to 4.20 V</text>')
    o.append(f'<text x="{px(2.5)+6}" y="{yI(0.05)-6}" class="t">done at ~2.5 h</text>')
    # the 6 h timer line, never reached
    o.append(f'<line x1="{px(6)}" y1="{Y0}" x2="{px(6)}" y2="{Y0+YH}" class="ax" stroke-dasharray="2 3"/>')
    o.append(f'<text x="{px(6)+6}" y="{Y0+14}" class="tb">6 h timer</text>')
    o.append(f'<text x="{px(6)+6}" y="{Y0+30}" class="t">never reached</text>')
    return fig("".join(o), "A Li-ion charge has two halves. First the charger pushes a fixed current and the voltage climbs. When the cell reaches 4.20 V the charger holds that voltage and the current tapers off; the charge is done when the current falls to a trickle. At the 500 mA jumper setting one 950 mAh 16340 is full in about 2.5 h, and the charger chip's six-hour clock, which runs through both halves, never gets a say.", 620, 280)


def fig_chain():
    # the energy ladder with efficiencies
    o = []
    boxes = [("USB-C", "5 V"), ("charger", "0.5 A linear"), ("cell", "3.0–4.2 V"), ("boost", "90 %"), ("LDO", "66 %"), ("3.3 V loads", "OLED · MCU")]
    for i, (a, b) in enumerate(boxes):
        x = 20 + i * 100
        o.append(f'<rect x="{x}" y="40" width="88" height="54" rx="6" class="{"bxs" if i in (1, 3, 4) else "bx"}"/>')
        o.append(f'<text x="{x+44}" y="62" class="tb" text-anchor="middle">{a}</text><text x="{x+44}" y="80" class="t" text-anchor="middle">{b}</text>')
        if i < 5:
            o.append(f'<line x1="{x+88}" y1="67" x2="{x+100}" y2="67" class="w"/><polygon points="{x+98},62 {x+106},67 {x+98},72" class="ar"/>')
    o.append('<text x="20" y="128" class="tb">To deliver 165 mW to the OLED:</text>')
    o.append('<text x="20" y="148" class="t">165 mW ÷ 0.66 = 250 mW out of the boost · 250 mW ÷ 0.90 = 278 mW out of the cell. Net 59 %.</text>')
    o.append('<text x="20" y="166" class="t">Two conversions in series multiply their losses. The linear one is the expensive one.</text>')
    o.append('<text x="20" y="196" class="tb">The 5 V amp skips the LDO:</text>')
    o.append('<text x="20" y="214" class="t">it hangs on the boost directly, which is why its 360 mA never passes through the hot regulator.</text>')
    return fig("".join(o), "Where the energy goes. Every box after the cell takes a cut. The boost is a switching converter and keeps about 90 percent; the controller's regulator is a linear part and keeps about 66 percent at 5 V in, 3.3 V out. This chain is what turns a 3.4 Wh cell into roughly 10 h of lit face when the clock is unplugged.", 620, 230)


def fig_boost():
    # boost converter principle
    o = []
    # inductor, switch, diode, cap drawn as a tiny schematic
    o.append('<text x="20" y="28" class="tb">A boost converter in one breath</text>')
    o.append('<line x1="40" y1="80" x2="110" y2="80" class="w"/>')
    o.append('<text x="40" y="70" class="m">3.7 V in</text>')
    # inductor coil
    o.append('<path d="M110,80 a10,10 0 0 1 20,0 a10,10 0 0 1 20,0 a10,10 0 0 1 20,0 a10,10 0 0 1 20,0" class="w"/>')
    o.append('<text x="150" y="62" class="t" text-anchor="middle">inductor</text>')
    o.append('<line x1="190" y1="80" x2="250" y2="80" class="w"/><circle cx="250" cy="80" r="4" class="dot"/>')
    # switch to ground
    o.append('<line x1="250" y1="80" x2="250" y2="110" class="w"/><line x1="250" y1="110" x2="268" y2="134" class="w"/><line x1="250" y1="140" x2="250" y2="160" class="w"/>')
    o.append('<path d="M238,160 L262,160 M242,166 L258,166 M246,172 L254,172" class="ax"/>')
    o.append('<text x="276" y="128" class="t">switch, ~1 MHz</text>')
    # diode to output
    o.append('<line x1="250" y1="80" x2="300" y2="80" class="w"/><polygon points="300,70 320,80 300,90" class="bx"/><line x1="320" y1="70" x2="320" y2="90" class="w"/><line x1="320" y1="80" x2="400" y2="80" class="w"/>')
    o.append('<text x="310" y="62" class="t" text-anchor="middle">diode</text>')
    # cap
    o.append('<circle cx="400" cy="80" r="4" class="dot"/><line x1="400" y1="80" x2="400" y2="110" class="w"/><line x1="386" y1="110" x2="414" y2="110" class="w"/><line x1="386" y1="120" x2="414" y2="120" class="w"/><line x1="400" y1="120" x2="400" y2="160" class="w"/>')
    o.append('<path d="M388,160 L412,160 M392,166 L408,166 M396,172 L404,172" class="ax"/>')
    o.append('<text x="420" y="118" class="t">capacitor</text>')
    o.append('<line x1="400" y1="80" x2="470" y2="80" class="w"/><text x="476" y="84" class="m">5 V out</text>')
    o.append('<text x="20" y="206" class="t">1. Switch closes: current builds in the inductor, energy stored in its magnetic field.</text>')
    o.append('<text x="20" y="224" class="t">2. Switch opens: the field collapses and the inductor shoves that current out through the diode at whatever</text>')
    o.append('<text x="20" y="242" class="t">   voltage it takes, so the capacitor is pumped above the input. Thousands of times a second.</text>')
    o.append('<text x="20" y="268" class="tb">Why it stalls at start-up:</text>')
    o.append('<text x="20" y="286" class="t">the output capacitor starts empty. A load that grabs 1 A instantly looks like a short, the current</text>')
    o.append('<text x="20" y="304" class="t">limit trips, and the voltage never climbs. Under 200 mA it ramps fine. So firmware turns the big</text>')
    o.append('<text x="20" y="322" class="t">loads on after the rail is up.</text>')
    return fig("".join(o), "The boost converter on the charger board. The inductor is the whole trick: it resists changes in current, so when the switch opens the current has to go somewhere, and it goes through the diode into the output at a higher voltage than it came in.", 620, 338)


def fig_discharge():
    # Li-ion discharge curve: why voltage is a poor fuel gauge
    o = []
    X0, Y0, XW, YH = 70, 30, 520, 180
    o.append(f'<rect x="{X0}" y="{Y0}" width="{XW}" height="{YH}" class="g"/>')
    def px(p): return X0 + p / 100 * XW
    def py(v): return Y0 + YH - (v - 2.9) / 1.4 * YH
    for p in (0, 20, 40, 60, 80, 100):
        o.append(f'<line x1="{px(p)}" y1="{Y0+YH}" x2="{px(p)}" y2="{Y0+YH+5}" class="ax"/><text x="{px(p)}" y="{Y0+YH+19}" class="t" text-anchor="middle">{100-p}</text>')
    for v in (3.0, 3.4, 3.8, 4.2):
        o.append(f'<line x1="{X0-5}" y1="{py(v)}" x2="{X0}" y2="{py(v)}" class="ax"/><text x="{X0-9}" y="{py(v)+4}" class="t" text-anchor="end">{v}</text>')
    o.append(f'<text x="{X0+XW/2}" y="{Y0+YH+38}" class="tb" text-anchor="middle">charge remaining, %</text>')
    o.append(f'<text x="18" y="{Y0+YH/2}" class="tb" text-anchor="middle" transform="rotate(-90 18 {Y0+YH/2})">cell voltage, V</text>')
    o.append(f'<path d="M{px(0)},{py(4.2)} C{px(8)},{py(3.95)} {px(15)},{py(3.85)} {px(25)},{py(3.78)} L{px(75)},{py(3.6)} C{px(88)},{py(3.5)} {px(95)},{py(3.3)} {px(100)},{py(3.0)}" class="cv"/>')
    o.append(f'<text x="{px(50)}" y="{py(3.7)-14}" class="tb" text-anchor="middle">the flat middle: 50 % of the charge inside 0.2 V</text>')
    o.append(f'<text x="{px(82)}" y="{py(3.2)}" class="t" text-anchor="end">the knee: warn here</text>')
    o.append(f'<text x="{px(12)}" y="{py(4.2)+12}" class="t">4.2 V full</text>')
    return fig("".join(o), "Why a voltmeter is a bad fuel gauge. Between about 80 and 30 percent the cell barely moves. The fuel gauge reads the same voltage but runs it through a model of the cell, with the slope and the temperature, to turn it into a percentage you can trust to a few percent.", 620, 260)


def body():
    return f"""
<div class="note warn"><span class="lbl">Rev B, 2026-10-31: no solar</span>
<p>The design no longer uses the solar panel. A lit screen is about 0.4 W around the clock, and a window panel at a yield of 0.6 gives about 12 Wh on a good day and far less on most: the budget never closed without the face going dark, which defeats a clock. Cyber Dawn is now a USB-C appliance with one 16340 cell as backup, charged at 500 mA through the charger board's own port. Section 2 stays as background reading on how a solar cell works; the panel is owned stock for another project and nothing on the power sheet connects to it. The record of the sums is <code>docs/SOLAR_FEASIBILITY.md</code>.</p>
</div>

<h2>What this is for</h2>
<p>Cyber Dawn's power path is seven parts and about a dozen wires, and every one of them was chosen because of some piece of physics. This is that physics, in the order the energy flows: USB-C into a charger, into a cell, out through a converter, into the clock. Nothing here needs more than arithmetic. Where a number matters, it is the number on the wiring sheet.</p>

<h2>1 · Energy, power, and the units on the sheet</h2>
<p><strong>Power is a rate; energy is an amount.</strong> A watt is a joule per second. A watt-hour is a watt held for an hour: 3,600 joules. The clock with its face lit averages about 0.4 W, so a day costs 0.4 × 24 = 9.6 Wh. That one number is why the clock is plugged in: a 3.4 Wh cell covers an unplugged evening, not a day.</p>
<p><strong>Volts × amps = watts.</strong> Every rail on the sheet is some voltage carrying some current. The OLED at 3.3 V and 50 mA is 0.165 W. The amp at 5 V and 360 mA is 1.8 W. Current is what heats wires and empties batteries; voltage is what the parts need to run.</p>
<p><strong>Milliamp-hours only mean something next to a voltage.</strong> A "950 mAh" 16340 cell is 0.95 Ah at 3.6 V nominal, so 3.4 Wh. The same 950 mAh at 12 V would be three times the energy. When you compare cells, multiply by the voltage first. The owned spares: the 1200 mAh pack is 4.4 Wh, the 6600 mAh pack 24.4 Wh. Neither is wired.</p>
<p><strong>Nothing is free.</strong> Every conversion between voltages loses a share as heat. Section 5 adds those up. The short version: a watt-hour at the cell becomes about 0.6 Wh at the 3.3 V parts.</p>

<h2>2 · The solar panel: background only</h2>
<p>Nothing in this section is wired in Rev B. It stays because the builder asked for the physics, and because the 5 W panel is in the drawer for a project where the sums do close.</p>
<p><strong>A solar cell is a diode that light pushes backwards.</strong> Silicon is doped so one face has spare electrons and the other has holes; where they meet there is a built-in electric field. A photon with enough energy knocks an electron loose, the field sweeps it to one side, and if a wire connects the faces the electron flows round as current. More light, more electrons, more current. That is the photovoltaic effect, and it is why a panel's <em>current</em> tracks brightness while its <em>voltage</em> barely changes.</p>
<p><strong>Every silicon cell makes about 0.6 V.</strong> That voltage comes from silicon's band gap, not from the cell's size. A postage-stamp cell and a roof cell both sit near 0.6 V; the big one just gives more amps. So a panel's voltage tells you how many cells are wired in series. The <a href="https://www.adafruit.com/product/5367" target="_blank" rel="noopener">5 W solar panel</a> is "6 V" because it is eleven cells in a row: 7.1 V with nothing connected, about 6.1 V when it is working hard.</p>
{fig_cells()}
<p><strong>The current–voltage curve has a knee, and power lives at the knee.</strong> Short the panel and you get its full current at zero volts: no power. Leave it open and you get full voltage at zero current: no power. In between, power is V × I, and it peaks just before the knee. For this panel that is 6.1 V × 0.94 A = 5.75 W. A charger that pulls the panel below the knee is wasting nothing; one that pulls it past the knee makes the current collapse and gets almost nothing.</p>
{fig_iv()}
<p><strong>This is why the charger wants a 5 to 7 V panel.</strong> The chip on the <a href="https://www.adafruit.com/product/6106" target="_blank" rel="noopener">charger board</a> is a linear charger: whatever voltage comes in above what the cell needs, it burns as heat. A 12 V panel would run the chip hot for no gain. A 6 V panel sits just above the 4.2 V cell plus the chip's overhead, so very little is wasted. And the chip watches its input: when the panel voltage starts to sag toward the knee, it backs off its current draw. That is a cheap cousin of the "maximum power point tracking" in big solar installations, and it is why the review kept this chip over the alternatives for a weak, high-impedance source like a window panel.</p>
<p><strong>Why indoors does not work.</strong> Full sun is about 1,000 W per square metre. A bright room is 1 to 5 W per square metre at the panel: a hundred to a thousand times less. The cell voltage stays near 0.6 V so the panel looks alive on a meter, but the current, and so the power, is a rounding error. The panel has to be in sun. That was the whole reason the earlier plan hung it on a cable as a detachable "sail" while the clock and its battery stayed in the shade, and it is half the reason the plan was dropped: a bedside clock does not live in a window.</p>
<p><strong>Why shade on part of the panel is worse than it looks.</strong> The eleven cells are in series, so the same current must pass through all of them. A shaded cell can only pass its own tiny current, and it throttles the string. Half a panel in shadow does not give half the power; it gives nearly none. A panel wants its whole face lit or none of it.</p>
<p><strong>Why ETFE and why these cells.</strong> The panel uses SunPower cells at about 22 percent efficiency, near the top for silicon, laminated under ETFE, a fluoropolymer that stays clear under UV for years. Cheaper panels use epoxy, which yellows, and lower-grade cells. For an experiment any 6 V panel would do; for a panel that lives in a window for years, the lamination is what you are paying for. That is why this one is worth keeping for the next project.</p>

<h2>3 · The battery</h2>
<p><strong>A lithium-ion cell is a shuttle.</strong> Lithium ions sit in a metal-oxide crystal on one side and a graphite lattice on the other, with an electrolyte between that lets ions through but not electrons. Charging drives ions into the graphite; discharging lets them flow back, and the electrons they leave behind go round the outside through your circuit. The voltage between the two sides is about 3.7 V in the middle of the shuttle's travel, 4.2 V when the graphite is full, 3.0 V when it is empty.</p>
<p><strong>The 4.2 V ceiling is a hard limit.</strong> Push past it and lithium starts plating out as metal on the graphite instead of slotting in. Metal lithium is reactive, grows in needles, and can short the cell from the inside; that is the mechanism behind every lithium battery fire. Chargers hold 4.20 V to within a few hundredths of a volt for this reason, and the protection circuit in the cell's button top cuts the cell off if a charger misbehaves.</p>
<p><strong>The 3.0 V floor is a slow death instead of a fast one.</strong> Below about 2.5 V the copper current collector begins to dissolve into the electrolyte; recharge it and the copper plates back as a short. The protection circuit in the 16340's button top opens near that floor and the gauge warns well before it. Store cells half full, not empty.</p>
<p><strong>C-rate is "how fast, relative to size".</strong> 1C means charging or discharging the whole capacity in one hour. The charger's 500 mA jumper setting into the 950 mAh cell is about 0.5C, gentle; the board's default 1 A would be about 1C, and Nitecore publishes no maximum charge current for the cell, which is why the jumper is set. On the way out, the cell is rated 2 A continuous; the boost's full 1 A at 5 V is about 1.5 A from a cell at 3.6 V, inside the rating, and only a Wi-Fi burst landing on a bass peak, which the firmware avoids while unplugged, would ask for more for a millisecond. Heat inside a cell goes up with the square of the current, so halving the rate quarters the heating.</p>
<p><strong>Parallel adds capacity, series adds voltage.</strong> The clock runs on one can: 3.6 V, 950 mAh. The owned 6600 mAh spare pack is three 2200 mAh 18650 cans in parallel, still 3.7 V, three times the charge; cells in parallel share current naturally because any cell that is fuller has a slightly higher voltage and gives a little more. A series stack would be 11.1 V and would need a balancer. Nothing in this clock is in series or in parallel.</p>
{fig_discharge()}
<p><strong>What "protected" buys, and what it does not.</strong> The 16340's button top hides a small board that opens the cell on over-charge, over-discharge and short circuit. It is a last line, not a charger: it does not watch temperature, so that rule moves to you. Keep the holder away from the controller's regulator and the amp, and charge it in a room, not a car. Lithium charges badly below 0 °C and ages fast above 45 °C. The holder sits in the top layer under the lid, the warm parts sit below on the speaker, which is the right way up.</p>

<h2>4 · Charging, and the six-hour clock</h2>
<p><strong>Constant current, then constant voltage.</strong> A charger pushes a fixed current while the cell voltage climbs. The moment the cell touches 4.20 V the charger switches to holding that voltage, and the current tapers as the last ions find their slots. The charge is "done" when the current drops to a tenth of the set rate. The first phase delivers about 80 percent of the capacity; the taper is slow and delivers the rest.</p>
{fig_charge()}
<p><strong>Why the timer exists.</strong> A cell that has been damaged can sit forever in the taper, drawing current and never terminating, slowly heating. A safety timer caps how long a charge may run. On the <a href="https://www.adafruit.com/product/6106" target="_blank" rel="noopener">charger board</a>'s chip that cap is six hours and it is fixed in the silicon, not a setting. If it ever fires, the charger latches a fault, the red F and orange C LEDs both come on, and it will not charge again until its input power is cycled: unplug, replug. The clock keeps running from USB through all of this; only the top-up stops.</p>
<p><strong>Why it never bites here.</strong> At 500 mA into 950 mAh the first phase is about 1.5 h and the taper about an hour: full from empty in about 2.5 h, less than half the window. It was a real problem in the earlier plan, where a 6600 mAh pack at 1 A needed 6.3 to 7.7 h and would have been cut off during the taper. One small cell made the problem go away, and the solar trick that was going to rescue it, a fresh timer every sunrise, is no longer needed.</p>
<p><strong>Power path: the load first, the cell second.</strong> When USB-C is present the chip feeds the clock from the input and sends only the surplus to the cell. Without this, every milliamp the clock drew would be a tiny discharge–recharge cycle on the cell. Lithium cells are good for a few hundred full cycles; shallow cycles count less, but they add up over years. The power path is what lets the cell sit full and idle most of its life, which for a plugged-in clock is nearly all of it.</p>
<p><strong>One charger per cell.</strong> Two chargers on one cell each see the other's voltage and misread the cell; one may keep pushing after the other has stopped. The cell's holder leads go, through the owned JST-PH pigtail, into the <a href="https://www.adafruit.com/product/5580" target="_blank" rel="noopener">fuel gauge</a>, the gauge into the charger board, and nothing else. A cell may visit the external Nitecore charger, but only after it has left the holder.</p>

<h2>5 · Converters: the boost and the regulator</h2>
<p><strong>The <a href="https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894" target="_blank" rel="noopener">controller</a> wants 5 V, the cell gives 3.0 to 4.2 V.</strong> Something has to raise the voltage. The <a href="https://www.adafruit.com/product/6106" target="_blank" rel="noopener">charger board</a> carries a boost converter for exactly this.</p>
{fig_boost()}
<p><strong>Switching converters are efficient because nothing in them is meant to get hot.</strong> A switch is either fully on (no voltage across it) or fully off (no current through it), and an inductor and capacitor store energy without burning it. The losses are the small resistances along the way and the diode's forward drop. Ninety percent is typical; the other ten percent is why the board gets warm at 1 A.</p>
<p><strong>The controller's own regulator is the opposite kind.</strong> It is a linear regulator: a transistor that drops 5 V to 3.3 V by acting as a variable resistor. The 1.7 V it removes multiplied by the current it passes is pure heat. At 300 mA that is half a watt in a part the size of a fingernail, which is why it is the hottest thing on the board and why the review says nothing else may hang on the 3V3 pin. It needs only about 0.3 V of headroom at this load (it is an 800 mA low-dropout part, per the controller board's schematic): if the 5 V rail dips below about 3.7 V, the 3.3 V rail falls with it and the controller resets. That dip is what Phase 4's oscilloscope test looks for during a bass note.</p>
{fig_chain()}
<p><strong>Why the amp bypasses the regulator.</strong> The amplifier sits on the 5 V rail directly. Its 360 mA average and 0.9 A peaks would cook the regulator and sag the 3.3 V rail; on 5 V they are the boost's problem, and the boost is rated for 1 A. The 6 dB gain strap from the Phase 1 sheet is what keeps those peaks under 1 A. A 9 dB setting would ask for 1.3 A, which the boost cannot give, and the result is a brownout that sounds like a crackle.</p>

<h2>6 · Capacitors on the rail</h2>
<p><strong>A capacitor is a bucket next to the tap.</strong> A boost converter answers a change in load in tens of microseconds; a bass note or a Wi-Fi transmit burst asks for hundreds of milliamps in less than one. For that first microsecond the current has to come from charge already stored nearby. The 220 µF electrolytic at the amp holds enough to cover a note; the 100 nF ceramic beside it answers the fastest spikes the electrolytic is too slow for.</p>
<p><strong>Why "at the pins".</strong> Every centimetre of wire is a small inductor, and an inductor resists a sudden change in current, which is exactly the thing the capacitor is there to supply. A capacitor ten centimetres from the amp is a capacitor with a speed limit. Solder them across the amp's own VIN and GND.</p>

<h2>7 · One source at a time</h2>
<p><strong>Two supplies on one piece of copper fight.</strong> If the <a href="https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894" target="_blank" rel="noopener">controller</a>'s USB socket and its 5V pin are both driven, two regulators are each trying to hold the same rail at their idea of 5 V. The one set a little higher sources all the current, the other sees current pushed backwards into its output, and depending on the part that is anywhere from harmless to fatal. Espressif's guide calls the USB ports, the 5V pin and the 3V3 pin "three mutually exclusive ways to provide power", which is the polite form of the same warning.</p>
<p><strong>The JST plug in the 5 V lane is a switch you cannot leave in the wrong position.</strong> To flash firmware you need the controller's USB; so the rule is pull the plug, flash, replug. The slide switch you own is rated for logic signals, not the amp's peaks, which is why it carries the arm input and not the rail.</p>
<p><strong>The charger is the one place two sources were allowed to meet.</strong> The <a href="https://www.adafruit.com/product/6106" target="_blank" rel="noopener">charger board</a> has two inputs, USB-C and the VIN pad, and chooses between them through two diodes: a designed junction. In Rev B only USB-C is used and the VIN pad stays empty, so the choice never comes up. The controller's 5V pin is not a designed junction, which is the whole point of the rule.</p>

<h2>8 · The fuel gauge</h2>
<p><strong>It is a voltmeter with a brain.</strong> The <a href="https://www.adafruit.com/product/5580" target="_blank" rel="noopener">fuel gauge</a> measures the cell voltage to a millivolt and runs it through a stored model of how a lithium cell's voltage relates to its charge, including the slope of the curve and how the cell is being loaded. The output is a percentage good to a few percent over most of the range, where a plain voltmeter would be ten or twenty percent off in the flat middle.</p>
<p><strong>Why it sits between the cell and the charger.</strong> Its two JST ports are wired together; the cell's current passes straight through and the gauge just listens across them. There is no shunt resistor and nothing to burn. Its report arrives over I²C at address 0x36, the same two wires every other sensor on the clock already shares.</p>
<p><strong>What the firmware does with it.</strong> The low-battery warning, the alarm reserve, and the plain battery gauge on the display all come from this one number. The charge-rate register, percent per hour, also tells the firmware whether the cell is charging or draining, which is why the charger's missing status pad does not matter.</p>

<h2>9 · Things to know, in one place</h2>
<div class="tw"><table>
<tr><th>Number</th><th>What it is</th><th>Why it is on the sheet</th></tr>
<tr><td class="m">4.20 V</td><td>Full Li-ion cell</td><td>Above it, lithium plates as metal. The charger and the cell's protection both enforce it; a protected 16340 terminates here, so the charger's profile fits unchanged.</td></tr>
<tr><td class="m">3.0 V</td><td>Empty Li-ion cell</td><td>The cell's protection opens near here. The gauge warns before.</td></tr>
<tr><td class="m">3.6 V · 950 mAh</td><td>One Nitecore 16340 cell</td><td>3.4 Wh. Roughly 10 h of lit face unplugged, far longer dark. Its job is to ride through unplugs and keep the alarm armed.</td></tr>
<tr><td class="m">500 mA · 0.5C</td><td>Charge current, the jumper on the charger's back</td><td>Gentle. The board's default 1 A would be about 1C, and Nitecore publishes no maximum.</td></tr>
<tr><td class="m">2.5 h</td><td>Full from empty</td><td>About 1.5 h of constant current, then the taper.</td></tr>
<tr><td class="m">6 h</td><td>Charger safety timer</td><td>Fixed in silicon. Never reached at 500 mA into 950 mAh. If it fires, red F and orange C light together; unplug and replug USB-C.</td></tr>
<tr><td class="m">2 A</td><td>The cell's continuous discharge rating</td><td>The boost's full 1 A at 5 V is about 1.5 A from the cell at 3.6 V, inside the rating; the firmware keeps the radio quiet while the amp plays unplugged.</td></tr>
<tr><td class="m">200 mA</td><td>Boost start-up limit</td><td>Loads above it at the instant of power-up stall the converter. Firmware sequences the OLED, radio and amp on after.</td></tr>
<tr><td class="m">3.7 V</td><td>Brownout threshold on the 5 V rail</td><td>The controller's linear regulator needs about 0.3 V of headroom (0.45 V worst case at its full 800 mA). Below this, the controller resets. Matters only while unplugged, when the boost runs from the cell.</td></tr>
<tr><td class="m">59 %</td><td>Cell to 3.3 V efficiency</td><td>Boost (90 %) × linear regulator (66 %). Why 3.4 Wh is hours, not days.</td></tr>
<tr><td class="m">1 A</td><td>Boost output rating</td><td>The 6 dB amp strap keeps audio peaks under it.</td></tr>
<tr><td class="m">0x36</td><td>Fuel gauge I²C address</td><td>One more board on the chain; no new wires.</td></tr>
<tr><td class="m">0 V</td><td>The charger's solar / DC input</td><td>Nothing wired. The 5 W panel is owned stock for another project.</td></tr>
</table></div>

<h2>The parts these ideas live in</h2>
<div class="tw"><table>
<tr><th>Idea</th><th>Part</th></tr>
<tr><td>Linear charging, the 500 mA jumper, the 6 h timer, power path, the boost</td><td><a href="https://www.adafruit.com/product/6106" target="_blank" rel="noopener">charger board with 5 V boost</a> (owned), fed over USB-C through its own port; its solar / DC input stays empty</td></tr>
<tr><td>One can, 4.2 V ceiling, protection in the button top, C-rate</td><td>One Nitecore 16340 cell, 3.6 V 950 mAh protected (owned ×6), in the <a href="https://www.amazon.com/dp/B0CRGK889F" target="_blank" rel="noopener">16340 holder with leads</a> (owned)</td></tr>
<tr><td>The plug you cannot leave in the wrong position</td><td>The owned JST-PH pigtails: one into the fuel gauge, one pair as the disconnect in the 5 V lane</td></tr>
<tr><td>Voltage-plus-model state of charge</td><td><a href="https://www.adafruit.com/product/5580" target="_blank" rel="noopener">fuel gauge</a> (owned)</td></tr>
<tr><td>The linear regulator and the 3.7 V brownout</td><td>The linear regulator on the <a href="https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894" target="_blank" rel="noopener">controller board</a> (owned)</td></tr>
<tr><td>The bucket next to the tap</td><td>220 µF from the ALLECIN kit and 100 nF from the BOJACK kit (owned)</td></tr>
<tr><td>Photovoltaic cells in series, the knee, ETFE (section 2, background only)</td><td><a href="https://www.adafruit.com/product/5367" target="_blank" rel="noopener">5 W solar panel</a>, with the <a href="https://www.adafruit.com/product/4287" target="_blank" rel="noopener">DC jack adapter</a> and the <a href="https://www.adafruit.com/product/368" target="_blank" rel="noopener">DC jack to screw terminals</a>: owned, not wired in Rev B</td></tr>
<tr><td>Cells in parallel (section 3, as a contrast)</td><td>The <a href="https://www.adafruit.com/product/353" target="_blank" rel="noopener">6600 mAh battery</a>: owned spare, not wired in Rev B</td></tr>
</table></div>
<p>The two fundamentals pages in the Pocket AI project, <em>Resistors and Rules</em> and <em>The Pin Switchboard</em>, cover the logic side: pull-ups, open-drain outputs and what a GPIO is. Together with this page they are the whole background the Cyber Dawn sheets assume.</p>
"""


def page_html():
    return "\n".join([
        '<title>Cyber Dawn Power Physics</title>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        style(),
        '<style>.wrap{max-width:900px} figure svg{width:100%} h2{margin-top:30px}</style>',
        '<div class="wrap">',
        '<div class="masthead"><div class="eyebrow">Cyber Dawn &middot; background reading</div>',
        '<h1>The physics behind the power path</h1>',
        '<div class="sub">USB-C to charger to cell to converter to clock: what each part is doing and why it was built that way. A light read to go with the <strong>Cyber Dawn Power Sheet</strong>. Rev B 2026-10-31: solar removed, compact body, 16340 cell; the solar-cell physics stays as background.</div></div>',
        body(),
        '<hr><p class="sub">Built by <code>docs/pages/gen/power_physics.py</code>. Numbers are from <code>docs/REVIEW.md</code>, <code>docs/COMPACT_DESIGN.md</code>, <code>docs/INVENTORY.md</code>, <code>docs/SOLAR_FEASIBILITY.md</code> (superseded 2026-10-31, kept as the record), Voltaic\'s page for the solar panel and the Adafruit guides for the charger board and the fuel gauge. The curves are drawn to those numbers, not measured on hardware.</p>',
        '</div>'])


def print_pdf(html):
    PRINT.mkdir(exist_ok=True)
    page_css = ("<style>@page{size:letter;margin:13mm 14mm 15mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#eaeaea;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:10pt!important;line-height:1.42} .wrap{max-width:none;padding:0}"
                "h2{font-size:14pt;margin-top:14pt;page-break-after:avoid} p{max-width:none;margin:6pt 0} figure{margin:8pt auto;padding:6pt;width:72%;break-inside:avoid;border:none} figure svg{width:100%}"
                "figcaption{font-size:8.5pt;line-height:1.35} table{font-size:8.5pt} th,td{padding:3pt 5pt} tr{break-inside:avoid}"
                "a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt}</style>")
    with tempfile.TemporaryDirectory() as d:
        p_html = pathlib.Path(d) / "p.html"
        p_html.write_text("<!doctype html><meta charset=utf-8>" + html.replace("</style>", "</style>" + page_css, 1))
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={PDF}", f"file://{p_html}"], check=True, capture_output=True, timeout=180)
    info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
    print("wrote", PDF, [l for l in info.splitlines() if l.startswith("Pages")])


def main():
    html = page_html()
    OUT.write_text(html)
    print("wrote", OUT, OUT.stat().st_size)
    print_pdf(html)


if __name__ == "__main__":
    main()
