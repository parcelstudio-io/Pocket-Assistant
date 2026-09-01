# Purchase-readiness review — 2026-09-01

## Verdict

**Buy a Phase 0 bench/fit batch now; do not buy the complete final-frame cart
or permanently assemble a pocket device yet.** The firmware and major-part
choices are credible enough for qualification. The power-service path,
carrier for the SMD passives, measured mechanical layout, guards, and physical
power/audio/RF/thermal tests are not finished.

## Phase 0 parts that are reasonable to order

- Two plain ESP32-C3 SuperMini samples and multiple INMP441 samples. These are
  marketplace qualification parts, not dimension-controlled final modules.
- [Adafruit #326 white OLED](https://www.adafruit.com/product/326) and
  [#4209 JST-SH-to-male-header cable](https://www.adafruit.com/product/4209).
- [DFRobot DFR0954](https://www.dfrobot.com/product-2614.html) amplifier.
- Same Sky `CMS-15113-078L100-67` 8 Ω speaker and `BOX-1511-1CC` from a
  distributor that actually has stock, or a later validated 1 cc cup.
- [Pololu S8V9F3 #4964](https://www.pololu.com/product/4964) and
  [Mini MOSFET Slide Switch LV #2810](https://www.pololu.com/product/2810).
- One [Nitecore NL169](https://www.nitecore.com/product/nl169), one
  [MPD BH123A](https://products.memoryprotectiondevices.com/?page_id=742),
  and the exact [XTAR ANT MC1 Plus USB-C](https://www.xtar.cc/product/xtar-ant-mc1-plus-charger-7.html)
  for measurement/qualification. Confirm the charger's automatic 0.5 A mode
  and termination voltage before accepting it.
- Breadboard/test leads, a USB data cable, exact breakout/header adapters, and
  the required measurement/safety tools listed in the authoritative BOM.

Buying these parts does **not** accept them for pocket use. Photograph labels,
measure every envelope, and retain return options.

## Hold until the design gates close

- Final PTC, bead, capacitors, resistors, and their carrier/PCB. The intended
  parts are SMD and there is no reviewed schematic, land pattern, or robust
  free-form mounting method yet.
- Final brass geometry, nickel-silver braces, printed guard/cradle/door,
  sub-plates, standoffs, and cosmetic fabrication sized to the stale CAD.
- Adafruit #4399 for direct SuperMini connection; both ends are JST-SH and the
  SuperMini has no mating socket.
- Longer NL169R/Fenix cell substitutions and an unfrozen Amazon XTAR variant.

Reusable brass stock, paint, insulation, wire, and general tools are fine to
buy opportunistically, but they do not make the current dimensions accepted.

## Release blockers

1. **USB service isolation.** Removing the cell removes regulator input, but
   USB can still drive the SuperMini 3.3 V pin, energize peripherals, and
   reverse-drive the unpowered S8V9F3 output. The exact clone's VBUS/LDO path
   is also uncontrolled. The final carrier needs a reviewed removable-module,
   service-connector, power-mux, or equivalent isolation design. Until then,
   flash only a bare/disconnected SuperMini.
2. **Electrical carrier.** Freeze a schematic and physical land patterns for
   the `1206L150SLYR`, `BLM21PG221SN1D`, `6SVPC220M`, decoupling, pull
   resistors, service isolation, test points, and strain relief. Run ERC/DRC
   if it becomes a PCB.
3. **Mechanical regeneration.** Claude's generated FCStd/STEP/report used the
   wrong BH123A envelope, a discontinued capacitor envelope, and an incomplete
   antenna keepout. The corrected script has not been rerun in FreeCAD and
   still needs actual SuperMini/mic measurements, cell-removal sweep, plugs,
   wires, insulation, mounts, guards, foam, and tolerances.
4. **Hardware proof.** The manifest explicitly records `hardware_tested:
   false`. Complete current-limited input sweeps, Wi-Fi plus simultaneous
   capture/playback, BTL speaker isolation, audio/acoustic tests, warm PTC and
   regulator tests, finished-frame RF comparison, battery sag/runtime, and
   key/coin/shake tests.

## Review of the preparation

| Area | Assessment |
| --- | --- |
| Editable firmware | **Good desk evidence.** Pinned source/SDK/dependencies, two identical clean builds, recorded digest, legal 16 kHz audio, GPIO4 mic data, dual OLED-address probing, and headless fallback. Not hardware-tested. |
| Flashing host tools | **Good.** Explicit ports, integrity checks, dry run, and unit tests. The assembled power-isolation procedure is not solved. |
| Net checker/Wokwi | **Useful limited guardrails.** They catch pin/sample-rate/static-net drift; they do not simulate the battery, regulator, audio power, RF, thermals, or mechanics. |
| Component research | **Strong major-part direction after corrections.** Exact battery, holder, regulator, switch, OLED, amp, and speaker are defensible. Clone boards and passive carrier remain unfrozen. |
| Educational/assembly material | **Thorough and safety-conscious.** The corrected source-build path is clear. Legacy vendor wiring must remain clearly segregated. |
| Claude CAD | **Valuable first placement study, not fit proof.** The audit invalidated the generated 93/93 claim; stale artifacts are retained only for provenance. |
| Physical evidence | **None.** No ESP32, battery circuit, speaker, frame, charger, or thermal test was connected in this workspace. |

Overall preparation quality is **good for ordering a measured breadboard
prototype, insufficient for a one-shot finished pager purchase**. Passing the
four release blockers above changes the verdict.
