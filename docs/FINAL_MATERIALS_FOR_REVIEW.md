# Final Phase 0 qualification materials list — for Claude review (F0)

> **Procurement authority for a reversible Phase 0 qualification build only.**
> Checked 2026-09-02. This document replaces the earlier complete-cart claim.
> It is safe to order the items marked `BUY-P0`, but it does **not** release a
> battery-powered pocket device, final quantities, or brass cutting. Claude's
> compact R1 proposal is preserved separately in
> [CLAUDE_R1_BUILD_PROPOSAL.md](CLAUDE_R1_BUILD_PROPOSAL.md).

This is the **finalized order list for Phase 0**, not a final-build BOM. A
truthful final-build BOM cannot exist until measurements choose the cell,
USB-source isolation, fuse, speaker/cavity, guard, and real enclosure geometry.
Claude should review and correct this list before checkout; passing that review
still authorizes only the `BUY-P0` quantities below.

The honest verdict is **GO for one reversible bench/fit batch; NO-GO for final
assembly or pocket carry**. The firmware pin/rate contract is credible, but no
physical board, battery chain, speaker, or frame has been tested in this
workspace. The former 500 mAh/direct-rail proposal also failed a datasheet
audit: its 0.5 A maximum continuous-discharge rating was below that design's
estimated 0.7–0.8 A coincident load. The new 5 V whole-load candidate must be
recalculated because its low-cell input current can be higher still.

## How to read the list

| Mark | Meaning |
| --- | --- |
| `OWNED` | Already purchased; do not buy again unless the incoming check fails. |
| `BUY-P0` | Buy now in the stated quantity for breadboard, measurement, and physical-fit qualification. |
| `ARRANGE` | Borrow, rent, obtain a sample, or confirm access before testing. |
| `HOLD` | Candidate only; do not buy final quantity or install until its named gate passes. |
| `REJECT` | Do not use in this revision. |

Confidence is the chance that the exact choice will survive Phase 0 unchanged,
not a claim that an untested assembly is safe: **high 85–100%**, **medium
60–84%**, **low below 60%**. Prices and stock are intentionally not frozen;
seller inventory changes faster than the engineering decision. Recheck the
exact manufacturer part number in the cart.

In this document, an **unresolved device choice** is one that is marked `HOLD`,
has confidence below 85%, or carries a supplier/lifecycle risk that could force
a redesign. Each such role has a preferred candidate plus two viable design
alternatives in the alternatives matrix. Workshop consumables and instruments
are capability requirements rather than parts of the device; where no exact
MPN is named, arrange access or select a reputable equivalent meeting the whole
specification rather than treating an example as frozen.

## Implemented functional contract and proposed control extension

The source-build target remains the plain ESP32-C3 layout already implemented
in `firmware/src/boards/pocket-wall-e-c3`:

| Function | Signal | Source-build GPIO / setting |
| --- | --- | ---: |
| OLED | SDA / SCL | 21 / 20 |
| Shared I2S | WS / BCLK | 1 / 2 |
| Amplifier | DIN | 3 |
| Microphone | data out | 4 |
| Amplifier | candidate hardware enable | 5; firmware change not yet implemented/frozen |
| Action switch | active-low input | 10 |
| OLED | controller/address | SSD1306, 128×64, 0x3C or 0x3D |
| Audio | sample rate / frame | 16 kHz, two 32-bit slots, 1.024 MHz BCLK |

The opaque creator image is a separate wiring path and keeps microphone data
on GPIO8. Never combine the two maps. Microphone modules with different names
have analogous I2S signals, not guaranteed identical physical pin order.

## Candidate power architecture

These are **mutually exclusive fixtures** to draw and review in KiCad. Phase 0
discharge qualification is literally battery-free; the only cell-connected
Phase 0 activity is the later staged OCV/standalone-charge gate.

```text
FIXTURE A — standalone charging only, no load branch:
  #258 factory JST-PH ── reviewed, polarity-keyed #1131-derived measurement adapter
    CELL_POS power branch ── `0251.500MXL` fuse immediately after the connector
      ── calibrated battery-side charge-current logger ── #4410 BAT+
    COMMON_GND power branch ───────────────────────────────── #4410 BAT−
    CELL_POS Kelvin-sense branch ── source-adjacent 1 kΩ ── shrouded SENSE+
    COMMON_GND Kelvin-sense branch ── source-adjacent 1 kΩ ── shrouded SENSE−
  Calibrated endpoint logger connects only across SENSE+ / SENSE−.
  #4410 USB-C ── qualified USB source
  The Molex harness, #2810, #2873, controller, and amp are absent.

FIXTURE B — battery-free discharge/power qualification only:
  current-limited bench supply positive (the sole CELL_POS substitute)
    ── separately guarded candidate-fuse test point at the source
    ── Molex two-pole bench harness ── Pololu #2810 VIN/VOUT
    ── VBAT_SW (sweep 4.2 V through candidate cutoff/restart)
         ── Pololu #2873 VIN; bridge SEL to its adjacent VIN-pulled pad for 5 V
              ── 5V_SYS (whole-load 3.0 V falling cutoff / ~3.4 V restart)
                   ├── Adafruit #3006 amp VIN + 220 µF reservoir
                   │     └── SD/MODE held LOW until rail and I2S are ready
                   └── controller power interface: HOLD; see the paragraph after this diagram
                        ── received-board LDO ── 3V3
                             ├── OLED
                             ├── I2S microphone
                             └── TI TXU-EVM TXU0104 VCCA

  bench supply return ── the other Molex conductor ── COMMON_GND

MCU WS/BCLK/DIN ── TXU0104 A1…A3; GPIO5 ── A4, with 4.7 kΩ to GND
TXU0104 B1…B4 ── amp LRC/BCLK/DIN/SD_MODE; VCCB = 5V_SYS
#2873 PG ── TXU0104 OE; OE has 10 kΩ to 5V_SYS; SD_MODE has 4.7 kΩ to GND

FUTURE CELL-DISCHARGE FIXTURE — HOLD, not Phase 0 wiring authority:
  #258 factory JST-PH ── polarity-mapped mating adapter
    ── selected fuse immediately after the source connector
    ── two-pole disconnect ── #2810 ── #2873 and loads
  The only unavoidable pre-fuse wire is the guarded factory battery lead.
  #4410 and its PCB traces are never used as a load pass-through.

Speaker: amplifier OUT+ and OUT− only; neither lead goes to GND or frame.
Brass frame: mechanically structural and electrically floating.
```

Why the extra power parts exist:

- `#4410` performs the Li-ion CC/CV charge algorithm; protection inside a pack
  is not a charger.
- `#2810` lets a tiny slide actuator control the load without forcing the
  ampere-class cell current through a generic 0.5 A mechanical contact. It is a user
  power control, **not** the positive-disconnect charging interlock.
- `#2873` gives the whole active load a regulated 5 V rail and a hysteretic
  3.0 V cutoff. The amplifier must remain in hardware shutdown during the
  regulator's 700 mA-limited startup and until I2S is valid; otherwise this
  topology is rejected. Brownout/reboot cycling and the pack PCM are not the
  normal empty-battery policy.
- The controller power/service interface remains `HOLD`. If continuity shows
  that the SuperMini `5V` pin is the USB-C receptacle's VBUS node, the former
  diode-only scheme is categorically `REJECT`: feeding `5V` would source power
  outward on the receptacle, regardless of diode orientation. The final path
  then requires reviewed board-trace separation plus true reverse blocking, a
  different controller, or a positive interlock that opens 5V_SYS before USB
  can mate. A `1N5820` also cannot prove the former ≤10 µA criterion: onsemi
  specifies reverse-current maxima in milliamps at rated reverse voltage.
- The populated `TXU0104` section of TI's `TXU-EVM` is the Phase 0 experiment
  across the powered-MCU/unpowered-amplifier boundary. Unlike the rejected
  auto-direction TXB0104 network, it is a one-way A-to-B translator with
  partial-power-down, supply isolation, output disable, and strong outputs that
  may drive the required `SD_MODE` pull-down. The #2873 `PG` signal supplies a
  hardware rail-good veto at `OE`; GPIO5 then controls channel 4 and amplifier
  shutdown independently. Its 1.024 MHz waveform, sequencing, and all
  partial-power states still need measurement.
- The fuse is branch/wire fault containment. Its final value remains `HOLD`
  until the current waveform and nuisance-opening margin are measured.

In Fixture A, “source-adjacent” means the positive power fuse and both sense
resistors are the first components after the mating battery connector, on a
rigid guarded adapter with no accessible raw-cell copper. Never attach ordinary
meter clips to the cell side. The two 1 kΩ sense resistors limit a single-lead
short to about 4.3 mA at the maximum accepted voltage; their loading/divider
error, tolerance, temperature coefficient, lead leakage, and logger input
impedance must all be included in the ≤5 mV uncertainty budget. Stage-1 OCV is
measured at the downstream, source-fused power output with #4410 absent.

Do not size the cell from the former 0.8 A estimate. At minimum cell voltage,
the new planning calculation is `(amplifier input power + controller/peripheral
input power) / (#2873 efficiency × cell voltage)`, followed by transient and
temperature margin. A 1.5 W speaker workload can make that result exceed
1.2 A; the measured waveform and every exact-part limit decide the answer.

The #4410 has no load sharing. In Phase 0 it may charge the quarantined pack
only on a standalone fixture with the load harness physically disconnected,
attended and outside a pocket. It cannot be promoted into the finished device
on a remembered OFF rule: final charging needs #4755-class power-path hardware
or an electrical/mechanical interlock that physically opens the load before a
charger plug can mate. Likewise, the SuperMini service connector may be used
only while bare or with the cell physically disconnected until a tested
interlock makes every unsafe dual-source state impossible.

All Phase 0 powered work is attended on a nonflammable bench. For the first
amplifier tests, `SD/MODE` is physically tied to GND while the regulator
starts, and TXU B4 is physically disconnected. De-energize the fixture, remove
the hard-ground link, and meter-confirm that it is open before connecting B4;
never let the translator drive a hard short. The proposed next experiment uses the populated TXU0104 section on
TI's `TXU-EVM`: connect VCCA=3V3 and VCCB=5V_SYS; route WS/BCLK/DIN through
A1→B1, A2→B2, and A3→B3; connect the uncommitted GPIO5 to A4 with 4.7 kΩ from
A4 to GND; and route B4 to `SD/MODE` with a separate 4.7 kΩ from B4 to GND.

Meter-map the TXU0104 section's J3 before power. Connect #2873's open-drain
`PG` to J3 center/`OE`, and pull that node up through **10 kΩ to VCCB/5V_SYS**.
The EVM shunt may remain only in the meter-confirmed center-to-VCCB position,
which uses its fitted 10 kΩ path; attach `PG` to the center node with a secure
test connection. If that is mechanically unreliable, remove the shunt and fit
the explicit 10 kΩ resistor. Never short `OE` directly to 5V_SYS. A 3V3
pull-up is not the candidate because USB could then feed an unpowered regulator
`PG` node.
Pololu describes `PG` as low until roughly 95% of nominal output and open-drain
afterward, but does not publish the limits needed to accept this circuit by
inspection. Scope it through cold start, slow ramp, brownout, switch-off, and
USB-only transitions. Scope evidence can qualify the current-limited bench
experiment but cannot establish unpublished absolute-maximum/sink ratings;
obtain written Pololu limits or add a reviewed buffer before a final design.

Firmware must configure GPIO5 output-low at its earliest board-init point and
initialize continuous clocks with zero data. The MCU does **not** sense `PG` in
this candidate: it may raise GPIO5 only after its own startup/rail-stabilization
delay and valid zero-data I2S, while `PG` independently keeps `OE` disabled
until the regulator is good. Keep samples at zero for a scope-qualified delay
that covers worst-case `PG` release plus the amplifier datasheet turn-on time;
if that bound cannot be guaranteed, add a reviewed level-safe `PG` sense path
before promotion. Official ESP32-C3 reset behavior does not itself
enable a GPIO5/MTDI pull-up, but firmware APIs can; never reset that pad into or
configure it with a pull-up. On stop, lower GPIO5 before clocks or power.
Measure `OE` below the TXU0104 guaranteed-low limit whenever `PG` is low.
Measure `SD/MODE` below **0.08 V** including instrument uncertainty while
disabled and above **1.5 V** only after the enable event; these are the
MAX98357A guaranteed comparator boundaries, not the 0.16 V and 1.4 V typical
values. KiCad review, the firmware change, a signal-integrity capture, and
per-line plus total unpowered-I/O injection tests are required before this
experiment can become the final circuit.

## BUY-P0 — exact electronics and power samples

| Qty | Role | Exact preferred item and source | Status | Confidence | Incoming/bench gate |
| ---: | --- | --- | --- | ---: | --- |
| 1 pack (≥3 boards) | Controller | Plain ESP32-C3 SuperMini, creator-linked [Amazon B0G5XS345R](https://www.amazon.com/dp/B0G5XS345R), USB-C, no U.FL and no RGB/Plus variant | `BUY-P0` | 60% | Qualify at least two. `esptool flash_id` ≥4 MB; record board dimensions, LDO marking, 5V↔VBUS continuity/diode behavior, idle current, and loaded 3V3 rail. Marketplace identity is not controlled by the ASIN alone. |
| 2 | White OLED | Adafruit [#326](https://www.adafruit.com/product/326), 0.96-inch white 128×64 OLED, SSD1306, I2C default, 29.2×26.7×6.2 mm | `BUY-P0` | 92% | Verify address, all-white test, burn-in, actual envelope, and connector clearance. This is slightly larger than a generic video-style board. |
| 2 | I2S microphone | Adafruit [#6049](https://www.adafruit.com/product/6049), ICS-43434 breakout | `BUY-P0` | 88% | `SEL` low, 3V3 only, acoustic port outward. Record clean left-slot audio at 16 kHz. Silicon is discontinued, so the spare is intentional. |
| 2 | I2S amplifier | Adafruit [#3006](https://www.adafruit.com/product/3006), MAX98357A mono breakout | `BUY-P0` | 94% part / 70% control | Power VIN from 5V_SYS, not raw cell voltage. Begin with `SD/MODE` hard-grounded, then qualify the reset-safe shutdown/left-select control above. Capture WS/BCLK/DIN; do not assume the stock `(L+R)/2` mode duplicates the left slot. |
| 2 | Primary speaker sample | Same Sky [CMS-20143-158SP](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMS-20143-158SP/28173678), 8 Ω, 1.5 W nominal, 20×14×3.7 mm | `BUY-P0` | 82% | Electrically safer than the former 0.8 W choice, but requires a sealed test baffle/rear cavity. Measure differential RMS voltage and compare speech intelligibility. |
| 2 | Enclosed acoustic comparison | Same Sky [CES-20134-088PM](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CES-20134-088PM/10821309), 8 Ω, 0.8 W nominal, enclosed | `BUY-P0` | 72% | A/B for acoustics and fit only. It is not final until firmware enforces a cap and measured output stays ≤2.53 Vrms differential (0.8 W into 8 Ω). |
| 2 each | Action button and white cap | Omron `B3F-1000` tact switch + `B32-1060` white cap from an authorized distributor | `BUY-P0` | 92% | Confirm cap height in the cardstock mock-up and verify active-low GPIO10 operation. GPIO9 remains ROM BOOT. |
| 10 strips | Module headers | Sullins [`PRPC040SAAN-RC`](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PRPC040SAAN-RC/2775214), DigiKey `S1011EC-40-ND`, black 1×40, 2.54 mm vertical break-away male header | `BUY-P0` | 95% | Current exact-stock substitute for out-of-stock Adafruit #392. Ten strips match/exceed that pack's usable pin count. Use for reversible bench tests; do not let tall headers dictate final frame depth. |
| 1 | Protected cell sample | Adafruit [#258](https://www.adafruit.com/product/258), 3.7 V 1200 mAh protected LiPo, JST-PH, 34×62×5 mm | `BUY-P0` | 65% | **Quarantine on arrival; do not connect initially.** Photograph lot/label, record dimensions and the connector's expected polarity from label/lot documents only, and match the shipping-lot datasheet. Actual electrical polarity is checked only inside Stage 1 of a signed release. Its documented continuous rating must exceed both a recalculated low-cell analytical bound and the captured full waveform by ≥20%; 1.2 A is not pre-approved. The published 500 mA charge ceiling is a limit, not present permission: the first release can authorize only one 100 mA cycle. No clamping, bending, puncture, or soldering. |
| 2 | USB-C charger | Adafruit [#4410](https://www.adafruit.com/product/4410), 100/500 mA Micro-Lipo | `BUY-P0` | 88% part / 65% final system | Phase 0 standalone pack charging only, with the load harness physically removed. Leave the jumper open at 100 mA. Target 4.20 V and require ≤4.23 V including calibrated-meter uncertainty, or the exact pack/charger revision's lower limit. The 500 mA setting and every cycle after the first remain `HOLD` for use; each needs a new written release and a repeated limit/fuse/thermal review. |
| 2 | Cell-adapter cable samples | Adafruit [#1131](https://www.adafruit.com/product/1131), JST-PH battery extension, 500 mm, color-coded 26 AWG | `BUY-P0` | 78% sample / 40% final | Connector/polarity/fit samples only. Keep intact and electrically disconnected until a charge or future discharge fixture has an exact fuse termination, current-instrument connection, rigid guard, and strain-relief drawing. A later written use release may cut one cable to the minimum pre-fuse stub; never cut or alter the battery lead. |
| 2 pairs | Removable two-pole battery-free bench harness | Molex Micro-Fit 3.0 [male-to-pigtail `2147531022`](https://www.molex.com/en-us/products/part-detail/2147531022) + [female-to-pigtail `2264291023`](https://www.molex.com/en-us/products/part-detail/2264291023), single-row 2-circuit locking assemblies, 300 mm, 18 AWG, black | `BUY-P0` | 88% Phase 0 | One pair is the bench-supply fixture and one is its spare; do not connect either to the cell in Phase 0. Both conductors—`CELL_POS` **and** `COMMON_GND`—open when unmated. Because both wires are black, meter-map pin 1 first, permanently mark `CELL_POS` red at both ends of both halves, key/label the mating halves, and repeat the polarity check before energization. Mate/unmate only with #2810 OFF, both USB cables absent, and a meter-confirmed de-energized harness. Molex publishes 8.5 A maximum per contact, but that is not this build's approved current: verify mating/keying, strain relief, repeated cycles, loaded voltage drop, and temperature at the recalculated current. This is neither a final battery adapter nor a charging interlock. |
| 2 | Power switch module | Pololu [#2810](https://www.pololu.com/product/2810), Mini MOSFET Slide Switch with reverse-voltage protection, LV | `BUY-P0` | 90% | 1.8–16 V operating range; measure off leakage, turn-on transient, and drop at the measured peak. This replaces the incorrectly described generic 0.5 A switch. |
| 2 | Whole-load regulator / UVLO | Pololu [#2873](https://www.pololu.com/product/2873), S9V11F3S5C3 | `BUY-P0` | 85% part / 70% system | For the reviewed 5 V candidate, bridge `SEL` to the adjacent unpopulated pad that Pololu documents as pulled up to VIN; do not infer this from board position without continuity-checking the received revision. Qualify the combined amp/controller load: amp shut down through its 700 mA-limited startup, then worst-case regulation/temperature; verify 3.0 V falling cutoff, ~3.4 V restart, no chatter, and no I/O back-power. |
| 1 | I2S/amp partial-power translator fixture | TI [`TXU-EVM`](https://www.ti.com/tool/TXU-EVM), DigiKey `296-TXU-EVM-ND`, using its populated TXU0104 A→B section | `BUY-P0` | 82% experiment / 35% final fit | Configure exactly as described above. Meter-map J3; connect #2873 `PG` to J3 center/`OE`, retaining only the VCCB-side 10 kΩ pull-up. GPIO5 goes to A4, not OE. Verify outputs are high impedance and total forbidden injection is ≤10 µA or the lower affected-part limit with either rail at 0 V; then verify clean 1.024 MHz edges and reset-safe `SD_MODE` thresholds. The EVM is a bench fixture, not final enclosure hardware. Do not substitute an auto-direction TXB/BSS138 board. |
| 5 | Charge-fixture fuse samples | Littelfuse [`0251.500MXL`](https://www.digikey.com/en/products/detail/littelfuse-inc/0251-500MXL/700707), PICO II 500 mA, fast acting | `BUY-P0` | 82% for the 100 mA charge fixture | **Installation remains `HOLD` until the charge-only release.** Before cell connection, build/guard the #1131-derived adapter and prove polarity, continuity, no shorts, logger burden, fuse placement, and current limiting using the bench supply. At 100 mA the fuse is only 20% loaded; log cell-terminal voltage only through the guarded, resistor-limited Kelvin branch and spot-check charger-side voltage because nominal fuse resistance causes early-cycle drop. This fuse does not authorize 500 mA charging or select the discharge fuse. |
| 5 | Discharge-fuse samples | Littelfuse `025101.5MAT1L`, PICO II 1.5 A | `BUY-P0` | 65% | Test stock only; **installation is `HOLD`**. Do not freeze the rating until a scope capture shows normal peak magnitude/duration plus cold/hot margin, continuous current is at most 75% of the ambient-rerated fuse rating, normal startup I²t clears the time-current curve with margin, fault I²t protects the weakest downstream conductor/contact, and fuse drop does not induce cutoff chatter. Never parallel fuses. Exact final termination/guard/strain relief remain `HOLD`. |
| 5 | Power-reservoir capacitor samples | Panasonic `EEU-FC1A221SB`, 220 µF, 10 V, 105 °C radial | `BUY-P0` | 90% | Test at amp VIN/GND and, separately, close to #2873 VIN during long-lead bench work; observe polarity. Scope rail droop, output overshoot, converter stability, and startup/inrush with and without it; measure ripple-current/ESR heating and check lifetime at the measured hot-spot temperature before freezing placement/value. It cannot fix an underspecified cell. |
| 10 | Signal pull-down resistors | Yageo [`MFR-25FBF52-4K7`](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-4K7/9138176), 4.7 kΩ, 1%, 1/4 W axial | `BUY-P0` | 90% circuit candidate | One establishes GPIO5/A4 low through reset and dominates any accidentally enabled firmware pull-up; one holds amp-side `SD_MODE` low against #3006's fitted pull-up and the MAX98357A internal pull-down. Paper margin is not acceptance: measure `SD_MODE` against <0.08 V / >1.5 V guaranteed boundaries through reset, ramp, and partial power. |
| 10 | Power-good/OE pull-up resistors | Yageo [`MFR-25FBF52-10K`](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-10K/13219), 10 kΩ, 1%, 1/4 W axial | `BUY-P0` | 86% circuit candidate | External spares for the #2873 `PG` → TXU `OE` test if J3's fitted VCCB-side 10 kΩ path cannot be used reliably. Pull to 5V_SYS only; measure `PG` sink voltage/current and `OE` through every rail transition because Pololu publishes functional thresholds, not full electrical limits for this pin. |
| 10 | Charge-voltage sense current-limit resistors | Yageo [`MFR-25FBF52-1K`](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-1K/13011), 1 kΩ, 1%, 1/4 W axial | `BUY-P0` | 88% fixture candidate | Fit one as the first component in each of Fixture A's guarded SENSE+ and SENSE− branches. Prove the adapter with a current-limited bench supply; verify shrouding, short-circuit current, resistance, temperature, and the complete logger error budget before the charge-only release. These do not replace the separate CELL_POS power fuse. |

The 1200 mAh cell is deliberately a **sample**, despite `BUY-P0`. Purchase does
not authorize connection or charging. Two separate written use releases are
required:

1. A **charge-only release** may authorize exactly two sequential stages and
   nothing else. Before signing, record the exact lot chemistry, documented
   expected connector polarity, and charge limits—without making an electrical
   connection. With no pressure on the pouch, inspect it and its leads,
   connector, and insulation for swelling, creases, puncture, damage, odor, or
   abnormal warmth. Quarantine/reject it—do not attempt recovery or charging—if
   it is damaged, swollen, or abnormally warm. Stage 1 then authorizes only the
   reviewed source-fused adapter and calibrated high-impedance DMM, with #4410
   and every other load absent, to verify actual polarity and make one OCV
   measurement. A negative/reversed result, PCM-open/0 V, deep discharge, or
   voltage outside the exact-lot maker's
   permitted pre-charge range immediately ends the release: disconnect and
   return the pack to quarantine. Only a passing OCV advances the same release
   to Stage 2, one 100 mA Fixture A cycle. The release also requires an inspected #4410;
   reviewed source-adjacent charge-fixture fuse, #1131-derived measurement
   adapter, guard, and strain relief; in-date calibration certificates and
   proved-ready current/voltage/three-channel thermal logging; an attended
   nonflammable bench; stop limits; and independent reviewer approval. The
   resulting logs are pass/fail evidence after the cycle; they are not a
   circular precondition. The Molex harness and every load remain physically absent.
2. A later **cell-discharge release** additionally requires documented cell
   discharge margin; passed KiCad/ERC and source-state review; source-adjacent
   discharge fuse and guarded adapter that never traverses #4410; measured
   wire/switch/connector/regulator margins; bench-supply startup/load/cutoff
   waveforms; accepted controller power/service isolation; no I/O back-power;
   rigid cell guard, strain relief, fit, and written stop limits.

Until the applicable checklist is signed, keep the cell in quarantine. An OFF
switch, open load harness, unplugged charger USB, current limit, or pack PCM is
not a substitute for physical cell disconnection.

## BUY-P0 — structure, insulation, wire, and temporary fixtures

| Qty | Role | Exact preferred item and source | Status | Confidence | Gate / color |
| ---: | --- | --- | --- | ---: | --- |
| 1 pack | Main frame tube | K&S `#9831`, 1.5 mm OD × 0.225 mm wall brass tube, four 300 mm lengths ([maker page](https://ksmetals.com/products/br225mm-1h)) | `BUY-P0` | 92% | Caliper and use offcuts only for process coupons. No final-frame cut, bend, joint, or paint is released by `BUY-P0`; those require every promotion gate plus a separate written final-fabrication release. Final finish is satin white/silver, not bare gold brass. |
| 1 pack | Braces/posts | K&S `#9861`, 1.0 mm round brass rod, five 300 mm lengths ([maker page](https://ksmetals.com/products/brrmet-1)) | `BUY-P0` | 92% | Verify one coupon telescopes into a tube coupon. Structural only; never a return conductor. Keep final-length stock untouched until written final-fabrication release. |
| 1 sample sheet | Primary electrical barrier | ITW Formex `GK-10BK`, black, 0.010 inch / 0.25 mm; obtain from ITW or an authorized converter | `ARRANGE` | 86% material / 60% source | Require the exact maker/grade on the invoice. Cut a cell cradle/liner with no sharp folds into the pouch. Formex's rating does not certify the finished device. |
| 1 roll | Local insulation | 3M Polyimide Film Electrical Tape `92`, 12.7 mm × 16.5 m | `BUY-P0` | 92% | Authorized stock only. Amber tape stays concealed; it anchors/insulates conductors but does not replace the rigid battery guard. |
| 1 sample | Rigid prototype guard | Genuine polycarbonate sheet, 0.5–0.8 mm, traceable maker/grade; source not frozen | `ARRANGE` | 65% | Obtain only after supplier/grade/size is documented. Bend/cut a smooth removable guard over the pouch. Reject acrylic sold as polycarbonate and any sharp cut edge. Final material/shape remain `HOLD` pending CAD and debris/compression tests. |
| 1 roll each | Power and speaker wire | Adafruit [#1877 red](https://www.adafruit.com/product/1877) and [#1881 black](https://www.adafruit.com/product/1881), 26 AWG silicone stranded wire | `BUY-P0` | 88% | Red = positive; black = return. Keep the high-current spine short. Twist OUT+/OUT− as a pair but do not treat black speaker wire as GND. |
| 1 roll each | Signal wire | Adafruit 30 AWG silicone wire: [#3166 blue](https://www.adafruit.com/product/3166), [#3167 yellow](https://www.adafruit.com/product/3167), [#3169 white](https://www.adafruit.com/product/3169) | `BUY-P0` | 88% | Assign and document one color per I2C/I2S function; keep I2S clock/data short. White supports the exterior palette but wire color has no electrical meaning. |
| 1 size sample each | Splice/identity insulation | 3M `FP-301` black, white, and red heat-shrink; final recovered diameter not frozen | `ARRANGE` | 78% | Measure the insulated wire/joint first, then record exact color, recovered size, package length, and distributor SKU. Black is the secondary accent; red permanently identifies both ends of `CELL_POS` on the all-black Phase 0 harness. |
| 1 local craft set | Mock-up stock | Approximately 1 mm cardstock/chipboard, painter's tape, graph paper, removable poster putty | `BUY-P0` | 95% | Non-device material; brand is immaterial. Build a 1:1 nonconductive fit model before brass cutting, including connector sweep and cell swelling clearance. |
| 1 fixture set | Speaker baffle test stock | Rigid sheet, non-hardening gasket, fasteners/clamps, and cavities sized after the two received speakers | `ARRANGE` | 70% | Build two repeatable, sealed comparison fixtures; do not glue either speaker. Record front aperture, rear volume, microphone distance, and leakage. |

### Frame solder and finish are conditional

Use the X-Tronic solder and Chip Quik electronics flux on **empty brass
coupons first**. A mechanically interlocked sleeve joint that survives the
coupon test is preferable to adding corrosive chemistry. If it will not wet
or the joint is weak, the controlled alternative is Harris Stay-Brite 8
`SB831` with Stay-Clean liquid flux `SCLF4`, used only on the empty frame with
local exhaust, eye/skin protection, manufacturer cleanup, water rinse, full
neutralization, and complete drying before electronics enter the area. This
acid-flux path is `HOLD` and is not the electronics-soldering process.

After all promotion gates and written final-fabrication release, the requested
palette is **satin white primary, silver accents, black secondary**. The later
sequence—not current Phase 0 authority—is:

1. Fabricate, clean, and electrically isolate the empty frame.
2. Coupon-test the complete primer/topcoat system on the same K&S brass lot.
3. Apply satin white to the outer frame; use metallic silver only on selected
   braces/guards. Keep the black OLED face, speaker opening, heat-shrink, and
   Formex visible as the secondary color.
4. Paint before installing electronics. Mask every joint land, port, antenna
   keepout, bearing surface, and ground-test point. Paint is never insulation.

The existing candidate numbers—Rust-Oleum `249322` self-etch primer,
`2081830` gray sandable primer, `7791830` satin white, and `7715830` aluminum
silver—remain `HOLD` until the brass coupon passes adhesion, scratch, heat,
and 72-hour cure checks. Aerosol work requires an appropriate legal outdoor
or spray-booth setting; a respirator does not replace ventilation.

## Tools and software

### Already owned

| Item | Status | Incoming check |
| --- | --- | --- |
| X-Tronic 3020-XTS complete station | `OWNED` | Identify the included solder alloy from its label. The silicone mat is the hot-work surface; the craft mat is not. |
| Chip Quik `CQ4LF` no-clean flux pen | `OWNED` | Electronics only; confirm cap/date and that it dispenses cleanly. |
| BOENFU 6-inch flush cutters | `OWNED` | Wire/component leads only, never brass tube. |
| WORKLION 12×18-inch self-healing mat | `OWNED` | Layout/craft cutting only, never soldering. |
| OLFA `CMP-1` circle cutter | `OWNED` | Cardstock/polymer grille templates only. |

### Buy or arrange before Phase 0

| Qty | Tool | Preferred specification | Status | Confidence / use |
| ---: | --- | --- | --- | --- |
| 1 + 1 each | General-purpose multimeter | Klein `MM450`, plus one spare `69032` 10 A/600 V fuse and one spare `69033` 500 mA/600 V fuse | `BUY-P0` | 90%; continuity, polarity, bring-up voltage/current, resistance, and spot temperature checks. These are the maker-specified MM450 fuses. Its 40.00 V range/accuracy is **not sufficient to release the 4.23 V charge gate**, and one probe cannot perform the required simultaneous thermal log. Never place the current input across a cell or supply. |
| 1 | Current-limited bench supply | KORAD `KA3005P`, 0–30 V / 0–5 A | `BUY-P0` | 85%; substitutes for the cell through every battery-free gate. Before any DUT, verify current limiting, output-enable/disable overshoot, and recovery from current limit on dummy loads. It is a source, not a guaranteed sink or battery emulator: #4410 must be physically absent from its circuit. |
| 1 | Dedicated charger USB source | Adafruit [#501](https://www.adafruit.com/product/501), UL-listed 5.25 V / 1 A USB-A wall supply | `BUY-P0` | 92%; dedicated to #4410 through the labeled `CHARGER` #4473 cable. Inspect the exact received label/certification and connector, then log no-load and 100 mA-fixture input voltage and temperature in a battery-free dummy run. Do not share it with the MCU or substitute an unknown multiport/PD charger. |
| 1 set each | Supply leads | Shrouded banana-to-hook low-current leads and short ≥5 A banana leads | `BUY-P0` | 80%; use the small leads for logic and the heavy pair for load tests. |
| 1 each | Dummy loads | Yageo `SQP10AJB-4R7` and `SQP10AJB-8R2`, 10 W wirewound | `BUY-P0` | 88%; power-path and speaker-load tests. Mount clear of plastics; they get hot. |
| access to 1 | Calibrated charge-voltage logger | Fluke `289`, with in-date traceable calibration and total uncertainty ≤5 mV at 4.20 V | `ARRANGE` | 92% need / 88% example; independently record terminal voltage/time through Fixture A's guarded resistor-limited Kelvin branch throughout the first charge. Acceptance uses reading plus the entire branch/instrument uncertainty. Do not substitute the MM450. |
| access to 1 + 3 probes | Multichannel temperature logger | Pico Technology calibrated `USB TC-08` + three `SE051` 1 m type-T probes for cell surface, charger surface, and ambient | `ARRANGE` | 95% need / 88% example; log all three simultaneously throughout charge. Include logger, probe, attachment, and calibration uncertainty; attachment must not short or press on the pouch. |
| access to 1 | Two-channel oscilloscope | ≥50 MHz, single-shot capture, differential-safe speaker measurement method | `ARRANGE` | 95% need; captures regulator startup/cutoff, I2S, and speaker differential voltage. |
| access to 1 | Fast current-capture instrument | Joulescope `JS220`, ±3 A continuous range, 300 kHz bandwidth, 2 MS/s | `ARRANGE` | 90% example; DMM averages cannot qualify Wi-Fi/audio millisecond peaks. Confirm expected peak/pulse limits, calibration, grounding, burden, and error before use. |
| access to 1 | Long-duration charge-current logger | Joulescope `JS220`, configured to record the complete ≤18 h, 100 mA charge without dropped data | `ARRANGE` | 88% example; validate timestamping, storage, 100 mA accuracy, insertion burden, and fail-safe capture before connecting the cell. This is separate from the endpoint-voltage logger. |
| access to 1 or more | Logging host(s) and storage | Host OS supported by the chosen JS220/Pico/bench-DMM software, with enough independent USB interfaces and storage for a ≥20 h dry run | `ARRANGE` | 90% need; document the entire USB/ground topology, disable sleep/restarts, verify clocks/files/recovery, and keep it out of the controller's USB source path. JS220 sensing is isolated from USB within its rating; TC-08 ground follows the host, so use electrically insulated thermocouple junctions/attachment and continuity-check that no probe creates a DUT-current path. Follow Pico's host-grounding instructions. A computer-hosted 34461A needs its own continuous logging connection. |
| 1 + 1 set each | Breadboard and jumpers | Adafruit [#239](https://www.adafruit.com/product/239) full-size breadboard, [#1957](https://www.adafruit.com/product/1957) 20×150 mm male/male jumpers, and [#1954](https://www.adafruit.com/product/1954) 20×150 mm female/male jumpers | `BUY-P0` | 90%; logic-only bring-up. Do not route the full amplifier/cell current through breadboard spring contacts. |
| 2 | Known-good USB data cables | Adafruit [#4473](https://www.adafruit.com/product/4473) USB-A-to-C, one labeled `MCU`, one labeled `CHARGER` | `BUY-P0` | 90%; only the MCU cable is a data requirement. Never plug both device ports during the candidate test. |
| 1 | Precision caliper | 0–150 mm digital caliper with 0.01 mm display | `BUY-P0` | 85%; record actual envelopes and connector sweeps. A traceable 0.01 mm claim is not required for this build. |
| 1 each | Fine wire tools | 20–30 AWG stripper, fine needle-nose pliers, round-nose pliers | `BUY-P0` | 90%; the X-Tronic bundle already supplies tweezers. Inspect that pair on arrival and add a reputable ESD-safe precision pair only if the included tool is not ESD-marked or cannot securely handle small parts. |
| 1 set | Brass tools | Jeweler's saw, 2/0–4/0 blades, bench pin, needle files, 400–800 grit abrasive, metric rule, square | `BUY-P0` | 88%; saw rather than crush the thin-wall tube; deburr every edge. |
| 1 each | Rework tools | Fine solder wick (Chemtronics `80-2-5` or equivalent) and magnification | `BUY-P0` | 90%; use the owned Chip Quik flux. The included solder sucker is too coarse for small module pads. |
| 1 | Controlled heat source | Adjustable heat gun for heat-shrink | `BUY-P0` | 85%; cell disconnected and removed before use. |
| 1 each | Safety | ANSI Z87.1 eye protection, source-capture electronics fume extraction, nonflammable work surface, Li-ion storage case | `BUY-P0` | 95%; if already owned, record it as `OWNED`. Acid flux and aerosols require separate controls appropriate to their SDS. |
| 1 | ESD setup | Grounded ESD mat and wrist strap | `BUY-P0` | 85%; especially for the MEMS mic and bare controller. |

Software is not a substitute for the electrical measurements:

| Software | Access in this workspace | What it can verify now |
| --- | --- | --- |
| Python/git/static checks | CLI available | Firmware metadata, local net/rate lint, links, and test scripts. |
| KiCad 10.0.6 | `kicad-cli` and KiCad MCP available; MCP currently points at an unrelated `/Projects/Pager/hardware/mochi` project and was not changed | A new exact power schematic, ERC, and later PCB/carrier DRC after explicitly creating/selecting this project's hardware workspace. No reviewed Pocket Assistant schematic exists yet. |
| Wokwi CLI 0.26.1 | CLI installed; token is **not present in this shell**; Wokwi MCP is not exposed | Partial ESP32/OLED/button diagram lint. It cannot validate battery power, analog audio, RF, thermals, real clone boards, solder, or fit. |
| FreeCAD | No working CLI detected in this shell | Existing generated fit artifacts are stale. Install/restore FreeCAD, or use a separate CAD host, after measuring the real parts. |

## Alternatives for every unresolved electrical/device path

Only one option in each row can become the final primary path. Alternatives are
`HOLD` unless their own cell explicitly says `BUY-P0` or `ARRANGE`; do not order
a held option unless Claude explicitly promotes it. “Replace qty” is what to
buy instead of the preferred item; do not buy all three options. Percentages
are design-retention confidence, not safety probabilities. These are credible
architectural alternatives, not a fictional final BOM: custom holders,
interlocks, guards, and the small translator carrier remain unnamed where real
measurements must set their geometry. Such an unnamed subassembly is an
explicit `HOLD`, not permission to improvise or purchase it.

| Role | Preferred candidate / status | Alternative 1 / status / replace qty | Alternative 2 / status / replace qty | Decision trigger |
| --- | --- | --- | --- | --- |
| Controller | SuperMini B0G5XS345R — `BUY-P0`, **60%** | Adafruit [QT Py ESP32-C3 #5405](https://www.adafruit.com/product/5405) — `HOLD`, **82%**, replace with 2 after stock/pin review | Seeed XIAO ESP32C3 — `HOLD`, **84%**, replace with 2 after pin/CAD port | Keep SuperMini only if ≥2 boards pass flash, LDO, VBUS, current, thermal, and fit gates. Otherwise port firmware before frame work. |
| Display | Adafruit #326 — `BUY-P0`, **92%** | DFRobot [DFR0650](https://www.dfrobot.com/product-2017.html/) — `HOLD`, **86%**, replace with 2 | Generic white SSD1306 Amazon B09T6SJBV5 — `HOLD`, **55%**, replace with 5-pack | Use the smallest board that passes address, pixel, burn-in, and measured-fit tests without changing the controller contract. |
| Microphone | Adafruit #6049 ICS-43434 — `BUY-P0`, **88%** for this one-off | DFRobot [SEN0526](https://wiki.dfrobot.com/sen0526/) — `HOLD`, **78%**, replace with 2 | Generic INMP441 B092HWW4RS — `HOLD`, **50%**, replace with 5-pack | Promote on clean 16 kHz capture, known pinout, acoustic port fit, and supplier continuity. Never swap by pin position alone. |
| Amplifier | Adafruit #3006 — `BUY-P0`, **94%** | DFRobot [DFR0954](https://www.dfrobot.com/product-2614.html) — `HOLD`, **80%**, replace with 2 | Generic HiLetgo MAX98357A B0CDWXZZCH — `HOLD`, **55%**, replace with 3-pack | Primary stays unless terminal-block geometry fails. Any substitute repeats supply, gain/SD-mode, noise, and power tests. |
| Speaker | CMS-20143-158SP 1.5 W — `BUY-P0`, **82%** | Same Sky `CDS-25148-L100`, 8 Ω / 1.5 W / 25×14×4.5 mm — `HOLD`, **84%**, replace with 2 | CES-20134-088PM enclosed 0.8 W — already `BUY-P0` comparison, **72%** after a hard cap, **35%** without it | Choose by measured speech clarity, sealed-cavity design, differential RMS power, current, and real fit—not loudness alone. |
| Cell | Adafruit #258 1200 mAh — `BUY-P0` quarantine, **65%** | Nitecore [NL169R](https://www.nitecore.com/product/nl169r), 950 mAh / 2 A / USB-C — `HOLD`, **62%**, replace with 1 cell + 2 Keystone [`1051`](https://www.digikey.com/en/products/detail/keystone-electronics/1051/3465420) holder fit samples + 2 [`1018C`](https://www.digikey.com/en/products/detail/keystone-electronics/1018C/2746320) retainers | Fenix [ARB-L16-700UP](https://www.fenixlighting.com/products/fenix-arb-l16-700up-built-in-usb-rechargeable-battery), 700 mAh / 2.5 A / protected micro-USB — `HOLD`, **61%**, replace with 1 cell + 2 Keystone `1051` holder fit samples + 2 `1018C` retainers | Final cell must have protection, factory termination, exact charge limits, measured fit, and ≥20% margin over both the recalculated low-cell bound and captured waveform. No fixed 1.2 A threshold is pre-approved. The `1051` is specified for CR123A, not either longer protected USB cell; it is only an exact low-confidence fit candidate. Reject it if contact travel, retention, wrap/port clearance, or drop behavior fails, and freeze another exact holder before purchase. |
| Cell-side charge/discharge adapter | #1131-derived minimum-length, polarity-keyed, source-adjacent fused measurement adapter — cable samples `BUY-P0`, use `HOLD`, **55%** | Custom PCB with genuine JST `B2B-PH-K-S(LF)(SN)` at the battery edge, selected fuse immediately adjacent, guarded output, and strain relief — `HOLD`, **68%**, one prototype + destructive-test spare | Professional battery-test lab supplies a documented fused adapter for the exact received pack/connector/current instrument — `ARRANGE`, **80%**, one service/fixture | No option may alter the battery lead or use #4410 as a load pass-through. Freeze polarity, positive power fuse, protected Kelvin-sense branches, fuse/holder/termination, pre-protection length, conductor rating, guard, strain relief, instrument insertion, uncertainty, and fault behavior before the applicable written use release. Charge and discharge fixtures may require different fuse values and sense provisions. |
| Charger/power path | #4410 for physically disconnected standalone Phase 0 charging — part `BUY-P0`, final path `HOLD`, **88% part / 35% final** | Adafruit [#4755 bq24074](https://www.adafruit.com/product/4755) — `HOLD`, **82% electrical / 40% fit**, replace with 2; set 500 mA/use LOAD | Nitecore NL169R's integrated USB-C charger with the exact `1051`/`1018C` fit-candidate set from the Cell row — `HOLD`, **70% electrical / 40% mechanical**; replace with 1 cell + 2 holders + 2 retainers and change #4410 checkout quantity to zero | Final charging requires measured hardware load sharing or a positive electrical/mechanical interlock that opens the load before USB can mate. OFF plus attendance is insufficient, and #2810 alone is not that interlock. Do not mix pouch and integrated-charge paths. |
| Whole-load 5 V conversion / UVLO | Pololu #2873, `SEL` bridged to its adjacent VIN-pulled pad, 3.0 V fixed cutoff — samples `BUY-P0`, final `HOLD`, **85% part / 70% system** | Pololu [#2870 `S9V11F5S6CMA`](https://www.pololu.com/product/2870), default 5 V with adjustable cutoff — `HOLD`, **80% electrical / 55% fit**, replace with 2 | Pololu [#2871 `S9V11F3S5CMA`](https://www.pololu.com/product/2871), `SEL` bridged to its documented adjacent VIN-pulled pad for 5 V with adjustable cutoff — `HOLD`, **78% electrical / 55% fit**, replace with 2 | Keep #2873 only if it cold-starts with the amp shut down, then sustains the simultaneous controller/audio load at minimum input without thermal or cutoff chatter. Both alternatives add height and a user-adjustable threshold: calibrate cutoff/restart, document drift/tamper control, and repeat startup, efficiency, rail-accuracy, thermal, back-power, and measured-fit gates. |
| Controller power/service isolation | Bare SuperMini continuity/source-state mapping — `BUY-P0` inspection; final interface `HOLD`, **35%** | Adafruit QT Py #5405 controller with its documented battery/USB input topology — `HOLD`, **78%**, coupled controller replacement qty 2 | Positive mechanical interlock that disconnects 5V_SYS before the SuperMini USB plug can mate — `HOLD`, **60%**, one measured custom mechanism + destructive-test spare | If SuperMini `5V` equals receptacle VBUS, any diode-only feed is `REJECT`; no measurement can legalize outward receptacle sourcing. Final acceptance requires an exact schematic/mechanism and tests with VBUS=on/SYS=off, SYS=on with an attached unpowered sink, both sources at stated min/max, neither source, and each case with possible GPIO back-power. |
| Powered-MCU/unpowered-amp signal and shutdown isolation | TI TXU-EVM populated TXU0104 section with #2873 `PG` at `OE` and GPIO5 on A4 — `BUY-P0` bench fixture; final carrier `HOLD`, **82% electrical / 35% fit** | TI [`SN74AHCT125N`](https://www.ti.com/product/SN74AHCT125/part-details/SN74AHCT125N) plus two series onsemi [`MGSF2N02ELT1G`](https://www.onsemi.com/pdf/datasheet/mgsf2n02el-d.pdf) logic-level sinks in the common active-low OE path — `HOLD`, **76% electrical / 25% fit**, replace with 2 ICs + 5 MOSFETs | TI [`ISO7740FDWR`](https://www.ti.com/product/ISO7740/part-details/ISO7740FDWR) default-low 4/0 isolator on Chip Quik `PA0005` bench carriers — `HOLD`, **87% electrical / 25% fit**, replace with 2 ICs + 2 carriers | Promote only after a reviewed exact schematic and reset/bootloader/service-USB tests show legal voltage and ≤10 µA total forbidden injection on every signal with either side unpowered, while 1.024 MHz I2S and `SD_MODE` thresholds remain clean. For AHCT, a 10 kΩ 5V_SYS pull-up disables the common OE; the two guaranteed-at-2.5-V MOSFETs enable it only when both GPIO5 and `PG` permit. For ISO7740F, GPIO5 is channel 4 and output-side `EN2` is held low by `PG` until rail-good. Both alternatives repeat ramp/brownout testing. |
| Fuse rating | Littelfuse `025101.5MAT1L` 1.5 A — test stock `BUY-P0`, install `HOLD`, **65%** | Littelfuse `02511.25MAT1L` 1.25 A — `HOLD`, **55%**, replace with 5 | Littelfuse `0251002.MAT1L` 2 A — `HOLD`, **55%**, replace with 5 | Choose only from captured peak duration, hot/cold normal waveform, ambient rerating, ≤75% continuous loading, nominal drop/cutoff interaction, startup I²t margin, fault I²t protection of the weakest downstream conductor/contact, and the maker curves. The fuse must sit immediately after the cell adapter connector in a guarded final fixture. |
| Charge-fixture fuse for 100 mA gate | Littelfuse `0251.500MXL` 500 mA — samples `BUY-P0`, use `HOLD`, **82%** | Littelfuse `0251.250MXL` 250 mA — `HOLD`, **70%**, replace with 5 | Littelfuse `0251.750MXL` 750 mA — `HOLD`, **65%**, replace with 5 | Review cold/hot resistance and resulting charger-to-cell drop, 100 mA loading, fault current/I²t, 26 AWG protection, breaking capacity, and guarded source-adjacent installation. Authorization is one 100 mA charge cycle only; a later 500 mA charge setting requires a new fuse/thermal review. |
| Battery barrier/guard | Formex GK-10BK + traceable polycarbonate cover — `ARRANGE`, **75% system** | DuPont Nomex 410, 0.25 mm, plus the same rigid cover — `HOLD`, **70%**, one sample sheet | SLS PA12 cradle/door from a named service/material lot — `HOLD`, **60%**, one prototype + one destructive-test spare | Pass measured fit, no pouch pressure, strain relief, swelling clearance, key/coin debris, shake/drop, and edge inspection. |
| Splice/identity insulation | 3M `FP-301`, exact black/white/red recovered size after measurement — `ARRANGE`, **78%** | TE Connectivity Raychem `RNF-100` family, exact black/white/red size after measurement — `HOLD`, **75%**, one small spool/kit | Alpha Wire `FIT-221` family, exact black/white/red size after measurement — `HOLD`, **75%**, one small spool/kit | Promote only an authorized, traceable size/color whose recovered ID grips the joint or received harness insulation without damage; record exact suffix and length. Red is mandatory at both ends of `CELL_POS` when the pigtail conductors are both black. |
| Fast current capture | Joulescope `JS220` — `ARRANGE`, **90%**, access to 1 | Keysight `N2820A` + `N2822A` 20 mΩ head + compatible scope — `ARRANGE`, **92%**, access to one set | Rohde & Schwarz `NGU201` two-quadrant SMU — `ARRANGE`, **94%**, access to 1 | Each complete method must cover the recalculated peak, ≥100 kHz useful bandwidth, and documented calibration/burden/error without unsafe earth-ground paths. The former Otii Arc Pro option is removed because 4 ksps cannot close this gate. |
| Charge-current logging | Joulescope `JS220` used as its documented inline current instrument — `ARRANGE`, **88%**, access to 1 | Calibrated Keysight `34461A` + continuously connected compatible SCPI/BenchVue logging host/storage, measuring a Kelvin-connected Vishay `WSL3637R0100FEA` 10 mΩ shunt — `ARRANGE`, **90%**, access to one complete set | Calibrated Keithley `DMM6500` logging a Kelvin-connected `WSL3637R0100FEA` 10 mΩ shunt — `ARRANGE`, **90%**, access to one instrument/fixture set | The logger must be a passive series measurement in the real cell-to-#4410 path; validate ≥18 h storage, timestamps, no dropped samples, insertion burden, isolation/earth safety, and total uncertainty at 100 mA before cell use. Independently log terminal voltage; one DMM cannot fill both simultaneous roles. |
| Charge-endpoint voltage logging | Calibrated Fluke `289` with uncertainty ≤5 mV at 4.20 V — `ARRANGE`, **88%**, access to 1 | Calibrated Keithley [`DMM6500`](https://www.tek.com/en/products/keithley/digital-multimeter/dmm6500-6-5-digit-multimeter) with logged data — `ARRANGE`, **95%**, access to 1 | Calibrated Keysight [`34461A`](https://www.keysight.com/us/en/product/34461A/digital-multimeter-6-5-digit-truevolt-dmm.html) + continuously connected compatible SCPI/BenchVue logging host/storage — `ARRANGE`, **94%**, access to one complete set | Every candidate must demonstrate total uncertainty ≤5 mV at 4.20 V and a continuous maximum record for the cycle. The measurement plus expanded uncertainty must remain ≤4.23 V or the lower exact-part limit. None is permission for unattended charging; MM450 and the Fluke 87V's 100 ms MIN/MAX mode fail this gate. |
| Charge thermal logging | Calibrated Pico `USB TC-08` + three `SE051` type-T probes — `ARRANGE`, **88%**, access to one logger/three probes | Extech `SDL200-NIST` with four supplied type-K probes — `ARRANGE`, **84%**, access to 1 | Keysight `DAQ970A` + `34901A` and three calibrated thermocouples — `ARRANGE`, **94%**, access to one set | Simultaneously log cell surface, charger-board surface, and ambient for the complete charge. Apply total channel/probe/attachment uncertainty to every stop limit and ensure probe attachment cannot short circuitry or load the pouch. |
| Frame joint | Mechanically sleeved joint with owned electronics solder/flux after alloy-ID and coupon pass — `HOLD`, **60%** | Harris Stay-Brite 8 `SB831` + Stay-Clean `SCLF4`, empty frame only — `HOLD`, **70%**, one kit | Professional jeweler fabricates/joins the empty K&S frame to the frozen drawing — `HOLD`, **80%**, one service | Promote only after pull/bend, electrical isolation, flux-removal, corrosion, and coating coupons pass. No electronics or cell may be present. |
| White/silver/black finish | Coupon-proven white/silver coating on brass — `HOLD`, **65%** | Professional nickel-plated silver frame + white nonconductive panels — `HOLD`, **70%**, one service set | Satin-white frame with exposed USB shells/fasteners as the silver accents — `HOLD`, **80%**, one coating set | Decide after solder/cleaning and a 72-hour coating coupon. Color cannot override RF, heat, service, or insulation needs. |

## Items explicitly not released

| Item | Status | Reason |
| --- | --- | --- |
| Mystery `14250 1200 mAh` cell, ER/LS14250, or any unverified chemistry | `REJECT` | Capacity/shape do not prove rechargeable chemistry. Never charge a primary Li-SOCl₂ cell. |
| Soldering, stripping, spot-heating, or clamping a cell can/pouch | `REJECT` | Use factory leads/connectors and a removable, smooth nonconductive cradle. |
| Adafruit #1578 or #4237 as a drop-in final cell for the current load estimate | `REJECT` pending redesign | Published continuous ratings do not provide the required margin; #4237 must also never be charged at #4410's 500 mA setting. |
| Generic SS12F44/SS12D00 carrying the battery load | `REJECT` for this topology | The cited Amazon switch is 0.5 A class while even the former direct-rail design estimated 0.7–0.8 A; the new low-cell calculation may be higher. Use it only as a microamp control input to a rated electronic switch. |
| Generic TP4056 module or 1 A creator charger | `REJECT` unmodified | Variant, protection, current programming, USB-C implementation, and thermal behavior are uncontrolled. |
| Fluke `87V` 100 ms MIN/MAX as the ≤5 mV charge-endpoint logger | `REJECT` for this role | Its MIN/MAX mode adds an error term large enough to exceed the gate before base accuracy and calibration uncertainty are included. Use a qualified logger from the alternatives row without relaxing the ≤5 mV criterion. |
| `1N5820` as SuperMini USB/source isolation | `REJECT` for the final interface | A direct `5V`↔receptacle-VBUS board would source outward regardless of series-diode direction, and onsemi permits far more than 10 µA reverse current at rated voltage. Do not buy it for this role. |
| SparkFun BOB-11771/TXB0104 for the I2S + `SD_MODE` boundary | `REJECT` for this role | The former 10 kΩ output pull-down violates TXB0104's external-pull requirement, while its required weaker pull cannot guarantee #3006 shutdown; the former 2.2 kΩ drive path and default-high OE strap also violate the intended operating conditions. Bench characterization cannot promote an out-of-spec network. |
| Frame as GND, battery terminal, antenna, or speaker return | `REJECT` | The exposed conductive frame must remain floating; the amplifier output is BTL. |
| Full-current battery/amp tests through Dupont jumpers or breadboard springs | `REJECT` | Use short, fused, current-rated leads and a reviewed fixture. |
| Paint, glue, Kapton, or heat-shrink as the only pouch-cell guard | `REJECT` | The final device needs both a specified dielectric liner and rigid debris/puncture protection. |
| Final brass cuts, glue, paint, or pocket carry before gates close | `HOLD` | These are difficult-to-reverse steps and depend on real dimensions and hardware evidence. |

## Independent audit summary Claude must disposition

The prior release was challenged in three independent review passes. These are
the audit inputs referred to by the promotion gate below:

1. **Power/safety:** #1578 publishes only 0.5 A continuous discharge against
   the former direct-rail 0.7–0.8 A estimate; the new regulated topology still
   needs a low-cell recalculation; the generic switch is 0.5 A class; the clone
   LDO/USB path and pack protection trip behavior are unqualified; procedural
   USB rules do not remove an electrical backfeed path; every charge must be
   attended; and firmware has no proven board-specific speaker-power cap.
2. **Digital/audio:** the GPIO map, 16 kHz rate, and 1.024 MHz clock are
   coherent. Source inspection predicts left-only TX data, not duplicated
   left/right samples, so #3006 channel mode needs a hardware capture. Carrier
   pin order cannot be inferred from the microphone IC name. `netcheck.py` is
   static metadata/net lint, not power, waveform, RF, fit, or acoustic proof.
3. **Requirements/procurement:** the old cart used generic or wrong part
   identities, omitted quantities and confidence/alternatives, treated an
   unsafe cell/switch margin as released, and did not freeze a traceable
   barrier, rigid guard, frame-join process, or finish system.

Claude's response should mark each unresolved alternatives row **accept**,
**reject**, or **replace**, cite the exact MPN/source for every replacement,
and state whether any correction changes another coupled row.

## Promotion gates before Claude may say “final GO”

1. **Document control:** Claude reviews this file, the
   [archived R1 proposal](CLAUDE_R1_BUILD_PROPOSAL.md), and the three audit
   classes summarized above. Every final row has one exact MPN, quantity,
   supplier class, wiring map, and promotion criterion.
2. **KiCad power review:** draw separate Fixture A charge nets, Fixture B
   bench-source/fuse/switch/regulator/amp nets, and the still-held future
   source-adjacent fused cell-discharge adapter; #4410 is not a load tap. Draw
   every controller USB/power and I2S/control isolation path. ERC passes, and
   a human checks all source states and reverse-current paths.
3. **Incoming inspection:** photograph markings; record dimensions, documented
   expected connector polarity, connector order, flash size, clone LDO/VBUS map,
   and battery lot documents. Do not electrically probe the cell at this gate.
4. **Battery-free digital gate:** no cell is electrically connected anywhere;
   its JST is physically unmated from #4410 and every adapter, and it is stored
   away from the bench. USB-power a bare controller and low-current peripherals.
   OLED, button, mic data, Wi-Fi, and one backend round trip work. Confirm
   16 kHz WS and 1.024 MHz BCLK on real hardware. For TXU sequencing, the MCU
   may remain USB-powered while an independent bench 5V_SYS powers the amp,
   with common GND but **no connection** from controller 5V/VBUS to 5V_SYS.
5. **Battery-free power gate:** the cell and #4410 are physically absent; the
   KORAD is the sole CELL_POS source and is never asked to sink charger current.
   First recalculate low-cell demand with 5 V
   amplifier output power, controller/LDO current, converter efficiency, and
   transient margin. Then use the current-limited bench supply and rated
   fixtures from 4.2 V down through cutoff/restart. Capture startup and
   simultaneous Wi-Fi + capture + playback current only after a controller
   power interface passes review; until then, qualify amp/regulator and USB-MCU
   subtests separately and do not improvise the rejected diode. Before the DUT,
   scope KORAD enable/disable overshoot and current-limit recovery on a dummy
   load. Once an interface exists, test VBUS=on/SYS=off, SYS=on with an attached
   unpowered sink, both sources at their stated min/max, neither source, and
   each state with possible GPIO back-power. Forbidden reverse/injection
   current is the lower exact-part limit; a sample-only result cannot override
   a worse datasheet maximum.
6. **Battery-free electrical/thermal margin:** the analytical bound and
   observed hot/worst-case waveform stay within Fixture B's fuse test piece,
   wire, switch, regulator, and connectors with ≥20% documented operating
   margin. Verify stable cutoff/restart, no I/O back-power, capacitor
   ripple/ESR temperature and life, and no part above its maker or fixture
   material limit. Pololu current graphs are typical, not guaranteed limits.
7. **Audio gate:** verify actual slot data. Into the final 8 Ω speaker/dummy
   load, differential RMS power never exceeds its continuous rating under
   startup, restored settings, remote volume commands, tones, and clipping.
   If CES-20134 is selected, the hard limit is 2.53 Vrms differential.
8. **Charge-only gate:** only a signed charge-only use release permits any cell
   connection. Stage 1 uses only the reviewed source-fused adapter and calibrated
   high-impedance DMM, with #4410 absent, after the no-pressure physical
   inspection. It verifies actual polarity before OCV; a negative/reversed or
   otherwise failed check immediately ends the release: disconnect and
   quarantine; never recovery-charge. A pass against the exact-lot pre-charge
   range advances to Stage 2, exactly one 100 mA Fixture A cycle. The Molex harness and every load are physically absent. Charge initially at
   20–25 °C ambient (never outside the exact pack's range or 0–45 °C). The
   MM450 alone cannot close this gate. Through one fully attended 100 mA cycle,
   use the reviewed source-adjacent fused measurement adapter, calibrated
   endpoint-voltage logger, three-channel temperature logger, and qualified
   long-duration current logger to record battery-side charge current, time,
   ambient, cell/charger surface temperature, and terminal voltage. Target
   4.20 V; never exceed 4.23 V including calibrated-meter uncertainty or any
   lower exact-part limit. Stop when a temperature reading **plus its total
   positive uncertainty** reaches 40 °C at the cell, 10 °C rise above ambient,
   or 60 °C at the charger board; also stop if charger temperature keeps rising, there is swelling,
   odor, damage, unstable current, missing termination, or 18 hours elapse.
   Enclosed/final charging additionally requires the selected hardware
   load-sharing or positive-interlock solution. The 500 mA setting and every
   subsequent charge remain `HOLD` for use: each requires a new signed release,
   repeated pre-charge inspection/OCV gate, and applicable limit, fuse, and
   thermal review; every authorized charge remains fully attended.
9. **Later fused cell-discharge gate:** this is outside the present `BUY-P0`
   use authority and requires its own written release. With the accepted
   source-adjacent fuse/adapter, controller interface, and rigid guard, capture
   minimum-voltage and worst-case load behavior, cell/connector temperature,
   voltage sag, PCM behavior, cutoff/restart, and ≥20% hot margin through every
   series element. Final GO is impossible until this gate passes.
10. **Fit/safety gate:** update CAD from caliper measurements, then complete a
   cardstock model. Verify antenna keepout, mic/speaker openings, rigid cell
   guard, swelling clearance, strain relief, port access, service interlock,
   frame isolation, and connector removal sweep.
11. **Finish/frame gate:** brass and coating coupons pass, then a separate
    written final-fabrication release precedes any final-stock cutting or paint.
    The complete unpowered assembly passes continuity, debris, shake, drop,
    edge, and fastener checks before first pocket carry.

## Condensed checkout

> **Procurement only.** This checklist authorizes inert samples and reversible
> battery-free bench fixtures—not assembly, energization, cell connection,
> charging, final-stock cutting, paint, or pocket carry. The cell stays
> quarantined until the separate written charge-only or discharge use release
> applies. OFF, an open harness, an unplugged USB cable, current limiting, or
> pack protection does not count as physical cell disconnection.

### Adafruit

- [ ] `BUY-P0` — `#326` white OLED ×2
- [ ] `BUY-P0` — `#6049` ICS-43434 mic ×2
- [ ] `BUY-P0` — `#3006` MAX98357A amp ×2
- [ ] `BUY-P0` — `#258` protected 1200 mAh pack ×1; quarantine on arrival
- [ ] `BUY-P0` — `#4410` USB-C Micro-Lipo ×2
- [ ] `BUY-P0` — `#1131` JST-PH extension samples ×2; keep intact/disconnected
- [ ] `BUY-P0` — `#239` breadboard ×1, `#1957` M/M jumpers ×1 set,
      `#1954` F/M jumpers ×1 set, and `#4473` USB-A-to-C cable ×2
- [ ] `BUY-P0` — `#501` dedicated UL-listed 5.25 V / 1 A USB-A charger supply ×1
- [ ] `BUY-P0` — `#1877`, `#1881`, `#3166`, `#3167`, `#3169` wire ×1 roll each

### Pololu

- [ ] `BUY-P0` — `#2810` LV MOSFET slide switch ×2
- [ ] `BUY-P0` — `#2873` 3.3/5 V buck-boost with fixed 3 V cutoff ×2

### Texas Instruments

- [ ] `BUY-P0` — `TXU-EVM` translator evaluation module ×1

### Authorized component distributor

- [ ] `BUY-P0` — Same Sky `CMS-20143-158SP` ×2
- [ ] `BUY-P0` — Same Sky `CES-20134-088PM` ×2
- [ ] `BUY-P0` — Omron `B3F-1000` ×2 and `B32-1060` white cap ×2
- [ ] `BUY-P0` — Littelfuse `025101.5MAT1L` ×5; test stock, installation held
- [ ] `BUY-P0` — Littelfuse `0251.500MXL` ×5; 100 mA charge-fixture test stock,
      installation held until written charge-only release
- [ ] `BUY-P0` — Panasonic `EEU-FC1A221SB` ×5
- [ ] `BUY-P0` — Yageo `MFR-25FBF52-4K7` ×10
- [ ] `BUY-P0` — Yageo `MFR-25FBF52-10K` ×10
- [ ] `BUY-P0` — Yageo `MFR-25FBF52-1K` ×10
- [ ] `BUY-P0` — Yageo `SQP10AJB-4R7` ×1 and `SQP10AJB-8R2` ×1
- [ ] `BUY-P0` — Molex `2147531022` ×2 and `2264291023` ×2
- [ ] `BUY-P0` — Sullins `PRPC040SAAN-RC` (`S1011EC-40-ND`) ×10 strips
- [ ] `BUY-P0` — 3M Tape `92`, 12.7 mm × 16.5 m, ×1 roll

### Maker / metal supplier

- [ ] `BUY-P0` — K&S `#9831` tube ×1 pack
- [ ] `BUY-P0` — K&S `#9861` rod ×1 pack
- [ ] `ARRANGE` — exact ITW Formex `GK-10BK` ×1 sample sheet
- [ ] `ARRANGE` — traceable 0.5–0.8 mm polycarbonate ×1 sample after source is frozen
- [ ] `ARRANGE` — 3M `FP-301` black, white, and red ×1 size sample each after
      joint/wire measurement; red permanently identifies both ends of `CELL_POS`

### Amazon / local tool supplier

- [ ] `BUY-P0` — ESP32-C3 SuperMini B0G5XS345R, one pack of at least three
- [ ] `BUY-P0` — Klein `MM450` ×1 + `69032` ×1 + `69033` ×1 spare input fuses
- [ ] `BUY-P0` — KORAD `KA3005P` ×1
- [ ] `BUY-P0` — one low-current hook-lead set and one short ≥5 A lead set
- [ ] `BUY-P0` — one grounded ESD mat-and-wrist-strap kit
- [ ] `BUY-P0` — one local mock-up set: ~1 mm card, tape, graph paper, putty
- [ ] `BUY-P0` — one each: 20–30 AWG stripper, fine needle-nose pliers,
      round-nose pliers, caliper, magnifier, fine solder wick, and heat gun
- [ ] `BUY-P0` — one set containing: jeweler's saw, bench pin, 2/0–4/0 blades,
      needle files, 400–800 grit abrasive, metric rule, and square
- [ ] `OWNED` — inspect the X-Tronic tweezers; buy one ESD-safe precision pair
      (`BUY-P0`) only if the included pair fails the incoming check
- [ ] `BUY-P0` — one each: ANSI Z87.1 eye protection, source-capture electronics
      fume extractor, nonflammable work surface, and Li-ion storage container

### Borrow/access

- [ ] `ARRANGE` — access to ×1 calibrated Fluke `289` or an alternatives-row instrument whose
      total uncertainty is ≤5 mV at 4.20 V
- [ ] `ARRANGE` — access to ×1 calibrated Pico `USB TC-08` + Pico `SE051` ×3, or an
      alternatives-row three-channel thermal logger/probe set
- [ ] `ARRANGE` — access to ×1 two-channel oscilloscope and ×1 alternatives-row
      ≥100 kHz fast current-capture instrument
- [ ] `ARRANGE` — access to ×1 alternatives-row charge-current logger that can
      record the full ≤18 h first charge at 100 mA
- [ ] `ARRANGE` — for every 34461A logger choice, one continuously connected
      compatible SCPI/BenchVue host with qualified storage; arrange two complete
      instrument/host sets if 34461A fills both simultaneous logger roles
- [ ] `ARRANGE` — logging host(s), software, USB/ground plan, and storage that
      pass a ≥20 h dry run for the selected JS220/Pico/DMM combination
- [ ] `ARRANGE` — two repeatable speaker baffle/cavity comparison fixtures
- [ ] `ARRANGE` — FreeCAD-capable host after parts are measured

### Later held prerequisites — not checkout actions

These are deliberately absent from the purchase checklist until an earlier
test selects the process:

- `HOLD` — appropriate paint booth or legal outdoor workspace, only if spray
  coating wins the finish coupons;
- `HOLD` — separate acid-flux controls, only if the empty-brass joint coupon
  forces the Stay-Clean path.

## Copy/paste prompt for Claude

```text
Review docs/FINAL_MATERIALS_FOR_REVIEW.md as an independent EE, firmware,
mechanical, and procurement audit. Compare it with
docs/CLAUDE_R1_BUILD_PROPOSAL.md, but treat the F0 status labels as controlling.
For every BUY-P0 row and every alternatives row, return: ACCEPT / REJECT /
REPLACE, confidence %, primary-source evidence, coupled design impacts, and an
exact corrected MPN + quantity when replacing anything. Check cell charge and
discharge limits, every USB/source state, regulator startup/thermal margin,
fuse time-current behavior, I2S TX slots, hard speaker power limiting, carrier
pin order, antenna/metal clearance, battery guarding, fit, and current seller
identity. Do not call the final device GO without physical gate evidence.
```

## Questions Claude should answer in its review

1. Are separate Fixture A (standalone charge), Fixture B (battery-free bench
   source), and the held future source-adjacent fused discharge adapter correct?
   What exact load-sharing or positive-interlock hardware is acceptable for the
   final enclosure, without ever using #4410 as a load pass-through?
2. Does the received SuperMini tie `5V` directly to receptacle VBUS? If yes,
   confirm that diode-only system powering is categorically rejected and choose
   an exact controller replacement, reviewed trace-separated interface, or
   positive mechanical service interlock. Review every enumerated source state.
3. After recalculating the 5 V amplifier/controller demand at minimum cell
   voltage, what fuse/adapter and controller interface can preserve ≥20% hot
   current margin for the exact #258 shipping lot without an unfused #4410 path?
4. Which speaker/cavity wins after differential-RMS and speech A/B tests, and
   where is the board-specific volume cap enforced against persisted and
   remote 0–100 commands?
5. Does hardware capture confirm the source-predicted left-only TX slot? If so,
   should the amplifier `SD` mode select left explicitly instead of using the
   default mono-mix assumption?
6. Does the TXU-EVM/TXU0104 experiment safely isolate every I2S/control pin
   when either side is unpowered while preserving the waveform and `SD_MODE`
   thresholds, and what exact small carrier makes it final? Would the
   SN74AHCT125N/MGSF2N02ELT1G or ISO7740FDWR alternative be safer?
7. What exact carrier, service interlock, rigid cell guard, and measured frame
   envelope will be frozen before brass is cut?

## Primary technical references

- [Reference project page](https://www.huyvector.org/robots-kinetic/pocket-ai-assistant)
  and [assembly video](https://www.youtube.com/watch?v=25RGnr407PM)
- [Espressif ESP32-C3 datasheet](https://documentation.espressif.com/ESP32-C3_Datasheet_en.pdf)
- [Adafruit #326 OLED](https://www.adafruit.com/product/326),
  [#6049 microphone](https://www.adafruit.com/product/6049), and
  [#3006 amplifier](https://www.adafruit.com/product/3006)
- [Sullins PRPC040SAAN-RC break-away header](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PRPC040SAAN-RC/2775214)
- [Klein MM450](https://www.kleintools.com/catalog/multimeters/slim-digital-multimeter-trms-auto-ranging-600v-temp)
  and its maker-specified replacement-fuse catalog
  [`69032`/`69033`](https://www.kleintools.com/catalog/replacement-parts/test-measurement-replacement-parts)
- [Fluke 289 logging multimeter](https://www.fluke.com/en-us/product/electrical-testing/digital-multimeters/fluke-289)
- [Fluke 80 Series V manual](https://assets.fluke.com/manuals/80v_____umeng0200.pdf)
  (87V MIN/MAX rejection evidence), [Keysight 34461A](https://www.keysight.com/us/en/product/34461A/digital-multimeter-6-5-digit-truevolt-dmm.html),
  and [Keithley DMM6500](https://www.tek.com/en/products/keithley/digital-multimeter/dmm6500-6-5-digit-multimeter)
- [Pico USB TC-08 specifications](https://www.picotech.com/data-logger/tc-08/usb-tc-08-specifications)
  and [SE051 probe/accessory catalog](https://www.picotech.com/data-logger/tc-08/usb-tc-08-accessories)
- [MAX98357A datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf)
- [Adafruit #258 protected pack](https://www.adafruit.com/product/258),
  [#4410 charger](https://www.adafruit.com/product/4410), and
  [#1131 JST-PH extension sample](https://www.adafruit.com/product/1131), and
  [#4755 load-sharing alternative](https://www.adafruit.com/product/4755);
  [#501](https://www.adafruit.com/product/501) is the dedicated charger USB source
- [Pololu #2810](https://www.pololu.com/product/2810),
  [#2873](https://www.pololu.com/product/2873), and adjustable-cutoff
  alternatives [#2870](https://www.pololu.com/product/2870) and
  [#2871](https://www.pololu.com/product/2871)
- Molex Micro-Fit 3.0 Phase 0 disconnect assemblies
  [`2147531022`](https://www.molex.com/en-us/products/part-detail/2147531022)
  and [`2264291023`](https://www.molex.com/en-us/products/part-detail/2264291023)
- [TI TXU-EVM](https://www.ti.com/tool/TXU-EVM)
  ([DigiKey `296-TXU-EVM-ND`](https://www.digikey.com/en/products/detail/texas-instruments/TXU-EVM/15853910)),
  [TXU0104](https://www.ti.com/product/TXU0104),
  [SN74AHCT125](https://www.ti.com/product/SN74AHCT125), and
  [ISO7740](https://www.ti.com/product/ISO7740); the AHCT candidate's specified
  sink is onsemi [MGSF2N02EL](https://www.onsemi.com/pdf/datasheet/mgsf2n02el-d.pdf);
  rejected-network evidence:
  [TXB0104](https://www.ti.com/product/TXB0104) and
  [SparkFun BOB-11771](https://www.sparkfun.com/sparkfun-voltage-level-translator-breakout-txb0104.html)
- [Nitecore NL169R](https://www.nitecore.com/product/nl169r) and
  [Fenix ARB-L16-700UP](https://www.fenixlighting.com/products/fenix-arb-l16-700up-built-in-usb-rechargeable-battery)
- [Littelfuse PICO II 251-series data](https://www.littelfuse.com/assetdocs/littelfuse_fuse_251_253_datasheet.pdf)
  and [Vishay WSL3637 data](https://www.vishay.com/docs/30099/wsl3637.pdf);
  [Yageo MFR-25FBF52-1K](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-1K/13011)
  is the exact guarded-sense resistor sample
- [Joulescope JS220 specifications](https://download.joulescope.com/products/JS220/JS220-K000/description.html),
  [JS220 isolation/user guide](https://download.joulescope.com/products/JS220/JS220-K000/users_guide/Joulescope%20JS220%20User%27s%20Guide%20v1_0.pdf),
  [Pico USB TC-08 user guide](https://www.picotech.com/download/manuals/USBTC08UsersGuide.pdf),
  [Keysight N2820A/N2822A data](https://www.keysight.com/content/dam/keysight/en/doc/ungate/data-sheets/5991-1711.pdf),
  and [Rohde & Schwarz NGU data](https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_brochures_and_datasheets/data_sheet/3608_6802_32/NGU_dat_en_3608-6802-32_v0201.pdf)
- [onsemi 1N5820 data](https://www.onsemi.com/download/data-sheet/pdf/1n5820-d.pdf)
  (rejection evidence for the former USB-isolation proposal)
- [Same Sky CMS-20143-158SP](https://www.sameskydevices.com/catalog/audio/speakers/miniature-%2810-mm~40-mm%29)
  and [CES-20134-088PM datasheet](https://www.sameskydevices.com/product/resource/ces-20134-088pm.pdf)
- [ITW Formex GK data](https://www.itwformex.com/file/output/1085/Formex-GK-Data-Sheet.pdf)
  and [3M Tape 92 data](https://www.3m.com/3M/en_US/p/d/b00034565/)
