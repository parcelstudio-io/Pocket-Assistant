# 05 — Measurement: DMM, bench supply, scope, and logic analyzer

## Learning objectives

After this lesson, you should be able to:

- choose an instrument that can answer a specific electrical question;
- measure voltage, resistance, continuity, and current without creating a short;
- use constant-voltage and current-limit controls on a bench supply;
- explain what a DMM can miss during a fast transient;
- capture I2C or I2S with a logic analyzer; and
- record a measurement so another person can reproduce it.

## Measurement is a controlled experiment

A meter does not simply reveal “the truth.” It becomes part of the circuit and
answers one question over a limited range and bandwidth. Before touching a
probe, write the question:

- Is 3V3 present relative to circuit ground?
- Is this connection open or continuous while power is off?
- How much current enters the whole assembly at idle?
- Does SDA acknowledge address `0x3C`?
- Does the rail dip below the controller's minimum during an audio burst?

That wording determines the instrument, connection, range, and test condition.

## Digital multimeter: the four common jobs

### Voltage

A voltmeter measures the potential difference **between two nodes**. Connect
it in parallel with the circuit being observed:

```text
3V3 o──────── load ───────o GND
    │                     │
    └───────( V )─────────┘
```

Put the black lead in `COM`, the red lead in the voltage/resistance jack, and
select DC volts. For the pager, “3.3 V” is incomplete unless the reference is
named: normally `3V3 relative to circuit GND`.

A DMM input is usually high resistance, so it draws little current. It can
still give a plausible voltage on a weakly coupled or floating node. A voltage
reading alone does not prove that a supply can deliver load current.

### Resistance and continuity

Resistance and continuity modes inject their own small test stimulus. Use them
only on an **unpowered** circuit whose capacitors have discharged.

Continuity answers “is the measured resistance below this meter's beeper
threshold?” It does not prove:

- that a solder joint can carry the intended current;
- that two boards use the same connector pin order;
- that a 0.3-ohm path is acceptable; or
- that a diode or semiconductor is healthy.

First touch the probes together and note the lead resistance. Very low
resistances are better evaluated by forcing a known current and measuring the
voltage drop: `R = V / I`.

### Diode mode

Diode mode reports a forward voltage under a small test current. It is useful
for checking a diode's direction and finding obvious shorts through protection
devices. In-circuit parallel paths can alter the result, so compare both probe
directions and consult the schematic.

### Current

An ammeter becomes a low-resistance part of the branch, so it must go **in
series**:

```text
supply + o────( A )──── device VIN
supply - o──────────── device GND
```

Move the red lead to the correct fused current jack, select a range above the
expected current, open the circuit, and insert the meter. Never touch a
current-mode meter across a supply; that is nearly a short through the meter's
fuse. Return the lead to the voltage jack immediately afterward.

For time-varying loads, an inline current meter also adds a small voltage drop
called burden voltage. A supply readout plus a scope across a current shunt is
often more informative for fast peaks.

## The current-limited bench supply

A bench supply has two interacting controls:

- **CV, constant voltage:** the supply holds the set voltage while the load
  takes less than the current limit.
- **CC, constant current:** the load tries to take too much, so the supply
  lowers its output voltage to keep current at the limit.

CC is not automatically a fault—it is the promised protection behavior—but an
unexpected transition into CC is evidence to stop and investigate.

### Safe first-power sequence

1. Disconnect the circuit.
2. Set the target voltage.
3. Set a deliberately low current limit appropriate for the stage under test.
4. Turn the output off.
5. Verify polarity at the cable end with a DMM.
6. Connect ground first and then positive.
7. Turn the output on while watching both voltage and current.
8. Stop for unexpected CC operation, heat, odor, or noise.
9. Raise the limit only after the measured behavior explains why more is safe.

The exact starting limit depends on what is connected. It is not a universal
number. Power one subsystem at a time and use its documented consumption plus
margin.

## Oscilloscope: voltage versus time

A DMM may update only a few times per second. A rail can average 3.30 V while
briefly collapsing during Wi-Fi or speaker peaks. A scope can show those
events, clock edges, ripple, ringing, and startup order.

Three settings matter immediately:

- **vertical scale:** volts per division;
- **timebase:** seconds per division; and
- **trigger:** the event that stabilizes the display.

Use the probe's short ground spring for fast edges when possible. A long ground
lead adds inductance and can create ringing that is mostly the measurement
setup.

Many bench scopes connect the probe ground clip to protective earth. Clipping
it to a non-ground node can short that node to earth. Confirm the scope,
supply, and circuit references before connecting. This is especially important
around bridge-tied speaker outputs: neither output is ground.

Record probe attenuation (`1x` or `10x`), coupling, bandwidth limit, sample
rate, vertical scale, and where both probe leads were connected.

## Logic analyzer: digital timing and protocol

A logic analyzer classifies voltages as 0 or 1 and samples them over time. It
is ideal for questions such as:

- Was there an I2C START?
- Which 7-bit address was sent?
- Did the OLED ACK?
- Are I2S `BCLK` and `WS` present at the expected frequencies?
- Does a control pin change before or after reset?

Connect analyzer ground to circuit ground, verify that its inputs tolerate the
logic voltage, and sample comfortably faster than the fastest signal. Ten times
the bit clock is a useful starting point, not a mathematical guarantee. Set the
decoder's address convention, clock polarity, word length, and sample edge to
match the protocol and firmware.

A logic analyzer cannot show how much analog margin an edge has. If a decoder
fails intermittently, inspect the actual waveform with a scope.

## Instrument loading and bandwidth

Every instrument has limits:

| Instrument | It adds or assumes | Easy-to-miss problem |
| --- | --- | --- |
| DMM voltmeter | finite input resistance/capacitance | fast dips and noise |
| DMM ammeter | shunt resistance and fuse | burden voltage and fast peaks |
| Scope probe | resistance, capacitance, ground path | probe-induced ringing or short |
| Logic analyzer | threshold and input capacitance | marginal analog levels |
| Bench supply | cable resistance and control-loop response | voltage at supply differs from voltage at board |

Measure the rail at the load as well as at the supply. A cable or connector may
drop voltage under current even when the supply display looks perfect.

## Worked Pocket Assistant example

Suppose the supply display says 3.30 V and 420 mA during a loud tone, while a
DMM at the controller reads 3.21 V.

**MEASURED:** path drop `Vdrop = 3.30 V - 3.21 V = 0.09 V`.

**CALCULATED:** the total resistance of positive and return paths is roughly:

```text
Rpath = Vdrop / I = 0.09 V / 0.420 A ≈ 0.21 Ω
```

This value includes leads, contacts, switches, protection parts, solder joints,
and PCB traces. It does not identify the culprit. Measure smaller sections
under the same load to localize the drop. Then use a scope at the controller to
check whether short dips are worse than the DMM average.

## Safe lab: characterize a resistor load

Use a current-limited supply, DMM, a `1 kΩ` resistor rated at least `0.25 W`,
and jumper leads. No battery is required.

1. With power off, measure the resistor and label the result **MEASURED**.
2. Calculate expected current at `3.3 V`: `I = V/R`, about `3.3 mA` for exactly
   `1 kΩ`.
3. Set the supply to `3.3 V` with a `10 mA` limit; verify cable polarity.
4. Connect the resistor, turn on the output, and measure voltage across it.
5. Insert the DMM in series to measure current, then return its lead to the
   voltage jack.
6. Calculate `R = V/I` and compare with the unpowered resistance reading.
7. Set the current limit below the load current and observe CC mode. Explain
   why both voltage and current change.

Do not substitute an LED without a series resistor.

## A reproducible measurement record

Write down:

```text
question:
date/time and operator:
device/module identifier:
schematic revision and firmware commit:
instrument and relevant settings:
probe points and polarity:
supply voltage and current limit:
load, temperature, and operating mode:
result with units:
evidence label:
pass/fail rule decided before the test:
photo, trace, or log path:
```

“It worked” cannot be audited. A dated trace tied to an exact unit and test
condition can.

## Common mistakes

- Leaving the red lead in the current jack and later trying to measure voltage.
- Measuring resistance on a powered board.
- Calling circuit ground “zero everywhere”; current causes real drops along
  conductors.
- Using a DMM average to approve transient-sensitive power.
- Trusting an auto-decoder without checking protocol settings and waveforms.
- Moving a grounded scope clip between nodes while the circuit is powered.
- Reporting extra decimal places that the instrument cannot justify.

## Check yourself

1. Where is an ammeter placed, and why must it not be placed across a supply?
2. The supply shows `CC` and only `0.8 V` despite a `3.3 V` setting. What does
   that mean?
3. Why might a DMM show a healthy rail while the ESP32-C3 resets?
4. What must be recorded with an I2C logic-analyzer capture?

<details>
<summary>Answers</summary>

1. In series with the measured branch. Its low-resistance shunt would nearly
   short a source if connected across it.
2. The load is demanding more than the set limit, so the supply is lowering
   voltage to hold the limit. Turn off and explain the demand before proceeding.
3. The reset may be caused by a short voltage dip faster than the DMM's update
   rate, or by a local drop the meter was not probing.
4. At least the device, firmware, probe points, voltage, sample rate, decoder
   settings, operating condition, and expected address/transaction.

</details>

## Authoritative further reading

- [Fluke: how to measure voltage with a digital multimeter](https://www.fluke.com/en-us/learn/blog/digital-multimeters/how-to-measure-voltage-with-a-digital-multimeter)
- [Fluke: how to measure current with a digital multimeter](https://www.fluke.com/en-us/learn/blog/digital-multimeters/how-to-measure-current-with-a-digital-multimeter)
- [Saleae: logic analyzer tutorial](https://www.saleae.com/support/tutorials-learning/guides/logic-analyzer-tutorial)
- [Tektronix: oscilloscope fundamentals](https://www.tek.com/en/documents/primer/oscilloscope-basics)
