# Power and battery — the part that has to be right

Everything in this note exists because a lithium cell stores enough energy to
start a fire, and because Wi-Fi radios draw current in violent little bursts.

## The problem the video's wiring ignores

A 1S Li-ion cell is not "3.7 V." It is 4.2 V fresh off the charger and about
3.0 V when it should be considered empty. The video feeds that moving voltage
into the SuperMini's `5V` pin, where a small linear regulator (an LDO) drops
it to 3.3 V. Two failures hide in that plan:

1. **An LDO can only step down**, and it needs headroom. At the ESP32-C3's
   335 mA Wi-Fi transmit peak, the SuperMini's LDO drops roughly 0.47 V. With
   a half-empty 3.4 V cell: 3.4 − 0.47 ≈ 2.93 V — below the chip's 3.0 V
   minimum. The symptom is maddening: random resets that only happen during
   Wi-Fi activity, only at lower battery.
2. The amplifier hangs directly on the raw rail, so every bass note yanks the
   same sagging supply the radio depends on.

## The fix: one regulated rail from a buck-boost

The Pololu S8V9F3 converts *any* input from 2.7 V up into a steady 3.3 V —
stepping **down** when the cell is full and **up** when it is nearly empty.
The whole circuit hangs on its output.

The verified budget, worst case (everything peaking at once):

| Load | Peak |
| --- | ---: |
| ESP32-C3, Wi-Fi transmit burst | 335 mA |
| MAX98357A driving 8 Ω at full swing | 412 mA |
| OLED (mostly-lit screen) | ~25 mA |
| Microphone + amp quiescent | ~6 mA |
| **Total** | **~778 mA** |

The regulator delivers ~1.29 A even with the cell at 3.0 V — a 1.66× margin
at the worst point of the discharge. On the cell side that peak becomes about
1 A of draw, well inside the protected 16340's capability.

**Runtime estimate:** if idle listening really averages ~130 mA at the rail,
that is roughly 141 mA from the cell. Derating the labeled 950 mAh to 750 mAh
for planning suggests about **5 hours**. Neither the average load nor usable
capacity has been measured on hardware, so record real runtime before relying
on it. This is a pager-sized companion, not an all-day device.

## Why the switch moved into the battery line

An earlier design put the slide switch on the regulator's EN (enable) pin,
because EN carries almost no current. Three facts break that plan:

- EN low is a **sleep state, not a disconnect** — the cell stays hard-wired
  to the regulator, its input capacitor, and all that wiring, forever.
- The regulator is **enabled by default**. If the tiny EN wire fatigues and
  breaks — in a hand-held flexed sculpture — the pager turns *on* and stays
  on until the cell is flat.
- It does not isolate the raw battery wiring for inspection or service.

So the corrected design breaks the battery's positive lead itself, with a
part rated for the ~1 A that flows there: the Pololu #2810 MOSFET slide
switch (3 A, and it also blocks a reverse-inserted cell), or — if you prefer
the original switch's look — the SS12F44 merely steering the gate of a
P-channel MOSFET that does the heavy lifting.

## The chain, from cell to rail

```text
cell (+) ──► PTC fuse ──► switch ──► regulator VIN ──► 3.3 V rail
   1.5 A hold /          load switch                   (everything)
   3.9 A trip          (not a safety cutoff)
```

- **The PTC** is a resettable fuse: a solid-state part whose resistance
  skyrockets when too much current heats it, then recovers. The cell's
  internal protection also limits current, but its threshold is unpublished
  and slow; the PTC is the protection level we can actually name (1.5 A hold,
  3.9 A trip at 20 °C — comfortably above the ~1 A estimated operating peak).
- **The holder** (polarity-marked CR123A type, behind a guard) makes the hard
  safety steps practical: cell out for soldering, painting, transport of an
  unfinished device, and charging. USB flashing additionally requires the
  separate rail/peripheral service isolation described in lesson 3.

## Charging

v1 charges nothing inside the frame. Pop the cell out, drop it in a proper
bench charger (XTAR/Nitecore class, ≤0.5 A for this cell), charge attended on
a non-flammable surface. This deletes four failure modes at once: a charging
IC whose battery-detection spec (>7 MΩ on the battery node) an attached
regulator violates; charge termination confused by a parallel load; no safety
timer; and a second USB-C port that invites plugging both in at once.

## Rules that have no exceptions

1. Never solder to, strip, dent, or heat a lithium cell. The video does this.
   Do not copy it.
2. The cell comes **out of the holder** for every soldering, painting,
   cleaning, or flashing operation.
3. Nothing conductive may bridge cell terminals — including the brass frame,
   which stays electrically floating and insulated from every powered node.
4. Retire any cell that has been dropped hard, run hot, dented, or has a torn
   wrapper. Do not re-wrap a cell to change its color — the wrapper is its
   insulation *and* your inspection window.
