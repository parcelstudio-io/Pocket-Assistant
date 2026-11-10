"""The lean build page: edu/pages/brass-harness-step-by-step.html.

Twelve moves, nothing optional. Every rod keeps its two drawings and its bend table because
those are the work; everything that only saves a redo is gone. Built from the same model as
the full page (harness_page.py, which now writes brass-harness-step-by-step-full.html).
"""
from __future__ import annotations

import pathlib
import re

import harness_model as M
import harness_draw as D
from harness_page import L, a

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "brass-harness-step-by-step.html"


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def fig(svg, caption=""):
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure><div class="scroll">{svg}</div>{cap}</figure>'


def step(sid, do, check=None):
    chk = f'<span class="chk">{check}</span>' if check else ""
    return f'<div class="step"><input type="checkbox" id="{sid}"><label for="{sid}"><span class="do">{do}</span>{chk}</label></div>'


def rod(name, sid, do, sleeve=None):
    c = next(r for r in M.rods() if r.name == name)
    rows = D.bend_table(c)
    if len(rows) == 1 and c.length() < 4:
        body = step(sid, f"{do} <span class='note'>Cut 3 mm, bare.</span>")
        return body + fig(D.map_figure(highlight={name}, title=f"{c.name}"), "The ring is the spot.")
    table = ['<div class="scrollx"><table class="t bends"><tr><th>Piece</th><th>mm</th><th>Direction</th><th>Ends at height</th></tr>']
    for i, L_, dirn, z in rows:
        table.append(f'<tr><td class="n">{i}</td><td class="n">{L_}</td><td>{dirn}</td><td class="n">{z}</td></tr>')
    table.append('</table></div>')
    sl = f" <strong>Sleeve:</strong> {sleeve}." if sleeve else ""
    body = (f'<div class="step"><input type="checkbox" id="{sid}"><label for="{sid}"><span class="do">{do}</span>'
            f'<span class="note">Cut <strong>{c.length() + 6:.0f} mm</strong>, finished {c.length():.0f} mm, {len(rows) - 1} bend{"s" if len(rows) != 2 else ""}; 3 mm bare at each end.{sl}</span>'
            f'{"".join(table)}</label></div>')
    return body + fig(D.unrolled(c)) + fig(D.map_figure(highlight={name}, title=f"{c.name} in the top view"))


def main():
    H = ['<title>Brass Harness Step by Step</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style(), '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · step 4d · the harness, minimum version</div>',
         '<h1>Brass harness, step by step</h1>',
         '<p class="lede">Twelve moves to a working prototype. Nothing on this page is optional. The harness is built on a printed card that serves as the jig; when every rod is on, the harness is rigid, the card comes off, and the bare harness goes into the frame. Each rod has its drawing, its cut length and its bends; x is millimetres from the left wall, y from the front wall, heights are above the card.</p>',
         '<div class="progress"><span id="done">0</span> of <span id="total">0</span> steps done <button class="reset" id="reset">clear</button></div>']

    H.append('<div class="callout"><span class="label">Three rules</span><ul>'
             '<li>USB unplugged whenever the iron is on.</li>'
             '<li>OUT+ and OUT− go to the speaker only — never to GND, a rail or the frame.</li>'
             '<li>The frame touches no rod and no rail.</li></ul></div>')

    H.append(f'<p class="stock">On the bench: the five modules · {a("rod", "1.0 mm rod")} (or the {a("ns18", "18 ga nickel silver")}, the same 1.0 mm; 20 ga for a finer look) · {a("cutters", "flush cutters")} · {a("pliers", "chain-nose pliers")} · {a("sand", "400 grit")} · {a("card", "cardstock")} · {a("kapton", "Kapton")} · {a("flux", "Chip Quik pen")} · {a("solder", "63/37 solder")} · electronics tip · {a("shrink", "heat-shrink")} + heat gun · {a("meter", "meter")} · helping hands · {a("res", "resistors")} · {a("cap220", "220 µF")} · {a("cap100n", "100 nF")} · {a("speaker", "speaker")} · hot glue gun</p>')

    H.append(fig(D.map_figure(title="The whole harness, top view, 10 px = 1 mm"), '<strong>Front (USB) at the bottom.</strong> Dots are stubs. The dashed square is the screen, floating above. The channel is the gap between A1 and the amp; the two rails lie in it.'))
    H.append('<div class="legend">' + "".join(
        f'<div><span class="sw" style="background:{D.NET_COLOR[n]}"></span>{D.NET_LABEL[n]}</div>' for n in ["5V", "GND", "3V3", "GPIO1", "GPIO2", "GPIO3", "GPIO4", "AMPSD", "GPIO10", "GPIO20", "GPIO21"]) + '</div>')

    # 1
    H.append('<h2>1 · Stubs</h2>')
    H.append(step("m1", f"<strong>A1 and the amp</strong> keep their black header strips (they stand 2.5 mm up on them). Clip the long pins <strong>flush with the underside of the strip</strong> with the {a('cutters', 'flush cutters')}. The stubs you solder to are the pins' short ends on <strong>top</strong> of the board, about 1.5 mm; leave them. The amp's strip is on one edge only, so shim its other edge level: a flat offcut of the K&S tube plus three layers of {a('card', 'cardstock')}, taped.",
                  "Both boards sit level, 2.5 mm above the card; every pin shows a bright nub on the component side."))
    H.append(step("m1b", f"<strong>Screen</strong> (strip on the back, pins pointing away from the glass): clip to 2 mm beyond the strip. <strong>Mic</strong>: it will lie chip-side down with its strip on top, pins pointing up: clip to 2 mm beyond the strip. <strong>Button</strong>: legs to 1 mm. Then sand every stub bright with {a('sand', '400 grit')}, dust away from the mic hole.",
                  "No two stubs bent toward each other; all shiny, not grey."))
    # 2
    H.append('<h2>2 · The jig card and the parts</h2>')
    H.append(step("m2", f"Print <code>harness-floor-letter.pdf</code> at Actual size, check the 50 mm bar, glue it to {a('card', 'cardstock')}, cut on the outer line. This card is the jig: everything is positioned and soldered on it, and it comes off at the end.",
                  "Every outline and every stub dot is on the card."))
    H.append(step("k1", f"{a('kapton', 'Kapton')} piece 1: the roof of A1's USB socket. Cut 9 × 8 mm, press it flat on the metal top, then a second piece on top of the first. Plug opening and A1's two tiny buttons stay clear.",
                  "The button will sit on film, not metal."))
    H.append(step("k2", f"{a('kapton', 'Kapton')} piece 2: a 10 × 9 mm strip on the amp board, just right of its stub row, where the resistor leads will hover. No tape on any stub.",
                  "That is all the Kapton on the parts. The mic, the screen and the speaker get none."))
    H.append(step("m3a", f"Check each board lies level before taping. A1 has header strips on both edges, so it sits level, 2.5 mm up. The amp has a strip on one edge only, so its other edge needs a 2.5 mm shim: a flat offcut of the K&S tube (1.5) plus three layers of {a('card', 'cardstock')}, taped together, under the pin-free edge.",
                  "Press each corner: no rocking; the caliper reads 2.5 mm from the card to the underside of the board at both edges."))
    H.append(fig(D.amp_level_figure(), '<strong>Strip on one edge, shim on the other.</strong> The header strip holds the pin edge 2.5 mm up; the shim holds the far edge at the same height, so the stubs sit level and the straight rods lie against them 5 mm up. Tape goes over the board, not under it: two loops, each stuck to the card on both sides of the board.'))
    H.append(step("m3", "Tape the parts onto their outlines with any tape, each the way the table says: a loop over the board, stuck down on both sides. Screen and button wait.",
                  "A1's GPIO1/2/3 stubs line up with the amp's LRC/BCLK/DIN stubs across the channel, and the 5V stub is at A1's front-right corner."))
    H.append('<div class="scrollx"><table class="t"><tr><th>Part</th><th>Which side up</th><th>Which way round</th><th>How you know it is right</th></tr>'
             '<tr><td><strong>A1</strong></td><td>component side up (chip, socket, antenna toward the ceiling)</td><td>USB socket toward the <strong>front</strong> edge, antenna toward the back; the 5V·GND·3V3·4·3·2·1 row on the right facing the channel</td><td>the 5V stub sits at the front-right corner beside the socket</td></tr>'
             '<tr><td><strong>Amp</strong></td><td>component side up (chip and terminal block up)</td><td>the 7 stubs on its <strong>left</strong> edge facing A1; <strong>VIN at the front</strong>, LRC at the back; the terminal block on the right edge toward the wall</td><td>VIN sits level with A1\'s 5V stub across the channel</td></tr>'
             '<tr><td><strong>Mic</strong></td><td><strong>chip side down</strong>: the hole and the six stubs point up</td><td>turn it like a dial until the SD·VDD·GND row is on the <strong>left</strong>, toward the channel; L/R·WS·SCK on the right toward the speaker</td><td>GND is the front stub of the left row, SD the back one</td></tr>'
             '<tr><td><strong>Speaker</strong></td><td>mesh up</td><td>long side along the back wall, in the back-right corner; leads toward the amp</td><td>its left edge is 0.5 mm from the mic\'s round board</td></tr>'
             '<tr><td><strong>220 µF</strong></td><td>lying on its side</td><td>along the right wall, leads toward the <strong>front</strong>; the stripe is the − lead</td><td>nothing is soldered to it until move 10</td></tr>'
             '<tr><td><strong>Screen</strong> (move 6)</td><td>glass up, stubs hanging down</td><td>header edge at the <strong>front</strong>; stubs read SDA·SCL·VCC·GND left to right</td><td>floats 17.5 mm up over the amp and the channel</td></tr>'
             '<tr><td><strong>Button</strong> (move 7)</td><td>plunger up</td><td>on the socket\'s Kapton, 1 mm behind the front edge, leg pairs left and right</td><td>left legs → GPIO10, right legs → GND</td></tr>'
             '</table></div>')
    H.append(fig(D.kapton_min_figure(), '<strong>Two pieces, nothing else.</strong> 1: cut 9 × 8 mm, lay it on the flat metal roof of the socket, press it down, then a second piece on top; the plug opening at the front stays clear, and so do A1\'s two tiny buttons beside the socket. 2: a 10 × 9 mm strip on the amp board just right of its stubs, where the resistor leads will hover.'))
    H.append(fig(D.svg_wrap(D.frame_top() + D.parts_top() + D.screen_outline() + "".join(D.poly_top(c, width=5) for c in M.rods()[:2]) + D.part_labels() + D.text(D.OX, 22, "Where everything goes", "t b"),
                            760, int(D.OY + M.INSIDE_Y * D.S + 40), "placement")))
    # 3
    H.append('<h2>3 · Rails</h2>')
    H.append(step("m4", "Two bare rods on their lines: 3V3 rail 21 mm at x = 24 from y = 2.5; GND rail 22 mm at x = 27 from y = 2. Tape each end. Painted rod: sand the paint off along the whole length first.",
                  "Meter between the rails: silent."))
    H.append(fig(D.map_figure(highlight={"3V3 rail", "GND rail"}, title="The rails")))
    # 4
    H.append('<h2>4 · Six channel rods</h2>')
    H.append('<p>For each: sand the ends, bend to the table, hold with the helping hands, flux, 1–2 s of iron per joint. The straight rods lie against the short top stubs, 5 mm up, and pass 3.5 mm above the rails.</p>')
    H.append(rod("5 V rod", "r1", "5 V rod: A1 5V stub straight across to amp VIN, lying against the top of both stubs, 5 mm up.", f"8 mm of {a('shrink', 'heat-shrink')} over its middle, where the screen's VCC tap will drop past it"))
    H.append(rod("GND rod", "r2", "GND rod: A1 GND stub straight across to amp GND, same height.", f"8 mm of {a('shrink', 'heat-shrink')} over its middle, for the 3V3 rail underneath"))
    H.append(rod("GND drop pin", "r3", "GND drop pin: a 3 mm piece standing on the GND rail directly under the GND rod, soldered at both ends. This makes the rail ground."))
    H.append(rod("3V3 tap", "r4", "3V3 tap: from A1's 3V3 stub, low, across to above the 3V3 rail, hook down onto it. This makes the rail 3V3."))
    H.append(rod("DIN rod", "r5", "DIN rod: A1 GPIO3 straight across to amp DIN."))
    H.append(rod("BCLK rod", "r6", "BCLK rod: A1 GPIO2 across to amp BCLK (solder it there as it passes), up to 8, right to x = 36, back to the mic, left onto SCK."))
    H.append(rod("WS rod", "r7", "WS rod: A1 GPIO1 across to amp LRC (solder in passing), back along the amp's edge, up to 10, right, back over the mic's right column, down onto WS."))
    H.append(step("m5", "Meter: GND rail to 3V3 rail silent; 5 V rod to both rails silent; each of DIN, BCLK, WS beeps only to its own ends.", "Anything else beeping: that rod comes off now."))
    # 5
    H.append('<h2>5 · Four fly-overs</h2>')
    H.append(rod("mic SD rod", "r8", "mic SD rod: out of A1 GPIO4 1.2 mm, up to 8, back along the channel's left lane (x = 22), right onto the mic's SD stub."))
    H.append(rod("amp SD rod", "r9", "amp SD rod: straight up A1's GPIO5 stub to 10.5, back to y = 8, right across A1 and the channel, back 1.7, down to 5, right onto amp SD."))
    H.append(rod("SCL rod", "r10", "SCL rod: out of A1 GPIO20 1.5 mm to the left lane, up to 10.5, forward to y = 13.5, right across A1 and the channel, forward along x = 29.7, up to the screen's SCL stub. Leave the end 3 mm long until the screen is in (move 6).",
                  f"{a('shrink', 'heat-shrink')} along the left lane and across A1 (dotted in the drawing)"))
    H.append(rod("SDA rod", "r11", "SDA rod: out of A1 GPIO21 to the left lane, up to 12.5, forward to y = 13.5, right directly above SCL, forward along x = 27.2, up to the screen's SDA stub. End 3 mm long until move 6."))
    H.append(step("m6", "Meter: GPIO4, GPIO5, GPIO20, GPIO21 each beep only to their own far end; none to a rail, none to each other.", ""))
    # 6
    H.append('<h2>6 · Screen</h2>')
    H.append(step("m7", f"A block 15 mm tall beside the amp (folded {a('card', 'cardstock')}, checked with the {a('caliper', 'calipers')}). Screen on it glass up, header edge at the front, stubs over their dots at y = 3.8 (SDA x = 27.2, SCL 29.7, VCC 32.3, GND 34.8). Tape it to the block. Solder the SCL and SDA rod ends to their stubs, trim.",
                  "Stub tips 13 mm up, directly above their rods."))
    H.append(rod("screen GND tap", "r12", "Screen GND tap: down the GND stub to 3.5, forward to y = 2, left to above the GND rail's front end, down onto it."))
    H.append(rod("screen VCC tap", "r13", "Screen VCC tap: down the VCC stub to 5.5, forward to y = 3.3, left over the GND tap's drop, down onto the 3V3 rail's front end."))
    H.append(step("m8", "Pull the block out. The screen hangs on four rods.", "Screen VCC to GND: silent. GPIO20 and GPIO21 still only to their own stubs."))
    # 7
    H.append('<h2>7 · Button</h2>')
    H.append(step("m9", f"The {a('button', 'button')} on the socket's Kapton, plunger up, 1 mm behind the front edge, leg pairs left and right. Meter which pair is which: left pair will be GPIO10, right pair GND. Tape it.", ""))
    H.append(rod("button rod", "r14", "Button rod: straight up A1's GPIO10 stub to 8, right 1.8, forward along x = 6 over A1, to the button's back-left leg."))
    H.append(rod("button GND rod", "r15", "Button GND rod: from the button's back-right leg diagonally back-right at 8, down to 5.5 beside A1's GND stub, onto it."))
    H.append(step("m10", "Meter GPIO10 to GND: silent released, beeps pressed.", ""))
    # 8
    H.append('<h2>8 · Mic</h2>')
    H.append(rod("mic GND tap", "r16", "Mic GND tap: from the mic's GND stub, forward beside the column at 6, right to above the GND rail's back end, down onto it."))
    H.append(rod("mic VDD tap", "r17", "Mic VDD tap: straight up the VDD stub to 9, forward above the column, left to x = 24.6, down onto the 3V3 rail's back end."))
    H.append(rod("L/R link", "r18", "L/R link: one straight piece from the mic's L/R stub to its GND stub, across the board's front edge."))
    H.append(step("m11", "Meter: mic VDD to GND silent; L/R beeps to GND.", ""))
    # 9
    H.append('<h2>9 · Resistors</h2>')
    H.append(f'<p>Two, from the {a("res", "kit")}; measure each before it goes in. Bend leads with the pliers next to the body, cut 3 mm past the joint. The GAIN resistor and the mic-SD pull-down were dropped on 2026-10-14: GAIN stays open (9 dB) and the firmware pulls GPIO4 down itself. R3 stays until a meter check of A1 (GPIO2 to 3V3, unpowered: about 10 kΩ means the board has its own pull-up and R3 can go too).</p>')
    H.append(step("m12", "R1, 4.7 kΩ (or the 1 kΩ from Step 11): one lead on the amp's SD stub, out over the amp board 2 mm up, body along y = 9.7 from x = 33 to 39, the other lead round at x = 40 and back along y = 7.1 to the amp's GND stub.", "GPIO5 to GND rail reads the resistor, not a beep."))
    H.append(fig(D.map_figure(highlight={"R1 lead a", "R1 body", "R1 lead b"}, title="R1 over the amp")))
    H.append(step("m14", "R3, 10 kΩ: one lead soldered to the BCLK rod in the channel at x = 25.5, up to 11, body back along the channel to y = 22.8, the other lead left 0.9 and down onto the top of the mic VDD tap's drop.", "GPIO2 to 3V3 rail reads about 10 kΩ."))
    H.append(fig(D.map_figure(highlight={"R3 lead a", "R3 body", "R3 lead b"}, title="R3 at the back of the channel")))
    # 10
    H.append('<h2>10 · Capacitors and speaker</h2>')
    H.append(step("m16", f"100 nF from the {a('cap100n', 'BOJACK kit')}: leads on the amp's VIN and GND stubs, body flat on the amp board pointing right.", ""))
    H.append(step("m17", f"220 µF from the {a('cap220', 'ALLECIN kit')}, lying in the right strip: leads bent 90° at its base, both in {a('shrink', 'heat-shrink')}. The + lead along y = 3 to the amp's front-left corner, up onto the VIN stub. The stripe (−) lead along y = 2 to x = 29, back along x = 29 under the 5 V rod, up onto the GND rod. A dab of hot glue from the capacitor's side to the amp's edge, so it hangs on the amp rather than on its leads.",
                  "VIN to GND: a chirp that stops. A steady tone is a short or a backwards capacitor."))
    H.append(fig(D.map_figure(highlight={"220u lead +", "220u lead -", "220u body", "100n lead +", "100n lead -", "100n body"}, title="The two capacitors")))
    H.append(step("m18", f"{a('speaker', 'Speaker')} leads into the terminal block, never cut.", "OUT+ and OUT− to the GND rail: silent."))
    # 11
    H.append('<h2>11 · Power up</h2>')
    H.append(step("m19", f"Sweep with the {a('meter', 'meter')}, probes on bare metal: GND rail to 3V3 rail, to the 5 V rod, to OUT+, to OUT−.", "All silent (a chirp that stops is the capacitors)."))
    H.append(step("m20", "USB in. The firmware is already on the board and the server is running.", "Eyes open, <code>got ip</code>, <code>hello accepted</code>. Upside-down eyes: say so, one flag fixes it."))
    H.append(step("m21", "Hold the button, ask Pip its name, release.", "Your words in the log as <code>user: …</code>; the face reacts."))
    H.append(step("m22", "Say <em>enable the amplifier</em>; I rebuild with the amp on at cap 45, you flash.", "Pip answers out loud. Unplug, wait ten seconds, plug in, ask once more."))
    # 12
    H.append('<h2>12 · Off the card, into the frame</h2>')
    H.append(step("m23", "Cut every piece of tape and lift the harness off the card as one piece. It is rigid now: A1 hangs on eleven rods, the amp on nine, the screen on four, the rails on their eight taps. Hold it up and look through it from the front and from the side against the drawings.", "Nothing flexes when you press a module gently; the card is bare paper again."))
    H.append(step("m24", f"{a('kapton', 'Kapton')} on the inside faces of the bottom loop, the posts and the top loop. Lower the bare harness in so A1 and the amp rest on the bottom loop's tubes, USB socket at the front opening.", "Meter frame to GND rail, 3V3 rail, 5 V rod, OUT+, OUT−: silent. Power up once more inside the frame."))
    H.append(step("m25", "Hot glue, low temperature, over the Kapton: A1's two front corners and the amp's two right corners to the bottom tubes, the screen's underside to the terminal block. Nothing near the mic hole, the USB port or the button.", "Pick it up, turn it over: nothing moves. Done."))

    H.append('<div class="evidence"><p>Geometry, lengths and heights are generated from <code>edu/pages/gen/harness_model.py</code>, checked pair by pair; the fuller page with the reasoning, the numbers and the optional precautions is <code>brass-harness-step-by-step-full.html</code>. Product links are your order sheets. The harness has not been built yet.</p></div>')
    H.append('</div>')
    H.append('''<script>
  (function () {
    var boxes = Array.prototype.slice.call(document.querySelectorAll('input[type=checkbox]'));
    var key = function (b) { return "brass-harness-min-" + b.id; };
    function count() { var n = boxes.filter(function (b) { return b.checked; }).length; document.getElementById("done").textContent = n; document.getElementById("total").textContent = boxes.length; }
    boxes.forEach(function (b) { try { b.checked = localStorage.getItem(key(b)) === "1"; } catch (e) {} b.addEventListener("change", function () { try { localStorage.setItem(key(b), b.checked ? "1" : "0"); } catch (e) {} count(); }); });
    document.getElementById("reset").addEventListener("click", function () { boxes.forEach(function (b) { b.checked = false; try { localStorage.removeItem(key(b)); } catch (e) {} }); count(); });
    count();
  })();
</script>''')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
