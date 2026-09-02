# Why this assembly works — the evidence behind each step

[BUILD_GUIDE.md](BUILD_GUIDE.md) says *what to do*, keyed to the video.
This says *why it will work*, and what would prove it doesn't. Every claim
traces to a datasheet, a source file in this repository, or a machine check you
can re-run.

Three things are worth stating up front, because they set the honest ceiling on
all of this:

1. **The reference device exists.** Someone built this from these part classes
   and it talks. We are not inventing an architecture; we are correcting a
   known-working one. That is the single strongest piece of evidence available.
2. **Nothing here has run on physical hardware.** `firmware/source-build.json`
   records `"hardware_tested": false`. Every number below is a datasheet
   calculation or a static check.
3. **Therefore Phase 0 is not optional.** It converts this document from
   argument into evidence.

---

## The three machine checks you can re-run

| Check | Command | What it proves |
| --- | --- | --- |
| Firmware builds reproducibly | `cd firmware && ./scripts/build.sh` | The corrected source compiles with the pinned ESP-IDF v6.0.2 and produces a byte-identical image across clean builds |
| Wiring rules hold | `python3 tools/netcheck.py` | **22 rules**: pin map matches the firmware's own `config.h`, no GPIO claimed twice, strapping pins respected, sample rate legal for both audio parts, display address covered, speaker floating, service jumper present, series-resistance budget, PTC hold margin, rail power budget |
| Parts physically fit | `freecadcmd cad/fitcheck.py` | **162 rules** (regenerated 2026-09-01 with the Amazon-part envelopes; 8 tagged PROVISIONAL pending caliper measurement, so it is a planning aid until arrivals are measured): no envelope intersects another or the frame tubes, antenna keep-out honoured, USB corridor clear, cell can be removed, service jumper reachable |

If you change a part, re-run all three. They are wired to each other: the
netcheck reads the firmware's `config.h` directly, so wiring and firmware
cannot silently drift apart.

---

## Phase 0 — bench bring-up

**Why it comes first:** every irreversible step (cutting brass, soldering a
frame, painting) is downstream of assumptions that a breadboard settles in an
afternoon and a finished sculpture makes expensive.

| Step | Evidence it rests on | What failure looks like |
| --- | --- | --- |
| `esptool flash_id` ≥ 4 MB | The partition table fills exactly 4 MB (`firmware/partitions/pocket-ai-4m.csv`) | Flash fails to write; a flash-less clone bricks at boot |
| Confirm plain SuperMini | Only listing text distinguishes variants; a U.FL socket or RGB LED means a different board | Wrong pin map |
| I²C scan finds the display | Firmware probes 0x3C then 0x3D and falls back to headless (`pocket_wall_e_c3.cc`) | Neither address answers → check the module's silkscreen pin order |
| Mic records, amp plays | Datasheet agreement at 16 kHz (below) | Silence → meter the amp's `SD` pin |
| **The chain test** | [The series-resistance budget](../edu/07-the-power-chain.md#the-series-resistance-budget) | Works on a full cell, won't cold-start on a half-empty one |
| Backend round trip | `CONFIG_OTA_URL` defaults to a third-party service | A beautiful object that cannot talk |
| Speaker A/B: pre-boxed vs open | Micro-speaker physics (Same Sky publishes it plainly: *"Enclosure: Required"* — an unbaffled driver's front and back waves cancel) | Audible only if held to your ear |

---

## The audio path — why 16 kHz is the only rate that works

Three parts must agree on one number, because they share one set of clocks.

| Part | Constraint | At 16 kHz |
| --- | --- | --- |
| MAX98357A | Datasheet, verbatim, twice: *"LRCLK clocks at 11.025kHz, 12kHz, 22.05kHz and **24kHz are NOT supported**"*; supported windows are 8, 16, 32, 44.1, 48, 88.2, 96 kHz | 16 kHz sits dead-centre in its fS2 window ✅ |
| INMP441 | Needs exactly 64 SCK per frame; SCK range 0.5–3.2 MHz | 16 000 × 64 = 1.024 MHz ✅ |
| Xiaozhi firmware | Opus voice encoder is hard-coded to 16 kHz | No input resampler needed; server audio uses the existing output resampler ✅ |

**The original build runs 24 kHz** — that rate was recovered from the vendor
image (`firmware/README.md`). So the reference device sits on an operating
point its own amplifier's datasheet excludes. It evidently works, but nothing
guarantees it across part lots or temperature. 16 kHz is two numbers in
`config.h` and costs nothing: telephony and voice assistants live there.

`netcheck.py` enforces both constraints, so this cannot silently regress.

**The shared-clock trick works** because the ESP32-C3's I²S peripheral is
full-duplex: it transmits speaker samples and receives microphone samples in
the same frame. Four wires do the work of six. The one hazard: wire each clock
as a separate stub to each module, never daisy-chained — the amplifier's
datasheet warns that losing LRCLK while BCLK runs produces *"a large DC output
voltage"*, and DC is how voice coils die.

**A correction worth reading:** an earlier version of these notes claimed the
amp's stock (L+R)/2 mode costs 6 dB because the firmware fills only the left
slot. That was wrong. Espressif's `i2s_ll.h` for this chip says verbatim: *"In
mono mode, there only should be one slot enabled, another inactive slot will
transmit same data as enabled slot."* The right slot is a duplicate, so
(L+L)/2 = L at full amplitude. Details and the corrected acceptance test are in
[the audio lesson](../edu/04-audio.md#the-channel-select-pin-sd_mode--and-a-correction).

---

## The power path — the numbers

**Rail budget** (worst case, everything peaking together):

| Load | Peak | Source |
| --- | ---: | --- |
| ESP32-C3, Wi-Fi TX | 335 mA | ESP32-C3 datasheet Table 5-7, 802.11b @21 dBm |
| MAX98357A into 8 Ω | 412 mA | 3.3 V ÷ 8 Ω bridge crest |
| OLED | 25 mA | measured figures for a mostly-lit SSD1306 |
| Mic + amp idle | 6 mA | datasheets |
| **Total** | **778 mA** | |

Against a buck-boost rated ~1.3 A at a 3.0 V input, that is **1.66× margin at
the worst point of the discharge** — not at the comfortable mid-charge point
where vendors quote their numbers.

**Cell side:** 778 mA at 3.3 V ≈ 1.15 A drawn at the ~2.6 V the converter terminal actually sees at end of discharge. The Nitecore
NL169 publishes **2 A max continuous** — 2× margin, from a manufacturer that
actually publishes the number.

**Runtime:** idle-listening averages ~130 mA at the rail ≈ 141 mA from the
cell. Against 950 mAh: **5–6 hours** of always-on listening. Not a day.

**The chain:** the finding that no single part reveals is that the cell, fuse
pair, holder, the two P-FETs and the wiring form 0.355 Ω in series — ~410 mV
lost at the 1.15 A peak — so the converter's input sees ~2.59 V when the cell
reads 3.0 V, and it must *cold start* through that. This is why the design
paralleled two PTCs, moved the mechanical switch out of the power path onto a
FET gate, and treats the converter's startup voltage as a purchase
requirement. Full derivation: [the power-chain lesson](../edu/07-the-power-chain.md).

---

## Why the pin map is safe

| Pin | Use | Evidence |
| --- | --- | --- |
| GPIO4 | mic data in | Moved off GPIO8. ESP32-C3 datasheet Table 3-3 marks GPIO2/8/9 as strapping pins; GPIO8 also carries the SuperMini's onboard LED. This build has **no OTA partitions**, so USB download mode is the only recovery path — losing it inside a soldered frame is permanent |
| GPIO2 | I²S BCLK | Strapping pin, so it gets a 10 kΩ pull-up per Espressif's schematic checklist |
| GPIO20/21 | I²C | Firmware `config.h`; verified against the netcheck |
| GPIO10 | action button | The firmware's only user input — chat toggle *and* long-press Wi-Fi reset |
| 11–17, 18–19 | untouched | SPI flash and native USB; netcheck asserts this |

A fair caveat, from the adversarial pass: because this build sets
`CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y`, esptool triggers download over USB
without the GPIO8 strap, so a board with an LED on GPIO8 would probably still
flash. Moving the mic to GPIO4 is cheap insurance that also frees GPIO8 to sit
at a defined level — not a fix for a proven failure.

---

## Why the frame is safe

**The frame carries no current.** The video uses the brass as its ground bus;
this build never does. That single decision removes the entire class of faults
where a structural joint becomes an electrical one.

- The cell lives in a **holder**, never soldered. Cell out for every soldering,
  painting, cleaning, and flashing operation.
- **Paint is not insulation** — no rated dielectric strength, thins to nothing
  on edges, hides whether metal is live. Kapton, fish paper and heat-shrink do
  the insulating; paint is decoration.
- Fish paper (flame-rated) goes under the cell; polycarbonate (not flame-rated)
  is for sub-plates only.
- The **service jumper** means USB and the converter are never both driving the
  3.3 V rail.
- Deburring every cut tube end is a safety step, not cosmetics: the acceptance
  rule is that no sharp edge can reach the cell.

**Antenna:** Espressif's layout guidance asks for 15 mm clearance in all
directions. The CAD check enforces a 15 mm keep-out around the board's antenna
end and requires it to cantilever ≥12 mm past the frame — verified as part of
the 144 rules.

---

## What would falsify this

Honest failure modes, in rough order of likelihood:

1. **The chain test fails at 3.0 V** → the converter's real startup is the
   2.8 V figure, not 2.0 V. Fix: lower-resistance holder, or a converter with a
   published 1.8 V startup.
2. **The holder won't take the cell** → its listing never claims 16340 support.
   Fix: the DGZZI 2-slot alternate, or a different holder.
3. **The toggle switch is too tall** (33 mm) for a pocket frame. Fix: a mini
   slide switch; the electrical requirement is only ≥1 A DC.
4. **A clone board differs** from its listing photo. This is why every
   marketplace part is bought in multipacks and qualified.
5. **The backend is unacceptable** — unreachable, or you don't want your
   microphone audio going there. Fix: self-host, or stop at Phase 0.

Each of these is caught on a breadboard, before any brass is cut. That
sequencing is the real safety property of this plan.
