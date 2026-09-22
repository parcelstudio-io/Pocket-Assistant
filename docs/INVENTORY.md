# Purchased inventory — what is in hand and what each item is for

> **Factual purchase record, last updated 2026-09-21.** This tracks what was
> *bought*, not what is *approved*. It takes no side in the R1/F0 design fork —
> part-selection authority stays in
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md). Mark items off
> as boxes arrive and incoming inspection passes.

**Status: the recorded orders provide a starting set for the USB prototype.**
Check what has actually arrived before each session. This inventory does not
establish a complete battery-powered design. Start with the
[action-only fast track](../plan/FAST_TRACK.md), using what is already owned;
software setup needs no new purchase, while the first physical boot needs any
proven USB data cable.

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
| Amazon #9 | Sep 21 | Rigol DHO802 oscilloscope, [B0CKX699F5](https://www.amazon.com/dp/B0CKX699F5); price paid not recorded |
| Amazon #10 | Sep 21 | BAISDY 45-piece wet/dry sandpaper, 400–3000 grit ([B07D2YYC11](https://www.amazon.com/dp/B07D2YYC11)) · JoTownCand solder wick 3-pack ([B0DRN688Q5](https://www.amazon.com/dp/B0DRN688Q5)) · Epic Medical Supply 91% isopropyl alcohol, 2 × 16 oz ([B0BSJ93RKB](https://www.amazon.com/dp/B0BSJ93RKB)); prices not recorded |
| DigiKey | Sep 21 | 5 × Same Sky `CES-20134-088PM` speaker, 2223-CES-20134-088PM-ND, $4.10 each — $20.50 |
| Amazon #12 | Sep 21 | Rust-Oleum Stops Rust spray paint, 12 oz: `7789830` gloss canvas white ([B000PIG3AS](https://www.amazon.com/dp/B000PIG3AS)) and `7791830` satin white ([B000Z8FGII](https://www.amazon.com/dp/B000Z8FGII)); prices not recorded |

Estimated total spend: **≈ $635–660**, plus the DHO802 (Rigol list price $329; the price paid is not recorded here), $20.50 for five more speakers, and the 21 September Amazon consumables (prices not recorded).

---

# 1 · Electronics

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **Meshnology ESP32-C3 SuperMini** dev board | 10 | The brain. A postage-stamp ESP32-C3 board with Wi-Fi, native USB-C, and the GPIO layout the firmware targets. It runs the assistant, talks to the cloud backend, and drives every peripheral. **Gate each board with `esptool flash_id` — reject anything under 4 MB flash**, and reject any "Plus" variant with an RGB LED on GPIO8, which breaks this pin map. ⚠️ **2026-09-21: the received boards carry a ceramic chip antenna and hit the SuperMini's documented Wi-Fi range problem.** The red rectangular block at the end opposite USB is the antenna; there is no U.FL socket and no PCB trace antenna on these. The SuperMini design is widely reported to leave too little clearance around that antenna and to place it too close to other components, so the board interferes with itself — see [Elektor's antenna mod](https://www.elektormagazine.com/articles/boosting-wifi-range-of-the-esp32c3-supermini-antenna-mod). Symptom here: Step 10 provisioning logged `WifiConfigurationAp: Access Point started` and the OLED showed the config screen, but no phone or laptop could see the SSID at any distance — on three separate boards from this pack (A1 in the breadboard, and two spares bare on an open desk), so it is the batch, not one unit or the wiring. Keep the antenna end clear of jumper wires, modules and metal; a 31 mm quarter-wave wire mod recovers 6-10 dB if clearance alone is not enough. **What worked on A1 (2026-09-21, builder-reported, not instrument-verified):** capping Wi-Fi transmit power at 8.5 dBm (`esp_wifi_set_max_tx_power(34)`, quarter-dBm units) made the hotspot visible, A1 was provisioned onto Wi-Fi, and one spoken question returned a remote response (PASS 10C, same day); the source build now applies that cap after every radio start, so try the current assistant build before any wire mod. Ten boards means you can afford to throw out bad clones. **VBUS-01, 2026-09-22 (builder-measured on A1, diode mode):** A1's `5V` pin is wired directly to the USB-C VBUS, with no diode: 0.001 V with red on VBUS and 0.002 V with the probes swapped, beeping both ways. This matches the published SuperMini schematic ([sigmdel.ca](https://sigmdel.ca/michel/ha/esp8266/super_mini_esp32c3_en.html)), which shows VBUS tied straight to the `5V` header pin. Anything connected to `5V` is therefore connected to the computer's USB port. |
| **Hosyond SSD1306 OLED**, 0.96" 128×64 I²C, white | 5 | The screen — the device's only visual output, showing state, the pairing code, and responses. White pixels on black glass are also the intended white/silver accent. Firmware probes both `0x3C` and `0x3D`, so either address works. **Read the silkscreen pin order before wiring**: vendors ship GND-VCC-SCL-SDA *and* VCC-GND-SCL-SDA on identical-looking boards. |
| **AITRIP INMP441** I²S MEMS microphone | 5 | The ears. A digital microphone that outputs I²S directly, so no analog audio wiring is needed. This is the creator's exact part. Tie `L/R` to GND to select the left slot; data goes to GPIO4. **Keep flux, IPA, glue, paint, and compressed air away from the acoustic port** — contaminating it is permanent. |
| **HiLetgo MAX98357** I²S class-D amplifier | 3 | Converts I²S to speaker output. Used in fast-track Step 11, powered only from the controller's `5V` pin; keep it disconnected before Step 11. Its supply range alone does not define a complete power circuit. Later inspect the exact carrier's gain and `SD/MODE` network: shutdown can be intentional, and mono-mix can attenuate left-only source audio. Do not change the mode or power it from a raw cell based on this inventory. |
| **Same Sky CES-20134-088PM** speaker, 8 Ω 0.8 W | 6 | The mouth. A factory-enclosed micro-speaker — the sealed rear cavity is what makes it audible at this size, and it removes the hardest acoustic problem in the build. 20 × 13 × 4.87 mm, top-firing, with two mounting flanges and a built-in dust mesh. Ships with 60 mm of 32 AWG lead, longer than the whole device, so **it needs no wire from you**. Cap output at ≤ 2.53 V RMS differential to respect the 0.8 W rating. One bought 2026-09-02; five more bought 2026-09-21 from DigiKey at $4.10 each, so no single unit is irreplaceable. Still never cut the leads of a unit you intend to use. |
| **QTEATAK tactile push buttons** | 420 | The only user control: a momentary button on GPIO10 to ground. Short press toggles chat, long press resets Wi-Fi. Pick a white cap to match the finish. Note the onboard GPIO9 button is ROM BOOT, not this input. |
| **2.54 mm male breakaway header pins** | 22 | Snap-apart pin strips for soldering onto modules so they can plug into a breadboard. Makes the whole Phase 0 bench stack reversible instead of permanent. |

# 2 · Power

| Item | Qty | What it is and why it is here |
| --- | ---: | --- |
| **Adafruit #1578** LiPo 3.7 V **500 mAh**, protected | 2 | Previously purchased compact battery candidate, nominally 29 × 36 × 4.75 mm. Keep disconnected and terminal-protected. The current material review records a 0.5 A maximum continuous-discharge rating and rejects it for the former estimated load; ownership is not permission to use it. Never solder to or alter its factory lead. |
| **Adafruit #258** LiPo 3.7 V **1200 mAh**, protected | 2 | The margin battery option, 34 × 62 × 5 mm. Roughly 1.2 A capable and more than twice the runtime, but 62 mm long — longer than the intended device — so fitting it changes the silhouette. Buying both sizes turns the capacity-vs-size argument into a measurement. |
| **Adafruit #4410** USB-C Micro-Lipo charger | 1 | Purchased LiPo charger, with a default 100 mA setting and no load sharing. Store separately from the USB prototype. A future charging arrangement needs its own wiring procedure; the slide-switch OFF position alone is not evidence of source isolation. Leave the charge-rate jumper unchanged. |
| **Chanzon SPDT mini slide switch** | 25 | Purchased switch samples. Useful for unpowered continuity exercises; not selected to carry the final device's battery current. The beginner prototype turns off by unplugging its USB cable. |
| **daier JST-PH 2.0 mm** 2-pin connector cables | 20 pr | Mating connectors for the battery. Their real value is bench testing: they let the current-limited power supply stand in where the battery goes, so the whole power chain is proven before a cell is ever connected. ⚠️ **Verify polarity with the meter, not wire color** — generic JST-PH leads are frequently wired opposite to Adafruit's convention. |
| **LuminologyPro resistor kit**, 25 values, 1/4 W | 1000 | Pull-up and pull-down resistors. 10 kΩ holds the I²S bit clock line GPIO2 (a boot-strap pin) at a defined level; 100 kΩ pulls down the microphone data line GPIO4. The action button needs no external resistor: it goes from GPIO10 to GND and the firmware enables the chip's internal pull-up (as wired and passed in fast-track Step 6). Without these the board can boot unpredictably. |
| **BOJACK ceramic capacitor kit** | 650 | Local decoupling — small capacitors placed at each module's power pins that supply the instantaneous current spikes digital chips demand, which long wires cannot deliver fast enough. 100 nF and 10 µF are the values used here. |
| **ALLECIN electrolytic capacitor kit**, 24 values | 1 kit | Bulk energy storage. The 220 µF sits at the amplifier's power input as a reservoir for bass notes and Wi-Fi transmit bursts, which would otherwise drag the shared battery rail down and reset the processor. |

Both cell sizes remain stored and terminal-protected. Portable battery power is
out of scope for this prototype by the builder's decision of 2026-09-21. Battery selection is later work and depends on a complete power
design and measured demand.

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
| **JoTownCand solder wick**, 3-pack, 3 widths, bought 2026-09-21 | Braided copper that lifts solder off a joint: the way to clear a bridge or remove header pins. Use the narrowest width on OLED, microphone and amplifier pads, with a touch of flux, and cut off the used end each time. |
| **Epic Medical Supply 91% isopropyl alcohol**, 2 × 16 oz, bought 2026-09-21 | Cleans flux residue off boards and rinses the brass after acid flux. 91% has little enough water to evaporate cleanly; keep it away from the microphone's acoustic port and away from flame or a hot iron. |
| **X-Tronic 3020-XTS station** + 5 tips, solder roll, solder sucker, tweezers, 2 helping hands, silicone mat | Temperature-controlled soldering iron and the bench kit around it. Temperature control matters because a MEMS microphone and an OLED flex tail are heat-sensitive. The helping hands hold parts while both of yours are busy; the silicone mat is the only heat-safe work surface you own. |
| **MAIYUM 63/37 rosin-core solder**, 0.8 mm, 100 g | Electronics solder. The 63/37 tin-lead alloy melts lower and wets faster than lead-free, meaning less time with a hot iron pressed against fragile parts. Wash hands, do not eat at the bench, ventilate. |
| **Chip Quik CQ4LF no-clean flux pen**, 10 ml | Flux chemically strips oxide off metal so solder actually bonds instead of balling up. "No-clean" residue is safe to leave on electronics. ⚠️ Duplicate — one was already owned. |
| **Harris SCLF4 Stay-Clean flux**, 4 oz | A far more aggressive **acid** (zinc-chloride) flux, needed because brass oxidizes too fast for rosin flux to handle. **Empty brass frame only — never near electronics.** It is corrosive and must be washed off and neutralized with baking soda, or it will eat the joints and blister any paint later. |

# 5 · Tools — measurement

| Item | What it is and why it is here |
| --- | --- |
| **KAIWEETS TRMS multimeter**, 6000 counts, + hard case | The most important instrument in the build. Every safety step is a meter step: battery polarity before the first connection, checking the brass frame is isolated from every circuit, continuity, switch voltage drop, charge termination voltage. Nothing electrical gets connected without it. |
| **SKY TOPPOWER DC supply**, 0–30 V / 0–5 A | An adjustable, **current-limited** bench power supply that substitutes for the battery during testing. If something is wired wrong it politely limits current instead of dumping a lithium cell's full energy into the fault. This is what lets the entire power chain be proven before a cell is ever installed. |
| **Rigol DHO802 oscilloscope**, 70 MHz, 2 channels + external trigger, 12-bit, two PVP3150 10X probes, bought 2026-09-21, **not yet received** | Shows voltage against time, which the multimeter cannot: clock edges, rail dips during Wi-Fi bursts, power-up order, and the speaker's differential signal. Two channels with both probe grounds on circuit ground plus its A−B math give the differential-safe speaker measurement the audio gate asks for; **never clip a probe ground to either speaker lead**. Its Single trigger mode catches one-off start-up events. Powered from a USB-C 15 V adapter; before first use, meter whether the BNC shells connect to the adapter's earth and to the rear GND terminal, and record the answer. Warranty three years on the mainframe, not the probes. It does not measure millisecond current peaks or log a charge cycle. |
| **NEIKO digital caliper**, 0–6" | Measures parts to a hundredth of a millimetre. Every module, board, and connector needs its real measured size before the frame geometry can be trusted — listing dimensions are frequently wrong. |
| **REXQualis breadboards**, 4 pcs (830 + 400 point) | Use for resistor labs and the controller's button/OLED/microphone connections. Check split power rails and header joints before use. Amplifier supply and speaker current do not go through breadboard contacts. Loose module headers must be soldered and inspected before jumper testing. |
| **TODOELEC Dupont jumper kit**, 120 wires, 10 cm | Pre-terminated jumper wires for breadboarding. Bench use only — not for final assembly, and never for the speaker output or high-current runs. |

**Instrument decision, 2026-09-21:** the DHO802 is the last instrument purchase. The purchase authority's remaining `ARRANGE` instruments — the fast current meter, the calibrated charge-voltage logger, and the three-channel temperature logger — are to be borrowed or rented if needed. Until access exists, the gates that name them stay closed.

# 6 · Tools — fabrication and safety

| Item | What it is and why it is here |
| --- | --- |
| **SE 3-in-1 jeweler's saw** + 144 blades + V-slot bench pin with clamp | The only correct way to cut 0.225 mm-wall brass tube — a fine-toothed blade removes material without crushing the tube. The bench pin clamps to the table and supports small work while you cut. |
| **WORKPRO jewelry pliers**, 3-pack | Round-nose and chain-nose pliers for bending brass into the frame's rectangles and forming braces. Round jaws make smooth curves without kinking the tube. |
| **Hakko CHP CSP-30-1 wire stripper**, 30–20 AWG | Removes insulation without nicking the conductor. Sized correctly for both wire gauges here; a blade or generic stripper nicks fine strands, which then break later inside a sealed frame. |
| **QWORK mini heat gun**, 300 W, with stand | Shrinks the heat-shrink tubing. Directed hot air is controllable in a way a lighter is not — no soot, no scorching adjacent insulation. |
| **SHJADE hot glue gun**, 20 W mini, + 30 sticks, white | Low-temperature adhesive for retaining modules in the frame — the reference build's own method. Low-temp matters near plastic module bodies and the OLED. Keep glue away from the microphone port, the switch mechanism, and connectors. |
| **SE 10-piece diamond needle file set**, 150 grit, 744DF-R | Small shaped files for deburring cut tube ends and fine shaping. ⚠️ **See the note below — diamond is not ideal for brass.** |
| **BAISDY wet/dry sandpaper**, 45 sheets, 400–3000 grit, bought 2026-09-21 | Deburrs every cut brass edge so none can cut a wire or a hand; 400–800 does the deburring, the finer grits polish or key a surface before paint. Sand brass wet or with a mask, well away from the electronics. |
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
  mostly a few strokes of 400–800 grit wet/dry, now in hand (bought 2026-09-21).
- **If filing gets frustrating**, a steel needle file set in cut 2 is about
  $10 and is the correct tool for brass.

Keep the diamond set — it earns its place on the harder materials.

---

## Still needed

A working data cable was proven at fast-track Step 3, and the 21 September
order covered the wick, sandpaper and alcohol, so nothing below blocks the
build. What remains is small and local.

| Item | Why | Approx. |
| --- | --- | ---: |
| **Swabs · baking soda** — buy **locally** (pharmacy + grocery) | Needed only if the frame is soldered with the Harris acid flux: baking soda neutralizes it and the owned 91% IPA rinses it off. Residue left on brass corrodes joints and blisters paint | ~$5 |
| Gel cyanoacrylate (super glue) — optional | Spot-bonding where hot glue is too bulky; keep it and its fumes away from the microphone port and the OLED glass | ~$5 |
| USB-A-to-C data cable, spare — optional | One proven cable is enough; a spare helps once one stays plugged into the finished device | ~$10 |

### Optional — white/silver finish

White system. **Bought 2026-09-21:** both topcoats, Rust-Oleum `7789830` gloss
canvas white, a warm off-white, and `7791830` satin white. **Not bought:** the
`7780830` white primer. The Rust-Oleum 249322 dark-green self-etching primer
was ordered and then canceled the same day.

1. Sand the bare brass with the owned 400–600 wet/dry and wipe it with the owned
   91% IPA, so the paint has a clean, keyed surface.
2. Rust-Oleum `7780830` Stops Rust Clean Metal Primer, flat white
   ([B000Z8C3PM](https://www.amazon.com/dp/B000Z8C3PM)).
3. One topcoat, chosen on the test coupons: Rust-Oleum `7791830` satin white
   ([B000Z8FGII](https://www.amazon.com/dp/B000Z8FGII)) or `7789830` gloss
   canvas white ([B000PIG3AS](https://www.amazon.com/dp/B000PIG3AS)). Use one
   sheen on the whole frame.

Without an etching primer, adhesion on smooth non-ferrous brass is the open
question, so the finish stays gated: spray test coupons cut from brass offcuts
first and check that the paint does not lift, and paint the frame only after
the fit and Wi-Fi checks pass. If the coupons peel, an etching primer returns
under the white coats. NYC Admin Code §10-117 keeps spray paint 21+ and locked.
Spray the empty frame outdoors or with strong ventilation, never with
electronics installed, and store cans away from the soldering iron and heat
gun. White styrene sheet for guards (~$10, Blick or Canal Plastics) remains
optional.

---

## What to do first

Follow the [action-only fast track](../plan/FAST_TRACK.md): identify and flash
one bare controller, prepare reliable headers, add the button and OLED, then
observe microphone levels in the offline diagnostic firmware. This uses the
controller's USB supply and needs no cloud account, amplifier, battery, or
enclosure. Save a wiring photograph and the serial output at each step. The
[USB prototype quickstart](PROTOTYPE_QUICKSTART.md) remains the compact
technical reference.

After those local tests pass, the regular source firmware provides the next
software/backend experiment. Speaker output and portable power remain separate
integration tasks; buying the parts did not verify them.
