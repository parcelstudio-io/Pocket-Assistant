# 01 — Charge, voltage, current, power, energy, and heat

## Learning objectives

After this lesson, you should be able to:

- explain charge, voltage, current, resistance, power, and energy without using
  the words as synonyms;
- attach the correct SI unit to each quantity and convert common prefixes;
- calculate electrical power and energy from voltage, current, and time;
- distinguish an instantaneous current peak from average energy use;
- explain why electrical loss can become heat without treating temperature as
  another name for power; and
- make a safe, battery-free voltage and resistor-power measurement.

## One circuit, six different questions

Imagine a small amount of charge moving through a wire and a component. We can
ask six different questions about it:

| Question | Quantity | Symbol | SI unit |
| --- | --- | ---: | --- |
| How much electric charge is present or moved? | charge | `Q` | coulomb (`C`) |
| How much energy is available per unit charge between two points? | voltage | `V` | volt (`V`) |
| How quickly is charge passing a point? | current | `I` | ampere (`A`) |
| How strongly does an element oppose current at this operating point? | resistance | `R` | ohm (`Ω`) |
| How quickly is electrical energy being transferred now? | power | `P` | watt (`W`) |
| How much energy has been transferred over time? | energy | `E` | joule (`J`) |

These quantities are related, but they are not interchangeable.

### Charge

Matter contains positive and negative electric charge. In metal wires, the
mobile charge carriers are electrons. Circuit diagrams normally use
**conventional current**, defined as the direction positive charge would move.
That direction is opposite the average electron motion in a metal. The
convention is old, but the equations work consistently when you follow it.

One coulomb is a large number of elementary charges. You usually do not count
individual electrons; you measure how fast charge moves:

```text
I = ΔQ / Δt
```

One ampere means one coulomb passes a point each second:

```text
1 A = 1 C/s
```

Current needs a complete path. If a switch opens the only path, steady DC
current stops even if voltage remains across the open switch.

### Voltage

Voltage is always a difference between two points. It describes electric
potential energy per unit charge:

```text
V = ΔE / Q
1 V = 1 J/C
```

A label such as `3.3 V` is incomplete unless the reference point is understood.
In a simple circuit it usually means 3.3 V relative to the node called ground.
Ground is a chosen reference and return network, not a hole into which charge
disappears.

### Current

Current is a rate, not a substance stored inside a load. A source establishes
voltage; the connected circuit and its operating state determine current. A
bench supply rated for 5 A does not force 5 A through a 1 kΩ resistor. Its
rating says what it can supply before reaching a limit.

It is useful to say that a component **draws current**, but be careful with the
phrase “uses up current.” Charge continues around a closed circuit. The load
transforms electrical energy into light, motion, radio waves, sound, stored
energy, or heat.

### Resistance

For an ideal resistor at a fixed temperature, voltage, current, and resistance
obey Ohm's law:

```text
V = I R        I = V / R        R = V / I
```

Not every component is an ideal resistor. Diodes, transistors, regulators,
speakers, and digital boards can have nonlinear or time-varying behavior. Ohm's
law still describes an actual resistor, and `V/I` can describe an operating
point, but do not assume every load has one constant resistance.

### Power

Electrical power is the rate of energy transfer:

```text
P = V I
1 W = 1 J/s
```

For an ideal resistor, substituting Ohm's law gives two additional forms:

```text
P = I² R        P = V² / R
```

Use those two forms only when the voltage and current refer to the same
resistive element. For a converter or an amplifier, input power and output power
are different and loss must be considered.

### Energy

Energy accumulates over time. If power is constant:

```text
E = P t
```

The SI unit is the joule. Battery and electricity discussions also use the
watt-hour:

```text
1 Wh = 3,600 J
```

An ampere-hour is charge, not energy:

```text
1 Ah = 3,600 C
```

Multiplying ampere-hours by an applicable voltage gives watt-hours. A cell's
voltage changes with state of charge, load, temperature, and age, so
`nominal voltage × Ah` is an energy estimate, not a guaranteed runtime.

## Prefixes and unit discipline

Small electronics use prefixes constantly:

| Prefix | Symbol | Multiplier | Example |
| --- | ---: | ---: | --- |
| pico | `p` | `10⁻¹²` | 100 pF |
| nano | `n` | `10⁻⁹` | 100 nF |
| micro | `µ` or `u` | `10⁻⁶` | 10 µF, 250 µA |
| milli | `m` | `10⁻³` | 330 mA, 5 mW |
| kilo | `k` | `10³` | 10 kΩ |
| mega | `M` | `10⁶` | 1 MΩ |

Capitalization matters: `m` means milli while `M` means mega, a factor of one
billion apart. Include units in every calculation and convert them before
combining values:

```text
330 mA = 0.330 A
10 kΩ = 10,000 Ω
100 nF = 0.000000100 F = 0.1 µF
```

A useful engineering habit is to estimate the order of magnitude first. If a
calculator says a tiny display dissipates 800 W, a prefix or unit is wrong.

## Heat and temperature are related, not identical

Power lost in resistance becomes thermal energy. If a regulator takes 2.0 W
in and delivers 1.7 W out, its loss is:

```text
P_loss = P_in - P_out = 0.3 W
```

That is a heating rate. It is not a temperature. Temperature rise also depends
on the component package, copper area, airflow, nearby heat sources, ambient
temperature, and time. A simplified steady-state estimate is:

```text
ΔT ≈ P_loss × θ
```

where `θ` is an applicable thermal resistance in degrees Celsius per watt.
Datasheet thermal numbers are measured under specified test conditions; a tiny
marketplace board inside a guard may behave very differently. The final answer
comes from a conservative calculation followed by measurement in the real
geometry.

Also distinguish these two limits:

- **average power** predicts energy use and long-term heating;
- **peak current or power** can cause voltage sag, resets, clipping, or current
  limiting even when the average is modest.

The Pocket Assistant has radio and audio loads that change quickly, so both
questions matter.

## Worked example — an illustrative Pocket Assistant power state

The following numbers teach the method. They are **ASSUMED**, not a frozen BOM
or a measured device specification.

Suppose a prototype's regulated rail is 3.3 V and its average current during a
voice exchange is 250 mA.

1. Convert current: `250 mA = 0.250 A`.
2. Calculate rail power:

   ```text
   P_out = 3.3 V × 0.250 A = 0.825 W
   ```

3. If that state lasts 20 minutes, then `t = 1/3 h`:

   ```text
   E_out = 0.825 W × 1/3 h = 0.275 Wh
         = 0.275 × 3,600 J = 990 J
   ```

4. Suppose converter efficiency is **ASSUMED** to be 85% at that operating
   point:

   ```text
   efficiency = P_out / P_in
   P_in = 0.825 W / 0.85 = 0.971 W
   P_loss = 0.971 W - 0.825 W = 0.146 W
   ```

5. At an **ASSUMED** 3.6 V converter input, average input current would be:

   ```text
   I_in = 0.971 W / 3.6 V = 0.270 A
   ```

The result is **CALCULATED** from assumptions. It does not prove converter
efficiency, cell runtime, temperature, or peak-current margin. Those become
**MEASURED** only after the exact hardware is tested under recorded conditions.

> **Durable principle:** energy in must cover useful energy out plus loss.
>
> **Project status:** exact rail currents, duty cycles, converter efficiency,
> and thermal behavior remain qualification measurements. Do not size or buy a
> final power chain from this illustrative example.

## Battery-free lab — voltage, current, and resistor power

### Equipment

- current-limited bench supply;
- digital multimeter with intact leads and fuse;
- solderless breadboard and jumpers;
- one 1 kΩ, 0.25 W resistor; and
- eye protection.

No lithium cell is used.

### Procedure

1. Turn the supply output off. Set it to 3.3 V and a 20 mA current limit.
2. With the circuit unpowered, measure the resistor. A tolerance-marked 1 kΩ
   part will not necessarily read exactly 1,000 Ω. Record the **MEASURED** value.
3. Connect the resistor from supply positive to supply ground. Inspect for
   accidental shorts.
4. Predict current using the measured resistance. For exactly 1 kΩ:

   ```text
   I = 3.3 V / 1,000 Ω = 0.0033 A = 3.3 mA
   ```

5. Turn on the output. Measure voltage **across** the resistor. It should be
   close to the supply voltage.
6. Infer current from measured voltage and resistance. Calculate resistor
   power. For the ideal values:

   ```text
   P = 3.3 V × 3.3 mA = 10.9 mW
   ```

   This is far below a 0.25 W resistor rating.
7. Turn the output off before moving wires. Confirm the reading returns toward
   0 V.

Optional: after reviewing the meter manual and Lesson 00, move the red lead to
the correct fused current jack and insert the meter **in series** to compare the
measured current. Return the lead to the voltage jack immediately afterward.
Never place a current-mode meter across the supply.

## Common mistakes

- **Confusing mA and mAh.** Milliamperes are current; milliampere-hours are
  charge capacity.
- **Calling voltage “the current.”** Voltage is a difference between points;
  current is charge per time through a path.
- **Assuming a source forces its current rating.** The circuit draws current;
  the rating is a capability or limit.
- **Using average current to check a transient limit.** A radio burst may reset
  a rail even when the average current looks comfortable.
- **Treating watts and watt-hours as interchangeable.** Watts are a rate;
  watt-hours are accumulated energy.
- **Assuming all electrical power becomes heat in one part.** Some becomes
  sound, light, RF, or stored energy; loss locations must be identified.
- **Predicting temperature from watts alone.** Thermal path and ambient
  conditions are essential.
- **Dropping prefixes or units in calculator work.** `250 mA` entered as `250 A`
  creates a thousandfold error.

## Check yourself

1. What does 500 mA mean in amperes and coulombs per second?
2. A 3.3 V load draws 40 mA for 10 s. What are its power and energy?
3. Is a 1,000 mAh rating a statement of current, charge, power, or energy?
4. A converter delivers 1.5 W and loses 0.2 W. What input power does it take?
5. Why can two boards dissipating the same 0.3 W reach different temperatures?

<details>
<summary>Answers</summary>

1. `500 mA = 0.500 A = 0.500 C/s`.
2. `P = 3.3 V × 0.040 A = 0.132 W`; `E = 0.132 W × 10 s = 1.32 J`.
3. Charge capacity. It becomes an approximate energy only when combined with an
   applicable voltage.
4. `P_in = P_out + P_loss = 1.5 W + 0.2 W = 1.7 W`.
5. Their packages, copper, airflow, mounting, ambient temperature, and thermal
   contact can differ. Power loss alone does not determine temperature.

</details>

## Authoritative further reading

- [BIPM, *The International System of Units (SI)*](https://www.bipm.org/en/publications/si-brochure)
- [NIST guide to SI units and prefixes](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-4-two-classes-si-units-and-si-prefixes)
- [OpenStax University Physics, electric current and resistance](https://openstax.org/books/university-physics-volume-2/pages/9-introduction)
- [OpenStax University Physics, electrical energy and power](https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power)

Next: [DC circuits, Ohm's law, and Kirchhoff's laws](02-dc-circuits-ohm-kirchhoff-series-parallel.md).
