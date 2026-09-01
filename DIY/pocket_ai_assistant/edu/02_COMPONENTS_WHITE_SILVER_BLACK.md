# 2 — Authoritative Rev A BOM: white, silver, and black

> **Purchase gate:** this freezes the intended identities/specifications, not
> authorization for a one-shot finished build. Order only the Phase 0 subset
> in the [purchase-readiness review](../docs/PURCHASE_READINESS.md). Hold the
> final passive carrier, frame, guards, and prints until USB isolation,
> measured CAD, and hardware tests pass.

This is the identity/specification baseline for the first free-form prototype.
It keeps the video's visible character but uses a removable protected
rechargeable cell and an external charger. That deliberate change removes an
undocumented charging circuit from an open metal sculpture. Safe assembled USB
service still requires the separate isolation design called out above; cell
removal alone does not isolate the regulator output/peripheral rail.

The deeper engineering rationale and rejected alternatives are in [Why each component was chosen](02-components.md). Prices and stock change; buy by exact order code/specification and recheck availability.

## Electronics

| Qty | Buy | Critical requirement and reason | Fit / color | Verify on arrival |
| ---: | --- | --- | --- | --- |
| 2 | ESP32-C3 SuperMini, plain version, black PCB, 4 MB+ flash | One installed, one qualified spare. Exact board/pins match the firmware; avoid Plus/V2/U.FL variants | About 22.5 × 18 mm; black accent | `esptool flash_id`, USB enumeration, pin silk, no U.FL, GPIO4 exposed |
| 1 | [Adafruit #326](https://www.adafruit.com/product/326) white 0.96-inch 128×64 SSD1306 OLED | Published schematic/mechanics and confirmed white pixels. Firmware probes `0x3c`, then `0x3d` | White face, black background; 29.2 × 26.7 × 6.2 mm | I2C scan, full-pixel test, actual mounting/connector envelope |
| 1 | INMP441 I2S microphone breakout | 3.3 V digital mic; firmware uses `SD` on GPIO4 and left slot (`L/R` low) | Prefer black PCB; never cover its port | Pin order, port location, intelligible 16 kHz capture |
| 1 | [DFRobot DFR0954](https://www.dfrobot.com/product-2614.html) MAX98357A I2S amplifier | Documented breakout. At 3.3 V it suits the selected 8 Ω/0.7 W speaker; configure left-channel mode as its schematic requires | Hide its non-black PCB behind a ventilated black guard | Correct board/labels; `SD`/channel configuration; clean audio |
| 1 | [Same Sky CMS-15113-078L100-67](https://www.sameskydevices.com/product/audio/speakers/miniature-%2810-mm~40-mm%29/cms-15113-078l100-67) wired speaker | Documented 8 Ω, 0.7 W, 15 × 11 mm part with factory 100 mm leads; needs about a 1 cc enclosure | Black/silver native; black cloth over outlet | Plausible coil resistance; neither lead reaches frame/GND; acoustic box fits |
| 1 | [Nitecore NL169 protected 16340](https://www.nitecore.com/product/nl169) | Rechargeable 3.6 V, 950 mAh, published 2 A continuous rating, 16.6 ±0.2 × 34.1 ±0.3 mm. Removable; never solder it | Hidden; no paint/wrap changes | Exact `NL169` without an integrated charge port, intact wrapper, protected marking, dimensions, polarity |
| 1 | [MPD BH123A](https://products.memoryprotectiondevices.com/?page_id=742) single CR123A/16340 holder | Spring/contact holder makes the cell removable; MPD states reverse-polarity protection. Confirm the protected cell's maximum-tolerance envelope and contact pressure in the received holder | Hidden inside white/black guard | Physical insertion/removal; polarity marks; no wrapper damage or loose contact |
| 1 | [XTAR ANT MC1 Plus USB-C](https://www.xtar.cc/product/xtar-ant-mc1-plus-charger-7.html) whose received manual/label explicitly lists 16340 and automatic 0.5/1 A operation | Charges the cell outside the sculpture with 4.2 V CC/CV termination and independent safety features | Not installed | Buy the exact official variant; confirm the cell selects 0.5 A and measure final voltage before accepting it |
| 1 | [Pololu S8V9F3 #4964](https://www.pololu.com/product/4964) 3.3 V step-up/down regulator | Regulates the entire load at 3.3 V across the cell range; published typical max is 1.5 A near output voltage | 10.2 × 16.5 × 2.5 mm; hide behind ventilated black guard | 3.3 V no-load and loaded; thermal/current stress at actual endpoints |
| 1 | [Pololu Mini MOSFET Slide Switch LV #2810](https://www.pololu.com/product/2810) | High-side operational switch with reverse-voltage protection; appropriate for a single lithium cell and avoids routing load current through a tiny cosmetic switch. It is not a safety cutoff | 15.2 × 15.2 mm, black PCB, red LED; mask LED if desired without trapping heat | Correct VIN/VOUT/GND; normal off-state behavior; cell remains the hard disconnect |
| 1 | Littelfuse `1206L150SLYR`, 1.5 A hold / 3.9 A trip PTC at 20 °C, 6 V | Named fault-current layer ahead of the regulator; cell protection remains the backup. Its hold rating derates with heat, so test for nuisance trips in the finished enclosure | Hide on insulated sub-plate or suitable carrier | Exact package/marking; cold resistance; peak-load and warm-enclosure test |
| 1 | Normally-open tactile action button, white cap (black fallback) | GPIO10-to-GND manual chat/Wi-Fi recovery; GPIO9 remains ROM BOOT | White primary control; black is an acceptable secondary accent | Open normally, <2 Ω pressed |
| 1 | Panasonic `6SVPC220M`, 220 µF/6.3 V polymer, about 6.3 mm diameter × 6.0 mm high | Active-production local reservoir on the regulated amplifier rail; replaces the lower-profile but end-of-life `6TPB220ML` | Black/silver | Correct polarity; mount on a suitable SMD carrier/land pattern close to the amp; use the corrected CAD envelope |
| as listed | 10 µF X5R ×3; 100 nF X7R ×4; 10 kΩ ×3; 100 kΩ ×1; Murata `BLM21PG221SN1D` ferrite bead; buy at least 10 of each small value | Local decoupling, boot-strap/data bias, button filtering, and audio supply filtering. No GPIO0 battery divider is fitted in Rev A | Hidden on a reviewed carrier/protoboard; the bead is 0805 | Values, package adapters, and placement checked against the final harness before soldering |

Power path: `protected 16340 → holder → PTC → MOSFET switch → S8V9F3 3.3 V → every module`.

No charger is installed in Rev A. Remove the cell and charge it externally. The brass/silver frame is structural only, and both speaker wires remain floating.

## Structure, insulation, and color materials

| Qty | Item | Purpose / treatment |
| ---: | --- | --- |
| 2 | K&S 1.5 mm OD brass tube, 300 mm | Two video-style main loops. Fabricate/solder empty, then satin-white finish. |
| as needed | Albion Alloys NSR10 1.0 mm nickel-silver rod; K&S 1.0 mm brass rod fallback | Bare silver structural braces only—not GND. If unavailable, paint the brass fallback satin silver after soldering. |
| as needed | 26–28 AWG flexible stranded wire | Battery/regulator/amp power. Black GND and a clearly labeled white/red positive. |
| as needed | 30 AWG insulated signal wire | Short I2C/I2S/button harness, labeled at both ends. |
| as needed | Fish paper, Kapton, heat-shrink | Actual electrical insulation between every node/module/cell and metal. Paint is not insulation. |
| as needed | Thin FR4/polycarbonate sub-plates and nylon M2.5 hardware | Modules attach mechanically to insulated plates; plates attach to frame. |
| 1 | ~1 cc sealed speaker cup or Same Sky BOX-1511-1CC | Prevents front/back acoustic cancellation. |
| as needed | White PETG/ABS bezel and battery/electronics guards | White primary panels and pocket protection. Hand-cut polycarbonate is acceptable if FreeCAD/printing is unavailable. |
| as needed | Black acoustic cloth | Secondary-color speaker grille without sealing the sound path. |
| as needed | 400–1000 grit abrasive, compatible metal primer, satin-silver paint, clear coat | Apply only to the empty, degreased frame after a scrap adhesion test. |

## Tools already bought

| Purchased item | Assessment |
| --- | --- |
| X-Tronic 3020-XTS kit | Suitable starting station, holder, solder, sucker, and tweezers. Use its silicone heat surface. |
| Chip Quik CQ4LF no-clean flux pen (`B07B53LNGX`) | Correct electronics flux. Never use plumbing/acid flux. |
| BOENFU 6-inch cutters (`B07C5PM8L4`) | Suitable only if its package rating covers the brass diameter. Keep separate fine flush cutters for component leads. |
| OLFA compass cutter (`B000BK7NWC`) | Useful for paper/plastic templates; optional and incapable of cutting brass. |
| Cutting-mat listing (`B07NRQY829`) | Confirm exact item from receipt/package. Layout only; not heat-resistant. |

## Still required

- Digital multimeter with continuity, resistance, voltage, and a fused current input.
- Adjustable current-limited 0–5 V bench supply with at least 1.5 A capability.
- Safety glasses and fume extraction.
- Digital calipers, metric ruler, cardstock, and a 1:1 forming/dry-fit jig.
- Round/needle-nose pliers, small vise, jeweler's saw or mini hacksaw, and needle files.
- Pin vise/mini drill with bits matched to the final carrier, guards, and M2.5 hardware.
- Active brass soft-solder flux for the **empty frame** plus the maker's required neutralizing/cleaning supplies; keep the Chip Quik pen for electronics only.
- Breadboard, breakaway headers, test hooks/jumpers, reviewed SMD carrier adapters, and a regulated 5 V USB supply for Phase 0.
- 26–30 AWG wire stripper, fine solder wick, magnification, controlled heat-shrink tool, and strain-relief materials.
- Two-part electronics-compatible epoxy, mixing/applicator supplies, and fixtures; speaker-maker-specified foam/seal/glue materials if using BOX-1511-1CC.
- USB-C data cable. During Phase 0 connect it only to a bare,
  harness-disconnected SuperMini; cell removal alone is not rail isolation.
- Contact thermometer or thermal camera. Strongly recommended: oscilloscope or min/max logger; use only differential/isolated probing on bridge speaker outputs.
- For white guards: access to a 3D printer and FreeCAD, or thin hand-cut white polycarbonate/PETG.

## Explicitly rejected

- Any `ER14250`, `LS14250`, primary Li-SOCl₂, chemistry-ambiguous, bare, or can-soldered cell.
- The video's claimed “14250 1200 mAh” cell and frame-as-negative wiring.
- An internal USB-C charger in Rev A; it can return only with a documented power-path/charge design.
- An undocumented phone-replacement speaker, 4 Ω speaker, or speaker output tied to GND.
- Raw cell into the SuperMini `5V` pin.
- Conductive paint/foil near the ESP32 antenna or any coating on a cell, mic port, speaker diaphragm, connector, or PCB.

The creator page's “98357BGA” is a naming error; the required amplifier is **MAX98357A**.
