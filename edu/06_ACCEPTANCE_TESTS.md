# Applied note — prototype acceptance-test worksheet

> **Status: NOT A DESIGN FREEZE.** The earlier “Rev A locked” text was
> withdrawn because the power chain, exact marketplace modules, service-power
> isolation, normal undervoltage shutdown, speaker assembly, and mechanical
> envelopes are not yet qualified. This worksheet says what must be proved; it
> does not say the present parts have passed.

Read [systematic debugging and the capstone](fundamentals/13-debugging-integration-and-capstone.md)
and use a fresh [lab record](fundamentals/reference/lab-record-template.md) for
each test. Keep the lithium cell out until the final gate.

## How to use this page

For every checkbox, attach a dated record containing:

- test-article ID and photographs;
- exact part markings/order code and received revision;
- schematic/BOM/firmware revision;
- instruments, settings, probe points, source voltage, and current limit;
- test condition, prediction, stop conditions, and pre-set pass/fail limit;
- values with units and evidence labels; and
- trace/photo/log paths plus reviewer and disposition.

An unchecked line is unresolved. “It turned on,” a listing, `netcheck`, Wokwi,
ERC/DRC, or collision-free CAD cannot substitute for the physical record.

## Gate A — one reconciled definition

- [ ] One reviewed schematic shows every source, return, protection, enable,
      boot strap, service-power, signal, frame, and BTL speaker connection.
- [ ] One controlled BOM names exact manufacturer/order code or explicitly
      labels an incoming-inspection sample candidate.
- [ ] The firmware source contract and wiring map agree on every GPIO, voltage,
      address, sample rate, slot, direction, and active level.
- [ ] Each connector is specified by family, pitch, positions, housing,
      contacts, mate, polarity, and physical pin order. “JST-PH 2.5 mm” is not
      accepted; genuine JST PH is 2.0 mm pitch.
- [ ] The power design includes a reviewed normal undervoltage shutdown with
      hysteresis, not only an assumed cell-protection cutoff.
- [ ] USB/service power has a reviewed isolation or source-selection design.

## Gate B — incoming exact parts

- [ ] Both faces, markings, seller/order, and lot of every module are recorded.
- [ ] Length, width, maximum height, connector/port locations, and configuration
      parts are measured on the received samples.
- [ ] Module pin order and supply range are verified against primary evidence
      and unpowered checks before connection.
- [ ] Onboard regulators, LEDs, pull resistors, level shifters, decoupling, and
      jumpers relevant to this design are inventoried.
- [ ] The protected cell wrapper, contact ends, dimensions, and manufacturer
      ratings are intact and match the eventual qualified holder/charger plan.
- [ ] The external charger's manufacturer instructions explicitly support the
      exact cell chemistry, size, polarity, and allowed charge conditions.
- [ ] Speaker nominal impedance, DC resistance, dimensions, enclosure, lead
      insulation, and source documentation are recorded without transferring
      specifications from a different speaker.

## Gate C — unpowered harness and frame

With every source removed and stored energy discharged:

- [ ] Intended grounds/returns and signal nets have the expected continuity.
- [ ] Raw input, 3V3, USB power, and signal nets are isolated where the
      schematic requires isolation.
- [ ] No adjacent connector pin or solder joint is bridged.
- [ ] The conductive frame is isolated from raw input, 3V3, GND, USB, every
      signal, and both speaker outputs.
- [ ] The speaker connects only between amplifier `OUT+` and `OUT−`; neither
      terminal connects to frame or ground.
- [ ] Cell contacts and powered nodes have mechanically retained primary
      insulation; paint is not counted as insulation.
- [ ] Wires have strain relief and cannot reach sharp edges or moving parts.

## Gate D — power module and input chain, battery absent

Use the current-limited supply and safe procedure in
[Lesson 06](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md).

- [ ] Exact converter sample produces the permitted rail under defined no-load
      and controlled-load conditions.
- [ ] Cold start and continued operation are recorded separately across the
      intended input range, input ramp, temperature, and real path impedance.
- [ ] Minimum rail, overshoot, ripple, and settling are captured at the load
      during defined transients.
- [ ] Loaded drop is measured across holder substitute, protection, switch,
      MOSFETs, connectors, wiring, and return; unsupported cell resistance is
      not inserted as a fact.
- [ ] Fuse/PPTC choice is supported by current-time-temperature data. Parallel
      sharing is not assumed to be exactly two times one device.
- [ ] MOSFET voltage drop and heat use maximum `RDS(on)` at actual gate drive
      and relevant temperature, with body-diode/orientation review.
- [ ] Off-state current and every alternate/backfeed path are measured.
- [ ] Temperatures stabilize within component and project limits under the
      defined high-average condition.

Any unexplained current limiting, start failure, reset, material rail dip,
abnormal heat, odor, or protection trip is a failure—not a reason to raise the
limit and continue.

## Gate E — controller and one peripheral at a time

- [ ] Bare ESP32-C3 boots through the intended service path; version and reset
      reason are recorded.
- [ ] Corrected-source contract is confirmed: GPIO1 `WS`, GPIO2 `BCLK`, GPIO3
      amp data, GPIO4 mic data, GPIO10 active-low action input, GPIO20 `SCL`,
      and GPIO21 `SDA`.
- [ ] Native USB recovery/BOOT/reset access remains available.
- [ ] One OLED is powered at the correct level, scanned at 100 kHz, initialized,
      and pixel/orientation-tested before the second target/load is added.
- [ ] Exact OLED addresses and effective pull-up resistance are recorded; SDA
      and SCL meet idle level and rise-time limits at the final 400 kHz request.
- [ ] I2S clocks measure approximately 16 kHz `WS` and 1.024 MHz `BCLK` for
      the current two-slot, 32-bit corrected-source configuration.
- [ ] Microphone raw samples have correct slot/alignment and acceptable
      silence, speech, clipping, and noise behavior.
- [ ] Amplifier mode/gain configuration is verified on the received board.
      Low-level audio is clean and no BTL output is grounded or probed unsafely.

## Gate F — simultaneous load, thermal, and faults

- [ ] Wi-Fi plus defined audio/capture workload produces no reset or corruption.
- [ ] Input current, rail minimum, reset log, audio level, and test duration are
      recorded together; peak, RMS, and average conditions remain distinct.
- [ ] Converter, protection, MCU, amplifier, speaker, wiring, and enclosure
      temperatures are recorded after stabilization.
- [ ] Brownout/current-limit behavior is safe when simulated with the bench
      source; no destructive cell fault is injected.
- [ ] Removing an OLED or signal produces a bounded logged failure/headless
      mode rather than uncontrolled heating or repeated high-current restart.
- [ ] Service USB cannot backfeed the converter, cell path, or an unqualified
      peripheral rail in any permitted switch/jumper state.

## Gate G — exact-part mechanical, acoustic, and RF evidence

- [ ] CAD uses measured maximum envelopes for the exact cell, holder, speaker
      assembly, boards, plugs, cables, bend radii, wire loops, insulation,
      strain relief, guards, mounts, controls, and tools/fingers.
- [ ] A physical 1:1 mock-up proves the complete insertion, fastening,
      connector-mating, button/switch actuation, cell-removal, and service path.
- [ ] Display, microphone port, speaker front/rear acoustic paths, antenna
      region, USB, BOOT, and reset remain usable.
- [ ] Relative speaker/enclosure A/B testing controls sample, gain, position,
      distance, supply, and room; no spec from a different speaker is reused.
- [ ] Repeated bare-board versus final-frame RF trials record RSSI distribution,
      packet loss, throughput/latency, and reconnects in intended orientations.
- [ ] Finished coating is fully cured, but electrical safety still relies on
      retained insulation and clearance rather than the coating.
- [ ] Shake, abrasion, rattle, retention, and pocket-access tests cause no
      intermittent power, exposed conductor, control activation, or movement.

## Gate H — protected-cell introduction

This gate remains closed until A–G pass and a reviewer records the release.

- [ ] Cell polarity and open-circuit voltage are checked before insertion.
- [ ] Normal undervoltage shutdown and restart hysteresis are already proven
      with the bench substitute.
- [ ] First cell power occurs on a fire-resistant surface with immediate safe
      disconnect available; no soldering, cutting, drilling, or metalwork occurs.
- [ ] Cell behavior matches the qualified bench envelope; no protection trip,
      abnormal heat, damage, or movement occurs.
- [ ] Runtime is measured under a named workload; it is not inferred by simply
      dividing mAh by 3V3 rail current.
- [ ] Charging occurs only outside the device in the approved external charger,
      following the cell and charger manufacturers' instructions.

## Substitutions and failures

A substitution reopens every affected gate. Compare exact order code,
schematic, pin order, logic levels, power/startup/thermal limits, configuration,
dimensions, connector, acoustics, RF, firmware, and failure behavior. Record a
failed result and disposition; do not delete it after a later passing run.
