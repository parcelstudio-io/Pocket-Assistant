# EE foundations for the Pocket Assistant

The course moves from physical intuition to a complete system. Read it in
order the first time; later, use individual lessons as references.

| Stage | Lessons | You should be able to do afterward |
| --- | --- | --- |
| Orientation | [00](00-safety-evidence-and-course-map.md) | Work safely and distinguish facts, assumptions, calculations, and measurements |
| Physical model | [01](01-units-charge-voltage-current-power-energy-heat.md)–[03](03-components-rc-diodes-mosfets-converters.md) | Explain a closed current path, solve small DC circuits, and predict component behavior |
| Engineering representation | [04](04-boards-schematics-datasheets-and-connectors.md)–[05](05-measurement-dmm-supply-scope-logic-analyzer.md) | Read a schematic/datasheet and use basic bench tools without creating a short |
| Power and digital | [06](06-li-ion-power-integrity-decoupling-uvlo-thermal.md)–[09](09-i2s-sampling-and-digital-audio.md) | Analyze the power rail, GPIO, I2C, and I2S timing |
| Physical implementation | [10](10-class-d-btl-speakers-and-acoustics.md)–[12](12-soldering-mechanics-insulation-tolerance.md) | Reason about audio, RF, soldering, insulation, and packaging |
| Integration | [13](13-debugging-integration-and-capstone.md) | Bring a system up one layer at a time and diagnose planted faults |

The recommended learning kit is a solderless breadboard, resistor/capacitor
assortment, LED, pushbutton, fused digital multimeter, current-limited bench
supply, jumper wires, and a bare ESP32-C3 plus OLED. A logic analyzer is very
helpful; an oscilloscope is optional. No lithium cell is needed for the
foundations course.

Each lesson uses five evidence labels:

- **DATASHEET** — a manufacturer-specified limit or behavior.
- **TYPICAL** — representative, not guaranteed for every unit or condition.
- **ASSUMED** — a design input that still requires evidence.
- **CALCULATED** — follows from stated inputs and equations.
- **MEASURED** — observed on an identified physical unit with recorded tools
  and conditions.

Never silently promote `TYPICAL` or `ASSUMED` to a guaranteed fact.
