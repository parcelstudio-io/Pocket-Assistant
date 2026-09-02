# 4 — Step-by-step assembly

This follows the video's visual rhythm—measure, bend, solder the sculpture, prewire modules, mount them, flash, and provision—but moves electrical testing earlier and the removable cell to the very end. Approximate video times are navigation aids, not authoritative dimensions.

## Phase A — prove parts before making the case

1. **Inventory and photograph every label.** Record exact model, PCB dimensions, pin silk, cell marking, holder polarity, and speaker order code. Stop on an ambiguous cell or speaker.
2. **Measure a 1:1 layout.** Put OLED, ESP32, regulator, mic, amp, speaker cup, MOSFET switch, holder plus protected 16340, PTC, insulation, and plugs on cardstock. Add wire-bend and removal clearance.
3. **Build the power path on an insulated bench board.** Wire holder positive → PTC → Pololu #2810 VIN; #2810 VOUT → S8V9F3 VIN; all negative/GND through insulated wire. Leave the cell out and feed the holder nodes from a current-limited supply.
4. **Verify the regulator.** Sweep the simulated cell input only over the documented range and confirm stable 3.3 V unloaded and with a dummy/electronic load. Identify #2810 on/off behavior and reverse-polarity response from its instructions.
5. **Breadboard the digital system.** Flash the bare, harness-disconnected
   SuperMini first. Disconnect USB, then power ESP32/OLED/mic from the regulated
   3.3 V rail. OLED must answer at `0x3c` or `0x3d`; INMP441 `SD` goes to
   GPIO4; audio is 16 kHz. Never join USB and the external rail at this stage.
6. **Test amplifier and enclosed speaker.** Configure DFR0954 left-channel mode, connect speaker only across `+`/`-`, and try the intended ~1 cc cup. Start at low volume; verify neither output reaches GND/frame.

Do not cut or glue anything until all modules pass independently.

## Phase B — fabricate the video-style structure

7. **Draw the forming template** (video about 0:55–1:20). Transfer the measured envelope to paper. The visible 40 mm/15 mm marks are only clues. Mark matching loops, braces, screen, cell door/removal path, switch, mic, speaker, insulation, and antenna keepout.
8. **Cut and deburr brass.** Wear safety glasses. Use a jeweler's saw/mini hacksaw or a tool explicitly rated for the 1.5 mm tube/1 mm rod. File every end smooth.
9. **Bend two matching tube loops** (about 1:05–1:45). Use a jig and gradual bends to avoid kinks. Compare both loops on the flat template after each bend.
10. **Tack the empty frame** (about 1:45–2:15). Clean brass, use the selected
    active brass soft-solder flux and a chisel tip over the silicone solder
    mat, tack 1 mm rod braces, check square/parallel, then finish joints. No
    electronics/cell may be nearby. Neutralize/clean exactly as the flux maker
    directs before primer; never use that active flux on electronics.
11. **Dry-fit dummy volumes.** Use cardstock/foam blocks equal to every part plus insulation. Confirm a 16.8 × 34.4 mm maximum-tolerance NL169 dummy can enter/leave its holder, the speaker cup fits, USB/BOOT are accessible with the cell removed, and antenna/mic paths are open.
12. **Finish the empty frame.** Remove flux, scuff/degrease, mask mount zones, test the finish on scrap, then prime/paint satin silver and fully cure. See lesson 5.

## Phase C — prewire and mount without a cell

13. **Build the harness outside the frame** (video about 2:20–4:20). Label both ends. Use short 26–28 AWG power wiring, 30 AWG signals, and a twisted speaker pair. Every GND is black insulated wire—not frame.
14. **Add support components.** Place decoupling at each load, the polymer reservoir/ferrite near the amp as designed, and strap/data resistors at the correct ESP/mic ends. Inspect polarity and values.
15. **Make insulated sub-plates.** Cover PCB backs with fish paper/Kapton and mount modules to thin FR4/polycarbonate with nylon hardware where possible. Paint is decoration, not insulation.
16. **Mount OLED and white bezel.** Retain mechanically; if glue is necessary, keep it off glass flex, connector, and active area.
17. **Mount ESP32 and microphone.** Point antenna toward an open nonmetal edge. Keep protective mic-port tape until dusty/paint work is finished, then remove it without touching the port.
18. **Mount speaker cup and amplifier.** Keep cup sealed except its front outlet, use black acoustic cloth, and strain-relieve factory leads. Neither speaker lead touches ground.
19. **Mount holder, PTC, regulator, MOSFET switch, and button.** Cell must be removable without flexing a PCB/wire. Expose the black control; keep test points reachable.
20. **Continuity audit.** With cell and USB absent, check every lesson 6 item. Frame must be open/high-resistance to GND, 3.3 V, raw battery nodes, signals, and both speaker leads.

## Phase D — staged power and battery-last completion

21. **Current-limited bring-up.** Feed the empty holder connection from the bench supply at 3.7 V. Begin with switch off, then on. Confirm 3.3 V before permitting normal operating current.
22. **Stress at endpoints.** Test the documented cell high and low operating voltages. Join Wi-Fi while capturing/playing audio. Record current peak, minimum 3.3 V, resets, and temperatures; fix failures before continuing.
23. **Remove bench power and install guards.** Add fish paper around holder terminals, sharp-edge guards, wire strain relief, and a nonconductive cell door. The frame remains floating.
24. **Insert the protected Nitecore NL169 last.** Verify polarity three times—holder mark, meter, and switch input—then insert without tools. Never unwrap, solder, crush, or modify it.
25. **Final battery stress test.** Repeat Wi-Fi/audio and measure cell sag/current/temperature. Remove the cell immediately for swelling, odor, unusual heat, protection trips, or resets.
26. **Provision** (video about 6:40 onward). Provision during the bare-board
    Phase 0 test. Do not USB-flash the final harness until a reviewed service
    connector/removable-module/power-isolation design disconnects the external
    rail and peripherals; removing only the cell is insufficient. Review the
    cloud service's privacy terms before sensitive use.
27. **External charging and pocket inspection.** Remove the cell and charge only in the approved external 16340 Li-ion charger on a nonflammable surface. Before carrying, ensure the guarded device cannot expose a powered node to keys/coins and the cell cannot eject or rattle.

## Hard stops

- Cell chemistry/protection/charger compatibility, holder polarity, or part identity is uncertain.
- Frame has continuity to any net, or either speaker lead reaches GND/frame.
- 3.3 V leaves component limits, firmware resets, or a part heats unexpectedly.
- Cell wrapper is damaged, cell is loose/compressed, or removal requires prying on electronics.
- Antenna, microphone port, speaker diaphragm, or service access is obstructed.
- USB service isolation is absent or its exact clone-board behavior is untested.
