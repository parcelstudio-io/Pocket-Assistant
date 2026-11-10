# Wiring, assembly, and staged test guide — archived R1 candidate

> **SUPERSEDED; DO NOT WIRE THE POWER SECTION BELOW.** The digital GPIO table
> remains useful, but the #1578/direct-rail/generic-switch power chain is not
> accepted. The current Phase 0 parts and candidate power topology are in
> [FINAL_MATERIALS_FOR_REVIEW.md](FINAL_MATERIALS_FOR_REVIEW.md), and no cell
> connection or final assembly is released. The source build uses microphone
> data on GPIO4; the creator image uses GPIO8. Never mix those maps.

## Power rules

1. Use only the released **protected** pack (or its protected alternate) with
   intact insulation and its factory JST lead. Never charge an `ER14250`,
   `LS14250`, or other primary Li-SOCl₂ cell; never use an undocumented cell.
2. Do not solder to, strip, puncture, clamp, or use the brass frame as a
   terminal for any cell. The pack connects only by its connector.
3. The charger's 4.2 V termination and programmed current must match the
   pack: #4410 ships at 100 mA; 500 mA (jumper) only for the 500 mAh pack
   after a clean attended first cycle. A stock 1 A TP4056 module is not used
   unchanged.
4. **Keep the device off while charging.** This class of charge board has no
   power-path/load-sharing controller.
5. **Slide switch OFF and pack unplugged before USB-C goes into the
   SuperMini.** Never attach both USB-C ports at once. SuperMini clone power
   paths vary; use continuity/diode mode once on your exact board to learn
   whether USB VBUS and the `5V` pin are directly or diode-connected — then
   follow the rule regardless.
6. Insulate the frame from battery positive and every exposed powered node.
   Strain-relieve every wire. The frame floats: no ground, power, or signal
   ever runs through brass.

Stop immediately if the pack swells, leaks, dents, becomes hot, smells
unusual, or has damaged insulation. Disconnect external power only if that
can be done safely; do not touch or move a hot or venting cell. Move people
away and follow the cell maker's emergency procedure.

## Signal wiring — source build (current firmware)

| ESP32-C3 SuperMini | Destination | Destination pin | Electrical note |
| --- | --- | --- | --- |
| `3.3V` | SSD1306 OLED | `VCC` | From the SuperMini's LDO output, not the raw cell rail |
| `GND` | SSD1306 OLED | `GND` | Common ground bus |
| GPIO21 | SSD1306 OLED | `SDA` | Firmware probes address `0x3C`, then `0x3D` |
| GPIO20 | SSD1306 OLED | `SCL` | 128×64 geometry; 400 kHz requested |
| `3.3V` | INMP441 | `VDD` | Microphone supply |
| `GND` | INMP441 | `GND`, `L/R` | `L/R` low = left slot (ICS-43434 alternate: `SEL` low) |
| GPIO1 | INMP441 + MAX98357A | `WS`, `LRC` | Shared I2S word select — separate stub to each module |
| GPIO2 | INMP441 + MAX98357A | `SCK`, `BCLK` | Shared I2S bit clock + 10 kΩ pull-up to 3.3 V (strap pin) |
| GPIO4 | INMP441 | `SD` | Mic data in + 100 kΩ pull-down. **Vendor image uses GPIO8 instead** |
| GPIO3 | MAX98357A | `DIN` | Audio data out |
| GPIO10 | Action button | other leg to `GND` | Active low; 10 kΩ pull-up + 100 nF. GPIO9 remains ROM BOOT |
| Switched battery bus | SuperMini `5V` + MAX98357A `VIN` | — | 3.0–4.2 V from the protected pack through the slide switch; 220 µF + 10 µF at the amp's VIN/GND |
| `GND` bus | MAX98357A | `GND` | Common ground |
| MAX98357A `OUT+`/`OUT−` | Speaker | two leads | Floating bridge (BTL) load — **neither speaker lead ever goes to ground or frame** |

Why the `5V`-pin feed works: the SuperMini's onboard LDO regulates the cell's
3.0–4.2 V down to ~3.3 V for the MCU and peripherals (in dropout below
~3.4 V input, where the rail sags gracefully — the reference device runs
exactly this way), and the MAX98357A's own 2.5–5.5 V rating covers the raw
cell rail directly. Verify stable operation across 3.3–4.2 V on the bench
(build guide Phase 0.5) before final assembly.

## Power wiring — one topology

```text
protected pack (JST-PH) ↔ charger board battery port
charger BAT pad → SPDT slide switch → switched-positive bus → SuperMini 5V + amp VIN
charger GND pad → common ground bus → every module GND
```

- The pack's protection PCM stays in circuit by construction (it's inside the
  pack, upstream of the JST). Never bypass it or solder past it.
- The load taps the charger board's `BAT`/`GND` pads (or a JST splitter) so
  the pack is never soldered.
- Charger USB-C is a charging input only, device switched off.
- Never infer pad function from board color or marketplace photos — read the
  silkscreen and beep it out.

## Build in this order

The full staged procedure with video timestamps is
[BUILD_GUIDE.md](BUILD_GUIDE.md); this is the wiring-level summary.

### 1. Bench-test the electronics before making the frame

- Pack and charger disconnected. Inspect each module for bridges; verify pin
  labels against silkscreen (marketplace boards vary).
- Breadboard ESP32-C3 + OLED + mic + amp with insulated jumpers; speaker only
  at the amp's own terminals via a short twisted pair.
- Power from the SuperMini's USB data cable for flashing and digital tests.
- For full-load audio + Wi-Fi tests, power the switched bus from a
  current-limited bench supply (4.2 → 3.3 V sweep, no USB attached at the
  same time), per build guide Phase 0.5.

### 2. Make a physical template

- Real parts on cardstock; target ≈ 45 × 32 × 20 mm but let the parts decide.
- Access for both USB-C ports, BOOT, the switch, button, mic port, charger
  LED, and the pack's removal path.
- Mark insulation, wire routes, and the antenna keep-out before cutting brass.

### 3. Form and solder the unpowered frame

- Eye protection. Jeweler's saw, deburr, bend with pliers over the template.
- Brass flux/solder on the empty structural frame only; wash and neutralize
  per the flux data sheet. No electronics anywhere near this operation.
- After cleaning: no sharp edge anywhere the pack or wiring can reach.

### 4. Mount and wire modules — pack absent

- Fish paper lines the pack bay; Kapton on module backs and frame crossings.
- Mic hole, display face, speaker outlet, ports, and controls stay clear.
- Route switched-positive, ground, I2C, and I2S as distinct insulated nets.
- With no pack: resistance-check every rail to ground, every net to frame,
  and both speaker leads to everything (all open).

### 5. Current-limited power test in final geometry

- Bench supply at the pack's JST position, 4.0 V / 1 A limit. Boot, display,
  mic, amp, round trip; switch toggles; ten minutes of loud audio + Wi-Fi
  with nothing more than warm.

### 6. Add the pack last

- Meter JST polarity against the charger markings before the first mating.
- Retain the pack mechanically (strap/guard); strain-relieve its lead.
- First charge: attended, device off, non-flammable surface, pack cool,
  DONE LED, 4.20 ± 0.05 V.

## Firmware and functional acceptance checklist

- [ ] Source build digest matches `firmware/source-build.json` (or vendor
      image verified by `tools/pocket_ai_device.py verify`).
- [ ] Explicit serial port and `esp32c3` chip identity confirmed.
- [ ] Switch OFF + pack unplugged during every USB flash.
- [ ] OLED initializes (0x3C or 0x3D), shows the UI, no persistent I2C errors.
- [ ] INMP441 records intelligible audio with `L/R` grounded.
- [ ] MAX98357A drives the speaker; neither output lead grounded.
- [ ] Assistant survives repeated Wi-Fi association + loud audio without
      brownout/reset, on the bench supply and then on the pack.
- [ ] On a clean boot the `Xiaozhi-XXXX` provisioning AP appears and the
      captive portal works at `192.168.4.1`.
- [ ] The cloud backend's privacy posture is acceptable before speaking
      sensitive content near the device.
- [ ] Attended first charge passes: current ≤ programmed value, 4.2 V
      termination, pack cool, device off.
- [ ] No energized conductor or sharp edge can contact the pack, user, keys,
      or coins; all wiring strain-relieved; frame floats from every net.

## Known limitations of the reference (and this build)

- No editable schematic, enclosure drawing, battery datasheet, or exact
  speaker spec is published on the project page; this repository's released
  design substitutes documented parts where the reference used mystery ones.
- The firmware talks to a third-party Xiaozhi-compatible cloud service; it is
  not an offline/on-device language model. Self-hosting is the alternative.
- The creator's links are not stable part numbers; several resolve to
  variants that differ from the labels on the page.
- This topology has no load sharing and no USB source mux — the five hard
  rules are the mitigation, and they are procedural, not electronic. If you
  want plug-and-play USB behavior, that is a Rev B carrier-board project.
