# 04 — Boards, schematics, datasheets, and connectors

## Learning objectives

After this lesson, you should be able to:

- distinguish an IC, package, module, development board, and assembled product;
- follow nodes and net labels on a schematic without confusing it with physical
  layout;
- distinguish a schematic symbol from a PCB footprint and a 3D envelope;
- find operating limits, pin definitions, timing, and mechanical data in a
  datasheet;
- identify the evidence gap between a chip datasheet and a marketplace module;
- specify a connector by family, pitch, positions, contacts, and mating part;
- explain why firmware, schematic, BOM, PCB/CAD, and the received hardware must
  describe one configuration; and
- create an unpowered evidence record for an unfamiliar board.

## Five levels that beginners often call “the chip”

These are different objects:

| Level | Meaning | Example kind of evidence |
| --- | --- | --- |
| integrated circuit (`IC`) | semiconductor die in a package | manufacturer IC datasheet |
| package | physical body and terminals around the die | package drawing and land pattern |
| module or breakout | IC plus PCB and support parts | module schematic, drawing, revision |
| development board | module/IC plus USB, regulator, buttons, headers, antenna, and other conveniences | board schematic, user guide, BOM, PCB files |
| assembled product | all boards, wiring, power, enclosure, mechanics, and firmware | system schematic, CAD, test record |

An ESP32-C3 datasheet describes the Espressif IC. It does not automatically
describe a generic “SuperMini” board's voltage regulator, USB-C resistors,
onboard LED, antenna, flash population, or dimensions. Likewise, an INMP441 IC
datasheet does not certify an unknown breakout's pin order or decoupling.

This distinction is central to the Pocket Assistant because several candidate
boards are marketplace modules rather than manufacturer-controlled development
boards.

## What a schematic tells you

A schematic is a logical map of electrical connections and component roles.
It usually does **not** show physical distance, orientation, wire length, or
where a connector is reachable.

### Symbols and reference designators

Symbols are abstractions. Common reference prefixes include:

| Prefix | Typical part |
| --- | --- |
| `R` | resistor |
| `C` | capacitor |
| `L` | inductor or ferrite element |
| `D` | diode |
| `Q` | transistor or MOSFET |
| `U` | integrated circuit or module |
| `J` | connector |
| `SW` | switch |
| `F` | fuse or resettable fuse |

`R3` on a schematic and `R3` on a PCB refer to the same logical component, not
to a resistance of 3 Ω.

### Wires, nodes, labels, and junctions

- Lines represent electrical nets, not necessarily individual physical wires.
- A junction dot normally means crossing lines connect.
- Crossing lines without a junction may be unconnected, depending on drawing
  convention.
- Identical net labels connect points even when no line is drawn between them.
- Power symbols are net labels, not energy sources by themselves.
- A deliberate no-connect marker means a pin was reviewed and intentionally
  left open; an unlabeled dangling pin may be a mistake.

Always locate both the forward path and return path. A page full of signal names
can hide the fact that two modules lack a shared electrical reference.

### Pin names and pin numbers are not interchangeable

A symbol might name a pin `GPIO4`, `SDA`, `VIN`, or `GND`, while its footprint
uses pad numbers. The symbol-to-footprint mapping must match the manufacturer's
package drawing and the actual board orientation.

For connectors, write both function and position. “Red wire is positive” is not
enough because harness colors and view directions can change.

## What a PCB adds

A printed circuit board turns schematic nets into copper and physical
mountings:

- **pads** accept component terminals;
- **traces** connect pads on a copper layer;
- **vias** connect copper layers;
- **planes or pours** distribute power or ground;
- **mounting holes** attach the board mechanically;
- **edge cuts** define the manufactured board outline; and
- **keepouts/courtyards** reserve space or restrict copper/components.

PCB geometry matters electrically. Long or narrow power traces add resistance
and inductance. Decoupling placement changes current-loop area. Antennas require
clearance. Switching converters have fast, noisy loops that cannot be repaired
by merely drawing the correct schematic.

### Symbol, footprint, and 3D model solve different problems

| Representation | Main question | Example failure it can miss |
| --- | --- | --- |
| schematic symbol | What connects electrically? | wrong physical pad spacing |
| footprint | Where are pads, holes, and courtyard? | tall connector hitting a guard |
| 3D/body envelope | Does the body occupy available space? | swapped pins or wrong net |
| full mechanical CAD | Can plugs, wires, tools, fingers, doors, and moving parts work? | unmodeled tolerance or flex |

A passing cuboid collision check is not fit proof when headers, cable heads,
wire-bend radii, fasteners, or access paths are absent.

## How to read a datasheet

Do not try to read a long datasheet front to back on the first pass. Use a
repeatable route.

### 1. Confirm identity and document revision

Record the manufacturer, complete orderable part number, package suffix,
datasheet revision/date, and where the document came from. Similar names can
refer to different packages, temperatures, memories, colors, or electrical
options.

Prefer the manufacturer's current page or document. A distributor copy can be
useful, but check whether it is obsolete or for another revision.

### 2. Read the feature summary skeptically

The first page helps identify the part. It is not the full design specification.
Headlines such as “2 A,” “3.3 V,” or “low power” may apply only under stated
conditions elsewhere.

### 3. Separate absolute maximum from recommended operation

- **Absolute maximum ratings** are stress boundaries. Operation there is not
  promised and repeated stress can reduce reliability.
- **Recommended operating conditions** define where normal behavior is
  intended.
- **Electrical characteristics** give minimum, typical, and maximum behavior
  under named conditions.

Design to guaranteed limits with margin. Do not turn a typical graph into a
guarantee.

### 4. Resolve pinout and view direction

Check whether a drawing is top view, bottom view, mating face, PCB side, or wire
side. Find pin 1 marks and package orientation. For an IC, distinguish package
pad numbering from a breakout's header order.

### 5. Find required external circuitry

Read application schematics, power sequencing, decoupling, pull resistors,
configuration pins, unused-pin rules, and layout guidance. “The chip works at
3.3 V” does not mean it works with power and ground alone.

### 6. Read timing and interface details

For a digital interface, record:

- logic voltage levels;
- clock frequency and polarity;
- data width and alignment;
- address or channel-selection behavior;
- setup/hold timing; and
- startup and shutdown sequencing.

Matching the bus name—`I2C` or `I2S`—is not enough if address, channel, format,
or sample rate differs.

### 7. Use mechanical drawings and tolerances

Record body maximums, lead/header height, holes, connectors, component
overhangs, and datum/view. A nominal `22.5 mm` dimension is not a maximum unless
the drawing says so.

### 8. Read notes, errata, and lifecycle information

Footnotes often control whether a specification applies. Also check errata,
product-change notices, and whether a part is active, not recommended for new
designs, or obsolete.

## Evidence hierarchy for a module

For an exact module, seek:

1. manufacturer product page and order code;
2. board schematic and revision;
3. dimensioned mechanical drawing;
4. PCB/pinout and connector definitions;
5. module-level operating limits and test conditions;
6. underlying IC datasheets; and
7. measurements of the received unit.

A marketplace listing can identify a candidate, but photos, titles, and bullet
points can conflict. An underlying IC datasheet proves what that IC is designed
to do, not which IC was fitted or how the seller wired it.

Use the course evidence labels:

- listing statement: usually **ASSUMED** until corroborated;
- IC behavior from the manufacturer: **DATASHEET** for the IC;
- inferred module behavior: **CALCULATED** or **ASSUMED**, not module datasheet;
- caliper or meter result on a serialized board: **MEASURED**.

## Connectors are systems, not generic white plugs

“JST connector” is as incomplete as “USB-like cable.” JST is a manufacturer
with many incompatible families, and marketplace sellers often use the name
loosely for clones.

Specify at least:

- manufacturer and series/family;
- pitch, measured center-to-center between adjacent positions;
- number of positions and rows;
- wire-to-board, wire-to-wire, or board-to-board role;
- header orientation: top/vertical or side/right-angle entry;
- housing, header, and crimp-contact order numbers;
- mating-face and PCB-side pin numbering;
- wire gauge and insulation range;
- current/voltage and temperature ratings under applicable conditions;
- keying, latch, polarization, and contact plating; and
- required crimp tool or qualified pre-crimped lead.

For example, genuine JST **PH** is a 2.0 mm-pitch family. A plug advertised as
“JST-PH 2.5 mm” is either mislabeled or a different family; do not buy a mating
part from that description. Measure pitch and identify housing geometry.

Pitch alone is insufficient. Different 2.0 mm families can still be
incompatible. A two-position connector also provides only one center-to-center
measurement, so inspect latch and housing dimensions.

### A connector changes the mechanical design

Model the mated pair, not just the PCB socket. Include housing length, wire exit,
bend radius, finger or tool clearance, latch travel, unplug path, strain relief,
and repeated service cycles. A connector that fits while empty may become
unusable after the board is installed.

USB-C deserves the same discipline. The receptacle alone does not prove correct
CC resistors, data wiring, current behavior, or cable compatibility on a generic
board.

## One configuration must cross every representation

The following artifacts are coupled:

```text
requirements
    ↓
exact BOM/order codes ↔ schematic/net names ↔ firmware pins and protocols
    ↓                         ↓
PCB or harness          mechanical CAD/access
    ↓                         ↓
received-part inspection and measured acceptance tests
```

A change to one layer can require changes elsewhere:

- swapping an OLED may change address, pin order, color, mounting, or driver;
- swapping an MCU board may change flash, LED/strap loading, USB path, antenna,
  buttons, or dimensions;
- swapping an amplifier board may change shutdown/channel resistors, gain,
  connector, and height; and
- swapping a speaker may change impedance, power, enclosure volume, connector,
  acoustic outlet, and CAD.

Static net checks catch valuable inconsistencies, but they cannot prove exact
part identity, solder quality, RF, acoustics, power integrity, or human access.

## Pocket Assistant interface map: durable versus provisional

This table describes the current qualification direction, not a released BOM:

| Area | Current interface constraint | Still provisional until evidence closes |
| --- | --- | --- |
| MCU | corrected firmware targets ESP32-C3 and requires the recorded GPIO/flash contract | exact SuperMini vendor/revision, flash, LDO/VBUS path, LED, antenna, dimensions |
| display | firmware expects a 128×64 SSD1306-compatible I2C device at a probed address | exact module, true controller, pin order, pull-ups, header, color, envelope |
| microphone | current source expects 3.3 V I2S input in the selected channel and timing | exact breakout schematic, port location, pin order, decoupling, acoustic mounting |
| amplifier | current source uses legal MAX98357A-format timing and floating BTL speaker outputs | exact board, `SD_MODE` network, gain, headers/terminal, height, thermal behavior |
| speaker | amplifier and speaker impedance/power/enclosure must be compatible; neither BTL lead is ground | exact driver, lead/connector, dimensions, box, grille, loudness and feedback behavior |
| power | every load needs a regulated rail and reviewed return/service path | exact converter, protection, switch, passives, carrier, USB isolation, heat and startup |

The theory and interface checks narrow the choices. They do not authorize the
final component or frame purchase. Use the current purchasing and readiness
documents only after their contradictions are resolved and exact samples pass
qualification.

## Worked example — qualify a candidate OLED before connection

Suppose a listing offers a white 0.96-inch, 128×64 “SSD1306 I2C” breakout. Do
not begin by connecting four wires from a listing photo.

1. **Record identity.** Save the exact listing/order identifier, seller, arrival
   date, PCB markings, and clear front/back photos. If no board manufacturer and
   revision exist, mark the module identity **ASSUMED**.
2. **Find the controller source.** Read the SSD1306 manufacturer's datasheet for
   protocol behavior, but do not claim it proves the board contains that IC.
3. **Read the received silkscreen.** Record header order exactly as viewed:
   `GND`, `VCC`, `SCL`, `SDA` or another order. Never infer the two power pins
   from wire colors.
4. **Inspect the module circuit.** Identify any regulator, level shifting, and
   I2C pull-ups if possible. Supplying 5 V to a board can also pull its I2C lines
   toward 5 V; use only a reviewed 3.3 V arrangement with the ESP32-C3.
5. **Measure mechanics.** Use calipers for maximum PCB, display glass, header,
   flex/overhang, and component height. Record connector and cable exit.
6. **Check unpowered.** Confirm obvious ground continuity and absence of a
   near-short between power and ground. A continuity result cannot prove the
   complete schematic.
7. **Power safely.** Only after review, use a current-limited 3.3 V supply. Check
   rail current and temperature before attaching signal pins.
8. **Test function.** Run an I2C scan and a full-pixel/edge pattern. An ACK at
   `0x3C` proves a device acknowledged that address; it does not by itself prove
   controller identity, resolution, color, or good pixels.
9. **Update every artifact.** Put measured dimensions and verified pin order
   into the wiring record and CAD before deciding the frame.

That sequence turns a listing into a qualified physical sample one evidence
step at a time.

## Battery-free lab — make a board evidence sheet

Choose an inexpensive spare low-voltage breakout or development board. Leave it
unpowered; no lithium cell is used.

### Equipment

- board and its packaging/listing identifier;
- magnification and good light;
- calipers or a metric ruler;
- DMM for unpowered continuity only; and
- notebook or worksheet.

### Procedure

1. Photograph both sides next to a scale. Assign the board a sample ID.
2. Transcribe every marking without guessing what it means.
3. Separate facts into three columns:

   | Claim | Evidence label/source | Test needed |
   | --- | --- | --- |
   | example: listing says 3.3–5 V | **ASSUMED**, listing | module schematic or controlled supply test |
   | example: PCB width 18.2 mm | **MEASURED**, named caliper | repeat at maximum protrusion |

4. Locate power, ground, signals, buttons, LEDs, antenna, holes, and connectors.
   Mark uncertain pins as unknown rather than filling them from a similar photo.
5. Find the primary datasheet for each readable IC marking. Record which claims
   apply to the IC and which remain unknown about the board.
6. Draw a block-level schematic. Include every connector position and its view
   direction.
7. With all sources removed, use continuity mode only for low-risk questions
   such as whether labeled ground pins join. Do not scrape coatings, bridge
   pins, or touch a MEMS microphone port.
8. Measure the complete envelope, mounting holes, connector pitch, plug approach,
   and likely cable-bend space.
9. Write a release sentence: either “qualified for the following limited bench
   test” with conditions, or “not ready because ...”. Do not use “looks right.”

The deliverable is the evidence sheet, not a powered board.

## Common mistakes

- **Treating the IC datasheet as the module datasheet.** Support parts and
  routing remain unknown.
- **Copying a pinout from a visually similar board.** Marketplace revisions can
  swap pins or parts without changing the title.
- **Confusing absolute maximum with recommended operation.** Surviving a limit
  is not normal function.
- **Ignoring footnotes and test conditions.** They define when a number applies.
- **Reading a bottom-view package drawing as top view.** Confirm the datum and
  pin-1 mark.
- **Assuming the schematic is a placement drawing.** Electrical adjacency does
  not imply physical adjacency.
- **Assigning a symbol the wrong footprint.** Correct nets can land on wrong
  pads.
- **Using “JST” or pitch alone as a connector specification.** Series, housing,
  contacts, and mating orientation all matter.
- **Modeling only an empty socket.** The plug, wires, bend, latch, and service
  path occupy space.
- **Believing an I2C ACK proves the display model.** It proves only an
  acknowledgment at that address.
- **Letting the BOM, firmware, and CAD name different component generations.**
  A pass in one representation then says little about the build.

## Check yourself

1. What does an ESP32-C3 IC datasheet fail to prove about a generic development
   board?
2. What is the difference between a schematic symbol and a footprint?
3. Why is an absolute maximum voltage not a recommended supply voltage?
4. A package drawing says “bottom view.” Can its left-to-right pin order be
   copied directly onto a top-view wiring sketch?
5. Why is “2-pin JST, 2.0 mm” still incomplete?
6. A CAD report passes, but the USB plug and guard are not modeled. What has the
   pass established?
7. A display acknowledges address `0x3C`. Name two things that observation does
   not prove.

<details>
<summary>Answers</summary>

1. It does not prove the board's regulator, USB circuit, flash, LED, buttons,
   antenna, connector, pinout, dimensions, or assembly revision.
2. The symbol represents electrical function and pins; the footprint represents
   physical pads, holes, outline, and placement constraints.
3. Absolute maximum is a stress boundary near possible damage, not a region
   where normal performance is guaranteed.
4. No. Translate the view using the pin-1 mark and manufacturer drawing.
5. Family/series, header and housing, contacts, orientation, pin numbering,
   ratings, wire range, and mating geometry are still needed.
6. Only that the geometry actually modeled satisfied the implemented rules. It
   says nothing about omitted plug or guard fit.
7. For example: controller identity, resolution, pixel health, color, pin order,
   voltage safety, pull-ups, or mechanical fit.

</details>

## Authoritative further reading

- [KiCad 10, *Getting Started in KiCad*](https://docs.kicad.org/10.0/en/getting_started_in_kicad/getting_started_in_kicad.html)
- [Espressif ESP32-C3 datasheet](https://documentation.espressif.com/ESP32-C3_Datasheet_en.pdf)
- [Espressif ESP32-C3 hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/index.html)
- [TDK InvenSense INMP441 datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf)
- [Analog Devices MAX98357A/MAX98357B datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf)
- [JST PH family datasheet](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf)

Next: [measurement and debugging tools](05-measurement-dmm-supply-scope-logic-analyzer.md).
