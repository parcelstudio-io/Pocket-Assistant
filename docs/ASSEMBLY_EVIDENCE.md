# Why the R1 assembly was proposed — archived evidence

> **SUPERSEDED DESK STUDY; NOT PROOF OF A SAFE ASSEMBLY.** The independent
> audit found unresolved cell-current, USB-source, regulator, switch, and audio
> issues in this compact architecture. `hardware_tested` remains `false`.
> Use [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md) for the
> current Phase 0 decision and promotion gates; the discussion below is kept
> so Claude can inspect the prior reasoning.

Three things set the honest ceiling on all of this:

1. **The reference device exists.** Someone built this from these part classes
   and it talks. We are not inventing an architecture; we are correcting a
   known-working one. That is the single strongest piece of evidence available.
2. **Nothing here has run on physical hardware in this workspace.**
   `firmware/source-build.json` records `"hardware_tested": false`. Every
   number below is a datasheet calculation or a static check.
3. **Therefore Phase 0 is not optional.** It converts this document from
   argument into evidence.

---

## The machine checks you can re-run

| Check | Command | What it proves |
| --- | --- | --- |
| Firmware builds reproducibly | `cd firmware && ./scripts/build.sh` | The corrected source compiles with the pinned ESP-IDF v6.0.2 and produces a byte-identical image across clean builds |
| Static wiring checks | `python3 tools/netcheck.py` | GPIO/protocol constraints hold (pins, sample rate, strap rules). It does not check power, fit, or acoustics |
| Stale placement study | `freecadcmd cad/fitcheck.py` | **Stale** — models the withdrawn R0 architecture. Regenerate from measured R1 parts before treating any output as fit evidence |

---

## Phase 0 — bench bring-up

**Why it comes first:** every irreversible step (cutting brass, soldering a
frame, painting) is downstream of assumptions that a breadboard settles in an
afternoon and a finished sculpture makes expensive.

| Step | Evidence it rests on | What failure looks like |
| --- | --- | --- |
| `esptool flash_id` ≥ 4 MB | The partition table fills exactly 4 MB (`firmware/partitions/pocket-ai-4m.csv`) | Flash fails to write; a 2 MB clone bricks at boot |
| Confirm plain SuperMini | Only listing text distinguishes variants; a U.FL socket or RGB LED means a different board | Wrong pin map |
| I²C scan finds the display | Firmware probes 0x3C then 0x3D and falls back to headless (`pocket_wall_e_c3.cc`) | Neither address answers → check the module's silkscreen pin order |
| Mic records, amp plays | Datasheet agreement at 16 kHz (below) | Silence → meter the amp's `SD` pin |
| Bench power sweep 4.2 → 3.3 V under load | The LDO-direct rail analysis below | Reset during Wi-Fi burst → more bulk capacitance, then a bigger pack |
| Backend round trip | `CONFIG_OTA_URL` defaults to a third-party service | A beautiful object that cannot talk |
| Speaker choice | Same Sky publishes it plainly: *"Enclosure: Required"* — an unbaffled driver's front and back waves cancel | The phone-speaker fallback audible only held to your ear |

---

## The audio path — why 16 kHz is the only rate that works

Three parts must agree on one number, because they share one set of clocks.

| Part | Constraint | At 16 kHz |
| --- | --- | --- |
| MAX98357A | Datasheet, verbatim, twice: *"LRCLK clocks at 11.025kHz, 12kHz, 22.05kHz and **24kHz are NOT supported**"*; supported windows are 8, 16, 32, 44.1, 48, 88.2, 96 kHz | 16 kHz sits dead-centre in its fS2 window ✅ |
| INMP441 | Needs exactly 64 SCK per frame; SCK range 0.5–3.2 MHz | 16 000 × 64 = 1.024 MHz ✅ |
| Xiaozhi firmware | Opus voice encoder is hard-coded to 16 kHz | No input resampler needed; server audio uses the existing output resampler ✅ |

**The original build runs 24 kHz** — recovered from the vendor image
(`firmware/README.md`). The reference device sits on an operating point its
own amplifier's datasheet excludes. It evidently works, but nothing
guarantees it across part lots or temperature. 16 kHz is two numbers in
`config.h` and costs nothing: telephony and voice assistants live there.

`netcheck.py` enforces both constraints, so this cannot silently regress.

**The shared-clock trick works** because the ESP32-C3's I²S peripheral is
full-duplex: it transmits speaker samples and receives microphone samples in
the same frame. Four wires do the work of six. The one hazard: wire each clock
as a separate stub to each module, never daisy-chained — the amplifier's
datasheet warns that losing LRCLK while BCLK runs produces *"a large DC output
voltage"*, and DC is how voice coils die.

**Digital-audio correction:** the archived R1 review misapplied an Espressif
copy-mono comment. The pinned codec requests mono DMA with
`I2S_STD_SLOT_LEFT`, while the pinned ESP-IDF enables TX copy-mono only for a
`BOTH` slot mask. Source inspection therefore predicts active left and inactive
right TX slots. Hardware capture remains required, and the #3006 default mix
must not be assumed to produce full amplitude. See
    [the audio lesson](../edu/04-audio.md#exact-module-channel-and-gain-configuration).

---

## The power path — the R1 numbers

The released chain is deliberately the reference's chain with a documented
protected pack:

```text
pack (3.0–4.2 V, PCM inside) → slide switch → SuperMini 5V pin → LDO → 3.3 V
                                            → MAX98357A VIN (2.5–5.5 V rated)
```

**Why each interface closes:**

| Interface | Evidence |
| --- | --- |
| Amp on the raw cell rail | MAX98357A datasheet: 2.5–5.5 V supply. 3.0–4.2 V sits inside it with margin on both ends |
| MCU/OLED/mic on the LDO | All three are 3.3 V parts. Above ~3.4 V cell the LDO regulates; below it the rail follows the cell minus dropout, and the ESP32-C3 runs to ~3.0 V. The reference device operates this way for its whole discharge |
| Peak load vs the pack | Worst coincident estimate: Wi-Fi TX ~335 mA (ESP32-C3 datasheet, 802.11b @21 dBm) + volume-limited amp peaks ~300–400 mA + OLED ~25 mA ≈ **0.7–0.8 A** transient at the cell — ~1.5C pulses on the 500 mAh pack. Short and infrequent; the bench sweep is the proof, and the 220 µF bulk cap carries the microseconds |
| Over-discharge | Pack PCM cuts at 3.0 V — below the useful operating floor anyway, so the device browns out (and the display dies) before the cell is endangered |
| Charging | #4410: CC/CV, 4.2 V termination, 100 mA default (0.2C) / 500 mA jumper (1C, the pack page's stated maximum). Device off while charging because there is no load sharing |
| Fault current | Pack PCM short-circuit protection + the JST as a hard disconnect. No separate fuse fitted — at these energies and with the pack's own protection, a fuse guards mainly against wiring errors the unpowered continuity check catches first |

**Runtime:** idle-listening ~130–150 mA at the cell → **≈ 3 h** on 500 mAh.
An estimate until measured; the R0 5–6 h figure assumed the withdrawn 950 mAh
16340.

**What was given up vs the withdrawn converter chain, knowingly:** regulation
of the last ~10 % of cell capacity (LDO dropout region), electronic UVLO
ahead of the PCM, and reverse-cell protection (the keyed JST connector and the
polarity check before first mating replace it). What was gained: roughly half
the device volume, five fewer failure-prone parts, and a build a beginner can
actually solder. The full trade-off record is in
[FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md).

---

## Why the pin map is safe

| Pin | Use | Evidence |
| --- | --- | --- |
| GPIO4 | mic data in | Moved off GPIO8. ESP32-C3 datasheet Table 3-3 marks GPIO2/8/9 as strapping pins; GPIO8 also carries the SuperMini's onboard LED. This build has **no OTA partitions**, so USB download mode is the only recovery path — losing it inside a soldered frame is permanent |
| GPIO2 | I²S BCLK | Strapping pin, so it gets a 10 kΩ pull-up per Espressif's schematic checklist |
| GPIO20/21 | I²C | Firmware `config.h`; verified against the netcheck |
| GPIO10 | action button | The firmware's only user input — chat toggle *and* long-press Wi-Fi reset |
| 11–17, 18–19 | untouched | SPI flash and native USB; netcheck asserts this |

A fair caveat from the adversarial pass: because this build sets
`CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y`, esptool triggers download over USB
without the GPIO8 strap, so a board with an LED on GPIO8 would probably still
flash. Moving the mic to GPIO4 is cheap insurance that also frees GPIO8 to sit
at a defined level — not a fix for a proven failure.

---

## Why the frame is safe

**The frame carries no current.** The video uses the brass as its ground bus;
this build never does. That single decision removes the entire class of faults
where a structural joint becomes an electrical one.

- The pack lives behind a **fish-paper barrier**, connects only by its factory
  JST lead, and is never soldered. JST unplugged for every soldering,
  painting, cleaning, and flashing operation.
- **Paint is not insulation** — no rated dielectric strength, thins to nothing
  on edges, hides whether metal is live. Kapton, fish paper and heat-shrink do
  the insulating; paint (if used at all — the reference is raw brass) is
  decoration.
- Deburring every cut tube end is a safety step, not cosmetics: the acceptance
  rule is that no sharp edge can reach the pack.
- **USB service is physical:** switch off + JST unplugged before the
  SuperMini's port is used. No electronic mux exists to get confused.

**Antenna:** Espressif's layout guidance asks for clearance around the PCB
antenna. Keep the SuperMini's antenna end at the frame's edge with open air
beyond it (the reference does the same), and compare in-frame RSSI against
open air in acceptance test 10.5.

---

## What would falsify this

Honest failure modes, in rough order of likelihood:

1. **The bench sweep resets near 3.3 V under Wi-Fi + audio** → the clone's
   LDO or the pack's sag is worse than the reference's. Fix: more bulk
   capacitance; then a 1000 mAh-class pack; a boost converter is the last
   resort, not the first.
2. **A clone board differs** from its listing photo (LDO, VBUS path, flash
   size). This is why every marketplace part is bought in multipacks and
   qualified, and why the USB rule is procedural rather than trusting a diode
   that may not exist.
3. **The pack doesn't fit the frame you drew** → the cardstock dry-fit
   catches it before brass is cut. The #4237 350 mAh alternate is 7 mm
   shorter.
4. **The speaker is too quiet** through a grille → the A/B and the volume
   limit are set on the bench first.
5. **The backend is unacceptable** — unreachable, or you don't want your
   microphone audio going there. Fix: self-host, or stop at Phase 0.

Each of these is caught on a breadboard, before any brass is cut. That
sequencing is the real safety property of this plan.
