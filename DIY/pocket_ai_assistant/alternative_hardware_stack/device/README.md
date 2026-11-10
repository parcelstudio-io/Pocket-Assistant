# CoreS3-SE device scaffold

This folder is a **review-only alternative**, isolated from the working
ESP32-C3/Xiaozhi firmware. It targets the M5Stack CoreS3-SE (`K128-SE`): a
finished USB-C device with a 320×240 touch display, ESP32-S3 Wi-Fi controller,
dual microphones, audio codec, amplifier, and 1 W speaker already assembled.
No CoreS3-SE hardware has been purchased, flashed, or electrically tested by
this repository.

The scaffold currently proves three design seams:

- a cute, asset-free 320×240 face with idle, listening, thinking, speaking,
  offline-demo, and error states;
- a press-and-release interaction that enforces microphone/speaker ownership;
- a LAN request to `POST /api/chat` and incremental parsing of the server's
  OpenAI-style SSE response.

It deliberately does **not** claim to be a finished voice assistant. The button
currently sends the configured demo sentence. Capturing PCM, local speech-to-
text, and streaming returned PCM to the speaker are the next milestones.

## Why CoreS3-SE

The SE keeps the useful CoreS3 hardware but omits the camera, IMU, magnetometer,
proximity sensor, and battery bottom. That makes it a smaller privacy surface
and matches this project's USB-powered prototype rule. The manufacturer lists
the unit as 54 × 54 × 15.5 mm and 37.8 g. It is wider than the current
ESP32-C3 mock-up, so it needs its own fit check before anyone calls it the final
enclosure.

Manufacturer references:

- <https://docs.m5stack.com/en/core/CoreS3-SE>
- <https://shop.m5stack.com/products/m5stack-cores3-se-iot-controller-w-o-battery-bottom>

## Hardware interface used by M5Unified

These are already routed inside the finished product; they are not a wiring
list.

| Function | Internal device path | ESP32-S3 interface |
| --- | --- | --- |
| UI | ILI9342C 320×240 LCD + FT6336U touch | M5Unified display/touch APIs |
| Control bus | touch, PMU, ES7210, AW88298 | I2C SDA `GPIO12`, SCL `GPIO11` |
| Microphones | dual microphones → ES7210 | I2S1 MCLK `GPIO0`, BCLK `GPIO34`, LRCLK `GPIO33`, data in `GPIO14` |
| Speaker | AW88298 → built-in 1 W speaker | I2S1 BCLK `GPIO34`, LRCLK `GPIO33`, data out `GPIO13` |
| Network | ESP32-S3 radio | 2.4 GHz Wi-Fi |
| Prototype power | finished device power path | USB-C only |

The code intentionally uses M5Unified rather than programming the codecs or
their pins directly.

## Half-duplex rule

M5Stack's own M5Unified microphone example says the microphone and speaker
cannot be used at the same time and explicitly shuts one down before starting
the other:

<https://raw.githubusercontent.com/m5stack/M5Unified/master/examples/Basic/Microphone/Microphone.ino>

This scaffold makes that constraint visible with `claimMicrophone()`,
`claimSpeaker()`, and `releaseAudio()`. Its first voice workflow must remain:

```text
hold → listen → release/stop mic → local STT/LLM/TTS → start speaker → idle
```

Do not add barge-in or simultaneous capture/playback until a separate ESP-IDF
audio design has demonstrated that mode on this exact board.

## Preview the UI without secrets

The checked-in build has no Wi-Fi credentials. On a CoreS3-SE it therefore
starts in **FACE DEMO** mode. A press and release cycles through listening,
thinking, and speaking, with a small local chirp. It sends no network traffic.

Build from this directory with a current PlatformIO Core:

```bash
uvx --from platformio==6.2.0 pio run
```

The first build downloads the pinned Espressif platform and libraries. A clean
compile verifies source compatibility; it does not verify physical audio,
touch, radio, or power behavior.

## Connect it to the local prototype server

Create the ignored configuration file and edit all placeholder values:

```bash
cp include/device_config.example.h include/device_config.h
```

`POCKET_SERVER_URL` must use the server computer's private-LAN address and port
`8787`, for example `http://192.168.1.10:8787`. Do not use `localhost`: from the
CoreS3-SE that name means the CoreS3-SE itself. LAN binding requires the server
to have `POCKET_AI_TOKEN`; set `POCKET_DEVICE_TOKEN` to that same value.

Then build, upload through USB-C, and monitor, substituting the actual serial
port:

```bash
uvx --from platformio==6.2.0 pio run
uvx --from platformio==6.2.0 pio run --target upload --upload-port /dev/ttyACM0
uvx --from platformio==6.2.0 pio device monitor --port /dev/ttyACM0 --baud 115200
```

Use a private, trusted 2.4 GHz LAN. The review protocol is plain HTTP/SSE and
must not be forwarded to the Internet. The bearer token limits accidental LAN
access but is not encryption; TLS is a later deployment requirement.

The device permits up to 130 seconds with no incoming server bytes, giving the
gateway's 120-second backend timeout a small transport margin. That is an
**idle** limit, not a whole-response limit: every HTTP header or SSE byte resets
the rollover-safe watchdog, so a healthy long response may keep streaming.

## Firmware pins and dependency policy

`platformio.ini` pins the build platform and every direct third-party library:

- PlatformIO Espressif32 `7.1.3`;
- M5Unified `0.2.23`;
- M5GFX `0.2.30`;
- ArduinoJson `7.4.3`.

The PlatformIO `m5stack-cores3` board definition supplies the 16 MB flash,
PSRAM, USB CDC, and CoreS3-family build flags. M5Unified initializes the shared
CoreS3-family display and audio hardware; this alternative is reviewed
specifically for CoreS3-SE, not for an arbitrary ESP32-S3 board.
