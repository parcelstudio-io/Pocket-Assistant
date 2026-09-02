# Final materials decision — R1 build release

> **RELEASED FOR PURCHASE AND STAGED ASSEMBLY — 2026-09-02 final audit.**
> This document supersedes the R0 qualification release (which held the power
> system at NO-GO behind a Pololu buck-boost/fuse/16340 chain). The final audit
> found that architecture safe on paper but **triple the reference device's
> volume and indefinitely blocked** — the opposite of the project goal, which is
> a compact pocket device faithful to the
> [reference build](https://www.huyvector.org/robots-kinetic/pocket-ai-assistant)
> and its [video](https://www.youtube.com/watch?v=25RGnr407PM).
> R1 returns to the creator's power topology and makes it safe with documented
> parts and hard procedural rules, instead of replacing it.

**GO:** the complete R1 cart below, breadboard bring-up, frame fabrication
after the cardstock dry-fit closes, and staged final assembly per
[BUILD_GUIDE.md](BUILD_GUIDE.md).
**Still gated:** first cell connection (after the bench power test), first
attended charge, and pocket carry (after the acceptance checks in
[edu/06_ACCEPTANCE_TESTS.md](../edu/06_ACCEPTANCE_TESTS.md)).

## Quick shopping list — one line per item

Prices checked 2026-09-01/02; re-verify in the cart. Rationale for every line
is in the detailed tables further down.

### Adafruit (one order)

- [ ] 2 × Battery — protected 500 mAh LiPo **#1578** — $7.95 ea — <https://www.adafruit.com/product/1578>
- [ ] 1 × Charger — USB-C Micro-Lipo **#4410** — $5.95 — <https://www.adafruit.com/product/4410>

### DigiKey

- [ ] 2 × Speaker — Same Sky **CES-20134-088PM** 8 Ω 0.8 W enclosed — ~$8 ea — <https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309>

### Amazon — electronics

- [ ] 1 × ESP32-C3 SuperMini 3-pack — $12.97 — <https://www.amazon.com/dp/B0G5XS345R> *(or 10-pack — $28.99 — <https://www.amazon.com/dp/B0F888JQ91>)*
- [ ] 1 × OLED 0.96" SSD1306 white I²C 5-pack — $14.99 — <https://www.amazon.com/dp/B09T6SJBV5>
- [ ] 1 × INMP441 microphone 5-pack — $11.99 — <https://www.amazon.com/dp/B092HWW4RS>
- [ ] 1 × MAX98357A amplifier 3-pack — $9.49 — <https://www.amazon.com/dp/B0CDWXZZCH>
- [ ] 1 × Tact button kit (6×6 mm + caps) — $15.99 — <https://www.amazon.com/dp/B0FHW6HMG4>
- [ ] 1 × SPDT slide switch 25-pack — ~$8 — <https://www.amazon.com/dp/B09R434VJQ>
- [ ] 1 × JST-PH **2.0 mm** pigtail set (any Prime listing; caliper the pitch) — ~$7
- [ ] 1 × Resistor kit (10 k / 100 k) — $6.39 — <https://www.amazon.com/dp/B0F4P352BB>
- [ ] 1 × Ceramic capacitor kit (100 nF / 10 µF) — $14.99 — <https://www.amazon.com/dp/B07P7HRGT9>
- [ ] 1 × Electrolytic capacitor kit (220 µF) — $9.99 — <https://www.amazon.com/dp/B0C1VBXCQM>

### Amazon — frame, insulation, wire

- [ ] 1 × Fish paper 0.2 mm — $15.88 — <https://www.amazon.com/dp/B0GZVDKBBS> *(slowest item — order first)*
- [ ] 1 × Kapton tape 4-pack — $9.99 — <https://www.amazon.com/dp/B072Z92QZ2>
- [ ] 1 × Heat-shrink kit — $9.99 — <https://www.amazon.com/dp/B08N4W4K9X>
- [ ] 1 × 30 AWG silicone wire kit — $13.99 — <https://www.amazon.com/dp/B073RDGTPB>
- [ ] 1 × 26 AWG silicone wire — $15.59 — <https://www.amazon.com/dp/B07G2LRX68>
- [ ] 1 × Brass tube K&S #9831 (1.5 mm OD ×4) — $7.80 — <https://www.amazon.com/dp/B005WPAW9M> *(or direct: <https://ksmetals.com/products/br225mm-1h>)*
- [ ] 1 × Brass rod K&S #9861 (1.0 mm ×5) — $8.59 — <https://www.amazon.com/dp/B005WPB7YG> *(or direct: <https://ksmetals.com/products/brrmet-1>)*

### Tools still to buy (skip anything you own)

- [ ] Multimeter KAIWEETS HT118A — $41.23 — <https://www.amazon.com/dp/B08BL288LW>
- [ ] Bench supply (current-limited) PS305H — $47.49 — <https://www.amazon.com/dp/B0BN1F6CGZ>
- [ ] Calipers Neiko 01407A — $27.99 — <https://www.amazon.com/dp/B000GSLKIW>
- [ ] Jeweler's saw + blades — $24.95 — <https://www.amazon.com/dp/B06XPSLS6N>
- [ ] Round/chain-nose pliers — ~$12 — <https://www.amazon.com/dp/B0B8QBVXXR>
- [ ] Wire strippers 30–20 AWG — $12.87 — <https://www.amazon.com/dp/B00FZPHMUG>
- [ ] Safety glasses — $14.99 — <https://www.amazon.com/dp/B016KZ1ZPM>
- [ ] Brass flux (frame only) Harris SCLF4 — $12.85 — <https://www.amazon.com/dp/B0015DWPV8>
- [ ] 63/37 solder — $11.69 — <https://www.amazon.com/dp/B076QF1Y85> *(only if the X-Tronic kit's roll turns out to be lead-free)*
- [ ] Breadboard + jumpers, USB-**A**-to-C data cable, 2.54 mm header strip — ~$23 (any Prime listings)
- [ ] Consumables: hot-glue gun, needle files, 400–800 grit, IPA + swabs + baking soda, solder wick, heat gun, ESD strap, rule/square/cardstock — ~$60–80

**Total: ~$530 + NYC tax** (≈$240 parts, ≈$290 tools/consumables).

## The audit question, answered

*Can the materials be configured, soldered, and assembled into a compact
pocket AI assistant that talks over Wi-Fi?* **Yes — with the R1 part set
below.** The evidence:

- **The reference device exists and works** with exactly these part classes:
  ESP32-C3 SuperMini + SSD1306 OLED + INMP441 + MAX98357A + 8 Ω speaker +
  1S Li-ion + Type-C charge board + slide switch, free-formed in a brass frame.
- **The firmware is proven buildable.** The source port compiles reproducibly
  (two identical clean builds, digest recorded in
  [source-build.json](../firmware/source-build.json)) and its pin/rate contract
  is legal per every datasheet involved (see
  [ASSEMBLY_EVIDENCE.md](ASSEMBLY_EVIDENCE.md)).
- **Every electrical interface closes on paper.** All modules are 3.3 V-logic
  compatible; the MAX98357A accepts 2.5–5.5 V so it runs happily from the raw
  cell; the SuperMini's onboard LDO makes 3.3 V from the cell for the MCU,
  OLED, and mic — the same arrangement the working reference uses.
- **The two genuinely dangerous things in the video are replaced, not
  reproduced**: the mystery `14250 1200 mAh` cell soldered by its can to the
  frame (replaced by a documented **protected** pack with a factory connector),
  and the frame-as-ground-bus wiring (the R1 frame is electrically floating).

What remains honest: `hardware_tested: false` — nothing in this workspace has
run on a physical board yet. That is why the build procedure is bench-first:
every part is proven on a breadboard, and the power chain from a
current-limited supply, before anything is soldered into the frame.

## R1 architecture

```text
protected 1S LiPo pack (protection PCM inside the pack, factory JST-PH lead)
  ↔ USB-C charge board, in the frame (charging port, like the video)
  → SPDT slide switch in the protected positive lead
  → switched battery bus (3.0–4.2 V)
      → ESP32-C3 SuperMini "5V" pin → onboard LDO → 3.3 V
            → OLED (I2C), INMP441 (I2S)
      → MAX98357A VIN (rated 2.5–5.5 V, so the raw cell rail is in-spec)
          + 220 µF bulk capacitor at the amp's VIN/GND (recommended)

speaker: MAX98357A OUT+/OUT− only — floating BTL pair, never grounded
brass frame: structure only — never GND, never a power or signal conductor
```

Deliberate deviations from the video, all safety-driven, all kept from the
earlier reviews:

1. **Protected pack, never a bare/mystery cell.** The video's `14250 1200 mAh`
   is almost certainly a primary Li-SOCl₂ cell mislabelled as rechargeable
   (see [BOM.md](BOM.md)); soldering to any cell's can remains **REJECT**.
2. **Frame floating.** All returns go through wires; Kapton/fish-paper
   insulation where conductors cross brass.
3. **Source firmware contract**: mic data on **GPIO4** (not the vendor GPIO8),
   16 kHz audio, OLED probed at 0x3C/0x3D. Vendor-image wiring (GPIO8) is
   documented separately and never mixed with this map.
4. **Charge current matched to the cell** (100→500 mA documented, not an
   unconditioned 1 A module).
5. **Hard rules** (below) for USB and charging states, since this simple
   topology has no load-sharing or source-mux hardware.

### The five hard rules

These are the whole price of the compact topology. They go on the bench card
and in every procedure:

1. **Slide switch OFF before plugging in either USB-C port** (SuperMini or
   charger), and never both USB ports at once. Most SuperMini clones tie the
   `5V` pin straight to USB VBUS; with the switch on, USB would meet the cell.
2. **Device OFF while charging.** The charge board has no load sharing; a load
   confuses CC/CV termination.
3. **First charge attended**, on a non-flammable surface, cell cool to the
   touch throughout; verify 4.20 ± 0.05 V termination.
4. **Never solder to, puncture, unwrap, or heat a cell.** The pack connects
   only by its factory lead. Cell disconnected (JST unplugged) for all
   soldering, painting, cleaning, and flashing.
5. **Stop conditions:** swelling, heat, odor, damaged insulation → disconnect
   if safe, move away, do not build on.

## R1 bill of materials — the released cart

Verification legend: **✅** = listing/product page fetched and specs read
during this audit cycle · **⚠️** = verify stated property on arrival.

### Electronics (digital + audio)

| Role | Released part | Why | Check |
| --- | --- | --- | --- |
| Controller | Plain **ESP32-C3 SuperMini**, USB-C, ≥4 MB flash — 3-pack (e.g. Amazon [B0G5XS345R](https://www.amazon.com/dp/B0G5XS345R) or [B0F888JQ91](https://www.amazon.com/dp/B0F888JQ91) 10-pack) | Reference layout; matches firmware/CAD | ⚠️ gate every board with `esptool flash_id` ≥ 4 MB; plain variant only (one blue LED, no U.FL, no WS2812) |
| Display | **0.96" SSD1306 128×64 I2C, white, 4-pin** — 5-pack (e.g. [B09T6SJBV5](https://www.amazon.com/dp/B09T6SJBV5)) | Creator-faithful, thin, 3.3 V, 0x3C (firmware also probes 0x3D) | ⚠️ read silkscreen pin order — vendors ship GND-VCC and VCC-GND variants |
| Microphone | **INMP441 I2S MEMS** breakout — 5-pack (e.g. [B092HWW4RS](https://www.amazon.com/dp/B092HWW4RS)) | Creator's exact mic; 64-SCK I2S at 1.024 MHz is in-spec; 3.3 V | `L/R` → GND (left slot). Alternate: Adafruit [#6049 ICS-43434](https://www.adafruit.com/product/6049) (controlled board, `SEL` → GND) — either works with the source build |
| Amplifier | **MAX98357A I2S class-D** breakout — HiLetgo 3-pack ([B0CDWXZZCH](https://www.amazon.com/dp/B0CDWXZZCH)) or Adafruit [#3006](https://www.adafruit.com/product/3006) | Creator's amp; 2.5–5.5 V VIN covers the cell rail | Stock SD ≈ 0.30 V = mono mix = full amplitude (see [edu/04-audio.md](../edu/04-audio.md)); GAIN floating = 9 dB |
| Speaker | **Same Sky CES-20134-088PM** — 8 Ω, 0.8 W, factory-enclosed, ~20 × 16 × 4.9 mm, bare leads ([DigiKey 2223-CES-20134-088PM-ND](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309)) ×2 | Sealed rear cavity solves the hardest acoustic problem at phone-speaker size | Software volume limit keeps average ≤ 0.8 W. Fallback: video-style phone speaker (undocumented specs — A/B it) |
| Action button | 6×6 mm tact switch (+cap), from any kit (e.g. [B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4)) | GPIO10 → GND, active low; chat toggle + long-press Wi-Fi reset | Onboard GPIO9 is ROM BOOT, not this input |

### Power — the audit's headline change

| Role | Released part | Why | Check |
| --- | --- | --- | --- |
| Cell | **Adafruit #1578** — 3.7 V 500 mAh LiPo, **protected** (overcharge, 3.0 V over-discharge cutout, short protection), JST-PH lead, 29 × 36 × 4.75 mm, $7.95 ✅ verified in stock 2026-09-02 | Documented protection + connector; half the volume of the withdrawn 16340+holder stack; ~3 h estimated idle-listening runtime | ⚠️ no thermistor — charge ≤ 500 mA per its own page. Smaller alternate: [#4237](https://www.adafruit.com/product/4237) 350 mAh protected |
| Charger (in frame) | **Adafruit #4410** — USB-C Micro-Lipo, 24 × 19 × 7.2 mm, 100 mA default / 500 mA via solder jumper, 4.2 V termination, JST battery port + 5V/GND/BAT breakout pads, $5.95 ✅ verified in stock 2026-09-02 | Documented current, right size, JST mates the pack directly; mounts in the frame like the video's Type-C board | Leave 100 mA for first charges; close the jumper (500 mA = 1C) only after a clean attended cycle. Creator-faithful alternate: TP4056-class USB-C module **only if** it carries DW01A+FS8205 protection and its 1.2 kΩ `Rprog` is replaced (3 kΩ ≈ 400 mA) |
| Power switch | **Mini SPDT slide** (SS12D00 class), e.g. from 25-pack [B09R434VJQ](https://www.amazon.com/dp/B09R434VJQ) | Creator's part; in the protected positive lead it is a true battery break | ⚠️ measure contact drop < 50 mV at 0.5 A on the chosen sample; average load ~0.15–0.25 A, transients < 1 A ms-scale |
| Bulk + local caps | 220 µF electrolytic at amp VIN; 100 nF + 10 µF ceramics at each module supply (e.g. [B0C1VBXCQM](https://www.amazon.com/dp/B0C1VBXCQM) + [B07P7HRGT9](https://www.amazon.com/dp/B07P7HRGT9)) | Wi-Fi + class-D transients on a shared cell rail | Fit the 220 µF from the start; the reference gets away without it, you might not |
| Pull/pulldown resistors | 10 kΩ (GPIO2 pull-up, button pull-up), 100 kΩ (GPIO4 pulldown) from any metal-film kit ([B0F4P352BB](https://www.amazon.com/dp/B0F4P352BB)) | Strap-pin hygiene per Espressif checklist | — |
| JST splitter/pigtail | JST-PH 2.0 mm pigtail pair | Taps the load off the pack↔charger connection without soldering to the pack | ⚠️ genuine JST-PH is 2.0 mm pitch — the old "2.5 mm JST-PH" claim was wrong |

**What the pack's PCM covers:** overcharge, over-discharge (3.0 V), and output
shorts — so no separate fuse, P-FET, or UVLO module is fitted. The LDO-direct
rail means the device browns out as the cell approaches the 3.0 V cutout
instead of regulating to the last millivolt: identical behavior to the
reference, and acceptable for R1. If bench testing shows resets during Wi-Fi
bursts near end-of-discharge, the fix is the 220 µF bulk cap and, failing
that, a bigger pack — not a return to the withdrawn converter chain.

### Frame, insulation, consumables

| Role | Released part | Note |
| --- | --- | --- |
| Frame tube | **K&S #9831** 1.5 mm OD × 0.225 mm wall brass, 4× 300 mm ([ksmetals](https://ksmetals.com/products/br225mm-1h)) | The reference's exact stock. Cut with jeweler's saw only; deburr every end |
| Frame rod | **K&S #9861** 1.0 mm brass rod, 5× 300 mm ([ksmetals](https://ksmetals.com/products/brrmet-1)) | Braces/posts; telescopes in the tube |
| Cell barrier | Fish paper 0.2 mm ([B0GZVDKBBS](https://www.amazon.com/dp/B0GZVDKBBS)) or Formex GK-10 | Flame-rated layer under/around the pack — mandatory |
| Local insulation | Kapton tape ([B072Z92QZ2](https://www.amazon.com/dp/B072Z92QZ2)), heat-shrink kit ([B08N4W4K9X](https://www.amazon.com/dp/B08N4W4K9X)) | Module backs, frame crossings, every splice |
| Wire | 26 AWG silicone (power/speaker, [B07G2LRX68](https://www.amazon.com/dp/B07G2LRX68)) + 30 AWG (signals, [B073RDGTPB](https://www.amazon.com/dp/B073RDGTPB)) | Speaker pair twisted; signals short |
| Adhesive | Electronics-safe hot glue + sparing CA | The video's method; keep away from mic port, switch, USB |
| Finish (optional) | Raw brass like the reference, or the white system in [edu/05_COLOR_AND_FINISH.md](../edu/05_COLOR_AND_FINISH.md) | Paint is decoration, never insulation |

### Tools

The owned X-Tronic 3020-XTS kit, CQ4LF flux pen, BOENFU cutters, WORKLION mat,
and OLFA cutter stand (see [MATERIALS.md](MATERIALS.md) for the
reconciliation). Still required: multimeter, current-limited bench supply
(the one non-negotiable instrument — it stands in for the cell during every
power test), calipers, jeweler's saw + pliers, wire strippers 26–30 AWG,
solder wick, heat gun, safety glasses, ventilation. 63/37 or verified
electronics solder for boards; hard-solder/flux for the empty frame only,
washed and neutralized before any electronics exist near it.

## Size and runtime targets

Provisional envelope **≈ 45 × 32 × 20 mm** plus the USB-C port projections —
set by the OLED face (27.5 × 27.8 mm), the pack (29 × 36 mm laid flat as the
back plane), and the charger board edge-mounted for port access. That is
video-scale, and roughly half the volume of the withdrawn R0 layout. The
number is a **target, not fit evidence**: the cardstock dry-fit with real
parts governs, and `cad/fitcheck.py` must be regenerated from measured parts
before brass is cut (the existing FITCHECK_REPORT models the withdrawn
architecture and is stale).

Runtime estimate: ~130–150 mA average from the cell while idle-listening →
**≈ 3 h** on 500 mAh. An estimate until measured (acceptance test 8.4).

## Withdrawn by this audit (R0 → R1)

Retained as history in the linked files; none of it is in the R1 cart.

| R0 item | R1 status | Reason |
| --- | --- | --- |
| Pololu #2873 buck-boost + #2810 MOSFET switch + PICO fuse chain | **WITHDRAWN** | Solved a marginality the reference proves survivable, at 3× device volume and an unbounded test program. The protected pack + rules cover the same failure classes at pocket scale |
| Nitecore NL169 16340 + MPD BH123A holder + external charger | **WITHDRAWN** | Cylindrical cell + holder is the single largest volume item; NL169's protection specs were never documented anyway. The Adafruit pack documents what the NL169 page does not |
| Oscilloscope/current-probe/load-step instrumentation gates | **RELAXED to recommended** | Right for a production release; disproportionate for a one-off that the bench supply, DMM, and staged bring-up adequately screen |
| 60 × 45 × 33 mm CAD envelope and 162-rule fitcheck | **STALE** | Models the withdrawn architecture; regenerate from measured R1 parts |
| `14250 1200 mAh` video cell; soldering to any cell | **REJECT (unchanged)** | Chemistry unproven, likely primary Li-SOCl₂; both remain prohibited |
| Frame as GND/power/speaker conductor | **REJECT (unchanged)** | Energized exposed structure in a pocket |
| Parallel PPTCs, unreviewed P-FET pairs, adjustable-output regulators, boost-only/buck-only converters | **REJECT (unchanged)** | The R0 analysis of these stands |
| "JST-PH 2.5 mm" | **REJECT (unchanged)** | JST-PH is 2.0 mm pitch |

## Release gates that remain

1. **Bench gate (before frame work):** full stack on a breadboard from USB +
   bench supply — flash, OLED at 0x3C/0x3D, mic capture, amp playback, one
   full cloud round trip; power chain from the current-limited supply swept
   3.3 → 4.2 V under Wi-Fi + audio load with no reset. Speaker A/B if using
   the phone-speaker fallback.
2. **Fit gate (before cutting brass):** cardstock 1:1 dry-fit with the real
   parts closes; every port, button, switch, mic hole, and the pack's removal
   path reachable.
3. **Unpowered gate (after mounting):** frame isolated from every net; no
   BTL lead grounded; polarity verified at the JST before first connection.
4. **Cell gate:** pack connected only after gates 1–3; first charge attended
   per the hard rules.
5. **Pocket gate:** acceptance checks in
   [edu/06_ACCEPTANCE_TESTS.md](../edu/06_ACCEPTANCE_TESTS.md) pass before the
   device rides in a pocket.

## Primary references

- [Reference build page](https://www.huyvector.org/robots-kinetic/pocket-ai-assistant) · [assembly video](https://www.youtube.com/watch?v=25RGnr407PM)
- [Firmware board configuration](../firmware/src/boards/pocket-wall-e-c3/config.h) · [source-build evidence](../firmware/source-build.json)
- [Adafruit #1578 protected 500 mAh pack](https://www.adafruit.com/product/1578) · [#4410 USB-C Micro-Lipo charger](https://www.adafruit.com/product/4410)
- [MAX98357A datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf) · [INMP441 datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf)
- [Same Sky CES-20134-088PM](https://www.sameskydevices.com/product/audio/speakers/miniature-%2810-mm~40-mm%29/ces-20134-088pm)
- [ESP32-C3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf)
- Procedures: [BUILD_GUIDE.md](BUILD_GUIDE.md) · [WIRING_AND_ASSEMBLY.md](WIRING_AND_ASSEMBLY.md) · [edu/04_ASSEMBLY_STEP_BY_STEP.md](../edu/04_ASSEMBLY_STEP_BY_STEP.md)

## Release verdict

**GO for the complete R1 cart and the staged build procedure. The cell
connects only after the bench gate; charging and pocket carry only after
their gates.** The device this releases is a compact, video-faithful brass
pager running the corrected 16 kHz source firmware — with a protected,
removable, never-soldered power system and a frame that carries no current.
