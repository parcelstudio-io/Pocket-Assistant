# Alternative hardware candidate: CoreS3-SE

> **Review status — do not order from this file yet.** This is an experimental
> USB-powered alternative to the breadboard A1 stack. It does not change or
> supersede the existing `firmware/`, fast track, inventory, or purchase
> authority.

## Proposed device

Use one **M5Stack CoreS3-SE (`K128-SE`)** as a thin voice-and-display client.
The language model runs on a computer on the same private network; it does not
run on the ESP32-S3.

The board integrates the parts that are separate on A1:

| Function | CoreS3-SE hardware |
| --- | --- |
| Controller | ESP32-S3, dual-core 240 MHz |
| Memory | 16 MB flash, 8 MB PSRAM |
| UI | 2.0-inch 320 x 240 IPS capacitive-touch display |
| Input audio | ES7210 with two built-in microphones |
| Output audio | AW88298 I2S amplifier and built-in 1 W speaker |
| Network | 2.4 GHz Wi-Fi |
| Development/power | USB-C |

The SE version is the deliberate choice. It omits the regular CoreS3's camera,
IMU, proximity sensor, magnetometer, battery bottom, and their unnecessary
cost/permissions. As checked on 2026-10-01, the manufacturer's store listed it
at **$38.90 and in stock**. Price and availability are not a purchase approval
and must be rechecked immediately before any order.

Primary references:

- [M5Stack CoreS3-SE documentation](https://docs.m5stack.com/en/core/CoreS3-SE)
- [M5Stack CoreS3-SE official store page](https://shop.m5stack.com/products/m5stack-cores3-se-iot-controller-w-o-battery-bottom)
- [ESP32-S3 I2S documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/i2s.html)

## Why this is a useful alternative

- The display, touch controller, microphones, codec, amplifier, and speaker are
  already assembled and have a vendor-supported board library.
- There are no loose breadboard I2S connections between the controller and the
  audio devices.
- A 320 x 240 color display can show a much more expressive interface than the
  existing 128 x 64 monochrome OLED.
- The ESP32-S3's 8 MB PSRAM is appropriate for display buffers, network
  buffers, and short audio queues. It is **not** enough to turn this into the
  local language-model host.
- The board can stay a USB-powered home device, preserving the project's
  present no-battery boundary.

This trades repairability and the smaller original silhouette for a much
faster, lower-risk software experiment. Its published dimensions are
54.0 x 54.0 x 15.5 mm, so it will not fit the current enclosure concept without
a new cardboard mock-up.

## Internal buses

Application firmware should use M5Stack's `M5Unified` abstraction instead of
initializing the codecs directly. These internal connections are recorded for
review and debugging:

| Signal | ESP32-S3 GPIO | Destination |
| --- | ---: | --- |
| Internal I2C SDA / SCL | 12 / 11 | touch, PMIC, codecs, RTC |
| I2S bit clock / word select | 34 / 33 | ES7210 and AW88298 |
| Microphone master clock | 0 | ES7210 |
| Microphone data into ESP32-S3 | 14 | ES7210 output |
| Speaker data out of ESP32-S3 | 13 | AW88298 input |

The official M5Unified microphone example stops speaker playback before
starting the microphone and stops the microphone before restarting the
speaker. Therefore the first implementation is intentionally **half duplex**:

```text
idle -> listening -> thinking -> speaking -> idle
```

It uses push-to-talk and has no barge-in while audio is playing. Full-duplex
echo cancellation is a later research task, not an MVP promise.

## Minimal review BOM

| Qty | Candidate | Needed now? |
| ---: | --- | --- |
| 1 | M5Stack CoreS3-SE `K128-SE` | No — review the browser prototype first |
| 1 | Known-good USB-C data/power cable | Already required by the current project |
| 1 | 5 V USB source with comfortable current margin | Later bench test; no battery |
| 1 | Existing computer capable of running Ollama | Yes; this is the model host |
| 1 | Private 2.4 GHz Wi-Fi network | Later hardware test |

Do not add a battery base, raw cell, external amplifier, external speaker, or
metal enclosure during this evaluation.

## Promotion gates

Keep each gate separate and record its evidence:

1. **UI-DEMO-01:** the desktop demo shows idle, listening, thinking, speaking,
   and error states at a 320 x 240 viewport.
2. **LOCAL-LLM-01:** a typed prompt streams from a locally hosted model with
   the computer disconnected from the Internet after model installation.
3. **LAN-AUTH-01:** the server binds to the private LAN only when explicitly
   requested and rejects a missing/wrong bearer token.
4. **S3-DISPLAY-01:** USB-powered CoreS3-SE renders the face and registers ten
   deliberate touch events without resets.
5. **S3-AUDIO-IN-01:** five microphone recordings are nonzero and intelligible;
   no speaker playback runs at the same time.
6. **S3-AUDIO-OUT-01:** five capped test sounds play cleanly from the built-in
   speaker, without warmth or reset; no microphone capture runs at the same
   time.
7. **S3-TURN-01:** twenty complete push-to-talk turns succeed without a reset,
   stuck UI state, or lost final response.
8. **FIT-S3-01:** only after the electrical tests, measure the actual unit and
   make a fresh 1:1 cardstock mock-up. The existing enclosure CAD is not reused.

No gate in this file has been run on physical CoreS3-SE hardware.

## Network and privacy boundary

- The model URL is configured on the host server, never accepted from browser
  or device input.
- Desktop preview binds to `127.0.0.1` by default.
- A physical device requires an explicit LAN bind and a long random bearer
  token, on a trusted private/IoT network.
- Do not forward the server port through the router.
- Typed Ollama chat can be fully local. Browser speech-recognition APIs are not
  guaranteed local and must not be described as offline voice recognition.
- A future fully local voice path should add a host-side speech-to-text engine
  and text-to-speech engine behind a defined streaming protocol.
