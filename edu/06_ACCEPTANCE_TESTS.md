# Applied note — prototype acceptance-test worksheet

> **Status: R1 RELEASE WORKSHEET — 2026-09-02.** This worksheet accepts the
> released architecture in
> [FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md)
> (protected pack + in-frame USB-C charger + slide switch + LDO-direct rail).
> It says what must be proved on the physical build; nothing here asserts the
> present parts have already passed.

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
- [ ] The power design's end-of-discharge behavior is understood and recorded:
      the LDO-direct rail sags until brownout, with the pack's documented
      3.0 V protection cutout as the backstop. (R1 deliberately has no
      separate UVLO module — the bench sweep proves the sag is graceful.)
- [ ] The USB/service rule is written where the builder works: switch OFF and
      pack JST unplugged before the SuperMini's USB-C connects; device off
      while the charger's USB-C is in; never both ports at once.

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

## Gate D — power chain, battery absent

Use the current-limited supply and safe procedure in
[Lesson 06](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md).
The supply stands at the pack's JST position for every test here.

- [ ] The switched rail feeds the SuperMini `5V` pin and amp `VIN`; the
      SuperMini's 3.3 V output is verified at no-load and under display +
      mic load before the amp joins.
- [ ] Supply sweep 4.2 → 3.3 V under Wi-Fi + loud audio: no reset, no I2C
      errors, no audio dropout anywhere in the range. Record the voltage
      where behavior first degrades.
- [ ] Slide-switch contact drop measured < 50 mV at 0.5 A; 20 on/off cycles
      give 20 clean boots.
- [ ] Loaded drop across the JST, switch, and wiring is measured (not
      inferred); total upstream drop recorded at peak load.
- [ ] Idle, average, and peak input currents recorded for the runtime
      estimate and the charge-rate sanity check.
- [ ] Off-state: switch off → input current ≈ 0; no alternate path keeps any
      module lit.
- [ ] Temperatures stabilize within limits after ten minutes of loud audio +
      Wi-Fi: amp warm is fine, nothing too hot to touch comfortably.

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
- [ ] MCU, amplifier, speaker, charger board, wiring, and pack-bay
      temperatures are recorded after stabilization.
- [ ] Brownout behavior is safe when simulated with the bench source (sweep
      below 3.3 V): the device resets or halts cleanly, without repeated
      high-current restart loops; no destructive cell fault is injected.
- [ ] Removing an OLED or signal produces a bounded logged failure/headless
      mode rather than uncontrolled heating or repeated high-current restart.
- [ ] With the switch OFF, USB into the SuperMini powers only the SuperMini
      and its 3.3 V peripherals — the switched bus side reads dead and no
      current flows toward the JST/charger in any permitted state.

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

## Gate H — protected-pack introduction

This gate opens only after A–G pass and the pass records exist.

- [ ] JST polarity metered against the charger's markings and pack
      open-circuit voltage checked (3.0–4.2 V) before the first mating.
- [ ] End-of-discharge behavior already proven with the bench substitute
      (Gate D sweep); the pack's 3.0 V protection cutout is the backstop,
      not the operating plan.
- [ ] First pack power occurs on a fire-resistant surface with the JST
      immediately unpluggable; no soldering, cutting, drilling, or metalwork
      occurs with the pack connected.
- [ ] Pack behavior matches the qualified bench envelope; no protection trip,
      abnormal heat, damage, or movement occurs.
- [ ] Runtime is measured under a named workload; it is not inferred by simply
      dividing mAh by 3V3 rail current.
- [ ] First charge attended: device off, charger current at its programmed
      value (100 mA default; 500 mA only after this cycle and only for the
      500 mAh pack), pack cool, DONE indication, 4.20 ± 0.05 V. The 500 mA
      jumper decision is recorded.

## Substitutions and failures

A substitution reopens every affected gate. Compare exact order code,
schematic, pin order, logic levels, power/startup/thermal limits, configuration,
dimensions, connector, acoustics, RF, firmware, and failure behavior. Record a
failed result and disposition; do not delete it after a later passing run.
