# Product brief: Cyber Dawn

## One-line pitch

An offline-first bedside signal terminal, not much bigger than its own screen, that makes time, alarms and room conditions feel like instruments on a tiny spacecraft console.

## Product spin

Cyber Dawn treats the screen as the object. Its dark OLED “horizon” slowly brightens before an alarm; a slim battery gauge at the edge shows how long the clock would last if the cable came out. The object remains calm and mostly black at night, then becomes legible only when a hand passes over the lid or the wake sequence begins.

This is not a cloud clock and not a shrunken smart display. The alarm works with the router and phone turned off. Network features enrich it; they do not own it.

## Physical design

Rev B, 2026-10-31: **82 W × 52 H × 68 D mm**, decided in [COMPACT_DESIGN.md](COMPACT_DESIGN.md). The 165 × 92 × 72 mm envelope of the first brief is withdrawn. The screen is most of the face; the body is a printed black box on two small brass cradles.

```text
 FRONT  82 × 52 mm (one piece of smoked acrylic; the OLED picture is 52 % of it)
 ┌─────────────────────────────────────────┐
 │                                         │
 │    ┌──────────────────────────────┐     │
 │    │                              │     │
 │    │   06:42            [###-]    │     │
 │    │                              │     │
 │    │   ╶────── dawn horizon ────╴ │     │
 │    │                              │     │
 │    │   alarm 07:00          TUE   │     │
 │    │                              │     │
 │    └──────────────────────────────┘     │
 │                                         │
 │                                         │
 └─────────────────────────────────────────┘
   ╰─╯ brass cradle            brass cradle ╰─╯    tilted ~8° toward the pillow

 TOP  82 × 68 mm, lid on, front edge at the bottom (depth foreshortened)
 ┌─────────────────────────────────────────┐  ← rear panel: USB-C, vents
 │                                         │
 │   (●) snooze button           ◉ knob    │  rear row of the lid
 │                                         │
▣│   ○ hand-wave hole      [16340 cell]    │▭  ← controller USB through the right wall
 │                                         │
 ├─────────────────────────────────────────┤  head zone: OLED module and ribbon
 └─────────────────────────────────────────┘  acrylic face
 ▣ arm switch, high on the left wall

 REAR PANEL (removable)  82 × 52 mm
 ┌─────────────────────────────────────────┐
 │   [▭ USB-C]            ≡≡≡ vents        │  charger board left; four small boards right
 │                                         │
 │                        ◯ coin cell      │  real-time clock, coin cell toward the panel
 └─────────────────────────────────────────┘
```

- **Face:** one piece of 3 mm smoked acrylic, the full 82 × 52 mm. The [OLED display](https://www.adafruit.com/product/2719)'s 60 × 37 mm picture is 52 % of it; the 72 × 43 mm module is 73 %. Bezel 11 mm at the sides, 7.5 mm top and bottom.
- **Body:** printed black PETG, 2 mm walls, three depth zones from the front: head 11 mm (OLED and ribbon), main 44 mm, rear 8 mm (boards standing against the rear panel). The lid lifts off for the cell; the rear panel comes off for the coin cell and the boards.
- **Cradles:** two bent brass U cradles of 3 mm tube from the [brass tube set](https://www.amazon.com/dp/B0F2FKLC2N), one near the front and one near the rear. They are the stand, the ~8° tilt and the 3 mm gap the speaker fires into. Electrically floating; the only brass left.
- **Snooze button:** the 16 mm [snooze button](https://www.adafruit.com/product/1505) on the lid, rear left. Hit without looking.
- **Knob:** the [rotary encoder](https://www.adafruit.com/product/6310) on the lid, rear right, cap outside. Scroll selects an alarm or volume; press confirms; long-press plus turn deliberately dismisses a ringing alarm.
- **Hand-wave hole:** a 5 mm hole in the lid, front left, over the [proximity and light sensor](https://www.adafruit.com/product/4161) facing up. A hand over the clock wakes the face.
- **Arm switch:** the [arm switch](https://www.adafruit.com/product/805) high on the left wall; shows armed state mechanically even if the display is dark.
- **Speaker:** one of the [speaker](https://www.adafruit.com/product/1669) pair flat on the floor, cone down over a floor slot, sound coming off the table through the cradle gap.
- **Rear panel:** removable. The [charger board](https://www.adafruit.com/product/6106)'s own USB-C port through a cutout, vent slots at the [temperature and humidity sensor](https://www.adafruit.com/product/4566), the [real-time clock](https://www.adafruit.com/product/5188)'s coin cell facing the panel.
- **Right wall:** a cutout for the [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894)'s USB ports, so flashing needs no disassembly.
- **Cell:** one Nitecore 16340 in the [16340 holder with leads](https://www.amazon.com/dp/B0CRGK889F), top layer, front right, lying along the width.

The fit arithmetic (datasheet sizes, zero margin in the main-zone depth) is in [COMPACT_DESIGN.md](COMPACT_DESIGN.md): confirm with the real boards on the bench before printing.

## Core experiences

| Experience | Interaction | Offline behavior |
|---|---|---|
| Glance at time | A hand over the lid wakes a sparse clock face; lux adjusts contrast | Fully available |
| Set an alarm | Encoder on device or local phone/web UI | On-device path fully available |
| Wake sequence | OLED horizon rises, then local chime ramps in volume | Fully available from the real-time clock + flash |
| Snooze | Press the big button on the lid | Fully available and persisted across reset |
| Dismiss | Long press and turn, reducing accidental dismissal | Fully available |
| Focus timer | Tilt left/right, preserving the reference interaction | Fully available |
| Room status | Temperature/humidity base; optional true CO2 upgrade | Fully available |
| Battery gauge | Cell state of charge and estimated runtime while unplugged; a plain gauge, not an energy history | Available from the fuel gauge |
| Setup/update | BLE provisioning; Wi-Fi local UI and OTA | Alarm remains active if unavailable |

## Display direction

The UI should look like a quiet instrument, not a miniature phone:

- White/amber-tinted monochrome pixels on black.
- Large digits without a permanently lit seconds field.
- Thin “orbital” horizon line for the pre-alarm animation.
- Status glyphs appear only when actionable.
- One-pixel origin shifts and alternate clock faces distribute OLED wear.
- At night, show only the minimum time pixels or blank until presence is detected.

The 2.42-inch 128×64 module is the MVP choice, confirmed on 2026-10-31 by [SCREEN_RESEARCH.md](SCREEN_RESEARCH.md): the compact body is sized around it. A 3.12-inch 256×64 grayscale panoramic OLED is a compelling production variant, but its higher current and bare-module integration make it a custom-PCB task.

## Connectivity and speaker boundary

The recommended [controller board](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-DEVKITC-1-N8R8/15295894) has Wi-Fi and BLE. BLE provisions credentials and changes settings nearby; Wi-Fi supplies SNTP, a local web UI, OTA, and optional integrations. Neither is required to sound an alarm.

The speaker is for alarms, chimes, guided focus intervals, and short locally stored soundscapes. The controller does not implement conventional Bluetooth Classic/A2DP. A music-streaming “SoundDock” variant can use the Adafruit [Wi-Fi and Bluetooth Feather board](https://www.adafruit.com/product/5400), which supports Classic Bluetooth, but it should be treated as a separate product branch: streaming raises radio/audio power, complicates concurrency, and should always be preempted by an alarm.

## Scope

### MVP

- Reliable recurring alarms, snooze, arm/disarm, volume ramp
- [Real-time clock](https://www.adafruit.com/product/5188) offline timekeeping and wake
- 2.42-inch OLED with burn-in protection
- Local speaker audio with a fallback synthesized tone
- Encoder knob, snooze button, and alarm-arm switch
- Wi-Fi time sync/local UI/OTA and BLE setup
- Battery gauge from the 16340 cell, and temperature/humidity

### After the alarm MVP is proven

- Presence/lux and tilt/tap gestures
- Optional true CO2 sensor
- MQTT/Home Assistant integration
- Warm low-power “dawn horizon” LEDs while USB-powered
- Custom PCB, panoramic OLED option, and external-antenna validation

### Explicit non-goals for the first build

- Cloud dependency
- Voice assistant or microphone
- Phone-music streaming on the S3 baseline
- Solar charging (removed 2026-10-31; the owned 5 W panel is stock for another project)
- Exposed cell or live brass

## Change notes

- Rev B 2026-10-31: solar removed, compact body, 16340 cell. The 165 × 92 × 72 mm envelope, the service pod, visor, snooze rail, brass exoskeleton and solar sail are withdrawn; see [COMPACT_DESIGN.md](COMPACT_DESIGN.md). The owned 2.42-inch OLED stays, per [SCREEN_RESEARCH.md](SCREEN_RESEARCH.md).
- Rev A 2026-09-23: first brief.
