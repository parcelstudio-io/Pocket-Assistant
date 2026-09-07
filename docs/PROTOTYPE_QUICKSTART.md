# USB prototype quickstart

Start here to make the parts you own do something observable. The first goal
is a USB-powered controller that logs button presses, tests the OLED, and
reports microphone levels. The default source build includes these offline
diagnostics, so this first prototype needs no cloud account or speaker.

This is a bring-up procedure, not a claim that the physical parts have already
passed it. Record your own results. The battery, charger, amplifier, speaker,
and brass enclosure are later integration work.

## Prepare what you already own

| Item | Recorded purchase link | Needed for |
| --- | --- | --- |
| Plain ESP32-C3 SuperMini | [Meshnology 10-pack](https://www.amazon.com/dp/B0F888JQ91) | First boot and all later steps |
| USB data cable | [Rankie USB-A-to-C](https://www.amazon.com/dp/B01JRY0VE4) | Power, flashing, serial output |
| Multimeter | [KAIWEETS HT118A](https://www.amazon.com/dp/B08BL288LW) | Unpowered continuity and voltage checks |
| Tactile button | [QTEATAK kit](https://www.amazon.com/dp/B0FHW6HMG4) | GPIO input and OLED test control |
| SSD1306 OLED | [Hosyond 0.96-inch](https://www.amazon.com/dp/B09T6SJBV5) | Pixel test |
| INMP441 microphone | [AITRIP pack](https://www.amazon.com/dp/B092HWW4RS) | Microphone levels |
| Breadboard, jumpers, and headers | REXQualis, TODOELEC, and breakaway headers; exact URLs not recorded | Reliable peripheral connections |
| Soldering setup if headers are loose | See [Day 11 materials](../plan/DAILY_STUDY_AND_LAB_PLAN.md#day-11--soldering-practice-before-project-hardware) | Header preparation |

Use an existing computer and notebook. Check which ordered items have arrived;
start with just the controller and cable if peripherals are still boxed or
their headers need preparation. No additional parts are prescribed here.

Use the controller's USB cable as the only power source. Its **3.3 V output**
may supply the OLED and microphone; it must not be connected to a separate
power source, converter, charger, or battery. Unplug USB before each wiring
change and before continuity/resistance measurements. Measure voltage with
the meter leads in COM and the voltage jack. Keep amplifier wiring absent.

## Boot the controller

Read [Lesson 00](../edu/fundamentals/00-safety-evidence-and-course-map.md) and
the pin-identification portion of
[Lesson 04](../edu/fundamentals/04-boards-schematics-datasheets-and-connectors.md)
as needed. You do not need to finish the electronics course first.

Label one plain SuperMini `A1` and photograph its two sides. Leave it bare,
including no button or peripheral wiring, for the first flash.

In Bash, from the repository root:

```bash
firmware/scripts/setup.sh
. firmware/.work/esp-idf/export.sh
firmware/scripts/build.sh
python3 firmware/scripts/verify_source_build.py
```

Setup downloads the pinned ESP-IDF toolchain and Python tools. The first run
requires internet access and may take much of a session. The
[firmware guide](../firmware/README.md) explains prerequisites and build
troubleshooting. In a new terminal, activate that same `export.sh` before
building or flashing again.

The default build is **offline diagnostics**; `build.sh --diagnostics` is an
explicit equivalent. It runs without Wi-Fi provisioning, cloud audio, or an
amplifier. The verifier checks the actual built artifact and its source inputs;
resolve a failure before flashing.

Connect the bare board by USB and list its port:

```bash
python3 tools/pocket_ai_device.py ports
```

Use the port that actually appeared. In the following commands replace
`/dev/ttyACM0` with that exact port if different:

```bash
python3 -m esptool --chip esp32c3 --port /dev/ttyACM0 flash-id
firmware/scripts/flash.sh /dev/ttyACM0 --dry-run
firmware/scripts/flash.sh /dev/ttyACM0 --monitor
```

Require an ESP32-C3 with at least 4 MB flash. The flash writes a complete merged
image and clears saved Wi-Fi settings. If automatic bootloader entry fails,
hold the onboard **BOOT** button (GPIO9), tap RESET, release BOOT, and retry.
Close other serial monitors before flashing.

Look for `BENCH DIAGNOSTICS: offline; Wi-Fi/cloud off; amplifier GPIO5 LOW`.
Save the boot log. Missing-display and meaningless microphone readings are
expected with no peripherals attached. The first success is a stable
diagnostic loop, with no repeated resets. Label your board record
`SOURCE DIAGNOSTICS / MIC GPIO4 / 16 kHz`.

To reopen logs later without flashing:

```bash
python3 tools/pocket_ai_device.py monitor --port /dev/ttyACM0
```

## Prepare reliable headers

Unplug USB. Inspect the controller, OLED, and microphone: some modules arrive
with loose header strips that are not electrically attached. Pushing those
pins through unsoldered holes is not a reliable connection.

If the required headers are already soldered, inspect for bridges and verify
continuity from each used pin to its labeled pad. Otherwise complete the
[Day 11 solder practice](../plan/DAILY_STUDY_AND_LAB_PLAN.md#day-11--soldering-practice-before-project-hardware)
before proceeding. Then solder the required header joints, one module at a
time, using electronics flux and the handling instructions in
[Lesson 12](../edu/fundamentals/12-soldering-mechanics-insulation-tolerance.md).
Inspect the joints and adjacent-pin isolation before powering up. Keep solder,
flux, solvent, glue, and hot air away from the microphone port.

Check the breadboard's connected rows and any split power rails with continuity
mode. Wire by the labels on the received board, not by its position in a photo.

## Add the button and OLED

Add the button first, then add the display after button presses appear in the
serial log. Unplug USB for each change. Read the relevant portions of
[Lesson 07](../edu/fundamentals/07-digital-logic-gpio-pullups-boot-straps.md) and
[Lesson 08](../edu/fundamentals/08-i2c-and-the-oled.md) just before those tests.

| Peripheral terminal | Controller connection |
| --- | --- |
| Button, one switched contact | GPIO10 |
| Button, other switched contact | GND |
| OLED GND | GND |
| OLED VCC, after confirming 3.3 V compatibility | 3.3 V output |
| OLED SCL | GPIO20 |
| OLED SDA | GPIO21 |

Use continuity mode to identify the button's two switched contacts. A four-leg
tact switch often has pairs of legs permanently connected; choosing two legs
in the same pair would hold the input active. The diagnostic firmware supplies
the internal GPIO10 pull-up. Keep the onboard GPIO9 button for ROM recovery.

OLED carriers can reverse VCC/GND pin order. Identify the actual labels before
wiring, then check for supply shorts. Reconnect USB and look for the detected
`0x3C` or `0x3D` address in the log. The boot test first reports `OLED: ALL ON`
and then `OLED: ALL OFF`. Each GPIO10 press logs `BUTTON GPIO10: click N` and
switches the pixel test between those states. Test ten presses, then unplug/reconnect USB
and repeat. Save a photograph and the serial output.

If the display is absent or fails, the diagnostic loop should still run.
Unplug USB and check VCC/GND, SDA/SCL, header joints, and breadboard rows before
changing firmware. An ACK proves an I²C response; the pixel test provides
separate evidence that the display initializes and lights correctly.

## Add the microphone

Read the samples, slots, and clocks sections of
[Lesson 09](../edu/fundamentals/09-i2s-sampling-and-digital-audio.md). Unplug USB
and identify the INMP441 carrier's actual pin labels and 3.3 V compatibility.
Use short jumpers:

| INMP441 terminal | Controller connection |
| --- | --- |
| VDD / VCC | 3.3 V output |
| GND | GND |
| L/R | GND, selecting the left slot |
| SCK / BCLK | GPIO2 |
| WS | GPIO1 |
| SD, the microphone data output | GPIO4 |

The OLED and button may stay connected after their individual tests pass. No
microphone wire connects to GPIO8; that is the historical vendor firmware's
different contract.

Reconnect USB and watch the once-per-second `MIC24` statistics: `samples`,
`min`, `max`, `rms`, `zero`, `same`, `clipped`, and `read_errors`. These describe
signed 24-bit sample values before application gain; RMS is a relative digital
level, not volts or calibrated sound pressure. Record about
ten seconds of quiet, speak normally at a fixed distance, then become quiet
again. Repeat a few times. Successful capture should show a repeatable change
with your voice, without stuck readings or repeated read failures. Ambient
noise means silence need not read zero. There is no universal RMS pass number
for all distances, rooms, and microphones.

If readings remain stuck, unplug USB and check power, common ground, L/R, data
GPIO4, and the two clock connections. Restore all connections before applying
power. A logic analyzer is optional for confirming the expected 16 kHz WS and
1.024 MHz BCLK; do not buy one merely to observe microphone activity.

## What this proves and what comes next

After a cold USB start, reproduce the button log, OLED pixel toggle, and
microphone level changes together. Save the firmware identity, wiring
photograph, and log. That is a useful working local prototype; it does not
establish speaker output, cloud conversation, runtime, or enclosure fit.

For a later backend experiment, build the regular application explicitly:

```bash
firmware/scripts/build.sh --assistant
python3 firmware/scripts/verify_source_build.py
firmware/scripts/flash.sh /dev/ttyACM0 --monitor
```

Use the actual port. The tested button, OLED, and microphone may remain
connected while flashing when they use only the controller's GPIO, GND, and
3.3 V output. Keep the battery, charger, external regulators, amplifier, and
all separately powered wiring disconnected. Unplug USB before any wiring
change; reflashing alone does not require rebuilding the tested harness.
Read the [firmware guide](../firmware/README.md) before provisioning Wi-Fi: the
regular application's default backend receives device metadata and microphone
audio. Amplifier enable remains disabled by default; this change alone does
not create spoken output. Return to the diagnostics build whenever you need
to isolate a local hardware problem.

Continue the [2–3 hour daily plan](../plan/DAILY_STUDY_AND_LAB_PLAN.md) around
these experiments. Keep battery and brass work separate until there is a
concrete power and mechanical design for the received parts. The existing
[CAD status](../cad/README.md) explains why its old passing fit report cannot
be used to cut this prototype's frame.
