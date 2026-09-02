# Purchased inventory — what is actually in hand

> **Factual purchase record, last updated 2026-09-02.** This tracks what was
> *bought*, not what is *approved*. It takes no side in the R1/F0 design fork —
> part-selection authority stays in
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md). Update the
> Status column as boxes arrive and incoming inspection passes.

Status key: **✅ in hand** · **🚚 in transit** · **☐ not bought**

## Orders placed

| Order | Date | Contents |
| --- | --- | --- |
| Adafruit | Sep 1 | Cells, charger, flux pen — $81.29 incl. shipping + tax |
| X-Tronic | earlier | Soldering station — $64.80 |
| Amazon #4 | Sep 1 | Bench supply, saw, solder, stripper, brass flux, jumpers, headers |
| Amazon #5 | Sep 1 | Multimeter, calipers, breadboards, safety glasses, pliers |
| Amazon #1 | Sep 2 | Core electronics, passives, insulation, switch, buttons, JST |
| Amazon #2 | Sep 2 | OLED, electrolytic caps (30 AWG wire since canceled) |
| Amazon #3 | Sep 2 | K&S 1 mm brass rod |
| DigiKey | Sep 2 | `CES-20134-088PM` speaker |
| Amazon #6 | Sep 2 | K&S #9831 brass tube, TUOFENG 26 AWG wire |

Estimated total spend: **≈ $600–625** (several Amazon line prices not captured).

---

## Electronics

| Item | Qty | Notes |
| --- | ---: | --- |
| Meshnology **ESP32-C3 SuperMini** dev board | 10 | Gate every board: `esptool flash_id` ≥ 4 MB. Plain variant only — reject any with a WS2812 on GPIO8 |
| Hosyond **SSD1306 OLED** 0.96" 128×64 I²C, white | 5 | Read the silkscreen pin order before wiring — vendors ship GND-VCC *and* VCC-GND |
| AITRIP **INMP441** I²S microphone module | 5 | `L/R` → GND for the left slot; data → GPIO4 |
| HiLetgo **MAX98357** I²S amplifier board | 3 | Meter `SD` on arrival: ~0.30 V = mono mix (fine); ~0 V = shutdown, needs rework |
| QTEATAK tactile push-button set | 420 | Action button, GPIO10 → GND. Pick a white cap if available |
| 2.54 mm male breakaway header pins | 22 | Reversible breadboard fixtures |
| Same Sky **CES-20134-088PM** speaker, 8 Ω 0.8 W enclosed | 1 | DigiKey `2223-CES-20134-088PM-ND`. Top-port, 20 × 13 × 4.87 mm, two mount flanges, ships with 60 mm 32 AWG leads. Cap output ≤ 2.53 V RMS differential |

## Power

| Item | Qty | Notes |
| --- | ---: | --- |
| Adafruit **#1578** LiPo 3.7 V **500 mAh** protected | 2 | 29 × 36 × 4.75 mm — the compact option; discharge rating unpublished |
| Adafruit **#258** LiPo 3.7 V **1200 mAh** protected | 2 | 34 × 62 × 5 mm — the margin option, ~1.2 A capable but 62 mm long |
| Adafruit **#4410** USB-C Micro-Lipo charger | 1 | 100 mA default; 500 mA via solder jumper; 4.2 V termination |
| Chanzon SPDT mini slide switch | 25 | Measure contact drop on the sample you fit |
| daier **JST-PH 2.0** 2-pin connector cable | 20 pr | ⚠️ **Verify polarity with the meter, not wire color** — generic JST-PH is often reversed vs Adafruit's convention |
| LuminologyPro resistor kit, 25 values 1/4 W | 1000 | 10 kΩ pull-ups, 100 kΩ pull-down |
| BOJACK ceramic capacitor kit | 650 | 100 nF + 10 µF local decoupling |
| ALLECIN electrolytic capacitor kit, 24 values | 1 kit | Covers the 220 µF bulk cap at the amp |

**Buying both cell sizes was the right call.** It converts the 500-vs-1200 mAh
argument into a measurement: bench the real current draw, then fit whichever
cell the numbers justify. Keep the unused pair sealed and terminal-protected.

## Frame, insulation, wire

| Item | Notes |
| --- | --- |
| K&S **1.0 mm round brass rod**, 5 rods | Braces and corner posts |
| XFJYMXDM **fish paper**, 16.4 ft | The flame-rated cell barrier — mandatory under/around the pack |
| ELEGOO **polyimide (Kapton) tape**, 4-pack | Module backs, frame crossings |
| Pointool **heat-shrink kit**, 14 sizes, **white** | Every splice — and it matches the white/silver direction |
| K&S **#9831 brass tube**, 1.5 mm OD × 0.225 mm wall × 300 mm, 4 tubes | The frame stock. ASIN `B005WPAW9M` verified to resolve to 9831, not a wrong-diameter variant. Caliper on arrival anyway |
| TUOFENG **26 AWG** silicone wire, 6 colors, 33 ft each | Battery bus and any load-carrying run |
| CBAZY **30 AWG** silicone hookup wire | ☐ **Canceled** — see the gauge note below |

### Wire-gauge note — current is not the deciding factor

The "26 AWG for power" rule came from the withdrawn R0 design, which pushed
~1.15 A through a long chain (holder + fuse + converter + two FETs). The
current frame is ~45 mm and the chain is three parts, so on **current** either
gauge is comfortable:

| | 30 AWG | 26 AWG |
| --- | ---: | ---: |
| Resistance | ~0.34 Ω/m | ~0.13 Ω/m |
| Loop drop @ 0.8 A peak, 160 mm | 43 mV | 17 mV |
| Loop drop @ 150 mA average | 8 mV | 3 mV |

Both are far inside the ≤300 mV upstream-drop screen, and resistive heating is
tens of milliwatts. **The speaker needs no wire at all** — the
`CES-20134-088PM` ships with 60 mm of 32 AWG leads, longer than the whole
device, so they reach the amplifier terminal directly with no splice.

The real trade is **mechanical**, in both directions:

- **26 AWG on the battery bus** is the robustness choice: 30 AWG nicks easily
  when stripped (it is the finest setting on the CSP-30-1), its strands fatigue
  with flexing, and its joints have less pull strength. The battery bus is the
  connection you least want failing inside a sealed frame.
- **30 AWG on signals** is the routing choice: roughly 15–17 conductors get
  free-formed inside a 45 mm cage (OLED 4, microphone 5–6, amplifier 5,
  button 2). 26 AWG is stiffer and bulkier there, and stiff wire levers on
  breakout pads — which is how a pad lifts off a thin OLED or microphone board.

**30 AWG is currently canceled.** The build is not blocked: Dupont jumpers
cover the whole breadboard phase, and 33 ft × 6 colors of 26 AWG can wire the
entire device. Re-order [CBAZY 30 AWG](https://www.amazon.com/dp/B073RDGTPB)
(~$14) if the 1:1 dry-fit shows the signal bundle crowding the frame — which
is the likely outcome. Strain-relieve both ends of every conductor regardless
of gauge.

## Tools

| Item | Notes |
| --- | --- |
| X-Tronic 3020-XTS station + tips, solder sucker, tweezers, helping hands, silicone mat | Covers the soldering line |
| KAIWEETS TRMS 6000-count multimeter + hard case | Every safety step is a meter step |
| SKY TOPPOWER DC supply 0–30 V / 0–5 A | The cell substitute for all power tests |
| REXQualis breadboards, 4 pcs (830 + 400 point) | Phase 0 |
| TODOELEC Dupont jumper kit, 120 wires | Phase 0 |
| NEIKO digital caliper | Incoming dimensions for every part |
| SE 3-in-1 jeweler's saw + 144 blades + bench pin | The only correct tool for 0.225 mm-wall tube |
| WORKPRO jewelry pliers, 3-pack | Forming the frame |
| Hakko CHP CSP-30-1 wire stripper, 30–20 AWG | Correct range |
| 3M Solus 1000 safety glasses | Wear them for sawing and clipping |
| MAIYUM 63/37 rosin-core solder, 0.8 mm | Electronics only |
| Chip Quik CQ4LF no-clean flux pen | ⚠️ Duplicate — one was already owned |
| Harris SCLF4 Stay-Clean flux, 4 oz | **Acid/zinc-chloride — empty brass frame ONLY.** Never near electronics |

---

## Still missing

**Every part needed to build the device has been ordered.** Nothing on this
list blocks the bench phase or the frame; what remains is consumables and
process tools.

### Needed before assembly

| Item | Why | Approx. |
| --- | --- | ---: |
| **IPA 90 %+ · swabs · baking soda** | **Safety-relevant** — neutralizes the Harris acid flux. Residue left on brass corrodes joints and blisters paint | ~$15 |
| **Heat gun** | You have white heat-shrink and nothing to shrink it with | ~$20 |
| Solder wick | Undoing mistakes on fine pads | ~$8 |
| Needle files + 400–800 grit | Deburring is a safety step — no sharp brass edge may reach the pack | ~$15 |
| Hot glue gun + gel CA | Module retention | ~$15 |
| USB-**A**-to-C data cable | Clone boards ship CC-resistor bugs that make C-to-C power-only | ~$7 |

### Optional — white/silver finish

Rust-Oleum 249322 self-etch → 2081830 gray → 7791830 satin white (~$24, buy in
person; NYC Admin Code §10-117 keeps spray paint 21+ and locked), plus white
styrene sheet for guards (~$10, Blick or Canal Plastics).

---

## What to do first

The bench supply is the latest-arriving item, but it only gates the **power**
tests. Everything digital runs from USB, so:

1. **Now:** build the firmware — `cd firmware && ./scripts/prepare.sh &&
   ./scripts/build.sh`.
2. **As boards arrive:** `esptool flash_id` on several SuperMinis (≥ 4 MB
   gate), flash one bare, provision Wi-Fi, pair the backend, confirm one full
   voice round trip.
3. **Then:** breadboard OLED + INMP441 + MAX98357A on the REXQualis board, at
   low volume. Order the speaker now so it arrives for this step.
4. **When the supply lands:** the current-limited sweep, then the 500-vs-1200
   mAh cell decision from measured numbers.

Both battery packs stay sealed and terminal-protected until step 4. Nothing
gets soldered into a frame before the breadboard stack works end to end.
