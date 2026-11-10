# Bill of materials — archived R1 reference reconciliation

> **HISTORICAL COMPARISON; NOT PURCHASE AUTHORITY.** This maps the creator's
> parts to Claude's superseded R1 proposal. Use the exact, status-marked Phase
> 0 list and alternatives in
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md). Do not order
> from [MATERIALS.md](MATERIALS.md) or interpret the “released” column below as
> a current decision.

This list reconciles the [project page](https://www.huyvector.org/robots-kinetic/pocket-ai-assistant),
its [assembly video](https://www.youtube.com/watch?v=25RGnr407PM), the wiring
diagram, and reachable listings. Creator links are affiliate/marketplace
links; verify the selected variant, dimensions, chemistry, and datasheet
before ordering.

## Electronics — creator part vs R1 part

| Creator's part | R1 released part | Delta |
| --- | --- | --- |
| ESP32-C3 **SuperMini** ([AliExpress](https://s.click.aliexpress.com/e/_oCNdARN) / [Amazon](https://www.amazon.com/dp/B0G5XS345R)) | Same class — plain SuperMini, ≥4 MB flash gated by `esptool flash_id` | None electrically; boards are qualified on arrival because clones vary |
| 0.96" SSD1306 I2C OLED, 0x3C ([AliExpress](https://s.click.aliexpress.com/e/_oCOMyUB)) | Same class, white, 4-pin I2C | Firmware also probes 0x3D, so an Adafruit #326 works too |
| INMP441 I2S microphone ([AliExpress](https://s.click.aliexpress.com/e/_c34pKgRt)) | Same part | Video uses a compact round PCB; rectangular breakouts are electrically identical — check fit. Alternate: Adafruit #6049 ICS-43434 |
| "98357BGA" amplifier ([AliExpress](https://s.click.aliexpress.com/e/_c4dOCXCR)) | MAX98357A breakout | The page's "98357BGA" is a naming error for the same chip |
| Phone speaker ([AliExpress](https://s.click.aliexpress.com/e/_oobS0wr)) | Same Sky CES-20134-088PM, 8 Ω 0.8 W enclosed | The one part upgraded on principle: the creator's speaker has no published impedance/power; the Same Sky documents both and ships its own sealed enclosure at the same size. Phone speaker stays as an A/B fallback |
| Mini SPDT slide switch ([AliExpress](https://s.click.aliexpress.com/e/_c3F1y5i3)) | Same class (SS12D00) | Same role — but in the **protected** positive lead |
| *(absent from the public diagram)* | 6×6 mm momentary button, GPIO10 → GND | Binary inspection shows this input exists in the firmware: chat toggle + long-press Wi-Fi reset. Without it the device still wake-words, but fit it — GPIO9 is ROM BOOT, not this |
| `14250 1200 mAh 3.7 V` cell, wrapper stripped, can soldered to frame | **Adafruit #1578** — protected 500 mAh LiPo, factory JST lead, never soldered | **The deliberate safety break with the video** — see below |
| Type-C charging module, 1 A ([Amazon](https://www.amazon.com/dp/B0BRXYZTWN)) | **Adafruit #4410** USB-C Micro-Lipo, 100→500 mA documented | Same in-frame charging concept; current matched to the cell. A TP4056-class module is acceptable only with DW01A+FS8205 protection and a swapped `Rprog` |
| Brass tube 1.5 mm ×2, "copper wire 1 mm" (video shows brass) | K&S #9831 tube + #9861 1.0 mm brass rod | Round brass rod matches the video; the page's "copper" appears to be an error |

## The battery decision — resolved

The creator's video shows a `14250 1200 mAh 3.7 V` cell, removes its wrapper,
and solders its can to the brass frame. **Do not reproduce that sequence.**

- A ~1200 mAh half-AA is commonly **primary** Li-SOCl₂ chemistry: the
  manufacturer's [Saft LS 14250 datasheet](https://saft4u.saft.com/en/download_file/133c84de-f6e9-46b6-a412-fc4ed453fb5c/English)
  identifies that cell class as primary and prohibits recharging and direct
  soldering. A capacity or `3.7 V` label alone proves nothing about
  chemistry or safe current.
- R1 therefore substitutes a **documented protected rechargeable pack**
  (Adafruit #1578: overcharge/over-discharge/short protection, JST lead) and
  keeps everything else about the creator's power topology: in-frame USB-C
  charging, slide switch, direct feed to the SuperMini `5V` pin and amp VIN.
- Those R1 procedural rules were withdrawn because OFF is not electrical
  isolation. The current separate-fixture rules are in the
  [candidate power architecture](FINAL_MATERIALS_FOR_REVIEW.md#candidate-power-architecture).

Rejected forever, regardless of listing: `ER14250`, `LS14250`, any 3.6 V
Li-SOCl₂, any cell without clearly stated chemistry, and any assembly that
makes the exposed brass frame a cell terminal.

## Structural material and consumables

| Qty. | Item | Source | Notes |
| ---: | --- | --- | --- |
| 1 pack | Brass tube 1.5 mm OD | [K&S #9831](https://ksmetals.com/products/br225mm-1h) | The page asks for two lengths; the 4-piece pack covers mistakes. Deburr after cutting |
| 1 pack | Brass rod 1.0 mm | [K&S #9861](https://ksmetals.com/products/brrmet-1) | Video says 1.0 mm brass wire despite the page saying copper; round rod matches the video |
| As needed | Hookup wire | 26 AWG (power/speaker), 30 AWG (signals) | Never the frame as a conductor |
| As needed | Fish paper, Kapton, heat-shrink | See [MATERIALS.md](MATERIALS.md) | Around the pack, positive rail, module backs, frame crossings |
| As needed | Hot glue + CA | Electronics-safe, sparing | The video's retention; keep clear of mic port, switch, connectors |
| As needed | Files, 400–800 grit, IPA, swabs | — | Clean brass before flux; no sharp edges near the pack |

The video shows ~40 mm and ~15 mm template marks but never a dimensioned
width/height/depth. Derive the finished geometry from the purchased parts on
cardstock (R1 target ≈ 45 × 32 × 20 mm) and dry-fit before cutting brass.

## Tools

The owned-equipment reconciliation and the remaining tool purchases are in
[MATERIALS.md](MATERIALS.md#4--tools). The short version: the X-Tronic
station kit covers soldering; still needed are a multimeter, a
current-limited bench supply (mandatory — it stands in for the cell in every
power test), calipers, a jeweler's saw, strippers, and safety gear.
