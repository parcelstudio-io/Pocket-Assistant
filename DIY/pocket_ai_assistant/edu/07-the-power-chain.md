# The power chain — the number that decides whether this works

Most of this build is forgiving. The battery lead is not. This lesson is the
one piece of real electrical engineering in the project, and it exists because
a design review found a failure that every individual part passes and the
*chain* fails.

## Why a buck-boost, restated as a rule

A 1S lithium cell is 4.2 V full and 3.0 V empty. Three converter types could
theoretically make 3.3 V from that, and two of them are traps:

| Type | What it does at 4.2 V | What it does at 3.0 V | Verdict |
| --- | --- | --- | --- |
| **Boost** (step-up only) | Cannot regulate down. Its inductor and high-side path conduct straight through, so the rail sits near 4.2 V | Fine | **Destroys the build.** The ESP32-C3's absolute maximum is 3.6 V |
| **Buck** (step-down only) / LDO | Fine | Needs headroom above 3.3 V; drops out and browns out the MCU | **Strands most of your battery** |
| **Buck-boost** (4-switch) | Steps down | Steps up | **Correct** |

The practical rule when shopping: **listings lie, chips don't.** Search titles
say "step up down" on single-topology parts constantly. Confirm the chip
marking — TPS63020 / TPS63802 / TPS63070 or another named 4-switch buck-boost —
on the board itself when it arrives.

One more shopping rule: prefer a **fixed** output set by a solder jumper over
an **adjustable** one set by a trimmer potentiometer. A trimpot that spans
2.5–8 V sits one screwdriver slip away from putting 8 V on a rail feeding a
3.6 V-max chip. That single consideration is why this build rejects an
otherwise excellent Pololu module.

## The series-resistance budget

Here is the finding. Between the cell and the converter's input there are five
resistances in series, and each one drops voltage under load:

| Element | Resistance | Drop at 1.0 A |
| --- | ---: | ---: |
| Cell internal (protected 16340, typical) | 0.12 Ω | 120 mV |
| PTC fuse — **two RUEF110 in parallel** | 0.125 Ω | 125 mV |
| Holder contacts (acceptance limit) | 0.03 Ω | 30 mV |
| Reverse-block P-FET | 0.03 Ω | 30 mV |
| Load-switch P-FET | 0.03 Ω | 30 mV |
| 26 AWG wiring, both legs | 0.02 Ω | 20 mV |
| **Total** | **0.355 Ω** | **355 mV** |

(The slide switch is absent from this table on purpose: it steers a FET gate
and carries microamps.) At end of discharge the cell rests at 3.0 V, so the
converter's input sees roughly **2.6 V, not 3.0 V** — `netcheck` computes it
at the self-consistent 1.15 A input peak: 2.59 V.

That is the whole point. Every part passes its own datasheet check. The chain
is what decides whether the pager still turns on when the battery is nearly
empty — and the converter has to *cold-start* through it, which is harder than
staying running.

**This turns into a purchase requirement:** the converter must start below
~2.6 V. Both modules this build recommends publish a startup of 1.8–2.0 V, so
both clear it — but one listing for the same module claims 2.8 V, which would
*not* clear it. That conflict cannot be settled from listings, so it becomes a
bench test (below).

`tools/netcheck.py` computes this budget on every run, so if you change the
fuse, the switch, or the wire gauge, the check tells you whether you just broke
end-of-discharge behaviour.

## Why two fuses instead of one

A PTC's hold current is specified at 25 °C and **derates as it warms** — inside
a closed frame next to a switching converter, assume roughly 75 %.

- One RUEF110: 1.1 A × 0.75 = **0.83 A** hold, against the ~1.15 A input peak.
  It would trip during normal loud audio on Wi-Fi. That is a nuisance trip: the
  pager just dies mid-sentence for no visible reason.
- Two in parallel: **1.65 A** hold, comfortably above the peak — *and* half the
  resistance, which buys back 125 mV in the budget above.

Two 20-cent parts instead of one, and it fixes both problems at once. The cell's
own protection PCB remains the real overcurrent backstop; the PTC is the layer
whose threshold you can actually name.

## What protects what

It is worth being precise about the layers, because they are often confused:

1. **The cell's protection PCB** (built into a protected cell) — overcharge,
   over-discharge, short circuit. Trips in milliseconds at several amps. This
   is your last line, not your first.
2. **The PTC pair** — the layer with a threshold you chose and can cite. Resets
   itself when it cools.
3. **The converter's own protection** — over-current and thermal shutdown.
   Everything *downstream* of the converter (OLED, mic, amp, MCU, and most of
   the solder joints in the object) is limited by this, which is why the
   dangerous zone is small and identifiable: the cell, the holder, the wiring
   to the converter input, and nothing else.
4. **The reverse-block P-FET** — stops a cell inserted backwards before it
   reaches anything else. See below.

## Reverse polarity, and why not a diode

A cell can go into a holder backwards, and a holder can be wired backwards.
The tempting fix is a series Schottky diode, and it is the wrong one: a
1N5819 drops ~0.35 V at 1 A, which on top of the budget above would push the
converter under its startup floor. You would trade a rare fault for a
guaranteed one.

The right part is a **P-channel MOSFET** (AO3401A, DMG2301L class): 20–40 mΩ,
so ~30 mV instead of 350 mV — and as of the Rev A lock it is **in the build**:
one always-on reverse-block FET in the spine (drain to battery side, source
downstream, gate to cell −), plus a second FET as the high-side load switch
whose gate the slide switch grounds. The metered polarity check on the holder
leads stays as the belt to the braces.

## The service jumper

One more node deserves protection, from a subtler problem. The ESP32-C3
SuperMini's `3V3` pin is its onboard regulator's *output*. Our converter also
drives that pin. Plug in USB to flash the board and you have two regulators on
one node, with the SuperMini's back-driving our converter's output — a
condition the converter's own manufacturer explicitly does not characterise.

The fix is a **2-pin header and a shunt** in the converter's output lead:

```
converter VOUT ──[ service jumper ]── 3.3 V star bus ── ESP32-C3 3V3, OLED, mic, amp
```

Pull the shunt and the converter is isolated, while USB can still power the
MCU *and* the peripherals for bench work. The service rule is two motions:

> **Cell out of the holder. Jumper out. Then plug USB.**

It is verifiable: with the jumper out, continuity from converter VOUT to the
3.3 V bus must read open.

## The bench test that settles all of it

Do this before the frame exists, with a current-limited supply standing in for
the cell (see [the build guide](../docs/BUILD_GUIDE.md) Phase 0):

1. Assemble the **real chain**: source → PTC pair → reverse-block P-FET →
   load-switch P-FET (slide switch on its gate) → converter. Do not test the
   converter alone on clean bench leads; that hides exactly the resistance
   you are trying to measure.
2. Set the source to 4.2 V, load the 3.3 V rail to 800 mA, confirm 3.30 V ±0.05.
3. Sweep the source down to 3.0 V. The rail must hold 3.3 V the whole way.
4. **Power-cycle at 3.0 V.** This is the real test — it proves cold start
   through the chain, not merely that it keeps running once started.
5. Measure the converter's input voltage during step 3 at 1.0 A. The difference
   from the source is your measured chain resistance. If the external chain
   (everything but the cell) exceeds ~250 mV at 1.0 A, find the offender
   (usually the holder's crimped lead) before proceeding.

If step 4 fails, the pager will work perfectly on a fresh cell and mysteriously
refuse to start when it is half empty. That is a miserable bug to chase after
the frame is soldered shut, and twenty minutes on the bench retires it.
