# Wiring, assembly, and staged test guide

> **Purchasing note:** buy only from [MATERIALS.md](MATERIALS.md).

> **Legacy/video-compatible wiring note:** the current Rev A source build and
> removable-cell architecture are documented in the
> [authoritative wiring contract](../edu/03_HOW_IT_WORKS.md) and
> [step-by-step guide](../edu/04_ASSEMBLY_STEP_BY_STEP.md). This file retains
> the pinned vendor-image GPIO8/internal-charger alternative for reference;
> do not mix its power or pin map with Rev A.

This guide transcribes the reference diagram into a firmware/hardware contract and changes the unsafe battery steps shown in the video. Read the [BOM battery decision](BOM.md#battery-decision--resolve-this-before-ordering) before purchasing or soldering a cell.

## Power rules

1. Use only a documented rechargeable 1S Li-ion/LiPo cell with intact insulation, factory tabs/leads, and preferably protection. Never charge an `ER14250`, `LS14250`, or other primary Li-SOCl₂ cell.
2. Do not solder to, strip, puncture, clamp, or use the brass frame as a terminal for a lithium cell.
3. Match the charger's 4.2 V termination and programmed current to the exact cell datasheet. The creator-linked module advertises 1 A and must not be used unchanged with a typical small 14250.
4. Keep the device off while charging. The simple board shown has no documented power-path/load-sharing controller.
5. Switch off or disconnect the battery before plugging USB into the ESP32-C3. Never attach both USB-C ports simultaneously. SuperMini clone power paths differ; use continuity/diode mode to determine whether USB VBUS and the header's `5V` pin are directly or diode-connected before final assembly.
6. Insulate the frame from battery positive and every exposed powered node. Provide strain relief and a nonconductive guard/enclosure before carrying the device.

Stop immediately if the cell swells, leaks, dents, becomes hot, smells unusual, or has damaged insulation. Disconnect external power only if that can be done safely; do not touch or move a hot or venting cell. Move people away and follow the cell maker's emergency procedure.

## Signal wiring

| ESP32-C3 SuperMini | Destination | Destination pin | Electrical note |
| --- | --- | --- | --- |
| `3.3V` | SSD1306 OLED | `VCC` | Do not power this display from the raw cell rail. |
| `GND` | SSD1306 OLED | `GND` | Common ground. |
| GPIO21 | SSD1306 OLED | `SDA` | I2C address expected by firmware: `0x3c`. |
| GPIO20 | SSD1306 OLED | `SCL` | Firmware expects 128×64 geometry. |
| `3.3V` | INMP441 | `VDD` | Microphone supply. |
| `GND` | INMP441 | `GND`, `L/R` | `L/R` low selects the channel expected by this port. |
| GPIO2 | INMP441 + MAX98357A | `SCK/BCLK`, `BCLK` | Shared I2S bit clock. |
| GPIO1 | INMP441 + MAX98357A | `WS`, `LRC` | Shared I2S word-select clock. |
| GPIO8 | INMP441 | `SD` | Microphone data into ESP32-C3. |
| GPIO3 | MAX98357A | `DIN` | Audio data out from ESP32-C3. |
| GPIO10 | Optional momentary button | Other terminal to `GND` | Active-low application/action input recovered from the binary; absent from the public diagram. GPIO9 remains the module's ROM BOOT button. |
| Switched raw battery rail | MAX98357A | `VIN` | Confirm the breakout's allowed voltage. If transient testing calls for an added 100 µF electrolytic, connect `+` to `VIN` and `−` to `GND`. |
| `GND` | MAX98357A | `GND` | Common ground. |
| MAX98357A `+` / `-` | Speaker | Two leads | The speaker is a floating bridge load. **Neither speaker lead goes to ground.** |

The diagram sends the switched 3.0–4.2 V battery rail into the SuperMini pin labeled `5V` and the amplifier `VIN`. This follows the reference but is marginal: the board's 3.3 V LDO may drop out as the cell discharges, and clone regulator/USB circuits vary. Confirm reliable operation over the chosen cell's protected discharge range. A revised carrier with documented buck-boost regulation and USB/battery power-path control is the better engineering solution if reliability matters more than matching the sculpture.

## Safer power wiring

Choose exactly one documented battery/protection topology. Do not mix their pad assignments.

| Allowed topology | Cell/pack connection | Charger and load connection |
| --- | --- | --- |
| Protected pack + charger-only board | Use the pack's factory protected leads; never bypass its protection PCB | Pack leads go to the charger's documented battery input. The switch/load also takes power from those protected pack leads. |
| Bare rechargeable cell + combined charger/protection board | Cell factory tabs/leads go **only** to `B+`/`B-` | Switch/load goes **only** to protected `OUT+`/`OUT-`. Follow the exact board schematic and current ratings. |
| Bare cell + charger without load protection | **Not permitted for this build** | Select a protected pack or add a documented compatible protection stage first. |

After the topology is resolved, connect protected positive through the slide switch to an insulated switched-positive bus feeding SuperMini `5V` and amplifier `VIN`. Connect protected negative and all module grounds to an insulated common-ground bus. Keep the brass frame electrically floating and insulated from every powered conductor. Charger USB-C is a charging input only, with the device switched off. Never infer pad function from board color or marketplace photographs.

## Build in this order

### 1. Bench-test the electronics before making the frame

- Leave the battery and charger disconnected.
- Inspect each module for solder bridges and verify its pin labels; marketplace boards vary.
- Wire the ESP32-C3, OLED, microphone, amplifier, and speaker temporarily with insulated leads.
- Power the ESP32-C3/OLED/microphone only from its USB data cable, fetch/verify the selected firmware, and run a flash dry-run before flashing.
- To test speaker audio at this stage, power only the amplifier `VIN` from a separate documented, current-limited 3.0–4.2 V bench rail with common ground; do not feed that rail into the SuperMini `5V` pin while USB is attached. Alternatively, first prove with continuity/diode tests that this exact board safely exposes USB VBUS at `5V`. Verify clean output at low volume. If audio resets the board, inspect supply wiring and evaluate the recommended local reservoir capacitor.

### 2. Make a physical template

- Place the actual modules, protected/tabbed cell, switch, and charger on cardstock. The video's visible 40 mm and 15 mm marks are only layout clues, not a dimensioned width/depth specification.
- Leave access for both USB-C connectors, BOOT/RESET, the switch, microphone port, and charger status LEDs.
- Mark insulation, wire routes, bend radii, and clearance around the cell before cutting brass.

### 3. Form and solder the unpowered frame

- Wear eye protection. Cut brass with a rated saw/cutter, deburr it, clean joint areas, and bend it with pliers around the template.
- Solder the empty structural frame over a heat-resistant silicone surface. Use electronics no-clean flux only; never plumbing/acid flux.
- After cooling and cleaning, check that intended frame joints have low resistance and that no sharp edge can reach the future cell.

### 4. Mount and wire modules without the cell

- Cover PCB backs and crossings with suitable electrical insulation before they touch brass.
- Mount modules so the microphone hole and connectors remain clear. Use minimal adhesive and add mechanical strain relief to wires.
- Route 3.3 V, switched positive, ground, I2C, and I2S as distinct insulated nets. Avoid using the frame as a convenient signal path.
- With no cell fitted, resistance-check every positive rail to ground and every adjacent signal for shorts. Verify speaker isolation from ground.

### 5. Current-limited power test

- First power the switched raw rail from a current-limited bench supply at the intended cell voltage. Start with amplifier volume low.
- Confirm polarity and record off current, idle current, Wi-Fi peak behavior, and audio peak behavior. Investigate unexpected heating, voltage collapse, resets, or excessive current before continuing.
- Sweep only within the documented cell operating range to ensure the SuperMini regulator remains stable near end-of-discharge.

### 6. Add charger and cell last

- Verify charger pad labels, termination voltage, programmed charge current, and protection behavior before connecting a cell.
- Switch off. Attach factory cell leads/tabs with correct polarity, insulate each connection immediately, and strain-relieve the cell independently of its wires.
- Perform the first charge on a nonflammable surface while attended. Measure charge current with a correctly fused meter or suitable inline instrument (never by placing a current-mode meter across the cell), and measure final cell voltage; stop if either exceeds the cell/charger specification or the cell warms abnormally.
- Unplug the charger before switching the assistant on unless your substituted charger explicitly provides load sharing.

## Firmware and functional acceptance checklist

- [ ] Image digest or source commit/toolchain checks pass before flashing.
- [ ] Explicit serial port and `esp32c3` chip identity are confirmed.
- [ ] Battery switch is off/disconnected during ESP USB flashing.
- [ ] OLED initializes at `0x3c`, shows the UI, and has no persistent I2C errors.
- [ ] INMP441 records intelligible audio with `L/R` grounded.
- [ ] MAX98357A drives the speaker without either output tied to ground.
- [ ] Assistant survives repeated Wi-Fi association and loud audio without brownout/reset.
- [ ] On a clean boot, the expected `Xiaozhi-XXXX` provisioning AP appears and the captive portal works at `192.168.4.1`; confirm the actual SSID in boot logs because no device was available for this audit.
- [ ] The intended cloud/bootstrap privacy policy is acceptable before speaking sensitive content.
- [ ] Charge current, 4.2 V termination, polarity, off-while-charging behavior, and cell temperature pass an attended test.
- [ ] No energized conductor or sharp edge can contact the cell, user, keys, or coins; all wiring has strain relief.

## Known limitations of the reference

- No editable schematic, custom-board source, enclosure drawing, battery datasheet, or exact speaker electrical specification is published on the project page.
- The published image uses a third-party Xiaozhi-compatible bootstrap/cloud service; it is not an offline/on-device language model.
- The creator links are not stable part numbers. Several currently resolve to variants that differ from the labels on the page.
- A successful firmware build or USB bench test does not validate the battery/charger assembly. Treat power validation as a separate hardware test.
