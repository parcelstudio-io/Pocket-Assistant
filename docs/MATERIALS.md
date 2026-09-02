# Archived material list — Claude R1 compact-build proposal

> **SUPERSEDED; DO NOT ORDER OR BUILD FROM THIS FILE.** Its #1578 cell,
> direct-to-SuperMini rail, generic slide switch, and software-only speaker
> assumptions did not pass the independent power/digital audit. The only
> current purchase authority is the reversible Phase 0 list in
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md). The original
> R1 list below is retained for provenance and Claude's comparison; labels such
> as “released” or “current” below are historical claims, not instructions.

> **Original R1 proposal text follows.** It described a protected LiPo pack +
> in-frame USB-C charger + generic slide switch, with no qualified regulator,
> fuse, or hardware USB-source isolation.

Listings were live-checked on **2026-09-01/02**. Prices, sellers, and stock
move; re-check in the cart. Where a claim could not be confirmed from the
listing it says so, with the measurement that settles it on arrival.

Legend: **✅ confirmed** = listing/product page fetched and specs read ·
**⚠️ measure** = a spec the listing does not publish; verify on arrival.

---

## 1 · Electronics

| Role | Part | Price | Spec check |
| --- | --- | --- | --- |
| **MCU** | ESP32-C3 SuperMini — [B0F888JQ91](https://www.amazon.com/dp/B0F888JQ91) 10-pack $28.99 (photo-confirmed `FH4` 4 MB marking) or [B0G5XS345R](https://www.amazon.com/dp/B0G5XS345R) 3-pack | $12.97–28.99 | ✅ USB-C, no U.FL, single blue LED on GPIO8. ⚠️ Gate every board with `esptool flash_id` ≥ 4 MB — the 3.54 MB image makes a 2 MB clone a hard stop. Plain variant only (a "Plus" with WS2812 on GPIO8 breaks this pin map) |
| **Display** | 0.96" SSD1306 128×64 I²C, **white**, 5-pack — [B09T6SJBV5](https://www.amazon.com/dp/B09T6SJBV5) (Hosyond) | $14.99 / 5 | ✅ SSD1306 (not SH1106), 4-pin I²C, 3.3–5 V, address 0x3C (firmware probes 0x3C then 0x3D). ⚠️ **Read the silkscreen pin order** — vendors ship GND-VCC-SCL-SDA *and* VCC-GND-SCL-SDA |
| **Microphone** | INMP441 I²S MEMS, 5-pack — [B092HWW4RS](https://www.amazon.com/dp/B092HWW4RS) | $11.99 / 5 | ✅ Ships from and sold by Amazon. 3.3 V, I²S, `L/R` → GND = left slot. The creator's exact mic; in-spec at the build's 1.024 MHz bit clock. Controlled-board alternate: Adafruit [#6049 ICS-43434](https://www.adafruit.com/product/6049) (`SEL` → GND) |
| **Amplifier** | MAX98357A I²S class-D, 3-pack — [B0CDWXZZCH](https://www.amazon.com/dp/B0CDWXZZCH) (HiLetgo) | $9.49 / 3 | ✅ Adafruit-lineage clone, 2.5–5.5 V — runs from the raw cell rail. Stock SD ≈ 0.30 V = (L+R)/2 mono mix at **full amplitude** ([why](../edu/04-audio.md#exact-module-channel-and-gain-configuration)). Or genuine Adafruit [#3006](https://www.adafruit.com/product/3006) |
| **Speaker — primary** | Same Sky **CES-20134-088PM** 8 Ω 0.8 W factory-enclosed, ~20 × 16 × 4.9 mm — [DigiKey 2223-CES-20134-088PM-ND](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309) ×2 | ~$8 ea | ✅ Manufacturer-controlled sealed enclosure — removes the hardest acoustic step at phone-speaker size. Keep software volume so average power ≤ 0.8 W |
| **Speaker — fallback** | Video-style phone/mini speaker (e.g. pre-boxed 8 Ω 4-pack [B0BHST51PQ](https://www.amazon.com/dp/B0BHST51PQ)) | $9.99 / 4 | ⚠️ No published specs — measure impedance and A/B against the primary at 1 m before it earns a frame slot |
| **Action button** | 6×6 mm tact + caps, 420 pc — [B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4) | $15.99 | ✅ Multiple stem heights and cap colours. GPIO10 → GND, active low |

## 2 · Power — the R1 chain (read [the power-chain lesson](../edu/07-the-power-chain.md))

The chain is: **protected pack ↔ charger board → slide switch → SuperMini
`5V` + amp `VIN`**. No buck-boost, no fuse pair, no P-FETs — the pack's
internal protection plus procedural rules were claimed to cover R1; the
[current power architecture](FINAL_MATERIALS_FOR_REVIEW.md#candidate-power-architecture)
withdraws that claim and must control instead.

| Role | Part | Price | Spec check |
| --- | --- | --- | --- |
| **Cell** | **Adafruit #1578** — 3.7 V 500 mAh LiPo, protected, JST-PH, 29 × 36 × 4.75 mm — [adafruit.com/product/1578](https://www.adafruit.com/product/1578) ×2 (one spare) | $7.95 ea | ✅ Verified in stock 2026-09-02. Protection PCM: overcharge, 3.0 V over-discharge cutout, short protection. Charge ≤ 500 mA (no thermistor). Smaller alternate: [#4237](https://www.adafruit.com/product/4237) 350 mAh protected, $5.95 |
| **Charger (mounts in frame)** | **Adafruit #4410** — USB-C Micro-Lipo, 24 × 19 × 7.2 mm — [adafruit.com/product/4410](https://www.adafruit.com/product/4410) | $5.95 | ✅ Verified in stock 2026-09-02. 100 mA default; 500 mA by closing the front solder jumper (do this only after a clean attended first cycle). 4.2 V termination, JST battery port, 5V/GND/BAT breakout pads for the load tap |
| ↳ creator-faithful alternate | Generic TP4056-class **USB-C** module | ~$1–2 ea | ⚠️ Only a variant with **DW01A + FS8205** protection ICs, and only after replacing its 1.2 kΩ `Rprog` (1 A) with 3 kΩ (≈400 mA). If you won't do the resistor swap, buy the #4410 |
| **Power switch** | Mini SPDT slide, SS12D00 class, 25-pack — [B09R434VJQ](https://www.amazon.com/dp/B09R434VJQ) | ~$8 | In the protected positive lead = true battery break; fails open = off. ⚠️ Measure contact drop < 50 mV at 0.5 A on the sample you fit (average load ~0.15–0.25 A) |
| **JST-PH pigtails** | JST-PH **2.0 mm** male+female pigtail set | ~$7 | Taps the load off the pack↔charger connection without soldering to the pack. ⚠️ Caliper the pitch: genuine PH is 2.0 mm |
| **Resistors** (10 k, 100 k) | 1000-pc metal film kit — [B0F4P352BB](https://www.amazon.com/dp/B0F4P352BB) | $6.39 | GPIO2 pull-up, GPIO4 pull-down, button pull-up |
| **Ceramic caps** (100 nF, 10 µF) | BOJACK 650-pc — [B07P7HRGT9](https://www.amazon.com/dp/B07P7HRGT9) | $14.99 | Local decoupling at each module. ⚠️ Dielectric unpublished; if warm-derated, parallel extra 10 µF at the amp |
| **Bulk cap** 220 µF | ALLECIN kit — [B0C1VBXCQM](https://www.amazon.com/dp/B0C1VBXCQM) | $9.99 | At amp VIN/GND — the bass reservoir and Wi-Fi-burst buffer on the shared cell rail |

**Withdrawn power parts (do not buy):** XL63070/63802/63020 converter modules,
RUEF110 PPTC pairs, AO3401A/DMG2301L P-FETs + adapters, service-jumper
hardware, Nitecore NL169/16340 cells, CR123A holders, XTAR/Nitecore external
chargers. See the [current audit summary](FINAL_MATERIALS_FOR_REVIEW.md#independent-audit-summary-claude-must-disposition).

## 3 · Frame, finish, wire, insulation

| Role | Part | Price | Notes |
| --- | --- | --- | --- |
| Brass tube 1.5 mm OD × 0.225 wall × 300 mm ×4 | K&S #9831 — [B005WPAW9M](https://www.amazon.com/dp/B005WPAW9M) or [ksmetals direct](https://ksmetals.com/products/br225mm-1h) | $7.80 | ✅ The reference's stock. ⚠️ The ASIN is a variation parent — caliper the OD on arrival |
| Brass rod 1.0 mm × 300 mm ×5 | K&S #9861 — [B005WPB7YG](https://www.amazon.com/dp/B005WPB7YG) | $8.59 | Telescopes inside the #9831 tube (ID ≈ 1.05 mm) |
| 30 AWG signal wire | CBAZY silicone kit — [B073RDGTPB](https://www.amazon.com/dp/B073RDGTPB) | $13.99 | I²C, I²S, button |
| 26 AWG power wire | TUOFENG — [B07G2LRX68](https://www.amazon.com/dp/B07G2LRX68) | $15.59 | Battery bus + twisted speaker pair |
| Kapton tape | ELEGOO 4-pack — [B072Z92QZ2](https://www.amazon.com/dp/B072Z92QZ2) | $9.99 | Module backs, frame crossings |
| **Fish paper** | 0.2 mm × 200 mm — [B0GZVDKBBS](https://www.amazon.com/dp/B0GZVDKBBS) | $15.88 | ✅ Sold/shipped by Amazon. The flame-rated barrier under and around the pack — mandatory |
| Heat-shrink kit | 14-size — [B08N4W4K9X](https://www.amazon.com/dp/B08N4W4K9X) | $9.99 | Every splice |
| Hot glue + CA | Any electronics-safe low-temp gun + gel CA | ~$15 | The video's retention method; keep clear of mic port, switch, USB |
| Finish (optional) | Raw brass like the reference, or the white paint system in [edu/05_COLOR_AND_FINISH.md](../edu/05_COLOR_AND_FINISH.md) (249322 self-etch + 2081830 gray + 7791830 satin white, in-person at Home Depot, 21+) | ~$24 | Paint is decoration, never insulation. NYC Admin Code §10-117: spray paint is 21+, kept locked |

## 4 · Tools

### Already owned (reconciled 2026-09-02)

| Owned item | Covers |
| --- | --- |
| **X-Tronic 3020-XTS Complete Kit** (75 W station) | Soldering station, 2 helping hands, T-2.4D chisel + T-K knife tips, solder sucker, tweezers, silicone mat, tip cleaner, holder, 50 g solder roll. ⚠️ Identify the roll's alloy on arrival: 60/40 leaded = use it; lead-free = buy the 63/37 below |
| **Chip Quik CQ4LF no-clean flux pen** | Electronics flux |
| **BOENFU flush cutters** | Wire and leads — **never the brass tube** (jeweler's saw does all tube cuts) |
| **WORKLION cutting mat** | Layout only — not heat-resistant; solder over the silicone mat |
| **OLFA CMP-1 circle cutter** | Speaker grille opening in template/guard material |

### Still to buy

| Tool | Part | Price |
| --- | --- | --- |
| Solder, 63/37 leaded | MAIYUM 0.8 mm — [B076QF1Y85](https://www.amazon.com/dp/B076QF1Y85) — skip if the X-Tronic roll is 60/40 | $11.69 |
| Multimeter | KAIWEETS HT118A — [B08BL288LW](https://www.amazon.com/dp/B08BL288LW) | $41.23 |
| **Bench supply, current-limited** | SKY TOPPOWER PS305H — [B0BN1F6CGZ](https://www.amazon.com/dp/B0BN1F6CGZ) — the one non-negotiable instrument: it stands in for the cell in every power test | $47.49 |
| Wire strippers 30–20 AWG | Hakko CSP-30-1 — [B00FZPHMUG](https://www.amazon.com/dp/B00FZPHMUG) | $12.87 |
| Calipers | Neiko 01407A — [B000GSLKIW](https://www.amazon.com/dp/B000GSLKIW) | $27.99 |
| Safety glasses | 3M Solus — [B016KZ1ZPM](https://www.amazon.com/dp/B016KZ1ZPM) | $14.99 |
| **Jeweler's saw** | SE 3-in-1 w/ blades — [B06XPSLS6N](https://www.amazon.com/dp/B06XPSLS6N) | $24.95 |
| Round + chain-nose pliers | WORKPRO 3-pc — [B0B8QBVXXR](https://www.amazon.com/dp/B0B8QBVXXR) | ~$12 |
| Brass flux (**frame only**) | Harris SCLF4 — [B0015DWPV8](https://www.amazon.com/dp/B0015DWPV8) — acid-class; wash + neutralize before any electronics exist near the frame | $12.85 |
| Breadboard + jumpers, USB-**A**-to-C data cable, header strip | Any Prime listings | ~$23 |

**Also required, cheap:** needle files + 400–800 grit (deburring is
safety-critical — no sharp edge may reach the pack), 90 %+ IPA + swabs +
baking soda (neutralizes the brass flux), solder wick, heat gun, ESD strap,
magnification, metric rule + square, cardstock. Budget ~$60–80.

**Why leaded 63/37:** melts lower and wets faster than lead-free — less time
with a hot iron against a MEMS microphone or an OLED flex tail. Wash hands,
don't eat at the bench, ventilate.

## Budget

| | |
| --- | ---: |
| Electronics (MCU, OLED, mic, amp, speakers, button) | ~$95 |
| Power (2× pack, charger, switch, pigtails, passives) | ~$60 |
| Frame + insulation + wire + adhesive | ~$85 |
| Tools still to buy + consumables | ~$290 |
| **Total remaining** | **~$530** (+ NYC 8.875 % tax) |

**Sequence:** order everything in one pass (Adafruit ships from Brooklyn —
typically 1–2 days to NYC; fish paper is the slowest Amazon item). Bench
bring-up while brass and paint wait. Multipacks mean spares of every
marketplace part — qualification means measuring several and keeping the best.

## Order sheet

Re-check price/seller/stock in the cart. NYC tax 8.875 % applies.

### Adafruit (one order, ships from Brooklyn)

- [ ] 2 × #1578 protected 500 mAh LiPo — $7.95 ea
- [ ] 1 × #4410 USB-C Micro-Lipo charger — $5.95
- [ ] *(optional alternates)* #4237 350 mAh pack · #6049 ICS-43434 mic · #3006 amp

### DigiKey

- [ ] 2 × CES-20134-088PM speaker — `2223-CES-20134-088PM-ND`

### Amazon

- [ ] MCU pack B0F888JQ91 (or B0G5XS345R) — flash-ID gate on arrival
- [ ] OLED white SSD1306 ×5 B09T6SJBV5 — $14.99
- [ ] INMP441 ×5 B092HWW4RS — $11.99
- [ ] MAX98357A ×3 B0CDWXZZCH — $9.49
- [ ] Tact-switch kit B0FHW6HMG4 — $15.99
- [ ] Slide switch 25-pack B09R434VJQ — ~$8
- [ ] JST-PH 2.0 mm pigtail set — ~$7 (caliper the pitch)
- [ ] Resistor kit B0F4P352BB — $6.39 · ceramics B07P7HRGT9 — $14.99 · electrolytics B0C1VBXCQM — $9.99
- [ ] Fish paper B0GZVDKBBS — $15.88 *(slowest item — order first)*
- [ ] Kapton B072Z92QZ2 — $9.99 · heat-shrink B08N4W4K9X — $9.99
- [ ] Wire: 30 AWG B073RDGTPB — $13.99 · 26 AWG B07G2LRX68 — $15.59
- [ ] Brass: #9831 tube B005WPAW9M — $7.80 · #9861 rod B005WPB7YG — $8.59 *(caliper on arrival)*
- [ ] Tools per the table above · bench items (breadboard, jumpers, USB-A-to-C data cable, header strip)

### In person (optional finish)

- [ ] Paint at Home Depot (21+, ID): 249322 · 2081830 · 7791830 — only if not keeping raw brass
