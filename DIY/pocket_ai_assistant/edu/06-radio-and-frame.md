# The radio vs. the sculpture — antennas, brass, and grounding

## The physics problem

This pager's soul is a 2.4 GHz radio living inside a hand-soldered metal
cage. At 2.4 GHz the wavelength is about 122 mm, which makes a quarter-wave
30 mm and a half-wave 61 mm — and a free-form frame cut from 300 mm brass
tube will contain straight runs in exactly those bands. Metal near an
antenna does three unhelpful things: it detunes the antenna (shifting its
resonant frequency), reflects and shadows the signal, and — when a piece of
metal is itself resonant — re-radiates as an uncontrolled parasitic element.

The SuperMini starts at a disadvantage before any brass appears: its tiny
ceramic chip antenna sits close to the board's ground plane, and community
measurements consistently show it several dB down against even a simple wire
antenna. Espressif's own layout guidance asks for **15 mm of clearance in
all directions** around an antenna; an earlier 5–8 mm proposal was only about
one third to one half of that.

## The design rules

1. **Cantilever the board.** Mount the SuperMini so its antenna end (the end
   away from the USB-C connector) projects 12–15 mm past every frame member,
   with no tube, no cell, and no wire bundle in that zone. The antenna hangs
   out of the cage.
2. **Break the resonant lengths.** Within ~30 mm of the antenna, avoid
   straight continuous tube runs of 28–34 mm or 58–64 mm; put a joint or a
   bend inside those bands.
3. **Keep the cell away.** The 16340's steel can is the largest single metal
   object in the build — it goes at the opposite end from the antenna.
4. **Measure before painting.** With the full harness and cell fitted, compare
   RSSI and connection stability first in open air and then in the finished
   geometry (the boot log or router client page can report it). Record distance,
   orientation, access point, and packet/reconnect behavior. Use the same setup
   after finishing; rework the layout if the frame causes a material loss.

## What the frame is, electrically

Decide this once, write it on the build sheet, and never improvise it at the
iron: **the frame is structure, not circuit.**

- No power, ground, or signal ever uses a brass member as a conductor. The
  video treats the frame as the battery's negative path — this build never
  does.
- Every insulated wire that crosses a member is sleeved or taped at the
  crossing; every module has an insulating barrier (fish paper / Kapton /
  sub-plate) between its solder side and any brass.
- **Keep the frame electrically floating for Rev A.** This open sculpture has
  no protective-earth/chassis system or designed ESD network. A ground bond
  would turn every exposed member into battery return, recreate part of the
  video's failure mode, and can worsen antenna coupling. If a later enclosed
  PCB revision adds a chassis/ESD design, review that as a new architecture.
- The safety test is unambiguous: with cell and USB absent, frame-to-GND,
  frame-to-battery-positive, frame-to-3.3 V, every signal, and both speaker
  terminals must all read open/high resistance.

## Why paint is not insulation

Decorative enamel has no rated dielectric strength, thins to nothing on
edges (exactly where brass meets wires), scratches in a pocket, and hides
whether the metal beneath is live. Treat painted brass exactly like bare
brass: anything that must not touch metal gets real insulation — Kapton tape
(rated ~300 kV/mm), fish paper, heat-shrink — with the paint purely for
looks. The corollary is freeing: you can paint the frame any color you like,
because nothing electrical depends on it.

## The pocket question

A device carried loose in a pocket shares space with keys and coins. Before
this object rides in one: no energized conductor reachable from outside, no
sharp cut tube ends (dome or cap them), the cell's holder contacts shielded
by a nonconductive guard, and strain relief on every wire that a drop or a
squeeze could tug. The acceptance checklist in the build guide makes these
explicit gates, not vibes.
