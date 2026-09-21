# Fast track — build Pocket AI Assistant v0 one step at a time

This is the main beginner build guide. **Do not read the whole guide before
starting.** Complete one `PASS` box, stop, and come back for the next one.
Stopping after any passed step is a successful work session.

## What this guide builds

At the end you will have a loose, USB-powered desk prototype with:

- one ESP32-C3 controller running firmware you built;
- one push button;
- one OLED display; and
- one microphone whose readings change when you speak.

This is **Pocket AI Assistant v0**, not the finished pocket device. The
supported firmware deliberately keeps the amplifier disabled. This guide does
not connect a battery, charger, amplifier, speaker, external power supply, or
brass enclosure, and the loose breadboard must not be carried in a pocket or
bag.

The project is intentionally split into three milestones:

1. **Build now:** the USB hardware prototype in Steps 0–9.
2. **Optional after a privacy decision:** the networked assistant experiment
   in Step 10. It uses a third-party service and still has no spoken output.
3. **Wait for later engineering tests:** powered speaker, battery, charging,
   enclosure, and pocket carry.

Two companion pages sit beside this one, and both are optional while you
build:

- [Parts outline](FAST_TRACK_PARTS.md) — every component this guide names,
  grouped by step, with its purchase link and whether that link is a recorded
  order or only a candidate.
- [Theory companion](FAST_TRACK_THEORY.md) — why each step works, linking out
  to the illustrated concept notes and the full course.

Theory is optional while building; the safety instructions on this page are
not.

The `PASS` boxes are targets for **you** to establish on your received parts,
not claims that the hardware has already passed. No physical-board results are
recorded in this repository yet.

If you feel overwhelmed, make today's whole assignment Step 0. Finding two
items, sorting the pile into safe groups, and stopping is real progress.

## Safety rules for every step

> **This guide uses USB power only.** Keep every battery, charger, amplifier,
> speaker, bench supply, regulator, and brass part off the bench. Power the
> OLED and microphone only from the controller's `3V3` pin—never from `5V` or
> `VBUS`.

1. Unplug USB before touching or moving any wire.
2. Use continuity or resistance mode only while USB is unplugged.
3. Do not use the meter's `A` or `mA` current modes anywhere in this guide.
   Keep the black lead in `COM` and the red lead in `V/Ω`.
4. Before reconnecting USB, read the labels on the actual boards and compare
   every wire with the table. Amazon photos are not pinout authority.
5. After Step 6 creates `3V3` and `GND` rails, check between them with
   unpowered continuity mode before every reconnection. A brief chirp can be
   capacitance; a persistent steady tone is a stop condition.
6. If anything becomes hot, smells unusual, smokes, behaves erratically, or
   repeatedly resets, disconnect USB at the computer end if safe and stop.
7. GPIO9 is the controller's **BOOT** button. The project button uses GPIO10.

## When you reopen a terminal

Use a Bash terminal and run commands from the repository root. Check that you
are in the right folder before doing anything else:

```bash
pwd
test -f firmware/scripts/setup.sh && echo "Project folder found"
```

If the second command does not print `Project folder found`, open a terminal in
the `pocket_ai_assistant` folder and try again. In every new terminal after
Step 1, activate the installed ESP-IDF tools first:

```bash
. firmware/.work/esp-idf/export.sh
```

Replace `/dev/ttyACM0` in later commands with the exact port printed on your
computer. It may instead be `/dev/ttyUSB0`, `/dev/cu.*`, or a Windows `COM`
port.

Product links identify the listings saved in the purchase record unless they
are explicitly marked as a candidate or search link. Marketplace sellers and
revisions can change; the labels on the received part control. The
[parts outline](FAST_TRACK_PARTS.md) collects every one of those links in one
place with its provenance marked.

## Know the two likely stopping points

- Steps 0–4 need only one plain controller and one proven USB data cable.
- Step 5 needs 26 usable header pins, practice material, soldering tools, and
  solder wick if you need to remove excess solder. It is fine to finish Step 4
  today and wait for those items.

---

## Step 0 — clear the desk and find the first two items

### Take out

- One plain [Meshnology ESP32-C3 SuperMini](https://www.amazon.com/dp/B0F888JQ91).
  The purchase record says ten were ordered, but you still need to find and
  inspect the package.
- One USB-A-to-C **data** cable. The project record does **not** confirm that
  the planned [Rankie data-cable 3-pack](https://www.amazon.com/dp/B01JRY0VE4)
  was bought. Any cable you already own is fine if Step 3 proves that it
  carries data.
- A small label or masking tape, a pen, and your phone.

### Do

1. Keep lithium packs disconnected and terminal-protected in their own
   nonconductive storage, away from brass, sharp parts, tools, and heat. Do not
   use a pack that is swollen, damaged, leaking, unusually warm, or smells
   unusual. If a pack is already hot, hissing, venting, smoking, or leaking,
   do not connect, charge, squeeze, puncture, or pick it up just to store it.
   Move people away and follow the maker's and local emergency guidance.
2. Put the charger, amplifier, speaker, regulators, and bench supply in a box
   labeled `LATER — POWER/AUDIO — DO NOT CONNECT`.
3. Put brass and cutting tools in a separate box labeled
   `LATER — BRASS/SHARP`.
4. Leave the button, OLEDs, microphones, breadboards, jumpers, resistors, and
   spare controllers in their packages in a box labeled
   `USB BUILD — WAIT FOR ITS STEP`. Do not inventory that box now.
5. Leave only one controller and one cable in the active work area.
6. Confirm the controller is a plain ESP32-C3 SuperMini matching the linked
   listing, and look at the end **opposite the USB connector** to see which
   antenna it has: a ceramic chip antenna (small red or brown block), a zigzag
   copper trace, or a U.FL socket for an external antenna. Write it down. All
   three work, but the SuperMini is widely reported to leave too little
   clearance around its antenna, so plan to keep that end free of jumper
   wires, modules and metal when you reach Step 6. Reject an RGB LED on
   GPIO8, which is a different variant with a different pin map. If the
   package says `Plus`, return it to the `USB BUILD` box with a note saying
   `not for this guide`, then find a plain one.
7. Label its bag or written record `A1` and photograph both sides. Keep tape
   off the board, especially its antenna end.

### PASS

- [ ] Only board `A1` and one possible data cable remain in the active work
      area; batteries are separately protected; the `USB BUILD`,
      `POWER/AUDIO`, and `BRASS/SHARP` groups are put away; and `A1` is the
      plain SuperMini with no RGB LED, and you have **identified what sits at
      the end opposite the USB connector**: a ceramic chip antenna (a small
      red or brown block), a zigzag copper trace, or a U.FL socket. Record
      which. Nothing before Step 10 uses the radio, so an antenna problem
      stays invisible until then — and the SuperMini's antenna is known to
      perform poorly when anything crowds it.

If you cannot find a cable, you can complete Steps 1–2 on the computer, but
Step 3 must wait for a proven data cable.

Optional theory: [why the build starts with one power source and one unknown](FAST_TRACK_THEORY.md#step-0--why-the-boundary-is-so-small).

---

## Step 1 — install the firmware tools

### Take out

- Your computer. Hardware can stay unplugged.

### Do

From the repository root, run setup by itself:

```bash
firmware/scripts/setup.sh
```

If setup prints an error, stop and use the troubleshooting list below. Only
after setup finishes without an error, run:

```bash
test -f firmware/.work/esp-idf/export.sh && echo "Setup ready"
```

The first run downloads a large toolchain and may appear quiet for a while.

### PASS

- [ ] The commands finish without an error and print `Setup ready`.

### If it does not pass

1. Confirm the computer has internet access.
2. Run `firmware/scripts/setup.sh` once more; setup is designed to resume
   safely.
3. If it still fails, stop and save the last 30 lines of output. Do not use
   `sudo` to work around it.

Optional theory: [how source code becomes firmware](FAST_TRACK_THEORY.md#steps-1-through-4--from-source-code-to-a-running-board).

---

## Step 2 — build and verify the diagnostic firmware

### Do

Run these commands in order:

```bash
. firmware/.work/esp-idf/export.sh
firmware/scripts/build.sh
python3 firmware/scripts/verify_source_build.py
```

The first build may download pinned source and components, so keep the computer
online and expect it to take a while. “Offline” describes the resulting
diagnostic firmware: after flashing, it does not start Wi-Fi or send microphone
audio anywhere.

### PASS

- [ ] The verifier prints `Build mode: diagnostics; amplifier: disabled` and
      `Verified source artifact:` without printing an error.

### If it does not pass

1. Run the `export.sh` command again in the same terminal.
2. Run `firmware/scripts/build.sh` again.
3. If verification still fails, stop. Never flash a build that fails its
   verifier; use the [firmware troubleshooting guide](../firmware/README.md).

Optional theory: [what building and verifying actually prove](FAST_TRACK_THEORY.md#steps-1-through-4--from-source-code-to-a-running-board).

---

## Step 3 — prove the cable and identify board A1

### Take out

- Board `A1`.
- The possible USB data cable.

Do not attach the button, OLED, microphone, or any other wire yet.

### Do

1. Leave board `A1` unplugged and run:

   ```bash
   . firmware/.work/esp-idf/export.sh
   python3 tools/pocket_ai_device.py ports
   ```

2. Save or photograph that first port list.
3. Connect bare board `A1` directly to the computer and run the same command
   again:

   ```bash
   . firmware/.work/esp-idf/export.sh
   python3 tools/pocket_ai_device.py ports
   ```

4. The new entry is board `A1`'s port. Substitute that exact entry here:

   ```bash
   . firmware/.work/esp-idf/export.sh
   python3 -m esptool --chip esp32c3 --port /dev/ttyACM0 flash-id
   ```

### PASS

- [ ] The board appears as a serial port, is identified as an ESP32-C3, and
      reports at least 4 MB of flash.

### If it does not pass

1. Try another USB port and reconnect the cable firmly.
2. Try a different known data-capable cable; a charge-only cable can power the
   board without creating a serial port.
3. If a port is listed but the command says `Permission denied` or `busy`, do
   not blame the board. Close serial programs and use the
   [host-tool troubleshooting guide](../tools/README.md#troubleshooting) to fix
   host access.
4. After port access works, hold **BOOT**, tap **RESET**, release **BOOT**, and
   retry. If it still fails, try `A2` with the same cable and computer USB port.
   Label `A1` `QUARANTINE` only if `A2` identifies successfully under those
   same conditions.

If you found additional controller boards, leave them in their package.

Optional theory: [why flash identity is a hardware test](FAST_TRACK_THEORY.md#steps-1-through-4--from-source-code-to-a-running-board).

---

## Step 4 — flash the bare board and see it run

### Do

1. Preview the exact flash operation, using your real port:

   ```bash
   . firmware/.work/esp-idf/export.sh
   firmware/scripts/flash.sh /dev/ttyACM0 --dry-run
   ```

2. Read the preview. Do not continue if it printed any error.

### PASS 4A — safe to flash

- [ ] The preview names the exact port from Step 3 and prints
      `Build mode: diagnostics; amplifier: disabled`.

### Do, after PASS 4A

3. Flash and open the monitor:

   ```bash
   . firmware/.work/esp-idf/export.sh
   firmware/scripts/flash.sh /dev/ttyACM0 --monitor
   ```

4. When asked, type the exact confirmation shown by the script.
5. Watch the log for at least 60 seconds. Exit the monitor with `Ctrl+]`.
6. Save a screenshot or copy of the log.

### PASS 4B — board runs

- [ ] The log contains
      `BENCH DIAGNOSTICS: offline; Wi-Fi/cloud off; amplifier GPIO5 LOW` once,
      then continues printing diagnostic lines for 60 seconds without showing
      another boot sequence or repeated resets.

Missing-display messages and meaningless microphone numbers are expected
because those parts are not connected yet.

### If it does not pass

1. Retry the **BOOT → RESET → release BOOT** sequence from Step 3.
2. Confirm you used the port printed by the port-list command.
3. If flashing succeeded but the board loops, save the entire log and stop
   before adding hardware.

Label the board record `SOURCE DIAGNOSTICS / MIC GPIO4 / 16 kHz`.

Optional theory: [flash, boot, reset, and serial logs](FAST_TRACK_THEORY.md#steps-1-through-4--from-source-code-to-a-running-board).

---

## Step 5 — prepare reliable header pins

Start with Step 5A. Do Steps 5B–5E only for modules whose header pins are not
already straight, firmly soldered, and electrically tested.

### Find before starting

- [Hosyond SSD1306 OLED](https://www.amazon.com/dp/B09T6SJBV5), recorded as
  purchased in a five-pack.
- [AITRIP INMP441 microphone](https://www.amazon.com/dp/B092HWW4RS), recorded
  as purchased in a five-pack.
- X-Tronic 3020-XTS soldering kit, Chip Quik CQ4LF electronics flux pen, and
  loose 2.54 mm headers are recorded as ordered; BOENFU flush cutters are
  separately recorded as owned. Their exact order links were not saved, and
  none is confirmed found. Use these
  [X-Tronic search results](https://www.amazon.com/s?k=X-Tronic+3020-XTS),
  [Chip Quik search results](https://www.amazon.com/s?k=Chip+Quik+CQ4LF), and
  [BOENFU search results](https://www.amazon.com/s?k=BOENFU+flush+cutters) only
  to compare names and packaging with your pile.
- [MAIYUM 63/37 0.8 mm solder](https://www.amazon.com/dp/B076QF1Y85).
- [3M Solus 1000 safety glasses](https://www.amazon.com/dp/B016KZ1ZPM).
- [KAIWEETS HT118A meter](https://www.amazon.com/dp/B08BL288LW).
- Optional but strongly useful for a beginner:
  [JoTownCand solder wick](https://www.amazon.com/dp/B0DRN688Q5). It is listed
  as still needed, not as already purchased.

### Step 5A — inspect and count

1. Keep USB unplugged. Put the meter's black lead in `COM`, its red lead in
   `V/Ω`, and select continuity/beeper mode. Touch the probes together: expect
   a steady tone or near-zero reading. Separate them: expect no tone or an
   open/over-range display. Stop if the meter does not pass this self-check.
2. Inspect the controller's 16 header positions, the
   OLED's 4, and the microphone's 6. Put the phone in a clean clear bag before
   using its camera near soldered boards.
3. For any header already soldered, use phone zoom to inspect every joint.
   Check continuity from each pad to its pin, no persistent short between
   adjacent pins, and no persistent short from the module's supply to ground.
4. Count only the pins still missing. A completely bare set needs 26 pins:
   16 + 4 + 6. Only 22 loose pins are confirmed in the purchase record.
5. If you do not have enough usable pins for the missing positions, stop here
   and obtain extra
   [Sullins PRPC040SAAN-RC 1×40 male breakaway headers](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PRPC040SAAN-RC/2775214).
   This exact current candidate is not recorded as bought.

### PASS 5A

- [ ] Every already-soldered header passes inspection and unpowered tests. If
      all 26 positions are already good, go directly to Step 6. Otherwise you
      found enough pins for the missing positions plus safety glasses,
      electronics flux, iron and stand, silicone mat, ventilation, meter, and
      practice material.

If every header was already good, wash your hands before removing the phone
from its bag, then continue to Step 6.

If you have no practice material, use a cheap
[2.54 mm perfboard](https://www.amazon.com/s?k=2.54mm+perfboard+prototype)
rather than making a project module your first attempt. This is a candidate
search, not a recorded purchase.

### Stop-safe rule for every soldering pause

If you end a work session after PASS 5B, 5C, 5D, or 5E, the safe shutdown is
part of that pass:

1. Switch off and unplug the iron.
2. Leave it untouched in its stand until fully cool.
3. Clean the mat and work area without handling hot waste.
4. Wash your hands before removing the phone from its bag or touching food.

### Step 5B — make three practice joints

1. Unplug USB. Keep all lithium batteries outside the work area.
2. Put on eye protection. Use the silicone mat and ventilation that moves
   fumes away from your face. Keep food and drink away. If you will use phone
   zoom, put the phone in a clean clear bag before handling solder.
3. Use only the electronics flux pen. Keep the Harris acid brass flux sealed
   in its separate storage container.
4. Set the iron to about 340 °C and keep it in its stand when not in use.
5. Clean and lightly tin the tip.
6. Touch the tip to the practice pad and pin together. Feed solder to the
   heated joint—not directly onto the tip. Remove the solder, remove the iron,
   and hold the parts still while the joint solidifies.
7. Limit one heating attempt to about 2–3 seconds. If it needs longer, remove
   the iron, let the joint cool, and clean or change the tip before retrying.
8. Inspect with phone-camera zoom. Repeat until three consecutive joints fully
   wet the pad and pin with no bridge or burned material.

#### PASS 5B

- [ ] Three consecutive practice joints pass visual inspection.

If stopping here today, complete the stop-safe rule before leaving the bench.

### Step 5C — solder the controller

If the controller's headers passed Step 5A, leave them alone and continue to
Step 5D. Otherwise:

1. With glasses on, cut two 8-pin header strips.
2. Use the spare 400-point breadboard as a soldering jig if you found it; heat
   can damage its contacts, so keep the 830-point final breadboard away.
   Otherwise use the helping hands.
3. Put the long ends into the jig and place the controller over the short ends.
4. Solder all 16 joints using the Step 5B motion.
5. After it cools, inspect all 16. In unpowered continuity mode, every pad must
   show continuity to its matching pin. Adjacent pins and `3V3` to `GND` must
   not show a persistent steady tone or near-zero resistance.

#### PASS 5C

- [ ] All 16 controller joints and unpowered checks pass.

If stopping here today, complete the stop-safe rule before leaving the bench.

### Step 5D — solder the OLED

If the OLED header passed Step 5A, leave it alone and continue to Step 5E.
Otherwise:

1. Cut one 4-pin strip and solder all four joints using the same jig and motion.
2. After it cools, inspect all four. Every pad must show continuity to its
   matching pin. Adjacent pins and `VCC` to `GND` must not show a persistent
   steady tone or near-zero resistance.

#### PASS 5D

- [ ] All four OLED joints and unpowered checks pass.

If stopping here today, complete the stop-safe rule before leaving the bench.

### Step 5E — solder the microphone

If the microphone header passed Step 5A, leave it alone, complete the stop-safe
rule if the iron was used, and finish Step 5. Otherwise:

1. Count the module's header rows before cutting anything. The common INMP441
   breakout carries its six positions as **two rows of three on opposite
   edges**, not one row of six. Cut strips to match the board in front of you,
   not this sentence. Do not let flux, solder, solvent, glue, compressed air,
   or hot air touch or enter the microphone's acoustic port.
2. Write down the label printed beside every pad, edge by edge, before you
   solder. Step 8 wires this module by label, and vendors change layouts
   without changing the product photo.
3. Solder all six joints using the same motion. Jig a two-row module the way
   you jigged the controller: the pin rows straddle the breadboard's center
   trench so the two sides stay electrically separate.
4. After it cools, inspect all six. Every pad must show continuity to its
   matching pin. Adjacent pins within a row, and `VDD` to `GND` wherever those
   two sit, must not show a persistent steady tone or near-zero resistance.
5. Complete the stop-safe rule before leaving the bench.

A brief meter chirp can be a capacitor charging. A persistent near-zero
reading or steady tone between supply and ground is a stop condition.

#### PASS 5E

- [ ] All six microphone joints and unpowered checks pass; the unplugged iron
      is fully cool in its stand or stored; the area and final breadboard are
      clean; and hands are washed.

### If it does not pass

1. Do not power the module.
2. Reinspect the failed joint with phone-camera zoom.
3. Let the joint cool. For a dry joint, add electronics flux and repeat one
   brief 2–3 second heating attempt.
4. For excess solder, stop if you do not have solder wick. If you do, add
   electronics flux, hold the wick with tweezers because it gets hot, heat it
   on the joint for at most 2–3 seconds, then lift the iron and wick together
   without dragging. Let everything cool before reinspecting.
5. Quarantine the module if a pad lifts, the microphone port is contaminated,
   or one careful rework attempt does not fix it. Use another module only if
   you actually found a packaged spare.

Wash your hands before removing the phone from its bag or touching food.

Put the soldering tools away before beginning the breadboard steps.

Optional theory: [why solder joints and continuity checks matter](FAST_TRACK_THEORY.md#step-5--soldering-and-connections).

---

## Step 6 — add only the button

### Take out

- Flashed board `A1`, its data cable, and the clean 830-point final breadboard.
  Do not use the 400-point board that may have been heated as a soldering jig.
- Four short male-to-male Dupont jumpers.
- One [QTEATAK tactile button](https://www.amazon.com/dp/B0FHW6HMG4).
- The [KAIWEETS meter](https://www.amazon.com/dp/B08BL288LW).

The REXQualis breadboards and TODOELEC 10 cm jumper kit are recorded as
purchased, but their exact order links were not saved. These
[breadboard search results](https://www.amazon.com/s?k=REXQualis+830+400+breadboard)
and [jumper search results](https://www.amazon.com/s?k=TODOELEC+10cm+Dupont+jumper+120)
are only for comparing package names and photos.

### Do

1. Unplug USB.
2. Place board `A1` across the breadboard's center gap so its two header rows
   are on electrically separate sides and its USB connector remains reachable.
3. Learn this breadboard before powering it. Each ordinary group of five holes
   should be connected; the group across the center trench should not be. Long
   side rails may be split halfway. Use continuity mode to map the exact rail
   segments you will use.
4. Choose one side-rail segment for `3V3` and a separate segment for `GND`.
   Wire controller `3V3` to the first and controller `GND` to the second with
   male-to-male jumpers. A red or blue stripe is only a label, not proof.
5. With USB still unplugged, prove continuity from the controller pin to each
   point you plan to use on its rail. Then check between the two rails: a brief
   chirp can be capacitance, but a persistent tone or near-zero resistance is a
   stop condition.
6. Seat the button so its two contacts land in two different breadboard
   nodes. A four-leg tactile button has two permanently joined leg pairs, and
   pressing bridges one pair to the other. Straddling the center trench does
   this when the legs reach across it; if they do not, place the button on one
   side with each joined pair inside a single column and the two pairs in
   different columns. Then, with the meter probes in the holes you will wire
   from, confirm those two nodes are open when released and connected only
   while pressed.
7. Wire exactly this:

   | Button | Connection |
   | --- | --- |
   | One tested switched contact | GPIO10 |
   | Other tested switched contact | verified `GND` rail |

   The power branches created here are:

   ```text
   controller 3V3 ── 3V3 rail ── later: OLED VCC, mic VDD, 10 kΩ
   controller GND ── GND rail ── button, later: OLED GND, mic GND/L-R, 100 kΩ
   ```

8. Recheck the rail mapping, both power jumpers, the button wires, and rail
   isolation. Then reconnect USB.
9. Reopen the monitor:

   ```bash
   . firmware/.work/esp-idf/export.sh
   python3 tools/pocket_ai_device.py monitor --port /dev/ttyACM0
   ```

10. Press the external button slowly ten times.

### PASS

- [ ] Both rails map correctly, there is no persistent supply-to-ground short,
      ten deliberate presses produce ten increasing `BUTTON GPIO10: click N`
      messages, and the board still boots normally.

### If it does not pass

1. Unplug USB before changing anything.
2. If it always reads pressed, a permanently joined leg pair is spanning two
   nodes and the breadboard is shorting the two contacts together. Lift the
   button, turn it 90°, and repeat the unpowered test at the holes.
3. Confirm the wire says GPIO10. Do not use the onboard GPIO9 **BOOT** button.

Keep the working button connected for the next step.

Optional theory: [how a button becomes a digital input](FAST_TRACK_THEORY.md#step-6--button-and-digital-input).

---

## Step 7 — add the OLED display

### Take out

- One soldered [Hosyond SSD1306 OLED](https://www.amazon.com/dp/B09T6SJBV5).
- Four short male-to-male jumpers. If you found more OLEDs, keep one packaged
  as a possible swap spare.

### Do

1. Unplug USB.
2. Read the labels printed on your exact OLED. Identical-looking boards can
   reverse `VCC` and `GND`; never copy their physical order from a photo.
3. Put the OLED in unused breadboard rows with each pin in a different
   five-hole node. Keep the glass visible and do not let the module touch the
   controller or button.
4. Wire by **label**:

   | OLED label | Connection |
   | --- | --- |
   | `GND` | verified `GND` rail |
   | `VCC` | verified `3V3` rail |
   | `SCL` | GPIO20 |
   | `SDA` | GPIO21 |

5. Compare all four wires with the table. Confirm that every used point on each
   rail connects to its controller pin and that `3V3` and `GND` do not have a
   persistent continuity tone or near-zero resistance.
6. Reconnect USB and reopen the monitor:

   ```bash
   . firmware/.work/esp-idf/export.sh
   python3 tools/pocket_ai_device.py monitor --port /dev/ttyACM0
   ```

7. Tap the controller's **RESET** button once so the open monitor captures the
   complete startup log. Do not hold the GPIO9 **BOOT** button.
8. Watch startup, then press the external GPIO10 button ten times.

### PASS

- [ ] The log reports OLED address `0x3C` or `0x3D`, startup reports
      `OLED: ALL ON` and `OLED: ALL OFF`, and ten button presses toggle the
      pixels without resets.

### If it does not pass

1. Unplug USB immediately and reread the actual `VCC` and `GND` labels.
2. Confirm `SCL → GPIO20` and `SDA → GPIO21`; then inspect the four solder
   joints and breadboard rows.
3. Only after the wiring passes those checks, try another OLED if you actually
   found a packaged spare; otherwise stop and record the failure.

Keep the working button and OLED connected.

Optional theory: [how I2C addresses and the OLED work](FAST_TRACK_THEORY.md#step-7--i2c-and-the-oled).

---

## Step 8 — add the microphone

### Take out

- One soldered [AITRIP INMP441 microphone](https://www.amazon.com/dp/B092HWW4RS).
- Six short male-to-male jumpers.
- One 10 kΩ and one 100 kΩ resistor from the recorded
  [LuminologyPro resistor kit](https://www.amazon.com/dp/B0F4P352BB).
- The meter.

### Do

1. Unplug USB.
2. Keep fingers, flux, solvent, glue, hot air, and compressed air away from
   the microphone's acoustic port.
3. With both resistors still loose, set the unplugged meter to resistance
   (`Ω`) mode and measure them one at a time. Accept and label the pull-up only
   if it reads roughly 9–11 kΩ; accept and label the pull-down only if it reads
   roughly 90–110 kΩ. Do not trust only the color bands or kit compartment.
   Resistors are not polarized, so either end may face either way.
4. Put the microphone in unused breadboard rows with every pin in a different
   five-hole node. Its acoustic port must face open air; if the port is on the
   underside, keep a clear air gap rather than pressing it against the
   breadboard or table.
5. Read the microphone's actual labels and wire:

   | Microphone label | Connection |
   | --- | --- |
   | `VDD` or `VCC` | verified `3V3` rail |
   | `GND` | verified `GND` rail |
   | `L/R` | verified `GND` rail |
   | `SCK` or `BCLK` | GPIO2 |
   | `WS` | GPIO1 |
   | `SD` | GPIO4 |

6. Add the two measured stability resistors:

   | Resistor | Connect between |
   | --- | --- |
   | measured 9–11 kΩ pull-up | GPIO2 and verified `3V3` rail |
   | measured 90–110 kΩ pull-down | GPIO4 and verified `GND` rail |

7. There must be no microphone wire on GPIO8. GPIO8 belongs only to the
   historical vendor firmware, which this guide does not use.
8. Compare all eight new connections with the tables and keep the I2S jumpers
   short. With USB still unplugged, prove both rail segments still connect to
   the correct controller pins. Confirm that `3V3` and `GND` do not have a
   persistent tone or near-zero resistance.
9. Reconnect USB and reopen the monitor:

   ```bash
   . firmware/.work/esp-idf/export.sh
   python3 tools/pocket_ai_device.py monitor --port /dev/ttyACM0
   ```

10. Read the once-per-second `MIC24` lines. Confirm `samples` is nonzero,
    `min` and `max` differ, and `read_errors=0`. One nonzero error can be a
    transient, but recurring nonzero errors fail this step.
11. For each trial, write down one quiet `rms` value, speak normally from the
    same distance, and write down one speech `rms` value:

    | Trial | Quiet `rms` | Speech `rms` |
    | --- | --- | --- |
    | 1 |  |  |
    | 2 |  |  |
    | 3 |  |  |

12. Press the external button and confirm the OLED still toggles.

### PASS

- [ ] `samples` is nonzero, `min` and `max` differ, recurring nonzero
      `read_errors` are absent, and the recorded speech `rms` is higher than
      quiet in all three trials. The button and OLED still pass.

There is no universal good `rms` number. The repeatable change between quiet
and speech is the result that matters.

### If it does not pass

1. Unplug USB. Confirm `SD → GPIO4`, `L/R → GND`, and a common ground. If
   `samples` counts up but `min` and `max` both stay at `0` with
   `read_errors=0`, that is the slot-mismatch signature: the mic is talking in
   the other slot, not broken. Recheck `L/R → GND` before suspecting a joint.
2. Confirm `SCK → GPIO2`, `WS → GPIO1`, and both resistor values/endpoints.
3. Inspect all six microphone header joints before trying another microphone,
   and do that only if you actually found a packaged spare.

Optional theory: [how the microphone turns sound into numbers](FAST_TRACK_THEORY.md#step-8--i2s-microphone-and-rms).

---

## Step 9 — prove the complete USB prototype

### Do

1. Save one clear overhead photograph that shows every wire and every board
   label.
2. For **cold start 1**, exit the monitor with `Ctrl+]` and unplug USB. Check
   that `3V3` and `GND` have no persistent continuity tone, then wait five
   seconds.
3. Reconnect USB. Watch the OLED perform its startup test, then open the
   monitor:

   ```bash
   . firmware/.work/esp-idf/export.sh
   python3 tools/pocket_ai_device.py monitor --port /dev/ttyACM0
   ```

4. Watch for 60 seconds without another boot sequence. Press the external
   button three times, confirm three clicks and OLED toggles, then record one
   quiet and one speech `rms` value.
5. For **cold start 2**, exit the monitor, unplug USB, repeat the unpowered
   rail check, and wait five seconds.
6. Reconnect USB, watch the OLED startup test, and reopen the monitor:

   ```bash
   . firmware/.work/esp-idf/export.sh
   python3 tools/pocket_ai_device.py monitor --port /dev/ttyACM0
   ```

7. Repeat the same 60-second, three-click, OLED, quiet, and speech tests.
8. Save the final log next to the wiring photograph.

### PASS — USB hardware prototype complete

- [ ] Cold start 1 and cold start 2 both boot without a reset loop; the
      external button logs all presses; the OLED starts and toggles; and speech
      produces a higher microphone RMS than quiet.

You have now built a real working hardware prototype. Keep it on the
breadboard in a tray; do not pocket-carry the loose assembly.

If a cold start fails, unplug USB first. Remove the microphone and its two
resistors, then confirm the button/OLED layer still passes. Remove the OLED
next only if that earlier layer also fails. Use the
[technical quickstart](../docs/PROTOTYPE_QUICKSTART.md) plus the saved photo to
find the first difference.

Optional theory: [why repeatability matters](FAST_TRACK_THEORY.md#step-9--integration-and-repeatability).

---

## Step 10 — optional, experimental networked assistant

Stop here unless Step 9 passes and you deliberately accept the privacy tradeoff.
Assistant mode uses the third-party Xiaozhi/Tenclass bootstrap service, which
receives device metadata and microphone audio. Do not continue if that is not
acceptable to you.

The amplifier remains disabled, so this experiment does **not** produce spoken
output. Its goal is only one successful backend round trip visible in the log
or display. This cloud path returned one remote response on board `A1` on
2026-09-21 (builder-reported), and it can change when the third-party service
changes.

> **Provisioning warning:** the temporary configuration network is open and
> the form at `http://192.168.4.1` is not encrypted. A nearby person could
> observe or interfere. Provision only in a private location and use a
> dedicated 2.4 GHz guest/IoT network with a unique password—not the password
> for an important network or account. The firmware stores those credentials
> unencrypted in flash settings. A reset does not erase them; the board retains
> them until a full reflash or flash erase.

> **Radio note for this board:** the SuperMini's ceramic chip antenna is poorly
> matched. At the firmware's default 20 dBm transmit power the setup hotspot
> was invisible on three boards from this batch, including `A1`, even with the
> phone touching the board. The assistant build therefore caps Wi-Fi transmit
> power at 8.5 dBm on this board, once for the setup hotspot and once for the
> normal connection, and prints a log line each time. That is **lower** power,
> not higher: the `34` in the source is in quarter-dBm units. Expect short
> range. Keep the phone within about a metre of the antenna end (the end
> opposite USB) during setup, and keep that end clear of wires and metal.

### Do

1. Read the [assistant-mode privacy and provisioning notes](../firmware/README.md#flash-and-monitor-source-builds).
2. Prepare the dedicated 2.4 GHz guest/IoT network described above, and
   confirm on the router that it broadcasts on 2.4 GHz. The ESP32-C3 cannot
   see 5 GHz networks at all.
3. Leave the Step 9 wiring exactly as it passed. Add nothing.
4. With the existing USB-only hardware, build assistant mode:

   ```bash
   . firmware/.work/esp-idf/export.sh
   firmware/scripts/build.sh --assistant
   ```

   If that command prints an error, stop. Do not run a later command using an
   older artifact.

5. After the build succeeds, verify it:

   ```bash
   python3 firmware/scripts/verify_source_build.py
   ```

   Stop unless it prints `Build mode: assistant; amplifier: disabled` without
   an error.

6. Preview the flash using the exact port from Step 3:

   ```bash
   firmware/scripts/flash.sh /dev/ttyACM0 --dry-run
   ```

### PASS 10A — safe to flash assistant mode

- [ ] The build and verifier finished without errors, the verifier and preview
      print `Build mode: assistant; amplifier: disabled`, and the preview names
      the exact port from Step 3.

### Do, after PASS 10A — find the hotspot and hand over the network

7. Flash and open the monitor:

   ```bash
   . firmware/.work/esp-idf/export.sh
   firmware/scripts/flash.sh /dev/ttyACM0 --monitor
   ```

8. In the boot log, find these three lines in this order. Other lines appear
   between them, and the numbers in parentheses vary. Write down the exact
   hotspot name; its last four characters differ per board.

   ```text
   I (…) WifiManager: Starting config AP
   I (…) WifiConfigurationAp: Access Point started with SSID Xiaozhi-XXXX
   I (…) WifiBoard: Wi-Fi max TX power capped at 8.5 dBm (provisioning AP)
   ```

   If the third line is missing, the board is running an older image at full
   power, which is the exact condition that was invisible on this batch. Go
   back to item 4 and rebuild.

9. The OLED shows the Wi-Fi configuration screen with the same hotspot name
   and the address `http://192.168.4.1`.
10. On the phone, turn mobile data off so the captive portal is not bypassed.
    Hold the phone within about 30 cm of the board's antenna end, open the
    Wi-Fi list, and wait up to 30 seconds. Pull down to rescan if the list
    does not refresh. The hotspot is open, with no password. Join it, and if
    the phone warns that the network has no internet, choose to stay
    connected.
11. If the captive portal does not open by itself within 15 seconds, open a
    browser and go to `http://192.168.4.1`.
12. In the form, choose your dedicated **2.4 GHz** guest/IoT network from the
    scanned list, type its password, and submit. The board switches to that
    network's channel to test the credentials. If the router refuses the first
    attempt, the firmware waits three seconds and tries once more by itself,
    so wait for the page's result before touching anything. The phone drops
    off the hotspot when the board reports success; that is expected.
13. Back in the monitor, find these lines in this order:

    ```text
    I (…) WifiBoard: Starting WiFi connection attempt
    I (…) WifiBoard: Wi-Fi max TX power capped at 8.5 dBm (station)
    I (…) WifiBoard: Connected to WiFi: <your guest network>
    ```

    If the board instead logs `WiFi connection timeout, entering config mode`,
    it could not reach the router at 8.5 dBm. Move the board and the router
    into the same room and repeat from item 10.

### PASS 10B — the board is on your network at capped power

- [ ] The hotspot appeared on the phone, the form accepted the guest network,
      and the monitor shows the station cap line followed by
      `Connected to WiFi: <your guest network>` without a reset. Record the
      hotspot name, the network name, and the time.

### Do, after PASS 10B — activation and one round trip

14. Keep watching the monitor and the OLED. Once on the network the firmware
    contacts the third-party bootstrap service. `Ota: Activation successful`
    in the log means the service already knows this board. Otherwise the
    display or log shows an activation instruction, usually a short code to
    enter on the service's own site. That flow belongs to the third party and
    may change independently of this repository. Enter the code only on the
    service's own activation page.
15. Give the external GPIO10 button one quick press. When the log or display
    shows that it is listening, ask one short question such as "What is two
    plus two?" Wait for a remote response to appear in the log or display.
    Quick-press the button once more if the interface remains active.

### PASS 10C — one assistant round trip

- [ ] Your quick press starts listening, and one spoken question produces a
      remote response in the display or serial log without a reset. Record the
      evidence: the log excerpt and a photograph of the display.

### If the hotspot never appears

Work down this list and stop at the first item that changes the result.

1. Confirm the `(provisioning AP)` cap line from item 8 is in the boot log.
   Without it the board is transmitting at 20 dBm.
2. Move the phone to within 30 cm of the antenna end, force a rescan, and
   wait 30 seconds. Check that no jumper wire crosses the antenna end.
3. Flash the same image onto a bare spare board lying on an open desk. If the
   spare's hotspot appears and `A1`'s does not, the breadboard wiring is
   crowding the antenna. If neither appears, the 8.5 dBm cap is not enough
   for your boards.
4. The remaining fixes are hardware: the 31 mm wire antenna mod, or a board
   with a real antenna socket. Both are described in the controller entry of
   the [inventory](../docs/INVENTORY.md). The second changes the pin map and
   is not a drop-in swap.

### Return to offline diagnostics

Return to offline diagnostics whenever you need to isolate a hardware problem.
Build first:

```bash
. firmware/.work/esp-idf/export.sh
firmware/scripts/build.sh --diagnostics
```

If the build prints an error, stop. After it succeeds, verify it:

```bash
python3 firmware/scripts/verify_source_build.py
```

Continue only when it prints `Build mode: diagnostics; amplifier: disabled`.
Preview the exact port:

```bash
firmware/scripts/flash.sh /dev/ttyACM0 --dry-run
```

Continue only when the preview repeats diagnostics mode, disabled amplifier,
and the right port. Then flash:

```bash
firmware/scripts/flash.sh /dev/ttyACM0 --monitor
```

That full diagnostic reflash writes this project's blank NVS area and clears
the saved Wi-Fi settings. Do not loan, sell, or discard a provisioned board
until that reflash succeeds or you deliberately erase its flash.

Optional theory: [what changes when the cloud is added](FAST_TRACK_THEORY.md#step-10--network-and-cloud-boundary).

## Stop here before speaker, battery, or brass

Those are separate projects, not additional beginner steps:

| Later milestone | Why it waits | Read before beginning |
| --- | --- | --- |
| Powered amplifier and speaker | Output power, I2S slot behavior, mute timing, and bridge-tied speaker leads still require bench qualification | [Speaker theory](concepts/10-speakers-and-amplifiers.md) and [current promotion gates](../docs/FINAL_MATERIALS_FOR_REVIEW.md#promotion-gates-before-claude-may-say-final-go) |
| Portable power and charging | USB back-power, regulator startup, current, thermal behavior, fuse choice, and charging isolation are unresolved | [Power theory](concepts/13-power-integrity.md) and [current power architecture](../docs/FINAL_MATERIALS_FOR_REVIEW.md#candidate-power-architecture) |
| Enclosure and brass frame | The existing CAD models an old architecture; real parts must be measured and mocked up first | [Fit theory](concepts/14-fit-and-radio.md) and [CAD status](../cad/README.md) |

Buying or finding those parts does not release them for connection. The USB
prototype is the complete fast-track win.
