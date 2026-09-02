# Bill of materials and tools

> **Superseded as a shopping list.** The current purchasing list is
> [MATERIALS.md](MATERIALS.md) (Amazon-first, milestone-reviewed 2026-09-01).

> **Rev A purchasing note:** this older audit preserves the creator-faithful
> charger alternatives for reference. The current recommended build uses a
> removable protected 16340, external charger, regulated 3.3 V rail, and no
> charger inside the frame. Buy from the
> [current purchasing list, MATERIALS.md](MATERIALS.md).

This list reconciles the [project page](https://www.huyvector.org/robots-kinetic/pocket-ai-assistant), its [assembly video](https://www.youtube.com/watch?v=25RGnr407PM), the wiring diagram, and currently reachable listings. Prices and stock were checked on **2026-09-01** and can change. Creator links are affiliate/marketplace links, so verify the selected variant, dimensions, chemistry, and datasheet before ordering.

## Electronics

| Qty. | Component | Required specification | Creator listing / practical guidance |
| ---: | --- | --- | --- |
| 1 | ESP32-C3 board | ESP32-C3 **SuperMini** pin layout, native USB-C, at least 4 MB flash | [AliExpress creator link](https://s.click.aliexpress.com/e/_oCNdARN) / [Amazon creator link](https://www.amazon.com/dp/B0G5XS345R). A differently laid-out C3 board needs new wiring and mechanical dimensions. |
| 1 | OLED | 0.96-inch, 128×64, SSD1306, four-pin I2C, address `0x3c`, 3.3 V compatible | [AliExpress](https://s.click.aliexpress.com/e/_oCOMyUB) / [Amazon](https://www.amazon.com/dp/B07FK8GB8T). Select the desired display color and confirm PCB dimensions. |
| 1 | Microphone module | INMP441 I2S MEMS microphone, 3.3 V | [AliExpress](https://s.click.aliexpress.com/e/_c34pKgRt) / [Amazon](https://www.amazon.com/dp/B0FKFR1WFX). The video uses a compact round PCB; many rectangular breakouts are electrically suitable but may not fit. |
| 1 | Audio amplifier | MAX98357A mono I2S class-D breakout | [AliExpress](https://s.click.aliexpress.com/e/_c4dOCXCR) / [Amazon](https://www.amazon.com/dp/B0912CWB7Z). The page's “98357BGA” text is a naming error. |
| 1 | Speaker | Compact 4–8 Ω speaker compatible with the MAX98357A, physically sized for the frame | [AliExpress creator link](https://s.click.aliexpress.com/e/_oobS0wr) / [Amazon phone-speaker link](https://www.amazon.com/dp/B0CMT97NL7). Prefer a part with published impedance/power ratings over an electrically undocumented phone replacement. |
| 1 | Slide switch | Mini SPDT, two-position, three-pin; use common plus one throw | [AliExpress](https://s.click.aliexpress.com/e/_c3F1y5i3) / [Amazon](https://www.amazon.com/dp/B09R434VJQ). Rate must exceed the device's peak current. |
| 0–1 | Momentary action button | Normally open, connected from GPIO10 to ground if fitted | Binary inspection shows this application input, but the creator's public diagram and BOM omit it. Without it, the source build still has wake-word operation, but loses manual chat toggle and long-press Wi-Fi recovery; the onboard GPIO9 button is ROM BOOT, not this input. |
| 1 | Rechargeable cell | Documented rechargeable 1S Li-ion, nominal 3.6/3.7 V and 4.2 V termination, enough measured pulse current for Wi-Fi/audio, **factory tabs or leads**, preferably protected | The video calls out 14250. Its apparent `1200 mAh` marking is not a safe purchasing specification; see the battery decision below. The protected [Adafruit 350 mAh LiPo #4237](https://www.adafruit.com/product/4237) was $5.95 and in stock, but it does not replace a 14 mm cylindrical cell in the same bay; check the whole layout physically. Its listing does not give a usable pulse-current rating, so validate runtime under current limit. |
| 1 | USB-C Li-ion charger | Single-cell CC/CV charger with 4.2 V termination and current explicitly compatible with the chosen cell | Do not use the [creator-linked 1 A module](https://www.amazon.com/dp/B0BRXYZTWN) unchanged with a typical small 14250. The [Adafruit USB-C Micro-Lipo](https://www.adafruit.com/product/4410) defaults to a documented 100 mA, though its 24×19 mm board may require a revised layout. It is a charger, not a cell-protection board. |
| 0–1 | Cell/load protection | Required unless the selected battery pack already includes documented overcharge, overdischarge, and overcurrent protection | Adafruit pack #4237 includes a protection circuit. With a bare cell, use a documented compatible protection board and connect the load only to its protected output pads; never assume a charger also provides protection. |
| 0–1 recommended | Bulk capacitor | 100 µF low-ESR electrolytic, at least 6.3 V (10 V preferred) | Add if transient testing shows supply dip/reset or if the breakout lacks adequate reservoir capacitance. Connect `+` to amplifier `VIN` and `−` to `GND`, close to the MAX98357A. The [MAX98357A datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf) shows baseline local decoupling of 10 µF plus 0.1 µF. |

Buy at least one spare OLED, microphone, amplifier, and SuperMini if marketplace lead times are long; module dimensions and assembly quality vary.

## Battery decision — resolve this before ordering

The creator's video appears to show a `14250 1200 mAh 3.7 V` cell, removes its wrapper, and solders its can to the brass frame. Do **not** reproduce that sequence.

- A roughly 1200 mAh half-AA cell is commonly **primary** Li-SOCl₂ chemistry. For example, the manufacturer's [Saft LS 14250 datasheet](https://saft4u.saft.com/en/download_file/133c84de-f6e9-46b6-a412-fc4ed453fb5c/English) identifies it as primary and explicitly prohibits recharging and direct soldering; the [Digi-Key listing](https://www.digikey.com/en/products/detail/saft/LS14250/13930743) is a useful secondary chemistry/capacity cross-check if the PDF is unavailable.
- Capacity or a `3.7 V` label alone does not prove rechargeable chemistry or a safe charge/discharge current.
- Require a real cell datasheet stating rechargeable Li-ion chemistry, 4.2 V termination, maximum charge current, and maximum continuous/pulse discharge current. Reject `ER14250`, `LS14250`, 3.6 V Li-SOCl₂, or any listing that does not state chemistry clearly.
- Use factory-welded tabs/leads or a suitable holder, leave the wrapper intact, insulate both ends with fish paper/Kapton/heat-shrink, and add strain relief. Never make the exposed brass frame the cell terminal.
- Set the charger current no higher than the cell maker's recommendation. When no better documented value is available, the [Adafruit charger](https://www.adafruit.com/product/4410) provides a conservative 100 mA default; do not close its 500 mA jumper for a small cell unless the cell datasheet permits it.
- The simple charger topology shown does not provide load sharing. Keep the assistant switched **off while charging** unless you deliberately substitute a documented power-path charger.

The 14250 geometry is optional. A protected 1S LiPo pack with leads and a documented pulse rating is a sound substitution if it fits a nonconductive enclosure; dry-fit it before building the frame.

For a safer first charging prototype, use the [Adafruit 350 mAh protected pack](https://www.adafruit.com/product/4237) and [100 mA USB-C charger](https://www.adafruit.com/product/4410), observing connector polarity. Their checked combined price is $11.90. This validates a conservative charge pairing, not Wi-Fi/audio pulse capability; measure voltage sag, peak current, and temperature under current-limited bench power before accepting it as the runtime supply. The flat pack cannot occupy the original cylindrical-cell bay directly, and overall fit needs a physical layout or CAD check.

## Structural material and consumables

| Qty. | Item | Specification / source | Notes |
| ---: | --- | --- | --- |
| 2 lengths | Brass tube | 1.5 mm outside diameter. [K&S four-piece, 300 mm stock](https://ksmetals.com/products/br225mm-1h) was $7.99 and in stock; [creator link](https://s.click.aliexpress.com/e/_c3ANKyC7). | The project page explicitly asks for two. Deburr after cutting. |
| As needed | Brass rod/wire | Video says 1.0 mm **brass** wire, despite the page saying copper. [K&S five-piece, 300 mm round rod](https://ksmetals.com/products/brrmet-1) was $5.99; [creator link](https://s.click.aliexpress.com/e/_c4pah9Tz). | The creator's current Amazon result is square brass, not round copper. Round rod best matches the video. |
| As needed | Hookup wire | 26–28 AWG flexible stranded wire for short battery/amplifier power paths; 30 AWG is suitable for signals | Size the power conductors from measured peak current and length. Do not rely on a conductive frame for signal wiring or battery return. |
| As needed | Electrical insulation | Fish paper, Kapton tape, heat-shrink tubing | Required around the cell, positive rail, module backs, frame crossings, and solder joints that can move. |
| As needed | Adhesive | Electronics-safe low-temperature hot glue and cyanoacrylate used sparingly | The video glues the OLED and speaker. Keep glue away from the microphone port, switch, connectors, and hot components. Prefer removable mechanical retention where practical. |
| As needed | Cleaning/deburring | Fine needle file, 400–800 grit abrasive, 90%+ IPA, lint-free swabs | Clean brass before fluxing; remove sharp edges and flux residue according to its data sheet. |

The video shows approximate 40 mm and 15 mm template marks, but it does not establish a dimensioned width, height, or depth (the 15 mm mark may be centerline-to-edge). Derive the finished geometry from the purchased parts on cardstock or in CAD and dry-fit everything before cutting brass.

## Your preliminary tool list, normalized

| Required tool | Selected replacement | Checked price/status | Decision |
| --- | --- | --- | --- |
| Soldering station | [X-Tronic 3020-XTS 75 W](https://xtronicusa.com/X-Tronic-Model-3020-XTS-LED-Soldering-Station-p74220205) | $54.80; in stock; free contiguous-US shipping | Suitable. Includes holder, two helping hands, small silicone heat mat, brass cleaner, sponge, and 50 g lead-free rosin-core solder. |
| Solder wire | Included Sn99.3/Cu0.7 lead-free rosin-core, 50 g | Included | Adequate. Use electronics flux and expect a higher working temperature than leaded solder. |
| Joint flux | [Chip Quik no-clean flux pen, Adafruit #3468](https://www.adafruit.com/product/3468) | $7.95; in stock | Suitable. The station's tip-cleaning compound is not joint flux. Never use acid/plumbing flux. |
| Iron stand / clamp | Included with X-Tronic | Included | Suitable; the helping hands hold the frame/modules, while the stand holds the hot iron. |
| Desoldering pump | [Adafruit #148](https://www.adafruit.com/product/148) | $5.00; in stock | Useful, but optional for initial assembly. Add fine solder wick for tiny pads. |
| Mini cutter | [CHP170 flush cutters, Adafruit #152](https://www.adafruit.com/product/152) | $7.25; in stock | Good for leads and hookup wire. Do not damage them on 1 mm brass; use a saw or cutter rated for brass. |
| Cutting pad | [Fiskars 12×18 self-healing mat](https://www.walmart.com/ip/Fiskars-12-x-18-Double-Sided-Rotary-Cutting-Mat-Gray/24548295) | $11.27; delivery/pickup varies | Fine for layout and craft cutting, **not heat resistant**. Solder only over the included silicone mat. |
| Circle cutter | [OLFA CMP-1](https://olfaproducts.com/products/olfa-cmp-1-compass-cutter-7) | $10.09; available to add to cart | Optional; no circle-cutting step is apparent in this build. |

The **preliminary selected-tool subtotal is $96.36 before tax/shipping**, including the optional pump and circle cutter and counting included items at $0. It excludes electronics, brass, battery/charger, consumables, and the missing safety/test tools below.

## Missing tools you should add

### Required for a safe build

- Digital multimeter with continuity, DC voltage, resistance, and a suitably fused current range. Learn the current-jack/range setup; never place a meter in current mode directly across a cell or supply.
- Current-limited bench supply covering the intended 1S-cell range, or an equivalently protected/current-limited source. The staged power test requires it before installing the cell.
- Safety glasses and active fume extraction or a well-ventilated soldering area.
- Fine needle-nose and round-nose pliers for forming/positioning brass.
- Fine-tooth jeweler's saw, mini hacksaw, or cutters explicitly rated for 1 mm brass; a small file for deburring.
- Wire stripper suitable for 26–30 AWG, fine tweezers, metric steel ruler or calipers, cardstock/paper, and a fine marker.
- USB-C **data** cable for the ESP32-C3 plus a separate suitable USB-C cable/source for the charger. A known-good USB-A-to-C cable avoids some clone-board C-to-C CC incompatibilities; otherwise confirm C-to-C enumeration first.
- Fine solder wick; the pump is awkward on small castellated/breakout pads.
- Heat-shrink/Kapton/fish paper and a heat gun or controlled hot-air source for heat-shrink.
- Low-temperature hot-glue gun if using the listed hot-glue consumable.
- Compatible 2–3 mm chisel tip for brass-frame joints if the station package does not include one; retain a fine tip for module pads.
- A nonconductive finished enclosure or robust guards/insulation. An energized bare brass sculpture is not suitable for carrying loose in a pocket with keys or coins.

### Strongly recommended for bring-up

- Breadboard or test leads to verify the display, microphone, amplifier, and firmware before free-form assembly.
- Magnification for inspecting module pads and fine-pitch solder joints.
- ESD mat/wrist strap and spare compatible modules.
