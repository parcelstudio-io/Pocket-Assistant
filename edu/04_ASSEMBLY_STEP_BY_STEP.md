# 4 — Video-aligned, battery-last staged assembly (archived R1)

> **SUPERSEDED; NO FINAL ASSEMBLY IS RELEASED.** Keep this page only as a
> candidate sequence and video index. Its R1 power wiring and part primaries
> are obsolete. Follow
> [FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md), and do
> not connect a cell, cut brass, or proceed to powered enclosure work until
> its promotion gates pass.

The sequence follows the visual rhythm of the reference video—template, form,
join, prewire, mount, flash, and provision—without copying its dimensions,
power architecture, conductive-frame wiring, or battery handling. Video times
are navigation aids only; see the
[reference build guide](../docs/BUILD_GUIDE.md) for the source link and context.

The current exact-part and purchase record is
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md). It
authorizes only a reversible Phase 0 qualification batch; this historical
sequence does not authorize a finished device.

Use [Lesson 13's bring-up ladder](fundamentals/13-debugging-integration-and-capstone.md)
as the controlling method. Record each gate in
[ASSEMBLY_EVIDENCE.md](../docs/ASSEMBLY_EVIDENCE.md) or an equivalent reviewed
test record.

## Phase 0 audio fixture boundary

For the battery-free signal tests, the corrected source build targets the R1
chain:

- **Adafruit #6049 ICS-43434** Phase 0 microphone: `WS/LRCLK` to GPIO1, `BCLK`
  to GPIO2, `DOUT` to GPIO4, and `SEL` low for the left slot. INMP441 is a
  held alternative with analogous signals but a non-interchangeable carrier
  pin order;
- **Adafruit #3006 MAX98357A** amplifier: `LRC` to
  GPIO1, `BCLK` to GPIO2, and `DIN` to GPIO3; and
- Same Sky `CMS-20143-158SP` 8-ohm, 1.5 W speaker primary (with a sealed test
  cavity), compared against `CES-20134-088PM`: either connects only to the
  amplifier's floating BTL output terminals.

The contract is 16,000 frames/s with 64 bit clocks per frame, so the expected
BCLK is `16,000 × 64 = 1.024 MHz`. Prove those clocks and GPIO2 boot/recovery
behavior on the exact fixture before attaching audio data paths.

The creator binary expects microphone data on GPIO8 at 24 kHz; never flash it
onto the GPIO4/16 kHz fixture above. Changing the microphone model reopens
pinout, timing, capture, fit, and acoustic checks — the two named parts above
are the only qualified choices.

DFRobot `DFR0954` remains a held alternative amplifier. The Phase 0 `#3006`
candidate is powered from regulated `5V_SYS`, never directly from a cell. Any
substitution must repeat the exact-board rail, startup, shutdown/mode,
partial-power isolation, current, noise, thermal, and measured-fit tests in the
current decision record.

## Gate 0 — release inputs before irreversible work

Do not cut final stock, solder a final harness, apply finish, use structural
adhesive, or introduce a cell until all applicable inputs exist:

- one reconciled exact-parts register and revision status;
- photographs, measurements, pin orders, connectors, and configuration states
  for the exact received samples;
- a reviewed, source-controlled electrical schematic/netlist covering power,
  grounds, protection, disconnects, USB/service power, test points, BTL speaker
  outputs, and frame isolation;
- one firmware build and matching pin/sample-rate/address contract;
- a current-limited bench-power test plan with limits and stop rules;
- a measured mechanical model or 1:1 mock-up containing real connector bodies,
  mating plugs, wire bends, fasteners, insulation, guards, coating allowance,
  antenna space, acoustic space, and access/removal sweeps; and
- separate approved plans for battery integration and pocket-use qualification.

If [MATERIALS.md](../docs/MATERIALS.md),
[PURCHASE_READINESS.md](../docs/PURCHASE_READINESS.md), the schematic, firmware,
CAD, or the received hardware disagree, the gate is closed. A document banner
does not overrule contradictory physical evidence.

## Stage 1 — incoming inspection and identity

This stage has no video equivalent and happens first.

1. Assign a unit ID to every board or module. Photograph both faces and all
   labels before soldering headers or wires. For the audio fixture, record the
   exact microphone breakout, amplifier breakout, and both Same Sky
   `CMS-20143-158SP` and `CES-20134-088PM` speaker identities rather than only
   their underlying component families.
2. Measure the board, component heights, mounting features, connector pitch,
   pin order, plug envelope, wire exit, antenna region, acoustic port, and any
   switch or jumper state. A published PCB dimension does not replace a
   measurement of terminal blocks, connectors, and wire-exit envelopes on the
   received sample.
3. Compare listing claims with manufacturer documentation and the received
   article. Do not transfer IC specifications to an undocumented module.
4. Quarantine any ambiguous, damaged, reworked, wrongly marked, or
   dimensionally different part.

**Gate 1:** the exact test articles are traceable and the schematic, firmware,
and mechanical records identify them consistently.

## Stage 2 — bare-controller and subsystem tests, no cell

The video flashes late; qualification moves this work forward because it is
reversible.

1. Flash and boot the bare, harness-disconnected controller using the intended
   build. Record flash identity/capacity, build identifier, serial log, and
   recovery-button behavior.
2. Prove the chosen backend or local service is functional and acceptable for
   the intended privacy model before building around it.
3. On an insulated bench, qualify the proposed source path and regulated rail
   from a current-limited laboratory supply. Follow the reviewed schematic,
   manufacturer limits, and written test points—not prose in an older lesson.
4. Bring up one peripheral at a time. Verify rail voltage/current first, then
   display communication, microphone timing/left-slot capture on GPIO4, and
   amplifier timing/mode/gain. Prove low-level playback into an 8-ohm dummy
   load before connecting either speaker.
5. A/B the open `CMS-20143-158SP` in its repeatable sealed test cavity against
   the enclosed `CES-20134-088PM`. Connect either only across the amplifier's
   floating BTL output terminals; neither side is ground. Use isolated or
   differential measurement where required. Start with conservative software
   volume and record differential RMS voltage, amplifier `SD_MODE`, gain,
   current, and temperature. Respect the CMS's 1.5 W nominal rating; for the
   0.8 W CES, enforce and verify no more than 2.53 Vrms differential.
6. Do not connect service USB and an external powered rail at the same time
   unless the reviewed service-power design explicitly permits and has tested
   that state.

Start with conservative current limits and low audio level. Increase a limit
only after the expected current and fault response are understood. See
[measurement practice](fundamentals/05-measurement-dmm-supply-scope-logic-analyzer.md),
[power integrity](fundamentals/06-li-ion-power-integrity-decoupling-uvlo-thermal.md),
and [digital audio](fundamentals/09-i2s-sampling-and-digital-audio.md).

**Gate 2:** every subsystem passes independently; the complete bench stack then
passes startup, shutdown, peak-load, simultaneous radio/audio, thermal, and
service-state tests over its approved input envelope. A cell is still absent.

## Stage 3 — exact 1:1 layout *(video about 0:50–1:10)*

1. Place the exact received parts, safe inert dummies, or dimensioned blocks on
   a 1:1 template. Never use a live cell as a layout tool.
2. Include carriers, insulation, guards, fasteners, labels, test access,
   connector insertion, wire bends, strain relief, acoustic openings, antenna
   adjustment space, and the planned energy-storage removal path.
3. Exercise every access/removal sweep with representative fingers, plugs, and
   tools. Check tolerance extremes, not just nominal dimensions.
4. Update CAD from measured parts, then compare the physical mock-up back to
   CAD. Generated fit reports are studies until this cross-check passes.

**Gate 3:** the exact stack fits with documented clearance and can be assembled,
tested, serviced, and removed without flexing a PCB, scraping insulation, or
blocking RF/acoustic features.

## Stage 4 — fabricate only the empty structure *(video about 1:10–2:15)*

1. Qualify cutting, forming, joining, cleaning, and finish on offcuts of the
   exact structural stock. Follow the material, tool, flux, solder, and coating
   manufacturers' limits.
2. Transfer only the measured template. Cut and deburr while wearing appropriate
   eye protection; make matching bends gradually in a fixture.
3. Join and clean the empty structure with no boards, harness, speaker,
   microphone, display, plastics, adhesive, or cell nearby. Keep structural
   metalwork chemistry separate from electronics work.
4. Recheck square, clearances, sharp edges, and all mounting points against
   inert dummies before any finish.

See [Lesson 12](fundamentals/12-soldering-mechanics-insulation-tolerance.md).
The frame is structure only and is treated as conductive, never as a circuit
return.

**Gate 4:** practice coupons pass, residues are removed by the approved process,
the empty frame matches the measured layout, and no edge or joint threatens an
insulator or wire.

## Stage 5 — qualify and finish the empty structure

Follow [the finish study](05_COLOR_AND_FINISH.md), not a product recipe. Test
the complete provisional surface system and any adhesive on exact-material
coupons. Mask electrical/mechanical seats and clearance-critical surfaces.
Allow the manufacturer's full cure before measuring fit again.

**Gate 5:** coupon adhesion/process evidence, cured dimensions, access, and
electrical-isolation design remain acceptable. Paint is not counted as
insulation or retention.

## Stage 6 — build the harness and carriers outside the frame *(video about 2:20–4:20)*

1. Build only from the released schematic and wiring table. Label both ends of
   every conductor and record connector orientation and pin 1.
2. Use wire gauge, insulation, routing, decoupling, protection, test points, and
   strain relief justified by the measured current and interface requirements.
3. Mount boards on designed nonconductive carriers. Keep service links,
   configuration features, heat-producing parts, and test points reachable.
4. Route switching-power and speaker-current loops away from microphone and
   antenna regions. Keep the two BTL speaker conductors together and isolated
   from frame and ground.
5. Inspect every joint under magnification and repeat continuity/net checks
   before placing the assembly in metal.

**Gate 6:** the harness passes the released netlist, polarity, resistance,
strain-relief, and subsystem bench tests outside the frame with no cell.

## Stage 7 — mount exact parts, still unpowered

Install carriers and guarded components in a reversible order. Preserve the
display active area, microphone acoustic port, the selected speaker's tested
front outlet/grille and cavity geometry, antenna space, thermal clearance,
controls, connectors, debug access, and all planned removal paths. If the CES
wins the A/B test, do not add an assumed rear cup to its existing enclosure; if
the CMS wins, reproduce its qualified sealed rear cavity. Never force a board
or use adhesive to correct a dimensional error.

Before power, verify with USB and every energy source absent:

- intended nets have continuity and unintended adjacent nets do not;
- positive rails are not shorted to their returns;
- the frame is isolated from every rail, signal, connector shell whose design
  requires isolation, and both BTL speaker outputs;
- polarity and pin 1 agree at every connector;
- no sharp edge, fastener, or guard compresses a wire or PCB; and
- service links and switches produce the expected unpowered topology in every
  position.

**Gate 7:** a second-person review or independently repeated check signs off the
unpowered article.

## Stage 8 — current-limited assembled bring-up, no cell

1. Feed only the schematic's designated bench-input point. Begin with the
   approved current limit and all loads/states defined by the test plan.
2. Confirm the expected input and regulated rails before enabling higher-level
   functions. Stop on excess current, wrong voltage, oscillation, reset, odor,
   sound, or unexpected heating.
3. Progress through boot, display, capture, low-level playback, radio join,
   simultaneous capture/playback, peak load, and controlled input endpoints.
4. Record voltage minima/maxima, current peaks, startup behavior, thermal data,
   logs, audio observations, and faults. Repeat enough cycles to expose
   intermittent connections.
5. Exercise USB/service states only according to the reviewed service-power
   procedure. Do not improvise a second power source.

**Gate 8:** the assembled, battery-free unit meets every electrical and thermal
limit and behaves no worse than the bench stack.

## Stage 9 — guards, acoustics, RF, and handling evidence

Fit all intended guards and closures around an inert energy-storage dummy. Then
repeat:

- controlled speaker/microphone A/B tests;
- controlled radio orientation, RSSI, loss, reconnect, and range A/B tests from
  [Lesson 11](fundamentals/11-rf-emc-antennas-and-metal-frame.md);
- thermal and peak-load tests;
- button, connector, debug, and removal-access tests; and
- pocket-hazard checks for exposed conductors, sharp edges, loose hardware,
  cable strain, compression, keys/coins, and shaking.

**Gate 9:** the finished geometry, not only the open bench stack, passes the
written acoustic, RF, thermal, mechanical, and access criteria.

## Stage 10 — battery introduction last

**Withdrawn R1 step—do not perform it.** The earlier #1578 direct-rail battery
release did not survive review. The current authority permits no cell-powered
device assembly: its only Phase 0 cell activity is the separately signed,
two-stage OCV/one-cycle standalone-charge gate in
[FINAL_MATERIALS_FOR_REVIEW.md](../docs/FINAL_MATERIALS_FOR_REVIEW.md#promotion-gates-before-claude-may-say-final-go).
Future cell discharge requires another written release after the battery-free
power, controller-interface, guarding, and fit gates pass.

Keep the pack unplugged during soldering, drilling, finishing, continuity
work, USB servicing, and any rework. Never solder, coat, rewrap, crush,
puncture, or use tools to force a cell. Stop for damaged insulation,
ambiguous polarity, poor fit, unusual heat, odor, swelling, leakage,
protection trips, resets, or unexplained voltage sag. Pocket carry waits for
the acceptance worksheet.

## Hard stops at every stage

- A part identity, pinout, polarity, connector, schematic revision, or firmware
  contract is ambiguous.
- A test requires exceeding a manufacturer limit or bypassing protection.
- The frame contacts any net, either BTL output contacts ground/frame, or paint
  is the only claimed isolation.
- USB/service power can energize an unintended rail or back-drive an unpowered
  device.
- Current, voltage, temperature, reset rate, sound, RF behavior, or mechanics
  falls outside the written acceptance limits.
- The antenna, acoustic ports, diaphragm, service access, test points, labels,
  controls, insulation, ventilation, or removal path is obstructed.
- A cell would be needed merely to continue diagnosis. Return to current-limited
  battery-free testing instead.
