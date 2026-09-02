# 02 — DC circuits: Ohm, Kirchhoff, series, and parallel

## Learning objectives

After this lesson, you should be able to:

- identify nodes, branches, loops, sources, loads, and a reference node;
- explain why steady current needs a closed path;
- apply Ohm's law to a resistor;
- use Kirchhoff's current law at a node and voltage law around a loop;
- calculate equivalent resistance for simple series and parallel networks;
- predict an unloaded and loaded resistor-divider voltage; and
- build and check low-voltage resistor networks without a battery.

## Circuit vocabulary

A schematic shows electrical relationships, not the physical shape of the
wires. These terms let us discuss those relationships precisely:

- A **node** is a set of conductors joined without an intervening component.
  Every point on an ideal node has the same voltage.
- A **branch** is a path between nodes containing one or more elements.
- A **loop** is a closed path that returns to its starting node.
- A **source** can deliver electrical energy, such as a bench supply.
- A **load** receives or converts electrical energy.
- A **reference node**, often labeled `GND`, is assigned 0 V so other node
  voltages have a common reference.

Ground is not automatically Earth, a metal chassis, or “where current vanishes.”
In the Pocket Assistant, the intended electrical return is insulated wiring.
The metal frame is structural, not a current-carrying ground path.

## A complete path comes first

Consider this simple loop:

```text
      switch       resistor
 +3.3 V ─o/ o──────/\/\/\/───── 0 V
   │                              │
   └──────── bench supply ────────┘
```

With the switch closed, the source, resistor, and return form a loop. With the
switch open, the resistor branch has voltage available on one side but no
steady current path.

Real circuits may contain several return paths through signal wires, USB
cables, protection diodes, test equipment, or another power supply. That is why
“the switch is off” or “the battery is removed” does not by itself prove every
node is unpowered.

## Ohm's law for a resistor

For an ideal resistor:

```text
V = I R
I = V / R
R = V / I
```

Choose signs consistently. A convenient **passive sign convention** defines
positive current as entering the terminal marked with positive voltage. Then a
resistor absorbs positive power:

```text
P = V I = I²R = V²/R
```

Example: 3.3 V across 1 kΩ gives:

```text
I = 3.3 V / 1,000 Ω = 3.3 mA
P = 3.3 V × 3.3 mA = 10.9 mW
```

## Kirchhoff's current law: charge does not pile up at a node

Kirchhoff's current law, or **KCL**, says the algebraic sum of currents at a
node is zero:

```text
ΣI = 0
```

An equivalent beginner phrasing is:

```text
total current entering a node = total current leaving it
```

For three parallel loads:

```text
            ┌── load A ──┐
source ─────┼── load B ──┼──── return
            └── load C ──┘

I_source = I_A + I_B + I_C
```

KCL is conservation of charge. It is also the reason a supply wire and return
wire both matter: in normal operation, the current that leaves the source has a
path back.

## Kirchhoff's voltage law: account for energy around a loop

Kirchhoff's voltage law, or **KVL**, says the algebraic sum of voltage rises and
drops around a closed loop is zero:

```text
ΣV = 0
```

For a 3.3 V source and two series-resistor drops:

```text
+3.3 V - V_R1 - V_R2 = 0
```

KVL is an energy-accounting rule. Choose a direction around the loop and retain
the signs. Reversing direction changes every sign but not the physical answer.

## Series circuits

Components are in **series** when the same branch current must flow through
them. Ideal series resistors add:

```text
R_series = R1 + R2 + ...
```

For 1 kΩ and 2.2 kΩ in series across 3.3 V:

```text
R_total = 1.0 kΩ + 2.2 kΩ = 3.2 kΩ
I = 3.3 V / 3.2 kΩ = 1.031 mA

V_R1 = 1.031 mA × 1.0 kΩ = 1.031 V
V_R2 = 1.031 mA × 2.2 kΩ = 2.269 V
```

KVL check:

```text
1.031 V + 2.269 V = 3.300 V
```

The larger resistor has the larger voltage drop because the same current flows
through both.

## Parallel circuits

Components are in **parallel** when both terminals of each component connect to
the same two nodes. They have the same voltage across them, while their branch
currents can differ.

For parallel resistors:

```text
1/R_parallel = 1/R1 + 1/R2 + ...
```

For two resistors, a convenient form is:

```text
R_parallel = R1 R2 / (R1 + R2)
```

With 1 kΩ and 2.2 kΩ in parallel:

```text
R_parallel = (1,000 × 2,200) / (1,000 + 2,200)
           = 687.5 Ω

I_1 = 3.3 V / 1 kΩ   = 3.3 mA
I_2 = 3.3 V / 2.2 kΩ = 1.5 mA
I_total = 4.8 mA
```

KCL check gives the same total. A parallel equivalent must be smaller than the
smallest branch resistance. If your answer is larger, revisit the formula.

### A frequent wording trap

Physical side-by-side placement does not mean electrical parallel, and a row of
parts does not mean series. Follow nodes in the schematic or verify connections
with power removed.

## Voltage dividers and loading

Two series resistors can divide a voltage:

```text
Vin ── R1 ──┬── Vout
            R2
             │
            GND
```

With no significant load at `Vout`:

```text
Vout = Vin × R2 / (R1 + R2)
```

Two equal 10 kΩ resistors ideally produce half the input: 1.65 V from 3.3 V.

But a divider is not an ideal voltage source. If a 10 kΩ load is connected from
`Vout` to ground, that load is parallel with the lower 10 kΩ resistor:

```text
R_lower = 10 kΩ || 10 kΩ = 5 kΩ
Vout = 3.3 V × 5 kΩ / (10 kΩ + 5 kΩ) = 1.1 V
```

This is **loading**. A microcontroller input often has high DC resistance, but
input leakage, protection networks, sampling capacitors, and startup states
still matter. A divider suitable for sensing is not automatically suitable for
powering a module.

## Worked example — an active-low action button

An illustrative button input uses a pull-up resistor:

```text
3.3 V ── 10 kΩ ──┬── GPIO input
                  │
                  o  normally-open button
                  │
                 GND
```

Treat the GPIO as a very high resistance for this first calculation.

### Button released

The button is open. Almost no DC current flows through the 10 kΩ resistor, so
its voltage drop is nearly zero and the GPIO node is near 3.3 V: logic high.

### Button pressed

The button closes and pulls the node near 0 V. The resistor prevents a direct
short:

```text
I = 3.3 V / 10 kΩ = 0.33 mA
P_resistor = 3.3 V × 0.33 mA = 1.09 mW
```

KVL accounts for the 3.3 V across the resistor. KCL says the resistor current
continues through the closed button to ground, apart from tiny GPIO leakage.

Without the pull-up, the released input would be **floating**: its voltage could
be influenced by leakage, noise, touch, or nearby signals.

> **Durable principle:** a pull resistor gives an otherwise open digital input
> a defined state, and its resistance limits current in the asserted state.
>
> **Project status:** 3.3 V, 10 kΩ, the exact button, debounce network, GPIO,
> and board behavior must remain consistent with the reviewed firmware and
> received hardware. This example explains a candidate topology; it does not
> freeze a purchase.

## Reading rail current with KCL

Suppose three **illustrative** parallel loads draw 80 mA, 20 mA, and 2 mA from
one regulated rail. KCL gives:

```text
I_rail = 80 mA + 20 mA + 2 mA = 102 mA
```

Do not interpret that sum as a Pocket Assistant requirement. Digital and audio
loads vary with time, datasheet maxima differ from typical readings, and a
converter must handle transients and startup. The method is durable; the input
numbers are provisional until measured and justified.

## Know the solderless breadboard before using it

A breadboard hides metal spring clips under its holes. On a common style, each
group of five holes beside the center trench is one node; the trench separates
the two sides so an IC can straddle it. Long red/blue “power rails” run in the
other direction—but many are split halfway, and not every breadboard follows
the same pattern.

```text
power rail:  o-o-o-o-o ... possible hidden break ... o-o-o-o-o

terminal:    o o o o o   || center trench ||   o o o o o
             └─one node─┘                     └─one node─┘
```

With all power disconnected, map the actual hidden connections using
continuity mode. Add explicit jumpers across intended rail breaks. A colored
stripe is a label, not proof of voltage or continuity, and a breadboard is not
an appropriate fixture for the pager's ampere-scale power qualification.

## Battery-free lab — verify series, parallel, KVL, and KCL

### Equipment

- current-limited bench supply set to 3.3 V;
- fused digital multimeter;
- solderless breadboard and jumpers;
- 1 kΩ and 2.2 kΩ resistors; and
- eye protection.

No lithium cell is used.

### Unpowered preparation

1. Turn the supply output off and disconnect it from the breadboard.
2. Measure both resistors and record their actual values.
3. Set the supply to 3.3 V with a 10 mA current limit.

### Series network

1. Connect the measured resistors in series across the supply.
2. Calculate expected current and each voltage drop using the measured values.
3. Inspect the circuit, then turn on the output.
4. Measure supply voltage and voltage across each resistor. Check KVL within
   meter and resistor tolerance.
5. Turn the output off before reconfiguring.

### Parallel network

1. Connect both resistors in parallel across the supply.
2. Predict each branch current and their KCL sum.
3. Turn on the output and measure the voltage across each branch.
4. Infer branch currents with `I = V/R`, then add them. Compare that sum with
   the supply's display if its resolution is adequate.
5. Turn the output off and disconnect the circuit.

All resistance and continuity measurements are made unpowered. If a current
reading is desired, review the meter's fuse, lead jacks, and series connection
procedure before changing modes. Inferring current from voltage and measured
resistance is sufficient for this lesson.

## Common mistakes

- **Applying Ohm's law to an entire nonlinear module as though it were one
  fixed resistor.** Operating current can change with state and voltage.
- **Adding parallel resistances directly.** Direct addition is for series
  resistors.
- **Forgetting loading in a divider.** The load changes the lower equivalent
  resistance.
- **Assuming ground absorbs current.** It is a reference and return network;
  current still needs a loop.
- **Treating wires that cross on paper as connected.** Look for a junction dot,
  net label, or explicit connection.
- **Calling physically adjacent components series or parallel.** Connectivity,
  not appearance, decides.
- **Ignoring hidden return paths through USB or instruments.** Multiple powered
  connections can create unintended loops.
- **Measuring resistance on a powered circuit.** De-energize it first.
- **Putting an ammeter across a source.** Current mode has very low resistance
  and can create a short.

## Check yourself

1. Two resistors, 3 kΩ and 7 kΩ, are in series. What is their equivalent
   resistance?
2. The same resistors are in parallel. Is the equivalent resistance greater or
   less than 3 kΩ, and what is it?
3. A node receives 12 mA. Two branches carry away 5 mA and 4 mA. What current
   must leave through a third branch?
4. A 5 V loop contains resistor drops of 1.2 V and 2.1 V. What remaining drop
   is required by KVL?
5. Why does a 10 kΩ/10 kΩ divider no longer produce 2.5 V from 5 V when a
   low-resistance load is attached?
6. In the active-low button example, what prevents pressing the button from
   directly shorting 3.3 V to ground?

<details>
<summary>Answers</summary>

1. `3 kΩ + 7 kΩ = 10 kΩ`.
2. Less than 3 kΩ. `R = (3 kΩ × 7 kΩ)/(3 kΩ + 7 kΩ) = 2.1 kΩ`.
3. `12 mA - 5 mA - 4 mA = 3 mA`.
4. `5.0 V - 1.2 V - 2.1 V = 1.7 V`.
5. The load is parallel with the lower divider resistor, changing the divider
   ratio and drawing additional current.
6. The series pull-up resistor limits the pressed-state current.

</details>

## Authoritative further reading

- [OpenStax University Physics, direct-current circuits](https://openstax.org/books/university-physics-volume-2/pages/10-introduction)
- [OpenStax, Kirchhoff's rules](https://openstax.org/books/university-physics-volume-2/pages/10-3-kirchhoffs-rules)
- [MIT OpenCourseWare 6.002, Circuits and Electronics](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/)
- [NIST SI base and derived units](https://www.nist.gov/pml/owm/metric-si/si-units)

Next: [resistors, capacitors, diodes, MOSFETs, and converters](03-components-rc-diodes-mosfets-converters.md).
