# Pocket Assistant electronics course

This directory teaches the electrical-engineering ideas needed to reason about
the Pocket Assistant and provides a small set of project-specific guides. It
assumes arithmetic and basic algebra, but no prior electronics experience.

Start with the [USB prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md) to
boot the controller and test the button, OLED, and microphone using owned
parts. The [daily study and lab plan](../plan/DAILY_STUDY_AND_LAB_PLAN.md)
adds 2–3 hour sessions around that work. Read the relevant
[foundations lesson](fundamentals/README.md) as each circuit becomes useful;
you do not need to finish the course before starting. Keep these references
nearby:

- [equation sheet](fundamentals/reference/equations.md);
- [glossary](fundamentals/reference/glossary.md); and
- [lab record template](fundamentals/reference/lab-record-template.md).

## Project-specific guides

- [Pocket Assistant project overview](01-how-it-fits-together.md) — system
  boundary, corrected-source logical contract, and lesson navigation.
- [White, silver, and black finish study](05_COLOR_AND_FINISH.md) — provisional
  visual direction and the tests required before a finish is adopted.

Project-specific component tables, power recipes, assembly instructions, and
acceptance worksheets are intentionally not duplicated here. Their status
changes as candidates are reviewed.

## Where truth lives

| Question | Source |
| --- | --- |
| Durable theory and safe technique | [Foundations course](fundamentals/README.md) |
| First USB prototype, owned-part wiring, and offline diagnostics | [Prototype quickstart](../docs/PROTOTYPE_QUICKSTART.md) |
| Firmware pins, rates, and build identity | [Firmware README](../firmware/README.md), [`config.h`](../firmware/src/boards/pocket-wall-e-c3/config.h), and [source-build manifest](../firmware/source-build.json) |
| Current candidates, purchase authority, and promotion gates | [Current material decision](../docs/FINAL_MATERIALS_FOR_REVIEW.md) |
| Results from a physical article | A completed [lab record](fundamentals/reference/lab-record-template.md) |

A marketplace listing, successful compile, static check, or CAD model is not
physical acceptance. The manifest currently records `hardware_tested: false`.

## Safety boundary

Keep lithium cells out of early labs. Never strip, solder, heat, puncture, or
deliberately short a cell. Use a current-limited bench supply and follow the
current material decision before introducing stored energy.

Treat the metal frame as conductive and isolate it from every electrical net.
It is never a circuit conductor or return path. Neither bridge-amplifier
speaker lead is ground.
