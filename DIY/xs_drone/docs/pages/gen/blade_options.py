#!/usr/bin/env python3
"""Blade options for the XS drone's lift revision, drawn on the drone itself.

Writes pages/blade-options.html; with --png also pages/blade-options.png (headless Chrome).
The drone is lift_views.three_quarter() with the prop swapped per option and the labels stripped.
Listings read 2026-11-10 (Tiny Whoop's product feed and the Amazon listing in the builder's Chrome).
Run: python3 blade_options.py [--png]
"""
import math
import pathlib
import re
import subprocess
import sys

import lift_views as lv

PAGES = pathlib.Path(__file__).resolve().parent.parent
OUT = PAGES / "blade-options.html"
PNG = PAGES / "blade-options.png"
READ = "2026-11-10"

# blade outlines in the prop plane, mm: (radius, half-width) out along the leading edge, then back along the trailing edge
PADDLE = ([(2.0, 1.0), (6.0, 2.6), (11.0, 4.2), (15.5, 4.4), (18.6, 3.0), (19.6, 0.8)],
          [(19.6, -0.6), (18.0, -2.2), (14.0, -2.9), (9.0, -2.4), (5.0, -1.6), (2.0, -1.0)])
SLIM = ([(1.8, 0.9), (6.0, 2.0), (11.0, 2.7), (15.5, 2.5), (18.8, 1.6), (19.7, 0.5)],
        [(19.7, -0.4), (18.0, -1.3), (13.0, -1.7), (8.0, -1.5), (4.0, -1.2), (1.8, -0.9)])

OPTIONS = [
    dict(key="grey", name="Grey polycarbonate, four blades", tag="in the Tiny Whoop cart now",
         url="https://www.tinywhoop.com/products/hq-prop-40mm-4-blade-props-grey-1mm-shaft",
         where="tinywhoop.com, $3.49 a set of four, in stock",
         spec="0.5 g each · pitch 1.0 · translucent", lift="the lift the physics page counts",
         blades=4, shape=PADDLE, fill="#AEB4BA", op=0.62, edge="#7B838B", hub="#8A9097", sheen=0.0,
         phases=(20, 65, 110, 5)),
    dict(key="black4", name="Solid black ABS, four blades", tag="the pick",
         url="https://www.amazon.com/dp/B0CH1WJ19N",
         where="Amazon, $9.99 for twelve (three sets), 4 left, arriving Thu 11-12",
         spec="0.31 g each · pitch 1.6 · opaque", lift="same lift, 0.8 g lighter; the classic brushed-whoop blade",
         blades=4, shape=PADDLE, fill="#17181B", op=1.0, edge="#000000", hub="#0B0B0D", sheen=0.20,
         phases=(20, 65, 110, 5)),
    dict(key="black2", name="Solid black polycarbonate, two blades", tag="slimmest, less lift",
         url="https://www.tinywhoop.com/products/hq-ultralight-whoop-prop-40mmx21-6x1-2-2cw-2ccw",
         where="tinywhoop.com, $3.25 a set of four, in stock",
         spec="0.2 g each · pitch 1.2 · opaque", lift="about 10 to 20 % less peak lift (est.), longer hover",
         blades=2, shape=SLIM, fill="#17181B", op=1.0, edge="#000000", hub="#0B0B0D", sheen=0.20,
         phases=(35, 120, 75, 160)),
]


def make_prop(o):
    count = [0]

    def prop(cx, cy):
        k = count[0] % 4
        count[0] += 1
        _, _, d = lv.P(cx, cy, lv.PROP_Z)
        disc = lv.circle3d(cx, cy, lv.PROP_Z, lv.PROP_R, "z")
        out = [f'<polygon points="{lv.pts(disc)}" class="disc-{o["key"]}"/>']
        turn = 1 if cx * cy > 0 else -1                      # CW and CCW props are mirror images
        lead, trail = o["shape"]
        for b in range(o["blades"]):
            a = math.radians(o["phases"][k] + 360 / o["blades"] * b)
            c, s = math.cos(a), math.sin(a)

            def at(r, w):
                w *= turn
                return lv.P(cx + r * c - w * s, cy + r * s + w * c, lv.PROP_Z)

            poly = [at(r, w) for r, w in lead] + [at(r, w) for r, w in trail]
            out.append(f'<polygon points="{lv.pts(poly)}" class="blade-{o["key"]}"/>')
            if o["sheen"]:
                hi = [at(5, 0.9), at(10, 1.8), at(15, 1.8), at(18, 1.0)] if o["blades"] == 4 else [at(5, 0.6), at(10, 1.0), at(15, 0.9), at(18, 0.5)]
                out.append(f'<polyline points="{lv.pts(hi)}" fill="none" stroke="#FFFFFF" stroke-opacity="{o["sheen"]}" stroke-width="1.6" stroke-linecap="round"/>')
        hub = lv.circle3d(cx, cy, lv.PROP_Z + 0.5, 2.5, "z", 20)
        out.append(f'<polygon points="{lv.pts(hub)}" fill="{o["hub"]}"/>')
        return d + 40, "".join(out)

    return prop


def bounds():
    us, vs = [], []
    for x in (-lv.AXLE_X - lv.PROP_R, lv.AXLE_X + lv.PROP_R):
        for y in (-lv.AXLE_Y - lv.PROP_R, lv.AXLE_Y + lv.PROP_R):
            for z in (-lv.SKID, lv.SERVO[5] + 1):
                u, v, _ = lv.P(x, y, z)
                us.append(u)
                vs.append(v)
    pad = 10
    return min(us) - pad, min(vs) - pad, max(us) - min(us) + 2 * pad, max(vs) - min(vs) + 2 * pad


def drone(o):
    keep = lv.prop
    lv.prop = make_prop(o)
    try:
        svg = lv.three_quarter()
    finally:
        lv.prop = keep
    svg = re.sub(r'<line [^>]*class="lead"/>', "", svg)
    svg = re.sub(r'<circle [^>]*class="dot"/>', "", svg)
    svg = re.sub(r'<text [^>]*class="[th]"[^>]*>.*?</text>', "", svg, flags=re.S)
    x, y, w, h = bounds()
    svg = re.sub(r'<svg viewBox="[^"]*"[^>]*>', f'<svg viewBox="{x:.0f} {y:.0f} {w:.0f} {h:.0f}" role="img" aria-label="The drone with {o["name"].lower()} props">', svg, count=1)
    extra = (f'.disc-{o["key"]}{{fill:none;stroke:var(--ink-2);stroke-opacity:0.35;stroke-width:0.8;stroke-dasharray:3 4}}'
             f'.blade-{o["key"]}{{fill:{o["fill"]};fill-opacity:{o["op"]};stroke:{o["edge"]};stroke-width:0.7;stroke-linejoin:round}}')
    return svg.replace("<style>", "<style>" + extra, 1)


def page():
    cards = []
    for o in OPTIONS:
        pick = " pick" if o["key"] == "black4" else ""
        cards.append(f'<article class="card{pick}"><div class="fig">{drone(o)}</div>'
                     f'<div class="tag">{o["tag"]}</div><h2><a href="{o["url"]}" target="_blank" rel="noopener">{o["name"]}</a></h2>'
                     f'<p>{o["where"]}</p><p>{o["spec"]}</p><p class="lift">{o["lift"]}</p></article>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XS Drone Blade Options</title>
<style>
:root{{--bg:#EEF0F2;--paper:#FFFFFF;--ink:#171B20;--ink-2:#5B6470;--line:#CBD1D8;
--metal:#7B838B;--metal-soft:#E2E5E8;--matte:#3A3E44;--matte-edge:#141619;--lamp-face:#F2F4F6;--lens:#E8EEF2;--skin:#F4F2EC;--skin-edge:#9C9890;
--board:#5E8A6A;--board-edge:#2F4A37;--brass:#9A7B3C;--brass-soft:#E8D9B8}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Source Sans 3","Segoe UI",system-ui,sans-serif;font-size:16px;line-height:1.45;padding:22px 24px 26px}}
h1{{font:700 26px/1.2 "Barlow Semi Condensed","Arial Narrow",Arial,sans-serif;margin:0 0 4px}}
.sub{{color:var(--ink-2);margin:0 0 18px;max-width:70ch}}
.row{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}
.card{{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:14px 16px 16px}}
.card.pick{{border:2px solid var(--brass)}}
.fig svg{{display:block;width:100%;height:auto}}
.tag{{font:600 12px/1 "Source Code Pro",ui-monospace,Menlo,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);margin-top:8px}}
.pick .tag{{color:var(--brass)}}
h2{{font:700 19px/1.25 "Barlow Semi Condensed","Arial Narrow",Arial,sans-serif;margin:6px 0 6px}}
h2 a{{color:inherit}}
p{{margin:0 0 3px;color:var(--ink-2)}} p.lift{{color:var(--ink)}}
@media (max-width:900px){{.row{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>Blade options on the drone</h1>
<p class="sub">The lift revision as approved, brass ladder and all, with three 40 mm props that fit the 1 mm motor shaft and are in stock. Listings read {READ}. Drawn, not photographed: the grey is see-through plastic, the black is solid.</p>
<div class="row">{"".join(cards)}</div>
</body></html>'''


def main():
    OUT.write_text(page(), encoding="utf8")
    print("wrote", OUT, OUT.stat().st_size)
    if "--png" in sys.argv:
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        "--window-size=1500,640", f"--screenshot={PNG}", OUT.as_uri()], check=True, capture_output=True, timeout=120)
        print("wrote", PNG, PNG.stat().st_size)


if __name__ == "__main__":
    main()
