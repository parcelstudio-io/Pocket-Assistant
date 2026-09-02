# 03 — Components: R, C, L, diodes, MOSFETs, and converters

## Learning objectives

After this lesson, you should be able to:

- describe what resistors, capacitors, and inductors do in DC and changing
  conditions;
- calculate an RC time constant and recognize the limits of that model;
- explain diode polarity without assuming one universal forward-voltage drop;
- use gate-to-source voltage, rather than gate-to-ground voltage, when
  reasoning about a MOSFET;
- distinguish threshold voltage from a guaranteed low on-resistance;
- distinguish linear, buck, boost, and buck-boost regulation;
- estimate converter input current from output power and efficiency; and
- perform a slow, visible RC experiment from a current-limited supply.

## Components are physical, not perfect symbols

A schematic symbol describes the intended electrical role. A real part adds
tolerance, resistance, capacitance, inductance, leakage, temperature effects,
voltage and current limits, and a physical package.

An ideal model is still valuable when you state where it applies. Start simple,
calculate, then add the non-ideal behavior that can change the decision.

## Resistors

A resistor relates voltage and current approximately by Ohm's law:

```text
V = I R
```

Common jobs include:

- limiting LED, gate, or fault current;
- pulling a digital signal toward a defined state;
- dividing voltage for sensing;
- setting an amplifier, regulator, or timing parameter; and
- converting current to a measurable voltage.

Important real specifications include:

- nominal resistance and tolerance;
- power rating and its temperature derating;
- maximum working voltage;
- temperature coefficient; and
- package or lead spacing.

A 100 kΩ resistor and a 100 Ω resistor may look alike while differing by a
factor of one thousand. Measure uncertain parts unpowered and retain their
labels.

## Capacitors

A capacitor stores separated charge and electric-field energy. Its defining
relationships are:

```text
Q = C V
i = C × ΔV/Δt
E = 1/2 C V²
```

The second equation says capacitor current is related to how quickly voltage
changes. An ideal capacitor can draw current while charging, then carry no
steady DC current after its voltage stops changing. Real capacitors leak and
have series resistance and inductance.

Common jobs include:

- **decoupling:** supplying a nearby load during fast current changes;
- **bulk storage:** reducing slower rail movement;
- filtering noise;
- AC coupling between stages; and
- timing with a resistor.

### Capacitance is not the whole identity

Also check:

- voltage rating with margin;
- tolerance;
- dielectric or capacitor technology;
- effective capacitance under DC bias;
- equivalent series resistance (`ESR`) and inductance (`ESL`);
- leakage and polarity; and
- case dimensions and temperature rating.

Ceramic capacitors are usually unpolarized. Aluminum electrolytic and polymer
capacitors are normally polarized: reversing one can damage it. Never infer
polarity from a CAD cylinder alone.

### Decoupling is a current-loop problem

A decoupling capacitor should be close to the load's power and ground pins so
the fast current loop is short. Adding “10 µF somewhere on the rail” is not
electrically identical to placing it beside a radio or amplifier. Wires and PCB
traces add impedance at high frequency.

## RC time constants

A resistor and capacitor create a first-order time scale:

```text
τ = R C
```

`τ` is the Greek letter tau. Ohms times farads equals seconds.

For an initially discharged capacitor charging toward a constant source through
a resistor:

```text
V_C(t) = V_source × (1 - e^(-t/RC))
```

You do not need calculus to use the important landmarks:

| Time | Charging voltage | Discharging voltage remaining |
| ---: | ---: | ---: |
| `1τ` | 63.2% | 36.8% |
| `2τ` | 86.5% | 13.5% |
| `3τ` | 95.0% | 5.0% |
| `5τ` | 99.3% | 0.7% |

The curve is exponential, not a straight ramp. The model assumes an ideal
source, resistor, and capacitor and no important load. GPIO thresholds,
capacitor tolerance, leakage, switch bounce, and input protection can change a
real timing circuit.

## Inductors

An inductor stores magnetic-field energy:

```text
V = L × ΔI/Δt
E = 1/2 L I²
```

An ideal inductor resists an **instantaneous change in current**, not current
itself. In steady DC it behaves like a wire; a real inductor also has winding
resistance and a current-dependent magnetic core.

Inductors are central to switching converters because they accept energy during
one switch state and release it during another. Important specifications
include inductance, tolerance, DC resistance, saturation current, RMS current,
core loss, shielding, and package height.

If an inductor current path is opened abruptly, the inductor produces whatever
voltage its circuit allows in an attempt to keep current continuous. Converter
switches and clamp or freewheel paths are designed around that behavior.

## Diodes

A diode strongly favors current in one direction. For a conventional diode
symbol, conventional forward current flows from **anode** to **cathode**. The
cathode is marked by the symbol's bar and often by a stripe on the package.

A diode is not a perfect one-way valve:

- forward voltage varies with current, temperature, and device type;
- reverse current is small, not mathematically zero;
- reverse voltage has a limit;
- switching takes time; and
- capacitance can matter on fast signals.

“Every silicon diode drops 0.7 V” is only a rough teaching shortcut. A Schottky
diode may drop less, a power diode may drop more at high current, and all of
them need the applicable datasheet curve and limits.

Common uses include rectification, clamping, reverse-polarity arrangements,
freewheel paths for inductive loads, and steering signals or power. A series
diode's voltage loss can be unacceptable in a low-voltage system even when its
direction is correct.

## MOSFETs as controlled switches

A metal-oxide-semiconductor field-effect transistor has gate (`G`), drain
(`D`), and source (`S`) terminals. Power MOSFETs also contain an intrinsic body
diode that makes source/drain orientation important in protection circuits.

The gate is insulated. It takes little steady DC current, but it acts like a
capacitor and requires transient current to charge or discharge. A floating
gate can retain charge and turn on unpredictably, so a deliberate gate-to-source
pull resistor often defines the off state.

### Gate voltage is relative to the source

The controlling quantity is:

```text
V_GS = V_gate - V_source
```

- An enhancement-mode **N-channel** MOSFET turns on with sufficiently positive
  `V_GS` and is convenient as a low-side switch.
- An enhancement-mode **P-channel** MOSFET turns on with sufficiently negative
  `V_GS` and can be convenient in a positive high-side path.

Saying “the gate is at 3.3 V” is not enough. If the source is also at 3.3 V,
then `V_GS = 0 V`.

### Threshold does not mean fully on

Datasheet `V_GS(th)` is normally measured at a tiny drain current. It indicates
the beginning of channel conduction, not a low-resistance power switch. For a
load switch, find a guaranteed `R_DS(on)` at the gate voltage the circuit can
actually provide.

Approximate conduction loss while fully enhanced is:

```text
P_conduction = I² R_DS(on)
```

`R_DS(on)` rises with temperature. Also check drain-source voltage, drain
current under the stated thermal conditions, gate maximum, package dissipation,
body-diode direction, and safe operating area.

High-side switching and reverse-polarity protection require more than selecting
“a P-FET.” Pin orientation, body diode, gate bias during every power state, USB
back-power paths, and fault behavior must be reviewed as one schematic.

## Voltage regulation

Digital circuits need a rail within a defined range despite changing input and
load. Two broad regulator families are useful here.

### Linear regulators

A linear regulator controls a pass element and discards excess voltage as heat.
It is simple and can be quiet, but it normally cannot raise voltage.

Approximate loss is:

```text
P_loss ≈ (V_in - V_out) × I_out
```

An LDO is a linear regulator designed to work with a small input-output
difference, called dropout. “Low dropout” does not mean zero dropout, and it
still cannot regulate after input falls too low.

### Switching converters

A switching converter rapidly controls switches and uses inductors and
capacitors to transfer energy efficiently:

| Topology | Basic job |
| --- | --- |
| buck | produces a lower output than input |
| boost | produces a higher output than input |
| buck-boost / step-up-down | regulates when input may be above or below output |

The topology must match the entire input range, not only a nominal voltage. A
buck-only board cannot maintain 3.3 V after its input falls below the required
headroom. A boost-only board may not safely regulate when input begins above its
output. “Buck-boost” on a marketplace title is not proof of the circuit inside.

### Power and efficiency

Efficiency is:

```text
η = P_out / P_in
P_out = V_out I_out
P_in = V_in I_in
```

Therefore an estimate of input current is:

```text
I_in = V_out I_out / (η V_in)
```

Input current rises as input voltage falls for the same output power. That is
why an output-current headline cannot by itself size the cell, holder, fuse,
switch, wiring, or converter.

### Specifications that must not be blended together

- **recommended operating range:** where normal operation is specified;
- **absolute maximum:** a damage boundary, not an operating target;
- **startup voltage:** input needed to start from off;
- **minimum operating or UVLO voltage:** where a running unit stops or becomes
  unspecified;
- **switch current limit:** internal peak current, often not equal to usable
  output current;
- **thermal limit:** depends on board and airflow;
- **efficiency curve:** typical behavior at stated conditions; and
- **transient response/ripple:** rail movement as load changes.

A module adds its own inductor, capacitors, feedback setting, connectors, copper,
and layout. A regulator-IC datasheet cannot certify an unknown module assembled
around that IC.

## Worked example 1 — RC button filtering

Suppose a candidate button circuit uses 10 kΩ and 100 nF:

```text
τ = 10,000 Ω × 100 × 10⁻⁹ F
  = 0.001 s = 1 ms
```

After 1 ms, an ideal charging node has moved 63.2% toward its final voltage;
after 5 ms it is at 99.3%. That does not prove a 5 ms debounce time. Mechanical
bounce, GPIO thresholds, resistor/capacitor tolerance, whether the capacitor is
across the switch or input, and firmware debounce behavior all matter.

## Worked example 2 — converter input current

Use **ASSUMED** qualification numbers, not BOM promises:

```text
V_out = 3.3 V
I_out = 0.50 A
V_in  = 3.0 V
η     = 0.85
```

Then:

```text
P_out = 3.3 V × 0.50 A = 1.65 W
P_in  = 1.65 W / 0.85 = 1.94 W
I_in  = 1.94 W / 3.0 V = 0.647 A
P_loss = 1.94 W - 1.65 W = 0.29 W
```

At the same output load, lower input voltage means higher input current. The
0.29 W loss is a heating rate, not a predicted temperature.

> **Durable principles:** topology follows the complete input/output range;
> input power equals output power plus loss; and `V_GS` is measured gate to
> source.
>
> **Project status:** the Pocket Assistant's exact converter module, MOSFETs,
> capacitors, power carrier, startup behavior, efficiency, and thermal margin
> remain hardware-qualification decisions. This lesson does not authorize a
> final purchase.

## Battery-free lab — watch an RC curve

### Equipment

- current-limited bench supply;
- DMM in voltage mode;
- breadboard and jumpers;
- 100 kΩ resistor;
- 100 µF capacitor rated at least 6.3 V; and
- stopwatch and eye protection.

Use a known, correctly polarized capacitor. No lithium cell is used.

### Predict

```text
τ = 100 kΩ × 100 µF = 10 s
```

For a 3.3 V step, predict approximately:

| Time | Capacitor voltage |
| ---: | ---: |
| 0 s | 0 V |
| 10 s (`1τ`) | 2.09 V |
| 20 s (`2τ`) | 2.85 V |
| 30 s (`3τ`) | 3.14 V |
| 50 s (`5τ`) | 3.28 V |

### Measure

1. Turn the supply off. Set 3.3 V and a 10 mA current limit.
2. Connect supply positive through 100 kΩ to capacitor positive. Connect
   capacitor negative to supply ground.
3. Connect the voltmeter across the capacitor, positive to positive.
4. Inspect polarity and wiring. Turn on the output and start the stopwatch.
5. Record voltage at 10 s intervals through 60 s.
6. Turn the supply off. Discharge the capacitor **through the 100 kΩ resistor**;
   do not short it with a wire. Observe the falling voltage.

Compare the curve with the prediction rather than expecting exact points.
Capacitor tolerance and leakage, resistor tolerance, meter input resistance,
timing error, and residual starting charge are real effects. Label observed
values **MEASURED**.

## Common mistakes

- **Treating a charged capacitor as harmless because power is off.** Verify and
  discharge it through an appropriate resistor.
- **Reversing a polarized capacitor.** Check the package and datasheet marking.
- **Assuming capacitance printed on a ceramic remains unchanged under DC bias.**
  Effective capacitance may be much lower.
- **Saying an inductor “blocks DC.”** An ideal inductor becomes a short in steady
  DC; it opposes change in current.
- **Using one fixed diode drop in every calculation.** Forward drop depends on
  device, current, and temperature.
- **Using MOSFET threshold as the drive voltage for low resistance.** Use a
  guaranteed `R_DS(on)` condition.
- **Forgetting the MOSFET body diode or source reference.** Both affect high-side
  and reverse-current behavior.
- **Assuming a converter's switch-current rating is output current.** It is not.
- **Choosing buck or boost from nominal input alone.** Check both endpoints,
  startup, and faults.
- **Treating a chip datasheet as proof of an unknown module.** Module layout and
  parts determine important behavior.

## Check yourself

1. What is `τ` for 47 kΩ and 10 µF?
2. After one time constant, approximately what percentage of its final voltage
   has a charging capacitor reached?
3. Why does a capacitor near an IC usually decouple better than the same value
   at the end of long wires?
4. An N-channel MOSFET gate and source are both at 3.3 V. What is `V_GS`?
5. Why is `V_GS(th) = 1 V` not proof that a MOSFET is a low-resistance switch at
   1 V gate drive?
6. Which basic converter topology is required when input can be both above and
   below the desired output?
7. A converter delivers 1.0 W at 80% efficiency. What input power and loss does
   that imply?

<details>
<summary>Answers</summary>

1. `47,000 Ω × 10 × 10⁻⁶ F = 0.47 s`.
2. About 63.2%.
3. Shorter conductors reduce parasitic impedance and the area of the fast
   current loop.
4. `V_GS = 3.3 V - 3.3 V = 0 V`.
5. Threshold is specified at a small test current and marks the beginning of
   conduction. Low on-resistance needs a separate guarantee at the actual gate
   voltage.
6. A buck-boost, or another reviewed step-up/down topology.
7. `P_in = 1.0 W / 0.80 = 1.25 W`; loss is `0.25 W`.

</details>

## Authoritative further reading

- [OpenStax University Physics, RC circuits](https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits)
- [Texas Instruments, *Understanding Smart Gate Drive* (MOSFET theory and operation)](https://www.ti.com/lit/an/slva714d/slva714d.pdf)
- [Texas Instruments, *Avoid Common Mistakes When Selecting and Designing with Power MOSFETs*](https://www.ti.com/lit/an/slpa021/slpa021.pdf)
- [Analog Devices, applying step-up/step-down regulators](https://www.analog.com/en/resources/analog-dialogue/articles/dc-to-dc-step-up-step-down-regulators.html)
- [Analog Devices, switch-mode power-supply basics](https://www.analog.com/en/resources/technical-articles/2022/07/16/10/04/switch-mode-power-supply-basics.html)

Next: [boards, schematics, datasheets, and connectors](04-boards-schematics-datasheets-and-connectors.md).
