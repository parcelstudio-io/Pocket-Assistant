"""Builds edu/pages/build-day.html: the harness and the battery on one concise page, every connection with its reason.
Drawn from the same model as the harness pages (harness_model / harness_draw), the net list, Why the Wiring,
and the final-build power page. Reading PDF via page_print.py build-day."""
from __future__ import annotations

import pathlib
import re

import harness_model as M
import harness_draw as D
from harness_page import a, L, fig
import power_page as P
import whole_build_page as W
import wiring_sheet as WS

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "build-day.html"
STEP_URL = "https://claude.ai/artifact/FAsL4WPArRK6QW7yEg2Nix"
POWER_URL = "https://claude.ai/artifact/J9qXnfWho79ZrsDc4a8jy6"
TEST_URL = "https://claude.ai/artifact/6kZ6h285bMka6wo8bbLfyp"


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def table(head, rows, keep=False):
    cls = 'scrollx keep' if keep else 'scrollx'
    o = [f'<div class="{cls}"><table class="t"><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr>"]
    for r in rows:
        o.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    o.append("</table></div>")
    return "".join(o)


def main():
    rods = {c.name: c for c in M.rods()}

    def L_(name):
        c = rods[name]
        return f"{c.name}, {c.length:.0f} mm" if hasattr(c, "length") else c.name

    H = ['<title>Build Day</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style(),
         '<style>figure svg .acc-fill { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.4; } figure svg .warn-fill { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1.2; }'
         ' figure svg .hole { fill: var(--surface); stroke: var(--pass); stroke-width: 2.2; stroke-dasharray: 3 2; } figure svg .card { fill: var(--surface); stroke: var(--muted); stroke-width: 1.2; }'
         ' figure svg .cap { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.2; } figure svg .spk { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1.2; }'
         ' td.why { color: var(--muted); } .keep { break-inside: avoid; page-break-inside: avoid; } figure.wide { width: 100% !important; } figure.wide svg { min-width: 900px; }</style>',
         '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · build day · the harness and the battery, with the reasons</div>',
         '<h1>Build day: every connection, and why</h1>',
         f'<p class="lede">One sheet for the whole device. The brass harness first, on USB, on its jig card; then the PowerBoost, the switch and the cell underneath it. Every line says what joins what and the one reason it is done that way. Cut lengths, bends and per-rod drawings are on the <a href="{STEP_URL}" target="_blank" rel="noopener">step-by-step page</a>; the battery details on the <a href="{POWER_URL}" target="_blank" rel="noopener">power page</a>.</p>']

    H.append('<div class="callout"><span class="label">Four rules for the day</span><ul>'
             '<li><strong>USB unplugged whenever the iron is on.</strong> A powered board and a grounded iron tip are a short waiting to happen.</li>'
             '<li><strong>OUT+ and OUT− go to the speaker only.</strong> Both are switched outputs that sit at 5 V half the time; tied to ground, the amp dies in milliseconds.</li>'
             '<li><strong>The frame carries nothing.</strong> 2 mm of air or Kapton between any conductor and the brass; a grounded cage also detunes the antenna.</li>'
             '<li><strong>One source at a time.</strong> A1\'s 5V pin is its USB VBUS with no diode. PowerBoost on means A1\'s USB stays empty; flashing means PowerBoost off.</li></ul></div>')

    # ------------------------------------------------------------ bench
    H.append('<h2>On the bench</h2>')
    H.append(f'<p><strong>Modules:</strong> {a("a1", "A1 SuperMini")}, {a("amp")}, {a("mic", "INMP441 mic")}, {a("screen", "SSD1306 screen")}, {a("speaker")}, {a("button", "tactile button")}. '
             f'<strong>Small parts:</strong> 4.7 kΩ and 10 kΩ from the {a("res", "resistor kit")}, 220 µF from the {a("cap220", "electrolytic kit")}, 100 nF from the {a("cap100n", "ceramic kit")}. '
             f'<strong>Conductors:</strong> {a("rod", "1.0 mm brass rod")} or {a("ns18", "18 ga nickel silver")}; {a("wire26", "26 AWG")} and 30 AWG insulated wire for the battery storey. '
             f'<strong>Battery:</strong> {a("powerboost_owned", "PowerBoost 1000C copy")}, {a("cell1200", "1200 mAh cell")}, {a("switch", "slide switch")}. '
             f'<strong>Tools and consumables:</strong> {a("cutters")}, {a("pliers")}, {a("sand")}, {a("flux")}, {a("solder")}, {a("wick")}, {a("shrink")}, {a("kapton")}, {a("card", "cardstock")}, {a("meter")}, {a("caliper")}, {a("ipa", "isopropyl")}, hot glue, heat gun, helping hands.</p>')

    # ------------------------------------------------------------ pictures
    H.append('<h2>The two pictures to keep beside you</h2>')
    H.append(f'<figure class="wide"><div class="scroll">{WS.sheet()}</div><figcaption><strong>Every connection on one sheet.</strong> A1 in the middle with each GPIO named; thick lines are the bare rods of the harness, thin lines the insulated wires of the battery storey; a dot is a joint, a ring a tap where a rod carries on, a crossing without a dot does not touch. Printed landscape as page 1 of the PDF.</figcaption></figure>'),
    H.append(f'<figure><div class="scroll">{W.fig_front()}</div><figcaption><strong>The whole device from the front, three storeys.</strong> Cell at the bottom in its cradle, the PowerBoost on a card shelf above it, the harness on top. Two insulated wires climb through the shelf to A1\'s 5V and GND stubs.</figcaption></figure>')

    # ------------------------------------------------------------ rails
    H.append('<h2>1 · The two rails</h2>')
    H.append('<p>A rail is one bare rod that many parts share, so nine power and ground connections become nine short taps instead of nine rods back to A1. Every ground in the device is then the same piece of metal, which is what makes every signal read correctly: a 1 or a 0 is a voltage measured against ground, and two grounds that differ by a few tenths of a volt turn 1s into 0s.</p>')
    H.append(table(["Rail", "Lies", "Fed by", "Who hooks on", "Why"], [
        ("<strong>3V3 rail</strong>", "x = 24, 21 mm, on the card", "A1 3V3 stub, by the 3V3 tap", "screen VCC, mic VDD, R3",
         '<span class="why">A1\'s regulator makes 3.3 V; the mic dies above 3.6 V and the screen is a 3.3 V part</span>'),
        ("<strong>GND rail</strong>", "x = 27, 22 mm, on the card", "A1 GND stub, by the GND rod and a 3 mm drop pin", "screen GND, mic GND, mic L/R, 220 µF −",
         '<span class="why">the amp\'s bursty return takes the straight rod to A1; the quiet rail hangs off it, so mic and screen never share its noise</span>'),
    ]))

    # ------------------------------------------------------------ A1 pins
    H.append('<h2>2 · Every A1 pin, where it goes, and why</h2>')
    H.append(table(["A1 pin", "Goes to", "By", "Why it is wired that way"], [
        ("<code>5V</code>", "amp VIN", "5 V rod, 10 mm, straight across the channel",
         '<span class="why">only two pins ever see 5 V: this input and the amp. The amp wants 5 V because loudness is voltage: twice the swing of 3.3 V, four times the sound</span>'),
        ("<code>GND</code>", "amp GND, then the GND rail", "GND rod, 10 mm; a 3 mm drop pin under it onto the rail",
         '<span class="why">the star point. Amp current returns on its own rod; the pin beneath makes the rail ground without routing that current along it</span>'),
        ("<code>3V3</code>", "3V3 rail", "3V3 tap, 7 mm, hooks down onto the rail",
         '<span class="why">A1 feeds the rail once; nobody else runs back to A1 for power</span>'),
        ("<code>GPIO4</code>", "mic SD", "mic SD rod, 32 mm",
         '<span class="why">sound in. The mic only drives this line during its slot; the firmware\'s internal pull-down holds it quiet the rest of the time (R4 dropped)</span>'),
        ("<code>GPIO3</code>", "amp DIN", "DIN rod, 10 mm",
         '<span class="why">sound out. One listener, one rod</span>'),
        ("<code>GPIO2</code>", "amp BCLK, then mic SCK", "BCLK rod, 38 mm, one rod with two taps",
         '<span class="why">the bit clock is the metronome; amp and mic must hear the same one. R3 10 kΩ to 3V3 sits on it because GPIO2 is a boot-strapping pin that must read high at power-on</span>'),
        ("<code>GPIO1</code>", "amp LRC, then mic WS", "WS rod, 33 mm, one rod with two taps",
         '<span class="why">the word clock that says "left slot, right slot" 16,000 times a second; shared for the same reason</span>'),
        ("<code>GPIO5</code>", "amp SD", "amp SD rod, 43 mm",
         '<span class="why">amplifier on/off. R1 4.7 kΩ to GND holds it off until the firmware is running, so the speaker cannot pop or sit at full gain on garbage</span>'),
        ("<code>GPIO10</code>", "button, left legs", "button rod, 19 mm; right legs to A1 GND by an 8 mm rod",
         '<span class="why">pressing grounds the pin; A1 pulls it up internally. Plain high-or-low, no timing</span>'),
        ("<code>GPIO20</code>", "screen SCL", "SCL rod, 53 mm, up to the floating screen",
         '<span class="why">I²C clock. The pull-ups I²C needs are already on the screen module, so the harness has none</span>'),
        ("<code>GPIO21</code>", "screen SDA", "SDA rod, 53 mm",
         '<span class="why">I²C data, same bus</span>'),
    ]))
    H.append('<p>Left as stubs: GPIO0, 6, 7, 8, 9. GPIO6 is reserved for the PowerBoost\'s low-battery flag; GPIO9 is the BOOT button and never an input.</p>')

    # ------------------------------------------------------------ taps and small parts
    H.append('<h2>3 · Taps and the small parts</h2>')
    H.append(table(["Part pin", "To", "By", "Why"], [
        ("screen GND · VCC", "GND rail front · 3V3 rail front", "two taps, 23 and 22 mm, dropping from the floating screen",
         '<span class="why">the screen is held up by its four rods; power comes from the rails nearest it</span>'),
        ("mic GND · VDD", "GND rail back · 3V3 rail back", "two taps, 11 and 20 mm",
         '<span class="why">the mic lies chip-side down at the back; its SD, VDD, GND row faces the channel</span>'),
        ("mic L/R", "mic GND stub", "8 mm link",
         '<span class="why">grounding L/R selects the left I²S slot, the one the firmware listens to</span>'),
        ("amp GND", "A1 GND stub", "the GND rod",
         '<span class="why">see the star point above</span>'),
        ("<strong>R1</strong> 4.7 kΩ", "amp SD ↔ amp GND", "a U lying over the amp board",
         '<span class="why">keeps the amp silent through the undefined moment between power-on and firmware</span>'),
        ("<strong>R3</strong> 10 kΩ", "BCLK rod ↔ 3V3 rail", "in the channel, 8.5 mm up",
         '<span class="why">boot-strap pull-up for GPIO2. One meter check retires it: A1 unpowered, ~10 kΩ between GPIO2 and 3V3 means the board has its own</span>'),
        ("<strong>C1</strong> 220 µF", "5 V net ↔ GND rod, stripe to GND", "lying in the right strip, leads sleeved",
         '<span class="why">a local reservoir for bass notes and Wi-Fi bursts, so the 5 V does not sag and reset A1</span>'),
        ("<strong>C2</strong> 100 nF", "amp VIN ↔ amp GND", "flat on the amp board at the pins",
         '<span class="why">answers the fast spikes the 220 µF is too slow for; it must sit at the pins to work</span>'),
        ("speaker", "OUT+ and OUT− only", "its own two leads, twisted",
         '<span class="why">a bridge output; neither side is ground, ever</span>'),
    ], keep=True))
    H.append('<p><strong>Dropped on 2026-10-14:</strong> R2 (GAIN stays open, 9 dB; add 100 kΩ GAIN-to-GND later for 15 dB if Pip is too quiet) and R4 (the firmware enables GPIO4\'s pull-down).</p>')

    # ------------------------------------------------------------ battery storey
    H.append('<h2>4 · The battery storey</h2>')
    H.append(f'<p>A lithium cell gives 3.7 V falling to 3.0 V. Fed straight to A1 the amp is a whisper and A1\'s regulator browns out with half the cell still full. The PowerBoost does three jobs the harness cannot: boost the cell to a steady 5.2 V so the harness sees exactly what USB gave it, charge the cell correctly (1 A until 4.2 V, then hold 4.2 V until the current tapers), and share the load so the device can run while charging. The harness does not change; its two power entry points just get a new supplier.</p>')
    H.append(fig(P.fig_power(), '<strong>Two wires into the harness, two into the switch, one JST to the cell, one cable to charge.</strong>'))
    H.append(table(["#", "From", "To", "With", "Why"], [
        ("P1", "PowerBoost <code>5V</code>", "A1\'s 5V stub, through the shelf hole", "26 AWG red, ≈ 60 mm",
         '<span class="why">that stub is where USB power used to enter; every rod downstream sees the same 5 V it always did, and the 220 µF stays where it is</span>'),
        ("P2", "PowerBoost <code>GND</code>", "A1\'s GND stub, through the shelf hole", "26 AWG black, ≈ 55 mm",
         '<span class="why">one ground meeting point. The rail stays a dead end, so no loop for the amp\'s current to run through the signal rods</span>'),
        ("P3", "PowerBoost <code>EN</code>", "slide switch, one side", "30 AWG, ≈ 40 mm",
         '<span class="why">EN is a logic input drawing microamps, so a tiny switch controls the whole load without carrying its 0.7 A or dropping volts where volts are scarce</span>'),
        ("P4", "switch, other side", "PowerBoost <code>GND</code>", "30 AWG, ≈ 40 mm",
         '<span class="why">closed = EN grounded = output off. The cell stays on the charger even when "off", so it charges either way</span>'),
        ("P5", "1200 mAh cell JST", "PowerBoost JST socket", "the cell\'s own lead",
         '<span class="why">the plug is the only connection the cell will ever have: factory-terminated, keyed, behind its own protection board. Meter + and − against the silkscreen before the first plug-in</span>'),
        ("P6", "PowerBoost <code>LBO</code>", "A1 GPIO6", "30 AWG, optional",
         '<span class="why">open-drain flag that goes low at 3.2 V; a free GPIO reads it so the face can warn before the cell cuts out</span>'),
        ("—", "A1 USB-C", "nothing; Kapton over it", "—",
         '<span class="why">A1\'s 5V stub is the USB VBUS node with no diode; a cable there would tie two supplies together</span>'),
    ], keep=True))
    H.append('<p><strong>Why the 1200 mAh and not the 500.</strong> The device peaks near 0.5 A at 5 V; through the boost that is about 0.75 A from the cell, 1.5C for a 500 mAh cell and over its rating, 0.6C for the 1200 and comfortable. Charging at 1 A is normal for the 1200, abusive for the 500. <strong>Why no solder ever touches the cell.</strong> It is a foil envelope; heat the tab and the separator inside can melt. It goes in last and comes out first.</p>')

    # ------------------------------------------------------------ order
    H.append('<h2>5 · The order of the day</h2>')
    H.append('<ol>'
             '<li><strong>Stubs.</strong> Clip A1\'s and the amp\'s pins flush under their header strips; the short ends on top are the stubs. Screen and mic pins to 2 mm, button legs to 1 mm. Sand every stub bright. <em>Why:</em> a rod lies against a short stub; a long pin would push it off the card.</li>'
             '<li><strong>Jig card.</strong> Print the floor template at Actual size, glue to cardstock. Kapton on the USB socket roof (two layers) and a strip on the amp beside its stubs. Tape the modules on their outlines the way up the step page says; shim the amp\'s pin-free edge to 2.5 mm. <em>Why:</em> everything is positioned on the card and soldered in place; the card comes off at the end.</li>'
             '<li><strong>Rails.</strong> 3V3 at x = 24, GND at x = 27, taped. Meter between them: silent.</li>'
             '<li><strong>Six channel rods.</strong> 5 V rod, GND rod, GND drop pin, 3V3 tap, DIN rod, then the BCLK and WS rods with their amp taps. Flux, 1–2 s of iron per joint, 320 °C. <em>Why this order:</em> low rods first; everything later crosses above them.</li>'
             '<li><strong>Four fly-overs.</strong> Mic SD, amp SD, button rod, and the BCLK and WS continuations to the mic, up to 10.5 mm. Heat-shrink wherever one crosses another under 1 mm.</li>'
             '<li><strong>Screen</strong> on its four rods (SCL, SDA, VCC tap, GND tap), floating 17.5 mm up. <strong>Button</strong> on the socket\'s Kapton. <strong>Mic</strong> chip-side down, its three taps and the L/R link.</li>'
             '<li><strong>R1, R3, C1, C2, speaker.</strong> Stripe of the 220 µF to GND. Speaker leads to OUT+ and OUT− only.</li>'
             '<li><strong>Power up on USB.</strong> Meter sweep first: GND rail to 3V3 rail, to the 5 V rod, to OUT+, to OUT−, all silent. USB in; eyes open, <code>got ip</code>, <code>hello accepted</code> in the server log. Hold the button, ask Pip its name. Then the amplifier build at cap 45 and Pip answers out loud. Unplug, wait ten seconds, plug in, ask once more.</li>'
             '<li><strong>Off the card.</strong> Cut the tape and lift the harness as one rigid piece. Kapton inside the frame. Meter frame to every rail and to OUT±: silent.</li>'
             '<li><strong>Bench-test the PowerBoost alone</strong> before it meets the harness: cell in (red to +), switch on EN, meter 5.1–5.3 V at its output, then one charge watching the LEDs (yellow charging, green full). The eight steps are on the <a href="' + TEST_URL + '" target="_blank" rel="noopener">real-test page</a>.</li>'
             '<li><strong>Assemble the storeys.</strong> Shelf with its two wire holes; PowerBoost on it, USB port to the wall; P1–P4 soldered at the PowerBoost end first and led up through the holes; harness onto the shelf; P1 to A1\'s 5V stub, P2 to A1\'s GND stub; Kapton over A1\'s USB; cradle and cell at the bottom, JST in last.</li>'
             '<li><strong>Final checks.</strong> Meter frame to everything: silent. Switch on: the same tests as step 8, now with no cable. Charge once through the PowerBoost\'s port with the device on.</li>'
             '</ol>')

    H.append('<div class="callout"><span class="label">Never</span><ul>'
             '<li>OUT+ or OUT− to GND, a rail, the frame, or a scope ground clip.</li>'
             '<li>Anything but A1\'s 3V3 pin feeding the screen or the mic.</li>'
             '<li>A1\'s USB and the PowerBoost output at the same time.</li>'
             '<li>Solder, brass, or an iron within 10 cm of the cell. The 500 mAh cell at all.</li>'
             '<li>Harris acid flux on this bench: it is for the empty frame only, washed and neutralised before any module arrives.</li></ul></div>')

    H.append('<div class="evidence"><p><strong>Sources.</strong> Connections and reasons from the net list, Why the Wiring, and the final-build power page, all generated from <code>harness_model.py</code> and the CLAUDE.md pin contract; PowerBoost functions from Adafruit\'s product page; cell ratings from <code>docs/INVENTORY.md</code>. Currents and runtime are estimates, not measurements. The harness and the battery storey have not been built.</p></div>')
    H.append('</div>')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
