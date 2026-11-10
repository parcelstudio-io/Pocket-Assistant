"""Builds edu/pages/brass-harness-step-by-step.html from the harness model and drawings."""
from __future__ import annotations

import pathlib

import harness_model as M
import harness_draw as D

OUT = pathlib.Path(__file__).resolve().parents[1] / "brass-harness-step-by-step-full.html"
TEMPLATE_SVG = pathlib.Path(__file__).resolve().parents[1] / "harness-floor-letter.svg"

# ---------------------------------------------------------------- product links (INVENTORY.md first, then MATERIALS.md)
L = {
    "rod": ("https://www.amazon.com/dp/B005WPB7YG", "K&S #9861 1.0 mm rod"),
    "tube": ("https://www.amazon.com/dp/B005WPAW9M", "K&S #9831 tube"),
    "card": ("https://www.amazon.com/dp/B0DSH5V1TT", "Amazon Basics cardstock"),
    "kapton": ("https://www.amazon.com/dp/B072Z92QZ2", "ELEGOO Kapton tape"),
    "shrink": ("https://www.amazon.com/dp/B08N4W4K9X", "Pointool heat-shrink"),
    "pliers": ("https://www.amazon.com/dp/B0B8QBVXXR", "WORKPRO pliers"),
    "cutters": ("https://www.amazon.com/dp/B07C5PM8L4", "BOENFU flush cutters"),
    "sand": ("https://www.amazon.com/dp/B07D2YYC11", "BAISDY 400 grit"),
    "flux": ("https://www.adafruit.com/product/3468", "Chip Quik CQ4LF pen"),
    "solder": ("https://www.amazon.com/dp/B076QF1Y85", "MAIYUM 63/37 solder"),
    "wick": ("https://www.amazon.com/dp/B0DRN688Q5", "JoTownCand solder wick"),
    "meter": ("https://www.amazon.com/dp/B08BL288LW", "KAIWEETS multimeter"),
    "caliper": ("https://www.amazon.com/dp/B000GSLKIW", "NEIKO caliper"),
    "ipa": ("https://www.amazon.com/dp/B0BSJ93RKB", "91 % isopropyl alcohol"),
    "a1": ("https://www.amazon.com/dp/B0F888JQ91", "Meshnology ESP32-C3 SuperMini"),
    "screen": ("https://www.amazon.com/dp/B09T6SJBV5", "Hosyond SSD1306 OLED"),
    "mic": ("https://www.amazon.com/dp/B092HWW4RS", "AITRIP INMP441"),
    "amp": ("https://www.amazon.com/dp/B0CDWXZZCH", "MAX98357A amplifier"),
    "button": ("https://www.amazon.com/dp/B0FHW6HMG4", "QTEATAK tactile buttons"),
    "speaker": ("https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309", "Same Sky CES-20134-088PM"),
    "res": ("https://www.amazon.com/dp/B0F4P352BB", "LuminologyPro resistor kit"),
    "ns14": ("https://www.amazon.com/dp/B0BSTSMLF7", "CRAFT WIRE 14 ga nickel silver"),
    "ns18": ("https://www.amazon.com/dp/B0BSTSMLF7", "CRAFT WIRE 18 ga nickel silver (same listing, 18 ga)"),
    "ns20": ("https://www.amazon.com/dp/B0BSTSMLF7", "CRAFT WIRE 20 ga nickel silver (same listing, 20 ga)"),
    "powerboost_owned": ("https://www.amazon.com/dp/B0G5PXGVG9", "PowerBoost 1000C copy (Amazon #20)"),
    "cap220": ("https://www.amazon.com/dp/B0C1VBXCQM", "ALLECIN electrolytic kit"),
    "cap100n": ("https://www.amazon.com/dp/B07P7HRGT9", "BOJACK ceramic kit"),
    "paint": ("https://www.amazon.com/dp/B000PIG3AS", "Rust-Oleum gloss white"),
    "harness-day": ("https://claude.ai/artifact/1Dj7UUzzfYgGRhe21xgUWq", "Harness Day"),
    "brass-wiring": ("https://claude.ai/artifact/8szP1YnS34Z8w7FkqujRKb", "Brass Wiring"),
    "pip-map": ("https://claude.ai/artifact/Tww4L4pJtn7XGBg2jBqvHk", "Pip Wiring Map"),
    "frame-soldering": ("https://claude.ai/artifact/MxppvtEBfmPhyNVasXHQGd", "Frame Soldering"),
}


def a(key, text=None):
    url, name = L[key]
    return f'<a href="{url}" target="_blank" rel="noopener">{text or name}</a>'


# no listing recorded for: heat gun (QWORK), X-Tronic station / helping hands / tweezers / mat, 900M-T tips, hot glue


def fig(svg, caption):
    return f'<figure><div class="scroll">{svg}</div><figcaption>{caption}</figcaption></figure>'


def step(sid, do, check=None, note=None, pre=None):
    out = [f'<div class="step"><input type="checkbox" id="{sid}"><label for="{sid}"><span class="do">{do}</span>']
    if pre:
        out.append(f'<pre>{pre}</pre>')
    if check:
        out.append(f'<span class="chk">{check}</span>')
    if note:
        out.append(f'<span class="note">{note}</span>')
    out.append('</label></div>')
    return "".join(out)


def rod_card(name, sid, do, check, joints, sleeve_note=None, extra_caption="", simple=False):
    """A build step for one rod: unrolled side view, top-view highlight, bend table, joints, check."""
    c = next(r for r in M.rods() + M.small_parts() if r.name == name)
    if simple:
        sl = f'<span class="note"><strong>Sleeve:</strong> {sleeve_note}</span>' if sleeve_note else ""
        body = (f'<div class="step"><input type="checkbox" id="{sid}"><label for="{sid}"><span class="do">{do}</span>'
                f'<span class="note"><strong>Cut 3 mm</strong> of {a("rod", "1.0 mm rod")}, bare all over.</span>'
                f'<span class="note"><strong>Joints:</strong> {joints}</span>{sl}<span class="chk">{check}</span></label></div>')
        return body + f'<details class="more"><summary>Drawing for the {c.name}</summary>' + fig(D.map_figure(highlight={name}, title=f"{c.name} in the top view"), f'<strong>Where it stands.</strong> {extra_caption}') + '</details>'
    rows = D.bend_table(c)
    table = ['<div class="scrollx"><table class="t bends"><tr><th>Piece</th><th>mm</th><th>Direction</th><th>Ends at height</th></tr>']
    for i, L_, dirn, z in rows:
        table.append(f'<tr><td class="n">{i}</td><td class="n">{L_}</td><td>{dirn}</td><td class="n">{z}</td></tr>')
    table.append('</table></div>')
    sl = f'<span class="note"><strong>Sleeve:</strong> {sleeve_note}</span>' if sleeve_note else ""
    body = (
        f'<div class="step"><input type="checkbox" id="{sid}"><label for="{sid}">'
        f'<span class="do">{do}</span>'
        f'<span class="note"><strong>Cut {c.length() + 6:.0f} mm</strong> of {a("rod", "1.0 mm rod")}, finished {c.length():.0f} mm, {len(rows) - 1} bend{"s" if len(rows) != 2 else ""}. '
        f'Sand 3 mm bare at each joint before bending.</span>'
        f'<span class="note"><strong>Joints:</strong> {joints}</span>{sl}'
        f'<span class="chk">{check}</span></label></div>'
    )
    figs = (f'<details class="more"><summary>Drawing, bends and lengths for the {c.name}</summary>'
            f'{"".join(table)}'
            + fig(D.unrolled(c), f'<strong>{c.name}, unrolled.</strong> Read it left to right from the first joint: each straight piece with its length, each corner a bend. {extra_caption}')
            + fig(D.map_figure(highlight={name}, title=f"{c.name} in the top view"), f'<strong>Where it lies.</strong> The bold line is this rod; the two rings are its end joints. Everything else is faded.')
            + '</details>')
    return body + figs


def main():
    conds = M.all_conductors()
    rep = M.check(conds)
    tight = [r for r in rep if r[3] in ("tight", "sleeve")]
    fails = [r for r in rep if r[3] in ("FAIL", "OVERLAP", "BOX")]
    assert not fails, fails
    rods = M.rods()
    total_rod = sum(c.length() + 6 for c in rods)

    H = []
    H.append('''<title>Brass Harness Step by Step</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root { --w-red: #D1293D; --w-black: #2A2F35; --w-yellow: #D99A00; --w-green: #23914A; --w-blue: #2C6BD4; --w-white: #8E99A4; --w-orange: #E0661C; --w-olive: #6B8E23; --w-purple: #7C3AED; --w-teal: #0B7285; --w-navy: #1B3F8B; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --w-red: #FF6170; --w-black: #C4CBD2; --w-yellow: #F5C24A; --w-green: #5BD48A; --w-blue: #6FA3FF; --w-white: #EEF2F5; --w-orange: #FF9A5C; --w-olive: #B5D46A; --w-purple: #C4A5FF; --w-teal: #4FC3D1; --w-navy: #7FA8FF; } }
  :root[data-theme="dark"] { --w-red: #FF6170; --w-black: #C4CBD2; --w-yellow: #F5C24A; --w-green: #5BD48A; --w-blue: #6FA3FF; --w-white: #EEF2F5; --w-orange: #FF9A5C; --w-olive: #B5D46A; --w-purple: #C4A5FF; --w-teal: #4FC3D1; --w-navy: #7FA8FF; }
  :root {
    --bg: #F3F5F7; --surface: #FFFFFF; --ink: #16202A; --muted: #5B6B7A; --line: #D3DAE1;
    --accent: #0B7285; --accent-ink: #085B6B; --accent-tint: #E1F2F5;
    --brass: #A07A1C; --brass-tint: #F6ECD2;
    --warn: #9A5B00; --warn-tint: #FFF3DB; --pass: #1E7B3E; --pass-tint: #E4F4E9;
    --code-bg: #EAEFF3; --figure-bg: #FAFBFC;
    --sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #0F1519; --surface: #161E24; --ink: #E4EAEF; --muted: #98A7B4; --line: #2A363F;
      --accent: #4FC3D1; --accent-ink: #7AD6E1; --accent-tint: #10292F;
      --brass: #E2B84E; --brass-tint: #2C2412;
      --warn: #F0B14A; --warn-tint: #2C2310; --pass: #5FCB7E; --pass-tint: #112A1A;
      --code-bg: #0B1014; --figure-bg: #121A1F; color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --bg: #0F1519; --surface: #161E24; --ink: #E4EAEF; --muted: #98A7B4; --line: #2A363F;
    --accent: #4FC3D1; --accent-ink: #7AD6E1; --accent-tint: #10292F;
    --brass: #E2B84E; --brass-tint: #2C2412;
    --warn: #F0B14A; --warn-tint: #2C2310; --pass: #5FCB7E; --pass-tint: #112A1A;
    --code-bg: #0B1014; --figure-bg: #121A1F; color-scheme: dark;
  }
  body { background: var(--bg); color: var(--ink); font-family: var(--sans); font-size: 15.5px; line-height: 1.5; -webkit-font-smoothing: antialiased; }
  .wrap { max-width: 840px; margin: 0 auto; padding-block: 28px 64px; padding-inline: 20px; }
  .eyebrow { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
  h1 { font-size: clamp(26px, 5vw, 34px); margin: 2px 0 6px; letter-spacing: -.01em; }
  .lede { color: var(--muted); max-width: 66ch; margin: 0 0 18px; }
  h2 { font-size: 22px; margin: 44px 0 8px; letter-spacing: -.01em; }
  h2 .when { font-family: var(--mono); font-weight: 500; color: var(--muted); font-size: .72em; margin-right: 8px; }
  h3 { font-size: 17px; margin: 26px 0 6px; }
  p { max-width: 70ch; margin: 0 0 10px; }
  ul, ol { max-width: 70ch; padding-left: 1.25em; margin: 0 0 12px; }
  li { margin-bottom: 4px; }
  code { font-family: var(--mono); font-size: .9em; background: var(--code-bg); padding: .1em .35em; border-radius: 4px; }
  pre { font-family: var(--mono); font-size: 13.5px; background: var(--code-bg); border: 1px solid var(--line); border-radius: 6px; padding: 10px 12px; overflow-x: auto; white-space: pre; margin: 8px 0 12px; }
  a { color: var(--accent-ink); }
  .step { display: grid; grid-template-columns: 26px 1fr; gap: 12px; align-items: start; padding: 10px 0; border-top: 1px solid var(--line); }
  .step input { width: 20px; height: 20px; margin-top: 3px; accent-color: var(--pass); cursor: pointer; }
  .step label { cursor: pointer; }
  .step .do { font-weight: 600; }
  .step .chk { display: block; color: var(--accent-ink); font-size: 14px; margin-top: 4px; }
  .step .chk::before { content: "check · "; font-weight: 600; letter-spacing: .04em; text-transform: uppercase; font-size: 11.5px; }
  .step .note { display: block; color: var(--muted); font-size: 14px; margin-top: 3px; }
  .callout { border-left: 3px solid var(--warn); background: var(--warn-tint); padding: 10px 14px; margin: 14px 0; max-width: 74ch; border-radius: 0 6px 6px 0; }
  .callout.info { border-left-color: var(--accent); background: var(--accent-tint); }
  .callout.pass { border-left-color: var(--pass); background: var(--pass-tint); }
  .callout .label { display: block; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; color: var(--warn); }
  .callout.info .label { color: var(--accent-ink); } .callout.pass .label { color: var(--pass); }
  .callout ul, .callout p { margin: 0; } .callout ul { padding-left: 1.2em; }
  .stock { display: inline-block; font-size: 14px; background: var(--brass-tint); border: 1px solid var(--brass); border-radius: 6px; padding: 5px 10px; margin: 0 0 10px; }
  .stock strong { color: var(--brass); }
  table.t { width: 100%; border-collapse: collapse; font-size: 14px; margin: 6px 0 12px; }
  table.t th, table.t td { text-align: left; padding: 6px 8px; border-top: 1px solid var(--line); vertical-align: top; }
  table.t th { font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); font-weight: 600; border-top: none; }
  table.t td.n { font-family: var(--mono); white-space: nowrap; }
  table.bends { max-width: 420px; margin-top: 4px; }
  .scrollx { overflow-x: auto; }
  .progress { position: sticky; top: env(safe-area-inset-top, 0px); background: var(--bg); padding: 8px 0; font-family: var(--mono); font-size: 13px; color: var(--muted); border-bottom: 1px solid var(--line); margin-bottom: 8px; z-index: 1; }
  .progress b { color: var(--pass); }
  button.reset { font: inherit; font-size: 13px; padding: 4px 10px; border-radius: 6px; border: 1px solid var(--line); background: var(--surface); color: var(--muted); cursor: pointer; margin-left: 10px; }
  .evidence { margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 14px; color: var(--muted); max-width: 74ch; }
  figure { margin: 12px 0 16px; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px 8px; }
  figure .scroll { overflow-x: auto; }
  figure svg { display: block; width: 100%; min-width: 600px; height: auto; color: var(--ink); font-family: var(--sans); background: var(--figure-bg); }
  figure svg text { fill: currentColor; }
  figure svg .t { font-size: 13px; } figure svg .s { font-size: 11.5px; } figure svg .b { font-weight: 600; } figure svg .m { font-family: var(--mono); }
  figure svg .pin { font-size: 8.5px; font-family: var(--mono); fill: var(--muted); paint-order: stroke; stroke: var(--figure-bg); stroke-width: 3px; stroke-linejoin: round; }
  figure svg .muted { fill: var(--muted); } figure svg .acc-ink { fill: var(--accent-ink); } figure svg .warn-ink { fill: var(--warn); } figure svg .pass-ink { fill: var(--pass); } figure svg .brass-ink { fill: var(--brass); }
  figure svg .pcb { fill: var(--code-bg); stroke: var(--line); stroke-width: 1; } figure svg .pcb.dim { opacity: .6; }
  figure svg .box { fill: var(--surface); stroke: currentColor; stroke-width: 1.2; }
  figure svg .kapton { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1; }
  figure svg .ant { fill: none; stroke: var(--warn); stroke-width: 1.2; stroke-dasharray: 3 2; }
  figure svg .kap { fill: var(--warn); fill-opacity: .28; stroke: var(--warn); stroke-width: 1.4; }
  figure svg .kap2 { fill: var(--warn); fill-opacity: .55; stroke: var(--warn); stroke-width: 1.4; }
  figure svg .num { fill: var(--warn); stroke: var(--figure-bg); stroke-width: 1.5; } figure svg .numt { fill: #fff; }
  figure svg .shim { fill: none; stroke: var(--muted); stroke-width: 1.2; stroke-dasharray: 3 3; }
  figure svg .tube { fill: var(--brass-tint); stroke: var(--brass); stroke-width: 1.4; }
  figure svg .card { fill: var(--surface); stroke: var(--muted); stroke-width: 1.2; }
  figure svg .glue { fill: var(--pass); stroke: var(--figure-bg); stroke-width: 1.5; }
  figure svg .rodx { fill: var(--brass-tint); stroke: var(--brass); stroke-width: 2; }
  figure svg .tapeline { fill: none; stroke: var(--warn); stroke-width: 3; opacity: .7; }
  figure svg .spk { fill: var(--warn-tint); stroke: var(--warn); stroke-width: 1.2; }
  figure svg .cap { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.2; }
  figure svg .port { fill: var(--surface); stroke: currentColor; stroke-width: 1.2; }
  figure svg .stubp { fill: var(--brass); stroke: none; }
  figure svg .screen-out { fill: none; stroke: var(--accent); stroke-width: 2; stroke-dasharray: 6 4; }
  figure svg .screen-side { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.2; }
  figure svg .glass { fill: var(--accent); opacity: .35; }
  figure svg .frame { fill: none; stroke: var(--brass); stroke-width: 5; } figure svg .post { fill: var(--brass); }
  figure svg .joint { fill: var(--surface); stroke: var(--pass); stroke-width: 2.2; }
  figure svg .floor { stroke: currentColor; stroke-width: 2; }
  figure svg .grid { stroke: var(--line); stroke-width: 1; fill: none; } figure svg .dashed { stroke-dasharray: 4 4; }
  figure svg .edge { stroke: currentColor; stroke-width: 1.2; fill: none; }
  figure svg .warn-line { stroke: var(--warn); fill: none; } figure svg .acc { stroke: var(--accent); fill: none; } figure svg .pass-line { stroke: var(--pass); fill: none; }
  figure svg .rod { stroke: var(--brass); stroke-width: 4; fill: none; stroke-linecap: round; stroke-linejoin: round; }
  figure svg .solder { fill: var(--muted); }
  figure svg .sleeve { fill: var(--surface); stroke: currentColor; stroke-width: 1.4; }
  figcaption { font-size: 13.5px; color: var(--muted); margin-top: 8px; max-width: 74ch; }
  figcaption strong { color: var(--ink); }
  .legend { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 4px 14px; font-size: 13.5px; margin: 8px 0 14px; }
  .legend span.sw { display: inline-block; width: 22px; height: 5px; border-radius: 3px; vertical-align: middle; margin-right: 7px; }
  details.more { margin: 2px 0 8px 38px; } details.more > summary { cursor: pointer; color: var(--accent-ink); font-size: 14px; }
  details.more[open] > summary { margin-bottom: 6px; }
  .short ol { counter-reset: s; padding-left: 0; list-style: none; max-width: 76ch; }
  .short li { counter-increment: s; display: grid; grid-template-columns: 30px 1fr; gap: 8px; padding: 6px 0; border-top: 1px solid var(--line); }
  .short li::before { content: counter(s); font-family: var(--mono); font-weight: 600; color: var(--brass); }
  .short li a { font-weight: 600; }
  .short .c { display: block; color: var(--muted); font-size: 14px; }
  .gate { display: grid; grid-template-columns: 24px 1fr; gap: 12px; background: var(--pass-tint); border: 1px solid color-mix(in srgb, var(--pass) 35%, transparent); border-radius: 8px; padding: 12px 14px; margin: 16px 0; max-width: 74ch; }
  .gate input { width: 20px; height: 20px; margin-top: 2px; accent-color: var(--pass); }
  .gate .name { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; font-weight: 700; color: var(--pass); }
  .gate p { margin: 2px 0 0; }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
</style>
''')
    H.append('<div class="wrap">')
    H.append('<div class="eyebrow">Pocket AI Assistant · step 4d · the brass harness, rod by rod</div>')
    H.append('<h1>Brass harness, step by step</h1>')
    H.append(f'<p class="lede">{len(rods)} rods, 2 resistors, 2 capacitors, 5 modules, one 57 × 39 mm card. Every rod below was placed in three dimensions against your 28 September part sizes and checked by computer: no two different signals come within 1 mm of each other without a sleeve, nothing comes within 2 mm of the frame, and nothing sits over the antenna. Each rod gets its own drawing, its cut length, its bends and its meter check. Tick as you go; the page remembers in this browser.</p>')
    H.append('<div class="progress"><span id="done">0</span> of <span id="total">0</span> steps done <button class="reset" id="reset">clear</button></div>')

    # ------------------------------------------------------------ the minimum
    H.append('<div class="short"><h2 id="short" style="margin-top:24px">The minimum</h2>'
             '<p>Twelve moves, nothing optional in them. Everything further down the page is detail: open it when a move confuses you, otherwise ignore it.</p><ol>'
             '<li><div><a href="#secA">Trim every module to 2 mm stubs</a>, sand them bright.</div></li>'
             '<li><div><a href="#secA">Floor card</a>: print the template at Actual size, glue it to cardstock, cut 57 × 39. Tape the five parts onto their outlines with any tape. <strong>Two pieces of Kapton</strong>: over the USB socket\'s roof, and a strip on the amp between its stubs and its chip. <span class="c">Mic chip-side down, hole up. That is all the tape that matters.</span></div></li>'
             '<li><div><a href="#secB">Two rails</a>, bare, on their lines: 3V3 at x = 24, GND at x = 27. A bit of tape at each end.</div></li>'
             '<li><div><a href="#secC">Six channel rods</a>: 5 V, GND (plus its 3 mm pin to the rail), the 3V3 tap, DIN, BCLK, WS. <span class="c">One sleeve: on the 5 V rod. Then the meter: GND rail to 3V3 rail silent, each rod only to its own ends.</span></div></li>'
             '<li><div><a href="#secD">Four fly-overs</a>: mic SD, amp SD, SCL, SDA. <span class="c">One sleeve: on SCL. Then the meter again.</span></div></li>'
             '<li><div><a href="#secE">Screen</a> on a 12.5 mm block: solder SCL and SDA to it, add its two power taps, pull the block.</div></li>'
             '<li><div><a href="#secE">Button</a> on the socket\'s Kapton, two rods.</div></li>'
             '<li><div><a href="#secE">Mic</a>: GND tap, VDD tap, L/R link.</div></li>'
             '<li><div><a href="#secF">Two resistors</a>, measured first (GAIN and the mic-SD pull-down were dropped 2026-10-14).</div></li>'
             '<li><div><a href="#secF">Two capacitors</a> (sleeve the 220 µF\'s two leads, they run side by side) and the speaker leads into the block.</div></li>'
             '<li><div><a href="#secG">Sweep, then power</a>: GND rail to 3V3 rail, to 5 V, to OUT+ and OUT−, all silent. USB in: eyes, button, mic, then the speaker build, two cold starts.</div></li>'
             '<li><div><a href="#secG">Frame</a>: Kapton on the inside of the tubes, lower the card in, six dots of glue.</div></li>'
             '</ol>'
             '<p><strong>The three rules that are not optional:</strong> USB unplugged whenever the iron is on · OUT+ and OUT− never touch GND, a rail or the frame · the frame touches no rod and no rail. Everything else on this page is there to save you a redo, not to keep you safe.</p></div>')

    # ------------------------------------------------------------ the two days
    H.append('<div class="callout" id="plan"><span class="label">The plan: two sessions</span>'
             '<p><strong>Day 1 — moves 1 to 5, about 4½ hours.</strong> Stubs, floor card, rails, the six channel rods, the four fly-overs. '
             'You stop with every rod in the channel metering clean and nothing powered: a safe place to leave it. '
             f'On the bench before you start: the five modules, the {a("rod", "1.0 mm rod")}, {a("cutters", "flush cutters")}, {a("pliers", "chain-nose pliers")}, {a("sand", "400 grit")}, '
             f'{a("caliper", "calipers")}, {a("card", "cardstock")} and the printed floor template, {a("kapton", "Kapton")}, {a("flux", "Chip Quik pen")}, {a("solder", "63/37 solder")}, '
             f'the electronics tip, {a("shrink", "heat-shrink")} (thinnest size) and the heat gun, the {a("meter", "meter")}, helping hands, a white sheet of paper. '
             'The brass-frame kit and the Harris flux stay in their box. USB stays unplugged all day.</p>'
             '<p><strong>Day 2 — moves 6 to 12, about 4 hours.</strong> Screen, button, mic taps, the small parts, the tests, the frame. Add the resistors (measured), both capacitors, the speaker, the hot glue gun, and the frame with Kapton on its tubes.</p>'
             '<p><strong>At the end of Day 1</strong>, send two photos (from above and from the front) and the result of the meter sweep: GND rail to 3V3 rail, and each of the ten rods to both rails. I check them against the drawings before Day 2 starts.</p></div>')

    # ------------------------------------------------------------ words
    H.append('<div class="callout pass"><span class="label">Words on this page</span><ul>'
             '<li><strong>Channel</strong>: the empty 8.5 mm strip between A1 and the amp, front to back (x = 21.5 to 30 on the map). The two rails lie in it; the straight rods cross it; the mic sits at its back end.</li>'
             '<li><strong>Stub</strong>: a header pin clipped to 2 mm. Every joint is a rod soldered beside a stub.</li>'
             '<li><strong>Rail</strong>: one of the two long bare rods on the card, GND and 3V3. A <strong>tap</strong> is a short rod from a stub down onto a rail.</li>'
             '<li><strong>Fly-over</strong>: a rod that leaves stub height and crosses above other rods, at 5.5, 7.5 or 9.5 mm.</li>'
             '<li><strong>x, y, height</strong>: millimetres from the left wall, from the front wall, and up from the card.</li>'
             '</ul></div>')

    # ------------------------------------------------------------ what changed
    H.append('<div class="callout info"><span class="label">What is different from the earlier pages</span><ul>'
             f'<li>The <strong>mic lies flat, pins up, hole up</strong>, at the back of the channel. Its six stubs then stand like a tiny breadboard, and its three power taps are 5–10 mm long instead of 30.</li>'
             f'<li>The <strong>screen floats 12.5 mm up on its four rods</strong>, header edge at the front, and overhangs the channel. The I²C rods reach its stubs without crossing the amp.</li>'
             f'<li>The <strong>button sits on the USB socket</strong> (two layers of {a("kapton", "Kapton")} under it), 5 mm from GPIO5 and 9 mm from GND. No rod runs along the left wall.</li>'
             f'<li>The <strong>220 µF lies in the right-hand strip</strong>, leads along the floor in heat-shrink. On the amp there is no room for it under the screen.</li>'
             f'<li>Rails sit <strong>on the card</strong>, not 2 mm up, so the straight rods cross 1.5 mm above them. The old sketch had them touching.</li>'
             f'<li>A1 and the amp both moved back 1 mm so the rails can turn up at the front; A1 sits on one layer of {a("card", "cardstock")} so the USB plug body clears the front tube.</li>'
             '</ul></div>')

    # ------------------------------------------------------------ checks before cutting
    H.append('<h2><span class="when">0:00</span>Four things to confirm before any rod is cut</h2>')
    H.append('<p><strong>All four were confirmed on 10 October</strong>, so the drawings are final; the fifth (the capacitor\'s size) is a caliper check when you get to step F6.</p>')
    H.append('<details class="more" style="margin-left:0"><summary>The four checks and what you answered</summary>')
    H.append(step("c1", f"Frame inside height: measure from the top of the bottom tube to the underside of the top tube with the {a('caliper', 'calipers')}.",
                  f"Confirmed 10 October: about 32 mm. The design needs {M.FRAME_H_MIN:g} (the screen's glass ends 15.5 mm up), so there is 15 mm to spare and nothing changes.",
                  "The spare height is above the screen; it is yours for later (a taller button, a lid), not something the harness needs."))
    H.append(step("c2", f"Amp: where is the speaker terminal block? The {a('amp')} is drawn with its 7 pins on its left edge, facing A1 across the channel, and the block on the opposite edge, toward the right wall.",
                  "Confirmed 10 October: the block is on the edge opposite the pins. With the pins facing the channel it points at the right wall, as drawn; nothing changes."))
    H.append(step("c3", f"Screen: read the four labels on your {a('screen')}. With the header edge toward you and the glass up, the drawings read SDA · SCL · VCC · GND left to right.",
                  "Confirmed 10 October: you read SDA · SCL · VCC · GND with the pins at the bottom. The drawings match; nothing to change.",
                  "SDA and SCL are the two left stubs either way."))
    H.append(step("c4", f"Mic: read the six labels on your {a('mic')}. Three on one side, three on the other. The drawings have SD · VDD · GND on one side and L/R · WS · SCK on the other, with L/R facing GND and SCK facing SD.",
                  "Confirmed 10 October: SD · VDD · GND on one side, L/R · WS · SCK on the other, L/R facing GND. Exactly as drawn; the L/R link is one straight piece.",
                  "If the labels are only printed on the chip side, write them on a sticky note before you flip the module."))
    H.append(step("c5", f"220 µF: caliper the capacitor from the {a('cap220')}.",
                  "Diameter ≤ 6.5 mm, length ≤ 12.5 mm lying down. A fatter one still fits lying along the right strip; tell me the size."))

    H.append('</details>')

    # ------------------------------------------------------------ the compatibility check
    H.append('<h2>What was checked, with the numbers</h2>')
    H.append('<p>Floor, heights, pitch alignment, every pair of conductors, the frame, the USB plug, the mic port, the speaker and the rod stock, each with a number. Reference, not steps.</p>')
    H.append('<details class="more" style="margin-left:0"><summary>The checks table and the tight-spot list</summary>')
    H.append('<div class="scrollx"><table class="t"><tr><th>Check</th><th>Number</th><th>Result</th></tr>')
    rowsck = [
        ("Floor, left to right", "A1 18 + channel 8.5 + amp 17 + right strip 10 + margins 3.5 = 57", "fits; the 220 µF (6.3) and the terminal block (3 mm proud) share the right strip"),
        ("Floor, front to back", "A1 22 + antenna keep-out 14.5 behind it; amp 17 + lane 4.3 + mic Ø13 = 34.3 of 39", "fits; the round mic ends 1 mm from the back"),
        ("Antenna", "nearest rod to the ceramic antenna: SDA's stub exit, 3.8 mm; nothing behind A1 at all", "ok"),
        ("Height", "screen glass top 15.5; 220 µF 6.3; button plunger 10.1; mic stubs 4.6", f"needs ≥ {M.FRAME_H_MIN:g} inside; your frame measures about 32"),
        ("Straight rods", "A1's right row and the amp's row are both 2.54 mm pitch; amp front edge 1.2 mm behind A1's", "5 V, GND, DIN, BCLK, WS are straight, 9.9 mm stub to stub"),
        ("Rails vs crossing rods", "rails on the card (centre 0.5 up), straight rods at 3.0", "1.5 mm air at every crossing; the 5 V rod sleeved anyway"),
        ("Every pair of different nets", f"{len(conds)} conductors, {len(conds) * (len(conds) - 1) // 2} pairs measured", f"none under 1.0 mm bare; {len([t for t in tight if t[3] == 'tight'])} between 1.0 and 1.5, listed below"),
        ("Frame", "every rod ≥ 2.0 mm from the four inner faces; the 220 µF leads 2.0 from the front", "ok with Kapton on the tubes"),
        ("USB plug", "socket face 0.8 mm behind the front; plug body 6.5 tall centred 3.5 up with A1 on a 0.3 shim", "clears the bottom tube by 0.5"),
        ("Mic port", "no rod within 2.5 mm of the hole above the board", "ok"),
        ("Speaker", "20 × 13 in the back-right corner, 0.5 mm from the mic's edge, flush with the right face", "fits; its leads reach the block (15 mm)"),
        ("Rod stock", f"{total_rod:.0f} mm of rod cut lengths, 2 rails bare", "1.1 of your 10 sticks; use an unpainted one for the rails if you have it"),
    ]
    for ck, num, res in rowsck:
        H.append(f'<tr><td>{ck}</td><td>{num}</td><td>{res}</td></tr>')
    H.append('</table></div>')
    H.append('<h3>The tight spots, and the sleeve that covers each</h3>')
    H.append('<p>Every pair below is between 1.0 and 1.5 mm apart on the drawing. Hands are not that precise, so each one gets a piece of heat-shrink on the rod named first. The per-rod steps repeat this where it applies.</p>')
    H.append('<div class="scrollx"><table class="t"><tr><th>Pair</th><th>Gap</th><th>Where (x, y, height)</th><th>Cover</th></tr>')
    covers = {
        ("SCL rod", "SDA rod"): "SCL sleeved along the left lane and across A1",
        ("SCL rod", "button rod"): "SCL's sleeve (already on)",
        ("amp SD rod", "button rod"): "the button rod's short sleeve",
        ("mic SD rod", "SCL rod"): "SCL's sleeve",
        ("SCL rod", "screen VCC tap"): "the VCC tap's sleeve",
        ("5 V rod", "screen VCC tap"): "the 5 V rod's sleeve",
        ("screen GND tap", "220u lead +"): "the capacitor lead's sleeve",
        ("3V3 tap", "amp SD rod"): "none needed: the tap ends 2 mm short; keep its hook tight",
        ("amp SD rod", "button GND rod"): "none needed; keep the button rod low",
        ("mic VDD tap", "L/R link"): "none needed; VDD rises straight up first",
        ("BCLK rod", "WS rod"): "none needed; 2.2 mm apart sideways",
    }
    seen = set()
    for gap, an, bn, flag, where in tight:
        if (an, bn) in seen:
            continue
        seen.add((an, bn))
        if gap >= 1.5:
            continue
        cov = covers.get((an, bn)) or covers.get((bn, an)) or "none needed"
        H.append(f'<tr><td>{an} × {bn}</td><td class="n">{gap:.1f} mm</td><td class="n">{where}</td><td>{cov}</td></tr>')
    H.append('</table></div>')

    H.append('</details>')

    # ------------------------------------------------------------ the layout
    H.append('<h2>The layout, to scale</h2>')
    H.append(fig(D.map_figure(title="Every rod, top view, 10 px = 1 mm"),
                 '<strong>The map.</strong> Front (USB) at the bottom. Dots are 2 mm stubs. Dotted stretches are heat-shrink. The dashed square is the screen, which floats above everything on its four rods. Colours name the signal; every rod is brass.'))
    H.append('<div class="legend">' + "".join(
        f'<div><span class="sw" style="background:{D.NET_COLOR[n]}"></span>{D.NET_LABEL[n]}</div>' for n in ["5V", "GND", "3V3", "GPIO1", "GPIO2", "GPIO3", "GPIO4", "AMPSD", "GPIO10", "GPIO20", "GPIO21"]) + '</div>')
    H.append(fig(D.front_elevation(), '<strong>Heights.</strong> Five levels: rails on the card, straight rods at 3 mm beside the stubs, then fly-overs at 5.5, 7.5 and 9.5 mm, and the screen at 12.5. A rod that has to cross another one does it on a different level, 2 mm apart.'))
    H.append(fig(D.side_elevation(), '<strong>From the right side.</strong> The channel runs the whole depth. The mic\'s stubs stand at the back; the screen\'s stubs hang at the front; the 220 µF lies low at the front right.'))

    # ------------------------------------------------------------ how each module is prepared
    H.append('<h2>How each module is prepared</h2>')
    H.append('<ul>'
             f'<li><strong>A1</strong> ({a("a1")}): pins clipped to 2 mm stubs on both rows, USB at the front, on one layer of {a("card", "cardstock")}. Two layers of {a("kapton", "Kapton")} on the USB socket\'s shell; the button sits on that.</li>'
             f'<li><strong>Amp</strong> ({a("amp")}): stubs, pin row facing the channel, VIN at the front. A strip of Kapton on the board between the stubs and the chip, where R1, R2 and the 100 nF lie.</li>'
             f'<li><strong>Mic</strong> ({a("mic")}): the round Ø13 board. Stubs, then <strong>turned over</strong>: chip side down on a Kapton pad, stubs and hole up. Turn it like a dial until the SD-VDD-GND row faces the channel; the two rows are 7.6 mm apart, which the calipers can confirm.</li>'
             f'<li><strong>Screen</strong> ({a("screen")}): stubs pointing down from the back, glass up, header edge at the front. It is held 12.5 mm up by a block while its four rods are soldered, then the block comes out.</li>'
             f'<li><strong>Button</strong> ({a("button")}): legs clipped to 1 mm, sticking out sideways. Meter the two legs on each side first: each side is one contact.</li>'
             f'<li><strong>Speaker</strong> ({a("speaker")}): untouched. Its own leads go into the terminal block last.</li>'
             '</ul>')

    # ------------------------------------------------------------ Phase A
    H.append('<h2 id="secA"><span class="when">0:20</span>A · Prepare</h2>')
    H.append(f'<p class="stock">Use: {a("pliers", "chain-nose pliers")} · {a("cutters", "flush cutters")} · {a("sand", "400 grit")} · {a("caliper", "calipers")} · {a("kapton", "Kapton")} · {a("card", "cardstock")} · white paper to work over</p>')
    H.append('<div class="callout pass"><span class="label">Already done on 10 October</span><p>The firmware was flashed to the board on USB and proved on its own: Wi-Fi joined under the 8.5 dBm cap, <code>got ip</code>, <code>hello accepted</code>, server link up in 5.6 s. The screen and the button get their check at step G2, on the harness.</p></div>')
    H.append(step("a2", f"Trim every module to 2 mm stubs: grip the black plastic strip with the {a('pliers', 'chain-nose pliers')}, rock it off, clip each pin 2 mm above the board with the {a('cutters', 'flush cutters')}. A1 both rows, amp, mic, screen; button legs to 1 mm. Then sand every stub bright with a corner of {a('sand', '400 grit')}, dust blown away from the mic, and a scrap of {a('kapton', 'Kapton')} over its hole.",
                  f"No stub under 1.5 or over 2.5 mm with the {a('caliper', 'calipers')}; a 1 mm one on A1 or the amp gets a splint. Stubs shiny, not grey."))
    H.append(step("a4", f"The floor: print <code>harness-floor-letter.pdf</code> at Actual size (black, Letter), check the 50 mm bar, glue it to {a('card', 'cardstock')} and cut on the outer line: 57 × 39 mm. Trim 0.5 mm all round so it drops into the frame later.",
                  "The 50 mm bar measures 50 mm. Every part outline and every stub dot is on the card."))
    H.append(fig(D.svg_wrap(
        D.frame_top() + D.parts_top() + D.screen_outline() + "".join(D.poly_top(c, width=5) for c in rods[:2]) + D.part_labels() + D.text(D.OX, 22, "The floor card: part outlines, stub dots and the two rails", "t b"),
        760, int(D.OY + M.INSIDE_Y * D.S + 40), "floor card"),
        '<strong>Lay the parts on their outlines.</strong> The printed card has the same drawing at 1:1. Each dot is where a stub stands; the two thick lines are the rails.'))
    H.append(step("a5", f"Two pieces of {a('kapton', 'Kapton')} that matter: over the roof of the USB socket (two layers; the button sits there and the shell is GND), and a strip on the amp board between its stubs and its chip (bare leads hover over it). Optional, skip freely: a 0.3 mm {a('card', 'cardstock')} shim under A1 (only if the USB plug rubs the front tube at the test), pads under the mic and the 220 µF, a scrap over the mic hole.",
                  "The button's legs can't reach the socket's metal. That's the only thing this step has to achieve."))
    H.append(fig(D.kapton_figure(),
                 '<strong>Two that matter, five that are optional.</strong> <strong>1</strong> two layers on the USB socket\'s roof (it is GND; the button\'s legs sit on it) and '
                 '<strong>2</strong> a strip on the amp between its stubs and its chip, under the resistor leads: these two are insulation and stay. '
                 'The rest is convenience and any tape will do: <strong>3</strong> a pad under the mic, <strong>4</strong> a pad under the 220 µF, '
                 '<strong>5</strong> loops holding the rails, <strong>6</strong> loops holding A1 and the amp, <strong>7</strong> a scrap over the mic\'s hole while you sand. Nothing on the antenna end of A1, nothing on any stub.'))
    H.append(step("a6", "Place A1 (USB at the front), the amp (pins to the channel, VIN front), the mic (chip down, SD-VDD-GND column toward the channel), the speaker, the 220 µF. Tape each down with whatever tape is nearest. The screen and button wait.",
                  "A1's GPIO1/2/3 stubs sit level with the amp's LRC/BCLK/DIN stubs across the channel. Sight along them: five straight lines."))
    H.append(step("a7", f"Paint rule: the two rails must be bare along their whole length (an unpainted stick of {a('rod')}, or {a('sand', '400 grit')} and an {a('ipa', 'IPA')} wipe). Every other rod needs only 3 mm bare at each joint. And every meter check below is probe-on-bare-metal: a probe on paint reads open even on a good joint.",
                  "A rail reads bright its whole length and beeps end to end."))

    # ------------------------------------------------------------ rails
    H.append('<h2 id="secB"><span class="when">1:00</span>B · The rails</h2>')
    H.append(f'<p class="stock">Use: <strong>ROD</strong> 1.0 mm · {a("rod")} · {a("flux", "Chip Quik pen")} · {a("solder", "63/37 solder")} · electronics tip · USB unplugged</p>')
    H.append(step("b1", f"The two rails: cut the 3V3 rail {rods[0].length():.0f} mm and the GND rail {rods[1].length():.0f} mm, bare, straight. Lay each on its printed line (3V3 at x = 24 starting 2.5 mm from the front, GND at x = 27 starting 2.0) and hold it down with a bit of tape at each end.",
                  "Both lie flat on the card along their lines. Meter between them: silent.",
                  "Nothing is soldered yet. The taps come to the rails; the rails never move."))
    H.append(fig(D.map_figure(highlight={"3V3 rail", "GND rail"}, title="The two rails on the card"), '<strong>3 mm apart, on the card.</strong> 3V3 nearer A1, GND nearer the amp. Both end 23.5 mm from the front, 1 mm short of the mic.'))

    # ------------------------------------------------------------ channel rods
    H.append('<h2 id="secC"><span class="when">1:20</span>C · The channel rods, one at a time</h2>')
    H.append('<p>Same four moves every time: sand the joint spots, bend to the table, hold with the helping hands, flux, 1–2 s of iron per joint. Each step lists its meter check; doing it per rod finds a fault while it is the only new thing, doing it once at the end of the section is fine too.</p>')
    H.append(rod_card("5 V rod", "c5v", "5 V rod: A1's 5V stub straight across to the amp's VIN stub, 3 mm up, beside both stubs.",
                      "5V stub beeps to VIN. 5 V rod to the GND rail: silent. To the 3V3 rail: silent.",
                      "two: A1 5V stub, amp VIN stub.",
                      f"slide 8 mm of the thinnest {a('shrink', 'heat-shrink')} on first and shrink it over the middle: it crosses both rails and later passes under the screen's VCC tap."))
    H.append(rod_card("GND rod", "cgnd", "GND rod: A1's GND stub straight across to the amp's GND stub, 3 mm up.",
                      "A1 GND beeps to amp GND. GND rod to the 3V3 rail: silent.",
                      "two: A1 GND stub, amp GND stub."))
    H.append(rod_card("GND drop pin", "cpin", "GND drop pin: a 3 mm piece standing on the GND rail directly under the GND rod, soldered at both ends. This is what makes the rail GND.",
                      "GND rail beeps to A1's GND stub. GND rail to the 3V3 rail: silent.",
                      "two: the rail below, the rod above.",
                      extra_caption="The ring marks the spot: x = 27, on the GND rod's line. Hold the piece with tweezers; one touch of the iron at the top, one at the bottom.", simple=True))
    H.append(rod_card("3V3 tap", "c3v3", "3V3 tap: from low on A1's 3V3 stub, across to above the 3V3 rail, then a hook straight down onto it.",
                      "3V3 rail beeps to A1's 3V3 stub. 3V3 rail to GND rail: silent (a chirp is the capacitors later, not now).",
                      "two: A1 3V3 stub, the 3V3 rail.",
                      "none; it ends 2 mm short of the amp SD rod's drop. Keep the hook tight to the rail."))
    H.append(rod_card("DIN rod", "cdin", "DIN rod: A1's GPIO3 stub straight across to the amp's DIN stub.",
                      "GPIO3 beeps to DIN only. To GPIO2, GPIO1, both rails: silent.",
                      "two: A1 GPIO3, amp DIN."))
    H.append(rod_card("BCLK rod", "cbclk", "BCLK rod: A1's GPIO2 straight across to the amp's BCLK stub, soldered there in passing, then up 2.5, right along the amp to x = 36, back past the amp to the mic, left onto SCK.",
                      "GPIO2 beeps to amp BCLK and to mic SCK. GPIO2 to GPIO1, GPIO3, both rails: silent.",
                      "three: A1 GPIO2, amp BCLK (the rod passes it, soldered without cutting), mic SCK.",
                      None,
                      "The long run along x = 36 is 1 mm from the speaker's plastic edge; that is fine."))
    H.append(rod_card("WS rod", "cws", "WS rod: A1's GPIO1 straight across to the amp's LRC stub (tap), then back along the amp's edge, up 4.5, right, back over the mic's right column, down onto WS.",
                      "GPIO1 beeps to amp LRC and to mic WS. GPIO1 to GPIO2 and to both rails: silent.",
                      "three: A1 GPIO1, amp LRC (in passing), mic WS.",
                      None,
                      "It passes 1.3 mm above the L/R stub on its way to WS; that is why it runs at 7.5."))

    # ------------------------------------------------------------ fly-overs
    H.append('<h2 id="secD"><span class="when">2:20</span>D · The fly-overs</h2>')
    H.append('<p>Four rods leave the stub level and cross above the channel. Each has its own height, so they never meet: mic SD at 5.5, amp SD and SCL at 7.5 (never in the same place), SDA at 9.5.</p>')
    H.append(rod_card("mic SD rod", "dmicsd", "mic SD rod: out of A1's GPIO4 stub 1.2 mm, up to 5.5, back along the channel's left lane (x = 22, beside A1's stubs), right at the mic's SD stub, down onto it.",
                      "GPIO4 beeps to mic SD only. To both rails, to GPIO1/2/3: silent.",
                      "two: A1 GPIO4, mic SD.",
                      None,
                      "It crosses above DIN, BCLK and WS with 1.5 mm of air, and under SCL and SDA where they cross the channel."))
    H.append(rod_card("amp SD rod", "dampsd", "amp SD rod: straight up A1's GPIO5 stub to 7.5, back along the left stub line to y = 8, right across A1 (over the USB socket's back edge) and the channel, back 1.7, down to 3, right onto the amp's SD stub.",
                      "GPIO5 beeps to amp SD only. To GND, 3V3, 5 V: silent.",
                      "two: A1 GPIO5, amp SD.",
                      None,
                      "Across A1 it is 5.5 mm above the board and 2.4 above the USB socket. It passes 1 mm behind the button's body."))
    H.append(rod_card("SCL rod", "dscl", "SCL rod: out of A1's GPIO20 stub 1.5 mm to the left lane, up to 7.5, forward to y = 13.5, right across A1 and the channel, forward along x = 29.7 to under the screen's SCL stub, up onto it.",
                      "GPIO20 beeps to screen SCL only. To GPIO21, both rails, GPIO4, GPIO5: silent.",
                      "two: A1 GPIO20, screen SCL (soldered after the screen is in place, step E1; leave the end 3 mm long until then).",
                      f"{a('shrink', 'heat-shrink')} along the left lane and across A1 (dotted in the drawing): SDA runs 2 mm directly above it, and the button rod and mic SD rod pass 1 mm under it."))
    H.append(rod_card("SDA rod", "dsda", "SDA rod: out of A1's GPIO21 stub to the left lane, up to 9.5, forward to y = 13.5, right across A1 and the channel directly above SCL, forward along x = 27.2, up onto the screen's SDA stub.",
                      "GPIO21 beeps to screen SDA only. To GPIO20: silent.",
                      "two: A1 GPIO21, screen SDA (after step E1).",
                      None,
                      "It leaves the stub sideways and climbs immediately, so it never passes over the antenna 4 mm away."))

    # ------------------------------------------------------------ screen, button, mic taps
    H.append('<h2 id="secE"><span class="when">3:20</span>E · Screen, button, mic taps</h2>')
    H.append(step("e1", f"Float the {a('screen')}: a block exactly 12.5 mm tall on the amp (fold a strip of {a('card', 'cardstock')} into a box and check it with the {a('caliper', 'calipers')}), the screen on it glass up, header edge at the front, its four stubs over the dots at y = 3.8. Tape it to the block. Now solder the SCL and SDA rod ends to their stubs and trim.",
                  "Looking from the front: the four stubs hang 10.5–12.5 mm up, SDA at x = 27.2 and SCL at x = 29.7 directly above their rods."))
    H.append(rod_card("screen GND tap", "egnd", "Screen GND tap: down the GND stub to 3.5, forward 1.8, left along y = 2 to above the GND rail's front end, down onto it.",
                      "Screen GND beeps to A1 GND. Screen GND to screen VCC: silent.",
                      "two: screen GND stub, the GND rail's front end."))
    H.append(rod_card("screen VCC tap", "evcc", "Screen VCC tap: down the VCC stub to 5.5, forward 0.5, left along y = 3.3 over the GND tap's drop, down onto the 3V3 rail's front end.",
                      "Screen VCC beeps to A1 3V3. VCC to GND: silent.",
                      "two: screen VCC stub, the 3V3 rail's front end.",
                      f"optional: {a('shrink', 'heat-shrink')} over the left-going run (it passes 1.3 mm from the VIN stub); a careful bend does the same job."))
    H.append(step("e2", "Pull the block out. The screen now hangs on four rods. Press it gently: it must not flex more than a hair. Later a dab of hot glue from its underside to the terminal block makes it rigid.",
                  "The four rods hold it level, 12.5 mm up, by eye against the front elevation."))
    H.append(step("e3", f"Button: two layers of {a('kapton', 'Kapton')} already on the USB socket. Set the {a('button', 'button')} on it, plunger up, 1 mm behind the front edge, its leg pairs left and right. Meter which pair is which: the left pair becomes GPIO10, the right pair GND. Tape it.",
                  "Pressing it does not press A1's own tiny buttons (they are beside the socket, not under it)."))
    H.append(rod_card("button rod", "ebtn", "Button rod: straight up A1's GPIO10 stub to 5.5, right 1.8, forward along x = 6 over A1's board, to the button's back-left leg.",
                      "GPIO10 to GND: silent released, beeps pressed.",
                      "two: A1 GPIO10, the button's left legs.",
                      f"optional: a 6 mm piece of {a('shrink', 'heat-shrink')} where it passes under the amp SD rod at y = 8; 1 mm of air is there without it."))
    H.append(rod_card("button GND rod", "ebtng", "Button GND rod: from the button's back-right leg diagonally back-right at 5.5, down to 3.5 beside A1's GND stub, onto it.",
                      "The button's right legs beep to the GND rail.",
                      "two: the button's right legs, A1's GND stub (next to the GND rod)."))
    H.append(rod_card("mic GND tap", "emg", "Mic GND tap: from the mic's GND stub, forward beside the column at 3.5, right to above the GND rail's back end, down onto it.",
                      "Mic GND beeps to A1 GND.",
                      "two: mic GND stub, the GND rail's back end."))
    H.append(rod_card("mic VDD tap", "emv", "Mic VDD tap: straight up the VDD stub to 6.5, forward above the column, left to x = 24.6, forward 0.5, down onto the 3V3 rail's back end.",
                      "Mic VDD beeps to A1 3V3. VDD to GND: silent.",
                      "two: mic VDD stub, the 3V3 rail's back end.",
                      None,
                      "It climbs first so it clears the GND stub below it and the L/R link by 1.1 mm."))
    H.append(rod_card("L/R link", "elr", "L/R link: one straight piece from the mic's L/R stub to its GND stub, 4.4 mm up, across the board's front edge.",
                      "Mic L/R beeps to GND.",
                      "two: mic L/R, mic GND.",
                      None,
                      "If on your module L/R does not face GND, say so: the link goes round the front edge instead."))

    # ------------------------------------------------------------ small parts
    H.append('<h2 id="secF"><span class="when">4:30</span>F · The small parts</h2>')
    H.append(f'<p class="stock">Use: {a("res", "resistors")} (measure each first) · {a("cap220", "220 µF")} · {a("cap100n", "100 nF")} · {a("shrink", "heat-shrink")} · heat gun (owned, no link recorded)</p>')
    H.append('<p>Each lead is its own rod: bend it with the pliers next to the body, never at the body; cut it 3 mm past the joint. Leads float 1.5–2 mm above the boards on a Kapton strip.</p>')
    H.append(step("f1", "R1, the amp SD pull-down (4.7 kΩ unless you chose 1 kΩ in Step 11): one lead on the amp's SD stub, out over the amp board 2 mm up, body lying along y = 9.7 from x = 33 to 39, the other lead round at x = 40 and back along y = 7.1 to the amp's GND stub.",
                  "GPIO5 to the GND rail reads the resistor's value, not a beep."))
    H.append(fig(D.map_figure(highlight={"R1 lead a", "R1 body", "R1 lead b"}, title="R1: a U-shape over the amp board"),
                 '<strong>The two pull-downs live on the amp, not in the channel.</strong> Each is a U: out along its own stub line, body, back along the GND stub line. They sit 2–3 mm above the board on Kapton, under the screen (which starts at 11.3).'))
    H.append(step("f3", "R3, 10 kΩ: one lead soldered to the BCLK rod in the channel at x = 25.5 (between the rails), up to 8.5, body back along the channel to y = 22.8, the other lead left 0.9 and down onto the top of the mic VDD tap's drop (that is 3V3).",
                  "GPIO2 to the 3V3 rail reads about 10 kΩ."))
    H.append(fig(D.map_figure(highlight={"R3 lead a", "R3 body", "R3 lead b"}, title="R3 at the back of the channel"),
                 '<strong>R3 rides high (11 mm)</strong> above the WS rod and the mic taps, and ends on something that is already the right net: R3 on the VDD tap (3V3), R4 on the L/R link (GND). R4 passes 3 mm in front of the mic\'s hole.'))
    H.append(step("f5", f"100 nF from the {a('cap100n', 'BOJACK kit')}: leads on the amp's VIN and GND stubs, 2.5 mm up, body lying flat on the amp board pointing right (x = 32 to 35).",
                  "VIN to GND: silent or a chirp."))
    H.append(step("f6", f"220 µF from the {a('cap220', 'ALLECIN kit')}: lies on its Kapton pad in the right strip, leads bent 90° at its base and sleeved in {a('shrink', 'heat-shrink')} along the floor. The + lead runs along y = 3 to the amp's front-left corner, up and onto the VIN stub. The − (stripe) lead runs along y = 2 to x = 29, back along x = 29 under the 5 V rod, up onto the GND rod.",
                  "VIN to GND: a chirp that stops. A steady tone means a short or a backwards capacitor. Stripe to GND."))
    H.append(fig(D.map_figure(highlight={"220u lead +", "220u lead -", "220u body", "100n lead +", "100n lead -", "100n body"}, title="The two capacitors"),
                 '<strong>The bulk capacitor lies where there is room.</strong> Its two sleeved leads run along the floor, 1 mm apart, to the 5 V net and the GND rod. 25 mm of lead on a 220 µF changes nothing it does; the 100 nF stays right at the pins.'))
    H.append(step("f7", f"Speaker leads into the terminal block: OUT+ and OUT−, twisted, never cut. Route them along the right strip over the 220 µF.",
                  "Meter OUT+ and OUT− to the GND rail, the frame and each other: silent (the speaker's own 8 Ω between them is fine on the Ω range)."))

    # ------------------------------------------------------------ tests
    H.append('<h2 id="secG"><span class="when">5:30</span>G · Test it, then the frame</h2>')
    H.append(step("g1", f"Full sweep with the {a('meter')} before power, probes on bare metal: GND rail to the 3V3 rail, to the 5 V rod, to every GPIO rod; 3V3 rail to 5 V; every GPIO rod to its neighbours.",
                  "No steady tone anywhere. A chirp on the rails is the capacitors."))
    H.append(step("g2", "Power up (USB in). Eyes, <code>got ip</code>, <code>hello accepted</code>, happy double blink.",
                  "Same as the breadboard this morning. Screen blank: its VCC/GND taps. No eyes at all: the 3V3 tap. Eyes upside down: say so, I rebuild with <code>CONFIG_POCKET_DISPLAY_FLIP=y</code> (the header edge faces the front in this build)."))
    H.append(step("g3", "Button: hold and release, say nothing.", "Listening → thinking → <code>heard nothing</code>."))
    H.append(step("g4", "Mic: uncover the hole. Hold the button, ask Pip its name, release.", "Your words appear as <code>user: …</code> in the log. If garbled, tell me the levels; the gain shift may need a notch."))
    H.append(step("g5", "Speaker: USB out. Say <em>enable the amplifier</em>; I rebuild with <code>CONFIG_POCKET_ENABLE_AMPLIFIER=y</code> at cap 45, you flash.",
                  "Boot log: <code>amplifier ENABLED; volume cap 45</code>. Pip answers out loud. <code>speaker peak</code> lines stay under 2.53 V."))
    H.append(step("g6", "Two cold starts: unplug, ten seconds, plug in, one question each.", "Both answer. Nothing warm."))
    H.append('<div class="gate"><input type="checkbox" id="gate"><label for="gate"><div class="name">WIRE-01 · the brass harness works off the frame</div><p>All of the above ticked. Photograph the harness from above and from the front, send both, with the inside height you measured.</p></label></div>')
    H.append(step("g7", f"Into the frame: {a('kapton', 'Kapton')} on every inner face of the tubes and posts. Lift the card with everything on it and lower it in. Nothing glued yet. Repeat the sweep against the frame: frame to GND rail, 3V3 rail, 5 V rod, OUT+, OUT−: silent.",
                  "Power up inside the frame: the full test again, and five questions for the Wi-Fi check."))
    H.append(fig(D.attachment_figure(),
                 '<strong>What touches the frame: only the card.</strong> The harness is one rigid piece held together by its own rods; it sits on the floor card; the card sits on the bottom loop, over Kapton, and four dabs of glue at its corners are the whole attachment. Two more dabs steady parts against each other (screen to terminal block, capacitor to its pad), not against the frame. Nothing touches the posts or the top loop.'))
    H.append(step("g8", "Small dabs of low-temperature hot glue: the card to the bottom loop at four corners, the screen's underside to the terminal block, the 220 µF to its pad. None near the mic hole, the USB port or the button.",
                  "The device can be picked up and turned over and nothing moves."))

    # ------------------------------------------------------------ evidence
    H.append('<div class="evidence">'
             '<p><strong>Sources.</strong> Connections, resistor values and tests: <code>plan/FAST_TRACK.md</code> Steps 6–11 and the <code>CLAUDE.md</code> hardware contract. Part sizes: your caliper measurements of 28 September (A1 22 × 18, screen 27 × 27, mic Ø13, amp 17 × 17, speaker 20 × 13, button 5 × 5) and the SuperMini and INMP441 pin pitches. Product links: <code>docs/INVENTORY.md</code>, then <code>docs/MATERIALS.md</code> for the two capacitor kits; the flux pen is Adafruit product 3468. The geometry is in <code>edu/pages/gen/harness_model.py</code>; every drawing and every number on this page is generated from it.</p>'
             '<p><strong>What is and is not verified.</strong> The circuit passed on the breadboard. The placement, heights and clearances are computed, not built: hands add ±0.5 mm, which is why every gap under 1.5 mm gets a sleeve. The four checks at the top are assumptions about your exact modules. Nothing on this page has been soldered yet, and no hardware result is claimed.</p>'
             '</div>')
    H.append('</div>')
    H.append('''<script>
  (function () {
    var boxes = Array.prototype.slice.call(document.querySelectorAll('input[type=checkbox]'));
    var key = function (b) { return "brass-harness-" + b.id; };
    function count() {
      var n = boxes.filter(function (b) { return b.checked; }).length;
      document.getElementById("done").textContent = n;
      document.getElementById("total").textContent = boxes.length;
    }
    boxes.forEach(function (b) {
      try { b.checked = localStorage.getItem(key(b)) === "1"; } catch (e) {}
      b.addEventListener("change", function () { try { localStorage.setItem(key(b), b.checked ? "1" : "0"); } catch (e) {} count(); });
    });
    document.getElementById("reset").addEventListener("click", function () {
      boxes.forEach(function (b) { b.checked = false; try { localStorage.removeItem(key(b)); } catch (e) {} });
      count();
    });
    count();
  })();
</script>
''')
    OUT.write_text("\n".join(H))
    TEMPLATE_SVG.write_text(D.floor_template_svg(3.7795))   # 96 dpi: 1 mm = 3.7795 px
    print("wrote", OUT, OUT.stat().st_size, "bytes;", TEMPLATE_SVG)


if __name__ == "__main__":
    main()
