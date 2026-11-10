# Staged build plan

The design is intentionally gated: prove alarm reliability first, then add the cell and charger board, then the printed body and its two brass cradles. Each phase ends with evidence that justifies the next wiring or fabrication step.

Rev B 2026-10-31: solar removed, compact body, 16340 cell. Phase 5 is no longer a solar experiment; Phase 6 builds the 82 × 52 × 68 mm body of [COMPACT_DESIGN.md](COMPACT_DESIGN.md).

## Phase 0 — Freeze the prototype decisions

Actions:

- Confirm the 2.42-inch OLED's received controller revision and logic/power requirements.
- Confirm the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) is the 8 MB flash / 8 MB PSRAM variant and inspect its schematic/pin conflicts.
- Print paper outlines for the OLED, the speaker, the 16340 holder, the controller board and the 82 × 52 mm face.
- Decide whether conventional phone-music streaming is actually required. If yes, create a separate SoundDock target on the [Wi-Fi and Bluetooth Feather board](https://www.adafruit.com/product/5400) now rather than changing MCU halfway through.

Gate:

- Signed-off baseline is either “S3 local audio” or “classic ESP32 A2DP variant.”
- Mechanical mockup shows the cell swaps with the lid off and the boards come out with the rear panel off, without touching the brass cradles.

Purchase after gate: core USB bench order only.

## Phase 1 — USB bench alarm

Build:

- [Controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894), [real-time clock](https://www.adafruit.com/product/5188) with its [coin cell](https://www.amazon.com/dp/B0D8T4C5PK), [amplifier](https://www.adafruit.com/product/3006) and [speaker](https://www.adafruit.com/product/1669), [OLED display](https://www.adafruit.com/product/2719), [rotary encoder](https://www.adafruit.com/product/6310), [snooze button](https://www.adafruit.com/product/1505), [arm switch](https://www.adafruit.com/product/805).
- Use insulated jumpers or a [solder-in proto board](https://www.adafruit.com/product/1609); no free-wire power construction yet.
- Implement real-time clock UTC read/write, one recurring alarm, fallback tone, snooze, dismiss, and basic OLED status.

Tests:

- Unplug router and phone.
- Reset 60 seconds before alarm and while ringing.
- Corrupt/remove the selected audio asset.
- Leave it operating for 72 hours and compare the real-time clock against system time.

Gate:

- 30 consecutive clock-triggered alarms sound without network.
- Reset cannot silently cancel ringing or snooze.
- Fallback tone works with filesystem/audio asset failure.
- Dedicated snooze responds within 100 ms after debounce.

## Phase 2 — Scheduler and local setup

Build:

- Multiple alarms, weekday masks, volume ramp, arm state, persisted snooze.
- Timezone-aware scheduler and defined DST policies.
- BLE provisioning and/or local setup portal, then SNTP.
- Local LAN web UI for alarms and status.

Tests:

- Host-unit tests for leap years, month/year rollover, DST gap/repeat, NTP jumps, and simultaneous alarms.
- Thousands of accelerated recurrence calculations.
- Disable Wi-Fi during setup, boot, and alarm events.

Gate:

- All calendar vectors pass.
- No network operation blocks alarm/input tasks.
- Credentials are absent from source and logs.

## Phase 3 — OLED life and sensing

Build:

- Presence/lux contrast, display blanking, pixel shift, alternate clock faces.
- Temperature/humidity and optional tilt-to-focus interaction.
- Power and fault indicators.

Tests:

- Day/night lux transitions without visible flicker.
- Presence timeout and recovery.
- Missing or stuck I2C sensor.
- Week-long static-pattern/shift test before longer aging work.

Gate:

- Optional sensor failures do not delay alarm boot.
- Night face is legible without excessive brightness.
- No UI element remains fixed at full brightness indefinitely.

Purchase after gate: nothing. The charger board, fuel gauge, 16340 cells and holder are owned ([INVENTORY.md](INVENTORY.md)); they are wired only after this gate.

## Phase 4 — Battery and peak-load validation

Build:

- The [charger board](https://www.adafruit.com/product/6106)'s power path from its own USB-C port; one Nitecore 16340 cell in the [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F) on a JST-PH pigtail, through the [fuel gauge](https://www.adafruit.com/product/5580) into BAT; charger jumper at 500 mA; the solar input left empty.
- Meter the holder leads for polarity before the cell meets anything.
- Safe boot sequencing and normal/eco/reserve power states.
- Fused or current-limited bench setup for initial battery work.

Tests:

- Scope 5 V and 3.3 V during maximum audio, Wi-Fi TX, and OLED update together.
- Cold boot from a low cell and from a current-limited bench supply.
- Measure real 24-hour energy in eco, balanced, and connected modes, and the unplugged runtime with the face dark and lit.
- Unplug and replug USB-C while the clock runs and while it rings; the 5 V rail must not dip below about 3.7 V, the controller regulator's dropout (corrected 2026-10-31 from 4.4 V; REVIEW.md, Rev B verification).

Gate:

- No brownout, audio glitch, or real-time clock corruption at the chosen volume.
- Battery and charger stay within vendor temperature limits.
- Measured unplugged runtime is logged and the battery gauge on the face matches it.
- Low-cell UI warns clearly while alarm reserve is protected.

Purchase after gate: nothing; the body print is Phase 6.

## Phase 5 — A week unplugged and replugged

The solar-sail experiment that lived here was dropped on 2026-10-31. The slot now proves the cell does its one job: ride through unplugs and keep the alarm armed.

Build:

- Log the [fuel gauge](https://www.adafruit.com/product/5580) and the USB-present state locally.
- Keep the bench wiring; no body yet.

Tests:

- Seven days of real bedside use with at least one unplug a day, some of them overnight.
- One full charge of the 16340 from the low-cell warning at the 500 mA jumper; expect about 2.5 h, well inside the [charger board](https://www.adafruit.com/product/6106)'s six-hour timer.
- An alarm that falls during an unplugged night.

Gate:

- No alarm missed while unplugged; the gauge's runtime estimate is honest to within an hour.
- Cell and charger board stay cool to the touch.

## Phase 6 — Acoustic and RF enclosure prototype

Build:

- The compact printed body (82 × 52 × 68 mm, black PETG) with its lid carrying the [snooze button](https://www.adafruit.com/product/1505), the [rotary encoder](https://www.adafruit.com/product/6310) knob and the 5 mm hand-wave hole over the [proximity and light sensor](https://www.adafruit.com/product/4161); the full-face smoked acrylic; the removable rear panel with the USB-C cutout and vents; the right-wall cutout for the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894)'s USB and the [arm switch](https://www.adafruit.com/product/805) on the left wall.
- The [speaker](https://www.adafruit.com/product/1669) flat on the floor over the floor slot, firing into the cradle gap.
- Body on blocks first; the two brass cradles only after the RSSI comparison.

Tests:

- Sweep tones for rattles/distortion; measure alarm level at 1 m and choose a safe maximum.
- Compare Wi-Fi/BLE RSSI and provisioning success bare versus enclosed, amp idle versus active.
- Drop/knock tests appropriate for a desk prototype.
- Verify the cell swaps with the lid off, the coin cell with the rear panel off, and the controller's USB reaches through the right wall.

Gate:

- Audible and adjustable across the intended room without rattles.
- RF margin remains practical; otherwise use the external-antenna module or move the cradles.
- Exposed metal cannot short any live conductor or battery.

Fabricate after gate: bend the two U cradles from the owned [brass tube set](https://www.amazon.com/dp/B0F2FKLC2N), cut the acrylic, fit inserts and screws.

## Phase 7 — Final sculpture and hardening

Build:

- Fit the two electrically isolated brass cradles and the final wiring harness; meter cradle-to-net isolation before power.
- Add strain relief, gaskets, service labels, and thermal separation.
- Add rollback-capable OTA and recovery workflow.

Tests:

- Repeat the complete offline/reset/brownout/audio suite in the final enclosure.
- Fault-inject stuck I2C, corrupt settings/audio, empty clock coin cell, interrupted OTA, and stuck buttons.
- Run a multi-week bedside pilot and record every missed/late event.

Prototype completion criteria:

- No missed alarm in the defined test campaign.
- All alarms remain usable with Wi-Fi/BLE unavailable.
- Runtime claims match logged evidence.
- Battery, charging, speaker, and metalwork remain within tested electrical/thermal limits.
- A second builder can assemble and recover the device from the documentation.

## Risk register

| Risk | Likelihood / impact | Mitigation and decision point |
|---|---|---|
| OLED image retention | Medium / medium | Contrast policy, pixel shift, presence blanking; inspect after aging test |
| [Charger board](https://www.adafruit.com/product/6106) timeout/startup | Low / high | Sequence loads; log status. A 950 mAh cell at 500 mA fills in about 2.5 h, well inside the six-hour timer |
| Brownout during alarm/Wi-Fi | Medium / high | Bulk capacitance, volume cap, rail scope, radio suppression during audio |
| Brass blocks RF | Low / medium | The only brass is two small cradles under the floor; compare RSSI with and without them; external-antenna module option |
| Body fit at zero margin | Medium / low | The main zone's depth closes at 44 of 44 mm on datasheet sizes; lay the real boards in a paper mockup before printing, and grow the body 2 mm if the encoder board is wider than 25 mm |
| Timezone/DST defect | Medium / high | Pure domain module and exhaustive host test vectors |
| Sensor locks I2C | Medium / high | Deadlines, bus recovery, optional power switch/isolation |
| A2DP scope creep | High / medium | Separate SoundDock variant; local-audio S3 remains baseline |
| Accidental alarm dismissal | Medium / high | Dedicated snooze; long-press-and-turn dismiss; physical armed indicator |

## Immediate next actions

1. Order the core USB bench BOM.
2. Install/pin ESP-IDF and add a reproducible build/CI job.
3. Confirm the OLED revision, then make display and real-time clock driver spikes.
4. Build the real-time clock → wake → fallback-tone path before any networking.
5. Print a full-scale paper mockup of the 82 × 52 × 68 mm body and lay the real boards in it while firmware work proceeds.

