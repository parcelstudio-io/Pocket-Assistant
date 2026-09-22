# Published learning pages (Claude artifacts)

Educational material for this project is published as illustrated web pages
alongside the Markdown here. Each page is built from a repository file, which
stays the authority; the page adds diagrams of the mechanisms. If a page and
the repository disagree, the repository wins.

The links are private to the builder's Claude account until shared from each
page's Share menu.

## The course, one page per lesson

Every lesson is condensed to at most three printed pages with two to four
diagrams, three check-yourself questions, and a link back to the full lesson.
Read them in order the first time.

| Lesson | Page | Built from | What it covers |
| ---: | --- | --- | --- |
| – | [How It Fits Together](https://claude.ai/artifact/AaUwqREAJCm2Yj5crymbVs) | [`01-how-it-fits-together.md`](01-how-it-fits-together.md) | The system with the USB-only boundary drawn, the round trip of one question, which lesson answers which question |
| 00 | [Safety and Evidence](https://claude.ai/artifact/HxYY9VNYw9Qve4PG2PFhMt) | [`00-safety-evidence-and-course-map.md`](../edu/fundamentals/00-safety-evidence-and-course-map.md) | The safe order of evidence, the five evidence labels, the lab rules, what software cannot prove |
| 01 | [Units and Energy](https://claude.ai/artifact/CTvQuhYJQLMfG3u7VoegtJ) | [`01-units-charge-voltage-current-power-energy-heat.md`](../edu/fundamentals/01-units-charge-voltage-current-power-energy-heat.md) | Charge in a loop, voltage as height and current as flow, power, heat, prefixes; the 1 kΩ bench lab |
| 02 | [DC Circuits](https://claude.ai/artifact/BJj6Wamepwqsj2nyqHcnmR) | [`02-dc-circuits-ohm-kirchhoff-series-parallel.md`](../edu/fundamentals/02-dc-circuits-ohm-kirchhoff-series-parallel.md) | Ohm, KVL and KCL, series and parallel, the loaded divider, the breadboard's hidden strips |
| 03 | [Components and RC](https://claude.ai/artifact/XfZKVLd7k5YSGNHXJFmYjr) | [`03-components-rc-diodes-mosfets-converters.md`](../edu/fundamentals/03-components-rc-diodes-mosfets-converters.md) | The RC curve and τ, decoupling as a local loop, diodes and MOSFETs, converter input current; the RC lab |
| 04 | [Boards and Datasheets](https://claude.ai/artifact/LeRUxVn4GvZPWC7irTYbxi) | [`04-boards-schematics-datasheets-and-connectors.md`](../edu/fundamentals/04-boards-schematics-datasheets-and-connectors.md) | The SuperMini's power path, schematic versus breadboard, datasheet ranges as nested bands, connector pin order |
| 05 | [Measurement Instruments](https://claude.ai/artifact/BBriZFBYeEjVMvMKAbGT94) | [`05-measurement-dmm-supply-scope-logic-analyzer.md`](../edu/fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md) | Where each meter connects, the supply's CV/CC corner, what a scope sees that a meter cannot, probe grounds |
| 06 | [Power Integrity](https://claude.ai/artifact/DPYa7BeFJFKsAB95SkEc5y) | [`06-li-ion-power-integrity-decoupling-uvlo-thermal.md`](../edu/fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md) | Discharge curve versus cut-off, current pulses and local capacitors, six protection jobs, heat as a ladder |
| 07 | [GPIO and Boot Straps](https://claude.ai/artifact/KoGirsk44qHRXGY8Tt4ELq) | [`07-digital-logic-gpio-pullups-boot-straps.md`](../edu/fundamentals/07-digital-logic-gpio-pullups-boot-straps.md) | Input thresholds, open-drain lines, the GPIO10 button with its internal pull-up, strap pins at reset |
| 08 | [I2C and the OLED](https://claude.ai/artifact/PgocR9PtYSz85o2iBAMxii) | [`08-i2c-and-the-oled.md`](../edu/fundamentals/08-i2c-and-the-oled.md) | Open-drain with pull-ups, one transaction START to STOP, the two addresses, the two swapped silkscreens |
| 09 | [I2S Audio](https://claude.ai/artifact/Gg5EHQxWAtStGZBY9zGV8V) | [`09-i2s-sampling-and-digital-audio.md`](../edu/fundamentals/09-i2s-sampling-and-digital-audio.md) | Sound to numbers at 16 kHz, one frame with two 32-bit slots giving 1.024 MHz, the duplex link, the slot-mismatch signature |
| 10 | [Speakers and Class-D](https://claude.ai/artifact/HWwymfV6dR7jdmsvZ28Lye) | [`10-class-d-btl-speakers-and-acoustics.md`](../edu/fundamentals/10-class-d-btl-speakers-and-acoustics.md) | Class-D switching, the bridge-tied load, peak versus RMS and the 0.8 W speaker, baffles, the differential-safe scope method |
| 11 | [Antennas and the Frame](https://claude.ai/artifact/LV7WFT17RGKGsNrMiDF18V) | [`11-rf-emc-antennas-and-metal-frame.md`](../edu/fundamentals/11-rf-emc-antennas-and-metal-frame.md) | Why the chip antenna needs clearance, the keep-out zone, the 8.5 dBm cap on the quarter-dBm scale, repeatable A/B tests |
| 12 | [Soldering and Mechanics](https://claude.ai/artifact/Mb8pEt8VdRsBwbxzAWFSyP) | [`12-soldering-mechanics-insulation-tolerance.md`](../edu/fundamentals/12-soldering-mechanics-insulation-tolerance.md) | Heat into pad and pin, strain relief, the insulation stack around a cell bay, tolerance stacks |
| 13 | [Debugging and Integration](https://claude.ai/artifact/AZjbnm8acNvaEogGHRiczm) | [`13-debugging-integration-and-capstone.md`](../edu/fundamentals/13-debugging-integration-and-capstone.md) | The bring-up ladder, a decision tree, an elimination matrix, the battery-free integration boundary |

## Plans and guides

| Page | Built from | What it covers | Published |
| --- | --- | --- | --- |
| [Scope Countdown](https://claude.ai/artifact/8w8pHPXT93Y3jmfXRspfbq) | [`DAILY_STUDY_AND_LAB_PLAN.md`](../plan/DAILY_STUDY_AND_LAB_PLAN.md), [`fundamentals/README.md`](fundamentals/README.md), the promotion gates | 22–30 September 2026: two illustrated lessons in two hours plus one build hour every day; the build hours prepare Step 11 (speaker lab, Step 10 record, batch radio survey, amplifier headers, dummy load, wiring and PASS 11A, measuring parts, scope prep), then the DHO802's first captures | 2026-09-21, revised 2026-09-22 |
| [Fast Track Theory](https://claude.ai/artifact/8fmiKrS74xgLZqA3zFEXDC) | [`plan/FAST_TRACK_THEORY.md`](../plan/FAST_TRACK_THEORY.md) | Why each fast-track step works, one mechanism drawing per step, including Step 11's one-supply speaker | 2026-09-21, Step 11 added the same evening |
| [Pocket AI Step 11](https://claude.ai/artifact/6bXhKLGEztiB1Z9zWkGJ4U) | [`plan/FAST_TRACK.md`](../plan/FAST_TRACK.md), Step 11 | Bench guide for the USB-powered speaker with owned parts only: why one supply removes the translator, the wiring, choosing the SD pull-down, the kit-resistor dummy load, and three pass gates | 2026-09-21 |
| [Pocket AI Step 10](https://claude.ai/artifact/8FfvUGDzoj4a3Zg7EQEabr) | [`plan/FAST_TRACK.md`](../plan/FAST_TRACK.md), Step 10 | Bench guide for Wi-Fi under the transmit-power cap and one assistant round trip; three pass gates | 2026-09-21 |

## Adding a page

1. Build the page from the repository file with inline SVG diagrams that show
   mechanisms, not decoration; at most three printed pages for a lesson.
2. Publish it, then add a row here with the source file and the date.
3. Put a one-line pointer to this index near the top of the source file if
   readers of that file would benefit.
