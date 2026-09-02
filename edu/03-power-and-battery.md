# Power and battery — applying the power-integrity lesson

> **DESIGN-FREEZE STATUS: NO-GO.** No converter, protection chain, switch,
> holder, service-power circuit, UVLO, charger pairing, or cell-powered build
> is released. This note turns [Lesson 06](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md)
> into a battery-free qualification plan.

## The durable system problem

The controller, display, microphone, and amplifier need a controlled supply.
A one-cell Li-ion source varies with charge, load, temperature, age, and path
resistance. The design must accommodate the exact cell's documented range,
including the possibility that its voltage is above and below `3.3 V`.

That makes a true buck-boost topology a reasonable candidate. It does not make
any named module safe or adequate. A boost-only module cannot regulate a fresh
cell downward, while a buck-only regulator or LDO loses regulation when input
falls below the output plus required headroom.

Never power the product by relying on an unknown SuperMini `5V`-pin regulator
dropout. The exact clone's LDO, USB path, reverse-current behavior, and thermal
capacity are uncharacterized until traced and tested.

## Keep average, RMS, peak, and transient separate

The previous `778 mA` “verified budget” added unlike quantities: an ESP32-C3
rail-current condition and a speaker waveform crest. A BTL speaker's
`3.3 V / 8 Ω ≈ 412 mA` crest is not automatically `412 mA` of steady 3.3 V
rail current.

For an ideal full-scale sine into an `8 Ω` estimate:

```text
speaker power ≈ 3.3² / (2 × 8) ≈ 0.68 W
```

Using the MAX98357A's `92%` **TYPICAL** efficiency at its stated test point
only as an estimate:

```text
amplifier average input current ≈ 0.68 W / (0.92 × 3.3 V) ≈ 224 mA
```

Combining that estimate with a `335 mA` controller condition, `25 mA` display
estimate, and about `2 mA` for the microphone gives roughly `586 mA`, which can
be rounded to `590 mA` for a deliberately demanding coincident estimate. The
amplifier input estimate already includes its loss; adding quiescent current
again would double-count it. This is not a measured product average or a
guaranteed maximum. Wi-Fi and class-D switching create faster peaks that
require scope measurements at the load.

For every branch, keep four columns:

| Quantity | What it is used for |
| --- | --- |
| average current and duty cycle | energy/runtime estimate |
| RMS current | wire, connector, MOSFET, and thermal loss |
| peak current | device/current-limit stress |
| transient magnitude and duration | rail droop and decoupling |

Do not approve all four from one DMM number.

## Convert rail load into source current

The first-order equations are:

```text
Pout = Vout × Iout
Iinput = Pout / (efficiency × Vconverter-input)
Vconverter-input = Vsource - Iinput × Rseries
```

Input current rises as input voltage falls for similar output power. The last
two equations interact: current causes drop, and drop causes more current.
Iterate them using conservative **ASSUMED** inputs, then replace assumptions
with measured waveforms.

For example, `590 mA` at `3.3 V` is about `1.95 W`. At an assumed 85%
efficiency and `2.7 V` at the converter pins, input is approximately:

```text
1.95 W / (0.85 × 2.7 V) ≈ 0.85 A
```

This is a calculation example, not a selected fuse, switch, cell, or module
rating.

## Cold start is not continued operation

Record these separately for every converter candidate:

- minimum input to start with output initially at zero;
- input at which an already-running unit enters UVLO;
- load present during startup;
- input ramp rate and source impedance;
- output overshoot, minimum, and settling time; and
- temperature and module sample identity.

The distinction disqualifies a central old assumption. TI specifies the
TPS63070 IC for operation from `2.0 V` once started with `VOUT ≥ 3.0 V`, but
requires `3.0 V` input for startup while `VOUT < 3.0 V`. A 3.3 V TPS63070
candidate therefore has no cold-start margin from a 3.0 V source before
holder, protection, switch, and wiring loss. A module listing's “2 V startup”
claim does not override the [TI datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf).

The TPS63802 IC has different limits: TI lists input above `1.8 V` for startup
and 2 A output at `VIN ≥ 2.3 V`, `VOUT = 3.3 V`. Those are IC conditions, not a
guarantee for an unidentified marketplace module and its inductor, passives,
layout, assembly, settings, or temperature. See the
[TPS63802 datasheet](https://www.ti.com/lit/ds/symlink/tps63802.pdf).

## Measure the complete series path

The source path can include cell impedance, holder contacts, wiring, fuse or
PPTC, reverse-polarity device, on/off device, connectors, and both return and
positive conductors. Do not assign exact resistance to parts whose manufacturer
does not publish it.

A loaded-drop measurement is more useful than ordinary two-wire resistance
mode for milliohm-scale paths:

```text
Rpath ≈ ΔVpath / ΔI
```

Measure voltage at the exact endpoints while forcing a known safe current.
Record temperature, because cell, PPTC, MOSFET, contact, and wire behavior can
all change as they heat.

Nitecore publishes the NL169's `950 mAh`, `3.6 V / 3.42 Wh`, dimensions, and
2 A maximum continuous discharge. Its public page does not publish the
`0.12 Ω` internal resistance or protection thresholds/timing formerly used in
project arithmetic. Those are unknown, not design constants.

## A PPTC is nonlinear protection

`Ihold` and `Itrip` apply under named temperatures and time conditions. A PPTC
warms, its resistance rises, and its trip time changes with current, ambient,
mounting, and previous heating.

Two parallel RUEF110 parts do not exactly double hold or trip current. Eaton's
application guide says parallel parts should be identical and similarly
located, and gives about `1.6–1.8 ×` a single device as a rule of thumb—not
`2 ×`. The exact protection architecture must be chosen from normal steady
current, surge duration, maximum ambient, available fault current, required
trip time, residual tripped current, and upstream wiring capability.

Primary sources:
[Littelfuse RUEF datasheet](https://www.littelfuse.com/assetdocs/littelfuse-ptc-radial-leaded-ruef-datasheet?assetguid=2139d828-f887-4a2a-9b25-01ddf761ab3a) and
[Eaton PPTC application guide](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/technical/eaton-ptc-resettable-fuse-application-guidelines.pdf).

Do not deliberately short the cell or use it to characterize a fault. Fault
tests belong on a current-limited source whose available energy is known.

## Reverse polarity, switching, and hard disconnect

A Schottky diode is simple but costs forward voltage. A P-channel MOSFET can
reduce loss, but only with a reviewed topology: source/drain orientation, body
diode, gate-to-source limits, startup state, alternate power sources, and fault
paths all matter.

AO3401A and DMG2301L are not equivalent low-resistance placeholders. At
`VGS = -2.5 V`, their datasheets allow maximum on-resistance of `85 mΩ` and
`150 mΩ`, respectively. At `1.15 A`, two series devices could therefore drop
about `0.20 V` or `0.35 V` before hot-resistance margin. Select an exact part
and recalculate from its guaranteed conditions.

An electronic load switch is also not automatically a hard disconnect. Body
diodes, leakage, gate faults, and USB or signal backfeed can leave nodes
energized. The design must state whether “off” means:

- firmware sleep;
- converter disable;
- electronic load disconnect; or
- physical opening of the cell path.

Measure off-state current and voltage at every rail and define the safe service
procedure. Removing the cell remains the unambiguous disconnect during
unreleased construction.

## UVLO and cell protection have different jobs

A protected cell's internal PCB is a last-resort fault layer, not the normal
low-battery shutdown. The present design has no qualified battery measurement
or system UVLO, so “3.0 V empty” is not enforced.

A normal cutoff needs an exact threshold chosen from cell data, load sag,
temperature, and converter needs, plus hysteresis so the device does not chatter
on and off. Firmware may request shutdown, but a hardware path must handle a
wedged or unpowered controller if continued draw would be unsafe.

No cell-powered release can occur until normal undervoltage shutdown and
restart behavior are defined and tested.

## USB and service power must not backfeed

The SuperMini `3V3` node, onboard regulator, USB `VBUS`, external converter,
and peripherals can create multiple-source paths. A jumper only isolates the
one conductor it opens. It does not prove that USB can safely supply the full
peripheral rail through an unknown clone LDO.

For foundation work, flash and test the bare controller over USB. For the
candidate power system, use the current-limited bench supply with USB absent.
Before combining them, require a reviewed source-selection/isolation schematic
and measure every off/backfeed state.

## Decoupling and heat close the loop

Place required ceramic decoupling at each device's supply pins with a short
return loop, following the exact datasheet/reference layout. Bulk capacitance
supports slower transients but cannot repair an undersized converter or high
series resistance. Effective ceramic capacitance depends on dielectric, DC
bias, temperature, tolerance, case size, and aging.

Thermal checks use the worst credible **average/RMS** operating mode, not one
short crest. Measure converter, MOSFET, PPTC, holder/contact, wire, and nearby
air temperatures after stabilization. Case temperature is not junction
temperature; use datasheet thermal information and margin.

## External charging only, after an exact pairing review

No charging circuit belongs in the provisional frame. If the design later uses
the NL169, qualify one exact external charger variant against the exact cell's
manufacturer information: supported size/chemistry, termination voltage,
charge-current selection, polarity, fault handling, and instructions.

“XTAR/Nitecore class” is not an electrical specification, and features cannot
be transferred between similarly named charger revisions. Until the pairing is
documented, do not charge a project cell as part of this course.

## Battery-free Phase 0 gate

Use the detailed lab in Lesson 06. The minimum release evidence is:

1. one reviewed candidate schematic including positive and return paths, USB,
   disconnect, protection, sensing/UVLO, and capacitor values;
2. exact received module/part identities and photographs;
3. correct no-load output before any MCU connection;
4. input sweep and repeated cold starts at the intended load and worst
   simulated source impedance;
5. average-load efficiency plus oscilloscope load-step droop/overshoot;
6. measured voltage drop across each upstream section;
7. stabilized thermal results at maximum credible average load;
8. verified off, reverse-polarity, and service-isolation behavior using the
   current-limited source; and
9. predeclared pass/fail limits with margin across more than one sample.

Ten successful room-temperature starts on one board are useful **MEASURED**
sample evidence, not a module specification. The power architecture remains
**NO-GO** until all gates close without relying on a lithium cell for testing.

## Safety rules

1. Never solder to, dent, pierce, deliberately short, or heat a Li-ion cell.
2. Keep all cells away from soldering, painting, cutting, cleaning, flashing,
   and first-power work.
3. Never place a current-mode meter across a source.
4. Stop for unexpected current limiting, rail overshoot, resets, heat, odor,
   swelling, smoke, or noise.
5. Decorative paint and the brass frame are not electrical insulation.
6. A successful boot is not power-integrity, protection, or thermal approval.
