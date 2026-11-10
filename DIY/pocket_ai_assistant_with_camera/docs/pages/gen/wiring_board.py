"""Builds the Pocket AI with Camera wiring page and its Markdown companions from one source of truth.

Writes
  docs/pages/wiring-board.html            the page (sheet + tower figure + outline + checks + parts)
  docs/pages/print/wiring-board.pdf       sheet landscape first, then the notes portrait, Letter, black only
  docs/pages/print/wiring-board-sheet.pdf the sheet alone
  docs/COMPONENTS.md                      the parts table (owned vs to buy, with the exact listings)
  docs/WIRING.md                          the net list, the pin audit, the current budget, the meter checks

Everything on the sheet is derived from PINS / NETS / PARTS below, and the script refuses to write anything if
the pin audit or the drawing-clearance check fails. Nothing here has been built; see README.md for status.

Rev A, 2026-10-27: one gear motor, the head pans. Rev B, 2026-11-10 (builder's choice that day): the head
tilts as well, on the second gear motor, inside a brass yoke; the action button and the two home stops share one
ADC pin as a resistor ladder, because the XIAO has eleven header pins and the build needs twelve signals; the
OLED's clock moves to the UART0 TX pin, where the boot ROM's chatter cannot form an I2C start condition.

Sources read 2026-10-27: Seeed wiki "Getting started with XIAO ESP32S3 (Sense)" (pinout, camera/mic/SD GPIOs,
700 mA 3V3 budget, charge LED behaviour, power figures), the pin-multiplexing page, retailer specs for the MX1508
(2-10 V, 1.5 A continuous, 1.8-7 V inputs), the Amazon listings the builder chose, and the two owned inventories.
Read 2026-11-10: the MAX98357 family datasheet and an ADI forum note (SD_MODE must go low before the clocks stop,
so the shutdown line stays); ESP32-S3 ADC1 covers GPIO1-10, so D10 (GPIO9) reads the ladder.
The Router (hops at every crossing) is copied from pocket_ai_assistant/edu/pages/gen/wiring_sheet.py so this
project stands on its own."""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PAGES = HERE.parent
DOCS = PAGES.parent
OUT = PAGES / "wiring-board.html"
PRINT = PAGES / "print"
STYLE = (HERE / "page_style.css").read_text()

W, H = 1360, 880
REV = "Rev B"
DRAWN = "2026-11-10"

# ----------------------------------------------------------------------------- the contract
# XIAO ESP32-S3 Sense: every header pin, what it does here. GPIO numbers from the Seeed wiki.
PINS = [  # (header, gpio, job, net)
    ("D0", 1, "I2S bit clock to the amp", "BCLK"),
    ("D1", 2, "I2S word clock to the amp", "LRC"),
    ("D2", 3, "I2S data to the amp", "DIN"),
    ("D3", 4, "amp shutdown, pull-down R1 keeps it silent at boot", "AMP_SD"),
    ("D4", 5, "I2C SDA, OLED", "SDA"),
    ("D5", 6, "tilt motor IN3 (LEDC PWM), pull-down R7", "IN3"),
    ("D6", 43, "I2C SCL, OLED. UART0 TX chatters here at boot: clock pulses with SDA held high are not a start condition, so the screen ignores them", "SCL"),
    ("D7", 44, "tilt motor IN4 (LEDC PWM), pull-down R8. UART0 RX is an input at boot; R8 holds the driver input low", "IN4"),
    ("D8", 7, "pan motor IN1 (LEDC PWM), pull-down R2", "IN1"),
    ("D9", 8, "pan motor IN2 (LEDC PWM), pull-down R3", "IN2"),
    ("D10", 9, "the ladder: ADC1 channel 8 reads which of the action button, the pan stop and the tilt stop is pressed", "LADDER"),
]
# GPIOs the Sense expansion board already owns. Camera DVP + SCCB, PDM microphone, SD slot.
RESERVED = {
    "camera": {10, 11, 12, 13, 14, 15, 16, 17, 18, 38, 39, 40, 47, 48},
    "pdm mic": {41, 42},
    "sd slot (empty)": {21, 7, 8, 9},   # 7/8/9 are D8-D10: the slot shares them, so it must stay empty
}
STRAPPING = {0, 3, 45, 46}
ADC1 = set(range(1, 11))  # ESP32-S3 ADC1: GPIO1-10

# The ladder: one 10 kΩ pull-up to 3V3 at the XIAO, three buttons each in series with its own resistor to GND.
LADDER = [  # (switch, where, series Ω)
    ("action button", "body front", 680),
    ("pan stop", "body roof, under the yoke", 2200),
    ("tilt stop", "yoke, left upright", 5600),
]
PULLUP = 10000
VREF = 3.3


def ladder_volts():
    """Every combination of pressed switches → volts at D10. The firmware's bands come from this."""
    out = {}
    names = [s for s, _, _ in LADDER]
    rs = [r for _, _, r in LADDER]
    for mask in range(8):
        pressed = [names[i] for i in range(3) if mask >> i & 1]
        if not pressed:
            out["none"] = VREF
            continue
        g = sum(1 / rs[i] for i in range(3) if mask >> i & 1)
        rpar = 1 / g
        out[" + ".join(pressed)] = VREF * rpar / (rpar + PULLUP)
    return out


NETS = [  # (net, from, to, wire, why)
    ("3V3", "XIAO 3V3", "OLED VCC, R4", "rod", "The screen is the only load on the 3.3 V regulator; the XIAO itself and the camera take the rest of its 700 mA. R4 is the ladder's pull-up."),
    ("GND", "holder − (the star)", "XIAO BAT− pad, amp GND, driver GND, 220 µF; then OLED GND, the three ladder resistors, R1-R3, R7, R8 and C4 on the XIAO's GND pin", "rod bus in the head and in the body; one 26 AWG wire across each joint; the holder's own lead to the star", "One net, two solder points. The amp's and motors' return current goes straight to the holder's − lead, never through the XIAO's pads. Only the small signal grounds sit on the XIAO's GND header pin."),
    ("SDA", "D4 (GPIO5)", "OLED SDA", "rod", "Any S3 pin can be I2C through the GPIO matrix. Address 0x3C or 0x3D, as before."),
    ("SCL", "D6 (GPIO43)", "OLED SCL", "rod", "GPIO43 is UART0 TX and the boot ROM prints on it for a fraction of a second. An I2C start needs SDA to fall while SCL is high; SDA sits high on its pull-up, so the SSD1306 never sees a frame. The console goes over USB, so nothing is lost."),
    ("BCLK", "D0 (GPIO1)", "amp BCLK", "rod", "I2S out only: the microphone is the PDM mic on the Sense board (GPIO41/42), so there is no shared duplex bus."),
    ("LRC", "D1 (GPIO2)", "amp LRC", "rod", ""),
    ("DIN", "D2 (GPIO3)", "amp DIN", "rod", "GPIO3 is a strapping pin on the S3; it only matters if the JTAG eFuse is burned, which it is not on a stock XIAO."),
    ("AMP_SD", "D3 (GPIO4)", "amp SD, with R1 4.7 kΩ to GND", "rod", "Same rule as the first build: the amp stays off until the firmware raises SD, and the pull-down beats the breakout's 1 MΩ pull-up. The line stays in Rev B because the amp must be shut down before its clocks stop, else the output can sit at DC."),
    ("BAT+", "holder + → switch → XIAO BAT+ pad", "amp VIN, driver VCC, 220 µF", "rod bus in the body and in the head; one 26 AWG wire across each joint; a short wire stub to the XIAO's BAT+ pad", "3.0-4.2 V straight from the cell. There is no 5 V rail in this design: the XIAO's 5V pin is dead on battery, and every part here accepts cell voltage."),
    ("IN1", "D8 (GPIO7)", "driver IN1, with R2 10 kΩ to GND", "rod in the head, 30 AWG across both joints", "Two pins drive one motor: IN1 high + IN2 low turns one way, swapped turns the other, both low coasts, PWM on the high one sets speed. Bridge A is the pan motor in the body."),
    ("IN2", "D9 (GPIO8)", "driver IN2, with R3 10 kΩ to GND", "rod in the head, 30 AWG across both joints", "R2/R3 hold both inputs low while the S3 boots and its pins float; drop them only if the meter shows the module has its own pull-downs."),
    ("IN3", "D5 (GPIO6)", "driver IN3, with R7 10 kΩ to GND", "rod in the head, 30 AWG across both joints", "Bridge B is the tilt motor. Same rules as IN1/IN2."),
    ("IN4", "D7 (GPIO44)", "driver IN4, with R8 10 kΩ to GND", "rod in the head, 30 AWG across both joints", "GPIO44 is UART0 RX, an input at boot with a weak pull-up inside the chip; against R8 that is 0.6 V at the driver, well under its 1.8 V threshold, so the tilt motor cannot twitch at boot."),
    ("M1", "driver OUT A1 / A2", "pan motor leads", "the motor's own leads, in the body", "Polarity does not matter: swap the two if 'left' turns right."),
    ("M2", "driver OUT B1 / B2", "tilt motor leads", "the motor's own leads to the body: 30 AWG across both joints", "The tilt motor lives in the head, the driver in the body. 0.36 A stalled over 150 mm of 30 AWG drops 20 mV: nothing."),
    ("LADDER", "D10 (GPIO9, ADC1_CH8)", "R4 10 kΩ to 3V3; C4 100 nF to GND; action button + 680 Ω, pan stop + 2.2 kΩ, tilt stop + 5.6 kΩ, each to GND", "rod in the head, 30 AWG across both joints, rod in the body", "Twelve signals, eleven pins: the three switches share one ADC pin. Nothing pressed reads 3.3 V; each switch pulls the pin to its own voltage (table below) and the pairs are distinct too, so the firmware never mistakes a stop for the button. C4 and the 10 kΩ source make a 1 ms filter against motor noise."),
    ("SPK", "amp OUT+ / OUT−", "speaker", "its own 32 AWG leads", "Neither lead is ground. Never clip a scope ground to either."),
]

# ----------------------------------------------------------------------------- the parts
PARTS = [
    ("Bought for this project, 2026-10-27 (Amazon order; prices not recorded)", [
        ("2", "Seeed XIAO ESP32-S3 Sense, with camera and microphone", "https://www.amazon.com/dp/B0C69FFVHH", "Amazon B0C69FFVHH", "",
         "The brain, the camera and the microphone in one 21 × 18 mm stack: ESP32-S3, two cores at 240 MHz, 8 MB PSRAM (the camera needs it), USB-C, a Li-ion charger on the back, a 700 mA 3.3 V regulator, and the Sense expansion board with the camera (OV2640 or OV5640, same pins, about 65° wide) plus a PDM mic. Black boards, silver shield. The pair (order 114-1888127-6908215) has not shipped as of 2026-11-10; Amazon's estimate is 11-10 to 11-15. The second is the Pocket AI Sphere's, not a spare. On arrival: note which sensor is printed on the camera module, and keep the SD slot empty."),
        ("1 pack of 5", "MX1508 dual H-bridge driver, Aideepen", "https://www.amazon.com/dp/B075S368Y2", "Amazon B075S368Y2", "",
         "Sold as an L298N replacement, but it is the MOSFET MX1508: 2-10 V motor supply, 1.5 A continuous per bridge, inputs happy at 3.3 V, no logic-supply pin. Both bridges are used now: A pans, B tilts. The board comes red or blue; it sits in the body behind the holder, out of sight. On arrival: the board should say MX1508 and carry VCC, GND, IN1-IN4 and two motor outputs. Delivered 2026-10-30."),
        ("2 (both on hand 2026-11-03)", "Micro gear motor 1218GEN20, 3 V 16 rpm, Naroote", "https://www.amazon.com/dp/B0BS9K8Q8Z", "Amazon B0BS9K8Q8Z", "",
         "12 mm metal gearmotors, 3 mm D-shaft, 16 rpm at 3 V. One pans from the body, one tilts from inside the head. Slow is what a head wants: at the cell's 3.7-4.2 V run them at 70 % PWM or less, one axis at a time. Stall current is not published; the 12 mm class is about 0.36 A, so measure it on the bench supply before either goes in the frame. Caliper the body length and the shaft before the yoke is cut."),
        ("1 pack of 10", "16340 / CR123A holder with leads, ACEIRMC", "https://www.amazon.com/dp/B0CRGK889F", "Amazon B0CRGK889F", "",
         "The holder from the old fit check (43 × 18 × 14 mm), black. CR123A and 16340 are the same can; the NL169 is 16.6 × 34.1 mm with a button top. On arrival: check that the spring reaches the button and meter that red is on the + contact. Delivered 2026-10-30."),
        ("1 pack of 20", "MTS-102 mini toggle switch, Ferwooh", "https://www.amazon.com/dp/B0CZ6XZ2P9", "Amazon B0CZ6XZ2P9", "",
         "SPDT ON-ON, 3 solder lugs, 6 A at 125 V AC: far above the 1 A peak it carries in the cell's + lead. Use the middle lug and one outer lug; the third stays empty; heat-shrink both (white). The owned Chanzon slide switches are bench-only here: not rated for that current. Delivered 2026-10-30."),
    ]),
    ("Owned, in pocket_ai_assistant/docs/INVENTORY.md: do not buy", [
        ("1", "Hosyond SSD1306 0.96\" OLED", "", "owned ×10", "", "Same screen, same I2C, same silkscreen trap (GND-VCC-SCL-SDA or VCC-GND-SCL-SDA: read it). White pixels on black glass; the board behind the glass is blue on some packs, so check the drawer and face it inward."),
        ("1", "HiLetgo MAX98357A amplifier", "", "owned ×12", "", "Runs from the cell (2.5-5.5 V in). GAIN left open = 9 dB. Volume cap stays at 65: at a full 4.2 V cell that is 0.47 W into the 0.8 W speaker. Under the speaker in the head, board side in."),
        ("1", "Same Sky CES-20134-088PM speaker", "", "owned ×6", "", "Black. Its 60 mm leads reach from the amp in the head without any wire of yours."),
        ("3", "QTEATAK tactile buttons", "", "owned ×420", "", "The action button, the pan stop and the tilt stop. White caps on the action button."),
        ("9", "Resistors: 680 Ω, 2.2 kΩ, 4.7 kΩ, 5.6 kΩ, 10 kΩ ×5", "", "LuminologyPro kit", "", "R1 amp SD pull-down (4.7 kΩ); R2, R3, R7, R8 driver input pull-downs (10 kΩ); R4 ladder pull-up (10 kΩ); the ladder's 680 Ω (button), 2.2 kΩ (pan stop), 5.6 kΩ (tilt stop)."),
        ("4", "Capacitors: 220 µF, 10 µF, 100 nF ×2", "", "ALLECIN and BOJACK kits", "", "220 µF on the BAT+ rail at the amp; 10 µF + 100 nF at the OLED's VCC pin; C4 100 nF at D10 for the ladder."),
        ("", "26 AWG (power) and 30 AWG (signal) silicone wire, headers, heat-shrink, Kapton", "", "TUOFENG, CBAZY, Pointool, ELEGOO, XFJYMXDM", "", "26 AWG for BAT+ and GND across the joints, 30 AWG for the other three. White or black wire only where it shows: the five run up one yoke upright as one deliberate line. White heat-shrink."),
        ("", "K&S 1.5 mm tube/rod, 1.0 mm rod", "", "owned", "", "Frame stock for the tower and the yoke: brass tube for the outline and the yoke, 1.0 mm rod for the harness, same soldering as the first frame. Bare brass, no paint (builder's rule 2026-11-09). The frame stays electrically floating."),
    ]),
    ("Owned, in cyber_clock_v2/docs/INVENTORY.md", [
        ("1 (of 13)", "Nitecore NL169 16340, 3.6 V 950 mAh, protected button-top", "", "owned ×13 (IMR Batteries, delivered 2026-10-21)", "", "The cell. Protected (2 A continuous, 4.20 V termination), so the XIAO's plain 4.2 V charger suits it. Never solder to it; it sits in the holder, in the body, where its printed wrap does not show."),
        ("2 + 1", "M METERXITY brass tube set, 2 to 7 mm", "", "owned (three sets, delivered 2026-10-28)", "", "Two sockets from the 4 mm × 0.5 mm wall tube (3 mm bore) over the two 3 mm D-shafts: the pan hub on the yoke's base and the tilt socket on the yoke's right upright; a drop of CA or a flat filed on the shaft locks each. One short piece of the 3 mm tube on the left upright is the bearing for the head's 1.5 mm pivot pin. Caliper all of it before cutting."),
    ]),
    ("Optional, not owned", [
        ("1", "External 16340 / CR123A Li-ion charger (Nitecore UI1/UI2 or XTAR VC2)", "", "any, about $10-15", "", "The fast way to charge: pull the cell, two hours, done. The XIAO's own charger is a 50-100 mA trickle for an asleep device. Not required to build or run."),
    ]),
    ("Not needed any more", [
        ("", "ESP32-C3 SuperMini, INMP441 microphone, PowerBoost 1000C copy, fish paper", "", "stay in the drawer", "", "The XIAO carries the mic and the charger, nothing here needs 5 V, and a hard-can cell in a plastic holder needs no jacket."),
    ]),
]


# ----------------------------------------------------------------------------- audits
def audit():
    used = {}
    for hdr, g, job, net in PINS:
        assert g not in used, f"{hdr}: GPIO{g} listed twice"
        used[g] = hdr
    for owner, gs in RESERVED.items():
        if owner.startswith("sd"):
            continue
        clash = gs & set(used)
        assert not clash, f"pin clash with the {owner}: GPIO {sorted(clash)}"
    sd = RESERVED["sd slot (empty)"] & set(used)
    assert sd == {7, 8, 9}, "D8-D10 are shared with the SD slot by design; the slot stays empty"
    straps = STRAPPING & set(used)
    assert straps <= {3}, f"strapping pins in use: {straps}"
    nets = {net for _, _, _, net in PINS if net}
    assert len(nets) == 11, f"every header pin carries a net in Rev B: {len(nets)}"
    ladder_pin = [g for _, g, _, net in PINS if net == "LADDER"]
    assert ladder_pin and ladder_pin[0] in ADC1, "the ladder must sit on an ADC1 pin"
    # the ladder's states must be told apart with 5 % resistors and 30 mV of ADC error
    v = ladder_volts()
    singles = sorted(v[s] for s, _, _ in LADDER)
    assert min(b - a for a, b in zip(singles, singles[1:])) > 0.2, f"ladder singles too close: {v}"
    btn = v["action button"]
    others = [val for k, val in v.items() if k not in ("none", "action button") and "action button" not in k]
    assert btn * 1.05 + 0.03 < min(others) * 0.95 - 0.03, f"button not separable from the stops: {v}"
    assert all(val <= btn + 1e-9 for k, val in v.items() if "action button" in k), v  # every combo with the button reads lower still
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
        self.segs = []          # (x0, y0, x1, y1, net)
        self.pins = []          # (x, y, net)

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
        """Every wire stays clear of every pin dot of another net, and parallel lanes of different nets that
        overlap in extent keep min_lane apart. Crossings are allowed (they get hops); we count them to keep few."""
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


def block(x, y, w, h, title, sub=None, cls="part", sub2=None, ty=24):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls}"/>', T(x + w / 2, y + ty, title, "title", "middle")]
    if sub:
        o.append(T(x + w / 2, y + ty + 18, sub, "sub", "middle"))
    if sub2:
        o.append(T(x + w / 2, y + ty + 34, sub2, "sub", "middle"))
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


def zigzag(rt, x, y0, y1, net, net2=None):
    """A resistor on a vertical run from y0 to y1, either direction. net2 names the far end when it differs."""
    a, b = min(y0, y1), max(y0, y1)
    mid = (a + b) / 2
    z = 9
    body = [(x, mid - 16)]
    for i, dx in enumerate((z, -z, z, -z, z, -z)):
        body.append((x + dx, mid - 16 + (i + 0.5) * (32 / 6)))
    body.append((x, mid + 16))
    top = rt.wire([(x, a), body[0]], "thin", net if y0 < y1 else (net2 or net))
    bot = rt.wire([body[-1], (x, b)], "thin", (net2 or net) if y0 < y1 else net)
    pts = body if y0 < y1 else body[::-1]
    path = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return top + bot + f'<path d="{path}" class="thin"/>'


def capacitor(rt, x, y0, y1, net):
    mid = (y0 + y1) / 2
    return "".join([rt.wire([(x, y0), (x, mid - 5)], "thin", net), rt.wire([(x, mid + 5), (x, y1)], "thin", "GND"),
                    f'<line x1="{x-12}" y1="{mid-5}" x2="{x+12}" y2="{mid-5}" class="thin"/>',
                    f'<line x1="{x-12}" y1="{mid+5}" x2="{x+12}" y2="{mid+5}" class="thin"/>'])


SVG_CSS = ("<style>"
           ".part{fill:var(--paper);stroke:var(--ink);stroke-width:1.6}"
           ".head{fill:none;stroke:var(--brass);stroke-width:1.4;stroke-dasharray:6 5}"
           ".ghost{fill:none;stroke:var(--ink-2);stroke-width:1.2;stroke-dasharray:4 3}"
           ".frame{fill:none;stroke:var(--brass);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}"
           ".usb{fill:var(--signal-soft);stroke:var(--signal);stroke-width:1.2}"
           ".title{font:700 17px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".sub{font:400 12px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".h1{font:900 24px 'Archivo','Helvetica Neue',Arial,sans-serif;fill:var(--ink)}"
           ".pin{font:700 13px 'JetBrains Mono',monospace;fill:var(--ink)}"
           ".fn{font:400 11.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink-2)}"
           ".lab{font:700 12.5px 'Public Sans',system-ui,sans-serif;fill:var(--ink)}"
           ".brass{font:700 12px 'JetBrains Mono',monospace;fill:var(--brass);letter-spacing:.08em}"
           ".rod{fill:none;stroke:var(--ink);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}"
           ".bus{fill:none;stroke:var(--brass);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}"
           ".thin{fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
           ".joint{fill:var(--ink)}"
           ".pinend{fill:var(--paper);stroke:var(--ink);stroke-width:1.8}"
           ".dim{fill:none;stroke:var(--ink-2);stroke-width:1}"
           "</style>")


# ----------------------------------------------------------------------------- the sheet
def sheet():
    rt = Router()
    w = rt.wire
    o = [T(20, 30, f"Pocket AI with camera, {REV}: every connection on one sheet", "h1"),
         T(20, 46, "A dot is a joint. A line that hops over another does not touch it. Thick = bare rod, or one of the five wires that cross the two joints. Thin = resistor or capacitor leg.", "sub"),
         T(20, 60, "Ground symbols: power grounds to the holder's − lead, signal grounds to the XIAO's GND pin. No 5 V rail exists.", "sub")]

    # ------------------------------------------------------------ XIAO, centre
    XX, XY, XW, XH = 540, 150, 320, 430
    o.append(block(XX, XY, XW, XH, "XIAO ESP32-S3 Sense", "camera: GPIO10-18 · 38-40 · 47 · 48 (internal)",
                   sub2="PDM mic: GPIO41/42 (internal) · SD slot stays empty", ty=60))
    L = {}
    for name, y, fn, net in (("3V3", 260, "3.3 V out", "3V3"), ("GND", 290, None, "GND"), ("D4", 340, "GPIO5 · SDA", "SDA"), ("D6", 370, "GPIO43 · SCL", "SCL"),
                             ("D0", 450, "GPIO1 · BCLK", "BCLK"), ("D1", 480, "GPIO2 · LRC", "LRC"), ("D2", 510, "GPIO3 · DIN", "DIN"), ("D3", 540, "GPIO4 · amp SD", "AMP_SD")):
        L[name] = (XX, y); o.append(pin(rt, XX, y, name, "L", net, fn, XX + 50))
    R = {}
    for name, y, fn, net in (("D8", 290, "GPIO7 · IN1 pan", "IN1"), ("D9", 320, "GPIO8 · IN2 pan", "IN2"), ("D5", 350, "GPIO6 · IN3 tilt", "IN3"), ("D7", 380, "GPIO44 · IN4 tilt", "IN4")):
        R[name] = (XX + XW, y); o.append(pin(rt, XX + XW, y, name, "R", net, fn, XX + XW - 50))
    o.append(T(XX + XW - 12, 414, "all eleven header pins in use", "fn", "end"))
    o.append(T(XX + XW - 12, 430, "5V pin: USB only · nothing connects here", "fn", "end"))
    Tp = {}
    for name, x, net in (("D10", 640, "LADDER"),):
        Tp[name] = (x, XY); o.append(pin(rt, x, XY, name, "T", net))
    o.append(T(654, 168, "GPIO9 · ADC1 ch 8", "fn"))
    B = {}
    for name, x, net in (("BAT+", 780, "BAT+"), ("BAT−", 830, "GND")):
        B[name] = (x, XY + XH); o.append(pin(rt, x, XY + XH, name, "B", net))
    o.append(T(850, 600, "BAT pads: back of the XIAO", "fn"))
    o.append(f'<rect x="{XX+10}" y="{XY+XH-24}" width="36" height="15" rx="3" class="usb"/>'); o.append(T(XX + 28, XY + XH - 13, "USB-C", "fn", "middle"))
    o.append(T(XX + 54, XY + XH - 13, "charges the cell · console", "fn"))

    # ------------------------------------------------------------ the ladder, top left
    v = ladder_volts()
    o.append(block(60, 66, 280, 92, "Action · Pan stop · Tilt stop", "three tactile buttons on one ADC pin",
                   sub2="680 Ω · 2.2 kΩ · 5.6 kΩ, each to GND"))
    o.append(T(210, 140, f"reads {v['action button']:.2f} · {v['pan stop']:.2f} · {v['tilt stop']:.2f} V · both stops {v['pan stop + tilt stop']:.2f} V", "fn", "middle"))
    o.append(pin(rt, 340, 110, "S", "R", "LADDER"))
    o.append(pin(rt, 70, 158, "GND", "B", "GND")); o.append(w([(70, 158), (70, 162)], "rod", "GND")); o.append(gnd(70, 162))
    o.append(w([Tp["D10"], (640, 110), (340, 110)], "rod", "LADDER")); o.append(T(560, 102, "LADDER", "lab", "middle"))
    # R4 pull-up to the 3V3 lane, C4 to ground
    o.append(zigzag(rt, 400, 110, 260, "LADDER", "3V3")); o.append(dot(400, 110)); o.append(T(414, 190, "R4 10 kΩ", "fn"))
    o.append(capacitor(rt, 470, 110, 150, "LADDER")); o.append(dot(470, 110)); o.append(gnd(470, 150)); o.append(T(484, 134, "C4 100 nF", "fn"))

    # ------------------------------------------------------------ OLED, left
    OX, OY, OW, OH = 60, 190, 280, 200
    o.append(block(OX, OY, OW, OH, "SSD1306 OLED 0.96\"", "Hosyond · I2C 0x3C/0x3D · 3.3 V"))
    P = {}
    for name, y, net in (("VCC", 260, "3V3"), ("GND", 290, "GND"), ("SDA", 340, "SDA"), ("SCL", 370, "SCL")):
        P[name] = (OX + OW, y); o.append(pin(rt, OX + OW, y, name, "R", net))
    o.append(T(OX + OW / 2, OY + 58, "silkscreen order varies: read it before wiring", "fn", "middle"))
    o.append(w([L["3V3"], P["VCC"]], "rod", "3V3")); o.append(T(450, 252, "3V3", "lab", "middle"))
    o.append(w([L["GND"], P["GND"]], "rod", "GND")); o.append(T(450, 282, "GND", "lab", "middle"))
    o.append(w([L["D4"], P["SDA"]], "rod", "SDA")); o.append(T(450, 332, "SDA", "lab", "middle"))
    o.append(w([L["D6"], P["SCL"]], "rod", "SCL")); o.append(T(450, 362, "SCL", "lab", "middle"))
    o.append(capacitor(rt, 400, 260, 290, "3V3")); o += [dot(400, 260), dot(400, 290)]
    o.append(T(400, 312, "10 µF + 100 nF", "fn", "middle"))

    # ------------------------------------------------------------ amp + speaker, bottom left
    AX, AY, AW, AH = 120, 400, 220, 250
    o.append(block(AX, AY, AW, AH, "MAX98357A amp", "HiLetgo · GAIN open = 9 dB"))
    o.append(T(AX + 16, 600, "VIN 2.5-5.5 V: runs from the cell", "fn"))
    A = {}
    for name, y, net in (("BCLK", 450, "BCLK"), ("LRC", 480, "LRC"), ("DIN", 510, "DIN"), ("SD", 540, "AMP_SD")):
        A[name] = (AX + AW, y); o.append(pin(rt, AX + AW, y, name, "R", net))
    for name, y, net in (("OUT+", 470, "SPK+"), ("OUT−", 510, "SPK-")):
        A[name] = (AX, y); o.append(pin(rt, AX, y, name, "L", net))
    for name, x, net in (("GND", 180, "GND"), ("VIN", 260, "BAT+")):
        A[name] = (x, AY + AH); o.append(pin(rt, x, AY + AH, name, "B", net))
    for a_, b_, lab in (("D0", "BCLK", "BCLK"), ("D1", "LRC", "LRC"), ("D2", "DIN", "DIN"), ("D3", "SD", "SD")):
        o.append(w([L[a_], A[b_]], "rod", {"D0": "BCLK", "D1": "LRC", "D2": "DIN", "D3": "AMP_SD"}[a_])); o.append(T(450, L[a_][1] - 8, lab, "lab", "middle"))
    o.append(zigzag(rt, 420, 540, 600, "AMP_SD", "GND")); o.append(dot(420, 540)); o.append(gnd(420, 600)); o.append(T(434, 574, "R1 4.7 kΩ", "fn"))
    o.append(block(10, 440, 80, 100, "Speaker", "8 Ω 0.8 W"))
    rt.pin(90, 470, "SPK+"); rt.pin(90, 510, "SPK-")
    o += [f'<circle cx="90" cy="470" r="4.5" class="pinend"/>', f'<circle cx="90" cy="510" r="4.5" class="pinend"/>']
    o.append(w([(90, 470), A["OUT+"]], "rod", "SPK+")); o.append(w([(90, 510), A["OUT−"]], "rod", "SPK-"))
    o.append(T(50, 528, "own leads", "fn", "middle"))
    o.append(w([A["GND"], (180, 680)], "rod", "GND")); o.append(gnd(180, 680))
    o.append(w([A["VIN"], (260, 700)], "rod", "BAT+"))

    # ------------------------------------------------------------ BAT+ rail, cell, switch
    o.append(w([(260, 700), (1040, 700)], "bus", "BAT+")); o.append(dot(260, 700))
    o.append(T(540, 690, "BAT+ rail · 3.0-4.2 V from the cell · 26 AWG", "brass", "middle"))
    o.append(capacitor(rt, 380, 700, 760, "BAT+")); o.append(dot(380, 700)); o.append(gnd(380, 760)); o.append(T(396, 736, "220 µF", "fn"))
    o.append(w([B["BAT+"], (780, 700)], "rod", "BAT+")); o.append(dot(780, 700))
    o.append(w([B["BAT−"], (830, 610)], "rod", "GND")); o.append(gnd(830, 610))
    o.append(block(440, 740, 160, 90, "16340 holder", "Nitecore NL169 950 mAh", sub2="in the body", ty=36))
    rt.pin(480, 740, "BAT+"); rt.pin(600, 812, "GND")
    o += [f'<circle cx="480" cy="740" r="4.5" class="pinend"/>', T(492, 732, "+", "pin", "start"),
          f'<circle cx="600" cy="812" r="4.5" class="pinend"/>', T(588, 817, "−", "pin", "end")]
    o.append(w([(600, 812), (630, 812)], "rod", "GND")); o.append(gnd(630, 812))
    o.append(block(660, 740, 140, 90, "Power switch", "MTS-102 toggle, 2 A+", sub2="charge with it ON, USB in", ty=36))
    rt.pin(700, 740, "BAT+"); rt.pin(780, 740, "BAT+")
    o += [f'<circle cx="700" cy="740" r="4.5" class="pinend"/>', T(712, 732, "in", "pin", "start"),
          f'<circle cx="780" cy="740" r="4.5" class="pinend"/>', T(792, 732, "out", "pin", "start")]
    o.append(w([(480, 740), (480, 720), (700, 720), (700, 740)], "rod", "BAT+"))
    o.append(w([(780, 740), (780, 700)], "rod", "BAT+"))

    # ------------------------------------------------------------ driver + two motors, right
    DX, DY, DW, DH = 1000, 200, 200, 300
    o.append(block(DX, DY, DW, DH, "MX1508 driver", "Aideepen · 2-10 V · 1.5 A per bridge", sub2="A = pan · B = tilt · in the body"))
    D = {}
    for name, y, net in (("IN1", 290, "IN1"), ("IN2", 320, "IN2"), ("IN3", 350, "IN3"), ("IN4", 380, "IN4")):
        D[name] = (DX, y); o.append(pin(rt, DX, y, name, "L", net))
    for name, y, net in (("A1", 310, "M1a"), ("A2", 350, "M1b"), ("B1", 430, "M2a"), ("B2", 470, "M2b")):
        D[name] = (DX + DW, y); o.append(pin(rt, DX + DW, y, name, "R", net))
    for name, x, net in (("VCC", 1040, "BAT+"), ("GND", 1120, "GND")):
        D[name] = (x, DY + DH); o.append(pin(rt, x, DY + DH, name, "B", net))
    for src, dst, net in (("D8", "IN1", "IN1"), ("D9", "IN2", "IN2"), ("D5", "IN3", "IN3"), ("D7", "IN4", "IN4")):
        o.append(w([R[src], D[dst]], "rod", net))
    # pull-downs: IN1 and IN2 rise to a signal ground above the lanes, IN3 and IN4 drop to one below (two hops in all)
    o.append(zigzag(rt, 915, 290, 220, "IN1", "GND")); o.append(dot(915, 290)); o.append(T(915, 196, "R2 10 kΩ", "fn", "end"))
    o.append(zigzag(rt, 945, 320, 220, "IN2", "GND")); o.append(dot(945, 320)); o.append(T(949, 210, "R3 10 kΩ", "fn"))
    o.append(w([(915, 220), (985, 220)], "thin", "GND")); o.append(gnd(985, 220))
    o.append(zigzag(rt, 955, 350, 445, "IN3", "GND")); o.append(dot(955, 350)); o.append(T(940, 404, "R7 10 kΩ", "fn", "end"))
    o.append(zigzag(rt, 985, 380, 445, "IN4", "GND")); o.append(dot(985, 380)); o.append(T(996, 480, "R8 10 kΩ", "fn", "end"))
    o.append(w([(955, 445), (985, 445)], "thin", "GND")); o.append(gnd(985, 445))
    o.append(w([D["VCC"], (1040, 700)], "rod", "BAT+")); o.append(dot(1040, 700))
    o.append(w([D["GND"], (1120, 530)], "rod", "GND")); o.append(gnd(1120, 530))
    # motors
    o.append(block(1230, 280, 110, 100, "Pan motor", "3 V · 16 rpm", sub2="in the body"))
    rt.pin(1230, 310, "M1a"); rt.pin(1230, 350, "M1b")
    o += [f'<circle cx="1230" cy="310" r="4.5" class="pinend"/>', f'<circle cx="1230" cy="350" r="4.5" class="pinend"/>']
    o.append(w([D["A1"], (1230, 310)], "rod", "M1a")); o.append(w([D["A2"], (1230, 350)], "rod", "M1b"))
    o.append(block(1230, 400, 110, 100, "Tilt motor", "3 V · 16 rpm", sub2="in the head"))
    rt.pin(1230, 430, "M2a"); rt.pin(1230, 470, "M2b")
    o += [f'<circle cx="1230" cy="430" r="4.5" class="pinend"/>', f'<circle cx="1230" cy="470" r="4.5" class="pinend"/>']
    o.append(w([D["B1"], (1230, 430)], "rod", "M2a")); o.append(w([D["B2"], (1230, 470)], "rod", "M2b"))
    for i, t_ in enumerate(("swap a pair if an axis", "turns the wrong way", "≤ 70 % PWM on a 3 V motor", "one axis moves at a time")):
        o.append(T(1280, 524 + 14 * i, t_, "fn", "middle"))

    # ------------------------------------------------------------ joints note
    o.append(T(1064, 578, "Across the two joints", "lab"))
    o.append(T(1064, 596, "Head tilts on the yoke; yoke turns on the body.", "fn"))
    o.append(T(1064, 610, "Five silicone wires run up one yoke upright:", "fn"))
    o.append(T(1064, 624, "BAT+ and GND (26 AWG), LADDER and the tilt", "fn"))
    o.append(T(1064, 638, "motor's pair (30 AWG). A loose coil at the pan", "fn"))
    o.append(T(1064, 652, "hub (±150°) and a loop at the tilt pin (±90°).", "fn"))
    o.append(T(1064, 666, "Everything else is bare rod.", "fn"))
    o.append(T(20, 860, f"{REV}, drawn {DRAWN}, verified on paper against the Seeed wiki, the MAX98357 datasheet and the vendor listings. Not built. "
                        "The pin audit, the ladder audit and the line-clearance check in gen/wiring_board.py pass.", "sub"))

    bad, crossings = rt.check()
    for b in bad:
        print("CLEARANCE:", b)
    assert not bad, f"{len(bad)} clearance failures"
    print(f"sheet: {len(rt.segs)} segments, {crossings} crossings (all drawn as hops)")
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Pocket AI with camera wiring sheet, Rev B">{SVG_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- the tower figure
def tower():
    o = []
    s = 4.0  # px per mm
    HW, HH, GAP, BH, SD = 50, 50, 10, 62, 42
    x0, y0 = 130, 60
    hx, hy = x0, y0
    by = y0 + (HH + GAP) * s
    ay = hy + HH / 2 * s                 # the tilt axis, through the head's centre
    cx = hx + HW * s / 2
    o.append(T(cx, 40, "Front", "lab", "middle"))
    # yoke: a U of 1.5 mm brass tube on the pan hub, uprights to the tilt axis
    yl, yr = hx - 3 * s, hx + (HW + 3) * s
    yb = by - 5 * s
    o.append(f'<path d="M{yl},{ay} L{yl},{yb} L{yr},{yb} L{yr},{ay}" class="frame"/>')
    o.append(f'<rect x="{cx - 2*s}" y="{yb}" width="{4*s}" height="{5*s}" class="part"/>')
    o.append(f'<rect x="{hx}" y="{hy}" width="{HW*s}" height="{HH*s}" rx="6" class="part"/>')
    o.append(f'<rect x="{hx}" y="{by}" width="{HW*s}" height="{BH*s}" rx="6" class="part"/>')
    # sockets on the uprights
    o.append(f'<circle cx="{yr}" cy="{ay}" r="{2*s}" class="part"/>'); o.append(f'<circle cx="{yl}" cy="{ay}" r="{1.5*s}" class="part"/>')
    # head contents
    o.append(f'<circle cx="{cx}" cy="{hy + 7*s}" r="{3.2*s}" class="part"/>'); o.append(f'<circle cx="{cx}" cy="{hy + 7*s}" r="{1.4*s}" class="joint"/>')
    o.append(T(cx + 4.5 * s, hy + 7 * s + 4, "camera", "fn"))
    o.append(f'<rect x="{hx + 24*s}" y="{ay - 6*s}" width="{25*s}" height="{12*s}" class="ghost"/>')
    o.append(f'<line x1="{hx + 49*s}" y1="{ay}" x2="{yr}" y2="{ay}" class="thin"/>')
    o.append(f'<rect x="{hx + (HW-27)/2*s}" y="{hy + 14*s}" width="{27*s}" height="{27*s}" class="usb"/>')
    o.append(T(cx, hy + 29 * s, "OLED 27 × 27", "fn", "middle"))
    o.append(T(cx, hy + 46 * s, "XIAO behind the screen,", "fn", "middle")); o.append(T(cx, hy + 49.5 * s, "amp + speaker under it", "fn", "middle"))
    o.append(T(yr + 12, ay - 12, "tilt motor behind the", "fn")); o.append(T(yr + 12, ay + 2, "screen (dashed), its", "fn")); o.append(T(yr + 12, ay + 16, "shaft in the yoke socket", "fn"))
    # tilt stop on the left upright, pan stop on the roof
    o.append(f'<rect x="{yl - 2.5*s}" y="{ay + 5*s}" width="{3*s}" height="{3*s}" class="usb"/>')
    o.append(T(yl - 1 * s, ay + 8 * s + 16, "tilt stop", "fn", "middle"))
    o.append(f'<rect x="{hx + 40*s}" y="{by - 2.5*s}" width="{3*s}" height="{2.5*s}" class="usb"/>')
    o.append(T(hx + HW * s + 12, by + 14, "pan stop on the roof", "fn"))
    # body contents
    o.append(f'<rect x="{hx + 4*s}" y="{by + 6*s}" width="{18*s}" height="{43*s}" class="usb"/>')
    o.append(T(hx + 13 * s, by + 27 * s, "16340", "fn", "middle")); o.append(T(hx + 13 * s, by + 32 * s, "holder", "fn", "middle"))
    o.append(f'<rect x="{hx + 28*s}" y="{by + 4*s}" width="{12*s}" height="{25*s}" class="usb"/>')
    o.append(T(hx + 34 * s, by + 17 * s, "pan", "fn", "middle")); o.append(T(hx + 34 * s, by + 21 * s, "motor", "fn", "middle"))
    o.append(f'<rect x="{hx + 26*s}" y="{by + 33*s}" width="{16*s}" height="{14*s}" class="usb"/>')
    o.append(T(hx + 34 * s, by + 41.5 * s, "MX1508", "fn", "middle"))
    o.append(T(hx + 34 * s, by + 55 * s, "switch · button", "fn", "middle"))
    # dimensions
    dx = x0 - 70
    o.append(f'<path d="M{dx},{hy} L{dx},{by + BH*s} M{dx-5},{hy} L{dx+5},{hy} M{dx-5},{by+BH*s} L{dx+5},{by+BH*s}" class="dim"/>')
    o.append(T(dx - 8, (hy + by + BH * s) / 2, "≈ 122 mm", "lab", "middle", f'transform="rotate(-90 {dx-8} {(hy + by + BH*s)/2})"'))
    ybd = by + BH * s + 22
    o.append(f'<path d="M{hx},{ybd} L{hx + HW*s},{ybd} M{hx},{ybd-5} L{hx},{ybd+5} M{hx+HW*s},{ybd-5} L{hx+HW*s},{ybd+5}" class="dim"/>')
    o.append(T(cx, ybd + 18, "50 mm", "lab", "middle"))
    # side view
    sx = x0 + HW * s + 170
    scx = sx + SD / 2 * s
    o.append(T(scx, 40, "Side", "lab", "middle"))
    o.append(f'<rect x="{sx - 4*s}" y="{ay - 21*s}" width="{50*s}" height="{42*s}" rx="6" class="ghost"/>')
    o.append(f'<rect x="{sx}" y="{hy}" width="{SD*s}" height="{HH*s}" rx="6" class="part"/>')
    o.append(f'<rect x="{sx}" y="{by}" width="{SD*s}" height="{BH*s}" rx="6" class="part"/>')
    o.append(f'<path d="M{scx},{yb} L{scx},{yb + 5*s}" class="frame"/>')
    o.append(f'<path d="M{sx + 2*s},{ay} L{scx - 6*s},{ay} M{scx + 6*s},{ay} L{sx + SD*s - 2*s},{ay}" class="dim"/>')
    o.append(f'<circle cx="{scx}" cy="{ay}" r="{6*s}" class="ghost"/>'); o.append(T(scx, ay + 4, "tilt motor", "fn", "middle"))
    o.append(f'<rect x="{sx + 2*s}" y="{hy + 14*s}" width="{3*s}" height="{27*s}" class="usb"/>')
    o.append(f'<rect x="{sx + 1*s}" y="{hy + 5*s}" width="{4*s}" height="{4*s}" class="usb"/>'); o.append(T(sx, hy - 8, "camera and screen at the front, USB-C at the back", "fn"))
    o.append(f'<rect x="{sx + 9*s}" y="{hy + 3*s}" width="{21*s}" height="{15*s}" class="usb"/>'); o.append(T(sx + 19.5 * s, hy + 12 * s, "XIAO + Sense", "fn", "middle"))
    o.append(f'<rect x="{sx + 9*s}" y="{hy + 33*s}" width="{18*s}" height="{10*s}" class="usb"/>'); o.append(T(sx + 18 * s, hy + 39.5 * s, "amp", "fn", "middle"))
    o.append(f'<rect x="{sx + 9*s}" y="{hy + 44*s}" width="{20*s}" height="{5*s}" class="usb"/>'); o.append(T(sx + 30.5 * s, hy + 48.5 * s, "speaker", "fn"))
    o.append(f'<rect x="{sx + SD*s - 6}" y="{hy + 6*s}" width="6" height="{9*s}" class="usb"/>')
    o.append(f'<rect x="{sx + 4*s}" y="{by + 6*s}" width="{14*s}" height="{43*s}" class="usb"/>'); o.append(T(sx + 11 * s, by + 28 * s, "cell", "fn", "middle"))
    o.append(f'<rect x="{sx + 24*s}" y="{by + 4*s}" width="{12*s}" height="{25*s}" class="usb"/>'); o.append(T(sx + 30 * s, by + 17 * s, "motor", "fn", "middle"))
    o.append(T(sx + 30 * s, by + 40 * s, "driver", "fn", "middle"))
    o.append(f'<path d="M{sx},{ybd} L{sx + SD*s},{ybd} M{sx},{ybd-5} L{sx},{ybd+5} M{sx+SD*s},{ybd-5} L{sx+SD*s},{ybd+5}" class="dim"/>')
    o.append(T(scx, ybd + 18, "42 mm", "lab", "middle"))
    nx = sx + 50 * s + 10
    notes = ["dashed: the head tilted 90°, looking straight up;", "it stands 4 mm proud of the body's front and back", "",
             "tilt axis through the head's centre: the head", "balances on it, so the motor holds no weight", "",
             "speaker under the amp, firing down; USB-C at the", "back of the head: charge and console", "",
             "yoke: 1.5 mm brass tube, 56 mm across, on the pan", "hub; sockets of 4 mm tube over the two 3 mm", "D-shafts, CA; a 1.5 mm pin in 3 mm tube on the left", "",
             "10 mm gap: the head's lower corners sweep 8 mm", "below its rest line at 45° of tilt", "",
             "pan ±150° on the hub, tilt ±90° on the yoke; both", "home to a stop at boot: pan to −150°, tilt to −90°", "(face down), then level and centre", "",
             "frame: owned K&S 1.5 mm brass tube and rod, bare,", "floating, never painted; wires white or black;", "boards face inward", "",
             "old frame 60 × 42 × 35; Rev A 45 × 42 × 115;", "Rev B 50 × 42 × 122: the tilt motor adds 5 mm"]
    lines = [(hy + 14 + 14 * i, t_) for i, t_ in enumerate(notes) if t_]
    for y, t in lines:
        o.append(T(nx, y, t, "fn"))
    TW, TH = 1040, int(ybd + 40)
    return f'<svg viewBox="0 0 {TW} {TH}" role="img" aria-label="The tower: a head in a brass yoke that tilts, on a body it turns above">{SVG_CSS}{"".join(o)}</svg>'


# ----------------------------------------------------------------------------- prose
def a(text, url):
    return f'<a href="{esc(url)}">{esc(text)}</a>' if url else esc(text)


def md_link(text, url):
    return f"[{text}]({url})" if url else text


BUDGET = [  # (load, from, typical mA, peak mA, source)
    ("XIAO ESP32-S3 Sense, Wi-Fi + camera streaming", "3V3 regulator (inside the XIAO)", 155, 366, "Seeed wiki, webcam example on battery"),
    ("XIAO, Wi-Fi connected, camera idle", "3V3 regulator", 110, 150, "Seeed wiki, Wi-Fi active"),
    ("OLED, all pixels", "3V3 pin", 20, 25, "SSD1306 module, typical"),
    ("Amp + speaker at the cap of 65", "BAT+ rail", 60, 250, "0.47 W into 8 Ω at 4.2 V, 85 % efficient"),
    ("Pan motor, running / stalled", "BAT+ rail", 100, 360, "12 mm class; this listing publishes none: measure yours"),
    ("Tilt motor, running / stalled", "BAT+ rail", 100, 360, "same motor; the firmware moves one axis at a time"),
]

CHECKS = [
    ("Holder polarity", "Cell in, nothing else connected: meter DC V on the holder leads. Red lead must read +3.6 to +4.2 V. If it reads negative the leads are swapped; swap them at the holder, never at the pads. On the XIAO's back, the BAT− pad is the one nearer the USB-C socket."),
    ("No shorts, unpowered", "Switch OFF, cell out. Ω between the BAT+ rail and GND: open or above 1 kΩ (the 220 µF makes it climb). 3V3 to GND: above 1 kΩ. BAT+ to 3V3: open."),
    ("OLED silkscreen", "Hold the module next to the sheet and read the four pin names before you solder. Two vendors, two orders."),
    ("Driver inputs", "Unpowered, Ω from each of IN1-IN4 to GND on the bare module. Under 100 kΩ means it has its own pull-downs and R2, R3, R7, R8 can go; open means keep them."),
    ("The ladder, unpowered", "Ω from the S pin to GND with nothing pressed: open. Press the button: 680 Ω. The pan stop: 2.2 kΩ. The tilt stop: 5.6 kΩ. Both stops: 1.6 kΩ. If a reading is off by more than 10 % a resistor is in the wrong place."),
    ("Bench supply first", "Holder empty. SKY TOPPOWER at 3.8 V, limit 0.5 A, + to the switch's 'in', − to GND. Switch ON: the XIAO boots, 3V3 pin reads 3.25-3.35 V, draw under 200 mA with the screen on. Then the camera stream: under 400 mA, no resets."),
    ("The ladder, powered", "Meter DC V on D10: 3.3 V with nothing pressed, about 0.21 V on the button, 0.60 V on the pan stop, 1.18 V on the tilt stop, 0.45 V with both stops. The firmware's bands sit halfway between."),
    ("Motors, head off the shafts", "Raise the limit to 1.5 A. Each motor in turn: 50 % PWM one way, then the other. Note the running current; stall it with a finger for one second and note the peak. Under 0.5 A stalled is the pass. Then with the head on: tilt down to the stop, pan to the stop, and watch that the wires coil and uncoil without pulling."),
    ("First charge, watched", "Cell in, switch ON, USB in, device asleep. Meter in series with the cell's + lead on the mA range: expect roughly 100 mA (Seeed says 100; one datasheet says 50). Cell cooler than 45 °C by touch after twenty minutes. The red LED goes out when it is full; the first full charge is not left unattended."),
    ("Speaker", "Volume cap 65 in the firmware, GAIN pin open. Scope the speaker differentially (A−B, both grounds on GND, never on a speaker lead): under 2.7 V peak."),
]

WHY = [
    ("One cell, no boost", "Every part on this sheet accepts 3.0-4.2 V: the XIAO has its own regulator and charger, the MX1508 runs from 2 V, the MAX98357A from 2.5 V, the OLED sits on the XIAO's 3.3 V. So the design has one rail, the cell itself. The PowerBoost, the 5 V harness points and the load-sharing worry of the first build all go away."),
    ("Eyes first, then the head", "The camera sees about 65° across; the eyes drawn on the 0.96 inch screen can only look about 20° off centre before they run out of glass. So the firmware finds the face in the frame and slides the eyes toward it first. When the face drifts past the eyes' reach, the head turns on its motors until the face is centred again and the eyes settle back to the middle. Eyes jump, head follows a beat later: a saccade, the thing that makes a face read as alive. The camera and the screen share one head, so where the camera looks is where the eyes look, by construction; the difference you would otherwise build with a second gimbal is drawn in pixels."),
    ("Two axes, two gear motors, one driver", "Pan from the body, tilt inside the head. The MX1508 has two bridges, so the second motor costs two pins and two pull-downs, not a board. The tilt axis runs through the head's centre of mass, so the tilt motor holds no weight and the gearbox's own friction keeps the head where it was left. Both motors were on hand on 2026-11-03."),
    ("Why the MX1508 and not the L298N", "The L298N's bipolar outputs lose 2-3 V and its onboard regulator wants 7 V or more. From a single 16340 a real L298N would hand the motor about 1 V. The board the builder linked is the MX1508: MOSFET outputs, 2-10 V in, inputs that read 3.3 V as high. Four control pins, two bridges, and both are used now."),
    ("Why a DC gear motor needs a home stop", "A DC motor has no idea where it is. The 16 rpm gearbox makes timed moves repeatable (100 ms is about 10°), but drift adds up, so the firmware drives each axis to its stop at boot and whenever it is unsure: tilt first, face down, then pan to the left stop, then up and centre. One switch per axis. A hobby servo would do all of this in one three-wire part; it wants 5 V and is louder and jerkier, so the motors stand."),
    ("Twelve signals, eleven pins: the ladder", "The header has eleven pins. Three I2S, one amp shutdown, two I2C, four motor inputs: ten. The action button, the pan stop and the tilt stop would make thirteen, so the three share one ADC pin through a resistor ladder: a 10 kΩ pull-up to 3.3 V, and each switch pulls the pin down through its own resistor. Nothing pressed is 3.3 V; the button alone 0.21 V, the pan stop 0.60 V, the tilt stop 1.18 V, both stops 0.45 V, and any combination with the button under 0.25 V. The firmware reads a band, not a level, and ignores the button while it is homing. 5 % resistors and the ADC's own error move each reading by 50 mV; the gaps are 200 mV or more. The script asserts that."),
    ("Why SCL sits on the UART pin", "GPIO43 is UART0 TX, and the boot ROM prints on it for about a hundred milliseconds before the firmware runs. Rev A left it spare for that reason. Rev B needs the pin, so it carries the one signal that boot chatter cannot disturb: the I2C clock. An I2C start is SDA falling while SCL is high; with SDA idle on its pull-up, clock pulses alone are nothing to the SSD1306. Any S3 pin can be I2C through the GPIO matrix, and the console goes over USB, so nothing is lost. GPIO44 (UART0 RX) is an input at boot and drives the tilt motor's IN4 through its pull-down, which holds the driver input at 0.6 V, far under its threshold."),
    ("Why the amp keeps its shutdown line", "An easy way to find a pin would be to leave the amp's SD open and let it run whenever the cell is on. The MAX98357's maker says to shut the amp down before stopping its clocks, else the output can sit at DC across the speaker. So R1 and the SD line stay, the amp is off until the firmware raises SD, and the pin came from the ladder instead."),
    ("Why the amp runs from BAT+ and the OLED from 3V3", "The XIAO's 3.3 V regulator is good for 700 mA, and the S3 with the camera can take 370 mA of that on its own. The amp (250 mA peaks) and a motor (360 mA stalled) would push it over, so they take the cell directly, which both are rated for. The OLED's 20 mA rides on 3V3 as before."),
    ("Charging through the XIAO, and its limit", "The XIAO's charger is an SGM40567 set to 50-100 mA (the wiki says 100, the datasheet 50, owners report both). The device awake draws more than that, so with USB in and the switch ON the cell still goes down unless the firmware deep-sleeps. In-device charging is therefore an overnight trickle with the device asleep: 10-20 hours from empty. The charger has no thermistor input: room temperature only, first cycle watched. The practical path is to pull the cell and use an external 16340 charger (about 2 hours); the protected NL169 is made for that, and thirteen cells means one is always charged. That charger is the one optional item not yet owned."),
    ("USB in with the switch OFF", "The XIAO runs from USB for flashing and bench work with no cell. The amp stays off (R1 holds SD low) and the driver idles at under 1 mA, so the dead BAT+ rail is harmless. Never run a motor or the amp in this state: the rail has no cell behind it."),
    ("The 5V pin", "On the XIAO it is the USB VBUS, nothing more. On battery it reads 0 V. Nothing in this design touches it, and nothing ever feeds it."),
    ("Bare rods where nothing moves, five wires where it does", "The builder wires with bare rod, as the first harness did: the owned 1.0 mm brass, soldered to the header pins at height levels so no two nets touch. Inside the head and inside the body every connection on the sheet is a rod. The two joints are different: a rod cannot flex ten thousand times, so the five connections that cross them (BAT+ and GND down to the head in 26 AWG; the ladder and the tilt motor's pair in 30 AWG) are silicone wire, run up one yoke upright as a single line, with a loose coil round the pan hub and a loop at the tilt pin. The holder, the motors and the speaker keep their factory leads, and the XIAO's BAT pads on the back of the board get a 10 mm flexible stub each rather than a rod soldered to a surface pad. Resistance is not a concern: 50 mm of 1.0 mm brass is 4 mΩ, nothing at 1 A. The frame stays floating, so every rod keeps 2 mm from it, as before."),
    ("Colour, under the rules of 2026-11-07 and 11-09", "White, ivory or black as much as possible; the frame its own metal; no paint and no skins. The frame and the yoke are bare brass. The screen is white on black glass, the XIAO and its Sense board are black, the speaker, the holder and the switch body are black, the switch lever and the motors are bare metal, the wires that show are white or black from the owned kits, the heat-shrink is white. The parts that come in other colours are placed where they do not show: the driver (red or blue) behind the holder in the body, the amp under the speaker, the OLED's board (blue on some packs) behind its own glass, the cell's printed wrap inside the holder. The one owned part this build does not use for colour reasons is nothing: there is no part to replace."),
    ("What the Sense board owns", "Fourteen GPIOs for the camera, two for the PDM microphone, and the SD slot's SPI on GPIO7/8/9, which are the header's D8-D10. Those three carry the pan motor and the ladder here, so the SD slot stays empty for good. That leaves exactly the eleven header pins on the sheet, all eleven in use."),
]


def parts_html():
    o = ['<h2 id="parts">Parts, with the exact listing</h2>',
         '<p>Nothing is left to buy as of 2026-11-10: the second motor, the stops and the ladder resistors are all on hand. The five Amazon listings are the ones the builder ordered on 2026-10-27; owned items are listed with the inventory that records them. The one part not yet in the building is the controller pair.</p>']
    for head, rows in PARTS:
        o.append(f"<h3>{esc(head)}</h3><div class='tw'><table><tr><th>Qty</th><th>Part</th><th>Where</th><th>Price</th><th>Why, and what to check</th></tr>")
        for qty, part, url, where, price, why in rows:
            o.append(f"<tr><td class='m'>{esc(qty)}</td><td>{a(part, url)}</td><td>{esc(where)}</td><td>{esc(price)}</td><td>{esc(why)}</td></tr>")
        o.append("</table></div>")
    return "\n".join(o)


def outline_html():
    o = ['<h2 id="why">Why each wire</h2>',
         '<div class="tw"><table><tr><th>Net</th><th>From</th><th>To</th><th>Wire</th><th>Why</th></tr>']
    for net, src, dst, wire, why in NETS:
        o.append(f"<tr><td class='m'>{esc(net)}</td><td>{esc(src)}</td><td>{esc(dst)}</td><td>{esc(wire)}</td><td>{esc(why)}</td></tr>")
    o.append("</table></div>")
    for h, body in WHY:
        o.append(f"<h3>{esc(h)}</h3><p>{esc(body)}</p>")
    return "\n".join(o)


def ladder_html():
    v = ladder_volts()
    order = ["none", "action button", "pan stop", "tilt stop", "pan stop + tilt stop", "action button + pan stop", "action button + tilt stop", "action button + pan stop + tilt stop"]
    o = ['<h2 id="ladder">The ladder, state by state</h2>',
         '<p>10 kΩ pull-up to 3.3 V on D10; each switch to GND through its own resistor. Volts at the pin for every combination, nominal; the firmware reads bands halfway between neighbours and ignores the button while it homes.</p>',
         '<div class="tw"><table><tr><th>Pressed</th><th>Volts at D10</th><th>Firmware reads</th></tr>']
    for k in order:
        reads = "nothing" if k == "none" else ("button" if "action button" in k else k)
        o.append(f"<tr><td>{esc(k)}</td><td class='m'>{v[k]:.2f} V</td><td>{esc(reads)}</td></tr>")
    o.append("</table></div>")
    return "\n".join(o)


def pins_html():
    o = ['<h2 id="pins">The pin map</h2>',
         '<p>All eleven header pins of the XIAO, all in use. Fixed by the Sense board: camera on GPIO 10-18, 38-40, 47, 48; PDM microphone on 41 (data) and 42 (clock); SD slot chip select on 21, SPI on 7/8/9.</p>',
         '<div class="tw"><table><tr><th>Header</th><th>GPIO</th><th>Net</th><th>Job</th></tr>']
    for hdr, g, job, net in PINS:
        o.append(f"<tr><td class='m'>{hdr}</td><td class='m'>{g}</td><td class='m'>{net or '—'}</td><td>{esc(job)}</td></tr>")
    o.append("</table></div>")
    return "\n".join(o)


def budget_html():
    o = ['<h2 id="power">Does the cell carry it?</h2>',
         '<p>The NL169 is a protected 950 mAh cell rated 2 A continuous. The device never asks for half of that.</p>',
         '<div class="tw"><table><tr><th>Load</th><th>Fed from</th><th>Typical</th><th>Peak</th><th>Figure from</th></tr>']
    for load, src, typ, pk, ref in BUDGET:
        o.append(f"<tr><td>{esc(load)}</td><td>{esc(src)}</td><td class='m'>{typ} mA</td><td class='m'>{pk} mA</td><td>{esc(ref)}</td></tr>")
    o.append("</table></div>")
    o.append('<div class="sched"><div class="t">3V3 regulator</div><div>Camera streaming 366 + OLED 25 = about 390 mA peak, inside the regulator\'s 700 mA. The amp and the motors are deliberately not on it.</div>'
             '<div class="t">Cell, worst second</div><div>390 + 250 + 360 = about 1.0 A if a motor stalls while it talks and streams. The firmware moves one axis at a time; even both stalled at once would be 1.36 A, under the cell\'s 2 A trip. The switch and the 26 AWG leads see this current; the 30 AWG signal wires never do.</div>'
             '<div class="t">Cell, average</div><div>Listening and talking with the camera on and the head following: about 270 mA, so about 3 hours. Wi-Fi idle with the camera off: about 130 mA, about 7 hours. Deep sleep on the Sense board is 3 mA.</div>'
             '<div class="t">Charge</div><div>50-100 mA from the XIAO\'s USB-C at the back of the head: 10 to 20 hours from empty, and only with the device asleep. An external 16340 charger (optional, not owned) does it in about two.</div></div>')
    return "\n".join(o)


def checks_html():
    o = ['<h2 id="checks">Meter checks before the first power-up</h2><ul class="check">']
    for h, body in CHECKS:
        o.append(f"<li><strong>{esc(h)}.</strong> {esc(body)}</li>")
    o.append("</ul>")
    return "\n".join(o)


def firmware_html():
    return "\n".join([
        '<h2 id="firmware">What changes in the firmware</h2>',
        '<p>The Pip character firmware (ESP-IDF 6.0.2) was written for the ESP32-C3. The port is a pin map and four drivers, not a rewrite:</p>',
        '<ul>',
        '<li><strong>Target</strong> esp32s3; keep the volume cap of 65, the amp-off-until-SD rule and the 8.5 dBm transmit cap as a config option (the XIAO has a real antenna; the cap can probably be lifted after an A/B test). Console on USB-serial-JTAG, not UART0.</li>',
        '<li><strong>Audio out</strong> I2S standard TX on GPIO1/2/3, amp SD on GPIO4, exactly as the sheet. SD low before the clocks stop, every time.</li>',
        '<li><strong>Microphone</strong> I2S PDM RX on GPIO42 (clock) and GPIO41 (data) replaces the INMP441 driver. 16 kHz mono as before.</li>',
        '<li><strong>Screen</strong> I2C on GPIO5 (SDA) and GPIO43 (SCL) through the GPIO matrix.</li>',
        '<li><strong>Camera</strong> the esp32-camera component with the XIAO ESP32S3 Sense pin table; OV2640 and OV5640 both initialise from it. Frames go into PSRAM; a face box from the frame drives the eyes and, past ±20°, the head.</li>',
        '<li><strong>Motors</strong> LEDC PWM on GPIO7/8 (pan) and GPIO6/44 (tilt) at 20 kHz (above hearing, under the MX1508\'s 50 kHz), duty capped at 70 %, one axis at a time. Home at boot: tilt down to its stop, pan to its stop, then level and centre; timed moves from there; re-home on any doubt.</li>',
        '<li><strong>Ladder</strong> ADC1 channel 8 (GPIO9), 12 dB attenuation, read at 100 Hz with a 4-sample average; bands at 0.33, 0.52, 0.85 and 1.6 V; the button is ignored while homing. Short press talks, long press resets Wi-Fi.</li>',
        '</ul>',
        '<p>None of this exists yet. The first bench step is the XIAO alone on USB with the screen, the same way the first build started.</p>'])


def page_html():
    return "\n".join([
        '<title>Pocket AI with Camera</title>',
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap">',
        "<style>" + STYLE + "</style>",
        '<style>body{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))} .wrap{padding-inline:0;max-width:1100px} figure.sheet{padding:8px} figure.sheet svg{width:100%;height:auto} figure.tower svg{max-width:880px}</style>',
        '<div class="wrap">',
        f'<div class="masthead"><div class="eyebrow">Pocket AI Assistant &middot; camera build &middot; {REV}</div>',
        '<h1>A tower that looks around, and up and down</h1>',
        f'<div class="sub">The second Pocket AI: a XIAO ESP32-S3 Sense (camera + mic + charger) in a head that tilts inside a brass yoke and turns on the body, the owned screen, amp and speaker, two gear motors on one MX1508, and one Nitecore 16340 cell that charges through the XIAO\'s USB-C.<br>{REV} drawn {DRAWN} for approval: adds the tilt axis, the yoke, and the three-button ladder. Rev A was 2026-10-27. Nothing built yet. Source of truth: <code>pocket_ai_assistant_with_camera/docs/WIRING.md</code> and <code>COMPONENTS.md</code>.</div></div>',
        f'<figure class="sheet">{sheet()}<figcaption><strong>Print it landscape on Letter; it is page 1 of the PDF.</strong> Thick lines are wires you solder, the brass line is the cell\'s rail, thin lines are resistor and capacitor legs. A dot is a joint; a hop is a crossing that does not touch; a ground symbol is a wire to GND. The whole power chain is on it: cell, holder, switch, rail, the XIAO\'s charger pads, the amp and the driver.</figcaption></figure>',
        '<div class="note warn"><span class="lbl">Three rules that do not bend</span>'
        '<p>The cell is the only power source: nothing is ever fed into the XIAO\'s 5V pin, and nothing else is ever connected to its BAT pads. '
        'The speaker\'s two leads are not ground: no scope ground, no GND wire, ever. '
        'The brass frame is not a conductor: every joint is insulated from it, as in the first build.</p></div>',
        pins_html(),
        f'<h2 id="tower">The tower</h2><p>The head carries everything that talks to the world: camera, microphone, screen, speaker, and the tilt motor whose shaft is fixed to the yoke. The yoke is a U of brass tube on the pan motor\'s shaft. The body carries everything heavy and still: the cell, the switch, the driver, the pan motor, the button.</p>'
        f'<figure class="tower">{tower()}<figcaption>Targets, not measurements: head 50 × 42 × 50 mm, yoke 56 mm across, body 50 × 42 × 62 mm, 122 mm overall, about 95 g with the cell. Pan ±150°, tilt ±90°. Runtime about 3 hours following and talking, 7 idle; charge 10-20 hours through the XIAO asleep, 2 hours in an external charger. Caliper every module, the motors most of all, before the frame is cut.</figcaption></figure>',
        outline_html(),
        ladder_html(),
        budget_html(),
        checks_html(),
        firmware_html(),
        parts_html(),
        '<hr><p class="sub">Built by <code>docs/pages/gen/wiring_board.py</code>. The script audits the pin map against the Sense board\'s reserved GPIOs, audits the ladder\'s voltages against 5 % resistors, and checks every drawn line for clearance before it writes anything. The electrical figures come from the Seeed wiki, the MAX98357 datasheet and vendor listings, not from measurement.</p>',
        '</div>'])


# ----------------------------------------------------------------------------- markdown companions
def components_md():
    o = ["# Components", "",
         f"**Nothing is left to buy as of {DRAWN} ({REV}).** The five Amazon listings below are the builder's order of 2026-10-27;",
         "owned items come from `pocket_ai_assistant/docs/INVENTORY.md` and `cyber_clock_v2/docs/INVENTORY.md` and are",
         "listed so they are not bought twice. The controller pair is the only line not yet in the building. Generated by",
         "`pages/gen/wiring_board.py`; edit the script, not this file.", ""]
    for head, rows in PARTS:
        o += [f"## {head}", "", "| Qty | Part | Where | Price | Why, and what to check |", "| ---: | --- | --- | --- | --- |"]
        for qty, part, url, where, price, why in rows:
            o.append(f"| {qty} | {md_link(part, url)} | {where} | {price} | {why} |")
        o.append("")
    o += ["## The simpler alternative, not chosen", "",
          "Two 9 g hobby servos (MG90S, about $4 each, black) would replace both motors, both stops, the ladder's two stop",
          "resistors and four pull-downs with two three-wire parts that know their own angle. They want 4.8-6 V and run weak",
          "and jerky at the cell's 3.7 V, and they are louder than a 16 rpm gearbox, which is why the builder's motors stand.",
          "If the motor path proves fiddly, the sheet changes by two blocks and a 5 V boost comes back.", ""]
    return "\n".join(o)


def wiring_md():
    v = ladder_volts()
    o = ["# Wiring", "",
         f"The net list, the pin audit, the ladder, the current budget and the meter checks for the camera build, {REV} ({DRAWN}).",
         "Drawn as `pages/wiring-board.html` (PDF in `pages/print/`). Generated by `pages/gen/wiring_board.py`; edit the script.",
         "Nothing here has been built or measured; every figure is from the Seeed wiki, the MAX98357 datasheet or a vendor listing.", "",
         "## Pin map", "", "| Header | GPIO | Net | Job |", "| --- | ---: | --- | --- |"]
    for hdr, g, job, net in PINS:
        o.append(f"| {hdr} | {g} | `{net or '—'}` | {job} |")
    o += ["", "Reserved by the Sense expansion board, never on the sheet:", ""]
    for owner, gs in RESERVED.items():
        o.append(f"- {owner}: GPIO {', '.join(str(g) for g in sorted(gs))}")
    o += ["", "The script asserts that no header pin on the sheet collides with the camera or the microphone, that D8-D10",
          "(the SD slot's SPI) are the only overlap and the slot stays empty, that the only strapping pin in use is",
          "GPIO3, which does nothing on a stock XIAO, that the ladder sits on an ADC1 pin, and that every ladder state",
          "is separable with 5 % resistors and 30 mV of ADC error.", "",
          "## Net list", "", "| Net | From | To | Wire | Why |", "| --- | --- | --- | --- | --- |"]
    for net, src, dst, wire, why in NETS:
        o.append(f"| `{net}` | {src} | {dst} | {wire} | {why} |")
    o += ["", "## The ladder, state by state", "", "| Pressed | Volts at D10 |", "| --- | ---: |"]
    for k in ["none", "action button", "pan stop", "tilt stop", "pan stop + tilt stop", "action button + pan stop", "action button + tilt stop", "action button + pan stop + tilt stop"]:
        o.append(f"| {k} | {v[k]:.2f} V |")
    o += ["", "Bands in the firmware: under 0.33 V the button (any combination), 0.33-0.52 V both stops, 0.52-0.85 V the pan stop,",
          "0.85-1.6 V the tilt stop, above 2 V nothing. The button is ignored while homing.", "", "## Why", ""]
    for h, body in WHY:
        o += [f"### {h}", "", body, ""]
    o += ["## Current budget", "", "| Load | Fed from | Typical | Peak | Figure from |", "| --- | --- | ---: | ---: | --- |"]
    for load, src, typ, pk, ref in BUDGET:
        o.append(f"| {load} | {src} | {typ} mA | {pk} mA | {ref} |")
    o += ["",
          "- 3V3 regulator: camera streaming 366 + OLED 25 ≈ 390 mA peak, inside the XIAO's 700 mA. The amp and the motors are not on it.",
          "- Cell, worst second: 390 + 250 + 360 ≈ 1.0 A if a motor stalls while it talks and streams; one axis moves at a time; both stalled would be 1.36 A, under the NL169's 2 A trip.",
          "- Cell, average: about 270 mA listening, talking and following with the camera on, so about 3 h; about 130 mA Wi-Fi idle, about 7 h; 3 mA in deep sleep.",
          "- Charge: 50-100 mA through the XIAO's USB-C (SGM40567; Seeed wiki says 100, datasheet 50), so 10-20 h from empty and only with the device asleep. An external 16340 charger (optional, not owned) does it in about 2 h.",
          "- Amp: volume cap 65 and GAIN open; at a full 4.2 V cell the worst case is (0.65 × 4.2)² / 2 / 8 Ω = 0.47 W into the 0.8 W speaker.",
          "- Motors: rated 3 V, run at ≤ 70 % PWM so the average voltage stays under 3 V at a full cell.", "",
          "## Meter checks before the first power-up", ""]
    for i, (h, body) in enumerate(CHECKS, 1):
        o.append(f"{i}. **{h}.** {body}")
    o += ["", "## Firmware changes (none written yet)", "",
          "- Target esp32s3; keep the cap of 65, amp off until SD (and SD low before the clocks stop), the tx-power cap as an option; console on USB-serial-JTAG.",
          "- I2S standard TX on GPIO1/2/3, SD on GPIO4; I2S PDM RX on GPIO42 (clk) / GPIO41 (data) replaces the INMP441 driver; I2C on GPIO5/43.",
          "- esp32-camera with the XIAO ESP32S3 Sense pin table (OV2640 and OV5640 both work); frames in PSRAM; the face box drives the eyes, and past ±20° the head.",
          "- LEDC PWM on GPIO7/8 (pan) and GPIO6/44 (tilt) at 20 kHz, duty ≤ 70 %, one axis at a time; home tilt then pan at boot and on doubt.",
          "- ADC1 ch 8 (GPIO9) reads the ladder at 100 Hz; bands at 0.33 / 0.52 / 0.85 / 1.6 V; button ignored while homing.", ""]
    return "\n".join(o)


# ----------------------------------------------------------------------------- output
def print_pdf(html, sheet_svg):
    PRINT.mkdir(exist_ok=True)
    sheet_css = ("<style>@page{size:letter landscape;margin:7mm} html,body{background:#fff;margin:0}"
                 ":root{--paper:#fff;--ink:#000;--ink-2:#333;--brass:#000;--brass-soft:#eee;--signal:#000;--signal-soft:#eee}"
                 "svg{width:262mm;height:auto;display:block;margin:0 auto}</style>")
    page_css = ("<style>@page{size:letter;margin:12mm 13mm 14mm}"
                ":root{--bg:#fff;--paper:#fff;--ink:#000;--ink-2:#333;--line:#999;--brass:#000;--brass-soft:#f2f2f2;--signal:#000;--signal-soft:#f2f2f2;--ok:#000;--ok-soft:#f2f2f2;--warn:#000;--warn-soft:#f4f4f4}"
                "html,body{background:#fff!important;color:#000!important;font-size:10pt!important;line-height:1.4} .wrap{max-width:none;padding:0} body{padding:0}"
                "figure.sheet{display:none} h2{font-size:14pt;margin-top:16pt;page-break-after:avoid} h3{font-size:9.5pt;margin-top:10pt} p,ul,ol{max-width:none} table{font-size:8.5pt} th,td{padding:4pt 6pt}"
                ".note{margin:10pt 0;padding:8pt 10pt} .note p{margin:3pt 0} a{color:#000;text-decoration:none} .masthead{border-bottom-width:2px;padding-bottom:8pt} h1{font-size:20pt}"
                "tr{break-inside:avoid} ul.check li{break-inside:avoid} figure.tower{break-inside:avoid}</style>")
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        (d / "s.html").write_text("<!doctype html><meta charset=utf-8><title>sheet</title>" + sheet_css + sheet_svg)
        (d / "p.html").write_text("<!doctype html><meta charset=utf-8>" + html.replace("</style>", "</style>" + page_css, 1))
        for src, pdf in (("s.html", "s.pdf"), ("p.html", "p.pdf")):
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                            f"--print-to-pdf={d / pdf}", f"file://{d / src}"], check=True, capture_output=True, timeout=180)
        out = PRINT / "wiring-board.pdf"
        subprocess.run(["pdfunite", str(d / "s.pdf"), str(d / "p.pdf"), str(out)], check=True)
        shutil.copyfile(d / "s.pdf", PRINT / "wiring-board-sheet.pdf")
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print("wrote", out, [l for l in info.splitlines() if l.startswith("Pages")])


def preview_png(svg_text, path, width=2720, height=1760):
    """A PNG of one figure, for checking the drawing by eye."""
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        (d / "s.html").write_text("<!doctype html><meta charset=utf-8><style>:root{--paper:#fff;--ink:#000;--ink-2:#333;--brass:#8F6114;--signal:#0E5F7A;--signal-soft:#D9EAF1}body{margin:0;background:#fff}svg{width:%dpx;height:auto;display:block}</style>" % width + svg_text)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--window-size={width},{height}",
                        f"--screenshot={path}", f"file://{d / 's.html'}"], check=True, capture_output=True, timeout=180)
    print("preview", path)


if __name__ == "__main__":
    audit()
    svg = sheet()
    html = page_html()
    OUT.write_text(html)
    (DOCS / "COMPONENTS.md").write_text(components_md())
    (DOCS / "WIRING.md").write_text(wiring_md())
    print("wrote", OUT, DOCS / "COMPONENTS.md", DOCS / "WIRING.md")
    if "--pdf" in sys.argv:
        print_pdf(html, svg)
    if "--png" in sys.argv:
        preview_png(svg, sys.argv[sys.argv.index("--png") + 1])
    if "--tower-png" in sys.argv:
        preview_png(tower(), sys.argv[sys.argv.index("--tower-png") + 1], 1920, 1400)
