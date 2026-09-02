# 06 — Li-ion power integrity, decoupling, UVLO, and heat

## Learning objectives

After this lesson, you should be able to:

- distinguish cell voltage, converter-input voltage, and the regulated rail;
- calculate average power and estimate converter input current;
- distinguish converter cold start from continued operation;
- explain voltage drop, decoupling, UVLO, and thermal derating;
- assign separate jobs to charging, fault protection, and normal shutdown; and
- qualify a power module without using a lithium-ion cell.

## Durable theory and provisional hardware

The equations in this lesson are durable. The Pocket Assistant's exact
converter module, holder, protection network, switch, and cutoff are still
**PROVISIONAL project design** until exact received parts pass review and
measurement. An Amazon title or a successful calculation is not a component
qualification.

Use the evidence labels from Lesson 00. In particular, do not turn a typical
graph, marketplace claim, or assumed resistance into **DATASHEET** evidence.

## Follow one complete current loop

Current must leave the source and return to it. A simplified power path is:

```text
source +
  → holder and wiring
  → fuse/protection
  → reverse-polarity and on/off devices
  → buck-boost converter
  → 3V3 loads
  → ground/return wiring
  → source -
```

`BAT+`, converter `VIN`, `3V3`, and USB `5V` are different nodes. Calling all
of them “power” hides the exact voltage and fault path being discussed.

At DC, a first approximation for the converter-input voltage is:

```text
Vconverter = Vsource - Iinput × Rseries
```

The same current passes through every series element, so their resistances and
voltage drops add. The power lost as heat in that path is:

```text
Ploss = Iinput² × Rseries
```

This square law is why a path that looks acceptable at 300 mA can become hot
or lose too much voltage near 1 A.

## Power, energy, and converter input current

For a regulated rail:

```text
Pout = Vout × Iout
efficiency η = Pout / Pin
Pin = Pout / η
Iinput = Pout / (η × Vconverter)
```

As cell voltage falls, input current generally rises for the same output
power. Efficiency also changes with voltage, current, mode, layout, and
temperature, so one efficiency number is an **ASSUMED** input unless the
applicable guaranteed specification says otherwise.

Battery capacity in amp-hours is charge, not energy. A nominal energy estimate
is `Wh ≈ nominal V × Ah`. Nitecore lists the NL169 as `3.6 V`, `950 mAh`, and
`3.42 Wh`; that agreement is a useful unit check, not a runtime guarantee.

### Worked estimate: average versus peak

Suppose the Pocket Assistant's branches average `590 mA` from `3.3 V` during a
demanding operating interval:

```text
Pout = 3.3 V × 0.590 A ≈ 1.95 W
```

If efficiency is **ASSUMED** to be 85% and converter input is 2.7 V:

```text
Iinput ≈ 1.95 W / (0.85 × 2.7 V) ≈ 0.85 A
```

If a coincident transient instead reaches `778 mA`, its output-power envelope
is about `2.57 W`, and the same assumptions give roughly `1.12 A` input. Do not
use that short crest as a steady thermal current, and do not use the average
current to approve a transient. Record both duration and repetition rate.

The calculation is also recursive: current creates path drop, path drop lowers
converter input voltage, and lower input voltage raises current. Iterate the
calculation or solve it as a system, then verify the waveform at the module
pins.

## A buck-boost is necessary, but its name is not enough

A one-cell Li-ion source can be above and below a 3.3 V rail during discharge.
A four-switch buck-boost can step down when input is high and step up when it
is low. A boost-only module cannot safely regulate a fresh cell down to 3.3 V,
and a buck-only regulator cannot maintain 3.3 V after its input loses the
required headroom.

Five limits must remain separate:

1. **Absolute maximum:** damage may occur beyond it; it is not an operating
   target.
2. **Recommended operating range:** conditions under which functions are
   specified.
3. **Cold-start voltage:** input needed to begin from an unpowered output.
4. **Operating/UVLO voltage:** input at which an already-running converter can
   continue.
5. **Available output current:** a function of input voltage, output voltage,
   temperature, inductor, layout, and protection settings.

The TI TPS63070 illustrates the distinction. Its IC can operate down to 2.0 V
once running, but its datasheet requires 3.0 V for startup while the output is
below 3.0 V. A 3.3 V module based on that IC therefore has no useful cold-start
margin from a 3.0 V source before series loss. A marketplace claim of “2 V
startup” does not override the IC datasheet.

The TI TPS63802 has different limits, including a lower startup threshold.
That does not guarantee the performance of an unidentified module built around
it: its inductor, capacitors, copper area, settings, assembly, and thermal path
still matter.

## Source impedance is more than a resistor

Cell, holder, contacts, wiring, fuse, MOSFETs, and connectors all contribute
voltage drop. Some contributions are strongly nonlinear:

- cell impedance changes with state of charge, age, temperature, and pulse
  duration;
- a PPTC heats from current and its resistance rises sharply toward trip;
- MOSFET resistance depends on gate-to-source voltage and junction temperature;
- contacts change with force, contamination, crimp quality, and wear; and
- breadboard contacts and thin jumper leads are poor fixtures for ampere-scale
  qualification.

A normal two-wire DMM cannot accurately resolve a few tens of milliohms. Force
a known load current and measure the voltage drop at the exact endpoints:

```text
Rpath ≈ (Vno-load - Vloaded) / (Iloaded - Ino-load)
```

Prefer four-wire/Kelvin sensing when available. Include both positive and
return conductors if the measurement spans the complete loop.

### PPTCs do not behave like ideal fuses

A polymer resettable fuse is a temperature-dependent resistor. `Ihold` means
the current it is specified to carry under stated ambient conditions; `Itrip`
is not an instantaneous precision threshold. Trip time depends on current,
ambient temperature, mounting, prior heating, and airflow.

Parallel PPTCs do not simply double their ratings. Small resistance and thermal
differences cause unequal current sharing. Eaton recommends derating and gives
roughly 1.6–1.8 times a single device's rating as a rule of thumb for carefully
matched, co-located parts—not 2 times. The project must not teach the two
RUEF110 parts as an exact `2 × Ihold` fuse.

### MOSFET names are not interchangeable specifications

Use maximum on-resistance at the actual available gate voltage, not a headline
current rating or a typical value at 10 V gate drive. At `VGS = -2.5 V`, the
AO3401A datasheet permits up to `85 mΩ`; the DMG2301L permits up to `150 mΩ`.
At `1.15 A`, two such series devices could drop approximately:

```text
AO3401A pair: 1.15 A × 0.170 Ω ≈ 0.20 V
DMG2301L pair: 1.15 A × 0.300 Ω ≈ 0.35 V
```

Those are **CALCULATED** worst-case room-temperature values before hot
resistance is considered. A reverse-polarity circuit also depends on MOSFET
orientation, body diode, gate limits, and all possible source connections.
Require a reviewed schematic; a part number alone is not a protection design.

## Decoupling is local energy plus a low-impedance loop

A load transient can change faster than the converter control loop and wiring
can respond. A nearby capacitor supplies or absorbs some of that current:

```text
I = C × ΔV/Δt        so        ΔV = I × Δt/C
```

For example, an ideal `100 µF` capacitor supplying an extra `0.4 A` for
`100 µs` would change by:

```text
ΔV = 0.4 A × 100 µs / 100 µF = 0.4 V
```

Real droop also includes capacitor ESR, ESL, traces, and connections. This
example shows why a bulk capacitor cannot repair a fundamentally undersized
converter or high-resistance power path.

Use different capacitors for different time scales:

- small ceramic capacitors close the fastest, smallest current loops;
- larger ceramic or bulk capacitors support slower load changes; and
- the converter and source must supply sustained energy.

Capacitance printed on a ceramic is measured under stated conditions. Effective
capacitance can fall with DC bias, temperature, tolerance, and aging—especially
with high-K dielectrics. Electrolytic capacitors add useful bulk energy but do
not replace the close ceramic bypass required by fast switching loads. Follow
the exact IC/module datasheet for value, dielectric, ESR, voltage rating, and
placement. A generic assortment is not a traceable power-integrity design.

## UVLO is normal shutdown, not emergency protection

Undervoltage lockout prevents operation when the source can no longer support
the load safely or predictably. It must have hysteresis so startup current does
not make the system chatter on and off:

```text
turn off below Voff
remain off until source recovers above Von
where Von > Voff
```

The thresholds must be chosen from the exact cell, load, converter, temperature
range, and required margin. An IC's lowest operating voltage may be below the
cell system's desired cutoff. Firmware can estimate state of charge and request
shutdown, but firmware alone cannot disconnect a wedged or unpowered system.

A protected cell's internal PCB is a last-resort fault layer. It is not the
normal low-battery control and its exact thresholds and timing must be sourced
from the cell manufacturer. Nitecore's public NL169 page gives capacity,
energy, dimensions, and 2 A maximum continuous discharge, but not the internal
resistance or protection thresholds/timing assumed in the old project lesson.

## Protection layers have separate jobs

| Layer | Intended job | It does not prove |
| --- | --- | --- |
| External approved charger | Controlled Li-ion charging | Safe discharge wiring or system UVLO |
| Cell protection PCB | Last-resort overcharge, overdischarge, and fault interruption | Normal shutdown or a known system trip curve without data |
| Fuse/PPTC | Limit a selected upstream fault envelope | Precise instantaneous trip or perfect parallel sharing |
| Reverse-polarity circuit | Block a reversed source when correctly designed | Protection from every USB/backfeed condition |
| Converter limits | Protect the converter under stated conditions | Safety of wiring upstream of it |
| System UVLO/disconnect | End normal discharge and prevent restart chatter | Safe charging |

Charge the final cell only in the exact external charger qualified for that
cell. Never improvise a charger from the 3.3 V converter or breadboard.

## USB, service power, and a real off state

Two regulators connected to one rail may force current backward through a path
that neither manufacturer specifies. Before USB and the battery system can
coexist, draw every path through the USB connector, board regulator, `3V3`
pin, converter, peripherals, protection diodes, and grounds.

A removable jumper isolates only the conductor it actually opens. USB may
still energize peripherals through the controller's regulator, and an unknown
clone regulator may not be rated for that load. During foundations labs, use a
bare controller on USB or a fully isolated power subsystem—not the complete
harness.

A MOSFET load switch gives low-loss electronic control, but it is not always a
hard disconnect: body diodes, leakage, gate faults, and alternate sources can
leave paths energized. The final architecture must explicitly decide whether
the user switch is a control input or a physical battery disconnect and test
the intended off-state current and fault behavior.

## Thermal limits are system limits

Electrical losses heat the junction, package, PCB, nearby PPTC, cell, and
enclosure. A semiconductor's advertised current is meaningful only with its
specified copper area, airflow, ambient temperature, and allowable junction
temperature.

Useful first models are:

```text
MOSFET conduction loss ≈ Irms² × RDS(on, hot)
path loss ≈ Irms² × Rpath
temperature rise ≈ dissipated power × thermal resistance
```

Switching and quiescent losses must also be included for a converter. Case
temperature is not junction temperature, and touching a board is neither a
measurement nor a safe thermometer. Use a thermocouple or calibrated thermal
method, stabilize at the worst credible average mode, and keep the cell out of
early thermal tests.

## Current Pocket Assistant release status

The following are not yet durable facts and must not be copied into a purchase
freeze as guarantees:

- the XL63070 marketplace module's claimed 2.0 V cold start;
- a fixed current limit inferred from the TPS63802 IC for an unknown module;
- `0.12 Ω` NL169 internal resistance or unpublished protection timing;
- exact doubling of two parallel RUEF110 ratings;
- treating AO3401A and DMG2301L as equal 20–40 mΩ devices;
- the generic holder's fit and loaded contact resistance;
- capacitance or ferrite impedance inferred from generic kit names;
- a 3.0 V normal shutdown when no qualified battery sensing/UVLO exists; and
- safe USB powering of the complete peripheral rail through an unknown clone.

The battery-free Phase 0 path is therefore the only released learning path:
qualify one exact power chain from a current-limited supply, record its part
markings and serial/sample identity, and keep it disconnected from the MCU
until its output and faults are understood.

## Safe lab: characterize a buck-boost without a cell

Use a current-limited bench supply, DMM, scope if available, exact converter
sample, `100 Ω` resistor rated at least `0.25 W`, and later a `10 Ω` resistor
rated at least `2 W` or a suitable electronic load. Do not use a solderless
breadboard for the higher-current step. Do not connect the MCU, battery,
charger, or complete harness.

1. Photograph both module faces and record markings, dimensions, jumper state,
   and seller/lot.
2. With the supply output off, inspect polarity and check for an obvious input
   or output short.
3. Set `3.8 V` and a `100 mA` current limit. Verify lead polarity at the module
   end before connecting.
4. Power the module with no load. Stop for unexpected current limiting, output
   above the intended rail, heat, odor, or noise.
5. After confirming the output, attach `100 Ω`. Measure input voltage at the
   module pins, output voltage at the resistor, and input current.
6. Sweep source voltage from `4.2 V` toward `3.0 V` in small steps. At each
   step, turn power fully off and back on as well as testing continued
   operation. Startup and run behavior are separate columns.
7. If the exact module specifications, wiring, resistor rating, and supervision
   permit it, replace the load with `10 Ω`, raise the current limit only as
   calculated, and repeat. The resistor becomes hot; mount it clear of wires
   and do not touch it.
8. Add a known series resistor or the unpowered upstream protection chain to
   simulate source impedance. Measure source voltage and module-pin voltage
   under the same load; calculate path resistance from the loaded drop.
9. With a scope, observe output at the load during power-on and a load step.
   Record minimum voltage, overshoot, settling time, probe points, bandwidth,
   and current limit.
10. Turn power off, verify capacitors discharged, and save a table of every
    startup attempt. Ten starts on one sample at room temperature are
    **MEASURED sample evidence**, not a universal module guarantee.

## Common mistakes

- Dividing battery amp-hours by rail current despite the different voltages
  and converter loss.
- Using a peak current as continuous heating, or an average as a transient
  limit.
- Confusing “operates down to” with “cold-starts at.”
- Measuring milliohms directly in ordinary two-wire resistance mode.
- Assuming two parallel protection devices share current equally.
- Adding a large capacitor without checking converter stability, inrush, DC
  bias, ESR, voltage rating, and placement.
- Treating the protected cell PCB as the normal on/off controller.
- Testing an ampere-scale chain through thin Dupont leads or a breadboard.
- Connecting USB before proving every possible backfeed path.

## Check yourself

1. Why does converter input current tend to rise as a cell discharges while
   output power stays constant?
2. A converter runs after starting at 3.5 V, then continues down to 2.2 V. Has
   a 2.2 V cold-start capability been demonstrated?
3. What additional facts are needed before two parallel PPTCs can be modeled?
4. Why does `100 µF` near a load not fix an undersized converter indefinitely?
5. What is the difference between cell protection cutoff and system UVLO?

<details>
<summary>Answers</summary>

1. `Iinput = Pout/(ηVin)`; for similar output power and efficiency, lower input
   voltage requires more current.
2. No. Continued operation and startup are separate tests and specifications.
3. Exact part data, temperature derating, resistance matching/current sharing,
   mutual heating, trip-time behavior, mounting, and fault requirements.
4. Its stored energy is finite; voltage changes by `IΔt/C`, after which the
   source and converter must deliver the sustained power.
5. Cell protection is a last-resort internal fault layer. System UVLO is the
   deliberate, repeatable normal-discharge shutdown with chosen hysteresis.

</details>

## Primary sources for the project-specific statements

- [TI TPS63070 datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf)
- [TI TPS63802 datasheet](https://www.ti.com/lit/ds/symlink/tps63802.pdf)
- [Nitecore NL169 product page](https://www.nitecore.com/product/nl169)
- [Littelfuse RUEF radial PPTC datasheet](https://www.littelfuse.com/assetdocs/littelfuse-ptc-radial-leaded-ruef-datasheet?assetguid=2139d828-f887-4a2a-9b25-01ddf761ab3a)
- [Eaton resettable-PTC application guidelines](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/technical/eaton-ptc-resettable-fuse-application-guidelines.pdf)
- [AOS AO3401A datasheet](https://www.aosmd.com/sites/default/files/res/datasheets/AO3401A.pdf)
- [Diodes Incorporated DMG2301L datasheet](https://www.diodes.com/assets/Datasheets/DMG2301L.pdf)
- [Espressif ESP32-C3 schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html)

