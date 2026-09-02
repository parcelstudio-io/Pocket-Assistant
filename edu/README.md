# Pocket assistant build course

This folder turns Huy Vector's attractive free-form brass build into a reproducible first prototype. It follows the visual sequence in the [build video](https://www.youtube.com/watch?v=25RGnr407PM) and the creator's [material guide](https://www.huyvector.org/robots-kinetic/pocket-ai-assistant), while correcting the battery, grounding, power-regulation, and speaker wiring.

Use the lessons in order:

1. [Software and verification](01_SOFTWARE_AND_VERIFICATION.md) — what is installed here and what each tool can actually prove.
2. [Corrected white/silver/black BOM](02_COMPONENTS_WHITE_SILVER_BLACK.md) — the Rev A identity/specification rationale and incoming-inspection gates (**purchasing list: [docs/MATERIALS.md](../docs/MATERIALS.md)**); and [the component deep dive](02-components.md) records the decisions.
3. [How the parts work together](03_HOW_IT_WORKS.md) — the wiring contract; [the bus/audio deep dive](01-how-it-fits-together.md) explains why.
4. [Step-by-step assembly](04_ASSEMBLY_STEP_BY_STEP.md) — a safer, video-correlated build order.
5. [Color and finish](05_COLOR_AND_FINISH.md) — how to achieve the requested palette without damaging parts.
6. [Acceptance tests](06_ACCEPTANCE_TESTS.md) — the exact evidence needed before the prototype is pocket-safe.

Additional focused lessons cover [power and battery safety](03-power-and-battery.md), [audio and the 16 kHz decision](04-audio.md), [display addresses and boot pins](05-display-and-pins.md), [radio/frame placement](06-radio-and-frame.md), and **[the power chain](07-the-power-chain.md)** — the series-resistance budget, why two fuses, and the service jumper. That last one is the only genuine electrical-engineering problem in the project; read it before ordering the converter.

The complete Amazon-first material list is [docs/MATERIALS.md](../docs/MATERIALS.md); the evidence behind every assembly step is [docs/ASSEMBLY_EVIDENCE.md](../docs/ASSEMBLY_EVIDENCE.md). The machine-readable role list is [parts.csv](parts.csv) (superseded for purchasing by [docs/MATERIALS.md](../docs/MATERIALS.md)). The
[purchase-readiness review](../docs/PURCHASE_READINESS.md) says what is safe
to buy now. Existing [project BOM](../docs/BOM.md) and [legacy/vendor-image
wiring guide](../docs/WIRING_AND_ASSEMBLY.md) retain broader alternatives and
historical firmware notes; neither overrides the Rev A contract.

## Current evidence boundary

The source firmware and pinned artifact have been checked on this computer. KiCad and Wokwi command-line tools are present. No physical ESP32 board, battery assembly, multimeter, power supply, or serial device is connected to this session, so the words **verified** and **tested** in this course never imply a physical hardware test. The final gates in lesson 6 must be performed on the parts in hand.

Do not reproduce the video's exposed-cell construction. Keep the lithium-cell wrapper intact, use factory leads and protection, keep the brass frame electrically floating, and never connect either MAX98357A speaker output to ground.
