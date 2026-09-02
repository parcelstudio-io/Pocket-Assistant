# Complete material list — Amazon-first, NYC

Every row was fetched live on **2026-09-01** and then re-verified by a second
pass that re-opened each listing independently. Prices, sellers and stock move;
re-check in the cart. Where a claim could not be confirmed from the listing it
says so, with the measurement that settles it on arrival.

**The whole electrical build is on Amazon except one part** (the cell — see
Exceptions). Nothing here requires DigiKey, Pololu, Adafruit or Same Sky.

Legend: **✅ confirmed** = listing fetched and specs read · **⚠️ measure**
= a spec the listing does not publish; verify on arrival.

---

## 1 · Electronics

| Role | Part / ASIN | Price | Spec check |
| --- | --- | --- | --- |
| **MCU** | ESP32-C3 SuperMini, plain, 3-pack — [B0GX966R9R](https://www.amazon.com/dp/B0GX966R9R) (Suuoo, FBA) | $12.97 / 3 | ✅ USB-C, no U.FL, single blue LED, castellated. ⚠️ 4 MB flash is listing text only — confirm with `esptool flash_id`. Only 5 reviews; buy the 3-pack and qualify two. Alt: [B0F888JQ91](https://www.amazon.com/dp/B0F888JQ91) 10-pack $28.99, whose photo shows the `FH4` 4 MB chip marking and whose text says "Onboard LED blue light: GPIO8" — best-evidenced board, but pre-soldered headers are a rework risk |
| **Display** | 0.96" SSD1306 128×64 I²C, **white**, 5-pack — [B09T6SJBV5](https://www.amazon.com/dp/B09T6SJBV5) (Hosyond) | $14.99 / 5 | ✅ SSD1306 (not SH1106), 4-pin I²C, white pixels, 3.3–5 V. Address 0x3C; firmware probes 0x3C then 0x3D so either works. ⚠️ **Read the silkscreen pin order** — vendors ship GND-VCC-SCL-SDA *and* VCC-GND-SCL-SDA |
| **Microphone** | INMP441 I²S MEMS, 5-pack — [B092HWW4RS](https://www.amazon.com/dp/B092HWW4RS) | $11.99 / 5 | ✅ **Ships from and sold by Amazon** (best fulfilment in the whole BOM). 3.3 V, I²S, `L/R` to GND = left slot |
| **Amplifier** | MAX98357A I²S class-D, 3-pack — [B0CDWXZZCH](https://www.amazon.com/dp/B0CDWXZZCH) (HiLetgo) | $9.49 / 3 | ✅ Adafruit-lineage clone, 2.5–5.5 V, works at 3.3 V. Stock SD ≈ 0.30 V = (L+R)/2 — **this is fine, not a 6 dB loss** ([why](../edu/04-audio.md#the-channel-select-pin-sd_mode--and-a-correction)). Genuine Adafruit ADA3006 is *unavailable* on Amazon |
| **Speaker** | 8 Ω 1 W cavity speaker, 15×10×3.5 mm, 4-pack — [B0CJNB3CR2](https://www.amazon.com/dp/B0CJNB3CR2) (Treedix) | $7.99 / 4 | ✅ 8 Ω, 1 W ≥ the 0.68 W the amp can deliver at 3.3 V. JST-PH leads |
| **Speaker enclosure** | Vinyl end caps, 20 mm ID — [B08HL9R5YB](https://www.amazon.com/dp/B08HL9R5YB) (uxcell, 25 pcs) | $7.55 | The no-3D-print answer: trim to depth for a sealed ~1 cc back volume. Alt: **[B0BHST51PQ](https://www.amazon.com/dp/B0BHST51PQ)** double-cavity 8 Ω speakers that ship *already boxed* — removes the enclosure step entirely |
| **Action button** | 6×6 mm tact + white caps, 420 pc — [B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4) | $15.99 | ✅ 8 stem heights, 7 cap colours incl. white. Same-day: Micro Center Brooklyn Inland kit $9.99 (no white cap) |

## 2 · Power — read [the power-chain lesson](../edu/07-the-power-chain.md) first

| Role | Part / ASIN | Price | Spec check |
| --- | --- | --- | --- |
| **3.3 V buck-boost** | XL63070 (TPS63070) module, 3-pack — [B0FFSHDLMV](https://www.amazon.com/dp/B0FFSHDLMV) (JESSINIE, FBA) | $9.99 / 3 | ✅ **True 4-switch buck-boost.** Output fixed by **solder jumper**, not a trimpot. 16×30 mm. Listing claims 2 V startup; a sibling listing for the same module claims 2.8 V and no current rating — **unresolved on paper, settled by the Phase 0 chain test**. ⚠️ Verify the 3V3 pad is bridged and Vout = 3.30 V *before* it touches the MCU |
| ↳ smaller backup | XL63802 (TPS63802), 5-pack — [B0D5YCSZFP](https://www.amazon.com/dp/B0D5YCSZFP) | $9.99 / 5 | ✅ 12.8 × 25.8 mm — the smallest. 1.8 V startup. But its "3.3 V @ 1.2 A" is quoted **at 3.7 V in**; at a 3.0 V cell expect ~0.9–1.0 A, i.e. only ~15–25 % over the 778 mA peak |
| ↳ if the frame is tight | XL63020 (TPS63020), 5-pack — [B0D8T3J8QZ](https://www.amazon.com/dp/B0D8T3J8QZ) | $13.99 / 5 | ✅ 1.3 A, 17.4 × 26.2 mm, 1.8 V startup. **Desolder its micro-USB connector** — a second power source on the cell node is a hazard, not a convenience |
| ❌ **do not buy** | Pololu S7V8A [B01MCV1XY6](https://www.amazon.com/dp/B01MCV1XY6) | $22.99 | Correct topology, but the output is a **trimpot spanning 2.5–8 V** on a rail feeding a 3.6 V-max chip. Amazon's "8 A" spec is metadata garbage. Also reject every boost-only and buck-only "3.3 V converter" — [why](../edu/07-the-power-chain.md#why-a-buck-boost-restated-as-a-rule) |
| **PTC fuse ×2** | RUEF110 10-pack — [B093L9KRP1](https://www.amazon.com/dp/B093L9KRP1) | $6.90 / 10 | **Fit two in parallel**: 1.65 A warm-derated hold vs a 1.0 A peak, and half the resistance. One alone derates to 0.83 A and nuisance-trips. Do *not* buy the single $12.37 MF-RX110 |
| **Battery holder** | CR123A holder w/ leads, 10-pack — [B0CRGK889F](https://www.amazon.com/dp/B0CRGK889F) (ACEIRMC) | $7.99 / 10 | 43.2 × 18.3 × 14.2 mm, wire leads. ⚠️ **Listing never says 16340** — fit is a geometric inference, not a confirmed spec. Buy the 10-pack, measure contact resistance on several, keep the best (**≤ 0.03 Ω**) |
| **Charger** | XTAR MC1 Plus — [B00WJGR1XM](https://www.amazon.com/dp/B00WJGR1XM) | $9.99 | ✅ In stock, FBA. Auto-selects 0.5/1 A; ⚠️ the *mechanism* is undocumented and 16340 is absent from this page's compatibility list (it is on XTAR's own). 1 A is within the NL169's rating, so **don't chase 0.5 A** — just watch the display on first charge |
| **Disconnect switch** | SPDT toggle MTS-102, 10-pack — [B0799HC3VY](https://www.amazon.com/dp/B0799HC3VY) | $7.99 / 10 | Electrically fine (6 A). ⚠️ **33 mm overall is probably too tall for a pocket frame** — dry-fit before committing, and be ready to substitute a mini slide switch. No published DC rating or contact resistance: measure and fold into the chain budget |
| **Service jumper** | 2-pin 0.1" header + shunt (from any header/jumper kit) | ~$1 | Breaks the 3.3 V rail so USB can't back-drive the converter. **[Why this exists](../edu/07-the-power-chain.md#the-service-jumper)** |

## 3 · Frame, finish, wire, insulation

| Role | Part / ASIN | Price | Notes |
| --- | --- | --- | --- |
| Brass tube 1.5 mm OD × 0.225 wall × 300 mm ×4 | K&S #9831 — [B005WPAW9M](https://www.amazon.com/dp/B005WPAW9M) | $7.80 | ✅ **Ships from and sold by Amazon.** ⚠️ This ASIN is a *variation parent* often indexed under the 1 mm title — verify OD with calipers on arrival |
| Brass rod 1.0 mm × 300 mm ×5 | K&S #9861 — [B005WPB7YG](https://www.amazon.com/dp/B005WPB7YG) | $8.59 | Telescopes inside the #9831 tube (ID ≈ 1.05 mm) |
| Paint 1 — self-etch primer | Rust-Oleum 249322 — [B003CT498A](https://www.amazon.com/dp/B003CT498A) | $7.47 | ⚠️ Its own listing names "bare metal, aluminum, fiberglass" — **brass is not listed**. Test on an offcut first |
| Paint 2 — gray sandable primer | Rust-Oleum 2081830 — [B000V69Q58](https://www.amazon.com/dp/B000V69Q58) | $6.27 | Kills the green etch coat before white |
| Paint 3 — satin white | Rust-Oleum 7791830 — [B000Z8FGII](https://www.amazon.com/dp/B000Z8FGII) | $6.47 | Aerosols are hazmat/non-returnable. In NYC they're **21+ and kept locked** (Admin Code §10-117) — buying in person at Home Depot is often easier |
| 30 AWG signal wire | CBAZY silicone kit — [B073RDGTPB](https://www.amazon.com/dp/B073RDGTPB) | $13.99 | White included |
| 26 AWG power wire | TUOFENG — [B07G2LRX68](https://www.amazon.com/dp/B07G2LRX68) | $15.59 | Battery/converter spine |
| Kapton tape | ELEGOO 4-pack — [B072Z92QZ2](https://www.amazon.com/dp/B072Z92QZ2) | $9.99 | |
| **Fish paper** | 0.2 mm × 200 mm × 16.4 ft — [B0GZVDKBBS](https://www.amazon.com/dp/B0GZVDKBBS) | $15.88 | ✅ **Sold and shipped by Amazon.** Goes under/around the cell — this is the flame-rated layer. Polycarbonate is *not* flame-rated; use it for sub-plates only |
| Polycarbonate sheet 0.5 mm | Zonon 5-pack — [B09KGZCMP3](https://www.amazon.com/dp/B09KGZCMP3) | $9.99 | ⚠️ Reviews report brittleness — the signature of acrylic sold as PC. Sub-plates only |
| White heat-shrink | 14-size kit — [B08N4W4K9X](https://www.amazon.com/dp/B08N4W4K9X) | $9.99 | |
| Resistors (10 k, 100 k, 470 k) | 1000-pc metal film kit — [B0F4P352BB](https://www.amazon.com/dp/B0F4P352BB) | $6.39 | |
| Ceramic caps (100 nF, 10 µF) | BOJACK 650-pc — [B07P7HRGT9](https://www.amazon.com/dp/B07P7HRGT9) | $14.99 | ⚠️ Dielectric code unpublished. If Y5V, capacitance falls sharply when warm — **parallel three 10 µF at the amp** rather than substituting an electrolytic (an electrolytic's 1–5 Ω ESR cannot decouple class-D edges) |
| Bulk cap 100–220 µF | ALLECIN kit — [B0C1VBXCQM](https://www.amazon.com/dp/B0C1VBXCQM) | $9.99 | 5 pcs per value (not 10) |
| Ferrite beads | BOJACK axial 100-pc — [B09C25PPBG](https://www.amazon.com/dp/B09C25PPBG) | $6.99 | ⚠️ Impedance unpublished; a DMM only reads DCR, which proves nothing |

## 4 · Tools

**Must-have** (~$300 if you own none of it):

| Tool | Part | Price |
| --- | --- | --- |
| Soldering station, 70 W | Weller WE1010NA — [B077JDGY1J](https://www.amazon.com/dp/B077JDGY1J) | $115.00 |
| Solder, **63/37 leaded** | MAIYUM 0.8 mm 100 g — [B076QF1Y85](https://www.amazon.com/dp/B076QF1Y85) | $11.69 |
| Electronics flux (no-clean) | Chip Quik SMD291 — [B0CT5T6HWN](https://www.amazon.com/dp/B0CT5T6HWN) | $15.95 |
| Brass flux (**frame only**) | Harris SCLF4 zinc chloride — [B0015DWPV8](https://www.amazon.com/dp/B0015DWPV8) | $12.85 |
| Multimeter | KAIWEETS HT118A — [B08BL288LW](https://www.amazon.com/dp/B08BL288LW) | $41.23 |
| **Bench supply, current-limited** | SKY TOPPOWER PS305H 0–30 V/0–5 A — [B0BN1F6CGZ](https://www.amazon.com/dp/B0BN1F6CGZ) | $47.49 |
| Helping hands | Toolour — [B07MZM7MPS](https://www.amazon.com/dp/B07MZM7MPS) | $36.99 |
| Flush cutters | Hakko CHP-170 — [B00FZPDG1K](https://www.amazon.com/dp/B00FZPDG1K) | $14.83–29.40 |
| Wire strippers 30–20 AWG | Hakko CSP-30-1 — [B00FZPHMUG](https://www.amazon.com/dp/B00FZPHMUG) | $12.87 |
| Calipers | Neiko 01407A — [B000GSLKIW](https://www.amazon.com/dp/B000GSLKIW) | $27.99 |
| Safety glasses | 3M Solus 1000 — [B016KZ1ZPM](https://www.amazon.com/dp/B016KZ1ZPM) | $14.99 |
| **Jeweler's saw** (brass) | SE 3-in-1 w/ 144 blades — [B06XPSLS6N](https://www.amazon.com/dp/B06XPSLS6N) | $24.95 |
| **Round + chain-nose pliers** | WORKPRO 3-pc — [B0B8QBVXXR](https://www.amazon.com/dp/B0B8QBVXXR) | ~$12 |
| **Organic-vapour respirator** | 3M 6211 OV/P95 — [B00004Z4EB](https://www.amazon.com/dp/B00004Z4EB) | ~$35 |

**Also required, cheap, easy to forget:** needle files + 400–800 grit (deburring
is *safety*-critical — no sharp edge may reach the cell, and abrasion is what
makes the primer stick), 90 %+ IPA + lint-free swabs + baking soda (to
neutralise the zinc-chloride brass flux — it is water-soluble, so water-rinse
then IPA, and the frame must be bone dry before primer or the residue blisters
the paint), a **heat-resistant silicone mat** (the Weller ships none), fine
solder wick, a heat gun, an ESD wrist strap, magnification, a metric steel rule
and small square, cardstock, and a spare Weller ET chisel tip. Budget
**~$110–140** for this group.

**Why leaded 63/37:** it melts lower and wets faster than lead-free, which
means less time with a hot iron against a MEMS microphone or an OLED flex tail.
Wash your hands, don't eat at the bench, and ventilate.

---

## Exceptions — the two things not on Amazon

**1 · The cell.** No protected 16340 with a published discharge rating exists on
Amazon; searches return chargers and primary CR123As. Buy:

> **Nitecore NL169** — 950 mAh, 3.6 V, protected, button top, **2 A max
> continuous** (2× our peak), 34.1 × 16.6 mm.
> [B&H Photo](https://www.bhphotovideo.com/c/product/1811930-REG/nitecore_nl169_16340_li_ion_rechargeable.html),
> $9.95, 420 Ninth Ave Manhattan. **Buy two.**

⚠️ B&H blocks automated fetches, so "in stock" is unverified — **call or load
the page in a browser before travelling.** Same cell at the same price from
[nitecorestore.com](https://nitecorestore.com) or Battery Junction if not.

**2 · Reverse-polarity protection.** Rev A has none. The tempting series
Schottky is the *wrong* fix (0.35 V would break the chain budget); the right
part is a P-channel MOSFET (AO3401A/DMG2301L). Rev A manages this
procedurally — meter the holder leads before first connection — and records the
MOSFET as the Rev B improvement.

## Budget

| | |
| --- | ---: |
| Electronics + power + frame/consumables | ~$260 |
| Cell + charger | ~$30 |
| Tools, if you own none | ~$400–440 |
| **Total, starting from nothing** | **~$690–730** |
| **Total, if you already have a soldering setup and meter** | **~$290** |

Multipacks mean you finish with spares of every consumable part — which is the
point, since qualification means measuring several and keeping the best.
