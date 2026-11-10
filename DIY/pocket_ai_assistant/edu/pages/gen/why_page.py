"""Builds edu/pages/why-the-wiring.html: why Pip is wired the way it is, battery included."""
from __future__ import annotations

import pathlib
import re

from harness_page import a, L
from power_page import L as _

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "why-the-wiring.html"
SCHEMATIC = "https://claude.ai/artifact/CAzzassRghF9MTSHMUD3Qf"
BRIDGE = "https://claude.ai/artifact/F5xmQ2TahCZxSLDdm6raMp"
PHYSICS = "https://claude.ai/artifact/2ihQAvK2zygttS25YtS58U"


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def fig_tree():
    o = ['<svg viewBox="0 0 760 230" role="img" aria-label="Two voltages from one source">']
    def box(x, y, w, h, t1, t2="", cls="box"):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" class="{cls}"/><text class="s b" x="{x+w/2}" y="{y+20}" text-anchor="middle">{t1}</text>'
        if t2:
            s += f'<text class="s muted" x="{x+w/2}" y="{y+36}" text-anchor="middle">{t2}</text>'
        return s
    o.append(box(20, 80, 150, 50, "USB or PowerBoost", "5 V, up to 1 A"))
    o.append('<line x1="170" y1="105" x2="250" y2="105" stroke="var(--w-red)" stroke-width="5" stroke-linecap="round"/><text class="s b" x="210" y="97" text-anchor="middle">5 V rail</text>')
    o.append(box(250, 30, 130, 50, "amp VIN", "wants 5 V for loudness"))
    o.append(box(250, 130, 130, 50, "A1 5V pin", "its regulator inside"))
    o.append('<line x1="250" y1="105" x2="250" y2="55" stroke="var(--w-red)" stroke-width="5" stroke-linecap="round"/><line x1="250" y1="105" x2="250" y2="155" stroke="var(--w-red)" stroke-width="5" stroke-linecap="round"/>')
    o.append('<line x1="380" y1="155" x2="460" y2="155" stroke="var(--w-orange)" stroke-width="5" stroke-linecap="round"/><text class="s b" x="420" y="147" text-anchor="middle">3V3 rail</text>')
    o.append(box(460, 100, 120, 44, "screen VCC", "3.3 V part"))
    o.append(box(460, 160, 120, 44, "mic VDD", "3.6 V maximum"))
    o.append(box(600, 130, 140, 50, "A1's own chip", "3.3 V too"))
    o.append('<line x1="460" y1="155" x2="460" y2="122" stroke="var(--w-orange)" stroke-width="5" stroke-linecap="round"/><line x1="460" y1="155" x2="460" y2="182" stroke="var(--w-orange)" stroke-width="5" stroke-linecap="round"/><line x1="580" y1="155" x2="600" y2="155" stroke="var(--w-orange)" stroke-width="5" stroke-linecap="round"/>')
    o.append('<text class="s warn-ink" x="20" y="215">5 V reaches two pins only. 3.3 V is made on A1 and shared on its own rail. Both return on the one GND rail.</text>')
    o.append('</svg>')
    return "".join(o)


def fig_charge():
    o = ['<svg viewBox="0 0 760 250" role="img" aria-label="How a lithium cell is charged">']
    o.append('<line x1="60" y1="200" x2="720" y2="200" class="edge"/><line x1="60" y1="200" x2="60" y2="30" class="edge"/>')
    o.append('<text class="s muted" x="720" y="218" text-anchor="end">time → about 1½ hours</text>')
    # current: flat at 1 A then tapering
    o.append('<path d="M60,70 L380,70 C 460,70 560,150 700,190" fill="none" stroke="var(--w-red)" stroke-width="3.5"/>')
    o.append('<text class="s b" x="200" y="62" fill="var(--w-red)">current: 1 A, steady</text><text class="s b" x="560" y="150" fill="var(--w-red)">then tapers</text>')
    # voltage: rising to 4.2 then flat
    o.append('<path d="M60,160 C 200,120 320,95 380,88 L700,88" fill="none" stroke="var(--w-orange)" stroke-width="3.5"/>')
    o.append('<text class="s b" x="120" y="150" fill="var(--w-orange)">voltage: 3.7 V rising</text><text class="s b" x="520" y="80" fill="var(--w-orange)">held at 4.2 V</text>')
    o.append('<line x1="380" y1="30" x2="380" y2="200" class="grid dashed"/><text class="s muted" x="380" y="24" text-anchor="middle">constant current → constant voltage</text>')
    o.append('<line x1="700" y1="30" x2="700" y2="200" class="grid dashed"/><text class="s muted" x="700" y="24" text-anchor="middle">full: current under 0.1 A, LED green</text>')
    o.append('</svg>')
    return "".join(o)


def main():
    H = ['<title>Why the Wiring</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style(), '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · final build · the reasons</div>',
         '<h1>Why Pip is wired the way it is</h1>',
         f'<p class="lede">Four pages on the reasons behind the <a href="{SCHEMATIC}" target="_blank" rel="noopener">rails-and-lanes diagram</a>: two voltages, one ground, three kinds of signal, five small parts, a frame that carries nothing, and a battery that gets its own board. Each rule on the build pages comes from one of these.</p>']

    H.append('<h2>1 · Two voltages, one source</h2>')
    H.append('<p>Everything in Pip runs on 5 V or 3.3 V, and only two pins ever see 5 V: A1\'s 5V input and the amplifier\'s VIN. The other parts are 3.3 V chips. The INMP441 microphone dies above 3.6 V; the screen\'s controller and A1\'s own ESP32-C3 are 3.3 V parts too. Feed them 5 V and you replace them.</p>')
    H.append('<p>So 5 V comes in once, from USB today and from the PowerBoost in the final build, and goes to those two pins. A1 has a small regulator that turns 5 V into 3.3 V; its 3V3 pin is the <em>output</em> of that regulator, and that is what the 3V3 rail carries to the screen and the mic. The regulator can give about 500 mA, and the screen and mic together want under 30.</p>')
    H.append(f'<figure><div class="scroll">{fig_tree()}</div><figcaption><strong>Why the amp is on 5 V and not 3.3.</strong> The amplifier works from 2.5 to 5.5 V, but loudness is voltage: at 5 V it can swing about twice what it could at 3.3 V, and power is voltage squared, so four times the sound. At cap 45 the harness runs the speaker at about 0.4 W peak; on 3.3 V that would be a whisper.</figcaption></figure>')

    H.append('<h2>2 · Why rails, and why one ground</h2>')
    H.append('<p>Thirteen of the device\'s connections are power or ground; nine of them are GND or 3V3. A rail is simply one shared conductor those nine can hook onto, instead of nine separate rods back to A1\'s two pins. That is the whole reason for the two long rods on the floor: fewer joints, shorter rods, and every ground in the device is the same piece of metal.</p>')
    H.append('<p>The same piece of metal matters more than it sounds. Every signal in Pip is a voltage <em>measured against ground</em>: the screen decides whether SDA is a 1 or a 0 by comparing it with its own GND pin. If the screen\'s ground and A1\'s ground were different wires meeting somewhere far away, current flowing in one of them would make the two grounds differ by a few tenths of a volt, and a 1 could read as a 0. One rail, short taps, one truth.</p>')
    H.append('<p>The amplifier is the exception that proves it. It is the one part that pulls real current in bursts, so its ground return is a straight rod to A1\'s GND stub, with the rail hanging off that rod by a pin. The noisy return does not run <em>through</em> the rail the mic and screen sit on; it runs beside it.</p>')

    H.append('<h2>3 · The three kinds of signal</h2>')
    H.append('<p><strong>I²C, two wires, the screen.</strong> SCL is a clock, SDA is data, and the same two wires could serve more devices. The screen only listens. Both lines idle at 3.3 V and get pulled low to talk; the pull-up resistors that make that work are already on the screen module, which is why the harness has none for I²C.</p>')
    H.append('<p><strong>I²S, four wires, sound both ways.</strong> BCLK ticks 1,024,000 times a second; WS flips 16,000 times a second to say "left slot, right slot"; DIN carries the bits going out to the amp, SD the bits coming in from the mic. The two clocks go to <em>both</em> the amp and the mic because they are the metronome: everyone plays to the same beat. That is why the WS and BCLK rods each pass the amp with a tap and carry on to the mic, while DIN and SD are single rods. The <a href="' + PHYSICS + '" target="_blank" rel="noopener">physics page</a> has the bit-by-bit picture.</p>')
    H.append('<p><strong>Plain pins, one wire each.</strong> The button grounds GPIO10; the amp\'s SD pin is a switch A1 pulls high to let the amp speak. Both are just "high or low", no timing.</p>')

    H.append('<h2>4 · The five small parts, and why each is where it is</h2>')
    H.append('<ul>'
             '<li><strong>R3, 10 kΩ, BCLK to 3V3 (kept for now).</strong> GPIO2 is one of the pins the ESP32-C3 reads at the instant it powers on to decide how to boot: Espressif says it must be high then, and the chip gives it no pull of its own. The amp and the mic only listen on this line, so nothing else holds it high; 10 kΩ to 3.3 V does, and is far too weak to bother the clock afterwards. One meter check retires it: A1 unpowered, Ω between GPIO2 and 3V3 — about 10 kΩ means the SuperMini board already has the pull-up and R3 can go.</li>'
             '<li><strong>Mic SD pull-down: in firmware, not brass (R4 dropped 2026-10-14).</strong> The mic drives SD only during its own slot and lets go the rest of the time; a line nobody drives picks up noise. The INMP441 datasheet asks for a 100 kΩ to ground, and A1 has one built in: Pip\'s firmware switches on GPIO4\'s internal pull-down at start-up, so the resistor would only repeat it.</li>'
             '<li><strong>R1, 4.7 kΩ, amp SD to GND.</strong> From power-on until Pip\'s firmware is running, GPIO5 is undefined. This resistor holds the amplifier\'s shutdown pin low through that gap so the speaker cannot click, pop or sit at full gain on garbage. The firmware then drives it high only while speaking.</li>'
             '<li><strong>GAIN: left open (R2 dropped 2026-10-14).</strong> The amp reads the resistance on its GAIN pin once and sets its volume range: open is 9 dB, 100 kΩ to ground would be 15 dB. Open is the quieter, safer setting and the one the board ships with; the resistor can be added later if Pip is too quiet.</li>'
             '<li><strong>C1 220 µF and C2 100 nF, across VIN and GND at the amp.</strong> A bass note or a Wi-Fi burst asks for a few hundred milliamps for a few milliseconds. A long thin wire cannot deliver that fast, and the 5 V would sag and reset A1. The 220 µF is a local reservoir that answers the slow bursts; the 100 nF answers the fast spikes it is too slow for. They sit at the amp because that is where the demand is; a reservoir 50 mm away is a reservoir with a straw.</li>'
             '</ul>')

    H.append('<h2>5 · Why OUT+ and OUT− never touch ground</h2>')
    H.append('<p>The amplifier drives the speaker with a bridge: four transistor switches, the speaker across the middle. To push the cone out it connects OUT+ to 5 V and OUT− to ground; to pull it in, the reverse. Neither output <em>is</em> ground, each is a switched node that spends half its time at 5 V. Tie OUT− to the GND rail and the moment the bridge flips, 5 V is shorted straight to ground through one transistor. It fails in milliseconds. The speaker gets its own two leads, twisted together, and nothing else. <a href="' + BRIDGE + '" target="_blank" rel="noopener">The Bridge</a> draws it.</p>')

    H.append('<h2>6 · Why the frame carries nothing</h2>')
    H.append('<p>Brass is a conductor, and the cage touches everything that touches it. If one rail brushed a tube, the whole frame would become GND, and every other accidental touch anywhere on it would be a short to ground. Worse, a grounded metal box 10 mm from A1\'s ceramic antenna is a ground plane in the wrong place: it detunes the antenna and the Wi-Fi gets worse. So the rule is absolute: 2 mm of air between any conductor and the frame, Kapton on the tubes, and the meter proving silence between the frame and every rail before power. The silver frame obeys the same rule; silver conducts even better.</p>')

    H.append('<h2>7 · The battery: why it needs its own board</h2>')
    H.append('<p>A lithium cell gives 3.7 V, sagging toward 3.0 V as it empties. Wire it straight to A1\'s 5V pin and three things go wrong at once. The amp is quiet (see section 1). A1\'s regulator needs its input a few tenths of a volt above 3.3 V, so below about 3.6 V the whole device browns out with half the cell still full. And there is no way to charge it except by taking it out.</p>')
    H.append('<p>The PowerBoost does three jobs the harness cannot. A <strong>boost converter</strong> turns 3.7 V into a steady 5.2 V, so the harness sees exactly what the USB socket used to give it and nothing downstream changes. A <strong>charger</strong> fills the cell correctly from any USB supply. And <strong>load sharing</strong> lets both happen at once.</p>')
    H.append(f'<figure><div class="scroll">{fig_charge()}</div><figcaption><strong>How a cell is charged: constant current, then constant voltage.</strong> The charger pushes 1 A until the cell reaches 4.2 V, then holds 4.2 V and lets the current fall; when it drops under about a tenth of the starting rate the cell is full and the LED turns green. Holding 4.2 V exactly is why this is a dedicated chip and not a resistor: 4.3 V shortens a cell\'s life, 4.5 V can set it on fire.</figcaption></figure>')
    H.append('<p><strong>Why load sharing is not optional.</strong> The charger decides "full" by watching the current into the cell fall. If the device were drawing its power from the cell during charging, that current would never fall, the charger would never terminate, and the cell would sit at 4.2 V under charge indefinitely. A load-sharing charger routes the USB power to the device directly and sends only the leftover to the cell, so the cell\'s current is its own. The #4410 charger you own has no such path, which is why it stays on the bench.</p>')
    H.append('<p><strong>Why the switch is on EN and not in the battery lead.</strong> EN is a logic pin: grounding it tells the boost to stop, and the current through the switch is microamps. A switch in the cell\'s own lead would carry the full 0.7 A, would need to be a bigger, better switch, and would drop a few tenths of a volt across its contacts exactly where volts are scarce. On EN, the cell stays connected to the charger even while the device is "off", so it charges either way.</p>')
    H.append('<p><strong>Why one source at a time.</strong> A1\'s 5V pin is wired straight to its USB socket: on this board they are the same copper, no diode between them (you measured that in September). With the PowerBoost feeding 5.2 V to that pin, plugging a cable into A1 would tie two supplies together; the higher one pushes current back into the lower, into a laptop port or into the boost\'s output, and something gives. So the final build blocks A1\'s port, and flashing happens with the PowerBoost switched off.</p>')
    H.append('<p><strong>Why the 1200 mAh cell and not the 500.</strong> The device peaks at about 0.5 A on the 5 V side, during a Wi-Fi burst with the amp playing. The boost converter trades volts for amps: 5 V × 0.5 A is 2.5 W, which at 3.7 V and 90 % efficiency is 0.75 A out of the cell. A pouch cell is rated in multiples of its capacity: 0.75 A is 1.5C for a 500 mAh cell, past its 1C rating, and 0.6C for the 1200, comfortably inside. The same arithmetic gives the runtime: 1200 mAh × 3.7 V is 4.4 Wh, about 4 Wh usable after the boost, and the device averages under 1 W while talking, so roughly five hours. Charging at 1 A is 0.8C for the 1200, normal; it would be 2C for the 500, abusive.</p>')
    H.append('<p><strong>Why no solder ever touches the cell.</strong> A pouch cell is a foil envelope; heat the tab and the separator inside can melt, and a lithium cell with a shorted separator does not fail quietly. The cell has its own protection board that cuts off above 4.25 V, below 3.0 V and on over-current, and it arrives with a JST plug. The plug is the only connection it will ever have. It also goes into the frame last and comes out first, so it is never near the iron.</p>')

    H.append('<h2>8 · Why the rods are where they are</h2>')
    H.append('<p>Bare rods have no insulation, so air is the insulation: 1 mm of it holds off thousands of volts, and this device has five. The whole geometry on the harness page exists to keep 1 mm of air between any two conductors that are not meant to meet, and 2 mm to the frame. Where a sketch could not promise that, a sleeve of heat-shrink or a square of Kapton does the job instead, and that is all those two materials are for: insulation where bare metal would otherwise rest on bare metal.</p>')

    H.append('<div class="evidence"><p><strong>Sources.</strong> The connections are fast-track Steps 6–11 and the CLAUDE.md contract; the strapping-pin behaviour is the ESP32-C3 datasheet; the amplifier facts (2.5–5.5 V, bridge output, GAIN and SD pins) are the MAX98357A datasheet; the PowerBoost functions are Adafruit\'s product page (MCP73871 charger with load sharing, TPS61090 boost); cell ratings are the project\'s September materials review. Runtime and current figures are estimates from typical values, not measurements.</p></div>')
    H.append('</div>')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
