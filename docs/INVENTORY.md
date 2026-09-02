# Purchased inventory — what is in hand and what each item is for

> **Factual purchase record, last updated 2026-09-02.** This tracks what was
> *bought*, not what is *approved*. It takes no side in the R1/F0 design fork —
> part-selection authority stays in
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md). Mark items off
> as boxes arrive and incoming inspection passes.

**Status: every part and tool needed to build the device has been ordered.**
What remains is a short consumables list at the bottom, none of it blocking.

## Orders placed

| Order | Date | Contents |
| --- | --- | --- |
| X-Tronic | earlier | Soldering station — $64.80 |
| Adafruit | Sep 1 | Cells, charger, flux pen — $81.29 incl. shipping + tax |
| Amazon #4 | Sep 1 | Bench supply, saw, solder, stripper, brass flux, jumpers, headers |
| Amazon #5 | Sep 1 | Multimeter, calipers, breadboards, safety glasses, pliers |
| Amazon #1 | Sep 2 | Core electronics, passives, insulation, switch, buttons, JST |
| Amazon #2 | Sep 2 | OLED, electrolytic caps |
| Amazon #3 | Sep 2 | K&S 1 mm brass rod |
| DigiKey | Sep 2 | `CES-20134-088PM` speaker |
| Amazon #6 | Sep 2 | K&S #9831 brass tube, TUOFENG 26 AWG wire |
| Amazon #7 | Sep 2 | CBAZY 30 AWG wire (re-ordered after cancellation) |
| Amazon #8 | Sep 2 | Heat gun $10.33 · hot glue gun $11.92 · diamond needle files |

Estimated total spend: **≈ $635–660**.

---

# 1 · Electronics

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **Meshnology ESP32-C3 SuperMini** dev board | 10 | The brain. A postage-stamp ESP32-C3 board with Wi-Fi, native USB-C, and the GPIO layout the firmware targets. It runs the assistant, talks to the cloud backend, and drives every peripheral. **Gate each board with `esptool flash_id` — reject anything under 4 MB flash**, and reject any "Plus" variant with an RGB LED on GPIO8, which breaks this pin map. Ten boards means you can afford to throw out bad clones. |
| **Hosyond SSD1306 OLED**, 0.96" 128×64 I²C, white | 5 | The screen — the device's only visual output, showing state, the pairing code, and responses. White pixels on black glass are also the intended white/silver accent. Firmware probes both `0x3C` and `0x3D`, so either address works. **Read the silkscreen pin order before wiring**: vendors ship GND-VCC-SCL-SDA *and* VCC-GND-SCL-SDA on identical-looking boards. |
| **AITRIP INMP441** I²S MEMS microphone | 5 | The ears. A digital microphone that outputs I²S directly, so no analog audio wiring is needed. This is the creator's exact part. Tie `L/R` to GND to select the left slot; data goes to GPIO4. **Keep flux, IPA, glue, paint, and compressed air away from the acoustic port** — contaminating it is permanent. |
| **HiLetgo MAX98357** I²S class-D amplifier | 3 | The voice. Takes the I²S stream straight from the ESP32-C3 and drives the speaker — no separate DAC. Runs on 2.5–5.5 V, so it can sit directly on the raw battery rail. **Meter the `SD` pin on arrival**: ~0.30 V is mono-mix mode (correct, plays at full amplitude); ~0 V means the board shipped in shutdown and needs rework. |
| **Same Sky CES-20134-088PM** speaker, 8 Ω 0.8 W | 1 | The mouth. A factory-enclosed micro-speaker — the sealed rear cavity is what makes it audible at this size, and it removes the hardest acoustic problem in the build. 20 × 13 × 4.87 mm, top-firing, with two mounting flanges and a built-in dust mesh. Ships with 60 mm of 32 AWG lead, longer than the whole device, so **it needs no wire from you**. Cap output at ≤ 2.53 V RMS differential to respect the 0.8 W rating. |
| **QTEATAK tactile push buttons** | 420 | The only user control: a momentary button on GPIO10 to ground. Short press toggles chat, long press resets Wi-Fi. Pick a white cap to match the finish. Note the onboard GPIO9 button is ROM BOOT, not this input. |
| **2.54 mm male breakaway header pins** | 22 | Snap-apart pin strips for soldering onto modules so they can plug into a breadboard. Makes the whole Phase 0 bench stack reversible instead of permanent. |

# 2 · Power

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **Adafruit #1578** LiPo 3.7 V **500 mAh**, protected | 2 | The compact battery option, 29 × 36 × 4.75 mm — small enough to lie flat behind the OLED and keep the device at video scale. "Protected" means an internal circuit board guards against overcharge, over-discharge (cuts at 3.0 V), and short circuit. Ships with a JST-PH lead so it is **never soldered**. Its discharge-current rating is unpublished — the open question these packs exist to answer. |
| **Adafruit #258** LiPo 3.7 V **1200 mAh**, protected | 2 | The margin battery option, 34 × 62 × 5 mm. Roughly 1.2 A capable and more than twice the runtime, but 62 mm long — longer than the intended device — so fitting it changes the silhouette. Buying both sizes turns the capacity-vs-size argument into a measurement. |
| **Adafruit #4410** USB-C Micro-Lipo charger | 1 | Recharges the pack in place through a USB-C port on the frame, the way the reference build does. Runs the proper constant-current/constant-voltage lithium charge algorithm and terminates at 4.2 V. Ships at a gentle 100 mA; a solder jumper raises it to 500 mA. Has **no load sharing**, so the device must be switched **off** while charging. |
| **Chanzon SPDT mini slide switch** | 25 | The power switch. Breaks the battery's positive lead, so "off" is a genuine disconnect rather than a sleep state. Measure the contact drop on the one you actually fit. |
| **daier JST-PH 2.0 mm** 2-pin connector cables | 20 pr | Mating connectors for the battery. Their real value is bench testing: they let the current-limited power supply stand in where the battery goes, so the whole power chain is proven before a cell is ever connected. ⚠️ **Verify polarity with the meter, not wire color** — generic JST-PH leads are frequently wired opposite to Adafruit's convention. |
| **LuminologyPro resistor kit**, 25 values, 1/4 W | 1000 | Pull-up and pull-down resistors. 10 kΩ holds the I²S bit clock line (a boot-strap pin) at a defined level and pulls up the button; 100 kΩ pulls down the microphone data line. Without these the board can boot unpredictably. |
| **BOJACK ceramic capacitor kit** | 650 | Local decoupling — small capacitors placed at each module's power pins that supply the instantaneous current spikes digital chips demand, which long wires cannot deliver fast enough. 100 nF and 10 µF are the values used here. |
| **ALLECIN electrolytic capacitor kit**, 24 values | 1 kit | Bulk energy storage. The 220 µF sits at the amplifier's power input as a reservoir for bass notes and Wi-Fi transmit bursts, which would otherwise drag the shared battery rail down and reset the processor. |

**Buying both cell sizes was the right call.** Bench the real current draw
first, then fit whichever pack the numbers justify. Keep the unused pair
sealed and terminal-protected.

# 3 · Frame, insulation, and wire

| Item | What it is and why it is here |
| --- | --- |
| **K&S #9831 brass tube**, 1.5 mm OD × 0.225 mm wall × 300 mm, 4 tubes | The frame itself — the exposed brass cage that gives the device its look and holds everything together. The reference build's exact stock. The wall is only 0.225 mm, so it must be cut with the jeweler's saw; flush cutters crush it. ASIN verified to resolve to 9831 and not a wrong-diameter variant. |
| **K&S 1.0 mm round brass rod**, 5 rods | Corner posts and cross braces. Solid rod, so it is stiffer than the tube and telescopes inside it (tube ID ≈ 1.05 mm) for clean joints. |
| **XFJYMXDM fish paper**, 16.4 ft | Flame-rated electrical insulation board that lines the battery bay. This is the mandatory barrier between the lithium cell and everything else — the one insulation layer that is a safety requirement rather than good practice. |
| **ELEGOO polyimide (Kapton) tape**, 4-pack | High-temperature insulating tape for module backs and anywhere a wire crosses brass. Survives soldering heat without melting, unlike vinyl electrical tape. |
| **Pointool heat-shrink tubing kit**, 14 sizes, **white** | Tubing that shrinks tightly around a solder joint when heated, insulating it and adding a little strain relief. White matches the intended finish. |
| **TUOFENG 26 AWG silicone wire**, 6 colors, 33 ft each | The power wiring — battery bus and any load-carrying run. Thicker than the signal wire for mechanical robustness at the connection you least want to fail. Silicone insulation stays flexible and resists soldering-iron burns. |
| **CBAZY 30 AWG silicone wire**, 6 colors, 32.8 ft each | The signal wiring — I²C to the display, I²S to the microphone and amplifier, and the button. Thin and flexible so 15+ conductors can be routed inside a 45 mm cage without levering on fragile breakout pads. |

### Wire-gauge note — current is not the deciding factor

The "26 AWG for power" rule came from the withdrawn R0 design, which pushed
~1.15 A through a long chain. The current frame is ~45 mm and the chain is
three parts, so on **current** either gauge is comfortable:

| | 30 AWG | 26 AWG |
| --- | ---: | ---: |
| Resistance | ~0.34 Ω/m | ~0.13 Ω/m |
| Loop drop @ 0.8 A peak, 160 mm | 43 mV | 17 mV |
| Loop drop @ 150 mA average | 8 mV | 3 mV |

Both are far inside the ≤300 mV upstream-drop screen. The real trade is
**mechanical**: 26 AWG resists nicking and fatigue on the battery bus, while
30 AWG routes without stressing pads on the signal side. Both are on hand —
use each where it belongs, and strain-relieve every conductor either way.

# 4 · Tools — soldering

| Item | What it is and why it is here |
| --- | --- |
| **X-Tronic 3020-XTS station** + 5 tips, solder roll, solder sucker, tweezers, 2 helping hands, silicone mat | Temperature-controlled soldering iron and the bench kit around it. Temperature control matters because a MEMS microphone and an OLED flex tail are heat-sensitive. The helping hands hold parts while both of yours are busy; the silicone mat is the only heat-safe work surface you own. |
| **MAIYUM 63/37 rosin-core solder**, 0.8 mm, 100 g | Electronics solder. The 63/37 tin-lead alloy melts lower and wets faster than lead-free, meaning less time with a hot iron pressed against fragile parts. Wash hands, do not eat at the bench, ventilate. |
| **Chip Quik CQ4LF no-clean flux pen**, 10 ml | Flux chemically strips oxide off metal so solder actually bonds instead of balling up. "No-clean" residue is safe to leave on electronics. ⚠️ Duplicate — one was already owned. |
| **Harris SCLF4 Stay-Clean flux**, 4 oz | A far more aggressive **acid** (zinc-chloride) flux, needed because brass oxidizes too fast for rosin flux to handle. **Empty brass frame only — never near electronics.** It is corrosive and must be washed off and neutralized with baking soda, or it will eat the joints and blister any paint later. |

# 5 · Tools — measurement

| Item | What it is and why it is here |
| --- | --- |
| **KAIWEETS TRMS multimeter**, 6000 counts, + hard case | The most important instrument in the build. Every safety step is a meter step: battery polarity before the first connection, checking the brass frame is isolated from every circuit, continuity, switch voltage drop, charge termination voltage. Nothing electrical gets connected without it. |
| **SKY TOPPOWER DC supply**, 0–30 V / 0–5 A | An adjustable, **current-limited** bench power supply that substitutes for the battery during testing. If something is wired wrong it politely limits current instead of dumping a lithium cell's full energy into the fault. This is what lets the entire power chain be proven before a cell is ever installed. |
| **NEIKO digital caliper**, 0–6" | Measures parts to a hundredth of a millimetre. Every module, board, and connector needs its real measured size before the frame geometry can be trusted — listing dimensions are frequently wrong. |
| **REXQualis breadboards**, 4 pcs (830 + 400 point) | Solderless boards for wiring the full circuit temporarily. The entire risk-reduction strategy is *prove the stack on a breadboard before soldering anything permanent*. |
| **TODOELEC Dupont jumper kit**, 120 wires, 10 cm | Pre-terminated jumper wires for breadboarding. Bench use only — not for final assembly, and never for the speaker output or high-current runs. |

# 6 · Tools — fabrication and safety

| Item | What it is and why it is here |
| --- | --- |
| **SE 3-in-1 jeweler's saw** + 144 blades + V-slot bench pin with clamp | The only correct way to cut 0.225 mm-wall brass tube — a fine-toothed blade removes material without crushing the tube. The bench pin clamps to the table and supports small work while you cut. |
| **WORKPRO jewelry pliers**, 3-pack | Round-nose and chain-nose pliers for bending brass into the frame's rectangles and forming braces. Round jaws make smooth curves without kinking the tube. |
| **Hakko CHP CSP-30-1 wire stripper**, 30–20 AWG | Removes insulation without nicking the conductor. Sized correctly for both wire gauges here; a blade or generic stripper nicks fine strands, which then break later inside a sealed frame. |
| **QWORK mini heat gun**, 300 W, with stand | Shrinks the heat-shrink tubing. Directed hot air is controllable in a way a lighter is not — no soot, no scorching adjacent insulation. |
| **SHJADE hot glue gun**, 20 W mini, + 30 sticks, white | Low-temperature adhesive for retaining modules in the frame — the reference build's own method. Low-temp matters near plastic module bodies and the OLED. Keep glue away from the microphone port, the switch mechanism, and connectors. |
| **SE 10-piece diamond needle file set**, 150 grit, 744DF-R | Small shaped files for deburring cut tube ends and fine shaping. ⚠️ **See the note below — diamond is not ideal for brass.** |
| **3M Solus 1000 safety glasses**, clear | Eye protection for sawing, filing, and clipping wire, all of which throw metal fragments. Wear them; the saw is the sharpest thing on the bench. |

### ⚠️ Note on the diamond file set

Diamond files cut by holding abrasive grit in a metal surface. Soft metals —
brass, copper, aluminium — pack into the gaps between the grit and the file
stops biting. They are excellent on glass, stone, and hardened steel, and they
will do light deburring on brass, but they will load up and dull with repeated
use.

This is not a problem to fix urgently:

- **Clean them** with a stiff brass brush when they load up, and they keep working.
- **Sandpaper does most of this job anyway.** Deburring a thin tube end is
  mostly a few strokes of 400–800 grit wet/dry, which is still on the buy list.
- **If filing gets frustrating**, a steel needle file set in cut 2 is about
  $10 and is the correct tool for brass.

Keep the diamond set — it earns its place on the harder materials.

---

## Still needed

Consumables only. None of this blocks the bench phase.

| Item | Why | Approx. |
| --- | --- | ---: |
| **IPA 91 %+ · swabs · baking soda** — buy **locally** (pharmacy + grocery) | **Safety-relevant** — baking soda neutralizes the Harris acid flux, IPA rinses it off. Residue left on brass corrodes joints and blisters paint. 70 % IPA has too much water | ~$6 |
| **400–800 wet/dry sandpaper** | Deburring is a safety step — no sharp brass edge may reach the battery. Also keys the surface if you paint | ~$8 |
| **Solder wick** — [JoTownCand 3-pack, 3 widths](https://www.amazon.com/JoTownCand-Premium-Desoldering-Residue-Solder/dp/B0DRN688Q5) | Braided copper that lifts solder off a joint when you make a mistake. The 0.08" width suits OLED and microphone pads | ~$8 |
| **USB-A-to-C data cable** — [Rankie USB 3.0, 3-pack](https://www.amazon.com/Rankie-USB-C-Charging-Transfer-3-Pack/dp/B01JRY0VE4) | Flashing the board. Clone boards ship CC-resistor bugs that make C-to-C cables power-only; "3.0" guarantees data lines. A charge-only cable makes a working board look dead | ~$10 |
| Gel cyanoacrylate (super glue) | Spot-bonding where hot glue is too bulky | ~$5 |

### Optional — white/silver finish

Rust-Oleum 249322 self-etch primer → 2081830 gray primer → 7791830 satin white
(~$24; buy in person, NYC Admin Code §10-117 keeps spray paint 21+ and locked),
plus white styrene sheet for guards (~$10, Blick or Canal Plastics).

---

## What to do first

The bench supply is the latest-arriving item, but it only gates the **power**
tests. Everything digital runs from USB:

1. **Now:** build the firmware — `cd firmware && ./scripts/prepare.sh &&
   ./scripts/build.sh`. No hardware required.
2. **Now:** decide the backend question. The default cloud service receives
   your microphone audio; self-hosting is the alternative.
3. **As boards arrive:** `esptool flash_id` on several SuperMinis (≥ 4 MB
   gate), flash one bare, provision Wi-Fi, pair, confirm one voice round trip.
4. **Then:** breadboard OLED + microphone + amplifier + speaker at low volume.
5. **When the supply lands:** the current-limited sweep, then the
   500-vs-1200 mAh decision from measured numbers.

Both battery packs stay sealed and terminal-protected until step 5. Nothing
gets soldered into a frame before the breadboard stack works end to end.
