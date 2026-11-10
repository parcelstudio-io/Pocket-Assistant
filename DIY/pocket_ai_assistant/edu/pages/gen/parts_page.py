"""Builds edu/pages/full-build-parts.html: every part of the full build (harness + battery + frame), with links."""
from __future__ import annotations

import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "full-build-parts.html"


def style():
    src = (HERE / "harness_page.py").read_text()
    return re.search(r"<style>.*?</style>", src, re.S).group(0)


def link(url, text):
    return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>' if url else text


AMZ = "https://www.amazon.com/dp/"

GROUPS = [
    ("The five modules", [
        ("ESP32-C3 SuperMini (A1)", "Meshnology, 10-pack", AMZ + "B0F888JQ91", "own", "the brain; 1 used"),
        ("0.96\" OLED, SSD1306", "Hosyond, 5-pack", AMZ + "B09T6SJBV5", "own", "the eyes; reads SDA·SCL·VCC·GND pins-at-bottom"),
        ("INMP441 microphone", "AITRIP, 5-pack, round Ø13", AMZ + "B092HWW4RS", "own", "lies chip-side down, hole up"),
        ("MAX98357A amplifier", "3-pack, terminal block opposite the pins", AMZ + "B0CDWXZZCH", "own", "pins face the channel, VIN at the front"),
        ("Speaker, 8 Ω 0.8 W, enclosed", "Same Sky CES-20134-088PM", "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309", "own", "its own leads into the block, never cut"),
        ("Tactile button", "QTEATAK kit", AMZ + "B0FHW6HMG4", "own", "on the USB socket's Kapton"),
    ]),
    ("Small parts", [
        ("Resistors: 4.7 kΩ (or 1 kΩ), 10 kΩ", "LuminologyPro kit", AMZ + "B0F4P352BB", "own", "R1, R3; measure each (R2 GAIN and R4 mic-SD dropped 2026-10-14)"),
        ("220 µF electrolytic", "ALLECIN kit", AMZ + "B0C1VBXCQM", "own", "C1, stripe to GND"),
        ("100 nF ceramic", "BOJACK kit", AMZ + "B07P7HRGT9", "own", "C2, at the amp's VIN/GND stubs"),
    ]),
    ("Power and battery", [
        ("PowerBoost 1000C (third-party copy)", "sold as 'For Powerboost 1000 … 2465 Module'; charger + load sharing + 5 V boost, EN switch pin — verify on the bench", AMZ + "B0G5PXGVG9", "own", "the one board that owns the power; micro-USB charge port"),
        ("1200 mAh LiPo, protected, JST-PH", "Adafruit #258", "https://www.adafruit.com/product/258", "own", "the only owned cell rated for the load; 62 × 34 × 5"),
        ("Slide switch", "Chanzon SPDT mini, 25-pack", AMZ + "B09R434VJQ", "own", "on the EN pin; carries no current"),
        ("26 AWG silicone wire", "TUOFENG", AMZ + "B07G2LRX68", "own", "5 V and GND from the PowerBoost"),
        ("30 AWG silicone wire", "CBAZY", AMZ + "B073RDGTPB", "own", "EN, LBO"),
        ("Micro-USB cable + any 5 V USB charger", "the PowerBoost's port is micro-USB", "", "check", "if you want USB-C instead: Seeed LiPo Rider Plus in place of the PowerBoost, same wiring"),
    ]),
    ("Wiring and frame, brass build", [
        ("1.0 mm brass rod", "K&S #9861, 5 per pack (10 owned)", AMZ + "B005WPB7YG", "own", "rails and all 19 rods"),
        ("1.5 mm brass tube", "K&S #9831, 4 per pack", AMZ + "B005WPAW9M", "own", "the frame loops; posts from the rod"),
        ("Harris Stay-Clean acid flux", "SCLF4", AMZ + "B0015DWPV8", "own", "brass tube frame only, wash the same day"),
        ("Jeweler's saw", "SE 3-in-1", AMZ + "B06XPSLS6N", "own", "the tube; never cutters"),
    ]),
    ("Wiring and frame, silver build (the one-frame battery version)", [
        ("18 ga .925 sterling round wire, 5 ft", "WireJewelry, dead-soft", AMZ + "B00ANA6JFC", "own", "rails and rods; straighten each piece first"),
        ("14 ga .925 sterling round wire, 5 ft", "WireJewelry, dead-soft", AMZ + "B00BY9A9HU", "own", "two loops at 65 × 39 inside, four posts of 35"),
    ]),
    ("Consumables", [
        ("Cardstock, 65 lb", "Amazon Basics", AMZ + "B0DSH5V1TT", "own", "jig card, shelf, cell cradle"),
        ("Kapton tape", "ELEGOO", AMZ + "B072Z92QZ2", "own", "socket roof, amp strip, A1's port, every tube"),
        ("Heat-shrink, 1.5–2 mm", "Pointool kit, white", AMZ + "B08N4W4K9X", "own", "5 V rod, GND rod, SCL, the 220 µF leads"),
        ("63/37 solder, 0.8 mm", "MAIYUM", AMZ + "B076QF1Y85", "own", ""),
        ("No-clean flux pen", "Chip Quik CQ4LF", "https://www.adafruit.com/product/3468", "own", "every electronics joint"),
        ("Solder wick", "JoTownCand", AMZ + "B0DRN688Q5", "own", "bridges between stubs"),
        ("400 grit wet/dry", "BAISDY", AMZ + "B07D2YYC11", "own", "stubs and joint spots bright"),
        ("91 % isopropyl alcohol", "Epic Medical Supply", AMZ + "B0BSJ93RKB", "own", "wipe after sanding paint"),
        ("Hot glue, low temperature", "SHJADE mini gun + sticks", "", "own", "six dots at the very end; no link recorded"),
    ]),
    ("Tools", [
        ("Soldering station + silicone mat + helping hands + tweezers", "X-Tronic 3020-XTS kit", "", "own", "no link recorded; electronics tip for the harness"),
        ("Soldering tips", "900M-T assortment + tinner", "", "own", "no link recorded"),
        ("Flush cutters", "BOENFU 6\"", AMZ + "B07C5PM8L4", "own", "pins, rod, leads; never the tube"),
        ("Chain-nose + round-nose pliers", "WORKPRO 3-pack", AMZ + "B0B8QBVXXR", "own", "the strip off the headers, every bend"),
        ("Digital caliper", "NEIKO 01407A", AMZ + "B000GSLKIW", "own", "stubs 1.5–2.5, the 12.5 mm screen block"),
        ("Multimeter", "KAIWEETS TRMS", AMZ + "B08BL288LW", "own", "continuity after every move"),
        ("Heat gun", "QWORK mini", "", "own", "no link recorded; shrinks the sleeves, never near the mic"),
        ("Cutting mat", "Dahle Vantage 10672", AMZ + "B0027ROZ9G", "own", "cutting the cards; never solder on it"),
    ]),
]


def main():
    H = ['<title>Full Build Parts</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
         style(),
         '<style>.tag { font-family: var(--mono); font-size: 11px; letter-spacing: .05em; text-transform: uppercase; padding: 2px 7px; border-radius: 4px; }'
         ' .own { background: var(--pass-tint); color: var(--pass); } .buy { background: var(--warn-tint); color: var(--warn); font-weight: 700; } .check { background: var(--accent-tint); color: var(--accent-ink); }</style>',
         '<div class="wrap">',
         '<div class="eyebrow">Pocket AI Assistant · final build · every part, with its listing</div>',
         '<h1>Everything the full build needs</h1>',
         '<p class="lede">Harness, battery, charging, frame and the tools to make them. Each row links to the listing you bought it from, or the one to buy. The whole device needs <strong>one purchase</strong>: the PowerBoost. One thing to check: a micro-USB cable for charging.</p>']
    n_buy = sum(1 for _, rows in GROUPS for r in rows if r[3] == "buy")
    H.append(f'<div class="callout pass"><span class="label">Summary</span><p>{sum(len(r) for _, r in GROUPS)} items · {n_buy} to buy · everything else is on the bench. The rechargeable battery is the 1200 mAh cell you own; it charges through the PowerBoost\'s USB port, in the device, with any 5 V USB charger.</p></div>')
    for title, rows in GROUPS:
        H.append(f'<h2>{title}</h2>')
        H.append('<div class="scrollx"><table class="t"><tr><th>Part</th><th>Exactly which</th><th></th><th>Role</th></tr>')
        for name, which, url, status, role in rows:
            tag = {"own": "own", "buy": "buy", "check": "check"}[status]
            H.append(f'<tr><td><strong>{name}</strong></td><td>{link(url, which) if url else which}</td><td><span class="tag {tag}">{tag}</span></td><td>{role}</td></tr>')
        H.append('</table></div>')
    H.append('<div class="evidence"><p><strong>Sources.</strong> Ownership and listings from <code>docs/INVENTORY.md</code> (Amazon #1–#19, DigiKey, Adafruit), the two capacitor kits from <code>docs/MATERIALS.md</code>. "No link recorded" means the purchase is recorded without its listing. The PowerBoost is the only part not yet bought.</p></div>')
    H.append('</div>')
    OUT.write_text("\n".join(H))
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
