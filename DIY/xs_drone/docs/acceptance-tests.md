# Acceptance tests and evidence ledger

These are measurable release gates. **Physical status at delivery: NOT RUN.** Digital checks are recorded separately in [verification](../verification/). A tutorial flight, a seller's specification and a successful compile are different kinds of evidence.

Use [measurement-log.csv](../verification/measurement-log.csv). Record date, operator, hardware revision, firmware hash, app/OS version, instrument/range, environment, measured value, uncertainty, result and evidence file. Do not overwrite failures with a pass; add a new row after correcting the cause.

## A — Incoming and mechanical checks

| ID | Test | Pass criterion | Method |
|---|---|---|---|
| A01 | Inventory and revisions | Matches selected kit BOM; differences resolved | Photograph all components and labels |
| A02 | Motor/prop interface | Matched 6 × 15 class motors and 0.8 mm hub fit; no binding, shaft damage or loose hubs | Calipers, visual inspection, hand rotation |
| A03 | Polarity and chemistry | 1S 4.2 V full-charge LiPo; correct mating polarity; cell undamaged | Meter plus cell label and datasheet |
| A04 | Envelopes | Actual PCB, connector, leads, battery and retainers fit inside CAD allowances or CAD updated | Measure in at least two orientations; include lead exits |
| A05 | Rotor clearance | ≥2 mm to unrelated fixed objects at rest and sufficient clearance through measured flex; no wire intrusion | Hand rotate every prop; inspect from above and side |
| A06 | Frame and retention | No cracks; motors do not move under handling; board/cell cannot slide into rotor area | Gentle pull/deflection checks, no powered props |
| A07 | Mass / CG | All-up mass known to ±0.5 g, symmetric balance; thrust ratio gates satisfied at that mass | Coin beam balance: a ruler on a round pencil, the aircraft on one end, coins at the same distance on the other (US nickel 5.000 g, penny 2.500 g, dime 2.268 g); the ledger estimate until then. Balance near the motor-diagonal crossing. The 0.01 g scale was dropped 2026-11-07 |

The battery's dimensions are still unknown in this session. Passing A04 is required before describing the custom model as physically compatible. A05 includes the antenna and restraint, which the CAD does not fully model.

## B — Electrical checks

| ID | Test | Pass criterion | Method |
|---|---|---|---|
| B01 | Unpowered net check | VBAT/GND not reversed or shorted; GPIO outputs reach correct drivers | Continuity and diode-mode checks against diagram |
| B02 | Board-only power | Stable boot, correct IMU identity and sane stationary data; no unexplained excessive current | Current-limited 1S-equivalent supply, props absent |
| B03 | Regulated rail integrity | 3.3 V supply stays within the ESP32-S3/IMU operating limits, including load transients; no reset | Scope at board rails, short ground spring, 4.2/3.7/3.5 V source cases |
| B04 | Connector and wiring | Measured operating current/duty and temperature comply with actual component rating; no intermittent voltage drop | Current trace and differential voltage across complete mating pair |
| B05 | Driver repetitive stress | FET VDS/VGS, diode repetitive current/power and device temperatures remain within fitted-part limits with margin | Oscilloscope/current probe or qualified shunt; thermal measurements |
| B06 | Battery under load | Current within cell limits; acceptable voltage sag/temperature; reserve retained | Complete-system fixture, real cell, load trace |
| B07 | Voltage telemetry | Error ≤0.10 V over 3.5–4.2 V as a project target | Compare calibrated meter and telemetry at several points |
| B08 | Charging | Correct CC/CV behavior and ≤cell-rated charge current; stops at allowed voltage; no abnormal heat | Supervised charge with motors disabled and FPV disconnected |

For B04, the historical PH connector datasheet is 2 A at its stated conditions; do not substitute the battery's 6.25 A C-rating arithmetic. For B05, a small diode's non-repetitive surge rating does not approve repeated PWM current. A thermocouple/IR reading may miss a tiny junction hot spot; apply datasheet thermal limits and waveform analysis, not touch alone.

Bench supplies and long leads can create artifacts. Measure at the board, use a fixture that cannot short the cell, and account for the meter/shunt's voltage drop. Avoid ground clips that short switched motor nodes through earth-referenced instruments. If measurement equipment or competence is missing, borrow a suitable lab setup before claiming these tests passed.

## C — Software, controls and link loss (props removed)

| ID | Test | Pass criterion |
|---|---|---|
| C01 | Firmware identity | Built source commit, patch hash, target and toolchain recorded; flashed image corresponds to that build |
| C02 | Startup | No unintended motor command; startup motor self-test disabled in patched configuration |
| C03 | IMU axes | Pitch/roll/yaw signs and physical orientation correct; stationary gyro settles; no repeated bus errors |
| C04 | Motor mapping | M1 FR, M2 RR, M3 RL, M4 FL; correct directions and clean stop |
| C05 | Controller mapping | Zero throttle means zero intended thrust; stick signs/ranges and stop action verified |
| C06 | Stale command behavior | Actual outputs reach zero within patched cutoff plus scheduling allowance; target ≤0.60 s from last valid command |
| C07 | Reconnect/arming | Nonzero-throttle reconnection cannot restart motors; deliberate zero-throttle action required before thrust resumes |
| C08 | App lifecycle | Screen lock, background, force-close, Wi-Fi disable and OS network switching each meet C06/C07 |
| C09 | Packet validity | Truncated, oversized and bad-checksum packets rejected without crash or motor command; host tests pass and bench replay inspected |
| C10 | Wi-Fi contention | At planned operating distance, command timing remains acceptable with realistic interference; stale-link action still works |
| C11 | Speaker path (added 2026-11-09) | A 1 kHz tone from the sigma-delta DAC reads 0.43 V p-p ±20 % at the filter node and plays clean at the speaker with no audible pulse-rate whine; full scale does not clip at a 3.5 V supply; the amplifier's quiescent draw is under 20 mA (its datasheet's typical is 10 mA at 3.6 V) |
| C12 | Voice loop (added 2026-11-09) | Props off: a spoken sentence from the drone's microphone transcribes correctly on the desk server; the server's reply plays through the speaker and is intelligible at 1 m; both run over the aircraft's own Wi-Fi link while the camera stream is up; the microphone's clock pin reads about 2.05 MHz (the 128× ratio), not 1.02 |

The patched design uses 300 ms stabilization and 500 ms motor-stop thresholds. C06 includes 100 ms scheduling/measurement allowance as a release ceiling, not proof of a measured timing bound. If the patch or build configuration changes, derive the acceptance limit again from the actual source. Host timing tests prove code decisions at selected timestamps; they do not measure FreeRTOS scheduling or phone behavior.

For each lifecycle scenario, hold a nonzero command with props absent, trigger the loss, and capture PWM or motor-supply behavior against a timestamped last-valid-packet marker. Verify all four outputs, not just the UI. Return the link with throttle deliberately nonzero first to test lockout; then set zero and verify deliberate recovery. Never perform this test by holding a spinning, propeller-equipped drone in a hand.

## D — Propulsion fixture and flight

| ID | Test | Pass criterion |
|---|---|---|
| D01 | Motor matching | Repeatable current across all four, props on, at the same duty and voltage on the bench supply; investigate >10% mismatch |
| D02 | Whole-aircraft margin | ≥2:1 thrust/weight fresh, read in flight: a full-throttle punch from a low hover over the bed, the accelerometer z log peak in g is the ratio; without the log, hover at ≤70% thrust command (thrust rises about as duty squared); ≥1.5:1 at the chosen end-of-flight voltage (hover ≤82%); the voice build at 37.5 g est. is designed to 1.8:1, so expect a hover command near 74 % (2026-11-09) |
| D03 | Thermal endurance | B04–B06 remain satisfied over representative flight duty; motor temperatures compatible with adhesive/frame |
| D04 | Initial hover | Several short low hovers without flips, strong oscillation, resets or unpredictable command response |
| D05 | Repeatability | Three controlled flights with logged time/voltage, no new mechanical or thermal defect, reserve on landing |
| D06 | Custom frame | Repeat A04–A07, B03–B06, C03–C10 and D01–D05 after changing geometry/material |
| D07 | FPV addition | Voltage, mass, mount, view, RF coexistence and new endurance qualified; repeat affected prior gates |

The 10% matching target is a diagnostic threshold for this build, not a manufacturer tolerance. Current measurement must include the controller/radio and video load, if fitted. A no-load motor current measurement cannot stand in for D02 or B05. Since 2026-11-07 there is no thrust stand: D02 is read from the aircraft itself during the first hover attempts of D04, which therefore start the moment it lifts.

## Minimal useful log for every flight

Record all-up mass, pack identifier, starting and ending resting voltage, minimum loaded voltage if available, flight duration, firmware/config hash, app version, observed hover throttle, conditions, motor/connector temperature observations and any control anomaly. Land early until the consumption/voltage relationship is established. Do not infer low-battery protection from the presence of a telemetry value or warning LED.

## Stop conditions

Stop and diagnose if a motor starts at boot, the control link loses stop behavior, an axis is reversed, a rail resets, a connector/device exceeds its rating, the cell is damaged, a motor binds, a prop is loose, or the frame/retainer can contact a rotor. These are direct failure conditions for the hardware being assembled, not theoretical paperwork gates.
