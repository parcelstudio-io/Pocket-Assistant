# Equation sheet

Use SI units unless stated otherwise. Keep units through every calculation and
label each input **DATASHEET**, **TYPICAL**, **ASSUMED**, or **MEASURED**. A
correct equation cannot rescue an unsuitable input or hidden condition.

## Prefix conversions

```text
1 kΩ  = 1,000 Ω
1 mA  = 0.001 A
1 µF  = 0.000001 F
1 MHz = 1,000,000 Hz
```

## Charge, current, and time

```text
I = Q / t                 Q = I t
```

- `I`: current in amperes (`A`)
- `Q`: charge in coulombs (`C`)
- `t`: time in seconds (`s`)

Battery charge capacity:

```text
capacity (Ah) = current (A) × time (h)
```

This does not by itself predict runtime; voltage, converter efficiency, load
profile, cutoff, temperature, age, and cell behavior matter.

## Ohm's law

For a resistor or approximately ohmic operating point:

```text
V = I R          I = V / R          R = V / I
```

- `V`: volts (`V`)
- `I`: amperes (`A`)
- `R`: ohms (`Ω`)

Do not apply one constant resistance to a diode, speaker across frequency,
switching converter, or battery over all operating conditions.

## Series and parallel resistance

```text
Rseries = R1 + R2 + ...

1/Rparallel = 1/R1 + 1/R2 + ...

two resistors: Rparallel = (R1 R2) / (R1 + R2)
```

The parallel formula assumes ideal resistors. Parallel fuses, batteries, or
active devices can share unevenly because resistance and temperature interact.

## Kirchhoff's laws

At a node:

```text
sum of current entering = sum of current leaving
```

Around a closed loop:

```text
algebraic sum of voltage rises and drops = 0
```

Choose current directions and voltage polarities; a negative answer means the
actual direction is opposite the chosen reference.

## Voltage divider

For two series resistors with no significant load on the midpoint:

```text
Vout = Vin × Rbottom / (Rtop + Rbottom)
```

A load `RL` from the output to ground appears in parallel with `Rbottom`. Use
`Rbottom || RL` in the equation. A divider is usually a poor power supply.

## Power and energy

```text
P = V I
P = I² R                 (resistor)
P = V² / R               (resistor)
E = P t                  (constant power)
1 Wh = 3600 J
```

For nominal battery energy:

```text
energy (Wh) ≈ nominal voltage (V) × rated capacity (Ah)
```

Example using the published NL169 headline ratings:

```text
3.6 V × 0.95 Ah = 3.42 Wh
```

This matches a nominal rating, not guaranteed delivered energy in the pager.

## Source and path voltage sag

Simple first-order model:

```text
Vloaded = Vopen - I Rpath
Vdrop   = I Rpath
Ploss   = I² Rpath
```

Real cells are not fixed resistors; state of charge, temperature, pulse length,
age, and electrochemistry affect the result.

## Converter efficiency and current

```text
η = Pout / Pin
Pout = Vout Iout
Iin ≈ Vout Iout / (η Vin)
```

Example with explicitly assumed efficiency:

```text
Vout = 3.3 V
Iout = 0.80 A
Vin  = 3.0 V
η    = 0.85 (ASSUMED)

Iin ≈ (3.3 × 0.80) / (0.85 × 3.0) ≈ 1.04 A
```

Use separately specified startup limits; an operating minimum after startup is
not necessarily the voltage from which a converter can cold-start.

Approximate LDO loss:

```text
Ploss ≈ (Vin - Vout) Iout + Vin Iq
```

## Capacitors and RC behavior

```text
Q = C V
Ecapacitor = 1/2 C V²
i = C × rate of voltage change
τ = R C
```

For an ideal capacitor charging through a resistor from 0 to a DC step:

```text
Vc(t) = Vs × (1 - e^(-t/RC))
```

Useful landmarks:

| Time | Approximate final voltage reached |
| --- | --- |
| `1τ` | 63% |
| `2τ` | 86% |
| `3τ` | 95% |
| `5τ` | 99% |

Real capacitors have tolerance, ESR, ESL, leakage, and voltage/temperature
dependence. Ceramic capacitance can fall under DC bias.

## Inductors

```text
voltage = L × rate of current change
Einductor = 1/2 L I²
```

An inductor's current cannot change instantaneously in the ideal model. Real
inductors have winding resistance, parasitic capacitance, current saturation,
core loss, and thermal limits.

For ideal components in sinusoidal steady state:

```text
capacitive reactance magnitude: Xc = 1 / (2πfC)
inductive reactance magnitude:  Xl = 2πfL
```

Both are in ohms. Impedance also includes phase and resistance; real ESR, ESL,
loss, saturation, and self-resonance limit these ideal formulas.

## I2C pull-up current and rise time

When one device pulls the line low:

```text
Ilow ≈ Vpullup / Rp
```

For a first-order RC bus, measured between the I2C-defined thresholds:

```text
tr ≈ 0.8473 Rp Cb
```

- `Rp`: equivalent pull-up resistance
- `Cb`: total bus capacitance

Example:

```text
Vpullup = 3.3 V
Rp = 4.7 kΩ
Ilow ≈ 0.70 mA
```

If two boards each have `4.7 kΩ` pull-ups, their equivalent is about `2.35 kΩ`.
Use the I2C specification and device sink-current/threshold limits to choose a
valid range; do not choose solely from this approximation.

## Timing, frequency, and I2S

```text
T = 1/f
Nyquist frequency = sample rate / 2
BCLK = sample rate × slots per frame × bits per slot
```

Current corrected-source contract:

```text
16,000 frames/s × 2 slots/frame × 32 bits/slot
= 1,024,000 bits/s = 1.024 MHz BCLK
```

The usable audio band must stay below the ideal Nyquist limit and depends on
the real converters and anti-alias/reconstruction filters.

## Sine-wave RMS and idealized speaker power

For a sine wave:

```text
Vrms = Vpeak / √2 = Vpp / (2√2)
Irms = Ipeak / √2
Paverage = Vrms² / R       (pure resistor)
```

An ideal BTL output whose two terminals can swing nearly rail-to-rail relative
to one another has an ideal upper-bound calculation. Real amplifiers have
output limits, distortion, protection, efficiency, and a speaker whose
impedance changes with frequency. Treat the result as **CALCULATED idealized**,
not guaranteed acoustic output.

## Decibels

```text
power ratio in dB = 10 log10(P2/P1)
same-impedance voltage or pressure ratio = 20 log10(A2/A1)
dBm = 10 log10(P / 1 mW)
```

- twice the power is about `+3.01 dB`;
- half the power is about `-3.01 dB`;
- twice the voltage/pressure ratio is about `+6.02 dB`;
- free-field pressure approximately falls `6 dB` per distance doubling under
  ideal far-field conditions.

## Radio wavelength

```text
λ = v / f
```

Using free-space speed `v ≈ 3.00 × 10^8 m/s` at `2.40 GHz`:

```text
λ ≈ 0.125 m = 12.5 cm
```

This does not produce a reliable “forbidden frame length.” Real antennas and
nearby conductors depend on geometry, dielectric material, orientation,
coupling, and feed/ground structure; follow layout guidance and measure.

## Tolerance and worst-case clearance

```text
minimum clearance
  = smallest permitted opening
  - largest permitted installed envelope
```

Include the plug, cable bend, solder, insulation, mounts, tool/finger access,
assembly path, and manufacturing variation—not only the component body.
