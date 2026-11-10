# Crumb: where the computing happens

Written 2026-11-09, answering the builder's question of the same day: which controller, and whether the camera can be processed on the robot or must go to the server. First written against Rev B, which carried a lidar; brought to Rev C the same day, after the builder took the lidar off (`CRUMB_BUILD.md`, approved 2026-11-09). Nothing is built or flashed yet.

**In one breath.** The brain on the robot is one microcontroller, the [XIAO ESP32-S3 Sense](https://www.amazon.com/dp/B0C69FFVHH). It owns everything that moves or stops the robot and draws the face. Speech and camera frames go over Wi-Fi to the pocket server on the PC (`pocket_ai_assistant/character/server`), which is the conversational brain and will be the vision brain. Safety never waits for Wi-Fi.

## The controller

| | XIAO ESP32-S3 Sense | Arduino Uno class | Raspberry Pi Zero 2 W |
| --- | --- | --- | --- |
| Cores, clock | 2 × 240 MHz | 1 × 16 MHz | 4 × 1 GHz |
| RAM | 512 kB + 8 MB PSRAM | 2 kB | 512 MB |
| Wi-Fi, camera, mic | on the board | none | none on the board |
| Board | 21 × 18 × 9 mm as a stack | 69 × 53 | 65 × 30 |
| Draw while streaming | 220–330 mA at 5 V | — | roughly 0.5 A or more at 5 V |
| Verdict | the design | cannot hold one frame or run Wi-Fi | fits neither the cage nor the 1 A rail; alone it would drain the 950 mAh cell in about 1.5 h |

Programmed with ESP-IDF, the same toolchain as Pip's firmware (`pocket_ai_assistant/firmware`), whose eyes and audio path Crumb reuses. The Arduino framework runs on the chip but is not in the plan.

## The split

| Job | Where | Why |
| --- | --- | --- |
| Motors: ramp 0.4 m/s², drive cap, turns in place | robot | 20 ms control tick |
| Edge stop: the laser ranger on the brow at 50 Hz | robot | the hard stop; a dropped Wi-Fi link must not matter |
| Obstacles ahead: a mug or a book in the ranger's cone reads shorter than the desk and stops Crumb the same way | robot | the only range sensor since Rev C; nothing looks farther than 112 mm ahead of the face |
| Wheel-drop and bump: the motion sensor | robot | 50 ms, independent of the ranger |
| Face: 240 × 240 at 30 fps over SPI with DMA | robot | 115 kB a frame, as Pip does |
| Hear and talk: mic to the server, speech back | server | Pip's protocol, already running |
| Camera: capture and send a JPEG | robot | hardware JPEG in the sensor |
| Camera: recognise, describe, answer "what do you see" | server | needs a vision model on the GPU |
| Map of the desk | not planned | no lidar since Rev C; a desk needs none |

If Crumb ever needs to see an obstacle before it enters the ranger's cone, the answer is on the robot, not on the PC. The owned 8×8 ranger could return to the brow on the free D2 (its enable) with the edge ranger moved to 0x2A, as `CRUMB_BUILD.md` notes; neither is drawn. The camera through the server is too slow to stop a robot.

## Data rates

| Stream | Rate | Note |
| --- | --- | --- |
| Edge ranger, motion sensor, gauge | bytes | one I²C chain at 400 kHz |
| Face | 115 kB a frame, 3.5 MB/s at 30 fps | SPI at 26 MHz, 35 ms a frame |
| Mic to the server | 32 kB/s | 16 kHz, 16-bit mono, 40 ms frames of 1,280 B |
| Camera, 320 × 240 JPEG | 8–15 kB a frame | about 120 kB/s at 12 fps, under 1 Mbit/s |
| Camera, 640 × 480 JPEG | 25–50 kB a frame | for a "look at this" still, one every few seconds |
| Camera, 1600 × 1200 JPEG | 100–250 kB | the sensor's full frame; stills only |

What the chip can do with the camera on its own: one small model trained ahead of time, such as person detection at 96 × 96, at a few to ten frames a second with the ESP32-S3's vector instructions. Enough to notice a person or a hand. Not enough to name an object, read a face, or hold a conversation about the scene; those go to the PC. The round trip on the LAN is a few hundred milliseconds, fine for looking, wrong for stopping.

Correction logged the same day, for Mochi's record: `PHYSICS.md` and its page said the lidar sends 4,500 bytes a second. It sends 4,500 points a second, about 17.6 kB in 47-byte packets of twelve; fixed in `pages/gen/mochi_physics.py`. Crumb Rev C has no lidar, so the number no longer touches this build.

## The server as it stands

The pocket server runs on the PC as a user service (`pocket-server`), aiohttp with `/health`, `/ws` and a status page. Protocol version 1 (`pocket_ai_assistant/character/PROTOCOL.md`): JSON control frames plus raw 16 kHz PCM in 40 ms frames, one WebSocket per device. Device to server: `hello`, `listen start/stop`, `text`, `abort`, `ping`. Server to device: `hello`, `state`, `emotion`, `gesture`, `transcript`, `audio start/end`, `error`, `pong`. The brain is a text model: the local `gpt-oss:20b` through Ollama on the RTX 5000 Ada, or OpenAI's `gpt-4.1-mini`; speech to text and text to speech run locally (faster-whisper, Kokoro) or through OpenAI.

What Crumb needs that it does not have:

1. **An image path.** The WebSocket caps a message at 64 kB (`app.py`), and no message type carries a picture. Cleanest: an HTTP `POST /image` on the same app, raw JPEG body with the device token in a header, answering JSON (a caption or a list of what was seen). The ESP32's HTTP client and the camera driver's JPEG output make that a few lines of firmware; the WebSocket stays for audio and the face.
2. **A model that can see.** `gpt-oss:20b` is text only. Options: a vision-language model through Ollama on the GPU for captions and questions, or the OpenAI path, whose model already takes images. For a cheap continuous "is anyone there, where is the mug", a classic detector on the GPU at tens of frames a second. To decide when the image path is written.
3. **Robot messages, later.** The protocol has no telemetry (cell %, ranger reading, state) and no way for the server to suggest a move. The first build keeps all behaviour on the robot; the server only talks and looks. Add telemetry when something on the PC wants it.

Already covered by the approved sheet: the camera streaming draw (220–330 mA at 5 V) is in the budget, and Wi-Fi inside the brass cage is a listed risk with an RSSI check before the skins go on.

## Order of work

By the house rule, step two (the physics page for Rev C) comes first. Then the bench tests in `CRUMB_BUILD.md`, the chain scan first and the current log last. Firmware begins when the XIAO lands: the safety loop first (the ranger and the motion sensor), the face second, Pip's audio path third. The camera path and the server's image endpoint come last; the robot drives, stops and talks without them.

Links: the Espressif [camera driver](https://github.com/espressif/esp32-camera) for the JPEG capture.
