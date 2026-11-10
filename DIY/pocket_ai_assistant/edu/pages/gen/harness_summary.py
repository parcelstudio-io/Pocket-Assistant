"""Builds edu/pages/brass-harness-connections.html: the net list of the harness as one page."""
from __future__ import annotations

import pathlib
import re

import harness_model as M
import harness_draw as D

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "brass-harness-connections.html"
STEP_URL = "https://claude.ai/artifact/FAsL4WPArRK6QW7yEg2Nix"

LEVEL = {0.5: "on the card", 3.0: "stub level, 3 mm", 5.5: "5.5 mm", 7.5: "7.5 mm", 9.5: "9.5 mm"}


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def rod(name):
    return next(r for r in M.rods() + M.small_parts() if r.name == name)


def level_of(c):
    zs = sorted({p[2] for p in c.pts})
    top = max(zs)
    if top <= 0.6:
        return "on the card"
    if top <= 3.1:
        return "3 mm, beside the stubs"
    return f"rises to {top:g} mm"


def main():
    rods = {c.name: c for c in M.rods()}
    H = ['<title>Brass Harness Connections</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style(), '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · step 4d · net list</div>',
         '<h1>Brass harness: what connects to what</h1>',
         f'<p class="lede">The whole harness as one list. 11 pins leave A1; 2 rails carry power and ground to everything; 2 resistors and 2 capacitors sit between. Rod names, lengths and heights match the <a href="{STEP_URL}" target="_blank" rel="noopener">step-by-step page</a>, which is where the drawings and the build order are.</p>']

    # ------------------------------------------------------------ rails
    H.append('<h2>The two rails</h2>')
    H.append('<p><strong>A rail is a bare, straight 1 mm rod lying on the jig card during the build; in the finished device it hangs on its taps, lowest thing in the cage.</strong> It is the one wire that many parts share: every part\'s ground hooks onto the GND rail, every 3.3 V part hooks onto the 3V3 rail. A1 feeds each rail once; after that nobody runs a rod back to A1 for power.</p>')
    H.append('<div class="scrollx"><table class="t"><tr><th>Rail</th><th>Where</th><th>Fed by</th><th>Who hooks on</th></tr>'
             '<tr><td><strong>3V3 rail</strong></td><td class="n">x = 24, y = 2.5 → 23.5, on the card (21 mm)</td><td>A1 3V3 stub, by the 3V3 tap</td><td>screen VCC, mic VDD, R3 (10 kΩ pull-up)</td></tr>'
             '<tr><td><strong>GND rail</strong></td><td class="n">x = 27, y = 2.0 → 23.5, on the card (21.5 mm)</td><td>A1 GND stub, by the GND rod and a 3 mm drop pin</td><td>amp GND (through the GND rod), screen GND, mic GND, mic L/R, button, R4, the 220 µF −</td></tr>'
             '</table></div>')
    H.append('<p>They lie in the channel, the 8.5 mm gap between A1 and the amp, 3 mm apart, 2 mm from the front edge, ending 1 mm short of the mic. The straight rods cross 1.5 mm above them. x is millimetres from the left wall, y from the front wall.</p>')
    H.append(D.fig(D.map_figure(highlight={"3V3 rail", "GND rail", "3V3 tap", "GND drop pin"}, title="The two rails and the two pieces that feed them"),
                   '<strong>Bold: the rails, the 3V3 tap and the GND drop pin.</strong> Everything else faded for position.') if hasattr(D, "fig") else
             f'<figure><div class="scroll">{D.map_figure(highlight={"3V3 rail", "GND rail", "3V3 tap", "GND drop pin"}, title="The two rails and the two pieces that feed them")}</div><figcaption><strong>Bold: the rails, the 3V3 tap and the GND drop pin.</strong> Everything else faded for position.</figcaption></figure>')

    # ------------------------------------------------------------ A1 pins
    H.append('<h2>Every A1 pin that is used</h2>')
    rows = [
        ("5V", "amp VIN", "5 V rod", "USB power for the amp only; the 220 µF hangs on this net"),
        ("GND", "amp GND, and the GND rail", "GND rod + GND drop pin", "one straight rod to the amp; the pin under it makes the rail ground"),
        ("3V3", "3V3 rail", "3V3 tap", "feeds the screen and the mic"),
        ("GPIO4", "mic SD", "mic SD rod", "sound in; pulled down inside A1 by the firmware (no resistor since 2026-10-14)"),
        ("GPIO3", "amp DIN", "DIN rod", "sound out"),
        ("GPIO2", "amp BCLK, then mic SCK", "BCLK rod", "one rod, two taps; R3 (10 kΩ) to 3V3 on this net"),
        ("GPIO1", "amp LRC, then mic WS", "WS rod", "one rod, two taps"),
        ("GPIO5", "amp SD", "amp SD rod", "amplifier on/off; R1 (4.7 kΩ) to GND on this net"),
        ("GPIO10", "button", "button rod", "the button's other side goes to A1 GND"),
        ("GPIO20", "screen SCL", "SCL rod", "I²C clock"),
        ("GPIO21", "screen SDA", "SDA rod", "I²C data"),
    ]
    H.append('<div class="scrollx"><table class="t"><tr><th>A1 pin</th><th>Goes to</th><th>By</th><th>Length</th><th>Height</th><th>Note</th></tr>')
    for pin, to, by, note in rows:
        names = [n.strip() for n in by.split("+")]
        c = rods[names[0]]
        L = sum(rods[n].length() for n in names)
        H.append(f'<tr><td class="n">{pin}</td><td>{to}</td><td>{by}</td><td class="n">{L:.0f} mm</td><td>{level_of(c)}</td><td>{note}</td></tr>')
    H.append('</table></div>')
    H.append('<p>Unused and left as stubs: GPIO0, 6, 7, 8, 9. GPIO9 is the BOOT button, never an input.</p>')

    # ------------------------------------------------------------ taps
    H.append('<h2>Power and ground taps</h2>')
    H.append('<div class="scrollx"><table class="t"><tr><th>Part pin</th><th>To</th><th>By</th><th>Length</th></tr>')
    taps = [("screen GND", "GND rail, front end", "screen GND tap"), ("screen VCC", "3V3 rail, front end", "screen VCC tap"),
            ("mic GND", "GND rail, back end", "mic GND tap"), ("mic VDD", "3V3 rail, back end", "mic VDD tap"),
            ("mic L/R", "mic GND stub (selects the left slot)", "L/R link"), ("button, right legs", "A1 GND stub", "button GND rod"),
            ("amp GND", "A1 GND stub", "GND rod")]
    for pin, to, by in taps:
        H.append(f'<tr><td>{pin}</td><td>{to}</td><td>{by}</td><td class="n">{rods[by].length():.0f} mm</td></tr>')
    H.append('</table></div>')

    # ------------------------------------------------------------ small parts
    H.append('<h2>The six small parts</h2>')
    H.append('<div class="scrollx"><table class="t"><tr><th>Part</th><th>Between</th><th>Why</th><th>Where it sits</th></tr>'
             '<tr><td><strong>R1</strong> 4.7 kΩ (or the 1 kΩ you chose in Step 11)</td><td>amp SD stub ↔ amp GND stub</td><td>holds the amp off while A1 boots</td><td>a U lying over the amp board</td></tr>'
             '<tr><td><s>R2</s> 100 kΩ</td><td>—</td><td>dropped 2026-10-14: GAIN open is 9 dB; fit 100 kΩ GAIN↔GND later for 15 dB</td><td>—</td></tr>'
             '<tr><td><strong>R3</strong> 10 kΩ</td><td>BCLK rod ↔ 3V3 rail</td><td>GPIO2 reads high at boot</td><td>in the channel, 8.5 mm up</td></tr>'
             '<tr><td><s>R4</s> 100 kΩ</td><td>—</td><td>dropped 2026-10-14: the firmware enables GPIO4\'s internal pull-down</td><td>—</td></tr>'
             '<tr><td><strong>C1</strong> 220 µF, stripe to GND</td><td>5 V net ↔ GND rod</td><td>bass and Wi-Fi bursts don\'t sag the 5 V</td><td>lying in the right strip, leads sleeved along the floor</td></tr>'
             '<tr><td><strong>C2</strong> 100 nF</td><td>amp VIN stub ↔ amp GND stub</td><td>the fast part of the same job, right at the pins</td><td>flat on the amp board</td></tr>'
             '</table></div>')

    # ------------------------------------------------------------ never
    H.append('<h2>Never connected</h2>')
    H.append('<ul><li><strong>OUT+ and OUT−</strong> go only to the speaker\'s own two leads. Never to GND, a rail, or the frame.</li>'
             '<li><strong>The frame</strong> carries nothing. Every rail and rod stays 2 mm from it, with Kapton on the tubes.</li>'
             '<li><strong>5 V</strong> reaches the amp only. The screen and mic live on 3V3.</li></ul>')

    # ------------------------------------------------------------ map
    H.append('<h2>All of it on one map</h2>')
    H.append(f'<figure><div class="scroll">{D.map_figure(title="Every rod, top view")}</div><figcaption><strong>Front at the bottom.</strong> Dots are stubs, dotted stretches are heat-shrink, the dashed square is the screen floating above.</figcaption></figure>')
    H.append('<div class="legend">' + "".join(
        f'<div><span class="sw" style="background:{D.NET_COLOR[n]}"></span>{D.NET_LABEL[n]}</div>' for n in ["5V", "GND", "3V3", "GPIO1", "GPIO2", "GPIO3", "GPIO4", "AMPSD", "GPIO10", "GPIO20", "GPIO21"]) + '</div>')
    H.append('<div class="evidence"><p><strong>Sources.</strong> The net list is fast-track Steps 6–11 and the <code>CLAUDE.md</code> hardware contract; rod names, lengths and heights are generated from <code>edu/pages/gen/harness_model.py</code>, the same model as the step-by-step page. The circuit passed on the breadboard; the harness has not been built yet.</p></div>')
    H.append('</div>')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
