# Engineering assessment — 2026-10-01

The original [Max Imagination video](https://www.youtube.com/watch?v=Sa6EslOHsI0) demonstrates a very small brushed FPV quad. It is a useful reference for learning, but the retrieved material is not a consistent, production-ready set of specifications. The original aircraft uses a Pro Mini, MPU6050, nRF24 link, discrete motor drivers, four 6 × 14 mm motors, small props, and 1S power. The creator reports roughly 30 g flying mass. The later [ESP-FLY](https://www.seeedstudio.com/ESP-FLY-co-create-p-6744.html) is the practical Wi-Fi baseline in this package. This is a deliberate hardware revision, not a claim that the original Arduino already supports Wi-Fi.

## Decisions and evidence quality

| Decision | Engineering reason | Evidence / remaining qualification |
|---|---|---|
| Buy one ESP-FLY kit as the first build | Matched core parts reduce motor, prop, PCB and battery sourcing uncertainty | Product listing and source reviewed; no sample physically inspected |
| Initial control: phone Wi-Fi and telemetry | Fits the requested Wi-Fi feature using existing local flight-control firmware | Protocol and code audited; app interoperability remains a bench test |
| Initial flights without FPV payload | Establish actual thrust, current and control margin first | Camera may consume most published payload allowance |
| Optional analog 5.8 GHz FPV | Existing supported architecture, separate from control link | Camera voltage, total mass and physical fit must pass receipt checks |
| Use supplied frame first | Preserves the creator's tested hardware arrangement | Its exact motor-axis coordinates are not published manufacturing dimensions |
| Provide independent editable 75 mm frame | Gives room to inspect wiring and accommodate provisional part envelopes | CAD checked; printing, strength, vibration and flight untested |
| Pin and patch firmware before bench qualification | Source inspection found malformed-packet and startup motor-test concerns | See firmware report for actual compile and regression-test results |

The requested meaning of “tested” is separated into five layers: source facts, calculations, digital artifacts, electrical bench results, and flight results. The first three can be checked here. The last two require hardware. No marked acceptance requirement is silently converted into a claimed result.

## Why a direct copy of the original has unresolved problems

The current YouTube description names a 5 V/16 MHz Pro Mini, while the [creator's older written instructions](https://www.elecrow.com/sharepj/make-a-tiny-arduino-drone-with-fpv-camera-317.html) name 3.3 V/8 MHz. The description also lists a small switching diode where the written build discusses a Schottky diode. These are electrically consequential differences, not cosmetic substitutions. The current downloadable firmware is examined in [firmware-audit.md](firmware-audit.md).

A 1S cell ranges up to 4.2 V when charged. Feeding it to a 5 V regulator does not create 5 V; feeding it through a 3.3 V linear regulator loses regulation when battery voltage approaches output voltage plus dropout. A 16 MHz AVR must also meet its speed-versus-voltage specification, regardless of whether a one-off sample seems to run. A bare MPU6050 or nRF24 is not a 4.2 V supply load. A breakout's input rating depends on the regulator and pull-up routing actually fitted. [ATmega328P product and data sheets](https://www.microchip.com/en-us/product/ATmega328P), [Nordic nRF24L01+ specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf).

The creator's grounded-foil observation is evidence that one assembly changed behavior. It does not isolate the cause of resets. Supply droop, common impedance in ground wiring, brush noise, reset-line coupling, and regulator instability can look similar. Investigate rails and reset behavior with a scope; a shield cannot supply missing current. Keep any conductive shield insulated and away from the antenna. In the revised kit, start with the manufacturer's board and layout, then diagnose measured behavior.

## Propulsion, mass and useful margins

Use gram-force for thrust figures and grams for mass in the ratio below. The gravitational constant cancels. Manufacturer no-load RPM is not a thrust specification: prop diameter, pitch, blade count, supply voltage, winding, brush direction and battery sag all matter.

At 25 g flying mass, each of four motors supplies 6.25 gf in a level hover; at 28 g it supplies 7 gf. The vendor's 17 gf per motor implies 68 gf total and ratios of 2.72 and 2.43 respectively. These are calculations from a vendor claim, not a measured thrust curve. The [official repository](https://github.com/Seeed-Projects/Co-Create_ESP-FLY) does not supply the voltage/current/test-fixture data necessary to reproduce that claim exactly.

| Measured total static thrust | 25 g aircraft | 28 g aircraft | 32 g aircraft |
|---:|---:|---:|---:|
| 40 gf | 1.60 | 1.43 | 1.25 |
| 50 gf | 2.00 | 1.79 | 1.56 |
| 60 gf | 2.40 | 2.14 | 1.88 |
| 68 gf | 2.72 | 2.43 | 2.13 |

For this project, require at least 2.0:1 on a fresh battery and 1.5:1 at the planned end-of-flight loaded voltage, with the actual propellers and payload. These are project acceptance targets, not universal flight laws. Testing only one motor from a laboratory supply overestimates a four-motor battery system if connector and cell losses are ignored. Measure individual motors, then verify the assembled four-motor system on a guarded fixture. Never hand-hold the aircraft for a powered prop test.

Weigh the complete drone, including solder, antenna, all wires, retaining material, propellers and battery. Keep a separate mass ledger. A label saying “3 g camera” may omit its antenna, lead, connector and mounting cover. Every extra 1 g on a 25 g aircraft adds 4% weight. Bigger batteries may improve energy capacity while reducing thrust margin and increasing rotational inertia; “higher mAh” is not enough to approve a replacement.

## Energy and current budget

A 250 mAh cell at nominal 3.7 V stores approximately 0.925 Wh. Using an assumed 80% capacity for planning leaves 0.200 Ah. Predicted minutes are `60 × usable_Ah / measured_average_A`. This approximation ignores voltage-dependent loads, aging, temperature and reserve errors.

| Average battery current | Planning endurance, 80% capacity |
|---:|---:|
| 2.0 A | 6.0 min |
| 2.4 A | 5.0 min |
| 3.0 A | 4.0 min |
| 4.0 A | 3.0 min |

At 2.4 A baseline current, adding a hypothetical 0.33 A video load changes the energy-only estimate to 4.40 minutes. The real reduction may be greater because camera mass also raises motor demand. This is a sensitivity example, not a measured camera-equipped flight time.

The kit's advertised 25C cell corresponds arithmetically to `0.25 Ah × 25 = 6.25 A`. That is a cell label, not a tested capacity of the whole electrical path. A PH-series connector's specified rating can be only 2 A under the manufacturer's wire/temperature conditions. The connector, PCB, FETs, diodes and wiring each impose separate limits. Require the actual connector identity and operating-current trace before approving the power path. If measured demand exceeds any component's allowed duty or temperature, stop and redesign that path; do not waive the rating because the battery advertises a larger number. [JST PH specification](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf).

Contact resistance is especially costly at low voltage: an illustrative 50 mΩ connection drops 0.20 V and dissipates 0.80 W at 4 A. That loss both heats the connector and removes propulsion voltage. The value is a diagnostic example, not a measurement of the kit connector. Measure loaded voltage at the cell lead, board VBAT and 3.3 V rail to distinguish cell, connector and regulator losses.

The ESP32-S3 supply must tolerate radio current bursts. Espressif specifies a 3.3 V supply capable of at least 500 mA for a chip-level design, with suitable local decoupling. This is regulator headroom, not an assertion that the drone's processor continuously draws 500 mA. Require the 3.3 V rail to remain within the operating range during motor steps and active Wi-Fi. [Espressif hardware guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html).

## Motor-driver checks

For a discrete replacement board, each motor needs its own low-side N-MOSFET: motor positive to VBAT, motor negative to drain, source to ground, gate to PWM with a defined gate-to-source pull-down. A flyback diode belongs across the motor with cathode toward VBAT and anode toward the drain. Reversing it creates an effective short when driven. These are brushed motors; four brushless ESCs, DShot settings and ESC calibration are inapplicable.

The generic marking “SI2300” is not a complete manufacturer part number. For example, Vishay's Si2300DS specifies a maximum 85 mΩ on-resistance at 2.5 V gate drive. A hypothetical 1 A drain current dissipates about 85 mW at continuous conduction, before switching losses and temperature effects; 2 A increases that to 340 mW. A headline ampere rating does not guarantee operation on a tiny hand-wired pad. [Si2300DS data sheet](https://www.vishay.com/docs/65701/si2300ds.pdf).

The creator circuit's small switching diodes also need a repetitive-current and thermal check against measured PWM current. A diode's one-time surge rating cannot be used as its continuous flyback rating. Because actual motor inductance, running/stall current and supplied diode markings are unknown, this package does not certify the kit driver stage. The bench test must capture drain overshoot, supply ringing and temperature. Do not deliberately stall these tiny motors for a prolonged measurement.

## Frame calculations and limits

The independent frame uses a 75 mm diagonal motor-axis distance and 30 mm propellers. For a square X arrangement, adjacent motor spacing is `75 / sqrt(2) = 53.033 mm`; total swept width is 83.033 mm. The four centres are `(±26.5165, ±26.5165)` mm. The camera-free board and battery envelopes are centred in that square. This is larger than the creator's 50 mm-class craft.

The generator evaluates exact rotor-solid intersections, mesh validity, solid volume and conservative horizontal clearance. Its tolerance allowance includes motor-axis error, prop-radius error and component placement. The battery and populated-board height remain assumptions until receipt; a passing calculation cannot turn those assumptions into measurements. See [cad-report.json](../verification/cad-report.json) for generated values and [frame-design.md](frame-design.md) for the physical fit protocol.

Longer arms change torque leverage, rotating inertia and flex. Applying a point-mass approximation to the motors gives inertia proportional to arm length squared; moving from a nominal 50 to 75 mm wheelbase multiplies that contribution by 2.25. That is not the ratio for the entire aircraft and it does not produce a reliable new PID value. Use the kit frame for initial flight, then qualify the new frame separately.

## What remains an open engineering gate

The current kit's populated height, battery envelope, motor loaded current/thrust curve, exact connector current capability, diode/FET identity, RF behavior and thermal performance need measurements or manufacturer clarification. App timeout behavior and board orientation also need bench confirmation. These are recorded as unresolved requirements in [acceptance-tests.md](acceptance-tests.md), with a test sheet in [measurement-log.csv](../verification/measurement-log.csv). No purchase or physical test was performed in this session.
