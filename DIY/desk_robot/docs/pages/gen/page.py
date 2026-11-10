"""Assembles the desk-robot concept page (round two, 2026-11-07) from the drawings in concepts.py."""
from __future__ import annotations
import html, pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "desk_robot_concepts.html"

A = lambda href, text: f'<a href="{href}" target="_blank" rel="noopener">{text}</a>'
L = {  # the exact listings, owned ones from the inventories, new ones from the research of 2026-11-07
    "xiao": "https://www.amazon.com/dp/B0C69FFVHH", "ips": "https://www.amazon.com/dp/B0HGLQZK3P", "n20": "https://www.amazon.com/dp/B0C9QC4SRY",
    "drv": "https://www.amazon.com/dp/B07YCVHQD5", "amp": "https://www.amazon.com/dp/B0CDWXZZCH", "rng1": "https://www.pololu.com/product/3415",
    "rng8": "https://www.pololu.com/product/3418", "imu": "https://www.amazon.com/dp/B00LP25V1A", "gauge": "https://www.adafruit.com/product/5580",
    "spk": "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309",
    "cell": "https://imrbatteries.com/products/nitecore-nl169-16340-950mah-battery", "holder": "https://www.amazon.com/dp/B0CRGK889F",
    "toggle": "https://www.amazon.com/dp/B0CZ6XZ2P9", "button": "https://www.amazon.com/dp/B0FHW6HMG4", "oled": "https://www.amazon.com/dp/B09T6SJBV5",
    "rod10": "https://www.amazon.com/dp/B005WPB7YG", "rod15": "https://www.amazon.com/dp/B01C6LUO5Q", "tube": "https://www.amazon.com/dp/B0F2FKLC2N",
    "white": "https://www.amazon.com/dp/B000PIG3AS", "card": "https://www.amazon.com/dp/B0DSH5V1TT", "tape": "https://www.amazon.com/dp/B0BD84GGPV",
    "qt": "https://www.adafruit.com/product/4210", "schottky": "https://www.amazon.com/dp/B079KJ46ZS",
    "nfet": "https://www.digikey.com/en/products/detail/evvo/AO3400A-EV/26221089", "gears": "https://www.amazon.com/dp/B0881RWD2L",
    "lidar_amz": "https://www.amazon.com/dp/B0CNCLQ68L", "lidar_ws": "https://www.waveshare.com/d500-lidar-kit.htm",
    "lidar_hw": "https://www.hiwonder.com/products/stl-19p-d500-lidar", "lidar_d300": "https://www.amazon.com/dp/B0B1QCV4XR",
    "lidar_ds": "https://www.waveshare.com/wiki/D500_LiDAR_Kit", "tmini": "https://www.robotshop.com/products/ydlidar-t-mini-plus-2d-compact-lidar-sensor",
    "w32": "https://www.pololu.com/product/1088", "w40": "https://www.pololu.com/product/1454", "w60": "https://www.pololu.com/product/1424",
    "w60dk": "https://www.digikey.com/en/products/detail/pololu/1424/10449812",
    "round_amz": "https://www.amazon.com/dp/B08V5538C6", "round_ws": "https://www.waveshare.com/1.28inch-lcd-module.htm",
    "round_diy": "https://www.amazon.com/dp/B0F9NY6JZ6",
    "boost": "https://www.adafruit.com/product/6106", "boost_dk": "https://www.digikey.com/en/products/detail/adafruit-industries-llc/6106/25805552",
    "boost_guide": "https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board/pinouts",
    "pfet": "https://www.digikey.com/en/products/result?keywords=AO3401A", "lds": "https://github.com/kaiaai/LDS",
    "sheet": "https://www.amazon.com/dp/B0006N6WLM", "kapton": "https://www.amazon.com/dp/B0BSTSMLF7",
    "mochan": "https://www.huyvector.org/robots-kinetic/diy-cute-desk-robot-mo-chan", "xiao_wiki": "https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/",
}

CSS = """
/* layout: brief, then three concept blocks (three views each, stacking on phones), the comparison, the shared electronics, the parts, the pick */
:root{
  --bg:#f3efe6; --fg:#23211c; --muted:#6b665a; --line:#cfc7b5; --panel:#faf8f2; --hid:#efe9dc;
  --brass:#b4904f; --brass-dk:#7d6132; --steel:#8f949b; --ivory:#f1ead9; --ivory-2:#ece4d1; --skin-edge:#c8bc9e;
  --black:#1a1b1e; --black-2:#2a2c31; --window:#6f7f92; --tyre:#2b2d31; --tyre-2:#3a3d43; --glass:#111317; --eye:#e8f4ff; --lens:#3a6ea5;
  --beam:#c2552a; --scan:#0e5f7a; --desk:#d9cfb8; --ink:#23211c; --ok:#2a6340; --ok-soft:#dfe9df; --warn:#98351e; --warn-soft:#f3e1d9;
  --display:"Chakra Petch",ui-sans-serif,system-ui,sans-serif;
  --body:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#1b1a17; --fg:#ece7da; --muted:#a39c8c; --line:#3b382f; --panel:#23221d; --hid:#2b2922;
  --brass:#c9a35f; --brass-dk:#d4b070; --steel:#9aa0a8; --ivory:#d9d0bb; --ivory-2:#cfc5ae; --skin-edge:#9a8f74;
  --black:#0d0e10; --black-2:#1c1e23; --window:#7f91a6; --tyre:#1f2124; --tyre-2:#33363c; --glass:#07080a; --eye:#e8f4ff; --lens:#6fa0d6;
  --beam:#e0693a; --scan:#5bb8d4; --desk:#2e2b24; --ink:#ece7da; --ok:#6fbf8e; --ok-soft:#1a3325; --warn:#ee8666; --warn-soft:#3b1d14; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#1b1a17; --fg:#ece7da; --muted:#a39c8c; --line:#3b382f; --panel:#23221d; --hid:#2b2922;
  --brass:#c9a35f; --brass-dk:#d4b070; --steel:#9aa0a8; --ivory:#d9d0bb; --ivory-2:#cfc5ae; --skin-edge:#9a8f74;
  --black:#0d0e10; --black-2:#1c1e23; --window:#7f91a6; --tyre:#1f2124; --tyre-2:#33363c; --glass:#07080a; --eye:#e8f4ff; --lens:#6fa0d6;
  --beam:#e0693a; --scan:#5bb8d4; --desk:#2e2b24; --ink:#ece7da; --ok:#6fbf8e; --ok-soft:#1a3325; --warn:#ee8666; --warn-soft:#3b1d14; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--body);line-height:1.5;margin:0;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 56px}
main{max-width:1120px;margin:0 auto;display:grid;gap:34px}
h1{font-family:var(--display);font-weight:600;font-size:clamp(1.6rem,3.6vw,2.3rem);margin:0;text-wrap:balance;letter-spacing:.01em;line-height:1.15}
h2{font-family:var(--display);font-weight:600;font-size:1.25rem;margin:0 0 8px;letter-spacing:.02em;text-wrap:balance}
h3{font-family:var(--mono);font-weight:500;font-size:.78rem;margin:14px 0 4px;letter-spacing:.08em;text-transform:uppercase;color:var(--brass-dk)}
p{margin:0 0 8px;max-width:72ch}
ul,ol{margin:4px 0 8px;padding-left:20px;max-width:72ch}
li{margin:3px 0}
a{color:var(--brass-dk);text-decoration-thickness:1px;text-underline-offset:2px}
.eyebrow{font-family:var(--mono);font-size:.76rem;color:var(--muted);letter-spacing:.06em;text-transform:uppercase}
.lede{font-size:1.05rem;max-width:78ch}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);padding:14px 16px;min-width:0}
.card h3{margin-top:0}
.card ul{margin-bottom:0;padding-left:18px;font-size:.94rem}
.concept{border-top:3px solid var(--brass);padding-top:14px;display:grid;gap:12px}
.concept .head{display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:baseline}
.letter{font-family:var(--display);font-weight:600;font-size:2rem;color:var(--brass);line-height:1}
.views{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
figure{margin:0;background:var(--panel);border:1px solid var(--line);padding:12px 12px 8px;min-width:0}
figure svg{width:100%;height:auto;display:block}
figcaption{font-family:var(--mono);font-size:.76rem;color:var(--muted);margin-top:8px;line-height:1.45}
.dims{font-family:var(--mono);font-size:.84rem;color:var(--muted)}
.key{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2px 26px;font-size:.9rem}
.key div{display:grid;grid-template-columns:2em 1fr;gap:8px;padding:5px 0;border-bottom:1px solid var(--line);min-width:0}
.key b{font-family:var(--mono);font-weight:500;color:var(--brass-dk)}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:4px 28px}
.two>div{min-width:0}
.stack{display:grid;gap:18px}
.stack>div{min-width:0}
.trade{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.trade div{padding:10px 14px;border-left:3px solid var(--ok);background:var(--panel);font-size:.92rem;min-width:0}
.trade div.minus{border-left-color:var(--warn)}
.trade ul{margin:0;padding-left:18px}
table{border-collapse:collapse;font-size:.88rem;width:100%}
th,td{text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:var(--mono);font-weight:500;color:var(--muted);font-size:.74rem;letter-spacing:.04em;text-transform:uppercase}
td.m,th.m{font-family:var(--mono);font-size:.8rem;white-space:nowrap}
.tw{overflow-x:auto;min-width:0}
.tw table{min-width:640px}
.note{background:var(--panel);border-left:3px solid var(--brass);padding:10px 14px;font-size:.92rem;max-width:none}
.pick{background:var(--panel);border:1px solid var(--brass);padding:16px 18px}
.pick p{max-width:78ch}
svg text{font-family:var(--mono);font-size:7.5px;fill:var(--muted)}
svg text.tag{fill:var(--brass-dk);font-weight:500}
svg text.hid{font-size:6.5px}
svg text.dimlab{font-size:7px}
svg.blk text{font-family:var(--body);font-size:12.5px;fill:var(--fg)}
svg.blk text.t{font-family:var(--display);font-weight:600;font-size:13.5px}
svg.blk text.s{font-size:11px;fill:var(--muted)}
svg.blk text.r{font-family:var(--mono);font-size:10.5px;fill:var(--brass-dk);font-weight:500}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""


# ----------------------------------------------------------------------------- the shared electronics, as a block diagram
def block_diagram():
    W, H = 1130, 640
    o = [f'<svg class="blk" viewBox="0 0 {W} {H}" role="img" aria-label="Power tree and buses shared by the three prototypes">']
    o.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')
    def box(x, y, w, h, title, lines, stroke="var(--line)"):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="var(--panel)" stroke="{stroke}" stroke-width="1.2"/>')
        o.append(f'<text class="t" x="{x + 10}" y="{y + 20}">{html.escape(title)}</text>')
        for i, ln in enumerate(lines):
            o.append(f'<text class="s" x="{x + 10}" y="{y + 38 + i * 15}">{html.escape(ln)}</text>')
    def wire(pts, color="currentColor", width=1.6, arrow=True, dash=""):
        d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(pts))
        o.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" {"marker-end=\"url(#ah)\"" if arrow else ""} '
                 f'{"stroke-dasharray=\"" + dash + "\"" if dash else ""} style="color:{color}"/>')
    def lab(x, y, s, cls="r", anchor="start"):
        o.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{html.escape(s)}</text>')

    BR, CELL, SIG = "var(--brass-dk)", "var(--warn)", "var(--scan)"
    # left column: the cell chain
    box(40, 40, 170, 56, "16340 cell", ["Nitecore, 950 mAh, protected", "in its holder, owned"])
    box(40, 126, 170, 44, "toggle", ["in the + lead, owned"])
    box(40, 210, 170, 118, "charger + 5 V boost", ["Adafruit bq25185 board, USB-C", "charge 500 mA (cut its jumper)", "boost 5 V, 1 A, EN pad", "runs while charging"])
    box(40, 364, 170, 82, "I²C motor driver", ["SparkFun Qwiic, 0x5D, owned", "VIN from the cell rail", "two N20 motors, owned"])
    box(40, 480, 170, 56, "fuel gauge", ["MAX17048, 0x36, owned", "reads the cell"])
    wire([(125, 96), (125, 126)], CELL, arrow=False); wire([(125, 170), (125, 210)], CELL, arrow=False)
    o.append(f'<circle cx="125" cy="190" r="3.5" fill="{CELL}"/>')
    wire([(125, 190), (24, 190), (24, 508), (40, 508)], CELL, arrow=True); wire([(24, 405), (40, 405)], CELL, arrow=True)
    lab(14, 300, "cell rail 3.0–4.2 V", anchor="middle"); o[-1] = o[-1].replace('<text', '<text transform="rotate(-90 14 300)"', 1)
    # 5 V rail: up the left of the charger, along the top, down the right edge
    wire([(210, 269), (236, 269), (236, 18), (1104, 18), (1104, 600)], BR, width=2.2, arrow=False)
    lab(640, 12, "5 V rail from the boost (1 A): XIAO, lidar, amplifier", anchor="middle")
    # XIAO
    box(400, 90, 290, 220, "XIAO ESP32-S3 Sense", ["camera + PDM microphone on the board, owned", "5V pin ← rail through a Schottky; BAT pads empty",
                                                   "3V3 out: 600 mA for screen and sensors", "I²S1 → amp · I²C → chain · UART1 ← lidar",
                                                   "SPI → screen (Mochi, Lantern)", "GPIO → lidar 5 V switch, on after boot",
                                                   "USB-C for flashing with the robot OFF", "cut jumper J3 (frees GPIO 7, 8, 9)"])
    wire([(470, 18), (470, 90)], BR, arrow=True); o.append('<polygon points="463,52 477,52 470,62" fill="var(--panel)" stroke="var(--brass-dk)" stroke-width="1.4"/>')
    o.append('<line x1="463" y1="62" x2="477" y2="62" stroke="var(--brass-dk)" stroke-width="1.6"/>'); lab(482, 60, "Schottky, owned")
    # right column: lidar switch, lidar, amp
    box(880, 100, 160, 50, "lidar 5 V switch", ["P-MOSFET + owned N-MOSFET"])
    wire([(1104, 125), (1040, 125)], BR, arrow=True)
    wire([(690, 125), (880, 125)], SIG, arrow=True); lab(700, 119, "GPIO: on 1 s after boot")
    box(840, 176, 240, 84, "lidar, STL-19P (D500 kit)", ["5 V, 290 mA running, 300 mA start", "TX 230400 baud, 3.3 V → XIAO RX", "PWM pin left open: 10 Hz", "black Ø38.6 body, 45 g"])
    wire([(960, 150), (960, 176)], BR, arrow=True)
    wire([(840, 220), (690, 220)], SIG, arrow=True); lab(700, 214, "UART1 RX, 230400")
    box(840, 290, 240, 66, "I²S amplifier + speaker", ["MAX98357A and the 20 × 13 speaker, owned", "VIN from the 5 V rail; SD on its pull-up"])
    wire([(1104, 323), (1080, 323)], BR, arrow=True)
    wire([(690, 295), (840, 295)], SIG, arrow=True); lab(700, 289, "I²S1: BCLK, LRC, DIN")
    # bottom: face, ranger+IMU, and the I²C chain
    box(400, 400, 220, 90, "the face", ["Mochi: 1.28\" round, SPI", "Lantern: 1.54\" square, SPI, owned", "Wheelie: two 0.96\" OLEDs, I²C, owned", "3V3 from the XIAO"])
    box(760, 400, 220, 76, "edge ranger + motion sensor", ["VL53L1X 0x29 and MPU6050 0x68", "both owned, on the I²C chain", "chain carries 3V3 too"])
    wire([(470, 310), (470, 400)], SIG, arrow=True); lab(478, 360, "SPI or I²C, 3V3")
    wire([(650, 310), (650, 580)], SIG, arrow=False)
    wire([(125, 580), (1060, 580)], SIG, width=2, arrow=False)
    lab(640, 604, "I²C chain, Qwiic/QT cables where the boards have sockets: 3V3, GND, SDA, SCL · 400 kHz · pull-ups trimmed to one set", anchor="middle")
    wire([(125, 580), (125, 536)], SIG, arrow=True); wire([(210, 405), (240, 405), (240, 580)], SIG, arrow=False)
    wire([(870, 580), (870, 476)], SIG, arrow=True); wire([(1040, 580), (1040, 536)], SIG, arrow=True)
    o.append('<rect x="1000" y="490" width="80" height="46" rx="4" fill="var(--panel)" stroke="var(--line)" stroke-width="1.2" stroke-dasharray="4 3"/>')
    lab(1040, 509, "Wheelie’s", cls="s", anchor="middle"); lab(1040, 524, "eyes, I²C", cls="s", anchor="middle")
    o.append(f'<circle cx="650" cy="580" r="3.5" fill="{SIG}"/><circle cx="240" cy="580" r="3.5" fill="{SIG}"/><circle cx="870" cy="580" r="3.5" fill="{SIG}"/>')
    lab(1104, 616, "GND: every return to the star at the cell holder; the brass is not a conductor", anchor="end", cls="s")
    o.append("</svg>")
    return "".join(o)


# ----------------------------------------------------------------------------- the page
def write(concepts):
    a, b, c = concepts
    figs = lambda cpt: '<div class="views">' + "".join(f"<figure>{svg}<figcaption>{html.escape(cap)}</figcaption></figure>" for svg, cap in cpt["views"]) + "</div>"
    key = lambda cpt: '<div class="key">' + "".join(f"<div><b>{n}</b><span>{html.escape(t)}</span></div>" for n, t in cpt["key"]) + "</div>"

    head = f"""<title>Desk Robot Prototypes</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<main>
<header style="display:grid;gap:10px">
  <span class="eyebrow">Desk robot · round two · three prototypes for a pick · 2026-11-07 · nothing new bought, nothing built</span>
  <h1>Three prototypes for the brass-and-ivory desk robot</h1>
  <p class="lede">Crumb’s parts have been on the bench since 2026-11-03: the two gear motors, the I²C motor driver, three colour screens, the amplifiers; its controller lands by 11-11. These three keep every one of them and add what you asked for today: a frame that is not Mo-chan’s wire hexagon, ivory wheels, a camera, a real spinning lidar, a speaker and a microphone, in white, ivory, brass and black only. The electronics are the same in all three. What changes is the body, the face, and where the lidar sits. Pick one and the pin-to-pin wiring sheet follows.</p>
  <p class="dims">Same scale in every drawing · millimetres · front, side (face to the right) and top (face at the top) · dashed boxes are parts hidden inside the skin · the blue dashed line is the lidar’s scan plane, the orange dashes the edge ranger’s field</p>
</header>

<section class="cards">
  <div class="card"><h3>You asked for</h3><ul>
    <li>Brass-coloured, with ivory wheels; cute; compact.</li>
    <li>A frame that is its own, not {A(L['mochan'], 'Mo-chan’s')} copper hexagon.</li>
    <li>A camera, a lidar, a small speaker and a microphone.</li>
    <li>Three prototype drawings before anything else.</li></ul></div>
  <div class="card"><h3>Already in Crumb’s bin</h3><ul>
    <li>{A(L['xiao'], 'XIAO ESP32-S3 Sense')} (camera, microphone; by 11-11), {A(L['ips'], '1.54" colour screens')} ×3, {A(L['n20'], 'N20 gear motors')} ×2, {A(L['drv'], 'I²C motor driver')}, {A(L['amp'], 'I²S amplifier')}.</li>
    <li>From shared stock: {A(L['cell'], '16340 cell')}, {A(L['holder'], 'holder')}, {A(L['toggle'], 'toggle')}, {A(L['spk'], 'speaker')}, {A(L['gauge'], 'fuel gauge')}, {A(L['rng1'], 'single-point laser ranger')}, {A(L['imu'], 'motion sensor')} (3-pack ordered 11-07), {A(L['oled'], '0.96" OLEDs')} (7 spare), {A(L['rod15'], '1.5 mm')} and {A(L['rod10'], '1.0 mm brass rod')}, {A(L['white'], 'canvas-white spray')} (Pip’s ivory), {A(L['card'], 'cardstock')}, {A(L['tape'], 'clear tape')}.</li>
    <li>Set aside, back to the shared bin: the two {A(L['gears'], '64-tooth steel gears')} (ivory wheels replace them) and the {A(L['rng8'], '8×8 ranger')} (the lidar does its job).</li></ul></div>
  <div class="card"><h3>New, the same in all three</h3><ul>
    <li>The lidar: LDROBOT STL-19P as the {A(L['lidar_amz'], 'Waveshare D500 kit')} (Amazon; ${'95.99'} at {A(L['lidar_ws'], 'Waveshare')}, ${'99.99'} at {A(L['lidar_hw'], 'Hiwonder')}).</li>
    <li>One pair of Pololu white wheels: {A(L['w32'], '32 mm')} (Mochi, ${'4.45'}), {A(L['w40'], '40 mm')} (Lantern, ${'5.45'}) or {A(L['w60'], '60 mm')} (Wheelie, ${'6.75'}). Not sold on Amazon in white.</li>
    <li>The {A(L['boost'], 'charger + 5 V boost board')} (Adafruit, ${'8.95'}; also {A(L['boost_dk'], 'DigiKey')}) and one {A(L['pfet'], 'P-channel MOSFET')} for the lidar’s power switch.</li>
    <li>Mochi alone adds the {A(L['round_amz'], '1.28" round screen')} (about ${'15'}).</li></ul></div>
</section>

<p class="note"><strong>The colour rule, applied.</strong> The skins are ivory card sprayed canvas white, Pip’s white; the brass rods show only as the edges of the body, two hoops and two rails at most; black is allowed only where it cannot be helped: the lidar’s body, the screen’s glass, the camera’s lens, the tyres. No board shows anywhere. The wheels come white; spray their faces canvas white with the tyre masked if you want them to match the skin exactly.</p>
"""

    def concept_block(letter, cpt, title, character, why, plus, minus):
        return f"""
<section class="concept" id="{cpt['name'].lower()}">
  <div class="head"><span class="letter">{letter}</span><div><h2>{html.escape(title)}</h2><p>{character}</p><p class="dims">{html.escape(cpt['dims'])}</p></div></div>
  {figs(cpt)}
  <h3>Key</h3>{key(cpt)}
  <div class="two"><div><h3>Why these numbers</h3><ul>{''.join(f'<li>{w}</li>' for w in why)}</ul></div>
  <div><h3>The trade</h3><div class="trade"><div><ul>{''.join(f'<li>{w}</li>' for w in plus)}</ul></div><div class="minus"><ul>{''.join(f'<li>{w}</li>' for w in minus)}</ul></div></div></div></div>
</section>"""

    blk_a = concept_block("A", a, "Mochi: a loaf with a hat",
        "A soft ivory loaf, 56 mm square in plan and 55 tall, with brass edges, one big round face and a black hat that spins. The wheels are small and tucked under, so it glides more than it rolls. It is the most compact of the three and the simplest frame: two hoops and two rails.",
        ["56 wide is two motors end to end (24 + 2 + 24) and the card. 56 deep is the cell across the back, the motors, and the screen with the XIAO behind it.",
         "Ø31 wheels keep the axle at 16 and the body low, so the hat does not make it tall: 94 over everything.",
         "The lidar’s flange is wider than its body (54 × 46 mm), so it hides under the top skin on two cross rods and only the round 33 mm body shows, 3 mm behind centre.",
         "The round screen’s board is Ø37.5, so the front needs a 40 mm flat zone: corner radius 6, not 10.",
         "The cell sits across the back above the motors’ tails: the centre of mass lands 4 mm behind the axle, on the tail skid; the nose skid rides 1 mm up and catches a hard stop."],
        ["The smallest and the softest shape; the hat is the custom spin in one glance.", "Fewest rods, one card wrap, flat panels front and back.", "Lidar plane clear through 360°."],
        ["Its plane is 86 mm up: it sees mugs, hands, laptop lids and monitor feet, not books, phones or pens. The edge ranger, the camera and the bump sensor cover the low desk.",
         "The round screen is a purchase; the owned square screen fits the same front with a 38 mm flat zone if you would rather not buy it."])

    blk_b = concept_block("B", b, "Lantern: a head floating over the lidar",
        "Two ivory blocks with brass edges and the lidar’s black rotor turning in the open band between them, like a lantern. The puck holds the heavy parts, the head holds the face, and three thin brass posts carry the head. It is the tallest, and the one that sees best.",
        ["The puck is 27 tall: the motors at axle 19 pass under the lidar’s flange at 25, so the lidar can sit 7 mm down into the puck.",
         "The band is the lidar’s own height above the puck plus 2 mm; the head is 44 tall because the owned 36 mm screen wants the lens above it.",
         "Ø40 wheels at the back of the puck sit flush with its back face; the cell lies ahead of them, under the lidar.",
         "Three 1.5 mm posts (two front corners, one back centre) hide 2–3° of the scan each; the loom of motor wires, cell leads and the I²C chain runs down the back post.",
         "The centre of mass is 9 mm ahead of the axle and 42 mm up: it rests on its nose skid and tips backward only above 2 m/s², which the firmware never asks for."],
        ["The best lidar view of the three: 52 mm up, all round, 360° but three slivers.", "Uses the owned square screen; nothing to buy for the face.", "The heavy parts are low in the puck."],
        ["Tallest at 106 mm.", "Every wire between puck and head runs down a post; the loom must be neat or it shows.", "Two storeys read more ‘robot’ than ‘cute’; the proportion depends on the band staying black and empty."])

    blk_c = concept_block("C", c, "Wheelie: big ivory wheels and a slim body",
        "Two big ivory wheels, a slim ivory capsule between them, two white eyes up high, and the lidar’s rotor looking out of a slot low in the front. It leans forward on its nose; the wheels sit behind the middle. It is the one where the ivory wheels are the design.",
        ["Ø60 wheels put the motors at 25–35 up, exactly where the lidar’s rotor would be, so the lidar stands 26 mm ahead of the axle and the wheels end 16 mm behind the body.",
         "The body is 56 wide for the lidar’s 54 mm flange; the two eye boards toe in 12° so the head reads as round and the eyes look at you from both sides.",
         "The slot is 21 mm tall, the rotor’s window plus margins; its lips are 1.0 mm rod, its back edge one short post.",
         "The cell lies across the back just above the lidar’s top; the centre of mass is 12 mm ahead of the axle, so the nose skid carries about a quarter of the weight.",
         "The downward ranger sits under the left eye and clears the rotor on its way to the desk."],
        ["The lowest scan plane, 33 mm: it sees books, phones, a mug’s foot, a hand on the desk.", "The wheels are the feature, as asked.", "Owned eyes; nothing to buy for the face."],
        ["Longest at 76 mm over the wheels; the wheels reach past the back.", "Each wheel hides about ±45° of the scan; the lidar sees forward and back, not sideways.", "The slot shows the black lidar body; less soft than the other two."])

    compare = f"""
<section>
  <h2>Side by side</h2>
  <div class="tw"><table>
    <tr><th></th><th>A · Mochi</th><th>B · Lantern</th><th>C · Wheelie</th></tr>
    <tr><td>Envelope W × D × H</td><td class="m">72 × 56 × 94</td><td class="m">72 × 56 × 106</td><td class="m">74 × 76 × 100</td></tr>
    <tr><td>Mass, estimated</td><td class="m">212 g</td><td class="m">208 g</td><td class="m">218 g</td></tr>
    <tr><td>Wheels</td><td>Ø31 × 7, axle 16</td><td>Ø40 × 7, axle 19</td><td>Ø60 × 8, axle 30</td></tr>
    <tr><td>Speed on the cell, about</td><td class="m">7 cm/s</td><td class="m">9 cm/s</td><td class="m">14 cm/s</td></tr>
    <tr><td>Face</td><td>1.28" round colour (buy)</td><td>1.54" square colour (owned)</td><td>two 0.96" OLED eyes (owned)</td></tr>
    <tr><td>Lidar plane</td><td>86 mm up, 360°</td><td>52 mm up, 360° less three 2° slivers</td><td>33 mm up, front and back; wheels hide ±45° each side</td></tr>
    <tr><td>What it sees on a desk</td><td>mugs, hands, laptops, monitor feet</td><td>plus tall books, a phone on its stand</td><td>plus flat books, phones, a mug’s foot</td></tr>
    <tr><td>Rods beyond the outline</td><td>2 (the rails)</td><td>3 (the posts)</td><td>3 (the slot’s lips and post)</td></tr>
    <tr><td>Rests on</td><td>tail skid, nose skid 1 mm up</td><td>nose skid</td><td>nose skid</td></tr>
    <tr><td>Card skin</td><td>one wrap round the hoops, two flat ends</td><td>two wraps, flat tops</td><td>one wrap, two flat sides, a slot</td></tr>
    <tr><td>To buy</td><td>lidar, 32 mm wheels, charger-boost, P-MOSFET, round screen</td><td>lidar, 40 mm wheels, charger-boost, P-MOSFET</td><td>lidar, 60 mm wheels, charger-boost, P-MOSFET</td></tr>
    <tr><td>About</td><td class="m">$126 + shipping</td><td class="m">$111 + shipping</td><td class="m">$112 + shipping</td></tr>
    <tr><td>Cute cue</td><td>a loaf in a top hat, one round eye-pair</td><td>a floating head, a glowing band</td><td>big wheels, two toed-in eyes, leaning in</td></tr>
    <tr><td>First risk</td><td>the hat’s height against the body: mock it in card first</td><td>the loom in the posts; Wi-Fi through two card boxes is fine</td><td>the tread on the desk: silicone tyres grip, so the nose skid must slide</td></tr>
  </table></div>
  <p class="note">Without the spinning lidar every concept loses 35 mm of height, 45 g and about $96: the owned 8×8 ranger goes back on the brow as in Crumb. Say so if you would rather start there and add the lidar later; the drawings only lose the hat, the band, or the slot.</p>
</section>"""

    electronics = f"""
<section>
  <h2>What they share: the electronics</h2>
  <p>One cell, one boost, one brain. The cell feeds the motor driver straight (the motors never load the boost) and the {A(L['boost'], 'charger-boost board')}, which makes the 5 V rail for the XIAO, the lidar and the amplifier and charges the cell at 500 mA over its own USB-C while the robot keeps running. The XIAO’s 5V pin takes the rail through a Schottky, as Seeed’s {A(L['xiao_wiki'], 'wiki')} asks, so the robot can be flashed over the XIAO’s USB-C with the toggle off and the PC never back-feeds the rail. The lidar gets its 5 V through a small MOSFET switch the firmware closes a second after boot, because the boost chip stalls if 300 mA is hanging on it at power-up ({A(L['boost_guide'], 'Adafruit’s note')}); the same switch is the lidar’s sleep.</p>
  <figure>{block_diagram()}<figcaption>Power tree and buses. Brass: the 5 V rail. Red: the cell rail. Blue: signals and the I²C chain. The lidar’s serial output is 3.3 V and one-way, so it needs no level shifting; its packet format is in the {A(L['lds'], 'LDS Arduino library')}, which already runs on the ESP32-S3.</figcaption></figure>
  <div class="stack">
    <div><h3>Pin budget, XIAO ESP32-S3 Sense (J3 cut)</h3><div class="tw"><table>
      <tr><th>Pin</th><th>GPIO</th><th>Mochi and Lantern (SPI screen)</th><th>Wheelie (I²C eyes)</th></tr>
      <tr><td class="m">D0</td><td class="m">1</td><td>screen SCK</td><td>lidar 5 V switch</td></tr>
      <tr><td class="m">D1</td><td class="m">2</td><td>screen MOSI</td><td>lidar PWM, optional</td></tr>
      <tr><td class="m">D2</td><td class="m">3</td><td>screen DC</td><td>action button</td></tr>
      <tr><td class="m">D3</td><td class="m">4</td><td>lidar TX in (UART1 RX)</td><td>lidar TX in (UART1 RX)</td></tr>
      <tr><td class="m">D4</td><td class="m">5</td><td>I²C SDA</td><td>I²C SDA, eyes at 0x3C and 0x3D</td></tr>
      <tr><td class="m">D5</td><td class="m">6</td><td>I²C SCL</td><td>I²C SCL</td></tr>
      <tr><td class="m">D6</td><td class="m">43</td><td>screen backlight PWM (the ROM chatters here at boot: a harmless flicker)</td><td>status light</td></tr>
      <tr><td class="m">D7</td><td class="m">44</td><td>lidar 5 V switch (an input at boot; a 100 kΩ pull-down keeps the lidar off)</td><td>spare</td></tr>
      <tr><td class="m">D8–D10</td><td class="m">7, 8, 9</td><td>I²S BCLK, LRC, DIN to the amp</td><td>same</td></tr>
      <tr><td class="m">5V · 3V3</td><td class="m">—</td><td>rail in through the Schottky · out to screen and chain</td><td>same</td></tr>
    </table></div>
    <p class="dims">Mochi and Lantern have no pin left for a button: a double tap on the body, read by the motion sensor, is the button. Only one ST ranger stays, so the address dance of Crumb’s plan is gone. The camera and the PDM microphone are on the Sense board’s own pins; the microphone keeps I²S0, the amp runs on I²S1, as before.</p></div>
    <div><h3>Power budget and run time</h3><div class="tw"><table>
      <tr><th>Load</th><th>Rail</th><th class="m">Typical</th><th class="m">Peak</th></tr>
      <tr><td>XIAO with the camera streaming</td><td>5 V, its own buck</td><td class="m">220 mA</td><td class="m">330</td></tr>
      <tr><td>Lidar spinning</td><td>5 V, switched</td><td class="m">290 mA</td><td class="m">300 at start</td></tr>
      <tr><td>Amplifier at the usual cap</td><td>5 V</td><td class="m">30 mA</td><td class="m">300</td></tr>
      <tr><td>Screen or eyes, ranger, motion sensor, gauge, driver logic</td><td>3V3 from the XIAO</td><td class="m">80 mA</td><td class="m">120</td></tr>
      <tr><td><strong>5 V rail</strong></td><td>boost, 1 A</td><td class="m"><strong>≈ 600 mA</strong></td><td class="m"><strong>≈ 950</strong></td></tr>
      <tr><td>Two motors, cell rail</td><td>cell, 2 A protection</td><td class="m">150 mA</td><td class="m">700, one stalled</td></tr>
    </table></div>
    <p class="dims">From the cell that is about 1.0 A while roaming with the lidar on: close to an hour. Lidar spinning only while it moves, about 1.5 h. Parked with the face on, lidar and camera off, 0.2 A: four to five hours. A full charge at 500 mA takes about 2.2 h, and the robot can keep running on the lead.</p></div>
  </div>
</section>"""

    parts = f"""
<section>
  <h2>Parts</h2>
  <div class="stack">
  <div><h3>Owned: Crumb’s bin and the shared bin</h3><div class="tw"><table>
    <tr><th>Qty</th><th>Part</th><th>Note</th></tr>
    <tr><td class="m">1</td><td>{A(L['xiao'], 'XIAO ESP32-S3 Sense')}</td><td>Crumb’s, in transit, by 11-11. Camera, microphone, Wi-Fi. Cut J3.</td></tr>
    <tr><td class="m">2</td><td>{A(L['n20'], 'N20 gear motors, 6 V 100 rpm')}</td><td>Crumb’s. 3 mm D-shaft, 10 mm long: the Pololu hubs press straight on.</td></tr>
    <tr><td class="m">1</td><td>{A(L['drv'], 'SparkFun Qwiic motor driver')}</td><td>Crumb’s. On the cell rail; cut its I²C pull-up jumper.</td></tr>
    <tr><td class="m">1</td><td>{A(L['ips'], '1.54" colour screen')}</td><td>Lantern’s face; Mochi’s fallback. Two more spare.</td></tr>
    <tr><td class="m">2</td><td>{A(L['oled'], '0.96" white OLEDs')}</td><td>Wheelie’s eyes; move one module’s address jumper to 0x3D.</td></tr>
    <tr><td class="m">1</td><td>{A(L['amp'], 'MAX98357A amplifier')} + {A(L['spk'], 'speaker')}</td><td>From the twelve and the six.</td></tr>
    <tr><td class="m">1</td><td>{A(L['rng1'], 'VL53L1X laser ranger')}</td><td>Crumb’s. The edge stop, 0x29, no re-addressing now.</td></tr>
    <tr><td class="m">1</td><td>{A(L['imu'], 'MPU6050 motion sensor')}</td><td>From the 3-pack ordered 11-07. Unsolder its 2.2 kΩ pull-ups.</td></tr>
    <tr><td class="m">1</td><td>{A(L['gauge'], 'MAX17048 fuel gauge')}</td><td>Crumb’s share. On the cell, QT cable to the chain.</td></tr>
    <tr><td class="m">1 + 1 + 1</td><td>{A(L['cell'], '16340 cell')}, {A(L['holder'], 'holder')}, {A(L['toggle'], 'toggle')}</td><td>Shared stock; eight cells spare.</td></tr>
    <tr><td class="m">1</td><td>{A(L['button'], 'tactile button')}</td><td>Wheelie only; the other two use a tap.</td></tr>
    <tr><td class="m">2 + 1</td><td>{A(L['schottky'], 'Schottky diode')}, {A(L['nfet'], 'AO3400A N-MOSFET')}</td><td>Rail into the XIAO; the driver half of the lidar switch. Drone stock, plenty.</td></tr>
    <tr><td class="m">≈ 2 rods + 2</td><td>{A(L['rod15'], '1.5 mm brass rod')} (hoops), {A(L['rod10'], '1.0 mm rod')} (rails, lips, skid posts)</td><td>About 87 and 8 spare rods.</td></tr>
    <tr><td class="m">≈ 20 mm</td><td>{A(L['tube'], '4 mm brass tube')}</td><td>Skid domes. Hubs are no longer needed.</td></tr>
    <tr><td class="m">2 sheets</td><td>{A(L['card'], 'cardstock')} + {A(L['white'], 'canvas-white spray')} + {A(L['tape'], 'clear tape')}</td><td>The skins: cut, wrap, spray; tape over the sprayed faces where fingers go.</td></tr>
    <tr><td class="m">as needed</td><td>26 and 30 AWG wire, Kapton, heat-shrink, {A(L['qt'], 'QT cables')}, 10 kΩ, 100 kΩ, 220 µF, 100 nF</td><td>Bench stock.</td></tr>
  </table></div></div>
  <div><h3>To buy (Amazon first, then DigiKey, then Adafruit; Pololu only where nobody else has it)</h3><div class="tw"><table>
    <tr><th>For</th><th>Part</th><th>Where, price</th><th>Why this one</th></tr>
    <tr><td>all</td><td>LDROBOT STL-19P lidar, the Waveshare D500 kit (sensor, pigtail, USB adapter for the bench)</td><td>{A(L['lidar_amz'], 'Amazon')} (price not read; the page blocks me) · {A(L['lidar_ws'], 'Waveshare $95.99')} · {A(L['lidar_hw'], 'Hiwonder $99.99')}</td><td>The smallest spinning lidar sold today that is in stock: Ø38.6 × 34.8 mm, 45 g, 5 V 290 mA, 3.3 V serial out, 3 cm to 12 m, ±10 mm up to 50 cm, 5000 points a second. Same housing as the older {A(L['lidar_d300'], 'D300')}, which is fine if you find it. {A(L['lidar_ds'], 'Datasheet and drawing')}. Runner-up {A(L['tmini'], 'YDLIDAR T-mini Plus')}: no flange, but 340 mA running and 1 A at start.</td></tr>
    <tr><td>all</td><td>{A(L['boost'], 'Adafruit bq25185 charger with 5 V boost')}</td><td>{A(L['boost_dk'], 'DigiKey')} · Adafruit $8.95. Not on Amazon.</td><td>USB-C, 500 mA charge after cutting its jumper, 5 V 1 A boost that keeps running on the charger, an EN pad, 29 × 19 mm. Replaces the XIAO’s 100 mA charger: a full cell in 2.2 h, not 10.</td></tr>
    <tr><td>all</td><td>P-channel MOSFET, SOT-23 (AO3401A or similar)</td><td>{A(L['pfet'], 'DigiKey')}, under $1</td><td>The high side of the lidar’s 5 V switch; the owned N-MOSFET pulls its gate. Unpowered, the lidar then floats nowhere near the XIAO’s pins.</td></tr>
    <tr><td>Mochi</td><td>{A(L['w32'], 'Pololu wheel 32×7 mm pair, white')}</td><td>Pololu $4.45</td><td>Ø31 over the silicone tyre, 3.1 g each, press fit on the 3 mm D-shaft; the shaft stands 1.4 mm proud outside, hidden by a dot of ivory card.</td></tr>
    <tr><td>Lantern</td><td>{A(L['w40'], 'Pololu wheel 40×7 mm pair, white')}</td><td>Pololu $5.45</td><td>4.3 g each, same hub.</td></tr>
    <tr><td>Wheelie</td><td>{A(L['w60'], 'Pololu wheel 60×8 mm pair, white')}</td><td>{A(L['w60dk'], 'DigiKey marketplace')} (ships from Pololu) · Pololu $6.75</td><td>11.3 g each; its 11 mm hub swallows the whole shaft.</td></tr>
    <tr><td>Mochi</td><td>{A(L['round_amz'], 'Waveshare 1.28" round LCD, GC9A01')}</td><td>Amazon (price not read) · {A(L['round_ws'], 'Waveshare $14.99')}</td><td>Round Ø37.5 board, Ø32.4 picture, 8-pin cable with a backlight pin for dimming at night. The {A(L['round_diy'], 'DIYables one')} ($14.99, Amazon) is square-boarded and always lit.</td></tr>
  </table></div>
  <p class="dims">Not needed: screws (the flange is hot-glued to its rods, the family way), brass sheet, anything printed, super glue.</p></div>
  </div>
</section>"""

    mochan = f"""
<section>
  <h2>Next to Mo-chan</h2>
  <div class="tw"><table>
    <tr><th>Element</th><th>{A(L['mochan'], 'Mo-chan')}</th><th>These three</th></tr>
    <tr><td>Frame</td><td>a bare copper-wire hexagonal prism, bent on an A4 template</td><td>ivory card skins on brass hoops and rails: the brass is the edge line, the body is a soft loaf, a lantern or a capsule</td></tr>
    <tr><td>Wheels</td><td>two steel 64-tooth gears, almost as tall as the body</td><td>ivory discs with black silicone tyres, small and tucked (A), flush with the puck (B), or the whole point (C)</td></tr>
    <tr><td>Face</td><td>one blue 0.96" OLED</td><td>a round colour eye-pair (A), a square colour face (B), two white OLED eyes toed in (C)</td></tr>
    <tr><td>Senses</td><td>none</td><td>a spinning lidar, a camera, a downward laser ranger for the edge, a motion sensor for bumps and heading</td></tr>
    <tr><td>Voice</td><td>none</td><td>an I²S amplifier and a sealed speaker; the microphone on the controller board</td></tr>
    <tr><td>Brain, driver</td><td>ESP32-C3 SuperMini, a mini L298N on four pins</td><td>XIAO ESP32-S3 Sense, an I²C motor driver with no motor pins at all</td></tr>
    <tr><td>Power</td><td>a pouch cell on a TP4056</td><td>a swappable protected 16340, a charger-boost with power path, a fuel gauge, a toggle</td></tr>
  </table></div>
</section>"""

    pick = f"""
<section class="pick" id="pick">
  <h2>What I need from you</h2>
  <p><strong>Pick one letter</strong>, or a mix (Mochi’s body with Wheelie’s eyes is a legal combination; Lantern’s band on Mochi’s loaf is not, the motors are in the way). My pick is <strong>A, Mochi</strong>: it is the most compact, the softest shape, the fewest rods, and the hat says “custom” before the robot moves. Its one real cost is a high lidar plane, and the edge ranger, the camera and the bump sensor already cover the low desk. If the big ivory wheels matter more than compactness, C.</p>
  <p>Three small decisions ride along: the round screen for Mochi (buy, about $15) or the owned square one; the wheels left white or sprayed canvas white; and whether the lidar goes in now or the owned 8×8 ranger stands in for a first, 35 mm shorter version.</p>
  <p>Then step one finishes the family way: the chosen body redrawn at full detail with every part placed, the wiring sheet pin to pin at about 95 % confidence, and the order list in Amazon, DigiKey, Adafruit order. Education pages and firmware wait for the approved diagram, as the house rule says.</p>
</section>
</main>"""

    OUT.write_text(head + blk_a + blk_b + blk_c + compare + electronics + parts + mochan + pick)
    print("wrote", OUT, OUT.stat().st_size, "bytes")
