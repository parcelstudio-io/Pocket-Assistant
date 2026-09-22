# Fast-track parts outline — every component, by step, with its link

[Back to the action-only fast track](FAST_TRACK.md) ·
[Theory companion](FAST_TRACK_THEORY.md) ·
[Full purchase record](../docs/INVENTORY.md)

This page is the "do not forget anything" checklist. It does not replace the
[fast track](FAST_TRACK.md), which stays the authority on order, wiring, and
safety. Use this page to answer one question only: *what do I need in my hand
before I start this step, and where did it come from?*

Do not go shopping from this page alone. Steps 0–4 need almost nothing, and
buying ahead of a gate is how a bench fills with parts you are not allowed to
connect yet.

## How to read the link column

| Mark | Meaning |
| --- | --- |
| ✅ | Recorded purchase link — this exact listing is in the purchase record |
| 📦 | Owned and recorded, but the exact order URL was not saved. The search link is only for comparing names and packaging with your pile |
| 🔍 | Candidate or search link. **Not** purchase provenance and **not** recorded as bought |
| ⬜ | On the still-needed list in [INVENTORY.md](../docs/INVENTORY.md#still-needed) |

Marketplace sellers and board revisions change. When a link and the label on
the received part disagree, **the label on the part wins.**

## Where you are now

**The USB prototype is complete — PASS 9 established 2026-09-20.** Two cold
starts booted without a reset loop, the button logged every press, the OLED
started and toggled, and speech read higher than quiet. This is the first
physical-hardware result in the project. **Step 10 followed on 2026-09-21:**
`A1` joined Wi-Fi under the 8.5 dBm transmit-power cap and one spoken question
returned a remote response from the Xiaozhi backend (PASS 10C,
builder-reported). No spoken output yet; the amplifier stays disabled.

Build history:

| Module | Headers | Notes |
| --- | --- | --- |
| Controller `A1` | 16 soldered in 5C, passed | Two 8-pin strips |
| OLED | Arrived factory-soldered | Silkscreen order `GND-VCC-SCL-SDA` |
| Microphone | 6 soldered in 5E | Two rows of three: `SD VDD GND` / `SCK WS L/R` (re-read 2026-09-20; an earlier note had the second row reversed) |

The Sullins 1×40 strip is in hand, so header supply is no longer a constraint.
Everything from Step 6 on is breadboard, jumpers, and the serial monitor.

**Step 6 passed 2026-09-20:** rails built and verified, button on GPIO10, ten
presses logged `BUTTON GPIO10: click 1`–`10`. The button's legs do not span
the trench, so it sits on one side with each joined leg pair in its own
column — the guide's Step 6 was corrected to state that requirement.

## Master list — everything the USB prototype touches

| Component | First needed at | Link |
| --- | --- | --- |
| Meshnology ESP32-C3 SuperMini (10-pack, use 1) | Step 0 | ✅ [Amazon B0F888JQ91](https://www.amazon.com/dp/B0F888JQ91) |
| USB-A-to-C **data** cable | Step 0 | ⬜ [Rankie 3-pack B01JRY0VE4](https://www.amazon.com/dp/B01JRY0VE4) — you already proved a working cable at Step 3 |
| KAIWEETS HT118A multimeter | Step 5A | ✅ [Amazon B08BL288LW](https://www.amazon.com/dp/B08BL288LW) |
| Hosyond SSD1306 OLED (5-pack, use 1) | Step 5A | ✅ [Amazon B09T6SJBV5](https://www.amazon.com/dp/B09T6SJBV5) |
| AITRIP INMP441 microphone (5-pack, use 1) | Step 5A | ✅ [Amazon B092HWW4RS](https://www.amazon.com/dp/B092HWW4RS) |
| 2.54 mm male breakaway headers (22 loose pins in hand) | Step 5A | 📦 Amazon order #4, URL not saved |
| Extra 1×40 headers, if you are short | Step 5A | 🔍 [Sullins PRPC040SAAN-RC — DigiKey](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PRPC040SAAN-RC/2775214) |
| 3M Solus 1000 safety glasses | Step 5B | ✅ [Amazon B016KZ1ZPM](https://www.amazon.com/dp/B016KZ1ZPM) |
| X-Tronic 3020-XTS station, tips, mat, helping hands | Step 5B | 📦 [X-Tronic search](https://www.amazon.com/s?k=X-Tronic+3020-XTS) |
| MAIYUM 63/37 solder, 0.8 mm | Step 5B | ✅ [Amazon B076QF1Y85](https://www.amazon.com/dp/B076QF1Y85) |
| Chip Quik CQ4LF no-clean flux pen | Step 5B | 📦 [Chip Quik search](https://www.amazon.com/s?k=Chip+Quik+CQ4LF) |
| BOENFU flush cutters | Step 5C | 📦 [BOENFU search](https://www.amazon.com/s?k=BOENFU+flush+cutters) |
| Practice material (perfboard or offcuts) | Step 5B | 🔍 [2.54 mm perfboard search](https://www.amazon.com/s?k=2.54mm+perfboard+prototype) |
| Solder wick | Step 5B rework | ⬜ [JoTownCand B0DRN688Q5](https://www.amazon.com/dp/B0DRN688Q5) |
| REXQualis breadboards (use the clean 830-point) | Step 6 | 📦 [Breadboard search](https://www.amazon.com/s?k=REXQualis+830+400+breadboard) |
| TODOELEC Dupont jumpers, 120 × 10 cm | Step 6 | 📦 [Jumper search](https://www.amazon.com/s?k=TODOELEC+10cm+Dupont+jumper+120) |
| QTEATAK tactile buttons (420, use 1) | Step 6 | ✅ [Amazon B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4) |
| LuminologyPro resistor kit (need 10 kΩ + 100 kΩ) | Step 8 | ✅ [Amazon B0F4P352BB](https://www.amazon.com/dp/B0F4P352BB) |
| Phone camera in a clean clear bag | Step 5A | General tool; no project purchase |

## Step by step

### Steps 0–4 — controller, cable, toolchain ✅ done

| Need | Link |
| --- | --- |
| One plain ESP32-C3 SuperMini, flash-ID gated ≥ 4 MB, no RGB LED on GPIO8 | ✅ [B0F888JQ91](https://www.amazon.com/dp/B0F888JQ91) |
| One proven USB-A-to-C **data** cable | ⬜ [B01JRY0VE4](https://www.amazon.com/dp/B01JRY0VE4) |
| A computer with a Bash terminal | — |

### Step 5A — inspect and count ✅ done

| Need | Link |
| --- | --- |
| KAIWEETS meter, continuity mode, self-checked | ✅ [B08BL288LW](https://www.amazon.com/dp/B08BL288LW) |
| One OLED and one microphone, to inspect | ✅ [OLED](https://www.amazon.com/dp/B09T6SJBV5) · ✅ [Mic](https://www.amazon.com/dp/B092HWW4RS) |
| Header pins for every unsoldered position | 📦 22 in hand · 🔍 [Sullins 1×40](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PRPC040SAAN-RC/2775214) if short |

**Pin arithmetic:** controller 16 + OLED 4 + microphone 6 = **26** if every
position is bare. The purchase record confirms only **22 loose pins**. Count
the positions you actually still need before ordering anything.

### Steps 5B–5E — soldering ✅ done

If all 26 positions already passed 5A, skip this whole block and go to Step 6.

| Need | Link |
| --- | --- |
| Safety glasses — required, not optional | ✅ [B016KZ1ZPM](https://www.amazon.com/dp/B016KZ1ZPM) |
| Soldering station, silicone mat, helping hands | 📦 [X-Tronic search](https://www.amazon.com/s?k=X-Tronic+3020-XTS) |
| 63/37 solder, 0.8 mm | ✅ [B076QF1Y85](https://www.amazon.com/dp/B076QF1Y85) |
| Electronics flux pen — **not** the Harris acid brass flux | 📦 [Chip Quik search](https://www.amazon.com/s?k=Chip+Quik+CQ4LF) |
| Flush cutters, to break header strips | 📦 [BOENFU search](https://www.amazon.com/s?k=BOENFU+flush+cutters) |
| Practice material for the three warm-up joints (5B) | 🔍 [Perfboard search](https://www.amazon.com/s?k=2.54mm+perfboard+prototype) |
| Solder wick, for removing excess solder | ⬜ [B0DRN688Q5](https://www.amazon.com/dp/B0DRN688Q5) |
| Ventilation that moves fumes away from your face | — |

Without wick you have no recovery path for a solder bridge: the fast track
tells you to stop rather than improvise. Decide before you heat the iron.

### Step 6 — button ✅ done

| Need | Link |
| --- | --- |
| The clean 830-point breadboard — not the 400-point jig | 📦 [Breadboard search](https://www.amazon.com/s?k=REXQualis+830+400+breadboard) |
| Four male-to-male jumpers | 📦 [Jumper search](https://www.amazon.com/s?k=TODOELEC+10cm+Dupont+jumper+120) |
| One tactile button | ✅ [B0FHW6HMG4](https://www.amazon.com/dp/B0FHW6HMG4) |
| The meter, to map rails and find the switched legs | ✅ [B08BL288LW](https://www.amazon.com/dp/B08BL288LW) |

### Step 7 — OLED ✅ done

| Need | Link |
| --- | --- |
| One soldered OLED; keep a second packaged as a swap spare | ✅ [B09T6SJBV5](https://www.amazon.com/dp/B09T6SJBV5) |
| Four more male-to-male jumpers | 📦 [Jumper search](https://www.amazon.com/s?k=TODOELEC+10cm+Dupont+jumper+120) |

### Step 8 — microphone ✅ done

| Need | Link |
| --- | --- |
| One soldered INMP441 | ✅ [B092HWW4RS](https://www.amazon.com/dp/B092HWW4RS) |
| Six more male-to-male jumpers | 📦 [Jumper search](https://www.amazon.com/s?k=TODOELEC+10cm+Dupont+jumper+120) |
| One 10 kΩ and one 100 kΩ resistor, **meter-verified** | ✅ [B0F4P352BB](https://www.amazon.com/dp/B0F4P352BB) |

### Step 9 ✅ done · Step 10 ✅ done (2026-09-21)

No new components. Step 9 needs the phone camera and somewhere to save the
log. Step 10 needs a dedicated 2.4 GHz guest/IoT network with a unique
password, and a deliberate privacy decision; it passed on `A1` with one
remote response. No part fixes the SuperMini's
invisible setup hotspot; the assistant build caps transmit power at 8.5 dBm
instead. Do not buy an external antenna for these boards: they have no socket.

### Step 11 ⬜ USB-powered speaker, nothing to buy

Every part is already in the inventory. The purchase authority's battery
fixture parts are not needed, by the scope decision of 2026-09-21.

| Part | Status |
| --- | --- |
| HiLetgo MAX98357A board, one of three | ✅ owned; used as `AMP-A1` |
| Same Sky CES-20134-088PM speaker | ✅ owned; the only one, leads never cut |
| Seven header pins from the spare 1×40 strip | ✅ owned |
| 220 µF electrolytic, 10 V or more | ✅ owned, ALLECIN kit |
| 100 nF ceramic | ✅ owned, BOJACK kit |
| `SD` pull-down, value from the board trace | ✅ owned, resistor kit |
| Dummy load: twelve 100 Ω resistors in parallel | ✅ owned, resistor kit, plus 26 AWG wire |
| Oscilloscope for PASS 11B | 📦 Rigol DHO802, arriving 2026-09-30 |

## The open gaps before Step 5B — resolved

All three were closed during Step 5: the OLED arrived factory-soldered (so only
22 pins were ever needed), the Sullins 1×40 arrived as spare stock, and the
mic was soldered without needing rework. Solder wick remains on the
still-needed list but nothing in Steps 6–9 uses an iron.

## Held parts — bought, but not released for this build

These are in the house and stay in their bags for the entire fast track.
Owning a part is not permission to connect it. The release authority is the
[Phase 0 promotion gates](../docs/FINAL_MATERIALS_FOR_REVIEW.md#promotion-gates-before-claude-may-say-final-go).

| Held part | Waits for |
| --- | --- |
| HiLetgo MAX98357A amplifier ×3 | Output power, I2S slot, and mute-timing qualification |
| Same Sky CES-20134-088PM speaker (DigiKey `2223-CES-20134-088PM-ND`) | The amplifier gate above |
| [Adafruit #1578 500 mAh](https://www.adafruit.com/product/1578) and [#258 1200 mAh](https://www.adafruit.com/product/258) LiPo cells | A complete power design and measured demand |
| [Adafruit #4410 USB-C Micro-Lipo charger](https://www.adafruit.com/product/4410) | Source-isolation and load-sharing design |
| SKY TOPPOWER bench supply, Chanzon slide switches, JST-PH leads | The power chain they belong to |
| K&S brass tube and rod, fish paper, Kapton, heat-shrink, 26/30 AWG wire | Measured parts and a non-stale CAD model |
| Harris SCLF4 acid flux | Empty brass frame only — never near electronics |

The full annotated record for every one of these, including why it was bought,
is in [INVENTORY.md](../docs/INVENTORY.md).
