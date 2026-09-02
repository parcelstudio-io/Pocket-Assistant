# Applied note — power-chain qualification worksheet

> **Correction notice:** the previous version of this page is withdrawn. It
> treated unsupported values as verified, doubled parallel PPTC ratings,
> understated two P-FET drops, and confused the TPS63070's operating minimum
> with its cold-start requirement. Do not purchase or fabricate from that old
> calculation.

Learn the underlying physics in
[Li-ion power integrity, decoupling, UVLO, and heat](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md).
This page applies the method to the Pocket Assistant without selecting a final
topology. The present outcome is **NO-GO for a component/design freeze** and
**GO only for returnable Phase 0 samples tested without a cell**.

## Why the complete chain matters

The converter does not see an ideal cell voltage. Under load it sees the cell
minus the drops in both outgoing and return paths:

```text
protected source or bench substitute
  → contacts/holder
  → fault protection
  → reverse-polarity and on/off elements
  → wiring/connectors
  → converter VIN
  → regulated 3V3 loads
  → return path
```

For a simple first estimate:

```text
Vconverter = Vsource - Iinput × Rseries
Iinput ≈ Vout × Iout / (efficiency × Vconverter)
Ploss = Iinput² × Rseries
```

The equations interact: higher input current makes more drop, which reduces
converter voltage and can demand still more input current. Calculate with
bounded inputs, then measure at the converter pins.

## Known corrections to the earlier candidate chain

### TPS63070 / “XL63070” candidate

TI specifies TPS63070 operation down to 2.0 V **after startup**, but when the
output is below 3.0 V the IC's startup input requirement is 3.0 V. A 3.3 V
module based on it has essentially no cold-start margin from a 3.0 V source
before holder, protection, MOSFET, wire, and return drops. A listing that says
“2 V startup” does not override the IC datasheet or qualify an unidentified
module.

TPS63802 has a different, lower startup requirement, but an IC headline still
does not prove an unknown module's output current, inductor, settings, copper,
thermal behavior, or assembly quality.

### Parallel RUEF110 PPTCs

One RUEF110 is specified by Littelfuse as 1.10 A hold and 2.20 A trip at its
stated reference condition, with temperature derating and time-dependent
behavior. Two parallel polymer devices do not share perfectly or become an
exact 2.20 A-hold/4.40 A-trip part. Small resistance and temperature
differences reinforce unequal sharing. Any parallel proposal needs a reviewed
application model and physical tests; it is not frozen here.

### Two P-channel MOSFETs

At `VGS = -2.5 V`, AO3401A permits up to 85 mΩ and DMG2301L up to 150 mΩ. If
two are in series, their room-temperature maximum drops at 1.15 A calculate to:

```text
two AO3401A: 1.15 A × 0.170 Ω ≈ 0.20 V
two DMG2301L: 1.15 A × 0.300 Ω ≈ 0.35 V
```

Hot resistance can be higher. The devices are not interchangeable 20–40 mΩ
parts. A reverse-polarity/high-side circuit also needs correct source/drain,
body-diode, gate bias, `VGS` limits, startup, off-state, and USB-backfeed
analysis.

### Cell and load model

Nitecore publicly specifies the NL169's nominal voltage, capacity/energy,
maximum continuous discharge, and dimensions. Its public page does not supply
the old `0.12 Ω` internal-resistance assumption or exact protection thresholds
and timings. Leave those cells blank until obtained from the maker or measured
under a safe, reviewed method.

The older `778 mA` rail number combined a coincident transient envelope. It is
not a steady thermal or PPTC current. Record at least:

- high-average rail current and duration for energy/heat;
- transient magnitude, duration, and repetition for rail stability;
- amplifier RMS/average demand for a defined waveform and gain; and
- startup/inrush state with every load's enable behavior.

### Normal low-voltage shutdown and USB service power

“The cell is empty at 3.0 V” is not an implemented shutdown. The current
firmware does not establish a qualified battery measurement/disconnect path.
A protected cell's fault cutoff is not normal state-of-charge control. The
final design needs reviewed hardware UVLO or supervised sensing plus a reliable
disconnect and restart hysteresis.

A header that separates converter VOUT from 3V3 does not by itself prove safe
USB service mode. An unknown SuperMini regulator may still power peripherals,
conduct reverse current, or expose alternate paths. Draw and test every state,
or use a proper source selector/power mux/removable harness.

## Candidate worksheet

Do not fill unknown cells with optimistic typical values.

| Quantity | Minimum/worst or range | Evidence label/source | Physical test |
| --- | ---: | --- | --- |
| source voltage during intended normal operation |  |  | controlled supply sweep |
| exact converter cold-start requirement |  |  | power-cycle at each condition |
| exact converter running/UVLO behavior |  |  | separate downward sweep |
| high-average 3V3 current and duration |  |  | measured workload |
| transient 3V3 current/time envelope |  |  | rail/current capture |
| efficiency across input/load range |  |  | input/output power measurement |
| holder/contact loaded drop |  |  | voltage-drop test |
| protection-device current/time/temp behavior |  |  | datasheet plus bounded test |
| MOSFET maximum hot resistance at actual `VGS` |  |  | calculation plus loaded drop |
| positive and return wire/connector drop |  |  | endpoint measurements |
| regulated-rail min/max and transient limits |  |  | exact load datasheets |
| normal shutdown/restart thresholds |  |  | UVLO test with hysteresis |
| service/off-state reverse/leakage paths |  |  | every switch/USB state |
| stabilized temperatures |  |  | defined high-average load |

## Battery-free qualification sequence

1. Identify and photograph the exact converter and every protection/switch
   sample. Transcribe chip and passive markings.
2. Draw a reviewed schematic including both current paths, enables, body
   diodes, USB/service sources, and rail capacitors.
3. Test the converter alone from a current-limited supply at no load and a
   modest resistor load. Stop for out-of-range voltage, CC mode, or heat.
4. Sweep input while already running, then fully remove power and cold-start at
   each point. These are different columns.
5. Increase only to controlled loads supported by the exact module, fixture,
   resistor/electronic-load rating, and current limit. Do not use a breadboard
   or thin Dupont leads at ampere scale.
6. Add one upstream element at a time. Measure its loaded drop on positive and
   return paths; do not infer milliohms from continuity beeps.
7. Apply defined load steps and capture 3V3 at the load. Record minimum,
   overshoot, settling, input current, source/current-limit settings, and reset
   logs.
8. Test normal UVLO/restart hysteresis and every USB/off/service state.
9. Stabilize the high-average load and measure temperatures at defined ambient.
10. Repeat on multiple samples and relevant conditions. Ten starts on one unit
    at room temperature are sample evidence, not a production guarantee.

Keep the ESP32-C3, audio modules, and lithium cell disconnected until the power
module's output is understood. Keep the cell out until the complete acceptance
worksheet passes.

## Release decision

Do not freeze the converter, PPTC/MOSFET chain, carrier, holder/harness, or
metal fabrication until:

- one schematic and BOM resolve all contradictions;
- every candidate number above has bounded evidence;
- exact received samples pass startup, load-step, UVLO, backfeed, fault, and
  thermal tests with margin; and
- the complete harness later passes simultaneous Wi-Fi/audio testing from a
  current-limited source.

Primary sources:

- [TI TPS63070 datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf)
- [TI TPS63802 datasheet](https://www.ti.com/lit/ds/symlink/tps63802.pdf)
- [Littelfuse RUEF datasheet](https://www.littelfuse.com/assetdocs/littelfuse-ptc-radial-leaded-ruef-datasheet?assetguid=2139d828-f887-4a2a-9b25-01ddf761ab3a)
- [AOS AO3401A datasheet](https://www.aosmd.com/sites/default/files/res/datasheets/AO3401A.pdf)
- [Diodes DMG2301L datasheet](https://www.diodes.com/assets/Datasheets/DMG2301L.pdf)
- [Nitecore NL169 product page](https://www.nitecore.com/product/nl169)
